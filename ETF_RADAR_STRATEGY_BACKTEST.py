# -*- coding: utf-8 -*-
"""
ETF RADAR STRATEGY BACKTEST

A: 단순 테마
B: 선행점수
C: 미래테마 + 선행 ETF
D: 미래테마 + 선행 ETF + 가격구간

연구용 백테스트
- 신호일 종가가 아닌 다음 거래일 종가 진입
- 실제 주문 체결/세금/배당/환전비용은 완전히 반영하지 않음

추가 기능
- 전략 진단
- 점수구간별 성과
- ETF별 성과
- 테마별 성과
- 가격상태별 성과
- 점수와 수익률의 상관관계
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="ETF RADAR STRATEGY TEST",
    page_icon="🧪",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

def init_session_state():

    defaults = {
        "strategy_result": None,
        "strategy_data": None,
        "sim_curve": None,
        "sim_metrics": None,
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


init_session_state()


# ============================================================
# 1. TEST UNIVERSE
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

    "미국기술": [
        "QQQ",
        "XLK"
    ],

    "반도체": [
        "SMH",
        "SOXX"
    ],

    "로봇AI": [
        "BOTZ",
        "ARKQ"
    ],

    "위험선호": [
        "QQQ",
        "XLK",
        "SMH",
        "SOXX",
        "BOTZ",
        "ARKQ"
    ],

    "방어자산": [
        "GLD",
        "TLT"
    ],

    "글로벌": [
        "INDA",
        "EWY",
        "EWJ",
        "EEM"
    ],
}


# ============================================================
# 2. DATA
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def download_prices(
    tickers,
    start,
    end
):

    symbols = list(
        dict.fromkeys(
            list(tickers)
            + [BENCH]
        )
    )

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

                d.columns = [
                    str(c)
                    for c in d.columns
                ]

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
        d.get(
            "Volume",
            np.nan
        ),
        errors="coerce"
    )

    d = d.dropna(
        subset=["Close"]
    )

    d["MA20"] = (
        d["Close"]
        .rolling(20)
        .mean()
    )

    d["MA60"] = (
        d["Close"]
        .rolling(60)
        .mean()
    )

    d["R5"] = (
        d["Close"]
        .pct_change(5)
        * 100
    )

    d["R20"] = (
        d["Close"]
        .pct_change(20)
        * 100
    )

    d["R60"] = (
        d["Close"]
        .pct_change(60)
        * 100
    )

    d["VR"] = (
        d["Volume"]
        /
        d["Volume"]
        .rolling(20)
        .mean()
    )

    delta = d["Close"].diff()

    gain = (
        delta
        .clip(lower=0)
        .rolling(14)
        .mean()
    )

    loss = (
        -delta
        .clip(upper=0)
        .rolling(14)
        .mean()
    )

    rs = (
        gain
        /
        loss.replace(
            0,
            np.nan
        )
    )

    d["RSI"] = (
        100
        -
        100
        /
        (1 + rs)
    )

    d["VOL20"] = (
        d["Volume"]
        .rolling(20)
        .mean()
    )

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
# 3. LEADING SIGNAL
# ============================================================

def leading_signal(
    row,
    benchmark_ret20=0
):

    current = float(
        row.get(
            "Close",
            0
        )
        or 0
    )

    ma20 = float(
        row.get(
            "MA20",
            current
        )
        or current
    )

    ma60 = float(
        row.get(
            "MA60",
            current
        )
        or current
    )

    ret5 = float(
        row.get(
            "R5",
            0
        )
        or 0
    )

    ret20 = float(
        row.get(
            "R20",
            0
        )
        or 0
    )

    vr = float(
        row.get(
            "VR",
            1
        )
        or 1
    )

    rsi = float(
        row.get(
            "RSI",
            50
        )
        or 50
    )

    dist20 = (

        (
            current
            /
            ma20
            - 1
        )
        * 100

        if ma20

        else 0
    )

    rs20 = (
        ret20
        -
        benchmark_ret20
    )

    accel = (
        ret5
        -
        ret20 / 4
    )

    early_price = (

        92
        if -1 <= dist20 <= 3

        else 82
        if dist20 <= 5

        else 65
        if dist20 < 8

        else 35
    )

    early_rsi = (

        92
        if 48 <= rsi <= 62

        else 84
        if 43 <= rsi < 68

        else 68
        if rsi < 72

        else 35
    )

    flow = (

        92
        if 1.10 <= vr <= 1.70

        else 82
        if 1.0 <= vr < 1.10

        else 76
        if 0.9 <= vr < 1.0

        else 58
        if vr < 2.2

        else 38
    )

    accel_score = (

        90
        if 0.5 <= accel <= 5

        else 78
        if 0 <= accel < 0.5

        else 68
        if accel > 5

        else 52
    )

    rel = (

        88
        if rs20 >= 6

        else 80
        if rs20 >= 3

        else 70
        if rs20 >= 0

        else 48
    )

    structure = (

        90

        if (
            current >= ma60
            and ma20 >= ma60
        )

        else 78

        if current >= ma60

        else 55

        if current >= ma20

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
                min(
                    100,
                    score
                )
            )
        ),

        "early_buy":
            bool(early_buy),

        "rs20":
            rs20,

        "dist20":
            dist20,

        "rsi":
            rsi,

        "vr":
            vr,

        "accel":
            accel,
    }


# ============================================================
# 4. THEME SCORE
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
            pd.isna(
                r.get("R20")
            )
            or
            pd.isna(
                r.get("R60")
            )
        ):

            continue

        sig = leading_signal(
            r,
            bench_ret20
        )

        vals.append({

            "r20":
                float(r["R20"]),

            "r60":
                float(r["R60"]),

            "rs20":
                sig["rs20"],

            "rs60":
                (
                    float(r["R60"])
                    -
                    bench_ret60
                ),

            "vr":
                float(
                    r.get(
                        "VR",
                        1
                    )
                    if pd.notna(
                        r.get(
                            "VR",
                            1
                        )
                    )
                    else 1
                ),

            "ma60gap": (

                (
                    float(r["Close"])
                    /
                    float(r["MA60"])
                    - 1
                )
                * 100

                if (
                    pd.notna(
                        r.get(
                            "MA60"
                        )
                    )
                    and r["MA60"]
                )

                else 0
            ),

            "accel":
                sig["accel"],

            "rsi":
                sig["rsi"],

            "lead":
                sig["score"],

            "early":
                sig["early_buy"],
        })

    if len(vals) < 2:

        return None

    x = pd.DataFrame(vals)

    def clip_score(
        v,
        lo,
        hi
    ):

        return float(

            np.clip(

                (
                    v
                    - lo
                )
                /
                (
                    hi
                    - lo
                )
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
        (
            x["r20"]
            > -2
        ).mean()
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

    rsi = float(

        np.clip(

            100
            -
            abs(
                float(
                    x["rsi"].mean()
                )
                - 58
            )
            * 2.5,

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
        early_count
        /
        len(x)
    )

    lead_avg = float(
        x["lead"].mean()
    )

    lead_theme = (

        lead_avg * 0.55

        + breadth * 0.25

        + early_ratio
        * 100
        * 0.20
    )

    final = (

        score * 0.70

        + lead_theme * 0.30
    )

    heat = 0

    if float(
        x["rsi"].mean()
    ) >= 75:

        heat += 12

    if float(
        x["r20"].mean()
    ) >= 12:

        heat += 10

    if float(
        x["ma60gap"].mean()
    ) >= 15:

        heat += 8

    final = float(

        np.clip(

            final
            - heat,

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

        "score":
            final,

        "stage":
            stage,

        "breadth":
            breadth,

        "lead_avg":
            lead_avg,

        "early_count":
            early_count,

        "members":
            len(x),

        "heat":
            heat,
    }


# ============================================================
# 5. SNAPSHOT
# ============================================================

def build_snapshot(
    all_data,
    date_i
):

    bench = all_data.get(
        BENCH
    )

    if (
        bench is None
        or bench.empty
    ):

        return None

    b = bench.iloc[
        :date_i + 1
    ]

    if len(b) < 65:

        return None

    br = b.iloc[-1]

    bench_ret20 = float(
        br.get(
            "R20",
            np.nan
        )
    )

    bench_ret60 = float(
        br.get(
            "R60",
            np.nan
        )
    )

    if (
        not np.isfinite(
            bench_ret20
        )
        or
        not np.isfinite(
            bench_ret60
        )
    ):

        return None

    theme_results = []

    for theme, members in (
        THEME_GROUPS.items()
    ):

        rows = []

        for t in members:

            d = all_data.get(t)

            if (
                d is None
                or d.empty
                or len(d) <= date_i
            ):

                continue

            r = d.iloc[
                date_i
            ]

            if (
                pd.isna(
                    r.get(
                        "MA60"
                    )
                )
                or
                pd.isna(
                    r.get(
                        "R20"
                    )
                )
                or
                pd.isna(
                    r.get(
                        "R60"
                    )
                )
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
        key=lambda z:
            z["score"],
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

        c = float(
            r["Close"]
        )

        ma20 = float(
            r["MA20"]
        )

        rsi = sig["rsi"]

        dist20 = sig["dist20"]

        if rsi >= 78:

            heat += 32

        elif rsi >= 72:

            heat += 24

        elif rsi >= 68:

            heat += 12

        if float(
            r["R5"]
        ) >= 10:

            heat += 25

        elif float(
            r["R5"]
        ) >= 7:

            heat += 18

        elif float(
            r["R5"]
        ) >= 5:

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

            "ETF":
                r["ETF"],

            "sig":
                sig,

            "heat":
                min(
                    100,
                    heat
                ),

            "close":
                c,

            "ma20":
                ma20,
        })

    if not candidates:

        return None

    candidates.sort(

        key=lambda z:

            z["sig"]["score"]
            -
            z["heat"] * 0.35,

        reverse=True
    )

    winner = candidates[0]

    return {

        "theme":
            top["theme"],

        "theme_score":
            top["score"],

        "theme_stage":
            top["stage"],

        "winner":
            winner,

        "themes":
            theme_results,
    }


# ============================================================
# 6. PRICE ZONE
# ============================================================

def price_zone(r):

    c = float(
        r["Close"]
    )

    ma20 = float(
        r["MA20"]
    )

    ma60 = float(
        r["MA60"]
    )

    low20 = float(
        r["LOW20"]
    )

    support = max(
        low20,
        ma20 * 0.985
    )

    ideal_top = (
        ma20 * 1.025
    )

    invalid = min(
        ma60 * 0.97,
        support * 0.97
    )

    if (
        c <= ideal_top
        and
        c >= invalid
        and
        c >= ma60 * 0.98
    ):

        state = "매수구간"

    elif c < invalid:

        state = "무효"

    elif c > ma20 * 1.07:

        state = "추격금지"

    else:

        state = "눌림대기"

    return {

        "state":
            state,

        "support":
            support,

        "ideal_top":
            ideal_top,

        "invalid":
            invalid,
    }


# ============================================================
# 7. BACKTEST
# ============================================================

def run_strategy_backtest(
    start,
    end,
    tickers,
    step_days=5
):

    download_start = (

        pd.Timestamp(start)
        -
        pd.Timedelta(
            days=140
        )

    ).strftime(
        "%Y-%m-%d"
    )

    download_end = (

        pd.Timestamp(end)
        +
        pd.Timedelta(
            days=80
        )

    ).strftime(
        "%Y-%m-%d"
    )

    raw = download_prices(
        tickers,
        download_start,
        download_end
    )

    data = {

        k:
        indicators(v)

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

    common = data[
        BENCH
    ].index

    for t in tickers:

        if t in data:

            common = common.intersection(
                data[t].index
            )

    common = common.sort_values()

    common = common[

        (
            common
            >= pd.Timestamp(start)
        )

        &

        (
            common
            <= pd.Timestamp(end)
        )
    ]

    rows = []

    for pos in range(

        0,

        len(common) - 61,

        max(
            1,
            step_days
        )
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

        winner = snap[
            "winner"
        ]

        t = winner["ETF"]

        d = data[t]

        if (
            hist_pos + 60
            >= len(d)
        ):

            continue

        entry_i = (
            hist_pos + 1
        )

        entry = d.iloc[
            entry_i
        ]

        entry_price = float(
            entry["Close"]
        )

        if (
            not np.isfinite(
                entry_price
            )
            or
            entry_price <= 0
        ):

            continue

        sig = winner["sig"]

        zone = price_zone(
            d.iloc[
                hist_pos
            ]
        )

        a_ok = True

        b_ok = (

            sig["score"] >= 72

            and
            sig["early_buy"]
        )

        c_ok = (

            snap["theme_score"]
            >= 60

            and
            b_ok
        )

        d_ok = (

            c_ok

            and
            zone["state"]
            == "매수구간"
        )

        future = d.iloc[
            entry_i:
            entry_i + 60
        ]

        if len(future) < 60:

            continue

        rec = {

            "날짜":
                dt.date(),

            "테마":
                snap["theme"],

            "테마점수":
                round(
                    snap[
                        "theme_score"
                    ],
                    1
                ),

            "테마단계":
                snap[
                    "theme_stage"
                ],

            "ETF":
                t,

            "선행점수":
                sig["score"],

            "과열점수":
                winner["heat"],

            "가격상태":
                zone["state"],

            "매수가":
                entry_price,

            "A_단순테마":
                a_ok,

            "B_선행점수":
                b_ok,

            "C_미래테마선행":
                c_ok,

            "D_미래테마선행가격":
                d_ok,
        }

        for n in [
            5,
            20,
            60
        ]:

            ret = (

                float(
                    future.iloc[
                        n - 1
                    ]["Close"]
                )
                /
                entry_price
                - 1

            ) * 100

            dd = (

                float(
                    future.iloc[
                        :n
                    ]["Close"].min()
                )
                /
                entry_price
                - 1

            ) * 100

            rec[
                f"{n}일수익"
            ] = ret

            rec[
                f"{n}일최저낙폭"
            ] = dd

        rows.append(rec)

    return (
        pd.DataFrame(rows),
        data
    )


# ============================================================
# 8. SUMMARY
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

            "신호수":
                0,

            "승률":
                np.nan,

            "평균수익":
                np.nan,

            "중앙값":
                np.nan,

            "평균낙폭":
                np.nan,

            "최고":
                np.nan,

            "최대손실":
                np.nan,
        }

    return {

        "신호수":
            len(x),

        "승률":
            (
                x > 0
            ).mean() * 100,

        "평균수익":
            x.mean(),

        "중앙값":
            x.median(),

        "평균낙폭":
            (
                dd.mean()
                if not dd.empty
                else np.nan
            ),

        "최고":
            x.max(),

        "최대손실":
            x.min(),
    }


# ============================================================
# 9. STRATEGY DIAGNOSIS
# ============================================================

def diagnostic_table(
    df,
    group_col,
    horizon=20
):

    if (
        df is None
        or df.empty
        or group_col not in df.columns
    ):

        return pd.DataFrame()

    ret_col = (
        f"{horizon}일수익"
    )

    if ret_col not in df.columns:

        return pd.DataFrame()

    rows = []

    for value, g in (
        df.groupby(
            group_col,
            dropna=False
        )
    ):

        x = pd.to_numeric(
            g[ret_col],
            errors="coerce"
        ).dropna()

        if x.empty:

            continue

        rows.append({

            group_col:
                value,

            "거래수":
                len(x),

            "승률":
                (
                    x > 0
                ).mean() * 100,

            "평균수익":
                x.mean(),

            "중앙값":
                x.median(),

            "최고수익":
                x.max(),

            "최대손실":
                x.min(),

            "누적단순수익":
                x.sum(),
        })

    if not rows:

        return pd.DataFrame()

    return pd.DataFrame(
        rows
    ).sort_values(
        "평균수익",
        ascending=False
    )


def score_correlation(
    df,
    score_col,
    return_col
):

    if (
        df is None
        or df.empty
        or score_col not in df.columns
        or return_col not in df.columns
    ):

        return np.nan

    x = df[
        [
            score_col,
            return_col
        ]
    ].copy()

    x[score_col] = pd.to_numeric(
        x[score_col],
        errors="coerce"
    )

    x[return_col] = pd.to_numeric(
        x[return_col],
        errors="coerce"
    )

    x = x.dropna()

    if len(x) < 3:

        return np.nan

    if (
        x[score_col].nunique()
        < 2
        or
        x[return_col].nunique()
        < 2
    ):

        return np.nan

    return float(
        x[score_col].corr(
            x[return_col]
        )
    )


def build_diagnostic_messages(
    r
):

    messages = []

    if (
        r is None
        or r.empty
    ):

        return messages

    ret20 = "20일수익"

    # --------------------------------------------------------
    # 1. 선행점수와 수익률 관계
    # --------------------------------------------------------

    corr = score_correlation(
        r,
        "선행점수",
        ret20
    )

    if np.isfinite(corr):

        if corr <= -0.20:

            messages.append(
                (
                    "warning",
                    "선행점수가 높을수록 "
                    "20일 수익률이 오히려 낮아지는 "
                    "경향이 있습니다."
                    f" 현재 상관계수 {corr:+.2f}"
                )
            )

        elif corr < 0.20:

            messages.append(
                (
                    "warning",
                    "선행점수와 20일 수익률의 "
                    "관계가 약합니다."
                    f" 현재 상관계수 {corr:+.2f}"
                )
            )

        else:

            messages.append(
                (
                    "success",
                    "선행점수와 20일 수익률 사이에 "
                    "양의 관계가 확인됩니다."
                    f" 현재 상관계수 {corr:+.2f}"
                )
            )

    # --------------------------------------------------------
    # 2. 테마점수와 수익률
    # --------------------------------------------------------

    theme_corr = score_correlation(
        r,
        "테마점수",
        ret20
    )

    if np.isfinite(theme_corr):

        if theme_corr <= -0.20:

            messages.append(
                (
                    "warning",
                    "테마점수가 높아질수록 "
                    "20일 성과가 악화되는 경향이 있습니다."
                    f" 상관계수 {theme_corr:+.2f}"
                )
            )

        elif theme_corr < 0.20:

            messages.append(
                (
                    "warning",
                    "테마점수와 실제 수익률의 "
                    "관계가 아직 뚜렷하지 않습니다."
                    f" 상관계수 {theme_corr:+.2f}"
                )
            )

        else:

            messages.append(
                (
                    "success",
                    "테마점수와 수익률 사이에 "
                    "양의 관계가 확인됩니다."
                    f" 상관계수 {theme_corr:+.2f}"
                )
            )

    # --------------------------------------------------------
    # 3. 가격상태 분포
    # --------------------------------------------------------

    if "가격상태" in r.columns:

        counts = (
            r["가격상태"]
            .value_counts()
        )

        total = len(r)

        if total:

            buy_count = int(
                counts.get(
                    "매수구간",
                    0
                )
            )

            buy_ratio = (
                buy_count
                /
                total
                * 100
            )

            if buy_ratio >= 90:

                messages.append(
                    (
                        "warning",
                        "가격구간 판정의 "
                        f"{buy_ratio:.1f}%가 "
                        "'매수구간'입니다. "
                        "현재 가격 필터가 실제 매매를 "
                        "거르는 역할을 충분히 하지 못할 "
                        "가능성이 있습니다."
                    )
                )

            elif buy_ratio <= 50:

                messages.append(
                    (
                        "success",
                        "가격구간 필터가 "
                        "매수/비매수 구간을 "
                        "구분하고 있습니다."
                    )
                )

    # --------------------------------------------------------
    # 4. 큰 손실
    # --------------------------------------------------------

    if ret20 in r.columns:

        x = pd.to_numeric(
            r[ret20],
            errors="coerce"
        ).dropna()

        if not x.empty:

            worst = float(
                x.min()
            )

            if worst <= -10:

                messages.append(
                    (
                        "warning",
                        "20일 기준 "
                        f"{worst:+.2f}%의 큰 손실 거래가 "
                        "존재합니다. "
                        "진입 필터뿐 아니라 손실관리 "
                        "조건도 검토할 필요가 있습니다."
                    )
                )

    return messages


def render_diagnostic(
    r
):

    st.subheader(
        "⑥ 🔍 전략 진단"
    )

    st.caption(
        "현재 백테스트 결과를 이용해 "
        "어떤 점수·테마·ETF·가격조건이 "
        "실제 수익과 연결되는지 확인합니다. "
        "이 단계에서는 투자로직을 변경하지 않습니다."
    )

    if (
        r is None
        or r.empty
    ):

        st.info(
            "진단할 백테스트 결과가 없습니다."
        )

        return

    # ========================================================
    # DIAGNOSTIC OVERVIEW
    # ========================================================

    d1, d2, d3, d4 = st.columns(4)

    d1.metric(
        "전체 검사",
        f"{len(r):,}건"
    )

    d_corr = score_correlation(
        r,
        "선행점수",
        "20일수익"
    )

    d2.metric(
        "선행점수↔20일수익",
        (
            f"{d_corr:+.2f}"
            if np.isfinite(d_corr)
            else "-"
        )
    )

    t_corr = score_correlation(
        r,
        "테마점수",
        "20일수익"
    )

    d3.metric(
        "테마점수↔20일수익",
        (
            f"{t_corr:+.2f}"
            if np.isfinite(t_corr)
            else "-"
        )
    )

    if "가격상태" in r.columns:

        buy_ratio = (
            (
                r["가격상태"]
                == "매수구간"
            ).mean()
            * 100
        )

    else:

        buy_ratio = np.nan

    d4.metric(
        "'매수구간' 비율",
        (
            f"{buy_ratio:.1f}%"
            if np.isfinite(
                buy_ratio
            )
            else "-"
        )
    )

    # ========================================================
    # 1. LEADING SCORE
    # ========================================================

    st.markdown(
        "#### ⑥-1 선행점수 구간별 성과"
    )

    score_df = r.copy()

    score_df["선행점수구간"] = pd.cut(
        pd.to_numeric(
            score_df["선행점수"],
            errors="coerce"
        ),
        bins=[
            -np.inf,
            70,
            80,
            85,
            90,
            np.inf
        ],
        labels=[
            "70 미만",
            "70~80",
            "80~85",
            "85~90",
            "90 이상"
        ],
        right=False
    )

    score_table = diagnostic_table(
        score_df,
        "선행점수구간",
        20
    )

    if not score_table.empty:

        st.dataframe(
            score_table,
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

                "최고수익":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),

                "최대손실":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),

                "누적단순수익":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),
            }
        )

    # ========================================================
    # 2. THEME SCORE
    # ========================================================

    st.markdown(
        "#### ⑥-2 테마점수 구간별 성과"
    )

    theme_score_df = r.copy()

    theme_score_df[
        "테마점수구간"
    ] = pd.cut(
        pd.to_numeric(
            theme_score_df[
                "테마점수"
            ],
            errors="coerce"
        ),
        bins=[
            -np.inf,
            50,
            60,
            70,
            80,
            np.inf
        ],
        labels=[
            "50 미만",
            "50~60",
            "60~70",
            "70~80",
            "80 이상"
        ],
        right=False
    )

    theme_score_table = diagnostic_table(
        theme_score_df,
        "테마점수구간",
        20
    )

    if not theme_score_table.empty:

        st.dataframe(
            theme_score_table,
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

                "최고수익":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),

                "최대손실":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),

                "누적단순수익":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),
            }
        )

    # ========================================================
    # 3. ETF
    # ========================================================

    st.markdown(
        "#### ⑥-3 ETF별 성과"
    )

    etf_table = diagnostic_table(
        r,
        "ETF",
        20
    )

    if not etf_table.empty:

        st.dataframe(
            etf_table,
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

                "최고수익":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),

                "최대손실":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),

                "누적단순수익":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),
            }
        )

    # ========================================================
    # 4. THEME
    # ========================================================

    st.markdown(
        "#### ⑥-4 테마별 성과"
    )

    theme_table = diagnostic_table(
        r,
        "테마",
        20
    )

    if not theme_table.empty:

        st.dataframe(
            theme_table,
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

                "최고수익":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),

                "최대손실":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),

                "누적단순수익":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),
            }
        )

    # ========================================================
    # 5. PRICE STATE
    # ========================================================

    st.markdown(
        "#### ⑥-5 가격상태별 성과"
    )

    price_table = diagnostic_table(
        r,
        "가격상태",
        20
    )

    if not price_table.empty:

        st.dataframe(
            price_table,
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

                "최고수익":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),

                "최대손실":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),

                "누적단순수익":
                    st.column_config.NumberColumn(
                        format="%+.2f%%"
                    ),
            }
        )

    # ========================================================
    # 6. CORRELATION
    # ========================================================

    st.markdown(
        "#### ⑥-6 점수와 실제 수익률의 관계"
    )

    corr_rows = []

    for score_name in [
        "선행점수",
        "테마점수",
        "과열점수"
    ]:

        for horizon in [
            5,
            20,
            60
        ]:

            corr = score_correlation(
                r,
                score_name,
                f"{horizon}일수익"
            )

            corr_rows.append({

                "지표":
                    score_name,

                "기간":
                    f"{horizon}일",

                "상관계수":
                    corr,
            })

    corr_table = pd.DataFrame(
        corr_rows
    )

    st.dataframe(
        corr_table,
        use_container_width=True,
        hide_index=True,
        column_config={

            "상관계수":
                st.column_config.NumberColumn(
                    format="%+.3f"
                )
        }
    )

    st.caption(
        "상관계수는 +1에 가까울수록 "
        "점수가 높을 때 수익률도 높아지는 경향, "
        "-1에 가까울수록 반대 경향을 의미합니다. "
        "표본이 적으면 통계적 의미가 약할 수 있습니다."
    )

    # ========================================================
    # 7. AUTOMATIC DIAGNOSIS
    # ========================================================

    st.markdown(
        "#### ⑥-7 현재 데이터의 자동 진단"
    )

    messages = build_diagnostic_messages(
        r
    )

    if not messages:

        st.info(
            "현재 데이터로 판단할 수 있는 "
            "뚜렷한 진단 항목이 부족합니다."
        )

    else:

        for level, message in messages:

            if level == "warning":

                st.warning(
                    message
                )

            elif level == "success":

                st.success(
                    message
                )

            else:

                st.info(
                    message
                )

    # ========================================================
    # 8. IMPORTANT NOTE
    # ========================================================

    st.info(
        "⚠ 전략 진단은 현재 백테스트 데이터를 "
        "설명하기 위한 기능입니다. "
        "이 결과만으로 특정 ETF의 미래 수익을 "
        "보장하지 않습니다. "
        "거래 수가 적은 경우 반드시 별도의 기간 "
        "검증이 필요합니다."
    )


# ============================================================
# 10. EQUITY SIMULATION
# ============================================================

def simulate_equity_curve(
    r,
    data,
    initial_cash=1_000_000,
    hold_days=20,
    fee_per_side=0.0010,
    slippage_per_side=0.0005
):

    if (
        r is None
        or r.empty
    ):

        return (
            pd.DataFrame(),
            {}
        )

    if (
        data is None
        or not isinstance(
            data,
            dict
        )
    ):

        return (
            pd.DataFrame(),
            {}
        )

    rr = r.loc[
        r[
            "D_미래테마선행가격"
        ] == True
    ].copy()

    if rr.empty:

        return (

            pd.DataFrame(),

            {

                "초기자산":
                    initial_cash,

                "최종자산":
                    initial_cash,

                "총수익률":
                    0.0,

                "승률":
                    np.nan,

                "거래수":
                    0,

                "최대낙폭":
                    0.0,

                "연환산":
                    np.nan,

                "평균거래수익":
                    np.nan,

                "trades":
                    pd.DataFrame(),
            }
        )

    rr["날짜"] = pd.to_datetime(
        rr["날짜"]
    )

    rr = (
        rr
        .sort_values(
            "날짜"
        )
        .reset_index(
            drop=True
        )
    )

    cash = float(
        initial_cash
    )

    equity_rows = []

    trades = []

    next_available = (
        pd.Timestamp.min
    )

    wins = 0

    for _, sig in rr.iterrows():

        signal_date = pd.Timestamp(
            sig["날짜"]
        )

        if (
            signal_date
            <
            next_available
        ):

            continue

        ticker = sig["ETF"]

        d = data.get(
            ticker
        )

        if (
            d is None
            or d.empty
        ):

            continue

        idx = d.index.searchsorted(
            signal_date
        )

        entry_i = (
            idx + 1
        )

        exit_i = (

            entry_i
            +
            int(hold_days)
            - 1
        )

        if (
            entry_i >= len(d)
            or
            exit_i >= len(d)
        ):

            continue

        entry_date = (
            d.index[entry_i]
        )

        exit_date = (
            d.index[exit_i]
        )

        entry_raw = float(
            d.iloc[
                entry_i
            ]["Close"]
        )

        exit_raw = float(
            d.iloc[
                exit_i
            ]["Close"]
        )

        if (
            not np.isfinite(
                entry_raw
            )
            or
            not np.isfinite(
                exit_raw
            )
            or
            entry_raw <= 0
        ):

            continue

        buy_price = (

            entry_raw
            *
            (
                1
                +
                slippage_per_side
            )
        )

        sell_price = (

            exit_raw
            *
            (
                1
                -
                slippage_per_side
            )
        )

        gross_ret = (

            sell_price
            /
            buy_price
            - 1
        )

        net_ret = (

            gross_ret
            -
            fee_per_side * 2
        )

        cash *= (
            1
            +
            net_ret
        )

        wins += int(
            net_ret > 0
        )

        next_available = (

            exit_date
            +
            pd.Timedelta(
                days=1
            )
        )

        trades.append({

            "신호일":
                signal_date.date(),

            "진입일":
                entry_date.date(),

            "청산일":
                exit_date.date(),

            "테마":
                sig["테마"],

            "ETF":
                ticker,

            "테마점수":
                sig["테마점수"],

            "선행점수":
                sig["선행점수"],

            "가격상태":
                sig["가격상태"],

            "진입가격":
                entry_raw,

            "청산가격":
                exit_raw,

            "순수익률":
                net_ret * 100,

            "거래후자산":
                cash,
        })

        equity_rows.append({

            "날짜":
                exit_date,

            "자산":
                cash,
        })

    trades_df = pd.DataFrame(
        trades
    )

    curve = pd.DataFrame(
        equity_rows
    )

    if curve.empty:

        return (

            curve,

            {

                "초기자산":
                    initial_cash,

                "최종자산":
                    initial_cash,

                "총수익률":
                    0.0,

                "승률":
                    np.nan,

                "거래수":
                    0,

                "최대낙폭":
                    0.0,

                "연환산":
                    np.nan,

                "평균거래수익":
                    np.nan,

                "trades":
                    trades_df,
            }
        )

    curve = (

        curve
        .sort_values(
            "날짜"
        )
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
        /
        curve["고점"]
        - 1

    ) * 100

    final_cash = float(
        curve.iloc[-1][
            "자산"
        ]
    )

    total_ret = (

        final_cash
        /
        initial_cash
        - 1

    ) * 100

    days = max(

        1,

        (
            pd.Timestamp(
                curve.iloc[-1][
                    "날짜"
                ]
            )
            -
            pd.Timestamp(
                curve.iloc[0][
                    "날짜"
                ]
            )
        ).days
    )

    annualized = (

        (
            final_cash
            /
            initial_cash
        )
        **
        (
            365.25
            /
            days
        )
        - 1

    ) * 100 if final_cash > 0 else -100

    metrics = {

        "초기자산":
            initial_cash,

        "최종자산":
            final_cash,

        "총수익률":
            total_ret,

        "승률": (

            wins
            /
            len(trades_df)
            * 100

            if len(trades_df)

            else np.nan
        ),

        "거래수":
            len(trades_df),

        "최대낙폭":
            float(
                curve[
                    "낙폭"
                ].min()
            ),

        "연환산":
            annualized,

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

        "trades":
            trades_df,
    }


# ============================================================
# 11. UI
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
    "현재 ETF RADAR의 핵심 로직에 실제 투자 우위가 있는지 "
    "확인하는 것입니다."
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
    options=[
        1,
        3,
        5,
        10
    ],
    value=5,
    format_func=lambda x:

        "매일"
        if x == 1
        else
        f"{x}거래일마다",
)

st.markdown("---")

run_clicked = st.button(
    "🧪 전체 투자로직 백테스트 실행",
    type="primary",
    use_container_width=True
)


# ============================================================
# 12. RUN BACKTEST
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
        expanded=True
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

            st.session_state[
                "strategy_result"
            ] = result

            st.session_state[
                "strategy_data"
            ] = data

            st.session_state[
                "sim_curve"
            ] = None

            st.session_state[
                "sim_metrics"
            ] = None

            status.update(
                label="백테스트 완료",
                state="complete",
                expanded=False
            )

        except Exception as ex:

            status.update(
                label="백테스트 실패",
                state="error",
                expanded=True
            )

            st.exception(ex)

            st.stop()


# ============================================================
# 13. RESTORE SESSION DATA
# ============================================================

r = st.session_state.get(
    "strategy_result"
)

data = st.session_state.get(
    "strategy_data"
)


# ============================================================
# 14. BEFORE TEST
# ============================================================

if r is None:

    st.markdown(
        "### 테스트 방법"
    )

    st.markdown(
        """
        **A. 단순 테마**
        → 테마 대표 ETF를 선택

        **B. 선행점수**
        → 선행점수 조건을 추가

        **C. 미래테마 + 선행**
        → 미래테마가 강한 구간에서만 선행 ETF 선택

        **D. 미래테마 + 선행 + 가격**
        → C에 현재 가격구간까지 추가

        최종적으로 **D가 A/B/C보다 지속적으로 우수한지**
        확인합니다.
        """
    )


# ============================================================
# 15. RESULTS
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

        "A 단순테마":
            "A_단순테마",

        "B 선행점수":
            "B_선행점수",

        "C 미래테마+선행":
            "C_미래테마선행",

        "D 미래테마+선행+가격":
            "D_미래테마선행가격",
    }


    # ========================================================
    # ① CORE RESULTS
    # ========================================================

    st.subheader(
        "① 한눈에 보는 핵심 결과"
    )

    for horizon in [
        20,
        60
    ]:

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
    # ② STRATEGY TABLE
    # ========================================================

    st.subheader(
        "② 전략 비교표"
    )

    rows = []

    for name, flag in (
        flags.items()
    ):

        for h in [
            5,
            20,
            60
        ]:

            q = strategy_summary(
                r,
                flag,
                h
            )

            rows.append({

                "전략":
                    name,

                "기간":
                    f"{h}일",

                "신호수":
                    q["신호수"],

                "승률":
                    q["승률"],

                "평균수익":
                    q["평균수익"],

                "중앙값":
                    q["중앙값"],

                "평균최저낙폭":
                    q["평균낙폭"],

                "최고수익":
                    q["최고"],

                "최대손실":
                    q["최대손실"],
            })

    summary = pd.DataFrame(
        rows
    )

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
        }
    )


    # ========================================================
    # ③ YEAR
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

    for year, g in (
        r2.groupby("연도")
    ):

        for name, flag in (
            flags.items()
        ):

            q = strategy_summary(
                g,
                flag,
                20
            )

            year_rows.append({

                "연도":
                    int(year),

                "전략":
                    name,

                "신호수":
                    q["신호수"],

                "20일 승률":
                    q["승률"],

                "20일 평균":
                    q["평균수익"],

                "20일 평균낙폭":
                    q["평균낙폭"],
            })

    st.dataframe(
        pd.DataFrame(
            year_rows
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

            "20일 평균낙폭":
                st.column_config.NumberColumn(
                    format="%.2f%%"
                ),
        }
    )


    # ========================================================
    # ④ THEME
    # ========================================================

    st.subheader(
        "④ 어떤 테마가 실제로 잘 작동했는가"
    )

    theme_rows = []

    for theme, g in (
        r.groupby("테마")
    ):

        q = strategy_summary(
            g,
            "C_미래테마선행",
            20
        )

        if q["신호수"]:

            theme_rows.append({

                "테마":
                    theme,

                "신호수":
                    q["신호수"],

                "20일 승률":
                    q["승률"],

                "20일 평균":
                    q["평균수익"],

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
            }
        )


    # ========================================================
    # ⑤ FINAL JUDGMENT
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
            -
            c20["평균수익"]
        )

        delta60 = (

            d60["평균수익"]
            -
            c60["평균수익"]

            if d60["신호수"]

            else np.nan
        )

        if (
            delta20 > 0
            and
            (
                np.isnan(
                    delta60
                )
                or
                delta60 > 0
            )
        ):

            st.success(

                f"가격구간을 추가했을 때 "
                f"평균수익이 개선되었습니다. "
                f"20일 {delta20:+.2f}%p / "
                f"60일 {delta60:+.2f}%p"
            )

        else:

            st.warning(

                f"가격구간 추가 효과가 "
                f"뚜렷하지 않습니다. "
                f"20일 {delta20:+.2f}%p / "
                f"60일 {delta60:+.2f}%p"
            )


    # ========================================================
    # ⑥ STRATEGY DIAGNOSIS
    # ========================================================

    render_diagnostic(
        r
    )


    # ========================================================
    # ⑦ RAW DATA
    # ========================================================

    with st.expander(
        "⑦ 전체 검사 원본 데이터"
    ):

        st.dataframe(
            r,
            use_container_width=True,
            hide_index=True,
            height=520
        )


    # ========================================================
    # ⑧ 1,000,000 WON SIMULATION
    # ========================================================

    st.markdown("---")

    st.subheader(
        "⑧ 💰 100만원 실제 운용 시뮬레이션"
    )

    st.caption(
        "D 전략 신호가 발생했을 때 "
        "1회 1포지션으로 순차 진입합니다. "
        "보유 중 새 신호는 건너뛰며, "
        "수수료와 슬리피지를 포함합니다."
    )

    sc1, sc2, sc3, sc4 = (
        st.columns(4)
    )

    initial_cash = sc1.number_input(
        "초기자금",
        min_value=100000,
        value=1000000,
        step=100000,
        key="sim_cash"
    )

    # 중요:
    # sim_hold는 selectbox가 직접 관리한다.
    # 아래에서 session_state에 다시 대입하지 않는다.

    hold_days = sc2.selectbox(
        "보유기간",
        [
            5,
            20,
            60
        ],
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
    # SIMULATION BUTTON
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

                # sim_hold는 수정하지 않는다.

            except Exception as ex:

                st.error(
                    "100만원 운용 시뮬레이션 중 오류가 발생했습니다."
                )

                st.exception(ex)


    # ========================================================
    # SIMULATION RESULT
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

        annualized = m.get(
            "연환산",
            np.nan
        )

        mc[2].metric(
            "연환산",
            (
                f"{annualized:+.1f}%"

                if np.isfinite(
                    annualized
                )

                else "-"
            )
        )

        win_rate = m.get(
            "승률",
            np.nan
        )

        mc[3].metric(
            "승률",
            (
                f"{win_rate:.1f}%"

                if np.isfinite(
                    win_rate
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
                    name="D 전략 자산"
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
                xaxis_title="날짜"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        trades = (
            m.get("trades")
            if isinstance(
                m,
                dict
            )
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
                ).encode(
                    "utf-8-sig"
                ),
                "ETF_RADAR_100만원_거래내역.csv",
                "text/csv",
                use_container_width=True
            )


    # ========================================================
    # BACKTEST CSV
    # ========================================================

    st.download_button(
        "📥 전략 백테스트 CSV 저장",
        r.to_csv(
            index=False
        ).encode(
            "utf-8-sig"
        ),
        "ETF_RADAR_STRATEGY_BACKTEST.csv",
        "text/csv",
        use_container_width=True
    )