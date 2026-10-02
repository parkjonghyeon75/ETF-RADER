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
# ETF Technical Radar v2
# 자동 지지/저항 + 매물대 + 종합점수 100점
# 눌림목 + 돌파 + 추격위험 + 매매 시나리오 + 모바일 UI
# ============================================================

st.set_page_config(
    page_title="ETF Technical Radar",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.stApp {max-width: 1000px; margin: 0 auto;}
.block-container {padding-top: 1rem; padding-bottom: 2rem; padding-left: .8rem; padding-right: .8rem;}
div[data-testid="stMetric"] {background:#1e222d; border:1px solid #2a2e39; border-radius:10px; padding:8px;}
.radar-card {
    background:#1e222d; border:1px solid #303542; border-radius:12px;
    padding:14px; margin-bottom:10px;
}
.small-muted {color:#9aa4b2; font-size:0.85rem;}
.big-score {font-size:2.0rem; font-weight:800;}
.signal-green {color:#35d07f;}
.signal-yellow {color:#f2c94c;}
.signal-red {color:#ff6b6b;}
.price-zone {
    border-radius:10px; padding:10px 12px; margin:5px 0;
    border:1px solid #303542; background:#191d26;
}
@media (max-width: 600px) {
    .block-container {padding-left:.55rem; padding-right:.55rem;}
    h1 {font-size:1.55rem;}
    h2 {font-size:1.25rem;}
    h3 {font-size:1.05rem;}
}
</style>
""", unsafe_allow_html=True)

WATCHLIST_FILE = "watchlist.json"
DEFAULT_WATCHLIST = {
    "069500": "KODEX 200 (069500)",
    "091160": "KODEX 반도체 (091160)",
    "466920": "KODEX AI반도체핵심장비 (466920)",
    "395160": "KODEX AI반도체TOP2플러스 (395160)",
    "379800": "KODEX 미국S&P500 (379800)"
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

if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()

# -----------------------------
# 데이터 수집
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
    clean_code = "".join(filter(str.isdigit, str(ticker_code)))
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
# 지표 계산
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

    df["Return5"] = df["Close"].pct_change(5) * 100
    df["Return20"] = df["Close"].pct_change(20) * 100

    tr = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - df["Close"].shift()).abs(),
        (df["Low"] - df["Close"].shift()).abs()
    ], axis=1).max(axis=1)
    df["ATR14"] = tr.rolling(14).mean()

    return df

# -----------------------------
# 자동 지지/저항
# -----------------------------
def local_extrema_levels(df, window=3):
    highs = []
    lows = []
    h = df["High"].values
    l = df["Low"].values

    for i in range(window, len(df) - window):
        if h[i] == max(h[i-window:i+window+1]):
            highs.append(h[i])
        if l[i] == min(l[i-window:i+window+1]):
            lows.append(l[i])

    return lows, highs

def cluster_levels(levels, tolerance=0.012):
    if not levels:
        return []

    levels = sorted(float(x) for x in levels if np.isfinite(x))
    clusters = []

    for price in levels:
        if not clusters:
            clusters.append([price])
            continue
        center = np.mean(clusters[-1])
        if abs(price - center) / center <= tolerance:
            clusters[-1].append(price)
        else:
            clusters.append([price])

    result = []
    for c in clusters:
        result.append({
            "price": float(np.mean(c)),
            "strength": len(c)
        })
    return result

def get_support_resistance(df):
    current = float(df["Close"].iloc[-1])
    recent = df.iloc[-120:] if len(df) >= 120 else df

    lows, highs = local_extrema_levels(recent, window=3)
    low_clusters = cluster_levels(lows, 0.012)
    high_clusters = cluster_levels(highs, 0.012)

    supports = [x for x in low_clusters if x["price"] < current]
    resistances = [x for x in high_clusters if x["price"] > current]

    # 이동평균도 보조 레벨로 추가
    for col in ["MA20", "MA60", "MA120"]:
        if col in df.columns and pd.notna(df[col].iloc[-1]):
            p = float(df[col].iloc[-1])
            if p < current:
                supports.append({"price": p, "strength": 2})
            elif p > current:
                resistances.append({"price": p, "strength": 2})

    # 최근 고점/저점
    recent20 = df.iloc[-20:]
    recent60 = df.iloc[-60:] if len(df) >= 60 else df

    for p in [float(recent20["Low"].min()), float(recent60["Low"].min())]:
        if p < current:
            supports.append({"price": p, "strength": 3})

    for p in [float(recent20["High"].max()), float(recent60["High"].max())]:
        if p > current:
            resistances.append({"price": p, "strength": 3})

    def dedup(levels):
        out = []
        for item in sorted(levels, key=lambda x: x["price"]):
            if not out or abs(item["price"] - out[-1]["price"]) / out[-1]["price"] > 0.012:
                out.append(item.copy())
            else:
                if item["strength"] > out[-1]["strength"]:
                    out[-1] = item.copy()
        return out

    supports = dedup(supports)
    resistances = dedup(resistances)

    supports = sorted(supports, key=lambda x: x["price"], reverse=True)[:3]
    resistances = sorted(resistances, key=lambda x: x["price"])[:3]

    return supports, resistances

# -----------------------------
# 거래량 매물대
# -----------------------------
def volume_profile(df, bins=24):
    data = df.iloc[-120:] if len(df) >= 120 else df
    low = float(data["Low"].min())
    high = float(data["High"].max())

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

def get_volume_zones(vp, current, n=3):
    if vp.empty:
        return [], []

    above = vp[vp["price"] > current].sort_values("price")
    below = vp[vp["price"] < current].sort_values("price", ascending=False)

    resist = above.sort_values("volume", ascending=False).head(n)
    support = below.sort_values("volume", ascending=False).head(n)

    return support["price"].tolist(), resist["price"].tolist()

# -----------------------------
# 기술점수 100점
# -----------------------------
def technical_score(df):
    x = df.iloc[-1]
    prev = df.iloc[-2]
    score = 0
    reasons = []

    close = float(x["Close"])
    ma5, ma20, ma60 = x["MA5"], x["MA20"], x["MA60"]
    rsi = x["RSI"]
    macd, sig, hist = x["MACD"], x["MACD_Signal"], x["MACD_Hist"]
    vol_ratio = x["Vol_Ratio"]

    # 25점: 추세
    trend = 0
    if pd.notna(ma5) and close > ma5: trend += 7
    if pd.notna(ma20) and close > ma20: trend += 8
    if pd.notna(ma60) and ma20 > ma60: trend += 5
    if pd.notna(ma5) and pd.notna(ma20) and ma5 > ma20: trend += 5
    score += trend

    # 15점: RSI
    rsi_score = 0
    if pd.notna(rsi):
        if 55 <= rsi < 68: rsi_score = 15
        elif 50 <= rsi < 55 or 68 <= rsi < 72: rsi_score = 12
        elif 40 <= rsi < 50: rsi_score = 8
        elif rsi >= 72: rsi_score = 5
        else: rsi_score = 3
    score += rsi_score

    # 15점: MACD
    macd_score = 0
    if pd.notna(macd) and pd.notna(sig):
        if macd > sig and hist > 0: macd_score = 15
        elif macd > sig: macd_score = 11
        elif hist > prev["MACD_Hist"]: macd_score = 7
        else: macd_score = 3
    score += macd_score

    # 15점: 거래량
    vol_score = 0
    if pd.notna(vol_ratio):
        if 1.2 <= vol_ratio <= 2.5 and close >= prev["Close"]: vol_score = 15
        elif vol_ratio >= 1.5 and close < prev["Close"]: vol_score = 4
        elif 0.8 <= vol_ratio < 1.5: vol_score = 10
        elif vol_ratio < 0.8: vol_score = 7
    score += vol_score

    # 10점: 볼린저
    bb_score = 0
    if pd.notna(x["BB_Upper"]) and pd.notna(x["BB_Lower"]):
        width = x["BB_Upper"] - x["BB_Lower"]
        if width > 0:
            pos = (close - x["BB_Lower"]) / width
            if 0.45 <= pos <= 0.75: bb_score = 10
            elif 0.25 <= pos < 0.45 or 0.75 < pos <= 0.90: bb_score = 8
            elif pos > 0.90: bb_score = 4
            else: bb_score = 6
    score += bb_score

    # 10점: 가격 위치/모멘텀
    location_score = 0
    ret5 = x["Return5"]
    if pd.notna(ret5):
        if 0 <= ret5 <= 5: location_score = 10
        elif ret5 > 8: location_score = 4
        elif ret5 < -5: location_score = 3
        else: location_score = 7
    score += location_score

    # 10점: 최근 모멘텀
    momentum_score = 0
    if pd.notna(x["Return20"]):
        if x["Return20"] > 10: momentum_score = 10
        elif x["Return20"] > 3: momentum_score = 8
        elif x["Return20"] >= 0: momentum_score = 6
        else: momentum_score = 3
    score += momentum_score

    score = int(max(0, min(100, score)))

    if score >= 80:
        label = "강한 상승"
    elif score >= 65:
        label = "상승 우위"
    elif score >= 45:
        label = "중립"
    elif score >= 30:
        label = "조정"
    else:
        label = "약세"

    return score, label

# -----------------------------
# 패턴/시나리오
# -----------------------------
def detect_patterns(df, supports, resistances, vp):
    x = df.iloc[-1]
    prev = df.iloc[-2]
    close = float(x["Close"])

    ma20 = x["MA20"]
    ma60 = x["MA60"]
    rsi = x["RSI"]
    macd = x["MACD"]
    sig = x["MACD_Signal"]
    hist = x["MACD_Hist"]
    vol = x["Vol_Ratio"]
    atr = x["ATR14"]

    recent20_high = float(df.iloc[-21:-1]["High"].max()) if len(df) >= 22 else float(df["High"].max())
    recent20_low = float(df.iloc[-21:-1]["Low"].min()) if len(df) >= 22 else float(df["Low"].min())

    patterns = []

    # 눌림목
    pullback = (
        pd.notna(ma20) and pd.notna(ma60) and pd.notna(rsi)
        and close >= ma20 * 0.985
        and close <= ma20 * 1.025
        and ma20 > ma60
        and 42 <= rsi <= 65
        and vol < 1.3
    )
    if pullback:
        patterns.append("눌림목 후보")

    # 저항 돌파
    breakout = (
        close > recent20_high
        and vol >= 1.3
        and pd.notna(macd) and macd > sig
    )
    if breakout:
        patterns.append("거래량 동반 돌파")

    # 돌파 실패
    false_breakout = (
        float(x["High"]) > recent20_high
        and close < recent20_high
        and vol >= 1.2
    )
    if false_breakout:
        patterns.append("돌파 실패 경계")

    # 추격 위험
    bb_width = x["BB_Upper"] - x["BB_Lower"]
    bb_pos = ((close - x["BB_Lower"]) / bb_width) if pd.notna(bb_width) and bb_width > 0 else 0.5
    chase = (
        pd.notna(rsi) and rsi >= 70
        and bb_pos >= 0.88
        and pd.notna(x["Return5"]) and x["Return5"] >= 6
    )
    if chase:
        patterns.append("단기 추격 위험")

    # 추세 훼손
    breakdown = (
        pd.notna(ma20) and pd.notna(ma60)
        and close < ma20
        and ma20 < ma60
        and macd < sig
    )
    if breakdown:
        patterns.append("추세 훼손")

    # 지지 이탈
    support_break = (
        bool(supports)
        and close < supports[0]["price"] * 0.99
        and vol >= 1.2
    )
    if support_break:
        patterns.append("지지선 이탈")

    if not patterns:
        if close > ma20 and ma20 > ma60:
            patterns.append("상승 추세 유지")
        elif close > ma20:
            patterns.append("단기 우상향")
        else:
            patterns.append("관망/조정")

    return patterns

def scenario_text(df, score, supports, resistances, patterns):
    x = df.iloc[-1]
    close = float(x["Close"])
    rsi = float(x["RSI"]) if pd.notna(x["RSI"]) else 50
    vol = float(x["Vol_Ratio"]) if pd.notna(x["Vol_Ratio"]) else 1
    ma20 = float(x["MA20"]) if pd.notna(x["MA20"]) else close
    ma60 = float(x["MA60"]) if pd.notna(x["MA60"]) else close

    s1 = supports[0]["price"] if supports else ma20
    s2 = supports[1]["price"] if len(supports) > 1 else ma60
    r1 = resistances[0]["price"] if resistances else close * 1.03
    r2 = resistances[1]["price"] if len(resistances) > 1 else close * 1.06

    if "단기 추격 위험" in patterns:
        title = "🟠 과열 구간 — 추격보다 눌림 확인"
        body = f"RSI {rsi:.1f}, 단기 상승폭과 밴드 위치가 높습니다. {s1:,.0f}원 부근 지지 여부와 거래량 둔화를 확인하는 시나리오입니다."
    elif "거래량 동반 돌파" in patterns:
        title = "🟢 돌파 시나리오"
        body = f"최근 저항을 종가 기준으로 넘어섰고 거래량이 {vol:.2f}배입니다. 돌파 가격을 다시 지지하는지 확인하면서 {r2:,.0f}원대까지 다음 저항을 관찰합니다."
    elif "돌파 실패 경계" in patterns:
        title = "🟠 돌파 실패 경계"
        body = f"장중 저항을 넘었지만 종가가 되돌아왔습니다. {r1:,.0f}원 회복 여부와 거래량을 확인하고, {s1:,.0f}원 지지 여부를 함께 봅니다."
    elif "눌림목 후보" in patterns:
        title = "🟢 상승 추세 속 눌림목 후보"
        body = f"20일선 {ma20:,.0f}원 부근에서 조정받는 구조입니다. 거래량이 과도하게 증가하지 않는 가운데 지지 후 RSI/MACD 반등 여부를 확인합니다."
    elif "지지선 이탈" in patterns or "추세 훼손" in patterns:
        title = "🔴 추세 훼손/관망"
        body = f"주요 지지와 중기 추세가 약해진 상태입니다. {s2:,.0f}원 부근 회복과 거래량 감소 여부를 먼저 확인하는 시나리오입니다."
    elif score >= 65:
        title = "🟢 상승 추세 유지"
        body = f"현재 기술점수 {score}/100입니다. {s1:,.0f}원 지지와 {r1:,.0f}원 저항을 기준으로 추세 지속 여부를 관찰합니다."
    else:
        title = "🔵 중립/조정 구간"
        body = f"현재 기술점수 {score}/100입니다. {s1:,.0f}원 지지와 {r1:,.0f}원 저항 중 어느 쪽을 이탈·돌파하는지가 다음 방향의 핵심입니다."

    return title, body, s1, s2, r1, r2

# -----------------------------
# 차트
# -----------------------------
def make_chart(df, supports, resistances, vp):
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        vertical_spacing=0.025,
        row_heights=[0.50, 0.16, 0.17, 0.17]
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"], name="주가"
        ), row=1, col=1
    )

    line_defs = [
        ("MA5", "yellow"), ("MA20", "orange"),
        ("MA60", "green"), ("MA120", "purple")
    ]
    for col, color in line_defs:
        if col in df:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df[col],
                    line=dict(color=color, width=1),
                    name=col
                ), row=1, col=1
            )

    fig.add_trace(
        go.Scatter(x=df.index, y=df["BB_Upper"],
                   line=dict(color="gray", dash="dot"), name="BB Upper"),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["BB_Lower"],
                   line=dict(color="gray", dash="dot"), name="BB Lower"),
        row=1, col=1
    )

    # 지지/저항선
    for i, item in enumerate(supports[:3]):
        fig.add_hline(
            y=item["price"], row=1, col=1,
            line_dash="dot", line_width=1,
            annotation_text=f"S{i+1} {item['price']:,.0f}",
            annotation_position="bottom left"
        )

    for i, item in enumerate(resistances[:3]):
        fig.add_hline(
            y=item["price"], row=1, col=1,
            line_dash="dash", line_width=1,
            annotation_text=f"R{i+1} {item['price']:,.0f}",
            annotation_position="top left"
        )

    vol_colors = ["red" if c >= o else "blue" for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(
        go.Bar(x=df.index, y=df["Volume"], marker_color=vol_colors, name="Volume"),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(x=df.index, y=df["RSI"],
                   line=dict(color="white", width=1.5), name="RSI"),
        row=3, col=1
    )
    fig.add_hline(y=70, row=3, col=1, line_dash="dot")
    fig.add_hline(y=30, row=3, col=1, line_dash="dot")

    fig.add_trace(
        go.Bar(x=df.index, y=df["MACD_Hist"], name="MACD Hist"),
        row=4, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["MACD"],
                   line=dict(color="blue"), name="MACD"),
        row=4, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["MACD_Signal"],
                   line=dict(color="red"), name="Signal"),
        row=4, col=1
    )

    fig.update_layout(
        height=720,
        margin=dict(l=5, r=5, t=5, b=5),
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        showlegend=False,
        dragmode=False
    )

    fig.update_yaxes(fixedrange=True)
    return fig

# ============================================================
# UI
# ============================================================
st.title("📈 ETF Technical Radar")
st.caption("기술적 조건을 종합해 현재 추세·지지/저항·눌림·돌파 상황을 보여줍니다.")

watchlist = st.session_state.watchlist
options = list(watchlist.values()) + ["➕ 종목코드로 관심종목 추가"]

c1, c2 = st.columns([2.1, 1])
with c1:
    selected = st.selectbox("⭐ 관심 ETF", options)
with c2:
    period = st.selectbox("분석기간", ["6m", "1y", "2y"], index=1)

if selected == "➕ 종목코드로 관심종목 추가":
    st.subheader("종목코드 등록")
    a, b = st.columns([2, 1])
    with a:
        new_code = st.text_input("종목코드", placeholder="예: 395160", label_visibility="collapsed")
    with b:
        add = st.button("⭐ 추가", use_container_width=True)

    if add and new_code:
        code = "".join(filter(str.isdigit, new_code))
        test_df, _ = load_etf_data(code, "6m")
        if test_df is not None:
            name = get_stock_name(code)
            st.session_state.watchlist[code] = f"{name} ({code})"
            save_watchlist(st.session_state.watchlist)
            st.success(f"{name} ({code}) 등록 완료")
            st.rerun()
        else:
            st.error("데이터를 가져올 수 없는 종목코드입니다.")
    st.stop()

symbol_input = next(k for k, v in watchlist.items() if v == selected)

delete_col, _ = st.columns([1, 3])
with delete_col:
    if st.button("🗑 삭제", use_container_width=True):
        del st.session_state.watchlist[symbol_input]
        save_watchlist(st.session_state.watchlist)
        st.rerun()

with st.spinner("ETF 기술적 분석 중..."):
    raw_df, code = load_etf_data(symbol_input, period)

if raw_df is None:
    st.error(f"데이터를 불러오지 못했습니다. 종목코드 {symbol_input}을 확인해주세요.")
    st.stop()

df = calculate_indicators(raw_df)

# 최소 데이터 확보
df = df.dropna(subset=["Close"]).copy()

score, score_label = technical_score(df)
supports, resistances = get_support_resistance(df)
vp = volume_profile(df)
vp_support, vp_resist = get_volume_zones(vp, float(df["Close"].iloc[-1]))

patterns = detect_patterns(df, supports, resistances, vp)
scenario_title, scenario_body, s1, s2, r1, r2 = scenario_text(
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

# ============================================================
# 모바일 핵심 카드
# ============================================================
st.markdown("### 현재 상태")

m1, m2 = st.columns(2)
with m1:
    st.metric("현재가", f"{price:,.0f}원", f"{change:+.2f}%")
with m2:
    st.metric("기술점수", f"{score}/100", score_label)

m3, m4, m5 = st.columns(3)
with m3:
    st.metric("RSI", f"{rsi:.1f}")
with m4:
    st.metric("거래량", f"{vol_ratio:.2f}x")
with m5:
    st.metric("MACD", "상승" if macd > macd_sig else "하락")

pattern_text = " · ".join(patterns)
st.markdown(
    f'<div class="radar-card"><b>🎯 현재 시그널</b><br>'
    f'<span style="font-size:1.05rem">{pattern_text}</span></div>',
    unsafe_allow_html=True
)

# 가격대
st.markdown("### 📍 핵심 가격대")

p1, p2, p3 = st.columns(3)
with p1:
    st.markdown(f"**🟢 S2**<br>{s2:,.0f}원", unsafe_allow_html=True)
with p2:
    st.markdown(f"**🟡 현재**<br>{price:,.0f}원", unsafe_allow_html=True)
with p3:
    st.markdown(f"**🔴 R1**<br>{r1:,.0f}원", unsafe_allow_html=True)

st.markdown(
    f'<div class="price-zone">🟢 <b>1차 지지</b> {s1:,.0f}원 '
    f'　→　🟢 <b>2차 지지</b> {s2:,.0f}원</div>'
    f'<div class="price-zone">🔴 <b>1차 저항</b> {r1:,.0f}원 '
    f'　→　🔴 <b>2차 저항</b> {r2:,.0f}원</div>',
    unsafe_allow_html=True
)

st.markdown("### 🎯 분석 시나리오")
if scenario_title.startswith("🟢"):
    st.success(f"**{scenario_title}**\n\n{scenario_body}")
elif scenario_title.startswith("🟠"):
    st.warning(f"**{scenario_title}**\n\n{scenario_body}")
elif scenario_title.startswith("🔴"):
    st.error(f"**{scenario_title}**\n\n{scenario_body}")
else:
    st.info(f"**{scenario_title}**\n\n{scenario_body}")

tab_chart, tab_zones, tab_score, tab_detail = st.tabs(
    ["📊 차트", "📍 지지/저항", "💯 점수", "🔍 지표"]
)

with tab_chart:
    st.caption("가격 / 이동평균 / 거래량 / RSI / MACD")
    fig = make_chart(df, supports, resistances, vp)
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "responsive": True,
            "scrollZoom": False,
            "displayModeBar": False,
            "doubleClick": False
        },
        key=f"chart_{symbol_input}_{period}"
    )

with tab_zones:
    st.subheader("자동 지지/저항")
    if supports:
        for i, item in enumerate(supports[:3], 1):
            st.success(f"S{i}  {item['price']:,.0f}원  · 강도 {item['strength']}")
    else:
        st.info("확인 가능한 지지 레벨이 부족합니다.")

    if resistances:
        for i, item in enumerate(resistances[:3], 1):
            st.warning(f"R{i}  {item['price']:,.0f}원  · 강도 {item['strength']}")
    else:
        st.info("확인 가능한 저항 레벨이 부족합니다.")

    st.subheader("거래량 매물대")
    if not vp.empty:
        vp_show = vp.head(5)[["price", "volume", "ratio"]].copy()
        vp_show["가격"] = vp_show["price"].map(lambda x: f"{x:,.0f}원")
        vp_show["거래량 비중"] = vp_show["ratio"].map(lambda x: f"{x*100:.0f}%")
        st.dataframe(
            vp_show[["가격", "거래량 비중"]],
            use_container_width=True,
            hide_index=True
        )

with tab_score:
    st.subheader(f"기술점수 {score}/100")
    st.progress(score / 100)
    st.markdown(f"### {score_label}")

    score_table = pd.DataFrame({
        "항목": ["추세", "RSI", "MACD", "거래량", "볼린저", "가격위치", "20일 모멘텀"],
        "배점": [25, 15, 15, 15, 10, 10, 10]
    })
    st.table(score_table)

    st.caption(
        "점수는 현재 기술적 조건을 수치화한 참고 지표이며, 미래 수익이나 투자 결과를 보장하지 않습니다."
    )

with tab_detail:
    bb_width = float(x["BB_Upper"] - x["BB_Lower"]) if pd.notna(x["BB_Upper"]) and pd.notna(x["BB_Lower"]) else 0
    bb_pos = ((price - float(x["BB_Lower"])) / bb_width * 100) if bb_width > 0 else 50

    details = pd.DataFrame({
        "지표": [
            "이동평균",
            "RSI(14)",
            "MACD",
            "볼린저밴드",
            "거래량",
            "5일 수익률",
            "20일 수익률"
        ],
        "현재값": [
            f"MA5 {x['MA5']:,.0f} / MA20 {x['MA20']:,.0f} / MA60 {x['MA60']:,.0f}",
            f"{rsi:.1f}",
            f"{macd:+.2f} / Signal {macd_sig:+.2f}",
            f"{bb_pos:.0f}% 위치",
            f"{vol_ratio:.2f}x",
            f"{x['Return5']:+.2f}%",
            f"{x['Return20']:+.2f}%"
        ]
    })
    st.dataframe(details, use_container_width=True, hide_index=True)

    st.markdown("### 패턴 감지")
    for p in patterns:
        st.write(f"• {p}")

st.caption("ETF Technical Radar · 기술적 분석 참고용")
