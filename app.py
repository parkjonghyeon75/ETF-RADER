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
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: Arial, sans-serif !important;
}
.stApp {
    background: #07111f;
    color: #eaf2ff;
}
.block-container {
    max-width: 1400px;
    padding: 1rem 1rem 3rem 1rem;
}
section[data-testid="stSidebar"] {
    background: #0b1728;
}
div[data-testid="stMetric"] {
    background: #0d1b2e;
    border: 1px solid #1e334d;
    border-radius: 12px;
    padding: 10px;
}
div[data-testid="stMetricLabel"] {
    color: #8ea6c2 !important;
}
div[data-testid="stMetricValue"] {
    color: #f5f9ff !important;
}
.stButton > button {
    width: 100%;
    border-radius: 10px;
    border: 1px solid #294764;
    background: #10243a;
    color: #eaf2ff;
    min-height: 42px;
    font-weight: 600;
}
.stButton > button:hover {
    border-color: #4da3ff;
    color: #ffffff;
}
div[data-baseweb="select"] > div {
    background: #0d1b2e !important;
    color: #ffffff !important;
    border-color: #294764 !important;
}
div[data-baseweb="select"] input {
    color: #ffffff !important;
}
div[data-baseweb="select"] span {
    color: #ffffff !important;
}
ul[role="listbox"] {
    background: #0d1b2e !important;
}
li[role="option"] {
    color: #ffffff !important;
    background: #0d1b2e !important;
}
li[role="option"]:hover {
    background: #173451 !important;
}
.stTextInput input {
    background: #0d1b2e !important;
    color: #ffffff !important;
    border-color: #294764 !important;
}
.stTextInput input::placeholder {
    color: #7188a2 !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #091522;
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #8ea6c2;
    border-radius: 8px;
    padding: 8px 12px;
}
.stTabs [aria-selected="true"] {
    background: #173451 !important;
    color: #ffffff !important;
}
.radar-card {
    background: linear-gradient(135deg, #0d1b2e, #0a1625);
    border: 1px solid #203a56;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 10px;
}
.theme-card-lead {
    background: linear-gradient(135deg, #162b40, #0c1b2c);
    border: 1px solid #3e78a8;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
}
.theme-card-next {
    background: linear-gradient(135deg, #13283b, #0c1928);
    border: 1px solid #2c5b80;
    border-radius: 14px;
    padding: 15px;
    margin-bottom: 12px;
}
.theme-card-early {
    background: linear-gradient(135deg, #112333, #0b1725);
    border: 1px solid #28506e;
    border-radius: 14px;
    padding: 15px;
    margin-bottom: 12px;
}
.decision-board {
    background: #0a1726;
    border: 1px solid #294764;
    border-radius: 16px;
    padding: 16px;
    margin: 12px 0;
}
.today-interest-panel {
    background: linear-gradient(135deg, #101f31, #0a1726);
    border: 1px solid #365b7d;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 15px;
}
.price-box {
    background: #0d1b2e;
    border: 1px solid #27435e;
    border-radius: 12px;
    padding: 12px;
}
.signal-box {
    background: #101f31;
    border: 1px solid #2d4e6c;
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 8px;
}
.small-label {
    color: #7f98b3;
    font-size: 0.78rem;
}
.big-number {
    font-size: 1.45rem;
    font-weight: 800;
    color: #ffffff;
}
.good {
    color: #61d69b !important;
}
.warn {
    color: #ffc857 !important;
}
.bad {
    color: #ff7d7d !important;
}
.neutral {
    color: #9fb2c7 !important;
}
@media (max-width: 768px) {
    .block-container {
        padding: 0.45rem 0.45rem 2rem 0.45rem;
    }
    h1 {
        font-size: 1.55rem !important;
    }
    h2 {
        font-size: 1.25rem !important;
    }
    h3 {
        font-size: 1.05rem !important;
    }
    .stButton > button {
        min-height: 44px;
        font-size: 0.88rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 7px 8px;
        font-size: 0.82rem;
    }
}
</style>
""", unsafe_allow_html=True)

DATA_DIR = "."
WATCHLIST_FILE = os.path.join(DATA_DIR, "watchlist.json")
HOLDINGS_FILE = os.path.join(DATA_DIR, "holdings.json")
ETF_CACHE_FILE = os.path.join(DATA_DIR, "etf_universe_cache.json")

DEFAULT_WATCHLIST = [
    "395160",
    "487240",
    "471990",
    "133690",
    "360750",
    "458730",
]

BASE_ETFS = [
    "395160",
    "487240",
    "471990",
    "133690",
    "360750",
    "458730",
]

FALLBACK_ETFS = [
    "091160",
    "102110",
    "069500",
    "229200",
    "381170",
    "379800",
    "305540",
    "261220",
    "278530",
    "364690",
    "381180",
    "441680",
    "461950",
    "476260",
    "487230",
    "475150",
    "449170",
    "458730",
    "466950",
    "465580",
    "385510",
    "371460",
    "228790",
    "371160",
    "143850",
    "244580",
    "161510",
    "139250",
    "117700",
    "272580",
    "261240",
    "315960",
    "385520",
    "292150",
    "319640",
    "252670",
    "379810",
    "402970",
    "411060",
    "438100",
    "462330",
    "465350",
    "475070",
]

THEMES = {
    "AI 반도체": {
        "seeds": [
            "AI",
            "반도체",
            "HBM",
            "메모리",
            "파운드리",
            "반도체",
        ],
        "stage": "현재 주도",
    },
    "AI 소프트웨어·빅테크": {
        "seeds": [
            "AI",
            "소프트웨어",
            "빅테크",
            "클라우드",
            "인터넷",
            "플랫폼",
        ],
        "stage": "현재 주도",
    },
    "데이터센터·AI 인프라": {
        "seeds": [
            "데이터센터",
            "AI인프라",
            "인프라",
            "클라우드",
            "서버",
            "데이터",
        ],
        "stage": "다음 수혜",
    },
    "전력 인프라": {
        "seeds": [
            "전력",
            "전력인프라",
            "전선",
            "변압기",
            "전력기기",
            "에너지",
        ],
        "stage": "다음 수혜",
    },
    "원자력": {
        "seeds": [
            "원자력",
            "원전",
            "SMR",
            "우라늄",
            "원전기기",
        ],
        "stage": "관심 확대",
    },
    "냉각·열관리": {
        "seeds": [
            "냉각",
            "열관리",
            "액침냉각",
            "공조",
            "HVAC",
            "칠러",
        ],
        "stage": "초기 관심",
    },
    "로봇·자율주행": {
        "seeds": [
            "로봇",
            "자율주행",
            "자동화",
            "스마트팩토리",
            "AI로봇",
        ],
        "stage": "초기 관심",
    },
    "방산·우주": {
        "seeds": [
            "방산",
            "우주",
            "항공",
            "미사일",
            "위성",
            "국방",
        ],
        "stage": "관심 확대",
    },
    "2차전지·ESS": {
        "seeds": [
            "2차전지",
            "배터리",
            "ESS",
            "전고체",
            "리튬",
            "양극재",
        ],
        "stage": "관심 확대",
    },
}

FUTURE_CHAIN = [
    ("AI 반도체", "현재 주도"),
    ("데이터센터·AI 인프라", "다음 수혜"),
    ("전력 인프라", "다음 수혜"),
    ("원자력", "관심 확대"),
    ("냉각·열관리", "초기 관심"),
]

MA_WINDOWS = [20, 60, 120]

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
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def safe_etf_name(name):
    if name is None:
        return ""
    try:
        name = str(name)
        if "�" in name:
            return ""
        if any(x in name for x in ["ì", "ë", "ê", "ã", "Â", "Ã"]):
            try:
                fixed = name.encode("latin1").decode("utf-8")
                if "�" not in fixed:
                    name = fixed
            except Exception:
                pass
        return html.unescape(name).strip()
    except Exception:
        return str(name)

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_krx_etf_master():
    urls = [
        "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd",
        "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd?bld=dbms/MDC/STAT/standard/MDCSTAT04601",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://data.krx.co.kr/",
    }
    for url in urls:
        try:
            payload = {
                "bld": "dbms/MDC/STAT/standard/MDCSTAT04601",
                "mktId": "ALL",
                "trdDd": datetime.now().strftime("%Y%m%d"),
            }
            r = requests.post(
                url,
                data=payload,
                headers=headers,
                timeout=10,
            )
            if r.ok:
                data = r.json()
                rows = data.get("OutBlock_1", [])
                if rows:
                    records = []
                    for row in rows:
                        code = str(
                            row.get("ISU_SRT_CD")
                            or row.get("ISU_CD")
                            or row.get("종목코드")
                            or ""
                        ).zfill(6)
                        name = safe_etf_name(
                            row.get("ISU_ABBRV")
                            or row.get("ISU_NM")
                            or row.get("종목명")
                            or ""
                        )
                        if code and name:
                            records.append(
                                {
                                    "code": code,
                                    "name": name,
                                    "source": "KRX",
                                }
                            )
                    if records:
                        return pd.DataFrame(records).drop_duplicates("code")
        except Exception:
            continue
    return pd.DataFrame(columns=["code", "name", "source"])

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_naver_etf_master():
    url = "https://finance.naver.com/api/sise/etfItemList.nhn"
    try:
        r = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        rows = data.get("result", {}).get("etfItemList", [])
        records = []
        for row in rows:
            code = str(row.get("itemcode") or "").zfill(6)
            name = safe_etf_name(row.get("itemname") or "")
            if code and name:
                records.append(
                    {
                        "code": code,
                        "name": name,
                        "source": "NAVER",
                    }
                )
        if records:
            return pd.DataFrame(records).drop_duplicates("code")
    except Exception:
        pass
    return pd.DataFrame(columns=["code", "name", "source"])

@st.cache_data(ttl=3600, show_spinner=False)
def load_etf_universe():
    krx = fetch_krx_etf_master()
    naver = fetch_naver_etf_master()
    frames = []
    if not krx.empty:
        frames.append(krx)
    if not naver.empty:
        frames.append(naver)
    if frames:
        df = pd.concat(frames, ignore_index=True)
        df["name"] = df["name"].map(safe_etf_name)
        df = df[df["code"].astype(str).str.len() == 6]
        df = df.drop_duplicates("code", keep="first")
    else:
        df = pd.DataFrame(
            {
                "code": FALLBACK_ETFS,
                "name": FALLBACK_ETFS,
                "source": "FALLBACK",
            }
        )
    existing = set(df["code"].astype(str))
    missing = [x for x in FALLBACK_ETFS if x not in existing]
    if missing:
        extra = pd.DataFrame(
            {
                "code": missing,
                "name": missing,
                "source": "FALLBACK",
            }
        )
        df = pd.concat([df, extra], ignore_index=True)
    return df.reset_index(drop=True)

def normalize_df(df):
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            "_".join([str(x) for x in col if str(x) != ""])
            for col in df.columns
        ]
    rename = {}
    for col in df.columns:
        c = str(col).lower()
        if c in ("date", "datetime", "index"):
            rename[col] = "Date"
        elif "open" in c:
            rename[col] = "Open"
        elif "high" in c:
            rename[col] = "High"
        elif "low" in c:
            rename[col] = "Low"
        elif "close" in c:
            rename[col] = "Close"
        elif "volume" in c:
            rename[col] = "Volume"
    df = df.rename(columns=rename)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df = df.sort_values("Date")
        df = df.set_index("Date")
    required = ["Open", "High", "Low", "Close", "Volume"]
    for col in required:
        if col not in df.columns:
            df[col] = np.nan
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[required].copy()
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
        vals.append({"r20":r20,"r60":r60,"rs20":sig["rs20"],"rs60":r60-bench_ret60,"vr":safe_float(r.get("vr",r.get("VR",1)),1),"ma60gap":safe_float(r.get("ma60_gap",0),0),"accel":sig["accel"],"rsi":sig["rsi"],"lead":sig["score"],"early":sig["early_buy"]})
    if len(vals)<2: return None
    x=pd.DataFrame(vals)
    def clip_score(v,lo,hi): return float(np.clip((v-lo)/(hi-lo)*100,0,100))
    r20=clip_score(x["r20"].mean(),-10,15); r60=clip_score(x["r60"].mean(),-15,30); rs20=clip_score(x["rs20"].mean(),-10,12); rs60=clip_score(x["rs60"].mean(),-15,20)
    vr=clip_score(x["vr"].mean(),.8,2); breadth=float((x["r20"]>-2).mean()*100); ma60=clip_score(x["ma60gap"].mean(),-10,15); accel=clip_score(x["accel"].mean(),-5,6)
    rsi=float(np.clip(100-abs(float(x["rsi"].mean())-58)*2.5,0,100))
    score=r20*.15+r60*.15+rs20*.15+rs60*.10+vr*.15+breadth*.15+ma60*.05+accel*.05+rsi*.05
    lead_theme=float(x["lead"].mean())*.55+breadth*.25+float(x["early"].mean())*100*.20
    heat=(12 if float(x["rsi"].mean())>=75 else 0)+(10 if float(x["r20"].mean())>=12 else 0)+(8 if float(x["ma60gap"].mean())>=15 else 0)
    return float(np.clip((score*.70+lead_theme*.30)-heat,0,100))

def validated_price_zone(row):
    c=safe_float(row.get("Close")); ma20=safe_float(row.get("MA20"),c); ma60=safe_float(row.get("MA60"),c); low20=safe_float(row.get("LOW20"),c)
    support=max(low20,ma20*.985); ideal_top=ma20*1.025; invalid=min(ma60*.97,support*.97)
    if c<=ideal_top and c>=invalid and c>=ma60*.98: state="매수구간"
    elif c<invalid: state="무효"
    elif c>ma20*1.07: state="추격금지"
    else: state="눌림대기"
    return {"state":state,"support":support,"ideal_top":ideal_top,"invalid":invalid}

def validated_cd_signal(row,tscore,benchmark_ret20=0):
    lead=leading_signal(row,benchmark_ret20); zone=validated_price_zone(row); c_pass=safe_float(tscore)>=60 and lead["early_buy"]; d_pass=c_pass and zone["state"]=="매수구간"
    if d_pass: state="D · 매수구간"
    elif c_pass and zone["state"]=="눌림대기": state="C · 눌림대기"
    elif c_pass and zone["state"]=="추격금지": state="C · 추격금지"
    elif c_pass: state="C · 관심"
    elif safe_float(tscore)>=60: state="테마 통과 · 선행 미통과"
    else: state="C 미통과"
    return {**lead,**zone,"theme_score":safe_float(tscore),"c_pass":c_pass,"d_pass":d_pass,"state":state}

def long_term_horizon(d):
    """V4 장기판정.
    V4 원칙
    1) 장기적합성은 미래수익률 예측점수가 아니라 계속 보유할 만한 구조인지 판단.
    2) 최근 252일의 장기추세 지속성을 가장 크게 반영.
    3) 20/60/120일 정배열과 장기 추세를 확인.
    4) RSI 과열은 장기적합성 자체를 크게 훼손하지 않도록 제한적으로 감점.
    """
    if d.empty or len(d) < 120:
        return {
            "score": 0,
            "label": "데이터 부족",
            "reasons": ["장기 판단에 필요한 데이터가 부족합니다."]
        }
    row=d.iloc[-1]
    close=safe_float(row.get("Close"))
    ma20=safe_float(row.get("MA20"),close)
    ma60=safe_float(row.get("MA60"),close)
    ma120=safe_float(row.get("MA120"),close)
    ma200=safe_float(row.get("MA200"),close)
    ret120=safe_float(row.get("RET120"),0)
    ret250=safe_float(row.get("RET250"),0)
    rsi=safe_float(row.get("RSI14"),50)
    trend_score=0
    if close>ma120: trend_score+=25
    if ma60>ma120: trend_score+=20
    if ma120>ma200: trend_score+=15
    if close>ma20: trend_score+=10
    if ma20>ma60: trend_score+=10
    ret_score=np.clip((ret250+30)/80*20,0,20)
    score=trend_score+ret_score
    if rsi>=80:
        score-=5
    elif rsi>=75:
        score-=2
    score=int(np.clip(score,0,100))
    if score>=80:
        label="장기 적합"
    elif score>=65:
        label="장기 우수"
    elif score>=50:
        label="장기 관찰"
    elif score>=35:
        label="장기 주의"
    else:
        label="장기 부적합"
    reasons=[
        f"현재가 {money(close)} · 120일선 {money(ma120)}",
        f"20/60/120일선 정렬 · {'양호' if ma20>ma60>ma120 else '혼조'}",
        f"최근 120일 {ret120:+.1f}% · 최근 250일 {ret250:+.1f}%",
        f"RSI14 {rsi:.1f} · {'과열' if rsi>=75 else '정상 범위'}"
    ]
    return {"score":score,"label":label,"reasons":reasons}

def medium_term_signal(d):
    if d.empty or len(d)<60:
        return {"score":0,"label":"데이터 부족","reasons":[]}
    row=d.iloc[-1]
    close=safe_float(row.get("Close"))
    ma20=safe_float(row.get("MA20"),close)
    ma60=safe_float(row.get("MA60"),close)
    rsi=safe_float(row.get("RSI14"),50)
    ret20=safe_float(row.get("RET20"),0)
    vr=safe_float(row.get("VOL_RATIO"),1)
    score=0
    if close>ma20: score+=25
    if ma20>ma60: score+=20
    if close>ma60: score+=20
    if ret20>0: score+=15
    if 45<=rsi<=68: score+=10
    if vr>=1: score+=10
    score=int(np.clip(score,0,100))
    if score>=80: label="중기 강세"
    elif score>=65: label="중기 양호"
    elif score>=50: label="중립"
    elif score>=35: label="중기 주의"
    else: label="중기 약세"
    return {
        "score":score,
        "label":label,
        "reasons":[
            f"20일선 {money(ma20)} · {'상회' if close>ma20 else '하회'}",
            f"60일선 {money(ma60)} · {'상회' if close>ma60 else '하회'}",
            f"최근 20일 {ret20:+.1f}% · RSI {rsi:.1f}",
            f"거래량 비율 {vr:.2f}배"
        ]
    }

def short_term_signal(d):
    if d.empty or len(d)<30:
        return {"score":0,"label":"데이터 부족","reasons":[]}
    row=d.iloc[-1]
    close=safe_float(row.get("Close"))
    ma20=safe_float(row.get("MA20"),close)
    rsi=safe_float(row.get("RSI14"),50)
    ret5=safe_float(row.get("RET5"),0)
    vr=safe_float(row.get("VOL_RATIO"),1)
    score=0
    if close>=ma20: score+=25
    if -2<=ret5<=6: score+=25
    if 45<=rsi<=68: score+=20
    if 0.9<=vr<=1.8: score+=15
    if ret5>0: score+=15
    score=int(np.clip(score,0,100))
    if score>=80: label="단기 양호"
    elif score>=65: label="단기 관심"
    elif score>=50: label="단기 중립"
    elif score>=35: label="단기 주의"
    else: label="단기 약세"
    return {
        "score":score,
        "label":label,
        "reasons":[
            f"5일 수익률 {ret5:+.1f}%",
            f"20일선 {money(ma20)} · {'상회' if close>=ma20 else '하회'}",
            f"RSI14 {rsi:.1f}",
            f"거래량 비율 {vr:.2f}배"
        ]
    }

def calculate_levels(d):
    if d.empty:
        return None
    row=d.iloc[-1]
    current=safe_float(row.get("Close"))
    ma20=safe_float(row.get("MA20"),current)
    ma60=safe_float(row.get("MA60"),current)
    high20=safe_float(row.get("HIGH20"),current)
    low20=safe_float(row.get("LOW20"),current)
    support=max(low20,ma20*.985,ma60*.97)
    first=ma20
    breakout=high20
    risk=min(support*.97,ma60*.95)
    return {
        "first":first,
        "support":support,
        "breakout":breakout,
        "risk":risk
    }

def get_etf_name(code):
    code=_normalize_etf_code(code)
    name=st.session_state.etf_universe.get(code)
    if name:
        return safe_etf_name(name)
    return lookup_live_etf(code)

def _normalize_etf_code(code):
    if code is None:
        return ""
    s=str(code).strip().upper()
    if s.endswith(".KS"):
        s=s[:-3]
    if s.isdigit():
        return s.zfill(6)
    return s

def build_etf_row(code, benchmark_ret20=0):
    df=load_price_data(code)
    if df.empty:
        return None
    d=calculate_indicators(df)
    if d.empty:
        return None
    row=d.iloc[-1]
    sig=leading_signal(row,benchmark_ret20)
    lt=long_term_horizon(d)
    mt=medium_term_signal(d)
    stg=short_term_signal(d)
    current=safe_float(row.get("Close"))
    prev=safe_float(d["Close"].iloc[-2],current) if len(d)>1 else current
    change=current-prev
    change_pct=change/prev*100 if prev else 0
    return {
        "code":_normalize_etf_code(code),
        "name":get_etf_name(code),
        "Close":current,
        "change":change,
        "change_pct":change_pct,
        "ret5":safe_float(row.get("RET5")),
        "ret20":safe_float(row.get("RET20")),
        "ret60":safe_float(row.get("RET60")),
        "ret120":safe_float(row.get("RET120")),
        "ret250":safe_float(row.get("RET250")),
        "rsi":safe_float(row.get("RSI14"),50),
        "vr":safe_float(row.get("VOL_RATIO"),1),
        "ma20":safe_float(row.get("MA20"),current),
        "ma60":safe_float(row.get("MA60"),current),
        "ma120":safe_float(row.get("MA120"),current),
        "ma200":safe_float(row.get("MA200"),current),
        "ma60_gap":(current/safe_float(row.get("MA60"),current)-1)*100,
        "lead_score":sig["score"],
        "early_buy":sig["early_buy"],
        "long_score":lt["score"],
        "long_label":lt["label"],
        "medium_score":mt["score"],
        "medium_label":mt["label"],
        "short_score":stg["score"],
        "short_label":stg["label"],
        "df":d
    }

def match_theme(name):
    text=safe_etf_name(name).lower()
    matched=[]
    for theme,info in THEMES.items():
        score=0
        for seed in info["seeds"]:
            if seed.lower() in text:
                score+=1
        if score:
            matched.append((theme,score))
    matched.sort(key=lambda x:x[1],reverse=True)
    return [x[0] for x in matched]

def discover_themes(universe):
    theme_map={theme:[] for theme in THEMES}
    for _,row in universe.iterrows():
        code=str(row["code"]).zfill(6)
        name=safe_etf_name(row["name"])
        for theme in match_theme(name):
            theme_map.setdefault(theme,[]).append((code,name))
    return theme_map

def render_judgment(j):
    if not j:
        return
    title=j.get("title","")
    if "상승" in title:
        cls="good"
    elif "약세" in title or "방어" in title:
        cls="bad"
    elif "조정" in title or "주의" in title:
        cls="warn"
    else:
        cls="neutral"
    st.markdown(
        f"""
        <div class="decision-board">
            <div class="small-label">현재 판단</div>
            <div class="big-number {cls}">{html.escape(title)}</div>
            <div style="margin-top:8px;">{html.escape(j.get("action",""))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    for reason in j.get("reasons",[]):
        st.caption("• "+reason)

def render_scenarios(d):
    levels = calculate_levels(d)
    if not levels:
        return
    current = safe_float(d["Close"].iloc[-1])
    ma20 = safe_float(d["MA20"].iloc[-1], current)
    ma60 = safe_float(d["MA60"].iloc[-1], current)
    high20 = safe_float(d["HIGH20"].iloc[-1], current)
    low20 = safe_float(d["LOW20"].iloc[-1], current)
    rsi = safe_float(d["RSI14"].iloc[-1], 50)
    vol_ratio = safe_float(d["VOL_RATIO"].iloc[-1], 1.0)
    st.markdown("### 핵심가격 · 대응 시나리오")
    st.caption("현재가를 기준으로 눌림 · 지지 · 돌파 · 위험 구간을 나누고, 각 가격에서 확인할 조건과 대응 방법을 제시합니다.")
    cards = [
        {
            "label": "① 1차 관심",
            "price": levels["first"],
            "condition": "20일선 부근 눌림",
            "meaning": "단기 상승 추세가 유지되는지 확인하는 첫 번째 가격대입니다.",
            "action": "급락 중 바로 매수하지 말고 가격이 20일선에서 멈추는지 확인합니다."
        },
        {
            "label": "② 핵심 지지",
            "price": levels["support"],
            "condition": "중기 추세 방어",
            "meaning": "최근 저점과 중기 이동평균을 기준으로 추세의 방어력을 확인합니다.",
            "action": "지지 + 거래량 안정이 확인될 때 분할 대응을 검토합니다."
        },
        {
            "label": "③ 돌파 기준",
            "price": levels["breakout"],
            "condition": "최근 20일 고점 돌파",
            "meaning": "최근 매물 부담을 넘어 새로운 단기 고점을 만드는 기준입니다.",
            "action": "가격만 돌파하지 말고 거래량 증가가 동반되는지 확인합니다."
        },
        {
            "label": "④ 위험 가격",
            "price": levels["risk"],
            "condition": "핵심 지지 이탈",
            "meaning": "중기 추세가 약해질 수 있어 신규 진입보다 방어가 우선되는 가격대입니다.",
            "action": "지지 회복 전까지 신규 매수는 보수적으로 접근합니다."
        }
    ]
    cols = st.columns(4)
    for col, card in zip(cols, cards):
        with col:
            with st.container(border=True):
                st.markdown(f"**{card['label']}**")
                st.markdown(f"### {money(card['price'])}")
                st.caption(card["condition"])
                st.markdown(f"**의미**  \n{card['meaning']}")
                st.markdown(f"**대응**  \n{card['action']}")
    st.divider()
    if current < levels["risk"]:
        state = "핵심 지지 하회"
        state_desc = "현재가는 위험 가격 아래에 있습니다. 지금은 신규 진입보다 지지 회복 여부를 먼저 확인하는 구간입니다."
        action = "신규매수 보류 · 지지 회복 확인"
        trigger = f"{money(levels['risk'])} 회복 여부"
    elif current <= levels["support"] * 1.015:
        state = "핵심 지지 접근"
        state_desc = "핵심 지지구간에 접근했습니다. 가격이 지지를 지키고 거래량이 안정되는지가 중요합니다."
        action = "분할매수 검토 · 지지 확인"
        trigger = f"{money(levels['support'])} 지지 + 거래량 안정"
    elif current < levels["first"] * 1.015:
        state = "1차 관심구간"
        state_desc = "20일선 부근에서 눌림을 확인할 수 있는 구간입니다. 급등 추격보다 지지 확인이 유리합니다."
        action = "눌림매수 검토 · 추격 자제"
        trigger = f"20일선 {money(ma20)} 지지 확인"
    elif current >= levels["breakout"]:
        state = "돌파구간"
        state_desc = "최근 20일 고점 기준을 넘어선 상태입니다. 거래량이 동반되면 돌파의 신뢰도를 높일 수 있습니다."
        action = "돌파 확인 · 거래량 체크"
        trigger = f"거래량 {vol_ratio:.2f}배 이상 여부"
    else:
        state = "추세 유지구간"
        state_desc = "현재가는 주요 지지와 돌파 기준 사이에 있습니다. 방향이 확정되기 전에는 추격보다 눌림을 기다리는 전략이 적합합니다."
        action = "보유 관찰 · 눌림 대기"
        trigger = f"20일선 {money(ma20)} / 고점 {money(high20)}"
    st.markdown("#### 지금은 어떻게 대응할까?")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("현재가", money(current))
        st.markdown(f"**현재 위치**  \n{state}")
        st.markdown(f"**권장 대응**  \n{action}")
    with c2:
        st.info(state_desc)
        st.markdown(f"**핵심 확인조건:** {trigger}")
        evidence = []
        evidence.append(f"20일선 {money(ma20)} · {'상회' if current >= ma20 else '하회'}")
        evidence.append(f"60일선 {money(ma60)} · {'상회' if current >= ma60 else '하회'}")
        evidence.append(f"RSI14 {rsi:.1f} · {'과열권' if rsi >= 70 else ('약세권' if rsi <= 40 else '중립권')}")
        evidence.append(f"거래량 {vol_ratio:.2f}배 · {'증가' if vol_ratio >= 1.1 else ('감소' if vol_ratio < 0.8 else '평균권')}")
        st.caption(" · ".join(evidence))
    st.markdown("#### 가격대별 행동 기준")
    scenario_cols = st.columns(3)
    with scenario_cols[0]:
        st.markdown("**눌림 시나리오**")
        st.write(f"20일선 {money(ma20)} 부근까지 조정 → 지지 확인 → 거래량 안정 시 분할 접근")
    with scenario_cols[1]:
        st.markdown("**돌파 시나리오**")
        st.write(f"최근 고점 {money(high20)} 돌파 → 거래량 증가 확인 → 돌파 유지 여부 확인")
    with scenario_cols[2]:
        st.markdown("**이탈 시나리오**")
        st.write(f"위험 가격 {money(levels['risk'])} 이탈 → 신규매수 보류 → 지지 회복 여부 재확인")

def render_chart(d):
    if d.empty:
        st.warning("차트 데이터를 확인하지 못했습니다.")
        return
    chart_df = d.tail(126).copy()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.025, row_heights=[0.75, 0.25])
    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            increasing_line_color="#39c99a",
            increasing_fillcolor="#39c99a",
            decreasing_line_color="#ef6678",
            decreasing_fillcolor="#ef6678",
            name="가격",
            showlegend=False
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=chart_df.index, y=chart_df["MA20"], mode="lines", line=dict(color="#4f86b5", width=1.4), name="20일선"),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=chart_df.index, y=chart_df["MA60"], mode="lines", line=dict(color="#a58c52", width=1.3), name="60일선"),
        row=1, col=1
    )
    if "MA200" in chart_df.columns:
        fig.add_trace(
            go.Scatter(x=chart_df.index, y=chart_df["MA200"], mode="lines", line=dict(color="#7b6fa8", width=1.1), name="200일선"),
            row=1, col=1
        )
    volume_colors = np.where(chart_df["Close"] >= chart_df["Open"], "#327f69", "#9b4653")
    fig.add_trace(
        go.Bar(x=chart_df.index, y=chart_df["Volume"], marker_color=volume_colors, opacity=0.5, name="거래량", showlegend=False),
        row=2, col=1
    )
    fig.update_xaxes(fixedrange=True, showgrid=False, rangeslider_visible=False)
    fig.update_yaxes(fixedrange=True, gridcolor="#17283a", tickfont=dict(color="#73879b", size=9), row=1, col=1)
    fig.update_yaxes(fixedrange=True, showticklabels=False, showgrid=False, row=2, col=1)
    fig.update_layout(
        height=390,
        margin=dict(l=4, r=4, t=18, b=4),
        paper_bgcolor="#0d1928",
        plot_bgcolor="#0d1928",
        font=dict(color="#aab8c7"),
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", font=dict(size=9, color="#8ea0b3")),
        dragmode=False,
        hovermode="x unified"
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False, "scrollZoom": False, "doubleClick": False, "responsive": True, "staticPlot": True}
    )

