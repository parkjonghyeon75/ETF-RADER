# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date


# ============================================================
# ETF RADAR STRATEGY TEST
# 미래테마 → 선행 ETF → 과열 필터 → 가격구간
# 실제 과거 데이터 검증 + 손실관리 + 점수 구성요소 검증
# ============================================================

st.set_page_config(
    page_title="ETF RADAR STRATEGY TEST",
    page_icon="🧪",
    layout="wide"
)


# ============================================================
# SESSION STATE
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
    "방어자산": ["GLD", "TLT"],
    "글로벌": ["INDA", "EWY", "EWJ", "EEM"],
}


# ============================================================
# DATA
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def download_prices(tickers, start, end):

    tickers = list(dict.fromkeys(tickers))

    if BENCH not in tickers:
        tickers.append(BENCH)

    try:
        data = yf.download(
            tickers,
            start=start,
            end=end,
            auto_adjust=True,
            progress=False,
            group_by="column",
        )

        if data is None or data.empty:
            return pd.DataFrame()

        if isinstance(data.columns, pd.MultiIndex):

            if "Close" in data.columns.get_level_values(0):
                data = data["Close"]

            elif "Adj Close" in data.columns.get_level_values(0):
                data = data["Adj Close"]

        else:

            if "Close" in data.columns:
                data = data[["Close"]]

        if isinstance(data, pd.Series):
            data = data.to_frame()

        data = data.sort_index()
        data = data.ffill()

        return data

    except Exception:
        return pd.DataFrame()


# ============================================================
# INDICATORS
# ============================================================

def indicators(s):

    s = pd.Series(s).astype(float)

    ma20 = s.rolling(20).mean()
    ma60 = s.rolling(60).mean()

    r5 = s.pct_change(5) * 100
    r20 = s.pct_change(20) * 100
    r60 = s.pct_change(60) * 100

    vol20 = s.pct_change().rolling(20).std() * np.sqrt(252) * 100

    low20 = s.rolling(20).min()
    high20 = s.rolling(20).max()

    vr = (
        s.pct_change().abs().rolling(5).mean()
        /
        s.pct_change().abs().rolling(20).mean()
    )

    delta = s.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    return pd.DataFrame({
        "price": s,
        "MA20": ma20,
        "MA60": ma60,
        "R5": r5,
        "R20": r20,
        "R60": r60,
        "VR": vr,
        "RSI": rsi,
        "VOL20": vol20,
        "LOW20": low20,
        "HIGH20": high20,
    })


# ============================================================
# SCORE UTILITY
# ============================================================

def clip_score(x):
    if pd.isna(x):
        return 50.0
    return float(np.clip(x, 0, 100))


# ============================================================
# LEADING SIGNAL
# ============================================================

def leading_signal(hist, bench_hist):

    if len(hist) < 65 or len(bench_hist) < 65:
        return None

    x = indicators(hist)
    b = indicators(bench_hist)

    row = x.iloc[-1]
    brow = b.iloc[-1]

    current = row["price"]
    ma20 = row["MA20"]
    ma60 = row["MA60"]

    r5 = row["R5"]
    r20 = row["R20"]

    vr = row["VR"]
    rsi = row["RSI"]

    if pd.isna(current) or pd.isna(ma20) or pd.isna(ma60):
        return None

    if pd.isna(r5) or pd.isna(r20):
        return None

    if pd.isna(vr):
        vr = 1.0

    if pd.isna(rsi):
        rsi = 50.0

    # --------------------------------------------------------
    # 상대강도
    # --------------------------------------------------------

    bench_ret20 = brow["R20"]

    if pd.isna(bench_ret20):
        bench_ret20 = 0.0

    rs20 = r20 - bench_ret20

    # --------------------------------------------------------
    # 가속도
    # --------------------------------------------------------

    accel = r5 - r20 / 4

    # --------------------------------------------------------
    # 기존 점수 구성요소
    # --------------------------------------------------------

    # 가격
    if current >= ma20:
        early_price = 60 + min(
            40,
            max(
                0,
                ((current / ma20) - 1) * 100 * 10
            )
        )
    else:
        early_price = max(
            0,
            50 - ((ma20 / current) - 1) * 100 * 8
        )

    # RSI
    if 50 <= rsi <= 65:
        early_rsi = 90
    elif 45 <= rsi < 50:
        early_rsi = 75
    elif 65 < rsi <= 70:
        early_rsi = 70
    elif 40 <= rsi < 45:
        early_rsi = 55
    elif 70 < rsi <= 75:
        early_rsi = 45
    else:
        early_rsi = 30

    # 거래량
    flow = clip_score(
        50 + (vr - 1.0) * 100
    )

    # 가속도
    accel_score = clip_score(
        50 + accel * 8
    )

    # 상대강도
    rel = clip_score(
        50 + rs20 * 4
    )

    # 추세구조
    structure = 50

    if current > ma20:
        structure += 20

    if ma20 > ma60:
        structure += 20

    if r20 > 0:
        structure += 10

    if r60 > 0:
        structure += 10

    structure = clip_score(structure)

    # --------------------------------------------------------
    # 기존 선행점수
    # --------------------------------------------------------

    score = (
        early_price * 0.22
        + early_rsi * 0.18
        + flow * 0.22
        + accel_score * 0.16
        + rel * 0.14
        + structure * 0.08
    )

    dist20 = (
        (current / ma20) - 1
    ) * 100

    early_buy = (
        score >= 72
        and vr >= 1.05
        and rsi < 70
        and dist20 < 7
        and rs20 >= -1
    )

    return {
        "current": current,
        "ma20": ma20,
        "ma60": ma60,
        "r5": r5,
        "r20": r20,
        "r60": row["R60"],
        "vr": vr,
        "rsi": rsi,
        "dist20": dist20,
        "rs20": rs20,
        "accel": accel,

        "early_price": early_price,
        "early_rsi": early_rsi,
        "flow": flow,
        "accel_score": accel_score,
        "rel": rel,
        "structure": structure,

        "score": score,
        "early_buy": early_buy,
    }


