# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import json
import os
import html
from datetime import datetime


# ============================================================
# ETF RADAR
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

CSS = r"""
<style>

:root {
    --bg: #07111f;
    --panel: #0d1928;
    --panel2: #111f31;
    --text: #e3eaf2;
    --muted: #8193a7;
    --blue: #62aef2;
    --green: #39c99a;
    --red: #ef6678;
    --yellow: #d5ae58;
    --border: #22384d;
}


/* ==========================================================
   GLOBAL
   ========================================================== */

html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {

    background: #07111f !important;
    color: #e3eaf2 !important;

    font-family:
        "Noto Sans KR",
        "Noto Sans CJK KR",
        "Apple SD Gothic Neo",
        "Malgun Gothic",
        "Nanum Gothic",
        Arial,
        sans-serif !important;
}


.block-container {
    max-width: 1180px !important;
    padding: 8px 10px 30px !important;
}


/* ==========================================================
   ALL TEXT
   ========================================================== */

.stApp p,
.stApp span,
.stApp label,
.stApp div {

    font-family:
        "Noto Sans KR",
        "Noto Sans CJK KR",
        "Apple SD Gothic Neo",
        "Malgun Gothic",
        "Nanum Gothic",
        Arial,
        sans-serif !important;
}


/* ==========================================================
   SELECTBOX
   ========================================================== */

/*
   핵심 수정:
   BaseWeb selectbox의 내부 텍스트까지 동일한 폰트를 강제합니다.
*/

div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {

    font-family:
        "Noto Sans KR",
        "Noto Sans CJK KR",
        "Apple SD Gothic Neo",
        "Malgun Gothic",
        "Nanum Gothic",
        Arial,
        sans-serif !important;

    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}


div[data-baseweb="select"] > div {

    background: #0c1928 !important;
    border-color: #294159 !important;
}


/* dropdown menu */

div[data-baseweb="popover"],
div[data-baseweb="popover"] *,
div[data-baseweb="menu"],
div[data-baseweb="menu"] *,
ul[role="listbox"],
ul[role="listbox"] *,
li[role="option"],
li[role="option"] * {

    font-family:
        "Noto Sans KR",
        "Noto Sans CJK KR",
        "Apple SD Gothic Neo",
        "Malgun Gothic",
        "Nanum Gothic",
        Arial,
        sans-serif !important;

    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}


div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"] {

    background: #0b1725 !important;
}


li[role="option"] {

    background: #0b1725 !important;
}


li[role="option"]:hover,
li[role="option"][aria-selected="true"] {

    background: #172a3e !important;
}


/* ==========================================================
   INPUT
   ========================================================== */

div[data-baseweb="input"],
div[data-baseweb="input"] > div {

    background: #0c1928 !important;
    border-color: #294159 !important;
}


div[data-baseweb="input"] input {

    background: transparent !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}


div[data-baseweb="input"] input::placeholder {

    color: #8296aa !important;
    opacity: 1 !important;
}


/* ==========================================================
   BUTTON
   ========================================================== */

.stButton > button {

    background: #122236 !important;
    color: #dce5ee !important;

    border: 1px solid #29445d !important;

    border-radius: 8px !important;

    font-weight: 750 !important;

    min-height: 36px !important;
}


.stButton > button:hover {

    background: #18314a !important;
    border-color: #4a7fa8 !important;
    color: #ffffff !important;
}


/* ==========================================================
   HEADER
   ========================================================== */

.app-header {

    padding: 4px 0 10px;
}


.app-title {

    font-size: 1.45rem;
    line-height: 1.1;

    font-weight: 850;

    color: #e5edf5 !important;
}


.app-subtitle {

    font-size: 0.73rem;

    color: #74889d !important;

    margin-top: 3px;
}


/* ==========================================================
   HERO
   ========================================================== */

.hero {

    background: #0d1928;

    border: 1px solid #263e54;

    border-radius: 12px;

    padding: 14px;

    margin-bottom: 10px;
}


.hero-name {

    font-size: 1.15rem;

    font-weight: 800;

    color: #e0e8f0 !important;
}


.hero-code {

    font-size: 0.70rem;

    color: #73879b !important;

    margin-top: 2px;
}


.quote-row {

    display: flex;

    gap: 12px;

    align-items: baseline;

    margin-top: 9px;
}


.quote-price {

    font-size: 1.72rem;

    font-weight: 850;

    color: #e6edf4 !important;
}


.quote-change {

    font-size: 0.84rem;

    font-weight: 750;
}


.hero-date {

    font-size: 0.68rem;

    color: #71859a !important;

    margin-top: 7px;
}


/* ==========================================================
   COLORS
   ========================================================== */

.positive {
    color: #39c99a !important;
}

.negative {
    color: #ef6678 !important;
}

.neutral {
    color: #a8b7c6 !important;
}


/* ==========================================================
   SECTION
   ========================================================== */

.section-title {

    font-size: 0.90rem;

    font-weight: 800;

    color: #cdd8e3 !important;

    margin: 15px 0 7px;
}


/* ==========================================================
   EVIDENCE
   ========================================================== */

.evidence-grid {

    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 6px;

    margin: 6px 0 9px;
}


.evidence-box {

    background: #0b1725;

    border: 1px solid #20374c;

    border-radius: 8px;

    padding: 8px;
}


.evidence-label {

    font-size: 0.64rem;

    color: #74879b !important;
}


.evidence-value {

    font-size: 0.86rem;

    font-weight: 800;

    color: #cdd8e3 !important;

    margin-top: 2px;
}


.evidence-sub {

    font-size: 0.62rem;

    color: #71859a !important;

    margin-top: 2px;
}


/* ==========================================================
   JUDGMENT
   ========================================================== */

.judgment-box,
.action-box {

    background: #0d1928;

    border: 1px solid #22394e;

    border-radius: 9px;

    padding: 11px;

    min-height: 112px;
}


.judgment-box {

    border-left: 3px solid #4b8bbd;
}


.action-box {

    border-left: 3px solid #90763c;
}


.judgment-title,
.action-title {

    font-size: 0.66rem;

    color: #75899d !important;

    font-weight: 750;
}


.action-title {

    color: #b59a5a !important;
}


.judgment-main {

    font-size: 0.96rem;

    line-height: 1.3;

    font-weight: 800;

    color: #d6e0e9 !important;

    margin-top: 4px;
}


.judgment-reason,
.action-main {

    font-size: 0.74rem;

    line-height: 1.48;

    color: #aab9c8 !important;

    margin-top: 7px;
}


.reason-label {

    color: #6f8499 !important;

    font-size: 0.64rem;

    font-weight: 750;

    margin-bottom: 3px;
}


.action-reason-label {

    color: #a48b50 !important;

    font-size: 0.64rem;

    font-weight: 750;

    margin-bottom: 3px;
}


/* ==========================================================
   HOLDING
   ========================================================== */

.holding-box {

    background: #0b1725;

    border: 1px solid #20374c;

    border-radius: 8px;

    padding: 9px;
}


.holding-value {

    font-size: 0.84rem;

    font-weight: 800;

    color: #ccd7e1 !important;
}


.holding-detail {

    font-size: 0.69rem;

    color: #8294a7 !important;

    margin-top: 3px;
}


/* ==========================================================
   FUTURE THEME
   ========================================================== */

.theme-card-lead {

    background:
        linear-gradient(
            135deg,
            #0d2238 0%,
            #0d1928 100%
        );

    border: 1px solid #2a5278;

    border-left: 4px solid #39c99a;

    border-radius: 10px;

    padding: 12px;

    margin-bottom: 7px;
}


.theme-card-next {

    background:
        linear-gradient(
            135deg,
            #1f1b11 0%,
            #0d1928 100%
        );

    border: 1px solid #5a4b28;

    border-left: 4px solid #d5ae58;

    border-radius: 10px;

    padding: 12px;

    margin-bottom: 7px;
}


.theme-card-early {

    background:
        linear-gradient(
            135deg,
            #121c2e 0%,
            #0d1928 100%
        );

    border: 1px solid #2c4464;

    border-left: 4px solid #62aef2;

    border-radius: 10px;

    padding: 12px;

    margin-bottom: 7px;
}


.theme-stage {

    font-size: 0.65rem;

    font-weight: 800;
}


.theme-title {

    font-size: 0.98rem;

    font-weight: 800;

    color: #d2dde7 !important;

    margin-top: 2px;
}


.theme-reason {

    font-size: 0.71rem;

    color: #899bab !important;

    line-height: 1.42;

    margin: 4px 0 8px;
}


/* ==========================================================
   ETF CARD
   ========================================================== */

.theme-etf-box {

    background: #0b1725;

    border: 1px solid #1f3549;

    border-radius: 8px;

    padding: 9px;

    min-height: 145px;
}


.theme-etf-name {

    font-size: 0.76rem;

    line-height: 1.3;

    font-weight: 800;

    color: #d0dbe5 !important;
}


.theme-etf-code {

    font-size: 0.62rem;

    color: #708398 !important;

    margin-top: 2px;
}


.theme-data-grid {

    display: grid;

    grid-template-columns:
        repeat(2, 1fr);

    gap: 4px;

    margin-top: 7px;
}


.theme-data-item {

    background: #091522;

    border-radius: 5px;

    padding: 5px;
}


.theme-data-label {

    font-size: 0.57rem;

    color: #6f8296 !important;
}


.theme-data-value {

    font-size: 0.70rem;

    font-weight: 800;

    color: #bdcad6 !important;

    margin-top: 1px;
}


/* ==========================================================
   ANALYSIS PANEL
   ========================================================== */

.future-analysis-panel {

    background: #0a1523;

    border: 1px solid #2d4c6a;

    border-radius: 10px;

    padding: 11px;

    margin-top: 8px;

    margin-bottom: 8px;
}


.future-analysis-title {

    font-size: 0.92rem;

    font-weight: 850;

    color: #dce6ef !important;
}


/* ==========================================================
   MOBILE
   ========================================================== */

@media (max-width: 700px) {

    .block-container {

        padding:
            7px 8px 24px !important;
    }


    .evidence-grid {

        gap: 4px;
    }


    .evidence-box {

        padding: 7px 5px;
    }


    .evidence-value {

        font-size: 0.78rem;
    }


    .theme-etf-box {

        min-height: 0;
    }

}

</style>
"""

