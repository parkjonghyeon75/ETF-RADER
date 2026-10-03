# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import json
import urllib.request
import urllib.parse
import ssl

from datetime import datetime, timedelta


# ============================================================
# PAGE
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

st.markdown(
    """
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

    div[data-testid="stMetricValue"] {
        font-size: 1.05rem !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
    }

    .stButton button {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)


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
# SESSION STATE
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

if "theme_refresh_count" not in st.session_state:
    st.session_state.theme_refresh_count = 0


# ============================================================
# TEXT UTILITY
# ============================================================

def clean_text(value):
    if value is None:
        return ""

    text = str(value)
    text = text.replace("\x00", "")
    text = text.replace("\r", " ")
    text = text.replace("\n", " ")

    return text.strip()


def normalize_text(value):
    text = clean_text(value).lower()

    for char in [
        " ",
        "-",
        "_",
        "/",
        ".",
        "&",
        "(",
        ")",
        "[",
        "]",
    ]:
        text = text.replace(char, "")

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

    return f"{value:,.0f}"


def get_clean_code(code):
    return (
        str(code)
        .replace(".KS", "")
        .replace(".KQ", "")
        .strip()
    )


# ============================================================
# ETF NAME
# ============================================================

def get_etf_name(code):
    code = get_clean_code(code)

    if code in BASE_ETFS:
        return BASE_ETFS[code]

    for item in st.session_state.search_results:
        if get_clean_code(item.get("code", "")) == code:
            return clean_text(item.get("name", code))

    return code


def get_display_name(code):
    code = get_clean_code(code)
    name = get_etf_name(code)

    if name == code:
        return code

    return f"{name} ({code})"


# ============================================================
# KRX ETF UNIVERSE
# ============================================================

@st.cache_data(
    ttl=60 * 60 * 12,
    show_spinner=False
)
def load_krx_etf_universe():

    rows = []

    try:
        from pykrx import stock

        today = datetime.now()

        date_list = [
            today.strftime("%Y%m%d"),
            (today - timedelta(days=1)).strftime("%Y%m%d"),
            (today - timedelta(days=3)).strftime("%Y%m%d"),
            (today - timedelta(days=7)).strftime("%Y%m%d"),
        ]

        ticker_list = []

        for date_text in date_list:
            try:
                ticker_list = stock.get_etf_ticker_list(
                    date_text
                )

                if ticker_list:
                    break

            except Exception:
                continue

        if not ticker_list:
            return pd.DataFrame(
                columns=["code", "name", "source"]
            )

        for ticker in ticker_list:

            try:
                code = get_clean_code(ticker)

                name = stock.get_etf_ticker_name(
                    ticker
                )

                name = clean_text(name)

                if code and name:

                    rows.append(
                        {
                            "code": code,
                            "name": name,
                            "source": "KRX",
                        }
                    )

            except Exception:
                continue

    except Exception:
        return pd.DataFrame(
            columns=["code", "name", "source"]
        )

    if not rows:
        return pd.DataFrame(
            columns=["code", "name", "source"]
        )

    df = pd.DataFrame(rows)

    df = df.drop_duplicates(
        subset=["code"]
    )

    return df.reset_index(drop=True)


# ============================================================
# BASE UNIVERSE
# ============================================================

def get_base_universe():

    rows = []

    for code, name in BASE_ETFS.items():

        rows.append(
            {
                "code": code,
                "name": name,
                "source": "BASE",
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# EXTERNAL UNIVERSE
# ============================================================

@st.cache_data(
    ttl=60 * 60 * 6,
    show_spinner=False
)
def get_external_universe():

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

    df = pd.concat(
        frames,
        ignore_index=True
    )

    df["code"] = (
        df["code"]
        .astype(str)
        .apply(get_clean_code)
    )

    df["name"] = (
        df["name"]
        .astype(str)
        .apply(clean_text)
    )

    df = df.drop_duplicates(
        subset=["code"],
        keep="first"
    )

    return df.reset_index(drop=True)


# ============================================================
# YAHOO SEARCH
# ============================================================

@st.cache_data(
    ttl=60 * 30,
    show_spinner=False
)
def yahoo_search(keyword):

    keyword = clean_text(keyword)

    if not keyword:
        return pd.DataFrame(
            columns=["code", "name", "source"]
        )

    rows = []

    try:

        encoded = urllib.parse.quote(
            keyword
        )

        url = (
            "https://query1.finance.yahoo.com/"
            "v1/finance/search?"
            f"q={encoded}"
            "&quotesCount=50"
            "&newsCount=0"
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        context = ssl.create_default_context()

        with urllib.request.urlopen(
            request,
            timeout=8,
            context=context
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

        data = json.loads(raw)

        quotes = data.get(
            "quotes",
            []
        )

        for quote in quotes:

            symbol = clean_text(
                quote.get(
                    "symbol",
                    ""
                )
            )

            if not symbol.endswith(".KS"):
                continue

            code = get_clean_code(
                symbol
            )

            name = (
                quote.get("longname")
                or quote.get("shortname")
                or code
            )

            name = clean_text(name)

            if code:

                rows.append(
                    {
                        "code": code,
                        "name": name,
                        "source": "Yahoo",
                    }
                )

    except Exception:
        pass

    if not rows:

        return pd.DataFrame(
            columns=["code", "name", "source"]
        )

    df = pd.DataFrame(rows)

    return df.drop_duplicates(
        subset=["code"]
    ).reset_index(drop=True)


# ============================================================
# ETF SEARCH
# ============================================================

def search_etfs(
    keyword,
    max_results=50
):

    keyword = clean_text(keyword)

    if not keyword:
        return []

    search_key = normalize_text(
        keyword
    )

    result_map = {}

    # --------------------------------------------------------
    # 1. KRX + BASE
    # --------------------------------------------------------

    try:

        universe = get_external_universe()

        if not universe.empty:

            for _, row in universe.iterrows():

                code = get_clean_code(
                    row["code"]
                )

                name = clean_text(
                    row["name"]
                )

                n_code = normalize_text(
                    code
                )

                n_name = normalize_text(
                    name
                )

                score = 0

                if search_key == n_code:
                    score += 1000

                if search_key == n_name:
                    score += 900

                if search_key in n_code:
                    score += 700

                if search_key in n_name:
                    score += 600

                if score > 0:

                    result_map[code] = {
                        "code": code,
                        "name": name,
                        "source": clean_text(
                            row.get(
                                "source",
                                "KRX"
                            )
                        ),
                        "score": score,
                    }

    except Exception:
        pass

    # --------------------------------------------------------
    # 2. Yahoo
    # --------------------------------------------------------

    try:

        yahoo_df = yahoo_search(
            keyword
        )

        if not yahoo_df.empty:

            for _, row in yahoo_df.iterrows():

                code = get_clean_code(
                    row["code"]
                )

                name = clean_text(
                    row["name"]
                )

                n_code = normalize_text(
                    code
                )

                n_name = normalize_text(
                    name
                )

                score = 200

                if search_key == n_code:
                    score += 1000

                if search_key in n_name:
                    score += 500

                if code in result_map:

                    result_map[code]["score"] += 300

                else:

                    result_map[code] = {
                        "code": code,
                        "name": name,
                        "source": "Yahoo",
                        "score": score,
                    }

    except Exception:
        pass

    # --------------------------------------------------------
    # 3. BASE 직접검색
    # --------------------------------------------------------

    for code, name in BASE_ETFS.items():

        n_code = normalize_text(code)
        n_name = normalize_text(name)

        if (
            search_key in n_code
            or search_key in n_name
        ):

            if code not in result_map:

                result_map[code] = {
                    "code": code,
                    "name": name,
                    "source": "BASE",
                    "score": 400,
                }

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    results = list(
        result_map.values()
    )

    results.sort(
        key=lambda x: (
            -x["score"],
            x["name"]
        )
    )

    return results[:max_results]


# ============================================================
# YAHOO PRICE
# ============================================================

@st.cache_data(
    ttl=60 * 15,
    show_spinner=False
)
def fetch_yahoo(
    code,
    period="1y"
):

    code = get_clean_code(code)

    ticker = f"{code}.KS"

    try:

        df = yf.download(
            ticker,
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        if isinstance(
            df.columns,
            pd.MultiIndex
        ):

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
            "Volume",
        ]

        for column in required:

            if column not in df.columns:
                return pd.DataFrame()

        df = df[
            required
        ].copy()

        for column in required:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        df = df.dropna(
            subset=["Close"]
        )

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# INDICATORS
# ============================================================

def calculate_indicators(df):

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    close = df["Close"]

    df["MA20"] = (
        close.rolling(20).mean()
    )

    df["MA60"] = (
        close.rolling(60).mean()
    )

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

    rs = (
        avg_gain
        / avg_loss.replace(
            0,
            np.nan
        )
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
# LEVELS
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
    recent60 = df.tail(60)

    support1 = safe_float(
        recent20["Low"].min()
    )

    support2 = safe_float(
        recent60["Low"].min()
    )

    resistance1 = safe_float(
        recent20["High"].max()
    )

    resistance2 = safe_float(
        recent60["High"].max()
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
# JUDGMENT
# ============================================================

def get_judgment(df):

    if df is None or df.empty:

        return {
            "score": 0,
            "trend": "데이터 부족",
            "action": "관찰",
            "reason": "가격 데이터가 부족합니다.",
            "rsi": np.nan,
            "volume_ratio": np.nan,
        }

    row = df.iloc[-1]

    current = safe_float(
        row["Close"]
    )

    ma20 = safe_float(
        row["MA20"]
    )

    ma60 = safe_float(
        row["MA60"]
    )

    rsi = safe_float(
        row["RSI"]
    )

    volume_ratio = safe_float(
        row["VolumeRatio"]
    )

    score = 50

    # --------------------------------------------------------
    # TREND
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
    # VOLUME
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
            min(
                100,
                score
            )
        )
    )

    if score >= 75:

        action = "강세 확인"

    elif score >= 60:

        action = "관심 유지"

    elif score >= 45:

        action = "관망"

    else:

        action = "약세 주의"

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
                "RSI 정상권"
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

    return {
        "score": score,
        "trend": trend,
        "action": action,
        "reason": " / ".join(reasons),
        "rsi": rsi,
        "volume_ratio": volume_ratio,
    }


# ============================================================
# COMPACT KPI
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


def render_kpis(
    df,
    judgment
):

    if df is None or df.empty:
        return

    row = df.iloc[-1]

    current = safe_float(
        row["Close"]
    )

    ma20 = safe_float(
        row["MA20"]
    )

    ma60 = safe_float(
        row["MA60"]
    )

    volume_ratio = safe_float(
        row["VolumeRatio"]
    )

    rsi = safe_float(
        row["RSI"]
    )

    score = judgment["score"]

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
            "단기 추세선 · 위면 단기 우세"
        )

    with c3:

        render_compact_kpi(
            "60일선",
            format_price(ma60),
            "중기 추세선 · 위면 중기 유지"
        )

    c4, c5, c6 = st.columns(3)

    with c4:

        volume_text = "-"

        if not pd.isna(volume_ratio):

            volume_text = (
                f"{volume_ratio:.2f}x"
            )

        render_compact_kpi(
            "거래량비",
            volume_text,
            "20일 평균 대비 거래량 · 1.5x↑ 관심"
        )

    with c5:

        rsi_text = "-"

        if not pd.isna(rsi):

            rsi_text = f"{rsi:.1f}"

        render_compact_kpi(
            "RSI",
            rsi_text,
            "모멘텀 · 70↑ 과열 / 30↓ 약세"
        )

    with c6:

        render_compact_kpi(
            "종합점수",
            f"{score}/100",
            "추세+거래량+모멘텀 종합"
        )

    st.caption(
        "점수 기준: 75↑ 강세 확인 · "
        "60~74 관심 유지 · "
        "45~59 관망 · "
        "44↓ 약세 주의"
    )


# ============================================================
# STRUCTURE
# ============================================================

def render_structure(df):

    if df is None or df.empty:
        return

    row = df.iloc[-1]

    current = safe_float(
        row["Close"]
    )

    ma20 = safe_float(
        row["MA20"]
    )

    ma60 = safe_float(
        row["MA60"]
    )

    if (
        pd.isna(ma20)
        or pd.isna(ma60)
    ):
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
            "추세 회복 여부 확인이 필요합니다."
        )

    else:

        structure = "혼조 구조"

        explanation = (
            "가격과 이동평균선의 방향이 일치하지 않아 "
            "추세 전환 여부를 확인하는 구간입니다."
        )

    st.info(
        f"**현재 구조: {structure}** · {explanation}"
    )


# ============================================================
# PRICE RESPONSE
# ============================================================

def render_price_response(df):

    levels = calculate_levels(df)

    if not levels:
        return

    st.subheader(
        "가격 대응 구간"
    )

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            "**하방 기준**"
        )

        st.write(
            f"1차 지지: **"
            f"{format_price(levels['support1'])}"
            f"**"
        )

        st.write(
            f"2차 지지: **"
            f"{format_price(levels['support2'])}"
            f"**"
        )

        st.caption(
            "지지선 이탈 여부로 추세 훼손 여부를 확인합니다."
        )

    with c2:

        st.markdown(
            "**상방 기준**"
        )

        st.write(
            f"1차 저항: **"
            f"{format_price(levels['resistance1'])}"
            f"**"
        )

        st.write(
            f"2차 저항: **"
            f"{format_price(levels['resistance2'])}"
            f"**"
        )

        st.caption(
            "저항 돌파와 거래량 증가가 함께 나타나는지 확인합니다."
        )


# ============================================================
# SCENARIOS
# ============================================================

def render_scenarios(df):

    levels = calculate_levels(df)

    if not levels:
        return

    st.subheader(
        "대응 시나리오"
    )

    with st.expander(
        "🟢 상승 / 돌파 시나리오",
        expanded=False
    ):

        st.write(
            f"현재가가 "
            f"**{format_price(levels['resistance1'])}** "
            "부근의 저항을 거래량 증가와 함께 돌파하는지 확인합니다."
        )

        st.write(
            f"돌파 후 "
            f"**{format_price(levels['resistance1'])}** "
            "위에서 지지가 형성되는지 확인합니다."
        )

    with st.expander(
        "🟡 눌림 / 조정 시나리오",
        expanded=False
    ):

        st.write(
            f"조정 시 "
            f"**{format_price(levels['support1'])}** "
            "부근에서 지지가 형성되는지 확인합니다."
        )

        st.write(
            "지지선에서 거래량이 감소하면서 "
            "가격이 안정되는지가 핵심입니다."
        )

    with st.expander(
        "🔴 추세 훼손 시나리오",
        expanded=False
    ):

        st.write(
            f"**{format_price(levels['support1'])}** "
            "이탈 후 "
            f"**{format_price(levels['support2'])}** "
            "까지 밀리는지 확인합니다."
        )

        st.write(
            "지지선 이탈과 거래량 증가가 동시에 나타나면 "
            "기존 상승 구조가 약해졌는지 재평가합니다."
        )


# ============================================================
# CHART
# ============================================================

def render_chart(df):

    if df is None or df.empty:

        st.warning(
            "차트 데이터가 없습니다."
        )

        return

    chart_df = df.tail(
        180
    ).copy()

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name="가격",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA20"],
            mode="lines",
            name="20일선",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA60"],
            mode="lines",
            name="60일선",
        )
    )

    fig.update_layout(
        height=430,
        margin=dict(
            l=5,
            r=5,
            t=25,
            b=5,
        ),
        dragmode=False,
        hovermode="x unified",
        showlegend=True,
    )

    fig.update_xaxes(
        fixedrange=True,
        rangeslider_visible=False,
    )

    fig.update_yaxes(
        fixedrange=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": False,
            "doubleClick": False,
            "displayModeBar": False,
            "responsive": True,
        },
    )


# ============================================================
# FULL ETF ANALYSIS
# ============================================================

def render_analysis(code):

    code = get_clean_code(code)

    name = get_etf_name(code)

    st.markdown(
        f"### 📊 {name}"
    )

    st.caption(
        f"종목코드 {code}"
    )

    df = fetch_yahoo(
        code
    )

    if df.empty:

        st.error(
            "가격 데이터를 가져오지 못했습니다. "
            "잠시 후 다시 시도해 주세요."
        )

        return

    df = calculate_indicators(
        df
    )

    judgment = get_judgment(
        df
    )

    render_kpis(
        df,
        judgment
    )

    render_structure(
        df
    )

    st.divider()

    st.subheader(
        "현재 판단"
    )

    c1, c2 = st.columns(2)

    with c1:

        st.write(
            f"상태: **{judgment['action']}**"
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

    st.subheader(
        "차트"
    )

    render_chart(
        df
    )


# ============================================================
# ANALYSIS BUTTON
# ============================================================

def analysis_button(
    code,
    key_prefix
):

    code = get_clean_code(code)

    state_key = (
        f"{key_prefix}_analysis_{code}"
    )

    if state_key not in st.session_state.analysis_open:

        st.session_state.analysis_open[
            state_key
        ] = False

    is_open = (
        st.session_state.analysis_open[
            state_key
        ]
    )

    label = (
        "ETF 분석 닫기"
        if is_open
        else "ETF 분석"
    )

    clicked = st.button(
        label,
        key=f"{key_prefix}_button_{code}",
        use_container_width=True,
    )

    if clicked:

        st.session_state.analysis_open[
            state_key
        ] = not is_open

        st.rerun()

    if st.session_state.analysis_open[
        state_key
    ]:

        render_analysis(
            code
        )


# ============================================================
# ETF SEARCH UI
# ============================================================

def render_search():

    st.subheader(
        "🔎 ETF 찾기"
    )

    st.caption(
        "KRX 전체 ETF와 Yahoo Finance 외부검색을 함께 사용합니다."
    )

    col1, col2 = st.columns(
        [4, 1]
    )

    with col1:

        keyword = st.text_input(
            "ETF 검색어",
            value=st.session_state.search_keyword,
            placeholder=(
                "예: AI반도체 / 반도체 / KODEX / TIGER / 395160"
            ),
            label_visibility="collapsed",
            key="etf_search_input",
        )

    with col2:

        search_clicked = st.button(
            "검색",
            key="etf_search_button",
            use_container_width=True,
        )

    if search_clicked:

        keyword = clean_text(
            keyword
        )

        st.session_state.search_keyword = (
            keyword
        )

        if not keyword:

            st.session_state.search_results = []

            st.warning(
                "검색어를 입력해 주세요."
            )

        else:

            with st.spinner(
                "외부 ETF 정보를 검색하고 있습니다..."
            ):

                results = search_etfs(
                    keyword
                )

            st.session_state.search_results = (
                results
            )

            st.session_state.search_generation += 1

            if results:

                st.session_state.selected_search_code = (
                    results[0]["code"]
                )

            else:

                st.session_state.selected_search_code = None

            st.rerun()

    results = (
        st.session_state.search_results
    )

    if results:

        st.success(
            f"검색결과 {len(results)}개"
        )

        result_codes = [
            get_clean_code(
                item["code"]
            )
            for item in results
        ]

        current_code = (
            st.session_state.selected_search_code
        )

        if current_code in result_codes:

            default_index = (
                result_codes.index(
                    current_code
                )
            )

        else:

            default_index = 0

        select_key = (
            "search_result_"
            f"{st.session_state.search_generation}"
        )

        selected_code = st.selectbox(
            "검색 결과",
            result_codes,
            index=default_index,
            format_func=get_display_name,
            key=select_key,
        )

        st.session_state.selected_search_code = (
            selected_code
        )

        selected_info = None

        for item in results:

            if (
                get_clean_code(
                    item["code"]
                )
                == selected_code
            ):

                selected_info = item
                break

        if selected_info:

            st.caption(
                "검색 출처: "
                f"{selected_info.get('source', '-')}"
            )

        st.divider()

        if st.button(
            "➕ 내 ETF에 추가",
            key=f"add_{selected_code}",
            use_container_width=True,
        ):

            if (
                selected_code
                not in st.session_state.watchlist
            ):

                st.session_state.watchlist.append(
                    selected_code
                )

                st.success(
                    f"{get_etf_name(selected_code)}을(를) "
                    "내 ETF에 추가했습니다."
                )

            else:

                st.info(
                    "이미 내 ETF에 등록되어 있습니다."
                )

        # 분석 버튼 바로 아래 결과
        analysis_button(
            selected_code,
            "search"
        )

    elif st.session_state.search_keyword:

        st.warning(
            f"'{st.session_state.search_keyword}' "
            "검색 결과를 찾지 못했습니다."
        )

        st.caption(
            "종목명 일부, 운용사, 테마명 또는 "
            "6자리 종목코드로 검색해 보세요."
        )

        st.write(
            "예: 반도체 · AI · 전력 · KODEX · "
            "TIGER · 395160"
        )


# ============================================================
# MY ETF
# ============================================================

def render_my_etf():

    st.subheader(
        "⭐ 내 ETF"
    )

    watchlist = [
        get_clean_code(x)
        for x in st.session_state.watchlist
    ]

    if not watchlist:

        st.info(
            "등록된 ETF가 없습니다."
        )

        return

    selected = st.selectbox(
        "보유/관심 ETF",
        watchlist,
        format_func=get_display_name,
        key="watchlist_select",
    )

    analysis_button(
        selected,
        "watch"
    )

    if st.button(
        "🗑️ 선택 ETF 삭제",
        key=f"delete_{selected}",
        use_container_width=True,
    ):

        if (
            selected
            in st.session_state.watchlist
        ):

            st.session_state.watchlist.remove(
                selected
            )

        st.rerun()


# ============================================================
# THEME DATA
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
            "396500",
        ],

        "keywords": [
            "AI 서버용 반도체 수요",
            "HBM 및 첨단 패키징 투자",
            "반도체 장비 투자 사이클",
            "AI 데이터센터 증설",
        ],

        "reason": (
            "AI 연산 수요가 실제 반도체 생산과 장비 투자로 "
            "연결되는지를 확인하는 핵심 테마입니다."
        ),

        "flow": (
            "AI 서비스 → 데이터센터 → GPU/메모리 → "
            "반도체 생산 → 핵심장비"
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
        ),
    },

    "AI 전력인프라·전력설비": {

        "stage": "다음 수혜",
        "emoji": "⚡",
        "rank": "02",

        "etfs": [
            "464240",
            "487130",
            "449170",
        ],

        "keywords": [
            "데이터센터 전력 수요",
            "전력망 증설",
            "변압기·배전설비 투자",
            "AI 인프라의 전력 병목",
        ],

        "reason": (
            "AI 데이터센터가 늘어날수록 전력 생산과 공급망 "
            "투자가 뒤따라야 한다는 점을 확인합니다."
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
        ),
    },

    "AI 데이터센터·인프라": {

        "stage": "다음 수혜",
        "emoji": "🏗️",
        "rank": "03",

        "etfs": [
            "449170",
            "434060",
            "381170",
        ],

        "keywords": [
            "데이터센터 증설",
            "AI 서버 인프라",
            "네트워크 및 냉각",
            "AI 인프라 투자 확대",
        ],

        "reason": (
            "AI 연산능력 확대가 데이터센터와 주변 인프라 "
            "투자로 확산되는지를 확인합니다."
        ),

        "flow": (
            "AI 모델 → GPU → 데이터센터 → "
            "네트워크/냉각/전력 → 인프라 투자"
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
        ),
    },

    "휴머노이드·로보틱스": {

        "stage": "초기 관심",
        "emoji": "🤖",
        "rank": "04",

        "etfs": [
            "458730",
            "364690",
        ],

        "keywords": [
            "휴머노이드 로봇",
            "산업용 로봇 자동화",
            "AI와 로봇의 결합",
            "로봇 부품 및 액추에이터",
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
        ),
    },

    "우주항공·방산": {

        "stage": "초기 관심",
        "emoji": "🚀",
        "rank": "05",

        "etfs": [
            "364690",
        ],

        "keywords": [
            "우주산업 투자",
            "위성 및 발사체",
            "방산 수출",
            "국방·항공우주 투자",
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
        ),
    },

    "SMR·원자력·에너지": {

        "stage": "초기 관심",
        "emoji": "⚛️",
        "rank": "06",

        "etfs": [
            "364690",
        ],

        "keywords": [
            "SMR 건설",
            "원전 투자",
            "전력수요 증가",
            "장기 에너지 인프라",
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
        ),
    },
}


# ============================================================
# THEME ANALYSIS
# ============================================================

def analyze_theme_etfs(
    codes
):

    rows = []

    for code in codes:

        code = get_clean_code(
            code
        )

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

            rows.append(
                {
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
                }
            )

        except Exception:
            continue

    return rows


# ============================================================
# THEME CARD
# ============================================================

def render_theme_card(
    theme_name,
    theme
):

    emoji = clean_text(
        theme.get(
            "emoji",
            "📌"
        )
    )

    stage = clean_text(
        theme.get(
            "stage",
            ""
        )
    )

    st.markdown(
        f"### {emoji} {theme_name}"
    )

    st.caption(
        f"{stage} · 테마 로드맵 "
        f"{theme.get('rank', '')}"
    )

    reason = clean_text(
        theme.get(
            "reason",
            ""
        )
    )

    if reason:

        st.write(
            reason
        )

    flow = clean_text(
        theme.get(
            "flow",
            ""
        )
    )

    if flow:

        st.info(
            f"**자금 이동 경로**\n\n{flow}"
        )

    codes = [
        get_clean_code(x)
        for x in theme.get(
            "etfs",
            []
        )
    ]

    rows = analyze_theme_etfs(
        codes
    )

    # --------------------------------------------------------
    # THEME SUMMARY
    # --------------------------------------------------------

    if rows:

        scores = [
            safe_float(
                x["score"]
            )
            for x in rows
            if not pd.isna(
                safe_float(x["score"])
            )
        ]

        returns20 = [
            safe_float(
                x["return20"]
            )
            for x in rows
            if not pd.isna(
                safe_float(x["return20"])
            )
        ]

        returns60 = [
            safe_float(
                x["return60"]
            )
            for x in rows
            if not pd.isna(
                safe_float(x["return60"])
            )
        ]

        volumes = [
            safe_float(
                x["volume_ratio"]
            )
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
            np.mean(returns20)
            if returns20
            else np.nan
        )

        avg60 = (
            np.mean(returns60)
            if returns60
            else np.nan
        )

        avg_volume = (
            np.mean(volumes)
            if volumes
            else np.nan
        )

        if (
            not pd.isna(avg_score)
            and avg_score >= 75
            and not pd.isna(avg20)
            and avg20 > 0
            and not pd.isna(avg_volume)
            and avg_volume >= 1.2
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

            st.caption(
                "테마점수"
            )

            if pd.isna(avg_score):

                st.markdown(
                    "**-**"
                )

            else:

                st.markdown(
                    f"**{avg_score:.0f}/100**"
                )

        with c2:

            st.caption(
                "20일 흐름"
            )

            if pd.isna(avg20):

                st.markdown(
                    "**-**"
                )

            else:

                st.markdown(
                    f"**{avg20:+.1f}%**"
                )

        with c3:

            st.caption(
                "60일 흐름"
            )

            if pd.isna(avg60):

                st.markdown(
                    "**-**"
                )

            else:

                st.markdown(
                    f"**{avg60:+.1f}%**"
                )

        with c4:

            st.caption(
                "평균 거래량"
            )

            if pd.isna(avg_volume):

                st.markdown(
                    "**-**"
                )

            else:

                st.markdown(
                    f"**{avg_volume:.2f}x**"
                )

        st.caption(
            "테마점수는 대표 ETF의 추세·거래량·모멘텀을 "
            "단순 평균한 참고값입니다."
        )

        table = []

        for item in rows:

            table.append(
                {
                    "ETF": item["name"],
                    "20일": (
                        "-"
                        if pd.isna(item["return20"])
                        else f"{item['return20']:+.1f}%"
                    ),
                    "60일": (
                        "-"
                        if pd.isna(item["return60"])
                        else f"{item['return60']:+.1f}%"
                    ),
                    "거래량": (
                        "-"
                        if pd.isna(item["volume_ratio"])
                        else f"{item['volume_ratio']:.2f}x"
                    ),
                    "점수": f"{item['score']}",
                }
            )

        if table:

            st.dataframe(
                pd.DataFrame(table),
                use_container_width=True,
                hide_index=True,
            )

    else:

        st.warning(
            "현재 테마 ETF 가격 데이터를 불러오지 못했습니다."
        )

    # --------------------------------------------------------
    # CORE CHECKPOINT
    # --------------------------------------------------------

    st.markdown(
        "### 🔗 핵심 체크포인트"
    )

    keywords = theme.get(
        "keywords",
        []
    )

    if keywords is None:

        keywords = []

    elif isinstance(
        keywords,
        str
    ):

        keywords = [
            keywords
        ]

    elif not isinstance(
        keywords,
        (list, tuple)
    ):

        keywords = [
            str(keywords)
        ]

    valid_keywords = []

    for item in keywords:

        item = clean_text(
            item
        )

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

    # --------------------------------------------------------
    # BULL / BEAR
    # --------------------------------------------------------

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            "**🟢 강해지는 조건**"
        )

        bull = clean_text(
            theme.get(
                "bull",
                ""
            )
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
            theme.get(
                "bear",
                ""
            )
        )

        if bear:

            st.write(
                bear
            )

    watch = clean_text(
        theme.get(
            "watch",
            ""
        )
    )

    if watch:

        st.info(
            f"**가장 먼저 볼 것:** {watch}"
        )

    # --------------------------------------------------------
    # ETF ANALYSIS
    # --------------------------------------------------------

    if codes:

        st.markdown(
            "### 📊 대표 ETF 분석"
        )

        for code in codes[:4]:

            with st.expander(
                get_display_name(code),
                expanded=False
            ):

                render_analysis(
                    code
                )


# ============================================================
# FUTURE THEMES
# ============================================================

def render_future_theme():

    st.subheader(
        "🚀 미래 테마"
    )

    st.caption(
        "현재 주도 → 다음 수혜 → 초기 관심으로 "
        "자금 확산 경로를 확인합니다."
    )

    if st.button(
        "🔄 테마 데이터 새로고침",
        key="theme_refresh_button",
        use_container_width=True,
    ):

        try:
            fetch_yahoo.clear()
        except Exception:
            pass

        try:
            yahoo_search.clear()
        except Exception:
            pass

        try:
            load_krx_etf_universe.clear()
        except Exception:
            pass

        try:
            get_external_universe.clear()
        except Exception:
            pass

        st.session_state.theme_refresh_count += 1

        st.rerun()

    st.caption(
        f"수동 새로고침: "
        f"{st.session_state.theme_refresh_count}회"
    )

    st.divider()

    # --------------------------------------------------------
    # ROADMAP
    # --------------------------------------------------------

    roadmap = st.columns(
        len(THEMES)
    )

    for column, (
        theme_name,
        theme
    ) in zip(
        roadmap,
        THEMES.items()
    ):

        with column:

            st.caption(
                theme.get(
                    "rank",
                    ""
                )
            )

            st.markdown(
                f"**{theme.get('emoji', '📌')} "
                f"{theme_name}**"
            )

            st.caption(
                theme.get(
                    "stage",
                    ""
                )
            )

    st.divider()

    # --------------------------------------------------------
    # THEME DETAILS
    # --------------------------------------------------------

    for theme_name, theme in THEMES.items():

        with st.expander(
            f"{theme.get('emoji', '📌')} "
            f"{theme_name} · "
            f"{theme.get('stage', '')}",
            expanded=False,
        ):

            render_theme_card(
                theme_name,
                theme
            )

        st.divider()


# ============================================================
# HEADER
# ============================================================

def render_header():

    st.title(
        "📊 ETF RADAR"
    )

    st.caption(
        "ETF 검색 · 기술분석 · 가격대응 · 미래테마"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    render_header()

    tab1, tab2, tab3 = st.tabs(
        [
            "⭐ 내 ETF",
            "🔎 ETF 찾기",
            "🚀 미래 테마",
        ]
    )

    with tab1:

        render_my_etf()

    with tab2:

        render_search()

    with tab3:

        render_future_theme()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()