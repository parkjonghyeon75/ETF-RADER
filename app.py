# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import json
import os
import html
from datetime import datetime


# ============================================================
# ETF RADAR
# Mobile Financial Dashboard
# Final Stable Version
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CSS
# ============================================================

CSS = """
<style>

html, body, [class*="css"] {
    font-family:
        "Noto Sans KR",
        "Noto Sans CJK KR",
        "Malgun Gothic",
        "Apple SD Gothic Neo",
        "Nanum Gothic",
        Arial,
        sans-serif !important;
}

.stApp {
    background: #f5f7fb;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px;
}

h1, h2, h3, h4, h5, h6,
p, div, span, label {
    font-family:
        "Noto Sans KR",
        "Noto Sans CJK KR",
        "Malgun Gothic",
        "Apple SD Gothic Neo",
        "Nanum Gothic",
        Arial,
        sans-serif !important;
}

/* -----------------------------
   Selectbox
   ----------------------------- */

div[data-baseweb="select"] {
    font-family:
        "Noto Sans KR",
        "Noto Sans CJK KR",
        "Malgun Gothic",
        "Apple SD Gothic Neo",
        "Nanum Gothic",
        Arial,
        sans-serif !important;
}

div[data-baseweb="select"] * {
    font-family:
        "Noto Sans KR",
        "Noto Sans CJK KR",
        "Malgun Gothic",
        "Apple SD Gothic Neo",
        "Nanum Gothic",
        Arial,
        sans-serif !important;
}

/* Dropdown popup */

div[role="listbox"],
div[role="option"],
ul[role="listbox"],
li[role="option"] {
    font-family:
        "Noto Sans KR",
        "Noto Sans CJK KR",
        "Malgun Gothic",
        "Apple SD Gothic Neo",
        "Nanum Gothic",
        Arial,
        sans-serif !important;
}

/* -----------------------------
   Buttons
   ----------------------------- */

.stButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 700;
    font-family:
        "Noto Sans KR",
        "Noto Sans CJK KR",
        "Malgun Gothic",
        "Apple SD Gothic Neo",
        "Nanum Gothic",
        Arial,
        sans-serif !important;
}

/* -----------------------------
   ETF selected information
   ----------------------------- */

.selected-etf-box {
    margin-top: 7px;
    margin-bottom: 12px;
    padding: 12px 14px;
    background: #ffffff;
    border: 1px solid #e2e7ef;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.selected-etf-name {
    font-size: 15px;
    font-weight: 800;
    color: #172033;
    line-height: 1.35;
}

.selected-etf-code {
    margin-top: 3px;
    font-size: 12px;
    font-weight: 600;
    color: #7a8495;
}

/* -----------------------------
   Cards
   ----------------------------- */

.dashboard-card {
    background: #ffffff;
    border: 1px solid #e5e9f0;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 14px;
    box-shadow: 0 4px 14px rgba(20,30,50,0.04);
}

.section-title {
    font-size: 19px;
    font-weight: 800;
    color: #172033;
    margin-bottom: 8px;
}

.section-subtitle {
    font-size: 12px;
    color: #7c8798;
    margin-bottom: 14px;
}

.metric-label {
    font-size: 12px;
    color: #788396;
    margin-bottom: 3px;
}

.metric-value {
    font-size: 19px;
    font-weight: 800;
    color: #172033;
}

.future-theme-card {
    background: #ffffff;
    border: 1px solid #e1e6ee;
    border-radius: 15px;
    padding: 14px;
    margin-bottom: 12px;
    box-shadow: 0 3px 12px rgba(20,30,50,0.04);
}

.future-theme-title {
    font-size: 17px;
    font-weight: 800;
    color: #182235;
}

.future-theme-stage {
    font-size: 11px;
    font-weight: 700;
    color: #6d7787;
    margin-bottom: 8px;
}

.future-analysis-title {
    font-size: 17px;
    font-weight: 800;
    color: #182235;
    margin-bottom: 10px;
}

.judgment-box {
    background: #f7f9fc;
    border-radius: 12px;
    padding: 13px;
    margin-top: 8px;
    margin-bottom: 10px;
}

.scenario-box {
    background: #ffffff;
    border: 1px solid #e4e8ef;
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 8px;
}

.small-text {
    font-size: 12px;
    color: #697487;
    line-height: 1.5;
}

.reason-text {
    font-size: 13px;
    color: #364154;
    line-height: 1.55;
}

.price-highlight {
    font-size: 17px;
    font-weight: 800;
    color: #162033;
}

@media (max-width: 768px) {

    .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }

    .section-title {
        font-size: 18px;
    }

    .metric-value {
        font-size: 17px;
    }

}

</style>
"""

