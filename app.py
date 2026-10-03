# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf


# ============================================================
# ETF RADAR v14
# 기존 v13 기능 유지 + UI/한글/차트 안정화
#
# 핵심 변경
# 1. 시장/ETF 목록 외부 새로고침 제거
# 2. JSON UTF-8-SIG 읽기
# 3. ETF 찾기 즉시 검색
# 4. 기존 다크 차트 유지
# 5. 최근 6개월 고정
# 6. 확대/축소/이동 제거
# 7. 현재판단 + 판단근거
# 8. 지금대응 + 대응근거
# 9. 핵심가격 + 대응 시나리오
# 10. 미래테마 ETF 분석을 현재 페이지 안에서 표시
# 11. 흰색 드롭다운/입력창 제거
# 12. 기존 기능 삭제 최소화
# ============================================================


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# FILES
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"
UNIVERSE_FILE = "etf_universe_cache.json"


# ============================================================
# ETF DATA
# ============================================================

BASE_ETFS = {
    "395160": "KODEX AI반도체핵심장비",
    "487240": "KODEX AI반도체",
    "471990": "KODEX AI반도체TOP2Plus",

    "133690": "TIGER 미국나스닥100",
    "360750": "TIGER 미국S&P500",
    "458730": "TIGER 글로벌AI&로봇",
    "381170": "TIGER 미국테크TOP10 INDXX",

    "396500": "TIGER 반도체",
    "091160": "KODEX 반도체",
    "091180": "KODEX 자동차",
    "139260": "TIGER 200 IT",
    "305720": "KODEX 2차전지산업",

    "364690": "KODEX 혁신기술테마액티브",
    "117700": "KODEX 건설",
    "140700": "KODEX 보험",
    "144600": "KODEX 은행",
    "102780": "KODEX 삼성그룹",
    "261220": "KODEX WTI원유선물(H)",

    "449170": "TIGER 글로벌AI인프라액티브",
    "434060": "TIGER 글로벌AI&반도체액티브",

    "464240": "KODEX AI전력핵심설비",
    "487130": "KODEX AI전력인프라",

    "475050": "ACE 글로벌반도체TOP4 Plus",
    "469150": "ACE AI반도체포커스",

    "130730": "KOSEF 원자력",
    "161510": "PLUS 고배당주",
}


DEFAULT_WATCHLIST = [
    "395160",
    "487240",
    "471990",
    "133690",
    "360750",
    "458730",
]


# ============================================================
# THEMES
# ============================================================

THEMES = {

    "AI 반도체": {
        "keywords": [
            "AI반도체",
            "반도체",
            "AI",
            "HBM",
            "반도체장비",
        ],
        "seeds": [
            "395160",
            "487240",
            "471990",
            "396500",
        ],
        "reason":
            "AI 연산 확대와 고대역폭 메모리, "
            "첨단 반도체 투자 증가의 직접적인 수혜 영역입니다.",
    },

    "데이터센터·AI 인프라": {
        "keywords": [
            "데이터센터",
            "AI인프라",
            "AI 인프라",
            "글로벌AI인프라",
        ],
        "seeds": [
            "449170",
            "434060",
            "381170",
        ],
        "reason":
            "AI 서비스 확산에 따라 서버·네트워크·"
            "데이터센터 투자가 확대되는 구간을 추적합니다.",
    },

    "전력 인프라": {
        "keywords": [
            "전력",
            "전력인프라",
            "전력핵심설비",
            "전력설비",
        ],
        "seeds": [
            "464240",
            "487130",
        ],
        "reason":
            "데이터센터와 산업용 전력수요 증가에 따른 "
            "전력망 및 핵심설비 투자를 추적합니다.",
    },

    "원자력": {
        "keywords": [
            "원자력",
            "원전",
            "원전산업",
        ],
        "seeds": [
            "130730",
            "161510",
        ],
        "reason":
            "전력수요 증가와 에너지 믹스 변화에 따라 "
            "원전 관련 산업 흐름을 추적합니다.",
    },

    "냉각·열관리": {
        "keywords": [
            "냉각",
            "열관리",
            "액침냉각",
            "AI냉각",
        ],
        "seeds": [
            "434060",
            "449170",
        ],
        "reason":
            "AI 서버 고집적화에 따라 냉각과 열관리의 "
            "중요성이 높아지는 후방 수혜 영역입니다.",
    },
}


FUTURE_CHAIN = [
    ("AI 반도체", "현재 주도"),
    ("데이터센터·AI 인프라", "다음 수혜"),
    ("전력 인프라", "다음 수혜"),
    ("원자력", "관심 확대"),
    ("냉각·열관리", "초기 관심"),
]


# ============================================================
# CSS
# ============================================================

