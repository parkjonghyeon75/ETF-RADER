# -*- coding: utf-8 -*-

"""
ETF RADAR
Automatic Future Theme Engine
Mobile Financial Dashboard

핵심 기능
1. 국내 ETF Universe 자동 수집
2. ETF 기술지표 분석
3. 내 ETF / ETF 검색 / 보유정보
4. 자동 미래테마 탐색
5. 테마별 모멘텀 / 상대강도 / 거래량 / breadth / 지속성 분석
6. 현재 주도 / 다음 수혜 / 관심 확대 / 초기 관심 / 관찰 자동 분류
7. 미래테마 수동 업데이트
8. 자동 캐시 갱신
9. 시장 레이더
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import json
import os
import html
import re
import requests
import urllib.parse
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
<style>

html, body, [class*="css"] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Noto Sans KR",
        "Malgun Gothic",
        "Apple SD Gothic Neo",
        sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, #182844 0%, #08111f 35%, #050b14 100%);
    color: #eef4ff;
}

.block-container {
    max-width: 1180px;
    padding-top: 1.0rem;
    padding-bottom: 3rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

section[data-testid="stSidebar"] {
    background: #07101c;
}

h1, h2, h3, h4 {
    color: #f5f8ff !important;
}

p, label, span, div {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Noto Sans KR",
        "Malgun Gothic",
        sans-serif;
}

div[data-baseweb="select"] > div {
    background: #101c2c;
    border: 1px solid #263b58;
    color: #f3f7ff;
}

div[data-baseweb="select"] * {
    color: #f3f7ff !important;
}

.stTextInput input {
    background: #101c2c !important;
    color: #f3f7ff !important;
    border: 1px solid #263b58 !important;
}

.stNumberInput input {
    background: #101c2c !important;
    color: #f3f7ff !important;
}

button {
    border-radius: 10px !important;
}

.stButton > button {
    background: #13243a;
    color: #eef5ff;
    border: 1px solid #2d4668;
    min-height: 38px;
    font-weight: 600;
}

.stButton > button:hover {
    border-color: #5e9cff;
    color: #ffffff;
}

.hero {
    background:
        linear-gradient(135deg, rgba(30,57,92,.96), rgba(9,19,32,.98));
    border: 1px solid #2b4769;
    border-radius: 20px;
    padding: 20px;
    margin: 8px 0 16px 0;
    box-shadow: 0 12px 40px rgba(0,0,0,.20);
}

.hero-title {
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -0.7px;
}

.hero-code {
    color: #93a8c2;
    font-size: 13px;
    margin-top: 4px;
}

.hero-price {
    font-size: 32px;
    font-weight: 800;
    margin-top: 14px;
}

.card {
    background: rgba(15,28,45,.94);
    border: 1px solid #263c5a;
    border-radius: 16px;
    padding: 16px;
    margin: 8px 0;
}

.theme-card {
    background:
        linear-gradient(145deg, rgba(19,38,61,.98), rgba(8,17,29,.98));
    border: 1px solid #294666;
    border-radius: 18px;
    padding: 17px;
    margin: 9px 0;
}

.theme-name {
    font-size: 21px;
    font-weight: 800;
}

.theme-score {
    font-size: 27px;
    font-weight: 800;
}

.small {
    font-size: 12px;
    color: #91a5be;
}

.muted {
    color: #8ea2bb;
}

.good {
    color: #42e0a1;
}

.warn {
    color: #ffc857;
}

.bad {
    color: #ff7185;
}

.blue {
    color: #62a7ff;
}

.badge {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 800;
    margin-right: 5px;
    border: 1px solid #3c5878;
    background: #172a43;
    color: #dbe9ff;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
}

.metric {
    background: #0d1a2b;
    border: 1px solid #243a57;
    border-radius: 12px;
    padding: 12px;
}

.metric-title {
    color: #8298b2;
    font-size: 11px;
}

.metric-value {
    font-size: 18px;
    font-weight: 800;
    margin-top: 5px;
}

.reason {
    background: #0a1625;
    border-left: 3px solid #4d8fe8;
    border-radius: 8px;
    padding: 10px 12px;
    margin-top: 10px;
    color: #c9d7e8;
    font-size: 13px;
    line-height: 1.6;
}

.scenario {
    background: #0c1929;
    border: 1px solid #233b59;
    border-radius: 13px;
    padding: 13px;
    margin: 6px 0;
}

.scenario-title {
    font-weight: 800;
    font-size: 14px;
}

.scenario-text {
    color: #aabbd0;
    font-size: 12px;
    line-height: 1.5;
    margin-top: 5px;
}

.footer-note {
    color: #71859e;
    font-size: 11px;
    text-align: center;
    margin-top: 30px;
}

@media (max-width: 700px) {

    .block-container {
        padding-left: .65rem;
        padding-right: .65rem;
    }

    .hero-title {
        font-size: 23px;
    }

    .hero-price {
        font-size: 28px;
    }

    .metric-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .theme-name {
        font-size: 18px;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# CONSTANTS
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"

DEFAULT_WATCHLIST = [
    "395160",
    "487240",
    "471990",
    "133690",
    "360750",
    "458730",
]

BENCHMARK_CODE = "069500"

CACHE_MINUTES = 5
THEME_CACHE_MINUTES = 30

KOREAN_ETF_URL = "https://finance.naver.com/api/sise/etfItemList.nhn"


# ============================================================
# FUTURE THEME VOCABULARY
# ============================================================

"""
중요:
이 사전은 '어떤 테마를 미래테마로 선정할지'를 결정하지 않습니다.

역할:
ETF 이름에 나타나는 표현을 동일한 테마 그룹으로 묶기 위한
최소한의 언어 사전입니다.

