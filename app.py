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


# ============================================================
# ETF RADAR
# Integrated Investment Decision Dashboard
# 미래테마 → ETF → 레이더 → 기술분석 → 가격구간 → 대응
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

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Noto Sans KR",
        "Malgun Gothic",
        Arial,
        sans-serif;
}

.stApp {
    background:#08111f;
    color:#e7edf5;
}

.block-container {
    max-width:1250px;
    padding:1rem 1rem 3rem 1rem;
}

h1,h2,h3,h4 {
    color:#f5f7fa !important;
    letter-spacing:-0.4px;
}

p,span,label,div {
    letter-spacing:-0.2px;
}

[data-testid="stHeader"] {
    background:rgba(8,17,31,0);
}

[data-testid="stToolbar"] {
    visibility:hidden;
}

div[data-baseweb="select"] > div {
    background:#111d2d !important;
    border:1px solid #26364b !important;
    color:#eef3f8 !important;
}

div[data-baseweb="select"] * {
    color:#eef3f8 !important;
}

input {
    background:#111d2d !important;
    color:#eef3f8 !important;
}

.stButton > button {
    width:100%;
    min-height:42px;
    border-radius:10px;
    border:1px solid #2b3d54;
    background:#122137;
    color:#edf3fa;
    font-weight:600;
}

.stButton > button:hover {
    border-color:#4f8cff;
    background:#182c47;
}

.hero {
    background:linear-gradient(
        135deg,
        #11243b 0%,
        #0d1828 55%,
        #101d30 100%
    );
    border:1px solid #263b55;
    border-radius:18px;
    padding:22px;
    margin:8px 0 18px 0;
}

.hero-title {
    font-size:28px;
    font-weight:800;
    margin-bottom:5px;
}

.hero-sub {
    color:#91a2b8;
    font-size:14px;
}

.hero-price {
    font-size:32px;
    font-weight:800;
    margin-top:12px;
}

.section {
    margin-top:22px;
    margin-bottom:10px;
    font-size:20px;
    font-weight:800;
}

.card {
    background:#0e1a2a;
    border:1px solid #23364d;
    border-radius:15px;
    padding:17px;
    margin-bottom:12px;
}

.card-title {
    font-size:17px;
    font-weight:750;
    margin-bottom:8px;
}

.muted {
    color:#8fa1b6;
    font-size:13px;
}

.metric {
    background:#101e30;
    border:1px solid #22354c;
    border-radius:12px;
    padding:13px;
    text-align:center;
}

.metric-label {
    color:#8497ad;
    font-size:12px;
}

.metric-value {
    font-size:20px;
    font-weight:800;
    margin-top:4px;
}

.good {
    color:#4ee29a;
}

.warn {
    color:#ffc857;
}

.bad {
    color:#ff7373;
}

.blue {
    color:#66a7ff;
}

.theme-card {
    background:linear-gradient(
        145deg,
        #102139,
        #0c1726
    );
    border:1px solid #29415e;
    border-radius:16px;
    padding:18px;
    margin-bottom:14px;
}

.theme-name {
    font-size:20px;
    font-weight:800;
}

.theme-score {
    font-size:26px;
    font-weight:850;
}

.badge {
    display:inline-block;
    padding:5px 9px;
    border-radius:20px;
    background:#172b44;
    border:1px solid #304b6b;
    color:#9ec4ff;
    font-size:12px;
    margin-right:5px;
}

.evidence {
    background:#0b1624;
    border-left:3px solid #4d91ff;
    border-radius:8px;
    padding:12px 14px;
    margin-top:10px;
    color:#bac8d8;
    font-size:13px;
    line-height:1.6;
}

.judgment {
    background:#111f31;
    border:1px solid #2a425e;
    border-radius:14px;
    padding:17px;
    margin:12px 0;
}

.judgment-title {
    font-size:20px;
    font-weight:800;
}

.action {
    background:#13253a;
    border:1px solid #355473;
    border-radius:12px;
    padding:14px;
    margin-top:12px;
    font-size:15px;
    font-weight:650;
    line-height:1.6;
}

.scenario {
    background:#0e1a2a;
    border:1px solid #25394f;
    border-radius:13px;
    padding:15px;
    min-height:135px;
}

.scenario-title {
    font-weight:800;
    font-size:15px;
}

.scenario-price {
    font-size:21px;
    font-weight:800;
    margin:7px 0;
}

.radar-card {
    background:#0e1a2a;
    border:1px solid #263b53;
    border-radius:15px;
    padding:17px;
    margin-bottom:12px;
}

.radar-score {
    font-size:26px;
    font-weight:850;
}

.price-zone {
    background:#0c1725;
    border:1px solid #24394f;
    border-radius:14px;
    padding:15px;
}

.zone-label {
    color:#8498ae;
    font-size:12px;
}

.zone-price {
    font-size:20px;
    font-weight:800;
}

.decision-box {
    background:linear-gradient(
        135deg,
        #13283f,
        #0d1b2d
    );
    border:1px solid #315373;
    border-radius:16px;
    padding:19px;
    margin:15px 0;
}

.decision-title {
    font-size:22px;
    font-weight:850;
}

.small-table {
    font-size:13px;
}

div[data-testid="stRadio"] > div {
    gap:5px;
}

div[data-testid="stRadio"] label {
    background:#101d2e;
    border:1px solid #25394f;
    padding:7px 13px;
    border-radius:9px;
}