st.markdown(
    r"""
<style>

/* ============================================================
   GLOBAL
   ============================================================ */

:root {
    --bg: #07111f;
    --panel: #0d1928;
    --panel2: #111f31;
    --panel3: #16263a;

    --text: #f4f7fb;
    --text2: #d6deea;
    --muted: #aebaca;

    --blue: #4da3ff;
    --cyan: #55d6ff;

    --green: #28d7a0;
    --red: #ff6577;
    --yellow: #ffc857;

    --border: #293d54;
}


html,
body,
[class*="css"] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        "Noto Sans KR",
        Arial,
        sans-serif;
}


.stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
}


.block-container {
    max-width: 1180px;
    padding-top: 0.65rem !important;
    padding-bottom: 2rem !important;
}


/* 기본 글자 */

p,
span,
div,
label {
    color: var(--text);
}


h1,
h2,
h3,
h4 {
    color: #ffffff !important;
}


/* Caption */

[data-testid="stCaptionContainer"] p,
.stCaption {
    color: var(--muted) !important;
    font-size: 0.80rem !important;
}


/* Divider */

hr {
    border-color: #1e3044 !important;
}


/* ============================================================
   BUTTON
   ============================================================ */

.stButton > button {

    background: #142235 !important;

    color: #f5f8fc !important;

    border:
        1px solid #31465e !important;

    border-radius: 8px !important;

    font-weight: 700 !important;

    min-height: 38px !important;
}


.stButton > button:hover {

    background: #1b3149 !important;

    border-color:
        #4da3ff !important;
}


.stButton > button[kind="primary"] {

    background: #1769aa !important;

    color: #ffffff !important;
}


/* ============================================================
   INPUT
   ============================================================ */

div[data-baseweb="input"] {

    background:
        #101d2d !important;

    border:
        1px solid #31465e !important;
}


div[data-baseweb="input"] input {

    color:
        #ffffff !important;

    -webkit-text-fill-color:
        #ffffff !important;
}


/* ============================================================
   SELECTBOX
   ============================================================ */

div[data-baseweb="select"] > div {

    background:
        #101d2d !important;

    border:
        1px solid #31465e !important;

    color:
        #ffffff !important;
}


div[data-baseweb="select"] span,
div[data-baseweb="select"] div {

    color:
        #ffffff !important;
}


/* 드롭다운 */

div[role="listbox"],
ul[role="listbox"],
li[role="option"] {

    background:
        #101d2d !important;

    color:
        #ffffff !important;
}


li[role="option"]:hover {

    background:
        #1b3149 !important;

    color:
        #ffffff !important;
}


/* ============================================================
   RADIO
   ============================================================ */

div[data-testid="stRadio"] label {

    color:
        #d6deea !important;
}


/* ============================================================
   DATAFRAME
   ============================================================ */

[data-testid="stDataFrame"] {

    background:
        #0d1928 !important;
}


[data-testid="stDataFrame"] * {

    color:
        #e8eef6 !important;
}


/* ============================================================
   HEADER
   ============================================================ */

.app-header {

    padding:
        8px 0 12px;
}


.app-title {

    font-size:
        1.65rem;

    font-weight:
        900;

    letter-spacing:
        -0.04em;

    color:
        #ffffff;
}


.app-subtitle {

    margin-top:
        2px;

    color:
        var(--muted);

    font-size:
        0.78rem;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {

    background:
        linear-gradient(
            135deg,
            #152a43,
            #0b1929
        );

    border:
        1px solid #294057;

    border-radius:
        14px;

    padding:
        18px;

    margin-bottom:
        12px;
}


.hero-name {

    font-size:
        1.38rem;

    font-weight:
        900;
}


.hero-code {

    color:
        #aebdd0;

    font-size:
        0.78rem;

    margin-top:
        3px;
}


.quote-row {

    display:
        flex;

    align-items:
        baseline;

    gap:
        12px;

    margin-top:
        15px;
}


.quote-price {

    font-size:
        2.15rem;

    line-height:
        1;

    font-weight:
        900;
}


.quote-change {

    font-size:
        1rem;

    font-weight:
        800;
}


.positive {
    color:
        var(--green) !important;
}


.negative {
    color:
        var(--red) !important;
}


.neutral {
    color:
        var(--text2) !important;
}


.hero-date {

    margin-top:
        8px;

    color:
        var(--muted);

    font-size:
        0.76rem;
}


/* ============================================================
   SECTION
   ============================================================ */

.section-title {

    font-size:
        1.08rem;

    font-weight:
        900;

    color:
        #ffffff;

    margin:
        18px 0 8px;

    letter-spacing:
        -0.03em;
}


/* ============================================================
   EVIDENCE
   ============================================================ */

.evidence-grid {

    display:
        grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap:
        8px;

    margin:
        8px 0 12px;
}


.evidence-box {

    background:
        #0e1b2b;

    border:
        1px solid #263b52;

    border-radius:
        9px;

    padding:
        10px 11px;
}


.evidence-label {

    font-size:
        0.72rem;

    color:
        #aebaca;

    margin-bottom:
        4px;
}


.evidence-value {

    font-size:
        0.98rem;

    font-weight:
        900;

    color:
        #f4f7fb;
}


.evidence-sub {

    margin-top:
        3px;

    font-size:
        0.73rem;

    color:
        #aab7c7;
}


/* ============================================================
   JUDGMENT
   ============================================================ */

.judgment-box {

    background:
        #0d1928;

    border:
        1px solid #294057;

    border-left:
        4px solid var(--blue);

    border-radius:
        10px;

    padding:
        14px 15px;
}


.judgment-title {

    font-size:
        0.75rem;

    color:
        var(--muted);
}


.judgment-main {

    margin-top:
        4px;

    font-size:
        1.18rem;

    font-weight:
        900;

    color:
        #ffffff;
}


.judgment-reason {

    margin-top:
        9px;

    color:
        #d3ddea;

    font-size:
        0.84rem;

    line-height:
        1.55;
}


.action-box {

    background:
        #102033;

    border:
        1px solid #31506e;

    border-radius:
        10px;

    padding:
        14px 15px;
}


.action-title {

    color:
        #75c8ff;

    font-size:
        0.75rem;

    font-weight:
        800;
}


.action-main {

    margin-top:
        5px;

    color:
        #ffffff;

    font-size:
        0.92rem;

    line-height:
        1.55;

    font-weight:
        700;
}


/* ============================================================
   PRICE SCENARIO
   ============================================================ */

.scenario-grid {

    display:
        grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap:
        8px;

    margin-top:
        7px;
}


.scenario-card {

    background:
        #0e1b2b;

    border:
        1px solid #263b52;

    border-radius:
        9px;

    padding:
        11px;
}


.scenario-label {

    color:
        #aebaca;

    font-size:
        0.70rem;
}


.scenario-price {

    color:
        #ffffff;

    font-size:
        1.12rem;

    font-weight:
        900;

    margin-top:
        4px;
}


.scenario-desc {

    color:
        #c4cfdd;

    font-size:
        0.73rem;

    line-height:
        1.4;

    margin-top:
        6px;
}


/* ============================================================
   HOLDING
   ============================================================ */

.holding-box {

    background:
        #0d1928;

    border:
        1px solid #263b52;

    border-radius:
        10px;

    padding:
        13px;
}


.holding-value {

    font-size:
        1rem;

    font-weight:
        900;
}


.holding-detail {

    margin-top:
        5px;

    color:
        #aebbc9;

    font-size:
        0.78rem;
}


/* ============================================================
   FUTURE THEME
   ============================================================ */

.theme-card {

    background:
        #0d1928;

    border:
        1px solid #293d54;

    border-radius:
        11px;

    padding:
        14px;

    margin-bottom:
        12px;
}


.theme-stage {

    color:
        #72c9ff;

    font-size:
        0.76rem;

    font-weight:
        800;

    margin-bottom:
        5px;
}


.theme-title {

    color:
        #ffffff;

    font-size:
        1.15rem;

    font-weight:
        900;
}


.theme-reason {

    color:
        #bac6d4;

    font-size:
        0.82rem;

    line-height:
        1.5;

    margin-top:
        5px;

    margin-bottom:
        11px;
}


.theme-etf-box {

    background:
        #111f31;

    border:
        1px solid #2a4058;

    border-radius:
        9px;

    padding:
        11px 12px;

    margin-bottom:
        8px;
}


.theme-etf-name {

    color:
        #ffffff;

    font-size:
        0.94rem;

    font-weight:
        900;

    line-height:
        1.3;
}


.theme-etf-code {

    color:
        #aebaca;

    font-size:
        0.72rem;

    margin-top:
        2px;
}


.theme-data-grid {

    display:
        grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap:
        5px;

    margin-top:
        9px;
}


.theme-data-item {

    background:
        #0b1726;

    border-radius:
        6px;

    padding:
        7px 6px;
}


.theme-data-label {

    color:
        #aebaca;

    font-size:
        0.68rem;
}


.theme-data-value {

    color:
        #f4f7fb;

    font-size:
        0.88rem;

    font-weight:
        900;

    margin-top:
        2px;
}


/* ============================================================
   INLINE FUTURE THEME ANALYSIS
   ============================================================ */

.inline-analysis {

    background:
        #0a1625;

    border:
        1px solid #31506e;

    border-radius:
        12px;

    padding:
        12px;

    margin:
        4px 0 14px;
}


.inline-title {

    font-size:
        0.92rem;

    font-weight:
        900;

    color:
        #ffffff;

    margin-bottom:
        8px;
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 700px) {

    .block-container {

        padding-left:
            10px !important;

        padding-right:
            10px !important;
    }

    .app-title {
        font-size:
            1.42rem;
    }

    .hero {
        padding:
            14px;
    }

    .hero-name {
        font-size:
            1.20rem;
    }

    .quote-price {
        font-size:
            1.90rem;
    }

    .evidence-grid {
        gap:
            6px;
    }

    .evidence-box {
        padding:
            9px 7px;
    }

    .evidence-value {
        font-size:
            0.86rem;
    }

    .evidence-sub {
        font-size:
            0.67rem;
    }

    .scenario-grid {
        grid-template-columns:
            repeat(2, 1fr);
    }

    .theme-data-grid {
        grid-template-columns:
            repeat(2, 1fr);
    }
}

</style>
""",
    unsafe_allow_html=True
)


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


