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
import ast
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None


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

/* ==========================================================
   READABILITY V2
   결과값을 우선 확대하고 기존 섹션 머리글은 유지합니다.
   ========================================================== */
.evidence-value { font-size: 1.00rem !important; color:#e3ebf3 !important; }
.evidence-sub { font-size: .72rem !important; color:#a8b8c8 !important; }
.judgment-main { font-size: 1.08rem !important; color:#e5edf5 !important; }
.judgment-reason, .action-main { font-size: .84rem !important; color:#c3cfda !important; }
.reason-label, .action-reason-label { font-size: .69rem !important; color:#91a5b8 !important; }
.scenario-price { font-size: 1.08rem !important; color:#e4ecf3 !important; }
.scenario-desc { font-size: .74rem !important; color:#aab9c8 !important; }
.holding-value { font-size: .98rem !important; color:#e0e8ef !important; }
.holding-detail { font-size: .76rem !important; color:#a1b1c1 !important; }
.theme-etf-name { font-size: .88rem !important; color:#e5edf5 !important; }
.theme-etf-code { font-size: .70rem !important; color:#8fa3b6 !important; }
.theme-data-label { font-size: .66rem !important; color:#8fa3b6 !important; }
.theme-data-value { font-size: .82rem !important; color:#e0e8ef !important; }
.theme-outlook { font-size: .80rem !important; color:#c7d3de !important; }
.theme-summary-title { font-size: .86rem !important; color:#e5edf5 !important; }
.theme-summary-meta { font-size: .74rem !important; color:#aab9c8 !important; }
.theme-summary-outlook { font-size: .78rem !important; color:#c4d0db !important; }
.summary-table td { font-size: .80rem !important; color:#d0dbe5 !important; }
.radar-value { font-size: .86rem !important; color:#e0e8ef !important; }
.radar-sub { font-size: .74rem !important; color:#a0b0c0 !important; }
.radar-label { font-size: .67rem !important; color:#91a5b8 !important; }
.radar-note { font-size: .74rem !important; color:#c1ced9 !important; }
.future-analysis-name { font-size: 1.12rem !important; color:#e6edf4 !important; }
.future-analysis-code { font-size: .72rem !important; color:#8fa3b6 !important; }

/* 자동판정의 핵심 결과값 */
.future-analysis .theme-outlook strong { color:#e6edf4 !important; }

/* ==========================================================
   DECISION UI V3
   운용전략 결과를 최우선으로 강조하고 가격 기준은 압축합니다.
   ========================================================== */
.strategy-section-title {
    font-size: 1.14rem !important;
    font-weight: 900 !important;
    color: #f0f5fa !important;
    margin: 17px 0 8px !important;
}
.strategy-result {
    background: #0d1d2d;
    border: 1px solid #416b8d;
    border-left: 4px solid #5da8d8;
    border-radius: 12px;
    padding: 13px 14px;
    margin-bottom: 10px;
}
.strategy-mode { font-size:.70rem; color:#a9bfd2 !important; font-weight:800; margin-bottom:2px; }
.strategy-main { font-size:1.34rem; line-height:1.25; font-weight:900; color:#f3f7fa !important; margin:2px 0 9px; }
.strategy-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:7px; }
.strategy-grid div { background:#091522; border-radius:8px; padding:8px; }
.strategy-grid span { display:block; font-size:.67rem; color:#91a7ba !important; margin-bottom:3px; }
.strategy-grid b { display:block; font-size:.91rem; color:#e6eef5 !important; line-height:1.3; }
.strategy-reason { margin-top:8px; font-size:.76rem; line-height:1.45; color:#b7c7d5 !important; }
.trade-section-title { font-size:.82rem !important; font-weight:850 !important; color:#cbd7e2 !important; margin:13px 0 5px !important; }
.trade-card-label { font-size:.68rem; color:#94a8ba !important; font-weight:800; }
.trade-card-price { font-size:.92rem; font-weight:900; color:#e6eef5 !important; margin-top:4px; }
.trade-card-price.small { font-size:.86rem; }
.trade-card-desc { font-size:.67rem; line-height:1.35; color:#aabac8 !important; margin-top:3px; }
[data-testid="stMetricValue"] { font-size:1.18rem !important; color:#edf4f8 !important; }
[data-testid="stMetricLabel"] { font-size:.68rem !important; color:#9db0c0 !important; }


@media (max-width:700px) {
    .evidence-value { font-size: .94rem !important; }
    .judgment-main { font-size: 1.00rem !important; }
    .judgment-reason, .action-main { font-size: .80rem !important; }
    .scenario-price { font-size: 1.02rem !important; }
    .scenario-desc { font-size: .72rem !important; }
    .theme-etf-name { font-size: .84rem !important; }
    .theme-data-value { font-size: .79rem !important; }
    .theme-summary-title { font-size: .84rem !important; }
    .theme-summary-meta { font-size: .72rem !important; }
    .theme-summary-outlook { font-size: .76rem !important; }
    .radar-value { font-size: .82rem !important; }
    .radar-sub { font-size: .72rem !important; }
    .future-analysis-name { font-size: 1.04rem !important; }
    .theme-outlook { font-size: .78rem !important; }
    .strategy-section-title { font-size: 1.06rem !important; }
    .strategy-main { font-size: 1.18rem !important; }
    .strategy-grid b { font-size: .84rem !important; }
    .strategy-grid { gap:5px; }
    .trade-card-price { font-size:.86rem !important; }
    [data-testid="stMetricValue"] { font-size:1.08rem !important; }
}


/* ==========================================================
   READABILITY V3 · MY ETF / FUTURE THEME
   모바일 결과값 가독성 우선
   ========================================================== */
.strategy-mode { font-size:.90rem !important; }
.strategy-main { font-size:1.65rem !important; }
.strategy-grid span { font-size:.86rem !important; }
.strategy-grid b { font-size:1.16rem !important; }
.strategy-reason { font-size:.96rem !important; }
.trade-section-title { font-size:.76rem !important; }
.trade-card-label { font-size:.82rem !important; }
.trade-card-price { font-size:.88rem !important; }
.trade-card-desc { font-size:.82rem !important; }
[data-testid="stMetricValue"] { font-size:1.42rem !important; }
[data-testid="stMetricLabel"] { font-size:.78rem !important; }

.theme-card .theme-stage-badge { font-size:.82rem !important; }
.theme-card .theme-title { font-size:1.42rem !important; }
.theme-card .theme-reason { font-size:1.00rem !important; line-height:1.55 !important; }
.theme-card .theme-outlook { font-size:1.00rem !important; line-height:1.55 !important; }
.theme-etf-name { font-size:1.30rem !important; line-height:1.35 !important; }
.theme-etf-code { font-size:.88rem !important; }
.theme-data-label { font-size:.82rem !important; }
.theme-data-value { font-size:1.08rem !important; }
.theme-etf-box > div:last-child { font-size:.84rem !important; color:#a9bac9 !important; }
.theme-summary-title { font-size:1.20rem !important; }
.theme-summary-meta { font-size:.94rem !important; }
.theme-summary-outlook { font-size:.98rem !important; line-height:1.55 !important; }
.future-analysis-title { font-size:.92rem !important; }
.future-analysis-name { font-size:1.42rem !important; }
.future-analysis-code { font-size:.90rem !important; }
.quote-price { font-size:1.35rem !important; }
.quote-change { font-size:.98rem !important; }

/* 미래테마는 기존 포맷 유지. ETF 분석 + 관심등록 두 버튼만 한 줄 */
.future-theme-buttons { display:flex !important; gap:.45rem !important; width:100% !important; }
.future-theme-buttons > div { flex:1 1 0 !important; min-width:0 !important; }

@media(max-width:700px){
  .strategy-main { font-size:1.48rem !important; }
  .strategy-grid span { font-size:.80rem !important; }
  .strategy-grid b { font-size:1.05rem !important; }
  .strategy-reason { font-size:.90rem !important; }
  .trade-card-label { font-size:.76rem !important; }
  .trade-card-price { font-size:.82rem !important; }
  .trade-card-desc { font-size:.76rem !important; }
  [data-testid="stMetricValue"] { font-size:1.28rem !important; }
  .theme-card .theme-title { font-size:1.28rem !important; }
  .theme-card .theme-reason, .theme-card .theme-outlook { font-size:.92rem !important; }
  .theme-etf-name { font-size:1.10rem !important; }
  .theme-etf-code { font-size:.82rem !important; }
  .theme-data-label { font-size:.76rem !important; }
  .theme-data-value { font-size:.98rem !important; }
  .theme-summary-title { font-size:1.08rem !important; }
  .theme-summary-meta { font-size:.86rem !important; }
  .theme-summary-outlook { font-size:.88rem !important; }
  .future-analysis-name { font-size:1.22rem !important; }
}


/* ==========================================================
   DECISION UI V4 · 상태별 단일 행동영역 + 미보유 가독성 강화
   ========================================================== */
.trade-section-title {
    font-size: 1.38rem !important;
    font-weight: 900 !important;
    color: #eef5fa !important;
    margin: 16px 0 7px !important;
}
.trade-card-label {
    font-size: 1.02rem !important;
    color: #b5c6d5 !important;
    font-weight: 900 !important;
}
.trade-card-price {
    font-size: 1.42rem !important;
    font-weight: 900 !important;
    color: #f0f6fa !important;
    margin-top: 5px !important;
}
.trade-card-price.small {
    font-size: 1.14rem !important;
}
.trade-card-desc {
    font-size: 1.00rem !important;
    line-height: 1.42 !important;
    color: #c0cfdb !important;
    margin-top: 4px !important;
}
@media(max-width:700px){
    .trade-section-title { font-size: 1.30rem !important; }
    .trade-card-label { font-size: .98rem !important; }
    .trade-card-price { font-size: 1.34rem !important; }
    .trade-card-price.small { font-size: 1.14rem !important; }
    .trade-card-desc { font-size: .94rem !important; }
}

/* ==========================================================
   FINAL UI FIX — ownership split + future theme 6-group layout
   ========================================================== */
.trade-section-title{font-size:1.18rem !important;font-weight:900 !important;color:#eef5fb !important;margin:16px 0 8px !important;}
.trade-card-label{font-size:.86rem !important;color:#cbd8e4 !important;}
.trade-card-price{font-size:1.20rem !important;color:#edf4f9 !important;font-weight:900 !important;}
.trade-card-price.small{font-size:1.08rem !important;}
.future-group-title{font-size:1.18rem !important;font-weight:900 !important;margin:18px 0 9px !important;padding:9px 12px !important;border-radius:10px !important;border:1px solid #416b8d !important;color:#f0f5fa !important;}
.future-group-priority{background:#152b3c !important;border-color:#4f86a9 !important;}
.future-group-secondary{background:#202a35 !important;border-color:#64778a !important;}
.future-group-watch{background:#252b31 !important;border-color:#66717b !important;}
.future-theme-headbox{border-radius:12px !important;padding:11px 13px !important;margin:8px 0 7px !important;}
.future-theme-headbox.future-group-priority{background:#102637 !important;border:1px solid #477fa4 !important;}
.future-theme-headbox.future-group-secondary{background:#18242f !important;border:1px solid #5d7182 !important;}
.future-theme-headbox.future-group-watch{background:#20272d !important;border:1px solid #66717b !important;}
.future-etf-card{background:#101b25 !important;border:1px solid #30485b !important;border-radius:11px !important;padding:12px !important;margin-bottom:7px !important;}
.future-rank-badge{display:inline-block !important;font-size:.82rem !important;font-weight:900 !important;color:#dfeaf3 !important;margin-bottom:4px !important;}
.future-etf-action{font-size:.90rem !important;font-weight:800 !important;color:#d6e4ee !important;margin:4px 0 7px !important;}
.future-etf-card .theme-etf-name{font-size:1.00rem !important;color:#edf4f9 !important;font-weight:900 !important;}
.future-etf-card .theme-etf-code{font-size:.78rem !important;color:#9eb1c2 !important;}
.future-etf-card .theme-data-label{font-size:.73rem !important;color:#9eb0c0 !important;}
.future-etf-card .theme-data-value{font-size:.92rem !important;color:#e3edf4 !important;font-weight:800 !important;}
[data-testid="stMetricValue"]{font-size:1.28rem !important;color:#edf5fa !important;}
@media(max-width:700px){.trade-section-title{font-size:1.10rem !important}.trade-card-price{font-size:1.10rem !important}.future-group-title{font-size:1.08rem !important}.future-etf-card .theme-etf-name{font-size:.94rem !important}.future-etf-card .theme-data-value{font-size:.86rem !important}.future-etf-action{font-size:.84rem !important}}
</style>
"""

if hasattr(st, "html"):
    st.html(CSS)
else:
    st.markdown(CSS, unsafe_allow_html=True)


# ============================================================
# FILES
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"


# ============================================================
# BASE ETF
# ============================================================

# ============================================================
# LIVE ETF MASTER
# 종목코드/종목명은 KRX + Naver Finance에서 실시간으로 구성합니다.
# 하드코딩된 ETF 종목명 목록은 사용하지 않습니다.
# ============================================================

BASE_ETFS = {}


DEFAULT_WATCHLIST = [
    "395160",
    "487240",
    "471990",
    "133690",
    "360750",
    "458730",
]


# ============================================================
# FUTURE THEME AUTO-UNIVERSE
# 고정 5개 테마를 사용하지 않고 전체 ETF 이름에서 테마 후보를 자동 발굴합니다.
# 동의어 사전은 테마를 찾기 위한 최소한의 언어 기준이며, 실제 표시 여부와 순위는
# 현재 ETF 유니버스와 가격 데이터로 결정됩니다.
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
    # KRX를 우선하고 Naver가 누락된 항목을 보완합니다.
    universe.update({k: v for k, v in krx.items() if v and not v.startswith("ETF ")})
    for code, name in naver.items():
        if code not in universe or not universe[code] or universe[code].startswith("ETF "):
            universe[code] = name
    return universe


# ============================================================
# STATE
# ============================================================

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


# ============================================================
# BASIC HELPERS
# ============================================================


def _name_has_hangul(text):
    return any("가" <= ch <= "힣" for ch in str(text))


def _looks_mojibake(text):
    t = str(text)
    bad = ("Ã", "Â", "â", "ê", "ë", "ì", "í", "î", "ï", "ð", "ñ", "�", "�")
    return any(x in t for x in bad)


def safe_etf_name(code, name=None):
    code = str(code).zfill(6)
    # 일부 캐시에는 ETF 레코드 전체가 문자열로 저장되어 있습니다.
    # 예: {'name': 'KODEX TRF3070', 'ticker': '329650.KS', 'themes': []}
    # 이 레코드 자체를 이름으로 표시하지 않고 name 필드만 추출합니다.
    if isinstance(name, dict):
        name = name.get("name") or name.get("etf_name") or name.get("title")

    text = html.unescape(str(name or "")).strip()
    if text.startswith("{") and "'name'" in text:
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, dict):
                text = str(parsed.get("name") or parsed.get("etf_name") or parsed.get("title") or "").strip()
        except Exception:
            # JSON/파이썬 dict 문자열이 완전하지 않은 경우에는 정규식으로 name만 추출
            m = re.search(r"['\"]name['\"]\s*:\s*['\"]([^'\"]+)['\"]", text)
            if m:
                text = m.group(1).strip()

    # HTML 엔티티가 남아 있거나 레코드 구조가 그대로 노출되는 경우도 차단합니다.
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


# ============================================================
# PRICE DATA
# ============================================================

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
    d["MA200"] = d["Close"].rolling(200).mean()

    delta = d["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta).clip(upper=0).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    d["RSI14"] = 100 - (100 / (1 + rs))

    d["VOL20"] = d["Volume"].rolling(20).mean()
    d["VOL_RATIO"] = d["Volume"] / d["VOL20"].replace(0, np.nan)

    d["RET5"] = d["Close"].pct_change(5) * 100
    d["RET20"] = d["Close"].pct_change(20) * 100
    d["RET60"] = d["Close"].pct_change(60) * 100
    d["RET120"] = d["Close"].pct_change(120) * 100
    d["RET250"] = d["Close"].pct_change(250) * 100

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
# HORIZON / VALIDATED C-D ENGINE
# ============================================================

def leading_signal(row, benchmark_ret20=0):
    current=safe_float(row.get("Close",0)); ma20=safe_float(row.get("MA20",current),current); ma60=safe_float(row.get("MA60",current),current)
    ret5=safe_float(row.get("RET5",row.get("R5",0)),0); ret20=safe_float(row.get("RET20",row.get("R20",0)),0)
    vr=safe_float(row.get("VOL_RATIO",row.get("VR",1)),1); rsi=safe_float(row.get("RSI14",row.get("RSI",50)),50)
    dist20=(current/ma20-1)*100 if ma20 else 0; rs20=ret20-benchmark_ret20; accel=ret5-ret20/4
    early_price=92 if -1<=dist20<=3 else 82 if dist20<=5 else 65 if dist20<8 else 35
    early_rsi=92 if 48<=rsi<=62 else 84 if 43<=rsi<68 else 68 if rsi<72 else 35
    flow=92 if 1.10<=vr<=1.70 else 82 if 1.0<=vr<1.10 else 76 if 0.9<=vr<1.0 else 58 if vr<2.2 else 38
    accel_score=90 if 0.5<=accel<=5 else 78 if 0<=accel<0.5 else 68 if accel>5 else 52
    rel=88 if rs20>=6 else 80 if rs20>=3 else 70 if rs20>=0 else 48
    structure=90 if current>=ma60 and ma20>=ma60 else 78 if current>=ma60 else 55 if current>=ma20 else 35
    score=round(early_price*.22+early_rsi*.18+flow*.22+accel_score*.16+rel*.14+structure*.08)
    early_buy=score>=72 and vr>=1.05 and rsi<70 and dist20<7 and rs20>=-1
    return {"score":int(np.clip(score,0,100)),"early_buy":bool(early_buy),"rs20":rs20,"dist20":dist20,"rsi":rsi,"vr":vr,"accel":accel}


def theme_score(theme_rows, bench_ret20=0, bench_ret60=0):
    if len(theme_rows)<2: return None
    vals=[]
    for r in theme_rows:
        r20=safe_float(r.get("ret20",r.get("R20")),np.nan); r60=safe_float(r.get("ret60",r.get("R60")),np.nan)
        if pd.isna(r20) or pd.isna(r60): continue
        sig=leading_signal(r,bench_ret20)
        vals.append({"r20":r20,"r60":r60,"rs20":sig["rs20"],"rs60":r60-bench_ret60,"vr":safe_float(r.get("vr",r.get("VR",1)),1),"ma60gap":safe_float(r.get("ma60_gap",0),0),"accel":sig["accel"],"rsi":sig["rsi"],"lead":sig["score"],"early":sig["early_buy"]})
    if len(vals)<2: return None
    x=pd.DataFrame(vals)
    def clip_score(v,lo,hi): return float(np.clip((v-lo)/(hi-lo)*100,0,100))
    r20=clip_score(x["r20"].mean(),-10,15); r60=clip_score(x["r60"].mean(),-15,30); rs20=clip_score(x["rs20"].mean(),-10,12); rs60=clip_score(x["rs60"].mean(),-15,20)
    vr=clip_score(x["vr"].mean(),.8,2); breadth=float((x["r20"]>-2).mean()*100); ma60=clip_score(x["ma60gap"].mean(),-10,15); accel=clip_score(x["accel"].mean(),-5,6)
    rsi=float(np.clip(100-abs(float(x["rsi"].mean())-58)*2.5,0,100))
    score=r20*.15+r60*.15+rs20*.15+rs60*.10+vr*.15+breadth*.15+ma60*.05+accel*.05+rsi*.05
    lead_theme=float(x["lead"].mean())*.55+breadth*.25+float(x["early"].mean())*100*.20
    heat=(12 if float(x["rsi"].mean())>=75 else 0)+(10 if float(x["r20"].mean())>=12 else 0)+(8 if float(x["ma60gap"].mean())>=15 else 0)
    return float(np.clip((score*.70+lead_theme*.30)-heat,0,100))


def validated_price_zone(row):
    c=safe_float(row.get("Close")); ma20=safe_float(row.get("MA20"),c); ma60=safe_float(row.get("MA60"),c); low20=safe_float(row.get("LOW20"),c)
    support=max(low20,ma20*.985); ideal_top=ma20*1.025; invalid=min(ma60*.97,support*.97)
    if c<=ideal_top and c>=invalid and c>=ma60*.98: state="매수구간"
    elif c<invalid: state="무효"
    elif c>ma20*1.07: state="추격금지"
    else: state="눌림대기"
    return {"state":state,"support":support,"ideal_top":ideal_top,"invalid":invalid}


def validated_cd_signal(row,tscore,benchmark_ret20=0):
    lead=leading_signal(row,benchmark_ret20); zone=validated_price_zone(row); c_pass=safe_float(tscore)>=60 and lead["early_buy"]; d_pass=c_pass and zone["state"]=="매수구간"
    if d_pass: state="D · 매수구간"
    elif c_pass and zone["state"]=="눌림대기": state="C · 눌림대기"
    elif c_pass and zone["state"]=="추격금지": state="C · 추격금지"
    elif c_pass: state="C · 관심"
    elif safe_float(tscore)>=60: state="테마 통과 · 선행 미통과"
    else: state="C 미통과"
    return {**lead,**zone,"theme_score":safe_float(tscore),"c_pass":c_pass,"d_pass":d_pass,"state":state}


def long_term_horizon(d):
    if d.empty or len(d)<200: return {"suitability":"데이터 부족","trend":"확인 불가","score":0,"reason":"장기 구조를 판단할 200일 데이터가 부족합니다."}
    r=d.iloc[-1]; c=safe_float(r["Close"]); ma60=safe_float(r["MA60"],c); ma120=safe_float(r["MA120"],c); ma200=safe_float(r["MA200"],c)
    ma200_prev=safe_float(d["MA200"].iloc[-21],ma200) if len(d)>=221 else ma200; ret120=safe_float(r.get("RET120"),0); ret250=safe_float(r.get("RET250"),0)
    gap200=(c/ma200-1)*100 if ma200 else 0; slope200=(ma200/ma200_prev-1)*100 if ma200_prev else 0
    structure=int(c>=ma200)+int(ma60>=ma200)+int(ma120>=ma200)+int(slope200>=0)
    score=float(np.clip(45+structure*12+np.clip(ret120,-10,20)*.5+np.clip(ret250,-20,40)*.15,0,100))
    if structure>=4 and gap200>=0: suitability="🟢 장기보유 적합"
    elif structure>=3 and gap200>=-3: suitability="🟡 보유+추세 확인"
    else: suitability="🔴 장기 적합성 재검토"
    if c>=ma200 and ma120>=ma200 and slope200>0: trend="📈 상승"
    elif c>=ma200 or ma120>=ma200: trend="🟡 조정/확인"
    else: trend="🔴 구조적 훼손"
    reason=f"현재가/200일선 {gap200:+.1f}% · 120일 {ret120:+.1f}% · 250일 {ret250:+.1f}% · 200일선 기울기 {slope200:+.2f}%"
    return {"suitability":suitability,"trend":trend,"score":int(round(score)),"reason":reason}


def _find_theme_for_etf(code):
    # 내 ETF 첫 진입 시 전체 미래테마 엔진을 다시 돌리지 않습니다.
    # 이미 생성된 캐시가 있으면 그대로 사용하고, 없으면 현재 ETF와 직접
    # 연관된 테마만 빠르게 계산하여 초기 로딩 지연을 줄입니다.
    code=str(code).zfill(6)
    try:
        cached=st.session_state.get("future_engine_cache")
        if cached:
            for theme,info in cached.get("data",{}).get("details",{}).items():
                rows=info.get("rows",[])
                if any(str(x.get("code")).zfill(6)==code for x in rows):
                    return theme,rows

        name=get_etf_name(code)
        matched_themes=[]
        for theme,keywords in THEME_LEXICON.items():
            hits=_theme_match(name,keywords)
            if hits:
                matched_themes.append((hits,theme,keywords))
        if not matched_themes:
            return None,[]
        matched_themes.sort(reverse=True)
        _,theme,keywords=matched_themes[0]
        universe=st.session_state.get("etf_universe",{})
        if not universe:
            universe=load_etf_universe(); st.session_state.etf_universe=universe
        candidates=[]
        for c,n in universe.items():
            h=_theme_match(n,keywords)
            if h:
                candidates.append((h,_normalize_etf_code(c),safe_etf_name(c,n)))
        candidates.sort(key=lambda x:(x[0],x[2]),reverse=True)
        rows=[]
        benchmark=_benchmark_snapshot()
        for _,c,n in candidates[:5]:
            df=load_price_data(c)
            if df.empty: continue
            d=calculate_indicators(df)
            if len(d)<65: continue
            r=d.iloc[-1]; close=d["Close"]
            ret20=safe_float(r.get("RET20")); ret60=safe_float(close.pct_change(60).iloc[-1]*100)
            ma20=safe_float(r.get("MA20"),safe_float(r.get("Close"))); ma60=safe_float(r.get("MA60"),safe_float(r.get("Close")))
            current=safe_float(r.get("Close")); ret5=safe_float(r.get("RET5")); vr=safe_float(r.get("VOL_RATIO"),1); rsi=safe_float(r.get("RSI14"),50)
            rows.append({"code":c,"name":n,"price":current,"rsi":rsi,"vr":vr,"ret20":ret20,"ret60":ret60,"ret5":ret5,"trend":"상승" if current>=ma20 else "조정","ma60_gap":((current/ma60-1)*100 if ma60 else 0),"breadth":(100.0 if current>=ma20 else 0.0),"accel":ret5-(ret20/4 if np.isfinite(ret20) else 0)})
        return (theme,rows) if rows else (None,[])
    except Exception:
        return None,[]


def horizon_engine(d,code):
    long=long_term_horizon(d)
    if d.empty: return {"long":long,"operation":"확인 불가","cd":None,"final":"확인 불가"}
    bench=_benchmark_snapshot(); theme,rows=_find_theme_for_etf(code); tscore=theme_score(rows,bench.get("ret20",0),bench.get("ret60",0)) if rows else None
    cd=validated_cd_signal(d.iloc[-1],tscore,bench.get("ret20",0)) if tscore is not None else None
    title=get_judgment(d)["title"]
    operation={"상승 추세 · 추격 주의":"🔥 단기 강세 · 추격 주의","상승 추세 유지":"🟢 보유·운용","단기 조정 · 중기 추세 확인":"🟡 눌림·추세 확인","중기 약세 · 방어 우선":"🔴 방어 우선"}.get(title,"⚪ 매수대기·방향 확인")
    return {"long":long,"operation":operation,"cd":cd,"theme":theme,"final":cd["state"] if cd else "C/D 산출 대기"}


def trade_levels(d, held=False, avg_price=0.0):
    """보유 여부에 따라 같은 가격 데이터를 다른 행동 기준으로 해석합니다."""
    if d.empty: return None
    c=safe_float(d["Close"].iloc[-1]); ma20=safe_float(d["MA20"].iloc[-1],c); ma60=safe_float(d["MA60"].iloc[-1],c)
    low20=safe_float(d["LOW20"].iloc[-1],c); low60=safe_float(d["LOW60"].iloc[-1],c)
    support=max(low20,ma20*.985)
    stop=min(ma60*.97,support*.97)
    stop=stop if stop>0 else c*.92
    if held and avg_price>0:
        entry=avg_price
        risk=max(entry-stop, c*.03)
        tp1=entry+risk
        tp2=entry+risk*2
        mode="보유중"
    else:
        entry=ma20*1.025
        risk=max(entry-stop,c*.05)
        tp1=entry+risk
        tp2=entry+risk*2
        mode="미보유"
    return {"entry":entry,"tp1":tp1,"tp2":tp2,"stop":stop,"support":support,"low60":low60,"mode":mode}


def render_horizon_strategy(d,code):
    h=horizon_engine(d,code); L=h["long"]; cd=h.get("cd")
    # 보유 여부 위젯의 현재 선택값을 즉시 반영합니다.
    # 저장 버튼을 누르기 전에도 화면이 미보유/보유중에 맞게 바뀌어야 합니다.
    holding=st.session_state.holdings.get(code) or {}
    held_widget=st.session_state.get(f"held_{code}", "보유중" if holding else "미보유")
    held=held_widget=="보유중"
    avg_price=safe_float(st.session_state.get(f"avg_{code}", holding.get("avg_price",0)),0) if held else 0

    # 가장 중요한 결과이므로 이 섹션만 일반 머리글보다 크게 강조합니다.
    st.markdown('<div class="strategy-section-title">🎯 운용전략 자동판정</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="strategy-result"><div class="strategy-mode">{"🟢 보유중" if held else "🔵 미보유"}</div><div class="strategy-main">{esc(L["suitability"])}</div><div class="strategy-grid"><div><span>📈 장기추세</span><b>{esc(L["trend"])}</b></div><div><span>🔥 현재운용</span><b>{esc(h["operation"])}</b></div><div><span>🎯 C/D 최종판정</span><b>{esc(h["final"])}</b></div></div><div class="strategy-reason">{esc(L["reason"])}</div></div>',unsafe_allow_html=True)

    if cd:
        c1,c2,c3=st.columns(3)
        with c1: st.metric("테마점수",f'{cd["theme_score"]:.0f}/100')
        with c2: st.metric("선행점수",f'{cd["score"]}/100')
        with c3: st.metric("현재구간",cd["state"].split("·")[-1].strip() if "·" in cd["state"] else cd["state"])
        st.caption(f'테마: {h.get("theme") or "-"} · RSI {cd["rsi"]:.1f} · 거래량 {cd["vr"]:.2f}배 · 20일선 이격 {cd["dist20"]:+.1f}%')
    else:
        st.caption("현재 ETF가 미래테마 엔진의 유효 테마에 포함되지 않아 C/D 판정을 확정하지 않았습니다.")

    lv=trade_levels(d,held,avg_price)
    if not lv: return

    # 보유 여부에 따라 필요한 행동 섹션만 표시합니다.
    # 미보유: 매수/대기/취소만 표시
    # 보유중: 익절/손절만 표시
    if not held:
        st.markdown('<div class="trade-section-title">미보유 · 가격별 행동</div>',unsafe_allow_html=True)
        st.caption("현재 보유하지 않은 ETF이므로 매수 후보 → 눌림대기 → 매수취소 순으로 판단합니다.")
        action_items=[
            ("현재가",safe_float(d["Close"].iloc[-1]),"현재 C/D 판정 확인"),
            ("🎯 매수 후보",lv["entry"],"20일선 + 2.5% 이내에서 조건 확인"),
            ("🟡 눌림대기",lv["support"],"지지 확인 후 분할 접근"),
            ("🛑 매수취소",lv["stop"],"핵심 지지 이탈")
        ]
        cols=st.columns(4)
        for col,(label,price,desc) in zip(cols,action_items):
            with col:
                with st.container(border=True):
                    st.markdown(f'<div class="trade-card-label">{esc(label)}</div><div class="trade-card-price">{money(price)}</div><div class="trade-card-desc">{esc(desc)}</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="trade-section-title">익절 · 손절 기준</div>',unsafe_allow_html=True)
        st.caption("보유중인 ETF는 매수 행동을 표시하지 않고, 평균매수가 기준의 익절·손절 기준만 표시합니다.")
        cards=[
            ("🎯 1차 익절",lv["tp1"],"1R · 일부 익절"),
            ("🎯 2차 익절",lv["tp2"],"2R · 추가 익절"),
            ("🛑 손절",lv["stop"],"핵심 지지 이탈 · 정리")
        ]
        cols=st.columns(3)
        for col,(label,price,desc) in zip(cols,cards):
            with col:
                with st.container(border=True):
                    st.markdown(f'<div class="trade-card-label">{esc(label)}</div><div class="trade-card-price small">{money(price)}</div><div class="trade-card-desc">{esc(desc)}</div>',unsafe_allow_html=True)
        st.caption("※ 2차 익절 이후에는 20일선 추적손절을 적용합니다. 손절은 하나의 명확한 기준으로 운영합니다.")

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

    current = safe_float(d["Close"].iloc[-1])
    ma20 = safe_float(d["MA20"].iloc[-1], current)
    ma60 = safe_float(d["MA60"].iloc[-1], current)
    high20 = safe_float(d["HIGH20"].iloc[-1], current)
    low20 = safe_float(d["LOW20"].iloc[-1], current)
    rsi = safe_float(d["RSI14"].iloc[-1], 50)
    vol_ratio = safe_float(d["VOL_RATIO"].iloc[-1], 1.0)

    st.markdown("### 핵심가격 · 대응 시나리오")
    st.caption("현재가를 기준으로 눌림 · 지지 · 돌파 · 위험 구간을 나누고, 각 가격에서 확인할 조건과 대응 방법을 제시합니다.")

    # --------------------------------------------------------
    # 1. 핵심 가격 4단계
    # HTML을 사용하지 않고 Streamlit 기본 컴포넌트만 사용합니다.
    # --------------------------------------------------------
    cards = [
        {
            "label": "① 1차 관심",
            "price": levels["first"],
            "condition": "20일선 부근 눌림",
            "meaning": "단기 상승 추세가 유지되는지 확인하는 첫 번째 가격대입니다.",
            "action": "급락 중 바로 매수하지 말고 가격이 20일선에서 멈추는지 확인합니다."
        },
        {
            "label": "② 핵심 지지",
            "price": levels["support"],
            "condition": "중기 추세 방어",
            "meaning": "최근 저점과 중기 이동평균을 기준으로 추세의 방어력을 확인합니다.",
            "action": "지지 + 거래량 안정이 확인될 때 분할 대응을 검토합니다."
        },
        {
            "label": "③ 돌파 기준",
            "price": levels["breakout"],
            "condition": "최근 20일 고점 돌파",
            "meaning": "최근 매물 부담을 넘어 새로운 단기 고점을 만드는 기준입니다.",
            "action": "가격만 돌파하지 말고 거래량 증가가 동반되는지 확인합니다."
        },
        {
            "label": "④ 위험 가격",
            "price": levels["risk"],
            "condition": "핵심 지지 이탈",
            "meaning": "중기 추세가 약해질 수 있어 신규 진입보다 방어가 우선되는 가격대입니다.",
            "action": "지지 회복 전까지 신규 매수는 보수적으로 접근합니다."
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

    # --------------------------------------------------------
    # 2. 현재가 위치 판정
    # --------------------------------------------------------
    if current < levels["risk"]:
        state = "핵심 지지 하회"
        state_desc = "현재가는 위험 가격 아래에 있습니다. 지금은 신규 진입보다 지지 회복 여부를 먼저 확인하는 구간입니다."
        action = "신규매수 보류 · 지지 회복 확인"
        trigger = f"{money(levels['risk'])} 회복 여부"
    elif current <= levels["support"] * 1.015:
        state = "핵심 지지 접근"
        state_desc = "핵심 지지구간에 접근했습니다. 가격이 지지를 지키고 거래량이 안정되는지가 중요합니다."
        action = "분할매수 검토 · 지지 확인"
        trigger = f"{money(levels['support'])} 지지 + 거래량 안정"
    elif current < levels["first"] * 1.015:
        state = "1차 관심구간"
        state_desc = "20일선 부근에서 눌림을 확인할 수 있는 구간입니다. 급등 추격보다 지지 확인이 유리합니다."
        action = "눌림매수 검토 · 추격 자제"
        trigger = f"20일선 {money(ma20)} 지지 확인"
    elif current >= levels["breakout"]:
        state = "돌파구간"
        state_desc = "최근 20일 고점 기준을 넘어선 상태입니다. 거래량이 동반되면 돌파의 신뢰도를 높일 수 있습니다."
        action = "돌파 확인 · 거래량 체크"
        trigger = f"거래량 {vol_ratio:.2f}배 이상 여부"
    else:
        state = "추세 유지구간"
        state_desc = "현재가는 주요 지지와 돌파 기준 사이에 있습니다. 방향이 확정되기 전에는 추격보다 눌림을 기다리는 전략이 적합합니다."
        action = "보유 관찰 · 눌림 대기"
        trigger = f"20일선 {money(ma20)} / 고점 {money(high20)}"

    # --------------------------------------------------------
    # 3. 현재 대응 + 판단 근거
    # --------------------------------------------------------
    st.markdown("#### 지금은 어떻게 대응할까?")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("현재가", money(current))
        st.markdown(f"**현재 위치**  \n{state}")
        st.markdown(f"**권장 대응**  \n{action}")
    with c2:
        st.info(state_desc)
        st.markdown(f"**핵심 확인조건:** {trigger}")

        evidence = []
        evidence.append(f"20일선 {money(ma20)} · {'상회' if current >= ma20 else '하회'}")
        evidence.append(f"60일선 {money(ma60)} · {'상회' if current >= ma60 else '하회'}")
        evidence.append(f"RSI14 {rsi:.1f} · {'과열권' if rsi >= 70 else ('약세권' if rsi <= 40 else '중립권')}")
        evidence.append(f"거래량 {vol_ratio:.2f}배 · {'증가' if vol_ratio >= 1.1 else ('감소' if vol_ratio < 0.8 else '평균권')}")
        st.caption(" · ".join(evidence))

    # --------------------------------------------------------
    # 4. 매매 시나리오를 한 줄로 정리
    # --------------------------------------------------------
    st.markdown("#### 가격대별 행동 기준")
    scenario_cols = st.columns(3)
    with scenario_cols[0]:
        st.markdown("**눌림 시나리오**")
        st.write(f"20일선 {money(ma20)} 부근까지 조정 → 지지 확인 → 거래량 안정 시 분할 접근")
    with scenario_cols[1]:
        st.markdown("**돌파 시나리오**")
        st.write(f"최근 고점 {money(high20)} 돌파 → 거래량 증가 확인 → 돌파 유지 여부 확인")
    with scenario_cols[2]:
        st.markdown("**이탈 시나리오**")
        st.write(f"위험 가격 {money(levels['risk'])} 이탈 → 신규매수 보류 → 지지 회복 여부 재확인")


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

    if "MA200" in chart_df.columns:
        fig.add_trace(
            go.Scatter(x=chart_df.index, y=chart_df["MA200"], mode="lines", line=dict(color="#7b6fa8", width=1.1), name="200일선"),
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

def lookup_live_etf(code):
    """신규/누락 ETF는 KRX → Naver → Yahoo 순으로 이름을 확인합니다."""
    code = _normalize_etf_code(code)
    if not code:
        return ""

    for source in (fetch_krx_etf_master(), fetch_naver_etf_master()):
        name = source.get(code)
        if name and not name.startswith("ETF "):
            st.session_state.etf_universe[code] = name
            return name

    try:
        info = yf.Ticker(f"{code}.KS").info
        name = info.get("shortName") or info.get("longName") or ""
        name = safe_etf_name(code, name)
        if name and not name.startswith("ETF "):
            st.session_state.etf_universe[code] = name
            return name
    except Exception:
        pass

    return f"ETF {code}"


def lookup_yahoo_etf_name(code):
    # 기존 함수명 호환. 실제 조회는 KRX/Naver를 먼저 사용합니다.
    return lookup_live_etf(code)


def search_etfs(query):
    # 검색 결과는 항상 내부 코드 + 안전하게 정제된 ETF명으로 구성합니다.
    # 특히 최신 ETF는 캐시 파일에 아직 없어도 '종목코드 직접 검색'으로 찾을 수 있어야 합니다.
    query_raw = (query or "").strip()
    query = query_raw.lower()
    if not query:
        return []

    results = []
    seen = set()

    # 1) 기존 ETF universe 검색
    for raw_code, raw_name in st.session_state.etf_universe.items():
        code = str(raw_code).strip().upper()
        # 숫자 코드는 6자리로 정규화하고, 신규 영문+숫자 코드는 그대로 유지합니다.
        if code.isdigit():
            code = code.zfill(6)
        name = get_etf_name(code)
        if code in seen:
            continue

        search_name = str(name).strip().lower()
        if query in code.lower() or query in search_name:
            results.append({"code": code, "name": name})
            seen.add(code)

    # 2) universe에 아직 없는 신규 ETF도 정확한 종목코드로 직접 검색
    # 예: 490490, 0173Y0
    compact = query_raw.replace(".", "").replace("-", "").strip().upper()
    if re.fullmatch(r"[0-9A-Z]{6}", compact):
        code = compact
        if code not in seen:
            name = lookup_yahoo_etf_name(code)
            results.insert(0, {"code": code, "name": name})
            st.session_state.etf_universe[code] = name
            seen.add(code)

    return results[:30]


# ============================================================
# WATCHLIST
# ============================================================

def add_watch(code):
    code = _normalize_etf_code(code)
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
        result_map = {str(x["code"]).zfill(6): x for x in results}
        result_codes = list(result_map.keys())
        selected_code = st.selectbox(
            "검색 결과",
            result_codes,
            format_func=lambda code: f'{get_etf_name(code)} · {code}',
            key="search_result"
        )
        item = result_map[str(selected_code).zfill(6)]

        c1, c2 = st.columns([4, 1])
        with c1:
            st.caption(f'선택: {item["name"]} ({item["code"]})')
        with c2:
            already = item["code"] in st.session_state.watchlist
            if st.button("추가" if not already else "등록됨", disabled=already, use_container_width=True, key=f'add_{item["code"]}'):
                add_watch(item["code"])
                st.rerun()
    elif query:
        st.caption("검색 결과가 없습니다.")


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

    selected_code = st.selectbox(
        "관심종목 선택",
        watchlist,
        index=default_index,
        format_func=lambda code: f'{get_etf_name(code)} · {code}',
        key="watch_select"
    )
    code = str(selected_code).zfill(6)
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
    render_horizon_strategy(d, code)

    st.markdown('<div class="section-title">가격 흐름 · 최근 6개월</div>', unsafe_allow_html=True)
    render_chart(d)


# ============================================================
# FUTURE THEME ENGINE
# ============================================================

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
    # 100점: 수익률보다 상대강도·확산·거래량·추세를 균형 있게 반영
    s=0.0
    s += np.clip((ret20+10)/30*100,0,100)*0.15
    s += np.clip((ret60+15)/50*100,0,100)*0.15
    s += np.clip((rs20+10)/30*100,0,100)*0.15
    s += np.clip((rs60+15)/50*100,0,100)*0.10
    s += np.clip((vr-0.6)/1.4*100,0,100)*0.15
    s += np.clip(breadth,0,100)*0.15
    s += np.clip((ma60+10)/30*100,0,100)*0.05
    s += np.clip((accel+10)/30*100,0,100)*0.05
    # RSI는 지나친 과열을 감점하되 강세권은 가점
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

    # 전체 ETF를 테마별로 자동 매칭합니다. 특정 테마를 무조건 노출하지 않습니다.
    for theme, keywords in THEME_LEXICON.items():
        matched=[]
        for code,name in universe.items():
            hits=_theme_match(name,keywords)
            if hits:
                matched.append((hits, _normalize_etf_code(code), safe_etf_name(code,name)))
        matched.sort(key=lambda x:(x[0],x[2]), reverse=True)
        # 같은 테마가 ETF 하나뿐이면 통계적으로 불안정하므로 제외
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
        # ETF간 평균으로 다시 확산도를 계산하여 단일 급등 종목의 왜곡을 줄입니다.
        breadth=sum(1 for x in rows if x["ret20"]>0)/len(rows)*100
        for x in rows: x["breadth"]=breadth
        score=_score_theme(rows,benchmark)
        candidates.append({"theme":theme,"score":score,"rows":rows,"count":len(rows)})

    candidates.sort(key=lambda x:x["score"],reverse=True)
    # 너무 작은/약한 테마는 미래테마에서 제외하고 상위 8개까지만 표시합니다.
    candidates=[x for x in candidates if x["score"]>=42][:8]
    chain=[]
    details={}
    total=len(candidates)
    for rank,item in enumerate(candidates,1):
        stage=_theme_stage(item["score"],rank,total)
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


# ============================================================

# INLINE FUTURE ETF ANALYSIS
# ============================================================

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
    st.markdown('<div class="section-title">가격 흐름 · 최근 6개월</div>', unsafe_allow_html=True)
    render_chart(d)


# ============================================================
# FUTURE THEME
# ============================================================

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


def _theme_etf_rank(item, benchmark_ret20=0):
    """미래테마 내 ETF 순위 계산.
    기존 테마 엔진의 선행점수/가격구간 로직을 그대로 사용합니다.
    """
    ranked = []
    for row in item.get("rows", []):
        code = row.get("code")
        df = load_price_data(code) if code else pd.DataFrame()
        if df.empty:
            continue
        d = calculate_indicators(df)
        if d.empty:
            continue
        r = d.iloc[-1]
        sig = leading_signal(r, benchmark_ret20)
        zone = validated_price_zone(r)
        score = float(sig["score"]) * 0.65 + float(item.get("score", 0)) * 0.35
        ranked.append({
            **row,
            "signal_score": round(score),
            "zone": zone,
            "lead": sig,
            "raw": r,
            "rsi": safe_float(sig.get("rsi"), 50),
            "ret20": safe_float(row.get("ret20", r.get("RET20", 0)), 0),
        })
    ranked.sort(
        key=lambda x: (x["signal_score"], x.get("ret20", -999)),
        reverse=True
    )
    return ranked


def render_future_theme():
    st.markdown('<div class="hero"><div class="hero-name">미래테마</div><div class="hero-code">유망 테마 TOP 6 · 강한 테마부터 압축 선별</div></div>',unsafe_allow_html=True)
    uc1,uc2=st.columns([1,1])
    with uc1:
        if st.button("🔄 미래테마 업데이트",use_container_width=True,key="future_theme_refresh"):
            st.session_state.theme_cache={}; st.session_state.price_cache={}; st.session_state.future_engine_cache=None; st.rerun()
    with uc2:
        auto_update=st.checkbox("⚡ 자동 업데이트 · 30분",value=False,key="future_auto_update")
        if auto_update and st_autorefresh is not None: st_autorefresh(interval=30*60*1000,key="future_theme_autorefresh")

    with st.spinner("테마와 ETF를 계산하는 중입니다…"):
        engine=build_future_theme_engine()
    chain=engine.get("chain",[])[:6]
    if not chain:
        st.warning("현재 가격 데이터에서 테마 후보를 찾지 못했습니다.")
        return
    bench=engine.get("benchmark",{})
    details=engine.get("details",{})
    st.caption(f'기준시각 {engine.get("updated","-")} · 전체 테마를 계산한 뒤 상위 6개만 화면에 표시합니다.')

    # 화면은 순위만으로 3단계로 구분합니다. 엔진의 점수 계산 로직은 변경하지 않습니다.
    groups=[("🥇 최우선",chain[:2],"future-group-priority"),
            ("🥈 우선",chain[2:4],"future-group-secondary"),
            ("👀 관찰",chain[4:6],"future-group-watch")]

    for group_label,items,group_cls in groups:
        if not items:
            continue
        st.markdown(f'<div class="future-group-title {group_cls}">{group_label}</div>',unsafe_allow_html=True)
        for theme,stage in items:
            info=details.get(theme,{})
            ranked=_theme_etf_rank(info,bench.get("ret20",0))
            if not ranked:
                continue
            score=safe_float(info.get("score",0),0)
            # 기존 테마/ETF 정보 포맷을 유지하면서 테마 박스만 강조합니다.
            st.markdown(
                f'<div class="future-theme-headbox {group_cls}">'
                f'<div class="theme-title">{esc(theme)}</div>'
                f'<div class="theme-summary-meta">테마점수 {score:.0f} · ETF {len(ranked)}개</div>'
                f'</div>',unsafe_allow_html=True)

            for i,item in enumerate(ranked[:3],1):
                name=item.get("name",item.get("code","-")); code=item.get("code","")
                price=item.get("price",np.nan)
                price_text=money(price) if np.isfinite(price) else "-"
                zone=item.get("zone",{}).get("state","")
                action=("지금 매수 검토" if zone=="매수구간" else
                        "매수 대기" if zone=="눌림대기" else
                        "추격매수 주의" if zone=="추격금지" else "관찰")
                ret_cls="positive" if safe_float(item.get("ret20"),0)>=0 else "negative"
                label={1:"🥇 최우선",2:"🥈 우선",3:"👀 관찰"}.get(i,"관찰")
                st.markdown(
                    f'<div class="future-etf-card">'
                    f'<div class="future-rank-badge">{label}</div>'
                    f'<div class="theme-etf-name">{esc(name)}</div>'
                    f'<div class="theme-etf-code">{esc(code)}</div>'
                    f'<div class="future-etf-action">{esc(action)}</div>'
                    f'<div class="theme-data-grid">'
                    f'<div class="theme-data-item"><div class="theme-data-label">현재가</div><div class="theme-data-value">{price_text}</div></div>'
                    f'<div class="theme-data-item"><div class="theme-data-label">신호점수</div><div class="theme-data-value">{safe_float(item.get("signal_score"),0):.0f}</div></div>'
                    f'<div class="theme-data-item"><div class="theme-data-label">RSI</div><div class="theme-data-value">{safe_float(item.get("rsi"),0):.1f}</div></div>'
                    f'<div class="theme-data-item"><div class="theme-data-label">20일</div><div class="theme-data-value {ret_cls}">{safe_float(item.get("ret20"),0):+.2f}%</div></div>'
                    f'</div></div>',unsafe_allow_html=True)

                # 반드시 한 줄에 좌우 2개 Streamlit 버튼으로 렌더링합니다.
                b1,b2=st.columns(2)
                is_open=st.session_state.future_detail_code==code
                with b1:
                    if st.button("분석 닫기" if is_open else "ETF 분석",key=f"theme_an_{theme}_{i}_{code}",use_container_width=True):
                        st.session_state.future_detail_code=None if is_open else code
                        st.session_state.future_detail_theme=None if is_open else theme
                        st.rerun()
                with b2:
                    already=code in st.session_state.watchlist
                    if st.button("⭐ 관심등록" if not already else "⭐ 등록됨",disabled=already,key=f"theme_watch_{theme}_{i}_{code}",use_container_width=True):
                        add_watch(code)
                        st.session_state.selected_code=code
                        st.rerun()
                if is_open:
                    render_future_inline_analysis()



# MARKET RADAR
# ============================================================

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

    # 1) 보유 ETF는 항상 레이더에 포함
    for raw_code in st.session_state.get("holdings", []):
        code = _normalize_etf_code(raw_code)
        if not code:
            continue
        name = get_etf_name(code)
        if not name or name.startswith("ETF "):
            live = lookup_live_etf(code)
            name = live or name
        targets[code] = name

    # 2) 현재 미래테마에 등록/검색되는 ETF만 추가
    for theme, _stage in get_future_chain():
        try:
            for item in theme_candidates(theme):
                code = _normalize_etf_code(item.get("code"))
                name = item.get("name") or get_etf_name(code)
                if code and name and not str(name).startswith("ETF "):
                    targets[code] = name
        except Exception:
            # 특정 테마 데이터 오류가 전체 레이더를 막지 않도록 방어
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
    # 모바일에서 radio의 선택 상태가 잘 보이지 않거나 터치가 씹히는 문제를 피하기 위해
    # Streamlit segmented_control을 우선 사용합니다. (구버전 Streamlit은 radio로 자동 fallback)
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
