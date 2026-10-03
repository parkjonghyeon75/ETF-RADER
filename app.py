import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import re
import time
import warnings

warnings.filterwarnings("ignore")

# ============================================================
# ETF RADAR v11
# ------------------------------------------------------------
# ETF Search Engine
# Theme Radar
# Theme -> ETF Auto Matching
# Market State
# Technical Analysis
# Support / Resistance
# Volume Profile
# 100 Point Score
# Pullback / Breakout / Chasing Risk
# Trading Scenario
# Mobile Financial UI
# ============================================================

st.set_page_config(
    page_title="ETF RADAR v11",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# GLOBAL STYLE
# ============================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont,
    "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 0%, rgba(35,90,180,.13), transparent 28%),
        radial-gradient(circle at 90% 10%, rgba(0,190,150,.08), transparent 25%),
        #07101d;
    color: #f5f7fb;
}

.block-container {
    max-width: 1250px;
    padding-top: 1rem;
    padding-bottom: 4rem;
}

h1, h2, h3 {
    letter-spacing: -0.5px;
}

.hero {
    padding: 22px 22px 18px 22px;
    border-radius: 22px;
    background:
        linear-gradient(135deg, rgba(20,38,65,.96), rgba(9,19,34,.96));
    border: 1px solid rgba(255,255,255,.08);
    box-shadow: 0 15px 45px rgba(0,0,0,.24);
    margin-bottom: 16px;
}

.hero-title {
    font-size: 30px;
    font-weight: 800;
    margin-bottom: 3px;
}

.hero-sub {
    color: #94a3b8;
    font-size: 13px;
}

.section-title {
    font-size: 19px;
    font-weight: 800;
    margin-top: 22px;
    margin-bottom: 10px;
}

.card {
    background: linear-gradient(
        145deg,
        rgba(18,31,51,.96),
        rgba(10,20,34,.96)
    );
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 18px;
    padding: 17px;
    margin-bottom: 10px;
}

.metric-label {
    color: #8190a6;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .5px;
}

.metric-value {
    font-size: 22px;
    font-weight: 800;
    margin-top: 3px;
}

.small {
    color: #8d9aae;
    font-size: 12px;
}

.green {
    color: #27d69b;
}

.red {
    color: #ff6b7d;
}

.yellow {
    color: #ffc857;
}

.blue {
    color: #65a8ff;
}

.score {
    font-size: 42px;
    font-weight: 900;
    line-height: 1;
}

.signal {
    display: inline-block;
    padding: 6px 11px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 800;
    background: rgba(255,255,255,.08);
}

.theme-card {
    min-height: 145px;
}

.theme-name {
    font-size: 17px;
    font-weight: 800;
}

.theme-score {
    font-size: 29px;
    font-weight: 900;
}

.theme-meta {
    color: #8290a3;
    font-size: 11px;
}

.reason {
    color: #bdc7d5;
    font-size: 13px;
    line-height: 1.55;
}

.scenario {
    border-left: 3px solid #4d9cff;
    padding: 10px 12px;
    background: rgba(255,255,255,.035);
    border-radius: 0 10px 10px 0;
    margin-bottom: 8px;
}

.scenario-title {
    font-weight: 800;
    font-size: 13px;
}

.scenario-price {
    font-size: 17px;
    font-weight: 800;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,.035);
    border: 1px solid rgba(255,255,255,.06);
    padding: 12px;
    border-radius: 14px;
}

.stButton button {
    border-radius: 12px;
    font-weight: 700;
}

.stTextInput input {
    border-radius: 14px;
}

