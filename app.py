# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import json
import os

from datetime import datetime


# ============================================================
# ETF RADAR
# Stable Mobile Financial Dashboard
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

:root {
    --bg: #07111f;
    --panel: #0d1928;
    --panel2: #111f31;
    --panel3: #16263a;

    --text: #d9e2ec;
    --text2: #aebdcd;
    --muted: #71859a;

    --blue: #5caeff;
    --green: #39c99a;
    --red: #ef6678;
    --yellow: #d9ad4b;

    --border: #22364b;
}


/* ============================================================
   BASE
   ============================================================ */

html,
body,
.stApp {
    background: #07111f !important;
    color: #d9e2ec !important;
}

html,
body,
[class*="css"] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        "Noto Sans KR",
        sans-serif;
}

.block-container {
    max-width: 1180px;
    padding: 10px 12px 30px !important;
}

p,
span,
div,
label {
    color: #d9e2ec;
}

h1,
h2,
h3,
h4 {
    color: #dfe7ef !important;
}


/* ============================================================
   CAPTION
   ============================================================ */

[data-testid="stCaptionContainer"] p,
.stCaption {
    color: #71859a !important;
}


/* ============================================================
   BUTTON
   ============================================================ */

.stButton > button {
    background: #132235 !important;
    color: #cfd9e5 !important;

    border: 1px solid #29425a !important;
    border-radius: 8px !important;

    font-weight: 700 !important;
    min-height: 36px !important;
}

.stButton > button:hover {
    background: #19304a !important;
    border-color: #47779f !important;
}

.stButton > button[kind="primary"] {
    background: #164d78 !important;
    color: #e7f1fa !important;
}


/* ============================================================
   INPUT
   ============================================================ */

div[data-baseweb="input"] > div {
    background: #0d1a29 !important;
    border-color: #294057 !important;
}

div[data-baseweb="input"] input {
    color: #d9e2ec !important;
    -webkit-text-fill-color: #d9e2ec !important;
}


/* ============================================================
   SELECTBOX
   ============================================================ */

div[data-baseweb="select"] > div {
    background: #0d1a29 !important;
    border-color: #294057 !important;
    color: #cbd7e4 !important;
}

div[data-baseweb="select"] * {
    color: #cbd7e4 !important;
}

ul[role="listbox"],
div[role="listbox"] {
    background: #0d1a29 !important;
    color: #cbd7e4 !important;
}

li[role="option"] {
    background: #0d1a29 !important;
    color: #cbd7e4 !important;
}

li[role="option"]:hover {
    background: #17304a !important;
}


/* ============================================================
   RADIO
   ============================================================ */

.stRadio label {
    color: #aebdcd !important;
}


/* ============================================================
   DIVIDER
   ============================================================ */

hr {
    border-color: #1b2b3d !important;
}


/* ============================================================
   HEADER
   ============================================================ */

.app-header {
    padding: 4px 0 10px;
}

.app-title {
    font-size: 1.45rem;
    font-weight: 850;
    color: #dce5ee;
}

.app-subtitle {
    font-size: 0.75rem;
    color: #73869b;
    margin-top: 2px;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {
    background: #0d1928;

    border: 1px solid #263d53;
    border-radius: 12px;

    padding: 14px;
    margin-bottom: 10px;
}

.hero-name {
    font-size: 1.18rem;
    font-weight: 800;
    color: #dce5ee;
}

.hero-code {
    font-size: 0.72rem;
    color: #71869b;
    margin-top: 2px;
}

.quote-row {
    display: flex;
    gap: 12px;
    align-items: baseline;
    margin-top: 10px;
}

.quote-price {
    font-size: 1.85rem;
    font-weight: 850;
    color: #e2e8ef;
}

.quote-change {
    font-size: 0.88rem;
    font-weight: 750;
}

.positive {
    color: #39c99a !important;
}

.negative {
    color: #ef6678 !important;
}

.neutral {
    color: #a9b7c6 !important;
}

.hero-date {
    font-size: 0.70rem;
    color: #71869b;
    margin-top: 6px;
}


/* ============================================================
   SECTION
   ============================================================ */

.section-title {
    font-size: 0.92rem;
    font-weight: 800;
    color: #cbd6e1;

    margin: 15px 0 7px;
}

.section-subtitle {
    font-size: 0.72rem;
    color: #71869b;
}


/* ============================================================
   EVIDENCE
   ============================================================ */

.evidence-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);

    gap: 6px;
    margin: 6px 0 9px;
}

