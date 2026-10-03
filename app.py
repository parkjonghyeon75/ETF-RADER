# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import os
import json
import time
from datetime import datetime, timedelta


# ============================================================
# ETF RADAR v12
# External ETF Search + Theme Radar
# Mobile Financial Dashboard
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# 기본 설정
# ============================================================

CACHE_FILE = "etf_universe_cache.json"

YF_SUFFIX = ".KS"


# ============================================================
# ETF RADAR 기본 ETF
# 검색 실패/외부 데이터 장애 시에도 핵심 ETF는 표시
# ============================================================

BASE_ETFS = {
    "395160": "\u004b\u004f\u0044\u0045\u0058 AI\uBC18\uB3C4\uCCB4\uD575\uC2EC\uC7A5\uBE44",
    "487240": "\u004b\u004f\u0044\u0045\u0058 AI\uBC18\uB3C4\uCCB4",
    "471990": "\u004b\u004f\u0044\u0045\u0058 AI\uBC18\uB3C4\uCCB4TOP2Plus",
    "133690": "\u0054\u0049\u0047\u0045\u0052 \uBBF8\uAD6D\uB098\uC2A4\uB2E4\uAFC4100",
    "360750": "\u0054\u0049\u0047\u0045\u0052 \uBBF8\uAD6DSP500",
    "458730": "\u0054\u0049\u0047\u0045\u0052 \uAE00\uB85C\uBC8CAI\u0026\uB85C\uBD07",
    "381170": "\u0054\u0049\u0047\u0045\u0052 \uBBF8\uAD6D\uD14C\uD06CTOP10 INDXX",
    "396500": "\u0054\u0049\u0047\u0045\u0052 \uBC18\uB3C4\uCCB4",
    "091160": "\u004b\u004f\u0044\u0045\u0058 \uBC18\uB3C4\uCCB4",
    "091180": "\u004b\u004f\u0044\u0045\u0058 \uC790\uB3D9\uCC28",
    "139260": "\u0054\u0049\u0047\u0045\u0052 200 IT",
    "305720": "\u004b\u004f\u0044\u0045\u0058 2\uCC28\uC804\uC9C0\uC0B0\uC5C5",
    "364690": "\u004b\u004f\u0044\u0045\u0058 \uD601\uC2E0\uAE30\uC220\uD14C\uB9C8\uC561\uD2F0\uBE0C",
    "117700": "\u004b\u004f\u0044\u0045\u0058 \uAC74\uC124",
    "140700": "\u004b\u004f\u0044\u0045\u0058 \uBCF4\uD5D8",
    "144600": "\u004b\u004f\u0044\uC5D0\uC2A4 \uC740\uD589",
    "102780": "\u004b\u004f\u0044\uC5D0\uC2A4 \uC0BC\uC131\uADF8\uB8F9",
    "261220": "\u004b\u004f\u0044\uC5D8\uC2A4 WTI\uC6D0\uC720\uC120\uBB3C(H)",
    "449170": "\u0054\u0049\u0047\u0045\u0052 \uAE00\uB85C\uBC8CAI\uC778\uD504\uB77C\uC561\uD2F0\uBE0C",
    "434060": "\u0054\u0049\u0047\u0045\u0052 \uAE00\uB85C\uBC8CAI\u0026\uBC18\uB3C4\uCCB4\uC561\uD2F0\uBE0C",
    "464240": "\u004b\u004f\u0044\u0045\u0058 AI\uC804\uB825\uD575\uC2EC\uC124\uBE44",
    "487130": "\u004b\u004f\u0044\u0045\u0058 AI\uC804\uB825\uC778\uD504\uB77C",
    "475050": "\u0041\u0043\u0045 \uAE00\uB85C\uBC8C\uBC18\uB3C4\uCCB4TOP4 Plus",
    "469150": "\u0041\u0043\u0045 AI\uBC18\uB3C4\uCCB4\uD3EC\uCEE4\uC2A4",
    "130730": "\u004b\u004f\u0053\u0045\u0046 \uB2E8\uAE30\uC790\uAE08",
    "161510": "\u0041\u0043\u0045 \uACE0\uBC30\uB2F9\uC8FC"
}


DEFAULT_WATCHLIST = [
    "395160",
    "487240",
    "471990",
    "133690",
    "360750",
    "458730"
]


# ============================================================
# 미래테마
# ============================================================