st.html(CSS)


# ============================================================
# FILES
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"
UNIVERSE_FILE = "etf_universe_cache.json"


# ============================================================
# BASE ETF
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
    "130730": "KOSEF 단기자금",
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

    "AI반도체·핵심장비": {
        "stage": "현재주도",
        "badge_class": "theme-card-lead",
        "stage_color": "#39c99a",
        "keywords": [
            "AI반도체",
            "반도체",
            "AI",
            "HBM",
            "반도체장비",
            "포커스"
        ],
        "seeds": [
            "395160",
            "487240",
            "471990",
            "469150"
        ],
        "reason":
            "AI 하드웨어 연산 수요와 HBM·미세공정 장비 투자 확대의 핵심 영역입니다."
    },

    "미국 빅테크 & 혁신": {
        "stage": "현재주도",
        "badge_class": "theme-card-lead",
        "stage_color": "#39c99a",
        "keywords": [
            "나스닥",
            "S&P500",
            "테크TOP10",
            "미국테크"
        ],
        "seeds": [
            "133690",
            "360750",
            "381170"
        ],
        "reason":
            "글로벌 AI 생태계의 중심인 미국 빅테크와 혁신기업을 중심으로 보는 주도 영역입니다."
    },

    "데이터센터·AI 인프라": {
        "stage": "다음수혜",
        "badge_class": "theme-card-next",
        "stage_color": "#d5ae58",
        "keywords": [
            "데이터센터",
            "AI인프라",
            "글로벌AI인프라"
        ],
        "seeds": [
            "449170",
            "434060"
        ],
        "reason":
            "AI 확산에 따른 데이터센터·서버·네트워크 인프라 확대의 수혜 영역입니다."
    },

    "전력 인프라 & 설비": {
        "stage": "다음수혜",
        "badge_class": "theme-card-next",
        "stage_color": "#d5ae58",
        "keywords": [
            "전력",
            "전력인프라",
            "전력핵심설비",
            "전력설비"
        ],
        "seeds": [
            "464240",
            "487130"
        ],
        "reason":
            "AI 데이터센터 전력수요 증가에 따른 전력망·변압기·핵심설비 투자 영역입니다."
    },

    "바이오·헬스케어 혁신": {
        "stage": "다음수혜",
        "badge_class": "theme-card-next",
        "stage_color": "#d5ae58",
        "keywords": [
            "바이오",
            "헬스케어",
            "제약"
        ],
        "seeds": [
            "364690"
        ],
        "reason":
            "신약개발과 헬스케어 산업의 장기 성장성을 관찰하는 영역입니다."
    },

    "로보틱스 & AI 자율주행": {
        "stage": "초기관심",
        "badge_class": "theme-card-early",
        "stage_color": "#62aef2",
        "keywords": [
            "로봇",
            "로보틱스",
            "자율주행",
            "AI&로봇"
        ],
        "seeds": [
            "458730"
        ],
        "reason":
            "제조자동화와 로봇 산업 확대에 따른 장기 성장 영역입니다."
    },

    "우주항공 & 방산": {
        "stage": "초기관심",
        "badge_class": "theme-card-early",
        "stage_color": "#62aef2",
        "keywords": [
            "우주",
            "방산",
            "항공",
            "우주항공"
        ],
        "seeds": [
            "364690"
        ],
        "reason":
            "우주·위성 및 글로벌 방산 투자 확대에 따른 장기 관심 영역입니다."
    },

    "SMR·원자력 에너지": {
        "stage": "초기관심",
        "badge_class": "theme-card-early",
        "stage_color": "#62aef2",
        "keywords": [
            "원자력",
            "원전",
            "SMR",
            "에너지"
        ],
        "seeds": [
            "130730",
            "161510"
        ],
        "reason":
            "AI 데이터센터 전력수요 증가와 원전·SMR에 대한 장기 관심 영역입니다."
    }
}


