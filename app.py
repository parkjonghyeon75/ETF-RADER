import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os

# 1. 모바일 최적화 페이지 설정
st.set_page_config(
    page_title="ETF Technical Radar",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS (모바일 가독성 증대)
st.markdown("""
<style>
    .stApp { max-width: 1000px; margin: 0 auto; }
    .metric-card {
        background-color: #1e222d;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        border: 1px solid #2a2e39;
    }
</style>
""", unsafe_allow_html=True)

# 2. 관심종목 파일 저장/불러오기 기능 (영구 보존)
WATCHLIST_FILE = "watchlist.json"
DEFAULT_WATCHLIST = {
    "069500": "KODEX 200 (069500)",
    "091160": "KODEX 반도체 (091160)",
    "466920": "KODEX AI반도체핵심장비 (466920)",
    "379800": "KODEX 미국S&P500 (379800)",
    "305540": "TIGER 2차전지테마 (305540)"
}

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_WATCHLIST.copy()
    return DEFAULT_WATCHLIST.copy()

def save_watchlist(data):
    try:
        with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"저장 실패: {e}")

if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()

# 3. 보조지표 계산 함수
def calculate_indicators(df):
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA60'] = df['Close'].rolling(60).mean()
    df['MA120'] = df['Close'].rolling(120).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    df['BB_Mid'] = df['MA20']
    std = df['Close'].rolling(20).std()
    df['BB_Upper'] = df['BB_Mid'] + (std * 2)
    df['BB_Lower'] = df['BB_Mid'] - (std * 2)
    
    df['Vol_MA20'] = df['Volume'].rolling(20).mean()
    return df

# 4. 데이터 로드 (캐싱을 통해 차트 로딩 속도 최적화)
@st.cache_data(ttl=300, show_spinner=False)
def load_etf_data(ticker_code, period="1y"):
    ticker = ticker_code.strip().upper()
    if not (ticker.endswith(".KS") or ticker.endswith(".KQ")):
        ticker = f"{ticker}.KS"
    
    data = yf.download(ticker, period=period, progress=False)
    if data.empty or len(data) < 30:
        return None, ticker
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
        
    df = calculate_indicators(data)
    return df, ticker

# UI 헤더
st.title("📈 ETF Technical Radar")

# 5. 관심종목 선택 및 관리
watchlist = st.session_state.watchlist
preset_options = [f"{v}" for k, v in watchlist.items()] + ["➕ 종목코드로 관심종목 추가"]

col_sel, col_pd = st.columns([2, 1])
with col_sel:
    selected_option = st.selectbox("⭐ 관심 ETF 선택", preset_options)
with col_pd:
    period = st.selectbox("기간", ["6m", "1y", "2y"], index=1)

# 종목코드로 관심종목 신규 등록
if selected_option == "➕ 종목코드로 관심종목 추가":
    st.subheader("📝 종목코드 입력 등록")
    col_code, col_btn = st.columns([2, 1])
    
    with col_code:
        new_code = st.text_input("종목코드 입력", placeholder="예: 466920", label_visibility="collapsed")
    with col_btn:
        add_btn = st.button("⭐ 추가", use_container_width=True)
        
    if add_btn and new_code:
        clean_code = new_code.strip().upper()
        # 데이터 유효성 검증
        test_df, full_code = load_etf_data(clean_code, period="1mo")
        if test_df is not None:
            display_label = f"ETF {clean_code} ({clean_code})"
            st.session_state.watchlist[clean_code] = display_label
            save_watchlist(st.session_state.watchlist)
            st.success(f"종목코드 '{clean_code}' 등록 완료!")
            st.rerun()
        else:
            st.error("유효하지 않은 종목코드이거나 데이터를 가져올 수 없습니다.")
else:
    # 선택된 종목코드 찾기
    symbol_input = [k for k, v in watchlist.items() if v == selected_option][0]
    
    # 삭제 버튼
    col_space, col_del = st.columns([3, 1])
    with col_del:
        if st.button("🗑️ 목록에서 삭제", use_container_width=True):
            del st.session_state.watchlist[symbol_input]
            save_watchlist(st.session_state.watchlist)
            st.toast("삭제되었습니다.")
            st.rerun()

# 6. 데이터 분석 및 차트 출력
df, full_ticker = load_etf_data(symbol_input, period)

if df is None:
    st.error(f"데이터를 불러올 수 없습니다. 종목코드('{symbol_input}')를 확인하세요.")