THEMES = {

    "AI \uBC18\uB3C4\uCCB4\u00b7\uD575\uC2EC\uC7A5\uBE44": {
        "stage": "\uD604\uC7AC \uC8FC\uB3C4",
        "emoji": "\U0001F534",
        "rank": 1,
        "etfs": ["395160", "487240", "471990", "396500"],
        "keywords": [
            "\uD83E\uDDE0 AI\uC5F0\uC0B0",
            "\uD83D\uDCA1 HBM/\uBA54\uBAA8\uB9AC",
            "\u2699\uFE0F \uBC18\uB3C4\uCCB4\uC7A5\uBE44",
            "\uD83D\uDCC8 \uB370\uC774\uD130\uC13C\uD130 CAPEX"
        ],
        "reason": (
            "AI \uC5F0\uC0B0\uC218\uC694\uAC00 \uD655\uB300\uB418\uBA74 GPU \uC790\uCCB4\uBFD0 \uC544\uB2C8\uB77C "
            "HBM\u00b7\uBA54\uBAA8\uB9AC\u00b7\uBC18\uB3C4\uCCB4 \uC7A5\uBE44\uB85C \uD22C\uC790\uBC94\uC704\uAC00 \uD655\uC0B0\uB429\uB2C8\uB2E4. "
            "\uD604\uC7AC\uB294 \uC2DC\uC7A5\uC5D0\uC11C \uBC18\uB3C4\uCCB4 \uD575\uC2EC\uC8FC\uB3C4\uC8FC\uAC00 \uC0C1\uB300\uC801\uC73C\uB85C \uBA3C\uC800 "
            "\uBC18\uC601\uB418\uB294\uC9C0 \uD655\uC778\uD558\uB294 \uAD6C\uAC04\uC785\uB2C8\uB2E4."
        ),
        "flow": (
            "AI \uC11C\uBC84 \u2192 GPU \u2192 HBM \u2192 \uBA54\uBAA8\uB9AC \u2192 "
            "\uBC18\uB3C4\uCCB4 \uC7A5\uBE44 \u2192 \uD6C4\uACF5\uC815"
        ),
        "bull": (
            "\uBC18\uB3C4\uCCB4 ETF \uAC70\uB798\uB7C9 \uC99D\uAC00 + "
            "\uC8FC\uC694 ETF \uC0C1\uB300\uAC15\uB3C4 \uC0C1\uC2B9 + "
            "\uC9C0\uC9C0\uC120 \uC720\uC9C0"
        ),
        "bear": (
            "\uC9C0\uC218\uAC00 \uC804\uACE0\uC810 \uC778\uADFC\uC5D0\uC11C \uAC70\uB798\uB7C9 \uAC10\uC18C + "
            "\uC774\uD3C9\uC120 \uD558\uD5A5\uC774\uD0C8 + "
            "\uBC18\uB3C4\uCCB4 ETF \uC0C1\uB300\uC57D\uC138"
        ),
        "watch": "\uD575\uC2EC\uC7A5\uBE44 \u2192 HBM \u2192 \uBA54\uBAA8\uB9AC \uC21C\uC73C\uB85C \uD655\uC0B0\uB418\uB294\uC9C0"
    },

    "AI \uC804\uB825\uC778\uD504\uB77C\u00b7\uC804\uB825\uC124\uBE44": {
        "stage": "\uB2E4\uC74C \uC218\uD61C",
        "emoji": "\U0001F7E0",
        "rank": 2,
        "etfs": ["464240", "487130", "449170"],
        "keywords": [
            "\u26A1 AI\uB370\uC774\uD130\uC13C\uD130",
            "\U0001F50C \uC804\uB825\uC218\uC694",
            "\uD83D\uDD0C \uBCC0\uC555\uAE30\u00b7\uBC30\uC804",
            "\U0001F4A1 \uC804\uB825\uB9DD"
        ],
        "reason": (
            "AI \uB370\uC774\uD130\uC13C\uD130\uAC00 \uD655\uB300\uB420\uC218\uB85D \uC804\uB825\uC218\uC694\uC640 "
            "\uC804\uB825\uB9DD\u00b7\uBCC0\uC555\u00b7\uBC30\uC804\uC124\uBE44\uC5D0 \uB300\uD55C \uD22C\uC790\uAC00 \uD544\uC694\uD569\uB2C8\uB2E4. "
            "\uBC18\uB3C4\uCCB4 \uD22C\uC790\uC758 \uB2E4\uC74C \uC2E4\uC81C \uC124\uBE44\uD22C\uC790\uB85C \uC790\uAE08\uC774 \uC774\uB3D9\uD558\uB294\uC9C0\uAC00 \uD575\uC2EC\uC785\uB2C8\uB2E4."
        ),
        "flow": (
            "AI \uB370\uC774\uD130\uC13C\uD130 \u2192 \uC804\uB825\uC218\uC694 \u2192 "
            "\uC804\uB825\uB9DD \u2192 \uBCC0\uC555\uAE30\u00b7\uBC30\uC804 \u2192 \uC804\uB825\uC124\uBE44"
        ),
        "bull": (
            "\uC804\uB825 ETF \uAC70\uB798\uB7C9 \uC99D\uAC00 + "
            "\uC0C1\uB300\uAC15\uB3C4 \uC0C1\uC2B9 + "
            "\uC7a5\uAE30 \uC774\uD3C9\uC120 \uC0C1\uD5a5"
        ),
        "bear": (
            "\uAC70\uB798\uB7C9 \uAE09\uAC10 + "
            "\uC8FC\uC694 \uC9C0\uC9C0\uC120 \uC774\uD0C8 + "
            "\uBC18\uB3C4\uCCB4 \uC0C1\uC2B9\uC5D0 \uB300\uBE44\uD55C \uC0C1\uB300\uC57D\uC138"
        ),
        "watch": "\uBC18\uB3C4\uCCB4 \uC0C1\uC2B9\uC5D0 \uB300\uD55C \uC804\uB825 ETF\uC758 \uC0C1\uB300\uAC15\uB3C4"
    },

    "AI \uB370\uC774\uD130\uC13C\uD130\u00b7\uC778\uD504\uB77C": {
        "stage": "\uB2E4\uC74C \uC218\uD61C",
        "emoji": "\U0001F7E0",
        "rank": 3,
        "etfs": ["449170", "434060", "381170"],
        "keywords": [
            "\U0001F5A5\uFE0F \uB370\uC774\uD130\uC13C\uD130",
            "\uD83C\uDFD7\uFE0F CAPEX",
            "\u2744\uFE0F \uB0C9\uAC01",
            "\u26A1 \uC804\uB825"
        ],
        "reason": (
            "AI \uC11C\uBC84 \uD22C\uC790\uAC00 \uD655\uB300\uB418\uBA74 \uC11C\uBC84\u00b7\uC804\uB825\u00b7\uB0C9\uAC01\u00b7\uB124\uD2B8\uC6CC\uD06C "
            "\uB4F1 \uC778\uD504\uB77C \uD22C\uC790\uAC00 \uB3D9\uBC18\uB418\uC5B4\uC57C \uD569\uB2C8\uB2E4. "
            "\uB370\uC774\uD130\uC13C\uD130 CAPEX \uD750\uB984\uC774 \uC2E4\uC81C ETF \uAC70\uB798\uB7C9\uC73C\uB85C \uD655\uC0B0\uB418\uB294\uC9C0\uAC00 \uC911\uC694\uD569\uB2C8\uB2E4."
        ),
        "flow": (
            "AI CAPEX \u2192 \uB370\uC774\uD130\uC13C\uD130 \u2192 \uC804\uB825\u00b7\uB0C9\uAC01 \u2192 "
            "\uB124\uD2B8\uC6CC\uD06C \u2192 \uC11C\uBC84\uC778\uD504\uB77C"
        ),
        "bull": (
            "\uB300\uD615 \uAE30\uC5C5 CAPEX \uC99D\uAC00 + "
            "\uAD00\uB828 ETF \uAC70\uB798\uB7C9 \uC99D\uAC00"
        ),
        "bear": (
            "CAPEX \uCD95\uC18C \uC2E0\uD638 + "
            "\uAC70\uB798\uB7C9 \uAC10\uC18C + "
            "\uC7A5\uAE30 \uCD94\uC138 \uC774\uD0C8"
        ),
        "watch": "\uB370\uC774\uD130\uC13C\uD130 \uAD00\uB828 ETF\uC758 \uC0C1\uB300\uAC15\uB3C4"
    },

    "\uD734\uBA38\uB178\uC774\uB4DC\u00b7\uB85C\uBCF4\uD2F1\uC2A4": {
        "stage": "\uCD08\uAE30 \uAD00\uC2EC",
        "emoji": "\U0001F7E1",
        "rank": 4,
        "etfs": ["458730", "364690"],
        "keywords": [
            "\U0001F916 \uD734\uBA38\uB178\uC774\uB4DC",
            "\u2699\uFE0F \uC561\uCD94\uC5D0\uC774\uD130",
            "\U0001F441\uFE0F \uBE44\uC804",
            "\U0001F9E0 AI"
        ],
        "reason": (
            "AI \uCD94\uB860\uAE30\uC220\uC774 \uB85C\uBD07\uC5D0 \uC801\uC6A9\uB418\uBA74 "
            "\uB85C\uBCF7\uC774 \uB2E8\uC21C \uC0B0\uC5C5\uC6A9 \uC124\uBE44\uC5D0\uC11C \uC2E0\uCCB4\uC640 \uD658\uACBD\uC744 \uC778\uC2DD\uD558\uB294 "
            "\uC9C0\uB2A5\uD615 \uC2DC\uC2A4\uD15C\uC73C\uB85C \uD655\uC7A5\uB420 \uAC00\uB2A5\uC131\uC774 \uC788\uC2B5\uB2C8\uB2E4. "
            "\uD604\uC7AC\uB294 \uC8FC\uB3C4\uC8FC\uBCF4\uB2E4\uB294 \uAD00\uB828 ETF \uAC70\uB798\uB7C9\uACFC \uC0C1\uB300\uAC15\uB3C4\uB97C \uD655\uC778\uD558\uBA74\uC11C \uCD08\uAE30 \uD750\uB984\uC744 \uAD00\uCC30\uD558\uB294 \uB2E8\uACC4\uB85C \uBD84\uB958\uD569\uB2C8\uB2E4."
        ),
        "flow": (
            "AI \uCD94\uB860 \u2192 \uBE44\uC804 \u2192 \uC81C\uC5B4 \u2192 "
            "\uC561\uCD94\uC5D0\uC774\uD130 \u2192 \uD734\uBA38\uB178\uC774\uB4DC"
        ),
        "bull": (
            "\uAD00\uB828 ETF \uAC70\uB798\uB7C9 \uAE09\uC99D + "
            "\uC7A5\uAE30 \uC774\uD3C9\uC120 \uC0C1\uD5A5\uC804\uD658"
        ),
        "bear": (
            "\uAC70\uB798\uB7C9 \uC5C6\uB294 \uC0C1\uC2B9 + "
            "\uC804\uACE0\uC810 \uBD84\uC7C1 + \uCD94\uC138 \uC774\uD0C8"
        ),
        "watch": "\uB85C\uBD07 ETF\uC758 \uAC70\uB798\uB7C9\uACFC \uC0C1\uB300\uAC15\uB3C4"
    },

    "\uC6B0\uC8FC\uD56D\uACF5\u00b7\uBC29\uC0B0": {
        "stage": "\uCD08\uAE30 \uAD00\uC2EC",
        "emoji": "\U0001F7E1",
        "rank": 5,
        "etfs": ["364690"],
        "keywords": [
            "\U0001F680 \uC6B0\uC8FC",
            "\U0001F6E9\uFE0F \uD56D\uACF5",
            "\U0001F6E1\uFE0F \uBC29\uC0B0",
            "\U0001F4E1 \uC704\uC131"
        ],
        "reason": (
            "\uC6B0\uC8FC\u00b7\uBC29\uC0B0\uC740 \uC815\uCC45\u00b7\uC218\uC8FC\u00b7\uC124\uBE44\uD22C\uC790\uAC00 \uC2E4\uC81C \uC2E4\uC801\uC73C\uB85C "
            "\uC774\uC5B4\uC9C0\uB294\uC9C0\uAC00 \uD575\uC2EC\uC785\uB2C8\uB2E4. \uC7A5\uAE30\uC801 \uD14C\uB9C8\uB85C\uC11C \uAD00\uCC30\uD558\uB418 "
            "\uB2E8\uAE30 \uC0C1\uC2B9\uB9CC\uC73C\uB85C \uC8FC\uB3C4\uD14C\uB9C8\uB77C\uACE0 \uD310\uB2E8\uD558\uC9C0 \uC54A\uB294 \uAD6C\uC870\uB85C \uAD00\uCC30\uD569\uB2C8\uB2E4."
        ),
        "flow": (
            "\uC815\uCC45 \u2192 \uC218\uC8FC \u2192 \uAC1C\uBC1C \u2192 \uC591\uC0B0 \u2192 "
            "\uC2E4\uC801 \u2192 \uAD00\uB828 ETF"
        ),
        "bull": "\uC218\uC8FC \uACF5\uC2DC + \uAC70\uB798\uB7C9 \uC99D\uAC00 + \uC7A5\uAE30\uCD94\uC138 \uC0C1\uD5A5",
        "bear": "\uC218\uC8FC \uBD80\uC9C4 + \uAC70\uB798\uB7C9 \uAC10\uC18C + \uC7A5\uAE30\uCD94\uC138 \uC774\uD0C8",
        "watch": "\uC2E4\uC801\uACFC \uAC70\uB798\uB7C9\uC774 \uB3D9\uBC18\uC99D\uAC00\uD558\uB294\uC9C0"
    },

    "SMR\u00b7\uC6D0\uC790\uB825\u00b7\uC5D0\uB108\uC9C0": {
        "stage": "\uCD08\uAE30 \uAD00\uC2EC",
        "emoji": "\U0001F7E1",
        "rank": 6,
        "etfs": ["364690"],
        "keywords": [
            "\u269B\uFE0F SMR",
            "\u26A1 \uC6D0\uC790\uB825",
            "\U0001F3ED \uC5D0\uB108\uC9C0",
            "\uD83D\uDD0C \uC804\uB825"
        ],
        "reason": (
            "SMR\uACFC \uC6D0\uC790\uB825\uC740 AI \uC804\uB825\uC218\uC694\uC640 \uACB0\uD569\uB420 \uACBD\uC6B0 \uC7A5\uAE30\uC801\uC778 "
            "\uAD00\uC2EC\uB300\uC0C1\uC774 \uB420 \uC218 \uC788\uC9C0\uB9CC, \uC2E4\uC81C \uC218\uC8FC\u00b7\uC778\uD5C8\uAC00\u00b7\uCC29\uACF5 "
            "\uB4F1 \uC2E4\uC81C\uD654 \uB2E8\uACC4\uB97C \uC5EC\uB7EC \uB2E8\uACC4 \uAC70\uCCD0 \uD655\uC778\uD560 \uD544\uC694\uAC00 \uC788\uC2B5\uB2C8\uB2E4."
        ),
        "flow": (
            "AI \uC804\uB825\uC218\uC694 \u2192 \uC6D0\uC790\uB825 \uD544\uC694\uC131 \u2192 "
            "SMR \uC218\uC8FC \u2192 \uC778\uD5C8\uAC00 \u2192 \uCC29\uACF5"
        ),
        "bull": "\uAD6D\uC81C\uC801 \uC218\uC8FC/\uCC29\uACF5 + \uAD00\uB828 ETF \uAC70\uB798\uB7C9 \uC99D\uAC00",
        "bear": "\uC0AC\uC5C5\uC9C0\uC5F0 + \uC218\uC8FC\uBD80\uC9C4 + \uAC70\uB798\uB7C9 \uAC10\uC18C",
        "watch": "\uC815\uCC45\uC774\uC288\uBCF4\uB2E4 \uC2E4\uC81C \uC218\uC8FC\u00b7\uCC29\uACF5 \uC9C4\uD589"
    }
}


