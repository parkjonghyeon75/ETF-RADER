import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import json
import os
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta


# ============================================================
# ETF RADAR v13
# Mobile Financial Dashboard
#
# 주요 수정
# 1. 화면 전환 session_state 충돌 제거
# 2. 종목 추가 오류 제거
# 3. 미래테마 ETF 분석 오류 제거
# 4. 차트 최근 6개월 고정
# 5. 차트 확대/축소/이동 제거
# 6. 차트 스크롤 방해 최소화
# 7. 핵심가격 빈 사각바 제거
# 8. 미래테마 장식용 바 제거
# 9. 미래테마 정보 글자 확대
# 10. RSI / 거래량 / MA20을 현재판단에 통합
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

    --text: #f4f7fb;
    --text2: #d6deea;
    --muted: #9eacbd;

    --blue: #4da3ff;
    --cyan: #55d6ff;

    --green: #28d7a0;
    --red: #ff6577;
    --yellow: #ffc857;

    --border: #25374d;
}

html, body, [class*="css"] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        "Noto Sans KR",
        sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 50% -10%,
            rgba(35, 91, 145, 0.18),
            transparent 38%
        ),
        var(--bg);
    color: var(--text);
}

/* 전체 폭 */
.block-container {
    max-width: 1180px;
    padding-top: 0.7rem !important;
    padding-bottom: 2rem !important;
}

/* 기본 글자 */
p, span, div, label {
    color: var(--text);
}

/* Caption */
[data-testid="stCaptionContainer"] p,
.stCaption {
    color: var(--muted) !important;
    font-size: 0.82rem !important;
}

/* 제목 */
h1, h2, h3, h4 {
    color: var(--text) !important;
}

/* 버튼 */
.stButton > button {
    border-radius: 8px !important;
    border: 1px solid #31465e !important;
    background: #142235 !important;
    color: #f5f8fc !important;
    font-weight: 700 !important;
    min-height: 38px !important;
}

.stButton > button:hover {
    border-color: var(--blue) !important;
    background: #1a3048 !important;
}

/* Primary 버튼 */
.stButton > button[kind="primary"] {
    background: #1769aa !important;
    border-color: #318bd1 !important;
    color: white !important;
}

/* Input */
div[data-baseweb="input"] {
    background: #101d2d !important;
    border-color: #31465e !important;
}

div[data-baseweb="input"] input {
    color: white !important;
}

/* Selectbox */
div[data-baseweb="select"] > div {
    background: #101d2d !important;
    border-color: #31465e !important;
    color: white !important;
}

/* Radio */
div[data-testid="stRadio"] label {
    color: var(--text2) !important;
}

/* Divider */
hr {
    border-color: #1d2c3e !important;
    margin: 0.8rem 0 !important;
}

/* ============================================================
   Header
   ============================================================ */

.app-header {
    padding: 8px 0 12px 0;
}

.app-title {
    font-size: 1.65rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    color: #ffffff;
}

.app-subtitle {
    margin-top: 2px;
    color: var(--muted);
    font-size: 0.78rem;
}

/* ============================================================
   Hero
   ============================================================ */

.hero {
    background:
        linear-gradient(
            135deg,
            rgba(21, 42, 67, 0.98),
            rgba(11, 25, 41, 0.98)
        );
    border: 1px solid #294057;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 12px;
}

.hero-name {
    font-size: 1.38rem;
    font-weight: 900;
    letter-spacing: -0.03em;
}

.hero-code {
    color: #aebdd0;
    font-size: 0.78rem;
    margin-top: 3px;
}

.quote-row {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-top: 15px;
}

.quote-price {
    font-size: 2.15rem;
    line-height: 1;
    font-weight: 900;
    letter-spacing: -0.05em;
}

.quote-change {
    font-size: 1rem;
    font-weight: 800;
}

.positive {
    color: var(--green) !important;
}

.negative {
    color: var(--red) !important;
}

.neutral {
    color: var(--text2) !important;
}

.hero-date {
    margin-top: 8px;
    color: var(--muted);
    font-size: 0.76rem;
}

/* ============================================================
   Section
   ============================================================ */

.section-title {
    font-size: 1.08rem;
    font-weight: 900;
    color: #ffffff;
    margin: 18px 0 8px 0;
    letter-spacing: -0.03em;
}