.evidence-box {
    background: #0b1725;

    border: 1px solid #1e3449;
    border-radius: 8px;

    padding: 8px;
}

.evidence-label {
    font-size: 0.66rem;
    color: #72859a;
}

.evidence-value {
    font-size: 0.88rem;
    font-weight: 800;
    color: #cbd6e1;
}

.evidence-sub {
    font-size: 0.65rem;
    color: #71869b;

    margin-top: 2px;
}


/* ============================================================
   JUDGMENT
   ============================================================ */

.judgment-box,
.action-box {
    background: #0d1928;

    border: 1px solid #22384d;
    border-radius: 9px;

    padding: 11px;
}

.judgment-box {
    border-left: 3px solid #4b89bd;
}

.action-box {
    border-left: 3px solid #7b6b42;
}

.judgment-title,
.action-title {
    font-size: 0.67rem;
    color: #72859a;
}

.action-title {
    color: #a99561;
}

.judgment-main {
    font-size: 1rem;
    font-weight: 800;

    color: #cfd9e4;

    margin-top: 3px;
}

.judgment-reason,
.action-main {
    font-size: 0.76rem;

    line-height: 1.45;

    color: #aab8c7;

    margin-top: 6px;
}


/* ============================================================
   SCENARIO
   ============================================================ */

.scenario-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);

    gap: 6px;
}

.scenario-card {
    background: #0b1725;

    border: 1px solid #1e3449;
    border-radius: 8px;

    padding: 9px;
}

.scenario-label {
    font-size: 0.65rem;
    color: #71859a;
}

.scenario-price {
    font-size: 0.95rem;
    font-weight: 800;

    color: #cbd5df;

    margin-top: 3px;
}

.scenario-desc {
    font-size: 0.65rem;
    line-height: 1.35;

    color: #8d9cad;

    margin-top: 4px;
}


/* ============================================================
   HOLDING
   ============================================================ */

.holding-box {
    background: #0b1725;

    border: 1px solid #20364b;
    border-radius: 8px;

    padding: 9px;
}

.holding-value {
    font-size: 0.86rem;
    font-weight: 800;
    color: #cbd6e1;
}

.holding-detail {
    font-size: 0.70rem;
    color: #8293a8;

    margin-top: 3px;
}


/* ============================================================
   FUTURE THEME
   ============================================================ */

.theme-card {
    background: #0d1928;

    border: 1px solid #22384d;
    border-radius: 10px;

    padding: 11px;
    margin-bottom: 7px;
}

.theme-stage {
    font-size: 0.67rem;
    color: #7199b8;
    font-weight: 750;
}

.theme-title {
    font-size: 1rem;
    font-weight: 800;

    color: #cfd9e4;

    margin-top: 2px;
}

.theme-reason {
    font-size: 0.72rem;
    color: #8999aa;

    line-height: 1.4;

    margin: 4px 0 8px;
}


/* ============================================================
   THEME ETF
   ============================================================ */

.theme-etf-box {
    background: #0b1725;

    border: 1px solid #1e3449;
    border-radius: 8px;

    padding: 9px;
}

.theme-etf-name {
    font-size: 0.78rem;
    font-weight: 800;

    color: #cbd5df;
}

.theme-etf-code {
    font-size: 0.64rem;
    color: #6f8297;
}

.theme-data-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);

    gap: 4px;
    margin-top: 6px;
}

.theme-data-item {
    background: #091522;

    border-radius: 5px;

    padding: 5px;
}

