# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import html
import json
import os
from datetime import datetime


# ============================================================
# ETF RADAR
# Stable Mobile Financial Dashboard
# v12 - Stability / Korean Font / ETF Analysis Fix
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# 1. GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       기본
    -------------------------------------------------------- */

    html, body, [class*="css"] {
        font-family:
            "Noto Sans KR",
            "Noto Sans CJK KR",
            "Apple SD Gothic Neo",
            "Malgun Gothic",
            Arial,
            sans-serif;
    }

    .stApp {
        background: #f5f7fa;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* --------------------------------------------------------
       모바일
    -------------------------------------------------------- */

    @media (max-width: 768px) {

        .block-container {
            padding-left: 0.7rem;
            padding-right: 0.7rem;
            padding-top: 0.6rem;
        }

        h1 {
            font-size: 1.45rem !important;
        }

        h2 {
            font-size: 1.15rem !important;
        }

        h3 {
            font-size: 1rem !important;
        }

        .metric-card {
            padding: 12px !important;
        }

        .metric-value {
            font-size: 1.35rem !important;
        }

        .scenario-card {
            padding: 12px !important;
        }
    }

    /* --------------------------------------------------------
       Header
    -------------------------------------------------------- */

    .radar-header {
        background: linear-gradient(
            135deg,
            #111827 0%,
            #1f2937 55%,
            #111827 100%
        );

        color: white;
        border-radius: 18px;
        padding: 20px 22px;
        margin-bottom: 15px;

        box-shadow:
            0 8px 24px rgba(15, 23, 42, 0.14);
    }

    .radar-title {
        font-size: 1.55rem;
        font-weight: 800;
        letter-spacing: -0.04em;
    }

    .radar-subtitle {
        margin-top: 5px;
        color: #cbd5e1;
        font-size: 0.82rem;
    }

    /* --------------------------------------------------------
       카드
    -------------------------------------------------------- */

    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 16px;
        border: 1px solid #e5e7eb;

        box-shadow:
            0 4px 14px rgba(15, 23, 42, 0.05);

        min-height: 105px;
    }

    .metric-label {
        color: #64748b;
        font-size: 0.76rem;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .metric-value {
        color: #111827;
        font-size: 1.55rem;
        font-weight: 800;
        letter-spacing: -0.04em;
    }

    .metric-sub {
        margin-top: 4px;
        color: #94a3b8;
        font-size: 0.72rem;
    }

    /* --------------------------------------------------------
       분석 결과
    -------------------------------------------------------- */

    .analysis-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 17px;
        padding: 17px;
        margin-top: 12px;

        box-shadow:
            0 5px 18px rgba(15, 23, 42, 0.05);
    }

    .section-title {
        font-size: 1rem;
        font-weight: 800;
        color: #111827;
        margin-bottom: 9px;
    }

    .section-desc {
        color: #64748b;
        font-size: 0.78rem;
        line-height: 1.55;
    }

    /* --------------------------------------------------------
       상태
    -------------------------------------------------------- */

    .status-box {
        border-radius: 14px;
        padding: 15px;
        margin-top: 10px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
    }

    .status-title {
        font-weight: 800;
        font-size: 0.92rem;
        color: #111827;
    }

    .status-text {
        margin-top: 6px;
        color: #475569;
        font-size: 0.78rem;
        line-height: 1.6;
    }

    /* --------------------------------------------------------
       시나리오
    -------------------------------------------------------- */

    .scenario-card {
        background: white;
        border-radius: 15px;
        border: 1px solid #e5e7eb;
        padding: 15px;
        min-height: 160px;

        box-shadow:
            0 4px 14px rgba(15, 23, 42, 0.04);
    }

    .scenario-title {
        font-weight: 800;
        font-size: 0.92rem;
        margin-bottom: 8px;
        color: #111827;
    }

    .scenario-price {
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 6px;
        color: #0f172a;
    }

    .scenario-text {
        font-size: 0.76rem;
        color: #475569;
        line-height: 1.55;
    }

    /* --------------------------------------------------------
       가격대
    -------------------------------------------------------- */

    .price-zone {
        background: #f8fafc;
        border-radius: 12px;
        padding: 12px 14px;
        margin-top: 7px;
        border: 1px solid #e2e8f0;
    }

    .price-zone-title {
        color: #64748b;
        font-size: 0.72rem;
        font-weight: 700;
    }

    .price-zone-value {
        margin-top: 4px;
        font-size: 1rem;
        font-weight: 800;
        color: #111827;
    }

    /* --------------------------------------------------------
       안내
    -------------------------------------------------------- */

    .notice {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 13px;
        padding: 12px 14px;
        color: #1e3a8a;
        font-size: 0.76rem;
        line-height: 1.55;
    }

    .warning {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        border-radius: 13px;
        padding: 12px 14px;
        color: #9a3412;
        font-size: 0.76rem;
        line-height: 1.55;
    }

    /* --------------------------------------------------------
       ETF list
    -------------------------------------------------------- */

    .etf-row {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 13px;
        padding: 11px 13px;
        margin-bottom: 7px;
    }

    .etf-name {
        font-size: 0.86rem;
        font-weight: 800;
        color: #111827;
    }

    .etf-code {
        color: #94a3b8;
        font-size: 0.68rem;
        margin-top: 3px;
    }

    /* --------------------------------------------------------
       Streamlit 기본 요소
    -------------------------------------------------------- */

    div[data-testid="stButton"] > button {
        border-radius: 11px;
        min-height: 42px;
        font-weight: 700;
    }

    div[data-testid="stDownloadButton"] > button {
        border-radius: 11px;
        font-weight: 700;
    }

    /* dataframe */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 2. ETF DATABASE
