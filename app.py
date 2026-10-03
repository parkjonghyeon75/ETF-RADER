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
from datetime import datetime
import html


# ============================================================
# ETF RADAR
# Simple ETF Investment Direction Guide
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 "Noto Sans KR", sans-serif;
}

.stApp {
    background: #F5F7FA;
    color: #172033;
}

.block-container {
    max-width: 760px;
    padding-top: 1rem;
    padding-bottom: 4rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* ---------- Header ---------- */

.app-header {
    background: linear-gradient(135deg, #172033, #253A5E);
    border-radius: 22px;
    padding: 22px 20px;
    margin-bottom: 16px;
    color: white;
    box-shadow: 0 8px 24px rgba(30,45,70,0.12);
}

.app-title {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -1px;
}

.app-subtitle {
    font-size: 14px;
    margin-top: 5px;
    color: #D8E1EF;
}

/* ---------- Cards ---------- */

.card {
    background: #FFFFFF;
    border: 1px solid #E4E8EF;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 13px;
    box-shadow: 0 5px 18px rgba(30,45,70,0.045);
}

.card-title {
    font-size: 15px;
    font-weight: 800;
    color: #172033;
    margin-bottom: 10px;
}

.card-subtitle {
    font-size: 12px;
    color: #7A8494;
    margin-bottom: 10px;
}

/* ---------- Hero ---------- */

.hero-card {
    background: #FFFFFF;
    border: 1px solid #E2E7EF;
    border-radius: 22px;
    padding: 20px;
    margin-bottom: 13px;
}

.hero-name {
    font-size: 18px;
    font-weight: 800;
    color: #172033;
}

.hero-code {
    font-size: 12px;
    color: #8A94A5;
    margin-top: 3px;
}

.hero-price {
    font-size: 36px;
    line-height: 1;
    font-weight: 850;
    margin-top: 18px;
    letter-spacing: -1px;
}

.hero-change {
    font-size: 15px;
    font-weight: 700;
    margin-top: 8px;
}

/* ---------- Judgment ---------- */

.judgment {
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 13px;
}

.judgment-green {
    background: #ECF9F1;
    border: 1px solid #C8EBD7;
}

.judgment-blue {
    background: #EDF5FF;
    border: 1px solid #C9DFFF;
}

.judgment-yellow {
    background: #FFF8E7;
    border: 1px solid #F5DF9C;
}

.judgment-red {
    background: #FFF0F0;
    border: 1px solid #F1CCCC;
}

.judgment-label {
    font-size: 12px;
    font-weight: 800;
    margin-bottom: 5px;
    letter-spacing: 0.2px;
}

.judgment-title {
    font-size: 24px;
    font-weight: 850;
    letter-spacing: -0.7px;
}

.judgment-desc {
    margin-top: 8px;
    font-size: 14px;
    line-height: 1.55;
}

/* ---------- Evidence ---------- */

.evidence-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 9px;
}

.evidence-item {
    background: #F7F9FC;
    border-radius: 13px;
    padding: 12px;
}

.evidence-label {
    font-size: 11px;
    color: #7A8494;
}

.evidence-value {
    font-size: 17px;
    font-weight: 800;
    margin-top: 3px;
    color: #172033;
}

.evidence-note {
    font-size: 11px;
    color: #7A8494;
    margin-top: 3px;
}

/* ---------- Status ---------- */

.status-pill {
    display: inline-block;
    border-radius: 999px;
    padding: 6px 11px;
    font-size: 12px;
    font-weight: 800;
    margin-right: 5px;
    margin-bottom: 5px;
}

.pill-green {
    background: #E8F7EE;
    color: #167344;
}

.pill-blue {
    background: #EAF3FF;
    color: #1D5EA8;
}

.pill-yellow {
    background: #FFF4D6;
    color: #8A6500;
}

.pill-red {
    background: #FFE8E8;
    color: #A52D2D;
}

.pill-gray {
    background: #EEF1F5;
    color: #657083;
}

/* ---------- Guide ---------- */

.guide-row {
    border-top: 1px solid #EEF1F5;
    padding: 13px 0;
}

.guide-row:first-child {
    border-top: none;
    padding-top: 0;
}

.guide-title {
    font-size: 14px;
    font-weight: 800;
}

.guide-desc {
    font-size: 13px;
    color: #687386;
    margin-top: 4px;
    line-height: 1.5;
}

/* ---------- Theme ---------- */

.theme-card {
    background: #FFFFFF;
    border: 1px solid #E3E8F0;
    border-radius: 18px;
    padding: 17px;
    margin-bottom: 12px;
}

.theme-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.theme-name {
    font-size: 18px;
    font-weight: 850;
}

.theme-stage {
    font-size: 11px;
    font-weight: 800;
    border-radius: 999px;
    padding: 6px 9px;
}

.stage-leader {
    background: #EAF3FF;
    color: #245B9B;
}

.stage-follower {
    background: #ECF9F1;
    color: #187344;
}

.stage-early {
    background: #FFF4D6;
    color: #876400;
}

.stage-watch {
    background: #EEF1F5;
    color: #687386;
}

.theme-desc {
    font-size: 13px;
    color: #697386;
    line-height: 1.5;
    margin-top: 9px;
}

.theme-chain {
    display: flex;
    align-items: center;
    gap: 7px;
    overflow-x: auto;
    padding: 5px 0 12px 0;
}

.chain-item {
    min-width: 110px;
    background: #FFFFFF;
    border: 1px solid #DDE4ED;
    border-radius: 13px;
    padding: 11px;
    text-align: center;
}

.chain-title {
    font-size: 12px;
    font-weight: 800;
}

.chain-stage {
    font-size: 10px;
    color: #7A8494;
    margin-top: 4px;
}

.chain-arrow {
    color: #9AA4B3;
    font-size: 18px;
}

/* ---------- Footer ---------- */

.disclaimer {
    color: #8A94A5;
    font-size: 11px;
    line-height: 1.5;
    text-align: center;
    margin-top: 25px;
}

/* ---------- Mobile ---------- */

@media (max-width: 600px) {

    .block-container {
        padding-left: 0.7rem;
        padding-right: 0.7rem;
    }

    .app-title {
        font-size: 25px;
    }

    .hero-price {
        font-size: 32px;
    }

    .judgment-title {
        font-size: 22px;
    }

    .evidence-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 0.35rem;
    }

    button {
        border-radius: 12px !important;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# CONFIG
# ============================================================

WATCHLIST_FILE = "watchlist.json"
THEME_FILE = "theme_info.json"


# ============================================================
# ETF UNIVERSE
# ============================================================

ETF_UNIVERSE = {

    # 미국 / 글로벌
    "360750": "TIGER 미국S&P500",
    "379800": "KODEX 미국S&P500TR",
    "448290": "SOL 미국S&P500",
    "133690": "TIGER 미국나스닥100",
    "379810": "KODEX 미국나스닥100TR",

    # AI / 반도체
    "487240": "KODEX 미국AI테크TOP10",
    "452330": "TIGER 미국테크TOP10",
    "395160": "KODEX AI반도체TOP2플러스",
    "462100": "TIGER AI반도체핵심공정",
    "486410": "TIGER 미국반도체TOP10",

    # 전력 / 원전
    "471990": "KODEX AI전력핵심설비",
    "445380": "SOL 원자력TOP3플러스",
    "465560": "TIGER 글로벌원자력",

    # 2차전지
    "305540": "KODEX 2차전지산업",
    "364980": "TIGER 2차전지소부장",
    "438320": "KODEX 2차전지핵심소재",

    # 로봇 / 우주
    "465610": "KODEX 로봇산업",
    "476250": "TIGER 우주항공&로봇",

    # 헬스케어 / 바이오
    "329200": "TIGER 헬스케어",
    "266420": "KODEX 바이오",
    "462610": "ARIRANG 3대주주바이오",

    # 배당
    "458730": "TIGER 미국배당다우존스",
    "476480": "KODEX 미국배당커버드콜",
    "451780": "TIGER 미국배당+7%프리미엄",

    # 금리 / 채권
    "423160": "KODEX CD금리액티브(합성)",
    "449170": "TIGER KOFR금리액티브",
    "308620": "KODEX 미국채울트라30년선물",
    "365780": "TIGER 미국채30년스트립액티브",
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
# THEME DATABASE
# ============================================================

THEMES = {

    "AI 반도체": {
        "stage": "LEADER",
        "label": "현재 주도",
        "class": "stage-leader",
        "description":
            "AI 서버와 고성능 연산 수요의 핵심 축. 반도체 업황과 AI 투자 사이클을 함께 확인합니다.",
        "etfs": [
            "395160",
            "462100",
            "486410",
            "487240",
            "452330",
        ],
    },

    "데이터센터": {
        "stage": "FOLLOWER",
        "label": "후속 수혜",
        "class": "stage-follower",
        "description":
            "AI 데이터센터 투자 확대가 지속될 경우 전력·서버·네트워크 관련 산업으로 관심이 확산되는 구간을 관찰합니다.",
        "etfs": [
            "471990",
            "487240",
            "486410",
        ],
    },

    "전력 인프라": {
        "stage": "FOLLOWER",
        "label": "후속 수혜",
        "class": "stage-follower",
        "description":
            "AI 데이터센터 전력수요 증가와 함께 전력설비 및 원전 관련 산업의 순환 가능성을 관찰합니다.",
        "etfs": [
            "471990",
            "445380",
            "465560",
        ],
    },

    "냉각·열관리": {
        "stage": "EARLY",
        "label": "선행 관심",
        "class": "stage-early",
        "description":
            "고밀도 AI 데이터센터에서 전력뿐 아니라 열관리 수요가 커지는지를 확인하는 후속 테마입니다.",
        "etfs": [],
    },

    "AI 의료·바이오": {
        "stage": "EARLY",
        "label": "선행 관심",
        "class": "stage-early",
        "description":
            "AI와 바이오·헬스케어의 결합 가능성을 장기 테마로 관찰합니다. ETF 자체의 바이오 비중과 추세를 함께 확인합니다.",
        "etfs": [
            "329200",
            "266420",
            "462610",
        ],
    },

    "로봇·자동화": {
        "stage": "WATCH",
        "label": "관찰",
        "class": "stage-watch",
        "description":
            "AI와 자동화 투자 확대가 산업용·서비스 로봇 수요로 이어지는지를 관찰합니다.",
        "etfs": [
            "465610",
            "476250",
        ],
    },

    "2차전지": {
        "stage": "WATCH",
        "label": "관찰",
        "class": "stage-watch",
        "description":
            "배터리 업황과 소재·소부장 사이클 회복 여부를 중심으로 관찰합니다.",
        "etfs": [
            "305540",
            "364980",
            "438320",
        ],
    },
}


THEME_CHAIN = [
    ("AI 반도체", "현재 주도"),
    ("데이터센터", "후속 수혜"),
    ("전력 인프라", "후속 수혜"),
    ("냉각·열관리", "선행 관심"),
    ("AI 의료·바이오", "선행 관심"),
]


# ============================================================
# UTILITY
# ============================================================

def esc(value):
    return html.escape(str(value))


def safe_float(value, default=np.nan):
    try:
        return float(value)
    except Exception:
        return default


def fmt_price(value):
    if pd.isna(value):
        return "-"
    return f"{value:,.0f}"


def fmt_pct(value):
    if pd.isna(value):
        return "-"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def render_html(content):
    st.markdown(content, unsafe_allow_html=True)


# ============================================================
# WATCHLIST
# ============================================================

def load_watchlist():

    if not os.path.exists(WATCHLIST_FILE):
        return DEFAULT_WATCHLIST.copy()

    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        result = []

        for code in data:
            code = str(code)

            if code in ETF_UNIVERSE:
                result.append(code)

        return result if result else DEFAULT_WATCHLIST.copy()

    except Exception:
        return DEFAULT_WATCHLIST.copy()


def save_watchlist(items):

    try:
        with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ============================================================
# NAVER DATA
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def fetch_from_naver(code, count=500):

    url = (
        "https://fchart.stock.naver.com/sise.nhn?"
        f"symbol={urllib.parse.quote(code)}"
        f"&timeframe=day"
        f"&count={count}"
        f"&requestType=0"
    )

    try:

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        )

        with urllib.request.urlopen(req, timeout=8) as response:
            raw = response.read()

        root = ET.fromstring(raw)

        rows = []

        for item in root.findall(".//item"):

            data = item.attrib.get("data", "")

            parts = data.split("|")

            if len(parts) != 6:
                continue

            date, open_, high, low, close, volume = parts

            rows.append({
                "Date": pd.to_datetime(date),
                "Open": safe_float(open_),
                "High": safe_float(high),
                "Low": safe_float(low),
                "Close": safe_float(close),
                "Volume": safe_float(volume),
            })

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)

        df = df.sort_values("Date")
        df = df.drop_duplicates("Date")
        df = df.set_index("Date")

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# YFINANCE FALLBACK
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def fetch_from_yfinance(code):

    try:

        ticker = yf.Ticker(f"{code}.KS")

        df = ticker.history(
            period="2y",
            interval="1d",
            auto_adjust=False
        )

        if df is None or df.empty:
            return pd.DataFrame()

        df = df.reset_index()

        if "Date" not in df.columns:
            return pd.DataFrame()

        df = df.rename(
            columns={
                "Open": "Open",
                "High": "High",
                "Low": "Low",
                "Close": "Close",
                "Volume": "Volume",
            }
        )

        required = [
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]

        for col in required:
            if col not in df.columns:
                return pd.DataFrame()

        df = df[required]

        df["Date"] = pd.to_datetime(df["Date"])

        try:
            df["Date"] = df["Date"].dt.tz_localize(None)
        except Exception:
            pass

        df = df.set_index("Date")

        return df.dropna(subset=["Close"])

    except Exception:
        return pd.DataFrame()


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def load_etf_data(code):

    df = fetch_from_naver(code, 500)

    if not df.empty:
        return df

    return fetch_from_yfinance(code)


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

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    df["RSI"] = 100 - (100 / (1 + rs))

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

    df["BB_MID"] = close.rolling(20).mean()

    std20 = close.rolling(20).std()

    df["BB_UPPER"] = df["BB_MID"] + 2 * std20
    df["BB_LOWER"] = df["BB_MID"] - 2 * std20

    df["VOL20"] = df["Volume"].rolling(20).mean()

    df["VOL_RATIO"] = (
        df["Volume"] /
        df["VOL20"].replace(0, np.nan)
    )

    df["RET_5"] = close.pct_change(5) * 100
    df["RET_20"] = close.pct_change(20) * 100
    df["RET_60"] = close.pct_change(60) * 100

    df["HIGH20"] = close.rolling(20).max()
    df["LOW20"] = close.rolling(20).min()

    return df


# ============================================================
# SUPPORT / RESISTANCE
# ============================================================

def calculate_levels(df):

    recent = df.tail(60)

    if recent.empty:
        return np.nan, np.nan

    support_candidates = []

    if "MA20" in recent.columns:
        support_candidates.append(
            recent["MA20"].dropna().iloc[-1]
            if not recent["MA20"].dropna().empty
            else np.nan
        )

    if "MA60" in recent.columns:
        support_candidates.append(
            recent["MA60"].dropna().iloc[-1]
            if not recent["MA60"].dropna().empty
            else np.nan
        )

    support_candidates.append(
        recent["Low"].tail(20).min()
    )

    support_candidates = [
        x for x in support_candidates
        if not pd.isna(x)
    ]

    support = max(support_candidates) if support_candidates else np.nan

    resistance = recent["High"].tail(20).max()

    return support, resistance


# ============================================================
# TREND STATUS
# ============================================================

def get_trend_status(row):

    close = safe_float(row.get("Close"))
    ma20 = safe_float(row.get("MA20"))
    ma60 = safe_float(row.get("MA60"))

    if pd.isna(close) or pd.isna(ma20) or pd.isna(ma60):
        return "데이터 부족", "gray"

    if close > ma20 and ma20 > ma60:
        return "상승 추세", "green"

    if close > ma60 and ma20 >= ma60:
        return "상승 유지", "green"

    if close < ma20 and ma20 < ma60:
        return "하락 추세", "red"

    if close < ma60:
        return "추세 약화", "red"

    return "방향 탐색", "yellow"


# ============================================================
# MARKET / THEME OUTLOOK
# ============================================================

def get_theme_outlook(code):

    leader_codes = {
        "395160",
        "487240",
        "471990",
        "133690",
        "360750",
        "458730",
    }

    positive_codes = {
        "462100",
        "486410",
        "452330",
        "445380",
        "465560",
        "465610",
        "476250",
    }

    weak_codes = {
        "305540",
        "364980",
        "438320",
    }

    if code in leader_codes:
        return "긍정적", "현재 시장 관심이 높은 핵심 축으로 분류"

    if code in positive_codes:
        return "긍정적", "관련 산업 확산 여부를 확인할 필요"

    if code in weak_codes:
        return "중립", "업황 회복 확인이 필요한 구간"

    return "중립", "시장 추세와 ETF 가격 흐름을 함께 확인"


# ============================================================
# JUDGMENT ENGINE
# ============================================================

def build_judgment(df, code):

    row = df.iloc[-1]

    close = safe_float(row["Close"])
    ma20 = safe_float(row["MA20"])
    ma60 = safe_float(row["MA60"])
    rsi = safe_float(row["RSI"])
    macd = safe_float(row["MACD"])
    signal = safe_float(row["MACD_SIGNAL"])
    vol_ratio = safe_float(row["VOL_RATIO"])
    ret20 = safe_float(row["RET_20"])

    theme_outlook, theme_note = get_theme_outlook(code)

    trend_positive = (
        not pd.isna(close)
        and not pd.isna(ma20)
        and not pd.isna(ma60)
        and close > ma20
        and ma20 >= ma60
    )

    trend_negative = (
        not pd.isna(close)
        and not pd.isna(ma20)
        and not pd.isna(ma60)
        and close < ma20
        and ma20 < ma60
    )

    momentum_positive = (
        not pd.isna(macd)
        and not pd.isna(signal)
        and macd >= signal
    )

    overextended = (
        (not pd.isna(rsi) and rsi >= 70)
        or
        (not pd.isna(ma20) and close > ma20 * 1.08)
        or
        (not pd.isna(ret20) and ret20 >= 12)
    )

    pullback_zone = (
        not pd.isna(ma20)
        and abs(close / ma20 - 1) <= 0.035
        and not pd.isna(rsi)
        and 42 <= rsi <= 67
    )

    # --------------------------------------------------------
    # 1. Risk
    # --------------------------------------------------------

    if trend_negative:

        return {
            "label": "리스크 재검토",
            "title": "추세가 약해졌습니다",
            "color": "red",
            "description":
                "가격이 주요 이동평균 아래에 있고 중기 추세도 약해진 상태입니다. "
                "추가 매수보다 추세 회복 여부를 먼저 확인하는 구간입니다.",
            "theme_outlook": theme_outlook,
            "theme_note": theme_note,
        }

    # --------------------------------------------------------
    # 2. Pullback wait
    # --------------------------------------------------------

    if trend_positive and overextended:

        return {
            "label": "눌림목 대기",
            "title": "추세는 살아 있지만 가격 부담이 있습니다",
            "color": "yellow",
            "description":
                "중기 추세는 양호하지만 최근 상승폭 또는 단기 과열 정도가 커졌습니다. "
                "현재 가격을 추격하기보다는 이동평균이나 지지선 부근의 눌림을 확인하는 시나리오입니다.",
            "theme_outlook": theme_outlook,
            "theme_note": theme_note,
        }

    # --------------------------------------------------------
    # 3. Buy review
    # --------------------------------------------------------

    if trend_positive and pullback_zone:

        return {
            "label": "매수 검토",
            "title": "추세 안에서 눌림을 확인하는 구간",
            "color": "green",
            "description":
                "중기 상승 추세가 유지되면서 가격이 주요 이동평균에 가까워졌습니다. "
                "거래량과 시장 흐름이 유지된다면 분할 접근을 검토할 수 있는 구간입니다.",
            "theme_outlook": theme_outlook,
            "theme_note": theme_note,
        }

    # --------------------------------------------------------
    # 4. Hold
    # --------------------------------------------------------

    if trend_positive:

        return {
            "label": "보유 유지",
            "title": "상승 추세가 유지되고 있습니다",
            "color": "blue",
            "description":
                "가격이 주요 이동평균 위에 있고 중기 추세도 유지되고 있습니다. "
                "급등 직후가 아니라면 추세 훼손 여부를 확인하면서 보유하는 시나리오가 가능합니다.",
            "theme_outlook": theme_outlook,
            "theme_note": theme_note,
        }

    # --------------------------------------------------------
    # 5. Momentum turn
    # --------------------------------------------------------

    if (
        not pd.isna(macd)
        and not pd.isna(signal)
        and macd > signal
        and not pd.isna(rsi)
        and rsi >= 45
    ):

        return {
            "label": "관망 후 확인",
            "title": "회복 신호를 확인하는 구간",
            "color": "yellow",
            "description":
                "모멘텀은 일부 개선되고 있지만 중기 추세가 아직 완전히 회복됐다고 보기 어렵습니다. "
                "MA20과 MA60의 방향 전환을 함께 확인하는 것이 좋습니다.",
            "theme_outlook": theme_outlook,
            "theme_note": theme_note,
        }

    return {
        "label": "관망",
        "title": "방향을 확인할 필요가 있습니다",
        "color": "yellow",
        "description":
            "현재 가격과 중기 이동평균의 관계가 뚜렷하지 않습니다. "
            "추세가 다시 만들어지는지 확인한 뒤 판단하는 시나리오입니다.",
        "theme_outlook": theme_outlook,
        "theme_note": theme_note,
    }


# ============================================================
# POSITION GUIDE
# ============================================================

def build_position_guide(
    df,
    judgment,
    avg_price=None,
    shares=None
):

    row = df.iloc[-1]

    close = safe_float(row["Close"])
    ma20 = safe_float(row["MA20"])
    ma60 = safe_float(row["MA60"])
    rsi = safe_float(row["RSI"])

    support, resistance = calculate_levels(df)

    result = []

    if avg_price is not None and shares is not None:

        pnl = (close - avg_price) * shares
        pnl_pct = (
            (close / avg_price - 1) * 100
            if avg_price != 0
            else np.nan
        )

        result.append({
            "title": "현재 보유상태",
            "desc":
                f"현재가 {fmt_price(close)}원 / "
                f"평균단가 {fmt_price(avg_price)}원 / "
                f"{shares:,.0f}주 / "
                f"수익률 {fmt_pct(pnl_pct)}"
        })

        if judgment["label"] == "눌림목 대기":

            result.append({
                "title": "추가매수",
                "desc":
                    "현재 가격을 추격하기보다 MA20 또는 지지선 부근에서 "
                    "반등과 거래량을 확인한 뒤 분할 접근하는 시나리오입니다."
            })

        elif judgment["label"] == "리스크 재검토":

            result.append({
                "title": "비중 점검",
                "desc":
                    "MA20과 MA60 아래에서 약세가 이어지는지 확인하고 "
                    "추가매수보다 보유비중과 리스크를 먼저 점검하는 구간입니다."
            })

        else:

            result.append({
                "title": "보유 전략",
                "desc":
                    "추세가 유지되는 동안에는 급하게 대응하기보다 "
                    "MA20 이탈과 모멘텀 약화 여부를 확인하는 방식입니다."
            })

        if not pd.isna(resistance):

            result.append({
                "title": "차익실현 검토",
                "desc":
                    f"최근 저항선 약 {fmt_price(resistance)}원 부근에서 "
                    "거래량 둔화나 모멘텀 약화가 동시에 나타나는지 확인합니다."
            })

        if not pd.isna(support):

            result.append({
                "title": "리스크 재검토 기준",
                "desc":
                    f"주요 지지선 약 {fmt_price(support)}원과 MA20/MA60을 "
                    "동시에 확인합니다."
            })

    else:

        if judgment["label"] == "눌림목 대기":

            result.append({
                "title": "현재",
                "desc":
                    "상승 추세는 살아 있지만 가격 부담이 있어 추격매수보다 눌림 확인이 우선입니다."
            })

            result.append({
                "title": "관심 가격대",
                "desc":
                    f"MA20 약 {fmt_price(ma20)}원 또는 주요 지지선 "
                    f"{fmt_price(support)}원 부근의 반응을 확인합니다."
            })

        elif judgment["label"] == "매수 검토":

            result.append({
                "title": "현재",
                "desc":
                    "추세가 유지되고 가격이 이동평균에 가까워진 구간이라 분할 접근을 검토할 수 있습니다."
            })

            result.append({
                "title": "진입 확인",
                "desc":
                    "지지선 반응과 거래량 회복이 함께 나타나는지를 확인합니다."
            })

        elif judgment["label"] == "보유 유지":

            result.append({
                "title": "현재",
                "desc":
                    "상승 추세가 유지되고 있어 급하게 추격하기보다 조정 시 진입 기회를 관찰합니다."
            })

        elif judgment["label"] == "리스크 재검토":

            result.append({
                "title": "현재",
                "desc":
                    "하락 추세 또는 추세 약화가 확인되고 있어 신규 진입보다 회복 여부를 확인합니다."
            })

        else:

            result.append({
                "title": "현재",
                "desc":
                    "방향성이 뚜렷하지 않아 추세가 만들어지는지를 먼저 확인합니다."
            })

        result.append({
            "title": "리스크 재검토 기준",
            "desc":
                f"MA20 {fmt_price(ma20)}원 / "
                f"MA60 {fmt_price(ma60)}원 / "
                f"주요 지지선 {fmt_price(support)}원"
        })

    return result


# ============================================================
# CHART
# ============================================================

def create_price_chart(df, days=132):

    chart_df = df.tail(days).copy()

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.76, 0.24],
        vertical_spacing=0.025
    )

    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            increasing_line_width=1,
            decreasing_line_width=1,
            name="가격"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA20"],
            mode="lines",
            name="MA20",
            line=dict(width=1.7)
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA60"],
            mode="lines",
            name="MA60",
            line=dict(width=1.7)
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=chart_df.index,
            y=chart_df["Volume"],
            name="거래량",
            opacity=0.35
        ),
        row=2,
        col=1
    )

    fig.update_layout(
        height=430,
        margin=dict(
            l=5,
            r=5,
            t=8,
            b=5
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
            font=dict(size=10)
        ),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        dragmode=False
    )

    fig.update_xaxes(
        showgrid=False,
        fixedrange=True,
        rangeslider_visible=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#EEF1F5",
        fixedrange=True
    )

    fig.update_xaxes(
        row=2,
        col=1,
        showticklabels=True
    )

    return fig


