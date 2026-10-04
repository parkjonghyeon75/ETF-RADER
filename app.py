import streamlit as st
import pandas as pd
import numpy as np
import datetime

# ============================================================
# PAGE CONFIG & STYLING
# ============================================================
st.set_page_config(
    page_title="ETF & Future Theme Investment Radar",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .app-title { font-size: 1.8rem; font-weight: 800; color: #1e293b; margin-bottom: 0.2rem; }
    .app-subtitle { font-size: 0.95rem; color: #64748b; margin-bottom: 1.5rem; }
    .section-title { font-size: 1.2rem; font-weight: 700; color: #0f172a; margin-top: 1.5rem; margin-bottom: 0.8rem; }
    .positive { color: #ef4444; }
    .negative { color: #3b82f6; }
    .neutral { color: #64748b; }
    
    .stage-core { background-color: #fee2e2; color: #991b1b; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.8rem; }
    .stage-next { background-color: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.8rem; }
    .stage-interest { background-color: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.8rem; }

    .decision-board {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .decision-board-head {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 12px;
        margin-bottom: 12px;
    }
    .decision-kicker { font-size: 0.75rem; font-weight: 700; color: #64748b; letter-spacing: 0.05em; }
    .decision-title { font-size: 1.1rem; font-weight: 800; color: #0f172a; }
    .decision-market { text-align: right; font-size: 0.85rem; color: #334155; }
    .decision-name { font-size: 1.1rem; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
    .decision-meta { font-size: 0.85rem; color: #64748b; margin-bottom: 10px; }
    .decision-state { font-size: 1rem; font-weight: 800; color: #0f172a; margin-bottom: 6px; }
    .decision-desc { font-size: 0.9rem; color: #334155; margin-bottom: 14px; line-height: 1.4; }
    .decision-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        background: #ffffff;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 10px;
        font-size: 0.85rem;
    }
    .decision-grid span { color: #64748b; display: block; font-size: 0.75rem; }
    .decision-grid b { color: #0f172a; font-size: 0.9rem; }
    .decision-price-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        background: #ffffff;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 14px;
        font-size: 0.85rem;
    }
    .decision-price-row span { color: #64748b; display: block; font-size: 0.75rem; }
    .decision-price-row b { color: #0f172a; font-size: 0.9rem; }
    .decision-next { font-size: 0.9rem; color: #0f172a; margin-bottom: 8px; }
    .decision-invalid { font-size: 0.8rem; color: #64748b; background: #f1f5f9; padding: 8px 12px; border-radius: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# STATE INITIALIZATION
# ============================================================
def init_state():
    if "main_page" not in st.session_state:
        st.session_state.main_page = "📊 내 ETF"
    if "future_detail_theme" not in st.session_state:
        st.session_state.future_detail_theme = None
    if "future_detail_code" not in st.session_state:
        st.session_state.future_detail_code = None


# ============================================================
# UTILS & MOCK DATA LOADERS
# ============================================================
def safe_float(val, default=0.0):
    try:
        return float(val)
    except:
        return default


def money(val):
    return f"{val:,.0f}원" if not pd.isna(val) else "0원"


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@st.cache_data
def load_price_data(code):
    # 가상의 가격 데이터를 생성하는 Mock 함수 (실제 환경에서는 yfinance나 pykrx 연동 가능)
    np.random.seed(hash(code) % 2**32)
    dates = pd.date_range(end=datetime.date.today(), periods=100, freq="B")
    base_price = 10000 + (hash(code) % 50000)
    returns = np.random.normal(0.0005, 0.015, len(dates))
    prices = base_price * np.cumprod(1 + returns)
    volumes = np.random.randint(10000, 500000, len(dates))
    
    df = pd.DataFrame({
        "Date": dates,
        "Close": prices,
        "Open": prices * (1 + np.random.normal(0, 0.005, len(dates))),
        "High": prices * (1 + abs(np.random.normal(0.005, 0.005, len(dates)))),
        "Low": prices * (1 - abs(np.random.normal(0.005, 0.005, len(dates)))),
        "Volume": volumes
    })
    df.set_index("Date", inplace=True)
    return df


def calculate_indicators(df):
    if df.empty or len(df) < 20:
        return pd.DataFrame()
    d = df.copy()
    d["MA20"] = d["Close"].rolling(20).mean()
    d["MA60"] = d["Close"].rolling(60).mean()
    
    delta = d["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    d["RSI14"] = 100 - (100 / (1 + rs))
    
    vol_ma20 = d["Volume"].rolling(20).mean()
    d["VR"] = d["Volume"] / vol_ma20
    return d.dropna()


def get_etf_name(code):
    names = {
        "069500": "KODEX 200",
        "229200": "KODEX 코스닥150",
        "379800": "KODEX 미국S&P500",
        "379810": "KODEX 미국나스닥100",
        "463230": "TIGER 반도체TOP10",
        "449170": "KODEX AI반도체핵심공정",
        "446770": "TIGER 2차전지소재",
        "462910": "KODEX 조선부품"
    }
    return names.get(code, f"종목코드 {code}")


# ============================================================
# FUTURE THEME ENGINE
# ============================================================
def build_future_theme_engine(force=False):
    return {
        "chain": [
            ("AI 반도체 및 고성능 컴퓨팅", "현재 주도"),
            ("차세대 2차전지 및 소재", "다음 수혜"),
            ("스마트 조선 및 자율운항", "관심 확대")
        ],
        "details": {
            "AI 반도체 및 고성능 컴퓨팅": {
                "score": 88.5,
                "stage": "현재 주도",
                "reason": "글로벌 빅테크 투자 확대 및 HBM 수요 급증에 따른 실적 모멘텀 지속",
                "rows": [
                    {"code": "463230", "name": "TIGER 반도체TOP10", "ret20": 8.5},
                    {"code": "449170", "name": "KODEX AI반도체핵심공정", "ret20": 11.2}
                ]
            },
            "차세대 2차전지 및 소재": {
                "score": 74.0,
                "stage": "다음 수혜",
                "reason": "가격 바닥 다지기 이후 신기술(전고체 등) 기대감 유입",
                "rows": [
                    {"code": "446770", "name": "TIGER 2차전지소재", "ret20": 3.1}
                ]
            },
            "스마트 조선 및 자율운항": {
                "score": 69.2,
                "stage": "관심 확대",
                "reason": "수주 잔고 기반 안정적 실적 및 친환경 선박 교체 사이클 도래",
                "rows": [
                    {"code": "462910", "name": "KODEX 조선부품", "ret20": 5.4}
                ]
            }
        }
    }


def future_theme_info(theme):
    engine = build_future_theme_engine()
    return engine.get("details", {}).get(theme, {})


def stage2_rank_theme_etfs(theme):
    info = future_theme_info(theme)
    rows = info.get("rows", [])
    result = []
    for idx, r in enumerate(rows):
        result.append({
            "rank": idx + 1,
            "code": r["code"],
            "name": r["name"],
            "rank_score": 80 - (idx * 5)
        })
    return result


# ============================================================
# RENDER MODULES: STAGES & DETAILS
# ============================================================
def render_stage1_integrated_decision(theme, stage, d):
    row = d.iloc[-1]
    current = safe_float(row["Close"])
    ma20 = safe_float(row["MA20"])
    
    st.markdown("#### 1단계 · 테마 및 구조적 위치 분석")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("테마 스테이지", stage)
    with col2:
        st.metric("현재가 vs 20일선", f"{(current - ma20) / ma20 * 100:+.2f}%")
    with col3:
        st.metric("RSI (14)", f"{safe_float(row['RSI14']):.1f}")


def render_stage2_integrated(theme, d):
    st.markdown("#### 2단계 · 타이밍 및 기술적 검증")
    row = d.iloc[-1]
    st.write(f"- **거래량 비율 (VR)**: {safe_float(row['VR']):.2f}배 (20일 평균 대비)")
    st.write(f"- **추세 판단**: 60일선 대비 {'정배열(상승추세)' if safe_float(row['Close']) > safe_float(row['MA60']) else '조정/횡보'}")


def stage3_final_decision(theme, d):
    row = d.iloc[-1]
    current = safe_float(row["Close"])
    ma20 = safe_float(row["MA20"])
    ma60 = safe_float(row["MA60"])
    rsi = safe_float(row["RSI14"])
    vr = safe_float(row["VR"])
    
    theme_info = future_theme_info(theme)
    theme_score = safe_float(theme_info.get("score"), 75)
    
    ranked = stage2_rank_theme_etfs(theme)
    rank = ranked[0]["rank"] if ranked else 1
    rank_score = ranked[0]["rank_score"] if ranked else 75
    
    theme_part = theme_score
    trend_part = 85 if current > ma20 else 60
    momentum_part = min(max(rsi * 1.2, 40), 100)
    rank_part = max(100 - (rank - 1) * 15, 50)
    
    timing = {
        "timing": "1차 매수 검토" if current >= ma20 else "돌파 확인",
        "first": current * 0.98,
        "second": ma20,
        "breakout": current * 1.02,
        "risk": ma60
    }

    confidence = theme_part * 0.30 + trend_part * 0.25 + momentum_part * 0.20 + rank_part * 0.15 + 70 * 0.10

    if confidence >= 72:
        state = "강한 매수 우위"
        summary = "테마 강도와 ETF 상대순위, 추세와 모멘텀이 모두 양호합니다. 20일선 부근 눌림을 활용한 분할 접근이 유리합니다."
        action = "20일선 눌림 분할매수 · 추세 추종"
    elif confidence >= 60:
        state = "상승 추세 유지"
        summary = "중기 추세와 테마 흐름은 유효합니다. 다만 현재가 추격보다는 1차 관심 가격대까지의 조정을 기다리는 전략이 적합합니다."
        action = "눌림 대기 · 분할 접근"
    elif confidence >= 48:
        state = "방향 확인 구간"
        summary = "테마 흐름은 남아 있으나 개별 ETF의 단기 모멘텀이 다소 정체되어 있습니다. 지지 확인 전까지 진입을 서두르지 않습니다."
        action = "보유 관찰 · 신규 보류"
    else:
        state = "방어 우선"
        summary = "테마 및 가격 추세가 약세로 전환되었습니다. 신규 매수보다 지지선 이탈 여부와 리스크 관리를 우선합니다."
        action = "신규 중단 · 지지 회복 확인"

    st.markdown(
        f"""
        <div class="decision-board">
            <div class="decision-board-head">
                <div>
                    <div class="decision-kicker">FUTURE THEME & STRATEGY SYNTHESIS</div>
                    <div class="decision-title">종합 투자 판단보드</div>
                </div>
                <div class="decision-market">테마종합점수 <b>{theme_score:.0f}점</b><br>전략확신도 <b>{confidence:.0f}%</b></div>
            </div>
            <div class="decision-main">
                <div class="decision-state">{esc(state)}</div>
                <div class="decision-desc">{esc(summary)}</div>
                <div class="decision-grid">
                    <div><span>현재가</span><b>{money(current)}</b></div>
                    <div><span>20일선</span><b>{money(ma20)}</b></div>
                    <div><span>60일선</span><b>{money(ma60)}</b></div>
                    <div><span>RSI / 거래량</span><b>{rsi:.1f} / {vr:.2f}배</b></div>
                </div>
                <div class="decision-price-row">
                    <div><span>1차 관심가</span><b>{money(timing["first"])}</b></div>
                    <div><span>핵심 지지가</span><b>{money(timing["second"])}</b></div>
                    <div><span>돌파 기준가</span><b>{money(timing["breakout"])}</b></div>
                    <div><span>위험 가격</span><b style="color:#ef6678">{money(timing["risk"])}</b></div>
                </div>
                <div class="decision-next"><b>권장 대응전략:</b> {esc(action)}</div>
                <div class="decision-invalid"><b>무효화 기준(Stop/Wait):</b> 현재가가 핵심 지지 및 위험 가격({money(timing["risk"])}) 아래로 이탈할 경우 기존 가설을 무효화하고 리스크 관리에 들어갑니다.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_chart(d):
    st.line_chart(d[["Close", "MA20", "MA60"]])


def render_future_detail():
    theme = st.session_state.future_detail_theme
    code = st.session_state.future_detail_code
    if not theme or not code:
        st.info("선택된 미래테마 종목이 없습니다.")
        if st.button("미래테마 화면으로 돌아가기"):
            st.session_state.main_page = "🚀 미래테마"
            st.rerun()
        return

    name = get_etf_name(code)
    df = load_price_data(code)

    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("← 돌아가기", use_container_width=True):
            st.session_state.main_page = "🚀 미래테마"
            st.session_state.future_detail_code = None
            st.session_state.future_detail_theme = None
            st.rerun()
    with c2:
        st.markdown(f"### {theme} · {name} ({code})")

    if df.empty:
        st.error("가격 데이터를 불러오지 못했습니다.")
        return

    d = calculate_indicators(df)
    if d.empty:
        st.error("지표를 계산하지 못했습니다.")
        return

    info = future_theme_info(theme)
    stage = info.get("stage", "관심 확대")

    tab1, tab2, tab3, tab4 = st.tabs(["1단계 종합판단", "2단계 타이밍·검증", "3단계 최종대응", "가격차트"])

    with tab1:
        render_stage1_integrated_decision(theme, stage, d)
        st.markdown(f"**테마 설명:** {info.get('reason', '')}")
    with tab2:
        render_stage2_integrated(theme, d)
    with tab3:
        stage3_final_decision(theme, d)
    with tab4:
        st.markdown(f"### {name} 차트")
        render_chart(d)


def render_future_theme_page():
    st.markdown('<div class="app-title">🚀 미래테마 RADAR</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">시장에서 자금이 유입되는 유망 테마와 대표 ETF를 자동 발굴하고 다차원으로 분석합니다.</div>', unsafe_allow_html=True)

    engine_data = build_future_theme_engine()
    chain = engine_data.get("chain", [])
    details = engine_data.get("details", {})

    if not chain:
        st.info("조건에 부합하는 테마가 없습니다.")
        return

    st.markdown('<div class="section-title">발굴된 유망 테마 순위</div>', unsafe_allow_html=True)
    
    for theme, stage in chain:
        info = details.get(theme, {})
        score = safe_float(info.get("score"), 0)
        rows = info.get("rows", [])
        
        badge_cls = "stage-core" if stage == "현재 주도" else ("stage-next" if stage == "다음 수혜" else "stage-interest")
        
        with st.container(border=True):
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f'<span class="theme-stage-badge {badge_cls}">{stage}</span> **{theme}**', unsafe_allow_html=True)
                st.caption(info.get("reason", ""))
            with cols[1]:
                st.markdown(f"### **{score:.0f}점**")
                st.caption(f"관련 ETF {len(rows)}개")

            if rows:
                sub_cols = st.columns(min(len(rows), 3))
                for i, r in enumerate(rows[:3]):
                    with sub_cols[i]:
                        st.markdown(f"**{r['name']}**")
                        st.caption(f"최근 20일 {r['ret20']:+.1f}%")
                        if st.button("분석하기", key=f"btn_theme_{theme}_{r['code']}"):
                            st.session_state.future_detail_theme = theme
                            st.session_state.future_detail_code = r["code"]
                            st.session_state.main_page = "미래테마상세"
                            st.rerun()


def render_market_radar():
    st.markdown('<div class="app-title">🎯 시장 전광판 · RADAR</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">국내외 주요 지수와 시장 전반의 수급 및 추세를 한눈에 확인합니다.</div>', unsafe_allow_html=True)

    indices = [
        {"code": "069500", "name": "KODEX 200 (KOSPI 200)"},
        {"code": "229200", "name": "KODEX 코스닥150"},
        {"code": "379800", "name": "KODEX 미국S&P500"},
        {"code": "379810", "name": "KODEX 미국나스닥100"},
    ]

    for item in indices:
        code = item["code"]
        df = load_price_data(code)
        if df.empty:
            continue
        d = calculate_indicators(df)
        if d.empty:
            continue
        row = d.iloc[-1]
        current = safe_float(row["Close"])
        prev = safe_float(d["Close"].iloc[-2]) if len(d) >= 2 else current
        chg = current - prev
        chg_pct = chg / prev * 100 if prev != 0 else 0
        cls = "positive" if chg > 0 else ("negative" if chg < 0 else "neutral")

        with st.container(border=True):
            cols = st.columns([2, 1, 1])
            with cols[0]:
                st.markdown(f"**{item['name']}** ({code})")
                st.caption(f"20일선: {money(safe_float(row['MA20']))} | RSI: {safe_float(row['RSI14']):.1f}")
            with cols[1]:
                st.markdown(f"### {money(current)}")
            with cols[2]:
                st.markdown(f'<div class="{cls}" style="font-weight:800; font-size:1.1rem; text-align:right;">{money(chg)} ({chg_pct:+.2f}%)</div>', unsafe_allow_html=True)


def render_my_etf():
    st.markdown('<div class="app-title">📊 내 ETF 포트폴리오</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">관심 있거나 보유 중인 ETF 종목들의 현황을 관리합니다.</div>', unsafe_allow_html=True)
    st.info("등록된 관심 ETF 종목이 없습니다. 미래테마 탭에서 종목을 발굴하고 분석해보세요!")


# ============================================================
# MAIN ROUTER
# ============================================================

def main():
    init_state()

    pages = ["📊 내 ETF", "🚀 미래테마", "🎯 시장 RADAR"]
    
    if st.session_state.main_page == "미래테마상세":
        render_future_detail()
        return

    current_page_index = pages.index(st.session_state.main_page) if st.session_state.main_page in pages else 0
    selected_page = st.radio("메뉴 선택", pages, index=current_page_index, horizontal=True, label_visibility="collapsed", key="nav_radio")

    if selected_page != st.session_state.main_page:
        st.session_state.main_page = selected_page
        st.rerun()

    st.divider()

    if selected_page == "📊 내 ETF":
        render_my_etf()
    elif selected_page == "🚀 미래테마":
        render_future_theme_page()
    elif selected_page == "🎯 시장 RADAR":
        render_market_radar()


if __name__ == "__main__":
    main()
