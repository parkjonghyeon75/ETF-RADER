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
import xml.etree.ElementTree as ET
from datetime import datetime
import html


# ============================================================
# ETF RADAR v11
# 미래준비형 ETF 투자 가이드
#
# 핵심 흐름
# 미래준비 테마
#      ↓
# 테마 순환 / 모멘텀
#      ↓
# 선점 후보
#      ↓
# 종목 판단
#      ↓
# 보유 / 미보유
#      ↓
# 매수 / 추가매수 / 보유 / 분할매도 시나리오
#      ↓
# 차트 확인
# ============================================================


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📡",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# GLOBAL STYLE
# ============================================================

st.html(
    """
    <style>

    /* ------------------------------
       전체
    ------------------------------ */

    .stApp {
        background:
            radial-gradient(circle at 15% 0%, rgba(40,90,160,.12), transparent 32%),
            radial-gradient(circle at 90% 5%, rgba(70,120,200,.08), transparent 30%),
            #07101d;
        color: #f3f7fb;
    }

    .block-container {
        max-width: 760px;
        padding-top: 0.7rem;
        padding-bottom: 5rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }

    /* Streamlit 기본 요소 */

    label,
    .stSelectbox label,
    .stTextInput label,
    .stNumberInput label,
    .stRadio label,
    .stCheckbox label {
        color: #aebccc !important;
        font-size: .82rem !important;
    }

    div[data-baseweb="select"] > div {
        background: #101b2a !important;
        border-color: #25364b !important;
        color: white !important;
    }

    input {
        background: #101b2a !important;
        color: white !important;
        border-color: #25364b !important;
    }

    button[kind="secondary"] {
        border-radius: 10px !important;
    }


    /* ------------------------------
       HERO
    ------------------------------ */

    .hero {
        padding: 18px 18px 17px 18px;
        border-radius: 22px;
        background:
            linear-gradient(145deg,
                rgba(22,42,68,.98),
                rgba(10,22,37,.98));
        border: 1px solid rgba(95,130,170,.20);
        box-shadow: 0 14px 40px rgba(0,0,0,.22);
        margin-bottom: 14px;
    }

    .hero-title {
        font-size: 1.55rem;
        font-weight: 800;
        letter-spacing: -.04em;
    }

    .hero-sub {
        color: #91a5bb;
        font-size: .82rem;
        margin-top: 4px;
    }

    .hero-price {
        margin-top: 18px;
        font-size: 2.1rem;
        font-weight: 850;
        letter-spacing: -.05em;
    }

    .hero-change {
        margin-left: 8px;
        font-size: .92rem;
        font-weight: 700;
    }


    /* ------------------------------
       SECTION
    ------------------------------ */

    .section {
        margin-top: 19px;
        margin-bottom: 9px;
    }

    .section-title {
        font-size: 1.05rem;
        font-weight: 800;
        letter-spacing: -.025em;
    }

    .section-sub {
        color: #8194aa;
        font-size: .76rem;
        margin-top: 3px;
    }


    /* ------------------------------
       CARDS
    ------------------------------ */

    .card {
        background: rgba(14,26,42,.94);
        border: 1px solid rgba(105,132,164,.16);
        border-radius: 17px;
        padding: 14px;
        margin-bottom: 9px;
    }

    .card-title {
        font-weight: 800;
        font-size: .93rem;
    }

    .card-sub {
        color: #8194aa;
        font-size: .73rem;
        margin-top: 3px;
    }


    /* ------------------------------
       THEME CARD
    ------------------------------ */

    .theme-card {
        background:
            linear-gradient(145deg,
                rgba(17,34,55,.98),
                rgba(10,21,35,.98));
        border: 1px solid rgba(94,126,163,.18);
        border-radius: 17px;
        padding: 13px;
        margin-bottom: 8px;
    }

    .theme-name {
        font-size: .92rem;
        font-weight: 800;
    }

    .theme-stage {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 20px;
        font-size: .67rem;
        font-weight: 800;
        margin-left: 5px;
    }

    .stage-ready {
        background: rgba(47,170,110,.16);
        color: #62d99a;
    }

    .stage-lead {
        background: rgba(80,145,235,.16);
        color: #7eb3ff;
    }

    .stage-hot {
        background: rgba(244,158,65,.16);
        color: #ffb76c;
    }

    .stage-cool {
        background: rgba(160,170,185,.12);
        color: #a9b5c4;
    }

    .stage-weak {
        background: rgba(235,83,83,.13);
        color: #ff8585;
    }

    .theme-metrics {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 6px;
        margin-top: 11px;
    }

    .theme-metric {
        background: rgba(255,255,255,.035);
        border-radius: 9px;
        padding: 7px 5px;
    }

    .theme-metric-label {
        color: #75899f;
        font-size: .60rem;
    }

    .theme-metric-value {
        font-size: .79rem;
        font-weight: 800;
        margin-top: 2px;
    }

    .theme-reason {
        margin-top: 10px;
        padding-top: 9px;
        border-top: 1px solid rgba(255,255,255,.06);
        color: #aebccc;
        font-size: .72rem;
        line-height: 1.5;
    }


    /* ------------------------------
       DECISION
    ------------------------------ */

    .decision {
        border-radius: 18px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,.08);
    }

    .decision-green {
        background: linear-gradient(
            145deg,
            rgba(26,83,62,.45),
            rgba(13,35,31,.75)
        );
        border-color: rgba(83,205,145,.25);
    }

    .decision-blue {
        background: linear-gradient(
            145deg,
            rgba(30,70,120,.48),
            rgba(13,28,49,.75)
        );
        border-color: rgba(100,160,240,.25);
    }

    .decision-orange {
        background: linear-gradient(
            145deg,
            rgba(110,72,28,.42),
            rgba(40,29,17,.75)
        );
        border-color: rgba(240,169,80,.24);
    }

    .decision-red {
        background: linear-gradient(
            145deg,
            rgba(110,40,45,.42),
            rgba(41,19,24,.75)
        );
        border-color: rgba(242,99,110,.24);
    }

    .decision-gray {
        background: linear-gradient(
            145deg,
            rgba(43,53,65,.52),
            rgba(18,25,34,.78)
        );
        border-color: rgba(150,165,180,.16);
    }

    .decision-label {
        color: #899db3;
        font-size: .68rem;
        font-weight: 700;
    }

    .decision-title {
        font-size: 1.23rem;
        font-weight: 850;
        margin-top: 2px;
        letter-spacing: -.035em;
    }

    .decision-reason {
        margin-top: 11px;
        color: #c2cfdb;
        font-size: .78rem;
        line-height: 1.55;
    }

    .decision-rule {
        margin-top: 10px;
        background: rgba(0,0,0,.17);
        border-radius: 10px;
        padding: 9px 10px;
        color: #d9e3ed;
        font-size: .73rem;
        line-height: 1.55;
    }


    /* ------------------------------
       INDICATOR CARDS
    ------------------------------ */

    .indicator-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
    }

    .indicator {
        background: rgba(15,29,46,.95);
        border: 1px solid rgba(100,130,160,.13);
        border-radius: 13px;
        padding: 11px;
    }

    .indicator-label {
        color: #71869c;
        font-size: .67rem;
    }

    .indicator-value {
        font-size: 1rem;
        font-weight: 800;
        margin-top: 3px;
    }

    .indicator-note {
        color: #8799ad;
        font-size: .66rem;
        margin-top: 3px;
    }


    /* ------------------------------
       PRICE LEVEL
    ------------------------------ */

    .level-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 7px;
    }

    .level {
        padding: 11px;
        border-radius: 12px;
        background: rgba(255,255,255,.035);
    }

    .level-label {
        color: #71869c;
        font-size: .64rem;
    }

    .level-price {
        font-size: .95rem;
        font-weight: 800;
        margin-top: 3px;
    }


    /* ------------------------------
       HOLDING
    ------------------------------ */

    .holding-box {
        border-radius: 17px;
        padding: 14px;
        background:
            linear-gradient(145deg,
                rgba(22,39,61,.95),
                rgba(10,21,35,.98));
        border: 1px solid rgba(93,133,176,.18);
    }

    .holding-result {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 7px;
        margin-top: 10px;
    }

    .holding-metric {
        background: rgba(0,0,0,.16);
        border-radius: 10px;
        padding: 8px;
    }

    .holding-label {
        color: #71869c;
        font-size: .62rem;
    }

    .holding-value {
        font-size: .83rem;
        font-weight: 800;
        margin-top: 3px;
    }


    /* ------------------------------
       WATCHLIST
    ------------------------------ */

    .watch-row {
        display: grid;
        grid-template-columns: 1.7fr .7fr .7fr .65fr;
        gap: 5px;
        align-items: center;
        padding: 10px 5px;
        border-bottom: 1px solid rgba(255,255,255,.055);
        font-size: .72rem;
    }

    .watch-name {
        font-weight: 750;
    }

    .watch-small {
        color: #7f93a8;
        font-size: .64rem;
    }


    /* ------------------------------
       FOOTNOTE
    ------------------------------ */

    .footnote {
        color: #65788e;
        font-size: .65rem;
        line-height: 1.55;
        margin-top: 18px;
        padding: 10px;
    }


    /* ------------------------------
       MOBILE
    ------------------------------ */

    @media (max-width: 600px) {

        .block-container {
            padding-left: .65rem;
            padding-right: .65rem;
        }

        .hero {
            padding: 15px;
            border-radius: 18px;
        }

        .hero-title {
            font-size: 1.32rem;
        }

        .hero-price {
            font-size: 1.8rem;
        }

        .theme-metrics {
            grid-template-columns: repeat(4, 1fr);
        }

        .indicator-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .level-grid {
            grid-template-columns: repeat(3, 1fr);
        }

        .holding-result {
            grid-template-columns: repeat(3, 1fr);
        }
    }

    </style>
    """
)


