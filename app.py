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
        "Volume": np.random.randint(10000, 50000, size=100)
    })
    return df

df = load_data()

# 세션 스테이트를 이용한 기본 ETF 목록 관리 (종목 추가 기능 지원)
if "etf_list" not in st.session_state:
    st.session_state.etf_list = [
        "KODEX AI반도체TOP2플러스",
        "KODEX AI전력핵심설비",
        "KODEX AI반도체핵심장비",
        "KODEX 미국AI광통신네트워크",
        "SOL 미국배당미국채혼합50",
        "TIGER 미국필라델피아반도체나스닥",
        "SOL AI반도체소부장",
        "TIGER 미국나스닥100",
        "TIGER 미국S&P500"
    ]

# 사이드바 설정
st.sidebar.title("🔍 관심 ETF 분석 설정")

# [수정 2] 종목명 또는 종목코드로 직접 추가할 수 있는 입력 기능
with st.sidebar.expander("➕ 종목(ETF) 추가하기"):
    new_etf_input = st.text_input("종목명 또는 종목코드 입력", placeholder="예: KODEX 200 또는 069500")
    if st.button("추가", use_container_width=True):
        if new_etf_input and new_etf_input not in st.session_state.etf_list:
            st.session_state.etf_list.append(new_etf_input)
            st.success(f"'{new_etf_input}' 추가 완료!")
        elif new_etf_input in st.session_state.etf_list:
            st.warning("이미 리스트에 존재하는 종목입니다.")

selected_etf = st.sidebar.selectbox("ETF 선택", st.session_state.etf_list, index=0)
analysis_period = st.sidebar.radio("분석 기간", ["단기 (1개월)", "중기 (3개월)", "중장기 (1년이상)"])

# 메인 타이틀
st.title(f"📊 {selected_etf} 종합 기술적 분석 대시보드")
st.markdown("---")

# 탭 구성
tab1, tab2 = st.tabs(["📈 기술적 분석 및 점수", "🏛️ 테마 및 중장기투자 관점"])

with tab1:
    st.subheader("1. 종합 기술 점수 및 세부 산출 내역")
    
    # [수정 1] 기본 20점 관련 문구/델타 완전 삭제 후 순수 100점 만점 산정
    score_ma = 28  # 이동평균선 점수 (35점 만점)
    score_rsi = 20 # RSI 점수 (25점 만점)
    score_macd = 18 # MACD 점수 (25점 만점)
    score_vol = 12  # 거래량 점수 (15점 만점)
    
    total_tech_score = score_ma + score_rsi + score_macd + score_vol
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # [수정 1] 깔끔하게 최종 점수만 표기
        st.metric(label="최종 종합 기술 점수", value=f"{total_tech_score} 점")
        
        # 지표 가이드를 상단 근처 Expander로 배치
        with st.expander("📖 주요 보조지표 해석 가이드 보기"):
            st.markdown("""
            - **이동평균선 (35점)**: 추세 방향성 및 이평선 배열 상태
            - **RSI (25점)**: 과매수(70 이상) / 과매도(30 이하) 구간 판별
            - **MACD (25점)**: 추세 전환 시그널 및 모멘텀 강도
            - **거래량 (15점)**: 수급 유입 및 주가 신뢰도 확인
            """)

    with col2:
        st.markdown("##### 📌 세부 지표별 획득 점수 및 행동 가이드")
        # [수정 3] 상태 칸을 모호한 단어가 아닌 구체적인 대응 가이드로 변경
        breakdown_df = pd.DataFrame({
            "지표명": ["이동평균선", "RSI", "MACD", "거래량"],
            "배점": [35, 25, 25, 15],
            "획득 점수": [score_ma, score_rsi, score_macd, score_vol],
            "대응 및 해석 가이드": [
                "정배열 유지 중 (분할 매수 유효)", 
                "중립 구간 위치 (추가 모멘텀 대기)", 
                "골든크로스 발생 (매수 관점 접근)", 
                "평균 거래량 이하 (관망 필요)"
            ]
        })
        st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("2. 가격 및 기술적 차트")
    
    # [수정 4] 이전 방식의 직관적인 캔들스틱 차트 원복 및 줌/스크롤 제어 최적화
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='ETF 가격'
    ))
    fig.update_layout(
        title=f"{selected_etf} 가격 추이",
        yaxis_title="가격 (KRW)",
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # 차트 영역 제어용 config (임의 줌 틀어짐 방지 설정)
    config = {'scrollZoom': False, 'displayModeBar': True, 'responsive': True}
    
    st.markdown('<div class="scrollable-chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=config)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("🏛️ 테마 및 중장기 투자 관점")
    
    # [수정 5] 체크리스트 제거 및 깔끔한 중장기 관점 가이드문구 배치
    st.markdown("""
    > **💡 중장기 투자 관점 가이드**
    > 단기 시세 변동에 흔들리지 않고, 산업 트렌드와 섹터별 수급 흐름을 바탕으로 포트폴리오 비중을 조절하는 영역입니다. 
    > 아래 그룹별 동향을 참고하여 자산 배분 전략을 수립하세요[span_2](start_span)[span_2](end_span).
    """)
    
    st.markdown("##### 🌐 관심 ETF 그룹별 테마 동향 비교[span_3](start_span)[span_3](end_span)")
    
    # [수정 5] 가독성을 높인 테마 동향 비교 테이블
    theme_df = pd.DataFrame({
        "ETF 종목": [
            "KODEX AI반도체TOP2플러스", "KODEX AI전력핵심설비", 
            "KODEX AI반도체핵심장비", "KODEX 미국AI광통신네트워크"
        ],
        "중장기 추세": ["상승세 유지", "강한 우상향", "박스권 횡보", "상승 주도"],
        "주요 수급 주체": ["기관 / 외국인", "외국인 연속 순매수", "개인 중심", "기관 중심"],
        "투자 비중 전략": ["코어(Core) 비중 유지", "적극적 분할 매수", "비중 유지 후 관망", "트레이딩 비중 확대"]
    })
    st.dataframe(theme_df, use_container_width=True, hide_index=True)
