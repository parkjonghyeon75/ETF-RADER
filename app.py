import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="종합 기술적 분석 대시보드",
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

# 샘플 데이터 생성 함수
@st.cache_data
def load_data():
    dates = pd.date_range(start="2025-01-01", periods=100, freq="B")
    df = pd.DataFrame({
        "Date": dates,
        "Open": np.random.randn(100).cumsum() + 100,
        "High": np.random.randn(100).cumsum() + 102,
        "Low": np.random.randn(100).cumsum() + 98,
        "Close": np.random.randn(100).cumsum() + 100,
        "Volume": np.random.randint(1000, 10000, size=100)
    })
    return df

df = load_data()

# 사이드바 설정
st.sidebar.title("🔍 분석 설정")
selected_stock = st.sidebar.selectbox("종목 선택", ["삼성전자", "SK하이닉스", "LG에너지솔루션", "현대차"])
analysis_period = st.sidebar.radio("분석 기간", ["단기 (1개월)", "중기 (3개월)", "중장기 (1년이상)"])

# 메인 타이틀
st.title(f"📊 {selected_stock} 종합 기술적 분석 대시보드")
st.markdown("---")

# 탭 구성 (하단 별도 탭 제거 및 통합)
tab1, tab2 = st.tabs(["📈 기술적 분석 및 점수", "🏛️ 테마 및 중장기투자 관점"])

with tab1:
    st.subheader("1. 종합 기술 점수 및 세부 산출 내역")
    
    # [개선 1 & 5] 기본 20점 제거 및 순수 지표 기반 점수 산정 (100점 만점)
    # 예시 지표: 이평선(35점), RSI(25점), MACD(25점), 거래량(15점)
    score_ma = 28  # 이동평균선 점수 (35점 만점)
    score_rsi = 20 # RSI 점수 (25점 만점)
    score_macd = 18 # MACD 점수 (25점 만점)
    score_vol = 12  # 거래량 점수 (15점 만점)
    
    total_tech_score = score_ma + score_rsi + score_macd + score_vol
    
    # 상단 점수 및 세부 내역 레이아웃 (우측 중복 점수 영역 제거)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(label="최종 종합 기술 점수", value=f"{total_tech_score} 점", delta="기준 점수(+20점) 폐지됨")
        
        # [개선 1] 지표 가이드를 상단 근처로 이동 (Expander 활용)
        with st.expander("📖 주요 보조지표 해석 가이드 보기"):
            st.markdown("""
            - **이동평균선 (35점)**: 골든크로스 및 정배열 상태 평가
            - **RSI (25점)**: 과매수(70 이상) 및 과매도(30 이하) 구간 분석
            - **MACD (25점)**: 추세 전환 시그널 강도 측정
            - **거래량 (15점)**: 수급 유입 및 이탈 여부 확인
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
        name='가격'
    ))
    fig.update_layout(
        title=f"{selected_stock} 주가 차트",
        yaxis_title="가격 (KRW)",
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # config 설정으로 불필요한 고정 줌 버그 방지 및 반응형 유지
    config = {'scrollZoom': True, 'displayModeBar': True, 'responsive': True}
    
    st.markdown('<div class="scrollable-chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=config)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("🏛️ 테마 및 중장기 투자 관점 가이드")
    
    # [개선 4] 중장기투자관점의 모호함 해결 (명확한 행동 지침 및 체크리스트 제공)
    st.markdown("""
    > **💡 중장기 투자관점 활용 가이드**
    > 본 탭은 단기 변동성에 흔들리지 않고, **6개월 ~ 3년 이상의 호흡**으로 기업의 펀더멘털과 산업 모멘텀을 점검하기 위한 영역입니다. 
    > 아래 체크리스트와 핵심 지표를 바탕으로 **분할 매수** 또는 **보유(Hold) 여부**를 결정하세요.
    """)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### 🔍 중장기 핵심 체크리스트")
        st.checkbox("1. 해당 테마의 구조적 성장성(정부 정책 또는 글로벌 트렌드)이 유효한가?", value=True)
        st.checkbox("2. 기업의 펀더멘털(영업이익 및 현금흐름)이 우상향하고 있는가?", value=False)
        st.checkbox("3. 120일선 및 240일선 장기 이동평균선 위에서 지지를 받고 있는가?", value=True)
        st.checkbox("4. 산업 내 시장 점유율(M/S)이 유지되거나 확대되고 있는가?", value=False)
        
    with col_b:
        st.markdown("#### 📋 투자 전략 액션 플랜")
        st.info("""
        - **적극 매수 (Score 80 이상)**: 장기 추세 우상향 및 테마 주도주 구간. 정액 분할 매수 추천.
        - **비중 확대 / 홀딩 (Score 50~79)**: 박스권 횡보 또는 조정 국면. 저점 분할 매집 유효.
        - **리스크 관리 / 현금화 (Score 50 미만)**: 장기 추세 이탈 및 모멘텀 약화. 비중 축소 권장.
        """)

    st.markdown("---")
    st.markdown("##### 🌐 관련 테마 동향 분석")
    theme_df = pd.DataFrame({
        "테마명": ["반도체 슈퍼사이클", "AI 인프라", "이차전지 소재", "로보틱스"],
        "테마 강도": ["매우 강함", "강함", "중립", "약함"],
        "수급 동향": ["기관/외인 순매수", "외인 순매수", "개인 매수 우위", "관망세"],
        "대응 전략": ["추세 추종", "분할 매수", "보유 후 관망", "비중 축소"]
    })
    st.dataframe(theme_df, use_container_width=True, hide_index=True)