# ============================================================
# CONSTANTS
# ============================================================

WATCHLIST_FILE = "watchlist.json"


ETF_UNIVERSE = {
    "360750": "TIGER 미국S&P500",
    "379800": "KODEX 미국S&P500TR",
    "448290": "SOL 미국S&P500",
    "133690": "TIGER 미국나스닥100",
    "379810": "KODEX 미국나스닥100TR",

    "487240": "KODEX 미국AI테크TOP10",
    "452330": "TIGER 미국테크TOP10",

    "395160": "KODEX AI반도체TOP2플러스",
    "462100": "TIGER AI반도체핵심공정",
    "486410": "TIGER 미국반도체TOP10",

    "471990": "KODEX AI전력핵심설비",
    "445380": "SOL 원자력TOP3플러스",
    "465560": "TIGER 글로벌원자력",

    "305540": "KODEX 2차전지산업",
    "364980": "TIGER 2차전지소부장",
    "438320": "KODEX 2차전지핵심소재",

    "465610": "KODEX 로봇산업",
    "476250": "TIGER 우주항공&로봇",

    "329200": "TIGER 헬스케어",
    "266420": "KODEX 바이오",
    "462610": "ARIRANG 3대주주바이오",

    "458730": "TIGER 미국배당다우존스",
    "441680": "SOL 미국배당다우존스",
    "476480": "KODEX 미국배당커버드콜",
    "451780": "TIGER 미국배당+7%프리미엄",

    "423160": "KODEX CD금리활성(합성)",
    "449170": "TIGER KOFR금리액티브",
    "308620": "KODEX 미국채울트라30년선물",
    "365780": "TIGER 미국채30년스트립액티브",
}