@media(max-width:700px) {

    .block-container {
        padding:0.65rem 0.65rem 2rem 0.65rem;
    }

    .hero {
        padding:17px;
    }

    .hero-title {
        font-size:23px;
    }

    .hero-price {
        font-size:27px;
    }

    .section {
        font-size:18px;
    }

    .theme-card,
    .radar-card,
    .card {
        padding:14px;
    }

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# FILES / DEFAULTS
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

BASE_ETFS = {}


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_float(v, default=np.nan):
    try:
        if v is None:
            return default
        return float(v)
    except:
        return default


def fmt_price(v):
    if pd.isna(v):
        return "-"
    return f"{v:,.0f}"


def fmt_pct(v):
    if pd.isna(v):
        return "-"
    return f"{v:+.1f}%"


def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return default


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass


def clean_text(text):
    if text is None:
        return ""

    text = str(text)

    if text.startswith("{") and "name" in text:
        try:
            obj = ast.literal_eval(text)
            if isinstance(obj, dict):
                for k in ["name", "itemname", "ETF_NM", "etfName"]:
                    if k in obj:
                        return str(obj[k])
        except:
            pass

    return html.unescape(text).strip()


def safe_etf_name(name, code):
    name = clean_text(name)

    if not name:
        return f"ETF {code}"

    bad = [
        "Ã", "Â", "ì", "ë", "í", "ê",
        "Ã©", "â", "ð"
    ]

    if any(x in name for x in bad):
        return f"ETF {code}"

    return name


# ============================================================
# STATE
# ============================================================

def init_state():

    if "watchlist" not in st.session_state:
        st.session_state.watchlist = load_json(
            WATCHLIST_FILE,
            DEFAULT_WATCHLIST.copy()
        )

    if "holdings" not in st.session_state:
        st.session_state.holdings = load_json(
            HOLDINGS_FILE,
            {}
        )

    if "etf_universe" not in st.session_state:
        st.session_state.etf_universe = {}

    if "price_cache" not in st.session_state:
        st.session_state.price_cache = {}

    if "theme_cache" not in st.session_state:
        st.session_state.theme_cache = {}

    if "future_engine_cache" not in st.session_state:
        st.session_state.future_engine_cache = None

    if "future_detail_code" not in st.session_state:
        st.session_state.future_detail_code = None

    if "future_detail_theme" not in st.session_state:
        st.session_state.future_detail_theme = None

    if "selected_code" not in st.session_state:
        st.session_state.selected_code = None

    if "main_page" not in st.session_state:
        st.session_state.main_page = "📊 내 ETF"

    if "radar_cache" not in st.session_state:
        st.session_state.radar_cache = None


# ============================================================
# ETF MASTER
# ============================================================

def fetch_naver_etf_master():

    url = "https://finance.naver.com/api/sise/etfItemList.nhn"

    try:
        r = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        data = r.json()

        result = {}

        for item in data.get("result", {}).get("etfItemList", []):

            code = str(
                item.get("itemcode", "")
            ).zfill(6)

            name = safe_etf_name(
                item.get("itemname", ""),
                code
            )

            if code:
                result[code] = name

        return result

    except:
        return {}


def fetch_krx_etf_master():

    url = (
        "https://data-dbg.krx.co.kr/"
        "svc/apis/etp/etpList"
    )

    try:
        r = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        if r.status_code != 200:
            return {}

        data = r.json()

        result = {}

        rows = (
            data.get("OutBlock_1")
            or data.get("data")
            or []
        )

        for row in rows:

            code = str(
                row.get("ISU_SRT_CD")
                or row.get("isuSrtCd")
                or ""
            ).zfill(6)

            name = (
                row.get("ISU_ABBRV")
                or row.get("isuAbbrv")
                or ""
            )

            if code and name:
                result[code] = safe_etf_name(
                    name,
                    code
                )

        return result

    except:
        return {}


@st.cache_data(ttl=1800)
def load_etf_universe():

    result = {}

    krx = fetch_krx_etf_master()
    naver = fetch_naver_etf_master()

    result.update(krx)
    result.update(naver)

    result.update(BASE_ETFS)

    return result


def refresh_universe():

    try:
        load_etf_universe.clear()
    except:
        pass

    st.session_state.etf_universe = load_etf_universe()


def get_etf_name(code):

    code = str(code).zfill(6)

    universe = st.session_state.get(
        "etf_universe",
        {}
    )

    if not universe:
        universe = load_etf_universe()
        st.session_state.etf_universe = universe

    return safe_etf_name(
        universe.get(code, f"ETF {code}"),
        code
    )


# ============================================================
# THEME LEXICON
# ============================================================

THEME_LEXICON = {

    "AI 반도체": [
        "AI반도체",
        "AI 반도체",
        "반도체",
        "HBM",
        "고대역폭",
        "AI",
        "반도체TOP"
    ],

    "반도체 장비·소부장": [
        "반도체장비",
        "반도체 장비",
        "소부장",
        "반도체소부장",
        "반도체",
        "장비"
    ],

    "로봇": [
        "로봇",
        "로보틱스",
        "휴머노이드",
        "AI로봇"
    ],

    "방산": [
        "방산",
        "국방",
        "K방산",
        "우주방산"
    ],

    "2차전지": [
        "2차전지",
        "이차전지",
        "배터리",
        "전지"
    ],

    "전기차": [
        "전기차",
        "EV",
        "전기자동차"
    ],

    "조선": [
        "조선",
        "K조선",
        "조선업"
    ],

    "원자력": [
        "원자력",
        "원전",
        "SMR"
    ],

    "전력 인프라": [
        "전력",
        "전력인프라",
        "전기설비",
        "전력설비",
        "전선",
        "전력기기"
    ],

    "데이터센터·AI 인프라": [
        "데이터센터",
        "AI인프라",
        "AI 인프라",
        "인프라"
    ],

    "냉각·열관리": [
        "냉각",
        "열관리",
        "액침냉각",
        "데이터센터냉각"
    ],

    "바이오": [
        "바이오",
        "헬스케어",
        "제약",
        "의료"
    ],

    "우주항공": [
        "우주",
        "항공우주",
        "우주항공"
    ],

    "AI 소프트웨어": [
        "AI소프트웨어",
        "AI 소프트웨어",
        "인공지능",
        "AI"
    ],

    "클라우드": [
        "클라우드",
        "Cloud"
    ],

    "보안": [
        "보안",
        "사이버보안",
        "정보보안"
    ],

    "5G·통신": [
        "5G",
        "통신",
        "네트워크"
    ],

    "신재생에너지": [
        "신재생",
        "태양광",
        "풍력",
        "재생에너지"
    ],

    "수소": [
        "수소",
        "Hydrogen"
    ],

    "친환경·탄소": [
        "친환경",
        "탄소",
        "ESG"
    ],

    "금융": [
        "금융",
        "은행",
        "증권",
        "보험"
    ],

    "자동차": [
        "자동차",
        "모빌리티",
        "차량"
    ],

    "화장품·K뷰티": [
        "화장품",
        "K뷰티",
        "뷰티"
    ],

    "음식료·소비": [
        "음식료",
        "소비",
        "식품"
    ],

    "건설·인프라": [
        "건설",
        "인프라",
        "SOC"
    ],

    "철강·금속": [
        "철강",
        "금속"
    ],

    "원자재": [
        "원자재",
        "원유",
        "원자재선물"
    ],

    "금·귀금속": [
        "금",
        "귀금속",
        "골드"
    ],

    "중국": [
        "중국",
        "차이나"
    ],

    "미국 기술": [
        "미국",
        "나스닥",
        "S&P",
        "테크"
    ],
}


THEME_REASONS = {

    "AI 반도체":
        "AI 연산 확대와 고성능 메모리·반도체 수요를 중심으로 연결되는 핵심 테마입니다.",

    "반도체 장비·소부장":
        "반도체 투자 확대가 장비·소재·부품으로 확산되는 후방 가치사슬입니다.",

    "로봇":
        "AI와 자동화가 결합되면서 산업용·서비스·휴머노이드 영역으로 적용 범위가 확대되고 있습니다.",

    "방산":
        "글로벌 국방비 확대와 수출 증가가 실적 및 수주 모멘텀으로 연결되는 구조입니다.",

    "2차전지":
        "전기차와 ESS를 중심으로 중장기 배터리 수요 변화가 이어지는 산업입니다.",

    "전력 인프라":
        "AI 데이터센터와 전력 수요 증가에 따라 발전·송배전·전력기기 투자가 연결되는 테마입니다.",

    "데이터센터·AI 인프라":
        "AI 연산 확대에 따라 서버·전력·냉각·네트워크 투자가 함께 증가하는 구조입니다.",

    "냉각·열관리":
        "고밀도 AI 서버 증가에 따라 데이터센터의 냉각 효율과 열관리 중요성이 높아지고 있습니다.",
}


def theme_reason(theme):

    return THEME_REASONS.get(
        theme,
        "관련 ETF의 가격 흐름과 거래량을 기반으로 시장 관심도가 확대되는지를 분석합니다."
    )


# ============================================================
# PRICE DATA
# ============================================================

def fetch_naver_history(code):

    url = (
        "https://fchart.stock.naver.com/"
        f"item/sise.nhn?code={code}"
        "&dayCount=1000"
        "&timeframe=day"
        "&requestType=0"
    )

    try:

        r = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        root = ET.fromstring(r.text)

        rows = []

        for item in root.findall(".//item"):

            data = item.attrib.get(
                "data",
                ""
            ).split("|")

            if len(data) >= 6:

                rows.append({
                    "Date": data[0],
                    "Open": safe_float(data[1]),
                    "High": safe_float(data[2]),
                    "Low": safe_float(data[3]),
                    "Close": safe_float(data[4]),
                    "Volume": safe_float(data[5])
                })

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)

        df["Date"] = pd.to_datetime(
            df["Date"]
        )

        df = df.set_index("Date")

        return df.sort_index()

    except:
        return pd.DataFrame()


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

        if df is not None and not df.empty:

            if isinstance(df.columns, pd.MultiIndex):

                df.columns = [
                    c[0]
                    for c in df.columns
                ]

            cols = [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume"
            ]

            available = [
                c for c in cols
                if c in df.columns
            ]

            df = df[available].copy()

            return df.dropna(
                subset=["Close"]
            )

    except:
        pass

    return fetch_naver_history(code)