.section-subtitle {
    color: var(--muted);
    font-size: 0.78rem;
    margin-top: -4px;
    margin-bottom: 9px;
}

/* ============================================================
   Market evidence
   ============================================================ */

.evidence-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin: 8px 0 12px 0;
}

.evidence-box {
    background: #0e1b2b;
    border: 1px solid #263b52;
    border-radius: 9px;
    padding: 10px 11px;
}

.evidence-label {
    font-size: 0.72rem;
    color: #9eacbd;
    margin-bottom: 4px;
}

.evidence-value {
    font-size: 0.98rem;
    font-weight: 900;
    color: #f4f7fb;
}

.evidence-sub {
    margin-top: 3px;
    font-size: 0.73rem;
    color: #aab7c7;
}

/* ============================================================
   Judgment
   ============================================================ */

.judgment-box {
    background: #0d1928;
    border: 1px solid #294057;
    border-left: 4px solid var(--blue);
    border-radius: 10px;
    padding: 14px 15px;
}

.judgment-title {
    font-size: 0.75rem;
    color: var(--muted);
}

.judgment-main {
    margin-top: 4px;
    font-size: 1.25rem;
    font-weight: 900;
    color: #ffffff;
}

.judgment-reason {
    margin-top: 9px;
    color: #d3ddea;
    font-size: 0.87rem;
    line-height: 1.55;
}

.action-box {
    background: #102033;
    border: 1px solid #31506e;
    border-radius: 10px;
    padding: 14px 15px;
}

.action-title {
    color: #75c8ff;
    font-size: 0.75rem;
    font-weight: 800;
}

.action-main {
    margin-top: 5px;
    color: #ffffff;
    font-size: 0.97rem;
    line-height: 1.55;
    font-weight: 700;
}

/* ============================================================
   Price scenarios
   ============================================================ */

.scenario-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin-top: 7px;
}

.scenario-card {
    background: #0e1b2b;
    border: 1px solid #263b52;
    border-radius: 9px;
    padding: 11px;
}

.scenario-label {
    color: #9eacbd;
    font-size: 0.70rem;
}

.scenario-price {
    color: #ffffff;
    font-size: 1.15rem;
    font-weight: 900;
    margin-top: 4px;
}

.scenario-desc {
    color: #c4cfdd;
    font-size: 0.74rem;
    line-height: 1.4;
    margin-top: 6px;
}

/* ============================================================
   Holding
   ============================================================ */

.holding-box {
    background: #0d1928;
    border: 1px solid #263b52;
    border-radius: 10px;
    padding: 13px;
}

.holding-value {
    font-size: 1rem;
    font-weight: 900;
}

.holding-detail {
    margin-top: 5px;
    color: #aebbc9;
    font-size: 0.78rem;
}

/* ============================================================
   Future theme
   ============================================================ */

.theme-card {
    background: #0d1928;
    border: 1px solid #293d54;
    border-radius: 11px;
    padding: 14px;
    margin-bottom: 12px;
}

.theme-stage {
    color: #72c9ff;
    font-size: 0.76rem;
    font-weight: 800;
    margin-bottom: 5px;
}

.theme-title {
    color: #ffffff;
    font-size: 1.15rem;
    font-weight: 900;
    letter-spacing: -0.03em;
}

.theme-reason {
    color: #bac6d4;
    font-size: 0.82rem;
    line-height: 1.5;
    margin-top: 5px;
    margin-bottom: 11px;
}

/* 테마 ETF 정보 - 크게 */
.theme-etf-box {
    background: #111f31;
    border: 1px solid #2a4058;
    border-radius: 9px;
    padding: 11px 12px;
    margin-bottom: 8px;
}

.theme-etf-name {
    color: #ffffff;
    font-size: 0.94rem;
    font-weight: 900;
    line-height: 1.3;
}

.theme-etf-code {
    color: #9eacbd;
    font-size: 0.72rem;
    margin-top: 2px;
}

.theme-data-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 5px;
    margin-top: 9px;
}

.theme-data-item {
    background: #0b1726;
    border-radius: 6px;
    padding: 7px 6px;
}

.theme-data-label {
    color: #9eacbd;
    font-size: 0.68rem;
}

.theme-data-value {
    color: #f4f7fb;
    font-size: 0.88rem;
    font-weight: 900;
    margin-top: 2px;
}

/* ============================================================
   Mobile
   ============================================================ */

