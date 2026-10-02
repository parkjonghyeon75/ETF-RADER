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
# ETF RADAR v10.1
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
    --bg: #f4f6fa;
    --card: #ffffff;
    --text: #111827;
    --muted: #64748b;
    --line: #e5e7eb;
    --blue: #2563eb;
    --green: #16a34a;
    --red: #dc2626;
    --orange: #d97706;
    --purple: #7c3aed;
}

.stApp {
    background:
        linear-gradient(
            180deg,
            #f8fafc 0%,
            #f4f7fb 45%,
            #eef2f7 100%
        );
    color: var(--text);
}

.block-container {
    max-width: 760px;
    padding-top: 0.55rem;
    padding-bottom: 3rem;
    padding-left: 0.65rem;
    padding-right: 0.65rem;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}


/* ============================================================
   TABS
   ============================================================ */

div[data-baseweb="tab-list"] {
    gap: 4px;
    background: #e8edf4;
    padding: 4px;
    border-radius: 15px;
    margin-bottom: 10px;
}

button[data-baseweb="tab"] {
    border-radius: 11px !important;
    font-size: 0.80rem !important;
    font-weight: 800 !important;
    color: #64748b !important;
    padding: 0.52rem 0.35rem !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: #ffffff !important;
    color: #111827 !important;
    box-shadow: 0 2px 8px rgba(15,23,42,0.08);
}


/* ============================================================
   COMMON CARD
   ============================================================ */

.card {
    background: rgba(255,255,255,0.97);
    border: 1px solid #e2e8f0;
    border-radius: 17px;
    padding: 14px;
    margin: 7px 0;
    box-shadow: 0 4px 16px rgba(15,23,42,0.045);
}

.card-tight { padding: 11px 13px; }

.card-title {
    color: #64748b;
    font-size: 0.68rem;
    font-weight: 850;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}


/* ============================================================
   HEADER
   ============================================================ */

