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
# ETF RADAR (점수 산출표 나란히 배치 및 시장/모멘텀 통합 버전)
# ============================================================

st.set_page_config(
    page_title="ETF Radar",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ============================================================
# PREMIUM MOBILE UI (Font Size Up & Detailed Readability)
# ============================================================

st.markdown("""
<style>

:root {
    --bg: #f4f6fa;
    --card: #ffffff;
    --text: #111827;
    --muted: #475569;
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
    max-width: 780px;
    padding-top: 0.8rem;
    padding-bottom: 3.5rem;
    padding-left: 0.8rem;
    padding-right: 0.8rem;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 1.02rem;
}


/* ============================================================
   TABS
   ============================================================ */

div[data-baseweb="tab-list"] {
    gap: 6px;
    background: #e2e8f0;
    padding: 5px;
    border-radius: 14px;
    margin-bottom: 14px;
}

button[data-baseweb="tab"] {
    border-radius: 10px !important;
    font-size: 0.98rem !important;
    font-weight: 800 !important;
    color: #475569 !important;
    padding: 0.6rem 0.5rem !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: #ffffff !important;
    color: #0f172a !important;
    box-shadow: 0 3px 10px rgba(15,23,42,0.1);
}


/* ============================================================
   COMMON CARD (글씨 크기 전반적 확대)
   ============================================================ */

.card {
    background: rgba(255,255,255,0.98);
    border: 1px solid #cbd5e1;
    border-radius: 16px;
    padding: 18px;
    margin: 10px 0;
    box-shadow: 0 4px 16px rgba(15,23,42,0.05);
}

.card-tight { padding: 15px 18px; }

.card-title {
    color: #475569;
    font-size: 0.85rem;
    font-weight: 850;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}


/* ============================================================
   HEADER
   ============================================================ */

.top-brand { padding: 0.4rem 0.1rem 0.7rem; }
.brand-small { color: #2563eb; font-size: 0.88rem; font-weight: 900; letter-spacing: 0.1em; }
.brand-main { color: #0f172a; font-size: 1.8rem; font-weight: 900; letter-spacing: -0.04em; margin-top: 2px; }
.brand-sub { color: #475569; font-size: 0.9rem; margin-top: 4px; font-weight: 600; }


/* ============================================================
   HERO
   ============================================================ */

.hero {
    background: radial-gradient(circle at 100% 0%, rgba(37,99,235,0.12), transparent 40%), #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 18px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 6px 20px rgba(15,23,42,0.06);
}

.hero-top { display: flex; align-items: flex-start; justify-content: space-between; }
.hero-name { font-size: 1.15rem; font-weight: 900; color: #0f172a; line-height: 1.35; }
.hero-code { font-size: 0.82rem; color: #64748b; margin-top: 3px; font-weight: 700; }
.hero-price { font-size: 2.5rem; line-height: 1.0; font-weight: 950; letter-spacing: -0.05em; color: #0f172a; margin-top: 12px; }
.hero-unit { font-size: 0.98rem; font-weight: 850; }
.hero-change { font-size: 1.02rem; font-weight: 900; margin-top: 8px; }

.hero-mini {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 8px 12px;
    min-width: 95px;
    text-align: center;
}

.hero-mini-label { font-size: 0.74rem; color: #64748b; font-weight: 850; }
.hero-mini-value { font-size: 1.05rem; color: #0f172a; font-weight: 950; margin-top: 2px; }


/* ============================================================
   SCORE & SIGNAL
   ============================================================ */

.score-card {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 16px;
    padding: 16px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 0 4px 15px rgba(15,23,42,0.05);
}

.score-number { font-size: 2.4rem; line-height: 1; font-weight: 950; color: #0f172a; }
.score-denom { color: #64748b; font-size: 0.75rem; margin-top: 4px; font-weight: 700; }
.score-label { margin-top: 8px; font-size: 0.92rem; font-weight: 900; color: #2563eb; text-align: center; }

.signal-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px; }
.signal { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px; }
.signal-title { font-size: 0.78rem; color: #475569; font-weight: 800; }
.signal-value { font-size: 0.98rem; font-weight: 950; margin-top: 4px; }
.signal-good { color: #15803d; }
.signal-warn { color: #d97706; }
.signal-bad { color: #dc2626; }


/* ============================================================
   SECTION & PATTERN
   ============================================================ */

.section-head { display: flex; align-items: center; justify-content: space-between; margin: 20px 2px 10px; }
.section-title { font-size: 1.1rem; font-weight: 900; color: #0f172a; letter-spacing: -0.02em; }
.section-caption { color: #475569; font-size: 0.78rem; font-weight: 700; }

.pattern-box {
    background: linear-gradient(135deg, #eef5ff, #f8fafc);
    border: 1px solid #bfdbfe;
    border-radius: 16px;
    padding: 16px;
}
.pattern-title { color: #1d4ed8; font-size: 0.78rem; font-weight: 900; letter-spacing: 0.06em; }
.pattern-main { color: #0f172a; font-size: 1.15rem; font-weight: 950; margin-top: 6px; line-height: 1.4; }
.pattern-desc { color: #334155; font-size: 0.85rem; margin-top: 8px; line-height: 1.5; font-weight: 600; }


/* ============================================================
   ACTION CARDS & PRICE MAP
   ============================================================ */

.action-card { border-radius: 15px; padding: 16px; margin: 8px 0; border: 1px solid; }
.action-buy { background: #f0fdf4; border-color: #86efac; }
.action-sell { background: #fff1f2; border-color: #fecdd3; }
.action-wait { background: #fffbeb; border-color: #fde68a; }
.action-break { background: #eff6ff; border-color: #93c5fd; }

.action-label { font-size: 0.78rem; font-weight: 900; letter-spacing: 0.05em; }
.action-price { font-size: 1.35rem; font-weight: 950; margin-top: 5px; color: #111827; }
.action-desc { font-size: 0.82rem; color: #334155; margin-top: 6px; line-height: 1.4; font-weight: 600; }

.price-map { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 16px; padding: 16px 18px; }
.price-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f1f5f9; }
.price-row:last-child { border-bottom: none; }
.price-name { font-size: 0.85rem; font-weight: 800; color: #475569; }
.price-number { font-size: 1.02rem; font-weight: 950; }

.score-breakdown { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 14px; padding: 14px 16px; height: 100%; display: flex; flex-direction: column; justify-content: center; }
.score-line { display: flex; justify-content: space-between; padding: 5px 0; font-size: 0.82rem; border-bottom: 1px dashed #e2e8f0; }
.score-line:last-child { border-bottom: none; }
.score-line-label { color: #475569; font-weight: 700; }
.score-line-value { font-weight: 950; color: #111827; }

.theme-card { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 14px; padding: 15px; }
.theme-rank { color: #2563eb; font-size: 0.74rem; font-weight: 900; letter-spacing: 0.06em; }
.theme-name { color: #111827; font-size: 1.1rem; font-weight: 900; margin-top: 4px; }

div[data-testid="stExpander"] { border: 1px solid #cbd5e1 !important; border-radius: 14px !important; background: #ffffff !important; overflow: hidden; }
.stButton > button { border-radius: 12px !important; font-weight: 900 !important; min-height: 44px !important; font-size: 0.95rem !important; }
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
    if score >= 80: label = "강한 상승세 (매우 양호)"
    elif score >= 65: label = "상승 우세 (관심 영역)"
    elif score >= 45: label = "중립 및 관망 (박스권)"
    elif score >= 30: label = "조정 국면 (지지 확인)"
    else: label = "약세 및 하락 주의"
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

    return {"가격 > MA20 (추세)": t_p, "MA20 > MA60 (정배열)": m_p, "RSI (모멘텀)": r_p, "MACD (수급신호)": mc_p, "거래량 (유입)": v_p, "기본점수": 20}

def detect_patterns(df, supports, resistances):
    x = df.iloc[-1]
    close, ma20, ma60, rsi = float(x["Close"]), x["MA20"], x["MA60"], x["RSI"]
    macd, sig, vol = x["MACD"], x["MACD_Signal"], x["Vol_Ratio"]
    recent20_high = float(df.iloc[-21:-1]["High"].max()) if len(df) >= 22 else float(df["High"].max())
    patterns = []

    if pd.notna(ma20) and pd.notna(ma60) and pd.notna(rsi):
        if ma20 * 0.985 <= close <= ma20 * 1.025 and ma20 > ma60 and 42 <= rsi <= 65:
            patterns.append("💡 눌림목 매수 관심 구간")
    if close > recent20_high and vol >= 1.3 and pd.notna(macd) and macd > sig:
        patterns.append("🚀 강력한 저항선 돌파 발생")
    if pd.notna(rsi) and rsi >= 70:
        patterns.append("⚠️ 단기 과열 구간 (주의 필요)")
    if pd.notna(ma20) and close < ma20 and pd.notna(macd) and macd < sig:
        patterns.append("🔻 단기 추세 약화 및 조정")

    if not patterns:
        patterns.append("📈 차분한 우상향 안정세" if (pd.notna(ma20) and close > ma20) else "💤 방향성 없는 횡보 및 관망")
    return patterns

def chase_risk(df):
    x = df.iloc[-1]
    close, ma20, rsi, vol = float(x["Close"]), x["MA20"], x["RSI"], x["Vol_Ratio"]
    risk, reasons = 0, []

    if pd.notna(rsi) and rsi >= 70: risk += 40; reasons.append("RSI 지표가 70을 넘는 과열권입니다.")
    if pd.notna(ma20) and close > ma20 * 1.05: risk += 30; reasons.append("20일 이동평균선과 이격도가 너무 벌어졌습니다.")
    if pd.notna(vol) and vol >= 2.0: risk += 20; reasons.append("평소 대비 거래량이 급증하여 변동성이 큽니다.")

    risk = min(100, risk)
    if risk >= 60: label, cls = "높음 (추격 자제)", "signal-bad"
    elif risk >= 30: label, cls = "주의 (분할 접근)", "signal-warn"
    else: label, cls = "낮음 (안정적)", "signal-good"
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
        st_title, b_g, s_g, w_g = "급등에 따른 과열 구간입니다. 무리한 추격 매수보다는 20일선 부근까지의 조정을 기다리세요.", f"지지선인 {s1:,.0f}원 부근 안착 여부를 확인하고 분할 매수를 고려합니다.", f"상단 {r1:,.0f}~{r2:,.0f}원 구간은 차익실현 압력이 강할 수 있습니다.", f"핵심 지지선인 {s1:,.0f}원이 이탈하는지 모니터링하세요."
    elif "🚀 강력한 저항선 돌파" in patterns:
        st_title, b_g, s_g, w_g = "직전 고점 저항선을 거래량을 동반하여 강하게 돌파했습니다. 추세 연장 가능성이 높습니다.", f"돌파된 저항선이 새로운 지지선({r1:,.0f}원)으로 작용하는지 테스트합니다.", f"다음 주요 저항선인 {r2:,.0f}원 도달 시 흐름을 점검합니다.", f"돌파 후 다시 가격이 안으로 밀려 내려오는지(이탈 여부) 확인합니다."
    elif "💡 눌림목 매수 관심" in patterns:
        st_title, b_g, s_g, w_g = "상승 추세 속에서 자연스러운 가격 조정(눌림목)이 진행 중인 매력적인 구간입니다.", f"현재가 및 {s1:,.0f}원 부근에서 분할 관점의 접근이 유리합니다.", f"반등 시 {r1:,.0f}원이 단기 목표가이자 저항선이 됩니다.", f"지지선인 {s2:,.0f}가 무너지면 리스크 관리가 필요합니다."
    elif "🔻 단기 추세 약화" in patterns:
        st_title, b_g, s_g, w_g = "단기 모멘텀이 둔화되면서 주요 이동평균선 아래로 내려온 조정 국면입니다.", f"하단 지지선({s1:,.0f}원)에서 매수세가 유입되는지 확인이 필요합니다.", f"반등 시 단기 이평선({r1:,.0f}원) 돌파 여부를 체크하세요.", f"추가 하락 시 {s2:,.0f}원 부근까지 열려있음에 유의하세요."
    else:
        st_title, b_g, s_g, w_g = "현재 뚜렷한 방향성 없이 박스권 내에서 등락을 거듭하고 있는 관망 구간입니다.", f"하단 지지 라인({s1:,.0f}원) 부근에서의 반등을 노립니다.", f"상단 저항 라인({r1:,.0f}원) 부근에서는 비중을 조절합니다.", f"박스권 이탈 여부를 차분히 지켜보세요."

    return st_title, b_g, s_g, w_g, s1, s2, r1, r2

def score_details(df):
    x = df.iloc[-1]
    close, ma20, ma60, rsi, macd, sig, vol = float(x["Close"]), x["MA20"], x["MA60"], x["RSI"], x["MACD"], x["MACD_Signal"], x["Vol_Ratio"]
    
    trend = "강세 (정배열)" if (pd.notna(ma20) and pd.notna(ma60) and close > ma20 and ma20 > ma60) else "중립 및 혼조"
    rsi_state = "과열권 (매도우위)" if (pd.notna(rsi) and rsi >= 70) else ("침체권 (저가메리트)" if (pd.notna(rsi) and rsi <= 30) else ("상승 탄력" if (pd.notna(rsi) and rsi >= 50) else "약세 흐름"))
    macd_state = "상승 확장" if (pd.notna(macd) and pd.notna(sig) and macd > sig) else "하락 둔화"
    volume_state = "데이터 부족" if pd.isna(vol) else ("거래량 대폭 유입" if vol >= 1.5 else ("평균 이상 거래" if vol >= 1.0 else "거래량 감소 (한산)"))
    return trend, rsi_state, macd_state, volume_state

def make_main_chart(df, supports, resistances):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.035, row_heights=[0.62, 0.20, 0.18])

    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], increasing_line_color="#16a34a", decreasing_line_color="#dc2626", name="가격"), row=1, col=1)

    for col, color in [("MA5", "#f59e0b"), ("MA20", "#2563eb"), ("MA60", "#16a34a"), ("MA120", "#7c3aed")]:
        if col in df:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], line=dict(color=color, width=1.8), name=col), row=1, col=1)

    for i, item in enumerate(supports[:2], 1):
        fig.add_hline(y=item["price"], row=1, col=1, line_dash="dot", line_color="#16a34a", annotation_text=f"지지 S{i}", annotation_position="bottom left")
    for i, item in enumerate(resistances[:2], 1):
        fig.add_hline(y=item["price"], row=1, col=1, line_dash="dash", line_color="#dc2626", annotation_text=f"저항 R{i}", annotation_position="top left")

    volume_colors = ["#16a34a" if c >= o else "#dc2626" for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], marker_color=volume_colors, name="거래량"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], line=dict(color="#2563eb", width=2.0), name="RSI"), row=3, col=1)

    fig.add_hline(y=70, row=3, col=1, line_dash="dot", line_color="#dc2626")
    fig.add_hline(y=30, row=3, col=1, line_dash="dot", line_color="#16a34a")

    fig.update_layout(
        height=680, margin=dict(l=4, r=4, t=8, b=8), template="plotly_white",
        showlegend=False, xaxis_rangeslider_visible=False, dragmode="zoom",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial", size=12, color="#334155")
    )
    fig.update_xaxes(showgrid=False, rangeslider=dict(visible=False))
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0", fixedrange=False)
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
                reasons.append("MACD 골든크로스 발생"); score_add += 35
            if pd.notna(x["Vol_Ratio"]) and x["Vol_Ratio"] >= 1.3 and x["Close"] > prev["Close"]:
                reasons.append("거래량 동반 상승"); score_add += 30
            if pd.notna(x["MA20"]) and 0.98 <= x["Close"] / x["MA20"] <= 1.02:
                reasons.append("20일 이동평균선 지지"); score_add += 25

            item_score = min(100, 50 + score_add)
            theme_total_score += item_score
            top_gems.append({
                "code": code, "name": name, "price": float(x["Close"]), "change": change,
                "reasons": (reasons if reasons else ["안정적인 우상향 흐름"]), "score": item_score
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
    <div class="brand-main">프리미엄 금융 대시보드</div>
    <div class="brand-sub">정밀 기술적 분석 · 모멘텀 진단 · 지지/저항 실시간 매핑</div>
</div>
""", unsafe_allow_html=True)

tab_analysis, tab_market = st.tabs(["📊 개별 종목 분석 (ETF RADAR)", "🔥 시장 테마 스캔 (MARKET RADAR)"])

# ------------------------------------------------------------
# TAB 1 : ETF RADAR
# ------------------------------------------------------------
with tab_analysis:
    watchlist = st.session_state.watchlist

    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        keyword_input = st.text_input("종목 검색", placeholder="ETF명 또는 종목코드 6자리 입력", label_visibility="collapsed", key="ind_search")
    with search_col2:
        search_add_btn = st.button("＋ 종목저장", use_container_width=True, key="ind_save_btn")

    if search_add_btn and keyword_input:
        with st.spinner("네이버 금융에서 ETF를 검색 중입니다..."):
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
                        "theme": "신규 등록 종목", "cycle": "탐색 구간",
                        "desc": f"{found_name} 실시간 추종 ETF", "long_view": "중장기 주가 흐름과 기초자산 모멘텀을 꾸준히 확인하세요."
                    }
                    save_json_file(THEME_FILE, st.session_state.theme_info)
                st.success(f"'{found_name}' 종목이 관심 목록에 저장되었습니다.")
                st.rerun()
            else:
                st.error("입력하신 검색어에 해당하는 ETF를 찾지 못했습니다. 정확한 명칭이나 코드를 입력해주세요.")

    options = list(watchlist.values())
    if not options:
        st.warning("등록된 관심종목이 없습니다. 위 검색창에서 종목을 추가해 주세요.")
        st.stop()

    c1, c2 = st.columns([2.2, 1])
    with c1:
        selected = st.selectbox("관심 ETF 선택", options, label_visibility="collapsed")
    with c2:
        period = st.selectbox("분석 기간", ["6m", "1y", "2y"], index=1, label_visibility="collapsed")

    symbol_input = next(k for k, v in watchlist.items() if v == selected)

    with st.spinner("선택된 종목의 시세 및 기술 지표를 계산 중입니다..."):
        raw_df, code = load_etf_data(symbol_input, period)

    if raw_df is None:
        st.error("해당 종목의 데이터를 불러오는 데 실패했습니다. 네트워크 상태나 코드를 다시 확인해 주세요.")
        st.stop()

    df = calculate_indicators(raw_df).dropna(subset=["Close"]).copy()
    if len(df) < 20:
        st.error("분석을 수행하기에 데이터가 충분하지 않습니다.")
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
                <div class="hero-code">종목코드: {code}</div>
            </div>
            <div class="hero-mini">
                <div class="hero-mini-label">기술 점수</div>
                <div class="hero-mini-value">{score}점</div>
            </div>
        </div>
        <div class="hero-price">{price:,.0f} <span class="hero-unit">원</span></div>
        <div class="hero-change" style="color:{change_color};">
            {"▲" if change >= 0 else "▼"} {abs(change):.2f}% 전일 대비
            <span style="color:#64748b; font-size:0.8rem; margin-left:8px; font-weight:600;">최근 거래일 종가 기준</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # SCORE + SCORE BREAKDOWN (나란히 배치)
    st.markdown("""
    <div class="section-head">
        <div class="section-title">📊 기술 점수 및 세부 산출 내역</div>
        <div class="section-caption">Technical Score Breakdown</div>
    </div>
    """, unsafe_allow_html=True)

    score_col, breakdown_col = st.columns([0.45, 0.55])
    with score_col:
        score_color = "#16a34a" if score >= 65 else ("#d97706" if score >= 45 else "#dc2626")
        st.markdown(f"""
        <div class="score-card">
            <div class="score-number" style="color:{score_color};">{score}</div>
            <div class="score-denom">/ 100점 만점</div>
            <div class="score-label">{score_label}</div>
        </div>
        """, unsafe_allow_html=True)

    with breakdown_col:
        breakdown_html = "".join([f'<div class="score-line"><div class="score-line-label">{l}</div><div class="score-line-value">+{v}점</div></div>' for l, v in score_breakdown.items()])
        st.markdown(f"""
        <div class="score-breakdown">
            <div class="card-title" style="margin-bottom:6px;">항목별 가점 내역</div>
            {breakdown_html}
        </div>
        """, unsafe_allow_html=True)

    # COMBINED MARKET DIAGNOSIS & MOMENTUM SUMMARY (통합 진단)
    st.markdown("""
    <div class="section-head">
        <div class="section-title">🔍 종합 시장 진단 및 핵심 모멘텀</div>
        <div class="section-caption">Unified Market & Momentum Analysis</div>
    </div>
    """, unsafe_allow_html=True)

    if rsi >= 70: rsi_desc = "과열 구간 (차익실현 주의)"
    elif rsi <= 30: rsi_desc = "침체 구간 (반등 대기)"
    else: rsi_desc = "건강한 모멘텀 유지"

    if vol_ratio >= 1.5: vol_desc = "거래량 대폭 유입"
    elif vol_ratio >= 1.0: vol_desc = "평균 이상 활발한 거래"
    else: vol_desc = "거래량 다소 한산함"

    macd_hist = float(x["MACD_Hist"])
    macd_arrow = "▲" if macd_hist > 0 else "▼"
    macd_desc = "수급 확장 및 상승 우세" if macd_hist > 0 else "수급 둔화 및 조정 압력"

    st.markdown(f"""
    <div class="card">
        <div class="signal-grid" style="margin-top:0;">
            <div class="signal">
                <div class="signal-title">추세 방향</div>
                <div class="signal-value {'signal-good' if '강세' in trend_state else 'signal-warn'}">{trend_state}</div>
            </div>
            <div class="signal">
                <div class="signal-title">상대강도 (RSI)</div>
                <div class="signal-value">{rsi:.0f} · {rsi_desc}</div>
            </div>
            <div class="signal">
                <div class="signal-title">수급 모멘텀 (MACD)</div>
                <div class="signal-value {'signal-good' if '확장' in macd_state else 'signal-bad'}">{macd_arrow} {macd_state} ({macd_desc})</div>
            </div>
            <div class="signal">
                <div class="signal-title">거래량 동향</div>
                <div class="signal-value">{vol_ratio:.1f}x · {vol_desc}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # TODAY SIGNAL
    st.markdown("""
    <div class="section-head">
        <div class="section-title">🎯 금일 핵심 투자 가이드 및 패턴 분석</div>
        <div class="section-caption">Actionable Insight</div>
    </div>
    """, unsafe_allow_html=True)

    pattern_main = patterns[0]
    pattern_desc = "현재 이동평균선과 보조지표를 바탕으로 단기 추세의 지속 여부를 타진하는 구간입니다."
    if "눌림목" in pattern_main:
        pattern_desc = "중장기 상승 추세가 꺾이지 않은 채, 주가가 20일 이동평균선 부근까지 건전하게 조정을 받은 후 반등을 시도하는 유리한 맥락입니다."
    elif "돌파" in pattern_main:
        pattern_desc = "직전 고점이나 강력한 저항 라인을 거래량 수반과 함께 상향 돌파했습니다. 매수세가 집중되어 있어 추가 상승 탄력이 기대됩니다."
    elif "과열" in pattern_main:
        pattern_desc = "단기간 가격이 가파르게 상승하여 RSI 등 지표가 과열 영역에 진입했습니다. 추격 매수보다는 충분한 가격 조정을 기다리는 것이 안전합니다."
    elif "약화" in pattern_main:
        pattern_desc = "단기 상승 동력이 약화되면서 주요 지지선 테스트가 진행되고 있습니다. 리스크 관리에 무게를 두어야 하는 국면입니다."

    st.markdown(f"""
    <div class="pattern-box">
        <div class="pattern-title">현재 시장 패턴 해석</div>
        <div class="pattern-main">{pattern_main}</div>
        <div class="pattern-desc">{pattern_desc}</div>
        <div style="margin-top:12px; color:#1e3a8a; font-size:0.88rem; font-weight:800; border-top:1px solid #bfdbfe; padding-top:10px;">💡 대응 전략: {status_title}</div>
    </div>
    """, unsafe_allow_html=True)

    # PRICE ZONES
    st.markdown("""
    <div class="section-head">
        <div class="section-title">📍 주요 가격대별 대응 전략 (Price Zones)</div>
        <div class="section-caption">Support & Resistance Strategy</div>
    </div>
    """, unsafe_allow_html=True)

    z1, z2 = st.columns(2)
    with z1:
        st.markdown(f"""
        <div class="action-card action-buy">
            <div class="action-label" style="color:#15803d;">🟢 1차 지지 / 관심 영역</div>
            <div class="action-price">{s1:,.0f}원</div>
            <div class="action-desc">{buy_guide}</div>
        </div>
        """, unsafe_allow_html=True)
    with z2:
        st.markdown(f"""
        <div class="action-card action-sell">
            <div class="action-label" style="color:#dc2626;">🔴 1차 저항 / 차익실현</div>
            <div class="action-price">{r1:,.0f}원</div>
            <div class="action-desc">{sell_guide}</div>
        </div>
        """, unsafe_allow_html=True)

    z3, z4 = st.columns(2)
    with z3:
        st.markdown(f"""
        <div class="action-card action-wait">
            <div class="action-label" style="color:#b45309;">🟡 2차 핵심 지지선</div>
            <div class="action-price">{s2:,.0f}원</div>
            <div class="action-desc">{wait_guide}</div>
        </div>
        """, unsafe_allow_html=True)
    with z4:
        st.markdown(f"""
        <div class="action-card action-break">
            <div class="action-label" style="color:#1d4ed8;">🔵 상단 돌파 목표가</div>
            <div class="action-price">{r2:,.0f}원+</div>
            <div class="action-desc">해당 가격대 안착 시 추가 상승 랠리 가능성 열림</div>
        </div>
        """, unsafe_allow_html=True)

    # CHASE RISK
    st.markdown("""
    <div class="section-head">
        <div class="section-title">⚠️ 추격 매수 위험도 진단 (Chase Risk)</div>
        <div class="section-caption">Overheating Warning</div>
    </div>
    """, unsafe_allow_html=True)

    risk_text = " · ".join(chase_reasons) if chase_reasons else "현재 가격대에서는 단기 과열이나 이격도 확대에 따른 추격 매수 위험이 낮습니다. 안정적인 분할 접근이 가능합니다."
    risk_bg = "#fff1f2" if chase_score >= 60 else ("#fffbeb" if chase_score >= 30 else "#f0fdf4")
    risk_bd = "#fecdd3" if chase_score >= 60 else ("#fde68a" if chase_score >= 30 else "#bbf7d0")

    st.markdown(f"""
    <div style="background:{risk_bg}; border:1px solid {risk_bd}; border-radius:16px; padding:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="color:#475569; font-size:0.78rem; font-weight:850;">추격 매수 위험 평가</div>
                <div style="font-size:1.18rem; font-weight:950; margin-top:3px; color:#111827;">위험도 수준: {chase_label}</div>
            </div>
            <div style="font-size:1.5rem; font-weight:950; color:#0f172a;">{chase_score}점</div>
        </div>
        <div style="color:#334155; font-size:0.84rem; margin-top:10px; line-height:1.4; font-weight:600;">진단 사유: {risk_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # PRICE MAP
    st.markdown("""
    <div class="section-head">
        <div class="section-title">🗺 실시간 가격 맵핑 (Price Map)</div>
        <div class="section-caption">Key Levels Reference</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="price-map">
        <div class="price-row"><div class="price-name">R2 · 2차 상단 저항선</div><div class="price-number" style="color:#dc2626;">{r2:,.0f}원</div></div>
        <div class="price-row"><div class="price-name">R1 · 1차 단기 저항선</div><div class="price-number" style="color:#dc2626;">{r1:,.0f}원</div></div>
        <div class="price-row" style="background:#eff6ff; margin:0 -10px; padding-left:10px; padding-right:10px; border-radius:8px;">
            <div class="price-name" style="font-weight:900; color:#1d4ed8;">NOW · 현재 종가</div><div class="price-number" style="color:#2563eb; font-size:1.1rem;">{price:,.0f}원</div>
        </div>
        <div class="price-row"><div class="price-name">S1 · 1차 주요 지지선</div><div class="price-number" style="color:#16a34a;">{s1:,.0f}원</div></div>
        <div class="price-row"><div class="price-name">S2 · 2차 핵심 지지선</div><div class="price-number" style="color:#16a34a;">{s2:,.0f}원</div></div>
    </div>
    """, unsafe_allow_html=True)

    # CHART (스크롤 및 확대/축소 개선)
    st.markdown("""
    <div class="section-head">
        <div class="section-title">📈 프리미엄 차트 분석 (Price Action)</div>
        <div class="section-caption">Candlestick · MA · Volume · RSI</div>
    </div>
    """, unsafe_allow_html=True)

    fig = make_main_chart(df, supports, resistances)
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True, "displayModeBar": True, "scrollZoom": True}, key=f"main_chart_{symbol_input}_{period}")

    # DETAIL TABS
    detail_tabs = st.tabs(["📍 매물대 분포", "🏛 테마 및 중장기 관점", "📖 지표 가이드 및 산정기준"])

    with detail_tabs[0]:
        st.markdown("#### 최근 120거래일 매물대 집중 구간")
        st.markdown("주가가 오랫동안 머물며 거래가 집중된 가격대는 향후 주가 하락 시 강력한 방어선(지지) 혹은 상승 시 저항으로 작용합니다.")
        if not vp.empty:
            vp_show = vp.head(7)[["price", "ratio"]].copy()
            vp_show["가격대"] = vp_show["price"].map(lambda x: f"{x:,.0f}원")
            vp_show["거래 집중도"] = vp_show["ratio"].map(lambda x: f"{x * 100:.1f}%")
            st.dataframe(vp_show[["가격대", "거래 집중도"]], use_container_width=True, hide_index=True)

        st.markdown("#### 주요 지지 및 저항 레벨 상세")
        sc, rc = st.columns(2)
        with sc:
            st.markdown("**🟢 주요 지지 라인 (Support)**")
            for i, item in enumerate(supports[:3], 1):
                st.success(f"지지 S{i} : {item['price']:,.0f}원 (신뢰도 높음)")
        with rc:
            st.markdown("**🔴 주요 저항 라인 (Resistance)**")
            for i, item in enumerate(resistances[:3], 1):
                st.warning(f"저항 R{i} : {item['price']:,.0f}원 (매물 출현 가능)")

    with detail_tabs[1]:
        theme_info = st.session_state.theme_info.get(code, {
            "theme": "미등록 테마", "cycle": "탐색 구간", "desc": "상세 테마 설명이 등록되지 않았습니다.", "long_view": "기초 자산의 산업 성장성을 바탕으로 중장기 분할 매수를 검토하세요."
        })
        st.markdown(f"""
        <div class="card">
            <div class="card-title">소속 테마 및 산업 사이클</div>
            <div style="font-size:1.2rem; font-weight:900; margin-top:6px; color:#0f172a;">{theme_info["theme"]}</div>
            <div style="margin-top:8px; color:#2563eb; font-weight:900; font-size:0.85rem;">현재 사이클: {theme_info["cycle"]}</div>
            <div style="margin-top:10px; color:#334155; font-size:0.85rem; line-height:1.6;"><b>테마 특징:</b> {theme_info["desc"]}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="action-card action-break">
            <div class="action-label" style="color:#1d4ed8;">📌 중장기 투자 관점 (Long-Term View)</div>
            <div style="margin-top:6px; font-size:0.85rem; line-height:1.6; color:#1e293b; font-weight:600;">{theme_info["long_view"]}</div>
        </div>
        """, unsafe_allow_html=True)

    with detail_tabs[2]:
        st.markdown("#### 종합 기술 점수 산정 기준")
        st.markdown("현재 종목의 기술적 건강 상태를 정량화하기 위해 아래 5가지 요소를 종합하여 100점 만점으로 환산합니다.")
        breakdown_html_tab = "".join([f'<div class="score-line"><div class="score-line-label">{l}</div><div class="score-line-value">+{v}점</div></div>' for l, v in score_breakdown.items()])
        st.markdown(f'<div class="score-breakdown">{breakdown_html_tab}</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ---
        #### 💡 주요 보조지표 해석 가이드
        * **RSI (상대강도지수):** 
          - **70 이상:** 매수세가 과도하게 유입된 과열 국면 (단기 차익실현 주의)
          - **50 ~ 70:** 상승 에너지가 우세한 건강한 모멘텀 구간
          - **30 이하:** 주가가 과도하게 하락한 침체 국면 (중장기 분할 접근 검토)
        * **MACD (이동평균수렴확산):** 
          - MACD선이 시그널선을 상향 돌파(골든크로스)하고 히스토그램이 양(+)일 때 수급 모멘텀이 가장 강력합니다.
        * **거래량 비율 (Vol Ratio):** 
          - 20일 평균 거래량 대비 **1.5배 이상** 터지며 주가가 상승할 때 진짜 주포(기관/외인)의 수급 유입으로 해석합니다.
        * **이동평균선 배열:** 
          - 주가가 20일선 위에 위치하고 20일선이 60일선보다 위에 있는 정배열 상태일 때 추세 추종 매매가 유리합니다.
        """)

    with st.expander("⚙ 관심종목 관리 설정"):
        st.markdown("현재 보고 계신 ETF를 관심 목록에서 삭제할 수 있습니다.")
        if st.button("🗑 현재 종목 관심목록에서 삭제", use_container_width=True):
            del st.session_state.watchlist[symbol_input]
            save_json_file(WATCHLIST_FILE, st.session_state.watchlist)
            st.success("종목이 삭제되었습니다.")
            st.rerun()


# ------------------------------------------------------------
# TAB 2 : MARKET RADAR
# ------------------------------------------------------------
with tab_market:
    st.markdown("""
    <div class="card">
        <div class="card-title">MARKET RADAR · 시장 전반 모멘텀 스캔</div>
        <div style="font-size:1.25rem; font-weight:900; margin-top:4px; color:#0f172a;">주요 ETF 테마군 실시간 순위 탐색</div>
        <div style="color:#334155; font-size:0.85rem; line-height:1.6; margin-top:8px; font-weight:600;">
            국내 주요 연금 계좌 및 DC형 퇴직연금 투자 가능 ETF 풀을 대상으로, 각 테마별 수급 모멘텀과 기술적 활성화 점수를 실시간 스캔하여 현재 가장 주목받는 주도 테마를 찾아냅니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 시장 테마 모멘텀 전체 스캔 실행", use_container_width=True, type="primary", key="auto_scan_btn"):
        st.cache_data.clear()

    with st.spinner("전체 연금 ETF 풀의 기술적 지표를 전수 분석 중입니다. 잠시만 기다려주세요..."):
        leading_themes = scan_market_leading_themes()

    if leading_themes:
        top_theme = leading_themes[0]
        top_change_color = "#16a34a" if top_theme["avg_change"] >= 0 else "#dc2626"

        st.markdown(f"""
        <div class="hero">
            <div class="card-title">👑 현재 시장 최고 주도 테마 (TOP 1)</div>
            <div style="font-size:1.35rem; font-weight:950; margin-top:5px; color:#0f172a;">{top_theme["theme_name"]}</div>
            <div style="display:flex; align-items:end; justify-content:space-between; margin-top:12px;">
                <div>
                    <div style="color:#475569; font-size:0.76rem; font-weight:800;">테마 활성화 점수</div>
                    <div style="font-size:2.3rem; font-weight:950; color:#2563eb;">{top_theme["avg_score"]:.1f}점</div>
                </div>
                <div style="color:{top_change_color}; font-weight:950; font-size:1.02rem;">
                    평균 등락률 {"▲" if top_theme["avg_change"] >= 0 else "▼"} {abs(top_theme["avg_change"]):.2f}%
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="section-head">
            <div class="section-title">🔥 전체 테마별 모멘텀 순위 랭킹</div>
            <div class="section-caption">Theme Momentum Ranking</div>
        </div>
        """, unsafe_allow_html=True)

        for rank, th in enumerate(leading_themes, 1):
            th_change_color = "#16a34a" if th["avg_change"] >= 0 else "#dc2626"
            with st.expander(f"RANK {rank:02d}  ｜  {th['theme_name']}  (모멘텀 점수: {th['avg_score']:.1f}점)"):
                st.markdown(f"""
                <div class="theme-card">
                    <div class="theme-rank">THEME RANK #{rank:02d}</div>
                    <div class="theme-name">{th["theme_name"]}</div>
                    <div style="display:flex; justify-content:space-between; align-items:end; margin-top:10px;">
                        <div>
                            <div style="color:#475569; font-size:0.74rem; font-weight:800;">테마 모멘텀 활성도</div>
                            <div style="font-size:1.4rem; font-weight:950; color:#2563eb;">{th["avg_score"]:.1f}점 / 100점</div>
                        </div>
                        <div style="color:{th_change_color}; font-weight:900; font-size:0.85rem;">
                            구성종목 평균 {"▲" if th["avg_change"] >= 0 else "▼"} {abs(th["avg_change"]):.2f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if th["gems"]:
                    st.markdown("**💎 해당 테마 내 기술적 우수 종목 (Top Picks)**")
                    for g in th["gems"][:5]:
                        g_color = "#16a34a" if g["change"] >= 0 else "#dc2626"
                        reasons_str = " · ".join(g["reasons"])
                        st.markdown(f"""
                        <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:14px; padding:14px; margin-top:8px;">
                            <div style="display:flex; justify-content:space-between;">
                                <div style="font-size:0.92rem; font-weight:900; color:#0f172a;">💎 {g["name"]}</div>
                                <div style="font-size:0.84rem; font-weight:950; color:{g_color};">
                                    {"▲" if g["change"] >= 0 else "▼"} {abs(g["change"]):.2f}%
                                </div>
                            </div>
                            <div style="font-size:0.78rem; color:#475569; margin-top:5px; font-weight:700;">
                                코드: {g["code"]}  ｜  현재가: {g["price"]:,.0f}원  ｜  기술 점수: <b>{g["score"]}점</b>
                            </div>
                            <div style="font-size:0.78rem; color:#1e4ed8; margin-top:6px; font-weight:800;">포착 신호: {reasons_str}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("현재 해당 테마 내에 뚜렷한 기술적 매수 신호가 포착된 종목이 없습니다.")
    else:
        st.warning("시장 테마 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")


# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div style="text-align:center; color:#64748b; font-size:0.8rem; margin-top:30px; padding-top:15px; border-top:1px solid #cbd5e1; font-weight:600;">
    ETF RADAR · Professional Mobile Financial Dashboard
</div>
""", unsafe_allow_html=True)
