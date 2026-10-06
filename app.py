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
from datetime import datetime, date
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
    border: 1
# ============================================================
# CONSTANTS / FILES
# ============================================================

APP_VERSION = "FINAL_HORIZON"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WATCHLIST_FILE = os.path.join(BASE_DIR, "watchlist.json")
HOLDINGS_FILE = os.path.join(BASE_DIR, "holdings.json")
ETF_CACHE_FILE = os.path.join(BASE_DIR, "etf_universe_cache.json")


# ============================================================
# DEFAULT WATCHLIST
# ============================================================

DEFAULT_WATCHLIST = [
    "395160",
    "487240",
    "471990",
    "133690",
    "360750",
    "458730",
]


# ============================================================
# FUTURE THEME DEFINITIONS
# ============================================================

THEMES = {
    "AI 반도체": {
        "stage": "현재 주도",
        "seeds": [
            "AI",
            "반도체",
            "HBM",
            "메모리",
            "반도체",
            "AI반도체",
        ],
        "outlook": "AI 연산 수요와 고대역폭 메모리 중심의 구조적 성장 여부를 우선 확인합니다.",
    },

    "AI 소프트웨어·빅테크": {
        "stage": "다음 수혜",
        "seeds": [
            "AI",
            "소프트웨어",
            "빅테크",
            "클라우드",
            "플랫폼",
        ],
        "outlook": "AI 활용 확산이 소프트웨어와 플랫폼 기업의 실적 성장으로 연결되는지를 봅니다.",
    },

    "데이터센터·AI 인프라": {
        "stage": "다음 수혜",
        "seeds": [
            "데이터센터",
            "AI인프라",
            "인프라",
            "서버",
            "네트워크",
        ],
        "outlook": "AI 데이터센터 투자 확대에 따른 서버·네트워크·인프라 수요를 추적합니다.",
    },

    "전력 인프라": {
        "stage": "다음 수혜",
        "seeds": [
            "전력",
            "전력인프라",
            "전력설비",
            "전선",
            "변압기",
            "전기",
        ],
        "outlook": "AI 데이터센터 증가로 인한 전력 수요 확대가 관련 산업의 구조적 성장으로 이어지는지 확인합니다.",
    },

    "원자력": {
        "stage": "관심 확대",
        "seeds": [
            "원자력",
            "원전",
            "SMR",
            "원전설비",
        ],
        "outlook": "전력 수요 증가와 에너지 안보를 배경으로 원전 투자가 확대되는지 확인합니다.",
    },

    "냉각·열관리": {
        "stage": "초기 관심",
        "seeds": [
            "냉각",
            "열관리",
            "액침냉각",
            "공조",
            "칠러",
        ],
        "outlook": "고밀도 AI 서버의 발열 증가가 냉각 및 열관리 수요 증가로 연결되는지를 봅니다.",
    },

    "로봇·자율주행": {
        "stage": "관심 확대",
        "seeds": [
            "로봇",
            "자율주행",
            "자동화",
            "스마트팩토리",
        ],
        "outlook": "AI와 자동화 기술의 실제 산업 적용 확대 여부를 중심으로 봅니다.",
    },

    "방산·우주항공": {
        "stage": "관심 확대",
        "seeds": [
            "방산",
            "우주",
            "항공",
            "방위",
            "미사일",
        ],
        "outlook": "국방비 증가와 지정학적 긴장, 우주산업 투자 확대가 실적 성장으로 이어지는지 확인합니다.",
    },

    "2차전지·ESS": {
        "stage": "관심 확대",
        "seeds": [
            "2차전지",
            "배터리",
            "ESS",
            "전기차",
            "리튬",
        ],
        "outlook": "전기차와 ESS 수요 회복 및 배터리 산업의 업황 개선 여부를 확인합니다.",
    },

    "바이오·헬스케어": {
        "stage": "관심 확대",
        "seeds": [
            "바이오",
            "헬스케어",
            "제약",
            "의료",
        ],
        "outlook": "신약개발과 바이오 산업의 실적 및 자금 유입을 중심으로 확인합니다.",
    },

    "5G·통신": {
        "stage": "초기 관심",
        "seeds": [
            "5G",
            "통신",
            "네트워크",
        ],
        "outlook": "통신 인프라 투자와 네트워크 고도화 사이클을 확인합니다.",
    },

    "신재생에너지": {
        "stage": "초기 관심",
        "seeds": [
            "태양광",
            "풍력",
            "신재생",
            "친환경",
        ],
        "outlook": "정책과 금리 환경 변화가 신재생에너지 투자 회복으로 이어지는지를 확인합니다.",
    },

    "수소": {
        "stage": "초기 관심",
        "seeds": [
            "수소",
            "수소경제",
            "연료전지",
        ],
        "outlook": "수소 인프라와 연료전지 산업의 상용화 진전을 확인합니다.",
    },

    "친환경·탄소": {
        "stage": "초기 관심",
        "seeds": [
            "탄소",
            "친환경",
            "ESG",
            "탄소배출",
        ],
        "outlook": "탄소 규제와 친환경 전환이 실제 투자와 산업 수요로 연결되는지 확인합니다.",
    },

    "금융": {
        "stage": "관심 확대",
        "seeds": [
            "은행",
            "금융",
            "보험",
            "증권",
        ],
        "outlook": "금리와 경기 사이클, 밸류에이션 및 주주환원 흐름을 확인합니다.",
    },

    "자동차": {
        "stage": "관심 확대",
        "seeds": [
            "자동차",
            "차량",
            "모빌리티",
        ],
        "outlook": "자동차 업황과 전동화·자율주행 전환 속도를 확인합니다.",
    },

    "화장품·K뷰티": {
        "stage": "관심 확대",
        "seeds": [
            "화장품",
            "K뷰티",
            "뷰티",
            "미용",
        ],
        "outlook": "글로벌 소비 확대와 K뷰티 수출 성장 지속 여부를 확인합니다.",
    },

    "음식료·소비": {
        "stage": "관심 확대",
        "seeds": [
            "음식료",
            "소비",
            "식품",
            "유통",
        ],
        "outlook": "내수와 글로벌 소비재 수요의 안정적인 성장 여부를 확인합니다.",
    },

    "건설·인프라": {
        "stage": "관심 확대",
        "seeds": [
            "건설",
            "인프라",
            "SOC",
            "플랜트",
        ],
        "outlook": "국내외 인프라 투자 확대와 건설 업황 개선 여부를 확인합니다.",
    },

    "철강·금속": {
        "stage": "초기 관심",
        "seeds": [
            "철강",
            "금속",
            "철",
            "소재",
        ],
        "outlook": "글로벌 경기와 원자재 가격 사이클에 따른 업황 변화를 확인합니다.",
    },

    "원자재": {
        "stage": "초기 관심",
        "seeds": [
            "원자재",
            "Commodity",
            "원유",
            "구리",
        ],
        "outlook": "글로벌 경기와 공급망 변화에 따른 원자재 가격 흐름을 확인합니다.",
    },

    "금·귀금속": {
        "stage": "관심 확대",
        "seeds": [
            "금",
            "귀금속",
            "골드",
            "Gold",
        ],
        "outlook": "금리와 달러, 지정학적 리스크에 따른 안전자산 수요를 확인합니다.",
    },

    "중국": {
        "stage": "초기 관심",
        "seeds": [
            "중국",
            "China",
        ],
        "outlook": "중국 경기 부양과 증시 자금 유입 여부를 확인합니다.",
    },

    "미국 기술": {
        "stage": "현재 주도",
        "seeds": [
            "나스닥",
            "미국기술",
            "NASDAQ",
            "테크",
        ],
        "outlook": "미국 기술주의 이익 성장과 AI 투자 사이클을 중심으로 확인합니다.",
    },

    "반도체 장비·소부장": {
        "stage": "다음 수혜",
        "seeds": [
            "반도체장비",
            "소부장",
            "장비",
            "반도체소재",
        ],
        "outlook": "반도체 투자 확대가 장비와 소재 업체로 확산되는지를 확인합니다.",
    },
}


# ============================================================
# FUTURE THEME ORDER
# ============================================================

FUTURE_THEME_ORDER = [
    "AI 반도체",
    "AI 소프트웨어·빅테크",
    "데이터센터·AI 인프라",
    "전력 인프라",
    "원자력",
    "냉각·열관리",
    "로봇·자율주행",
    "방산·우주항공",
    "2차전지·ESS",
    "바이오·헬스케어",
    "5G·통신",
    "신재생에너지",
    "수소",
    "친환경·탄소",
    "금융",
    "자동차",
    "화장품·K뷰티",
    "음식료·소비",
    "건설·인프라",
    "철강·금속",
    "원자재",
    "금·귀금속",
    "중국",
    "미국 기술",
    "반도체 장비·소부장",
]


# ============================================================
# FUTURE CHAIN
# ============================================================

FUTURE_CHAIN = [
    ("AI 반도체", "현재 주도"),
    ("데이터센터·AI 인프라", "다음 수혜"),
    ("전력 인프라", "다음 수혜"),
    ("원자력", "관심 확대"),
    ("냉각·열관리", "초기 관심"),
]


# ============================================================
# FALLBACK ETF MASTER
# ============================================================

FALLBACK_ETFS = [
    ("069500", "KODEX 200"),
    ("229200", "KODEX 코스닥150"),
    ("133690", "TIGER 미국나스닥100"),
    ("360750", "TIGER 미국S&P500"),
    ("458730", "TIGER 미국배당다우존스"),
    ("395160", "KODEX AI반도체TOP2플러스"),
    ("487240", "KODEX 미국AI테크TOP10"),
    ("471990", "KODEX AI전력핵심설비"),
]


# ============================================================
# SAFE JSON
# ============================================================

def safe_read_json(path, default):
    try:
        if not os.path.exists(path):
            return default

        with open(path, "r", encoding="utf-8") as f:
            value = json.load(f)

        return value

    except Exception:
        return default


def safe_write_json(path, value):
    try:
        tmp = path + ".tmp"

        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(
                value,
                f,
                ensure_ascii=False,
                indent=2
            )

        os.replace(tmp, path)
        return True

    except Exception:
        return False


# ============================================================
# ETF CODE
# ============================================================

def _normalize_etf_code(code):
    if code is None:
        return ""

    s = str(code).strip()

    if s.endswith(".KS"):
        s = s[:-3]

    if s.endswith(".KQ"):
        s = s[:-3]

    s = re.sub(r"[^0-9]", "", s)

    if not s:
        return ""

    return s.zfill(6)


# ============================================================
# SAFE FLOAT
# ============================================================

def safe_float(value, default=0.0):
    try:
        if value is None:
            return default

        if isinstance(value, str):
            value = value.replace(",", "").replace("%", "").strip()

        value = float(value)

        if np.isnan(value) or np.isinf(value):
            return default

        return value

    except Exception:
        return default


# ============================================================
# SAFE INT
# ============================================================