.top-brand { padding: 0.35rem 0.1rem 0.55rem; }
.brand-small { color: #2563eb; font-size: 0.72rem; font-weight: 900; letter-spacing: 0.12em; }
.brand-main { color: #0f172a; font-size: 1.52rem; font-weight: 900; letter-spacing: -0.055em; margin-top: 2px; }
.brand-sub { color: #64748b; font-size: 0.70rem; margin-top: 2px; }


/* ============================================================
   HERO
   ============================================================ */

.hero {
    background: radial-gradient(circle at 100% 0%, rgba(37,99,235,0.14), transparent 38%), #ffffff;
    border: 1px solid #dfe6ef;
    border-radius: 21px;
    padding: 16px;
    margin: 8px 0;
    box-shadow: 0 7px 24px rgba(15,23,42,0.06);
}

.hero-top { display: flex; align-items: flex-start; justify-content: space-between; }
.hero-name { font-size: 0.92rem; font-weight: 850; color: #111827; line-height: 1.35; }
.hero-code { font-size: 0.67rem; color: #94a3b8; margin-top: 2px; }
.hero-price { font-size: 2.25rem; line-height: 1.0; font-weight: 900; letter-spacing: -0.065em; color: #0f172a; margin-top: 13px; }
.hero-unit { font-size: 0.82rem; font-weight: 800; }
.hero-change { font-size: 0.88rem; font-weight: 900; margin-top: 6px; }

.hero-mini {
    background: #f8fafc;
    border: 1px solid #edf1f5;
    border-radius: 11px;
    padding: 7px 9px;
    min-width: 82px;
    text-align: center;
}

.hero-mini-label { font-size: 0.59rem; color: #94a3b8; font-weight: 800; }
.hero-mini-value { font-size: 0.84rem; color: #111827; font-weight: 900; margin-top: 2px; }


/* ============================================================
   SCORE & SIGNAL
   ============================================================ */

.score-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 19px;
    padding: 13px;
    min-height: 156px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 0 4px 17px rgba(15,23,42,0.045);
}

.score-number { font-size: 2rem; line-height: 1; font-weight: 950; color: #0f172a; }
.score-denom { color: #94a3b8; font-size: 0.60rem; margin-top: 3px; }
.score-label { margin-top: 8px; font-size: 0.76rem; font-weight: 900; color: #2563eb; text-align: center; }

.signal-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 7px; margin-top: 7px; }
.signal { background: #f8fafc; border: 1px solid #e7ebf0; border-radius: 12px; padding: 9px; }
.signal-title { font-size: 0.62rem; color: #64748b; font-weight: 800; }
.signal-value { font-size: 0.83rem; font-weight: 900; margin-top: 2px; }
.signal-good { color: #15803d; }
.signal-warn { color: #d97706; }
.signal-bad { color: #dc2626; }


/* ============================================================
   SECTION & PATTERN
   ============================================================ */

.section-head { display: flex; align-items: center; justify-content: space-between; margin: 17px 2px 7px; }
.section-title { font-size: 0.91rem; font-weight: 900; color: #0f172a; letter-spacing: -0.025em; }
.section-caption { color: #94a3b8; font-size: 0.63rem; }

.pattern-box {
    background: linear-gradient(135deg, #eef5ff, #f8fafc);
    border: 1px solid #dbeafe;
    border-radius: 17px;
    padding: 13px;
}
.pattern-title { color: #1d4ed8; font-size: 0.63rem; font-weight: 900; letter-spacing: 0.08em; }
.pattern-main { color: #0f172a; font-size: 0.98rem; font-weight: 900; margin-top: 4px; line-height: 1.35; }
.pattern-desc { color: #64748b; font-size: 0.69rem; margin-top: 5px; line-height: 1.45; }


/* ============================================================
   ACTION CARDS & PRICE MAP
   ============================================================ */

.action-card { border-radius: 15px; padding: 12px; margin: 5px 0; border: 1px solid; }
.action-buy { background: #f0fdf4; border-color: #bbf7d0; }
.action-sell { background: #fff7f7; border-color: #fecaca; }
.action-wait { background: #fffbeb; border-color: #fde68a; }
.action-break { background: #eff6ff; border-color: #bfdbfe; }

.action-label { font-size: 0.62rem; font-weight: 900; letter-spacing: 0.07em; }
.action-price { font-size: 1.12rem; font-weight: 950; margin-top: 3px; color: #111827; }
.action-desc { font-size: 0.66rem; color: #64748b; margin-top: 3px; line-height: 1.35; }

.price-map { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 17px; padding: 12px 14px; }
.price-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f1f5f9; }
.price-row:last-child { border-bottom: none; }
.price-name { font-size: 0.68rem; font-weight: 800; color: #64748b; }
.price-number { font-size: 0.84rem; font-weight: 950; }

.momentum-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 15px; padding: 11px; min-height: 88px; }
.momentum-title { color: #64748b; font-size: 0.61rem; font-weight: 850; }
.momentum-value { color: #0f172a; font-size: 1.15rem; font-weight: 950; margin-top: 4px; }
.momentum-sub { color: #94a3b8; font-size: 0.63rem; margin-top: 2px; }

.score-breakdown { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 14px; padding: 11px; }
.score-line { display: flex; justify-content: space-between; padding: 5px 0; font-size: 0.67rem; }
.score-line-label { color: #64748b; }
.score-line-value { font-weight: 900; color: #111827; }

.theme-card { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 14px; padding: 12px; }
.theme-rank { color: #2563eb; font-size: 0.60rem; font-weight: 900; letter-spacing: 0.08em; }
.theme-name { color: #111827; font-size: 0.91rem; font-weight: 900; margin-top: 3px; }

div[data-testid="stExpander"] { border: 1px solid #e2e8f0 !important; border-radius: 14px !important; background: #ffffff !important; overflow: hidden; }
.stButton > button { border-radius: 11px !important; font-weight: 850 !important; min-height: 40px !important; }
button[kind="primary"] { background: #2563eb !important; }
div[data-testid="stDataFrame"] { border-radius: 13px; overflow: hidden; }

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA & POOLS
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
        "441680": "SOL 미국배당다우존스",
        "476480": "KODEX 미국배당커버드콜",
        "451780": "TIGER 미국배당+7%프리미엄"
    },
    "🛡 안전자산 / 국내단기채 / 미국국채": {
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
        "long_view": "메모리 반도체 업황 사이클과 AI 서버 투자 흐름이 주요 변수입니다."
    },
    "487240": {
        "theme": "미국 AI 빅테크 TOP10",
        "cycle": "고성장기",
        "desc": "AI 관련 미국 대형 기술기업 중심 포트폴리오.",
        "long_view": "AI 서비스 수익화와 기업 실적 증가 여부가 핵심 변수입니다."
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
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_json_file(WATCHLIST_FILE, DEFAULT_WATCHLIST)

if "theme_info" not in st.session_state:
    st.session_state.theme_info = load_json_file(THEME_FILE, DEFAULT_THEME_INFO)


# ============================================================
# NAVER & YFINANCE API
# ============================================================

def search_stock_code_by_keyword(keyword):
    try:
        encoded = urllib.parse.quote(keyword)
        url = f"https://ac.stock.naver.com/ac?q={encoded}&target=etf"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            res_json = json.loads(response.read().decode("utf-8"))
            items = res_json.get("items", [])
            if items:
                return items[0][0], items[0][1]
    except Exception:
        pass
    return None, None

def get_stock_name(code):
    try:
        url = f"https://m.stock.naver.com/api/stock/{code}/basic"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("stockName", f"ETF {code}")
    except Exception:
        return f"ETF {code}"

def fetch_from_naver(code, count=500):
    try:
        url = f"https://fchart.stock.naver.com/sise.nhn?symbol={urllib.parse.quote(code)}&timeframe=day&count={count}&requestType=0"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read().decode("euc-kr", errors="ignore")
        root = ET.fromstring(xml_data)
        rows = []
        for item in root.findall(".//item"):
            parts = item.attrib.get("data", "").split("|")
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
        return pd.DataFrame(rows).set_index("Date").sort_index()
    except Exception:
        return None

@st.cache_data(ttl=300, show_spinner=False)
def load_etf_data(ticker_code, period="1y"):
    clean_code = "".join(filter(str.isalnum, str(ticker_code)))
    if not clean_code:
        clean_code = str(ticker_code).strip()

    df = fetch_from_naver(clean_code, count=500)

    if df is None or df.empty:
        for suffix in [".KS", ".KQ"]:
            try:
                data = yf.download(f"{clean_code}{suffix}", period="2y", progress=False, auto_adjust=False, threads=False)
                if not data.empty and len(data) >= 20:
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.get_level_values(0)
                    data = data[["Open", "High", "Low", "Close", "Volume"]].copy()
                    data.index = pd.to_datetime(data.index)
                    df = data
                    break
            except Exception:
                pass

    if df is None or df.empty or len(df) < 20:
        return None, clean_code

    if period == "6m":
        df = df.iloc[-130:]
    elif period == "1y":
        df = df.iloc[-260:]
    else:
        df = df.iloc[-500:]

    return df.copy(), clean_code


# ============================================================
# TECHNICAL ANALYSIS & INDICATORS
# ============================================================

def calculate_indicators(df):
    df = df.copy()
    for n in [5, 20, 60, 120]:
        df[f"MA{n}"] = df["Close"].rolling(n).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta).clip(upper=0).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    df["BB_Mid"] = df["MA20"]
    std20 = df["Close"].rolling(20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * std20
    df["BB_Lower"] = df["BB_Mid"] - 2 * std20

    df["Vol_MA20"] = df["Volume"].rolling(20).mean()
    df["Vol_Ratio"] = df["Volume"] / df["Vol_MA20"].replace(0, np.nan)
    return df

def get_support_resistance(df):
    current = float(df["Close"].iloc[-1])
    recent20 = df.iloc[-20:]
    supports, resistances = [], []

    for col in ["MA20", "MA60", "MA120"]:
        if col in df.columns and pd.notna(df[col].iloc[-1]):
            p = float(df[col].iloc[-1])
            if p < current:
                supports.append({"price": p, "strength": 2})
            elif p > current:
                resistances.append({"price": p, "strength": 2})

    p_low = float(recent20["Low"].min())
    if p_low < current:
        supports.append({"price": p_low, "strength": 3})

    p_high = float(recent20["High"].max())
    if p_high > current:
        resistances.append({"price": p_high, "strength": 3})

    def dedup(levels):
        out = []
        for item in sorted(levels, key=lambda x: x["price"]):
            if not out or abs(item["price"] - out[-1]["price"]) / out[-1]["price"] > 0.012:
                out.append(item.copy())
            else:
                if item["strength"] > out[-1]["strength"]:
                    out[-1] = item.copy()
        return out

    supports = sorted(dedup(supports), key=lambda x: x["price"], reverse=True)[:3]
    resistances = sorted(dedup(resistances), key=lambda x: x["price"])[:3]
    return supports, resistances

def volume_profile(df, bins=20):
    data = df.iloc[-120:] if len(df) >= 120 else df
    low, high = float(data["Low"].min()), float(data["High"].max())
    if high <= low:
        return pd.DataFrame(columns=["price", "volume"])

    edges = np.linspace(low, high, bins + 1)
    volumes = np.zeros(bins)
    typical = (data["High"] + data["Low"] + data["Close"]) / 3

    for price, vol in zip(typical, data["Volume"]):
        idx = np.searchsorted(edges, price, side="right") - 1
        idx = min(max(idx, 0), bins - 1)
        volumes[idx] += float(vol)

    prices = (edges[:-1] + edges[1:]) / 2
    vp = pd.DataFrame({"price": prices, "volume": volumes})
    vp["ratio"] = vp["volume"] / max(vp["volume"].max(), 1)
    return vp.sort_values("volume", ascending=False).reset_index(drop=True)

def technical_score(df):
    x = df.iloc[-1]
    prev = df.iloc[-2]
    score = 0
    close, ma20, ma60, rsi = float(x["Close"]), x["MA20"], x["MA60"], x["RSI"]
    macd, sig, hist, vol_ratio = x["MACD"], x["MACD_Signal"], x["MACD_Hist"], x["Vol_Ratio"]

    if pd.notna(ma20) and close > ma20: score += 15
    if pd.notna(ma60) and pd.notna(ma20) and ma20 > ma60: score += 10
    if pd.notna(rsi):
        if 50 <= rsi < 70: score += 20
        elif 40 <= rsi < 50: score += 12
        else: score += 5
    if pd.notna(macd) and pd.notna(sig):
        if macd > sig and hist > 0: score += 20
        elif macd > sig: score += 15
        else: score += 5
    if pd.notna(vol_ratio) and 1.2 <= vol_ratio <= 3.0 and close >= float(prev["Close"]): score += 15

    score = int(max(0, min(100, score + 20)))
    if score >= 80: label = "강한 상승세"
    elif score >= 65: label = "상승 우세"
    elif score >= 45: label = "중립 / 관망"
    elif score >= 30: label = "조정 국면"
    else: label = "약세 / 하락 위험"
    return score, label

def get_score_breakdown(df):
    x = df.iloc[-1]
    prev = df.iloc[-2]
    close, ma20, ma60, rsi = float(x["Close"]), x["MA20"], x["MA60"], x["RSI"]
    macd, sig, hist, vol = x["MACD"], x["MACD_Signal"], x["MACD_Hist"], x["Vol_Ratio"]

    t_p = 15 if (pd.notna(ma20) and close > ma20) else 0
    m_p = 10 if (pd.notna(ma20) and pd.notna(ma60) and ma20 > ma60) else 0
    r_p = 20 if (pd.notna(rsi) and 50 <= rsi < 70) else (12 if (pd.notna(rsi) and 40 <= rsi < 50) else 5)
    mc_p = 20 if (pd.notna(macd) and pd.notna(sig) and macd > sig and hist > 0) else (15 if (pd.notna(macd) and pd.notna(sig) and macd > sig) else 5)
    v_p = 15 if (pd.notna(vol) and 1.2 <= vol <= 3.0 and close >= float(prev["Close"])) else 0

    return {"가격 > MA20": t_p, "MA20 > MA60": m_p, "RSI": r_p, "MACD": mc_p, "거래량": v_p, "기본점수": 20}

def detect_patterns(df, supports, resistances):
    x = df.iloc[-1]
    close, ma20, ma60, rsi = float(x["Close"]), x["MA20"], x["MA60"], x["RSI"]
    macd, sig, vol = x["MACD"], x["MACD_Signal"], x["Vol_Ratio"]
    recent20_high = float(df.iloc[-21:-1]["High"].max()) if len(df) >= 22 else float(df["High"].max())
    patterns = []

    if pd.notna(ma20) and pd.notna(ma60) and pd.notna(rsi):
        if ma20 * 0.985 <= close <= ma20 * 1.025 and ma20 > ma60 and 42 <= rsi <= 65:
            patterns.append("💡 눌림목 매수 관심")
    if close > recent20_high and vol >= 1.3 and pd.notna(macd) and macd > sig:
        patterns.append("🚀 강력한 저항선 돌파")
    if pd.notna(rsi) and rsi >= 70:
        patterns.append("⚠️ 단기 과열")
    if pd.notna(ma20) and close < ma20 and pd.notna(macd) and macd < sig:
        patterns.append("🔻 단기 추세 약화")

    if not patterns:
        patterns.append("📈 차분한 우상향" if (pd.notna(ma20) and close > ma20) else "💤 횡보 / 관망")
    return patterns

def chase_risk(df):
    x = df.iloc[-1]
    close, ma20, rsi, vol = float(x["Close"]), x["MA20"], x["RSI"], x["Vol_Ratio"]
    risk, reasons = 0, []

    if pd.notna(rsi) and rsi >= 70: risk += 40; reasons.append("RSI 과열")
    if pd.notna(ma20) and close > ma20 * 1.05: risk += 30; reasons.append("20일선과 거리 확대")
    if pd.notna(vol) and vol >= 2.0: risk += 20; reasons.append("거래량 급증")

    risk = min(100, risk)
    if risk >= 60: label, cls = "높음", "signal-bad"
    elif risk >= 30: label, cls = "주의", "signal-warn"
    else: label, cls = "낮음", "signal-good"
    return risk, label, cls, reasons

def easy_action_scenario(df, score, supports, resistances, patterns):
    x = df.iloc[-1]
    close = float(x["Close"])
    ma20 = float(x["MA20"]) if pd.notna(x["MA20"]) else close

    s1 = supports[0]["price"] if supports else ma20
    s2 = supports[1]["price"] if len(supports) > 1 else ma20 * 0.97
    r1 = resistances[0]["price"] if resistances else close * 1.03
    r2 = resistances[1]["price"] if len(resistances) > 1 else close * 1.06

    if "⚠ 단기 과열" in patterns:
        st_title, b_g, s_g, w_g = "과열 구간 · 추격보다 눌림 대기", f"{s1:,.0f}원 부근 지지 여부", f"{r1:,.0f}~{r2:,.0f}원 저항 구간", f"{s1:,.0f}원 지지선 확인"
    elif "🚀 강력한 저항선 돌파" in patterns:
        st_title, b_g, s_g, w_g = "돌파 확인 · 거래량 유지 중요", f"{r1:,.0f}원 돌파 후 지지", f"{r2:,.0f}원 전후 저항 확인", f"{r1:,.0f}원 재이탈 확인"
    elif "💡 눌림목 매수 관심" in patterns:
        st_title, b_g, s_g, w_g = "눌림목 구간 · 추세 확인", f"{s1:,.0f}~{close:,.0f}원", f"{r1:,.0f}원 1차 저항", f"{s2:,.0f}원 이탈 여부"
    elif "🔻 단기 추세 약화" in patterns:
        st_title, b_g, s_g, w_g = "단기 추세 약화 · 지지선 확인", f"{s1:,.0f}원 지지 확인", f"{r1:,.0f}원 반등 저항", f"{s2:,.0f}원 추가 조정 여부"
    else:
        st_title, b_g, s_g, w_g = "추세 대응 구간", f"{s1:,.0f}원 지지 확인", f"{r1:,.0f}원 저항 확인", "박스권 흐름 모니터링"

    return st_title, b_g, s_g, w_g, s1, s2, r1, r2

def score_details(df):
    x = df.iloc[-1]
    close, ma20, ma60, rsi, macd, sig, vol = float(x["Close"]), x["MA20"], x["MA60"], x["RSI"], x["MACD"], x["MACD_Signal"], x["Vol_Ratio"]
    
    trend = "강세" if (pd.notna(ma20) and pd.notna(ma60) and close > ma20 and ma20 > ma60) else "중립"
    rsi_state = "과열" if (pd.notna(rsi) and rsi >= 70) else ("침체" if (pd.notna(rsi) and rsi <= 30) else ("상승" if (pd.notna(rsi) and rsi >= 50) else "약세"))
    macd_state = "상승" if (pd.notna(macd) and pd.notna(sig) and macd > sig) else "약세"
    volume_state = "확인중" if pd.isna(vol) else ("강한 유입" if vol >= 1.5 else ("평균 이상" if vol >= 1.0 else "조용함"))
    return trend, rsi_state, macd_state, volume_state

def make_main_chart(df, supports, resistances):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.035, row_heights=[0.62, 0.20, 0.18])

    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], increasing_line_color="#16a34a", decreasing_line_color="#dc2626", name="가격"), row=1, col=1)

    for col, color in [("MA5", "#f59e0b"), ("MA20", "#2563eb"), ("MA60", "#16a34a"), ("MA120", "#7c3aed")]:
        if col in df:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], line=dict(color=color, width=1.35), name=col), row=1, col=1)

    for i, item in enumerate(supports[:2], 1):
        fig.add_hline(y=item["price"], row=1, col=1, line_dash="dot", line_color="#16a34a", annotation_text=f"S{i}", annotation_position="bottom left")
    for i, item in enumerate(resistances[:2], 1):
        fig.add_hline(y=item["price"], row=1, col=1, line_dash="dash", line_color="#dc2626", annotation_text=f"R{i}", annotation_position="top left")

    volume_colors = ["#16a34a" if c >= o else "#dc2626" for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], marker_color=volume_colors, name="거래량"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], line=dict(color="#2563eb", width=1.7), name="RSI"), row=3, col=1)

    fig.add_hline(y=70, row=3, col=1, line_dash="dot", line_color="#dc2626")
    fig.add_hline(y=30, row=3, col=1, line_dash="dot", line_color="#16a34a")

    fig.update_layout(
        height=650, margin=dict(l=4, r=4, t=8, b=8), template="plotly_white",
        showlegend=False, xaxis_rangeslider_visible=False, dragmode=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", size=10, color="#64748b")
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7", fixedrange=True)
    return fig

def scan_market_leading_themes():
    theme_scores = []
    for theme_name, pool_dict in DC_PENSION_POOLS.items():
        theme_total_score, theme_change_sum, valid_count, top_gems = 0, 0, 0, []
        for code, name in pool_dict.items():
            raw_df, _ = load_etf_data(code, "6m")
            if raw_df is None or len(raw_df) < 30: continue
            df = calculate_indicators(raw_df)
            x, prev = df.iloc[-1], df.iloc[-2]
            change = float((x["Close"] - prev["Close"]) / prev["Close"] * 100)
            theme_change_sum += change
            valid_count += 1

            reasons, score_add = [], 0
            if pd.notna(x["MACD"]) and pd.notna(x["MACD_Signal"]) and prev["MACD"] <= prev["MACD_Signal"] and x["MACD"] > x["MACD_Signal"]:
                reasons.append("MACD 골든크로스"); score_add += 35
            if pd.notna(x["Vol_Ratio"]) and x["Vol_Ratio"] >= 1.3 and x["Close"] > prev["Close"]:
                reasons.append("거래량 유입"); score_add += 30
            if pd.notna(x["MA20"]) and 0.98 <= x["Close"] / x["MA20"] <= 1.02:
                reasons.append("20일선 지지"); score_add += 25

            item_score = min(100, 50 + score_add)
            theme_total_score += item_score
            top_gems.append({
                "code": code, "name": name, "price": float(x["Close"]), "change": change,
                "reasons": (reasons if reasons else ["안정적 흐름"]), "score": item_score
            })

        if valid_count > 0:
            theme_scores.append({
                "theme_name": theme_name,
                "avg_score": theme_total_score / valid_count,
                "avg_change": theme_change_sum / valid_count,
                "gems": sorted(top_gems, key=lambda x: x["score"], reverse=True)
            })
    return sorted(theme_scores, key=lambda x: x["avg_score"], reverse=True)


# ============================================================
# MAIN UI APP LAYOUT
# ============================================================

st.markdown("""
<div class="top-brand">
    <div class="brand-small">ETF RADAR</div>
    <div class="brand-main">Technical Dashboard</div>
    <div class="brand-sub">ETF Technical Analysis · Momentum · Support / Resistance</div>
</div>
""", unsafe_allow_html=True)

tab_analysis, tab_market = st.tabs(["📊 ETF RADAR", "🔥 MARKET RADAR"])

# ------------------------------------------------------------
# TAB 1 : ETF RADAR
# ------------------------------------------------------------
with tab_analysis:
    watchlist = st.session_state.watchlist

    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        keyword_input = st.text_input("종목 검색", placeholder="ETF명 또는 코드", label_visibility="collapsed", key="ind_search")
    with search_col2:
        search_add_btn = st.button("＋ 저장", use_container_width=True, key="ind_save_btn")

    if search_add_btn and keyword_input:
        with st.spinner("ETF 검색 중..."):
            found_code, found_name = search_stock_code_by_keyword(keyword_input.strip())
            if not found_code:
                clean_test = "".join(filter(str.isalnum, keyword_input.strip()))
                test_df, _ = load_etf_data(clean_test, "6m")
                if test_df is not None:
                    found_code, found_name = clean_test, get_stock_name(clean_test)

            if found_code:
                st.session_state.watchlist[found_code] = f"{found_name} ({found_code})"
                save_json_file(WATCHLIST_FILE, st.session_state.watchlist)
                if found_code not in st.session_state.theme_info:
                    st.session_state.theme_info[found_code] = {
                        "theme": "신규 등록 ETF", "cycle": "관찰 필요",
                        "desc": f"{found_name} 관련 ETF", "long_view": "중장기 흐름 확인 필요"
                    }
                    save_json_file(THEME_FILE, st.session_state.theme_info)
                st.success(f"{found_name} 저장 완료")
                st.rerun()
            else:
                st.error("해당 ETF를 찾을 수 없습니다.")

    options = list(watchlist.values())
    if not options:
        st.warning("관심종목을 먼저 추가해주세요.")
        st.stop()

    c1, c2 = st.columns([2.2, 1])
    with c1:
        selected = st.selectbox("관심 ETF", options, label_visibility="collapsed")
    with c2:
        period = st.selectbox("기간", ["6m", "1y", "2y"], index=1, label_visibility="collapsed")

    symbol_input = next(k for k, v in watchlist.items() if v == selected)

    with st.spinner("시장 데이터를 분석하고 있습니다..."):
        raw_df, code = load_etf_data(symbol_input, period)

    if raw_df is None:
        st.error("데이터를 불러오지 못했습니다.")
        st.stop()

    df = calculate_indicators(raw_df).dropna(subset=["Close"]).copy()
    if len(df) < 20:
        st.error("분석에 필요한 데이터가 부족합니다.")
        st.stop()

    score, score_label = technical_score(df)
    supports, resistances = get_support_resistance(df)
    vp = volume_profile(df)
    patterns = detect_patterns(df, supports, resistances)
    status_title, buy_guide, sell_guide, wait_guide, s1, s2, r1, r2 = easy_action_scenario(df, score, supports, resistances, patterns)
    trend_state, rsi_state, macd_state, volume_state = score_details(df)
    chase_score, chase_label, chase_class, chase_reasons = chase_risk(df)
    score_breakdown = get_score_breakdown(df)

    x, prev = df.iloc[-1], df.iloc[-2]
    price = float(x["Close"])
    change = (price - float(prev["Close"])) / float(prev["Close"]) * 100
    rsi = float(x["RSI"]) if pd.notna(x["RSI"]) else 50
    vol_ratio = float(x["Vol_Ratio"]) if pd.notna(x["Vol_Ratio"]) else 1
    change_color = "#16a34a" if change >= 0 else "#dc2626"

    # HERO
    st.markdown(f"""
    <div class="hero">
        <div class="hero-top">
            <div>
                <div class="hero-name">{selected.split(" (")[0]}</div>
                <div class="hero-code">{code}</div>
            </div>
            <div class="hero-mini">
                <div class="hero-mini-label">SCORE</div>
                <div class="hero-mini-value">{score}/100</div>
            </div>
        </div>
        <div class="hero-price">{price:,.0f} <span class="hero-unit">원</span></div>
        <div class="hero-change" style="color:{change_color};">
            {"▲" if change >= 0 else "▼"} {abs(change):.2f}%
            <span style="color:#94a3b8; font-size:0.65rem; margin-left:5px;">최근 거래일 기준</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # SCORE + SIGNAL
    score_col, signal_col = st.columns([0.85, 1.15])
    with score_col:
        score_color = "#16a34a" if score >= 65 else ("#d97706" if score >= 45 else "#dc2626")
        st.markdown(f"""
        <div class="score-card">
            <div class="score-number" style="color:{score_color};">{score}</div>
            <div class="score-denom">/ 100</div>
            <div class="score-label">{score_label}</div>
        </div>
        """, unsafe_allow_html=True)

    with signal_col:
        st.markdown(f"""
        <div class="card card-tight">
            <div class="card-title">MARKET SIGNAL</div>
            <div class="signal-grid">
                <div class="signal">
                    <div class="signal-title">추세</div>
                    <div class="signal-value {'signal-good' if trend_state == '강세' else 'signal-warn'}">{trend_state}</div>
                </div>
                <div class="signal">
                    <div class="signal-title">RSI</div>
                    <div class="signal-value">{rsi:.0f} · {rsi_state}</div>
                </div>
                <div class="signal">
                    <div class="signal-title">MACD</div>
                    <div class="signal-value {'signal-good' if macd_state == '상승' else 'signal-bad'}">{macd_state}</div>
                </div>
                <div class="signal">
                    <div class="signal-title">거래량</div>
                    <div class="signal-value">{vol_ratio:.1f}x · {volume_state}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # TODAY SIGNAL
    st.markdown("""
    <div class="section-head">
        <div class="section-title">🎯 TODAY SIGNAL</div>
        <div class="section-caption">Technical setup</div>
    </div>
    """, unsafe_allow_html=True)

    pattern_main = patterns[0]
    pattern_desc = (
        "중단기 상승추세가 유지되는 가운데 20일선 부근에서 가격 지지를 확인하는 구간입니다." if "눌림목" in pattern_main else
        ("최근 고점을 넘어선 상태입니다. 돌파 이후 거래량과 지지 여부를 함께 확인합니다." if "돌파" in pattern_main else
         ("단기 상승 탄력이 강해진 구간입니다. 추격보다는 조정 시 지지 확인이 중요합니다." if "과열" in pattern_main else
          ("가격이 단기 기준선 아래로 내려온 상태입니다. 다음 지지선의 반응을 확인할 필요가 있습니다." if "약화" in pattern_main else
           "현재 이동평균과 모멘텀을 기준으로 단기 방향성을 확인하는 구간입니다.")))

    st.markdown(f"""
    <div class="pattern-box">
        <div class="pattern-title">CURRENT SETUP</div>
        <div class="pattern-main">{pattern_main}</div>
        <div class="pattern-desc">{pattern_desc}</div>
        <div style="margin-top:7px; color:#334155; font-size:0.69rem; font-weight:800;">{status_title}</div>
    </div>
    """, unsafe_allow_html=True)

    # PRICE ZONES
    st.markdown("""
    <div class="section-head">
        <div class="section-title">📍 PRICE ZONES</div>
        <div class="section-caption">Key levels</div>
    </div>
    """, unsafe_allow_html=True)

    z1, z2 = st.columns(2)
    with z1:
        st.markdown(f"""
        <div class="action-card action-buy">
            <div class="action-label" style="color:#15803d;">🟢 INTEREST ZONE</div>
            <div class="action-price">{s1:,.0f}원</div>
            <div class="action-desc">1차 지지 · {buy_guide}</div>
        </div>
        """, unsafe_allow_html=True)
    with z2:
        st.markdown(f"""
        <div class="action-card action-sell">
            <div class="action-label" style="color:#dc2626;">🔴 RESISTANCE</div>
            <div class="action-price">{r1:,.0f}원</div>
            <div class="action-desc">1차 저항 · {sell_guide}</div>
        </div>
        """, unsafe_allow_html=True)

    z3, z4 = st.columns(2)
    with z3:
        st.markdown(f"""
        <div class="action-card action-wait">
            <div class="action-label" style="color:#b45309;">🟡 SECOND SUPPORT</div>
            <div class="action-price">{s2:,.0f}원</div>
            <div class="action-desc">핵심 지지 · {wait_guide}</div>
        </div>
        """, unsafe_allow_html=True)
    with z4:
        st.markdown(f"""
        <div class="action-card action-break">
            <div class="action-label" style="color:#1d4ed8;">🔵 BREAKOUT</div>
            <div class="action-price">{r2:,.0f}원+</div>
            <div class="action-desc">2차 저항 돌파 확인 구간</div>
        </div>
        """, unsafe_allow_html=True)

    # CHASE RISK
    st.markdown("""
    <div class="section-head">
        <div class="section-title">⚠️ CHASE RISK</div>
        <div class="section-caption">추격매수 위험</div>
    </div>
    """, unsafe_allow_html=True)

    risk_text = " · ".join(chase_reasons) if chase_reasons else "현재 가격 기준 추격 위험 요인이 크지 않습니다."
    risk_bg = "#fff1f2" if chase_score >= 60 else ("#fffbeb" if chase_score >= 30 else "#f0fdf4")
    risk_bd = "#fecdd3" if chase_score >= 60 else ("#fde68a" if chase_score >= 30 else "#bbf7d0")

    st.markdown(f"""
    <div style="background:{risk_bg}; border:1px solid {risk_bd}; border-radius:15px; padding:12px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="color:#64748b; font-size:0.63rem; font-weight:850;">CHASE RISK</div>
                <div style="font-size:1rem; font-weight:900; margin-top:2px;">{chase_label}</div>
            </div>
            <div style="font-size:1.25rem; font-weight:950;">{chase_score}</div>
        </div>
        <div style="color:#64748b; font-size:0.67rem; margin-top:6px;">{risk_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # PRICE MAP
    st.markdown("""
    <div class="section-head">
        <div class="section-title">🗺 PRICE MAP</div>
        <div class="section-caption">Support / Resistance</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="price-map">
        <div class="price-row"><div class="price-name">R2 · 2차 저항</div><div class="price-number" style="color:#dc2626;">{r2:,.0f}원</div></div>
        <div class="price-row"><div class="price-name">R1 · 1차 저항</div><div class="price-number" style="color:#dc2626;">{r1:,.0f}원</div></div>
        <div class="price-row" style="background:#eff6ff; margin:0 -8px; padding-left:8px; padding-right:8px; border-radius:8px;">
            <div class="price-name">NOW · 현재가</div><div class="price-number" style="color:#2563eb;">{price:,.0f}원</div>
        </div>
        <div class="price-row"><div class="price-name">S1 · 1차 지지</div><div class="price-number" style="color:#16a34a;">{s1:,.0f}원</div></div>
        <div class="price-row"><div class="price-name">S2 · 2차 지지</div><div class="price-number" style="color:#16a34a;">{s2:,.0f}원</div></div>
    </div>
    """, unsafe_allow_html=True)

    # CHART
    st.markdown("""
    <div class="section-head">
        <div class="section-title">📈 PRICE ACTION</div>
        <div class="section-caption">Candle · MA · Volume · RSI</div>
    </div>
    """, unsafe_allow_html=True)

    fig = make_main_chart(df, supports, resistances)
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True, "displayModeBar": False, "scrollZoom": False}, key=f"main_chart_{symbol_input}_{period}")

    # MOMENTUM
    st.markdown("""
    <div class="section-head">
        <div class="section-title">📊 MOMENTUM</div>
        <div class="section-caption">Current indicators</div>
    </div>
    """, unsafe_allow_html=True)

    i1, i2, i3 = st.columns(3)
    with i1:
        st.markdown(f"""
        <div class="momentum-card">
            <div class="momentum-title">RSI</div>
            <div class="momentum-value">{rsi:.1f}</div>
            <div class="momentum-sub">{rsi_state}</div>
        </div>
        """, unsafe_allow_html=True)
    with i2:
        st.markdown(f"""
        <div class="momentum-card">
            <div class="momentum-title">VOLUME</div>
            <div class="momentum-value">{vol_ratio:.1f}x</div>
            <div class="momentum-sub">20일 평균 대비</div>
        </div>
        """, unsafe_allow_html=True)
    with i3:
        macd_hist = float(x["MACD_Hist"])
        macd_arrow = "↑" if macd_hist > 0 else "↓"
        st.markdown(f"""
        <div class="momentum-card">
            <div class="momentum-title">MACD</div>
            <div class="momentum-value">{macd_arrow}</div>
            <div class="momentum-sub">{macd_state}</div>
        </div>
        """, unsafe_allow_html=True)

    # DETAIL TABS
    detail_tabs = st.tabs(["📍 매물대", "🏛 테마", "📖 지표"])

    with detail_tabs[0]:
        st.markdown("#### 매물대 집중 구간")
        if not vp.empty:
            vp_show = vp.head(7)[["price", "ratio"]].copy()
            vp_show["가격대"] = vp_show["price"].map(lambda x: f"{x:,.0f}원")
            vp_show["집중도"] = vp_show["ratio"].map(lambda x: f"{x * 100:.0f}%")
            st.dataframe(vp_show[["가격대", "집중도"]], use_container_width=True, hide_index=True)

        st.markdown("#### 지지 / 저항")
        sc, rc = st.columns(2)
        with sc:
            st.markdown("**🟢 SUPPORT**")
            for i, item in enumerate(supports[:3], 1):
                st.success(f"S{i} · {item['price']:,.0f}원")
        with rc:
            st.markdown("**🔴 RESISTANCE**")
            for i, item in enumerate(resistances[:3], 1):
                st.warning(f"R{i} · {item['price']:,.0f}원")

    with detail_tabs[1]:
        theme_info = st.session_state.theme_info.get(code, {
            "theme": "미등록 테마", "cycle": "관찰 필요", "desc": "정보 등록 필요", "long_view": "중장기 관점을 입력해주세요."
        })
        st.markdown(f"""
        <div class="card">
            <div class="card-title">THEME</div>
            <div style="font-size:1.05rem; font-weight:900; margin-top:4px;">{theme_info["theme"]}</div>
            <div style="margin-top:8px; color:#2563eb; font-weight:850; font-size:0.73rem;">{theme_info["cycle"]}</div>
            <div style="margin-top:10px; color:#64748b; font-size:0.72rem; line-height:1.55;">{theme_info["desc"]}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="action-card action-break">
            <div class="action-label" style="color:#1d4ed8;">LONG VIEW</div>
            <div style="margin-top:5px; font-size:0.75rem; line-height:1.5; color:#334155;">{theme_info["long_view"]}</div>
        </div>
        """, unsafe_allow_html=True)

    with detail_tabs[2]:
        st.markdown("#### 종합점수 구성")
        breakdown_html = "".join([f'<div class="score-line"><div class="score-line-label">{l}</div><div class="score-line-value">+{v}</div></div>' for l, v in score_breakdown.items()])
        st.markdown(f'<div class="score-breakdown">{breakdown_html}</div>', unsafe_allow_html=True)
        st.markdown("""
        #### RSI  
        **70 이상** → 단기 과열 영역 | **50~70** → 상승 모멘텀 영역 | **30 이하** → 침체 영역  
        ---  
        #### MACD  
        MACD가 Signal보다 위에 있으면 단기 모멘텀이 상대적으로 강한 상태입니다.  
        ---  
        #### 거래량  
        **1.0x** → 20일 평균 | **1.5x 이상** → 거래량 증가 | **2.0x 이상** → 강한 거래량 유입  
        ---  
        #### 이동평균  
        **MA20 > MA60** → 중단기 추세가 상대적으로 강한 상태입니다.
        """)

    with st.expander("⚙️ 관심종목 관리"):
        if st.button("🗑 현재 종목 삭제", use_container_width=True):
            del st.session_state.watchlist[symbol_input]
            save_json_file(WATCHLIST_FILE, st.session_state.watchlist)
            st.rerun()


# ------------------------------------------------------------
# TAB 2 : MARKET RADAR
# ------------------------------------------------------------
with tab_market:
    st.markdown("""
    <div class="card">
        <div class="card-title">MARKET RADAR</div>
        <div style="font-size:1.12rem; font-weight:900; margin-top:4px;">시장 모멘텀 탐색</div>
        <div style="color:#64748b; font-size:0.72rem; line-height:1.5; margin-top:6px;">
            주요 ETF 테마군의 MACD · 거래량 · 이동평균을 종합해 현재 모멘텀을 확인합니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 MARKET RADAR 실행", use_container_width=True, type="primary", key="auto_scan_btn"):
        st.cache_data.clear()

    with st.spinner("시장 테마를 분석하고 있습니다..."):
        leading_themes = scan_market_leading_themes()

    if leading_themes:
        top_theme = leading_themes[0]
        top_change_color = "#16a34a" if top_theme["avg_change"] >= 0 else "#dc2626"

        st.markdown(f"""
        <div class="hero">
            <div class="card-title">CURRENT MOMENTUM</div>
            <div style="font-size:1.15rem; font-weight:900; margin-top:4px;">{top_theme["theme_name"]}</div>
            <div style="display:flex; align-items:end; justify-content:space-between; margin-top:10px;">
                <div>
                    <div style="color:#64748b; font-size:0.63rem;">MOMENTUM SCORE</div>
                    <div style="font-size:1.95rem; font-weight:950; color:#2563eb;">{top_theme["avg_score"]:.1f}</div>
                </div>
                <div style="color:{top_change_color}; font-weight:900; font-size:0.86rem;">
                    {"▲" if top_theme["avg_change"] >= 0 else "▼"} {abs(top_theme["avg_change"]):.2f}%
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="section-head">
            <div class="section-title">🔥 THEME MOMENTUM</div>
            <div class="section-caption">Technical activation</div>
        </div>
        """, unsafe_allow_html=True)

        for rank, th in enumerate(leading_themes, 1):
            th_change_color = "#16a34a" if th["avg_change"] >= 0 else "#dc2626"
            with st.expander(f"{rank:02d}  {th['theme_name']}  ·  {th['avg_score']:.1f}점"):
                st.markdown(f"""
                <div class="theme-card">
                    <div class="theme-rank">MOMENTUM {rank:02d}</div>
                    <div class="theme-name">{th["theme_name"]}</div>
                    <div style="display:flex; justify-content:space-between; align-items:end; margin-top:8px;">
                        <div>
                            <div style="color:#64748b; font-size:0.61rem;">ACTIVATION</div>
                            <div style="font-size:1.2rem; font-weight:950; color:#2563eb;">{th["avg_score"]:.1f}</div>
                        </div>
                        <div style="color:{th_change_color}; font-weight:850; font-size:0.71rem;">
                            {"▲" if th["avg_change"] >= 0 else "▼"} {abs(th["avg_change"]):.2f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if th["gems"]:
                    st.markdown("**💎 MOMENTUM ETF**")
                    for g in th["gems"][:5]:
                        g_color = "#16a34a" if g["change"] >= 0 else "#dc2626"
                        reasons_str = " · ".join(g["reasons"])
                        st.markdown(f"""
                        <div style="background:#f8fafc; border:1px solid #e5e7eb; border-radius:13px; padding:10px; margin-top:7px;">
                            <div style="display:flex; justify-content:space-between;">
                                <div style="font-size:0.74rem; font-weight:900; color:#111827;">💎 {g["name"]}</div>
                                <div style="font-size:0.69rem; font-weight:900; color:{g_color};">
                                    {"▲" if g["change"] >= 0 else "▼"} {abs(g["change"]):.2f}%
                                </div>
                            </div>
                            <div style="font-size:0.64rem; color:#64748b; margin-top:3px;">
                                {g["code"]} · {g["price"]:,.0f}원 · 기술점수 {g["score"]}
                            </div>
                            <div style="font-size:0.64rem; color:#334155; margin-top:3px;">{reasons_str}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("현재 뚜렷한 신호가 없습니다.")
    else:
        st.warning("시장 데이터를 불러오지 못했습니다.")


# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div style="text-align:center; color:#94a3b8; font-size:0.61rem; margin-top:24px; padding-top:12px; border-top:1px solid #e2e8f0;">
    ETF RADAR v10.1 · Technical Dashboard
</div>
""", unsafe_allow_html=True)