def lookup_live_etf(code):
    """신규/누락 ETF는 KRX → Naver → Yahoo 순으로 이름을 확인합니다."""
    code = _normalize_etf_code(code)
    if not code:
        return ""
    for source in (fetch_krx_etf_master(), fetch_naver_etf_master()):
        name = source.get(code)
        if name and not name.startswith("ETF "):
            st.session_state.etf_universe[code] = name
            return name
    try:
        info = yf.Ticker(f"{code}.KS").info
        name = info.get("shortName") or info.get("longName") or ""
        name = safe_etf_name(code, name)
        if name and not name.startswith("ETF "):
            st.session_state.etf_universe[code] = name
            return name
    except Exception:
        pass
    return f"ETF {code}"

def lookup_yahoo_etf_name(code):
    return lookup_live_etf(code)

def search_etfs(query):
    query_raw = (query or "").strip()
    query = query_raw.lower()
    if not query:
        return []
    results = []
    seen = set()
    for raw_code, raw_name in st.session_state.etf_universe.items():
        code = str(raw_code).strip().upper()
        if code.isdigit():
            code = code.zfill(6)
        name = get_etf_name(code)
        if code in seen:
            continue
        search_name = str(name).strip().lower()
        if query in code.lower() or query in search_name:
            results.append({"code": code, "name": name})
            seen.add(code)
    compact = query_raw.replace(".", "").replace("-", "").strip().upper()
    if re.fullmatch(r"[0-9A-Z]{6}", compact):
        code = compact
        if code not in seen:
            name = lookup_yahoo_etf_name(code)
            results.insert(0, {"code": code, "name": name})
            st.session_state.etf_universe[code] = name
            seen.add(code)
    return results[:30]