# ============================================================
# Session State
# ============================================================

if "watchlist" not in st.session_state:
    st.session_state.watchlist = DEFAULT_WATCHLIST.copy()

if "selected_code" not in st.session_state:
    st.session_state.selected_code = DEFAULT_WATCHLIST[0]

if "search_keyword" not in st.session_state:
    st.session_state.search_keyword = ""

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "search_selected_code" not in st.session_state:
    st.session_state.search_selected_code = None

if "search_generation" not in st.session_state:
    st.session_state.search_generation = 0

if "analysis_open" not in st.session_state:
    st.session_state.analysis_open = {}

if "theme_open" not in st.session_state:
    st.session_state.theme_open = {}

if "etf_universe" not in st.session_state:
    st.session_state.etf_universe = None

if "universe_updated" not in st.session_state:
    st.session_state.universe_updated = False


# ============================================================
# 유틸리티
# ============================================================

def normalize_code(code):
    if code is None:
        return ""

    s = str(code).strip()

    if s.endswith(".KS"):
        s = s[:-3]

    if s.isdigit():
        return s.zfill(6)

    return s


def safe_float(v):
    try:
        return float(v)
    except Exception:
        return np.nan


def is_broken_text(text):
    if not isinstance(text, str):
        return False

    bad = [
        "\ufffd",
        "\u00c3",
        "\u00c2",
        "\u00ec",
        "\u00eb",
        "\u00ed",
        "\u00ef",
        "\u00e2",
        "\u00b0"
    ]

    return any(x in text for x in bad)


