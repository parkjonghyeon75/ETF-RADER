# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import json
import os
import html
from datetime import datetime


# ============================================================
# ETF RADAR
# 통합형 모바일 ETF 분석 대시보드
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# 파일
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"
UNIVERSE_FILE = "etf_universe_cache.json"


# ============================================================
# 기본 ETF
# ============================================================

BASE_ETFS = {
    "395160": "KODEX AI반도체핵심장비",
    "487240": "KODEX AI반도체",
    "471990": "KODEX AI반도체TOP2Plus",

    "133690": "TIGER 미국나스닥100",
    "360750": "TIGER 미국S&P500",
    "458730": "TIGER 글로벌AI&로봇",
    "381170": "TIGER 미국테크TOP10 INDXX",

    "396500": "TIGER 반도체",
    "091160": "KODEX 반도체",
    "091180": "KODEX 자동차",
    "139260": "TIGER 200 IT",
    "305720": "KODEX 2차전지산업",
    "364690": "KODEX 혁신기술테마액티브",

    "117700": "KODEX 건설",
    "140700": "KODEX 보험",
    "144600": "KODEX 은행",
    "102780": "KODEX 삼성그룹",

    "261220": "KODEX WTI원유선물(H)",

    "449170": "TIGER 글로벌AI인프라액티브",
    "434060": "TIGER 글로벌AI&반도체액티브",

    "464240": "KODEX AI전력핵심설비",
    "487130": "KODEX AI전력인프라",

    "475050": "ACE 글로벌반도체TOP4 Plus",
    "469150": "ACE AI반도체포커스",

    "130730": "KOSEF 단기자금",
    "161510": "PLUS 고배당주",
}


DEFAULT_WATCHLIST = [
    "395160",
    "487240",
    "471990",
    "133690",
    "360750",
    "458730",
]


# ============================================================
# 미래테마
# ============================================================

FUTURE_CHAIN = {
    "현재주도": {
        "AI반도체·핵심장비": [
            "395160",
            "487240",
            "471990",
            "469150"
        ],
        "미국 빅테크 & 혁신": [
            "133690",
            "360750",
            "381170"
        ],
    },

    "다음수혜": {
        "데이터센터·AI 인프라": [
            "449170",
            "434060"
        ],
        "전력 인프라 & 설비": [
            "464240",
            "487130"
        ],
        "바이오·헬스케어 혁신": [
            "364690"
        ],
    },

    "초기관심": {
        "로보틱스 & AI 자율주행": [
            "458730"
        ],
        "우주항공 & 방산": [
            "364690"
        ],
        "SMR·원자력 에너지": [
            "130730",
            "161510"
        ],
    }
}


# ============================================================
# CSS
# ============================================================

CSS = """
<style>

html, body {
    background: #f5f7fa;
}

.block-container {
    max-width: 1100px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    letter-spacing: -0.5px;
}

.etf-title {
    font-size: 24px;
    font-weight: 800;
    letter-spacing: -0.8px;
    margin-bottom: 3px;
}

.etf-subtitle {
    color: #6b7280;
    font-size: 13px;
    margin-bottom: 15px;
}

.selected-etf-box {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 14px 16px;
    margin-top: 5px;
    margin-bottom: 12px;
}

.selected-etf-name {
    font-size: 18px;
    font-weight: 800;
    color: #111827;
}

.selected-etf-code {
    margin-top: 4px;
    font-size: 12px;
    color: #6b7280;
}

.price-box {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 15px;
    margin-bottom: 12px;
}

.price-main {
    font-size: 27px;
    font-weight: 800;
    color: #111827;
}

.price-change {
    font-size: 15px;
    margin-top: 3px;
}

.card-title {
    font-size: 16px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 5px;
}

.card-sub {
    font-size: 12px;
    color: #6b7280;
}

.judgment {
    border-radius: 14px;
    padding: 15px;
    margin: 8px 0 12px 0;
    background: #ffffff;
    border: 1px solid #e5e7eb;
}

.judgment-title {
    font-size: 18px;
    font-weight: 800;
}

.judgment-action {
    font-size: 14px;
    margin-top: 5px;
    font-weight: 700;
}

.reason {
    margin-top: 9px;
    font-size: 13px;
    line-height: 1.55;
    color: #374151;
}

.level-box {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 12px;
}

.level-row {
    display: flex;
    justify-content: space-between;
    padding: 7px 0;
    border-bottom: 1px solid #f0f0f0;
}

.level-row:last-child {
    border-bottom: none;
}

.level-label {
    color: #6b7280;
    font-size: 13px;
}

.level-value {
    font-weight: 800;
    color: #111827;
}

.scenario-box {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 15px;
    margin-bottom: 12px;
}

.scenario-title {
    font-size: 15px;
    font-weight: 800;
    margin-bottom: 8px;
}

.scenario-text {
    font-size: 13px;
    line-height: 1.6;
    color: #374151;
}

.future-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 15px;
    min-height: 130px;
}

.future-name {
    font-size: 16px;
    font-weight: 800;
}

.future-code {
    color: #6b7280;
    font-size: 11px;
    margin-top: 3px;
}

.future-price {
    font-size: 18px;
    font-weight: 800;
    margin-top: 12px;
}

.future-change {
    font-size: 12px;
    margin-top: 3px;
}

.footer {
    text-align: center;
    color: #9ca3af;
    font-size: 11px;
    padding: 30px 0 10px 0;
}

</style>
"""