# ============================================================
# THEME SCORE
# ============================================================

def theme_score(
    theme,
    date_idx,
    prices,
    bench_hist
):

    members = THEME_GROUPS.get(theme, [])

    rows = []

    for ticker in members:

        if ticker not in prices.columns:
            continue

        hist = prices[ticker].loc[:date_idx].dropna()

        if len(hist) < 65:
            continue

        sig = leading_signal(
            hist,
            bench_hist.loc[:date_idx].dropna()
        )

        if sig is None:
            continue

        rows.append(sig)

    if not rows:
        return None

    scores = [x["score"] for x in rows]

    lead_avg = float(np.mean(scores))

    early_ratio = (
        np.mean(
            [x["early_buy"] for x in rows]
        ) * 100
    )

    breadth = (
        np.mean(
            [x["r20"] > 0 for x in rows]
        ) * 100
    )

    heat = max(
        0,
        np.mean(
            [
                max(0, x["dist20"])
                for x in rows
            ]
        )
    )

    score = (
        lead_avg * 0.55
        + breadth * 0.25
        + early_ratio * 0.20
    )

    if heat > 10:
        score -= (heat - 10) * 1.2

    score = clip_score(score)

    if score >= 75:
        stage = "초기상승"
    elif score >= 65:
        stage = "상승준비"
    elif score >= 55:
        stage = "관찰"
    elif score >= 45:
        stage = "약세"
    else:
        stage = "회피"

    return {
        "theme": theme,
        "theme_score": score,
        "breadth": breadth,
        "lead_avg": lead_avg,
        "early_ratio": early_ratio,
        "heat": heat,
        "stage": stage,
        "members": rows,
    }


# ============================================================
# PRICE ZONE
# ============================================================

def price_zone(sig):

    if sig is None:
        return "데이터부족"

    current = sig["current"]
    ma20 = sig["ma20"]
    rsi = sig["rsi"]
    dist20 = sig["dist20"]

    if current < ma20 * 0.93:
        return "무효"

    if rsi >= 75 or dist20 >= 10:
        return "추격금지"

    if current >= ma20 and dist20 <= 5:
        return "매수구간"

    return "눌림대기"


# ============================================================
# BUILD SNAPSHOT
# ============================================================

def build_snapshot(
    date_idx,
    prices,
    bench_prices
):

    bench_hist = bench_prices.loc[:date_idx].dropna()

    theme_rows = []

    for theme in THEME_GROUPS:

        ts = theme_score(
            theme,
            date_idx,
            prices,
            bench_hist
        )

        if ts is not None:
            theme_rows.append(ts)

    if not theme_rows:
        return None

    theme_rows = sorted(
        theme_rows,
        key=lambda x: x["theme_score"],
        reverse=True
    )

    best_theme = theme_rows[0]

    candidate_rows = []

    for member in best_theme["members"]:

        ticker = None

        for t, name in POOL.items():
            if name == best_theme["theme"]:
                pass

        # members에는 ticker가 없으므로
        # theme 구성종목을 다시 확인
        for t in THEME_GROUPS.get(
            best_theme["theme"],
            []
        ):
            if t in prices.columns:

                hist = prices[t].loc[:date_idx].dropna()

                if len(hist) < 65:
                    continue

                sig = leading_signal(
                    hist,
                    bench_hist
                )

                if sig is None:
                    continue

                heat_penalty = max(
                    0,
                    sig["dist20"] - 7
                ) * 1.5

                final_score = (
                    sig["score"]
                    - heat_penalty
                )

                candidate_rows.append(
                    (
                        t,
                        sig,
                        heat_penalty,
                        final_score
                    )
                )

    if not candidate_rows:
        return None

    candidate_rows.sort(
        key=lambda x: x[3],
        reverse=True
    )

    ticker, sig, heat_penalty, final_score = (
        candidate_rows[0]
    )

    pzone = price_zone(sig)

    return {
        "theme": best_theme["theme"],
        "theme_score": best_theme["theme_score"],
        "theme_stage": best_theme["stage"],
        "breadth": best_theme["breadth"],
        "theme_lead_avg": best_theme["lead_avg"],
        "theme_early_ratio": best_theme["early_ratio"],
        "theme_heat": best_theme["heat"],

        "ticker": ticker,
        "leading_score": sig["score"],
        "heat_score": heat_penalty,
        "price_state": pzone,
        "price": sig["current"],

        "early_price": sig["early_price"],
        "early_rsi": sig["early_rsi"],
        "flow": sig["flow"],
        "accel_score": sig["accel_score"],
        "relative_score": sig["rel"],
        "structure_score": sig["structure"],

        "r5": sig["r5"],
        "r20": sig["r20"],
        "r60": sig["r60"],
        "vr": sig["vr"],
        "rsi": sig["rsi"],
        "dist20": sig["dist20"],
        "rs20": sig["rs20"],
        "accel": sig["accel"],
    }


# ============================================================
# BACKTEST
# ============================================================