def load_price_data(code, force=False):

    code = str(code).zfill(6)

    cache = st.session_state.price_cache

    if not force and code in cache:

        item = cache[code]

        if (
            datetime.now()
            - item["time"]
        ).total_seconds() < 300:

            return item["data"]

    df = fetch_yahoo(code)

    if df is not None and not df.empty:

        df = df.copy()

        numeric_cols = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]

        for c in numeric_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(
                    df[c],
                    errors="coerce"
                )

        close = df["Close"]

        df["MA20"] = (
            close.rolling(20).mean()
        )

        df["MA60"] = (
            close.rolling(60).mean()
        )

        df["MA120"] = (
            close.rolling(120).mean()
        )

        delta = close.diff()

        gain = delta.clip(
            lower=0
        ).rolling(14).mean()

        loss = (
            -delta.clip(upper=0)
            .rolling(14)
            .mean()
        )

        rs = gain / loss.replace(
            0,
            np.nan
        )

        df["RSI14"] = (
            100
            - (
                100
                / (1 + rs)
            )
        )

        df["VOL20"] = (
            df["Volume"]
            .rolling(20)
            .mean()
        )

        df["VOL_RATIO"] = (
            df["Volume"]
            / df["VOL20"]
        )

        df["RET5"] = (
            close.pct_change(5)
            * 100
        )

        df["RET20"] = (
            close.pct_change(20)
            * 100
        )

        df["RET60"] = (
            close.pct_change(60)
            * 100
        )

        df["HIGH20"] = (
            df["High"]
            .rolling(20)
            .max()
        )

        df["LOW20"] = (
            df["Low"]
            .rolling(20)
            .min()
        )

        df["HIGH60"] = (
            df["High"]
            .rolling(60)
            .max()
        )

        df["LOW60"] = (
            df["Low"]
            .rolling(60)
            .min()
        )

        cache[code] = {
            "time": datetime.now(),
            "data": df
        }

    return df


# ============================================================
# TECHNICAL JUDGMENT
# ============================================================

def get_judgment(d):

    price = safe_float(d.get("Close"))
    ma20 = safe_float(d.get("MA20"))
    ma60 = safe_float(d.get("MA60"))
    rsi = safe_float(d.get("RSI14"))
    vol = safe_float(d.get("VOL_RATIO"))
    ret20 = safe_float(d.get("RET20"))

    if any(pd.isna(x) for x in [
        price, ma20, ma60
    ]):

        return {
            "title": "분석 데이터 부족",
            "reason": "충분한 가격 데이터가 필요합니다.",
            "action": "추가 데이터 확보 후 판단합니다.",
            "ma_state": "-",
            "rsi_state": "-",
            "volume_state": "-",
            "rsi": rsi,
            "volume_ratio": vol,
            "ret20": ret20
        }

    if price > ma20 > ma60:

        if rsi >= 72:

            title = "상승 추세 · 추격 주의"

            reason = (
                "주가가 20일선과 60일선 위에 있어 "
                "중기 추세는 유지되고 있으나 RSI가 높아 "
                "단기 추격은 주의할 구간입니다."
            )

            action = (
                "신규 접근은 추격보다 20일선 부근의 "
                "눌림과 거래량 안정 여부를 확인합니다."
            )

        else:

            title = "상승 추세 유지"

            reason = (
                "주가가 20일선과 60일선 위에 있고 "
                "중기 추세가 상승 방향을 유지하고 있습니다."
            )

            action = (
                "보유자는 추세를 따라가되, "
                "신규 접근은 20일선 눌림 또는 거래량을 동반한 돌파를 확인합니다."
            )

        ma_state = "상승"

    elif price < ma20 and price > ma60:

        title = "단기 조정 · 중기 추세 확인"

        reason = (
            "단기적으로 20일선을 하회했지만 "
            "60일선 위에 있어 중기 추세가 완전히 훼손된 상태는 아닙니다."
        )

        action = (
            "20일선 회복 여부 또는 60일선 지지 여부를 확인합니다."
        )

        ma_state = "조정"

    elif price < ma20 and price < ma60:

        title = "중기 약세 · 방어 우선"

        reason = (
            "주가가 20일선과 60일선을 모두 하회하여 "
            "단기와 중기 추세가 모두 약해진 상태입니다."
        )

        action = (
            "신규 진입은 서두르지 않고 추세 회복을 확인합니다."
        )

        ma_state = "약세"

    else:

        title = "방향 확인 구간"

        reason = (
            "주요 이동평균선의 방향이 뚜렷하지 않아 "
            "추세 확인이 필요한 구간입니다."
        )

        action = (
            "가격과 거래량이 동시에 개선되는지를 확인합니다."
        )

        ma_state = "혼조"

    if pd.isna(rsi):
        rsi_state = "-"
    elif rsi >= 70:
        rsi_state = "과열"
    elif rsi >= 55:
        rsi_state = "강세"
    elif rsi >= 45:
        rsi_state = "중립"
    else:
        rsi_state = "약세"

    if pd.isna(vol):
        volume_state = "-"
    elif vol >= 1.8:
        volume_state = "강한 증가"
    elif vol >= 1.2:
        volume_state = "증가"
    elif vol <= 0.7:
        volume_state = "감소"
    else:
        volume_state = "보통"

    return {
        "title": title,
        "reason": reason,
        "action": action,
        "ma_state": ma_state,
        "rsi_state": rsi_state,
        "volume_state": volume_state,
        "rsi": rsi,
        "volume_ratio": vol,
        "ret20": ret20
    }


# ============================================================
# PRICE ZONES
# ============================================================

def calculate_levels(d):

    ma20 = safe_float(d.get("MA20"))
    ma60 = safe_float(d.get("MA60"))
    low20 = safe_float(d.get("LOW20"))
    low60 = safe_float(d.get("LOW60"))
    high20 = safe_float(d.get("HIGH20"))

    support_candidates = [
        x for x in [
            ma60,
            low20
        ]
        if not pd.isna(x)
    ]

    risk_candidates = [
        x for x in [
            ma60,
            low20,
            low60
        ]
        if not pd.isna(x)
    ]

    return {
        "first": ma20,
        "support": (
            min(support_candidates)
            if support_candidates
            else np.nan
        ),
        "breakout": high20,
        "risk": (
            min(risk_candidates)
            if risk_candidates
            else np.nan
        )
    }