FUTURE_CHAIN = [
    (
        "현재주도",
        [
            "AI반도체·핵심장비",
            "미국 빅테크 & 혁신"
        ]
    ),
    (
        "다음수혜",
        [
            "데이터센터·AI 인프라",
            "전력 인프라 & 설비",
            "바이오·헬스케어 혁신"
        ]
    ),
    (
        "초기관심",
        [
            "로보틱스 & AI 자율주행",
            "우주항공 & 방산",
            "SMR·원자력 에너지"
        ]
    )
]


# ============================================================
# HELPERS
# ============================================================

def clean_text(text):

    if not isinstance(text, str):
        return str(text)

    return text


def esc(value):

    return html.escape(
        str(value)
    )


def read_json(path, default):

    try:

        if not os.path.exists(path):
            return default

        with open(
            path,
            "r",
            encoding="utf-8-sig"
        ) as f:

            data = json.load(f)

        return (
            data
            if data is not None
            else default
        )

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

            code = (
                str(code)
                .strip()
                .zfill(6)
            )

            if not code or not name:
                continue

            if isinstance(
                name,
                dict
            ):

                name = name.get(
                    "name",
                    f"ETF {code}"
                )

            universe[code] = clean_text(
                str(name)
            )


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

            code = item.get("code")
            name = item.get("name")

            if not code or not name:
                continue

            universe[
                str(code)
                .strip()
                .zfill(6)
            ] = clean_text(
                str(name)
            )


    return universe