# ============================================================
# DETAILED TECHNICAL CHART
# ============================================================

def create_detail_chart(df):

    chart_df = df.tail(132).copy()

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.55, 0.22, 0.23],
        vertical_spacing=0.035
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
            y=chart_df["BB_UPPER"],
            mode="lines",
            name="BB Upper",
            line=dict(width=1, dash="dot")
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["BB_LOWER"],
            mode="lines",
            name="BB Lower",
            line=dict(width=1, dash="dot")
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["RSI"],
            mode="lines",
            name="RSI",
            line=dict(width=1.7)
        ),
        row=2,
        col=1
    )

    fig.add_hline(
        y=70,
        line_dash="dot",
        row=2,
        col=1
    )

    fig.add_hline(
        y=30,
        line_dash="dot",
        row=2,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MACD"],
            mode="lines",
            name="MACD",
            line=dict(width=1.5)
        ),
        row=3,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MACD_SIGNAL"],
            mode="lines",
            name="Signal",
            line=dict(width=1.2)
        ),
        row=3,
        col=1
    )

    fig.update_layout(
        height=650,
        margin=dict(
            l=5,
            r=5,
            t=10,
            b=5
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        dragmode=False,
        showlegend=True
    )

    fig.update_xaxes(
        showgrid=False,
        fixedrange=True
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#EEF1F5",
        fixedrange=True
    )

    return fig


# ============================================================
# JUDGMENT CARD
# ============================================================

def render_judgment(judgment):

    color = judgment["color"]

    css_class = {
        "green": "judgment-green",
        "blue": "judgment-blue",
        "yellow": "judgment-yellow",
        "red": "judgment-red"
    }.get(color, "judgment-yellow")

    render_html(
        f"""
        <div class="judgment {css_class}">
            <div class="judgment-label">
                투자 방향
            </div>

            <div class="judgment-title">
                {esc(judgment["label"])}
            </div>

            <div style="
                font-size:17px;
                font-weight:800;
                margin-top:6px;
            ">
                {esc(judgment["title"])}
            </div>

            <div class="judgment-desc">
                {esc(judgment["description"])}
            </div>
        </div>
        """
    )


# ============================================================
# EVIDENCE CARD
# ============================================================

def render_evidence(df, judgment):

    row = df.iloc[-1]

    close = safe_float(row["Close"])
    ma20 = safe_float(row["MA20"])
    ma60 = safe_float(row["MA60"])
    rsi = safe_float(row["RSI"])
    ret20 = safe_float(row["RET_20"])
    vol = safe_float(row["VOL_RATIO"])

    trend, trend_color = get_trend_status(row)

    trend_pill = {
        "green": "pill-green",
        "yellow": "pill-yellow",
        "red": "pill-red",
        "gray": "pill-gray"
    }.get(trend_color, "pill-gray")

    render_html(
        f"""
        <div class="card">
            <div class="card-title">
                왜 이렇게 판단했나요?
            </div>

            <div style="margin-bottom:12px;">
                <span class="status-pill {trend_pill}">
                    {esc(trend)}
                </span>

                <span class="status-pill pill-blue">
                    전망 {esc(judgment["theme_outlook"])}
                </span>
            </div>

            <div class="evidence-grid">

                <div class="evidence-item">
                    <div class="evidence-label">
                        현재가
                    </div>
                    <div class="evidence-value">
                        {fmt_price(close)}원
                    </div>
                </div>

                <div class="evidence-item">
                    <div class="evidence-label">
                        20일 수익률
                    </div>
                    <div class="evidence-value">
                        {fmt_pct(ret20)}
                    </div>
                </div>

                <div class="evidence-item">
                    <div class="evidence-label">
                        MA20
                    </div>
                    <div class="evidence-value">
                        {fmt_price(ma20)}원
                    </div>
                    <div class="evidence-note">
                        단기 추세 기준
                    </div>
                </div>

                <div class="evidence-item">
                    <div class="evidence-label">
                        MA60
                    </div>
                    <div class="evidence-value">
                        {fmt_price(ma60)}원
                    </div>
                    <div class="evidence-note">
                        중기 추세 기준
                    </div>
                </div>

                <div class="evidence-item">
                    <div class="evidence-label">
                        RSI
                    </div>
                    <div class="evidence-value">
                        {f"{rsi:.1f}" if not pd.isna(rsi) else "-"}
                    </div>
                    <div class="evidence-note">
                        과열 여부
                    </div>
                </div>

                <div class="evidence-item">
                    <div class="evidence-label">
                        거래량
                    </div>
                    <div class="evidence-value">
                        {f"{vol:.2f}배" if not pd.isna(vol) else "-"}
                    </div>
                    <div class="evidence-note">
                        20일 평균 대비
                    </div>
                </div>

            </div>

            <div style="
                margin-top:13px;
                padding-top:12px;
                border-top:1px solid #EEF1F5;
                font-size:13px;
                line-height:1.55;
                color:#667085;
            ">
                <b style="color:#172033;">테마 관점</b><br>
                {esc(judgment["theme_note"])}
            </div>
        </div>
        """
    )


# ============================================================
# THEME CARD
# ============================================================

def render_theme_card(theme_name, info, df_map):

    stage_class = info["class"]

    etf_html = ""

    if info["etfs"]:

        for code in info["etfs"]:

            name = ETF_UNIVERSE.get(code, code)

            trend_text = ""

            if code in df_map and not df_map[code].empty:

                try:
                    row = df_map[code].iloc[-1]
                    trend, _ = get_trend_status(row)
                    trend_text = trend
                except Exception:
                    trend_text = ""

            etf_html += f"""
                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    padding:8px 0;
                    border-top:1px solid #EEF1F5;
                ">
                    <div>
                        <b style="font-size:13px;">
                            {esc(name)}
                        </b>
                        <div style="
                            font-size:10px;
                            color:#8A94A5;
                        ">
                            {esc(code)}
                        </div>
                    </div>

                    <div style="
                        font-size:11px;
                        color:#657083;
                    ">
                        {esc(trend_text)}
                    </div>
                </div>
            """

    else:

        etf_html = """
            <div style="
                margin-top:12px;
                padding:10px;
                border-radius:10px;
                background:#F7F9FC;
                font-size:12px;
                color:#7A8494;
            ">
                현재 등록된 전용 ETF가 없습니다.
                관련 ETF가 만들어지거나 편입 범위가 확인되면
                리서치 대상으로 추가할 수 있습니다.
            </div>
        """

    render_html(
        f"""
        <div class="theme-card">

            <div class="theme-header">

                <div class="theme-name">
                    {esc(theme_name)}
                </div>

                <div class="theme-stage {stage_class}">
                    {esc(info["label"])}
                </div>

            </div>

            <div class="theme-desc">
                {esc(info["description"])}
            </div>

            <div style="
                margin-top:14px;
                font-size:12px;
                font-weight:800;
                color:#172033;
            ">
                관련 ETF
            </div>

            <div style="margin-top:5px;">
                {etf_html}
            </div>

        </div>
        """
    )


# ============================================================
# APP HEADER
# ============================================================

render_html(
    """
    <div class="app-header">

        <div class="app-title">
            📊 ETF RADAR
        </div>

        <div class="app-subtitle">
            복잡한 차트보다 먼저 보는 ETF 투자 방향
        </div>

    </div>
    """
)


# ============================================================
# SESSION STATE
# ============================================================

if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()

if "selected_code" not in st.session_state:
    st.session_state.selected_code = st.session_state.watchlist[0]

if "chart_range" not in st.session_state:
    st.session_state.chart_range = "6M"


# ============================================================
# TABS
# ============================================================

tab_my, tab_theme = st.tabs(
    [
        "📌 내 ETF",
        "🚀 미래테마",
    ]
)


# ============================================================
# TAB 1
# ============================================================

with tab_my:

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    render_html(
        """
        <div class="card">
            <div class="card-title">
                내가 관심 있는 ETF
            </div>

            <div class="card-subtitle">
                ETF 이름이나 종목코드를 검색해 보세요.
            </div>
        </div>
        """
    )

    search = st.text_input(
        "ETF 검색",
        placeholder="예: AI반도체 / S&P500 / 395160",
        label_visibility="collapsed"
    )

    search = search.strip().lower()

    filtered = {}

    for code, name in ETF_UNIVERSE.items():

        if (
            search == ""
            or search in code.lower()
            or search in name.lower()
        ):
            filtered[code] = name

    if not filtered:

        st.warning(
            "현재 등록된 ETF 목록에서는 찾지 못했습니다."
        )

        st.stop()

    options = list(filtered.keys())

    current_code = st.session_state.selected_code

    if current_code not in options:
        current_code = options[0]

    selected = st.selectbox(
        "ETF 선택",
        options,
        index=options.index(current_code),
        format_func=lambda x:
            f"{ETF_UNIVERSE[x]}  ({x})"
    )

    st.session_state.selected_code = selected

    # --------------------------------------------------------
    # Watchlist buttons
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        if selected in st.session_state.watchlist:

            if st.button(
                "★ 관심 ETF에서 제거",
                use_container_width=True
            ):

                st.session_state.watchlist.remove(selected)

                if not st.session_state.watchlist:
                    st.session_state.watchlist = [selected]

                save_watchlist(st.session_state.watchlist)

                st.rerun()

        else:

            if st.button(
                "☆ 내 ETF에 추가",
                use_container_width=True
            ):

                st.session_state.watchlist.append(selected)

                save_watchlist(
                    st.session_state.watchlist
                )

                st.rerun()

    with col2:

        if st.button(
            "↻ 데이터 새로고침",
            use_container_width=True
        ):

            st.cache_data.clear()
            st.rerun()

    # --------------------------------------------------------
    # Watchlist
    # --------------------------------------------------------

    render_html(
        """
        <div class="card">

            <div class="card-title">
                내 ETF
            </div>

        """
        +
        "".join(
            [
                f"""
                <span class="status-pill pill-blue">
                    {esc(ETF_UNIVERSE.get(code, code))}
                </span>
                """
                for code in st.session_state.watchlist
            ]
        )
        +
        """
        </div>
        """
    )

    # --------------------------------------------------------
    # Data
    # --------------------------------------------------------

    with st.spinner("ETF 데이터를 불러오는 중입니다..."):

        df = load_etf_data(selected)

    if df.empty:

        st.error(
            "가격 데이터를 가져오지 못했습니다. "
            "잠시 후 다시 시도해 주세요."
        )

        st.stop()

    df = add_indicators(df)

    latest = df.iloc[-1]

    current_price = safe_float(latest["Close"])

    prev_close = (
        safe_float(df.iloc[-2]["Close"])
        if len(df) >= 2
        else np.nan
    )

    daily_change = (
        (current_price / prev_close - 1) * 100
        if not pd.isna(prev_close) and prev_close != 0
        else np.nan
    )

    # --------------------------------------------------------
    # Hero
    # --------------------------------------------------------

    change_class = (
        "#18864B"
        if daily_change >= 0
        else "#C53B3B"
    )

    render_html(
        f"""
        <div class="hero-card">

            <div class="hero-name">
                {esc(ETF_UNIVERSE[selected])}
            </div>

            <div class="hero-code">
                {esc(selected)}
            </div>

            <div class="hero-price">
                {fmt_price(current_price)}원
            </div>

            <div class="hero-change"
                 style="color:{change_class};">

                오늘
                {"+" if daily_change >= 0 else ""}
                {daily_change:.2f}%

            </div>

        </div>
        """
    )

    # --------------------------------------------------------
    # Judgment
    # --------------------------------------------------------

    judgment = build_judgment(
        df,
        selected
    )

    render_judgment(judgment)

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    render_evidence(
        df,
        judgment
    )

    # --------------------------------------------------------
    # Holding
    # --------------------------------------------------------

    render_html(
        """
        <div class="card">

            <div class="card-title">
                내 보유상태
            </div>

            <div class="card-subtitle">
                보유 여부와 평균단가를 입력하면
                현재 상황에 맞는 대응 기준을 보여드립니다.
            </div>

        </div>
        """
    )

    holding = st.radio(
        "보유 여부",
        [
            "미보유",
            "보유 중"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

    avg_price = None
    shares = None

    if holding == "보유 중":

        col1, col2 = st.columns(2)

        with col1:

            avg_price = st.number_input(
                "평균 매수가",
                min_value=0.0,
                value=0.0,
                step=100.0
            )

        with col2:

            shares = st.number_input(
                "보유 수량",
                min_value=0.0,
                value=0.0,
                step=1.0
            )

        if avg_price <= 0 or shares <= 0:

            st.info(
                "평균 매수가와 보유 수량을 입력하면 "
                "보유 전략을 계산합니다."
            )

            avg_price = None
            shares = None

    # --------------------------------------------------------
    # Position guide
    # --------------------------------------------------------

    guide = build_position_guide(
        df,
        judgment,
        avg_price,
        shares
    )

    render_html(
        """
        <div class="card">

            <div class="card-title">
                다음 행동을 어떻게 볼까?
            </div>

        """
        +
        "".join(
            [
                f"""
                <div class="guide-row">

                    <div class="guide-title">
                        {esc(item["title"])}
                    </div>

                    <div class="guide-desc">
                        {esc(item["desc"])}
                    </div>

                </div>
                """
                for item in guide
            ]
        )
        +
        """
        </div>
        """
    )

    # --------------------------------------------------------
    # Chart
    # --------------------------------------------------------

    render_html(
        """
        <div class="card">

            <div class="card-title">
                가격 흐름
            </div>

            <div class="card-subtitle">
                MA20과 MA60을 중심으로 추세만 간단히 확인합니다.
            </div>

        </div>
        """
    )

    range_col1, range_col2, range_col3, range_col4 = st.columns(4)

    range_options = [
        ("1M", 22),
        ("3M", 66),
        ("6M", 132),
        ("1Y", 264),
    ]

    for col, (label, days) in zip(
        [range_col1, range_col2, range_col3, range_col4],
        range_options
    ):

        with col:

            if st.button(
                label,
                use_container_width=True,
                key=f"range_{label}"
            ):

                st.session_state.chart_range = label

    range_days = {
        "1M": 22,
        "3M": 66,
        "6M": 132,
        "1Y": 264
    }

    days = range_days.get(
        st.session_state.chart_range,
        132
    )

    fig = create_price_chart(
        df,
        days
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "doubleClick": False,
            "responsive": True
        }
    )

    # --------------------------------------------------------
    # Detailed Technical Analysis
    # --------------------------------------------------------

    with st.expander(
        "🔎 상세 기술분석 보기"
    ):

        row = df.iloc[-1]

        support, resistance = calculate_levels(df)

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "RSI",
                (
                    f"{row['RSI']:.1f}"
                    if not pd.isna(row["RSI"])
                    else "-"
                )
            )

        with col2:

            st.metric(
                "거래량 / 20일",
                (
                    f"{row['VOL_RATIO']:.2f}배"
                    if not pd.isna(row["VOL_RATIO"])
                    else "-"
                )
            )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "MACD",
                (
                    f"{row['MACD']:.2f}"
                    if not pd.isna(row["MACD"])
                    else "-"
                )
            )

        with col2:

            st.metric(
                "MACD Signal",
                (
                    f"{row['MACD_SIGNAL']:.2f}"
                    if not pd.isna(row["MACD_SIGNAL"])
                    else "-"
                )
            )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "주요 지지선",
                (
                    f"{support:,.0f}원"
                    if not pd.isna(support)
                    else "-"
                )
            )

        with col2:

            st.metric(
                "주요 저항선",
                (
                    f"{resistance:,.0f}원"
                    if not pd.isna(resistance)
                    else "-"
                )
            )

        st.plotly_chart(
            create_detail_chart(df),
            use_container_width=True,
            config={
                "displayModeBar": False,
                "scrollZoom": False,
                "doubleClick": False,
                "responsive": True
            }
        )

        st.markdown(
            """
            **지표 해석**

            - RSI 70 이상: 단기 과열 가능성
            - RSI 30 이하: 단기 과매도 가능성
            - MA20 > MA60: 중기 상승 구조
            - MACD > Signal: 단기 모멘텀 개선
            - 거래량 증가: 가격 움직임의 신뢰도 확인에 활용
            - 지지선 이탈: 추세 재검토 필요
            """,
        )

    # --------------------------------------------------------
    # Next thing to watch
    # --------------------------------------------------------

    render_html(
        f"""
        <div class="card">

            <div class="card-title">
                👀 다음에 볼 것
            </div>

            <div style="
                font-size:14px;
                line-height:1.65;
                color:#5F6B7A;
            ">

                <b style="color:#172033;">
                    ① 가격
                </b>
                — MA20 위에서 추세가 유지되는지 확인<br>

                <b style="color:#172033;">
                    ② 거래량
                </b>
                — 상승 또는 반등 시 거래량이 따라오는지 확인<br>

                <b style="color:#172033;">
                    ③ 모멘텀
                </b>
                — RSI 과열과 MACD 약화를 함께 확인<br>

                <b style="color:#172033;">
                    ④ 테마
                </b>
                — 관련 산업의 관심이 다음 단계로 확산되는지 확인

            </div>

        </div>
        """
    )