@media (max-width: 700px) {
    .block-container {
        padding-left: 10px;
        padding-right: 10px;
    }

    .hero-title {
        font-size: 24px;
    }

    .section-title {
        font-size: 17px;
    }

    .score {
        font-size: 34px;
    }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# ETF MASTER DATA
# ============================================================

BASE_ETFS = [

    # AI / Semiconductor
    ("069500", "KODEX 200", "삼성자산운용", ["코스피", "대형주"]),
    ("091160", "KODEX 반도체", "삼성자산운용", ["반도체", "소부장"]),
    ("091170", "KODEX 은행", "삼성자산운용", ["은행", "금융"]),
    ("395160", "KODEX AI반도체핵심장비", "삼성자산운용", ["AI", "반도체", "장비"]),
    ("396500", "TIGER 반도체", "미래에셋자산운용", ["반도체"]),
    ("364690", "KODEX 혁신기술테마액티브", "삼성자산운용", ["혁신기술", "테크"]),
    ("381180", "TIGER 미국필라델피아반도체나스닥", "미래에셋자산운용", ["반도체", "미국"]),
    ("381170", "TIGER 미국테크TOP10 INDXX", "미래에셋자산운용", ["AI", "테크", "미국"]),
    ("465580", "ACE AI반도체포커스", "한국투자신탁운용", ["AI", "반도체"]),
    ("469150", "ACE AI반도체TOP3+", "한국투자신탁운용", ["AI", "반도체"]),
    ("494340", "TIGER AI반도체핵심공정", "미래에셋자산운용", ["AI", "반도체"]),
    ("494310", "TIGER AI전력기기TOP3", "미래에셋자산운용", ["AI", "전력"]),

    # Power / Nuclear / Energy
    ("487240", "KODEX AI전력핵심설비", "삼성자산운용", ["AI", "전력", "데이터센터"]),
    ("445670", "KODEX K-신재생에너지액티브", "삼성자산운용", ["신재생", "에너지"]),
    ("433250", "KODEX 원자력SMR", "삼성자산운용", ["원전", "SMR"]),
    ("442550", "ACE 글로벌원자력TOP10 SOLACTIVE", "한국투자신탁운용", ["원전"]),
    ("466950", "TIGER 글로벌AI&원전POWER", "미래에셋자산운용", ["AI", "원전", "전력"]),
    ("469170", "TIGER AI전력기기", "미래에셋자산운용", ["AI", "전력"]),
    ("486450", "SOL 미국AI전력인프라", "신한자산운용", ["AI", "전력", "미국"]),

    # Robot
    ("445290", "KODEX 로봇액티브", "삼성자산운용", ["로봇", "자동화"]),
    ("469070", "RISE AI&로봇", "KB자산운용", ["AI", "로봇"]),
    ("461950", "KODEX 2차전지핵심소재10", "삼성자산운용", ["2차전지"]),
    ("450910", "SOL 코리아메가트렌드", "신한자산운용", ["AI", "로봇", "미래산업"]),
    ("475050", "ACE KPOP포커스", "한국투자신탁운용", ["K콘텐츠"]),

    # Defense / Aerospace
    ("449450", "PLUS K방산", "한화자산운용", ["방산"]),
    ("463250", "TIGER K방산&우주", "미래에셋자산운용", ["방산", "우주"]),
    ("494370", "KODEX 방산TOP10", "삼성자산운용", ["방산"]),
    ("469060", "RISE K방산", "KB자산운용", ["방산"]),

    # Shipbuilding
    ("466920", "SOL 조선TOP3플러스", "신한자산운용", ["조선"]),
    ("494360", "KODEX 조선TOP10", "삼성자산운용", ["조선"]),
    ("466930", "TIGER 조선TOP10", "미래에셋자산운용", ["조선"]),

    # Battery
    ("305720", "KODEX 2차전지산업", "삼성자산운용", ["2차전지"]),
    ("364980", "TIGER 2차전지테마", "미래에셋자산운용", ["2차전지"]),
    ("455850", "SOL 2차전지소부장Fn", "신한자산운용", ["2차전지", "소부장"]),

    # Bio
    ("244580", "KODEX 바이오", "삼성자산운용", ["바이오"]),
    ("364970", "TIGER 바이오TOP10", "미래에셋자산운용", ["바이오"]),
    ("464470", "PLUS K바이오", "한화자산운용", ["바이오"]),

    # Finance / Dividend
    ("279530", "KODEX 고배당", "삼성자산운용", ["고배당"]),
    ("161510", "PLUS 고배당주", "한화자산운용", ["고배당"]),
    ("211560", "TIGER 배당성장", "미래에셋자산운용", ["배당"]),
]


# ============================================================
# THEME DEFINITIONS
# ============================================================

THEMES = {

    "AI 반도체": {
        "keywords": [
            "AI", "인공지능", "반도체", "HBM",
            "메모리", "파운드리", "소부장"
        ],
        "etf_keywords": [
            "AI", "반도체", "HBM", "소부장"
        ],
        "color": "blue"
    },

    "AI 전력·데이터센터": {
        "keywords": [
            "전력", "전력기기", "데이터센터",
            "전력망", "AI전력", "변압기",
            "케이블", "냉각"
        ],
        "etf_keywords": [
            "전력", "AI전력", "데이터센터"
        ],
        "color": "yellow"
    },

    "원전·SMR": {
        "keywords": [
            "원전", "원자력", "SMR",
            "소형모듈원자로"
        ],
        "etf_keywords": [
            "원전", "원자력", "SMR"
        ],
        "color": "yellow"
    },

    "휴머노이드·로봇": {
        "keywords": [
            "로봇", "휴머노이드",
            "자동화", "피지컬AI"
        ],
        "etf_keywords": [
            "로봇", "휴머노이드", "자동화"
        ],
        "color": "green"
    },

    "방산·우주": {
        "keywords": [
            "방산", "방위산업",
            "우주", "항공", "미사일"
        ],
        "etf_keywords": [
            "방산", "우주"
        ],
        "color": "red"
    },

    "조선·해양": {
        "keywords": [
            "조선", "해양",
            "LNG", "선박"
        ],
        "etf_keywords": [
            "조선"
        ],
        "color": "blue"
    },

    "2차전지": {
        "keywords": [
            "2차전지", "배터리",
            "리튬", "전기차"
        ],
        "etf_keywords": [
            "2차전지", "배터리"
        ],
        "color": "green"
    },

    "바이오": {
        "keywords": [
            "바이오", "제약",
            "헬스케어", "신약"
        ],
        "etf_keywords": [
            "바이오"
        ],
        "color": "green"
    },

    "신재생·수소": {
        "keywords": [
            "신재생", "태양광",
            "풍력", "수소", "친환경"
        ],
        "etf_keywords": [
            "신재생", "수소"
        ],
        "color": "green"
    },

    "K-콘텐츠": {
        "keywords": [
            "KPOP", "콘텐츠",
            "엔터", "게임"
        ],
        "etf_keywords": [
            "KPOP", "콘텐츠"
        ],
        "color": "blue"
    },

    "금융·배당": {
        "keywords": [
            "은행", "금융",
            "배당", "고배당", "보험"
        ],
        "etf_keywords": [
            "은행", "배당", "고배당"
        ],
        "color": "yellow"
    },

    "K-대형주": {
        "keywords": [
            "코스피", "대형주",
            "삼성전자", "SK하이닉스"
        ],
        "etf_keywords": [
            "200", "대형주"
        ],
        "color": "blue"
    },
}


# ============================================================
# SESSION STATE
# ============================================================

if "selected_etf" not in st.session_state:
    st.session_state.selected_etf = "091160"

if "etf_master" not in st.session_state:
    st.session_state.etf_master = None

if "theme_cache_time" not in st.session_state:
    st.session_state.theme_cache_time = None


# ============================================================
# UTILITIES
# ============================================================

def normalize_code(code):
    code = str(code).strip()
    code = re.sub(r"\D", "", code)
    if len(code) <= 6:
        return code.zfill(6)
    return code


def yf_symbol(code):
    return normalize_code(code) + ".KS"


def safe_float(value, default=np.nan):
    try:
        return float(value)
    except:
        return default


def pct_change(series, periods=1):
    if series is None or len(series) <= periods:
        return np.nan

    try:
        return (series.iloc[-1] / series.iloc[-periods - 1] - 1) * 100
    except:
        return np.nan


def fmt_price(value):
    if pd.isna(value):
        return "-"
    return f"{value:,.0f}"


def fmt_pct(value):
    if pd.isna(value):
        return "-"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def color_class(value):
    if pd.isna(value):
        return "small"
    if value > 0:
        return "green"
    if value < 0:
        return "red"
    return "yellow"


# ============================================================
# KRX ETF MASTER
# ============================================================

@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def load_krx_etf_master():

    rows = []

    # --------------------------------------------------------
    # Try pykrx
    # --------------------------------------------------------

    try:

        from pykrx import stock

        today = datetime.now()

        for delta in range(0, 8):

            d = today - timedelta(days=delta)
            date_str = d.strftime("%Y%m%d")

            try:
                tickers = stock.get_etf_ticker_list(date_str)

                if tickers:
                    for code in tickers:

                        try:
                            name = stock.get_etf_ticker_name(code)
                        except:
                            name = ""

                        if name:
                            rows.append({
                                "code": normalize_code(code),
                                "name": name,
                                "manager": "",
                                "source": "KRX"
                            })

                    if rows:
                        break

            except:
                continue

    except Exception:
        pass

    # --------------------------------------------------------
    # Always add local seed universe
    # --------------------------------------------------------

    for code, name, manager, tags in BASE_ETFS:

        rows.append({
            "code": normalize_code(code),
            "name": name,
            "manager": manager,
            "source": "LOCAL"
        })

    if not rows:
        return pd.DataFrame(
            columns=["code", "name", "manager", "source"]
        )

    df = pd.DataFrame(rows)

    df["code"] = df["code"].map(normalize_code)

    df = df.drop_duplicates(
        subset=["code"],
        keep="first"
    )

    return df.reset_index(drop=True)


# ============================================================
# ETF SEARCH ENGINE
# ============================================================

def search_etfs(query, master, limit=80):

    if master is None or master.empty:
        return pd.DataFrame()

    q = str(query).strip().lower()

    if not q:
        return master.head(limit).copy()

    # code exact
    exact = master[
        master["code"].str.lower() == q
    ]

    if not exact.empty:
        return exact

    # remove spaces
    q_clean = re.sub(r"\s+", "", q)

    work = master.copy()

    work["_name"] = (
        work["name"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.replace(" ", "", regex=False)
    )

    work["_manager"] = (
        work["manager"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    work["_code"] = work["code"].astype(str)

    mask = (
        work["_name"].str.contains(q_clean, na=False)
        |
        work["_manager"].str.contains(q, na=False)
        |
        work["_code"].str.contains(q_clean, na=False)
    )

    result = work[mask].copy()

    # Korean ETF common aliases
    aliases = {
        "삼성": "kodex",
        "미래": "tiger",
        "미래에셋": "tiger",
        "한국투자": "ace",
        "한투": "ace",
        "kb": "rise",
        "신한": "sol",
        "한화": "plus",
        "nh": "hanaro",
    }

    if result.empty and q in aliases:

        alias = aliases[q]

        result = work[
            work["_name"].str.contains(
                alias,
                na=False
            )
        ]

    return result.head(limit).drop(
        columns=["_name", "_manager", "_code"],
        errors="ignore"
    )


# ============================================================
# DOWNLOAD DATA
# ============================================================

@st.cache_data(ttl=60 * 15, show_spinner=False)
def download_etf_data(code, period="1y"):

    symbol = yf_symbol(code)

    try:

        df = yf.download(
            symbol,
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.columns = [
            str(c).lower()
            for c in df.columns
        ]

        required = [
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]

        for c in required:
            if c not in df.columns:
                df[c] = np.nan

        df = df[required].copy()

        df = df.dropna(
            subset=["close"]
        )

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# MARKET DATA
# ============================================================

@st.cache_data(ttl=60 * 15, show_spinner=False)
def download_market_data():

    indexes = {
        "KOSPI": "^KS11",
        "KOSDAQ": "^KQ11",
        "NASDAQ": "^IXIC",
        "S&P500": "^GSPC",
        "SOX": "^SOX"
    }

    output = {}

    for name, symbol in indexes.items():

        try:

            df = yf.download(
                symbol,
                period="3mo",
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=False
            )

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if not df.empty:
                output[name] = df

        except:
            continue

    return output


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

def calculate_indicators(df):

    data = df.copy()

    close = data["close"]
    high = data["high"]
    low = data["low"]
    volume = data["volume"]

    # Moving averages
    data["ma5"] = close.rolling(5).mean()
    data["ma20"] = close.rolling(20).mean()
    data["ma60"] = close.rolling(60).mean()
    data["ma120"] = close.rolling(120).mean()

    # RSI
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    data["rsi"] = 100 - (
        100 / (1 + rs)
    )

    # MACD
    ema12 = close.ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = close.ewm(
        span=26,
        adjust=False
    ).mean()

    data["macd"] = ema12 - ema26
    data["macd_signal"] = data["macd"].ewm(
        span=9,
        adjust=False
    ).mean()

    data["macd_hist"] = (
        data["macd"] -
        data["macd_signal"]
    )

    # Bollinger
    mid = close.rolling(20).mean()
    std = close.rolling(20).std()

    data["bb_mid"] = mid
    data["bb_upper"] = mid + std * 2
    data["bb_lower"] = mid - std * 2

    # ATR
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    tr = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    data["atr"] = tr.rolling(14).mean()

    # Volume
    data["volume_ma20"] = volume.rolling(20).mean()

    data["volume_ratio"] = (
        volume /
        data["volume_ma20"].replace(0, np.nan)
    )

    # Momentum
    data["return_5"] = close.pct_change(5) * 100
    data["return_20"] = close.pct_change(20) * 100
    data["return_60"] = close.pct_change(60) * 100

    # High / Low
    data["high_20"] = high.rolling(20).max()
    data["low_20"] = low.rolling(20).min()

    return data


# ============================================================
# SUPPORT / RESISTANCE
# ============================================================

def calculate_support_resistance(df):

    close = df["close"]

    recent = close.tail(120)

    supports = []
    resistances = []

    for window in [10, 20, 40, 60]:

        if len(recent) < window:
            continue

        supports.append(
            recent.tail(window).min()
        )

        resistances.append(
            recent.tail(window).max()
        )

    support = np.nanmedian(supports)
    resistance = np.nanmedian(resistances)

    current = close.iloc[-1]

    # Additional local levels
    rolling_low = (
        df["low"]
        .rolling(20)
        .min()
        .iloc[-1]
    )

    rolling_high = (
        df["high"]
        .rolling(20)
        .max()
        .iloc[-1]
    )

    support = np.nanmin([
        support,
        rolling_low
    ])

    resistance = np.nanmax([
        resistance,
        rolling_high
    ])

    return support, resistance


# ============================================================
# VOLUME PROFILE
# ============================================================

def volume_profile(df, bins=28):

    data = df.tail(120).copy()

    if data.empty:
        return pd.DataFrame()

    low = data["low"].min()
    high = data["high"].max()

    if low == high:
        return pd.DataFrame()

    data["price_bin"] = pd.cut(
        data["close"],
        bins=bins
    )

    grouped = (
        data.groupby(
            "price_bin",
            observed=True
        )["volume"]
        .sum()
    )

    result = pd.DataFrame({
        "volume": grouped
    })

    result["price"] = [
        interval.mid
        for interval in result.index
    ]

    return result.sort_values(
        "volume",
        ascending=False
    )


# ============================================================
# SCORE ENGINE
# ============================================================

def calculate_score(data):

    if data.empty:
        return {
            "total": 0,
            "trend": 0,
            "momentum": 0,
            "volume": 0,
            "technical": 0,
            "risk": 0
        }

    last = data.iloc[-1]

    score = 0

    # Trend 25
    trend = 0

    if last["close"] > last["ma20"]:
        trend += 8

    if last["ma20"] > last["ma60"]:
        trend += 8

    if last["ma60"] > last["ma120"]:
        trend += 5

    if last["ma5"] > last["ma20"]:
        trend += 4

    trend = min(trend, 25)

    # Momentum 25
    momentum = 0

    rsi = safe_float(last["rsi"])

    if 50 <= rsi <= 70:
        momentum += 10
    elif rsi > 70:
        momentum += 5
    elif rsi >= 40:
        momentum += 6

    if last["macd"] > last["macd_signal"]:
        momentum += 8

    if last["return_20"] > 0:
        momentum += 7

    momentum = min(momentum, 25)

    # Volume 20
    volume_score = 0

    vr = safe_float(
        last["volume_ratio"],
        1
    )

    if vr >= 1.5:
        volume_score = 20
    elif vr >= 1.2:
        volume_score = 16
    elif vr >= 1:
        volume_score = 12
    elif vr >= .8:
        volume_score = 8
    else:
        volume_score = 4

    # Technical 20
    technical = 0

    if last["close"] > last["bb_mid"]:
        technical += 8

    if last["macd_hist"] > 0:
        technical += 6

    if last["return_5"] > 0:
        technical += 6

    technical = min(
        technical,
        20
    )

    # Risk 10
    risk = 5

    if rsi > 78:
        risk = 2
    elif rsi > 72:
        risk = 4
    elif rsi < 35:
        risk = 6
    elif 45 <= rsi <= 65:
        risk = 8
    else:
        risk = 7

    total = (
        trend +
        momentum +
        volume_score +
        technical +
        risk
    )

    return {
        "total": int(round(total)),
        "trend": int(round(trend)),
        "momentum": int(round(momentum)),
        "volume": int(round(volume_score)),
        "technical": int(round(technical)),
        "risk": int(round(risk))
    }


# ============================================================
# SIGNAL ENGINE
# ============================================================

def signal_from_data(data):

    if data.empty:
        return "데이터 없음"

    last = data.iloc[-1]

    score = calculate_score(data)["total"]

    rsi = safe_float(last["rsi"])

    if (
        score >= 80
        and rsi < 72
        and last["close"] > last["ma20"]
    ):
        return "강한 상승"

    if (
        score >= 70
        and last["close"] > last["ma20"]
    ):
        return "상승 추세"

    if (
        last["close"] > last["ma20"]
        and last["macd"] > last["macd_signal"]
    ):
        return "상승 전환"

    if (
        last["close"] < last["ma20"]
        and last["macd"] < last["macd_signal"]
    ):
        return "조정 / 약세"

    return "중립"


# ============================================================
# MARKET STATE
# ============================================================

def calculate_market_state():

    market = download_market_data()

    rows = []

    for name, df in market.items():

        if df is None or df.empty:
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close_col = "Close"

        if close_col not in df.columns:
            continue

        close = df[close_col].dropna()

        if len(close) < 20:
            continue

        current = close.iloc[-1]

        d1 = pct_change(close, 1)
        d5 = pct_change(close, 5)
        d20 = pct_change(close, 20)

        ma20 = close.rolling(20).mean().iloc[-1]

        rows.append({
            "시장": name,
            "현재": current,
            "1D": d1,
            "5D": d5,
            "20D": d20,
            "MA20": ma20,
            "추세": "상승" if current > ma20 else "약세"
        })

    return pd.DataFrame(rows)


def overall_market_signal(market_df):

    if market_df.empty:
        return "시장 데이터 부족"

    score = 0

    for _, row in market_df.iterrows():

        if row["1D"] > 0:
            score += 1

        if row["5D"] > 0:
            score += 1

        if row["20D"] > 0:
            score += 1

        if row["현재"] > row["MA20"]:
            score += 1

    max_score = len(market_df) * 4

    ratio = score / max_score if max_score else 0

    if ratio >= .72:
        return "Risk-On"

    if ratio >= .5:
        return "혼조 / 중립"

    return "Risk-Off"


# ============================================================
# THEME -> ETF MATCHING
# ============================================================

def theme_matches_etf(name, tags, theme):

    definition = THEMES[theme]

    text = (
        str(name) + " " +
        " ".join(tags)
    ).lower()

    hits = 0

    for keyword in (
        definition["keywords"] +
        definition["etf_keywords"]
    ):

        if keyword.lower() in text:
            hits += 1

    return hits


def get_theme_etfs(theme, master):

    definition = THEMES[theme]

    records = []

    # First use local BASE_ETFS because tags are explicit
    for code, name, manager, tags in BASE_ETFS:

        score = theme_matches_etf(
            name,
            tags,
            theme
        )

        if score > 0:

            records.append({
                "code": code,
                "name": name,
                "manager": manager,
                "match": score
            })

    # KRX master keyword fallback
    if master is not None and not master.empty:

        for _, row in master.iterrows():

            name = str(row["name"])

            score = 0

            text = name.lower()

            for keyword in (
                definition["keywords"] +
                definition["etf_keywords"]
            ):

                if keyword.lower() in text:
                    score += 1

            if score > 0:

                records.append({
                    "code": row["code"],
                    "name": name,
                    "manager": row.get(
                        "manager",
                        ""
                    ),
                    "match": score
                })

    if not records:
        return pd.DataFrame()

    result = pd.DataFrame(records)

    result = result.drop_duplicates(
        subset=["code"]
    )

    return result.sort_values(
        "match",
        ascending=False
    )


# ============================================================
# THEME MOMENTUM
# ============================================================

@st.cache_data(ttl=60 * 20, show_spinner=False)
def calculate_theme_radar(master):

    rows = []

    for theme in THEMES.keys():

        etfs = get_theme_etfs(
            theme,
            master
        )

        returns_5 = []
        returns_20 = []
        volume_ratios = []
        scores = []

        for _, row in etfs.head(8).iterrows():

            df = download_etf_data(
                row["code"],
                "3mo"
            )

            if df.empty:
                continue

            data = calculate_indicators(df)

            if data.empty:
                continue

            last = data.iloc[-1]

            returns_5.append(
                safe_float(
                    last["return_5"],
                    0
                )
            )

            returns_20.append(
                safe_float(
                    last["return_20"],
                    0
                )
            )

            volume_ratios.append(
                safe_float(
                    last["volume_ratio"],
                    1
                )
            )

            scores.append(
                calculate_score(data)["total"]
            )

        if not scores:
            continue

        avg5 = np.mean(returns_5)
        avg20 = np.mean(returns_20)
        avgvol = np.mean(volume_ratios)
        avgscore = np.mean(scores)

        momentum = (
            avg5 * 2.0 +
            avg20 * 0.8 +
            (avgvol - 1) * 12 +
            avgscore * 0.35
        )

        # Normalize to 0-100
        radar_score = np.clip(
            50 + momentum * 1.6,
            0,
            100
        )

        rows.append({
            "theme": theme,
            "score": float(radar_score),
            "5D": avg5,
            "20D": avg20,
            "volume": avgvol,
            "etf_count": len(etfs)
        })

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).sort_values(
        "score",
        ascending=False
    )


# ============================================================
# THEME EXPLANATION
# ============================================================

def theme_reason(row):

    reasons = []

    if row["5D"] > 2:
        reasons.append(
            "최근 5거래일 상승 모멘텀이 강합니다."
        )
    elif row["5D"] > 0:
        reasons.append(
            "단기 상승 흐름이 유지되고 있습니다."
        )
    else:
        reasons.append(
            "단기 수익률은 아직 약한 편입니다."
        )

    if row["20D"] > 5:
        reasons.append(
            "20일 기준 중기 추세도 양호합니다."
        )
    elif row["20D"] > 0:
        reasons.append(
            "중기 추세는 플러스권입니다."
        )

    if row["volume"] >= 1.3:
        reasons.append(
            "관련 ETF의 거래량이 평균보다 증가하고 있습니다."
        )
    elif row["volume"] >= 1:
        reasons.append(
            "거래활동이 평균 수준 이상입니다."
        )

    return " ".join(reasons)


# ============================================================
# CHART
# ============================================================

def make_price_chart(data):

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=.04,
        row_heights=[
            .58,
            .20,
            .22
        ]
    )

    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            name="가격"
        ),
        row=1,
        col=1
    )

    for col, name in [
        ("ma20", "MA20"),
        ("ma60", "MA60"),
        ("ma120", "MA120")
    ]:

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data[col],
                name=name,
                mode="lines",
                line=dict(width=1.5)
            ),
            row=1,
            col=1
        )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["bb_upper"],
            name="BB Upper",
            line=dict(
                width=1,
                dash="dot"
            )
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["bb_lower"],
            name="BB Lower",
            line=dict(
                width=1,
                dash="dot"
            )
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data["volume"],
            name="거래량"
        ),
        row=2,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["rsi"],
            name="RSI",
            line=dict(width=1.5)
        ),
        row=3,
        col=1
    )

    fig.add_hline(
        y=70,
        line_dash="dot",
        row=3,
        col=1
    )

    fig.add_hline(
        y=30,
        line_dash="dot",
        row=3,
        col=1
    )

    fig.update_layout(
        height=650,
        margin=dict(
            l=5,
            r=5,
            t=15,
            b=5
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#cbd5e1"
        ),
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0
        )
    )

    fig.update_xaxes(
        showgrid=False
    )

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,.05)"
    )

    return fig