THEMES = {
    "AI 반도체": [
        "395160",
        "462100",
        "486410",
        "487240",
        "452330",
    ],
    "전력·원전": [
        "471990",
        "445380",
        "465560",
    ],
    "미국 AI·테크": [
        "487240",
        "452330",
        "133690",
    ],
    "미국 대표지수": [
        "360750",
        "379800",
        "448290",
        "133690",
        "379810",
    ],
    "2차전지": [
        "305540",
        "364980",
        "438320",
    ],
    "로봇·우주": [
        "465610",
        "476250",
    ],
    "바이오": [
        "329200",
        "266420",
        "462610",
    ],
    "배당": [
        "458730",
        "441680",
        "476480",
        "451780",
    ],
    "금리·채권": [
        "423160",
        "449170",
        "308620",
        "365780",
    ],
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
# UTILITY
# ============================================================

def safe_float(v, default=np.nan):
    try:
        if pd.isna(v):
            return default
        return float(v)
    except Exception:
        return default


def fmt_price(v):
    v = safe_float(v)
    if np.isnan(v):
        return "-"
    return f"{v:,.0f}"


def fmt_pct(v):
    v = safe_float(v)
    if np.isnan(v):
        return "-"
    sign = "+" if v > 0 else ""
    return f"{sign}{v:.1f}%"


def fmt_num(v):
    v = safe_float(v)
    if np.isnan(v):
        return "-"
    return f"{v:,.1f}"


def pct_color(v):
    v = safe_float(v)

    if np.isnan(v):
        return "#aebccc"

    if v > 0:
        return "#5fd398"

    if v < 0:
        return "#ff777f"

    return "#aebccc"


def html_card(content):
    st.html(content)


# ============================================================
# WATCHLIST
# ============================================================

def load_watchlist():

    if not os.path.exists(WATCHLIST_FILE):
        return DEFAULT_WATCHLIST.copy()

    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

    except Exception:
        pass

    return DEFAULT_WATCHLIST.copy()


def save_watchlist(items):

    try:
        with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

    except Exception:
        pass


if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()


# ============================================================
# NAVER DATA
# ============================================================

@st.cache_data(ttl=600, show_spinner=False)
def fetch_from_naver(code, count=500):

    url = (
        "https://fchart.stock.naver.com/sise.nhn"
        f"?symbol={code}"
        "&timeframe=day"
        f"&count={count}"
        "&requestType=0"
    )

    try:

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read()

        root = ET.fromstring(raw)

        rows = []

        for item in root.findall(".//item"):

            data = item.attrib.get("data", "").split("|")

            if len(data) < 6:
                continue

            date = data[0]

            rows.append(
                {
                    "Date": pd.to_datetime(date),
                    "Open": safe_float(data[1]),
                    "High": safe_float(data[2]),
                    "Low": safe_float(data[3]),
                    "Close": safe_float(data[4]),
                    "Volume": safe_float(data[5]),
                }
            )

        df = pd.DataFrame(rows)

        if df.empty:
            return pd.DataFrame()

        df = df.sort_values("Date")
        df = df.set_index("Date")

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# YAHOO FALLBACK
# ============================================================

@st.cache_data(ttl=600, show_spinner=False)
def fetch_from_yahoo(code):

    try:

        ticker = f"{code}.KS"

        df = yf.download(
            ticker,
            period="2y",
            interval="1d",
            auto_adjust=False,
            progress=False,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        rename = {
            "Open": "Open",
            "High": "High",
            "Low": "Low",
            "Close": "Close",
            "Volume": "Volume",
        }

        df = df.rename(columns=rename)

        needed = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]

        df = df[[c for c in needed if c in df.columns]]

        df = df.dropna(subset=["Close"])

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# LOAD ETF
# ============================================================

@st.cache_data(ttl=600, show_spinner=False)
def load_etf_data(code):

    df = fetch_from_naver(code, 500)

    if df.empty:

        df = fetch_from_yahoo(code)

    if df.empty:
        return pd.DataFrame()

    df = df.copy()

    for col in [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]:

        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    df = df.dropna(subset=["Close"])

    return df


# ============================================================
# INDICATORS
# ============================================================

def add_indicators(df):

    df = df.copy()

    close = df["Close"]

    df["MA5"] = close.rolling(5).mean()
    df["MA20"] = close.rolling(20).mean()
    df["MA60"] = close.rolling(60).mean()
    df["MA120"] = close.rolling(120).mean()

    # RSI
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()

    df["MACD"] = ema12 - ema26
    df["MACD_SIGNAL"] = df["MACD"].ewm(
        span=9,
        adjust=False
    ).mean()

    df["MACD_HIST"] = (
        df["MACD"] -
        df["MACD_SIGNAL"]
    )

    # Bollinger
    df["BB_MID"] = close.rolling(20).mean()

    std20 = close.rolling(20).std()

    df["BB_UPPER"] = (
        df["BB_MID"] +
        2 * std20
    )

    df["BB_LOWER"] = (
        df["BB_MID"] -
        2 * std20
    )

    # Volume
    df["VOL_MA20"] = df["Volume"].rolling(20).mean()

    df["VOL_RATIO"] = (
        df["Volume"] /
        df["VOL_MA20"].replace(0, np.nan)
    )

    # Return
    df["RET_1D"] = close.pct_change() * 100

    df["RET_20D"] = (
        close.pct_change(20) * 100
    )

    df["RET_60D"] = (
        close.pct_change(60) * 100
    )

    df["RET_120D"] = (
        close.pct_change(120) * 100
    )

    # ATR
    prev_close = close.shift(1)

    tr1 = df["High"] - df["Low"]
    tr2 = abs(df["High"] - prev_close)
    tr3 = abs(df["Low"] - prev_close)

    true_range = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    df["ATR14"] = true_range.rolling(14).mean()

    return df


# ============================================================
# TECHNICAL SCORE
# ============================================================

def technical_score(df):

    if len(df) < 60:
        return 50

    last = df.iloc[-1]

    close = safe_float(last["Close"])
    ma5 = safe_float(last["MA5"])
    ma20 = safe_float(last["MA20"])
    ma60 = safe_float(last["MA60"])
    ma120 = safe_float(last["MA120"])

    rsi = safe_float(last["RSI"])
    macd = safe_float(last["MACD"])
    signal = safe_float(last["MACD_SIGNAL"])
    hist = safe_float(last["MACD_HIST"])

    vol_ratio = safe_float(last["VOL_RATIO"])
    ret1 = safe_float(last["RET_1D"])

    score = 0

    if close > ma20:
        score += 15

    if ma20 > ma60:
        score += 10

    if ma60 > ma120:
        score += 10

    if 50 <= rsi <= 68:
        score += 15

    elif 40 <= rsi < 50:
        score += 10

    elif 68 < rsi < 72:
        score += 8

    else:
        score += 5

    if macd > signal:
        score += 15

    if hist > 0:
        score += 5

    if vol_ratio >= 1.2 and ret1 > 0:
        score += 10

    if close > safe_float(last["BB_MID"]):
        score += 5

    if close > ma5:
        score += 5

    prev20_high = safe_float(
        df["High"].rolling(20).max().shift(1).iloc[-1]
    )

    if (
        not np.isnan(prev20_high)
        and close > prev20_high
        and vol_ratio >= 1.3
    ):
        score += 10

    return int(max(0, min(100, score)))


# ============================================================
# SCORE LABEL
# ============================================================

def score_label(score):

    if score >= 80:
        return "강한 상승 구조"

    if score >= 65:
        return "상승 우위"

    if score >= 50:
        return "중립 / 확인"

    if score >= 35:
        return "약세 전환 주의"

    return "약세"


# ============================================================
# SUPPORT / RESISTANCE
# ============================================================

def calculate_levels(df):

    if len(df) < 30:
        return np.nan, np.nan, np.nan, np.nan

    last = df.iloc[-1]

    close = safe_float(last["Close"])

    ma20 = safe_float(last["MA20"])
    ma60 = safe_float(last["MA60"])
    ma120 = safe_float(last["MA120"])

    low20 = safe_float(
        df["Low"].rolling(20).min().iloc[-1]
    )

    low60 = safe_float(
        df["Low"].rolling(60).min().iloc[-1]
    )

    high20 = safe_float(
        df["High"].rolling(20).max().shift(1).iloc[-1]
    )

    high60 = safe_float(
        df["High"].rolling(60).max().shift(1).iloc[-1]
    )

    bb_upper = safe_float(last["BB_UPPER"])

    support_candidates = [
        x for x in [
            ma20,
            ma60,
            ma120,
            low20,
            low60,
        ]
        if not np.isnan(x)
        and x < close
    ]

    resistance_candidates = [
        x for x in [
            high20,
            high60,
            bb_upper,
        ]
        if not np.isnan(x)
        and x > close
    ]

    support = (
        max(support_candidates)
        if support_candidates
        else np.nan
    )

    resistance = (
        min(resistance_candidates)
        if resistance_candidates
        else np.nan
    )

    return (
        support,
        resistance,
        high20,
        low20,
    )


# ============================================================
# PATTERN
# ============================================================

def detect_pattern(df):

    last = df.iloc[-1]

    close = safe_float(last["Close"])
    ma20 = safe_float(last["MA20"])
    ma60 = safe_float(last["MA60"])

    rsi = safe_float(last["RSI"])
    macd = safe_float(last["MACD"])
    signal = safe_float(last["MACD_SIGNAL"])

    vol_ratio = safe_float(last["VOL_RATIO"])

    prev20_high = safe_float(
        df["High"].rolling(20).max().shift(1).iloc[-1]
    )

    breakout = (
        not np.isnan(prev20_high)
        and close > prev20_high
        and vol_ratio >= 1.3
        and macd > signal
    )

    pullback = (
        not np.isnan(ma20)
        and not np.isnan(ma60)
        and abs(close - ma20) / ma20 <= 0.035
        and ma20 > ma60
        and 42 <= rsi <= 65
    )

    overbought = rsi >= 70

    weakening = (
        close < ma20
        and macd < signal
    )

    if breakout:
        return "돌파"

    if pullback:
        return "눌림"

    if overbought:
        return "과열주의"

    if weakening:
        return "약세전환"

    if close > ma20 and ma20 > ma60:
        return "상승추세"

    return "관망"


# ============================================================
# THEME STAGE
# ============================================================

def theme_stage(
    ret20,
    ret60,
    breadth,
    avg_rsi,
):

    ret20 = safe_float(ret20, 0)
    ret60 = safe_float(ret60, 0)
    breadth = safe_float(breadth, 0)
    avg_rsi = safe_float(avg_rsi, 50)

    acceleration = ret20 - (ret60 / 3)

    # 과열
    if (
        ret20 >= 8
        and avg_rsi >= 68
    ):
        return "과열", "stage-hot"

    # 주도
    if (
        ret20 >= 4
        and breadth >= 60
        and acceleration >= 1
    ):
        return "주도", "stage-lead"

    # 점화 / 미래준비
    if (
        acceleration >= 2
        and ret20 > -2
        and breadth >= 40
    ):
        return "점화", "stage-ready"

    # 냉각
    if (
        ret20 < 0
        and ret60 > 0
    ):
        return "냉각", "stage-cool"

    # 약세
    if (
        ret20 < -4
        and ret60 < 0
    ):
        return "약세", "stage-weak"

    return "관망", "stage-cool"


# ============================================================
# THEME SCAN
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def scan_themes():

    rows = []

    for theme_name, codes in THEMES.items():

        items = []

        for code in codes:

            df = load_etf_data(code)

            if df.empty or len(df) < 70:
                continue

            df = add_indicators(df)

            last = df.iloc[-1]

            close = safe_float(last["Close"])
            ret20 = safe_float(last["RET_20D"])
            ret60 = safe_float(last["RET_60D"])
            rsi = safe_float(last["RSI"])

            score = technical_score(df)

            items.append(
                {
                    "code": code,
                    "name": ETF_UNIVERSE.get(code, code),
                    "close": close,
                    "ret20": ret20,
                    "ret60": ret60,
                    "rsi": rsi,
                    "score": score,
                }
            )

        if not items:
            continue

        x = pd.DataFrame(items)

        avg20 = x["ret20"].mean()
        avg60 = x["ret60"].mean()

        breadth = (
            (x["ret20"] > 0).mean() * 100
        )

        avg_rsi = x["rsi"].mean()
        avg_score = x["score"].mean()

        stage, stage_class = theme_stage(
            avg20,
            avg60,
            breadth,
            avg_rsi
        )

        # 미래준비 후보
        candidates = x[
            (
                (x["score"] >= 55)
                &
                (x["ret20"] > -3)
                &
                (x["ret60"] > -8)
            )
        ].sort_values(
            ["score", "ret20"],
            ascending=False
        )

        candidate_text = ", ".join(
            candidates["name"]
            .head(2)
            .tolist()
        )

        acceleration = avg20 - avg60 / 3

        rows.append(
            {
                "theme": theme_name,
                "avg20": avg20,
                "avg60": avg60,
                "breadth": breadth,
                "rsi": avg_rsi,
                "score": avg_score,
                "acceleration": acceleration,
                "stage": stage,
                "stage_class": stage_class,
                "candidates": candidate_text,
            }
        )

    result = pd.DataFrame(rows)

    if result.empty:
        return result

    return result.sort_values(
        ["score", "acceleration"],
        ascending=False
    ).reset_index(drop=True)


# ============================================================
# THEME REASON
# ============================================================

def theme_reason(row):

    stage = row["stage"]
    ret20 = safe_float(row["avg20"])
    ret60 = safe_float(row["avg60"])
    breadth = safe_float(row["breadth"])
    accel = safe_float(row["acceleration"])

    if stage == "점화":

        return (
            f"최근 20일 {ret20:+.1f}% / 60일 {ret60:+.1f}%로 "
            f"단기 모멘텀이 상대적으로 개선되고 있습니다. "
            f"상승 ETF 비율 {breadth:.0f}%, 가속도 {accel:+.1f}p입니다. "
            "아직 과열보다 초기 확산 여부를 확인하는 구간입니다."
        )

    if stage == "주도":

        return (
            f"20일 평균 {ret20:+.1f}%로 강한 흐름이며 "
            f"상승 ETF 비율도 {breadth:.0f}%입니다. "
            "현재 시장의 주도 테마 성격을 보이는지 확인하는 단계입니다."
        )

    if stage == "과열":

        return (
            f"20일 평균 {ret20:+.1f}% 상승과 RSI 평균 "
            f"{row['rsi']:.0f} 수준으로 단기 과열 여부를 확인해야 합니다. "
            "새 진입은 추격보다 눌림 여부를 확인하는 것이 핵심입니다."
        )

    if stage == "냉각":

        return (
            f"장기 흐름은 아직 {ret60:+.1f}%지만 최근 20일은 "
            f"{ret20:+.1f}%입니다. "
            "상승 추세가 유지되는지 재확인이 필요한 테마입니다."
        )

    if stage == "약세":

        return (
            f"20일 {ret20:+.1f}% / 60일 {ret60:+.1f}%로 "
            "단기와 중기 흐름이 모두 약합니다. "
            "미래준비 후보라 하더라도 추세 회복을 확인하는 편이 안전합니다."
        )

    return (
        f"20일 {ret20:+.1f}% / 60일 {ret60:+.1f}%, "
        f"상승 ETF 비율 {breadth:.0f}%입니다. "
        "아직 뚜렷한 순환 신호가 형성되는지 관찰하는 구간입니다."
    )


# ============================================================
# POSITION GUIDE
# ============================================================

def position_guide(
    df,
    holding,
    avg_price=0,
    shares=0,
):

    df = add_indicators(df)

    last = df.iloc[-1]

    close = safe_float(last["Close"])

    ma20 = safe_float(last["MA20"])
    ma60 = safe_float(last["MA60"])

    rsi = safe_float(last["RSI"])
    macd = safe_float(last["MACD"])
    signal = safe_float(last["MACD_SIGNAL"])
    vol_ratio = safe_float(last["VOL_RATIO"])

    score = technical_score(df)

    support, resistance, prev20_high, prev20_low = calculate_levels(df)

    pattern = detect_pattern(df)

    # 이전 데이터 기준 지지
    prev_df = df.iloc[:-1]

    if len(prev_df) >= 70:
        (
            prev_support,
            prev_resistance,
            _,
            _
        ) = calculate_levels(prev_df)

    else:
        prev_support = support
        prev_resistance = resistance

    broken_support = (
        not np.isnan(prev_support)
        and close < prev_support
    )

    breakout = (
        not np.isnan(prev_resistance)
        and close > prev_resistance
        and vol_ratio >= 1.3
    )

    near_ma20 = (
        not np.isnan(ma20)
        and abs(close - ma20) / ma20 <= .035
    )

    near_resistance = (
        not np.isnan(resistance)
        and close >= resistance * .985
    )

    pullback = (
        near_ma20
        and ma20 > ma60
        and 42 <= rsi <= 65
    )

    pnl_pct = np.nan
    pnl_amount = np.nan

    if holding and avg_price > 0 and shares > 0:

        pnl_pct = (
            (close / avg_price) - 1
        ) * 100

        pnl_amount = (
            close - avg_price
        ) * shares

    # --------------------------------------------------------
    # 보유
    # --------------------------------------------------------

    if holding:

        if broken_support:

            title = "리스크 관리 우선"
            css = "decision-red"

            reason = (
                "현재 종가가 직전 구조적 지지선 아래에 있습니다. "
                "평균단가를 낮추기 위한 추가매수보다 "
                "지지선 회복 여부를 먼저 확인하는 시나리오입니다."
            )

            rule = (
                f"핵심 기준: 지지선 {fmt_price(prev_support)} 회복 여부 → "
                "MA20 재돌파 여부 → MACD 회복 여부"
            )

        elif pullback and score >= 60:

            title = "추가매수 검토 구간"
            css = "decision-green"

            reason = (
                "상승 추세가 유지되는 가운데 가격이 MA20/지지선 주변으로 "
                "조정되었습니다. RSI도 과열권이 아니어서 "
                "추격보다 눌림 확인형 접근에 적합한 구조입니다."
            )

            rule = (
                f"근거: MA20 {fmt_price(ma20)} / "
                f"지지 {fmt_price(support)} / "
                f"RSI {rsi:.0f} / "
                f"MACD {'상승' if macd > signal else '약세'}"
            )

        elif near_resistance and rsi >= 68:

            title = "분할매도 검토 구간"
            css = "decision-orange"

            reason = (
                "가격이 주요 저항선에 접근했고 RSI가 높은 수준입니다. "
                "상승 추세가 끝났다는 의미는 아니지만, "
                "일부 이익실현과 재진입 기회를 함께 검토할 수 있는 구간입니다."
            )

            rule = (
                f"관찰 기준: 저항 {fmt_price(resistance)} / "
                f"RSI {rsi:.0f} / 거래량비 {vol_ratio:.1f}배"
            )

        elif rsi >= 72:

            title = "보유 유지 · 추격매수 주의"
            css = "decision-orange"

            reason = (
                "추세 자체는 유지될 수 있지만 단기 과열 가능성이 커졌습니다. "
                "추가매수보다 눌림 또는 거래량 안정 여부를 확인하는 시나리오입니다."
            )

            rule = (
                f"근거: RSI {rsi:.0f} / "
                f"MA20 {fmt_price(ma20)} / "
                f"현재가 {fmt_price(close)}"
            )

        elif score >= 55:

            title = "보유 유지 · 추세 확인"
            css = "decision-blue"

            reason = (
                "중기 추세가 아직 훼손되지 않았습니다. "
                "현재는 매도보다 MA20과 지지선 유지 여부를 관찰하는 구간입니다."
            )

            rule = (
                f"근거: 종합점수 {score} / "
                f"MA20 {fmt_price(ma20)} / "
                f"MA60 {fmt_price(ma60)} / "
                f"RSI {rsi:.0f}"
            )

        else:

            title = "추가매수보다 관찰"
            css = "decision-gray"

            reason = (
                "현재 기술적 조건이 강한 상승 구조라고 보기 어렵습니다. "
                "추가매수보다는 MA20 회복과 MACD 개선을 먼저 확인하는 시나리오입니다."
            )

            rule = (
                f"확인 기준: 종합점수 {score} / "
                f"MA20 {fmt_price(ma20)} / "
                f"RSI {rsi:.0f}"
            )

        return {
            "title": title,
            "css": css,
            "reason": reason,
            "rule": rule,
            "score": score,
            "support": support,
            "resistance": resistance,
            "pnl_pct": pnl_pct,
            "pnl_amount": pnl_amount,
            "pattern": pattern,
            "ma20": ma20,
            "ma60": ma60,
            "rsi": rsi,
            "vol_ratio": vol_ratio,
            "prev_support": prev_support,
            "prev_resistance": prev_resistance,
            "breakout": breakout,
        }

    # --------------------------------------------------------
    # 미보유
    # --------------------------------------------------------

    if breakout:

        title = "돌파 후 재확인"
        css = "decision-blue"

        reason = (
            "주요 저항을 거래량과 함께 돌파하는 조건이 발생했습니다. "
            "다만 돌파 직후 추격보다 돌파 가격을 다시 지지하는지를 "
            "확인하는 방식이 더 안정적인 시나리오입니다."
        )

        rule = (
            f"돌파 기준 {fmt_price(prev_resistance)} / "
            f"거래량비 {vol_ratio:.1f}배 / "
            f"MACD {'상승' if macd > signal else '약세'}"
        )

    elif pullback and score >= 60:

        title = "눌림매수 검토"
        css = "decision-green"

        reason = (
            "상승 추세가 유지되면서 가격이 MA20/지지선에 접근했습니다. "
            "미보유라면 추격보다 눌림 확인을 우선하는 시나리오입니다."
        )

        rule = (
            f"검토 가격대: {fmt_price(min(support, ma20))} ~ "
            f"{fmt_price(max(support, ma20))} / "
            f"RSI {rsi:.0f}"
        )

    elif score >= 65 and close > ma20 and rsi < 68:

        title = "상승추세 진입 검토"
        css = "decision-blue"

        reason = (
            "가격이 MA20 위에 있고 중기 이동평균 구조가 개선되어 있습니다. "
            "다만 이미 상승한 가격이라면 일부 진입보다 분할 접근을 검토하는 구조입니다."
        )

        rule = (
            f"근거: 종합점수 {score} / "
            f"MA20 {fmt_price(ma20)} / "
            f"MA60 {fmt_price(ma60)} / "
            f"RSI {rsi:.0f}"
        )

    elif rsi >= 70 or (
        not np.isnan(ma20)
        and close > ma20 * 1.07
    ):

        title = "추격매수 주의"
        css = "decision-orange"

        reason = (
            "상승 자체보다 현재 가격이 단기 평균에서 얼마나 이격됐는지가 문제입니다. "
            "신규 진입이라면 눌림을 기다리는 시나리오가 우선입니다."
        )

        rule = (
            f"현재가 {fmt_price(close)} / "
            f"MA20 {fmt_price(ma20)} / "
            f"RSI {rsi:.0f}"
        )

    elif score < 50:

        title = "관망"
        css = "decision-gray"

        reason = (
            "아직 상승 추세를 확인할 기술적 근거가 충분하지 않습니다. "
            "MA20 회복, MACD 개선 또는 거래량 증가가 나타나는지 관찰합니다."
        )

        rule = (
            f"현재 종합점수 {score} / "
            f"MA20 {fmt_price(ma20)} / "
            f"RSI {rsi:.0f}"
        )

    else:

        title = "조건 확인 후 접근"
        css = "decision-gray"

        reason = (
            "방향성이 뚜렷하지 않습니다. "
            "가격보다 다음 신호가 먼저 나타나는지 확인하는 구간입니다."
        )

        rule = (
            f"확인 기준: MA20 {fmt_price(ma20)} / "
            f"MA60 {fmt_price(ma60)} / "
            f"RSI {rsi:.0f}"
        )

    return {
        "title": title,
        "css": css,
        "reason": reason,
        "rule": rule,
        "score": score,
        "support": support,
        "resistance": resistance,
        "pnl_pct": np.nan,
        "pnl_amount": np.nan,
        "pattern": pattern,
        "ma20": ma20,
        "ma60": ma60,
        "rsi": rsi,
        "vol_ratio": vol_ratio,
        "prev_support": prev_support,
        "prev_resistance": prev_resistance,
        "breakout": breakout,
    }


# ============================================================
# PRICE CHART
# ============================================================

def make_price_chart(
    df,
    period,
    interactive=False,
):

    period_map = {
        "3개월": 70,
        "6개월": 130,
        "1년": 260,
        "2년": 500,
    }

    n = period_map.get(period, 130)

    chart_df = df.tail(n).copy()

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        row_heights=[
            0.56,
            0.19,
            0.25,
        ],
        vertical_spacing=0.025,
    )

    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name="가격",
            increasing_line_color="#63d59a",
            decreasing_line_color="#ff727d",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA20"],
            name="MA20",
            line=dict(
                color="#e6c96b",
                width=1.5,
            ),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA60"],
            name="MA60",
            line=dict(
                color="#73a7e8",
                width=1.4,
            ),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["BB_UPPER"],
            name="BB Upper",
            line=dict(
                color="rgba(150,165,185,.35)",
                width=1,
                dash="dot",
            ),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["BB_LOWER"],
            name="BB Lower",
            line=dict(
                color="rgba(150,165,185,.35)",
                width=1,
                dash="dot",
            ),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=chart_df.index,
            y=chart_df["Volume"],
            name="거래량",
            marker_color="rgba(92,140,185,.45)",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["RSI"],
            name="RSI",
            line=dict(
                color="#b08cff",
                width=1.6,
            ),
        ),
        row=3,
        col=1,
    )

    fig.add_hline(
        y=70,
        line_dash="dot",
        line_color="rgba(255,120,130,.45)",
        row=3,
        col=1,
    )

    fig.add_hline(
        y=50,
        line_dash="dot",
        line_color="rgba(150,170,190,.30)",
        row=3,
        col=1,
    )

    fig.update_layout(
        height=520,
        margin=dict(
            l=8,
            r=8,
            t=10,
            b=5,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#9cafc3",
            size=10,
        ),
        legend=dict(
            orientation="h",
            y=1.02,
            x=0,
            font=dict(size=9),
        ),
        hovermode="x unified",
        dragmode="pan" if interactive else False,
        xaxis_rangeslider_visible=False,
        showlegend=True,
    )

    fig.update_xaxes(
        showgrid=False,
        fixedrange=not interactive,
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(120,145,170,.08)",
        fixedrange=not interactive,
    )

    fig.update_yaxes(
        range=[20, 80],
        row=3,
        col=1,
    )

    return fig


