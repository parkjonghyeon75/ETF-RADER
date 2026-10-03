# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import os
import json
import re
import urllib.request
import urllib.parse
import ssl
from datetime import datetime, timedelta


# ============================================================
# ETF RADAR
# Mobile Financial Dashboard
# ETF Search / Technical Analysis / Future Themes
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# 기본 CSS
# HTML container를 열고 닫는 방식은 사용하지 않음
# ============================================================

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 3rem;
    padding-left: 0.8rem;
    padding-right: 0.8rem;
}

h1 {
    font-size: 1.65rem !important;
}

h2 {
    font-size: 1.35rem !important;
}

h3 {
    font-size: 1.08rem !important;
}

div[data-testid="stMetric"] {
    padding: 0.2rem 0.2rem 0.2rem 0.2rem;
}

div[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
}

div[data-testid="stMetricValue"] {
    font-size: 1.05rem !important;
}

.stButton button {
    width: 100%;
}

[data-testid="stExpander"] {
    border-radius: 10px;
}

.small-note {
    font-size: 0.72rem;
}

.theme-title {
    font-size: 1.05rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 기본 ETF 목록
# ============================================================

BASE_ETFS = {
    "395160": "KODEX AI반도체핵심장비",
    "487240": "KODEX AI반도체",
    "471990": "KODEX AI반도체TOP2Plus",

    "133690": "TIGER 미국나스닥100",
    "360750": "TIGER 미국S&P500",
    "458730": "TIGER 글로벌AI&로봇",
    "381170": "TIGER 미국테크TOP10INDXX",

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
    "161510": "ACE 고배당주",
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
# 세션 상태
# ============================================================

if "watchlist" not in st.session_state:
    st.session_state.watchlist = DEFAULT_WATCHLIST.copy()

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "search_keyword" not in st.session_state:
    st.session_state.search_keyword = ""

if "selected_search_code" not in st.session_state:
    st.session_state.selected_search_code = None

if "search_generation" not in st.session_state:
    st.session_state.search_generation = 0

if "analysis_open" not in st.session_state:
    st.session_state.analysis_open = {}

if "theme_refresh" not in st.session_state:
    st.session_state.theme_refresh = 0


# ============================================================
# 유틸리티
# ============================================================

def normalize_text(value):
    """
    검색어 비교용 정규화.
    한글 띄어쓰기 / 영문 대소문자 / 특수문자 차이를 최대한 제거.
    """
    if value is None:
        return ""

    text = str(value).strip().lower()

    text = text.replace(" ", "")
    text = text.replace("-", "")
    text = text.replace("_", "")
    text = text.replace("/", "")
    text = text.replace(".", "")
    text = text.replace("&", "")
    text = text.replace("(", "")
    text = text.replace(")", "")

    return text


def safe_float(value, default=np.nan):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def format_price(value):
    value = safe_float(value)

    if pd.isna(value):
        return "-"

    if value >= 1000:
        return f"{value:,.0f}"

    return f"{value:,.2f}"


def format_pct(value):
    value = safe_float(value)

    if pd.isna(value):
        return "-"

    return f"{value:+.1f}%"


def clean_text(value):
    if value is None:
        return ""

    text = str(value)

    text = text.replace("\x00", "")
    text = text.replace("\r", " ")
    text = text.replace("\n", " ")

    return text.strip()


# ============================================================
# ETF 이름 표시
# ============================================================

def get_etf_name(code):
    code = str(code).replace(".KS", "").replace(".KQ", "")

    if code in BASE_ETFS:
        return BASE_ETFS[code]

    for item in st.session_state.search_results:
        if str(item.get("code")) == code:
            return item.get("name", code)

    return code


def get_display_name(code):
    code = str(code)

    name = get_etf_name(code)

    if name == code:
        return code

    return f"{name}  ({code})"


# ============================================================
# KRX ETF 전체 목록
# ============================================================

@st.cache_data(
    ttl=60 * 60 * 12,
    show_spinner=False
)
def load_krx_etf_universe():
    """
    KRX ETF 목록.

    pykrx가 작동하면 실제 KRX ETF 전체 목록을 가져온다.
    """
    rows = []

    try:
        from pykrx import stock

        today = datetime.now()

        dates = [
            today.strftime("%Y%m%d"),
            (today - timedelta(days=1)).strftime("%Y%m%d"),
            (today - timedelta(days=3)).strftime("%Y%m%d"),
            (today - timedelta(days=7)).strftime("%Y%m%d"),
        ]

        tickers = []

        for date_str in dates:
            try:
                tickers = stock.get_etf_ticker_list(date_str)

                if tickers:
                    break

            except Exception:
                continue

        if not tickers:
            return pd.DataFrame(columns=["code", "name", "source"])

        for code in tickers:
            try:
                name = stock.get_etf_ticker_name(code)

                if name:
                    rows.append({
                        "code": str(code),
                        "name": clean_text(name),
                        "source": "KRX"
                    })

            except Exception:
                continue

    except Exception:
        pass

    if not rows:
        return pd.DataFrame(columns=["code", "name", "source"])

    df = pd.DataFrame(rows)

    df = df.drop_duplicates("code")

    return df


# ============================================================
# 기본 ETF 목록
# ============================================================

def get_base_universe():
    rows = []

    for code, name in BASE_ETFS.items():
        rows.append({
            "code": str(code),
            "name": name,
            "source": "BASE"
        })

    return pd.DataFrame(rows)


# ============================================================
# Yahoo Finance 외부 검색
# ============================================================

@st.cache_data(
    ttl=60 * 30,
    show_spinner=False
)
def yahoo_search(keyword):
    """
    Yahoo Finance 검색 API를 이용한 외부 ETF 검색.

    예:
    AI반도체
    395160
    KODEX
    TIGER 반도체
    """
    keyword = clean_text(keyword)

    if not keyword:
        return pd.DataFrame(columns=["code", "name", "source"])

    rows = []

    try:
        encoded = urllib.parse.quote(keyword)

        url = (
            "https://query1.finance.yahoo.com/v1/finance/search?"
            f"q={encoded}"
            "&quotesCount=50"
            "&newsCount=0"
        )

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        context = ssl.create_default_context()

        with urllib.request.urlopen(
            req,
            timeout=8,
            context=context
        ) as response:

            raw = response.read().decode("utf-8")

        data = json.loads(raw)

        quotes = data.get("quotes", [])

        for quote in quotes:

            symbol = str(
                quote.get("symbol", "")
            )

            if not symbol.endswith(".KS"):
                continue

            code = symbol.replace(".KS", "")

            long_name = (
                quote.get("longname")
                or quote.get("shortname")
                or code
            )

            rows.append({
                "code": code,
                "name": clean_text(long_name),
                "source": "Yahoo"
            })

    except Exception:
        pass

    if not rows:
        return pd.DataFrame(columns=["code", "name", "source"])

    return pd.DataFrame(rows).drop_duplicates("code")


# ============================================================
# ETF 전체 Universe
# ============================================================

@st.cache_data(
    ttl=60 * 60 * 6,
    show_spinner=False
)
def get_external_universe():
    """
    KRX + 기본 ETF를 합친 Universe.
    """
    frames = []

    try:
        krx = load_krx_etf_universe()

        if not krx.empty:
            frames.append(krx)

    except Exception:
        pass

    base = get_base_universe()

    if not base.empty:
        frames.append(base)

    if not frames:
        return pd.DataFrame(
            columns=["code", "name", "source"]
        )

    result = pd.concat(
        frames,
        ignore_index=True
    )

    result["code"] = (
        result["code"]
        .astype(str)
        .str.replace(".KS", "", regex=False)
    )

    result["name"] = result["name"].astype(str)

    result = result.drop_duplicates(
        subset=["code"],
        keep="first"
    )

    return result.reset_index(drop=True)


# ============================================================
# ETF 검색
# ============================================================

def search_etfs(keyword, max_results=50):

    keyword = clean_text(keyword)

    if not keyword:
        return []

    normalized_keyword = normalize_text(keyword)

    result_map = {}

    # --------------------------------------------------------
    # 1. KRX + BASE 검색
    # --------------------------------------------------------

    try:
        universe = get_external_universe()

        if not universe.empty:

            for _, row in universe.iterrows():

                code = str(row["code"])
                name = clean_text(row["name"])

                n_code = normalize_text(code)
                n_name = normalize_text(name)

                score = 0

                # 정확한 코드
                if normalized_keyword == n_code:
                    score += 1000

                # 이름 정확 일치
                if normalized_keyword == n_name:
                    score += 900

                # 코드 포함
                if normalized_keyword in n_code:
                    score += 700

                # 이름 포함
                if normalized_keyword in n_name:
                    score += 600

                if score > 0:
                    result_map[code] = {
                        "code": code,
                        "name": name,
                        "source": row.get("source", "KRX"),
                        "score": score
                    }

    except Exception:
        pass

    # --------------------------------------------------------
    # 2. Yahoo 외부검색
    # --------------------------------------------------------

    try:
        yahoo = yahoo_search(keyword)

        if not yahoo.empty:

            for _, row in yahoo.iterrows():

                code = str(row["code"])
                name = clean_text(row["name"])

                if code in result_map:
                    result_map[code]["score"] += 300
                    continue

                n_code = normalize_text(code)
                n_name = normalize_text(name)

                score = 200

                if normalized_keyword == n_code:
                    score += 1000

                if normalized_keyword in n_name:
                    score += 500

                result_map[code] = {
                    "code": code,
                    "name": name,
                    "source": "Yahoo",
                    "score": score
                }

    except Exception:
        pass

    # --------------------------------------------------------
    # 3. 기본 ETF 직접검색
    # --------------------------------------------------------

    for code, name in BASE_ETFS.items():

        n_code = normalize_text(code)
        n_name = normalize_text(name)

        if (
            normalized_keyword in n_code
            or normalized_keyword in n_name
        ):

            if code not in result_map:

                result_map[code] = {
                    "code": code,
                    "name": name,
                    "source": "BASE",
                    "score": 400
                }

    # --------------------------------------------------------
    # 정렬
    # --------------------------------------------------------

    results = list(result_map.values())

    results.sort(
        key=lambda x: (
            -x["score"],
            x["name"]
        )
    )

    return results[:max_results]


# ============================================================
# Yahoo 가격 데이터
# ============================================================

@st.cache_data(
    ttl=60 * 15,
    show_spinner=False
)
def fetch_yahoo(code, period="1y"):

    code = str(code).replace(".KS", "")

    ticker = f"{code}.KS"

    try:

        df = yf.download(
            ticker,
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            return pd.DataFrame()

        # MultiIndex 처리
        if isinstance(df.columns, pd.MultiIndex):

            try:
                df.columns = df.columns.get_level_values(0)

            except Exception:
                df.columns = [
                    col[0]
                    if isinstance(col, tuple)
                    else col
                    for col in df.columns
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

        df = df.dropna(
            subset=["Close"]
        )

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# 보조지표
# ============================================================

def calculate_indicators(df):

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    close = df["Close"]

    df["MA20"] = close.rolling(20).mean()

    df["MA60"] = close.rolling(60).mean()

    df["Volume20"] = (
        df["Volume"]
        .rolling(20)
        .mean()
    )

    df["VolumeRatio"] = (
        df["Volume"]
        / df["Volume20"]
    )

    delta = close.diff()

    gain = delta.clip(
        lower=0
    )

    loss = -delta.clip(
        upper=0
    )

    avg_gain = gain.rolling(
        14
    ).mean()

    avg_loss = loss.rolling(
        14
    ).mean()

    rs = avg_gain / avg_loss.replace(
        0,
        np.nan
    )

    df["RSI"] = (
        100
        - (
            100
            / (1 + rs)
        )
    )

    df["Return20"] = (
        close.pct_change(20)
        * 100
    )

    df["Return60"] = (
        close.pct_change(60)
        * 100
    )

    return df


# ============================================================
# 지지 / 저항
# ============================================================

def calculate_levels(df):

    if df is None or df.empty:
        return {}

    current = safe_float(
        df["Close"].iloc[-1]
    )

    ma20 = safe_float(
        df["MA20"].iloc[-1]
    )

    ma60 = safe_float(
        df["MA60"].iloc[-1]
    )

    recent20 = df.tail(20)

    support1 = safe_float(
        recent20["Low"].min()
    )

    support2 = safe_float(
        df.tail(60)["Low"].min()
    )

    resistance1 = safe_float(
        recent20["High"].max()
    )

    resistance2 = safe_float(
        df.tail(60)["High"].max()
    )

    return {
        "current": current,
        "ma20": ma20,
        "ma60": ma60,
        "support1": support1,
        "support2": support2,
        "resistance1": resistance1,
        "resistance2": resistance2,
    }


# ============================================================
# 종합 판단
# ============================================================

def get_judgment(df):

    if df is None or df.empty:
        return {
            "score": 0,
            "trend": "데이터 부족",
            "action": "관찰",
            "reason": "가격 데이터가 충분하지 않습니다.",
            "rsi": np.nan,
            "volume_ratio": np.nan,
        }

    row = df.iloc[-1]

    current = safe_float(row["Close"])
    ma20 = safe_float(row["MA20"])
    ma60 = safe_float(row["MA60"])
    rsi = safe_float(row["RSI"])
    volume_ratio = safe_float(
        row["VolumeRatio"]
    )

    score = 50

    # --------------------------------------------------------
    # 추세
    # --------------------------------------------------------

    if (
        not pd.isna(ma20)
        and not pd.isna(ma60)
    ):

        if current > ma20 > ma60:
            score += 25
            trend = "상승 구조"

        elif current > ma20:
            score += 12
            trend = "단기 상승"

        elif current < ma20 < ma60:
            score -= 25
            trend = "하락 구조"

        elif current < ma20:
            score -= 12
            trend = "단기 약세"

        else:
            trend = "혼조"

    else:
        trend = "데이터 부족"

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    if not pd.isna(rsi):

        if 50 <= rsi < 70:
            score += 10

        elif 40 <= rsi < 50:
            score += 2

        elif rsi >= 70:
            score -= 3

        elif rsi < 30:
            score -= 5

    # --------------------------------------------------------
    # 거래량
    # --------------------------------------------------------

    if not pd.isna(volume_ratio):

        if volume_ratio >= 1.5:
            score += 10

        elif volume_ratio >= 1.1:
            score += 5

        elif volume_ratio < 0.7:
            score -= 5

    score = int(
        max(
            0,
            min(100, score)
        )
    )

    # --------------------------------------------------------
    # 액션
    # --------------------------------------------------------

    if score >= 75:
        action = "강세 확인"

    elif score >= 60:
        action = "관심 유지"

    elif score >= 45:
        action = "관망"

    else:
        action = "약세 주의"

    # --------------------------------------------------------
    # 판단 근거
    # --------------------------------------------------------

    reasons = []

    if (
        not pd.isna(ma20)
        and current > ma20
    ):
        reasons.append(
            "현재가가 20일선 위"
        )
    else:
        reasons.append(
            "현재가가 20일선 아래"
        )

    if (
        not pd.isna(ma60)
        and current > ma60
    ):
        reasons.append(
            "60일선 위"
        )
    else:
        reasons.append(
            "60일선 아래"
        )

    if not pd.isna(rsi):

        if rsi >= 70:
            reasons.append(
                "RSI 과열권"
            )

        elif rsi <= 30:
            reasons.append(
                "RSI 약세권"
            )

        else:
            reasons.append(
                "RSI 중립~정상권"
            )

    if not pd.isna(volume_ratio):

        if volume_ratio >= 1.5:
            reasons.append(
                "거래량 증가"
            )

        elif volume_ratio < 0.7:
            reasons.append(
                "거래량 감소"
            )

    reason = " / ".join(reasons)

    return {
        "score": score,
        "trend": trend,
        "action": action,
        "reason": reason,
        "rsi": rsi,
        "volume_ratio": volume_ratio,
    }


# ============================================================
# KPI 설명
# ============================================================

def render_compact_kpi(
    label,
    value,
    meaning
):

    st.caption(label)

    st.markdown(
        f"**{value}**"
    )

    st.caption(
        meaning
    )


def render_kpis(df, judgment):

    if df is None or df.empty:
        return

    row = df.iloc[-1]

    current = safe_float(row["Close"])
    ma20 = safe_float(row["MA20"])
    ma60 = safe_float(row["MA60"])
    volume_ratio = safe_float(
        row["VolumeRatio"]
    )
    rsi = safe_float(
        row["RSI"]
    )

    score = judgment["score"]

    # --------------------------------------------------------
    # 1행
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:
        render_compact_kpi(
            "현재가",
            format_price(current),
            "현재 시장에서 거래되는 기준가격"
        )

    with c2:
        render_compact_kpi(
            "20일선",
            format_price(ma20),
            "단기 추세선 · 현재가가 위면 단기 우세"
        )

    with c3:
        render_compact_kpi(
            "60일선",
            format_price(ma60),
            "중기 추세선 · 위면 중기 추세 유지"
        )

    # --------------------------------------------------------
    # 2행
    # --------------------------------------------------------

    c4, c5, c6 = st.columns(3)

    with c4:

        if pd.isna(volume_ratio):
            volume_text = "-"
        else:
            volume_text = f"{volume_ratio:.2f}x"

        render_compact_kpi(
            "거래량비",
            volume_text,
            "20일 평균 대비 거래량 · 1.5x 이상이면 증가"
        )

    with c5:

        if pd.isna(rsi):
            rsi_text = "-"
        else:
            rsi_text = f"{rsi:.1f}"

        render_compact_kpi(
            "RSI",
            rsi_text,
            "모멘텀 · 70↑ 과열 가능 / 30↓ 약세"
        )

    with c6:

        render_compact_kpi(
            "종합점수",
            f"{score}/100",
            "추세+거래량+모멘텀 종합 · 75↑ 강세"
        )

    st.caption(
        "점수 기준: 75↑ 강세 확인 · "
        "60~74 관심 유지 · "
        "45~59 관망 · "
        "44↓ 약세 주의"
    )


# ============================================================
# 구조 설명
# ============================================================

def render_structure(df):

    if df is None or df.empty:
        return

    row = df.iloc[-1]

    current = safe_float(row["Close"])
    ma20 = safe_float(row["MA20"])
    ma60 = safe_float(row["MA60"])

    if pd.isna(ma20) or pd.isna(ma60):
        return

    if current > ma20 > ma60:

        structure = "상승 구조"
        explanation = (
            "현재가가 20일선과 60일선 위에 있고 "
            "단기선이 중기선 위에 있습니다."
        )

    elif current < ma20 < ma60:

        structure = "하락 구조"
        explanation = (
            "현재가가 20일선과 60일선 아래에 있어 "
            추세 회복 여부 확인이 필요합니다."
        )

    else:

        structure = "혼조 구조"
        explanation = (
            "가격과 이동평균선의 방향이 일치하지 않아 "
            추세 전환 여부를 확인하는 구간입니다."
        )

    st.info(
        f"**현재 구조: {structure}**  ·  {explanation}"
    )


# ============================================================
# 가격 대응
# ============================================================

def render_price_response(df):

    levels = calculate_levels(df)

    if not levels:
        return

    current = levels["current"]
    support1 = levels["support1"]
    support2 = levels["support2"]
    resistance1 = levels["resistance1"]
    resistance2 = levels["resistance2"]

    st.subheader("가격 대응 구간")

    c1, c2 = st.columns(2)

    with c1:

        st.markdown("**하방 기준**")

        st.write(
            f"1차 지지: **{format_price(support1)}**"
        )

        st.write(
            f"2차 지지: **{format_price(support2)}**"
        )

        st.caption(
            "지지선 이탈 여부를 통해 추세 훼손 여부를 확인합니다."
        )

    with c2:

        st.markdown("**상방 기준**")

        st.write(
            f"1차 저항: **{format_price(resistance1)}**"
        )

        st.write(
            f"2차 저항: **{format_price(resistance2)}**"
        )

        st.caption(
            "저항 돌파와 거래량 증가가 함께 나타나는지 확인합니다."
        )


# ============================================================
# 매매 시나리오
# ============================================================

def render_scenarios(df):

    levels = calculate_levels(df)

    if not levels:
        return

    current = levels["current"]
    support1 = levels["support1"]
    support2 = levels["support2"]
    resistance1 = levels["resistance1"]
    resistance2 = levels["resistance2"]

    st.subheader("대응 시나리오")

    with st.expander(
        "🟢 상승 / 돌파 시나리오",
        expanded=False
    ):

        st.write(
            f"현재가가 **{format_price(resistance1)}** "
            f"부근의 저항을 거래량 증가와 함께 돌파하는지 확인합니다."
        )

        st.write(
            f"돌파 후 **{format_price(resistance1)}** 위에서 "
            "지지가 형성되면 상승 구조가 강화되는지 관찰합니다."
        )

    with st.expander(
        "🟡 눌림 / 조정 시나리오",
        expanded=False
    ):

        st.write(
            f"현재가가 조정을 받아 "
            f"**{format_price(support1)}** 부근까지 내려오는 경우 "
            "지지 여부를 확인합니다."
        )

        st.write(
            "지지선에서 거래량이 감소하면서 가격이 안정되는지가 "
            "핵심 확인 포인트입니다."
        )

    with st.expander(
        "🔴 추세 훼손 시나리오",
        expanded=False
    ):

        st.write(
            f"**{format_price(support1)}** 이탈 후 "
            f"**{format_price(support2)}**까지 밀리는지 확인합니다."
        )

        st.write(
            "지지선 이탈과 거래량 증가가 동시에 발생하면 "
            "기존 상승 구조가 약해졌는지 재평가할 필요가 있습니다."
        )


# ============================================================
# 차트
# ============================================================

def render_chart(df):

    if df is None or df.empty:
        st.warning("차트 데이터가 없습니다.")
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

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA20"],
            name="20일선",
            mode="lines"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA60"],
            name="60일선",
            mode="lines"
        )
    )

    fig.update_layout(
        height=430,
        margin=dict(
            l=5,
            r=5,
            t=25,
            b=5
        ),
        dragmode=False,
        xaxis=dict(
            fixedrange=True,
            rangeslider=dict(
                visible=False
            )
        ),
        yaxis=dict(
            fixedrange=True
        ),
        hovermode="x unified",
        showlegend=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": False,
            "doubleClick": False,
            "displayModeBar": False,
            "responsive": True
        }
    )


# ============================================================
# ETF 분석
# ============================================================

def render_analysis(code):

    code = str(code)

    name = get_etf_name(code)

    st.markdown(
        f"### 📊 {name}"
    )

    st.caption(
        f"종목코드 {code}"
    )

    df = fetch_yahoo(code)

    if df.empty:

        st.error(
            "가격 데이터를 가져오지 못했습니다. "
            "잠시 후 다시 시도해 주세요."
        )

        return

    df = calculate_indicators(df)

    judgment = get_judgment(df)

    render_kpis(
        df,
        judgment
    )

    render_structure(
        df
    )

    st.divider()

    # --------------------------------------------------------
    # 판단
    # --------------------------------------------------------

    st.subheader("현재 판단")

    c1, c2 = st.columns(2)

    with c1:

        st.write(
            f"**상태: {judgment['action']}**"
        )

        st.write(
            f"추세: **{judgment['trend']}**"
        )

    with c2:

        st.write(
            f"종합점수: **{judgment['score']}/100**"
        )

        st.caption(
            judgment["reason"]
        )

    st.divider()

    render_price_response(
        df
    )

    st.divider()

    render_scenarios(
        df
    )

    st.divider()

    st.subheader("차트")

    render_chart(
        df
    )


# ============================================================
# 분석 버튼
# ============================================================

def analysis_button(
    code,
    key_prefix=""
):

    code = str(code)

    state_key = (
        f"{key_prefix}_analysis_{code}"
    )

    if state_key not in st.session_state.analysis_open:
        st.session_state.analysis_open[state_key] = False

    is_open = st.session_state.analysis_open[
        state_key
    ]

    label = (
        "ETF 분석 닫기"
        if is_open
        else "ETF 분석"
    )

    if st.button(
        label,
        key=f"{key_prefix}_btn_{code}",
        use_container_width=True
    ):

        st.session_state.analysis_open[
            state_key
        ] = not is_open

        st.rerun()

    if st.session_state.analysis_open[
        state_key
    ]:

        # 버튼 바로 아래에 분석
        render_analysis(
            code
        )


# ============================================================
# ETF 찾기
# ============================================================

def render_search():

    st.subheader("🔎 ETF 찾기")

    search_col1, search_col2 = st.columns(
        [4, 1]
    )

    with search_col1:

        keyword = st.text_input(
            "ETF 검색",
            value=st.session_state.search_keyword,
            placeholder="예: AI반도체 / 반도체 / KODEX / 395160",
            label_visibility="collapsed",
            key="etf_search_input"
        )

    with search_col2:

        search_clicked = st.button(
            "검색",
            key="etf_search_button",
            use_container_width=True
        )

    if search_clicked:

        keyword = clean_text(keyword)

        st.session_state.search_keyword = keyword

        if not keyword:

            st.session_state.search_results = []

            st.warning(
                "검색어를 입력해 주세요."
            )

        else:

            with st.spinner(
                "KRX / Yahoo Finance에서 ETF를 검색하고 있습니다..."
            ):

                results = search_etfs(
                    keyword
                )

            st.session_state.search_results = results

            st.session_state.search_generation += 1

            if results:

                st.session_state.selected_search_code = (
                    results[0]["code"]
                )

            else:

                st.session_state.selected_search_code = None

            st.rerun()

    # --------------------------------------------------------
    # 검색 결과
    # --------------------------------------------------------

    results = st.session_state.search_results

    if results:

        st.caption(
            f"검색결과 {len(results)}개"
        )

        result_codes = [
            str(x["code"])
            for x in results
        ]

        search_select_key = (
            "search_result_select_"
            f"{st.session_state.search_generation}"
        )

        default_index = 0

        if (
            st.session_state.selected_search_code
            in result_codes
        ):

            default_index = result_codes.index(
                st.session_state.selected_search_code
            )

        selected_code = st.selectbox(
            "검색 결과",
            options=result_codes,
            index=default_index,
            format_func=get_display_name,
            key=search_select_key
        )

        st.session_state.selected_search_code = (
            selected_code
        )

        selected_info = None

        for item in results:

            if str(item["code"]) == str(selected_code):

                selected_info = item

                break

        if selected_info:

            st.caption(
                f"검색출처: {selected_info.get('source', '-')}"
            )

        # ----------------------------------------------------
        # 추가
        # ----------------------------------------------------

        if st.button(
            "➕ 내 ETF에 추가",
            key=f"add_search_{selected_code}",
            use_container_width=True
        ):

            if selected_code not in st.session_state.watchlist:

                st.session_state.watchlist.append(
                    selected_code
                )

                st.success(
                    f"{get_etf_name(selected_code)}을(를) 내 ETF에 추가했습니다."
                )

            else:

                st.info(
                    "이미 내 ETF에 등록되어 있습니다."
                )

        analysis_button(
            selected_code,
            "search"
        )

    elif st.session_state.search_keyword:

        st.warning(
            f"'{st.session_state.search_keyword}' 검색 결과를 찾지 못했습니다."
        )

        st.caption(
            "종목명 일부 또는 종목코드로 다시 검색해 주세요. "
            "예: 반도체 / AI / KODEX / TIGER / 395160"
        )


# ============================================================
# 내 ETF
# ============================================================

def render_my_etf():

    st.subheader("⭐ 내 ETF")

    watchlist = st.session_state.watchlist

    if not watchlist:

        st.info(
            "등록된 ETF가 없습니다."
        )

        return

    valid_codes = []

    for code in watchlist:

        code = str(code)

        valid_codes.append(code)

    selected = st.selectbox(
        "보유/관심 ETF",
        options=valid_codes,
        format_func=get_display_name,
        key="watchlist_select"
    )

    col1, col2 = st.columns(2)

    with col1:

        analysis_button(
            selected,
            "watch"
        )

    with col2:

        if st.button(
            "삭제",
            key=f"delete_watch_{selected}",
            use_container_width=True
        ):

            if selected in st.session_state.watchlist:

                st.session_state.watchlist.remove(
                    selected
                )

            st.rerun()


# ============================================================
# 테마 ETF 분석
# ============================================================

def analyze_theme_etfs(
    codes
):

    rows = []

    for code in codes:

        code = str(code)

        try:

            df = fetch_yahoo(
                code,
                period="1y"
            )

            if df.empty:
                continue

            df = calculate_indicators(
                df
            )

            judgment = get_judgment(
                df
            )

            row = df.iloc[-1]

            rows.append({
                "code": code,
                "name": get_etf_name(code),
                "score": judgment["score"],
                "return20": safe_float(
                    row["Return20"]
                ),
                "return60": safe_float(
                    row["Return60"]
                ),
                "volume_ratio": safe_float(
                    row["VolumeRatio"]
                ),
            })

        except Exception:
            continue

    return rows


# ============================================================
# 테마 데이터
# ============================================================

THEMES = {

    "AI 반도체·핵심장비": {
        "stage": "현재 주도",
        "emoji": "🔥",
        "rank": "01",

        "etfs": [
            "395160",
            "487240",
            "471990",
            "396500"
        ],

        "keywords": [
            "AI 서버용 반도체 수요",
            "HBM 및 첨단 패키징 투자",
            "반도체 장비 투자 사이클",
            "AI 데이터센터 증설"
        ],

        "reason": (
            "AI 연산 수요가 실제 반도체 생산과 장비 투자로 연결되는지 "
            "확인하는 핵심 구간입니다."
        ),

        "flow": (
            "AI 서비스 → 데이터센터 → GPU/메모리 → "
            "반도체 생산 → 핵심장비 순으로 자금이 확산되는 구조를 봅니다."
        ),

        "bull": (
            "대표 ETF가 20일선 위에서 유지되고 "
            "거래량 증가와 함께 60일선 상승 구조가 이어지는 경우"
        ),

        "bear": (
            "주요 ETF가 20일선과 60일선을 동시에 이탈하고 "
            "거래량 증가를 동반한 하락이 나타나는 경우"
        ),

        "watch": (
            "핵심장비 ETF의 상대강도와 거래량"
        )
    },

    "AI 전력인프라·전력설비": {
        "stage": "다음 수혜",
        "emoji": "⚡",
        "rank": "02",

        "etfs": [
            "464240",
            "487130",
            "449170"
        ],

        "keywords": [
            "데이터센터 전력 수요",
            "전력망 증설",
            "변압기·배전설비 투자",
            "AI 인프라의 전력 병목"
        ],

        "reason": (
            "AI 데이터센터가 늘어날수록 전력 생산과 공급망 투자가 "
            "뒤따라야 한다는 점에 주목합니다."
        ),

        "flow": (
            "AI 서버 증가 → 데이터센터 증가 → 전력수요 증가 → "
            "전력망/변압기/배전설비 투자"
        ),

        "bull": (
            "전력설비 ETF에서 20일선 지지와 거래량 증가가 "
            "동시에 나타나는 경우"
        ),

        "bear": (
            "전력설비 ETF가 상승 추세선을 이탈하고 "
            "시장 대비 상대강도가 지속적으로 약해지는 경우"
        ),

        "watch": (
            "전력 ETF 거래량과 반도체 ETF 대비 상대강도"
        )
    },

    "AI 데이터센터·인프라": {
        "stage": "다음 수혜",
        "emoji": "🏗️",
        "rank": "03",

        "etfs": [
            "449170",
            "434060",
            "381170"
        ],

        "keywords": [
            "데이터센터 증설",
            "AI 서버 인프라",
            "네트워크 및 냉각",
            "AI 인프라 투자 확대"
        ],

        "reason": (
            "AI 연산능력 확대가 데이터센터와 주변 인프라 투자로 "
            "확산되는지를 확인합니다."
        ),

        "flow": (
            "AI 모델 → GPU → 데이터센터 → 네트워크/냉각/전력 → "
            "인프라 투자"
        ),

        "bull": (
            "대표 ETF의 20일선과 60일선이 동시에 상승하고 "
            "거래량이 평균 이상으로 유지되는 경우"
        ),

        "bear": (
            "인프라 관련 ETF가 60일선 아래로 내려가고 "
            "거래량 증가가 하락 방향으로 나타나는 경우"
        ),

        "watch": (
            "AI 인프라 ETF의 20일 수익률과 거래량비"
        )
    },

    "휴머노이드·로보틱스": {
        "stage": "초기 관심",
        "emoji": "🤖",
        "rank": "04",

        "etfs": [
            "458730",
            "364690"
        ],

        "keywords": [
            "휴머노이드 로봇",
            "산업용 로봇 자동화",
            "AI와 로봇의 결합",
            "로봇 부품 및 액추에이터"
        ],

        "reason": (
            "AI의 다음 응용처 가운데 실제 제조현장과 로봇으로 "
            "확산되는 흐름을 확인합니다."
        ),

        "flow": (
            "AI 모델 → 로봇 인지/제어 → 휴머노이드 → "
            "부품/액추에이터 → 제조 자동화"
        ),

        "bull": (
            "로봇 관련 ETF의 거래량 증가와 60일선 회복이 "
            "동시에 나타나는 경우"
        ),

        "bear": (
            "테마 뉴스는 증가하지만 ETF 가격과 거래량이 "
            "동반하지 않는 경우"
        ),

        "watch": (
            "뉴스보다 ETF 거래량과 추세 확인"
        )
    },

    "우주항공·방산": {
        "stage": "초기 관심",
        "emoji": "🚀",
        "rank": "05",

        "etfs": [
            "364690"
        ],

        "keywords": [
            "우주산업 투자",
            "위성 및 발사체",
            "방산 수출",
            "국방·항공우주 투자"
        ],

        "reason": (
            "우주항공과 방산은 개별 종목별 차별화가 크기 때문에 "
            "테마 전체 자금 유입 여부를 우선 확인합니다."
        ),

        "flow": (
            "정부/민간 투자 → 수주 → 매출 증가 → "
            "관련 기업 실적 반영"
        ),

        "bull": (
            "관련 ETF 또는 주요 종목군의 거래량 증가가 "
            "지속되고 추세가 개선되는 경우"
        ),

        "bear": (
            "거래량 없이 단기 뉴스만 반복되고 가격 추세가 "
            "따라오지 않는 경우"
        ),

        "watch": (
            "ETF 거래량과 주요 기업 수주 흐름"
        )
    },

    "SMR·원자력·에너지": {
        "stage": "초기 관심",
        "emoji": "⚛️",
        "rank": "06",

        "etfs": [
            "364690"
        ],

        "keywords": [
            "SMR 건설",
            "원전 투자",
            "전력수요 증가",
            "장기 에너지 인프라"
        ],

        "reason": (
            "AI 데이터센터의 전력수요 증가가 장기적으로 "
            "발전설비 투자 확대와 연결되는지를 확인합니다."
        ),

        "flow": (
            "전력수요 증가 → 발전설비 투자 → 원전/SMR → "
            "관련 기자재 및 인프라"
        ),

        "bull": (
            "원전 관련 ETF와 종목군에서 장기 추세 회복과 "
            "거래량 증가가 함께 나타나는 경우"
        ),

        "bear": (
            "정책 기대감만 커지고 실제 거래량과 가격 추세가 "
            "동반되지 않는 경우"
        ),

        "watch": (
            "정책 뉴스보다 실제 투자와 수주 흐름"
        )
    }
}


# ============================================================
# 테마 ETF 자동 보완
# ============================================================

def find_theme_candidates(
    theme_name,
    theme
):

    existing = list(
        theme.get("etfs", [])
    )

    valid = []

    for code in existing:

        try:

            df = fetch_yahoo(
                code,
                period="6mo"
            )

            if not df.empty:
                valid.append(code)

        except Exception:
            continue

    # --------------------------------------------------------
    # 기존 ETF가 있으면 우선 사용
    # --------------------------------------------------------

    if valid:
        return valid

    # --------------------------------------------------------
    # 외부 Universe에서 테마명 검색
    # --------------------------------------------------------

    keywords = [
        theme_name
    ]

    if "AI" in theme_name:
        keywords.append("AI")

    if "반도체" in theme_name:
        keywords.append("반도체")

    if "전력" in theme_name:
        keywords.append("전력")

    if "로봇" in theme_name:
        keywords.append("로봇")

    if "우주" in theme_name:
        keywords.append("우주")

    if "원자력" in theme_name:
        keywords.append("원자력")

    found = []

    for keyword in keywords:

        try:

            results = search_etfs(
                keyword,
                max_results=10
            )

            for item in results:

                code = str(
                    item["code"]
                )

                if code not in found:
                    found.append(code)

        except Exception:
            continue

        if len(found) >= 5:
            break

    return found[:5]


# ============================================================
# 테마 카드
# ============================================================

def render_theme_card(
    theme_name,
    theme
):

    stage = clean_text(
        theme.get("stage", "")
    )

    emoji = clean_text(
        theme.get("emoji", "📌")
    )

    st.markdown(
        f"### {emoji} {theme_name}"
    )

    st.caption(
        f"{stage} · 테마 로드맵 {theme.get('rank', '')}"
    )

    reason = clean_text(
        theme.get("reason", "")
    )

    if reason:
        st.write(
            reason
        )

    # --------------------------------------------------------
    # 자금 이동 경로
    # --------------------------------------------------------

    flow = clean_text(
        theme.get("flow", "")
    )

    if flow:

        st.info(
            f"**자금 이동 경로**\n\n{flow}"
        )

    # --------------------------------------------------------
    # ETF 분석
    # --------------------------------------------------------

    codes = find_theme_candidates(
        theme_name,
        theme
    )

    rows = analyze_theme_etfs(
        codes
    )

    if rows:

        scores = [
            safe_float(x["score"])
            for x in rows
            if not pd.isna(
                safe_float(x["score"])
            )
        ]

        ret20 = [
            safe_float(x["return20"])
            for x in rows
            if not pd.isna(
                safe_float(x["return20"])
            )
        ]

        ret60 = [
            safe_float(x["return60"])
            for x in rows
            if not pd.isna(
                safe_float(x["return60"])
            )
        ]

        vol = [
            safe_float(x["volume_ratio"])
            for x in rows
            if not pd.isna(
                safe_float(x["volume_ratio"])
            )
        ]

        avg_score = (
            np.mean(scores)
            if scores
            else np.nan
        )

        avg20 = (
            np.mean(ret20)
            if ret20
            else np.nan
        )

        avg60 = (
            np.mean(ret60)
            if ret60
            else np.nan
        )

        avg_vol = (
            np.mean(vol)
            if vol
            else np.nan
        )

        # ----------------------------------------------------
        # 테마 신호
        # ----------------------------------------------------

        if (
            not pd.isna(avg_score)
            and avg_score >= 75
            and not pd.isna(avg20)
            and avg20 > 0
            and not pd.isna(avg_vol)
            and avg_vol >= 1.2
        ):

            signal = "🔥 모멘텀 확인"

        elif (
            not pd.isna(avg_score)
            and avg_score >= 60
        ):

            signal = "🟠 관심 유지"

        else:

            signal = "⚪ 관찰"

        st.markdown(
            f"**테마 신호: {signal}**"
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.caption("테마점수")

            st.markdown(
                f"**{avg_score:.0f}/100**"
                if not pd.isna(avg_score)
                else "**-**"
            )

        with c2:

            st.caption("20일 흐름")

            st.markdown(
                f"**{avg20:+.1f}%**"
                if not pd.isna(avg20)
                else "**-**"
            )

        with c3:

            st.caption("60일 흐름")

            st.markdown(
                f"**{avg60:+.1f}%**"
                if not pd.isna(avg60)
                else "**-**"
            )

        with c4:

            st.caption("평균 거래량")

            st.markdown(
                f"**{avg_vol:.2f}x**"
                if not pd.isna(avg_vol)
                else "**-**"
            )

        st.caption(
            "테마점수 = 대표 ETF들의 추세·거래량·모멘텀을 단순 평균한 참고값"
        )

        # ----------------------------------------------------
        # 대표 ETF
        # ----------------------------------------------------

        table_rows = []

        for item in rows:

            table_rows.append({
                "ETF": item["name"],
                "20일": (
                    f"{item['return20']:+.1f}%"
                    if not pd.isna(item["return20"])
                    else "-"
                ),
                "60일": (
                    f"{item['return60']:+.1f}%"
                    if not pd.isna(item["return60"])
                    else "-"
                ),
                "거래량": (
                    f"{item['volume_ratio']:.2f}x"
                    if not pd.isna(item["volume_ratio"])
                    else "-"
                ),
                "점수": (
                    f"{item['score']:.0f}"
                )
            })

        if table_rows:

            st.dataframe(
                pd.DataFrame(table_rows),
                use_container_width=True,
                hide_index=True
            )

    else:

        st.warning(
            "현재 테마 대표 ETF 가격 데이터를 불러오지 못했습니다."
        )

    # ========================================================
    # 핵심 체크포인트
    # ========================================================

    st.markdown(
        "### 🔗 핵심 체크포인트"
    )

    keywords = theme.get(
        "keywords",
        []
    )

    # 오류 방지용 안전 처리
    if keywords is None:
        keywords = []

    if isinstance(
        keywords,
        str
    ):
        keywords = [
            keywords
        ]

    if not isinstance(
        keywords,
        (list, tuple)
    ):
        keywords = [
            str(keywords)
        ]

    valid_keywords = []

    for item in keywords:

        item = clean_text(item)

        if item:
            valid_keywords.append(
                item
            )

    if valid_keywords:

        for item in valid_keywords:

            st.write(
                f"• {item}"
            )

    else:

        st.caption(
            "등록된 체크포인트가 없습니다."
        )

    # ========================================================
    # 강해지는 조건 / 약해지는 조건
    # ========================================================

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            "**🟢 강해지는 조건**"
        )

        bull = clean_text(
            theme.get("bull", "")
        )

        if bull:
            st.write(
                bull
            )

    with c2:

        st.markdown(
            "**🔴 약해지는 조건**"
        )

        bear = clean_text(
            theme.get("bear", "")
        )

        if bear:
            st.write(
                bear
            )

    watch = clean_text(
        theme.get("watch", "")
    )

    if watch:

        st.info(
            f"**가장 먼저 볼 것:** {watch}"
        )

    # ========================================================
    # 대표 ETF 분석
    # ========================================================

    if codes:

        st.markdown(
            "### 📊 대표 ETF 분석"
        )

        # 최대 4개
        for idx, code in enumerate(
            codes[:4]
        ):

            code = str(code)

            with st.expander(
                get_display_name(code),
                expanded=False
            ):

                render_analysis(
                    code
                )


# ============================================================
# 미래 테마
# ============================================================

def render_future_theme():

    st.subheader(
        "🚀 미래 테마"
    )

    st.caption(
        "현재 주도 → 다음 수혜 → 초기 관심으로 자금 확산 경로를 확인합니다."
    )

    # --------------------------------------------------------
    # 수동 업데이트
    # --------------------------------------------------------

    if st.button(
        "🔄 테마 데이터 새로고침",
        key="theme_manual_refresh",
        use_container_width=True
    ):

        try:
            fetch_yahoo.clear()
        except Exception:
            pass

        try:
            yahoo_search.clear()
        except Exception:
            pass

        st.session_state.theme_refresh += 1

        st.rerun()

    st.caption(
        f"마지막 수동 새로고침 번호: {st.session_state.theme_refresh}"
    )

    # --------------------------------------------------------
    # 로드맵
    # --------------------------------------------------------

    roadmap_cols = st.columns(
        len(THEMES)
    )

    for col, (
        theme_name,
        theme
    ) in zip(
        roadmap_cols,
        THEMES.items()
    ):

        with col:

            st.caption(
                f"{theme.get('rank', '')}"
            )

            st.markdown(
                f"**{theme.get('emoji', '📌')} {theme_name}**"
            )

            st.caption(
                theme.get("stage", "")
            )

    st.divider()

    # --------------------------------------------------------
    # 테마별 분석
    # --------------------------------------------------------

    for theme_name, theme in THEMES.items():

        with st.expander(
            f"{theme.get('emoji', '📌')} "
            f"{theme_name} · "
            f"{theme.get('stage', '')}",
            expanded=False
        ):

            render_theme_card(
                theme_name,
                theme
            )

        st.divider()


# ============================================================
# 시장 개요
# ============================================================

def render_market_summary():

    st.subheader(
        "📌 ETF RADAR"
    )

    st.caption(
        "ETF 검색 → 기술분석 → 가격대응 → 미래테마를 한 화면에서 확인합니다."
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.info(
            "**ETF 찾기**\n\n"
            "KRX + Yahoo Finance 외부검색"
        )

    with c2:

        st.info(
            "**차트 분석**\n\n"
            "20일선 · 60일선 · RSI · 거래량"
        )

    with c3:

        st.info(
            "**테마 분석**\n\n"
            "현재 주도 → 다음 수혜 → 초기 관심"
        )


# ============================================================
# 메인
# ============================================================

def main():

    render_market_summary()

    st.divider()

    tab1, tab2, tab3 = st.tabs(
        [
            "⭐ 내 ETF",
            "🔎 ETF 찾기",
            "🚀 미래 테마"
        ]
    )

    # --------------------------------------------------------
    # 내 ETF
    # --------------------------------------------------------

    with tab1:

        render_my_etf()

    # --------------------------------------------------------
    # ETF 검색
    # --------------------------------------------------------

    with tab2:

        render_search()

    # --------------------------------------------------------
    # 미래 테마
    # --------------------------------------------------------

    with tab3:

        render_future_theme()


# ============================================================
# 실행
# ============================================================

if __name__ == "__main__":
    main()