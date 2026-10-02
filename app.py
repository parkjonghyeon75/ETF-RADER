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


# ============================================================
# ETF RADAR v10
# Premium Mobile Financial Dashboard
# ============================================================

st.set_page_config(
    page_title="ETF Radar",
    page_icon="📈",
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
    --line: #e5e7eb;
    --blue: #2563eb;
    --green: #16a34a;
    --red: #dc2626;
    --orange: #f59e0b;
    --purple: #7c3aed;
}

.stApp {
    background:
        linear-gradient(
            180deg,
            #f8fafc 0%,
            #f3f6fb 45%,
            #eef2f7 100%
        );
    color: var(--text);
}

.block-container {
    max-width: 720px;
    padding-top: 0.65rem;
    padding-bottom: 3rem;
    padding-left: 0.65rem;
    padding-right: 0.65rem;
}

/* ---------------------------
   Hide Streamlit branding
--------------------------- */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}


/* ---------------------------
   Typography
--------------------------- */

html,
body,
[class*="css"] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        Helvetica,
        Arial,
        sans-serif;
}

h1 {
    font-size: 1.55rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.04em;
    color: #0f172a !important;
}

h2 {
    font-size: 1.25rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.035em;
}

h3 {
    font-size: 1.05rem !important;
    font-weight: 800 !important;
}


/* ---------------------------
   Header
--------------------------- */

.app-header {
    padding: 0.45rem 0.15rem 0.65rem 0.15rem;
}

.app-brand {
    font-size: 0.78rem;
    font-weight: 800;
    color: #2563eb;
    letter-spacing: 0.11em;
}

.app-title {
    font-size: 1.65rem;
    font-weight: 850;
    color: #0f172a;
    letter-spacing: -0.05em;
    margin-top: 0.05rem;
}

.app-subtitle {
    color: #64748b;
    font-size: 0.75rem;
    margin-top: 0.05rem;
}


/* ---------------------------
   Top Navigation
--------------------------- */

div[data-baseweb="tab-list"] {
    gap: 4px;
    background: #e9eef5;
    padding: 4px;
    border-radius: 14px;
}

button[data-baseweb="tab"] {
    border-radius: 10px !important;
    font-size: 0.79rem !important;
    font-weight: 750 !important;
    color: #64748b !important;
    padding: 0.48rem 0.4rem !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: #ffffff !important;
    color: #111827 !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
}


/* ---------------------------
   Cards
--------------------------- */

.card {
    background: rgba(255,255,255,0.96);
    border: 1px solid rgba(226,232,240,0.9);
    border-radius: 18px;
    padding: 16px;
    margin: 8px 0;
    box-shadow:
        0 4px 18px rgba(15,23,42,0.045);
}

.card-tight {
    padding: 12px 14px;
}

.card-title {
    color: #64748b;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.card-value {
    color: #0f172a;
    font-size: 1.45rem;
    font-weight: 850;
    letter-spacing: -0.04em;
    margin-top: 2px;
}

.card-sub {
    color: #64748b;
    font-size: 0.74rem;
    margin-top: 3px;
}


/* ---------------------------
   Instrument Hero
--------------------------- */

.hero {
    background:
        radial-gradient(
            circle at 100% 0%,
            rgba(37,99,235,0.13),
            transparent 35%
        ),
        #ffffff;

    border: 1px solid #e2e8f0;
    border-radius: 22px;
    padding: 17px;
    margin: 10px 0;
    box-shadow:
        0 8px 26px rgba(15,23,42,0.06);
}

.hero-name {
    font-size: 0.92rem;
    font-weight: 800;
    color: #111827;
}

.hero-code {
    font-size: 0.69rem;
    color: #94a3b8;
    margin-top: 2px;
}

.hero-price {
    font-size: 2.35rem;
    line-height: 1.0;
    font-weight: 900;
    letter-spacing: -0.06em;
    color: #0f172a;
    margin-top: 12px;
}

.hero-change {
    font-size: 0.9rem;
    font-weight: 850;
    margin-top: 5px;
}


/* ---------------------------
   Score Ring
--------------------------- */

.score-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 15px;
    min-height: 168px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow:
        0 5px 20px rgba(15,23,42,0.045);
}

.score-ring {
    width: 112px;
    height: 112px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        conic-gradient(
            #2563eb calc(var(--score) * 1%),
            #e8edf5 0
        );
    position: relative;
}

.score-ring::before {
    content: "";
    position: absolute;
    inset: 10px;
    border-radius: 50%;
    background: #ffffff;
}

.score-number {
    position: relative;
    z-index: 2;
    text-align: center;
}

.score-number-main {
    font-size: 1.75rem;
    font-weight: 900;
    line-height: 1;
    color: #0f172a;
}

.score-number-sub {
    font-size: 0.62rem;
    color: #94a3b8;
    margin-top: 3px;
}

.score-label {
    margin-top: 8px;
    font-size: 0.78rem;
    font-weight: 850;
    color: #2563eb;
}


/* ---------------------------
   Signal Grid
--------------------------- */

.signal-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-top: 8px;
}

.signal {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 13px;
    padding: 10px;
}

.signal-title {
    font-size: 0.67rem;
    color: #64748b;
    font-weight: 750;
}

.signal-value {
    font-size: 0.9rem;
    font-weight: 850;
    margin-top: 2px;
}

.signal-good {
    color: #15803d;
}

.signal-warn {
    color: #d97706;
}

.signal-bad {
    color: #dc2626;
}

.signal-neutral {
    color: #475569;
}


/* ---------------------------
   Action Cards
--------------------------- */

.action-card {
    border-radius: 17px;
    padding: 14px;
    margin: 7px 0;
    border: 1px solid;
}

.action-buy {
    background: #f0fdf4;
    border-color: #bbf7d0;
}

.action-sell {
    background: #fff7f7;
    border-color: #fecaca;
}

.action-wait {
    background: #fffbeb;
    border-color: #fde68a;
}

.action-break {
    background: #eff6ff;
    border-color: #bfdbfe;
}

.action-label {
    font-size: 0.68rem;
    font-weight: 850;
    letter-spacing: 0.08em;
}