def current_zone(price, levels):

    if pd.isna(price):
        return "분석불가"

    first = levels["first"]
    support = levels["support"]
    breakout = levels["breakout"]
    risk = levels["risk"]

    if (
        not pd.isna(breakout)
        and price >= breakout * 0.995
    ):
        return "돌파 확인 구간"

    if (
        not pd.isna(first)
        and price >= first
        and price <= first * 1.025
    ):
        return "20일선 관심 구간"

    if (
        not pd.isna(support)
        and price >= support
        and price <= support * 1.025
    ):
        return "핵심 지지 관심 구간"

    if (
        not pd.isna(first)
        and price > first * 1.025
    ):
        return "추세 추종 구간"

    if (
        not pd.isna(risk)
        and price < risk
    ):
        return "지지 이탈 구간"

    return "중간 구간"


def response_for_zone(
    price,
    levels,
    judgment,
    radar_score=None,
    overheat=None
):

    zone = current_zone(
        price,
        levels
    )

    title = judgment["title"]

    if zone == "돌파 확인 구간":

        if overheat is not None and overheat >= 45:
            return (
                "돌파 흐름은 강하지만 단기 과열 여부를 확인합니다. "
                "추격보다는 돌파 유지와 거래량 지속 여부를 확인합니다."
            )

        return (
            "20일 고점을 거래량과 함께 넘어서는지 확인합니다. "
            "돌파가 유지되면 추세 추종이 가능하고 "
            "재차 이탈하면 추격을 보류합니다."
        )

    if zone == "20일선 관심 구간":

        return (
            "현재가가 20일선 부근입니다. "
            "20일선 지지와 거래량 안정이 확인되면 "
            "분할 접근을 검토할 수 있는 구간입니다."
        )

    if zone == "핵심 지지 관심 구간":

        return (
            "중요 지지 가격대에 접근했습니다. "
            "지지 확인 없이 한 번에 진입하기보다 "
            "반등과 거래량을 확인하는 것이 핵심입니다."
        )

    if zone == "지지 이탈 구간":

        return (
            "중요 지지 가격을 하회했습니다. "
            "신규 접근보다 추세 회복 여부를 먼저 확인합니다."
        )

    if title == "상승 추세 · 추격 주의":

        return (
            "추세는 양호하지만 현재 위치가 높습니다. "
            "가격을 추격하기보다 20일선 눌림을 기다리는 전략이 유리합니다."
        )

    if title == "상승 추세 유지":

        return (
            "상승 추세는 유지되고 있습니다. "
            "20일선 눌림 또는 거래량을 동반한 신고가 여부를 확인합니다."
        )

    return (
        "현재는 명확한 가격 우위 구간이 아닙니다. "
        "추세와 주요 지지선의 회복 여부를 확인합니다."
    )


# ============================================================
# THEME MATCH
# ============================================================

def theme_match(name, theme):

    name_lower = str(name).lower()

    return any(
        str(k).lower() in name_lower
        for k in THEME_LEXICON.get(
            theme,
            []
        )
    )


def matched_themes(name):

    result = []

    for theme in THEME_LEXICON:

        if theme_match(
            name,
            theme
        ):
            result.append(theme)

    return result


def theme_stage(score):

    if score >= 78:
        return "현재 주도"

    if score >= 64:
        return "다음 수혜"

    if score >= 50:
        return "관심 확대"

    return "초기 관심"


# ============================================================
# BENCHMARK
# ============================================================

def benchmark_snapshot():

    df = load_price_data(
        "069500"
    )

    if df is None or df.empty:
        return {}

    d = df.iloc[-1]

    return {
        "price": safe_float(
            d["Close"]
        ),
        "ret5": safe_float(
            d["RET5"]
        ),
        "ret20": safe_float(
            d["RET20"]
        ),
        "ret60": safe_float(
            d["RET60"]
        )
    }


# ============================================================
# THEME ENGINE
# ============================================================

def score_theme(rows, benchmark):

    if not rows:
        return 0

    df = pd.DataFrame(rows)

    def avg(col):
        if col not in df:
            return 0
        return safe_float(
            df[col].mean(),
            0
        )

    ret20 = avg("RET20")
    ret60 = avg("RET60")
    rel20 = avg("REL20")
    rel60 = avg("REL60")
    volume = avg("VOL_RATIO")
    breadth = avg("ABOVE20")
    ma60 = avg("MA60_GAP")
    accel = avg("ACCEL")
    rsi = avg("RSI")

    s = 0

    s += np.clip(
        ret20 * 0.7,
        -5,
        15
    )

    s += np.clip(
        ret60 * 0.35,
        -5,
        15
    )

    s += np.clip(
        rel20 * 0.8,
        -5,
        15
    )

    s += np.clip(
        rel60 * 0.4,
        -5,
        10
    )

    s += np.clip(
        (volume - 1) * 15,
        -5,
        15
    )

    s += np.clip(
        breadth * 15,
        0,
        15
    )

    s += np.clip(
        ma60 * 0.1,
        -3,
        5
    )

    s += np.clip(
        accel * 0.5,
        -3,
        5
    )

    if 50 <= rsi <= 70:
        s += 5
    elif rsi > 75:
        s -= 3

    return round(
        float(np.clip(s + 40, 0, 100)),
        1
    )


def build_future_theme_engine(
    force=False
):

    cache = st.session_state.get(
        "future_engine_cache"
    )

    if (
        not force
        and cache is not None
    ):
        return cache

    universe = st.session_state.etf_universe

    benchmark = benchmark_snapshot()

    theme_rows = {}

    for theme in THEME_LEXICON:

        matches = [
            (code, name)
            for code, name
            in universe.items()
            if theme_match(
                name,
                theme
            )
        ]

        if len(matches) < 2:
            continue

        rows = []

        for code, name in matches[:8]:

            df = load_price_data(code)

            if (
                df is None
                or len(df) < 65
            ):
                continue

            d = df.iloc[-1]

            ret20 = safe_float(
                d.get("RET20")
            )

            ret60 = safe_float(
                d.get("RET60")
            )

            if pd.isna(ret20):
                continue

            bench20 = benchmark.get(
                "ret20",
                0
            )

            bench60 = benchmark.get(
                "ret60",
                0
            )

            ma60 = safe_float(
                d.get("MA60")
            )

            close = safe_float(
                d.get("Close")
            )

            ma60_gap = (
                (close / ma60 - 1)
                * 100
                if (
                    not pd.isna(ma60)
                    and ma60 != 0
                )
                else 0
            )

            ret5 = safe_float(
                d.get("RET5"),
                0
            )

            rows.append({
                "code": code,
                "name": name,
                "RET20": ret20,
                "RET60": ret60,
                "REL20": ret20 - bench20,
                "REL60": ret60 - bench60,
                "VOL_RATIO": safe_float(
                    d.get("VOL_RATIO"),
                    1
                ),
                "ABOVE20": (
                    1
                    if close > safe_float(
                        d.get("MA20"),
                        close
                    )
                    else 0
                ),
                "MA60_GAP": ma60_gap,
                "ACCEL": ret5,
                "RSI": safe_float(
                    d.get("RSI14"),
                    50
                )
            })

        if len(rows) < 2:
            continue

        score = score_theme(
            rows,
            benchmark
        )

        if score < 42:
            continue

        top_rows = sorted(
            rows,
            key=lambda x: (
                x["RET20"]
                + x["REL20"]
            ),
            reverse=True
        )[:5]

        breadth = np.mean([
            r["ABOVE20"]
            for r in rows
        ])

        avg20 = np.mean([
            r["RET20"]
            for r in rows
        ])

        avg60 = np.mean([
            r["RET60"]
            for r in rows
        ])

        avg_rsi = np.mean([
            r["RSI"]
            for r in rows
        ])

        avg_vol = np.mean([
            r["VOL_RATIO"]
            for r in rows
        ])

        theme_rows[theme] = {
            "theme": theme,
            "score": score,
            "stage": theme_stage(score),
            "reason": theme_reason(theme),
            "rows": top_rows,
            "breadth": breadth,
            "avg20": avg20,
            "avg60": avg60,
            "avg_rsi": avg_rsi,
            "avg_vol": avg_vol,
        }

    result = sorted(
        theme_rows.values(),
        key=lambda x: x["score"],
        reverse=True
    )[:10]

    st.session_state.future_engine_cache = result

    return result