# ============================================================

ETF_DATABASE = {

    "KODEX AI반도체TOP2플러스": {
        "ticker": "0124Z0.KS",
        "theme": "AI 반도체",
        "holding": True
    },

    "KODEX AI반도체핵심장비": {
        "ticker": "471990.KS",
        "theme": "반도체 핵심장비",
        "holding": False
    },

    "KODEX 반도체": {
        "ticker": "091160.KS",
        "theme": "반도체",
        "holding": False
    },

    "TIGER 반도체": {
        "ticker": "091230.KS",
        "theme": "반도체",
        "holding": False
    },

    "KODEX AI전력핵심설비": {
        "ticker": "487240.KS",
        "theme": "전력 인프라",
        "holding": False
    },

    "TIGER AI전력인프라": {
        "ticker": "487130.KS",
        "theme": "전력 인프라",
        "holding": False
    },

    "KODEX 미국AI테크TOP10": {
        "ticker": "485540.KS",
        "theme": "미국 AI",
        "holding": False
    },

    "TIGER 미국테크TOP10 INDXX": {
        "ticker": "381170.KS",
        "theme": "미국 AI",
        "holding": False
    },

    "KODEX 미국나스닥100": {
        "ticker": "379810.KS",
        "theme": "미국 기술주",
        "holding": False
    },

    "TIGER 미국나스닥100": {
        "ticker": "133690.KS",
        "theme": "미국 기술주",
        "holding": False
    },

    "KODEX K-신재생에너지액티브": {
        "ticker": "385510.KS",
        "theme": "신재생에너지",
        "holding": False
    },

    "TIGER 2차전지테마": {
        "ticker": "305540.KS",
        "theme": "2차전지",
        "holding": False
    },

    "KODEX 2차전지산업": {
        "ticker": "305720.KS",
        "theme": "2차전지",
        "holding": False
    },

    "TIGER 글로벌AI&로보틱스 INDXX": {
        "ticker": "464310.KS",
        "theme": "AI 로봇",
        "holding": False
    },

    "KODEX K-로봇액티브": {
        "ticker": "445290.KS",
        "theme": "AI 로봇",
        "holding": False
    }
}


# ============================================================
# 3. FUTURE THEMES
# ============================================================

FUTURE_THEMES = {
    "AI 반도체": [
        "AI 반도체",
        "HBM",
        "반도체 핵심장비",
        "반도체 소재·부품"
    ],

    "전력 인프라": [
        "전력망",
        "변압기",
        "전선",
        "전력기기",
        "AI 데이터센터 전력"
    ],

    "광통신": [
        "광통신",
        "데이터센터 네트워크",
        "광트랜시버",
        "AI 네트워크"
    ],

    "AI 로봇": [
        "휴머노이드",
        "산업용 로봇",
        "서비스 로봇",
        "AI 로봇"
    ],

    "우주·방산": [
        "우주항공",
        "위성",
        "방산",
        "드론"
    ]
}