def run_strategy_backtest(
    start,
    end,
    tickers,
    step_days=5
):

    tickers = list(
        dict.fromkeys(tickers)
    )

    data = download_prices(
        tickers,
        start,
        end
    )

    if data.empty:
        return pd.DataFrame()

    if BENCH not in data.columns:
        return pd.DataFrame()

    required = [
        x for x in tickers
        if x in data.columns
    ]

    if not required:
        return pd.DataFrame()

    prices = data[required].copy()
    bench = data[BENCH].copy()

    common = prices.index.intersection(
        bench.dropna().index
    )

    prices = prices.loc[common]
    bench = bench.loc[common]

    prices = prices.ffill()

    rows = []

    dates = list(prices.index)

    start_pos = 65

    for i in range(
        start_pos,
        len(dates),
        step_days
    ):

        d = dates[i]

        snap = build_snapshot(
            d,
            prices,
            bench
        )

        if snap is None:
            continue

        ticker = snap["ticker"]

        if ticker not in prices.columns:
            continue

        future_dates = dates[i + 1:]

        if len(future_dates) == 0:
            continue

        entry_date = future_dates[0]

        entry_price = prices.loc[
            entry_date,
            ticker
        ]

        if pd.isna(entry_price):
            continue

        row = {
            "날짜": d,
            "진입일": entry_date,
            "테마": snap["theme"],
            "테마점수": snap["theme_score"],
            "테마단계": snap["theme_stage"],
            "ETF": ticker,
            "선행점수": snap["leading_score"],
            "과열점수": snap["heat_score"],
            "가격상태": snap["price_state"],
            "매수가": entry_price,

            "가격점수": snap["early_price"],
            "RSI점수": snap["early_rsi"],
            "거래량점수": snap["flow"],
            "가속도점수": snap["accel_score"],
            "상대강도점수": snap["relative_score"],
            "구조점수": snap["structure_score"],

            "R5": snap["r5"],
            "R20": snap["r20"],
            "R60": snap["r60"],
            "VR": snap["vr"],
            "RSI": snap["rsi"],
            "MA20이격": snap["dist20"],
            "상대강도": snap["rs20"],
            "가속도": snap["accel"],
        }

        # ----------------------------------------------------
        # 미래 수익률
        # ----------------------------------------------------

        for horizon in [5, 20, 60]:

            future_idx = i + 1 + horizon - 1

            if future_idx < len(dates):

                exit_date = dates[future_idx]

                exit_price = prices.loc[
                    exit_date,
                    ticker
                ]

                ret = (
                    exit_price / entry_price - 1
                ) * 100

                row[
                    f"{horizon}일수익률"
                ] = ret

                # 진입 후 최대낙폭
                window = prices.loc[
                    entry_date:exit_date,
                    ticker
                ].dropna()

                if len(window):

                    running_max = (
                        window.cummax()
                    )

                    dd = (
                        window / running_max - 1
                    ) * 100

                    row[
                        f"{horizon}일최대낙폭"
                    ] = dd.min()

                else:
                    row[
                        f"{horizon}일최대낙폭"
                    ] = np.nan

            else:

                row[
                    f"{horizon}일수익률"
                ] = np.nan

                row[
                    f"{horizon}일최대낙폭"
                ] = np.nan

        # ----------------------------------------------------
        # 전략 A/B/C/D
        # ----------------------------------------------------

        row["A"] = (
            row["테마점수"] >= 55
        )

        row["B"] = (
            row["선행점수"] >= 72
        )

        row["C"] = (
            row["테마점수"] >= 55
            and row["선행점수"] >= 72
        )

        row["D"] = (
            row["테마점수"] >= 55
            and row["선행점수"] >= 72
            and row["가격상태"] == "매수구간"
        )

        rows.append(row)

    return pd.DataFrame(rows)


# ============================================================
# SUMMARY
# ============================================================

def strategy_summary(
    df,
    strategy_col,
    horizon
):

    if df.empty:
        return {
            "신호수": 0,
            "승률": np.nan,
            "평균수익률": np.nan,
            "중앙값": np.nan,
            "평균낙폭": np.nan,
            "최고": np.nan,
            "최저": np.nan,
        }

    col = f"{horizon}일수익률"
    dd_col = f"{horizon}일최대낙폭"

    x = df[
        df[strategy_col] == True
    ].copy()

    r = pd.to_numeric(
        x[col],
        errors="coerce"
    ).dropna()

    dd = pd.to_numeric(
        x[dd_col],
        errors="coerce"
    ).dropna()

    if len(r) == 0:
        return {
            "신호수": 0,
            "승률": np.nan,
            "평균수익률": np.nan,
            "중앙값": np.nan,
            "평균낙폭": np.nan,
            "최고": np.nan,
            "최저": np.nan,
        }

    return {
        "신호수": len(r),
        "승률": (
            (r > 0).mean() * 100
        ),
        "평균수익률": r.mean(),
        "중앙값": r.median(),
        "평균낙폭": (
            dd.mean()
            if len(dd)
            else np.nan
        ),
        "최고": r.max(),
        "최저": r.min(),
    }


# ============================================================
# DIAGNOSTIC
# ============================================================

def diagnostic_table(
    df,
    group_col,
    horizon=20
):

    if df.empty or group_col not in df.columns:
        return pd.DataFrame()

    ret_col = f"{horizon}일수익률"

    rows = []

    for key, g in df.groupby(
        group_col,
        dropna=False
    ):

        r = pd.to_numeric(
            g[ret_col],
            errors="coerce"
        ).dropna()

        if len(r) == 0:
            continue

        rows.append({
            group_col: key,
            "표본": len(r),
            "승률": (r > 0).mean() * 100,
            "평균수익률": r.mean(),
            "중앙값": r.median(),
            "최고": r.max(),
            "최저": r.min(),
            "수익률합": r.sum(),
        })

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).sort_values(
        "평균수익률",
        ascending=False
    )


def score_correlation(
    df,
    score_col,
    return_col
):

    if (
        df.empty
        or score_col not in df.columns
        or return_col not in df.columns
    ):
        return np.nan

    x = pd.DataFrame({
        "score": pd.to_numeric(
            df[score_col],
            errors="coerce"
        ),
        "ret": pd.to_numeric(
            df[return_col],
            errors="coerce"
        )
    }).dropna()

    if len(x) < 3:
        return np.nan

    return x["score"].corr(
        x["ret"]
    )