def write_json(path, data):

    try:

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

        return True

    except Exception:

        return False


# ============================================================
# ETF UNIVERSE
# ============================================================

def load_etf_universe():

    universe = dict(
        BASE_ETFS
    )

    cached = read_json(
        UNIVERSE_FILE,
        {}
    )

    if isinstance(
        cached,
        dict
    ):

        for code, name in cached.items():

            if code and name:

                universe[
                    str(code).zfill(6)
                ] = str(name)

    elif isinstance(
        cached,
        list
    ):

        for item in cached:

            if (
                isinstance(item, dict)
                and item.get("code")
                and item.get("name")
            ):

                universe[
                    str(
                        item["code"]
                    ).zfill(6)
                ] = str(
                    item["name"]
                )

    return universe


# ============================================================
# SESSION
# ============================================================

def init_state():

    if "watchlist" not in st.session_state:

        saved = read_json(
            WATCHLIST_FILE,
            DEFAULT_WATCHLIST.copy()
        )

        if isinstance(
            saved,
            list
        ):

            st.session_state.watchlist = [
                str(x).zfill(6)
                for x in saved
            ]

        else:

            st.session_state.watchlist = (
                DEFAULT_WATCHLIST.copy()
            )

    if "holdings" not in st.session_state:

        holdings = read_json(
            HOLDINGS_FILE,
            {}
        )

        st.session_state.holdings = (
            holdings
            if isinstance(
                holdings,
                dict
            )
            else {}
        )

    if "etf_universe" not in st.session_state:

        st.session_state.etf_universe = (
            load_etf_universe()
        )

    if "price_cache" not in st.session_state:
        st.session_state.price_cache = {}

    if "theme_cache" not in st.session_state:
        st.session_state.theme_cache = {}

    if "selected_code" not in st.session_state:

        st.session_state.selected_code = (
            st.session_state.watchlist[0]
            if st.session_state.watchlist
            else next(iter(BASE_ETFS))
        )

    if "main_page" not in st.session_state:

        st.session_state.main_page = (
            "📊 내 ETF"
        )

    if "page_request" not in st.session_state:
        st.session_state.page_request = None

    if "theme_analysis" not in st.session_state:
        st.session_state.theme_analysis = None


# ============================================================
# ETF NAME
# ============================================================

def get_etf_name(code):

    code = str(code).zfill(6)

    return (
        st.session_state.etf_universe.get(
            code
        )
        or BASE_ETFS.get(
            code
        )
        or f"ETF {code}"
    )


# ============================================================
# PRICE DATA
# ============================================================

def normalize_df(df):

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    if isinstance(
        df.columns,
        pd.MultiIndex
    ):

        df.columns = [
            c[0]
            if isinstance(c, tuple)
            else str(c)
            for c in df.columns
        ]

    rename = {}

    for col in df.columns:

        key = str(
            col
        ).lower()

        if key in [
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]:

            rename[col] = key.title()

    df = df.rename(
        columns=rename
    )

    required = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    if any(
        col not in df.columns
        for col in required
    ):

        return pd.DataFrame()

    df = df[
        required
    ].copy()

    for col in required:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(
        subset=[
            "Close"
        ]
    )

    try:

        if getattr(
            df.index,
            "tz",
            None
        ) is not None:

            df.index = (
                df.index
                .tz_localize(None)
            )

    except Exception:
        pass

    return df


def fetch_yahoo(code):

    try:

        df = yf.download(
            f"{code}.KS",
            period="2y",
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False
        )

        return normalize_df(
            df
        )

    except Exception:

        return pd.DataFrame()


def load_price_data(
    code,
    force=False
):

    code = str(
        code
    ).zfill(6)

    now = datetime.now()

    cached = (
        st.session_state.price_cache.get(
            code
        )
    )

    if (
        cached
        and not force
    ):

        try:

            age = (
                now
                - cached["time"]
            ).total_seconds()

            if age < 300:

                return cached["data"]

        except Exception:
            pass

    df = fetch_yahoo(
        code
    )

    if not df.empty:

        st.session_state.price_cache[
            code
        ] = {
            "time": now,
            "data": df
        }

    return df


# ============================================================
# INDICATORS
# ============================================================

