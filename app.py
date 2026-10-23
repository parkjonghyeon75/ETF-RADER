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
# 고정 5개 테마에 한정하지 않고 ETF 상품명에서 후보 테마를 자동 발굴합니다.
# 기존 사전은 의미가 명확한 기준 분류이며, 신규 후보와 실제 노출 순위는
# ETF 마스터/가격 데이터가 갱신될 때 재계산됩니다. 자동 발굴 키워드는 후보이지
# 사업 연관성이 검증된 산업 분류를 뜻하지 않으므로 최소 ETF 수와 가격 기준을 적용합니다.
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
    "인프라","테크","성장","투자","산업","기업","시장","전략","포트폴리오","주식","지수","선물","현물",
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
        # 종목명에서 분리된 완전한 한글 토큰만 후보로 사용합니다.
        # 부분 문자열 n-gram은 '전력인프라'에서 '력인프', '주항공' 같은
        # 가짜 테마를 양산하므로 사용하지 않습니다.
        words=re.findall(r"[가-힣]{2,12}", text)
        seen=set()
        for w in words:
            if w in _AUTO_THEME_STOP or len(w)<2: continue
            if w in seen: continue
            seen.add(w); counts[w]+=1; samples.setdefault(w,[]).append((code,name))
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
    """국내 ETF 가격을 복수 시장 접미사로 조회하고, 실패 시 네이버로 보완합니다.

    Yahoo Finance에서 일부 국내 종목은 .KS 대신 .KQ로 제공되거나
    일시적인 빈 응답을 반환할 수 있어 한 번의 .KS 요청만으로 포기하지 않습니다.
    """
    code = _normalize_etf_code(code)
    if not code or not code.isdigit():
        return pd.DataFrame()

    # 국내 ETF는 대체로 .KS이지만, 데이터 제공처의 분류 차이에 대비해 .KQ도 시도합니다.
    for suffix in (".KS", ".KQ"):
        try:
            raw = yf.download(
                f"{code}{suffix}", period="5y", interval="1d", auto_adjust=False,
                progress=False, threads=False, timeout=12
            )
            df = normalize_df(raw)
            if not df.empty and len(df) >= 2:
                return df.sort_index()
        except Exception:
            continue

    # Yahoo에서 찾지 못한 경우 네이버 일봉을 최종 fallback으로 사용합니다.
    try:
        df = fetch_naver_history(code, count=1200)
        if df is not None and not df.empty:
            return df.sort_index()
    except Exception:
        pass
    return pd.DataFrame()


def load_price_data(code, force=False):
    code = str(code).zfill(6)
    now = datetime.now()
    cached = st.session_state.price_cache.get(code)
    if cached and not force:
        age = (now - cached["time"]).total_seconds()
        cached_data = cached.get("data")
        ttl = 300 if cached_data is not None and not cached_data.empty else 45
        if age < ttl:
            return cached_data if cached_data is not None else pd.DataFrame()

    df = fetch_yahoo(code)
    # 빈 응답도 짧게 캐시해 동일한 실행 중 반복 요청·일시 차단을 줄입니다.
    # 정상 데이터는 기존 5분 캐시를 그대로 적용합니다.
    st.session_state.price_cache[code] = {
        "time": now,
        "data": df if df is not None else pd.DataFrame(),
    }
    return st.session_state.price_cache[code]["data"]


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


# 미국장 선행신호 → 국내 ETF 테마 연결. 점수는 미국장 종가 기준으로만 계산합니다.
US_LEADING_THEME_MAP = {
    "AI 반도체": ["SMH", "SOXX", "NVDA", "AMD", "AVGO"],
    "반도체 장비·소부장": ["SMH", "SOXX", "AMAT", "LRCX", "KLAC"],
    "로봇": ["BOTZ", "ROBO", "ISRG"],
    "방산": ["ITA", "XAR", "LMT", "RTX", "NOC"],
    "2차전지": ["LIT", "BATT", "ALB", "TSLA"],
    "전기차": ["DRIV", "IDRV", "TSLA"],
    "자동차": ["CARZ", "TSLA", "GM", "F"],
    "조선": ["BOAT", "XLI"],
    "원자력": ["URA", "NLR", "CCJ"],
    "전력 인프라": ["GRID", "PAVE", "ETN", "VRT"],
    "데이터센터·AI 인프라": ["SRVR", "VPN", "VRT", "ANET"],
    "냉각·열관리": ["VRT", "CARR", "TT"],
    "바이오": ["XBI", "IBB", "IHI"],
    "우주항공": ["ARKX", "UFO", "RKLB"],
    "AI 소프트웨어": ["IGV", "WCLD", "CLOU", "PLTR"],
    "클라우드": ["SKYY", "CLOU", "WCLD"],
    "보안": ["CIBR", "HACK", "BUG"],
    "5G·통신": ["IYZ", "FIVG", "ANET"],
    "신재생에너지": ["ICLN", "TAN", "FAN"],
    "수소": ["HDRO", "HYDR"],
    "금융": ["XLF", "KBE", "KRE"],
    "화장품·K뷰티": ["XLP", "IYC"],
    "음식료·소비": ["XLP", "XLY", "IYC"],
    "건설·인프라": ["PAVE", "IFRA", "XLI"],
    "철강·금속": ["XME", "PICK", "SLX"],
    "미국 기술": ["QQQ", "XLK", "IGV"],
    "배당": ["SCHD", "VYM", "DVY"],
    "리츠": ["VNQ", "IYR", "XLRE"],
    "한국 대표시장": ["SPY", "QQQ", "IWM"],
    # Broad-market proxies; used for index products, not industry themes.
    "미국 대표시장": ["SPY", "VOO", "IVV", "QQQM", "IWM", "ARKK"],
}

def _us_leading_snapshot(force=False):
    """미국 대표 ETF의 최근 2개 종가와 20일 추세를 캐시해 선행 점수를 산출."""
    cache = st.session_state.get("us_leading_snapshot_cache")
    now = datetime.now()
    if cache and not force:
        try:
            if (now-cache["time"]).total_seconds() < 900:
                return cache["data"]
        except Exception:
            pass
    tickers = sorted({t.strip() for ts in US_LEADING_THEME_MAP.values() for t in ts if t.strip()})
    result = {}
    try:
        raw = yf.download(tickers, period="3mo", interval="1d", auto_adjust=True,
                          progress=False, threads=True, group_by="ticker", timeout=15)
        for ticker in tickers:
            try:
                if isinstance(raw.columns, pd.MultiIndex):
                    close = None
                    # yfinance can return either (Ticker, Field) or (Field, Ticker).
                    if ticker in raw.columns.get_level_values(0):
                        block = raw[ticker]
                        if isinstance(block, pd.DataFrame) and "Close" in block.columns:
                            close = block["Close"]
                    if close is None and "Close" in raw.columns.get_level_values(0):
                        block = raw.xs("Close", axis=1, level=0, drop_level=True)
                        if ticker in block.columns:
                            close = block[ticker]
                    if close is None:
                        continue
                    close = pd.to_numeric(close, errors="coerce").dropna()
                else:
                    if "Close" not in raw.columns:
                        continue
                    close = pd.to_numeric(raw["Close"], errors="coerce").dropna()
                if len(close) < 22:
                    continue
                last = float(close.iloc[-1]); prev = float(close.iloc[-2]); ma20 = float(close.tail(20).mean())
                ret1 = (last/prev-1)*100 if prev else np.nan
                ret20 = (last/float(close.iloc[-21])-1)*100 if float(close.iloc[-21]) else np.nan
                if np.isfinite(ret1) and np.isfinite(ret20):
                    result[ticker] = {"ret1":ret1,"ret20":ret20,"above20":last>=ma20,
                                      "as_of":str(pd.to_datetime(close.index[-1]).date())}
            except Exception:
                continue
    except Exception:
        result = {}
    data = {"tickers":result,"fetched_at":now.isoformat()}
    st.session_state["us_leading_snapshot_cache"] = {"time":now,"data":data}
    return data