def safe_int(value, default=0):
    try:
        return int(float(value))
    except Exception:
        return default


# ============================================================
# NUMBER FORMAT
# ============================================================

def money(value):
    value = safe_float(value, 0)

    if abs(value) >= 1000:
        return f"{value:,.0f}"

    if abs(value) >= 100:
        return f"{value:,.1f}"

    return f"{value:,.2f}"


def pct(value):
    value = safe_float(value, 0)

    sign = "+" if value > 0 else ""

    return f"{sign}{value:.2f}%"


# ============================================================
# NAME CLEANING
# ============================================================

def safe_etf_name(name):
    if name is None:
        return ""

    s = str(name).strip()

    if not s:
        return ""

    replacements = {
        "KODEX 200": "KODEX 200",
        "TIGER 200": "TIGER 200",
        "�": "",
        "&amp;": "&",
        "&quot;": '"',
        "&#39;": "'",
        "&lt;": "<",
        "&gt;": ">",
    }

    for a, b in replacements.items():
        s = s.replace(a, b)

    try:
        if s.count("Ã") >= 2 or s.count("Â") >= 2:
            s = s.encode("latin1").decode("utf-8")
    except Exception:
        pass

    return html.unescape(s)


# ============================================================
# WATCHLIST
# ============================================================

def load_watchlist():
    value = safe_read_json(
        WATCHLIST_FILE,
        DEFAULT_WATCHLIST.copy()
    )

    if not isinstance(value, list):
        value = DEFAULT_WATCHLIST.copy()

    result = []

    for code in value:
        c = _normalize_etf_code(code)

        if c and c not in result:
            result.append(c)

    return result


def save_watchlist():
    safe_write_json(
        WATCHLIST_FILE,
        st.session_state.get("watchlist", [])
    )


def add_watch(code):
    code = _normalize_etf_code(code)

    if not code:
        return

    if "watchlist" not in st.session_state:
        st.session_state.watchlist = load_watchlist()

    if code not in st.session_state.watchlist:
        st.session_state.watchlist.append(code)
        save_watchlist()


def remove_watch(code):
    code = _normalize_etf_code(code)

    if "watchlist" not in st.session_state:
        st.session_state.watchlist = load_watchlist()

    if code in st.session_state.watchlist:
        st.session_state.watchlist.remove(code)
        save_watchlist()


# ============================================================
# HOLDINGS
# ============================================================

def load_holdings():
    value = safe_read_json(
        HOLDINGS_FILE,
        {}
    )

    if not isinstance(value, dict):
        return {}

    return value


def save_holdings():
    safe_write_json(
        HOLDINGS_FILE,
        st.session_state.get("holdings", {})
    )


# ============================================================
# INITIAL SESSION STATE
# ============================================================

if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()

if "holdings" not in st.session_state:
    st.session_state.holdings = load_holdings()

if "selected_code" not in st.session_state:
    st.session_state.selected_code = "395160"

if "price_cache" not in st.session_state:
    st.session_state.price_cache = {}

if "etf_master_cache" not in st.session_state:
    st.session_state.etf_master_cache = None

if "future_theme_cache" not in st.session_state:
    st.session_state.future_theme_cache = None

if "radar_cache" not in st.session_state:
    st.session_state.radar_cache = {}

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()


# ============================================================
# ETF MASTER
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_krx_etf_master():
    """
    KRX ETF master.
    네트워크/API 상태에 따라 실패할 수 있으므로
    항상 빈 리스트를 반환할 수 있도록 방어합니다.
    """

    urls = [
        "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd",
        "https://openapi.krx.co.kr/contents/OPN/ETF/ETFList",
    ]

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120 Safari/537.36"
        ),
        "Referer": "https://data.krx.co.kr/",
    }

    for url in urls[:1]:
        try:
            payload = {
                "bld": "dbms/MDC/STAT/standard/MDCSTAT04601",
                "locale": "ko_KR",
                "tboxindTpCd": "ETF",
                "share": "1",
                "csvxls_isNo": "false",
            }

            r = requests.post(
                url,
                data=payload,
                headers=headers,
                timeout=12
            )

            if r.status_code != 200:
                continue

            data = r.json()

            rows = (
                data.get("OutBlock_1")
                or data.get("result")
                or []
            )

            result = []

            for row in rows:
                code = (
                    row.get("ISU_SRT_CD")
                    or row.get("isu_srt_cd")
                    or row.get("종목코드")
                )

                name = (
                    row.get("ISU_ABBRV")
                    or row.get("isu_abbrv")
                    or row.get("종목명")
                )

                code = _normalize_etf_code(code)
                name = safe_etf_name(name)

                if code and name:
                    result.append({
                        "code": code,
                        "name": name,
                        "source": "KRX",
                    })

            if result:
                return result

        except Exception:
            continue

    return []


# ============================================================
# NAVER ETF MASTER
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_naver_etf_master():
    """
    네이버 금융 ETF 목록 fallback.
    """

    result = []

    urls = [
        "https://finance.naver.com/api/sise/etfItemList.nhn",
        "https://finance.naver.com/api/sise/etfItemList.nhn?etfType=0",
    ]

    for url in urls:
        try:
            r = requests.get(
                url,
                headers={
                    "User-Agent":
                    "Mozilla/5.0 AppleWebKit/537.36 Chrome/120 Safari/537.36"
                },
                timeout=10
            )

            if r.status_code != 200:
                continue

            data = r.json()

            items = (
                data.get("result", {}).get("etfItemList")
                or data.get("etfItemList")
                or []
            )

            for item in items:
                code = _normalize_etf_code(
                    item.get("itemcode")
                    or item.get("code")
                )

                name = safe_etf_name(
                    item.get("itemname")
                    or item.get("name")
                )

                if code and name:
                    result.append({
                        "code": code,
                        "name": name,
                        "source": "NAVER",
                    })

            if result:
                return result

        except Exception:
            continue

    return []


# ============================================================
# LOAD ETF UNIVERSE
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def load_etf_universe():
    krx = fetch_krx_etf_master()
    naver = fetch_naver_etf_master()

    merged = {}

    for item in krx + naver:
        code = _normalize_etf_code(item.get("code"))
        name = safe_etf_name(item.get("name"))

        if not code:
            continue

        if code not in merged:
            merged[code] = {
                "code": code,
                "name": name,
                "source": item.get("source", ""),
            }
        else:
            if (
                len(name) > len(merged[code]["name"])
                and name
            ):
                merged[code]["name"] = name

    for code, name in FALLBACK_ETFS:
        code = _normalize_etf_code(code)

        if code not in merged:
            merged[code] = {
                "code": code,
                "name": name,
                "source": "FALLBACK",
            }

    result = list(merged.values())

    result.sort(
        key=lambda x: (
            safe_etf_name(x.get("name", "")),
            x.get("code", "")
        )
    )

    return result


# ============================================================
# ETF LOOKUP
# ============================================================

def get_etf_name(code):
    code = _normalize_etf_code(code)

    for item in load_etf_universe():
        if item.get("code") == code:
            return safe_etf_name(item.get("name"))

    for c, n in FALLBACK_ETFS:
        if _normalize_etf_code(c) == code:
            return n

    return code


def find_etfs(keyword="", limit=50):
    keyword = str(keyword or "").strip().lower()

    universe = load_etf_universe()

    if not keyword:
        return universe[:limit]

    result = []

    for item in universe:
        code = str(item.get("code", ""))
        name = safe_etf_name(item.get("name", ""))

        if (
            keyword in code.lower()
            or keyword in name.lower()
        ):
            result.append(item)

    return result[:limit]


# ============================================================
# YAHOO PRICE
# ============================================================