# ============================================================
# VOLUME PROFILE
# ============================================================

def volume_profile(df, bins=14, window=120):

    x = df.tail(window).copy()

    if x.empty:
        return pd.DataFrame()

    low = x["Low"].min()
    high = x["High"].max()

    if low == high:
        return pd.DataFrame()

    hist, edges = np.histogram(
        x["Close"],
        bins=bins,
        range=(low, high),
        weights=x["Volume"],
    )

    centers = (
        edges[:-1] +
        edges[1:]
    ) / 2

    result = pd.DataFrame(
        {
            "price": centers,
            "volume": hist,
        }
    )

    return result.sort_values(
        "volume",
        ascending=False
    )


# ============================================================
# HERO
# ============================================================

def render_hero(
    name,
    code,
    close,
    change_pct,
    score,
):

    color = pct_color(change_pct)

    html_card(
        f"""
        <div class="hero">

            <div class="hero-title">
                📡 ETF RADAR
            </div>

            <div class="hero-sub">
                미래준비형 ETF 투자 가이드 · {html.escape(name)}
                · {code}
            </div>

            <div class="hero-price">
                {fmt_price(close)}
                <span
                    class="hero-change"
                    style="color:{color};"
                >
                    {fmt_pct(change_pct)}
                </span>
            </div>

            <div class="hero-sub">
                기술구조 {score}/100 · {score_label(score)}
            </div>

        </div>
        """
    )


