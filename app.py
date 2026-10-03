import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import json
import os
import urllib.request
import xml.etree.ElementTree as ET

from datetime import datetime


# ============================================================
# ETF RADAR
# Premium Graphite / Mint / Coral / Amber UI
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# GLOBAL STYLE
# ============================================================

st.markdown(
    r"""
<style>

:root {
    --bg: #151719;
    --panel: #202326;
    --panel2: #282c30;
    --panel3: #191b1e;

    --line: #3a4046;
    --line2: #464d54;

    --text: #f5f3ee;
    --text2: #dddeda;
    --muted: #aeb3b8;

    --mint: #62e6c4;
    --coral: #ff756b;
    --amber: #f4c95d;
    --sky: #72b7ff;
}

/* ============================================================
   GLOBAL
   ============================================================ */

html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
.main,
.block-container {
    background: var(--bg) !important;
    color: var(--text) !important;
}

.block-container {
    max-width: 1180px;
    padding: 10px 12px 28px !important;
}

[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="column"] {
    background: transparent !important;
}

* {
    color: var(--text);
}

/* ============================================================
   TYPOGRAPHY
   ============================================================ */

h1,
h2,
h3,
h4 {
    color: var(--text) !important;
}

.app-title {
    font-size: 1.65rem;
    font-weight: 900;
    letter-spacing: -0.05em;
}

.app-sub {
    color: var(--muted) !important;
    font-size: 0.78rem;
    margin-top: 2px;
}

.section {
    font-size: 1.05rem;
    font-weight: 900;
    margin: 17px 0 8px;
}

.sub {
    color: var(--muted) !important;
    font-size: 0.78rem;
}

/* ============================================================
   COMMON PANELS
   ============================================================ */

.hero,
.panel,
.card,
.theme-card {
    background: var(--panel) !important;
    border: 1px solid var(--line);
    border-radius: 12px;
    color: var(--text);
    box-shadow: 0 5px 18px rgba(0, 0, 0, 0.12);
}

.hero {
    padding: 16px;
    margin: 10px 0;
}

/* ============================================================
   HERO
   ============================================================ */

.hero-name {
    font-size: 1.3rem;
    font-weight: 900;
}

.hero-code {
    font-size: 0.76rem;
    color: var(--muted) !important;
}

.quote {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-top: 13px;
}

.price {
    font-size: 2.1rem;
    font-weight: 900;
    letter-spacing: -0.05em;
}

.chg {
    font-size: 1rem;
    font-weight: 800;
}

.pos {
    color: var(--mint) !important;
}

.neg {
    color: var(--coral) !important;
}

.neu {
    color: var(--text) !important;
}

/* ============================================================
   EVIDENCE
   ============================================================ */

.evidence {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 7px;
    margin: 8px 0;
}

.e-box {
    background: var(--panel2);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 10px;
}

.e-label {
    font-size: 0.70rem;
    color: var(--muted) !important;
}

.e-value {
    font-size: 0.95rem;
    font-weight: 900;
    margin-top: 3px;
}

.e-sub {
    font-size: 0.70rem;
    color: var(--muted) !important;
    margin-top: 2px;
}

/* ============================================================
   JUDGMENT
   ============================================================ */

.judge {
    border-left: 4px solid var(--mint);
    padding: 13px;
    background: var(--panel2);
    border-radius: 9px;
}

.judge-title {
    font-size: 0.73rem;
    color: var(--muted) !important;
}

.judge-main {
    font-size: 1.20rem;
    font-weight: 900;
    margin-top: 3px;
}

.judge-text {
    font-size: 0.83rem;
    line-height: 1.55;
    color: #d8d9d6 !important;
    margin-top: 7px;
}

.action {
    border-left: 4px solid var(--amber);
    padding: 13px;
    background: var(--panel2);
    border-radius: 9px;
}

.action-title {
    font-size: 0.73rem;
    color: var(--amber) !important;
    font-weight: 800;
}

.action-text {
    font-size: 0.84rem;
    line-height: 1.55;
    font-weight: 700;
    margin-top: 5px;
}

/* ============================================================
   PRICE SCENARIO
   ============================================================ */

.scenarios {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 7px;
}

.scenario {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 10px;
}

.s-label {
    font-size: 0.68rem;
    color: var(--muted) !important;
}

.s-price {
    font-size: 1.05rem;
    font-weight: 900;
    margin-top: 4px;
}

.s-desc {
    font-size: 0.70rem;
    color: #c2c6c9 !important;
    line-height: 1.4;
    margin-top: 5px;
}

/* ============================================================
   FUTURE THEME
   ============================================================ */

.theme-card {
    padding: 13px;
    margin: 9px 0;
}

.stage {
    font-size: 0.72rem;
    color: var(--mint) !important;
    font-weight: 900;
}

.theme-title {
    font-size: 1.10rem;
    font-weight: 900;
    margin-top: 2px;
}

.theme-reason {
    font-size: 0.79rem;
    color: #c4c7c8 !important;
    line-height: 1.5;
    margin: 4px 0 10px;
}

.theme-etf {
    background: var(--panel2);
    border: 1px solid var(--line);
    border-radius: 9px;
    padding: 10px;
}

.theme-name {
    font-size: 0.92rem;
    font-weight: 900;
}

.theme-code {
    font-size: 0.70rem;
    color: var(--muted) !important;
}

.theme-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 5px;
    margin-top: 8px;
}

.theme-stat {
    background: var(--panel3);
    border-radius: 6px;
    padding: 7px;
}

.theme-stat-label {
    font-size: 0.65rem;
    color: var(--muted) !important;
}

.theme-stat-value {
    font-size: 0.84rem;
    font-weight: 900;
    margin-top: 2px;
}

/* ============================================================
   BUTTON
   ============================================================ */

.stButton > button {
    background: #2a2e32 !important;
    color: #ffffff !important;
    border: 1px solid #464d54 !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
}

.stButton > button:hover {
    background: #343a40 !important;
    border-color: var(--mint) !important;
    color: #ffffff !important;
}

.stButton > button[kind="primary"] {
    background: #2b7668 !important;
    border-color: var(--mint) !important;
}

/* ============================================================
   INPUT
   ============================================================ */

div[data-baseweb="input"],
div[data-baseweb="input"] > div {
    background: var(--panel) !important;
    color: #ffffff !important;
    border-color: var(--line2) !important;
}

div[data-baseweb="input"] input {
    background: transparent !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

div[data-baseweb="input"] input::placeholder {
    color: #8f969c !important;
}

/* ============================================================
   SELECTBOX
   ============================================================ */

div[data-baseweb="select"],
div[data-baseweb="select"] > div {
    background: var(--panel) !important;
    color: #ffffff !important;
    border-color: var(--line2) !important;
}

div[data-baseweb="select"] span {
    color: #ffffff !important;
}

ul[role="listbox"],
div[role="listbox"],
li[role="option"] {
    background: var(--panel) !important;
    color: #ffffff !important;
}

li[role="option"]:hover {
    background: #343a40 !important;
}

/* ============================================================
   RADIO
   ============================================================ */

[data-testid="stRadio"] label,
[data-testid="stRadio"] label p {
    color: #dddddd !important;
}

/* ============================================================
   CAPTION
   ============================================================ */

.stCaption,
[data-testid="stCaptionContainer"] p {
    color: var(--muted) !important;
}

/* ============================================================
   ALERT
   ============================================================ */

[data-testid="stAlert"] {
    background: #24282c !important;
    color: #dddddd !important;
    border: 1px solid #41484e !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div {
    color: #dddddd !important;
}

/* ============================================================
   DATAFRAME
   ============================================================ */

[data-testid="stDataFrame"] {
    background: var(--panel) !important;
    border: 1px solid var(--line) !important;
}

/* ============================================================
   DIVIDER
   ============================================================ */

hr {
    border-color: #34393e !important;
}

/* ============================================================
   PLOTLY
   ============================================================ */

.js-plotly-plot {
    background: var(--panel) !important;
    border-radius: 10px;
}

/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 700px) {

    .block-container {
        padding: 8px 9px 20px !important;
    }

    .price {
        font-size: 1.85rem;
    }

    .scenarios {
        grid-template-columns: repeat(2, 1fr);
    }

    .theme-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .theme-name {
        font-size: 0.90rem;
    }

    .theme-stat-value {
        font-size: 0.82rem;
    }

    .e-value {
        font-size: 0.82rem;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# FILE
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"
UNIVERSE_FILE = "etf_universe_cache.json"


# ============================================================
# ETF DATA
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
    "305720": "KODEX 2차전지산업",
    "449170": "TIGER 글로벌AI인프라액티브",
    "434060": "TIGER 글로벌AI&반도체액티브",
    "464240": "KODEX AI전력핵심설비",
    "487130": "KODEX AI전력인프라",
    "475050": "ACE 글로벌반도체TOP4 Plus",
    "469150": "ACE AI반도체포커스",
}

FALLBACK_ETFS = BASE_ETFS.copy()

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
            "반도체장비"
        ],
        "seeds": [
            "395160",
            "487240",
            "471990",
            "396500"
        ],
        "reason":
            "AI 연산 확대와 첨단 반도체 투자 증가의 직접적인 수혜 영역입니다.",
    },

    "데이터센터·AI 인프라": {
        "keywords": [
            "데이터센터",
            "AI인프라",
            "AI 인프라",
            "글로벌AI인프라"
        ],
        "seeds": [
            "449170",
            "434060",
            "381170"
        ],
        "reason":
            "AI 서비스 확산에 따라 서버·네트워크·데이터센터 투자를 추적합니다.",
    },

    "전력 인프라": {
        "keywords": [
            "전력",
            "전력인프라",
            "전력핵심설비",
            "전력설비"
        ],
        "seeds": [
            "464240",
            "487130"
        ],
        "reason":
            "데이터센터와 산업용 전력수요 증가에 따른 전력망 투자를 추적합니다.",
    },

    "원자력": {
        "keywords": [
            "원자력",
            "원전"
        ],
        "seeds": [],
        "reason":
            "전력수요와 에너지 믹스 변화에 따른 원전 관련 흐름을 추적합니다.",
    },

    "냉각·열관리": {
        "keywords": [
            "냉각",
            "열관리",
            "액침냉각"
        ],
        "seeds": [
            "434060",
            "449170"
        ],
        "reason":
            "AI 서버 고집적화에 따른 냉각·열관리 후방 수혜를 추적합니다.",
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
# JSON
# ============================================================

def read_json(path, default):

    try:

        if not os.path.exists(path):
            return default

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:
        return default


def write_json(path, data):

    try:

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

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
# ETF UNIVERSE
# ============================================================

def load_universe():

    universe = dict(
        BASE_ETFS
    )

    cached = read_json(
        UNIVERSE_FILE,
        {}
    )

    if isinstance(
        cached,
        dict
    ):

        for code, name in cached.items():

            if code and name:

                universe[
                    str(code).zfill(6)
                ] = str(name)

    return universe


def fetch_catalog():

    url = (
        "https://finance.naver.com/"
        "api/sise/etfItemList.nhn"
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
        timeout=7
    ) as response:

        raw = response.read()

    root = ET.fromstring(
        raw
    )

    result = {}

    for item in root.findall(
        ".//item"
    ):

        code = (
            item.attrib.get(
                "itemcode"
            )
            or item.attrib.get(
                "code"
            )
            or ""
        )

        name = (
            item.attrib.get(
                "itemname"
            )
            or item.attrib.get(
                "name"
            )
            or ""
        )

        if code and name:

            result[
                str(code).zfill(6)
            ] = name

    return result


def refresh_universe():

    try:

        external = fetch_catalog()

        if external:

            universe = dict(
                st.session_state.etf_universe
            )

            universe.update(
                external
            )

            st.session_state.etf_universe = (
                universe
            )

            write_json(
                UNIVERSE_FILE,
                universe
            )

            st.session_state.notice = (
                f"ETF 목록을 "
                f"{len(external):,}개 확인했습니다."
            )

            return

    except Exception:
        pass

    st.session_state.notice = (
        "외부 목록 연결이 지연되어 "
        "기존 ETF 목록을 사용합니다."
    )


# ============================================================
# SESSION STATE
# ============================================================

def init_state():

    if "watchlist" not in st.session_state:

        saved = read_json(
            WATCHLIST_FILE,
            DEFAULT_WATCHLIST.copy()
        )

        if isinstance(
            saved,
            list
        ):

            st.session_state.watchlist = [
                str(x).zfill(6)
                for x in saved
            ]

        else:

            st.session_state.watchlist = (
                DEFAULT_WATCHLIST.copy()
            )

    if "holdings" not in st.session_state:

        holdings = read_json(
            HOLDINGS_FILE,
            {}
        )

        st.session_state.holdings = (
            holdings
            if isinstance(
                holdings,
                dict
            )
            else {}
        )

    if "etf_universe" not in st.session_state:

        st.session_state.etf_universe = (
            load_universe()
        )

    if "price_cache" not in st.session_state:
        st.session_state.price_cache = {}

    if "theme_cache" not in st.session_state:
        st.session_state.theme_cache = {}

    if "selected_code" not in st.session_state:

        st.session_state.selected_code = (
            st.session_state.watchlist[0]
            if st.session_state.watchlist
            else list(BASE_ETFS)[0]
        )

    if "main_page" not in st.session_state:
        st.session_state.main_page = "📊 내 ETF"

    if "page_request" not in st.session_state:
        st.session_state.page_request = None

    if "notice" not in st.session_state:
        st.session_state.notice = None


# ============================================================
# HELPERS
# ============================================================

def name_of(code):

    code = str(code).zfill(6)

    return (
        st.session_state.etf_universe.get(
            code
        )
        or BASE_ETFS.get(
            code
        )
        or f"ETF {code}"
    )


def sf(value, default=0.0):

    try:

        if pd.isna(value):
            return default

        return float(value)

    except Exception:

        return default


def money(value):

    value = sf(value)

    if abs(value) >= 1000:
        return f"{value:,.0f}원"

    return f"{value:,.2f}원"


# ============================================================
# PRICE DATA
# ============================================================

def normalize(df):

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    if isinstance(
        df.columns,
        pd.MultiIndex
    ):

        df.columns = [
            c[0]
            if isinstance(c, tuple)
            else str(c)
            for c in df.columns
        ]

    rename = {}

    for col in df.columns:

        key = str(col).lower()

        mapping = {
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }

        if key in mapping:
            rename[col] = mapping[key]

    df = df.rename(
        columns=rename
    )

    required = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    if any(
        col not in df.columns
        for col in required
    ):

        return pd.DataFrame()

    for col in required:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(
        subset=["Close"]
    )

    try:

        if df.index.tz is not None:

            df.index = (
                df.index.tz_localize(None)
            )

    except Exception:
        pass

    return df[required]


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
            timeout=7
        ) as response:

            raw = response.read()

        root = ET.fromstring(
            raw
        )

        rows = []

        for item in root.findall(
            ".//item"
        ):

            values = item.attrib.get(
                "data",
                ""
            ).split("|")

            if len(values) < 6:
                continue

            rows.append(
                [
                    values[0],
                    float(values[1]),
                    float(values[2]),
                    float(values[3]),
                    float(values[4]),
                    float(values[5]),
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

        return normalize(df)

    except Exception:

        return pd.DataFrame()


def fetch_yahoo(code):

    try:

        ticker = (
            f"{str(code).zfill(6)}.KS"
        )

        df = yf.download(
            ticker,
            period="2y",
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False
        )

        return normalize(df)

    except Exception:

        return pd.DataFrame()


def load_price(
    code,
    force=False
):

    code = str(code).zfill(6)

    now = datetime.now()

    cached = (
        st.session_state.price_cache.get(
            code
        )
    )

    if cached and not force:

        age = (
            now - cached["time"]
        ).total_seconds()

        if age < 300:

            return cached["data"]

    df = fetch_naver(code)

    if df.empty:
        df = fetch_yahoo(code)

    if not df.empty:

        st.session_state.price_cache[
            code
        ] = {
            "time": now,
            "data": df
        }

    return df


# ============================================================
# INDICATORS
# ============================================================

def indicators(df):

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

    delta = d["Close"].diff()

    gain = (
        delta
        .where(delta > 0, 0)
        .rolling(14)
        .mean()
    )

    loss = (
        -delta
        .where(delta < 0, 0)
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

    d["LOW60"] = (
        d["Low"]
        .rolling(60)
        .min()
    )

    return d


# ============================================================
# JUDGMENT
# ============================================================

def get_judgment(d):

    row = d.iloc[-1]

    current = sf(
        row["Close"]
    )

    ma20 = sf(
        row["MA20"],
        current
    )

    ma60 = sf(
        row["MA60"],
        current
    )

    rsi = sf(
        row["RSI14"],
        50
    )

    volume_ratio = sf(
        row["VOL_RATIO"],
        1
    )

    ret20 = sf(
        row["RET20"],
        0
    )

    above20 = (
        current >= ma20
    )

    above60 = (
        current >= ma60
    )

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

    if volume_ratio >= 1.5:
        volume_state = "거래량 강한 확대"
    elif volume_ratio >= 1.1:
        volume_state = "거래량 증가"
    elif volume_ratio >= 0.8:
        volume_state = "평균 수준"
    else:
        volume_state = "거래량 감소"

    if (
        above20
        and above60
        and rsi >= 70
    ):

        title = "상승 추세 · 추격 주의"

        action = (
            "추세는 양호하지만 RSI가 높은 구간입니다. "
            "신규 매수는 현재가 추격보다 "
            "20일선 부근 눌림 확인을 우선합니다."
        )

    elif (
        above20
        and above60
    ):

        title = "상승 추세 유지"

        action = (
            "20일선과 60일선 위입니다. "
            "보유자는 20일선 이탈 여부를 확인하고, "
            "미보유자는 돌파 추격보다 눌림을 기다립니다."
        )

    elif above60:

        title = "단기 조정 · 중기 추세 확인"

        action = (
            "20일선 아래 조정이지만 60일선 위라면 "
            "중기 추세 훼손 여부를 추가 확인합니다."
        )

    elif rsi <= 40:

        title = "중기 약세 · 방어 우선"

        action = (
            "60일선 아래에서 RSI도 약합니다. "
            "신규 진입보다 지지 형성과 "
            "거래량 회복을 확인합니다."
        )

    else:

        title = "방향 확인 구간"

        action = (
            "추세가 명확하지 않습니다. "
            "20일선 회복 또는 최근 고점 돌파와 "
            "거래량 동반 여부를 확인합니다."
        )

    reasons = [
        (
            f"현재가 {money(current)} · "
            f"20일선 {money(ma20)} · "
            f"{ma_state}"
        ),
        (
            f"RSI14 {rsi:.1f} · "
            f"{rsi_state}"
        ),
        (
            f"거래량 {volume_ratio:.2f}배 · "
            f"{volume_state} · "
            f"20일 수익률 {ret20:+.2f}%"
        )
    ]

    return {
        "title": title,
        "action": action,
        "ma": ma_state,
        "rsi": rsi,
        "rsi_state": rsi_state,
        "volume": volume_ratio,
        "volume_state": volume_state,
        "reasons": reasons,
    }


# ============================================================
# PRICE LEVELS
# ============================================================

def get_levels(d):

    row = d.iloc[-1]

    current = sf(
        row["Close"]
    )

    ma20 = sf(
        row["MA20"],
        current
    )

    ma60 = sf(
        row["MA60"],
        current
    )

    high20 = sf(
        row["HIGH20"],
        current
    )

    low20 = sf(
        row["LOW20"],
        current
    )

    low60 = sf(
        row["LOW60"],
        current
    )

    return [
        (
            "1차 관심가격",
            ma20,
            "20일선 눌림 확인"
        ),
        (
            "핵심 지지",
            min(ma60, low20),
            "중기 추세 확인"
        ),
        (
            "돌파 기준",
            high20,
            "최근 20일 고점"
        ),
        (
            "위험 가격",
            min(ma60, low20, low60),
            "이탈 시 방어 검토"
        ),
    ]


# ============================================================
# NAVIGATION
# ============================================================

def navigate_to_etf(code):

    st.session_state.selected_code = (
        str(code).zfill(6)
    )

    # radio widget이 생성된 후
    # main_page를 직접 수정하지 않는다.
    st.session_state.page_request = (
        "📊 내 ETF"
    )

    st.rerun()


# ============================================================
# SEARCH
# ============================================================

def search_etfs(query):

    query = (
        query or ""
    ).strip().lower()

    if not query:
        return []

    result = []

    for code, name in (
        st.session_state.etf_universe.items()
    ):

        if (
            query in code.lower()
            or query in name.lower()
        ):

            result.append(
                (
                    code,
                    name
                )
            )

    return result[:40]


# ============================================================
# ETF FINDER
# ============================================================

def render_finder():

    st.markdown(
        '<div class="section">ETF 찾기</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(
        [5, 1]
    )

    with c1:

        query = st.text_input(
            "ETF 검색",
            placeholder="ETF명 또는 종목코드",
            label_visibility="collapsed",
            key="search_query"
        )

    with c2:

        if st.button(
            "목록 갱신",
            use_container_width=True,
            key="refresh_universe"
        ):

            refresh_universe()

            st.rerun()

    if st.session_state.notice:

        st.caption(
            st.session_state.notice
        )

        st.session_state.notice = None

    results = search_etfs(
        query
    )

    if not results:

        if query:
            st.caption(
                "검색 결과가 없습니다."
            )

        return

    labels = [
        f"{name} · {code}"
        for code, name in results
    ]

    selected_label = st.selectbox(
        "검색 결과",
        labels,
        label_visibility="collapsed",
        key="search_result"
    )

    index = labels.index(
        selected_label
    )

    selected_code, selected_name = (
        results[index]
    )

    a, b = st.columns(
        [5, 1]
    )

    with a:

        st.caption(
            f"선택: {selected_name} "
            f"({selected_code})"
        )

    with b:

        already = (
            selected_code
            in st.session_state.watchlist
        )

        if st.button(
            "등록됨"
            if already
            else "추가",
            disabled=already,
            use_container_width=True,
            key=f"add_{selected_code}"
        ):

            if (
                selected_code
                not in st.session_state.watchlist
            ):

                st.session_state.watchlist.append(
                    selected_code
                )

                write_json(
                    WATCHLIST_FILE,
                    st.session_state.watchlist
                )

            navigate_to_etf(
                selected_code
            )


# ============================================================
# WATCHLIST
# ============================================================

def render_watchlist():

    st.markdown(
        '<div class="section">관심종목</div>',
        unsafe_allow_html=True
    )

    watchlist = (
        st.session_state.watchlist
    )

    if not watchlist:

        st.caption(
            "관심종목이 없습니다."
        )

        return

    labels = [
        f"{name_of(code)} · {code}"
        for code in watchlist
    ]

    current = (
        st.session_state.selected_code
    )

    try:

        default_index = (
            watchlist.index(
                current
            )
        )

    except ValueError:

        default_index = 0

    selected_label = st.selectbox(
        "관심종목",
        labels,
        index=default_index,
        label_visibility="collapsed",
        key="watchlist_select"
    )

    selected_index = labels.index(
        selected_label
    )

    selected_code = (
        watchlist[selected_index]
    )

    st.session_state.selected_code = (
        selected_code
    )

    if st.button(
        "현재 ETF 관심종목에서 삭제",
        use_container_width=True,
        key="delete_watchlist"
    ):

        st.session_state.watchlist = [
            code
            for code in watchlist
            if code != selected_code
        ]

        write_json(
            WATCHLIST_FILE,
            st.session_state.watchlist
        )

        if st.session_state.watchlist:

            st.session_state.selected_code = (
                st.session_state.watchlist[0]
            )

        else:

            st.session_state.selected_code = (
                list(BASE_ETFS)[0]
            )

        st.rerun()


# ============================================================
# JUDGMENT UI
# ============================================================

def render_judgment(d):

    j = get_judgment(d)

    st.markdown(
        '<div class="section">현재판단 · 지금대응</div>',
        unsafe_allow_html=True
    )

    ma_class = (
        "pos"
        if "상회" in j["ma"]
        else "neg"
    )

    rsi_class = (
        "pos"
        if j["rsi"] >= 60
        else "neg"
        if j["rsi"] < 40
        else "neu"
    )

    volume_class = (
        "pos"
        if j["volume"] >= 1.1
        else "neg"
        if j["volume"] < 0.8
        else "neu"
    )

    st.markdown(
        f"""
        <div class="evidence">

            <div class="e-box">
                <div class="e-label">
                    20일선
                </div>

                <div class="e-value {ma_class}">
                    {j["ma"]}
                </div>

                <div class="e-sub">
                    단기 추세
                </div>
            </div>

            <div class="e-box">
                <div class="e-label">
                    RSI14
                </div>

                <div class="e-value {rsi_class}">
                    {j["rsi"]:.1f}
                </div>

                <div class="e-sub">
                    {j["rsi_state"]}
                </div>
            </div>

            <div class="e-box">
                <div class="e-label">
                    거래량
                </div>

                <div class="e-value {volume_class}">
                    {j["volume"]:.2f}배
                </div>

                <div class="e-sub">
                    {j["volume_state"]}
                </div>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            f"""
            <div class="judge">

                <div class="judge-title">
                    현재 시장 판단
                </div>

                <div class="judge-main">
                    {j["title"]}
                </div>

                <div class="judge-text">
                    {"<br>".join(j["reasons"])}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="action">

                <div class="action-title">
                    지금 대응
                </div>

                <div class="action-text">
                    {j["action"]}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# CHART
# ============================================================

def render_chart(d):

    end_date = d.index.max()

    start_date = (
        end_date
        - pd.DateOffset(
            months=6
        )
    )

    chart_df = d[
        d.index >= start_date
    ].copy()

    if chart_df.empty:
        return

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.025,
        row_heights=[
            0.76,
            0.24
        ]
    )

    # 가격
    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            increasing_line_color="#62e6c4",
            increasing_fillcolor="#62e6c4",
            decreasing_line_color="#ff756b",
            decreasing_fillcolor="#ff756b",
            name="가격"
        ),
        row=1,
        col=1
    )

    # 20일선
    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA20"],
            mode="lines",
            line=dict(
                color="#72b7ff",
                width=1.5
            ),
            name="20일선"
        ),
        row=1,
        col=1
    )

    # 60일선
    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA60"],
            mode="lines",
            line=dict(
                color="#f4c95d",
                width=1.4
            ),
            name="60일선"
        ),
        row=1,
        col=1
    )

    volume_colors = np.where(
        chart_df["Close"]
        >= chart_df["Open"],
        "#62e6c4",
        "#ff756b"
    )

    # 거래량
    fig.add_trace(
        go.Bar(
            x=chart_df.index,
            y=chart_df["Volume"],
            marker_color=volume_colors,
            opacity=0.45,
            name="거래량",
            showlegend=False
        ),
        row=2,
        col=1
    )

    # ========================================================
    # 차트 조작 차단
    # ========================================================

    fig.update_xaxes(
        fixedrange=True,
        showgrid=False,
        rangeslider_visible=False
    )

    fig.update_yaxes(
        fixedrange=True,
        showgrid=True,
        gridcolor="#30353a",
        zeroline=False
    )

    fig.update_yaxes(
        fixedrange=True,
        showgrid=False,
        showticklabels=False,
        row=2,
        col=1
    )

    fig.update_layout(
        height=410,
        margin=dict(
            l=5,
            r=5,
            t=18,
            b=5
        ),
        paper_bgcolor="#202326",
        plot_bgcolor="#202326",
        font=dict(
            color="#eeeeee"
        ),
        dragmode=False,
        hovermode="x unified",
        showlegend=True,
        legend=dict(
            orientation="h",
            y=1.02,
            x=1,
            xanchor="right",
            font=dict(
                size=10
            )
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "doubleClick": False,
            "responsive": True
        },
        key="six_month_fixed_chart"
    )

    st.caption(
        "최근 6개월 고정 · 확대/축소/좌우이동 없음"
    )


# ============================================================
# FUTURE THEME
# ============================================================

def get_theme_rows(theme):

    cached = (
        st.session_state.theme_cache.get(
            theme
        )
    )

    now = datetime.now()

    if cached:

        age = (
            now - cached["time"]
        ).total_seconds()

        if age < 300:
            return cached["rows"]

    info = THEMES[theme]

    candidates = []
    seen = set()

    for code in info["seeds"]:

        code = str(code).zfill(6)

        if code not in seen:

            candidates.append(
                code
            )

            seen.add(code)

    for code, name in (
        st.session_state.etf_universe.items()
    ):

        if code in seen:
            continue

        text = name.lower()

        if any(
            keyword.lower()
            in text
            for keyword in info["keywords"]
        ):

            candidates.append(
                code
            )

            seen.add(code)

    rows = []

    for code in candidates[:4]:

        try:

            raw = load_price(
                code
            )

            d = indicators(
                raw
            )

            if d.empty:
                continue

            row = d.iloc[-1]

            price = sf(
                row["Close"]
            )

            rows.append(
                {
                    "code": code,
                    "name": name_of(code),
                    "price": price,
                    "rsi": sf(
                        row["RSI14"],
                        50
                    ),
                    "volume": sf(
                        row["VOL_RATIO"],
                        1
                    ),
                    "ret20": sf(
                        row["RET20"],
                        0
                    ),
                    "trend":
                        "상승"
                        if price >= sf(
                            row["MA20"],
                            price
                        )
                        else "조정"
                }
            )

        except Exception:
            continue

    st.session_state.theme_cache[
        theme
    ] = {
        "time": now,
        "rows": rows
    }

    return rows


def render_theme(
    theme,
    stage,
    theme_index
):

    info = THEMES[theme]

    st.markdown(
        f"""
        <div class="theme-card">

            <div class="stage">
                {stage}
            </div>

            <div class="theme-title">
                {theme}
            </div>

            <div class="theme-reason">
                {info["reason"]}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    rows = get_theme_rows(
        theme
    )

    if not rows:

        st.caption(
            "현재 표시 가능한 ETF 데이터가 없습니다."
        )

        return

    cols = st.columns(
        len(rows)
    )

    for index, item in enumerate(rows):

        with cols[index]:

            ret_class = (
                "pos"
                if item["ret20"] >= 0
                else "neg"
            )

            trend_class = (
                "pos"
                if item["trend"] == "상승"
                else "neg"
            )

            st.markdown(
                f"""
                <div class="theme-etf">

                    <div class="theme-name">
                        {item["name"]}
                    </div>

                    <div class="theme-code">
                        {item["code"]}
                    </div>

                    <div class="theme-grid">

                        <div class="theme-stat">
                            <div class="theme-stat-label">
                                현재가
                            </div>
                            <div class="theme-stat-value">
                                {money(item["price"])}
                            </div>
                        </div>

                        <div class="theme-stat">
                            <div class="theme-stat-label">
                                RSI14
                            </div>
                            <div class="theme-stat-value">
                                {item["rsi"]:.1f}
                            </div>
                        </div>

                        <div class="theme-stat">
                            <div class="theme-stat-label">
                                거래량
                            </div>
                            <div class="theme-stat-value">
                                {item["volume"]:.2f}배
                            </div>
                        </div>

                        <div class="theme-stat">
                            <div class="theme-stat-label">
                                20일
                            </div>
                            <div class="theme-stat-value {ret_class}">
                                {item["ret20"]:+.2f}%
                            </div>
                        </div>

                    </div>

                    <div style="
                        font-size:0.74rem;
                        color:#b8bec2;
                        margin-top:7px;
                    ">
                        추세:
                        <span class="{trend_class}">
                            {item["trend"]}
                        </span>
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                "ETF 분석",
                use_container_width=True,
                key=(
                    f"theme_"
                    f"{theme_index}_"
                    f"{index}_"
                    f"{item['code']}"
                )
            ):

                navigate_to_etf(
                    item["code"]
                )


# ============================================================
# MY ETF PAGE
# ============================================================

def render_my_etf():

    render_finder()

    render_watchlist()

    code = (
        st.session_state.selected_code
    )

    raw = load_price(
        code
    )

    d = indicators(
        raw
    )

    if d.empty:

        st.warning(
            "가격 데이터를 불러오지 못했습니다. "
            "잠시 후 다시 시도해 주세요."
        )

        return

    current = sf(
        d["Close"].iloc[-1]
    )

    previous = sf(
        d["Close"].iloc[-2],
        current
    )

    change = (
        current - previous
    )

    change_pct = (
        change
        / previous
        * 100
        if previous
        else 0
    )

    change_class = (
        "pos"
        if change > 0
        else "neg"
        if change < 0
        else "neu"
    )

    date_text = (
        d.index[-1].strftime(
            "%Y-%m-%d"
        )
    )

    # ========================================================
    # HERO
    # ========================================================

    st.markdown(
        f"""
        <div class="hero">

            <div class="hero-name">
                {name_of(code)}
            </div>

            <div class="hero-code">
                {code} · 기준일 {date_text}
            </div>

            <div class="quote">

                <div class="price">
                    {money(current)}
                </div>

                <div class="chg {change_class}">
                    {money(change)}
                    ({change_pct:+.2f}%)
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # HOLDING
    # ========================================================

    st.markdown(
        '<div class="section">보유 상태</div>',
        unsafe_allow_html=True
    )

    existing = (
        st.session_state.holdings.get(
            code
        )
    )

    holding_status = st.radio(
        "보유 여부",
        [
            "미보유",
            "보유중"
        ],
        index=1 if existing else 0,
        horizontal=True,
        label_visibility="collapsed",
        key=f"holding_{code}"
    )

    if holding_status == "보유중":

        c1, c2 = st.columns(2)

        with c1:

            avg_price = st.number_input(
                "평균매수가",
                min_value=0.0,
                value=float(
                    existing.get(
                        "avg_price",
                        0
                    )
                    if existing
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
                    existing.get(
                        "quantity",
                        0
                    )
                    if existing
                    else 0
                ),
                step=1.0,
                key=f"qty_{code}"
            )

        if st.button(
            "보유정보 저장",
            use_container_width=True,
            key=f"save_{code}"
        ):

            st.session_state.holdings[
                code
            ] = {
                "avg_price": avg_price,
                "quantity": quantity
            }

            write_json(
                HOLDINGS_FILE,
                st.session_state.holdings
            )

            st.rerun()

    elif code in st.session_state.holdings:

        if st.button(
            "보유정보 삭제",
            use_container_width=True,
            key=f"delete_hold_{code}"
        ):

            del st.session_state.holdings[
                code
            ]

            write_json(
                HOLDINGS_FILE,
                st.session_state.holdings
            )

            st.rerun()

    # ========================================================
    # JUDGMENT
    # ========================================================

    render_judgment(
        d
    )

    # ========================================================
    # PRICE SCENARIO
    # ========================================================

    st.markdown(
        '<div class="section">핵심가격 · 대응 시나리오</div>',
        unsafe_allow_html=True
    )

    cards = get_levels(
        d
    )

    cards_html = (
        '<div class="scenarios">'
    )

    for label, price, desc in cards:

        cards_html += f"""
        <div class="scenario">

            <div class="s-label">
                {label}
            </div>

            <div class="s-price">
                {money(price)}
            </div>

            <div class="s-desc">
                {desc}
            </div>

        </div>
        """

    cards_html += (
        '</div>'
    )

    st.markdown(
        cards_html,
        unsafe_allow_html=True
    )

    # ========================================================
    # CHART
    # ========================================================

    st.markdown(
        '<div class="section">가격 흐름</div>',
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
        key="future_refresh"
    ):

        st.session_state.price_cache = {}
        st.session_state.theme_cache = {}

        refresh_universe()

        st.rerun()

    for index, (
        theme,
        stage
    ) in enumerate(
        FUTURE_CHAIN
    ):

        render_theme(
            theme,
            stage,
            index
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    summary = []

    for theme, stage in FUTURE_CHAIN:

        rows = get_theme_rows(
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

        avg_volume = np.mean(
            [
                x["volume"]
                for x in rows
            ]
        )

        summary.append(
            {
                "테마": theme,
                "단계": stage,
                "평균 20일수익률":
                    f"{avg_ret:+.2f}%",
                "평균 RSI":
                    f"{avg_rsi:.1f}",
                "평균 거래량":
                    f"{avg_volume:.2f}배"
            }
        )

    if summary:

        st.markdown(
            '<div class="section">테마 요약</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            pd.DataFrame(summary),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# START
# ============================================================

init_state()


# ============================================================
# SAFE PAGE REQUEST
# ============================================================

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
    <div class="app-title">
        ETF RADAR
    </div>

    <div class="app-sub">
        ETF 추세 · 모멘텀 · 거래량 · 핵심가격 · 대응 시나리오
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# NAVIGATION
# ============================================================

page = st.radio(
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

if page == "📊 내 ETF":

    render_my_etf()

else:

    render_future_theme()