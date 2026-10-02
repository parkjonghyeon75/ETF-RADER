import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os

# ==========================================
# 0. 페이지 기본 설정 및 스타일링
# ==========================================
st.set_page_config(
    page_title="ETF Technical Radar & Gem Finder v5",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background-color: #1e222d;
        border-radius: 8px;
        padding: 12px 16px;
        border: 1px solid #2a2e39;
        margin-bottom: 10px;
    }
    .badge-dc {
        background-color: #1b5e20;
        color: #a5d6a7;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    .stTable { font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DC 퇴직연금 투자 가능 주요 ETF 데이터베이스
# ==========================================
DC_ETF_DATABASE = {
    # [미국 대표지수 / 배당]
    "TIGER 미국S&P500": {"ticker": "360750.KS", "category": "미국지수", "fee": "0.07%", "dc": True},
    "ACE 미국나스닥100": {"ticker": "368590.KS", "category": "미국지수", "fee": "0.07%", "dc": True},
    "KODEX 미국S&P500TR": {"ticker": "379800.KS", "category": "미국지수", "fee": "0.05%", "dc": True},
    "SOL 미국배당다우존스": {"ticker": "429000.KS", "category": "배당/성장", "fee": "0.05%", "dc": True},
    "TIGER 미국배당다우존스": {"ticker": "423160.KS", "category": "배당/성장", "fee": "0.01%", "dc": True},
    
    # [테크 / 반도체 / AI]
    "KODEX 미국반도체MV": {"ticker": "381180.KS", "category": "반도체/AI", "fee": "0.09%", "dc": True},
    "TIGER 미국필라델피아반도체나스닥": {"ticker": "381180.KS", "category": "반도체/AI", "fee": "0.49%", "dc": True},
    "TIGER 미국테크TOP10 INDXX": {"ticker": "381170.KS", "category": "빅테크", "fee": "0.49%", "dc": True},
    "ACE 미국빅테크TOP7 Plus": {"ticker": "465580.KS", "category": "빅테크", "fee": "0.30%", "dc": True},
    
    # [국내 지수 / 대표 테마]
    "KODEX 200": {"ticker": "069500.KS", "category": "국내지수", "fee": "0.15%", "dc": True},
    "TIGER 200": {"ticker": "102110.KS", "category": "국내지수", "fee": "0.05%", "dc": True},
    "KODEX 2차전지산업": {"ticker": "305720.KS", "category": "2차전지", "fee": "0.45%", "dc": True},
    "KODEX K-로봇active": {"ticker": "426410.KS", "category": "로봇/AI", "fee": "0.50%", "dc": True},
    "TIGER K-반도체": {"ticker": "396500.KS", "category": "국내반도체", "fee": "0.45%", "dc": True},
    
    # [채권 / 리츠 / 안정형]
    "ACE 미국30년국채액티브(H)": {"ticker": "453850.KS", "category": "해외채권", "fee": "0.05%", "dc": True},
    "KODEX KOFR금리액티브(합성)": {"ticker": "423160.KS", "category": "파킹/금리", "fee": "0.03%", "dc": True},
    "TIGER 리츠부동산인프라": {"ticker": "329200.KS", "category": "리츠/배당", "fee": "0.29%", "dc": True},
}

# ==========================================
# 2. 데이터 수집 및 지표 연산 엔진
# ==========================================
@st.cache_data(ttl=3600)
def fetch_etf_data(ticker_symbol, period="2y"):
    """yfinance를 통한 일봉 및 주봉 지표 연산"""
    try:
        etf = yf.Ticker(ticker_symbol)
        df = etf.history(period=period)
        if df.empty:
            return None, None
        
        # --- 일봉 지표 ---
        df['MA5'] = df['Close'].rolling(window=5).mean()
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
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal']
        
        # 이격도 & MDD
        df['Disparity_120'] = (df['Close'] / df['MA120']) * 100
        rolling_max = df['Close'].rolling(window=252, min_periods=1).max()
        df['Drawdown'] = (df['Close'] - rolling_max) / rolling_max * 100

        # --- 주봉 지표 ---
        df_weekly = df['Close'].resample('W').last().to_frame()
        df_weekly['W_MA20'] = df_weekly['Close'].rolling(window=20).mean()
        df_weekly['W_MA60'] = df_weekly['Close'].rolling(window=60).mean()

        return df, df_weekly
    except Exception:
        return None, None

def evaluate_gem_score(df_daily, df_weekly):
    """중장기 원석 ETF 판별 스코어링 엔진 (100점 만점)"""
    if df_daily is None or len(df_daily) < 200 or df_weekly is None or len(df_weekly) < 60:
        return 0, "데이터 부족", {}

    last_d = df_daily.iloc[-1]
    last_w = df_weekly.iloc[-1]
    
    score = 0
    details = {}
    
    # 1. 주봉 20주선 > 60주선 정배열 (30점)
    if last_w['W_MA20'] > last_w['W_MA60']:
        score += 30
        details['주봉추세'] = "대세 우상향"
    else:
        details['주봉추세'] = "조정/역배열"
        
    # 2. 200일선 상회 지지 여부 (20점)
    if last_d['Close'] > last_d['MA200']:
        score += 20
        details['장기지지'] = "200일선 상회"
    else:
        details['장기지지'] = "200일선 하회"
        
    # 3. 52주 최고가 대비 적정 눌림목 (20점)
    high_52w = df_daily['Close'].tail(252).max()
    pullback = ((last_d['Close'] - high_52w) / high_52w) * 100
    details['52주이격'] = f"{pullback:.1f}%"
    
    if -15 <= pullback <= -3:
        score += 20
        details['매수타점'] = "적립식 최적 눌림목"
    elif -3 < pullback <= 0:
        score += 10
        details['매수타점'] = "신고가 부근 (분할매수)"
    else:
        score += 5
        details['매수타점'] = "과도한 낙폭/소외"
        
    # 4. RSI 모멘텀 (15점)
    rsi = last_d['RSI']
    details['RSI'] = f"{rsi:.1f}"
    if 40 <= rsi <= 60:
        score += 15
    elif 30 <= rsi < 40:
        score += 10
    else:
        score += 5
        
    # 5. MDD 변동성 (15점)
    mdd = last_d['Drawdown']
    details['MDD'] = f"{mdd:.1f}%"
    if mdd > -15:
        score += 15
    elif mdd > -25:
        score += 10
    else:
        score += 5

    # 등급 결정
    if score >= 80:
        grade = "💎💎💎 (S급 원석)"
    elif score >= 65:
        grade = "💎💎 (A급 우량)"
    elif score >= 50:
        grade = "💎 (B급 관망)"
    else:
        grade = "⚠️ (C급 주의)"

    return score, grade, details

# ==========================================
# 3. 데이터 저장 관리 (테마/관점 메모장)
# ==========================================
THEME_FILE = "theme_info.json"

def load_theme_info():
    if os.path.exists(THEME_FILE):
        with open(THEME_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_theme_info(data):
    with open(THEME_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

theme_db = load_theme_info()

# ==========================================
# 4. 사이드바 구성
# ==========================================
st.sidebar.title("📡 ETF Radar v5")
st.sidebar.caption("DC 퇴직연금 원석찾기 & 기술적 분석")

# 분석 대상 설정
st.sidebar.subheader("📌 종목 선택")
selected_etf_name = st.sidebar.selectbox(
    "개별 상세 분석 종목:",
    options=list(DC_ETF_DATABASE.keys())
)

# 커스텀 티커 추가
st.sidebar.markdown("---")
st.sidebar.subheader("➕ 사용자 종목 추가")
custom_ticker = st.sidebar.text_input("yfinance 티커 (예: 005930.KS)").strip().upper()
custom_name = st.sidebar.text_input("종목명").strip()

if st.sidebar.button("종목 추가하기"):
    if custom_ticker and custom_name:
        DC_ETF_DATABASE[custom_name] = {"ticker": custom_ticker, "category": "사용자추가", "fee": "N/A", "dc": True}
        st.sidebar.success(f"'{custom_name}' 추가 완료!")
    else:
        st.sidebar.warning("티커와 종목명을 모두 입력해주세요.")

# ==========================================
# 5. 메인 화면 - 탭 레이아웃
# ==========================================
st.title("📡 ETF Technical Radar & DC Gem Finder")

tab_gem, tab_chart, tab_theme, tab_guide = st.tabs([
    "🔍 1. DC 퇴직연금 원석찾기",
    "📈 2. 개별 ETF 정밀 기술적 분석",
    "💡 3. 테마 & 관점 메모장",
    "📘 4. 보조지표 가이드"
])

# ------------------------------------------
# TAB 1: DC 퇴직연금 원석찾기 (신규 기능)
# ------------------------------------------
with tab_gem:
    st.subheader("🔍 DC 퇴직연금 투자 가능 ETF '원석' 스크리너")
    st.write("DC/IRP 퇴직연금 계좌에서 매수 가능한 전체 우량 ETF 중 **장기 우상향 추세(주봉 정배열 + 200일선 지지 + 적정 눌림목)**를 갖춘 보석 종목을 자동 검색합니다.")
    
    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        category_filter = st.multiselect(
            "카테고리 필터:",
            options=list(set(info['category'] for info in DC_ETF_DATABASE.values())),
            default=list(set(info['category'] for info in DC_ETF_DATABASE.values()))
        )
        
    if st.button("🚀 원석 종목 전체 스캔 실행"):
        st.cache_data.clear()

    gem_results = []
    progress_bar = st.progress(0)
    
    filtered_items = [item for item in DC_ETF_DATABASE.items() if item[1]['category'] in category_filter]
    
    for idx, (name, info) in enumerate(filtered_items):
        df_d, df_w = fetch_etf_data(info['ticker'])
        if df_d is not None and not df_d.empty:
            score, grade, details = evaluate_gem_score(df_d, df_w)
            last_p = df_d['Close'].iloc[-1]
            disp_120 = df_d['Disparity_120'].iloc[-1]
            
            gem_results.append({
                "원석 등급": grade,
                "종목명": name,
                "카테고리": info['category'],
                "원석 점수": score,
                "현재가": f"{last_p:,.0f}원" if ".KS" in info['ticker'] else f"${last_p:,.2f}",
                "주봉 추세": details.get('주봉추세', '-'),
                "120일선 이격도": f"{disp_120:.1f}%",
                "52주 최고 대비": details.get('52주이격', '-'),
                "매수 평가": details.get('매수타점', '-'),
                "총보수": info['fee'],
                "DC투자가능": "✅ 가능" if info['dc'] else "❌ 불가"
            })
        progress_bar.progress((idx + 1) / len(filtered_items))
    progress_bar.empty()

    if gem_results:
        res_df = pd.DataFrame(gem_results).sort_values(by="원석 점수", ascending=False).reset_index(drop=True)
        
        top_item = res_df.iloc[0]
        st.markdown(f"""
        <div class="metric-card">
            <h4>🏆 오늘의 TOP DC 퇴직연금 원석: <span style="color:#4caf50;">{top_item['종목명']}</span> ({top_item['원석 점수']}점)</h4>
            <p><b>평가:</b> {top_item['원석 등급']} | <b>매수 가이드:</b> {top_item['매수 평가']} | <b>120일 이격도:</b> {top_item['120일선 이격도']} | <b>총보수:</b> {top_item['총보수']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.dataframe(res_df, use_container_width=True, height=450)
    else:
        st.info("스크리닝 버튼을 누르거나 필터 조건을 확인해주세요.")

# ------------------------------------------
# TAB 2: 개별 ETF 정밀 기술적 분석 (원래 앱 기능 100% 보존)
# ------------------------------------------
with tab_chart:
    st.subheader(f"📈 {selected_etf_name} 정밀 차트 및 매매 시나리오")
    
    target_info = DC_ETF_DATABASE[selected_etf_name]
    df_d, df_w = fetch_etf_data(target_info['ticker'])
    
    if df_d is not None and not df_d.empty:
        last_d = df_d.iloc[-1]
        prev_d = df_d.iloc[-2]
        
        price_diff = last_d['Close'] - prev_d['Close']
        price_ratio = (price_diff / prev_d['Close']) * 100
        
        # 핵심 메트릭 지표
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("현재가", f"{last_d['Close']:,.0f}원" if ".KS" in target_info['ticker'] else f"${last_d['Close']:,.2f}", f"{price_ratio:+.2f}%")
        m2.metric("20일 이동평균선", f"{last_d['MA20']:,.0f}원" if ".KS" in target_info['ticker'] else f"${last_d['MA20']:,.2f}")
        m3.metric("120일선 (DCA Zone)", f"{last_d['MA120']:,.0f}원" if ".KS" in target_info['ticker'] else f"${last_d['MA120']:,.2f}")
        m4.metric("RSI (14)", f"{last_d['RSI']:.1f}")
        m5.metric("MACD 히스토그램", f"{last_d['MACD_Hist']:.2f}")

        # 기술적 차트 생성 (Candlestick + Volume + RSI + MACD)
        fig = make_subplots(
            rows=3, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.03, 
            row_heights=[0.55, 0.2, 0.25]
        )
        
        # 주가 캔들차트 및 이동평균선
        fig.add_trace(go.Candlestick(
            x=df_d.index, open=df_d['Open'], high=df_d['High'],
            low=df_d['Low'], close=df_d['Close'], name="주가"
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df_d.index, y=df_d['MA5'], line=dict(color='gray', width=1), name='5일선'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_d.index, y=df_d['MA20'], line=dict(color='orange', width=1.5), name='20일선'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_d.index, y=df_d['MA60'] if 'MA60' in df_d else df_d['MA50'], line=dict(color='blue', width=1.5), name='50/60일선'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_d.index, y=df_d['MA120'], line=dict(color='purple', width=2), name='120일선'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_d.index, y=df_d['MA200'], line=dict(color='red', width=2), name='200일선'), row=1, col=1)

        # 거래량
        colors = ['red' if c >= o else 'blue' for c, o in zip(df_d['Close'], df_d['Open'])]
        fig.add_trace(go.Bar(x=df_d.index, y=df_d['Volume'], marker_color=colors, name="거래량"), row=2, col=1)

        # MACD
        fig.add_trace(go.Scatter(x=df_d.index, y=df_d['MACD'], line=dict(color='blue', width=1), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_d.index, y=df_d['Signal'], line=dict(color='orange', width=1), name="Signal"), row=3, col=1)
        fig.add_trace(go.Bar(x=df_d.index, y=df_d['MACD_Hist'], name="Hist"), row=3, col=1)

        fig.update_layout(height=700, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        # 원래 앱의 단기/스윙 대응 시나리오 제공
        st.markdown("### 🎯 쉽게 풀어쓴 매매 대응 전략 (원래 기능)")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🟢 매수 관점 (Support & Dip)")
            if last_d['Close'] <= last_d['MA20']:
                st.write("- **20일선 하회 구간:** 단기 눌림목 형성 중. 분할 매수 1차 타점 고려 가능.")
            if last_d['RSI'] <= 40:
                st.write("- **RSI 저평가 (40 이하):** 과매도 구간 진입. 반등 가능성 상승.")
            st.write(f"- **1차 주요 지지선 (120일선):** `{last_d['MA120']:,.0f}원` 부근 적립식 매수 유효")
            
        with c2:
            st.markdown("#### 🔴 매도/리스크 관리 관점 (Resistance)")
            if last_d['RSI'] >= 65:
                st.write("- **RSI 과열 (65 이상):** 단기 고점 신호. 신규 추격 매수 자제 필요.")
            if last_d['MACD_Hist'] < 0:
                st.write("- **MACD 음전:** 단기 조정 모멘텀 지속 중.")
            st.write(f"- **손절/리스크 기준선 (200일선):** `{last_d['MA200']:,.0f}원` 이탈 시 비중 축소 권장")

# ------------------------------------------
# TAB 3: 테마 & 관점 메모장 (원래 앱 기능 100% 보존)
# ------------------------------------------
with tab_theme:
    st.subheader(f"💡 {selected_etf_name} 테마 분석 및 개인 관점 기록")
    
    current_note = theme_db.get(selected_etf_name, "")
    
    with st.form("theme_form"):
        user_note = st.text_area("해당 ETF에 대한 투자 아이디어, 주요 구성종목, 테마 이슈 작성:", value=current_note, height=200)
        submitted = st.form_submit_button("💾 메모 저장하기")
        
        if submitted:
            theme_db[selected_etf_name] = user_note
            save_theme_info(theme_db)
            st.success("관점 메모가 안전하게 저장되었습니다.")

    st.markdown("---")
    st.markdown("#### 📋 기본 등록된 테마 및 ETF 특징 요약")
    info = DC_ETF_DATABASE[selected_etf_name]
    st.write(f"- **카테고리:** {info['category']}")
    st.write(f"- **총보수율:** {info['fee']}")
    st.write(f"- **DC 퇴직연금 투자 여부:** {'가능' if info['dc'] else '불가'}")

# ------------------------------------------
# TAB 4: 보조지표 가이드 (원래 앱 기능 100% 보존)
# ------------------------------------------
with tab_guide:
    st.subheader("📘 지표 쉬운 설명서")
    
    st.markdown("""
    ### 1. 이동평균선 (Moving Average)
    * **20일선 (황색):** 단기 추세선. 주가가 20일선 위에 있으면 단기 우상향.
    * **120일선 (보라색):** 중기 수급선 / 적립식 매수 타점 (DCA Zone).
    * **200일선 (적색):** 장기 대세선. 주가가 200일선 아래로 무너지면 장기 침체 가능성.

    ---

    ### 2. RSI (상대강도지수)
    * **70 이상:** 과매수 (단기 고점 위험, 분할 매도 고려)
    * **30 이하:** 과매도 (단기 바닥 가능성, 분할 매수 고려)
    * **40 ~ 60:** 적정 상승 추세 유지 구간

    ---

    ### 3. DC 퇴직연금 투자 팁
    * **레버리지/인버스 금지:** 퇴직연금법상 2배 레버리지나 인버스 상품은 투자할 수 없습니다.
    * **장기 우상향 종목 선택:** 120일선/200일선 지지를 받으면서 주봉이 정배열된 종목 위주로 모아가는 것이 안정적입니다.
    """)
