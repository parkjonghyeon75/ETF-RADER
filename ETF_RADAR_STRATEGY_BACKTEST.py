# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date


# ============================================================
# ETF RADAR STRATEGY BACKTEST
# A : 현재 선행점수
# B : 가격 + 가속도 + 상대강도 중심
# C : 가격 + 상대강도 + 가속도 + 과열 억제
#
# 목적
# 미래테마 → 선행 ETF → 과열 필터 → 가격구간
# 실제 과거 데이터에서 투자성과가 발생했는지 검증
# ============================================================


st.set_page_config(
    page_title="ETF RADAR STRATEGY TEST",
    page_icon="🧪",
    layout="wide"
)


# ============================================================
# SESSION
# ============================================================

defaults = {
    "strategy_result": None,
    "strategy_data": None,
    "sim_curve": None,
    "sim_metrics": None,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ============================================================
# UNIVERSE
# ============================================================

POOL = {
    "QQQ": "나스닥100",
    "XLK": "미국기술",
    "SMH": "반도체",
    "SOXX": "반도체",
    "BOTZ": "로봇AI",
    "ARKQ": "자동화로봇",
    "HACK": "사이버보안",
    "ITA": "방산",
    "PAVE": "인프라",
    "URA": "원전우라늄",
    "LIT": "2차전지",
    "XBI": "바이오",
    "INDA": "인도",
    "EWY": "한국",
    "EWJ": "일본",
    "EEM": "신흥국",
    "GLD": "금",
    "TLT": "미국장기채",
}

BENCH = "SPY"


THEME_GROUPS = {
    "미국기술": ["QQQ", "XLK"],
    "반도체": ["SMH", "SOXX"],
    "로봇AI": ["BOTZ", "ARKQ"],
    "위험선호": [
        "QQQ",
        "XLK",
        "SMH",
        "SOXX",
        "BOTZ",
        "ARKQ",
    ],
    "방어자산": [
        "GLD",
        "TLT",
    ],
    "글로벌": [
        "INDA",
        "EWY",
        "EWJ",
        "EEM",
    ],
}


# ============================================================
# DATA
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def download_prices(tickers, start, end):

    symbols = list(dict.fromkeys(list(tickers) + [BENCH]))

    data = yf.download(
        symbols,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        group_by="column",
    )

    if data is None or data.empty:
        return pd.DataFrame()

    try:
        close = data["Close"].copy()
    except Exception:
        close = data.copy()

    if isinstance(close, pd.Series):
        close = close.to_frame()

    close.columns = [str(c) for c in close.columns]

    close = close.sort_index()
    close = close.dropna(how="all")

    return close


# ============================================================
# INDICATORS
# ============================================================

def indicators(s):

    s = s.astype(float)

    out = pd.DataFrame(index=s.index)

    out["Close"] = s
    out["MA20"] = s.rolling(20).mean()
    out["MA60"] = s.rolling(60).mean()

    out["R5"] = s.pct_change(5) * 100
    out["R20"] = s.pct_change(20) * 100
    out["R60"] = s.pct_change(60) * 100

    ret = s.pct_change()
    vol20 = ret.rolling(20).std()

    out["VOL20"] = vol20

    dollar_ret = s.pct_change().abs()

    out["VR"] = (
        dollar_ret / dollar_ret.rolling(20).mean()
    )

    delta = s.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    out["RSI"] = 100 - (100 / (1 + rs))

    out["LOW20"] = s.rolling(20).min()
    out["HIGH20"] = s.rolling(20).max()

    return out


# ============================================================
# SCORE HELPERS
# ============================================================

def clip_score(x):
    return float(np.clip(x, 0, 100))


def normalize_price_score(r5, r20, r60, dist20):

    score = 50

    score += np.clip(r5 * 2.5, -15, 15)
    score += np.clip(r20 * 1.5, -15, 20)
    score += np.clip(r60 * 0.35, -10, 15)

    if dist20 >= 0:
        score += np.clip(dist20 * 1.2, -5, 10)
    else:
        score += np.clip(dist20 * 1.0, -10, 5)

    return clip_score(score)


def rsi_score(rsi):

    if pd.isna(rsi):
        return 50

    if rsi < 30:
        return 55

    if 30 <= rsi < 45:
        return 80

    if 45 <= rsi < 60:
        return 90

    if 60 <= rsi < 70:
        return 75

    if 70 <= rsi < 80:
        return 45

    return 20


def volume_score(vr):

    if pd.isna(vr):
        return 50

    if vr < 0.75:
        return 35

    if vr < 0.90:
        return 45

    if vr < 1.05:
        return 60

    if vr < 1.20:
        return 80

    if vr < 1.50:
        return 92

    return 75


def acceleration_score(accel):

    if pd.isna(accel):
        return 50

    score = 50 + accel * 10

    return clip_score(score)


def relative_score(rs20):

    if pd.isna(rs20):
        return 50

    return clip_score(
        50 + rs20 * 4
    )


def structure_score(close, ma20, ma60):

    if pd.isna(ma20) or pd.isna(ma60):
        return 50

    score = 50

    if close > ma20:
        score += 20
    else:
        score -= 15

    if ma20 > ma60:
        score += 20
    else:
        score -= 15

    if close > ma60:
        score += 10
    else:
        score -= 10

    return clip_score(score)


# ============================================================
# LEADING SIGNAL
# ============================================================

def leading_signal(
    row,
    benchmark_row=None,
    mode="A"
):

    close = row["Close"]
    ma20 = row["MA20"]
    ma60 = row["MA60"]

    r5 = row["R5"]
    r20 = row["R20"]
    r60 = row["R60"]

    vr = row["VR"]
    rsi = row["RSI"]

    if pd.isna(close):
        return None

    dist20 = (
        (close / ma20 - 1) * 100
        if pd.notna(ma20) and ma20 != 0
        else 0
    )

    if benchmark_row is not None:
        b_r20 = benchmark_row["R20"]

        if pd.isna(b_r20):
            b_r20 = 0

        rs20 = r20 - b_r20

    else:
        rs20 = 0

    accel = r5 - r20 / 4

    early_price = normalize_price_score(
        r5,
        r20,
        r60,
        dist20
    )

    early_rsi = rsi_score(rsi)

    flow = volume_score(vr)

    accel_score = acceleration_score(
        accel
    )

    rel = relative_score(rs20)

    structure = structure_score(
        close,
        ma20,
        ma60
    )

    # --------------------------------------------------------
    # A : 기존 공식
    # --------------------------------------------------------

    score_a = (
        early_price * 0.22
        + early_rsi * 0.18
        + flow * 0.22
        + accel_score * 0.16
        + rel * 0.14
        + structure * 0.08
    )

    # --------------------------------------------------------
    # B : 가격 + 가속도 + 상대강도 중심
    # --------------------------------------------------------

    score_b = (
        early_price * 0.30
        + early_rsi * 0.05
        + flow * 0.05
        + accel_score * 0.25
        + rel * 0.25
        + structure * 0.10
    )

    # --------------------------------------------------------
    # C : 가격 + 상대강도 + 가속도 중심
    # RSI / 거래량 비중 축소
    # 90점 이상 과열 억제
    # --------------------------------------------------------

    raw_c = (
        early_price * 0.40
        + rel * 0.25
        + accel_score * 0.20
        + structure * 0.05
        + early_rsi * 0.05
        + flow * 0.05
    )

    heat_penalty = 0

    if raw_c >= 90:
        heat_penalty = (raw_c - 88) * 1.5

    score_c = raw_c - heat_penalty

    score_map = {
        "A": score_a,
        "B": score_b,
        "C": score_c,
    }

    score = clip_score(
        score_map.get(mode, score_a)
    )

    # --------------------------------------------------------
    # BUY FILTER
    # --------------------------------------------------------

    early_buy = (
        score >= 72
        and vr >= 1.05
        and rsi < 70
        and dist20 < 7
        and rs20 >= -1
    )

    return {
        "current": close,
        "MA20": ma20,
        "MA60": ma60,

        "R5": r5,
        "R20": r20,
        "R60": r60,

        "VR": vr,
        "RSI": rsi,

        "dist20": dist20,
        "rs20": rs20,
        "accel": accel,

        "early_price": early_price,
        "early_rsi": early_rsi,
        "flow": flow,
        "accel_score": accel_score,
        "rel": rel,
        "structure": structure,

        "score_A": score_a,
        "score_B": score_b,
        "score_C_raw": raw_c,
        "heat_penalty": heat_penalty,

        "score": score,
        "early_buy": early_buy,
    }


# ============================================================
# THEME SCORE
# ============================================================

def theme_score(
    theme,
    current_date,
    price_data,
    indicator_data,
    benchmark_indicator,
    mode="A"
):

    tickers = THEME_GROUPS.get(
        theme,
        []
    )

    scores = []
    returns = []
    leaders = 0
    valid = 0

    for ticker in tickers:

        if ticker not in indicator_data:
            continue

        ind = indicator_data[ticker]

        if current_date not in ind.index:
            continue

        row = ind.loc[current_date]

        if benchmark_indicator is not None:
            if current_date in benchmark_indicator.index:
                brow = benchmark_indicator.loc[current_date]
            else:
                brow = None
        else:
            brow = None

        sig = leading_signal(
            row,
            brow,
            mode
        )

        if sig is None:
            continue

        valid += 1

        scores.append(sig["score"])
        returns.append(sig["R20"])

        if sig["early_buy"]:
            leaders += 1

    if valid == 0:
        return None

    lead_avg = np.nanmean(scores)

    breadth = (
        leaders / valid * 100
        if valid
        else 0
    )

    ret_avg = (
        np.nanmean(returns)
        if returns
        else 0
    )

    # 테마 모멘텀 + 선행 ETF 강도
    score = (
        lead_avg * 0.55
        + breadth * 0.25
        + clip_score(
            50 + ret_avg * 3
        ) * 0.20
    )

    score = clip_score(score)

    if score >= 75:
        stage = "강한상승"
    elif score >= 65:
        stage = "상승"
    elif score >= 55:
        stage = "초기"
    elif score >= 45:
        stage = "중립"
    else:
        stage = "약세"

    return {
        "theme": theme,
        "score": score,
        "breadth": breadth,
        "lead_avg": lead_avg,
        "ret_avg": ret_avg,
        "stage": stage,
    }


# ============================================================
# PRICE ZONE
# ============================================================

def price_zone(sig):

    if sig is None:
        return "무효"

    close = sig["current"]
    ma20 = sig["MA20"]
    ma60 = sig["MA60"]

    dist20 = sig["dist20"]
    score = sig["score"]

    if pd.isna(close) or pd.isna(ma20):
        return "무효"

    if close < ma60:
        return "무효"

    if dist20 > 10:
        return "추격금지"

    if score >= 72 and -3 <= dist20 <= 7:
        return "매수구간"

    if dist20 < -5:
        return "눌림대기"

    return "눌림대기"


# ============================================================
# SNAPSHOT
# ============================================================

def build_snapshot(
    current_date,
    price_data,
    indicator_data,
    benchmark_indicator,
    mode="A"
):

    theme_results = []

    for theme in THEME_GROUPS:

        result = theme_score(
            theme,
            current_date,
            price_data,
            indicator_data,
            benchmark_indicator,
            mode
        )

        if result is not None:
            theme_results.append(result)

    if not theme_results:
        return None

    theme_results = sorted(
        theme_results,
        key=lambda x: x["score"],
        reverse=True
    )

    top_theme = theme_results[0]

    theme = top_theme["theme"]

    candidates = []

    for ticker in THEME_GROUPS[theme]:

        if ticker not in indicator_data:
            continue

        ind = indicator_data[ticker]

        if current_date not in ind.index:
            continue

        row = ind.loc[current_date]

        if current_date in benchmark_indicator.index:
            brow = benchmark_indicator.loc[
                current_date
            ]
        else:
            brow = None

        sig = leading_signal(
            row,
            brow,
            mode
        )

        if sig is None:
            continue

        zone = price_zone(sig)

        # 과열 ETF는 점수에서 추가 감점
        heat_penalty = 0

        if zone == "추격금지":
            heat_penalty = 8

        selection_score = (
            sig["score"] - heat_penalty
        )

        candidates.append({
            "ticker": ticker,
            "signal": sig,
            "zone": zone,
            "selection_score": selection_score,
        })

    if not candidates:
        return None

    candidates = sorted(
        candidates,
        key=lambda x: x["selection_score"],
        reverse=True
    )

    winner = candidates[0]

    sig = winner["signal"]

    return {
        "날짜": current_date,
        "테마": theme,
        "테마점수": top_theme["score"],
        "테마단계": top_theme["stage"],
        "ETF": winner["ticker"],

        "선행점수": sig["score"],
        "과열점수": sig["heat_penalty"],
        "가격상태": winner["zone"],
        "매수가": sig["current"],

        "가격점수": sig["early_price"],
        "RSI점수": sig["early_rsi"],
        "거래량점수": sig["flow"],
        "가속도점수": sig["accel_score"],
        "상대강도점수": sig["rel"],
        "구조점수": sig["structure"],

        "R5": sig["R5"],
        "R20": sig["R20"],
        "R60": sig["R60"],
        "VR": sig["VR"],
        "RSI": sig["RSI"],
        "MA20이격": sig["dist20"],
        "상대강도": sig["rs20"],
        "가속도": sig["accel"],
    }


# ============================================================
# FORWARD RETURN
# ============================================================

def forward_return(
    price_series,
    entry_date,
    days
):

    if entry_date not in price_series.index:
        return np.nan, np.nan

    pos = price_series.index.get_loc(
        entry_date
    )

    if isinstance(pos, slice):
        pos = pos.start

    target_pos = pos + days

    if target_pos >= len(price_series):
        return np.nan, np.nan

    entry_price = price_series.iloc[pos]

    future = price_series.iloc[
        pos + 1:target_pos + 1
    ]

    if future.empty:
        return np.nan, np.nan

    exit_price = price_series.iloc[
        target_pos
    ]

    ret = (
        exit_price / entry_price - 1
    ) * 100

    drawdown = (
        future / entry_price - 1
    ).min() * 100

    return ret, drawdown


# ============================================================
# BACKTEST
# ============================================================

def run_strategy_backtest(
    start_date,
    end_date,
    tickers,
    step_days=5,
    mode="A"
):

    all_tickers = list(
        dict.fromkeys(
            list(tickers) + [BENCH]
        )
    )

    prices = download_prices(
        all_tickers,
        start_date,
        end_date
    )

    if prices.empty:
        return pd.DataFrame()

    available = [
        t for t in tickers
        if t in prices.columns
    ]

    if BENCH not in prices.columns:
        return pd.DataFrame()

    prices = prices.dropna(
        how="all"
    )

    indicator_data = {}

    for ticker in available:

        s = prices[ticker].dropna()

        if len(s) < 80:
            continue

        indicator_data[ticker] = indicators(
            s
        )

    benchmark_indicator = indicators(
        prices[BENCH].dropna()
    )

    if not indicator_data:
        return pd.DataFrame()

    common_start = max(
        x.index.min()
        for x in indicator_data.values()
    )

    common_start = max(
        common_start,
        benchmark_indicator.index.min()
    )

    test_start = pd.Timestamp(
        start_date
    )

    test_end = pd.Timestamp(
        end_date
    )

    dates = benchmark_indicator.index[
        (benchmark_indicator.index >= common_start)
        & (benchmark_indicator.index >= test_start)
        & (benchmark_indicator.index <= test_end)
    ]

    rows = []

    for i in range(
        0,
        len(dates),
        step_days
    ):

        current_date = dates[i]

        snapshot = build_snapshot(
            current_date,
            prices,
            indicator_data,
            benchmark_indicator,
            mode
        )

        if snapshot is None:
            continue

        ticker = snapshot["ETF"]

        if ticker not in prices.columns:
            continue

        entry_series = prices[
            ticker
        ].dropna()

        future_dates = entry_series.index[
            entry_series.index > current_date
        ]

        if len(future_dates) == 0:
            continue

        entry_date = future_dates[0]

        snapshot["진입일"] = entry_date

        r5, dd5 = forward_return(
            entry_series,
            entry_date,
            5
        )

        r20, dd20 = forward_return(
            entry_series,
            entry_date,
            20
        )

        r60, dd60 = forward_return(
            entry_series,
            entry_date,
            60
        )

        snapshot["5일수익률"] = r5
        snapshot["5일최대낙폭"] = dd5

        snapshot["20일수익률"] = r20
        snapshot["20일최대낙폭"] = dd20

        snapshot["60일수익률"] = r60
        snapshot["60일최대낙폭"] = dd60

        # ----------------------------------------------------
        # A/B/C/D
        # ----------------------------------------------------

        snapshot["A"] = (
            snapshot["테마점수"] >= 55
        )

        snapshot["B"] = (
            snapshot["선행점수"] >= 72
        )

        snapshot["C"] = (
            snapshot["테마점수"] >= 55
            and snapshot["선행점수"] >= 72
        )

        snapshot["D"] = (
            snapshot["테마점수"] >= 55
            and snapshot["선행점수"] >= 72
            and snapshot["가격상태"] == "매수구간"
        )

        snapshot["공식"] = mode

        rows.append(
            snapshot
        )

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


# ============================================================
# SUMMARY
# ============================================================

def strategy_summary(
    df,
    signal_col,
    horizon=20
):

    if df is None or df.empty:
        return {
            "건수": 0,
            "승률": np.nan,
            "평균수익률": np.nan,
            "중앙값": np.nan,
            "평균낙폭": np.nan,
            "최고": np.nan,
            "최저": np.nan,
        }

    ret_col = f"{horizon}일수익률"
    dd_col = f"{horizon}일최대낙폭"

    x = df[
        df[signal_col] == True
    ].copy()

    x = x.dropna(
        subset=[ret_col]
    )

    if x.empty:
        return {
            "건수": 0,
            "승률": np.nan,
            "평균수익률": np.nan,
            "중앙값": np.nan,
            "평균낙폭": np.nan,
            "최고": np.nan,
            "최저": np.nan,
        }

    return {
        "건수": len(x),
        "승률": (
            (x[ret_col] > 0).mean()
            * 100
        ),
        "평균수익률": x[ret_col].mean(),
        "중앙값": x[ret_col].median(),
        "평균낙폭": x[dd_col].mean(),
        "최고": x[ret_col].max(),
        "최저": x[ret_col].min(),
    }


# ============================================================
# DIAGNOSTIC
# ============================================================

def diagnostic_table(
    df,
    group_col,
    horizon=20
):

    ret_col = f"{horizon}일수익률"

    if df.empty:
        return pd.DataFrame()

    x = df.dropna(
        subset=[ret_col]
    ).copy()

    if x.empty:
        return pd.DataFrame()

    result = (
        x.groupby(group_col)[ret_col]
        .agg(
            ["count", "mean", "median"]
        )
        .reset_index()
    )

    win = (
        x.groupby(group_col)[ret_col]
        .apply(
            lambda z: (
                z > 0
            ).mean() * 100
        )
        .reset_index(
            name="승률"
        )
    )

    result = result.merge(
        win,
        on=group_col,
        how="left"
    )

    result.columns = [
        group_col,
        "건수",
        "평균수익률",
        "중앙값",
        "승률",
    ]

    return result


def score_correlation(
    df,
    score_col,
    return_col
):

    if (
        score_col not in df.columns
        or return_col not in df.columns
    ):
        return np.nan

    x = df[
        [score_col, return_col]
    ].dropna()

    if len(x) < 5:
        return np.nan

    return x[
        score_col
    ].corr(
        x[return_col]
    )


# ============================================================
# STOP LOSS TEST
# ============================================================

def stop_loss_test(
    df,
    signal_col,
    horizon=20,
    stop_levels=None
):

    if stop_levels is None:
        stop_levels = [
            None,
            -5,
            -7,
            -10,
            -12,
            -15,
        ]

    ret_col = f"{horizon}일수익률"
    dd_col = f"{horizon}일최대낙폭"

    x = df[
        df[signal_col] == True
    ].copy()

    x = x.dropna(
        subset=[
            ret_col,
            dd_col
        ]
    )

    rows = []

    for stop in stop_levels:

        if x.empty:
            rows.append({
                "손절": (
                    "손절 없음"
                    if stop is None
                    else f"-{abs(stop)}%"
                ),
                "건수": 0,
                "평균수익률": np.nan,
                "승률": np.nan,
                "평균낙폭": np.nan,
                "손절발생률": np.nan,
            })
            continue

        if stop is None:

            final_ret = x[ret_col]

            stop_rate = 0

        else:

            triggered = (
                x[dd_col] <= stop
            )

            final_ret = np.where(
                triggered,
                stop,
                x[ret_col]
            )

            stop_rate = (
                triggered.mean() * 100
            )

            final_ret = pd.Series(
                final_ret,
                index=x.index
            )

        rows.append({
            "손절": (
                "손절 없음"
                if stop is None
                else f"-{abs(stop)}%"
            ),
            "건수": len(x),
            "평균수익률": final_ret.mean(),
            "승률": (
                (final_ret > 0).mean()
                * 100
            ),
            "평균낙폭": x[dd_col].mean(),
            "손절발생률": stop_rate,
        })

    return pd.DataFrame(rows)


# ============================================================
# SIMULATION
# ============================================================

def simulate_equity_curve(
    df,
    signal_col,
    hold_days=20,
    initial=1_000_000
):

    if df.empty:
        return pd.DataFrame(), {}

    x = df[
        df[signal_col] == True
    ].copy()

    x = x.dropna(
        subset=[
            "진입일",
            f"{hold_days}일수익률"
        ]
    )

    if x.empty:
        return pd.DataFrame(), {}

    x = x.sort_values(
        "진입일"
    )

    capital = initial
    curve = []

    last_exit_position = -1

    for idx, row in x.iterrows():

        current_position = x.index.get_loc(
            idx
        )

        if current_position <= last_exit_position:
            continue

        ret = row[
            f"{hold_days}일수익률"
        ]

        capital *= (
            1 + ret / 100
        )

        curve.append({
            "진입일": row["진입일"],
            "ETF": row["ETF"],
            "수익률": ret,
            "자산": capital,
        })

        # 실제 보유기간을 고려하여
        # 같은 기간에 겹치는 신호는 제외
        last_exit_position = (
            current_position
            + hold_days
            - 1
        )

    curve_df = pd.DataFrame(
        curve
    )

    if curve_df.empty:
        return curve_df, {}

    returns = curve_df["수익률"]

    metrics = {
        "초기자산": initial,
        "최종자산": curve_df["자산"].iloc[-1],
        "총수익률": (
            curve_df["자산"].iloc[-1]
            / initial
            - 1
        ) * 100,
        "거래수": len(curve_df),
        "승률": (
            (returns > 0).mean()
            * 100
        ),
        "평균수익률": returns.mean(),
        "최고수익률": returns.max(),
        "최저수익률": returns.min(),
    }

    return curve_df, metrics


# ============================================================
# FORMULA COMPARISON
# ============================================================

def compare_formula_modes(
    start_date,
    end_date,
    tickers,
    step_days
):

    result_rows = []

    all_data = {}

    for mode in ["A", "B", "C"]:

        data = run_strategy_backtest(
            start_date,
            end_date,
            tickers,
            step_days,
            mode
        )

        all_data[mode] = data

        if data.empty:
            continue

        for signal in [
            "A",
            "B",
            "C",
            "D"
        ]:

            s20 = strategy_summary(
                data,
                signal,
                20
            )

            s60 = strategy_summary(
                data,
                signal,
                60
            )

            result_rows.append({
                "공식": mode,
                "전략": signal,
                "20일 건수": s20["건수"],
                "20일 평균수익률":
                    s20["평균수익률"],
                "20일 승률":
                    s20["승률"],
                "60일 건수": s60["건수"],
                "60일 평균수익률":
                    s60["평균수익률"],
                "60일 승률":
                    s60["승률"],
            })

    return (
        pd.DataFrame(result_rows),
        all_data
    )


# ============================================================
# UI
# ============================================================

st.title("🧪 ETF RADAR STRATEGY TEST")

st.caption(
    "미래테마 → 선행 ETF → 과열 필터 → 가격구간까지 "
    "실제 투자 흐름을 과거 데이터로 검증합니다."
)

st.info(
    "연구용 백테스트입니다. 과거 성과가 미래 수익을 보장하지 않습니다."
)


# ============================================================
# SETTINGS
# ============================================================

with st.expander(
    "⚙️ 백테스트 설정",
    expanded=True
):

    c1, c2, c3 = st.columns(3)

    start_date = c1.date_input(
        "시작일",
        date(2021, 1, 1)
    )

    end_date = c2.date_input(
        "종료일",
        date(2025, 12, 31)
    )

    step_days = c3.selectbox(
        "검사 간격",
        [1, 5, 10, 20],
        index=1
    )

    selected_tickers = st.multiselect(
        "테스트 ETF",
        list(POOL.keys()),
        default=[
            "QQQ",
            "XLK",
            "SMH",
            "SOXX",
            "BOTZ",
            "ARKQ",
            "GLD",
            "TLT",
            "INDA",
            "EWY",
            "EWJ",
            "EEM",
        ],
        format_func=lambda x:
            f"{x} · {POOL[x]}"
    )

    run_button = st.button(
        "🚀 전체 백테스트 실행",
        type="primary",
        use_container_width=True
    )


# ============================================================
# RUN
# ============================================================

if run_button:

    if not selected_tickers:
        st.error(
            "테스트할 ETF를 하나 이상 선택하세요."
        )
        st.stop()

    with st.spinner(
        "과거 데이터를 다운로드하고 "
        "A/B/C 점수공식을 다시 계산하는 중입니다..."
    ):

        comparison, all_data = (
            compare_formula_modes(
                start_date,
                end_date,
                selected_tickers,
                step_days
            )
        )

    if comparison.empty:
        st.error(
            "백테스트 결과가 없습니다."
        )
        st.stop()

    st.session_state[
        "strategy_result"
    ] = comparison

    st.session_state[
        "strategy_data"
    ] = all_data["C"]

    st.session_state[
        "formula_data"
    ] = all_data


# ============================================================
# RESULT
# ============================================================

comparison = st.session_state.get(
    "strategy_result"
)

data = st.session_state.get(
    "strategy_data"
)

formula_data = st.session_state.get(
    "formula_data"
)


if comparison is not None and not comparison.empty:

    # ========================================================
    # ① CORE
    # ========================================================

    st.subheader(
        "① 한눈에 보는 핵심 결과"
    )

    st.write(
        "먼저 A/B/C 점수공식이 실제 ETF 선정 성과를 "
        "개선시키는지 확인합니다."
    )

    for mode in ["A", "B", "C"]:

        x = comparison[
            comparison["공식"] == mode
        ]

        c20 = x[
            x["전략"] == "C"
        ]

        c60 = x[
            x["전략"] == "C"
        ]

        if not c20.empty:

            r20 = c20.iloc[0]

            st.write(
                f"**{mode}안 · 미래테마 + 선행**"
            )

            st.write(
                f"20일 평균 "
                f"**{r20['20일 평균수익률']:+.2f}%**, "
                f"승률 "
                f"**{r20['20일 승률']:.1f}%**"
            )

            st.write(
                f"60일 평균 "
                f"**{r20['60일 평균수익률']:+.2f}%**, "
                f"승률 "
                f"**{r20['60일 승률']:.1f}%**"
            )


    # ========================================================
    # ② FORMULA COMPARISON
    # ========================================================

    st.subheader(
        "② A/B/C 점수공식 비교"
    )

    display = comparison.copy()

    for col in [
        "20일 평균수익률",
        "60일 평균수익률",
    ]:
        display[col] = display[col].round(2)

    for col in [
        "20일 승률",
        "60일 승률",
    ]:
        display[col] = display[col].round(1)

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )

    st.success(
        "여기서 C안이 기존 A안보다 실제 전략 성과까지 "
        "좋아졌는지가 핵심입니다."
    )


    # ========================================================
    # ③ EXISTING STRATEGY
    # ========================================================

    st.subheader(
        "③ C안 기준 전략 비교"
    )

    cdata = formula_data["C"]

    rows = []

    for signal in [
        "A",
        "B",
        "C",
        "D"
    ]:

        s20 = strategy_summary(
            cdata,
            signal,
            20
        )

        s60 = strategy_summary(
            cdata,
            signal,
            60
        )

        rows.append({
            "전략": signal,
            "20일 건수": s20["건수"],
            "20일 평균": s20["평균수익률"],
            "20일 승률": s20["승률"],
            "60일 건수": s60["건수"],
            "60일 평균": s60["평균수익률"],
            "60일 승률": s60["승률"],
        })

    st.dataframe(
        pd.DataFrame(rows).round(2),
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # ④ YEAR
    # ========================================================

    st.subheader(
        "④ 연도별 검증 · C안"
    )

    yd = cdata.copy()

    yd["연도"] = pd.to_datetime(
        yd["진입일"]
    ).dt.year

    year_rows = []

    for year, g in yd.groupby("연도"):

        r20 = g["20일수익률"].dropna()
        r60 = g["60일수익률"].dropna()

        year_rows.append({
            "연도": year,
            "건수": len(g),
            "20일 평균":
                r20.mean(),
            "20일 승률":
                (r20 > 0).mean() * 100
                if len(r20) else np.nan,
            "60일 평균":
                r60.mean(),
            "60일 승률":
                (r60 > 0).mean() * 100
                if len(r60) else np.nan,
        })

    st.dataframe(
        pd.DataFrame(year_rows).round(2),
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # ⑤ THEME
    # ========================================================

    st.subheader(
        "⑤ 어떤 테마가 실제로 잘 작동했는가"
    )

    theme20 = diagnostic_table(
        cdata,
        "테마",
        20
    )

    theme60 = diagnostic_table(
        cdata,
        "테마",
        60
    )

    st.write("20일")

    st.dataframe(
        theme20.round(2),
        use_container_width=True,
        hide_index=True
    )

    st.write("60일")

    st.dataframe(
        theme60.round(2),
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # ⑥ DIAGNOSTIC
    # ========================================================

    st.subheader(
        "⑥ 전략 진단"
    )

    ret20 = cdata[
        "20일수익률"
    ].dropna()

    score_corr = score_correlation(
        cdata,
        "선행점수",
        "20일수익률"
    )

    theme_corr = score_correlation(
        cdata,
        "테마점수",
        "20일수익률"
    )

    buy_ratio = (
        (
            cdata["가격상태"]
            == "매수구간"
        ).mean()
        * 100
    )

    d1, d2, d3, d4 = st.columns(4)

    d1.metric(
        "전체 검사",
        len(cdata)
    )

    d2.metric(
        "선행점수 ↔ 20일",
        f"{score_corr:+.2f}"
    )

    d3.metric(
        "테마점수 ↔ 20일",
        f"{theme_corr:+.2f}"
    )

    d4.metric(
        "매수구간 비율",
        f"{buy_ratio:.1f}%"
    )


    # --------------------------------------------------------
    # ⑥-1
    # --------------------------------------------------------

    st.markdown(
        "### ⑥-1 선행점수 구간별"
    )

    score_bins = [
        -np.inf,
        60,
        70,
        80,
        90,
        np.inf
    ]

    score_labels = [
        "60 이하",
        "60~70",
        "70~80",
        "80~90",
        "90 이상",
    ]

    temp = cdata.copy()

    temp["선행점수구간"] = pd.cut(
        temp["선행점수"],
        bins=score_bins,
        labels=score_labels
    )

    st.dataframe(
        diagnostic_table(
            temp,
            "선행점수구간",
            20
        ).round(2),
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # ⑥-2
    # --------------------------------------------------------

    st.markdown(
        "### ⑥-2 테마점수 구간별"
    )

    theme_bins = [
        -np.inf,
        50,
        60,
        70,
        80,
        np.inf
    ]

    theme_labels = [
        "50 이하",
        "50~60",
        "60~70",
        "70~80",
        "80 이상",
    ]

    temp2 = cdata.copy()

    temp2["테마점수구간"] = pd.cut(
        temp2["테마점수"],
        bins=theme_bins,
        labels=theme_labels
    )

    st.dataframe(
        diagnostic_table(
            temp2,
            "테마점수구간",
            20
        ).round(2),
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # ⑥-3 ETF
    # --------------------------------------------------------

    st.markdown(
        "### ⑥-3 ETF별"
    )

    st.dataframe(
        diagnostic_table(
            cdata,
            "ETF",
            20
        ).sort_values(
            "평균수익률",
            ascending=False
        ).round(2),
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # ⑥-4 PRICE
    # --------------------------------------------------------

    st.markdown(
        "### ⑥-4 가격상태별"
    )

    st.dataframe(
        diagnostic_table(
            cdata,
            "가격상태",
            20
        ).round(2),
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # ⑥-5 SCORE COMPONENT
    # --------------------------------------------------------

    st.markdown(
        "### ⑥-5 선행점수 구성요소 검증"
    )

    components = [
        "가격점수",
        "RSI점수",
        "거래량점수",
        "가속도점수",
        "상대강도점수",
        "구조점수",
        "선행점수",
        "테마점수",
    ]

    corr_rows = []

    for component in components:

        corr_rows.append({
            "구성요소": component,
            "5일":
                score_correlation(
                    cdata,
                    component,
                    "5일수익률"
                ),
            "20일":
                score_correlation(
                    cdata,
                    component,
                    "20일수익률"
                ),
            "60일":
                score_correlation(
                    cdata,
                    component,
                    "60일수익률"
                ),
        })

    st.dataframe(
        pd.DataFrame(
            corr_rows
        ).round(3),
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # ⑥-6
    # --------------------------------------------------------

    st.markdown(
        "### ⑥-6 점수와 실제 수익률"
    )

    for horizon in [
        5,
        20,
        60
    ]:

        corr = score_correlation(
            cdata,
            "선행점수",
            f"{horizon}일수익률"
        )

        st.write(
            f"{horizon}일 : "
            f"**{corr:+.3f}**"
        )


    # --------------------------------------------------------
    # ⑥-7 AUTO DIAGNOSIS
    # --------------------------------------------------------

    st.markdown(
        "### ⑥-7 자동진단"
    )

    if score_corr < 0.10:

        st.warning(
            "현재 선행점수와 실제 20일 수익률의 "
            "관계가 약합니다."
        )

    elif score_corr < 0.20:

        st.info(
            "선행점수와 실제 수익률 사이에 "
            "약한 양의 관계가 있습니다."
        )

    else:

        st.success(
            "선행점수가 실제 수익률과 "
            "의미 있는 양의 관계를 보입니다."
        )


    if theme_corr < 0.10:

        st.warning(
            "테마점수와 실제 수익률의 관계도 "
            "아직 강하지 않습니다."
        )


    if len(ret20) > 0:

        worst = ret20.min()

        if worst <= -15:

            st.error(
                f"20일 기준 {worst:.2f}%의 큰 손실 거래가 "
                "존재합니다. 손실관리 검토가 필요합니다."
            )


    # ========================================================
    # ⑦ STOP LOSS
    # ========================================================

    st.subheader(
        "⑦ 손실관리 테스트"
    )

    s1, s2 = st.columns(2)

    stop_strategy = s1.selectbox(
        "검증 전략",
        [
            "A · 단순테마",
            "B · 선행점수",
            "C · 미래테마 + 선행",
            "D · 미래테마 + 선행 + 가격",
        ],
        index=2
    )

    stop_horizon = s2.selectbox(
        "검증 기간",
        [20, 60],
        index=0
    )

    stop_col = {
        "A · 단순테마": "A",
        "B · 선행점수": "B",
        "C · 미래테마 + 선행": "C",
        "D · 미래테마 + 선행 + 가격": "D",
    }[stop_strategy]

    stop_result = stop_loss_test(
        cdata,
        stop_col,
        stop_horizon
    )

    st.dataframe(
        stop_result.round(2),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "주의: 현재 CSV에는 일별 가격경로가 없으므로 "
        "손절 발생 여부는 기간 최대낙폭을 이용한 연구용 근사치입니다."
    )


    # ========================================================
    # ⑧ FORMULA COMPONENT VALIDATION
    # ========================================================

    st.subheader(
        "⑧ 선행점수 구성요소 검증"
    )

    st.write(
        "구성요소별로 실제 미래수익률과 어느 정도 "
        "연결되는지 확인합니다."
    )

    st.dataframe(
        pd.DataFrame(
            corr_rows
        ).round(3),
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "상관계수는 인과관계를 의미하지 않습니다. "
        "다른 기간·다른 ETF에서도 반복되는지 확인해야 합니다."
    )


    # ========================================================
    # ⑨ 1M SIMULATION
    # ========================================================

    st.subheader(
        "⑨ 100만원 가상투자 시뮬레이션"
    )

    sc1, sc2 = st.columns(2)

    sim_strategy = sc1.selectbox(
        "시뮬레이션 전략",
        [
            "A · 단순테마",
            "B · 선행점수",
            "C · 미래테마 + 선행",
            "D · 미래테마 + 선행 + 가격",
        ],
        index=2
    )

    hold_days = sc2.selectbox(
        "보유기간",
        [5, 20, 60],
        index=1,
        key="sim_hold"
    )

    sim_col = {
        "A · 단순테마": "A",
        "B · 선행점수": "B",
        "C · 미래테마 + 선행": "C",
        "D · 미래테마 + 선행 + 가격": "D",
    }[sim_strategy]

    if st.button(
        "💰 시뮬레이션 실행",
        use_container_width=True
    ):

        curve, metrics = simulate_equity_curve(
            cdata,
            sim_col,
            hold_days
        )

        st.session_state[
            "sim_curve"
        ] = curve

        st.session_state[
            "sim_metrics"
        ] = metrics

    sim_curve = st.session_state.get(
        "sim_curve"
    )

    sim_metrics = st.session_state.get(
        "sim_metrics"
    )

    if sim_metrics:

        m1, m2, m3, m4 = st.columns(4)

        m1.metric(
            "최종자산",
            f"{sim_metrics['최종자산']:,.0f}원"
        )

        m2.metric(
            "총수익률",
            f"{sim_metrics['총수익률']:+.2f}%"
        )

        m3.metric(
            "거래수",
            f"{sim_metrics['거래수']}"
        )

        m4.metric(
            "승률",
            f"{sim_metrics['승률']:.1f}%"
        )

        if sim_curve is not None and not sim_curve.empty:

            st.line_chart(
                sim_curve.set_index(
                    "진입일"
                )["자산"]
            )

            csv_sim = sim_curve.to_csv(
                index=False
            ).encode("utf-8-sig")

            st.download_button(
                "📥 시뮬레이션 CSV 다운로드",
                csv_sim,
                file_name=(
                    "ETF_RADAR_100만원_거래내역.csv"
                ),
                mime="text/csv",
                use_container_width=True
            )


    # ========================================================
    # ⑩ RAW DATA
    # ========================================================

    st.subheader(
        "⑩ 원본 백테스트 데이터"
    )

    st.dataframe(
        cdata,
        use_container_width=True,
        hide_index=True
    )

    csv_data = cdata.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 ETF_RADAR_STRATEGY_BACKTEST.csv 다운로드",
        csv_data,
        file_name=(
            "ETF_RADAR_STRATEGY_BACKTEST.csv"
        ),
        mime="text/csv",
        use_container_width=True
    )


    # ========================================================
    # FINAL JUDGMENT
    # ========================================================

    st.subheader(
        "⑪ 최종 판단"
    )

    comp_c = comparison[
        (
            comparison["공식"] == "C"
        )
        &
        (
            comparison["전략"] == "C"
        )
    ]

    comp_a = comparison[
        (
            comparison["공식"] == "A"
        )
        &
        (
            comparison["전략"] == "C"
        )
    ]

    if (
        not comp_c.empty
        and not comp_a.empty
    ):

        a20 = comp_a.iloc[0][
            "20일 평균수익률"
        ]

        c20 = comp_c.iloc[0][
            "20일 평균수익률"
        ]

        a60 = comp_a.iloc[0][
            "60일 평균수익률"
        ]

        c60 = comp_c.iloc[0][
            "60일 평균수익률"
        ]

        diff20 = c20 - a20
        diff60 = c60 - a60

        st.write(
            f"**C안 - A안 차이**"
        )

        st.write(
            f"20일 : **{diff20:+.2f}%p**"
        )

        st.write(
            f"60일 : **{diff60:+.2f}%p**"
        )

        if diff20 > 0 and diff60 > 0:

            st.success(
                "C안이 20일과 60일 모두에서 "
                "A안보다 개선되었습니다. "
                "다음 단계에서 C안 채택을 검토할 수 있습니다."
            )

        elif diff20 > 0 or diff60 > 0:

            st.warning(
                "C안이 한쪽 기간에서는 개선됐지만 "
                "모든 기간에서 우위는 아닙니다. "
                "추가 검증이 필요합니다."
            )

        else:

            st.error(
                "C안이 현재식보다 개선되지 않았습니다. "
                "현재식을 유지하는 것이 좋습니다."
            )


st.caption(
    "ETF RADAR STRATEGY TEST · Research Only"
)