실제 미래테마 점수는 시장 데이터가 결정합니다.
"""

THEME_VOCABULARY = {

    "AI 반도체": [
        "AI반도체",
        "AI 반도체",
        "반도체",
        "HBM",
        "메모리",
        "반도체장비",
        "반도체 장비",
        "반도체소부장",
        "반도체 소부장",
        "파운드리",
        "시스템반도체",
        "비메모리",
    ],

    "AI 인프라": [
        "AI인프라",
        "AI 인프라",
        "데이터센터",
        "데이터 센터",
        "AI전력",
        "AI 전력",
        "AI인프라",
        "인프라",
    ],

    "전력 인프라": [
        "전력",
        "전력인프라",
        "전력 인프라",
        "전력설비",
        "전력 설비",
        "전력핵심설비",
        "전력 핵심설비",
        "변압기",
        "배전",
        "전선",
        "전기",
        "전력기기",
    ],

    "원자력": [
        "원자력",
        "원전",
        "원전산업",
        "SMR",
        "소형모듈원전",
        "소형 원자로",
    ],

    "냉각·열관리": [
        "냉각",
        "열관리",
        "액침냉각",
        "액침 냉각",
        "데이터센터냉각",
        "열관리",
    ],

    "로봇·자동화": [
        "로봇",
        "로보틱스",
        "자동화",
        "스마트팩토리",
        "스마트팩토리",
        "휴머노이드",
    ],

    "방산·우주": [
        "방산",
        "방위산업",
        "우주",
        "항공우주",
        "드론",
        "방위",
    ],

    "조선·해양": [
        "조선",
        "조선업",
        "해양",
        "LNG",
        "선박",
        "친환경선박",
    ],

    "2차전지": [
        "2차전지",
        "이차전지",
        "배터리",
        "전기차배터리",
        "양극재",
        "음극재",
        "배터리소재",
    ],

    "바이오·헬스케어": [
        "바이오",
        "헬스케어",
        "제약",
        "신약",
        "의료",
        "바이오헬스",
    ],

    "자동차·모빌리티": [
        "자동차",
        "모빌리티",
        "전기차",
        "자율주행",
        "미래차",
        "EV",
    ],

    "인터넷·AI소프트웨어": [
        "인터넷",
        "소프트웨어",
        "AI",
        "클라우드",
        "빅테크",
        "플랫폼",
    ],

    "친환경·신재생": [
        "태양광",
        "풍력",
        "신재생",
        "친환경",
        "수소",
        "그린에너지",
    ],

    "금융·고배당": [
        "은행",
        "금융",
        "고배당",
        "배당",
        "리츠",
    ],
}


THEME_REASON_BASE = {
    "AI 반도체": "AI 연산 수요와 반도체 생태계의 시장 흐름을 추적합니다.",
    "AI 인프라": "AI 데이터센터 확대와 관련 인프라 수요의 확산을 추적합니다.",
    "전력 인프라": "AI·데이터센터 및 산업 전력 수요와 전력설비 흐름을 추적합니다.",
    "원자력": "원전 및 차세대 원자력 관련 ETF의 시장 확산을 추적합니다.",
    "냉각·열관리": "고밀도 AI 데이터센터의 냉각·열관리 수요 관련 흐름을 추적합니다.",
    "로봇·자동화": "자동화와 로봇 산업 관련 ETF의 추세 확산을 추적합니다.",
    "방산·우주": "방산 및 우주산업 관련 ETF의 시장 흐름을 추적합니다.",
    "조선·해양": "조선·해양 및 관련 산업의 시장 확산을 추적합니다.",
    "2차전지": "배터리 및 전기차 생태계의 시장 흐름을 추적합니다.",
    "바이오·헬스케어": "바이오·제약 및 헬스케어 산업의 시장 흐름을 추적합니다.",
    "자동차·모빌리티": "자동차·전기차·자율주행 관련 산업의 흐름을 추적합니다.",
    "인터넷·AI소프트웨어": "AI·클라우드·소프트웨어 산업의 시장 흐름을 추적합니다.",
    "친환경·신재생": "신재생·수소·친환경 에너지 관련 산업의 흐름을 추적합니다.",
    "금융·고배당": "금융·배당·리츠 관련 ETF의 시장 흐름을 추적합니다.",
}


# ============================================================
# SESSION STATE
# ============================================================

if "selected_code" not in st.session_state:
    st.session_state.selected_code = None

if "future_detail_code" not in st.session_state:
    st.session_state.future_detail_code = None

if "future_detail_theme" not in st.session_state:
    st.session_state.future_detail_theme = None

if "future_updated_at" not in st.session_state:
    st.session_state.future_updated_at = None

if "future_results" not in st.session_state:
    st.session_state.future_results = None


# ============================================================
# BASIC UTILITIES
# ============================================================

def clean_code(code):
    if code is None:
        return ""

    s = str(code).strip()

    m = re.search(r"(\d{6})", s)

    if m:
        return m.group(1)

    return s


def safe_float(v, default=np.nan):
    try:
        if v is None:
            return default

        if isinstance(v, str):
            v = v.replace(",", "").replace("%", "").strip()

        return float(v)

    except Exception:
        return default


def pct(v):
    if pd.isna(v):
        return "-"

    return f"{v:+.1f}%"


def num(v, digits=2):
    if pd.isna(v):
        return "-"

    return f"{v:,.{digits}f}"


def load_json_file(path, default):
    try:
        if not os.path.exists(path):
            return default

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return default


def save_json_file(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return True

    except Exception:
        return False


def normalize_name(text):
    if text is None:
        return ""

    text = str(text)

    replacements = {
        "\xa0": " ",
        "\n": " ",
        "\r": " ",
        "　": " ",
    }

    for a, b in replacements.items():
        text = text.replace(a, b)

    return re.sub(r"\s+", " ", text).strip()


def safe_etf_name(value, code=""):
    if isinstance(value, dict):
        for key in [
            "itemname",
            "itemName",
            "name",
            "etfName",
            "isuNm",
            "ISU_NM",
        ]:
            if key in value and value[key]:
                return normalize_name(value[key])

    s = normalize_name(value)

    if not s or s.lower() in ["nan", "none"]:
        return f"ETF {code}"

    return s


# ============================================================
# ETF MASTER
# ============================================================

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_naver_etf_master():

    rows = []

    try:

        r = requests.get(
            KOREAN_ETF_URL,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        )

        r.raise_for_status()

        data = r.json()

        items = data.get("result", {}).get("etfItemList", [])

        for item in items:

            code = clean_code(
                item.get("itemcode")
                or item.get("itemCode")
                or item.get("code")
            )

            if len(code) != 6:
                continue

            name = safe_etf_name(
                item.get("itemname")
                or item.get("itemName")
                or item.get("name"),
                code,
            )

            rows.append(
                {
                    "code": code,
                    "name": name,
                    "source": "NAVER",
                }
            )

    except Exception:
        pass

    return pd.DataFrame(rows)


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_krx_etf_master():

    rows = []

    url = (
        "https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd"
    )

    try:

        r = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://data.krx.co.kr/",
            },
        )

        if r.status_code == 200:

            data = r.json()

            items = (
                data.get("OutBlock_1")
                or data.get("output")
                or []
            )

            for item in items:

                code = clean_code(
                    item.get("ISU_SRT_CD")
                    or item.get("isuSrtCd")
                    or item.get("code")
                )

                if len(code) != 6:
                    continue

                name = safe_etf_name(
                    item.get("ISU_ABBRV")
                    or item.get("isuAbrv")
                    or item.get("name"),
                    code,
                )

                rows.append(
                    {
                        "code": code,
                        "name": name,
                        "source": "KRX",
                    }
                )

    except Exception:
        pass

    return pd.DataFrame(rows)


@st.cache_data(ttl=1800, show_spinner=False)
def load_etf_universe():

    frames = []

    naver = fetch_naver_etf_master()

    if not naver.empty:
        frames.append(naver)

    krx = fetch_krx_etf_master()

    if not krx.empty:
        frames.append(krx)

    if not frames:
        return pd.DataFrame(
            {
                "code": [],
                "name": [],
                "source": [],
            }
        )

    df = pd.concat(frames, ignore_index=True)

    df["code"] = df["code"].astype(str).map(clean_code)
    df["name"] = df["name"].astype(str).map(normalize_name)

    df = df[df["code"].str.len() == 6]

    df = (
        df.sort_values(["code", "source"])
        .drop_duplicates("code", keep="first")
        .reset_index(drop=True)
    )

    return df


# ============================================================
# PRICE DATA
# ============================================================

def yahoo_symbol(code):
    return f"{clean_code(code)}.KS"


@st.cache_data(ttl=300, show_spinner=False)
def fetch_price_data(code, period="1y"):

    code = clean_code(code)

    if not code:
        return pd.DataFrame()

    # -------------------------
    # Yahoo
    # -------------------------

    try:

        df = yf.download(
            yahoo_symbol(code),
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False,
        )

        if isinstance(df.columns, pd.MultiIndex):

            try:
                df.columns = df.columns.get_level_values(0)
            except Exception:
                pass

        df = df.reset_index()

        if not df.empty:

            rename_map = {}

            for col in df.columns:

                c = str(col).lower()

                if c == "date":
                    rename_map[col] = "Date"

                elif c == "open":
                    rename_map[col] = "Open"

                elif c == "high":
                    rename_map[col] = "High"

                elif c == "low":
                    rename_map[col] = "Low"

                elif c == "close":
                    rename_map[col] = "Close"

                elif c == "volume":
                    rename_map[col] = "Volume"

            df = df.rename(columns=rename_map)

            needed = [
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]

            if all(x in df.columns for x in needed):

                for col in needed[1:]:
                    df[col] = pd.to_numeric(
                        df[col],
                        errors="coerce",
                    )

                df = df.dropna(
                    subset=["Close"]
                )

                if len(df) >= 20:
                    return df[needed].copy()

    except Exception:
        pass

    # -------------------------
    # Naver fallback
    # -------------------------

    try:

        url = (
            "https://fchart.stock.naver.com/"
            f"fchart.nhn?symbol={code}&"
            "timeframe=day&"
            "count=400&"
            "requestType=0"
        )

        r = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        )

        root = ET.fromstring(r.text)

        rows = []

        for item in root.findall(".//item"):

            data = item.attrib.get("data", "")

            parts = data.split("|")

            if len(parts) < 7:
                continue

            rows.append(
                {
                    "Date": pd.to_datetime(parts[0]),
                    "Open": safe_float(parts[1]),
                    "High": safe_float(parts[2]),
                    "Low": safe_float(parts[3]),
                    "Close": safe_float(parts[4]),
                    "Volume": safe_float(parts[6]),
                }
            )

        df = pd.DataFrame(rows)

        if not df.empty:
            return df.sort_values("Date").reset_index(drop=True)

    except Exception:
        pass

    return pd.DataFrame()


# ============================================================
# INDICATORS
# ============================================================

def calculate_indicators(df):

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    close = pd.to_numeric(
        df["Close"],
        errors="coerce",
    )

    volume = pd.to_numeric(
        df["Volume"],
        errors="coerce",
    )

    df["MA20"] = close.rolling(20).mean()
    df["MA60"] = close.rolling(60).mean()
    df["MA120"] = close.rolling(120).mean()

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    df["RSI14"] = 100 - (
        100 / (1 + rs)
    )

    df["VOL20"] = volume.rolling(20).mean()

    df["VOL_RATIO"] = (
        volume /
        df["VOL20"].replace(0, np.nan)
    )

    df["RET5"] = close.pct_change(5) * 100
    df["RET20"] = close.pct_change(20) * 100
    df["RET60"] = close.pct_change(60) * 100

    df["HIGH20"] = close.rolling(20).max()
    df["LOW20"] = close.rolling(20).min()

    df["HIGH60"] = close.rolling(60).max()
    df["LOW60"] = close.rolling(60).min()

    df["ABOVE_MA20"] = close > df["MA20"]
    df["ABOVE_MA60"] = close > df["MA60"]

    return df


def latest_row(df):

    if df is None or df.empty:
        return None

    return df.iloc[-1]


# ============================================================
# ETF JUDGMENT
# ============================================================

def judge_etf(df):

    row = latest_row(df)

    if row is None:
        return {
            "title": "데이터 부족",
            "reason": "분석 가능한 가격 데이터가 부족합니다.",
            "action": "관찰",
        }

    rsi = safe_float(row.get("RSI14"))
    ret20 = safe_float(row.get("RET20"))
    ma20 = safe_float(row.get("MA20"))
    ma60 = safe_float(row.get("MA60"))
    close = safe_float(row.get("Close"))

    if (
        not pd.isna(ma20)
        and not pd.isna(ma60)
        and close > ma20 > ma60
    ):
        trend = "상승 추세"

    elif (
        not pd.isna(ma20)
        and not pd.isna(ma60)
        and close < ma20 < ma60
    ):
        trend = "중기 약세"

    else:
        trend = "방향 확인"

    if not pd.isna(rsi) and rsi >= 72:
        rsi_state = "과열"

    elif not pd.isna(rsi) and rsi >= 55:
        rsi_state = "강세"

    elif not pd.isna(rsi) and rsi <= 35:
        rsi_state = "침체"

    else:
        rsi_state = "중립"

    if trend == "상승 추세" and rsi_state == "과열":
        title = "상승 추세 · 추격 주의"
        action = "추격 매수보다 눌림 확인"

    elif trend == "상승 추세":
        title = "상승 추세 유지"
        action = "조정 시 분할 접근"

    elif trend == "중기 약세":
        title = "중기 약세 · 방어 우선"
        action = "지지선 회복 확인"

    else:
        title = "방향 확인 구간"
        action = "추세 확인 후 대응"

    reason = (
        f"{trend}, RSI {num(rsi,1)}, "
        f"20일 수익률 {pct(ret20)}입니다."
    )

    return {
        "title": title,
        "reason": reason,
        "action": action,
    }


# ============================================================
# PRICE LEVELS
# ============================================================

def price_levels(df):

    row = latest_row(df)

    if row is None:
        return {
            "interest": np.nan,
            "support": np.nan,
            "breakout": np.nan,
            "risk": np.nan,
        }

    ma20 = safe_float(row.get("MA20"))
    ma60 = safe_float(row.get("MA60"))
    low20 = safe_float(row.get("LOW20"))
    high20 = safe_float(row.get("HIGH20"))
    low60 = safe_float(row.get("LOW60"))

    support_candidates = [
        x for x in [ma60, low20]
        if not pd.isna(x)
    ]

    risk_candidates = [
        x for x in [ma60, low20, low60]
        if not pd.isna(x)
    ]

    return {
        "interest": ma20,
        "support": min(support_candidates)
        if support_candidates else np.nan,
        "breakout": high20,
        "risk": min(risk_candidates)
        if risk_candidates else np.nan,
    }


def scenario_state(df):

    row = latest_row(df)

    levels = price_levels(df)

    if row is None:
        return "데이터 부족"

    close = safe_float(row.get("Close"))

    interest = levels["interest"]
    support = levels["support"]
    breakout = levels["breakout"]

    if not pd.isna(support) and close < support:
        return "핵심 지지 하회"

    if not pd.isna(support) and close <= support * 1.025:
        return "핵심 지지 접근"

    if not pd.isna(interest) and close <= interest * 1.025:
        return "1차 관심구간"

    if not pd.isna(breakout) and close >= breakout * 0.995:
        return "돌파구간"

    return "추세 유지구간"


# ============================================================
# CHART
# ============================================================

def render_chart(df, title="가격 차트"):

    if df is None or df.empty:
        st.info("차트 데이터가 없습니다.")
        return

    chart = df.tail(126).copy()

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=chart["Date"],
            open=chart["Open"],
            high=chart["High"],
            low=chart["Low"],
            close=chart["Close"],
            name="가격",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=chart["Date"],
            y=chart["MA20"],
            mode="lines",
            name="MA20",
            line={"width": 1.5},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=chart["Date"],
            y=chart["MA60"],
            mode="lines",
            name="MA60",
            line={"width": 1.5},
        )
    )

    fig.update_layout(
        title=title,
        height=410,
        margin=dict(l=5, r=5, t=35, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dbe7f5"),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        dragmode=False,
    )

    fig.update_xaxes(
        fixedrange=True,
        showgrid=False,
    )

    fig.update_yaxes(
        fixedrange=True,
        showgrid=True,
        gridcolor="rgba(120,150,180,.10)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "staticPlot": False,
            "scrollZoom": False,
        },
    )


# ============================================================
# ETF SEARCH
# ============================================================

def search_etfs(universe, query):

    if universe is None or universe.empty:
        return pd.DataFrame()

    q = normalize_name(query).lower()

    if not q:
        return universe.head(100)

    mask = (
        universe["code"]
        .astype(str)
        .str.lower()
        .str.contains(q, na=False)
        |
        universe["name"]
        .astype(str)
        .str.lower()
        .str.contains(q, na=False)
    )

    return universe[mask].head(100)


# ============================================================
# WATCHLIST
# ============================================================

def get_watchlist():

    data = load_json_file(
        WATCHLIST_FILE,
        DEFAULT_WATCHLIST,
    )

    if not isinstance(data, list):
        return DEFAULT_WATCHLIST.copy()

    return [
        clean_code(x)
        for x in data
        if clean_code(x)
    ]


def set_watchlist(codes):

    codes = list(
        dict.fromkeys(
            clean_code(x)
            for x in codes
            if clean_code(x)
        )
    )

    save_json_file(
        WATCHLIST_FILE,
        codes,
    )


# ============================================================
# HOLDINGS
# ============================================================

def get_holdings():

    data = load_json_file(
        HOLDINGS_FILE,
        {},
    )

    return data if isinstance(data, dict) else {}


def save_holdings(data):

    return save_json_file(
        HOLDINGS_FILE,
        data,
    )


# ============================================================
# THEME MATCHING
# ============================================================

def matching_themes(name):

    name = normalize_name(name)

    found = []

    for theme, words in THEME_VOCABULARY.items():

        for word in words:

            if word.lower() in name.lower():
                found.append(theme)
                break

    return found


def build_theme_groups(universe):

    groups = {}

    if universe is None or universe.empty:
        return groups

    for _, row in universe.iterrows():

        code = clean_code(row["code"])
        name = safe_etf_name(row["name"], code)

        themes = matching_themes(name)

        for theme in themes:

            groups.setdefault(
                theme,
                [],
            ).append(
                {
                    "code": code,
                    "name": name,
                }
            )

    return groups


# ============================================================
# ETF SNAPSHOT FOR THEME ENGINE
# ============================================================

@st.cache_data(ttl=1800, show_spinner=False)
def theme_etf_snapshot(code):

    df = fetch_price_data(
        code,
        period="1y",
    )

    if df.empty or len(df) < 65:
        return None

    df = calculate_indicators(df)

    row = latest_row(df)

    if row is None:
        return None

    return {
        "code": code,
        "close": safe_float(row.get("Close")),
        "ret5": safe_float(row.get("RET5")),
        "ret20": safe_float(row.get("RET20")),
        "ret60": safe_float(row.get("RET60")),
        "rsi": safe_float(row.get("RSI14")),
        "vol_ratio": safe_float(row.get("VOL_RATIO")),
        "above_ma20": bool(row.get("ABOVE_MA20", False)),
        "above_ma60": bool(row.get("ABOVE_MA60", False)),
        "ma20": safe_float(row.get("MA20")),
        "ma60": safe_float(row.get("MA60")),
    }


@st.cache_data(ttl=1800, show_spinner=False)
def benchmark_snapshot():

    df = fetch_price_data(
        BENCHMARK_CODE,
        period="1y",
    )

    if df.empty:
        return None

    df = calculate_indicators(df)

    row = latest_row(df)

    if row is None:
        return None

    return {
        "ret5": safe_float(row.get("RET5")),
        "ret20": safe_float(row.get("RET20")),
        "ret60": safe_float(row.get("RET60")),
    }


# ============================================================
# THEME SCORING
# ============================================================

def clamp(v, low=0, high=100):

    if pd.isna(v):
        return low

    return max(
        low,
        min(high, float(v)),
    )


def normalize_score(value, low, high):

    if pd.isna(value):
        return 50

    if high == low:
        return 50

    return clamp(
        (value - low)
        / (high - low)
        * 100
    )


def score_theme(theme, members):

    snapshots = []

    for item in members:

        snap = theme_etf_snapshot(
            item["code"]
        )

        if snap is not None:
            snap["name"] = item["name"]
            snapshots.append(snap)

    if len(snapshots) < 2:
        return None

    df = pd.DataFrame(snapshots)

    benchmark = benchmark_snapshot()

    avg_ret5 = df["ret5"].mean()
    avg_ret20 = df["ret20"].mean()
    avg_ret60 = df["ret60"].mean()

    avg_vol = df["vol_ratio"].mean()
    avg_rsi = df["rsi"].mean()

    breadth20 = (
        (df["ret20"] > 0).mean() * 100
    )

    breadth60 = (
        (df["ret60"] > 0).mean() * 100
    )

    trend20 = (
        df["above_ma20"].mean() * 100
    )

    trend60 = (
        df["above_ma60"].mean() * 100
    )

    # -----------------------------
    # Relative strength
    # -----------------------------

    if benchmark:

        rs20 = (
            avg_ret20 -
            benchmark["ret20"]
        )

        rs60 = (
            avg_ret60 -
            benchmark["ret60"]
        )

    else:
        rs20 = 0
        rs60 = 0

    # -----------------------------
    # Persistence
    # -----------------------------

    positive5 = (
        df["ret5"] > 0
    ).mean()

    positive20 = (
        df["ret20"] > 0
    ).mean()

    positive60 = (
        df["ret60"] > 0
    ).mean()

    persistence = (
        positive5 * 35
        + positive20 * 35
        + positive60 * 30
    )

    # -----------------------------
    # Momentum score
    # -----------------------------

    momentum_score = (
        normalize_score(
            avg_ret20,
            -10,
            20,
        ) * 0.55
        +
        normalize_score(
            avg_ret60,
            -20,
            40,
        ) * 0.45
    )

    # -----------------------------
    # Volume score
    # -----------------------------

    volume_score = normalize_score(
        avg_vol,
        0.70,
        2.50,
    )

    # -----------------------------
    # Relative strength score
    # -----------------------------

    relative_score = (
        normalize_score(
            rs20,
            -10,
            15,
        ) * 0.60
        +
        normalize_score(
            rs60,
            -20,
            30,
        ) * 0.40
    )

    # -----------------------------
    # Trend score
    # -----------------------------

    trend_score = (
        trend20 * 0.45
        + trend60 * 0.55
    )

    # -----------------------------
    # Breadth score
    # -----------------------------

    breadth_score = (
        breadth20 * 0.55
        + breadth60 * 0.45
    )

    # -----------------------------
    # Overheat penalty
    # -----------------------------

    overheat = 0

    if avg_rsi > 72:
        overheat += min(
            12,
            (avg_rsi - 72) * 1.5,
        )

    if avg_ret5 > 10:
        overheat += min(
            8,
            (avg_ret5 - 10) * 0.8,
        )

    if avg_vol > 2.5:
        overheat += 4

    # -----------------------------
    # Final score
    # -----------------------------

    raw_score = (
        momentum_score * 0.20
        + normalize_score(
            avg_ret60,
            -20,
            40,
        ) * 0.15
        + volume_score * 0.15
        + relative_score * 0.15
        + trend_score * 0.10
        + breadth_score * 0.10
        + persistence * 0.10
        + normalize_score(
            len(snapshots),
            2,
            8,
        ) * 0.05
    )

    final_score = clamp(
        raw_score - overheat
    )

    # -----------------------------
    # Stage
    # -----------------------------

    if (
        final_score >= 80
        and avg_ret20 >= 8
        and breadth20 >= 65
    ):

        stage = "현재 주도"

    elif (
        final_score >= 72
        and (
            rs20 >= 3
            or trend20 >= 60
        )
    ):

        stage = "다음 수혜"

    elif (
        final_score >= 64
        and (
            avg_vol >= 1.10
            or breadth20 >= 55
        )
    ):

        stage = "관심 확대"

    elif final_score >= 55:

        stage = "초기 관심"

    else:

        stage = "관찰"

    # -----------------------------
    # Reasons
    # -----------------------------

    reasons = []

    if avg_ret20 >= 5:
        reasons.append(
            f"20일 평균 수익률 {avg_ret20:+.1f}%"
        )

    if avg_ret60 >= 10:
        reasons.append(
            f"60일 평균 수익률 {avg_ret60:+.1f}%"
        )

    if avg_vol >= 1.15:
        reasons.append(
            f"거래량 {avg_vol:.2f}배"
        )

    if rs20 >= 3:
        reasons.append(
            f"KOSPI 대비 상대강도 {rs20:+.1f}%p"
        )

    if breadth20 >= 60:
        reasons.append(
            f"상승 ETF 비율 {breadth20:.0f}%"
        )

    if trend60 >= 60:
        reasons.append(
            f"60일선 위 ETF {trend60:.0f}%"
        )

    if persistence >= 65:
        reasons.append(
            "단기·중기 상승 지속성 양호"
        )

    if avg_rsi >= 72:
        reasons.append(
            "단기 과열 신호 존재"
        )

    if not reasons:
        reasons.append(
            "시장 데이터 변화가 관찰되고 있습니다."
        )

    return {
        "theme": theme,
        "score": round(final_score, 1),
        "stage": stage,
        "count": len(snapshots),
        "avg_ret5": avg_ret5,
        "avg_ret20": avg_ret20,
        "avg_ret60": avg_ret60,
        "avg_vol": avg_vol,
        "avg_rsi": avg_rsi,
        "breadth20": breadth20,
        "breadth60": breadth60,
        "trend20": trend20,
        "trend60": trend60,
        "rs20": rs20,
        "rs60": rs60,
        "persistence": persistence,
        "overheat": overheat,
        "reasons": reasons,
        "etfs": snapshots,
    }


# ============================================================
# AUTOMATIC FUTURE THEME ENGINE
# ============================================================

@st.cache_data(
    ttl=THEME_CACHE_MINUTES * 60,
    show_spinner=False,
)
def run_future_theme_engine():

    universe = load_etf_universe()

    if universe.empty:
        return []

    groups = build_theme_groups(
        universe
    )

    results = []

    for theme, members in groups.items():

        # 너무 작은 그룹은 제외
        if len(members) < 2:
            continue

        # 동일 ETF 중복 제거
        unique = {}
        for item in members:
            unique[item["code"]] = item

        members = list(unique.values())

        # 지나치게 큰 그룹은 상위 12개만
        members = members[:12]

        result = score_theme(
            theme,
            members,
        )

        if result is not None:
            results.append(result)

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True,
    )

    return results


def refresh_future_theme_engine():

    run_future_theme_engine.clear()
    theme_etf_snapshot.clear()
    benchmark_snapshot.clear()

    results = run_future_theme_engine()

    st.session_state.future_results = results
    st.session_state.future_updated_at = datetime.now()

    return results


# ============================================================
# FUTURE THEME UI
# ============================================================

def stage_badge(stage):

    if stage == "현재 주도":
        return "🔥 현재 주도"

    if stage == "다음 수혜":
        return "🚀 다음 수혜"

    if stage == "관심 확대":
        return "📈 관심 확대"

    if stage == "초기 관심":
        return "🌱 초기 관심"

    return "👀 관찰"


def render_future_theme_detail(theme_result):

    if not theme_result:
        return

    theme = theme_result["theme"]

    st.markdown(
        f"""