# ============================================================
# CSS 적용
# ============================================================

st.markdown(CSS, unsafe_allow_html=True)


# ============================================================
# JSON
# ============================================================

def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass

    return default


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )
    except Exception:
        pass


# ============================================================
# SESSION STATE
# ============================================================

if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_json(
        WATCHLIST_FILE,
        DEFAULT_WATCHLIST.copy()
    )

if "holdings" not in st.session_state:
    st.session_state.holdings = load_json(
        HOLDINGS_FILE,
        []
    )

if "etf_universe" not in st.session_state:
    st.session_state.etf_universe = load_json(
        UNIVERSE_FILE,
        {}
    )

if "price_cache" not in st.session_state:
    st.session_state.price_cache = {}

if "selected_code" not in st.session_state:
    st.session_state.selected_code = None

if "future_detail_code" not in st.session_state:
    st.session_state.future_detail_code = None

if "theme_last_update" not in st.session_state:
    st.session_state.theme_last_update = None

if "main_nav" not in st.session_state:
    st.session_state.main_nav = "📊 ETF"

if "main_nav_target" not in st.session_state:
    st.session_state.main_nav_target = None


# ============================================================
# ETF 이름
# ============================================================

def get_etf_name(code):

    code = str(code).strip().zfill(6)

    if code in BASE_ETFS:
        return BASE_ETFS[code]

    universe = st.session_state.get("etf_universe", {})

    if isinstance(universe, dict):

        item = universe.get(code)

        if isinstance(item, str):
            return item

        if isinstance(item, dict):
            return (
                item.get("name")
                or item.get("ETF명")
                or item.get("etf_name")
                or code
            )

    return code


# ============================================================
# 숫자 안전 변환
# ============================================================

def safe_float(value, default=np.nan):

    try:
        if pd.isna(value):
            return default

        return float(value)

    except Exception:
        return default


# ============================================================
# Yahoo Finance
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def fetch_yahoo(code):

    code = str(code).strip().zfill(6)

    try:

        ticker = f"{code}.KS"

        df = yf.download(
            ticker,
            period="2y",
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):

            try:
                df.columns = df.columns.get_level_values(0)
            except Exception:
                df.columns = [
                    c[0] if isinstance(c, tuple) else c
                    for c in df.columns
                ]

        df = df.copy()

        required = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]

        for col in required:

            if col not in df.columns:
                return pd.DataFrame()

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        df = df.dropna(subset=["Close"])

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# 지표
# ============================================================

def calculate_indicators(df):

    if df is None or df.empty:
        return pd.DataFrame()

    d = df.copy()

    close = d["Close"]

    d["MA20"] = close.rolling(20).mean()
    d["MA60"] = close.rolling(60).mean()
    d["MA120"] = close.rolling(120).mean()

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    d["RSI14"] = 100 - (
        100 / (1 + rs)
    )

    d["VOL20"] = d["Volume"].rolling(20).mean()

    d["VOL_RATIO"] = (
        d["Volume"] /
        d["VOL20"].replace(0, np.nan)
    )

    d["RET5"] = close.pct_change(5) * 100
    d["RET20"] = close.pct_change(20) * 100

    d["HIGH20"] = d["High"].rolling(20).max()
    d["LOW20"] = d["Low"].rolling(20).min()

    d["HIGH60"] = d["High"].rolling(60).max()
    d["LOW60"] = d["Low"].rolling(60).min()

    return d