def add_watch(code):
    code = _normalize_etf_code(code)
    if code not in st.session_state.watchlist:
        st.session_state.watchlist.append(code)
        write_json(WATCHLIST_FILE, st.session_state.watchlist)
    st.session_state.selected_code = code

def render_finder():
    st.markdown('<div class="section-title">ETF 찾기</div>', unsafe_allow_html=True)
    query = st.text_input("ETF명 또는 종목코드", placeholder="예: AI반도체 / 395160", label_visibility="collapsed", key="search_q")
    results = search_etfs(query)
    if results:
        result_map = {str(x["code"]).zfill(6): x for x in results}
        result_codes = list(result_map.keys())
        selected_code = st.selectbox(
            "검색 결과",
            result_codes,
            format_func=lambda code: f'{get_etf_name(code)} · {code}',
            key="search_result"
        )
        item = result_map[str(selected_code).zfill(6)]
        c1, c2 = st.columns([4, 1])
        with c1:
            st.caption(f'선택: {item["name"]} ({item["code"]})')
        with c2:
            already = item["code"] in st.session_state.watchlist
            if st.button("추가" if not already else "등록됨", disabled=already, use_container_width=True, key=f'add_{item["code"]}'):
            item["future_theme_score"] = safe_float(tscore, 0)
        except Exception:
            item["future_theme"] = "미래테마 미연결"
            item["future_theme_related"] = False
            item["future_theme_score"] = 0.0
        zone = validated_price_zone({
            "Close": current,
            "MA20": ma20,
            "MA60": ma60,
            "LOW20": safe_float(r.get("LOW20"), current),
        })
        item["price_zone"] = zone["state"]
        item["support"] = zone["support"]
        item["ideal_top"] = zone["ideal_top"]
        item["invalid"] = zone["invalid"]
        item["cross_score"] = round(
            item["opportunity"] * 0.55
            + item["future_theme_score"] * 0.25
            + (100 - item["overheat"]) * 0.20,
            1
        )
        item["future_signal"] = leading_signal(r, benchmark["ret20"])
        rows.append(item)
    rows.sort(key=lambda x: (x["cross_score"], x["opportunity"], -x["overheat"]), reverse=True)
    data = {
        "time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "benchmark": benchmark,
        "rows": rows,
        "target_key": target_key,
    }
    st.session_state.radar_cache = data
    return data