# ============================================================
# TRADING SCENARIO
# ============================================================

def build_scenarios(data):

    last = data.iloc[-1]

    current = last["close"]

    support, resistance = (
        calculate_support_resistance(data)
    )

    atr = safe_float(
        last["atr"],
        current * .02
    )

    pullback_low = max(
        support,
        current - atr * 1.2
    )

    pullback_high = max(
        pullback_low,
        current - atr * .3
    )

    breakout = max(
        resistance,
        last["high_20"]
    )

    chasing = current + atr * .8

    stop = support - atr * .5

    return {
        "현재가": current,
        "눌림매수": (
            pullback_low,
            pullback_high
        ),
        "돌파매수": breakout,
        "추격주의": chasing,
        "추세훼손": stop,
        "지지": support,
        "저항": resistance
    }


def scenario_text(data):

    s = build_scenarios(data)

    current = s["현재가"]

    return [

        (
            "눌림목 대응",
            f"{fmt_price(s['눌림매수'][0])} ~ "
            f"{fmt_price(s['눌림매수'][1])}",
            "현재가를 추격하기보다 단기 지지권 접근 여부를 확인합니다."
        ),

        (
            "돌파 대응",
            fmt_price(s["돌파매수"]),
            "저항을 거래량 증가와 함께 돌파하는지 확인합니다."
        ),

        (
            "추격 주의",
            fmt_price(s["추격주의"]),
            "ATR 기준 단기 과열 가능성이 커지는 구간입니다."
        ),

        (
            "추세 훼손",
            fmt_price(s["추세훼손"]),
            "핵심 지지선 이탈 시 기존 상승 시나리오를 다시 점검합니다."
        )
    ]