.theme-data-label {
    font-size: 0.58rem;
    color: #6f8297;
}

.theme-data-value {
    font-size: 0.72rem;
    font-weight: 800;

    color: #bfcbd7;

    margin-top: 1px;
}


/* ============================================================
   DATAFRAME
   ============================================================ */

[data-testid="stDataFrame"] {
    background: #0d1928 !important;
}


/* ============================================================
   METRIC
   ============================================================ */

[data-testid="stMetric"] {
    background: #0b1725 !important;

    border: 1px solid #1e3449 !important;

    padding: 7px !important;

    border-radius: 7px !important;
}

[data-testid="stMetricLabel"] {
    color: #74879b !important;
    font-size: 0.65rem !important;
}

[data-testid="stMetricValue"] {
    color: #cbd6e1 !important;
    font-size: 1rem !important;
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 700px) {

    .block-container {
        padding: 7px 8px 24px !important;
    }

    .app-title {
        font-size: 1.3rem;
    }

    .quote-price {
        font-size: 1.65rem;
    }

    .evidence-value {
        font-size: 0.80rem;
    }

    .scenario-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .theme-data-grid {
        grid-template-columns: repeat(2, 1fr);
    }

}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# FILE
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"
UNIVERSE_FILE = "etf_universe_cache.json"


# ============================================================
# ETF
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

            if not isinstance(
                item,
                dict
            ):
                continue

            code = item.get(
                "code"
            )

            name = item.get(
                "name"
            )

            if code and name:

                universe[
                    str(code).zfill(6)
                ] = str(name)

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

        saved = read_json(
            HOLDINGS_FILE,
            {}
        )

        st.session_state.holdings = (
            saved
            if isinstance(saved, dict)
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
            else "395160"
        )


    if "main_page" not in st.session_state:

        st.session_state.main_page = (
            "📊 내 ETF"
        )


# ============================================================
# ETF NAME
# ============================================================

def get_etf_name(code):

    code = str(code).zfill(6)

    return (
        st.session_state.etf_universe.get(
            code
        )
        or BASE_ETFS.get(code)
        or f"ETF {code}"
    )


# ============================================================
# PRICE
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

    rename_map = {}

    for col in df.columns:

        key = str(col).lower()

        if key == "open":
            rename_map[col] = "Open"

        elif key == "high":
            rename_map[col] = "High"

        elif key == "low":
            rename_map[col] = "Low"

        elif key == "close":
            rename_map[col] = "Close"

        elif key == "volume":
            rename_map[col] = "Volume"

    df = df.rename(
        columns=rename_map
    )

    required = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    if not all(
        col in df.columns
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
        subset=["Close"]
    )

    if getattr(
        df.index,
        "tz",
        None
    ) is not None:

        try:

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

        return normalize_df(df)

    except Exception:

        return pd.DataFrame()


