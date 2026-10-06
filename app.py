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
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DEFAULT_WATCHLIST = [
    "395160",
    "487240",
    "471990",
    "133690",
    "360750",
    "458730",
]

BASE_ETFS = [
    ("395160", "KODEX AI반도체TOP2플러스"),
    ("487240", "KODEX 미국AI테크TOP10"),
    ("471990", "KODEX AI전력핵심설비"),
    ("133690", "TIGER 미국나스닥100"),
    ("360750", "TIGER 미국S&P500"),
    ("458730", "TIGER 미국배당다우존스"),
]

FALLBACK_ETFS = [
    ("091160", "KODEX 반도체"),
    ("091170", "KODEX 은행"),
    ("102110", "TIGER 200"),
    ("117700", "KODEX 건설"),
    ("139230", "TIGER 200 IT"),
    ("143850", "TIGER 미국S&P500선물(H)"),
    ("157500", "TIGER 증권"),
    ("160580", "TIGER 구리실물"),
    ("182480", "TIGER 미국MSCI리츠(합성 H)"),
    ("195930", "TIGER 일본TOPIX(합성 H)"),
    ("203780", "TIGER 미국나스닥바이오"),
    ("228790", "TIGER 화장품"),
    ("232080", "TIGER 코스닥150"),
    ("245340", "TIGER 미국다우존스30"),
    ("261220", "TIGER 미국달러선물레버리지"),
    ("261240", "TIGER 미국달러선물인버스2X"),
    ("261250", "KODEX 미국달러선물레버리지"),
    ("261270", "KODEX 미국달러선물인버스2X"),
    ("266410", "KODEX 필수소비재"),
    ("267440", "KBSTAR 미국장기국채선물레버리지"),
    ("272560", "KBSTAR 단기국공채액티브"),
    ("275750", "KBSTAR 200선물레버리지"),
    ("278240", "KBSTAR 코스닥150선물레버리지"),
    ("284430", "KODEX 200미국채혼합"),
    ("292150", "TIGER TOP10"),
    ("292500", "SOL KRX300"),
    ("292560", "TIGER 일본엔선물"),
    ("294400", "KODEX 200선물인버스2X"),
    ("300950", "KODEX 게임산업"),
    ("305720", "KODEX 2차전지산업"),
    ("307510", "TIGER 의료기기"),
    ("315930", "KODEX 미국나스닥100선물(H)"),
    ("319640", "TIGER 골드선물(H)"),
    ("322400", "HANARO e커머스"),
    ("332500", "KODEX 200TR"),
    ("333940", "TIGER 코스닥150바이오테크"),
    ("364690", "KODEX 혁신기술테마액티브"),
    ("365000", "TIGER KRX2차전지K-뉴딜"),
    ("368190", "KODEX K-신재생에너지액티브"),
    ("371460", "TIGER 차이나전기차SOLACTIVE"),
    ("381170", "TIGER 미국테크TOP10 INDXX"),
    ("385510", "KODEX K-로봇액티브"),
    ("387280", "TIGER 퓨처모빌리티액티브"),
    ("388420", "KBSTAR 비메모리반도체액티브"),
    ("394280", "TIGER 글로벌메타버스액티브"),
    ("396500", "TIGER 차이나반도체FACTSET"),
    ("396520", "TIGER 차이나항셍테크"),
    ("402970", "TIGER 미국S&P500배당귀족"),
    ("403790", "KODEX 미국반도체MV"),
    ("407830", "SOL 미국TOP5채권혼합40 Solactive"),
    ("411060", "ACE KRX금현물"),
    ("413220", "SOL 차이나태양광CSI"),
    ("419650", "PLUS 글로벌수소&차세대연료전지"),
    ("422420", "KBSTAR 2차전지액티브"),
    ("429000", "TIGER 미국S&P500배당귀족"),
    ("438900", "HANARO 글로벌백신치료제"),
    ("441640", "KODEX 미국배당프리미엄액티브"),
    ("448290", "TIGER K-방산&우주"),
    ("450910", "SOL 미국S&P500"),
    ("454910", "두산로보틱스"),
    ("457480", "ACE 테슬라밸류체인액티브"),
    ("458730", "TIGER 미국배당다우존스"),
    ("461490", "KODEX 2차전지핵심소재10"),
    ("465580", "KODEX AI반도체"),
    ("466930", "SOL 조선TOP3플러스"),
    ("468380", "KODEX AI전력핵심설비"),
    ("469150", "ACE AI반도체포커스"),
    ("469160", "ACE 미국빅테크TOP7 Plus"),
    ("469170", "TIGER AI반도체핵심공정"),
    ("469250", "TIGER 미국테크TOP10"),
    ("469530", "SOL 미국AI전력인프라"),
    ("471990", "KODEX AI전력핵심설비"),
    ("472830", "KODEX 미국AI테크TOP10타겟커버드콜"),
    ("475050", "ACE 글로벌반도체TOP4 Plus"),
    ("475150", "KODEX 글로벌전력반도체"),
    ("475300", "SOL 미국30년국채커버드콜(합성)"),
    ("475380", "KODEX 미국30년국채울트라선물(H)"),
    ("475560", "TIGER 미국30년국채커버드콜액티브(H)"),
    ("476690", "TIGER 글로벌AI&로보틱스 INDXX"),
    ("477490", "KODEX 미국AI테크TOP10타겟커버드콜"),
    ("479520", "SOL 미국AI소프트웨어"),
    ("480460", "TIGER 미국AI빅테크10"),
    ("481190", "TIGER 미국나스닥100타겟커버드콜"),
    ("482730", "TIGER 미국S&P500타겟커버드콜"),
    ("483320", "ACE 미국30년국채액티브"),
    ("484790", "TIGER 미국필라델피아반도체나스닥"),
    ("486450", "SOL 미국AI전력인프라"),
    ("487230", "KODEX 미국AI테크TOP10"),
    ("487240", "KODEX 미국AI테크TOP10"),
    ("488500", "TIGER 미국테크TOP10+10%프리미엄"),
    ("489010", "PLUS 글로벌AI인프라"),
    ("489250", "KODEX 미국AI전력핵심설비"),
    ("491010", "TIGER 글로벌AI인프라액티브"),
]

THEMES = {
    "AI 반도체": {
        "keywords": ["AI반도체", "반도체", "HBM", "AI CHIP", "AI칩", "비메모리", "메모리"],
        "seeds": ["395160", "465580", "469150", "403790"],
        "stage": "현재 주도",
    },
    "AI 소프트웨어·빅테크": {
        "keywords": ["AI", "소프트웨어", "빅테크", "테크", "나스닥", "메타버스"],
        "seeds": ["487240", "480460", "469160", "479520"],
        "stage": "현재 주도",
    },
    "데이터센터·AI 인프라": {
        "keywords": ["데이터센터", "AI인프라", "인프라", "전력", "클라우드"],
        "seeds": ["471990", "489010", "491010", "469530"],
        "stage": "다음 수혜",
    },
    "전력 인프라": {
        "keywords": ["전력", "전력인프라", "전력설비", "전선", "변압기"],
        "seeds": ["471990", "468380", "486450", "489250"],
        "stage": "다음 수혜",
    },
    "원자력": {
        "keywords": ["원자력", "원전", "원전산업", "SMR", "소형모듈원전"],
        "seeds": [],
        "stage": "관심 확대",
    },
    "냉각·열관리": {
        "keywords": ["냉각", "열관리", "액침냉각", "열관리솔루션"],
        "seeds": [],
        "stage": "초기 관심",
    },
    "로봇·자율주행": {
        "keywords": ["로봇", "로보틱스", "자율주행", "모빌리티"],
        "seeds": ["385510", "476690", "387280"],
        "stage": "관심 확대",
    },
    "방산·우주": {
        "keywords": ["방산", "우주", "항공", "미사일", "방위산업"],
        "seeds": ["448290"],
        "stage": "관심 확대",
    },
    "2차전지·ESS": {
        "keywords": ["2차전지", "이차전지", "배터리", "ESS", "전지"],
        "seeds": ["305720", "422420", "461490"],
        "stage": "관심 확대",
    },
    "신재생에너지": {
        "keywords": ["신재생", "태양광", "풍력", "수소", "연료전지"],
        "seeds": ["368190", "413220", "419650"],
        "stage": "초기 관심",
    },
    "조선": {
        "keywords": ["조선", "선박", "조선업"],
        "seeds": ["466930"],
        "stage": "관심 확대",
    },
    "금": {
        "keywords": ["골드", "금"],
        "seeds": ["411060", "319640"],
        "stage": "관심 확대",
    },
}

FUTURE_CHAIN = [
    ("AI 반도체", "현재 주도"),
    ("AI 소프트웨어·빅테크", "현재 주도"),
    ("데이터센터·AI 인프라", "다음 수혜"),
    ("전력 인프라", "다음 수혜"),
    ("원자력", "관심 확대"),
    ("냉각·열관리", "초기 관심"),
]

THEME_CHAIN = FUTURE_CHAIN

