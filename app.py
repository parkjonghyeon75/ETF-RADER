import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
import json
import warnings

warnings.filterwarnings("ignore")


# ============================================================
# ETF RADAR
# Premium Mobile ETF Technical Analysis Dashboard
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

st.markdown("""
<style>

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
        linear-gradient(
            180deg,
            #f5f7fb 0%,
            #eef2f7 100%
        );
}

.block-container {
    max-width: 760px;
    padding-top: 1rem;
    padding-bottom: 5rem;
}

/* ---------- HEADER ---------- */

.hero {
    background:
        linear-gradient(
            135deg,
            #101828 0%,
            #172554 55%,
            #1e3a8a 100%
        );
    border-radius: 24px;
    padding: 24px 22px;
    color: white;
    margin-bottom: 16px;
    box-shadow: 0 12px 30px rgba(15,23,42,.18);
}

.hero-title {
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -1.2px;
}

.hero-sub {
    margin-top: 5px;
    color: #cbd5e1;
    font-size: 13px;
}

.section-title {
    font-size: 19px;
    font-weight: 800;
    color: #0f172a;
    margin: 20px 2px 10px 2px;
    letter-spacing: -0.5px;
}

/* ---------- CARDS ---------- */

.card {
    background: rgba(255,255,255,.96);
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    padding: 18px;
    margin: 10px 0;
    box-shadow: 0 5px 18px rgba(15,23,42,.06);
}

.card-title {
    font-size: 14px;
    color: #64748b;
    font-weight: 700;
}

.big-number {
    font-size: 28px;
    font-weight: 850;
    color: #0f172a;
    letter-spacing: -1px;
}

.small-muted {
    color: #64748b;
    font-size: 12px;
}

.metric-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.metric {
    background: #f8fafc;
    border-radius: 15px;
    padding: 13px;
    border: 1px solid #edf0f4;
}

.metric-label {
    font-size: 11px;
    color: #64748b;
    margin-bottom: 5px;
}

.metric-value {
    font-size: 18px;
    font-weight: 800;
    color: #111827;
}

/* ---------- SIGNAL ---------- */

.signal {
    border-radius: 18px;
    padding: 17px;
    margin: 10px 0;
}

.signal-title {
    font-size: 17px;
    font-weight: 850;
    margin-bottom: 6px;
}

.signal-text {
    font-size: 13px;
    line-height: 1.65;
}

.signal-buy {
    background: #ecfdf5;
    border: 1px solid #bbf7d0;
}

.signal-watch {
    background: #fffbeb;
    border: 1px solid #fde68a;
}

.signal-risk {
    background: #fff1f2;
    border: 1px solid #fecdd3;
}

.signal-neutral {
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
}

/* ---------- SCORE ---------- */

.score-wrap {
    text-align: center;
    padding: 8px 0 14px;
}

.score-number {
    font-size: 48px;
    font-weight: 900;
    color: #0f172a;
    line-height: 1;
}

.score-label {
    font-size: 12px;
    color: #64748b;
    margin-top: 6px;
}

/* ---------- BADGE ---------- */

.badge {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 800;
    margin: 3px;
}

.badge-blue {
    background: #dbeafe;
    color: #1d4ed8;
}

.badge-green {
    background: #dcfce7;
    color: #15803d;
}

.badge-yellow {
    background: #fef3c7;
    color: #a16207;
}

.badge-red {
    background: #fee2e2;
    color: #b91c1c;
}

.badge-gray {
    background: #e2e8f0;
    color: #475569;
}

/* ---------- TABLE ---------- */

.data-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 13px;
}

.data-row:last-child {
    border-bottom: none;
}

.data-label {
    color: #64748b;
}

.data-value {
    color: #0f172a;
    font-weight: 750;
}

/* ---------- WARNING ---------- */

.notice {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: 15px;
    padding: 13px;
    font-size: 12px;
    line-height: 1.6;
    color: #9a3412;
}

/* ---------- MOBILE ---------- */

@media (max-width: 600px) {

    .block-container {
        padding-left: 12px;
        padding-right: 12px;
    }

    .hero {
        padding: 20px 17px;
        border-radius: 20px;
    }

    .hero-title {
        font-size: 26px;
    }

    .big-number {
        font-size: 25px;
    }

}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e5e7eb;
    padding: 12px;
    border-radius: 15px;
}

button[kind="primary"] {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# ETF DATABASE
# ============================================================

ETF_POOL = {

    "미국 대표지수": {
        "360750": "TIGER 미국S&P500",
        "379800": "KODEX 미국S&P500TR",
        "448290": "SOL 미국S&P500",
        "133690": "TIGER 미국나스닥100",
        "379810": "KODEX 미국나스닥100TR",
    },

    "AI / 반도체": {
        "487240": "KODEX 미국AI테크TOP10",
        "452330": "TIGER 미국테크TOP10",
        "395160": "KODEX AI반도체TOP2플러스",
        "462100": "TIGER AI반도체핵심공정",
        "441680": "SOL 미국AI반도체",
        "486410": "TIGER 미국반도체TOP10",
    },

    "전력 / 원자력": {
        "471990": "KODEX AI전력핵심설비",
        "445380": "SOL 원자력TOP3플러스",
        "465560": "TIGER 글로벌원자력",
    },

    "2차전지": {
        "305540": "KODEX 2차전지산업",
        "364980": "TIGER 2차전지소부장",
        "438320": "KODEX 2차전지핵심소재",
    },

    "로봇 / 우주": {
        "465610": "KODEX 로봇산업",
        "476250": "TIGER 우주항공&로봇",
    },

    "헬스케어 / 바이오": {
        "329200": "TIGER 헬스케어",
        "266420": "KODEX 바이오",
        "462610": "ARIRANG 3대주주바이오",
    },

    "배당": {
        "458730": "TIGER 미국배당다우존스",
        "441680": "SOL 미국배당 다우존스",
        "476480": "KODEX 미국배당커버드콜",
        "451780": "TIGER 미국배당+7%프리미엄",
    },

    "채권 / 금리": {
        "423160": "KODEX CD금리활성(합성)",
        "449170": "TIGER KOFR금리액티브",
        "308620": "KODEX 미국채울트라30년선물",
        "365780": "TIGER 미국채30년스트립액티브",
    },
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
# NAVE STOCK DATA
# ============================================================

def fetch_from_naver(code, count=500):

    url = (
        "https://fchart.stock.naver.com/sise.nhn?"
        f"symbol={code}&timeframe=day&count={count}&requestType=0"
    )

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        xml_data = urllib.request.urlopen(
            req,
            timeout=10
        ).read()

        root = ET.fromstring(xml_data)

        rows = []

        for item in root.iter("item"):

            data = item.attrib.get("data", "")

            if not data:
                continue

            parts = data.split("|")

            if len(parts) < 7:
                continue

            rows.append(parts)

        if not rows:
            return None

        df = pd.DataFrame(
            rows,
            columns=[
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "Foreign"
            ]
        )

        df["Date"] = pd.to_datetime(df["Date"])

        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        df = df.dropna()

        df = df.sort_values("Date")
        df = df.set_index("Date")

        return df

    except Exception:
        return None


# ============================================================
# YFINANCE FALLBACK
# ============================================================

def fetch_from_yfinance(code, period="2y"):

    candidates = [
        f"{code}.KS",
        f"{code}.KQ",
    ]

    for ticker in candidates:

        try:

            data = yf.download(
                ticker,
                period=period,
                interval="1d",
                auto_adjust=False,
                progress=False
            )

            if data is None or data.empty:
                continue

            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            rename_map = {
                "Open": "Open",
                "High": "High",
                "Low": "Low",
                "Close": "Close",
                "Volume": "Volume",
            }

            data = data.rename(columns=rename_map)

            needed = [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume"
            ]

            data = data[needed].copy()

            return data.dropna()

        except Exception:
            pass

    return None


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(ttl=300)
def load_etf_data(code):

    df = fetch_from_naver(code, 500)

    if df is not None and len(df) > 50:
        return df

    return fetch_from_yfinance(code)


# ============================================================
# INDICATORS
# ============================================================

def calculate_indicators(df):

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

    ema12 = close.ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = close.ewm(
        span=26,
        adjust=False
    ).mean()

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

    df["BB_STD"] = close.rolling(20).std()

    df["BB_UPPER"] = (
        df["BB_MID"] +
        2 * df["BB_STD"]
    )

    df["BB_LOWER"] = (
        df["BB_MID"] -
        2 * df["BB_STD"]
    )

    df["VOL_MA20"] = df["Volume"].rolling(20).mean()

    df["VOL_RATIO"] = (
        df["Volume"] /
        df["VOL_MA20"]
    )

    df["RETURN_1D"] = close.pct_change()

    df["RETURN_5D"] = close.pct_change(5)

    df["RETURN_20D"] = close.pct_change(20)

    return df


# ============================================================
# SUPPORT / RESISTANCE
# ============================================================

def calculate_support_resistance(df):

    recent = df.tail(120)

    current = float(df["Close"].iloc[-1])

    lows = []

    highs = []

    for value in [
        df["MA20"].iloc[-1],
        df["MA60"].iloc[-1],
        df["MA120"].iloc[-1],
        recent["Low"].min(),
    ]:

        if pd.notna(value) and value < current:
            lows.append(float(value))

    for value in [
        recent["High"].max(),
        df["BB_UPPER"].iloc[-1],
    ]:

        if pd.notna(value) and value > current:
            highs.append(float(value))

    support = max(lows) if lows else current * 0.95

    resistance = min(highs) if highs else current * 1.05

    return support, resistance


# ============================================================
# VOLUME PROFILE
# ============================================================

def volume_profile(df, bins=20):

    data = df.tail(120).copy()

    low = float(data["Low"].min())
    high = float(data["High"].max())

    if high <= low:
        return pd.DataFrame()

    data["PriceBin"] = pd.cut(
        data["Close"],
        bins=bins
    )

    profile = (
        data
        .groupby("PriceBin", observed=False)["Volume"]
        .sum()
        .reset_index()
    )

    profile["Price"] = profile["PriceBin"].apply(
        lambda x: x.mid if pd.notna(x) else np.nan
    )

    return profile.dropna()


# ============================================================
# TECHNICAL SCORE
# ============================================================

def technical_score(df):

    row = df.iloc[-1]

    score = 0

    if row["Close"] > row["MA20"]:
        score += 15

    if row["MA20"] > row["MA60"]:
        score += 10

    if 50 <= row["RSI"] <= 70:
        score += 20

    elif 40 <= row["RSI"] < 50:
        score += 12

    elif row["RSI"] > 70:
        score += 7

    else:
        score += 5

    if (
        row["MACD"] > row["MACD_SIGNAL"]
        and row["MACD_HIST"] > 0
    ):
        score += 20

    elif row["MACD"] > row["MACD_SIGNAL"]:
        score += 15

    else:
        score += 5

    if (
        row["VOL_RATIO"] >= 1.2
        and row["RETURN_1D"] > 0
    ):
        score += 15

    score += 20

    return int(np.clip(score, 0, 100))


# ============================================================
# PATTERN
# ============================================================

def detect_pattern(df):

    row = df.iloc[-1]

    close = row["Close"]
    ma20 = row["MA20"]
    ma60 = row["MA60"]
    rsi = row["RSI"]
    vol = row["VOL_RATIO"]

    previous_high = (
        df["High"]
        .rolling(20)
        .max()
        .shift(1)
        .iloc[-1]
    )

    if (
        close > previous_high
        and vol >= 1.3
        and row["MACD"] > row["MACD_SIGNAL"]
    ):
        return "돌파"

    if (
        abs(close - ma20) / ma20 < 0.025
        and ma20 > ma60
        and 42 <= rsi <= 65
    ):
        return "눌림목"

    if rsi >= 70:
        return "과열"

    if (
        close < ma20
        and row["MACD"] < row["MACD_SIGNAL"]
    ):
        return "추세 약화"

    if (
        close > ma20
        and ma20 > ma60
    ):
        return "상승 추세"

    return "횡보"


# ============================================================
# ACTION GUIDE
# ============================================================

def action_guide(
    df,
    support,
    resistance
):

    row = df.iloc[-1]

    price = float(row["Close"])

    rsi = float(row["RSI"])

    score = technical_score(df)

    pattern = detect_pattern(df)

    distance_support = (
        price - support
    ) / price

    distance_resistance = (
        resistance - price
    ) / price

    if pattern == "돌파":

        return {
            "type": "watch",
            "title": "돌파 확인 구간",
            "text":
                "20일 고점 돌파와 거래량 증가가 동시에 나타난 구간입니다. "
                "다만 돌파 직후 급등했다면 추격매수보다 돌파가격 지지 여부를 확인하는 접근이 유리합니다."
        }

    if pattern == "눌림목":

        return {
            "type": "buy",
            "title": "눌림목 관심 구간",
            "text":
                "중기 이동평균선 위에서 조정을 받고 있어 눌림목 후보입니다. "
                "지지선 부근에서 거래량이 감소하고 다시 반등하는지 확인하는 것이 핵심입니다."
        }

    if pattern == "과열":

        return {
            "type": "risk",
            "title": "추격매수 주의",
            "text":
                "RSI가 과열권에 진입했습니다. "
                "현재 가격을 추격하기보다 조정 후 지지 확인 여부를 보는 구간입니다."
        }

    if pattern == "추세 약화":

        return {
            "type": "risk",
            "title": "추세 약화",
            "text":
                "현재가가 20일선 아래이고 MACD도 약화되어 있습니다. "
                "신규 진입은 추세 회복 여부를 확인한 뒤 판단하는 것이 좋습니다."
        }

    if score >= 70:

        return {
            "type": "watch",
            "title": "상승 모멘텀 유지",
            "text":
                "기술적 점수가 높은 편입니다. "
                "다만 저항선과의 거리가 짧다면 한 번에 진입하기보다 분할 접근을 고려할 수 있습니다."
        }

    return {
        "type": "neutral",
        "title": "관망 / 확인 구간",
        "text":
            "현재 지표가 뚜렷한 매수 신호를 만들지 못하고 있습니다. "
            "지지선 반등 또는 거래량을 동반한 저항 돌파를 확인하는 것이 중요합니다."
    }


# ============================================================
# HOLDING GUIDE
# ============================================================

def holding_guide(
    df,
    avg_price,
    quantity,
    support,
    resistance
):

    row = df.iloc[-1]

    price = float(row["Close"])

    rsi = float(row["RSI"])

    score = technical_score(df)

    pattern = detect_pattern(df)

    profit_rate = (
        (price - avg_price)
        / avg_price
        * 100
    )

    # --------------------------------------------------------
    # 수익권
    # --------------------------------------------------------

    if profit_rate >= 15:

        if rsi >= 70:

            return {
                "type": "risk",
                "title": "수익보존 우선",
                "action": "일부 이익실현 검토",
                "text":
                    "현재 수익률이 높은 상태에서 RSI까지 과열권입니다. "
                    "전량매도보다는 일부 이익실현 후 나머지는 추세를 따라가는 방식이 가능한 구간입니다.",
                "extra":
                    "20일선 또는 직전 돌파가격을 이탈하면 잔여물량의 리스크 관리가 필요합니다."
            }

        return {
            "type": "buy",
            "title": "수익 추세 보유 구간",
            "action": "보유 유지 + 추세 확인",
            "text":
                "수익권이면서 기술적 추세가 유지되고 있습니다. "
                "상승 추세가 유지되는 동안 성급하게 전량매도하기보다는 주요 지지선 이탈 여부를 확인하는 전략을 고려할 수 있습니다.",
            "extra":
                f"주요 관리선: {support:,.0f}원"
        }

    # --------------------------------------------------------
    # 소폭 수익
    # --------------------------------------------------------

    if 0 <= profit_rate < 15:

        if pattern in ["상승 추세", "눌림목"]:

            return {
                "type": "buy",
                "title": "보유 유지 / 추가매수는 조건부",
                "action": "기본 보유 + 눌림 시 분할매수",
                "text":
                    "현재 보유 포지션은 추세가 유지되는 한 보유를 우선적으로 검토할 수 있습니다. "
                    "추가매수는 현재가를 추격하기보다 지지선 부근에서 분할 접근하는 방식이 적합합니다.",
                "extra":
                    f"1차 관심가격: {support:,.0f}원"
            }

        return {
            "type": "watch",
            "title": "보유 유지 / 신규 추가는 신중",
            "action": "보유 + 추세 확인",
            "text":
                "현재 손익은 플러스지만 기술적 신호가 강하지 않습니다. "
                "추가매수보다 현재 보유분의 추세 유지 여부를 확인하는 것이 중요합니다.",
            "extra":
                f"저항: {resistance:,.0f}원"
        }

    # --------------------------------------------------------
    # 소폭 손실
    # --------------------------------------------------------

    if -8 <= profit_rate < 0:

        if (
            price > support
            and row["MACD"] >= row["MACD_SIGNAL"]
        ):

            return {
                "type": "watch",
                "title": "손실 회복 대기 구간",
                "action": "보유 유지 / 추가매수는 분할",
                "text":
                    "평균매수가 아래에 있지만 주요 지지선 위에서 기술적 회복 신호가 나타나는지 확인할 수 있습니다. "
                    "추가매수는 한 번에 하지 않고 지지 확인 후 분할 접근하는 방식이 가능합니다.",
                "extra":
                    f"손익분기점: {avg_price:,.0f}원"
            }

        return {
            "type": "risk",
            "title": "리스크 관리 필요",
            "action": "추가매수 보류",
            "text":
                "현재 가격이 주요 지지선과 가까워지고 있습니다. "
                "지지선이 무너지는 경우 손실 확대를 막기 위한 대응 기준을 미리 정해두는 것이 중요합니다.",
            "extra":
                f"주요 지지: {support:,.0f}원"
        }

    # --------------------------------------------------------
    # 손실 -8% 이하
    # --------------------------------------------------------

    if profit_rate < -8:

        return {
            "type": "risk",
            "title": "손실관리 우선",
            "action": "추가매수보다 추세 회복 확인",
            "text":
                "평균매수가 대비 손실폭이 커진 상태입니다. "
                "단순히 평균단가를 낮추기 위한 추가매수보다는 추세 회복 여부를 먼저 확인하는 것이 중요합니다.",
            "extra":
                f"현재가: {price:,.0f}원 / 평균가: {avg_price:,.0f}원"
        }

    return {
        "type": "neutral",
        "title": "보유 유지 여부 점검",
        "action": "지표 재확인",
        "text":
            "현재 포지션은 가격과 기술지표를 함께 확인하면서 대응하는 구간입니다.",
        "extra": ""
    }


# ============================================================
# NEW BUY GUIDE
# ============================================================

def new_buy_guide(
    df,
    support,
    resistance
):

    row = df.iloc[-1]

    price = float(row["Close"])
    rsi = float(row["RSI"])
    score = technical_score(df)
    pattern = detect_pattern(df)

    ma20 = float(row["MA20"])

    # 추격 위험
    if pattern == "과열":

        return {
            "type": "risk",
            "title": "현재 추격매수 주의",
            "action": "신규매수보다 조정 대기",
            "text":
                "RSI 과열권으로 현재 가격을 바로 추격하는 것보다 "
                "20일선 또는 최근 돌파가격 부근까지 조정이 발생하는지 확인하는 것이 좋습니다.",
            "buy1": support,
            "buy2": ma20
        }

    # 돌파
    if pattern == "돌파":

        return {
            "type": "watch",
            "title": "돌파 매매 관심",
            "action": "돌파 유지 확인 후 분할 접근",
            "text":
                "저항을 거래량과 함께 돌파한 상태입니다. "
                "돌파 가격을 다시 이탈하지 않는지 확인한 뒤 분할 접근하는 시나리오를 고려할 수 있습니다.",
            "buy1": price * 0.985,
            "buy2": support
        }

    # 눌림목
    if pattern == "눌림목":

        return {
            "type": "buy",
            "title": "눌림목 매수 관심",
            "action": "지지 확인 후 분할매수",
            "text":
                "20일선 주변에서 눌림목 형태가 나타나고 있습니다. "
                "지지선에서 반등이 확인될 경우 분할매수를 고려할 수 있는 구간입니다.",
            "buy1": support,
            "buy2": ma20
        }

    # 상승추세
    if (
        score >= 70
        and price > ma20
        and rsi < 70
    ):

        return {
            "type": "watch",
            "title": "상승 추세 유지",
            "action": "조정 시 분할매수",
            "text":
                "상승 추세와 기술적 모멘텀이 유지되고 있습니다. "
                "현재가 일괄매수보다는 20일선과 지지선 부근의 조정을 활용하는 접근이 가능합니다.",
            "buy1": ma20,
            "buy2": support
        }

    return {
        "type": "neutral",
        "title": "지금은 확인 우선",
        "action": "관망 후 조건 충족 시 진입",
        "text":
            "현재 지표가 뚜렷한 신규매수 신호를 만들지 못하고 있습니다. "
            "지지선 반등 또는 저항 돌파가 확인될 때까지 기다리는 시나리오가 가능합니다.",
        "buy1": support,
        "buy2": ma20
    }


# ============================================================
# CHART
# ============================================================

def make_chart(df, support, resistance):

    data = df.tail(150).copy()

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.035,
        row_heights=[0.58, 0.20, 0.22]
    )

    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="가격"
        ),
        row=1,
        col=1
    )

    for ma, name in [
        ("MA20", "MA20"),
        ("MA60", "MA60"),
        ("MA120", "MA120")
    ]:

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data[ma],
                name=name,
                mode="lines",
                line=dict(width=1.5)
            ),
            row=1,
            col=1
        )

    fig.add_hline(
        y=support,
        line_dash="dot",
        annotation_text=f"지지 {support:,.0f}",
        row=1,
        col=1
    )

    fig.add_hline(
        y=resistance,
        line_dash="dot",
        annotation_text=f"저항 {resistance:,.0f}",
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data["Volume"],
            name="거래량",
            opacity=.45
        ),
        row=2,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["RSI"],
            name="RSI",
            mode="lines"
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
        height=720,
        margin=dict(
            l=10,
            r=10,
            t=25,
            b=10
        ),
        template="plotly_white",
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0
        )
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#eef2f7"
    )

    return fig


# ============================================================
# FORMAT
# ============================================================

def money(v):

    if pd.isna(v):
        return "-"

    return f"{v:,.0f}"


def pct(v):

    if pd.isna(v):
        return "-"

    return f"{v:+.2f}%"


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">
    <div class="hero-title">📊 ETF RADAR</div>
    <div class="hero-sub">
        기술적 분석 · 보유전략 · 신규진입 시나리오
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# ETF SELECT
# ============================================================

all_etfs = {}

for theme, items in ETF_POOL.items():
    for code, name in items.items():
        all_etfs[code] = name

selected_code = st.selectbox(
    "분석할 ETF",
    options=list(all_etfs.keys()),
    format_func=lambda x: f"{all_etfs[x]}  ·  {x}"
)

selected_name = all_etfs[selected_code]


# ============================================================
# LOAD
# ============================================================

with st.spinner("시장 데이터를 불러오는 중입니다..."):

    df = load_etf_data(selected_code)

if df is None or len(df) < 60:

    st.error(
        "시장 데이터를 불러오지 못했습니다. "
        "잠시 후 다시 시도해주세요."
    )

    st.stop()


df = calculate_indicators(df)

df = df.dropna(
    subset=[
        "MA20",
        "MA60",
        "RSI",
        "MACD"
    ]
)

row = df.iloc[-1]

current_price = float(row["Close"])

previous_price = float(df["Close"].iloc[-2])

daily_change = (
    current_price -
    previous_price
) / previous_price * 100

support, resistance = calculate_support_resistance(df)

score = technical_score(df)

pattern = detect_pattern(df)

guide = action_guide(
    df,
    support,
    resistance
)


# ============================================================
# BASIC INFO
# ============================================================

st.markdown(
    f"""
<div class="card">

<div class="card-title">
    {selected_name}
</div>

<div class="big-number">
    {money(current_price)}원
</div>

<div style="margin-top:5px;">
    <span class="badge {'badge-green' if daily_change >= 0 else 'badge-red'}">
        {pct(daily_change)}
    </span>

    <span class="badge badge-blue">
        {pattern}
    </span>

    <span class="badge badge-gray">
        기술점수 {score}/100
    </span>
</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# METRICS
# ============================================================

st.markdown(
    '<div class="section-title">시장 상태</div>',
    unsafe_allow_html=True
)

c1, c2 = st.columns(2)

with c1:
    st.metric(
        "RSI",
        f"{row['RSI']:.1f}"
    )

with c2:
    st.metric(
        "거래량",
        f"{row['VOL_RATIO']:.2f}배"
    )

c3, c4 = st.columns(2)

with c3:
    st.metric(
        "MA20",
        money(row["MA20"])
    )

with c4:
    st.metric(
        "MA60",
        money(row["MA60"])
    )


# ============================================================
# TECHNICAL GUIDE
# ============================================================

st.markdown(
    '<div class="section-title">현재 기술적 판단</div>',
    unsafe_allow_html=True
)

signal_class = {
    "buy": "signal-buy",
    "watch": "signal-watch",
    "risk": "signal-risk",
    "neutral": "signal-neutral"
}.get(
    guide["type"],
    "signal-neutral"
)

st.markdown(
    f"""
<div class="signal {signal_class}">

<div class="signal-title">
    {guide["title"]}
</div>

<div class="signal-text">
    {guide["text"]}
</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# SUPPORT / RESISTANCE
# ============================================================

st.markdown(
    '<div class="section-title">핵심 가격대</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
<div class="metric-grid">

<div class="metric">
    <div class="metric-label">주요 지지</div>
    <div class="metric-value">
        {money(support)}원
    </div>
</div>

<div class="metric">
    <div class="metric-label">주요 저항</div>
    <div class="metric-value">
        {money(resistance)}원
    </div>
</div>

<div class="metric">
    <div class="metric-label">20일 이동평균</div>
    <div class="metric-value">
        {money(row["MA20"])}원
    </div>
</div>

<div class="metric">
    <div class="metric-label">60일 이동평균</div>
    <div class="metric-value">
        {money(row["MA60"])}원
    </div>
</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# POSITION
# ============================================================

st.markdown(
    '<div class="section-title">내 보유 포지션</div>',
    unsafe_allow_html=True
)

holding = st.radio(
    "해당 ETF를 현재 보유하고 계신가요?",
    ["보유 중", "보유하지 않음"],
    horizontal=True
)


# ============================================================
# HOLDING
# ============================================================

if holding == "보유 중":

    col1, col2 = st.columns(2)

    with col1:

        avg_price = st.number_input(
            "평균 매수가",
            min_value=0.0,
            value=float(current_price),
            step=100.0,
            format="%.0f"
        )

    with col2:

        quantity = st.number_input(
            "보유 수량",
            min_value=0,
            value=1,
            step=1
        )

    invested = avg_price * quantity

    valuation = current_price * quantity

    profit = valuation - invested

    profit_rate = (
        profit / invested * 100
        if invested > 0
        else 0
    )

    st.markdown(
        f"""
<div class="card">

<div class="metric-grid">

<div class="metric">
    <div class="metric-label">투자원금</div>
    <div class="metric-value">
        {money(invested)}원
    </div>
</div>

<div class="metric">
    <div class="metric-label">평가금액</div>
    <div class="metric-value">
        {money(valuation)}원
    </div>
</div>

<div class="metric">
    <div class="metric-label">평가손익</div>
    <div class="metric-value">
        {money(profit)}원
    </div>
</div>

<div class="metric">
    <div class="metric-label">수익률</div>
    <div class="metric-value">
        {profit_rate:+.2f}%
    </div>
</div>

</div>

</div>
""",
        unsafe_allow_html=True
    )

    hguide = holding_guide(
        df,
        avg_price,
        quantity,
        support,
        resistance
    )

    hclass = {
        "buy": "signal-buy",
        "watch": "signal-watch",
        "risk": "signal-risk",
        "neutral": "signal-neutral"
    }.get(
        hguide["type"],
        "signal-neutral"
    )

    st.markdown(
        '<div class="section-title">보유자 대응 가이드</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
<div class="signal {hclass}">

<div class="signal-title">
    {hguide["title"]}
</div>

<div style="
    font-weight:800;
    font-size:14px;
    margin-bottom:7px;
">
    ▶ {hguide["action"]}
</div>

<div class="signal-text">
    {hguide["text"]}
</div>

<div class="small-muted" style="margin-top:8px;">
    {hguide["extra"]}
</div>

</div>
""",
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # PERSONAL PRICE LEVELS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">내 포지션 기준 가격</div>',
        unsafe_allow_html=True
    )

    stop_price = support * 0.97

    partial_sell = resistance

    add_price = min(
        float(row["MA20"]),
        support * 1.02
    )

    st.markdown(
        f"""
<div class="card">

<div class="data-row">
    <span class="data-label">평균매수가</span>
    <span class="data-value">
        {money(avg_price)}원
    </span>
</div>

<div class="data-row">
    <span class="data-label">현재가</span>
    <span class="data-value">
        {money(current_price)}원
    </span>
</div>

<div class="data-row">
    <span class="data-label">추가매수 관심가격</span>
    <span class="data-value">
        {money(add_price)}원
    </span>
</div>

<div class="data-row">
    <span class="data-label">1차 이익실현 검토</span>
    <span class="data-value">
        {money(partial_sell)}원
    </span>
</div>

<div class="data-row">
    <span class="data-label">리스크 관리선</span>
    <span class="data-value">
        {money(stop_price)}원
    </span>
</div>

</div>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="notice">
⚠️ <b>중요:</b>
위 가격은 자동화된 기술적 기준선입니다.
특정 가격에서 반드시 매도하거나 추가매수해야 한다는 의미가 아닙니다.
지지선 이탈이 일시적인지 거래량을 동반한 추세 이탈인지 함께 확인하세요.
</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# NO HOLDING
# ============================================================

else:

    nguide = new_buy_guide(
        df,
        support,
        resistance
    )

    nclass = {
        "buy": "signal-buy",
        "watch": "signal-watch",
        "risk": "signal-risk",
        "neutral": "signal-neutral"
    }.get(
        nguide["type"],
        "signal-neutral"
    )

    st.markdown(
        '<div class="section-title">신규 진입 가이드</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
<div class="signal {nclass}">

<div class="signal-title">
    {nguide["title"]}
</div>

<div style="
    font-weight:800;
    font-size:14px;
    margin-bottom:7px;
">
    ▶ {nguide["action"]}
</div>

<div class="signal-text">
    {nguide["text"]}
</div>

</div>
""",
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # BUY ZONES
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">신규매수 관심 가격대</div>',
        unsafe_allow_html=True
    )

    buy1 = float(nguide["buy1"])
    buy2 = float(nguide["buy2"])

    st.markdown(
        f"""
<div class="metric-grid">

<div class="metric">
    <div class="metric-label">1차 관심가격</div>
    <div class="metric-value">
        {money(buy1)}원
    </div>
</div>

<div class="metric">
    <div class="metric-label">2차 관심가격</div>
    <div class="metric-value">
        {money(buy2)}원
    </div>
</div>

<div class="metric">
    <div class="metric-label">현재가</div>
    <div class="metric-value">
        {money(current_price)}원
    </div>
</div>

<div class="metric">
    <div class="metric-label">주요 저항</div>
    <div class="metric-value">
        {money(resistance)}원
    </div>
</div>

</div>
""",
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="notice">
💡 <b>분할매수 원칙</b><br>
1차 가격에서 전체 예정금액을 한 번에 투입하기보다
일부만 진입하고, 지지 확인 또는 추가 조정 시 2차 진입을 검토하는 방식입니다.
돌파 직후 거래량이 급증한 경우에는 추격매수 위험을 별도로 확인하세요.
</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# CHART
# ============================================================

st.markdown(
    '<div class="section-title">가격 / 거래량 / RSI</div>',
    unsafe_allow_html=True
)

fig = make_chart(
    df,
    support,
    resistance
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False
    }
)


# ============================================================
# MACD
# ============================================================

st.markdown(
    '<div class="section-title">MACD 상태</div>',
    unsafe_allow_html=True
)

macd_state = (
    "상승 모멘텀"
    if row["MACD"] > row["MACD_SIGNAL"]
    else "하락 모멘텀"
)

macd_hist = row["MACD_HIST"]

st.markdown(
    f"""
<div class="card">

<div class="data-row">
    <span class="data-label">MACD</span>
    <span class="data-value">
        {row["MACD"]:.3f}
    </span>
</div>

<div class="data-row">
    <span class="data-label">Signal</span>
    <span class="data-value">
        {row["MACD_SIGNAL"]:.3f}
    </span>
</div>

<div class="data-row">
    <span class="data-label">Histogram</span>
    <span class="data-value">
        {macd_hist:.3f}
    </span>
</div>

<div class="data-row">
    <span class="data-label">판정</span>
    <span class="data-value">
        {macd_state}
    </span>
</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# BOLLINGER
# ============================================================

st.markdown(
    '<div class="section-title">볼린저밴드</div>',
    unsafe_allow_html=True
)

bb_position = (
    current_price -
    row["BB_LOWER"]
) / (
    row["BB_UPPER"] -
    row["BB_LOWER"]
) * 100

bb_position = float(
    np.clip(
        bb_position,
        0,
        100
    )
)

st.markdown(
    f"""
<div class="card">

<div class="data-row">
    <span class="data-label">상단밴드</span>
    <span class="data-value">
        {money(row["BB_UPPER"])}원
    </span>
</div>

<div class="data-row">
    <span class="data-label">중심선</span>
    <span class="data-value">
        {money(row["BB_MID"])}원
    </span>
</div>

<div class="data-row">
    <span class="data-label">하단밴드</span>
    <span class="data-value">
        {money(row["BB_LOWER"])}원
    </span>
</div>

<div class="data-row">
    <span class="data-label">밴드 내 위치</span>
    <span class="data-value">
        {bb_position:.1f}%
    </span>
</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# VOLUME PROFILE
# ============================================================

st.markdown(
    '<div class="section-title">최근 120일 매물대</div>',
    unsafe_allow_html=True
)

vp = volume_profile(df)

if not vp.empty:

    vp_top = vp.sort_values(
        "Volume",
        ascending=False
    ).head(5)

    for _, item in vp_top.iterrows():

        st.markdown(
            f"""
<div class="data-row">

<span class="data-label">
    매물대
</span>

<span class="data-value">
    {money(item["Price"])}원
</span>

</div>
""",
            unsafe_allow_html=True
        )


# ============================================================
# TECHNICAL SCORE BREAKDOWN
# ============================================================

st.markdown(
    '<div class="section-title">기술점수 구성</div>',
    unsafe_allow_html=True
)

score_items = []

if row["Close"] > row["MA20"]:
    score_items.append(("가격 > MA20", 15))
else:
    score_items.append(("가격 < MA20", 0))

if row["MA20"] > row["MA60"]:
    score_items.append(("MA20 > MA60", 10))
else:
    score_items.append(("MA20 < MA60", 0))

if 50 <= row["RSI"] <= 70:
    score_items.append(("RSI 정상 상승구간", 20))
elif 40 <= row["RSI"] < 50:
    score_items.append(("RSI 회복구간", 12))
else:
    score_items.append(("RSI 기타", 5))

if row["MACD"] > row["MACD_SIGNAL"]:
    score_items.append(("MACD 상승", 15))
else:
    score_items.append(("MACD 약세", 5))

if row["VOL_RATIO"] >= 1.2 and row["RETURN_1D"] > 0:
    score_items.append(("거래량 동반 상승", 15))
else:
    score_items.append(("거래량 보통", 0))

for label, pts in score_items:

    st.markdown(
        f"""
<div class="data-row">
    <span class="data-label">{label}</span>
    <span class="data-value">+{pts}</span>
</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

st.markdown(
    '<div class="section-title">오늘의 핵심 정리</div>',
    unsafe_allow_html=True
)

if holding == "보유 중":

    final_text = f"""
현재 {selected_name}은(는) {pattern} 상태이며,
기술점수는 {score}/100입니다.

현재가 {money(current_price)}원,
평균매수가 {money(avg_price)}원 기준으로
수익률은 {profit_rate:+.2f}%입니다.

핵심은 현재 가격을 추격하기보다
{money(support)}원 지지선과 {money(resistance)}원 저항선의
돌파·이탈 여부를 확인하는 것입니다.
"""

else:

    final_text = f"""
현재 {selected_name}은(는) {pattern} 상태이며,
기술점수는 {score}/100입니다.

현재가 {money(current_price)}원에서
무리하게 일괄 진입하기보다
{money(support)}원 부근 지지 여부와
{money(resistance)}원 돌파 여부를 확인하는 것이 핵심입니다.
"""


st.markdown(
    f"""
<div class="card">

<div class="signal-text">
{final_text}
</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# DISCLAIMER
# ============================================================

st.markdown(
    """
<div class="notice">
📌 <b>ETF RADAR 안내</b><br>
본 앱의 매수·매도·보유 가이드는 이동평균선, RSI, MACD,
거래량, 지지·저항 등 기술적 지표를 조합한 참고용 시나리오입니다.
미래 수익을 보장하지 않으며 실제 투자 판단과 책임은 투자자에게 있습니다.
</div>
""",
    unsafe_allow_html=True
)