import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import urllib.request
import xml.etree.ElementTree as ET

# 1. 모바일 최적화 페이지 설정
st.set_page_config(
    page_title="ETF Technical Radar",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS
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

# 2. 관심종목 파일 저장/불러오기 기능
WATCHLIST_FILE = "watchlist.json"
DEFAULT_WATCHLIST = {
    "069500": "KODEX 200 (069500)",
    "091160": "KODEX 반도체 (091160)",
    "466920": "KODEX AI반도체핵심장비 (466920)",
    "395160": "KODEX AI반도체TOP2플러스 (395160)",
    "379800": "KODEX 미국S&P500 (379800)"
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
    df['MA5'] = df['Close'].rolling(5).mean()
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

# 네이버 증권 API로 실제 종목명 가져오기
def get_stock_name(code):
    try:
        url = f"https://m.stock.naver.com/api/stock/{code}/basic"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('stockName', f'ETF {code}')
    except Exception:
        return f"ETF {code}"

# 네이버 금융 주가 데이터 수집
def fetch_from_naver(code, count=500):
    try:
        url = f"https://fchart.stock.naver.com/sise.nhn?symbol={code}&timeframe=day&count={count}&requestType=0"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read().decode('euc-kr', errors='ignore')
        
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        
        rows = []
        for item in items:
            data_str = item.attrib.get('data', '')
            parts = data_str.split('|')
            if len(parts) >= 6:
                rows.append({
                    'Date': pd.to_datetime(parts[0]),
                    'Open': float(parts[1]),
                    'High': float(parts[2]),
                    'Low': float(parts[3]),
                    'Close': float(parts[4]),
                    'Volume': float(parts[5])
                })
        if not rows:
            return None
        df = pd.DataFrame(rows)
        df.set_index('Date', inplace=True)
        return df
    except Exception:
        return None

# 4. 데이터 로드
@st.cache_data(ttl=300, show_spinner=False)
def load_etf_data(ticker_code, period="1y"):
    clean_code = ''.join(filter(str.isdigit, str(ticker_code)))
    if not clean_code:
        clean_code = str(ticker_code).strip()

    df = fetch_from_naver(clean_code, count=500)
    
    if df is None or df.empty:
        for suffix in [".KS", ".KQ"]:
            ticker = f"{clean_code}{suffix}"
            try:
                data = yf.download(ticker, period=period, progress=False)
                if not data.empty and len(data) >= 5:
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.get_level_values(0)
                    df = data
                    break
            except Exception:
                pass

    if df is None or df.empty or len(df) < 5:
        return None, clean_code

    if period == "6m":
        df = df.iloc[-120:]
    elif period == "1y":
        df = df.iloc[-250:]
    elif period == "2y":
        df = df.iloc[-500:]

    df = calculate_indicators(df)
    return df, clean_code

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

if selected_option == "➕ 종목코드로 관심종목 추가":
    st.subheader("📝 종목코드 입력 등록")
    col_code, col_btn = st.columns([2, 1])
    
    with col_code:
        new_code = st.text_input("종목코드 입력", placeholder="예: 395160", label_visibility="collapsed")
    with col_btn:
        add_btn = st.button("⭐ 추가", use_container_width=True)
        
    if add_btn and new_code:
        clean_code = ''.join(filter(str.isdigit, str(new_code)))
        if not clean_code:
            st.error("숫자 종목코드를 정확히 입력해주세요.")
        else:
            test_df, _ = load_etf_data(clean_code, period="6m")
            if test_df is not None:
                stock_name = get_stock_name(clean_code)
                display_label = f"{stock_name} ({clean_code})"
                st.session_state.watchlist[clean_code] = display_label
                save_watchlist(st.session_state.watchlist)
                st.success(f"'{display_label}' 등록 완료!")
                st.rerun()
            else:
                st.error("유효하지 않은 종목코드이거나 데이터를 가져올 수 없습니다.")
    st.stop()
else:
    symbol_input = [k for k, v in watchlist.items() if v == selected_option][0]
    
    col_space, col_del = st.columns([3, 1])
    with col_del:
        if st.button("🗑 목록에서 삭제", use_container_width=True):
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
    
    rsi = float(df['RSI'].iloc[-1]) if 'RSI' in df and not pd.isna(df['RSI'].iloc[-1]) else 50.0
    ma5 = float(df['MA5'].iloc[-1]) if 'MA5' in df and not pd.isna(df['MA5'].iloc[-1]) else curr_price
    ma20 = float(df['MA20'].iloc[-1]) if 'MA20' in df and not pd.isna(df['MA20'].iloc[-1]) else curr_price
    ma60 = float(df['MA60'].iloc[-1]) if 'MA60' in df and not pd.isna(df['MA60'].iloc[-1]) else curr_price
    ma120 = float(df['MA120'].iloc[-1]) if 'MA120' in df and not pd.isna(df['MA120'].iloc[-1]) else curr_price
    macd = float(df['MACD'].iloc[-1]) if 'MACD' in df and not pd.isna(df['MACD'].iloc[-1]) else 0.0
    macd_sig = float(df['MACD_Signal'].iloc[-1]) if 'MACD_Signal' in df and not pd.isna(df['MACD_Signal'].iloc[-1]) else 0.0
    
    vol_ma20 = df['Vol_MA20'].iloc[-1] if 'Vol_MA20' in df and not pd.isna(df['Vol_MA20'].iloc[-1]) else 1.0
    vol_ratio = float(df['Volume'].iloc[-1] / vol_ma20) if vol_ma20 > 0 else 1.0
    
    bb_upper = float(df['BB_Upper'].iloc[-1]) if 'BB_Upper' in df and not pd.isna(df['BB_Upper'].iloc[-1]) else curr_price
    bb_lower = float(df['BB_Lower'].iloc[-1]) if 'BB_Lower' in df and not pd.isna(df['BB_Lower'].iloc[-1]) else curr_price
    
    trend_score = 0
    if curr_price > ma5: trend_score += 1
    if curr_price > ma20: trend_score += 1
    if ma20 > ma60: trend_score += 1
    
    status_text = "강한 상승" if trend_score == 3 else ("상승/조정" if trend_score == 2 else "하락/관망")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("현재가", f"{curr_price:,.0f}원", f"{chg_pct:+.2f}%")
    m2.metric("추세점수", f"{trend_score}/3", status_text)
    m3.metric("RSI (14)", f"{rsi:.1f}", "과열(>70)" if rsi > 70 else ("침체(<30)" if rsi < 30 else "중립"))
    m4.metric("거래량 비율", f"{vol_ratio:.2f}x", "급증(≥1.5)" if vol_ratio >= 1.5 else "평이")

    tab_chart, tab_scenario, tab_details = st.tabs(["📊 차트", "🎯 시나리오", "🔍 지표 분석"])

    with tab_chart:
        st.caption("💡 **차트 관전 포인트**: 노란색(5일선)과 주황색(20일선)의 지지 여부 및 하단 MACD 모멘텀 확인")
        
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.03, row_heights=[0.55, 0.2, 0.25])

        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                                     low=df['Low'], close=df['Close'], name="주가"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], line=dict(color='yellow', width=1), name="MA5"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='orange', width=1), name="MA20"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], line=dict(color='green', width=1), name="MA60"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA120'], line=dict(color='purple', width=1), name="MA120"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='gray', dash='dot'), name="BB상단"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='gray', dash='dot'), name="BB하단"), row=1, col=1)

        colors = ['red' if c >= o else 'blue' for c, o in zip(df['Close'], df['Open'])]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="거래량"), row=2, col=1)

        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='blue'), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], line=dict(color='red'), name="Signal"), row=3, col=1)

        # dragmode=False로 설정하여 모바일 터치 시 차트가 확대되거나 화면 밖으로 이탈하는 현상 방지
        fig.update_layout(
            height=550, 
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_rangeslider_visible=False, 
            template="plotly_dark", 
            showlegend=False,
            dragmode=False
        )
        
        st.plotly_chart(
            fig, 
            use_container_width=True, 
            key=f"chart_{symbol_input}_{period}",
            config={
                'responsive': True,
                'scrollZoom': False,
                'displayModeBar': False,
                'doubleClick': False
            }
        )

    with tab_scenario:
        recent_60 = df.iloc[-60:] if len(df) >= 60 else df
        r1 = float(recent_60['High'].max())
        s1 = float(recent_60['Low'].min())
        
        st.subheader("📌 지지 & 저항 가격대")
        c_sup, c_res = st.columns(2)
        c_sup.info(f"**1차 지지선 (20일선 기준)**\n\n### {ma20:,.0f} 원")
        c_res.warning(f"**1차 저항선 (전고점 기준)**\n\n### {r1:,.0f} 원")

        st.subheader("💡 보조지표 기반 대응 시나리오")
        
        if rsi >= 70:
            st.warning("🟡 **[단기 과열 경계 시나리오 (RSI > 70)]**\n\n보조지표 RSI가 70 이상으로 과열권입니다. 신규 추격 매수보다는 분할 차익실현 및 20일선 지지 확인이 유효합니다.")
        elif macd > macd_sig and curr_price > ma20 and vol_ratio >= 1.3:
            st.success("🟢 **[거래량 동반 돌파 시나리오 (MACD+ / 거래량 상승)]**\n\nMACD가 골든크로스를 유지하며 20일 이동평균선 및 거래량이 수반되고 있습니다. 저항대 돌파 시 추가 시세 분출이 기대되는 구간입니다.")
        elif curr_price >= ma20 and rsi < 65:
            st.success(f"🟢 **[상승 추세 속 눌림목 매수 시나리오 (20일선 수호 / RSI 중립)]**\n\n20일선({ma20:,.0f}원) 지지력을 유지 중이며 RSI가 50~60 수준으로 부담 없는 위치입니다. 20일선 부근까지 눌릴 때 분할 접근이 유리합니다.")
        elif curr_price < ma20 and curr_price >= bb_lower:
            st.info("🔵 **[단기 조정 및 관망 시나리오 (20일선 이탈)]**\n\n20일 이동평균선을 하회하고 있으므로 볼린저 밴드 하단 및 MACD 반등 여부를 먼저 확인해야 합니다.")
        else:
            st.error("🔴 **[추세 이탈 경고 시나리오 (역배열 진행)]**\n\n주요 이평선 하회 및 MACD 음전이 지속되고 있습니다. 거래량을 동반한 반등 신호 전까지는 관망을 권장합니다.")

    with tab_details:
        st.markdown("### 🔍 보조지표 핵심 분석 종합")
        
        bb_denom = (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 1
        bb_pos = ((curr_price - bb_lower) / bb_denom) * 100
        
        ma_status = "이동평균선 정배열 (강한 상승 추세)" if (curr_price > ma5 > ma20 > ma60) else ("20일선 상회 (단기 우상향)" if curr_price > ma20 else "20일선 하회 (조정세)")
        rsi_status = f"{rsi:.1f} - 과열권 (>70)" if rsi >= 70 else (f"{rsi:.1f} - 침체권 (<30)" if rsi <= 30 else f"{rsi:.1f} - 중립~강세 (50~65)")
        macd_status = "골든크로스 (상승 모멘텀)" if macd > macd_sig else "데드크로스 (약세 모멘텀)"
        bb_status = f"밴드 내 {bb_pos:.0f}% 위치 ({'상단 부근 이탈 경계' if bb_pos > 85 else ('하단 부근 지지 테스트' if bb_pos < 15 else '중앙권 이격 평이')})"
        vol_status = f"20일 평균 대비 {vol_ratio*100:.0f}% ({'거래량 수반 상승' if vol_ratio >= 1.3 else '거래량 소강 상태'})"

        details_df = pd.DataFrame({
            "보조지표": ["이동평균선 (MA)", "RSI (14)", "MACD / Signal", "볼린저 밴드", "거래량 (Volume)"],
            "현재 수치": [
                f"현재가: {curr_price:,.0f}원 (5일: {ma5:,.0f} / 20일: {ma20:,.0f})",
                f"{rsi:.1f}",
                f"MACD: {macd:+.1f} / Signal: {macd_sig:+.1f}",
                f"상단: {bb_upper:,.0f}원 / 하단: {bb_lower:,.0f}원",
                f"20일 평균 대비 {vol_ratio:.2f}배"
            ],
            "핵심 해석 및 시그널": [ma_status, rsi_status, macd_status, bb_status, vol_status]
        })
        st.table(details_df)