.action-price {
    font-size: 1.25rem;
    font-weight: 900;
    margin-top: 4px;
    color: #111827;
}

.action-desc {
    font-size: 0.74rem;
    color: #64748b;
    margin-top: 3px;
}


/* ---------------------------
   Price Map
--------------------------- */

.price-map {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 15px;
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
    font-size: 0.73rem;
    font-weight: 750;
    color: #64748b;
}

.price-number {
    font-size: 0.9rem;
    font-weight: 900;
}


/* ---------------------------
   Pattern
--------------------------- */

.pattern-box {
    background:
        linear-gradient(
            135deg,
            #eff6ff,
            #f8fafc
        );
    border: 1px solid #dbeafe;
    border-radius: 17px;
    padding: 14px;
}

.pattern-title {
    color: #1d4ed8;
    font-size: 0.68rem;
    font-weight: 900;
    letter-spacing: 0.08em;
}

.pattern-main {
    color: #0f172a;
    font-size: 1rem;
    font-weight: 850;
    margin-top: 4px;
    line-height: 1.4;
}


/* ---------------------------
   Section Header
--------------------------- */

.section-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 18px 2px 8px;
}

.section-title {
    font-size: 0.95rem;
    font-weight: 900;
    color: #0f172a;
    letter-spacing: -0.025em;
}

.section-caption {
    color: #94a3b8;
    font-size: 0.67rem;
}


/* ---------------------------
   Theme Cards
--------------------------- */

.theme-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 14px;
    margin: 8px 0;
    box-shadow: 0 4px 14px rgba(15,23,42,0.035);
}

.theme-rank {
    font-size: 0.68rem;
    color: #2563eb;
    font-weight: 900;
}

.theme-name {
    font-size: 0.93rem;
    font-weight: 850;
    color: #0f172a;
    margin-top: 2px;
}

.theme-score {
    font-size: 1.25rem;
    font-weight: 900;
    color: #2563eb;
}

.theme-change {
    font-size: 0.73rem;
    font-weight: 800;
}

.gem {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 13px;
    padding: 10px;
    margin-top: 8px;
}

.gem-name {
    font-size: 0.78rem;
    font-weight: 850;
    color: #111827;
}

.gem-meta {
    font-size: 0.68rem;
    color: #64748b;
    margin-top: 3px;
}


/* ---------------------------
   Expander
--------------------------- */

div[data-testid="stExpander"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 15px !important;
    background: #ffffff !important;
    overflow: hidden;
}


/* ---------------------------
   Inputs
--------------------------- */

div[data-baseweb="input"] {
    border-radius: 12px !important;
}

div[data-baseweb="select"] > div {
    border-radius: 12px !important;
}


/* ---------------------------
   Buttons
--------------------------- */

.stButton > button {
    border-radius: 12px !important;
    font-weight: 800 !important;
    min-height: 42px !important;
}

button[kind="primary"] {
    background: #2563eb !important;
}


/* ---------------------------
   Dataframe
--------------------------- */

div[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}


/* ---------------------------
   Mobile
--------------------------- */

@media (max-width: 600px) {

    .block-container {
        padding-left: 0.48rem;
        padding-right: 0.48rem;
        padding-top: 0.4rem;
    }

    .app-title {
        font-size: 1.48rem;
    }

    .hero-price {
        font-size: 2.15rem;
    }

    .score-ring {
        width: 102px;
        height: 102px;
    }

    .signal-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .stButton > button {
        min-height: 44px !important;
    }

    p,
    .stMarkdown {
        font-size: 0.86rem;
    }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA
# ============================================================

WATCHLIST_FILE = "watchlist.json"
THEME_FILE = "theme_info.json"


DC_PENSION_POOLS = {

    "🇺🇸 미국 S&P500 / 대형가치": {
        "360750": "TIGER 미국S&P500",
        "379800": "KODEX 미국S&P500TR",
        "448290": "SOL 미국S&P500"
    },

    "🇺🇸 미국 나스닥100 / 빅테크": {
        "133690": "TIGER 미국나스닥100",
        "379810": "KODEX 미국나스닥100TR",
        "487240": "KODEX 미국AI테크TOP10",
        "452330": "TIGER 미국테크TOP10"
    },

    "🤖 AI 반도체 / HBM / 소부장": {
        "395160": "KODEX AI반도체TOP2플러스",
        "462100": "TIGER AI반도체핵심공정",
        "441680": "SOL 미국AI반도체",
        "486410": "TIGER 미국반도체TOP10"
    },

    "⚡ AI 전력인프라 / 원자력": {
        "471990": "KODEX AI전력핵심설비",
        "445380": "SOL 원자력TOP3플러스",
        "465560": "TIGER 글로벌원자력"
    },

    "🔋 2차전지 / 배터리 소재": {
        "305540": "KODEX 2차전지산업",
        "364980": "TIGER 2차전지소부장",
        "438320": "KODEX 2차전지핵심소재"
    },

    "🚀 우주항공 / 로봇 / 차세대": {
        "465610": "KODEX 로봇산업",
        "476250": "TIGER 우주항공&로봇",
        "456720": "SOL 다이와일본레버리지"
    },

    "💊 바이오 / 헬스케어": {
        "329200": "TIGER 헬스케어",
        "266420": "KODEX 바이오",
        "462610": "ARIRANG 3대주주바이오"
    },

    "💰 미국 고배당 / 월배당": {
        "458730": "TIGER 미국배당다우존스",
        "441680": "SOL 미국배당 다우존스",
        "476480": "KODEX 미국배당커버드콜",
        "451780": "TIGER 미국배당+7%프리미엄"
    },

    "🛡️ 안전자산 / 국내단기채 / 미국국채": {
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
        "theme": "국내 AI 반도체 / HBM",
        "cycle": "성장기",
        "desc": "SK하이닉스, 삼성전자 중심의 HBM 및 반도체 공정 핵심 기업 추종.",
        "long_view": "메모리 반도체 업황 사이클 및 AI 서버 CapEx 지속 여부가 핵심입니다."
    },

    "487240": {
        "theme": "미국 AI 빅테크 TOP10",
        "cycle": "고성장기",
        "desc": "AI 관련 메가캡 기업 중심 포트폴리오.",
        "long_view": "AI 서비스 수익화와 실적 증가 여부가 핵심입니다."
    },

    "471990": {
        "theme": "AI 전력망 / 변압기 / 원자력",
        "cycle": "확장기",
        "desc": "AI 데이터센터 전력 인프라 관련 기업군.",
        "long_view": "전력망 투자와 데이터센터 증설 흐름이 주요 변수입니다."
    },

    "133690": {
        "theme": "미국 대표 기술주",
        "cycle": "장기 성장",
        "desc": "미국 나스닥100 추종 ETF.",
        "long_view": "미국 대형 기술주의 장기 성장 흐름을 반영합니다."
    },

    "360750": {
        "theme": "미국 대표 대형주",
        "cycle": "장기 성장",
        "desc": "미국 S&P500 추종 ETF.",
        "long_view": "미국 대형주 전반의 장기 흐름을 반영합니다."
    },

    "458730": {
        "theme": "미국 배당 성장",
        "cycle": "안정적 성장",
        "desc": "미국 우량 배당주 중심 ETF.",
        "long_view": "배당과 자본성장을 함께 추구하는 장기형 자산입니다."
    }
}


# ============================================================
# FILE FUNCTIONS
# ============================================================

def load_json_file(file_path, default_data):

    if os.path.exists(file_path):

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, (dict, list)) and data:
                return data

        except Exception:
            pass

    return default_data.copy()