def _us_theme_signal(theme, product_name="", force=False):
    """테마별 미국장 신호(50=중립). 광범위 지수형 상품은 산업 테마와 분리합니다."""
    mapping = None
    product_text = str(product_name or "").upper().replace(" ", "")
    # 상품명 우선 판별: 광범위 지수형/배당/리츠 상품은 산업 테마와 분리합니다.
    # 미국장 지표는 국내시장 ETF의 직접 복제물이 아니라 다음 국내장 위험선호의 대리변수입니다.
    if "S&P500" in product_text or "SP500" in product_text or "S&P 500" in product_text:
        mapping = ["SPY", "VOO", "IVV"]
    elif "NASDAQ100" in product_text or "나스닥100" in product_text or "나스닥" in product_text:
        mapping = ["QQQ", "QQQM"]
    elif "리츠" in product_text or "REIT" in product_text:
        mapping = ["VNQ", "IYR", "XLRE"]
    elif "배당" in product_text:
        mapping = ["SCHD", "VYM", "DVY"]
    elif "KOSPI200" in product_text or "코스피200" in product_text or "TIGER 200" in product_text or "KODEX 200" in product_text or "PLUS 200" in product_text or "RISE 200" in product_text or "KIWOOM 200" in product_text or "코스피" in product_text:
        mapping = ["SPY", "QQQ", "IWM"]
    elif "KOSDAQ150" in product_text or "코스닥150" in product_text or "코스닥" in product_text:
        mapping = ["QQQ", "IWM"]
    if mapping is None:
        for key, tickers in US_LEADING_THEME_MAP.items():
            if key == theme:
                mapping = tickers
                break
    if mapping is None:
        text = f"{theme} {product_name}".lower()
        aliases = [("반도체", "AI 반도체"), ("배터리", "2차전지"), ("전력", "전력 인프라"),
                   ("데이터센터", "데이터센터·AI 인프라"), ("원전", "원자력"), ("방산", "방산"),
                   ("로봇", "로봇"), ("바이오", "바이오"), ("클라우드", "클라우드"),
                   ("보안", "보안"), ("금융", "금융"), ("우주", "우주항공"),
                   ("리츠", "리츠"), ("배당", "배당"),
                   ("미국 기술", "미국 기술"), ("AI", "AI 소프트웨어")]
        for alias, key in aliases:
            if alias in text and key in US_LEADING_THEME_MAP:
                mapping = US_LEADING_THEME_MAP[key]; break
    if not mapping:
        return {"available":False,"score":np.nan,"tickers":[],"as_of":None,"mapping":"미국장 테마 연결 없음","contribution":0.0}
    snapshot = _us_leading_snapshot(force=force)
    vals = [(t,snapshot["tickers"][t]) for t in mapping if t in snapshot.get("tickers",{})]
    if not vals:
        return {"available":False,"score":np.nan,"tickers":mapping,"as_of":None,"mapping":"연결 티커 가격 미확보","contribution":0.0}
    # 일간 급등 하나보다 일간 방향·20일 추세의 동시성을 중시합니다.
    daily = float(np.mean([np.clip(v["ret1"],-5,5) for _,v in vals]))
    medium = float(np.mean([np.clip(v["ret20"],-15,15) for _,v in vals]))
    breadth = float(np.mean([1.0 if v["above20"] else 0.0 for _,v in vals]))
    score = float(np.clip(50 + daily*3.0 + medium*1.0 + (breadth-.5)*12, 0, 100))
    # 중립 50점 기준 ±8점 상한. 가격/추세가 모두 약하면 국내 ETF 점수도 감점됩니다.
    contribution = float(np.clip((score-50)*0.16,-8,8))
    dates = [v["as_of"] for _,v in vals if v.get("as_of")]
    return {"available":True,"score":round(score,1),"tickers":[t for t,_ in vals],
            "as_of":max(dates) if dates else None,"mapping":"미국 대표 ETF·관련 종목 가격/추세",
            "contribution":round(contribution,2)}


def _theme_keywords_for_etf(theme):
    return THEME_LEXICON.get(theme, ())