<div class="hero">
    <div class="hero-title">
        {html.escape(theme)}
    </div>
    <div class="hero-code">
        자동 미래테마 상세 분석
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="metric-grid">

<div class="metric">
<div class="metric-title">테마 점수</div>
<div class="metric-value">{theme_result['score']:.1f}</div>
</div>

<div class="metric">
<div class="metric-title">20일 평균</div>
<div class="metric-value">{theme_result['avg_ret20']:+.1f}%</div>
</div>

<div class="metric">
<div class="metric-title">거래량</div>
<div class="metric-value">{theme_result['avg_vol']:.2f}배</div>
</div>

<div class="metric">
<div class="metric-title">상승 ETF 비율</div>
<div class="metric-value">{theme_result['breadth20']:.0f}%</div>
</div>

</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="reason">
<b>선정 단계</b><br>
{stage_badge(theme_result['stage'])}<br><br>

<b>선정 근거</b><br>
{" · ".join(theme_result["reasons"])}
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### 구성 ETF")

    for item in theme_result["etfs"]:

        c1, c2, c3 = st.columns(
            [3.0, 1.2, 1.1]
        )

        with c1:
            st.markdown(
                f"""
<b>{html.escape(item['name'])}</b><br>
<span class="small">{item['code']}</span>
""",
                unsafe_allow_html=True,
            )

        with c2:
            st.write(
                f"20일 {item['ret20']:+.1f}%"
            )

        with c3:

            if st.button(
                "ETF 분석",
                key=f"future_detail_{theme}_{item['code']}",
                use_container_width=True,
            ):
                st.session_state.selected_code = item[
                    "code"
                ]
                st.session_state.future_detail_code = None
                st.rerun()