def save_json_file(file_path, data):

    try:

        with open(file_path, "w", encoding="utf-8") as f:
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


# ============================================================
# NAVER SEARCH
# ============================================================

def search_stock_code_by_keyword(keyword):

    try:

        encoded = urllib.parse.quote(keyword)

        url = (
            "https://ac.stock.naver.com/ac?"
            f"q={encoded}&target=etf"
        )

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(req, timeout=5) as response:

            res_json = json.loads(
                response.read().decode("utf-8")
            )

            items = res_json.get("items", [])

            if items:
                return items[0][0], items[0][1]

    except Exception:
        pass

    return None, None


def get_stock_name(code):

    try:

        url = (
            f"https://m.stock.naver.com/"
            f"api/stock/{code}/basic"
        )

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(req, timeout=8) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

            return data.get(
                "stockName",
                f"ETF {code}"
            )

    except Exception:

        return f"ETF {code}"


# ============================================================
# DATA FETCH
# ============================================================

def fetch_from_naver(code, count=500):

    try:

        url = (
            "https://fchart.stock.naver.com/sise.nhn?"
            f"symbol={urllib.parse.quote(code)}"
            f"&timeframe=day"
            f"&count={count}"
            f"&requestType=0"
        )

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(
            req,
            timeout=10
        ) as response:

            xml_data = response.read().decode(
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

                rows.append({

                    "Date": pd.to_datetime(parts[0]),

                    "Open": float(parts[1]),

                    "High": float(parts[2]),

                    "Low": float(parts[3]),

                    "Close": float(parts[4]),

                    "Volume": float(parts[5])
                })

        if not rows:
            return None

        return (
            pd.DataFrame(rows)
            .set_index("Date")
            .sort_index()
        )

    except Exception:

        return None


@st.cache_data(
    ttl=300,
    show_spinner=False
)
def load_etf_data(
    ticker_code,
    period="1y"
):

    clean_code = "".join(
        filter(
            str.isalnum,
            str(ticker_code)
        )
    )

    if not clean_code:
        clean_code = str(ticker_code).strip()

    df = fetch_from_naver(
        clean_code,
        count=500
    )

    if df is None or df.empty:

        for suffix in [".KS", ".KQ"]:

            try:

                data = yf.download(
                    f"{clean_code}{suffix}",
                    period="2y",
                    progress=False,
                    auto_adjust=False,
                    threads=False
                )

                if (
                    not data.empty
                    and len(data) >= 20
                ):

                    if isinstance(
                        data.columns,
                        pd.MultiIndex
                    ):

                        data.columns = (
                            data.columns
                            .get_level_values(0)
                        )

                    data = data[
                        [
                            "Open",
                            "High",
                            "Low",
                            "Close",
                            "Volume"
                        ]
                    ].copy()

                    data.index = pd.to_datetime(
                        data.index
                    )

                    df = data
                    break

            except Exception:
                pass

    if (
        df is None
        or df.empty
        or len(df) < 20
    ):

        return None, clean_code

    if period == "6m":
        df = df.iloc[-130:]

    elif period == "1y":
        df = df.iloc[-260:]

    else:
        df = df.iloc[-500:]

    return df.copy(), clean_code


# ============================================================
# TECHNICAL INDICATORS
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
        delta
        .clip(lower=0)
        .rolling(14)
        .mean()
    )

    loss = (
        -delta
        .clip(upper=0)
        .rolling(14)
        .mean()
    )

    rs = gain / loss.replace(
        0,
        np.nan
    )

    df["RSI"] = (
        100
        - (
            100
            / (1 + rs)
        )
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
        df["MACD"]
        - df["MACD_Signal"]
    )

    df["BB_Mid"] = df["MA20"]

    std20 = (
        df["Close"]
        .rolling(20)
        .std()
    )

    df["BB_Upper"] = (
        df["BB_Mid"]
        + 2 * std20
    )

    df["BB_Lower"] = (
        df["BB_Mid"]
        - 2 * std20
    )

    df["Vol_MA20"] = (
        df["Volume"]
        .rolling(20)
        .mean()
    )

    df["Vol_Ratio"] = (
        df["Volume"]
        / df["Vol_MA20"].replace(
            0,
            np.nan
        )
    )

    return df


# ============================================================
# SUPPORT / RESISTANCE
# ============================================================