# ============================================================
# SECTION TITLE
# ============================================================

def section_title(title, subtitle=""):

    html_card(
        f"""
        <div class="section">

            <div class="section-title">
                {html.escape(title)}
            </div>

            <div class="section-sub">
                {html.escape(subtitle)}
            </div>

        </div>
        """
    )


# ============================================================
# MAIN
# ============================================================

# ------------------------------------------------------------
# TOP NAV / SEARCH
# ------------------------------------------------------------

section_title(
    "오늘 어디를 봐야 할까?",
    "종목보다 먼저 테마의 흐름을 확인합니다."
)


search = st.text_input(
    "ETF 검색",
    placeholder="예: AI반도체 / S&P500 / 전력 / 395160",
    label_visibility="collapsed",
)


search_lower = search.strip().lower()

if search_lower:

    filtered = [
        code
        for code, name in ETF_UNIVERSE.items()
        if (
            search_lower in code.lower()
            or search_lower in name.lower()
        )
    ]

else:

    filtered = list(ETF_UNIVERSE.keys())


if not filtered:
    filtered = list(ETF_UNIVERSE.keys())


selected_code = st.selectbox(
    "분석 ETF",
    filtered,
    format_func=lambda x:
        f"{ETF_UNIVERSE.get(x, x)}  ·  {x}",
)


