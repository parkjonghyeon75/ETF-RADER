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
import re
from datetime import datetime
from urllib.parse import quote
from urllib.request import Request, urlopen


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
# HTML ESCAPE
# ============================================================

def esc(value):
    """동적 문자열의 HTML 깨짐 방지"""
    return html.escape(str(value))


# ============================================================
# CSS
# ============================================================

CSS = r"""
<style>

/* ==========================================================
   GLOBAL
   ========================================================== */

:root {
    --bg: #07111f;
    --bg2: #091522;
    --panel: #0d1928;
    --panel2: #111f31;
    --panel3: #16263a;

    --text: #e3eaf2;
    --text2: #c3cfdb;
    --muted: #8193a7;

    --blue: #62aef2;
    --green: #39c99a;
    --red: #ef6678;
    --yellow: #d5ae58;

    --border: #22384d;
    --border2: #29445d;
}


/* ==========================================================
   STREAMLIT BACKGROUND
   ========================================================== */

html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background: #07111f !important;
    color: #e3eaf2 !important;
}

[data-testid="stHeader"] {
    background: #07111f !important;
}

[data-testid="stToolbar"] {
    background: #07111f !important;
}

[data-testid="stSidebar"] {
    background: #091522 !important;
}

[data-testid="stSidebar"] * {
    color: #d7e1eb !important;
}


/* ==========================================================
   MAIN
   ========================================================== */

.block-container {
    max-width: 1180px !important;
    padding: 10px 12px 32px !important;
}


/* ==========================================================
   TEXT
   ========================================================== */

.stApp p {
    color: #c7d2de;
}

.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp h5,
.stApp h6 {
    color: #e3eaf2 !important;
}


/* ==========================================================
   INPUT
   ========================================================== */

div[data-baseweb="input"],
div[data-baseweb="input"] > div {
    background: #0c1928 !important;
    border-color: #294159 !important;
    color: #dce5ee !important;
}

div[data-baseweb="input"] input {
    background: transparent !important;
    color: #e3eaf2 !important;
    -webkit-text-fill-color: #e3eaf2 !important;
    caret-color: #62aef2 !important;
}

div[data-baseweb="input"] input::placeholder {
    color: #71859a !important;
    opacity: 1 !important;
}


/* ==========================================================
   SELECTBOX
   ========================================================== */

div[data-baseweb="select"],
div[data-baseweb="select"] > div {
    background: #0c1928 !important;
    color: #e3eaf2 !important;
    border-color: #294159 !important;
}

div[data-baseweb="select"] span {
    color: #dce5ee !important;
}

div[data-baseweb="popover"] {
    background: #0b1725 !important;
    border: 1px solid #294159 !important;
}

div[data-baseweb="menu"],
ul[role="listbox"] {
    background: #0b1725 !important;
}

li[role="option"] {
    background: #0b1725 !important;
    color: #dce5ee !important;
}

li[role="option"]:hover {
    background: #16283b !important;
    color: #ffffff !important;
}


/* ==========================================================
   RADIO
   ========================================================== */

div[data-testid="stRadio"] label,
div[data-testid="stRadio"] p {
    color: #c8d4df !important;
}


/* ==========================================================
   BUTTON
   ========================================================== */

.stButton > button {
    background: #122236 !important;
    color: #dce5ee !important;
    border: 1px solid #29445d !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    min-height: 36px !important;
    box-shadow: none !important;
}

.stButton > button:hover {
    background: #18314a !important;
    border-color: #4a7fa8 !important;
    color: #ffffff !important;
}

.stButton > button:disabled {
    background: #0d1928 !important;
    color: #5f7082 !important;
    border-color: #1d3043 !important;
}


/* ==========================================================
   ALERT
   ========================================================== */

[data-testid="stAlert"] {
    background: #0d1928 !important;
    border: 1px solid #263d53 !important;
    color: #cbd6e1 !important;
}

[data-testid="stAlert"] p {
    color: #cbd6e1 !important;
}


/* ==========================================================
   CAPTION
   ========================================================== */

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    color: #72869b !important;
}


/* ==========================================================
   APP HEADER
   ========================================================== */

.app-header {
    padding: 3px 0 10px;
}

.app-title {
    font-size: 1.45rem;
    line-height: 1.1;
    font-weight: 850;
    color: #e5edf5 !important;
}

.app-subtitle {
    font-size: 0.74rem;
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
    font-size: 1.16rem;
    line-height: 1.35;
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
    line-height: 1;
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
    grid-template-columns: repeat(3, 1fr);
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
   JUDGMENT / ACTION
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
   SCENARIO
   ========================================================== */

.scenario-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
}

.scenario-card {
    background: #0b1725;
    border: 1px solid #20374c;
    border-radius: 8px;
    padding: 9px;
}

.scenario-label {
    font-size: 0.63rem;
    color: #74879a !important;
}

.scenario-price {
    font-size: 0.92rem;
    font-weight: 800;
    color: #d1dce6 !important;
    margin-top: 3px;
}

.scenario-desc {
    font-size: 0.63rem;
    line-height: 1.38;
    color: #899bab !important;
    margin-top: 4px;
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

.theme-card {
    background: #0d1928;
    border: 1px solid #22394e;
    border-radius: 10px;
    padding: 11px;
    margin-bottom: 7px;
}

.theme-stage {
    display: inline-block;
    font-size: 0.64rem;
    font-weight: 800;
    padding: 3px 7px;
    border-radius: 999px;
    margin-bottom: 4px;
}

.theme-stage.stage-lead {
    color: #55d6a8 !important;
    background: rgba(57,201,154,.12);
    border: 1px solid rgba(57,201,154,.30);
}

.theme-stage.stage-next {
    color: #66aef0 !important;
    background: rgba(98,174,242,.12);
    border: 1px solid rgba(98,174,242,.30);
}

.theme-stage.stage-interest {
    color: #e0bb61 !important;
    background: rgba(213,174,88,.12);
    border: 1px solid rgba(213,174,88,.30);
}

.theme-stage.stage-early {
    color: #c28cff !important;
    background: rgba(194,140,255,.12);
    border: 1px solid rgba(194,140,255,.30);
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
    grid-template-columns: repeat(2, 1fr);
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
   FUTURE ANALYSIS
   ========================================================== */

.future-analysis {
    background: #0d1928;
    border: 1px solid #31516c;
    border-radius: 11px;
    padding: 12px;
    margin: 12px 0 10px;
}

.future-analysis-title {
    font-size: 0.68rem;
    color: #6ea7d1 !important;
    font-weight: 800;
}

.future-analysis-name {
    font-size: 1.02rem;
    font-weight: 800;
    color: #e0e8ef !important;
    margin-top: 2px;
}

.future-analysis-code {
    font-size: 0.64rem;
    color: #72879b !important;
}


/* ==========================================================
   SUMMARY TABLE
   ========================================================== */

.summary-table-wrap {
    width: 100%;
    overflow-x: auto;
    background: #0b1725;
    border: 1px solid #20374c;
    border-radius: 9px;
}

.summary-table {
    width: 100%;
    border-collapse: collapse;
    min-width: 500px;
}

.summary-table th {
    background: #101f31;
    color: #7f94a9;
    font-size: 0.64rem;
    font-weight: 750;
    text-align: left;
    padding: 8px 7px;
    border-bottom: 1px solid #233a50;
}

.summary-table td {
    background: #0b1725;
    color: #c4d0db;
    font-size: 0.68rem;
    padding: 8px 7px;
    border-bottom: 1px solid #172c40;
}

.summary-table tr:last-child td {
    border-bottom: none;
}

.summary-card {
    background: #0b1725;
    border: 1px solid #20374c;
    border-radius: 9px;
    padding: 9px;
    margin-bottom: 7px;
}

.summary-card-title {
    font-size: .76rem;
    font-weight: 800;
    color: #d6e0e9 !important;
}

.summary-card-meta {
    font-size: .62rem;
    color: #7d91a5 !important;
    margin-top: 2px;
}

.summary-card-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 5px;
    margin-top: 7px;
}

.summary-mini {
    background: #091522;
    border-radius: 5px;
    padding: 5px;
}

.summary-mini-label {
    font-size: .55rem;
    color: #6f8296 !important;
}

.summary-mini-value {
    font-size: .68rem;
    font-weight: 800;
    color: #c4d0db !important;
    margin-top: 1px;
}


/* ==========================================================
   STREAMLIT CONTAINERS
   ========================================================== */

[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="column"] {
    background: transparent !important;
}


/* ==========================================================
   EXPANDER
   ========================================================== */

[data-testid="stExpander"] {
    background: #0d1928 !important;
    border: 1px solid #22384d !important;
}

[data-testid="stExpander"] summary {
    color: #cbd7e2 !important;
}


/* ==========================================================
   TABS
   ========================================================== */

button[data-baseweb="tab"] {
    color: #8da0b3 !important;
    background: transparent !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #dce6ef !important;
}


/* ==========================================================
   MOBILE
   ========================================================== */

@media (max-width: 700px) {

    .block-container {
        padding: 7px 8px 24px !important;
    }

    .app-title {
        font-size: 1.30rem;
    }

    .hero {
        padding: 12px;
    }

    .hero-name {
        font-size: 1.05rem;
    }

    .quote-price {
        font-size: 1.58rem;
    }

    .quote-change {
        font-size: 0.78rem;
    }

    .evidence-grid {
        gap: 5px;
    }

    .evidence-box {
        padding: 7px;
    }

    .evidence-value {
        font-size: 0.80rem;
    }

    .scenario-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .judgment-box,
    .action-box {
        min-height: auto;
    }

    .theme-data-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ============================================================
# FILES
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"


# ============================================================
# BASE ETF
# ============================================================

# 앱 내부 종목명 목록을 두지 않고 외부 금융검색 결과를 사용합니다.


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
            "반도체장비"
        ],
        "reason":
            "AI 연산 확대와 고대역폭 메모리, 첨단 반도체 투자 증가의 직접적인 수혜 영역입니다.",
        "cycle": "AI 투자 확대 → GPU/가속기 수요 → HBM·첨단공정 → 장비·핵심부품 순으로 자금이 확산되는 출발 구간입니다.",
        "issue": "AI 데이터센터 투자와 고성능 연산 수요가 계속되는지, HBM 및 첨단공정 투자 증가가 실제 수주·거래량으로 이어지는지를 봅니다."
    },

    "데이터센터·AI 인프라": {
        "keywords": [
            "데이터센터",
            "AI인프라",
            "AI 인프라",
            "글로벌AI인프라"
        ],
        "reason":
            "AI 서비스 확산에 따라 서버·네트워크·데이터센터 투자가 확대되는 구간을 추적합니다.",
        "cycle": "AI 반도체 투자 → 서버 증설 → 데이터센터 CAPEX → 네트워크·인프라 투자로 이어지는 중간 확산 구간입니다.",
        "issue": "글로벌 데이터센터 CAPEX와 AI 서버 증설이 실제 수요로 이어지는지, 관련 ETF의 거래량이 함께 붙는지를 봅니다."
    },

    "전력 인프라": {
        "keywords": [
            "전력",
            "전력인프라",
            "전력핵심설비",
            "전력설비"
        ],
        "reason":
            "데이터센터와 산업용 전력수요 증가에 따른 전력망 및 핵심설비 투자를 추적합니다.",
        "cycle": "데이터센터 증설 → 전력수요 증가 → 변압기·배전·송전 투자 → 전력 핵심설비 수주로 연결되는 후방 확산 구간입니다.",
        "issue": "전력 인프라 증설 계획과 수주 증가가 실제 실적·거래량으로 확인되는지 봅니다."
    },

    "원자력": {
        "keywords": [
            "원자력",
            "원전",
            "원전산업"
        ],
        "reason":
            "전력수요 증가와 에너지 믹스 변화에 따라 원전 관련 산업 흐름을 추적합니다.",
        "cycle": "전력수요 증가 → 안정적 전원 필요 → 원전·SMR 투자 논의 → 기자재·건설 수주로 이어지는 장기 테마입니다.",
        "issue": "신규 원전·SMR 프로젝트와 정책·수주 뉴스가 실제 계약 및 관련 종목 거래량으로 연결되는지 봅니다."
    },

    "냉각·열관리": {
        "keywords": [
            "냉각",
            "열관리",
            "액침냉각",
            "AI냉각"
        ],
        "reason":
            "AI 서버 고집적화에 따라 냉각과 열관리의 중요성이 높아지는 후방 수혜 영역입니다.",
        "cycle": "AI 서버 고집적화 → 발열 증가 → 공랭 한계 → 액침·수랭 등 열관리 투자로 이어지는 후방 수혜 사이클입니다.",
        "issue": "고밀도 AI 서버의 냉각 방식 변화와 실제 데이터센터 적용·수주 여부를 확인합니다."
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
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


# ============================================================
# ETF UNIVERSE
# ============================================================

def load_etf_universe():
    return {}


# ============================================================
# STATE
# ============================================================

def init_state():
    if "watchlist" not in st.session_state:
        saved = read_json(WATCHLIST_FILE, DEFAULT_WATCHLIST.copy())
        if isinstance(saved, list):
            st.session_state.watchlist = [str(x).zfill(6) for x in saved]
        else:
            st.session_state.watchlist = DEFAULT_WATCHLIST.copy()

    if "holdings" not in st.session_state:
        saved = read_json(HOLDINGS_FILE, {})
        st.session_state.holdings = saved if isinstance(saved, dict) else {}

    if "etf_universe" not in st.session_state:
        st.session_state.etf_universe = load_etf_universe()

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
        st.session_state.main_page = "📊 내 ETF"

    if "future_detail_code" not in st.session_state:
        st.session_state.future_detail_code = None

    if "future_detail_theme" not in st.session_state:
        st.session_state.future_detail_theme = None


# ============================================================
# BASIC HELPERS
# ============================================================

def display_text(value):
    """외부에서 받은 문자열을 임의의 인코딩으로 재변환하지 않습니다.
    정상 UTF-8 한글을 손상시키지 않는 것이 최우선입니다.
    """
    if value is None:
        return ""
    return str(value)


@st.cache_data(ttl=1800, show_spinner=False)
def resolve_etf_name(code):
    code = str(code).zfill(6)
    korean_name = naver_etf_name(code)
    if korean_name:
        return korean_name
    # 네이버 조회가 일시적으로 실패할 때만 Yahoo 이름을 보조 사용합니다.
    for q in (f"{code}.KS", code):
        try:
            quotes = yf.Search(q, max_results=10).quotes
            if isinstance(quotes, list):
                for raw in quotes:
                    item = _normalize_search_quote(raw)
                    if item and item["code"] == code:
                        return display_text(item["name"])
        except Exception:
            pass
    return f"ETF {code}"


def get_etf_name(code):
    code = str(code).strip().zfill(6)
    return display_text(resolve_etf_name(code))


def normalize_df(df):
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        new_columns = []
        for col in df.columns:
            if isinstance(col, tuple):
                found = None
                for item in col:
                    item_str = str(item)
                    if item_str.lower() in ["open", "high", "low", "close", "volume"]:
                        found = item_str.title()
                        break
                new_columns.append(found if found else str(col[0]))
            else:
                new_columns.append(str(col))
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

    df = df.rename(columns=rename_map)
    required = ["Open", "High", "Low", "Close", "Volume"]
    if not all(col in df.columns for col in required):
        return pd.DataFrame()

    df = df[required].copy()
    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Close"])
    if getattr(df.index, "tz", None) is not None:
        try:
            df.index = df.index.tz_localize(None)
        except Exception:
            pass
    return df


# ============================================================
# PRICE DATA
# ============================================================

def fetch_yahoo(code):
    try:
        ticker = f"{code}.KS"
        df = yf.download(
            ticker,
            period="2y",
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False
        )
        return normalize_df(df)
    except Exception:
        return pd.DataFrame()


def load_price_data(code, force=False):
    code = str(code).zfill(6)
    now = datetime.now()
    cached = st.session_state.price_cache.get(code)
    if cached and not force:
        age = (now - cached["time"]).total_seconds()
        if age < 300:
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

    d["MA20"] = d["Close"].rolling(20).mean()
    d["MA60"] = d["Close"].rolling(60).mean()
    d["MA120"] = d["Close"].rolling(120).mean()

    delta = d["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta).clip(upper=0).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    d["RSI14"] = 100 - (100 / (1 + rs))

    d["VOL20"] = d["Volume"].rolling(20).mean()
    d["VOL_RATIO"] = d["Volume"] / d["VOL20"].replace(0, np.nan)

    d["RET5"] = d["Close"].pct_change(5) * 100
    d["RET20"] = d["Close"].pct_change(20) * 100

    d["HIGH20"] = d["High"].rolling(20).max()
    d["LOW20"] = d["Low"].rolling(20).min()
    d["HIGH60"] = d["High"].rolling(60).max()
    d["LOW60"] = d["Low"].rolling(60).min()

    return d


# ============================================================
# HELPERS
# ============================================================

def safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def money(value):
    value = safe_float(value)
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
            "reasons": ["가격 데이터를 확인하지 못했습니다."],
            "action": "가격 데이터를 다시 확인해 주세요.",
            "ma_state": "확인 불가",
            "rsi_state": "확인 불가",
            "vol_state": "확인 불가",
            "rsi": 0,
            "vol_ratio": 0,
            "ret20": 0
        }

    row = d.iloc[-1]
    current = safe_float(row["Close"])
    ma20 = safe_float(row["MA20"], current)
    ma60 = safe_float(row["MA60"], current)
    rsi = safe_float(row["RSI14"], 50)
    vol_ratio = safe_float(row["VOL_RATIO"], 1)
    ret20 = safe_float(row["RET20"], 0)

    above20 = current >= ma20
    above60 = current >= ma60

    ma_state = "20일선 상회" if above20 else "20일선 하회"

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

    if above20 and above60 and rsi >= 70:
        title = "상승 추세 · 추격 주의"
        action = "추세는 양호하지만 과열 가능성이 있습니다. 신규 매수는 현재가 추격보다 눌림 확인을 우선합니다."
    elif above20 and above60:
        title = "상승 추세 유지"
        action = "20일선과 60일선 위입니다. 보유자는 추세를 확인하고 신규 매수는 돌파 추격보다 눌림을 우선합니다."
    elif above60 and not above20:
        title = "단기 조정 · 중기 추세 확인"
        action = "20일선 아래지만 60일선 위입니다. 20일선 회복 여부를 확인하면서 지지구간의 거래량을 봅니다."
    elif not above60 and rsi <= 40:
        title = "중기 약세 · 방어 우선"
        action = "60일선 아래이고 RSI도 약합니다. 지지 형성과 거래량 회복을 먼저 확인합니다."
    else:
        title = "방향 확인 구간"
        action = "추세가 명확하지 않습니다. 20일선 회복 또는 최근 고점 돌파와 거래량 동반 여부를 확인합니다."

    reasons = [
        f"현재가 {money(current)} · 20일선 {money(ma20)} · {ma_state}",
        f"60일선 {money(ma60)} · {'중기 추세 유지' if above60 else '중기 추세 약화'}",
        f"RSI14 {rsi:.1f} · {rsi_state}",
        f"거래량 {vol_ratio:.2f}배 · {vol_state} · 최근 20일 {ret20:+.2f}%"
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
# PRICE LEVELS
# ============================================================

def calculate_levels(d):
    if d.empty:
        return None
    current = safe_float(d["Close"].iloc[-1])
    ma20 = safe_float(d["MA20"].iloc[-1], current)
    ma60 = safe_float(d["MA60"].iloc[-1], current)
    high20 = safe_float(d["HIGH20"].iloc[-1], current)
    low20 = safe_float(d["LOW20"].iloc[-1], current)
    low60 = safe_float(d["LOW60"].iloc[-1], current)

    return {
        "first": ma20,
        "support": min(ma60, low20),
        "breakout": high20,
        "risk": min(ma60, low20, low60)
    }


# ============================================================
# JUDGMENT UI
# ============================================================

def render_judgment(d):
    judgment = get_judgment(d)
    st.markdown('<div class="section-title">현재판단 · 지금대응</div>', unsafe_allow_html=True)

    rsi = judgment["rsi"]
    vr = judgment["vol_ratio"]

    ma_color = "positive" if judgment["ma_state"] == "20일선 상회" else "negative"
    rsi_color = "positive" if rsi >= 60 else ("negative" if rsi < 40 else "neutral")
    vol_color = "positive" if vr >= 1.1 else ("negative" if vr < 0.8 else "neutral")

    st.markdown(
        f"""
        <div class="evidence-grid">
            <div class="evidence-box">
                <div class="evidence-label">20일선</div>
                <div class="evidence-value {ma_color}">{esc(judgment["ma_state"])}</div>
                <div class="evidence-sub">단기 추세</div>
            </div>
            <div class="evidence-box">
                <div class="evidence-label">RSI14</div>
                <div class="evidence-value {rsi_color}">{rsi:.1f}</div>
                <div class="evidence-sub">{esc(judgment["rsi_state"])}</div>
            </div>
            <div class="evidence-box">
                <div class="evidence-label">거래량</div>
                <div class="evidence-value {vol_color}">{vr:.2f}배</div>
                <div class="evidence-sub">{esc(judgment["vol_state"])}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)
    with c1:
        reasons_html = "<br>".join(esc(x) for x in judgment["reasons"])
        st.markdown(
            f"""
            <div class="judgment-box">
                <div class="judgment-title">현재판단</div>
                <div class="judgment-main">{esc(judgment["title"])}</div>
                <div class="reason-label">판단근거</div>
                <div class="judgment-reason">{reasons_html}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="action-box">
                <div class="action-title">지금대응</div>
                <div class="action-main">{esc(judgment["action"])}</div>
                <div class="action-reason-label">대응근거</div>
                <div class="judgment-reason">현재 추세·RSI·거래량을 기준으로 신규 매수는 추격보다 눌림 또는 확인 후 대응하도록 설정했습니다.</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# SCENARIOS
# ============================================================

def render_scenarios(d):
    levels = calculate_levels(d)
    if not levels:
        return
    st.markdown('<div class="section-title">핵심가격 · 대응 시나리오</div>', unsafe_allow_html=True)
    current = safe_float(d["Close"].iloc[-1])
    ma20 = safe_float(d["MA20"].iloc[-1], current)
    ma60 = safe_float(d["MA60"].iloc[-1], current)
    high20 = safe_float(d["HIGH20"].iloc[-1], current)
    low20 = safe_float(d["LOW20"].iloc[-1], current)
    risk = safe_float(levels["risk"], low20)
    rsi = safe_float(d["RSI14"].iloc[-1], 50)
    vol = safe_float(d["VOL_RATIO"].iloc[-1], 1)
    if current < ma20:
        interest_desc, interest_action = "20일선 회복 전까지 신규매수보다 관망·눌림 확인", "대기"
    elif rsi >= 70:
        interest_desc, interest_action = "추세는 강하지만 과열권이므로 추격매수 자제", "추격 자제"
    else:
        interest_desc, interest_action = "20일선 지지 확인 시 분할 접근 가능", "분할 접근"
    breakout_desc = "최근 고점 부근. 거래량 증가가 동반되는지 확인" if current >= high20 * 0.995 else "최근 20일 고점 돌파 + 거래량 증가를 확인"
    support = min(ma60, low20)
    cards = [
        ("1차 관심구간", ma20, interest_action, interest_desc),
        ("핵심 지지선", support, "지지 확인", "지지 후 반등하면 보유·추가접근, 이탈하면 재평가"),
        ("돌파 확인선", high20, "돌파 대기", breakout_desc),
        ("최종 방어선", risk, "이탈 주의", "이탈 시 단순 조정인지 추세 훼손인지 재확인"),
    ]
    for row_start in (0, 2):
        cols = st.columns(2)
        for col, (label, price, action, desc) in zip(cols, cards[row_start:row_start + 2]):
            with col:
                st.markdown(f'''<div class="scenario-card"><div class="scenario-label">{esc(label)}</div><div class="scenario-price">{money(price)}</div><div class="scenario-action">{esc(action)}</div><div class="scenario-desc">{esc(desc)}</div></div>''', unsafe_allow_html=True)
    gap_to_breakout = ((high20 / current) - 1) * 100 if current else 0
    gap_to_support = ((support / current) - 1) * 100 if current else 0
    gap_to_risk = ((risk / current) - 1) * 100 if current else 0
    if current >= high20 * 0.995 and vol >= 1.2:
        overall = "돌파 확인 단계 · 거래량이 유지되는지 확인"
    elif current >= ma20:
        overall = "상승 추세 유지 단계 · 20일선 지지가 핵심"
    elif current >= ma60:
        overall = "조정 단계 · 20일선 회복 전까지 추격 자제"
    else:
        overall = "방어 단계 · 핵심 지지선 회복 여부 확인"
    st.markdown(f'''<div class="scenario-summary"><div class="scenario-summary-title">현재 대응</div><div class="scenario-summary-main">{esc(overall)}</div><div class="scenario-summary-detail">현재가 {money(current)} · 20일선 {money(ma20)} · 60일선 {money(ma60)} · 돌파선까지 {gap_to_breakout:+.2f}% · 핵심지지선까지 {gap_to_support:+.2f}% · 방어선까지 {gap_to_risk:+.2f}% · RSI {rsi:.1f} · 거래량 {vol:.2f}배</div></div>''', unsafe_allow_html=True)


# ============================================================
# CHART
# ============================================================

def render_chart(d):
    if d.empty:
        st.warning("차트 데이터를 확인하지 못했습니다.")
        return

    chart_df = d.tail(126).copy()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.025, row_heights=[0.75, 0.25])

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
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=chart_df.index, y=chart_df["MA20"], mode="lines", line=dict(color="#4f86b5", width=1.4), name="20일선"),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=chart_df.index, y=chart_df["MA60"], mode="lines", line=dict(color="#a58c52", width=1.3), name="60일선"),
        row=1, col=1
    )

    volume_colors = np.where(chart_df["Close"] >= chart_df["Open"], "#327f69", "#9b4653")

    fig.add_trace(
        go.Bar(x=chart_df.index, y=chart_df["Volume"], marker_color=volume_colors, opacity=0.5, name="거래량", showlegend=False),
        row=2, col=1
    )

    fig.update_xaxes(fixedrange=True, showgrid=False, rangeslider_visible=False)
    fig.update_yaxes(fixedrange=True, gridcolor="#17283a", tickfont=dict(color="#73879b", size=9), row=1, col=1)
    fig.update_yaxes(fixedrange=True, showticklabels=False, showgrid=False, row=2, col=1)

    fig.update_layout(
        height=390,
        margin=dict(l=4, r=4, t=18, b=4),
        paper_bgcolor="#0d1928",
        plot_bgcolor="#0d1928",
        font=dict(color="#aab8c7"),
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", font=dict(size=9, color="#8ea0b3")),
        dragmode=False,
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False, "scrollZoom": False, "doubleClick": False, "responsive": True, "staticPlot": True}
    )


# ============================================================
# SEARCH
# ============================================================

@st.cache_data(ttl=1800, show_spinner=False)
def naver_etf_name(code):
    """KRX 6자리 코드의 한국어 정식명을 Naver Finance에서 가져옵니다.
    문자열은 원문 그대로 사용하며 임의의 UTF-8/Latin 변환을 하지 않습니다.
    """
    code = str(code).strip().zfill(6)
    if not (code.isdigit() and len(code) == 6):
        return ""
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    try:
        req = Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36",
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
        })
        with urlopen(req, timeout=7) as response:
            raw = response.read()
        # Naver 국내 금융 페이지는 CP949/EUC-KR 계열입니다. CP949가 더 넓은 범위를 안전하게 포함합니다.
        text = None
        for enc in ("cp949", "euc-kr", "utf-8"):
            try:
                candidate = raw.decode(enc)
                if "<html" in candidate.lower() or "wrap_company" in candidate:
                    text = candidate
                    break
            except UnicodeDecodeError:
                continue
        if not text:
            return ""

        patterns = [
            r'<h2[^>]*class=["\']wrap_company["\'][^>]*>.*?<a[^>]*>(.*?)</a>',
            r'<h2[^>]*>\s*(.*?)\s*</h2>',
            r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']',
        ]
        for pattern in patterns:
            m = re.search(pattern, text, re.S | re.I)
            if not m:
                continue
            name = re.sub(r"<[^>]+>", "", m.group(1))
            name = html.unescape(re.sub(r"\s+", " ", name)).strip()
            name = re.sub(r"\s*:\s*Naver Finance.*$", "", name, flags=re.I).strip()
            if name and len(name) >= 2 and "404" not in name:
                return name
    except Exception:
        pass
    return ""


@st.cache_data(ttl=1800, show_spinner=False)
def naver_etf_universe():
    """Naver의 국내 ETF 목록을 읽어 코드/한국어명을 동적으로 구성합니다.
    앱에 종목명을 하드코딩하지 않습니다.
    """
    rows = []
    seen = set()
    base = "https://finance.naver.com/sise/etf.naver"
    for page in range(1, 11):
        url = f"{base}?&page={page}"
        try:
            req = Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36",
                "Accept-Language": "ko-KR,ko;q=0.9",
            })
            with urlopen(req, timeout=7) as response:
                raw = response.read()
            text = None
            for enc in ("cp949", "euc-kr", "utf-8"):
                try:
                    candidate = raw.decode(enc)
                    if "etf" in candidate.lower() and "finance" in candidate.lower():
                        text = candidate
                        break
                except UnicodeDecodeError:
                    continue
            if not text:
                continue

            # ETF 링크의 item/main.naver?code=XXXXXX를 기준으로 코드와 표시명을 함께 추출
            link_pat = re.compile(
                r'<a[^>]+href=["\']/item/main\.naver\?code=(\d{6})[^"\']*["\'][^>]*>(.*?)</a>',
                re.S | re.I
            )
            for m in link_pat.finditer(text):
                code = m.group(1)
                name = re.sub(r"<[^>]+>", "", m.group(2))
                name = html.unescape(re.sub(r"\s+", " ", name)).strip()
                if code not in seen and name:
                    rows.append({"code": code, "name": name})
                    seen.add(code)
        except Exception:
            continue
    return rows


def _normalize_search_quote(q):
    if not isinstance(q, dict):
        return None
    symbol = str(q.get("symbol") or q.get("ticker") or "").strip()
    raw_name = q.get("shortname") or q.get("longname") or q.get("name") or ""
    name = display_text(raw_name)
    if not symbol:
        return None
    # 국내 ETF는 사용자 입력 6자리 코드를 기준으로 내부에서만 .KS를 붙여 조회합니다.
    if symbol.endswith(".KS"):
        code = symbol[:-3]
    elif symbol.isdigit() and len(symbol) <= 6:
        code = symbol.zfill(6)
    else:
        return None
    if not code.isdigit() or len(code) != 6:
        return None
    return {"code": code, "name": name}


@st.cache_data(ttl=600, show_spinner=False)
def yahoo_etf_search(query):
    """사용자 검색은 Yahoo를 보조 검색으로 사용하고, 국내 ETF는 Naver ETF 목록을 함께 검색합니다."""
    q = str(query).strip()
    if not q:
        return []
    results, seen = [], set()

    # 1) 6자리 코드는 가장 정확하게 직접 조회
    if q.isdigit():
        code = q.zfill(6)
        name = naver_etf_name(code)
        if name:
            results.append({"code": code, "name": name})
            seen.add(code)
        yahoo_queries = [f"{code}.KS", code]
    else:
        yahoo_queries = [q, f"{q} ETF"]

    # 2) Naver 국내 ETF 목록에서 한국어 이름/코드 검색
    nq = q.lower()
    try:
        universe = naver_etf_universe()
        if universe:
            for item in universe:
                name = str(item.get("name", ""))
                code = str(item.get("code", "")).zfill(6)
                if code in seen:
                    continue
                if nq in name.lower() or (q.isdigit() and code == q.zfill(6)):
                    results.append({"code": code, "name": name})
                    seen.add(code)
                    if len(results) >= 30:
                        break
    except Exception:
        pass

    # 3) Yahoo는 가격 티커 발견용 보조 경로
    for search_q in yahoo_queries:
        try:
            data = yf.Search(search_q, max_results=25).quotes
        except Exception:
            data = []
        if isinstance(data, list):
            for raw in data:
                item = _normalize_search_quote(raw)
                if item and item["code"] not in seen:
                    # 한국어 정식명이 있으면 교체
                    item["name"] = naver_etf_name(item["code"]) or item["name"]
                    results.append(item)
                    seen.add(item["code"])

    if q.isdigit():
        code = q.zfill(6)
        results.sort(key=lambda x: 0 if x["code"] == code else 1)
    else:
        results.sort(key=lambda x: (0 if nq in str(x["name"]).lower() else 1, str(x["name"])))
    return results[:30]


def search_etfs(query):
    """앱 내부 종목 목록이 아니라 Yahoo Finance 검색을 기준으로 ETF를 찾습니다."""
    query = (query or "").strip()
    if not query:
        return []
    return yahoo_etf_search(query)


# ============================================================
# WATCHLIST
# ============================================================

def add_watch(code):
    code = str(code).zfill(6)
    if code not in st.session_state.watchlist:
        st.session_state.watchlist.append(code)
        write_json(WATCHLIST_FILE, st.session_state.watchlist)
    st.session_state.selected_code = code


# ============================================================
# ETF FINDER
# ============================================================

def render_finder():
    st.markdown('<div class="section-title">ETF 찾기</div>', unsafe_allow_html=True)
    query = st.text_input("ETF명 또는 종목코드", placeholder="예: AI반도체 / 395160", label_visibility="collapsed", key="search_q")
    results = search_etfs(query)
    if results:
        result_codes = [str(x["code"]).zfill(6) for x in results]
        result_map = {str(x["code"]).zfill(6): x for x in results}
        selected_code = st.selectbox("검색 결과", result_codes, format_func=lambda code: str(result_map.get(str(code).zfill(6), {}).get("name", "ETF")), key="search_result_code")
        item = result_map[str(selected_code).zfill(6)]
        c1, c2 = st.columns([4, 1])
        with c1:
            st.caption(f'선택: {display_text(item["name"])} · 종목코드 {item["code"]}')
        with c2:
            already = item["code"] in st.session_state.watchlist
            if st.button("추가" if not already else "등록됨", disabled=already, use_container_width=True, key=f'add_{item["code"]}'):
                add_watch(item["code"])
                st.rerun()
    elif query:
        st.caption("검색 결과가 없습니다. 6자리 종목코드 또는 ETF명을 입력해 주세요.")


# ============================================================
# WATCHLIST UI
# ============================================================

def render_watchlist():
    st.markdown('<div class="section-title">관심종목</div>', unsafe_allow_html=True)
    watchlist = st.session_state.watchlist
    if not watchlist:
        st.info("관심종목이 없습니다.")
        return

    current = st.session_state.selected_code
    default_index = watchlist.index(current) if current in watchlist else 0

    code = st.selectbox(
        "관심종목 선택",
        watchlist,
        index=default_index,
        format_func=lambda x: f"{display_text(get_etf_name(x))} · {str(x).zfill(6)}",
        key="watch_select_code"
    )
    st.session_state.selected_code = code

    if st.button("현재 ETF 관심종목에서 삭제", use_container_width=True, key="remove_watch"):
        watchlist.remove(code)
        write_json(WATCHLIST_FILE, watchlist)
        st.session_state.selected_code = watchlist[0] if watchlist else "395160"
        st.rerun()


# ============================================================
# HOLDINGS
# ============================================================

def render_holdings(code, current):
    st.markdown('<div class="section-title">보유 상태</div>', unsafe_allow_html=True)
    old = st.session_state.holdings.get(code)

    held = st.radio("보유 여부", ["미보유", "보유중"], index=1 if old else 0, horizontal=True, key=f"held_{code}")

    if held == "보유중":
        c1, c2 = st.columns(2)
        with c1:
            avg = st.number_input("평균매수가", min_value=0.0, value=float(old.get("avg_price", 0) if old else 0), step=100.0, key=f"avg_{code}")
        with c2:
            qty = st.number_input("보유수량", min_value=0.0, value=float(old.get("quantity", 0) if old else 0), step=1.0, key=f"qty_{code}")

        if st.button("보유정보 저장", key=f"save_{code}", use_container_width=True):
            st.session_state.holdings[code] = {"avg_price": avg, "quantity": qty}
            write_json(HOLDINGS_FILE, st.session_state.holdings)
            st.rerun()

        if avg > 0:
            pnl = (current / avg - 1) * 100
            cls = "positive" if pnl >= 0 else "negative"
            st.markdown(
                f"""
                <div class="holding-box">
                    <div class="holding-value">보유 {qty:,.0f}주</div>
                    <div class="holding-detail">평균매수가 {money(avg)} · 현재 수익률 <span class="{cls}">{pnl:+.2f}%</span></div>
                </div>
                """,
                unsafe_allow_html=True
            )
    elif old:
        if st.button("보유정보 삭제", key=f"del_{code}", use_container_width=True):
            del st.session_state.holdings[code]
            write_json(HOLDINGS_FILE, st.session_state.holdings)
            st.rerun()


# ============================================================
# MY ETF
# ============================================================

def render_my_etf():
    render_finder()
    render_watchlist()

    code = st.session_state.selected_code
    name = get_etf_name(code)
    df = load_price_data(code)

    if df.empty:
        st.error("가격 데이터를 불러오지 못했습니다. 종목코드 또는 인터넷 연결을 확인해 주세요.")
        return

    d = calculate_indicators(df)
    if d.empty:
        st.error("분석 데이터를 만들지 못했습니다.")
        return

    current = safe_float(d["Close"].iloc[-1])
    previous = safe_float(d["Close"].iloc[-2]) if len(d) >= 2 else current
    change = current - previous
    change_pct = change / previous * 100 if previous != 0 else 0
    cls = "positive" if change > 0 else ("negative" if change < 0 else "neutral")
    date_text = d.index[-1].strftime("%Y-%m-%d")

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-name">{esc(name)}</div>
            <div class="hero-code">{esc(code)}</div>
            <div class="quote-row">
                <div class="quote-price">{money(current)}</div>
                <div class="quote-change {cls}">{money(change)} ({change_pct:+.2f}%)</div>
            </div>
            <div class="hero-date">기준일 {esc(date_text)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    render_holdings(code, current)
    render_judgment(d)
    render_scenarios(d)

    st.markdown('<div class="section-title">가격 흐름 · 최근 6개월</div>', unsafe_allow_html=True)
    render_chart(d)


# ============================================================
# THEME CANDIDATES
# ============================================================

def theme_candidates(theme):
    """테마별 후보를 Naver 국내 ETF 목록에서 동적으로 찾습니다.
    Yahoo 한국어 검색이 실패해도 미래테마가 비지 않도록 합니다.
    """
    info = THEMES[theme]
    keywords = info.get("keywords", [])
    result, used = [], set()

    try:
        universe = naver_etf_universe()
    except Exception:
        universe = []

    # 이름에 테마 키워드가 들어간 국내 ETF를 우선 추출
    scored = []
    for item in universe:
        code = str(item.get("code", "")).zfill(6)
        name = str(item.get("name", ""))
        if not (code.isdigit() and len(code) == 6) or code in used:
            continue
        score = 0
        low = name.lower()
        for kw in keywords:
            if str(kw).lower() in low:
                score += 1
        if score:
            scored.append((score, name, code))

    scored.sort(key=lambda x: (-x[0], x[1]))
    for score, name, code in scored:
        result.append({"code": code, "name": name})
        used.add(code)
        if len(result) >= 4:
            break

    # Naver 목록 접속이 일시적으로 실패하면 Yahoo의 국내 티커 검색을 보조 사용
    if len(result) < 4:
        for keyword in keywords[:3]:
            for item in yahoo_etf_search(keyword):
                code = item["code"]
                if code in used:
                    continue
                result.append({"code": code, "name": naver_etf_name(code) or item["name"]})
                used.add(code)
                if len(result) >= 4:
                    return result
    return result


# ============================================================
# THEME SNAPSHOT
# ============================================================

def theme_snapshot(theme):
    cached = st.session_state.theme_cache.get(theme)
    now = datetime.now()
    if cached:
        age = (now - cached["time"]).total_seconds()
        if age < 300:
            return cached["rows"]

    rows = []
    candidates = theme_candidates(theme)

    for item in candidates:
        code = item["code"]
        df = load_price_data(code)
        if df.empty:
            continue
        d = calculate_indicators(df)
        if d.empty:
            continue
        row = d.iloc[-1]
        current = safe_float(row["Close"])
        ma20 = safe_float(row["MA20"], current)

        rows.append({
            "code": code,
            "name": item["name"],
            "price": current,
            "rsi": safe_float(row["RSI14"], 50),
            "vr": safe_float(row["VOL_RATIO"], 1),
            "ret": safe_float(row["RET20"], 0),
            "trend": "상승" if current >= ma20 else "조정"
        })

    st.session_state.theme_cache[theme] = {"time": now, "rows": rows}
    return rows


# ============================================================
# INLINE FUTURE ETF ANALYSIS
# ============================================================

def render_future_inline_analysis(code, theme):
    if not code:
        return
    df = load_price_data(code)
    if df.empty:
        st.warning("선택한 ETF의 가격 데이터를 확인하지 못했습니다.")
        return

    d = calculate_indicators(df)
    if d.empty:
        return

    name = get_etf_name(code)
    current = safe_float(d["Close"].iloc[-1])
    previous = safe_float(d["Close"].iloc[-2]) if len(d) > 1 else current
    change = current - previous
    pct = change / previous * 100 if previous else 0
    cls = "positive" if change > 0 else ("negative" if change < 0 else "neutral")

    st.markdown(
        f"""
        <div class="future-analysis">
            <div class="future-analysis-title">미래테마 안에서 분석 · {esc(theme or "선택 ETF")}</div>
            <div class="future-analysis-name">{esc(name)}</div>
            <div class="future-analysis-code">{esc(code)}</div>
            <div class="quote-row">
                <div class="quote-price">{money(current)}</div>
                <div class="quote-change {cls}">{money(change)} ({pct:+.2f}%)</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    render_judgment(d)
    render_scenarios(d)
    st.markdown('<div class="section-title">가격 흐름 · 최근 6개월</div>', unsafe_allow_html=True)
    render_chart(d)


# ============================================================
# FUTURE THEME
# ============================================================

def stage_class(stage):
    if stage == "현재 주도":
        return "stage-lead"
    if stage == "다음 수혜":
        return "stage-next"
    if stage == "관심 확대":
        return "stage-interest"
    return "stage-early"


def render_future_theme():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-name">미래테마</div>
            <div class="hero-code">현재 주도 → 다음 수혜 → 초기 관심</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    for theme_index, (theme, stage) in enumerate(FUTURE_CHAIN):
        info = THEMES[theme]
        st.markdown(
            f"""
            <div class="theme-card">
                <div class="theme-stage {stage_class(stage)}">{esc(stage)}</div>
                <div class="theme-title">{esc(theme)}</div>
                <div class="theme-reason">{esc(info["reason"])}</div>
                <div class="theme-reason"><b>순환 사이클</b> · {esc(info.get("cycle", ""))}</div>
                <div class="theme-reason"><b>핵심 이슈</b> · {esc(info.get("issue", ""))}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        rows = theme_snapshot(theme)
        if not rows:
            st.caption("현재 표시 가능한 ETF 데이터가 없습니다.")
            continue

        cols = st.columns(len(rows))
        for i, item in enumerate(rows):
            with cols[i]:
                ret_cls = "positive" if item["ret"] >= 0 else "negative"
                trend_cls = "positive" if item["trend"] == "상승" else "negative"

                st.markdown(
                    f"""
                    <div class="theme-etf-box">
                        <div class="theme-etf-name">{esc(item["name"])}</div>
                        <div class="theme-etf-code">{esc(item["code"])}</div>
                        <div class="theme-data-grid">
                            <div class="theme-data-item">
                                <div class="theme-data-label">현재가</div>
                                <div class="theme-data-value">{money(item["price"])}</div>
                            </div>
                            <div class="theme-data-item">
                                <div class="theme-data-label">RSI</div>
                                <div class="theme-data-value">{item["rsi"]:.1f}</div>
                            </div>
                            <div class="theme-data-item">
                                <div class="theme-data-label">거래량</div>
                                <div class="theme-data-value">{item["vr"]:.2f}배</div>
                            </div>
                            <div class="theme-data-item">
                                <div class="theme-data-label">20일</div>
                                <div class="theme-data-value {ret_cls}">{item["ret"]:+.2f}%</div>
                            </div>
                        </div>
                        <div style="font-size:.64rem;color:#71869a;margin-top:5px;">
                            추세 <span class="{trend_cls}">{esc(item["trend"])}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                is_open = (st.session_state.future_detail_code == item["code"] and st.session_state.future_detail_theme == theme)
                if st.button(
                    "분석 닫기" if is_open else "ETF 분석",
                    key=f"theme_an_{theme_index}_{i}_{item['code']}",
                    use_container_width=True
                ):
                    if is_open:
                        st.session_state.future_detail_code = None
                        st.session_state.future_detail_theme = None
                    else:
                        st.session_state.future_detail_code = item["code"]
                        st.session_state.future_detail_theme = theme
                    st.rerun()

                if is_open:
                    render_future_inline_analysis(item["code"], theme)

    st.markdown('<div class="section-title">테마 요약</div>', unsafe_allow_html=True)
    summary_rows = []

    for theme, stage in FUTURE_CHAIN:
        rows = theme_snapshot(theme)
        if not rows:
            continue
        avg_ret = np.mean([x["ret"] for x in rows])
        avg_rsi = np.mean([x["rsi"] for x in rows])
        avg_vol = np.mean([x["vr"] for x in rows])

        summary_rows.append({
            "theme": theme,
            "stage": stage,
            "ret": avg_ret,
            "rsi": avg_rsi,
            "vol": avg_vol
        })

    if summary_rows:
        # HTML table 대신 Streamlit 컬럼/마크다운으로 구성하여 모바일에서
        # HTML/Python 원문이 노출되는 문제를 차단합니다.
        for row in summary_rows:
            ret_cls = "positive" if row["ret"] >= 0 else "negative"
            st.markdown(
                f"""
                <div class=\"summary-card\">
                    <div class=\"summary-card-title\">{esc(row["theme"])}</div>
                    <div class=\"summary-card-meta\">{esc(row["stage"])}</div>
                    <div class=\"summary-card-grid\">
                        <div class=\"summary-mini\"><div class=\"summary-mini-label\">20일 수익률</div><div class=\"summary-mini-value {ret_cls}\">{row["ret"]:+.2f}%</div></div>
                        <div class=\"summary-mini\"><div class=\"summary-mini-label\">RSI</div><div class=\"summary-mini-value\">{row["rsi"]:.1f}</div></div>
                        <div class=\"summary-mini\"><div class=\"summary-mini-label\">거래량</div><div class=\"summary-mini-value\">{row["vol"]:.2f}배</div></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# MAIN
# ============================================================

init_state()

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">ETF RADAR</div>
        <div class="app-subtitle">ETF 추세 · 모멘텀 · 거래량 · 핵심가격 · 대응 시나리오</div>
    </div>
    """,
    unsafe_allow_html=True
)

nav = st.radio(
    "메뉴",
    ["📊 내 ETF", "🚀 미래테마"],
    horizontal=True,
    key="main_page",
    label_visibility="collapsed"
)

if nav == "📊 내 ETF":
    render_my_etf()
else:
    render_future_theme()