def init_state():

    if "watchlist" not in st.session_state:

        saved = read_json(
            WATCHLIST_FILE,
            DEFAULT_WATCHLIST.copy()
        )

        if (
            isinstance(saved, list)
            and saved
        ):

            st.session_state.watchlist = [
                str(x)
                .strip()
                .zfill(6)

                for x in saved
                if x
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
            if isinstance(
                saved,
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

            else "395160"
        )


    if "main_nav" not in st.session_state:

        st.session_state.main_nav = (
            "📊 내 ETF"
        )


    if "main_nav_target" not in st.session_state:

        st.session_state.main_nav_target = None


    if "future_detail_code" not in st.session_state:

        st.session_state.future_detail_code = None


    if "theme_last_update" not in st.session_state:

        st.session_state.theme_last_update = None


def get_etf_name(code):

    code = (
        str(code)
        .strip()
        .zfill(6)
    )

    name = (

        BASE_ETFS.get(code)

        or st.session_state.etf_universe.get(code)

        or f"ETF {code}"
    )


    if isinstance(
        name,
        dict
    ):

        name = name.get(
            "name",
            f"ETF {code}"
        )


    return clean_text(
        str(name)
    )


# ============================================================
# DATA
# ============================================================

def normalize_df(df):

    if df is None or df.empty:
        return pd.DataFrame()


    df = df.copy()


    if isinstance(
        df.columns,
        pd.MultiIndex
    ):

        new_columns = []

        for col in df.columns:

            if isinstance(
                col,
                tuple
            ):

                found = None

                for item in col:

                    item_str = str(item)

                    if item_str.lower() in [
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume"
                    ]:

                        found = (
                            item_str.capitalize()
                        )

                        break

                new_columns.append(
                    found
                    if found
                    else str(col[0])
                )

            else:

                new_columns.append(
                    str(col)
                )


        df.columns = new_columns


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
        "Volume"
    ]


    if not all(
        col in df.columns
        for col in required
    ):

        return pd.DataFrame()


    df = df[required].copy()


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

        code = (
            str(code)
            .strip()
            .zfill(6)
        )


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

    code = (
        str(code)
        .strip()
        .zfill(6)
    )


    now = datetime.now()


    cached = (
        st.session_state
        .price_cache
        .get(code)
    )


    if cached and not force:

        if (
            now - cached["time"]
        ).total_seconds() < 300:

            return cached["data"]


    df = fetch_yahoo(code)


    if not df.empty:

        st.session_state.price_cache[code] = {

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
        delta.clip(lower=0)
        .rolling(14)
        .mean()
    )


    loss = (
        (-delta)
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


    d["RSI14"] = (
        100 -
        (
            100 /
            (1 + rs)
        )
    )


    d["VOL20"] = (
        d["Volume"]
        .rolling(20)
        .mean()
    )


    d["VOL_RATIO"] = (
        d["Volume"] /
        d["VOL20"]
        .replace(0, np.nan)
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

    return f"{value:,.0f}원"


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
                "가격 데이터를 다시 확인해 주세요.",

            "ma_state":
                "확인 불가",

            "rsi_state":
                "확인 불가",

            "vol_state":
                "확인 불가",

            "rsi": 0,

            "vol_ratio": 0,

            "ret20": 0
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
        else
        "20일선 하회"
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
            "신규 매수는 추격보다 눌림 확인을 우선합니다."
        )


    elif above20 and above60:

        title = (
            "상승 추세 유지"
        )

        action = (
            "20일선과 60일선 위입니다. "
            "보유자는 추세를 확인하고 신규 매수는 눌림을 우선합니다."
        )


    elif above60 and not above20:

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
            "지지 형성과 거래량 회복을 확인합니다."
        )


    else:

        title = (
            "방향 확인 구간"
        )

        action = (
            "추세가 명확하지 않습니다. "
            "20일선 회복 또는 고점 돌파 여부를 확인합니다."
        )


    reasons = [

        f"현재가 {money(current)} · "
        f"20일선 {money(ma20)} · "
        f"{ma_state}",

        f"60일선 {money(ma60)} · "
        f"{'중기 추세 유지' if above60 else '중기 추세 약화'}",

        f"RSI14 {rsi:.1f} · "
        f"{rsi_state}",

        f"거래량 {vol_ratio:.2f}배 · "
        f"{vol_state} · "
        f"최근 20일 {ret20:+.2f}%"
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

        "ret20": ret20
    }