def component_correlation_table(df):

    components = {
        "가격점수": "가격점수",
        "RSI점수": "RSI점수",
        "거래량점수": "거래량점수",
        "가속도점수": "가속도점수",
        "상대강도점수": "상대강도점수",
        "구조점수": "구조점수",
        "선행점수": "선행점수",
        "테마점수": "테마점수",
        "과열점수": "과열점수",
    }

    rows = []

    for name, col in components.items():

        rows.append({
            "구성요소": name,
            "5일": score_correlation(
                df,
                col,
                "5일수익률"
            ),
            "20일": score_correlation(
                df,
                col,
                "20일수익률"
            ),
            "60일": score_correlation(
                df,
                col,
                "60일수익률"
            ),
        })

    return pd.DataFrame(rows)


# ============================================================
# LOSS CONTROL BACKTEST
# ============================================================

def simulate_stop_strategy(
    df,
    strategy_col,
    stop_pct,
    horizon=20
):

    if df.empty:
        return None

    if strategy_col not in df.columns:
        return None

    rows = []

    for _, row in df.iterrows():

        if not bool(row[strategy_col]):
            continue

        entry = row["매수가"]
        ticker = row["ETF"]
        entry_date = row["진입일"]

        if pd.isna(entry):
            continue

        # ----------------------------------------------------
        # 이미 계산된 고정기간 수익률
        # ----------------------------------------------------

        base_ret = row[
            f"{horizon}일수익률"
        ]

        base_dd = row[
            f"{horizon}일최대낙폭"
        ]

        if pd.isna(base_ret):
            continue

        # 손절 없음
        if stop_pct is None:
            result_ret = base_ret
            stopped = False

        else:

            # 최대낙폭이 손절선 이하라면
            # 실제로 해당 기간 중 손절에 걸린 것으로 간주
            if (
                not pd.isna(base_dd)
                and base_dd <= stop_pct
            ):
                result_ret = stop_pct
                stopped = True

            else:
                result_ret = base_ret
                stopped = False

        rows.append({
            "ETF": ticker,
            "진입일": entry_date,
            "기본수익률": base_ret,
            "최대낙폭": base_dd,
            "손절수익률": result_ret,
            "손절발생": stopped,
        })

    if not rows:
        return None

    r = pd.Series(
        [x["손절수익률"] for x in rows]
    )

    dd = pd.Series(
        [x["최대낙폭"] for x in rows]
    )

    stopped = pd.Series(
        [x["손절발생"] for x in rows]
    )

    return {
        "손절": (
            "없음"
            if stop_pct is None
            else f"{stop_pct:.0f}%"
        ),
        "거래수": len(r),
        "승률": (r > 0).mean() * 100,
        "평균수익률": r.mean(),
        "중앙값": r.median(),
        "최고": r.max(),
        "최저": r.min(),
        "평균낙폭": dd.mean(),
        "손절발생률": stopped.mean() * 100,
        "누적단순수익률": r.sum(),
    }


def loss_control_table(
    df,
    strategy_col="C",
    horizon=20
):

    levels = [
        None,
        -5,
        -7,
        -10,
        -12,
        -15,
    ]

    rows = []

    for level in levels:

        result = simulate_stop_strategy(
            df,
            strategy_col,
            level,
            horizon
        )

        if result:
            rows.append(result)

    return pd.DataFrame(rows)


# ============================================================
# AUTOMATIC DIAGNOSTIC MESSAGE
# ============================================================

def build_diagnostic_messages(df):

    messages = []

    corr_lead = score_correlation(
        df,
        "선행점수",
        "20일수익률"
    )

    corr_theme = score_correlation(
        df,
        "테마점수",
        "20일수익률"
    )

    if not pd.isna(corr_lead):

        if corr_lead < 0:
            messages.append(
                f"⚠ 선행점수가 높을수록 오히려 수익률이 낮은 "
                f"역관계가 관찰됩니다. 상관계수 {corr_lead:+.2f}"
            )

        elif corr_lead < 0.15:
            messages.append(
                f"선행점수와 20일 수익률의 관계가 약합니다. "
                f"현재 상관계수 {corr_lead:+.2f}"
            )

        else:
            messages.append(
                f"선행점수와 20일 수익률 사이에 "
                f"양의 관계가 확인됩니다. {corr_lead:+.2f}"
            )

    if not pd.isna(corr_theme):

        if corr_theme < 0:
            messages.append(
                f"⚠ 테마점수와 수익률 사이에 역관계가 있습니다. "
                f"상관계수 {corr_theme:+.2f}"
            )

        elif corr_theme < 0.15:
            messages.append(
                f"테마점수와 실제 수익률의 관계가 아직 뚜렷하지 않습니다. "
                f"상관계수 {corr_theme:+.2f}"
            )

        else:
            messages.append(
                f"테마점수와 수익률 사이에 양의 관계가 확인됩니다. "
                f"상관계수 {corr_theme:+.2f}"
            )

    if (
        "가격상태" in df.columns
        and len(df) > 0
    ):

        buy_ratio = (
            (
                df["가격상태"] == "매수구간"
            ).mean() * 100
        )

        if buy_ratio >= 90:
            messages.append(
                f"⚠ 매수구간 비율이 {buy_ratio:.1f}%로 너무 높습니다. "
                f"가격필터가 충분히 차별화되지 않습니다."
            )

        elif buy_ratio <= 20:
            messages.append(
                f"매수구간 비율이 {buy_ratio:.1f}%로 낮습니다. "
                f"가격필터가 지나치게 엄격할 가능성이 있습니다."
            )

    worst = pd.to_numeric(
        df["20일수익률"],
        errors="coerce"
    ).min()

    if not pd.isna(worst):

        if worst <= -15:
            messages.append(
                f"⚠ 20일 기준 {worst:.2f}%의 큰 손실 거래가 존재합니다. "
                f"진입 필터뿐 아니라 손실관리 조건을 검토할 필요가 있습니다."
            )

        elif worst <= -10:
            messages.append(
                f"20일 기준 최악의 거래가 {worst:.2f}%입니다. "
                f"손실관리 테스트가 필요합니다."
            )

    return messages


