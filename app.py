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

# 커스텀 CSS (레이아웃 최적화)
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .scrollable-chart-container {
        max-height: 750px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# 샘플 ETF 데이터 생성 함수 (이동평균선 계산 포함)
@st.cache_data
def load_data(ticker):
    np.random.seed(hash(ticker) % 10000)
    dates = pd.date_range(start="2025-01-01", periods=60, freq="B")
    base_price = 40000
    random_walk = np.random.randn(60).cumsum() * 300
    closes = base_price + random_walk
    opens = closes + np.random.randn(60) * 150
    highs = np.maximum(opens, closes) + np.abs(np.random.randn(60) * 200)
    lows = np.minimum(opens, closes) - np.abs(np.random.randn(60) * 200)
    
    df = pd.DataFrame({
        "Date": dates,
        "Open": opens,
        "High": highs,
        "Low": lows,
        "Close": closes,
        "Volume": np.random.randint(50000, 300000, size=60)
    })
    
    # 이동평균선(MA5, MA20) 계산
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    return df

# 기본 종목 및 시세 정보 사전 (코드 입력 대응 포함)
if "etf_dict" not in st.session_state:
    st.session_state.etf_dict = {
        "KODEX AI반도체TOP2플러스": {"code": "471570", "price": "43,220원", "change": "+0.50%"},
        "KODEX AI전력핵심설비": {"code": "481530", "price": "36,900원", "change": "+1.35%"},
        "KODEX AI반도체핵심장비": {"code": "485550", "price": "30,300원", "change": "-0.75%"},
        "KODEX 미국AI광통신네트워크": {"code": "486420", "price": "11,680원", "change": "+3.50%"},
        "SOL 미국배당미국채혼합50": {"code": "476250", "price": "10,450원", "change": "0.00%"},
        "TIGER 미국필라델피아반도체나스닥": {"code": "411540", "price": "45,260원", "change": "-1.35%"},
        "SOL AI반도체소부장": {"code": "473330", "price": "30,500원", "change": "-1.34%"},
        "TIGER 미국나스닥100": {"code": "133690", "price": "183,055원", "change": "-1.40%"},
        "TIGER 미국S&P500": {"code": "360750", "price": "25,780원", "change": "-0.71%"}
    }

# 사이드바 설정
st.sidebar.title("🔍 관심 ETF 분석 설정")

# [수정 1] 종목 코드(예: 411540) 또는 종목명 추가 기능
with st.sidebar.expander("➕ 종목(ETF) 추가하기"):
    new_input = st.text_input("종목명 또는 종목코드 입력", placeholder="예: 411540 또는 KODEX 200")
    if st.button("추가", use_container_width=True):
        if new_input:
            # 코드로 입력한 경우 매핑 처리
            code_mapping = {"411540": "TIGER 미국필라델피아반도체나스닥", "069500": "KODEX 200"}
            target_name = code_mapping.get(new_input, new_input)
            
            if target_name not in st.session_state.etf_dict:
                st.session_state.etf_dict[target_name] = {"code": new_input, "price": "종가 동기화 중", "change": "0.00%"}
                st.success(f"'{target_name}' 추가 완료!")
            else:
                st.warning("이미 등록된 종목입니다.")

# [수정 1] 등록된 종목 삭제 기능 추가
with st.sidebar.expander("🗑️ 종목 삭제하기"):
    remove_target = st.selectbox("삭제할 종목 선택", list(st.session_state.etf_dict.keys()), key="del_box")
    if st.button("선택 종목 삭제", use_container_width=True):
        if len(st.session_state.etf_dict) > 1:
            del st.session_state.etf_dict[remove_target]
            st.success(f"'{remove_target}' 삭제 완료!")
            st.rerun()
        else:
            st.error("최소 1개 이상의 종목이 있어야 합니다.")

# [수정 4] 사이드바 셀렉트박스에 현재가 및 등락률 포맷팅 반영
formatted_etf_options = [
    f"{name} ({info['price']}, {info['change']})" 
    for name, info in st.session_state.etf_dict.items()
]

selected_display = st.sidebar.selectbox("ETF 선택 (현재가·등락률 포함)", formatted_etf_options)
# 선택된 문자열에서 실제 종목명 추출
selected_etf = selected_display.split(" (")[0]
current_info = st.session_state.etf_dict[selected_etf]

analysis_period = st.sidebar.radio("분석 기간", ["단기 (1개월)", "중기 (3개월)", "중장기 (1년이상)"])

df = load_data(selected_etf)

# 메인 타이틀
st.title(f"📊 {selected_etf} 종합 기술적 분석 대시보드")
st.markdown(f"**종목코드**: `{current_info['code']}` | **현재가**: `{current_info['price']}` | **등락률**: `{current_info['change']}`")
st.markdown("---")

# 탭 구성
tab1, tab2 = st.tabs(["📈 기술적 분석 및 점수", "🚀 미래 유망 테마 스캐너"])

with tab1:
    st.subheader("1. 종합 기술 점수 및 세부 산출 내역")
    
    score_ma = 28  
    score_rsi = 20 
    score_macd = 18 
    score_vol = 12  
    total_tech_score = score_ma + score_rsi + score_macd + score_vol
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(label="최종 종합 기술 점수", value=f"{total_tech_score} 점")
        
        with st.expander("📖 주요 보조지표 해석 가이드 보기"):
            st.markdown("""
            - **이동평균선 (35점)**: 추세 방향성 및 이평선 배열 상태
            - **RSI (25점)**: 과매수(70 이상) / 과매도(30 이하) 구간 판별
            - **MACD (25점)**: 추세 전환 시그널 및 모멘텀 강도
            - **거래량 (15점)**: 수급 유입 및 주가 신뢰도 확인
            """)

    with col2:
        st.markdown("##### 📌 세부 지표별 획득 점수 및 행동 가이드")
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
    st.subheader("2. 가격 및 기술적 차트 (이동평균선 포함)")
    
    # [수정 2] 캔들스틱 + 이동평균선(MA5, MA20) 추가 및 날짜 뭉개짐 방지 적용
    fig = go.Figure()
    
    # 캔들스틱 추가
    fig.add_trace(go.Candlestick(
        x=df['Date'].dt.strftime('%Y-%m-%d'),
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='ETF 가격',
        increasing_line_color='#ef5350', 
        decreasing_line_color='#26a69a'
    ))
    
    # 이동평균선 5일선 추가
    fig.add_trace(go.Scatter(
        x=df['Date'].dt.strftime('%Y-%m-%d'),
        y=df['MA5'],
        mode='lines',
        name='MA 5',
        line=dict(color='#ff9800', width=1.5)
    ))

    # 이동평균선 20일선 추가
    fig.add_trace(go.Scatter(
        x=df['Date'].dt.strftime('%Y-%m-%d'),
        y=df['MA20'],
        mode='lines',
        name='MA 20',
        line=dict(color='#2196f3', width=1.5)
    ))
    
    fig.update_layout(
        title=f"{selected_etf} 가격 및 이동평균선(MA5, MA20) 추이",
        yaxis_title="가격 (KRW)",
        xaxis_rangeslider_visible=False,
        height=520,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(nticks=10, type='category') # 날짜 간격 최적화
    )
    
    config = {'scrollZoom': False, 'displayModeBar': True, 'responsive': True}
    
    st.markdown('<div class="scrollable-chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config=config)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    # [수정 3] 미래 먹거리 선점을 위한 유망 테마 스캐너로 전면 개편
    st.subheader("🚀 미래 먹거리 및 차세대 유망 테마 자동 스캐너")
    st.markdown("""
    > **💡 미래 테마 스캐너 가이드**  
    > 본 탭은 다가오는 글로벌 메가트렌드와 신성장 산업을 사전에 점검하기 위한 **미래 먹거리 사전 스캔 공간**입니다. 
    > 주도 섹터의 핵심 동향과 관련 선도 ETF를 파악하여 선제적인 투자 아이디어를 발굴하세요.
    """)
    
    st.markdown("##### 🔍 차세대 글로벌 메가트렌드 및 유망 테마 리스트")
    
    future_theme_df = pd.DataFrame({
        "유망 테마명": [
            "AI 반도체 & HBM 심화", 
            "AI 데이터센터 전력 인프라", 
            "차세대 광통신 & 네트워크", 
            "휴머노이드 & 첨단 로보틱스",
            "우주항공 & 방산 기술",
            "양자 컴퓨팅 & 차세대 보안"
        ],
        "핵심 성장 동력": [
            "초거대 AI 학습량 급증 및 온디바이스 AI 확산",
            "전력 수요 폭증에 따른 송배전, 변압기, SMR 수요",
            "데이터 전송 속도 극대화 및 초저지연 통신망 구축",
            "생산 자동화 및 인구 구조 변화에 따른 로봇 대체",
            "지정학적 리스크 및 우주 상업화 본격화",
            "기존 암호 체계의 한계를 극복하는 미래 보안 인프라"
        ],
        "관련 대표 ETF / 종목군": [
            "KODEX AI반도체TOP2플러스 / SOL AI반도체소부장",
            "KODEX AI전력핵심설비",
            "KODEX 미국AI광통신네트워크",
            "TIGER 글로벌로보틱스 & AI",
            "TIGER 우주항공앤방산",
            "미래 글로벌 테크 패키지"
        ],
        "미래 성장 잠재력": [
            "⭐⭐⭐⭐⭐ (최상)", "⭐⭐⭐⭐⭐ (최상)", 
            "⭐⭐⭐⭐ (상)", "⭐⭐⭐⭐ (상)", 
            "⭐⭐⭐⭐ (상)", "⭐⭐⭐ (중상)"
        ]
    })
    
    st.dataframe(future_theme_df, use_container_width=True, hide_index=True)