@media (max-width: 700px) {

    .block-container {
        padding-left: 10px !important;
        padding-right: 10px !important;
    }

    .app-title {
        font-size: 1.42rem;
    }

    .hero {
        padding: 14px;
    }

    .hero-name {
        font-size: 1.2rem;
    }

    .quote-price {
        font-size: 1.9rem;
    }

    .evidence-grid {
        gap: 6px;
    }

    .evidence-box {
        padding: 9px 7px;
    }

    .evidence-value {
        font-size: 0.86rem;
    }

    .evidence-sub {
        font-size: 0.67rem;
    }

    .scenario-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .theme-data-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .theme-etf-name {
        font-size: 0.93rem;
    }

    .theme-data-label {
        font-size: 0.70rem;
    }

    .theme-data-value {
        font-size: 0.90rem;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# FILES
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"
UNIVERSE_FILE = "etf_universe_cache.json"


# ============================================================
# DEFAULT ETF DATA
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


FALLBACK_ETFS = {
    "395160": "KODEX AI반도체핵심장비",
    "487240": "KODEX AI반도체",
    "471990": "KODEX AI반도체TOP2Plus",
    "464240": "KODEX AI전력핵심설비",
    "487130": "KODEX AI전력인프라",
    "449170": "TIGER 글로벌AI인프라액티브",
    "434060": "TIGER 글로벌AI&반도체액티브",
    "381170": "TIGER 미국테크TOP10 INDXX",
    "396500": "TIGER 반도체",
    "091160": "KODEX 반도체",
    "305720": "KODEX 2차전지산업",
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
        "reason": "AI 연산 확대와 고대역폭 메모리, 첨단 반도체 투자 증가의 직접적인 수혜 영역입니다.",
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
        "reason": "AI 서비스 확산에 따라 서버·네트워크·데이터센터 투자가 확대되는 구간을 추적합니다.",
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
        "reason": "데이터센터와 산업용 전력수요 증가에 따른 전력망 및 핵심설비 투자를 추적합니다.",
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
        "reason": "전력수요 증가와 에너지 믹스 변화에 따라 원전 관련 산업 흐름을 추적합니다.",
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
        "reason": "AI 서버 고집적화에 따라 냉각과 열관리의 중요성이 높아지는 후방 수혜 영역입니다.",
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
# JSON HELPERS
# ============================================================

def read_json(path, default):
    try:
        if not os.path.exists(path):
            return default

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return default


def write_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
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
# SESSION STATE
# ============================================================

def init_state():

    if "watchlist" not in st.session_state:
        saved = read_json(
            WATCHLIST_FILE,
            DEFAULT_WATCHLIST.copy()
        )

        if not isinstance(saved, list):
            saved = DEFAULT_WATCHLIST.copy()

        st.session_state.watchlist = [
            str(x).zfill(6)
            for x in saved
        ]

    if "holdings" not in st.session_state:
        holdings = read_json(
            HOLDINGS_FILE,
            {}
        )

        if not isinstance(holdings, dict):
            holdings = {}

        st.session_state.holdings = holdings

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
            else list(BASE_ETFS.keys())[0]
        )

    if "main_page" not in st.session_state:
        st.session_state.main_page = "📊 내 ETF"

    # 중요:
    # 화면 전환을 main_page widget이 생성된 이후 직접 변경하지 않는다.
    if "page_request" not in st.session_state:
        st.session_state.page_request = None

    if "notice" not in st.session_state:
        st.session_state.notice = None


# ============================================================
# ETF UNIVERSE
# ============================================================

def load_etf_universe():

    universe = {}

    universe.update(BASE_ETFS)
    universe.update(FALLBACK_ETFS)

    cached = read_json(
        UNIVERSE_FILE,
        {}
    )

    if isinstance(cached, dict):
        for code, name in cached.items():
            if code and name:
                universe[str(code).zfill(6)] = str(name)

    elif isinstance(cached, list):

        for item in cached:
            if not isinstance(item, dict):
                continue

            code = str(
                item.get("code", "")
            ).zfill(6)

            name = item.get("name")

            if code and name:
                universe[code] = name

    return universe


def fetch_krx_etf_catalog():

    url = (
        "https://finance.naver.com/api/sise/etfItemList.nhn"
    )

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/130 Safari/537.36"
            )
        }
    )

    with urllib.request.urlopen(
        req,
        timeout=8
    ) as response:

        raw = response.read()

    root = ET.fromstring(raw)

    result = {}

    for item in root.findall(".//item"):

        code = (
            item.attrib.get("itemcode")
            or item.attrib.get("code")
            or ""
        )

        name = (
            item.attrib.get("itemname")
            or item.attrib.get("name")
            or ""
        )

        if code and name:
            result[
                str(code).zfill(6)
            ] = name

    return result


