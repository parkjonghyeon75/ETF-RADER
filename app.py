# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import json
import os
import io
import zipfile
import html
import ast
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, date, time as datetime_time
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed

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
   FINAL TARGET
   ========================================================== */
.final-target-hero { background: linear-gradient(135deg, #10263a, #0b1725); border:1px solid #39627f; border-radius:13px; padding:13px; margin:8px 0 12px; }
.final-target-title { font-size:1.12rem; font-weight:900; color:#e5edf4 !important; }
.final-target-sub { font-size:.70rem; color:#8ea6ba !important; margin-top:4px; line-height:1.45; }
.final-target-rank { font-size:.66rem; font-weight:850; color:#70b8e8 !important; }
.final-horizon-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:6px; margin-top:8px; }
.final-horizon-box { background:#091522; border:1px solid #20374c; border-radius:8px; padding:7px; }
.final-horizon-label { font-size:.58rem; color:#70859a !important; }
.final-horizon-value { font-size:.72rem; font-weight:850; color:#d4e0ea !important; margin-top:2px; }
@media (max-width: 640px) { .final-horizon-grid { grid-template-columns:1fr; } }

/* ==========================================================
   MARKET RADAR
   ========================================================== */
.radar-card { background:#0d1928; border:1px solid #263e54; border-radius:10px; padding:11px; margin-bottom:7px; }
.radar-title { font-size:.92rem; font-weight:850; color:#dce6ef !important; }
.final-target-name { font-size:1.02rem !important; margin:2px 0 5px !important; }
.final-target-name + * { }
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
.radar-trade-title { margin-top:10px; padding-top:9px; border-top:1px solid #22384d; font-size:.76rem; font-weight:900; color:#dce6ef !important; }
.radar-action { margin-top:5px; padding:8px 9px; border-radius:7px; background:#0a1826; border-left:3px solid #4f8eb8; color:#e1eaf2 !important; font-size:.78rem; font-weight:850; line-height:1.4; }
.radar-trade-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:5px; margin-top:7px; }
.radar-trade-item { background:#091522; border:1px solid #1d3347; border-radius:7px; padding:7px; }
.radar-trade-price { font-size:.91rem; font-weight:900; color:#e8eff5 !important; margin-top:3px; }
.radar-trade-desc { font-size:.62rem; color:#8296a9 !important; margin-top:2px; }
.radar-follow { margin-top:6px; padding:7px 8px; background:#0a1522; border-radius:6px; color:#aebdca !important; font-size:.68rem; line-height:1.4; }
.radar-follow b { color:#dce6ef !important; }
@media(max-width:700px){ .radar-trade-grid{grid-template-columns:repeat(2,1fr);} .radar-trade-price{font-size:.84rem;} .radar-action{font-size:.75rem;} }

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

/* 미래테마 버튼 2개를 모바일에서도 한 행에 고정 */
div[data-testid="stHorizontalBlock"]:has([class*="st-key-future_an_"]) ,
div[data-testid="stHorizontalBlock"]:has([class*="st-key-future_watch_"]) {
    display:flex !important;
    flex-direction:row !important;
    flex-wrap:nowrap !important;
    width:100% !important;
    align-items:stretch !important;
    gap:.5rem !important;
}
div[data-testid="stHorizontalBlock"]:has([class*="st-key-future_an_"]) > div,
div[data-testid="stHorizontalBlock"]:has([class*="st-key-future_watch_"]) > div {
    min-width:0 !important;
    width:50% !important;
    flex:1 1 50% !important;
}
div[data-testid="stHorizontalBlock"]:has([class*="st-key-future_an_"]) button,
div[data-testid="stHorizontalBlock"]:has([class*="st-key-future_watch_"]) button {
    width:100% !important;
    white-space:nowrap !important;
}
/* C/D 미래테마 핵심 결과 가독성 */
.priority-theme-card .theme-etf-title { font-size:1.14rem !important; color:#ffffff !important; }
.priority-theme-card .theme-summary-meta { font-size:.80rem !important; color:#b9c7d4 !important; }
.priority-theme-card .theme-summary-outlook { font-size:.82rem !important; color:#d0dbe5 !important; }
.priority-theme-card .cd-item .theme-summary-title { font-size:1.00rem !important; color:#ffffff !important; }
.priority-theme-card .cd-item .theme-summary-meta { font-size:.82rem !important; color:#d0dbe5 !important; line-height:1.65 !important; }
.theme-summary-card .theme-etf-title { font-size:1.04rem !important; color:#ffffff !important; }
.theme-summary-card .theme-summary-meta { font-size:.78rem !important; color:#b1c0ce !important; }
.theme-summary-card .theme-summary-outlook { font-size:.80rem !important; color:#c8d4df !important; }

/* 미래테마: 테마명 + 최우선 ETF + C/D 가이드를 하나의 강조 박스로 묶음 */
.priority-theme-card {
    background:linear-gradient(180deg,#132b3d 0%,#0f1d29 100%) !important;
    border:1px solid #4d86ab !important;
    border-radius:14px !important;
    padding:14px !important;
    margin:10px 0 10px !important;
    box-shadow:0 2px 8px rgba(0,0,0,.22) !important;
}
.priority-theme-card .priority-theme-head {
    background:#1a3a50 !important;
    border:1px solid #5b93b7 !important;
    border-radius:10px !important;
    padding:11px 13px !important;
    margin-bottom:9px !important;
}
.priority-theme-card .priority-theme-head .theme-title {
    font-size:1.28rem !important; font-weight:900 !important; color:#ffffff !important;
}
.priority-theme-card .theme-summary-card {
    background:#101f2c !important; border:1px solid #36566d !important;
    border-radius:10px !important; padding:11px 13px !important;
}
.priority-theme-card .cd-item {
    background:#172a39 !important; border:1px solid #45667e !important;
    border-radius:10px !important; padding:11px 13px !important; margin-top:9px !important;
}
@media(max-width:700px){
 .priority-theme-card .priority-theme-head .theme-title{font-size:1.18rem !important;}
 .priority-theme-card .theme-etf-title{font-size:1.12rem !important;}
 .priority-theme-card .theme-summary-meta{font-size:.88rem !important;}
 .priority-theme-card .theme-summary-outlook{font-size:.90rem !important;}
 .priority-theme-card .cd-item .theme-summary-meta{font-size:.90rem !important;}
}
/* FINAL TARGET V5 */
.final-target-primary{background:linear-gradient(145deg,#173b52 0%,#0d2232 58%,#0b1725 100%) !important;border:2px solid #5aa8d8 !important;border-radius:16px !important;padding:16px !important;margin:8px 0 14px !important;box-shadow:0 4px 18px rgba(45,120,170,.18) !important;}
.final-target-primary .final-target-rank{font-size:.84rem !important;color:#7ec8f5 !important;}
.final-target-primary .final-target-name-main{font-size:1.55rem !important;line-height:1.25 !important;font-weight:950 !important;color:#ffffff !important;margin-top:5px !important;}
.final-target-current-price{display:inline-block;margin-left:10px;font-size:1.05rem;font-weight:900;color:#f0d36d !important;vertical-align:middle;white-space:nowrap;}
.final-secondary-target .final-target-current-price{font-size:.88rem;margin-left:7px;}
@media(max-width:700px){.final-target-current-price{font-size:.92rem;margin-left:7px;}.final-secondary-target .final-target-current-price{font-size:.80rem;margin-left:5px;}}
.final-target-primary .final-target-code{font-size:.86rem !important;color:#a9bfd0 !important;margin-top:3px !important;}
.final-target-primary .final-target-score{font-size:2.15rem !important;font-weight:950 !important;color:#74c5f4 !important;line-height:1 !important;}
.final-target-primary .final-target-horizon{font-size:.94rem !important;font-weight:900 !important;color:#f0d36d !important;}
.final-target-primary .final-target-reason{margin-top:9px !important;padding:8px 9px !important;background:#0a1826 !important;border-radius:8px !important;color:#d2dee8 !important;font-size:.78rem !important;line-height:1.5 !important;}
.final-secondary-target{background:#0d1928 !important;border:1px solid #30485b !important;border-radius:11px !important;padding:11px !important;margin:7px 0 !important;}
.final-secondary-target .final-target-name-main{font-size:1.08rem !important;font-weight:900 !important;color:#edf4f9 !important;}
.final-secondary-target .final-target-code{font-size:.72rem !important;color:#93a9bb !important;}
.final-secondary-target .final-target-score{font-size:1.20rem !important;font-weight:900 !important;color:#69b5ed !important;}
.final-secondary-target .final-target-horizon{font-size:.76rem !important;font-weight:850 !important;color:#e0c768 !important;}
.final-target-divider{height:1px;background:#2b4559;margin:12px 0 !important;}
.final-horizon-box .final-horizon-label{font-size:.90rem !important;font-weight:900 !important;color:#b8c9d8 !important;}
.final-horizon-box .final-horizon-value{font-size:1.12rem !important;font-weight:950 !important;color:#f0f6fa !important;}
.radar-score-block .radar-score{font-size:1.85rem !important;}
.radar-score-code{font-size:.74rem !important;color:#8ea5b8 !important;margin-top:3px !important;}
@media(max-width:700px){
.final-target-primary{padding:14px !important;}
.final-target-primary .final-target-name-main{font-size:1.38rem !important;}
.final-target-primary .final-target-score{font-size:1.95rem !important;}
.final-target-primary .final-target-horizon{font-size:.86rem !important;}
.final-horizon-box .final-horizon-label{font-size:.86rem !important;}
.final-horizon-box .final-horizon-value{font-size:1.04rem !important;}
.radar-score-block .radar-score{font-size:1.65rem !important;}
}
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
# 추천 결과를 날짜별로 남겨 실제 시장 가격으로 사후 추적합니다.
RECOMMENDATION_LOG_FILE = "ETF_RADAR_RECOMMENDATION_LOG.csv"


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
    "반도체 장비·소부장": ["반도체장비", "반도체장비주", "반도체소부장", "반도체소재부품장비", "반도체장비소재"],
}


# ============================================================
# AUTO THEME DISCOVERY V2
# ETF MASTER가 갱신되면 ETF명에서 반복되는 산업/기술 키워드를 자동 발굴합니다.
# 기존 THEME_LEXICON은 seed로 유지하고, 신규 후보는 최소 ETF 수/빈도/노이즈 필터를 통과한 것만 사용합니다.
# ============================================================
_AUTO_THEME_STOP = {
    "etf","인버스","레버리지","커버드콜","채권","국채","단기채","월배당","배당","액티브",
    "증권","미국","한국","글로벌","코리아","선진국","신흥국","TOP","TOP10","TOP5",
    "소부장","부품","소재","장비",
    "혼합","파생","환헤지","합성","TR","H","PLUS","TIGER","KODEX","ACE","RISE","SOL","TIMEFOLIO",
    "HANARO","KOSEF","KBSTAR","WOORI","ARIRANG","FOCUS","UNICORN","TREX","KIWOOM"
}

@st.cache_data(ttl=1800, show_spinner=False)
def discover_auto_theme_lexicon(universe_items):
    """ETF명 자체에서 반복되는 후보 테마를 발견합니다. 가격 데이터는 사용하지 않습니다."""
    from collections import Counter
    counts=Counter()
    samples={}
    for code,name in universe_items:
        text=re.sub(r"[^0-9A-Za-z가-힣]", " ", str(name or ""))
        # 한글 2~7글자 연속 구간에서 n-gram 후보를 추출
        words=re.findall(r"[가-힣]{2,8}", text)
        seen=set()
        for w in words:
            if w in _AUTO_THEME_STOP or len(w)<2: continue
            pieces={w}
            if len(w)>=4:
                for n in (2,3,4):
                    for i in range(0,len(w)-n+1): pieces.add(w[i:i+n])
            for term in pieces:
                if term in _AUTO_THEME_STOP or len(term)<2: continue
                if term in seen: continue
                seen.add(term); counts[term]+=1; samples.setdefault(term,[]).append((code,name))
    # 기존 사전과 겹치거나 지나치게 일반적인 단어 제거
    existing_kw=set()
    for kws in THEME_LEXICON.values(): existing_kw.update(map(str,kws))
    ranked=[]
    for term,n in counts.items():
        if n<3 or term in existing_kw: continue
        if term in {"투자","산업","기업","시장","전략","포트","미래","테마","성장","수익","인덱스","코스피","코스닥"}: continue
        # 너무 짧은 후보는 최소 3개 ETF, 긴 후보는 2개 이상이어야 안정적
        if len(term)==2 and n<4: continue
        ranked.append((n, len(term), term))
    ranked.sort(key=lambda x:(x[0],x[1]), reverse=True)
    out={}
    for n,_,term in ranked[:35]:
        # 동일 후보가 기존 키워드의 부분문자열이면 새 테마로 만들지 않음
        if any(term in k or k in term for k in existing_kw if len(k)>=2):
            continue
        out[f"자동·{term}"]=[term]
        if len(out)>=18: break
    return out


def get_dynamic_theme_lexicon(universe):
    items=tuple(sorted((str(k),str(v)) for k,v in universe.items()))
    auto=discover_auto_theme_lexicon(items)
    merged=dict(THEME_LEXICON)
    merged.update(auto)
    return merged

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
        raw = saved if isinstance(saved, dict) else {}
        # 구버전의 avg_price/quantity 기록은 더 이상 보유 판정에 사용하지 않습니다.
        st.session_state.holdings = {k:{"held":True} for k,v in raw.items() if isinstance(v,dict) and v.get("held") is True}

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
        st.session_state.main_page = "🏆 최종 타겟"

    if "future_detail_code" not in st.session_state:
        st.session_state.future_detail_code = None

    if "future_detail_theme" not in st.session_state:
        st.session_state.future_detail_theme = None

    if "radar_cache" not in st.session_state:
        st.session_state.radar_cache = None

    if "radar_mode" not in st.session_state:
        st.session_state.radar_mode = "🎯 유망후보"

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
                    if item_str.lower() in ["adj close", "adj_close"]:
                        found = "Adj Close"
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
        elif key in ["adj close", "adj_close"]:
            rename_map[col] = "Adj Close"

    df = df.rename(columns=rename_map)
    required = ["Open", "High", "Low", "Close", "Volume"]
    if not all(col in df.columns for col in required):
        return pd.DataFrame()

    keep = required + (["Adj Close"] if "Adj Close" in df.columns else [])
    df = df[keep].copy()
    for col in keep:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Close"])

    # 조정가격 품질검사:
    # Adj Close에 음수/0/비현실적인 조정계수가 섞이면 해당 ETF에서 Adj Close 전체를
    # 사용하지 않습니다. 일부 날짜만 원가격으로 대체하면 가격 기준이 혼합되어
    # 백테스트 수익률과 MDD가 왜곡될 수 있으므로, 해당 ETF는 일관되게 Close 기준으로 처리합니다.
    if "Adj Close" in df.columns:
        close_num = pd.to_numeric(df["Close"], errors="coerce")
        adj_num = pd.to_numeric(df["Adj Close"], errors="coerce")
        ratio = adj_num / close_num.where(close_num > 0)
        observed = adj_num.notna() & close_num.notna()
        invalid_adj = observed & (
            (adj_num <= 0) | (close_num <= 0) | (~np.isfinite(ratio)) |
            (ratio < 0.05) | (ratio > 5.0)
        )
        if invalid_adj.any():
            df = df.drop(columns=["Adj Close"])

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
    """숫자 변환 + NaN/±inf 방어. ML/점수 계산에 비정상값이 전파되지 않게 합니다."""
    try:
        if pd.isna(value):
            return default
        v = float(value)
        if not np.isfinite(v):
            return default
        # 극단적인 API/계산 이상치도 ML 입력으로 전달하지 않습니다.
        if abs(v) > 1e12:
            return default
        return v
    except Exception:
        return default


def money(value):
    """가격 표시. 결측/비정상 값은 0원으로 오인시키지 않고 확인 불가로 표시합니다."""
    try:
        if value is None or pd.isna(value):
            return "확인 불가"
        value = float(value)
        if not np.isfinite(value) or abs(value) > 1e12:
            return "확인 불가"
    except (TypeError, ValueError, OverflowError):
        return "확인 불가"
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
    """V4 장기판정.

    V4 원칙
    1) 장기적합성은 미래수익률 예측점수가 아니라 계속 보유할 만한 구조인지 판단.
    2) 최근 252일의 장기추세 지속성을 가장 크게 반영.
    3) 현재 장기추세와 구조적 훼손은 장기적합성과 별도 축으로 판단.
    4) 장기 적합성 재검토는 매도 신호가 아니며, 구조적 훼손일 때만 신규매수를 중단.
    """
    if d.empty or len(d) < 252:
        return {
            "suitability":"데이터 부족", "trend":"확인 불가", "score":0,
            "structural_break":False,
            "reason":"장기 구조를 판단할 252일 데이터가 부족합니다."
        }

    r=d.iloc[-1]
    close=safe_float(r["Close"])
    ma120=safe_float(r["MA120"],close)
    ma200=safe_float(r["MA200"],close)
    ma200_60=safe_float(d["MA200"].iloc[-61],ma200) if len(d)>=61 else ma200
    ma120_60=safe_float(d["MA120"].iloc[-61],ma120) if len(d)>=61 else ma120
    r120=safe_float(r.get("RET120"),0)
    r252=safe_float(r.get("RET250"),0)

    # 최근 252일 동안 장기 이동평균 위에서 머문 비율
    w=d.iloc[-252:]
    above200=float((w["Close"] >= w["MA200"]).mean())*100
    above120=float((w["Close"] >= w["MA120"]).mean())*100
    ma200_up=ma200 > ma200_60
    ma120_up=ma120 > ma120_60

    # V4 장기적합성: 지속성 중심
    suitability=(
        above200*0.40
        + above120*0.20
        + (25 if ma200_up else 0)
        + (15 if r252 > 0 else 7 if r252 > -15 else 0)
    )
    suitability=float(np.clip(suitability,0,100))

    if suitability >= 78:
        fit_state="🟢 장기 핵심보유"
    elif suitability >= 62:
        fit_state="🟢 장기 보유"
    elif suitability >= 48:
        fit_state="🟡 장기 보유 + 추세 확인"
    else:
        fit_state="🔴 장기 적합성 재검토"

    # V4 장기추세: 현재 가격보다 장기 추세 방향을 우선
    trend_score=0
    trend_score += 30 if ma200_up else 0
    trend_score += 25 if ma120_up else 0
    trend_score += 20 if ma120 > ma200 else 0
    trend_score += 15 if r120 > 0 else 0
    trend_score += 10 if close > ma200 else 0

    if trend_score >= 75:
        trend_state="🟢 장기 상승추세"
    elif trend_score >= 50:
        trend_state="🟡 장기 조정/추세 확인"
    else:
        trend_state="🔴 장기 하락추세"

    # 단순 MA200 하회는 구조적 훼손으로 보지 않음.
    # 장기 지속성 자체가 동시에 무너진 경우에만 신규매수 중단 신호.
    structural_break=(
        above200 < 45 and above120 < 50 and
        r252 < 0 and r120 < 0 and
        not ma200_up and not ma120_up and
        ma120 < ma200 and close < ma200
    )

    reason=(
        f"장기적합성 {suitability:.0f}/100 · 최근 252일 200일선 위 {above200:.0f}% · "
        f"120일선 위 {above120:.0f}% · 120일 {r120:+.1f}% · 250일 {r252:+.1f}% · "
        f"장기추세 {trend_score}/100"
    )
    if structural_break:
        reason += " · 구조적 훼손 확인"
    else:
        reason += " · 구조적 훼손 아님"

    return {
        "suitability":fit_state,
        "trend":trend_state,
        "score":int(round(suitability)),
        "trend_score":int(trend_score),
        "structural_break":bool(structural_break),
        "reason":reason,
    }


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
            hits=_theme_match_for_theme(name,keywords,theme)
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
            h=_theme_match_for_theme(n,keywords,theme)
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
            accel=ret5-(ret20/4 if np.isfinite(ret20) else 0)
            prev=d.iloc[-21] if len(d)>=86 else None
            if prev is not None:
                prev_close=safe_float(prev.get("Close"),0); prev_ma20=safe_float(prev.get("MA20"),prev_close)
                prev_ret20=safe_float(prev.get("RET20"),0); prev_ret5=safe_float(prev.get("RET5"),0)
                prev_breadth=100.0 if prev_close>=prev_ma20 else 0.0
                prev_accel=prev_ret5-(prev_ret20/4 if np.isfinite(prev_ret20) else 0)
                prev_bench20=safe_float(benchmark.get("ret20"),np.nan)
                prev_rs20=prev_ret20-prev_bench20 if np.isfinite(prev_bench20) else np.nan
            else:
                prev_ret20=ret20; prev_breadth=100.0 if current>=ma20 else 0.0; prev_accel=accel
                prev_bench20=safe_float(benchmark.get("ret20"),np.nan)
                prev_rs20=ret20-prev_bench20 if np.isfinite(prev_bench20) else np.nan
            bench20_value=safe_float(benchmark.get("ret20"),np.nan)
            rows.append({"code":c,"name":n,"price":current,"rsi":rsi,"vr":vr,"ret20":ret20,"ret60":ret60,"ret5":ret5,"trend":"상승" if current>=ma20 else "조정","ma60_gap":((current/ma60-1)*100 if ma60 else 0),"breadth":(100.0 if current>=ma20 else 0.0),"accel":accel,"rs20":(ret20-bench20_value) if np.isfinite(bench20_value) else np.nan,"ret20_prev":prev_ret20,"breadth_prev":prev_breadth,"accel_prev":prev_accel,"rs20_prev":prev_rs20})
        return (theme,rows) if rows else (None,[])
    except Exception:
        return None,[]



def integrated_decision_engine(d, code):
    """미래테마→선행→가격→보유→매도 통합 상태 엔진. 현재 데이터만 사용."""
    if d is None or d.empty or len(d) < 252:
        return {"state":"데이터 부족","action":"관찰","theme_score":0,"lead_score":0,"price_score":0,"hold_score":0,"exit_score":0}
    bench=_benchmark_snapshot()
    theme, rows=_find_theme_for_etf(code)
    tscore=theme_score(rows,bench.get("ret20",0),bench.get("ret60",0)) if rows else 0.0
    lifecycle=_theme_lifecycle(rows,bench) if rows else {"score":0.0,"state":"관찰"}
    r=d.iloc[-1]; current=safe_float(r.get("Close"),0)
    ma20=safe_float(r.get("MA20"),current); ma60=safe_float(r.get("MA60"),current); ma120=safe_float(r.get("MA120"),current)
    r5=safe_float(r.get("RET5"),0); r20=safe_float(r.get("RET20"),0); r60=safe_float(r.get("RET60"),0); rsi=safe_float(r.get("RSI14"),50); vr=safe_float(r.get("VOL_RATIO"),1)
    rs20=r20-safe_float(bench.get("ret20"),0)
    ts=float(np.clip(tscore or 0,0,100)); theme_state="주도" if ts>=78 else "상승확산" if ts>=64 else "초기확대" if ts>=50 else "관찰" if ts>0 else "미분류"
    lead=leading_signal(r,safe_float(bench.get("ret20"),0)); lead_score=float(lead["score"])
    zone=validated_price_zone(r); price_score={"매수구간":92,"눌림대기":70,"추격금지":25,"무효":10}.get(zone["state"],10)
    long=long_term_horizon(d); hold_score=float(long.get("score",0)); structural=bool(long.get("structural_break",False))
    mid_score=(25 if current>ma60 else 0)+(20 if ma20>ma60 else 0)+(20 if ma60>ma120 else 0)+(20 if r60>0 else 0)+(15 if rs20>0 else 0)
    mid_state="중기 상승" if mid_score>=75 else "중기 확인" if mid_score>=55 else "중기 약세"
    dist20=(current/ma20-1)*100 if ma20 else 0
    overheat=radar_overheat_score({"rsi":rsi,"ret5":r5,"dist20":dist20,"vr":vr})
    theme_fading=ts<50 or lifecycle.get("state")=="쇠퇴"; lead_fading=lead_score<55 and rs20<0; trend_break=current<ma60 and ma20<ma60 and r60<0
    if structural: exit_score,exit_state=95,"구조적 훼손"
    elif theme_fading and lead_fading: exit_score,exit_state=88,"테마·선행 동시 약화"
    elif trend_break and lead_fading: exit_score,exit_state=78,"중기 추세 이탈"
    elif overheat>=65: exit_score,exit_state=62,"과열·분할익절"
    elif overheat>=45: exit_score,exit_state=40,"과열 주의"
    else: exit_score,exit_state=15,"정상"
    if structural: state,action="EXIT / REASSESS","🔴 구조적 훼손 · 신규매수 중단 · 보유비중 재검토"
    elif theme_fading and lead_fading: state,action="REDUCE","🔴 테마와 선행성 동시 약화 · 신규매수 중단 · 비중축소 검토"
    elif trend_break and lead_fading: state,action="REDUCE","🟠 중기 추세 이탈 · 신규매수 중단 · 반등 확인"
    elif overheat>=65: state,action="TRIM","🟡 과열구간 · 신규추격 금지 · 분할익절/추적관리"
    elif ts>=64 and lifecycle.get("state") not in {"쇠퇴","과열"} and lead_score>=72 and price_score>=85: state,action="BUY","🟢 미래테마 + 선행 ETF + 매수가격 일치 · 분할매수 후보"
    elif ts>=64 and lead_score>=72: state,action="WATCH_BUY","🟢 미래테마·선행성 양호 · 가격 확인 후 접근"
    elif hold_score>=78 and mid_score>=55: state,action="HOLD","🟢 장기 핵심보유 유지 · 중기 추세 관리"
    elif hold_score>=62: state,action="HOLD_WATCH","🟡 장기보유 가능 · 중기 추세 확인"
    else: state,action="WATCH","⚪ 관찰 · 방향 확인 전 신규매수 보류"
    return {"state":state,"action":action,"theme":theme or "미분류","theme_score":round(ts,1),"theme_state":theme_state,"lifecycle_score":float(lifecycle.get("score",0)),"lifecycle_state":lifecycle.get("state","관찰"),"lead_score":round(lead_score,1),"price_score":round(price_score,1),"hold_score":round(hold_score,1),"mid_score":int(mid_score),"mid_state":mid_state,"exit_score":int(exit_score),"exit_state":exit_state,"overheat":int(overheat),"price_zone":zone["state"],"theme_fading":theme_fading,"lead_fading":lead_fading,"structural_break":structural}

def horizon_engine(d,code):
    long=long_term_horizon(d)
    if d.empty: return {"long":long,"operation":"확인 불가","cd":None,"final":"확인 불가"}
    bench=_benchmark_snapshot(); theme,rows=_find_theme_for_etf(code); tscore=theme_score(rows,bench.get("ret20",0),bench.get("ret60",0)) if rows else None
    cd=validated_cd_signal(d.iloc[-1],tscore,bench.get("ret20",0)) if tscore is not None else None
    title=get_judgment(d)["title"]
    operation={"상승 추세 · 추격 주의":"🔥 단기 강세 · 추격 주의","상승 추세 유지":"🟢 보유·운용","단기 조정 · 중기 추세 확인":"🟡 눌림·추세 확인","중기 약세 · 방어 우선":"🔴 방어 우선"}.get(title,"⚪ 매수대기·방향 확인")
    integrated=integrated_decision_engine(d,code)
    return {"long":long,"operation":operation,"cd":cd,"theme":theme,"final":cd["state"] if cd else "C/D 산출 대기","integrated":integrated}


def _forward_reach_rate(d, target_ratio, horizon_days):
    """과거 시점에서 현재 목표수익률(target_ratio)을 향후 도달한 비율.
    각 과거 시점에서는 그 시점 이후 데이터만 사용하므로 미래누수가 없습니다.
    """
    try:
        close=d["Close"].astype(float).values
        high=d["High"].astype(float).values
        n=len(close)
        if n < horizon_days + 30 or target_ratio <= 1:
            return np.nan
        hits=[]
        for i in range(20, n-horizon_days):
            if not np.isfinite(close[i]) or close[i] <= 0:
                continue
            future=np.nanmax(high[i+1:i+1+horizon_days])
            hits.append(1.0 if np.isfinite(future) and future/close[i] >= target_ratio else 0.0)
        return float(np.mean(hits)) if hits else np.nan
    except Exception:
        return np.nan


def _forward_score_text(rate):
    if not np.isfinite(rate):
        return "과거 표본 부족"
    if rate >= .70:
        return f"도달 가능성 높음 · 과거 {rate*100:.0f}%"
    if rate >= .55:
        return f"도달 가능성 보통 이상 · 과거 {rate*100:.0f}%"
    if rate >= .40:
        return f"도달 가능성 보통 · 과거 {rate*100:.0f}%"
    return f"도달 가능성 낮음 · 과거 {rate*100:.0f}%"


def trade_levels(d, held=False, avg_price=0.0, horizon="중기"):
    """투자기간별 실제 운용 가격.

    핵심 원칙:
    1) 손절은 고정 %가 아니라 구조적 무효선과 ATR 정상변동폭을 결합합니다.
    2) 익절은 R 배수 하나로 정하지 않고 실제 저항 + 과거 Forward 도달률을 함께 봅니다.
    3) 장기는 전고점을 돌파하면 고정 2차 익절을 두지 않고 추세추적합니다.
    """
    if d.empty:
        return None
    c=safe_float(d["Close"].iloc[-1],0)
    if c<=0:
        return None
    ma20=safe_float(d["MA20"].iloc[-1],c)
    ma60=safe_float(d["MA60"].iloc[-1],c)
    low20=safe_float(d["LOW20"].iloc[-1],c)
    low60=safe_float(d["LOW60"].iloc[-1],c)

    prior20=float(d["High"].rolling(20).max().shift(1).iloc[-1]) if len(d)>=21 else np.nan
    prior60=float(d["High"].rolling(60).max().shift(1).iloc[-1]) if len(d)>=61 else np.nan
    prior120=float(d["High"].rolling(120).max().shift(1).iloc[-1]) if len(d)>=121 else np.nan
    prior252=float(d["High"].rolling(252).max().shift(1).iloc[-1]) if len(d)>=253 else np.nan
    prior20=prior20 if np.isfinite(prior20) and prior20>c else np.nan
    prior60=prior60 if np.isfinite(prior60) and prior60>c else np.nan
    prior120=prior120 if np.isfinite(prior120) and prior120>c else np.nan
    prior252=prior252 if np.isfinite(prior252) and prior252>c else np.nan

    tr=pd.concat([(d["High"]-d["Low"]).abs(),
                  (d["High"]-d["Close"].shift(1)).abs(),
                  (d["Low"]-d["Close"].shift(1)).abs()],axis=1).max(axis=1)
    atr14=safe_float(tr.rolling(14).mean().iloc[-1],c*.02)
    # 이 앱은 평단가/보유수량을 사용하지 않습니다.
    # 변동성 기준도 항상 현재가를 기준으로 계산합니다.
    ref=c
    atr_pct=float(np.clip(atr14/ref,0.005,0.20))

    if horizon=="단기":
        horizon_days=20; atr_mult=1.6; max_loss=0.09
        structural=max(low20*0.985,ma20*0.985)
        trail="20일선과 최근 스윙저점 중 더 강한 방어선 추적"
    elif horizon=="중기":
        horizon_days=40; atr_mult=2.2; max_loss=0.12
        structural=max(low60*0.985,ma60*0.985)
        trail="20일선 → 60일선 순으로 추세 훼손 여부 추적"
    else:
        horizon_days=60; atr_mult=2.8; max_loss=0.15
        structural=max(low60*0.98,ma60*0.98)
        trail="전고점 돌파 후 60일선·최근 저점 추적"

    # 정상 변동폭보다 좁은 손절을 피하되, 구조선이 지나치게 멀면 최대손실 한도에서 제한.
    volatility_floor=max(atr14*atr_mult, ref*atr_pct*atr_mult)
    # 보유 여부만 사용합니다. 평단가/수량은 전략 계산에서 제외합니다.
    # 미보유 추천 매수가는 어떤 경우에도 현재가를 초과하지 않습니다.
    pullback_candidates=[x for x in (ma20, ma60, low20, low60)
                         if np.isfinite(x) and x>0 and x<=c]
    if pullback_candidates:
        entry=max(pullback_candidates)
    else:
        entry=c*0.985
    entry=min(entry,c)

    adaptive_cap=min(max_loss,max(0.07,atr_pct*4.0))
    if held:
        # 보유중이어도 평단가를 사용하지 않고 현재 구조의 방어선만 표시합니다.
        mode="보유중"
        stop=max(structural,c-volatility_floor)
    else:
        mode="미보유"
        stop=max(structural,entry-volatility_floor)
    stop=max(stop,entry*(1-adaptive_cap))
    stop=min(stop,entry*0.995)

    # 현재가보다 높은 가격은 '매수추천가'로 사용하지 않습니다.
    # 돌파 진입은 별도 확인 가격으로만 반환합니다.
    breakout_candidates=[x for x in (ma20*1.01, prior20)
                         if np.isfinite(x) and x>c]
    breakout_entry=min(breakout_candidates) if breakout_candidates else None

    support=max(min(low20,ma20)*0.995, min(c,ma20)*0.995)

    def resistance_candidates():
        vals=[]
        for x,label in [(prior20,"20일 저항"),(prior60,"60일 저항"),(prior120,"120일 저항"),(prior252,"52주 전고점")]:
            if np.isfinite(x) and x>c*1.01:
                vals.append((x,label))
        return sorted(vals,key=lambda z:z[0])

    cands=resistance_candidates()
    tp1=None; tp2=None; tp1_label=""; tp2_label=""
    # 현재 추천기간의 미래도달 가능성을 계산해 가장 현실적인 저항을 선택.
    scored=[]
    for price,label in cands:
        ratio=price/c
        rate=_forward_reach_rate(d,ratio,horizon_days)
        scored.append((price,label,rate))
    viable=[x for x in scored if np.isfinite(x[2]) and x[2]>=0.55]
    if viable:
        tp1,lab,rate=min(viable,key=lambda x:x[0])
        tp1_label=f"{lab} · {_forward_score_text(rate)}"
        later=[x for x in scored if x[0]>tp1*1.01 and (not np.isfinite(x[2]) or x[2]>=0.40)]
        if horizon!="장기" and later:
            tp2,lab2,rate2=min(later,key=lambda x:x[0])
            tp2_label=f"{lab2} · {_forward_score_text(rate2)}"
    else:
        # 실제 저항이 없거나 과거 도달률 표본이 약한 경우 임의의 큰 목표를 만들지 않음.
        # 가장 가까운 저항이 너무 멀면 '목표 재산정'으로 둡니다.
        if cands and cands[0][0] <= c*1.12:
            tp1,lab=cands[0][0],cands[0][1]
            rate=_forward_reach_rate(d,tp1/c,horizon_days)
            tp1_label=f"{lab} · {_forward_score_text(rate)}"
        else:
            tp1=None
            tp1_label="유효한 1차 목표 부족 · 돌파/추세 확인 후 재산정"

    if horizon=="장기":
        breakout=bool(np.isfinite(prior252) and c>prior252)
        if breakout:
            tp1=None
            tp2=None
            tp1_label="52주 전고점 돌파 상태 · 고정 익절 없음"
        tp2_label="고정 2차 익절 없음 · 돌파 후 추세추적"
    elif tp1 is not None and tp2 is None:
        # 2차를 억지로 만들지 않고, 1차 돌파 후 재산정.
        tp2_label="1차 돌파 후 다음 저항을 재산정"

    return {
        "entry":entry,"breakout_entry":breakout_entry,"tp1":tp1,"tp2":tp2,"stop":stop,
        "support":support,"low60":low60,"prior20":prior20,
        "prior60":prior60,"prior252":prior252,"mode":mode,
        "horizon":horizon,"trail":trail,"tp1_label":tp1_label,
        "tp2_label":tp2_label,"max_loss":adaptive_cap if 'adaptive_cap' in locals() else max_loss,
        "atr_pct":atr_pct,"atr14":atr14,"volatility_floor":volatility_floor,
    }

def _recommended_horizon(d, code):
    """현재 ETF 상태에서 앱이 우선 추천할 투자기간을 하나만 결정합니다."""
    h=_final_horizon_snapshot(d,code)
    focus=h.get("focus","관찰 중심")
    mapping={
        "장기 중심":("장기","🟢 장기추천","6~12개월"),
        "중기 중심":("중기","🔵 중기추천","1~3개월"),
        "단기 중심":("단기","🟡 단기추천","1~4주"),
    }
    if focus in mapping:
        return mapping[focus],h
    # 관찰 중심일 때도 무작정 세 전략을 동시에 제시하지 않고,
    # 현재 점수가 가장 높은 실질 운용축 하나만 선택합니다.
    scores={
        "장기":safe_float(h.get("long_score"),0),
        "중기":safe_float(h.get("mid_score"),0),
        "단기":safe_float(h.get("lead_score"),0),
    }
    best=max(scores,key=scores.get)
    meta={"장기":("장기","🟢 장기 우선검토","6~12개월"),
          "중기":("중기","🔵 중기 우선검토","1~3개월"),
          "단기":("단기","🟡 단기 우선검토","1~4주")}
    return meta[best],h


def _render_trade_cards(lv, avg_price=0.0, qty=0.0):
    """선택된 투자기간의 목표·방어 가격과 근거를 표시합니다.
    평균매수가/보유수량은 사용하지 않습니다.
    """
    tp1=money(lv["tp1"]) if lv.get("tp1") is not None else "재산정"
    tp2=money(lv["tp2"]) if lv.get("tp2") is not None else "고정 2차 없음"
    stop=money(lv["stop"])
    cards=[
        ("🎯 1차 익절",tp1,lv.get("tp1_label","")),
        ("🎯 2차 익절",tp2,lv.get("tp2_label","")),
        ("🛡️ 방어/손절",stop,"구조 + 변동성 기반"),
    ]
    cols=st.columns(3)
    for col,(title,price,desc) in zip(cols,cards):
        with col:
            with st.container(border=True):
                st.markdown(f'<div class="trade-card-label">{esc(title)}</div><div class="trade-card-price small">{esc(price)}</div><div class="trade-card-desc">{esc(desc)}</div>',unsafe_allow_html=True)
    st.caption(f"운용: {lv['trail']} · ATR14 {lv.get('atr_pct',0)*100:.1f}%")

def render_horizon_strategy(d,code):
    """내 ETF의 추천기간 중심 실제 운용전략.

    앱이 현재 상태를 보고 장기/중기/단기 중 하나를 추천하고,
    사용자는 그 추천기간의 매수·익절·손절 기준을 우선 사용합니다.
    다른 기간은 별도 접기에서만 확인할 수 있습니다.
    """
    hmeta,h=_recommended_horizon(d,code)
    rec_horizon,rec_label,rec_period=hmeta
    holding=st.session_state.holdings.get(code) or {}
    held_widget=st.session_state.get(f"held_{code}", "보유중" if holding.get("held",False) else "미보유")
    held=held_widget=="보유중"
    avg_price=0.0
    qty=0.0

    st.markdown('<div class="strategy-section-title">🎯 실제 매수 · 익절 · 손절 전략</div>',unsafe_allow_html=True)
    st.markdown(
        f'<div class="trade-recommendation-banner"><b>{esc(rec_label)}</b> · 추천기간 {esc(rec_period)}</div>',
        unsafe_allow_html=True
    )

    lv=trade_levels(d,held,avg_price,rec_horizon)
    if not lv:
        st.warning("현재 가격 데이터로 전략을 계산할 수 없습니다.")
        return

    if not held:
        st.caption("현재 미보유 상태입니다. 앱이 추천한 투자기간을 기준으로 매수·무효 가격을 제시합니다.")
        cols=st.columns(3)
        cards=[
            ("🎯 추천 매수가",money(lv["entry"]),f"{rec_period} 추천 진입 · 현재가 이하"),
            ("🔵 돌파 확인",money(lv["breakout_entry"]),"돌파 기준 형성 시 별도 진입" if lv["breakout_entry"] is not None else "현재 유효한 돌파 기준 없음"),
            ("🛑 무효금액",money(lv["stop"]),"이탈 시 매수 취소"),
        ]
        for col,(title,price,desc) in zip(cols,cards):
            with col:
                with st.container(border=True):
                    st.markdown(f'<div class="trade-card-label">{esc(title)}</div><div class="trade-card-price">{esc(price)}</div><div class="trade-card-desc">{esc(desc)}</div>',unsafe_allow_html=True)
        return

    st.caption("보유중 · 평단/수량 입력 없이 구조 기반으로 관리")
    _render_trade_cards(lv)

    other=[("장기","🟢 장기 · 6~12개월"),("중기","🔵 중기 · 1~3개월"),("단기","🟡 단기 · 1~4주")]
    others=[x for x in other if x[0]!=rec_horizon]
    with st.expander("다른 투자기간 전략 보기",expanded=False):
        for horizon,label in others:
            lv2=trade_levels(d,True,0.0,horizon)
            if not lv2: continue
            st.markdown(f"**{label}**")
            _render_trade_cards(lv2)

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
    """보유 상태만 관리합니다. 평균매수가/보유수량 입력은 사용하지 않습니다."""
    st.markdown('<div class="section-title">보유 상태</div>', unsafe_allow_html=True)
    old=st.session_state.holdings.get(code) or {}
    default_index=1 if bool(old.get("held",False)) else 0

    held=st.radio(
        "보유 여부",
        ["미보유","보유중"],
        index=default_index,
        horizontal=True,
        key=f"held_{code}"
    )

    if held=="보유중":
        st.session_state.holdings[code]={"held":True}
        write_json(HOLDINGS_FILE, st.session_state.holdings)
        st.markdown(
            '<div class="holding-box"><div class="holding-value">보유중</div>'
            '<div class="holding-detail">평단가·보유수량 없이 현재 추세와 가격구조 기준으로 관리합니다.</div></div>',
            unsafe_allow_html=True
        )
    else:
        if code in st.session_state.holdings:
            del st.session_state.holdings[code]
            write_json(HOLDINGS_FILE, st.session_state.holdings)



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

    # 관심종목의 보유 여부에 따라 실제 매수/익절/손절 전략을 바로 표시합니다.
    # 과거 버전에서 이 호출이 빠지면서 내 ETF의 전략 영역이 사라지는 문제가 있었습니다.
    render_horizon_strategy(d, code)

    st.markdown('<div class="section-title">가격 흐름 · 최근 6개월</div>', unsafe_allow_html=True)
    render_chart(d)


# ============================================================
# FUTURE THEME ENGINE
# ============================================================

def _theme_match(name, keywords):
    text = str(name or "").replace(" ", "").lower()
    return sum(1 for k in keywords if str(k).replace(" ", "").lower() in text)


def _theme_match_for_theme(name, keywords, theme=None):
    """테마별 예외 규칙을 적용한 ETF 이름 매칭.

    자동차소부장 ETF가 이름에 '소부장'을 포함한다는 이유만으로
    반도체 장비·소부장 테마에 들어가지 않도록 한다. ETF명에 반도체,
    HBM, 메모리, 파운드리 등 반도체를 명시하는 표현이 있을 때만
    반도체 테마 매칭을 허용한다.
    """
    text = re.sub(r"[^0-9A-Za-z가-힣]", "", str(name or "")).lower()
    theme_text = str(theme or "")
    hits = _theme_match(name, keywords)
    is_semiconductor_theme = ("반도체" in theme_text) or ("반도체" in "".join(map(str, keywords)))
    explicit_semiconductor_terms = (
        "반도체", "hbm", "메모리", "파운드리", "팹리스", "실리콘웨이퍼",
        "반도체장비", "반도체소부장", "반도체소재부품장비"
    )
    has_explicit_semiconductor_term = any(term in text for term in explicit_semiconductor_terms)
    automotive_terms = ("자동차", "자동차부품", "자동차소부장", "차량부품", "완성차")
    is_automotive_name = any(term in text for term in automotive_terms)

    if is_semiconductor_theme and is_automotive_name and not has_explicit_semiconductor_term:
        return 0
    return hits


def _theme_lifecycle(rows, benchmark):
    """테마 생애주기 점수. 현재 강도보다 '강해지는 방향'을 별도 평가합니다.

    현재 시점과 20거래일 전의 상대강도·확산도·가속도 변화를 사용하므로
    미래 데이터를 참조하지 않습니다.
    """
    if not rows:
        return {"score":0.0,"state":"관찰","delta_rs":0.0,"delta_breadth":0.0,"delta_accel":0.0}

    def avg(key, default=0.0):
        vals=[safe_float(x.get(key),np.nan) for x in rows]
        vals=[v for v in vals if np.isfinite(v)]
        return float(np.mean(vals)) if vals else default

    rs_now=avg("rs20")
    rs_prev=avg("rs20_prev")
    breadth_now=avg("breadth")
    breadth_prev=avg("breadth_prev", breadth_now)
    accel_now=avg("accel")
    accel_prev=avg("accel_prev", accel_now)
    vr=avg("vr")
    rsi=avg("rsi")

    d_rs=rs_now-rs_prev
    d_breadth=breadth_now-breadth_prev
    d_accel=accel_now-accel_prev

    # 변화량을 0~100으로 정규화
    rs_score=float(np.clip((d_rs+5)/15*100,0,100))
    breadth_score=float(np.clip((d_breadth+10)/40*100,0,100))
    accel_score=float(np.clip((d_accel+2)/8*100,0,100))
    flow_score=100 if 1.05<=vr<=1.8 else 75 if 0.9<=vr<1.05 else 65 if vr>1.8 else 40

    # 과열은 '좋은 테마'와 별개로 생애주기 후반으로 이동시키는 요인
    heat_penalty=0
    if rsi>=75: heat_penalty+=30
    elif rsi>=70: heat_penalty+=15
    if avg("ret20")>=15: heat_penalty+=20
    elif avg("ret20")>=10: heat_penalty+=10

    score=(rs_score*.35+breadth_score*.25+accel_score*.25+flow_score*.15)-heat_penalty
    score=float(np.clip(score,0,100))

    if heat_penalty>=30 or (rsi>=72 and score<55):
        state="과열"
    elif d_rs < -2 and d_breadth < -12 and d_accel < -1:
        state="쇠퇴"
    elif score>=72 and d_rs>=2 and d_breadth>=5:
        state="주도 강화"
    elif score>=55 and (d_rs>0 or d_breadth>0 or d_accel>0):
        state="상승 확산"
    elif score>=42:
        state="초기 확대"
    else:
        state="관찰"

    return {"score":round(score,1),"state":state,"delta_rs":round(d_rs,2),
            "delta_breadth":round(d_breadth,1),"delta_accel":round(d_accel,2)}


def _theme_stage(score, rank, total, lifecycle=None):
    """현재 강도 + 생애주기를 결합한 화면용 단계."""
    lc=lifecycle or {}
    state=lc.get("state","")
    if state=="쇠퇴":
        return "쇠퇴"
    if state=="과열":
        return "과열"
    if score >= 78 and lc.get("score",0)>=60:
        return "현재 주도"
    if score >= 64 and lc.get("score",0)>=50:
        return "상승 확산"
    if lc.get("score",0)>=45 or score>=50:
        return "초기 확대"
    return "초기 관심"


def _benchmark_snapshot():
    """Benchmark snapshot; unavailable data stays unavailable rather than becoming 0%."""
    missing = {"ret20": np.nan, "ret60": np.nan, "available": False, "as_of": None}
    try:
        df = load_price_data("069500")
        if df is None or df.empty:
            return missing.copy()
        d = calculate_indicators(df)
        if d is None or d.empty or len(d) < 61:
            return missing.copy()
        close = pd.to_numeric(d["Close"], errors="coerce")
        ret20 = safe_float(d["RET20"].iloc[-1], np.nan)
        ret60 = safe_float(close.pct_change(60).iloc[-1] * 100, np.nan)
        if not np.isfinite(ret20) or not np.isfinite(ret60):
            return missing.copy()
        return {"ret20": ret20, "ret60": ret60, "available": True,
                "as_of": str(pd.to_datetime(d.index[-1]).date())}
    except Exception:
        return missing.copy()


def _score_theme(rows, benchmark):
    """Score a domestic theme from observed metrics only; missing data is not a zero/neutral score."""
    if not rows:
        return np.nan

    def avg(key):
        vals = [safe_float(x.get(key), np.nan) for x in rows]
        vals = [v for v in vals if np.isfinite(v)]
        return float(np.mean(vals)) if vals else np.nan

    ret20, ret60 = avg("ret20"), avg("ret60")
    vr, breadth, ma60, accel, rsi = (avg(k) for k in ("vr", "breadth", "ma60_gap", "accel", "rsi"))
    bench20 = safe_float((benchmark or {}).get("ret20"), np.nan)
    bench60 = safe_float((benchmark or {}).get("ret60"), np.nan)
    rs20 = ret20 - bench20 if np.isfinite(ret20) and np.isfinite(bench20) else np.nan
    rs60 = ret60 - bench60 if np.isfinite(ret60) and np.isfinite(bench60) else np.nan

    # Each component is included only when its underlying metric is observed.
    parts = []
    if np.isfinite(ret20): parts.append((.15, float(np.clip((ret20 + 10) / 30 * 100, 0, 100))))
    if np.isfinite(ret60): parts.append((.15, float(np.clip((ret60 + 15) / 50 * 100, 0, 100))))
    if np.isfinite(rs20): parts.append((.15, float(np.clip((rs20 + 10) / 30 * 100, 0, 100))))
    if np.isfinite(rs60): parts.append((.10, float(np.clip((rs60 + 15) / 50 * 100, 0, 100))))
    if np.isfinite(vr): parts.append((.15, float(np.clip((vr - .6) / 1.4 * 100, 0, 100))))
    if np.isfinite(breadth): parts.append((.15, float(np.clip(breadth, 0, 100))))
    if np.isfinite(ma60): parts.append((.05, float(np.clip((ma60 + 10) / 30 * 100, 0, 100))))
    if np.isfinite(accel): parts.append((.05, float(np.clip((accel + 10) / 30 * 100, 0, 100))))
    if np.isfinite(rsi):
        if 52 <= rsi <= 68: rsi_score = 100
        elif 45 <= rsi < 52 or 68 < rsi <= 73: rsi_score = 75
        elif 40 <= rsi < 45 or 73 < rsi <= 78: rsi_score = 45
        else: rsi_score = 20
        parts.append((.05, float(rsi_score)))

    observed_weight = sum(weight for weight, _ in parts)
    # Avoid presenting a score when less than half of the model's weighted evidence exists.
    if observed_weight < .50:
        return np.nan
    return float(np.clip(sum(weight * value for weight, value in parts) / observed_weight, 0, 100))


# ============================================================
# US MARKET -> DOMESTIC THEME IMPULSE (LIVE TARGET PIPELINE)
# ============================================================

# 명시적으로 연결한 미국 상장 ETF만 사용합니다. 연결되지 않은 국내 테마에
# QQQ/SPY 점수를 무차별 대입하지 않습니다.
US_MARKET_TICKERS = {
    "SPY": "미국시장 기준",
    "QQQ": "나스닥 성장주",
    "XLK": "미국 기술주",
    "SMH": "미국 반도체",
    "SOXX": "미국 반도체",
    "BOTZ": "글로벌 로봇·AI",
    "ARKQ": "자동화·로봇",
    "GRID": "전력망·스마트그리드",
    "PAVE": "인프라 투자",
    "URA": "우라늄·원자력",
    "XLE": "미국 에너지",
    "TAN": "미국 태양광",
    "ICLN": "글로벌 청정에너지",
    "XLF": "미국 금융",
    "XBI": "바이오테크",
    "CIBR": "사이버보안",
    "ITA": "항공우주·방산",
    "COPX": "구리·광산",
    "LIT": "배터리·리튬",
    "USO": "미국 원유 선물 프록시",
    "UNG": "미국 천연가스 선물 프록시",
}

_US_THEME_MAP = [
    # 특정 하위산업을 넓은 ETF로 연결할 때 직접 비교가 아니라 간접 프록시임을 명시합니다.
    ("전고체·실리콘음극재", ("전고체", "실리콘음극", "황화물계", "고체전해질"), ("LIT",), "간접 프록시: LIT는 전고체 기술 전용 ETF가 아님"),
    ("반도체", ("반도체", "semiconductor", "hbm", "메모리", "파운드리", "칩장비", "반도체장비", "ai반도체", "ai 반도체"), ("SMH", "SOXX"), "미국 반도체 ETF 프록시; 국내 ETF 구성종목과 차이 가능"),
    ("AI·로봇", ("인공지능", "로봇", "자동화", "robot", "ai소프트웨어"), ("BOTZ", "ARKQ", "QQQ"), "미국 로봇·성장 ETF 프록시; AI 하위산업과 구성 차이 가능"),
    ("ESS·에너지저장", ("에너지저장", "전력저장", "ess"), ("LIT", "GRID"), "간접 프록시: LIT·GRID는 ESS 전용 ETF가 아님"),
    ("전력·인프라", ("전력", "전력기기", "변압기", "전선", "전력망", "스마트그리드", "인프라"), ("GRID", "PAVE"), "미국 전력망·인프라 ETF 프록시; 국내 전력기기와 구성은 다름"),
    ("태양광·청정에너지", ("태양광", "태양열", "신재생", "재생에너지", "청정에너지", "solar"), ("TAN", "ICLN"), "미국 태양광·청정에너지 ETF 프록시; 국내 구성과 차이 가능"),
    ("원자력·우라늄", ("원자력", "원전", "우라늄", "핵연료"), ("URA",), "미국 상장 우라늄 ETF 프록시"),
    ("배터리·리튬", ("배터리", "리튬", "이차전지", "2차전지", "전기차", "전기자동차"), ("LIT",), "미국 배터리·리튬 ETF 프록시"),
    ("에너지", ("에너지", "정유", "석유", "가스", "원유"), ("XLE",), "미국 에너지 섹터 ETF 프록시; 신재생·ESS와 구분 필요"),
    ("금융", ("은행", "금융", "증권", "보험", "핀테크"), ("XLF",), "미국 금융 섹터 ETF 프록시"),
    ("바이오·헬스케어", ("바이오", "헬스케어", "제약", "의료기기", "신약"), ("XBI",), "미국 바이오 ETF 프록시"),
    ("사이버보안", ("사이버보안", "정보보안", "보안소프트웨어"), ("CIBR",), "미국 사이버보안 ETF 프록시"),
    ("방산·우주항공", ("방산", "항공우주", "우주항공", "항공기"), ("ITA",), "미국 항공우주·방산 ETF 프록시"),
    ("원유 생산·에너지기업", ("원유생산기업", "원유에너지기업", "에너지기업"), ("XLE",), "간접 프록시: XLE는 원유생산기업 국내 ETF와 구성·성과가 다를 수 있음"),
    ("천연가스 밸류체인·인프라", ("천연가스밸류체인", "천연가스인프라"), ("XLE",), "간접 프록시: XLE는 천연가스 인프라 전용 ETF가 아님"),
    ("원유 선물", ("원유선물", "wti", "원유"), ("USO",), "미국 원유 선물 ETF 프록시; 국내 선물상품과 추적오차 가능"),
    ("천연가스", ("천연가스", "naturalgas", "natural gas"), ("UNG",), "미국 천연가스 선물 ETF 프록시; 국내 상품과 추적오차 가능"),
    ("구리·금속", ("구리", "비철금속", "금속", "광산", "구리광산"), ("COPX",), "미국 구리·광산 ETF 프록시"),
    ("미국기술·성장", ("나스닥", "미국테크", "미국 기술", "미국테크top", "빅테크", "기술주", "성장주", "소프트웨어", "클라우드"), ("QQQ", "XLK"), "미국 성장·기술 ETF 프록시"),
]


def get_us_market_snapshot(force=False):
    """미국 동부시간 기준 마지막 완료 일봉으로 수익률/상대강도/추세를 계산합니다.

    당일 미국장이 진행 중이면 당일 부분 일봉을 제외합니다. SPY가 없으면 상대강도는
    계산하지 않고, 오래된/불완전한 데이터는 실제 신호로 취급하지 않습니다.
    """
    try:
        now = datetime.now()
        cached = st.session_state.get("us_market_snapshot_cache")
        if cached and not force and (now - cached.get("time", now)).total_seconds() < 900:
            return cached.get("data", {})
    except Exception:
        now = datetime.now()

    def fetch_one(ticker):
        try:
            df = yf.Ticker(ticker).history(period="1y", interval="1d", auto_adjust=True, actions=False)
            if df is None or df.empty or "Close" not in df.columns:
                return ticker, None
            close = pd.to_numeric(df["Close"], errors="coerce").dropna()
            if close.empty:
                return ticker, None
            # yfinance의 최신 날짜가 현재 미국 세션의 부분 일봉일 수 있으므로 컷오프 적용
            try:
                ny_now = datetime.now(ZoneInfo("America/New_York"))
                include_today = ny_now.time() >= datetime_time(17, 0)
                cutoff = ny_now.date() if include_today else ny_now.date()
                keep = [idx.date() < cutoff or (include_today and idx.date() == cutoff) for idx in close.index]
                close = close.loc[keep]
            except Exception:
                # 타임존 처리 실패 시 최신 바를 임의로 삭제하거나 미래로 추정하지 않음
                pass
            if len(close) < 65:
                return ticker, None
            last = float(close.iloc[-1])
            if not np.isfinite(last) or last <= 0:
                return ticker, None
            def pct(n):
                base = float(close.iloc[-(n + 1)])
                return (last / base - 1.0) * 100.0 if base > 0 else np.nan
            ret5, ret20, ret60 = pct(5), pct(20), pct(60)
            if not all(np.isfinite(v) for v in (ret5, ret20, ret60)):
                return ticker, None
            return ticker, {
                "date": str(close.index[-1].date()),
                "ret5": float(ret5), "ret20": float(ret20), "ret60": float(ret60),
                "accel": float(ret5 - ret20 / 4.0),
                "above20": bool(last >= float(close.tail(20).mean())),
                "above60": bool(last >= float(close.tail(60).mean())),
            }
        except Exception:
            return ticker, None

    results = {}
    # 병렬 수집으로 앱 응답 대기시간을 줄이고, 개별 티커 실패가 전체 수집을 막지 않게 함
    try:
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = [pool.submit(fetch_one, ticker) for ticker in US_MARKET_TICKERS]
            for future in as_completed(futures):
                ticker, row = future.result()
                if row is not None:
                    results[ticker] = row
    except Exception:
        results = {}

    # 전체 데이터 중 가장 최신 티커만 보고 오래된 개별 티커를 놓치지 않도록
    # 티커별 기준일도 확인합니다. 주말·짧은 휴장은 허용하되 5일 넘은 신호는 폐기합니다.
    try:
        ny_today = datetime.now(ZoneInfo("America/New_York")).date()
        results = {
            ticker: row for ticker, row in results.items()
            if row.get("date") and (ny_today - datetime.strptime(row["date"], "%Y-%m-%d").date()).days <= 5
        }
    except Exception:
        pass
    spy = results.get("SPY")
    if spy:
        for ticker, row in results.items():
            row["rs20"] = row["ret20"] - spy["ret20"]
            row["rs60"] = row["ret60"] - spy["ret60"]
    # 제공자 응답이 지나치게 오래된 경우에는 신호로 사용하지 않음
    if results:
        try:
            latest_date = max(datetime.strptime(x["date"], "%Y-%m-%d").date() for x in results.values())
            if (datetime.now(ZoneInfo("America/New_York")).date() - latest_date).days > 7:
                results = {}
        except Exception:
            pass
    try:
        st.session_state["us_market_snapshot_cache"] = {"time": datetime.now(), "data": results}
    except Exception:
        pass
    return results


def _theme_us_impulse(theme, rows, us_snapshot):
    """선언된 테마 연결과 충분한 미국장 가격 자료만 사용해 0~100 점수를 계산합니다.

    미국 ETF의 절대 수익률만 보지 않고 SPY 대비 상대강도(20/60일), 중기 수익률,
    상승 가속도, 20/60일 이동평균 추세를 함께 평가합니다. 이 점수는 수익 확률이 아닙니다.
    """
    text = re.sub(r"\s+", "", str(theme or "")).lower()
    # 냉각/열관리와 광통신은 현재 이 매핑표에 전용 미국 ETF가 없습니다.
    # 이름에 AI·데이터센터가 함께 들어가더라도 로봇/성장 ETF로 오분류하지 않습니다.
    unmapped_specialty = ("냉각", "열관리", "액침냉각", "수랭", "칠러", "광통신", "광통신망", "광트랜시버", "광모듈")
    if any(re.sub(r"\s+", "", term).lower() in text for term in unmapped_specialty):
        return {"score": None, "available": False,
                "mapping": "전용 미국 ETF 연결 근거 없음 · 점수 미산출",
                "tickers": [], "used_tickers": [], "ret20": None, "rs20": None,
                "as_of": None, "link_type": "U", "link_score": None}
    match = None
    for label, keywords, tickers, mapping in _US_THEME_MAP:
        hit = False
        for keyword in keywords:
            kw = re.sub(r"\s+", "", str(keyword)).lower()
            if kw == "ess":
                # ESS는 영문 ETF/기업 이름의 일부에 우연히 포함되는 것을 막습니다.
                hit = bool(re.search(r"(?<![a-z])ess(?![a-z])", str(theme or "").lower()))
            elif kw in text:
                hit = True
            if hit:
                break
        if hit:
            match = (label, tickers, mapping)
            break
    if match is None:
        return {"score": None, "available": False, "mapping": "미국 테마 미확인 · 점수 미산출", "tickers": [], "used_tickers": [], "ret20": None, "rs20": None, "as_of": None, "link_type": "U", "link_score": None}

    label, tickers, mapping = match
    usable = [(ticker, us_snapshot[ticker]) for ticker in tickers if ticker in us_snapshot]
    # 다중 프록시의 일부만 수집됐으면 실제 사용 종목을 기록합니다. 전부 미수집이면 연결 실패입니다.
    if not usable:
        return {"score": None, "available": False, "mapping": mapping + " · 데이터 미확보 · 점수 미산출", "tickers": list(tickers), "used_tickers": [], "ret20": None, "rs20": None, "as_of": None, "link_type": "U", "link_score": None}

    scored = []
    for ticker, r in usable:
        # 관측되지 않은 지표는 중립값으로 대체하지 않습니다. 유효 지표만 재가중합니다.
        parts = []
        if np.isfinite(safe_float(r.get("rs20"), np.nan)):
            parts.append((.30, float(np.clip((float(r["rs20"]) + 10.0) / 25.0 * 100.0, 0, 100))))
        if np.isfinite(safe_float(r.get("rs60"), np.nan)):
            parts.append((.20, float(np.clip((float(r["rs60"]) + 15.0) / 35.0 * 100.0, 0, 100))))
        if np.isfinite(safe_float(r.get("ret20"), np.nan)):
            parts.append((.15, float(np.clip((float(r["ret20"]) + 15.0) / 35.0 * 100.0, 0, 100))))
        if isinstance(r.get("above20"), (bool, np.bool_)) and isinstance(r.get("above60"), (bool, np.bool_)):
            trend_score = 100.0 if r.get("above20") and r.get("above60") else (65.0 if r.get("above20") or r.get("above60") else 25.0)
            parts.append((.20, trend_score))
        if np.isfinite(safe_float(r.get("accel"), np.nan)):
            parts.append((.10, float(np.clip((float(r["accel"]) + 5.0) / 15.0 * 100.0, 0, 100))))
        if np.isfinite(safe_float(r.get("ret5"), np.nan)):
            parts.append((.05, float(np.clip((float(r["ret5"]) + 5.0) / 15.0 * 100.0, 0, 100))))
        weight_sum = sum(w for w, _ in parts)
        if weight_sum >= .50:  # 최소 절반 이상의 지표 가중치가 관측될 때만 점수 인정
            scored.append((ticker, r, sum(w * v for w, v in parts) / weight_sum))

    if not scored:
        return {"score": None, "available": False, "mapping": mapping + " · 유효 지표 부족 · 점수 미산출", "tickers": list(tickers), "used_tickers": [], "ret20": None, "rs20": None, "as_of": None, "link_type": "U", "link_score": None}
    is_indirect = "간접 프록시" in mapping
    link_type = "C-간접 프록시" if is_indirect else "B-산업 프록시"
    link_score = 35.0 if is_indirect else 60.0
    final_score = float(np.mean([score for _, _, score in scored]))
    is_inverse = "인버스" in text
    if is_inverse:
        # 인버스 국내 ETF는 기초자산 방향과 반대이므로 방향성 점수를 반전합니다.
        # 레버리지·복리효과를 정확히 재현하는 백테스트 수익률이 아니라 방향성 신호입니다.
        final_score = 100.0 - final_score
        mapping = "인버스 방향 반전 적용 · " + mapping
    return {
        "score": final_score, "available": True, "mapping": mapping,
        "tickers": list(tickers), "used_tickers": [t for t, _, _ in scored],
        "ret20": float(np.mean([safe_float(r.get("ret20"), np.nan) for _, r, _ in scored if np.isfinite(safe_float(r.get("ret20"), np.nan))])) if any(np.isfinite(safe_float(r.get("ret20"), np.nan)) for _, r, _ in scored) else None,
        "rs20": float(np.mean([safe_float(r.get("rs20"), np.nan) for _, r, _ in scored if np.isfinite(safe_float(r.get("rs20"), np.nan))])) if any(np.isfinite(safe_float(r.get("rs20"), np.nan)) for _, r, _ in scored) else None,
        # 기준일은 실제 점수에 기여한 모든 티커의 공통 최신 가능일(가장 이른 날짜)로 보수적으로 기록
        "as_of": min(str(r.get("date", "")) for _, r, _ in scored if str(r.get("date", "")).strip()) or None,
        "link_type": link_type, "link_score": link_score,
    }


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
    us_snapshot = get_us_market_snapshot(force=force)
    candidates=[]

    # 기존 seed 테마 + ETF명에서 자동 발굴한 신규 테마를 함께 평가합니다.
    dynamic_lexicon = get_dynamic_theme_lexicon(universe)
    for theme, keywords in dynamic_lexicon.items():
        matched=[]
        for code,name in universe.items():
            hits=_theme_match_for_theme(name,keywords,theme)
            if hits:
                matched.append((hits, _normalize_etf_code(code), safe_etf_name(code,name)))
        matched.sort(key=lambda x:(x[0],x[2]), reverse=True)
        # 같은 테마가 ETF 하나뿐이면 통계적으로 불안정하므로 제외합니다.
        if len(matched)<2:
            continue
        # 특정 ETF/키워드 히트수에만 표본이 몰리는 것을 줄이기 위해
        # 네트워크 가격 조회 폭증을 막기 위해 상위 6개와 나머지 구간의 균등 표본 최대 6개를 씁니다.
        # 단순 상위 8개 고정 표본보다 테마 내 중소형 ETF가 누락될 가능성을 낮춥니다.
        if len(matched) <= 12:
            sampled = matched
        else:
            sampled = matched[:6]
            rest = matched[6:]
            idxs = np.linspace(0, len(rest)-1, 6, dtype=int).tolist()
            sampled.extend(rest[i] for i in idxs if rest[i] not in sampled)
        rows=[]
        for hits,code,name in sampled:
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
            # 20거래일 전 상태를 함께 저장해 테마가 실제로 확산 중인지 판별
            prev=d.iloc[-21] if len(d)>=86 else None
            if prev is not None:
                prev_close=safe_float(prev.get("Close"),0)
                prev_ma20=safe_float(prev.get("MA20"),prev_close)
                prev_ma60=safe_float(prev.get("MA60"),prev_close)
                prev_ret20=safe_float(prev.get("RET20"),0)
                prev_ret60=safe_float(close.pct_change(60).iloc[-21]*100,0)
                prev_ret5=safe_float(prev.get("RET5"),0)
                prev_breadth=100.0 if prev_close>=prev_ma20 else 0.0
                prev_accel=prev_ret5-(prev_ret20/4 if np.isfinite(prev_ret20) else 0)
                prev_bench20=safe_float(benchmark.get("ret20"),np.nan)
                prev_rs20=prev_ret20-prev_bench20 if np.isfinite(prev_bench20) else np.nan
            else:
                prev_ret20=ret20; prev_ret60=ret60; prev_breadth=breadth; prev_accel=accel
                prev_bench20=safe_float(benchmark.get("ret20"),np.nan)
                prev_rs20=ret20-prev_bench20 if np.isfinite(prev_bench20) else np.nan
            rows.append({"code":code,"name":name,"price":current,"rsi":rsi,"vr":vr,"ret":ret20,"ret20":ret20,"ret60":ret60,"ret5":ret5,"trend":"상승" if current>=ma20 else "조정","ma60_gap":ma60_gap,"breadth":breadth,"accel":accel,"hits":hits,
                         "rs20":(ret20-safe_float(benchmark.get("ret20"),np.nan)) if np.isfinite(safe_float(benchmark.get("ret20"),np.nan)) else np.nan,"ret20_prev":prev_ret20,"ret60_prev":prev_ret60,"breadth_prev":prev_breadth,"accel_prev":prev_accel,"rs20_prev":prev_rs20})
        if len(rows)<2: continue
        score=_score_theme(rows,benchmark)
        # ETF간 평균으로 다시 확산도를 계산하여 단일 급등 종목의 왜곡을 줄입니다.
        breadth=sum(1 for x in rows if x["ret20"]>0)/len(rows)*100
        breadth_prev=sum(1 for x in rows if x.get("ret20_prev",0)>0)/len(rows)*100
        for x in rows:
            x["breadth"]=breadth
            x["breadth_prev"]=breadth_prev
        score=_score_theme(rows,benchmark)
        lifecycle=_theme_lifecycle(rows,benchmark)
        # 미국장 점수는 유효한 테마/데이터가 있을 때만 결합합니다.
        # 연결 또는 데이터가 없으면 미국장 점수를 만들지 않고 국내 분석값만 사용합니다.
        us_impulse = _theme_us_impulse(theme, rows, us_snapshot)
        if us_impulse.get("available"):
            final_score=float(np.clip((score*.60 + lifecycle["score"]*.20 + us_impulse["score"]*.20),0,100))
        else:
            # 연결/데이터가 없을 때 중립 50점을 억지로 섞지 않고 기존 국내 점수 구조를 유지
            final_score=float(np.clip(score*.75 + lifecycle["score"]*.25,0,100))
        candidates.append({"theme":theme,"score":final_score,"base_score":score,"lifecycle":lifecycle,
                           "us_impulse":us_impulse,"rows":rows,"count":len(rows)})

    candidates.sort(key=lambda x:x["score"],reverse=True)
    # 너무 작은/약한 테마는 미래테마에서 제외하고 상위 10개까지만 표시합니다.
    candidates=[x for x in candidates if x["score"]>=42][:10]
    chain=[]
    details={}
    total=len(candidates)
    for rank,item in enumerate(candidates,1):
        stage=_theme_stage(item["score"],rank,total,item.get("lifecycle"))
        item["stage"]=stage; item["rank"]=rank
        item["reason"]=THEME_REASONS.get(item["theme"],"전체 ETF 시장에서 가격·거래량·상대강도·추세가 함께 개선되는 테마를 자동 선별합니다.")
        chain.append((item["theme"],stage))
        details[item["theme"]]=item
    data={"chain":chain,"details":details,"benchmark":benchmark,"us_market":us_snapshot,
          "updated":datetime.now().strftime("%Y-%m-%d %H:%M")}
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


DOMESTIC_IMPLEMENTATION = {
    "QQQ": [{"name":"TIGER 미국나스닥100", "code":"133690", "match":"나스닥100 직접 추종", "horizon":"장기 코어 후보", "confidence":"높음"}],
    "XLK": [{"name":"TIGER 미국테크TOP10 INDXX", "code":"381170", "match":"미국 대형 기술주 집중", "horizon":"장기 코어 + 중기 운용", "confidence":"중간"}],
    "SMH": [{"name":"TIGER 미국필라델피아반도체나스닥", "code":"381180", "match":"미국 반도체 섹터", "horizon":"중기 + 장기 위성", "confidence":"높음"}],
    "SOXX": [{"name":"TIGER 미국필라델피아반도체나스닥", "code":"381180", "match":"미국 반도체 섹터", "horizon":"중기 + 장기 위성", "confidence":"높음"}],
    "BOTZ": [{"name":"TIGER 글로벌AI&로보틱스 INDXX", "code":"464310", "match":"AI·로봇 관련 글로벌 혁신기업", "horizon":"중기 위성", "confidence":"중간"}],
    "ARKQ": [{"name":"TIGER 글로벌AI&로보틱스 INDXX", "code":"464310", "match":"AI·로봇 관련 글로벌 혁신기업", "horizon":"중기 위성", "confidence":"중간"}],
    "GLD": [{"name":"TIGER 골드선물(H)", "code":"319640", "match":"금 가격", "horizon":"장기 분산자산", "confidence":"높음"}],
    "TLT": [{"name":"TIGER 미국30년국채스트립액티브(합성 H)", "code":"458250", "match":"미국 장기국채", "horizon":"중장기 방어자산", "confidence":"중간"}],
}

DOMESTIC_IMPLEMENTATION_CODES = {v["code"] for vals in DOMESTIC_IMPLEMENTATION.values() for v in vals}

def get_domestic_implementation(code):
    return DOMESTIC_IMPLEMENTATION.get(str(code).upper(), [])


def _user_trade_guide(x):
    r = x.get("raw") if isinstance(x, dict) else None
    if r is None:
        return None
    c = safe_float(r.get("Close"), np.nan)
    ma20 = safe_float(r.get("MA20"), c)
    low20 = safe_float(r.get("LOW20"), c)
    ma60 = safe_float(r.get("MA60"), c)
    if not np.isfinite(c) or c <= 0:
        return None
    support = max(low20, ma20 * 0.985)
    buy_top = ma20 * 1.025
    invalid = min(ma60 * 0.97, support * 0.97)
    if invalid <= 0:
        invalid = c * 0.92
    risk = max(buy_top - invalid, c * 0.05)
    return {
        "buy1": buy_top,
        "buy2": (buy_top + invalid) / 2,
        "buy3": invalid,
        "stop": invalid,
        "tp1": buy_top + risk,
        "tp2": buy_top + risk * 2,
    }


def _render_theme_etf_card(theme, item, rank, guide=False, theme_score=None):
    name=item.get("name",item.get("code","-")); code=item.get("code","")
    domestic=get_domestic_implementation(code); dom=domestic[0] if domestic else None
    label={1:"🥇 최우선",2:"🥈 우선",3:"👀 관찰"}.get(rank,f"{rank}순위")
    price=item.get("price",np.nan); zone=item.get("zone",{}).get("state","")
    action=("지금 매수 검토" if zone=="매수구간" else
            "매수 대기" if zone=="눌림대기" else
            "추격매수 주의" if zone=="추격금지" else "관찰")
    display=dom["name"] if dom else name
    price_text=money(price) if np.isfinite(price) else "-"
    sig_score=safe_float(item.get("signal_score"),0)

    if guide:
        g=_user_trade_guide(item)
        st.markdown(
            f'<div class="priority-theme-card">'
            f'<div class="priority-theme-head">'
            f'<div class="theme-title">{esc(theme)}</div>'
            f'<div class="theme-summary-meta">테마점수 {safe_float(theme_score,0):.0f} · C/D 선행점수 {sig_score:.0f} · 최우선 ETF</div>'
            f'</div>'
            f'<div class="theme-summary-card">'
            f'<div class="theme-stage-wrap"><span class="theme-stage-badge">{label}</span>'
            f'<span class="theme-stage-badge">{action}</span></div>'
            f'<div class="theme-etf-title">{esc(display)}</div>'
            f'<div class="theme-summary-meta">{esc(theme)} · C/D 선행점수 {sig_score:.0f} · 현재가 {price_text}</div>'
            f'<div class="theme-summary-outlook">국내 테마 선도 ETF · {esc(code)} · 20일 {safe_float(item.get("ret20"),0):+.2f}% · RSI {safe_float(item.get("rsi"),0):.1f}</div>'
            f'</div>'
            + (f'<div class="cd-item"><div class="theme-summary-title">매수·매도 가이드</div>'
               f'<div class="theme-summary-meta">1차 40% · {money(g["buy1"])} 이하</div>'
               f'<div class="theme-summary-meta">2차 30% · {money(g["buy2"])} 이하</div>'
               f'<div class="theme-summary-meta">3차 30% · {money(g["buy3"])} 이하</div>'
               f'<div class="theme-summary-meta">손절 {money(g["stop"])} · 1차 익절 {money(g["tp1"])} · 2차 익절 {money(g["tp2"])}</div></div>' if g else '')
            + '</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="theme-summary-card">'
            f'<div class="theme-stage-wrap"><span class="theme-stage-badge">{label}</span>'
            f'<span class="theme-stage-badge">{action}</span></div>'
            f'<div class="theme-etf-title">{esc(display)}</div>'
            f'<div class="theme-summary-meta">{esc(theme)} · C/D 선행점수 {sig_score:.0f} · 현재가 {price_text}</div>'
            f'<div class="theme-summary-outlook">국내 테마 선도 ETF · {esc(code)} · 20일 {safe_float(item.get("ret20"),0):+.2f}% · RSI {safe_float(item.get("rsi"),0):.1f}</div>'
            f'</div>', unsafe_allow_html=True)

    # 미래테마에서 내 ETF로 바로 이동할 수 있는 두 버튼을 한 행에 배치
    b1,b2=st.columns(2)
    is_open=st.session_state.get("future_detail_code")==code
    with b1:
        if st.button("분석 닫기" if is_open else "ETF 분석", use_container_width=True,
                     key=f"future_an_{theme}_{rank}_{code}"):
            st.session_state.future_detail_code=None if is_open else code
            st.session_state.future_detail_theme=None if is_open else theme
            st.rerun()
    with b2:
        already=code in st.session_state.watchlist
        if st.button("⭐ 관심등록" if not already else "⭐ 등록됨", disabled=already,
                     use_container_width=True, key=f"future_watch_{theme}_{rank}_{code}"):
            add_watch(code)
            st.session_state.selected_code=code
            st.rerun()
    if is_open:
        render_future_inline_analysis()


def render_future_theme():
    st.caption("🔄 ETF MASTER 기반 자동 테마 발굴 · 기존 테마 + 신규 ETF명 반복 키워드 자동 반영")
    st.markdown('<div class="hero"><div class="hero-name">미래테마</div><div class="hero-code">유망 테마 TOP 10 · 강한 테마부터 압축 선별</div></div>',unsafe_allow_html=True)
    c1,c2=st.columns([1,1])
    with c1:
        if st.button("🔄 미래테마 업데이트",use_container_width=True,key="future_theme_refresh"):
            st.session_state.theme_cache={}; st.session_state.price_cache={}; st.session_state.future_engine_cache=None; st.session_state.us_market_snapshot_cache=None; st.session_state.radar_cache=None; st.rerun()
    with c2:
        auto_update=st.checkbox("⚡ 자동 업데이트 · 30분",value=False,key="future_auto_update")
        if auto_update and st_autorefresh is not None: st_autorefresh(interval=30*60*1000,key="future_theme_autorefresh")

    with st.spinner("테마와 ETF를 계산하는 중입니다…"):
        engine=build_future_theme_engine()
    chain=engine.get("chain",[])[:10]
    if not chain:
        st.warning("현재 가격 데이터에서 테마 후보를 찾지 못했습니다.")
        return
    bench=engine.get("benchmark",{})
    details=engine.get("details",{})
    _us_snapshot = engine.get("us_market", {})
    if _us_snapshot:
        _us_dates = sorted({str(v.get("date")) for v in _us_snapshot.values() if v.get("date")})
        _us_date_text = _us_dates[-1] if _us_dates else "날짜 확인 불가"
        st.caption(f'기준시각 {engine.get("updated","-")} · 미국장 기준일 {_us_date_text} · 미국장 수집 {len(_us_snapshot)}/{len(US_MARKET_TICKERS)}개 · 전체 테마 계산 후 상위 10개 표시')
    else:
        st.warning("미국장 가격을 가져오지 못했습니다. 미국장 테마가 명시적으로 연결되지 않으면 국내 신호만 사용되며, 테마 순위는 국내 가격 데이터 중심입니다.")
        st.caption(f'기준시각 {engine.get("updated","-")} · 전체 테마 계산 후 상위 10개 표시')

    # 미래테마 화면 순위는 국내 가격·생애주기·미국장 선행 프록시를 결합한 점수로 정렬합니다.
    # 화면 단계만 1~2위 / 3~4위 / 5~6위로 구분하며 C/D 계산식 자체는 변경하지 않습니다.
    groups=[("🥇 최우선",chain[:2],"future-group-priority"),
            ("🥈 우선",chain[2:6],"future-group-secondary"),
            ("👀 관찰",chain[6:10],"future-group-watch")]

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
            _us_info = info.get("us_impulse", {}) if isinstance(info, dict) else {}
            _us_label = f"미국장 {_us_info.get('score', 50):.0f}/100" if _us_info.get("available") else "미국장 미연결·미산출"
            _us_mapping = str(_us_info.get("mapping", "명시적 미국 테마 연결 없음"))
            st.caption(f"{theme} · 통합 테마점수 {score:.0f}/100 · {_us_label} · {_us_mapping}")
            # 최우선/우선 테마는 테마 + 최우선 ETF + C/D 가이드를 하나로 강조
            is_priority_theme=group_label in {"🥇 최우선","🥈 우선"}
            if is_priority_theme:
                _render_theme_etf_card(theme,ranked[0],1,guide=True,theme_score=score)
                for i,x in enumerate(ranked[1:3],2):
                    _render_theme_etf_card(theme,x,i,guide=False,theme_score=score)
            else:
                st.markdown(
                    f'<div class="theme-card"><div class="theme-title">{esc(theme)}</div>'
                    f'<div class="theme-summary-meta">테마점수 {score:.0f} · ETF {len(ranked)}개</div></div>',
                    unsafe_allow_html=True)
                for i,x in enumerate(ranked[:3],1):
                    _render_theme_etf_card(theme,x,i,guide=False,theme_score=score)
            if len(ranked)>3:
                with st.expander(f"{theme} 나머지 ETF {len(ranked)-3}개 보기"):
                    for i,x in enumerate(ranked[3:],4):
                        _render_theme_etf_card(theme,x,i,guide=False,theme_score=score)


# FINAL TARGET
# ============================================================

def _future_theme_selected_map(benchmark_ret20=0):
    """
    미래테마 TOP 순위와 테마 내부 ETF 순위를 분리해서 보관합니다.
    기존에는 `rank` 하나만 저장하여 '미래테마 #1'과 '그 테마의 ETF #1'이
    혼용될 수 있었습니다. 최종타겟에서는 반드시 두 순위를 별도로 사용합니다.
    """
    selected = {}
    try:
        for theme_rank, (theme, _stage) in enumerate(get_future_chain(), 1):
            info = future_theme_info(theme)
            ranked = _theme_etf_rank(info, benchmark_ret20)
            for etf_rank, x in enumerate(ranked[:3], 1):
                code = _normalize_etf_code(x.get('code'))
                if not code:
                    continue
                rec = {
                    'theme': theme,
                    'theme_rank': theme_rank,
                    'etf_rank': etf_rank,
                    'signal_score': safe_float(x.get('signal_score'), 0),
                    'theme_score': safe_float(info.get('score'), 0),
                }
                prev = selected.get(code)
                # 같은 ETF가 복수 테마에 걸리면 미래테마 우선순위가 높은 연결을 사용합니다.
                if prev is None or (
                    rec['theme_rank'], rec['etf_rank'], -rec['signal_score']
                ) < (
                    prev['theme_rank'], prev['etf_rank'], -prev['signal_score']
                ):
                    selected[code] = rec
    except Exception:
        pass
    return selected


def _final_horizon_snapshot(d, code):
    if d is None or d.empty:
        return {'long':'데이터 부족','long_score':0,'mid':'데이터 부족','mid_score':0,'short':'데이터 부족','lead_score':0,'price_zone':'확인','focus':'확인 불가','structural_break':False}
    long = long_term_horizon(d)
    r=d.iloc[-1]
    c=safe_float(r.get('Close'),0); ma20=safe_float(r.get('MA20'),c); ma60=safe_float(r.get('MA60'),c); ma120=safe_float(r.get('MA120'),c)
    r60=safe_float(r.get('RET60'),0); bench=_benchmark_snapshot(); rs20=safe_float(r.get('RET20'),0)-safe_float(bench.get('ret20'),0)
    mid_score=(25 if c>ma60 else 0)+(20 if ma20>ma60 else 0)+(20 if ma60>ma120 else 0)+(20 if r60>0 else 0)+(15 if rs20>0 else 0)
    mid='🟢 중기 상승' if mid_score>=75 else '🟡 중기 확인' if mid_score>=55 else '🔴 중기 약세'
    lead=leading_signal(r,safe_float(bench.get('ret20'),0)); zone=validated_price_zone(r)
    overheat=radar_overheat_score({'rsi':safe_float(r.get('RSI14'),50),'ret5':safe_float(r.get('RET5'),0),'dist20':((c/ma20-1)*100 if ma20 else 0),'vr':safe_float(r.get('VOL_RATIO'),1)})
    if zone['state']=='매수구간' and lead['score']>=72 and overheat<65: short='🔥 단기 진입 우위'
    elif zone['state']=='눌림대기': short='🟢 단기 눌림대기'
    elif zone['state']=='추격금지': short='🔴 단기 추격금지'
    elif zone['state']=='무효': short='🔴 단기 무효'
    else: short='🟡 단기 확인'
    if long.get('score',0)>=78 and mid_score>=55: focus='장기 중심'
    elif mid_score>=75: focus='중기 중심'
    elif lead['score']>=72 and zone['state'] in {'매수구간','눌림대기'}: focus='단기 중심'
    else: focus='관찰 중심'
    return {'long':long.get('suitability','확인 불가'),'long_score':int(long.get('score',0)),'mid':mid,'mid_score':int(mid_score),'short':short,'lead_score':int(lead.get('score',0)),'price_zone':zone.get('state','확인'),'focus':focus,'structural_break':bool(long.get('structural_break',False))}


def render_final_target_horizon(code):
    df=load_price_data(code)
    if df.empty: st.info('장기·중기·단기 판정에 필요한 가격 데이터를 확인하지 못했습니다.'); return
    d=calculate_indicators(df)
    if d.empty: st.info('장기·중기·단기 판정에 필요한 지표를 계산하지 못했습니다.'); return
    h=_final_horizon_snapshot(d,code)
    with st.expander('📆 투자기간별 전략 보기', expanded=False):
        st.markdown(f'''<div class="final-horizon-grid">
        <div class="final-horizon-box"><div class="final-horizon-label">6~12개월 · 장기</div><div class="final-horizon-value">{esc(h['long'])} · {h['long_score']}/100</div></div>
        <div class="final-horizon-box"><div class="final-horizon-label">1~3개월 · 중기</div><div class="final-horizon-value">{esc(h['mid'])} · {h['mid_score']}/100</div></div>
        <div class="final-horizon-box"><div class="final-horizon-label">1~4주 · 단기</div><div class="final-horizon-value">{esc(h['short'])}</div></div></div>''', unsafe_allow_html=True)
        st.caption(f"장기 = 6~12개월 · 중기 = 1~3개월 · 단기 = 1~4주 | 현재 우선축: {h['focus']} · 선행점수 {h['lead_score']}/100 · 가격구간 {h['price_zone']}")
        if h['structural_break']: st.warning('장기 구조적 훼손이 확인되어 신규매수보다 구조 재검토를 우선합니다.')


# 통합 수익기회 랭킹
# 안전등급 ETF만 후보군에서 제외하고, 나머지는 테마/상대강도/모멘텀으로 한 번에 비교합니다.
_SAFE_ASSET_NAME_TERMS = (
    "종합채권", "회사채", "국고채", "국채", "통안채", "단기채", "채권",
    "머니마켓", "MMF", "KOFR", "CD금리", "SOFR", "단기금융", "현금관리",
    "현금성", "금리액티브", "금리플러스", "초단기채", "우량채"
)


def _is_safe_asset_etf(item):
    """안전자산 목적의 채권/현금성 ETF를 최종 후보군에서 제외합니다.

    이름으로 확인할 수 없는 상품 분류는 추정하지 않습니다. 안전자산 분류 메타데이터가
    추후 연결되면 해당 공식 분류를 우선 사용해야 합니다.
    """
    name = str(item.get('name') or item.get('etf_name') or '').upper().replace(' ', '')
    if not name:
        return False
    terms = tuple(x.upper().replace(' ', '') for x in _SAFE_ASSET_NAME_TERMS)
    return any(term in name for term in terms)


def _cross_section_percentile(values):
    """후보군 내 상대순위(0~100). 유효 후보가 하나뿐이면 과대평가를 막기 위해 중립 50."""
    series = pd.to_numeric(pd.Series(values), errors="coerce")
    if len(series) == 0:
        return []
    valid = series.notna() & np.isfinite(series.astype(float))
    out = pd.Series(np.nan, index=series.index, dtype=float)
    n_valid = int(valid.sum())
    if n_valid == 1:
        out.loc[valid] = 50.0
    elif n_valid > 1:
        out.loc[valid] = series.loc[valid].rank(method="average", pct=True) * 100.0
    return out.clip(0.0, 100.0).tolist()



def _unified_return_opportunity_score(theme_strength, rs20, rs60, ret20,
                                      ret60, acceleration, trend_score):
    """Candidate score from observed percentile inputs; missing values are excluded and weights rebalanced."""
    parts = [
        (theme_strength, 0.25), (rs20, 0.20), (rs60, 0.20),
        (ret20, 0.15), (ret60, 0.10), (acceleration, 0.05), (trend_score, 0.05),
    ]
    observed = []
    for value, weight in parts:
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue
        if np.isfinite(value):
            observed.append((float(np.clip(value, 0.0, 100.0)), weight))
    weight_sum = sum(weight for _, weight in observed)
    if weight_sum < 0.50:
        return np.nan
    return float(np.clip(sum(value * weight for value, weight in observed) / weight_sum, 0.0, 100.0))



def build_final_targets(radar_data):
    """미국장 선행신호에서 국내 ETF 최종 타겟까지 이어지는 통합 산출 엔진.

    장기 타겟은 미국장 선행 45%, 국내 테마 연결 25%, 국내 상대강도 15%,
    국내 추세 지속성 15%를 기본으로 계산하고 성장단계를 제한적으로 반영합니다.
    현재 진입 점수는 별도 과열·가격위험 규칙으로 산출합니다.
    """
    rows = radar_data.get('rows', []) if radar_data else []
    if not rows:
        return []
    benchmark = radar_data.get('benchmark', {}) if radar_data else {}
    bench20 = safe_float(benchmark.get('ret20'), np.nan)
    bench60 = safe_float(benchmark.get('ret60'), np.nan)
    benchmark_available = bool(benchmark.get('available', False)) and np.isfinite(bench20) and np.isfinite(bench60)

    prepared = []
    for item in rows:
        x = dict(item)
        code = _normalize_etf_code(x.get('code'))
        if not code or _is_safe_asset_etf(x):
            continue
        raw = x.get('raw') if isinstance(x.get('raw'), dict) else {}
        price = safe_float(x.get('price'), safe_float(raw.get('Close'), 0))
        if price <= 0:
            continue
        ret5 = safe_float(x.get('ret5'), safe_float(raw.get('RET5'), np.nan))
        ret20 = safe_float(x.get('ret20'), safe_float(raw.get('RET20'), np.nan))
        ret60 = safe_float(x.get('ret60'), safe_float(raw.get('RET60'), np.nan))
        ret120 = safe_float(raw.get('RET120'), safe_float(x.get('ret120'), np.nan))
        rs20 = safe_float(x.get('rs20'), ret20 - bench20 if np.isfinite(ret20) and benchmark_available else np.nan)
        rs60 = ret60 - bench60 if np.isfinite(ret60) and benchmark_available else np.nan
        # 최근 20일 성과가 직전 40일 평균보다 개선되는지 보는 단순 가속도
        acceleration = ret20 - (ret60 / 3.0)
        ma20 = safe_float(raw.get('MA20'), np.nan)
        ma60 = safe_float(raw.get('MA60'), np.nan)
        ma120 = safe_float(raw.get('MA120'), np.nan)
        # 결측 이동평균을 현재가로 대체하면 데이터가 부족한 ETF에 추세 점수를 잘못 줄 수 있습니다.
        # 사용 가능한 조건만 계산하고, 평가 가능한 가중치 합으로 정규화합니다.
        trend_parts = []
        if np.isfinite(ma20) and ma20 > 0:
            trend_parts.append((35.0, 35.0 if price > ma20 else 0.0))
        if np.isfinite(ma60) and ma60 > 0:
            trend_parts.append((35.0, 35.0 if price > ma60 else 0.0))
        if np.isfinite(ma20) and ma20 > 0 and np.isfinite(ma60) and ma60 > 0:
            trend_parts.append((20.0, 20.0 if ma20 > ma60 else 0.0))
        if np.isfinite(ma60) and ma60 > 0 and np.isfinite(ma120) and ma120 > 0:
            trend_parts.append((10.0, 10.0 if ma60 > ma120 else 0.0))
        trend_weight = sum(w for w, _ in trend_parts)
        trend_score = (sum(v for _, v in trend_parts) / trend_weight * 100.0) if trend_weight else np.nan
        # theme_score는 build_radar_data에서 국내 ETF 구성만으로 계산한 테마 점수입니다.
        # 미래테마 엔진의 통합 점수와 섞이지 않도록 국내 원점수 필드를 우선 사용합니다.
        theme_score_value = safe_float(x.get('domestic_theme_score', x.get('theme_score')), np.nan)
        if not np.isfinite(theme_score_value):
            theme_score_value = np.nan
        theme_name = str(x.get('future_theme') or x.get('theme') or '미분류')
        if theme_name in {'', '미래테마 미연결', '기타'}:
            theme_name = str(x.get('theme') or '미분류')
        lifecycle = str(x.get('lifecycle_state') or '관찰')
        prepared.append({
            **x, 'code': code, 'price': price, 'ret5': ret5, 'ret20': ret20,
            'ret60': ret60, 'ret120': ret120, 'rs20': rs20, 'rs60': rs60,
            'acceleration_raw': acceleration, 'trend_score_raw': trend_score,
            'ma20_value': ma20, 'ma60_value': ma60, 'ma120_value': ma120,
            'theme_score_raw': theme_score_value, 'future_theme': theme_name,
            'lifecycle_state': lifecycle,
        })

    if not prepared:
        return []

    # 동일 ETF가 중복 행으로 들어오는 경우 최신 한 행만 남깁니다.
    unique = {}
    for x in prepared:
        unique[x['code']] = x
    prepared = list(unique.values())

    # 각 지표를 후보군 내 백분위로 변환하여 특정 단위/임계값의 영향력을 줄입니다.
    rank_inputs = {
        'theme_rank_pct': [x['theme_score_raw'] for x in prepared],
        'rs20_pct': [x['rs20'] for x in prepared],
        'rs60_pct': [x['rs60'] for x in prepared],
        'ret20_pct': [x['ret20'] for x in prepared],
        'ret60_pct': [x['ret60'] for x in prepared],
        'acceleration_pct': [x['acceleration_raw'] for x in prepared],
        'trend_pct': [x['trend_score_raw'] for x in prepared],
    }
    for key, values in rank_inputs.items():
        pct = _cross_section_percentile(values)
        for x, value in zip(prepared, pct):
            x[key] = value

    # 최종 추천 파이프라인에 미국장 신호를 명시적으로 주입합니다.
    # 이전 흐름에서는 미래테마 엔진에 미국장 신호가 있어도 build_radar_data()의 행에
    # us_theme_* 필드가 없으면 최종 타겟 단계에서 전부 국내시장 후보가 되는 누락이 있었습니다.
    try:
        _us_snapshot_for_targets = get_us_market_snapshot()
    except Exception:
        _us_snapshot_for_targets = {}
    for _x in prepared:
        _has_explicit_us = (
            bool(_x.get('us_theme_available', False))
            and np.isfinite(safe_float(_x.get('us_theme_score'), np.nan))
            and bool(_x.get('us_theme_tickers'))
            and bool(_x.get('us_theme_score_as_of') or _x.get('us_theme_as_of'))
            and bool(str(_x.get('us_theme_mapping') or '').strip())
        )
        if not _has_explicit_us:
            _theme_for_us = ' '.join(str(_x.get(k) or '') for k in ('future_theme', 'theme', 'name', 'etf_name', 'code')).strip() or '미분류'
            _impulse = _theme_us_impulse(_theme_for_us, [], _us_snapshot_for_targets)
            _x['us_theme_score'] = _impulse.get('score')
            _x['us_theme_available'] = bool(_impulse.get('available', False))
            _x['us_theme_tickers'] = list(_impulse.get('used_tickers') or _impulse.get('tickers') or [])
            _x['us_theme_score_as_of'] = _impulse.get('as_of')
            _x['us_theme_mapping'] = _impulse.get('mapping', '미국 테마 미확인 · 점수 미산출')
            _x['us_theme_link_type'] = _impulse.get('link_type', 'U')
            _x['us_theme_link_score'] = _impulse.get('link_score')

    # 미국장 선행 타겟은 실제 미국 테마 점수 + 티커 + 기준일 + 명시적 연결 근거가 모두 있을 때만 성립.
    # 연결이 없거나 점수가 미산출인 후보는 국내시장 후보로 분리하며, 미국장 점수를 부여하지 않습니다.
    for x in prepared:
        raw_us_score = safe_float(x.get('us_theme_score'), np.nan)
        tickers_value = x.get('us_theme_tickers', [])
        if isinstance(tickers_value, str):
            tickers = [t.strip() for t in tickers_value.replace(';', ',').split(',') if t.strip()]
        elif isinstance(tickers_value, (list, tuple, set)):
            tickers = [str(t).strip() for t in tickers_value if str(t).strip()]
        else:
            tickers = []
        us_as_of = str(x.get('us_theme_score_as_of') or x.get('us_theme_as_of') or '').strip()
        mapping = str(x.get('us_theme_mapping') or '').strip()
        declared_available = bool(x.get('us_theme_available', False))
        us_available = bool(declared_available and np.isfinite(raw_us_score) and tickers and us_as_of and mapping and '미확인' not in mapping and '미연결' not in mapping and '미산출' not in mapping)
        us_score = float(np.clip(raw_us_score, 0, 100)) if us_available else np.nan
        domestic_theme_pct = safe_float(x.get('theme_rank_pct'), np.nan)
        domestic_rs_pct = np.nanmean([safe_float(x.get('rs20_pct'), np.nan), safe_float(x.get('rs60_pct'), np.nan)]) if any(np.isfinite(safe_float(x.get(k), np.nan)) for k in ('rs20_pct','rs60_pct')) else np.nan
        domestic_trend_pct = safe_float(x.get('trend_pct'), np.nan)
        lifecycle_state = str(x.get('lifecycle_state') or '관찰')
        lifecycle_adjustment = {'초기 확대': 4.0, '상승 확산': 2.0, '주도 강화': 1.0, '관찰': 0.0, '과열': -5.0, '쇠퇴': -8.0}.get(lifecycle_state, 0.0)
        # 국내 구성요소도 유효한 데이터만 재가중하며, 결측을 50점으로 숨기지 않습니다.
        domestic_parts = [(0.40, domestic_theme_pct), (0.30, domestic_rs_pct), (0.30, domestic_trend_pct)]
        valid_domestic = [(w, float(v)) for w, v in domestic_parts if np.isfinite(v)]
        domestic_weight = sum(w for w, _ in valid_domestic)
        domestic_base = sum(w * v for w, v in valid_domestic) / domestic_weight if domestic_weight else np.nan
        domestic_score = float(np.clip(domestic_base + lifecycle_adjustment, 0, 100)) if np.isfinite(domestic_base) else np.nan

        mapping_lower = mapping.lower()
        if us_available:
            if '간접 프록시' in mapping_lower:
                link_score, link_type = 35.0, 'C-간접 프록시'
            elif '프록시' in mapping_lower:
                link_score, link_type = 60.0, 'B-산업 프록시'
            else:
                link_score, link_type = 70.0, 'B-연결 근거 확인'
            # 연결 근거를 별도 점수화합니다. 현재 매핑은 대부분 프록시이므로 직접 연결로 과장하지 않습니다.
            target_parts = [(0.35, us_score), (0.25, link_score), (0.20, domestic_theme_pct), (0.10, domestic_rs_pct), (0.10, domestic_trend_pct)]
            valid_target = [(w, float(v)) for w, v in target_parts if np.isfinite(v)]
            valid_weight = sum(w for w, _ in valid_target)
            score = sum(w * v for w, v in valid_target) / valid_weight if valid_weight else np.nan
            score = float(np.clip(score + lifecycle_adjustment, 0, 100)) if np.isfinite(score) else np.nan
            us_contribution = 0.35 * (us_score - 50.0)
            theme_factor_pct = (0.60 * us_score + 0.40 * domestic_theme_pct) if np.isfinite(domestic_theme_pct) else us_score
            recommendation_type = ('미국장 선행 타겟' if us_score >= 55.0 else ('미국장 역풍' if us_score < 45.0 else '미국장 연결·신호 중립'))
        else:
            link_score, link_type = np.nan, 'U-미확인'
            score = domestic_score
            us_contribution = np.nan
            theme_factor_pct = domestic_theme_pct if np.isfinite(domestic_theme_pct) else np.nan
            recommendation_type = '국내시장 후보'

        x['us_signal_state'] = ('선행 우호' if us_available and us_score >= 55.0 else ('역풍' if us_available and us_score < 45.0 else ('중립/약함' if us_available else '미확인')))
        x['us_theme_rank_pct'] = us_score if us_available else np.nan
        x['us_link_score'] = link_score
        x['us_link_type'] = link_type
        x['theme_factor_pct'] = theme_factor_pct
        # 진입 위험 지표는 누락 시 0/중립값으로 가정하지 않고, 실제 가격 이력에서 재계산합니다.
        raw_ind = x.get('raw') if isinstance(x.get('raw'), dict) else {}
        rsi_value = safe_float(x.get('rsi'), safe_float(raw_ind.get('RSI14'), np.nan))
        dist20 = safe_float(x.get('dist20'), safe_float(raw_ind.get('DIST20'), np.nan))
        ret5_value = safe_float(x.get('ret5'), safe_float(raw_ind.get('RET5'), np.nan))
        entry_data_status = '가격 지표 확인'
        if not (np.isfinite(rsi_value) and np.isfinite(dist20) and np.isfinite(ret5_value)):
            try:
                hist = load_price_data(code)
                hist = normalize_df(hist)
                if not hist.empty and 'Close' in hist.columns:
                    close = pd.to_numeric(hist['Close'], errors='coerce').dropna()
                    if len(close) >= 21:
                        last = float(close.iloc[-1])
                        prev5 = float(close.iloc[-6])
                        ma20_hist = float(close.tail(20).mean())
                        delta = close.diff()
                        gains = delta.clip(lower=0).rolling(14).mean()
                        losses = -delta.clip(upper=0).rolling(14).mean()
                        loss_now = float(losses.iloc[-1]) if pd.notna(losses.iloc[-1]) else 0.0
                        gain_now = float(gains.iloc[-1]) if pd.notna(gains.iloc[-1]) else 0.0
                        calc_rsi = 100.0 if loss_now <= 0 and gain_now > 0 else (50.0 if loss_now <= 0 else 100.0 - 100.0 / (1.0 + gain_now / loss_now))
                        if not np.isfinite(rsi_value): rsi_value = calc_rsi
                        if not np.isfinite(dist20) and ma20_hist > 0: dist20 = (last / ma20_hist - 1.0) * 100.0
                        if not np.isfinite(ret5_value) and prev5 > 0: ret5_value = (last / prev5 - 1.0) * 100.0
            except Exception:
                pass
        metrics_available = all(np.isfinite(v) for v in (rsi_value, dist20, ret5_value)) and np.isfinite(trend_score)
        entry_penalty_reasons = []
        if not metrics_available:
            # 자료 부족은 저위험이 아니라 확인 불가입니다. 진입점수를 제한하고 차이를 감점으로 기록합니다.
            entry_data_status = '진입 지표 부족 · 신규 진입 보류'
            entry_score = min(float(score), 55.0)
            overheat_penalty = max(0.0, float(score) - entry_score)
            if overheat_penalty > 0:
                entry_penalty_reasons.append('진입 지표 부족: 55점 상한')
            else:
                entry_penalty_reasons.append('진입 지표 부족: 신규 진입 보류')
        else:
            overheat_penalty = 0.0
            ret20_value = safe_float(x.get('ret20'), np.nan)
            if rsi_value >= 78:
                overheat_penalty += 18; entry_penalty_reasons.append('RSI 78 이상 +18')
            elif rsi_value >= 72:
                overheat_penalty += 10; entry_penalty_reasons.append('RSI 72 이상 +10')
            if ret5_value >= 12:
                overheat_penalty += 15; entry_penalty_reasons.append('5일 수익률 12% 이상 +15')
            elif ret5_value >= 8:
                overheat_penalty += 8; entry_penalty_reasons.append('5일 수익률 8% 이상 +8')
            if np.isfinite(ret20_value):
                if ret20_value >= 30:
                    overheat_penalty += 18; entry_penalty_reasons.append('20일 수익률 30% 이상 +18')
                elif ret20_value >= 20:
                    overheat_penalty += 12; entry_penalty_reasons.append('20일 수익률 20% 이상 +12')
                elif ret20_value >= 12:
                    overheat_penalty += 6; entry_penalty_reasons.append('20일 수익률 12% 이상 +6')
            if dist20 >= 12:
                overheat_penalty += 15; entry_penalty_reasons.append('MA20 이격 12% 이상 +15')
            elif dist20 >= 8:
                overheat_penalty += 8; entry_penalty_reasons.append('MA20 이격 8% 이상 +8')
            if np.isfinite(trend_score) and trend_score < 40:
                overheat_penalty += 5; entry_penalty_reasons.append('가격 추세 약함 +5')
            elif not np.isfinite(trend_score):
                entry_penalty_reasons.append('이동평균 추세 자료 부족 · 추세 감점 미판정')
            if rs20 <= 0:
                overheat_penalty += 4; entry_penalty_reasons.append('20일 시장 대비 상대강도 열위 +4')
            if np.isfinite(ma20) and ma20 > 0 and price < ma20:
                overheat_penalty += 5; entry_penalty_reasons.append('현재가 MA20 하회 +5')
            entry_score = float(np.clip(score - overheat_penalty, 0, 100))
            entry_data_status = '진입 지표 확인 완료'
        if not entry_penalty_reasons:
            entry_penalty_reasons.append('계산된 진입 위험 감점 없음')
        if overheat_penalty >= 20:
            entry_status = '과열·추격 위험: 타겟 유지, 진입 대기'
        elif x['trend_score_raw'] >= 70 and x['rs20'] > 0 and x['ret20'] > 0:
            entry_status = '추세·상대강도 동반'
        elif x['rs20'] > 0 and x['ret20'] > 0:
            entry_status = '상대강도 개선'
        elif x['ret20'] > 0 or x['ret60'] > 0:
            entry_status = '추세 회복 관찰'
        else:
            entry_status = '상승 모멘텀 미확인'
        x.update({
            'target_asset_class': 'risk_asset_unified',
            'future_theme_selected': True,
            'future_theme_score': round(x['theme_score_raw'], 1),
            'domestic_theme_score_pct': round(domestic_theme_pct, 1),
            'theme_factor_score': round(theme_factor_pct, 1),
            'us_theme_score': round(us_score, 1) if us_available else np.nan,
            'us_theme_score_as_of': x.get('us_theme_score_as_of'),
            'us_theme_tickers': list(x.get('us_theme_tickers', [])),
            'us_theme_available': us_available,
            'us_theme_mapping': x.get('us_theme_mapping', '미국장 신호 미연결'),
            'us_link_score': round(link_score, 1) if np.isfinite(link_score) else np.nan,
            'us_link_type': link_type,
            'recommendation_type': recommendation_type,
            'domestic_target_score': round(domestic_score, 1),
            'momentum_score': round((x['ret20_pct'] + x['ret60_pct']) / 2, 1),
            'relative_strength_score': round((x['rs20_pct'] + x['rs60_pct']) / 2, 1),
            'acceleration_score': round(x['acceleration_pct'], 1),
            'trend_score': round(x['trend_pct'], 1),
            'entry_risk_penalty': round(overheat_penalty, 1),
            'entry_penalty_reasons': entry_penalty_reasons,
            'score_gap': round(float(score) - float(entry_score), 1),
            'us_score_contribution': round(us_contribution, 1),
            'entry_score': round(entry_score, 1),
            'entry_status': entry_status,
            'entry_data_status': entry_data_status,
            'entry_rsi14': round(rsi_value, 2) if np.isfinite(rsi_value) else np.nan,
            'entry_ret5_pct': round(ret5_value, 2) if np.isfinite(ret5_value) else np.nan,
            'entry_dist20_pct': round(dist20, 2) if np.isfinite(dist20) else np.nan,
            'final_score': round(score, 1) if np.isfinite(score) else np.nan,
        })

    prepared.sort(key=lambda x: (
        bool(x.get('us_theme_available', False)),
        np.isfinite(safe_float(x.get('final_score'), np.nan)),
        safe_float(x.get('final_score'), -1), safe_float(x.get('relative_strength_score'), -1),
        safe_float(x.get('momentum_score'), -1), safe_float(x.get('trend_score'), -1)
    ), reverse=True)

    for rank, x in enumerate(prepared, 1):
        x['final_rank'] = rank
        x['final_state'] = '상대강도·모멘텀 상위' if rank <= 3 else '수익기회 후보'
    entry_order = sorted(prepared, key=lambda x: (
        np.isfinite(safe_float(x.get('entry_score'), np.nan)),
        safe_float(x.get('entry_score'), -1),
        safe_float(x.get('final_score'), -1)), reverse=True)
    for rank, x in enumerate(entry_order, 1):
        x['entry_rank'] = rank
        us_score_reason = f"{safe_float(x.get('us_theme_score'), np.nan):.0f}/100" if np.isfinite(safe_float(x.get('us_theme_score'), np.nan)) else "미산출"
        us_contribution_reason = f"{safe_float(x.get('us_score_contribution'), np.nan):+.1f}점" if np.isfinite(safe_float(x.get('us_score_contribution'), np.nan)) else "미산출"
        theme_pct_reason = f"{safe_float(x.get('theme_rank_pct'), np.nan):.0f}백분위" if np.isfinite(safe_float(x.get('theme_rank_pct'), np.nan)) else "국내 테마점수 미산출"
        # 숫자 나열 대신 투자자가 읽을 수 있는 문장으로 선정 이유를 생성합니다.
        # 가격/이동평균 데이터에서 확인할 수 없는 뉴스 원인은 단정하지 않습니다.
        theme_name = str(x.get('future_theme') or x.get('theme') or '해당 테마')
        theme_background = THEME_REASONS.get(theme_name, '')
        if not theme_background:
            theme_background = f"{theme_name} 관련 ETF들의 가격 흐름과 상대강도를 바탕으로 후보를 평가했습니다."
        reasons = [f"{theme_name}을(를) 살펴보는 이유: {theme_background}"]

        if bool(x.get('us_theme_available', False)) and np.isfinite(safe_float(x.get('us_theme_score'), np.nan)):
            us_sc = safe_float(x.get('us_theme_score'), np.nan)
            tickers_v = x.get('us_theme_tickers', [])
            if isinstance(tickers_v, str):
                tickers_text = ', '.join(t.strip() for t in tickers_v.replace(';', ',').split(',') if t.strip())
            elif isinstance(tickers_v, (list, tuple, set)):
                tickers_text = ', '.join(str(t) for t in tickers_v if str(t).strip())
            else:
                tickers_text = ''
            map_text = str(x.get('us_theme_mapping') or '연결 근거 추가 확인 필요')
            if us_sc >= 65:
                us_interp = '미국 관련 ETF의 가격 신호가 강한 편입니다.'
            elif us_sc >= 45:
                us_interp = '미국 관련 ETF의 신호는 중간 수준으로, 뚜렷한 우위가 확인됐다고 보기는 어렵습니다.'
            else:
                us_interp = '미국 관련 ETF의 신호가 약합니다. 국내 ETF 점수가 높더라도 미국장 선행 근거는 약한 편입니다.'
            reasons.append(f"미국장 확인: {tickers_text or '관련 티커 미확인'} 점수 {us_sc:.0f}/100. {us_interp} 연결은 '{map_text}' 기준이므로 직접 연관성과는 구분해 해석해야 합니다.")
        else:
            reasons.append('미국장 선행 근거: 관련 미국 테마 또는 유효한 데이터가 확인되지 않아 미국장 점수를 산출하지 않았습니다. 따라서 이 후보는 미국장 선행 타겟이 아니라 국내시장 데이터 기반 후보로 봐야 합니다.')

        ret20_v = safe_float(x.get('ret20'), np.nan)
        ret60_v = safe_float(x.get('ret60'), np.nan)
        rs20_v = safe_float(x.get('rs20'), np.nan)
        rs60_v = safe_float(x.get('rs60'), np.nan)
        if np.isfinite(ret20_v) and np.isfinite(ret60_v):
            if ret20_v > 0 and ret60_v > 0:
                price_read = f"국내 ETF는 최근 20일 {ret20_v:+.1f}%, 60일 {ret60_v:+.1f}%로 두 기간 모두 상승했습니다."
            elif ret20_v > 0 and ret60_v <= 0:
                price_read = f"최근 20일은 {ret20_v:+.1f}% 반등했지만, 60일 수익률은 {ret60_v:+.1f}%로 중기 추세 회복은 아직 확인이 필요합니다."
            elif ret20_v <= 0 and ret60_v > 0:
                price_read = f"60일 수익률은 {ret60_v:+.1f}%지만 최근 20일은 {ret20_v:+.1f}%로 조정 중입니다. 추세가 다시 살아나는지 확인이 필요합니다."
            else:
                price_read = f"최근 20일 {ret20_v:+.1f}%, 60일 {ret60_v:+.1f}%로 두 기간 모두 약세입니다. 현재는 상승 추세가 확인된 후보로 보기 어렵습니다."
            reasons.append(price_read)
        if np.isfinite(rs20_v) and np.isfinite(rs60_v):
            if rs20_v > 0 and rs60_v > 0:
                reasons.append(f"시장 대비로도 20일 {rs20_v:+.1f}%p, 60일 {rs60_v:+.1f}%p 앞서 상대강도가 양호합니다.")
            elif rs20_v > 0 or rs60_v > 0:
                reasons.append(f"시장 대비 상대강도는 20일 {rs20_v:+.1f}%p, 60일 {rs60_v:+.1f}%p로 기간별 신호가 엇갈립니다.")
            else:
                reasons.append(f"시장 대비 상대강도는 20일 {rs20_v:+.1f}%p, 60일 {rs60_v:+.1f}%p로 모두 열위입니다.")

        ma20_v = safe_float(x.get('ma20_value'), np.nan)
        ma60_v = safe_float(x.get('ma60_value'), np.nan)
        price_v = safe_float(x.get('price'), np.nan)
        if np.isfinite(ma20_v) and np.isfinite(ma60_v) and ma20_v > 0 and ma60_v > 0:
            if ma20_v > ma60_v:
                cross_text = '20일 이동평균선이 60일선을 웃돌아 골든크로스 이후 또는 단기 우위 상태입니다.'
            else:
                cross_text = '20일 이동평균선이 60일선 아래에 있어 골든크로스가 아직 확인되지 않았습니다.'
            if np.isfinite(price_v):
                if price_v > ma20_v > ma60_v:
                    cross_text += ' 현재가도 두 이동평균선 위에 있어 추세 구조가 상대적으로 양호합니다.'
                elif price_v < ma20_v:
                    cross_text += ' 다만 현재가는 20일선 아래여서 단기 추세 회복 확인이 필요합니다.'
                elif price_v < ma60_v:
                    cross_text += ' 현재가가 60일선 아래여서 중기 추세는 아직 약합니다.'
            reasons.append(cross_text)
        else:
            reasons.append('이동평균선 자료가 충분하지 않아 20일·60일선 교차 상태는 판단하지 않았습니다.')

        risk_pen = safe_float(x.get('entry_risk_penalty'), 0)
        penalties = x.get('entry_penalty_reasons', [])
        penalty_text = ' · '.join(str(z) for z in penalties if str(z).strip()) if isinstance(penalties, (list, tuple)) else str(penalties or '')
        if risk_pen >= 15:
            reasons.append(f"진입 판단: 위험 감점이 {risk_pen:.0f}점으로 커서 지금 추격하기보다는 조정 안정 또는 추세 회복을 기다리는 편이 낫습니다. 주요 사유: {penalty_text}.")
        elif risk_pen > 0:
            reasons.append(f"진입 판단: 위험 요인으로 {risk_pen:.0f}점 감점했습니다. {penalty_text}.")
        else:
            reasons.append('진입 판단: 현재 계산된 과열·추세 위험 감점은 없지만, 이는 수익이나 안전을 보장한다는 뜻은 아닙니다.')

        reasons.append(f"종합: 장기 타겟 {safe_float(x.get('final_score'), 0):.0f}/100, 현재 진입 {safe_float(x.get('entry_score'), x.get('final_score', 0)):.0f}/100입니다. 장기 관심도와 지금 진입할 만한지는 별도로 판단하세요.")
        x['final_reason'] = ' '.join(reasons)
    return prepared

def render_final_target_trade_strategy(code,item=None):
    """최종 타겟 각 ETF의 추천기간 하나를 기준으로 실제 행동전략을 표시합니다."""
    try:
        df=load_price_data(code); d=calculate_indicators(df)
    except Exception:
        return
    if d.empty: return

    holding=st.session_state.holdings.get(code) or {}
    held=bool(holding.get("held",False))
    hmeta,h=_recommended_horizon(d,code)
    rec_horizon,rec_label,rec_period=hmeta

    with st.expander("💰 실제 매수·익절·손절 전략", expanded=False):
        st.markdown(f"**{esc(rec_label)} · 추천기간 {esc(rec_period)}**")
        lv=trade_levels(d,held,0.0,rec_horizon)
        if not lv:
            st.info("현재 가격 데이터로 전략을 계산할 수 없습니다.")
            return

        if not held:
            st.caption("미보유 · 추천기간 기준")
            cols=st.columns(3)
            cards=[
                ("🎯 추천 매수가",money(lv["entry"]),f"{rec_period} 추천 진입 · 현재가 이하"),
                ("🔵 돌파 확인",money(lv["breakout_entry"]),"돌파 기준 형성 시 별도 진입" if lv["breakout_entry"] is not None else "현재 유효한 돌파 기준 없음"),
                ("🛑 무효금액",money(lv["stop"]),"이탈 시 매수 취소"),
            ]
            for col,(title,price,desc) in zip(cols,cards):
                with col:
                    with st.container(border=True):
                        st.markdown(f'<div class="trade-card-label">{esc(title)}</div><div class="trade-card-price">{esc(price)}</div><div class="trade-card-desc">{esc(desc)}</div>',unsafe_allow_html=True)
        else:
            st.caption("보유중 · 평단/수량 입력 없이 구조 기반으로 관리")
            _render_trade_cards(lv)
            with st.expander("다른 투자기간 전략 보기",expanded=False):
                for horizon,label in [("장기","🟢 장기 · 6~12개월"),("중기","🔵 중기 · 1~3개월"),("단기","🟡 단기 · 1~4주")]:
                    if horizon==rec_horizon: continue
                    lv2=trade_levels(d,True,0.0,horizon)
                    st.markdown(f"**{label}**")
                    _render_trade_cards(lv2)

def _read_recommendation_log():
    """추천 기록 CSV를 읽습니다. 파일 오류가 나도 앱의 주요 기능은 계속 작동합니다."""
    try:
        if os.path.exists(RECOMMENDATION_LOG_FILE):
            df = pd.read_csv(RECOMMENDATION_LOG_FILE, dtype={"code": str})
            if "code" in df.columns:
                df["code"] = df["code"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(6)
            # 과거 로그를 새 스키마로 마이그레이션합니다. 예전 기록에 없던 값은
            # 실제로 수집된 것처럼 꾸미지 않고 '과거 기록: 미수집' 또는 NaN으로 둡니다.
            schema_defaults = {
                "recommendation_reason": "과거 기록: 미수집",
                "us_theme_score": np.nan,
                "us_score_contribution": np.nan,
                "us_theme_available": False,
                "us_theme_mapping": "과거 기록: 미수집",
                "us_theme_tickers": "",
                "us_theme_score_as_of": "",
                "domestic_theme_score_pct": np.nan,
                "theme_factor_score": np.nan,
                "entry_risk_penalty": np.nan,
                "entry_penalty_reasons": "과거 기록: 미수집",
                "score_gap": np.nan,
                "price_at_recommendation": np.nan,
                "latest_price": np.nan,
                "latest_price_date": "",
                "return_pct": np.nan,
                "sessions_elapsed": 0,
                "return_5d_pct": np.nan,
                "return_20d_pct": np.nan,
                "benchmark_return_5d_pct": np.nan,
                "benchmark_return_20d_pct": np.nan,
                "excess_return_5d_pct": np.nan,
                "excess_return_20d_pct": np.nan,
                "tracking_status": "과거 기록 · 새 기준 추적 대기",
            }
            for col, default in schema_defaults.items():
                if col not in df.columns:
                    df[col] = default
            return df
    except Exception:
        pass
    return pd.DataFrame(columns=[
        "snapshot_date", "code", "name", "theme", "target_rank", "target_score",
        "entry_score", "entry_status", "recommendation_reason", "us_theme_score", "us_score_contribution",
        "us_theme_available", "us_theme_mapping", "us_theme_tickers", "us_theme_score_as_of",
        "domestic_theme_score_pct", "theme_factor_score", "entry_risk_penalty", "entry_penalty_reasons", "score_gap",
        "price_at_recommendation", "latest_price", "latest_price_date", "return_pct", "sessions_elapsed", "return_5d_pct",
        "return_20d_pct", "benchmark_return_5d_pct", "benchmark_return_20d_pct",
        "excess_return_5d_pct", "excess_return_20d_pct", "tracking_status"
    ])


def _save_recommendation_log(df):
    try:
        df.to_csv(RECOMMENDATION_LOG_FILE, index=False, encoding="utf-8-sig")
        return True
    except Exception:
        return False


def _target_diversification_bucket(item):
    """ETF 이름/테마의 명시적 키워드로 상위 추천의 테마 쏠림을 제한합니다."""
    text = (str(item.get("future_theme", "")) + " " + str(item.get("theme", "")) + " " + str(item.get("name", ""))).lower()
    groups = [
        ("2차전지", ("2차전지", "배터리", "전고체", "음극재", "양극재", "리튬", "ess")),
        ("반도체", ("반도체", "semiconductor", "hbm", "메모리")),
        ("AI·로봇", ("인공지능", "ai", "로봇", "로보틱스")),
        ("전력·원전", ("전력", "전력기기", "원전", "원자력", "변압기", "전력망")),
        ("신재생에너지", ("태양광", "풍력", "신재생", "수소")),
        ("바이오·헬스케어", ("바이오", "헬스케어", "제약", "의료")),
        ("방산·우주", ("방산", "우주", "항공")),
        ("조선·운송", ("조선", "해운", "운송")),
    ]
    for bucket, keywords in groups:
        if any(word in text for word in keywords):
            return bucket
    return str(item.get("future_theme") or item.get("theme") or "기타").strip() or "기타"


def _diversified_target_shortlist(targets, limit=5, max_per_theme=2):
    """점수순을 최대한 유지하면서 상위 추천의 단일 테마 집중을 완화합니다."""
    ordered = list(targets or [])
    selected, deferred, counts, seen_codes = [], [], {}, set()
    for item in ordered:
        code = _normalize_etf_code(item.get("code", ""))
        if not code or code in seen_codes:
            continue
        seen_codes.add(code)
        bucket = _target_diversification_bucket(item)
        if counts.get(bucket, 0) < max_per_theme and len(selected) < limit:
            selected.append(item)
            counts[bucket] = counts.get(bucket, 0) + 1
        else:
            deferred.append(item)
        if len(selected) >= limit:
            break
    if len(selected) < limit:
        for item in deferred:
            code = _normalize_etf_code(item.get("code", ""))
            if code and all(_normalize_etf_code(x.get("code", "")) != code for x in selected):
                selected.append(item)
                if len(selected) >= limit:
                    break
    return selected


def record_daily_recommendations(targets, radar_data):
    """추천 상위 5개를 국내 가격 기준일별로 기록합니다(가격수익률, 분배금 미포함)."""
    if not targets:
        return
    log = _read_recommendation_log()
    if log.empty:
        log = pd.DataFrame(columns=[
            "snapshot_date", "code", "name", "theme", "target_rank", "target_score",
            "entry_score", "entry_status", "recommendation_reason", "us_theme_score", "us_score_contribution",
            "us_theme_available", "us_theme_mapping", "us_theme_tickers", "us_theme_score_as_of", "us_link_type", "us_link_score", "recommendation_type",
            "domestic_theme_score_pct", "theme_factor_score", "entry_risk_penalty", "entry_penalty_reasons", "score_gap",
            "price_at_recommendation", "latest_price", "latest_price_date", "return_pct", "sessions_elapsed", "return_5d_pct",
            "return_20d_pct", "benchmark_return_5d_pct", "benchmark_return_20d_pct",
        "excess_return_5d_pct", "excess_return_20d_pct", "tracking_status"
        ])
    # 같은 거래일의 추천은 재실행 때 최신 산출 결과로 갱신합니다.
    # 과거 거래일의 기록은 불변으로 두되, 오늘의 오래된/중복 후보가 CSV에 누적되지 않게 합니다.
    us_targets = [x for x in (targets or []) if bool(x.get("us_theme_available", False)) and np.isfinite(safe_float(x.get("us_theme_score"), np.nan))]
    shortlist = _diversified_target_shortlist(us_targets, 5, 2)
    recorded_codes_by_date = {}
    for rank, item in enumerate(shortlist, 1):
        code = _normalize_etf_code(item.get("code"))
        if not code:
            continue
        try:
            px = load_price_data(code)
            if px.empty:
                continue
            px = normalize_df(px)
            price_date = pd.Timestamp(px.index[-1]).strftime("%Y-%m-%d")
            current_price = safe_float(px["Close"].iloc[-1], 0)
            if current_price <= 0:
                continue
        except Exception:
            continue
        key = (price_date, code)
        row = {
            "snapshot_date": price_date, "code": code, "name": str(item.get("name", get_etf_name(code))),
            "theme": str(item.get("future_theme", item.get("theme", "미분류"))),
            "target_rank": rank, "target_score": safe_float(item.get("final_score"), 0),
            "entry_score": safe_float(item.get("entry_score"), safe_float(item.get("final_score"), 0)),
            "entry_status": str(item.get("entry_status", "확인 필요")),
            "recommendation_reason": str(item.get("final_reason", "")),
            "us_theme_score": safe_float(item.get("us_theme_score"), np.nan),
            "us_score_contribution": safe_float(item.get("us_score_contribution"), np.nan),
            "us_theme_available": bool(item.get("us_theme_available", False)),
            "us_theme_mapping": str(item.get("us_theme_mapping", "미국장 신호 미연결")),
            "us_theme_tickers": ", ".join(item.get("us_theme_tickers", [])) if isinstance(item.get("us_theme_tickers", []), (list, tuple)) else str(item.get("us_theme_tickers", "")),
            "us_theme_score_as_of": str(item.get("us_theme_score_as_of") or ""),
            "us_link_type": str(item.get("us_link_type") or "U-미확인"),
            "us_link_score": safe_float(item.get("us_link_score"), np.nan),
            "recommendation_type": str(item.get("recommendation_type") or "미분류"),
            "domestic_theme_score_pct": safe_float(item.get("domestic_theme_score_pct"), np.nan),
            "theme_factor_score": safe_float(item.get("theme_factor_score"), np.nan),
            "entry_risk_penalty": safe_float(item.get("entry_risk_penalty"), 0),
            "entry_penalty_reasons": " · ".join(item.get("entry_penalty_reasons", [])) if isinstance(item.get("entry_penalty_reasons", []), list) else str(item.get("entry_penalty_reasons", "")),
            "score_gap": safe_float(item.get("score_gap"), safe_float(item.get("final_score"), 0) - safe_float(item.get("entry_score"), safe_float(item.get("final_score"), 0))),
            "price_at_recommendation": current_price, "latest_price": current_price,
            "latest_price_date": price_date, "return_pct": 0.0, "sessions_elapsed": 0,
            "return_5d_pct": np.nan, "return_20d_pct": np.nan,
            "benchmark_return_5d_pct": np.nan, "benchmark_return_20d_pct": np.nan,
            "excess_return_5d_pct": np.nan, "excess_return_20d_pct": np.nan,
            "tracking_status": "추천일 기록 · 추적 중"
        }
        recorded_codes_by_date.setdefault(price_date, set()).add(code)
        mask = (log.get("snapshot_date", pd.Series(dtype=str)).astype(str) == price_date) & (log.get("code", pd.Series(dtype=str)).astype(str).str.zfill(6) == code)
        if not mask.any():
            log = pd.concat([log, pd.DataFrame([row])], ignore_index=True)
        else:
            # 동일 거래일은 아직 확정된 과거 성과가 없으므로 최신 점수/연결근거로 갱신합니다.
            # 이미 관측된 수익률 추적값은 보존하고, 추천 산출 필드만 교체합니다.
            idx = log.index[mask][0]
            for col, value in row.items():
                if col not in {"return_pct", "sessions_elapsed", "return_5d_pct", "return_20d_pct",
                               "benchmark_return_5d_pct", "benchmark_return_20d_pct",
                               "excess_return_5d_pct", "excess_return_20d_pct", "tracking_status",
                               "latest_price", "latest_price_date"}:
                    log.at[idx, col] = value
    # 해당 날짜에 후보 3개 이상을 정상 기록했다면, 같은 날짜의 오래된 추천 목록을 정리합니다.
    # 날짜가 다른 과거 스냅샷과 수익률 추적 기록은 그대로 둡니다.
    for snap_date, recorded_codes in recorded_codes_by_date.items():
        if len(recorded_codes) >= min(3, len(shortlist)):
            same_day = log["snapshot_date"].astype(str) == snap_date
            code_col = log["code"].astype(str).str.zfill(6)
            log = log.loc[~same_day | code_col.isin(recorded_codes)].copy()
    # 기존 파일에 남아 있는 중복도 날짜+정확한 6자리 종목코드로 정리합니다.
    if not log.empty and {"snapshot_date", "code"}.issubset(log.columns):
        log["code"] = log["code"].map(_normalize_etf_code)
        log["snapshot_date"] = pd.to_datetime(log["snapshot_date"], errors="coerce").dt.strftime("%Y-%m-%d")
        log = log[log["code"].astype(str).str.len() == 6]
        log = log[log["snapshot_date"].notna()]
        log = log.drop_duplicates(subset=["snapshot_date", "code"], keep="first")
        log = log.sort_values(["snapshot_date", "target_rank"], ascending=[False, True], na_position="last")
    # 오래된 로그를 무제한 키우지 않고 최근 2년을 보관합니다.
    if not log.empty and "snapshot_date" in log:
        log = log[pd.to_datetime(log["snapshot_date"], errors="coerce") >= (pd.Timestamp.today().normalize() - pd.Timedelta(days=730))]
    _save_recommendation_log(log)


def update_spot_recommendation_results(max_codes=60):
    """추천 당시 가격을 기준으로 5/20거래일 수익률과 KODEX 200 대비 초과수익을 계산합니다."""
    log = _read_recommendation_log()
    if log.empty:
        return log
    if "code" not in log.columns or "snapshot_date" not in log.columns:
        return log
    log["code"] = log["code"].map(_normalize_etf_code)
    log = log[log["code"].astype(str).str.len() == 6].copy()
    log = log.drop_duplicates(subset=["snapshot_date", "code"], keep="first")
    codes = log.sort_values("snapshot_date", ascending=False)["code"].drop_duplicates().head(max_codes).tolist()
    cache = {}
    for code in codes:
        try:
            px = normalize_df(load_price_data(code, force=True))
            if not px.empty and "Close" in px.columns:
                px = px.sort_index()
                px = px[~px.index.duplicated(keep="last")]
                cache[code] = px
        except Exception:
            continue
    try:
        bench = normalize_df(load_price_data("069500", force=True))
        if not bench.empty and "Close" in bench.columns:
            bench = bench.sort_index()
            bench = bench[~bench.index.duplicated(keep="last")]
        else:
            bench = pd.DataFrame()
    except Exception:
        bench = pd.DataFrame()

    for idx, rec in log.iterrows():
        code = str(rec.get("code", ""))
        if code not in cache:
            log.loc[idx, "tracking_status"] = "ETF 가격 데이터 미확보"
            continue
        px = cache[code].copy()
        try:
            rec_date = pd.Timestamp(rec.get("snapshot_date")).normalize()
            px.index = pd.to_datetime(px.index)
            if getattr(px.index, "tz", None) is not None:
                px.index = px.index.tz_localize(None)
            px.index = px.index.normalize()
            px = px[~px.index.duplicated(keep="last")].sort_index()
            if px.empty or pd.Timestamp(px.index[-1]).normalize() < rec_date:
                log.loc[idx, "tracking_status"] = "추천일 이후 ETF 가격 데이터 미확보"
                continue
            # 추천 당시 저장한 종가를 기준으로 삼습니다. 재조회 데이터의 첫 행을
            # 기준가격으로 대체하면 추천일 가격 누락 시 성과가 왜곡될 수 있습니다.
            anchor = safe_float(rec.get("price_at_recommendation"), np.nan)
            if not np.isfinite(anchor) or anchor <= 0:
                exact = px.loc[px.index == rec_date]
                if exact.empty:
                    log.loc[idx, "tracking_status"] = "추천 당시 기준가격 미수집"
                    continue
                anchor = safe_float(exact["Close"].iloc[-1], np.nan)
            if not np.isfinite(anchor) or anchor <= 0:
                log.loc[idx, "tracking_status"] = "추천 당시 기준가격 오류"
                continue

            future_px = px.loc[px.index > rec_date]
            latest = safe_float(px["Close"].iloc[-1], anchor)
            log.loc[idx, "latest_price"] = latest
            log.loc[idx, "latest_price_date"] = pd.Timestamp(px.index[-1]).strftime("%Y-%m-%d")
            log.loc[idx, "price_at_recommendation"] = anchor
            log.loc[idx, "return_pct"] = (latest / anchor - 1) * 100
            elapsed = len(future_px)
            log.loc[idx, "sessions_elapsed"] = elapsed

            bench_px = pd.DataFrame()
            if not bench.empty:
                bench_px = bench.copy()
                bench_px.index = pd.to_datetime(bench_px.index)
                if getattr(bench_px.index, "tz", None) is not None:
                    bench_px.index = bench_px.index.tz_localize(None)
                bench_px.index = bench_px.index.normalize()
                bench_px = bench_px[~bench_px.index.duplicated(keep="last")].sort_index()
            bench_start = np.nan
            if not bench_px.empty:
                bstart_rows = bench_px.loc[bench_px.index == rec_date]
                if not bstart_rows.empty:
                    bench_start = safe_float(bstart_rows["Close"].iloc[-1], np.nan)

            for horizon in (5, 20):
                ret_col = f"return_{horizon}d_pct"
                bench_col = f"benchmark_return_{horizon}d_pct"
                excess_col = f"excess_return_{horizon}d_pct"
                if elapsed < horizon:
                    log.loc[idx, ret_col] = np.nan
                    log.loc[idx, bench_col] = np.nan
                    log.loc[idx, excess_col] = np.nan
                    continue
                end_date = pd.Timestamp(future_px.index[horizon - 1]).normalize()
                end_rows = px.loc[px.index == end_date]
                if end_rows.empty:
                    continue
                end_price = safe_float(end_rows["Close"].iloc[-1], np.nan)
                etf_ret = np.nan
                if np.isfinite(end_price) and end_price > 0:
                    etf_ret = (end_price / anchor - 1) * 100
                    log.loc[idx, ret_col] = etf_ret
                if np.isfinite(bench_start) and bench_start > 0 and not bench_px.empty:
                    bend_rows = bench_px.loc[bench_px.index == end_date]
                    if not bend_rows.empty:
                        bend = safe_float(bend_rows["Close"].iloc[-1], np.nan)
                        if np.isfinite(bend) and bend > 0:
                            bench_ret = (bend / bench_start - 1) * 100
                            log.loc[idx, bench_col] = bench_ret
                            if np.isfinite(etf_ret):
                                log.loc[idx, excess_col] = etf_ret - bench_ret

            if elapsed >= 20:
                log.loc[idx, "tracking_status"] = "20거래일 성과 산출 시점 도달 · 벤치마크 동시 확인"
            elif elapsed >= 5:
                log.loc[idx, "tracking_status"] = "5거래일 성과 산출 시점 도달 · 20거래일 추적 중"
            else:
                log.loc[idx, "tracking_status"] = f"추천 후 {elapsed}/5거래일 경과"
            if elapsed >= 5 and not np.isfinite(safe_float(log.loc[idx, "return_5d_pct"], np.nan)):
                log.loc[idx, "tracking_status"] += " · 5일 ETF 가격 산출 불가"
            if elapsed >= 20 and not np.isfinite(safe_float(log.loc[idx, "return_20d_pct"], np.nan)):
                log.loc[idx, "tracking_status"] += " · 20일 ETF 가격 산출 불가"
        except Exception as e:
            log.loc[idx, "tracking_status"] = "성과 계산 오류: " + type(e).__name__
            continue
    _save_recommendation_log(log)
    return log


def render_spot_tracking_panel():
    """추천 이후 실제 가격성과를 확인하는 현물 추적 패널."""
    with st.expander("📍 추천 타겟 현물 성과 추적", expanded=False):
        st.caption("추천 당시 기록한 종가를 기준으로 실제 가격을 추적합니다. 5/20거래일 성과이며 분배금·세금·거래비용은 포함하지 않습니다. 추천일 이후 해당 거래일 수가 지나지 않았으면 미경과로 표시하고, 과거 추천 당시 저장되지 않은 점수·사유는 미수집으로 구분합니다.")
        if st.button("현물 성과 갱신", key="update_spot_target_tracking", use_container_width=True):
            with st.spinner("기록된 추천 종목의 최신 가격을 조회하고 성과를 갱신합니다…"):
                updated = update_spot_recommendation_results()
            if updated.empty:
                st.info("아직 기록된 추천이 없습니다. 최종 타겟 화면을 열면 오늘의 후보가 기록됩니다.")
            else:
                st.success("실제 가격으로 추천 성과를 갱신했습니다.")
        log = _read_recommendation_log()
        if log.empty:
            st.info("최종 타겟 후보를 기록하면 이후 실제 가격으로 성과를 추적합니다.")
        else:
            view = log.sort_values("snapshot_date", ascending=False).head(30).copy()
            # 누락을 빈칸으로 숨기지 않고 과거 미수집/아직 미경과 상태를 명시합니다.
            for col in ["us_theme_score", "us_score_contribution", "entry_risk_penalty", "return_5d_pct", "benchmark_return_5d_pct", "excess_return_5d_pct", "return_20d_pct", "benchmark_return_20d_pct", "excess_return_20d_pct"]:
                if col in view.columns:
                    view[col] = view[col].where(view[col].notna(), "미수집/미경과")
            if "entry_penalty_reasons" in view.columns:
                def _display_penalty_reason(row):
                    value = row.get("entry_penalty_reasons")
                    if pd.notna(value) and str(value).strip() and str(value).strip() not in {"과거 기록: 미수집", "미수집", "확인 필요"}:
                        return value
                    penalty = safe_float(row.get("entry_risk_penalty"), np.nan)
                    if np.isfinite(penalty) and penalty > 0:
                        return f"감점 {penalty:.0f}점 확인 · 세부 사유는 과거 기록 미수집"
                    return "과거 기록: 미수집"
                view["entry_penalty_reasons"] = view.apply(_display_penalty_reason, axis=1)
            if "us_theme_mapping" in view.columns:
                view["us_theme_mapping"] = view["us_theme_mapping"].fillna("과거 기록: 미수집")
            if "us_theme_available" in view.columns:
                view["us_theme_available"] = view["us_theme_available"].map(
                    lambda v: "연결됨" if str(v).strip().lower() in {"true", "1", "yes"} else "미연결/미수집"
                )
            if "us_theme_score" in view.columns and "us_theme_available" in view.columns:
                # 점수 50은 중립값일 수 있으므로, 연결 플래그가 없으면 미국장 반영 근거로 간주하지 않습니다.
                not_linked = view["us_theme_available"] != "연결됨"
                view.loc[not_linked, "us_theme_mapping"] = view.loc[not_linked, "us_theme_mapping"].fillna("미연결/미수집")
                # 과거 버전 로그에는 연결 플래그는 미연결인데 기여도가 ±10점으로 저장된
                # 모순 행이 있습니다. 이를 정상 기여도로 보여주지 않고 명시적으로 표시합니다.
                if "us_score_contribution" in view.columns:
                    for ridx in view.index[not_linked]:
                        contribution = safe_float(view.at[ridx, "us_score_contribution"], np.nan)
                        if np.isfinite(contribution) and abs(contribution) > 0.05:
                            prior = str(view.at[ridx, "us_theme_mapping"] or "미연결/미수집")
                            view.at[ridx, "us_theme_mapping"] = f"과거 기록 불일치: 미연결 플래그인데 기여도 {contribution:+.1f}점 저장 · {prior}"
                            view.at[ridx, "us_score_contribution"] = "과거 기록 불일치"
            cols = [c for c in ["snapshot_date", "target_rank", "name", "theme", "target_score", "entry_score", "domestic_theme_score_pct", "theme_factor_score", "us_theme_score", "us_theme_available", "us_theme_tickers", "us_theme_score_as_of", "us_theme_mapping", "us_link_type", "us_link_score", "recommendation_type", "us_score_contribution", "entry_risk_penalty", "entry_penalty_reasons", "price_at_recommendation", "return_5d_pct", "benchmark_return_5d_pct", "excess_return_5d_pct", "return_20d_pct", "benchmark_return_20d_pct", "excess_return_20d_pct", "tracking_status"] if c in view.columns]
            view = view[cols].rename(columns={"snapshot_date":"추천 기준일", "target_rank":"순위", "name":"ETF", "theme":"테마", "target_score":"타겟점수", "entry_score":"진입점수", "domestic_theme_score_pct":"국내 테마 백분위", "theme_factor_score":"통합 테마요소", "us_theme_score":"미국장 점수", "us_theme_available":"미국장 연결 여부", "us_theme_tickers":"미국장 사용 ETF", "us_theme_score_as_of":"미국장 기준일", "us_theme_mapping":"미국장 연결 근거", "us_link_type":"미국장 연결 등급", "us_link_score":"연결 점수", "recommendation_type":"추천 유형", "us_score_contribution":"미국장 중립대비 기여", "entry_risk_penalty":"진입 위험 감점", "entry_penalty_reasons":"감점 사유", "price_at_recommendation":"추천 종가", "return_5d_pct":"ETF 5일(%)", "benchmark_return_5d_pct":"KODEX200 5일(%)", "excess_return_5d_pct":"5일 초과수익(%p)", "return_20d_pct":"ETF 20일(%)", "benchmark_return_20d_pct":"KODEX200 20일(%)", "excess_return_20d_pct":"20일 초과수익(%p)", "tracking_status":"추적 상태"})
            st.dataframe(view, use_container_width=True, hide_index=True)


# ============================================================
# RECENT US THEME NEWS (headline-grounded, source-linked)
# ============================================================

US_THEME_NEWS_QUERIES = {
    "반도체": 'US semiconductor stocks AI chip demand earnings',
    "AI 반도체": 'US AI semiconductor chip demand data center earnings',
    "인공지능": 'US artificial intelligence AI data center investment earnings',
    "AI": 'US artificial intelligence AI data center investment earnings',
    "전력기기": 'US power grid electricity demand data center infrastructure',
    "전력 인프라": 'US power grid electricity demand data center infrastructure',
    "배터리": 'US battery energy storage lithium battery industry',
    "2차전지": 'US battery energy storage lithium battery industry',
    "전고체": 'US solid state battery technology investment',
    "ESS": 'US battery energy storage systems grid storage',
    "태양광": 'US solar energy policy investment solar companies',
    "신재생에너지": 'US renewable energy solar wind investment policy',
    "로봇": 'US robotics automation industry investment earnings',
    "방산": 'US defense aerospace spending contracts industry',
    "우주": 'US space industry satellite launch investment',
    "광통신": 'US optical networking data center AI infrastructure',
    "통신": 'US optical networking data center infrastructure',
    "사이버보안": 'US cybersecurity stocks demand earnings',
    "바이오": 'US biotechnology healthcare stocks drug development',
    "헬스케어": 'US healthcare biotechnology industry earnings',
    "원자력": 'US nuclear energy power data center investment',
    "원전": 'US nuclear energy power data center investment',
    "천연가스": 'US natural gas power demand energy market',
    "에너지": 'US energy sector oil gas prices policy',
    "금": 'US gold prices central bank demand inflation',
    "금융": 'US banks financial sector earnings interest rates',
    "클라우드": 'US cloud computing software AI spending earnings',
}


def _theme_news_query(theme):
    """국내 테마명을 미국 뉴스 검색에 적합한 영문 검색어로 변환합니다."""
    text = str(theme or '').strip()
    for key in sorted(US_THEME_NEWS_QUERIES, key=len, reverse=True):
        if key.lower() in text.lower():
            return US_THEME_NEWS_QUERIES[key]
    # 미등록 테마는 한국어 이름만으로 미국 테마라고 추정하지 않고,
    # 원문 테마명과 미국 관련 표현을 붙여 검색하되 결과 근거를 별도 표시합니다.
    return f'"{text}" US industry stocks ETF' if text else ''


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_recent_us_theme_news(theme, limit=4):
    """Google News RSS에서 최근 뉴스 제목/출처/날짜/URL을 가져옵니다.

    기사 제목은 원문 그대로 보여주며, 뉴스만으로 인과관계를 단정하지 않습니다.
    네트워크 실패나 검색 결과 부족 시 빈 목록을 반환합니다.
    """
    query = _theme_news_query(theme)
    if not query:
        return []
    try:
        from urllib.parse import quote_plus
        from datetime import timedelta
        rss_url = (
            'https://news.google.com/rss/search?q=' + quote_plus(query + ' when:14d')
            + '&hl=en-US&gl=US&ceid=US:en'
        )
        response = requests.get(
            rss_url,
            timeout=5,
            headers={'User-Agent': 'Mozilla/5.0 ETF-RADAR/1.0'}
        )
        response.raise_for_status()
        root = ET.fromstring(response.content)
        now_utc = datetime.now(ZoneInfo('UTC'))
        cutoff = now_utc - timedelta(days=14)
        results = []
        channel = root.find('channel')
        if channel is None:
            return []
        for node in channel.findall('item'):
            title = (node.findtext('title') or '').strip()
            link = (node.findtext('link') or '').strip()
            source_node = node.find('source')
            source = (source_node.text or '').strip() if source_node is not None else ''
            pub_text = (node.findtext('pubDate') or '').strip()
            try:
                from email.utils import parsedate_to_datetime
                published = parsedate_to_datetime(pub_text)
                if published.tzinfo is None:
                    published = published.replace(tzinfo=ZoneInfo('UTC'))
                published = published.astimezone(ZoneInfo('UTC'))
                if published < cutoff:
                    continue
                date_text = published.astimezone(ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d %H:%M KST')
            except Exception:
                date_text = '게시일 확인 불가'
            if not title or not link:
                continue
            results.append({
                'title': title,
                'source': source or '출처 미표시',
                'published': date_text,
                'url': link,
            })
            if len(results) >= max(1, min(int(limit), 5)):
                break
        return results
    except Exception:
        return []


def summarize_theme_news(theme, articles):
    """최근 기사 제목에서 반복되는 투자 논점을 보수적으로 요약합니다."""
    if not articles:
        return '최근 14일 내 관련 미국 뉴스에서 확인 가능한 기사를 가져오지 못했습니다. 뉴스 배경은 미확인으로 두며, 가격 신호만으로 미국에서 테마가 부상한다고 단정하지 않습니다.'
    titles = ' '.join(str(a.get('title', '')) for a in articles).lower()
    points = []
    topic_rules = [
        (('ai', 'artificial intelligence', 'data center', 'datacenter'), 'AI·데이터센터 투자와 관련 수요가 기사에서 언급됩니다'),
        (('earnings', 'profit', 'revenue', 'forecast', 'guidance'), '기업 실적이나 향후 실적 전망이 주요 논점으로 나타납니다'),
        (('demand', 'orders', 'backlog', 'shortage'), '수요·주문·공급 부족 관련 보도가 포함됩니다'),
        (('investment', 'spending', 'capex', 'funding'), '투자 지출과 자금 조달 규모가 주요 논점으로 나타납니다'),
        (('policy', 'government', 'regulation', 'subsidy', 'tariff'), '정책·규제 변화가 관련 산업의 변수로 거론됩니다'),
        (('competition', 'china', 'oversupply', 'risk', 'selloff', 'decline'), '경쟁 심화 또는 하락 위험에 관한 경계 요인도 보입니다'),
        (('grid', 'power', 'electricity', 'energy storage'), '전력 수요·전력망·에너지저장 관련 이슈가 보도됩니다'),
        (('battery', 'lithium', 'solid-state'), '배터리 기술·리튬·저장장치 관련 이슈가 보도됩니다'),
        (('cybersecurity', 'security breach', 'ransomware'), '사이버보안 수요와 보안 위협 관련 이슈가 보도됩니다'),
    ]
    for terms, sentence in topic_rules:
        if any(term in titles for term in terms):
            points.append(sentence)
    if not points:
        points.append('관련 산업의 기업·시장 동향이 보도되지만, 제목만으로 공통된 상승 촉매를 특정하기는 어렵습니다')
    return '최근 14일 기사 제목에서 확인된 논점: ' + '; '.join(points[:3]) + '. 뉴스는 시장의 관심 배경을 설명하는 참고 자료이며, 가격 상승이나 향후 수익을 보장하지 않습니다.'


def render_theme_news_panel(theme):
    """추천 테마의 최근 미국 뉴스와 근거 링크를 보여줍니다."""
    articles = fetch_recent_us_theme_news(str(theme or ''), 4)
    st.markdown('#### 📰 미국에서 이 테마가 주목받는 배경')
    st.write(summarize_theme_news(theme, articles))
    if not articles:
        st.caption('뉴스 연결 실패 또는 최근 기사 미확인 · 뉴스 근거 없이 테마 부상 원인을 만들어내지 않았습니다.')
        return
    for article in articles:
        title = str(article.get('title', '기사 제목 미확인'))
        source = str(article.get('source', '출처 미표시'))
        published = str(article.get('published', '게시일 확인 불가'))
        url = str(article.get('url', ''))
        st.markdown(f"- **[{esc(title)}]({url})**  \n  <span style='color:#91a5b8;font-size:.8rem'>{esc(source)} · {esc(published)}</span>", unsafe_allow_html=True)
    st.caption('자동 요약은 기사 제목의 주제어를 정리한 것입니다. 기사 전문을 해석한 확정적 인과 분석은 아니며, 링크를 열어 원문을 확인하세요.')


def render_final_target():
    if st_autorefresh is not None:
        st_autorefresh(interval=10*60*1000, key="final_target_autorefresh")
    st.markdown('<div class="hero"><div class="hero-name">🏆 오늘의 추천 ETF</div><div class="hero-code">1순위와 추천 이유부터 확인하세요</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="final-target-hero"><div class="final-target-title">실제 미국장 선행 신호와 연결 근거가 확인된 국내 ETF를 우선 발굴합니다</div><div class="final-target-sub">미국 테마·점수·사용 티커·기준일·연결 근거가 모두 확인된 후보만 미국장 선행 타겟으로 분류합니다. 미국 테마 또는 연결 근거가 없는 ETF는 미국장 점수를 부여하지 않고 국내시장 후보로 별도 표시합니다. 장기 타겟과 현재 진입 적합성은 분리하며, 점수는 수익 확률이나 수익 보장이 아닌 후보 우선순위입니다.</div></div>', unsafe_allow_html=True)
    if st.button("🔄 최종 타겟 새로고침", use_container_width=True, key="final_target_refresh"):
        st.session_state.radar_cache=None; st.session_state.future_engine_cache=None; st.session_state.price_cache={}; st.session_state.us_market_snapshot_cache=None; st.rerun()
    with st.spinner("미국장 완료 일봉과 국내 ETF 테마·모멘텀·상대강도를 연결하는 중입니다…"):
        data=build_radar_data(); targets=build_final_targets(data)
    # 1~4단계 결과를 실제 장에서 사후 확인할 수 있도록 추천일·순위·가격을 기록합니다.
    record_daily_recommendations(targets, data)
    try:
        _us_snapshot = build_future_theme_engine().get("us_market", {})
        if _us_snapshot:
            _us_dates = sorted({str(v.get("date")) for v in _us_snapshot.values() if v.get("date")})
            _us_date_text = _us_dates[-1] if _us_dates else "날짜 확인 불가"
            st.caption(f"미국장 데이터 기준일: {_us_date_text} · 수집 티커 {len(_us_snapshot)}/{len(US_MARKET_TICKERS)} · 연결 근거/유효 데이터가 없으면 미국장 점수 미산출")
            with st.expander("🔎 미국장 티커별 수집 진단", expanded=False):
                _diag_rows = []
                for _ticker, _label in US_MARKET_TICKERS.items():
                    _row = _us_snapshot.get(_ticker)
                    _diag_rows.append({"티커": _ticker, "분류": _label, "상태": "수집 성공" if _row else "미수집", "기준일": (_row or {}).get("date", "—"), "20일 수익률(%)": round(float(_row["ret20"]), 2) if _row and np.isfinite(safe_float(_row.get("ret20"), np.nan)) else "—", "SPY 대비 20일(%)": round(float(_row["rs20"]), 2) if _row and np.isfinite(safe_float(_row.get("rs20"), np.nan)) else "SPY/상대강도 미확인"})
                st.dataframe(pd.DataFrame(_diag_rows), use_container_width=True, hide_index=True)
                st.caption("SPY가 수집되지 않으면 상대강도는 계산되지 않습니다. ‘미수집’은 가격 제공처 응답, 데이터 길이 또는 날짜 검증에서 제외됐음을 뜻합니다.")
        else:
            st.warning("미국장 데이터 수집 결과가 0개입니다. 가격 제공처 응답 또는 날짜/데이터 길이 검증 단계에서 실패했을 수 있습니다.")
            with st.expander("🔎 미국장 티커별 수집 진단", expanded=True):
                st.dataframe(pd.DataFrame([{"티커": t, "분류": label, "상태": "미수집"} for t, label in US_MARKET_TICKERS.items()]), use_container_width=True, hide_index=True)
    except Exception:
        st.warning("미국장 데이터 연결 상태를 확인할 수 없습니다. 미국장 점수를 확정 신호로 해석하지 마세요.")
    # 미국장 가격 수집 성공과 국내 ETF 테마 연결 성공을 분리해서 진단합니다.
    # 티커 수집표만으로는 어떤 국내 테마가 연결되지 않았는지 알 수 없어 최종 타겟별 연결표를 추가합니다.
    if targets:
        with st.expander("🧩 국내 ETF별 미국장 테마 연결 진단", expanded=False):
            _mapping_diag = []
            for _target in targets:
                _raw_score = safe_float(_target.get("us_theme_score"), np.nan)
                _mapping_diag.append({
                    "국내 ETF": str(_target.get("name") or _target.get("etf_name") or _target.get("code") or ""),
                    "종목코드": str(_target.get("code") or ""),
                    "국내 테마": str(_target.get("future_theme") or _target.get("theme") or "미분류"),
                    "미국 티커": ", ".join(_target.get("us_theme_tickers", [])) if isinstance(_target.get("us_theme_tickers"), (list, tuple, set)) else str(_target.get("us_theme_tickers") or ""),
                    "미국 점수": round(float(_raw_score), 1) if np.isfinite(_raw_score) else "미산출",
                    "미국 기준일": str(_target.get("us_theme_score_as_of") or _target.get("us_theme_as_of") or "—"),
                    "연결 근거": str(_target.get("us_theme_mapping") or "미국 테마 미확인"),
                    "최종 분류": str(_target.get("recommendation_type") or "국내시장 후보"),
                })
            st.dataframe(pd.DataFrame(_mapping_diag), use_container_width=True, hide_index=True)
            st.caption("미국 티커 수집이 성공해도 국내 테마와 사전 연결표가 일치하지 않으면 미국 점수는 미산출입니다. 연결 근거 열에서 미확인·데이터 미확보가 나타나는지 확인하세요.")
    if not targets:
        st.info("현재 가격 및 미래테마 연결 데이터에서 평가할 후보를 찾지 못했습니다.")
        return
    us_targets = [x for x in targets if x.get("recommendation_type") == "미국장 선행 타겟"]
    domestic_targets = [x for x in targets if x.get("recommendation_type") != "미국장 선행 타겟"]
    if us_targets:
        st.markdown("### 🇺🇸 미국장 신호로 찾은 추천")
        _render_final_target_list(us_targets, data, "미국장 선행 타겟")
    else:
        st.info("현재 미국 테마·유효 점수·티커·기준일·연결 근거가 모두 확인된 국내 ETF 타겟이 없습니다. 근거가 부족한 후보에 미국장 점수를 임의로 부여하지 않았습니다.")
    if domestic_targets:
        st.markdown("### 🇰🇷 국내시장 추천 · 미국장 선행 신호 미확인")
        st.caption("아래 후보는 국내 가격·테마 데이터만으로 평가했습니다. 미국장 선행 신호가 확인된 타겟과 구분해서 보세요.")
        _render_final_target_list(domestic_targets, data, "국내시장 후보")
    render_spot_tracking_panel()


def _render_final_target_list(targets, data, group_label):
    """Compact recommendation-first UI: one clear pick, short alternatives, details on demand."""
    unique_targets = []
    seen_codes = set()
    for candidate in (targets or []):
        if not isinstance(candidate, dict):
            continue
        code_key = _normalize_etf_code(candidate.get("code", ""))
        if not code_key or code_key in seen_codes:
            continue
        seen_codes.add(code_key)
        unique_targets.append(candidate)
    unique_targets.sort(key=lambda z: (safe_float(z.get("final_score"), -1), safe_float(z.get("relative_strength_score"), -1), safe_float(z.get("momentum_score"), -1)), reverse=True)
    for rank, candidate in enumerate(unique_targets, 1):
        candidate["final_rank"] = rank
    entry_sorted = sorted(unique_targets, key=lambda z: (safe_float(z.get("entry_score"), -1), safe_float(z.get("final_score"), -1)), reverse=True)
    for rank, candidate in enumerate(entry_sorted, 1):
        candidate["entry_rank"] = rank
    if not unique_targets:
        st.info(f"{group_label}: 현재 평가 가능한 ETF가 없습니다.")
        return

    top = _diversified_target_shortlist(unique_targets, 5, 2)
    st.caption(f"{group_label} {len(unique_targets)}개 · 추천 기준 {data.get('time', '최신 데이터')} · 점수는 수익 보장이 아닌 후보 우선순위입니다.")
    primary = top[0] if top else unique_targets[0]
    code = _normalize_etf_code(primary.get("code", ""))
    already = code in st.session_state.watchlist
    us_score = safe_float(primary.get("us_theme_score"), np.nan)
    target_score = safe_float(primary.get("final_score"), np.nan)
    entry_score = safe_float(primary.get("entry_score"), np.nan)
    us_text = f"{us_score:.1f}/100" if np.isfinite(us_score) else "미산출"
    target_text = f"{target_score:.1f}" if np.isfinite(target_score) else "미산출"
    entry_text = f"{entry_score:.1f}" if np.isfinite(entry_score) else "미산출"
    link_type = str(primary.get("us_link_type", primary.get("us_link_grade", "")) or "")
    us_tickers = primary.get("us_theme_tickers", [])
    ticker_text = ", ".join(str(t) for t in us_tickers if t) if isinstance(us_tickers, (list, tuple)) else str(us_tickers or "")
    us_date = str(primary.get("us_theme_score_as_of") or "미확인")
    theme = str(primary.get("future_theme", primary.get("theme", "테마 미분류")) or "테마 미분류")
    rec_type = str(primary.get("recommendation_type", group_label) or group_label)
    entry_status = str(primary.get("entry_status", "진입 상태 추가 확인") or "진입 상태 추가 확인")
    entry_data = str(primary.get("entry_data_status", "지표 확인 필요") or "지표 확인 필요")
    reason = str(primary.get("final_reason", "선정 근거를 추가 확인해야 합니다.") or "선정 근거를 추가 확인해야 합니다.")
    try:
        df = load_price_data(code)
        ind = calculate_indicators(df) if not df.empty else pd.DataFrame()
        current_price = safe_float(ind.iloc[-1].get("Close"), 0.0) if not ind.empty else 0.0
    except Exception:
        current_price = 0.0
    price_text = money(current_price) if current_price > 0 else "가격 미확인"

    card_html = f"""<div style="border:2px solid #3b82f6;border-radius:14px;padding:16px;margin:8px 0 12px;background:linear-gradient(145deg,rgba(59,130,246,.12),rgba(15,23,42,.2));">
      <div style="font-size:12px;font-weight:700;opacity:.85;margin-bottom:7px;">⭐ {esc(group_label)} · 1순위</div>
      <div style="font-size:21px;font-weight:800;line-height:1.3;margin-bottom:4px;">{esc(str(primary.get('name','이름 미확인')))}</div>
      <div style="font-size:12px;opacity:.8;margin-bottom:12px;">{esc(code or '코드 미확인')} · {esc(theme)} · {esc(price_text)}</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
        <div style="flex:1;min-width:90px;background:rgba(100,116,139,.15);border-radius:9px;padding:9px;"><div style="font-size:11px;opacity:.8;">장기 타겟</div><div style="font-size:22px;font-weight:800;">{esc(target_text)}<span style="font-size:11px;font-weight:500;"> / 100</span></div></div>
        <div style="flex:1;min-width:90px;background:rgba(100,116,139,.15);border-radius:9px;padding:9px;"><div style="font-size:11px;opacity:.8;">현재 진입</div><div style="font-size:22px;font-weight:800;">{esc(entry_text)}<span style="font-size:11px;font-weight:500;"> / 100</span></div></div>
        <div style="flex:1;min-width:90px;background:rgba(100,116,139,.15);border-radius:9px;padding:9px;"><div style="font-size:11px;opacity:.8;">미국장 신호</div><div style="font-size:22px;font-weight:800;">{esc(us_text)}</div></div>
      </div>
      <div style="font-size:13px;font-weight:700;margin-bottom:4px;">지금 판단: {esc(entry_status)}</div>
      <div style="font-size:12px;line-height:1.55;opacity:.9;">{esc(reason).replace('. ', '.<br>')}</div>
    </div>"""
    st.markdown(card_html, unsafe_allow_html=True)

    with st.expander("📰 최근 미국 뉴스로 보는 테마 부상 배경", expanded=False):
        render_theme_news_panel(theme)

    b1, b2 = st.columns([1, 2])
    with b1:
        if st.button("⭐ 관심등록" if not already else "⭐ 관심등록됨", disabled=already, use_container_width=True, key=f"simple_watch_{group_label}_{code}"):
            add_watch(code); st.session_state.selected_code = code; st.rerun()
    with b2:
        with st.expander("왜 이 ETF인가? · 연결 근거와 위험 보기", expanded=False):
            st.write(f"**추천 유형:** {rec_type}")
            st.write(f"**진입 지표 상태:** {entry_data}")
            st.write(f"**미국장 ETF:** {ticker_text or '미확인'}")
            st.write(f"**미국장 기준일:** {us_date}")
            st.write(f"**연결 등급:** {link_type or '미확인'}")
            evidence = primary.get('us_theme_link_evidence', primary.get('us_theme_mapping_reason', primary.get('us_link_evidence', '자료 확인 필요')))
            st.write(f"**연결 근거:** {evidence or '자료 확인 필요'}")
            st.write(f"**위험 감점:** {safe_float(primary.get('entry_risk_penalty'), 0):.1f}점")
            penalties = primary.get('entry_penalty_reasons', [])
            st.write("**진입 위험:** " + (" · ".join(penalties) if isinstance(penalties, (list, tuple)) and penalties else "계산된 감점 없음"))
            st.caption("미국장 신호 또는 연결 근거가 미확인인 후보는 미국장 선행 타겟으로 해석하면 안 됩니다.")
            render_final_target_trade_strategy(code, primary)

    if len(top) > 1:
        st.markdown("#### 다른 추천 후보")
        for item in top[1:]:
            ccode = _normalize_etf_code(item.get("code", ""))
            tscore = safe_float(item.get("final_score"), np.nan)
            escore = safe_float(item.get("entry_score"), np.nan)
            tscore_text = f"{tscore:.1f}" if np.isfinite(tscore) else "—"
            escore_text = f"{escore:.1f}" if np.isfinite(escore) else "—"
            theme_text = str(item.get("future_theme", item.get("theme", "테마 미분류")) or "테마 미분류")
            with st.expander(f"#{item.get('final_rank', '-')}  {item.get('name', '이름 미확인')}  ·  타겟 {tscore_text} / 진입 {escore_text}", expanded=False):
                st.write(f"**코드:** {ccode or '미확인'} · **테마:** {theme_text}")
                st.write(f"**현재 판단:** {item.get('entry_status', '추가 확인')} · **지표:** {item.get('entry_data_status', '확인 필요')}")
                st.write(f"**선정 근거:** {item.get('final_reason', '자료 확인 필요')}")
                ic1, ic2 = st.columns([1, 2])
                with ic1:
                    is_saved = ccode in st.session_state.watchlist
                    if st.button("관심등록" if not is_saved else "등록됨", disabled=is_saved, key=f"simple_watch_alt_{group_label}_{ccode}", use_container_width=True):
                        add_watch(ccode); st.session_state.selected_code = ccode; st.rerun()
                with ic2:
                    st.caption(f"미국장: {item.get('us_theme_score', '미산출')} · 티커: {item.get('us_theme_tickers', '미확인')} · 기준일: {item.get('us_theme_score_as_of', '미확인')}")

    entry_ranked = sorted(unique_targets, key=lambda z: (safe_float(z.get("entry_score"), -1), safe_float(z.get("final_score"), -1)), reverse=True)
    with st.expander("현재 진입 순위 전체 보기", expanded=False):
        entry_rows = []
        for rank, item in enumerate(entry_ranked[:10], 1):
            risk = item.get("entry_penalty_reasons", [])
            entry_rows.append({
                "진입순위": rank, "ETF": item.get("name", "-"),
                "진입점수": round(safe_float(item.get("entry_score"), np.nan), 1) if np.isfinite(safe_float(item.get("entry_score"), np.nan)) else "미산출",
                "타겟점수": round(safe_float(item.get("final_score"), np.nan), 1) if np.isfinite(safe_float(item.get("final_score"), np.nan)) else "미산출",
                "판단": item.get("entry_status", "추가 확인"),
                "위험": " · ".join(risk) if isinstance(risk, (list, tuple)) and risk else "추가 확인 필요",
            })
        if entry_rows:
            st.dataframe(pd.DataFrame(entry_rows), use_container_width=True, hide_index=True)


# MARKET RADAR
# ============================================================

def get_benchmark_metrics():
    """Return KOSPI200 ETF benchmark returns without disguising missing data as 0%.

    A zero return is a real market observation; NaN means the benchmark could not be
    measured. Downstream relative-strength scores must not treat these as equivalent.
    """
    missing = {"ret20": np.nan, "ret5": np.nan, "ret60": np.nan, "available": False, "as_of": None}
    try:
        df = load_price_data("069500")
        if df is None or df.empty:
            return missing.copy()
        d = calculate_indicators(df)
        if d is None or d.empty or len(d) < 61:
            return missing.copy()
        row = d.iloc[-1]
        close = pd.to_numeric(d["Close"], errors="coerce")
        values = {
            "ret20": safe_float(row.get("RET20"), np.nan),
            "ret5": safe_float(row.get("RET5"), np.nan),
            "ret60": safe_float(close.pct_change(60).iloc[-1] * 100, np.nan),
        }
        if not all(np.isfinite(v) for v in values.values()):
            return missing.copy()
        values.update({"available": True, "as_of": str(pd.to_datetime(d.index[-1]).date())})
        return values
    except Exception:
        return missing.copy()


def radar_theme_for(code, name):
    text=f"{code} {name}"
    best=None; hits=0
    for theme,keywords in THEME_LEXICON.items():
        h=_theme_match_for_theme(text,keywords,theme)
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
    """시장레이더는 미래테마 후보 + 보유 ETF를 중심으로 분석합니다.
    전체 ETF의 가격데이터를 매번 조회하지 않도록 후보군을 제한합니다.
    """
    targets = {}

    # 미래테마 TOP 10에 포함된 ETF만 레이더 후보로 사용합니다.
    # build_future_theme_engine() 결과는 자체 캐시를 사용하므로 매번 재계산하지 않습니다.
    try:
        engine = build_future_theme_engine()
        details = engine.get("details", {}) if engine else {}
        for info in details.values():
            for row in info.get("rows", []):
                code = _normalize_etf_code(row.get("code"))
                if not code:
                    continue
                name = row.get("name") or get_etf_name(code)
                if name and not str(name).startswith("ETF "):
                    targets[code] = name
    except Exception:
        pass

    # 보유 ETF는 미래테마에 없더라도 항상 포함합니다.
    for raw_code in st.session_state.get("holdings", []):
        code = _normalize_etf_code(raw_code)
        if not code:
            continue
        name = get_etf_name(code)
        if not name or name.startswith("ETF "):
            name = lookup_live_etf(code) or name
        targets[code] = name

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
    benchmark_available = bool(benchmark.get("available", False)) and np.isfinite(safe_float(benchmark.get("ret20"), np.nan)) and np.isfinite(safe_float(benchmark.get("ret60"), np.nan))
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
        prev_close = safe_float(d["Close"].iloc[-2], current) if len(d) >= 2 else current
        ret1 = ((current / prev_close) - 1.0) * 100.0 if prev_close else 0.0
        item = {
            "code": code, "name": name, "price": current,
            "rsi": safe_float(r["RSI14"], 50),
            "vr": safe_float(r["VOL_RATIO"], 1),
            "ret1": ret1,
            "ret5": safe_float(r["RET5"], 0),
            "ret20": safe_float(r["RET20"], 0),
            "dist20": (current / ma20 - 1) * 100 if ma20 else 0,
            "above20": current >= ma20,
            "above60": current >= ma60,
            # 유망후보 가격가이드가 실제 최신 지표를 사용하도록 원본 행을 함께 보관
            "raw": r.to_dict(),
        }
        # Relative strength is unavailable without a valid benchmark; do not substitute 0%.
        item["rs20"] = item["ret20"] - benchmark["ret20"] if benchmark_available else np.nan
        item["benchmark_available"] = benchmark_available
        item["benchmark_as_of"] = benchmark.get("as_of") if benchmark_available else None
        item["theme"] = radar_theme_for(code, name)
        item["stage"] = radar_stage_for(item["theme"])
        item["opportunity"] = radar_score(item)
        item["overheat"] = radar_overheat_score(item)

        # 미래테마 × 시장레이더 교차검증
        # 레이더 단독 점수가 아니라 테마 생애주기·선행성·가격 위치까지 함께 평가합니다.
        try:
            bench20 = safe_float(benchmark.get("ret20"), np.nan)
            bench60 = safe_float(benchmark.get("ret60"), np.nan)
            theme_name, theme_members = _find_theme_for_etf(code)
            item["future_theme"] = theme_name if theme_members else "미래테마 미연결"
            item["future_theme_related"] = bool(theme_members)
            tscore = theme_score(theme_members, bench20, bench60) if theme_members else 0.0
            lc = _theme_lifecycle(theme_members, benchmark) if theme_members else {"score":0.0,"state":"관찰"}
            lead = leading_signal(r, bench20)
            zone = validated_price_zone(r)
            pscore = {"매수구간":100,"눌림대기":70,"추격금지":25,"무효":0}.get(zone.get("state"),0)
            # 레이더 점수는 '현재 시장조건'만 평가합니다.
            # 미래테마 점수는 최종타겟에서 별도로 결합하여 중복 가중치를 줄입니다.
            cross = (
                float(np.clip(lead.get("score",0),0,100)) * 0.40 +
                float(np.clip(item["opportunity"],0,100)) * 0.30 +
                float(np.clip(pscore,0,100)) * 0.20 +
                float(np.clip(lc.get("score",0),0,100)) * 0.10
            )
            # The radar score is not considered fully validated without a measurable benchmark.
            if not benchmark_available:
                item["cross_score"] = None
                item["cross_state"] = "⚪ 기준지수 미확보 · 점수 보류"
                item["benchmark_warning"] = "069500 기준지수 가격/지표를 확보하지 못해 상대강도 기반 최종 점수를 확정하지 않았습니다."
            else:
                item["benchmark_warning"] = None
            # 현재 시장의 쇠퇴·과열은 레이더에서도 명시적으로 감점합니다.
            if lc.get("state") == "쇠퇴":
                cross -= 12
            elif lc.get("state") == "과열":
                cross -= 8
            if item["overheat"] >= 65:
                cross -= 10
            item["theme_score"] = round(float(tscore),1)
            # 최종 타겟의 테마명은 _find_theme_for_etf()에서 온 국내 분류명입니다.
            # future_theme_info()는 별도 미래테마 엔진의 키를 요구하므로 이름이 다르면
            # 미국장 연결이 있어도 빈 결과가 나올 수 있습니다. 동일한 선언형 매핑 함수를
            # 국내 테마 라벨에 직접 적용해 미국장 연결 누락을 방지합니다.
            try:
                _us_snapshot = get_us_market_snapshot()
                _us_impulse = _theme_us_impulse(theme_name, theme_members, _us_snapshot) if theme_members else {
                    "score": None, "available": False, "mapping": "국내 테마 구성 없음"
                }
            except Exception:
                _us_impulse = {"score": None, "available": False, "mapping": "미국장 데이터 조회 실패"}
            item["us_theme_score"] = safe_float(_us_impulse.get("score"), np.nan)
            item["us_theme_available"] = bool(_us_impulse.get("available", False))
            item["us_theme_mapping"] = str(_us_impulse.get("mapping", "미국장 신호 미연결"))
            item["us_theme_as_of"] = _us_impulse.get("as_of")
            item["us_theme_tickers"] = list(_us_impulse.get("used_tickers", []))
            item["us_theme_score_as_of"] = _us_impulse.get("as_of")
            item["lifecycle_score"] = round(float(lc.get("score",0)),1)
            item["lifecycle_state"] = lc.get("state","관찰")
            item["lead_score"] = round(float(lead.get("score",0)),1)
            item["price_zone"] = zone.get("state","확인")
            if benchmark_available:
                item["cross_score"] = int(np.clip(round(cross),0,100))
                if item["cross_score"] >= 80 and item["price_zone"] == "매수구간" and item["overheat"] < 65:
                    item["cross_state"] = "🔥 최우선 후보"
                elif item["cross_score"] >= 70:
                    item["cross_state"] = "🟢 우선 관찰"
                elif item["cross_score"] >= 55:
                    item["cross_state"] = "🟡 확인 필요"
                else:
                    item["cross_state"] = "⚪ 대기"
        except Exception:
            item.update({"theme_score":0.0,"lifecycle_score":0.0,"lifecycle_state":"관찰",
                         "lead_score":0.0,"price_zone":"확인","cross_score":0,"cross_state":"⚪ 대기",
                         "future_theme":"미래테마 미연결","future_theme_related":False})

        item["held"] = code in st.session_state.holdings
        rows.append(item)
    data = {"time": now, "rows": rows, "benchmark": benchmark, "target_key": target_key}
    st.session_state.radar_cache = data
    return data


def render_radar_card(item, mode, hide_title=False):
    # 시장 레이더 카드: 기회검색에서는 기존 후보선별을 유지하면서 실제 매매가격까지 표시.
    if mode == "🎯 유망후보":
        score = item.get("cross_score")
        if score is None or not np.isfinite(safe_float(score, np.nan)):
            score = "보류"
        state = item.get("cross_state", "기회 후보")
        badge = '<span class="radar-badge radar-badge-op">'+esc(state)+'</span>'
        title = "미래테마·선행성·시장레이더·가격구간을 모두 통과한 유망 후보"
    else:
        score = item["overheat"]
        badge = '<span class="radar-badge radar-badge-hot">과열 주의</span>'
        title = "단기 상승폭·RSI·이격·거래량을 함께 확인"
    held = '<span class="radar-badge radar-badge-hold">보유중</span>' if item["held"] else ''
    theme_text = f'{item["theme"]} · {item["stage"]}' if item["theme"] != "기타" else "테마 미분류"
    position = "20/60일선 위" if item["above20"] and item["above60"] else ("20일선 위 · 60일선 아래" if item["above20"] else "20일선 아래")
    guide_html = ""
    if mode == "🎯 유망후보":
        raw = item.get("raw") if isinstance(item, dict) else None
        if raw is None:
            raw = {}
        c = safe_float(raw.get("Close"), item.get("price", np.nan))
        ma20 = safe_float(raw.get("MA20"), c)
        ma60 = safe_float(raw.get("MA60"), c)
        low20 = safe_float(raw.get("LOW20"), c)
        if np.isfinite(c) and c > 0 and np.isfinite(ma20) and ma20 > 0 and np.isfinite(ma60) and ma60 > 0:
            support = max(low20, ma20 * 0.985)
            buy1 = ma20 * 1.025
            invalid = min(ma60 * 0.97, support * 0.97)
            if invalid <= 0: invalid = c * 0.92
            buy2 = (buy1 + invalid) / 2
            risk = max(buy1 - invalid, c * 0.05)
            tp1 = buy1 + risk
            tp2 = buy1 + risk * 2
            chase = ma20 * 1.07
            zone = item.get("price_zone", "확인")
            if zone == "매수구간": action = "🔥 지금 1차 매수 검토"
            elif zone == "눌림대기": action = "🟢 지금 추격하지 말고 눌림 2차 매수 대기"
            elif zone == "추격금지": action = "🔴 지금 매수 금지 · 눌림 대기"
            else: action = "🔴 매수 보류 · 가격구간 무효"
            guide_html = f'''<div class="radar-trade-title">실제 행동 / 가격</div>
  <div class="radar-action">{esc(action)}</div>
  <div class="radar-trade-grid">
    <div class="radar-trade-item"><div class="radar-label">1차 매수</div><div class="radar-trade-price">{money(buy1)}</div><div class="radar-trade-desc">20일선 + 2.5%</div></div>
    <div class="radar-trade-item"><div class="radar-label">2차 매수</div><div class="radar-trade-price">{money(buy2)}</div><div class="radar-trade-desc">눌림 구간</div></div>
    <div class="radar-trade-item"><div class="radar-label">추격 금지</div><div class="radar-trade-price">{money(chase)}</div><div class="radar-trade-desc">이상 매수 금지</div></div>
    <div class="radar-trade-item"><div class="radar-label">손절 / 무효</div><div class="radar-trade-price">{money(invalid)}</div><div class="radar-trade-desc">가격 이탈 시 재평가</div></div>
    <div class="radar-trade-item"><div class="radar-label">1차 익절</div><div class="radar-trade-price">{money(tp1)}</div><div class="radar-trade-desc">1R</div></div>
    <div class="radar-trade-item"><div class="radar-label">2차 익절</div><div class="radar-trade-price">{money(tp2)}</div><div class="radar-trade-desc">2R</div></div>
  </div>
  <div class="radar-follow">이후: <b>20일선 추적</b> · 1차/2차 익절 후 잔여 물량은 20일선 이탈 여부를 우선 확인</div>'''
    title_html = "" if hide_title else f'<div class="radar-title">{esc(item["name"])} · {esc(item["code"])}</div>'
    st.markdown(f'''<div class="radar-card">
  <div>{badge}{held}</div>
  {title_html}
  <div class="radar-sub">{esc(title)} · {esc(theme_text)}</div>
  <div style="display:flex;justify-content:space-between;align-items:center;margin-top:7px;">
     <div class="radar-score-block"><div class="radar-label">레이더 점수</div><div class="radar-score">{score}</div><div class="radar-score-code">{esc(item["code"])}</div></div>
    <div style="text-align:right"><div class="radar-label">현재가</div><div class="radar-value">{money(item["price"])}</div></div>
  </div>
  <div class="radar-grid">
    <div class="radar-metric"><div class="radar-label">테마</div><div class="radar-value">{item.get("theme_score",0):.0f}</div></div>
    <div class="radar-metric"><div class="radar-label">선행</div><div class="radar-value">{item.get("lead_score",0):.0f}</div></div>
    <div class="radar-metric"><div class="radar-label">가격</div><div class="radar-value">{esc(item.get("price_zone","확인"))}</div></div>
    <div class="radar-metric"><div class="radar-label">생애주기</div><div class="radar-value">{esc(item.get("lifecycle_state","관찰"))}</div></div>
  </div>
  <div class="radar-note">20일선 대비 <b>{item["dist20"]:+.1f}%</b> · {position} · 미래테마×레이더 교차점수 <b>{esc(str(item.get("cross_score") if item.get("cross_score") is not None else "보류"))}</b> · 최근 5일 <b>{item["ret5"]:+.1f}%</b> · RSI <b>{item["rsi"]:.1f}</b></div>
  <div class="radar-note">미래테마 연결: <b>{("🟢 실제 후보 · " + str(item.get("future_theme")) + " · ETF 순위 #" + str(item.get("future_theme_rank"))) if item.get("future_theme_selected") else (("🟡 연관테마 · " + str(item.get("future_theme"))) if item.get("future_theme_related") else "⚪ 현재 미래테마 엔진과 직접 연결되지 않음")}</b></div>
</div>''', unsafe_allow_html=True)

    if mode == "🎯 유망후보":
        with st.expander("💰 실제 행동 / 매수가·손절·익절 보기", expanded=False):
            if guide_html:
                st.markdown(guide_html, unsafe_allow_html=True)
            else:
                st.info("현재 가격 데이터로 행동 가격을 계산할 수 없습니다.")


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
    radar_modes = ["🎯 유망후보", "⚠️ 과열검색", "🔄 테마순환"]
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
    if mode == "🎯 유망후보":
        candidates = [x for x in rows if x["opportunity"] >= 55 and x["rsi"] < 72 and x["ret5"] < 8 and x.get("benchmark_available", False)]
        candidates.sort(key=lambda x:(safe_float(x.get("cross_score"), -1), x["opportunity"], safe_float(x.get("rs20"), -999), -x["ret5"]), reverse=True)
        st.markdown("### 🔥 아직 안 오른 강세 유망 후보")
        if any(not x.get("benchmark_available", False) for x in rows):
            st.caption("기준지수 데이터가 유효하지 않은 동안에는 상대강도 기반 유망후보 순위를 보류합니다.")
        st.caption("미래테마가 살아 있고 → 테마가 확산되고 → ETF가 선행하고 → 시장레이더도 잡히면서 → 아직 단기 급등하지 않은 후보입니다. 아래에서 바로 매수·손절·익절 가격과 행동을 확인합니다.")
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
# 통합 백테스트 LAB
# ============================================================

BT_POOL = {
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

BT_BENCH = "SPY"

BT_THEME_GROUPS = {
    "미국기술": ["QQQ", "XLK"],
    "반도체": ["SMH", "SOXX"],
    "로봇AI": ["BOTZ", "ARKQ"],
    "위험선호": ["QQQ", "XLK", "SMH", "SOXX", "BOTZ", "ARKQ"],
    "방어자산": ["GLD", "TLT"],
    "글로벌": ["INDA", "EWY", "EWJ", "EEM"],
}

def bt_download_prices(tickers, start, end):
    symbols = list(dict.fromkeys(list(tickers) + [BT_BENCH]))
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

def bt_indicators(d):
    d = d.copy()
    if "Close" not in d.columns:
        return pd.DataFrame()
    d["Close"] = pd.to_numeric(d["Close"], errors="coerce")
    d["Volume"] = pd.to_numeric(d.get("Volume", np.nan), errors="coerce")
    d = d.dropna(subset=["Close"])

    d["MA20"] = d["Close"].rolling(20).mean()
    d["MA60"] = d["Close"].rolling(60).mean()
    d["MA120"] = d["Close"].rolling(120).mean()
    d["MA200"] = d["Close"].rolling(200).mean()
    d["R5"] = d["Close"].pct_change(5) * 100
    d["R20"] = d["Close"].pct_change(20) * 100
    d["R60"] = d["Close"].pct_change(60) * 100
    d["R120"] = d["Close"].pct_change(120) * 100
    d["R252"] = d["Close"].pct_change(252) * 100
    d["HIGH252"] = d["Close"].rolling(252).max()
    d["VR"] = d["Volume"] / d["Volume"].rolling(20).mean()

    delta = d["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    d["RSI"] = 100 - 100 / (1 + rs)

    d["VOL20"] = d["Volume"].rolling(20).mean()
    d["LOW20"] = d["Close"].rolling(20).min()
    d["HIGH20"] = d["Close"].rolling(20).max()
    return d

def bt_leading_signal(row, benchmark_ret20=0):
    current = float(row.get("Close", 0) or 0)
    ma20 = float(row.get("MA20", current) or current)
    ma60 = float(row.get("MA60", current) or current)
    ret5 = float(row.get("R5", 0) or 0)
    ret20 = float(row.get("R20", 0) or 0)
    vr = float(row.get("VR", 1) or 1)
    rsi = float(row.get("RSI", 50) or 50)

    dist20 = (current / ma20 - 1) * 100 if ma20 else 0
    rs20 = ret20 - benchmark_ret20
    accel = ret5 - ret20 / 4

    early_price = 92 if -1 <= dist20 <= 3 else 82 if dist20 <= 5 else 65 if dist20 < 8 else 35
    early_rsi = 92 if 48 <= rsi <= 62 else 84 if 43 <= rsi < 68 else 68 if rsi < 72 else 35
    flow = 92 if 1.10 <= vr <= 1.70 else 82 if 1.0 <= vr < 1.10 else 76 if 0.9 <= vr < 1.0 else 58 if vr < 2.2 else 38
    accel_score = 90 if 0.5 <= accel <= 5 else 78 if 0 <= accel < 0.5 else 68 if accel > 5 else 52
    rel = 88 if rs20 >= 6 else 80 if rs20 >= 3 else 70 if rs20 >= 0 else 48
    structure = 90 if current >= ma60 and ma20 >= ma60 else 78 if current >= ma60 else 55 if current >= ma20 else 35

    score = round(
        early_price * 0.22
        + early_rsi * 0.18
        + flow * 0.22
        + accel_score * 0.16
        + rel * 0.14
        + structure * 0.08
    )

    early_buy = score >= 72 and vr >= 1.05 and rsi < 70 and dist20 < 7 and rs20 >= -1

    return {
        "score": int(max(0, min(100, score))),
        "early_buy": bool(early_buy),
        "rs20": rs20,
        "dist20": dist20,
        "rsi": rsi,
        "vr": vr,
        "accel": accel,
    }

def bt_theme_score(theme_rows, bench_ret20=0, bench_ret60=0):
    if len(theme_rows) < 2:
        return None

    vals = []
    for r in theme_rows:
        if pd.isna(r.get("R20")) or pd.isna(r.get("R60")):
            continue
        sig = bt_leading_signal(r, bench_ret20)
        vals.append({
            "r20": float(r["R20"]),
            "r60": float(r["R60"]),
            "rs20": sig["rs20"],
            "rs60": float(r["R60"]) - bench_ret60,
            "vr": float(r.get("VR", 1) if pd.notna(r.get("VR", 1)) else 1),
            "ma60gap": ((float(r["Close"]) / float(r["MA60"]) - 1) * 100) if pd.notna(r.get("MA60")) and r["MA60"] else 0,
            "accel": sig["accel"],
            "rsi": sig["rsi"],
            "lead": sig["score"],
            "early": sig["early_buy"],
        })

    if len(vals) < 2:
        return None

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
    rsi = 100 - abs(float(x["rsi"].mean()) - 58) * 2.5
    rsi = float(np.clip(rsi, 0, 100))

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

    early_count = int(x["early"].sum())
    early_ratio = early_count / len(x)
    lead_avg = float(x["lead"].mean())

    # 기존 앱의 선행 테마 개념을 반영
    lead_theme = lead_avg * 0.55 + breadth * 0.25 + early_ratio * 100 * 0.20
    final = score * 0.70 + lead_theme * 0.30

    # 과열 패널티: 너무 많이 오른 테마는 미래테마 후보에서 감점
    heat = 0
    if float(x["rsi"].mean()) >= 75:
        heat += 12
    if float(x["r20"].mean()) >= 12:
        heat += 10
    if float(x["ma60gap"].mean()) >= 15:
        heat += 8

    final = float(np.clip(final - heat, 0, 100))

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

def bt_build_snapshot(all_data, date_i):
    bench = all_data.get(BT_BENCH)
    if bench is None or bench.empty:
        return None

    b = bench.iloc[: date_i + 1]
    if len(b) < 65:
        return None
    br = b.iloc[-1]
    bench_ret20 = float(br.get("R20", np.nan))
    bench_ret60 = float(br.get("R60", np.nan))
    if not np.isfinite(bench_ret20) or not np.isfinite(bench_ret60):
        return None

    theme_results = []
    for theme, members in BT_THEME_GROUPS.items():
        rows = []
        for t in members:
            d = all_data.get(t)
            if d is None or d.empty or len(d) <= date_i:
                continue
            r = d.iloc[date_i]
            if pd.isna(r.get("MA60")) or pd.isna(r.get("R20")) or pd.isna(r.get("R60")):
                continue
            rr = r.to_dict()
            rr["ETF"] = t
            rows.append(rr)
        ts = bt_theme_score(rows, bench_ret20, bench_ret60)
        if ts:
            ts["theme"] = theme
            ts["rows"] = rows
            theme_results.append(ts)

    if not theme_results:
        return None

    theme_results.sort(key=lambda z: z["score"], reverse=True)
    top = theme_results[0]
    candidates = []
    for r in top["rows"]:
        sig = bt_leading_signal(r, bench_ret20)
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
        candidates.append({"ETF": r["ETF"], "sig": sig, "heat": min(100, heat), "close": c, "ma20": ma20})

    if not candidates:
        return None

    # 선행점수 - 과열패널티를 적용해 테마 대표 ETF를 선정
    candidates.sort(key=lambda z: z["sig"]["score"] - z["heat"] * 0.35, reverse=True)
    winner = candidates[0]

    return {
        "theme": top["theme"],
        "bt_theme_score": top["score"],
        "theme_stage": top["stage"],
        "winner": winner,
        "themes": theme_results,
    }

def bt_price_zone(r):
    c = float(r["Close"])
    ma20 = float(r["MA20"])
    ma60 = float(r["MA60"])
    low20 = float(r["LOW20"])

    # 매수 가능: MA20 부근/최근 저점 부근 + 추세 훼손 전
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

def bt_run_strategy_backtest(start, end, tickers, step_days=5):
    download_start = (pd.Timestamp(start) - pd.Timedelta(days=140)).strftime("%Y-%m-%d")
    download_end = (pd.Timestamp(end) + pd.Timedelta(days=80)).strftime("%Y-%m-%d")

    raw = bt_download_prices(tickers, download_start, download_end)
    data = {k: bt_indicators(v) for k, v in raw.items()}
    data = {k: v for k, v in data.items() if not v.empty}

    if BT_BENCH not in data:
        raise RuntimeError("SPY 벤치마크 데이터를 가져오지 못했습니다.")

    common = data[BT_BENCH].index
    for t in tickers:
        if t in data:
            common = common.intersection(data[t].index)
    common = common.sort_values()
    common = common[(common >= pd.Timestamp(start)) & (common <= pd.Timestamp(end))]

    rows = []
    dates_used = []

    # 5거래일 간격으로 검사하여 실행시간을 줄이고 과도한 중복신호를 완화
    for pos in range(0, len(common) - 61, max(1, step_days)):
        dt = common[pos]
        hist_pos = data[BT_BENCH].index.get_loc(dt)
        snap = bt_build_snapshot(data, hist_pos)
        if snap is None:
            continue

        winner = snap["winner"]
        t = winner["ETF"]
        d = data[t]
        if hist_pos + 60 >= len(d):
            continue

        # 신호 당일 종가가 아닌 다음 거래일 종가 진입
        entry_i = hist_pos + 1
        entry = d.iloc[entry_i]
        entry_price = float(entry["Close"])
        if not np.isfinite(entry_price) or entry_price <= 0:
            continue

        # 전략 A: 선택된 테마의 대표 ETF를 무조건 보유
        # 전략 B: 선행점수 >=72
        # 전략 C: 미래테마 + 선행 ETF
        # 전략 D: 미래테마 + 선행 ETF + 가격구간
        sig = winner["sig"]
        zone = bt_price_zone(d.iloc[hist_pos])

        # A: 단순 테마 대표 ETF
        a_ok = True
        # B: 개별 선행점수만 통과
        b_ok = sig["score"] >= 72 and sig["early_buy"]
        # C: 미래테마 + 선행 ETF
        c_ok = snap["bt_theme_score"] >= 60 and b_ok
        # D: C + 가격구간
        d_ok = c_ok and zone["state"] == "매수구간"

        future = d.iloc[entry_i + 0 : entry_i + 60]
        if len(future) < 60:
            continue

        rec = {
            "날짜": dt.date(),
            "테마": snap["theme"],
            "테마점수": round(snap["bt_theme_score"], 1),
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
            ret = (float(future.iloc[n - 1]["Close"]) / entry_price - 1) * 100
            dd = (float(future.iloc[:n]["Close"].min()) / entry_price - 1) * 100
            rec[f"{n}일수익"] = ret
            rec[f"{n}일최저낙폭"] = dd

        # 전략별 활성 여부에 따른 결과도 별도 저장
        rows.append(rec)
        dates_used.append(dt)

    return pd.DataFrame(rows), data

def bt_strategy_summary(r, flag, horizon):
    x = r.loc[r[flag], f"{horizon}일수익"].dropna()
    dd = r.loc[r[flag], f"{horizon}일최저낙폭"].dropna()
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
        "승률": (x > 0).mean() * 100,
        "평균수익": x.mean(),
        "중앙값": x.median(),
        "평균낙폭": dd.mean() if not dd.empty else np.nan,
        "최고": x.max(),
        "최대손실": x.min(),
    }

def bt_simulate_equity_curve(r, data, initial_cash=1_000_000, hold_days=20,
                          fee_per_side=0.0010, slippage_per_side=0.0005):
    """D 전략을 실제 포트폴리오처럼 1회 1포지션으로 순차 시뮬레이션.
    - 신호일 이후 다음 거래일 종가 진입
    - D 조건만 사용
    - 보유 중 새 신호는 무시
    - 기본은 hold_days 후 청산
    - 수수료+슬리피지를 매수/매도 각각 반영
    """
    if r is None or r.empty:
        return pd.DataFrame(), {}
    rr = r.loc[r["D_미래테마선행가격"] == True].copy()
    rr["날짜"] = pd.to_datetime(rr["날짜"])
    rr = rr.sort_values("날짜").reset_index(drop=True)

    cash = float(initial_cash)
    equity_rows = []
    trades = []
    next_available = pd.Timestamp.min
    n_days = 0
    wins = 0

    for _, sig in rr.iterrows():
        signal_date = pd.Timestamp(sig["날짜"])
        if signal_date < next_available:
            continue
        ticker = sig["ETF"]
        d = data.get(ticker)
        if d is None or d.empty:
            continue
        idx = d.index.searchsorted(signal_date)
        entry_i = idx + 1
        exit_i = entry_i + int(hold_days) - 1
        if entry_i >= len(d) or exit_i >= len(d):
            continue
        entry_date = d.index[entry_i]
        exit_date = d.index[exit_i]
        entry_raw = float(d.iloc[entry_i]["Close"])
        exit_raw = float(d.iloc[exit_i]["Close"])
        if not np.isfinite(entry_raw) or not np.isfinite(exit_raw) or entry_raw <= 0:
            continue

        # 매수/매도 슬리피지를 불리하게 적용
        buy_price = entry_raw * (1 + slippage_per_side)
        sell_price = exit_raw * (1 - slippage_per_side)
        gross_ret = sell_price / buy_price - 1
        net_ret = gross_ret - fee_per_side * 2
        start_cash = cash
        cash = cash * (1 + net_ret)
        wins += int(net_ret > 0)
        n_days += max(1, (exit_date - entry_date).days)
        next_available = exit_date + pd.Timedelta(days=1)

        trades.append({
            "신호일": signal_date.date(), "진입일": entry_date.date(), "청산일": exit_date.date(),
            "테마": sig["테마"], "ETF": ticker, "테마점수": sig["테마점수"],
            "선행점수": sig["선행점수"], "가격상태": sig["가격상태"],
            "진입가격": entry_raw, "청산가격": exit_raw,
            "순수익률": net_ret * 100, "거래후자산": cash,
        })
        equity_rows.append({"날짜": exit_date, "자산": cash})

    trades_df = pd.DataFrame(trades)
    curve = pd.DataFrame(equity_rows)
    if curve.empty:
        return curve, {"초기자산": initial_cash, "최종자산": initial_cash, "총수익률": 0.0,
                       "승률": np.nan, "거래수": 0, "최대낙폭": 0.0, "연환산": np.nan}
    curve = curve.sort_values("날짜").drop_duplicates("날짜", keep="last")
    curve["고점"] = curve["자산"].cummax()
    curve["낙폭"] = (curve["자산"] / curve["고점"] - 1) * 100
    final_cash = float(curve.iloc[-1]["자산"])
    total_ret = (final_cash / initial_cash - 1) * 100
    days = max(1, (pd.Timestamp(curve.iloc[-1]["날짜"]) - pd.Timestamp(curve.iloc[0]["날짜"])).days)
    annualized = ((final_cash / initial_cash) ** (365.25 / days) - 1) * 100 if final_cash > 0 else -100
    metrics = {
        "초기자산": initial_cash, "최종자산": final_cash, "총수익률": total_ret,
        "승률": (wins / len(trades_df) * 100) if len(trades_df) else np.nan,
        "거래수": len(trades_df), "최대낙폭": float(curve["낙폭"].min()), "연환산": annualized,
        "평균거래수익": float(trades_df["순수익률"].mean()) if not trades_df.empty else np.nan,
    }
    return curve, {**metrics, "trades": trades_df}

def bt_simulate_buy_hold(ticker, data, initial_cash=1_000_000):
    d = data.get(ticker)
    if d is None or d.empty:
        return pd.DataFrame(), {}
    x = d.dropna(subset=["Close"]).copy()
    if len(x) < 2:
        return pd.DataFrame(), {}
    p0 = float(x.iloc[0]["Close"])
    curve = pd.DataFrame({"날짜": x.index, "자산": initial_cash * x["Close"] / p0})
    curve["고점"] = curve["자산"].cummax()
    curve["낙폭"] = (curve["자산"] / curve["고점"] - 1) * 100
    final_cash = float(curve.iloc[-1]["자산"])
    days = max(1, (x.index[-1] - x.index[0]).days)
    annualized = ((final_cash / initial_cash) ** (365.25 / days) - 1) * 100
    return curve, {"초기자산": initial_cash, "최종자산": final_cash,
                   "총수익률": (final_cash / initial_cash - 1) * 100,
                   "최대낙폭": float(curve["낙폭"].min()), "연환산": annualized}

def bt_horizon_judgment_backtest_row(d, i):
    """시점 i까지의 정보만 사용해 장기/단기 판정을 만들고
    이후 20/60/120/250 거래일 성과를 별도로 기록한다.
    미래 데이터는 판정 계산에 사용하지 않는다.
    """
    if i < 200 or i + 250 >= len(d):
        return None

    r = d.iloc[i]
    close = float(r["Close"])
    ma60 = float(r["MA60"])
    ma120 = float(r["MA120"])
    ma200 = float(r["MA200"])
    r60 = float(r["R60"])
    r20 = float(r["R20"])
    r5 = float(r["R5"])
    rsi = float(r["RSI"])
    vr = float(r["VR"]) if np.isfinite(r["VR"]) else 1.0

    # 장기 보유 판단: 장기 추세 + 장기 모멘텀 + 장기 추세 훼손 여부
    long_score = 0
    long_score += 25 if close > ma200 else 0
    long_score += 20 if ma120 > ma200 else 0
    long_score += 15 if ma60 > ma120 else 0
    long_score += 15 if r60 > 10 else 8 if r60 > 0 else 0
    long_score += 15 if ma200 >= float(d.iloc[i-21]["MA200"]) else 0
    long_score += 10 if ma120 >= float(d.iloc[i-21]["MA120"]) else 0

    if long_score >= 80:
        long_state = "🟢 장기 핵심보유"
    elif long_score >= 65:
        long_state = "🟢 장기 보유"
    elif long_score >= 50:
        long_state = "🟡 추세 확인"
    else:
        long_state = "🔴 장기 재검토"

    # 단기 운용 판단: 최근 모멘텀 + MA20/60 + RSI + 거래량
    short_score = 0
    short_score += 25 if r5 > 0 else 0
    short_score += 20 if r20 > 2 else 10 if r20 > 0 else 0
    short_score += 20 if close > float(r["MA20"]) else 0
    short_score += 15 if float(r["MA20"]) > ma60 else 0
    short_score += 10 if 50 <= rsi <= 68 else 5 if 45 <= rsi <= 72 else 0
    short_score += 10 if vr >= 1.05 else 5 if vr >= 0.9 else 0

    if short_score >= 75:
        short_state = "🔥 단기 강세"
    elif short_score >= 60:
        short_state = "🟢 보유/운용"
    elif short_score >= 45:
        short_state = "🟡 매수 대기"
    else:
        short_state = "⚪ 단기 관찰"

    if long_score >= 80 and short_score >= 75:
        final_state = "🟢 장기 핵심보유 + 적극 운용"
    elif long_score >= 65 and short_score >= 60:
        final_state = "🟢 장기 보유 + 운용"
    elif long_score >= 65:
        final_state = "🟢 장기 보유 + 신규매수 대기"
    elif long_score < 50 and short_score < 50:
        final_state = "🔴 장기 재검토 + 단기 관찰"
    else:
        final_state = "🟡 혼합/추세 확인"

    entry_i = i + 1
    entry_price = float(d.iloc[entry_i]["Close"])
    out = {
        "신호일": d.index[i].date(),
        "진입일": d.index[entry_i].date(),
        "장기점수": long_score,
        "장기판정": long_state,
        "단기점수": short_score,
        "단기판정": short_state,
        "최종판정": final_state,
        "진입가": entry_price,
    }
    for h in [20, 60, 120, 250]:
        exit_price = float(d.iloc[entry_i + h - 1]["Close"])
        out[f"{h}일후수익률"] = (exit_price / entry_price - 1) * 100
    return out

def bt_run_horizon_backtest(start, end, tickers, step_days=5):
    download_start = (pd.Timestamp(start) - pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    download_end = (pd.Timestamp(end) + pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    raw = bt_download_prices(tickers, download_start, download_end)
    data = {k: bt_indicators(v) for k, v in raw.items()}
    rows = []
    for ticker in tickers:
        d = data.get(ticker)
        if d is None or len(d) < 451:
            continue
        dates = d.index[(d.index >= pd.Timestamp(start)) & (d.index <= pd.Timestamp(end))]
        for dt in dates[::max(1, int(step_days))]:
            i = d.index.get_loc(dt)
            rec = bt_horizon_judgment_backtest_row(d, i)
            if rec is not None:
                rec["ETF"] = ticker
                rec["종목명"] = BT_POOL.get(ticker, ticker)
                rows.append(rec)
    return pd.DataFrame(rows), data

def bt_summarize_horizon_backtest(df):
    if df is None or df.empty:
        return pd.DataFrame()
    rows = []
    for state_col in ["장기판정", "단기판정", "최종판정"]:
        for state, g in df.groupby(state_col):
            rows.append({
                "구분": state_col,
                "판정": state,
                "건수": len(g),
                "20일 평균": g["20일후수익률"].mean(),
                "60일 평균": g["60일후수익률"].mean(),
                "120일 평균": g["120일후수익률"].mean(),
                "250일 평균": g["250일후수익률"].mean(),
                "20일 승률": (g["20일후수익률"] > 0).mean() * 100,
                "120일 승률": (g["120일후수익률"] > 0).mean() * 100,
                "250일 승률": (g["250일후수익률"] > 0).mean() * 100,
            })
    return pd.DataFrame(rows)

def bt_horizon_judgment_v2(d, i):
    """시점 i 이전 데이터만 사용.
    V1의 문제였던 '일시적 조정 = 장기 재검토'를 줄이고,
    장기 재검토는 구조적 추세 훼손이 확인될 때만 발생하도록 설계한다.
    """
    if i < 252 or i + 250 >= len(d):
        return None
    r=d.iloc[i]
    close=float(r["Close"]); ma60=float(r["MA60"]); ma120=float(r["MA120"]); ma200=float(r["MA200"])
    ma200_60=float(d.iloc[i-60]["MA200"]); ma120_20=float(d.iloc[i-20]["MA120"])
    r60=float(r["R60"]); r120=float(r["R120"])
    high252=float(r["HIGH252"]) if np.isfinite(r["HIGH252"]) else close
    dd252=(close/high252-1)*100 if high252>0 else 0

    # 장기 적합도: 한 번의 조정으로 급락하지 않도록 '구조'에 더 높은 가중치
    score=0
    score += 30 if close > ma200 else 0
    score += 20 if ma120 > ma200 else 0
    score += 15 if ma60 > ma120 else 0
    score += 15 if ma200 > ma200_60 else 0
    score += 10 if ma120 > ma120_20 else 0
    score += 5 if r120 > 0 else 0
    score += 5 if dd252 > -20 else 0

    # 구조적 훼손: 단순 조정이 아니라 여러 조건이 동시에 무너진 경우만 재검토
    structural_break = (
        close < ma200 and
        ma120 < ma200 and
        ma200 <= ma200_60 and
        r120 < 0
    )

    # 20거래일 이상 MA200 아래에 있었는지도 확인
    below20 = int((d["Close"].iloc[i-19:i+1] < d["MA200"].iloc[i-19:i+1]).sum()) >= 15
    structural_break = structural_break and below20

    if structural_break:
        long_state="🔴 장기 재검토"
    elif score >= 80:
        long_state="🟢 장기 핵심보유"
    elif score >= 65:
        long_state="🟢 장기 보유"
    else:
        long_state="🟡 추세 확인"

    # 단기 운용은 기존 V1과 동일한 구조를 유지
    r20=float(r["R20"]); r5=float(r["R5"]); rsi=float(r["RSI"])
    vr=float(r["VR"]) if np.isfinite(r["VR"]) else 1.0
    short_score=0
    short_score += 25 if r5 > 0 else 0
    short_score += 20 if r20 > 2 else 10 if r20 > 0 else 0
    short_score += 20 if close > float(r["MA20"]) else 0
    short_score += 15 if float(r["MA20"]) > ma60 else 0
    short_score += 10 if 50 <= rsi <= 68 else 5 if 45 <= rsi <= 72 else 0
    short_score += 10 if vr >= 1.05 else 5 if vr >= 0.9 else 0
    if short_score >= 75: short_state="🔥 단기 강세"
    elif short_score >= 60: short_state="🟢 보유/운용"
    elif short_score >= 45: short_state="🟡 매수 대기"
    else: short_state="⚪ 단기 관찰"

    if long_state == "🔴 장기 재검토":
        final_state="🔴 장기 재검토"
    elif long_state == "🟢 장기 핵심보유" and short_state == "🔥 단기 강세":
        final_state="🟢 장기 핵심보유 + 적극 운용"
    elif long_state in ("🟢 장기 핵심보유","🟢 장기 보유"):
        final_state="🟢 장기 보유 + 현재 추세 확인"
    else:
        final_state="🟡 장기 보유 가능 + 추세 확인"

    entry_i=i+1; entry_price=float(d.iloc[entry_i]["Close"])
    out={"신호일":d.index[i].date(),"진입일":d.index[entry_i].date(),
         "장기점수V2":score,"장기판정V2":long_state,"단기점수":short_score,
         "단기판정":short_state,"최종판정V2":final_state,"진입가":entry_price,
         "구조적훼손":structural_break,"252일고점대비":dd252}
    for h in [20,60,120,250]:
        ep=float(d.iloc[entry_i+h-1]["Close"])
        out[f"{h}일후수익률"]=(ep/entry_price-1)*100
    return out

def bt_run_horizon_backtest_v2(start,end,tickers,step_days=5):
    download_start=(pd.Timestamp(start)-pd.Timedelta(days=520)).strftime("%Y-%m-%d")
    download_end=(pd.Timestamp(end)+pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    raw=bt_download_prices(tickers,download_start,download_end)
    data={k:bt_indicators(v) for k,v in raw.items()}
    rows=[]
    for ticker in tickers:
        d=data.get(ticker)
        if d is None or len(d)<520: continue
        dates=d.index[(d.index>=pd.Timestamp(start))&(d.index<=pd.Timestamp(end))]
        for dt in dates[::max(1,int(step_days))]:
            i=d.index.get_loc(dt); rec=bt_horizon_judgment_v2(d,i)
            if rec is not None:
                rec["ETF"]=ticker; rec["종목명"]=BT_POOL.get(ticker,ticker); rows.append(rec)
    return pd.DataFrame(rows),data

def bt_summarize_horizon_v2(df):
    if df is None or df.empty: return pd.DataFrame()
    rows=[]
    for col in ["장기판정V2","단기판정","최종판정V2"]:
        for state,g in df.groupby(col):
            rows.append({"구분":col,"판정":state,"건수":len(g),
                "20일 평균":g["20일후수익률"].mean(),"60일 평균":g["60일후수익률"].mean(),
                "120일 평균":g["120일후수익률"].mean(),"250일 평균":g["250일후수익률"].mean(),
                "20일 승률":(g["20일후수익률"]>0).mean()*100,
                "120일 승률":(g["120일후수익률"]>0).mean()*100,
                "250일 승률":(g["250일후수익률"]>0).mean()*100})
    return pd.DataFrame(rows)

def bt_horizon_judgment_v3(d, i):
    """시점 i 이전 데이터만 사용.

    V3 원칙
    1) 장기적합성: 일시적 조정 때문에 장기보유 ETF를 탈락시키지 않는다.
    2) 장기추세: 현재 가격이 MA200 아래인지보다 장기 추세의 방향을 우선한다.
    3) 구조적훼손: 장기수익률/MA200/MA120이 동시에 약해질 때만 경고한다.
    4) 현재운용: 단기 점수는 장기적합성과 별도로 판단한다.
    """
    if i < 252 or i + 250 >= len(d):
        return None
    r=d.iloc[i]
    close=float(r["Close"])
    ma20=float(r["MA20"]); ma60=float(r["MA60"])
    ma120=float(r["MA120"]); ma200=float(r["MA200"])
    ma200_60=float(d.iloc[i-60]["MA200"])
    ma120_60=float(d.iloc[i-60]["MA120"])
    r60=float(r["R60"]); r120=float(r["R120"]); r252=float(r["R252"])
    high252=float(r["HIGH252"]) if np.isfinite(r["HIGH252"]) else close
    dd252=(close/high252-1)*100 if high252>0 else 0

    # --------------------------------------------------------
    # A. 장기적합성
    # 핵심은 '현재 가격 위치'보다 장기 추세의 지속성.
    # --------------------------------------------------------
    suitability=0
    suitability += 25 if r252 > 15 else 18 if r252 > 0 else 8 if r252 > -15 else 0
    suitability += 20 if ma200 > ma200_60 else 0
    suitability += 15 if ma120 > ma120_60 else 0
    suitability += 15 if r120 > 10 else 10 if r120 > 0 else 4 if r120 > -10 else 0
    suitability += 15 if ma120 > ma200 else 7 if ma120 >= ma200*0.98 else 0
    suitability += 10 if r60 > 0 else 4 if r60 > -8 else 0

    # 장기적합성은 일시적 가격조정만으로 핵심보유를 박탈하지 않음.
    if suitability >= 75:
        fit_state="🟢 장기 핵심보유"
    elif suitability >= 55:
        fit_state="🟢 장기 보유"
    elif suitability >= 40:
        fit_state="🟡 장기 보유 + 추세 확인"
    else:
        fit_state="🔴 장기 적합성 재검토"

    # --------------------------------------------------------
    # B. 장기추세 상태
    # --------------------------------------------------------
    trend_score=0
    trend_score += 30 if ma200 > ma200_60 else 0
    trend_score += 25 if ma120 > ma120_60 else 0
    trend_score += 20 if ma120 > ma200 else 0
    trend_score += 15 if r120 > 0 else 0
    trend_score += 10 if close > ma200 else 0
    if trend_score >= 75:
        trend_state="🟢 장기 상승추세"
    elif trend_score >= 50:
        trend_state="🟡 장기 추세 확인"
    else:
        trend_state="🔴 장기 하락추세"

    # --------------------------------------------------------
    # C. 구조적 훼손
    # 단순 MA200 하회는 훼손으로 보지 않는다.
    # 장기수익률 음수 + MA200 하락 + MA120 하락 + MA120<MA200
    # 네 조건이 동시에 확인될 때만 장기 경고.
    # --------------------------------------------------------
    below20=int((d["Close"].iloc[i-19:i+1] < d["MA200"].iloc[i-19:i+1]).sum()) >= 15
    structural_break=(
        r252 < 0 and r120 < 0 and
        ma200 <= ma200_60 and ma120 <= ma120_60 and
        ma120 < ma200 and close < ma200 and below20
    )

    # --------------------------------------------------------
    # D. 현재 운용 — V2의 단기 구조 유지
    # --------------------------------------------------------
    r20=float(r["R20"]); r5=float(r["R5"]); rsi=float(r["RSI"])
    vr=float(r["VR"]) if np.isfinite(r["VR"]) else 1.0
    short_score=0
    short_score += 25 if r5 > 0 else 0
    short_score += 20 if r20 > 2 else 10 if r20 > 0 else 0
    short_score += 20 if close > ma20 else 0
    short_score += 15 if ma20 > ma60 else 0
    short_score += 10 if 50 <= rsi <= 68 else 5 if 45 <= rsi <= 72 else 0
    short_score += 10 if vr >= 1.05 else 5 if vr >= 0.9 else 0
    if short_score >= 75: short_state="🔥 단기 강세"
    elif short_score >= 60: short_state="🟢 보유/운용"
    elif short_score >= 45: short_state="🟡 매수 대기"
    else: short_state="⚪ 단기 관찰"

    # --------------------------------------------------------
    # E. 최종 행동
    # 장기적합성/장기추세/현재운용을 섞지 않고 순서대로 표시.
    # --------------------------------------------------------
    if structural_break:
        action="🔴 장기 추세 훼손 · 신규매수 중단"
    elif fit_state == "🟢 장기 핵심보유" and short_state == "🔥 단기 강세":
        action="🟢 핵심보유 + 적극 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유") and short_state in ("🟢 보유/운용","🔥 단기 강세"):
        action="🟢 장기보유 + 현재 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유"):
        action="🟡 장기보유 유지 + 신규매수 대기"
    else:
        action="🟡 추세 확인 후 운용"

    entry_i=i+1
    entry_price=float(d.iloc[entry_i]["Close"])
    out={
        "신호일":d.index[i].date(),"진입일":d.index[entry_i].date(),
        "장기적합성점수V3":suitability,"장기적합성V3":fit_state,
        "장기추세점수V3":trend_score,"장기추세V3":trend_state,
        "단기점수V3":short_score,"단기운용V3":short_state,
        "최종행동V3":action,"진입가":entry_price,
        "구조적훼손V3":structural_break,"252일고점대비":dd252,
    }
    for h in [20,60,120,250]:
        ep=float(d.iloc[entry_i+h-1]["Close"])
        out[f"{h}일후수익률"]=(ep/entry_price-1)*100
    return out

def bt_run_horizon_backtest_v3(start,end,tickers,step_days=5):
    download_start=(pd.Timestamp(start)-pd.Timedelta(days=520)).strftime("%Y-%m-%d")
    download_end=(pd.Timestamp(end)+pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    raw=bt_download_prices(tickers,download_start,download_end)
    data={k:bt_indicators(v) for k,v in raw.items()}
    rows=[]
    for ticker in tickers:
        d=data.get(ticker)
        if d is None or len(d)<520: continue
        dates=d.index[(d.index>=pd.Timestamp(start))&(d.index<=pd.Timestamp(end))]
        for dt in dates[::max(1,int(step_days))]:
            i=d.index.get_loc(dt)
            rec=bt_horizon_judgment_v3(d,i)
            if rec is not None:
                rec["ETF"]=ticker; rec["종목명"]=BT_POOL.get(ticker,ticker); rows.append(rec)
    return pd.DataFrame(rows),data

def bt_summarize_horizon_v3(df):
    if df is None or df.empty: return pd.DataFrame()
    rows=[]
    for col in ["장기적합성V3","장기추세V3","단기운용V3","최종행동V3"]:
        for state,g in df.groupby(col):
            rows.append({"구분":col,"판정":state,"건수":len(g),
                "20일 평균":g["20일후수익률"].mean(),"60일 평균":g["60일후수익률"].mean(),
                "120일 평균":g["120일후수익률"].mean(),"250일 평균":g["250일후수익률"].mean(),
                "20일 승률":(g["20일후수익률"]>0).mean()*100,
                "120일 승률":(g["120일후수익률"]>0).mean()*100,
                "250일 승률":(g["250일후수익률"]>0).mean()*100})
    return pd.DataFrame(rows)

def bt_horizon_judgment_v4(d, i):
    """시점 i 이전 데이터만 사용.

    V4 원칙
    - 장기적합성은 미래수익률을 예측하는 점수가 아니라 '계속 보유할 만한 구조인가'를 판단.
    - 단기 조정/고점 대비 하락만으로 장기 핵심보유를 박탈하지 않음.
    - 장기적합성에는 최근 1년 동안 장기추세가 유지된 '지속성'을 가장 크게 반영.
    - 현재 추세와 단기운용은 별도 축으로 판단.
    - 구조적 훼손만 실제 신규매수 중단 사유로 사용.
    """
    if i < 300 or i + 250 >= len(d): return None
    r=d.iloc[i]
    close=float(r["Close"]); ma20=float(r["MA20"]); ma60=float(r["MA60"])
    ma120=float(r["MA120"]); ma200=float(r["MA200"])
    ma200_60=float(d.iloc[i-60]["MA200"]); ma120_60=float(d.iloc[i-60]["MA120"])
    r20=float(r["R20"]); r60=float(r["R60"]); r120=float(r["R120"]); r252=float(r["R252"])
    high252=float(r["HIGH252"]) if np.isfinite(r["HIGH252"]) else close
    dd252=(close/high252-1)*100 if high252>0 else 0

    # ① 장기 지속성: 최근 252일 중 장기추세 위에서 머문 비율
    w=d.iloc[i-251:i+1]
    above200=float((w["Close"] >= w["MA200"]).mean())*100
    above120=float((w["Close"] >= w["MA120"]).mean())*100
    ma200_up=ma200 > ma200_60
    ma120_up=ma120 > ma120_60

    # ② 장기적합성: 현재 가격의 단기 위치보다 추세 지속성을 우선
    suitability=(
        above200*0.40
        + above120*0.20
        + (25 if ma200_up else 0)
        + (15 if r252>0 else 7 if r252>-15 else 0)
    )
    suitability=float(np.clip(suitability,0,100))

    if suitability >= 78:
        fit_state="🟢 장기 핵심보유"
    elif suitability >= 62:
        fit_state="🟢 장기 보유"
    elif suitability >= 48:
        fit_state="🟡 장기 보유 + 추세 확인"
    else:
        fit_state="🔴 장기 적합성 재검토"

    # ③ 장기추세: 현재 위치를 포함해 '지금의 추세'를 별도 판단
    trend_score=0
    trend_score += 30 if ma200_up else 0
    trend_score += 25 if ma120_up else 0
    trend_score += 20 if ma120 > ma200 else 0
    trend_score += 15 if r120 > 0 else 0
    trend_score += 10 if close > ma200 else 0
    if trend_score >= 75: trend_state="🟢 장기 상승추세"
    elif trend_score >= 50: trend_state="🟡 장기 조정/추세 확인"
    else: trend_state="🔴 장기 하락추세"

    # ④ 구조적 훼손: 지속성 자체가 무너졌을 때만
    structural_break=(
        above200 < 45 and above120 < 50 and
        r252 < 0 and r120 < 0 and
        not ma200_up and not ma120_up and
        ma120 < ma200 and close < ma200
    )

    # ⑤ 현재 운용 — 기존 단기 구조 유지
    rsi=float(r["RSI"]); vr=float(r["VR"]) if np.isfinite(r["VR"]) else 1.0
    short_score=0
    short_score += 25 if float(r["R5"]) > 0 else 0
    short_score += 20 if r20 > 2 else 10 if r20 > 0 else 0
    short_score += 20 if close > ma20 else 0
    short_score += 15 if ma20 > ma60 else 0
    short_score += 10 if 50 <= rsi <= 68 else 5 if 45 <= rsi <= 72 else 0
    short_score += 10 if vr >= 1.05 else 5 if vr >= 0.9 else 0
    if short_score >= 75: short_state="🔥 단기 강세"
    elif short_score >= 60: short_state="🟢 보유/운용"
    elif short_score >= 45: short_state="🟡 매수 대기"
    else: short_state="⚪ 단기 관찰"

    # ⑥ 최종 행동: 장기 보유 판단과 매매 타이밍을 분리
    if structural_break:
        action="🔴 구조적 추세 훼손 · 신규매수 중단"
    elif fit_state == "🟢 장기 핵심보유" and short_state == "🔥 단기 강세":
        action="🟢 핵심보유 + 적극 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유") and short_state in ("🟢 보유/운용","🔥 단기 강세"):
        action="🟢 장기보유 + 현재 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유"):
        action="🟡 장기보유 유지 + 신규매수 대기"
    elif trend_state == "🟡 장기 조정/추세 확인":
        action="🟡 장기 추세 확인 후 운용"
    else:
        action="⚪ 관찰"

    entry_i=i+1; entry_price=float(d.iloc[entry_i]["Close"])
    out={
        "신호일":d.index[i].date(),"진입일":d.index[entry_i].date(),
        "장기적합성점수V4":round(suitability,1),"장기적합성V4":fit_state,
        "장기추세점수V4":trend_score,"장기추세V4":trend_state,
        "단기점수V4":short_score,"단기운용V4":short_state,
        "장기추세지속성V4":round(above200,1),"구조적훼손V4":structural_break,
        "최종행동V4":action,"진입가":entry_price,"252일고점대비":dd252,
    }
    for h in [20,60,120,250]:
        ep=float(d.iloc[entry_i+h-1]["Close"]); out[f"{h}일후수익률"]=(ep/entry_price-1)*100
    return out

def bt_run_horizon_backtest_v4(start,end,tickers,step_days=5):
    download_start=(pd.Timestamp(start)-pd.Timedelta(days=560)).strftime("%Y-%m-%d")
    download_end=(pd.Timestamp(end)+pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    raw=bt_download_prices(tickers,download_start,download_end)
    data={k:bt_indicators(v) for k,v in raw.items()}
    rows=[]
    for ticker in tickers:
        d=data.get(ticker)
        if d is None or len(d)<560: continue
        dates=d.index[(d.index>=pd.Timestamp(start))&(d.index<=pd.Timestamp(end))]
        for dt in dates[::max(1,int(step_days))]:
            i=d.index.get_loc(dt); rec=bt_horizon_judgment_v4(d,i)
            if rec is not None:
                rec["ETF"]=ticker; rec["종목명"]=BT_POOL.get(ticker,ticker); rows.append(rec)
    return pd.DataFrame(rows),data

def bt_summarize_horizon_v4(df):
    if df is None or df.empty: return pd.DataFrame()
    rows=[]
    for col in ["장기적합성V4","장기추세V4","단기운용V4","최종행동V4"]:
        for state,g in df.groupby(col):
            rows.append({"구분":col,"판정":state,"건수":len(g),
                "20일 평균":g["20일후수익률"].mean(),"60일 평균":g["60일후수익률"].mean(),
                "120일 평균":g["120일후수익률"].mean(),"250일 평균":g["250일후수익률"].mean(),
                "20일 승률":(g["20일후수익률"]>0).mean()*100,
                "120일 승률":(g["120일후수익률"]>0).mean()*100,
                "250일 승률":(g["250일후수익률"]>0).mean()*100})
    return pd.DataFrame(rows)

def bt_trade_levels_v6(d, signal_i, entry_price):
    """신호일의 정보만 사용해 다음 거래일 진입 기준을 계산한다."""
    r = d.iloc[signal_i]
    c = float(r["Close"])
    ma20 = float(r["MA20"])
    ma60 = float(r["MA60"])
    low20 = float(r["LOW20"])
    support = max(low20, ma20 * 0.985)
    stop1 = min(ma60 * 0.97, support * 0.97)
    stop2 = min(stop1, low20 * 0.98)
    if not np.isfinite(stop1) or stop1 <= 0:
        stop1 = entry_price * 0.95
    if not np.isfinite(stop2) or stop2 <= 0:
        stop2 = stop1
    risk = max(entry_price - stop1, entry_price * 0.02)
    tp1 = entry_price + risk
    tp2 = entry_price + risk * 2.0
    return {"entry": entry_price, "support": support, "stop1": stop1,
            "stop2": stop2, "risk": risk, "tp1": tp1, "tp2": tp2,
            "signal_close": c}

def bt_simulate_cd_trade_v7(r, data, initial_cash=1_000_000,
                         fee_per_side=0.0010, slippage_per_side=0.0005,
                         max_hold_days=250):
    """V7 실전형 C/D 체결 시뮬레이션.

    C/D 선정 로직은 변경하지 않고 청산 구조만 개선한다.
    1) D 신호 다음 거래일 시가 진입.
    2) 1R에서 50% 익절.
    3) 2R에서 남은 물량의 50%(전체의 25%) 익절.
    4) 2R 도달 이후 남은 25%는 20일선 추적손절.
    5) 1차 손절은 보유물량의 50%, 2차 손절은 잔여물량 전량.
    6) 같은 봉에서 손절과 익절이 충돌하면 보수적으로 손절 우선.
    7) 최대 보유기간 종료 시 잔여물량 종가 청산.
    8) 보유 중 새 D 신호는 무시.
    """
    if r is None or r.empty:
        return pd.DataFrame(), {"거래수": 0}

    signals = r.loc[r["D_미래테마선행가격"] == True].copy()
    if signals.empty:
        return pd.DataFrame(), {"거래수": 0}
    signals["날짜"] = pd.to_datetime(signals["날짜"])
    signals = signals.sort_values("날짜").reset_index(drop=True)

    cash = float(initial_cash)
    trades = []
    next_available = pd.Timestamp.min

    def px(v, fallback):
        try:
            v = float(v)
            return v if np.isfinite(v) and v > 0 else fallback
        except Exception:
            return fallback

    for _, sig in signals.iterrows():
        signal_date = pd.Timestamp(sig["날짜"])
        if signal_date < next_available:
            continue

        ticker = sig["ETF"]
        d = data.get(ticker)
        if d is None or d.empty:
            continue

        idx = d.index.searchsorted(signal_date)
        if idx >= len(d) or d.index[idx] != signal_date:
            continue
        entry_i = idx + 1
        if entry_i >= len(d):
            continue

        entry_row = d.iloc[entry_i]
        raw_entry = px(entry_row.get("Open", np.nan),
                       px(entry_row.get("Close", np.nan), np.nan))
        if not np.isfinite(raw_entry) or raw_entry <= 0:
            continue

        entry_fill = raw_entry * (1 + slippage_per_side)
        lv = bt_trade_levels_v6(d, idx, entry_fill)
        stop1 = float(lv["stop1"])
        stop2 = float(lv["stop2"])
        tp1 = float(lv["tp1"])
        tp2 = float(lv["tp2"])

        # 전체 포지션을 1.0으로 두고 부분청산한다.
        remaining = 1.0
        realized = 0.0
        tp1_hit = False
        tp2_hit = False
        stop1_hit = False
        stop2_hit = False
        trail_hit = False
        trail_active = False
        exit_reason = ""

        last_i = min(len(d) - 1, entry_i + int(max_hold_days) - 1)
        exit_i = last_i

        def net_return(fill, weight):
            # entry_fill은 진입 슬리피지를 이미 반영.
            # 각 부분청산에는 청산 슬리피지와 양쪽 비용을 보수적으로 반영.
            return weight * ((fill / entry_fill - 1) - fee_per_side * 2)

        for j in range(entry_i, last_i + 1):
            bar = d.iloc[j]
            close_j = px(bar.get("Close", np.nan), np.nan)
            high_j = px(bar.get("High", np.nan), close_j)
            low_j = px(bar.get("Low", np.nan), close_j)
            ma20_j = px(bar.get("MA20", np.nan), np.nan)
            if not np.isfinite(close_j):
                continue

            # ① 2R 이후에는 구조적 손절보다 20일선 추적손절을 우선 적용한다.
            #    2R 이후 남은 25%는 별도의 runner로 취급한다.
            #    같은 봉에서 추적손절과 다른 손절이 함께 닿으면 더 높은 가격의
            #    추적손절이 먼저 체결되는 것으로 처리한다.
            if trail_active and remaining > 0 and np.isfinite(ma20_j) and ma20_j > 0:
                trail_stop = ma20_j * 0.99
                if low_j <= trail_stop:
                    fill = trail_stop * (1 - slippage_per_side)
                    realized += net_return(fill, remaining)
                    trail_hit = True
                    exit_reason = "20일선 추적손절"
                    remaining = 0.0
                    exit_i = j
                    break

            # ② 추적손절이 활성화되기 전에는 구조적 손절을 적용한다.
            if (not trail_active) and remaining > 0 and low_j <= stop2:
                fill = stop2 * (1 - slippage_per_side)
                realized += net_return(fill, remaining)
                stop2_hit = True
                exit_reason = "2차 손절"
                remaining = 0.0
                exit_i = j
                break

            if (not trail_active) and remaining > 0 and (not stop1_hit) and low_j <= stop1:
                fill = stop1 * (1 - slippage_per_side)
                cut = min(0.5, remaining)
                realized += net_return(fill, cut)
                remaining -= cut
                stop1_hit = True
                # 같은 봉의 TP는 인정하지 않는다.
                if j == last_i and remaining > 0:
                    fill = close_j * (1 - slippage_per_side)
                    realized += net_return(fill, remaining)
                    remaining = 0.0
                    exit_reason = "1차 손절·기간만료"
                    exit_i = j
                    break
                continue

            # ③ 1R: 최초 물량의 절반 익절.
            #    같은 봉에서 2R까지 도달해도 실제 가격 경로상 1R이 먼저 체결된다.
            if remaining > 0 and (not tp1_hit) and high_j >= tp1:
                fill = tp1 * (1 - slippage_per_side)
                cut = min(0.5, remaining)
                realized += net_return(fill, cut)
                remaining -= cut
                tp1_hit = True

            # ④ 2R: 남은 물량의 절반(초기 포지션 기준 25%)만 익절.
            #    2R 이후 잔여 25%는 다음 봉부터 20일선 추적손절을 적용한다.
            if remaining > 0 and tp1_hit and (not tp2_hit) and high_j >= tp2:
                fill = tp2 * (1 - slippage_per_side)
                cut = min(0.25, remaining)
                realized += net_return(fill, cut)
                remaining -= cut
                tp2_hit = True
                trail_active = remaining > 0
                # 같은 봉의 추적손절은 장중 순서를 알 수 없으므로 다음 봉부터 적용.
                continue

            if remaining <= 0:
                exit_reason = "2R 익절" if tp2_hit else "1R 익절"
                exit_i = j
                break

            # ⑤ 최대 보유기간 종료.
            if j == last_i and remaining > 0:
                fill = close_j * (1 - slippage_per_side)
                realized += net_return(fill, remaining)
                remaining = 0.0
                if trail_active:
                    exit_reason = "추적손절·기간만료"
                elif tp2_hit:
                    exit_reason = "2R 후 기간만료"
                elif tp1_hit:
                    exit_reason = "1R 후 기간만료"
                else:
                    exit_reason = "기간만료"
                exit_i = j
                break

        cash *= (1 + realized)
        exit_date = d.index[exit_i]
        next_available = exit_date + pd.Timedelta(days=1)

        trades.append({
            "신호일": signal_date.date(),
            "진입일": d.index[entry_i].date(),
            "청산일": exit_date.date(),
            "ETF": ticker,
            "테마": sig["테마"],
            "테마점수": float(sig["테마점수"]),
            "선행점수": int(sig["선행점수"]),
            "진입가": entry_fill,
            "1차익절": tp1,
            "2차익절": tp2,
            "1차손절": stop1,
            "2차손절": stop2,
            "R": lv["risk"],
            "1R도달": tp1_hit,
            "2R도달": tp2_hit,
            "1차손절도달": stop1_hit,
            "2차손절도달": stop2_hit,
            "20일선추적손절": trail_hit,
            "청산사유": exit_reason,
            "보유거래일": int(exit_i - entry_i + 1),
            "순수익률": realized * 100,
            "거래후자산": cash,
        })

    td = pd.DataFrame(trades)
    if td.empty:
        return td, {
            "초기자산": initial_cash, "최종자산": initial_cash,
            "총수익률": 0.0, "거래수": 0, "승률": np.nan,
            "최대낙폭": 0.0, "연환산": np.nan,
        }

    curve = td[["청산일", "거래후자산"]].copy()
    curve["청산일"] = pd.to_datetime(curve["청산일"])
    curve["고점"] = curve["거래후자산"].cummax()
    curve["낙폭"] = (curve["거래후자산"] / curve["고점"] - 1) * 100

    final_cash = float(td.iloc[-1]["거래후자산"])
    total_ret = (final_cash / initial_cash - 1) * 100
    days = max(1, (curve["청산일"].iloc[-1] - curve["청산일"].iloc[0]).days)
    annualized = ((final_cash / initial_cash) ** (365.25 / days) - 1) * 100 if final_cash > 0 else -100

    wins = int((td["순수익률"] > 0).sum())
    avg_win = td.loc[td["순수익률"] > 0, "순수익률"].mean()
    avg_loss = td.loc[td["순수익률"] <= 0, "순수익률"].mean()
    gross_profit = td.loc[td["순수익률"] > 0, "순수익률"].sum()
    gross_loss = -td.loc[td["순수익률"] < 0, "순수익률"].sum()

    metrics = {
        "초기자산": initial_cash,
        "최종자산": final_cash,
        "총수익률": total_ret,
        "연환산": annualized,
        "거래수": len(td),
        "승률": wins / len(td) * 100,
        "평균승리": avg_win,
        "평균손실": avg_loss,
        "손익비": (abs(avg_win / avg_loss) if pd.notna(avg_win) and pd.notna(avg_loss) and avg_loss != 0 else np.nan),
        "ProfitFactor": (gross_profit / gross_loss if gross_loss > 0 else np.inf),
        "기대값": td["순수익률"].mean(),
        "최대낙폭": float(curve["낙폭"].min()),
        "1R도달률": td["1R도달"].mean() * 100,
        "2R도달률": td["2R도달"].mean() * 100,
        "1차손절률": td["1차손절도달"].mean() * 100,
        "2차손절률": td["2차손절도달"].mean() * 100,
        "추적손절률": td["20일선추적손절"].mean() * 100,
        "평균보유일": td["보유거래일"].mean(),
    }
    return td, metrics

def bt_market_filter_pass(signal_date, spy, mode):
    if spy is None or spy.empty:
        return False
    try:
        dt = pd.Timestamp(signal_date)
        idx = spy.index.searchsorted(dt)
        if idx >= len(spy) or spy.index[idx] != dt:
            return False
        r = spy.iloc[idx]
        close = float(r.get("Close", np.nan))
        ma60 = float(r.get("MA60", np.nan))
        ma120 = float(r.get("MA120", np.nan))
        ma200 = float(r.get("MA200", np.nan))
        r20 = float(r.get("R20", r.get("RET20", np.nan)))
        r60 = float(r.get("R60", r.get("RET60", np.nan)))
        if not all(np.isfinite(v) for v in [close, ma60, ma120, ma200, r20, r60]):
            return False
        if mode == "완화":
            return close >= ma120 and r20 >= -3.0
        if mode == "기본":
            return close >= ma60 and r20 >= 0.0
        if mode == "엄격":
            return close >= ma200 and r60 >= 0.0
        return True
    except Exception:
        return False

def bt_filtered_signal_rows(r, data, mode):
    if r is None or r.empty or mode == "기본 V7":
        return r.copy() if r is not None else pd.DataFrame()
    spy = data.get(BT_BENCH)
    if spy is None or spy.empty:
        return pd.DataFrame(columns=r.columns)
    x = r.copy()
    x["시장필터통과"] = x["날짜"].apply(lambda d: bt_market_filter_pass(d, spy, mode))
    return x[x["시장필터통과"] == True].copy()

def bt_run_market_filter_comparison(r, data, initial_cash=1_000_000, fee=0.001, slip=0.0005, hold=250):
    rows = []
    for mode in ["기본 V7", "완화", "기본", "엄격"]:
        rr = bt_filtered_signal_rows(r, data, mode)
        trades, m = bt_simulate_cd_trade_v7(rr, data, initial_cash=initial_cash,
                                         fee_per_side=fee, slippage_per_side=slip,
                                         max_hold_days=hold)
        rows.append({
            "시장필터": mode,
            "신호수": int((rr["D_미래테마선행가격"] == True).sum()) if not rr.empty and "D_미래테마선행가격" in rr else 0,
            "필터통과신호": int(len(rr)),
            "거래수": int(m.get("거래수", 0)),
            "최종자산": float(m.get("최종자산", initial_cash)),
            "총수익률": float(m.get("총수익률", 0)),
            "승률": float(m.get("승률", 0)),
            "MDD": float(m.get("최대낙폭", 0)),
            "평균손익": float(m.get("기대값", 0)),
            "2차손절률": float(m.get("2차손절률", 0)),
            "추적손절률": float(m.get("추적손절률", 0)),
        })
    return pd.DataFrame(rows)

def bt_strict_market_pass_with_condition(signal_date, row, data, condition):
    spy = data.get(BT_BENCH)
    if spy is None or spy.empty or row is None:
        return False
    try:
        dt = pd.Timestamp(signal_date)
        idx = spy.index.searchsorted(dt)
        if idx >= len(spy) or spy.index[idx] != dt:
            return False
        sr = spy.iloc[idx]
        if not all(np.isfinite(float(sr.get(k, np.nan))) for k in ["Close","MA200","R60"]):
            return False
        # 현재 채택 후보인 엄격 시장환경 필터는 고정한다.
        if float(sr["Close"]) < float(sr["MA200"]) or float(sr["R60"]) < 0:
            return False

        if condition == "A · 엄격 기준선":
            return True

        close = float(row.get("Close", np.nan))
        ma20 = float(row.get("MA20", np.nan))
        ma60 = float(row.get("MA60", np.nan))
        r5 = float(row.get("R5", np.nan))
        r20 = float(row.get("R20", np.nan))
        vr = float(row.get("VR", np.nan))
        rsi = float(row.get("RSI", np.nan))
        vals = [close, ma20, ma60, r5, r20, vr, rsi]
        if not all(np.isfinite(v) for v in vals):
            return False

        if condition == "B · 개별 ETF 추세확인":
            # 기존 C/D의 선행진입을 지나치게 훼손하지 않는 완화형 개별추세 확인.
            # 진입 직전 종가가 MA20/MA60 부근에 있고 중기수익률이 급락 상태가 아닌지만 확인한다.
            trend_ok = (
                close >= ma60 * 0.98
                and ma20 >= ma60 * 0.98
                and r20 >= -3.0
            )
            return bool(trend_ok)

        if condition == "C · 거래량/모멘텀 확인":
            # 거래량·RSI가 정상 범위이고 단기 급락 상태만 제외한다.
            flow_ok = 0.90 <= vr <= 2.20
            momentum_ok = 40 <= rsi <= 72 and r5 >= -5.0
            return bool(flow_ok and momentum_ok)

        return False
    except Exception:
        return False

def bt_run_3condition_comparison(r, data, initial_cash=1_000_000, fee=0.001, slip=0.0005, hold=250):
    rows = []
    trade_details = {}
    names = ["A · 엄격 기준선", "B · 개별 ETF 추세확인", "C · 거래량/모멘텀 확인"]

    for name in names:
        selected = []
        if r is not None and not r.empty:
            for _, rr in r.iterrows():
                if not bool(rr.get("D_미래테마선행가격", False)):
                    continue
                if bt_strict_market_pass_with_condition(rr.get("날짜"), rr, data, name):
                    selected.append(rr)
        rrdf = pd.DataFrame(selected, columns=r.columns if r is not None else [])
        trades, m = bt_simulate_cd_trade_v7(
            rrdf, data,
            initial_cash=initial_cash,
            fee_per_side=fee,
            slippage_per_side=slip,
            max_hold_days=hold,
        )
        if trades is None:
            trades = pd.DataFrame()
        td = trades.copy()
        if not td.empty:
            td.insert(0, "추가조건", name)
        trade_details[name] = td
        rows.append({
            "추가조건": name,
            "통과신호": len(rrdf),
            "거래수": int(m.get("거래수", 0)),
            "최종자산": float(m.get("최종자산", initial_cash)),
            "총수익률": float(m.get("총수익률", 0)),
            "승률": float(m.get("승률", 0)),
            "MDD": float(m.get("최대낙폭", 0)),
            "평균손익": float(m.get("기대값", 0)),
            "2차손절률": float(m.get("2차손절률", 0)),
            "추적손절률": float(m.get("추적손절률", 0)),
        })
    return pd.DataFrame(rows), trade_details


# ============================================================
# ETF RADAR 통합 백테스트 LAB
# 기존 실시간 ETF RADAR 로직은 유지하고, 백테스트 엔진만 별도 네임스페이스로 연결한다.
# ============================================================


# ============================================================
# 조건 기여도 비교 백테스트
# ============================================================

def bt_condition_contribution_flags(r, data):
    """동일한 D 기준에서 각 추가조건의 독립/복합 기여도를 계산한다.
    - BASE = 미래테마 + 선행점수 + 가격구간(D)
    - TREND = Close > MA20 > MA60 and R20 > 0
    - MOMVOL = VR 1.05~2.50 and RSI 50~72 and R5 > 0
    - MARKET = SPY Close >= MA60, Close >= MA120, R20 >= 0
    모든 조건은 신호일의 정보만 사용한다.
    """
    if r is None or r.empty:
        return pd.DataFrame()
    x=r.copy()
    if "D_미래테마선행가격" not in x.columns:
        return pd.DataFrame()

    trend=[]; momvol=[]; market=[]
    spy=data.get(BT_BENCH)
    if spy is not None and not spy.empty:
        spy=bt_indicators(spy.copy()) if "MA120" not in spy.columns else spy

    for _, row in x.iterrows():
        ticker=row.get("ETF")
        dt=pd.Timestamp(row.get("날짜"))
        d=data.get(ticker)
        tr=mv=False
        if d is not None and not d.empty:
            pos=d.index.searchsorted(dt)
            if pos < len(d) and d.index[pos] == dt:
                z=d.iloc[pos]
                close=float(z.get("Close",np.nan)); ma20=float(z.get("MA20",np.nan)); ma60=float(z.get("MA60",np.nan))
                r20=float(z.get("R20",np.nan)); r5=float(z.get("R5",np.nan)); rsi=float(z.get("RSI",np.nan))
                vr=float(z.get("VR",np.nan)) if np.isfinite(z.get("VR",np.nan)) else np.nan
                tr=bool(np.isfinite(close) and np.isfinite(ma20) and np.isfinite(ma60) and np.isfinite(r20) and close>ma20>ma60 and r20>0)
                mv=bool(np.isfinite(vr) and np.isfinite(rsi) and np.isfinite(r5) and 1.05<=vr<=2.50 and 50<=rsi<=72 and r5>0)
        mk=False
        if spy is not None and not spy.empty:
            pos=spy.index.searchsorted(dt)
            if pos < len(spy) and spy.index[pos] == dt:
                z=spy.iloc[pos]
                close=float(z.get("Close",np.nan)); ma60=float(z.get("MA60",np.nan)); ma120=float(z.get("MA120",np.nan)); r20=float(z.get("R20",np.nan))
                mk=bool(np.isfinite(close) and np.isfinite(ma60) and np.isfinite(ma120) and np.isfinite(r20) and close>=ma60 and close>=ma120 and r20>=0)
        trend.append(tr); momvol.append(mv); market.append(mk)

    x["조건_추세"]=trend
    x["조건_거래량모멘텀"]=momvol
    x["조건_시장환경"]=market
    base=x["D_미래테마선행가격"].fillna(False).astype(bool)
    x["BASE"]=base
    x["BASE_추세"]=base & x["조건_추세"]
    x["BASE_거래량모멘텀"]=base & x["조건_거래량모멘텀"]
    x["BASE_시장환경"]=base & x["조건_시장환경"]
    x["BASE_추세_거래량모멘텀"]=base & x["조건_추세"] & x["조건_거래량모멘텀"]
    x["BASE_추세_거래량모멘텀_시장환경"]=base & x["조건_추세"] & x["조건_거래량모멘텀"] & x["조건_시장환경"]
    return x


def bt_simulate_contribution_strategy(r, data, flag, initial_cash=1_000_000, hold_days=60,
                                      fee_per_side=0.0010, slippage_per_side=0.0005):
    """조건 기여도 비교 전용 동일 체결엔진.
    모든 전략에 동일하게 다음 거래일 시가 진입/고정 보유기간/비용을 적용한다.
    신호가 중복되면 보유 종료일까지 새 신호를 무시한다.
    """
    if r is None or r.empty or flag not in r.columns:
        return pd.DataFrame(), {"거래수":0,"총수익률":0.0,"CAGR":np.nan,"MDD":0.0,"승률":np.nan,"Profit Factor":np.nan}
    sigs=r.loc[r[flag].fillna(False).astype(bool)].copy()
    if sigs.empty:
        return pd.DataFrame(), {"거래수":0,"총수익률":0.0,"CAGR":np.nan,"MDD":0.0,"승률":np.nan,"Profit Factor":np.nan}
    sigs["날짜"]=pd.to_datetime(sigs["날짜"])
    sigs=sigs.sort_values("날짜").reset_index(drop=True)
    cash=float(initial_cash); peak=float(initial_cash); next_available=pd.Timestamp.min
    trades=[]; curve=[]
    for _,sig in sigs.iterrows():
        signal_date=pd.Timestamp(sig["날짜"])
        if signal_date < next_available: continue
        d=data.get(sig["ETF"])
        if d is None or d.empty: continue
        idx=d.index.searchsorted(signal_date)
        if idx>=len(d) or d.index[idx]!=signal_date: continue
        entry_i=idx+1; exit_i=entry_i+int(hold_days)-1
        if exit_i>=len(d): continue
        er=d.iloc[entry_i]; xr=d.iloc[exit_i]
        entry=float(er.get("Open",er.get("Close",np.nan))); exitp=float(xr.get("Close",np.nan))
        if not np.isfinite(entry) or not np.isfinite(exitp) or entry<=0: continue
        buy=entry*(1+slippage_per_side); sell=exitp*(1-slippage_per_side)
        net=(sell/buy-1)-fee_per_side*2
        before=cash; cash*=1+net; peak=max(peak,cash)
        curve.append({"날짜":d.index[exit_i],"자산":cash})
        trades.append({"신호일":signal_date.date(),"진입일":d.index[entry_i].date(),"청산일":d.index[exit_i].date(),"ETF":sig["ETF"],"순수익률":net*100,"거래후자산":cash})
        next_available=d.index[exit_i]+pd.Timedelta(days=1)
    td=pd.DataFrame(trades); cv=pd.DataFrame(curve)
    if cv.empty:
        return td,{"거래수":0,"총수익률":0.0,"CAGR":np.nan,"MDD":0.0,"승률":np.nan,"Profit Factor":np.nan}
    cv=cv.sort_values("날짜").drop_duplicates("날짜",keep="last")
    cv["고점"]=cv["자산"].cummax(); cv["낙폭"]=(cv["자산"]/cv["고점"]-1)*100
    final=float(cv.iloc[-1]["자산"]); total=(final/initial_cash-1)*100
    days=max(1,(pd.Timestamp(cv.iloc[-1]["날짜"])-pd.Timestamp(cv.iloc[0]["날짜"])).days)
    cagr=((final/initial_cash)**(365.25/days)-1)*100 if final>0 else -100
    wins=int((td["순수익률"]>0).sum()); losses=td.loc[td["순수익률"]<0,"순수익률"]
    gains=float(td.loc[td["순수익률"]>0,"순수익률"].sum()); loss_abs=float(abs(losses.sum()))
    pf=(gains/loss_abs) if loss_abs>0 else np.inf if gains>0 else np.nan
    return td,{"거래수":len(td),"총수익률":total,"CAGR":cagr,"MDD":float(cv["낙폭"].min()),"승률":wins/len(td)*100 if len(td) else np.nan,"Profit Factor":pf,"평균거래수익":float(td["순수익률"].mean()) if not td.empty else np.nan}


def bt_annual_contribution(trades):
    if trades is None or trades.empty: return pd.DataFrame()
    t=trades.copy(); t["청산일"]=pd.to_datetime(t["청산일"]); t["연도"]=t["청산일"].dt.year
    rows=[]
    for y,g in t.groupby("연도"):
        wins=(g["순수익률"]>0).sum(); losses=g.loc[g["순수익률"]<0,"순수익률"]
        gain=g.loc[g["순수익률"]>0,"순수익률"].sum(); loss=abs(losses.sum())
        rows.append({"연도":int(y),"거래수":len(g),"승률":wins/len(g)*100 if len(g) else np.nan,"평균거래수익":g["순수익률"].mean(),"누적거래수익률":g["순수익률"].sum(),"Profit Factor":gain/loss if loss>0 else np.inf if gain>0 else np.nan})
    return pd.DataFrame(rows)


def bt_run_condition_contribution(r,data,initial_cash=1_000_000,hold_days=60,fee=0.001,slip=0.0005):
    x=bt_condition_contribution_flags(r,data)
    if x.empty: return pd.DataFrame(),{},{}
    flags=[
        ("BASE","D 기본"),
        ("BASE_추세","BASE + ETF 추세"),
        ("BASE_거래량모멘텀","BASE + 거래량/모멘텀"),
        ("BASE_시장환경","BASE + 시장환경"),
        ("BASE_추세_거래량모멘텀","BASE + 추세 + 거래량/모멘텀"),
        ("BASE_추세_거래량모멘텀_시장환경","BASE + 추세 + 거래량/모멘텀 + 시장환경"),
    ]
    rows=[]; details={}; annual={}
    for flag,name in flags:
        td,m=bt_simulate_contribution_strategy(x,data,flag,initial_cash,hold_days,fee,slip)
        details[name]=td; annual[name]=bt_annual_contribution(td)
        rows.append({"전략":name,"신호수":int(x[flag].sum()),**{k:m.get(k,np.nan) for k in ["거래수","총수익률","CAGR","MDD","승률","Profit Factor","평균거래수익"]}})
    return pd.DataFrame(rows),details,annual

def bt_run_final_strategy_compare(r, data, initial_cash=1_000_000, hold_days=60, fee=0.001, slip=0.0005):
    """최종 후보 3개만 동일 체결엔진으로 비교한다.
    C = 미래테마 + 선행점수
    D = C + 가격구간
    D+M = D + 시장환경
    """
    x = bt_condition_contribution_flags(r, data)
    if x.empty:
        return pd.DataFrame(), {}, {}

    specs = [
        ("C_미래테마선행", "C · 미래테마+선행"),
        ("D_미래테마선행가격", "D · 미래테마+선행+가격"),
        ("BASE_시장환경", "D+M · D+시장환경"),
    ]
    rows, details, annual = [], {}, {}
    for flag, name in specs:
        td, m = bt_simulate_contribution_strategy(
            x, data, flag, initial_cash, hold_days, fee, slip
        )
        details[name] = td
        annual[name] = bt_annual_contribution(td)
        rows.append({
            "전략": name,
            "신호수": int(x[flag].fillna(False).sum()),
            "거래수": int(m.get("거래수", 0)),
            "총수익률": m.get("총수익률", np.nan),
            "CAGR": m.get("CAGR", np.nan),
            "MDD": m.get("MDD", np.nan),
            "승률": m.get("승률", np.nan),
            "Profit Factor": m.get("Profit Factor", np.nan),
            "평균거래수익": m.get("평균거래수익", np.nan),
        })
    return pd.DataFrame(rows), details, annual




# ============================================================
# 미래테마 · 선행 ETF 검증 실험실
# 기존 D는 BASELINE으로 고정하고 새 ETF 선정 로직만 단계별 검증한다.
# ============================================================

def _bt_row_market_features(row, data, bench_df=None):
    """신호일 현재까지 공개된 가격정보만 사용해 ETF 선행/미반영 특성을 계산."""
    ticker = row.get("ETF")
    dt = pd.Timestamp(row.get("날짜"))
    d = data.get(ticker)
    if d is None or d.empty:
        return {}
    pos = d.index.searchsorted(dt)
    if pos >= len(d) or d.index[pos] != dt:
        return {}
    z = d.iloc[pos]
    def f(k, default=np.nan):
        try:
            v=float(z.get(k, default)); return v if np.isfinite(v) else default
        except Exception: return default
    close=f("Close"); ma20=f("MA20"); ma60=f("MA60"); r20=f("R20", f("RET20")); r5=f("R5", f("RET5"))
    rsi=f("RSI", f("RSI14", 50)); vr=f("VR", f("VOL_RATIO", 1))
    dist20=(close/ma20-1)*100 if np.isfinite(close) and np.isfinite(ma20) and ma20 else np.nan
    rs20=r20
    if bench_df is not None and not bench_df.empty:
        bp=bench_df.index.searchsorted(dt)
        if bp < len(bench_df) and bench_df.index[bp] == dt:
            bz=bench_df.iloc[bp]
            br20=bz.get("R20", bz.get("RET20", np.nan))
            try:
                if np.isfinite(float(br20)) and np.isfinite(r20): rs20=r20-float(br20)
            except Exception: pass
    trend=1.0 if np.isfinite(close) and np.isfinite(ma20) and np.isfinite(ma60) and close>=ma20>=ma60 else (0.65 if np.isfinite(close) and np.isfinite(ma60) and close>=ma60 else 0.35)
    not_hot=100.0
    if np.isfinite(rsi): not_hot -= max(0.0, rsi-62)*2.0
    if np.isfinite(dist20): not_hot -= max(0.0, dist20-4)*4.0
    if np.isfinite(r20): not_hot -= max(0.0, r20-10)*2.0
    not_hot=float(np.clip(not_hot,0,100))
    # "미반영도"는 약한 종목을 찾는 점수가 아니라, 선행조건은 양호하면서 가격 과열이 낮은 상태를 선호한다.
    lead_raw=safe_float(row.get("선행점수", row.get("선행점수", 0)),0)
    if not np.isfinite(lead_raw): lead_raw=0
    lead_norm=float(np.clip(lead_raw,0,100))
    rel_score=50.0 if not np.isfinite(rs20) else float(np.clip(50+rs20*4,0,100))
    accel_score=50.0
    if np.isfinite(r5) and np.isfinite(r20): accel_score=float(np.clip(50+(r5-r20/4)*8,0,100))
    flow_score=50.0 if not np.isfinite(vr) else float(np.clip(50+(vr-1)*35,0,100))
    early_score=0.35*lead_norm + 0.20*rel_score + 0.15*trend*100 + 0.10*accel_score + 0.10*flow_score + 0.10*not_hot
    # 미반영도: 선행강도와 비과열도를 결합. 너무 약한 ETF는 자동으로 낮아진다.
    underpriced=float(np.clip(0.60*lead_norm + 0.40*not_hot,0,100))
    return {"lead":lead_norm,"rsi":rsi,"vr":vr,"r20":r20,"r5":r5,"dist20":dist20,
            "rs20":rs20,"trend":trend*100,"not_hot":not_hot,"early_score":early_score,"underpriced":underpriced}

def bt_build_early_selection_flags(r, data):
    """D0~D3을 같은 D 신호군에서 파생한다. 기존 D 계산식은 변경하지 않는다."""
    if r is None or r.empty or "D_미래테마선행가격" not in r.columns:
        return pd.DataFrame()
    x=r.copy()
    bench=data.get(BT_BENCH)
    if bench is not None and not bench.empty and "MA60" not in bench.columns:
        bench=bt_indicators(bench.copy())
    feats=[]
    for _,row in x.iterrows():
        feats.append(_bt_row_market_features(row,data,bench))
    f=pd.DataFrame(feats,index=x.index)
    for c in f.columns: x["검증_"+c]=f[c]
    base=x["D_미래테마선행가격"].fillna(False).astype(bool)
    # 날짜별 cross-section percentile. 특정 시대의 절대값 변화에 덜 민감하게 한다.
    for c in ["early_score","underpriced","lead","not_hot"]:
        x["검증_"+c+"_pct"]=x.groupby("날짜")["검증_"+c].rank(pct=True)*100
    x["D0_기존"] = base
    x["D1_선행강세"] = base & (x["검증_early_score_pct"]>=60)
    x["D2_선행_미반영"] = base & (x["검증_early_score_pct"]>=60) & (x["검증_underpriced_pct"]>=60)
    x["D3_선행_미반영_과열회피"] = base & (x["검증_early_score_pct"]>=60) & (x["검증_underpriced_pct"]>=60) & (x["검증_not_hot_pct"]>=40)
    return x

def bt_simulate_selection_validation(r, data, flag, initial_cash=1_000_000, hold_days=60, fee_per_side=0.001, slippage_per_side=0.0005):
    """동일한 고정 보유기간 체결엔진 + MFE/MAE. 다음 거래일 시가 진입."""
    if r is None or r.empty or flag not in r.columns: return pd.DataFrame(), {}
    sigs=r.loc[r[flag].fillna(False).astype(bool)].copy().sort_values("날짜")
    if sigs.empty: return pd.DataFrame(), {}
    cash=float(initial_cash); peak=float(initial_cash); next_available=pd.Timestamp.min; trades=[]; curve=[]
    for _,sig in sigs.iterrows():
        signal_date=pd.Timestamp(sig["날짜"]);
        if signal_date < next_available: continue
        d=data.get(sig["ETF"]);
        if d is None or d.empty: continue
        idx=d.index.searchsorted(signal_date)
        entry_i=idx+1; exit_i=entry_i+int(hold_days)-1
        if idx>=len(d) or d.index[idx]!=signal_date or exit_i>=len(d): continue
        er=d.iloc[entry_i]; xr=d.iloc[exit_i]
        entry=float(er.get("Open",er.get("Close",np.nan))); exitp=float(xr.get("Close",np.nan))
        if not np.isfinite(entry) or entry<=0 or not np.isfinite(exitp): continue
        path=d.iloc[entry_i:exit_i+1]
        highs=pd.to_numeric(path.get("High",path.get("Close")),errors="coerce")
        lows=pd.to_numeric(path.get("Low",path.get("Close")),errors="coerce")
        mfe=(float(highs.max())/entry-1)*100 if highs.notna().any() else np.nan
        mae=(float(lows.min())/entry-1)*100 if lows.notna().any() else np.nan
        buy=entry*(1+slippage_per_side); sell=exitp*(1-slippage_per_side); net=(sell/buy-1)-fee_per_side*2
        cash*=1+net; peak=max(peak,cash); curve.append({"날짜":d.index[exit_i],"자산":cash})
        trades.append({"전략":flag,"신호일":signal_date.date(),"진입일":d.index[entry_i].date(),"청산일":d.index[exit_i].date(),"ETF":sig["ETF"],
                       "테마":sig.get("테마",""),"테마점수":sig.get("테마점수",np.nan),"선행점수":sig.get("선행점수",np.nan),
                       "검증_선행점수":sig.get("검증_lead",np.nan),"검증_선행강세점수":sig.get("검증_early_score",np.nan),
                       "검증_미반영점수":sig.get("검증_underpriced",np.nan),"검증_비과열점수":sig.get("검증_not_hot",np.nan),
                       "20일수익":sig.get("20일수익",np.nan),"60일수익":sig.get("60일수익",np.nan),"MFE":mfe,"MAE":mae,"순수익률":net*100,"거래후자산":cash})
        next_available=d.index[exit_i]+pd.Timedelta(days=1)
    td=pd.DataFrame(trades); cv=pd.DataFrame(curve)
    if td.empty or cv.empty: return td,{"거래수":0,"총수익률":0,"CAGR":np.nan,"MDD":0,"승률":np.nan,"Profit Factor":np.nan,"평균MFE":np.nan,"平均MAE":np.nan}
    cv=cv.sort_values("날짜").drop_duplicates("날짜",keep="last"); cv["고점"]=cv["자산"].cummax(); cv["낙폭"]=(cv["자산"]/cv["고점"]-1)*100
    final=float(cv.iloc[-1]["자산"]); total=(final/initial_cash-1)*100; days=max(1,(pd.Timestamp(cv.iloc[-1]["날짜"])-pd.Timestamp(cv.iloc[0]["날짜"])).days)
    cagr=((final/initial_cash)**(365.25/days)-1)*100 if final>0 else -100
    wins=int((td["순수익률"]>0).sum()); loss_abs=abs(float(td.loc[td["순수익률"]<0,"순수익률"].sum())); gains=float(td.loc[td["순수익률"]>0,"순수익률"].sum())
    pf=gains/loss_abs if loss_abs>0 else (np.inf if gains>0 else np.nan)
    return td,{"거래수":len(td),"총수익률":total,"CAGR":cagr,"MDD":float(cv["낙폭"].min()),"승률":wins/len(td)*100 if len(td) else np.nan,
               "Profit Factor":pf,"평균거래수익":float(td["순수익률"].mean()),"평균MFE":float(td["MFE"].mean()),"평균MAE":float(td["MAE"].mean()),
               "MFE_중앙값":float(td["MFE"].median()),"MAE_중앙값":float(td["MAE"].median())}

def bt_run_early_selection_validation(r,data,initial_cash=1_000_000,hold_days=60,fee=0.001,slip=0.0005):
    x=bt_build_early_selection_flags(r,data)
    if x.empty: return pd.DataFrame(),{},{}
    specs=[("D0_기존","D0 · 기존 D"),("D1_선행강세","D1 · D + 선행강세"),("D2_선행_미반영","D2 · D + 선행 + 미반영"),("D3_선행_미반영_과열회피","D3 · D + 선행 + 미반영 + 과열회피")]
    rows=[]; details={}; annual={}
    for flag,name in specs:
        td,m=bt_simulate_selection_validation(x,data,flag,initial_cash,hold_days,fee,slip); details[name]=td
        if not td.empty:
            z=td.copy(); z["청산일"]=pd.to_datetime(z["청산일"]); z["연도"]=z["청산일"].dt.year
            annual[name]=z.groupby("연도").agg(거래수=("순수익률","size"),평균수익=("순수익률","mean"),승률=("순수익률",lambda s:(s>0).mean()*100),평균MFE=("MFE","mean"),평균MAE=("MAE","mean")).reset_index()
        else: annual[name]=pd.DataFrame()
        rows.append({"전략":name,"신호수":int(x[flag].sum()),**m})
    cmp=pd.DataFrame(rows)
    if not cmp.empty:
        base=cmp.iloc[0]
        for col in ["CAGR","Profit Factor","승률","MDD","평균MFE","평균MAE"]:
            cmp["기준대비_"+col]=cmp[col]-base[col] if col in cmp.columns else np.nan
    return cmp,details,annual

def render_backtest_lab():
    """백테스트 LAB - 최종 화면 5개 섹션만 표시."""
    st.markdown(
        '<div class="hero"><div class="hero-name">🧪 백테스트 LAB</div>'
        '<div class="hero-code">기존 전략 검증 · 미래테마 · 선행 ETF · 미반영 · 과열회피</div></div>',
        unsafe_allow_html=True,
    )
    st.info(
        "연구용 백테스트입니다. 신호일 이후 데이터가 섞이지 않도록 다음 거래일 진입을 사용합니다. "
        "실제 주문체결·세금·배당·환전비용은 완전히 반영되지 않습니다."
    )

    # ========================================================
    # ① 설정 / 실행
    # ========================================================
    st.markdown("### ① 백테스트 설정 / 실행")

    c1, c2, c3 = st.columns(3)
    with c1:
        start = st.date_input("시작일", date(2018, 1, 1), key="bt_start")
    with c2:
        end = st.date_input("종료일", date.today(), key="bt_end")
    with c3:
        step = st.select_slider(
            "검사 간격", options=[1, 3, 5, 10], value=5, key="bt_step",
            format_func=lambda x: "매일" if x == 1 else f"{x}거래일마다"
        )

    defaults = [
        "QQQ", "XLK", "SMH", "SOXX", "BOTZ", "ARKQ",
        "GLD", "TLT", "INDA", "EWY", "EWJ", "EEM"
    ]
    # BT_POOL 변경으로 기본값이 사라져도 앱이 멈추지 않도록 교집합 처리
    defaults = [x for x in defaults if x in BT_POOL]
    selected = st.multiselect(
        "검증 ETF", list(BT_POOL.keys()), defaults,
        key="bt_selected",
        format_func=lambda x: f"{x} · {BT_POOL[x]}"
    )

    v1, v2, v3 = st.columns(3)
    with v1:
        initial_cash = st.number_input(
            "초기자산", min_value=100000, value=1000000,
            step=100000, key="bt_final_cash"
        )
    with v2:
        hold_days = st.number_input(
            "보유기간", min_value=5, max_value=500, value=60,
            step=5, key="bt_final_hold"
        )
    with v3:
        fee = st.number_input(
            "편도 수수료", min_value=0.0, max_value=0.01, value=0.001,
            step=0.0001, format="%.4f", key="bt_final_fee"
        )
    slip = st.number_input(
        "편도 슬리피지", min_value=0.0, max_value=0.01, value=0.0005,
        step=0.0001, format="%.4f", key="bt_final_slip"
    )

    if st.button(
        "🚀 최종 3전략 백테스트 실행",
        type="primary", use_container_width=True, key="bt_run_final3"
    ):
        if start >= end:
            st.error("시작일은 종료일보다 빨라야 합니다.")
        elif len(selected) < 4:
            st.error("테마 비교를 위해 ETF를 4개 이상 선택하십시오.")
        else:
            with st.spinner("가격·지표·미래테마·선행신호를 계산하는 중입니다…"):
                try:
                    result, data = bt_run_strategy_backtest(start, end, selected, step)
                    st.session_state["strategy_result"] = result
                    st.session_state["strategy_data"] = data
                    st.session_state["final_compare"] = None
                    st.session_state["final_details"] = None
                    st.session_state["final_annual"] = None
                    st.session_state["bt_last_config"] = {
                        "start": str(start), "end": str(end),
                        "selected": selected, "step": step,
                        "hold_days": hold_days, "fee": fee, "slip": slip,
                    }
                    st.success(f"검사 완료 · {len(result):,}개 검사 시점")
                except Exception as ex:
                    st.error("백테스트 실행 중 오류가 발생했습니다.")
                    st.exception(ex)

    r = st.session_state.get("strategy_result")
    data = st.session_state.get("strategy_data")

    if r is None or data is None:
        st.caption("①의 실행 버튼을 누르면 ②~⑤ 결과가 표시됩니다.")
        return
    if r.empty:
        st.warning("백테스트 결과가 없습니다.")
        return

    # ========================================================
    # ② 최종 전략 비교
    # ========================================================
    st.markdown("---")
    st.markdown("### ② 최종 전략 비교 — C / D / D+시장환경")
    st.caption(
        "C = 미래테마 + 선행점수 / D = C + 가격구간 / D+M = D + 시장환경. "
        "동일한 진입일·보유기간·비용 조건으로 비교합니다."
    )

    if st.button(
        "🔬 C / D / D+시장환경 비교 실행",
        type="primary", use_container_width=True, key="bt_run_final_compare"
    ):
        with st.spinner("최종 후보 3전략을 동일 조건으로 비교하는 중입니다…"):
            try:
                final_cmp, final_details, final_annual = bt_run_final_strategy_compare(
                    r, data,
                    initial_cash=initial_cash,
                    hold_days=hold_days,
                    fee=fee,
                    slip=slip,
                )
                st.session_state["final_compare"] = final_cmp
                st.session_state["final_details"] = final_details
                st.session_state["final_annual"] = final_annual
            except Exception as ex:
                st.error("최종 전략 비교 중 오류가 발생했습니다.")
                st.exception(ex)

    final_cmp = st.session_state.get("final_compare")
    final_details = st.session_state.get("final_details")
    final_annual = st.session_state.get("final_annual")

    if isinstance(final_cmp, pd.DataFrame) and not final_cmp.empty:
        st.dataframe(final_cmp, use_container_width=True, hide_index=True)
        st.download_button(
            "📥 최종 3전략 비교 CSV",
            final_cmp.to_csv(index=False).encode("utf-8-sig"),
            "ETF_RADAR_FINAL_3_STRATEGY_COMPARISON.csv",
            "text/csv;charset=utf-8",
            use_container_width=True,
            key="bt_download_final_compare",
        )
    else:
        st.info("②의 비교 실행 버튼을 누르면 C / D / D+시장환경 결과가 표시됩니다.")

    # ========================================================
    # ③ 연도별 성과
    # ========================================================
    st.markdown("---")
    st.markdown("### ③ 연도별 성과")
    st.caption("최종 3전략의 연도별 거래 수와 수익률을 비교합니다.")

    if isinstance(final_annual, dict) and final_annual:
        annual_frames = []
        for name, df in final_annual.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                z = df.copy()
                z.insert(0, "전략", name)
                annual_frames.append(z)
        if annual_frames:
            annual_all = pd.concat(annual_frames, ignore_index=True)
            st.dataframe(annual_all, use_container_width=True, hide_index=True)
            st.download_button(
                "📥 연도별 성과 CSV",
                annual_all.to_csv(index=False).encode("utf-8-sig"),
                "ETF_RADAR_FINAL_3_STRATEGY_ANNUAL.csv",
                "text/csv;charset=utf-8",
                use_container_width=True,
                key="bt_download_final_annual",
            )
        else:
            st.info("연도별 성과 데이터가 없습니다.")
    else:
        st.info("②의 최종 전략 비교를 먼저 실행하면 연도별 성과가 표시됩니다.")

    # ========================================================
    # ④ 거래 상세
    # ========================================================
    st.markdown("---")
    st.markdown("### ④ 거래 상세")
    st.caption("최종 3전략에서 실제로 발생한 진입·청산 거래를 확인합니다.")

    all_detail = None
    if isinstance(final_details, dict) and final_details:
        detail_frames = []
        for name, df in final_details.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                z = df.copy()
                z.insert(0, "전략", name)
                detail_frames.append(z)
        if detail_frames:
            all_detail = pd.concat(detail_frames, ignore_index=True)

    if isinstance(all_detail, pd.DataFrame) and not all_detail.empty:
        with st.expander("📋 거래 상세 열기", expanded=False):
            st.dataframe(
                all_detail,
                use_container_width=True,
                hide_index=True,
                height=420,
            )
        st.download_button(
            "📥 최종 전략 거래상세 CSV",
            all_detail.to_csv(index=False).encode("utf-8-sig"),
            "ETF_RADAR_FINAL_3_STRATEGY_TRADES.csv",
            "text/csv;charset=utf-8",
            use_container_width=True,
            key="bt_download_final_trades",
        )
    else:
        st.info("②의 최종 전략 비교를 먼저 실행하면 거래 상세가 표시됩니다.")

    # ========================================================
    # ⑤ 원본 검사시점
    # ========================================================
    st.markdown("---")
    st.markdown("### ⑤ 원본 검사시점")
    st.caption(
        f"전체 {len(r):,}개 검사 시점 · 화면에는 최근 300개만 표시하며, "
        "전체 데이터는 CSV로 받을 수 있습니다."
    )

    with st.expander("📋 원본 검사시점 전체 데이터 열기", expanded=False):
        st.dataframe(
            r.tail(300),
            use_container_width=True,
            hide_index=True,
            height=420,
        )

    st.download_button(
        "📥 원본 검사시점 전체 CSV",
        r.to_csv(index=False).encode("utf-8-sig"),
        "ETF_RADAR_BACKTEST_SIGNAL_DETAIL.csv",
        "text/csv;charset=utf-8",
        use_container_width=True,
        key="bt_download_signal",
    )

    # ========================================================
    # ⑥ 미래테마 · 선행 ETF 검증
    # ========================================================
    st.markdown("---")
    st.markdown("### ⑥ 미래테마 · 선행 ETF 검증")
    st.caption(
        "기존 D를 BASELINE으로 고정하고, 같은 검사시점·다음 거래일 시가·동일 보유기간·동일 비용으로 "
        "선행강세 → 미반영 → 과열회피를 한 단계씩 추가합니다. "
        "신호일 이후 OHLC로 MFE/MAE를 계산하며, 기존 D 계산식은 변경하지 않습니다."
    )

    if st.button("🧪 D0 / D1 / D2 / D3 검증 실행", type="primary", use_container_width=True, key="bt_run_early_validation"):
        with st.spinner("선행강세·미반영·과열회피와 MFE/MAE를 검증하는 중입니다…"):
            try:
                vc,vd,va=bt_run_early_selection_validation(r,data,initial_cash,hold_days,fee,slip)
                st.session_state["early_validation_cmp"]=vc
                st.session_state["early_validation_details"]=vd
                st.session_state["early_validation_annual"]=va
            except Exception as ex:
                st.error("선행 ETF 검증 중 오류가 발생했습니다.")
                st.exception(ex)

    vc=st.session_state.get("early_validation_cmp")
    vd=st.session_state.get("early_validation_details")
    va=st.session_state.get("early_validation_annual")
    if isinstance(vc,pd.DataFrame) and not vc.empty:
        display_cols=["전략","신호수","거래수","총수익률","CAGR","MDD","승률","Profit Factor","평균거래수익","평균MFE","평균MAE","MFE_중앙값","MAE_중앙값"]
        st.dataframe(vc[[c for c in display_cols if c in vc.columns]],use_container_width=True,hide_index=True)
        st.download_button("📥 D0-D3 검증 비교 CSV",vc.to_csv(index=False).encode("utf-8-sig"),"ETF_RADAR_D0_D3_EARLY_SELECTION_VALIDATION.csv","text/csv;charset=utf-8",use_container_width=True,key="bt_download_early_cmp")

        st.markdown("#### 판정 기준")
        st.info("D1~D3는 D0보다 거래수가 지나치게 줄면서 성과가 좋아진 경우를 별도로 봐야 합니다. CAGR·PF만 상승했다고 채택하지 않고 MDD, 승률, MFE/MAE, 연도별 재현성을 함께 확인합니다.")

        if isinstance(vd,dict) and vd:
            frames=[]
            for name,td in vd.items():
                if isinstance(td,pd.DataFrame) and not td.empty:
                    frames.append(td)
            if frames:
                all_v=pd.concat(frames,ignore_index=True)
                with st.expander("📋 D0-D3 거래별 MFE / MAE",expanded=False):
                    st.dataframe(all_v,use_container_width=True,hide_index=True,height=420)
                st.download_button("📥 D0-D3 거래 상세 CSV",all_v.to_csv(index=False).encode("utf-8-sig"),"ETF_RADAR_D0_D3_EARLY_SELECTION_TRADES.csv","text/csv;charset=utf-8",use_container_width=True,key="bt_download_early_trades")

        if isinstance(va,dict) and va:
            af=[]
            for name,df in va.items():
                if isinstance(df,pd.DataFrame) and not df.empty:
                    z=df.copy(); z.insert(0,"전략",name); af.append(z)
            if af:
                annual_all=pd.concat(af,ignore_index=True)
                with st.expander("📊 D0-D3 연도별 검증",expanded=False):
                    st.dataframe(annual_all,use_container_width=True,hide_index=True)
                st.download_button("📥 D0-D3 연도별 CSV",annual_all.to_csv(index=False).encode("utf-8-sig"),"ETF_RADAR_D0_D3_EARLY_SELECTION_ANNUAL.csv","text/csv;charset=utf-8",use_container_width=True,key="bt_download_early_annual")

        st.markdown("#### 핵심 해석")
        st.write("• D1: 기존 D에서 선행강세가 실제로 추가가치를 만드는지 확인")
        st.write("• D2: 선행조건이 좋으면서 아직 가격에 덜 반영된 ETF가 더 좋은지 확인")
        st.write("• D3: D2에서 과열 ETF를 제거해 손실/MDD가 개선되는지 확인")
        st.write("• MFE가 커지고 MAE가 덜 나빠지면서 PF/CAGR가 개선되고, 여러 연도에서 반복되어야 최종 채택 후보입니다.")
    else:
        st.info("⑥의 검증 실행 버튼을 누르면 새 ETF 선정 로직을 기존 D와 동일 조건으로 비교합니다.")


# ============================================================
# TRUE WALK-FORWARD VALIDATION
# 실제 앱의 THEME_LEXICON / ETF MASTER / 선행 ETF / 가격구간 로직을
# 과거 날짜별로 재생하는 화면형 검증 엔진
# ============================================================

WF_BENCH = "069500"
WF_HOLD_DAYS = 60
WF_FEE = 0.0010
WF_SLIPPAGE = 0.0005
WF_OOS_YEAR = 2024
WF_MAX_MEMBERS = 5


def wf_indicator(df):
    if df is None or df.empty:
        return pd.DataFrame()
    return bt_indicators(df.copy())


def wf_fetch_one(code):
    code = _normalize_etf_code(code)
    try:
        d = yf.download(
            f"{code}.KS", period="max", interval="1d",
            auto_adjust=False, progress=False, threads=False
        )
        d = normalize_df(d)
        if not d.empty:
            return code, d
    except Exception:
        pass
    try:
        d = fetch_naver_history(code, count=2000)
        return code, d
    except Exception:
        return code, pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def wf_download_history(codes):
    codes = tuple(sorted(set(_normalize_etf_code(x) for x in codes if x)))
    out = {}
    # 병렬 다운로드. 실패한 종목은 조용히 제외합니다.
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(wf_fetch_one, c) for c in codes]
        for f in as_completed(futures):
            try:
                code, d = f.result()
                if d is not None and not d.empty:
                    out[code] = wf_indicator(d)
            except Exception:
                continue
    return out


def wf_build_universe():
    universe = st.session_state.get("etf_universe") or load_etf_universe()
    if not universe:
        raise RuntimeError("ETF MASTER를 가져오지 못했습니다.")
    st.session_state.etf_universe = universe
    theme_members = {}
    codes = {WF_BENCH}
    for theme, keywords in THEME_LEXICON.items():
        matched = []
        for code, name in universe.items():
            hits = _theme_match_for_theme(name, keywords, theme)
            if hits:
                matched.append((hits, _normalize_etf_code(code), safe_etf_name(code, name)))
        matched.sort(key=lambda x: (x[0], x[2]), reverse=True)
        if len(matched) >= 2:
            # Store the full current-master candidate set. wf_snapshot will select up to
            # WF_MAX_MEMBERS only from candidates that actually have data by each date.
            # This mitigates future-listing leakage, but cannot recover delisted ETFs
            # absent from the current ETF MASTER.
            theme_members[theme] = [(x[1], x[2], x[0]) for x in matched]
            codes.update(x[1] for x in matched)
    return universe, theme_members, sorted(codes)


def wf_row_at(d, dt):
    if d is None or d.empty:
        return None
    # Do not carry the last available row forward beyond the end of the price series.
    if pd.Timestamp(dt) > pd.Timestamp(d.index.max()):
        return None
    pos = d.index.searchsorted(pd.Timestamp(dt), side="right") - 1
    if pos < 0 or pos >= len(d):
        return None
    return d.iloc[pos]


def wf_snapshot(data, theme_members, dt):
    """현재 실전 미래테마/레이더/최종타겟 산식을 과거 날짜에 그대로 재생합니다."""
    bench = data.get(WF_BENCH)
    br = wf_row_at(bench, dt)
    if br is None:
        return None
    bench_ret20 = float(br.get("R20", np.nan))
    bench_ret60 = float(br.get("R60", np.nan))
    if not np.isfinite(bench_ret20) or not np.isfinite(bench_ret60):
        return None

    theme_results = []
    for theme, members in theme_members.items():
        rows = []
        # Point-in-time availability filter: an ETF must have price history on or
        # before the simulated date AND must not have ended trading before that date.
        # This prevents stale last prices from a delisted/ended series being reused.
        # Limitation: current ETF MASTER still omits delisted ETFs and historical theme membership.
        eligible_members = []
        for code, name, hits in members:
            candidate_data = data.get(code)
            if candidate_data is None or candidate_data.empty:
                continue
            first_dt = pd.Timestamp(candidate_data.index.min())
            last_dt = pd.Timestamp(candidate_data.index.max())
            point_dt = pd.Timestamp(dt)
            if first_dt > point_dt or last_dt < point_dt:
                continue
            eligible_members.append((code, name, hits))
        members = eligible_members[:WF_MAX_MEMBERS]
        for code, name, hits in members:
            d = data.get(code)
            r = wf_row_at(d, dt)
            if r is None:
                continue
            needed = ["Close", "MA20", "MA60", "R5", "R20", "R60", "VR", "RSI", "LOW20"]
            if any(not np.isfinite(float(r.get(k, np.nan))) for k in needed):
                continue
            rr = r.to_dict()
            current = float(rr["Close"])
            ma20 = float(rr["MA20"])
            ma60 = float(rr["MA60"])
            ret20 = float(rr["R20"])
            ret60 = float(rr["R60"])
            ret5 = float(rr["R5"])
            vr = float(rr["VR"])
            rsi = float(rr["RSI"])
            accel = ret5 - ret20 / 4
            breadth = 100.0 if current >= ma20 else 0.0
            prev = None
            if d is not None and not d.empty:
                # Use only the number of observations available at dt. Do not gate
                # this calculation on len(d), which includes future rows in a replay.
                pos = d.index.searchsorted(pd.Timestamp(dt), side="right") - 1
                if pos >= 21:
                    prev = d.iloc[pos - 20]
            if prev is not None:
                prev_close = safe_float(prev.get("Close"), 0)
                prev_ma20 = safe_float(prev.get("MA20"), prev_close)
                prev_ret20 = safe_float(prev.get("R20"), ret20)
                prev_ret5 = safe_float(prev.get("R5"), ret5)
                prev_breadth = 100.0 if prev_close >= prev_ma20 else 0.0
                prev_accel = prev_ret5 - prev_ret20 / 4
                prev_rs20 = prev_ret20 - bench_ret20
            else:
                prev_ret20 = ret20
                prev_breadth = breadth
                prev_accel = accel
                prev_rs20 = ret20 - bench_ret20
            rr.update({
                "ETF": code, "Name": name, "hits": hits,
                "ret20": ret20, "ret60": ret60, "ret5": ret5,
                "vr": vr, "rsi": rsi,
                "ma60_gap": (current / ma60 - 1) * 100 if ma60 else 0,
                "breadth": breadth, "accel": accel,
                "rs20": ret20 - bench_ret20,
                "ret20_prev": prev_ret20, "breadth_prev": prev_breadth,
                "accel_prev": prev_accel, "rs20_prev": prev_rs20,
            })
            rows.append(rr)

        if len(rows) < 2:
            continue
        raw_score = theme_score(rows, bench_ret20, bench_ret60)
        if raw_score is None:
            continue
        lifecycle = _theme_lifecycle(rows, {"ret20": bench_ret20, "ret60": bench_ret60})
        final_score = float(np.clip(raw_score * 0.75 + lifecycle["score"] * 0.25, 0, 100))
        stage = _theme_stage(final_score, 0, 0, lifecycle)
        theme_results.append({
            "theme": theme,
            "score": final_score,
            "base_score": raw_score,
            "lifecycle": lifecycle,
            "rows": rows,
            "stage": stage,
            "heat": max(0, 100 - lifecycle["score"]),
        })

    if not theme_results:
        return None

    # 실전 미래테마 엔진과 동일하게 점수 기준으로 테마 순위를 만듭니다.
    theme_results.sort(key=lambda x: x["score"], reverse=True)
    theme_results = [x for x in theme_results if x["score"] >= 42][:8]
    if not theme_results:
        return None

    # 실전 _theme_etf_rank와 동일한 개념으로 각 테마의 대표 ETF를 과거 시점에서 계산합니다.
    selected = []
    for theme_rank, top in enumerate(theme_results, 1):
        ranked = []
        for row in top["rows"]:
            sig = leading_signal(row, bench_ret20)
            zone = validated_price_zone(row)
            signal_score = float(sig["score"]) * 0.65 + float(top["score"]) * 0.35
            ranked.append({
                "row": row,
                "sig": sig,
                "zone": zone,
                "signal_score": signal_score,
            })
        ranked.sort(key=lambda z: (z["signal_score"], safe_float(z["row"].get("ret20"), -999)), reverse=True)

        for etf_rank, cand in enumerate(ranked[:3], 1):
            row = cand["row"]
            sig = cand["sig"]
            zone = cand["zone"]
            radar = {
                "above20": float(row["Close"]) >= float(row["MA20"]),
                "above60": float(row["Close"]) >= float(row["MA60"]),
                "rs20": sig["rs20"],
                "vr": sig["vr"], "ret20": float(row["R20"]), "ret5": float(row["R5"]),
                "rsi": sig["rsi"], "dist20": sig["dist20"],
            }
            opportunity = radar_score(radar)
            overheat = radar_overheat_score(radar)
            pscore = {"매수구간":100, "눌림대기":70, "추격금지":25, "무효":0}.get(zone["state"], 0)
            cross = (
                float(np.clip(top["base_score"], 0, 100)) * 0.30
                + float(np.clip(top["lifecycle"]["score"], 0, 100)) * 0.20
                + float(np.clip(cand["sig"]["score"], 0, 100)) * 0.30
                + float(np.clip(opportunity, 0, 100)) * 0.10
                + float(np.clip(pscore, 0, 100)) * 0.10
            )
            # 현재 앱 build_radar_data와 동일한 쇠퇴/과열 감점.
            if top["lifecycle"].get("state") == "쇠퇴":
                cross -= 18
            elif top["lifecycle"].get("state") == "과열":
                cross -= 10
            if overheat >= 65:
                cross -= 10
            cross_score = int(np.clip(round(cross), 0, 100))

            selected.append({
                "row": row, "theme": top["theme"], "theme_rank": theme_rank,
                "etf_rank": etf_rank, "theme_score": top["score"],
                "lifecycle_score": top["lifecycle"]["score"],
                "lifecycle_state": top["lifecycle"]["state"],
                "lead_score": sig["score"], "price_zone": zone["state"],
                "opportunity": opportunity, "overheat": overheat,
                "cross_score": cross_score,
            })

    # 실전과 같은 7개 축(테마·상대강도·모멘텀·가속·추세)으로 과거 후보를 정렬합니다.
    # 과거 시점의 후보 집합 안에서 각 지표를 백분위화해 단위가 다른 값을 직접 섞지 않습니다.
    targets = []
    for x in selected:
        row = x["row"]
        ret5 = safe_float(row.get("R5"), 0)
        ret20 = safe_float(row.get("R20"), 0)
        ret60 = safe_float(row.get("R60"), 0)
        rs20 = ret20 - bench_ret20
        rs60 = ret60 - bench_ret60
        accel = ret20 - ret60 / 3.0
        close = safe_float(row.get("Close"), 0)
        ma20 = safe_float(row.get("MA20"), close)
        ma60 = safe_float(row.get("MA60"), close)
        ma120 = safe_float(row.get("MA120"), close)
        trend_score = (
            (35 if close >= ma20 and ma20 > 0 else 0)
            + (35 if close >= ma60 and ma60 > 0 else 0)
            + (20 if ma20 >= ma60 and ma20 > 0 and ma60 > 0 else 0)
            + (10 if ma60 >= ma120 and ma60 > 0 and ma120 > 0 else 0)
        )
        x.update({"ret5": ret5, "ret20": ret20, "ret60": ret60, "rs20": rs20,
                  "rs60": rs60, "acceleration_raw": accel, "trend_score": trend_score})
        targets.append(x)

    if not targets:
        return None
    rank_fields = {
        "theme_pct": [safe_float(x.get("theme_score"), 50) for x in targets],
        "rs20_pct": [x["rs20"] for x in targets],
        "rs60_pct": [x["rs60"] for x in targets],
        "ret20_pct": [x["ret20"] for x in targets],
        "ret60_pct": [x["ret60"] for x in targets],
        "accel_pct": [x["acceleration_raw"] for x in targets],
        "trend_pct": [x["trend_score"] for x in targets],
    }
    for field, values in rank_fields.items():
        pct_values = _cross_section_percentile(values)
        for x, value in zip(targets, pct_values):
            x[field] = value
    for x in targets:
        x["final_score"] = _unified_return_opportunity_score(
            x["theme_pct"], x["rs20_pct"], x["rs60_pct"], x["ret20_pct"],
            x["ret60_pct"], x["accel_pct"], x["trend_pct"]
        )
    targets.sort(key=lambda x: (x["final_score"], x["cross_score"], x.get("rs20", -999), x.get("ret20", -999), -x["theme_rank"]), reverse=True)
    winner = targets[0]
    row = winner["row"]
    market_pass = bool(
        float(br.get("Close", np.nan)) >= float(br.get("MA60", np.nan))
        and float(br.get("Close", np.nan)) >= float(br.get("MA120", np.nan))
        and bench_ret20 >= 0
    )
    return {
        "date": pd.Timestamp(dt),
        "theme": winner["theme"],
        "theme_rank": int(winner["theme_rank"]),
        "theme_score": float(winner["theme_score"]),
        "theme_stage": winner["lifecycle_state"],
        "etf": row["ETF"], "name": row.get("Name", row["ETF"]),
        "etf_rank": int(winner["etf_rank"]),
        "final_score": float(winner["final_score"]),
        "cross_score": int(winner["cross_score"]),
        "opportunity": int(winner["opportunity"]),
        "overheat": int(winner["overheat"]),
        "lead_score": float(winner["lead_score"]),
        "price_zone": winner["price_zone"],
        "rsi": float(row["RSI"]), "vr": float(row["VR"]),
        "rs20": float(winner["row"]["R20"] - bench_ret20),
        "dist20": float((row["Close"] / row["MA20"] - 1) * 100),
        "market_pass": market_pass,
        "trend_pass": bool(
            float(row.get("Close", np.nan)) > float(row.get("MA20", np.nan)) > float(row.get("MA60", np.nan))
            and float(row.get("R20", np.nan)) > 0
        ),
        "momvol_pass": bool(
            1.05 <= float(row.get("VR", np.nan)) <= 2.50
            and 50 <= float(row.get("RSI", np.nan)) <= 72
            and float(row.get("R5", np.nan)) > 0
        ),
        "C": bool(winner["final_score"] >= 60),
        "D": bool(winner["final_score"] >= 72 and winner["price_zone"] == "매수구간"),
        "DM": bool(winner["final_score"] >= 72 and winner["price_zone"] == "매수구간" and market_pass),
        "FINAL": bool(winner["final_score"] >= 72),
        # FINAL V2: 기존 FINAL 신호 중 추세가 유지되고 과열되지 않은 눌림 구간만 선택
        "FINAL_V2": bool(
            winner["final_score"] >= 72
            and float(row.get("Close", np.nan)) > float(row.get("MA20", np.nan)) > float(row.get("MA60", np.nan))
            and float(row.get("R20", np.nan)) > 0
            and -4.0 <= float((row.get("Close", np.nan) / row.get("MA20", np.nan) - 1) * 100) <= 2.5
            and 42.0 <= float(row.get("RSI", np.nan)) <= 68.0
            and 0.7 <= float(row.get("VR", np.nan)) <= 3.0
        ),
    }


def wf_trade_from_signal(data, sig, strategy):
    code = sig["etf"]
    d = data.get(code)
    if d is None or d.empty:
        return None
    dt = pd.Timestamp(sig["date"])
    pos = d.index.searchsorted(dt, side="right")
    if pos >= len(d):
        return None
    entry_i = pos
    exit_i = entry_i + WF_HOLD_DAYS - 1
    # 완전한 보유기간을 확보하지 못한 말기 신호는 성과에서 제외합니다.
    if exit_i >= len(d):
        return None
    entry_date = d.index[entry_i]
    exit_date = d.index[exit_i]
    entry = float(d.iloc[entry_i].get("Open", d.iloc[entry_i]["Close"]))
    exit_px = float(d.iloc[exit_i].get("Close", np.nan))
    if not np.isfinite(entry) or entry <= 0 or not np.isfinite(exit_px):
        return None
    ret = (exit_px / entry - 1) * 100
    net = ret - (WF_FEE + WF_SLIPPAGE) * 2 * 100
    return {
        "strategy": strategy,
        "signal_date": dt.date().isoformat(),
        "entry_date": entry_date.date().isoformat(),
        "exit_date": exit_date.date().isoformat(),
        "ETF": code,
        "ETF명": sig["name"],
        "테마": sig["theme"],
        "테마점수": round(sig["theme_score"], 2),
        "선행점수": round(sig["lead_score"], 2),
        "가격구간": sig["price_zone"],
        "시장통과": sig["market_pass"],
        "진입가": round(entry, 4),
        "청산가": round(exit_px, 4),
        "수익률": round(ret, 4),
        "비용차감후수익률": round(net, 4),
        "보유거래일": int(exit_i - entry_i + 1),
    }


def wf_make_trades(data, signals, strategy):
    candidates = [s for s in signals if s.get(strategy, False)]
    trades = []
    last_exit = None
    for s in sorted(candidates, key=lambda x: x["date"]):
        t = wf_trade_from_signal(data, s, strategy)
        if t is None:
            continue
        ed = pd.Timestamp(t["entry_date"])
        xd = pd.Timestamp(t["exit_date"])
        if last_exit is not None and ed <= last_exit:
            continue
        trades.append(t)
        last_exit = xd
    return pd.DataFrame(trades)


def wf_summary(trades):
    if trades is None or trades.empty:
        return {"거래수":0,"승률":0,"평균수익률":0,"누적복리":0,"MDD":0}
    r = trades["비용차감후수익률"].astype(float) / 100
    equity = (1 + r).cumprod()
    dd = equity / equity.cummax() - 1
    return {
        "거래수": int(len(trades)),
        "승률": float((r > 0).mean() * 100),
        "평균수익률": float(r.mean() * 100),
        "누적복리": float((equity.iloc[-1] - 1) * 100),
        "MDD": float(dd.min() * 100),
    }


def wf_annual(trades):
    if trades is None or trades.empty:
        return pd.DataFrame(columns=["연도","거래수","승률","평균수익률","누적복리"])
    x=trades.copy()
    x["연도"]=pd.to_datetime(x["entry_date"]).dt.year
    rows=[]
    for y,g in x.groupby("연도"):
        rr=g["비용차감후수익률"].astype(float)/100
        rows.append({"연도":int(y),"거래수":len(g),"승률":(rr>0).mean()*100,"평균수익률":rr.mean()*100,"누적복리":((1+rr).prod()-1)*100})
    return pd.DataFrame(rows).sort_values("연도")


def render_true_walk_forward():
    st.markdown('<div class="hero"><div class="hero-name">🧬 TRUE WALK-FORWARD VALIDATION</div><div class="hero-code">실제 ETF RADAR 미래테마 엔진을 과거 날짜별로 재생 · 다음 거래일 진입 · OOS 검증</div></div>', unsafe_allow_html=True)
    st.info("이 검증은 현재 앱의 THEME_LEXICON + 실시간 ETF MASTER + 테마점수 + 선행 ETF + 가격구간 로직을 사용합니다. 신호일 이후 가격은 신호 계산에 사용하지 않습니다. 단, 현재 ETF MASTER를 과거에 적용하므로 생존편향은 남습니다.")

    c1,c2,c3=st.columns(3)
    with c1:
        start=st.date_input("검증 시작일", date(2022,1,1), key="wf_start")
    with c2:
        end=st.date_input("검증 종료일", date.today(), key="wf_end")
    with c3:
        step=st.select_slider("신호 검사 간격", options=[1,3,5,10], value=1, key="wf_step", format_func=lambda x:"매일" if x==1 else f"{x}거래일마다")

    st.markdown("### 검증 기준")
    st.write("**C** = 미래테마 + 선행 ETF · **D** = C + 매수구간 · **D+M** = D + 시장환경 통과")
    run=st.button("🚀 TRUE WALK-FORWARD 실행", type="primary", use_container_width=True, key="wf_run")

    if run:
        if start >= end:
            st.error("시작일은 종료일보다 빨라야 합니다.")
            return
        with st.status("실제 앱 로직을 과거 날짜별로 재생하는 중...", expanded=True) as status:
            try:
                status.write("① 현재 ETF MASTER에서 테마별 ETF 후보 구성")
                universe, theme_members, codes = wf_build_universe()
                status.write(f"② 검증 ETF {len(codes)}개 가격 데이터 다운로드")
                data=wf_download_history(tuple(codes))
                data={k:v for k,v in data.items() if v is not None and not v.empty}
                if WF_BENCH not in data:
                    raise RuntimeError("KODEX 200(069500) 데이터를 가져오지 못했습니다.")
                status.write("③ 과거 날짜별 미래테마 → 선행 ETF → 가격구간 계산")
                bench=data[WF_BENCH]
                dates=bench.index[(bench.index>=pd.Timestamp(start))&(bench.index<=pd.Timestamp(end))]
                signals=[]
                for i,dt in enumerate(dates):
                    if i % int(step):
                        continue
                    s=wf_snapshot(data,theme_members,dt)
                    if s:
                        signals.append(s)
                if not signals:
                    raise RuntimeError("유효한 과거 신호가 없습니다. 기간을 늘리거나 검사 간격을 줄여주세요.")
                status.write("④ 다음 거래일 진입 + 60거래일 보유 시뮬레이션")
                trade_map={}
                for strategy in ["C","D","DM","FINAL"]:
                    trade_map[strategy]=wf_make_trades(data,signals,strategy)
                rows=[]
                for strategy,label in [("C","C · 미래테마선행"),("D","D · 미래테마선행가격"),("DM","D+M · 시장환경"),("FINAL","FINAL · 현재 최종타겟")]:
                    m=wf_summary(trade_map[strategy])
                    m["전략"]=label
                    rows.append(m)
                summary=pd.DataFrame(rows)[["전략","거래수","승률","평균수익률","누적복리","MDD"]]
                sigdf=pd.DataFrame(signals)
                oos=sigdf[pd.to_datetime(sigdf["date"]).dt.year>=WF_OOS_YEAR].copy()
                alltrades=pd.concat([trade_map[x] for x in ["C","D","DM","FINAL"]],ignore_index=True)
                # 화면의 OOS 연도별 표에는 OOS 신호로 시작한 거래만 포함합니다.
                oos_trade_map={}
                for x in ["C","D","DM","FINAL"]:
                    tx=trade_map[x].copy()
                    if not tx.empty and "signal_date" in tx.columns:
                        tx=tx[pd.to_datetime(tx["signal_date"]).dt.year>=WF_OOS_YEAR]
                    oos_trade_map[x]=tx
                annual=pd.concat([wf_annual(oos_trade_map[x]).assign(전략=x) for x in ["C","D","DM","FINAL"]],ignore_index=True)
                st.session_state["wf_result"]={"summary":summary,"signals":sigdf,"trades":alltrades,"annual":annual,"oos":oos}
                status.update(label="TRUE WALK-FORWARD 완료",state="complete",expanded=False)
            except Exception as ex:
                status.update(label="검증 실패",state="error",expanded=True)
                st.exception(ex)
                return

    result=st.session_state.get("wf_result")
    if not result:
        return
    summary=result["summary"]
    st.markdown("### 검증 결과")
    st.dataframe(summary, use_container_width=True, hide_index=True)
    c1,c2,c3=st.columns(3)
    with c1:
        st.metric("신호 수", len(result["signals"]))
    with c2:
        st.metric("OOS 신호 수", len(result["oos"]))
    with c3:
        st.metric("전체 거래 수", len(result["trades"]))

    st.markdown("### OOS 연도별 결과")
    st.dataframe(result["annual"],use_container_width=True,hide_index=True)
    st.markdown("### 최근 생성된 신호")
    st.dataframe(result["signals"].sort_values("date",ascending=False).head(30),use_container_width=True,hide_index=True)

    files={
        "TRUE_WALK_FORWARD_SUMMARY.csv":result["summary"],
        "TRUE_WALK_FORWARD_SIGNALS.csv":result["signals"],
        "TRUE_WALK_FORWARD_TRADES.csv":result["trades"],
        "TRUE_WALK_FORWARD_ANNUAL.csv":result["annual"],
        "TRUE_WALK_FORWARD_OOS.csv":result["oos"],
    }
    st.markdown("### CSV 결과 다운로드")
    cols=st.columns(3)
    for i,(name,df) in enumerate(files.items()):
        with cols[i%3]:
            st.download_button(f"📥 {name}",df.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig"),file_name=name,mime="text/csv",use_container_width=True,key="wf_dl_"+name)



# ============================================================
# FINAL VALIDATION LAB
# 매일 신호 + 보유기간별 + 조건 기여도 + OOS
# ============================================================

WF_HORIZONS = [5, 10, 20, 40, 60]


def wf_trade_horizon(data, sig, strategy, hold_days):
    code = sig.get("etf")
    d = data.get(code)
    if d is None or d.empty:
        return None
    dt = pd.Timestamp(sig["date"])
    pos = d.index.searchsorted(dt, side="right")
    if pos >= len(d):
        return None
    entry_i = pos
    exit_i = entry_i + int(hold_days) - 1
    # 검증 종료 전에 완전한 보유기간이 끝나지 않는 신호는 제외합니다.
    if exit_i >= len(d):
        return None
    entry_date = d.index[entry_i]
    exit_date = d.index[exit_i]
    entry = float(d.iloc[entry_i].get("Open", d.iloc[entry_i].get("Close", np.nan)))
    exit_px = float(d.iloc[exit_i].get("Close", np.nan))
    if not np.isfinite(entry) or entry <= 0 or not np.isfinite(exit_px):
        return None
    gross = (exit_px / entry - 1) * 100
    net = gross - (WF_FEE + WF_SLIPPAGE) * 2 * 100
    return {
        "strategy": strategy, "보유기간": int(hold_days),
        "signal_date": dt.date().isoformat(),
        "entry_date": entry_date.date().isoformat(),
        "exit_date": exit_date.date().isoformat(),
        "ETF": code, "ETF명": sig.get("name", code), "테마": sig.get("theme", ""),
        "테마점수": round(float(sig.get("theme_score", 0)), 2),
        "선행점수": round(float(sig.get("lead_score", 0)), 2),
        "가격구간": sig.get("price_zone", ""),
        "시장통과": bool(sig.get("market_pass", False)),
        "진입가": round(entry, 4), "청산가": round(exit_px, 4),
        "수익률": round(gross, 4), "비용차감후수익률": round(net, 4),
        "보유거래일": int(exit_i-entry_i+1),
    }


def wf_make_trades_horizon(data, signals, strategy, hold_days):
    candidates = [x for x in signals if x.get(strategy, False)]
    trades=[]; last_exit=None
    for sig in sorted(candidates, key=lambda x: x["date"]):
        t=wf_trade_horizon(data, sig, strategy, hold_days)
        if t is None: continue
        ed=pd.Timestamp(t["entry_date"]); xd=pd.Timestamp(t["exit_date"])
        if last_exit is not None and ed <= last_exit: continue
        trades.append(t); last_exit=xd
    return pd.DataFrame(trades)


def wf_add_final_strategy_flags(signals):
    """D를 기준으로 필터의 독립/복합 기여도를 계산한다."""
    out=[]
    for s in signals:
        x=dict(s)
        d=bool(x.get("D",False)); t=bool(x.get("trend_pass",False)); mv=bool(x.get("momvol_pass",False)); m=bool(x.get("market_pass",False))
        x["BASE_D"]=d
        x["D+TREND"]=d and t
        x["D+MOMVOL"]=d and mv
        x["D+MARKET"]=d and m
        x["D+T+MV"]=d and t and mv
        x["D+T+M"]=d and t and m
        x["D+MV+M"]=d and mv and m
        x["D+T+MV+M"]=d and t and mv and m
        out.append(x)
    return out


def wf_final_summary(trades):
    if trades is None or trades.empty:
        return {"거래수":0,"승률":0,"평균수익률":0,"누적복리":0,"MDD":0}
    r=pd.to_numeric(trades["비용차감후수익률"],errors="coerce").dropna()/100
    if r.empty: return {"거래수":0,"승률":0,"평균수익률":0,"누적복리":0,"MDD":0}
    eq=(1+r).cumprod(); dd=eq/eq.cummax()-1
    return {"거래수":int(len(r)),"승률":float((r>0).mean()*100),"평균수익률":float(r.mean()*100),"누적복리":float((eq.iloc[-1]-1)*100),"MDD":float(dd.min()*100)}



# ============================================================
# FORWARD + ML FUTURE PROBABILITY
# 최종검증 내부에서만 사용. 과거 T의 정보로 T+20/T+40/T+60 결과를 학습합니다.
# sklearn이 없으면 규칙 기반 Forward 결과만 표시하며 앱은 정상 동작합니다.
# ============================================================

def _forward_theme_feature(rows, benchmark_ret20=0.0):
    """Forward/ML용 9개 feature를 항상 유한한 범위로 반환합니다."""
    if not rows:
        return None
    def av(k):
        vals=[]
        for x in rows:
            v=safe_float(x.get(k),0.0)
            if np.isfinite(v):
                vals.append(v)
        return float(np.mean(vals)) if vals else 0.0
    arr=np.asarray([
        av("ret5"), av("ret20"), av("ret60"), av("vr"), av("rsi"),
        av("ma60_gap"), av("breadth"), av("accel"), av("rs20")
    ],dtype=np.float64)
    # 학습 실패를 유발하는 NaN/inf/초대형 값 최종 방어
    arr=np.nan_to_num(arr,nan=0.0,posinf=0.0,neginf=0.0)
    arr=np.clip(arr,-1e6,1e6)
    return arr


def _historical_theme_sample(theme, info, horizon=20, max_samples=18):
    """현재 테마 구성 ETF를 사용하되 각 과거 시점의 가격만으로 feature/label을 생성."""
    members=info.get("rows",[])[:8]
    if len(members)<2: return []
    series={}
    for m in members:
        df=load_price_data(m.get("code"))
        if df is not None and not df.empty and len(df)>=150:
            series[m.get("code")]=calculate_indicators(df)
    if len(series)<2: return []
    bench_code=WF_BENCH if 'WF_BENCH' in globals() else '069500'
    bdf=series.get(bench_code)
    if bdf is None:
        bdf=load_price_data(bench_code)
        if bdf is not None and not bdf.empty: bdf=calculate_indicators(bdf)
    if bdf is None or bdf.empty: return []
    common=sorted(set.intersection(*[set(x.index) for x in series.values()]))
    common=[x for x in common if x in bdf.index]
    if len(common)<horizon+80: return []
    # 20거래일 간격으로 표본화하여 계산량을 제한
    idxs=list(range(80, len(common)-horizon, max(10, len(common)//max_samples)))
    samples=[]
    for pos in idxs[-max_samples:]:
        dt=common[pos]
        rows=[]
        for code,d in series.items():
            if dt not in d.index: continue
            r=d.loc[dt]
            c=safe_float(r.get('Close'),0); ma20=safe_float(r.get('MA20'),c); ma60=safe_float(r.get('MA60'),c)
            ret20=safe_float(r.get('RET20'),0); ret60=safe_float(r.get('RET60'),0)
            ret5=safe_float(r.get('RET5'),0); vr=safe_float(r.get('VOL_RATIO'),1); rsi=safe_float(r.get('RSI14'),50)
            rows.append({'ret5':ret5,'ret20':ret20,'ret60':ret60,'vr':vr,'rsi':rsi,
                         'ma60_gap':((c/ma60-1)*100 if ma60 else 0),'breadth':100 if c>=ma20 else 0,
                         'accel':ret5-ret20/4,'rs20':ret20-safe_float(bdf.loc[dt].get('RET20'),0)})
        if len(rows)<2: continue
        feat=_forward_theme_feature(rows)
        future_rows=[]
        future_dt=common[pos+horizon]
        for code,d in series.items():
            if future_dt not in d.index: continue
            r=d.loc[future_dt]
            future_rows.append(safe_float(r.get('RET20'),0)-safe_float(bdf.loc[future_dt].get('RET20'),0))
        if not future_rows: continue
        # 미래 20일 상대강도 평균이 +3% 이상이면 '미래 강화' 1
        label=1 if float(np.mean(future_rows))>=3.0 else 0
        samples.append((feat,label))
    return samples


def run_forward_ml():
    engine=build_future_theme_engine()
    details=engine.get('details',{})
    rows=[]
    allX=[]; allY=[]; meta=[]
    # 현재 상위 테마를 기준으로 과거 Forward 샘플 생성
    for theme,info in list(details.items())[:10]:
        for horizon in (20,40,60):
            samples=_historical_theme_sample(theme,info,horizon=horizon,max_samples=12)
            if not samples: continue
            for x,y in samples:
                allX.append(x); allY.append(y); meta.append((theme,horizon))
    result=[]
    try:
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.linear_model import LogisticRegression
        sklearn_ok=True
    except Exception:
        sklearn_ok=False
    if sklearn_ok and len(allX)>=20 and len(set(allY))>=2:
        # ML 직전 전체 학습행렬을 다시 정제합니다.
        X=np.asarray(allX,dtype=np.float64)
        y=np.asarray(allY,dtype=np.int64)
        finite_mask=np.isfinite(X).all(axis=1) & np.isfinite(y)
        X=X[finite_mask]
        y=y[finite_mask]
        X=np.nan_to_num(X,nan=0.0,posinf=0.0,neginf=0.0)
        X=np.clip(X,-1e6,1e6)
        if len(X)<20 or len(np.unique(y))<2:
            sklearn_ok=False
        else:
            model=Pipeline([('scaler',StandardScaler()),('lr',LogisticRegression(max_iter=1000,class_weight='balanced'))])
            model.fit(X,y)
            for theme,info in details.items():
                f=_forward_theme_feature(info.get('rows',[]),safe_float(engine.get('benchmark',{}).get('ret20'),0))
                if f is None or not np.isfinite(f).all():
                    continue
                f=np.nan_to_num(f,nan=0.0,posinf=0.0,neginf=0.0)
                f=np.clip(f,-1e6,1e6)
                prob=float(model.predict_proba([f])[0,1]*100)
                # 20/40/60 학습 샘플을 합쳐 현재 테마의 미래 강화 확률을 계산합니다.
                result.append({'테마':theme,'현재점수':round(safe_float(info.get('score')),1),'ML미래강화확률':round(prob,1),
                               '판정':'🔥 높음' if prob>=70 else '🟢 양호' if prob>=55 else '🟡 보통' if prob>=45 else '🔴 낮음'})
            return pd.DataFrame(result), {'sklearn':True,'samples':len(X),'positive_rate':float(np.mean(y)*100)}
    # sklearn 미설치 또는 표본 부족: ML 대신 Forward 규칙 확률을 표시
    for theme,info in details.items():
        score=safe_float(info.get('score')); life=safe_float(info.get('lifecycle',{}).get('score'))
        p=float(np.clip(score*.65+life*.35,0,100))
        result.append({'테마':theme,'현재점수':round(score,1),'ML미래강화확률':round(p,1),
                       '판정':'⚠️ ML 미실행' if not sklearn_ok else '⚠️ 표본부족'})
    return pd.DataFrame(result), {'sklearn':False,'samples':len(allX),'positive_rate':float(np.mean(allY)*100) if allY else 0}


def render_forward_ml_panel():
    with st.expander('🧠 Forward + ML 미래테마 검증', expanded=False):
        st.caption('과거 T 시점의 정보만 사용해 T+20/T+40/T+60의 테마 강화 여부를 학습합니다. 현재 앱의 미래테마 판단을 대체하지 않고 보조합니다.')
        if st.button('🚀 Forward + ML 실행 / 갱신', type='primary', use_container_width=True, key='forward_ml_run'):
            with st.spinner('과거 Forward 샘플을 구성하고 ML을 학습하는 중...'):
                try:
                    out,meta=run_forward_ml()
                    st.session_state['forward_ml_result']=out
                    st.session_state['forward_ml_meta']=meta
                except Exception as ex:
                    st.error(f'Forward + ML 실행 실패: {ex}')
        out=st.session_state.get('forward_ml_result')
        meta=st.session_state.get('forward_ml_meta')
        if out is None:
            st.info('버튼을 누르면 과거 Forward 결과를 기반으로 미래테마 강화 확률을 계산합니다.')
            return
        if meta:
            a,b,c=st.columns(3)
            a.metric('학습 표본',f"{meta.get('samples',0):,}")
            b.metric('ML 사용', '예' if meta.get('sklearn') else '아니오')
            c.metric('강화 표본 비율',f"{meta.get('positive_rate',0):.1f}%")
        st.dataframe(out.sort_values(['ML미래강화확률','현재점수'],ascending=False),use_container_width=True,hide_index=True)
        st.caption('주의: 현재 ETF MASTER를 과거에 적용하므로 생존편향은 남습니다. 확률은 투자수익 보장이 아니라 후보 우선순위용입니다.')


# ============================================================
# 독립 백테스트 엔진
# 신호 생성은 기존 과거 스냅샷을 사용하되, 체결/비용/포트폴리오 곡선/벤치마크 계산은 별도로 수행
# ============================================================

def independent_net_return(entry, exit_price, fee=WF_FEE, slippage=WF_SLIPPAGE):
    """양방향 비용을 매수/매도 가격에 적용한 순수익률(소수)."""
    entry = safe_float(entry, np.nan)
    exit_price = safe_float(exit_price, np.nan)
    if not np.isfinite(entry) or not np.isfinite(exit_price) or entry <= 0 or exit_price <= 0:
        return np.nan
    buy_cost = entry * (1.0 + slippage) * (1.0 + fee)
    sell_net = exit_price * (1.0 - slippage) * (1.0 - fee)
    return sell_net / buy_cost - 1.0


def independent_forward_samples(data, signals, strategy, horizons=(5, 20, 60), fee=WF_FEE, slippage=WF_SLIPPAGE, end_date=None):
    """신호 이후 정방향 수익률 표본. 손절 변형은 포트폴리오 체결 결과로만 비교한다."""
    if strategy in ("FINAL_SL10", "FINAL_V2_SL10"):
        return pd.DataFrame()
    bench = data.get(WF_BENCH)
    if bench is None or bench.empty:
        return pd.DataFrame()
    end_ts = pd.Timestamp(end_date) if end_date is not None else None
    rows = []
    for sig in sorted(signals, key=lambda x: pd.Timestamp(x.get('date'))):
        if not bool(sig.get(strategy, False)):
            continue
        signal_date = pd.Timestamp(sig['date'])
        code = sig.get('etf')
        d = data.get(code)
        if d is None or d.empty:
            continue
        epos = d.index.searchsorted(signal_date, side='right')
        bpos = bench.index.searchsorted(signal_date, side='right')
        if epos >= len(d) or bpos >= len(bench):
            continue
        for hold in horizons:
            exi = epos + int(hold) - 1
            bxi = bpos + int(hold) - 1
            if exi >= len(d) or bxi >= len(bench):
                continue
            entry_date = pd.Timestamp(d.index[epos])
            exit_date = pd.Timestamp(d.index[exi])
            b_entry_date = pd.Timestamp(bench.index[bpos])
            b_exit_date = pd.Timestamp(bench.index[bxi])
            if end_ts is not None and (exit_date > end_ts or b_exit_date > end_ts):
                continue
            entry = safe_float(d.iloc[epos].get('Open', d.iloc[epos].get('Close', np.nan)), np.nan)
            exit_px = safe_float(d.iloc[exi].get('Close', np.nan), np.nan)
            b_entry = safe_float(bench.iloc[bpos].get('Open', bench.iloc[bpos].get('Close', np.nan)), np.nan)
            b_exit = safe_float(bench.iloc[bxi].get('Close', np.nan), np.nan)
            # ETF/benchmark 모두 ETF 단위로 검증된 가격 기준을 사용합니다.
            entry_adj = entry * independent_adjustment_factor(d, entry_date)
            exit_adj = exit_px * independent_adjustment_factor(d, exit_date)
            b_entry_adj = b_entry * independent_adjustment_factor(bench, b_entry_date)
            b_exit_adj = b_exit * independent_adjustment_factor(bench, b_exit_date)
            ret = independent_net_return(entry_adj, exit_adj, fee, slippage)
            bret = independent_net_return(b_entry_adj, b_exit_adj, fee, slippage)
            if not np.isfinite(ret) or not np.isfinite(bret):
                continue
            rows.append({
                '신호일': signal_date.date().isoformat(), '진입일': entry_date.date().isoformat(),
                '청산일': exit_date.date().isoformat(), 'ETF': code, 'ETF명': sig.get('name', code),
                '전략': strategy, '최종점수': safe_float(sig.get('final_score'), np.nan),
                '보유기간': int(hold), 'ETF순수익률(%)': ret * 100,
                'KODEX200순수익률(%)': bret * 100, '초과수익률(%p)': (ret - bret) * 100,
                'ETF수익여부': bool(ret > 0), '벤치마크초과여부': bool(ret > bret),
            })
    return pd.DataFrame(rows)


def independent_adjustment_series_valid(frame):
    """ETF 단위로 Adj Close 데이터의 사용 가능 여부를 판정합니다.

    일부 날짜만 raw Close로 되돌리면 동일 ETF 안에서 가격 기준이 섞이므로,
    Adj Close에 0/음수/비수치 값 또는 비정상 조정계수가 하나라도 있으면
    해당 ETF 전체를 raw Close 기준으로 계산합니다.
    """
    if frame is None or frame.empty or "Adj Close" not in frame.columns or "Close" not in frame.columns:
        return False
    cached = frame.attrs.get("_independent_adj_valid")
    if cached is not None:
        return bool(cached)
    close = pd.to_numeric(frame["Close"], errors="coerce")
    adj = pd.to_numeric(frame["Adj Close"], errors="coerce")
    valid_close = close.notna() & np.isfinite(close) & (close > 0)
    valid_adj = adj.notna() & np.isfinite(adj) & (adj > 0)
    # 유효한 종가가 있는 행에 대해 조정가격이 모두 유효해야 합니다.
    valid = bool(valid_close.any() and valid_adj[valid_close].all())
    if valid:
        factor = adj[valid_close] / close[valid_close]
        # 비정상적인 조정계수는 자동 보정하지 않고 Adj Close 전체를 배제합니다.
        valid = bool(np.isfinite(factor).all() and (factor > 0).all() and (factor <= 10).all())
    frame.attrs["_independent_adj_valid"] = valid
    return valid


def independent_close_series(frame):
    """유효한 Adj Close가 ETF 전체에서 확인될 때만 조정종가를 반환합니다."""
    if frame is None or frame.empty or "Close" not in frame.columns:
        return pd.Series(dtype=float)
    if independent_adjustment_series_valid(frame):
        return pd.to_numeric(frame["Adj Close"], errors="coerce")
    return pd.to_numeric(frame["Close"], errors="coerce")


def independent_adjustment_factor(frame, dt):
    """ETF 단위 검증을 통과한 경우에만 Adj Close / Close 조정계수를 반환합니다."""
    if not independent_adjustment_series_valid(frame):
        return 1.0
    pos = frame.index.searchsorted(pd.Timestamp(dt), side="right") - 1
    if pos < 0 or pos >= len(frame) or pd.Timestamp(frame.index[pos]) != pd.Timestamp(dt):
        return 1.0
    close = safe_float(frame.iloc[pos].get("Close", np.nan), np.nan)
    adj = safe_float(frame.iloc[pos].get("Adj Close", np.nan), np.nan)
    if np.isfinite(close) and close > 0 and np.isfinite(adj) and adj > 0:
        return adj / close
    return 1.0


def independent_portfolio_backtest(data, signals, strategy='FINAL', hold_days=20, start_date=None, end_date=None, fee=WF_FEE, slippage=WF_SLIPPAGE):
    """독립 포트폴리오 시뮬레이터. 거래수익과 일별 MDD에 동일한 조정가격 기준을 적용한다."""
    signal_strategy = strategy
    stop_loss_pct = None
    if strategy == "FINAL_SL10":
        signal_strategy, stop_loss_pct = "FINAL", 0.10
    elif strategy == "FINAL_V2_SL10":
        signal_strategy, stop_loss_pct = "FINAL_V2", 0.10
    bench = data.get(WF_BENCH)
    if bench is None or bench.empty:
        return pd.DataFrame(), pd.DataFrame(), {}
    start_ts = pd.Timestamp(start_date) if start_date is not None else bench.index.min()
    end_ts = pd.Timestamp(end_date) if end_date is not None else bench.index.max()
    calendar = bench.index[(bench.index >= start_ts) & (bench.index <= end_ts)]
    if len(calendar) < 2:
        return pd.DataFrame(), pd.DataFrame(), {}

    candidates = [x for x in signals if bool(x.get(signal_strategy, False)) and start_ts <= pd.Timestamp(x['date']) <= end_ts]
    candidates.sort(key=lambda x: pd.Timestamp(x['date']))
    planned = []
    last_exit = None
    for sig in candidates:
        d = data.get(sig.get('etf'))
        if d is None or d.empty:
            continue
        signal_date = pd.Timestamp(sig['date'])
        entry_i = d.index.searchsorted(signal_date, side='right')
        exit_i = entry_i + int(hold_days) - 1
        if entry_i >= len(d) or exit_i >= len(d):
            continue
        entry_date = pd.Timestamp(d.index[entry_i])
        exit_date = pd.Timestamp(d.index[exit_i])
        if entry_date < calendar[0] or exit_date > calendar[-1]:
            continue
        if last_exit is not None and entry_date <= last_exit:
            continue
        entry = safe_float(d.iloc[entry_i].get('Open', d.iloc[entry_i].get('Close', np.nan)), np.nan)
        exit_px = safe_float(d.iloc[exit_i].get('Close', np.nan), np.nan)
        exit_reason = '기간청산'
        actual_exit_i = exit_i
        # 손절 변형은 일중 저가가 진입가 대비 -10%에 닿으면 청산합니다.
        # 시가가 손절선을 갭 하락으로 통과한 경우 손절가가 아닌 시가로 체결 가정합니다.
        if stop_loss_pct is not None and np.isfinite(entry) and entry > 0:
            stop_price = entry * (1.0 - stop_loss_pct)
            for j in range(entry_i, exit_i + 1):
                day_row = d.iloc[j]
                day_low = safe_float(day_row.get('Low', np.nan), np.nan)
                day_open = safe_float(day_row.get('Open', np.nan), np.nan)
                if np.isfinite(day_low) and day_low <= stop_price:
                    actual_exit_i = j
                    exit_px = day_open if np.isfinite(day_open) and day_open < stop_price else stop_price
                    exit_reason = '손절 -10%'
                    break
        exit_date = pd.Timestamp(d.index[actual_exit_i])
        if exit_date > calendar[-1]:
            continue
        entry_factor = independent_adjustment_factor(d, entry_date)
        exit_factor = independent_adjustment_factor(d, exit_date)
        entry_adjusted = entry * entry_factor
        exit_adjusted = exit_px * exit_factor
        net = independent_net_return(entry_adjusted, exit_adjusted, fee, slippage)
        if not np.isfinite(net):
            continue
        planned.append({'신호일': signal_date, '진입일': entry_date, '청산일': exit_date, 'ETF': sig.get('etf'),
                        'ETF명': sig.get('name', sig.get('etf')), '테마': sig.get('theme', ''), '최종점수': safe_float(sig.get('final_score'), np.nan),
                        '진입가': entry, '청산가': exit_px, '진입조정가': entry_adjusted, '청산조정가': exit_adjusted,
                        '조정가격사용': bool(independent_adjustment_series_valid(d)), '순수익률(%)': net * 100,
                        '청산사유': exit_reason, '보유거래일': int(actual_exit_i - entry_i + 1)})
        last_exit = exit_date

    trades = pd.DataFrame(planned)
    equity = 1.0
    trade_idx = 0
    curve_rows = []
    for day in calendar:
        # 신호가 없거나 포지션 진입 전이면 현금 보유, 포지션 기간에는 종가 기준 평가
        if trade_idx < len(planned):
            tr = planned[trade_idx]
            if tr['진입일'] <= day <= tr['청산일']:
                d = data.get(tr['ETF'])
                pos = d.index.searchsorted(day)
                if pos < len(d) and pd.Timestamp(d.index[pos]) == day:
                    close_px = safe_float(d.iloc[pos].get('Close', np.nan), np.nan)
                    # Use the same adjusted-price basis as trade returns so dividends/
                    # distributions are reflected consistently in daily MDD.
                    day_factor = independent_adjustment_factor(d, day)
                    mark_px = close_px * day_factor if np.isfinite(close_px) else np.nan
                    # On the actual exit date, mark the curve at the simulated fill,
                    # not at the day's close (important for stop-loss/gap exits).
                    if pd.Timestamp(day) == pd.Timestamp(tr['청산일']):
                        mark_px = safe_float(tr.get('청산조정가', np.nan), mark_px)
                    entry_basis = safe_float(tr.get('진입조정가', np.nan), np.nan)
                    mark_ret = independent_net_return(entry_basis, mark_px, fee, slippage)
                    value = equity * (1.0 + mark_ret) if np.isfinite(mark_ret) else equity
                else:
                    value = equity
                curve_rows.append({'날짜': day, '자산지수': value})
                if day == tr['청산일']:
                    final_ret = safe_float(tr['순수익률(%)'], 0.0) / 100.0
                    equity *= (1.0 + final_ret)
                    trade_idx += 1
                continue
        curve_rows.append({'날짜': day, '자산지수': equity})

    curve = pd.DataFrame(curve_rows)
    # 같은 기간 KODEX 200 매수 후 보유(비용 차감) 기준선
    b = bench.loc[(bench.index >= calendar[0]) & (bench.index <= calendar[-1])].copy()
    b_open = safe_float(b.iloc[0].get('Open', b.iloc[0].get('Close', np.nan)), np.nan)
    b_factor = independent_adjustment_factor(bench, b.index[0])
    b_open_adjusted = b_open * b_factor
    b_close = independent_close_series(bench).reindex(b.index)
    bvals = (b_close * (1.0 - slippage) * (1.0 - fee)) / (b_open_adjusted * (1.0 + slippage) * (1.0 + fee))
    benchmark_curve = pd.DataFrame({'날짜': b.index, '자산지수': bvals.values})
    if not benchmark_curve.empty:
        # Initial capital baseline is prior to the first close observation, so first-day
        # movement contributes to MDD as well as cumulative return.
        baseline = pd.DataFrame({'날짜': [pd.Timestamp(calendar[0]) - pd.Timedelta(days=1)], '자산지수': [1.0]})
        benchmark_curve = pd.concat([baseline, benchmark_curve], ignore_index=True)
    curve['고점'] = curve['자산지수'].cummax()
    curve['낙폭(%)'] = (curve['자산지수'] / curve['고점'] - 1.0) * 100
    benchmark_curve['고점'] = benchmark_curve['자산지수'].cummax()
    benchmark_curve['낙폭(%)'] = (benchmark_curve['자산지수'] / benchmark_curve['고점'] - 1.0) * 100

    def metrics(c, period_start=None):
        if c.empty:
            return {'누적수익률(%)': np.nan, 'CAGR(%)': np.nan, 'MDD(%)': np.nan}
        vals = pd.to_numeric(c['자산지수'], errors='coerce').dropna()
        if vals.empty:
            return {'누적수익률(%)': np.nan, 'CAGR(%)': np.nan, 'MDD(%)': np.nan}
        total = (float(vals.iloc[-1]) - 1.0) * 100
        start = pd.Timestamp(period_start) if period_start is not None else pd.Timestamp(c['날짜'].iloc[0])
        days = max(1, (pd.Timestamp(c['날짜'].iloc[-1]) - start).days)
        cagr = ((float(vals.iloc[-1]) ** (365.25 / days)) - 1.0) * 100 if float(vals.iloc[-1]) > 0 else -100.0
        mdd = float(pd.to_numeric(c['낙폭(%)'], errors='coerce').min()) if '낙폭(%)' in c else np.nan
        return {'누적수익률(%)': total, 'CAGR(%)': cagr, 'MDD(%)': mdd}

    strat_m = metrics(curve)
    bench_m = metrics(benchmark_curve, period_start=calendar[0])
    r = pd.to_numeric(trades.get('순수익률(%)', pd.Series(dtype=float)), errors='coerce').dropna()
    summary = {
        '전략': strategy, '보유기간': int(hold_days), '거래수': int(len(trades)),
        '승률(%)': float((r > 0).mean() * 100) if len(r) else np.nan,
        '평균거래수익(%)': float(r.mean()) if len(r) else np.nan,
        **strat_m, 'KODEX200 누적수익률(%)': bench_m['누적수익률(%)'],
        'KODEX200 MDD(%)': bench_m['MDD(%)'],
        '벤치마크대비 초과수익률(%p)': strat_m['누적수익률(%)'] - bench_m['누적수익률(%)'],
    }
    return trades, curve, summary



def independent_export_price_history(data):
    """백테스트에 실제 사용한 일별 가격·지표를 재현 가능한 CSV로 내보냅니다."""
    frames = []
    coverage = []
    for code, frame in (data or {}).items():
        if frame is None or frame.empty:
            continue
        d = frame.copy()
        d.index = pd.to_datetime(d.index, errors="coerce")
        d = d.loc[~d.index.isna()].copy()
        if d.empty:
            continue
        d.index.name = "날짜"
        d = d.reset_index()
        d.insert(0, "ETF코드", str(code).zfill(6))
        # 원시 OHLCV와 백테스트 신호 계산에 사용된 지표를 함께 보존
        frames.append(d)
        coverage.append({
            "ETF코드": str(code).zfill(6),
            "시작일": pd.to_datetime(frame.index).min().date().isoformat(),
            "종료일": pd.to_datetime(frame.index).max().date().isoformat(),
            "가격행수": int(len(frame)),
            "필수가격열": all(c in frame.columns for c in ["Open", "High", "Low", "Close", "Volume"]),
            "지표열": ", ".join(str(c) for c in frame.columns if c not in ["Open", "High", "Low", "Close", "Volume"]),
        })
    history = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if not history.empty:
        history["날짜"] = pd.to_datetime(history["날짜"], errors="coerce").dt.strftime("%Y-%m-%d")
        history = history.sort_values(["ETF코드", "날짜"]).reset_index(drop=True)
    return history, pd.DataFrame(coverage)


def independent_export_theme_universe(universe, theme_members):
    """현재 MASTER에서 과거 재생에 사용한 테마 구성의 추적 기록."""
    rows = []
    for theme, members in (theme_members or {}).items():
        for code, name, hits in members:
            rows.append({
                "테마": theme,
                "ETF코드": str(code).zfill(6),
                "ETF명": str(name),
                "키워드일치수": int(hits) if pd.notna(hits) else 0,
                "유니버스기준": "현재 ETF MASTER",
            })
    return pd.DataFrame(rows)

def render_independent_backtest():
    st.markdown('<div class="hero"><div class="hero-name">🧪 독립 과거 백테스트</div><div class="hero-code">C / D / D+M / FINAL · FINAL V2 · 손절 비교 · 비용 반영 · 일별 MDD</div></div>', unsafe_allow_html=True)
    st.warning('현재 ETF MASTER를 과거에 적용하는 한계는 남습니다. 정방향 표본은 보유기간이 서로 겹칠 수 있어 예측력 평가용이며, 투자 가능한 포트폴리오 성과는 비중복 포지션 시뮬레이션으로 별도 계산합니다.')
    st.info('거래수익과 일별 자산곡선은 Adj Close 조정계수를 동일하게 적용합니다. 단, 현재 ETF MASTER를 과거에 적용하는 생존편향은 남습니다. 선택한 전략은 같은 과거 날짜·ETF 후보군·수수료·슬리피지로 비교합니다. FINAL V2는 FINAL 신호 중 추세 유지, MA20 이격률 -4~+2.5%, RSI 42~68, 거래량비 0.7~3.0 조건을 추가합니다. 손절10% 변형은 일중 저가가 손절선에 닿으면 청산하며, 갭 하락 시 시가 체결로 가정합니다.')
    c1,c2,c3=st.columns(3)
    with c1: start=st.date_input('백테스트 시작일', date(2020,1,1), key='ib_start')
    with c2: end=st.date_input('백테스트 종료일', date.today(), key='ib_end')
    with c3: oos_year=st.number_input('OOS 시작연도', min_value=2018, max_value=2030, value=2024, step=1, key='ib_oos')
    strategy_labels={
        'C · 미래테마+선행':'C',
        'D · 매수구간 추가':'D',
        'D+M · 시장환경 추가':'DM',
        'FINAL · 기존 최종타겟':'FINAL',
        'FINAL + 손절10%':'FINAL_SL10',
        'FINAL V2 · 완화 눌림매수':'FINAL_V2',
        'FINAL V2 + 손절10%':'FINAL_V2_SL10',
    }
    selected_labels=st.multiselect(
        '비교할 전략',
        options=list(strategy_labels.keys()),
        default=list(strategy_labels.keys()),
        key='ib_strategies_v2',
    )
    strategies=[strategy_labels[label] for label in selected_labels]
    hold=st.selectbox('포트폴리오 보유기간(거래일)', options=[5,10,20,40,60], index=2, key='ib_hold')
    c4,c5=st.columns(2)
    with c4: fee_pct=st.number_input('편도 수수료(%)', min_value=0.0, max_value=1.0, value=0.10, step=0.01, key='ib_fee')
    with c5: slip_pct=st.number_input('편도 슬리피지(%)', min_value=0.0, max_value=1.0, value=0.05, step=0.01, key='ib_slip')
    if st.button('전략 비교 실행', type='primary', use_container_width=True, key='ib_run'):
        if start >= end:
            st.error('시작일은 종료일보다 빨라야 합니다.')
        elif not strategies:
            st.error('비교할 전략을 하나 이상 선택해 주세요.')
        else:
            fee=fee_pct/100.0; slip=slip_pct/100.0
            with st.status('전략별 독립 백테스트 실행 중...', expanded=True) as status:
                try:
                    status.write('① 현재 ETF MASTER를 기준으로 과거 재생 대상 구성')
                    universe, theme_members, codes=wf_build_universe()
                    status.write(f'② {len(codes)}개 ETF와 KODEX 200 가격 데이터 확보')
                    data=wf_download_history(tuple(codes))
                    data={k:v for k,v in data.items() if v is not None and not v.empty}
                    if WF_BENCH not in data:
                        raise RuntimeError('KODEX 200(069500) 데이터를 가져오지 못했습니다.')
                    bench=data[WF_BENCH]
                    dates=bench.index[(bench.index>=pd.Timestamp(start))&(bench.index<=pd.Timestamp(end))]
                    signals=[]
                    for dt in dates:
                        snap=wf_snapshot(data,theme_members,dt)
                        if snap:
                            signals.append(snap)
                    if not signals:
                        raise RuntimeError('유효한 신호가 없습니다. 시작일을 더 앞당기거나 종료일을 확인해 주세요.')
                    signals=wf_add_final_strategy_flags(signals)
                    status.write(f'③ 공통 과거 신호 {len(signals):,}개 생성')
                    oos_start=max(pd.Timestamp(start),pd.Timestamp(f'{int(oos_year)}-01-01'))
                    forward_rows=[]; sample_frames=[]; portfolio_rows=[]; trade_frames=[]; curve_frames=[]
                    for strategy in strategies:
                        status.write(f'④ {strategy} 전략의 정방향 표본 및 포트폴리오 계산')
                        samples=independent_forward_samples(data, signals, strategy, horizons=(5,10,20,40,60), fee=fee, slippage=slip, end_date=end)
                        if not samples.empty:
                            samples['구간']=np.where(pd.to_datetime(samples['신호일'])>=oos_start, f'OOS {int(oos_year)}+', '전체')
                            samples['전략']=strategy
                            sample_frames.append(samples.copy())
                            for period, group in [('전체', samples), (f'OOS {int(oos_year)}+', samples[pd.to_datetime(samples['신호일'])>=oos_start])]:
                                for horizon,g in group.groupby('보유기간'):
                                    forward_rows.append({'전략':strategy,'구간':period,'보유기간':int(horizon),'표본수':len(g),
                                        '평균ETF수익률(%)':g['ETF순수익률(%)'].mean(),'중앙ETF수익률(%)':g['ETF순수익률(%)'].median(),
                                        '수익표본비율(%)':g['ETF수익여부'].mean()*100,'평균KODEX200수익률(%)':g['KODEX200순수익률(%)'].mean(),
                                        '평균초과수익률(%p)':g['초과수익률(%p)'].mean(),'벤치마크초과비율(%)':g['벤치마크초과여부'].mean()*100})
                        for period, lo, hi, sig_subset in [
                            ('전체', pd.Timestamp(start), pd.Timestamp(end), signals),
                            (f'OOS {int(oos_year)}+', oos_start, pd.Timestamp(end), [x for x in signals if pd.Timestamp(x['date'])>=oos_start]),
                        ]:
                            tr, curve, summary=independent_portfolio_backtest(data,sig_subset,strategy,hold,lo,hi,fee,slip)
                            portfolio_rows.append({'구간':period, **summary})
                            if not tr.empty:
                                tr=tr.copy(); tr['구간']=period; tr['전략']=strategy; trade_frames.append(tr)
                            if not curve.empty:
                                curve=curve.copy(); curve['구간']=period; curve['전략']=strategy
                                curve['시리즈']=strategy+' · '+period; curve_frames.append(curve)
                    forward_summary=pd.DataFrame(forward_rows)
                    portfolio_summary=pd.DataFrame(portfolio_rows)
                    portfolio_trades=pd.concat(trade_frames,ignore_index=True) if trade_frames else pd.DataFrame()
                    all_samples=pd.concat(sample_frames,ignore_index=True) if sample_frames else pd.DataFrame()
                    curves=pd.concat(curve_frames,ignore_index=True) if curve_frames else pd.DataFrame()
                    price_history, price_coverage = independent_export_price_history(data)
                    theme_universe_export = independent_export_theme_universe(universe, theme_members)

                    # 모든 결과 파일을 같은 실행 ID로 묶어 서로 다른 실행의 CSV가 섞이는 문제를 방지합니다.
                    run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
                    run_frames = {
                        'portfolio_summary': portfolio_summary,
                        'forward_summary': forward_summary,
                        'samples': all_samples,
                        'trades': portfolio_trades,
                        'curves': curves,
                        'signals': pd.DataFrame(signals),
                        'price_history': price_history,
                        'price_coverage': price_coverage,
                        'theme_universe': theme_universe_export,
                    }
                    for _df in run_frames.values():
                        if isinstance(_df, pd.DataFrame):
                            _df.insert(0, '실행ID', run_id)

                    # 요약표 MDD/누적수익률과 같은 실행의 자산곡선 계산값을 자동 대조합니다.
                    audit_rows = []
                    if not portfolio_summary.empty and not curves.empty:
                        for _, _s in portfolio_summary.iterrows():
                            _g = curves[(curves['전략'] == _s['전략']) & (curves['구간'] == _s['구간'])].copy()
                            if _g.empty:
                                audit_rows.append({
                                    '실행ID': run_id, '구간': _s['구간'], '전략': _s['전략'],
                                    '요약거래수': _s.get('거래수', np.nan), '곡선행수': 0,
                                    '요약누적수익률(%)': _s.get('누적수익률(%)', np.nan),
                                    '곡선누적수익률(%)': np.nan, '요약MDD(%)': _s.get('MDD(%)', np.nan),
                                    '곡선MDD(%)': np.nan, '검증결과': '곡선 누락'
                                })
                                continue
                            _g = _g.sort_values('날짜')
                            _vals = pd.to_numeric(_g['자산지수'], errors='coerce').dropna()
                            _curve_total = (float(_vals.iloc[-1]) - 1) * 100 if len(_vals) else np.nan
                            _curve_mdd = float(pd.to_numeric(_g['낙폭(%)'], errors='coerce').min()) if '낙폭(%)' in _g else np.nan
                            _total_diff = abs(float(_s['누적수익률(%)']) - _curve_total) if pd.notna(_s.get('누적수익률(%)')) and pd.notna(_curve_total) else np.nan
                            _mdd_diff = abs(float(_s['MDD(%)']) - _curve_mdd) if pd.notna(_s.get('MDD(%)')) and pd.notna(_curve_mdd) else np.nan
                            _ok = pd.notna(_total_diff) and pd.notna(_mdd_diff) and _total_diff < 0.02 and _mdd_diff < 0.02
                            audit_rows.append({
                                '실행ID': run_id, '구간': _s['구간'], '전략': _s['전략'],
                                '요약거래수': _s.get('거래수', np.nan),
                                '곡선행수': int(len(_g)),
                                '요약누적수익률(%)': _s.get('누적수익률(%)', np.nan),
                                '곡선누적수익률(%)': _curve_total,
                                '요약MDD(%)': _s.get('MDD(%)', np.nan),
                                '곡선MDD(%)': _curve_mdd,
                                '누적수익률차이(%p)': _total_diff,
                                'MDD차이(%p)': _mdd_diff,
                                '검증결과': 'PASS' if _ok else 'CHECK'
                            })
                    curve_audit = pd.DataFrame(audit_rows)
                    if not curve_audit.empty:
                        curve_audit.insert(0, '실행ID', run_id) if '실행ID' not in curve_audit.columns else None

                    st.session_state['ib_result']={'portfolio_summary':portfolio_summary,'forward_summary':forward_summary,
                        'samples':all_samples,'trades':portfolio_trades,'curves':curves,'signals':pd.DataFrame(signals),
                        'price_history':price_history,'price_coverage':price_coverage,'theme_universe':theme_universe_export,
                        'curve_audit':curve_audit, 'run_id':run_id,
                        'strategies':strategies,'hold':hold}
                    status.update(label='전략 비교 완료',state='complete',expanded=False)
                except Exception as ex:
                    status.update(label='독립 백테스트 실패',state='error',expanded=True)
                    st.exception(ex)
    r=st.session_state.get('ib_result')
    if not r:
        st.info('비교 실행 버튼을 누르면 가격 데이터 다운로드 후 전략별 결과가 생성됩니다.')
        return
    st.markdown('### 1. 투자 가능한 포트폴리오 성과 비교')
    st.dataframe(r['portfolio_summary'].round(3),use_container_width=True,hide_index=True)
    st.caption(f"실행 ID: {r.get('run_id', '미기록')} · 비중복 포지션 방식입니다. 다음 거래일 시가 진입, 선택한 보유기간 동안 보유, 양방향 수수료·슬리피지 반영. MDD는 일별 종가 평가곡선 기준입니다.")
    st.markdown('### 1-1. 요약표와 자산곡선 자동 대조')
    if not r.get('curve_audit', pd.DataFrame()).empty:
        st.dataframe(r['curve_audit'].round(3), use_container_width=True, hide_index=True)
        if (r['curve_audit']['검증결과'] == 'PASS').all():
            st.success('요약표의 누적수익률·MDD와 같은 실행의 자산곡선이 일치합니다.')
        else:
            st.warning('일부 전략의 요약표와 자산곡선이 일치하지 않습니다. 아래 통합 ZIP의 실행 ID가 같은 파일끼리 확인해 주세요.')
    st.markdown('### 2. 정방향 예측력 비교 — 보유기간별')
    if not r['forward_summary'].empty:
        st.dataframe(r['forward_summary'].round(3),use_container_width=True,hide_index=True)
        st.caption('손절10% 변형은 조기 청산 규칙이 정방향 고정 보유기간 표본과 다르므로 이 표본 비교에서는 제외하고, 포트폴리오 성과표와 체결 내역에서 비교합니다.')
    else:
        st.info('정방향 표본이 충분하지 않습니다.')
    st.markdown('### 3. 전략별 독립 포트폴리오 자산곡선')
    if not r['curves'].empty:
        chart=r['curves'].pivot_table(index='날짜',columns='시리즈',values='자산지수',aggfunc='last').sort_index()
        st.line_chart(chart)
    st.markdown('### 4. 체결 내역')
    st.dataframe(r['trades'].tail(200),use_container_width=True,hide_index=True)
    st.markdown('### 5. 가격 데이터 범위 확인')
    st.caption('아래 파일은 이번 실행에서 실제로 내려받아 백테스트에 사용한 일별 가격·지표입니다. 현재 ETF MASTER를 과거에 적용한 구성이라는 한계는 유지됩니다.')
    if not r.get('price_coverage', pd.DataFrame()).empty:
        st.dataframe(r['price_coverage'],use_container_width=True,hide_index=True)
    # Prospective validation: export only the latest available signal snapshot for manual, forward-looking tracking.
    st.markdown('### 6. 실전 신호 전향 검증 기록')
    st.caption('오늘까지의 과거 성과를 다시 최적화하는 대신, 최신 신호를 CSV로 저장해 이후 20거래일 성과를 추적합니다. 매 거래일 최신 신호 파일을 저장하고, 20거래일 경과 후 결과를 누적 비교하세요.')
    siglog = r.get('signals', pd.DataFrame()).copy()
    if not siglog.empty and 'date' in siglog.columns:
        siglog['date'] = pd.to_datetime(siglog['date'], errors='coerce')
        latest_dt = siglog['date'].max()
        latest = siglog[siglog['date'].eq(latest_dt)].copy()
        ph = r.get('price_history', pd.DataFrame()).copy()
        if not ph.empty and {'ETF코드','날짜','Close'}.issubset(ph.columns):
            ph['ETF코드'] = ph['ETF코드'].astype(str).str.zfill(6)
            ph['날짜'] = pd.to_datetime(ph['날짜'], errors='coerce')
            latest['ETF코드'] = latest['etf'].astype(str).str.zfill(6)
            latest = latest.merge(
                ph[['ETF코드','날짜','Close']].rename(columns={'날짜':'date','Close':'신호일종가'}),
                on=['ETF코드','date'], how='left'
            )
        else:
            latest['신호일종가'] = np.nan
        # Export both positive and negative strategy flags to record the full decision state.
        keep = [c for c in [
            'date','etf','name','theme','final_score','price_zone','rsi','vr','dist20',
            'trend_pass','FINAL','FINAL_V2','신호일종가'
        ] if c in latest.columns]
        latest = latest[keep].rename(columns={
            'date':'신호일','etf':'ETF코드','name':'ETF명','theme':'테마',
            'final_score':'FINAL점수','price_zone':'가격구간','rsi':'RSI','vr':'거래량비',
            'dist20':'MA20이격률(%)','trend_pass':'상승추세조건','FINAL':'기존FINAL신호',
            'FINAL_V2':'FINAL_V2신호'
        })
        latest['기록목적'] = '전향검증용; 신호일 이후 수익률은 미래 데이터 확보 후 계산'
        latest['20거래일후수익률(%)'] = np.nan
        latest['KODEX200_20거래일수익률(%)'] = np.nan
        st.dataframe(latest, use_container_width=True, hide_index=True)
        st.download_button(
            '📥 최신 신호 전향검증 CSV 저장',
            data=latest.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"ETF_RADAR_FORWARD_TEST_{pd.Timestamp(latest_dt).strftime('%Y%m%d')}.csv",
            mime='text/csv',
            use_container_width=True,
            key='ib_forward_test_export'
        )
    else:
        st.info('신호 데이터가 없습니다. 먼저 전략 비교 실행을 눌러 주세요.')

    files={'INDEPENDENT_PORTFOLIO_SUMMARY.csv':r['portfolio_summary'],'INDEPENDENT_FORWARD_SUMMARY.csv':r['forward_summary'],
           'INDEPENDENT_FORWARD_SAMPLES.csv':r['samples'],'INDEPENDENT_PORTFOLIO_TRADES.csv':r['trades'],'INDEPENDENT_EQUITY_CURVES.csv':r['curves'],
           'INDEPENDENT_SIGNALS.csv':r['signals'],'INDEPENDENT_PRICE_HISTORY.csv':r.get('price_history',pd.DataFrame()),
           'INDEPENDENT_PRICE_COVERAGE.csv':r.get('price_coverage',pd.DataFrame()),
           'INDEPENDENT_THEME_UNIVERSE.csv':r.get('theme_universe',pd.DataFrame()),
           'INDEPENDENT_CURVE_AUDIT.csv':r.get('curve_audit',pd.DataFrame())}

    # 단일 실행에서 나온 파일을 하나의 ZIP으로 제공하여 서로 다른 실행 결과가 섞이지 않게 합니다.
    _zip_buffer = io.BytesIO()
    with zipfile.ZipFile(_zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as _zip:
        _zip.writestr('RUN_INFO.txt', f"실행ID: {r.get('run_id', '미기록')}\n선택전략: {', '.join(r.get('strategies', []))}\n보유기간: {r.get('hold', '')} 거래일\n모든 CSV는 같은 실행에서 생성되었습니다.\n")
        for _name, _df in files.items():
            if isinstance(_df, pd.DataFrame):
                _zip.writestr(_name, _df.to_csv(index=False).encode('utf-8-sig'))
    st.download_button(
        '📦 이번 실행 결과 전체 다운로드 (CSV 10개 + 실행 정보)',
        data=_zip_buffer.getvalue(),
        file_name=f"ETF_RADAR_BACKTEST_{r.get('run_id', 'run')}.zip",
        mime='application/zip',
        type='primary',
        use_container_width=True,
        key='ib_download_bundle'
    )
    cols=st.columns(3)
    for i,(name,df) in enumerate(files.items()):
        with cols[i%3]:
            st.download_button(f'📥 {name}',df.to_csv(index=False,encoding='utf-8-sig').encode('utf-8-sig'),file_name=name,mime='text/csv',use_container_width=True,key='ib_dl_'+name)

def render_final_validation():
    st.markdown('<div class="hero"><div class="hero-name">🏁 FINAL VALIDATION LAB</div><div class="hero-code">D+M 최종검증 · 매일 신호 · 보유기간 5/10/20/40/60일 · 조건 기여도 · OOS</div></div>', unsafe_allow_html=True)
    st.info("기존 검증은 현재 ETF MASTER를 과거에 적용하므로 생존편향이 남습니다. 또한 기존 MDD는 거래 결과를 이어 붙인 기준으로, 보유 중 일별 최대 낙폭을 완전히 반영하지 않습니다. 아래 🧪 독립검증 메뉴에서 별도 체결·비용·일별 자산곡선으로 재검증할 수 있습니다.")
    render_forward_ml_panel()
    c1,c2,c3=st.columns(3)
    with c1: start=st.date_input("검증 시작일",date(2018,1,1),key="fv_start")
    with c2: end=st.date_input("검증 종료일",date.today(),key="fv_end")
    with c3: oos_year=st.number_input("OOS 시작연도",min_value=2018,max_value=2030,value=2024,step=1,key="fv_oos")
    st.markdown("**검사 간격: 매일(1거래일)** · **비용: 편도 수수료 0.10% + 슬리피지 0.05%**")
    if st.button("🚀 FINAL VALIDATION 실행",type="primary",use_container_width=True,key="fv_run"):
        if start>=end:
            st.error("시작일은 종료일보다 빨라야 합니다."); return
        with st.status("최종 검증을 실행하는 중...",expanded=True) as status:
            try:
                status.write("① 현재 ETF MASTER에서 테마군 구성")
                universe,theme_members,codes=wf_build_universe()
                status.write(f"② ETF {len(codes)}개 가격 데이터 다운로드")
                data=wf_download_history(tuple(codes)); data={k:v for k,v in data.items() if v is not None and not v.empty}
                if WF_BENCH not in data: raise RuntimeError("KODEX 200 데이터를 가져오지 못했습니다.")
                bench=data[WF_BENCH]
                dates=bench.index[(bench.index>=pd.Timestamp(start))&(bench.index<=pd.Timestamp(end))]
                signals=[]
                for i,dt in enumerate(dates):
                    snap=wf_snapshot(data,theme_members,dt)
                    if snap: signals.append(snap)
                if not signals: raise RuntimeError("유효한 신호가 없습니다.")
                signals=wf_add_final_strategy_flags(signals)
                status.write(f"③ 매일 검사 완료: {len(signals):,}개 신호")
                strategy_keys=["BASE_D","D+TREND","D+MOMVOL","D+MARKET","D+T+MV","D+T+M","D+MV+M","D+T+MV+M"]
                labels={"BASE_D":"BASE D","D+TREND":"D + 추세","D+MOMVOL":"D + 모멘텀·거래량","D+MARKET":"D + 시장환경","D+T+MV":"D + 추세 + 모멘텀·거래량","D+T+M":"D + 추세 + 시장환경","D+MV+M":"D + 모멘텀·거래량 + 시장환경","D+T+MV+M":"D + 추세 + 모멘텀·거래량 + 시장환경"}
                all_summary=[]; all_trades=[]
                for hold in WF_HORIZONS:
                    for key in strategy_keys:
                        td=wf_make_trades_horizon(data,signals,key,hold)
                        m=wf_final_summary(td)
                        m.update({"전략":labels[key],"조건키":key,"보유기간":hold})
                        all_summary.append(m)
                        if not td.empty: all_trades.append(td)
                summary=pd.DataFrame(all_summary)
                trades=pd.concat(all_trades,ignore_index=True) if all_trades else pd.DataFrame()
                sigdf=pd.DataFrame(signals)
                oos=sigdf[pd.to_datetime(sigdf["date"]).dt.year>=int(oos_year)].copy()
                # OOS는 거래까지 포함한 표
                oos_rows=[]
                for hold in WF_HORIZONS:
                    for key in strategy_keys:
                        td=wf_make_trades_horizon(data,signals,key,hold)
                        if not td.empty:
                            z=td[pd.to_datetime(td["signal_date"]).dt.year>=int(oos_year)].copy()
                            if not z.empty:
                                m=wf_final_summary(z); m.update({"전략":labels[key],"조건키":key,"보유기간":hold})
                                oos_rows.append(m)
                oos_summary=pd.DataFrame(oos_rows)
                st.session_state["fv_result"]={"summary":summary,"trades":trades,"signals":sigdf,"oos_signals":oos,"oos_summary":oos_summary}
                status.update(label="FINAL VALIDATION 완료",state="complete",expanded=False)
            except Exception as ex:
                status.update(label="최종 검증 실패",state="error",expanded=True); st.exception(ex); return
    r=st.session_state.get("fv_result")
    if not r: return
    st.markdown("### 1. 보유기간별 전체 결과")
    pivot=r["summary"].pivot_table(index="전략",columns="보유기간",values="누적복리",aggfunc="first")
    st.dataframe(pivot.round(2),use_container_width=True)
    st.markdown("### 2. 전체 상세 결과")
    st.dataframe(r["summary"].sort_values(["보유기간","누적복리"],ascending=[True,False]),use_container_width=True,hide_index=True)
    st.markdown("### 3. OOS 결과")
    st.dataframe(r["oos_summary"].sort_values(["보유기간","누적복리"],ascending=[True,False]),use_container_width=True,hide_index=True)
    st.markdown("### 4. 신호 표본")
    st.write(f"전체 신호 {len(r['signals']):,}개 / OOS 신호 {len(r['oos_signals']):,}개")
    st.dataframe(r["signals"].sort_values("date",ascending=False).head(50),use_container_width=True,hide_index=True)
    files={
        "FINAL_VALIDATION_SUMMARY.csv":r["summary"],
        "FINAL_VALIDATION_TRADES.csv":r["trades"],
        "FINAL_VALIDATION_SIGNALS.csv":r["signals"],
        "FINAL_VALIDATION_OOS_SUMMARY.csv":r["oos_summary"],
        "FINAL_VALIDATION_OOS_SIGNALS.csv":r["oos_signals"],
    }
    st.markdown("### 5. CSV 다운로드")
    cols=st.columns(3)
    for i,(name,df) in enumerate(files.items()):
        with cols[i%3]: st.download_button(f"📥 {name}",df.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig"),file_name=name,mime="text/csv",use_container_width=True,key="fv_dl_"+name)


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
    ["🏆 최종 타겟", "🚀 미래테마", "📊 내 ETF", "🧪 백테스트", "🧬 TRUE 검증", "🏁 최종검증", "🧪 독립검증"],
    horizontal=True,
    key="main_page",
    label_visibility="collapsed"
)

if nav == "🏆 최종 타겟":
    render_final_target()
elif nav == "🚀 미래테마":
    render_future_theme()
elif nav == "📊 내 ETF":
    render_my_etf()
elif nav == "🧪 백테스트":
    render_backtest_lab()
elif nav == "🧬 TRUE 검증":
    render_true_walk_forward()
elif nav == "🏁 최종검증":
    render_final_validation()
elif nav == "🧪 독립검증":
    render_independent_backtest()
