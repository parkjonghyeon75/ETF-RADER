import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ==========================================
# 0. 페이지 기본 설정 및 디자인 스타일링
# ==========================================
st.set_page_config(
    page_title="ETF Gem Radar v5 - 중장기 보석 ETF 발굴기",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background-color: #1e222d;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #2a2e39;
        margin-bottom: 10px;
    }
    .gem-badge-top {
        background-color: #2e7d32;
        color: white;
        padding: 4px 8px;
        border-radius: 5px;
        font-weight: bold;
    }
    .gem-badge-mid {
        background-color: #1565c0;
        color: white;
        padding: 4px 8px;
        border-radius: 5px;
        font-weight: bold;
    }
    .stTable { font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 기본 분석 대상 ETF 리스트 정의
# ==========================================
DEFAULT_ETF_DB = {
    # 한국 상장 주요 ETF (yfinance 티커 규격)
    "TIGER 미국S&P500": {"ticker": "360750.KS", "category": "지수추종", "fee": "0.07%"},
    "TIGER 미국나스닥100": {"ticker": "133690.KS", "category": "테크/성장", "fee": "0.07%"},
    "KODEX 200": {"ticker": "069500.KS", "category": "국내지수", "fee": "0.15%"},
    "KODEX 미국반도체MV": {"ticker": "381180.KS", "category": "반도체/테크", "fee": "0.09%"},
    "TIGER 미국배당다우존스": {"ticker": "423160.KS", "category": "배당/성장", "fee": "0.01%"},
    "KODEX 2차전지산업": {"ticker": "305720.KS", "category": "테마/에너지", "fee": "0.45%"},
    "TIGER 미국테크TOP10 INDXX": {"ticker": "381170.KS", "category": "테크/성장", "fee": "0.49%"},
    # 미국 상장 주요 ETF
    "SPDR S&P 500 (SPY)": {"ticker": "SPY", "category": "미국지수", "fee": "0.09%"},
    "Invesco QQQ (QQQ)": {"ticker": "QQQ", "category": "미국테크", "fee": "0.20%"},
    "Schwab US Dividend Equity (SCHD)": {"ticker": "SCHD", "category": "미국배당", "fee": "0.06%"},
    "iShares Semiconductor (SOXX)": {"ticker": "SOXX", "category": "반도체", "fee": "0.35%"},
    "Vanguard Total World Stock (VT)": {"ticker": "VT", "category": "글로벌지수", "fee": "0.07%"},
}

# ==========================================
# 2. 데이터 연산 및 분석 함수
# ==========================================
@st.cache_data(ttl=3600)
def load_etf_data(ticker_symbol, period="2y"):
    """yfinance를 통해 일봉/주봉 데이터를 수집하고 주요 기술적 지표를 계산합니다."""
    try:
        etf = yf.Ticker(ticker_symbol)
        df = etf.history(period=period)
        if df.empty:
            return None, None, None
        
        # --- 일봉 지표 계산 ---
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA120'] = df['Close'].rolling(window=120).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
        
        # RSI (14)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 120일/200일선 이격도 (%)
        df['Disparity_120'] = (df['Close'] / df['MA120']) * 100
        df['Disparity_200'] = (df['Close'] / df['MA200']) * 100
        
        # MDD (최대 낙폭) 계산 (1년 기준)
        rolling_max = df['Close'].rolling(window=252, min_periods=1).max()
        df['Drawdown'] = (df['Close'] - rolling_max) / rolling_max * 100
        
        # --- 주봉 데이터 생성 및 지표 계산 ---
        df_weekly = df['Close'].resample('W').last().to_frame()
        df_weekly['W_MA20'] = df_weekly['Close'].rolling(window=20).mean()
        df_weekly['W_MA60'] = df_weekly['Close'].rolling(window=60).mean()
        
        # 펀더멘털 기본 정보 추출
        info = etf.info if hasattr(etf, 'info') else {}
        
        return df, df_weekly, info
    except Exception as e:
        return None, None, None

def evaluate_gem_score(df_daily, df_weekly):
    """
    중장기 우상향 보석 종목 판별을 위한 종합 스코어링 엔진 (100점 만점)
    - 주봉 정배열 (30점)
    - 200일선 상회 추세 (20점)
    - 52주 최고가 대비 적정 눌림목 형성 (20점)
    - 중기 RSI 모멘텀 적정성 (15점)
    - 변동성/MDD 안정성 (15점)
    """
    if df_daily is None or len(df_daily) < 200 or df_weekly is None or len(df_weekly) < 60:
        return 0, "데이터 부족", {}

    last_d = df_daily.iloc[-1]
    last_w = df_weekly.iloc[-1]
    
    score = 0
    details = {}
    
    # 1. 주봉 20주선 > 60주선 정배열 (30점)
    if last_w['W_MA20'] > last_w['W_MA60']:
        score += 30
        details['주봉추세'] = "대세 우상향 (정배열)"
    else:
        details['주봉추세'] = "역배열/조정 국면"
        
    # 2. 현재가 > 200일 이동평균선 (20점)
    if last_d['Close'] > last_d['MA200']:
        score += 20
        details['장기지리'] = "200일선 상회 (장기 지지)"
    else:
        details['장기지리'] = "200일선 하회 (주의)"
        
    # 3. 52주 최고가 대비 적정 눌림목 (-5% ~ -15% 구간 우대) (20점)
    high_52w = df_daily['Close'].tail(252).max()
    pullback = ((last_d['Close'] - high_52w) / high_52w) * 100
    details['52주이격'] = f"{pullback:.1f}%"
    
    if -15 <= pullback <= -3:
        score += 20
        details['매수타점'] = "적립식 매수 최적 구간 (High-Quality Dip)"
    elif -3 < pullback <= 0:
        score += 10
        details['매수타점'] = "신고가 부근 (분할매수 추천)"
    else:
        score += 5
        details['매수타점'] = "과도한 낙폭 or 장기 소외"
        
    # 4. RSI 적정성 (40 ~ 60 구간 우대) (15점)
    rsi = last_d['RSI']
    details['RSI'] = f"{rsi:.1f}"
    if 40 <= rsi <= 60:
        score += 15
    elif 30 <= rsi < 40:
        score += 10
    else:
        score += 5
        
    # 5. MDD 안정성 (-20% 이내 유지시 15점) (15점)
    mdd = last_d['Drawdown']
    details['MDD'] = f"{mdd:.1f}%"
    if mdd > -15:
        score += 15
    elif mdd > -25:
        score += 10
    else:
        score += 5

    # 등급 산출
    if score >= 80:
        grade = "💎💎💎 (S급 최상위 보석)"
    elif score >= 65:
        grade = "💎💎 (A급 우수 종목)"
    elif score >= 50:
        grade = "💎 (B급 관망/보유)"
    else:
        grade = "⚠️ (C급 하락추세)"

    return score, grade, details

# ==========================================
# 3. 사이드바 - 설정 및 대상 종목 관리
# ==========================================
st.sidebar.title("💎 ETF Radar v5")
st.sidebar.caption("중장기 우상향 보석 ETF 스크리너")

st.sidebar.subheader("📌 스크리닝 대상 선택")
selected_etf_names = st.sidebar.multiselect(
    "분석할 ETF를 선택하세요:",
    options=list(DEFAULT_ETF_DB.keys()),
    default=list(DEFAULT_ETF_DB.keys())[:6]
)

# 사용자 정의 티커 추가 기능
st.sidebar.markdown("---")
st.sidebar.subheader("➕ 사용자 정의 티커 추가")
custom_ticker = st.sidebar.text_input("yfinance 티커 입력 (예: NVDA, 005930.KS)", "").strip().upper()
custom_name = st.sidebar.text_input("종목명 입력", "").strip()

if st.sidebar.button("티커 추가"):
    if custom_ticker and custom_name:
        DEFAULT_ETF_DB[custom_name] = {"ticker": custom_ticker, "category": "사용자추가", "fee": "N/A"}
        st.sidebar.success(f"'{custom_name}' 추가 완료! 목록에서 선택하세요.")
    else:
        st.sidebar.warning("티커와 종목명을 모두 입력해주세요.")

# ==========================================
# 4. 메인 화면 구성 (탭 구조)
# ==========================================
st.title("🛡️ ETF Technical & Fundamental Radar v5")
st.caption("장기 우상향 펀더멘털과 주봉/일봉 기술적 눌림목을 결합한 스마트 ETF 매매 보조 시스템")

tab1, tab2, tab3 = st.tabs([
    "💎 1. 중장기 보석 ETF 스크리너", 
    "🏛️ 2. ETF 펀더멘털 & 적립식 타점", 
    "📈 3. 주봉/일봉 추세 분석 차트"
])

# ------------------------------------------
# TAB 1: 중장기 보석 ETF 스크리너
# ------------------------------------------
with tab1:
    st.subheader("🔍 실시간 중장기 우상향 보석 종목 스크리닝")
    st.write("주봉 정배열, 200일선 장기 지지, 52주 최고가 대비 눌림목 깊이를 종합 계산하여 우량 ETF를 자동으로 정렬합니다.")
    
    if st.button("🚀 스크리닝 실행 / 데이터 갱신"):
        st.cache_data.clear()

    screener_results = []
    
    progress_bar = st.progress(0)
    for idx, name in enumerate(selected_etf_names):
        info_dict = DEFAULT_ETF_DB[name]
        df_d, df_w, yf_info = load_etf_data(info_dict['ticker'])
        
        if df_d is not None and not df_d.empty:
            score, grade, details = evaluate_gem_score(df_d, df_w)
            last_price = df_d['Close'].iloc[-1]
            disp_120 = df_d['Disparity_120'].iloc[-1]
            
            screener_results.append({
                "보석 등급": grade,
                "종목명": name,
                "카테고리": info_dict['category'],
                "보석 점수": score,
                "현재가": f"{last_price:,.0f}" if "KS" in info_dict['ticker'] else f"${last_price:,.2f}",
                "주봉 추세": details.get('주봉추세', '-'),
                "120일 이격도": f"{disp_120:.1f}%",
                "52주 최고 대비": details.get('52주이격', '-'),
                "매수 평가": details.get('매수타점', '-'),
                "운용보수": info_dict['fee']
            })
        progress_bar.progress((idx + 1) / len(selected_etf_names))
    progress_bar.empty()

    if screener_results:
        res_df = pd.DataFrame(screener_results)
        res_df = res_df.sort_values(by="보석 점수", ascending=False).reset_index(drop=True)
        
        # 메트릭 요약 카드로 상위 1위 종목 강조
        top_gem = res_df.iloc[0]
        st.markdown(f"""
        <div class="metric-card">
            <h4>🏆 오늘의 TOP 추천 보석 ETF: <span style="color:#4caf50;">{top_gem['종목명']}</span> ({top_gem['보석 점수']}점)</h4>
            <p><b>평가:</b> {top_gem['보석 등급']} | <b>매수 가이드:</b> {top_gem['매수 평가']} | <b>120일 이격도:</b> {top_gem['120일 이격도']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 스크리닝 결과 테이블 출력
        st.dataframe(res_df, use_container_width=True, height=400)
    else:
        st.warning("선택된 종목의 데이터를 불러올 수 없습니다.")

# ------------------------------------------
# TAB 2: ETF 펀더멘털 & 적립식 매수 타점
# ------------------------------------------
with tab2:
    st.subheader("🏛️ ETF 기초체력 검증 & 분할매수 적기 진단")
    
    col_sel, col_empty = st.columns([1, 2])
    with col_sel:
        target_name = st.selectbox("상세 분석할 ETF 선택:", selected_etf_names)
    
    target_info = DEFAULT_ETF_DB[target_name]
    df_d, df_w, yf_info = load_etf_data(target_info['ticker'])
    
    if df_d is not None and not df_d.empty:
        last_d = df_d.iloc[-1]
        score, grade, details = evaluate_gem_score(df_d, df_w)
        
        # 주요 핵심 지표 4개 메트릭 카드로 표출
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재가", f"{last_d['Close']:,.0f}" if "KS" in target_info['ticker'] else f"${last_d['Close']:,.2f}")
        c2.metric("200일 이동평균선", f"{last_d['MA200']:,.0f}" if "KS" in target_info['ticker'] else f"${last_d['MA200']:,.2f}")
        
        # 120일선 이격도에 따른 매수 진단
        disp120 = last_d['Disparity_120']
        disp_status = "🟢 적립식 매수 적기 (저평가/눌림)" if disp120 <= 100 else ("🟡 정상 추세 진행 중" if disp120 <= 110 else "🔴 단기 과열 (분할 매수 자제)")
        c3.metric("120일선 이격도", f"{disp120:.1f}%", delta=disp_status)
        c4.metric("최대 낙폭 (MDD)", f"{last_d['Drawdown']:.1f}%")

        st.markdown("---")
        
        # 분할 매수 가이드 제시
        st.subheader("🎯 중장기 적립식 분할매수 가이드라인")
        
        ma120_val = last_d['MA120']
        ma200_val = last_d['MA200']
        curr_val = last_d['Close']
        
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("#### 📌 가격대별 매수 타점 목표가")
            st.write(f"- **1차 분할 매수 타점 (120일선 부근):** `{ma120_val:,.0f}` (현재 대비 {((ma120_val-curr_val)/curr_val)*100:+.1f}%)")
            st.write(f"- **2차 강력 매수 타점 (200일선 부근):** `{ma200_val:,.0f}` (현재 대비 {((ma200_val-curr_val)/curr_val)*100:+.1f}%)")
            st.info("💡 **전략 Tip:** 중장기 우상향 종목은 120일선 이하로 내려올 때 월간 적립금의 1.5배~2배를 매수하는 전략이 가장 높은 CAGR을 기록합니다.")
            
        with g2:
            st.markdown("#### 📋 ETF 기초체력 정보")
            st.write(f"- **티커 코드:** `{target_info['ticker']}`")
            st.write(f"- **운용 보수:** `{target_info['fee']}`")
            st.write(f"- **카테고리:** `{target_info['category']}`")
            if yf_info and 'totalAssets' in yf_info and yf_info['totalAssets']:
                st.write(f"- **순자산 총액 (AUM):** `{yf_info['totalAssets'] / 1e8:,.1f} 억`")

# ------------------------------------------
# TAB 3: 주봉/일봉 추세 분석 차트
# ------------------------------------------
with tab3:
    st.subheader(f"📈 {target_name} 기술적 추세 차트")
    
    chart_type = st.radio("차트 주기 선택:", ["일봉 (Daily) + 이동평균선", "주봉 (Weekly) 대세 추세"], horizontal=True)
    
    if df_d is not None and not df_d.empty:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        
        if "일봉" in chart_type:
            # 일봉 캔들차트 및 주요 이동평균선
            fig.add_trace(go.Candlestick(
                x=df_d.index, open=df_d['Open'], high=df_d['High'],
                low=df_d['Low'], close=df_d['Close'], name="주가(일봉)"
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(x=df_d.index, y=df_d['MA20'], line=dict(color='orange', width=1.5), name='20일선'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_d.index, y=df_d['MA50'], line=dict(color='blue', width=1.5), name='50일선'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_d.index, y=df_d['MA120'], line=dict(color='purple', width=2), name='120일선 (DCA Zone)'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_d.index, y=df_d['MA200'], line=dict(color='red', width=2.5), name='200일선 (장기지지)'), row=1, col=1)
            
            # RSI 하단 서브플롯
            fig.add_trace(go.Scatter(x=df_d.index, y=df_d['RSI'], line=dict(color='green', width=1.5), name='RSI(14)'), row=2, col=1)
            fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dot", line_color="blue", row=2, col=1)
            
        else:
            # 주봉 추세 차트
            fig.add_trace(go.Scatter(x=df_w.index, y=df_w['Close'], line=dict(color='black', width=2), name='주봉 종가'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_w.index, y=df_w['W_MA20'], line=dict(color='green', width=2), name='20주선 (중기추세)'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_w.index, y=df_w['W_MA60'], line=dict(color='red', width=2.5), name='60주선 (장기추세)'), row=1, col=1)
            
            # 주봉 MDD 서브플롯
            fig.add_trace(go.Scatter(x=df_d.index, y=df_d['Drawdown'], line=dict(color='crimson', width=1), name='MDD (%)'), row=2, col=1)

        fig.update_layout(
            height=650,
            template="plotly_dark",
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