else:
    curr_price = float(df['Close'].iloc[-1])
    prev_price = float(df['Close'].iloc[-2])
    chg_pct = ((curr_price - prev_price) / prev_price) * 100
    
    rsi = float(df['RSI'].iloc[-1])
    ma20 = float(df['MA20'].iloc[-1])
    ma60 = float(df['MA60'].iloc[-1])
    ma120 = float(df['MA120'].iloc[-1])
    macd = float(df['MACD'].iloc[-1])
    macd_sig = float(df['MACD_Signal'].iloc[-1])
    vol_ratio = float(df['Volume'].iloc[-1] / df['Vol_MA20'].iloc[-1]) if df['Vol_MA20'].iloc[-1] > 0 else 1.0
    bb_upper = float(df['BB_Upper'].iloc[-1])
    bb_lower = float(df['BB_Lower'].iloc[-1])
    
    trend_score = 0
    if curr_price > ma20: trend_score += 1
    if ma20 > ma60: trend_score += 1
    if ma60 > ma120: trend_score += 1
    
    status_text = "상승 추세" if trend_score >= 2 else ("조정/횡보" if trend_score == 1 else "하락 추세")
    
    # 지표 카드
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("현재가", f"{curr_price:,.0f}원", f"{chg_pct:+.2f}%")
    m2.metric("추세점수", f"{trend_score}/3", status_text)
    m3.metric("RSI (14)", f"{rsi:.1f}", "과열" if rsi > 70 else ("침체" if rsi < 30 else "중립"))
    m4.metric("거래량 비율", f"{vol_ratio:.2f}x", "급증" if vol_ratio >= 1.5 else "평이")

    tab_chart, tab_scenario, tab_details = st.tabs(["📊 차트", "🎯 시나리오", "🔍 지표 분석"])

    with tab_chart:
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.03, row_heights=[0.55, 0.2, 0.25])

        # 캔들차트
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                                     low=df['Low'], close=df['Close'], name="주가"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='orange', width=1), name="MA20"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], line=dict(color='green', width=1), name="MA60"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA120'], line=dict(color='purple', width=1), name="MA120"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='gray', dash='dot'), name="BB상단"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='gray', dash='dot'), name="BB하단"), row=1, col=1)

        # 거래량
        colors = ['red' if c >= o else 'blue' for c, o in zip(df['Close'], df['Open'])]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="거래량"), row=2, col=1)

        # MACD
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='blue'), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], line=dict(color='red'), name="Signal"), row=3, col=1)

        fig.update_layout(height=550, margin=dict(l=10, r=10, t=10, b=10),
                          xaxis_rangeslider_visible=False, template="plotly_dark", showlegend=False)
        
        # 고유 key 값을 부여하여 차트가 새로고침 시 깜빡이거나 튀는 현상 방지
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{symbol_input}_{period}")

    with tab_scenario:
        recent_60 = df.iloc[-60:]
        r1 = float(recent_60['High'].max())
        s1 = float(recent_60['Low'].min())
        
        st.subheader("📌 지지 & 저항 가격대")
        c_sup, c_res = st.columns(2)
        c_sup.info(f"**1차 지지선 (60일 최저)**\n\n### {s1:,.0f} 원")
        c_res.warning(f"**1차 저항선 (60일 최고)**\n\n### {r1:,.0f} 원")

        st.subheader("💡 자동 분석 대응 시나리오")
        if trend_score == 3 and rsi < 65:
            st.success("🟢 **강한 상승 추세 / 눌림목 매수 유효 구간**\n\nMA20 부근까지 이격 조정을 줄 때 분할 접근이 유리합니다.")
        elif trend_score >= 2 and rsi >= 70:
            st.warning("🟡 **상승 지속 중이나 RSI 단기 과열**\n\n신규 추격 매수보다는 보유자 영역이며, 밴드 상단 이탈 시 분할 익절을 고려하세요.")
        elif trend_score <= 1 and curr_price <= bb_lower:
            st.info("🔵 **하락/조정세 과매도 구간**\n\n볼린저밴드 하단에 도달했습니다. 반등 확인 후 기술적 분할 매수가 가능한 위치입니다.")
        else:
            st.error("🔴 **추세 약화 및 관망 구간**\n\n이동평균선 역배열 또는 모멘텀 부재 상태입니다. 뚜렷한 거래량 동반 반등 전까지 관망을 권장합니다.")

    with tab_details:
        st.markdown("### 📋 세부 보조지표 종합")
        details_df = pd.DataFrame({
            "지표": ["MA20 위치", "MA60 위치", "MACD 방향", "볼린저밴드 위치", "거래량 변동"],
            "상태": [
                "상회" if curr_price > ma20 else "하회",
                "상회" if curr_price > ma60 else "하회",
                "우상향 (Golden Cross)" if macd > macd_sig else "우하향 (Dead Cross)",
                f"상단 대비 {((curr_price - bb_lower)/(bb_upper - bb_lower))*100:.0f}% 위치",
                f"20일 평균 대비 {vol_ratio*100:.0f}%"
            ]
        })
        st.table(details_df)