def calculate_indicators(df):

    if df is None or df.empty:
        return pd.DataFrame()

    d = df.copy()

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

    d["MA120"] = (
        d["Close"]
        .rolling(120)
        .mean()
    )

    delta = d["Close"].diff()

    gain = (
        delta
        .where(
            delta > 0,
            0
        )
        .rolling(14)
        .mean()
    )

    loss = (
        -delta
        .where(
            delta < 0,
            0
        )
        .rolling(14)
        .mean()
    )

    rs = (
        gain
        / loss.replace(
            0,
            np.nan
        )
    )

    d["RSI14"] = (
        100
        - (
            100
            / (
                1 + rs
            )
        )
    )

    d["VOL20"] = (
        d["Volume"]
        .rolling(20)
        .mean()
    )

    d["VOL_RATIO"] = (
        d["Volume"]
        / d["VOL20"]
    )

    d["RET5"] = (
        d["Close"]
        .pct_change(5)
        * 100
    )

    d["RET20"] = (
        d["Close"]
        .pct_change(20)
        * 100
    )

    d["HIGH20"] = (
        d["High"]
        .rolling(20)
        .max()
    )

    d["LOW20"] = (
        d["Low"]
        .rolling(20)
        .min()
    )

    d["HIGH60"] = (
        d["High"]
        .rolling(60)
        .max()
    )

    d["LOW60"] = (
        d["Low"]
        .rolling(60)
        .min()
    )

    return d


# ============================================================
# NUMBER
# ============================================================

def safe_float(
    value,
    default=0.0
):

    try:

        if pd.isna(value):
            return default

        return float(value)

    except Exception:

        return default


def money(value):

    value = safe_float(
        value
    )

    if abs(value) >= 1000:

        return f"{value:,.0f}원"

    return f"{value:,.2f}원"


# ============================================================
# CHANGE
# ============================================================

def get_daily_change(d):

    if (
        d is None
        or len(d) < 2
    ):

        return 0.0, 0.0

    current = safe_float(
        d["Close"].iloc[-1]
    )

    previous = safe_float(
        d["Close"].iloc[-2]
    )

    if previous == 0:
        return 0.0, 0.0

    change = (
        current
        - previous
    )

    change_pct = (
        change
        / previous
        * 100
    )

    return (
        change,
        change_pct
    )


# ============================================================
# PRICE LEVELS
# ============================================================

def calculate_levels(d):

    if d is None or d.empty:
        return {}

    current = safe_float(
        d["Close"].iloc[-1]
    )

    ma20 = safe_float(
        d["MA20"].iloc[-1],
        current
    )

    ma60 = safe_float(
        d["MA60"].iloc[-1],
        current
    )

    high20 = safe_float(
        d["HIGH20"].iloc[-1],
        current
    )

    low20 = safe_float(
        d["LOW20"].iloc[-1],
        current
    )

    low60 = safe_float(
        d["LOW60"].iloc[-1],
        current
    )

    support = min(
        ma60,
        low20
    )

    risk = min(
        support,
        low60
    )

    return {
        "current": current,
        "first_interest": ma20,
        "support": support,
        "breakout": high20,
        "risk": risk,
    }


# ============================================================
# JUDGMENT
# ============================================================

def get_judgment(d):

    if d is None or d.empty:

        return {
            "title": "데이터 부족",
            "reasons": [
                "가격 데이터를 확인하지 못했습니다."
            ],
            "action":
                "잠시 후 다시 조회해 주세요.",
            "action_reason":
                "가격·거래량 데이터가 확보되지 않아 "
                "판단을 보류합니다.",
            "ma_state": "확인 불가",
            "rsi_state": "확인 불가",
            "vol_state": "확인 불가",
            "rsi": 0,
            "vol_ratio": 0,
            "ret20": 0,
        }

    row = d.iloc[-1]

    current = safe_float(
        row["Close"]
    )

    ma20 = safe_float(
        row["MA20"],
        current
    )

    ma60 = safe_float(
        row["MA60"],
        current
    )

    rsi = safe_float(
        row["RSI14"],
        50
    )

    vol_ratio = safe_float(
        row["VOL_RATIO"],
        1
    )

    ret20 = safe_float(
        row["RET20"],
        0
    )

    above20 = (
        current >= ma20
    )

    above60 = (
        current >= ma60
    )

    ma_state = (
        "20일선 상회"
        if above20
        else "20일선 하회"
    )

    if rsi >= 70:
        rsi_state = "과열권"

    elif rsi >= 60:
        rsi_state = "강세권"

    elif rsi >= 45:
        rsi_state = "중립권"

    elif rsi >= 30:
        rsi_state = "약세권"

    else:
        rsi_state = "과매도권"

    if vol_ratio >= 1.5:
        vol_state = "거래량 강한 확대"

    elif vol_ratio >= 1.1:
        vol_state = "거래량 증가"

    elif vol_ratio >= 0.8:
        vol_state = "평균 수준"

    else:
        vol_state = "거래량 감소"

    if (
        above20
        and above60
        and rsi >= 70
    ):

        title = (
            "상승 추세 · 추격 주의"
        )

        action = (
            "추세는 양호하지만 RSI가 높은 구간입니다. "
            "신규 매수는 현재가 추격보다 20일선 부근 "
            "눌림 확인을 우선합니다."
        )

        action_reason = (
            "20일선·60일선 위의 상승 구조이지만 "
            "과열권에서는 손익비가 낮아질 수 있어 "
            "눌림 확인이 유리합니다."
        )

    elif (
        above20
        and above60
    ):

        title = (
            "상승 추세 유지"
        )

        action = (
            "현재가는 20일선과 60일선 위입니다. "
            "보유자는 20일선 이탈 여부를 확인하고, "
            "미보유자는 돌파 추격보다 눌림을 기다립니다."
        )

        action_reason = (
            "단·중기 이동평균선이 모두 현재가 아래에 있어 "
            "추세가 유지되고 있습니다."
        )

    elif (
        above60
        and not above20
    ):

        title = (
            "단기 조정 · 중기 추세 확인"
        )

        action = (
            "20일선 아래로 조정 중이지만 60일선 위라면 "
            "중기 흐름이 아직 훼손됐다고 단정하기 어렵습니다. "
            "20일선 회복을 확인합니다."
        )

        action_reason = (
            "단기 모멘텀은 약해졌지만 60일선 위라는 "
            "중기 지지 구조가 남아 있습니다."
        )

    elif (
        not above60
        and rsi <= 40
    ):

        title = (
            "중기 약세 · 방어 우선"
        )

        action = (
            "60일선 아래에서 RSI도 약한 구간입니다. "
            "신규 진입보다 지지 형성과 거래량 회복을 "
            "먼저 확인합니다."
        )

        action_reason = (
            "중기 추세와 모멘텀이 동시에 약해 "
            "추가 하락 위험을 가격 확인 없이 "
            "감수할 필요가 낮습니다."
        )

    else:

        title = (
            "방향 확인 구간"
        )

        action = (
            "추세와 모멘텀이 명확하지 않습니다. "
            "20일선 회복 또는 주요 저항 돌파와 "
            "거래량 동반 여부를 확인합니다."
        )

        action_reason = (
            "이동평균·RSI·거래량 중 일부 신호가 "
            "엇갈려 방향 확인이 필요한 구간입니다."
        )

    reasons = [
        f"현재가 {money(current)} · "
        f"20일선 {money(ma20)} · {ma_state}",

        f"RSI14 {rsi:.1f} · "
        f"{rsi_state}",

        f"거래량 {vol_ratio:.2f}배 · "
        f"{vol_state} · "
        f"최근 20일 {ret20:+.2f}%",
    ]

    return {
        "title": title,
        "reasons": reasons,
        "action": action,
        "action_reason": action_reason,
        "ma_state": ma_state,
        "rsi_state": rsi_state,
        "vol_state": vol_state,
        "rsi": rsi,
        "vol_ratio": vol_ratio,
        "ret20": ret20,
    }