selected_name = ETF_UNIVERSE.get(
    selected_code,
    selected_code,
)


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

with st.spinner("시장 데이터를 분석하고 있습니다..."):

    raw_df = load_etf_data(selected_code)


if raw_df.empty:

    st.error(
        "데이터를 불러오지 못했습니다. "
        "잠시 후 다시 시도해주세요."
    )

    st.stop()


df = add_indicators(raw_df)


if len(df) < 70:

    st.warning(
        "분석에 필요한 데이터가 충분하지 않습니다."
    )

    st.stop()


# ------------------------------------------------------------
# BASIC
# ------------------------------------------------------------

last = df.iloc[-1]
prev = df.iloc[-2]

close = safe_float(last["Close"])
prev_close = safe_float(prev["Close"])

change_pct = (
    close / prev_close - 1
) * 100

score = technical_score(df)

pattern = detect_pattern(df)

support, resistance, prev20_high, prev20_low = (
    calculate_levels(df)
)


# ------------------------------------------------------------
# HERO
# ------------------------------------------------------------

render_hero(
    selected_name,
    selected_code,
    close,
    change_pct,
    score,
)


# ============================================================
# 1. 미래준비 테마
# ============================================================

section_title(
    "① 미래준비 테마",
    "테마가 이미 달리고 있는지보다, 다음 순환 후보가 나타나는지를 봅니다."
)


if (
    "theme_scan_time" not in st.session_state
    or st.session_state.get("theme_scan_time") is None
):

    st.session_state.theme_scan_time = None


scan_col1, scan_col2 = st.columns(
    [2.2, 1],
    gap="small"
)


with scan_col1:

    if st.session_state.theme_scan_time:

        st.caption(
            "최근 스캔: "
            + st.session_state.theme_scan_time
        )

    else:

        st.caption(
            "아직 이번 세션에서 테마 스캔을 하지 않았습니다."
        )


with scan_col2:

    scan_clicked = st.button(
        "🔄 테마 스캔",
        use_container_width=True,
    )


if scan_clicked:

    scan_themes.clear()

    st.session_state.theme_scan_time = (
        datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )
    )


theme_df = scan_themes()


if theme_df.empty:

    st.warning(
        "테마 데이터를 아직 계산하지 못했습니다."
    )

else:

    # 미래준비 테마를 먼저
    ready_df = theme_df[
        theme_df["stage"] == "점화"
    ].copy()

    if ready_df.empty:

        ready_df = theme_df[
            theme_df["stage"].isin(
                ["관망", "주도"]
            )
        ].copy()

    if not ready_df.empty:

        html_card(
            """
            <div class="card">

                <div class="card-title">
                    🌱 미래준비 후보
                </div>

                <div class="card-sub">
                    최근 모멘텀이 개선되거나 순환 초기 신호가 나타나는 테마
                </div>

            </div>
            """
        )

        for _, row in ready_df.head(4).iterrows():

            reason = theme_reason(row)

            candidates = row["candidates"]

            html_card(
                f"""
                <div class="theme-card">

                    <div>
                        <span class="theme-name">
                            {html.escape(row["theme"])}
                        </span>

                        <span class="theme-stage {row["stage_class"]}">
                            {html.escape(row["stage"])}
                        </span>
                    </div>

                    <div class="theme-metrics">

                        <div class="theme-metric">
                            <div class="theme-metric-label">
                                20일
                            </div>
                            <div
                                class="theme-metric-value"
                                style="color:{pct_color(row["avg20"])};"
                            >
                                {fmt_pct(row["avg20"])}
                            </div>
                        </div>

                        <div class="theme-metric">
                            <div class="theme-metric-label">
                                60일
                            </div>
                            <div
                                class="theme-metric-value"
                                style="color:{pct_color(row["avg60"])};"
                            >
                                {fmt_pct(row["avg60"])}
                            </div>
                        </div>

                        <div class="theme-metric">
                            <div class="theme-metric-label">
                                확산
                            </div>
                            <div class="theme-metric-value">
                                {row["breadth"]:.0f}%
                            </div>
                        </div>

                        <div class="theme-metric">
                            <div class="theme-metric-label">
                                구조
                            </div>
                            <div class="theme-metric-value">
                                {row["score"]:.0f}
                            </div>
                        </div>

                    </div>

                    <div class="theme-reason">

                        <b>왜 보는가?</b><br>
                        {html.escape(reason)}

                        <br><br>

                        <b>선점 후보</b><br>
                        {html.escape(candidates) if candidates else "아직 명확한 후보 없음"}

                    </div>

                </div>
                """
            )


    # --------------------------------------------------------
    # 전체 테마 흐름
    # --------------------------------------------------------

    html_card(
        """
        <div class="card">

            <div class="card-title">
                🔄 테마 순환 지도
            </div>

            <div class="card-sub">
                현재 강한 테마만 보는 것이 아니라 점화 → 확산 → 주도 → 과열 → 냉각 흐름을 관찰합니다.
            </div>

        </div>
        """
    )

    for _, row in theme_df.iterrows():

        stage = row["stage"]

        if stage == "점화":
            icon = "🌱"

        elif stage == "주도":
            icon = "🚀"

        elif stage == "과열":
            icon = "🔥"

        elif stage == "냉각":
            icon = "❄️"

        elif stage == "약세":
            icon = "🔻"

        else:
            icon = "👀"

        html_card(
            f"""
            <div class="theme-card">

                <div>
                    <span class="theme-name">
                        {icon} {html.escape(row["theme"])}
                    </span>

                    <span class="theme-stage {row["stage_class"]}">
                        {html.escape(stage)}
                    </span>
                </div>

                <div class="theme-metrics">

                    <div class="theme-metric">
                        <div class="theme-metric-label">
                            20D
                        </div>
                        <div class="theme-metric-value">
                            {fmt_pct(row["avg20"])}
                        </div>
                    </div>

                    <div class="theme-metric">
                        <div class="theme-metric-label">
                            60D
                        </div>
                        <div class="theme-metric-value">
                            {fmt_pct(row["avg60"])}
                        </div>
                    </div>

                    <div class="theme-metric">
                        <div class="theme-metric-label">
                            상승비율
                        </div>
                        <div class="theme-metric-value">
                            {row["breadth"]:.0f}%
                        </div>
                    </div>

                    <div class="theme-metric">
                        <div class="theme-metric-label">
                            가속도
                        </div>
                        <div class="theme-metric-value">
                            {row["acceleration"]:+.1f}
                        </div>
                    </div>

                </div>

            </div>
            """
        )


# ============================================================
# 2. SELECTED ETF JUDGMENT
# ============================================================

section_title(
    "② 이 ETF는 지금 어떤 상태인가?",
    "판단과 근거를 바로 붙여서 보여줍니다."
)


# Pattern / score

if score >= 65:
    decision_css = "decision-blue"
else:
    decision_css = "decision-gray"


if pattern == "돌파":

    pattern_text = "🚀 돌파"
    pattern_reason = (
        "20일 고점을 넘어서는 움직임과 거래량 증가 여부를 확인합니다."
    )

elif pattern == "눌림":

    pattern_text = "↘️ 눌림"
    pattern_reason = (
        "상승 추세 안에서 MA20 주변으로 조정된 상태입니다."
    )

