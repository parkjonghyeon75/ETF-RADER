import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 페이지 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ETF 분석 대시보드",
    page_icon="📈",
    layout="wide"
)

# -----------------------------------------------------------------------------
# CSS 스타일 적용 (st.html 대신 st.markdown을 사용하여 호환성 확보)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 유틸리티 함수
# -----------------------------------------------------------------------------
def safe_float(val, default=0.0):
    try:
        if val is None or pd.isna(val):
            return default
        return float(val)
    except (ValueError, TypeError):
        return default

def format_money(val):
    val_f = safe_float(val)
    return f"{val_f:,.0f}원" if val_f >= 1000 else f"{val_f:,.2f}"

# -----------------------------------------------------------------------------
# 데이터 수처리 및 정규화 함수
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_etf_data(ticker_symbol, start_date, end_date):
    try:
        df = yf.download(ticker_symbol, start=start_date, end=end_date, progress=False)
        if df.empty:
            return pd.DataFrame()
        
        # 멀티인덱스 컬럼 구조 대응 (yfinance 최신 버전 호환)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # 타임존 제거 (tz-naive로 변환하여 에러 방지)
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
            
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다 ({ticker_symbol}): {e}")
        return pd.DataFrame()

# -----------------------------------------------------------------------------
# 메인 레이아웃
# -----------------------------------------------------------------------------
st.markdown('<p class="main-header">📈 ETF 종합 분석 대시보드</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">관심 있는 ETF의 성과, 변동성 및 차트를 실시간으로 분석해보세요.</p>', unsafe_allow_html=True)

# 사이드바 설정
st.sidebar.header("⚙️ 분석 설정")
ticker = st.sidebar.text_input("ETF 티커 입력 (예: SPY, QQQ, 069500.KS)", value="SPY").strip().upper()

period_option = st.sidebar.selectbox(
    "조회 기간",
    [" 최근 6개월", " 최근 1년", " 최근 3년", " 최근 5년", " 직접 선택"],
    index=1
)

end_date = datetime.today()
if period_option == " 최근 6개월":
    start_date = end_date - timedelta(days=180)
elif period_option == " 최근 1년":
    start_date = end_date - timedelta(days=365)
elif period_option == " 최근 3년":
    start_date = end_date - timedelta(days=365 * 3)
elif period_option == " 최근 5년":
    start_date = end_date - timedelta(days=365 * 5)
else:
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("시작일", end_date - timedelta(days=365))
    with col2:
        end_date = st.date_input("종료일", end_date)

# -----------------------------------------------------------------------------
# 데이터 로드 및 분석 실행
# -----------------------------------------------------------------------------
if ticker:
    with st.spinner(f"'{ticker}' 데이터를 불러오는 중입니다..."):
        df = load_etf_data(ticker, start_date, end_date)
        
    if df.empty:
        st.warning(f"'{ticker}'에 대한 데이터를 찾을 수 없습니다. 티커 심볼을 다시 확인해 주세요.")
    else:
        # 기본 지표 계산
        latest_close = safe_float(df['Close'].iloc[-1])
        prev_close = safe_float(df['Close'].iloc[-2]) if len(df) > 1 else latest_close
        daily_change = latest_close - prev_close
        daily_change_pct = (daily_change / prev_close) * 100 if prev_close != 0 else 0.0
        
        high_52w = safe_float(df['High'].max())
        low_52w = safe_float(df['Low'].min())
        
        # 지표 출력 영역
        st.subheader(f"📊 {ticker} 요약 정보")
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.metric("현재가 (종가)", f"{latest_close:,.2f}", f"{daily_change:+.2f} ({daily_change_pct:+.2f}%)")
        with m2:
            st.metric("기간 최고가", f"{high_52w:,.2f}")
        with m3:
            st.metric("기간 최저가", f"{low_52w:,.2f}")
        with m4:
            total_return = ((latest_close - safe_float(df['Close'].iloc[0])) / safe_float(df['Close'].iloc[0])) * 100
            st.metric("기간 누적 수익률", f"{total_return:+.2f}%")
            
        st.markdown("---")
        
        # 차트 그리기 (Plotly)
        st.subheader("📈 주가 추이 차트")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df['Close'], 
            mode='lines', 
            name='종가 (Close)',
            line=dict(color='#2563EB', width=2)
        ))
        
        fig.update_layout(
            title=f"{ticker} 가격 추이",
            xaxis_title="날짜",
            yaxis_title="가격",
            template="plotly_white",
            hovermode="x unified",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 데이터 테이블 확인 옵션
        with st.expander("원천 데이터(DataFrame) 확인하기"):
            st.dataframe(df.tail(20))