st.html(CSS)


# ============================================================
# FILES
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"
UNIVERSE_FILE = "etf_universe_cache.json"


# ============================================================
# BASE ETF
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
# FUTURE THEMES
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
# SESSION STATE
# ============================================================

if "watchlist" not in st.session_state:
    st.session_state.watchlist = DEFAULT_WATCHLIST.copy()

if "holdings" not in st.session_state:
    st.session_state.holdings = {}

if "etf_universe" not in st.session_state:
    st.session_state.etf_universe = {}

if "price_cache" not in st.session_state:
    st.session_state.price_cache = {}

if "theme_cache" not in st.session_state:
    st.session_state.theme_cache = {}

if "selected_code" not in st.session_state:
    st.session_state.selected_code = None

if "main_nav" not in st.session_state:
    st.session_state.main_nav = "📊 내 ETF"

if "main_nav_target" not in st.session_state:
    st.session_state.main_nav_target = None

if "future_detail_code" not in st.session_state:
    st.session_state.future_detail_code = None

if "theme_last_update" not in st.session_state:
    st.session_state.theme_last_update = None


# ============================================================
# JSON HELPERS
# ============================================================

def load_json(path, default):

    try:

        if os.path.exists(path):

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

    except Exception:
        pass

    return default


def save_json(path, data):

    try:

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

        return True

    except Exception:
        return False


# ============================================================
# INITIAL LOAD
# ============================================================

if os.path.exists(WATCHLIST_FILE):

    loaded_watchlist = load_json(
        WATCHLIST_FILE,
        DEFAULT_WATCHLIST
    )

    if isinstance(loaded_watchlist, list):

        st.session_state.watchlist = [
            str(x).zfill(6)
            for x in loaded_watchlist
        ]


if os.path.exists(HOLDINGS_FILE):

    loaded_holdings = load_json(
        HOLDINGS_FILE,
        {}
    )

    if isinstance(loaded_holdings, dict):
        st.session_state.holdings = loaded_holdings


if os.path.exists(UNIVERSE_FILE):

    loaded_universe = load_json(
        UNIVERSE_FILE,
        {}
    )

    if isinstance(loaded_universe, dict):
        st.session_state.etf_universe = loaded_universe


# ============================================================
# ETF NAME
# ============================================================

def get_etf_name(code):

    code = str(code).strip().zfill(6)

    if code in BASE_ETFS:
        return BASE_ETFS[code]

    universe = st.session_state.get(
        "etf_universe",
        {}
    )

    item = universe.get(code)

    if isinstance(item, dict):

        name = item.get("name")

        if name:
            return str(name)

    if isinstance(item, str):
        return item

    return f"ETF {code}"


# ============================================================
# PRICE DATA
# ============================================================

def fetch_yahoo(code):

    code = str(code).strip().zfill(6)

    try:

        df = yf.download(
            f"{code}.KS",
            period="2y",
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):

            df.columns = [
                c[0] if isinstance(c, tuple) else c
                for c in df.columns
            ]

        df.columns = [
            str(c).strip()
            for c in df.columns
        ]

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

        df = df[required].copy()

        for col in required:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        df.dropna(
            subset=["Close"],
            inplace=True
        )

        return df

    except Exception:

        return pd.DataFrame()


def load_price_data(code):

    code = str(code).strip().zfill(6)

    if code in st.session_state.price_cache:

        cached = st.session_state.price_cache[code]

        if isinstance(cached, pd.DataFrame):
            return cached

    df = fetch_yahoo(code)

    if not df.empty:

        st.session_state.price_cache[code] = df

    return df


# ============================================================
# INDICATORS
# ============================================================

