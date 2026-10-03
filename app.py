# -*- coding: utf-8 -*-

import os
import json

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# ============================================================
# ETF RADAR FINAL
# 시장 새로고침 제거
# 한글 깨짐 방지
# 기존 분석 기능 유지
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# FILE
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"
UNIVERSE_FILE = "etf_universe_cache.json"


# ============================================================
# BASE ETF
# ============================================================

BASE_ETFS = {

    "069500": {
        "name": "KODEX 200",
        "ticker": "069500.KS",
        "themes": ["국내대표"]
    },

    "091160": {
        "name": "KODEX 반도체",
        "ticker": "091160.KS",
        "themes": ["AI 반도체", "반도체"]
    },

    "395160": {
        "name": "KODEX AI반도체TOP10",
        "ticker": "395160.KS",
        "themes": ["AI 반도체"]
    },

    "396500": {
        "name": "KODEX AI반도체 핵심장비",
        "ticker": "396500.KS",
        "themes": ["AI 반도체", "반도체장비"]
    },

    "464600": {
        "name": "TIGER AI반도체핵심공정",
        "ticker": "464600.KS",
        "themes": ["AI 반도체", "반도체장비"]
    },

    "475080": {
        "name": "KODEX AI전력핵심설비",
        "ticker": "475080.KS",
        "themes": ["전력 인프라"]
    },

    "487240": {
        "name": "KODEX AI전력핵심설비",
        "ticker": "487240.KS",
        "themes": ["전력 인프라"]
    },

    "434060": {
        "name": "TIGER 원자력ETF",
        "ticker": "434060.KS",
        "themes": ["원자력"]
    },

    "483320": {
        "name": "ACE 원자력테마딥서치",
        "ticker": "483320.KS",
        "themes": ["원자력"]
    },

    "475300": {
        "name": "SOL AI전력인프라",
        "ticker": "475300.KS",
        "themes": [
            "전력 인프라",
            "데이터센터·AI 인프라"
        ]
    },

    "457990": {
        "name": "TIGER 글로벌AI&로봇",
        "ticker": "457990.KS",
        "themes": ["AI"]
    },
}


DEFAULT_WATCHLIST = [
    "396500",
    "091160",
    "395160",
    "475080",
    "434060"
]


# ============================================================
# FUTURE THEMES
# ============================================================

FUTURE_CHAIN = [

    {
        "theme": "AI 반도체",
        "stage": "현재 주도",
        "desc": "AI 연산 수요 확대의 직접 수혜",
        "keywords": [
            "AI",
            "반도체",
            "HBM",
            "핵심장비"
        ],
        "seeds": [
            "396500",
            "395160",
            "091160"
        ]
    },

    {
        "theme": "데이터센터·AI 인프라",
        "stage": "다음 수혜",
        "desc": "AI 데이터센터 증설에 따른 인프라 투자",
        "keywords": [
            "데이터센터",
            "AI인프라",
            "인프라",
            "서버"
        ],
        "seeds": [
            "475300"
        ]
    },

    {
        "theme": "전력 인프라",
        "stage": "다음 수혜",
        "desc": "AI 전력수요 증가에 따른 핵심 전력설비",
        "keywords": [
            "전력",
            "변압기",
            "전력설비",
            "전력인프라"
        ],
        "seeds": [
            "475080",
            "487240",
            "475300"
        ]
    },

    {
        "theme": "원자력",
        "stage": "관심 확대",
        "desc": "전력수요와 에너지 안보에 따른 원전 투자",
        "keywords": [
            "원자력",
            "원전",
            "SMR"
        ],
        "seeds": [
            "434060",
            "483320"
        ]
    },

    {
        "theme": "냉각·열관리",
        "stage": "초기 관심",
        "desc": "고집적 AI 서버의 열관리 수요",
        "keywords": [
            "냉각",
            "열관리",
            "액침",
            "데이터센터"
        ],
        "seeds": []
    },
]


# ============================================================
# JSON
# ============================================================

def read_json(path, default):

    try:

        if not os.path.exists(path):
            return default

        with open(
            path,
            "r",
            encoding="utf-8-sig"
        ) as f:

            return json.load(f)

    except Exception:

        return default


def write_json(path, obj):

    try:

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                obj,
                f,
                ensure_ascii=False,
                indent=2
            )

        return True

    except Exception:

        return False


# ============================================================
# CODE
# ============================================================

def normalize_code(value):

    s = str(value).strip()

    digits = "".join(
        ch
        for ch in s
        if ch.isdigit()
    )

    if digits:
        return digits[-6:].zfill(6)

    return s


# ============================================================
# UNIVERSE
# ============================================================

def normalize_universe(data):

    result = {}

    if not isinstance(data, dict):
        return result

    for code, item in data.items():

        if not isinstance(item, dict):
            continue

        code = normalize_code(code)

        themes = item.get(
            "themes",
            []
        )

        if not isinstance(themes, list):
            themes = []

        result[code] = {

            "name": str(
                item.get(
                    "name",
                    code
                )
            ),

            "ticker": str(
                item.get(
                    "ticker",
                    f"{code}.KS"
                )
            ),

            "themes": themes
        }

    return result