def build_future_theme_engine(force=False):
    """국내 ETF의 테마 강도·추세·상대강도로 타겟을 선정하고 진입 점수를 분리합니다."""
    cached = st.session_state.get("future_engine_cache")
    if cached and not force:
        try:
            cached_data = cached.get("data", {})
            if (cached_data.get("engine_version") == "ETF_THEME_FIRST_US_LEADING_V4"
                    and (datetime.now() - cached["time"]).total_seconds() < 1800):
                return cached_data
        except Exception:
            pass

    universe = st.session_state.get("etf_universe", {})
    if not universe:
        universe = load_etf_universe()
        st.session_state.etf_universe = universe
    benchmark = _benchmark_snapshot()
    # 미국장 종가 기반 선행신호를 실제 수집합니다. 실패 시 국내 점수만으로 평가합니다.
    us_snapshot = _us_leading_snapshot()
    candidates = []
    # ETF별 가격을 여러 테마에서 반복 다운로드하지 않도록 엔진 실행 중 로컬 캐시를 둡니다.
    local_price_cache = {}

    # 기존 테마는 기준 분류로 유지하되 고정 목록에 한정하지 않습니다.
    # ETF 마스터가 갱신되면 반복 출현하는 새 키워드를 자동 발굴하고,
    # 자동 후보는 최소 3개 국내 ETF에 연결되며 가격 데이터 평가를 통과해야 노출합니다.
    # 현재 자동 발굴은 ETF 상품명 기반입니다. 구성종목/공시 기반의 산업 의미 검증과는 구분합니다.
    # ETF_THEME_PLAYBOOK was removed in the domestic-only refactor. Build the
    # engine configuration from the still-active THEME_LEXICON instead.
    theme_configs = {
        theme: {
            "keywords": tuple(keywords),
            "reason": "국내 ETF의 가격·추세·상대강도를 기준으로 평가합니다.",
        }
        for theme, keywords in THEME_LEXICON.items()
    }
    try:
        dynamic_lexicon = get_dynamic_theme_lexicon(universe)
    except Exception:
        dynamic_lexicon = dict(THEME_LEXICON)
    for discovered_theme, discovered_keywords in dynamic_lexicon.items():
        if discovered_theme in theme_configs or not str(discovered_theme).startswith("자동·"):
            continue
        theme_configs[discovered_theme] = {
            "keywords": tuple(discovered_keywords),
            "reason": "ETF 마스터에서 반복적으로 관찰된 키워드로 발굴한 후보 테마입니다. 실제 투자 테마인지 구성종목·가격 흐름을 추가 확인합니다.",
            "discovered": True,
        }

    # 원자재 가격 추종 ETF는 산업 테마 상승 타겟과 분리하며 미래테마 엔진에서도 제외합니다.
    # 전력/에너지/2차전지 등 산업 테마는 유지하고 상품 자체를 추종하는 명칭만 거릅니다.
    _commodity_theme_names = {"원자재", "금·귀금속"}
    _commodity_product_terms = (
        "원유선물", "원유", "wti", "brent", "천연가스선물", "천연가스",
        "금선물", "금현물", "골드선물", "gold futures", "gold spot",
        "은선물", "은현물", "실버선물", "구리선물", "알루미늄선물",
        "농산물선물", "곡물선물", "커머디티", "commodity",
    )
    # 성능 최적화: 테마별로 가격을 하나씩 순차 요청하면 신규 실행에서 수십 초가 걸립니다.
    # 모든 테마의 상위 표본 코드 중 캐시에 없는 코드만 먼저 모아 제한된 병렬 처리로 수집합니다.
    # 세션 상태는 메인 스레드에서만 갱신하고, 작업 스레드는 네트워크 조회만 수행합니다.
    prefetch_codes = set()
    for _theme, _config in theme_configs.items():
        if _theme in _commodity_theme_names:
            continue
        _matched = []
        for _code, _name in universe.items():
            _normalized_product_name = re.sub(r"[^0-9a-z가-힣]+", "", str(_name or "").lower())
            if any(re.sub(r"[^0-9a-z가-힣]+", "", term.lower()) in _normalized_product_name
                   for term in _commodity_product_terms):
                continue
            _hits = _theme_match_for_theme(_name, _config["keywords"], _theme)
            if _hits:
                _matched.append((_hits, _normalize_etf_code(_code), safe_etf_name(_code, _name)))
        _matched.sort(key=lambda x: (x[0], len(str(x[2])), x[2]), reverse=True)
        if _config.get("discovered") and len({_x[1] for _x in _matched}) < 3:
            continue
        prefetch_codes.update(_x[1] for _x in _matched[:14] if _x[1])

    _fetch_codes = []
    _now_prefetch = datetime.now()
    for _code in prefetch_codes:
        _cached = st.session_state.price_cache.get(_code)
        _ttl = 300 if _cached and _cached.get("data") is not None and not _cached["data"].empty else 45
        _age = (_now_prefetch - _cached["time"]).total_seconds() if _cached else 10**9
        if not _cached or _age >= _ttl:
            _fetch_codes.append(_code)

    if _fetch_codes:
        _fetched = {}
        with ThreadPoolExecutor(max_workers=8) as _pool:
            _future_map = {_pool.submit(fetch_yahoo, _code): _code for _code in _fetch_codes}
            for _future in as_completed(_future_map):
                _code = _future_map[_future]
                try:
                    _df = _future.result()
                    _fetched[_code] = _df if _df is not None else pd.DataFrame()
                except Exception:
                    _fetched[_code] = pd.DataFrame()
        _finished = datetime.now()
        for _code, _df in _fetched.items():
            st.session_state.price_cache[_code] = {"time": _finished, "data": _df}

    for theme, config in theme_configs.items():
        if theme in _commodity_theme_names:
            continue
        keywords = config["keywords"]
        matched = []
        for code, name in universe.items():
            _normalized_product_name = re.sub(r"[^0-9a-z가-힣]+", "", str(name or "").lower())
            if any(re.sub(r"[^0-9a-z가-힣]+", "", term.lower()) in _normalized_product_name
                   for term in _commodity_product_terms):
                continue
            hits = _theme_match_for_theme(name, keywords, theme)
            if hits:
                matched.append((hits, _normalize_etf_code(code), safe_etf_name(code, name)))
        # ETF 이름의 단어 하나만 우연히 맞는 광범위한 테마 편입을 줄이기 위해
        # 특수한 좁은 키워드 우선순위로 정렬하고, 유동적 표본을 가격 데이터로 검증합니다.
        matched.sort(key=lambda x: (x[0], len(str(x[2])), x[2]), reverse=True)
        if not matched:
            continue
        # 자동 발굴 테마는 이름의 우연한 중복으로 생성되는 것을 막기 위해
        # 서로 다른 국내 ETF가 최소 3개 연결되어야 가격 평가 단계로 진입합니다.
        if config.get("discovered") and len({x[1] for x in matched}) < 3:
            continue
        # 각 테마 최대 14개를 평가하되, 이름 일치도가 높은 후보를 우선합니다.
        # 전체 후보를 무조건 내려받아 속도가 급격히 느려지는 문제를 피합니다.
        sample = matched[:14]
        rows = []
        for hits, code, name in sample:
            if code not in local_price_cache:
                try:
                    df = load_price_data(code)
                    d = calculate_indicators(df) if df is not None and not df.empty else pd.DataFrame()
                    local_price_cache[code] = d
                except Exception:
                    local_price_cache[code] = pd.DataFrame()
            d = local_price_cache[code]
            if d is None or d.empty or len(d) < 65:
                continue
            r = d.iloc[-1]
            close = pd.to_numeric(d["Close"], errors="coerce")
            current = safe_float(r.get("Close"), np.nan)
            ret5 = safe_float(r.get("RET5"), np.nan)
            ret20 = safe_float(r.get("RET20"), np.nan)
            ret60 = safe_float(close.pct_change(60).iloc[-1] * 100, np.nan)
            ma20 = safe_float(r.get("MA20"), np.nan)
            ma60 = safe_float(r.get("MA60"), np.nan)
            rsi = safe_float(r.get("RSI14"), np.nan)
            vr = safe_float(r.get("VOL_RATIO"), np.nan)
            if not np.isfinite(current) or current <= 0 or not np.isfinite(ret20) or not np.isfinite(ret60):
                continue
            prev = d.iloc[-21] if len(d) >= 86 else None
            prev_ret20 = safe_float(prev.get("RET20"), ret20) if prev is not None else ret20
            prev_ret60 = safe_float(close.pct_change(60).iloc[-21] * 100, ret60) if prev is not None else ret60
            prev_close = safe_float(prev.get("Close"), current) if prev is not None else current
            prev_ma20 = safe_float(prev.get("MA20"), prev_close) if prev is not None else ma20
            prev_ret5 = safe_float(prev.get("RET5"), ret5) if prev is not None else ret5
            breadth = 100.0 if np.isfinite(ma20) and current >= ma20 else 0.0
            breadth_prev = 100.0 if np.isfinite(prev_ma20) and prev_close >= prev_ma20 else 0.0
            accel = ret5 - ret20 / 4.0 if np.isfinite(ret5) else np.nan
            prev_accel = prev_ret5 - prev_ret20 / 4.0 if np.isfinite(prev_ret5) else accel
            bench20 = safe_float(benchmark.get("ret20"), np.nan)
            rows.append({
                "code": code, "name": name, "price": current, "rsi": rsi, "vr": vr,
                "ret": ret20, "ret20": ret20, "ret60": ret60, "ret5": ret5,
                "trend": "상승" if np.isfinite(ma20) and current >= ma20 else "조정",
                "ma60_gap": (current / ma60 - 1) * 100 if np.isfinite(ma60) and ma60 > 0 else np.nan,
                "breadth": breadth, "accel": accel, "hits": hits,
                "rs20": ret20 - bench20 if np.isfinite(bench20) else np.nan,
                "ret20_prev": prev_ret20, "ret60_prev": prev_ret60,
                "breadth_prev": breadth_prev, "accel_prev": prev_accel,
                "rs20_prev": prev_ret20 - bench20 if np.isfinite(bench20) else np.nan,
                "as_of": str(pd.to_datetime(d.index[-1]).date()),
            })
        if not rows:
            continue
        # 테마의 가격 움직임은 표본 내 한 종목의 급등보다 확산을 우선합니다.
        breadth_now = sum(1 for x in rows if x["ret20"] > 0) / len(rows) * 100.0
        breadth_before = sum(1 for x in rows if x.get("ret20_prev", 0) > 0) / len(rows) * 100.0
        for row in rows:
            row["breadth"] = breadth_now
            row["breadth_prev"] = breadth_before
        domestic_score = _score_theme(rows, benchmark)
        if not np.isfinite(domestic_score):
            continue
        lifecycle = _theme_lifecycle(rows, benchmark)
        # 국내 테마의 자체 강도와 미국장 선행신호를 결합합니다.
        lifecycle_score = safe_float(lifecycle.get("score"), np.nan)
        domestic_final = float(np.clip(
            domestic_score * .70 + lifecycle_score * .30, 0, 100
        )) if np.isfinite(lifecycle_score) else float(np.clip(domestic_score, 0, 100))
        us_info = _us_theme_signal(theme)
        us_available = bool(us_info.get("available"))
        us_contribution = safe_float(us_info.get("contribution"), 0.0) if us_available else 0.0
        final_score = float(np.clip(domestic_final + us_contribution, 0, 100))
        candidates.append({
            "theme": theme, "score": final_score, "base_score": domestic_score,
            "domestic_score": domestic_score, "lifecycle": lifecycle,
            "us_impulse": {"score": us_info.get("score"), "available": us_available,
                           "contribution": us_contribution, "mapping": us_info.get("mapping"),
                           "tickers": us_info.get("tickers", []), "used_tickers": us_info.get("tickers", []),
                           "as_of": us_info.get("as_of")},
            "us_status": "미국장 선행신호 반영" if us_available else "미국장 신호 미확보 · 국내 데이터로 평가",
            "rows": rows, "count": len(rows), "reason": config["reason"],
        })

    candidates.sort(key=lambda x: (x["score"], x["count"]), reverse=True)
    # 최소 기준을 통과한 테마만 노출하되, 후보가 적으면 억지로 채우지 않습니다.
    candidates = [x for x in candidates if x["score"] >= 38][:12]
    chain, details = [], {}
    total = len(candidates)
    for rank, item in enumerate(candidates, 1):
        stage = _theme_stage(item["score"], rank, total, item.get("lifecycle"))
        item["stage"] = stage
        item["rank"] = rank
        item["reason"] = item.get("reason") or "국내 ETF의 가격·상대강도·추세 확산을 평가합니다."
        chain.append((item["theme"], stage))
        details[item["theme"]] = item
    data = {
        "chain": chain, "details": details, "benchmark": benchmark,
        "us_market": us_snapshot, "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "engine_version": "ETF_THEME_FIRST_US_LEADING_V4",
    }
    st.session_state.future_engine_cache = {"time": datetime.now(), "data": data}
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
    st.caption("🔄 국내 ETF 테마 자동 발굴·강도 재평가 → 테마별 ETF 선별 → 매수 시점 분리")
    st.markdown('<div class="hero"><div class="hero-name">미래테마</div><div class="hero-code">유망 테마를 먼저 찾고, 테마별 추천 국내 ETF를 선별합니다</div></div>',unsafe_allow_html=True)
    c1,c2=st.columns([1,1])
    with c1:
        if st.button("🔄 미래테마 업데이트",use_container_width=True,key="future_theme_refresh"):
            st.session_state.theme_cache={}; st.session_state.price_cache={}; st.session_state.future_engine_cache=None; st.session_state.radar_cache=None; st.rerun()
    with c2:
        auto_update=st.checkbox("⚡ 자동 업데이트 · 30분",value=True,key="future_auto_update")
        if auto_update and st_autorefresh is not None:
            st_autorefresh(interval=30*60*1000,key="future_theme_autorefresh")
        elif auto_update and st_autorefresh is None:
            st.caption("자동 새로고침 모듈이 없어 화면 자동 갱신은 비활성입니다. 수동 업데이트 버튼을 이용해 주세요.")

    with st.spinner("국내 ETF의 유망 테마와 후보를 평가하는 중입니다…"):
        engine=build_future_theme_engine()
    chain=engine.get("chain",[])[:10]
    if not chain:
        st.warning("현재 가격 데이터에서 테마 후보를 찾지 못했습니다.")
        return
    bench=engine.get("benchmark",{})
    details=engine.get("details",{})
    st.caption(f'기준시각 {engine.get("updated","-")} · 국내 ETF 마스터에서 신규 키워드 테마 후보 자동 발굴 · 가격/상대강도/추세로 거래일 기준 재평가 · 상위 10개 표시')

    # 미래테마 화면 순위는 국내 가격·생애주기 지표로 정렬합니다.
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