def get_display_name(code):
    code = normalize_code(code)

    if code in BASE_ETFS:
        return BASE_ETFS[code]

    if st.session_state.etf_universe is not None:
        u = st.session_state.etf_universe

        row = u[u["code"] == code]

        if not row.empty:
            name = str(row.iloc[0]["name"])

            if not is_broken_text(name):
                return name

    return code


def format_price(v):
    if pd.isna(v):
        return "-"

    return f"{v:,.0f}"


def format_pct(v):
    if pd.isna(v):
        return "-"

    return f"{v:+.2f}%"


# ============================================================
# KRX ETF 전체 목록
#
# pykrx를 사용하여 KRX ETF 종목을 가져옵니다.
# 외부망/거래소 응답 상태에 따라 시간이 걸릴 수 있으므로
# cache + session state를 함께 사용합니다.
# ============================================================

@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def load_krx_etf_universe():
    try:
        from pykrx import stock

        today = datetime.now()
        start = today - timedelta(days=10)

        date_list = pd.date_range(
            start=start,
            end=today,
            freq="D"
        )

        # 최근 영업일을 역순으로 검사
        for dt in reversed(date_list):

            date_str = dt.strftime("%Y%m%d")

            try:
                tickers = stock.get_etf_ticker_list(date_str)

                if tickers:

                    rows = []

                    for code in tickers:

                        code = normalize_code(code)

                        try:
                            name = stock.get_etf_ticker_name(code)
                        except Exception:
                            name = ""

                        if name:
                            rows.append({
                                "code": code,
                                "name": str(name),
                                "source": "KRX"
                            })

                    if rows:
                        df = pd.DataFrame(rows)

                        df = df.drop_duplicates(
                            subset=["code"]
                        )

                        return df

            except Exception:
                continue

    except Exception:
        pass

    return pd.DataFrame(
        columns=["code", "name", "source"]
    )