# ============================================================
# ETF ANALYSIS
# ============================================================

def analyze_etf(code):

    df = download_etf_data(
        code,
        "1y"
    )

    if df.empty:
        return None

    data = calculate_indicators(df)

    if data.empty:
        return None

    last = data.iloc[-1]

    score = calculate_score(data)

    support, resistance = (
        calculate_support_resistance(data)
    )

    scenario = build_scenarios(data)

    return {
        "raw": df,
        "data": data,
        "last": last,
        "score": score,
        "support": support,
        "resistance": resistance,
        "scenario": scenario,
        "signal": signal_from_data(data)
    }


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">

<div class="hero-title">
📡 ETF RADAR <span style="color:#65a8ff;">v11</span>
</div>

<div class="hero-sub">
ETF Search · Market State · Theme Radar · Technical Analysis
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# LOAD MASTER
# ============================================================

with st.spinner("ETF 종목 DB를 준비하고 있습니다..."):

    master = load_krx_etf_master()

st.session_state.etf_master = master


# ============================================================
# SEARCH
# ============================================================

st.markdown(
    '<div class="section-title">🔎 ETF SEARCH</div>',
    unsafe_allow_html=True
)

search_col1, search_col2 = st.columns(
    [4, 1]
)

with search_col1:

    query = st.text_input(
        "ETF 검색",
        placeholder="종목명 / 코드 / 운용사를 입력하세요  예) AI반도체, KODEX, 091160",
        label_visibility="collapsed"
    )