def refresh_etf_universe():

    try:

        external = fetch_krx_etf_catalog()

        if external:

            merged = dict(
                st.session_state.etf_universe
            )

            merged.update(external)

            st.session_state.etf_universe = merged

            write_json(
                UNIVERSE_FILE,
                merged
            )

            st.session_state.notice = (
                f"ETF 목록 {len(external):,}개를 확인했습니다."
            )

            return True

    except Exception:
        pass

    # 외부 조회가 실패해도 기존 목록은 유지
    st.session_state.etf_universe = load_etf_universe()

    st.session_state.notice = (
        "현재 저장된 ETF 목록으로 검색합니다."
    )

    return False


# ============================================================
# ETF NAME
# ============================================================

def get_etf_name(code):

    code = str(code).zfill(6)

    return (
        st.session_state.etf_universe.get(code)
        or BASE_ETFS.get(code)
        or FALLBACK_ETFS.get(code)
        or f"ETF {code}"
    )


# ============================================================
# PRICE DATA
# ============================================================

def normalize_df(df):

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    if isinstance(df.columns, pd.MultiIndex):

        new_columns = []

        for col in df.columns:

            if isinstance(col, tuple):
                new_columns.append(col[0])
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

        elif key == "adj close":
            rename_map[col] = "Adj Close"

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

    for col in required:

        if col not in df.columns:
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

    if df.index.tz is not None:
        try:
            df.index = df.index.tz_localize(None)
        except Exception:
            pass

    return df


def fetch_yahoo(code):

    ticker = f"{code}.KS"

    try:

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