# ============================================================
# LEVELS
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

        "first": ma20,

        "support": min(
            ma60,
            low20
        ),

        "breakout": high20,

        "risk": min(
            ma60,
            low20,
            low60
        )
    }


# ============================================================
# JUDGMENT RENDER
# ============================================================

def render_judgment(d):

    judgment = get_judgment(d)


    st.markdown(
        '<div class="section-title">'
        '현재판단 · 지금대응'
        '</div>',
        unsafe_allow_html=True
    )


    rsi = judgment["rsi"]

    vr = judgment["vol_ratio"]


    ma_color = (
        "positive"
        if judgment["ma_state"]
        == "20일선 상회"
        else
        "negative"
    )


    rsi_color = (

        "positive"

        if rsi >= 60

        else

        (
            "negative"
            if rsi < 40
            else "neutral"
        )
    )


    vol_color = (

        "positive"

        if vr >= 1.1

        else

        (
            "negative"
            if vr < 0.8
            else "neutral"
        )
    )


    st.html(f"""

        <div class="evidence-grid">

            <div class="evidence-box">

                <div class="evidence-label">
                    20일선
                </div>

                <div class="evidence-value {ma_color}">
                    {esc(judgment["ma_state"])}
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
                    {esc(judgment["rsi_state"])}
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
                    {esc(judgment["vol_state"])}
                </div>

            </div>

        </div>

    """)


    c1, c2 = st.columns(2)


    with c1:

        reasons_html = "<br>".join(
            esc(x)
            for x in judgment["reasons"]
        )


        st.html(f"""

            <div class="judgment-box">

                <div class="judgment-title">
                    현재판단
                </div>

                <div class="judgment-main">
                    {esc(judgment["title"])}
                </div>

                <div class="reason-label">
                    판단근거
                </div>

                <div class="judgment-reason">
                    {reasons_html}
                </div>

            </div>

        """)


    with c2:

        st.html(f"""

            <div class="action-box">

                <div class="action-title">
                    지금대응
                </div>

                <div class="action-main">
                    {esc(judgment["action"])}
                </div>

                <div class="action-reason-label">
                    대응근거
                </div>

                <div class="judgment-reason">
                    추격보다는 눌림 또는 확인 후 대응을 우선합니다.
                </div>

            </div>

        """)


# ============================================================
# SCENARIOS
# ============================================================

def render_scenarios(d):

    levels = calculate_levels(d)

    if not levels:
        return


    st.markdown(
        "### 핵심가격 · 대응 시나리오"
    )


    cards = [

        {
            "label": "① 1차 관심",
            "price": levels["first"],
            "condition": "20일선 부근 눌림",
            "meaning": "단기 상승 추세 유지 확인",
            "action": "20일선에서 지지되는지 확인"
        },

        {
            "label": "② 핵심 지지",
            "price": levels["support"],
            "condition": "중기 추세 방어",
            "meaning": "최근 저점 및 중기 이평선 기준",
            "action": "지지 확인 후 분할 대응"
        },

        {
            "label": "③ 돌파 기준",
            "price": levels["breakout"],
            "condition": "최근 20일 고점 돌파",
            "meaning": "새로운 단기 고점 형성 기준",
            "action": "거래량 증가 동반 여부 확인"
        },

        {
            "label": "④ 위험 가격",
            "price": levels["risk"],
            "condition": "핵심 지지 이탈",
            "meaning": "중기 추세 약화 가능성",
            "action": "지지 회복 전까지 보수적 접근"
        }

    ]


    cols = st.columns(4)


    for col, card in zip(
        cols,
        cards
    ):

        with col:

            with st.container(
                border=True
            ):

                st.markdown(
                    f"**{card['label']}**"
                )

                st.markdown(
                    f"### {money(card['price'])}"
                )

                st.caption(
                    card["condition"]
                )

                st.markdown(
                    f"**의미**  \n"
                    f"{card['meaning']}"
                )

                st.markdown(
                    f"**대응**  \n"
                    f"{card['action']}"
                )


# ============================================================
# CHART
# ============================================================

def render_chart(d):

    if d.empty:
        return


    chart_df = d.tail(126).copy()


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


    volume_colors = np.where(

        chart_df["Close"]
        >=
        chart_df["Open"],

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


    fig.update_xaxes(
        fixedrange=True,
        showgrid=False,
        rangeslider_visible=False
    )


    fig.update_yaxes(
        fixedrange=True,
        gridcolor="#17283a",
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
            xanchor="right"
        ),

        dragmode=False,

        hovermode=False
    )


    st.plotly_chart(

        fig,

        use_container_width=True,

        config={
            "displayModeBar": False,
            "responsive": True,
            "staticPlot": True
        }
    )