with search_col2:

    refresh = st.button(
        "↻ ETF DB",
        use_container_width=True
    )

if refresh:

    st.cache_data.clear()

    st.rerun()


search_results = search_etfs(
    query,
    master,
    limit=80
)

if not search_results.empty:

    display_options = {}

    for _, row in search_results.iterrows():

        label = (
            f"{row['name']}  "
            f"({row['code']})"
        )

        display_options[label] = row["code"]

    selected_label = st.selectbox(
        "검색 결과",
        list(display_options.keys()),
        label_visibility="collapsed"
    )

    if selected_label:

        st.session_state.selected_etf = (
            display_options[selected_label]
        )


# ============================================================
# MARKET STATE
# ============================================================

st.markdown(
    '<div class="section-title">🌐 MARKET STATE</div>',
    unsafe_allow_html=True
)

market_df = calculate_market_state()

market_signal = overall_market_signal(
    market_df
)

if market_signal == "Risk-On":
    signal_color = "green"
elif market_signal == "Risk-Off":
    signal_color = "red"
else:
    signal_color = "yellow"

st.markdown(
    f"""
<div class="card">

<div style="display:flex;justify-content:space-between;align-items:center;">

<div>
<div class="metric-label">GLOBAL MARKET CONDITION</div>
<div class="metric-value {signal_color}">
{market_signal}
</div>
</div>

<div style="text-align:right;">
<div class="small">
{datetime.now().strftime("%Y-%m-%d %H:%M")}
</div>
<div class="small">
KOSPI · KOSDAQ · NASDAQ · S&P500 · SOX
</div>
</div>

</div>

</div>
""",
    unsafe_allow_html=True
)