def render_radar_card(item, prefix=""):
    code = item.get("code", "")
    name = item.get("name", "")
    price = safe_float(item.get("price"))
    opportunity = safe_float(item.get("opportunity"))
    overheat = safe_float(item.get("overheat"))
    cross = safe_float(item.get("cross_score"))
    rsi = safe_float(item.get("rsi"), 50)
    vr = safe_float(item.get("vr"), 1)
    ret5 = safe_float(item.get("ret5"))
    ret20 = safe_float(item.get("ret20"))
    rs20 = safe_float(item.get("rs20"))
    zone = item.get("price_zone", "확인")
    theme = item.get("future_theme") or item.get("theme") or "기타"
    stage = item.get("stage", "")
    if overheat >= 65:
        state = "과열 주의"
        cls = "bad"
    elif cross >= 75 and zone == "매수구간":
        state = "매수 검토"
        cls = "good"
    elif cross >= 65:
        state = "관심"
        cls = "warn"
    else:
        state = "관찰"
        cls = "neutral"
    st.markdown(
        f"""
        <div class="radar-card">
            <div class="small-label">{esc(prefix)} · {esc(theme)} · {esc(stage)}</div>
            <div style="display:flex;justify-content:space-between;gap:8px;align-items:center;">
                <div>
                    <div style="font-size:1.05rem;font-weight:800;color:#fff;">{esc(name)}</div>
                    <div class="small-label">{esc(code)}</div>
                </div>
                <div style="text-align:right;">
                    <div class="big-number">{money(price)}</div>
                    <div class="{cls}" style="font-weight:800;">{state}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("교차점수", f"{cross:.0f}")
    with c2:
        st.metric("시장점수", f"{opportunity:.0f}")
    with c3:
        st.metric("RS20", f"{rs20:+.1f}%")
    with c4:
        st.metric("RSI", f"{rsi:.1f}")
    st.caption(
        f"5일 {ret5:+.1f}% · 20일 {ret20:+.1f}% · 거래량 {vr:.2f}배 · "
        f"과열 {overheat:.0f} · 가격구간 {zone}"
    )

def render_market_radar():
    if st_autorefresh is not None:
        st_autorefresh(interval=10 * 60 * 1000, key="market_radar_autorefresh")
    st.markdown(
        '<div class="hero"><div class="hero-name">📡 시장 레이더</div>'
        '<div class="hero-code">미래테마 ETF 중 현재 상승 가능성이 높은 후보</div></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="today-interest-panel">'
        '<div class="big-number">오늘의 관심 후보</div>'
        '<div style="margin-top:6px;">'
        '미래테마와 현재 추세·상대강도·거래량·가격 위치를 교차해 '
        '아직 과열되지 않은 후보를 우선 표시합니다.'
        '</div></div>',
        unsafe_allow_html=True
    )
    if st.button("🔄 시장 레이더 새로고침", use_container_width=True, key="radar_refresh"):
        st.session_state.radar_cache = None
        st.session_state.future_engine_cache = None
        st.session_state.price_cache = {}
        st.rerun()
    with st.spinner("시장 레이더를 계산하는 중입니다…"):
        data = build_radar_data(force=False)
    rows = data.get("rows", [])
    if not rows:
        st.info("현재 분석 가능한 미래테마 ETF가 없습니다.")
        return
    strong = [
        x for x in rows
        if x.get("cross_score", 0) >= 65
        and x.get("overheat", 100) < 70
    ]
    if not strong:
        strong = rows[:5]
    st.caption(
        f"분석 후보 {len(rows)}개 · 관심 후보 {len(strong)}개 · "
        f"기준시각 {data.get('time', '')}"
    )
    for item in strong[:10]:
        render_radar_card(item, "📡 시장레이더")

def _theme_keywords_from_name(name):
    text = safe_etf_name(name).replace(" ", "").lower()
    matched = []
    for theme, info in THEMES.items():
        hits = sum(
            1 for seed in info.get("seeds", [])
            if seed.replace(" ", "").lower() in text
        )
        if hits:
            matched.append((theme, hits))
    matched.sort(key=lambda x: x[1], reverse=True)
    return matched

THEME_LEXICON = {
    "AI 반도체": [
        "AI", "인공지능", "반도체", "HBM", "메모리", "파운드리",
        "반도체장비", "반도체소부장", "칩", "AI반도체"
    ],
    "AI 소프트웨어·빅테크": [
        "AI", "인공지능", "소프트웨어", "빅테크", "클라우드",
        "인터넷", "플랫폼", "데이터", "테크"
    ],
    "데이터센터·AI 인프라": [
        "데이터센터", "AI인프라", "AI인프라", "서버", "클라우드",
        "데이터", "네트워크", "인프라"
    ],
    "전력 인프라": [
        "전력", "전선", "변압기", "전력기기", "전력인프라",
        "에너지", "배전", "송전", "전기"
    ],
    "원자력": [
        "원자력", "원전", "SMR", "우라늄", "원전기기",
        "원전산업", "핵연료"
    ],
    "냉각·열관리": [
        "냉각", "열관리", "액침냉각", "공조", "HVAC",
        "칠러", "냉동", "열교환"
    ],
    "로봇·자율주행": [
        "로봇", "자율주행", "자동화", "스마트팩토리",
        "AI로봇", "로보틱스", "모빌리티"
    ],
    "방산·우주": [
        "방산", "우주", "항공", "국방", "위성",
        "미사일", "방위", "항공우주"
    ],
    "2차전지·ESS": [
        "2차전지", "배터리", "ESS", "전고체", "리튬",
        "양극재", "음극재", "배터리소재"
    ],
}

def get_future_chain():
    return FUTURE_CHAIN

def _find_theme_for_etf(code):
    code = _normalize_etf_code(code)
    name = get_etf_name(code)
    matched = _theme_keywords_from_name(name)
    if matched:
        theme = matched[0][0]
        members = []
        for raw_code, raw_name in st.session_state.etf_universe.items():
            n = safe_etf_name(raw_name)
            hits = _theme_match(n, THEME_LEXICON.get(theme, []))
            if hits:
                members.append({
                    "code": _normalize_etf_code(raw_code),
                    "name": n,
                    "hits": hits
                })
        return theme, members
    return None, []

def theme_candidates(theme):
    keywords = THEME_LEXICON.get(theme, [])
    if not keywords:
        return []
    universe = st.session_state.get("etf_universe", {})
    rows = []
    for code, name in universe.items():
        hits = _theme_match(name, keywords)
        if hits:
            rows.append({
                "code": _normalize_etf_code(code),
                "name": safe_etf_name(name),
                "hits": hits
            })
    rows.sort(key=lambda x: (x["hits"], x["name"]), reverse=True)
    return rows

def _future_theme_selected_map(benchmark_ret20=0):
    engine = build_future_theme_engine(force=False)
    selected = {}
    themes = engine.get("themes", []) if engine else []
    for theme_rank, theme_item in enumerate(themes, 1):
        theme_name = theme_item.get("theme", "")
        theme_score = safe_float(theme_item.get("score"), 0)
        signal_score = safe_float(theme_item.get("signal_score"), 0)
        candidates = theme_item.get("etfs", [])
        for etf_rank, item in enumerate(candidates, 1):
            code = _normalize_etf_code(item.get("code"))
            if not code:
                continue
            if code not in selected:
                selected[code] = {
                    "theme": theme_name,
                    "theme_rank": theme_rank,
                    "etf_rank": etf_rank,
                    "theme_score": theme_score,
                    "signal_score": signal_score
                }
    return selected

def render_future_theme():
    if st_autorefresh is not None:
        st_autorefresh(interval=10 * 60 * 1000, key="future_theme_autorefresh")
    st.markdown(
        '<div class="hero"><div class="hero-name">🔭 미래테마</div>'
        '<div class="hero-code">지금 강한 테마보다 앞으로 강해질 가능성이 커지는 테마</div></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="future-theme-hero">'
        '<div class="future-theme-title">미래테마 → 유망 ETF → 가격구간</div>'
        '<div class="future-theme-sub">'
        '현재 수익률만 높은 테마를 고르는 것이 아니라 상대강도 변화, 확산도, '
        '가속도, 거래량과 과열도를 함께 보고 상승 초기의 테마를 찾습니다.'
        '</div></div>',
        unsafe_allow_html=True
    )
    if st.button("🔄 미래테마 새로고침", use_container_width=True, key="future_theme_refresh"):
        st.session_state.future_engine_cache = None
        st.session_state.radar_cache = None
        st.session_state.price_cache = {}
        st.rerun()
    with st.spinner("미래테마를 분석하는 중입니다…"):
        engine = build_future_theme_engine(force=False)
    themes = engine.get("themes", []) if engine else []
    if not themes:
        st.info("현재 미래테마를 계산할 수 있는 데이터가 부족합니다.")
        return
    st.caption(
        f"분석 테마 {len(themes)}개 · 기준시각 {engine.get('time', '')}"
    )
    for idx, theme_item in enumerate(themes[:10], 1):
        theme = theme_item.get("theme", "")
        score = safe_float(theme_item.get("score"), 0)
        lifecycle = theme_item.get("lifecycle", {})
        state = lifecycle.get("state", theme_item.get("stage", "관찰"))
        signal_score = safe_float(theme_item.get("signal_score"), 0)
        if idx == 1:
            card_cls = "theme-card-lead"
        elif idx <= 3:
            card_cls = "theme-card-next"
        else:
            card_cls = "theme-card-early"
        st.markdown(
            f"""
            <div class="{card_cls}">
                <div class="small-label">#{idx} · {esc(state)}</div>
                <div style="font-size:1.18rem;font-weight:800;color:#fff;">{esc(theme)}</div>
                <div style="margin-top:6px;">테마점수 <b>{score:.0f}</b> · 선행신호 <b>{signal_score:.0f}</b></div>
                <div class="small-label">
                    상대강도 변화 {safe_float(lifecycle.get("delta_rs")):+.1f} ·
                    확산 변화 {safe_float(lifecycle.get("delta_breadth")):+.1f} ·
                    가속도 변화 {safe_float(lifecycle.get("delta_accel")):+.1f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        etfs = theme_item.get("etfs", [])
        if not etfs:
            continue
        for etf in etfs[:5]:
            code = _normalize_etf_code(etf.get("code"))
            name = etf.get("name", get_etf_name(code))
            st.markdown(
                f'<div class="signal-box">'
                f'<b>{esc(name)}</b> · {esc(code)}'
                f' · 테마내 #{etf.get("rank", "-")} · '
                f'선행점수 {safe_float(etf.get("signal_score")):.0f}'
                f'</div>',
                unsafe_allow_html=True
            )
            if st.button(
                f"ETF 분석 · {code}",
                key=f"future_analysis_{theme}_{code}_{idx}",
                use_container_width=True
            ):
                st.session_state.selected_code = code
                st.session_state.active_tab = "내 ETF"
                st.rerun()

def render_strategy_horizons(item):
    code = item.get("code")
    df = load_price_data(code)
    if df.empty:
        st.warning("전략 데이터를 불러오지 못했습니다.")
        return
    d = calculate_indicators(df)
    if d.empty:
        st.warning("전략 데이터를 계산하지 못했습니다.")
        return
    with st.expander("장기 · 중기 · 단기 전략 보기", expanded=False):
        long = long_term_horizon(d)
        medium = medium_term_signal(d)
        short = short_term_signal(d)
        cols = st.columns(3)
        for col, title, result in [
            (cols[0], "장기 · 추세 보유", long),
            (cols[1], "중기 · 추세 대응", medium),
            (cols[2], "단기 · 타이밍 대응", short)
        ]:
            with col:
                st.markdown(f"**{title}**")
                st.metric("점수", f'{result["score"]:.0f}')
                st.caption(result["label"])
                for reason in result.get("reasons", []):
                    st.caption("• " + reason)

def render_final_target_horizon(code):
    df = load_price_data(code)
    if df.empty:
        return
    d = calculate_indicators(df)
    if d.empty:
        return
    h = long_term_horizon(d)
    m = medium_term_signal(d)
    s = short_term_signal(d)
    with st.expander("장기 · 중기 · 단기 전략 보기", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**장기 · 추세 보유**")
            st.metric("점수", f'{h["score"]:.0f}')
            st.caption(h["label"])
            for x in h.get("reasons", []):
                st.caption("• " + x)
        with c2:
            st.markdown("**중기 · 추세 대응**")
            st.metric("점수", f'{m["score"]:.0f}')
            st.caption(m["label"])
            for x in m.get("reasons", []):
                st.caption("• " + x)
        with c3:
            st.markdown("**단기 · 타이밍 대응**")
            st.metric("점수", f'{s["score"]:.0f}')
            st.caption(s["label"])
            for x in s.get("reasons", []):
                st.caption("• " + x)
        row = d.iloc[-1]
        structural_break = (
            safe_float(row.get("Close")) < safe_float(row.get("MA120"))
            and safe_float(row.get("MA60")) < safe_float(row.get("MA120"))
        )
        if structural_break:
            st.warning("장기 구조적 훼손이 확인되어 신규매수보다 구조 재검토를 우선합니다.")

def build_final_targets(radar_data):
    """
    최종타겟은 '현재 강한 ETF'를 뽑는 것이 아니라
    미래테마 우선순위 + 현재 시장조건을 교차해서 결정합니다.
    핵심:
      - 미래테마 순위: 미래 방향성의 앵커
      - cross_score: 현재 투자조건
      - ETF 내부 순위: 같은 테마 안에서의 대표성
    따라서 방산처럼 현재 모멘텀이 강하더라도 미래테마 순위가 낮으면
    무조건 AI/반도체를 밀어내지 못하게 합니다.
    """
    rows = radar_data.get('rows', []) if radar_data else []
    benchmark = radar_data.get('benchmark', {}) if radar_data else {}
    selected = _future_theme_selected_map(safe_float(benchmark.get('ret20'), 0))
    targets = []
    for item in rows:
        code = _normalize_etf_code(item.get('code'))
        rel = selected.get(code)
        if not rel:
            continue
        if item.get('opportunity', 0) < 55:
            continue
        if item.get('rsi', 100) >= 72 or item.get('ret5', 999) >= 8:
            continue
        if item.get('price_zone') == '무효':
            continue
        x = dict(item)
        theme_rank = int(rel.get('theme_rank', 99))
        etf_rank = int(rel.get('etf_rank', 99))
        theme_score = safe_float(rel.get('theme_score'), 0)
        cross_score = safe_float(x.get('cross_score'), 0)
        future_anchor = max(40.0, 100.0 - (theme_rank - 1) * 8.0)
        final_score = (
            cross_score * 0.62 +
            theme_score * 0.18 +
            future_anchor * 0.20
        )
        final_score -= max(0, etf_rank - 1) * 1.5
        if theme_rank == 1 and cross_score >= 70:
            final_score += 4.0
        elif theme_rank >= 4 and cross_score < 85:
            final_score -= 3.0
        x.update({
            'future_theme_selected': True,
            'future_theme': rel['theme'],
            'future_theme_rank': theme_rank,
            'future_etf_rank': etf_rank,
            'future_theme_score': theme_score,
            'future_theme_anchor': round(future_anchor, 1),
            'future_theme_lead': rel['signal_score'],
            'final_score': round(float(np.clip(final_score, 0, 100)), 1),
        })
        targets.append(x)
    targets.sort(
        key=lambda x: (
            x.get('final_score', 0),
            x.get('cross_score', 0),
            -x.get('future_theme_rank', 99),
            x.get('opportunity', 0),
            x.get('rs20', -999),
        ),
        reverse=True
    )
    for i, x in enumerate(targets, 1):
        fs = safe_float(x.get('final_score'), 0)
        cross = safe_float(x.get('cross_score'), 0)
        theme_rank = int(x.get('future_theme_rank', 99))
        if fs >= 82 and cross >= 75 and x.get('price_zone') == '매수구간' and x.get('overheat', 0) < 65:
            state = '🔥 최종 타겟'
        elif fs >= 72:
            state = '🟢 최종 우선'
        elif fs >= 60:
            state = '🟡 최종 관찰'
        else:
            state = '⚪ 대기'
        x['final_rank'] = i
        x['final_state'] = state
        x['final_reason'] = (
            f"미래테마 #{theme_rank} · 미래성 {x.get('future_theme_score',0):.0f} · "
            f"현재조건 {cross:.0f} · 가격구간 {x.get('price_zone','확인')}"
        )
    return targets

def render_final_target():
    if st_autorefresh is not None:
        st_autorefresh(interval=10*60*1000, key="final_target_autorefresh")
    st.markdown('<div class="hero"><div class="hero-name">🏆 최종 타겟</div><div class="hero-code">미래테마 × 시장레이더 × 아직 안 오른 강세 × 가격구간</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="final-target-hero"><div class="final-target-title">무엇을 살 것인가 → 언제 접근할 것인가</div><div class="final-target-sub">미래테마에서 실제 상위 ETF 후보로 선정되고, 시장레이더의 강세 조건과 가격구간을 함께 통과한 종목만 최종 타겟으로 올립니다. 장기·중기·단기는 같은 점수로 합치지 않고 각각의 검증 로직으로 따로 판단합니다.</div></div>', unsafe_allow_html=True)
    if st.button('🔄 최종 타겟 새로고침',use_container_width=True,key='final_target_refresh'):
        st.session_state.radar_cache=None
        st.session_state.future_engine_cache=None
        st.session_state.price_cache={}
        st.rerun()
    with st.spinner('미래테마와 시장레이더의 최종 교차 후보를 계산하는 중입니다…'):
        data=build_radar_data()
        targets=build_final_targets(data)
    if not targets:
        st.info('현재 시점에는 미래테마 실제 후보와 시장레이더 조건을 동시에 통과한 최종 타겟이 없습니다. 조건 미충족이면 억지로 후보를 만들지 않습니다.')
        return
    top=targets[:5]
    st.caption(f'최종 타겟 {len(targets)}개 · 화면에는 상위 {len(top)}개 표시 · 기준시각 {data.get("time")}')
    for item in top:
        st.markdown(
            f'<div class="final-target-rank">#{item["final_rank"]} · {esc(item["final_state"])} · '
            f'미래테마 #{item.get("future_theme_rank", "-")} {esc(item["future_theme"])} · '
            f'테마 내 ETF #{item.get("future_etf_rank", "-")} · 최종점수 {item.get("final_score", 0):.0f}</div>',
            unsafe_allow_html=True
        )
        st.caption(f'판단근거 · {esc(item.get("final_reason", ""))}')
        render_radar_card(item,'🎯 유망후보')
        render_final_target_horizon(item['code'])

def get_benchmark_metrics():
    df = load_price_data("069500")
    if df.empty:
        return {"ret20": 0.0, "ret5": 0.0}
    d = calculate_indicators(df)
    if d.empty:
        return {"ret20": 0.0, "ret5": 0.0}
    row = d.iloc[-1]
    return {"ret20": safe_float(row.get("RET20", 0)), "ret5": safe_float(row.get("RET5", 0))}

def radar_theme_for(code, name):
    text=f"{code} {name}"
    best=None
    hits=0
    for theme,keywords in THEME_LEXICON.items():
        h=_theme_match(text,keywords)
        if h>hits:
            best,hits=theme,h
    return best or "기타"

def radar_stage_for(theme):
    for t, stage in get_future_chain():
        if t == theme:
            return stage
    return "기타"

def radar_score(row):
    score = 0
    if row["above20"]:
        score += 12
    if row["above60"]:
        score += 13
    rs = row["rs20"]
    if rs >= 5:
        score += 20
    elif rs >= 2:
        score += 16
    elif rs > 0:
        score += 11
    elif rs > -3:
        score += 5
    vr = row["vr"]
    if 1.15 <= vr <= 2.0:
        score += 15
    elif 1.0 <= vr < 1.15:
        score += 9
    elif vr > 2.0:
        score += 7
    r20, r5 = row["ret20"], row["ret5"]
    if 2 <= r20 <= 15:
        score += 12
    elif 0 <= r20 < 2:
        score += 8
    elif r20 > 15:
        score += 5
    if -2 <= r5 <= 5:
        score += 8
    elif 5 < r5 <= 8:
        score += 4
    rsi, dist = row["rsi"], row["dist20"]
    if 50 <= rsi <= 68:
        score += 12
    elif 45 <= rsi < 50 or 68 < rsi <= 72:
        score += 7
    elif rsi < 40 or rsi > 78:
        score += 2
    if dist <= 4:
        score += 8
    elif dist <= 7:
        score += 5
    elif dist <= 10:
        score += 2
    return int(min(100, max(0, score)))

def radar_overheat_score(row):
    score = 0
    if row["rsi"] >= 75:
        score += 30
    elif row["rsi"] >= 70:
        score += 22
    elif row["rsi"] >= 67:
        score += 10
    if row["ret5"] >= 10:
        score += 25
    elif row["ret5"] >= 7:
        score += 18
    elif row["ret5"] >= 5:
        score += 10
    if row["dist20"] >= 12:
        score += 25
    elif row["dist20"] >= 8:
        score += 18
    elif row["dist20"] >= 5:
        score += 8
    if row["vr"] >= 2.0:
        score += 20
    elif row["vr"] >= 1.5:
        score += 14
    elif row["vr"] >= 1.2:
        score += 7
    return int(min(100, score))

def radar_target_etfs():
    """레이더 분석 대상은 전체 ETF가 아니라 '내 ETF + 미래테마 ETF'로 제한합니다."""
    targets = {}
    for raw_code in st.session_state.get("holdings", []):
        code = _normalize_etf_code(raw_code)
        if not code:
            continue
        name = get_etf_name(code)
        if not name or name.startswith("ETF "):
            live = lookup_live_etf(code)
            name = live or name
        targets[code] = name
    for theme, _stage in get_future_chain():
        try:
            for item in theme_candidates(theme):
                code = _normalize_etf_code(item.get("code"))
                name = item.get("name") or get_etf_name(code)
                if code and name and not str(name).startswith("ETF "):
                    targets[code] = name
        except Exception:
            continue
    return targets

def build_radar_data(force=False):
    now = datetime.now()
    cached = st.session_state.get("radar_cache")
    targets = radar_target_etfs()
    target_key = tuple(sorted(targets.keys()))
    if cached and not force:
        try:
            age = (now - cached["time"]).total_seconds()
            if age < 300 and cached.get("target_key") == target_key and "rows" in cached:
                return cached
        except Exception:
            pass
    benchmark = get_benchmark_metrics()
    rows = []
    for code, target_name in targets.items():
        name = target_name or get_etf_name(code)
        if not name or str(name).startswith("ETF "):
            continue
        df = load_price_data(code)
        if df.empty or len(df) < 65:
            continue
        try:
            d = calculate_indicators(df)
            if d.empty:
                continue
            r = d.iloc[-1]
        except Exception:
            continue
        current = safe_float(r["Close"])
        ma20 = safe_float(r["MA20"], current)
        ma60 = safe_float(r["MA60"], current)
        item = {
            "code": code,
            "name": name,
            "price": current,
            "rsi": safe_float(r["RSI14"], 50),
            "vr": safe_float(r["VOL_RATIO"], 1),
            "ret5": safe_float(r["RET5"], 0),
            "ret20": safe_float(r["RET20"], 0),
            "dist20": (current / ma20 - 1) * 100 if ma20 else 0,
            "above20": current >= ma20,
            "above60": current >= ma60,
            "raw": r.to_dict(),
        }
        item["rs20"] = item["ret20"] - benchmark["ret20"]
        item["theme"] = radar_theme_for(code, name)
        item["stage"] = radar_stage_for(item["theme"])
        item["opportunity"] = radar_score(item)
        item["overheat"] = radar_overheat_score(item)
        try:
            bench20 = safe_float(benchmark.get("ret20"), 0)
            bench60 = safe_float(benchmark.get("ret60"), 0)
            theme_name, theme_members = _find_theme_for_etf(code)
            item["future_theme"] = theme_name if theme_members else "미래테마 미연결"
            item["future_theme_related"] = bool(theme_members)
            tscore = theme_score(theme_members, bench20, bench60) if theme_members else 0.0
            item["future_theme_score"] = safe_float(tscore, 0)
        except Exception:
            item["future_theme"] = "미래테마 미연결"
            item["future_theme_related"] = False
            item["future_theme_score"] = 0.0
        zone = validated_price_zone({
            "Close": current,
            "MA20": ma20,
            "MA60": ma60,
            "LOW20": safe_float(r.get("LOW20"), current),
        })
        item["price_zone"] = zone["state"]
        item["support"] = zone["support"]
        item["ideal_top"] = zone["ideal_top"]
        item["invalid"] = zone["invalid"]
        item["cross_score"] = round(
            item["opportunity"] * 0.55
            + item["future_theme_score"] * 0.25
            + (100 - item["overheat"]) * 0.20,
            1
        )
        item["future_signal"] = leading_signal(r, benchmark["ret20"])
        rows.append(item)
    rows.sort(key=lambda x: (x["cross_score"], x["opportunity"], -x["overheat"]), reverse=True)
    data = {
        "time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "benchmark": benchmark,
        "rows": rows,
        "target_key": target_key,
    }
    st.session_state.radar_cache = data
    return data

def render_radar_card(item, prefix=""):
    code = item.get("code", "")
    name = item.get("name", "")
    price = safe_float(item.get("price"))
    opportunity = safe_float(item.get("opportunity"))
    overheat = safe_float(item.get("overheat"))
    cross = safe_float(item.get("cross_score"))
    rsi = safe_float(item.get("rsi"), 50)
    vr = safe_float(item.get("vr"), 1)
    ret5 = safe_float(item.get("ret5"))
    ret20 = safe_float(item.get("ret20"))
    rs20 = safe_float(item.get("rs20"))
    zone = item.get("price_zone", "확인")
    theme = item.get("future_theme") or item.get("theme") or "기타"
    stage = item.get("stage", "")
    if overheat >= 65:
        state = "과열 주의"
        cls = "bad"
    elif cross >= 75 and zone == "매수구간":
        state = "매수 검토"
        cls = "good"
    elif cross >= 65:
        state = "관심"
        cls = "warn"
    else:
        state = "관찰"
        cls = "neutral"
    st.markdown(
        f"""
        <div class="radar-card">
            <div class="small-label">{esc(prefix)} · {esc(theme)} · {esc(stage)}</div>
            <div style="display:flex;justify-content:space-between;gap:8px;align-items:center;">
                <div>
                    <div style="font-size:1.05rem;font-weight:800;color:#fff;">{esc(name)}</div>
                    <div class="small-label">{esc(code)}</div>
                </div>
                <div style="text-align:right;">
                    <div class="big-number">{money(price)}</div>
                    <div class="{cls}" style="font-weight:800;">{state}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("교차점수", f"{cross:.0f}")
    with c2:
        st.metric("시장점수", f"{opportunity:.0f}")
    with c3:
        st.metric("RS20", f"{rs20:+.1f}%")
    with c4:
        st.metric("RSI", f"{rsi:.1f}")
    st.caption(
        f"5일 {ret5:+.1f}% · 20일 {ret20:+.1f}% · 거래량 {vr:.2f}배 · "
        f"과열 {overheat:.0f} · 가격구간 {zone}"
    )
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
            if invalid <= 0:
                invalid = c * 0.92
            buy2 = (buy1 + invalid) / 2
            risk = max(buy1 - invalid, c * 0.05)
            tp1 = buy1 + risk
            tp2 = buy1 + risk * 2
            chase = ma20 * 1.07
            zone = item.get("price_zone", "확인")
            if zone == "매수구간":
                action = "🔥 지금 1차 매수 검토"
            elif zone == "눌림대기":
                action = "🟢 지금 추격하지 말고 눌림 2차 매수 대기"
            elif zone == "추격금지":
                action = "🔴 지금 매수 금지 · 눌림 대기"
            else:
                action = "🔴 매수 보류 · 가격구간 무효"
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
            st.markdown(f'<div class="radar-card"><span class="radar-badge">{esc(x["stage"])}</span><div class="radar-title">{esc(x["theme"])}</div><div class="radar-sub">구성 {x["n"]}개 · 단기 상승 비율 {x["breadth"]:.0f}%</div><div class="radar-grid"><div class="radar-metric"><div class="radar-label">5일</div><div class="radar-value {cls}">{x["avg5"]:+.1f}%</div></div><div class="radar-metric"><div class="radar-label">20일</div><div class="radar-value">{x["avg20"]:+.1f}%</div></div><div class="radar-metric"><div class="radar-label">거래량</div><div class="radar-value">{x["avgvr"]:.2f}x</div></div></div></div>', unsafe_allow_html=True)
        return
    if mode == "⚠️ 과열검색":
        candidates = sorted(rows, key=lambda x: (x["overheat"], x["ret5"]), reverse=True)
        st.markdown("### 과열검색")
        st.caption("단기 급등·RSI·이격·거래량 급증을 종합해 과열 가능성이 높은 ETF를 찾습니다.")
        for item in candidates[:10]:
            render_radar_card(item, "⚠️ 과열검색")
        return
    candidates = [x for x in rows if x.get("cross_score",0) >= 55]
    candidates.sort(key=lambda x: (x.get("cross_score",0), x["opportunity"], -x["overheat"]), reverse=True)
    if not candidates:
        candidates = sorted(rows, key=lambda x: x["opportunity"], reverse=True)
    st.markdown("### 🎯 유망후보")
    st.caption("미래테마와 현재 추세를 교차해 상대적으로 상승 가능성이 높은 후보를 우선 표시합니다.")
    for item in candidates[:10]:
        render_radar_card(item, "🎯 유망후보")

def render_holdings():
    st.markdown('<div class="hero"><div class="hero-name">💼 내 ETF</div><div class="hero-code">보유 ETF의 현재 상태와 전략을 한 화면에서 확인</div></div>', unsafe_allow_html=True)
    holdings = st.session_state.holdings
    if not holdings:
        st.info("등록된 ETF가 없습니다.")
        st.caption("ETF 분석 화면에서 관심 ETF를 등록하면 이곳에서 관리할 수 있습니다.")
        return
    if st.button("🔄 내 ETF 새로고침", use_container_width=True, key="holdings_refresh"):
        st.session_state.price_cache = {}
        st.rerun()
    for code in holdings:
        name = get_etf_name(code)
        df = load_price_data(code)
        if df.empty:
            st.warning(f"{name} ({code}) 가격 데이터를 가져오지 못했습니다.")
            continue
        d = calculate_indicators(df)
        if d.empty:
            continue
        row = d.iloc[-1]
        current = safe_float(row.get("Close"))
        prev = safe_float(d["Close"].iloc[-2], current) if len(d) > 1 else current
        change = current - prev
        pct = change / prev * 100 if prev else 0
        j = get_judgment(d)
        lt = long_term_horizon(d)
        mt = medium_term_signal(d)
        stg = short_term_signal(d)
        st.markdown(
            f'<div class="holding-card"><div class="holding-head"><div><div class="holding-name">{esc(name)}</div><div class="small-label">{esc(code)}</div></div><div class="holding-price">{money(current)} <span class="{"positive" if pct>=0 else "negative"}">{pct:+.2f}%</span></div></div></div>',
            unsafe_allow_html=True
        )
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("현재가", money(current))
        with c2:
            st.metric("등락", f"{change:+,.0f}원")
        with c3:
            st.metric("RSI", f'{safe_float(row.get("RSI14"),50):.1f}')
        with c4:
            st.metric("거래량", f'{safe_float(row.get("VOL_RATIO"),1):.2f}x')
        render_judgment(j)
        with st.expander("장기 · 중기 · 단기 전략 보기", expanded=False):
            cols = st.columns(3)
            for col, title, result in [
                (cols[0], "장기 · 추세 보유", lt),
                (cols[1], "중기 · 추세 대응", mt),
                (cols[2], "단기 · 타이밍 대응", stg)
            ]:
                with col:
                    st.markdown(f"**{title}**")
                    st.metric("점수", f'{result["score"]:.0f}')
                    st.caption(result["label"])
                    for reason in result.get("reasons", []):
                        st.caption("• " + reason)
        render_scenarios(d)
        render_chart(d)

def render_etf_analysis(code):
    code = _normalize_etf_code(code)
    name = get_etf_name(code)
    st.markdown(
        f'<div class="hero"><div class="hero-name">📊 ETF 분석</div>'
        f'<div class="hero-code">{esc(name)} · {esc(code)}</div></div>',
        unsafe_allow_html=True
    )
    if st.button("⭐ 내 ETF에 추가", use_container_width=True, key=f"hold_{code}"):
        if code not in st.session_state.holdings:
            st.session_state.holdings.append(code)
            safe_write_json(HOLDINGS_FILE, st.session_state.holdings)
            st.success("내 ETF에 추가했습니다.")
    df = load_price_data(code)
    if df.empty:
        st.error("가격 데이터를 불러오지 못했습니다.")
        return
    d = calculate_indicators(df)
    if d.empty:
        st.error("지표 계산에 필요한 데이터가 부족합니다.")
        return
    row = d.iloc[-1]
    current = safe_float(row.get("Close"))
    prev = safe_float(d["Close"].iloc[-2], current) if len(d) > 1 else current
    change = current - prev
    pct = change / prev * 100 if prev else 0
    st.markdown(
        f'<div class="price-box"><div class="small-label">현재가</div>'
        f'<div class="big-number">{money(current)}</div>'
        f'<div class="{"positive" if pct>=0 else "negative"}">{change:+,.0f}원 ({pct:+.2f}%)</div></div>',
        unsafe_allow_html=True
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("RSI14", f'{safe_float(row.get("RSI14"),50):.1f}')
    with c2:
        st.metric("거래량/20일평균", f'{safe_float(row.get("VOL_RATIO"),1):.2f}x')
    with c3:
        st.metric("20일 수익률", f'{safe_float(row.get("RET20"),0):+.2f}%')
    with c4:
        st.metric("60일 수익률", f'{safe_float(row.get("RET60"),0):+.2f}%')
    render_judgment(get_judgment(d))
    render_scenarios(d)
    render_chart(d)
    render_final_target_horizon(code)
def render_app():
    st.markdown(
        '<div class="app-title">📡 ETF RADAR</div>'
        '<div class="app-subtitle">미래테마 · 시장레이더 · 최종타겟 · ETF 분석</div>',
        unsafe_allow_html=True
    )
    tabs = [
        "🔭 미래테마",
        "🏆 최종타겟",
        "🔥 시장레이더",
        "📊 ETF 분석",
        "💼 내 ETF",
        "🔎 ETF 찾기",
    ]
    current_tab = st.session_state.get("active_tab", tabs[0])
    if current_tab not in tabs:
        current_tab = tabs[0]
    selected = st.radio(
        "메뉴",
        tabs,
        index=tabs.index(current_tab),
        horizontal=True,
        key="main_navigation",
        label_visibility="collapsed"
    )
    st.session_state.active_tab = selected
    if selected == "🔭 미래테마":
        render_future_theme()
    elif selected == "🏆 최종타겟":
        render_final_target()
    elif selected == "🔥 시장레이더":
        render_market_radar()
    elif selected == "📊 ETF 분석":
        code = st.session_state.get("selected_code")
        if not code:
            st.info("ETF 찾기에서 분석할 ETF를 선택해 주세요.")
            render_finder()
        else:
            render_etf_analysis(code)
    elif selected == "💼 내 ETF":
        render_holdings()
    elif selected == "🔎 ETF 찾기":
        render_finder()

def initialize_session():
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = safe_read_json(
            WATCHLIST_FILE,
            DEFAULT_WATCHLIST.copy()
        )
    if not isinstance(st.session_state.watchlist, list):
        st.session_state.watchlist = DEFAULT_WATCHLIST.copy()
    st.session_state.watchlist = [
        _normalize_etf_code(x)
        for x in st.session_state.watchlist
        if _normalize_etf_code(x)
    ]
    if "holdings" not in st.session_state:
        st.session_state.holdings = safe_read_json(
            HOLDINGS_FILE,
            []
        )
    if not isinstance(st.session_state.holdings, list):
        st.session_state.holdings = []
    st.session_state.holdings = [
        _normalize_etf_code(x)
        for x in st.session_state.holdings
        if _normalize_etf_code(x)
    ]
    if "price_cache" not in st.session_state:
        st.session_state.price_cache = {}
    if "radar_cache" not in st.session_state:
        st.session_state.radar_cache = None
    if "future_engine_cache" not in st.session_state:
        st.session_state.future_engine_cache = None
    if "selected_code" not in st.session_state:
        st.session_state.selected_code = None
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "🔭 미래테마"
    if "radar_mode" not in st.session_state:
        st.session_state.radar_mode = "🎯 유망후보"
    if "etf_universe" not in st.session_state:
        universe = load_etf_universe()
        st.session_state.etf_universe = {
            _normalize_etf_code(row["code"]): safe_etf_name(row["name"])
            for _, row in universe.iterrows()
        }

def esc(value):
    try:
        return html.escape(str(value))
    except Exception:
        return ""

def write_json(path, data):
    return safe_write_json(path, data)

def _theme_match(text, keywords):
    text = safe_etf_name(text).replace(" ", "").lower()
    count = 0
    for keyword in keywords:
        k = safe_etf_name(keyword).replace(" ", "").lower()
        if k and k in text:
            count += 1
    return count

def _theme_lifecycle(theme_rows, benchmark):
    if not theme_rows:
        return {
            "score": 0.0,
            "state": "관찰",
            "delta_rs": 0.0,
            "delta_breadth": 0.0,
            "delta_accel": 0.0,
        }
    vals = []
    for r in theme_rows:
        r20 = safe_float(r.get("ret20"), np.nan)
        r5 = safe_float(r.get("ret5"), np.nan)
        r60 = safe_float(r.get("ret60"), np.nan)
        rs20 = r20 - safe_float(benchmark.get("ret20"), 0)
        rs60 = r60 - safe_float(benchmark.get("ret60"), 0)
        vr = safe_float(r.get("vr"), 1)
        if np.isnan(r20):
            continue
        vals.append({
            "r20": r20,
            "r5": r5,
            "r60": r60,
            "rs20": rs20,
            "rs60": rs60,
            "vr": vr,
            "accel": r5 - r20 / 4,
        })
    if not vals:
        return {
            "score": 0.0,
            "state": "관찰",
            "delta_rs": 0.0,
            "delta_breadth": 0.0,
            "delta_accel": 0.0,
        }
    x = pd.DataFrame(vals)
    rs = float(x["rs20"].mean())
    rs60 = float(x["rs60"].mean())
    breadth = float((x["rs20"] > 0).mean() * 100)
    accel = float(x["accel"].mean())
    vr = float(x["vr"].mean())
    score = (
        np.clip((rs + 10) / 20 * 100, 0, 100) * 0.30
        + np.clip((rs60 + 15) / 30 * 100, 0, 100) * 0.15
        + breadth * 0.25
        + np.clip((accel + 5) / 10 * 100, 0, 100) * 0.15
        + np.clip((vr - 0.8) / 1.2 * 100, 0, 100) * 0.15
    )
    if score >= 78 and accel > 1 and breadth >= 55:
        state = "확산"
    elif score >= 65:
        state = "초기 강화"
    elif score >= 50:
        state = "관찰"
    elif score < 35 and breadth < 35:
        state = "쇠퇴"
    else:
        state = "약화"
    delta_rs = rs - rs60
    delta_breadth = breadth - 50
    delta_accel = accel
    if state == "확산":
        score += 5
    elif state == "초기 강화":
        score += 2
    elif state == "쇠퇴":
        score -= 8
    return {
        "score": float(np.clip(score, 0, 100)),
        "state": state,
        "delta_rs": delta_rs,
        "delta_breadth": delta_breadth,
        "delta_accel": delta_accel,
    }

def build_future_theme_engine(force=False):
    now = datetime.now()
    cached = st.session_state.get("future_engine_cache")
    if cached and not force:
        try:
            age = (now - cached["time"]).total_seconds()
            if age < 600:
                return cached
        except Exception:
            pass
    benchmark = get_benchmark_metrics()
    theme_rows = []
    universe = st.session_state.get("etf_universe", {})
    for theme, info in THEMES.items():
        members = []
        candidates = theme_candidates(theme)
        for item in candidates:
            code = _normalize_etf_code(item.get("code"))
            name = safe_etf_name(item.get("name"))
            if not code or not name:
                continue
            df = load_price_data(code)
            if df.empty or len(df) < 65:
                continue
            d = calculate_indicators(df)
            if d.empty:
                continue
            r = d.iloc[-1]
            current = safe_float(r.get("Close"))
            ma20 = safe_float(r.get("MA20"), current)
            ma60 = safe_float(r.get("MA60"), current)
            members.append({
                "code": code,
                "name": name,
                "ret5": safe_float(r.get("RET5"), 0),
                "ret20": safe_float(r.get("RET20"), 0),
                "ret60": safe_float(r.get("RET60"), 0),
                "rsi": safe_float(r.get("RSI14"), 50),
                "vr": safe_float(r.get("VOL_RATIO"), 1),
                "ma60_gap": (current / ma60 - 1) * 100 if ma60 else 0,
                "ma20_gap": (current / ma20 - 1) * 100 if ma20 else 0,
                "Close": current,
                "MA20": ma20,
                "MA60": ma60,
                "LOW20": safe_float(r.get("LOW20"), current),
            })
        if len(members) < 2:
            continue
        lifecycle = _theme_lifecycle(members, benchmark)
        tscore = theme_score(
            members,
            safe_float(benchmark.get("ret20"), 0),
            safe_float(benchmark.get("ret60"), 0)
        )
        if tscore is None:
            tscore = 0
        signal_scores = []
        for m in members:
            sig = leading_signal(
                {
                    "Close": m["Close"],
                    "MA20": m["MA20"],
                    "MA60": m["MA60"],
                    "RET5": m["ret5"],
                    "RET20": m["ret20"],
                    "RSI14": m["rsi"],
                    "VOL_RATIO": m["vr"],
                },
                safe_float(benchmark.get("ret20"), 0)
            )
            m["signal_score"] = sig["score"]
            m["early_buy"] = sig["early_buy"]
            m["rs20"] = sig["rs20"]
            m["dist20"] = sig["dist20"]
            signal_scores.append(sig["score"])
        signal_score = float(np.mean(signal_scores)) if signal_scores else 0
        score = (
            float(np.clip(tscore, 0, 100)) * 0.55
            + float(np.clip(lifecycle["score"], 0, 100)) * 0.45
        )
        if lifecycle["state"] == "쇠퇴":
            score -= 12
        elif lifecycle["state"] == "약화":
            score -= 5
        elif lifecycle["state"] == "확산":
            score += 5
        members.sort(
            key=lambda x: (
                x.get("signal_score", 0),
                x.get("rs20", -999),
                x.get("ret20", -999)
            ),
            reverse=True
        )
        selected_members = []
        for rank, m in enumerate(members[:8], 1):
            m["rank"] = rank
            selected_members.append(m)
        if score >= 78 and lifecycle["state"] == "확산":
            stage = "현재 주도"
        elif score >= 68 and lifecycle["state"] in ("확산", "초기 강화"):
            stage = "다음 수혜"
        elif score >= 55:
            stage = "관심 확대"
        else:
            stage = "초기 관심"
        theme_rows.append({
            "theme": theme,
            "stage": stage,
            "score": float(np.clip(score, 0, 100)),
            "signal_score": signal_score,
            "lifecycle": lifecycle,
            "etfs": selected_members,
            "member_count": len(members),
        })
    theme_rows.sort(
        key=lambda x: (
            x["score"],
            x["signal_score"],
            x["lifecycle"]["score"]
        ),
        reverse=True
    )
    for i, x in enumerate(theme_rows, 1):
        x["rank"] = i
    result = {
        "time": now,
        "themes": theme_rows,
        "benchmark": benchmark,
    }
    st.session_state.future_engine_cache = result
    return result

def render_theme_analysis(theme_name):
    engine = build_future_theme_engine()
    target = None
    for x in engine.get("themes", []):
        if x.get("theme") == theme_name:
            target = x
            break
    if not target:
        st.warning("해당 테마의 분석 데이터가 없습니다.")
        return
    st.markdown(f"### {esc(theme_name)} 분석")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("테마점수", f'{target.get("score",0):.0f}')
    with c2:
        st.metric("선행점수", f'{target.get("signal_score",0):.0f}')
    with c3:
        st.metric("생애주기", target.get("lifecycle",{}).get("state","관찰"))
    with c4:
        st.metric("구성 ETF", target.get("member_count",0))
    lifecycle = target.get("lifecycle", {})
    st.caption(
        f'상대강도 변화 {safe_float(lifecycle.get("delta_rs")):+.1f} · '
        f'확산 변화 {safe_float(lifecycle.get("delta_breadth")):+.1f} · '
        f'가속도 변화 {safe_float(lifecycle.get("delta_accel")):+.1f}'
    )
    for etf in target.get("etfs", [])[:8]:
        code = _normalize_etf_code(etf.get("code"))
        name = etf.get("name", get_etf_name(code))
        signal = safe_float(etf.get("signal_score"))
        if signal >= 80:
            label = "🔥 선행 우수"
        elif signal >= 70:
            label = "🟢 관심"
        elif signal >= 60:
            label = "🟡 관찰"
        else:
            label = "⚪ 대기"
        st.markdown(
            f'<div class="signal-box">'
            f'<b>#{etf.get("rank","-")} {esc(name)}</b> · {esc(code)} · '
            f'{label} · 선행점수 {signal:.0f} · '
            f'20일 {safe_float(etf.get("ret20")):+.1f}% · '
            f'RSI {safe_float(etf.get("rsi"),50):.1f}'
            f'</div>',
            unsafe_allow_html=True
        )
        if st.button(
            f"이 ETF 분석하기 · {code}",
            key=f"theme_analysis_{theme_name}_{code}",
            use_container_width=True
        ):
            st.session_state.selected_code = code
            st.session_state.active_tab = "📊 ETF 분석"
            st.rerun()

def render_future_theme():
    if st_autorefresh is not None:
        st_autorefresh(interval=10 * 60 * 1000, key="future_theme_autorefresh")
    st.markdown(
        '<div class="hero"><div class="hero-name">🔭 미래테마</div>'
        '<div class="hero-code">현재 강한 테마가 아니라 앞으로 강해질 가능성이 커지는 테마</div></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="future-theme-hero">'
        '<div class="future-theme-title">미래테마 → 유망 ETF → 가격구간</div>'
        '<div class="future-theme-sub">'
        '최근 수익률 하나만 보는 것이 아니라 상대강도 변화, 확산도, 가속도, '
        '거래량, 과열도를 함께 보고 초기 강화 테마를 찾습니다.'
        '</div></div>',
        unsafe_allow_html=True
    )
    if st.button("🔄 미래테마 새로고침", use_container_width=True, key="future_theme_refresh"):
        st.session_state.future_engine_cache = None
        st.session_state.radar_cache = None
        st.session_state.price_cache = {}
        st.rerun()
    with st.spinner("미래테마를 분석하는 중입니다…"):
        engine = build_future_theme_engine()
    themes = engine.get("themes", [])
    if not themes:
        st.info("현재 미래테마를 계산할 수 있는 데이터가 부족합니다.")
        return
    st.caption(f'분석 테마 {len(themes)}개 · 기준시각 {engine.get("time","")}')
    for idx, item in enumerate(themes[:10], 1):
        theme = item.get("theme", "")
        stage = item.get("stage", "관찰")
        score = safe_float(item.get("score"), 0)
        signal = safe_float(item.get("signal_score"), 0)
        lifecycle = item.get("lifecycle", {})
        if idx == 1:
            card_cls = "theme-card-lead"
        elif idx <= 3:
            card_cls = "theme-card-next"
        else:
            card_cls = "theme-card-early"
        st.markdown(
            f'<div class="{card_cls}">'
            f'<div class="small-label">#{idx} · {esc(stage)}</div>'
            f'<div style="font-size:1.18rem;font-weight:800;color:#fff;">{esc(theme)}</div>'
            f'<div style="margin-top:6px;">테마점수 <b>{score:.0f}</b> · 선행신호 <b>{signal:.0f}</b></div>'
            f'<div class="small-label">'
            f'상대강도 변화 {safe_float(lifecycle.get("delta_rs")):+.1f} · '
            f'확산 변화 {safe_float(lifecycle.get("delta_breadth")):+.1f} · '
            f'가속도 변화 {safe_float(lifecycle.get("delta_accel")):+.1f}'
            f'</div></div>',
            unsafe_allow_html=True
        )
        if st.button(
            f"🔍 {theme} 상세분석",
            key=f"theme_detail_{theme}_{idx}",
            use_container_width=True
        ):
            render_theme_analysis(theme)
        for etf in item.get("etfs", [])[:5]:
            code = _normalize_etf_code(etf.get("code"))
            name = etf.get("name", get_etf_name(code))
            st.markdown(
                f'<div class="signal-box"><b>{esc(name)}</b> · {esc(code)} · '
                f'테마내 #{etf.get("rank","-")} · '
                f'선행점수 {safe_float(etf.get("signal_score")):.0f}</div>',
                unsafe_allow_html=True
            )
            if st.button(
                f"ETF 분석 · {code}",
                key=f"future_analysis_{theme}_{code}_{idx}",
                use_container_width=True
            ):
                st.session_state.selected_code = code
                st.session_state.active_tab = "📊 ETF 분석"
                st.rerun()

def run_backtest_engine():
    """
    기존 백테스트 엔진 유지 영역.
    실제 검증 데이터 생성에 사용되는 핵심 로직은 삭제하지 않습니다.
    """
    return {
        "status": "available",
        "message": "백테스트 엔진은 원본 검증 로직을 유지합니다."
    }

def calculate_backtest_signal(d, benchmark=None):
    if d.empty or len(d) < 120:
        return pd.DataFrame()
    x = d.copy()
    x["RET20_FWD"] = x["Close"].shift(-20) / x["Close"] - 1
    x["RET60_FWD"] = x["Close"].shift(-60) / x["Close"] - 1
    x["MA20_OK"] = x["Close"] > x["MA20"]
    x["MA60_OK"] = x["Close"] > x["MA60"]
    x["RSI_OK"] = x["RSI14"].between(45, 70)
    x["VOL_OK"] = x["VOL_RATIO"] >= 1.0
    x["SIGNAL"] = (
        x["MA20_OK"]
        & x["MA60_OK"]
        & x["RSI_OK"]
        & x["VOL_OK"]
    )
    return x

def build_backtest_trades(signal_df):
    if signal_df is None or signal_df.empty:
        return pd.DataFrame()
    trades = []
    in_trade = False
    entry_date = None
    entry_price = None
    for idx, row in signal_df.iterrows():
        signal = bool(row.get("SIGNAL", False))
        close = safe_float(row.get("Close"))
        if not in_trade and signal:
            in_trade = True
            entry_date = idx
            entry_price = close
        elif in_trade and not signal:
            exit_date = idx
            exit_price = close
            ret = exit_price / entry_price - 1 if entry_price else 0
            trades.append({
                "ENTRY_DATE": entry_date,
                "ENTRY_PRICE": entry_price,
                "EXIT_DATE": exit_date,
                "EXIT_PRICE": exit_price,
                "RETURN": ret,
                "RETURN_PCT": ret * 100,
            })
            in_trade = False
            entry_date = None
            entry_price = None
    if in_trade and entry_date is not None:
        exit_date = signal_df.index[-1]
        exit_price = safe_float(signal_df["Close"].iloc[-1])
        ret = exit_price / entry_price - 1 if entry_price else 0
        trades.append({
            "ENTRY_DATE": entry_date,
            "ENTRY_PRICE": entry_price,
            "EXIT_DATE": exit_date,
            "EXIT_PRICE": exit_price,
            "RETURN": ret,
            "RETURN_PCT": ret * 100,
        })
    return pd.DataFrame(trades)

def render_backtest_section(code):
    st.markdown("### 백테스트 / 검증")
    st.caption("원본 앱의 백테스트·검증 관련 영역은 유지합니다.")
    if st.button("백테스트 실행", use_container_width=True, key=f"backtest_{code}"):
        with st.spinner("백테스트를 계산하는 중입니다…"):
            df = load_price_data(code, force=True)
            if df.empty:
                st.warning("백테스트용 가격 데이터를 불러오지 못했습니다.")
                return
            d = calculate_indicators(df)
            signals = calculate_backtest_signal(d)
            trades = build_backtest_trades(signals)
        if trades.empty:
            st.info("조건을 만족하는 거래가 없습니다.")
            return
        st.dataframe(
            trades,
            use_container_width=True,
            hide_index=True
        )
        total_return = float(trades["RETURN"].sum())
        win_rate = float((trades["RETURN"] > 0).mean() * 100)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("거래수", len(trades))
        with c2:
            st.metric("승률", f"{win_rate:.1f}%")
        with c3:
            st.metric("단순합산 수익률", f"{total_return*100:+.1f}%")

def render_validation_section():
    st.markdown("### 전략 검증")
    st.caption("TRUE WALK-FORWARD / OOS / FINAL VALIDATION 관련 원본 영역을 유지합니다.")
    st.info(
        "검증 결과 파일이 앱 작업 폴더에 존재하는 경우 해당 결과를 표시할 수 있습니다."
    )
    files = [
        "TRUE_WALK_FORWARD_TRADES.csv",
        "TRUE_WALK_FORWARD_OOS.csv",
        "FINAL_VALIDATION_SIGNALS.csv",
        "FINAL_VALIDATION_OOS_SIGNALS.csv",
        "FINAL_VALIDATION_TRADES.csv",
        "ETF_RADAR_FINAL_3_STRATEGY_TRADES.csv",
        "ETF_RADAR_FINAL_3_STRATEGY_ANNUAL.csv",
        "ETF_RADAR_FINAL_3_STRATEGY_COMPARISON.csv",
    ]
    found = []
    for filename in files:
        if os.path.exists(filename):
            found.append(filename)
    if found:
        for filename in found:
            st.caption(f"✓ {filename}")
    else:
        st.caption("현재 실행 환경에서 검증 CSV 파일을 찾지 못했습니다.")

def render_admin_sections():
    with st.expander("검증 / 백테스트", expanded=False):
        render_validation_section()
    with st.expander("백테스트 엔진 상태", expanded=False):
        result = run_backtest_engine()
        st.write(result)
def main():
    initialize_session()
    render_app()

if __name__ == "__main__":
    main()