# ============================================================
# 4. SESSION STATE
# ============================================================

if "selected_etf" not in st.session_state:
    st.session_state.selected_etf = None

if "analysis_requested" not in st.session_state:
    st.session_state.analysis_requested = False

if "theme_filter" not in st.session_state:
    st.session_state.theme_filter = "전체"

if "last_update" not in st.session_state:
    st.session_state.last_update = None


# ============================================================
# 5. UTILITY
# ============================================================

def safe_text(value, default="-"):
    """
    화면에 표시할 문자열을 안전하게 정리합니다.
    """

    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    text = str(value)

    if not text.strip():
        return default

    return html.escape(text)


def safe_float(value, default=np.nan):
    try:
        if value is None:
            return default

        result = float(value)

        if not np.isfinite(result):
            return default

        return result

    except Exception:
        return default


def format_price(value):

    value = safe_float(value)

    if np.isnan(value):
        return "-"

    return f"{value:,.0f}"


def format_pct(value):

    value = safe_float(value)

    if np.isnan(value):
        return "-"

    return f"{value:+.2f}%"


# ============================================================
# 6. DATA DOWNLOAD
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner=False
)
def get_price_data(ticker, period="6mo"):

    try:

        if not ticker:
            return pd.DataFrame()

        data = yf.download(
            ticker,
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False
        )

        if data is None or data.empty:
            return pd.DataFrame()

        # yfinance MultiIndex 처리
        if isinstance(data.columns, pd.MultiIndex):

            try:
                data.columns = data.columns.get_level_values(0)
            except Exception:
                data.columns = [
                    str(c[0]) if isinstance(c, tuple) else str(c)
                    for c in data.columns
                ]

        data = data.copy()

        required = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]

        for col in required:

            if col not in data.columns:
                data[col] = np.nan

        data = data[required]

        for col in required:
            data[col] = pd.to_numeric(
                data[col],
                errors="coerce"
            )

        data = data.dropna(
            subset=["Close"]
        )

        if data.empty:
            return pd.DataFrame()

        return data

    except Exception:
        return pd.DataFrame()


# ============================================================
# 7. TECHNICAL INDICATORS
# ============================================================

def calculate_indicators(df):

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # 이동평균
    df["MA5"] = close.rolling(5).mean()
    df["MA20"] = close.rolling(20).mean()
    df["MA60"] = close.rolling(60).mean()

    # RSI
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    df["RSI"] = 100 - (
        100 / (1 + rs)
    )

    # 거래량 평균
    df["VOL20"] = volume.rolling(20).mean()

    # 볼린저
    df["BB_MID"] = close.rolling(20).mean()
    df["BB_STD"] = close.rolling(20).std()

    df["BB_UPPER"] = (
        df["BB_MID"] +
        df["BB_STD"] * 2
    )

    df["BB_LOWER"] = (
        df["BB_MID"] -
        df["BB_STD"] * 2
    )

    # 최근 고저
    df["HIGH20"] = high.rolling(20).max()
    df["LOW20"] = low.rolling(20).min()

    df["HIGH60"] = high.rolling(60).max()
    df["LOW60"] = low.rolling(60).min()

    # 수익률
    df["RET5"] = close.pct_change(5) * 100
    df["RET20"] = close.pct_change(20) * 100

    return df


# ============================================================
# 8. SUPPORT / RESISTANCE
# ============================================================

def calculate_support_resistance(df):

    if df is None or df.empty:
        return {
            "support1": np.nan,
            "support2": np.nan,
            "resistance1": np.nan,
            "resistance2": np.nan
        }

    close = safe_float(df["Close"].iloc[-1])

    low20 = safe_float(
        df["Low"].tail(20).min()
    )

    high20 = safe_float(
        df["High"].tail(20).max()
    )

    low60 = safe_float(
        df["Low"].tail(60).min()
    )

    high60 = safe_float(
        df["High"].tail(60).max()
    )

    ma20 = safe_float(
        df["MA20"].iloc[-1]
    )

    ma60 = safe_float(
        df["MA60"].iloc[-1]
    )

    supports = [
        x for x in [
            low20,
            low60,
            ma20,
            ma60
        ]
        if np.isfinite(x)
        and x < close
    ]

    resistances = [
        x for x in [
            high20,
            high60
        ]
        if np.isfinite(x)
        and x > close
    ]

    supports = sorted(
        supports,
        reverse=True
    )

    resistances = sorted(
        resistances
    )

    return {
        "support1": supports[0]
        if len(supports) > 0
        else close * 0.97,

        "support2": supports[1]
        if len(supports) > 1
        else close * 0.94,

        "resistance1": resistances[0]
        if len(resistances) > 0
        else close * 1.04,

        "resistance2": resistances[1]
        if len(resistances) > 1
        else close * 1.08
    }