if not market_df.empty:

    cols = st.columns(
        min(len(market_df), 5)
    )

    for i, (_, row) in enumerate(
        market_df.iterrows()
    ):

        with cols[i % len(cols)]:

            cls = color_class(
                row["1D"]
            )

            st.markdown(
                f"""
<div class="card">

<div class="metric-label">
{row['시장']}
</div>

<div class="metric-value">
{row['현재']:,.1f}
</div>

<div class="{cls}">
{fmt_pct(row['1D'])}
</div>

<div class="small">
5D {fmt_pct(row['5D'])}
&nbsp;·&nbsp;
20D {fmt_pct(row['20D'])}
</div>

</div>
""",
                unsafe_allow_html=True
            )


# ============================================================
# THEME RADAR
# ============================================================

st.markdown(
    '<div class="section-title">🔥 THEME RADAR</div>',
    unsafe_allow_html=True
)

theme_col1, theme_col2 = st.columns(
    [5, 1]
)

with theme_col1:

    st.markdown(
        """
<div class="small">
시장 데이터 기반으로 테마별 ETF의 단기·중기 모멘텀,
거래량 및 기술적 흐름을 종합합니다.
</div>
""",
        unsafe_allow_html=True
    )

with theme_col2:

    if st.button(
        "↻ 테마 업데이트",
        use_container_width=True
    ):

        calculate_theme_radar.clear()

        st.rerun()


theme_df = calculate_theme_radar(
    master
)

if theme_df.empty:

    st.warning(
        "테마 데이터를 아직 충분히 확보하지 못했습니다."
    )

else:

    top_themes = theme_df.head(8)

    for start in range(
        0,
        len(top_themes),
        2
    ):

        cols = st.columns(2)

        for j in range(2):

            idx = start + j

            if idx >= len(top_themes):
                continue

            row = top_themes.iloc[idx]

            score = row["score"]

            if score >= 80:
                level = "🔥 강세"
                cls = "green"

            elif score >= 65:
                level = "▲ 관심"
                cls = "blue"

            elif score >= 50:
                level = "→ 중립"
                cls = "yellow"

            else:
                level = "▼ 약세"
                cls = "red"

            reason = theme_reason(row)

            with cols[j]:

                st.markdown(
                    f"""
<div class="card theme-card">

<div style="display:flex;
justify-content:space-between;
align-items:flex-start;">

<div>

<div class="theme-name">
{row['theme']}
</div>

<div class="theme-meta">
관련 ETF {row['etf_count']}개
</div>

</div>

<div style="text-align:right">

<div class="theme-score {cls}">
{score:.0f}
</div>

<div class="{cls}">
{level}
</div>

</div>

</div>

<div style="margin-top:12px"
class="reason">

{reason}

</div>

<div class="theme-meta"
style="margin-top:8px">

5D {fmt_pct(row['5D'])}
&nbsp; · &nbsp;
20D {fmt_pct(row['20D'])}
&nbsp; · &nbsp;
거래량 {row['volume']:.1f}x

</div>

</div>
""",
                    unsafe_allow_html=True
                )