def _domestic_theme_first_map():
    """국내 테마 엔진 순위로 ETF의 대표 테마를 정합니다. 미국 신호는 참조하지 않습니다."""
    try:
        engine = build_future_theme_engine()
        details = (engine or {}).get("details", {})
    except Exception:
        details = {}
    theme_items = sorted(list(details.items()), key=lambda kv: safe_float((kv[1] or {}).get("score"), -1), reverse=True)
    out = {}
    for theme_rank, (theme, info) in enumerate(theme_items, 1):
        info = info or {}
        theme_score = safe_float(info.get("domestic_score", info.get("base_score", info.get("score"))), np.nan)
        lifecycle = info.get("lifecycle") or {}
        lifecycle_state = str(lifecycle.get("state") or lifecycle.get("stage") or info.get("stage") or "관찰")
        for row in info.get("rows", []) or []:
            code = _normalize_etf_code(row.get("code"))
            if not code:
                continue
            if code not in out:
                out[code] = {
                    "theme": str(theme), "theme_rank": theme_rank, "theme_score": theme_score,
                    "lifecycle_state": lifecycle_state,
                    "theme_engine_score": safe_float(info.get("score"), np.nan),
                    "theme_count": int(info.get("count", len(info.get("rows", []) or []))),
                }
    return out