elif pattern == "과열주의":

    pattern_text = "🔥 과열주의"
    pattern_reason = (
        "RSI가 높은 구간이라 신규 추격보다 눌림 여부를 확인합니다."
    )

elif pattern == "약세전환":

    pattern_text = "⚠️ 약세전환"
    pattern_reason = (
        "MA20 아래 + MACD 약세가 동시에 나타나는지 확인합니다."
    )

elif pattern == "상승추세":

    pattern_text = "📈 상승추세"
    pattern_reason = (
        "가격이 MA20 위이고 MA20이 MA60보다 높은 구조입니다."
    )

else:

    pattern_text = "👀 관망"
    pattern_reason = (
        "추세 방향이 아직 뚜렷하지 않습니다."
    )


html_card(
    f"""
    <div class="decision {decision_css}">

        <div class="decision-label">
            현재 기술구조
        </div>

        <div class="decision-title">
            {pattern_text}
        </div>

        <div class="decision-reason">
            {html.escape(pattern_reason)}
        </div>

        <div class="decision-rule">
            <b>판단 근거</b><br>
            종합점수 {score}/100 ·
            MA20 {fmt_price(last["MA20"])} ·
            MA60 {fmt_price(last["MA60"])} ·
            RSI {fmt_num(last["RSI"])} ·
            거래량 {fmt_num(last["VOL_RATIO"])}배
        </div>

    </div>
    """
)


# ============================================================
# 3. PRICE LEVEL
# ============================================================

section_title(
    "③ 가격 기준선",
    "판단을 숫자로 확인하는 구간입니다."
)


html_card(
    f"""
    <div class="level-grid">

        <div class="level">
            <div class="level-label">
                현재가
            </div>
            <div class="level-price">
                {fmt_price(close)}
            </div>
        </div>

        <div class="level">
            <div class="level-label">
                지지선
            </div>
            <div
                class="level-price"
                style="color:#62d99a;"
            >
                {fmt_price(support)}
            </div>
        </div>

        <div class="level">
            <div class="level-label">
                저항선
            </div>
            <div
                class="level-price"
                style="color:#ffb76c;"
            >
                {fmt_price(resistance)}
            </div>
        </div>

    </div>
    """
)


# ============================================================
# 4. HOLDING / NON HOLDING
# ============================================================

section_title(
    "④ 내 포지션",
    "보유 중인지에 따라 같은 차트도 다른 대응 시나리오를 보여줍니다."
)


holding_choice = st.radio(
    "현재 보유 여부",
    ["미보유", "보유"],
    horizontal=True,
)


holding = holding_choice == "보유"


avg_price = 0.0
shares = 0.0


if holding:

    c1, c2 = st.columns(
        2,
        gap="small"
    )

    with c1:

        avg_price = st.number_input(
            "평균 매수가",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.0f",
        )

    with c2:

        shares = st.number_input(
            "보유 수량",
            min_value=0.0,
            value=0.0,
            step=1.0,
            format="%.0f",
        )


guide = position_guide(
    df,
    holding,
    avg_price,
    shares,
)


# ============================================================
# POSITION DECISION
# ============================================================

html_card(
    f"""
    <div class="decision {guide["css"]}">

        <div class="decision-label">
            {"보유자 대응" if holding else "미보유자 대응"}
        </div>

        <div class="decision-title">
            {html.escape(guide["title"])}
        </div>

        <div class="decision-reason">
            {html.escape(guide["reason"])}
        </div>

        <div class="decision-rule">
            <b>판단 근거</b><br>
            {html.escape(guide["rule"])}
        </div>

    </div>
    """
)


# ============================================================
# HOLDING RESULT
# ============================================================

if holding:

    pnl_pct = guide["pnl_pct"]
    pnl_amount = guide["pnl_amount"]

    html_card(
        f"""
        <div class="holding-box">

            <div class="card-title">
                💼 보유 포지션
            </div>

            <div class="holding-result">

                <div class="holding-metric">
                    <div class="holding-label">
                        평균단가
                    </div>
                    <div class="holding-value">
                        {fmt_price(avg_price)}
                    </div>
                </div>

                <div class="holding-metric">
                    <div class="holding-label">
                        현재가
                    </div>
                    <div class="holding-value">
                        {fmt_price(close)}
                    </div>
                </div>

                <div class="holding-metric">
                    <div class="holding-label">
                        보유수량
                    </div>
                    <div class="holding-value">
                        {shares:,.0f}
                    </div>
                </div>

                <div class="holding-metric">
                    <div class="holding-label">
                        수익률
                    </div>
                    <div
                        class="holding-value"
                        style="color:{pct_color(pnl_pct)};"
                    >
                        {fmt_pct(pnl_pct)}
                    </div>
                </div>

                <div class="holding-metric">
                    <div class="holding-label">
                        평가손익
                    </div>
                    <div
                        class="holding-value"
                        style="color:{pct_color(pnl_amount)};"
                    >
                        {fmt_price(pnl_amount)}
                    </div>
                </div>

                <div class="holding-metric">
                    <div class="holding-label">
                        기술점수
                    </div>
                    <div class="holding-value">
                        {score}/100
                    </div>
                </div>

            </div>

        </div>
        """
    )


# ============================================================
# ACTION ROADMAP
# ============================================================

section_title(
    "⑤ 매매 시나리오",
    "현재 가격을 무조건 매수/매도로 단정하지 않고 조건이 충족될 때의 행동을 보여줍니다."
)


if holding:

    html_card(
        f"""
        <div class="card">

            <div class="card-title">
                ➕ 추가매수 검토
            </div>

            <div class="card-sub">
                상승 추세가 유지되고 MA20/지지선에서 반등 확인 시
            </div>

            <div class="decision-rule">
                MA20: <b>{fmt_price(guide["ma20"])}</b><br>
                지지선: <b>{fmt_price(guide["support"])}</b><br>
                RSI: <b>{guide["rsi"]:.0f}</b><br>
                조건: MA20 위 · RSI 과열 아님 · MACD 개선
            </div>

        </div>
        """
    )

    html_card(
        f"""
        <div class="card">

            <div class="card-title">
                💰 분할매도 검토
            </div>

            <div class="card-sub">
                저항선 접근 + 상승탄력 둔화가 동시에 나타날 때
            </div>

            <div class="decision-rule">
                주요 저항: <b>{fmt_price(guide["resistance"])}</b><br>
                RSI: <b>{guide["rsi"]:.0f}</b><br>
                조건: 저항 접근 · RSI 과열 · 거래량 둔화/음봉 확인
            </div>

        </div>
        """
    )

    html_card(
        f"""
        <div class="card">

            <div class="card-title">
                ⚠️ 리스크 재검토
            </div>

            <div class="card-sub">
                지지선이 무너질 경우 평균단가 낮추기보다 구조부터 재확인
            </div>

            <div class="decision-rule">
                중요 가격: <b>{fmt_price(guide["prev_support"])}</b><br>
                추가 확인: MA20 회복 여부 · MACD 방향 · 거래량
            </div>

        </div>
        """
    )

else:

    html_card(
        f"""
        <div class="card">

            <div class="card-title">
                🌱 신규 진입 후보
            </div>

            <div class="card-sub">
                현재 조건에 따라 접근 시나리오
            </div>

            <div class="decision-rule">

                <b>1. 눌림</b><br>
                MA20 / 지지선 부근에서 반등 확인
                → {fmt_price(support)} ~ {fmt_price(guide["ma20"])}
                <br><br>

                <b>2. 돌파</b><br>
                {fmt_price(guide["prev_resistance"])}
                돌파 + 거래량 증가
                → 돌파 후 재지지 확인
                <br><br>

                <b>3. 추격</b><br>
                RSI 70 이상 또는 MA20 대비 과도한 이격
                → 신규 진입보다 대기
                <br><br>

                <b>4. 약세</b><br>
                MA20 아래 + MACD 약세
                → 관망

            </div>

        </div>
        """
    )


# ============================================================
# 6. INDICATORS
# ============================================================

section_title(
    "⑥ 왜 그렇게 판단했는가?",
    "핵심 지표만 남겨 판단 카드 바로 아래에 배치했습니다."
)