# ============================================================
# NAVIGATION
# ============================================================

def navigate_to_etf(code):

    code = str(
        code
    ).zfill(6)

    st.session_state.selected_code = code

    st.session_state.page_request = (
        "📊 내 ETF"
    )

    st.rerun()


# ============================================================
# SEARCH
# ============================================================

def search_etfs(query):

    query = (
        query or ""
    ).strip().lower()

    if not query:
        return []

    results = []

    for code, name in (
        st.session_state.etf_universe.items()
    ):

        if (
            query in code.lower()
            or query in name.lower()
        ):

            results.append({
                "code": code,
                "name": name
            })

    return results[:50]


# ============================================================
# WATCHLIST
# ============================================================

def add_to_watchlist(code):

    code = str(
        code
    ).zfill(6)

    if code not in (
        st.session_state.watchlist
    ):

        st.session_state.watchlist.append(
            code
        )

        write_json(
            WATCHLIST_FILE,
            st.session_state.watchlist
        )

    navigate_to_etf(
        code
    )


def remove_from_watchlist(code):

    code = str(
        code
    ).zfill(6)

    if code in (
        st.session_state.watchlist
    ):

        st.session_state.watchlist.remove(
            code
        )

        write_json(
            WATCHLIST_FILE,
            st.session_state.watchlist
        )

    if (
        st.session_state.selected_code
        == code
    ):

        if st.session_state.watchlist:

            st.session_state.selected_code = (
                st.session_state.watchlist[0]
            )

        else:

            st.session_state.selected_code = (
                next(iter(BASE_ETFS))
            )


# ============================================================
# HOLDINGS
# ============================================================