def build_final_targets(radar_data):
    """국내 테마를 먼저 선정하고 테마 내부 ETF를 평가하는 최종 타겟 엔진."""
    rows = radar_data.get('rows', []) if radar_data else []
    if not rows:
        return []
    benchmark = radar_data.get('benchmark', {}) if radar_data else {}
    bench20 = safe_float(benchmark.get('ret20'), np.nan)
    bench60 = safe_float(benchmark.get('ret60'), np.nan)
    benchmark_available = bool(benchmark.get('available', False)) and np.isfinite(bench20) and np.isfinite(bench60)

    domestic_theme_map = _domestic_theme_first_map()
    prepared = []
    for item in rows:
        x = dict(item)
        code = _normalize_etf_code(x.get('code'))
        product_name = str(x.get('name') or x.get('etf_name') or x.get('종목명') or '').strip().lower()
        # 국내 테마의 상승 타겟을 찾는 화면이므로 인버스/숏/베어 및 하락 2배 상품은 추천 대상에서 제외합니다.
        normalized_product_name = re.sub(r"[^0-9a-z가-힣]+", "", product_name)
        # 인버스/곱버스/숏/베어 상품은 상승 타겟에서 제외합니다.
        inverse_terms = ('인버스', '곱버스', 'inverse', 'bear', 'short', '울트라숏', '숏', '하락2x', '2xshort', '2xbear', '1xbear')
        # 원유·금 등 원자재 자체의 가격을 추종하는 상품은 제외합니다. 산업 ETF는 유지합니다.
        commodity_terms = (
            '원유', 'wti', 'brent', '천연가스선물', '천연가스', '금선물', '금현물',
            '골드선물', 'goldfutures', 'goldspot', '은선물', '은현물', '실버선물',
            '구리선물', '알루미늄선물', '농산물선물', '곡물선물', '원자재', '커머디티', 'commodity'
        )
        foreign_theme_terms = ('미국', '나스닥', 's&p', '스탠더드앤드푸어스', '중국', '차이나', 'china', '일본', 'japan', '인도', 'india', '베트남', 'vietnam', '유럽', 'europe', '글로벌', 'global', '월드', 'world', '해외', 'overseas')
        # 최종 추천 목록은 국내 상장 국내시장·산업테마 ETF만 대상으로 합니다.
        # 미국장 신호는 추천 상품으로 노출하지 않고, 관련 국내 ETF의 선행 신호로만 사용합니다.
        is_foreign_theme = any(term in product_name for term in foreign_theme_terms)
        if (not code or _is_safe_asset_etf(x)
                or any(term in normalized_product_name for term in inverse_terms)
                or any(re.sub(r"[^0-9a-z가-힣]+", "", term.lower()) in normalized_product_name for term in commodity_terms)
                or is_foreign_theme):
            continue
        x['recommendation_type'] = '국내시장 후보'
        x['is_broad_index_etf'] = False
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
        theme_info = domestic_theme_map.get(code, {})
        theme_score_value = safe_float(theme_info.get('theme_score'), np.nan)
        if not np.isfinite(theme_score_value):
            theme_score_value = safe_float(x.get('domestic_theme_score', x.get('theme_score')), np.nan)
        theme_name = str(theme_info.get('theme') or x.get('future_theme') or x.get('theme') or '미분류')
        if theme_name in {'', '미래테마 미연결', '기타', '미분류'}:
            theme_name = str(x.get('theme') or '미분류')
        lifecycle = str(theme_info.get('lifecycle_state') or x.get('lifecycle_state') or '관찰')
        prepared.append({
            **x, 'code': code, 'price': price, 'ret5': ret5, 'ret20': ret20,
            'ret60': ret60, 'ret120': ret120, 'rs20': rs20, 'rs60': rs60,
            'acceleration_raw': acceleration, 'trend_score_raw': trend_score,
            'ma20_value': ma20, 'ma60_value': ma60, 'ma120_value': ma120,
            'theme_score_raw': theme_score_value, 'future_theme': theme_name,
            'domestic_theme_rank': safe_float(theme_info.get('theme_rank'), np.nan),
            'domestic_theme_engine_score': safe_float(theme_info.get('theme_engine_score'), np.nan),
            'domestic_theme_count': safe_float(theme_info.get('theme_count'), np.nan),
            'lifecycle_state': lifecycle,
        })

    if not prepared:
        return []

    # 테마 엔진의 점수/표본 조건 때문에 테마 지도에서 빠진 ETF도 가격 기반으로 평가합니다.
    # 테마 연결은 후보를 전부 탈락시키는 필수조건이 아니라 분류·가산 정보입니다.
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
    # 국내 테마 ETF와 해외 대표지수 ETF를 같은 후보군에서 평가합니다.
    # 유형별로 점수를 따로 정규화해 순위 비교가 왜곡되는 것을 막던 분리 로직을 제거합니다.
    for key, values in rank_inputs.items():
        if key == 'theme_rank_pct':
            raw_values = [x.get('theme_score_raw') for x in prepared]
        elif key == 'rs20_pct':
            raw_values = [x.get('rs20') for x in prepared]
        elif key == 'rs60_pct':
            raw_values = [x.get('rs60') for x in prepared]
        elif key == 'ret20_pct':
            raw_values = [x.get('ret20') for x in prepared]
        elif key == 'ret60_pct':
            raw_values = [x.get('ret60') for x in prepared]
        elif key == 'acceleration_pct':
            raw_values = [x.get('acceleration_raw') for x in prepared]
        else:
            raw_values = [x.get('trend_score_raw') for x in prepared]
        pct = _cross_section_percentile(raw_values)
        for x, value in zip(prepared, pct):
            x[key] = value

    # 미국장 선행신호를 국내 ETF의 실제 테마와 연결해 최종 점수에 반영합니다.
    us_snapshot_ready = None
    for x in prepared:
        us_info = _us_theme_signal(str(x.get('future_theme') or x.get('theme') or ''), str(x.get('name') or ''))
        tickers = us_info.get('tickers', [])
        us_as_of = us_info.get('as_of') or ''
        mapping = us_info.get('mapping', '미국장 테마 연결 없음')
        us_available = bool(us_info.get('available'))
        us_score = safe_float(us_info.get('score'), np.nan)
        us_contribution = safe_float(us_info.get('contribution'), 0.0) if us_available else 0.0
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
        # STOCK_RADAR의 테마 선행 선정 원칙을 ETF 데이터에 맞게 적용합니다.
        theme_engine_score = safe_float(x.get('domestic_theme_engine_score'), np.nan)
        theme_rank = safe_float(x.get('domestic_theme_rank'), np.nan)
        theme_priority = float(np.clip(100 - (theme_rank - 1) * 8, 20, 100)) if np.isfinite(theme_rank) else np.nan
        if np.isfinite(theme_engine_score) and np.isfinite(domestic_score):
            theme_first_score = domestic_score * 0.70 + theme_engine_score * 0.30
        elif np.isfinite(domestic_score):
            theme_first_score = domestic_score
        else:
            theme_first_score = np.nan
        if np.isfinite(theme_first_score) and np.isfinite(theme_priority):
            theme_first_score = float(np.clip(theme_first_score * 0.90 + theme_priority * 0.10, 0, 100))

        link_score, link_type = (us_score, '미국장 테마 연결') if us_available else (np.nan, '미국장 미연결')
        score = float(np.clip(theme_first_score + us_contribution, 0, 100)) if np.isfinite(theme_first_score) else np.nan
        theme_factor_pct = domestic_theme_pct if np.isfinite(domestic_theme_pct) else np.nan
        recommendation_type = '해외 대표 지수 ETF' if x.get('is_broad_index_etf') else '국내시장 후보'

        x['us_signal_state'] = ('선행 우호' if us_available and us_score >= 55.0 else ('역풍' if us_available and us_score < 45.0 else ('중립' if us_available else '미확인')))
        x['us_theme_score'] = us_score
        x['us_theme_available'] = us_available
        x['us_theme_tickers'] = list(tickers)
        x['us_theme_score_as_of'] = us_as_of or None
        x['us_theme_mapping'] = mapping
        x['us_score_contribution'] = us_contribution if us_available else np.nan
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
            'us_theme_mapping': mapping,
            'us_link_score': round(link_score, 1) if np.isfinite(link_score) else np.nan,
            'us_link_type': link_type,
            'recommendation_type': recommendation_type,
            'domestic_target_score': round(domestic_score, 1) if np.isfinite(domestic_score) else np.nan,
            'domestic_theme_engine_score': round(theme_engine_score, 1) if np.isfinite(theme_engine_score) else np.nan,
            'domestic_theme_rank': int(theme_rank) if np.isfinite(theme_rank) else np.nan,
            'domestic_theme_priority_score': round(theme_priority, 1) if np.isfinite(theme_priority) else np.nan,
            'theme_first_score': round(theme_first_score, 1) if np.isfinite(theme_first_score) else np.nan,
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
        np.isfinite(safe_float(x.get('final_score'), np.nan)),
        safe_float(x.get('final_score'), -1),
        -safe_float(x.get('domestic_theme_rank'), 999),
        safe_float(x.get('relative_strength_score'), -1),
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

        theme_rank_value = safe_float(x.get('domestic_theme_rank'), np.nan)
        theme_engine_value = safe_float(x.get('domestic_theme_engine_score'), np.nan)
        if np.isfinite(theme_rank_value) and np.isfinite(theme_engine_value):
            reasons.append(f"국내 테마 우선 선정: {theme_name} 테마 순위 {theme_rank_value:.0f}위, 테마 점수 {theme_engine_value:.1f}/100을 반영했습니다.")
        else:
            reasons.append('국내 가격·상대강도·추세 자료를 기본으로 평가했습니다.')

        if bool(x.get('us_theme_available')):
            usv = safe_float(x.get('us_theme_score'), np.nan)
            usc = safe_float(x.get('us_score_contribution'), 0.0)
            ust = ', '.join(x.get('us_theme_tickers', [])[:5])
            reasons.append(f"미국장 선행신호: {ust} 기준 {usv:.0f}/100, 국내 ETF 최종 타겟 점수에 {usc:+.1f}점 반영했습니다(미국장 기준일 {x.get('us_theme_score_as_of') or '확인 불가'}).")
        else:
            reasons.append('미국장 선행신호: 관련 미국 티커 가격 또는 테마 연결을 확보하지 못해 점수에 가산하지 않았습니다.')

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
    domestic_targets = [
        x for x in (targets or [])
        if not _is_safe_asset_etf(x)
        and not any(term in str(x.get("name", "")).lower() for term in ("인버스", "곱버스", "inverse", "bear", "short", "울트라숏"))
        and not any(term in str(x.get("name", "")).lower() for term in ("미국", "나스닥", "s&p", "중국", "일본", "인도", "베트남", "유럽", "글로벌", "월드", "해외"))
        and np.isfinite(safe_float(x.get("final_score"), np.nan))
    ]
    shortlist = _diversified_target_shortlist(
        [x for x in domestic_targets if x.get("recommendation_type") == "국내시장 후보"], 5, 2
    )
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
    st.caption("국내 테마 ETF를 통합 평가하고, 미국장 선행신호·추세·과열도를 반영해 유망 후보만 표시합니다.")
    if st.button("🔄 최종 타겟 새로고침", use_container_width=True, key="final_target_refresh"):
        st.session_state.radar_cache=None; st.session_state.future_engine_cache=None; st.session_state.price_cache={}; st.rerun()
    with st.spinner("국내 ETF 테마·모멘텀·상대강도를 평가하는 중입니다…"):
        data=build_radar_data(); targets=build_final_targets(data)
    # 1~4단계 결과를 실제 장에서 사후 확인할 수 있도록 추천일·순위·가격을 기록합니다.
    record_daily_recommendations(targets, data)
    if not targets:
        st.warning("추천 후보를 만들지 못했습니다. ETF 목록 또는 가격 데이터 수집이 실패했거나, 가격 이력이 부족할 수 있습니다.")
        with st.expander("원인 확인"):
            _u = st.session_state.get("etf_universe", {})
            _fc = st.session_state.get("future_engine_cache") or {}
            _fd = _fc.get("data", {}) if isinstance(_fc, dict) else {}
            st.write(f"ETF 목록 수: {len(_u) if isinstance(_u, dict) else 0}")
            st.write(f"미래테마 평가 테마 수: {len(_fd.get('details', {})) if isinstance(_fd, dict) else 0}")
            st.write(f"가격 데이터 캐시 수: {len(st.session_state.get('price_cache', {}))}")
            st.caption("미국장 데이터가 확보되지 않으면 국내 가격·추세 기준으로만 후보를 평가합니다.")
        return
    # 국내 테마 ETF만 최종 추천 목록에 표시합니다. 미국장 신호는 국내 후보 평가에만 활용합니다.
    integrated_targets = sorted(
        targets,
        key=lambda x: (safe_float(x.get("final_score"), safe_float(x.get("target_score"), 0)), safe_float(x.get("entry_score"), 0)),
        reverse=True,
    )
    # 점수가 낮은 후보를 억지로 노출하지 않습니다. 후보가 없으면 명시적으로 안내합니다.
    display_threshold = 55.0
    visible_targets = [x for x in integrated_targets if safe_float(x.get("final_score"), safe_float(x.get("target_score"), 0)) >= display_threshold]
    st.markdown("### 🎯 통합 ETF 추천")
    st.caption("국내 테마 ETF를 종합점수순으로 표시합니다. 해외 대표지수 ETF는 추천 목록에서 제외하며, 미국장 신호는 국내 ETF 평가에만 활용합니다. 점수 55점 미만은 숨깁니다.")
    if visible_targets:
        _render_final_target_list(visible_targets, data, "통합 ETF 후보")
    else:
        st.info("현재 기준(55점)을 넘는 ETF가 없습니다. 낮은 점수의 종목을 억지로 추천하지 않고 관망을 우선합니다.")
    render_spot_tracking_panel()


