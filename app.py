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
# ETF Technical Radar v3 (밝은 라이트 테마 적용)
# ============================================================

st.set_page_config(
    page_title="ETF Technical Radar",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 🎨 시각적 가독성 개선 CSS (밝고 화사한 라이트 모드 테마)
st.markdown("""
<style>
.stApp {max-width: 1000px; margin: 0 auto; background-color: #f8fafc;}
.block-container {padding-top: 1rem; padding-bottom: 2rem; padding-left: .8rem; padding-right: .8rem;}

/* 밝은 고대비 카드 및 글자색 설정 */
div[data-testid="stMetric"] {
    background: #ffffff; 
    border: 1px solid #e2e8f0; 
    border-radius: 10px; 
    padding: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
div[data-testid="stMetricLabel"] {
    color: #475569 !important; /* 명확한 다크 회색 */
    font-size: 0.95rem !important;
    font-weight: 600;
}
div[data-testid="stMetricValue"] {
    color: #0f172a !important; /* 선명한 다크 슬레이트 */
    font-weight: 700;
}

.radar-card {
    background: #ffffff; 
    border: 1px solid #e2e8f0; 
    border-radius: 12px;
    padding: 16px; 
    margin-bottom: 12px;
    color: #0f172a;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* 텍스트 가독성 강화 */
.text-bright {color: #0f172a !important; font-size: 0.95rem; line-height: 1.5;}
.text-sub {color: #475569 !important; font-size: 0.88rem;}
.highlight-green {color: #16a34a; font-weight: bold;}
.highlight-red {color: #dc2626; font-weight: bold;}
.highlight-yellow {color: #d97706; font-weight: bold;}

.price-zone {
    border-radius: 10px; 
    padding: 12px; 
    margin: 6px 0;
    border: 1px solid #e2e8f0; 
    background: #ffffff;
    color: #0f172a;
    font-size: 0.95rem;
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

WATCHLIST_FILE = "watchlist.json"
DEFAULT_WATCHLIST = {
    "395160": "KODEX AI반도체TOP2플러스 (395160)",
    "487240": "KODEX 미국AI테크TOP10 (487240)",
    "471990": "KODEX AI전력핵심설비 (471990)",
    "0173Y0": "KODEX 미국AI광통신네트워크 (0173Y0)",
    "133690": "TIGER 미국나스닥100 (133690)",
    "360750": "TIGER 미국S&P500 (360750)"
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

    for col in ["MA20", "MA60", "MA120"]:
        if col in df.columns and pd.notna(df[col].iloc[-1]):
            p = float(df[col].iloc[-1])
            if p < current:
                supports.append({"price": p, "strength": 2})
            elif p > current:
                resistances.append({"price": p, "strength": 2})

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

# -----------------------------
# 기술점수 계산
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

    # 추세 (25점)
    if pd.notna(ma5) and close > ma5: score += 7
    if pd.notna(ma20) and close > ma20: score += 8
    if pd.notna(ma60) and ma20 > ma60: score += 5
    if pd.notna(ma5) and pd.notna(ma20) and ma5 > ma20: score += 5

    # RSI (15점)
    if pd.notna(rsi):
        if 55 <= rsi < 68: score += 15
        elif 50 <= rsi < 55 or 68 <= rsi < 72: score += 12
        elif 40 <= rsi < 50: score += 8
        elif rsi >= 72: score += 5
        else: score += 3

    # MACD (15점)
    if pd.notna(macd) and pd.notna(sig):
        if macd > sig and hist > 0: score += 15
        elif macd > sig: score += 11
        elif hist > prev["MACD_Hist"]: score += 7
        else: score += 3

    # 거래량 (15점)
    if pd.notna(vol_ratio):
        if 1.2 <= vol_ratio <= 2.5 and close >= prev["Close"]: score += 15
        elif vol_ratio >= 1.5 and close < prev["Close"]: score += 4
        elif 0.8 <= vol_ratio < 1.5: score += 10
        elif vol_ratio < 0.8: score += 7

    # 볼린저 (10점)
    if pd.notna(x["BB_Upper"]) and pd.notna(x["BB_Lower"]):
        width = x["BB_Upper"] - x["BB_Lower"]
        if width > 0:
            pos = (close - x["BB_Lower"]) / width
            if 0.45 <= pos <= 0.75: score += 10
            elif 0.25 <= pos < 0.45 or 0.75 < pos <= 0.90: score += 8
            elif pos > 0.90: score += 4
            else: score += 6

    # 모멘텀 (20점)
    ret5 = x["Return5"]
    if pd.notna(ret5):
        if 0 <= ret5 <= 5: score += 10
        elif ret5 > 8: score += 4
        elif ret5 < -5: score += 3
        else: score += 7

    if pd.notna(x["Return20"]):
        if x["Return20"] > 10: score += 10
        elif x["Return20"] > 3: score += 8
        elif x["Return20"] >= 0: score += 6
        else: score += 3

    score = int(max(0, min(100, score)))

    if score >= 80: label = "강한 상승세"
    elif score >= 65: label = "상승 우세"
    elif score >= 45: label = "중립/관망"
    elif score >= 30: label = "조정 국면"
    else: label = "약세/하락 위험"

    return score, label

def detect_patterns(df, supports, resistances):
    x = df.iloc[-1]
    close = float(x["Close"])
    ma20 = x["MA20"]
    ma60 = x["MA60"]
    rsi = x["RSI"]
    macd = x["MACD"]
    sig = x["MACD_Signal"]
    vol = x["Vol_Ratio"]

    recent20_high = float(df.iloc[-21:-1]["High"].max()) if len(df) >= 22 else float(df["High"].max())
    patterns = []

    # 눌림목
    if pd.notna(ma20) and pd.notna(ma60) and pd.notna(rsi):
        if close >= ma20 * 0.985 and close <= ma20 * 1.025 and ma20 > ma60 and 42 <= rsi <= 65 and vol < 1.3:
            patterns.append("💡 눌림목 매수 적기")

    # 강한 돌파
    if close > recent20_high and vol >= 1.3 and pd.notna(macd) and macd > sig:
        patterns.append("🚀 강력한 저항선 돌파")

    # 추격 위험
    bb_width = x["BB_Upper"] - x["BB_Lower"]
    bb_pos = ((close - x["BB_Lower"]) / bb_width) if pd.notna(bb_width) and bb_width > 0 else 0.5
    if pd.notna(rsi) and rsi >= 70 and bb_pos >= 0.88:
        patterns.append("⚠️ 단기 과열 (추격매수 위험)")

    # 추세 훼손/이탈
    if pd.notna(ma20) and close < ma20 and macd < sig:
        patterns.append("🔻 단기 추세 약화")

    if not patterns:
        if close > ma20: patterns.append("📈 차분한 우상향 흐름")
        else: patterns.append("💤 횡보/관망 구간")

    return patterns

# -----------------------------
# 명확하고 쉬운 매매 안내 생성기
# -----------------------------
def easy_action_scenario(df, score, supports, resistances, patterns):
    x = df.iloc[-1]
    close = float(x["Close"])
    rsi = float(x["RSI"]) if pd.notna(x["RSI"]) else 50
    ma20 = float(x["MA20"]) if pd.notna(x["MA20"]) else close

    s1 = supports[0]["price"] if supports else ma20
    s2 = supports[1]["price"] if len(supports) > 1 else ma20 * 0.97
    r1 = resistances[0]["price"] if resistances else close * 1.03
    r2 = resistances[1]["price"] if len(resistances) > 1 else close * 1.06

    buy_guide = ""
    sell_guide = ""
    wait_guide = ""

    if "⚠️ 단기 과열 (추격매수 위험)" in patterns:
        status_title = "🟠 과열 구간 : 지금 바로 사지 말고 기다리세요!"
        buy_guide = f"**지금 매수는 위험합니다.** 주가가 단기 폭등하여 RSI가 {rsi:.0f}로 과열되었습니다. 주가가 **{s1:,.0f}원 부근**까지 내려와서 숨고르기를 할 때 분할 매수로 접근하세요."
        sell_guide = f"기존 보유자라면 **{r1:,.0f}원~{r2:,.0f}원 매물대 구간**에서 이익을 일부 실현(팔아서 현금화)하기 좋은 위치입니다."
        wait_guide = f"**{s1:,.0f}원 지지선**이 무너지면 조정이 길어질 수 있으니 섣부른 추격 매수는 금물입니다."

    elif "🚀 강력한 저항선 돌파" in patterns:
        status_title = "🟢 강력한 저항 돌파 : 추가 상승 가능성이 높은 구간!"
        buy_guide = f"위쪽 매물대를 거래량을 싣고 뚫어냈습니다! **현재 가격대 또는 {r1:,.0f}원 부근**으로 잠시 밀릴 때(돌파 후 지지) 매수 타이밍으로 잡을 수 있습니다."
        sell_guide = f"다음 강한 저항선인 **{r2:,.0f}원 부근**까지 추가 상승을 노려보세요."
        wait_guide = f"만약 다시 밀려 **{s1:,.0f}원 아래로 종가가 떨어지면** '가짜 돌파'일 수 있으니 손절/관망이 필요합니다."

    elif "💡 눌림목 매수 적기" in patterns:
        status_title = "🟢 눌림목 기회 : 차분히 모아가기 좋은 매수 타이밍!"
        buy_guide = f"상승 추세 중에 잠시 쉬어가는 구간입니다. 20일 이동평균선 근처인 **{s1:,.0f}원~{close:,.0f}원 사이**는 매수하기에 매우 매력적인 가격대입니다."
        sell_guide = f"상승 전환 시 전고점 및 저항대인 **{r1:,.0f}원**을 1차 목표가로 잡고 대응하세요."
        wait_guide = f"주요 지지선인 **{s2:,.0f}원**을 하향 이탈하면 추세가 꺾일 수 있으니 이때는 손절(매도)로 대응하세요."

    elif "🔻 단기 추세 약화" in patterns or score < 45:
        status_title = "🔴 추세 약화 : 무리한 매수 금지, 관망이 필요한 때!"
        buy_guide = f"지금은 힘이 빠지는 구간입니다. **매수를 멈추고 관망**하는 것이 안전합니다."
        sell_guide = f"보유 중이라면 **{r1:,.0f}원** 근처로 반등할 때 비중을 줄이거나 팔아서 현금을 확보하세요."
        wait_guide = f"하방 지지선인 **{s1:,.0f}원 및 {s2:,.0f}원**에서 주가가 멈추고 반등 신호가 나올 때까지 기다려야 합니다."

    else:
        status_title = "🔵 중립 흐름 : 뚜렷한 방향성을 찾는 중"
        buy_guide = f"안전하게 사려면 주가가 **{s1:,.0f}원 지지선**까지 내려오거나, 반대로 **{r1:,.0f}원 저항선**을 확실하게 뚫어줄 때 매수하세요."
        sell_guide = f"상승 시 **{r1:,.0f}원 부근**에 매물(팔려는 물량)이 몰려있으니 이 가격대에 오면 익절을 고려하세요."
        wait_guide = f"{s1:,.0f}원~{r1:,.0f}원 박스권 안에서 주가가 어느 방향으로 튈지 지켜보는 구간입니다."

    return status_title, buy_guide, sell_guide, wait_guide, s1, s2, r1, r2

# -----------------------------
# 차트 생성 (라이트 모드 고대비 설정)
# -----------------------------
def make_chart(df, supports, resistances):
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.50, 0.16, 0.17, 0.17]
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"], name="주가"
        ), row=1, col=1
    )

    line_defs = [
        ("MA5", "#d97706"), ("MA20", "#ea580c"),
        ("MA60", "#16a34a"), ("MA120", "#7c3aed")
    ]
    for col, color in line_defs:
        if col in df:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df[col],
                    line=dict(color=color, width=1.4),
                    name=col
                ), row=1, col=1
            )

    # 지지/저항 표시 (라이트 테마 대비 보정)
    for i, item in enumerate(supports[:2]):
        fig.add_hline(
            y=item["price"], row=1, col=1,
            line_dash="dot", line_color="#16a34a", line_width=1.5,
            annotation_text=f"지지 S{i+1} ({item['price']:,.0f}원)",
            annotation_position="bottom left",
            annotation_font_color="#16a34a"
        )

    for i, item in enumerate(resistances[:2]):
        fig.add_hline(
            y=item["price"], row=1, col=1,
            line_dash="dash", line_color="#dc2626", line_width=1.5,
            annotation_text=f"저항 R{i+1} ({item['price']:,.0f}원)",
            annotation_position="top left",
            annotation_font_color="#dc2626"
        )

    vol_colors = ["#dc2626" if c >= o else "#2563eb" for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(
        go.Bar(x=df.index, y=df["Volume"], marker_color=vol_colors, name="거래량"),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(x=df.index, y=df["RSI"], line=dict(color="#2563eb", width=1.5), name="RSI"),
        row=3, col=1
    )
    fig.add_hline(y=70, row=3, col=1, line_dash="dot", line_color="#dc2626")
    fig.add_hline(y=30, row=3, col=1, line_dash="dot", line_color="#16a34a")

    fig.add_trace(
        go.Bar(x=df.index, y=df["MACD_Hist"], name="MACD 히스토그램"),
        row=4, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["MACD"], line=dict(color="#2563eb"), name="MACD"),
        row=4, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["MACD_Signal"], line=dict(color="#dc2626"), name="Signal"),
        row=4, col=1
    )

    fig.update_layout(
        height=700,
        margin=dict(l=5, r=5, t=10, b=5),
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        showlegend=False,
        dragmode=False
    )

    fig.update_yaxes(fixedrange=True)
    return fig

# ============================================================
# UI 메인 화면
# ============================================================
st.title("📈 ETF 매매 레이더 (쉬운 매매 안내)")

watchlist = st.session_state.watchlist
options = list(watchlist.values()) + ["➕ 종목코드로 관심종목 추가"]

c1, c2 = st.columns([2.1, 1])
with c1:
    selected = st.selectbox("⭐ 관심 ETF 선택", options)
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
    if st.button("🗑 목록에서 삭제", use_container_width=True):
        del st.session_state.watchlist[symbol_input]
        save_watchlist(st.session_state.watchlist)
        st.rerun()

with st.spinner("최신 데이터 및 매매 신호 분석 중..."):
    raw_df, code = load_etf_data(symbol_input, period)

if raw_df is None:
    st.error(f"데이터를 불러오지 못했습니다. 종목코드 {symbol_input}을 확인해주세요.")
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
# 1. 핵심 요약 카드
# -----------------------------
st.markdown("### 📊 현재 주가 및 종합 점수")

m1, m2 = st.columns(2)
with m1:
    st.metric("현재가", f"{price:,.0f}원", f"{change:+.2f}%")
with m2:
    st.metric("종합 점수", f"{score}점 / 100점", score_label)

pattern_text = " · ".join(patterns)
st.markdown(
    f'<div class="radar-card">'
    f'<b style="font-size:1.05rem; color:#b45309;">🎯 핵심 신호: {pattern_text}</b>'
    f'</div>',
    unsafe_allow_html=True
)

# -----------------------------
# 2. 명확한 매매 안내 (사용자 요청 핵심!)
# -----------------------------
st.markdown("### 💡 쉽게 풀어쓴 매매 대응 전략")

if "🟢" in status_title:
    st.success(f"### {status_title}")
elif "🔴" in status_title:
    st.error(f"### {status_title}")
elif "🟠" in status_title:
    st.warning(f"### {status_title}")
else:
    st.info(f"### {status_title}")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(
        f'<div class="price-zone">'
        f'<b class="highlight-green">🛒 언제 사나요? (매수 전략)</b><br>{buy_guide}'
        f'</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="price-zone">'
        f'<b class="highlight-red">💰 어디서 파나요? (익절/매도)</b><br>{sell_guide}'
        f'</div>',
        unsafe_allow_html=True
    )

with col_b:
    st.markdown(
        f'<div class="price-zone">'
        f'<b class="highlight-yellow">🛑 어디서 손절/관망 하나요?</b><br>{wait_guide}'
        f'</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="price-zone">'
        f'<b>📍 핵심 가격 요약</b><br>'
        f'• <b>2차 저항 (최종 목표)</b>: <span class="highlight-red">{r2:,.0f}원</span><br>'
        f'• <b>1차 저항 (매물대/벽)</b>: <span class="highlight-red">{r1:,.0f}원</span><br>'
        f'• <b>현재 가격</b>: <b>{price:,.0f}원</b><br>'
        f'• <b>1차 지지 (1차 바닥)</b>: <span class="highlight-green">{s1:,.0f}원</span><br>'
        f'• <b>2차 지지 (손절 마지노선)</b>: <span class="highlight-green">{s2:,.0f}원</span>'
        f'</div>',
        unsafe_allow_html=True
    )

# -----------------------------
# 3. 탭별 상세 내용 (차트, 지지저항, 지표 설명서)
# -----------------------------
tab_chart, tab_zones, tab_guide = st.tabs(
    ["📊 차트 보기", "📍 매물대 & 지지/저항", "📖 보조지표 쉬운 설명서"]
)

with tab_chart:
    st.caption("캔들차트 / 이동평균선 / 거래량 / RSI / MACD")
    fig = make_chart(df, supports, resistances)
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"responsive": True, "displayModeBar": False},
        key=f"chart_{symbol_input}_{period}"
    )

with tab_zones:
    st.subheader("📍 지지선과 저항선이란?")
    st.markdown("""
    - **저항선 (R)**: 매물(물린 사람들의 팔려는 물량)이 몰려있어서 **주가가 올라가다 막히는 벽**입니다. 뚫으면 급등하지만, 못 뚫으면 밀립니다.
    - **지지선 (S)**: 살려는 사람들의 대기 물량이 많아 **주가가 떨어지다 튕겨 올라가는 바닥**입니다. 깨지면 추가 하락합니다.
    """)

    col_s, col_r = st.columns(2)
    with col_s:
        st.markdown("**🟢 아래를 받쳐주는 지지 가격 (바닥)**")
        if supports:
            for i, item in enumerate(supports[:3], 1):
                st.success(f"S{i} 지지선: **{item['price']:,.0f}원** (신뢰도: {item['strength']})")
        else:
            st.info("지점 데이터 부족")

    with col_r:
        st.markdown("**🔴 위를 막고 있는 저항 가격 (벽)**")
        if resistances:
            for i, item in enumerate(resistances[:3], 1):
                st.warning(f"R{i} 저항선: **{item['price']:,.0f}원** (신뢰도: {item['strength']})")
        else:
            st.info("지점 데이터 부족")

    st.subheader("🧱 매물대 분포 (거래가 가장 많이 터진 구간)")
    if not vp.empty:
        vp_show = vp.head(5)[["price", "volume", "ratio"]].copy()
        vp_show["가격대"] = vp_show["price"].map(lambda x: f"{x:,.0f}원 부근")
        vp_show["매물 집중도"] = vp_show["ratio"].map(lambda x: f"{x*100:.0f}%")
        st.dataframe(
            vp_show[["가격대", "매물 집중도"]],
            use_container_width=True,
            hide_index=True
        )

with tab_guide:
    st.subheader("❓ 각종 보조지표, 어쩌라는 건가요? (초보자 해설)")

    st.markdown(f"""
    #### 1. RSI (상대강도지수) : 현재 값 **{rsi:.1f}**
    - **의미**: 주가가 너무 과열되었는지, 아니면 너무 소외되어 싸졌는지 나타냅니다.
    - **해석 방법**:
        - **70 이상**: <span class="highlight-red">과열 상태</span> (남들이 다 산 상태, 지금 사면 상투 잡을 위험 높음!)
        - **30 이하**: <span class="highlight-green">침체 상태</span> (너무 많이 빠진 상태, 반등 기대 매수 구간)
        - **50 부근**: 정상적인 흐름

    #### 2. MACD (추세 방향) : 현재 **{"상승 우세" if macd > macd_sig else "하락/조정 우세"}**
    - **의미**: 주가의 단기 방향성과 에너지를 알려줍니다.
    - **해석 방법**:
        - **파란선이 빨간선 위로 올라탈 때**: <span class="highlight-green">상승 신호 (매수 고려)</span>
        - **파란선이 빨간선 아래로 꺾일 때**: <span class="highlight-red">하락 신호 (매도/관망 고려)</span>

    #### 3. 거래량 비율 : 평소의 **{vol_ratio:.2f}배**
    - **의미**: 주가 움직임이 '진짜'인지 '가짜'인지 판가름합니다.
    - **해석 방법**:
        - **저항선을 뚫을 때 거래량이 1.5~2배 이상 터지면**: <span class="highlight-green">진짜 폭등 시작!</span>
        - **거래량 없이 슬금슬금 오르면**: 언제든 다시 무너질 수 있는 약한 상승.

    #### 4. 이동평균선 (MA)
    - **20일선 (주황색)**: 생명선입니다. 주가가 20일선 위에 있어야 안전한 상승장입니다.
    """, unsafe_allow_html=True)

st.caption("ETF Technical Radar · 라이트 테마 가독성 강화 버전")