def render_holdings(code):

    code = str(
        code
    ).zfill(6)

    holdings = (
        st.session_state.holdings
    )

    current_holding = (
        holdings.get(code)
    )

    st.markdown(
        '<div class="section-title">보유 상태</div>',
        unsafe_allow_html=True
    )

    selected = st.radio(
        "보유 여부",
        [
            "미보유",
            "보유중"
        ],
        index=(
            1
            if current_holding
            else 0
        ),
        horizontal=True,
        key=f"holding_status_{code}"
    )

    if selected == "보유중":

        c1, c2 = st.columns(2)

        with c1:

            avg_price = st.number_input(
                "평균매수가",
                min_value=0.0,
                value=float(
                    current_holding.get(
                        "avg_price",
                        0
                    )
                    if current_holding
                    else 0
                ),
                step=100.0,
                key=f"avg_{code}"
            )

        with c2:

            quantity = st.number_input(
                "보유수량",
                min_value=0.0,
                value=float(
                    current_holding.get(
                        "quantity",
                        0
                    )
                    if current_holding
                    else 0
                ),
                step=1.0,
                key=f"qty_{code}"
            )

        if st.button(
            "보유정보 저장",
            key=f"save_hold_{code}",
            use_container_width=True
        ):

            holdings[code] = {
                "avg_price": avg_price,
                "quantity": quantity
            }

            st.session_state.holdings = (
                holdings
            )

            write_json(
                HOLDINGS_FILE,
                holdings
            )

            st.rerun()

        if current_holding:

            current = safe_float(
                st.session_state.get(
                    f"current_price_{code}",
                    0
                )
            )

            if (
                current > 0
                and avg_price > 0
            ):

                pnl_pct = (
                    current
                    / avg_price
                    - 1
                ) * 100

                cls = (
                    "positive"
                    if pnl_pct >= 0
                    else "negative"
                )

                st.markdown(
                    f"""
                    <div class="holding-box">

                        <div class="holding-value">
                            보유 {quantity:,.0f}주
                        </div>

                        <div class="holding-detail">

                            평균매수가
                            {money(avg_price)}

                            · 현재 수익률

                            <span class="{cls}">
                                {pnl_pct:+.2f}%
                            </span>

                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

    elif code in holdings:

        if st.button(
            "보유정보 삭제",
            key=f"delete_hold_{code}",
            use_container_width=True
        ):

            del holdings[code]

            write_json(
                HOLDINGS_FILE,
                holdings
            )

            st.rerun()


# ============================================================
# JUDGMENT UI
# ============================================================

def render_judgment(d):

    judgment = get_judgment(
        d
    )

    rsi = judgment["rsi"]
    vr = judgment["vol_ratio"]

    ma_color = (
        "positive"
        if judgment["ma_state"]
        == "20일선 상회"
        else "negative"
    )

    if rsi >= 60:
        rsi_color = "positive"

    elif rsi < 40:
        rsi_color = "negative"

    else:
        rsi_color = "neutral"

    if vr >= 1.1:
        vol_color = "positive"

    elif vr < 0.8:
        vol_color = "negative"

    else:
        vol_color = "neutral"

    st.markdown(
        '<div class="section-title">'
        '현재판단 · 지금대응'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="evidence-grid">

            <div class="evidence-box">

                <div class="evidence-label">
                    20일선
                </div>

                <div class="evidence-value {ma_color}">
                    {judgment["ma_state"]}
                </div>

                <div class="evidence-sub">
                    최근 20일 추세 기준
                </div>

            </div>


            <div class="evidence-box">

                <div class="evidence-label">
                    RSI14
                </div>

                <div class="evidence-value {rsi_color}">
                    {rsi:.1f}
                </div>

                <div class="evidence-sub">
                    {judgment["rsi_state"]}
                </div>

            </div>


            <div class="evidence-box">

                <div class="evidence-label">
                    거래량
                </div>

                <div class="evidence-value {vol_color}">
                    {vr:.2f}배
                </div>

                <div class="evidence-sub">
                    {judgment["vol_state"]}
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            f"""
            <div class="judgment-box">

                <div class="judgment-title">
                    현재 시장 판단
                </div>

                <div class="judgment-main">
                    {judgment["title"]}
                </div>

                <div class="judgment-reason">

                    <b>판단근거</b>

                    <br>

                    {"<br>".join(
                        judgment["reasons"]
                    )}

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="action-box">

                <div class="action-title">
                    지금 대응
                </div>

                <div class="action-main">

                    {judgment["action"]}

                    <br>
                    <br>

                    <span style="
                        color:#aebaca;
                        font-weight:600;
                    ">

                        대응근거 ·
                        {judgment["action_reason"]}

                    </span>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# PRICE SCENARIOS
# ============================================================

def render_price_scenarios(d):

    levels = calculate_levels(
        d
    )

    if not levels:
        return

    st.markdown(
        '<div class="section-title">'
        '핵심가격 · 대응 시나리오'
        '</div>',
        unsafe_allow_html=True
    )

    cards = [

        (
            "1차 관심가격",
            levels["first_interest"],
            "20일선. 눌림 후 회복 여부 확인"
        ),

        (
            "핵심 지지",
            levels["support"],
            "중기 추세가 유지되는지 확인"
        ),

        (
            "돌파 기준",
            levels["breakout"],
            "최근 20일 고점 돌파 여부"
        ),

        (
            "위험 가격",
            levels["risk"],
            "이탈 시 방어적 대응 검토"
        ),
    ]

    html = (
        '<div class="scenario-grid">'
    )

    for label, price, desc in cards:

        html += f"""
        <div class="scenario-card">

            <div class="scenario-label">
                {label}
            </div>

            <div class="scenario-price">
                {money(price)}
            </div>

            <div class="scenario-desc">
                {desc}
            </div>

        </div>
        """

    html += (
        "</div>"
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# ============================================================
# CHART
# 기존 v13 차트 구조 그대로 유지
# ============================================================

def render_chart(d):

    if d is None or d.empty:

        st.info(
            "차트 데이터를 불러오지 못했습니다."
        )

        return

    chart_df = d.copy()

    end_date = (
        chart_df.index.max()
    )

    start_date = (
        end_date
        - pd.DateOffset(
            months=6
        )
    )

    chart_df = chart_df[
        chart_df.index >= start_date
    ].copy()

    if chart_df.empty:
        return

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.025,
        row_heights=[
            0.74,
            0.26
        ]
    )

    # --------------------------------------------------------
    # CANDLE
    # --------------------------------------------------------

    fig.add_trace(
        go.Candlestick(

            x=chart_df.index,

            open=chart_df["Open"],

            high=chart_df["High"],

            low=chart_df["Low"],

            close=chart_df["Close"],

            increasing=dict(
                line=dict(
                    color="#28d7a0",
                    width=1
                ),
                fillcolor="#28d7a0"
            ),

            decreasing=dict(
                line=dict(
                    color="#ff6577",
                    width=1
                ),
                fillcolor="#ff6577"
            ),

            name="가격",

            showlegend=False
        ),

        row=1,
        col=1
    )

    # --------------------------------------------------------
    # MA20
    # --------------------------------------------------------

    fig.add_trace(
        go.Scatter(

            x=chart_df.index,

            y=chart_df["MA20"],

            mode="lines",

            line=dict(
                color="#55b8ff",
                width=1.6
            ),

            name="20일선"
        ),

        row=1,
        col=1
    )

    # --------------------------------------------------------
    # MA60
    # --------------------------------------------------------

    fig.add_trace(
        go.Scatter(

            x=chart_df.index,

            y=chart_df["MA60"],

            mode="lines",

            line=dict(
                color="#ffc857",
                width=1.5
            ),

            name="60일선"
        ),

        row=1,
        col=1
    )

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    volume_colors = np.where(
        chart_df["Close"]
        >= chart_df["Open"],
        "#28d7a0",
        "#ff6577"
    )

    fig.add_trace(
        go.Bar(

            x=chart_df.index,

            y=chart_df["Volume"],

            marker_color=volume_colors,

            opacity=0.55,

            name="거래량",

            showlegend=False
        ),

        row=2,
        col=1
    )

    # --------------------------------------------------------
    # X AXIS
    # --------------------------------------------------------

    fig.update_xaxes(
        fixedrange=True,
        showgrid=False,
        rangeslider_visible=False,
        row=1,
        col=1
    )

    fig.update_xaxes(
        fixedrange=True,
        showgrid=False,
        row=2,
        col=1
    )

    # --------------------------------------------------------
    # Y AXIS
    # --------------------------------------------------------

    fig.update_yaxes(
        fixedrange=True,
        showgrid=True,
        gridcolor="#1b2a3b",
        zeroline=False,
        tickfont=dict(
            color="#aebbc9",
            size=10
        ),
        row=1,
        col=1
    )

    fig.update_yaxes(
        fixedrange=True,
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        row=2,
        col=1
    )

    # --------------------------------------------------------
    # LAYOUT
    # --------------------------------------------------------

    fig.update_layout(

        height=420,

        margin=dict(
            l=8,
            r=8,
            t=15,
            b=10
        ),

        paper_bgcolor="#0d1928",

        plot_bgcolor="#0d1928",

        font=dict(
            color="#e8eef6"
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,

            font=dict(
                size=10,
                color="#d6deea"
            )
        ),

        hovermode="x unified",

        dragmode=False,

        showlegend=True
    )

    st.plotly_chart(

        fig,

        use_container_width=True,

        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "doubleClick": False,
            "responsive": True,
            "staticPlot": False
        },

        key="fixed_six_month_chart"
    )

    st.caption(
        "최근 6개월 고정 · 확대/축소/이동 없음"
    )


# ============================================================
# THEME CANDIDATES
# ============================================================

def theme_candidates(theme):

    info = THEMES.get(
        theme,
        {}
    )

    seeds = info.get(
        "seeds",
        []
    )

    keywords = info.get(
        "keywords",
        []
    )

    result = []

    # Seed 우선

    for code in seeds:

        code = str(
            code
        ).zfill(6)

        if code not in [
            x["code"]
            for x in result
        ]:

            result.append({
                "code": code,
                "name": get_etf_name(
                    code
                )
            })

    # 키워드

    for code, name in (
        st.session_state.etf_universe.items()
    ):

        text = (
            f"{code} {name}"
        ).lower()

        if any(
            str(k).lower() in text
            for k in keywords
        ):

            if not any(
                x["code"] == code
                for x in result
            ):

                result.append({
                    "code": code,
                    "name": name
                })

    return result[:4]