def get_future_chain():

    engine = build_future_theme_engine()

    return [
        (
            x["theme"],
            x["stage"]
        )
        for x in engine
    ]


def future_theme_info(theme):

    engine = build_future_theme_engine()

    for item in engine:

        if item["theme"] == theme:
            return item

    return None


def theme_candidates(theme):

    info = future_theme_info(theme)

    if not info:
        return []

    return info.get(
        "rows",
        []
    )


# ============================================================
# RADAR
# ============================================================

def radar_theme_for(code, name):

    matches = matched_themes(name)

    if not matches:
        return "기타"

    engine = build_future_theme_engine()

    available = {
        x["theme"]: x
        for x in engine
    }

    matches = [
        x for x in matches
        if x in available
    ]

    if not matches:
        return "기타"

    return max(
        matches,
        key=lambda x:
        available[x]["score"]
    )


def radar_stage_for(theme):

    info = future_theme_info(theme)

    if info:
        return info["stage"]

    return "일반"


def radar_score(row):

    score = 0

    if row["ABOVE20"]:
        score += 12

    if row["ABOVE60"]:
        score += 13

    score += np.clip(
        row["REL20"] * 0.8,
        -5,
        20
    )

    score += np.clip(
        (row["VOL_RATIO"] - 1)
        * 12,
        -5,
        15
    )

    score += np.clip(
        row["RET20"] * 0.45,
        -5,
        12
    )

    score += np.clip(
        row["RET5"] * 0.8,
        -4,
        8
    )

    rsi = row["RSI"]

    if 50 <= rsi <= 68:
        score += 12
    elif 68 < rsi <= 75:
        score += 8
    elif rsi < 40:
        score += 2

    dist = row["DIST_MA20"]

    score += np.clip(
        8 - abs(dist) * 1.2,
        0,
        8
    )

    return round(
        float(
            np.clip(
                score,
                0,
                100
            )
        ),
        1
    )


def radar_overheat_score(row):

    score = 0

    rsi = row["RSI"]

    if rsi >= 80:
        score += 30
    elif rsi >= 75:
        score += 22
    elif rsi >= 70:
        score += 15

    ret5 = row["RET5"]

    if ret5 >= 12:
        score += 30
    elif ret5 >= 8:
        score += 22
    elif ret5 >= 5:
        score += 12

    dist = row["DIST_MA20"]

    if dist >= 15:
        score += 25
    elif dist >= 10:
        score += 18
    elif dist >= 6:
        score += 10

    vol = row["VOL_RATIO"]

    if vol >= 2.5:
        score += 20
    elif vol >= 2:
        score += 15
    elif vol >= 1.5:
        score += 8

    return round(
        float(
            np.clip(
                score,
                0,
                100
            )
        ),
        1
    )


def radar_target_etfs():

    targets = {}

    holdings = st.session_state.get(
        "holdings",
        {}
    )

    if isinstance(
        holdings,
        dict
    ):

        for code in holdings.keys():

            code = str(code).zfill(6)

            targets[code] = get_etf_name(
                code
            )

    for theme, _stage in get_future_chain():

        for item in theme_candidates(theme):

            code = item["code"]
            name = item["name"]

            targets[code] = name

    return targets


def build_radar_data(
    force=False
):

    if (
        not force
        and st.session_state.radar_cache
        is not None
    ):
        return st.session_state.radar_cache

    targets = radar_target_etfs()

    benchmark = benchmark_snapshot()

    result = []

    for code, name in targets.items():

        df = load_price_data(code)

        if (
            df is None
            or df.empty
            or len(df) < 65
        ):
            continue

        d = df.iloc[-1]

        close = safe_float(
            d.get("Close")
        )

        ma20 = safe_float(
            d.get("MA20")
        )

        ma60 = safe_float(
            d.get("MA60")
        )

        if pd.isna(close):
            continue

        ret5 = safe_float(
            d.get("RET5"),
            0
        )

        ret20 = safe_float(
            d.get("RET20"),
            0
        )

        rel20 = (
            ret20
            - benchmark.get(
                "ret20",
                0
            )
        )

        dist_ma20 = (
            (close / ma20 - 1)
            * 100
            if (
                not pd.isna(ma20)
                and ma20 != 0
            )
            else 0
        )

        row = {
            "code": code,
            "name": name,
            "price": close,
            "RET5": ret5,
            "RET20": ret20,
            "REL20": rel20,
            "RSI": safe_float(
                d.get("RSI14"),
                50
            ),
            "VOL_RATIO": safe_float(
                d.get("VOL_RATIO"),
                1
            ),
            "DIST_MA20": dist_ma20,
            "ABOVE20": (
                1
                if (
                    not pd.isna(ma20)
                    and close > ma20
                )
                else 0
            ),
            "ABOVE60": (
                1
                if (
                    not pd.isna(ma60)
                    and close > ma60
                )
                else 0
            ),
            "theme":
                radar_theme_for(
                    code,
                    name
                ),
        }

        row["stage"] = radar_stage_for(
            row["theme"]
        )

        row["opportunity"] = radar_score(
            row
        )

        row["overheat"] = (
            radar_overheat_score(row)
        )

        row["held"] = (
            code
            in st.session_state.holdings
        )

        result.append(row)

    df = pd.DataFrame(result)

    if not df.empty:
        df = df.sort_values(
            "opportunity",
            ascending=False
        )

    st.session_state.radar_cache = df

    return df


# ============================================================
# UNIFIED INVESTMENT SIGNAL
# ============================================================