def get_etf_universe(force=False):

    if (
        force
        or st.session_state.etf_universe is None
    ):

        df = load_krx_etf_universe()

        if df is not None and not df.empty:

            # BASE ETF와 합쳐서 검색 안정성 확보
            base_rows = []

            for code, name in BASE_ETFS.items():
                base_rows.append({
                    "code": code,
                    "name": name,
                    "source": "BASE"
                })

            base_df = pd.DataFrame(base_rows)

            df = pd.concat(
                [base_df, df],
                ignore_index=True
            )

            df["code"] = df["code"].apply(
                normalize_code
            )

            df = df.drop_duplicates(
                subset=["code"],
                keep="first"
            )

            st.session_state.etf_universe = df

        else:

            base_rows = []

            for code, name in BASE_ETFS.items():
                base_rows.append({
                    "code": code,
                    "name": name,
                    "source": "BASE"
                })

            st.session_state.etf_universe = pd.DataFrame(
                base_rows
            )

    return st.session_state.etf_universe


# ============================================================
# ETF 검색
# ============================================================

def search_etfs(keyword):

    keyword = str(keyword).strip()

    if not keyword:
        return []

    df = get_etf_universe()

    if df is None or df.empty:
        return []

    q = keyword.lower()

    result = df[
        df["name"].astype(str).str.lower().str.contains(
            q,
            regex=False,
            na=False
        )
        |
        df["code"].astype(str).str.contains(
            q,
            regex=False,
            na=False
        )
    ].copy()

    # BASE ETF 우선
    result["priority"] = np.where(
        result["code"].isin(BASE_ETFS.keys()),
        0,
        1
    )

    result = result.sort_values(
        ["priority", "name"]
    )

    return result[
        ["code", "name", "source"]
    ].to_dict("records")


# ============================================================
# Yahoo Finance
# ============================================================

@st.cache_data(ttl=60 * 10, show_spinner=False)
def fetch_yahoo(code, period="1y"):

    code = normalize_code(code)

    if not code:
        return pd.DataFrame()

    ticker = code + YF_SUFFIX

    try:

        df = yf.download(
            ticker,
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):

            df.columns = [
                c[0] if isinstance(c, tuple) else c
                for c in df.columns
            ]

        needed = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]

        for col in needed:
            if col not in df.columns:
                return pd.DataFrame()

        df = df[needed].copy()

        for col in needed:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        df = df.dropna(
            subset=["Close"]
        )

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# 지표
# ============================================================

def calculate_indicators(df):

    df = df.copy()

    if df.empty:
        return df

    df["MA20"] = (
        df["Close"]
        .rolling(20)
        .mean()
    )

    df["MA60"] = (
        df["Close"]
        .rolling(60)
        .mean()
    )

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(
        0,
        np.nan
    )

    df["RSI"] = 100 - (
        100 / (1 + rs)
    )

    df["Volume20"] = (
        df["Volume"]
        .rolling(20)
        .mean()
    )

    df["VolumeRatio"] = (
        df["Volume"]
        / df["Volume20"].replace(0, np.nan)
    )

    df["Return20"] = (
        df["Close"]
        .pct_change(20)
        * 100
    )

    df["Return60"] = (
        df["Close"]
        .pct_change(60)
        * 100
    )

    return df


# ============================================================
# 가격 레벨
# ============================================================

def calculate_levels(df):

    if df.empty:
        return {}

    last = df.iloc[-1]

    current = safe_float(
        last["Close"]
    )

    ma20 = safe_float(
        last.get("MA20", np.nan)
    )

    ma60 = safe_float(
        last.get("MA60", np.nan)
    )

    low20 = safe_float(
        df["Low"].tail(20).min()
    )

    low60 = safe_float(
        df["Low"].tail(60).min()
    )

    high20 = safe_float(
        df["High"].tail(20).max()
    )

    high60 = safe_float(
        df["High"].tail(60).max()
    )

    support1 = low20
    support2 = low60

    breakout = max(
        high20,
        high60
    )

    risk = min(
        support1,
        support2
    )

    return {
        "current": current,
        "ma20": ma20,
        "ma60": ma60,
        "support1": support1,
        "support2": support2,
        "breakout": breakout,
        "risk": risk
    }


# ============================================================
# 판단
# ============================================================

def get_judgment(df):

    if df.empty:
        return {
            "trend": "-",
            "action": "-",
            "reason": "데이터가 없습니다.",
            "rsi": np.nan,
            "volume_ratio": np.nan,
            "score": 0
        }

    last = df.iloc[-1]

    close = safe_float(last["Close"])
    ma20 = safe_float(last.get("MA20"))
    ma60 = safe_float(last.get("MA60"))
    rsi = safe_float(last.get("RSI"))
    vr = safe_float(last.get("VolumeRatio"))

    score = 50

    if not pd.isna(ma20) and close > ma20:
        score += 10
    else:
        score -= 10

    if not pd.isna(ma60) and close > ma60:
        score += 15
    else:
        score -= 15

    if (
        not pd.isna(ma20)
        and not pd.isna(ma60)
        and ma20 > ma60
    ):
        score += 10

    if not pd.isna(vr):
        if vr >= 1.5:
            score += 10
        elif vr < 0.7:
            score -= 5

    if not pd.isna(rsi):

        if 50 <= rsi <= 70:
            score += 5

        elif rsi >= 75:
            score -= 5

        elif rsi < 35:
            score -= 5

    score = int(
        max(
            0,
            min(
                100,
                score
            )
        )
    )

    if (
        close > ma20
        and close > ma60
        and ma20 > ma60
    ):
        trend = "상승 추세"

    elif close > ma20:
        trend = "단기 상승 / 중기 확인"

    elif close > ma60:
        trend = "중기 유지 / 단기 약세"

    else:
        trend = "하락 추세"

    if score >= 75:

        if not pd.isna(rsi) and rsi >= 75:
            action = "추격보다 눌림 대기"

        else:
            action = "보유 / 눌림 분할"

    elif score >= 60:
        action = "눌림 시 분할 접근"

    elif score >= 45:
        action = "관망 / 지지 확인"

    else:
        action = "신규매수 보류"

    reasons = []

    if close > ma20:
        reasons.append("현재가가 MA20 위")
    else:
        reasons.append("현재가가 MA20 아래")

    if close > ma60:
        reasons.append("MA60 위에서 중기 추세 유지")
    else:
        reasons.append("MA60 아래")

    if not pd.isna(vr):

        if vr >= 1.5:
            reasons.append("거래량 증가")
        elif vr < 0.7:
            reasons.append("거래량 부족")

    if not pd.isna(rsi):

        if rsi >= 75:
            reasons.append("RSI 과열권")
        elif rsi <= 35:
            reasons.append("RSI 약세권")

    return {
        "trend": trend,
        "action": action,
        "reason": " / ".join(reasons),
        "rsi": rsi,
        "volume_ratio": vr,
        "score": score
    }