# ============================================================
# THEME SNAPSHOT
# ============================================================

def theme_snapshot(
    theme,
    force=False
):

    now = datetime.now()

    cached = (
        st.session_state.theme_cache.get(
            theme
        )
    )

    if cached and not force:

        try:

            age = (
                now
                - cached["time"]
            ).total_seconds()

            if age < 300:

                return cached["rows"]

        except Exception:
            pass

    rows = []

    candidates = theme_candidates(
        theme
    )

    for item in candidates:

        code = item["code"]

        df = load_price_data(
            code
        )

        if df.empty:
            continue

        d = calculate_indicators(
            df
        )

        if d.empty:
            continue

        row = d.iloc[-1]

        current = safe_float(
            row["Close"]
        )

        rsi = safe_float(
            row["RSI14"],
            50
        )

        vr = safe_float(
            row["VOL_RATIO"],
            1
        )

        ret20 = safe_float(
            row["RET20"],
            0
        )

        ma20 = safe_float(
            row["MA20"],
            current
        )

        rows.append({
            "code": code,
            "name": item["name"],
            "price": current,
            "rsi": rsi,
            "vol_ratio": vr,
            "ret20": ret20,
            "trend":
                "상승"
                if current >= ma20
                else "조정"
        })

    st.session_state.theme_cache[
        theme
    ] = {
        "time": now,
        "rows": rows
    }

    return rows


# ============================================================
# INLINE ETF ANALYSIS
# ============================================================

def render_inline_analysis(code):

    df = load_price_data(
        code
    )

    if df.empty:

        st.warning(
            "선택 ETF의 가격 데이터를 "
            "불러오지 못했습니다."
        )

        return

    d = calculate_indicators(
        df
    )

    name = get_etf_name(
        code
    )

    current = safe_float(
        d["Close"].iloc[-1]
    )

    change, change_pct = (
        get_daily_change(d)
    )

    st.markdown(
        f"""
        <div class="inline-analysis">

            <div class="inline-title">
                {name}
                · {code}
                · 상세분석
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "현재가",
        money(current)
    )

    c2.metric(
        "등락",
        f"{change:+,.0f}원",
        f"{change_pct:+.2f}%"
    )

    c3.metric(
        "RSI14",
        f"{safe_float(
            d['RSI14'].iloc[-1],
            50
        ):.1f}"
    )

    c4.metric(
        "거래량",
        f"{safe_float(
            d['VOL_RATIO'].iloc[-1],
            1
        ):.2f}배"
    )

    render_judgment(
        d
    )

    render_price_scenarios(
        d
    )

    st.markdown(
        '<div class="section-title">'
        '가격 흐름'
        '</div>',
        unsafe_allow_html=True
    )

    render_chart(
        d
    )


# ============================================================
# THEME ETF CARD
# ============================================================

def render_theme_etf(
    item,
    theme_index,
    item_index
):

    code = item["code"]

    ret20 = item["ret20"]

    trend = item["trend"]

    ret_cls = (
        "positive"
        if ret20 >= 0
        else "negative"
    )

    trend_cls = (
        "positive"
        if trend == "상승"
        else "negative"
    )

    st.markdown(
        f"""
        <div class="theme-etf-box">

            <div class="theme-etf-name">
                {item["name"]}
            </div>

            <div class="theme-etf-code">
                {code}
            </div>

            <div class="theme-data-grid">

                <div class="theme-data-item">

                    <div class="theme-data-label">
                        현재가
                    </div>

                    <div class="theme-data-value">
                        {money(item["price"])}
                    </div>

                </div>


                <div class="theme-data-item">

                    <div class="theme-data-label">
                        RSI14
                    </div>

                    <div class="theme-data-value">
                        {item["rsi"]:.1f}
                    </div>

                </div>


                <div class="theme-data-item">

                    <div class="theme-data-label">
                        거래량
                    </div>

                    <div class="theme-data-value">
                        {item["vol_ratio"]:.2f}배
                    </div>

                </div>


                <div class="theme-data-item">

                    <div class="theme-data-label">
                        20일 수익률
                    </div>

                    <div class="theme-data-value {ret_cls}">
                        {ret20:+.2f}%
                    </div>

                </div>

            </div>

            <div style="
                margin-top:7px;
                font-size:.78rem;
                color:#b9c6d5;
            ">

                추세:

                <span class="{trend_cls}">
                    {trend}
                </span>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "ETF 분석",
        key=(
            f"future_analyze_"
            f"{theme_index}_"
            f"{item_index}_"
            f"{code}"
        ),
        use_container_width=True
    ):

        # 미래테마 화면을 유지하고
        # 선택 ETF만 바로 아래에 표시

        st.session_state.theme_analysis = (
            code
        )

        st.rerun()


# ============================================================
# FUTURE THEME CARD
# ============================================================