# ============================================================
# ETF SEARCH
# ============================================================

def search_etfs(query):

    query = (
        query or ""
    ).strip().lower()


    if not query:
        return []


    results = []


    for code, name in (
        st.session_state
        .etf_universe
        .items()
    ):

        code = (
            str(code)
            .strip()
            .zfill(6)
        )


        name_str = clean_text(
            str(name)
        )


        if (
            query in code.lower()
            or
            query in name_str.lower()
        ):

            results.append({

                "code": code,

                "name": name_str
            })


    return results[:30]


# ============================================================
# SEARCH DISPLAY STRING
# ============================================================

def make_search_option(
    code,
    name=None
):

    code = (
        str(code)
        .strip()
        .zfill(6)
    )


    if name is None:
        name = get_etf_name(code)


    # 중요:
    # 특수문자 · 대신 일반 ASCII 구분자를 사용합니다.
    return f"{name} [{code}]"


def code_from_search_option(
    value
):

    if not value:
        return ""


    text = str(value).strip()


    if "[" in text and "]" in text:

        code = (
            text.rsplit(
                "[",
                1
            )[-1]
            .replace(
                "]",
                ""
            )
            .strip()
        )

        return code.zfill(6)


    return text[:6].zfill(6)


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

        "ETF명 또는 종목코드",

        placeholder="예: AI반도체 / 395160",

        label_visibility="collapsed",

        key="search_q"
    )


    results = search_etfs(query)


    if results:

        # ====================================================
        # 핵심 수정
        #
        # 기존:
        # selectbox(options=[dict, dict, dict])
        #
        # 변경:
        # selectbox(options=["KODEX ... [395160]", ...])
        #
        # 따라서 BaseWeb이 dict를 렌더링하는 과정 자체가 없습니다.
        # ====================================================

        search_options = [

            make_search_option(
                item["code"],
                item["name"]
            )

            for item in results
        ]


        # 검색 결과가 바뀌어 이전 선택값이 존재하지 않으면 초기화
        old_value = st.session_state.get(
            "search_result_display"
        )


        if (
            old_value is not None
            and old_value not in search_options
        ):

            del st.session_state[
                "search_result_display"
            ]


        selected_display = st.selectbox(

            "검색 결과",

            search_options,

            key="search_result_display"
        )


        code = code_from_search_option(
            selected_display
        )


        name = get_etf_name(code)


        st.html(f"""

            <div class="holding-box">

                <div class="holding-value">
                    {esc(name)}
                </div>

                <div class="holding-detail">
                    종목코드 {esc(code)}
                </div>

            </div>

        """)


        st.write("")


        c1, c2 = st.columns(
            [3, 1]
        )


        with c1:

            if code in (
                st.session_state.watchlist
            ):

                st.info(
                    f"「{name}」은 현재 관심종목에 등록되어 있습니다."
                )

            else:

                st.caption(
                    "관심종목에 추가하여 바로 분석할 수 있습니다."
                )


        with c2:

            if st.button(

                "추가",

                use_container_width=True,

                key=f"finder_add_{code}"

            ):

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


                st.session_state.selected_code = code

                st.rerun()


    elif query:

        st.caption(
            "검색 결과가 없습니다."
        )


# ============================================================
# WATCHLIST
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


    # ========================================================
    # 검색 드롭다운과 동일하게
    # selectbox에는 dict를 넣지 않고 문자열만 넣습니다.
    # ========================================================

    watch_options = [

        make_search_option(
            code
        )

        for code in watchlist
    ]


    current = (
        str(
            st.session_state.selected_code
        )
        .strip()
        .zfill(6)
    )


    current_display = make_search_option(
        current
    )


    if current_display in watch_options:

        default_index = (
            watch_options.index(
                current_display
            )
        )

    else:

        default_index = 0


    # 위젯 생성 전에 현재 상태를 맞춥니다.
    if (
        st.session_state.get(
            "watch_select_display"
        )
        not in watch_options
    ):

        st.session_state.watch_select_display = (
            watch_options[default_index]
        )


    selected_display = st.selectbox(

        "관심종목 선택",

        watch_options,

        key="watch_select_display"
    )


    selected_code = code_from_search_option(
        selected_display
    )


    st.session_state.selected_code = (
        selected_code
    )


    if st.button(

        "현재 ETF 관심종목에서 삭제",

        use_container_width=True,

        key="remove_watch"

    ):

        remove_code = selected_code


        if remove_code in watchlist:

            watchlist.remove(
                remove_code
            )


            write_json(

                WATCHLIST_FILE,

                watchlist
            )


            if watchlist:

                st.session_state.selected_code = (
                    watchlist[0]
                )

            else:

                st.session_state.selected_code = (
                    "395160"
                )


            st.session_state.pop(
                "watch_select_display",
                None
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

        index=(
            1
            if old
            else 0
        ),

        horizontal=True,

        key=f"held_{code}"
    )


    if held == "보유중":

        c1, c2 = st.columns(2)


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

            st.session_state.holdings[code] = {

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
                current / avg - 1
            ) * 100


            cls = (
                "positive"
                if pnl >= 0
                else
                "negative"
            )


            st.html(f"""

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

            """)


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
            "가격 데이터를 불러오지 못했습니다."
        )

        return


    d = calculate_indicators(
        df
    )


    if d.empty:
        return


    current = safe_float(
        d["Close"].iloc[-1]
    )


    previous = (

        safe_float(
            d["Close"].iloc[-2]
        )

        if len(d) >= 2

        else current
    )


    change = (
        current - previous
    )


    change_pct = (

        change / previous * 100

        if previous != 0

        else 0
    )


    cls = (

        "positive"

        if change > 0

        else

        (
            "negative"
            if change < 0
            else "neutral"
        )
    )


    date_text = (
        d.index[-1]
        .strftime("%Y-%m-%d")
    )


    st.html(f"""

        <div class="hero">

            <div class="hero-name">
                {esc(name)}
            </div>

            <div class="hero-code">
                {esc(code)}
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
                기준일 {esc(date_text)}
            </div>

        </div>

    """)


    render_holdings(
        code,
        current
    )


    render_judgment(
        d
    )


    render_scenarios(
        d
    )


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
# FUTURE THEME
# ============================================================