# ============================================================
# 9. SCORE
# ============================================================

def calculate_score(df):

    if df is None or df.empty:
        return {
            "score": 0,
            "trend": "데이터 부족",
            "reason": "가격 데이터를 불러오지 못했습니다."
        }

    last = df.iloc[-1]

    close = safe_float(last["Close"])
    ma5 = safe_float(last["MA5"])
    ma20 = safe_float(last["MA20"])
    ma60 = safe_float(last["MA60"])
    rsi = safe_float(last["RSI"])
    ret5 = safe_float(last["RET5"])
    ret20 = safe_float(last["RET20"])

    score = 50

    reasons = []

    # 추세
    if np.isfinite(ma20) and close > ma20:
        score += 10
        reasons.append("현재가가 20일선 위에 있습니다.")
    else:
        score -= 8
        reasons.append("현재가가 20일선 아래입니다.")

    if (
        np.isfinite(ma20)
        and np.isfinite(ma60)
        and ma20 > ma60
    ):
        score += 12
        reasons.append("20일선이 60일선 위에 있어 중기 추세가 양호합니다.")

    elif (
        np.isfinite(ma20)
        and np.isfinite(ma60)
    ):
        score -= 10
        reasons.append("20일선이 60일선 아래에 있습니다.")

    # 단기 모멘텀
    if np.isfinite(ret5):

        if ret5 > 5:
            score += 7
            reasons.append("최근 5거래일 상승 모멘텀이 강합니다.")

        elif ret5 < -5:
            score -= 7
            reasons.append("최근 5거래일 조정폭이 큽니다.")

    # RSI
    if np.isfinite(rsi):

        if 50 <= rsi <= 68:
            score += 8
            reasons.append("RSI가 상승 추세에서 비교적 건강한 구간입니다.")

        elif rsi > 75:
            score -= 5
            reasons.append("RSI가 높아 단기 추격 위험이 있습니다.")

        elif rsi < 35:
            score += 3
            reasons.append("RSI가 낮아 기술적 반등 가능성을 확인할 필요가 있습니다.")

    score = int(
        max(
            0,
            min(
                100,
                score
            )
        )
    )

    if score >= 75:
        trend = "강한 상승"
    elif score >= 62:
        trend = "상승 우위"
    elif score >= 48:
        trend = "중립"
    elif score >= 35:
        trend = "조정"
    else:
        trend = "약세"

    return {
        "score": score,
        "trend": trend,
        "reason": " ".join(reasons)
    }


# ============================================================
# 10. BUY / HOLD / TAKE PROFIT
# ============================================================

def make_action(df, sr, score_data):

    if df is None or df.empty:
        return {
            "status": "분석 불가",
            "action": "데이터 확인",
            "text": "가격 데이터를 불러오지 못했습니다."
        }

    close = safe_float(
        df["Close"].iloc[-1]
    )

    support1 = safe_float(
        sr["support1"]
    )

    resistance1 = safe_float(
        sr["resistance1"]
    )

    score = score_data["score"]

    if not np.isfinite(close):
        return {
            "status": "분석 불가",
            "action": "데이터 확인",
            "text": "현재 가격을 확인할 수 없습니다."
        }

    # 추격 방지
    if (
        score >= 75
        and np.isfinite(resistance1)
        and close >= resistance1 * 0.98
    ):

        return {
            "status": "상승 추세 / 추격주의",
            "action": "보유 또는 눌림 대기",
            "text":
                "추세는 양호하지만 주요 저항선 부근에서는 "
                "추격매수보다 눌림 확인 후 접근하는 전략이 유리합니다."
        }

    if (
        score >= 62
        and np.isfinite(support1)
        and close > support1
    ):

        return {
            "status": "상승 추세",
            "action": "보유 / 눌림매수",
            "text":
                "중기 추세가 유지되는 구간입니다. "
                "현재가를 무리하게 추격하기보다 지지선 부근의 "
                "거래량과 반등 여부를 확인하는 접근이 적절합니다."
        }

    if score >= 48:

        return {
            "status": "중립",
            "action": "관망",
            "text":
                "추세 방향이 아직 명확하지 않습니다. "
                "20일선 회복 또는 주요 저항 돌파 여부를 확인할 필요가 있습니다."
        }

    return {
        "status": "조정",
        "action": "매수 대기 / 손실관리",
        "text":
            "단기 조정 신호가 우세합니다. "
            "지지선 이탈 여부를 확인한 뒤 대응하는 것이 필요합니다."
    }