def load_universe():

    result = dict(
        BASE_ETFS
    )

    cached = normalize_universe(
        read_json(
            UNIVERSE_FILE,
            {}
        )
    )

    result.update(
        cached
    )

    return normalize_universe(
        result
    )


# ============================================================
# SESSION
# ============================================================

watchlist = read_json(
    WATCHLIST_FILE,
    DEFAULT_WATCHLIST
)

holdings = read_json(
    HOLDINGS_FILE,
    {}
)


if not isinstance(
    watchlist,
    list
):

    watchlist = list(
        DEFAULT_WATCHLIST
    )


watchlist = [
    normalize_code(x)
    for x in watchlist
]


if not isinstance(
    holdings,
    dict
):

    holdings = {}


if "watchlist" not in st.session_state:

    st.session_state.watchlist = watchlist


if "holdings" not in st.session_state:

    st.session_state.holdings = holdings


if "main_page" not in st.session_state:

    st.session_state.main_page = "📊 내 ETF"


if "theme_detail_code" not in st.session_state:

    st.session_state.theme_detail_code = None


if "theme_detail_name" not in st.session_state:

    st.session_state.theme_detail_name = None


if "finder_code" not in st.session_state:

    st.session_state.finder_code = None


if "universe" not in st.session_state:

    st.session_state.universe = load_universe()


universe = st.session_state.universe


# ============================================================
# CSS
# ============================================================

