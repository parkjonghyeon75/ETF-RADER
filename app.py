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
# ETF Technical Radar v6 (메인: 기술적 분석 + 서브메인: DC연금 카테고리별 원석 찾기)
# ============================================================

st.set_page_config(
    page_title="ETF Radar & DC Gem Finder",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 🎨 시각적 가독성 개선 CSS (라이트 모드)
st.markdown("""
<style>
.stApp {max-width: 1000px; margin: 0 auto; background-color: #f8fafc;}
.block-container {padding-top: 1rem; padding-bottom: 2rem; padding-left: .8rem; padding-right: .8rem;}

div[data-testid="stMetric"] {
    background: #ffffff; 
    border: 1px solid #e2e8f0; 
    border-radius: 10px; 
    padding: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
div[data-testid="stMetricLabel"] {color: #475569 !important; font-size: 0.95rem !important; font-weight: 600;}
div[data-testid="stMetricValue"] {color: #0f172a !important; font-weight: 700;}

.radar-card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 16px; margin-bottom: 12px; color: #0f172a; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.gem-card {
    background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px;
    padding: 14px; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}
.highlight-green {color: #16a34a; font-weight: bold;}
.highlight-red {color: #dc2626; font-weight: bold;}
.highlight-yellow {color: #d97706; font-weight: bold;}

.price-zone {
    border-radius: 10px; padding: 12px; margin: 6px 0;
    border: 1px solid #e2e8f0; background: #ffffff; color: #0f172a; font-size: 0.95rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}

@media (max-width: 600px) {
    .block-container {padding-left: .55rem; padding-right: .55rem;}
    h1 {font-size: 1.55rem;}
    h2 {font-size: 1.25rem;}
    h3 {font-size: 1.05rem;}
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 파일 관리 및 DC 퇴직연금 카테고리 풀(Pool) 정의
# -----------------------------
WATCHLIST_FILE = "watchlist.json"
THEME_FILE = "theme_info.json"

DC_PENSION_POOLS = {
    "🇺🇸 미국 대표지수 / 성장주": {
        "360750": "TIGER 미국S&P500",
        "133690": "TIGER 미국나스닥100",
        "487240": "KODEX 미국AI테크TOP10",
        "379800": "KODEX 미국S&P500TR",
        "379810": "KODEX 미국나스닥100TR"
    },
    "🤖 AI / 반도체 / 테크": {
        "395160": "KODEX AI반도체TOP2플러스",
        "471990": "KODEX AI전력핵심설비",
        "462100": "TIGER AI반도체핵심공정",
        "441680": "SOL 미국AI반도체",
        "0173Y0": "KODEX 미국AI광통신네트워크"
    },
    "🔋 2차전지 / 소부장 / 신재생": {
        "305540": "KODEX 2차전지산업",
        "364980": "TIGER 2차전지소부장",
        "438320": "KODEX 2차전지핵심소재",
        "329750": "TIGER 친환경자동차"
    },
    "💊 바이오 / 헬스케어": {
        "329200": "TIGER 헬스케어",
        "266420": "KODEX 바이오",
        "462610": "ARIRANG 3대주주바이오"
    },
    "💰 배당 / 월배당 / 인컴": {
        "458730": "TIGER 미국배당다우존스",
        "441680": "SOL 미국배당 다우존스",
        "476480": "KODEX 미국배당커버드콜",
        "451780": "TIGER 미국배당+7%프리미엄"
    },
    "🛡️ 채권 / 안전자산 / 금리": {
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
        "cycle": "성장기 (메모리 재편기)",
        "desc": "SK하이닉스, 삼성전자 중심의 HBM 및 반도체 공정 핵심 기업 추종.",
        "long_view": "메모리 반도체 업황 사이클 및 AI 서버 CapEx 지속 여부가 중장기 주가를 좌우합니다."
    },
    "487240": {
        "theme": "미국 AI 빅테크 TOP10",
        "cycle": "고성장기 (시장 독점기)",
        "desc": "엔비디아, 마이크로소프트 등 독점적 지위를 지닌 메가캡 중심 포트폴리오.",
        "long_view": "단순 기대감을 넘어 AI 서비스 수익화 단계 진입에 따른 실적 확인이 핵심입니다."
    },
    "471990": {
        "theme": "AI 전력망 / 변압기 / 원자력",
        "cycle": "확장기 (초기 병목 해소)",
        "desc": "AI 데이터센터 증설의 최대 병목인 전력 부족을 해결하는 인프라 기업.",
        "long_view": "북미 노후 전력망 교체 및 데이터센터 전력 공급 계약 확대로 장기 수혜가 기대됩니다."
    },
    "133690": {
        "theme": "미국 대표 기술주 (나스닥100)",
        "cycle": "구조적 장기 우상향",
        "desc": "미국 나스닥 상장 상위 100개 혁신 기술기업 추종 패시브 자산.",
        "long_view": "개별 테마의 순환매 변동성을 완화해 주는 포트폴리오 코어 자산입니다."
    },
    "360750": {
        "theme": "미국 대표 대형주 (S&P500)",
        "cycle": "구조적 장기 우상향",
        "desc": "미국 자본주의 핵심 대형 기업 500개 추종 기초 체력 자산.",
        "long_view": "테마주 변동성 위험을 흡수하는 필수 보유 종목입니다."
    },
    "458730": {
        "theme": "미국 배당 성장",
        "cycle": "안정적 우상향",
        "desc": "미국 우량 배당주에 투자하여 주기적인 배당과 성장을 동시에 추구.",
        "long_view": "퇴직연금 장기 적립식 투자에 가장 적합한 배당 성장 코어 자산입니다."
    }
}

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) and data else DEFAULT_WATCHLIST.copy()
        except Exception:
            pass
    return DEFAULT_WATCHLIST.copy()

def save_watchlist(data):
    try:
        with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_theme_info():
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else DEFAULT_THEME_INFO.copy()
        except Exception:
            pass
    return DEFAULT_THEME_INFO.copy()

def save_theme_info(data):
    try:
        with open(THEME_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()

if "theme_info" not in st.session_state:
    st.session_state.theme_info = load_theme_info()

# -----------------------------
# 데이터 수집 (네이버 금융 크롤링 + 야후 파이낸스 백업)
# -----------------------------
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
        url = (
            "https://fchart.stock.naver.com/sise.nhn?"
            f"symbol={urllib.parse.quote(code)}&timeframe=day&count={count}&requestType=0"
        )
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

        df = pd.DataFrame(rows).set_index("Date").sort_index()
        return df
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
                data = yf.download(
                    f"{clean_code}{suffix}",
                    period="2y",
                    progress=False,
                    auto_adjust=False,
                    threads=False
                )
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

# -----------------------------
# 기술 지표 계산
# -----------------------------
def calculate_indicators(df):
    df = df.copy()

    for n in [5, 20, 60, 120]:
        df[f"MA{n}"] = df["Close"].rolling(n).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
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

# -----------------------------
# 지지/저항 및 매물대 계산
# -----------------------------
def get_support_resistance(df):
    current = float(df["Close"].iloc[-1])
    recent20 = df.iloc[-20:]

    supports = []
    resistances = []

    for col in ["MA20", "MA60", "MA120"]:
        if col in df.columns and pd.notna(df[col].iloc[-1]):
            p = float(df[col].iloc[-1])
            if p < current: supports.append({"price": p, "strength": 2})
            elif p > current: resistances.append({"price": p, "strength": 2})

    p_low = float(recent20["Low"].min())
    if p_low < current: supports.append({"price": p_low, "strength": 3})

    p_high = float(recent20["High"].max())
    if p_high > current: resistances.append({"price": p_high, "strength": 3})

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
    low = float(data["Low"].min())
    high = float(data["High"].max())
    if high <= low: return pd.DataFrame(columns=["price", "volume"])

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

# -----------------------------
# 기술 점수 및 매매 전략
# -----------------------------
def technical_score(df):
    x = df.iloc[-1]
    prev = df.iloc[-2]
    score = 0
    close = float(x["Close"])
    ma5, ma20, ma60 = x["MA5"], x["MA20"], x["MA60"]
    rsi = x["RSI"]
    macd, sig, hist = x["MACD"], x["MACD_Signal"], x["MACD_Hist"]
    vol_ratio = x["Vol_Ratio"]

    if pd.notna(ma20) and close > ma20: score += 15
    if pd.notna(ma60) and ma20 > ma60: score += 10
    if pd.notna(rsi):
        if 50 <= rsi < 70: score += 20
        elif 40 <= rsi < 50: score += 12
        else: score += 5
    if pd.notna(macd) and pd.notna(sig):
        if macd > sig and hist > 0: score += 20
        elif macd > sig: score += 15
        else: score += 5
    if pd.notna(vol_ratio) and 1.2 <= vol_ratio <= 3.0 and close >= prev["Close"]:
        score += 15

    score = int(max(0, min(100, score + 20)))
    if score >= 80: label = "강한 상승세"
    elif score >= 65: label = "상승 우세"
    elif score >= 45: label = "중립/관망"
    elif score >= 30: label = "조정 국면"
    else: label = "약세/하락 위험"
    return score, label

def detect_patterns(df, supports, resistances):
    x = df.iloc[-1]
    close = float(x["Close"])
    ma20, ma60, rsi = x["MA20"], x["MA60"], x["RSI"]
    macd, sig, vol = x["MACD"], x["MACD_Signal"], x["Vol_Ratio"]
    recent20_high = float(df.iloc[-21:-1]["High"].max()) if len(df) >= 22 else float(df["High"].max())
    
    patterns = []
    if pd.notna(ma20) and pd.notna(ma60) and pd.notna(rsi):
        if close >= ma20 * 0.985 and close <= ma20 * 1.025 and ma20 > ma60 and 42 <= rsi <= 65:
            patterns.append("💡 눌림목 매수 적기")
    if close > recent20_high and vol >= 1.3 and pd.notna(macd) and macd > sig:
        patterns.append("🚀 강력한 저항선 돌파")
    if pd.notna(rsi) and rsi >= 70:
        patterns.append("⚠️ 단기 과열 (추격매수 위험)")
    if pd.notna(ma20) and close < ma20 and macd < sig:
        patterns.append("🔻 단기 추세 약화")
    if not patterns:
        patterns.append("📈 차분한 우상향 흐름" if close > ma20 else "💤 횡보/관망 구간")
    return patterns

def easy_action_scenario(df, score, supports, resistances, patterns):
    x = df.iloc[-1]
    close = float(x["Close"])
    rsi = float(x["RSI"]) if pd.notna(x["RSI"]) else 50
    ma20 = float(x["MA20"]) if pd.notna(x["MA20"]) else close
    s1 = supports[0]["price"] if supports else ma20
    s2 = supports[1]["price"] if len(supports) > 1 else ma20 * 0.97
    r1 = resistances[0]["price"] if resistances else close * 1.03
    r2 = resistances[1]["price"] if len(resistances) > 1 else close * 1.06

    if "⚠️ 단기 과열 (추격매수 위험)" in patterns:
        status_title = "🟠 과열 구간 : 지금 바로 사지 말고 기다리세요!"
        buy_guide = f"RSI {rsi:.0f} 과열 상태입니다. **{s1:,.0f}원 부근**까지 내려올 때 분할 매수하세요."
        sell_guide = f"**{r1:,.0f}원~{r2:,.0f}원 매물대** 구간에서 일부 이익 실현을 고려하세요."
        wait_guide = f"**{s1:,.0f}원 지지선** 이탈 여부를 확인하세요."
    elif "💡 눌림목 매수 적기" in patterns:
        status_title = "🟢 눌림목 기회 : 적립식으로 모아가기 좋은 타이밍!"
        buy_guide = f"20일선 근처인 **{s1:,.0f}원~{close:,.0f}원 사이**는 매력적인 분할 매수 구간입니다."
        sell_guide = f"저항대인 **{r1:,.0f}원**을 1차 목표가로 설정하세요."
        wait_guide = f"핵심 지지선 **{s2:,.0f}원** 하향 이탈 시 리스크 관리가 필요합니다."
    else:
        status_title = "🔵 안정적 흐름 : 추세 대응 구간"
        buy_guide = f"**{s1:,.0f}원 지지선** 근처에서 매수 관점이 유효합니다."
        sell_guide = f"**{r1:,.0f}원** 도달 시 비중 조절을 검토하세요."
        wait_guide = f"박스권 내 등락을 모니터링하세요."

    return status_title, buy_guide, sell_guide, wait_guide, s1, s2, r1, r2

# -----------------------------
# 💎 DC연금 카테고리별 원석 찾기 엔진
# -----------------------------
def find_dc_category_gems(pool_dict):
    gem_list = []
    for code, name in pool_dict.items():
        raw_df, _ = load_etf_data(code, "6m")
        if raw_df is None or len(raw_df) < 30:
            continue
        df = calculate_indicators(raw_df)
        x = df.iloc[-1]
        prev = df.iloc[-2]
        
        reasons = []
        score_add = 0
        
        if pd.notna(x["MACD"]) and pd.notna(x["MACD_Signal"]):
            if prev["MACD"] <= prev["MACD_Signal"] and x["MACD"] > x["MACD_Signal"]:
                reasons.append("⚡ MACD 골든크로스 (상승 반전)")
                score_add += 35
        if pd.notna(x["Vol_Ratio"]) and x["Vol_Ratio"] >= 1.4 and x["Close"] > prev["Close"]:
            reasons.append("🔥 거래량 유입 동반 상승")
            score_add += 30
        if pd.notna(x["MA20"]) and pd.notna(x["RSI"]):
            if 0.98 <= (x["Close"] / x["MA20"]) <= 1.02 and 42 <= x["RSI"] <= 62:
                reasons.append("🎯 20일선 눌림목 지지 반등")
                score_add += 25
        if pd.notna(x["RSI"]) and x["RSI"] < 42 and x["Close"] > prev["Close"]:
            reasons.append("🛡️ 과매도 구간 탈출 시도")
            score_add += 20

        if reasons:
            gem_list.append({
                "code": code,
                "name": name,
                "price": float(x["Close"]),
                "change": float((x["Close"] - prev["Close"]) / prev["Close"] * 100),
                "reasons": reasons,
                "score": min(100, 50 + score_add)
            })
    return sorted(gem_list, key=lambda x: x["score"], reverse=True)

# -----------------------------
# Plotly 차트 생성
# -----------------------------
def make_chart(df, supports, resistances):
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.50, 0.16, 0.17, 0.17])
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="주가"), row=1, col=1)

    for col, color in [("MA5", "#d97706"), ("MA20", "#ea580c"), ("MA60", "#16a34a"), ("MA120", "#7c3aed")]:
        if col in df:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], line=dict(color=color, width=1.4), name=col), row=1, col=1)

    for i, item in enumerate(supports[:2]):
        fig.add_hline(y=item["price"], row=1, col=1, line_dash="dot", line_color="#16a34a", annotation_text=f"지지 S{i+1}", annotation_position="bottom left")
    for i, item in enumerate(resistances[:2]):
        fig.add_hline(y=item["price"], row=1, col=1, line_dash="dash", line_color="#dc2626", annotation_text=f"저항 R{i+1}", annotation_position="top left")

    vol_colors = ["#dc2626" if c >= o else "#2563eb" for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], marker_color=vol_colors, name="거래량"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], line=dict(color="#2563eb", width=1.5), name="RSI"), row=3, col=1)
    fig.add_hline(y=70, row=3, col=1, line_dash="dot", line_color="#dc2626")
    fig.add_hline(y=30, row=3, col=1, line_dash="dot", line_color="#16a34a")

    fig.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"], name="MACD Hist"), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], line=dict(color="#2563eb"), name="MACD"), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD_Signal"], line=dict(color="#dc2626"), name="Signal"), row=4, col=1)

    fig.update_layout(height=700, margin=dict(l=5, r=5, t=10, b=5), xaxis_rangeslider_visible=False, template="plotly_white", showlegend=False, dragmode=False)
    fig.update_yaxes(fixedrange=True)
    return fig

# ============================================================
# UI 메인 레이아웃
# ============================================================
st.title("📈 ETF 기술적 레이더 & 💎 DC연금 원석 찾기")

watchlist = st.session_state.watchlist
options = list(watchlist.values()) + ["➕ 종목코드로 관심종목 추가"]

c1, c2 = st.columns([2.1, 1])
with c1:
    selected = st.selectbox("⭐ 관심 ETF 선택 (개별 종목 분석용)", options)
with c2:
    period = st.selectbox("분석 기간", ["6m", "1y", "2y"], index=1)

if selected == "➕ 종목코드로 관심종목 추가":
    st.subheader("종목코드 등록")
    a, b = st.columns([2, 1])
    with a:
        new_code = st.text_input("종목코드 6자리", placeholder="예: 395160", label_visibility="collapsed")
    with b:
        add = st.button("⭐ 추가", use_container_width=True)

    if add and new_code:
        code = "".join(filter(str.isalnum, new_code))
        test_df, _ = load_etf_data(code, "6m")
        if test_df is not None:
            name = get_stock_name(code)
            st.session_state.watchlist[code] = f"{name} ({code})"
            save_watchlist(st.session_state.watchlist)
            if code not in st.session_state.theme_info:
                st.session_state.theme_info[code] = {
                    "theme": "신규 등록 테마", "cycle": "관찰 필요",
                    "desc": f"{name} 관련 정보 등록 필요", "long_view": "중장기 관점을 입력해주세요."
                }
                save_theme_info(st.session_state.theme_info)
            st.success(f"{name} ({code}) 등록 완료")
            st.rerun()
        else:
            st.error("유효하지 않은 종목코드입니다.")
    st.stop()

symbol_input = next(k for k, v in watchlist.items() if v == selected)

del_col, _ = st.columns([1, 3])
with del_col:
    if st.button("🗑 목록에서 삭제", use_container_width=True):
        del st.session_state.watchlist[symbol_input]
        save_watchlist(st.session_state.watchlist)
        st.rerun()

with st.spinner("데이터 분석 중..."):
    raw_df, code = load_etf_data(symbol_input, period)

if raw_df is None:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()

df = calculate_indicators(raw_df).dropna(subset=["Close"]).copy()
score, score_label = technical_score(df)
supports, resistances = get_support_resistance(df)
vp = volume_profile(df)
patterns = detect_patterns(df, supports, resistances)
status_title, buy_guide, sell_guide, wait_guide, s1, s2, r1, r2 = easy_action_scenario(
    df, score, supports, resistances, patterns
)

x = df.iloc[-1]
prev = df.iloc[-2]
price = float(x["Close"])
change = (price - float(prev["Close"])) / float(prev["Close"]) * 100
rsi = float(x["RSI"]) if pd.notna(x["RSI"]) else 50
vol_ratio = float(x["Vol_Ratio"]) if pd.notna(x["Vol_Ratio"]) else 1
macd = float(x["MACD"]) if pd.notna(x["MACD"]) else 0
macd_sig = float(x["MACD_Signal"]) if pd.notna(x["MACD_Signal"]) else 0

# -----------------------------
# 전체 기능을 분리된 탭으로 구성
# -----------------------------
main_tab1, main_tab2, main_tab3, main_tab4, main_tab5, main_tab6 = st.tabs([
    "📊 개별종목 레이더 & 매매전략",
    "💎 DC연금 카테고리별 원석 찾기", 
    "📊 정밀 차트 분석", 
    "📍 매물대 & 지지/저항", 
    "🏛️ 테마 & 중장기 분석", 
    "📖 지표 설명서"
])

with main_tab1:
    st.markdown("### 📊 현재 주가 및 종합 점수")
    m1, m2 = st.columns(2)
    with m1: st.metric("현재가", f"{price:,.0f}원", f"{change:+.2f}%")
    with m2: st.metric("종합 점수", f"{score}점 / 100점", score_label)

    st.markdown(f'<div class="radar-card"><b style="color:#b45309;">🎯 핵심 신호: {" · ".join(patterns)}</b></div>', unsafe_allow_html=True)

    st.markdown("### 💡 쉽고 명확한 매매 대응 전략")
    if "🟢" in status_title: st.success(f"### {status_title}")
    elif "🔴" in status_title: st.error(f"### {status_title}")
    elif "🟠" in status_title: st.warning(f"### {status_title}")
    else: st.info(f"### {status_title}")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f'<div class="price-zone"><b class="highlight-green">🛒 매수 전략</b><br>{buy_guide}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-zone"><b class="highlight-red">💰 익절 전략</b><br>{sell_guide}</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<div class="price-zone"><b class="highlight-yellow">🛑 손절/관망 전략</b><br>{wait_guide}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-zone"><b>📍 핵심 가격 요약</b><br>'
                    f'• <b>2차 저항</b>: <span class="highlight-red">{r2:,.0f}원</span><br>'
                    f'• <b>1차 저항</b>: <span class="highlight-red">{r1:,.0f}원</span><br>'
                    f'• <b>현재가</b>: <b>{price:,.0f}원</b><br>'
                    f'• <b>1차 지지</b>: <span class="highlight-green">{s1:,.0f}원</span><br>'
                    f'• <b>2차 지지</b>: <span class="highlight-green">{s2:,.0f}원</span></div>', unsafe_allow_html=True)

with main_tab2:
    st.subheader("💎 DC퇴직연금 카테고리별 '원석' 스크리닝")
    st.caption("퇴직연금 계좌로 투자 가능한 주요 섹터/카테고리를 선택하여, 반등 신호가 포착된 저평가 유망주를 발굴합니다.")

    selected_category = st.selectbox("📂 스캔할 DC연금 투자 카테고리 선택", list(DC_PENSION_POOLS.keys()))
    target_pool = DC_PENSION_POOLS[selected_category]

    if st.button(f"🔍 [{selected_category}] 전 종목 스캔 실행", use_container_width=True):
        st.cache_data.clear()

    with st.spinner(f"'{selected_category}' 카테고리 내 종목 정밀 분석 중..."):
        category_gems = find_dc_category_gems(target_pool)

    if category_gems:
        st.success(f"총 {len(category_gems)}개의 반등 기대 원석이 포착되었습니다!")
        for g in category_gems:
            reasons_html = "<br>".join([f"• {r}" for r in g["reasons"]])
            st.markdown(
                f'<div class="gem-card">'
                f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                f'<b style="font-size:1.05rem; color:#15803d;">💎 {g["name"]}</b>'
                f'<span style="font-size:1.0rem; font-weight:bold;">{g["price"]:,.0f}원 ({g["change"]:+.2f}%)</span>'
                f'</div>'
                f'<div style="margin-top:6px; font-size:0.9rem; color:#334155;">'
                f'<b>포착된 신호:</b><br>{reasons_html}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )
    else:
        st.info(f"현재 '{selected_category}' 카테고리 내에서 뚜렷한 상승 신호가 포착된 원석이 없습니다. 안전하게 관망하거나 다른 카테고리를 스캔해보세요.")

with main_tab3:
    st.caption("캔들차트 / 이평선 / 거래량 / RSI / MACD 통합 레이더")
    fig = make_chart(df, supports, resistances)
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True, "displayModeBar": False}, key=f"chart_{symbol_input}_{period}")

with main_tab4:
    st.subheader("📍 지지선과 저항선 분석")
    col_s, col_r = st.columns(2)
    with col_s:
        st.markdown("**🟢 지지 가격 (바닥)**")
        if supports:
            for i, item in enumerate(supports[:3], 1): st.success(f"S{i}: **{item['price']:,.0f}원**")
        else: st.info("데이터 부족")
    with col_r:
        st.markdown("**🔴 저항 가격 (벽)**")
        if resistances:
            for i, item in enumerate(resistances[:3], 1): st.warning(f"R{i}: **{item['price']:,.0f}원**")
        else: st.info("데이터 부족")

    st.subheader("🧱 매물대 집중 분포")
    if not vp.empty:
        vp_show = vp.head(5)[["price", "ratio"]].copy()
        vp_show["가격대"] = vp_show["price"].map(lambda x: f"{x:,.0f}원")
        vp_show["집중도"] = vp_show["ratio"].map(lambda x: f"{x*100:.0f}%")
        st.dataframe(vp_show[["가격대", "집중도"]], use_container_width=True, hide_index=True)

with main_tab5:
    st.subheader("🏛️ 테마 분류 및 중장기 사이클 분석")
    theme_info = st.session_state.theme_info.get(code, {
        "theme": "미등록 테마", "cycle": "관찰 필요",
        "desc": "정보 등록 필요", "long_view": "중장기 관점을 입력해주세요."
    })
    c_t1, c_t2 = st.columns(2)
    with c_t1:
        st.markdown(f"**🏷 테마**: {theme_info['theme']}")
        st.markdown(f"**🔄 사이클**: <span class='highlight-yellow'>{theme_info['cycle']}</span>", unsafe_allow_html=True)
    with c_t2:
        st.markdown(f"**📝 개요**: {theme_info['desc']}")
    st.markdown(f'<div class="price-zone"><b class="highlight-green">🎯 중장기 투자 포인트</b><br>{theme_info["long_view"]}</div>', unsafe_allow_html=True)

with main_tab6:
    st.subheader("📖 지표 가이드")
    st.markdown(f"- **RSI (현재 {rsi:.1f})**: 70 이상 과열, 30 이하 침체\n- **MACD**: 추세 반전 판단 지표\n- **거래량 비율 ({vol_ratio:.2f}배)**: 평균 대비 거래량 유입 강도")

st.caption("ETF Technical Radar & DC Gem Finder 통합 버전")