def calculate_indicators(df):

    if df.empty:
        return df

    df = df.copy()

    df["MA20"] = (
        df["Close"]
        .rolling(20)
        .mean()
    )

    df["MA60"] = (
        df["Close"]
        .rolling(60)
        .mean()
    )

    df["MA120"] = (
        df["Close"]
        .rolling(120)
        .mean()
    )

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(
        0,
        np.nan
    )

    df["RSI14"] = (
        100 -
        (100 / (1 + rs))
    )

    df["VOL20"] = (
        df["Volume"]
        .rolling(20)
        .mean()
    )

    df["VOL_RATIO"] = (
        df["Volume"] /
        df["VOL20"].replace(0, np.nan)
    )

    df["RET5"] = (
        df["Close"]
        .pct_change(5) * 100
    )

    df["RET20"] = (
        df["Close"]
        .pct_change(20) * 100
    )

    df["HIGH20"] = (
        df["High"]
        .rolling(20)
        .max()
    )

    df["LOW20"] = (
        df["Low"]
        .rolling(20)
        .min()
    )

    df["HIGH60"] = (
        df["High"]
        .rolling(60)
        .max()
    )

    df["LOW60"] = (
        df["Low"]
        .rolling(60)
        .min()
    )

    return df


# ============================================================
# JUDGMENT
# ============================================================

def get_judgment(df):

    if df.empty:
        return None

    d = df.iloc[-1]

    close = float(d["Close"])

    ma20 = float(d["MA20"]) if pd.notna(d["MA20"]) else close
    ma60 = float(d["MA60"]) if pd.notna(d["MA60"]) else close

    rsi = float(d["RSI14"]) if pd.notna(d["RSI14"]) else 50
    vol_ratio = (
        float(d["VOL_RATIO"])
        if pd.notna(d["VOL_RATIO"])
        else 1
    )

    ret20 = (
        float(d["RET20"])
        if pd.notna(d["RET20"])
        else 0
    )

    if close > ma20 > ma60:

        ma_state = "상승 추세"

    elif close > ma60:

        ma_state = "중기 상승"

    elif close < ma20 < ma60:

        ma_state = "하락 압력"

    else:

        ma_state = "혼조"

    if rsi >= 70:

        rsi_state = "과열"

    elif rsi >= 55:

        rsi_state = "강세"

    elif rsi <= 30:

        rsi_state = "침체"

    elif rsi <= 45:

        rsi_state = "약세"

    else:

        rsi_state = "중립"

    if vol_ratio >= 1.5:

        vol_state = "거래량 급증"

    elif vol_ratio >= 1.1:

        vol_state = "거래량 증가"

    elif vol_ratio <= 0.7:

        vol_state = "거래량 감소"

    else:

        vol_state = "평균 수준"

    reasons = [
        f"20일선 기준: {ma_state}",
        f"RSI14: {rsi:.1f} ({rsi_state})",
        f"거래량: 평균 대비 {vol_ratio:.2f}배 ({vol_state})",
        f"20일 수익률: {ret20:+.1f}%"
    ]

    if ma_state == "상승 추세" and rsi < 70:

        title = "상승 추세 유지"
        action = "눌림목 중심 대응"

    elif ma_state in [
        "상승 추세",
        "중기 상승"
    ] and rsi >= 70:

        title = "상승세지만 과열 구간"
        action = "추격매수보다 조정 대기"

    elif ma_state == "하락 압력":

        title = "추세 약화"
        action = "반등 확인 후 대응"

    else:

        title = "방향 탐색 구간"
        action = "추세 확인 후 대응"

    return {

        "title": title,
        "action": action,
        "reasons": reasons,
        "ma_state": ma_state,
        "rsi_state": rsi_state,
        "vol_state": vol_state,
        "rsi": rsi,
        "vol_ratio": vol_ratio,
        "ret20": ret20
    }


# ============================================================
# PRICE LEVELS
# ============================================================

def calculate_levels(df):

    if df.empty:
        return {}

    d = df.iloc[-1]

    close = float(d["Close"])

    ma20 = (
        float(d["MA20"])
        if pd.notna(d["MA20"])
        else close
    )

    ma60 = (
        float(d["MA60"])
        if pd.notna(d["MA60"])
        else close
    )

    low20 = (
        float(d["LOW20"])
        if pd.notna(d["LOW20"])
        else close
    )

    high20 = (
        float(d["HIGH20"])
        if pd.notna(d["HIGH20"])
        else close
    )

    low60 = (
        float(d["LOW60"])
        if pd.notna(d["LOW60"])
        else close
    )

    return {

        "first": ma20,

        "support": min(
            ma60,
            low20
        ),

        "breakout": high20,

        "risk": min(
            ma60,
            low20,
            low60
        )
    }


# ============================================================
# JUDGMENT UI
# ============================================================

