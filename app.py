
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import json
import os
import html
import ast
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def esc(value):
    """동적 문자열의 HTML 깨짐 방지"""
    return html.escape(str(value))

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
    font-size: 0.65rem;
    color: #7199b8 !important;
    font-weight: 750;
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
   FUTURE THEME PRIORITY / OUTLOOK
   ========================================================== */

.theme-stage-wrap {
    display:flex;
    align-items:center;
    gap:6px;
    margin-bottom:5px;
}

.theme-stage-badge {
    display:inline-block;
    padding:3px 7px;
    border-radius:999px;
    font-size:.60rem;
    font-weight:800;
    border:1px solid transparent;
}

.stage-core { background:#173b32; color:#55d7ad !important; border-color:#2d8068; }
.stage-next { background:#17324a; color:#6db8f2 !important; border-color:#35688f; }
.stage-interest { background:#3b3219; color:#e0bd63 !important; border-color:#80692e; }
.stage-early { background:#32223b; color:#c59ae8 !important; border-color:#694b7c; }

.theme-outlook {
    margin-top:7px;
    padding:7px 8px;
    border-radius:7px;
    background:#0a1522;
    border-left:3px solid #3d6584;
    color:#b9c7d4 !important;
    font-size:.67rem;
    line-height:1.45;
}

.theme-outlook strong { color:#e0e8ef !important; }

.theme-summary-card {
    background:#0b1725;
    border:1px solid #20374c;
    border-radius:9px;
    padding:9px;
    margin-bottom:7px;
}

.theme-summary-title {
    font-size:.72rem;
    font-weight:800;
    color:#e0e8ef !important;
}

.theme-summary-meta {
    font-size:.64rem;
    color:#8295a8 !important;
    margin-top:3px;
}

.theme-summary-outlook {
    font-size:.68rem;
    color:#bdcad6 !important;
    margin-top:6px;
    line-height:1.45;
}

/* ==========================================================
   BACKTEST C / D HIGHLIGHT
   ========================================================== */
.cd-highlight {
    background: #0d1d2c;
    border: 1px solid #3b6484;
    border-left: 4px solid #69b5ed;
    border-radius: 12px;
    padding: 12px;
    margin: 12px 0 14px;
}
.cd-highlight-title {
    font-size: 1.02rem;
    font-weight: 850;
    color: #e5edf5 !important;
}
.cd-highlight-sub {
    font-size: .67rem;
    color: #91a8bc !important;
    margin-top: 4px;
    line-height: 1.45;
}
.cd-item {
    background: #0a1725;
    border: 1px solid #29445d;
    border-radius: 9px;
    padding: 9px;
    margin-top: 7px;
}
.cd-count { margin:7px 0 8px; padding:7px 9px; background:#0b1725; border:1px solid #20374c; border-radius:7px; color:#9fb1c2; font-size:.68rem; }
.cd-count b { color:#dce6ef; }

.cd-code {
    display:inline-block;
    margin-top:4px;
    padding:2px 7px;
    border-radius:5px;
    background:#162c42;
    color:#72b9ed !important;
    font-size:.65rem;
    font-weight:800;
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

/* ==========================================================
   MARKET RADAR
   ========================================================== */
.radar-card { background:#0d1928; border:1px solid #263e54; border-radius:10px; padding:11px; margin-bottom:7px; }
.radar-title { font-size:.92rem; font-weight:850; color:#dce6ef !important; }
.radar-sub { font-size:.67rem; color:#7f93a7 !important; margin-top:3px; line-height:1.45; }
.radar-score { font-size:1.35rem; font-weight:900; color:#69b5ed !important; }
.radar-label { font-size:.62rem; color:#74899d !important; }
.radar-value { font-size:.75rem; font-weight:800; color:#cbd7e2 !important; }
.radar-badge { display:inline-block; padding:3px 7px; border-radius:999px; font-size:.58rem; font-weight:800; margin-right:4px; border:1px solid #29445d; background:#122236; color:#9fb3c6 !important; }
.radar-badge-hot { background:#3a211f; border-color:#78463f; color:#ef8c80 !important; }
.radar-badge-op { background:#16362f; border-color:#2c7965; color:#5dd3ae !important; }
.radar-badge-hold { background:#26321f; border-color:#596d3d; color:#c8d982 !important; }
.radar-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:5px; margin-top:8px; }
.radar-metric { background:#091522; border-radius:6px; padding:6px; }
.radar-note { margin-top:7px; padding:7px 8px; background:#0a1522; border-left:3px solid #3e6685; border-radius:6px; color:#aebdcb !important; font-size:.65rem; line-height:1.45; }
@media(max-width:700px){ .radar-grid{grid-template-columns:repeat(2,1fr);} }

</style>
"""

if hasattr(st, "html"):
    st.html(CSS)
else:
    st.markdown(CSS, unsafe_allow_html=True)

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"

BASE_ETFS = {}

DEFAULT_WATCHLIST = [
    "395160",
    "487240",
    "471990",
    "133690",
    "360750",
    "458730",
]

THEME_LEXICON = {
    "AI 반도체": ["반도체", "AI반도체", "AI 반도체", "HBM", "메모리", "시스템반도체", "반도체장비", "반도체소부장"],
    "로봇": ["로봇", "로보틱스", "휴머노이드", "로보틱", "스마트팩토리"],
    "방산": ["방산", "방위산업", "K방산", "국방", "우주항공방산"],
    "2차전지": ["2차전지", "이차전지", "배터리", "전고체", "양극재", "음극재", "리튬", "배터리소재"],
    "전기차": ["전기차", "EV", "전기자동차", "자율주행", "모빌리티"],
    "조선": ["조선", "조선업", "선박", "LNG선", "해운", "선박기자재"],
    "원자력": ["원자력", "원전", "SMR", "소형모듈원전", "핵융합"],
    "전력 인프라": ["전력", "전력인프라", "전력설비", "전력망", "변압기", "전선", "송배전", "전기설비"],
    "데이터센터·AI 인프라": ["데이터센터", "AI인프라", "AI 인프라", "서버", "네트워크", "클라우드", "IDC"],
    "냉각·열관리": ["냉각", "열관리", "액침냉각", "수랭", "칠러", "열교환", "냉동공조"],
    "바이오": ["바이오", "헬스케어", "제약", "신약", "항암", "면역", "의료기기", "유전체"],
    "우주항공": ["우주", "우주항공", "항공우주", "위성", "발사체", "UAM"],
    "AI 소프트웨어": ["AI", "인공지능", "생성AI", "AI소프트웨어", "소프트웨어", "빅데이터"],
    "클라우드": ["클라우드", "SaaS", "데이터센터"],
    "보안": ["보안", "사이버보안", "정보보안", "보안솔루션"],
    "5G·통신": ["5G", "6G", "통신", "네트워크", "위성통신"],
    "신재생에너지": ["태양광", "태양광발전", "풍력", "신재생", "친환경에너지", "수소"],
    "수소": ["수소", "수소경제", "수소연료전지", "연료전지"],
    "친환경·탄소": ["탄소", "탄소중립", "친환경", "ESG", "폐기물", "리사이클", "재활용"],
    "금융": ["은행", "금융", "증권", "보험", "고배당", "배당"],
    "자동차": ["자동차", "자동차부품", "차량", "모빌리티"],
    "화장품·K뷰티": ["화장품", "K뷰티", "뷰티", "미용"],
    "음식료·소비": ["음식료", "식품", "소비재", "유통", "소비"],
    "건설·인프라": ["건설", "인프라", "SOC", "건설기계", "시멘트"],
    "철강·금속": ["철강", "금속", "구리", "알루미늄", "비철금속"],
    "원자재": ["원자재", "상품", "원유", "천연가스", "커머디티"],
    "금·귀금속": ["금", "골드", "귀금속", "은", "실버"],
    "중국": ["중국", "차이나", "CSI", "홍콩", "상하이"],
    "미국 기술": ["나스닥", "미국테크", "미국기술", "S&P500", "테크"],
    "반도체 장비·소부장": ["반도체장비", "반도체장비주", "소부장", "소재부품장비", "장비"],
}

THEME_REASONS = {
    "AI 반도체":"AI 연산과 데이터 처리 수요 확대에 직접 연결되는 반도체 산업 흐름입니다.",
    "로봇":"자동화·휴머노이드·스마트팩토리 투자 확대와 연결되는 산업 흐름입니다.",
    "방산":"국방비 확대와 글로벌 방산 수요 변화에 연결되는 산업 흐름입니다.",
    "2차전지":"전기차·ESS·배터리 기술 변화와 연결되는 배터리 산업 흐름입니다.",
    "전기차":"전동화와 미래 모빌리티 투자 흐름을 추적합니다.",
    "조선":"선박 발주와 친환경·고부가 선박 수요에 연결되는 산업 흐름입니다.",
    "원자력":"원전·SMR 등 장기 전력 수요와 에너지 투자 흐름을 추적합니다.",
    "전력 인프라":"전력수요 증가와 송배전·변압기·전선 설비 투자 흐름입니다.",
    "데이터센터·AI 인프라":"AI 확산에 따른 데이터센터·서버·네트워크 투자 흐름입니다.",
    "냉각·열관리":"고집적 서버와 산업설비 확대에 따른 냉각·열관리 수요 흐름입니다.",
}

THEMES = {}
FUTURE_CHAIN = []

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

def _normalize_etf_code(code):
    code = str(code or "").strip().upper()
    if code.isdigit():
        return code.zfill(6)
    return code

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_naver_etf_master():
    """네이버 금융의 국내 ETF 전체 목록을 직접 가져옵니다."""
    url = "https://finance.naver.com/api/sise/etfItemList.nhn"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.naver.com/sise/etf.nhn"}
    try:
        r = requests.get(url, headers=headers, timeout=12)
        r.raise_for_status()
        try:
            payload = r.json()
        except Exception:
            payload = json.loads(r.content.decode("cp949", errors="ignore"))
        items = payload.get("result", {}).get("etfItemList", [])
        return {
            _normalize_etf_code(x.get("itemcode")): safe_etf_name(_normalize_etf_code(x.get("itemcode")), x.get("itemname"))
            for x in items
            if x.get("itemcode") and x.get("itemname")
        }
    except Exception:
        return {}

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_krx_etf_master():
    """KRX ETF master(MDCSTAT04601)를 직접 조회합니다. 실패하면 빈 dict를 반환합니다."""
    url = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd",
        "Origin": "https://data.krx.co.kr",
    }
    payload = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT04601",
        "locale": "ko_KR",
        "share": "1",
        "csvxls_isNo": "false",
    }
    try:
        r = requests.post(url, headers=headers, data=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
        rows = data.get("output") or data.get("OutBlock_1") or []
        result = {}
        for x in rows:
            code = _normalize_etf_code(x.get("ISU_SRT_CD") or x.get("isu_srt_cd") or x.get("ISU_CD"))
            name = x.get("ISU_ABBRV") or x.get("isu_abrv") or x.get("ISU_NM")
            if code and name:
                result[code] = safe_etf_name(code, name)
        return result
    except Exception:
        return {}

def load_etf_universe():
    """하드코딩 목록 대신 KRX/Naver 실시간 ETF master를 합칩니다."""
    krx = fetch_krx_etf_master()
    naver = fetch_naver_etf_master()
    universe = {}
    universe.update({k: v for k, v in krx.items() if v and not v.startswith("ETF ")})
    for code, name in naver.items():
        if code not in universe or not universe[code] or universe[code].startswith("ETF "):
            universe[code] = name
    return universe

def init_state():
    if "watchlist" not in st.session_state:
        saved = read_json(WATCHLIST_FILE, DEFAULT_WATCHLIST.copy())
        if isinstance(saved, list):
            st.session_state.watchlist = [_normalize_etf_code(x) for x in saved]
        else:
            st.session_state.watchlist = DEFAULT_WATCHLIST.copy()

    if "holdings" not in st.session_state:
        saved = read_json(HOLDINGS_FILE, {})
        st.session_state.holdings = saved if isinstance(saved, dict) else {}

    if "etf_universe" not in st.session_state:
        st.session_state.etf_universe = load_etf_universe()
        if not st.session_state.etf_universe:
            st.session_state.etf_universe = {}

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

    if "radar_cache" not in st.session_state:
        st.session_state.radar_cache = None

    if "radar_mode" not in st.session_state:
        st.session_state.radar_mode = "🎯 기회검색"

    if "future_engine_cache" not in st.session_state:
        st.session_state.future_engine_cache = None

def _name_has_hangul(text):
    return any("가" <= ch <= "힣" for ch in str(text))

def _looks_mojibake(text):
    t = str(text)
    bad = ("Ã", "Â", "â", "ê", "ë", "ì", "í", "î", "ï", "ð", "ñ", "�", "�")
    return any(x in t for x in bad)

def safe_etf_name(code, name=None):
    code = str(code).zfill(6)
    if isinstance(name, dict):
        name = name.get("name") or name.get("etf_name") or name.get("title")

    text = html.unescape(str(name or "")).strip()
    if text.startswith("{") and "'name'" in text:
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, dict):
                text = str(parsed.get("name") or parsed.get("etf_name") or parsed.get("title") or "").strip()
        except Exception:
            m = re.search(r"['\"]name['\"]\s*:\s*['\"]([^'\"]+)['\"]", text)
            if m:
                text = m.group(1).strip()

    text = html.unescape(text).strip()
    if not text or _looks_mojibake(text) or text.startswith("{") or "'ticker'" in text or '"ticker"' in text:
        return f"ETF {code}"
    return text

def get_etf_name(code):
    code = str(code).zfill(6)
    return safe_etf_name(code, st.session_state.etf_universe.get(code))

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

def fetch_naver_history(code, count=600):
    """Yahoo에서 제공하지 않는 국내 ETF/비정형 코드를 위한 Naver 가격 fallback."""
    code = _normalize_etf_code(code)
    url = f"https://fchart.stock.naver.com/sise.nhn?symbol={code}&timeframe=day&count={count}&requestType=0"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        rows = []
        for item in root.findall(".//item"):
            raw = item.attrib.get("data", "")
            parts = raw.split("|")
            if len(parts) < 6:
                continue
            rows.append(parts[:6])
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["Date", "Close"]).set_index("Date")
        return normalize_df(df)
    except Exception:
        return pd.DataFrame()

def fetch_yahoo(code):
    code = _normalize_etf_code(code)
    try:
        ticker = f"{code}.KS"
        df = yf.download(
            ticker, period="2y", interval="1d", auto_adjust=False,
            progress=False, threads=False
        )
        df = normalize_df(df)
        if not df.empty:
            return df
    except Exception:
        pass
    return fetch_naver_history(code)

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
    loss_safe = loss.replace(0, np.nan)
    rs = gain / loss_safe
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.where(loss.notna(), np.where(gain > 0, 100.0, 50.0))
    d["RSI14"] = rsi.clip(lower=0, upper=100)

    d["VOL20"] = d["Volume"].rolling(20).mean()
    d["VOL_RATIO"] = d["Volume"] / d["VOL20"].replace(0, np.nan)

    d["RET5"] = d["Close"].pct_change(5) * 100
    d["RET20"] = d["Close"].pct_change(20) * 100

    d["HIGH20"] = d["High"].rolling(20).max()
    d["LOW20"] = d["Low"].rolling(20).min()
    d["HIGH60"] = d["High"].rolling(60).max()
    d["LOW60"] = d["Low"].rolling(60).min()

    return d

def safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        value = float(value)
        return value if np.isfinite(value) else default
    except Exception:
        return default

def money(value):
    value = safe_float(value)
    if abs(value) >= 1000:
        return f"{value:,.0f}원"
    return f"{value:,.2f}원"

def us_money(value):
    value = safe_float(value)
    return f"${value:,.2f}"

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

def render_scenarios(d):
    levels = calculate_levels(d)
    if not levels:
        return

    current = safe_float(d["Close"].iloc[-1])
    ma20 = safe_float(d["MA20"].iloc[-1], current)
    ma60 = safe_float(d["MA60"].iloc[-1], current)
    high20 = safe_float(d["HIGH20"].iloc[-1], current)
    low20 = safe_float(d["LOW20"].iloc[-1], current)

    # 기존 핵심가격을 실제 매매 가격으로 번역합니다.
    # 1차/2차 손절은 기존 지지·위험가격을 그대로 사용하고,
    # 익절은 현재가 대비 1R/2R 방식으로 계산해 임의의 고정 수익률을 쓰지 않습니다.
    sl1 = min(levels["support"], current * 0.995)
    sl2 = min(levels["risk"], sl1 * 0.98)
    risk1 = max(current - sl1, current * 0.02)
    tp1 = max(high20, current + risk1)
    tp2 = max(tp1, current + risk1 * 2.0)

    st.markdown("### 1차 익절 · 2차 익절 · 1차 손절 · 2차 손절")
    st.caption("현재가와 기존 지지·위험가격을 기준으로 목표수익과 위험관리 가격을 계산합니다. 2차 익절 이후에는 20일선 이탈을 후행손절 기준으로 활용합니다.")

    cards = [
        {
            "label": "① 1차 익절",
            "price": tp1,
            "condition": "첫 번째 목표가격",
            "meaning": "현재가에서 1차 목표에 도달하면 일부 이익을 확보하는 구간입니다.",
            "action": "보유수량 일부 익절을 검토하고 나머지는 추세를 확인합니다."
        },
        {
            "label": "② 2차 익절",
            "price": tp2,
            "condition": "두 번째 목표가격",
            "meaning": "1차 익절 이후 상승 추세가 계속될 때 추가 이익을 확보하는 구간입니다.",
            "action": "추가 익절을 검토하고 남은 물량은 20일선 후행손절로 관리합니다."
        },
        {
            "label": "③ 1차 손절",
            "price": sl1,
            "condition": "단기 지지 이탈",
            "meaning": "현재 추세의 첫 번째 방어선이 무너지는 가격입니다.",
            "action": "신규매수는 중단하고 보유 중이면 일부 축소를 검토합니다."
        },
        {
            "label": "④ 2차 손절",
            "price": sl2,
            "condition": "중기 추세 이탈",
            "meaning": "중기 추세가 훼손될 가능성이 커지는 최종 방어가격입니다.",
            "action": "보유비중을 적극적으로 줄이고 추세 회복 전 재진입을 기다립니다."
        }
    ]

    cols = st.columns(4)
    for col, card in zip(cols, cards):
        with col:
            with st.container(border=True):
                st.markdown(f"**{card['label']}**")
                st.markdown(f"### {money(card['price'])}")
                st.caption(card["condition"])
                st.markdown(f"**의미**  \n{card['meaning']}")
                st.markdown(f"**대응**  \n{card['action']}")

    st.divider()

    if current <= sl2:
        state = "2차 손절선 하회"
        state_desc = "현재가가 중기 방어선까지 이탈했습니다. 신규매수보다 위험관리와 추세 회복 여부 확인이 우선입니다."
        action = "신규매수 보류 · 보유비중 축소 검토"
        trigger = f"2차 손절선 {money(sl2)} 회복 여부"
    elif current <= sl1:
        state = "1차 손절선 하회"
        state_desc = "단기 지지선이 무너졌습니다. 반등 확인 없이 추가매수하지 말고 2차 손절선 이탈 여부를 확인합니다."
        action = "추가매수 보류 · 반등 확인"
        trigger = f"1차 손절선 {money(sl1)} / 2차 손절선 {money(sl2)}"
    elif current >= tp2:
        state = "2차 익절구간"
        state_desc = "2차 목표가격에 도달했습니다. 일부 이익을 확보하고 남은 물량은 20일선 후행손절로 관리합니다."
        action = "2차 익절 검토 · 잔여물량 추세관리"
        trigger = f"20일선 {money(ma20)} 이탈 여부"
    elif current >= tp1:
        state = "1차 익절구간"
        state_desc = "1차 목표가격에 도달했습니다. 일부 이익을 확보한 뒤 상승 추세가 유지되는지 확인합니다."
        action = "1차 익절 검토 · 잔여물량 보유"
        trigger = f"2차 목표 {money(tp2)} / 20일선 {money(ma20)}"
    else:
        state = "보유·대기구간"
        state_desc = "아직 익절 또는 손절 기준에 도달하지 않았습니다. 추세가 유지되는 동안 목표가격과 손절선을 기준으로 대응합니다."
        action = "보유 관찰 · 기준가격 준수"
        trigger = f"1차 익절 {money(tp1)} / 1차 손절 {money(sl1)}"

    st.markdown("#### 지금은 어떻게 대응할까?")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("현재가", money(current))
        st.markdown(f"**현재 위치**  \n{state}")
        st.markdown(f"**권장 대응**  \n{action}")
    with c2:
        st.info(state_desc)
        st.markdown(f"**핵심 확인가격:** {trigger}")

def _theme_match(name, keywords):
    text = str(name or "").replace(" ", "").lower()
    return sum(1 for k in keywords if str(k).replace(" ", "").lower() in text)

def _theme_stage(score, rank, total):
    if score >= 78:
        return "현재 주도"
    if score >= 64:
        return "다음 수혜"
    if score >= 50:
        return "관심 확대"
    return "초기 관심"

def _benchmark_snapshot():
    df = load_price_data("069500")
    if df.empty:
        return {"ret20":0.0,"ret60":0.0}
    d = calculate_indicators(df)
    if d.empty:
        return {"ret20":0.0,"ret60":0.0}
    close = d["Close"]
    return {
        "ret20": safe_float(d["RET20"].iloc[-1]),
        "ret60": safe_float(close.pct_change(60).iloc[-1] * 100),
    }

def _score_theme(rows, benchmark):
    if not rows:
        return 0.0
    def avg(key):
        vals=[safe_float(x.get(key), np.nan) for x in rows]
        vals=[x for x in vals if np.isfinite(x)]
        return float(np.mean(vals)) if vals else 0.0
    ret20=avg("ret20"); ret60=avg("ret60"); vr=avg("vr")
    rs20=ret20-benchmark["ret20"]; rs60=ret60-benchmark["ret60"]
    breadth=avg("breadth"); ma60=avg("ma60_gap"); accel=avg("accel")
    rsi=avg("rsi")
    s=0.0
    s += np.clip((ret20+10)/30*100,0,100)*0.15
    s += np.clip((ret60+15)/50*100,0,100)*0.15
    s += np.clip((rs20+10)/30*100,0,100)*0.15
    s += np.clip((rs60+15)/50*100,0,100)*0.10
    s += np.clip((vr-0.6)/1.4*100,0,100)*0.15
    s += np.clip(breadth,0,100)*0.15
    s += np.clip((ma60+10)/30*100,0,100)*0.05
    s += np.clip((accel+10)/30*100,0,100)*0.05
    if 52 <= rsi <= 68: rsi_score=100
    elif 45 <= rsi < 52 or 68 < rsi <= 73: rsi_score=75
    elif 40 <= rsi < 45 or 73 < rsi <= 78: rsi_score=45
    else: rsi_score=20
    s += rsi_score*0.05
    return float(np.clip(s,0,100))

def build_future_theme_engine(force=False):
    cached=st.session_state.get("future_engine_cache")
    if cached and not force:
        if (datetime.now()-cached["time"]).total_seconds() < 1800:
            return cached["data"]

    universe=st.session_state.get("etf_universe",{})
    if not universe:
        universe=load_etf_universe()
        st.session_state.etf_universe=universe
    benchmark=_benchmark_snapshot()
    candidates=[]

    for theme, keywords in THEME_LEXICON.items():
        matched=[]
        for code,name in universe.items():
            hits=_theme_match(name,keywords)
            if hits:
                matched.append((hits, _normalize_etf_code(code), safe_etf_name(code,name)))
        matched.sort(key=lambda x:(x[0],x[2]), reverse=True)
        if len(matched)<2:
            continue
        rows=[]
        for hits,code,name in matched[:5]:
            df=load_price_data(code)
            if df.empty: continue
            d=calculate_indicators(df)
            if len(d)<65: continue
            r=d.iloc[-1]; close=d["Close"]
            ret20=safe_float(r.get("RET20")); ret60=safe_float(close.pct_change(60).iloc[-1]*100)
            ma20=safe_float(r.get("MA20"),safe_float(r.get("Close"))); ma60v=safe_float(r.get("MA60"),safe_float(r.get("Close")))
            current=safe_float(r.get("Close"))
            ret5=safe_float(r.get("RET5")); vr=safe_float(r.get("VOL_RATIO"),1); rsi=safe_float(r.get("RSI14"),50)
            breadth=100.0 if current>=ma20 else 0.0
            ma60_gap=(current/ma60v-1)*100 if ma60v else 0
            accel=ret5-(ret20/4 if np.isfinite(ret20) else 0)
            rows.append({"code":code,"name":name,"price":current,"rsi":rsi,"vr":vr,"ret":ret20,"ret20":ret20,"ret60":ret60,"ret5":ret5,"trend":"상승" if current>=ma20 else "조정","ma60_gap":ma60_gap,"breadth":breadth,"accel":accel,"hits":hits})
        if len(rows)<2: continue
        score=_score_theme(rows,benchmark)
        breadth=sum(1 for x in rows if x["ret20"]>0)/len(rows)*100
        for x in rows: x["breadth"]=breadth
        score=_score_theme(rows,benchmark)
        candidates.append({"theme":theme,"score":score,"rows":rows,"count":len(rows)})

    candidates.sort(key=lambda x:x["score"],reverse=True)
    candidates=[x for x in candidates if x["count"]>=2]
    chain=[]
    details={}
    total=len(candidates)
    for rank,item in enumerate(candidates,1):
        score=item["score"]
        stage="🔥 지금 주목" if score>=70 else ("🟡 관심" if score>=55 else "👀 관찰")
        item["stage"]=stage; item["rank"]=rank
        item["reason"]=THEME_REASONS.get(item["theme"],"전체 ETF 시장에서 가격·거래량·상대강도·추세가 함께 개선되는 테마를 자동 선별합니다.")
        chain.append((item["theme"],stage))
        details[item["theme"]]=item
    data={"chain":chain,"details":details,"benchmark":benchmark,"updated":datetime.now().strftime("%Y-%m-%d %H:%M")}
    st.session_state.future_engine_cache={"time":datetime.now(),"data":data}
    return data

def get_future_chain(force=False):
    return build_future_theme_engine(force).get("chain",[])

def future_theme_info(theme):
    return build_future_theme_engine().get("details",{}).get(theme,{})

def theme_candidates(theme):
    return [{"code":x["code"],"name":x["name"]} for x in future_theme_info(theme).get("rows",[])]

def theme_snapshot(theme):
    info=future_theme_info(theme)
    rows=info.get("rows",[])
    return rows

def render_future_inline_analysis():
    code = st.session_state.future_detail_code
    if not code:
        return

    theme = st.session_state.future_detail_theme
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

def future_stage_class(stage):
    if "현재 주도" in stage: return "stage-core"
    if "다음 수혜" in stage: return "stage-next"
    if "관심 확대" in stage: return "stage-interest"
    return "stage-early"

def future_outlook(theme, rows):
    if not rows: return "현재 가격 데이터를 충분히 확보하지 못했습니다."
    avg20=float(np.mean([x["ret20"] for x in rows])); avg60=float(np.mean([x["ret60"] for x in rows]))
    avg_rsi=float(np.mean([x["rsi"] for x in rows])); avg_vol=float(np.mean([x["vr"] for x in rows]))
    rising=sum(1 for x in rows if x["trend"]=="상승"); total=len(rows)
    return f"구성 ETF {rising}/{total}개가 20일선 위이며 20일 {avg20:+.1f}%, 60일 {avg60:+.1f}%, RSI {avg_rsi:.1f}, 거래량 {avg_vol:.2f}배입니다. 가격 상승뿐 아니라 확산도와 거래량을 함께 확인합니다."

def leading_signal(row, benchmark_ret20=0):
    current = safe_float(row.get("Close"), 0)
    ma20 = safe_float(row.get("MA20"), current)
    ma60 = safe_float(row.get("MA60"), current)
    ret5 = safe_float(row.get("RET5"), 0)
    ret20 = safe_float(row.get("RET20"), 0)
    vr = safe_float(row.get("VOL_RATIO"), 1)
    rsi = safe_float(row.get("RSI14"), 50)
    dist20 = (current / ma20 - 1) * 100 if ma20 else 0
    rs20 = ret20 - benchmark_ret20
    accel = ret5 - ret20 / 4
    early_price = 92 if -1 <= dist20 <= 3 else 82 if dist20 <= 5 else 65 if dist20 < 8 else 35
    early_rsi = 92 if 48 <= rsi <= 62 else 84 if 43 <= rsi < 68 else 68 if rsi < 72 else 35
    flow = 92 if 1.10 <= vr <= 1.70 else 82 if 1.0 <= vr < 1.10 else 76 if 0.9 <= vr < 1.0 else 58 if vr < 2.2 else 38
    accel_score = 90 if 0.5 <= accel <= 5 else 78 if 0 <= accel < 0.5 else 68 if accel > 5 else 52
    rel = 88 if rs20 >= 6 else 80 if rs20 >= 3 else 70 if rs20 >= 0 else 48
    structure = 90 if current >= ma60 and ma20 >= ma60 else 78 if current >= ma60 else 55 if current >= ma20 else 35
    score = round(early_price*.22 + early_rsi*.18 + flow*.22 + accel_score*.16 + rel*.14 + structure*.08)
    early_buy = score >= 72 and vr >= 1.05 and rsi < 70 and dist20 < 7 and rs20 >= -1
    return {"score": int(max(0,min(100,score))), "early_buy": bool(early_buy), "rs20": rs20, "dist20": dist20, "rsi": rsi, "vr": vr, "accel": accel}

def validated_price_zone(row):
    c = safe_float(row.get("Close"), 0)
    ma20 = safe_float(row.get("MA20"), c)
    ma60 = safe_float(row.get("MA60"), c)
    low20 = safe_float(row.get("LOW20"), c)
    support = max(low20, ma20 * 0.985)
    ideal_top = ma20 * 1.025
    invalid = min(ma60 * 0.97, support * 0.97)
    if c <= ideal_top and c >= invalid and c >= ma60 * 0.98:
        state = "매수구간"
    elif c < invalid:
        state = "무효"
    elif c > ma20 * 1.07:
        state = "추격금지"
    else:
        state = "눌림대기"
    return {"state": state, "support": support, "ideal_top": ideal_top, "invalid": invalid}

def validated_theme_score(rows, benchmark_ret20=0, benchmark_ret60=0):
    """백테스트의 C전략과 동일한 테마점수 계산.
    메인 앱의 기존 미래테마 점수와 섞지 않아 60점 기준의 의미를 보존합니다.
    """
    if len(rows) < 2:
        return 0.0

    vals = []
    for item in rows:
        ret20 = safe_float(item.get("ret20"), np.nan)
        ret60 = safe_float(item.get("ret60"), np.nan)
        if not np.isfinite(ret20) or not np.isfinite(ret60):
            continue
        vr = safe_float(item.get("vr"), 1)
        rsi = safe_float(item.get("rsi"), 50)
        ma60gap = safe_float(item.get("ma60_gap"), 0)
        accel = safe_float(item.get("accel"), ret20 * 0)
        code = item.get("code")
        df = load_price_data(code) if code else pd.DataFrame()
        if df.empty:
            continue
        d = calculate_indicators(df)
        if d.empty:
            continue
        sig = leading_signal(d.iloc[-1], benchmark_ret20)
        vals.append({
            "r20": ret20,
            "r60": ret60,
            "rs20": sig["rs20"],
            "rs60": ret60 - benchmark_ret60,
            "vr": vr,
            "ma60gap": ma60gap,
            "accel": sig["accel"],
            "rsi": rsi,
            "lead": sig["score"],
            "early": sig["early_buy"],
        })

    if len(vals) < 2:
        return 0.0

    x = pd.DataFrame(vals)
    def clip_score(v, lo, hi):
        return float(np.clip((v - lo) / (hi - lo) * 100, 0, 100))

    r20 = clip_score(x["r20"].mean(), -10, 15)
    r60 = clip_score(x["r60"].mean(), -15, 30)
    rs20 = clip_score(x["rs20"].mean(), -10, 12)
    rs60 = clip_score(x["rs60"].mean(), -15, 20)
    vr = clip_score(x["vr"].mean(), 0.8, 2.0)
    breadth = float((x["r20"] > -2).mean() * 100)
    ma60 = clip_score(x["ma60gap"].mean(), -10, 15)
    accel = clip_score(x["accel"].mean(), -5, 6)
    rsi = float(np.clip(100 - abs(float(x["rsi"].mean()) - 58) * 2.5, 0, 100))

    score = (
        r20 * 0.15 + r60 * 0.15 + rs20 * 0.15 + rs60 * 0.10
        + vr * 0.15 + breadth * 0.15 + ma60 * 0.05 + accel * 0.05 + rsi * 0.05
    )
    early_count = int(x["early"].sum())
    early_ratio = early_count / len(x)
    lead_avg = float(x["lead"].mean())
    lead_theme = lead_avg * 0.55 + breadth * 0.25 + early_ratio * 100 * 0.20
    final = score * 0.70 + lead_theme * 0.30

    heat = 0
    if float(x["rsi"].mean()) >= 75:
        heat += 12
    if float(x["r20"].mean()) >= 12:
        heat += 10
    if float(x["ma60gap"].mean()) >= 15:
        heat += 8
    return float(np.clip(final - heat, 0, 100))

def validated_cd_signal(row, theme_score, benchmark_ret20=0):
    lead = leading_signal(row, benchmark_ret20)
    zone = validated_price_zone(row)
    c_pass = safe_float(theme_score) >= 60 and lead["early_buy"]
    d_pass = c_pass and zone["state"] == "매수구간"
    if d_pass:
        state = "D · 매수구간"
    elif c_pass and zone["state"] == "눌림대기":
        state = "C · 눌림대기"
    elif c_pass and zone["state"] == "추격금지":
        state = "C · 추격금지"
    elif c_pass:
        state = "C · 관심"
    elif safe_float(theme_score) >= 60:
        state = "테마 통과 · 선행 미통과"
    else:
        state = "C 미통과"
    return {**lead, **zone, "theme_score": safe_float(theme_score), "c_pass": c_pass, "d_pass": d_pass, "state": state}

BACKTEST_POOL = {"QQQ":"나스닥100","XLK":"미국기술","SMH":"반도체","SOXX":"반도체","BOTZ":"로봇AI","ARKQ":"자동화로봇","HACK":"사이버보안","ITA":"방산","PAVE":"인프라","URA":"원전우라늄","LIT":"2차전지","XBI":"바이오","INDA":"인도","EWY":"한국","EWJ":"일본","EEM":"신흥국","GLD":"금","TLT":"미국장기채"}
BACKTEST_THEME_GROUPS = {"미국기술":["QQQ","XLK"],"반도체":["SMH","SOXX"],"로봇AI":["BOTZ","ARKQ"],"위험선호":["QQQ","XLK","SMH","SOXX","BOTZ","ARKQ"],"방어자산":["GLD","TLT"],"글로벌":["INDA","EWY","EWJ","EEM"]}

def fetch_us_price_data(code, force=False):
    key="US:"+str(code).upper(); now=datetime.now(); cached=st.session_state.price_cache.get(key)
    if cached and not force and (now-cached["time"]).total_seconds()<300: return cached["data"]
    try:
        df=normalize_df(yf.download(str(code).upper(),period="2y",interval="1d",auto_adjust=False,progress=False,threads=False))
        if not df.empty:
            st.session_state.price_cache[key]={"time":now,"data":df}; return df
    except Exception: pass
    return pd.DataFrame()

def backtest_benchmark_snapshot():
    df=fetch_us_price_data("SPY")
    if df.empty: return {"ret20":0.0,"ret60":0.0}
    d=calculate_indicators(df)
    return {"ret20":safe_float(d["RET20"].iloc[-1]),"ret60":safe_float(d["Close"].pct_change(60).iloc[-1]*100)} if not d.empty else {"ret20":0.0,"ret60":0.0}

def backtest_theme_rows(codes, benchmark):
    rows=[]
    for code in codes:
        df=fetch_us_price_data(code)
        if df.empty or len(df)<65: continue
        d=calculate_indicators(df); r=d.iloc[-1]
        ret20=safe_float(r.get("RET20"),np.nan); ret60=safe_float(d["Close"].pct_change(60).iloc[-1],np.nan)*100
        if not np.isfinite(ret20) or not np.isfinite(ret60): continue
        sig=leading_signal(r,benchmark["ret20"]); cur=safe_float(r.get("Close")); ma60=safe_float(r.get("MA60"),cur)
        rows.append({"code":code,"name":code,"ret20":ret20,"ret60":ret60,"vr":safe_float(r.get("VOL_RATIO"),1),"rsi":safe_float(r.get("RSI14"),50),"ma60_gap":(cur/ma60-1)*100 if ma60 else 0,"lead":sig["score"],"early":sig["early_buy"],"rs20":sig["rs20"],"accel":sig["accel"]})
    return rows

def backtest_theme_score(rows, benchmark):
    if len(rows)<2: return 0.0
    x=pd.DataFrame(rows)
    def clip(v,lo,hi): return float(np.clip((v-lo)/(hi-lo)*100,0,100))
    r20=clip(x.ret20.mean(),-10,15); r60=clip(x.ret60.mean(),-15,30); rs20=clip(x.rs20.mean(),-10,12); rs60=clip((x.ret60-benchmark["ret60"]).mean(),-15,20); vr=clip(x.vr.mean(),.8,2); breadth=float((x.ret20>-2).mean()*100); ma60=clip(x.ma60_gap.mean(),-10,15); accel=clip(x.accel.mean(),-5,6); rsi=float(np.clip(100-abs(x.rsi.mean()-58)*2.5,0,100))
    score=r20*.15+r60*.15+rs20*.15+rs60*.10+vr*.15+breadth*.15+ma60*.05+accel*.05+rsi*.05
    lead_theme=x.lead.mean()*.55+breadth*.25+x.early.mean()*100*.20
    final=score*.70+lead_theme*.30; heat=(12 if x.rsi.mean()>=75 else 0)+(10 if x.ret20.mean()>=12 else 0)+(8 if x.ma60_gap.mean()>=15 else 0)
    return float(np.clip(final-heat,0,100))

DOMESTIC_IMPLEMENTATION = {
    "QQQ": [
        {"name":"TIGER 미국나스닥100", "code":"133690", "match":"나스닥100 직접 추종", "horizon":"장기 코어 후보", "confidence":"높음"},
    ],
    "XLK": [
        {"name":"TIGER 미국테크TOP10 INDXX", "code":"381170", "match":"미국 대형 기술주 집중", "horizon":"장기 코어 + 중기 운용", "confidence":"중간"},
    ],
    "SMH": [
        {"name":"TIGER 미국필라델피아반도체나스닥", "code":"381180", "match":"미국 반도체 섹터", "horizon":"중기 + 장기 위성", "confidence":"높음"},
    ],
    "SOXX": [
        {"name":"TIGER 미국필라델피아반도체나스닥", "code":"381180", "match":"미국 반도체 섹터", "horizon":"중기 + 장기 위성", "confidence":"높음"},
    ],
    "BOTZ": [
        {"name":"TIGER 글로벌AI&로보틱스 INDXX", "code":"464310", "match":"AI·로봇 관련 글로벌 혁신기업", "horizon":"중기 위성", "confidence":"중간"},
    ],
    "ARKQ": [
        {"name":"TIGER 글로벌AI&로보틱스 INDXX", "code":"464310", "match":"AI·로봇 관련 글로벌 혁신기업", "horizon":"중기 위성", "confidence":"중간"},
    ],
    "GLD": [
        {"name":"TIGER 골드선물(H)", "code":"319640", "match":"금 가격", "horizon":"장기 분산자산", "confidence":"높음"},
    ],
    "TLT": [
        {"name":"TIGER 미국30년국채스트립액티브(합성 H)", "code":"458250", "match":"미국 장기국채", "horizon":"중장기 방어자산", "confidence":"중간"},
    ],
}

DOMESTIC_IMPLEMENTATION_CODES = {v["code"] for vals in DOMESTIC_IMPLEMENTATION.values() for v in vals}

def get_domestic_implementation(code):
    """미국 신호 ETF를 국내 상장 ETF 후보로 연결.
    없는 매핑은 억지로 만들지 않고 후보 없음으로 표시합니다.
    """
    return DOMESTIC_IMPLEMENTATION.get(str(code).upper(), [])

def domestic_quote(code):
    """국내 ETF 현재가와 가격구간/기술지표."""
    try:
        df = load_price_data(str(code))
        if df.empty:
            return {}
        d = calculate_indicators(df)
        if d.empty:
            return {}
        r = d.iloc[-1]
        current = safe_float(r.get("Close"), np.nan)
        ma20 = safe_float(r.get("MA20"), current)
        ma60 = safe_float(r.get("MA60"), current)
        low20 = safe_float(r.get("LOW20"), current)
        support = max(low20, ma20 * 0.985)
        ideal_top = ma20 * 1.025
        invalid = min(ma60 * 0.97, support * 0.97)
        if current <= ideal_top and current >= invalid and current >= ma60 * 0.98:
            state = "매수구간"
        elif current < invalid:
            state = "무효"
        elif current > ma20 * 1.07:
            state = "추격금지"
        else:
            state = "눌림대기"
        return {
            "price": current,
            "rsi": safe_float(r.get("RSI14"), np.nan),
            "ret20": safe_float(r.get("RET20"), np.nan),
            "ma20": ma20, "ma60": ma60, "low20": low20,
            "support": support, "ideal_top": ideal_top, "invalid": invalid,
            "state": state,
        }
    except Exception:
        return {}

def render_domestic_implementation_panel(candidates):
    """C/D 미국 신호를 실제 국내 상장 ETF 후보와 연결하는 실행 패널."""
    st.markdown(
        '<div class="cd-highlight" style="margin-top:10px;">'
        '<div class="cd-highlight-title">🇰🇷 국내 ETF 실행 연결</div>'
        '<div class="cd-highlight-sub">미국 ETF = 선행 신호 · 국내 상장 ETF = 실제 DC/IRP 투자 후보 · C/D는 진입시점 판단</div>'
        '</div>', unsafe_allow_html=True
    )

    shown = []
    for x in candidates[:8]:
        for item in get_domestic_implementation(x["code"]):
            q = domestic_quote(item["code"])
            shown.append((x, item, q))

    if not shown:
        st.info("현재 C/D 통과 신호에 연결할 국내 상장 ETF 후보가 없습니다. 미국 신호는 계속 참고용으로 표시됩니다.")
        return

    for x, item, q in shown[:8]:
        price_text = money(q["price"]) if np.isfinite(q.get("price", np.nan)) else "데이터 확인 필요"
        rsi_text = f'{q["rsi"]:.1f}' if np.isfinite(q.get("rsi", np.nan)) else "-"
        ret20_text = f'{q["ret20"]:+.2f}%' if np.isfinite(q.get("ret20", np.nan)) else "-"
        signal = "🟢 D" if x["d_pass"] else ("🟡 C" if x["c_pass"] else "⚪ 참고")
        st.markdown(
            f'<div class="cd-item">'
            f'<div class="theme-stage-wrap">'
            f'<span class="theme-stage-badge">{signal} → 국내 구현</span>'
            f'<span class="theme-stage-badge">{esc(item["horizon"])}</span>'
            f'<span class="theme-stage-badge">매칭 {esc(item["confidence"])}</span>'
            f'</div>'
            f'<div class="theme-summary-title">{esc(item["name"])}</div>'
            f'<span class="cd-code">국내 티커 · {esc(item["code"])} · 미국 신호 {esc(x["code"])}</span>'
            f'<div class="theme-summary-meta">{esc(item["match"])} · 현재가 {price_text} · RSI {rsi_text} · 20일 {ret20_text}</div>'
            f'<div class="theme-summary-outlook"><b>DC/IRP:</b> 국내상장 후보 · <b>보유:</b> {esc(item["horizon"])} · C/D는 중기 진입 신호이므로 장기 보유 판단과 분리</div>'
            f'</div>', unsafe_allow_html=True
        )

    st.caption("※ 국내 상장 여부와 별개로 실제 DC/IRP 편입 가능 상품 및 위험자산 한도는 가입 금융기관의 최신 상품목록에서 최종 확인합니다.")

BACKTEST_ETF_NAMES = {
    "QQQ":"Invesco QQQ Trust",
    "XLK":"Technology Select Sector SPDR Fund",
    "SMH":"VanEck Semiconductor ETF",
    "SOXX":"iShares Semiconductor ETF",
    "BOTZ":"Global X Robotics & Artificial Intelligence ETF",
    "ARKQ":"ARK Autonomous Technology & Robotics ETF",
    "HACK":"Amplify Cybersecurity ETF",
    "ITA":"iShares U.S. Aerospace & Defense ETF",
    "PAVE":"Global X U.S. Infrastructure Development ETF",
    "URA":"Global X Uranium ETF",
    "LIT":"Global X Lithium & Battery Tech ETF",
    "XBI":"SPDR S&P Biotech ETF",
    "INDA":"iShares MSCI India ETF",
    "EWY":"iShares MSCI South Korea ETF",
    "EWJ":"iShares MSCI Japan ETF",
    "EEM":"iShares MSCI Emerging Markets ETF",
    "GLD":"SPDR Gold Shares",
    "TLT":"iShares 20+ Year Treasury Bond ETF",
}

def get_backtest_cd_candidates():
    """검증 C/D 후보를 만들고, 부족하면 같은 테마의 차선 후보까지 확장한다."""
    benchmark=backtest_benchmark_snapshot(); themes=[]; strict=[]; pool=[]
    for theme,codes in BACKTEST_THEME_GROUPS.items():
        rows=backtest_theme_rows(codes,benchmark)
        score=backtest_theme_score(rows,benchmark)
        themes.append({"theme":theme,"score":score,"count":len(rows)})
        if score < 60:
            continue
        for row in rows:
            df=fetch_us_price_data(row["code"])
            if df.empty:
                continue
            d=calculate_indicators(df)
            if d.empty:
                continue
            last=d.iloc[-1]
            sig=leading_signal(last,benchmark["ret20"])
            zone=validated_price_zone(last)
            item={
                "theme":theme,"stage":"검증 C","name":row["code"],"code":row["code"],
                "theme_score":score,**sig,**zone,
                "c_pass":bool(score>=60 and sig["early_buy"]),
                "d_pass":bool(score>=60 and sig["early_buy"] and zone["state"]=="매수구간"),
                "state":"D · 매수구간" if score>=60 and sig["early_buy"] and zone["state"]=="매수구간" else (f"C · {zone['state']}" if score>=60 and sig["early_buy"] else "관찰")
            }
            pool.append(item)
            if item["c_pass"]:
                strict.append(item)

    # 동일 ETF가 여러 테마에 걸리면 가장 강한 신호만 유지
    def dedupe(rows):
        best={}
        for x in rows:
            k=x["code"]
            rank=(int(x.get("d_pass",False)),safe_float(x.get("theme_score"),0),safe_float(x.get("score"),0))
            if k not in best or rank > best[k][0]:
                best[k]=(rank,x)
        return [v[1] for v in best.values()]

    strict=dedupe(strict)
    pool=dedupe(pool)
    state_rank={"매수구간":4,"눌림대기":3,"추격금지":2,"무효":1}
    strict.sort(key=lambda x:(int(x["d_pass"]),state_rank.get(x["state"].split("·")[-1].strip(),0),x["theme_score"],x["score"]),reverse=True)
    pool.sort(key=lambda x:(int(x["d_pass"]),int(x["c_pass"]),state_rank.get(x["state"].split("·")[-1].strip(),0),x["theme_score"],x["score"]),reverse=True)

    # 1차: C 통과 후보. 2차: 같은 유망 테마의 차선 후보를 추가해 최대 3개 확보.
    selected=[]
    for x in strict + pool:
        if x["code"] not in {z["code"] for z in selected}:
            selected.append(x)
        if len(selected)>=3:
            break
    return selected,themes,benchmark

def _user_trade_plan(x):
    """가격구간을 40/30/30 매수와 추세형 익절/손절로 변환."""
    support=safe_float(x.get("support"),np.nan); top=safe_float(x.get("ideal_top"),np.nan)
    invalid=safe_float(x.get("invalid"),np.nan); current=safe_float(x.get("current"),np.nan)
    ma20=safe_float(x.get("ma20"),np.nan); ma60=safe_float(x.get("ma60"),np.nan)
    if not np.isfinite(support) or not np.isfinite(top): return {}
    buy1=top; buy2=(top+support)/2; buy3=support; entry=(buy1+buy2+buy3)/3
    base_stop=invalid if np.isfinite(invalid) else support*0.97
    if np.isfinite(ma60): base_stop=max(base_stop, ma60*0.97)
    risk=max(entry-base_stop,0)
    tp1=entry+risk
    tp2=entry+risk*2
    trail20=ma20*0.97 if np.isfinite(ma20) else base_stop
    return {"current":current,"buy1":buy1,"buy2":buy2,"buy3":buy3,"entry":entry,
            "stop":base_stop,"tp1":tp1,"tp2":tp2,"trail20":trail20}

def _trade_action(x):
    """내부 신호를 사용자 행동으로 번역."""
    plan=_user_trade_plan(x)
    if not plan:
        return "⚪ 관찰", "현재 가격 데이터를 충분히 확보하지 못했습니다.", "매수 보류", plan
    if x.get("d_pass"):
        return "🟢 지금 매수 검토", "현재 가격이 검증된 매수구간에 있습니다. 1차 40%부터 시작합니다.", "40% → 30% → 30%", plan
    state=str(x.get("state",""))
    if "눌림대기" in state:
        return "🟡 매수 대기", "상승 추세는 유효하지만 현재 가격이 매수구간보다 높습니다. 아래 가격대를 기다립니다.", "가격 도달 시 40% → 30% → 30%", plan
    if "추격금지" in state:
        return "🟠 추격매수 금지", "추세는 살아 있지만 단기 가격 부담이 큽니다. 매수구간으로 내려올 때까지 기다립니다.", "매수 보류", plan
    return "⚪ 관찰", "현재 선행조건이 충분하지 않습니다. 신규매수를 서두르지 않습니다.", "매수 보류", plan


def _rank_domestic_candidates(candidates):
    """미국 신호와 연결된 국내 ETF를 중복 없이 우선순위화."""
    rows=[]; seen=set()
    for x in candidates:
        domestic=get_domestic_implementation(x["code"])
        for item in domestic:
            key=item["code"]
            if key in seen: continue
            seen.add(key)
            priority=(3 if x.get("d_pass") else 2 if x.get("c_pass") else 1)
            rows.append((x,item,priority))
    rows.sort(key=lambda z:(z[2],safe_float(z[0].get("theme_score"),0),safe_float(z[0].get("score"),0)),reverse=True)
    return rows

def _rank_all_signal_candidates(candidates):
    """국내 매칭이 없는 경우에도 미국 선행 후보를 차선/관찰 후보로 확보."""
    rows=[]; seen=set()
    for x in candidates:
        key=x["code"]
        if key in seen: continue
        seen.add(key)
        domestic=get_domestic_implementation(key)
        if domestic:
            for item in domestic:
                rows.append((x,item,3 if x.get("d_pass") else 2))
        else:
            rows.append((x,{"name":BACKTEST_ETF_NAMES.get(key,key),"code":key,"match":"미국 선행 신호 ETF","horizon":"중기 운용","confidence":"참고"},1))
    rows.sort(key=lambda z:(z[2],int(bool(z[0].get("d_pass"))),safe_float(z[0].get("theme_score"),0),safe_float(z[0].get("score"),0)),reverse=True)
    return rows

def render_final_buy_panel(candidates):
    st.markdown('<div class="section-title">🎯 최종 매수 가이드</div>', unsafe_allow_html=True)
    st.caption("내부 C/D 신호는 숨기고, 실제 매수·익절·손절 행동으로 표시합니다.")
    ranked=_rank_all_signal_candidates(candidates)
    if not ranked:
        st.info("현재 조건을 만족하는 최종 후보가 없습니다.")
        return
    labels=["🥇 최우선", "🥈 차선", "🥉 관찰"]
    for rank,(x,item,_) in enumerate(ranked[:3]):
        q=domestic_quote(item["code"]) if item["code"] in DOMESTIC_IMPLEMENTATION_CODES else {}
        ux=dict(x)
        if q and np.isfinite(q.get("price",np.nan)):
            ux.update(q); ux["current"]=q["price"]; ux["d_pass"]=bool(x.get("d_pass")) and q.get("state")=="매수구간"
            ux["state"]="D · 매수구간" if ux["d_pass"] else f'C · {q.get("state",x.get("state",""))}'
        else:
            # 국내 매칭이 없으면 미국 신호의 검증 가격구간을 참고값으로 표시
            ux["current"]=safe_float(x.get("current"),np.nan)
        action,detail,split,plan=_trade_action(ux)
        if not plan: continue
        p1,p2,p3,stop,tp1,tp2,trail=[plan[k] for k in ("buy1","buy2","buy3","stop","tp1","tp2","trail20")]
        cur=plan.get("current"); current_text=money(cur) if np.isfinite(cur) else "-"
        name=item["name"]; code=item["code"]
        domestic_note="국내 상장 ETF" if code in DOMESTIC_IMPLEMENTATION_CODES else "미국 선행 신호(국내 매칭 후보 없음)"
        st.markdown(
            f'<div class="cd-highlight">'
            f'<div class="theme-stage-wrap"><span class="theme-stage-badge">{labels[rank]}</span><span class="theme-stage-badge">{esc(action)}</span></div>'
            f'<div class="cd-highlight-title">{esc(name)}</div>'
            f'<div class="cd-highlight-sub">{esc(domestic_note)} · 티커 {esc(code)} · 미국 선행 ETF {esc(x["code"])} · 현재가 {current_text}</div>'
            f'<div class="theme-data-grid">'
            f'<div class="theme-data-item"><div class="theme-data-label">1차 매수 40%</div><div class="theme-data-value">{money(p1)}</div></div>'
            f'<div class="theme-data-item"><div class="theme-data-label">2차 매수 30%</div><div class="theme-data-value">{money(p2)}</div></div>'
            f'<div class="theme-data-item"><div class="theme-data-label">3차 매수 30%</div><div class="theme-data-value">{money(p3)}</div></div>'
            f'<div class="theme-data-item"><div class="theme-data-label">손절 기준</div><div class="theme-data-value">{money(stop)}</div></div></div>'
            f'<div class="theme-summary-outlook"><strong>현재 판단</strong> · {esc(detail)}<br>'
            f'<strong>1차 익절</strong> · {money(tp1)} · <strong>2차 익절</strong> · {money(tp2)}<br>'
            f'<strong>추세 유지</strong> · 2차 익절 후 20일선 이탈({money(trail)})을 후행손절 기준으로 활용<br>'
            f'<strong>판단 근거</strong> · 테마 {safe_float(x.get("theme_score"),0):.0f}점 · 선행신호 {safe_float(x.get("score"),0):.0f}점 · {esc(item.get("horizon",""))}'
            f'</div></div>', unsafe_allow_html=True)

def render_validated_cd_panel():
    candidates,themes,benchmark=get_backtest_cd_candidates()
    st.markdown(
        '<div class="cd-highlight"><div class="cd-highlight-title">🎯 검증된 매수 후보</div>'
        '<div class="cd-highlight-sub">백테스트로 검증한 테마·선행조건·가격구간을 현재 시장에 적용합니다.</div></div>',
        unsafe_allow_html=True
    )
    if not candidates:
        st.info("현재 백테스트 검증 C 조건을 동시에 만족하는 ETF가 없습니다.")
        with st.expander("C/D 계산 현황 보기"):
            for x in sorted(themes,key=lambda z:z["score"],reverse=True):
                st.write(f'{x["theme"]} · 테마점수 {x["score"]:.1f} · 구성 {x["count"]}개')
        return
    st.markdown(f'<div class="cd-count">현재 조건 통과 <b>{len(candidates)}종목</b> · 즉시 매수구간 <b>{sum(1 for x in candidates if x["d_pass"])}종목</b></div>', unsafe_allow_html=True)
    for x in candidates[:8]:
        if x["d_pass"]:
            badge="🟢 지금 매수 검토"; desc=f'{us_money(x["support"])} ~ {us_money(x["ideal_top"])} 구간 분할매수 검토'
        elif x["state"]=="C · 눌림대기":
            badge="🟡 매수 대기"; desc=f'선행 조건 통과 · {us_money(x["support"])} 부근 눌림 대기'
        elif x["state"]=="C · 추격금지":
            badge="🟠 추격매수 금지"; desc="선행 조건 통과 · 현재가 추격매수 금지"
        else:
            badge="🟡 관심"; desc="선행 조건 확인 · 가격구간 대기"
        code=x["code"]
        display_name=BACKTEST_ETF_NAMES.get(code, code)
        st.markdown(
            f'<div class="cd-item"><div class="theme-stage-wrap"><span class="theme-stage-badge">{badge}</span>'
            f'<span class="theme-stage-badge">테마 {x["theme_score"]:.0f}</span><span class="theme-stage-badge">선행신호 {x["score"]}</span></div>'
            f'<div class="theme-summary-title">{esc(display_name)}</div><span class="cd-code">티커 · {esc(code)}</span>'
            f'<div class="theme-summary-meta">{esc(x["theme"])} · RSI {x["rsi"]:.1f} · 거래량 {x["vr"]:.2f}배 · 상대강도 {x["rs20"]:+.2f}%p</div>'
            f'<div class="theme-summary-outlook">{esc(desc)}</div></div>',
            unsafe_allow_html=True
        )

    render_domestic_implementation_panel(candidates)
    render_final_buy_panel(candidates)

def _theme_etf_rank(item, benchmark_ret20=0):
    ranked=[]
    for row in item.get("rows",[]):
        code=row.get("code")
        df=load_price_data(code) if code else pd.DataFrame()
        if df.empty: continue
        d=calculate_indicators(df)
        if d.empty: continue
        r=d.iloc[-1]
        sig=leading_signal(r, benchmark_ret20)
        zone=validated_price_zone(r)
        score=float(sig["score"])*0.65+float(item.get("score",0))*0.35
        ranked.append({**row,"signal_score":round(score),"zone":zone,"lead":sig,"raw":r})
    ranked.sort(key=lambda x:(x["signal_score"],x.get("ret20",-999)),reverse=True)
    return ranked

def _user_trade_guide(x):
    r=x.get("raw")
    if r is None: return None
    c=safe_float(r.get("Close"),np.nan); ma20=safe_float(r.get("MA20"),c); low20=safe_float(r.get("LOW20"),c); ma60=safe_float(r.get("MA60"),c)
    if not np.isfinite(c) or c<=0: return None
    support=max(low20,ma20*0.985); buy_top=ma20*1.025; invalid=min(ma60*0.97,support*0.97)
    if invalid<=0: invalid=c*0.92
    risk=max(buy_top-invalid,c*0.05)
    return {"buy1":buy_top,"buy2":(buy_top+invalid)/2,"buy3":invalid,"stop":invalid,"tp1":buy_top+risk,"tp2":buy_top+risk*2}

def _render_theme_etf_card(theme,item,rank,guide=False):
    name=item.get("name",item.get("code","-")); code=item.get("code","")
    domestic=get_domestic_implementation(code); dom=domestic[0] if domestic else None
    label={1:"🥇 최우선",2:"🥈 차선",3:"🥉 관찰"}.get(rank,f"{rank}순위")
    price=item.get("price",np.nan); zone=item.get("zone",{}).get("state","")
    action="지금 매수 검토" if zone=="매수구간" else "매수 대기" if zone=="눌림대기" else "추격매수 주의" if zone=="추격금지" else "관찰"
    display=dom["name"] if dom else name
    price_text=money(price) if np.isfinite(price) else "-"
    html=(f'<div class="theme-summary-card"><div class="theme-stage-wrap"><span class="theme-stage-badge">{label}</span>'
          f'<span class="theme-stage-badge">{action}</span></div><div class="theme-summary-title">{esc(display)}</div>'
          f'<div class="theme-summary-meta">{esc(theme)} · 신호점수 {item.get("signal_score",0):.0f} · 현재가 {price_text}</div>'
          f'<div class="theme-summary-outlook">미국 선행 ETF · {esc(code)} · 20일 {item.get("ret20",0):+.2f}% · RSI {item.get("rsi",0):.1f}</div></div>')
    st.markdown(html,unsafe_allow_html=True)
    if guide:
        g=_user_trade_guide(item)
        if g:
            guide_html=(f'<div class="cd-item"><div class="theme-summary-title">매수·매도 가이드</div>'
                        f'<div class="theme-summary-meta">1차 40% · {money(g["buy1"])} 이하</div>'
                        f'<div class="theme-summary-meta">2차 30% · {money(g["buy2"])} 이하</div>'
                        f'<div class="theme-summary-meta">3차 30% · {money(g["buy3"])} 이하</div>'
                        f'<div class="theme-summary-meta">손절 {money(g["stop"])} · 1차 익절 {money(g["tp1"])} · 2차 익절 {money(g["tp2"])}</div></div>')
            st.markdown(guide_html,unsafe_allow_html=True)

def render_future_theme():
    st.markdown('<div class="hero"><div class="hero-name">미래테마</div><div class="hero-code">유망 테마를 모두 유지하고 강도별로 정리합니다</div></div>',unsafe_allow_html=True)
    c1,c2=st.columns([1,1])
    with c1:
        if st.button("🔄 미래테마 업데이트",use_container_width=True,key="future_theme_refresh"):
            st.session_state.theme_cache={}; st.session_state.price_cache={}; st.session_state.future_engine_cache=None; st.rerun()
    with c2:
        auto_update=st.checkbox("⚡ 자동 업데이트 · 30분",value=False,key="future_auto_update")
        if auto_update and st_autorefresh is not None: st_autorefresh(interval=30*60*1000,key="future_theme_autorefresh")
    with st.spinner("테마와 ETF를 계산하는 중입니다…"):
        engine=build_future_theme_engine()
    chain=engine.get("chain",[]); details=engine.get("details",{})
    if not chain:
        st.warning("현재 가격 데이터에서 테마 후보를 찾지 못했습니다."); return
    bench=engine.get("benchmark",{})
    groups={"🔥 지금 주목":[],"🟡 관심":[],"👀 관찰":[]}
    for theme,stage in chain:
        if stage in groups: groups[stage].append((theme,stage))
    st.caption(f'기준시각 {engine.get("updated","-")} · 점수는 삭제 기준이 아니라 관심도 분류에 사용합니다.')
    for group,items in groups.items():
        if not items: continue
        st.markdown(f"### {group}")
        for theme,stage in items:
            info=details.get(theme,{})
            ranked=_theme_etf_rank(info,bench.get("ret20",0))
            st.markdown(f'<div class="theme-card"><div class="theme-title">{esc(theme)}</div><div class="theme-summary-meta">테마점수 {info.get("score",0):.0f} · ETF {len(ranked)}개</div></div>',unsafe_allow_html=True)
            for i,x in enumerate(ranked[:3],1):
                _render_theme_etf_card(theme,x,i,guide=(group=="🔥 지금 주목" and i==1))
            if len(ranked)>3:
                with st.expander(f"{theme} 나머지 ETF {len(ranked)-3}개 보기"):
                    for i,x in enumerate(ranked[3:],4): _render_theme_etf_card(theme,x,i,guide=False)
    st.markdown('<div class="section-title">테마 전체 목록</div>',unsafe_allow_html=True)
    for idx,(theme,stage) in enumerate(chain,1):
        info=details.get(theme,{})
        st.markdown(f'<div class="theme-summary-card"><div class="theme-stage-wrap"><span class="theme-stage-badge">{esc(stage)}</span><span class="theme-stage-badge">{info.get("score",0):.0f}점</span></div><div class="theme-summary-title">{idx}. {esc(theme)}</div></div>',unsafe_allow_html=True)


def get_benchmark_metrics():
    df = load_price_data("069500")
    if df.empty:
        return {"ret20": 0.0, "ret5": 0.0}
    d = calculate_indicators(df)
    if d.empty:
        return {"ret20": 0.0, "ret5": 0.0}
    row = d.iloc[-1]
    return {"ret20": safe_float(row.get("RET20", 0)), "ret5": safe_float(row.get("RET5", 0))}

def radar_theme_for(code, name):
    text=f"{code} {name}"
    best=None; hits=0
    for theme,keywords in THEME_LEXICON.items():
        h=_theme_match(text,keywords)
        if h>hits: best,hits=theme,h
    return best or "기타"

def radar_stage_for(theme):
    for t, stage in get_future_chain():
        if t == theme:
            return stage
    return "기타"

def radar_score(row):
    score = 0
    if row["above20"]: score += 12
    if row["above60"]: score += 13
    rs = row["rs20"]
    if rs >= 5: score += 20
    elif rs >= 2: score += 16
    elif rs > 0: score += 11
    elif rs > -3: score += 5
    vr = row["vr"]
    if 1.15 <= vr <= 2.0: score += 15
    elif 1.0 <= vr < 1.15: score += 9
    elif vr > 2.0: score += 7
    r20, r5 = row["ret20"], row["ret5"]
    if 2 <= r20 <= 15: score += 12
    elif 0 <= r20 < 2: score += 8
    elif r20 > 15: score += 5
    if -2 <= r5 <= 5: score += 8
    elif 5 < r5 <= 8: score += 4
    rsi, dist = row["rsi"], row["dist20"]
    if 50 <= rsi <= 68: score += 12
    elif 45 <= rsi < 50 or 68 < rsi <= 72: score += 7
    elif rsi < 40 or rsi > 78: score += 2
    if dist <= 4: score += 8
    elif dist <= 7: score += 5
    elif dist <= 10: score += 2
    return int(min(100, max(0, score)))

def radar_overheat_score(row):
    score = 0
    if row["rsi"] >= 75: score += 30
    elif row["rsi"] >= 70: score += 22
    elif row["rsi"] >= 67: score += 10
    if row["ret5"] >= 10: score += 25
    elif row["ret5"] >= 7: score += 18
    elif row["ret5"] >= 5: score += 10
    if row["dist20"] >= 12: score += 25
    elif row["dist20"] >= 8: score += 18
    elif row["dist20"] >= 5: score += 8
    if row["vr"] >= 2.0: score += 20
    elif row["vr"] >= 1.5: score += 14
    elif row["vr"] >= 1.2: score += 7
    return int(min(100, score))

def radar_target_etfs():
    """레이더 분석 대상은 전체 ETF가 아니라 '내 ETF + 미래테마 ETF'로 제한합니다."""
    targets = {}

    for raw_code in st.session_state.get("holdings", []):
        code = _normalize_etf_code(raw_code)
        if not code:
            continue
        name = get_etf_name(code)
        if not name or name.startswith("ETF "):
            live = lookup_live_etf(code)
            name = live or name
        targets[code] = name

    for theme, _stage in get_future_chain():
        try:
            for item in theme_candidates(theme):
                code = _normalize_etf_code(item.get("code"))
                name = item.get("name") or get_etf_name(code)
                if code and name and not str(name).startswith("ETF "):
                    targets[code] = name
        except Exception:
            continue

    return targets

def build_radar_data(force=False):
    now = datetime.now()
    cached = st.session_state.get("radar_cache")
    targets = radar_target_etfs()
    target_key = tuple(sorted(targets.keys()))
    if cached and not force:
        try:
            age = (now - cached["time"]).total_seconds()
            if age < 300 and cached.get("target_key") == target_key and "rows" in cached:
                return cached
        except Exception:
            pass

    benchmark = get_benchmark_metrics()
    rows = []
    for code, target_name in targets.items():
        name = target_name or get_etf_name(code)
        if not name or str(name).startswith("ETF "):
            continue
        df = load_price_data(code)
        if df.empty or len(df) < 65:
            continue
        try:
            d = calculate_indicators(df)
            if d.empty:
                continue
            r = d.iloc[-1]
        except Exception:
            continue
        current = safe_float(r["Close"])
        ma20 = safe_float(r["MA20"], current)
        ma60 = safe_float(r["MA60"], current)
        item = {
            "code": code, "name": name, "price": current,
            "rsi": safe_float(r["RSI14"], 50),
            "vr": safe_float(r["VOL_RATIO"], 1),
            "ret5": safe_float(r["RET5"], 0),
            "ret20": safe_float(r["RET20"], 0),
            "dist20": (current / ma20 - 1) * 100 if ma20 else 0,
            "above20": current >= ma20,
            "above60": current >= ma60,
        }
        item["rs20"] = item["ret20"] - benchmark["ret20"]
        item["theme"] = radar_theme_for(code, name)
        item["stage"] = radar_stage_for(item["theme"])
        item["opportunity"] = radar_score(item)
        item["overheat"] = radar_overheat_score(item)
        item["held"] = code in st.session_state.holdings
        rows.append(item)
    data = {"time": now, "rows": rows, "benchmark": benchmark, "target_key": target_key}
    st.session_state.radar_cache = data
    return data

def render_radar_card(item, mode):
    if mode == "🎯 기회검색":
        score = item["opportunity"]
        badge = '<span class="radar-badge radar-badge-op">기회 후보</span>'
        title = "강세는 확인되지만 단기 추격 위험은 상대적으로 낮은 후보"
    else:
        score = item["overheat"]
        badge = '<span class="radar-badge radar-badge-hot">과열 주의</span>'
        title = "단기 상승폭·RSI·이격·거래량을 함께 확인"
    held = '<span class="radar-badge radar-badge-hold">보유중</span>' if item["held"] else ''
    ret5_cls = "positive" if item["ret5"] >= 0 else "negative"
    ret20_cls = "positive" if item["ret20"] >= 0 else "negative"
    rs_cls = "positive" if item["rs20"] >= 0 else "negative"
    theme_text = f'{item["theme"]} · {item["stage"]}' if item["theme"] != "기타" else "테마 미분류"
    position = "20/60일선 위" if item["above20"] and item["above60"] else ("20일선 위 · 60일선 아래" if item["above20"] else "20일선 아래")
    st.markdown(f'''<div class="radar-card">
  <div>{badge}{held}</div>
  <div class="radar-title">{esc(item["name"])} · {esc(item["code"])}</div>
  <div class="radar-sub">{esc(title)} · {esc(theme_text)}</div>
  <div style="display:flex;justify-content:space-between;align-items:center;margin-top:7px;">
    <div><div class="radar-label">레이더 점수</div><div class="radar-score">{score}</div></div>
    <div style="text-align:right"><div class="radar-label">현재가</div><div class="radar-value">{money(item["price"])}</div></div>
  </div>
  <div class="radar-grid">
    <div class="radar-metric"><div class="radar-label">5일</div><div class="radar-value {ret5_cls}">{item["ret5"]:+.2f}%</div></div>
    <div class="radar-metric"><div class="radar-label">20일</div><div class="radar-value {ret20_cls}">{item["ret20"]:+.2f}%</div></div>
    <div class="radar-metric"><div class="radar-label">상대강도</div><div class="radar-value {rs_cls}">{item["rs20"]:+.2f}%p</div></div>
    <div class="radar-metric"><div class="radar-label">RSI / 거래량</div><div class="radar-value">{item["rsi"]:.1f} / {item["vr"]:.2f}배</div></div>
  </div>
  <div class="radar-note">20일선 대비 <b>{item["dist20"]:+.1f}%</b> · {position} · 점수는 신호를 정렬하기 위한 스크리닝 지표이며 수익을 보장하지 않습니다.</div>
</div>''', unsafe_allow_html=True)

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


def render_market_radar():
    st.markdown('<div class="hero"><div class="hero-name">🔥 시장 레이더</div><div class="hero-code">수급에 가까운 거래량 · 추세 · 상대강도 · 과열을 한 화면에서 확인</div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🔄 레이더 새로고침", use_container_width=True, key="radar_refresh"):
            st.session_state.radar_cache = None
            st.session_state.price_cache = {}
            st.rerun()
    with c2:
        st.caption("레이더는 내 ETF + 현재 미래테마 ETF만 분석합니다. 결과는 5분 캐시로 재사용합니다.")
    radar_modes = ["🎯 기회검색", "⚠️ 과열검색", "🔄 테마순환"]
    if hasattr(st, "segmented_control"):
        mode = st.segmented_control(
            "레이더 모드",
            options=radar_modes,
            default=st.session_state.get("radar_mode", radar_modes[0]),
            key="radar_mode",
            label_visibility="collapsed"
        )
    else:
        mode = st.radio(
            "레이더 모드",
            radar_modes,
            horizontal=True,
            key="radar_mode",
            label_visibility="collapsed"
        )
    if not mode:
        mode = st.session_state.get("radar_mode", radar_modes[0])

    with st.spinner("시장 레이더 데이터를 계산하는 중입니다…"):
        data = build_radar_data()
    rows = data["rows"]
    if not rows:
        st.warning("레이더에 사용할 가격 데이터가 없습니다.")
        return
    if mode == "🔄 테마순환":
        st.markdown("### 테마순환")
        theme_rows = []
        for theme, stage in get_future_chain():
            members = [x for x in rows if x["theme"] == theme]
            if not members:
                continue
            vals5 = [x["ret5"] for x in members if np.isfinite(x["ret5"])]
            vals20 = [x["ret20"] for x in members if np.isfinite(x["ret20"])]
            valsvr = [x["vr"] for x in members if np.isfinite(x["vr"])]
            if not vals5 or not vals20 or not valsvr:
                continue
            avg5 = float(np.mean(vals5))
            avg20 = float(np.mean(vals20))
            avgvr = float(np.mean(valsvr))
            breadth = sum(1 for x in members if x["ret5"] >= 0) / len(members) * 100
            strength = avg5 * 0.45 + avg20 * 0.25 + (avgvr - 1) * 10 + breadth * 0.10
            theme_rows.append({"theme":theme,"stage":stage,"avg5":avg5,"avg20":avg20,"avgvr":avgvr,"breadth":breadth,"strength":strength,"n":len(members)})
        theme_rows.sort(key=lambda x:x["strength"], reverse=True)
        for x in theme_rows:
            cls = "positive" if x["avg5"] >= 0 else "negative"
            st.markdown(f'<div class="radar-card"><span class="radar-badge">{esc(x["stage"])}</span><div class="radar-title">{esc(x["theme"])}</div><div class="radar-sub">구성 {x["n"]}개 · 단기 상승 비율 {x["breadth"]:.0f}%</div><div class="radar-grid"><div class="radar-metric"><div class="radar-label">5일 평균</div><div class="radar-value {cls}">{x["avg5"]:+.2f}%</div></div><div class="radar-metric"><div class="radar-label">20일 평균</div><div class="radar-value">{x["avg20"]:+.2f}%</div></div><div class="radar-metric"><div class="radar-label">거래량</div><div class="radar-value">{x["avgvr"]:.2f}배</div></div><div class="radar-metric"><div class="radar-label">상승비율</div><div class="radar-value">{x["breadth"]:.0f}%</div></div></div></div>', unsafe_allow_html=True)
        st.caption("테마순환은 각 테마 구성 ETF의 평균 수익률·거래량·상승 종목 비율을 이용한 상대 비교입니다.")
        return
    if mode == "🎯 기회검색":
        candidates = [x for x in rows if x["opportunity"] >= 55 and x["rsi"] < 72 and x["ret5"] < 8]
        candidates.sort(key=lambda x:(x["opportunity"], x["rs20"]), reverse=True)
        st.markdown("### 아직 안 오른 강세 후보")
        st.caption("상승 추세 + 상대강도 + 거래량을 보면서 최근 단기 급등과 과도한 이격은 감점합니다. '매수 신호'가 아니라 추적 우선순위를 정하는 화면입니다.")
        if not candidates:
            st.info("현재 조건을 동시에 만족하는 후보가 없습니다.")
        for item in candidates[:10]:
            render_radar_card(item, mode)
    else:
        candidates = [x for x in rows if x["overheat"] >= 35]
        candidates.sort(key=lambda x:(x["overheat"], x["ret5"]), reverse=True)
        st.markdown("### 단기 과열 후보")
        st.caption("RSI·단기 상승률·20일선 이격·거래량 급증을 함께 확인합니다. 과열은 상승 지속 여부와 별개의 경고 신호입니다.")
        if not candidates:
            st.info("현재 과열 조건을 강하게 충족하는 ETF가 없습니다.")
        for item in candidates[:10]:
            render_radar_card(item, mode)

init_state()

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">ETF RADAR</div>
        <div class="app-subtitle">ETF 추세 · 모멘텀 · 거래량 · 익절 · 손절</div>
    </div>
    """,
    unsafe_allow_html=True
)

nav = st.radio(
    "메뉴",
    ["📊 내 ETF", "🚀 미래테마", "🔥 시장 레이더"],
    horizontal=True,
    key="main_page",
    label_visibility="collapsed"
)

if nav == "📊 내 ETF":
    render_my_etf()
elif nav == "🚀 미래테마":
    render_future_theme()
else:
    render_market_radar()