# ============================================================
# SIMULATION
# ============================================================

def simulate_equity_curve(
    df,
    strategy_col="D",
    hold_days=20,
    initial_capital=1_000_000,
    fee_pct=0.05,
    slippage_pct=0.05
):

    if df.empty:
        return pd.DataFrame(), {}

    signals = df[
        df[strategy_col] == True
    ].copy()

    signals = signals.sort_values(
        "진입일"
    )

    capital = float(
        initial_capital
    )

    curve = []

    last_exit = None

    trades = []

    for _, row in signals.iterrows():

        entry_date = row["진입일"]

        if (
            last_exit is not None
            and entry_date <= last_exit
        ):
            continue

        ret = row[
            f"{hold_days}일수익률"
        ]

        if pd.isna(ret):
            continue

        total_cost = (
            fee_pct * 2
            + slippage_pct * 2
        )

        net_ret = ret - total_cost

        start_capital = capital

        capital *= (
            1 + net_ret / 100
        )

        exit_date = entry_date

        last_exit = exit_date

        trades.append({
            "진입일": entry_date,
            "ETF": row["ETF"],
            "테마": row["테마"],
            "수익률": ret,
            "비용반영수익률": net_ret,
            "시작자산": start_capital,
            "종료자산": capital,
        })

        curve.append({
            "날짜": entry_date,
            "자산": capital,
        })

    curve_df = pd.DataFrame(curve)

    if curve_df.empty:
        return curve_df, {}

    equity = curve_df["자산"]

    running_max = equity.cummax()

    dd = (
        equity / running_max - 1
    ) * 100

    returns = equity.pct_change().dropna()

    metrics = {
        "초기자산": initial_capital,
        "최종자산": capital,
        "총수익률": (
            capital / initial_capital - 1
        ) * 100,
        "거래수": len(trades),
        "승률": (
            np.mean(
                [
                    x["비용반영수익률"] > 0
                    for x in trades
                ]
            ) * 100
            if trades
            else np.nan
        ),
        "최대낙폭": dd.min(),
        "평균거래수익률": (
            np.mean(
                [
                    x["비용반영수익률"]
                    for x in trades
                ]
            )
            if trades
            else np.nan
        ),
    }

    return curve_df, metrics


# ============================================================
# FORMAT
# ============================================================

def format_table(df):

    if df.empty:
        return df

    out = df.copy()

    for col in out.columns:

        if (
            pd.api.types.is_float_dtype(
                out[col]
            )
            or pd.api.types.is_integer_dtype(
                out[col]
            )
        ):

            if (
                "승률" in str(col)
                or "수익률" in str(col)
                or "낙폭" in str(col)
                or "상관" in str(col)
                or "5일" == str(col)
                or "20일" == str(col)
                or "60일" == str(col)
            ):
                out[col] = out[col].map(
                    lambda x:
                    f"{x:.2f}%"
                    if pd.notna(x)
                    else "-"
                )

    return out


# ============================================================
# UI
# ============================================================

st.title("🧪 ETF RADAR STRATEGY TEST")

st.caption(
    "미래테마 → 선행 ETF → 과열 필터 → 가격구간까지 "
    "실제 투자 흐름을 과거 데이터로 검증합니다."
)

st.info(
    "이번 테스트의 목적은 기능을 더 만드는 것이 아니라, "
    "현재 ETF RADAR의 핵심 로직에 실제 투자 우위가 있는지 확인하는 것입니다."
)


# ============================================================
# INPUT
# ============================================================

c1, c2 = st.columns(2)

with c1:

    start_date = st.date_input(
        "시작일",
        value=date(2021, 1, 1)
    )

with c2:

    end_date = st.date_input(
        "종료일",
        value=date(2025, 12, 31)
    )


st.subheader("테스트 ETF")

default_tickers = [
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
]

selected_tickers = st.multiselect(
    "검증할 ETF",
    options=list(POOL.keys()),
    default=default_tickers,
    format_func=lambda x:
        f"{x} · {POOL[x]}"
)


step_label = st.selectbox(
    "검사 간격",
    [
        "5거래일마다",
        "매일",
        "10거래일마다",
    ],
    index=0
)

if step_label == "매일":
    step_days = 1
elif step_label == "10거래일마다":
    step_days = 10
else:
    step_days = 5


run_button = st.button(
    "🚀 전체 백테스트 실행",
    type="primary",
    use_container_width=True
)


# ============================================================
# RUN
# ============================================================

if run_button:

    if start_date >= end_date:
        st.error(
            "시작일은 종료일보다 이전이어야 합니다."
        )
        st.stop()

    if len(selected_tickers) < 2:
        st.error(
            "테스트 ETF를 2개 이상 선택해주세요."
        )
        st.stop()

    with st.spinner(
        "과거 데이터를 다운로드하고 전략을 계산하는 중입니다..."
    ):

        result = run_strategy_backtest(
            str(start_date),
            str(end_date),
            selected_tickers,
            step_days
        )

    if result.empty:

        st.error(
            "백테스트 결과가 없습니다. "
            "기간 또는 ETF 데이터를 확인해주세요."
        )

    else:

        st.session_state[
            "strategy_result"
        ] = result

        st.session_state[
            "strategy_data"
        ] = result

        st.success(
            f"검증 완료 · {len(result):,}개 검사 시점"
        )


# ============================================================
# RESULT
# ============================================================

r = st.session_state.get(
    "strategy_result"
)