def get_support_resistance(df):

    current = float(
        df["Close"].iloc[-1]
    )

    recent20 = df.iloc[-20:]

    supports = []
    resistances = []

    for col in [
        "MA20",
        "MA60",
        "MA120"
    ]:

        if (
            col in df.columns
            and pd.notna(df[col].iloc[-1])
        ):

            p = float(
                df[col].iloc[-1]
            )

            if p < current:

                supports.append({
                    "price": p,
                    "strength": 2
                })

            elif p > current:

                resistances.append({
                    "price": p,
                    "strength": 2
                })

    p_low = float(
        recent20["Low"].min()
    )

    if p_low < current:

        supports.append({
            "price": p_low,
            "strength": 3
        })

    p_high = float(
        recent20["High"].max()
    )

    if p_high > current:

        resistances.append({
            "price": p_high,
            "strength": 3
        })

    def dedup(levels):

        out = []

        for item in sorted(
            levels,
            key=lambda x: x["price"]
        ):

            if (
                not out
                or
                abs(
                    item["price"]
                    - out[-1]["price"]
                )
                / out[-1]["price"]
                > 0.012
            ):

                out.append(item.copy())

            else:

                if (
                    item["strength"]
                    > out[-1]["strength"]
                ):

                    out[-1] = item.copy()

        return out

    supports = sorted(
        dedup(supports),
        key=lambda x: x["price"],
        reverse=True
    )[:3]

    resistances = sorted(
        dedup(resistances),
        key=lambda x: x["price"]
    )[:3]

    return supports, resistances


# ============================================================
# VOLUME PROFILE
# ============================================================

def volume_profile(
    df,
    bins=20
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
                "volume"
            ]
        )

    edges = np.linspace(
        low,
        high,
        bins + 1
    )

    volumes = np.zeros(bins)

    typical = (
        data["High"]
        + data["Low"]
        + data["Close"]
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
            )
            - 1
        )

        idx = min(
            max(idx, 0),
            bins - 1
        )

        volumes[idx] += float(vol)

    prices = (
        edges[:-1]
        + edges[1:]
    ) / 2

    vp = pd.DataFrame({

        "price": prices,

        "volume": volumes

    })

    vp["ratio"] = (
        vp["volume"]
        / max(
            vp["volume"].max(),
            1
        )
    )

    return (
        vp
        .sort_values(
            "volume",
            ascending=False
        )
        .reset_index(drop=True)
    )


# ============================================================
# SCORE
# ============================================================

def technical_score(df):

    x = df.iloc[-1]
    prev = df.iloc[-2]

    score = 0

    close = float(
        x["Close"]
    )

    ma20 = x["MA20"]
    ma60 = x["MA60"]

    rsi = x["RSI"]

    macd = x["MACD"]
    sig = x["MACD_Signal"]
    hist = x["MACD_Hist"]

    vol_ratio = x["Vol_Ratio"]

    if (
        pd.notna(ma20)
        and close > ma20
    ):

        score += 15

    if (
        pd.notna(ma60)
        and pd.notna(ma20)
        and ma20 > ma60
    ):

        score += 10

    if pd.notna(rsi):

        if 50 <= rsi < 70:
            score += 20

        elif 40 <= rsi < 50:
            score += 12

        else:
            score += 5

    if (
        pd.notna(macd)
        and pd.notna(sig)
    ):

        if (
            macd > sig
            and hist > 0
        ):

            score += 20

        elif macd > sig:

            score += 15

        else:

            score += 5

    if (
        pd.notna(vol_ratio)
        and 1.2 <= vol_ratio <= 3.0
        and close >= float(prev["Close"])
    ):

        score += 15

    score = int(
        max(
            0,
            min(
                100,
                score + 20
            )
        )
    )

    if score >= 80:
        label = "강한 상승세"

    elif score >= 65:
        label = "상승 우세"

    elif score >= 45:
        label = "중립 / 관망"

    elif score >= 30:
        label = "조정 국면"

    else:
        label = "약세 / 하락 위험"

    return score, label


# ============================================================
# PATTERN
# ============================================================

def detect_patterns(
    df,
    supports,
    resistances
):

    x = df.iloc[-1]

    close = float(
        x["Close"]
    )

    ma20 = x["MA20"]
    ma60 = x["MA60"]

    rsi = x["RSI"]

    macd = x["MACD"]
    sig = x["MACD_Signal"]

    vol = x["Vol_Ratio"]

    recent20_high = (
        float(
            df.iloc[-21:-1]["High"].max()
        )
        if len(df) >= 22
        else float(
            df["High"].max()
        )
    )

    patterns = []

    if (
        pd.notna(ma20)
        and pd.notna(ma60)
        and pd.notna(rsi)
    ):

        if (
            close >= ma20 * 0.985
            and close <= ma20 * 1.025
            and ma20 > ma60
            and 42 <= rsi <= 65
        ):

            patterns.append(
                "💡 눌림목 매수 관심"
            )

    if (
        close > recent20_high
        and vol >= 1.3
        and pd.notna(macd)
        and macd > sig
    ):

        patterns.append(
            "🚀 강력한 저항선 돌파"
        )

    if (
        pd.notna(rsi)
        and rsi >= 70
    ):

        patterns.append(
            "⚠️ 단기 과열"
        )

    if (
        pd.notna(ma20)
        and close < ma20
        and macd < sig
    ):

        patterns.append(
            "🔻 단기 추세 약화"
        )

    if not patterns:

        if close > ma20:

            patterns.append(
                "📈 차분한 우상향"
            )

        else:

            patterns.append(
                "💤 횡보 / 관망"
            )

    return patterns


# ============================================================
# ACTION SCENARIO
# ============================================================