# ============================================================
# 차트
# ============================================================

def render_chart(df, name):

    if df.empty:
        st.warning("차트 데이터가 없습니다.")
        return

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.72, 0.28]
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="가격"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MA20"],
            name="MA20",
            mode="lines"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MA60"],
            name="MA60",
            mode="lines"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            name="거래량"
        ),
        row=2,
        col=1
    )

    fig.update_layout(
        title=name,
        height=520,
        margin=dict(
            l=10,
            r=10,
            t=45,
            b=10
        ),
        dragmode=False,
        hovermode="x unified",
        showlegend=True,
        xaxis_rangeslider_visible=False
    )

    # 모바일에서 차트 이동/확대 방지
    fig.update_xaxes(
        fixedrange=True,
        rangeslider_visible=False
    )

    fig.update_yaxes(
        fixedrange=True
    )

    fig.update_layout(
        xaxis2_rangeslider_visible=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": False,
            "doubleClick": False,
            "displayModeBar": False,
            "responsive": True
        }
    )


# ============================================================
# 가격 대응
# ============================================================

def render_price_response(df):

    levels = calculate_levels(df)

    if not levels:
        return

    current = levels["current"]

    st.markdown("### 💰 가격 대응 구간")

    data = pd.DataFrame([
        {
            "구간": "현재가",
            "가격": format_price(current),
            "대응": "현재 위치 확인"
        },
        {
            "구간": "1차 지지",
            "가격": format_price(levels["support1"]),
            "대응": "눌림 1차 확인"
        },
        {
            "구간": "2차 지지",
            "가격": format_price(levels["support2"]),
            "대응": "강한 조정 시 핵심 지지"
        },
        {
            "구간": "돌파 기준",
            "가격": format_price(levels["breakout"]),
            "대응": "거래량 동반 돌파 확인"
        },
        {
            "구간": "위험 기준",
            "가격": format_price(levels["risk"]),
            "대응": "추세 훼손 여부 확인"
        }
    ])

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 판단
# ============================================================

def render_judgment(df):

    j = get_judgment(df)

    st.markdown("### 🧭 현재 판단")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "종합점수",
        f"{j['score']} / 100"
    )

    c2.metric(
        "추세",
        j["trend"]
    )

    c3.metric(
        "RSI",
        "-" if pd.isna(j["rsi"])
        else f"{j['rsi']:.1f}"
    )

    st.info(
        f"**현재 대응:** {j['action']}\n\n"
        f"**판단 근거:** {j['reason']}"
    )


# ============================================================
# 시나리오
# ============================================================

def render_scenarios(df):

    levels = calculate_levels(df)

    if not levels:
        return

    current = levels["current"]
    breakout = levels["breakout"]
    support1 = levels["support1"]
    support2 = levels["support2"]

    st.markdown("### 🎯 대응 시나리오")

    st.markdown(
        f"""
**① 상승 시나리오**

현재가가 **{format_price(breakout)}원**을 거래량 증가와 함께 돌파하면
추세 연장 여부를 확인합니다.

→ 돌파 직후 급등하면 추격보다는 다음 눌림을 기다리는 전략이 유리합니다.


**② 눌림 시나리오**

**{format_price(support1)}원** 부근에서 지지가 확인되면
1차 눌림 구간으로 볼 수 있습니다.

→ 지지 후 거래량이 다시 증가하는지 확인합니다.


**③ 깊은 조정 시나리오**

**{format_price(support2)}원**까지 내려오면 중기 추세의
핵심 방어구간으로 봅니다.

→ 이 구간까지 이탈하면 기존 상승 시나리오를 다시 검토합니다.
"""
    )


# ============================================================
# ETF 분석
# ============================================================

def render_analysis(code):

    code = normalize_code(code)

    name = get_display_name(code)

    st.markdown(
        f"## {name}"
    )

    st.caption(
        f"종목코드 {code}"
    )

    with st.spinner("시장 데이터를 분석하는 중입니다..."):

        df = fetch_yahoo(code)

    if df.empty:

        st.error(
            "외부 시세 데이터를 가져오지 못했습니다. "
            "잠시 후 다시 시도해 주세요."
        )

        return

    df = calculate_indicators(df)

    last = df.iloc[-1]

    current = safe_float(
        last["Close"]
    )

    previous = safe_float(
        df.iloc[-2]["Close"]
    ) if len(df) >= 2 else np.nan

    change = (
        (current / previous - 1) * 100
        if previous
        and not pd.isna(previous)
        else np.nan
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "현재가",
        format_price(current),
        format_pct(change)
    )

    c2.metric(
        "MA20",
        format_price(last["MA20"])
    )

    c3.metric(
        "MA60",
        format_price(last["MA60"])
    )

    c4.metric(
        "거래량비",
        "-"
        if pd.isna(last["VolumeRatio"])
        else f"{last['VolumeRatio']:.2f}x"
    )

    render_judgment(df)

    render_price_response(df)

    render_scenarios(df)

    st.markdown("### 📈 가격 차트")

    render_chart(
        df,
        name
    )


# ============================================================
# 분석 버튼
# ============================================================

def analysis_button(code, key_prefix):

    code = normalize_code(code)

    state_key = (
        f"{key_prefix}_{code}"
    )

    if state_key not in st.session_state.analysis_open:
        st.session_state.analysis_open[state_key] = False

    opened = st.session_state.analysis_open[state_key]

    label = (
        "🔽 ETF 분석 닫기"
        if opened
        else
        "📊 ETF 분석"
    )

    if st.button(
        label,
        key=f"analysis_btn_{state_key}",
        use_container_width=True
    ):

        st.session_state.analysis_open[state_key] = not opened

        st.rerun()

    if st.session_state.analysis_open[state_key]:

        render_analysis(code)