if r is not None and not r.empty:

    st.divider()

    # ========================================================
    # ① 핵심 결과
    # ========================================================

    st.header(
        "① 한눈에 보는 핵심 결과"
    )

    result_cols = st.columns(4)

    for idx, horizon in enumerate(
        [20, 60]
    ):

        st.subheader(
            f"{horizon}일 성과"
        )

        for strategy, name in [
            ("A", "A 단순테마"),
            ("B", "B 선행점수"),
            ("C", "C 미래테마+선행"),
            ("D", "D 미래테마+선행+가격"),
        ]:

            s = strategy_summary(
                r,
                strategy,
                horizon
            )

            with result_cols[
                (idx * 2)
                + (0 if horizon == 20 else 1)
            ] if False else result_cols[0]:

                pass

            st.metric(
                name,
                (
                    f"{s['평균수익률']:+.2f}%"
                    if pd.notna(
                        s["평균수익률"]
                    )
                    else "-"
                ),
                (
                    f"승률 {s['승률']:.1f}%"
                    if pd.notna(
                        s["승률"]
                    )
                    else "-"
                )
            )

    # ========================================================
    # ② 전략 비교
    # ========================================================

    st.header(
        "② 전략 비교표"
    )

    rows = []

    for strategy, name in [
        ("A", "A 단순테마"),
        ("B", "B 선행점수"),
        ("C", "C 미래테마+선행"),
        ("D", "D 미래테마+선행+가격"),
    ]:

        s20 = strategy_summary(
            r,
            strategy,
            20
        )

        s60 = strategy_summary(
            r,
            strategy,
            60
        )

        rows.append({
            "전략": name,
            "20일 거래수": s20["신호수"],
            "20일 승률": s20["승률"],
            "20일 평균": s20["평균수익률"],
            "20일 중앙값": s20["중앙값"],
            "60일 승률": s60["승률"],
            "60일 평균": s60["평균수익률"],
            "60일 중앙값": s60["중앙값"],
            "60일 평균낙폭": s60["평균낙폭"],
        })

    comparison = pd.DataFrame(rows)

    st.dataframe(
        comparison.style.format({
            "20일 승률": "{:.1f}%",
            "20일 평균": "{:+.2f}%",
            "20일 중앙값": "{:+.2f}%",
            "60일 승률": "{:.1f}%",
            "60일 평균": "{:+.2f}%",
            "60일 중앙값": "{:+.2f}%",
            "60일 평균낙폭": "{:.2f}%",
        }),
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # ③ 연도별
    # ========================================================

    st.header(
        "③ 연도별 검증"
    )

    yearly_rows = []

    temp = r.copy()

    temp["연도"] = pd.to_datetime(
        temp["진입일"]
    ).dt.year

    for year, g in temp.groupby("연도"):

        row = {
            "연도": year
        }

        for strategy in [
            "A",
            "B",
            "C",
            "D"
        ]:

            x = g[
                g[strategy] == True
            ]["20일수익률"].dropna()

            row[
                f"{strategy} 평균"
            ] = (
                x.mean()
                if len(x)
                else np.nan
            )

            row[
                f"{strategy} 승률"
            ] = (
                (x > 0).mean() * 100
                if len(x)
                else np.nan
            )

        yearly_rows.append(row)

    yearly = pd.DataFrame(
        yearly_rows
    )

    st.dataframe(
        yearly.style.format(
            {
                col: (
                    "{:+.2f}%"
                    if "평균" in col
                    else "{:.1f}%"
                )
                for col in yearly.columns
                if col != "연도"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # ④ 테마
    # ========================================================

    st.header(
        "④ 어떤 테마가 실제로 잘 작동했는가"
    )

    theme_table = diagnostic_table(
        r,
        "테마",
        20
    )

    if not theme_table.empty:

        st.dataframe(
            theme_table.style.format({
                "승률": "{:.1f}%",
                "평균수익률": "{:+.2f}%",
                "중앙값": "{:+.2f}%",
                "최고": "{:+.2f}%",
                "최저": "{:+.2f}%",
                "수익률합": "{:+.2f}%",
            }),
            use_container_width=True,
            hide_index=True
        )

    # ========================================================
    # ⑤ 최종 판단
    # ========================================================

    st.header(
        "⑤ 최종 판단"
    )

    c20 = strategy_summary(
        r,
        "C",
        20
    )

    d20 = strategy_summary(
        r,
        "D",
        20
    )

    c60 = strategy_summary(
        r,
        "C",
        60
    )

    d60 = strategy_summary(
        r,
        "D",
        60
    )

    if (
        pd.notna(c20["평균수익률"])
        and pd.notna(d20["평균수익률"])
    ):

        diff20 = (
            d20["평균수익률"]
            - c20["평균수익률"]
        )

        diff60 = (
            d60["평균수익률"]
            - c60["평균수익률"]
        )

        st.write(
            f"가격구간 추가 효과: "
            f"20일 {diff20:+.2f}%p / "
            f"60일 {diff60:+.2f}%p"
        )

        if abs(diff20) < 0.2:

            st.info(
                "단기 기준으로 가격구간 추가 효과가 "
                "뚜렷하지 않습니다."
            )

        elif diff20 > 0:

            st.success(
                "단기 기준 가격구간 추가가 "
                "긍정적으로 작동했습니다."
            )

        else:

            st.warning(
                "단기 기준 가격구간 추가가 "
                "오히려 성과를 낮췄습니다."
            )

    # ========================================================
    # ⑥ STRATEGY DIAGNOSIS
    # ========================================================

    st.header(
        "⑥ 🔍 전략 진단"
    )

    st.caption(
        "현재 백테스트 결과를 이용해 어떤 점수·테마·ETF·가격조건이 "
        "실제 수익과 연결되는지 확인합니다. "
        "이 단계에서는 기존 투자로직을 변경하지 않습니다."
    )

    corr_lead = score_correlation(
        r,
        "선행점수",
        "20일수익률"
    )

    corr_theme = score_correlation(
        r,
        "테마점수",
        "20일수익률"
    )

    buy_ratio = (
        (
            r["가격상태"] == "매수구간"
        ).mean() * 100
    )

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "전체 검사",
        f"{len(r):,}건"
    )

    m2.metric(
        "선행점수↔20일수익",
        (
            f"{corr_lead:+.2f}"
            if pd.notna(corr_lead)
            else "-"
        )
    )

    m3.metric(
        "테마점수↔20일수익",
        (
            f"{corr_theme:+.2f}"
            if pd.notna(corr_theme)
            else "-"
        )
    )

    st.metric(
        "'매수구간' 비율",
        f"{buy_ratio:.1f}%"
    )

    # --------------------------------------------------------
    # ⑥-1
    # --------------------------------------------------------

    st.subheader(
        "⑥-1 선행점수 구간별 성과"
    )

    score_bins = [
        -np.inf,
        70,
        80,
        85,
        90,
        np.inf,
    ]

    score_labels = [
        "70 미만",
        "70~80",
        "80~85",
        "85~90",
        "90 이상",
    ]

    temp = r.copy()

    temp["선행점수구간"] = pd.cut(
        temp["선행점수"],
        bins=score_bins,
        labels=score_labels
    )

    score_table = diagnostic_table(
        temp,
        "선행점수구간",
        20
    )

    if not score_table.empty:

        st.dataframe(
            score_table.style.format({
                "승률": "{:.1f}%",
                "평균수익률": "{:+.2f}%",
                "중앙값": "{:+.2f}%",
                "최고": "{:+.2f}%",
                "최저": "{:+.2f}%",
                "수익률합": "{:+.2f}%",
            }),
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # ⑥-2
    # --------------------------------------------------------

    st.subheader(
        "⑥-2 테마점수 구간별 성과"
    )

    theme_bins = [
        -np.inf,
        50,
        60,
        70,
        80,
        np.inf,
    ]

    theme_labels = [
        "50 미만",
        "50~60",
        "60~70",
        "70~80",
        "80 이상",
    ]

    temp["테마점수구간"] = pd.cut(
        temp["테마점수"],
        bins=theme_bins,
        labels=theme_labels
    )

    theme_score_table = diagnostic_table(
        temp,
        "테마점수구간",
        20
    )

    if not theme_score_table.empty:

        st.dataframe(
            theme_score_table.style.format({
                "승률": "{:.1f}%",
                "평균수익률": "{:+.2f}%",
                "중앙값": "{:+.2f}%",
                "최고": "{:+.2f}%",
                "최저": "{:+.2f}%",
                "수익률합": "{:+.2f}%",
            }),
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # ⑥-3 ETF
    # --------------------------------------------------------

    st.subheader(
        "⑥-3 ETF별 성과"
    )

    etf_table = diagnostic_table(
        r,
        "ETF",
        20
    )

    if not etf_table.empty:

        st.dataframe(
            etf_table.style.format({
                "승률": "{:.1f}%",
                "평균수익률": "{:+.2f}%",
                "중앙값": "{:+.2f}%",
                "최고": "{:+.2f}%",
                "최저": "{:+.2f}%",
                "수익률합": "{:+.2f}%",
            }),
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # ⑥-4 테마
    # --------------------------------------------------------

    st.subheader(
        "⑥-4 테마별 성과"
    )

    if not theme_table.empty:

        st.dataframe(
            theme_table.style.format({
                "승률": "{:.1f}%",
                "평균수익률": "{:+.2f}%",
                "중앙값": "{:+.2f}%",
                "최고": "{:+.2f}%",
                "최저": "{:+.2f}%",
                "수익률합": "{:+.2f}%",
            }),
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # ⑥-5
    # --------------------------------------------------------

    st.subheader(
        "⑥-5 가격상태별 성과"
    )

    price_table = diagnostic_table(
        r,
        "가격상태",
        20
    )

    if not price_table.empty:

        st.dataframe(
            price_table.style.format({
                "승률": "{:.1f}%",
                "평균수익률": "{:+.2f}%",
                "중앙값": "{:+.2f}%",
                "최고": "{:+.2f}%",
                "최저": "{:+.2f}%",
                "수익률합": "{:+.2f}%",
            }),
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # ⑥-6
    # --------------------------------------------------------

    st.subheader(
        "⑥-6 점수와 실제 수익률의 관계"
    )

    st.caption(
        "상관계수는 +1에 가까울수록 점수가 높을 때 수익률도 "
        "높아지는 경향, -1에 가까울수록 반대 경향을 의미합니다."
    )

    corr_rows = []

    for score_col, name in [
        ("선행점수", "선행점수"),
        ("테마점수", "테마점수"),
        ("과열점수", "과열점수"),
    ]:

        corr_rows.append({
            "점수": name,
            "5일": score_correlation(
                r,
                score_col,
                "5일수익률"
            ),
            "20일": score_correlation(
                r,
                score_col,
                "20일수익률"
            ),
            "60일": score_correlation(
                r,
                score_col,
                "60일수익률"
            ),
        })

    corr_table = pd.DataFrame(
        corr_rows
    )

    st.dataframe(
        corr_table.style.format({
            "5일": "{:+.2f}",
            "20일": "{:+.2f}",
            "60일": "{:+.2f}",
        }),
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # ⑥-7
    # --------------------------------------------------------

    st.subheader(
        "⑥-7 현재 데이터의 자동 진단"
    )

    messages = build_diagnostic_messages(
        r
    )

    for msg in messages:
        st.write(msg)

    st.warning(
        "전략 진단은 현재 백테스트 데이터를 설명하기 위한 기능입니다. "
        "이 결과만으로 특정 ETF의 미래 수익을 보장하지 않습니다. "
        "거래 수가 적은 경우 반드시 별도의 기간 검증이 필요합니다."
    )

    # ========================================================
    # ⑦ NEW: LOSS CONTROL
    # ========================================================

    st.divider()

    st.header(
        "⑦ 🛡️ 손실관리 테스트"
    )

    st.caption(
        "기존 C/D 진입전략은 그대로 두고, "
        "손절선만 변경했을 때 실제 결과가 어떻게 달라지는지 비교합니다."
    )

    loss_strategy = st.selectbox(
        "손실관리 대상 전략",
        [
            "C · 미래테마 + 선행",
            "D · 미래테마 + 선행 + 가격",
        ],
        key="loss_strategy_select"
    )

    loss_col = (
        "C"
        if loss_strategy.startswith("C")
        else "D"
    )

    loss_horizon = st.selectbox(
        "손실관리 평가기간",
        [20, 60],
        index=0,
        key="loss_horizon_select"
    )

    loss_table = loss_control_table(
        r,
        loss_col,
        loss_horizon
    )

    if not loss_table.empty:

        st.dataframe(
            loss_table.style.format({
                "승률": "{:.1f}%",
                "평균수익률": "{:+.2f}%",
                "중앙값": "{:+.2f}%",
                "최고": "{:+.2f}%",
                "최저": "{:+.2f}%",
                "평균낙폭": "{:.2f}%",
                "손절발생률": "{:.1f}%",
                "누적단순수익률": "{:+.2f}%",
            }),
            use_container_width=True,
            hide_index=True
        )

        best_idx = loss_table[
            "평균수익률"
        ].idxmax()

        best_row = loss_table.loc[
            best_idx
        ]

        st.info(
            f"현재 데이터에서 {loss_strategy} / "
            f"{loss_horizon}일 기준 평균수익률이 가장 높은 "
            f"손실관리 조건은 "
            f"'{best_row['손절']}'입니다. "
            f"단, 이것만으로 최적 손절선을 확정하면 안 됩니다."
        )

    # ========================================================
    # ⑧ NEW: SCORE COMPONENT TEST
    # ========================================================

    st.header(
        "⑧ 🧬 선행점수 구성요소 검증"
    )

    st.caption(
        "현재 선행점수를 구성하는 각 요소가 실제 5/20/60일 수익률과 "
        "어떤 관계가 있는지 확인합니다."
    )

    component_table = component_correlation_table(
        r
    )

    st.dataframe(
        component_table.style.format({
            "5일": "{:+.3f}",
            "20일": "{:+.3f}",
            "60일": "{:+.3f}",
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        """
**해석 방법**

- `+0.30 이상` : 비교적 의미 있는 양의 관계 후보
- `+0.10 ~ +0.30` : 약한 양의 관계
- `-0.10 ~ +0.10` : 사실상 관계가 약함
- `-0.10 이하` : 역관계 후보

단, 이것은 **인과관계가 아니라 상관관계**입니다.
따라서 이 결과만 보고 즉시 가중치를 변경하지 않습니다.
"""
    )

    # ========================================================
    # ⑨ 1M SIMULATION
    # ========================================================

    st.divider()

    st.header(
        "⑨ 💰 100만원 가상투자 시뮬레이션"
    )

    sc1, sc2, sc3 = st.columns(3)

    with sc1:

        sim_strategy = st.selectbox(
            "전략",
            ["C", "D"],
            index=1,
            key="sim_strategy"
        )

    with sc2:

        hold_days = st.selectbox(
            "보유기간",
            [5, 20, 60],
            index=1,
            key="sim_hold"
        )

    with sc3:

        initial_money = st.number_input(
            "초기금액",
            min_value=100_000,
            max_value=100_000_000,
            value=1_000_000,
            step=100_000,
            key="sim_initial_money"
        )

    sim_button = st.button(
        "💰 시뮬레이션 실행",
        use_container_width=True
    )

    if sim_button:

        curve, metrics = simulate_equity_curve(
            r,
            strategy_col=sim_strategy,
            hold_days=hold_days,
            initial_capital=initial_money,
            fee_pct=0.05,
            slippage_pct=0.05
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

    if (
        sim_curve is not None
        and not sim_curve.empty
        and sim_metrics
    ):

        a, b, c, d = st.columns(4)

        a.metric(
            "최종자산",
            f"{sim_metrics['최종자산']:,.0f}원"
        )

        b.metric(
            "총수익률",
            f"{sim_metrics['총수익률']:+.2f}%"
        )

        c.metric(
            "승률",
            f"{sim_metrics['승률']:.1f}%"
        )

        d.metric(
            "최대낙폭",
            f"{sim_metrics['최대낙폭']:.2f}%"
        )

        chart_df = sim_curve.set_index(
            "날짜"
        )

        st.line_chart(
            chart_df["자산"]
        )

    # ========================================================
    # ⑩ RAW DATA
    # ========================================================

    st.divider()

    st.header(
        "⑩ 원본 백테스트 데이터"
    )

    st.dataframe(
        r,
        use_container_width=True,
        hide_index=True
    )

    csv = r.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        "📥 전략 백테스트 CSV 저장",
        data=csv,
        file_name="ETF_RADAR_STRATEGY_BACKTEST.csv",
        mime="text/csv",
        use_container_width=True
    )

    # ========================================================
    # FINAL
    # ========================================================

    st.divider()

    st.success(
        "백테스트 완료. "
        "이제 ⑦ 손실관리 테스트와 ⑧ 선행점수 구성요소 검증 결과를 "
        "확인하면 다음 전략 수정 여부를 판단할 수 있습니다."
    )

else:

    st.info(
        "시작일·종료일·ETF를 선택한 후 "
        "'전체 백테스트 실행'을 눌러주세요."
    )