def easy_action_scenario(
    df,
    score,
    supports,
    resistances,
    patterns
):

    x = df.iloc[-1]

    close = float(
        x["Close"]
    )

    rsi = (
        float(x["RSI"])
        if pd.notna(x["RSI"])
        else 50
    )

    ma20 = (
        float(x["MA20"])
        if pd.notna(x["MA20"])
        else close
    )

    s1 = (
        supports[0]["price"]
        if supports
        else ma20
    )

    s2 = (
        supports[1]["price"]
        if len(supports) > 1
        else ma20 * 0.97
    )

    r1 = (
        resistances[0]["price"]
        if resistances
        else close * 1.03
    )

    r2 = (
        resistances[1]["price"]
        if len(resistances) > 1
        else close * 1.06
    )

    if (
        "⚠️ 단기 과열"
        in patterns
    ):

        status_title = (
            "과열 구간 · 추격보다 눌림 대기"
        )

        buy_guide = (
            f"{s1:,.0f}원 부근 "
            "지지 여부 확인"
        )

        sell_guide = (
            f"{r1:,.0f}~{r2:,.0f}원 "
            "저항 구간"
        )

        wait_guide = (
            f"{s1:,.0f}원 "
            "지지선 확인"
        )

    elif (
        "💡 눌림목 매수 관심"
        in patterns
    ):

        status_title = (
            "눌림목 구간 · 추세 확인"
        )

        buy_guide = (
            f"{s1:,.0f}~{close:,.0f}원"
        )

        sell_guide = (
            f"{r1:,.0f}원 1차 저항"
        )

        wait_guide = (
            f"{s2:,.0f}원 이탈 여부"
        )

    else:

        status_title = (
            "추세 대응 구간"
        )

        buy_guide = (
            f"{s1:,.0f}원 지지 확인"
        )

        sell_guide = (
            f"{r1:,.0f}원 저항 확인"
        )

        wait_guide = (
            "박스권 흐름 모니터링"
        )

    return (
        status_title,
        buy_guide,
        sell_guide,
        wait_guide,
        s1,
        s2,
        r1,
        r2
    )


# ============================================================
# SCORE DETAIL
# ============================================================