# ============================================================
# 내 ETF
# ============================================================

def render_my_etf():

    st.markdown("# 📊 내 ETF")

    st.caption(
        "외부 ETF 목록 검색 → 선택 → 분석 → 보유목록 추가"
    )

    # --------------------------------------------------------
    # 검색
    # --------------------------------------------------------

    st.markdown("### 🔎 ETF 찾기")

    search_col1, search_col2 = st.columns(
        [4, 1]
    )

    with search_col1:

        keyword = st.text_input(
            "ETF 검색",
            value=st.session_state.search_keyword,
            placeholder="예: AI / 반도체 / 전력 / TIGER / KODEX",
            label_visibility="collapsed"
        )

    with search_col2:

        search_clicked = st.button(
            "검색",
            type="primary",
            use_container_width=True
        )

    if search_clicked:

        keyword = keyword.strip()

        st.session_state.search_keyword = keyword

        if keyword:

            results = search_etfs(
                keyword
            )

            st.session_state.search_results = results

            # 핵심:
            # 검색할 때마다 selectbox key 자체를 바꿈
            # Streamlit의 이전 위젯값이 새 검색결과를 덮어쓰는 문제 방지
            st.session_state.search_generation += 1

            if results:

                first_code = normalize_code(
                    results[0]["code"]
                )

                st.session_state.search_selected_code = first_code
                st.session_state.selected_code = first_code

            else:

                st.session_state.search_selected_code = None

        else:

            st.session_state.search_results = []
            st.session_state.search_selected_code = None

        st.rerun()

    # --------------------------------------------------------
    # 검색 결과
    # --------------------------------------------------------

    results = st.session_state.search_results

    if results:

        st.markdown(
            f"### 🔎 검색결과 {len(results)}개"
        )

        result_codes = [
            normalize_code(x["code"])
            for x in results
        ]

        selected_code = (
            st.session_state.search_selected_code
            if st.session_state.search_selected_code
            in result_codes
            else result_codes[0]
        )

        selected_index = result_codes.index(
            selected_code
        )

        # 검색마다 새로운 key
        search_select_key = (
            f"search_result_select_"
            f"{st.session_state.search_generation}"
        )

        selected_search = st.selectbox(
            "검색결과",
            result_codes,
            index=selected_index,
            key=search_select_key,
            format_func=lambda x:
                get_display_name(x)
        )

        selected_search = normalize_code(
            selected_search
        )

        st.session_state.search_selected_code = selected_search
        st.session_state.selected_code = selected_search

        # 한글을 selectbox 내부가 아닌 native markdown으로 별도 표시
        st.success(
            f"선택 ETF  |  "
            f"**{get_display_name(selected_search)}**  "
            f"({selected_search})"
        )

        if selected_search not in st.session_state.watchlist:

            if st.button(
                "➕ 내 ETF에 추가",
                use_container_width=True
            ):

                st.session_state.watchlist.append(
                    selected_search
                )

                st.success(
                    "내 ETF에 추가했습니다."
                )

                time.sleep(0.3)
                st.rerun()

        analysis_button(
            selected_search,
            "search"
        )

    elif st.session_state.search_keyword:

        st.warning(
            f"'{st.session_state.search_keyword}'에 대한 "
            "검색결과가 없습니다."
        )

        st.caption(
            "KRX ETF 목록을 새로고침한 뒤 다시 검색해 보세요."
        )

    # --------------------------------------------------------
    # ETF 목록 새로고침
    # --------------------------------------------------------

    if st.button(
        "🔄 ETF 시장목록 새로고침",
        use_container_width=True
    ):

        load_krx_etf_universe.clear()

        st.session_state.etf_universe = None

        st.session_state.universe_updated = True

        st.rerun()

    if st.session_state.universe_updated:

        st.success(
            "외부 ETF 시장목록을 새로 불러오도록 초기화했습니다."
        )

        st.session_state.universe_updated = False

    # --------------------------------------------------------
    # 내 ETF
    # --------------------------------------------------------

    st.divider()

    st.markdown("### ⭐ 내 ETF")

    watchlist = st.session_state.watchlist

    if not watchlist:

        st.info(
            "보유/관심 ETF가 없습니다."
        )

        return

    watch_codes = [
        normalize_code(x)
        for x in watchlist
    ]

    selected_watch = st.selectbox(
        "내 ETF 선택",
        watch_codes,
        format_func=lambda x:
            get_display_name(x),
        key="watchlist_select"
    )

    st.info(
        f"**{get_display_name(selected_watch)}** "
        f"({selected_watch})"
    )

    analysis_button(
        selected_watch,
        "watch"
    )

    # --------------------------------------------------------
    # 삭제
    # --------------------------------------------------------

    if st.button(
        "🗑 선택 ETF 삭제",
        use_container_width=True
    ):

        if selected_watch in st.session_state.watchlist:

            st.session_state.watchlist.remove(
                selected_watch
            )

            if not st.session_state.watchlist:
                st.session_state.watchlist = []

            st.rerun()


# ============================================================
# 테마 분석 점수
# ============================================================

def analyze_theme_etfs(codes):

    rows = []

    for code in codes:

        code = normalize_code(code)

        df = fetch_yahoo(code)

        if df.empty:
            continue

        df = calculate_indicators(df)

        j = get_judgment(df)

        last = df.iloc[-1]

        rows.append({
            "code": code,
            "name": get_display_name(code),
            "score": j["score"],
            "return20": safe_float(
                last.get("Return20")
            ),
            "return60": safe_float(
                last.get("Return60")
            ),
            "volume_ratio": safe_float(
                last.get("VolumeRatio")
            ),
            "rsi": safe_float(
                last.get("RSI")
            )
        })

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


# ============================================================
# 미래테마 카드
# ============================================================