def fetch_naver(code):

    try:

        code = str(code).zfill(6)

        url = (
            "https://fchart.stock.naver.com/"
            f"spevent.nhn?symbol={code}"
            "&timeframe=day"
            "&count=600"
            "&requestType=0"
        )

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            req,
            timeout=8
        ) as response:

            raw = response.read()

        root = ET.fromstring(raw)

        rows = []

        for item in root.findall(".//item"):

            data = item.attrib.get(
                "data",
                ""
            )

            parts = data.split("|")

            if len(parts) < 6:
                continue

            date = parts[0]
            open_ = float(parts[1])
            high = float(parts[2])
            low = float(parts[3])
            close = float(parts[4])
            volume = float(parts[5])

            rows.append(
                [
                    date,
                    open_,
                    high,
                    low,
                    close,
                    volume
                ]
            )

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
                "Volume"
            ]
        )

        df["Date"] = pd.to_datetime(
            df["Date"]
        )

        df = df.set_index(
            "Date"
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

    cached = st.session_state.price_cache.get(
        code
    )

    if cached and not force:

        cached_time = cached.get(
            "time"
        )

        if cached_time:

            age = (
                now - cached_time
            ).total_seconds()

            if age < 300:

                return cached.get(
                    "data",
                    pd.DataFrame()
                )

    df = fetch_naver(code)

    if df.empty:
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
        delta.where(delta > 0, 0)
        .rolling(14)
        .mean()
    )

    loss = (
        -delta.where(delta < 0, 0)
        .rolling(14)
        .mean()
    )

    rs = gain / loss.replace(
        0,
        np.nan
    )

    d["RSI14"] = (
        100 - (
            100 / (1 + rs)
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
# SAFE NUMBER
# ============================================================

def safe_float(value, default=0.0):

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


def percent(value):

    value = safe_float(
        value
    )

    return f"{value:+.2f}%"


# ============================================================
# DAILY CHANGE
# ============================================================

def get_daily_change(d):

    if d is None or len(d) < 2:
        return 0.0, 0.0

    current = safe_float(
        d["Close"].iloc[-1]
    )

    previous = safe_float(
        d["Close"].iloc[-2]
    )

    if previous == 0:
        return 0.0, 0.0

    change = current - previous

    change_pct = (
        change
        / previous
        * 100
    )

    return change, change_pct


# ============================================================
# LEVELS
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
            "action": "잠시 후 다시 조회해 주세요.",
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

    if above20:
        ma_state = "20일선 상회"
    else:
        ma_state = "20일선 하회"

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

        title = "상승 추세 · 추격 주의"

        action = (
            "추세 자체는 양호하지만 RSI가 높은 구간입니다. "
            "새 매수라면 현재가 추격보다 20일선 부근의 "
            "눌림 확인을 우선합니다."
        )

    elif (
        above20
        and above60
    ):

        title = "상승 추세 유지"

        action = (
            "현재가는 20일선과 60일선 위에 있습니다. "
            "보유자는 추세를 유지하면서 20일선 이탈 여부를 "
            "중요하게 확인하고, 미보유자는 돌파 추격보다 "
            "눌림 구간을 기다리는 접근이 적절합니다."
        )

    elif (
        above60
        and not above20
    ):

        title = "단기 조정 · 중기 추세 확인"

        action = (
            "20일선 아래로 조정 중이지만 60일선 위라면 "
            "중기 상승 흐름이 아직 훼손됐다고 단정하기 어렵습니다. "
            "20일선 회복 여부를 확인합니다."
        )

    elif (
        not above60
        and rsi <= 40
    ):

        title = "중기 약세 · 방어 우선"

        action = (
            "60일선 아래에서 RSI도 약한 구간입니다. "
            "신규 진입보다는 지지선 형성과 거래량 회복 여부를 "
            "먼저 확인하는 구간입니다."
        )

    else:

        title = "방향 확인 구간"

        action = (
            "추세와 모멘텀이 명확하지 않습니다. "
            "20일선 회복 또는 주요 저항 돌파와 함께 "
            "거래량이 동반되는지를 확인합니다."
        )

    reasons = [
        f"현재가 {money(current)} · 20일선 {money(ma20)} · {ma_state}",
        f"RSI14 {rsi:.1f} · {rsi_state}",
        f"거래량 {vol_ratio:.2f}배 · {vol_state} · 최근 20일 {ret20:+.2f}%",
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
        "ret20": ret20,
    }


# ============================================================
# NAVIGATION
# ============================================================

def navigate_to_etf(code):

    code = str(code).zfill(6)

    # 현재 화면의 radio widget을 직접 변경하지 않는다.
    st.session_state.selected_code = code

    st.session_state.page_request = "📊 내 ETF"

    st.rerun()


# ============================================================
# SEARCH
# ============================================================

def search_etfs(query):

    universe = (
        st.session_state.etf_universe
    )

    query = (
        query or ""
    ).strip().lower()

    if not query:
        return []

    results = []

    for code, name in universe.items():

        if (
            query in str(code).lower()
            or query in str(name).lower()
        ):
            results.append(
                {
                    "code": code,
                    "name": name
                }
            )

    return results[:50]


# ============================================================
# WATCHLIST
# ============================================================

def add_to_watchlist(code):

    code = str(code).zfill(6)

    if code not in st.session_state.watchlist:

        st.session_state.watchlist.append(
            code
        )

        write_json(
            WATCHLIST_FILE,
            st.session_state.watchlist
        )

        st.session_state.notice = (
            f"{get_etf_name(code)}을(를) 관심종목에 추가했습니다."
        )

    else:

        st.session_state.notice = (
            "이미 관심종목에 등록되어 있습니다."
        )

    navigate_to_etf(code)


def remove_from_watchlist(code):

    code = str(code).zfill(6)

    if code in st.session_state.watchlist:

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
                list(BASE_ETFS.keys())[0]
            )


# ============================================================
# HOLDINGS
# ============================================================

def render_holdings(code):

    code = str(code).zfill(6)

    holdings = st.session_state.holdings

    current_holding = holdings.get(
        code
    )

    st.markdown(
        '<div class="section-title">보유 상태</div>',
        unsafe_allow_html=True
    )

    is_held = current_holding is not None

    selected = st.radio(
        "보유 여부",
        ["미보유", "보유중"],
        index=1 if is_held else 0,
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

            st.session_state.holdings = holdings

            write_json(
                HOLDINGS_FILE,
                holdings
            )

            st.session_state.notice = (
                "보유정보를 저장했습니다."
            )

            st.rerun()

        if current_holding:

            current = safe_float(
                st.session_state.get(
                    f"current_price_{code}",
                    0
                )
            )

            if current > 0 and avg_price > 0:

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
                            평균매수가 {money(avg_price)}
                            · 현재 수익률
                            <span class="{cls}">
                                {pnl_pct:+.2f}%
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    else:

        if code in holdings:

            if st.button(
                "보유정보 삭제",
                key=f"delete_hold_{code}",
                use_container_width=True
            ):

                del holdings[code]

                st.session_state.holdings = holdings

                write_json(
                    HOLDINGS_FILE,
                    holdings
                )

                st.rerun()


# ============================================================
# JUDGMENT RENDER
# ============================================================

def render_judgment(
    d,
    code
):

    judgment = get_judgment(d)

    st.markdown(
        '<div class="section-title">현재판단 · 지금대응</div>',
        unsafe_allow_html=True
    )

    # 핵심 지표를 이곳에 통합
    rsi = judgment["rsi"]
    vr = judgment["vol_ratio"]

    if judgment["ma_state"] == "20일선 상회":
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
                <div class="evidence-label">20일선</div>
                <div class="evidence-value {ma_color}">
                    {judgment["ma_state"]}
                </div>
                <div class="evidence-sub">
                    최근 20일 추세 기준
                </div>
            </div>

            <div class="evidence-box">
                <div class="evidence-label">RSI14</div>
                <div class="evidence-value {rsi_color}">
                    {rsi:.1f}
                </div>
                <div class="evidence-sub">
                    {judgment["rsi_state"]}
                </div>
            </div>

            <div class="evidence-box">
                <div class="evidence-label">거래량</div>
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
        [1, 1]
    )

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
                    {"<br>".join(judgment["reasons"])}
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
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# PRICE SCENARIO
# ============================================================

def render_price_scenarios(d):

    levels = calculate_levels(d)

    if not levels:
        return

    st.markdown(
        '<div class="section-title">핵심가격 · 대응 시나리오</div>',
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

    html = '<div class="scenario-grid">'

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

    if d is None or d.empty:
        st.info(
            "차트 데이터를 불러오지 못했습니다."
        )
        return

    chart_df = d.copy()

    # 최근 6개월 고정
    end_date = chart_df.index.max()

    start_date = (
        end_date
        - pd.DateOffset(months=6)
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

    # 캔들
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

    # MA20
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

    # MA60
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

    # 거래량
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
    # 중요:
    # 최근 6개월 고정
    # 줌/팬/드래그 금지
    # x/y축 고정
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

    # --------------------------------------------------------
    # interaction 완전 제한
    # --------------------------------------------------------

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
# THEME ETF MATCH
# ============================================================

def theme_candidates(theme):

    info = THEMES.get(
        theme,
        {}
    )

    keywords = info.get(
        "keywords",
        []
    )

    seeds = info.get(
        "seeds",
        []
    )

    universe = (
        st.session_state.etf_universe
    )

    result = []

    # 우선 seed
    for code in seeds:

        code = str(code).zfill(6)

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

    # 키워드 검색
    for code, name in universe.items():

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
        name = item["name"]

        try:

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

            trend = (
                "상승"
                if current >= ma20
                else "조정"
            )

            rows.append(
                {
                    "code": code,
                    "name": name,
                    "price": current,
                    "rsi": rsi,
                    "vol_ratio": vr,
                    "ret20": ret20,
                    "trend": trend
                }
            )

        except Exception:
            # ETF 하나가 실패해도 테마 전체는 계속 표시
            continue

    st.session_state.theme_cache[
        theme
    ] = {
        "time": now,
        "rows": rows
    }

    return rows


# ============================================================
# THEME ETF CARD
# ============================================================

def render_theme_etf(
    item,
    button_key
):

    code = item["code"]
    name = item["name"]

    price = item["price"]
    rsi = item["rsi"]
    vr = item["vol_ratio"]
    ret20 = item["ret20"]
    trend = item["trend"]

    price_cls = (
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
                {name}
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
                        {money(price)}
                    </div>
                </div>

                <div class="theme-data-item">
                    <div class="theme-data-label">
                        RSI14
                    </div>
                    <div class="theme-data-value">
                        {rsi:.1f}
                    </div>
                </div>

                <div class="theme-data-item">
                    <div class="theme-data-label">
                        거래량
                    </div>
                    <div class="theme-data-value">
                        {vr:.2f}배
                    </div>
                </div>

                <div class="theme-data-item">
                    <div class="theme-data-label">
                        20일 수익률
                    </div>
                    <div class="theme-data-value {price_cls}">
                        {ret20:+.2f}%
                    </div>
                </div>

            </div>

            <div style="
                margin-top:7px;
                font-size:0.78rem;
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

    # 중요:
    # theme 문자열을 key로 사용하지 않고
    # 단순 index/code 기반 key 사용
    if st.button(
        "ETF 분석",
        key=button_key,
        use_container_width=True
    ):

        navigate_to_etf(
            code
        )


# ============================================================
# FUTURE THEME CARD
# ============================================================

def render_theme_card(
    theme_index,
    theme,
    stage
):

    info = THEMES.get(
        theme,
        {}
    )

    reason = info.get(
        "reason",
        ""
    )

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
                {reason}
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
            "현재 표시 가능한 ETF 데이터를 확인하지 못했습니다."
        )

        return

    cols = st.columns(
        len(rows)
    )

    for i, item in enumerate(rows):

        with cols[i]:

            render_theme_etf(
                item,
                button_key=(
                    f"future_analyze_"
                    f"{theme_index}_"
                    f"{i}_"
                    f"{item['code']}"
                )
            )


# ============================================================
# SEARCH / WATCHLIST UI
# ============================================================

def render_etf_finder():

    st.markdown(
        '<div class="section-title">ETF 찾기</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(
        [5, 1]
    )

    with c1:

        query = st.text_input(
            "ETF 검색",
            placeholder="ETF명 또는 종목코드 입력",
            label_visibility="collapsed",
            key="etf_search_query"
        )

    with c2:

        if st.button(
            "목록 갱신",
            use_container_width=True,
            key="refresh_universe"
        ):

            refresh_etf_universe()

    if st.session_state.notice:

        st.info(
            st.session_state.notice
        )

        st.session_state.notice = None

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

        selected_index = labels.index(
            selected_label
        )

        selected_item = results[
            selected_index
        ]

        c3, c4 = st.columns(
            [4, 1]
        )

        with c3:

            st.caption(
                f"선택: {selected_item['name']} "
                f"({selected_item['code']})"
            )

        with c4:

            already = (
                selected_item["code"]
                in st.session_state.watchlist
            )

            if st.button(
                "추가" if not already else "등록됨",
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


def render_watchlist():

    st.markdown(
        '<div class="section-title">관심종목</div>',
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
        default_index = watchlist.index(
            current
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

    selected_code = watchlist[idx]

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
# MY ETF PAGE
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
        d.index[-1].strftime(
            "%Y-%m-%d"
        )
    )

    # 현재가
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

    # 현재가를 holdings에서 사용할 수 있도록 저장
    st.session_state[
        f"current_price_{code}"
    ] = current

    # 보유
    render_holdings(
        code
    )

    # 판단
    render_judgment(
        d,
        code
    )

    # 핵심가격
    render_price_scenarios(
        d
    )

    # 차트
    st.markdown(
        '<div class="section-title">가격 흐름</div>',
        unsafe_allow_html=True
    )

    render_chart(
        d
    )


# ============================================================
# FUTURE THEME PAGE
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

    if st.button(
        "시장 데이터 다시 탐색",
        use_container_width=True,
        key="theme_refresh"
    ):

        st.session_state.price_cache = {}
        st.session_state.theme_cache = {}

        refresh_etf_universe()

        st.rerun()

    # 미래 테마
    for idx, (
        theme,
        stage
    ) in enumerate(FUTURE_CHAIN):

        render_theme_card(
            idx,
            theme,
            stage
        )

    # 전체 테마 요약
    st.markdown(
        '<div class="section-title">테마 요약</div>',
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

        summary_rows.append(
            {
                "테마": theme,
                "단계": stage,
                "평균 20일수익률": f"{avg_ret:+.2f}%",
                "평균 RSI": f"{avg_rsi:.1f}",
                "평균 거래량": f"{avg_vol:.2f}배",
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
# MAIN
# ============================================================

init_state()


# ------------------------------------------------------------
# 중요:
# 이전 실행에서 버튼이 남긴 page_request를
# radio widget 생성 전에 적용한다.
# ------------------------------------------------------------

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
            ETF 추세 · 모멘텀 · 거래량 · 핵심가격 · 대응 시나리오
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