def build_investment_signal(
    code,
    theme=None
):

    code = str(code).zfill(6)

    name = get_etf_name(code)

    df = load_price_data(code)

    if (
        df is None
        or df.empty
    ):
        return None

    d = df.iloc[-1]

    judgment = get_judgment(d)

    levels = calculate_levels(d)

    price = safe_float(
        d.get("Close")
    )

    radar_df = build_radar_data()

    radar_row = None

    if (
        radar_df is not None
        and not radar_df.empty
    ):

        match = radar_df[
            radar_df["code"] == code
        ]

        if not match.empty:
            radar_row = match.iloc[0]

    if radar_row is not None:

        opportunity = safe_float(
            radar_row["opportunity"],
            0
        )

        overheat = safe_float(
            radar_row["overheat"],
            0
        )

        if theme is None:
            theme = radar_row["theme"]

    else:

        opportunity = 0
        overheat = 0

    if theme:
        theme_info = future_theme_info(
            theme
        )
    else:
        theme_info = None

    theme_score = (
        safe_float(
            theme_info["score"],
            0
        )
        if theme_info
        else 0
    )

    stage = (
        theme_info["stage"]
        if theme_info
        else "일반"
    )

    zone = current_zone(
        price,
        levels
    )

    response = response_for_zone(
        price,
        levels,
        judgment,
        opportunity,
        overheat
    )

    # --------------------------------------------------------
    # 종합 상태
    # --------------------------------------------------------

    if (
        theme_score >= 64
        and opportunity >= 65
        and judgment["ma_state"] == "상승"
        and overheat < 45
    ):
        overall = "관심 확대"

    elif (
        theme_score >= 50
        and opportunity >= 55
        and judgment["ma_state"] in [
            "상승",
            "조정"
        ]
    ):
        overall = "관찰 우선"

    elif overheat >= 45:
        overall = "추격 주의"

    elif judgment["ma_state"] == "약세":
        overall = "추세 확인"

    else:
        overall = "대기"

    # --------------------------------------------------------
    # 통합 대응 문구
    # --------------------------------------------------------

    if overall == "관심 확대":

        final_action = (
            f"테마와 ETF 흐름이 동시에 양호합니다. "
            f"다만 현재 가격이 {zone}인지 확인한 뒤 "
            f"20일선 눌림 또는 거래량을 동반한 돌파를 기준으로 "
            f"분할 접근을 검토합니다."
        )

    elif overall == "관찰 우선":

        final_action = (
            f"테마 흐름은 살아 있지만 아직 확정 신호는 아닙니다. "
            f"{zone}에서 지지와 거래량을 확인하면서 접근 시점을 기다립니다."
        )

    elif overall == "추격 주의":

        final_action = (
            "테마와 추세가 강하더라도 단기 과열 신호가 있습니다. "
            "현재 가격을 추격하기보다 20일선 눌림 또는 "
            "돌파 후 재지지 여부를 확인합니다."
        )

    elif overall == "추세 확인":

        final_action = (
            "현재는 가격 추세가 약합니다. "
            "주요 지지선 회복과 거래량 개선을 확인한 후 "
            "다시 판단합니다."
        )

    else:

        final_action = response

    return {
        "code": code,
        "name": name,
        "theme": theme,
        "theme_score": theme_score,
        "stage": stage,
        "opportunity": opportunity,
        "overheat": overheat,
        "judgment": judgment,
        "levels": levels,
        "price": price,
        "zone": zone,
        "overall": overall,
        "response": response,
        "final_action": final_action,
        "data": d
    }


# ============================================================
# CHART
# ============================================================