def theme_candidates(theme):

    info = THEMES[theme]

    result = []

    used = set()


    for code in info["seeds"]:

        code = (
            str(code)
            .strip()
            .zfill(6)
        )


        if code not in used:

            result.append({

                "code": code,

                "name": get_etf_name(code)
            })


            used.add(code)


    for code, name in (
        st.session_state
        .etf_universe
        .items()
    ):

        code = (
            str(code)
            .strip()
            .zfill(6)
        )


        name_str = clean_text(
            str(name)
        )


        text = (
            f"{code} {name_str}"
        ).lower()


        if any(

            keyword.lower()
            in text

            for keyword
            in info["keywords"]

        ):

            if code not in used:

                result.append({

                    "code": code,

                    "name": name_str
                })


                used.add(code)


    return result[:3]


def theme_snapshot(
    theme,
    force=False
):

    cached = (
        st.session_state
        .theme_cache
        .get(theme)
    )


    now = datetime.now()


    if cached and not force:

        if (
            now - cached["time"]
        ).total_seconds() < 300:

            return cached["rows"]


    rows = []


    for item in theme_candidates(
        theme
    ):

        code = item["code"]


        df = load_price_data(
            code,
            force=force
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


        rows.append({

            "code": code,

            "name": item["name"],

            "price": current,

            "rsi": safe_float(
                row["RSI14"],
                50
            ),

            "vr": safe_float(
                row["VOL_RATIO"],
                1
            ),

            "ret": safe_float(
                row["RET20"],
                0
            ),

            "trend": (

                "상승"

                if current >= safe_float(
                    row["MA20"],
                    current
                )

                else "조정"
            )
        })


    st.session_state.theme_cache[
        theme
    ] = {

        "time": now,

        "rows": rows
    }


    return rows


def refresh_future_themes():

    st.session_state.theme_cache = {}

    st.session_state.theme_last_update = (
        datetime.now()
    )


# ============================================================
# ★ FUTURE ETF DETAIL
# ============================================================

def render_future_detail(
    item
):

    code = item["code"]

    name = item["name"]


    # --------------------------------------------------------
    # 여기서부터는 "방금 누른 카드" 바로 아래에 렌더링됩니다.
    # --------------------------------------------------------

    st.markdown(
        '<div class="future-analysis-panel">',
        unsafe_allow_html=True
    )


    st.markdown(
        f"""
        <div class="future-analysis-title">
            🔍 {esc(name)}
            ({esc(code)})
            · 정밀 분석
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


    if st.button(

        "📊 내 ETF 화면으로 이동",

        key=f"future_move_{code}",

        use_container_width=True

    ):

        st.session_state.selected_code = code

        st.session_state.future_detail_code = None

        # main_nav 위젯을 직접 수정하지 않습니다.
        st.session_state.main_nav_target = (
            "📊 내 ETF"
        )

        st.rerun()


    df_detail = load_price_data(
        code
    )


    if df_detail.empty:

        st.warning(
            "해당 ETF의 가격 데이터를 불러오지 못했습니다."
        )

        return


    d_detail = calculate_indicators(
        df_detail
    )


    if d_detail.empty:

        st.warning(
            "분석에 필요한 데이터가 부족합니다."
        )

        return


    render_judgment(
        d_detail
    )


    render_scenarios(
        d_detail
    )


    st.markdown(
        '<div class="section-title">'
        '가격 흐름 · 최근 6개월'
        '</div>',
        unsafe_allow_html=True
    )


    render_chart(
        d_detail
    )


# ============================================================
# FUTURE THEME PAGE
# ============================================================

def render_future_theme():

    st.html("""

        <div class="hero">

            <div class="hero-name">
                미래테마 대시보드
            </div>

            <div class="hero-code">
                현재 주도 → 다음 수혜 → 초기 관심
                순서로 AI 산업 밸류체인을 추적합니다.
            </div>

        </div>

    """)


    update_time = (
        st.session_state.theme_last_update
    )


    update_text = (

        update_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        if update_time

        else
        "아직 업데이트 안됨"
    )


    c1, c2 = st.columns(
        [3, 1]
    )


    with c1:

        st.html(f"""

            <div class="holding-box">

                <div class="holding-value">
                    테마 데이터 기준 시각
                </div>

                <div class="holding-detail">
                    {esc(update_text)}
                </div>

            </div>

        """)


    with c2:

        if st.button(

            "🔄 전체 테마 갱신",

            use_container_width=True,

            key="refresh_future_theme"

        ):

            refresh_future_themes()

            st.rerun()


    # ========================================================
    # 현재 선택된 ETF
    # ========================================================

    current_detail = (
        st.session_state.get(
            "future_detail_code"
        )
    )


    for stage_name, theme_names in FUTURE_CHAIN:

        st.markdown(
            f"### 📍 [{stage_name}] 핵심 테마군"
        )


        for theme in theme_names:

            info = THEMES[theme]


            st.html(f"""

                <div class="{info['badge_class']}">

                    <div
                        class="theme-stage"
                        style="color:{info['stage_color']};"
                    >
                        STAGE: {esc(stage_name)}
                    </div>

                    <div class="theme-title">
                        {esc(theme)}
                    </div>

                    <div class="theme-reason">
                        {esc(info['reason'])}
                    </div>

                </div>

            """)


            rows = theme_snapshot(
                theme
            )


            if not rows:

                st.caption(
                    "표시 가능한 ETF 데이터가 없습니다."
                )

                continue


            # =================================================
            # ETF 카드 3개
            # =================================================

            cols = st.columns(
                len(rows)
            )


            for i, item in enumerate(rows):

                with cols[i]:

                    ret_cls = (

                        "positive"

                        if item["ret"] >= 0

                        else
                        "negative"
                    )


                    trend_cls = (

                        "positive"

                        if item["trend"] == "상승"

                        else
                        "negative"
                    )


                    # -----------------------------------------
                    # ETF 카드
                    # -----------------------------------------

                    st.html(f"""

                        <div class="theme-etf-box">

                            <div class="theme-etf-name">
                                {esc(item["name"])}
                            </div>

                            <div class="theme-etf-code">
                                {esc(item["code"])}
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


                            <div
                                style="
                                    font-size:.64rem;
                                    color:#71869a;
                                    margin-top:5px;
                                "
                            >
                                추세

                                <span class="{trend_cls}">
                                    {esc(item["trend"])}
                                </span>

                            </div>

                        </div>

                    """)


                    # =================================================
                    # 분석 버튼
                    # =================================================

                    is_active = (
                        current_detail
                        == item["code"]
                    )


                    button_text = (

                        "분석 닫기"

                        if is_active

                        else
                        "ETF 분석"
                    )


                    if st.button(

                        button_text,

                        key=(
                            f"future_analysis_"
                            f"{theme}_"
                            f"{item['code']}"
                        ),

                        use_container_width=True
                    ):

                        if is_active:

                            st.session_state.future_detail_code = None

                        else:

                            st.session_state.future_detail_code = (
                                item["code"]
                            )

                        st.rerun()


                    # =================================================
                    # ★ 핵심 수정 부분
                    #
                    # 절대로 여기 바깥에서 분석 결과를 그리지 않습니다.
                    #
                    # 방금 누른 카드의 with cols[i] 안에서
                    # 바로 render_future_detail()을 호출합니다.
                    # =================================================

                    if (
                        st.session_state.get(
                            "future_detail_code"
                        )
                        == item["code"]
                    ):

                        render_future_detail(
                            item
                        )


            st.write("")


# ============================================================
# INITIALIZE
# ============================================================

init_state()


# ============================================================
# NAVIGATION TARGET
#
# 위젯이 생성되기 전에 적용해야 합니다.
# ============================================================

if st.session_state.get(
    "main_nav_target"
):

    st.session_state.main_nav = (
        st.session_state.main_nav_target
    )

    st.session_state.main_nav_target = None


# ============================================================
# HEADER
# ============================================================

st.html("""

    <div class="app-header">

        <div class="app-title">
            ETF RADAR
        </div>

        <div class="app-subtitle">
            ETF 추세 · 모멘텀 · 거래량 · 핵심가격 · 대응 시나리오
        </div>

    </div>

""")


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

    key="main_nav",

    label_visibility="collapsed"
)


# ============================================================
# PAGE
# ============================================================

if nav == "📊 내 ETF":

    render_my_etf()

else:

    render_future_theme()