def score_details(df):

    x = df.iloc[-1]

    close = float(x["Close"])

    ma20 = x["MA20"]
    ma60 = x["MA60"]

    rsi = x["RSI"]

    macd = x["MACD"]
    sig = x["MACD_Signal"]

    vol = x["Vol_Ratio"]

    trend = (
        "강세"
        if pd.notna(ma20)
        and pd.notna(ma60)
        and close > ma20
        and ma20 > ma60
        else "중립"
    )

    rsi_state = "중립"

    if pd.notna(rsi):

        if rsi >= 70:
            rsi_state = "과열"

        elif rsi <= 30:
            rsi_state = "침체"

        elif rsi >= 50:
            rsi_state = "상승"

        else:
            rsi_state = "약세"

    macd_state = (
        "상승"
        if pd.notna(macd)
        and pd.notna(sig)
        and macd > sig
        else "약세"
    )

    if pd.isna(vol):
        volume_state = "확인중"

    elif vol >= 1.5:
        volume_state = "강한 유입"

    elif vol >= 1.0:
        volume_state = "평균 이상"

    else:
        volume_state = "조용함"

    return (
        trend,
        rsi_state,
        macd_state,
        volume_state
    )


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
            0.63,
            0.19,
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

    for col, color in [
        ("MA5", "#f59e0b"),
        ("MA20", "#2563eb"),
        ("MA60", "#16a34a"),
        ("MA120", "#7c3aed")
    ]:

        if col in df:

            fig.add_trace(

                go.Scatter(

                    x=df.index,

                    y=df[col],

                    line=dict(
                        color=color,
                        width=1.4
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

            annotation_text=f"S{i}",

            annotation_position="bottom left"
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

            annotation_text=f"R{i}",

            annotation_position="top left"
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
                width=1.7
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

        height=640,

        margin=dict(
            l=4,
            r=4,
            t=8,
            b=8
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
            color="#64748b"
        )
    )

    fig.update_xaxes(
        showgrid=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#eef2f7",
        fixedrange=True
    )

    return fig


# ============================================================
# MARKET THEME SCANNER
# ============================================================

def scan_market_leading_themes():

    theme_scores = []

    for (
        theme_name,
        pool_dict
    ) in DC_PENSION_POOLS.items():

        theme_total_score = 0

        theme_change_sum = 0

        valid_count = 0

        top_gems_in_theme = []

        for code, name in pool_dict.items():

            raw_df, _ = load_etf_data(
                code,
                "6m"
            )

            if (
                raw_df is None
                or len(raw_df) < 30
            ):
                continue

            df = calculate_indicators(
                raw_df
            )

            x = df.iloc[-1]

            prev = df.iloc[-2]

            change = float(
                (
                    x["Close"]
                    - prev["Close"]
                )
                / prev["Close"]
                * 100
            )

            theme_change_sum += change

            valid_count += 1

            reasons = []

            score_add = 0

            if (
                pd.notna(x["MACD"])
                and pd.notna(x["MACD_Signal"])
            ):

                if (
                    prev["MACD"]
                    <= prev["MACD_Signal"]
                    and
                    x["MACD"]
                    > x["MACD_Signal"]
                ):

                    reasons.append(
                        "MACD 골든크로스"
                    )

                    score_add += 35

            if (
                pd.notna(x["Vol_Ratio"])
                and x["Vol_Ratio"] >= 1.3
                and x["Close"] > prev["Close"]
            ):

                reasons.append(
                    "거래량 유입"
                )

                score_add += 30

            if (
                pd.notna(x["MA20"])
                and
                0.98
                <= x["Close"] / x["MA20"]
                <= 1.02
            ):

                reasons.append(
                    "20일선 지지"
                )

                score_add += 25

            item_score = min(
                100,
                50 + score_add
            )

            theme_total_score += item_score

            if (
                reasons
                or change > 0
            ):

                top_gems_in_theme.append({

                    "code": code,

                    "name": name,

                    "price": float(
                        x["Close"]
                    ),

                    "change": change,

                    "reasons":
                        reasons
                        if reasons
                        else [
                            "안정적 흐름"
                        ],

                    "score":
                        item_score
                })

        if valid_count > 0:

            avg_theme_score = (
                theme_total_score
                / valid_count
            )

            avg_change = (
                theme_change_sum
                / valid_count
            )

            top_gems_in_theme = sorted(
                top_gems_in_theme,
                key=lambda x: x["score"],
                reverse=True
            )

            theme_scores.append({

                "theme_name":
                    theme_name,

                "avg_score":
                    avg_theme_score,

                "avg_change":
                    avg_change,

                "gems":
                    top_gems_in_theme
            })

    return sorted(
        theme_scores,
        key=lambda x: x["avg_score"],
        reverse=True
    )


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="app-header">

    <div class="app-brand">
        ETF RADAR
    </div>

    <div class="app-title">
        Technical Dashboard
    </div>

    <div class="app-subtitle">
        ETF Technical Analysis · Momentum · Support / Resistance
    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# MAIN TABS
# ============================================================

tab_analysis, tab_gem_finder = st.tabs([
    "📊 ETF RADAR",
    "🔥 MARKET RADAR"
])


# ============================================================
# TAB 1
# ============================================================

with tab_analysis:

    watchlist = (
        st.session_state.watchlist
    )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    search_col1, search_col2 = st.columns(
        [3, 1]
    )

    with search_col1:

        keyword_input = st.text_input(
            "종목 검색",
            placeholder="ETF명 또는 코드",
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
            "ETF 검색 중..."
        ):

            found_code, found_name = (
                search_stock_code_by_keyword(
                    keyword_input.strip()
                )
            )

            if not found_code:

                clean_test = "".join(
                    filter(
                        str.isalnum,
                        keyword_input.strip()
                    )
                )

                test_df, _ = load_etf_data(
                    clean_test,
                    "6m"
                )

                if test_df is not None:

                    found_code = clean_test

                    found_name = get_stock_name(
                        clean_test
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
                    not in st.session_state.theme_info
                ):

                    st.session_state.theme_info[
                        found_code
                    ] = {

                        "theme":
                            "신규 등록 ETF",

                        "cycle":
                            "관찰 필요",

                        "desc":
                            f"{found_name} 관련 ETF",

                        "long_view":
                            "중장기 흐름 확인 필요"
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
                    "해당 ETF를 찾을 수 없습니다."
                )


    # --------------------------------------------------------
    # Selector
    # --------------------------------------------------------

    options = list(
        watchlist.values()
    )

    if not options:

        st.warning(
            "관심종목을 먼저 추가해주세요."
        )

        st.stop()

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
        k
        for k, v in watchlist.items()
        if v == selected
    )


    # --------------------------------------------------------
    # Data
    # --------------------------------------------------------

    with st.spinner(
        "시장 데이터를 분석하고 있습니다..."
    ):

        raw_df, code = load_etf_data(
            symbol_input,
            period
        )

    if raw_df is None:

        st.error(
            "데이터를 불러오지 못했습니다."
        )

        st.stop()


    # --------------------------------------------------------
    # Analysis
    # --------------------------------------------------------

    df = (
        calculate_indicators(raw_df)
        .dropna(
            subset=["Close"]
        )
        .copy()
    )

    score, score_label = (
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

    (
        status_title,
        buy_guide,
        sell_guide,
        wait_guide,
        s1,
        s2,
        r1,
        r2
    ) = easy_action_scenario(
        df,
        score,
        supports,
        resistances,
        patterns
    )

    (
        trend_state,
        rsi_state,
        macd_state,
        volume_state
    ) = score_details(df)

    x = df.iloc[-1]

    prev = df.iloc[-2]

    price = float(
        x["Close"]
    )

    change = (
        price
        - float(prev["Close"])
    ) / float(prev["Close"]) * 100

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


    # ========================================================
    # HERO
    # ========================================================

    change_color = (
        "#16a34a"
        if change >= 0
        else "#dc2626"
    )

    st.markdown(
        f"""
        <div class="hero">

            <div class="hero-name">
                {selected.split(" (")[0]}
            </div>

            <div class="hero-code">
                {code}
            </div>

            <div class="hero-price">
                {price:,.0f}<span style="font-size:0.9rem;">원</span>
            </div>

            <div
                class="hero-change"
                style="color:{change_color};"
            >
                {"▲" if change >= 0 else "▼"}
                {abs(change):.2f}%
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # SCORE + SIGNAL
    # ========================================================

    score_col, signal_col = st.columns(
        [0.9, 1.1]
    )

    with score_col:

        st.markdown(
            f"""
            <div class="score-card">

                <div
                    class="score-ring"
                    style="--score:{score};"
                >

                    <div class="score-number">

                        <div class="score-number-main">
                            {score}
                        </div>

                        <div class="score-number-sub">
                            / 100
                        </div>

                    </div>

                </div>

                <div class="score-label">
                    {score_label}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with signal_col:

        st.markdown(
            f"""
            <div class="card card-tight">

                <div class="card-title">
                    MARKET SIGNAL
                </div>

                <div class="signal-grid">

                    <div class="signal">

                        <div class="signal-title">
                            추세
                        </div>

                        <div class="signal-value signal-good">
                            {trend_state}
                        </div>

                    </div>

                    <div class="signal">

                        <div class="signal-title">
                            RSI
                        </div>

                        <div class="signal-value">
                            {rsi:.0f}
                            · {rsi_state}
                        </div>

                    </div>

                    <div class="signal">

                        <div class="signal-title">
                            MACD
                        </div>

                        <div class="signal-value signal-good">
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


    # ========================================================
    # TODAY SIGNAL
    # ========================================================

    st.markdown(
        """
        <div class="section-head">

            <div class="section-title">
                🎯 TODAY SIGNAL
            </div>

            <div class="section-caption">
                Technical setup
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    pattern_main = patterns[0]

    st.markdown(
        f"""
        <div class="pattern-box">

            <div class="pattern-title">
                CURRENT SETUP
            </div>

            <div class="pattern-main">
                {pattern_main}
            </div>

            <div
                style="
                margin-top:5px;
                color:#64748b;
                font-size:0.72rem;
                "
            >
                {status_title}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # PRICE ZONES
    # ========================================================

    st.markdown(
        """
        <div class="section-head">

            <div class="section-title">
                📍 PRICE ZONES
            </div>

            <div class="section-caption">
                Key levels
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    z1, z2 = st.columns(2)

    with z1:

        st.markdown(
            f"""
            <div class="action-card action-buy">

                <div
                    class="action-label"
                    style="color:#15803d;"
                >
                    🟢 INTEREST ZONE
                </div>

                <div class="action-price">
                    {s1:,.0f}원
                </div>

                <div class="action-desc">
                    1차 지지 · {buy_guide}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with z2:

        st.markdown(
            f"""
            <div class="action-card action-sell">

                <div
                    class="action-label"
                    style="color:#dc2626;"
                >
                    🔴 RESISTANCE
                </div>

                <div class="action-price">
                    {r1:,.0f}원
                </div>

                <div class="action-desc">
                    1차 저항 · {sell_guide}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    z3, z4 = st.columns(2)

    with z3:

        st.markdown(
            f"""
            <div class="action-card action-wait">

                <div
                    class="action-label"
                    style="color:#b45309;"
                >
                    🟡 SECOND SUPPORT
                </div>

                <div class="action-price">
                    {s2:,.0f}원
                </div>

                <div class="action-desc">
                    핵심 지지 · {wait_guide}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with z4:

        st.markdown(
            f"""
            <div class="action-card action-break">

                <div
                    class="action-label"
                    style="color:#1d4ed8;"
                >
                    🔵 BREAKOUT
                </div>

                <div class="action-price">
                    {r2:,.0f}원+
                </div>

                <div class="action-desc">
                    2차 저항 돌파 확인 구간
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # PRICE MAP
    # ========================================================

    st.markdown(
        """
        <div class="section-head">

            <div class="section-title">
                🗺 PRICE MAP
            </div>

            <div class="section-caption">
                Support / Resistance
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
                    R2 · 2차 저항
                </div>

                <div
                    class="price-number"
                    style="color:#dc2626;"
                >
                    {r2:,.0f}원
                </div>

            </div>

            <div class="price-row">

                <div class="price-name">
                    R1 · 1차 저항
                </div>

                <div
                    class="price-number"
                    style="color:#dc2626;"
                >
                    {r1:,.0f}원
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

                <div class="price-name">
                    NOW · 현재가
                </div>

                <div
                    class="price-number"
                    style="color:#2563eb;"
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
                    {s1:,.0f}원
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
                    {s2:,.0f}원
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # CHART
    # ========================================================

    st.markdown(
        """
        <div class="section-head">

            <div class="section-title">
                📈 PRICE ACTION
            </div>

            <div class="section-caption">
                Candle · MA · Volume · RSI
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
        key=f"main_chart_{symbol_input}_{period}"
    )


    # ========================================================
    # INDICATORS
    # ========================================================

    st.markdown(
        """
        <div class="section-head">

            <div class="section-title">
                📊 MOMENTUM
            </div>

            <div class="section-caption">
                Current indicators
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    i1, i2, i3 = st.columns(3)

    with i1:

        st.markdown(
            f"""
            <div class="card card-tight">

                <div class="card-title">
                    RSI
                </div>

                <div class="card-value">
                    {rsi:.1f}
                </div>

                <div class="card-sub">
                    {rsi_state}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with i2:

        st.markdown(
            f"""
            <div class="card card-tight">

                <div class="card-title">
                    VOLUME
                </div>

                <div class="card-value">
                    {vol_ratio:.1f}x
                </div>

                <div class="card-sub">
                    20일 평균 대비
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with i3:

        macd_hist = float(
            x["MACD_Hist"]
        )

        macd_arrow = (
            "↑"
            if macd_hist > 0
            else "↓"
        )

        st.markdown(
            f"""
            <div class="card card-tight">

                <div class="card-title">
                    MACD
                </div>

                <div class="card-value">
                    {macd_arrow}
                </div>

                <div class="card-sub">
                    {macd_state}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # DETAILED TABS
    # ========================================================

    detail_tabs = st.tabs([
        "📍 매물대",
        "🏛 테마",
        "📖 지표"
    ])


    # --------------------------------------------------------
    # Volume Profile
    # --------------------------------------------------------

    with detail_tabs[0]:

        st.markdown(
            "#### 매물대 집중 구간"
        )

        if not vp.empty:

            vp_show = (
                vp.head(7)[
                    [
                        "price",
                        "ratio"
                    ]
                ]
                .copy()
            )

            vp_show["가격대"] = (
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
                    f"{x * 100:.0f}%"
                )
            )

            st.dataframe(
                vp_show[
                    [
                        "가격대",
                        "집중도"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        st.markdown(
            "#### 지지 / 저항"
        )

        sc, rc = st.columns(2)

        with sc:

            st.markdown(
                "**🟢 SUPPORT**"
            )

            for i, item in enumerate(
                supports[:3],
                1
            ):

                st.success(
                    f"S{i} · "
                    f"{item['price']:,.0f}원"
                )

        with rc:

            st.markdown(
                "**🔴 RESISTANCE**"
            )

            for i, item in enumerate(
                resistances[:3],
                1
            ):

                st.warning(
                    f"R{i} · "
                    f"{item['price']:,.0f}원"
                )


    # --------------------------------------------------------
    # Theme
    # --------------------------------------------------------

    with detail_tabs[1]:

        theme_info = (
            st.session_state.theme_info
            .get(
                code,
                {
                    "theme":
                        "미등록 테마",

                    "cycle":
                        "관찰 필요",

                    "desc":
                        "정보 등록 필요",

                    "long_view":
                        "중장기 관점을 입력해주세요."
                }
            )
        )

        st.markdown(
            f"""
            <div class="card">

                <div class="card-title">
                    THEME
                </div>

                <div
                    style="
                    font-size:1.1rem;
                    font-weight:850;
                    margin-top:4px;
                    "
                >
                    {theme_info["theme"]}
                </div>

                <div
                    style="
                    margin-top:10px;
                    color:#2563eb;
                    font-weight:800;
                    font-size:0.78rem;
                    "
                >
                    {theme_info["cycle"]}
                </div>

                <div
                    style="
                    margin-top:12px;
                    color:#64748b;
                    font-size:0.78rem;
                    line-height:1.55;
                    "
                >
                    {theme_info["desc"]}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="action-card action-break">

                <div
                    class="action-label"
                    style="color:#1d4ed8;"
                >
                    LONG VIEW
                </div>

                <div
                    style="
                    margin-top:5px;
                    font-size:0.8rem;
                    line-height:1.5;
                    color:#334155;
                    "
                >
                    {theme_info["long_view"]}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # Guide
    # --------------------------------------------------------

    with detail_tabs[2]:

        st.markdown(
            """
            #### RSI

            **70 이상**
            → 단기 과열 영역

            **50~70**
            → 상승 모멘텀 영역

            **30 이하**
            → 침체 영역

            ---

            #### MACD

            MACD가 Signal보다 위에 있으면
            단기 모멘텀이 상대적으로 강한 상태입니다.

            ---

            #### 거래량

            **1.0x**
            → 20일 평균 수준

            **1.5x 이상**
            → 거래량 증가

            **2.0x 이상**
            → 강한 거래량 유입

            ---

            #### 이동평균

            MA20 > MA60

            → 중단기 추세가 상대적으로 강한 상태입니다.
            """
        )


    # ========================================================
    # DELETE
    # ========================================================

    with st.expander(
        "⚙️ 관심종목 관리"
    ):

        if st.button(
            "🗑 현재 종목 삭제",
            use_container_width=True
        ):

            del st.session_state.watchlist[
                symbol_input
            ]

            save_json_file(
                WATCHLIST_FILE,
                st.session_state.watchlist
            )

            st.rerun()


# ============================================================
# TAB 2 : MARKET RADAR
# ============================================================

with tab_gem_finder:

    st.markdown(
        """
        <div class="card">

            <div class="card-title">
                MARKET RADAR
            </div>

            <div
                style="
                font-size:1.2rem;
                font-weight:900;
                margin-top:4px;
                "
            >
                시장 주도 테마 탐색
            </div>

            <div
                style="
                color:#64748b;
                font-size:0.75rem;
                line-height:1.5;
                margin-top:6px;
                "
            >
                9개 DC연금 테마군의
                모멘텀·거래량·이동평균을
                자동으로 분석합니다.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    scan_btn = st.button(
        "🚀 MARKET RADAR 실행",
        use_container_width=True,
        type="primary",
        key="auto_scan_btn"
    )

    if scan_btn:

        st.cache_data.clear()

    with st.spinner(
        "시장 테마를 분석하고 있습니다..."
    ):

        leading_themes = (
            scan_market_leading_themes()
        )


    if leading_themes:

        top_theme = leading_themes[0]

        top_change_color = (
            "#16a34a"
            if top_theme["avg_change"] >= 0
            else "#dc2626"
        )

        # ----------------------------------------------------
        # Top Theme
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div class="hero">

                <div class="card-title">
                    CURRENT MARKET LEADER
                </div>

                <div
                    style="
                    font-size:1.2rem;
                    font-weight:900;
                    margin-top:4px;
                    "
                >
                    {top_theme["theme_name"]}
                </div>

                <div
                    style="
                    display:flex;
                    align-items:end;
                    justify-content:space-between;
                    margin-top:10px;
                    "
                >

                    <div>

                        <div
                            style="
                            font-size:0.68rem;
                            color:#64748b;
                            "
                        >
                            MOMENTUM SCORE
                        </div>

                        <div
                            style="
                            font-size:2rem;
                            font-weight:900;
                            color:#2563eb;
                            "
                        >
                            {top_theme["avg_score"]:.1f}
                        </div>

                    </div>

                    <div
                        style="
                        color:{top_change_color};
                        font-weight:900;
                        font-size:0.9rem;
                        "
                    >
                        {"▲"
                         if top_theme["avg_change"] >= 0
                         else "▼"}
                        {abs(top_theme["avg_change"]):.2f}%
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # Ranking
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="section-head">

                <div class="section-title">
                    🔥 THEME RANKING
                </div>

                <div class="section-caption">
                    Momentum
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        for rank, th in enumerate(
            leading_themes,
            1
        ):

            theme_change_color = (
                "#16a34a"
                if th["avg_change"] >= 0
                else "#dc2626"
            )

            with st.expander(
                f"{rank:02d}  "
                f"{th['theme_name']}   "
                f"· {th['avg_score']:.1f}점"
            ):

                st.markdown(
                    f"""
                    <div class="theme-card">

                        <div class="theme-rank">
                            RANK {rank:02d}
                        </div>

                        <div class="theme-name">
                            {th["theme_name"]}
                        </div>

                        <div
                            style="
                            display:flex;
                            justify-content:space-between;
                            align-items:end;
                            margin-top:8px;
                            "
                        >

                            <div>

                                <div
                                    style="
                                    color:#64748b;
                                    font-size:0.65rem;
                                    "
                                >
                                    ACTIVATION
                                </div>

                                <div class="theme-score">
                                    {th["avg_score"]:.1f}
                                </div>

                            </div>

                            <div
                                class="theme-change"
                                style="
                                color:{theme_change_color};
                                "
                            >
                                {"▲"
                                 if th["avg_change"] >= 0
                                 else "▼"}
                                {abs(th["avg_change"]):.2f}%
                            </div>

                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


                if th["gems"]:

                    st.markdown(
                        "**💎 MOMENTUM ETF**"
                    )

                    for g in th["gems"][:5]:

                        g_color = (
                            "#16a34a"
                            if g["change"] >= 0
                            else "#dc2626"
                        )

                        reasons_str = (
                            " · ".join(
                                g["reasons"]
                            )
                        )

                        st.markdown(
                            f"""
                            <div class="gem">

                                <div
                                    style="
                                    display:flex;
                                    justify-content:space-between;
                                    "
                                >

                                    <div class="gem-name">
                                        💎 {g["name"]}
                                    </div>

                                    <div
                                        style="
                                        font-size:0.72rem;
                                        font-weight:850;
                                        color:{g_color};
                                        "
                                    >
                                        {"▲"
                                         if g["change"] >= 0
                                         else "▼"}
                                        {abs(g["change"]):.2f}%
                                    </div>

                                </div>

                                <div class="gem-meta">

                                    {g["code"]}
                                    ·
                                    {g["price"]:,.0f}원
                                    ·
                                    기술점수 {g["score"]}

                                </div>

                                <div
                                    class="gem-meta"
                                    style="
                                    color:#334155;
                                    "
                                >
                                    {reasons_str}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                else:

                    st.info(
                        "현재 뚜렷한 신호가 없습니다."
                    )

    else:

        st.warning(
            "시장 데이터를 불러오지 못했습니다."
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
        font-size:0.65rem;
        margin-top:25px;
        padding-top:12px;
        border-top:1px solid #e2e8f0;
        "
    >
        ETF RADAR v10 · Technical Dashboard
    </div>
    """,
    unsafe_allow_html=True
)