def render_chart(df, title=""):

    chart_df = df.tail(126).copy()

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[
            0.72,
            0.28
        ]
    )

    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name="가격"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA20"],
            name="MA20",
            line=dict(width=1.5)
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA60"],
            name="MA60",
            line=dict(width=1.5)
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=chart_df.index,
            y=chart_df["Volume"],
            name="거래량",
            opacity=0.55
        ),
        row=2,
        col=1
    )

    fig.update_layout(
        title=title,
        height=570,
        paper_bgcolor="#08111f",
        plot_bgcolor="#08111f",
        font=dict(
            color="#dbe5f0"
        ),
        margin=dict(
            l=10,
            r=10,
            t=45,
            b=10
        ),
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            y=1.02
        )
    )

    fig.update_xaxes(
        gridcolor="#1c2c3e"
    )

    fig.update_yaxes(
        gridcolor="#1c2c3e"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# ============================================================
# PRICE SCENARIOS
# ============================================================

def render_scenarios(
    d,
    signal=None
):

    levels = calculate_levels(d)

    first = levels["first"]
    support = levels["support"]
    breakout = levels["breakout"]
    risk = levels["risk"]

    price = safe_float(
        d.get("Close")
    )

    st.markdown(
        '<div class="section">가격구간</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(4)

    scenarios = [
        (
            "1차 관심",
            first,
            "20일선",
        ),
        (
            "핵심 지지",
            support,
            "중기 지지",
        ),
        (
            "돌파 기준",
            breakout,
            "20일 고점",
        ),
        (
            "위험 가격",
            risk,
            "지지 이탈",
        )
    ]

    for col, item in zip(
        cols,
        scenarios
    ):

        label, value, sub = item

        with col:

            st.markdown(
                f"""
                <div class="scenario">
                    <div class="scenario-title">
                        {label}
                    </div>
                    <div class="scenario-price">
                        {fmt_price(value)}
                    </div>
                    <div class="muted">
                        {sub}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    zone = current_zone(
        price,
        levels
    )

    st.markdown(
        f"""
        <div class="action">
            현재 위치: <b>{zone}</b><br>
            현재가 {fmt_price(price)} ·
            20일선 {fmt_price(first)} ·
            핵심지지 {fmt_price(support)} ·
            돌파 {fmt_price(breakout)}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# JUDGMENT PANEL
# ============================================================

def render_judgment(
    signal
):

    j = signal["judgment"]

    st.markdown(
        '<div class="section">현재 판단</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="judgment">

            <div class="judgment-title">
                {j["title"]}
            </div>

            <div class="evidence">
                {j["reason"]}
            </div>

            <div class="action">
                {j["action"]}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    cols = st.columns(4)

    metrics = [
        (
            "RSI",
            (
                f"{j['rsi']:.1f}"
                if not pd.isna(j["rsi"])
                else "-"
            )
        ),
        (
            "거래량",
            (
                f"{j['volume_ratio']:.2f}x"
                if not pd.isna(
                    j["volume_ratio"]
                )
                else "-"
            )
        ),
        (
            "20일 수익률",
            fmt_pct(j["ret20"])
        ),
        (
            "추세",
            j["ma_state"]
        )
    ]

    for col, (label, value) in zip(
        cols,
        metrics
    ):

        with col:

            st.markdown(
                f"""
                <div class="metric">
                    <div class="metric-label">
                        {label}
                    </div>
                    <div class="metric-value">
                        {value}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# UNIFIED DECISION PANEL
# ============================================================

def render_unified_decision(
    signal
):

    st.markdown(
        '<div class="section">종합판단</div>',
        unsafe_allow_html=True
    )

    theme = signal["theme"] or "일반"

    st.markdown(
        f"""
        <div class="decision-box">

            <div class="decision-title">
                {signal["overall"]}
            </div>

            <div style="margin-top:8px;">
                <span class="badge">
                    테마 · {theme}
                </span>

                <span class="badge">
                    {signal["stage"]}
                </span>

                <span class="badge">
                    테마 {signal["theme_score"]:.0f}
                </span>

                <span class="badge">
                    레이더 {signal["opportunity"]:.0f}
                </span>

                <span class="badge">
                    과열 {signal["overheat"]:.0f}
                </span>
            </div>

            <div class="evidence">
                <b>현재 위치</b><br>
                {signal["zone"]}
                <br><br>

                <b>대응</b><br>
                {signal["final_action"]}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# HOLDINGS
# ============================================================

def render_holdings(
    code
):

    holdings = st.session_state.holdings

    item = holdings.get(
        code
    )

    if item is None:
        return

    qty = safe_float(
        item.get("qty"),
        0
    )

    avg = safe_float(
        item.get("avg"),
        0
    )

    df = load_price_data(code)

    if (
        df is None
        or df.empty
    ):
        return

    price = safe_float(
        df.iloc[-1]["Close"]
    )

    if avg <= 0:
        return

    pnl = (
        price / avg - 1
    ) * 100

    value = price * qty

    st.markdown(
        '<div class="section">보유 현황</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="metric">
                <div class="metric-label">
                    보유수량
                </div>
                <div class="metric-value">
                    {qty:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric">
                <div class="metric-label">
                    평균매수가
                </div>
                <div class="metric-value">
                    {fmt_price(avg)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        cls = (
            "good"
            if pnl >= 0
            else "bad"
        )

        st.markdown(
            f"""
            <div class="metric">
                <div class="metric-label">
                    평가손익률
                </div>
                <div class="metric-value {cls}">
                    {pnl:+.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# ETF FINDER
# ============================================================

def search_etfs(query):

    query = str(
        query or ""
    ).strip().lower()

    if not query:
        return []

    universe = (
        st.session_state.etf_universe
    )

    result = []

    for code, name in universe.items():

        if (
            query in code.lower()
            or query in name.lower()
        ):

            result.append(
                (code, name)
            )

        if len(result) >= 30:
            break

    return result


def render_finder():

    st.markdown(
        '<div class="section">ETF 찾기</div>',
        unsafe_allow_html=True
    )

    query = st.text_input(
        "ETF명 또는 종목코드",
        placeholder="예: 반도체 / 069500",
        label_visibility="collapsed"
    )

    if query:

        results = search_etfs(
            query
        )

        if not results:

            st.info(
                "검색 결과가 없습니다."
            )

        for code, name in results:

            c1, c2 = st.columns(
                [5, 1]
            )

            with c1:

                st.markdown(
                    f"""
                    <div class="card">
                        <b>{name}</b>
                        <div class="muted">
                            {code}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with c2:

                if st.button(
                    "추가",
                    key=f"add_{code}"
                ):

                    if code not in st.session_state.watchlist:

                        st.session_state.watchlist.append(
                            code
                        )

                        save_json(
                            WATCHLIST_FILE,
                            st.session_state.watchlist
                        )

                        st.rerun()


# ============================================================
# WATCHLIST
# ============================================================

def render_watchlist():

    st.markdown(
        '<div class="section">관심 ETF</div>',
        unsafe_allow_html=True
    )

    watchlist = (
        st.session_state.watchlist
    )

    if not watchlist:

        st.info(
            "관심 ETF가 없습니다."
        )

        return

    for code in watchlist:

        name = get_etf_name(
            code
        )

        df = load_price_data(
            code
        )

        if (
            df is None
            or df.empty
        ):
            continue

        d = df.iloc[-1]

        price = safe_float(
            d.get("Close")
        )

        ret5 = safe_float(
            d.get("RET5")
        )

        c1, c2, c3 = st.columns(
            [4, 2, 1]
        )

        with c1:

            st.markdown(
                f"""
                <div class="card">
                    <b>{name}</b>
                    <div class="muted">
                        {code}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:

            st.markdown(
                f"""
                <div style="padding:15px 0;">
                    <b>{fmt_price(price)}</b><br>
                    <span class="muted">
                        5일 {fmt_pct(ret5)}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c3:

            if st.button(
                "분석",
                key=f"watch_{code}"
            ):

                st.session_state.selected_code = code
                st.rerun()


# ============================================================
# MY ETF
# ============================================================

def render_my_etf():

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">
                📊 내 ETF
            </div>
            <div class="hero-sub">
                보유 ETF와 관심 ETF의 추세·가격구간·대응을 한눈에 확인합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    render_finder()

    code = st.session_state.get(
        "selected_code"
    )

    if code is None:

        if st.session_state.watchlist:
            code = st.session_state.watchlist[0]

    if code:

        signal = build_investment_signal(
            code
        )

        if signal:

            st.markdown(
                f"""
                <div class="hero">
                    <div class="hero-title">
                        {signal["name"]}
                    </div>
                    <div class="hero-sub">
                        {signal["code"]}
                    </div>
                    <div class="hero-price">
                        {fmt_price(signal["price"])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            render_unified_decision(
                signal
            )

            render_judgment(
                signal
            )

            render_scenarios(
                signal["data"],
                signal
            )

            render_holdings(
                code
            )

            render_chart(
                load_price_data(code),
                signal["name"]
            )

    render_watchlist()


# ============================================================
# FUTURE THEME
# ============================================================

def render_future_inline_analysis(
    code,
    theme=None
):

    signal = build_investment_signal(
        code,
        theme
    )

    if not signal:
        st.warning(
            "가격 데이터를 가져오지 못했습니다."
        )
        return

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">
                {signal["name"]}
            </div>
            <div class="hero-sub">
                {signal["code"]} · {theme or signal["theme"] or "ETF"}
            </div>
            <div class="hero-price">
                {fmt_price(signal["price"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    render_unified_decision(
        signal
    )

    render_judgment(
        signal
    )

    render_scenarios(
        signal["data"],
        signal
    )

    render_chart(
        load_price_data(code),
        signal["name"]
    )


def render_future_theme():

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">
                🚀 미래테마
            </div>
            <div class="hero-sub">
                시장 흐름을 분석해 관심이 확대되는 테마와 ETF를 찾습니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(
        [1, 5]
    )

    with c1:

        if st.button(
            "🔄 테마 업데이트"
        ):

            st.session_state.future_engine_cache = None
            st.session_state.radar_cache = None

            st.session_state.price_cache = {}

            st.rerun()

    engine = build_future_theme_engine()

    if not engine:

        st.warning(
            "현재 분석 가능한 테마 데이터가 없습니다."
        )

        return

    st.markdown(
        '<div class="section">테마 흐름</div>',
        unsafe_allow_html=True
    )

    for item in engine:

        theme = item["theme"]
        score = item["score"]
        stage = item["stage"]

        st.markdown(
            f"""
            <div class="theme-card">

                <div class="theme-name">
                    {theme}
                </div>

                <div style="margin-top:6px;">
                    <span class="badge">
                        {stage}
                    </span>

                    <span class="badge">
                        테마점수 {score:.0f}
                    </span>
                </div>

                <div style="margin-top:12px;">
                    {item["reason"]}
                </div>

                <div class="evidence">
                    평균 20일 수익률
                    <b>{item["avg20"]:+.1f}%</b>
                    ·
                    평균 60일 수익률
                    <b>{item["avg60"]:+.1f}%</b>
                    ·
                    20일선 위 ETF
                    <b>{item["breadth"]*100:.0f}%</b>
                    ·
                    평균 거래량
                    <b>{item["avg_vol"]:.2f}x</b>
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        rows = item["rows"]

        if rows:

            for row in rows:

                code = row["code"]
                name = row["name"]

                df = load_price_data(
                    code
                )

                if (
                    df is None
                    or df.empty
                ):
                    continue

                d = df.iloc[-1]

                price = safe_float(
                    d.get("Close")
                )

                rsi = safe_float(
                    d.get("RSI14")
                )

                vol = safe_float(
                    d.get("VOL_RATIO")
                )

                ret20 = safe_float(
                    d.get("RET20")
                )

                ret60 = safe_float(
                    d.get("RET60")
                )

                c1, c2, c3, c4, c5 = st.columns(
                    [4, 1.4, 1.4, 1.4, 1.3]
                )

                with c1:

                    st.markdown(
                        f"""
                        <div class="card">
                            <b>{name}</b>
                            <div class="muted">
                                {code}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with c2:

                    st.markdown(
                        f"""
                        <div class="metric">
                            <div class="metric-label">
                                현재가
                            </div>
                            <div class="metric-value">
                                {fmt_price(price)}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with c3:

                    st.markdown(
                        f"""
                        <div class="metric">
                            <div class="metric-label">
                                20일
                            </div>
                            <div class="metric-value">
                                {fmt_pct(ret20)}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with c4:

                    st.markdown(
                        f"""
                        <div class="metric">
                            <div class="metric-label">
                                RSI
                            </div>
                            <div class="metric-value">
                                {rsi:.1f}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with c5:

                    if st.button(
                        "ETF 분석",
                        key=f"future_{theme}_{code}"
                    ):

                        st.session_state.future_detail_code = code
                        st.session_state.future_detail_theme = theme
                        st.rerun()

                st.markdown(
                    f"""
                    <div class="muted"
                         style="margin:-4px 0 12px 4px;">
                        60일 {fmt_pct(ret60)}
                        · 거래량 {vol:.2f}x
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown(
            "<hr style='border-color:#1d3044;'>",
            unsafe_allow_html=True
        )

    detail_code = st.session_state.get(
        "future_detail_code"
    )

    detail_theme = st.session_state.get(
        "future_detail_theme"
    )

    if detail_code:

        st.markdown(
            '<div class="section">선택 ETF 종합분석</div>',
            unsafe_allow_html=True
        )

        if st.button(
            "← 테마 목록으로"
        ):

            st.session_state.future_detail_code = None
            st.session_state.future_detail_theme = None
            st.rerun()

        render_future_inline_analysis(
            detail_code,
            detail_theme
        )


# ============================================================
# RADAR CARD
# ============================================================

def render_radar_card(
    row
):

    score = row["opportunity"]
    overheat = row["overheat"]

    if score >= 75:
        score_cls = "good"
    elif score >= 55:
        score_cls = "warn"
    else:
        score_cls = "bad"

    st.markdown(
        f"""
        <div class="radar-card">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
            ">

                <div>
                    <div style="
                        font-size:18px;
                        font-weight:800;
                    ">
                        {row["name"]}
                    </div>

                    <div class="muted">
                        {row["code"]}
                    </div>
                </div>

                <div class="radar-score {score_cls}">
                    {score:.0f}
                </div>

            </div>

            <div style="margin-top:8px;">
                <span class="badge">
                    {row["theme"]}
                </span>

                <span class="badge">
                    {row["stage"]}
                </span>

                {
                    '<span class="badge">보유중</span>'
                    if row["held"]
                    else ""
                }
            </div>

            <div class="evidence">

                현재가 <b>{fmt_price(row["price"])}</b>
                · 5일 <b>{fmt_pct(row["RET5"])}</b>
                · 20일 <b>{fmt_pct(row["RET20"])}</b>
                · 상대강도 <b>{fmt_pct(row["REL20"])}</b>

                <br>

                RSI <b>{row["RSI"]:.1f}</b>
                · 거래량 <b>{row["VOL_RATIO"]:.2f}x</b>
                · 20일선 대비 <b>{row["DIST_MA20"]:+.1f}%</b>

                <br>

                과열점수 <b>{overheat:.0f}</b>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "상세 분석",
        key=f"radar_detail_{row['code']}"
    ):

        st.session_state.selected_code = (
            row["code"]
        )

        st.rerun()


# ============================================================
# MARKET RADAR
# ============================================================

def render_market_radar():

    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">
                🔥 시장 레이더
            </div>
            <div class="hero-sub">
                미래테마 ETF와 보유 ETF의 기회·과열·테마순환을 동시에 확인합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(
        [1, 5]
    )

    with c1:

        if st.button(
            "🔄 시장 새로고침"
        ):

            st.session_state.radar_cache = None
            st.session_state.price_cache = {}

            st.rerun()

    mode = st.radio(
        "레이더 모드",
        [
            "🎯 기회검색",
            "⚠️ 과열검색",
            "🔄 테마순환"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

    radar = build_radar_data()

    if radar is None or radar.empty:

        st.warning(
            "현재 레이더 데이터를 만들 수 없습니다."
        )

        return

    if mode == "🎯 기회검색":

        filtered = radar[
            (
                radar["opportunity"]
                >= 55
            )
            &
            (
                radar["RSI"]
                < 75
            )
            &
            (
                radar["RET5"]
                < 10
            )
        ].copy()

        filtered = filtered.sort_values(
            "opportunity",
            ascending=False
        )

        st.markdown(
            '<div class="section">현재 기회 후보</div>',
            unsafe_allow_html=True
        )

    elif mode == "⚠️ 과열검색":

        filtered = radar[
            radar["overheat"] >= 30
        ].copy()

        filtered = filtered.sort_values(
            "overheat",
            ascending=False
        )

        st.markdown(
            '<div class="section">과열 주의 후보</div>',
            unsafe_allow_html=True
        )

    else:

        grouped = (
            radar
            .groupby("theme")
            .agg(
                ETF수=("code", "count"),
                평균5일=("RET5", "mean"),
                평균20일=("RET20", "mean"),
                평균거래량=("VOL_RATIO", "mean"),
                평균기회=("opportunity", "mean")
            )
            .reset_index()
        )

        grouped = grouped.sort_values(
            "평균20일",
            ascending=False
        )

        st.markdown(
            '<div class="section">테마 순환</div>',
            unsafe_allow_html=True
        )

        for _, r in grouped.iterrows():

            st.markdown(
                f"""
                <div class="card">

                    <div class="card-title">
                        {r["theme"]}
                    </div>

                    <div class="evidence">
                        ETF {int(r["ETF수"])}개
                        · 5일 {r["평균5일"]:+.1f}%
                        · 20일 {r["평균20일"]:+.1f}%
                        · 거래량 {r["평균거래량"]:.2f}x
                        · 기회 {r["평균기회"]:.0f}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        return

    if filtered.empty:

        st.info(
            "현재 조건에 맞는 ETF가 없습니다."
        )

        return

    for _, row in filtered.iterrows():

        render_radar_card(
            row
        )


# ============================================================
# ETF DETAIL
# ============================================================

def render_selected_detail():

    code = st.session_state.get(
        "selected_code"
    )

    if not code:
        return

    signal = build_investment_signal(
        code
    )

    if not signal:
        return

    st.markdown(
        '<div class="section">ETF 종합분석</div>',
        unsafe_allow_html=True
    )

    render_unified_decision(
        signal
    )

    render_judgment(
        signal
    )

    render_scenarios(
        signal["data"],
        signal
    )

    render_holdings(
        code
    )

    render_chart(
        load_price_data(code),
        signal["name"]
    )


# ============================================================
# MAIN
# ============================================================

init_state()

if not st.session_state.etf_universe:

    st.session_state.etf_universe = (
        load_etf_universe()
    )

nav = st.radio(
    "메뉴",
    [
        "📊 내 ETF",
        "🚀 미래테마",
        "🔥 시장 레이더"
    ],
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