# ============================================================
# 판단
# ============================================================

def get_judgment(d):

    if d is None or d.empty:
        return {
            "title": "데이터 부족",
            "action": "분석 대기",
            "reasons": ["차트 데이터를 충분히 확보하지 못했습니다."]
        }

    last = d.iloc[-1]

    close = safe_float(last["Close"])
    ma20 = safe_float(last["MA20"])
    ma60 = safe_float(last["MA60"])
    rsi = safe_float(last["RSI14"])
    vol_ratio = safe_float(last["VOL_RATIO"])
    ret5 = safe_float(last["RET5"])

    reasons = []

    # 추세
    if not np.isnan(ma20) and not np.isnan(ma60):

        if close > ma20 > ma60:

            trend = "상승추세"

            reasons.append(
                "현재가가 20일선과 60일선 위에 있고 "
                "단기 이동평균선이 중기 이동평균선 위에 있습니다."
            )

        elif close < ma20 < ma60:

            trend = "하락추세"

            reasons.append(
                "현재가가 20일선과 60일선 아래에 있어 "
                "단기 추세가 약한 상태입니다."
            )

        else:

            trend = "혼조"

            reasons.append(
                "20일선과 60일선의 방향이 엇갈려 "
                "추세 확인이 필요한 구간입니다."
            )

    else:

        trend = "데이터 부족"

    # RSI
    if not np.isnan(rsi):

        if rsi >= 70:

            reasons.append(
                f"RSI {rsi:.1f}로 단기 과열 가능성을 확인해야 합니다."
            )

        elif rsi <= 30:

            reasons.append(
                f"RSI {rsi:.1f}로 단기 과매도권에 진입했습니다."
            )

        else:

            reasons.append(
                f"RSI {rsi:.1f}로 극단적인 과열·과매도 구간은 아닙니다."
            )

    # 거래량
    if not np.isnan(vol_ratio):

        if vol_ratio >= 1.5:

            reasons.append(
                f"최근 거래량이 20일 평균 대비 {vol_ratio:.1f}배로 "
                "수급이 강하게 유입된 흔적이 있습니다."
            )

        elif vol_ratio <= 0.7:

            reasons.append(
                f"최근 거래량이 20일 평균 대비 {vol_ratio:.1f}배로 "
                "추격 매수보다는 방향 확인이 필요한 상태입니다."
            )

        else:

            reasons.append(
                "거래량은 평소 수준에 가까워 "
                "강한 수급 신호는 제한적입니다."
            )

    # 종합
    if trend == "상승추세":

        if not np.isnan(rsi) and rsi >= 70:

            title = "상승추세 · 과열주의"
            action = "보유 중심 · 신규 추격매수 주의"

        elif not np.isnan(vol_ratio) and vol_ratio >= 1.5:

            title = "상승추세 · 수급강화"
            action = "보유 중심 · 눌림목 대응"

        else:

            title = "상승추세"
            action = "보유 중심 · 눌림목 매수 검토"

    elif trend == "하락추세":

        title = "하락추세"
        action = "신규매수 보수적 접근"

    else:

        title = "혼조구간"
        action = "방향 확인 후 대응"

    return {
        "title": title,
        "action": action,
        "reasons": reasons
    }


# ============================================================
# 가격구간
# ============================================================

def calculate_levels(d):

    if d is None or d.empty:

        return {
            "first": np.nan,
            "support": np.nan,
            "breakout": np.nan,
            "risk": np.nan
        }

    last = d.iloc[-1]

    ma20 = safe_float(last["MA20"])
    ma60 = safe_float(last["MA60"])
    low20 = safe_float(last["LOW20"])
    low60 = safe_float(last["LOW60"])
    high20 = safe_float(last["HIGH20"])

    support_candidates = [
        x for x in [ma60, low20]
        if not np.isnan(x)
    ]

    risk_candidates = [
        x for x in [ma60, low20, low60]
        if not np.isnan(x)
    ]

    support = (
        min(support_candidates)
        if support_candidates
        else np.nan
    )

    risk = (
        min(risk_candidates)
        if risk_candidates
        else np.nan
    )

    return {
        "first": ma20,
        "support": support,
        "breakout": high20,
        "risk": risk
    }