# ============================================================
# TAB 2 : FUTURE THEMES
# ============================================================

with tab_theme:

    render_html(
        """
        <div class="card">

            <div class="card-title">
                🚀 미래테마
            </div>

            <div style="
                font-size:14px;
                line-height:1.55;
                color:#687386;
            ">
                현재 강한 테마만 보는 것이 아니라
                <b style="color:#172033;">
                다음에 자금이 이동할 가능성이 있는 산업
                </b>
                을 단계별로 관찰합니다.
            </div>

        </div>
        """
    )

    # --------------------------------------------------------
    # Theme chain
    # --------------------------------------------------------

    render_html(
        """
        <div class="card">

            <div class="card-title">
                테마 순환 구조
            </div>

            <div class="card-subtitle">
                아래 방향은 확정된 미래 예측이 아니라
                ETF 리서치를 위한 시나리오 구조입니다.
            </div>

            <div class="theme-chain">
        """
        +
        "".join(
            [
                f"""
                <div class="chain-item">

                    <div class="chain-title">
                        {esc(name)}
                    </div>

                    <div class="chain-stage">
                        {esc(stage)}
                    </div>

                </div>

                <div class="chain-arrow">
                    →
                </div>
                """
                for name, stage in THEME_CHAIN
            ]
        ).rstrip(
            '<div class="chain-arrow">\n                    →\n                </div>'
        )
        +
        """
            </div>

        </div>
        """
    )

    # --------------------------------------------------------
    # Research update
    # --------------------------------------------------------

    col1, col2 = st.columns([1.2, 1])

    with col1:

        if st.button(
            "🔄 테마 리서치 업데이트",
            use_container_width=True
        ):

            st.session_state.theme_updated = (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                )
            )

            st.cache_data.clear()

            st.rerun()

    with col2:

        updated = st.session_state.get(
            "theme_updated",
            "앱 기본 데이터"
        )

        st.caption(
            f"최근 업데이트: {updated}"
        )

    # --------------------------------------------------------
    # Load theme data
    # --------------------------------------------------------

    theme_df_map = {}

    # Keep this deliberately light:
    # only ETFs connected to the themes are loaded.

    theme_codes = set()

    for info in THEMES.values():

        for code in info["etfs"]:
            theme_codes.add(code)

    # Load only current theme ETF data
    # to avoid making the page unnecessarily heavy.

    for code in list(theme_codes):

        try:

            temp = load_etf_data(code)

            if not temp.empty:

                theme_df_map[code] = add_indicators(temp)

        except Exception:
            pass

    # --------------------------------------------------------
    # Theme sections
    # --------------------------------------------------------

    render_html(
        """
        <div style="
            font-size:20px;
            font-weight:850;
            margin:18px 0 12px 2px;
        ">
            테마별 현재 위치
        </div>
        """
    )

    for theme_name, info in THEMES.items():

        render_theme_card(
            theme_name,
            info,
            theme_df_map
        )

    # --------------------------------------------------------
    # Early candidate / rough stone
    # --------------------------------------------------------

    render_html(
        """
        <div style="
            font-size:20px;
            font-weight:850;
            margin:22px 0 12px 2px;
        ">
            💎 원석 후보
        </div>

        <div class="card">

            <div class="card-title">
                아직 주도주가 아닌 후보를 찾는 방법
            </div>

            <div style="
                font-size:13px;
                color:#687386;
                line-height:1.65;
            ">
                원석은 단순히 많이 오른 ETF를 뜻하지 않습니다.
                <br><br>

                <b style="color:#172033;">
                ① 테마 관심 증가
                </b><br>
                아직 가격에 충분히 반영되지 않았는지 확인합니다.
                <br><br>

                <b style="color:#172033;">
                ② 장기 추세 전환
                </b><br>
                MA60 부근에서 상승 구조가 만들어지는지를 봅니다.
                <br><br>

                <b style="color:#172033;">
                ③ 거래량 변화
                </b><br>
                평소보다 관심이 증가하는지를 확인합니다.
                <br><br>

                <b style="color:#172033;">
                ④ 후속 테마
                </b><br>
                이미 급등한 주도 테마보다 한 단계 뒤의 산업을 찾습니다.
            </div>

        </div>
        """
    )

    # --------------------------------------------------------
    # Automatic early candidate scan
    # --------------------------------------------------------

    candidates = []

    for theme_name, info in THEMES.items():

        if info["stage"] not in ["EARLY", "FOLLOWER"]:
            continue

        for code in info["etfs"]:

            if code not in theme_df_map:
                continue

            temp = theme_df_map[code]

            if len(temp) < 65:
                continue

            row = temp.iloc[-1]

            close = safe_float(row["Close"])
            ma20 = safe_float(row["MA20"])
            ma60 = safe_float(row["MA60"])
            rsi = safe_float(row["RSI"])
            vol = safe_float(row["VOL_RATIO"])
            ret20 = safe_float(row["RET_20"])

            if any(
                pd.isna(x)
                for x in [
                    close,
                    ma20,
                    ma60,
                    rsi
                ]
            ):
                continue

            early_score = 0

            if close > ma60:
                early_score += 1

            if ma20 >= ma60:
                early_score += 1

            if 45 <= rsi <= 65:
                early_score += 1

            if not pd.isna(vol) and vol >= 1.1:
                early_score += 1

            if not pd.isna(ret20) and 0 <= ret20 <= 12:
                early_score += 1

            if early_score >= 3:

                candidates.append({
                    "theme": theme_name,
                    "code": code,
                    "name": ETF_UNIVERSE.get(
                        code,
                        code
                    ),
                    "score": early_score,
                    "ret20": ret20,
                    "rsi": rsi,
                })

    candidates = sorted(
        candidates,
        key=lambda x: (
            x["score"],
            x["ret20"]
        ),
        reverse=True
    )

    if candidates:

        for item in candidates[:6]:

            render_html(
                f"""
                <div class="theme-card">

                    <div style="
                        font-size:11px;
                        color:#8A94A5;
                        font-weight:700;
                    ">
                        {esc(item["theme"])}
                    </div>

                    <div style="
                        font-size:17px;
                        font-weight:850;
                        margin-top:4px;
                    ">
                        💎 {esc(item["name"])}
                    </div>

                    <div style="
                        font-size:11px;
                        color:#8A94A5;
                        margin-top:2px;
                    ">
                        {esc(item["code"])}
                    </div>

                    <div style="
                        display:grid;
                        grid-template-columns:
                        repeat(3,1fr);
                        gap:7px;
                        margin-top:12px;
                    ">

                        <div class="evidence-item">
                            <div class="evidence-label">
                                초기 신호
                            </div>
                            <div class="evidence-value">
                                {item["score"]}/5
                            </div>
                        </div>

                        <div class="evidence-item">
                            <div class="evidence-label">
                                20일
                            </div>
                            <div class="evidence-value">
                                {fmt_pct(item["ret20"])}
                            </div>
                        </div>

                        <div class="evidence-item">
                            <div class="evidence-label">
                                RSI
                            </div>
                            <div class="evidence-value">
                                {item["rsi"]:.1f}
                            </div>
                        </div>

                    </div>

                    <div style="
                        margin-top:11px;
                        font-size:12px;
                        color:#687386;
                        line-height:1.5;
                    ">
                        아직 급등 여부만으로 판단하지 않고
                        추세·거래량·RSI가 함께 개선되는지를
                        관찰하는 후보입니다.
                    </div>

                </div>
                """
            )

    else:

        st.info(
            "현재 데이터에서는 뚜렷한 원석 후보가 발견되지 않았습니다. "
            "시장 변화에 따라 후보가 달라집니다."
        )

    # --------------------------------------------------------
    # Theme principle
    # --------------------------------------------------------

    render_html(
        """
        <div class="card">

            <div class="card-title">
                💡 ETF RADAR의 테마 관점
            </div>

            <div style="
                font-size:13px;
                color:#687386;
                line-height:1.65;
            ">

                <b style="color:#172033;">
                주도 테마
                </b>
                를 무조건 따라가는 것이 아니라,
                <br>

                <b style="color:#172033;">
                주도 → 후속 수혜 → 선행 관심
                </b>
                순서로 관찰합니다.

                <br><br>

                예를 들어 AI 반도체가 강해질 경우
                데이터센터 → 전력 인프라 → 냉각/열관리처럼
                실제 투자 증가에 따라 관련 산업이 확산되는지를
                확인하는 방식입니다.

                <br><br>

                이 화면의 '원석'은 미래 상승을 보장하는 종목이 아니라
                <b style="color:#172033;">
                다음 사이클을 관찰하기 위한 후보
                </b>
                입니다.

            </div>

        </div>
        """
    )


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="disclaimer">

        ETF RADAR의 판단은 가격·추세·거래량 등의
        정량 데이터를 바탕으로 만든 참고용 시나리오입니다.
        <br>
        미래 수익이나 가격 방향을 보장하지 않습니다.

    </div>
    """
)