# ============================================================
# THEME ETF MATCHING
# ============================================================

st.markdown(
    '<div class="section-title">🧩 THEME → ETF MATCHING</div>',
    unsafe_allow_html=True
)

theme_names = list(THEMES.keys())

selected_theme = st.selectbox(
    "테마 선택",
    theme_names,
    index=0
)

theme_etfs = get_theme_etfs(
    selected_theme,
    master
)

if theme_etfs.empty:

    st.info(
        "현재 데이터베이스에서 연결되는 ETF를 찾지 못했습니다."
    )

else:

    st.markdown(
        f"""
<div class="small">
<strong>{selected_theme}</strong> 관련 ETF
· 키워드 및 종목명 기준 자동 매칭
</div>
""",
        unsafe_allow_html=True
    )

    # calculate quick ranking
    ranking = []

    for _, row in theme_etfs.head(12).iterrows():

        data = download_etf_data(
            row["code"],
            "3mo"
        )

        if data.empty:
            continue

        ind = calculate_indicators(data)

        if ind.empty:
            continue

        score = calculate_score(ind)

        last = ind.iloc[-1]

        ranking.append({
            "code": row["code"],
            "name": row["name"],
            "price": last["close"],
            "d1": pct_change(
                ind["close"],
                1
            ),
            "d20": pct_change(
                ind["close"],
                20
            ),
            "score": score["total"]
        })

    ranking_df = pd.DataFrame(
        ranking
    )

    if not ranking_df.empty:

        for _, row in ranking_df.head(8).iterrows():

            cls = color_class(
                row["d1"]
            )

            c1, c2, c3, c4 = st.columns(
                [3.5, 1.3, 1.3, 1.2]
            )

            with c1:
                st.markdown(
                    f"""
<div class="card">
<strong>{row['name']}</strong>
<div class="small">
{row['code']}
</div>
</div>
""",
                    unsafe_allow_html=True
                )

            with c2:
                st.metric(
                    "현재가",
                    fmt_price(row["price"])
                )

            with c3:
                st.markdown(
                    f"""
<div class="card">
<div class="metric-label">20D</div>
<div class="{color_class(row['d20'])}"
style="font-size:18px;font-weight:800;">
{fmt_pct(row['d20'])}
</div>
</div>
""",
                    unsafe_allow_html=True
                )

            with c4:
                st.markdown(
                    f"""
<div class="card">
<div class="metric-label">SCORE</div>
<div style="font-size:20px;font-weight:900;">
{row['score']}
</div>
</div>
""",
                    unsafe_allow_html=True
                )


# ============================================================
# SELECTED ETF
# ============================================================

code = st.session_state.selected_etf

selected_info = master[
    master["code"] == code
]

if not selected_info.empty:

    etf_name = selected_info.iloc[0]["name"]
    manager = selected_info.iloc[0].get(
        "manager",
        ""
    )

else:

    etf_name = code
    manager = ""


st.markdown(
    '<div class="section-title">📊 ETF ANALYSIS</div>',
    unsafe_allow_html=True
)

analysis = analyze_etf(
    code
)

if analysis is None:

    st.error(
        f"{etf_name}의 가격 데이터를 가져오지 못했습니다."
    )

    st.stop()


data = analysis["data"]
last = analysis["last"]
score = analysis["score"]
signal = analysis["signal"]


# ============================================================
# ETF HEADER
# ============================================================

price = last["close"]
day_change = pct_change(
    data["close"],
    1
)

st.markdown(
    f"""
<div class="card">

<div style="display:flex;
justify-content:space-between;
align-items:center;">

<div>

<div class="metric-label">
{code} · {manager}
</div>

<div style="font-size:25px;font-weight:900;">
{etf_name}
</div>

</div>

<div style="text-align:right">

<div style="font-size:28px;font-weight:900;">
{fmt_price(price)}
</div>

<div class="{color_class(day_change)}"
style="font-size:15px;font-weight:800;">
{fmt_pct(day_change)}
</div>

</div>

</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# SCORE CARDS
# ============================================================

c1, c2, c3, c4, c5 = st.columns(5)

with c1:

    st.metric(
        "종합점수",
        f"{score['total']}/100"
    )

with c2:

    st.metric(
        "추세",
        f"{score['trend']}/25"
    )

with c3:

    st.metric(
        "모멘텀",
        f"{score['momentum']}/25"
    )

with c4:

    st.metric(
        "거래량",
        f"{score['volume']}/20"
    )

with c5:

    st.metric(
        "기술",
        f"{score['technical']}/20"
    )


# ============================================================
# SIGNAL / INDICATORS
# ============================================================

rsi = last["rsi"]
macd_hist = last["macd_hist"]
volume_ratio = last["volume_ratio"]

if signal in ["강한 상승", "상승 추세"]:
    signal_cls = "green"
elif "약세" in signal:
    signal_cls = "red"
else:
    signal_cls = "yellow"

st.markdown(
    f"""
<div class="card">

<div style="display:flex;
justify-content:space-between;
align-items:center;">

<div>

<div class="metric-label">
TECHNICAL SIGNAL
</div>

<div class="metric-value {signal_cls}">
{signal}
</div>

</div>

<div class="signal">
RSI {rsi:.1f}
</div>

</div>

<div style="margin-top:14px"
class="reason">

현재 가격과 이동평균선, MACD, RSI, 거래량을 종합하면
<strong>{signal}</strong> 상태입니다.
단일 지표만으로 판단하기보다는 가격 위치와 거래량을 함께 확인하는 것이 중요합니다.

</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# PRICE / INDICATORS
# ============================================================

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "5일",
        fmt_pct(
            pct_change(
                data["close"],
                5
            )
        )
    )

with m2:
    st.metric(
        "20일",
        fmt_pct(
            pct_change(
                data["close"],
                20
            )
        )
    )

with m3:
    st.metric(
        "RSI",
        f"{rsi:.1f}"
    )

with m4:
    st.metric(
        "거래량",
        f"{volume_ratio:.1f}x"
    )


# ============================================================
# CHART
# ============================================================

