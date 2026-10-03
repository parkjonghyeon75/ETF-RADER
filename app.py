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
# Dynamic Future Theme Engine
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

CSS = r"""
<style>

.stApp {
    background: #07111d;
    color: #d9e4ef;
}

.block-container {
    max-width: 1280px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}

.hero {
    background: linear-gradient(135deg,#0e2236,#0a1727);
    border: 1px solid #1e3a53;
    border-radius: 18px;
    padding: 20px;
    margin: 12px 0 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,.18);
}

.hero-name {
    font-size: 1.25rem;
    font-weight: 800;
    color: #f1f7fc;
}

.hero-code {
    font-size: .72rem;
    color: #71869a;
    margin-top: 3px;
}

.quote-row {
    display:flex;
    align-items:baseline;
    gap:12px;
    margin-top:12px;
    flex-wrap:wrap;
}

.quote-price {
    font-size:2rem;
    font-weight:900;
    color:#ffffff;
}

.quote-change {
    font-size:.95rem;
    font-weight:800;
}

.hero-date {
    margin-top:7px;
    color:#71869a;
    font-size:.72rem;
}

.section-title {
    font-size:1.05rem;
    font-weight:850;
    margin:20px 0 10px;
    color:#eaf2f9;
}

.positive {
    color:#39c99a !important;
}

.negative {
    color:#ef6678 !important;
}

.neutral {
    color:#aab8c7 !important;
}

.evidence-grid {
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:9px;
    margin:10px 0 12px;
}

.evidence-box {
    background:#0c1b2b;
    border:1px solid #1a3249;
    border-radius:13px;
    padding:12px;
}

.evidence-label {
    font-size:.68rem;
    color:#71869a;
}

.evidence-value {
    font-size:1rem;
    font-weight:850;
    margin-top:5px;
}

.evidence-sub {
    font-size:.66rem;
    color:#657b8f;
    margin-top:3px;
}

.judgment-box,
.action-box {
    background:#0c1b2b;
    border:1px solid #1a3249;
    border-radius:14px;
    padding:15px;
    min-height:150px;
}

.action-box {
    background:#0c2023;
    border-color:#20534e;
}

.judgment-title,
.action-title {
    font-size:.72rem;
    color:#71869a;
    font-weight:800;
}

.judgment-main,
.action-main {
    font-size:1rem;
    font-weight:850;
    margin:8px 0;
    color:#f0f6fb;
}

.reason-label,
.action-reason-label {
    font-size:.68rem;
    color:#71869a;
    margin-top:10px;
}

.judgment-reason {
    font-size:.73rem;
    line-height:1.65;
    color:#aab8c7;
}

.theme-card {
    background:linear-gradient(135deg,#0d2032,#0b1725);
    border:1px solid #203d56;
    border-radius:16px;
    padding:16px;
    margin:10px 0 8px;
}

.theme-title {
    font-size:1.12rem;
    font-weight:900;
    color:#f2f7fb;
    margin-top:7px;
}

.theme-reason {
    font-size:.72rem;
    color:#8196aa;
    line-height:1.55;
    margin-top:5px;
}

.theme-outlook {
    margin-top:11px;
    padding-top:10px;
    border-top:1px solid #1b3449;
    font-size:.74rem;
    color:#b4c2ce;
    line-height:1.6;
}

.theme-stage-wrap {
    margin-bottom:3px;
}

.theme-stage-badge {
    display:inline-block;
    padding:4px 8px;
    border-radius:999px;
    font-size:.64rem;
    font-weight:850;
}

.stage-core {
    background:#173b39;
    color:#54d9b0;
}

.stage-next {
    background:#19364c;
    color:#67b6ef;
}

.stage-interest {
    background:#3b321b;
    color:#e1c45f;
}

.stage-early {
    background:#30283d;
    color:#b99ae8;
}

.theme-etf-box {
    background:#0b1928;
    border:1px solid #1a344b;
    border-radius:13px;
    padding:12px;
    min-height:150px;
}

.theme-etf-name {
    font-size:.76rem;
    font-weight:800;
    color:#e9f1f7;
    line-height:1.35;
}

.theme-etf-code {
    font-size:.62rem;
    color:#61778b;
    margin-top:2px;
}

.theme-data-grid {
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:6px;
    margin-top:10px;
}

.theme-data-item {
    background:#0e2234;
    border-radius:8px;
    padding:7px;
}

.theme-data-label {
    font-size:.58rem;
    color:#60778c;
}

.theme-data-value {
    font-size:.72rem;
    font-weight:800;
    color:#dbe7ef;
    margin-top:2px;
}

.theme-summary-card {
    background:#0c1b2b;
    border:1px solid #1b354c;
    border-radius:14px;
    padding:13px;
    margin:8px 0;
}

.theme-summary-title {
    font-weight:850;
    font-size:.92rem;
    margin-top:6px;
}

.theme-summary-meta {
    font-size:.7rem;
    color:#8799aa;
    margin-top:5px;
}

.theme-summary-outlook {
    font-size:.71rem;
    line-height:1.55;
    color:#b3c0cc;
    margin-top:7px;
}

.radar-card {
    background:#0b1a2a;
    border:1px solid #1c3951;
    border-radius:15px;
    padding:15px;
    margin:9px 0;
}

.radar-badge {
    display:inline-block;
    background:#17364b;
    color:#75bce9;
    border-radius:999px;
    padding:4px 8px;
    font-size:.63rem;
    font-weight:850;
}

.radar-title {
    margin-top:8px;
    font-size:.95rem;
    font-weight:850;
    color:#edf4f9;
}

.radar-sub {
    font-size:.68rem;
    color:#70869a;
    margin-top:3px;
}

.radar-grid {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:7px;
    margin-top:12px;
}

.radar-metric {
    background:#0e2234;
    border-radius:9px;
    padding:8px;
}

.radar-label {
    font-size:.58rem;
    color:#61798d;
}

.radar-value {
    font-size:.78rem;
    font-weight:850;
    margin-top:2px;
}

.holding-box {
    background:#0d211f;
    border:1px solid #1e5148;
    border-radius:13px;
    padding:12px;
    margin-bottom:12px;
}

.holding-value {
    font-size:.9rem;
    font-weight:850;
}

.holding-detail {
    font-size:.68rem;
    color:#8297a8;
    margin-top:4px;
}

.future-analysis {
    background:#0d2430;
    border:1px solid #23566a;
    border-radius:15px;
    padding:15px;
    margin:12px 0;
}

.future-analysis-title {
    font-size:.7rem;
    color:#72bdd7;
    font-weight:800;
}

.future-analysis-name {
    font-size:1.05rem;
    font-weight:900;
    margin-top:6px;
}

.future-analysis-code {
    font-size:.65rem;
    color:#71889a;
}

.theme-score-box {
    background:#101f30;
    border:1px solid #22425b;
    border-radius:13px;
    padding:11px;
    margin-top:10px;
}

.theme-score-number {
    font-size:1.45rem;
    font-weight:900;
}

.theme-score-label {
    font-size:.62rem;
    color:#70879b;
}

@media (max-width: 700px) {
    .block-container {
        padding-left:.55rem;
        padding-right:.55rem;
    }

    .evidence-grid {
        grid-template-columns:repeat(3,1fr);
    }

    .radar-grid {
        grid-template-columns:repeat(2,1fr);
    }

    .quote-price {
        font-size:1.65rem;
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
# THEME LIBRARY
#
# 고정된 FUTURE_CHAIN이 아니라
# "후보 테마군"만 정의합니다.
#
# 실제 단계와 순서는 시장 데이터로 자동 계산합니다.
# ============================================================

THEME_LIBRARY = {

    "AI 반도체": {
        "keywords": [
            "AI반도체", "반도체", "AI", "HBM",
            "반도체장비", "반도체소부장", "메모리"
        ],
        "seeds": [
            "395160", "487240", "471990", "396500"
        ],
        "reason":
            "AI 연산 확대와 HBM·첨단 메모리·반도체 투자 확대의 직접적인 수혜 영역입니다."
    },

    "데이터센터·AI 인프라": {
        "keywords": [
            "데이터센터", "AI인프라", "AI 인프라",
            "글로벌AI인프라", "네트워크", "서버"
        ],
        "seeds": [
            "449170", "434060", "381170"
        ],
        "reason":
            "AI 서비스 확산에 따라 서버·네트워크·데이터센터 투자가 증가하는 영역입니다."
    },

    "전력 인프라": {
        "keywords": [
            "전력", "전력인프라", "전력핵심설비",
            "전력설비", "전선", "전력기기"
        ],
        "seeds": [
            "464240", "487130"
        ],
        "reason":
            "데이터센터와 산업용 전력수요 증가에 따른 전력망·전력기기 투자 영역입니다."
    },

    "원자력": {
        "keywords": [
            "원자력", "원전", "원전산업",
            "SMR", "소형모듈원전"
        ],
        "seeds": [
            "130730", "161510"
        ],
        "reason":
            "전력수요 증가와 에너지 공급 안정성에 따라 원전 관련 산업 흐름을 추적합니다."
    },

    "냉각·열관리": {
        "keywords": [
            "냉각", "열관리", "액침냉각",
            "AI냉각", "열관리솔루션"
        ],
        "seeds": [
            "434060", "449170"
        ],
        "reason":
            "AI 서버 고집적화에 따라 냉각·열관리의 중요성이 높아지는 후방 수혜 영역입니다."
    },

    "광통신·네트워크": {
        "keywords": [
            "광통신", "광통신부품", "통신",
            "네트워크", "광섬유", "데이터전송"
        ],
        "seeds": [
            "261220", "322000"
        ],
        "reason":
            "AI 데이터센터 간 데이터 전송량 증가와 네트워크 고도화의 수혜 가능성을 추적합니다."
    },

    "로봇·자동화": {
        "keywords": [
            "로봇", "로보틱스", "자동화",
            "스마트팩토리", "산업자동화"
        ],
        "seeds": [
            "445290", "469750"
        ],
        "reason":
            "산업 자동화와 AI 기반 로봇 적용 확대에 따른 성장 영역입니다."
    },

    "2차전지": {
        "keywords": [
            "2차전지", "이차전지", "배터리",
            "전기차", "양극재", "음극재"
        ],
        "seeds": [
            "305540", "364980"
        ],
        "reason":
            "전기차·ESS·배터리 산업의 수요와 투자 흐름을 추적합니다."
    },

    "방산·우주": {
        "keywords": [
            "방산", "방위산업", "우주",
            "항공우주", "미사일", "국방"
        ],
        "seeds": [
            "449450", "463250"
        ],
        "reason":
            "국방비 증가와 우주산업 확대에 따른 관련 산업 흐름을 추적합니다."
    },
}


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
# BASIC HELPERS
# ============================================================

def esc(value):
    return html.escape(str(value))


def _normalize_etf_code(code):
    code = str(code or "").strip().upper()

    if code.isdigit():
        return code.zfill(6)

    return code


def _name_has_hangul(text):
    return any("가" <= ch <= "힣" for ch in str(text))


def _looks_mojibake(text):
    t = str(text)

    bad = (
        "Ã", "Â", "â", "ê", "ë", "ì",
        "í", "î", "ï", "ð", "ñ", "�"
    )

    return any(x in t for x in bad)


def safe_etf_name(code, name=None):

    code = str(code).zfill(6)

    if isinstance(name, dict):
        name = (
            name.get("name")
            or name.get("etf_name")
            or name.get("title")
        )

    text = html.unescape(str(name or "")).strip()

    if text.startswith("{") and "'name'" in text:
        try:
            parsed = ast.literal_eval(text)

            if isinstance(parsed, dict):
                text = str(
                    parsed.get("name")
                    or parsed.get("etf_name")
                    or parsed.get("title")
                    or ""
                ).strip()

        except Exception:

            m = re.search(
                r"['\"]name['\"]\s*:\s*['\"]([^'\"]+)['\"]",
                text
            )

            if m:
                text = m.group(1).strip()

    text = html.unescape(text).strip()

    if (
        not text
        or _looks_mojibake(text)
        or text.startswith("{")
        or "'ticker'" in text
        or '"ticker"' in text
    ):
        return f"ETF {code}"

    return text


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
# ETF MASTER
# ============================================================

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_naver_etf_master():

    url = "https://finance.naver.com/api/sise/etfItemList.nhn"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://finance.naver.com/sise/etf.nhn"
    }

    try:
        r = requests.get(
            url,
            headers=headers,
            timeout=12
        )

        r.raise_for_status()

        try:
            payload = r.json()

        except Exception:
            payload = json.loads(
                r.content.decode(
                    "cp949",
                    errors="ignore"
                )
            )

        items = (
            payload
            .get("result", {})
            .get("etfItemList", [])
        )

        return {
            _normalize_etf_code(x.get("itemcode")):
                safe_etf_name(
                    _normalize_etf_code(x.get("itemcode")),
                    x.get("itemname")
                )
            for x in items
            if x.get("itemcode")
            and x.get("itemname")
        }

    except Exception:
        return {}


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_krx_etf_master():

    url = (
        "https://data.krx.co.kr/"
        "comm/bldAttendant/getJsonData.cmd"
    )

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer":
            "https://data.krx.co.kr/contents/"
            "MDC/MDI/mdiLoader/index.cmd",
        "Origin": "https://data.krx.co.kr",
    }

    payload = {
        "bld":
            "dbms/MDC/STAT/standard/MDCSTAT04601",
        "locale": "ko_KR",
        "share": "1",
        "csvxls_isNo": "false",
    }

    try:
        r = requests.post(
            url,
            headers=headers,
            data=payload,
            timeout=15
        )

        r.raise_for_status()

        data = r.json()

        rows = (
            data.get("output")
            or data.get("OutBlock_1")
            or []
        )

        result = {}

        for x in rows:

            code = _normalize_etf_code(
                x.get("ISU_SRT_CD")
                or x.get("isu_srt_cd")
                or x.get("ISU_CD")
            )

            name = (
                x.get("ISU_ABBRV")
                or x.get("isu_abrv")
                or x.get("ISU_NM")
            )

            if code and name:
                result[code] = safe_etf_name(
                    code,
                    name
                )

        return result

    except Exception:
        return {}


def load_etf_universe():

    krx = fetch_krx_etf_master()
    naver = fetch_naver_etf_master()

    universe = {}

    for k, v in krx.items():

        if v and not v.startswith("ETF "):
            universe[k] = v

    for code, name in naver.items():

        if (
            code not in universe
            or not universe[code]
            or universe[code].startswith("ETF ")
        ):
            universe[code] = name

    return universe


# ============================================================
# STATE
# ============================================================

def init_state():

    if "watchlist" not in st.session_state:

        saved = read_json(
            WATCHLIST_FILE,
            DEFAULT_WATCHLIST.copy()
        )

        if isinstance(saved, list):
            st.session_state.watchlist = [
                _normalize_etf_code(x)
                for x in saved
            ]
        else:
            st.session_state.watchlist = (
                DEFAULT_WATCHLIST.copy()
            )

    if "holdings" not in st.session_state:

        saved = read_json(
            HOLDINGS_FILE,
            {}
        )

        st.session_state.holdings = (
            saved if isinstance(saved, dict)
            else {}
        )

    if "etf_universe" not in st.session_state:
        st.session_state.etf_universe = (
            load_etf_universe()
        )

    if "price_cache" not in st.session_state:
        st.session_state.price_cache = {}

    if "theme_cache" not in st.session_state:
        st.session_state.theme_cache = {}

    if "theme_engine_cache" not in st.session_state:
        st.session_state.theme_engine_cache = None

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

                found = None

                for item in col:

                    item_str = str(item)

                    if item_str.lower() in [
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume"
                    ]:
                        found = item_str.title()
                        break

                new_columns.append(
                    found if found else str(col[0])
                )

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

    required = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
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

    if getattr(df.index, "tz", None) is not None:

        try:
            df.index = df.index.tz_localize(None)

        except Exception:
            pass

    return df


def fetch_naver_history(code, count=600):

    code = _normalize_etf_code(code)

    url = (
        "https://fchart.stock.naver.com/"
        f"sise.nhn?symbol={code}"
        "&timeframe=day"
        f"&count={count}"
        "&requestType=0"
    )

    try:

        r = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=12
        )

        r.raise_for_status()

        root = ET.fromstring(r.text)

        rows = []

        for item in root.findall(".//item"):

            raw = item.attrib.get(
                "data",
                ""
            )

            parts = raw.split("|")

            if len(parts) < 6:
                continue

            rows.append(parts[:6])

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
            df["Date"],
            errors="coerce"
        )

        for col in [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        df = (
            df.dropna(
                subset=["Date", "Close"]
            )
            .set_index("Date")
        )

        return normalize_df(df)

    except Exception:
        return pd.DataFrame()


def fetch_yahoo(code):

    code = _normalize_etf_code(code)

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

        df = normalize_df(df)

        if not df.empty:
            return df

    except Exception:
        pass

    return fetch_naver_history(code)


def load_price_data(code, force=False):

    code = str(code).zfill(6)

    now = datetime.now()

    cached = st.session_state.price_cache.get(
        code
    )

    if cached and not force:

        age = (
            now - cached["time"]
        ).total_seconds()

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
        delta.clip(lower=0)
        .rolling(14)
        .mean()
    )

    loss = (
        (-delta)
        .clip(upper=0)
        .rolling(14)
        .mean()
    )

    rs = (
        gain /
        loss.replace(0, np.nan)
    )

    d["RSI14"] = (
        100 -
        (100 / (1 + rs))
    )

    d["VOL20"] = (
        d["Volume"]
        .rolling(20)
        .mean()
    )

    d["VOL_RATIO"] = (
        d["Volume"] /
        d["VOL20"].replace(0, np.nan)
    )

    d["RET5"] = (
        d["Close"]
        .pct_change(5) * 100
    )

    d["RET20"] = (
        d["Close"]
        .pct_change(20) * 100
    )

    d["RET60"] = (
        d["Close"]
        .pct_change(60) * 100
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
# ETF NAME
# ============================================================

def get_etf_name(code):

    code = str(code).zfill(6)

    return safe_etf_name(
        code,
        st.session_state.etf_universe.get(code)
    )


def lookup_live_etf(code):

    code = _normalize_etf_code(code)

    if not code:
        return ""

    for source in (
        fetch_krx_etf_master(),
        fetch_naver_etf_master()
    ):

        name = source.get(code)

        if (
            name
            and not name.startswith("ETF ")
        ):
            st.session_state.etf_universe[
                code
            ] = name

            return name

    try:

        info = yf.Ticker(
            f"{code}.KS"
        ).info

        name = (
            info.get("shortName")
            or info.get("longName")
            or ""
        )

        name = safe_etf_name(
            code,
            name
        )

        if (
            name
            and not name.startswith("ETF ")
        ):
            st.session_state.etf_universe[
                code
            ] = name

            return name

    except Exception:
        pass

    return f"ETF {code}"


# ============================================================
# JUDGMENT
# ============================================================

def get_judgment(d):

    if d.empty:

        return {
            "title": "데이터 부족",
            "reasons": [
                "가격 데이터를 확인하지 못했습니다."
            ],
            "action":
                "가격 데이터를 다시 확인해 주세요.",
            "ma_state": "확인 불가",
            "rsi_state": "확인 불가",
            "vol_state": "확인 불가",
            "rsi": 0,
            "vol_ratio": 0,
            "ret20": 0
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

    above20 = current >= ma20
    above60 = current >= ma60

    ma_state = (
        "20일선 상회"
        if above20
        else "20일선 하회"
    )

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
            "추세는 양호하지만 과열 가능성이 있습니다. "
            "신규 매수는 현재가 추격보다 눌림 확인을 우선합니다."
        )

    elif above20 and above60:

        title = "상승 추세 유지"

        action = (
            "20일선과 60일선 위입니다. "
            "신규 매수는 돌파 추격보다 눌림을 우선합니다."
        )

    elif above60 and not above20:

        title = "단기 조정 · 중기 추세 확인"

        action = (
            "20일선 아래지만 60일선 위입니다. "
            "20일선 회복 여부와 지지구간 거래량을 확인합니다."
        )

    elif not above60 and rsi <= 40:

        title = "중기 약세 · 방어 우선"

        action = (
            "60일선 아래이고 RSI도 약합니다. "
            "지지 형성과 거래량 회복을 먼저 확인합니다."
        )

    else:

        title = "방향 확인 구간"

        action = (
            "추세가 명확하지 않습니다. "
            "20일선 회복 또는 최근 고점 돌파와 "
            "거래량 동반 여부를 확인합니다."
        )

    reasons = [
        f"현재가 {money(current)} · "
        f"20일선 {money(ma20)} · {ma_state}",

        f"60일선 {money(ma60)} · "
        f"{'중기 추세 유지' if above60 else '중기 추세 약화'}",

        f"RSI14 {rsi:.1f} · {rsi_state}",

        f"거래량 {vol_ratio:.2f}배 · "
        f"{vol_state} · 최근 20일 {ret20:+.2f}%"
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

    return {
        "first": ma20,
        "support": min(ma60, low20),
        "breakout": high20,
        "risk": min(
            ma60,
            low20,
            low60
        )
    }


# ============================================================
# JUDGMENT UI
# ============================================================

def render_judgment(d):

    judgment = get_judgment(d)

    st.markdown(
        "### 현재판단 · 지금대응"
    )

    rsi = judgment["rsi"]
    vr = judgment["vol_ratio"]

    ma_color = (
        "positive"
        if judgment["ma_state"]
        == "20일선 상회"
        else "negative"
    )

    rsi_color = (
        "positive"
        if rsi >= 60
        else (
            "negative"
            if rsi < 40
            else "neutral"
        )
    )

    vol_color = (
        "positive"
        if vr >= 1.1
        else (
            "negative"
            if vr < 0.8
            else "neutral"
        )
    )

    st.markdown(
        f"""
        <div class="evidence-grid">

            <div class="evidence-box">
                <div class="evidence-label">
                    20일선
                </div>
                <div class="evidence-value {ma_color}">
                    {esc(judgment["ma_state"])}
                </div>
                <div class="evidence-sub">
                    단기 추세
                </div>
            </div>

            <div class="evidence-box">
                <div class="evidence-label">
                    RSI14
                </div>
                <div class="evidence-value {rsi_color}">
                    {rsi:.1f}
                </div>
                <div class="evidence-sub">
                    {esc(judgment["rsi_state"])}
                </div>
            </div>

            <div class="evidence-box">
                <div class="evidence-label">
                    거래량
                </div>
                <div class="evidence-value {vol_color}">
                    {vr:.2f}배
                </div>
                <div class="evidence-sub">
                    {esc(judgment["vol_state"])}
                </div>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:

        reasons_html = "<br>".join(
            esc(x)
            for x in judgment["reasons"]
        )

        st.markdown(
            f"""
            <div class="judgment-box">
                <div class="judgment-title">
                    현재판단
                </div>

                <div class="judgment-main">
                    {esc(judgment["title"])}
                </div>

                <div class="reason-label">
                    판단근거
                </div>

                <div class="judgment-reason">
                    {reasons_html}
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
                    지금대응
                </div>

                <div class="action-main">
                    {esc(judgment["action"])}
                </div>

                <div class="action-reason-label">
                    대응근거
                </div>

                <div class="judgment-reason">
                    현재 추세·RSI·거래량을 기준으로
                    신규 매수는 추격보다 눌림 또는
                    확인 후 대응하도록 설정했습니다.
                </div>
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

    rsi = safe_float(
        d["RSI14"].iloc[-1],
        50
    )

    vol_ratio = safe_float(
        d["VOL_RATIO"].iloc[-1],
        1
    )

    st.markdown(
        "### 핵심가격 · 대응 시나리오"
    )

    st.caption(
        "현재가를 기준으로 눌림 · 지지 · 돌파 · 위험 구간을 "
        "나누고 각 가격에서 확인할 조건과 대응 방법을 제시합니다."
    )

    cards = [

        {
            "label": "① 1차 관심",
            "price": levels["first"],
            "condition": "20일선 부근 눌림",
            "meaning":
                "단기 상승 추세가 유지되는지 확인하는 첫 번째 가격대입니다.",
            "action":
                "급락 중 바로 매수하지 말고 가격이 20일선에서 멈추는지 확인합니다."
        },

        {
            "label": "② 핵심 지지",
            "price": levels["support"],
            "condition": "중기 추세 방어",
            "meaning":
                "최근 저점과 중기 이동평균을 기준으로 추세의 방어력을 확인합니다.",
            "action":
                "지지와 거래량 안정이 확인될 때 분할 대응을 검토합니다."
        },

        {
            "label": "③ 돌파 기준",
            "price": levels["breakout"],
            "condition": "최근 20일 고점 돌파",
            "meaning":
                "최근 매물 부담을 넘어 새로운 단기 고점을 만드는 기준입니다.",
            "action":
                "가격만 돌파하지 말고 거래량 증가가 동반되는지 확인합니다."
        },

        {
            "label": "④ 위험 가격",
            "price": levels["risk"],
            "condition": "핵심 지지 이탈",
            "meaning":
                "중기 추세가 약해질 수 있어 신규 진입보다 방어가 우선되는 가격대입니다.",
            "action":
                "지지 회복 전까지 신규 매수는 보수적으로 접근합니다."
        }
    ]

    cols = st.columns(4)

    for col, card in zip(cols, cards):

        with col:

            with st.container(border=True):

                st.markdown(
                    f"**{card['label']}**"
                )

                st.markdown(
                    f"### {money(card['price'])}"
                )

                st.caption(
                    card["condition"]
                )

                st.markdown(
                    f"**의미**  \n"
                    f"{card['meaning']}"
                )

                st.markdown(
                    f"**대응**  \n"
                    f"{card['action']}"
                )

    st.divider()

    if current < levels["risk"]:

        state = "핵심 지지 하회"

        state_desc = (
            "현재가는 위험 가격 아래에 있습니다. "
            "신규 진입보다 지지 회복 여부를 먼저 확인하는 구간입니다."
        )

        action = "신규매수 보류 · 지지 회복 확인"

        trigger = (
            f"{money(levels['risk'])} 회복 여부"
        )

    elif current <= levels["support"] * 1.015:

        state = "핵심 지지 접근"

        state_desc = (
            "핵심 지지구간에 접근했습니다. "
            "가격이 지지를 지키고 거래량이 안정되는지가 중요합니다."
        )

        action = "분할매수 검토 · 지지 확인"

        trigger = (
            f"{money(levels['support'])} 지지 + 거래량 안정"
        )

    elif current < levels["first"] * 1.015:

        state = "1차 관심구간"

        state_desc = (
            "20일선 부근에서 눌림을 확인할 수 있는 구간입니다. "
            "급등 추격보다 지지 확인이 중요합니다."
        )

        action = "눌림매수 검토 · 추격 자제"

        trigger = (
            f"20일선 {money(ma20)} 지지 확인"
        )

    elif current >= levels["breakout"]:

        state = "돌파구간"

        state_desc = (
            "최근 20일 고점 기준을 넘어선 상태입니다. "
            "거래량이 동반되면 돌파 신뢰도를 높일 수 있습니다."
        )

        action = "돌파 확인 · 거래량 체크"

        trigger = (
            f"거래량 {vol_ratio:.2f}배 이상 여부"
        )

    else:

        state = "추세 유지구간"

        state_desc = (
            "현재가는 주요 지지와 돌파 기준 사이에 있습니다. "
            "방향이 확정되기 전에는 추격보다 눌림을 기다립니다."
        )

        action = "보유 관찰 · 눌림 대기"

        trigger = (
            f"20일선 {money(ma20)} / "
            f"고점 {money(high20)}"
        )

    st.markdown(
        "#### 지금은 어떻게 대응할까?"
    )

    c1, c2 = st.columns([1, 2])

    with c1:

        st.metric(
            "현재가",
            money(current)
        )

        st.markdown(
            f"**현재 위치**  \n{state}"
        )

        st.markdown(
            f"**권장 대응**  \n{action}"
        )

    with c2:

        st.info(state_desc)

        st.markdown(
            f"**핵심 확인조건:** {trigger}"
        )

        evidence = []

        evidence.append(
            f"20일선 {money(ma20)} · "
            f"{'상회' if current >= ma20 else '하회'}"
        )

        evidence.append(
            f"60일선 {money(ma60)} · "
            f"{'상회' if current >= ma60 else '하회'}"
        )

        evidence.append(
            f"RSI14 {rsi:.1f} · "
            f"{'과열권' if rsi >= 70 else ('약세권' if rsi <= 40 else '중립권')}"
        )

        evidence.append(
            f"거래량 {vol_ratio:.2f}배 · "
            f"{'증가' if vol_ratio >= 1.1 else ('감소' if vol_ratio < 0.8 else '평균권')}"
        )

        st.caption(
            " · ".join(evidence)
        )

    st.markdown(
        "#### 가격대별 행동 기준"
    )

    scenario_cols = st.columns(3)

    with scenario_cols[0]:

        st.markdown("**눌림 시나리오**")

        st.write(
            f"20일선 {money(ma20)} 부근까지 조정 "
            "→ 지지 확인 → 거래량 안정 시 분할 접근"
        )

    with scenario_cols[1]:

        st.markdown("**돌파 시나리오**")

        st.write(
            f"최근 고점 {money(high20)} 돌파 "
            "→ 거래량 증가 확인 → 돌파 유지 여부 확인"
        )

    with scenario_cols[2]:

        st.markdown("**이탈 시나리오**")

        st.write(
            f"위험 가격 {money(levels['risk'])} 이탈 "
            "→ 신규매수 보류 → 지지 회복 여부 재확인"
        )


# ============================================================
# CHART
# ============================================================

def render_chart(d):

    if d.empty:

        st.warning(
            "차트 데이터를 확인하지 못했습니다."
        )

        return

    chart_df = d.tail(126).copy()

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.025,
        row_heights=[0.75, 0.25]
    )

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
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA20"],
            mode="lines",
            line=dict(
                color="#4f86b5",
                width=1.4
            ),
            name="20일선"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA60"],
            mode="lines",
            line=dict(
                color="#a58c52",
                width=1.3
            ),
            name="60일선"
        ),
        row=1,
        col=1
    )

    volume_colors = np.where(
        chart_df["Close"] >= chart_df["Open"],
        "#327f69",
        "#9b4653"
    )

    fig.add_trace(
        go.Bar(
            x=chart_df.index,
            y=chart_df["Volume"],
            marker_color=volume_colors,
            opacity=0.5,
            name="거래량",
            showlegend=False
        ),
        row=2,
        col=1
    )

    fig.update_xaxes(
        fixedrange=True,
        showgrid=False,
        rangeslider_visible=False
    )

    fig.update_yaxes(
        fixedrange=True,
        gridcolor="#17283a",
        tickfont=dict(
            color="#73879b",
            size=9
        ),
        row=1,
        col=1
    )

    fig.update_yaxes(
        fixedrange=True,
        showticklabels=False,
        showgrid=False,
        row=2,
        col=1
    )

    fig.update_layout(
        height=390,
        margin=dict(
            l=4,
            r=4,
            t=18,
            b=4
        ),
        paper_bgcolor="#0d1928",
        plot_bgcolor="#0d1928",
        font=dict(
            color="#aab8c7"
        ),
        legend=dict(
            orientation="h",
            y=1.02,
            x=1,
            xanchor="right",
            font=dict(
                size=9,
                color="#8ea0b3"
            )
        ),
        dragmode=False,
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "doubleClick": False,
            "responsive": True,
            "staticPlot": True
        }
    )


# ============================================================
# SEARCH
# ============================================================

def search_etfs(query):

    query_raw = (
        query or ""
    ).strip()

    query = query_raw.lower()

    if not query:
        return []

    results = []
    seen = set()

    for raw_code, raw_name in (
        st.session_state.etf_universe.items()
    ):

        code = str(
            raw_code
        ).strip().upper()

        if code.isdigit():
            code = code.zfill(6)

        name = get_etf_name(code)

        if code in seen:
            continue

        search_name = (
            str(name)
            .strip()
            .lower()
        )

        if (
            query in code.lower()
            or query in search_name
        ):

            results.append({
                "code": code,
                "name": name
            })

            seen.add(code)

    compact = (
        query_raw
        .replace(".", "")
        .replace("-", "")
        .strip()
        .upper()
    )

    if re.fullmatch(
        r"[0-9A-Z]{6}",
        compact
    ):

        code = compact

        if code not in seen:

            name = lookup_live_etf(
                code
            )

            results.insert(
                0,
                {
                    "code": code,
                    "name": name
                }
            )

            st.session_state.etf_universe[
                code
            ] = name

            seen.add(code)

    return results[:30]


# ============================================================
# WATCHLIST
# ============================================================

def add_watch(code):

    code = _normalize_etf_code(code)

    if code not in st.session_state.watchlist:

        st.session_state.watchlist.append(
            code
        )

        write_json(
            WATCHLIST_FILE,
            st.session_state.watchlist
        )

    st.session_state.selected_code = code


def render_finder():

    st.markdown(
        "### ETF 찾기"
    )

    query = st.text_input(
        "ETF명 또는 종목코드",
        placeholder="예: AI반도체 / 395160",
        label_visibility="collapsed",
        key="search_q"
    )

    results = search_etfs(query)

    if results:

        result_map = {
            str(x["code"]).zfill(6): x
            for x in results
        }

        result_codes = list(
            result_map.keys()
        )

        selected_code = st.selectbox(
            "검색 결과",
            result_codes,
            format_func=lambda code:
                f"{get_etf_name(code)} · {code}",
            key="search_result"
        )

        item = result_map[
            str(selected_code).zfill(6)
        ]

        c1, c2 = st.columns([4, 1])

        with c1:

            st.caption(
                f'선택: {item["name"]} '
                f'({item["code"]})'
            )

        with c2:

            already = (
                item["code"]
                in st.session_state.watchlist
            )

            if st.button(
                "추가" if not already else "등록됨",
                disabled=already,
                use_container_width=True,
                key=f'add_{item["code"]}'
            ):

                add_watch(
                    item["code"]
                )

                st.rerun()

    elif query:

        st.caption(
            "검색 결과가 없습니다."
        )


# ============================================================
# WATCHLIST UI
# ============================================================

def render_watchlist():

    st.markdown(
        "### 관심종목"
    )

    watchlist = (
        st.session_state.watchlist
    )

    if not watchlist:

        st.info(
            "관심종목이 없습니다."
        )

        return

    current = (
        st.session_state.selected_code
    )

    default_index = (
        watchlist.index(current)
        if current in watchlist
        else 0
    )

    selected_code = st.selectbox(
        "관심종목 선택",
        watchlist,
        index=default_index,
        format_func=lambda code:
            f"{get_etf_name(code)} · {code}",
        key="watch_select"
    )

    code = str(
        selected_code
    ).zfill(6)

    st.session_state.selected_code = code

    if st.button(
        "현재 ETF 관심종목에서 삭제",
        use_container_width=True,
        key="remove_watch"
    ):

        watchlist.remove(code)

        write_json(
            WATCHLIST_FILE,
            watchlist
        )

        st.session_state.selected_code = (
            watchlist[0]
            if watchlist
            else "395160"
        )

        st.rerun()


# ============================================================
# HOLDINGS
# ============================================================

def render_holdings(code, current):

    st.markdown(
        "### 보유 상태"
    )

    old = (
        st.session_state.holdings.get(code)
    )

    held = st.radio(
        "보유 여부",
        ["미보유", "보유중"],
        index=1 if old else 0,
        horizontal=True,
        key=f"held_{code}"
    )

    if held == "보유중":

        c1, c2 = st.columns(2)

        with c1:

            avg = st.number_input(
                "평균매수가",
                min_value=0.0,
                value=float(
                    old.get(
                        "avg_price",
                        0
                    )
                    if old
                    else 0
                ),
                step=100.0,
                key=f"avg_{code}"
            )

        with c2:

            qty = st.number_input(
                "보유수량",
                min_value=0.0,
                value=float(
                    old.get(
                        "quantity",
                        0
                    )
                    if old
                    else 0
                ),
                step=1.0,
                key=f"qty_{code}"
            )

        if st.button(
            "보유정보 저장",
            key=f"save_{code}",
            use_container_width=True
        ):

            st.session_state.holdings[
                code
            ] = {
                "avg_price": avg,
                "quantity": qty
            }

            write_json(
                HOLDINGS_FILE,
                st.session_state.holdings
            )

            st.rerun()

        if avg > 0:

            pnl = (
                current / avg - 1
            ) * 100

            cls = (
                "positive"
                if pnl >= 0
                else "negative"
            )

            st.markdown(
                f"""
                <div class="holding-box">

                    <div class="holding-value">
                        보유 {qty:,.0f}주
                    </div>

                    <div class="holding-detail">
                        평균매수가 {money(avg)}
                        · 현재 수익률
                        <span class="{cls}">
                            {pnl:+.2f}%
                        </span>
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    elif old:

        if st.button(
            "보유정보 삭제",
            key=f"del_{code}",
            use_container_width=True
        ):

            del st.session_state.holdings[
                code
            ]

            write_json(
                HOLDINGS_FILE,
                st.session_state.holdings
            )

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

        st.error(
            "가격 데이터를 불러오지 못했습니다. "
            "종목코드 또는 인터넷 연결을 확인해 주세요."
        )

        return

    d = calculate_indicators(df)

    if d.empty:

        st.error(
            "분석 데이터를 만들지 못했습니다."
        )

        return

    current = safe_float(
        d["Close"].iloc[-1]
    )

    previous = (
        safe_float(
            d["Close"].iloc[-2]
        )
        if len(d) >= 2
        else current
    )

    change = current - previous

    change_pct = (
        change / previous * 100
        if previous != 0
        else 0
    )

    cls = (
        "positive"
        if change > 0
        else (
            "negative"
            if change < 0
            else "neutral"
        )
    )

    date_text = d.index[
        -1
    ].strftime("%Y-%m-%d")

    st.markdown(
        f"""
        <div class="hero">

            <div class="hero-name">
                {esc(name)}
            </div>

            <div class="hero-code">
                {esc(code)}
            </div>

            <div class="quote-row">

                <div class="quote-price">
                    {money(current)}
                </div>

                <div class="quote-change {cls}">
                    {money(change)}
                    ({change_pct:+.2f}%)
                </div>

            </div>

            <div class="hero-date">
                기준일 {esc(date_text)}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    render_holdings(
        code,
        current
    )

    render_judgment(d)

    render_scenarios(d)

    st.markdown(
        '<div class="section-title">'
        '가격 흐름 · 최근 6개월'
        '</div>',
        unsafe_allow_html=True
    )

    render_chart(d)


# ============================================================
# THEME CLASSIFICATION
# ============================================================

def theme_candidates(theme):

    info = THEME_LIBRARY[
        theme
    ]

    result = []

    used = set()

    # seed ETF
    for code in info["seeds"]:

        code = _normalize_etf_code(
            code
        )

        if code in used:
            continue

        name = get_etf_name(code)

        if (
            not name
            or name.startswith("ETF ")
        ):
            name = lookup_live_etf(
                code
            )

        result.append({
            "code": code,
            "name": name
        })

        used.add(code)

    # universe keyword
    for raw_code, raw_name in (
        st.session_state.etf_universe.items()
    ):

        code = _normalize_etf_code(
            raw_code
        )

        name = safe_etf_name(
            code,
            raw_name
        )

        text = (
            f"{code} {name}"
            .lower()
        )

        if any(
            keyword.lower() in text
            for keyword in info["keywords"]
        ):

            if code not in used:

                result.append({
                    "code": code,
                    "name": name
                })

                used.add(code)

    return result[:8]


# ============================================================
# BENCHMARK
# ============================================================

def get_benchmark_metrics():

    df = load_price_data(
        "069500"
    )

    if df.empty:
        return {
            "ret5": 0.0,
            "ret20": 0.0,
            "ret60": 0.0
        }

    d = calculate_indicators(df)

    if d.empty:
        return {
            "ret5": 0.0,
            "ret20": 0.0,
            "ret60": 0.0
        }

    row = d.iloc[-1]

    return {
        "ret5": safe_float(
            row.get("RET5", 0)
        ),
        "ret20": safe_float(
            row.get("RET20", 0)
        ),
        "ret60": safe_float(
            row.get("RET60", 0)
        )
    }


# ============================================================
# FUTURE THEME ENGINE
#
# 핵심 알고리즘
#
# ETF별:
# 5일 수익률
# 20일 수익률
# 60일 수익률
# 거래량
# RSI
# 20/60일선
# 시장 대비 상대강도
#
# 테마별:
# 평균 모멘텀
# 상승 ETF 비율
# 거래량 확산
# 상대강도
# 추세 확산
#
# 을 종합해 100점 계산.
# ============================================================

def score_range(
    value,
    low,
    high,
    points
):

    if value <= low:
        return 0.0

    if value >= high:
        return float(points)

    return (
        (value - low)
        / (high - low)
    ) * points


def calculate_theme_score(
    rows,
    benchmark
):

    if not rows:
        return {
            "score": 0.0,
            "avg5": 0.0,
            "avg20": 0.0,
            "avg60": 0.0,
            "avg_rsi": 0.0,
            "avg_vol": 0.0,
            "breadth": 0.0,
            "trend_breadth": 0.0,
            "relative20": 0.0
        }

    avg5 = float(
        np.mean([
            x["ret5"]
            for x in rows
        ])
    )

    avg20 = float(
        np.mean([
            x["ret20"]
            for x in rows
        ])
    )

    avg60 = float(
        np.mean([
            x["ret60"]
            for x in rows
        ])
    )

    avg_rsi = float(
        np.mean([
            x["rsi"]
            for x in rows
        ])
    )

    avg_vol = float(
        np.mean([
            x["vr"]
            for x in rows
        ])
    )

    breadth = (
        sum(
            1
            for x in rows
            if x["ret20"] > 0
        )
        / len(rows)
        * 100
    )

    trend_breadth = (
        sum(
            1
            for x in rows
            if x["above20"]
            and x["above60"]
        )
        / len(rows)
        * 100
    )

    relative20 = (
        avg20
        - benchmark["ret20"]
    )

    # --------------------------------------------
    # 100점 구성
    #
    # 20일 상대강도       25
    # 60일 모멘텀         20
    # 5일 모멘텀          10
    # 거래량 확산         15
    # 상승 확산도         15
    # 장기 추세 확산      10
    # RSI 건전성            5
    # --------------------------------------------

    relative_score = score_range(
        relative20,
        -5,
        10,
        25
    )

    ret60_score = score_range(
        avg60,
        -10,
        20,
        20
    )

    ret5_score = score_range(
        avg5,
        -3,
        7,
        10
    )

    volume_score = score_range(
        avg_vol,
        0.8,
        1.8,
        15
    )

    breadth_score = (
        breadth / 100
    ) * 15

    trend_score = (
        trend_breadth / 100
    ) * 10

    # RSI가 너무 낮거나 너무 높은 경우 감점
    if 50 <= avg_rsi <= 68:
        rsi_score = 5

    elif 45 <= avg_rsi < 50:
        rsi_score = 3.5

    elif 68 < avg_rsi <= 72:
        rsi_score = 3.5

    else:
        rsi_score = 1.5

    total = (
        relative_score
        + ret60_score
        + ret5_score
        + volume_score
        + breadth_score
        + trend_score
        + rsi_score
    )

    return {
        "score": round(
            min(100, max(0, total)),
            1
        ),
        "avg5": avg5,
        "avg20": avg20,
        "avg60": avg60,
        "avg_rsi": avg_rsi,
        "avg_vol": avg_vol,
        "breadth": breadth,
        "trend_breadth": trend_breadth,
        "relative20": relative20
    }


def theme_snapshot_dynamic(
    theme,
    benchmark
):

    cached = (
        st.session_state
        .theme_cache
        .get(theme)
    )

    now = datetime.now()

    if cached:

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

        df = load_price_data(code)

        if df.empty:
            continue

        if len(df) < 65:
            continue

        d = calculate_indicators(df)

        if d.empty:
            continue

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

        ret5 = safe_float(
            row["RET5"],
            0
        )

        ret20 = safe_float(
            row["RET20"],
            0
        )

        ret60 = safe_float(
            row["RET60"],
            0
        )

        rsi = safe_float(
            row["RSI14"],
            50
        )

        vr = safe_float(
            row["VOL_RATIO"],
            1
        )

        rows.append({
            "code": code,
            "name": item["name"],
            "price": current,
            "rsi": rsi,
            "vr": vr,
            "ret5": ret5,
            "ret20": ret20,
            "ret60": ret60,
            "relative20":
                ret20 - benchmark["ret20"],
            "above20":
                current >= ma20,
            "above60":
                current >= ma60,
            "dist20":
                (
                    current / ma20 - 1
                ) * 100
                if ma20
                else 0,
            "trend":
                "상승"
                if current >= ma20
                else "조정"
        })

    st.session_state.theme_cache[
        theme
    ] = {
        "time": now,
        "rows": rows
    }

    return rows


# ============================================================
# DYNAMIC STAGE
# ============================================================

def assign_theme_stages(
    scored_themes
):

    if not scored_themes:
        return []

    # 점수순으로 정렬
    ranked = sorted(
        scored_themes,
        key=lambda x:
            x["score"],
        reverse=True
    )

    # 점수 절대값과 상대순위를 함께 사용
    result = []

    for idx, item in enumerate(ranked):

        score = item["score"]

        if idx == 0 and score >= 65:

            stage = "현재 주도"

        elif score >= 65:

            stage = "다음 수혜"

        elif score >= 52:

            stage = "관심 확대"

        else:

            stage = "초기 관심"

        item = dict(item)

        item["stage"] = stage

        result.append(item)

    # 1위가 충분히 강하지 않으면
    # '현재 주도'를 억지로 만들지 않음.
    if result:

        if result[0]["score"] < 65:

            for item in result:

                if item["stage"] == "현재 주도":
                    item["stage"] = "관심 확대"

    return result


def build_future_theme_engine(
    force=False
):

    now = datetime.now()

    cached = (
        st.session_state
        .theme_engine_cache
    )

    if cached and not force:

        age = (
            now - cached["time"]
        ).total_seconds()

        if age < 300:
            return cached

    benchmark = get_benchmark_metrics()

    scored = []

    for theme in THEME_LIBRARY:

        rows = theme_snapshot_dynamic(
            theme,
            benchmark
        )

        if not rows:
            continue

        metrics = calculate_theme_score(
            rows,
            benchmark
        )

        scored.append({
            "theme": theme,
            "score": metrics["score"],
            "rows": rows,
            **metrics
        })

    staged = assign_theme_stages(
        scored
    )

    data = {
        "time": now,
        "benchmark": benchmark,
        "themes": staged
    }

    st.session_state.theme_engine_cache = data

    return data


# ============================================================
# FUTURE OUTLOOK
# ============================================================

def future_outlook(
    theme,
    rows,
    metrics=None
):

    if not rows:
        return (
            "현재 가격 데이터를 충분히 확보하지 못했습니다."
        )

    avg_ret = float(
        np.mean([
            x["ret20"]
            for x in rows
        ])
    )

    avg_rsi = float(
        np.mean([
            x["rsi"]
            for x in rows
        ])
    )

    avg_vol = float(
        np.mean([
            x["vr"]
            for x in rows
        ])
    )

    rising = sum(
        1
        for x in rows
        if x["trend"] == "상승"
    )

    total = len(rows)

    if metrics:

        breadth = metrics.get(
            "breadth",
            0
        )

        relative20 = metrics.get(
            "relative20",
            0
        )

        score = metrics.get(
            "score",
            0
        )

        return (
            f"테마점수 {score:.1f}/100 · "
            f"20일 평균 {avg_ret:+.1f}% · "
            f"시장 대비 {relative20:+.1f}%p · "
            f"상승확산 {breadth:.0f}% · "
            f"RSI {avg_rsi:.1f} · "
            f"거래량 {avg_vol:.2f}배"
        )

    if (
        rising == total
        and avg_ret >= 3
    ):

        return (
            f"단기 추세가 우호적입니다. "
            f"구성 ETF {rising}/{total}개가 상승 추세이며 "
            f"20일 평균 수익률 {avg_ret:+.1f}%입니다."
        )

    if (
        rising >= max(
            1,
            total // 2
        )
        and avg_ret >= 0
    ):

        return (
            f"상승과 조정이 혼재하지만 흐름은 유지되고 있습니다. "
            f"{rising}/{total}개가 상승 추세이며 "
            f"20일 평균 수익률은 {avg_ret:+.1f}%입니다."
        )

    if avg_ret < 0:

        return (
            f"아직 추세가 약한 구간입니다. "
            f"20일 평균 수익률 {avg_ret:+.1f}%로 "
            f"회복 여부를 확인해야 합니다."
        )

    return (
        f"중립적인 흐름입니다. "
        f"20일 평균 수익률 {avg_ret:+.1f}%, "
        f"RSI {avg_rsi:.1f}, "
        f"거래량 {avg_vol:.2f}배를 기준으로 "
        f"추세 전환 여부를 확인합니다."
    )


# ============================================================
# INLINE FUTURE ETF ANALYSIS
# ============================================================

def render_future_inline_analysis():

    code = (
        st.session_state.future_detail_code
    )

    if not code:
        return

    theme = (
        st.session_state.future_detail_theme
    )

    df = load_price_data(code)

    if df.empty:

        st.warning(
            "선택한 ETF의 가격 데이터를 확인하지 못했습니다."
        )

        return

    d = calculate_indicators(df)

    if d.empty:
        return

    name = get_etf_name(code)

    current = safe_float(
        d["Close"].iloc[-1]
    )

    previous = (
        safe_float(
            d["Close"].iloc[-2]
        )
        if len(d) > 1
        else current
    )

    change = current - previous

    pct = (
        change / previous * 100
        if previous
        else 0
    )

    cls = (
        "positive"
        if change > 0
        else (
            "negative"
            if change < 0
            else "neutral"
        )
    )

    st.markdown(
        f"""
        <div class="future-analysis">

            <div class="future-analysis-title">
                미래테마 안에서 분석 ·
                {esc(theme or "선택 ETF")}
            </div>

            <div class="future-analysis-name">
                {esc(name)}
            </div>

            <div class="future-analysis-code">
                {esc(code)}
            </div>

            <div class="quote-row">

                <div class="quote-price">
                    {money(current)}
                </div>

                <div class="quote-change {cls}">
                    {money(change)}
                    ({pct:+.2f}%)
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    render_judgment(d)

    render_scenarios(d)

    st.markdown(
        '<div class="section-title">'
        '가격 흐름 · 최근 6개월'
        '</div>',
        unsafe_allow_html=True
    )

    render_chart(d)


# ============================================================
# FUTURE THEME UI
# ============================================================

def future_stage_class(stage):

    if "현재 주도" in stage:
        return "stage-core"

    if "다음 수혜" in stage:
        return "stage-next"

    if "관심 확대" in stage:
        return "stage-interest"

    return "stage-early"


def render_future_theme():

    st.markdown(
        """
        <div class="section-title">
            🚀 미래테마
        </div>

        <div style="
            color:#8196aa;
            font-size:.75rem;
            margin-bottom:12px;
        ">
            ETF 전체 흐름을 분석하여
            현재 주도 → 다음 수혜 → 관심 확대 →
            초기 관심 순으로 자동 분류합니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    uc1, uc2 = st.columns([1, 1])

    with uc1:

        if st.button(
            "🔄 미래테마 수동 업데이트",
            use_container_width=True,
            key="future_theme_refresh"
        ):

            st.session_state.theme_cache = {}

            st.session_state.theme_engine_cache = None

            st.session_state.price_cache = {}

            st.rerun()

    with uc2:

        auto_update = st.checkbox(
            "⚡ 자동 업데이트 · 30분",
            value=False,
            key="future_auto_update"
        )

        if auto_update:

            if st_autorefresh is not None:

                st_autorefresh(
                    interval=30 * 60 * 1000,
                    key="future_theme_autorefresh"
                )

            else:

                st.caption(
                    "자동 업데이트 기능은 "
                    "requirements.txt에 "
                    "streamlit-autorefresh가 필요합니다."
                )

    with st.spinner(
        "미래테마를 시장 데이터로 계산하는 중입니다…"
    ):

        engine = build_future_theme_engine()

    themes = engine["themes"]

    if not themes:

        st.warning(
            "미래테마를 계산할 수 있는 ETF 데이터가 없습니다."
        )

        return

    # --------------------------------------------------------
    # 자동 선정 기준 설명
    # --------------------------------------------------------

    with st.expander(
        "미래테마 선정 알고리즘 보기",
        expanded=False
    ):

        st.markdown(
            """
            **테마 점수 100점 구성**

            - 20일 시장 대비 상대강도: 25점
            - 60일 모멘텀: 20점
            - 5일 단기 모멘텀: 10점
            - 거래량 확산: 15점
            - 테마 내 상승 ETF 비율: 15점
            - 20·60일선 추세 확산: 10점
            - RSI 건전성: 5점

            각 테마의 구성 ETF 데이터를 집계한 후
            시장 전체 대비 상대강도와 테마 내부의
            상승 확산도를 함께 반영합니다.

            따라서 **테마의 순서와 단계는 고정되지 않고
            시장 데이터에 따라 변경됩니다.**
            """
        )

    # --------------------------------------------------------
    # 테마별 자동 순위
    # --------------------------------------------------------

    for theme_index, item in enumerate(themes):

        theme = item["theme"]
        stage = item["stage"]
        rows = item["rows"]

        info = THEME_LIBRARY[theme]

        stage_cls = future_stage_class(
            stage
        )

        outlook = future_outlook(
            theme,
            rows,
            item
        )

        st.markdown(
            f"""
            <div class="theme-card">

                <div class="theme-stage-wrap">
                    <span class="theme-stage-badge {stage_cls}">
                        {esc(stage)}
                    </span>
                </div>

                <div class="theme-title">
                    {esc(theme)}
                </div>

                <div class="theme-reason">
                    {esc(info["reason"])}
                </div>

                <div class="theme-score-box">

                    <div class="theme-score-label">
                        자동 테마 점수
                    </div>

                    <div class="theme-score-number">
                        {item["score"]:.1f}
                        <span style="
                            font-size:.72rem;
                            color:#71879b;
                        ">
                            / 100
                        </span>
                    </div>

                    <div style="
                        font-size:.66rem;
                        color:#71879b;
                        margin-top:4px;
                    ">
                        20일 상대강도
                        {item["relative20"]:+.2f}%p
                        · 상승확산
                        {item["breadth"]:.0f}%
                        · 추세확산
                        {item["trend_breadth"]:.0f}%
                    </div>

                </div>

                <div class="theme-outlook">
                    <strong>현재 흐름</strong>
                    · {esc(outlook)}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        if not rows:

            st.caption(
                "현재 표시 가능한 ETF 데이터가 없습니다."
            )

            continue

        cols = st.columns(
            min(len(rows), 4)
        )

        for i, item_etf in enumerate(
            rows[:4]
        ):

            with cols[i]:

                ret_cls = (
                    "positive"
                    if item_etf["ret20"] >= 0
                    else "negative"
                )

                trend_cls = (
                    "positive"
                    if item_etf["trend"] == "상승"
                    else "negative"
                )

                st.markdown(
                    f"""
                    <div class="theme-etf-box">

                        <div class="theme-etf-name">
                            {esc(item_etf["name"])}
                        </div>

                        <div class="theme-etf-code">
                            {esc(item_etf["code"])}
                        </div>

                        <div class="theme-data-grid">

                            <div class="theme-data-item">
                                <div class="theme-data-label">
                                    현재가
                                </div>
                                <div class="theme-data-value">
                                    {money(item_etf["price"])}
                                </div>
                            </div>

                            <div class="theme-data-item">
                                <div class="theme-data-label">
                                    RSI
                                </div>
                                <div class="theme-data-value">
                                    {item_etf["rsi"]:.1f}
                                </div>
                            </div>

                            <div class="theme-data-item">
                                <div class="theme-data-label">
                                    거래량
                                </div>
                                <div class="theme-data-value">
                                    {item_etf["vr"]:.2f}배
                                </div>
                            </div>

                            <div class="theme-data-item">
                                <div class="theme-data-label">
                                    20일
                                </div>
                                <div class="theme-data-value {ret_cls}">
                                    {item_etf["ret20"]:+.2f}%
                                </div>
                            </div>

                        </div>

                        <div style="
                            font-size:.64rem;
                            color:#71869a;
                            margin-top:7px;
                        ">
                            5일
                            {item_etf["ret5"]:+.2f}%
                            · 60일
                            {item_etf["ret60"]:+.2f}%
                            · 추세
                            <span class="{trend_cls}">
                                {esc(item_etf["trend"])}
                            </span>
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                is_open = (
                    st.session_state.future_detail_code
                    == item_etf["code"]
                )

                button_label = (
                    "분석 닫기"
                    if is_open
                    else "ETF 분석"
                )

                if st.button(
                    button_label,
                    key=(
                        f"theme_an_"
                        f"{theme_index}_"
                        f"{i}_"
                        f"{item_etf['code']}"
                    ),
                    use_container_width=True
                ):

                    if is_open:

                        st.session_state.future_detail_code = None

                        st.session_state.future_detail_theme = None

                    else:

                        st.session_state.future_detail_code = (
                            item_etf["code"]
                        )

                        st.session_state.future_detail_theme = theme

                    st.rerun()

                if (
                    st.session_state.future_detail_code
                    == item_etf["code"]
                ):

                    render_future_inline_analysis()

    # --------------------------------------------------------
    # 테마 요약
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '테마 요약'
        '</div>',
        unsafe_allow_html=True
    )

    for rank, item in enumerate(
        themes,
        start=1
    ):

        stage_cls = future_stage_class(
            item["stage"]
        )

        ret_cls = (
            "positive"
            if item["avg20"] >= 0
            else "negative"
        )

        st.markdown(
            f"""
            <div class="theme-summary-card">

                <div class="theme-stage-wrap">
                    <span class="theme-stage-badge {stage_cls}">
                        {esc(item["stage"])}
                    </span>
                </div>

                <div class="theme-summary-title">
                    {rank}. {esc(item["theme"])}
                </div>

                <div class="theme-summary-meta">

                    테마점수
                    <strong>
                        {item["score"]:.1f}
                    </strong>

                    · 5일
                    {item["avg5"]:+.2f}%

                    · 20일
                    <span class="{ret_cls}">
                        {item["avg20"]:+.2f}%
                    </span>

                    · 60일
                    {item["avg60"]:+.2f}%

                    · RSI
                    {item["avg_rsi"]:.1f}

                    · 거래량
                    {item["avg_vol"]:.2f}배

                </div>

                <div class="theme-summary-outlook">

                    상승확산
                    {item["breadth"]:.0f}%

                    · 추세확산
                    {item["trend_breadth"]:.0f}%

                    · 시장대비
                    {item["relative20"]:+.2f}%p

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# MARKET RADAR
# ============================================================

def radar_theme_for(
    code,
    name
):

    code = str(code).upper()

    text = (
        f"{code} {name}"
        .lower()
    )

    for theme, info in (
        THEME_LIBRARY.items()
    ):

        seed_codes = [
            str(x).upper()
            for x in info["seeds"]
        ]

        if (
            code in seed_codes
            or any(
                k.lower() in text
                for k in info["keywords"]
            )
        ):
            return theme

    return "기타"


def radar_stage_for(
    theme,
    engine
):

    for item in engine.get(
        "themes",
        []
    ):

        if item["theme"] == theme:
            return item["stage"]

    return "기타"


def radar_score(row):

    score = 0

    if row["above20"]:
        score += 12

    if row["above60"]:
        score += 13

    rs20 = row["rs20"]

    if rs20 >= 5:
        score += 20

    elif rs20 >= 2:
        score += 16

    elif rs20 > 0:
        score += 11

    elif rs20 > -3:
        score += 5

    vr = row["vr"]

    if 1.15 <= vr <= 2.0:
        score += 15

    elif 1.0 <= vr < 1.15:
        score += 9

    elif vr > 2.0:
        score += 7

    r20 = row["ret20"]

    if 2 <= r20 <= 15:
        score += 12

    elif 0 <= r20 < 2:
        score += 8

    elif r20 > 15:
        score += 5

    r5 = row["ret5"]

    if -2 <= r5 <= 5:
        score += 8

    elif 5 < r5 <= 8:
        score += 4

    rsi = row["rsi"]

    if 50 <= rsi <= 68:
        score += 12

    elif (
        45 <= rsi < 50
        or 68 < rsi <= 72
    ):
        score += 7

    elif (
        rsi < 40
        or rsi > 78
    ):
        score += 2

    dist = row["dist20"]

    if dist <= 4:
        score += 8

    elif dist <= 7:
        score += 5

    elif dist <= 10:
        score += 2

    return int(
        min(
            100,
            max(0, score)
        )
    )


def radar_overheat_score(row):

    score = 0

    if row["rsi"] >= 75:
        score += 30

    elif row["rsi"] >= 70:
        score += 22

    elif row["rsi"] >= 67:
        score += 10

    if row["ret5"] >= 10:
        score += 25

    elif row["ret5"] >= 7:
        score += 18

    elif row["ret5"] >= 5:
        score += 10

    if row["dist20"] >= 12:
        score += 25

    elif row["dist20"] >= 8:
        score += 18

    elif row["dist20"] >= 5:
        score += 8

    if row["vr"] >= 2.0:
        score += 20

    elif row["vr"] >= 1.5:
        score += 14

    elif row["vr"] >= 1.2:
        score += 7

    return int(
        min(
            100,
            score
        )
    )


def radar_target_etfs():

    targets = {}

    # 보유 ETF
    for raw_code in (
        st.session_state
        .holdings
        .keys()
    ):

        code = _normalize_etf_code(
            raw_code
        )

        if not code:
            continue

        name = get_etf_name(code)

        if (
            not name
            or name.startswith("ETF ")
        ):
            name = lookup_live_etf(
                code
            )

        targets[code] = name

    # 미래테마 ETF
    for theme in THEME_LIBRARY:

        try:

            for item in theme_candidates(
                theme
            ):

                code = _normalize_etf_code(
                    item.get("code")
                )

                name = (
                    item.get("name")
                    or get_etf_name(code)
                )

                if (
                    code
                    and name
                    and not str(name).startswith("ETF ")
                ):

                    targets[code] = name

        except Exception:
            continue

    return targets


def build_radar_data(
    force=False
):

    now = datetime.now()

    cached = (
        st.session_state.radar_cache
    )

    targets = radar_target_etfs()

    target_key = tuple(
        sorted(targets.keys())
    )

    if cached and not force:

        try:

            age = (
                now - cached["time"]
            ).total_seconds()

            if (
                age < 300
                and cached.get(
                    "target_key"
                ) == target_key
                and "rows" in cached
            ):
                return cached

        except Exception:
            pass

    benchmark = get_benchmark_metrics()

    engine = build_future_theme_engine()

    rows = []

    for code, target_name in (
        targets.items()
    ):

        name = (
            target_name
            or get_etf_name(code)
        )

        if (
            not name
            or str(name).startswith("ETF ")
        ):
            continue

        df = load_price_data(code)

        if (
            df.empty
            or len(df) < 65
        ):
            continue

        try:

            d = calculate_indicators(df)

            if d.empty:
                continue

            r = d.iloc[-1]

        except Exception:
            continue

        current = safe_float(
            r["Close"]
        )

        ma20 = safe_float(
            r["MA20"],
            current
        )

        ma60 = safe_float(
            r["MA60"],
            current
        )

        item = {
            "code": code,
            "name": name,
            "price": current,
            "rsi": safe_float(
                r["RSI14"],
                50
            ),
            "vr": safe_float(
                r["VOL_RATIO"],
                1
            ),
            "ret5": safe_float(
                r["RET5"],
                0
            ),
            "ret20": safe_float(
                r["RET20"],
                0
            ),
            "ret60": safe_float(
                r["RET60"],
                0
            ),
            "dist20":
                (
                    current / ma20 - 1
                ) * 100
                if ma20
                else 0,
            "above20":
                current >= ma20,
            "above60":
                current >= ma60,
        }

        item["rs20"] = (
            item["ret20"]
            - benchmark["ret20"]
        )

        item["theme"] = radar_theme_for(
            code,
            name
        )

        item["stage"] = radar_stage_for(
            item["theme"],
            engine
        )

        item["opportunity"] = (
            radar_score(item)
        )

        item["overheat"] = (
            radar_overheat_score(item)
        )

        item["held"] = (
            code
            in st.session_state.holdings
        )

        rows.append(item)

    data = {
        "time": now,
        "rows": rows,
        "benchmark": benchmark,
        "target_key": target_key
    }

    st.session_state.radar_cache = data

    return data


def render_radar_card(
    item,
    mode
):

    if mode == "🎯 기회검색":

        score = item["opportunity"]

        badge = "기회 후보"

        title = (
            "강세는 확인되지만 "
            "단기 추격 위험은 상대적으로 낮은 후보"
        )

    else:

        score = item["overheat"]

        badge = "과열 주의"

        title = (
            "단기 상승폭·RSI·이격·거래량을 함께 확인"
        )

    held = (
        " · 보유중"
        if item["held"]
        else ""
    )

    ret5_cls = (
        "positive"
        if item["ret5"] >= 0
        else "negative"
    )

    ret20_cls = (
        "positive"
        if item["ret20"] >= 0
        else "negative"
    )

    rs_cls = (
        "positive"
        if item["rs20"] >= 0
        else "negative"
    )

    theme_text = (
        f'{item["theme"]} · {item["stage"]}'
        if item["theme"] != "기타"
        else "테마 미분류"
    )

    position = (
        "20/60일선 위"
        if (
            item["above20"]
            and item["above60"]
        )
        else (
            "20일선 위 · 60일선 아래"
            if item["above20"]
            else "20일선 아래"
        )
    )

    st.markdown(
        f"""
        <div class="radar-card">

            <span class="radar-badge">
                {esc(badge)}
            </span>

            <span style="
                font-size:.62rem;
                color:#7890a4;
                margin-left:6px;
            ">
                {esc(held)}
            </span>

            <div class="radar-title">
                {esc(item["name"])}
                · {esc(item["code"])}
            </div>

            <div class="radar-sub">
                {esc(title)}
                · {esc(theme_text)}
            </div>

            <div class="radar-grid">

                <div class="radar-metric">
                    <div class="radar-label">
                        레이더 점수
                    </div>
                    <div class="radar-value">
                        {score}
                    </div>
                </div>

                <div class="radar-metric">
                    <div class="radar-label">
                        현재가
                    </div>
                    <div class="radar-value">
                        {money(item["price"])}
                    </div>
                </div>

                <div class="radar-metric">
                    <div class="radar-label">
                        5일 / 20일
                    </div>
                    <div class="radar-value">
                        <span class="{ret5_cls}">
                            {item["ret5"]:+.2f}%
                        </span>
                        /
                        <span class="{ret20_cls}">
                            {item["ret20"]:+.2f}%
                        </span>
                    </div>
                </div>

                <div class="radar-metric">
                    <div class="radar-label">
                        RSI / 거래량
                    </div>
                    <div class="radar-value">
                        {item["rsi"]:.1f}
                        /
                        {item["vr"]:.2f}배
                    </div>
                </div>

            </div>

            <div style="
                font-size:.67rem;
                color:#74899c;
                margin-top:9px;
            ">

                상대강도
                <span class="{rs_cls}">
                    {item["rs20"]:+.2f}%p
                </span>

                · 20일선 대비
                <strong>
                    {item["dist20"]:+.1f}%
                </strong>

                · {position}

            </div>

            <div style="
                font-size:.61rem;
                color:#62798c;
                margin-top:7px;
            ">
                점수는 신호를 정렬하기 위한
                스크리닝 지표이며 수익을 보장하지 않습니다.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def render_market_radar():

    st.markdown(
        """
        <div class="section-title">
            🔥 시장 레이더
        </div>

        <div style="
            color:#8196aa;
            font-size:.73rem;
            margin-bottom:12px;
        ">
            거래량 · 추세 · 상대강도 · 과열을
            한 화면에서 확인합니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns([1, 1])

    with c1:

        if st.button(
            "🔄 레이더 새로고침",
            use_container_width=True,
            key="radar_refresh"
        ):

            st.session_state.radar_cache = None

            st.session_state.price_cache = {}

            st.session_state.theme_cache = {}

            st.session_state.theme_engine_cache = None

            st.rerun()

    with c2:

        st.caption(
            "레이더는 내 ETF + 미래테마 ETF를 분석합니다. "
            "결과는 5분 캐시로 재사용합니다."
        )

    radar_modes = [
        "🎯 기회검색",
        "⚠️ 과열검색",
        "🔄 테마순환"
    ]

    if hasattr(
        st,
        "segmented_control"
    ):

        mode = st.segmented_control(
            "레이더 모드",
            options=radar_modes,
            default=st.session_state.get(
                "radar_mode",
                radar_modes[0]
            ),
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

        mode = st.session_state.get(
            "radar_mode",
            radar_modes[0]
        )

    with st.spinner(
        "시장 레이더 데이터를 계산하는 중입니다…"
    ):

        data = build_radar_data()

    rows = data["rows"]

    if not rows:

        st.warning(
            "레이더에 사용할 가격 데이터가 없습니다."
        )

        return

    # --------------------------------------------------------
    # 테마 순환
    # --------------------------------------------------------

    if mode == "🔄 테마순환":

        st.markdown(
            "### 테마순환"
        )

        engine = build_future_theme_engine()

        stage_map = {
            x["theme"]: x["stage"]
            for x in engine["themes"]
        }

        theme_rows = []

        for theme in THEME_LIBRARY:

            members = [
                x
                for x in rows
                if x["theme"] == theme
            ]

            if not members:
                continue

            vals5 = [
                x["ret5"]
                for x in members
                if np.isfinite(
                    x["ret5"]
                )
            ]

            vals20 = [
                x["ret20"]
                for x in members
                if np.isfinite(
                    x["ret20"]
                )
            ]

            valsvr = [
                x["vr"]
                for x in members
                if np.isfinite(
                    x["vr"]
                )
            ]

            if (
                not vals5
                or not vals20
                or not valsvr
            ):
                continue

            avg5 = float(
                np.mean(vals5)
            )

            avg20 = float(
                np.mean(vals20)
            )

            avgvr = float(
                np.mean(valsvr)
            )

            breadth = (
                sum(
                    1
                    for x in members
                    if x["ret5"] >= 0
                )
                / len(members)
                * 100
            )

            strength = (
                avg5 * 0.45
                + avg20 * 0.25
                + (avgvr - 1) * 10
                + breadth * 0.10
            )

            theme_rows.append({
                "theme": theme,
                "stage":
                    stage_map.get(
                        theme,
                        "기타"
                    ),
                "avg5": avg5,
                "avg20": avg20,
                "avgvr": avgvr,
                "breadth": breadth,
                "strength": strength,
                "n": len(members)
            })

        theme_rows.sort(
            key=lambda x:
                x["strength"],
            reverse=True
        )

        for x in theme_rows:

            cls = (
                "positive"
                if x["avg5"] >= 0
                else "negative"
            )

            st.markdown(
                f"""
                <div class="radar-card">

                    <span class="radar-badge">
                        {esc(x["stage"])}
                    </span>

                    <div class="radar-title">
                        {esc(x["theme"])}
                    </div>

                    <div class="radar-sub">
                        구성 {x["n"]}개
                        · 단기 상승 비율
                        {x["breadth"]:.0f}%
                    </div>

                    <div class="radar-grid">

                        <div class="radar-metric">
                            <div class="radar-label">
                                5일 평균
                            </div>
                            <div class="radar-value {cls}">
                                {x["avg5"]:+.2f}%
                            </div>
                        </div>

                        <div class="radar-metric">
                            <div class="radar-label">
                                20일 평균
                            </div>
                            <div class="radar-value">
                                {x["avg20"]:+.2f}%
                            </div>
                        </div>

                        <div class="radar-metric">
                            <div class="radar-label">
                                거래량
                            </div>
                            <div class="radar-value">
                                {x["avgvr"]:.2f}배
                            </div>
                        </div>

                        <div class="radar-metric">
                            <div class="radar-label">
                                상승비율
                            </div>
                            <div class="radar-value">
                                {x["breadth"]:.0f}%
                            </div>
                        </div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        st.caption(
            "테마순환은 각 테마 구성 ETF의 평균 수익률·"
            "거래량·상승 종목 비율을 이용한 상대 비교입니다."
        )

        return

    # --------------------------------------------------------
    # 기회검색
    # --------------------------------------------------------

    if mode == "🎯 기회검색":

        candidates = [
            x
            for x in rows
            if (
                x["opportunity"] >= 55
                and x["rsi"] < 72
                and x["ret5"] < 8
            )
        ]

        candidates.sort(
            key=lambda x: (
                x["opportunity"],
                x["rs20"]
            ),
            reverse=True
        )

        st.markdown(
            "### 아직 안 오른 강세 후보"
        )

        st.caption(
            "상승 추세 + 상대강도 + 거래량을 보면서 "
            "최근 단기 급등과 과도한 이격은 감점합니다. "
            "매수 신호가 아니라 추적 우선순위를 정하는 화면입니다."
        )

        if not candidates:

            st.info(
                "현재 조건을 동시에 만족하는 후보가 없습니다."
            )

        for item in candidates[:10]:

            render_radar_card(
                item,
                mode
            )

    # --------------------------------------------------------
    # 과열검색
    # --------------------------------------------------------

    else:

        candidates = [
            x
            for x in rows
            if x["overheat"] >= 35
        ]

        candidates.sort(
            key=lambda x: (
                x["overheat"],
                x["ret5"]
            ),
            reverse=True
        )

        st.markdown(
            "### 단기 과열 후보"
        )

        st.caption(
            "RSI·단기 상승률·20일선 이격·"
            "거래량 급증을 함께 확인합니다. "
            "과열은 상승 지속 여부와 별개의 경고 신호입니다."
        )

        if not candidates:

            st.info(
                "현재 과열 조건을 강하게 충족하는 ETF가 없습니다."
            )

        for item in candidates[:10]:

            render_radar_card(
                item,
                mode
            )


# ============================================================
# MAIN
# ============================================================

init_state()

st.markdown(
    """
    <div style="
        padding:4px 2px 10px;
    ">

        <div style="
            font-size:1.45rem;
            font-weight:950;
            color:#f3f8fc;
        ">
            ETF RADAR
        </div>

        <div style="
            color:#74899d;
            font-size:.73rem;
            margin-top:3px;
        ">
            ETF 추세 · 모멘텀 · 거래량 ·
            핵심가격 · 미래테마 · 시장레이더
        </div>

    </div>
    """,
    unsafe_allow_html=True
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