# ============================================================
# 판단 표시
# ============================================================

def render_judgment(d, compact=False):

    result = get_judgment(d)

    reasons_html = ""

    for reason in result["reasons"]:

        reasons_html += (
            f"<div class='reason'>• "
            f"{html.escape(reason)}</div>"
        )

    st.markdown(
        f"""
        <div class="judgment">
            <div class="judgment-title">
                {html.escape(result["title"])}
            </div>

            <div class="judgment-action">
                {html.escape(result["action"])}
            </div>

            {reasons_html}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 가격구간 표시
# ============================================================

def render_levels(d):

    levels = calculate_levels(d)

    def money(x):

        if np.isnan(x):
            return "-"

        return f"{x:,.0f}원"

    st.markdown(
        f"""
        <div class="level-box">

            <div class="card-title">
                핵심 가격구간
            </div>

            <div class="level-row">
                <span class="level-label">1차 관심</span>
                <span class="level-value">{money(levels["first"])}</span>
            </div>

            <div class="level-row">
                <span class="level-label">주요 지지</span>
                <span class="level-value">{money(levels["support"])}</span>
            </div>

            <div class="level-row">
                <span class="level-label">돌파 기준</span>
                <span class="level-value">{money(levels["breakout"])}</span>
            </div>

            <div class="level-row">
                <span class="level-label">리스크 기준</span>
                <span class="level-value">{money(levels["risk"])}</span>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 시나리오
# ============================================================

def render_scenarios(d, compact=False):

    levels = calculate_levels(d)

    def money(x):

        if np.isnan(x):
            return "-"

        return f"{x:,.0f}원"

    first = money(levels["first"])
    support = money(levels["support"])
    breakout = money(levels["breakout"])
    risk = money(levels["risk"])

    st.markdown(
        f"""
        <div class="scenario-box">

            <div class="scenario-title">
                📈 상승 시나리오
            </div>

            <div class="scenario-text">
                {breakout} 부근의 최근 고점을 거래량과 함께 돌파하면
                상승추세 재가속 여부를 확인합니다.
                돌파 직후 급등한 경우에는 추격보다 재눌림을 기다리는 방식이 유리합니다.
            </div>

        </div>

        <div class="scenario-box">

            <div class="scenario-title">
                ↔️ 눌림목 시나리오
            </div>

            <div class="scenario-text">
                {first}~{support} 구간까지 조정이 발생할 경우
                이동평균선 지지 여부와 거래량 감소 여부를 확인합니다.
                지지 확인 후 반등하는 경우 분할 접근을 검토할 수 있습니다.
            </div>

        </div>

        <div class="scenario-box">

            <div class="scenario-title">
                ⚠️ 하락 시나리오
            </div>

            <div class="scenario-text">
                {risk} 아래로 이탈하고 거래량까지 증가하면
                기존 상승 시나리오가 약화될 수 있으므로
                신규매수보다 추세 회복 여부를 먼저 확인합니다.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 차트
# ============================================================

def render_chart(df):

    if df is None or df.empty:
        st.info("차트 데이터가 없습니다.")
        return

    chart_df = df.tail(180).copy()

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name="가격"
        )
    )

    if "MA20" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["MA20"],
                name="MA20",
                mode="lines",
                line=dict(width=1.4)
            )
        )

    if "MA60" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["MA60"],
                name="MA60",
                mode="lines",
                line=dict(width=1.4)
            )
        )

    fig.update_layout(
        height=430,
        margin=dict(
            l=5,
            r=5,
            t=15,
            b=5
        ),
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# ============================================================
# ETF 분석 전체
# ============================================================

def render_analysis(code):

    code = str(code).strip().zfill(6)

    name = get_etf_name(code)

    st.markdown(
        f"""
        <div class="selected-etf-box">
            <div class="selected-etf-name">
                {html.escape(name)}
            </div>
            <div class="selected-etf-code">
                종목코드 {code}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.spinner("ETF 데이터를 분석하고 있습니다..."):

        raw = fetch_yahoo(code)

    if raw.empty:

        st.error(
            "해당 ETF의 시장 데이터를 가져오지 못했습니다."
        )

        return

    df = calculate_indicators(raw)

    if df.empty:

        st.error("분석 가능한 데이터가 없습니다.")
        return

    last = df.iloc[-1]

    price = safe_float(last["Close"])
    prev = safe_float(df.iloc[-2]["Close"]) if len(df) >= 2 else np.nan

    change = np.nan

    if not np.isnan(price) and not np.isnan(prev) and prev != 0:
        change = (price / prev - 1) * 100

    change_text = "-"

    if not np.isnan(change):
        sign = "+" if change >= 0 else ""
        change_text = f"{sign}{change:.2f}%"

    st.markdown(
        f"""
        <div class="price-box">

            <div class="card-sub">
                현재가
            </div>

            <div class="price-main">
                {price:,.0f}원
            </div>

            <div class="price-change">
                전일 대비 {change_text}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 📌 현재 판단")

    render_judgment(df)

    st.markdown("### 🎯 핵심 가격")

    render_levels(df)

    st.markdown("### 🧭 대응 시나리오")

    render_scenarios(df)

    st.markdown("### 📈 차트")

    render_chart(df)


# ============================================================
# ETF 검색
# ============================================================

def search_etfs(query):

    query = str(query).strip().lower()

    universe = {}

    universe.update(BASE_ETFS)

    cached = st.session_state.get(
        "etf_universe",
        {}
    )

    if isinstance(cached, dict):

        for code, item in cached.items():

            code = str(code).strip().zfill(6)

            if isinstance(item, str):

                universe[code] = item

            elif isinstance(item, dict):

                name = (
                    item.get("name")
                    or item.get("ETF명")
                    or item.get("etf_name")
                )

                if name:
                    universe[code] = name

    results = []

    for code, name in universe.items():

        code = str(code).zfill(6)
        name = str(name)

        if (
            query in code.lower()
            or query in name.lower()
        ):

            results.append({
                "code": code,
                "name": name
            })

    results.sort(
        key=lambda x: (
            not x["code"].startswith(query),
            x["name"]
        )
    )

    return results


# ============================================================
# 통합 ETF 화면
# ============================================================

def render_etf_dashboard():

    st.markdown(
        """
        <div class="etf-title">
            📊 내 ETF
        </div>

        <div class="etf-subtitle">
            관심 ETF를 검색하고 바로 분석하세요.
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # 검색
    # --------------------------------------------------------

    st.markdown("### 🔎 ETF 찾기")

    query = st.text_input(
        "ETF 검색",
        placeholder="ETF명 또는 종목코드 입력",
        key="etf_search_input",
        label_visibility="collapsed"
    )

    # 검색 결과
    results = search_etfs(query)

    if query.strip():

        if results:

            # ==================================================
            # 중요:
            # selectbox에는 한글 이름을 절대 넣지 않음
            # 숫자 코드만 넣어서 한글 깨짐 방지
            # ==================================================

            result_codes = [
                str(x["code"]).zfill(6)
                for x in results
            ]

            selected_code = st.selectbox(
                "검색 결과",
                result_codes,
                key="search_result_code",
                label_visibility="collapsed"
            )

            selected_code = str(
                selected_code
            ).strip().zfill(6)

            selected_name = get_etf_name(
                selected_code
            )

            st.markdown(
                f"""
                <div class="selected-etf-box">

                    <div class="selected-etf-name">
                        {html.escape(selected_name)}
                    </div>

                    <div class="selected-etf-code">
                        종목코드 {selected_code}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "➕ 관심 ETF 추가",
                    use_container_width=True,
                    key="finder_add"
                ):

                    if selected_code not in st.session_state.watchlist:

                        st.session_state.watchlist.append(
                            selected_code
                        )

                        save_json(
                            WATCHLIST_FILE,
                            st.session_state.watchlist
                        )

                        st.success(
                            f"{selected_name}을 관심 ETF에 추가했습니다."
                        )

                    else:

                        st.info(
                            "이미 관심 ETF에 등록되어 있습니다."
                        )

            with c2:

                if st.button(
                    "📊 ETF 분석",
                    use_container_width=True,
                    key="finder_analysis"
                ):

                    st.session_state.selected_code = selected_code

                    st.rerun()

        else:

            st.info(
                "검색 결과가 없습니다."
            )

    else:

        st.caption(
            "ETF명 또는 종목코드를 입력하면 검색됩니다."
        )


    # ========================================================
    # 관심 ETF
    # ========================================================

    st.markdown("---")

    st.markdown("### ⭐ 관심 ETF")

    watchlist = st.session_state.watchlist

    if not watchlist:

        st.info(
            "관심 ETF가 없습니다. 위 검색창에서 ETF를 추가해 주세요."
        )

    else:

        # ----------------------------------------------------
        # 중요:
        # 여기 역시 selectbox에는 코드만 표시
        # ----------------------------------------------------

        watch_codes = [
            str(x).zfill(6)
            for x in watchlist
        ]

        # 중복 제거
        watch_codes = list(
            dict.fromkeys(watch_codes)
        )

        watch_selected = st.selectbox(
            "관심 ETF 선택",
            watch_codes,
            key="watchlist_code",
            label_visibility="collapsed"
        )

        watch_selected = str(
            watch_selected
        ).strip().zfill(6)

        watch_name = get_etf_name(
            watch_selected
        )

        st.markdown(
            f"""
            <div class="selected-etf-box">

                <div class="selected-etf-name">
                    {html.escape(watch_name)}
                </div>

                <div class="selected-etf-code">
                    종목코드 {watch_selected}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "📊 선택 ETF 분석",
                use_container_width=True,
                key="watch_analysis"
            ):

                st.session_state.selected_code = watch_selected

                st.rerun()

        with c2:

            if st.button(
                "🗑 관심 ETF 삭제",
                use_container_width=True,
                key="watch_delete"
            ):

                if watch_selected in st.session_state.watchlist:

                    st.session_state.watchlist.remove(
                        watch_selected
                    )

                    save_json(
                        WATCHLIST_FILE,
                        st.session_state.watchlist
                    )

                    st.rerun()


    # ========================================================
    # 선택 ETF 분석
    # ========================================================

    if st.session_state.selected_code:

        st.markdown("---")

        st.markdown("## 📊 ETF 분석")

        render_analysis(
            st.session_state.selected_code
        )


# ============================================================
# 미래테마 상세
# ============================================================

def render_future_detail(item):

    code = str(item["code"]).zfill(6)
    name = get_etf_name(code)

    st.markdown(
        f"""
        <div class="selected-etf-box">

            <div class="selected-etf-name">
                {html.escape(name)}
            </div>

            <div class="selected-etf-code">
                종목코드 {code}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    raw = fetch_yahoo(code)

    if raw.empty:

        st.warning(
            "현재 시장 데이터를 가져오지 못했습니다."
        )

        return

    df = calculate_indicators(raw)

    last = df.iloc[-1]

    price = safe_float(last["Close"])

    prev = (
        safe_float(df.iloc[-2]["Close"])
        if len(df) >= 2
        else np.nan
    )

    change = np.nan

    if (
        not np.isnan(price)
        and not np.isnan(prev)
        and prev != 0
    ):
        change = (price / prev - 1) * 100

    if np.isnan(change):

        change_text = "-"

    else:

        sign = "+" if change >= 0 else ""

        change_text = (
            f"{sign}{change:.2f}%"
        )

    st.markdown(
        f"""
        <div class="price-box">

            <div class="card-sub">
                현재가
            </div>

            <div class="price-main">
                {price:,.0f}원
            </div>

            <div class="price-change">
                전일 대비 {change_text}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("#### 현재 판단")

    render_judgment(
        df,
        compact=True
    )

    st.markdown("#### 핵심 가격")

    render_levels(df)

    st.markdown("#### 대응 시나리오")

    render_scenarios(
        df,
        compact=True
    )

    st.markdown("#### 차트")

    render_chart(df)

    if st.button(
        "📊 내 ETF 화면에서 보기",
        use_container_width=True,
        key=f"future_go_{code}"
    ):

        st.session_state.selected_code = code

        st.session_state.main_nav_target = "📊 ETF"

        st.rerun()


# ============================================================
# 미래테마
# ============================================================

def render_future_theme():

    st.markdown(
        """
        <div class="etf-title">
            🔮 미래테마
        </div>

        <div class="etf-subtitle">
            현재 주도 → 다음 수혜 → 초기 관심 순으로
            ETF 흐름을 확인합니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns([3, 1])

    with c1:

        if st.session_state.theme_last_update:

            st.caption(
                "마지막 업데이트: "
                + str(
                    st.session_state.theme_last_update
                )
            )

    with c2:

        if st.button(
            "🔄 테마 업데이트",
            use_container_width=True,
            key="theme_update"
        ):

            st.session_state.theme_last_update = (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                )
            )

            st.rerun()


    # ========================================================
    # 테마 단계
    # ========================================================

    for stage, themes in FUTURE_CHAIN.items():

        st.markdown(
            f"## {stage}"
        )

        for theme, codes in themes.items():

            st.markdown(
                f"### {theme}"
            )

            valid_codes = [
                str(code).zfill(6)
                for code in codes
            ]

            cols = st.columns(
                min(
                    3,
                    len(valid_codes)
                )
            )

            for idx, code in enumerate(valid_codes):

                name = get_etf_name(code)

                with cols[idx % len(cols)]:

                    raw = fetch_yahoo(code)

                    price_text = "-"
                    change_text = ""

                    if (
                        raw is not None
                        and not raw.empty
                    ):

                        last_price = safe_float(
                            raw.iloc[-1]["Close"]
                        )

                        if not np.isnan(last_price):

                            price_text = (
                                f"{last_price:,.0f}원"
                            )

                        if len(raw) >= 2:

                            prev_price = safe_float(
                                raw.iloc[-2]["Close"]
                            )

                            if (
                                not np.isnan(last_price)
                                and not np.isnan(prev_price)
                                and prev_price != 0
                            ):

                                chg = (
                                    last_price /
                                    prev_price -
                                    1
                                ) * 100

                                sign = (
                                    "+"
                                    if chg >= 0
                                    else ""
                                )

                                change_text = (
                                    f"{sign}{chg:.2f}%"
                                )

                    # 카드 전체를 하나의 HTML 블록으로 생성
                    # ------------------------------------------------

                    st.markdown(
                        f"""
                        <div class="future-card">

                            <div class="future-name">
                                {html.escape(name)}
                            </div>

                            <div class="future-code">
                                {code}
                            </div>

                            <div class="future-price">
                                {price_text}
                            </div>

                            <div class="future-change">
                                {change_text}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    button_key = (
                        "future_analysis_"
                        + stage
                        + "_"
                        + theme
                        + "_"
                        + code
                    )

                    if st.button(
                        "ETF 분석",
                        key=button_key,
                        use_container_width=True
                    ):

                        if (
                            st.session_state.future_detail_code
                            == code
                        ):

                            st.session_state.future_detail_code = None

                        else:

                            st.session_state.future_detail_code = code

                        st.rerun()

                    # ==================================================
                    # 핵심:
                    # 버튼 바로 아래에서 해당 ETF 결과 출력
                    # ==================================================

                    if (
                        st.session_state.future_detail_code
                        == code
                    ):

                        with st.container(
                            border=True
                        ):

                            render_future_detail(
                                {
                                    "code": code,
                                    "name": name
                                }
                            )

            st.markdown("")


# ============================================================
# 상단 네비게이션 상태 처리
# ============================================================

if st.session_state.get("main_nav_target"):

    st.session_state.main_nav = (
        st.session_state.main_nav_target
    )

    st.session_state.main_nav_target = None


# ============================================================
# 헤더
# ============================================================

st.markdown(
    """
    <div class="etf-title">
        📊 ETF RADAR
    </div>

    <div class="etf-subtitle">
        국내 ETF 기술적 흐름 · 가격구간 · 대응 시나리오
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 메뉴
#
# 여기서 '내 ETF'와 'ETF 찾기'를 완전히 분리하지 않습니다.
# 하나의 📊 ETF 화면에서 같이 사용합니다.
# ============================================================

nav = st.radio(
    "메뉴",
    [
        "📊 ETF",
        "🔮 미래테마"
    ],
    horizontal=True,
    key="main_nav",
    label_visibility="collapsed"
)


st.markdown("---")


# ============================================================
# 화면
# ============================================================

if nav == "📊 ETF":

    render_etf_dashboard()

elif nav == "🔮 미래테마":

    render_future_theme()


# ============================================================
# Footer
# ============================================================

st.markdown(
    """
    <div class="footer">
        ETF RADAR · Technical Analysis Dashboard
    </div>
    """,
    unsafe_allow_html=True
)