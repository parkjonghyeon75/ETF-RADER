import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timedelta


# ============================================================
# ETF RADAR v11
# ------------------------------------------------------------
# 1. 관심/보유 ETF 매매 가이드
# 2. 익절 / 손실관리 / 추격위험
# 3. 자동 지지 / 저항 / 매물대
# 4. 미래 유망 테마 탐색
# 5. 모바일 금융앱 UI
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📡",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ============================================================
# PREMIUM MOBILE UI
# ============================================================

st.markdown("""
<style>

:root {
    --bg: #f5f7fb;
    --card: #ffffff;
    --text: #111827;
    --muted: #64748b;
    --line: #e2e8f0;
    --blue: #2563eb;
    --blue2: #eff6ff;
    --green: #16a34a;
    --green2: #f0fdf4;
    --red: #dc2626;
    --red2: #fff1f2;
    --orange: #d97706;
    --orange2: #fffbeb;
    --purple: #7c3aed;
}

.stApp {
    background:
        linear-gradient(
            180deg,
            #f8fafc 0%,
            #f5f7fb 50%,
            #eef2f7 100%
        );
    color: var(--text);
}

.block-container {
    max-width: 760px;
    padding-top: 0.55rem;
    padding-bottom: 4rem;
    padding-left: 0.65rem;
    padding-right: 0.65rem;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

html, body, [class*="css"] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        Helvetica,
        Arial,
        sans-serif;
}


/* ============================================================
   HEADER
   ============================================================ */

.top-brand {
    padding: 0.35rem 0.15rem 0.75rem;
}

.brand-small {
    color: #2563eb;
    font-size: 0.75rem;
    font-weight: 950;
    letter-spacing: 0.15em;
}

.brand-main {
    color: #0f172a;
    font-size: 1.65rem;
    font-weight: 950;
    letter-spacing: -0.05em;
    margin-top: 2px;
}

.brand-sub {
    color: #64748b;
    font-size: 0.82rem;
    margin-top: 3px;
    font-weight: 650;
}


/* ============================================================
   TABS
   ============================================================ */

div[data-baseweb="tab-list"] {
    gap: 5px;
    background: #e2e8f0;
    padding: 4px;
    border-radius: 13px;
    margin-bottom: 12px;
}

button[data-baseweb="tab"] {
    border-radius: 9px !important;
    font-size: 0.88rem !important;
    font-weight: 850 !important;
    color: #475569 !important;
    padding: 0.55rem 0.35rem !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: #ffffff !important;
    color: #0f172a !important;
    box-shadow: 0 2px 8px rgba(15,23,42,0.08);
}


/* ============================================================
   CARD
   ============================================================ */

.card {
    background: rgba(255,255,255,0.98);
    border: 1px solid #dbe3ed;
    border-radius: 15px;
    padding: 15px;
    margin: 8px 0;
    box-shadow: 0 3px 12px rgba(15,23,42,0.045);
}

.card-title {
    color: #64748b;
    font-size: 0.72rem;
    font-weight: 900;
    letter-spacing: 0.07em;
}

.section-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 18px 2px 8px;
}

.section-title {
    font-size: 1rem;
    font-weight: 950;
    color: #0f172a;
    letter-spacing: -0.025em;
}

.section-caption {
    color: #94a3b8;
    font-size: 0.68rem;
    font-weight: 800;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {
    background:
        radial-gradient(
            circle at 100% 0%,
            rgba(37,99,235,0.12),
            transparent 38%
        ),
        #ffffff;

    border: 1px solid #d7e0ea;
    border-radius: 17px;
    padding: 17px;
    margin: 8px 0;
    box-shadow: 0 5px 17px rgba(15,23,42,0.055);
}

.hero-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
}

.hero-name {
    font-size: 1.06rem;
    font-weight: 950;
    color: #0f172a;
    line-height: 1.35;
}

.hero-code {
    font-size: 0.72rem;
    color: #94a3b8;
    margin-top: 2px;
    font-weight: 750;
}

.hero-price {
    font-size: 2.35rem;
    line-height: 1;
    font-weight: 950;
    letter-spacing: -0.06em;
    color: #0f172a;
    margin-top: 12px;
}

.hero-unit {
    font-size: 0.9rem;
    font-weight: 850;
}

.hero-change {
    font-size: 0.9rem;
    font-weight: 900;
    margin-top: 7px;
}

.hero-date {
    color: #94a3b8;
    font-size: 0.68rem;
    margin-top: 6px;
    font-weight: 650;
}

.hero-mini {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 11px;
    padding: 7px 10px;
    min-width: 80px;
    text-align: center;
}

.hero-mini-label {
    font-size: 0.66rem;
    color: #64748b;
    font-weight: 850;
}

.hero-mini-value {
    font-size: 1rem;
    color: #0f172a;
    font-weight: 950;
    margin-top: 2px;
}


/* ============================================================
   DECISION CARD
   ============================================================ */

.decision {
    border-radius: 15px;
    padding: 16px;
    margin: 8px 0;
    border: 1px solid;
}

.decision-title {
    font-size: 0.72rem;
    font-weight: 900;
    letter-spacing: 0.08em;
}

.decision-main {
    font-size: 1.28rem;
    font-weight: 950;
    color: #111827;
    margin-top: 4px;
    line-height: 1.35;
}

.decision-desc {
    color: #334155;
    font-size: 0.82rem;
    line-height: 1.55;
    margin-top: 7px;
    font-weight: 650;
}

.decision-green {
    background: #f0fdf4;
    border-color: #bbf7d0;
}

.decision-blue {
    background: #eff6ff;
    border-color: #bfdbfe;
}

.decision-yellow {
    background: #fffbeb;
    border-color: #fde68a;
}

.decision-red {
    background: #fff1f2;
    border-color: #fecdd3;
}


/* ============================================================
   SCORE
   ============================================================ */

.score-card {
    background: #ffffff;
    border: 1px solid #dbe3ed;
    border-radius: 15px;
    padding: 14px;
    min-height: 145px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 0 3px 12px rgba(15,23,42,0.045);
}

.score-number {
    font-size: 2.25rem;
    line-height: 1;
    font-weight: 950;
}

.score-denom {
    color: #94a3b8;
    font-size: 0.68rem;
    margin-top: 3px;
    font-weight: 750;
}

.score-label {
    margin-top: 7px;
    font-size: 0.8rem;
    font-weight: 900;
    text-align: center;
}

.signal-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 7px;
    margin-top: 8px;
}

.signal {
    background: #f8fafc;
    border: 1px solid #e5eaf0;
    border-radius: 10px;
    padding: 9px;
}

.signal-title {
    font-size: 0.67rem;
    color: #64748b;
    font-weight: 800;
}

.signal-value {
    font-size: 0.78rem;
    font-weight: 950;
    margin-top: 3px;
    line-height: 1.25;
}

.signal-good { color: #15803d; }
.signal-warn { color: #d97706; }
.signal-bad { color: #dc2626; }
.signal-blue { color: #2563eb; }


/* ============================================================
   POSITION
   ============================================================ */

.position-card {
    background: #0f172a;
    color: white;
    border-radius: 15px;
    padding: 15px;
    margin: 8px 0;
}

.position-label {
    color: #94a3b8;
    font-size: 0.68rem;
    font-weight: 850;
}

.position-value {
    font-size: 1.18rem;
    font-weight: 950;
    margin-top: 3px;
}

.position-sub {
    color: #cbd5e1;
    font-size: 0.72rem;
    margin-top: 4px;
    font-weight: 650;
}


/* ============================================================
   PRICE MAP
   ============================================================ */

.price-map {
    background: #ffffff;
    border: 1px solid #dbe3ed;
    border-radius: 15px;
    padding: 12px 15px;
}

.price-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid #f1f5f9;
}

.price-row:last-child {
    border-bottom: none;
}

.price-name {
    font-size: 0.76rem;
    font-weight: 800;
    color: #64748b;
}

.price-number {
    font-size: 0.95rem;
    font-weight: 950;
}


/* ============================================================
   MOMENTUM
   ============================================================ */

.momentum-card {
    background: #ffffff;
    border: 1px solid #dbe3ed;
    border-radius: 13px;
    padding: 12px;
    min-height: 102px;
}

.momentum-title {
    color: #64748b;
    font-size: 0.68rem;
    font-weight: 850;
}

.momentum-value {
    color: #0f172a;
    font-size: 1.15rem;
    font-weight: 950;
    margin-top: 5px;
}

.momentum-sub {
    color: #64748b;
    font-size: 0.68rem;
    margin-top: 4px;
    font-weight: 700;
    line-height: 1.3;
}


/* ============================================================
   THEME RADAR
   ============================================================ */

.theme-hero {
    background:
        radial-gradient(
            circle at 100% 0%,
            rgba(124,58,237,0.15),
            transparent 40%
        ),
        #ffffff;
    border: 1px solid #ddd6fe;
    border-radius: 17px;
    padding: 17px;
}

.theme-card {
    background: #ffffff;
    border: 1px solid #dbe3ed;
    border-radius: 14px;
    padding: 14px;
    margin: 7px 0;
    box-shadow: 0 2px 8px rgba(15,23,42,0.035);
}

.theme-rank {
    color: #7c3aed;
    font-size: 0.68rem;
    font-weight: 950;
    letter-spacing: 0.08em;
}

.theme-name {
    color: #111827;
    font-size: 1rem;
    font-weight: 950;
    margin-top: 3px;
}

.theme-score {
    font-size: 1.35rem;
    font-weight: 950;
    color: #7c3aed;
}

.theme-reason {
    color: #475569;
    font-size: 0.72rem;
    font-weight: 700;
    line-height: 1.45;
    margin-top: 7px;
}


/* ============================================================
   MISC
   ============================================================ */

.pattern-box {
    background: linear-gradient(135deg, #eef5ff, #f8fafc);
    border: 1px solid #bfdbfe;
    border-radius: 15px;
    padding: 14px;
}

.pattern-title {
    color: #2563eb;
    font-size: 0.68rem;
    font-weight: 900;
    letter-spacing: 0.07em;
}

.pattern-main {
    color: #0f172a;
    font-size: 1.08rem;
    font-weight: 950;
    margin-top: 5px;
    line-height: 1.4;
}

.pattern-desc {
    color: #334155;
    font-size: 0.79rem;
    margin-top: 7px;
    line-height: 1.5;
    font-weight: 650;
}

.score-breakdown {
    background: #f8fafc;
    border: 1px solid #dbe3ed;
    border-radius: 13px;
    padding: 12px;
}

.score-line {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    font-size: 0.76rem;
}

.score-line-label {
    color: #64748b;
    font-weight: 700;
}

.score-line-value {
    font-weight: 950;
    color: #111827;
}

div[data-testid="stExpander"] {
    border: 1px solid #dbe3ed !important;
    border-radius: 13px !important;
    background: #ffffff !important;
    overflow: hidden;
}

.stButton > button {
    border-radius: 11px !important;
    font-weight: 900 !important;
    min-height: 42px !important;
    font-size: 0.86rem !important;
}

button[kind="primary"] {
    background: #2563eb !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 11px;
    overflow: hidden;
}

@media (max-width: 480px) {

    .block-container {
        padding-left: 0.45rem;
        padding-right: 0.45rem;
    }

    .hero-price {
        font-size: 2.15rem;
    }

    .section-title {
        font-size: 0.94rem;
    }

    .hero {
        padding: 14px;
    }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# FILES
# ============================================================

WATCHLIST_FILE = "watchlist.json"
THEME_FILE = "theme_info.json"
POSITION_FILE = "position_info.json"


# ============================================================
# ETF UNIVERSE
# ============================================================

ETF_POOLS = {

    "🇺🇸 미국 S&P500 / 대형주": {
        "360750": "TIGER 미국S&P500",
        "379800": "KODEX 미국S&P500TR",
        "448290": "SOL 미국S&P500"
    },

    "🇺🇸 미국 나스닥 / AI": {
        "133690": "TIGER 미국나스닥100",
        "379810": "KODEX 미국나스닥100TR",
        "487240": "KODEX 미국AI테크TOP10",
        "452330": "TIGER 미국테크TOP10"
    },

    "🤖 AI 반도체 / HBM": {
        "395160": "KODEX AI반도체TOP2플러스",
        "462100": "TIGER AI반도체핵심공정",
        "441680": "SOL 미국AI반도체",
        "486410": "TIGER 미국반도체TOP10"
    },

    "⚡ AI 전력 / 원전": {
        "471990": "KODEX AI전력핵심설비",
        "445380": "SOL 원자력TOP3플러스",
        "465560": "TIGER 글로벌원자력"
    },

    "🔋 2차전지": {
        "305540": "KODEX 2차전지산업",
        "364980": "TIGER 2차전지소부장",
        "438320": "KODEX 2차전지핵심소재"
    },

    "🚀 우주 / 로봇": {
        "465610": "KODEX 로봇산업",
        "476250": "TIGER 우주항공&로봇"
    },

    "💊 바이오 / 헬스케어": {
        "329200": "TIGER 헬스케어",
        "266420": "KODEX 바이오",
        "462610": "ARIRANG 3대주주바이오"
    },

    "💰 미국 배당": {
        "458730": "TIGER 미국배당다우존스",
        "441680": "SOL 미국배당다우존스",
        "476480": "KODEX 미국배당커버드콜",
        "451780": "TIGER 미국배당+7%프리미엄"
    },

    "🛡 안전자산 / 채권": {
        "423160": "KODEX CD금리활성(합성)",
        "449170": "TIGER KOFR금리액티브",
        "308620": "KODEX 미국채울트라30년선물",
        "365780": "TIGER 미국채30년스트립액티브"
    }
}


DEFAULT_WATCHLIST = {
    "395160": "KODEX AI반도체TOP2플러스 (395160)",
    "487240": "KODEX 미국AI테크TOP10 (487240)",
    "471990": "KODEX AI전력핵심설비 (471990)",
    "133690": "TIGER 미국나스닥100 (133690)",
    "360750": "TIGER 미국S&P500 (360750)",
    "458730": "TIGER 미국배당다우존스 (458730)"
}


DEFAULT_THEME_INFO = {

    "395160": {
        "theme": "AI 반도체 / HBM",
        "cycle": "성장·확장",
        "desc": "AI 서버 투자와 고대역폭메모리 수요의 영향을 받는 반도체 테마입니다.",
        "long_view": "AI 데이터센터 투자와 메모리 업황의 방향이 핵심 변수입니다."
    },

    "487240": {
        "theme": "미국 AI 빅테크",
        "cycle": "성장",
        "desc": "AI 플랫폼과 빅테크 기업 중심의 성장 테마입니다.",
        "long_view": "AI 서비스 수익화와 기업 실적 증가 여부가 중요합니다."
    },

    "471990": {
        "theme": "AI 전력 인프라",
        "cycle": "확장",
        "desc": "데이터센터 증가에 필요한 전력망·변압기·발전 인프라 관련 테마입니다.",
        "long_view": "데이터센터 전력수요와 전력 인프라 투자 확대가 핵심입니다."
    },

    "133690": {
        "theme": "미국 나스닥100",
        "cycle": "장기 성장",
        "desc": "미국 대형 기술기업 중심의 대표 성장지수입니다.",
        "long_view": "미국 기술주 실적과 금리 환경의 영향을 크게 받습니다."
    },

    "360750": {
        "theme": "미국 S&P500",
        "cycle": "장기 성장",
        "desc": "미국 대표 대형주 지수를 추종합니다.",
        "long_view": "미국 기업 실적과 경기 사이클이 핵심 변수입니다."
    },

    "458730": {
        "theme": "미국 배당 성장",
        "cycle": "안정적 성장",
        "desc": "미국 우량 배당기업에 투자하는 ETF입니다.",
        "long_view": "배당 성장과 금리 수준이 중요한 변수입니다."
    }
}


# ============================================================
# FUTURE THEME DISCOVERY
# ============================================================

DISCOVERY_THEMES = {

    "AI 데이터센터": [
        "AI 데이터센터",
        "데이터센터",
        "AI 서버",
        "GPU 서버"
    ],

    "AI 전력 인프라": [
        "AI 전력",
        "데이터센터 전력",
        "전력망",
        "변압기",
        "전력 인프라"
    ],

    "HBM / AI 반도체": [
        "HBM",
        "AI 반도체",
        "고대역폭메모리",
        "첨단 패키징"
    ],

    "원전 / SMR": [
        "SMR",
        "소형모듈원전",
        "원자력",
        "원전 수출"
    ],

    "휴머노이드 로봇": [
        "휴머노이드",
        "휴머노이드 로봇",
        "로봇",
        "AI 로봇"
    ],

    "우주항공": [
        "우주항공",
        "위성",
        "우주 산업",
        "발사체"
    ],

    "방산": [
        "방산",
        "K방산",
        "무기 수출",
        "방위산업"
    ],

    "바이오 / 비만치료": [
        "비만치료제",
        "GLP-1",
        "바이오",
        "신약"
    ],

    "2차전지 차세대": [
        "전고체 배터리",
        "배터리",
        "2차전지",
        "ESS"
    ],

    "광통신 / 데이터 전송": [
        "광통신",
        "데이터센터 광통신",
        "광트랜시버",
        "광모듈"
    ]
}


# ============================================================
# JSON
# ============================================================

def load_json_file(path, default):

    if os.path.exists(path):

        try:

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, type(default)):
                return data

        except Exception:
            pass

    return default.copy()


def save_json_file(path, data):

    try:

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception:
        pass


if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_json_file(
        WATCHLIST_FILE,
        DEFAULT_WATCHLIST
    )


if "theme_info" not in st.session_state:
    st.session_state.theme_info = load_json_file(
        THEME_FILE,
        DEFAULT_THEME_INFO
    )


if "positions" not in st.session_state:
    st.session_state.positions = load_json_file(
        POSITION_FILE,
        {}
    )


# ============================================================
# NETWORK
# ============================================================

def http_get(url, timeout=8):

    try:

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        )

        with urllib.request.urlopen(
            req,
            timeout=timeout
        ) as response:

            return response.read()

    except Exception:
        return None


# ============================================================
# NAVER ETF SEARCH
# ============================================================

def search_stock_code_by_keyword(keyword):

    try:

        encoded = urllib.parse.quote(keyword)

        url = (
            "https://ac.stock.naver.com/ac"
            f"?q={encoded}&target=etf"
        )

        raw = http_get(url, 7)

        if raw:

            data = json.loads(
                raw.decode("utf-8")
            )

            items = data.get("items", [])

            if items:

                return (
                    str(items[0][0]),
                    str(items[0][1])
                )

    except Exception:
        pass

    return None, None


def get_stock_name(code):

    try:

        url = (
            f"https://m.stock.naver.com/"
            f"api/stock/{code}/basic"
        )

        raw = http_get(url, 7)

        if raw:

            data = json.loads(
                raw.decode("utf-8")
            )

            return data.get(
                "stockName",
                f"ETF {code}"
            )

    except Exception:
        pass

    return f"ETF {code}"


# ============================================================
# NAVER CHART
# ============================================================

def fetch_from_naver(code, count=500):

    try:

        url = (
            "https://fchart.stock.naver.com/"
            "sise.nhn?"
            f"symbol={urllib.parse.quote(code)}"
            "&timeframe=day"
            f"&count={count}"
            "&requestType=0"
        )

        raw = http_get(url, 10)

        if not raw:
            return None

        xml_data = raw.decode(
            "euc-kr",
            errors="ignore"
        )

        root = ET.fromstring(xml_data)

        rows = []

        for item in root.findall(".//item"):

            parts = item.attrib.get(
                "data",
                ""
            ).split("|")

            if len(parts) >= 6:

                try:

                    rows.append({
                        "Date": pd.to_datetime(parts[0]),
                        "Open": float(parts[1]),
                        "High": float(parts[2]),
                        "Low": float(parts[3]),
                        "Close": float(parts[4]),
                        "Volume": float(parts[5])
                    })

                except Exception:
                    continue

        if not rows:
            return None

        df = pd.DataFrame(rows)

        df = (
            df
            .drop_duplicates("Date")
            .set_index("Date")
            .sort_index()
        )

        return df

    except Exception:
        return None


# ============================================================
# YFINANCE
# ============================================================

def fetch_from_yfinance(code):

    for suffix in [".KS", ".KQ"]:

        try:

            data = yf.download(
                f"{code}{suffix}",
                period="2y",
                progress=False,
                auto_adjust=False,
                threads=False
            )

            if data is None or data.empty:
                continue

            if isinstance(
                data.columns,
                pd.MultiIndex
            ):

                data.columns = [
                    c[0]
                    for c in data.columns
                ]

            needed = [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume"
            ]

            if not all(
                c in data.columns
                for c in needed
            ):
                continue

            data = data[needed].copy()

            data.index = pd.to_datetime(
                data.index
            )

            data = data.dropna(
                subset=["Close"]
            )

            if len(data) >= 20:
                return data

        except Exception:
            continue

    return None


# ============================================================
# LOAD ETF DATA
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner=False
)
def load_etf_data(
    ticker_code,
    period="1y"
):

    clean_code = re.sub(
        r"[^0-9A-Za-z]",
        "",
        str(ticker_code)
    )

    if not clean_code:
        clean_code = str(ticker_code).strip()

    df = fetch_from_naver(
        clean_code,
        600
    )

    source = "Naver"

    if df is None or df.empty:

        df = fetch_from_yfinance(
            clean_code
        )

        source = "Yahoo Finance"

    if df is None or df.empty:

        return None, clean_code, None

    if period == "6m":
        df = df.iloc[-130:]

    elif period == "1y":
        df = df.iloc[-260:]

    else:
        df = df.iloc[-500:]

    return (
        df.copy(),
        clean_code,
        source
    )


# ============================================================
# INDICATORS
# ============================================================

def calculate_indicators(df):

    df = df.copy()

    for n in [5, 20, 60, 120]:
        df[f"MA{n}"] = (
            df["Close"]
            .rolling(n)
            .mean()
        )

    delta = df["Close"].diff()

    gain = (
        delta.clip(lower=0)
        .rolling(14)
        .mean()
    )

    loss = (
        (-delta.clip(upper=0))
        .rolling(14)
        .mean()
    )

    rs = gain / loss.replace(
        0,
        np.nan
    )

    df["RSI"] = (
        100 -
        (100 / (1 + rs))
    )

    ema12 = (
        df["Close"]
        .ewm(
            span=12,
            adjust=False
        )
        .mean()
    )

    ema26 = (
        df["Close"]
        .ewm(
            span=26,
            adjust=False
        )
        .mean()
    )

    df["MACD"] = ema12 - ema26

    df["MACD_Signal"] = (
        df["MACD"]
        .ewm(
            span=9,
            adjust=False
        )
        .mean()
    )

    df["MACD_Hist"] = (
        df["MACD"] -
        df["MACD_Signal"]
    )

    df["BB_Mid"] = df["MA20"]

    std20 = (
        df["Close"]
        .rolling(20)
        .std()
    )

    df["BB_Upper"] = (
        df["BB_Mid"] +
        2 * std20
    )

    df["BB_Lower"] = (
        df["BB_Mid"] -
        2 * std20
    )

    df["Vol_MA20"] = (
        df["Volume"]
        .rolling(20)
        .mean()
    )

    df["Vol_Ratio"] = (
        df["Volume"] /
        df["Vol_MA20"].replace(
            0,
            np.nan
        )
    )

    # ATR
    prev_close = df["Close"].shift(1)

    tr = pd.concat(
        [
            df["High"] - df["Low"],
            (df["High"] - prev_close).abs(),
            (df["Low"] - prev_close).abs()
        ],
        axis=1
    ).max(axis=1)

    df["ATR14"] = (
        tr.rolling(14).mean()
    )

    # MA20 이격
    df["MA20_Distance"] = (
        df["Close"] /
        df["MA20"] - 1
    ) * 100

    # 최근 수익률
    df["Return5"] = (
        df["Close"]
        .pct_change(5) * 100
    )

    df["Return20"] = (
        df["Close"]
        .pct_change(20) * 100
    )

    return df


# ============================================================
# SUPPORT / RESISTANCE
# ============================================================

def get_support_resistance(df):

    current = float(
        df["Close"].iloc[-1]
    )

    candidates_support = []
    candidates_resist = []

    # Moving averages
    for col in [
        "MA20",
        "MA60",
        "MA120"
    ]:

        if (
            col in df.columns and
            pd.notna(df[col].iloc[-1])
        ):

            value = float(
                df[col].iloc[-1]
            )

            if value < current:
                candidates_support.append(
                    (value, 2, col)
                )

            elif value > current:
                candidates_resist.append(
                    (value, 2, col)
                )

    # Recent swing levels
    for window in [20, 60]:

        if len(df) >= window:

            section = df.iloc[-window:]

            low = float(
                section["Low"].min()
            )

            high = float(
                section["High"].max()
            )

            if low < current:
                candidates_support.append(
                    (
                        low,
                        3 if window == 20 else 2,
                        f"{window}D Low"
                    )
                )

            if high > current:
                candidates_resist.append(
                    (
                        high,
                        3 if window == 20 else 2,
                        f"{window}D High"
                    )
                )

    def cluster(items):

        if not items:
            return []

        items = sorted(
            items,
            key=lambda x: x[0]
        )

        groups = []

        for item in items:

            if not groups:

                groups.append(
                    [item]
                )

            else:

                last_price = np.mean(
                    [x[0] for x in groups[-1]]
                )

                if (
                    abs(item[0] - last_price)
                    / max(last_price, 1)
                    <= 0.015
                ):

                    groups[-1].append(
                        item
                    )

                else:

                    groups.append(
                        [item]
                    )

        result = []

        for group in groups:

            price = np.mean(
                [x[0] for x in group]
            )

            strength = sum(
                x[1] for x in group
            )

            source = ", ".join(
                x[2] for x in group
            )

            result.append({
                "price": price,
                "strength": strength,
                "source": source
            })

        return result

    supports = cluster(
        candidates_support
    )

    resistances = cluster(
        candidates_resist
    )

    supports = sorted(
        supports,
        key=lambda x: x["price"],
        reverse=True
    )[:3]

    resistances = sorted(
        resistances,
        key=lambda x: x["price"]
    )[:3]

    return supports, resistances


# ============================================================
# VOLUME PROFILE
# ============================================================

def volume_profile(
    df,
    bins=24
):

    data = (
        df.iloc[-120:]
        if len(df) >= 120
        else df
    )

    low = float(
        data["Low"].min()
    )

    high = float(
        data["High"].max()
    )

    if high <= low:
        return pd.DataFrame(
            columns=[
                "price",
                "volume",
                "ratio"
            ]
        )

    edges = np.linspace(
        low,
        high,
        bins + 1
    )

    volumes = np.zeros(bins)

    typical = (
        data["High"] +
        data["Low"] +
        data["Close"]
    ) / 3

    for price, vol in zip(
        typical,
        data["Volume"]
    ):

        idx = (
            np.searchsorted(
                edges,
                price,
                side="right"
            ) - 1
        )

        idx = min(
            max(idx, 0),
            bins - 1
        )

        volumes[idx] += float(vol)

    prices = (
        edges[:-1] +
        edges[1:]
    ) / 2

    vp = pd.DataFrame({
        "price": prices,
        "volume": volumes
    })

    vmax = max(
        vp["volume"].max(),
        1
    )

    vp["ratio"] = (
        vp["volume"] / vmax
    )

    return vp.sort_values(
        "volume",
        ascending=False
    ).reset_index(drop=True)


# ============================================================
# TECHNICAL SCORE
# ============================================================

def technical_score(df):

    x = df.iloc[-1]

    score = 0
    breakdown = {}

    close = float(x["Close"])
    ma20 = x["MA20"]
    ma60 = x["MA60"]
    rsi = x["RSI"]
    macd = x["MACD"]
    sig = x["MACD_Signal"]
    vol = x["Vol_Ratio"]

    # Trend 25
    trend = 0

    if pd.notna(ma20) and close > ma20:
        trend += 12

    if (
        pd.notna(ma20)
        and pd.notna(ma60)
        and ma20 > ma60
    ):
        trend += 13

    breakdown["추세"] = trend
    score += trend

    # Momentum 20
    momentum = 0

    if (
        pd.notna(macd)
        and pd.notna(sig)
        and macd > sig
    ):
        momentum += 10

    if (
        pd.notna(x["MACD_Hist"])
        and x["MACD_Hist"] > 0
    ):
        momentum += 10

    breakdown["MACD 모멘텀"] = momentum
    score += momentum

    # RSI 15
    rsi_score = 0

    if pd.notna(rsi):

        if 50 <= rsi < 65:
            rsi_score = 15

        elif 45 <= rsi < 50:
            rsi_score = 11

        elif 65 <= rsi < 70:
            rsi_score = 10

        elif 35 <= rsi < 45:
            rsi_score = 7

        elif rsi >= 70:
            rsi_score = 4

        else:
            rsi_score = 3

    breakdown["RSI"] = rsi_score
    score += rsi_score

    # Volume 15
    volume_score = 0

    if pd.notna(vol):

        if 1.2 <= vol <= 2.5:
            volume_score = 15

        elif 0.9 <= vol < 1.2:
            volume_score = 9

        elif vol > 2.5:
            volume_score = 10

        else:
            volume_score = 4

    breakdown["거래량"] = volume_score
    score += volume_score

    # Price location 15
    location = 0

    if pd.notna(ma20):

        distance = (
            close / ma20 - 1
        ) * 100

        if -2 <= distance <= 3:
            location = 15

        elif 3 < distance <= 6:
            location = 10

        elif distance < -5:
            location = 5

        else:
            location = 7

    breakdown["가격 위치"] = location
    score += location

    # Short-term confirmation 10
    confirm = 0

    if len(df) >= 6:

        r5 = (
            df["Close"].iloc[-1]
            /
            df["Close"].iloc[-6]
            - 1
        ) * 100

        if 0 < r5 <= 8:
            confirm = 10

        elif r5 > 8:
            confirm = 6

        elif -3 <= r5 <= 0:
            confirm = 6

        else:
            confirm = 3

    breakdown["단기 흐름"] = confirm
    score += confirm

    score = int(
        max(
            0,
            min(
                100,
                score
            )
        )
    )

    if score >= 80:
        label = "상승 추세 우세"

    elif score >= 65:
        label = "상승 가능성 우세"

    elif score >= 50:
        label = "중립 / 확인 필요"

    elif score >= 35:
        label = "조정 / 방어 필요"

    else:
        label = "약세 / 리스크 관리"

    return (
        score,
        label,
        breakdown
    )


# ============================================================
# CHASE RISK
# ============================================================

def chase_risk(df):

    x = df.iloc[-1]

    close = float(x["Close"])
    ma20 = x["MA20"]
    rsi = x["RSI"]
    vol = x["Vol_Ratio"]
    ret5 = x["Return5"]

    risk = 0
    reasons = []

    if (
        pd.notna(rsi)
        and rsi >= 70
    ):

        risk += 40
        reasons.append(
            "RSI 70 이상 과열"
        )

    elif (
        pd.notna(rsi)
        and rsi >= 65
    ):

        risk += 20
        reasons.append(
            "RSI 상승 과열 접근"
        )

    if pd.notna(ma20):

        distance = (
            close / ma20 - 1
        ) * 100

        if distance >= 8:

            risk += 35
            reasons.append(
                "20일선 대비 8% 이상 이격"
            )

        elif distance >= 5:

            risk += 20
            reasons.append(
                "20일선 대비 이격 확대"
            )

    if pd.notna(vol):

        if vol >= 2.5:

            risk += 20
            reasons.append(
                "거래량 급증"
            )

        elif vol >= 1.8:

            risk += 10
            reasons.append(
                "거래량 증가"
            )

    if pd.notna(ret5):

        if ret5 >= 12:

            risk += 20
            reasons.append(
                "5거래일 급등"
            )

        elif ret5 >= 7:

            risk += 10
            reasons.append(
                "단기 상승 속도 빠름"
            )

    risk = min(
        100,
        risk
    )

    if risk >= 70:

        label = "높음"
        css = "signal-bad"

    elif risk >= 40:

        label = "주의"
        css = "signal-warn"

    else:

        label = "낮음"
        css = "signal-good"

    return (
        risk,
        label,
        css,
        reasons
    )


# ============================================================
# PATTERN ENGINE
# ============================================================

def detect_patterns(
    df,
    supports,
    resistances
):

    x = df.iloc[-1]

    close = float(x["Close"])
    ma20 = x["MA20"]
    ma60 = x["MA60"]
    rsi = x["RSI"]
    macd = x["MACD"]
    sig = x["MACD_Signal"]
    vol = x["Vol_Ratio"]

    patterns = []

    previous_high = (
        float(
            df.iloc[-21:-1]["High"].max()
        )
        if len(df) >= 22
        else float(
            df["High"].max()
        )
    )

    # Breakout
    if (
        close > previous_high
        and pd.notna(vol)
        and vol >= 1.4
        and pd.notna(macd)
        and pd.notna(sig)
        and macd > sig
    ):

        patterns.append(
            "🚀 거래량 동반 돌파"
        )

    # Pullback
    if (
        pd.notna(ma20)
        and pd.notna(ma60)
        and pd.notna(rsi)
        and ma20 > ma60
        and 42 <= rsi <= 65
        and 0.98 <= close / ma20 <= 1.025
    ):

        patterns.append(
            "💡 상승 추세 눌림목"
        )

    # Overheated
    if (
        pd.notna(rsi)
        and rsi >= 70
    ):

        patterns.append(
            "⚠️ 단기 과열"
        )

    # Weakening
    if (
        pd.notna(ma20)
        and close < ma20
        and pd.notna(macd)
        and pd.notna(sig)
        and macd < sig
    ):

        patterns.append(
            "🔻 단기 추세 약화"
        )

    if not patterns:

        if (
            pd.notna(ma20)
            and close > ma20
        ):

            patterns.append(
                "📈 상승 추세 유지"
            )

        else:

            patterns.append(
                "💤 방향성 확인 필요"
            )

    return patterns


# ============================================================
# EXIT / ENTRY SCENARIO
# ============================================================

def build_trade_plan(
    df,
    score,
    supports,
    resistances,
    patterns,
    chase_score,
    entry_price=None
):

    x = df.iloc[-1]

    current = float(
        x["Close"]
    )

    ma20 = (
        float(x["MA20"])
        if pd.notna(x["MA20"])
        else current
    )

    atr = (
        float(x["ATR14"])
        if pd.notna(x["ATR14"])
        else current * 0.03
    )

    s1 = (
        supports[0]["price"]
        if supports
        else ma20
    )

    s2 = (
        supports[1]["price"]
        if len(supports) >= 2
        else s1 - atr
    )

    r1 = (
        resistances[0]["price"]
        if resistances
        else current + atr
    )

    r2 = (
        resistances[1]["price"]
        if len(resistances) >= 2
        else current + atr * 2
    )

    # 돌파 확인선
    breakout = (
        max(
            current,
            r1
        )
    )

    # 손실관리선
    stop = min(
        s2,
        ma20 - atr * 0.5
    )

    if stop >= current:
        stop = current - atr

    # ========================================================
    # 1. 보유단가가 있는 경우
    # ========================================================

    pnl = None

    if (
        entry_price is not None
        and entry_price > 0
    ):

        pnl = (
            current /
            entry_price - 1
        ) * 100

    # ========================================================
    # SELL / HOLD 판단
    # ========================================================

    if pnl is not None:

        if (
            current < stop
            and score < 45
        ):

            action = "손실관리 검토"

            color = "red"

            title = (
                "핵심 지지선 이탈"
            )

            desc = (
                f"현재가는 {current:,.0f}원이며 "
                f"핵심 방어선 {stop:,.0f}원 아래로 "
                "밀릴 경우 추세 훼손으로 보고 "
                "손실을 제한하는 대응을 검토할 구간입니다."
            )

        elif (
            pnl >= 12
            and (
                chase_score >= 60
                or rsi_value(df) >= 70
            )
        ):

            action = "익절 / 비중축소 검토"

            color = "yellow"

            title = (
                "수익 확보를 우선 검토할 구간"
            )

            desc = (
                f"현재 수익률은 +{pnl:.1f}%입니다. "
                "단기 과열 신호가 동시에 나타나고 있어 "
                "전량 매도보다는 일부 익절 또는 "
                "비중 조절을 검토할 수 있는 구간입니다."
            )

        elif (
            current >= r1
            and score >= 70
        ):

            action = "1차 익절선 접근"

            color = "yellow"

            title = (
                "저항선에서 수익 확보 여부 확인"
            )

            desc = (
                f"현재가가 1차 저항선 {r1:,.0f}원에 "
                "접근하고 있습니다. "
                "돌파가 확인되지 않는다면 일부 익절을 "
                "검토할 수 있습니다."
            )

        elif (
            score >= 65
            and current >= ma20
        ):

            action = "보유 유지"

            color = "green"

            title = (
                "상승 추세 유지"
            )

            desc = (
                f"현재가는 20일선 {ma20:,.0f}원 위에 있고 "
                "기술적 추세가 유지되고 있습니다. "
                f"{stop:,.0f}원 부근이 무너지기 전까지는 "
                "추세를 따라가는 시나리오입니다."
            )

        else:

            action = "보유 / 확인"

            color = "blue"

            title = (
                "추세 확인 구간"
            )

            desc = (
                f"현재가는 {current:,.0f}원입니다. "
                "즉각적인 매도보다 "
                f"{s1:,.0f}원 지지 여부와 "
                f"{r1:,.0f}원 돌파 여부를 확인하는 "
                "것이 중요한 구간입니다."
            )

    # ========================================================
    # 신규 진입
    # ========================================================

    else:

        if chase_score >= 70:

            action = "추격매수 자제"

            color = "red"

            title = (
                "가격이 너무 빠르게 올라간 상태"
            )

            desc = (
                f"현재가 {current:,.0f}원에서 "
                "추격 진입하기보다 "
                f"{s1:,.0f}원 부근의 눌림과 "
                "거래량 감소 후 재상승을 확인하는 "
                "시나리오가 적합합니다."
            )

        elif (
            "💡 상승 추세 눌림목"
            in patterns
        ):

            action = "눌림목 관심"

            color = "green"

            title = (
                "상승 추세 안에서 매수 관심 구간"
            )

            desc = (
                f"{s1:,.0f}~{current:,.0f}원 구간의 "
                "지지 확인이 핵심입니다. "
                "한 번에 진입하기보다 분할 접근을 "
                "검토할 수 있는 위치입니다."
            )

        elif (
            "🚀 거래량 동반 돌파"
            in patterns
        ):

            action = "돌파 확인"

            color = "blue"

            title = (
                "저항 돌파가 발생한 상태"
            )

            desc = (
                f"{breakout:,.0f}원 위에서 "
                "가격이 유지되는지 확인합니다. "
                "돌파 직후 급등한 경우에는 "
                "재차 눌림을 기다리는 것도 중요합니다."
            )

        else:

            action = "관망 / 가격 대기"

            color = "yellow"

            title = (
                "아직 명확한 진입 신호 부족"
            )

            desc = (
                f"{s1:,.0f}원 지지 또는 "
                f"{breakout:,.0f}원 돌파 중 하나가 "
                "확인될 때까지 기다리는 구간입니다."
            )

    return {
        "action": action,
        "color": color,
        "title": title,
        "desc": desc,
        "s1": s1,
        "s2": s2,
        "r1": r1,
        "r2": r2,
        "stop": stop,
        "breakout": breakout,
        "pnl": pnl
    }


def rsi_value(df):

    value = df["RSI"].iloc[-1]

    if pd.isna(value):
        return 50

    return float(value)


# ============================================================
# CHART
# ============================================================

def make_main_chart(
    df,
    supports,
    resistances
):

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.035,
        row_heights=[
            0.60,
            0.22,
            0.18
        ]
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            increasing_line_color="#16a34a",
            decreasing_line_color="#dc2626",
            name="가격"
        ),
        row=1,
        col=1
    )

    ma_colors = {
        "MA5": "#f59e0b",
        "MA20": "#2563eb",
        "MA60": "#16a34a",
        "MA120": "#7c3aed"
    }

    for col, color in ma_colors.items():

        if col in df.columns:

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    line=dict(
                        color=color,
                        width=1.5
                    ),
                    name=col
                ),
                row=1,
                col=1
            )

    for i, item in enumerate(
        supports[:2],
        1
    ):

        fig.add_hline(
            y=item["price"],
            row=1,
            col=1,
            line_dash="dot",
            line_color="#16a34a",
            annotation_text=f"S{i}"
        )

    for i, item in enumerate(
        resistances[:2],
        1
    ):

        fig.add_hline(
            y=item["price"],
            row=1,
            col=1,
            line_dash="dash",
            line_color="#dc2626",
            annotation_text=f"R{i}"
        )

    volume_colors = [
        "#16a34a"
        if c >= o
        else "#dc2626"
        for c, o in zip(
            df["Close"],
            df["Open"]
        )
    ]

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            marker_color=volume_colors,
            name="거래량"
        ),
        row=2,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["RSI"],
            line=dict(
                color="#2563eb",
                width=2
            ),
            name="RSI"
        ),
        row=3,
        col=1
    )

    fig.add_hline(
        y=70,
        row=3,
        col=1,
        line_dash="dot",
        line_color="#dc2626"
    )

    fig.add_hline(
        y=30,
        row=3,
        col=1,
        line_dash="dot",
        line_color="#16a34a"
    )

    fig.update_layout(
        height=630,
        margin=dict(
            l=3,
            r=3,
            t=5,
            b=5
        ),
        template="plotly_white",
        showlegend=False,
        xaxis_rangeslider_visible=False,
        dragmode=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Arial",
            size=10,
            color="#475569"
        )
    )

    fig.update_xaxes(
        showgrid=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#edf1f5",
        fixedrange=True
    )

    return fig


# ============================================================
# SCORE DETAILS
# ============================================================

def get_signal_details(df):

    x = df.iloc[-1]

    close = float(x["Close"])
    ma20 = x["MA20"]
    ma60 = x["MA60"]
    rsi = x["RSI"]
    macd = x["MACD"]
    sig = x["MACD_Signal"]
    vol = x["Vol_Ratio"]

    if (
        pd.notna(ma20)
        and pd.notna(ma60)
        and close > ma20
        and ma20 > ma60
    ):
        trend = "상승 정배열"
        trend_cls = "signal-good"

    elif (
        pd.notna(ma20)
        and close > ma20
    ):
        trend = "단기 상승"
        trend_cls = "signal-good"

    elif pd.notna(ma20):

        trend = "20일선 아래"
        trend_cls = "signal-bad"

    else:

        trend = "판단 보류"
        trend_cls = "signal-warn"

    if pd.isna(rsi):

        rsi_state = "계산중"

    elif rsi >= 70:

        rsi_state = "과열"

    elif rsi >= 50:

        rsi_state = "상승 모멘텀"

    elif rsi >= 30:

        rsi_state = "중립"

    else:

        rsi_state = "침체"

    if (
        pd.notna(macd)
        and pd.notna(sig)
        and macd > sig
    ):

        macd_state = "상승 모멘텀"

    else:

        macd_state = "둔화"

    if pd.isna(vol):

        volume_state = "계산중"

    elif vol >= 1.5:

        volume_state = "거래량 유입"

    elif vol >= 1:

        volume_state = "평균 수준"

    else:

        volume_state = "거래량 감소"

    return (
        trend,
        trend_cls,
        rsi_state,
        macd_state,
        volume_state
    )


# ============================================================
# THEME: ETF TECHNICAL SCORE
# ============================================================

def analyze_etf_basic(
    code,
    name
):

    raw, _, _ = load_etf_data(
        code,
        "6m"
    )

    if raw is None or len(raw) < 30:
        return None

    df = calculate_indicators(
        raw
    )

    score, label, breakdown = technical_score(
        df
    )

    x = df.iloc[-1]
    prev = df.iloc[-2]

    change = (
        float(x["Close"]) /
        float(prev["Close"]) - 1
    ) * 100

    return {
        "code": code,
        "name": name,
        "score": score,
        "label": label,
        "change": change,
        "price": float(x["Close"]),
        "rsi": float(x["RSI"])
        if pd.notna(x["RSI"])
        else 50,
        "volume": float(x["Vol_Ratio"])
        if pd.notna(x["Vol_Ratio"])
        else 1,
        "return20": float(x["Return20"])
        if pd.notna(x["Return20"])
        else 0
    }


# ============================================================
# MARKET THEME SCAN
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def scan_market_themes():

    results = []

    for theme, pool in ETF_POOLS.items():

        items = []

        for code, name in pool.items():

            item = analyze_etf_basic(
                code,
                name
            )

            if item:
                items.append(item)

        if not items:
            continue

        avg_score = np.mean(
            [x["score"] for x in items]
        )

        avg_change = np.mean(
            [x["change"] for x in items]
        )

        avg_return20 = np.mean(
            [x["return20"] for x in items]
        )

        volume_hits = sum(
            1
            for x in items
            if x["volume"] >= 1.3
        )

        positive = sum(
            1
            for x in items
            if x["change"] > 0
        )

        breadth = (
            positive /
            len(items) *
            100
        )

        # 미래 선점 관점
        future_score = (
            avg_score * 0.45
            +
            max(
                0,
                min(
                    100,
                    50 + avg_return20 * 3
                )
            ) * 0.20
            +
            breadth * 0.20
            +
            min(
                100,
                volume_hits /
                len(items) * 100
            ) * 0.15
        )

        if (
            avg_return20 > 5
            and breadth >= 60
        ):

            phase = "상승 활성화"

        elif (
            avg_return20 > 0
            and breadth >= 45
        ):

            phase = "초기 관심"

        elif avg_return20 < -5:

            phase = "조정"

        else:

            phase = "관찰"

        results.append({
            "theme": theme,
            "score": future_score,
            "avg_score": avg_score,
            "avg_change": avg_change,
            "avg_return20": avg_return20,
            "breadth": breadth,
            "volume_hits": volume_hits,
            "count": len(items),
            "phase": phase,
            "etfs": sorted(
                items,
                key=lambda x:
                x["score"],
                reverse=True
            )
        })

    return sorted(
        results,
        key=lambda x:
        x["score"],
        reverse=True
    )


# ============================================================
# NEWS / KEYWORD DISCOVERY
# ============================================================

@st.cache_data(
    ttl=86400,
    show_spinner=False
)
def search_theme_news(keyword):

    try:

        encoded = urllib.parse.quote(
            keyword
        )

        url = (
            "https://search.naver.com/"
            "search.naver?"
            f"where=news&query={encoded}"
        )

        raw = http_get(
            url,
            8
        )

        if not raw:
            return 0

        text = raw.decode(
            "utf-8",
            errors="ignore"
        )

        # 검색결과 제목/본문에 반복되는
        # 키워드의 대략적 활성도
        count = len(
            re.findall(
                re.escape(keyword),
                text,
                flags=re.IGNORECASE
            )
        )

        return min(
            100,
            count
        )

    except Exception:
        return 0


@st.cache_data(
    ttl=86400,
    show_spinner=False
)
def discover_future_themes():

    discovered = []

    for theme, keywords in DISCOVERY_THEMES.items():

        signals = []

        for keyword in keywords:

            count = search_theme_news(
                keyword
            )

            signals.append(
                count
            )

        news_activity = sum(
            signals
        )

        # 현재 ETF 시장에서 연관되는
        # 테마 ETF 성과도 함께 확인
        matching = []

        for pool_name, pool in ETF_POOLS.items():

            for code, name in pool.items():

                for keyword in keywords:

                    if (
                        keyword.replace(
                            " ",
                            ""
                        )
                        in
                        name.replace(
                            " ",
                            ""
                        )
                    ):

                        item = analyze_etf_basic(
                            code,
                            name
                        )

                        if item:
                            matching.append(
                                item
                            )

                        break

        if matching:

            technical = np.mean(
                [
                    x["score"]
                    for x in matching
                ]
            )

            recent_return = np.mean(
                [
                    x["return20"]
                    for x in matching
                ]
            )

        else:

            technical = 50
            recent_return = 0

        news_score = min(
            100,
            news_activity * 1.5
        )

        # 미래 선점형 점수
        # 뉴스 활성 + 시장 반응 + 기술확산
        discovery_score = (
            news_score * 0.45
            +
            technical * 0.35
            +
            max(
                0,
                min(
                    100,
                    50 +
                    recent_return * 3
                )
            ) * 0.20
        )

        if discovery_score >= 70:

            phase = "🔥 급부상 탐색"

        elif discovery_score >= 55:

            phase = "🟣 선점 관찰"

        elif discovery_score >= 40:

            phase = "🔵 초기 관심"

        else:

            phase = "⚪ 관찰"

        discovered.append({
            "theme": theme,
            "score": discovery_score,
            "news": news_score,
            "technical": technical,
            "return20": recent_return,
            "phase": phase
        })

    return sorted(
        discovered,
        key=lambda x:
        x["score"],
        reverse=True
    )


# ============================================================
# SAFE HTML
# ============================================================

def html_escape(text):

    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="top-brand">
    <div class="brand-small">ETF RADAR</div>
    <div class="brand-main">투자 흐름을 읽다</div>
    <div class="brand-sub">
        보유종목 매매판단 · 미래 테마 탐색 · 가격대 분석
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# MAIN TABS
# ============================================================

tab_analysis, tab_theme = st.tabs(
    [
        "📊 내 ETF",
        "🔭 미래 테마"
    ]
)


# ============================================================
# TAB 1
# ============================================================

with tab_analysis:

    watchlist = (
        st.session_state.watchlist
    )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search_col1, search_col2 = st.columns(
        [3, 1]
    )

    with search_col1:

        keyword_input = st.text_input(
            "ETF 검색",
            placeholder="ETF명 또는 6자리 코드",
            label_visibility="collapsed",
            key="ind_search"
        )

    with search_col2:

        search_add_btn = st.button(
            "＋ 저장",
            use_container_width=True,
            key="ind_save_btn"
        )

    if (
        search_add_btn
        and keyword_input
    ):

        with st.spinner(
            "ETF를 검색하고 있습니다..."
        ):

            found_code, found_name = (
                search_stock_code_by_keyword(
                    keyword_input.strip()
                )
            )

            if not found_code:

                clean_test = re.sub(
                    r"\D",
                    "",
                    keyword_input.strip()
                )

                if len(clean_test) == 6:

                    test_df, _, _ = (
                        load_etf_data(
                            clean_test,
                            "6m"
                        )
                    )

                    if test_df is not None:

                        found_code = clean_test

                        found_name = (
                            get_stock_name(
                                clean_test
                            )
                        )

            if found_code:

                st.session_state.watchlist[
                    found_code
                ] = (
                    f"{found_name} "
                    f"({found_code})"
                )

                save_json_file(
                    WATCHLIST_FILE,
                    st.session_state.watchlist
                )

                if (
                    found_code
                    not in
                    st.session_state.theme_info
                ):

                    st.session_state.theme_info[
                        found_code
                    ] = {
                        "theme": "자동 탐색 필요",
                        "cycle": "탐색",
                        "desc":
                        "신규 등록 ETF입니다.",
                        "long_view":
                        "시장 테마와 기초자산 "
                        "흐름을 계속 확인합니다."
                    }

                    save_json_file(
                        THEME_FILE,
                        st.session_state.theme_info
                    )

                st.success(
                    f"{found_name} 저장 완료"
                )

                st.rerun()

            else:

                st.error(
                    "ETF를 찾지 못했습니다."
                )

    options = list(
        watchlist.values()
    )

    if not options:

        st.warning(
            "관심종목을 먼저 등록해 주세요."
        )

        st.stop()

    # --------------------------------------------------------
    # SELECT
    # --------------------------------------------------------

    c1, c2 = st.columns(
        [2.2, 1]
    )

    with c1:

        selected = st.selectbox(
            "관심 ETF",
            options,
            label_visibility="collapsed"
        )

    with c2:

        period = st.selectbox(
            "기간",
            ["6m", "1y", "2y"],
            index=1,
            label_visibility="collapsed"
        )

    symbol_input = next(
        (
            k
            for k, v in watchlist.items()
            if v == selected
        ),
        None
    )

    if symbol_input is None:
        st.stop()

    # --------------------------------------------------------
    # POSITION
    # --------------------------------------------------------

    existing_position = (
        st.session_state.positions
        .get(
            symbol_input,
            {}
        )
    )

    with st.expander(
        "💼 보유단가 입력 / 수정"
    ):

        p1, p2 = st.columns(2)

        with p1:

            entry_default = float(
                existing_position.get(
                    "entry_price",
                    0
                )
            )

            entry_price_input = st.number_input(
                "평균매수가",
                min_value=0.0,
                value=entry_default,
                step=100.0,
                format="%.0f"
            )

        with p2:

            quantity_default = int(
                existing_position.get(
                    "quantity",
                    0
                )
            )

            quantity_input = st.number_input(
                "보유수량",
                min_value=0,
                value=quantity_default,
                step=1
            )

        if st.button(
            "보유정보 저장",
            use_container_width=True
        ):

            if entry_price_input > 0:

                st.session_state.positions[
                    symbol_input
                ] = {
                    "entry_price":
                    entry_price_input,
                    "quantity":
                    quantity_input
                }

            else:

                st.session_state.positions.pop(
                    symbol_input,
                    None
                )

            save_json_file(
                POSITION_FILE,
                st.session_state.positions
            )

            st.success(
                "보유정보가 저장되었습니다."
            )

    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    with st.spinner(
        "시장 데이터를 분석하고 있습니다..."
    ):

        raw_df, code, source = (
            load_etf_data(
                symbol_input,
                period
            )
        )

    if raw_df is None:

        st.error(
            "시장 데이터를 불러오지 못했습니다."
        )

        st.stop()

    df = calculate_indicators(
        raw_df
    ).dropna(
        subset=["Close"]
    ).copy()

    if len(df) < 30:

        st.error(
            "기술적 분석에 필요한 데이터가 부족합니다."
        )

        st.stop()

    # --------------------------------------------------------
    # ANALYSIS
    # --------------------------------------------------------

    score, score_label, breakdown = (
        technical_score(df)
    )

    supports, resistances = (
        get_support_resistance(df)
    )

    vp = volume_profile(df)

    patterns = detect_patterns(
        df,
        supports,
        resistances
    )

    chase_score, chase_label, chase_class, chase_reasons = (
        chase_risk(df)
    )

    position = (
        st.session_state.positions
        .get(
            symbol_input,
            {}
        )
    )

    entry_price = (
        position.get(
            "entry_price"
        )
        if position
        else None
    )

    trade_plan = build_trade_plan(
        df,
        score,
        supports,
        resistances,
        patterns,
        chase_score,
        entry_price
    )

    x = df.iloc[-1]
    prev = df.iloc[-2]

    price = float(
        x["Close"]
    )

    change = (
        price /
        float(prev["Close"]) -
        1
    ) * 100

    rsi = (
        float(x["RSI"])
        if pd.notna(x["RSI"])
        else 50
    )

    vol_ratio = (
        float(x["Vol_Ratio"])
        if pd.notna(x["Vol_Ratio"])
        else 1
    )

    change_color = (
        "#16a34a"
        if change >= 0
        else "#dc2626"
    )

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="hero">

            <div class="hero-top">

                <div>

                    <div class="hero-name">
                        {html_escape(
                            selected.split(" (")[0]
                        )}
                    </div>

                    <div class="hero-code">
                        {code} · {source}
                    </div>

                </div>

                <div class="hero-mini">

                    <div class="hero-mini-label">
                        기술점수
                    </div>

                    <div class="hero-mini-value">
                        {score}
                    </div>

                </div>

            </div>

            <div class="hero-price">
                {price:,.0f}
                <span class="hero-unit">
                    원
                </span>
            </div>

            <div
                class="hero-change"
                style="color:{change_color};"
            >
                {"▲" if change >= 0 else "▼"}
                {abs(change):.2f}%
                <span
                    style="
                    color:#94a3b8;
                    font-size:0.7rem;
                    margin-left:6px;
                    "
                >
                    전일 대비
                </span>
            </div>

            <div class="hero-date">
                최근 거래일:
                {df.index[-1].strftime("%Y-%m-%d")}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # MAIN DECISION
    # --------------------------------------------------------

    color_map = {
        "green": (
            "decision-green",
            "#15803d"
        ),
        "blue": (
            "decision-blue",
            "#2563eb"
        ),
        "yellow": (
            "decision-yellow",
            "#b45309"
        ),
        "red": (
            "decision-red",
            "#dc2626"
        )
    }

    decision_cls, decision_color = (
        color_map[
            trade_plan["color"]
        ]
    )

    st.markdown(
        f"""
        <div class="decision {decision_cls}">

            <div
                class="decision-title"
                style="color:{decision_color};"
            >
                TODAY'S DECISION
            </div>

            <div class="decision-main">
                {trade_plan["action"]}
            </div>

            <div class="decision-desc">
                {trade_plan["desc"]}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # POSITION P/L
    # --------------------------------------------------------

    if (
        entry_price is not None
        and entry_price > 0
    ):

        pnl = trade_plan["pnl"]

        pnl_color = (
            "#16a34a"
            if pnl >= 0
            else "#dc2626"
        )

        st.markdown(
            f"""
            <div class="position-card">

                <div class="position-label">
                    MY POSITION
                </div>

                <div
                    class="position-value"
                    style="color:{pnl_color};"
                >
                    {"+" if pnl >= 0 else ""}
                    {pnl:.2f}%
                </div>

                <div class="position-sub">
                    평균매수가:
                    {entry_price:,.0f}원
                    · 현재가:
                    {price:,.0f}원
                </div>

                <div class="position-sub">
                    핵심 방어선:
                    {trade_plan["stop"]:,.0f}원
                    · 1차 목표:
                    {trade_plan["r1"]:,.0f}원
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # SCORE / SIGNAL
    # --------------------------------------------------------

    score_color = (
        "#16a34a"
        if score >= 65
        else (
            "#d97706"
            if score >= 45
            else "#dc2626"
        )
    )

    trend, trend_cls, rsi_state, macd_state, volume_state = (
        get_signal_details(df)
    )

    sc1, sc2 = st.columns(
        [0.82, 1.18]
    )

    with sc1:

        st.markdown(
            f"""
            <div class="score-card">

                <div
                    class="score-number"
                    style="color:{score_color};"
                >
                    {score}
                </div>

                <div class="score-denom">
                    / 100
                </div>

                <div
                    class="score-label"
                    style="color:{score_color};"
                >
                    {score_label}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with sc2:

        st.markdown(
            f"""
            <div class="card">

                <div class="card-title">
                    MARKET STATE
                </div>

                <div class="signal-grid">

                    <div class="signal">
                        <div class="signal-title">
                            추세
                        </div>
                        <div class="signal-value {trend_cls}">
                            {trend}
                        </div>
                    </div>

                    <div class="signal">
                        <div class="signal-title">
                            RSI
                        </div>
                        <div class="signal-value">
                            {rsi:.0f} · {rsi_state}
                        </div>
                    </div>

                    <div class="signal">
                        <div class="signal-title">
                            MACD
                        </div>
                        <div class="signal-value">
                            {macd_state}
                        </div>
                    </div>

                    <div class="signal">
                        <div class="signal-title">
                            거래량
                        </div>
                        <div class="signal-value">
                            {vol_ratio:.1f}x
                            · {volume_state}
                        </div>
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # CORE PRICE PLAN
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-head">
            <div class="section-title">
                🎯 핵심 대응 가격
            </div>
            <div class="section-caption">
                TRADE MAP
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    p1, p2 = st.columns(2)

    with p1:

        st.markdown(
            f"""
            <div class="decision decision-green">

                <div class="decision-title"
                     style="color:#15803d;">
                    🟢 관심 / 지지
                </div>

                <div class="decision-main">
                    {trade_plan["s1"]:,.0f}원
                </div>

                <div class="decision-desc">
                    1차 지지선.
                    이 가격에서 반등하는지 확인합니다.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with p2:

        st.markdown(
            f"""
            <div class="decision decision-red">

                <div class="decision-title"
                     style="color:#dc2626;">
                    🔴 손실관리 기준
                </div>

                <div class="decision-main">
                    {trade_plan["stop"]:,.0f}원
                </div>

                <div class="decision-desc">
                    이탈 시 상승 시나리오가 훼손될 수 있어
                    손실 제한을 검토합니다.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    p3, p4 = st.columns(2)

    with p3:

        st.markdown(
            f"""
            <div class="decision decision-yellow">

                <div class="decision-title"
                     style="color:#b45309;">
                    🟡 1차 익절 / 저항
                </div>

                <div class="decision-main">
                    {trade_plan["r1"]:,.0f}원
                </div>

                <div class="decision-desc">
                    상승 시 첫 번째로 확인할
                    차익실현 가격대입니다.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with p4:

        st.markdown(
            f"""
            <div class="decision decision-blue">

                <div class="decision-title"
                     style="color:#1d4ed8;">
                    🔵 2차 목표
                </div>

                <div class="decision-main">
                    {trade_plan["r2"]:,.0f}원
                </div>

                <div class="decision-desc">
                    1차 저항 돌파 후 다음으로
                    확인할 가격대입니다.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # PRICE MAP
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-head">
            <div class="section-title">
                🗺 가격 지도
            </div>
            <div class="section-caption">
                SUPPORT / RESISTANCE
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="price-map">

            <div class="price-row">
                <div class="price-name">
                    R2 · 2차 목표
                </div>
                <div
                    class="price-number"
                    style="color:#dc2626;"
                >
                    {trade_plan["r2"]:,.0f}원
                </div>
            </div>

            <div class="price-row">
                <div class="price-name">
                    R1 · 1차 익절 / 저항
                </div>
                <div
                    class="price-number"
                    style="color:#dc2626;"
                >
                    {trade_plan["r1"]:,.0f}원
                </div>
            </div>

            <div
                class="price-row"
                style="
                background:#eff6ff;
                margin:0 -8px;
                padding-left:8px;
                padding-right:8px;
                border-radius:8px;
                "
            >
                <div
                    class="price-name"
                    style="color:#2563eb;"
                >
                    NOW · 현재가
                </div>

                <div
                    class="price-number"
                    style="
                    color:#2563eb;
                    font-size:1.05rem;
                    "
                >
                    {price:,.0f}원
                </div>
            </div>

            <div class="price-row">
                <div class="price-name">
                    S1 · 1차 지지
                </div>
                <div
                    class="price-number"
                    style="color:#16a34a;"
                >
                    {trade_plan["s1"]:,.0f}원
                </div>
            </div>

            <div class="price-row">
                <div class="price-name">
                    S2 · 2차 지지
                </div>
                <div
                    class="price-number"
                    style="color:#16a34a;"
                >
                    {trade_plan["s2"]:,.0f}원
                </div>
            </div>

            <div class="price-row">
                <div class="price-name">
                    STOP · 추세 훼손 기준
                </div>
                <div
                    class="price-number"
                    style="color:#dc2626;"
                >
                    {trade_plan["stop"]:,.0f}원
                </div>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # PATTERN
    # --------------------------------------------------------

    pattern_main = patterns[0]

    if "눌림목" in pattern_main:

        pattern_desc = (
            "상승 추세가 유지되는 상태에서 "
            "20일선 주변까지 가격이 조정되는 패턴입니다. "
            "거래량 감소 후 반등이 확인되면 관심도가 높아집니다."
        )

    elif "돌파" in pattern_main:

        pattern_desc = (
            "직전 고점 또는 저항선을 거래량과 함께 "
            "상향 돌파한 상태입니다. "
            "돌파 가격을 다시 지지하는지가 핵심입니다."
        )

    elif "과열" in pattern_main:

        pattern_desc = (
            "단기간 상승 속도가 빠른 상태입니다. "
            "상승 자체보다 현재 가격에서 추가 진입할 "
            "여유가 있는지를 확인해야 합니다."
        )

    elif "약화" in pattern_main:

        pattern_desc = (
            "20일선과 MACD 흐름이 동시에 약해지고 있습니다. "
            "보유자는 반등 여부보다 핵심 지지선 방어 여부를 "
            "우선 확인해야 합니다."
        )

    else:

        pattern_desc = (
            "현재 추세와 모멘텀을 종합하면 "
            "뚜렷한 매매 신호보다 다음 가격 돌파 또는 "
            "지지 확인을 기다리는 구간입니다."
        )

    st.markdown(
        f"""
        <div class="section-head">
            <div class="section-title">
                🔎 현재 패턴
            </div>
            <div class="section-caption">
                PRICE ACTION
            </div>
        </div>

        <div class="pattern-box">

            <div class="pattern-title">
                CURRENT PATTERN
            </div>

            <div class="pattern-main">
                {pattern_main}
            </div>

            <div class="pattern-desc">
                {pattern_desc}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # CHASE RISK
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-head">
            <div class="section-title">
                ⚠️ 추격매수 위험
            </div>
            <div class="section-caption">
                CHASE RISK
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    risk_text = (
        " · ".join(chase_reasons)
        if chase_reasons
        else
        "현재 가격의 이격도가 과도하지 않습니다."
    )

    risk_cls = (
        "decision-red"
        if chase_score >= 70
        else (
            "decision-yellow"
            if chase_score >= 40
            else "decision-green"
        )
    )

    st.markdown(
        f"""
        <div class="decision {risk_cls}">

            <div class="decision-title">
                추격 위험 {chase_score}/100
            </div>

            <div class="decision-main">
                {chase_label}
            </div>

            <div class="decision-desc">
                {risk_text}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # CHART
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-head">
            <div class="section-title">
                📈 가격 흐름
            </div>
            <div class="section-caption">
                PRICE · VOLUME · RSI
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    fig = make_main_chart(
        df,
        supports,
        resistances
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "responsive": True,
            "displayModeBar": False,
            "scrollZoom": False
        },
        key=f"main_chart_{code}_{period}"
    )

    # --------------------------------------------------------
    # MOMENTUM
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-head">
            <div class="section-title">
                📊 핵심 모멘텀
            </div>
            <div class="section-caption">
                INDICATORS
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if rsi >= 70:

        rsi_desc = "과열 · 익절 주의"

    elif rsi >= 50:

        rsi_desc = "상승 모멘텀"

    elif rsi >= 30:

        rsi_desc = "중립"

    else:

        rsi_desc = "침체"

    if vol_ratio >= 1.5:

        vol_desc = "거래량 강하게 유입"

    elif vol_ratio >= 1:

        vol_desc = "평균 수준"

    else:

        vol_desc = "거래량 감소"

    macd_hist = (
        float(x["MACD_Hist"])
        if pd.notna(x["MACD_Hist"])
        else 0
    )

    macd_desc = (
        "상승 모멘텀 확대"
        if macd_hist > 0
        else "모멘텀 둔화"
    )

    i1, i2, i3 = st.columns(3)

    with i1:

        st.markdown(
            f"""
            <div class="momentum-card">
                <div class="momentum-title">
                    RSI
                </div>
                <div class="momentum-value">
                    {rsi:.1f}
                </div>
                <div class="momentum-sub">
                    {rsi_desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with i2:

        st.markdown(
            f"""
            <div class="momentum-card">
                <div class="momentum-title">
                    거래량
                </div>
                <div class="momentum-value">
                    {vol_ratio:.1f}x
                </div>
                <div class="momentum-sub">
                    {vol_desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with i3:

        st.markdown(
            f"""
            <div class="momentum-card">
                <div class="momentum-title">
                    MACD
                </div>
                <div class="momentum-value">
                    {"▲" if macd_hist > 0 else "▼"}
                </div>
                <div class="momentum-sub">
                    {macd_desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # DETAIL
    # --------------------------------------------------------

    detail_tabs = st.tabs(
        [
            "📍 매물대",
            "🏛 테마",
            "🧮 점수"
        ]
    )

    with detail_tabs[0]:

        st.markdown(
            "#### 최근 거래 집중 가격대"
        )

        if not vp.empty:

            vp_show = (
                vp.head(8)
                [["price", "ratio"]]
                .copy()
            )

            vp_show["가격"] = (
                vp_show["price"]
                .map(
                    lambda x:
                    f"{x:,.0f}원"
                )
            )

            vp_show["집중도"] = (
                vp_show["ratio"]
                .map(
                    lambda x:
                    f"{x * 100:.1f}%"
                )
            )

            st.dataframe(
                vp_show[
                    ["가격", "집중도"]
                ],
                use_container_width=True,
                hide_index=True
            )

        st.markdown(
            "#### 주요 지지 / 저항"
        )

        a, b = st.columns(2)

        with a:

            st.markdown(
                "**🟢 지지**"
            )

            for i, item in enumerate(
                supports[:3],
                1
            ):

                st.success(
                    f"S{i} · "
                    f"{item['price']:,.0f}원"
                )

        with b:

            st.markdown(
                "**🔴 저항**"
            )

            for i, item in enumerate(
                resistances[:3],
                1
            ):

                st.warning(
                    f"R{i} · "
                    f"{item['price']:,.0f}원"
                )

    with detail_tabs[1]:

        theme_info = (
            st.session_state.theme_info
            .get(
                code,
                {
                    "theme":
                    "자동 탐색 필요",
                    "cycle":
                    "탐색",
                    "desc":
                    "시장 테마를 분석합니다.",
                    "long_view":
                    "미래 테마 변화와 "
                    "기초자산 흐름을 확인합니다."
                }
            )
        )

        st.markdown(
            f"""
            <div class="card">

                <div class="card-title">
                    ETF THEME
                </div>

                <div
                    style="
                    font-size:1.12rem;
                    font-weight:950;
                    margin-top:5px;
                    "
                >
                    {theme_info["theme"]}
                </div>

                <div
                    style="
                    color:#2563eb;
                    font-size:0.75rem;
                    font-weight:900;
                    margin-top:5px;
                    "
                >
                    {theme_info["cycle"]}
                </div>

                <div
                    style="
                    color:#475569;
                    font-size:0.78rem;
                    line-height:1.55;
                    margin-top:8px;
                    "
                >
                    {theme_info["desc"]}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.info(
            theme_info["long_view"]
        )

    with detail_tabs[2]:

        st.markdown(
            "#### 100점 기술점수 구성"
        )

        breakdown_html = ""

        for label, value in breakdown.items():

            breakdown_html += f"""
            <div class="score-line">
                <div class="score-line-label">
                    {label}
                </div>
                <div class="score-line-value">
                    {value}점
                </div>
            </div>
            """

        st.markdown(
            f"""
            <div class="score-breakdown">
                {breakdown_html}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "점수는 매수 추천 점수가 아니라 현재 추세·모멘텀·거래량·가격위치를 종합한 기술적 상태 점수입니다."
        )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    with st.expander(
        "⚙ 관심종목 관리"
    ):

        if st.button(
            "🗑 현재 ETF 삭제",
            use_container_width=True
        ):

            st.session_state.watchlist.pop(
                symbol_input,
                None
            )

            st.session_state.positions.pop(
                symbol_input,
                None
            )

            save_json_file(
                WATCHLIST_FILE,
                st.session_state.watchlist
            )

            save_json_file(
                POSITION_FILE,
                st.session_state.positions
            )

            st.rerun()


# ============================================================
# TAB 2 : FUTURE THEME RADAR
# ============================================================

with tab_theme:

    st.markdown(
        """
        <div class="theme-hero">

            <div class="card-title">
                FUTURE THEME RADAR
            </div>

            <div
                style="
                font-size:1.35rem;
                font-weight:950;
                margin-top:5px;
                "
            >
                아직 시장이 완전히 몰리기 전,
                다음 테마를 찾습니다.
            </div>

            <div
                style="
                color:#475569;
                font-size:0.79rem;
                line-height:1.55;
                margin-top:8px;
                font-weight:650;
                "
            >
                테마의 최근 가격 흐름만 보는 것이 아니라
                뉴스 활성도와 ETF 기술적 확산을 함께 확인하여
                관심 테마를 탐색합니다.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-head">
            <div class="section-title">
                🔭 미래 테마 탐색
            </div>
            <div class="section-caption">
                DAILY DISCOVERY
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "하루 한 번 '새로고침'하면 최신 데이터 기준으로 다시 탐색할 수 있습니다."
    )

    b1, b2 = st.columns(2)

    with b1:

        if st.button(
            "🔄 시장 데이터 새로고침",
            use_container_width=True,
            type="primary"
        ):

            st.cache_data.clear()
            st.rerun()

    with b2:

        if st.button(
            "🔭 미래 테마 재탐색",
            use_container_width=True
        ):

            discover_future_themes.clear()
            scan_market_themes.clear()
            st.rerun()

    # --------------------------------------------------------
    # CURRENT ETF THEME MOMENTUM
    # --------------------------------------------------------

    with st.spinner(
        "현재 ETF 시장의 테마 확산 상태를 분석 중입니다..."
    ):

        theme_results = (
            scan_market_themes()
        )

    if theme_results:

        st.markdown(
            """
            <div class="section-head">
                <div class="section-title">
                    📡 ETF 테마 활성도
                </div>
                <div class="section-caption">
                    MARKET MOMENTUM
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        top = theme_results[0]

        st.markdown(
            f"""
            <div class="theme-card">

                <div class="theme-rank">
                    CURRENT MOMENTUM
                </div>

                <div class="theme-name">
                    {top["theme"]}
                </div>

                <div
                    style="
                    margin-top:8px;
                    "
                >
                    <span class="theme-score">
                        {top["score"]:.1f}
                    </span>
                    <span
                        style="
                        color:#94a3b8;
                        font-size:0.7rem;
                        "
                    >
                        / 100
                    </span>
                </div>

                <div class="theme-reason">
                    최근 20일 평균:
                    {"+" if top["avg_return20"] >= 0 else ""}
                    {top["avg_return20"]:.1f}%
                    · 상승 ETF 비율:
                    {top["breadth"]:.0f}%
                    · 거래량 활성:
                    {top["volume_hits"]}개
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        for rank, item in enumerate(
            theme_results,
            1
        ):

            with st.expander(
                f"{rank:02d} · "
                f"{item['theme']} · "
                f"{item['phase']}"
            ):

                st.markdown(
                    f"""
                    <div class="theme-card">

                        <div class="theme-name">
                            {item["theme"]}
                        </div>

                        <div
                            style="
                            display:flex;
                            justify-content:space-between;
                            margin-top:8px;
                            "
                        >

                            <div>
                                <div
                                    style="
                                    color:#64748b;
                                    font-size:0.67rem;
                                    "
                                >
                                    테마 활성도
                                </div>

                                <div class="theme-score">
                                    {item["score"]:.1f}
                                </div>
                            </div>

                            <div
                                style="
                                text-align:right;
                                "
                            >

                                <div
                                    style="
                                    color:#64748b;
                                    font-size:0.67rem;
                                    "
                                >
                                    20일 평균
                                </div>

                                <div
                                    style="
                                    font-size:0.95rem;
                                    font-weight:950;
                                    "
                                >
                                    {"+" if item["avg_return20"] >= 0 else ""}
                                    {item["avg_return20"]:.1f}%
                                </div>

                            </div>

                        </div>

                        <div class="theme-reason">
                            상승 ETF 비율:
                            {item["breadth"]:.0f}%
                            · 거래량 활성:
                            {item["volume_hits"]}/
                            {item["count"]}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    "**테마 내 기술적으로 강한 ETF**"
                )

                for etf in item["etfs"][:4]:

                    etf_color = (
                        "#16a34a"
                        if etf["change"] >= 0
                        else "#dc2626"
                    )

                    st.markdown(
                        f"""
                        <div
                            style="
                            background:#f8fafc;
                            border:1px solid #e2e8f0;
                            border-radius:11px;
                            padding:10px;
                            margin-top:6px;
                            "
                        >

                            <div
                                style="
                                display:flex;
                                justify-content:space-between;
                                "
                            >

                                <div
                                    style="
                                    font-size:0.76rem;
                                    font-weight:900;
                                    "
                                >
                                    {etf["name"]}
                                </div>

                                <div
                                    style="
                                    color:{etf_color};
                                    font-size:0.72rem;
                                    font-weight:900;
                                    "
                                >
                                    {"+" if etf["change"] >= 0 else ""}
                                    {etf["change"]:.2f}%
                                </div>

                            </div>

                            <div
                                style="
                                color:#64748b;
                                font-size:0.66rem;
                                margin-top:4px;
                                "
                            >
                                {etf["code"]}
                                · 기술점수 {etf["score"]}
                                · RSI {etf["rsi"]:.0f}
                                · 거래량 {etf["volume"]:.1f}x
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    # --------------------------------------------------------
    # FUTURE DISCOVERY
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="section-head">
            <div class="section-title">
                🔮 다음 테마 탐색
            </div>
            <div class="section-caption">
                NEWS + MARKET SIGNAL
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.spinner(
        "뉴스 활성도와 시장 신호를 교차 분석 중입니다..."
    ):

        future_results = (
            discover_future_themes()
        )

    if future_results:

        for rank, item in enumerate(
            future_results,
            1
        ):

            phase_color = (
                "#dc2626"
                if "급부상" in item["phase"]
                else (
                    "#7c3aed"
                    if "선점" in item["phase"]
                    else "#2563eb"
                )
            )

            st.markdown(
                f"""
                <div class="theme-card">

                    <div
                        style="
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                        "
                    >

                        <div>

                            <div class="theme-rank">
                                DISCOVERY #{rank:02d}
                            </div>

                            <div class="theme-name">
                                {item["theme"]}
                            </div>

                        </div>

                        <div
                            style="
                            color:{phase_color};
                            font-size:0.72rem;
                            font-weight:950;
                            "
                        >
                            {item["phase"]}
                        </div>

                    </div>

                    <div
                        style="
                        display:flex;
                        gap:20px;
                        margin-top:10px;
                        "
                    >

                        <div>
                            <div
                                style="
                                color:#94a3b8;
                                font-size:0.64rem;
                                "
                            >
                                탐색점수
                            </div>
                            <div
                                style="
                                font-size:1.2rem;
                                font-weight:950;
                                "
                            >
                                {item["score"]:.1f}
                            </div>
                        </div>

                        <div>
                            <div
                                style="
                                color:#94a3b8;
                                font-size:0.64rem;
                                "
                            >
                                뉴스활성
                            </div>
                            <div
                                style="
                                font-size:1rem;
                                font-weight:900;
                                "
                            >
                                {item["news"]:.0f}
                            </div>
                        </div>

                        <div>
                            <div
                                style="
                                color:#94a3b8;
                                font-size:0.64rem;
                                "
                            >
                                시장기술
                            </div>
                            <div
                                style="
                                font-size:1rem;
                                font-weight:900;
                                "
                            >
                                {item["technical"]:.0f}
                            </div>
                        </div>

                    </div>

                    <div class="theme-reason">

                        이 테마는 현재 뉴스 관심도와
                        시장 기술적 반응을 함께 확인하는
                        탐색 대상입니다.
                        20일 평균 수익률:
                        {"+" if item["return20"] >= 0 else ""}
                        {item["return20"]:.1f}%

                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.caption(
        "미래 테마 탐색 점수는 투자수익을 예측하는 점수가 아니라 뉴스 관심도와 시장 반응을 이용해 탐색 우선순위를 정하는 지표입니다."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div
        style="
        text-align:center;
        color:#94a3b8;
        font-size:0.68rem;
        margin-top:28px;
        padding-top:12px;
        border-top:1px solid #dbe3ed;
        font-weight:650;
        "
    >
        ETF RADAR · Market Intelligence Dashboard
    </div>
    """,
    unsafe_allow_html=True
)
