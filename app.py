import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    .status-badge {
        font-weight: bold;
        padding: 4px 8px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 2. 세션 상태(Session State) 기반 관심종목 목록 초기화
if "watchlist" not in st.session_state:
    st.session_state.watchlist = {
        "KODEX 200": "069500",
        "KODEX 반도체": "091160",
        "KODEX AI반도체핵심장비": "466920",
        "KODEX 미국S&P500": "379800",
        "TIGER 2차전지테마": "305540"
    }

# 3. 보조지표 계산 함수 (순수 Pandas 구현)
def calculate_indicators(df):
    # 이동평균선
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA60'] = df['Close'].rolling(60).mean()
    df['MA120'] = df['Close'].rolling(120).mean()
    
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD (12, 26, 9)
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    # Bollinger Bands (20, 2)
    df['BB_Mid'] = df['MA20']
    std = df['Close'].rolling(20).std()
    df['BB_Upper'] = df['BB_Mid'] + (std * 2)
    df['BB_Lower'] = df['BB_Mid'] - (std * 2)
    
    # 거래량 20일 평균
    df['Vol_MA20'] = df['Volume'].rolling(20).mean()
    
    return df

# 4. 데이터 로드
@st.cache_data(ttl=300)
def load_etf_data(ticker_code, period="1y"):
    ticker = ticker_code.strip().upper()
    if not (ticker.endswith(".KS") or ticker.endswith(".KQ")):
        ticker = f"{ticker}.KS"
    
    data = yf.download(ticker, period=period, progress=False)
    if data.empty or len(data) < 30:
        return None, ticker
    
    # MultiIndex 컬럼 정리
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
        
    df = calculate_indicators(data)
    return df, ticker

# UI 헤더
st.title("📈 ETF Technical Radar")

# 5. 관심종목 선택 및 관리 UI
preset_options = list(st.session_state.watchlist.keys()) + ["➕ 직접 입력 / 관심종목 등록"]

col_sel, col_pd = st.columns([2, 1])
with col_sel:
    selected_preset = st.selectbox("⭐ 관심 ETF 선택", preset_options)
with col_pd:
    period = st.selectbox("기간", ["6m", "1y", "2y"], index=1)

# 직접 입력 및 신규 관심종목 저장 처리
if selected_preset == "➕ 직접 입력 / 관심종목 등록":
    st.subheader("📝 신규 관심종목 등록")
    col_name, col_code = st.columns([1, 1])
    with col_name:
        custom_name = st.text_input("종목명", placeholder="예: KODEX AI전력")
    with col_code:
        symbol_input = st.text_input("종목코드", placeholder="예: 466920")
    
    if st.button("⭐ 관심종목에 추가하기", use_container_width=True):
        if custom_name and symbol_input:
            st.session_state.watchlist[custom_name] = symbol_input
            st.success(f"'{custom_name}'({symbol_input})이(가) 관심종목에 저장되었습니다!")
            st.rerun()
        else:
            st.warning("종목명과 종목코드를 모두 입력해주세요.")
else:
    symbol_input = st.session_state.watchlist[selected_preset]
    
    # 기존 관심종목 삭제 버튼
    col_space, col_del = st.columns([3, 1])
    with col_del:
        if st.button("🗑️ 관심종목 삭제", use_container_width=True):
            del st.session_state.watchlist[selected_preset]
            st.toast(f"'{selected_preset}' 항목이 삭제되었습니다.")
            st.rerun()

# 6. 데이터 분석 및 화면 출력
df, full_ticker = load_etf_data(symbol_input, period)

if df is None:
    st.error(f"데이터를 불러올 수 없습니다. 종목코드('{symbol_input}')를 확인하세요.")
else:
    curr_price = float(df['Close'].iloc[-1])
    prev_price = float(df['Close'].iloc[-2])
    chg_pct = ((curr_price - prev_price) / prev_price) * 100
    
    # 최신 지표값 추출
    rsi = float(df['RSI'].iloc[-1])
    ma20 = float(df['MA20'].iloc[-1])
    ma60 = float(df['MA60'].iloc[-1])
    ma120 = float(df['MA120'].iloc[-1])
    macd = float(df['MACD'].iloc[-1])
    macd_sig = float(df['MACD_Signal'].iloc[-1])
    vol_ratio = float(df['Volume'].iloc[-1] / df['Vol_MA20'].iloc[-1]) if df['Vol_MA20'].iloc[-1] > 0 else 1.0
    bb_upper = float(df['BB_Upper'].iloc[-1])
    bb_lower = float(df['BB_Lower'].iloc[-1])
    
    # 분석 점수 및 상태 진단
    trend_score = 0
    if curr_price > ma20: trend_score += 1
    if ma20 > ma60: trend_score += 1
    if ma60 > ma120: trend_score += 1
    
    status_text = "상승 추세" if trend_score >= 2 else ("조정/횡보" if trend_score == 1 else "하락 추세")
    
    # 핵심 지표 요약 카드
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("현재가", f"{curr_price:,.0f}원", f"{chg_pct:+.2f}%")
    m2.metric("추세점수", f"{trend_score}/3", status_text)
    m3.metric("RSI (14)", f"{rsi:.1f}", "과열" if rsi > 70 else ("침체" if rsi < 30 else "중립"))
    m4.metric("거래량 비율", f"{vol_ratio:.2f}x", "급증" if vol_ratio >= 1.5 else "평이")

    # 탭 구성 (차트 / 시나리오 / 지표상세)
    tab_chart, tab_scenario, tab_details = st.tabs(["📊 차트", "🎯 시나리오", "🔍 지표 분석"])

    with tab_chart:
        # Plotly 차트 생성 (Candlestick + MA + Volume + Subplots)
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
        st.plotly_chart(fig, use_container_width=True)

    with tab_scenario:
        # 자동 지지/저항선 산출 (최근 60일 피벗)
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