def render_theme_card(
    theme_index,
    theme,
    stage
):

    info = THEMES[
        theme
    ]

    st.markdown(
        f"""
        <div class="theme-card">

            <div class="theme-stage">
                {stage}
            </div>

            <div class="theme-title">
                {theme}
            </div>

            <div class="theme-reason">
                {info["reason"]}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    rows = theme_snapshot(
        theme
    )

    if not rows:

        st.info(
            "현재 표시 가능한 ETF 데이터를 "
            "확인하지 못했습니다."
        )

        return

    cols = st.columns(
        len(rows)
    )

    for i, item in enumerate(rows):

        with cols[i]:

            render_theme_etf(
                item,
                theme_index,
                i
            )

        # ====================================================
        # 중요:
        # ETF 분석을 누르면
        # 내 ETF 페이지로 이동하지 않고
        # 해당 ETF 카드 아래에서 바로 분석
        # ====================================================

        if (
            st.session_state.theme_analysis
            == item["code"]
        ):

            render_inline_analysis(
                item["code"]
            )


# ============================================================
# ETF FINDER
# ============================================================

def render_etf_finder():

    st.markdown(
        '<div class="section-title">'
        'ETF 찾기'
        '</div>',
        unsafe_allow_html=True
    )

    query = st.text_input(
        "ETF 검색",
        placeholder="ETF명 또는 종목코드 입력",
        label_visibility="collapsed",
        key="etf_search_query"
    )

    results = search_etfs(
        query
    )

    if results:

        labels = [
            f"{x['name']} · {x['code']}"
            for x in results
        ]

        selected_label = st.selectbox(
            "검색 결과",
            labels,
            key="search_result_select"
        )

        selected_item = results[
            labels.index(
                selected_label
            )
        ]

        c1, c2 = st.columns(
            [4, 1]
        )

        with c1:

            st.caption(
                f"선택: "
                f"{selected_item['name']} "
                f"({selected_item['code']})"
            )

        with c2:

            already = (
                selected_item["code"]
                in st.session_state.watchlist
            )

            if st.button(
                "추가"
                if not already
                else "등록됨",

                disabled=already,

                use_container_width=True,

                key=(
                    "add_"
                    + selected_item["code"]
                )
            ):

                add_to_watchlist(
                    selected_item["code"]
                )

    elif query:

        st.caption(
            "검색 결과가 없습니다."
        )


# ============================================================
# WATCHLIST UI
# ============================================================

def render_watchlist():

    st.markdown(
        '<div class="section-title">'
        '관심종목'
        '</div>',
        unsafe_allow_html=True
    )

    watchlist = (
        st.session_state.watchlist
    )

    if not watchlist:

        st.info(
            "관심종목이 없습니다."
        )

        return

    options = [
        f"{get_etf_name(code)} · {code}"
        for code in watchlist
    ]

    current = (
        st.session_state.selected_code
    )

    try:

        default_index = (
            watchlist.index(
                current
            )
        )

    except ValueError:

        default_index = 0

    selected_label = st.selectbox(
        "관심종목 선택",
        options,
        index=default_index,
        key="watchlist_select"
    )

    idx = options.index(
        selected_label
    )

    selected_code = (
        watchlist[idx]
    )

    st.session_state.selected_code = (
        selected_code
    )

    if st.button(
        "현재 ETF 관심종목에서 삭제",
        use_container_width=True,
        key="remove_watchlist"
    ):

        remove_from_watchlist(
            selected_code
        )

        st.rerun()


# ============================================================
# MY ETF
# ============================================================

def render_my_etf():

    render_etf_finder()

    render_watchlist()

    code = (
        st.session_state.selected_code
    )

    name = get_etf_name(
        code
    )

    df = load_price_data(
        code
    )

    if df.empty:

        st.error(
            "가격 데이터를 불러오지 못했습니다. "
            "잠시 후 다시 시도해 주세요."
        )

        return

    d = calculate_indicators(
        df
    )

    if d.empty:

        st.error(
            "분석 데이터를 만들지 못했습니다."
        )

        return

    current = safe_float(
        d["Close"].iloc[-1]
    )

    change, change_pct = (
        get_daily_change(d)
    )

    change_cls = (

        "positive"
        if change > 0

        else "negative"
        if change < 0

        else "neutral"
    )

    date_text = (
        d.index[-1]
        .strftime(
            "%Y-%m-%d"
        )
    )

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="hero">

            <div class="hero-name">
                {name}
            </div>

            <div class="hero-code">
                {code}
            </div>

            <div class="quote-row">

                <div class="quote-price">
                    {money(current)}
                </div>

                <div class="quote-change {change_cls}">
                    {money(change)}
                    ({change_pct:+.2f}%)
                </div>

            </div>

            <div class="hero-date">
                기준일 {date_text}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.session_state[
        f"current_price_{code}"
    ] = current

    # --------------------------------------------------------
    # HOLDING
    # --------------------------------------------------------

    render_holdings(
        code
    )

    # --------------------------------------------------------
    # JUDGMENT
    # --------------------------------------------------------

    render_judgment(
        d
    )

    # --------------------------------------------------------
    # PRICE LEVEL
    # --------------------------------------------------------

    render_price_scenarios(
        d
    )

    # --------------------------------------------------------
    # CHART
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '가격 흐름'
        '</div>',
        unsafe_allow_html=True
    )

    render_chart(
        d
    )


# ============================================================
# FUTURE THEME
# ============================================================

def render_future_theme():

    st.markdown(
        """
        <div class="hero">

            <div class="hero-name">
                미래테마
            </div>

            <div class="hero-code">
                현재 주도 → 다음 수혜 → 초기 관심
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # 시장 새로고침 제거
    #
    # ETF 목록을 외부에서 다시 긁어오는 과정이
    # 한글 깨짐과 불필요한 오류의 원인이 될 수 있으므로
    # 기본 ETF + 기존 캐시 목록만 사용
    #
    # 실제 가격/거래량 데이터는 ETF 분석 시
    # yfinance에서 별도로 조회
    # ========================================================

    for idx, (
        theme,
        stage
    ) in enumerate(
        FUTURE_CHAIN
    ):

        render_theme_card(
            idx,
            theme,
            stage
        )

    # ========================================================
    # THEME SUMMARY
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '테마 요약'
        '</div>',
        unsafe_allow_html=True
    )

    summary_rows = []

    for theme, stage in FUTURE_CHAIN:

        rows = theme_snapshot(
            theme
        )

        if not rows:
            continue

        avg_ret = np.mean(
            [
                x["ret20"]
                for x in rows
            ]
        )

        avg_rsi = np.mean(
            [
                x["rsi"]
                for x in rows
            ]
        )

        avg_vol = np.mean(
            [
                x["vol_ratio"]
                for x in rows
            ]
        )

        summary_rows.append({

            "테마":
                theme,

            "단계":
                stage,

            "평균 20일수익률":
                f"{avg_ret:+.2f}%",

            "평균 RSI":
                f"{avg_rsi:.1f}",

            "평균 거래량":
                f"{avg_vol:.2f}배",

        })

    if summary_rows:

        st.dataframe(
            pd.DataFrame(
                summary_rows
            ),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# INIT
# ============================================================

init_state()


# ============================================================
# PAGE REQUEST
# ============================================================

if st.session_state.page_request:

    requested_page = (
        st.session_state.page_request
    )

    st.session_state.page_request = None

    if requested_page in [
        "📊 내 ETF",
        "🚀 미래테마"
    ]:

        st.session_state.main_page = (
            requested_page
        )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="app-header">

        <div class="app-title">
            ETF RADAR
        </div>

        <div class="app-subtitle">
            ETF 추세 · 모멘텀 · 거래량 ·
            핵심가격 · 대응 시나리오
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# NAVIGATION
# ============================================================

nav = st.radio(
    "메뉴",
    [
        "📊 내 ETF",
        "🚀 미래테마"
    ],
    horizontal=True,
    key="main_page"
)


# ============================================================
# PAGE
# ============================================================

if nav == "📊 내 ETF":

    render_my_etf()

else:

    render_future_theme()