CSS = """
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.stApp {
    background: #071018;
    color: #eef4f7;
}
.block-container {
    max-width: 1500px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}
h1, h2, h3, h4 {
    color: #f5f8fa;
}
div[data-testid="stMetric"] {
    background: #0d1922;
    border: 1px solid #20313d;
    border-radius: 12px;
    padding: 8px;
}
div[data-testid="stMetricLabel"] {
    color: #8fa5b4;
}
div[data-testid="stMetricValue"] {
    color: #f2f7fa;
}
.stButton > button {
    border-radius: 10px;
    border: 1px solid #2b414f;
    background: #0d1a24;
    color: #eaf2f5;
    min-height: 42px;
}
.stButton > button:hover {
    border-color: #5c91ad;
}
div[data-baseweb="select"] > div {
    background: #0d1922;
    border-color: #29404d;
    color: #f1f5f7;
}
div[data-baseweb="select"] span {
    color: #f1f5f7 !important;
}
div[data-baseweb="select"] input {
    color: #f1f5f7 !important;
}
div[role="listbox"] {
    background: #0d1922 !important;
}
div[role="option"] {
    color: #f1f5f7 !important;
    background: #0d1922 !important;
}
div[role="option"]:hover {
    background: #17303e !important;
}
input, textarea {
    color: #f1f5f7 !important;
    background: #0d1922 !important;
}
.stTextInput label, .stSelectbox label, .stMultiSelect label {
    color: #9db1bd !important;
}
hr {
    border-color: #20313d;
}
.radar-card {
    background: linear-gradient(135deg, #0c1923, #0b151d);
    border: 1px solid #223641;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 12px;
}
.radar-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #f2f7fa;
}
.radar-sub {
    color: #91a8b5;
    font-size: 0.82rem;
}
.radar-score {
    font-size: 1.35rem;
    font-weight: 800;
    color: #8ed0ef;
}
.theme-card-lead,
.theme-card-next,
.theme-card-early {
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 12px;
    border: 1px solid #263d49;
    background: #0b1720;
}
.theme-card-lead {
    border-left: 5px solid #66b9df;
}
.theme-card-next {
    border-left: 5px solid #8dbb72;
}
.theme-card-early {
    border-left: 5px solid #c89b58;
}
.decision-board {
    background: #0b1720;
    border: 1px solid #263d49;
    border-radius: 14px;
    padding: 15px;
    margin: 10px 0 15px;
}
.today-interest-panel {
    background: linear-gradient(135deg, #101d28, #0a141c);
    border: 1px solid #314b59;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 15px;
}
.price-box {
    background: #0d1a23;
    border: 1px solid #29404d;
    border-radius: 12px;
    padding: 12px;
    margin: 6px 0;
}
.small-note {
    color: #8399a6;
    font-size: 0.78rem;
}
.badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 999px;
    background: #17303d;
    color: #a8d9ed;
    font-size: 0.75rem;
    margin-right: 4px;
}
@media (max-width: 768px) {
    .block-container {
        padding-left: 0.65rem;
        padding-right: 0.65rem;
    }
    h1 {
        font-size: 1.65rem;
    }
    h2 {
        font-size: 1.25rem;
    }
    h3 {
        font-size: 1.05rem;
    }
    div[data-testid="stMetric"] {
        padding: 6px;
    }
    .radar-card,
    .theme-card-lead,
    .theme-card-next,
    .theme-card-early,
    .decision-board,
    .today-interest-panel {
        padding: 11px;
    }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

DATA_DIR = "."
WATCHLIST_FILE = os.path.join(DATA_DIR, "watchlist.json")
HOLDINGS_FILE = os.path.join(DATA_DIR, "holdings.json")
ETF_UNIVERSE_CACHE = os.path.join(DATA_DIR, "etf_universe_cache.json")

YAHOO_SUFFIX = ".KS"

PRICE_COLUMNS = [
    "Open",
    "High",
    "Low",
    "Close",
    "Adj Close",
    "Volume",
]

INDICATOR_COLUMNS = [
    "MA20",
    "MA60",
    "MA120",
    "RSI14",
    "MACD",
    "MACD_SIGNAL",
    "BB_MID",
    "BB_UPPER",
    "BB_LOWER",
    "VOL20",
    "VOLUME_RATIO",
    "RET5",
    "RET20",
    "HIGH20",
    "LOW20",
    "HIGH60",
    "LOW60",
]

def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        if isinstance(value, str):
            value = value.replace(",", "").replace("%", "").strip()
            if not value:
                return default
        x = float(value)
        if np.isnan(x) or np.isinf(x):
            return default
        return x
    except Exception:
        return default

def safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(float(value))
    except Exception:
        return default

def safe_read_json(path, default):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def safe_write_json(path, data):
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        return True
    except Exception:
        return False

def normalize_code(code):
    if code is None:
        return ""
    s = str(code).strip()
    s = re.sub(r"\.0$", "", s)
    digits = re.sub(r"\D", "", s)
    if len(digits) == 6:
        return digits
    return s

def normalize_name(name):
    if name is None:
        return ""
    s = str(name).strip()
    s = html.unescape(s)
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def safe_etf_name(name, fallback=""):
    s = normalize_name(name)
    if not s:
        return fallback
    bad_markers = ["Ã", "Â", "ì", "ë", "í", "ê", "ï¿½"]
    if sum(s.count(x) for x in bad_markers) >= 2:
        try:
            repaired = s.encode("latin1").decode("utf-8")
            if repaired:
                s = repaired
        except Exception:
            pass
    return s or fallback

def code_to_yahoo(code):
    code = normalize_code(code)
    if not code:
        return ""
    if code.endswith(".KS"):
        return code
    return code + YAHOO_SUFFIX

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_yahoo(code, period="2y"):
    ticker = code_to_yahoo(code)
    if not ticker:
        return pd.DataFrame()
    try:
        df = yf.download(
            ticker,
            period=period,
            auto_adjust=False,
            progress=False,
            threads=False,
        )
        if df is None or df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [
                c[0] if isinstance(c, tuple) else c
                for c in df.columns
            ]
        df = df.reset_index()
        return normalize_df(df)
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_naver_history(code, count=600):
    code = normalize_code(code)
    if not code:
        return pd.DataFrame()
    url = (
        "https://fchart.stock.naver.com/sise.nhn"
        f"?symbol={code}&timeframe=day&count={count}&requestType=0"
    )
    try:
        r = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        r.raise_for_status()
        root = ET.fromstring(r.text)
        rows = []
        for item in root.findall(".//item"):
            data = item.attrib.get("data", "")
            parts = data.split("|")
            if len(parts) < 6:
                continue
            rows.append(
                {
                    "Date": pd.to_datetime(parts[0], errors="coerce"),
                    "Open": safe_float(parts[1], np.nan),
                    "High": safe_float(parts[2], np.nan),
                    "Low": safe_float(parts[3], np.nan),
                    "Close": safe_float(parts[4], np.nan),
                    "Volume": safe_float(parts[5], np.nan),
                }
            )
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        return normalize_df(df)
    except Exception:
        return pd.DataFrame()

def normalize_df(df):
    if df is None or len(df) == 0:
        return pd.DataFrame()
    out = df.copy()
    if isinstance(out.columns, pd.MultiIndex):
        out.columns = [
            c[0] if isinstance(c, tuple) else c
            for c in out.columns
        ]
    rename_map = {}
    for c in out.columns:
        cs = str(c).strip()
        low = cs.lower()
        if low in ("date", "datetime"):
            rename_map[c] = "Date"
        elif low == "open":
            rename_map[c] = "Open"
        elif low == "high":
            rename_map[c] = "High"
        elif low == "low":
            rename_map[c] = "Low"
        elif low == "close":
            rename_map[c] = "Close"
        elif low in ("adj close", "adj_close"):
            rename_map[c] = "Adj Close"
        elif low == "volume":
            rename_map[c] = "Volume"
    out = out.rename(columns=rename_map)
    if "Date" not in out.columns:
        if isinstance(out.index, pd.DatetimeIndex):
            out = out.reset_index().rename(columns={"index": "Date"})
        else:
            out["Date"] = pd.RangeIndex(len(out))
    out["Date"] = pd.to_datetime(out["Date"], errors="coerce")
    for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    if "Close" not in out.columns:
        return pd.DataFrame()
    out = out.dropna(subset=["Close"]).copy()
    out = out.sort_values("Date").drop_duplicates("Date")
    return out.reset_index(drop=True)

def load_price_data(code, period="2y"):
    code = normalize_code(code)
    if not code:
        return pd.DataFrame()
    cache = st.session_state.get("price_cache", {})
    key = f"{code}:{period}"
    if key in cache:
        return cache[key]
    df = fetch_yahoo(code, period=period)
    if df.empty:
        df = fetch_naver_history(code, count=600)
    if not df.empty:
        cache[key] = df
        st.session_state.price_cache = cache
    return df

def add_indicators(df):
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy()
    close = pd.to_numeric(out["Close"], errors="coerce")
    volume = pd.to_numeric(
        out.get("Volume", pd.Series(index=out.index, dtype=float)),
        errors="coerce",
    )
    out["MA20"] = close.rolling(20).mean()
    out["MA60"] = close.rolling(60).mean()
    out["MA120"] = close.rolling(120).mean()
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out["RSI14"] = 100 - (100 / (1 + rs))
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    out["MACD"] = ema12 - ema26
    out["MACD_SIGNAL"] = out["MACD"].ewm(span=9, adjust=False).mean()
    out["BB_MID"] = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    out["BB_UPPER"] = out["BB_MID"] + 2 * bb_std
    out["BB_LOWER"] = out["BB_MID"] - 2 * bb_std
    out["VOL20"] = volume.rolling(20).mean()
    out["VOLUME_RATIO"] = volume / out["VOL20"].replace(0, np.nan)
    out["RET5"] = close.pct_change(5) * 100
    out["RET20"] = close.pct_change(20) * 100
    out["HIGH20"] = close.rolling(20).max()
    out["LOW20"] = close.rolling(20).min()
    out["HIGH60"] = close.rolling(60).max()
    out["LOW60"] = close.rolling(60).min()
    return out

def latest_row(df):
    if df is None or df.empty:
        return {}
    return df.iloc[-1].to_dict()

def calc_trend_score(row):
    score = 0.0
    close = safe_float(row.get("Close"), 0)
    ma20 = safe_float(row.get("MA20"), 0)
    ma60 = safe_float(row.get("MA60"), 0)
    ma120 = safe_float(row.get("MA120"), 0)
    rsi = safe_float(row.get("RSI14"), 50)
    ret20 = safe_float(row.get("RET20"), 0)
    volume_ratio = safe_float(row.get("VOLUME_RATIO"), 1)
    if close > ma20 > 0:
        score += 20
    if close > ma60 > 0:
        score += 20
    if close > ma120 > 0:
        score += 15
    if ma20 > ma60 > 0:
        score += 15
    if ret20 > 0:
        score += min(15, ret20 * 0.75)
    if 45 <= rsi <= 70:
        score += 10
    elif rsi > 70:
        score += 5
    if volume_ratio >= 1.2:
        score += 5
    return min(100, max(0, score))

def calc_risk_score(row):
    score = 0.0
    close = safe_float(row.get("Close"), 0)
    ma20 = safe_float(row.get("MA20"), 0)
    ma60 = safe_float(row.get("MA60"), 0)
    rsi = safe_float(row.get("RSI14"), 50)
    if close < ma20 and ma20 > 0:
        score += 25
    if close < ma60 and ma60 > 0:
        score += 30
    if rsi >= 75:
        score += 20
    if rsi <= 30:
        score += 15
    if safe_float(row.get("RET20"), 0) < -10:
        score += 20
    return min(100, score)

def get_judgment(row):
    if not row:
        return "데이터 부족"
    close = safe_float(row.get("Close"), 0)
    ma20 = safe_float(row.get("MA20"), 0)
    ma60 = safe_float(row.get("MA60"), 0)
    rsi = safe_float(row.get("RSI14"), 50)
    ret20 = safe_float(row.get("RET20"), 0)
    if close <= 0:
        return "데이터 부족"
    if close < ma60 and ma60 > 0:
        return "리스크 재검토"
    if rsi >= 75:
        return "과열 주의"
    if close < ma20 and ma20 > 0 and 35 <= rsi <= 50:
        return "눌림목 대기"
    if close > ma20 > ma60 and ret20 > 0:
        return "매수 검토"
    if close > ma20 > 0:
        return "보유 유지"
    return "관찰"

def get_price_zone(row):
    if not row:
        return {}
    close = safe_float(row.get("Close"), 0)
    ma20 = safe_float(row.get("MA20"), close)
    ma60 = safe_float(row.get("MA60"), close)
    low20 = safe_float(row.get("LOW20"), close)
    high20 = safe_float(row.get("HIGH20"), close)
    return {
        "current": close,
        "support1": min(ma20, low20) if close else 0,
        "support2": min(ma60, low20) if close else 0,
        "resistance1": max(ma20, high20) if close else 0,
        "resistance2": max(ma60, high20) if close else 0,
    }

def theme_match_score(name, theme):
    text = safe_etf_name(name).upper()
    keywords = THEMES.get(theme, {}).get("keywords", [])
    if not text or not keywords:
        return 0.0
    score = 0
    for kw in keywords:
        if kw.upper() in text:
            score += 1
    return min(100.0, score * 30.0)

def infer_theme_from_name(name):
    text = safe_etf_name(name).upper()
    matches = []
    for theme, info in THEMES.items():
        score = 0
        for kw in info.get("keywords", []):
            if kw.upper() in text:
                score += 1
        if score:
            matches.append((theme, score))
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_krx_etf_master():
    urls = [
        "https://data-dbg.krx.co.kr/svc/apis/etp/etp_bydd_trd",
        "https://openapi.krx.co.kr/contents/OPP/OPPREST/ETP/etf_search.jsp",
    ]
    for url in urls:
        try:
            r = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            if r.status_code != 200:
                continue
            data = r.json()
            if isinstance(data, dict):
                rows = (
                    data.get("OutBlock_1")
                    or data.get("result")
                    or data.get("data")
                    or []
                )
                if isinstance(rows, list) and rows:
                    return pd.DataFrame(rows)
        except Exception:
            continue
    return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_naver_etf_master():
    urls = [
        "https://finance.naver.com/api/sise/etfItemList.nhn",
        "https://finance.naver.com/api/sise/etfItemList.nhn?etfType=0",
    ]
    for url in urls:
        try:
            r = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            r.raise_for_status()
            data = r.json()
            items = data.get("result", {}).get("etfItemList", [])
            if items:
                rows = []
                for item in items:
                    code = normalize_code(
                        item.get("itemcode")
                        or item.get("itemCode")
                        or item.get("code")
                    )
                    name = safe_etf_name(
                        item.get("itemname")
                        or item.get("itemName")
                        or item.get("name")
                    )
                    if code:
                        rows.append(
                            {
                                "code": code,
                                "name": name,
                            }
                        )
                if rows:
                    return pd.DataFrame(rows)
        except Exception:
            continue
    return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def load_etf_universe():
    rows = []
    for code, name in BASE_ETFS + FALLBACK_ETFS:
        rows.append(
            {
                "code": normalize_code(code),
                "name": safe_etf_name(name),
                "source": "base",
            }
        )
    base = pd.DataFrame(rows)
    krx = fetch_krx_etf_master()
    if not krx.empty:
        krx_code_col = next(
            (
                c
                for c in krx.columns
                if str(c).lower()
                in ("isu_cd", "isu_srt_cd", "symbol", "code", "ticker")
            ),
            None,
        )
        krx_name_col = next(
            (
                c
                for c in krx.columns
                if str(c).lower()
                in ("isu_nm", "isu_abbrv", "name", "etf_name")
            ),
            None,
        )
        if krx_code_col and krx_name_col:
            tmp = pd.DataFrame(
                {
                    "code": krx[krx_code_col].map(normalize_code),
                    "name": krx[krx_name_col].map(safe_etf_name),
                    "source": "krx",
                }
            )
            base = pd.concat([base, tmp], ignore_index=True)
    naver = fetch_naver_etf_master()
    if not naver.empty:
        naver = naver.copy()
        naver["code"] = naver["code"].map(normalize_code)
        naver["name"] = naver["name"].map(safe_etf_name)
        naver["source"] = "naver"
        base = pd.concat([base, naver], ignore_index=True)
    base = base.dropna(subset=["code"]).copy()
    base["code"] = base["code"].astype(str)
    base = base[base["code"].str.len() == 6]
    base = base.drop_duplicates("code", keep="first")
    base["name"] = base.apply(
        lambda r: safe_etf_name(r["name"], r["code"]),
        axis=1,
    )
    return base.sort_values(["name", "code"]).reset_index(drop=True)

def get_etf_name(universe, code):
    code = normalize_code(code)
    if universe is None or universe.empty:
        return code
    m = universe[universe["code"] == code]
    if m.empty:
        return code
    return safe_etf_name(m.iloc[0]["name"], code)

def search_etfs(universe, query):
    if universe is None or universe.empty:
        return pd.DataFrame()
    q = normalize_name(query)
    if not q:
        return universe.head(50).copy()
    code_q = normalize_code(q)
    name_mask = universe["name"].astype(str).str.contains(
        q,
        case=False,
        na=False,
        regex=False,
    )
    code_mask = universe["code"].astype(str).str.contains(
        code_q,
        case=False,
        na=False,
        regex=False,
    )
    return universe[name_mask | code_mask].head(100).copy()

def initialize_session():
    if "price_cache" not in st.session_state:
        st.session_state.price_cache = {}
    if "watchlist" not in st.session_state:
        saved = safe_read_json(
            WATCHLIST_FILE,
            DEFAULT_WATCHLIST,
        )
        if not isinstance(saved, list):
            saved = DEFAULT_WATCHLIST.copy()
        st.session_state.watchlist = [
            normalize_code(x) for x in saved if normalize_code(x)
        ]
    if "holdings" not in st.session_state:
        saved = safe_read_json(HOLDINGS_FILE, {})
        st.session_state.holdings = saved if isinstance(saved, dict) else {}
    if "selected_etf" not in st.session_state:
        st.session_state.selected_etf = DEFAULT_WATCHLIST[0]
    if "future_theme_cache" not in st.session_state:
        st.session_state.future_theme_cache = {}
    if "market_radar_cache" not in st.session_state:
        st.session_state.market_radar_cache = {}
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "미래테마"

def render_header():
    st.title("📡 ETF RADAR")
    st.caption(
        "미래테마 → 유망 ETF → 가격구간 → 시장레이더 → 최종타겟"
    )

def render_top_summary(universe):
    watchlist = st.session_state.get("watchlist", DEFAULT_WATCHLIST)
    rows = []
    for code in watchlist:
        df = load_price_data(code, period="1y")
        if df.empty:
            continue
        ind = add_indicators(df)
        row = latest_row(ind)
        row["code"] = code
        row["name"] = get_etf_name(universe, code)
        row["trend_score"] = calc_trend_score(row)
        row["risk_score"] = calc_risk_score(row)
        row["judgment"] = get_judgment(row)
        rows.append(row)
    if not rows:
        return
    st.subheader("오늘의 관심")
    cols = st.columns(min(3, len(rows)))
    for i, row in enumerate(rows[:3]):
        with cols[i]:
            st.markdown(
                f"""
                <div class="today-interest-panel">
                    <div class="radar-title">{html.escape(str(row["name"]))}</div>
                    <div class="radar-sub">{row["code"]}</div>
                    <div class="radar-score">{row["trend_score"]:.0f}</div>
                    <div>{row["judgment"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

def render_etf_analysis(universe, code=None):
    if code is None:
        code = st.session_state.get("selected_etf", DEFAULT_WATCHLIST[0])
    code = normalize_code(code)
    name = get_etf_name(universe, code)
    st.subheader("ETF 분석")
    st.markdown(
        f"### {html.escape(name)} "
        f"<span class='badge'>{code}</span>",
        unsafe_allow_html=True,
    )
    df = load_price_data(code, period="2y")
    if df.empty:
        st.warning("가격 데이터를 불러오지 못했습니다.")
        return
    ind = add_indicators(df)
    row = latest_row(ind)
    price = safe_float(row.get("Close"), 0)
    prev = safe_float(ind.iloc[-2].get("Close"), price) if len(ind) >= 2 else price
    change = price - prev
    change_pct = change / prev * 100 if prev else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("현재가", f"{price:,.0f}", f"{change:+,.0f}")
    c2.metric("등락률", f"{change_pct:+.2f}%")
    c3.metric("RSI14", f"{safe_float(row.get('RSI14'), 0):.1f}")
    c4.metric("거래량/20일", f"{safe_float(row.get('VOLUME_RATIO'), 0):.2f}x")
    score = calc_trend_score(row)
    risk = calc_risk_score(row)
    judgment = get_judgment(row)
    st.markdown(
        f"""
        <div class="decision-board">
            <b>판단</b> : {judgment}<br>
            <span class="small-note">기술점수 {score:.0f} / 위험점수 {risk:.0f}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    zone = get_price_zone(row)
    z1, z2, z3, z4, z5 = st.columns(5)
    z1.metric("현재", f"{zone['current']:,.0f}")
    z2.metric("1차 지지", f"{zone['support1']:,.0f}")
    z3.metric("2차 지지", f"{zone['support2']:,.0f}")
    z4.metric("1차 저항", f"{zone['resistance1']:,.0f}")
    z5.metric("2차 저항", f"{zone['resistance2']:,.0f}")
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.72, 0.28],
    )
    fig.add_trace(
        go.Candlestick(
            x=ind["Date"],
            open=ind["Open"],
            high=ind["High"],
            low=ind["Low"],
            close=ind["Close"],
            name="가격",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=ind["Date"],
            y=ind["MA20"],
            name="MA20",
            line=dict(width=1.4),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=ind["Date"],
            y=ind["MA60"],
            name="MA60",
            line=dict(width=1.4),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=ind["Date"],
            y=ind["Volume"],
            name="거래량",
        ),
        row=2,
        col=1,
    )
    fig.update_layout(
        height=520,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor="#071018",
        plot_bgcolor="#071018",
        font=dict(color="#dce7ec"),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h"),
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "doubleClick": "reset",
        },
    )
    with st.expander("장기·중기·단기 전략 보기", expanded=False):
        long_term = (
            "상승추세 유지" if price > safe_float(row.get("MA120"), 0)
            else "장기 추세 확인 필요"
        )
        mid_term = (
            "중기 상승" if price > safe_float(row.get("MA60"), 0)
            else "중기 조정"
        )
        short_term = (
            "단기 우위" if price > safe_float(row.get("MA20"), 0)
            else "단기 눌림"
        )
        st.markdown(
            f"""
            **장기 추세 전략**  
            {long_term}

            **중기 추세 전략**  
            {mid_term}

            **단기 가격 전략**  
            {short_term}
            """
        )

def get_theme_etfs(universe, theme, limit=20):
    if universe is None or universe.empty:
        return pd.DataFrame()
    info = THEMES.get(theme, {})
    seeds = {normalize_code(x) for x in info.get("seeds", [])}
    rows = []
    for _, r in universe.iterrows():
        code = normalize_code(r.get("code"))
        name = safe_etf_name(r.get("name"), code)
        score = theme_match_score(name, theme)
        if code in seeds:
            score += 35
        if score > 0:
            rows.append(
                {
                    "code": code,
                    "name": name,
                    "theme_score": min(100, score),
                }
            )
    if not rows:
        return pd.DataFrame(
            columns=["code", "name", "theme_score"]
        )
    out = pd.DataFrame(rows)
    return out.sort_values(
        ["theme_score", "name"],
        ascending=[False, True],
    ).head(limit)

def analyze_theme_etf(universe, code, theme):
    df = load_price_data(code, period="2y")
    if df.empty:
        return None
    ind = add_indicators(df)
    row = latest_row(ind)
    trend = calc_trend_score(row)
    risk = calc_risk_score(row)
    match = theme_match_score(
        get_etf_name(universe, code),
        theme,
    )
    ret20 = safe_float(row.get("RET20"), 0)
    rsi = safe_float(row.get("RSI14"), 50)
    volume = safe_float(row.get("VOLUME_RATIO"), 1)
    future_score = (
        match * 0.35
        + trend * 0.35
        + max(0, min(100, 50 + ret20 * 2)) * 0.15
        + min(100, volume * 50) * 0.05
        + max(0, min(100, 100 - abs(rsi - 55) * 2)) * 0.10
        - risk * 0.20
    )
    return {
        "code": code,
        "name": get_etf_name(universe, code),
        "theme": theme,
        "theme_score": match,
        "trend_score": trend,
        "risk_score": risk,
        "ret20": ret20,
        "rsi": rsi,
        "volume_ratio": volume,
        "future_theme_score": max(0, min(100, future_score)),
        "judgment": get_judgment(row),
        "row": row,
    }

def render_theme_analysis(universe, theme):
    st.markdown(
        f"#### {html.escape(theme)} ETF 분석"
    )
    etfs = get_theme_etfs(universe, theme, limit=12)
    if etfs.empty:
        st.info("해당 테마 ETF를 찾지 못했습니다.")
        return []
    results = []
    for code in etfs["code"].tolist():
        result = analyze_theme_etf(universe, code, theme)
        if result:
            results.append(result)
    if not results:
        st.info("분석 가능한 ETF가 없습니다.")
        return []
    results = sorted(
        results,
        key=lambda x: x.get("future_theme_score", 0),
        reverse=True,
    )
    for item in results:
        st.markdown(
            f"""
            <div class="radar-card">
                <div class="radar-title">
                    {html.escape(item["name"])}
                </div>
                <div class="radar-sub">
                    {item["code"]} · {item["judgment"]}
                </div>
                <div class="radar-score">
                    미래테마 {item["future_theme_score"]:.0f}
                </div>
                <div class="small-note">
                    테마 {item["theme_score"]:.0f}
                    · 추세 {item["trend_score"]:.0f}
                    · 위험 {item["risk_score"]:.0f}
                    · 20일 {item["ret20"]:+.1f}%
                    · RSI {item["rsi"]:.1f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    return results

def score_future_theme(theme, universe):
    info = THEMES.get(theme, {})
    seed_codes = [normalize_code(x) for x in info.get("seeds", [])]
    seed_results = []
    for code in seed_codes:
        result = analyze_theme_etf(universe, code, theme)
        if result:
            seed_results.append(result)
    if seed_results:
        scores = [x["future_theme_score"] for x in seed_results]
        trend = [x["trend_score"] for x in seed_results]
        ret20 = [x["ret20"] for x in seed_results]
        return {
            "theme": theme,
            "stage": info.get("stage", ""),
            "score": float(np.mean(scores)),
            "trend": float(np.mean(trend)),
            "ret20": float(np.mean(ret20)),
            "seed_count": len(seed_results),
        }
    return {
        "theme": theme,
        "stage": info.get("stage", ""),
        "score": 0.0,
        "trend": 0.0,
        "ret20": 0.0,
        "seed_count": 0,
    }

def discover_future_themes(universe):
    results = []
    for theme in THEMES:
        result = score_future_theme(theme, universe)
        results.append(result)
    out = pd.DataFrame(results)
    if out.empty:
        return out
    stage_order = {
        "현재 주도": 0,
        "다음 수혜": 1,
        "관심 확대": 2,
        "초기 관심": 3,
    }
    out["stage_order"] = out["stage"].map(
        lambda x: stage_order.get(x, 9)
    )
    out = out.sort_values(
        ["stage_order", "score", "trend"],
        ascending=[True, False, False],
    ).reset_index(drop=True)
    return out

def render_future_theme(universe):
    st.subheader("미래테마")
    st.caption(
        "현재 주도 → 다음 수혜 → 관심 확대 → 초기 관심 순으로 "
        "테마의 흐름과 ETF 후보를 찾습니다."
    )
    themes = discover_future_themes(universe)
    if themes.empty:
        st.info("미래테마 데이터를 계산할 수 없습니다.")
        return
    for _, item in themes.iterrows():
        theme = item["theme"]
        stage = item["stage"]
        score = safe_float(item.get("score"), 0)
        ret20 = safe_float(item.get("ret20"), 0)
        trend = safe_float(item.get("trend"), 0)
        cls = (
            "theme-card-lead"
            if stage == "현재 주도"
            else "theme-card-next"
            if stage in ("다음 수혜", "관심 확대")
            else "theme-card-early"
        )
        st.markdown(
            f"""
            <div class="{cls}">
                <div class="radar-title">
                    {html.escape(str(theme))}
                    <span class="badge">{html.escape(str(stage))}</span>
                </div>
                <div class="radar-score">
                    {score:.0f}
                </div>
                <div class="small-note">
                    추세 {trend:.0f} · 20일 수익률 {ret20:+.1f}%
                    · Seed {safe_int(item.get("seed_count"), 0)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            f"{theme} 유망 ETF 보기",
            key=f"theme_analysis_{theme}",
            use_container_width=True,
        ):
            st.session_state[f"theme_open_{theme}"] = not st.session_state.get(
                f"theme_open_{theme}",
                False,
            )
        if st.session_state.get(f"theme_open_{theme}", False):
            render_theme_analysis(universe, theme)

def build_market_radar(universe):
    rows = []
    if universe is None or universe.empty:
        return pd.DataFrame()
    candidates = universe["code"].dropna().astype(str).tolist()
    for code in candidates:
        df = load_price_data(code, period="1y")
        if df.empty:
            continue
        ind = add_indicators(df)
        row = latest_row(ind)
        trend = calc_trend_score(row)
        risk = calc_risk_score(row)
        ret20 = safe_float(row.get("RET20"), 0)
        ret5 = safe_float(row.get("RET5"), 0)
        volume = safe_float(row.get("VOLUME_RATIO"), 1)
        score = (
            trend * 0.45
            + max(0, min(100, 50 + ret20 * 2)) * 0.20
            + max(0, min(100, 50 + ret5 * 3)) * 0.10
            + min(100, volume * 50) * 0.10
            + max(0, 100 - risk) * 0.15
        )
        rows.append(
            {
                "code": code,
                "name": get_etf_name(universe, code),
                "score": max(0, min(100, score)),
                "trend": trend,
                "risk": risk,
                "ret5": ret5,
                "ret20": ret20,
                "volume_ratio": volume,
                "judgment": get_judgment(row),
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(
        "score",
        ascending=False,
    ).reset_index(drop=True)

def render_market_radar(universe):
    st.subheader("시장레이더")
    st.caption(
        "현재 시장에서 상승 가능성이 상대적으로 높은 ETF를 "
        "기술적 강도·수익률·거래량·위험도 기준으로 선별합니다."
    )
    radar = build_market_radar(universe)
    if radar.empty:
        st.info("시장레이더 데이터를 계산할 수 없습니다.")
        return
    top = radar.head(15)
    for _, item in top.iterrows():
        st.markdown(
            f"""
            <div class="radar-card">
                <div class="radar-title">
                    {html.escape(str(item["name"]))}
                    <span class="badge">{item["code"]}</span>
                </div>
                <div class="radar-score">
                    {safe_float(item["score"]):.0f}
                </div>
                <div class="radar-sub">
                    {item["judgment"]}
                </div>
                <div class="small-note">
                    추세 {safe_float(item["trend"]):.0f}
                    · 위험 {safe_float(item["risk"]):.0f}
                    · 5일 {safe_float(item["ret5"]):+.1f}%
                    · 20일 {safe_float(item["ret20"]):+.1f}%
                    · 거래량 {safe_float(item["volume_ratio"]):.2f}x
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def build_final_targets(universe):
    themes = discover_future_themes(universe)
    radar = build_market_radar(universe)
    if themes.empty or radar.empty:
        return pd.DataFrame()
    candidates = []
    top_themes = themes.head(8)
    for _, t in top_themes.iterrows():
        theme = t["theme"]
        etfs = get_theme_etfs(universe, theme, limit=10)
        for code in etfs["code"].tolist():
            result = analyze_theme_etf(universe, code, theme)
            if not result:
                continue
            r = radar[radar["code"] == code]
            market_score = safe_float(
                r.iloc[0]["score"], 0
            ) if not r.empty else 0
            final_score = (
                result["future_theme_score"] * 0.45
                + market_score * 0.35
                + result["trend_score"] * 0.20
            )
            candidates.append(
                {
                    "code": code,
                    "name": result["name"],
                    "theme": theme,
                    "theme_stage": t["stage"],
                    "future_theme_score": result["future_theme_score"],
                    "market_score": market_score,
                    "trend_score": result["trend_score"],
                    "risk_score": result["risk_score"],
                    "ret20": result["ret20"],
                    "rsi": result["rsi"],
                    "final_score": final_score,
                    "judgment": result["judgment"],
                }
            )
    if not candidates:
        return pd.DataFrame()
    out = pd.DataFrame(candidates)
    out = out.sort_values(
        "final_score",
        ascending=False,
    ).drop_duplicates("code")
    return out.reset_index(drop=True)

def render_final_targets(universe):
    st.subheader("최종타겟")
    st.caption(
        "미래테마의 유망도와 현재 시장 강도를 결합해 "
        "실제 관찰 우선순위가 높은 ETF를 선별합니다."
    )
    targets = build_final_targets(universe)
    if targets.empty:
        st.info("최종타겟을 계산할 수 없습니다.")
        return
    for _, item in targets.head(20).iterrows():
        st.markdown(
            f"""
            <div class="radar-card">
                <div class="radar-title">
                    {html.escape(str(item["name"]))}
                    <span class="badge">{item["code"]}</span>
                </div>
                <div class="radar-sub">
                    {html.escape(str(item["theme"]))}
                    · {html.escape(str(item["theme_stage"]))}
                    · {item["judgment"]}
                </div>
                <div class="radar-score">
                    최종 {safe_float(item["final_score"]):.0f}
                </div>
                <div class="small-note">
                    미래테마 {safe_float(item["future_theme_score"]):.0f}
                    · 시장 {safe_float(item["market_score"]):.0f}
                    · 추세 {safe_float(item["trend_score"]):.0f}
                    · 위험 {safe_float(item["risk_score"]):.0f}
                    · 20일 {safe_float(item["ret20"]):+.1f}%
                    · RSI {safe_float(item["rsi"]):.1f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_my_etf(universe):
    st.subheader("내 ETF")
    watchlist = st.session_state.get(
        "watchlist",
        DEFAULT_WATCHLIST,
    )
    if not watchlist:
        st.info("관심 ETF가 없습니다.")
        return
    selected = []
    for code in watchlist:
        name = get_etf_name(universe, code)
        selected.append(f"{code} | {name}")
    choice = st.selectbox(
        "ETF 선택",
        selected,
        key="my_etf_select",
    )
    code = normalize_code(choice.split("|")[0])
    render_etf_analysis(universe, code)
    st.divider()
    st.markdown("#### 관심 ETF 관리")
    new_code = st.text_input(
        "ETF 코드 추가",
        placeholder="예: 395160",
        key="add_watch_code",
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button(
            "관심 ETF 추가",
            use_container_width=True,
        ):
            nc = normalize_code(new_code)
            if len(nc) == 6:
                if nc not in watchlist:
                    watchlist.append(nc)
                    st.session_state.watchlist = watchlist
                    safe_write_json(WATCHLIST_FILE, watchlist)
                    st.rerun()
                else:
                    st.info("이미 등록된 ETF입니다.")
            else:
                st.warning("6자리 ETF 코드를 입력하세요.")
    with c2:
        if st.button(
            "현재 ETF 삭제",
            use_container_width=True,
        ):
            if code in watchlist:
                watchlist.remove(code)
                st.session_state.watchlist = watchlist
                safe_write_json(WATCHLIST_FILE, watchlist)
                st.rerun()

def render_search(universe):
    st.subheader("ETF 검색")
    q = st.text_input(
        "ETF 이름 또는 코드",
        key="etf_search",
        placeholder="예: AI / 반도체 / 395160",
    )
    results = search_etfs(universe, q)
    if results.empty:
        st.info("검색 결과가 없습니다.")
        return
    options = [
        f"{r['code']} | {safe_etf_name(r['name'])}"
        for _, r in results.iterrows()
    ]
    choice = st.selectbox(
        "검색 결과",
        options,
        key="search_result_select",
    )
    code = normalize_code(choice.split("|")[0])
    if st.button(
        "선택 ETF 분석",
        use_container_width=True,
    ):
        st.session_state.selected_etf = code
    render_etf_analysis(universe, code)

def render_app():
    universe = load_etf_universe()
    render_header()
    render_top_summary(universe)
    tabs = st.tabs(
        [
            "미래테마",
            "최종타겟",
            "시장레이더",
            "ETF 분석",
            "내 ETF",
            "검색",
        ]
    )
    with tabs[0]:
        render_future_theme(universe)
    with tabs[1]:
        render_final_targets(universe)
    with tabs[2]:
        render_market_radar(universe)
    with tabs[3]:
        render_etf_analysis(
            universe,
            st.session_state.get(
                "selected_etf",
                DEFAULT_WATCHLIST[0],
            ),
        )
    with tabs[4]:
        render_my_etf(universe)
    with tabs[5]:
        render_search(universe)

initialize_session()
render_app()
]
THEME_LEXICON = {
    "AI 반도체": ["반도체", "AI반도체", "AI 반도체", "HBM", "메모리", "시스템반도체", "반도체장비", "반도체소부장"],
    "로봇": ["로봇", "로보틱스", "휴머노이드", "로보틱", "스마트팩토리"],
    "방산": ["방산", "방위산업", "K방산", "국방", "우주항공방산"],
    "2차전지": ["2차전지", "이차전지", "배터리", "전고체", "양극재", "음극재", "리튬", "배터리소재"],
    "전기차": ["전기차", "EV", "전기자동차", "자율주행", "모빌리티"],
    "조선": ["조선", "조선업", "선박", "LNG선", "해운", "선박기자재"],
    "원자력": ["원자력", "원전", "SMR", "소형모듈원전", "핵융합"],
    "전력 인프라": ["전력", "전력인프라", "전력설비", "전력망", "변압기", "전선", "송배전", "전기설비"],
    "데이터센터·AI 인프라": ["데이터센터", "AI인프라", "AI 인프라", "서버", "네트워크", "클라우드", "IDC"],
    "냉각·열관리": ["냉각", "열관리", "액침냉각", "수랭", "칠러", "열교환", "냉동공조"],
    "바이오": ["바이오", "헬스케어", "제약", "신약", "항암", "면역", "의료기기", "유전체"],
    "우주항공": ["우주", "우주항공", "항공우주", "위성", "발사체", "UAM"],
    "AI 소프트웨어": ["AI", "인공지능", "생성AI", "AI소프트웨어", "소프트웨어", "빅데이터"],
    "클라우드": ["클라우드", "SaaS", "데이터센터"],
    "보안": ["보안", "사이버보안", "정보보안", "보안솔루션"],
    "5G·통신": ["5G", "6G", "통신", "네트워크", "위성통신"],
    "신재생에너지": ["태양광", "태양광발전", "풍력", "신재생", "친환경에너지", "수소"],
    "수소": ["수소", "수소경제", "수소연료전지", "연료전지"],
    "친환경·탄소": ["탄소", "탄소중립", "친환경", "ESG", "폐기물", "리사이클", "재활용"],
    "금융": ["은행", "금융", "증권", "보험", "고배당", "배당"],
    "자동차": ["자동차", "자동차부품", "차량", "모빌리티"],
    "화장품·K뷰티": ["화장품", "K뷰티", "뷰티", "미용"],
    "음식료·소비": ["음식료", "식품", "소비재", "유통", "소비"],
    "건설·인프라": ["건설", "인프라", "SOC", "건설기계", "시멘트"],
    "철강·금속": ["철강", "금속", "구리", "알루미늄", "비철금속"],
    "원자재": ["원자재", "상품", "원유", "천연가스", "커머디티"],
    "금·귀금속": ["금", "골드", "귀금속", "은", "실버"],
    "중국": ["중국", "차이나", "CSI", "홍콩", "상하이"],
    "미국 기술": ["나스닥", "미국테크", "미국기술", "S&P500", "테크"],
    "반도체 장비·소부장": ["반도체장비", "반도체장비주", "소부장", "소재부품장비", "장비"],
}
THEME_REASONS = {
    "AI 반도체":"AI 연산과 데이터 처리 수요 확대에 직접 연결되는 반도체 산업 흐름입니다.",
    "로봇":"자동화·휴머노이드·스마트팩토리 투자 확대와 연결되는 산업 흐름입니다.",
    "방산":"국방비 확대와 글로벌 방산 수요 변화에 연결되는 산업 흐름입니다.",
    "2차전지":"전기차·ESS·배터리 기술 변화와 연결되는 배터리 산업 흐름입니다.",
    "전기차":"전동화와 미래 모빌리티 투자 흐름을 추적합니다.",
    "조선":"선박 발주와 친환경·고부가 선박 수요에 연결되는 산업 흐름입니다.",
    "원자력":"원전·SMR 등 장기 전력 수요와 에너지 투자 흐름을 추적합니다.",
    "전력 인프라":"전력수요 증가와 송배전·변압기·전선 설비 투자 흐름입니다.",
    "데이터센터·AI 인프라":"AI 확산에 따른 데이터센터·서버·네트워크 투자 흐름입니다.",
    "냉각·열관리":"고집적 서버와 산업설비 확대에 따른 냉각·열관리 수요 흐름입니다.",
}
THEMES = {}
FUTURE_CHAIN = []
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
def _normalize_etf_code(code):
    code = str(code or "").strip().upper()
    if code.isdigit():
        return code.zfill(6)
    return code
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_naver_etf_master():
    """네이버 금융의 국내 ETF 전체 목록을 직접 가져옵니다."""
    url = "https://finance.naver.com/api/sise/etfItemList.nhn"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.naver.com/sise/etf.nhn"}
    try:
        r = requests.get(url, headers=headers, timeout=12)
        r.raise_for_status()
        try:
            payload = r.json()
        except Exception:
            payload = json.loads(r.content.decode("cp949", errors="ignore"))
        items = payload.get("result", {}).get("etfItemList", [])
        return {
            _normalize_etf_code(x.get("itemcode")): safe_etf_name(_normalize_etf_code(x.get("itemcode")), x.get("itemname"))
            for x in items
            if x.get("itemcode") and x.get("itemname")
        }
    except Exception:
        return {}
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_krx_etf_master():
    """KRX ETF master(MDCSTAT04601)를 직접 조회합니다. 실패하면 빈 dict를 반환합니다."""
    url = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd",
        "Origin": "https://data.krx.co.kr",
    }
    payload = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT04601",
        "locale": "ko_KR",
        "share": "1",
        "csvxls_isNo": "false",
    }
    try:
        r = requests.post(url, headers=headers, data=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
        rows = data.get("output") or data.get("OutBlock_1") or []
        result = {}
        for x in rows:
            code = _normalize_etf_code(x.get("ISU_SRT_CD") or x.get("isu_srt_cd") or x.get("ISU_CD"))
            name = x.get("ISU_ABBRV") or x.get("isu_abrv") or x.get("ISU_NM")
            if code and name:
                result[code] = safe_etf_name(code, name)
        return result
    except Exception:
        return {}
def load_etf_universe():
    """하드코딩 목록 대신 KRX/Naver 실시간 ETF master를 합칩니다."""
    krx = fetch_krx_etf_master()
    naver = fetch_naver_etf_master()
    universe = {}
    universe.update({k: v for k, v in krx.items() if v and not v.startswith("ETF ")})
    for code, name in naver.items():
        if code not in universe or not universe[code] or universe[code].startswith("ETF "):
            universe[code] = name
    return universe
def init_state():
    if "watchlist" not in st.session_state:
        saved = read_json(WATCHLIST_FILE, DEFAULT_WATCHLIST.copy())
        if isinstance(saved, list):
            st.session_state.watchlist = [_normalize_etf_code(x) for x in saved]
        else:
            st.session_state.watchlist = DEFAULT_WATCHLIST.copy()
    if "holdings" not in st.session_state:
        saved = read_json(HOLDINGS_FILE, {})
        st.session_state.holdings = saved if isinstance(saved, dict) else {}
    if "etf_universe" not in st.session_state:
        st.session_state.etf_universe = load_etf_universe()
        if not st.session_state.etf_universe:
            st.session_state.etf_universe = {}
    if "price_cache" not in st.session_state:
        st.session_state.price_cache = {}
    if "theme_cache" not in st.session_state:
        st.session_state.theme_cache = {}
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
        st.session_state.radar_mode = "🎯 유망후보"
    if "future_engine_cache" not in st.session_state:
        st.session_state.future_engine_cache = None
def _name_has_hangul(text):
    return any("가" <= ch <= "힣" for ch in str(text))
def _looks_mojibake(text):
    t = str(text)
    bad = ("Ã", "Â", "â", "ê", "ë", "ì", "í", "î", "ï", "ð", "ñ", "�", "�")
    return any(x in t for x in bad)
def safe_etf_name(code, name=None):
    code = str(code).zfill(6)
    if isinstance(name, dict):
        name = name.get("name") or name.get("etf_name") or name.get("title")
    text = html.unescape(str(name or "")).strip()
    if text.startswith("{") and "'name'" in text:
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, dict):
                text = str(parsed.get("name") or parsed.get("etf_name") or parsed.get("title") or "").strip()
        except Exception:
            m = re.search(r"['\"]name['\"]\s*:\s*['\"]([^'\"]+)['\"]", text)
            if m:
                text = m.group(1).strip()
    text = html.unescape(text).strip()
    if not text or _looks_mojibake(text) or text.startswith("{") or "'ticker'" in text or '"ticker"' in text:
        return f"ETF {code}"
    return text
def get_etf_name(code):
    code = str(code).zfill(6)
    return safe_etf_name(code, st.session_state.etf_universe.get(code))
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
                    if item_str.lower() in ["open", "high", "low", "close", "volume"]:
                        found = item_str.title()
                        break
                new_columns.append(found if found else str(col[0]))
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
    required = ["Open", "High", "Low", "Close", "Volume"]
    if not all(col in df.columns for col in required):
        return pd.DataFrame()
    df = df[required].copy()
    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Close"])
    if getattr(df.index, "tz", None) is not None:
        try:
            df.index = df.index.tz_localize(None)
        except Exception:
            pass
    return df
def fetch_naver_history(code, count=600):
    """Yahoo에서 제공하지 않는 국내 ETF/비정형 코드를 위한 Naver 가격 fallback."""
    code = _normalize_etf_code(code)
    url = f"https://fchart.stock.naver.com/sise.nhn?symbol={code}&timeframe=day&count={count}&requestType=0"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        rows = []
        for item in root.findall(".//item"):
            raw = item.attrib.get("data", "")
            parts = raw.split("|")
            if len(parts) < 6:
                continue
            rows.append(parts[:6])
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["Date", "Close"]).set_index("Date")
        return normalize_df(df)
    except Exception:
        return pd.DataFrame()
def fetch_yahoo(code):
    code = _normalize_etf_code(code)
    try:
        ticker = f"{code}.KS"
        df = yf.download(
            ticker, period="2y", interval="1d", auto_adjust=False,
            progress=False, threads=False
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
    cached = st.session_state.price_cache.get(code)
    if cached and not force:
        age = (now - cached["time"]).total_seconds()
        if age < 300:
            return cached["data"]
    df = fetch_yahoo(code)
    if not df.empty:
        st.session_state.price_cache[code] = {
            "time": now,
            "data": df
        }
    return df
def calculate_indicators(df):
    if df.empty:
        return pd.DataFrame()
    d = df.copy()
    d["MA20"] = d["Close"].rolling(20).mean()
    d["MA60"] = d["Close"].rolling(60).mean()
    d["MA120"] = d["Close"].rolling(120).mean()
    d["MA200"] = d["Close"].rolling(200).mean()
    delta = d["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta).clip(upper=0).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    d["RSI14"] = 100 - (100 / (1 + rs))
    d["VOL20"] = d["Volume"].rolling(20).mean()
    d["VOL_RATIO"] = d["Volume"] / d["VOL20"].replace(0, np.nan)
    d["RET5"] = d["Close"].pct_change(5) * 100
    d["RET20"] = d["Close"].pct_change(20) * 100
    d["RET60"] = d["Close"].pct_change(60) * 100
    d["RET120"] = d["Close"].pct_change(120) * 100
    d["RET250"] = d["Close"].pct_change(250) * 100
    d["HIGH20"] = d["High"].rolling(20).max()
    d["LOW20"] = d["Low"].rolling(20).min()
    d["HIGH60"] = d["High"].rolling(60).max()
    d["LOW60"] = d["Low"].rolling(60).min()
    return d
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
def get_judgment(d):
    if d.empty:
        return {
            "title": "데이터 부족",
            "reasons": ["가격 데이터를 확인하지 못했습니다."],
            "action": "가격 데이터를 다시 확인해 주세요.",
            "ma_state": "확인 불가",
            "rsi_state": "확인 불가",
            "vol_state": "확인 불가",
            "rsi": 0,
            "vol_ratio": 0,
            "ret20": 0
        }
    row = d.iloc[-1]
    current = safe_float(row["Close"])
    ma20 = safe_float(row["MA20"], current)
    ma60 = safe_float(row["MA60"], current)
    rsi = safe_float(row["RSI14"], 50)
    vol_ratio = safe_float(row["VOL_RATIO"], 1)
    ret20 = safe_float(row["RET20"], 0)
    above20 = current >= ma20
    above60 = current >= ma60
    ma_state = "20일선 상회" if above20 else "20일선 하회"
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
    if above20 and above60 and rsi >= 70:
        title = "상승 추세 · 추격 주의"
        action = "추세는 양호하지만 과열 가능성이 있습니다. 신규 매수는 현재가 추격보다 눌림 확인을 우선합니다."
    elif above20 and above60:
        title = "상승 추세 유지"
        action = "20일선과 60일선 위입니다. 보유자는 추세를 확인하고 신규 매수는 돌파 추격보다 눌림을 우선합니다."
    elif above60 and not above20:
        title = "단기 조정 · 중기 추세 확인"
        action = "20일선 아래지만 60일선 위입니다. 20일선 회복 여부를 확인하면서 지지구간의 거래량을 봅니다."
    elif not above60 and rsi <= 40:
        title = "중기 약세 · 방어 우선"
        action = "60일선 아래이고 RSI도 약합니다. 지지 형성과 거래량 회복을 먼저 확인합니다."
    else:
        title = "방향 확인 구간"
        action = "추세가 명확하지 않습니다. 20일선 회복 또는 최근 고점 돌파와 거래량 동반 여부를 확인합니다."
    reasons = [
        f"현재가 {money(current)} · 20일선 {money(ma20)} · {ma_state}",
        f"60일선 {money(ma60)} · {'중기 추세 유지' if above60 else '중기 추세 약화'}",
        f"RSI14 {rsi:.1f} · {rsi_state}",
        f"거래량 {vol_ratio:.2f}배 · {vol_state} · 최근 20일 {ret20:+.2f}%"
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
def leading_signal(row, benchmark_ret20=0):
    current=safe_float(row.get("Close",0)); ma20=safe_float(row.get("MA20",current),current); ma60=safe_float(row.get("MA60",current),current)
    ret5=safe_float(row.get("RET5",row.get("R5",0)),0); ret20=safe_float(row.get("RET20",row.get("R20",0)),0)
    vr=safe_float(row.get("VOL_RATIO",row.get("VR",1)),1); rsi=safe_float(row.get("RSI14",row.get("RSI",50)),50)
    dist20=(current/ma20-1)*100 if ma20 else 0; rs20=ret20-benchmark_ret20; accel=ret5-ret20/4
    early_price=92 if -1<=dist20<=3 else 82 if dist20<=5 else 65 if dist20<8 else 35
    early_rsi=92 if 48<=rsi<=62 else 84 if 43<=rsi<68 else 68 if rsi<72 else 35
    flow=92 if 1.10<=vr<=1.70 else 82 if 1.0<=vr<1.10 else 76 if 0.9<=vr<1.0 else 58 if vr<2.2 else 38
    accel_score=90 if 0.5<=accel<=5 else 78 if 0<=accel<0.5 else 68 if accel>5 else 52
    rel=88 if rs20>=6 else 80 if rs20>=3 else 70 if rs20>=0 else 48
    structure=90 if current>=ma60 and ma20>=ma60 else 78 if current>=ma60 else 55 if current>=ma20 else 35
    score=round(early_price*.22+early_rsi*.18+flow*.22+accel_score*.16+rel*.14+structure*.08)
    early_buy=score>=72 and vr>=1.05 and rsi<70 and dist20<7 and rs20>=-1
    return {"score":int(np.clip(score,0,100)),"early_buy":bool(early_buy),"rs20":rs20,"dist20":dist20,"rsi":rsi,"vr":vr,"accel":accel}
def theme_score(theme_rows, bench_ret20=0, bench_ret60=0):
    if len(theme_rows)<2: return None
    vals=[]
    for r in theme_rows:
        r20=safe_float(r.get("ret20",r.get("R20")),np.nan); r60=safe_float(r.get("ret60",r.get("R60")),np.nan)
        if pd.isna(r20) or pd.isna(r60): continue
        sig=leading_signal(r,bench_ret20)
        vals.append({"r20":r20,"r60":r60,"rs20":sig["rs20"],"rs60":r60-bench_ret60,"vr":safe_float(r.get("vr",r.get("VR",1)),1),"ma60gap":safe_float(r.get("ma60_gap",0)),"breadth":safe_float(r.get("breadth",0)),"accel":sig["accel"]})
    if len(vals)<2: return None
    df=pd.DataFrame(vals)
    breadth=(df["breadth"]>50).mean()*100
    return float(np.clip(
        df["r20"].mean()*1.8+
        df["r60"].mean()*0.8+
        df["rs20"].mean()*1.5+
        df["rs60"].mean()*0.5+
        breadth*0.18+
        df["vr"].clip(0,2).mean()*8+
        df["accel"].mean()*1.2+
        45,0,100
    ))
def _benchmark_snapshot():
    bench_codes=["069500","229200","133690"]
    vals=[]
    for code in bench_codes:
        df=load_price_data(code)
        if df.empty: continue
        d=calculate_indicators(df)
        if d.empty: continue
        r=d.iloc[-1]
        vals.append({
            "code":code,
            "ret20":safe_float(r.get("RET20"),0),
            "ret60":safe_float(r.get("RET60"),0),
            "price":safe_float(r.get("Close"),0),
        })
    if not vals:
        return {"ret20":0.0,"ret60":0.0,"price":0.0}
    return {
        "ret20":float(np.mean([x["ret20"] for x in vals])),
        "ret60":float(np.mean([x["ret60"] for x in vals])),
        "price":float(np.mean([x["price"] for x in vals])),
    }
def _find_theme_for_etf(code):
    name=get_etf_name(code)
    matches=[]
    for theme,keywords in THEME_LEXICON.items():
        score=sum(1 for k in keywords if k.lower() in name.lower())
        if score:
            matches.append((theme,score))
    if not matches:
        return None,[]
    matches.sort(key=lambda x:x[1],reverse=True)
    theme=matches[0][0]
    codes=[]
    for c,n in st.session_state.etf_universe.items():
        if any(k.lower() in str(n).lower() for k in THEME_LEXICON[theme]):
            codes.append(c)
    rows=[]
    bench=_benchmark_snapshot()
    for c in codes[:30]:
        df=load_price_data(c)
        if df.empty: continue
        d=calculate_indicators(df)
        if len(d)<65: continue
        r=d.iloc[-1]
        rows.append({
            "code":c,
            "name":get_etf_name(c),
            "close":safe_float(r.get("Close")),
            "ret20":safe_float(r.get("RET20")),
            "ret60":safe_float(r.get("RET60")),
            "ret5":safe_float(r.get("RET5")),
            "rsi":safe_float(r.get("RSI14"),50),
            "vr":safe_float(r.get("VOL_RATIO"),1),
            "ma60_gap":((safe_float(r.get("Close"))/safe_float(r.get("MA60"),safe_float(r.get("Close")))-1)*100),
            "breadth":100 if safe_float(r.get("Close"))>=safe_float(r.get("MA20"),safe_float(r.get("Close"))) else 0,
        })
    return theme,rows
def _theme_lifecycle(rows,bench):
    if not rows:
        return {"score":0.0,"state":"관찰"}
    df=pd.DataFrame(rows)
    rs20=df["ret20"]-bench.get("ret20",0)
    breadth=(df["breadth"]>50).mean()*100
    accel=df["ret5"]-df["ret20"]/4
    score=float(np.clip(
        df["ret20"].mean()*2+
        rs20.mean()*2+
        breadth*.25+
        df["vr"].clip(0,2).mean()*10+
        accel.mean()*1.5+
        35,0,100
    ))
    if score>=78: state="주도"
    elif score>=64: state="상승확산"
    elif score>=50: state="초기확대"
    elif score>=35: state="관찰"
    else: state="쇠퇴"
    return {"score":score,"state":state}
def long_term_horizon(d):
    if d.empty or len(d)<252:
        return {"score":0,"trend":"확인 불가","suitability":"데이터 부족","reason":"1년 이상의 가격 데이터가 필요합니다.","structural_break":False}
    r=d.iloc[-1]
    c=safe_float(r.get("Close")); ma60=safe_float(r.get("MA60"),c); ma120=safe_float(r.get("MA120"),c); ma200=safe_float(r.get("MA200"),c)
    ret120=safe_float(r.get("RET120")); ret250=safe_float(r.get("RET250")); r60=safe_float(r.get("RET60"))
    score=0
    score+=25 if c>ma200 else 0
    score+=20 if ma60>ma120 else 0
    score+=20 if ma120>ma200 else 0
    score+=20 if ret250>0 else 0
    score+=15 if ret120>0 else 0
    structural_break=bool(c<ma200 and ret250<0)
    if structural_break:
        trend="장기 추세 훼손"
        suitability="장기 핵심보유 부적합"
        reason="200일선과 장기 수익률이 동시에 약화되어 장기 추세 확인이 필요합니다."
    elif score>=80:
        trend="장기 상승"
        suitability="장기 핵심보유 적합"
        reason="장기 이동평균 구조와 중장기 수익률이 모두 양호합니다."
    elif score>=60:
        trend="장기 우호"
        suitability="장기보유 가능"
        reason="장기 구조는 우호적이지만 추가 추세 확인이 필요합니다."
    elif score>=40:
        trend="장기 중립"
        suitability="선별 보유"
        reason="장기 방향성이 명확하지 않아 중기 추세를 함께 확인해야 합니다."
    else:
        trend="장기 약세"
        suitability="장기보유 주의"
        reason="장기 이동평균과 수익률이 약해 방어적인 접근이 필요합니다."
    return {"score":score,"trend":trend,"suitability":suitability,"reason":reason,"structural_break":structural_break}
def radar_overheat_score(row):
    rsi=safe_float(row.get("rsi",50),50)
    ret5=safe_float(row.get("ret5",0),0)
    dist20=safe_float(row.get("dist20",0),0)
    vr=safe_float(row.get("vr",1),1)
    score=0
    score+=35 if rsi>=75 else 25 if rsi>=70 else 10 if rsi>=65 else 0
    score+=25 if ret5>=10 else 18 if ret5>=7 else 10 if ret5>=4 else 0
    score+=25 if dist20>=10 else 18 if dist20>=7 else 10 if dist20>=4 else 0
    score+=15 if vr>=2 else 8 if vr>=1.5 else 0
    return min(100,score)
def validated_price_zone(row):
    c=safe_float(row.get("Close"),0); ma20=safe_float(row.get("MA20"),c); ma60=safe_float(row.get("MA60"),c); low20=safe_float(row.get("LOW20"),c); high20=safe_float(row.get("HIGH20"),c)
    if c<=0: return {"state":"무효","price":c}
    dist=(c/ma20-1)*100 if ma20 else 0
    if c<min(ma60,low20): state="무효"
    elif dist<=2.5 and c>=ma60: state="매수구간"
    elif dist<=5: state="눌림대기"
    else: state="추격금지"
    return {"state":state,"price":c,"dist20":dist,"ma20":ma20,"ma60":ma60,"low20":low20,"high20":high20}
def validated_cd_signal(row,theme_score_value,bench_ret20=0):
    sig=leading_signal(row,bench_ret20)
    zone=validated_price_zone(row)
    ts=float(theme_score_value or 0)
    if ts>=72 and sig["score"]>=78 and zone["state"]=="매수구간":
        state="C/D 매수"
    elif ts>=60 and sig["score"]>=70:
        state="C/D 관심"
    elif ts>=50 and sig["score"]>=60:
        state="C/D 대기"
    else:
        state="C/D 제외"
    return {"state":state,"theme_score":ts,"score":sig["score"],"rsi":sig["rsi"],"vr":sig["vr"],"dist20":sig["dist20"],"price_zone":zone["state"]}
def future_theme_engine():
    universe=st.session_state.etf_universe
    bench=_benchmark_snapshot()
    themes=[]
    seen=set()
    for theme,keywords in THEME_LEXICON.items():
        if theme in seen: continue
        rows=[]
        for code,name in universe.items():
            if not any(k.lower() in str(name).lower() for k in keywords): continue
            df=load_price_data(code)
            if df.empty: continue
            d=calculate_indicators(df)
            if len(d)<65: continue
            r=d.iloc[-1]; close=d["Close"]
            ret20=safe_float(r.get("RET20")); ret60=safe_float(close.pct_change(60).iloc[-1]*100)
            ma20=safe_float(r.get("MA20"),safe_float(r.get("Close"))); ma60=safe_float(r.get("MA60"),safe_float(r.get("Close")))
            current=safe_float(r.get("Close")); ret5=safe_float(r.get("RET5")); vr=safe_float(r.get("VOL_RATIO"),1); rsi=safe_float(r.get("RSI14"),50)
            accel=ret5-(ret20/4 if np.isfinite(ret20) else 0)
            prev=d.iloc[-21] if len(d)>=86 else None
            if prev is not None:
                prev_close=safe_float(prev.get("Close"),0); prev_ma20=safe_float(prev.get("MA20"),prev_close)
                prev_ret20=safe_float(prev.get("RET20"),0); prev_ret5=safe_float(prev.get("RET5"),0)
                prev_breadth=100.0 if prev_close>=prev_ma20 else 0.0
                prev_accel=prev_ret5-(prev_ret20/4 if np.isfinite(prev_ret20) else 0)
                prev_rs20=prev_ret20-safe_float(bench.get("ret20"),0)
            else:
                prev_ret20=ret20; prev_breadth=100.0 if current>=ma20 else 0.0; prev_accel=accel; prev_rs20=ret20-safe_float(bench.get("ret20"),0)
            rows.append({"code":code,"name":name,"price":current,"rsi":rsi,"vr":vr,"ret20":ret20,"ret60":ret60,"ret5":ret5,"trend":"상승" if current>=ma20 else "조정","ma60_gap":((current/ma60-1)*100 if ma60 else 0),"breadth":(100.0 if current>=ma20 else 0.0),"accel":accel,"rs20":ret20-safe_float(bench.get("ret20"),0),"ret20_prev":prev_ret20,"breadth_prev":prev_breadth,"accel_prev":prev_accel,"rs20_prev":prev_rs20})
        if not rows: continue
        ts=theme_score(rows,bench.get("ret20",0),bench.get("ret60",0))
        lifecycle=_theme_lifecycle(rows,bench)
        if ts is None: continue
        lead_count=sum(1 for x in rows if leading_signal(x,bench.get("ret20",0))["early_buy"])
        themes.append({"theme":theme,"score":round(ts,1),"lifecycle":lifecycle["state"],"lifecycle_score":round(lifecycle["score"],1),"count":len(rows),"lead_count":lead_count,"rows":rows})
        seen.add(theme)
    themes.sort(key=lambda x:(x["score"],x["lifecycle_score"]),reverse=True)
    return themes
def _future_theme_candidates(theme_item):
    rows=theme_item.get("rows",[])
    out=[]
    for r in rows:
        sig=leading_signal(r,0)
        if sig["score"]>=60:
            out.append({**r,"lead_score":sig["score"],"early_buy":sig["early_buy"],"dist20":sig["dist20"]})
    return sorted(out,key=lambda x:(x["lead_score"],x["rs20"],x["ret20"]),reverse=True)
def render_future_theme():
    st.markdown("## 🔮 미래테마")
    st.caption("현재 시장의 강한 테마보다 **다음으로 확산될 가능성이 있는 테마와 선행 ETF**를 찾습니다.")
    engine=future_theme_engine()
    if not engine:
        st.warning("미래테마 데이터를 계산할 수 없습니다.")
        return
    top=engine[:10]
    for i,t in enumerate(top,1):
        cls="lead" if i<=2 else "next" if i<=5 else "early"
        cands=_future_theme_candidates(t)
        st.markdown(
            f'<div class="theme-card {cls}"><div class="theme-rank">#{i}</div><div class="theme-name">{esc(t["theme"])}</div><div class="theme-score">미래테마 점수 {t["score"]:.0f}</div><div class="theme-meta">라이프사이클 {esc(t["lifecycle"])} · 선행 ETF {t["lead_count"]}개 · 구성 ETF {t["count"]}개</div></div>',
            unsafe_allow_html=True
        )
        if cands:
            best=cands[0]
            st.markdown(
                f'<div class="future-best"><b>⭐ 대표 선행 ETF</b> · {esc(best["name"])} ({best["code"]}) · 선행점수 {best["lead_score"]} · 20일 {best["ret20"]:+.1f}% · RSI {best["rsi"]:.1f} · 거래량 {best["vr"]:.2f}배</div>',
                unsafe_allow_html=True
            )
            if st.button(f"{t['theme']} 유망 ETF 분석",key=f"future_btn_{i}",use_container_width=True):
                st.session_state.future_detail_theme=t["theme"]
                st.session_state.future_detail_code=best["code"]
        if st.session_state.get("future_detail_theme")==t["theme"]:
            render_future_detail(t)
def render_future_detail(theme_item):
    code=st.session_state.get("future_detail_code")
    if not code: return
    st.markdown(f"### 🎯 {esc(theme_item['theme'])} · 유망 ETF")
    d=load_price_data(code)
    if d.empty:
        st.warning("가격 데이터를 불러오지 못했습니다.")
        return
    d=calculate_indicators(d)
    r=d.iloc[-1]
    sig=leading_signal(r,0)
    zone=validated_price_zone(r)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.metric("현재가",money(r["Close"]))
    with c2: st.metric("선행점수",f'{sig["score"]}/100')
    with c3: st.metric("RSI",f'{sig["rsi"]:.1f}')
    with c4: st.metric("거래량",f'{sig["vr"]:.2f}배')
    st.info(f'**가격구간:** {zone["state"]} · 20일선 이격 {zone["dist20"]:+.1f}%')
def render_future_engine():
    engine=future_theme_engine()
    if not engine: return
    top=engine[:10]
    data=[]
    for i,t in enumerate(top,1):
        cands=_future_theme_candidates(t)
        best=cands[0] if cands else {}
        data.append({
            "순위":i,
            "테마":t["theme"],
            "점수":t["score"],
            "라이프사이클":t["lifecycle"],
            "대표ETF":best.get("name","-"),
            "선행점수":best.get("lead_score",0),
        })
    if data:
        st.dataframe(pd.DataFrame(data),use_container_width=True,hide_index=True)
def market_radar_candidates():
    universe=st.session_state.etf_universe
    bench=_benchmark_snapshot()
    rows=[]
    for code,name in universe.items():
        df=load_price_data(code)
        if df.empty: continue
        d=calculate_indicators(df)
        if len(d)<65: continue
        r=d.iloc[-1]
        sig=leading_signal(r,bench.get("ret20",0))
        zone=validated_price_zone(r)
        overheat=radar_overheat_score({
            "rsi":safe_float(r.get("RSI14"),50),
            "ret5":safe_float(r.get("RET5"),0),
            "dist20":sig["dist20"],
            "vr":safe_float(r.get("VOL_RATIO"),1)
        })
        if sig["score"]<60: continue
        score=sig["score"]-overheat*.25
        rows.append({
            "code":code,
            "name":name,
            "score":round(score,1),
            "lead_score":sig["score"],
            "rsi":sig["rsi"],
            "vr":sig["vr"],
            "ret20":safe_float(r.get("RET20"),0),
            "dist20":sig["dist20"],
            "zone":zone["state"],
            "overheat":overheat
        })
    return sorted(rows,key=lambda x:x["score"],reverse=True)
def render_market_radar():
    st.markdown("## 📡 시장레이더")
    st.caption("현재 시장에서 상승 가능성이 높은 ETF를 선행성·추세·가격위치·과열도를 함께 평가합니다.")
    rows=market_radar_candidates()
    if not rows:
        st.info("시장레이더 후보가 없습니다.")
        return
    for i,x in enumerate(rows[:15],1):
        st.markdown(
            f'<div class="radar-card"><div class="radar-rank">#{i}</div><div class="radar-name">{esc(x["name"])} <span class="ticker">{x["code"]}</span></div><div class="radar-score">시장점수 {x["score"]:.0f}</div><div class="radar-meta">선행 {x["lead_score"]} · 20일 {x["ret20"]:+.1f}% · RSI {x["rsi"]:.1f} · 거래량 {x["vr"]:.2f}배 · 가격구간 {x["zone"]} · 과열 {x["overheat"]}</div></div>',
            unsafe_allow_html=True
        )
def final_target_candidates():
    future=future_theme_engine()
    radar=market_radar_candidates()
    if not future or not radar:
        return []
    radar_map={x["code"]:x for x in radar}
    out=[]
    for t in future[:8]:
        cands=_future_theme_candidates(t)
        for c in cands[:10]:
            r=radar_map.get(c["code"])
            if not r: continue
            final_score=t["score"]*.40+c["lead_score"]*.30+r["score"]*.30
            out.append({
                "code":c["code"],
                "name":c["name"],
                "theme":t["theme"],
                "theme_score":t["score"],
                "lead_score":c["lead_score"],
                "market_score":r["score"],
                "final_score":round(final_score,1),
                "rsi":c["rsi"],
                "vr":c["vr"],
                "zone":r["zone"],
                "overheat":r["overheat"]
            })
    unique={}
    for x in out:
        if x["code"] not in unique or x["final_score"]>unique[x["code"]]["final_score"]:
            unique[x["code"]]=x
    return sorted(unique.values(),key=lambda x:x["final_score"],reverse=True)
def render_final_target():
    st.markdown("## 🎯 최종타겟")
    st.caption("미래테마 + 선행 ETF + 시장레이더를 결합한 최종 후보입니다.")
    rows=final_target_candidates()
    if not rows:
        st.info("최종타겟 후보가 없습니다.")
        return
    for i,x in enumerate(rows[:15],1):
        st.markdown(
            f'<div class="final-target-card"><div class="final-rank">#{i}</div><div class="final-name">{esc(x["name"])} <span class="ticker">{x["code"]}</span></div><div class="final-score">최종점수 {x["final_score"]:.0f}</div><div class="final-meta">테마 {x["theme_score"]:.0f} · 선행 {x["lead_score"]} · 시장 {x["market_score"]:.0f} · RSI {x["rsi"]:.1f} · 거래량 {x["vr"]:.2f}배 · {x["zone"]}</div></div>',
            unsafe_allow_html=True
        )
        if st.button("ETF 분석",key=f"final_analysis_{i}",use_container_width=True):
            st.session_state.selected_code=x["code"]
            st.session_state.main_page="📊 내 ETF"
            st.rerun()
def render_my_etf():
    st.markdown("## 📊 내 ETF")
    universe=st.session_state.etf_universe
    watchlist=st.session_state.watchlist
    options=[f"{c} · {get_etf_name(c)}" for c in watchlist]
    if options:
        selected=st.selectbox("관심 ETF",options,index=0,key="watch_select")
        code=selected.split(" · ")[0]
    else:
        code=st.session_state.selected_code
    c1,c2=st.columns([3,1])
    with c1:
        add_code=st.text_input("ETF 코드 추가",value="",placeholder="예: 395160",key="add_etf_code")
    with c2:
        if st.button("추가",use_container_width=True):
            new_code=_normalize_etf_code(add_code)
            if new_code and new_code not in watchlist:
                watchlist.append(new_code)
                write_json(WATCHLIST_FILE,watchlist)
                st.session_state.watchlist=watchlist
                st.rerun()
    d=load_price_data(code)
    if d.empty:
        st.warning("가격 데이터를 불러오지 못했습니다.")
        return
    d=calculate_indicators(d)
    st.markdown(f"### {esc(get_etf_name(code))} <span class='ticker'>{code}</span>",unsafe_allow_html=True)
    r=d.iloc[-1]
    current=safe_float(r.get("Close"))
    prev=safe_float(d["Close"].iloc[-2]) if len(d)>=2 else current
    chg=current-prev
    pct=chg/prev*100 if prev else 0
    c1,c2,c3,c4=st.columns(4)
    with c1: st.metric("현재가",money(current),f"{pct:+.2f}%")
    with c2: st.metric("RSI14",f'{safe_float(r.get("RSI14"),50):.1f}')
    with c3: st.metric("거래량/20일",f'{safe_float(r.get("VOL_RATIO"),1):.2f}배')
    with c4: st.metric("20일 수익률",f'{safe_float(r.get("RET20"),0):+.1f}%')
    render_horizon_strategy(d,code)
    render_judgment(d)
    render_scenarios(d)
    st.markdown("### 가격차트")
    fig=go.Figure()
    fig.add_trace(go.Candlestick(x=d.index,open=d["Open"],high=d["High"],low=d["Low"],close=d["Close"],name="가격"))
    fig.add_trace(go.Scatter(x=d.index,y=d["MA20"],name="MA20"))
    fig.add_trace(go.Scatter(x=d.index,y=d["MA60"],name="MA60"))
    fig.update_layout(height=480,margin=dict(l=0,r=0,t=20,b=0),xaxis_rangeslider_visible=False)
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False,"scrollZoom":False})
    holding=st.session_state.holdings.get(code) or {}
    with st.expander("보유정보",expanded=False):
        held=st.selectbox("보유상태",["미보유","보유중"],index=1 if holding else 0,key=f"held_{code}")
        if held=="보유중":
            avg=st.number_input("평균매수가",min_value=0.0,value=safe_float(holding.get("avg_price"),0),key=f"avg_{code}")
            st.session_state.holdings[code]={"avg_price":avg}
            write_json(HOLDINGS_FILE,st.session_state.holdings)
def render_search_page():
    st.markdown("## 🔎 ETF 검색")
    q=st.text_input("ETF 이름 또는 코드",key="search_query",placeholder="AI / 반도체 / 395160")
    universe=st.session_state.etf_universe
    if not q:
        st.caption("ETF 이름 또는 6자리 코드를 입력하세요.")
        return
    results=[]
    for code,name in universe.items():
        if q.lower() in str(name).lower() or q in code:
            results.append((code,name))
    if not results:
        st.info("검색 결과가 없습니다.")
        return
    for code,name in results[:30]:
        c1,c2=st.columns([4,1])
        with c1:
            st.markdown(f"**{esc(name)}** `{code}`")
        with c2:
            if st.button("분석",key=f"search_{code}"):
                st.session_state.selected_code=code
                st.session_state.main_page="📊 내 ETF"
                st.rerun()
def render_navigation():
    pages=["📊 내 ETF","🔮 미래테마","🎯 최종타겟","📡 시장레이더","🔎 ETF 검색"]
    st.session_state.main_page=st.radio(
        "메뉴",
        pages,
        index=pages.index(st.session_state.main_page) if st.session_state.main_page in pages else 0,
        horizontal=True,
        label_visibility="collapsed"
    )
def render_app():
    init_state()
    render_navigation()
    page=st.session_state.main_page
    if page=="📊 내 ETF":
        render_my_etf()
    elif page=="🔮 미래테마":
        render_future_theme()
    elif page=="🎯 최종타겟":
        render_final_target()
    elif page=="📡 시장레이더":
        render_market_radar()
    elif page=="🔎 ETF 검색":
        render_search_page()
if __name__=="__main__":
    render_app()
def add_watch(code):
    code=_normalize_etf_code(code)
    if code and code not in st.session_state.watchlist:
        st.session_state.watchlist.append(code)
        write_json(WATCHLIST_FILE,st.session_state.watchlist)
def remove_watch(code):
    code=_normalize_etf_code(code)
    st.session_state.watchlist=[x for x in st.session_state.watchlist if x!=code]
    write_json(WATCHLIST_FILE,st.session_state.watchlist)
def get_price_summary(code):
    df=load_price_data(code)
    if df.empty:
        return None
    d=calculate_indicators(df)
    if d.empty:
        return None
    r=d.iloc[-1]
    current=safe_float(r.get("Close"),0)
    prev=safe_float(d["Close"].iloc[-2],current) if len(d)>1 else current
    change=current-prev
    pct=(change/prev*100) if prev else 0
    return {
        "current":current,
        "change":change,
        "pct":pct,
        "rsi":safe_float(r.get("RSI14"),50),
        "vr":safe_float(r.get("VOL_RATIO"),1),
        "ret20":safe_float(r.get("RET20"),0),
        "ret60":safe_float(r.get("RET60"),0),
        "ma20":safe_float(r.get("MA20"),current),
        "ma60":safe_float(r.get("MA60"),current),
    }
def theme_members(theme):
    keywords=THEME_LEXICON.get(theme,[])
    result=[]
    for code,name in st.session_state.etf_universe.items():
        if any(k.lower() in str(name).lower() for k in keywords):
            result.append((code,name))
    return result
def theme_snapshot(theme):
    members=theme_members(theme)
    rows=[]
    for code,name in members[:40]:
        df=load_price_data(code)
        if df.empty:
            continue
        d=calculate_indicators(df)
        if len(d)<65:
            continue
        r=d.iloc[-1]
        rows.append({
            "code":code,
            "name":name,
            "close":safe_float(r.get("Close")),
            "ret5":safe_float(r.get("RET5")),
            "ret20":safe_float(r.get("RET20")),
            "ret60":safe_float(r.get("RET60")),
            "rsi":safe_float(r.get("RSI14"),50),
            "vr":safe_float(r.get("VOL_RATIO"),1),
            "ma20":safe_float(r.get("MA20")),
            "ma60":safe_float(r.get("MA60")),
        })
    return rows
def render_theme_detail(theme):
    st.markdown(f"### {esc(theme)}")
    rows=theme_snapshot(theme)
    if not rows:
        st.info("테마 데이터를 확인할 수 없습니다.")
        return
    bench=_benchmark_snapshot()
    ts=theme_score(rows,bench.get("ret20",0),bench.get("ret60",0))
    lc=_theme_lifecycle(rows,bench)
    c1,c2,c3=st.columns(3)
    with c1:
        st.metric("테마점수",f"{safe_float(ts):.0f}")
    with c2:
        st.metric("라이프사이클",lc.get("state","관찰"))
    with c3:
        st.metric("구성 ETF",len(rows))
    ranked=[]
    for x in rows:
        sig=leading_signal(x,bench.get("ret20",0))
        ranked.append({**x,"lead_score":sig["score"],"early_buy":sig["early_buy"],"rs20":sig["rs20"],"dist20":sig["dist20"]})
    ranked=sorted(ranked,key=lambda x:(x["lead_score"],x["rs20"],x["ret20"]),reverse=True)
    for i,x in enumerate(ranked[:10],1):
        st.markdown(
            f'<div class="theme-member"><b>#{i} {esc(x["name"])}</b> <span class="ticker">{x["code"]}</span><br>'
            f'선행점수 {x["lead_score"]} · 20일 {x["ret20"]:+.1f}% · 60일 {x["ret60"]:+.1f}% · '
            f'RSI {x["rsi"]:.1f} · 거래량 {x["vr"]:.2f}배 · 이격 {x["dist20"]:+.1f}%</div>',
            unsafe_allow_html=True
        )
def radar_signal(row,bench_ret20=0):
    sig=leading_signal(row,bench_ret20)
    overheat=radar_overheat_score(row)
    score=sig["score"]-overheat*0.25
    return {
        "score":round(score,1),
        "lead":sig["score"],
        "overheat":overheat,
        "early_buy":sig["early_buy"],
        "dist20":sig["dist20"],
        "rs20":sig["rs20"],
    }
def build_radar_rows():
    universe=st.session_state.etf_universe
    bench=_benchmark_snapshot()
    rows=[]
    for code,name in universe.items():
        df=load_price_data(code)
        if df.empty:
            continue
        d=calculate_indicators(df)
        if len(d)<65:
            continue
        r=d.iloc[-1]
        row={
            "Close":safe_float(r.get("Close")),
            "MA20":safe_float(r.get("MA20")),
            "MA60":safe_float(r.get("MA60")),
            "RSI14":safe_float(r.get("RSI14"),50),
            "VOL_RATIO":safe_float(r.get("VOL_RATIO"),1),
            "RET5":safe_float(r.get("RET5"),0),
            "RET20":safe_float(r.get("RET20"),0),
            "RET60":safe_float(r.get("RET60"),0),
            "LOW20":safe_float(r.get("LOW20")),
            "HIGH20":safe_float(r.get("HIGH20")),
        }
        sig=radar_signal(row,bench.get("ret20",0))
        if sig["lead"]<55:
            continue
        zone=validated_price_zone(row)
        rows.append({
            "code":code,
            "name":name,
            "price":row["Close"],
            "ret20":row["RET20"],
            "ret60":row["RET60"],
            "rsi":row["RSI14"],
            "vr":row["VOL_RATIO"],
            "lead_score":sig["lead"],
            "market_score":sig["score"],
            "overheat":sig["overheat"],
            "dist20":sig["dist20"],
            "rs20":sig["rs20"],
            "zone":zone["state"],
            "early_buy":sig["early_buy"],
        })
    return sorted(rows,key=lambda x:x["market_score"],reverse=True)
def render_radar_card(item,rank):
    score=item["market_score"]
    if score>=80:
        cls="strong"
    elif score>=70:
        cls="positive"
    elif score>=60:
        cls="neutral"
    else:
        cls="weak"
    st.markdown(
        f'<div class="radar-card {cls}">'
        f'<div class="radar-rank">#{rank}</div>'
        f'<div class="radar-name">{esc(item["name"])} <span class="ticker">{item["code"]}</span></div>'
        f'<div class="radar-score">{score:.0f}</div>'
        f'<div class="radar-meta">선행 {item["lead_score"]} · 20일 {item["ret20"]:+.1f}% · '
        f'RSI {item["rsi"]:.1f} · 거래량 {item["vr"]:.2f}배 · '
        f'가격 {item["zone"]} · 과열 {item["overheat"]}</div>'
        f'</div>',
        unsafe_allow_html=True
    )
def render_radar_detail(item):
    st.markdown("### 🔍 시장레이더 상세")
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.metric("시장점수",f'{item["market_score"]:.0f}')
    with c2:
        st.metric("선행점수",f'{item["lead_score"]:.0f}')
    with c3:
        st.metric("RSI",f'{item["rsi"]:.1f}')
    with c4:
        st.metric("거래량",f'{item["vr"]:.2f}배')
    st.info(
        f'가격구간: **{item["zone"]}** · '
        f'20일 수익률 {item["ret20"]:+.1f}% · '
        f'20일선 이격 {item["dist20"]:+.1f}% · '
        f'과열점수 {item["overheat"]}'
    )
def render_radar_page():
    st.markdown("## 📡 시장레이더")
    st.caption("현재 시장에서 상승 가능성이 높은 ETF를 선행성·추세·가격위치·과열도를 함께 평가합니다.")
    rows=build_radar_rows()
    if not rows:
        st.info("시장레이더 후보가 없습니다.")
        return
    top=rows[:20]
    for i,item in enumerate(top,1):
        render_radar_card(item,i)
def final_target_score(theme_score_value,lead_score,market_score):
    return round(
        safe_float(theme_score_value)*0.40+
        safe_float(lead_score)*0.30+
        safe_float(market_score)*0.30,
        1
    )
def build_final_targets():
    future=future_theme_engine()
    radar=build_radar_rows()
    if not future or not radar:
        return []
    radar_map={x["code"]:x for x in radar}
    out=[]
    for theme_item in future[:10]:
        theme_members_rows=_future_theme_candidates(theme_item)
        for member in theme_members_rows[:15]:
            r=radar_map.get(member["code"])
            if not r:
                continue
            fs=final_target_score(
                theme_item["score"],
                member["lead_score"],
                r["market_score"]
            )
            out.append({
                "code":member["code"],
                "name":member["name"],
                "theme":theme_item["theme"],
                "theme_score":theme_item["score"],
                "lead_score":member["lead_score"],
                "market_score":r["market_score"],
                "final_score":fs,
                "rsi":member["rsi"],
                "vr":member["vr"],
                "ret20":member["ret20"],
                "zone":r["zone"],
                "overheat":r["overheat"],
            })
    best={}
    for x in out:
        old=best.get(x["code"])
        if old is None or x["final_score"]>old["final_score"]:
            best[x["code"]]=x
    return sorted(best.values(),key=lambda x:x["final_score"],reverse=True)
def render_final_target_card(item,rank):
    score=item["final_score"]
    if score>=80:
        cls="strong"
    elif score>=70:
        cls="positive"
    elif score>=60:
        cls="neutral"
    else:
        cls="weak"
    st.markdown(
        f'<div class="final-target-card {cls}">'
        f'<div class="final-rank">#{rank}</div>'
        f'<div class="final-name">{esc(item["name"])} <span class="ticker">{item["code"]}</span></div>'
        f'<div class="final-score">최종점수 {score:.0f}</div>'
        f'<div class="final-meta">테마 {item["theme_score"]:.0f} · 선행 {item["lead_score"]:.0f} · '
        f'시장 {item["market_score"]:.0f} · RSI {item["rsi"]:.1f} · '
        f'거래량 {item["vr"]:.2f}배 · 가격 {item["zone"]}</div>'
        f'</div>',
        unsafe_allow_html=True
    )
def render_final_target_page():
    st.markdown("## 🎯 최종타겟")
    st.caption("미래테마 + 선행 ETF + 시장레이더를 결합한 최종 후보입니다.")
    rows=build_final_targets()
    if not rows:
        st.info("최종타겟 후보가 없습니다.")
        return
    for i,item in enumerate(rows[:15],1):
        render_final_target_card(item,i)
        if st.button("ETF 분석",key=f"target_analysis_{item['code']}",use_container_width=True):
            st.session_state.selected_code=item["code"]
            st.session_state.main_page="📊 내 ETF"
            st.rerun()
def render_future_theme_card(item,rank):
    cls="lead" if rank<=2 else "next" if rank<=5 else "early"
    st.markdown(
        f'<div class="theme-card {cls}">'
        f'<div class="theme-rank">#{rank}</div>'
        f'<div class="theme-name">{esc(item["theme"])}</div>'
        f'<div class="theme-score">미래테마 점수 {item["score"]:.0f}</div>'
        f'<div class="theme-meta">라이프사이클 {esc(item["lifecycle"])} · '
        f'선행 ETF {item["lead_count"]}개 · 구성 ETF {item["count"]}개</div>'
        f'</div>',
        unsafe_allow_html=True
    )
def render_future_candidate(item,theme_item,rank):
    st.markdown(
        f'<div class="future-candidate">'
        f'<b>{esc(item["name"])}</b> <span class="ticker">{item["code"]}</span> · '
        f'선행점수 {item["lead_score"]} · 20일 {item["ret20"]:+.1f}% · '
        f'RSI {item["rsi"]:.1f} · 거래량 {item["vr"]:.2f}배'
        f'</div>',
        unsafe_allow_html=True
    )
def render_future_theme_page():
    st.markdown("## 🔮 미래테마")
    st.caption("현재 주도 테마가 아니라 다음으로 확산될 가능성이 있는 테마와 선행 ETF를 찾습니다.")
    engine=future_theme_engine()
    if not engine:
        st.warning("미래테마 데이터를 계산할 수 없습니다.")
        return
    for i,item in enumerate(engine[:10],1):
        render_future_theme_card(item,i)
        candidates=_future_theme_candidates(item)
        if candidates:
            for j,c in enumerate(candidates[:3],1):
                render_future_candidate(c,item,j)
            best=candidates[0]
            if st.button(
                f'{item["theme"]} 유망 ETF 분석',
                key=f'future_analysis_{i}',
                use_container_width=True
            ):
                st.session_state.selected_code=best["code"]
                st.session_state.main_page="📊 내 ETF"
                st.rerun()
def render_etf_search():
    st.markdown("## 🔎 ETF 검색")
    q=st.text_input(
        "ETF 이름 또는 코드",
        placeholder="예: AI / 반도체 / 395160",
        key="etf_search_query"
    )
    if not q:
        st.caption("ETF 이름 또는 6자리 코드를 입력하세요.")
        return
    q=q.strip().lower()
    results=[]
    for code,name in st.session_state.etf_universe.items():
        if q in code.lower() or q in str(name).lower():
            results.append((code,name))
    if not results:
        st.info("검색 결과가 없습니다.")
        return
    st.caption(f"{len(results)}개 ETF")
    for code,name in results[:50]:
        c1,c2=st.columns([5,1])
        with c1:
            st.markdown(f"**{esc(name)}** `{code}`")
        with c2:
            if st.button("분석",key=f"search_analysis_{code}",use_container_width=True):
                st.session_state.selected_code=code
                st.session_state.main_page="📊 내 ETF"
                st.rerun()
def render_watchlist_manager():
    st.markdown("### ⭐ 관심 ETF")
    watchlist=st.session_state.watchlist
    if watchlist:
        for code in watchlist:
            name=get_etf_name(code)
            c1,c2,c3=st.columns([5,1,1])
            with c1:
                st.markdown(f"**{esc(name)}** `{code}`")
            with c2:
                if st.button("선택",key=f"watch_select_{code}",use_container_width=True):
                    st.session_state.selected_code=code
            with c3:
                if st.button("삭제",key=f"watch_delete_{code}",use_container_width=True):
                    remove_watch(code)
                    st.rerun()
    else:
        st.caption("관심 ETF가 없습니다.")
    with st.expander("ETF 추가",expanded=False):
        add_code=st.text_input("ETF 코드",placeholder="예: 395160",key="watch_add_code")
        if st.button("관심 ETF 등록",key="watch_add_button",use_container_width=True):
            code=_normalize_etf_code(add_code)
            if code:
                add_watch(code)
                st.rerun()
def render_my_etf_page():
    st.markdown("## 📊 내 ETF")
    render_watchlist_manager()
    watchlist=st.session_state.watchlist
    selected=st.session_state.selected_code
    if watchlist and selected not in watchlist:
        selected=watchlist[0]
        st.session_state.selected_code=selected
    if not selected:
        st.info("ETF를 선택해주세요.")
        return
    d=load_price_data(selected)
    if d.empty:
        st.warning("가격 데이터를 불러오지 못했습니다.")
        return
    d=calculate_indicators(d)
    name=get_etf_name(selected)
    st.markdown(
        f"### {esc(name)} <span class='ticker'>{selected}</span>",
        unsafe_allow_html=True
    )
    r=d.iloc[-1]
    current=safe_float(r.get("Close"),0)
    prev=safe_float(d["Close"].iloc[-2],current) if len(d)>1 else current
    change=current-prev
    pct=change/prev*100 if prev else 0
    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.metric("현재가",money(current),f"{change:+,.0f}원 ({pct:+.2f}%)")
    with c2:
        st.metric("RSI14",f'{safe_float(r.get("RSI14"),50):.1f}')
    with c3:
        st.metric("거래량/20일",f'{safe_float(r.get("VOL_RATIO"),1):.2f}배')
    with c4:
        st.metric("20일 수익률",f'{safe_float(r.get("RET20"),0):+.1f}%')
    render_horizon_strategy(d,selected)
    render_judgment(d)
    render_scenarios(d)
    st.markdown("### 📈 가격차트")
    fig=go.Figure()
    fig.add_trace(go.Candlestick(
        x=d.index,
        open=d["Open"],
        high=d["High"],
        low=d["Low"],
        close=d["Close"],
        name="가격"
    ))
    fig.add_trace(go.Scatter(x=d.index,y=d["MA20"],name="MA20"))
    fig.add_trace(go.Scatter(x=d.index,y=d["MA60"],name="MA60"))
    fig.update_layout(
        height=480,
        margin=dict(l=0,r=0,t=20,b=0),
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar":False,"scrollZoom":False}
    )
    holding=st.session_state.holdings.get(selected) or {}
    with st.expander("보유정보",expanded=False):
        held=st.selectbox(
            "보유상태",
            ["미보유","보유중"],
            index=1 if holding else 0,
            key=f"holding_state_{selected}"
        )
        if held=="보유중":
            avg=st.number_input(
                "평균매수가",
                min_value=0.0,
                value=safe_float(holding.get("avg_price"),0),
                key=f"holding_avg_{selected}"
            )
            st.session_state.holdings[selected]={"avg_price":avg}
            write_json(HOLDINGS_FILE,st.session_state.holdings)
def render_settings():
    st.markdown("### ⚙️ 설정")
    if st.button("가격 캐시 초기화",use_container_width=True):
        st.session_state.price_cache={}
        st.success("가격 캐시를 초기화했습니다.")
    if st.button("ETF 마스터 새로고침",use_container_width=True):
        st.session_state.etf_universe=load_etf_universe()
        st.session_state.price_cache={}
        st.success("ETF 마스터를 새로고침했습니다.")
def render_header():
    st.markdown(
        '<div class="app-header">'
        '<div class="app-title">ETF RADAR</div>'
        '<div class="app-subtitle">미래테마 · 선행 ETF · 시장레이더 · 최종타겟</div>'
        '</div>',
        unsafe_allow_html=True
    )
def render_main_navigation():
    pages=[
        "📊 내 ETF",
        "🔮 미래테마",
        "🎯 최종타겟",
        "📡 시장레이더",
        "🔎 ETF 검색",
    ]
    current=st.session_state.get("main_page","📊 내 ETF")
    if current not in pages:
        current=pages[0]
    selected=st.radio(
        "메뉴",
        pages,
        index=pages.index(current),
        horizontal=True,
        label_visibility="collapsed",
        key="main_navigation"
    )
    st.session_state.main_page=selected
def render_app_body():
    page=st.session_state.get("main_page","📊 내 ETF")
    if page=="📊 내 ETF":
        render_my_etf_page()
    elif page=="🔮 미래테마":
        render_future_theme_page()
    elif page=="🎯 최종타겟":
        render_final_target_page()
    elif page=="📡 시장레이더":
        render_radar_page()
    elif page=="🔎 ETF 검색":
        render_etf_search()
def run_app():
    init_state()
    render_header()
    render_main_navigation()
    render_app_body()
def render_app():
    run_app()
def main():
    render_app()
lc = _theme_lifecycle(theme_members, benchmark) if theme_members else {"score":0.0,"state":"관찰"}
lead = leading_signal(r, bench20)
zone = validated_price_zone(r)
pscore = {"매수구간":100,"눌림대기":70,"추격금지":25,"무효":0}.get(zone.get("state"),0)
cross = (
    float(np.clip(tscore,0,100)) * 0.30 +
    float(np.clip(lc.get("score",0),0,100)) * 0.20 +
    float(np.clip(lead.get("score",0),0,100)) * 0.30 +
    float(np.clip(item["opportunity"],0,100)) * 0.10 +
    float(np.clip(pscore,0,100)) * 0.10
)
if lc.get("state") == "쇠퇴":
    cross -= 18
elif lc.get("state") == "과열":
    cross -= 10
if item["overheat"] >= 65:
    cross -= 10
item["theme_score"] = round(float(tscore),1)
item["lifecycle_score"] = round(float(lc.get("score",0)),1)
item["lifecycle_state"] = lc.get("state","관찰")
item["lead_score"] = round(float(lead.get("score",0)),1)
item["price_zone"] = zone.get("state","확인")
item["cross_score"] = int(np.clip(round(cross),0,100))
if item["cross_score"] >= 80 and item["price_zone"] == "매수구간" and item["overheat"] < 65:
    item["cross_state"] = "🔥 최우선 후보"
elif item["cross_score"] >= 70:
    item["cross_state"] = "🟢 우선 관찰"
elif item["cross_score"] >= 55:
    item["cross_state"] = "🟡 확인 필요"
else:
    item["cross_state"] = "⚪ 대기"
except Exception:
    item.update({"theme_score":0.0,"lifecycle_score":0.0,"lifecycle_state":"관찰",
                 "lead_score":0.0,"price_zone":"확인","cross_score":0,"cross_state":"⚪ 대기",
                 "future_theme":"미래테마 미연결","future_theme_related":False})
item["held"] = code in st.session_state.holdings
rows.append(item)
data = {"time": now, "rows": rows, "benchmark": benchmark, "target_key": target_key}
st.session_state.radar_cache = data
return data
def render_radar_card(item, mode):
    if mode == "🎯 유망후보":
        score = item.get("cross_score", item["opportunity"])
        state = item.get("cross_state", "기회 후보")
        badge = '<span class="radar-badge radar-badge-op">'+esc(state)+'</span>'
        title = "미래테마·선행성·시장레이더·가격구간을 모두 통과한 유망 후보"
    else:
        score = item["overheat"]
        badge = '<span class="radar-badge radar-badge-hot">과열 주의</span>'
        title = "단기 상승폭·RSI·이격·거래량을 함께 확인"
    held = '<span class="radar-badge radar-badge-hold">보유중</span>' if item["held"] else ''
    theme_text = f'{item["theme"]} · {item["stage"]}' if item["theme"] != "기타" else "테마 미분류"
    position = "20/60일선 위" if item["above20"] and item["above60"] else ("20일선 위 · 60일선 아래" if item["above20"] else "20일선 아래")
    guide_html = ""
    if mode == "🎯 유망후보":
        raw = item.get("raw") if isinstance(item, dict) else None
        if raw is None:
            raw = {}
        c = safe_float(raw.get("Close"), item.get("price", np.nan))
        ma20 = safe_float(raw.get("MA20"), c)
        ma60 = safe_float(raw.get("MA60"), c)
        low20 = safe_float(raw.get("LOW20"), c)
        if np.isfinite(c) and c > 0 and np.isfinite(ma20) and ma20 > 0 and np.isfinite(ma60) and ma60 > 0:
            support = max(low20, ma20 * 0.985)
            buy1 = ma20 * 1.025
            invalid = min(ma60 * 0.97, support * 0.97)
            if invalid <= 0: invalid = c * 0.92
            buy2 = (buy1 + invalid) / 2
            risk = max(buy1 - invalid, c * 0.05)
            tp1 = buy1 + risk
            tp2 = buy1 + risk * 2
            chase = ma20 * 1.07
            zone = item.get("price_zone", "확인")
            if zone == "매수구간": action = "🔥 지금 1차 매수 검토"
            elif zone == "눌림대기": action = "🟢 지금 추격하지 말고 눌림 2차 매수 대기"
            elif zone == "추격금지": action = "🔴 지금 매수 금지 · 눌림 대기"
            else: action = "🔴 매수 보류 · 가격구간 무효"
            guide_html = f'''<div class="radar-trade-title">실제 행동 / 가격</div>
  <div class="radar-action">{esc(action)}</div>
  <div class="radar-trade-grid">
    <div class="radar-trade-item"><div class="radar-label">1차 매수</div><div class="radar-trade-price">{money(buy1)}</div><div class="radar-trade-desc">20일선 + 2.5%</div></div>
    <div class="radar-trade-item"><div class="radar-label">2차 매수</div><div class="radar-trade-price">{money(buy2)}</div><div class="radar-trade-desc">눌림 구간</div></div>
    <div class="radar-trade-item"><div class="radar-label">추격 금지</div><div class="radar-trade-price">{money(chase)}</div><div class="radar-trade-desc">이상 매수 금지</div></div>
    <div class="radar-trade-item"><div class="radar-label">손절 / 무효</div><div class="radar-trade-price">{money(invalid)}</div><div class="radar-trade-desc">가격 이탈 시 재평가</div></div>
    <div class="radar-trade-item"><div class="radar-label">1차 익절</div><div class="radar-trade-price">{money(tp1)}</div><div class="radar-trade-desc">1R</div></div>
    <div class="radar-trade-item"><div class="radar-label">2차 익절</div><div class="radar-trade-price">{money(tp2)}</div><div class="radar-trade-desc">2R</div></div>
  </div>
  <div class="radar-follow">이후: <b>20일선 추적</b> · 1차/2차 익절 후 잔여 물량은 20일선 이탈 여부를 우선 확인</div>'''
    st.markdown(f'''<div class="radar-card">
  <div>{badge}{held}</div>
  <div class="radar-title">{esc(item["name"])} · {esc(item["code"])}</div>
  <div class="radar-sub">{esc(title)} · {esc(theme_text)}</div>
  <div style="display:flex;justify-content:space-between;align-items:center;margin-top:7px;">
    <div><div class="radar-label">레이더 점수</div><div class="radar-score">{score}</div></div>
    <div style="text-align:right"><div class="radar-label">현재가</div><div class="radar-value">{money(item["price"])}</div></div>
  </div>
  <div class="radar-grid">
    <div class="radar-metric"><div class="radar-label">테마</div><div class="radar-value">{item.get("theme_score",0):.0f}</div></div>
    <div class="radar-metric"><div class="radar-label">선행</div><div class="radar-value">{item.get("lead_score",0):.0f}</div></div>
    <div class="radar-metric"><div class="radar-label">가격</div><div class="radar-value">{esc(item.get("price_zone","확인"))}</div></div>
    <div class="radar-metric"><div class="radar-label">생애주기</div><div class="radar-value">{esc(item.get("lifecycle_state","관찰"))}</div></div>
  </div>
  <div class="radar-note">20일선 대비 <b>{item["dist20"]:+.1f}%</b> · {position} · 미래테마×레이더 교차점수 <b>{item.get("cross_score",0)}</b> · 최근 5일 <b>{item["ret5"]:+.1f}%</b> · RSI <b>{item["rsi"]:.1f}</b></div>
  <div class="radar-note">미래테마 연결: <b>{("🟢 실제 후보 · " + str(item.get("future_theme")) + " · ETF 순위 #" + str(item.get("future_theme_rank"))) if item.get("future_theme_selected") else (("🟡 연관테마 · " + str(item.get("future_theme"))) if item.get("future_theme_related") else "⚪ 현재 미래테마 엔진과 직접 연결되지 않음")}</b></div>
</div>''', unsafe_allow_html=True)
    if mode == "🎯 유망후보":
        with st.expander("💰 실제 행동 / 매수가·손절·익절 보기", expanded=False):
            if guide_html:
                st.markdown(guide_html, unsafe_allow_html=True)
            else:
                st.info("현재 가격 데이터로 행동 가격을 계산할 수 없습니다.")
def render_market_radar():
    st.markdown('<div class="hero"><div class="hero-name">🔥 시장 레이더</div><div class="hero-code">수급에 가까운 거래량 · 추세 · 상대강도 · 과열을 한 화면에서 확인</div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🔄 레이더 새로고침", use_container_width=True, key="radar_refresh"):
            st.session_state.radar_cache = None
            st.session_state.price_cache = {}
            st.rerun()
    with c2:
        st.caption("레이더는 내 ETF + 현재 미래테마 ETF만 분석합니다. 결과는 5분 캐시로 재사용합니다.")
    radar_modes = ["🎯 유망후보", "⚠️ 과열검색", "🔄 테마순환"]
    if hasattr(st, "segmented_control"):
        mode = st.segmented_control(
            "레이더 모드",
            options=radar_modes,
            default=st.session_state.get("radar_mode", radar_modes[0]),
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
        mode = st.session_state.get("radar_mode", radar_modes[0])
    with st.spinner("시장 레이더 데이터를 계산하는 중입니다…"):
        data = build_radar_data()
    rows = data["rows"]
    if not rows:
        st.warning("레이더에 사용할 가격 데이터가 없습니다.")
        return
    if mode == "🔄 테마순환":
        st.markdown("### 테마순환")
        theme_rows = []
        for theme, stage in get_future_chain():
            members = [x for x in rows if x["theme"] == theme]
            if not members:
                continue
        vals5 = [x["ret5"] for x in members if np.isfinite(x["ret5"])]
        vals20 = [x["ret20"] for x in members if np.isfinite(x["ret20"])]
        valsvr = [x["vr"] for x in members if np.isfinite(x["vr"])]
        if not vals5 or not vals20 or not valsvr:
            continue
        avg5 = float(np.mean(vals5))
        avg20 = float(np.mean(vals20))
        avgvr = float(np.mean(valsvr))
        breadth = sum(1 for x in members if x["ret5"] >= 0) / len(members) * 100
        strength = avg5 * 0.45 + avg20 * 0.25 + (avgvr - 1) * 10 + breadth * 0.10
        theme_rows.append({"theme":theme,"stage":stage,"avg5":avg5,"avg20":avg20,"avgvr":avgvr,"breadth":breadth,"strength":strength,"n":len(members)})
    theme_rows.sort(key=lambda x:x["strength"], reverse=True)
    for x in theme_rows:
        cls = "positive" if x["avg5"] >= 0 else "negative"
        st.markdown(f'<div class="radar-card"><span class="radar-badge">{esc(x["stage"])}</span><div class="radar-title">{esc(x["theme"])}</div><div class="radar-sub">구성 {x["n"]}개 · 단기 상승 비율 {x["breadth"]:.0f}%</div><div class="radar-grid"><div class="radar-metric"><div class="radar-label">5일[...]</div></div></div></div>', unsafe_allow_html=True)
    suitability += 15 if ma120 > ma200 else 7 if ma120 >= ma200*0.98 else 0
    suitability += 10 if r60 > 0 else 4 if r60 > -8 else 0
    if suitability >= 75:
        fit_state="🟢 장기 핵심보유"
    elif suitability >= 55:
        fit_state="🟢 장기 보유"
    elif suitability >= 40:
        fit_state="🟡 장기 보유 + 추세 확인"
    else:
        fit_state="🔴 장기 적합성 재검토"
    trend_score=0
    trend_score += 30 if ma200 > ma200_60 else 0
    trend_score += 25 if ma120 > ma120_60 else 0
    trend_score += 20 if ma120 > ma200 else 0
    trend_score += 15 if r120 > 0 else 0
    trend_score += 10 if close > ma200 else 0
    if trend_score >= 75:
        trend_state="🟢 장기 상승추세"
    elif trend_score >= 50:
        trend_state="🟡 장기 추세 확인"
    else:
        trend_state="🔴 장기 하락추세"
    below20=int((d["Close"].iloc[i-19:i+1] < d["MA200"].iloc[i-19:i+1]).sum()) >= 15
    structural_break=(
        r252 < 0 and r120 < 0 and
        ma200 <= ma200_60 and ma120 <= ma120_60 and
        ma120 < ma200 and close < ma200 and below20
    )
    r20=float(r["R20"]); r5=float(r["R5"]); rsi=float(r["RSI"])
    vr=float(r["VR"]) if np.isfinite(r["VR"]) else 1.0
    short_score=0
    short_score += 25 if r5 > 0 else 0
    short_score += 20 if r20 > 2 else 10 if r20 > 0 else 0
    short_score += 20 if close > ma20 else 0
    short_score += 15 if ma20 > ma60 else 0
    short_score += 10 if 50 <= rsi <= 68 else 5 if 45 <= rsi <= 72 else 0
    short_score += 10 if vr >= 1.05 else 5 if vr >= 0.9 else 0
    if short_score >= 75: short_state="🔥 단기 강세"
    elif short_score >= 60: short_state="🟢 보유/운용"
    elif short_score >= 45: short_state="🟡 매수 대기"
    else: short_state="⚪ 단기 관찰"
    if structural_break:
        action="🔴 장기 추세 훼손 · 신규매수 중단"
    elif fit_state == "🟢 장기 핵심보유" and short_state == "🔥 단기 강세":
        action="🟢 핵심보유 + 적극 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유") and short_state in ("🟢 보유/운용","🔥 단기 강세"):
        action="🟢 장기보유 + 현재 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유"):
        action="🟡 장기보유 유지 + 신규매수 대기"
    else:
        action="🟡 추세 확인 후 운용"
    entry_i=i+1
    entry_price=float(d.iloc[entry_i]["Close"])
    out={
        "신호일":d.index[i].date(),"진입일":d.index[entry_i].date(),
        "장기적합성점수V3":suitability,"장기적합성V3":fit_state,
        "장기추세점수V3":trend_score,"장기추세V3":trend_state,
        "단기점수V3":short_score,"단기운용V3":short_state,
        "최종행동V3":action,"진입가":entry_price,
        "구조적훼손V3":structural_break,"252일고점대비":dd252,
    }
    for h in [20,60,120,250]:
        ep=float(d.iloc[entry_i+h-1]["Close"])
        out[f"{h}일후수익률"]=(ep/entry_price-1)*100
    return out
def bt_run_horizon_backtest_v3(start,end,tickers,step_days=5):
    download_start=(pd.Timestamp(start)-pd.Timedelta(days=520)).strftime("%Y-%m-%d")
    download_end=(pd.Timestamp(end)+pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    raw=bt_download_prices(tickers,download_start,download_end)
    data={k:bt_indicators(v) for k,v in raw.items()}
    rows=[]
    for ticker in tickers:
        d=data.get(ticker)
        if d is None or len(d)<520: continue
        dates=d.index[(d.index>=pd.Timestamp(start))&(d.index<=pd.Timestamp(end))]
        for dt in dates[::max(1,int(step_days))]:
            i=d.index.get_loc(dt)
            rec=bt_horizon_judgment_v3(d,i)
            if rec is not None:
                rec["ETF"]=ticker
                rec["종목명"]=BT_POOL.get(ticker,ticker)
                rows.append(rec)
    return pd.DataFrame(rows),data
def bt_summarize_horizon_v3(df):
    if df is None or df.empty: return pd.DataFrame()
    rows=[]
    for col in ["장기적합성V3","장기추세V3","단기운용V3","최종행동V3"]:
        for state,g in df.groupby(col):
            rows.append({"구분":col,"판정":state,"건수":len(g),
                "20일 평균":g["20일후수익률"].mean(),
                "60일 평균":g["60일후수익률"].mean(),
                "120일 평균":g["120일후수익률"].mean(),
                "250일 평균":g["250일후수익률"].mean(),
                "20일 승률":(g["20일후수익률"]>0).mean()*100,
                "120일 승률":(g["120일후수익률"]>0).mean()*100,
                "250일 승률":(g["250일후수익률"]>0).mean()*100})
    return pd.DataFrame(rows)
def bt_horizon_judgment_v4(d, i):
    """시점 i 이전 데이터만 사용.
    V4 원칙
    - 장기적합성은 미래수익률을 예측하는 점수가 아니라 '계속 보유할 만한 구조인가'를 판단.
    - 단기 조정/고점 대비 하락만으로 장기 핵심보유를 박탈하지 않음.
    - 장기적합성에는 최근 1년 동안 장기추세가 유지된 '지속성'을 가장 크게 반영.
    - 현재 추세와 단기운용은 별도 축으로 판단.
    - 구조적 훼손만 실제 신규매수 중단 사유로 사용.
    """
    if i < 300 or i + 250 >= len(d): return None
    r=d.iloc[i]
    close=float(r["Close"]); ma20=float(r["MA20"]); ma60=float(r["MA60"])
    ma120=float(r["MA120"]); ma200=float(r["MA200"])
    ma200_60=float(d.iloc[i-60]["MA200"]); ma120_60=float(d.iloc[i-60]["MA120"])
    r20=float(r["R20"]); r60=float(r["R60"]); r120=float(r["R120"]); r252=float(r["R252"])
    high252=float(r["HIGH252"]) if np.isfinite(r["HIGH252"]) else close
    dd252=(close/high252-1)*100 if high252>0 else 0
    w=d.iloc[i-251:i+1]
    above200=float((w["Close"] >= w["MA200"]).mean())*100
    above120=float((w["Close"] >= w["MA120"]).mean())*100
    ma200_up=ma200 > ma200_60
    ma120_up=ma120 > ma120_60
    suitability=(
        above200*0.40
        + above120*0.20
        + (25 if ma200_up else 0)
        + (15 if r252>0 else 7 if r252>-15 else 0)
    )
    suitability=float(np.clip(suitability,0,100))
    if suitability >= 78:
        fit_state="🟢 장기 핵심보유"
    elif suitability >= 62:
        fit_state="🟢 장기 보유"
    elif suitability >= 48:
        fit_state="🟡 장기 보유 + 추세 확인"
    else:
        fit_state="🔴 장기 적합성 재검토"
    trend_score=0
    trend_score += 30 if ma200_up else 0
    trend_score += 25 if ma120_up else 0
    trend_score += 20 if ma120 > ma200 else 0
    trend_score += 15 if r120 > 0 else 0
    trend_score += 10 if close > ma200 else 0
    if trend_score >= 75: trend_state="🟢 장기 상승추세"
    elif trend_score >= 50: trend_state="🟡 장기 조정/추세 확인"
    else: trend_state="🔴 장기 하락추세"
    structural_break=(
        above200 < 45 and above120 < 50 and
        r252 < 0 and r120 < 0 and
        not ma200_up and not ma120_up and
        ma120 < ma200 and close < ma200
    )
    rsi=float(r["RSI"]); vr=float(r["VR"]) if np.isfinite(r["VR"]) else 1.0
    short_score=0
    short_score += 25 if float(r["R5"]) > 0 else 0
    short_score += 20 if r20 > 2 else 10 if r20 > 0 else 0
    short_score += 20 if close > ma20 else 0
    short_score += 15 if ma20 > ma60 else 0
    short_score += 10 if 50 <= rsi <= 68 else 5 if 45 <= rsi <= 72 else 0
    short_score += 10 if vr >= 1.05 else 5 if vr >= 0.9 else 0
    if short_score >= 75: short_state="🔥 단기 강세"
    elif short_score >= 60: short_state="🟢 보유/운용"
    elif short_score >= 45: short_state="🟡 매수 대기"
    else: short_state="⚪ 단기 관찰"
    if structural_break:
        action="🔴 구조적 추세 훼손 · 신규매수 중단"
    elif fit_state == "🟢 장기 핵심보유" and short_state == "🔥 단기 강세":
        action="🟢 핵심보유 + 적극 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유") and short_state in ("🟢 보유/운용","🔥 단기 강세"):
        action="🟢 장기보유 + 현재 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유"):
        action="🟡 장기보유 유지 + 신규매수 대기"
    elif trend_state == "🟡 장기 조정/추세 확인":
        action="🟡 장기 추세 확인 후 운용"
    else:
        action="⚪ 관찰"
    entry_i=i+1; entry_price=float(d.iloc[entry_i]["Close"])
    out={
        "신호일":d.index[i].date(),"진입일":d.index[entry_i].date(),
        "장기적합성점수V4":round(suitability,1),"장기적합성V4":fit_state,
        "장기추세점수V4":trend_score,"장기추세V4":trend_state,
        "단기점수V4":short_score,"단기운용V4":short_state,
        "장기추세지속성V4":round(above200,1),"구조적훼손V4":structural_break,
        "최종행동V4":action,"진입가":entry_price,"252일고점대비":dd252,
    }
    for h in [20,60,120,250]:
        ep=float(d.iloc[entry_i+h-1]["Close"])
        out[f"{h}일후수익률"]=(ep/entry_price-1)*100
    return out
def bt_run_horizon_backtest_v4(start,end,tickers,step_days=5):
    download_start=(pd.Timestamp(start)-pd.Timedelta(days=560)).strftime("%Y-%m-%d")
    download_end=(pd.Timestamp(end)+pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    raw=bt_download_prices(tickers,download_start,download_end)
    data={k:bt_indicators(v) for k,v in raw.items()}
    rows=[]
    for ticker in tickers:
        d=data.get(ticker)
        if d is None or len(d)<560: continue
        dates=d.index[(d.index>=pd.Timestamp(start))&(d.index<=pd.Timestamp(end))]
        for dt in dates[::max(1,int(step_days))]:
            i=d.index.get_loc(dt); rec=bt_horizon_judgment_v4(d,i)
            if rec is not None:
                rec["ETF"]=ticker
                rec["종목명"]=BT_POOL.get(ticker,ticker)
                rows.append(rec)
    return pd.DataFrame(rows),data
def bt_summarize_horizon_v4(df):
    if df is None or df.empty: return pd.DataFrame()
    rows=[]
    for col in ["장기적합성V4","장기추세V4","단기운용V4","최종행동V4"]:
        for state,g in df.groupby(col):
            rows.append({"구분":col,"판정":state,"건수":len(g),
                "20일 평균":g["20일후수익률"].mean(),
                "60일 평균":g["60일후수익률"].mean(),
                "120일 평균":g["120일후수익률"].mean(),
                "250일 평균":g["250일후수익률"].mean(),
                "20일 승률":(g["20일후수익률"]>0).mean()*100,
                "120일 승률":(g["120일후수익률"]>0).mean()*100,
                "250일 승률":(g["250일후수익률"]>0).mean()*100})
    return pd.DataFrame(rows)
def bt_trade_levels_v6(d, signal_i, entry_price):
    """신호일의 정보만 사용해 다음 거래일 진입 기준을 계산한다."""
    r = d.iloc[signal_i]
    c = float(r["Close"])
    ma20 = float(r["MA20"])
    ma60 = float(r["MA60"])
    low20 = float(r["LOW20"])
    support = max(low20, ma20 * 0.985)
    stop1 = min(ma60 * 0.97, support * 0.97)
    stop2 = min(stop1, low20 * 0.98)
    if not np.isfinite(stop1) or stop1 <= 0:
        stop1 = entry_price * 0.95
    if not np.isfinite(stop2) or stop2 <= 0:
        stop2 = stop1
    risk = max(entry_price - stop1, entry_price * 0.02)
    tp1 = entry_price + risk
    tp2 = entry_price + risk * 2.0
    return {"entry": entry_price, "support": support, "stop1": stop1,
            "stop2": stop2, "risk": risk, "tp1": tp1, "tp2": tp2,
            "signal_close": c}
def bt_simulate_cd_trade_v7(r, data, initial_cash=1_000_000,
                         fee_per_side=0.0010, slippage_per_side=0.0005,
                         max_hold_da
                       "검증_선행점수":sig.get("검증_lead",np.nan),"검증_선행강세점수":sig.get("검증_early_score",np.nan),
                       "검증_미반영점수":sig.get("검증_underpriced",np.nan),"검증_비과열점수":sig.get("검증_not_hot",np.nan),
                       "20일수익":sig.get("20일수익",np.nan),"60일수익":sig.get("60일수익",np.nan),"MFE":mfe,"MAE":mae,"순수익률":net*100,"거래후자산":cash})
        next_available=d.index[exit_i]+pd.Timedelta(days=1)
    td=pd.DataFrame(trades); cv=pd.DataFrame(curve)
    if td.empty or cv.empty: return td,{"거래수":0,"총수익률":0,"CAGR":np.nan,"MDD":0,"승률":np.nan,"Profit Factor":np.nan,"평균MFE":np.nan,"平均MAE":np.nan}
    cv=cv.sort_values("날짜").drop_duplicates("날짜",keep="last"); cv["고점"]=cv["자산"].cummax(); cv["낙폭"]=(cv["자산"]/cv["고점"]-1)*100
    final=float(cv.iloc[-1]["자산"]); total=(final/initial_cash-1)*100; days=max(1,(pd.Timestamp(cv.iloc[-1]["날짜"])-pd.Timestamp(cv.iloc[0]["날짜"])).days)
    cagr=((final/initial_cash)**(365.25/days)-1)*100 if final>0 else -100
    wins=int((td["순수익률"]>0).sum()); loss_abs=abs(float(td.loc[td["순수익률"]<0,"순수익률"].sum())); gains=float(td.loc[td["순수익률"]>0,"순수익률"].sum())
    pf=gains/loss_abs if loss_abs>0 else (np.inf if gains>0 else np.nan)
    return td,{"거래수":len(td),"총수익률":total,"CAGR":cagr,"MDD":float(cv["낙폭"].min()),"승률":wins/len(td)*100 if len(td) else np.nan,
               "Profit Factor":pf,"평균거래수익":float(td["순수익률"].mean()),"평균MFE":float(td["MFE"].mean()),"평균MAE":float(td["MAE"].mean()),
               "MFE_중앙값":float(td["MFE"].median()),"MAE_중앙값":float(td["MAE"].median())}
def bt_run_early_selection_validation(r,data,initial_cash=1_000_000,hold_days=60,fee=0.001,slip=0.0005):
    x=bt_build_early_selection_flags(r,data)
    if x.empty: return pd.DataFrame(),{},{}
    specs=[("D0_기존","D0 · 기존 D"),("D1_선행강세","D1 · D + 선행강세"),("D2_선행_미반영","D2 · D + 선행 + 미반영"),("D3_선행_미반영_과열회피","D3 · D + 선행 + 미반영 + 과열회피")]
    rows=[]; details={}; annual={}
    for flag,name in specs:
        td,m=bt_simulate_selection_validation(x,data,flag,initial_cash,hold_days,fee,slip); details[name]=td
        if not td.empty:
            z=td.copy(); z["청산일"]=pd.to_datetime(z["청산일"]); z["연도"]=z["청산일"].dt.year
            annual[name]=z.groupby("연도").agg(거래수=("순수익률","size"),평균수익=("순수익률","mean"),승률=("순수익률",lambda s:(s>0).mean()*100),평균MFE=("MFE","mean"),평균MAE=("MAE","mean")).reset_index()
        else: annual[name]=pd.DataFrame()
        rows.append({"전략":name,"신호수":int(x[flag].sum()),**m})
    cmp=pd.DataFrame(rows)
    if not cmp.empty:
        base=cmp.iloc[0]
        for col in ["CAGR","Profit Factor","승률","MDD","평균MFE","평균MAE"]:
            cmp["기준대비_"+col]=cmp[col]-base[col] if col in cmp.columns else np.nan
    return cmp,details,annual
def render_backtest_lab():
    """백테스트 LAB - 최종 화면 5개 섹션만 표시."""
    st.markdown(
        '<div class="hero"><div class="hero-name">🧪 백테스트 LAB</div>'
        '<div class="hero-code">기존 전략 검증 · 미래테마 · 선행 ETF · 미반영 · 과열회피</div></div>',
        unsafe_allow_html=True,
    )
    st.info(
        "연구용 백테스트입니다. 신호일 이후 데이터가 섞이지 않도록 다음 거래일 진입을 사용합니다. "
        "실제 주문체결·세금·배당·환전비용은 완전히 반영되지 않습니다."
    )
    st.markdown("### ① 백테스트 설정 / 실행")
    c1, c2, c3 = st.columns(3)
    with c1:
        start = st.date_input("시작일", date(2018, 1, 1), key="bt_start")
    with c2:
        end = st.date_input("종료일", date.today(), key="bt_end")
    with c3:
        step = st.select_slider(
            "검사 간격", options=[1, 3, 5, 10], value=5, key="bt_step",
            format_func=lambda x: "매일" if x == 1 else f"{x}거래일마다"
        )
    defaults = [
        "QQQ", "XLK", "SMH", "SOXX", "BOTZ", "ARKQ",
        "GLD", "TLT", "INDA", "EWY", "EWJ", "EEM"
    ]
    defaults = [x for x in defaults if x in BT_POOL]
    selected = st.multiselect(
        "검증 ETF", list(BT_POOL.keys()), defaults,
        key="bt_selected",
        format_func=lambda x: f"{x} · {BT_POOL[x]}"
    )
    v1, v2, v3 = st.columns(3)
    with v1:
        initial_cash = st.number_input(
            "초기자산", min_value=100000, value=1000000,
            step=100000, key="bt_final_cash"
        )
    with v2:
        hold_days = st.number_input(
            "보유기간", min_value=5, max_value=500, value=60,
            step=5, key="bt_final_hold"
        )
    with v3:
        fee = st.number_input(
            "편도 수수료", min_value=0.0, max_value=0.01, value=0.001,
            step=0.0001, format="%.4f", key="bt_final_fee"
        )
    slip = st.number_input(
        "편도 슬리피지", min_value=0.0, max_value=0.01, value=0.0005,
        step=0.0001, format="%.4f", key="bt_final_slip"
    )
    if st.button(
        "🚀 최종 3전략 백테스트 실행",
        type="primary", use_container_width=True, key="bt_run_final3"
    ):
        if start >= end:
            st.error("시작일은 종료일보다 빨라야 합니다.")
        elif len(selected) < 4:
            st.error("테마 비교를 위해 ETF를 4개 이상 선택하십시오.")
        else:
            with st.spinner("가격·지표·미래테마·선행신호를 계산하는 중입니다…"):
                try:
                    result, data = bt_run_strategy_backtest(start, end, selected, step)
                    st.session_state["strategy_result"] = result
                    st.session_state["strategy_data"] = data
                    st.session_state["final_compare"] = None
                    st.session_state["final_details"] = None
                    st.session_state["final_annual"] = None
                    st.session_state["bt_last_config"] = {
                        "start": str(start), "end": str(end),
                        "selected": selected, "step": step,
                        "hold_days": hold_days, "fee": fee, "slip": slip,
                    }
                    st.success(f"검사 완료 · {len(result):,}개 검사 시점")
                except Exception as ex:
                    st.error("백테스트 실행 중 오류가 발생했습니다.")
                    st.exception(ex)
    r = st.session_state.get("strategy_result")
    data = st.session_state.get("strategy_data")
    if r is None or data is None:
        st.caption("①의 실행 버튼을 누르면 ②~⑤ 결과가 표시됩니다.")
        return
    if r.empty:
        st.warning("백테스트 결과가 없습니다.")
        return
    st.markdown("---")
    st.markdown("### ② 최종 전략 비교 — C / D / D+시장환경")
    st.caption(
        "C = 미래테마 + 선행점수 / D = C + 가격구간 / D+M = D + 시장환경. "
        "동일한 진입일·보유기간·비용 조건으로 비교합니다."
    )
    if st.button(
        "🔬 C / D / D+시장환경 비교 실행",
        type="primary", use_container_width=True, key="bt_run_final_compare"
    ):
        with st.spinner("최종 후보 3전략을 동일 조건으로 비교하는 중입니다…"):
            try:
                final_cmp, final_details, final_annual = bt_run_final_strategy_compare(
                    r, data,
                    initial_cash=initial_cash,
                    hold_days=hold_days,
                    fee=fee,
                    slip=slip,
                )
                st.session_state["final_compare"] = final_cmp
                st.session_state["final_details"] = final_details
                st.session_state["final_annual"] = final_annual
            except Exception as ex:
                st.error("최종 전략 비교 중 오류가 발생했습니다.")
                st.exception(ex)
    final_cmp = st.session_state.get("final_compare")
    final_details = st.session_state.get("final_details")
    final_annual = st.session_state.get("final_annual")
    if isinstance(final_cmp, pd.DataFrame) and not final_cmp.empty:
        st.dataframe(final_cmp, use_container_width=True, hide_index=True)
        st.download_button(
            "📥 최종 3전략 비교 CSV",
            final_cmp.to_csv(index=False).encode("utf-8-sig"),
            "ETF_RADAR_FINAL_3_STRATEGY_COMPARISON.csv",
            "text/csv;charset=utf-8",
            use_container_width=True,
            key="bt_download_final_compare",
        )
    else:
        st.info("②의 비교 실행 버튼을 누르면 C / D / D+시장환경 결과가 표시됩니다.")
    st.markdown("---")
    st.markdown("### ③ 연도별 성과")
    st.caption("최종 3전략의 연도별 거래 수와 수익률을 비교합니다.")
    if isinstance(final_annual, dict) and final_annual:
        annual_frames = []
        for name, df in final_annual.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                z = df.copy()
                z.insert(0, "전략", name)
                annual_frames.append(z)
        if annual_frames:
            annual_all = pd.concat(annual_frames, ignore_index=True)
            st.dataframe(annual_all, use_container_width=True, hide_index=True)
            st.download_button(
                "📥 연도별 성과 CSV",
                annual_all.to_csv(index=False).encode("utf-8-sig"),
                "ETF_RADAR_FINAL_3_STRATEGY_ANNUAL.csv",
                "text/csv;charset=utf-8",
                use_container_width=True,
                key="bt_download_final_annual",
            )
        else:
            st.info("연도별 성과 데이터가 없습니다.")
    else:
        st.info("②의 최종 전략 비교를 먼저 실행하면 연도별 성과가 표시됩니다.")
    st.markdown("---")
    st.markdown("### ④ 거래 상세")
    st.caption("최종 3전략에서 실제로 발생한 진입·청산 거래를 확인합니다.")
    all_detail = None
    if isinstance(final_details, dict) and final_details:
        detail_frames = []
        for name, df in final_details.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                z = df.copy()
                z.insert(0, "전략", name)
                detail_frames.append(z)
        if detail_frames:
            all_detail = pd.concat(detail_frames, ignore_index=True)
    if isinstance(all_detail, pd.DataFrame) and not all_detail.empty:
        with st.expander("📋 거래 상세 열기", expanded=False):
            st.dataframe(
                all_detail,
                use_container_width=True,
                hide_index=True,
                height=420,
            )
        st.download_button(
            "📥 최종 전략 거래상세 CSV",
            all_detail.to_csv(index=False).encode("utf-8-sig"),
            "ETF_RADAR_FINAL_3_STRATEGY_TRADES.csv",
            "text/csv;charset=utf-8",
            use_container_width=True,
            key="bt_download_final_trades",
        )
    else:
        st.info("②의 최종 전략 비교를 먼저 실행하면 거래 상세가 표시됩니다.")
    st.markdown("---")
    st.markdown("### ⑤ 백테스트 결과 검증")
    st.caption("최종 전략 결과를 추가 검증합니다.")
    if st.button("🔬 TRUE WALK-FORWARD 검증",use_container_width=True,key="bt_run_true_wf"):
        with st.spinner("TRUE WALK-FORWARD 검증을 실행하는 중입니다…"):
            try:
                wf_result=run_true_walk_forward(start,end,selected)
                st.session_state["true_wf_result"]=wf_result
            except Exception as ex:
                st.error("TRUE WALK-FORWARD 검증 중 오류가 발생했습니다.")
                st.exception(ex)
    wf_result=st.session_state.get("true_wf_result")
    if isinstance(wf_result,dict):
        st.dataframe(wf_result.get("summary",pd.DataFrame()),use_container_width=True,hide_index=True)
def render_true_walk_forward():
    st.markdown('<div class="hero"><div class="hero-name">🧬 TRUE WALK-FORWARD</div><div class="hero-code">과거로 학습 · 미래구간 OOS · 신호일 이후 데이터 차단</div></div>',unsafe_allow_html=True)
    st.info("실제 투자 시점에서 사용할 수 있었던 정보만으로 신호를 만들고, 이후 구간을 OOS로 분리해 검증합니다.")
    c1,c2,c3=st.columns(3)
    with c1: start=st.date_input("WF 시작일",date(2018,1,1),key="wf_start")
    with c2: end=st.date_input("WF 종료일",date.today(),key="wf_end")
    with c3: train_years=st.number_input("학습기간",min_value=2,max_value=10,value=4,step=1,key="wf_train")
    if st.button("🚀 TRUE WALK-FORWARD 실행",type="primary",use_container_width=True,key="wf_run"):
        with st.spinner("TRUE WALK-FORWARD를 실행하는 중입니다…"):
            try:
                result=run_true_walk_forward(start,end,train_years)
                st.session_state["wf_result"]=result
            except Exception as ex:
                st.error("TRUE WALK-FORWARD 실행 중 오류가 발생했습니다.")
                st.exception(ex)
    result=st.session_state.get("wf_result")
    if not result: return
    c1,c2,c3=st.columns(3)
    with c1: st.metric("신호 수", len(result["signals"]))
    with c2: st.metric("OOS 신호 수", len(result["oos"]))
    with c3: st.metric("전체 거래 수", len(result["trades"]))
    st.markdown("### OOS 연도별 결과")
    st.dataframe(result["annual"],use_container_width=True,hide_index=True)
    st.markdown("### 최근 생성된 신호")
    st.dataframe(result["signals"].sort_values("date",ascending=False).head(30),use_container_width=True,hide_index=True)
    files={
        "TRUE_WALK_FORWARD_SUMMARY.csv":result["summary"],
        "TRUE_WALK_FORWARD_SIGNALS.csv":result["signals"],
        "TRUE_WALK_FORWARD_TRADES.csv":result["trades"],
        "TRUE_WALK_FORWARD_ANNUAL.csv":result["annual"],
        "TRUE_WALK_FORWARD_OOS.csv":result["oos"],
    }
    st.markdown("### CSV 결과 다운로드")
    cols=st.columns(3)
    for i,(name,df) in enumerate(files.items()):
        with cols[i%3]:
            st.download_button(f"📥 {name}",df.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig"),file_name=name,mime="text/csv",use_container_width=True,key="wf_dl_"+name)
WF_HORIZONS = [5, 10, 20, 40, 60]
def wf_trade_horizon(data, sig, strategy, hold_days):
    code = sig.get("etf")
    d = data.get(code)
    if d is None or d.empty:
        return None
    dt = pd.Timestamp(sig["date"])
    pos = d.index.searchsorted(dt, side="right")
    if pos >= len(d):
        return None
    entry_i = pos
    exit_i = min(entry_i + int(hold_days), len(d) - 1)
    entry_date = d.index[entry_i]
    exit_date = d.index[exit_i]
    entry = float(d.iloc[entry_i].get("Open", d.iloc[entry_i].get("Close", np.nan)))
    exit_px = float(d.iloc[exit_i].get("Close", np.nan))
    if not np.isfinite(entry) or entry <= 0 or not np.isfinite(exit_px):
        return None
    gross = (exit_px / entry - 1) * 100
    net = gross - (WF_FEE + WF_SLIPPAGE) * 2 * 100
    return {
        "strategy": strategy, "보유기간": int(hold_days),
        "signal_date": dt.date().isoformat(),
        "entry_date": entry_date.date().isoformat(),
        "exit_date": exit_date.date().isoformat(),
        "ETF": code, "ETF명": sig.get("name", code), "테마": sig.get("theme", ""),
        "테마점수": round(float(sig.get("theme_score", 0)), 2),
        "선행점수": round(float(sig.get("lead_score", 0)), 2),
        "가격구간": sig.get("price_zone", ""),
        "시장통과": bool(sig.get("market_pass", False)),
        "진입가": round(entry, 4), "청산가": round(exit_px, 4),
        "수익률": round(gross, 4), "비용차감후수익률": round(net, 4),
        "보유거래일": int(exit_i-entry_i),
    }
def wf_make_trades_horizon(data, signals, strategy, hold_days):
    candidates = [x for x in signals if x.get(strategy, False)]
    trades=[]; last_exit=None
    for sig in sorted(candidates, key=lambda x: x["date"]):
        t=wf_trade_horizon(data, sig, strategy, hold_days)
        if t is None: continue
        ed=pd.Timestamp(t["entry_date"]); xd=pd.Timestamp(t["exit_date"])
        if last_exit is not None and ed <= last_exit: continue
        trades.append(t); last_exit=xd
    return pd.DataFrame(trades)
def wf_add_final_strategy_flags(signals):
    """D를 기준으로 필터의 독립/복합 기여도를 계산한다."""
    out=[]
    for s in signals:
        x=dict(s)
        d=bool(x.get("D",False)); t=bool(x.get("trend_pass",False)); mv=bool(x.get("momvol_pass",False)); m=bool(x.get("market_pass",False))
        x["BASE_D"]=d
        x["D+TREND"]=d and t
        x["D+MOMVOL"]=d and mv
        x["D+MARKET"]=d and m
        x["D+T+MV"]=d and t and mv
        x["D+T+M"]=d and t and m
        x["D+MV+M"]=d and mv and m
        x["D+T+MV+M"]=d and t and mv and m
        out.append(x)
    return out
def wf_final_summary(trades):
    if trades is None or trades.empty:
        return {"거래수":0,"승률":0,"평균수익률":0,"누적복리":0,"MDD":0}
    r=pd.to_numeric(trades["비용차감후수익률"],errors="coerce").dropna()/100
    if r.empty: return {"거래수":0,"승률":0,"평균수익률":0,"누적복리":0,"MDD":0}
    eq=(1+r).cumprod(); dd=eq/eq.cummax()-1
    return {"거래수":int(len(r)),"승률":float((r>0).mean()*100),"평균수익률":float(r.mean()*100),"누적복리":float((eq.iloc[-1]-1)*100),"MDD":float(dd.min()*100)}
def render_final_validation():
    st.markdown('<div class="hero"><div class="hero-name">🏁 FINAL VALIDATION LAB</div><div class="hero-code">D+M 최종검증 · 매일 신호 · 보유기간 5/10/20/40/60일 · 조건 기여도 · OOS</div></div>', unsafe_allow_html=True)
    st.info("이 화면은 전략을 새로 만드는 곳이 아닙니다. 현재 D+M 후보를 고정하고 표본 수·보유기간·필터 기여도·OOS를 동시에 검증합니다.")
    c1,c2,c3=st.columns(3)
    with c1: start=st.date_input("검증 시작일",date(2018,1,1),key="fv_start")
    with c2: end=st.date_input("검증 종료일",date.today(),key="fv_end")
    with c3: oos_year=st.number_input("OOS 시작연도",min_value=2018,max_value=2030,value=2024,step=1,key="fv_oos")
    st.markdown("**검사 간격: 매일(1거래일)** · **비용: 편도 수수료 0.10% + 슬리피지 0.05%**")
    if st.button("🚀 FINAL VALIDATION 실행",type="primary",use_container_width=True,key="fv_run"):
        if start>=end:
            st.error("시작일은 종료일보다 빨라야 합니다."); return
        with st.status("최종 검증을 실행하는 중...",expanded=True) as status:
            try:
                status.write("① 현재 ETF MASTER에서 테마군 구성")
                universe,theme_members,codes=wf_build_universe()
                status.write(f"② ETF {len(codes)}개 가격 데이터 다운로드")
                data=wf_download_history(tuple(codes)); data={k:v for k,v in data.items() if v is not None and not v.empty}
                if WF_BENCH not in data: raise RuntimeError("KODEX 200 데이터를 가져오지 못했습니다.")
                bench=data[WF_BENCH]
                dates=bench.index[(bench.index>=pd.Timestamp(start))&(bench.index<=pd.Timestamp(end))]
                signals=[]
                for i,dt in enumerate(dates):
                    snap=wf_snapshot(data,theme_members,dt)
                    if snap: signals.append(snap)
                if not signals: raise RuntimeError("유효한 신호가 없습니다.")
                signals=wf_add_final_strategy_flags(signals)
                status.write(f"③ 매일 검사 완료: {len(signals):,}개 신호")
                strategy_keys=["BASE_D","D+TREND","D+MOMVOL","D+MARKET","D+T+MV","D+T+M","D+MV+M","D+T+MV+M"]
                labels={"BASE_D":"BASE D","D+TREND":"D + 추세","D+MOMVOL":"D + 모멘텀·거래량","D+MARKET":"D + 시장환경","D+T+MV":"D + 추세 + 모멘텀·거래량","D+T+M":"D + 추세 + 시장환경","D+MV+M":"D + 모멘텀·거래량 + 시장환경","D+T+MV+M":"D + 추세 + 모멘텀·거래량 + 시장환경"}
                all_summary=[]; all_trades=[]
                for hold in WF_HORIZONS:
                    for key in strategy_keys:
                        td=wf_make_trades_horizon(data,signals,key,hold)
                        m=wf_final_summary(td)
                        m.update({"전략":labels[key],"조건키":key,"보유기간":hold})
                        all_summary.append(m)
                        if not td.empty: all_trades.append(td)
                summary=pd.DataFrame(all_summary)
                trades=pd.concat(all_trades,ignore_index=True) if all_trades else pd.DataFrame()
                sigdf=pd.DataFrame(signals)
                oos=sigdf[pd.to_datetime(sigdf["date"]).dt.year>=int(oos_year)].copy()
                oos_rows=[]
                for hold in WF_HORIZONS:
                    for key in strategy_keys:
                        td=wf_make_trades_horizon(data,signals,key,hold)
                        if not td.empty:
                            z=td[pd.to_datetime(td["signal_date"]).dt.year>=int(oos_year)].copy()
                            if not z.empty:
                                m=wf_final_summary(z); m.update({"전략":labels[key],"조건키":key,"보유기간":hold})
                                oos_rows.append(m)
                oos_summary=pd.DataFrame(oos_rows)
                st.session_state["fv_result"]={"summary":summary,"trades":trades,"signals":sigdf,"oos_signals":oos,"oos_summary":oos_summary}
                status.update(label="FINAL VALIDATION 완료",state="complete",expanded=False)
            except Exception as ex:
                status.update(label="최종 검증 실패",state="error",expanded=True); st.exception(ex); return
    r=st.session_state.get("fv_result")
    if not r: return
    st.markdown("### 1. 보유기간별 전체 결과")
    pivot=r["summary"].pivot_table(index="전략",columns="보유기간",values="누적복리",aggfunc="first")
    st.dataframe(pivot.round(2),use_container_width=True)
    st.markdown("### 2. 전체 상세 결과")
    st.dataframe(r["summary"].sort_values(["보유기간","누적복리"],ascending=[True,False]),use_container_width=True,hide_index=True)
    st.markdown("### 3. OOS 결과")
    st.dataframe(r["oos_summary"].sort_values(["보유기간","누적복리"],ascending=[True,False]),use_container_width=True,hide_index=True)
    st.markdown("### 4. 신호 표본")
    st.write(f"전체 신호 {len(r['signals']):,}개 / OOS 신호 {len(r['oos_signals']):,}개")
    st.dataframe(r["signals"].sort_values("date",ascending=False).head(50),use_container_width=True,hide_index=True)
    files={
        "FINAL_VALIDATION_SUMMARY.csv":r["summary"],
        "FINAL_VALIDATION_TRADES.csv":r["trades"],
        "FINAL_VALIDATION_SIGNALS.csv":r["signals"],
        "FINAL_VALIDATION_OOS_SUMMARY.csv":r["oos_summary"],
        "FINAL_VALIDATION_OOS_SIGNALS.csv":r["oos_signals"],
    }
    st.markdown("### 5. CSV 다운로드")
    cols=st.columns(3)
    for i,(name,df) in enumerate(files.items()):
        with cols[i%3]: st.download_button(f"📥 {name}",df.to_csv(index=False,encoding="utf-8-sig").encode("utf-8-sig"),file_name=name,mime="text/csv",use_container_width=True,key="fv_dl_"+name)
init_state()
st.markdown(
    """
    <div class="app-header">
        <div class="app-title">ETF RADAR</div>
        <div class="app-subtitle">ETF 추세 · 모멘텀 · 거래량 · 핵심가격 · 대응 시나리오</div>
    </div>
    """,
    unsafe_allow_html=True
)
nav = st.radio(
    "메뉴",
    ["🏆 최종 타겟", "🚀 미래테마", "📊 내 ETF", "🧪 백테스트", "🧬 TRUE 검증", "🏁 최종검증"],
    horizontal=True,
    key="main_page",
    label_visibility="collapsed"
)
if nav == "🏆 최종 타겟":
    render_final_target()
elif nav == "🚀 미래테마":
    render_future_theme()
elif nav == "📊 내 ETF":
    render_my_etf()
elif nav == "🧪 백테스트":
    render_backtest_lab()
elif nav == "🧬 TRUE 검증":
    render_true_walk_forward()
elif nav == "🏁 최종검증":
    render_final_validation()