rsi = safe_float(last["RSI"])
macd = safe_float(last["MACD"])
macd_signal = safe_float(last["MACD_SIGNAL"])
vol_ratio = safe_float(last["VOL_RATIO"])

indicator_html = f"""
<div class="indicator-grid">

    <div class="indicator">
        <div class="indicator-label">
            RSI(14)
        </div>
        <div class="indicator-value">
            {rsi:.1f}
        </div>
        <div class="indicator-note">
            {"과열" if rsi >= 70 else "중립" if rsi >= 45 else "약세"}
        </div>
    </div>

    <div class="indicator">
        <div class="indicator-label">
            MACD
        </div>
        <div class="indicator-value">
            {"상승" if macd > macd_signal else "약세"}
        </div>
        <div class="indicator-note">
            Signal 대비
        </div>
    </div>

    <div class="indicator">
        <div class="indicator-label">
            거래량
        </div>
        <div class="indicator-value">
            {vol_ratio:.1f}배
        </div>
        <div class="indicator-note">
            20일 평균 대비
        </div>
    </div>

    <div class="indicator">
        <div class="indicator-label">
            MA 구조
        </div>
        <div class="indicator-value">
            {"상승" if last["MA20"] > last["MA60"] else "약세"}
        </div>
        <div class="indicator-note">
            MA20 vs MA60
        </div>
    </div>

</div>
"""

html_card(indicator_html)


# ============================================================
# 7. CHART
# ============================================================

section_title(
    "⑦ 차트",
    "기본은 읽기 모드입니다. 분석할 때만 차트 조작을 켭니다."
)


chart_col1, chart_col2 = st.columns(
    [1.4, 1],
    gap="small"
)


with chart_col1:

    chart_period = st.selectbox(
        "기간",
        ["3개월", "6개월", "1년", "2년"],
        index=1,
        label_visibility="collapsed",
    )


with chart_col2:

    interactive_chart = st.checkbox(
        "차트 분석 모드",
        value=False,
    )


fig = make_price_chart(
    df,
    chart_period,
    interactive_chart,
)


st.plotly_chart(
    fig,
    width="stretch",
    config={
        "displayModeBar": False,
        "scrollZoom": False,
        "doubleClick": "reset",
        "responsive": True,
        "displaylogo": False,
    },
)


# ============================================================
# 8. CHART READING
# ============================================================

html_card(
    f"""
    <div class="card">

        <div class="card-title">
            차트 한줄 해석
        </div>

        <div class="decision-rule">

            현재가
            <b>{fmt_price(close)}</b>
            /
            MA20
            <b>{fmt_price(last["MA20"])}</b>
            /
            MA60
            <b>{fmt_price(last["MA60"])}</b>

            <br><br>

            현재 구조:
            <b>{html.escape(pattern)}</b>

            <br>

            지지:
            <b style="color:#62d99a;">
                {fmt_price(support)}
            </b>

            ·

            저항:
            <b style="color:#ffb76c;">
                {fmt_price(resistance)}
            </b>

        </div>

    </div>
    """
)


# ============================================================
# 9. VOLUME PROFILE
# ============================================================

section_title(
    "⑧ 매물대",
    "가격이 많이 거래된 구간을 확인합니다."
)


vp = volume_profile(df)


if not vp.empty:

    top_vp = vp.head(5).copy()

    for _, row in top_vp.iterrows():

        html_card(
            f"""
            <div class="watch-row">

                <div>
                    <div class="watch-name">
                        {fmt_price(row["price"])}
                    </div>

                    <div class="watch-small">
                        거래집중 가격
                    </div>
                </div>

                <div>
                    <div class="watch-small">
                        거래량
                    </div>

                    <div>
                        {row["volume"]/1_000_000:.1f}M
                    </div>
                </div>

                <div>
                    <div class="watch-small">
                        현재가 대비
                    </div>

                    <div>
                        {(row["price"]/close-1)*100:+.1f}%
                    </div>
                </div>

                <div>
                    <div class="watch-small">
                        위치
                    </div>

                    <div>
                        {"위" if row["price"] > close else "아래"}
                    </div>
                </div>

            </div>
            """
        )


# ============================================================
# 10. WATCHLIST
# ============================================================

section_title(
    "⑨ 관심종목",
    "미래준비 후보와 실제 관찰 종목을 한곳에서 관리합니다."
)


watch_add_col1, watch_add_col2 = st.columns(
    [3, 1],
    gap="small"
)


with watch_add_col1:

    watch_add = st.selectbox(
        "관심종목 추가",
        list(ETF_UNIVERSE.keys()),
        format_func=lambda x:
            ETF_UNIVERSE.get(x, x),
        label_visibility="collapsed",
    )


with watch_add_col2:

    if st.button(
        "＋ 추가",
        use_container_width=True,
    ):

        if watch_add not in st.session_state.watchlist:

            st.session_state.watchlist.append(
                watch_add
            )

            save_watchlist(
                st.session_state.watchlist
            )

            st.rerun()


for code in st.session_state.watchlist:

    if code not in ETF_UNIVERSE:
        continue

    wdf = load_etf_data(code)

    if wdf.empty:
        continue

    wdf = add_indicators(wdf)

    wlast = wdf.iloc[-1]

    wclose = safe_float(wlast["Close"])

    if len(wdf) >= 2:

        wprev = safe_float(
            wdf["Close"].iloc[-2]
        )

        wchange = (
            wclose / wprev - 1
        ) * 100

    else:

        wchange = 0

    wscore = technical_score(wdf)

    wpattern = detect_pattern(wdf)

    html_card(
        f"""
        <div class="watch-row">

            <div>
                <div class="watch-name">
                    {html.escape(ETF_UNIVERSE[code])}
                </div>

                <div class="watch-small">
                    {code} · {wpattern}
                </div>
            </div>

            <div>
                {fmt_price(wclose)}
            </div>

            <div
                style="color:{pct_color(wchange)};"
            >
                {fmt_pct(wchange)}
            </div>

            <div>
                {wscore}
            </div>

        </div>
        """
    )


# ============================================================
# 11. RESEARCH WORKFLOW
# ============================================================

section_title(
    "⑩ 사전 리서치",
    "아직 매수할 필요가 없는 종목도 미리 후보군으로 관리합니다."
)


html_card(
    """
    <div class="card">

        <div class="card-title">
            📚 ETF RADAR의 기본 순서
        </div>

        <div class="decision-rule">

            <b>STEP 1 · 미래준비 테마</b><br>
            어떤 테마로 자금이 이동하기 시작하는지 확인

            <br><br>

            <b>STEP 2 · 테마 순환</b><br>
            점화 → 확산 → 주도 → 과열 → 냉각 흐름 관찰

            <br><br>

            <b>STEP 3 · 후보 ETF</b><br>
            테마 안에서 아직 과열되지 않은 종목 선별

            <br><br>

            <b>STEP 4 · 기술구조</b><br>
            MA20 / MA60 / RSI / MACD / 거래량 확인

            <br><br>

            <b>STEP 5 · 가격</b><br>
            지지 / 저항 / 매물대 확인

            <br><br>

            <b>STEP 6 · 포지션</b><br>
            보유자는 추가매수·보유·분할매도 시나리오,
            미보유자는 신규진입·눌림·돌파 재확인 시나리오 확인

        </div>

    </div>
    """
)


# ============================================================
# FOOTNOTE
# ============================================================

html_card(
    """
    <div class="footnote">

        ※ ETF RADAR의 판단은 가격·거래량·이동평균·RSI·MACD 등
        공개 시장데이터를 이용한 규칙 기반 시나리오입니다.

        <br>

        ※ '매수 검토', '추가매수 검토', '분할매도 검토'는
        미래 수익을 보장하는 예측이나 개인별 투자자문이 아니라
        사용자가 판단할 수 있도록 조건과 근거를 정리한 것입니다.

        <br>

        ※ 테마의 '점화'는 미래 상승을 예측한다는 의미가 아니라
        최근 모멘텀 개선과 확산 여부를 조기에 관찰하기 위한 분류입니다.

    </div>
    """
)