# ============================================================
# 11. SCENARIOS
# ============================================================

def make_scenarios(df, sr):

    if df is None or df.empty:
        return []

    close = safe_float(
        df["Close"].iloc[-1]
    )

    support1 = safe_float(sr["support1"])
    support2 = safe_float(sr["support2"])
    resistance1 = safe_float(sr["resistance1"])
    resistance2 = safe_float(sr["resistance2"])

    return [

        {
            "title": "상승 시나리오",
            "price":
                f"{format_price(resistance1)} → "
                f"{format_price(resistance2)}",
            "text":
                "거래량 증가와 함께 1차 저항을 돌파하면 "
                "다음 저항선까지 상승 여지를 확인합니다. "
                "돌파 직후에는 눌림 확인이 중요합니다."
        },

        {
            "title": "중립 시나리오",
            "price":
                f"{format_price(support1)} ~ "
                f"{format_price(resistance1)}",
            "text":
                "주요 지지와 저항 사이에서 움직이면 "
                "추세 확인 전까지 신규매수보다 관망 비중을 높입니다."
        },

        {
            "title": "조정 시나리오",
            "price":
                f"{format_price(support1)} → "
                f"{format_price(support2)}",
            "text":
                "1차 지지선을 이탈하면 2차 지지선까지 "
                "조정 가능성을 열어두고 대응합니다. "
                "거래량 증가를 동반한 이탈은 특히 주의합니다."
        }
    ]


# ============================================================
# 12. CHART
# ============================================================

def make_chart(df, name):

    if df is None or df.empty:
        return None

    chart = go.Figure()

    chart.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="가격"
        )
    )

    if "MA20" in df.columns:

        chart.add_trace(
            go.Scatter(
                x=df.index,
                y=df["MA20"],
                mode="lines",
                name="20일선",
                line=dict(width=1.5)
            )
        )

    if "MA60" in df.columns:

        chart.add_trace(
            go.Scatter(
                x=df.index,
                y=df["MA60"],
                mode="lines",
                name="60일선",
                line=dict(width=1.5)
            )
        )

    chart.update_layout(

        title=safe_text(name),

        height=390,

        margin=dict(
            l=5,
            r=5,
            t=45,
            b=5
        ),

        xaxis_rangeslider_visible=False,

        font=dict(
            family=
            "Noto Sans KR, Noto Sans CJK KR, "
            "Malgun Gothic, Arial"
        ),

        paper_bgcolor="white",
        plot_bgcolor="white",

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0
        ),

        hovermode="x unified"
    )

    return chart


# ============================================================
# 13. ETF ANALYSIS FUNCTION
# ============================================================

def analyze_etf(name):

    if name not in ETF_DATABASE:
        return None

    info = ETF_DATABASE[name]

    ticker = info.get("ticker")

    if not ticker:
        return None

    raw = get_price_data(
        ticker,
        period="6mo"
    )

    if raw.empty:
        return {
            "name": name,
            "ticker": ticker,
            "info": info,
            "data": pd.DataFrame(),
            "error": True
        }

    data = calculate_indicators(raw)

    sr = calculate_support_resistance(
        data
    )

    score_data = calculate_score(
        data
    )

    action = make_action(
        data,
        sr,
        score_data
    )

    scenarios = make_scenarios(
        data,
        sr
    )

    return {
        "name": name,
        "ticker": ticker,
        "info": info,
        "data": data,
        "sr": sr,
        "score": score_data,
        "action": action,
        "scenarios": scenarios,
        "error": False
    }


# ============================================================
# 14. HEADER
# ============================================================