def fetch_yahoo(code, period="1y"):
    code = _normalize_etf_code(code)

    if not code:
        return pd.DataFrame()

    ticker = f"{code}.KS"

    try:
        df = yf.download(
            ticker,
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            try:
                df.columns = df.columns.get_level_values(0)
            except Exception:
                df.columns = [
                    str(c[0]) if isinstance(c, tuple) else str(c)
                    for c in df.columns
                ]

        df = df.reset_index()

        return normalize_df(df)

    except Exception:
        return pd.DataFrame()


# ============================================================
# NAVER HISTORY
# ============================================================

def fetch_naver_history(code, pages=30):
    code = _normalize_etf_code(code)

    if not code:
        return pd.DataFrame()

    rows = []

    headers = {
        "User-Agent":
        "Mozilla/5.0 AppleWebKit/537.36 Chrome/120 Safari/537.36"
    }

    for page in range(1, pages + 1):
        url = (
            f"https://fchart.stock.naver.com/sise.nhn"
            f"?symbol={code}&timeframe=day&count=200&requestType=0"
        )

        try:
            r = requests.get(
                url,
                headers=headers,
                timeout=10
            )

            if r.status_code != 200:
                break

            root = ET.fromstring(r.text)

            found = False

            for item in root.findall(".//item"):
                data = item.attrib.get("data", "")

                parts = data.split("|")

                if len(parts) < 6:
                    continue

                dt = parts[0]
                close = safe_float(parts[1], np.nan)
                open_ = safe_float(parts[2], np.nan)
                high = safe_float(parts[3], np.nan)
                low = safe_float(parts[4], np.nan)
                volume = safe_float(parts[5], np.nan)

                if not dt:
                    continue

                rows.append([
                    dt,
                    open_,
                    high,
                    low,
                    close,
                    volume
                ])

                found = True

            if found:
                break

        except Exception:
            break

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(
        rows,
        columns=[
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]
    )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    for c in [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]:
        df[c] = pd.to_numeric(
            df[c],
            errors="coerce"
        )

    df = (
        df.dropna(subset=["Date", "Close"])
        .drop_duplicates(subset=["Date"])
        .sort_values("Date")
        .reset_index(drop=True)
    )

    return df


# ============================================================
# NORMALIZE PRICE DATA
# ============================================================

def normalize_df(df):
    if df is None or df.empty:
        return pd.DataFrame()

    d = df.copy()

    rename = {}

    for col in d.columns:
        s = str(col).strip().lower()

        if s in {"date", "datetime", "index"}:
            rename[col] = "Date"
        elif s == "open":
            rename[col] = "Open"
        elif s == "high":
            rename[col] = "High"
        elif s == "low":
            rename[col] = "Low"
        elif s == "close":
            rename[col] = "Close"
        elif s in {"adj close", "adj_close"}:
            rename[col] = "Adj Close"
        elif s == "volume":
            rename[col] = "Volume"

    d = d.rename(columns=rename)

    if "Date" not in d.columns:
        if isinstance(d.index, pd.DatetimeIndex):
            d = d.reset_index()
            if "index" in d.columns:
                d = d.rename(columns={"index": "Date"})

    if "Date" not in d.columns:
        return pd.DataFrame()

    d["Date"] = pd.to_datetime(
        d["Date"],
        errors="coerce"
    )

    for c in [
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Volume"
    ]:
        if c in d.columns:
            d[c] = pd.to_numeric(
                d[c],
                errors="coerce"
            )

    if "Close" not in d.columns:
        return pd.DataFrame()

    if "Volume" not in d.columns:
        d["Volume"] = 0

    d = (
        d.dropna(subset=["Date", "Close"])
        .drop_duplicates(subset=["Date"])
        .sort_values("Date")
        .reset_index(drop=True)
    )

    return d


# ============================================================
# LOAD PRICE DATA
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def load_price_data_cached(code, period="1y"):
    code = _normalize_etf_code(code)

    if not code:
        return pd.DataFrame()

    df = fetch_yahoo(code, period=period)

    if df.empty:
        df = fetch_naver_history(code)

    if df.empty:
        return pd.DataFrame()

    return normalize_df(df)


def load_price_data(code, period="1y"):
    code = _normalize_etf_code(code)

    if not code:
        return pd.DataFrame()

    key = f"{code}_{period}"

    cache = st.session_state.price_cache

    if key in cache:
        try:
            cached = cache[key]

            if (
                isinstance(cached, pd.DataFrame)
                and not cached.empty
            ):
                return cached.copy()

        except Exception:
            pass

    df = load_price_data_cached(
        code,
        period=period
    )

    if not df.empty:
        cache[key] = df.copy()

    return df.copy()


# ============================================================
# INDICATORS
# ============================================================

def calculate_rsi(series, period=14):
    series = pd.to_numeric(
        series,
        errors="coerce"
    )

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss.replace(
        0,
        np.nan
    )

    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(close):
    ema12 = close.ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = close.ewm(
        span=26,
        adjust=False
    ).mean()

    macd = ema12 - ema26

    signal = macd.ewm(
        span=9,
        adjust=False
    ).mean()

    hist = macd - signal

    return macd, signal, hist


def calculate_indicators(df):
    if df is None or df.empty:
        return pd.DataFrame()

    d = df.copy()

    if "Close" not in d.columns:
        return pd.DataFrame()

    close = pd.to_numeric(
        d["Close"],
        errors="coerce"
    )

    volume = pd.to_numeric(
        d.get("Volume", 0),
        errors="coerce"
    ).fillna(0)

    d["MA20"] = close.rolling(20).mean()
    d["MA60"] = close.rolling(60).mean()
    d["MA120"] = close.rolling(120).mean()

    d["STD20"] = close.rolling(20).std()

    d["BB_MID"] = d["MA20"]
    d["BB_UPPER"] = (
        d["MA20"] +
        d["STD20"] * 2
    )
    d["BB_LOWER"] = (
        d["MA20"] -
        d["STD20"] * 2
    )

    d["RSI14"] = calculate_rsi(
        close,
        14
    )

    macd, signal, hist = calculate_macd(close)

    d["MACD"] = macd
    d["MACD_SIGNAL"] = signal
    d["MACD_HIST"] = hist

    d["VOL20"] = volume.rolling(20).mean()

    d["VOL_RATIO"] = (
        volume /
        d["VOL20"].replace(0, np.nan)
    )

    d["RET5"] = (
        close.pct_change(5) * 100
    )

    d["RET20"] = (
        close.pct_change(20) * 100
    )

    d["RET60"] = (
        close.pct_change(60) * 100
    )

    d["RET120"] = (
        close.pct_change(120) * 100
    )

    d["HIGH20"] = close.rolling(20).max()
    d["LOW20"] = close.rolling(20).min()

    d["HIGH60"] = close.rolling(60).max()
    d["LOW60"] = close.rolling(60).min()

    d["HIGH120"] = close.rolling(120).max()
    d["LOW120"] = close.rolling(120).min()

    d["DIST_MA20"] = (
        (close / d["MA20"]) - 1
    ) * 100

    d["DIST_MA60"] = (
        (close / d["MA60"]) - 1
    ) * 100

    return d


# ============================================================
# BENCHMARK
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def _benchmark_snapshot():
    """
    시장 기준값.
    KODEX 200을 기본 벤치마크로 사용합니다.
    """

    df = load_price_data_cached(
        "069500",
        period="1y"
    )

    if df.empty:
        return {
            "price": 0,
            "ret20": 0,
            "ret60": 0,
            "ma20": 0,
            "ma60": 0,
        }

    d = calculate_indicators(df)

    if d.empty:
        return {
            "price": 0,
            "ret20": 0,
            "ret60": 0,
            "ma20": 0,
            "ma60": 0,
        }

    r = d.iloc[-1]

    return {
        "price": safe_float(
            r.get("Close"),
            0
        ),
        "ret20": safe_float(
            r.get("RET20"),
            0
        ),
        "ret60": safe_float(
            r.get("RET60"),
            0
        ),
        "ma20": safe_float(
            r.get("MA20"),
            0
        ),
        "ma60": safe_float(
            r.get("MA60"),
            0
        ),
    }


# ============================================================
# LONG TERM HORIZON
# ============================================================

def long_term_horizon(d):
    if d is None or d.empty:
        return {
            "suitability": "데이터 부족",
            "score": 0,
            "structural_break": False,
        }

    r = d.iloc[-1]

    c = safe_float(
        r.get("Close"),
        0
    )

    ma20 = safe_float(
        r.get("MA20"),
        c
    )

    ma60 = safe_float(
        r.get("MA60"),
        c
    )

    ma120 = safe_float(
        r.get("MA120"),
        c
    )

    ret60 = safe_float(
        r.get("RET60"),
        0
    )

    ret120 = safe_float(
        r.get("RET120"),
        0
    )

    rsi = safe_float(
        r.get("RSI14"),
        50
    )

    score = 0

    score += 25 if c > ma120 else 0
    score += 20 if ma60 > ma120 else 0
    score += 15 if ma20 > ma60 else 0
    score += 15 if ret60 > 0 else 0
    score += 15 if ret120 > 0 else 0
    score += 10 if 40 <= rsi <= 72 else 0

    structural_break = (
        c < ma120 and
        ma60 < ma120 and
        ret60 < 0
    )

    if structural_break:
        suitability = "장기 구조 훼손"
    elif score >= 78:
        suitability = "장기 우호"
    elif score >= 60:
        suitability = "장기 확인"
    else:
        suitability = "장기 보수"

    return {
        "suitability": suitability,
        "score": int(score),
        "structural_break": structural_break,
    }


# ============================================================
# LEADING SIGNAL
# ============================================================

def leading_signal(r, benchmark_ret20=0):
    c = safe_float(
        r.get("Close"),
        0
    )

    ma20 = safe_float(
        r.get("MA20"),
        c
    )

    ma60 = safe_float(
        r.get("MA60"),
        c
    )

    rsi = safe_float(
        r.get("RSI14"),
        50
    )

    macd_hist = safe_float(
        r.get("MACD_HIST"),
        0
    )

    ret20 = safe_float(
        r.get("RET20"),
        0
    )

    vr = safe_float(
        r.get("VOL_RATIO"),
        1
    )

    score = 0

    score += 20 if c > ma20 else 0
    score += 15 if ma20 > ma60 else 0
    score += 20 if ret20 > benchmark_ret20 else 0
    score += 15 if macd_hist > 0 else 0
    score += 15 if 45 <= rsi <= 72 else 0
    score += 15 if vr >= 1 else 0

    if score >= 78:
        state = "강한 상승 선행"
    elif score >= 65:
        state = "상승 우위"
    elif score >= 50:
        state = "중립"
    else:
        state = "약세"

    return {
        "score": int(score),
        "state": state,
    }


# ============================================================
# OVERHEAT
# ============================================================

def radar_overheat_score(item):
    rsi = safe_float(
        item.get("rsi"),
        50
    )

    ret5 = safe_float(
        item.get("ret5"),
        0
    )

    dist20 = safe_float(
        item.get("dist20"),
        0
    )

    vr = safe_float(
        item.get("vr"),
        1
    )

    score = 0

    if rsi >= 80:
        score += 40
    elif rsi >= 75:
        score += 28
    elif rsi >= 70:
        score += 15

    if ret5 >= 12:
        score += 25
    elif ret5 >= 8:
        score += 18
    elif ret5 >= 5:
        score += 10

    if dist20 >= 15:
        score += 25
    elif dist20 >= 10:
        score += 18
    elif dist20 >= 7:
        score += 10

    if vr >= 2.5:
        score += 10
    elif vr >= 2:
        score += 7

    return min(
        int(score),
        100
    )


# ============================================================
# PRICE ZONE
# ============================================================

def validated_price_zone(r):
    c = safe_float(
        r.get("Close"),
        0
    )

    ma20 = safe_float(
        r.get("MA20"),
        c
    )

    ma60 = safe_float(
        r.get("MA60"),
        c
    )

    low20 = safe_float(
        r.get("LOW20"),
        c
    )

    high20 = safe_float(
        r.get("HIGH20"),
        c
    )

    rsi = safe_float(
        r.get("RSI14"),
        50
    )

    if c <= 0:
        return {
            "state": "무효",
            "low": 0,
            "high": 0,
            "reason": "가격 데이터 부족",
        }

    dist20 = (
        ((c / ma20) - 1) * 100
        if ma20
        else 0
    )

    if (
        ma20 > 0 and
        c < ma20 * 0.97 and
        c < ma60
    ):
        state = "무효"
        reason = "20일선과 중기 추세가 함께 훼손되었습니다."

    elif (
        rsi >= 75 or
        dist20 >= 10
    ):
        state = "추격금지"
        reason = "단기 과열 가능성이 높아 추격매수를 피합니다."

    elif (
        c >= ma20 * 0.97 and
        c <= ma20 * 1.03 and
        rsi <= 68
    ):
        state = "매수구간"
        reason = "20일선 부근에서 추세와 가격 위치가 양호합니다."

    elif (
        c < ma20 and
        c > ma60
    ):
        state = "눌림대기"
        reason = "중기 추세는 살아 있으나 단기 눌림 구간입니다."

    elif (
        low20 <= c <= high20
    ):
        state = "확인"
        reason = "가격 위치를 추가 확인할 필요가 있습니다."

    else:
        state = "확인"
        reason = "현재 가격 위치가 명확한 매수구간은 아닙니다."

    return {
        "state": state,
        "low": low20,
        "high": high20,
        "reason": reason,
    }


# ============================================================
# JUDGMENT
# ============================================================

def get_judgment(r):
    if r is None:
        return "데이터 부족"

    c = safe_float(
        r.get("Close"),
        0
    )

    ma20 = safe_float(
        r.get("MA20"),
        c
    )

    ma60 = safe_float(
        r.get("MA60"),
        c
    )

    rsi = safe_float(
        r.get("RSI14"),
        50
    )

    ret20 = safe_float(
        r.get("RET20"),
        0
    )

    if c <= 0:
        return "데이터 부족"

    if c < ma60 and ma20 < ma60:
        return "리스크 재검토"

    if rsi >= 78:
        return "추격매수 금지"

    if c < ma20 and c > ma60:
        return "눌림목 대기"

    if (
        c > ma20 and
        ma20 > ma60 and
        45 <= rsi <= 70 and
        ret20 > 0
    ):
        return "매수 검토"

    if (
        c > ma60 and
        ret20 > 0
    ):
        return "보유 유지"

    return "관찰"


# ============================================================
# ACTION
# ============================================================

def get_action(r):
    if r is None:
        return "가격 데이터 확인"

    zone = validated_price_zone(r)

    state = zone.get("state")

    if state == "매수구간":
        return "분할매수 검토"

    if state == "눌림대기":
        return "눌림 확인 후 접근"

    if state == "추격금지":
        return "추격매수 금지"

    if state == "무효":
        return "신규매수 보류"

    return "추세 확인"


# ============================================================
# FUTURE THEME SCORE
# ============================================================

def theme_name_match(name, seeds):
    name = str(name or "").lower()

    for seed in seeds:
        if str(seed).lower() in name:
            return True

    return False


def calculate_theme_etf_score(d):
    if d is None or d.empty:
        return 0

    r = d.iloc[-1]

    c = safe_float(
        r.get("Close"),
        0
    )

    ma20 = safe_float(
        r.get("MA20"),
        c
    )

    ma60 = safe_float(
        r.get("MA60"),
        c
    )

    ret20 = safe_float(
        r.get("RET20"),
        0
    )

    ret60 = safe_float(
        r.get("RET60"),
        0
    )

    rsi = safe_float(
        r.get("RSI14"),
        50
    )

    vr = safe_float(
        r.get("VOL_RATIO"),
        1
    )

    score = 0

    score += 25 if c > ma20 else 0
    score += 20 if ma20 > ma60 else 0
    score += 20 if ret20 > 0 else 0
    score += 15 if ret60 > 0 else 0
    score += 10 if 40 <= rsi <= 72 else 0
    score += 10 if vr >= 1 else 0

    return int(score)


# ============================================================
# THEME ETF MATCH
# ============================================================

def match_theme_etfs(theme, universe=None, limit=8):
    if universe is None:
        universe = load_etf_universe()

    info = THEMES.get(theme, {})

    seeds = info.get(
        "seeds",
        []
    )

    matches = []

    for item in universe:
        name = safe_etf_name(
            item.get("name")
        )

        if theme_name_match(
            name,
            seeds
        ):
            matches.append(item)

    if not matches:
        return []

    return matches[:limit]


# ============================================================
# FUTURE THEME CANDIDATES
# ============================================================

def discover_future_theme_candidates():
    universe = load_etf_universe()

    candidates = []

    benchmark = _benchmark_snapshot()

    for theme_rank, theme in enumerate(
        FUTURE_THEME_ORDER,
        start=1
    ):

        info = THEMES.get(
            theme,
            {}
        )

        seeds = info.get(
            "seeds",
            []
        )

        matched = []

        for item in universe:

            name = safe_etf_name(
                item.get("name")
            )

            if not theme_name_match(
                name,
                seeds
            ):
                continue

            code = _normalize_etf_code(
                item.get("code")
            )

            if not code:
                continue

            try:
                df = load_price_data(code)

                if df.empty:
                    continue

                d = calculate_indicators(df)

                if d.empty:
                    continue

                r = d.iloc[-1]

                theme_score = calculate_theme_etf_score(
                    d
                )

                lead = leading_signal(
                    r,
                    benchmark.get("ret20", 0)
                )

                matched.append({
                    "code": code,
                    "name": name,
                    "score": theme_score,
                    "lead_score": lead["score"],
                    "ret20": safe_float(
                        r.get("RET20"),
                        0
                    ),
                    "ret60": safe_float(
                        r.get("RET60"),
                        0
                    ),
                })

            except Exception:
                continue

        if not matched:
            continue

        matched.sort(
            key=lambda x: (
                x["score"],
                x["lead_score"],
                x["ret20"]
            ),
            reverse=True
        )

        top = matched[:5]

        avg_score = (
            np.mean(
                [x["score"] for x in top]
            )
            if top
            else 0
        )

        avg_ret20 = (
            np.mean(
                [x["ret20"] for x in top]
            )
            if top
            else 0
        )

        avg_ret60 = (
            np.mean(
                [x["ret60"] for x in top]
            )
            if top
            else 0
        )

        lead_avg = (
            np.mean(
                [x["lead_score"] for x in top]
            )
            if top
            else 0
        )

        stage = info.get(
            "stage",
            "초기 관심"
        )

        stage_bonus = {
            "현재 주도": 10,
            "다음 수혜": 8,
            "관심 확대": 6,
            "초기 관심": 3,
        }.get(
            stage,
            0
        )

        future_score = (
            avg_score * 0.40 +
            lead_avg * 0.25 +
            max(avg_ret20, 0) * 1.5 +
            max(avg_ret60, 0) * 0.35 +
            stage_bonus
        )

        future_score = min(
            max(future_score, 0),
            100
        )

        candidates.append({
            "theme": theme,
            "rank": theme_rank,
            "stage": stage,
            "future_score": float(future_score),
            "avg_score": float(avg_score),
            "avg_ret20": float(avg_ret20),
            "avg_ret60": float(avg_ret60),
            "lead_score": float(lead_avg),
            "etfs": top,
            "outlook": info.get(
                "outlook",
                ""
            ),
        })

    candidates.sort(
        key=lambda x: (
            x["future_score"],
            x["lead_score"],
            x["avg_score"]
        ),
        reverse=True
    )

    for idx, item in enumerate(
        candidates,
        start=1
    ):
        item["future_rank"] = idx

    return candidates


# ============================================================
# FINAL TARGET HORIZON SNAPSHOT
# ============================================================

def _final_horizon_snapshot(d, code):
    if d is None or d.empty:
        return {
            "long": "데이터 부족",
            "long_score": 0,
            "mid": "데이터 부족",
            "mid_score": 0,
            "short": "데이터 부족",
            "lead_score": 0,
            "price_zone": "확인",
            "focus": "확인 불가",
            "structural_break": False,
        }

    long = long_term_horizon(d)

    r = d.iloc[-1]

    c = safe_float(
        r.get("Close"),
        0
    )

    ma20 = safe_float(
        r.get("MA20"),
        c
    )

    ma60 = safe_float(
        r.get("MA60"),
        c
    )

    ma120 = safe_float(
        r.get("MA120"),
        c
    )

    r60 = safe_float(
        r.get("RET60"),
        0
    )

    bench = _benchmark_snapshot()

    rs20 = (
        safe_float(
            r.get("RET20"),
            0
        )
        -
        safe_float(
            bench.get("ret20"),
            0
        )
    )

    mid_score = (
        (25 if c > ma60 else 0) +
        (20 if ma20 > ma60 else 0) +
        (20 if ma60 > ma120 else 0) +
        (20 if r60 > 0 else 0) +
        (15 if rs20 > 0 else 0)
    )

    if mid_score >= 75:
        mid = "🟢 중기 상승"
    elif mid_score >= 55:
        mid = "🟡 중기 확인"
    else:
        mid = "🔴 중기 약세"

    lead = leading_signal(
        r,
        safe_float(
            bench.get("ret20"),
            0
        )
    )

    zone = validated_price_zone(r)

    overheat = radar_overheat_score({
        "rsi": safe_float(
            r.get("RSI14"),
            50
        ),
        "ret5": safe_float(
            r.get("RET5"),
            0
        ),
        "dist20": (
            ((c / ma20) - 1) * 100
            if ma20
            else 0
        ),
        "vr": safe_float(
            r.get("VOL_RATIO"),
            1
        ),
    })

    if (
        zone["state"] == "매수구간"
        and lead["score"] >= 72
        and overheat < 65
    ):
        short = "🔥 단기 진입 우위"

    elif zone["state"] == "눌림대기":
        short = "🟢 단기 눌림대기"

    elif zone["state"] == "추격금지":
        short = "🔴 단기 추격금지"

    elif zone["state"] == "무효":
        short = "🔴 단기 무효"

    else:
        short = "🟡 단기 확인"

    if (
        long.get("score", 0) >= 78
        and mid_score >= 55
    ):
        focus = "장기 중심"

    elif mid_score >= 75:
        focus = "중기 중심"

    elif (
        lead["score"] >= 72
        and zone["state"]
        in {"매수구간", "눌림대기"}
    ):
        focus = "단기 중심"

    else:
        focus = "관찰 중심"

    return {
        "long": long.get(
            "suitability",
            "확인 불가"
        ),
        "long_score": int(
            long.get("score", 0)
        ),
        "mid": mid,
        "mid_score": int(
            mid_score
        ),
        "short": short,
        "lead_score": int(
            lead.get("score", 0)
        ),
        "price_zone": zone.get(
            "state",
            "확인"
        ),
        "focus": focus,
        "structural_break": bool(
            long.get(
                "structural_break",
                False
            )
        ),
    }


# ============================================================
# FINAL HORIZON RECOMMENDATION
# ============================================================

def final_horizon_recommendation(h):
    """
    최종 타겟의 '주력 투자기간'을 하나만 선택합니다.

    장기 / 중기 / 단기 전략 상세는 기존 expander에서 제공하고,
    여기서는 사용자가 종목을 보는 순간 바로 이해할 수 있도록
    대표 추천 기간만 표시합니다.
    """

    if not h:
        return "⚪ 관찰", "radar-horizon-watch"

    if h.get("structural_break"):
        return "⚪ 관찰", "radar-horizon-watch"

    long_score = safe_int(
        h.get("long_score"),
        0
    )

    mid_score = safe_int(
        h.get("mid_score"),
        0
    )

    lead_score = safe_int(
        h.get("lead_score"),
        0
    )

    price_zone = str(
        h.get("price_zone", "")
    )

    short_text = str(
        h.get("short", "")
    )

    short_good = (
        "진입 우위" in short_text
    )

    # 1. 장기 구조가 가장 좋은 경우
    if (
        long_score >= 78
        and mid_score >= 55
    ):
        return (
            "🟢 장기추천",
            "radar-horizon-long"
        )

    # 2. 중기 추세가 명확한 경우
    if mid_score >= 75:
        return (
            "🔵 중기추천",
            "radar-horizon-mid"
        )

    # 3. 단기 진입 조건이 좋은 경우
    if (
        short_good
        and price_zone
        in {"매수구간", "눌림대기"}
        and lead_score >= 72
    ):
        return (
            "🟡 단기추천",
            "radar-horizon-short"
        )

    # 4. 단기 모멘텀이 강한데 장기/중기 조건은 아직 아닌 경우
    if (
        lead_score >= 78
        and price_zone == "매수구간"
        and long_score < 78
    ):
        return (
            "🟡 단기추천",
            "radar-horizon-short"
        )

    return (
        "⚪ 관찰",
        "radar-horizon-watch"
    )


# ============================================================
# FINAL TARGET BUILD
# ============================================================

def build_final_targets(radar_data):
    if not radar_data:
        return []

    future_themes = discover_future_theme_candidates()

    if not future_themes:
        return []

    future_map = {}

    for item in future_themes:
        future_map[
            item["theme"]
        ] = item

    candidates = []

    for item in radar_data:

        code = _normalize_etf_code(
            item.get("code")
        )

        if not code:
            continue

        theme = item.get(
            "theme",
            ""
        )

        future = future_map.get(
            theme
        )

        if future is None:
            continue

        radar_score = safe_float(
            item.get("score"),
            0
        )

        future_score = safe_float(
            future.get("future_score"),
            0
        )

        future_rank = safe_int(
            future.get("future_rank"),
            99
        )

        future_etfs = future.get(
            "etfs",
            []
        )

        future_etf_rank = 99

        for idx, etf in enumerate(
            future_etfs,
            start=1
        ):
            if _normalize_etf_code(
                etf.get("code")
            ) == code:
                future_etf_rank = idx
                break

        if future_etf_rank == 99:
            continue

        opportunity = safe_float(
            item.get("opportunity"),
            radar_score
        )

        rsi = safe_float(
            item.get("rsi"),
            50
        )

        ret5 = safe_float(
            item.get("ret5"),
            0
        )

        price_zone = str(
            item.get(
                "price_zone",
                ""
            )
        )

        # 과열 종목은 최종 타겟에서 제외
        if rsi >= 78:
            continue

        if ret5 >= 15:
            continue

        if price_zone == "무효":
            continue

        if opportunity < 45:
            continue

        # ----------------------------------------------------
        # FINAL SCORE
        #
        # 현재 투자조건 62%
        # 미래테마 18%
        # 미래테마 순위 anchor 20%
        # ----------------------------------------------------

        future_rank_anchor = max(
            0,
            100 - (
                max(future_rank - 1, 0)
                * 8
            )
        )

        final_score = (
            opportunity * 0.62
            + future_score * 0.18
            + future_rank_anchor * 0.20
        )

        # 미래테마 1위에 대한 추가 anchor
        if (
            future_rank == 1
            and opportunity >= 65
        ):
            final_score += 5

        # 테마 내 ETF 1위 가산
        if future_etf_rank == 1:
            final_score += 3

        final_score = min(
            final_score,
            100
        )

        if final_score >= 78:
            final_state = "강한 관심"
        elif final_score >= 68:
            final_state = "관심"
        elif final_score >= 58:
            final_state = "관찰"
        else:
            final_state = "보류"

        reason_parts = [
            f"미래테마 #{future_rank} {theme}",
            f"현재조건 {opportunity:.0f}",
            f"테마점수 {future_score:.0f}",
            f"가격구간 {price_zone}",
        ]

        candidates.append({
            "code": code,
            "name": safe_etf_name(
                item.get(
                    "name",
                    get_etf_name(code)
                )
            ),
            "theme": theme,
            "future_theme": theme,
            "future_theme_rank": future_rank,
            "future_etf_rank": future_etf_rank,
            "future_score": future_score,
            "opportunity": opportunity,
            "radar_score": radar_score,
            "final_score": float(final_score),
            "final_state": final_state,
            "final_reason": " · ".join(
                reason_parts
            ),
            "price": safe_float(
                item.get("price"),
                0
            ),
            "rsi": rsi,
            "ret5": ret5,
            "price_zone": price_zone,
            "theme_stage": future.get(
                "stage",
                ""
            ),
        })

    # 미래테마 rank anchor를 적용했지만
    # 동일 테마 내에서는 최종점수로 정렬
    candidates.sort(
        key=lambda x: (
            x["final_score"],
            -x["future_theme_rank"],
            -x["future_etf_rank"]
        ),
        reverse=True
    )

    # 동일 테마의 ETF가 지나치게 많이 최종타겟을 차지하지 않도록
    # 상위 후보를 우선 유지합니다.
    selected = []

    theme_count = {}

    for item in candidates:

        theme = item.get(
            "future_theme",
            ""
        )

        cnt = theme_count.get(
            theme,
            0
        )

        if cnt >= 2:
            continue

        selected.append(item)

        theme_count[theme] = cnt + 1

        if len(selected) >= 8:
            break

    for idx, item in enumerate(
        selected,
        start=1
    ):
        item["final_rank"] = idx

    return selected
# ============================================================
# RADAR DATA
# ============================================================

def build_radar_item(code, name=None, theme=""):
    code = _normalize_etf_code(code)

    if not code:
        return None

    if not name:
        name = get_etf_name(code)

    df = load_price_data(code)

    if df.empty:
        return None

    d = calculate_indicators(df)

    if d.empty:
        return None

    r = d.iloc[-1]

    bench = _benchmark_snapshot()

    price = safe_float(
        r.get("Close"),
        0
    )

    ma20 = safe_float(
        r.get("MA20"),
        price
    )

    ma60 = safe_float(
        r.get("MA60"),
        price
    )

    ma120 = safe_float(
        r.get("MA120"),
        price
    )

    rsi = safe_float(
        r.get("RSI14"),
        50
    )

    ret5 = safe_float(
        r.get("RET5"),
        0
    )

    ret20 = safe_float(
        r.get("RET20"),
        0
    )

    ret60 = safe_float(
        r.get("RET60"),
        0
    )

    vol_ratio = safe_float(
        r.get("VOL_RATIO"),
        1
    )

    rs20 = (
        ret20 -
        safe_float(
            bench.get("ret20"),
            0
        )
    )

    lead = leading_signal(
        r,
        safe_float(
            bench.get("ret20"),
            0
        )
    )

    zone = validated_price_zone(r)

    overheat = radar_overheat_score({
        "rsi": rsi,
        "ret5": ret5,
        "dist20": (
            ((price / ma20) - 1) * 100
            if ma20
            else 0
        ),
        "vr": vol_ratio,
    })

    # --------------------------------------------------------
    # CURRENT OPPORTUNITY SCORE
    # --------------------------------------------------------

    opportunity = 0

    opportunity += (
        20 if price > ma20 else 0
    )

    opportunity += (
        15 if ma20 > ma60 else 0
    )

    opportunity += (
        15 if ma60 > ma120 else 0
    )

    opportunity += (
        15 if ret20 > 0 else 0
    )

    opportunity += (
        10 if rs20 > 0 else 0
    )

    opportunity += (
        10
        if 45 <= rsi <= 72
        else 0
    )

    opportunity += (
        10 if vol_ratio >= 1 else 0
    )

    opportunity += (
        5 if zone["state"]
        in {"매수구간", "눌림대기"}
        else 0
    )

    opportunity -= (
        min(overheat * 0.35, 25)
    )

    opportunity = min(
        max(opportunity, 0),
        100
    )

    # --------------------------------------------------------
    # RADAR SCORE
    # --------------------------------------------------------

    radar_score = (
        opportunity * 0.65
        + lead["score"] * 0.25
        + max(min(rs20 * 1.5, 10), 0)
    )

    radar_score = min(
        max(radar_score, 0),
        100
    )

    if radar_score >= 80:
        radar_state = "🔥 강한 상승"
    elif radar_score >= 70:
        radar_state = "🟢 상승 우위"
    elif radar_score >= 58:
        radar_state = "🟡 관심"
    elif radar_score >= 45:
        radar_state = "⚪ 중립"
    else:
        radar_state = "🔴 약세"

    judgment = get_judgment(r)

    action = get_action(r)

    return {
        "code": code,
        "name": safe_etf_name(name),
        "theme": theme,
        "price": price,
        "change": (
            price -
            safe_float(
                d.iloc[-2]["Close"],
                price
            )
            if len(d) >= 2
            else 0
        ),
        "change_pct": (
            (
                price /
                safe_float(
                    d.iloc[-2]["Close"],
                    price
                ) - 1
            ) * 100
            if len(d) >= 2
            else 0
        ),
        "ma20": ma20,
        "ma60": ma60,
        "ma120": ma120,
        "rsi": rsi,
        "ret5": ret5,
        "ret20": ret20,
        "ret60": ret60,
        "vol_ratio": vol_ratio,
        "rs20": rs20,
        "lead_score": lead["score"],
        "lead_state": lead["state"],
        "overheat": overheat,
        "price_zone": zone["state"],
        "price_zone_reason": zone["reason"],
        "opportunity": float(opportunity),
        "score": float(radar_score),
        "radar_state": radar_state,
        "judgment": judgment,
        "action": action,
        "data": d,
    }


# ============================================================
# RADAR UNIVERSE
# ============================================================

def build_radar_universe(limit=None):
    universe = load_etf_universe()

    if limit:
        universe = universe[:limit]

    results = []

    progress = None

    try:
        progress = st.progress(
            0,
            text="ETF 레이더 계산 중..."
        )
    except Exception:
        progress = None

    total = len(universe)

    def worker(item):
        return build_radar_item(
            item.get("code"),
            item.get("name"),
        )

    # 네트워크 호출이 많기 때문에 병렬 처리
    max_workers = min(
        8,
        max(2, total)
    )

    completed = 0

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        futures = [
            executor.submit(
                worker,
                item
            )
            for item in universe
        ]

        for future in as_completed(futures):

            try:
                item = future.result()

                if item:
                    results.append(item)

            except Exception:
                pass

            completed += 1

            if progress is not None:
                try:
                    progress.progress(
                        completed / max(total, 1),
                        text=(
                            f"ETF 레이더 계산 중... "
                            f"{completed}/{total}"
                        )
                    )
                except Exception:
                    pass

    if progress is not None:
        try:
            progress.empty()
        except Exception:
            pass

    results.sort(
        key=lambda x: x.get(
            "score",
            0
        ),
        reverse=True
    )

    return results


# ============================================================
# RADAR CARD
# ============================================================

def render_radar_card(
    item,
    mode,
    hide_title=False
):

    if not item:
        return

    code = _normalize_etf_code(
        item.get("code")
    )

    name = safe_etf_name(
        item.get("name", "")
    )

    score = safe_int(
        item.get("score"),
        0
    )

    price = safe_float(
        item.get("price"),
        0
    )

    change_pct = safe_float(
        item.get("change_pct"),
        0
    )

    theme = item.get(
        "theme",
        ""
    )

    lead_state = item.get(
        "lead_state",
        "확인"
    )

    lead_score = safe_int(
        item.get("lead_score"),
        0
    )

    price_zone = item.get(
        "price_zone",
        "확인"
    )

    opportunity = safe_int(
        item.get("opportunity"),
        0
    )

    overheat = safe_int(
        item.get("overheat"),
        0
    )

    rsi = safe_float(
        item.get("rsi"),
        50
    )

    ret20 = safe_float(
        item.get("ret20"),
        0
    )

    vol_ratio = safe_float(
        item.get("vol_ratio"),
        1
    )

    judgment = item.get(
        "judgment",
        "관찰"
    )

    action = item.get(
        "action",
        "추세 확인"
    )

    # --------------------------------------------------------
    # FINAL TARGET ONLY:
    # 레이더 점수 옆에 대표 투자기간 표시
    # --------------------------------------------------------

    horizon_badge = ""

    if mode == "🎯 유망후보":

        h = item.get(
            "horizon_snapshot"
        )

        if h is None:

            d = item.get(
                "data"
            )

            if d is None or (
                not isinstance(
                    d,
                    pd.DataFrame
                )
            ):
                try:
                    df = load_price_data(
                        code
                    )
                    d = calculate_indicators(
                        df
                    )
                except Exception:
                    d = pd.DataFrame()

            h = _final_horizon_snapshot(
                d,
                code
            )

            item[
                "horizon_snapshot"
            ] = h

        recommendation, css_class = (
            final_horizon_recommendation(h)
        )

        horizon_badge = (
            f'<span class="radar-horizon-badge '
            f'{css_class}">'
            f'{esc(recommendation)}'
            f'</span>'
        )

    # --------------------------------------------------------
    # PRICE COLOR
    # --------------------------------------------------------

    change_class = (
        "positive"
        if change_pct > 0
        else
        "negative"
        if change_pct < 0
        else
        "neutral"
    )

    change_sign = (
        "+"
        if change_pct > 0
        else
        ""
    )

    # --------------------------------------------------------
    # CARD
    # --------------------------------------------------------

    st.markdown(
        '<div class="radar-card">',
        unsafe_allow_html=True
    )

    if not hide_title:
        st.markdown(
            f'''
            <div class="radar-title">
                {esc(name)}
            </div>
            <div class="radar-sub">
                {esc(code)}
            </div>
            ''',
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # SCORE / PRICE
    # --------------------------------------------------------

    st.markdown(
        f'''
        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-top:7px;
        ">
            <div>
                <div class="radar-label">
                    레이더 점수
                </div>
                <div class="radar-score">
                    {score}
                    {horizon_badge}
                </div>
            </div>

            <div style="text-align:right">
                <div class="radar-label">
                    현재가
                </div>
                <div class="radar-value">
                    {money(price)}
                    <span class="{change_class}">
                        {change_sign}{change_pct:.2f}%
                    </span>
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # BADGES
    # --------------------------------------------------------

    badge_html = ""

    if lead_score >= 78:
        badge_html += (
            '<span class="radar-badge radar-badge-op">'
            '선행강함'
            '</span>'
        )
    elif lead_score >= 65:
        badge_html += (
            '<span class="radar-badge">'
            '상승우위'
            '</span>'
        )

    if price_zone == "매수구간":
        badge_html += (
            '<span class="radar-badge radar-badge-op">'
            '매수구간'
            '</span>'
        )

    elif price_zone == "눌림대기":
        badge_html += (
            '<span class="radar-badge radar-badge-hold">'
            '눌림대기'
            '</span>'
        )

    elif price_zone == "추격금지":
        badge_html += (
            '<span class="radar-badge radar-badge-hot">'
            '추격금지'
            '</span>'
        )

    if overheat >= 65:
        badge_html += (
            '<span class="radar-badge radar-badge-hot">'
            '과열주의'
            '</span>'
        )

    if badge_html:
        st.markdown(
            f'''
            <div style="margin-top:6px;">
                {badge_html}
            </div>
            ''',
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    st.markdown(
        f'''
        <div class="radar-grid">

            <div class="radar-metric">
                <div class="radar-label">
                    RSI
                </div>
                <div class="radar-value">
                    {rsi:.1f}
                </div>
            </div>

            <div class="radar-metric">
                <div class="radar-label">
                    20일 수익
                </div>
                <div class="radar-value">
                    {pct(ret20)}
                </div>
            </div>

            <div class="radar-metric">
                <div class="radar-label">
                    거래량
                </div>
                <div class="radar-value">
                    {vol_ratio:.2f}x
                </div>
            </div>

            <div class="radar-metric">
                <div class="radar-label">
                    현재조건
                </div>
                <div class="radar-value">
                    {opportunity}
                </div>
            </div>

        </div>
        ''',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # THEME
    # --------------------------------------------------------

    if theme:
        st.markdown(
            f'''
            <div class="radar-note">
                <b>테마</b> · {esc(theme)}
            </div>
            ''',
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    st.markdown(
        f'''
        <div class="radar-note">
            <b>현재 상태</b> ·
            {esc(item.get("radar_state", "확인"))}
            · 선행점수 {lead_score}/100
            · 가격구간 {esc(price_zone)}
        </div>
        ''',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # TRADE INTERPRETATION
    # --------------------------------------------------------

    st.markdown(
        f'''
        <div class="radar-trade-title">
            판단
        </div>

        <div class="radar-action">
            {esc(judgment)}
        </div>

        <div class="radar-follow">
            <b>대응</b> · {esc(action)}
        </div>
        ''',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # TRADE LEVELS
    # --------------------------------------------------------

    d = item.get("data")

    if isinstance(d, pd.DataFrame) and not d.empty:

        r = d.iloc[-1]

        c = safe_float(
            r.get("Close"),
            price
        )

        ma20 = safe_float(
            r.get("MA20"),
            c
        )

        ma60 = safe_float(
            r.get("MA60"),
            c
        )

        low20 = safe_float(
            r.get("LOW20"),
            c
        )

        high20 = safe_float(
            r.get("HIGH20"),
            c
        )

        st.markdown(
            f'''
            <div class="radar-trade-grid">

                <div class="radar-trade-item">
                    <div class="radar-label">
                        기준가격
                    </div>
                    <div class="radar-trade-price">
                        {money(c)}
                    </div>
                    <div class="radar-trade-desc">
                        현재가
                    </div>
                </div>

                <div class="radar-trade-item">
                    <div class="radar-label">
                        1차 기준
                    </div>
                    <div class="radar-trade-price">
                        {money(ma20)}
                    </div>
                    <div class="radar-trade-desc">
                        20일선
                    </div>
                </div>

                <div class="radar-trade-item">
                    <div class="radar-label">
                        중기 기준
                    </div>
                    <div class="radar-trade-price">
                        {money(ma60)}
                    </div>
                    <div class="radar-trade-desc">
                        60일선
                    </div>
                </div>

                <div class="radar-trade-item">
                    <div class="radar-label">
                        20일 저점
                    </div>
                    <div class="radar-trade-price">
                        {money(low20)}
                    </div>
                    <div class="radar-trade-desc">
                        지지 후보
                    </div>
                </div>

                <div class="radar-trade-item">
                    <div class="radar-label">
                        20일 고점
                    </div>
                    <div class="radar-trade-price">
                        {money(high20)}
                    </div>
                    <div class="radar-trade-desc">
                        저항 후보
                    </div>
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
# FINAL TARGET HORIZON
# ============================================================

def render_final_target_horizon(code):

    df = load_price_data(code)

    if df.empty:
        st.info(
            "장기·중기·단기 판정에 필요한 가격 데이터를 확인하지 못했습니다."
        )
        return

    d = calculate_indicators(df)

    if d.empty:
        st.info(
            "장기·중기·단기 판정에 필요한 지표를 계산하지 못했습니다."
        )
        return

    h = _final_horizon_snapshot(
        d,
        code
    )

    with st.expander(
        "📆 투자기간별 전략 보기",
        expanded=False
    ):

        st.markdown(
            f'''
            <div class="final-horizon-grid">

                <div class="final-horizon-box">
                    <div class="final-horizon-label">
                        6~12개월 · 장기
                    </div>
                    <div class="final-horizon-value">
                        {esc(h["long"])}
                        · {h["long_score"]}/100
                    </div>
                </div>

                <div class="final-horizon-box">
                    <div class="final-horizon-label">
                        1~3개월 · 중기
                    </div>
                    <div class="final-horizon-value">
                        {esc(h["mid"])}
                        · {h["mid_score"]}/100
                    </div>
                </div>

                <div class="final-horizon-box">
                    <div class="final-horizon-label">
                        1~4주 · 단기
                    </div>
                    <div class="final-horizon-value">
                        {esc(h["short"])}
                    </div>
                </div>

            </div>
            ''',
            unsafe_allow_html=True
        )

        st.caption(
            "6~12개월=장기 구조 · "
            "1~3개월=중기 추세 · "
            "1~4주=단기 진입 타이밍 "
            f"| 현재 우선축: {h['focus']} "
            f"· 선행점수 {h['lead_score']}/100 "
            f"· 가격구간 {h['price_zone']}"
        )

        if h["structural_break"]:
            st.warning(
                "장기 구조적 훼손이 확인되어 "
                "신규매수보다 구조 재검토를 우선합니다."
            )


# ============================================================
# FINAL TARGET RENDER
# ============================================================

def render_final_target():

    st.markdown(
        '''
        <div class="section-title">
            🎯 최종 타겟
        </div>
        ''',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # RADAR DATA
    # --------------------------------------------------------

    radar_data = st.session_state.get(
        "radar_data"
    )

    if radar_data is None:

        with st.spinner(
            "최종 타겟 계산 중..."
        ):
            radar_data = build_radar_universe(
                limit=None
            )

        st.session_state.radar_data = (
            radar_data
        )

    if not radar_data:
        st.warning(
            "ETF 레이더 데이터를 계산하지 못했습니다."
        )
        return

    # --------------------------------------------------------
    # FINAL TARGETS
    # --------------------------------------------------------

    with st.spinner(
        "미래테마와 현재 모멘텀을 결합하여 최종 타겟을 선정하는 중..."
    ):

        top = build_final_targets(
            radar_data
        )

    if not top:
        st.info(
            "현재 조건에서 최종 타겟 후보를 찾지 못했습니다."
        )
        return

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    lead = top[0]

    st.markdown(
        f'''
        <div class="final-target-hero">

            <div class="final-target-title">
                🎯 오늘의 최종 관심축
            </div>

            <div class="final-target-sub">
                미래테마의 순위를 유지하면서
                현재 모멘텀·ETF 조건·가격 위치를 함께 반영한
                최종 후보입니다.
            </div>

        </div>
        ''',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # TARGET LIST
    # --------------------------------------------------------

    for item in top:

        # ----------------------------------------------------
        # Horizon snapshot을 한 번만 계산해서
        # radar score 옆 badge에서도 재사용
        # ----------------------------------------------------

        code = _normalize_etf_code(
            item["code"]
        )

        try:
            df = load_price_data(code)

            if not df.empty:
                d = calculate_indicators(df)

                if not d.empty:
                    item[
                        "horizon_snapshot"
                    ] = _final_horizon_snapshot(
                        d,
                        code
                    )

        except Exception:
            item[
                "horizon_snapshot"
            ] = None

        st.markdown(
            f'''
            <div class="final-target-rank">
                #{item["final_rank"]}
                · {esc(item["final_state"])}
                · 미래테마 #{item.get("future_theme_rank", "-")}
                {esc(item["future_theme"])}
                · 테마 내 ETF #{item.get("future_etf_rank", "-")}
                · 최종점수 {item.get("final_score", 0):.0f}
            </div>
            ''',
            unsafe_allow_html=True
        )

        st.caption(
            f'판단근거 · '
            f'{esc(item.get("final_reason", ""))}'
        )

        # ----------------------------------------------------
        # NAME + WATCH
        # ----------------------------------------------------

        name_col, watch_col = st.columns(
            [6.6, 1.0]
        )

        with name_col:

            st.markdown(
                f'''
                <div class="radar-title final-target-name">
                    {esc(item["name"])}
                    · {esc(item["code"])}
                </div>
                ''',
                unsafe_allow_html=True
            )

        with watch_col:

            code = _normalize_etf_code(
                item["code"]
            )

            already = (
                code in
                st.session_state.watchlist
            )

            if st.button(
                "⭐ 등록됨"
                if already
                else
                "⭐ 관심등록",
                disabled=already,
                use_container_width=False,
                key=(
                    f"final_watch_"
                    f"{code}_"
                    f"{item.get('final_rank', 0)}"
                )
            ):

                add_watch(code)

                st.session_state.selected_code = (
                    code
                )

                st.rerun()

        # ----------------------------------------------------
        # RADAR CARD
        # ----------------------------------------------------

        render_radar_card(
            item,
            "🎯 유망후보",
            hide_title=True
        )

        # ----------------------------------------------------
        # HORIZON DETAILS
        # ----------------------------------------------------

        render_final_target_horizon(
            item["code"]
        )

        st.markdown(
            '<div style="height:4px;"></div>',
            unsafe_allow_html=True
        )


# ============================================================
# FUTURE THEME RENDER
# ============================================================

def render_future_theme():

    st.markdown(
        '''
        <div class="section-title">
            🔭 미래테마
        </div>
        ''',
        unsafe_allow_html=True
    )

    cached = st.session_state.get(
        "future_theme_cache"
    )

    if cached is None:

        with st.spinner(
            "미래테마를 분석하는 중..."
        ):
            cached = discover_future_theme_candidates()

        st.session_state.future_theme_cache = (
            cached
        )

    if not cached:
        st.info(
            "현재 데이터를 기반으로 미래테마를 계산하지 못했습니다."
        )
        return

    # 상위 8개만 화면 표시
    top_themes = cached[:8]

    for idx, item in enumerate(
        top_themes,
        start=1
    ):

        theme = item["theme"]
        stage = item["stage"]

        if stage == "현재 주도":
            stage_class = "stage-core"
        elif stage == "다음 수혜":
            stage_class = "stage-next"
        elif stage == "관심 확대":
            stage_class = "stage-interest"
        else:
            stage_class = "stage-early"

        score = safe_int(
            item.get("future_score"),
            0
        )

        avg_score = safe_int(
            item.get("avg_score"),
            0
        )

        avg_ret20 = safe_float(
            item.get("avg_ret20"),
            0
        )

        avg_ret60 = safe_float(
            item.get("avg_ret60"),
            0
        )

        lead_score = safe_int(
            item.get("lead_score"),
            0
        )

        st.markdown(
            f'''
            <div class="future-theme-panel">

                <div class="theme-stage-wrap">
                    <span class="theme-stage-badge {stage_class}">
                        {esc(stage)}
                    </span>
                    <span class="radar-label">
                        미래테마 #{idx}
                    </span>
                </div>

                <div class="future-theme-title">
                    {esc(theme)}
                </div>

                <div class="future-theme-subtitle">
                    미래테마 점수 {score}/100
                    · 현재 ETF 평균 {avg_score}
                </div>

                <div class="theme-data-grid">

                    <div class="theme-data-box">
                        <div class="theme-data-label">
                            20일 평균
                        </div>
                        <div class="theme-data-value">
                            {pct(avg_ret20)}
                        </div>
                    </div>

                    <div class="theme-data-box">
                        <div class="theme-data-label">
                            60일 평균
                        </div>
                        <div class="theme-data-value">
                            {pct(avg_ret60)}
                        </div>
                    </div>

                    <div class="theme-data-box">
                        <div class="theme-data-label">
                            선행점수
                        </div>
                        <div class="theme-data-value">
                            {lead_score}
                        </div>
                    </div>

                    <div class="theme-data-box">
                        <div class="theme-data-label">
                            미래점수
                        </div>
                        <div class="theme-data-value">
                            {score}
                        </div>
                    </div>

                </div>

                <div class="theme-outlook">
                    <strong>전망</strong> ·
                    {esc(item.get("outlook", ""))}
                </div>

            </div>
            ''',
            unsafe_allow_html=True
        )

        # ----------------------------------------------------
        # THEME ETF
        # ----------------------------------------------------

        etfs = item.get(
            "etfs",
            []
        )

        if etfs:

            with st.expander(
                f"📌 {theme} 대표 ETF",
                expanded=False
            ):

                for rank, etf in enumerate(
                    etfs[:5],
                    start=1
                ):

                    st.markdown(
                        f'''
                        <div class="theme-etf-row">

                            <div class="theme-etf-name">
                                #{rank}
                                · {esc(etf.get("name", ""))}
                            </div>

                            <div class="theme-etf-code">
                                {esc(etf.get("code", ""))}
                                · ETF 점수 {safe_int(etf.get("score"), 0)}
                                · 선행 {safe_int(etf.get("lead_score"), 0)}
                                · 20일 {pct(etf.get("ret20", 0))}
                            </div>

                        </div>
                        ''',
                        unsafe_allow_html=True
                    )

        # ----------------------------------------------------
        # THEME ANALYSIS BUTTON
        # ----------------------------------------------------

        if etfs:

            btn_code = _normalize_etf_code(
                etfs[0].get("code")
            )

            if st.button(
                f"🔎 {theme} 대표 ETF 분석",
                key=f"theme_analysis_{theme}_{idx}",
                use_container_width=True
            ):
                st.session_state.selected_code = (
                    btn_code
                )

                st.session_state.jump_to_analysis = (
                    True
                )

                st.rerun()
# ============================================================
# MARKET RADAR
# ============================================================

def render_market_radar():

    st.markdown(
        '''
        <div class="section-title">
            📡 시장 레이더
        </div>
        ''',
        unsafe_allow_html=True
    )

    radar_data = st.session_state.get(
        "radar_data"
    )

    if radar_data is None:

        with st.spinner(
            "시장 레이더 계산 중..."
        ):
            radar_data = build_radar_universe()

        st.session_state.radar_data = (
            radar_data
        )

    if not radar_data:
        st.info(
            "시장 레이더 데이터를 계산하지 못했습니다."
        )
        return

    # 현재 시장에서 실제 모멘텀이 강한 ETF
    top = sorted(
        radar_data,
        key=lambda x: (
            x.get("score", 0),
            x.get("lead_score", 0),
            x.get("ret20", 0)
        ),
        reverse=True
    )

    top = top[:10]

    for item in top:

        render_radar_card(
            item,
            "📡 시장레이더"
        )


# ============================================================
# MY ETF
# ============================================================

def render_my_etf():

    st.markdown(
        '''
        <div class="section-title">
            ⭐ 내 ETF
        </div>
        ''',
        unsafe_allow_html=True
    )

    watchlist = st.session_state.get(
        "watchlist",
        []
    )

    if not watchlist:

        st.info(
            "관심등록한 ETF가 없습니다."
        )

        return

    rows = []

    for code in watchlist:

        code = _normalize_etf_code(code)

        if not code:
            continue

        name = get_etf_name(code)

        item = build_radar_item(
            code,
            name
        )

        if item:
            rows.append(item)

    if not rows:

        st.info(
            "관심 ETF의 가격 데이터를 확인하지 못했습니다."
        )

        return

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    rows.sort(
        key=lambda x: (
            x.get("score", 0)
        ),
        reverse=True
    )

    # --------------------------------------------------------
    # WATCHLIST CARD
    # --------------------------------------------------------

    for item in rows:

        code = _normalize_etf_code(
            item["code"]
        )

        col1, col2 = st.columns(
            [6.4, 1.0]
        )

        with col1:

            st.markdown(
                f'''
                <div class="etf-card">

                    <div class="etf-name">
                        {esc(item["name"])}
                    </div>

                    <div class="etf-code">
                        {esc(code)}
                    </div>

                    <div class="etf-meta">
                        현재가 {money(item["price"])}
                        ·
                        <span class="{
                            "positive"
                            if item["change_pct"] > 0
                            else
                            "negative"
                            if item["change_pct"] < 0
                            else
                            "neutral"
                        }">
                            {item["change_pct"]:+.2f}%
                        </span>

                        · 레이더 {safe_int(item["score"], 0)}
                        · RSI {item["rsi"]:.1f}
                        · 20일 {item["ret20"]:+.2f}%
                    </div>

                </div>
                ''',
                unsafe_allow_html=True
            )

        with col2:

            if st.button(
                "분석",
                key=f"my_etf_select_{code}",
                use_container_width=True
            ):

                st.session_state.selected_code = (
                    code
                )

                st.rerun()

            if st.button(
                "삭제",
                key=f"my_etf_delete_{code}",
                use_container_width=True
            ):

                remove_watch(code)

                st.rerun()


# ============================================================
# ETF SEARCH
# ============================================================

def render_etf_search():

    st.markdown(
        '''
        <div class="section-title">
            🔎 ETF 찾기
        </div>
        ''',
        unsafe_allow_html=True
    )

    search = st.text_input(
        "ETF 이름 또는 코드",
        placeholder="예: AI반도체 / 395160 / 나스닥",
        key="etf_search_input"
    )

    results = find_etfs(
        search,
        limit=30
    )

    if not results:

        st.info(
            "검색 결과가 없습니다."
        )

        return

    options = []

    for item in results:

        code = _normalize_etf_code(
            item.get("code")
        )

        name = safe_etf_name(
            item.get("name")
        )

        options.append(
            f"{name} · {code}"
        )

    selected = st.selectbox(
        "ETF 선택",
        options,
        key="etf_search_select"
    )

    if selected:

        code = selected.split("·")[-1].strip()

        col1, col2 = st.columns(
            [4, 1]
        )

        with col1:

            st.markdown(
                f'''
                <div class="etf-card">

                    <div class="etf-name">
                        {esc(get_etf_name(code))}
                    </div>

                    <div class="etf-code">
                        {esc(code)}
                    </div>

                </div>
                ''',
                unsafe_allow_html=True
            )

        with col2:

            if st.button(
                "분석",
                key=f"search_analyze_{code}",
                use_container_width=True
            ):

                st.session_state.selected_code = (
                    code
                )

                st.session_state.jump_to_analysis = (
                    True
                )

                st.rerun()


# ============================================================
# ETF ANALYSIS
# ============================================================

def render_etf_analysis(code):

    code = _normalize_etf_code(code)

    if not code:
        st.warning(
            "ETF 코드를 확인할 수 없습니다."
        )
        return

    name = get_etf_name(code)

    df = load_price_data(
        code,
        period="1y"
    )

    if df.empty:

        st.error(
            "가격 데이터를 가져오지 못했습니다."
        )

        return

    d = calculate_indicators(df)

    if d.empty:

        st.error(
            "기술지표를 계산하지 못했습니다."
        )

        return

    r = d.iloc[-1]

    price = safe_float(
        r.get("Close"),
        0
    )

    prev = (
        safe_float(
            d.iloc[-2].get("Close"),
            price
        )
        if len(d) >= 2
        else price
    )

    change = price - prev

    change_pct = (
        (price / prev - 1) * 100
        if prev
        else 0
    )

    judgment = get_judgment(r)

    action = get_action(r)

    zone = validated_price_zone(r)

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.markdown(
        f'''
        <div class="hero">

            <div class="hero-name">
                {esc(name)}
            </div>

            <div class="hero-code">
                {esc(code)}
            </div>

            <div class="quote-row">

                <div class="quote-price">
                    {money(price)}
                </div>

                <div class="quote-change {
                    "positive"
                    if change_pct > 0
                    else
                    "negative"
                    if change_pct < 0
                    else
                    "neutral"
                }">
                    {change:+,.0f}
                    ({change_pct:+.2f}%)
                </div>

            </div>

            <div class="hero-date">
                기준일 ·
                {esc(
                    str(
                        d.iloc[-1]["Date"]
                    )[:10]
                )}
            </div>

        </div>
        ''',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    st.markdown(
        f'''
        <div class="evidence-grid">

            <div class="evidence-box">
                <div class="evidence-label">
                    RSI14
                </div>
                <div class="evidence-value">
                    {safe_float(r.get("RSI14"), 0):.1f}
                </div>
                <div class="evidence-sub">
                    과열 여부
                </div>
            </div>

            <div class="evidence-box">
                <div class="evidence-label">
                    20일 수익률
                </div>
                <div class="evidence-value">
                    {safe_float(r.get("RET20"), 0):+.2f}%
                </div>
                <div class="evidence-sub">
                    단기 모멘텀
                </div>
            </div>

            <div class="evidence-box">
                <div class="evidence-label">
                    거래량
                </div>
                <div class="evidence-value">
                    {safe_float(r.get("VOL_RATIO"), 1):.2f}x
                </div>
                <div class="evidence-sub">
                    20일 평균 대비
                </div>
            </div>

        </div>
        ''',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # JUDGMENT / ACTION
    # --------------------------------------------------------

    col1, col2 = st.columns(
        2
    )

    with col1:

        st.markdown(
            f'''
            <div class="judgment-box">

                <div class="judgment-title">
                    현재 판단
                </div>

                <div class="judgment-main">
                    {esc(judgment)}
                </div>

                <div class="judgment-reason">
                    <div class="reason-label">
                        판단근거
                    </div>

                    가격 {money(price)}
                    · 20일선 {money(r.get("MA20", price))}
                    · 60일선 {money(r.get("MA60", price))}
                    · RSI {safe_float(r.get("RSI14"), 0):.1f}
                    · 20일 수익 {safe_float(r.get("RET20"), 0):+.2f}%
                </div>

            </div>
            ''',
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f'''
            <div class="action-box">

                <div class="action-title">
                    대응
                </div>

                <div class="judgment-main">
                    {esc(action)}
                </div>

                <div class="action-main">

                    <div class="action-reason-label">
                        가격구간
                    </div>

                    {esc(zone["state"])}
                    · {esc(zone["reason"])}

                </div>

            </div>
            ''',
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # PRICE ZONE
    # --------------------------------------------------------

    st.markdown(
        '''
        <div class="section-title">
            📍 가격구간
        </div>
        ''',
        unsafe_allow_html=True
    )

    low20 = safe_float(
        r.get("LOW20"),
        price
    )

    high20 = safe_float(
        r.get("HIGH20"),
        price
    )

    ma20 = safe_float(
        r.get("MA20"),
        price
    )

    ma60 = safe_float(
        r.get("MA60"),
        price
    )

    st.markdown(
        f'''
        <div class="scenario-grid">

            <div class="scenario-card">
                <div class="scenario-label">
                    현재가
                </div>
                <div class="scenario-price">
                    {money(price)}
                </div>
                <div class="scenario-desc">
                    현재 위치
                </div>
            </div>

            <div class="scenario-card">
                <div class="scenario-label">
                    20일선
                </div>
                <div class="scenario-price">
                    {money(ma20)}
                </div>
                <div class="scenario-desc">
                    단기 기준선
                </div>
            </div>

            <div class="scenario-card">
                <div class="scenario-label">
                    60일선
                </div>
                <div class="scenario-price">
                    {money(ma60)}
                </div>
                <div class="scenario-desc">
                    중기 기준선
                </div>
            </div>

            <div class="scenario-card">
                <div class="scenario-label">
                    20일 고저점
                </div>
                <div class="scenario-price">
                    {money(low20)}
                    ~
                    {money(high20)}
                </div>
                <div class="scenario-desc">
                    최근 가격범위
                </div>
            </div>

        </div>
        ''',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # CHART
    # --------------------------------------------------------

    st.markdown(
        '''
        <div class="section-title">
            📈 가격 흐름
        </div>
        ''',
        unsafe_allow_html=True
    )

    chart_df = d.tail(180)

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.72, 0.28]
    )

    fig.add_trace(
        go.Candlestick(
            x=chart_df["Date"],
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name="가격",
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df["Date"],
            y=chart_df["MA20"],
            name="MA20",
            mode="lines",
            line=dict(
                width=1.2
            )
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df["Date"],
            y=chart_df["MA60"],
            name="MA60",
            mode="lines",
            line=dict(
                width=1.2
            )
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=chart_df["Date"],
            y=chart_df["Volume"],
            name="거래량",
        ),
        row=2,
        col=1
    )

    fig.update_layout(
        height=500,
        margin=dict(
            l=5,
            r=5,
            t=10,
            b=5
        ),
        paper_bgcolor="#0b1725",
        plot_bgcolor="#0b1725",
        font=dict(
            color="#aebdcc"
        ),
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0
        ),
    )

    fig.update_xaxes(
        showgrid=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#1c3043"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        }
    )


# ============================================================
# PORTFOLIO / HOLDINGS
# ============================================================

def render_holdings():

    st.markdown(
        '''
        <div class="section-title">
            💼 보유 ETF
        </div>
        ''',
        unsafe_allow_html=True
    )

    holdings = st.session_state.get(
        "holdings",
        {}
    )

    if not holdings:

        st.info(
            "등록된 보유 ETF가 없습니다."
        )

        return

    for code, info in holdings.items():

        code = _normalize_etf_code(
            code
        )

        name = get_etf_name(code)

        qty = safe_float(
            info.get("quantity"),
            0
        )

        avg_price = safe_float(
            info.get("avg_price"),
            0
        )

        df = load_price_data(
            code
        )

        if df.empty:
            continue

        current = safe_float(
            df.iloc[-1]["Close"],
            0
        )

        pnl = (
            (current - avg_price)
            / avg_price
            * 100
            if avg_price
            else 0
        )

        st.markdown(
            f'''
            <div class="holding-box">

                <div class="holding-value">
                    {esc(name)}
                    · {esc(code)}
                </div>

                <div class="holding-detail">
                    수량 {qty:g}
                    · 평균단가 {money(avg_price)}
                    · 현재가 {money(current)}
                    · 수익률 {pnl:+.2f}%
                </div>

            </div>
            ''',
            unsafe_allow_html=True
        )


# ============================================================
# REFRESH
# ============================================================

def refresh_app_data():

    st.session_state.price_cache = {}

    st.session_state.radar_cache = {}

    st.session_state.radar_data = None

    st.session_state.future_theme_cache = None

    try:
        load_etf_universe.clear()
    except Exception:
        pass

    try:
        fetch_krx_etf_master.clear()
    except Exception:
        pass

    try:
        fetch_naver_etf_master.clear()
    except Exception:
        pass

    try:
        load_price_data_cached.clear()
    except Exception:
        pass

    try:
        _benchmark_snapshot.clear()
    except Exception:
        pass


# ============================================================
# APP HEADER
# ============================================================

st.markdown(
    '''
    <div class="app-header">

        <div class="app-title">
            📊 ETF RADAR
        </div>

        <div class="app-subtitle">
            미래테마 → 현재 모멘텀 → 최종 타겟
        </div>

    </div>
    ''',
    unsafe_allow_html=True
)


# ============================================================
# AUTO REFRESH
# ============================================================

if st_autorefresh is not None:

    try:
        st_autorefresh(
            interval=15 * 60 * 1000,
            key="etf_radar_refresh"
        )
    except Exception:
        pass


# ============================================================
# TOP CONTROLS
# ============================================================

top_col1, top_col2 = st.columns(
    [5.5, 1.5]
)

with top_col1:

    selected_code = st.session_state.get(
        "selected_code",
        DEFAULT_WATCHLIST[0]
    )

    selected_name = get_etf_name(
        selected_code
    )

    st.markdown(
        f'''
        <div class="etf-card">

            <div class="etf-name">
                {esc(selected_name)}
            </div>

            <div class="etf-code">
                {esc(selected_code)}
            </div>

        </div>
        ''',
        unsafe_allow_html=True
    )

with top_col2:

    if st.button(
        "🔄 새로고침",
        use_container_width=True,
        key="manual_refresh"
    ):

        refresh_app_data()

        st.rerun()


# ============================================================
# MAIN TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🎯 최종타겟",
        "🔭 미래테마",
        "📡 시장레이더",
        "⭐ 내 ETF",
        "🔎 ETF 찾기",
    ]
)


# ============================================================
# TAB 1
# ============================================================

with tab1:

    render_final_target()


# ============================================================
# TAB 2
# ============================================================

with tab2:

    render_future_theme()


# ============================================================
# TAB 3
# ============================================================

with tab3:

    render_market_radar()


# ============================================================
# TAB 4
# ============================================================

with tab4:

    render_my_etf()


# ============================================================
# TAB 5
# ============================================================

with tab5:

    render_etf_search()


# ============================================================
# SELECTED ETF ANALYSIS
# ============================================================

st.markdown(
    '''
    <div class="section-title">
        📊 선택 ETF 상세분석
    </div>
    ''',
    unsafe_allow_html=True
)

render_etf_analysis(
    st.session_state.selected_code
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    f'''
    <div style="
        margin-top:20px;
        padding-top:10px;
        border-top:1px solid #1c3043;
        color:#61758a;
        font-size:.62rem;
        text-align:center;
    ">
        ETF RADAR · {APP_VERSION}
        · 미래테마와 현재 모멘텀을 결합한 분석 도구
    </div>
    ''',
    unsafe_allow_html=True
)