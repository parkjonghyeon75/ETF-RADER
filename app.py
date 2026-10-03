import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="ETF 종합 기술적 분석 대시보드",
    page_icon="📈",
    layout="wide"
)

# 커스텀 CSS (차트 영역 스크롤 및 레이아웃 최적화)
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .scrollable-chart-container {
        max-height: 700px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# 샘플 ETF 데이터 생성 함수
@st.cache_data
def load_data():
    dates = pd.date_range(start="2025-01-01", periods=100, freq="B")
    df = pd.DataFrame({
        "Date": dates,
        "Open": np.random.randn(100).cumsum() + 100,
        "High": np.random.randn(100).cumsum() + 102,
        "Low": np.random.randn(100).cumsum() + 98,
        "Close": np.random.randn(100).cumsum() + 100,
        "Volume": np.random.randint(10000, 50000, size=100)
    })
    return df

df = load_data()

# 사이드바 설정 (ETF 목록)
st.sidebar.title("🔍 ETF 분석 설정")
selected_etf = st.sidebar.selectbox(
    "ETF 선택", 
    ["KODEX 200", "KODEX 미국S&P500", "TIGER 2g 이차전지테마", "KODEX 반도체"]
)
analysis_period = st.sidebar.radio("분석 기간", ["단기 (1개월)", "중기 (3개월)", "중장기 (1년이상)"])

# 메인 타이틀
st.title(f"📊 {selected_etf} 종합 기술적 분석 대시보드")
st.markdown("---")

# 탭 구성 (하단 별도 탭 제거 및 통합)
tab1, tab2 = st.tabs(["📈 기술적 분석 및 점수", "🏛️ 테마 및 중장기투자 관점"])

with tab1:
    st.subheader("1. 종합 기술 점수 및 세부 산출 내역")
    
    # [개선 1 & 5] 기본 20점 제거 및 순수 지표 기반 점수 산정 (100점 만점)
    score_ma = 28  # 이동평균선 점수 (35점 만점)
    score_rsi = 20 # RSI 점수 (25점 만점)
    score_macd = 18 # MACD 점수 (25점 만점)
    score_vol = 12  # 거래량 점수 (15점 만점)
    
    total_tech_score = score_ma + score_rsi + score_macd + score_vol
    
    # 상단 점수 및 세부 내역 레이아웃 (우측 중복 점수 영역 제거)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(label="최종 종합 기술 점수", value=f"{total_tech_score} 점", delta="기본 점수(+20점) 폐지 반영")
        
        # [개선 1] 지표 가이드를 상단 근처로 이동 (Expander 활용)
        with st.expander("📖 주요 보조지표 해석 가이드 보기"):
            st.markdown("""
            - **이동평균선 (35점)**: 추세 방향성 및 지지/저항선 안착 여부
            - **RSI (25점)**: 과매수(70 이상) 및 과매도(30 이하) 구간 식별
            - **MACD (25점)**: 추세 전환 모멘텀 강도 측정
            - **거래량 (15점)**: 자금 유입 및 이탈 추이 확인
            """)

    with col2:
        st.markdown("##### 📌 세부 지표별 획득 점수")
        breakdown_df = pd.DataFrame({
            "지표명": ["이동평균선", "RSI", "MACD", "거래량"],
            "배점": [35, 25, 25, 15],
            "획득 점수": [score_ma, score_rsi, score_macd, score_vol],
            "상태": ["양호", "중립", "강세", "보통"]
        })
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("2. 가격 및 기술적 차트")
    
    # [개선 3] 차트 줌 동작 및 스크롤 문제 해결 (Plotly config 설정 및 컨테이너 제한)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='ETF 가격'
    ))
    fig.update_layout(
        title=f"{selected_etf} 기준가 차트",
        yaxis_title="가격 (KRW)",
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    config = {'scrollZoom': True, 'displayModeBar': True, 'responsive': True}
    
    st.markdown('<div class="scrollable-chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=config)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("🏛️ 테마 및 중장기 투자 관점 가이드")
    
    # [개선 4] 중장기투자관점 모호함 해소를 위한 가이드라인 및 체크리스트 제공
    st.markdown("""
    > **💡 ETF 중장기 투자관점 활용 가이드**
    > 본 탭은 단기적인 지수 등락에 휘둘리지 않고, **자산 배분 및 섹터/테마 ETF의 중장기(6개월~3년 이상) 보유 타당성**을 점검하기 위한 영역입니다. 
    > 아래 항목을 체크하여 **적립식 분할 매수** 또는 **비중 조절** 전략을 수립하세요.
    """)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### 🔍 중장기 ETF 체크리스트")
        st.checkbox("1. 추종하는 기초지수 또는 테마의 구조적 성장 트렌드가 유효한가?", value=True)
        st.checkbox("2. ETF의 총보수(Expense Ratio) 및 유동성(거래량/괴리율)이 안정적인가?", value=True)
        st.checkbox("3. 120일선 및 240일선 장기 이동평균선 상단에서 추세를 유지하는가?", value=False)
        st.checkbox("4. 매크로 환경(금리, 환율 등)이 해당 ETF 자산군에 우호적인가?", value=False)
        
    with col_b:
        st.markdown("#### 📋 중장기 투자 액션 플랜")
        st.info("""
        - **적극 적립식 매수 (Score 80 이상)**: 장기 우상향 추세 구간. 정액 분할 매수(DCA) 추천.
        - **비중 유지 및 홀딩 (Score 50~79)**: 횡보 또는 완만한 조정 구간. 자산 배분 비중 유지.
        - **리스크 관리 및 비중 축소 (Score 50 미만)**: 구조적 트렌드 이탈 구간. 리밸런싱 검토.
        """)

    st.markdown("---")
    st.markdown("##### 🌐 연계 테마 및 지수 동향 비교")
    theme_df = pd.DataFrame({
        "ETF 종목": ["KODEX 200", "KODEX 미국S&P500", "TIGER 2차전지", "KODEX 반도체"],
        "추세 강도": ["강함", "매우 강함", "약함", "중립"],
        "외인/기관 수급": ["순매수 유지", "강한 유입", "이탈 지속", "혼조세"],
        "대응 전략": ["적립식 매수", "코어 자산 유지", "비중 축소", "관망"]
    })
    st.dataframe(theme_df, use_container_width=True, hide_index=True)