def _action_guide_for_horizon(item, horizon="중기"):
    """상대강도와 추세를 함께 사용해 투자기간별 행동을 명시적으로 제시합니다.
    점수만 높다고 매수를 권하지 않으며, 자료 부족은 약세와 구분합니다.
    """
    price = safe_float(item.get("price"), 0.0)
    ma20 = safe_float(item.get("ma20_value"), np.nan)
    ma60 = safe_float(item.get("ma60_value"), np.nan)
    ma120 = safe_float(item.get("ma120_value"), np.nan)
    ret20 = safe_float(item.get("ret20"), np.nan)
    ret60 = safe_float(item.get("ret60"), np.nan)
    rs20 = safe_float(item.get("rs20"), np.nan)
    rs60 = safe_float(item.get("rs60"), np.nan)
    rsi = safe_float(item.get("entry_rsi14"), np.nan)
    risk = safe_float(item.get("entry_risk_penalty"), 0.0)
    target = safe_float(item.get("final_score"), 0.0)
    entry = safe_float(item.get("entry_score"), 0.0)
    if price <= 0 or not np.isfinite(ma20) or not np.isfinite(ret20):
        return {"action":"데이터 확인 필요", "why":"현재가·20일 추세·수익률 자료가 부족해 매수 판단을 보류합니다.", "buy1":None, "buy2":None, "invalid":None}
    relative_positive = (np.isfinite(rs20) and rs20 > 0) or (np.isfinite(rs60) and rs60 > 0)
    relative_strong = np.isfinite(rs20) and np.isfinite(rs60) and rs20 > 0 and rs60 > 0
    ma60_ok = np.isfinite(ma60) and ma60 > 0 and price >= ma60
    ma120_ok = np.isfinite(ma120) and ma120 > 0 and price >= ma120
    overheated = risk >= 18 or (np.isfinite(rsi) and rsi >= 74) or (price > ma20 * 1.10)
    if horizon == "장기":
        # 장기는 단기 MA20 이탈 하나로 자동 배제하지 않습니다. 장기 구조와 상대강도를 더 중시합니다.
        if target >= 68 and relative_positive and (ma120_ok or (np.isfinite(ret60) and ret60 > 0)) and not (np.isfinite(ret60) and ret60 < -18):
            if overheated:
                action = "장기 후보 우수 · 분할매수는 눌림 대기"
                why = "장기 관심도와 상대강도는 양호하지만 단기 과열 위험이 있어 한 번에 진입하지 말고 20일선 부근 조정을 기다립니다."
            elif ma60_ok or relative_strong:
                action = "장기 분할매수 검토"
                why = "장기 점수와 시장 대비 상대강도가 양호합니다. 계획 금액을 나누어 진입하고, 추가 매수는 추세 유지 시에만 검토합니다."
            else:
                action = "장기 후보 · 회복 확인 후 분할매수"
                why = "장기 후보 점수는 양호하지만 가격 추세가 아직 불안정합니다. 60일선 회복 또는 상대강도 개선을 확인한 뒤 분할 진입합니다."
        elif target >= 52 and (relative_positive or (np.isfinite(ret60) and ret60 > -8)):
            action = "장기 관심종목 · 소액 분할 또는 대기"
            why = "장기 구조가 확정적으로 강하다고 보기 어렵습니다. 예정 투자금 전액 진입보다 소액 분할 또는 추세 회복 대기가 적절합니다."
        else:
            action = "장기 신규매수 보류"
            why = "장기 점수와 추세·상대강도가 충분하지 않습니다. 시장이 하락해서가 아니라 해당 ETF 자체의 강도가 확인되지 않아 대기합니다."
        buy1 = min(price, ma20) if np.isfinite(ma20) and ma20 > 0 else price
        buy2 = min(buy1, ma60) if np.isfinite(ma60) and ma60 > 0 else buy1 * 0.97
        invalid = ma120 * 0.95 if np.isfinite(ma120) and ma120 > 0 else (ma60 * 0.94 if np.isfinite(ma60) and ma60 > 0 else None)
    else:
        if target >= 62 and entry >= 58 and relative_positive and ma60_ok and not overheated:
            action = "지금 1차 매수 검토"
            why = "ETF 자체의 상대강도와 중기 추세가 양호하고 진입 과열도 제한적입니다. 계획 금액 일부만 먼저 진입하고 손절·무효 기준을 함께 설정합니다."
        elif target >= 60 and relative_positive and overheated:
            action = "좋은 후보 · 눌림목 대기"
            why = "종목 강도는 괜찮지만 단기 상승폭·이격 또는 위험 감점이 커 추격매수보다 20일선 부근 조정을 기다립니다."
        elif target >= 55 and relative_positive and (np.isfinite(ret20) and ret20 > 0):
            action = "상대강도 후보 · 추세 회복 확인"
            why = "시장 대비 강도는 관찰되지만 중기 추세 또는 진입 조건이 완전히 맞지 않습니다. 20일선 회복과 60일선 지지를 확인합니다."
        elif target >= 50 and (relative_positive or (np.isfinite(ret60) and ret60 > 0)):
            action = "관심 유지 · 매수 신호 대기"
            why = "일부 긍정 신호는 있지만 추세와 상대강도가 충분히 일치하지 않습니다. 가격 회복이 확인되기 전에는 진입을 서두르지 않습니다."
        else:
            action = "중기 신규매수 보류"
            why = "ETF 자체의 상대강도·모멘텀이 약합니다. 시장 상황과 별개로 현재는 매수 우선순위를 낮춥니다."
        buy1 = min(price, ma20) if np.isfinite(ma20) and ma20 > 0 else price
        buy2 = min(buy1, ma60) if np.isfinite(ma60) and ma60 > 0 else buy1 * 0.97
        invalid = ma60 * 0.95 if np.isfinite(ma60) and ma60 > 0 else None
    return {"action":action, "why":why, "buy1":buy1, "buy2":buy2, "invalid":invalid}