st.markdown(
    """
    <div class="radar-header">

        <div class="radar-title">
            📊 ETF RADAR
        </div>

        <div class="radar-subtitle">
            보유 · 관심 ETF 기술적 분석 / 지지·저항 / 가격구간 / 대응 시나리오
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 15. TOP TABS
# ============================================================

tab1, tab2, tab3 = st.tabs(
    [
        "📊 ETF 분석",
        "🔎 ETF 찾기",
        "🚀 미래 테마"
    ]
)


# ============================================================
# TAB 1 : ETF ANALYSIS
# ============================================================

with tab1:

    names = list(
        ETF_DATABASE.keys()
    )

    if not names:

        st.warning(
            "등록된 ETF가 없습니다."
        )

    else:

        # --------------------------------------------
        # ETF 선택
        # --------------------------------------------

        default_index = 0

        if (
            st.session_state.selected_etf
            in names
        ):

            default_index = names.index(
                st.session_state.selected_etf
            )

        selected = st.selectbox(
            "분석할 ETF",
            names,
            index=default_index,
            key="analysis_select"
        )

        # --------------------------------------------
        # 핵심 수정
        #
        # 버튼 클릭 -> session_state에 종목 저장
        # -> rerun -> 분석
        # --------------------------------------------

        col1, col2 = st.columns(
            [2, 1]
        )

        with col1:

            if st.button(
                "📈 ETF 분석",
                key="btn_analyze",
                use_container_width=True
            ):

                st.session_state.selected_etf = selected
                st.session_state.analysis_requested = True

                st.rerun()

        with col2:

            if st.button(
                "🔄 데이터 새로고침",
                key="btn_refresh",
                use_container_width=True
            ):

                get_price_data.clear()

                st.session_state.selected_etf = selected
                st.session_state.analysis_requested = True

                st.rerun()

        # --------------------------------------------
        # 분석 대상
        # --------------------------------------------

        if (
            st.session_state.analysis_requested
            and st.session_state.selected_etf
        ):

            target = (
                st.session_state.selected_etf
            )

            with st.spinner(
                f"{target} 분석 중..."
            ):

                result = analyze_etf(
                    target
                )

            if result is None:

                st.error(
                    "ETF 분석 정보를 찾을 수 없습니다."
                )

            elif result.get("error"):

                st.warning(
                    f"""
                    **{safe_text(target)}**

                    현재 가격 데이터를 불러오지 못했습니다.

                    티커:
                    `{safe_text(result.get("ticker"))}`

                    잠시 후 데이터 새로고침을 다시 눌러주세요.
                    """
                )

            else:

                data = result["data"]
                score = result["score"]
                action = result["action"]
                sr = result["sr"]

                current = safe_float(
                    data["Close"].iloc[-1]
                )

                previous = (
                    safe_float(
                        data["Close"].iloc[-2]
                    )
                    if len(data) >= 2
                    else current
                )

                day_change = (
                    (current / previous - 1) * 100
                    if (
                        np.isfinite(current)
                        and np.isfinite(previous)
                        and previous != 0
                    )
                    else np.nan
                )

                rsi = safe_float(
                    data["RSI"].iloc[-1]
                )

                ret20 = safe_float(
                    data["RET20"].iloc[-1]
                )

                # ----------------------------------------
                # 제목
                # ----------------------------------------

                st.markdown(
                    f"""
                    <div class="analysis-card">

                        <div class="section-title">
                            {safe_text(target)}
                        </div>

                        <div class="section-desc">
                            {safe_text(result["info"].get("theme"))}
                            ·
                            {safe_text(result["ticker"])}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # ----------------------------------------
                # 핵심 지표
                # ----------------------------------------

                c1, c2, c3, c4 = st.columns(4)

                with c1:

                    st.markdown(
                        f"""
                        <div class="metric-card">

                            <div class="metric-label">
                                현재가
                            </div>

                            <div class="metric-value">
                                {format_price(current)}
                            </div>

                            <div class="metric-sub">
                                전일 대비 {format_pct(day_change)}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with c2:

                    st.markdown(
                        f"""
                        <div class="metric-card">

                            <div class="metric-label">
                                종합점수
                            </div>

                            <div class="metric-value">
                                {score["score"]}/100
                            </div>

                            <div class="metric-sub">
                                {safe_text(score["trend"])}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with c3:

                    st.markdown(
                        f"""
                        <div class="metric-card">

                            <div class="metric-label">
                                RSI
                            </div>

                            <div class="metric-value">
                                {format_price(rsi)}
                            </div>

                            <div class="metric-sub">
                                14일 기준
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with c4:

                    st.markdown(
                        f"""
                        <div class="metric-card">

                            <div class="metric-label">
                                20일 수익률
                            </div>

                            <div class="metric-value">
                                {format_pct(ret20)}
                            </div>

                            <div class="metric-sub">
                                최근 20거래일
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # ----------------------------------------
                # 현재 상태
                # ----------------------------------------

                st.markdown(
                    """
                    <div class="analysis-card">

                        <div class="section-title">
                            현재 상태
                        </div>

                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="status-box">

                        <div class="status-title">
                            {safe_text(action["status"])}
                            ·
                            {safe_text(action["action"])}
                        </div>

                        <div class="status-text">
                            {safe_text(action["text"])}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class="status-box">

                        <div class="status-title">
                            판단 근거
                        </div>

                        <div class="status-text">
                            {safe_text(score["reason"])}
                        </div>

                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # ----------------------------------------
                # 가격 구간
                # ----------------------------------------

                st.markdown(
                    """
                    <div class="analysis-card">

                        <div class="section-title">
                            주요 가격 구간
                        </div>

                    """,
                    unsafe_allow_html=True
                )

                p1, p2, p3, p4 = st.columns(4)

                with p1:

                    st.markdown(
                        f"""
                        <div class="price-zone">

                            <div class="price-zone-title">
                                2차 지지
                            </div>

                            <div class="price-zone-value">
                                {format_price(sr["support2"])}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with p2:

                    st.markdown(
                        f"""
                        <div class="price-zone">

                            <div class="price-zone-title">
                                1차 지지
                            </div>

                            <div class="price-zone-value">
                                {format_price(sr["support1"])}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with p3:

                    st.markdown(
                        f"""
                        <div class="price-zone">

                            <div class="price-zone-title">
                                1차 저항
                            </div>

                            <div class="price-zone-value">
                                {format_price(sr["resistance1"])}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with p4:

                    st.markdown(
                        f"""
                        <div class="price-zone">

                            <div class="price-zone-title">
                                2차 저항
                            </div>

                            <div class="price-zone-value">
                                {format_price(sr["resistance2"])}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

                # ----------------------------------------
                # 차트
                # ----------------------------------------

                st.markdown(
                    """
                    <div class="analysis-card">

                        <div class="section-title">
                            가격 추세
                        </div>

                    """,
                    unsafe_allow_html=True
                )

                chart = make_chart(
                    data.tail(120),
                    target
                )

                if chart is not None:
                    st.plotly_chart(
                        chart,
                        use_container_width=True,
                        config={
                            "displayModeBar": False
                        }
                    )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

                # ----------------------------------------
                # 시나리오
                # ----------------------------------------

                st.markdown(
                    """
                    <div class="analysis-card">

                        <div class="section-title">
                            대응 시나리오
                        </div>

                    """,
                    unsafe_allow_html=True
                )

                scenarios = result[
                    "scenarios"
                ]

                cols = st.columns(
                    len(scenarios)
                )

                for idx, scenario in enumerate(
                    scenarios
                ):

                    with cols[idx]:

                        st.markdown(
                            f"""
                            <div class="scenario-card">

                                <div class="scenario-title">
                                    {safe_text(scenario["title"])}
                                </div>

                                <div class="scenario-price">
                                    {safe_text(scenario["price"])}
                                </div>

                                <div class="scenario-text">
                                    {safe_text(scenario["text"])}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

                # ----------------------------------------
                # 데이터 표
                # ----------------------------------------

                with st.expander(
                    "세부 기술지표 보기"
                ):

                    view = data.tail(30).copy()

                    columns = [
                        "Close",
                        "MA5",
                        "MA20",
                        "MA60",
                        "RSI",
                        "RET5",
                        "RET20",
                        "Volume"
                    ]

                    columns = [
                        c for c in columns
                        if c in view.columns
                    ]

                    st.dataframe(
                        view[columns].round(2),
                        use_container_width=True
                    )


# ============================================================
# TAB 2 : ETF FINDER
# ============================================================

with tab2:

    st.markdown(
        """
        <div class="analysis-card">

            <div class="section-title">
                🔎 ETF 찾기
            </div>

            <div class="section-desc">
                테마와 보유 여부를 기준으로 분석 대상을 빠르게 찾습니다.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    themes = [
        "전체"
    ] + sorted(
        list(
            set(
                info["theme"]
                for info in ETF_DATABASE.values()
            )
        )
    )

    theme = st.selectbox(
        "테마",
        themes,
        key="finder_theme"
    )

    holding_option = st.radio(
        "보유 상태",
        [
            "전체",
            "보유중",
            "관심/미보유"
        ],
        horizontal=True,
        key="finder_holding"
    )

    filtered = []

    for name, info in ETF_DATABASE.items():

        if (
            theme != "전체"
            and info["theme"] != theme
        ):
            continue

        if (
            holding_option == "보유중"
            and not info["holding"]
        ):
            continue

        if (
            holding_option == "관심/미보유"
            and info["holding"]
        ):
            continue

        filtered.append(
            (name, info)
        )

    st.write("")

    if not filtered:

        st.info(
            "조건에 맞는 ETF가 없습니다."
        )

    else:

        for name, info in filtered:

            c1, c2 = st.columns(
                [4, 1]
            )

            with c1:

                st.markdown(
                    f"""
                    <div class="etf-row">

                        <div class="etf-name">
                            {safe_text(name)}
                        </div>

                        <div class="etf-code">
                            {safe_text(info["ticker"])}
                            ·
                            {safe_text(info["theme"])}
                            ·
                            {"보유중" if info["holding"] else "관심"}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with c2:

                if st.button(
                    "분석",
                    key=f"finder_{info['ticker']}_{name}"
                ):

                    st.session_state.selected_etf = name
                    st.session_state.analysis_requested = True

                    st.rerun()


# ============================================================
# TAB 3 : FUTURE THEMES
# ============================================================

with tab3:

    st.markdown(
        """
        <div class="analysis-card">

            <div class="section-title">
                🚀 미래 유망 테마
            </div>

            <div class="section-desc">
                AI 데이터센터와 반도체를 중심으로 중장기적으로
                확인할 필요가 있는 테마를 정리합니다.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------
    # 수동 업데이트 버튼
    # --------------------------------------------

    c1, c2 = st.columns(
        [2, 1]
    )

    with c1:

        if st.button(
            "🔄 테마 데이터 새로고침",
            key="theme_refresh",
            use_container_width=True
        ):

            get_price_data.clear()

            st.session_state.last_update = (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                )
            )

            st.rerun()

    with c2:

        if st.session_state.last_update:

            st.caption(
                f"업데이트: {st.session_state.last_update}"
            )

    st.write("")

    # --------------------------------------------
    # Theme cards
    # --------------------------------------------

    for theme_name, keywords in FUTURE_THEMES.items():

        st.markdown(
            f"""
            <div class="analysis-card">

                <div class="section-title">
                    {safe_text(theme_name)}
                </div>

                <div class="section-desc">
                    관련 키워드:
                    {safe_text(", ".join(keywords))}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        related = [
            (
                name,
                info
            )
            for name, info
            in ETF_DATABASE.items()
            if info["theme"] == theme_name
        ]

        if related:

            for name, info in related:

                c1, c2 = st.columns(
                    [4, 1]
                )

                with c1:

                    st.markdown(
                        f"""
                        <div class="etf-row">

                            <div class="etf-name">
                                {safe_text(name)}
                            </div>

                            <div class="etf-code">
                                {safe_text(info["ticker"])}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with c2:

                    if st.button(
                        "분석",
                        key=f"theme_{info['ticker']}_{name}"
                    ):

                        st.session_state.selected_etf = name
                        st.session_state.analysis_requested = True

                        # 분석 탭으로 이동시키기 위해
                        # 선택값만 저장
                        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        margin-top:25px;
        padding:15px;
        text-align:center;
        color:#94a3b8;
        font-size:0.7rem;
    ">
        ETF RADAR · Technical analysis based on market data
        <br>
        본 화면의 기술적 분석은 참고용이며 투자 판단은 사용자의 책임입니다.
    </div>
    """,
    unsafe_allow_html=True
)