st.markdown(
    r"""
<style>

:root {
    --bg:#111417;
    --panel:#1a1e22;
    --line:#353b40;
    --text:#f4f5f2;
    --sub:#d8ddd8;
    --muted:#c1c8c1;
}


html,
body,
[class*="stApp"] {
    background:var(--bg)!important;
    color:var(--text)!important;
}


.block-container {
    max-width:1200px;
    padding-top:1rem;
    padding-bottom:3rem;
}


* {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Noto Sans KR",
        "Malgun Gothic",
        "Apple SD Gothic Neo",
        sans-serif!important;
}


.stMarkdown,
p,
label,
span,
div {
    color:var(--text);
}


[data-testid="stCaptionContainer"] p {
    color:var(--muted)!important;
}


hr {
    border-color:var(--line)!important;
}


/* METRIC */

[data-testid="stMetric"] {
    background:var(--panel);
    border:1px solid var(--line);
    border-radius:12px;
    padding:10px 12px;
}


[data-testid="stMetricLabel"] {
    color:var(--sub)!important;
    font-size:.78rem!important;
}


[data-testid="stMetricValue"] {
    color:var(--text)!important;
    font-size:1.15rem!important;
    line-height:1.15!important;
}


/* BUTTON */

.stButton>button {
    width:100%;
    border-radius:10px;
    border:1px solid #4b5359;
    background:#242a2f;
    color:#f5f5f2;
    min-height:38px;
}


.stButton>button:hover {
    border-color:#7f8a92;
    background:#2a3137;
}


/* INPUT */

input,
textarea {
    color:#f5f5f2!important;
    background:#20252a!important;
    caret-color:#f5f5f2!important;
}


input::placeholder {
    color:#aeb6b0!important;
    opacity:1!important;
}


/* SELECTBOX */

[data-baseweb="select"] > div {
    background:#20252a!important;
    border-color:#4a5258!important;
    color:#f4f5f2!important;
}


[data-baseweb="select"] * {
    color:#f4f5f2!important;
}


[role="listbox"] {
    background:#20252a!important;
    border:1px solid #4a5258!important;
}


[role="option"] {
    background:#20252a!important;
    color:#f4f5f2!important;
}


[role="option"]:hover,
[aria-selected="true"] {
    background:#30373d!important;
    color:#ffffff!important;
}


/* RADIO */

[data-testid="stRadio"] label {
    color:var(--sub)!important;
}


/* LABEL */

.stTextInput label,
.stSelectbox label,
.stNumberInput label {
    color:var(--sub)!important;
}


/* APP */

.app-title {
    font-size:1.55rem;
    font-weight:800;
    letter-spacing:-.04em;
    margin-bottom:0;
}


.app-sub {
    color:var(--sub)!important;
    font-size:.86rem;
    margin-top:2px;
}


.section-title {
    font-size:1.08rem;
    font-weight:800;
    margin:1rem 0 .55rem;
}


/* CARD */

.card-title {
    font-size:1rem;
    font-weight:800;
    color:#fff!important;
}


.card-sub {
    color:var(--sub)!important;
    font-size:.78rem;
    line-height:1.45;
}


/* PRICE */

.price-main {
    font-size:1.55rem;
    font-weight:800;
    letter-spacing:-.03em;
}


/* JUDGMENT */

.judge-box {
    background:#191e22;
    border:1px solid #394147;
    border-radius:14px;
    padding:14px;
    margin:.35rem 0 .65rem;
}


.judge-label {
    color:var(--muted)!important;
    font-size:.76rem;
    margin-bottom:3px;
}


.judge-value {
    color:#fff!important;
    font-size:1.02rem;
    font-weight:800;
}


.reason-box {
    background:#20252a;
    border-radius:10px;
    padding:9px 11px;
    margin-top:6px;
}


.reason-title {
    color:#dce2dc!important;
    font-size:.75rem;
    font-weight:800;
    margin-bottom:2px;
}


.reason-text {
    color:#cbd2cc!important;
    font-size:.78rem;
    line-height:1.5;
}


/* PRICE SCENARIO */

.price-box {
    background:#1b2024;
    border:1px solid #343b40;
    border-radius:12px;
    padding:11px 12px;
    height:100%;
}


.price-name {
    color:var(--sub)!important;
    font-size:.74rem;
    font-weight:700;
}


.price-value {
    color:#fff!important;
    font-size:1.02rem;
    font-weight:800;
    margin:2px 0;
}


.price-basis {
    color:#cbd2cc!important;
    font-size:.73rem;
    line-height:1.45;
}


.price-action {
    color:#e8ece8!important;
    font-size:.76rem;
    font-weight:700;
    margin-top:4px;
}


.theme-stage {
    display:inline-block;
    border:1px solid #4a535a;
    border-radius:999px;
    padding:3px 8px;
    font-size:.7rem;
    color:#dce2dc!important;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# HISTORY
# ============================================================

def get_history(
    code,
    period="1y"
):

    meta = universe.get(
        code,
        BASE_ETFS.get(
            code,
            {
                "ticker": f"{code}.KS"
            }
        )
    )

    ticker = meta.get(
        "ticker",
        f"{code}.KS"
    )

    try:

        df = yf.download(
            ticker,
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False
        )

        if (
            df is None
            or df.empty
        ):

            return pd.DataFrame()


        if isinstance(
            df.columns,
            pd.MultiIndex
        ):

            df.columns = [
                c[0]
                for c in df.columns
            ]


        columns = {
            str(c).lower(): c
            for c in df.columns
        }


        close_col = columns.get(
            "close"
        )

        volume_col = columns.get(
            "volume"
        )


        if close_col is None:

            return pd.DataFrame()


        result = pd.DataFrame(
            index=df.index
        )


        result["Close"] = pd.to_numeric(
            df[close_col],
            errors="coerce"
        )


        if volume_col:

            result["Volume"] = pd.to_numeric(
                df[volume_col],
                errors="coerce"
            )

        else:

            result["Volume"] = 0


        return result.dropna(
            subset=["Close"]
        )

    except Exception:

        return pd.DataFrame()


# ============================================================
# INDICATORS
# ============================================================

def add_indicators(df):

    x = df.copy()

    close = x["Close"]


    x["MA20"] = (
        close
        .rolling(20)
        .mean()
    )


    x["MA60"] = (
        close
        .rolling(60)
        .mean()
    )


    delta = close.diff()


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
        gain /
        loss.replace(
            0,
            np.nan
        )
    )


    x["RSI14"] = (
        100 -
        (
            100 /
            (1 + rs)
        )
    )


    x["VOL20"] = (
        x["Volume"]
        .rolling(20)
        .mean()
    )


    x["VOL_RATIO"] = (
        x["Volume"] /
        x["VOL20"].replace(
            0,
            np.nan
        )
    )


    x["RET20"] = (
        close
        .pct_change(20)
        * 100
    )


    x["HIGH20"] = (
        close
        .rolling(20)
        .max()
    )


    x["LOW20"] = (
        close
        .rolling(20)
        .min()
    )


    x["LOW60"] = (
        close
        .rolling(60)
        .min()
    )


    return x.dropna(
        subset=["Close"]
    )


# ============================================================
# ANALYSIS
# ============================================================

def analyze(code):

    df = add_indicators(
        get_history(code)
    )


    name = universe.get(
        code,
        {}
    ).get(
        "name",
        code
    )


    if df.empty:

        return {

            "code": code,
            "name": name,
            "df": df,

            "close": None,
            "change": None,

            "ma20": None,
            "ma60": None,

            "rsi": None,
            "vr": None,
            "ret20": None,

            "high20": None,
            "low20": None,
            "low60": None,

            "judgment":
                "데이터 확인 필요",

            "action":
                "현재는 신규 매수를 서두르지 않고 데이터 확인",

            "reason":
                "차트 데이터가 충분하지 않아 추세와 지지·저항을 안정적으로 계산하기 어렵습니다.",

            "action_reason":
                "데이터가 복구되면 동일 기준으로 다시 판단합니다.",

            "first": None,
            "support": None,
            "breakout": None,
            "danger": None,

            "first_basis":
                "데이터 부족",

            "support_basis":
                "데이터 부족",

            "breakout_basis":
                "데이터 부족",

            "danger_basis":
                "데이터 부족",

            "first_action":
                "관망",

            "support_action":
                "반등 확인 후 검토",

            "breakout_action":
                "돌파 안착 확인",

            "danger_action":
                "비중 점검"
        }


    last = df.iloc[-1]


    close = float(
        last["Close"]
    )


    prev = (
        float(
            df["Close"].iloc[-2]
        )
        if len(df) >= 2
        else close
    )


    change = close - prev


    ma20 = (
        float(last["MA20"])
        if pd.notna(last["MA20"])
        else None
    )


    ma60 = (
        float(last["MA60"])
        if pd.notna(last["MA60"])
        else None
    )


    rsi = (
        float(last["RSI14"])
        if pd.notna(last["RSI14"])
        else None
    )


    vr = (
        float(last["VOL_RATIO"])
        if pd.notna(last["VOL_RATIO"])
        else None
    )


    ret20 = (
        float(last["RET20"])
        if pd.notna(last["RET20"])
        else None
    )


    high20 = (
        float(last["HIGH20"])
        if pd.notna(last["HIGH20"])
        else None
    )


    low20 = (
        float(last["LOW20"])
        if pd.notna(last["LOW20"])
        else None
    )


    low60 = (
        float(last["LOW60"])
        if pd.notna(last["LOW60"])
        else None
    )


    trend_up = (
        ma20 is not None
        and ma60 is not None
        and close >= ma20
        and close >= ma60
        and ma20 >= ma60
    )


    trend_down = (
        ma20 is not None
        and ma60 is not None
        and close < ma20
        and close < ma60
    )


    # ========================================================
    # CURRENT JUDGMENT
    # ========================================================

    if (
        trend_up
        and rsi is not None
        and rsi >= 70
    ):

        judgment = (
            "상승추세지만 단기 과열 구간"
        )

        action = (
            "추격매수보다 눌림을 기다리는 대응"
        )

        reason = (
            f"현재가가 MA20·MA60 위에 있고 "
            f"이동평균 배열도 상승형이지만 "
            f"RSI14가 {rsi:.1f}로 높아 "
            "단기 추격 부담이 있습니다."
        )

        action_reason = (
            "상승추세는 유지하되 고점 추격보다 "
            "MA20 또는 1차 지지 확인을 우선합니다."
        )


    elif trend_up:

        judgment = (
            "상승추세 유지"
        )

        action = (
            "보유 우선, 눌림 시 분할매수 검토"
        )

        reason = (
            f"현재가가 MA20·MA60 위에 있고 "
            f"20일 수익률은 {ret20:+.1f}%입니다. "
            "추세 훼손 신호가 아직 뚜렷하지 않습니다."
        )

        action_reason = (
            "추세가 살아 있는 동안 전량 추격보다 "
            "핵심 지지에서 거래량과 반등을 확인합니다."
        )


    elif (
        ma20 is not None
        and close >= ma20
    ):

        judgment = (
            "단기 반등·추세 확인 구간"
        )

        action = (
            "돌파 안착 여부 확인 후 대응"
        )

        reason = (
            "단기 이동평균은 회복했지만 "
            "중기 MA60 위에 안정적으로 올라선 "
            "상태가 아니어서 추세 전환 확인이 필요합니다."
        )

        action_reason = (
            "MA60 돌파와 거래량 증가가 함께 확인되기 "
            "전에는 확인 매매를 우선합니다."
        )


    elif trend_down:

        judgment = (
            "하락추세 또는 약세 구간"
        )

        action = (
            "신규매수보다 지지 확인 우선"
        )

        reason = (
            f"현재가가 MA20·MA60 아래에 있어 "
            f"중단기 추세가 약합니다. "
            f"20일 수익률은 {ret20:+.1f}%입니다."
        )

        action_reason = (
            "하락 중간에서 평균단가를 낮추기보다 "
            "최근 저점 지지와 MA20 회복을 확인합니다."
        )


    else:

        judgment = (
            "방향 탐색 구간"
        )

        action = (
            "관망 후 돌파·지지 확인"
        )

        reason = (
            "단기와 중기 추세가 엇갈려 "
            "방향성이 명확하지 않습니다."
        )

        action_reason = (
            "지지 이탈 또는 돌파 안착 중 "
            "어느 쪽이 먼저 확인되는지 보고 대응합니다."
        )


    # ========================================================
    # KEY PRICE
    # ========================================================

    first = (
        ma20
        if ma20
        else close * 0.97
    )


    support_candidates = [
        x
        for x in [
            low20,
            low60,
            ma20 * 0.98
            if ma20
            else None
        ]
        if x is not None
    ]


    support = (
        max(support_candidates)
        if support_candidates
        else close * 0.95
    )


    breakout = (
        high20 * 1.005
        if high20
        else close * 1.03
    )


    danger_candidates = [
        x
        for x in [
            low20 * 0.98
            if low20
            else None,

            ma60 * 0.97
            if ma60
            else None
        ]
        if x is not None
    ]


    danger = (
        min(danger_candidates)
        if danger_candidates
        else close * 0.92
    )


    return {

        "code": code,
        "name": name,
        "df": df,

        "close": close,
        "change": change,

        "ma20": ma20,
        "ma60": ma60,

        "rsi": rsi,
        "vr": vr,
        "ret20": ret20,

        "high20": high20,
        "low20": low20,
        "low60": low60,

        "judgment": judgment,
        "action": action,

        "reason": reason,
        "action_reason": action_reason,

        "first": first,
        "support": support,
        "breakout": breakout,
        "danger": danger,

        "first_basis":
            "MA20 인근의 1차 눌림 확인 구간",

        "support_basis":
            "최근 20일 저점과 이동평균을 함께 반영한 핵심 방어 구간",

        "breakout_basis":
            "최근 20일 고점 상향 돌파 후 안착 여부를 보는 기준",

        "danger_basis":
            "최근 저점 또는 MA60을 명확히 이탈할 경우 추세 훼손 가능성",

        "first_action":
            "눌림 후 반등 시 1차 매수 검토",

        "support_action":
            "지지 확인 시 분할매수·보유 대응",

        "breakout_action":
            "거래량 증가와 함께 안착하면 추가 대응 검토",

        "danger_action":
            "신규매수 중단, 보유비중 및 손실관리 점검"
    }


# ============================================================
# GET ANALYSIS
# ============================================================

@st.cache_data(
    ttl=120,
    show_spinner=False
)
def get_analysis(code):

    return analyze(code)


# ============================================================
# FORMAT
# ============================================================

def fmt_price(value):

    if value is None or pd.isna(value):
        return "-"

    return (
        f"{int(round(float(value))):,}원"
    )


def fmt_pct(value):

    if value is None or pd.isna(value):
        return "-"

    return (
        f"{float(value):+.1f}%"
    )


def fmt_ratio(value):

    if value is None or pd.isna(value):
        return "-"

    return (
        f"{float(value):.2f}배"
    )


# ============================================================
# METRICS
# ============================================================

def render_metrics(a):

    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "RSI14",
            "-"
            if a["rsi"] is None
            else f'{a["rsi"]:.1f}'
        )


    with c2:

        st.metric(
            "거래량",
            fmt_ratio(
                a["vr"]
            )
        )


    with c3:

        st.metric(
            "20일 수익률",
            fmt_pct(
                a["ret20"]
            )
        )


    with c4:

        st.metric(
            "MA20 / MA60",
            f'{fmt_price(a["ma20"])} / '
            f'{fmt_price(a["ma60"])}'
        )


# ============================================================
# CURRENT JUDGMENT
# ============================================================

def render_judgment(a):

    st.markdown(
        '<div class="section-title">'
        '현재판단 · 지금대응'
        '</div>',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="judge-box">',
        unsafe_allow_html=True
    )


    c1, c2 = st.columns(2)


    with c1:

        st.markdown(
            '<div class="judge-label">'
            '현재판단'
            '</div>',
            unsafe_allow_html=True
        )


        st.markdown(
            f'<div class="judge-value">'
            f'{a["judgment"]}'
            f'</div>',
            unsafe_allow_html=True
        )


        st.markdown(
            f'''
            <div class="reason-box">

                <div class="reason-title">
                    판단근거
                </div>

                <div class="reason-text">
                    {a["reason"]}
                </div>

            </div>
            ''',
            unsafe_allow_html=True
        )


    with c2:

        st.markdown(
            '<div class="judge-label">'
            '지금대응'
            '</div>',
            unsafe_allow_html=True
        )


        st.markdown(
            f'<div class="judge-value">'
            f'{a["action"]}'
            f'</div>',
            unsafe_allow_html=True
        )


        st.markdown(
            f'''
            <div class="reason-box">

                <div class="reason-title">
                    대응근거
                </div>

                <div class="reason-text">
                    {a["action_reason"]}
                </div>

            </div>
            ''',
            unsafe_allow_html=True
        )


    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# KEY PRICE / SCENARIO
# ============================================================

def render_price_scenarios(a):

    st.markdown(
        '<div class="section-title">'
        '핵심가격 · 대응 시나리오'
        '</div>',
        unsafe_allow_html=True
    )


    items = [

        (
            "1차 관심가격",
            a["first"],
            a["first_basis"],
            a["first_action"]
        ),

        (
            "핵심 지지",
            a["support"],
            a["support_basis"],
            a["support_action"]
        ),

        (
            "돌파 기준",
            a["breakout"],
            a["breakout_basis"],
            a["breakout_action"]
        ),

        (
            "위험 가격",
            a["danger"],
            a["danger_basis"],
            a["danger_action"]
        )
    ]


    cols = st.columns(4)


    for col, item in zip(
        cols,
        items
    ):

        name, value, basis, action = item


        with col:

            st.markdown(
                f'''
                <div class="price-box">

                    <div class="price-name">
                        {name}
                    </div>

                    <div class="price-value">
                        {fmt_price(value)}
                    </div>

                    <div class="price-basis">
                        {basis}
                    </div>

                    <div class="price-action">
                        → {action}
                    </div>

                </div>
                ''',
                unsafe_allow_html=True
            )


# ============================================================
# CHART
# ============================================================

def render_chart(a):

    df = (
        a["df"]
        .tail(130)
        .copy()
    )


    if df.empty:

        st.info(
            "차트 데이터를 불러오지 못했습니다."
        )

        return


    fig = go.Figure()


    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            name="가격",
            mode="lines",
            line=dict(
                width=2
            )
        )
    )


    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MA20"],
            name="MA20",
            mode="lines",
            line=dict(
                width=1.4
            )
        )
    )


    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MA60"],
            name="MA60",
            mode="lines",
            line=dict(
                width=1.2
            )
        )
    )


    fig.update_layout(
        height=360,
        margin=dict(
            l=8,
            r=8,
            t=10,
            b=8
        ),
        paper_bgcolor="#111417",
        plot_bgcolor="#111417",
        font=dict(
            color="#e8ece8"
        ),
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            y=1.02,
            x=0
        ),
        hovermode="x unified"
    )


    fig.update_xaxes(
        showgrid=False
    )


    fig.update_yaxes(
        showgrid=True,
        gridcolor="#30363b"
    )


    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# ============================================================
# WATCHLIST
# ============================================================

def add_watch(code):

    code = normalize_code(code)


    if code not in st.session_state.watchlist:

        st.session_state.watchlist.append(
            code
        )


        write_json(
            WATCHLIST_FILE,
            st.session_state.watchlist
        )


def remove_watch(code):

    st.session_state.watchlist = [
        x
        for x in st.session_state.watchlist
        if x != code
    ]


    write_json(
        WATCHLIST_FILE,
        st.session_state.watchlist
    )


# ============================================================
# ETF FINDER
# ============================================================

def render_finder():

    st.markdown(
        '<div class="section-title">'
        'ETF 찾기'
        '</div>',
        unsafe_allow_html=True
    )


    query = st.text_input(
        "ETF 이름 또는 코드",
        placeholder="예: 반도체 / 전력 / 396500",
        label_visibility="collapsed"
    )


    text = (
        query or ""
    ).strip().lower()


    matches = []


    for code, item in universe.items():

        hay = (
            f'{code} '
            f'{item.get("name", "")} '
            f'{" ".join(item.get("themes", []))}'
        ).lower()


        if (
            not text
            or text in hay
        ):

            matches.append(
                code
            )


    matches = sorted(
        matches,
        key=lambda c: (
            universe[c].get(
                "name",
                ""
            ),
            c
        )
    )[:80]


    if not matches:

        st.warning(
            "검색 결과가 없습니다. "
            "ETF명 또는 종목코드를 다시 입력해 주세요."
        )

        return None


    options = {

        f'{universe[c]["name"]} · {c}':
            c

        for c in matches
    }


    labels = list(
        options.keys()
    )


    default_index = next(
        (
            i
            for i, label
            in enumerate(labels)
            if options[label]
            == st.session_state.finder_code
        ),
        0
    )


    selected_label = st.selectbox(
        "검색 결과",
        labels,
        index=default_index,
        key="finder_select"
    )


    selected = options[
        selected_label
    ]


    st.session_state.finder_code = selected


    c1, c2 = st.columns(2)


    with c1:

        if st.button(
            "ETF 분석",
            key="finder_analyze",
            use_container_width=True
        ):

            st.session_state.main_page = (
                "📊 내 ETF"
            )

            st.rerun()


    with c2:

        if (
            selected
            in st.session_state.watchlist
        ):

            if st.button(
                "관심종목에서 삭제",
                key="finder_remove",
                use_container_width=True
            ):

                remove_watch(
                    selected
                )

                st.rerun()

        else:

            if st.button(
                "관심종목에 추가",
                key="finder_add",
                use_container_width=True
            ):

                add_watch(
                    selected
                )

                st.rerun()


    return selected


# ============================================================
# WATCHLIST UI
# ============================================================

def render_watchlist(selected):

    items = [

        code
        for code in st.session_state.watchlist
        if code in universe
    ]


    if not items:

        st.info(
            "관심종목이 없습니다. "
            "ETF 찾기에서 관심종목에 추가해 주세요."
        )

        return selected


    labels = [

        f'{universe[code]["name"]} · {code}'

        for code in items
    ]


    current = (
        selected
        if selected in items
        else items[0]
    )


    index = items.index(
        current
    )


    selected_label = st.selectbox(
        "관심종목",
        labels,
        index=index,
        key="watch_select"
    )


    code = items[
        labels.index(
            selected_label
        )
    ]


    c1, c2 = st.columns(
        [1, 1]
    )


    with c1:

        st.caption(
            f"관심종목 {len(items)}개"
        )


    with c2:

        if st.button(
            "현재 ETF 삭제",
            key="watch_delete"
        ):

            remove_watch(
                code
            )

            st.rerun()


    return code


# ============================================================
# HOLDINGS
# ============================================================

def render_holding(
    code,
    a
):

    st.markdown(
        '<div class="section-title">'
        '보유현황'
        '</div>',
        unsafe_allow_html=True
    )


    holding = (
        st.session_state.holdings.get(
            code,
            {}
        )
    )


    if not isinstance(
        holding,
        dict
    ):

        holding = {}


    owned = (
        code
        in st.session_state.holdings
    )


    status = st.radio(
        "보유 상태",
        [
            "미보유",
            "보유중"
        ],
        index=1 if owned else 0,
        horizontal=True,
        key=f"hold_status_{code}"
    )


    if status == "보유중":

        c1, c2, c3 = st.columns(3)


        with c1:

            qty = st.number_input(
                "보유수량",
                min_value=0.0,
                value=float(
                    holding.get(
                        "qty",
                        0
                    ) or 0
                ),
                step=1.0,
                key=f"qty_{code}"
            )


        with c2:

            avg = st.number_input(
                "평균매입가",
                min_value=0.0,
                value=float(
                    holding.get(
                        "avg",
                        0
                    ) or 0
                ),
                step=100.0,
                key=f"avg_{code}"
            )


        with c3:

            if st.button(
                "보유정보 저장",
                key=f"save_hold_{code}"
            ):

                st.session_state.holdings[
                    code
                ] = {
                    "qty": qty,
                    "avg": avg
                }


                write_json(
                    HOLDINGS_FILE,
                    st.session_state.holdings
                )


                st.success(
                    "보유정보가 저장되었습니다."
                )


        if (
            holding.get("avg")
            and a.get("close")
        ):

            pnl = (
                a["close"]
                / float(
                    holding["avg"]
                )
                - 1
            ) * 100


            st.caption(
                f"현재가 기준 수익률: "
                f"{pnl:+.1f}%"
            )


    elif owned:

        if st.button(
            "기존 보유정보 삭제",
            key=f"delete_hold_{code}"
        ):

            st.session_state.holdings.pop(
                code,
                None
            )


            write_json(
                HOLDINGS_FILE,
                st.session_state.holdings
            )


            st.rerun()


# ============================================================
# MY ETF
# ============================================================

def render_my_etf():

    st.markdown(
        '<div class="app-title">'
        '📊 내 ETF'
        '</div>',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="app-sub">'
        '보유종목·관심종목을 기준으로 '
        '현재상태와 대응가격을 한 화면에서 확인합니다.'
        '</div>',
        unsafe_allow_html=True
    )


    finder = render_finder()


    if finder:

        selected = finder

    elif st.session_state.watchlist:

        selected = (
            st.session_state.watchlist[0]
        )

    else:

        selected = next(
            iter(universe)
        )


    selected = render_watchlist(
        selected
    )


    if selected not in universe:

        st.warning(
            "선택한 ETF 정보를 찾을 수 없습니다."
        )

        return


    a = get_analysis(
        selected
    )


    st.markdown(
        f'''
        <div class="section-title">
            {a["name"]} · {selected}
        </div>
        ''',
        unsafe_allow_html=True
    )


    c1, c2, c3 = st.columns(
        [1.5, 1, 1]
    )


    with c1:

        st.markdown(
            f'''
            <div class="price-main">
                {fmt_price(a["close"])}
            </div>
            ''',
            unsafe_allow_html=True
        )


    with c2:

        st.metric(
            "전일 대비",
            fmt_price(
                a["change"]
            )
        )


    with c3:

        themes = universe.get(
            selected,
            {}
        ).get(
            "themes",
            []
        )


        st.caption(
            " · ".join(themes)
            if themes
            else "ETF"
        )


    # 보조지표

    render_metrics(
        a
    )


    # 중요:
    # 판단 → 근거 → 대응 → 근거

    render_judgment(
        a
    )


    # 핵심가격 → 대응

    render_price_scenarios(
        a
    )


    # 보유현황

    render_holding(
        selected,
        a
    )


    st.markdown(
        '<div class="section-title">'
        '가격 차트'
        '</div>',
        unsafe_allow_html=True
    )


    render_chart(
        a
    )


# ============================================================
# FUTURE THEME ROWS
# ============================================================

def theme_rows(
    info
):

    key = (
        f'theme_rows_'
        f'{info["theme"]}'
    )


    if key in st.session_state:

        return st.session_state[key]


    found = []


    # 먼저 지정 ETF

    for code in info.get(
        "seeds",
        []
    ):

        if (
            code in universe
            and code not in found
        ):

            found.append(
                code
            )


    # 이후 키워드 검색

    keywords = [
        k.lower()
        for k
        in info.get(
            "keywords",
            []
        )
    ]


    for code, item in universe.items():

        if code in found:

            continue


        hay = (
            f'{item.get("name", "")} '
            f'{" ".join(item.get("themes", []))}'
        ).lower()


        if any(
            keyword in hay
            for keyword in keywords
        ):

            found.append(
                code
            )


    rows = []


    for code in found[:6]:

        try:

            rows.append(
                get_analysis(
                    code
                )
            )

        except Exception:

            pass


    st.session_state[key] = rows


    return rows


# ============================================================
# FUTURE THEME CARD
# ============================================================

def render_theme_card(
    info,
    rows
):

    st.markdown(
        f'''
        <div class="section-title">

            {info["theme"]}

            <span class="theme-stage">
                {info["stage"]}
            </span>

        </div>
        ''',
        unsafe_allow_html=True
    )


    st.caption(
        info["desc"]
    )


    if not rows:

        st.info(
            "현재 연결된 ETF 데이터가 없습니다."
        )

        return


    for a in rows[:4]:

        with st.container(
            border=True
        ):

            c1, c2, c3, c4 = st.columns(
                [2.2, 1, 1, 1.2]
            )


            with c1:

                st.markdown(
                    f'''
                    <div class="card-title">
                        {a["name"]}
                    </div>

                    <div class="card-sub">
                        {a["code"]} ·
                        {fmt_price(a["close"])}
                    </div>
                    ''',
                    unsafe_allow_html=True
                )


            with c2:

                st.metric(
                    "RSI",
                    "-"
                    if a["rsi"] is None
                    else f'{a["rsi"]:.1f}'
                )


            with c3:

                st.metric(
                    "거래량",
                    fmt_ratio(
                        a["vr"]
                    )
                )


            with c4:

                st.metric(
                    "20일",
                    fmt_pct(
                        a["ret20"]
                    )
                )


            st.caption(
                f'현재판단: '
                f'{a["judgment"]}'
            )


            if st.button(
                "ETF 분석",
                key=(
                    f'theme_analyze_'
                    f'{info["theme"]}_'
                    f'{a["code"]}'
                ),
                use_container_width=True
            ):

                st.session_state.theme_detail_code = (
                    a["code"]
                )

                st.session_state.theme_detail_name = (
                    info["theme"]
                )

                st.rerun()


# ============================================================
# INLINE FUTURE ETF ANALYSIS
# ============================================================

def render_inline_etf(
    code,
    theme_name
):

    a = get_analysis(
        code
    )


    st.markdown(
        f'''
        <div class="section-title">
            {theme_name} · ETF 상세분석
        </div>
        ''',
        unsafe_allow_html=True
    )


    c1, c2 = st.columns(
        [3, 1]
    )


    with c1:

        st.markdown(
            f'''
            <div class="card-title">
                {a["name"]} · {code}
            </div>
            ''',
            unsafe_allow_html=True
        )


    with c2:

        if st.button(
            "분석 닫기",
            key="close_theme_detail",
            use_container_width=True
        ):

            st.session_state.theme_detail_code = None

            st.rerun()


    st.metric(
        "현재가",
        fmt_price(
            a["close"]
        )
    )


    render_metrics(
        a
    )


    render_judgment(
        a
    )


    render_price_scenarios(
        a
    )


    st.markdown(
        '<div class="section-title">'
        '가격 차트'
        '</div>',
        unsafe_allow_html=True
    )


    render_chart(
        a
    )


# ============================================================
# FUTURE THEMES
# ============================================================

def render_future_themes():

    st.markdown(
        '<div class="app-title">'
        '🚀 미래테마'
        '</div>',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="app-sub">'
        '현재 주도 → 다음 수혜 → 초기 관심 순서로 '
        'AI 관련 밸류체인을 확인합니다.'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # 시장 새로고침 버튼 제거
    # --------------------------------------------------------
    # ETF 목록은 BASE_ETFS + 기존 캐시를 사용합니다.
    # 가격/거래량/차트는 ETF 분석 시 최신 조회합니다.
    # --------------------------------------------------------


    for info in FUTURE_CHAIN:

        rows = theme_rows(
            info
        )


        render_theme_card(
            info,
            rows
        )


        if (
            st.session_state.theme_detail_code
            and
            st.session_state.theme_detail_code
            in [
                a["code"]
                for a in rows
            ]
        ):

            render_inline_etf(
                st.session_state.theme_detail_code,
                st.session_state.theme_detail_name
                or info["theme"]
            )


    # ========================================================
    # THEME SUMMARY
    # ========================================================

    summary = []


    for info in FUTURE_CHAIN:

        rows = theme_rows(
            info
        )


        if rows:

            r = rows[0]


            summary.append(
                {
                    "테마":
                        info["theme"],

                    "단계":
                        info["stage"],

                    "대표 ETF":
                        r["name"],

                    "현재판단":
                        r["judgment"],

                    "20일":
                        fmt_pct(
                            r["ret20"]
                        ),

                    "RSI":
                        "-"
                        if r["rsi"] is None
                        else round(
                            r["rsi"],
                            1
                        )
                }
            )

        else:

            summary.append(
                {
                    "테마":
                        info["theme"],

                    "단계":
                        info["stage"],

                    "대표 ETF":
                        "-",

                    "현재판단":
                        "데이터 없음",

                    "20일":
                        "-",

                    "RSI":
                        "-"
                }
            )


    st.markdown(
        '<div class="section-title">'
        '테마 요약'
        '</div>',
        unsafe_allow_html=True
    )


    st.dataframe(
        pd.DataFrame(
            summary
        ),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# APP HEADER
# ============================================================

st.markdown(
    '<div class="app-title">'
    'ETF RADAR'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="app-sub">'
    'ETF 기술지표 · 현재판단 · 핵심가격 · 대응 시나리오'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# NAVIGATION
# ============================================================

pages = [
    "📊 내 ETF",
    "🚀 미래테마"
]


current = (
    st.session_state.main_page
    if st.session_state.main_page
    in pages
    else pages[0]
)


page = st.radio(
    "화면",
    pages,
    index=pages.index(
        current
    ),
    horizontal=True,
    key="main_page_radio",
    label_visibility="collapsed"
)


st.session_state.main_page = page


# ============================================================
# PAGE
# ============================================================

if page == "📊 내 ETF":

    render_my_etf()

else:

    render_future_themes()