def render_theme_card(theme_name, theme):

    stage = theme["stage"]
    emoji = theme["emoji"]

    stage_color = {
        "현재 주도": "🔴",
        "다음 수혜": "🟠",
        "초기 관심": "🟡"
    }.get(
        stage,
        "⚪"
    )

    st.markdown(
        f"## {emoji} {theme_name}"
    )

    st.markdown(
        f"### {stage_color} {stage}"
    )

    st.write(
        theme["reason"]
    )

    st.markdown(
        f"**자금 이동 경로**  \n"
        f"`{theme['flow']}`"
    )

    # 테마 ETF 분석
    df_theme = analyze_theme_etfs(
        theme["etfs"]
    )

    if not df_theme.empty:

        avg_score = df_theme["score"].mean()

        avg_return20 = df_theme[
            "return20"
        ].mean()

        avg_return60 = df_theme[
            "return60"
        ].mean()

        avg_volume = df_theme[
            "volume_ratio"
        ].mean()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "테마점수",
            f"{avg_score:.0f}/100"
        )

        c2.metric(
            "20일 흐름",
            format_pct(avg_return20)
        )

        c3.metric(
            "60일 흐름",
            format_pct(avg_return60)
        )

        c4.metric(
            "평균 거래량비",
            "-"
            if pd.isna(avg_volume)
            else f"{avg_volume:.2f}x"
        )

        st.markdown(
            "### 📊 테마 대표 ETF"
        )

        display_df = df_theme[
            [
                "code",
                "name",
                "score",
                "return20",
                "return60",
                "volume_ratio"
            ]
        ].copy()

        display_df.columns = [
            "코드",
            "ETF",
            "점수",
            "20일",
            "60일",
            "거래량비"
        ]

        display_df["20일"] = display_df[
            "20일"
        ].apply(
            lambda x:
            "-"
            if pd.isna(x)
            else f"{x:+.2f}%"
        )

        display_df["60일"] = display_df[
            "60일"
        ].apply(
            lambda x:
            "-"
            if pd.isna(x)
            else f"{x:+.2f}%"
        )

        display_df["거래량비"] = display_df[
            "거래량비"
        ].apply(
            lambda x:
            "-"
            if pd.isna(x)
            else f"{x:.2f}x"
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

    st.markdown("### 🔗 핵심 체크포인트")

    for item in theme["keywords"]:
        st.markdown(
            f"- {item}"
        )

    st.markdown(
        f"""
### 🚀 테마가 강해지는 조건

{theme['bull']}

### ⚠️ 테마가 약해지는 조건

{theme['bear']}

### 👀 다음에 볼 것

{theme['watch']}
"""
    )

    # 대표 ETF 개별 분석 버튼
    st.markdown(
        "### 📈 대표 ETF 상세분석"
    )

    for i, code in enumerate(theme["etfs"]):

        code = normalize_code(code)

        if code not in BASE_ETFS and (
            st.session_state.etf_universe is None
            or code not in st.session_state.etf_universe["code"].values
        ):
            continue

        st.markdown(
            f"**{get_display_name(code)}** "
            f"({code})"
        )

        analysis_button(
            code,
            f"theme_{theme_name}_{i}"
        )

        st.write("")


# ============================================================
# 미래테마
# ============================================================

def render_future_theme():

    st.markdown("# 🔮 미래테마 레이더")

    st.caption(
        "현재 주도 → 다음 수혜 → 초기 관심으로 자금 이동 가능성을 추적합니다."
    )

    st.info(
        "단순한 테마 목록이 아니라, "
        "각 테마의 시장 단계와 대표 ETF 흐름을 함께 확인하도록 구성했습니다."
    )

    # --------------------------------------------------------
    # 전체 테마 요약
    # --------------------------------------------------------

    st.markdown("## 🗺 테마 로드맵")

    roadmap = []

    for name, theme in THEMES.items():

        df_theme = analyze_theme_etfs(
            theme["etfs"]
        )

        if df_theme.empty:

            score = np.nan
            ret20 = np.nan
            volume = np.nan

        else:

            score = df_theme["score"].mean()
            ret20 = df_theme["return20"].mean()
            volume = df_theme["volume_ratio"].mean()

        roadmap.append({
            "단계": theme["stage"],
            "테마": name,
            "테마점수": score,
            "20일흐름": ret20,
            "거래량비": volume
        })

    roadmap_df = pd.DataFrame(
        roadmap
    )

    if not roadmap_df.empty:

        roadmap_df["테마점수"] = roadmap_df[
            "테마점수"
        ].apply(
            lambda x:
            "-"
            if pd.isna(x)
            else f"{x:.0f}"
        )

        roadmap_df["20일흐름"] = roadmap_df[
            "20일흐름"
        ].apply(
            lambda x:
            "-"
            if pd.isna(x)
            else f"{x:+.2f}%"
        )

        roadmap_df["거래량비"] = roadmap_df[
            "거래량비"
        ].apply(
            lambda x:
            "-"
            if pd.isna(x)
            else f"{x:.2f}x"
        )

        st.dataframe(
            roadmap_df,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # 테마 카드
    # --------------------------------------------------------

    for theme_name, theme in THEMES.items():

        st.divider()

        key = (
            f"theme_open_{theme_name}"
        )

        if key not in st.session_state.theme_open:
            st.session_state.theme_open[key] = False

        opened = st.session_state.theme_open[key]

        if st.button(
            (
                f"🔽 {theme['stage']} · "
                f"{theme_name} 분석 닫기"
                if opened
                else
                f"🔍 {theme['stage']} · "
                f"{theme_name} 분석"
            ),
            key=f"theme_btn_{theme_name}",
            use_container_width=True
        ):

            st.session_state.theme_open[key] = not opened

            st.rerun()

        if st.session_state.theme_open[key]:

            render_theme_card(
                theme_name,
                theme
            )


# ============================================================
# 헤더
# ============================================================

def render_header():

    st.markdown(
        """
# 📊 ETF RADAR

**ETF 검색 · 차트분석 · 가격대응 · 미래테마 레이더**

시장 전체에서 ETF를 찾고,
가격과 거래량을 함께 분석합니다.
"""
    )

    st.caption(
        f"데이터 기준 앱 실행시각: "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    render_header()

    tab1, tab2 = st.tabs(
        [
            "📊 내 ETF",
            "🔮 미래테마"
        ]
    )

    with tab1:
        render_my_etf()

    with tab2:
        render_future_theme()


main()