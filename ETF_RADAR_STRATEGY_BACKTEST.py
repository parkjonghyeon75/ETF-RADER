# -*- coding: utf-8 -*-
"""
ETF RADAR STRATEGY BACKTEST

목적
- 현재 ETF RADAR의 핵심 아이디어를 과거 시점으로 되돌려 검증한다.
- A: 단순 보유
- B: 선행점수
- C: 미래테마 + 선행 ETF
- D: 미래테마 + 선행 ETF + 가격구간

주의
- 이 앱은 연구용 백테스트입니다.
- 실제 주문 체결, 세금, 배당, 환전비용 등은 완전히 반영하지 않습니다.
- 신호일 종가가 아니라 다음 거래일 종가 진입으로 계산하여 look-ahead를 줄입니다.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date

st.set_page_config(
    page_title="ETF RADAR STRATEGY TEST",
    page_icon="🧪",
    layout="wide"
)


# ============================================================
# 0. SESSION STATE
# ============================================================

def init_session_state():
    """Streamlit 재실행에도 백테스트 결과를 유지한다."""

    defaults = {
        "strategy_result": None,
        "strategy_data": None,
        "sim_curve": None,
        "sim_metrics": None,
        "sim_hold": 20,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ============================================================
# 1. 테스트 유니버스
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


# 실제 테마 계산을 위해 2개 이상 ETF가 있는 테마를 중심으로 사용
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
# 2. 데이터
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def download_prices(tickers, start, end):

    symbols = list(dict.fromkeys(list(tickers) + [BENCH]))

    x = yf.download(
        symbols,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        threads=True,
        group_by="ticker",
    )

    out = {}

    for t in symbols:
        try:
            if len(symbols) == 1:
                d = x.copy()
            else:
                d = x[t].copy()

            if not d.empty:
                d.columns = [str(c) for c in d.columns]
                out[t] = d

        except Exception:
            continue

    return out


def indicators(d):

    d = d.copy()

    if "Close" not in d.columns:
        return pd.DataFrame()

    d["Close"] = pd.to_numeric(
        d["Close"],
        errors="coerce"
    )

    d["Volume"] = pd.to_numeric(
        d.get("Volume", np.nan),
        errors="coerce"
    )

    d = d.dropna(
        subset=["Close"]
    )

    d["MA20"] = d["Close"].rolling(20).mean()
    d["MA60"] = d["Close"].rolling(60).mean()

    d["R5"] = d["Close"].pct_change(5) * 100
    d["R20"] = d["Close"].pct_change(20) * 100
    d["R60"] = d["Close"].pct_change(60) * 100

    d["VR"] = (
        d["Volume"]
        / d["Volume"].rolling(20).mean()
    )

    delta = d["Close"].diff()

    gain = (
        delta.clip(lower=0)
        .rolling(14)
        .mean()
    )

    loss = (
        (-delta.clip(upper=0))
        .rolling(14)
        .mean()
    )

    rs = gain / loss.replace(0, np.nan)

    d["RSI"] = 100 - 100 / (1 + rs)

    d["VOL20"] = d["Volume"].rolling(20).mean()

    d["LOW20"] = (
        d["Close"]
        .rolling(20)
        .min()
    )

    d["HIGH20"] = (
        d["Close"]
        .rolling(20)
        .max()
    )

    return d


# ============================================================
# 3. 기존 ETF RADAR 선행신호와 동일한 핵심 구조
# ============================================================

def leading_signal(row, benchmark_ret20=0):

    current = float(
        row.get("Close", 0) or 0
    )

    ma20 = float(
        row.get("MA20", current) or current
    )

    ma60 = float(
        row.get("MA60", current) or current
    )

    ret5 = float(
        row.get("R5", 0) or 0
    )

    ret20 = float(
        row.get("R20", 0) or 0
    )

    vr = float(
        row.get("VR", 1) or 1
    )

    rsi = float(
        row.get("RSI", 50) or 50
    )

    dist20 = (
        (current / ma20 - 1) * 100
        if ma20
        else 0
    )

    rs20 = ret20 - benchmark_ret20

    accel = ret5 - ret20 / 4

    early_price = (
        92 if -1 <= dist20 <= 3
        else 82 if dist20 <= 5
        else 65 if dist20 < 8
        else 35
    )

    early_rsi = (
        92 if 48 <= rsi <= 62
        else 84 if 43 <= rsi < 68
        else 68 if rsi < 72
        else 35
    )

    flow = (
        92 if 1.10 <= vr <= 1.70
        else 82 if 1.0 <= vr < 1.10
        else 76 if 0.9 <= vr < 1.0
        else 58 if vr < 2.2
        else 38
    )

    accel_score = (
        90 if 0.5 <= accel <= 5
        else 78 if 0 <= accel < 0.5
        else 68 if accel > 5
        else 52
    )

    rel = (
        88 if rs20 >= 6
        else 80 if rs20 >= 3
        else 70 if rs20 >= 0
        else 48
    )

    structure = (
        90 if current >= ma60 and ma20 >= ma60
        else 78 if current >= ma60
        else 55 if current >= ma20
        else 35
    )

    score = round(
        early_price * 0.22
        + early_rsi * 0.18
        + flow * 0.22
        + accel_score * 0.16
        + rel * 0.14
        + structure * 0.08
    )

    early_buy = (
        score >= 72
        and vr >= 1.05
        and rsi < 70
        and dist20 < 7
        and rs20 >= -1
    )

    return {
        "score": int(
            max(
                0,
                min(100, score)
            )
        ),
        "early_buy": bool(early_buy),
        "rs20": rs20,
        "dist20": dist20,
        "rsi": rsi,
        "vr": vr,
        "accel": accel,
    }


# ============================================================
# 4. 테마 점수
# ============================================================

def theme_score(
    theme_rows,
    bench_ret20=0,
    bench_ret60=0
):

    if len(theme_rows) < 2:
        return None

    vals = []

    for r in theme_rows:

        if (
            pd.isna(r.get("R20"))
            or pd.isna(r.get("R60"))
        ):
            continue

        sig = leading_signal(
            r,
            bench_ret20
        )

        vals.append({
            "r20": float(r["R20"]),
            "r60": float(r["R60"]),
            "rs20": sig["rs20"],
            "rs60": (
                float(r["R60"])
                - bench_ret60
            ),
            "vr": float(
                r.get("VR", 1)
                if pd.notna(r.get("VR", 1))
                else 1
            ),
            "ma60gap": (
                (
                    float(r["Close"])
                    / float(r["MA60"])
                    - 1
                ) * 100
                if pd.notna(r.get("MA60"))
                and r["MA60"]
                else 0
            ),
            "accel": sig["accel"],
            "rsi": sig["rsi"],
            "lead": sig["score"],
            "early": sig["early_buy"],
        })

    if len(vals) < 2:
        return None

    x = pd.DataFrame(vals)

    def clip_score(v, lo, hi):

        return float(
            np.clip(
                (v - lo)
                / (hi - lo)
                * 100,
                0,
                100
            )
        )

    r20 = clip_score(
        x["r20"].mean(),
        -10,
        15
    )

    r60 = clip_score(
        x["r60"].mean(),
        -15,
        30
    )

    rs20 = clip_score(
        x["rs20"].mean(),
        -10,
        12
    )

    rs60 = clip_score(
        x["rs60"].mean(),
        -15,
        20
    )

    vr = clip_score(
        x["vr"].mean(),
        0.8,
        2.0
    )

    breadth = float(
        (x["r20"] > -2).mean()
        * 100
    )

    ma60 = clip_score(
        x["ma60gap"].mean(),
        -10,
        15
    )

    accel = clip_score(
        x["accel"].mean(),
        -5,
        6
    )

    rsi = (
        100
        - abs(
            float(x["rsi"].mean())
            - 58
        ) * 2.5
    )

    rsi = float(
        np.clip(
            rsi,
            0,
            100
        )
    )

    score = (
        r20 * 0.15
        + r60 * 0.15
        + rs20 * 0.15
        + rs60 * 0.10
        + vr * 0.15
        + breadth * 0.15
        + ma60 * 0.05
        + accel * 0.05
        + rsi * 0.05
    )

    early_count = int(
        x["early"].sum()
    )

    early_ratio = (
        early_count / len(x)
    )

    lead_avg = float(
        x["lead"].mean()
    )

    # 기존 앱의 선행 테마 개념을 반영
    lead_theme = (
        lead_avg * 0.55
        + breadth * 0.25
        + early_ratio * 100 * 0.20
    )

    final = (
        score * 0.70
        + lead_theme * 0.30
    )

    # 과열 패널티
    heat = 0

    if float(x["rsi"].mean()) >= 75:
        heat += 12

    if float(x["r20"].mean()) >= 12:
        heat += 10

    if float(x["ma60gap"].mean()) >= 15:
        heat += 8

    final = float(
        np.clip(
            final - heat,
            0,
            100
        )
    )

    if final >= 78:
        stage = "현재 주도"
    elif final >= 64:
        stage = "다음 수혜"
    elif final >= 50:
        stage = "관심 확대"
    else:
        stage = "초기 관심"

    return {
        "score": final,
        "stage": stage,
        "breadth": breadth,
        "lead_avg": lead_avg,
        "early_count": early_count,
        "members": len(x),
        "heat": heat,
    }


# ============================================================
# 5. 날짜별 테마 선정
# ============================================================

def build_snapshot(
    all_data,
    date_i
):

    bench = all_data.get(BENCH)

    if bench is None or bench.empty:
        return None

    b = bench.iloc[
        : date_i + 1
    ]

    if len(b) < 65:
        return None

    br = b.iloc[-1]

    bench_ret20 = float(
        br.get("R20", np.nan)
    )

    bench_ret60 = float(
        br.get("R60", np.nan)
    )

    if (
        not np.isfinite(bench_ret20)
        or not np.isfinite(bench_ret60)
    ):
        return None

    theme_results = []

    for theme, members in THEME_GROUPS.items():

        rows = []

        for t in members:

            d = all_data.get(t)

            if (
                d is None
                or d.empty
                or len(d) <= date_i
            ):
                continue

            r = d.iloc[date_i]

            if (
                pd.isna(r.get("MA60"))
                or pd.isna(r.get("R20"))
                or pd.isna(r.get("R60"))
            ):
                continue

            rr = r.to_dict()
            rr["ETF"] = t
            rows.append(rr)

        ts = theme_score(
            rows,
            bench_ret20,
            bench_ret60
        )

        if ts:

            ts["theme"] = theme
            ts["rows"] = rows

            theme_results.append(ts)

    if not theme_results:
        return None

    theme_results.sort(
        key=lambda z: z["score"],
        reverse=True
    )

    top = theme_results[0]

    candidates = []

    for r in top["rows"]:

        sig = leading_signal(
            r,
            bench_ret20
        )

        heat = 0

        c = float(r["Close"])
        ma20 = float(r["MA20"])
        rsi = sig["rsi"]
        dist20 = sig["dist20"]

        if rsi >= 78:
            heat += 32
        elif rsi >= 72:
            heat += 24
        elif rsi >= 68:
            heat += 12

        if float(r["R5"]) >= 10:
            heat += 25
        elif float(r["R5"]) >= 7:
            heat += 18
        elif float(r["R5"]) >= 5:
            heat += 10

        if dist20 >= 12:
            heat += 23
        elif dist20 >= 8:
            heat += 16
        elif dist20 >= 5:
            heat += 8

        if sig["vr"] >= 2:
            heat += 15
        elif sig["vr"] >= 1.5:
            heat += 10
        elif sig["vr"] >= 1.2:
            heat += 5

        candidates.append({
            "ETF": r["ETF"],
            "sig": sig,
            "heat": min(100, heat),
            "close": c,
            "ma20": ma20,
        })

    if not candidates:
        return None

    # 선행점수 - 과열패널티
    candidates.sort(
        key=lambda z:
            z["sig"]["score"]
            - z["heat"] * 0.35,
        reverse=True
    )

    winner = candidates[0]

    return {
        "theme": top["theme"],
        "theme_score": top["score"],
        "theme_stage": top["stage"],
        "winner": winner,
        "themes": theme_results,
    }


# ============================================================
# 6. 가격구간
# ============================================================

def price_zone(r):

    c = float(r["Close"])
    ma20 = float(r["MA20"])
    ma60 = float(r["MA60"])
    low20 = float(r["LOW20"])

    support = max(
        low20,
        ma20 * 0.985
    )

    ideal_top = ma20 * 1.025

    invalid = min(
        ma60 * 0.97,
        support * 0.97
    )

    if (
        c <= ideal_top
        and c >= invalid
        and c >= ma60 * 0.98
    ):
        state = "매수구간"

    elif c < invalid:
        state = "무효"

    elif c > ma20 * 1.07:
        state = "추격금지"

    else:
        state = "눌림대기"

    return {
        "state": state,
        "support": support,
        "ideal_top": ideal_top,
        "invalid": invalid,
    }


# ============================================================
# 7. 전체 전략 백테스트
# ============================================================

def run_strategy_backtest(
    start,
    end,
    tickers,
    step_days=5
):

    download_start = (
        pd.Timestamp(start)
        - pd.Timedelta(days=140)
    ).strftime("%Y-%m-%d")

    download_end = (
        pd.Timestamp(end)
        + pd.Timedelta(days=80)
    ).strftime("%Y-%m-%d")

    raw = download_prices(
        tickers,
        download_start,
        download_end
    )

    data = {
        k: indicators(v)
        for k, v in raw.items()
    }

    data = {
        k: v
        for k, v in data.items()
        if not v.empty
    }

    if BENCH not in data:
        raise RuntimeError(
            "SPY 벤치마크 데이터를 가져오지 못했습니다."
        )

    common = data[BENCH].index

    for t in tickers:

        if t in data:
            common = common.intersection(
                data[t].index
            )

    common = common.sort_values()

    common = common[
        (common >= pd.Timestamp(start))
        & (common <= pd.Timestamp(end))
    ]

    rows = []

    # 5거래일 간격
    for pos in range(
        0,
        len(common) - 61,
        max(1, step_days)
    ):

        dt = common[pos]

        hist_pos = (
            data[BENCH]
            .index
            .get_loc(dt)
        )

        snap = build_snapshot(
            data,
            hist_pos
        )

        if snap is None:
            continue

        winner = snap["winner"]

        t = winner["ETF"]

        d = data[t]

        if hist_pos + 60 >= len(d):
            continue

        # 다음 거래일 진입
        entry_i = hist_pos + 1

        entry = d.iloc[entry_i]

        entry_price = float(
            entry["Close"]
        )

        if (
            not np.isfinite(entry_price)
            or entry_price <= 0
        ):
            continue

        sig = winner["sig"]

        zone = price_zone(
            d.iloc[hist_pos]
        )

        # 전략 A
        a_ok = True

        # 전략 B
        b_ok = (
            sig["score"] >= 72
            and sig["early_buy"]
        )

        # 전략 C
        c_ok = (
            snap["theme_score"] >= 60
            and b_ok
        )

        # 전략 D
        d_ok = (
            c_ok
            and zone["state"] == "매수구간"
        )

        future = d.iloc[
            entry_i:
            entry_i + 60
        ]

        if len(future) < 60:
            continue

        rec = {
            "날짜": dt.date(),
            "테마": snap["theme"],
            "테마점수": round(
                snap["theme_score"],
                1
            ),
            "테마단계": snap["theme_stage"],
            "ETF": t,
            "선행점수": sig["score"],
            "과열점수": winner["heat"],
            "가격상태": zone["state"],
            "매수가": entry_price,
            "A_단순테마": a_ok,
            "B_선행점수": b_ok,
            "C_미래테마선행": c_ok,
            "D_미래테마선행가격": d_ok,
        }

        for n in [5, 20, 60]:

            ret = (
                float(
                    future.iloc[n - 1]["Close"]
                )
                / entry_price
                - 1
            ) * 100

            dd = (
                float(
                    future.iloc[:n]["Close"].min()
                )
                / entry_price
                - 1
            ) * 100

            rec[f"{n}일수익"] = ret
            rec[f"{n}일최저낙폭"] = dd

        rows.append(rec)

    return pd.DataFrame(rows), data


# ============================================================
# 8. 성과 계산
# ============================================================

def strategy_summary(
    r,
    flag,
    horizon
):

    x = r.loc[
        r[flag],
        f"{horizon}일수익"
    ].dropna()

    dd = r.loc[
        r[flag],
        f"{horizon}일최저낙폭"
    ].dropna()

    if x.empty:

        return {
            "신호수": 0,
            "승률": np.nan,
            "평균수익": np.nan,
            "중앙값": np.nan,
            "평균낙폭": np.nan,
            "최고": np.nan,
            "최대손실": np.nan,
        }

    return {
        "신호수": len(x),
        "승률": (
            x > 0
        ).mean() * 100,
        "평균수익": x.mean(),
        "중앙값": x.median(),
        "평균낙폭": (
            dd.mean()
            if not dd.empty
            else np.nan
        ),
        "최고": x.max(),
        "최대손실": x.min(),
    }


# ============================================================
# 9. D 전략 자산곡선 시뮬레이션
# ============================================================

def simulate_equity_curve(
    r,
    data,
    initial_cash=1_000_000,
    hold_days=20,
    fee_per_side=0.0010,
    slippage_per_side=0.0005
):
    """
    D 전략을 실제 포트폴리오처럼
    1회 1포지션으로 순차 시뮬레이션.

    - 신호일 이후 다음 거래일 종가 진입
    - D 조건만 사용
    - 보유 중 새 신호는 무시
    - 기본은 hold_days 후 청산
    - 수수료+슬리피지를 매수/매도 각각 반영
    """

    if r is None or r.empty:
        return pd.DataFrame(), {}

    if data is None or not isinstance(data, dict):
        return pd.DataFrame(), {}

    rr = r.loc[
        r["D_미래테마선행가격"] == True
    ].copy()

    if rr.empty:
        return pd.DataFrame(), {
            "초기자산": initial_cash,
            "최종자산": initial_cash,
            "총수익률": 0.0,
            "승률": np.nan,
            "거래수": 0,
            "최대낙폭": 0.0,
            "연환산": np.nan,
            "평균거래수익": np.nan,
            "trades": pd.DataFrame(),
        }

    rr["날짜"] = pd.to_datetime(
        rr["날짜"]
    )

    rr = (
        rr
        .sort_values("날짜")
        .reset_index(drop=True)
    )

    cash = float(initial_cash)

    equity_rows = []
    trades = []

    next_available = pd.Timestamp.min

    wins = 0

    for _, sig in rr.iterrows():

        signal_date = pd.Timestamp(
            sig["날짜"]
        )

        if signal_date < next_available:
            continue

        ticker = sig["ETF"]

        d = data.get(ticker)

        if d is None or d.empty:
            continue

        idx = d.index.searchsorted(
            signal_date
        )

        entry_i = idx + 1

        exit_i = (
            entry_i
            + int(hold_days)
            - 1
        )

        if (
            entry_i >= len(d)
            or exit_i >= len(d)
        ):
            continue

        entry_date = d.index[entry_i]
        exit_date = d.index[exit_i]

        entry_raw = float(
            d.iloc[entry_i]["Close"]
        )

        exit_raw = float(
            d.iloc[exit_i]["Close"]
        )

        if (
            not np.isfinite(entry_raw)
            or not np.isfinite(exit_raw)
            or entry_raw <= 0
        ):
            continue

        # 매수/매도 슬리피지
        buy_price = (
            entry_raw
            * (1 + slippage_per_side)
        )

        sell_price = (
            exit_raw
            * (1 - slippage_per_side)
        )

        gross_ret = (
            sell_price
            / buy_price
            - 1
        )

        net_ret = (
            gross_ret
            - fee_per_side * 2
        )

        cash = cash * (
            1 + net_ret
        )

        wins += int(
            net_ret > 0
        )

        next_available = (
            exit_date
            + pd.Timedelta(days=1)
        )

        trades.append({
            "신호일": signal_date.date(),
            "진입일": entry_date.date(),
            "청산일": exit_date.date(),
            "테마": sig["테마"],
            "ETF": ticker,
            "테마점수": sig["테마점수"],
            "선행점수": sig["선행점수"],
            "가격상태": sig["가격상태"],
            "진입가격": entry_raw,
            "청산가격": exit_raw,
            "순수익률": net_ret * 100,
            "거래후자산": cash,
        })

        equity_rows.append({
            "날짜": exit_date,
            "자산": cash,
        })

    trades_df = pd.DataFrame(
        trades
    )

    curve = pd.DataFrame(
        equity_rows
    )

    if curve.empty:

        return curve, {
            "초기자산": initial_cash,
            "최종자산": initial_cash,
            "총수익률": 0.0,
            "승률": np.nan,
            "거래수": 0,
            "최대낙폭": 0.0,
            "연환산": np.nan,
            "평균거래수익": np.nan,
            "trades": trades_df,
        }

    curve = (
        curve
        .sort_values("날짜")
        .drop_duplicates(
            "날짜",
            keep="last"
        )
    )

    curve["고점"] = (
        curve["자산"]
        .cummax()
    )

    curve["낙폭"] = (
        curve["자산"]
        / curve["고점"]
        - 1
    ) * 100

    final_cash = float(
        curve.iloc[-1]["자산"]
    )

    total_ret = (
        final_cash
        / initial_cash
        - 1
    ) * 100

    days = max(
        1,
        (
            pd.Timestamp(
                curve.iloc[-1]["날짜"]
            )
            - pd.Timestamp(
                curve.iloc[0]["날짜"]
            )
        ).days,
    )

    annualized = (
        (
            final_cash
            / initial_cash
        )
        ** (365.25 / days)
        - 1
    ) * 100 if final_cash > 0 else -100

    metrics = {
        "초기자산": initial_cash,
        "최종자산": final_cash,
        "총수익률": total_ret,
        "승률": (
            wins
            / len(trades_df)
            * 100
            if len(trades_df)
            else np.nan
        ),
        "거래수": len(trades_df),
        "최대낙폭": float(
            curve["낙폭"].min()
        ),
        "연환산": annualized,
        "평균거래수익": (
            float(
                trades_df[
                    "순수익률"
                ].mean()
            )
            if not trades_df.empty
            else np.nan
        ),
    }

    return curve, {
        **metrics,
        "trades": trades_df,
    }


def simulate_buy_hold(
    ticker,
    data,
    initial_cash=1_000_000
):

    d = data.get(ticker)

    if d is None or d.empty:
        return pd.DataFrame(), {}

    x = d.dropna(
        subset=["Close"]
    ).copy()

    if len(x) < 2:
        return pd.DataFrame(), {}

    p0 = float(
        x.iloc[0]["Close"]
    )

    curve = pd.DataFrame({
        "날짜": x.index,
        "자산": (
            initial_cash
            * x["Close"]
            / p0
        ),
    })

    curve["고점"] = (
        curve["자산"]
        .cummax()
    )

    curve["낙폭"] = (
        curve["자산"]
        / curve["고점"]
        - 1
    ) * 100

    final_cash = float(
        curve.iloc[-1]["자산"]
    )

    days = max(
        1,
        (
            x.index[-1]
            - x.index[0]
        ).days,
    )

    annualized = (
        (
            final_cash
            / initial_cash
        )
        ** (365.25 / days)
        - 1
    ) * 100

    return curve, {
        "초기자산": initial_cash,
        "최종자산": final_cash,
        "총수익률": (
            final_cash
            / initial_cash
            - 1
        ) * 100,
        "최대낙폭": float(
            curve["낙폭"].min()
        ),
        "연환산": annualized,
    }


# ============================================================
# 10. UI
# ============================================================

st.title(
    "🧪 ETF RADAR STRATEGY TEST"
)

st.caption(
    "미래테마 → 선행 ETF → 과열 필터 → "
    "가격구간까지 실제 투자 흐름을 "
    "과거 데이터로 검증합니다."
)

st.info(
    "이번 테스트의 목적은 기능을 더 만드는 것이 아니라, "
    "현재 ETF RADAR의 핵심 로직에 실제 투자 우위가 있는지 확인하는 것입니다. "
    "데이터 다운로드와 계산은 Streamlit 캐시를 사용해 반복 실행을 줄입니다."
)


c1, c2 = st.columns(2)

start = c1.date_input(
    "시작일",
    date(2021, 1, 1),
    key="st_start"
)

end = c2.date_input(
    "종료일",
    date(2025, 12, 31),
    key="st_end"
)


selected = st.multiselect(
    "테스트 ETF",
    list(POOL.keys()),
    [
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
        f"{x} · {POOL[x]}",
)


step = st.select_slider(
    "검사 간격",
    options=[1, 3, 5, 10],
    value=5,
    format_func=lambda x:
        "매일"
        if x == 1
        else f"{x}거래일마다",
)


st.markdown("---")


run_clicked = st.button(
    "🧪 전체 투자로직 백테스트 실행",
    type="primary",
    use_container_width=True,
)


# ============================================================
# 11. 백테스트 실행
# ============================================================

if run_clicked:

    if start >= end:

        st.error(
            "시작일은 종료일보다 빨라야 합니다."
        )

        st.stop()

    if len(selected) < 4:

        st.error(
            "테마 비교를 위해 ETF를 4개 이상 선택하십시오."
        )

        st.stop()

    with st.status(
        "전체 투자로직을 과거 날짜별로 검증하는 중...",
        expanded=True,
    ) as status:

        st.write(
            "① 과거 가격 데이터 다운로드"
        )

        st.write(
            "② ETF별 기술지표 계산"
        )

        st.write(
            "③ 날짜별 미래테마 계산"
        )

        st.write(
            "④ 테마 대표 ETF + 선행신호 + 가격구간 판정"
        )

        st.write(
            "⑤ 다음 거래일 진입 후 5·20·60일 성과 계산"
        )

        try:

            result, data = (
                run_strategy_backtest(
                    start,
                    end,
                    selected,
                    step
                )
            )

            # ==================================================
            # 중요 수정 ①
            # 백테스트 결과와 data를 모두 session_state에 저장
            # ==================================================

            st.session_state[
                "strategy_result"
            ] = result

            st.session_state[
                "strategy_data"
            ] = data

            # 기존 시뮬레이션 결과는 새 백테스트 후 초기화
            st.session_state[
                "sim_curve"
            ] = None

            st.session_state[
                "sim_metrics"
            ] = None

            status.update(
                label="백테스트 완료",
                state="complete",
                expanded=False,
            )

        except Exception as ex:

            status.update(
                label="백테스트 실패",
                state="error",
                expanded=True,
            )

            st.exception(ex)
            st.stop()


# ============================================================
# 12. 저장된 백테스트 결과 복원
# ============================================================

# ============================================================
# 중요 수정 ②
# Streamlit 재실행 시에도 result와 data를 복원
# ============================================================

r = st.session_state.get(
    "strategy_result"
)

data = st.session_state.get(
    "strategy_data"
)


# ============================================================
# 13. 백테스트 전 화면
# ============================================================

if r is None:

    st.markdown(
        "### 테스트 방법"
    )

    st.markdown(
        """
        **A. 단순 테마** → 테마 대표 ETF를 선택

        **B. 선행점수** → 선행점수 조건을 추가

        **C. 미래테마 + 선행** → 미래테마가 강한 구간에서만 선행 ETF 선택

        **D. 미래테마 + 선행 + 가격** → C에 현재 가격구간까지 추가

        최종적으로 **D가 A/B/C보다 지속적으로 우수한지** 확인합니다.
        """
    )


# ============================================================
# 14. 백테스트 결과 화면
# ============================================================

else:

    if r.empty:

        st.error(
            "조건을 만족하는 테스트 결과가 없습니다."
        )

        st.stop()


    st.success(
        f"검증 완료 · {len(r):,}개 검사 시점"
    )


    flags = {
        "A 단순테마": "A_단순테마",
        "B 선행점수": "B_선행점수",
        "C 미래테마+선행": "C_미래테마선행",
        "D 미래테마+선행+가격": "D_미래테마선행가격",
    }


    # ========================================================
    # ① 핵심 결과
    # ========================================================

    st.subheader(
        "① 한눈에 보는 핵심 결과"
    )

    for horizon in [20, 60]:

        st.markdown(
            f"#### {horizon}일 성과"
        )

        cols = st.columns(4)

        for col, (
            name,
            flag
        ) in zip(
            cols,
            flags.items()
        ):

            q = strategy_summary(
                r,
                flag,
                horizon
            )

            if q["신호수"] == 0:

                col.metric(
                    name,
                    "신호 없음"
                )

            else:

                col.metric(
                    name,
                    f"{q['평균수익']:+.2f}%",
                    f"승률 {q['승률']:.1f}%"
                )


    # ========================================================
    # ② 전략 비교표
    # ========================================================

    st.subheader(
        "② 전략 비교표"
    )

    rows = []

    for name, flag in flags.items():

        for h in [5, 20, 60]:

            q = strategy_summary(
                r,
                flag,
                h
            )

            rows.append({
                "전략": name,
                "기간": f"{h}일",
                "신호수": q["신호수"],
                "승률": q["승률"],
                "평균수익": q["평균수익"],
                "중앙값": q["중앙값"],
                "평균최저낙폭": q["평균낙폭"],
                "최고수익": q["최고"],
                "최대손실": q["최대손실"],
            })


    summary = pd.DataFrame(rows)


    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "승률":
                st.column_config.NumberColumn(
                    format="%.1f%%"
                ),
            "평균수익":
                st.column_config.NumberColumn(
                    format="%+.2f%%"
                ),
            "중앙값":
                st.column_config.NumberColumn(
                    format="%+.2f%%"
                ),
            "평균최저낙폭":
                st.column_config.NumberColumn(
                    format="%.2f%%"
                ),
            "최고수익":
                st.column_config.NumberColumn(
                    format="%+.2f%%"
                ),
            "최대손실":
                st.column_config.NumberColumn(
                    format="%+.2f%%"
                ),
        },
    )


    # ========================================================
    # ③ 연도별 검증
    # ========================================================

    st.subheader(
        "③ 연도별 검증"
    )

    r2 = r.copy()

    r2["연도"] = (
        pd.to_datetime(
            r2["날짜"]
        ).dt.year
    )

    year_rows = []

    for year, g in r2.groupby("연도"):

        for name, flag in flags.items():

            q = strategy_summary(
                g,
                flag,
                20
            )

            year_rows.append({
                "연도": int(year),
                "전략": name,
                "신호수": q["신호수"],
                "20일 승률": q["승률"],
                "20일 평균": q["평균수익"],
                "20일 평균낙폭": q["평균낙폭"],
            })


    st.dataframe(
        pd.DataFrame(year_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "20일 승률":
                st.column_config.NumberColumn(
                    format="%.1f%%"
                ),
            "20일 평균":
                st.column_config.NumberColumn(
                    format="%+.2f%%"
                ),
            "20일 평균낙폭":
                st.column_config.NumberColumn(
                    format="%.2f%%"
                ),
        },
    )


    # ========================================================
    # ④ 테마별 검증
    # ========================================================

    st.subheader(
        "④ 어떤 테마가 실제로 잘 작동했는가"
    )

    theme_rows = []

    for theme, g in r.groupby("테마"):

        q = strategy_summary(
            g,
            "C_미래테마선행",
            20
        )

        if q["신호수"]:

            theme_rows.append({
                "테마": theme,
                "신호수": q["신호수"],
                "20일 승률": q["승률"],
                "20일 평균": q["평균수익"],
                "60일 평균":
                    strategy_summary(
                        g,
                        "C_미래테마선행",
                        60
                    )["평균수익"],
                "60일 평균낙폭":
                    strategy_summary(
                        g,
                        "C_미래테마선행",
                        60
                    )["평균낙폭"],
            })


    if theme_rows:

        st.dataframe(
            pd.DataFrame(
                theme_rows
            ).sort_values(
                "20일 평균",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "20일 승률":
                    st.column_config.NumberColumn(
                        format="%.1f%%"
                    ),
                "20일 평균":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),
                "60일 평균":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),
                "60일 평균낙폭":
                    st.column_config.NumberColumn(
                        format="%.2f%%"
                    ),
            },
        )


    # ========================================================
    # ⑤ 최종 판단
    # ========================================================

    st.subheader(
        "⑤ 최종 판단"
    )

    c20 = strategy_summary(
        r,
        "C_미래테마선행",
        20
    )

    d20 = strategy_summary(
        r,
        "D_미래테마선행가격",
        20
    )

    c60 = strategy_summary(
        r,
        "C_미래테마선행",
        60
    )

    d60 = strategy_summary(
        r,
        "D_미래테마선행가격",
        60
    )


    if (
        d20["신호수"]
        and c20["신호수"]
    ):

        delta20 = (
            d20["평균수익"]
            - c20["평균수익"]
        )

        delta60 = (
            d60["평균수익"]
            - c60["평균수익"]
            if d60["신호수"]
            else np.nan
        )


        if (
            delta20 > 0
            and (
                np.isnan(delta60)
                or delta60 > 0
            )
        ):

            st.success(
                f"가격구간을 추가했을 때 평균수익이 개선되었습니다. "
                f"20일 {delta20:+.2f}%p / "
                f"60일 {delta60:+.2f}%p"
            )

        else:

            st.warning(
                f"가격구간 추가 효과가 뚜렷하지 않습니다. "
                f"20일 {delta20:+.2f}%p / "
                f"60일 {delta60:+.2f}%p"
            )


    # ========================================================
    # ⑥ 원본 데이터
    # ========================================================

    with st.expander(
        "⑥ 전체 검사 원본 데이터"
    ):

        st.dataframe(
            r,
            use_container_width=True,
            hide_index=True,
            height=520
        )


    # ========================================================
    # ⑦ 100만원 실제 운용 시뮬레이션
    # ========================================================

    st.markdown("---")

    st.subheader(
        "⑦ 💰 100만원 실제 운용 시뮬레이션"
    )

    st.caption(
        "D 전략 신호가 발생했을 때 "
        "1회 1포지션으로 순차 진입합니다. "
        "보유 중 새 신호는 건너뛰며, "
        "수수료와 슬리피지를 포함합니다."
    )


    sc1, sc2, sc3, sc4 = st.columns(4)


    initial_cash = sc1.number_input(
        "초기자금",
        min_value=100000,
        value=1000000,
        step=100000,
        key="sim_cash"
    )


    hold_days = sc2.selectbox(
        "보유기간",
        [5, 20, 60],
        index=1,
        key="sim_hold"
    )


    fee = sc3.number_input(
        "편도 비용",
        min_value=0.0,
        max_value=1.0,
        value=0.10,
        step=0.01,
        key="sim_fee",
        help="수수료·세금 등을 단순화한 가정(%)"
    )


    slip = sc4.number_input(
        "편도 슬리피지",
        min_value=0.0,
        max_value=1.0,
        value=0.05,
        step=0.01,
        key="sim_slip",
        help="신호와 실제 체결가격 차이 가정(%)"
    )


    # ========================================================
    # 중요 수정 ③
    # 100만원 버튼을 눌러 Streamlit이 재실행되어도
    # session_state에 저장된 data를 사용한다.
    # ========================================================

    if st.button(
        "💰 100만원 운용 결과 계산",
        type="primary",
        use_container_width=True
    ):

        current_result = (
            st.session_state.get(
                "strategy_result"
            )
        )

        current_data = (
            st.session_state.get(
                "strategy_data"
            )
        )


        # 안전장치
        if (
            current_result is None
            or current_result.empty
        ):

            st.warning(
                "먼저 '전체 투자로직 백테스트'를 실행하십시오."
            )

        elif (
            current_data is None
            or not isinstance(
                current_data,
                dict
            )
            or not current_data
        ):

            st.warning(
                "백테스트 가격 데이터가 없습니다. "
                "전체 투자로직 백테스트를 다시 실행하십시오."
            )

        else:

            try:

                curve, m = (
                    simulate_equity_curve(
                        current_result,
                        current_data,
                        initial_cash=float(
                            initial_cash
                        ),
                        hold_days=int(
                            hold_days
                        ),
                        fee_per_side=float(
                            fee
                        ) / 100,
                        slippage_per_side=float(
                            slip
                        ) / 100,
                    )
                )


                st.session_state[
                    "sim_curve"
                ] = curve

                st.session_state[
                    "sim_metrics"
                ] = m

                st.session_state[
                    "sim_hold"
                ] = hold_days


            except Exception as ex:

                st.error(
                    "100만원 운용 시뮬레이션 중 오류가 발생했습니다."
                )

                st.exception(ex)


    # ========================================================
    # 저장된 시뮬레이션 결과
    # ========================================================

    m = st.session_state.get(
        "sim_metrics"
    )

    curve = st.session_state.get(
        "sim_curve"
    )


    if m is not None:

        mc = st.columns(5)


        mc[0].metric(
            "최종자산",
            f"₩{m['최종자산']:,.0f}"
        )


        mc[1].metric(
            "총수익률",
            f"{m['총수익률']:+.1f}%"
        )


        mc[2].metric(
            "연환산",
            (
                f"{m['연환산']:+.1f}%"
                if np.isfinite(
                    m["연환산"]
                )
                else "-"
            )
        )


        mc[3].metric(
            "승률",
            (
                f"{m['승률']:.1f}%"
                if np.isfinite(
                    m["승률"]
                )
                else "-"
            )
        )


        mc[4].metric(
            "최대낙폭",
            f"{m['최대낙폭']:.1f}%"
        )


        if (
            curve is not None
            and not curve.empty
        ):

            import plotly.graph_objects as go


            fig = go.Figure()


            fig.add_trace(
                go.Scatter(
                    x=curve["날짜"],
                    y=curve["자산"],
                    mode="lines",
                    name="D 전략 자산",
                )
            )


            fig.update_layout(
                height=380,
                margin=dict(
                    l=10,
                    r=10,
                    t=30,
                    b=10
                ),
                yaxis_title="자산(원)",
                xaxis_title="날짜",
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )


        trades = (
            m.get("trades")
            if isinstance(m, dict)
            else None
        )


        if (
            trades is not None
            and not trades.empty
        ):

            st.markdown(
                f"**거래 {len(trades)}회 · "
                f"평균 거래수익 "
                f"{trades['순수익률'].mean():+.2f}%**"
            )


            st.dataframe(
                trades,
                use_container_width=True,
                hide_index=True
            )


            st.download_button(
                "📥 100만원 거래내역 CSV",
                trades.to_csv(
                    index=False
                ).encode("utf-8-sig"),
                "ETF_RADAR_100만원_거래내역.csv",
                "text/csv",
                use_container_width=True,
            )


    # ========================================================
    # 전략 백테스트 CSV
    # ========================================================

    st.download_button(
        "📥 전략 백테스트 CSV 저장",
        r.to_csv(
            index=False
        ).encode("utf-8-sig"),
        "ETF_RADAR_STRATEGY_BACKTEST.csv",
        "text/csv",
        use_container_width=True,
    )