def load_price_data(
    code,
    force=False
):

    code = str(code).zfill(6)

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

        age = (
            now - cached["time"]
        ).total_seconds()
        
        if age < 300:

            return cached["data"]

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

    if df.empty:
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

    rs = gain / loss.replace(
        0,
        np.nan
    )

    d["RSI14"] = (
        100
        - (
            100
            / (1 + rs)
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

    d["LOW60"] = (
        d["Low"]
        .rolling(60)
        .min()
    )

    return d


# ============================================================
# SAFE
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
# JUDGMENT
# ============================================================

def get_judgment(d):

    if d.empty:

        return {
            "title": "데이터 부족",
            "reasons": [
                "가격 데이터를 확인하지 못했습니다."
            ],
            "action":
                "데이터를 다시 조회해 주세요.",
            "ma_state": "확인 불가",
            "rsi_state": "확인 불가",
            "vol_state": "확인 불가",
            "rsi": 0,
            "vol_ratio": 0,
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
            "추세는 양호하지만 과열 가능성이 있습니다. "
            "신규 매수는 현재가 추격보다 눌림 확인을 우선합니다."
        )


    elif (
        above20
        and above60
    ):

        title = (
            "상승 추세 유지"
        )

        action = (
            "20일선과 60일선 위입니다. "
            "보유자는 추세를 확인하고 신규 매수는 "
            "돌파 추격보다 눌림을 우선합니다."
        )


    elif (
        above60
        and not above20
    ):

        title = (
            "단기 조정 · 중기 추세 확인"
        )

        action = (
            "20일선 아래지만 60일선 위입니다. "
            "20일선 회복 여부를 확인합니다."
        )


    elif (
        not above60
        and rsi <= 40
    ):

        title = (
            "중기 약세 · 방어 우선"
        )

        action = (
            "60일선 아래이고 RSI도 약합니다. "
            "지지 형성과 거래량 회복을 먼저 확인합니다."
        )


    else:

        title = (
            "방향 확인 구간"
        )

        action = (
            "추세가 명확하지 않습니다. "
            "20일선 회복 또는 저항 돌파와 "
            "거래량 동반 여부를 확인합니다."
        )


    reasons = [

        (
            f"현재가 {money(current)} · "
            f"20일선 {money(ma20)} · "
            f"{ma_state}"
        ),

        (
            f"RSI14 {rsi:.1f} · "
            f"{rsi_state}"
        ),

        (
            f"거래량 {vol_ratio:.2f}배 · "
            f"{vol_state} · "
            f"최근 20일 {ret20:+.2f}%"
        ),
    ]


    return {

        "title": title,

        "reasons": reasons,

        "action": action,

        "ma_state": ma_state,

        "rsi_state": rsi_state,

        "vol_state": vol_state,

        "rsi": rsi,

        "vol_ratio": vol_ratio,
    }


# ============================================================
# LEVEL
# ============================================================

def calculate_levels(d):

    if d.empty:
        return None

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

    return {

        "first":
            ma20,

        "support":
            min(
                ma60,
                low20
            ),

        "breakout":
            high20,

        "risk":
            min(
                ma60,
                low20,
                low60
            ),
    }


# ============================================================
# JUDGMENT UI
# ============================================================

def render_judgment(d):

    judgment = get_judgment(
        d
    )

    st.markdown(
        '<div class="section-title">'
        '현재판단 · 지금대응'
        '</div>',
        unsafe_allow_html=True
    )


    rsi = judgment["rsi"]
    vr = judgment["vol_ratio"]


    if (
        judgment["ma_state"]
        == "20일선 상회"
    ):

        ma_color = "positive"

    else:

        ma_color = "negative"


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
                    단기 추세
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


    c1, c2 = st.columns(
        2
    )


    with c1:

        st.markdown(
            f"""
            <div class="judgment-box">

                <div class="judgment-title">
                    현재판단
                </div>

                <div class="judgment-main">
                    {judgment["title"]}
                </div>

                <div class="judgment-reason">
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
                    지금대응
                </div>

                <div class="action-main">
                    {judgment["action"]}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# PRICE SCENARIOS
# ============================================================

def render_scenarios(d):

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
            "1차 관심",
            levels["first"],
            "20일선 부근 눌림 확인"
        ),

        (
            "핵심 지지",
            levels["support"],
            "중기 추세 유지 여부"
        ),

        (
            "돌파 기준",
            levels["breakout"],
            "최근 20일 고점 돌파"
        ),

        (
            "위험 가격",
            levels["risk"],
            "이탈 시 방어 검토"
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


    html += "</div>"


    st.markdown(
        html,
        unsafe_allow_html=True
    )


# ============================================================
# CHART
# ============================================================

def render_chart(d):

    if d.empty:

        st.warning(
            "차트 데이터를 확인하지 못했습니다."
        )

        return


    chart_df = d.tail(
        126
    ).copy()


    fig = make_subplots(

        rows=2,
        cols=1,

        shared_xaxes=True,

        vertical_spacing=0.025,

        row_heights=[
            0.75,
            0.25
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

            increasing_line_color="#39c99a",

            increasing_fillcolor="#39c99a",

            decreasing_line_color="#ef6678",

            decreasing_fillcolor="#ef6678",

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
                color="#4f86b5",
                width=1.4
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
                color="#a58c52",
                width=1.3
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

        "#327f69",

        "#9b4653"
    )


    fig.add_trace(

        go.Bar(

            x=chart_df.index,

            y=chart_df["Volume"],

            marker_color=volume_colors,

            opacity=0.5,

            name="거래량",

            showlegend=False
        ),

        row=2,
        col=1
    )


    # --------------------------------------------------------
    # AXIS
    # --------------------------------------------------------

    fig.update_xaxes(

        fixedrange=True,

        showgrid=False,

        rangeslider_visible=False
    )


    fig.update_yaxes(

        fixedrange=True,

        gridcolor="#17283a",

        tickfont=dict(
            color="#73879b",
            size=9
        ),

        row=1,
        col=1
    )


    fig.update_yaxes(

        fixedrange=True,

        showticklabels=False,

        showgrid=False,

        row=2,
        col=1
    )


    # --------------------------------------------------------
    # LAYOUT
    # --------------------------------------------------------

    fig.update_layout(

        height=390,

        margin=dict(
            l=4,
            r=4,
            t=18,
            b=4
        ),

        paper_bgcolor="#0d1928",

        plot_bgcolor="#0d1928",

        font=dict(
            color="#aab8c7"
        ),

        legend=dict(

            orientation="h",

            y=1.02,

            x=1,

            xanchor="right",

            font=dict(
                size=9,
                color="#8ea0b3"
            )
        ),

        dragmode=False,

        hovermode="x unified"
    )


    st.plotly_chart(

        fig,

        use_container_width=True,

        config={

            "displayModeBar": False,

            "scrollZoom": False,

            "doubleClick": False,

            "responsive": True,
        }
    )


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

            results.append(
                {
                    "code": code,
                    "name": name
                }
            )


    return results[:30]


# ============================================================
# WATCHLIST
# ============================================================

def add_watch(code):

    code = str(code).zfill(6)


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


    st.session_state.selected_code = (
        code
    )


# ============================================================
# FINDER
# ============================================================

def render_finder():

    st.markdown(
        '<div class="section-title">'
        'ETF 찾기'
        '</div>',
        unsafe_allow_html=True
    )


    query = st.text_input(

        "ETF명 또는 종목코드",

        placeholder=
        "예: AI반도체 / 395160",

        label_visibility="collapsed",

        key="search_q"
    )


    results = search_etfs(
        query
    )


    if results:

        labels = [

            f'{x["name"]} · {x["code"]}'

            for x in results

        ]


        selected_label = (
            st.selectbox(
                "검색 결과",
                labels,
                key="search_result"
            )
        )


        item = results[
            labels.index(
                selected_label
            )
        ]


        c1, c2 = st.columns(
            [4, 1]
        )


        with c1:

            st.caption(
                f'선택: {item["name"]} '
                f'({item["code"]})'
            )


        with c2:

            already = (
                item["code"]
                in st.session_state.watchlist
            )


            if st.button(

                "추가"
                if not already
                else "등록됨",

                disabled=already,

                use_container_width=True,

                key=f'add_{item["code"]}'
            ):

                add_watch(
                    item["code"]
                )

                st.rerun()


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


    labels = [

        f"{get_etf_name(code)} · {code}"

        for code in watchlist

    ]


    current = (
        st.session_state.selected_code
    )


    if current in watchlist:

        default_index = (
            watchlist.index(
                current
            )
        )

    else:

        default_index = 0


    selected_label = st.selectbox(

        "관심종목 선택",

        labels,

        index=default_index,

        key="watch_select"
    )


    code = watchlist[
        labels.index(
            selected_label
        )
    ]


    st.session_state.selected_code = (
        code
    )


    if st.button(

        "현재 ETF 관심종목에서 삭제",

        use_container_width=True,

        key="remove_watch"
    ):

        watchlist.remove(
            code
        )

        write_json(
            WATCHLIST_FILE,
            watchlist
        )


        st.session_state.selected_code = (

            watchlist[0]
            if watchlist
            else "395160"
        )


        st.rerun()


# ============================================================
# HOLDINGS
# ============================================================

def render_holdings(
    code,
    current
):

    st.markdown(
        '<div class="section-title">'
        '보유 상태'
        '</div>',
        unsafe_allow_html=True
    )


    old = (
        st.session_state.holdings.get(
            code
        )
    )


    held = st.radio(

        "보유 여부",

        [
            "미보유",
            "보유중"
        ],

        index=1 if old else 0,

        horizontal=True,

        key=f"held_{code}"
    )


    if held == "보유중":

        c1, c2 = st.columns(
            2
        )


        with c1:

            avg = st.number_input(

                "평균매수가",

                min_value=0.0,

                value=float(
                    old.get(
                        "avg_price",
                        0
                    )
                    if old
                    else 0
                ),

                step=100.0,

                key=f"avg_{code}"
            )


        with c2:

            qty = st.number_input(

                "보유수량",

                min_value=0.0,

                value=float(
                    old.get(
                        "quantity",
                        0
                    )
                    if old
                    else 0
                ),

                step=1.0,

                key=f"qty_{code}"
            )


        if st.button(

            "보유정보 저장",

            key=f"save_{code}",

            use_container_width=True
        ):

            st.session_state.holdings[
                code
            ] = {

                "avg_price": avg,

                "quantity": qty
            }


            write_json(

                HOLDINGS_FILE,

                st.session_state.holdings
            )


            st.rerun()


        if avg > 0:

            pnl = (
                current
                / avg
                - 1
            ) * 100


            cls = (
                "positive"
                if pnl >= 0
                else "negative"
            )


            st.markdown(

                f"""
                <div class="holding-box">

                    <div class="holding-value">
                        보유 {qty:,.0f}주
                    </div>

                    <div class="holding-detail">
                        평균매수가 {money(avg)}
                        · 현재 수익률
                        <span class="{cls}">
                            {pnl:+.2f}%
                        </span>
                    </div>

                </div>
                """,

                unsafe_allow_html=True
            )


    elif old:

        if st.button(

            "보유정보 삭제",

            key=f"del_{code}",

            use_container_width=True
        ):

            del st.session_state.holdings[
                code
            ]

            write_json(

                HOLDINGS_FILE,

                st.session_state.holdings
            )

            st.rerun()


# ============================================================
# MY ETF
# ============================================================

def render_my_etf():

    render_finder()

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
            "종목코드 또는 인터넷 연결을 확인해 주세요."
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


    if len(d) >= 2:

        previous = safe_float(
            d["Close"].iloc[-2]
        )

    else:

        previous = current


    change = (
        current
        - previous
    )


    if previous != 0:

        change_pct = (
            change
            / previous
            * 100
        )

    else:

        change_pct = 0


    if change > 0:

        cls = "positive"

    elif change < 0:

        cls = "negative"

    else:

        cls = "neutral"


    date_text = (
        d.index[-1]
        .strftime("%Y-%m-%d")
    )


    # ========================================================
    # HERO
    # ========================================================

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

                <div class="quote-change {cls}">
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


    # ========================================================
    # HOLDING
    # ========================================================

    render_holdings(
        code,
        current
    )


    # ========================================================
    # JUDGMENT
    # ========================================================

    render_judgment(
        d
    )


    # ========================================================
    # SCENARIO
    # ========================================================

    render_scenarios(
        d
    )


    # ========================================================
    # CHART
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '가격 흐름 · 최근 6개월'
        '</div>',
        unsafe_allow_html=True
    )


    render_chart(
        d
    )


# ============================================================
# THEME CANDIDATES
# ============================================================

def theme_candidates(theme):

    info = THEMES[
        theme
    ]


    result = []


    for code in info["seeds"]:

        if code not in [
            x["code"]
            for x in result
        ]:

            result.append(
                {
                    "code": code,
                    "name": get_etf_name(code)
                }
            )


    for code, name in (
        st.session_state.etf_universe.items()
    ):

        text = (
            f"{code} {name}"
        ).lower()


        if any(

            keyword.lower()
            in text

            for keyword
            in info["keywords"]

        ):

            if code not in [
                x["code"]
                for x in result
            ]:

                result.append(
                    {
                        "code": code,
                        "name": name
                    }
                )


    return result[:4]


# ============================================================
# THEME SNAPSHOT
# ============================================================

def theme_snapshot(theme):

    cached = (
        st.session_state.theme_cache.get(
            theme
        )
    )


    now = datetime.now()


    if cached:

        age = (
            now - cached["time"]
        ).total_seconds()


        if age < 300:

            return cached["rows"]


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

        ma20 = safe_float(
            row["MA20"],
            current
        )


        rows.append(

            {
                "code":
                    code,

                "name":
                    item["name"],

                "price":
                    current,

                "rsi":
                    safe_float(
                        row["RSI14"],
                        50
                    ),

                "vr":
                    safe_float(
                        row["VOL_RATIO"],
                        1
                    ),

                "ret":
                    safe_float(
                        row["RET20"],
                        0
                    ),

                "trend":
                    (
                        "상승"
                        if current >= ma20
                        else "조정"
                    ),
            }
        )


    st.session_state.theme_cache[
        theme
    ] = {

        "time":
            now,

        "rows":
            rows
    }


    return rows


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
    # THEME CARDS
    # ========================================================

    for theme_index, (
        theme,
        stage
    ) in enumerate(
        FUTURE_CHAIN
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

            st.caption(
                "현재 표시 가능한 ETF 데이터가 없습니다."
            )

            continue


        cols = st.columns(
            len(rows)
        )


        for i, item in enumerate(
            rows
        ):

            with cols[i]:

                ret_cls = (
                    "positive"
                    if item["ret"] >= 0
                    else "negative"
                )


                trend_cls = (
                    "positive"
                    if item["trend"] == "상승"
                    else "negative"
                )


                st.markdown(

                    f"""
                    <div class="theme-etf-box">

                        <div class="theme-etf-name">
                            {item["name"]}
                        </div>

                        <div class="theme-etf-code">
                            {item["code"]}
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
                                    RSI
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
                                    {item["vr"]:.2f}배
                                </div>

                            </div>


                            <div class="theme-data-item">

                                <div class="theme-data-label">
                                    20일
                                </div>

                                <div class="theme-data-value {ret_cls}">
                                    {item["ret"]:+.2f}%
                                </div>

                            </div>

                        </div>


                        <div style="
                            font-size:.65rem;
                            color:#71869a;
                            margin-top:5px;
                        ">

                            추세

                            <span class="{trend_cls}">
                                {item["trend"]}
                            </span>

                        </div>

                    </div>
                    """,

                    unsafe_allow_html=True
                )


                if st.button(

                    "ETF 분석",

                    key=(
                        f"theme_an_"
                        f"{theme_index}_"
                        f"{i}_"
                        f"{item['code']}"
                    ),

                    use_container_width=True
                ):

                    st.session_state.selected_code = (
                        item["code"]
                    )

                    st.session_state.main_page = (
                        "📊 내 ETF"
                    )

                    st.rerun()


    # ========================================================
    # SUMMARY
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
                x["ret"]
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
                x["vr"]
                for x in rows
            ]
        )


        summary_rows.append(

            {
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
            }
        )


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
# HEADER
# ============================================================

st.markdown(

    """
    <div class="app-header">

        <div class="app-title">
            ETF RADAR
        </div>

        <div class="app-subtitle">
            ETF 추세 · 모멘텀 · 거래량 · 핵심가격 · 대응 시나리오
        </div>

    </div>
    """,

    unsafe_allow_html=True
)


# ============================================================
# NAV
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