def _action_guide_html(item, horizon="중기"):
    guide = _action_guide_for_horizon(item, horizon)
    def fmt(v):
        return money(v) if v is not None and np.isfinite(safe_float(v, np.nan)) and safe_float(v, 0) > 0 else "자료 부족"
    return (f'<div style="border:1px solid #64748b;border-radius:10px;padding:11px;margin:8px 0;background:rgba(30,41,59,.45);">'
            f'<div style="font-weight:800;font-size:15px;margin-bottom:5px;">{esc(horizon)} 행동 가이드: {esc(guide["action"])}</div>'
            f'<div style="font-size:12px;line-height:1.55;margin-bottom:7px;">{esc(guide["why"])}</div>'
            f'<div style="font-size:12px;line-height:1.7;">1차 검토 가격: <b>{esc(fmt(guide["buy1"]))}</b> · '
            f'눌림 추가 검토: <b>{esc(fmt(guide["buy2"]))}</b> · '
            f'추세 무효 참고: <b>{esc(fmt(guide["invalid"]))}</b></div>'
            f'<div style="font-size:10px;opacity:.75;margin-top:4px;">가격은 이동평균 기반 참고 구간이며 확정 매수·손절 가격이 아닙니다.</div></div>')


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
    domestic_theme_score = safe_float(primary.get("domestic_theme_engine_score"), np.nan)
    target_score = safe_float(primary.get("final_score"), np.nan)
    entry_score = safe_float(primary.get("entry_score"), np.nan)
    theme_score_text = f"{domestic_theme_score:.1f}/100" if np.isfinite(domestic_theme_score) else "자료 부족"
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
        <div style="flex:1;min-width:90px;background:rgba(100,116,139,.15);border-radius:9px;padding:9px;"><div style="font-size:11px;opacity:.8;">국내 테마 점수</div><div style="font-size:22px;font-weight:800;">{esc(theme_score_text)}</div></div>
      </div>
      <div style="font-size:13px;font-weight:700;margin-bottom:4px;">지금 판단: {esc(entry_status)}</div>
      <div style="font-size:12px;line-height:1.55;opacity:.9;">{esc(reason).replace('. ', '.<br>')}</div>
    </div>"""
    st.markdown(card_html, unsafe_allow_html=True)
    # 종목 평가와 투자기간별 진입 행동을 분리해 사용자가 실행할 다음 행동을 바로 알 수 있게 합니다.
    mid_tab, long_tab = st.tabs(["🔵 중기 매매 가이드", "🟢 장기 분할매수 가이드"])
    with mid_tab:
        st.markdown(_action_guide_html(primary, "중기"), unsafe_allow_html=True)
    with long_tab:
        st.markdown(_action_guide_html(primary, "장기"), unsafe_allow_html=True)

    b1, b2 = st.columns([1, 2])
    with b1:
        if st.button("⭐ 관심등록" if not already else "⭐ 관심등록됨", disabled=already, use_container_width=True, key=f"simple_watch_{group_label}_{code}"):
            add_watch(code); st.session_state.selected_code = code; st.rerun()
    with b2:
        with st.expander("왜 이 ETF인가? · 국내 테마 근거와 위험 보기", expanded=False):
            st.write(f"**추천 유형:** {rec_type}")
            st.write(f"**진입 지표 상태:** {entry_data}")
            st.write(f"**위험 감점:** {safe_float(primary.get('entry_risk_penalty'), 0):.1f}점")
            penalties = primary.get('entry_penalty_reasons', [])
            st.write("**진입 위험:** " + (" · ".join(penalties) if isinstance(penalties, (list, tuple)) and penalties else "계산된 감점 없음"))
            st.caption("미국장 선행신호는 실제 가격 데이터와 테마 연결이 확보된 경우에만 점수에 반영됩니다.")
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
                mid_alt, long_alt = st.tabs(["중기 행동", "장기 행동"])
                with mid_alt:
                    st.markdown(_action_guide_html(item, "중기"), unsafe_allow_html=True)
                with long_alt:
                    st.markdown(_action_guide_html(item, "장기"), unsafe_allow_html=True)
                ic1, ic2 = st.columns([1, 2])
                with ic1:
                    is_saved = ccode in st.session_state.watchlist
                    if st.button("관심등록" if not is_saved else "등록됨", disabled=is_saved, key=f"simple_watch_alt_{group_label}_{ccode}", use_container_width=True):
                        add_watch(ccode); st.session_state.selected_code = ccode; st.rerun()
                with ic2:
                    st.caption(f"국내 테마 점수: {item.get('domestic_theme_engine_score', '자료 부족')} · 테마 순위: {item.get('domestic_theme_rank', '미분류')}")

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
    text = f"{code} {name}".lower().replace(" ", "")
    priority = [
        ("반도체 장비·소부장", ("반도체장비", "반도체소부장", "칩장비", "소부장")),
        ("AI 반도체", ("ai반도체", "인공지능반도체", "hbm")),
        ("2차전지", ("2차전지", "배터리", "양극재", "음극재", "전고체", "리튬")),
        ("전력 인프라", ("전력기기", "전력망", "변압기", "전선", "전력인프라")),
        ("원자력", ("원자력", "원전", "우라늄")),
        ("방산", ("방산", "방위산업", "항공우주")),
        ("로봇", ("로봇", "로보틱스", "자동화")),
        ("조선", ("조선", "조선업")),
        ("바이오", ("바이오", "제약", "헬스케어")),
    ]
    for theme, keywords in priority:
        if any(word in text for word in keywords):
            return theme
    best = None
    hits = 0
    for theme, keywords in THEME_LEXICON.items():
        h = _theme_match_for_theme(text, keywords, theme)
        if h > hits:
            best, hits = theme, h
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

    # 미래테마 후보가 있어도 최종 점수/안전성 필터에서 전부 탈락할 수 있으므로,
    # 일반 ETF 대체 후보를 항상 함께 구성합니다. 그래야 미래테마 후보 목록의 존재와
    # 실제 최종 추천 가능 여부를 혼동하지 않습니다.
    universe = st.session_state.get("etf_universe", {})
    if not universe:
        try:
            universe = load_etf_universe()
            st.session_state.etf_universe = universe
        except Exception:
            universe = {}
    excluded = (
        "인버스", "곱버스", "bear", "inverse", "short", "숏", "울트라숏",
        "원유", "wti", "brent", "천연가스", "금선물", "금현물", "은선물",
        "은현물", "구리선물", "농산물선물", "곡물선물", "원자재", "commodity",
        "종합채권", "회사채", "국고채", "국채", "머니마켓", "mmf", "kofr",
        "cd금리", "초단기채"
    )
    broad = ("나스닥100", "나스닥 100", "s&p500", "s&p 500", "sp500")
    foreign = ("미국", "중국", "일본", "인도", "베트남", "유럽", "글로벌", "월드", "해외")
    fallback_added = 0
    for raw_code, raw_name in (universe.items() if isinstance(universe, dict) else []):
        code = _normalize_etf_code(raw_code)
        name = safe_etf_name(code, raw_name)
        low = str(name or "").lower().replace(" ", "")
        if not code or not name or name.startswith("ETF ") or code in targets:
            continue
        if any(term.replace(" ", "") in low for term in excluded):
            continue
        if any(term.replace(" ", "") in low for term in foreign) and not any(term.replace(" ", "") in low for term in broad):
            continue
        targets[code] = name
        fallback_added += 1
        if fallback_added >= 45:
            break

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

    # 속도 개선: 레이더 대상 가격을 한 종목씩 네트워크 호출하지 않고,
    # 캐시 만료/미보유 코드만 제한된 병렬 작업으로 먼저 수집합니다.
    # 세션 상태(price_cache)는 메인 스레드에서만 기록해 Streamlit 상태 경합을 방지합니다.
    _prefetch_now = datetime.now()
    _missing_codes = []
    for _code in targets:
        _cached_price = st.session_state.price_cache.get(str(_code).zfill(6))
        _cached_df = _cached_price.get("data") if _cached_price else None
        _ttl = 300 if _cached_df is not None and not _cached_df.empty else 45
        _age = (_prefetch_now - _cached_price["time"]).total_seconds() if _cached_price else 10**9
        if not _cached_price or _age >= _ttl:
            _missing_codes.append(str(_code).zfill(6))
    if _missing_codes:
        _parallel_results = {}
        with ThreadPoolExecutor(max_workers=8) as _price_pool:
            _price_futures = {_price_pool.submit(fetch_yahoo, _code): _code for _code in _missing_codes}
            for _future in as_completed(_price_futures):
                _code = _price_futures[_future]
                try:
                    _result_df = _future.result()
                    _parallel_results[_code] = _result_df if _result_df is not None else pd.DataFrame()
                except Exception:
                    _parallel_results[_code] = pd.DataFrame()
        _cache_write_time = datetime.now()
        for _code, _result_df in _parallel_results.items():
            st.session_state.price_cache[_code] = {"time": _cache_write_time, "data": _result_df}

    rows = []
    for code, target_name in targets.items():
        name = target_name or get_etf_name(code)
        if not name or str(name).startswith("ETF "):
            continue
        df = load_price_data(code)
        if df.empty or len(df) < 25:
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
            # 국내 ETF의 실제 테마명/상품명으로 미국 선행신호를 연결합니다.
            us_info = _us_theme_signal(str(item.get("future_theme") or item.get("theme") or ""), str(item.get("name") or ""))
            item["us_theme_score"] = safe_float(us_info.get("score"), np.nan)
            item["us_theme_available"] = bool(us_info.get("available"))
            item["us_theme_mapping"] = us_info.get("mapping", "미국장 테마 연결 없음")
            item["us_theme_as_of"] = us_info.get("as_of")
            item["us_theme_tickers"] = us_info.get("tickers", [])
            item["us_theme_score_as_of"] = us_info.get("as_of")
            item["us_score_contribution"] = safe_float(us_info.get("contribution"), 0.0) if item["us_theme_available"] else 0.0
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
    # 가격 이력이 일시적으로 비어 미래테마 기반 rows가 0개인 경우,
    # ETF 마스터에서 제한된 대체 후보를 평가합니다. 테마 엔진 결과가 있다는 이유만으로
    # 빈 화면을 반환하지 않으며, 실제 가격 데이터가 있는 ETF만 rows에 추가합니다.
    if not rows:
        universe = st.session_state.get("etf_universe", {})
        excluded_terms = (
            "인버스", "곱버스", "inverse", "bear", "short", "숏",
            "원유", "wti", "brent", "천연가스", "금선물", "금현물",
            "은선물", "은현물", "구리선물", "농산물선물", "곡물선물",
            "원자재", "commodity", "종합채권", "회사채", "국고채", "국채",
            "머니마켓", "mmf", "kofr", "cd금리", "초단기채"
        )
        foreign_terms = ("미국", "중국", "일본", "인도", "베트남", "유럽", "글로벌", "월드", "해외")
        index_terms = ("나스닥100", "나스닥 100", "s&p500", "s&p 500", "sp500")
        fallback_count = 0
        for raw_code, raw_name in (universe.items() if isinstance(universe, dict) else []):
            code = _normalize_etf_code(raw_code)
            name = safe_etf_name(code, raw_name)
            low = str(name or "").lower().replace(" ", "")
            if not code or not name or name.startswith("ETF "):
                continue
            if any(term.replace(" ", "") in low for term in excluded_terms):
                continue
            if any(term in low for term in foreign_terms) and not any(term.replace(" ", "") in low for term in index_terms):
                continue
            try:
                df = load_price_data(code)
                if df is None or df.empty or len(df) < 25:
                    continue
                d = calculate_indicators(df)
                if d is None or d.empty:
                    continue
                r = d.iloc[-1]
                current = safe_float(r.get("Close"), np.nan)
                if not np.isfinite(current) or current <= 0:
                    continue
                ma20 = safe_float(r.get("MA20"), current)
                ma60 = safe_float(r.get("MA60"), current)
                prev_close = safe_float(d["Close"].iloc[-2], current) if len(d) >= 2 else current
                ret1 = ((current / prev_close) - 1.0) * 100.0 if prev_close else 0.0
                item = {
                    "code": code, "name": name, "price": current,
                    "rsi": safe_float(r.get("RSI14"), 50),
                    "vr": safe_float(r.get("VOL_RATIO"), 1),
                    "ret1": ret1, "ret5": safe_float(r.get("RET5"), 0),
                    "ret20": safe_float(r.get("RET20"), 0),
                    "dist20": (current / ma20 - 1) * 100 if ma20 else 0,
                    "above20": current >= ma20, "above60": current >= ma60,
                    "raw": r.to_dict(),
                }
                item["rs20"] = item["ret20"] - benchmark["ret20"] if benchmark_available else np.nan
                item["benchmark_available"] = benchmark_available
                item["benchmark_as_of"] = benchmark.get("as_of") if benchmark_available else None
                item["theme"] = radar_theme_for(code, name)
                item["stage"] = radar_stage_for(item["theme"])
                item["opportunity"] = radar_score(item)
                item["overheat"] = radar_overheat_score(item)
                item.update({
                    "future_theme": "미래테마 미연결",
                    "future_theme_related": False,
                    "us_theme_score": np.nan,
                    "us_theme_available": False,
                    "us_theme_mapping": "미국장 테마 연결 미확인",
                    "us_theme_as_of": None,
                    "us_theme_tickers": [],
                    "us_theme_score_as_of": None,
                    "lifecycle_score": 0.0,
                    "lifecycle_state": "관찰",
                    "lead_score": 0.0,
                    "price_zone": "확인",
                    "cross_score": None if not benchmark_available else int(np.clip(round(item["opportunity"]), 0, 100)),
                    "cross_state": "⚪ 기준지수 미확보 · 점수 보류" if not benchmark_available else "🟡 가격 기반 대체 후보",
                    "benchmark_warning": None if benchmark_available else "기준지수 미확보",
                    "theme_score": 0.0,
                    "held": code in st.session_state.holdings,
                })
                rows.append(item)
                fallback_count += 1
                if fallback_count >= 45:
                    break
            except Exception:
                continue

    data = {
        "time": now, "rows": rows, "benchmark": benchmark,
        "target_key": target_key,
        "diagnostics": {
            "primary_target_count": len(targets),
            "price_prefetch_count": len(_missing_codes),
            "valid_primary_rows": sum(1 for x in rows if x.get("future_theme_related")),
            "total_valid_rows": len(rows),
            "fallback_used": bool(rows) and not any(x.get("future_theme_related") for x in rows),
            "benchmark_available": benchmark_available,
        },
    }
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
# ============================================================
# MAIN — 핵심 투자 흐름만 유지
# ============================================================

init_state()

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">ETF RADAR</div>
        <div class="app-subtitle">국내 테마 발굴 → 국내 ETF 선정 → 진입 판단</div>
    </div>
    """,
    unsafe_allow_html=True
)

nav = st.radio(
    "메뉴",
    ["🏆 ETF 추천", "🚀 미래테마", "📊 내 ETF"],
    horizontal=True,
    key="main_page",
    label_visibility="collapsed"
)

if nav == "🏆 ETF 추천":
    render_final_target()
elif nav == "🚀 미래테마":
    render_future_theme()
elif nav == "📊 내 ETF":
    render_my_etf()