def render_future_theme():

    st.markdown(
        """
<div class="hero">
<div class="hero-title">🚀 미래테마</div>
<div class="hero-code">
시장 데이터를 분석하여 현재 시장에서 관심이 확대되는 테마를 자동 탐색합니다.
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(
        [3, 1]
    )

    with col1:

        if st.session_state.future_updated_at:

            update_text = (
                st.session_state.future_updated_at
                .strftime("%Y-%m-%d %H:%M")
            )

            st.caption(
                f"마지막 업데이트: {update_text}"
            )

        else:

            st.caption(
                "시장 데이터 기반 자동 분석"
            )

    with col2:

        if st.button(
            "🔄 미래테마 업데이트",
            use_container_width=True,
        ):

            with st.spinner(
                "시장 데이터를 분석하고 있습니다..."
            ):
                refresh_future_theme_engine()

            st.rerun()

    if st.session_state.future_results is None:

        with st.spinner(
            "미래테마를 자동 탐색하고 있습니다..."
        ):

            st.session_state.future_results = (
                run_future_theme_engine()
            )

            st.session_state.future_updated_at = (
                datetime.now()
            )

    results = (
        st.session_state.future_results
        or []
    )

    if not results:

        st.warning(
            "현재 분석 가능한 미래테마 데이터가 부족합니다."
        )

        return

    # --------------------------------------------------------
    # Top themes
    # --------------------------------------------------------

    top_results = results[:8]

    for idx, result in enumerate(
        top_results,
        start=1,
    ):

        theme = result["theme"]

        st.markdown(
            f"""
<div class="theme-card">

<div style="display:flex;
justify-content:space-between;
align-items:center;">

<div>
<span class="small">#{idx}</span>
<div class="theme-name">
{html.escape(theme)}
</div>
</div>

<div style="text-align:right;">
<div class="theme-score">
{result['score']:.0f}
</div>
<div class="small">THEME SCORE</div>
</div>

</div>

<div style="margin-top:8px;">
<span class="badge">
{stage_badge(result['stage'])}
</span>

<span class="badge">
ETF {result['count']}개
</span>
</div>

<div class="reason">

<b>왜 선정되었는가?</b><br>

20일 평균 {result['avg_ret20']:+.1f}% ·
60일 평균 {result['avg_ret60']:+.1f}% ·
거래량 {result['avg_vol']:.2f}배 ·
상승 ETF {result['breadth20']:.0f}% ·
KOSPI 대비 상대강도 {result['rs20']:+.1f}%p

<br><br>

{" · ".join(result["reasons"])}

</div>

</div>
""",
            unsafe_allow_html=True,
        )

        b1, b2 = st.columns(
            [1, 1]
        )

        with b1:

            if st.button(
                "테마 상세분석",
                key=f"theme_analysis_{theme}",
                use_container_width=True,
            ):

                st.session_state.future_detail_theme = theme
                st.rerun()

        with b2:

            if st.button(
                "구성 ETF 보기",
                key=f"theme_etfs_{theme}",
                use_container_width=True,
            ):

                st.session_state.future_detail_theme = theme
                st.rerun()

    # --------------------------------------------------------
    # Detail
    # --------------------------------------------------------

    selected_theme = (
        st.session_state.future_detail_theme
    )

    if selected_theme:

        selected = next(
            (
                x
                for x in results
                if x["theme"] == selected_theme
            ),
            None,
        )

        if selected:

            st.divider()

            render_future_theme_detail(
                selected
            )


# ============================================================
# HOLDING / ETF DETAIL
# ============================================================

def render_etf_detail(code, universe):

    code = clean_code(code)

    if not code:
        st.info("ETF를 선택해주세요.")
        return

    match = universe[
        universe["code"] == code
    ]

    if not match.empty:
        name = safe_etf_name(
            match.iloc[0]["name"],
            code,
        )
    else:
        name = f"ETF {code}"

    with st.spinner(
        f"{name} 분석 중..."
    ):

        df = fetch_price_data(
            code,
            period="1y",
        )

        df = calculate_indicators(
            df
        )

    if df.empty:

        st.error(
            "가격 데이터를 가져오지 못했습니다."
        )

        return

    row = latest_row(df)

    if row is None:
        return

    close = safe_float(
        row.get("Close")
    )

    prev_close = (
        safe_float(
            df.iloc[-2]["Close"]
        )
        if len(df) >= 2
        else np.nan
    )

    daily_change = (
        (close / prev_close - 1)
        * 100
        if (
            not pd.isna(close)
            and not pd.isna(prev_close)
            and prev_close != 0
        )
        else np.nan
    )

    judgment = judge_etf(df)
    levels = price_levels(df)
    state = scenario_state(df)

    st.markdown(
        f"""
<div class="hero">

<div class="hero-title">
{html.escape(name)}
</div>

<div class="hero-code">
{code}
</div>

<div class="hero-price">
{num(close,0)}
</div>

<div class="{'good' if daily_change >= 0 else 'bad'}">
오늘 {pct(daily_change)}
</div>

</div>
""",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    rsi = safe_float(
        row.get("RSI14")
    )

    vol_ratio = safe_float(
        row.get("VOL_RATIO")
    )

    ret20 = safe_float(
        row.get("RET20")
    )

    ret60 = safe_float(
        row.get("RET60")
    )

    st.markdown(
        f"""
<div class="metric-grid">

<div class="metric">
<div class="metric-title">RSI</div>
<div class="metric-value">{num(rsi,1)}</div>
</div>

<div class="metric">
<div class="metric-title">거래량</div>
<div class="metric-value">{num(vol_ratio,2)}배</div>
</div>

<div class="metric">
<div class="metric-title">20일 수익률</div>
<div class="metric-value">{pct(ret20)}</div>
</div>

<div class="metric">
<div class="metric-title">60일 수익률</div>
<div class="metric-value">{pct(ret60)}</div>
</div>

</div>
""",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Judgment
    # --------------------------------------------------------

    st.markdown("### 현재 판단")

    st.markdown(
        f"""
<div class="card">

<div style="font-size:20px;font-weight:800;">
{judgment['title']}
</div>

<div class="reason">
{judgment['reason']}<br><br>
<b>대응:</b> {judgment['action']}
</div>

<div style="margin-top:10px;">
<span class="badge">
현재상태: {state}
</span>
</div>

</div>
""",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Price levels
    # --------------------------------------------------------

    st.markdown("### 가격 구간")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "1차 관심",
            num(levels["interest"], 0),
        )

    with c2:
        st.metric(
            "핵심 지지",
            num(levels["support"], 0),
        )

    with c3:
        st.metric(
            "돌파 기준",
            num(levels["breakout"], 0),
        )

    with c4:
        st.metric(
            "위험 가격",
            num(levels["risk"], 0),
        )

    # --------------------------------------------------------
    # Scenario
    # --------------------------------------------------------

    st.markdown("### 대응 시나리오")

    scenarios = [
        (
            "① 1차 관심",
            levels["interest"],
            "20일 이동평균선 부근의 눌림 여부를 확인합니다.",
        ),
        (
            "② 핵심 지지",
            levels["support"],
            "중기 추세가 유지되는지 확인하는 기준입니다.",
        ),
        (
            "③ 돌파 기준",
            levels["breakout"],
            "최근 20일 고점 돌파 여부를 확인합니다.",
        ),
        (
            "④ 위험 가격",
            levels["risk"],
            "핵심 지지 이탈 시 추세 훼손 여부를 재검토합니다.",
        ),
    ]

    for title, price, text in scenarios:

        st.markdown(
            f"""
<div class="scenario">
<div class="scenario-title">
{title} · {num(price,0)}
</div>
<div class="scenario-text">
{text}
</div>
</div>
""",
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # Holdings
    # --------------------------------------------------------

    holdings = get_holdings()

    holding = holdings.get(
        code,
        {},
    )

    st.markdown("### 보유정보")

    hc1, hc2 = st.columns(2)

    with hc1:

        avg_price = st.number_input(
            "평균매수가",
            min_value=0.0,
            value=float(
                holding.get(
                    "avg_price",
                    0,
                )
            ),
            step=100.0,
            key=f"avg_{code}",
        )

    with hc2:

        quantity = st.number_input(
            "보유수량",
            min_value=0,
            value=int(
                holding.get(
                    "quantity",
                    0,
                )
            ),
            step=1,
            key=f"qty_{code}",
        )

    bc1, bc2 = st.columns(2)

    with bc1:

        if st.button(
            "보유정보 저장",
            key=f"save_hold_{code}",
            use_container_width=True,
        ):

            holdings[code] = {
                "avg_price": avg_price,
                "quantity": quantity,
            }

            if save_holdings(holdings):
                st.success(
                    "보유정보를 저장했습니다."
                )

    with bc2:

        if st.button(
            "보유정보 삭제",
            key=f"delete_hold_{code}",
            use_container_width=True,
        ):

            if code in holdings:
                del holdings[code]

            save_holdings(holdings)

            st.rerun()

    if (
        avg_price > 0
        and quantity > 0
        and close > 0
    ):

        pnl = (
            close - avg_price
        ) * quantity

        pnl_pct = (
            close / avg_price - 1
        ) * 100

        st.markdown(
            f"""
<div class="card">

<b>평가손익</b><br>

<span class="{'good' if pnl >= 0 else 'bad'}"
style="font-size:22px;font-weight:800;">

{pnl:+,.0f}원

</span>

<br>

<span class="small">
수익률 {pnl_pct:+.2f}%
</span>

</div>
""",
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # Chart
    # --------------------------------------------------------

    st.markdown("### 차트")

    render_chart(
        df,
        title=name,
    )


# ============================================================
# ETF FINDER
# ============================================================

def render_etf_finder(universe):

    st.markdown("### 🔎 ETF 찾기")

    query = st.text_input(
        "ETF명 또는 종목코드",
        placeholder="예: 반도체 / 395160",
        key="finder_query",
    )

    results = search_etfs(
        universe,
        query,
    )

    if results.empty:

        st.info(
            "검색 결과가 없습니다."
        )

        return

    for _, row in results.head(20).iterrows():

        code = clean_code(
            row["code"]
        )

        name = safe_etf_name(
            row["name"],
            code,
        )

        c1, c2, c3 = st.columns(
            [1.1, 4.2, 1.3]
        )

        with c1:
            st.markdown(
                f"""
<span class="small">{code}</span>
""",
                unsafe_allow_html=True,
            )

        with c2:
            st.write(name)

        with c3:

            if st.button(
                "분석",
                key=f"finder_analyze_{code}",
                use_container_width=True,
            ):

                st.session_state.selected_code = code
                st.rerun()

            watchlist = get_watchlist()

            if code not in watchlist:

                if st.button(
                    "추가",
                    key=f"finder_add_{code}",
                    use_container_width=True,
                ):

                    watchlist.append(code)

                    set_watchlist(
                        watchlist
                    )

                    st.rerun()


# ============================================================
# WATCHLIST
# ============================================================

def render_watchlist(universe):

    watchlist = get_watchlist()

    if not watchlist:
        st.info(
            "관심 ETF가 없습니다."
        )
        return

    name_map = {}

    for _, row in universe.iterrows():

        code = clean_code(
            row["code"]
        )

        name_map[code] = safe_etf_name(
            row["name"],
            code,
        )

    options = []

    for code in watchlist:

        options.append(
            f"{code} · "
            f"{name_map.get(code, 'ETF ' + code)}"
        )

    selected_label = st.selectbox(
        "관심 ETF",
        options,
        key="watchlist_select",
    )

    selected_code = clean_code(
        selected_label.split("·")[0]
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "ETF 분석",
            use_container_width=True,
        ):

            st.session_state.selected_code = (
                selected_code
            )
            st.rerun()

    with c2:

        if st.button(
            "관심종목 삭제",
            use_container_width=True,
        ):

            watchlist = [
                x for x in watchlist
                if x != selected_code
            ]

            set_watchlist(
                watchlist
            )

            st.rerun()


# ============================================================
# MARKET RADAR
# ============================================================

def radar_theme_for(name):

    matches = matching_themes(name)

    if matches:
        return matches[0]

    return "기타"


def radar_score(snap):

    if not snap:
        return np.nan

    score = 50

    score += (
        normalize_score(
            snap["ret20"],
            -10,
            20,
        )
        - 50
    ) * 0.35

    score += (
        normalize_score(
            snap["vol_ratio"],
            0.6,
            2.5,
        )
        - 50
    ) * 0.20

    score += (
        20
        if snap["above_ma20"]
        else -10
    )

    score += (
        15
        if snap["above_ma60"]
        else -10
    )

    if (
        not pd.isna(snap["rsi"])
        and snap["rsi"] > 72
    ):
        score -= 15

    if (
        not pd.isna(snap["ret5"])
        and snap["ret5"] > 8
    ):
        score -= 10

    return clamp(score)


def render_market_radar(universe):

    st.markdown(
        """
<div class="hero">
<div class="hero-title">🔥 시장 레이더</div>
<div class="hero-code">
시장 내 상대적으로 강한 ETF와 테마 흐름을 탐색합니다.
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    mode = st.radio(
        "레이더 모드",
        [
            "🎯 기회검색",
            "⚠️ 과열검색",
            "🔄 테마순환",
        ],
        horizontal=True,
    )

    watchlist = get_watchlist()

    candidates = []

    # 관심 ETF + 미래테마 ETF
    codes = list(watchlist)

    if st.session_state.future_results:

        for result in st.session_state.future_results:

            for item in result["etfs"]:
                codes.append(
                    item["code"]
                )

    codes = list(
        dict.fromkeys(codes)
    )

    with st.spinner(
        "시장 레이더 분석 중..."
    ):

        for code in codes:

            snap = theme_etf_snapshot(
                code
            )

            if snap is None:
                continue

            match = universe[
                universe["code"] == code
            ]

            if match.empty:
                name = f"ETF {code}"
            else:
                name = safe_etf_name(
                    match.iloc[0]["name"],
                    code,
                )

            snap["code"] = code
            snap["name"] = name
            snap["theme"] = radar_theme_for(
                name
            )
            snap["score"] = radar_score(
                snap
            )

            candidates.append(snap)

    if not candidates:

        st.info(
            "레이더 분석 데이터가 없습니다."
        )

        return

    df = pd.DataFrame(candidates)

    if mode == "🎯 기회검색":

        df = df[
            (df["score"] >= 55)
            &
            (df["rsi"] < 72)
        ].sort_values(
            "score",
            ascending=False,
        )

    elif mode == "⚠️ 과열검색":

        df["overheat"] = (
            df["rsi"].fillna(50) * 0.6
            + df["ret5"].fillna(0) * 2
            + df["vol_ratio"].fillna(1) * 5
        )

        df = df.sort_values(
            "overheat",
            ascending=False,
        )

    else:

        theme_rows = []

        for theme, group in df.groupby(
            "theme"
        ):

            theme_rows.append(
                {
                    "theme": theme,
                    "ETF수": len(group),
                    "20일": group["ret20"].mean(),
                    "5일": group["ret5"].mean(),
                    "거래량": group["vol_ratio"].mean(),
                    "강도": group["score"].mean(),
                }
            )

        theme_df = pd.DataFrame(
            theme_rows
        ).sort_values(
            "강도",
            ascending=False,
        )

        st.dataframe(
            theme_df,
            use_container_width=True,
            hide_index=True,
        )

        return

    if df.empty:

        st.info(
            "현재 조건에 해당하는 ETF가 없습니다."
        )

        return

    st.markdown("### 레이더 결과")

    for _, row in df.head(15).iterrows():

        c1, c2, c3, c4 = st.columns(
            [3.2, 1.2, 1.2, 1.2]
        )

        with c1:

            st.markdown(
                f"""
<b>{html.escape(row['name'])}</b><br>
<span class="small">
{row['code']} · {html.escape(row['theme'])}
</span>
""",
                unsafe_allow_html=True,
            )

        with c2:
            st.write(
                f"20일 {row['ret20']:+.1f}%"
            )

        with c3:
            st.write(
                f"RSI {row['rsi']:.1f}"
                if not pd.isna(row["rsi"])
                else "RSI -"
            )

        with c4:

            if st.button(
                f"분석 {row['code']}",
                key=f"radar_{row['code']}",
                use_container_width=True,
            ):

                st.session_state.selected_code = (
                    row["code"]
                )

                st.rerun()


# ============================================================
# MAIN ETF PAGE
# ============================================================

def render_my_etf(universe):

    st.markdown(
        """
<div class="hero">
<div class="hero-title">📊 내 ETF</div>
<div class="hero-code">
관심 ETF를 검색하고 기술적 분석과 대응 시나리오를 확인합니다.
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    render_etf_finder(
        universe
    )

    st.divider()

    render_watchlist(
        universe
    )

    if st.session_state.selected_code:

        st.divider()

        code = st.session_state.selected_code

        if st.button(
            "✕ 분석 닫기",
            key="close_detail",
        ):

            st.session_state.selected_code = None
            st.rerun()

        render_etf_detail(
            code,
            universe,
        )


# ============================================================
# AUTO REFRESH NOTICE
# ============================================================

def automatic_theme_refresh():

    if (
        st.session_state.future_updated_at
        is None
    ):
        return

    elapsed = (
        datetime.now()
        - st.session_state.future_updated_at
    ).total_seconds()

    if elapsed >= THEME_CACHE_MINUTES * 60:

        try:

            refresh_future_theme_engine()

        except Exception:
            pass


# ============================================================
# MAIN
# ============================================================

def main():

    universe = load_etf_universe()

    if universe.empty:

        st.error(
            "ETF 목록을 불러오지 못했습니다. "
            "잠시 후 다시 시도해주세요."
        )

        return

    automatic_theme_refresh()

    nav = st.radio(
        "",
        [
            "📊 내 ETF",
            "🚀 미래테마",
            "🔥 시장 레이더",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    if nav == "📊 내 ETF":

        render_my_etf(
            universe
        )

    elif nav == "🚀 미래테마":

        render_future_theme()

    elif nav == "🔥 시장 레이더":

        render_market_radar(
            universe
        )

    st.markdown(
        """
<div class="footer-note">
ETF RADAR · 시장 데이터 기반 분석 도구 ·
미래테마 점수는 시장 데이터의 변화와 상대강도를 정량화한 참고 지표입니다.
</div>
""",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()