def render_judgment(d, compact=False):

    judgment = get_judgment(d)

    if judgment is None:

        st.warning("분석할 데이터가 없습니다.")

        return

    st.markdown(
        "### 📌 현재 판단"
    )

    st.markdown(
        f"""
        <div class="judgment-box">

        <div style="font-size:18px;font-weight:800;">
        {html.escape(judgment["title"])}
        </div>

        <div style="margin-top:5px;font-size:14px;font-weight:700;">
        대응: {html.escape(judgment["action"])}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if compact:

        for reason in judgment["reasons"]:

            st.markdown(
                f"• {html.escape(reason)}"
            )

        return

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            f"""
            <div class="small-text">
            • {html.escape(judgment["reasons"][0])}<br>
            • {html.escape(judgment["reasons"][1])}
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="small-text">
            • {html.escape(judgment["reasons"][2])}<br>
            • {html.escape(judgment["reasons"][3])}
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# SCENARIOS
# ============================================================

def render_scenarios(d, compact=False):

    levels = calculate_levels(d)

    if not levels:
        return

    cards = [

        (
            "① 눌림목",
            levels["first"],
            "20일선 부근에서 지지 확인 시 분할 접근"
        ),

        (
            "② 지지구간",
            levels["support"],
            "중기 지지선과 최근 저점 확인"
        ),

        (
            "③ 돌파",
            levels["breakout"],
            "최근 20일 고점 돌파와 거래량 동반 여부 확인"
        ),

        (
            "④ 위험관리",
            levels["risk"],
            "중요 지지선 이탈 시 비중 조절 검토"
        )
    ]

    st.markdown(
        "### 🎯 가격 대응 구간"
    )

    if compact:

        for title, price, desc in cards:

            st.markdown(
                f"""
                <div class="scenario-box">

                <div style="font-size:14px;font-weight:800;">
                {title}
                </div>

                <div class="price-highlight">
                {price:,.0f}원
                </div>

                <div class="small-text">
                {desc}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        return

    cols = st.columns(4)

    for col, item in zip(cols, cards):

        title, price, desc = item

        with col:

            st.markdown(
                f"""
                <div class="scenario-box">

                <div style="font-size:13px;font-weight:800;">
                {title}
                </div>

                <div class="price-highlight">
                {price:,.0f}원
                </div>

                <div class="small-text">
                {desc}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# CHART
# ============================================================

def render_chart(d):

    if d.empty:
        return

    chart_df = d.tail(120).copy()

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.72, 0.28]
    )

    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name="가격"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA20"],
            name="MA20",
            line=dict(width=1.5)
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA60"],
            name="MA60",
            line=dict(width=1.5)
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=chart_df.index,
            y=chart_df["Volume"],
            name="거래량"
        ),
        row=2,
        col=1
    )

    fig.update_layout(
        height=520,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10
        ),
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        font=dict(
            family="Noto Sans KR, Malgun Gothic, sans-serif"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


# ============================================================
# ETF SEARCH
# ============================================================

def search_etfs(query):

    query = str(query or "").strip().lower()

    universe = {}

    universe.update(BASE_ETFS)

    for code, value in st.session_state.get(
        "etf_universe",
        {}
    ).items():

        if isinstance(value, dict):

            name = value.get(
                "name",
                ""
            )

        else:

            name = str(value)

        universe[
            str(code).zfill(6)
        ] = name

    if not query:

        items = list(
            universe.items()
        )[:30]

    else:

        items = []

        for code, name in universe.items():

            code_text = str(code)

            name_text = str(name)

            if (
                query in code_text.lower()
                or query in name_text.lower()
            ):

                items.append(
                    (
                        code,
                        name
                    )
                )

            if len(items) >= 50:
                break

    return [
        {
            "code": str(code).zfill(6),
            "name": str(name)
        }

        for code, name in items
    ]


# ============================================================
# ETF FINDER
#
# IMPORTANT:
# selectbox에는 한글 ETF명을 넣지 않는다.
# Android/BaseWeb 드롭다운의 한글 렌더링 문제를
# 종목코드 선택 방식으로 완전히 우회한다.
# ============================================================

def render_finder():

    st.markdown(
        '<div class="section-title">🔎 ETF 찾기</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">ETF명 또는 종목코드를 검색하세요.</div>',
        unsafe_allow_html=True
    )

    query = st.text_input(
        "ETF 검색",
        placeholder="예: 반도체 / AI / 395160",
        key="etf_search_query"
    )

    results = search_etfs(query)

    if not results:

        st.info(
            "검색 결과가 없습니다."
        )

        return

    # --------------------------------------------------------
    # 드롭다운에는 숫자 코드만 표시
    # --------------------------------------------------------

    search_codes = [
        item["code"]
        for item in results
    ]

    selected_code = st.selectbox(
        "검색 결과",
        search_codes,
        key="search_result_code"
    )

    selected_code = str(
        selected_code
    ).strip().zfill(6)

    selected_name = get_etf_name(
        selected_code
    )

    # --------------------------------------------------------
    # ETF 이름은 별도의 HTML 영역에서 표시
    # --------------------------------------------------------

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
            key="finder_add",
            use_container_width=True
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
                    f"{selected_name} 추가 완료"
                )

            else:

                st.info(
                    "이미 관심 ETF에 있습니다."
                )

    with c2:

        if st.button(
            "📊 ETF 분석",
            key="finder_analysis",
            use_container_width=True
        ):

            st.session_state.selected_code = selected_code

            st.session_state.main_nav_target = "📊 내 ETF"

            st.session_state.future_detail_code = None

            st.rerun()