st.plotly_chart(
    make_price_chart(
        data.tail(180)
    ),
    use_container_width=True,
    config={
        "displayModeBar": False
    }
)


# ============================================================
# SUPPORT / RESISTANCE
# ============================================================

st.markdown(
    '<div class="section-title">🎯 PRICE RADAR</div>',
    unsafe_allow_html=True
)

support = analysis["support"]
resistance = analysis["resistance"]

p1, p2, p3 = st.columns(3)

with p1:

    st.markdown(
        f"""
<div class="card">

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

with p2:

    st.markdown(
        f"""
<div class="card">

<div class="metric-label">
자동 지지
</div>

<div class="metric-value green">
{fmt_price(support)}
</div>

<div class="small">
지지까지
{((support / price) - 1) * 100:.1f}%
</div>

</div>
""",
        unsafe_allow_html=True
    )

with p3:

    st.markdown(
        f"""
<div class="card">

<div class="metric-label">
자동 저항
</div>

<div class="metric-value red">
{fmt_price(resistance)}
</div>

<div class="small">
저항까지
{((resistance / price) - 1) * 100:.1f}%
</div>

</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# VOLUME PROFILE
# ============================================================

st.markdown(
    '<div class="section-title">📦 VOLUME PROFILE</div>',
    unsafe_allow_html=True
)

vp = volume_profile(
    data
)

if not vp.empty:

    vp_display = vp.head(8).copy()

    fig_vp = go.Figure()

    fig_vp.add_trace(
        go.Bar(
            x=vp_display["volume"],
            y=vp_display["price"],
            orientation="h",
            name="거래량"
        )
    )

    fig_vp.update_layout(
        height=320,
        margin=dict(
            l=5,
            r=5,
            t=10,
            b=5
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#cbd5e1"
        ),
        showlegend=False
    )

    fig_vp.update_xaxes(
        showgrid=False
    )

    fig_vp.update_yaxes(
        gridcolor="rgba(255,255,255,.05)"
    )

    st.plotly_chart(
        fig_vp,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# ============================================================
# JUDGEMENT REASON
# ============================================================

st.markdown(
    '<div class="section-title">🧠 판단 근거</div>',
    unsafe_allow_html=True
)

reasons = []

if price > last["ma20"]:
    reasons.append(
        "현재 가격이 20일 이동평균선 위에 있어 단기 추세가 유지되고 있습니다."
    )
else:
    reasons.append(
        "현재 가격이 20일 이동평균선 아래에 있어 단기 추세 회복 여부 확인이 필요합니다."
    )

if last["ma20"] > last["ma60"]:
    reasons.append(
        "20일선이 60일선 위에 있어 중기 추세가 우호적입니다."
    )
else:
    reasons.append(
        "20일선이 60일선 아래에 있어 중기 추세는 아직 완전히 회복되지 않았습니다."
    )

if macd_hist > 0:
    reasons.append(
        "MACD 히스토그램이 양수로 모멘텀이 유지되고 있습니다."
    )
else:
    reasons.append(
        "MACD 히스토그램이 음수로 단기 모멘텀 약화 여부를 확인해야 합니다."
    )

if volume_ratio >= 1.3:
    reasons.append(
        "최근 거래량이 20일 평균보다 크게 증가해 시장 참여가 확대되고 있습니다."
    )
elif volume_ratio >= 1:
    reasons.append(
        "거래량은 평균 수준 이상으로 유지되고 있습니다."
    )
else:
    reasons.append(
        "거래량이 평균보다 낮아 상승 신뢰도 확인이 필요합니다."
    )

if rsi >= 75:
    reasons.append(
        "RSI가 높아 단기 추격매수 위험이 커진 상태입니다."
    )
elif rsi <= 35:
    reasons.append(
        "RSI가 낮아 단기 과매도 영역에 접근해 있습니다."
    )
else:
    reasons.append(
        "RSI는 극단적인 과열·과매도 구간에 있지 않습니다."
    )

st.markdown(
    f"""
<div class="card">

<div class="reason">

{" ".join(reasons)}

</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# TRADING SCENARIOS
# ============================================================

st.markdown(
    '<div class="section-title">🎯 대응 시나리오</div>',
    unsafe_allow_html=True
)

scenarios = scenario_text(
    data
)

for title, price_text, description in scenarios:

    st.markdown(
        f"""
<div class="scenario">

<div class="scenario-title">
{title}
</div>

<div class="scenario-price">
{price_text}
</div>

<div class="small">
{description}
</div>

</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# INDICATOR DETAIL
# ============================================================

st.markdown(
    '<div class="section-title">🔬 INDICATOR DETAIL</div>',
    unsafe_allow_html=True
)

i1, i2, i3, i4 = st.columns(4)

with i1:
    st.metric(
        "MA20",
        fmt_price(last["ma20"])
    )

with i2:
    st.metric(
        "MA60",
        fmt_price(last["ma60"])
    )

with i3:
    st.metric(
        "MACD",
        f"{last['macd']:.2f}"
    )

with i4:
    st.metric(
        "ATR",
        fmt_price(last["atr"])
    )


# ============================================================
# WATCHLIST-LIKE QUICK SELECT
# ============================================================

st.markdown(
    '<div class="section-title">⚡ QUICK ETF</div>',
    unsafe_allow_html=True
)

quick = [
    ("091160", "KODEX 반도체"),
    ("395160", "KODEX AI반도체핵심장비"),
    ("487240", "KODEX AI전력핵심설비"),
    ("445290", "KODEX 로봇액티브"),
    ("449450", "PLUS K방산"),
    ("466920", "SOL 조선TOP3플러스"),
]

qcols = st.columns(3)

for i, (qcode, qname) in enumerate(quick):

    with qcols[i % 3]:

        if st.button(
            qname,
            key=f"quick_{qcode}",
            use_container_width=True
        ):

            st.session_state.selected_etf = qcode

            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div style="
margin-top:35px;
padding:15px;
text-align:center;
color:#68778c;
font-size:11px;
">

ETF RADAR v11 · Market data may be delayed or unavailable.
Technical analysis is for informational purposes only.

</div>
""",
    unsafe_allow_html=True
)