# ============================================================
# WATCHLIST
# ============================================================

def render_watchlist():

    st.markdown(
        '<div class="section-title">⭐ 관심 ETF</div>',
        unsafe_allow_html=True
    )

    watchlist = [
        str(x).zfill(6)
        for x in st.session_state.watchlist
    ]

    if not watchlist:

        st.info(
            "관심 ETF가 없습니다."
        )

        return

    selected = st.selectbox(
        "관심 ETF 선택",
        watchlist,
        key="watchlist_code"
    )

    selected = str(
        selected
    ).zfill(6)

    name = get_etf_name(
        selected
    )

    st.markdown(
        f"""
        <div class="selected-etf-box">

            <div class="selected-etf-name">
                {html.escape(name)}
            </div>

            <div class="selected-etf-code">
                종목코드 {selected}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "📊 분석하기",
            key="watch_analysis",
            use_container_width=True
        ):

            st.session_state.selected_code = selected

            st.session_state.future_detail_code = None

            st.rerun()

    with c2:

        if st.button(
            "🗑 관심 해제",
            key="watch_remove",
            use_container_width=True
        ):

            if selected in st.session_state.watchlist:

                st.session_state.watchlist.remove(
                    selected
                )

                save_json(
                    WATCHLIST_FILE,
                    st.session_state.watchlist
                )

                st.rerun()


# ============================================================
# MAIN ETF ANALYSIS
# ============================================================

def render_etf_analysis(code):

    code = str(code).zfill(6)

    name = get_etf_name(code)

    st.markdown(
        f"""
        <div class="dashboard-card">

            <div class="section-title">
            📊 {html.escape(name)}
            </div>

            <div class="section-subtitle">
            종목코드 {code}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    df = load_price_data(code)

    if df.empty:

        st.error(
            "가격 데이터를 불러오지 못했습니다."
        )

        return

    d = calculate_indicators(df)

    last = d.iloc[-1]

    close = float(
        last["Close"]
    )

    prev = (
        float(d.iloc[-2]["Close"])
        if len(d) >= 2
        else close
    )

    change = close - prev

    change_pct = (
        change / prev * 100
        if prev != 0
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.markdown(
            f"""
            <div class="dashboard-card">
            <div class="metric-label">현재가</div>
            <div class="metric-value">
            {close:,.0f}원
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="dashboard-card">
            <div class="metric-label">등락률</div>
            <div class="metric-value">
            {change_pct:+.2f}%
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        rsi = (
            float(last["RSI14"])
            if pd.notna(last["RSI14"])
            else 0
        )

        st.markdown(
            f"""
            <div class="dashboard-card">
            <div class="metric-label">RSI14</div>
            <div class="metric-value">
            {rsi:.1f}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:

        vr = (
            float(last["VOL_RATIO"])
            if pd.notna(last["VOL_RATIO"])
            else 0
        )

        st.markdown(
            f"""
            <div class="dashboard-card">
            <div class="metric-label">거래량</div>
            <div class="metric-value">
            {vr:.2f}배
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    render_judgment(d)

    render_scenarios(d)

    st.markdown(
        "### 📈 차트"
    )

    render_chart(d)


# ============================================================
# FUTURE THEME DETAIL
# ============================================================

def render_future_detail(item):

    code = str(
        item["code"]
    ).zfill(6)

    name = item["name"]

    # --------------------------------------------------------
    # 중요:
    # 분석 결과를 이 함수 호출 위치에서 바로 렌더링한다.
    # 따라서 클릭한 ETF 버튼 바로 아래에 표시된다.
    # --------------------------------------------------------

    with st.container(border=True):

        st.markdown(
            f"""
            <div class="future-analysis-title">
            🔍 {html.escape(name)} ({code}) · 정밀 분석
            </div>
            """,
            unsafe_allow_html=True
        )

        df = load_price_data(code)

        if df.empty:

            st.warning(
                "가격 데이터를 불러오지 못했습니다."
            )

            return

        d = calculate_indicators(df)

        last = d.iloc[-1]

        close = float(
            last["Close"]
        )

        prev = (
            float(d.iloc[-2]["Close"])
            if len(d) >= 2
            else close
        )

        change_pct = (
            (close - prev) /
            prev * 100
            if prev != 0
            else 0
        )

        c1, c2 = st.columns(2)

        with c1:

            st.markdown(
                f"""
                <div class="metric-label">
                현재가
                </div>

                <div class="metric-value">
                {close:,.0f}원
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:

            st.markdown(
                f"""
                <div class="metric-label">
                전일 대비
                </div>

                <div class="metric-value">
                {change_pct:+.2f}%
                </div>
                """,
                unsafe_allow_html=True
            )

        render_judgment(
            d,
            compact=True
        )

        render_scenarios(
            d,
            compact=True
        )

        st.markdown(
            "### 📈 차트"
        )

        render_chart(d)

        if st.button(
            "📊 내 ETF 화면에서 보기",
            key=f"move_my_etf_{code}",
            use_container_width=True
        ):

            st.session_state.selected_code = code

            st.session_state.future_detail_code = None

            # 현재 위젯 key를 직접 변경하지 않고
            # 다음 rerun 전에 target을 전달한다.
            st.session_state.main_nav_target = "📊 내 ETF"

            st.rerun()


# ============================================================
# FUTURE THEME
# ============================================================

def render_future_theme():

    st.markdown(
        '<div class="section-title">🔮 미래테마</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-subtitle">
        현재 주도 → 다음 수혜 → 초기 관심 순서로
        AI 산업 확산에 따른 ETF 흐름을 확인합니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "🔄 테마 업데이트",
        key="theme_update",
        use_container_width=True
    ):

        st.session_state.theme_cache = {}

        st.session_state.theme_last_update = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        )

        st.success(
            "미래테마 데이터가 새로고침되었습니다."
        )

    if st.session_state.theme_last_update:

        st.caption(
            "최근 업데이트: "
            + st.session_state.theme_last_update
        )

    for stage, themes in FUTURE_CHAIN.items():

        st.markdown(
            f"## {stage}"
        )

        for theme, codes in themes.items():

            st.markdown(
                f"""
                <div class="future-theme-card">

                <div class="future-theme-stage">
                {html.escape(stage)}
                </div>

                <div class="future-theme-title">
                {html.escape(theme)}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            rows = []

            for code in codes:

                code = str(code).zfill(6)

                name = get_etf_name(code)

                df = load_price_data(code)

                if df.empty:

                    rows.append(
                        {
                            "code": code,
                            "name": name,
                            "price": None,
                            "ret20": None,
                            "judgment": "데이터 없음"
                        }
                    )

                    continue

                d = calculate_indicators(df)

                last = d.iloc[-1]

                price = float(
                    last["Close"]
                )

                ret20 = (
                    float(last["RET20"])
                    if pd.notna(last["RET20"])
                    else 0
                )

                judgment = get_judgment(d)

                rows.append(
                    {
                        "code": code,
                        "name": name,
                        "price": price,
                        "ret20": ret20,
                        "judgment": (
                            judgment["title"]
                            if judgment
                            else "-"
                        )
                    }
                )

            # ------------------------------------------------
            # 카드
            # ------------------------------------------------

            cols = st.columns(
                min(3, max(1, len(rows)))
            )

            for i, item in enumerate(rows):

                with cols[i]:

                    st.markdown(
                        f"""
                        <div class="future-theme-card">

                        <div style="
                            font-size:15px;
                            font-weight:800;
                            margin-bottom:5px;
                        ">
                        {html.escape(item["name"])}
                        </div>

                        <div class="small-text">
                        {item["code"]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if item["price"] is not None:

                        st.markdown(
                            f"""
                            <div style="
                                font-size:18px;
                                font-weight:800;
                                margin-top:8px;
                            ">
                            {item["price"]:,.0f}원
                            </div>

                            <div class="small-text">
                            20일 수익률
                            {item["ret20"]:+.1f}%
                            </div>

                            <div class="small-text">
                            {html.escape(item["judgment"])}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    else:

                        st.caption(
                            "가격 데이터 없음"
                        )

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )

                    # ------------------------------------------------
                    # 핵심 수정:
                    # 클릭한 카드 바로 아래에서 분석을 렌더링한다.
                    # ------------------------------------------------

                    is_active = (
                        st.session_state.get(
                            "future_detail_code"
                        )
                        == item["code"]
                    )

                    button_text = (
                        "✕ 분석 닫기"
                        if is_active
                        else "📊 ETF 분석"
                    )

                    if st.button(
                        button_text,
                        key=(
                            f"future_analysis_"
                            f"{stage}_"
                            f"{theme}_"
                            f"{item['code']}"
                        ),
                        use_container_width=True
                    ):

                        if is_active:

                            st.session_state.future_detail_code = None

                        else:

                            st.session_state.future_detail_code = item["code"]

                        st.rerun()

                    # --------------------------------------------
                    # 분석 결과가 바로 이 버튼 아래에 나온다.
                    # --------------------------------------------

                    if (
                        st.session_state.get(
                            "future_detail_code"
                        )
                        == item["code"]
                    ):

                        render_future_detail(
                            item
                        )


# ============================================================
# HOLDINGS
# ============================================================

def render_holdings():

    st.markdown(
        '<div class="section-title">💼 보유 ETF</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.holdings:

        st.info(
            "등록된 보유 ETF가 없습니다."
        )

        return

    for code, info in st.session_state.holdings.items():

        code = str(code).zfill(6)

        name = get_etf_name(code)

        if isinstance(info, dict):

            quantity = info.get(
                "quantity",
                0
            )

            avg_price = info.get(
                "avg_price",
                0
            )

        else:

            quantity = 0
            avg_price = 0

        st.markdown(
            f"""
            <div class="dashboard-card">

            <div style="font-size:16px;font-weight:800;">
            {html.escape(name)}
            </div>

            <div class="small-text">
            {code}
            </div>

            <div style="margin-top:8px;">
            보유수량 {quantity:,}주
            </div>

            <div>
            평균단가 {avg_price:,.0f}원
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# NAV TARGET 처리
#
# 반드시 radio가 생성되기 전에 실행
# ============================================================

if st.session_state.get(
    "main_nav_target"
):

    st.session_state.main_nav = (
        st.session_state.main_nav_target
    )

    st.session_state.main_nav_target = None


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div style="
        padding:8px 2px 14px 2px;
    ">

        <div style="
            font-size:27px;
            font-weight:900;
            color:#111827;
        ">
        📊 ETF RADAR
        </div>

        <div style="
            font-size:13px;
            color:#7a8495;
            margin-top:3px;
        ">
        AI · 반도체 · 전력 · 미래테마 ETF 분석
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# MAIN NAV
# ============================================================

nav = st.radio(
    "메뉴",
    [
        "📊 내 ETF",
        "🔎 ETF 찾기",
        "🔮 미래테마"
    ],
    horizontal=True,
    key="main_nav",
    label_visibility="collapsed"
)


# ============================================================
# MAIN
# ============================================================

if nav == "📊 내 ETF":

    render_watchlist()

    st.divider()

    if st.session_state.selected_code:

        render_etf_analysis(
            st.session_state.selected_code
        )

    else:

        st.info(
            "관심 ETF를 선택하거나 ETF 찾기에서 분석할 종목을 선택하세요."
        )

    st.divider()

    render_holdings()


elif nav == "🔎 ETF 찾기":

    render_finder()

    st.divider()

    render_watchlist()


elif nav == "🔮 미래테마":

    render_future_theme()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#9aa3b2;
        font-size:11px;
        padding:20px 0 5px 0;
    ">
    ETF RADAR · Technical analysis based on market data
    </div>
    """,
    unsafe_allow_html=True
)