import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET


# ============================================================
# ETF RADAR
# Mobile ETF Research / Decision Support
# HTML BODY FREE VERSION
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CSS
# - CSS 외에는 HTML을 사용하지 않음
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 760px;
        padding-top: 1rem;
        padding-bottom: 3rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    h1 {
        letter-spacing: -0.04em;
    }

    h2, h3 {
        letter-spacing: -0.03em;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 10px 12px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.15rem;
    }

    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    button {
        border-radius: 10px !important;
    }

    [data-testid="stTabs"] button {
        font-weight: 700;
    }

    .small-gap {
        margin-top: 0.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FILES
# ============================================================

WATCHLIST_FILE = "watchlist.json"


# ============================================================
# ETF UNIVERSE
# ============================================================

ETF_UNIVERSE = {
    "360750": "TIGER 미국S&P500",
    "379800": "KODEX 미국S&P500TR",
    "448290": "SOL 미국S&P500",

    "133690": "TIGER 미국나스닥100",
    "379810": "KODEX 미국나스닥100TR",

    "487240": "KODEX 미국AI테크TOP10",
    "452330": "TIGER 미국테크TOP10",

    "395160": "KODEX AI반도체TOP2플러스",
    "462100": "TIGER AI반도체핵심공정",
    "486410": "TIGER 미국반도체TOP10",

    "471990": "KODEX AI전력핵심설비",
    "445380": "SOL 원자력TOP3플러스",
    "465560": "TIGER 글로벌원자력",

    "305540": "KODEX 2차전지산업",
    "364980": "TIGER 2차전지소부장",
    "438320": "KODEX 2차전지핵심소재",

    "465610": "KODEX 로봇산업",
    "476250": "TIGER 우주항공&로봇",

    "329200": "TIGER 헬스케어",
    "266420": "KODEX 바이오",
    "462610": "ARIRANG 3대주주바이오",

    "458730": "TIGER 미국배당다우존스",
    "476480": "KODEX 미국배당커버드콜",
    "451780": "TIGER 미국배당+7%프리미엄",

    "423160": "KODEX CD금리액티브(합성)",
    "449170": "TIGER KOFR금리액티브",

    "308620": "KODEX 미국채울트라30년선물",
    "365780": "TIGER 미국채30년스트립액티브",
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
# THEME DATABASE
# ============================================================

THEMES = {
    "AI 반도체": {
        "stage": "LEADER",
        "label": "현재 주도",
        "description": "AI 연산 수요와 반도체 투자 확대의 직접적인 수혜 영역",
        "etfs": [
            "395160",
            "462100",
            "486410",
            "487240",
            "452330",
        ],
    },

    "데이터센터": {
        "stage": "FOLLOWER",
        "label": "후속 수혜",
        "description": "AI 서버·데이터센터 증설에 따른 인프라 투자 확대",
        "etfs": [
            "471990",
            "487240",
            "486410",
        ],
    },

    "전력 인프라": {
        "stage": "FOLLOWER",
        "label": "후속 수혜",
        "description": "AI 데이터센터 전력 수요 증가와 전력설비 투자 확대",
        "etfs": [
            "471990",
            "445380",
            "465560",
        ],
    },

    "냉각·열관리": {
        "stage": "EARLY",
        "label": "선행 관심",
        "description": "고집적 AI 서버의 전력밀도 증가에 따른 냉각·열관리 영역",
        "etfs": [],
    },

    "AI 의료·바이오": {
        "stage": "EARLY",
        "label": "선행 관심",
        "description": "AI 기술과 의료·바이오 산업의 결합 영역",
        "etfs": [
            "329200",
            "266420",
            "462610",
        ],
    },

    "로봇·자동화": {
        "stage": "WATCH",
        "label": "관찰",
        "description": "AI와 자동화 기술의 산업 적용 확대 영역",
        "etfs": [
            "465610",
            "476250",
        ],
    },

    "2차전지": {
        "stage": "WATCH",
        "label": "관찰",
        "description": "전기차·ESS·배터리 소재 및 장비 관련 영역",
        "etfs": [
            "305540",
            "364980",
            "438320",
        ],
    },
}


THEME_CHAIN = [
    ("AI 반도체", "현재 주도"),
    ("데이터센터", "후속 수혜"),
    ("전력 인프라", "후속 수혜"),
    ("냉각·열관리", "선행 관심"),
    ("AI 의료·바이오", "선행 관심"),
]


# ============================================================
# WATCHLIST
# ============================================================

def load_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        return DEFAULT_WATCHLIST.copy()

    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            result = []

            for code in data:
                code = str(code)

                if code in ETF_UNIVERSE:
                    result.append(code)

            if result:
                return result

    except Exception:
        pass

    return DEFAULT_WATCHLIST.copy()


def save_watchlist(items):
    try:
        with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

        return True

    except Exception:
        return False


# ============================================================
# NAVER DATA
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def fetch_from_naver(code, count=500):

    url = (
        "https://fchart.stock.naver.com/sise.nhn?"
        f"symbol={urllib.parse.quote(code)}"
        f"&timeframe=day"
        f"&count={count}"
        f"&requestType=0"
    )

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            data = response.read()

        root = ET.fromstring(data)

        rows = []

        for item in root.findall(".//item"):

            raw = item.attrib.get("data", "")

            parts = raw.split("|")

            if len(parts) != 6:
                continue

            date_value, open_value, high_value, low_value, close_value, volume_value = parts

            rows.append(
                [
                    date_value,
                    float(open_value),
                    float(high_value),
                    float(low_value),
                    float(close_value),
                    float(volume_value),
                ]
            )

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(
            rows,
            columns=[
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ],
        )

        df["Date"] = pd.to_datetime(df["Date"])

        df = df.sort_values("Date")

        df = df.set_index("Date")

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# YAHOO FALLBACK
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def fetch_from_yahoo(code):

    try:

        ticker = yf.Ticker(f"{code}.KS")

        df = ticker.history(
            period="2y",
            interval="1d",
            auto_adjust=False,
        )

        if df.empty:
            return pd.DataFrame()

        df = df.reset_index()

        if "Datetime" in df.columns:
            df = df.rename(columns={"Datetime": "Date"})

        df["Date"] = pd.to_datetime(df["Date"])

        df = df.set_index("Date")

        columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]

        df = df[[c for c in columns if c in df.columns]]

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# DATA LOADER
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def load_price_data(code):

    df = fetch_from_naver(code, 500)

    if df.empty:
        df = fetch_from_yahoo(code)

    if df.empty:
        return pd.DataFrame()

    df = df.copy()

    numeric_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    for column in numeric_columns:

        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    df = df.dropna(subset=["Close"])

    return df


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

def calculate_indicators(df):

    df = df.copy()

    if df.empty:
        return df

    close = df["Close"]

    # Moving averages
    df["MA5"] = close.rolling(5).mean()
    df["MA20"] = close.rolling(20).mean()
    df["MA60"] = close.rolling(60).mean()
    df["MA120"] = close.rolling(120).mean()

    # RSI
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    df["RSI14"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = close.ewm(
        span=12,
        adjust=False,
    ).mean()

    ema26 = close.ewm(
        span=26,
        adjust=False,
    ).mean()

    df["MACD"] = ema12 - ema26

    df["MACD_SIGNAL"] = df["MACD"].ewm(
        span=9,
        adjust=False,
    ).mean()

    df["MACD_HIST"] = (
        df["MACD"] -
        df["MACD_SIGNAL"]
    )

    # Bollinger
    middle = close.rolling(20).mean()
    std = close.rolling(20).std()

    df["BB_MID"] = middle
    df["BB_UPPER"] = middle + std * 2
    df["BB_LOWER"] = middle - std * 2

    # Volume
    df["VOL20"] = df["Volume"].rolling(20).mean()

    df["VOLUME_RATIO"] = (
        df["Volume"] /
        df["VOL20"]
    )

    # Returns
    df["RET5"] = close.pct_change(5) * 100
    df["RET20"] = close.pct_change(20) * 100
    df["RET60"] = close.pct_change(60) * 100

    # Recent high/low
    df["HIGH20"] = close.rolling(20).max()
    df["LOW20"] = close.rolling(20).min()

    return df


# ============================================================
# SUPPORT / RESISTANCE
# ============================================================

def calculate_support_resistance(df):

    if df.empty:
        return np.nan, np.nan

    latest = df.iloc[-1]

    support_candidates = []

    for column in [
        "MA20",
        "MA60",
        "LOW20",
    ]:

        value = latest.get(column)

        if pd.notna(value):
            support_candidates.append(float(value))

    resistance = latest.get("HIGH20")

    if support_candidates:
        support = max(support_candidates)
    else:
        support = np.nan

    if pd.notna(resistance):
        resistance = float(resistance)
    else:
        resistance = np.nan

    return support, resistance


# ============================================================
# JUDGMENT ENGINE
# ============================================================

def get_judgment(df):

    if df.empty or len(df) < 60:
        return {
            "label": "데이터 부족",
            "type": "info",
            "reason": "충분한 가격 데이터가 없어 판단을 보류합니다.",
            "trend": "확인 필요",
        }

    latest = df.iloc[-1]

    close = float(latest["Close"])

    ma20 = latest["MA20"]
    ma60 = latest["MA60"]
    rsi = latest["RSI14"]
    macd = latest["MACD"]
    signal = latest["MACD_SIGNAL"]
    ret20 = latest["RET20"]

    if any(
        pd.isna(x)
        for x in [
            ma20,
            ma60,
            rsi,
            macd,
            signal,
        ]
    ):
        return {
            "label": "관망",
            "type": "info",
            "reason": "주요 지표가 충분히 형성되지 않았습니다.",
            "trend": "확인 필요",
        }

    positive_trend = (
        close > ma20
        and ma20 > ma60
    )

    weak_trend = (
        close < ma20
        and ma20 < ma60
    )

    extended = (
        rsi >= 70
        or close >= ma20 * 1.08
        or (
            pd.notna(ret20)
            and ret20 >= 12
        )
    )

    near_ma20 = (
        abs(close - ma20) /
        ma20 <= 0.035
    )

    momentum_positive = macd > signal

    if weak_trend:

        return {
            "label": "리스크 재검토",
            "type": "error",
            "reason": "현재가가 MA20 아래에 있고 MA20도 MA60보다 낮아 추세가 약한 상태입니다.",
            "trend": "하락/약세",
        }

    if positive_trend and extended:

        return {
            "label": "눌림목 대기",
            "type": "warning",
            "reason": "중기 추세는 긍정적이지만 단기 상승폭 또는 RSI가 높아 추격보다는 조정을 확인하는 구간입니다.",
            "trend": "상승 추세",
        }

    if (
        positive_trend
        and near_ma20
        and 42 <= rsi <= 67
    ):

        return {
            "label": "매수 검토",
            "type": "success",
            "reason": "MA20 부근의 눌림과 양호한 중기 추세가 함께 나타나는 구간입니다.",
            "trend": "상승 추세",
        }

    if positive_trend:

        return {
            "label": "보유 유지",
            "type": "success",
            "reason": "현재가가 MA20과 MA60 위에 있어 중기 추세가 유지되고 있습니다.",
            "trend": "상승 추세",
        }

    if (
        momentum_positive
        and rsi >= 45
    ):

        return {
            "label": "관망 후 확인",
            "type": "warning",
            "reason": "모멘텀은 개선되고 있지만 추세 전환이 완전히 확인되지는 않았습니다.",
            "trend": "전환 확인",
        }

    return {
        "label": "관망",
        "type": "info",
        "reason": "현재 방향성이 뚜렷하지 않아 추세 확인 후 접근하는 편이 적절합니다.",
        "trend": "중립",
    }


# ============================================================
# HOLDING SCENARIO
# ============================================================

def holding_scenario(
    df,
    average_price,
    shares,
):

    if df.empty:
        return None

    latest = df.iloc[-1]

    price = float(latest["Close"])

    ma20 = latest["MA20"]
    ma60 = latest["MA60"]
    rsi = latest["RSI14"]
    macd = latest["MACD"]
    signal = latest["MACD_SIGNAL"]

    support, resistance = calculate_support_resistance(df)

    profit = (
        price - average_price
    ) * shares

    profit_pct = (
        (price / average_price) - 1
    ) * 100

    risk_condition = False

    if pd.notna(ma20) and pd.notna(ma60):

        if (
            price < ma20
            and ma20 < ma60
        ):
            risk_condition = True

    if risk_condition:

        action = "리스크 재검토"

        explanation = (
            "현재가가 MA20 아래로 내려가고 중기 이동평균 구조도 약해지고 있습니다. "
            "추가매수보다는 추세 회복 여부를 확인하는 구간입니다."
        )

    elif (
        pd.notna(resistance)
        and price >= resistance * 0.97
        and pd.notna(rsi)
        and rsi >= 68
    ):

        action = "일부 이익실현 검토"

        explanation = (
            "최근 저항권에 접근했고 RSI도 높은 편입니다. "
            "추가 상승 가능성을 열어두되 일부 이익실현 여부를 검토할 수 있는 구간입니다."
        )

    elif (
        pd.notna(ma20)
        and abs(price - ma20) / ma20 <= 0.035
        and pd.notna(rsi)
        and 42 <= rsi <= 67
        and price > ma60
    ):

        action = "추가매수 검토"

        explanation = (
            "중기 추세가 유지되는 가운데 MA20 부근까지 조정된 상태입니다. "
            "지지 확인 시 분할 접근을 검토할 수 있습니다."
        )

    else:

        action = "보유 유지 검토"

        explanation = (
            "현재 추세가 크게 훼손되지 않았습니다. "
            "MA20과 MA60의 방향을 중심으로 보유 여부를 점검하는 구간입니다."
        )

    return {
        "price": price,
        "profit": profit,
        "profit_pct": profit_pct,
        "action": action,
        "explanation": explanation,
        "support": support,
        "resistance": resistance,
    }


# ============================================================
# CHART
# ============================================================

def draw_chart(df, period):

    if df.empty:
        st.warning("차트 데이터가 없습니다.")
        return

    period_days = {
        "1M": 22,
        "3M": 66,
        "6M": 132,
        "1Y": 252,
    }

    days = period_days.get(period, 66)

    chart_df = df.tail(days).copy()

    if chart_df.empty:
        st.warning("선택한 기간의 데이터가 없습니다.")
        return

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.78, 0.22],
        vertical_spacing=0.04,
    )

    # Price
    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["Close"],
            name="가격",
            mode="lines",
            line=dict(width=2),
        ),
        row=1,
        col=1,
    )

    # MA20
    if "MA20" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["MA20"],
                name="MA20",
                mode="lines",
                line=dict(width=1.5),
            ),
            row=1,
            col=1,
        )

    # MA60
    if "MA60" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["MA60"],
                name="MA60",
                mode="lines",
                line=dict(width=1.5),
            ),
            row=1,
            col=1,
        )

    # Volume
    fig.add_trace(
        go.Bar(
            x=chart_df.index,
            y=chart_df["Volume"],
            name="거래량",
            opacity=0.5,
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        height=430,
        margin=dict(
            l=5,
            r=5,
            t=10,
            b=5,
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
        ),
        hovermode="x unified",
        dragmode=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    fig.update_xaxes(
        fixedrange=True,
        showgrid=False,
        rangeslider_visible=False,
    )

    fig.update_yaxes(
        fixedrange=True,
        showgrid=True,
        gridcolor="#eeeeee",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "doubleClick": False,
            "responsive": True,
        },
    )


# ============================================================
# FORMAT FUNCTIONS
# ============================================================

def fmt_price(value):

    if pd.isna(value):
        return "-"

    return f"{value:,.0f}원"


def fmt_pct(value):

    if pd.isna(value):
        return "-"

    return f"{value:+.2f}%"


def fmt_ratio(value):

    if pd.isna(value):
        return "-"

    return f"{value:.2f}배"


# ============================================================
# ETF SEARCH
# ============================================================

def search_etfs(keyword):

    keyword = keyword.strip().lower()

    if not keyword:
        return ETF_UNIVERSE

    result = {}

    for code, name in ETF_UNIVERSE.items():

        if (
            keyword in code.lower()
            or keyword in name.lower()
        ):
            result[code] = name

    return result


# ============================================================
# ETF DETAIL
# ============================================================

def render_etf_detail(
    code,
    name,
):

    st.subheader(name)

    with st.spinner("ETF 데이터를 불러오는 중입니다..."):

        df = load_price_data(code)

    if df.empty:

        st.error(
            "가격 데이터를 불러오지 못했습니다. "
            "잠시 후 다시 시도해주세요."
        )

        return

    df = calculate_indicators(df)

    latest = df.iloc[-1]

    price = float(latest["Close"])

    previous = (
        df["Close"].iloc[-2]
        if len(df) >= 2
        else np.nan
    )

    if pd.notna(previous) and previous != 0:

        daily_change = (
            (price / previous) - 1
        ) * 100

    else:

        daily_change = np.nan

    judgment = get_judgment(df)

    support, resistance = calculate_support_resistance(df)

    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    st.caption(
        f"최근 데이터: {df.index[-1].strftime('%Y-%m-%d')}"
    )

    price_col1, price_col2 = st.columns(2)

    with price_col1:

        st.metric(
            "현재가",
            fmt_price(price),
            fmt_pct(daily_change),
        )

    with price_col2:

        st.metric(
            "20일 수익률",
            fmt_pct(latest["RET20"]),
            f"60일 {fmt_pct(latest['RET60'])}",
        )

    # --------------------------------------------------------
    # JUDGMENT
    # --------------------------------------------------------

    st.markdown("### 오늘의 판단")

    if judgment["type"] == "success":

        st.success(
            f"**{judgment['label']}**\n\n"
            f"{judgment['reason']}"
        )

    elif judgment["type"] == "warning":

        st.warning(
            f"**{judgment['label']}**\n\n"
            f"{judgment['reason']}"
        )

    elif judgment["type"] == "error":

        st.error(
            f"**{judgment['label']}**\n\n"
            f"{judgment['reason']}"
        )

    else:

        st.info(
            f"**{judgment['label']}**\n\n"
            f"{judgment['reason']}"
        )

    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    st.markdown("### 판단 근거")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "추세",
            judgment["trend"],
        )

    with c2:

        st.metric(
            "MA20",
            fmt_price(latest["MA20"]),
        )

    with c3:

        st.metric(
            "MA60",
            fmt_price(latest["MA60"]),
        )

    c4, c5, c6 = st.columns(3)

    with c4:

        st.metric(
            "RSI",
            f"{latest['RSI14']:.1f}"
            if pd.notna(latest["RSI14"])
            else "-",
        )

    with c5:

        st.metric(
            "거래량",
            fmt_ratio(latest["VOLUME_RATIO"]),
        )

    with c6:

        st.metric(
            "MACD",
            "긍정"
            if latest["MACD"] > latest["MACD_SIGNAL"]
            else "약화",
        )

    # --------------------------------------------------------
    # SUPPORT / RESISTANCE
    # --------------------------------------------------------

    st.markdown("### 가격 구간")

    p1, p2 = st.columns(2)

    with p1:

        st.metric(
            "주요 지지",
            fmt_price(support),
        )

    with p2:

        st.metric(
            "주요 저항",
            fmt_price(resistance),
        )

    # --------------------------------------------------------
    # HOLDING
    # --------------------------------------------------------

    st.markdown("### 보유 여부")

    holding = st.radio(
        "현재 보유하고 있습니까?",
        [
            "아니오",
            "예",
        ],
        horizontal=True,
        key=f"holding_{code}",
    )

    if holding == "예":

        input1, input2 = st.columns(2)

        with input1:

            average_price = st.number_input(
                "평균 매수가",
                min_value=0.0,
                value=float(price),
                step=100.0,
                key=f"avg_{code}",
            )

        with input2:

            shares = st.number_input(
                "보유 수량",
                min_value=0.0,
                value=1.0,
                step=1.0,
                key=f"shares_{code}",
            )

        scenario = holding_scenario(
            df,
            average_price,
            shares,
        )

        if scenario:

            st.markdown("### 보유 포지션")

            h1, h2, h3 = st.columns(3)

            with h1:

                st.metric(
                    "평가손익",
                    f"{scenario['profit']:+,.0f}원",
                )

            with h2:

                st.metric(
                    "수익률",
                    f"{scenario['profit_pct']:+.2f}%",
                )

            with h3:

                st.metric(
                    "현재가",
                    fmt_price(scenario["price"]),
                )

            st.markdown("### 대응 시나리오")

            if scenario["action"] == "추가매수 검토":

                st.success(
                    f"**{scenario['action']}**\n\n"
                    f"{scenario['explanation']}"
                )

            elif scenario["action"] == "리스크 재검토":

                st.error(
                    f"**{scenario['action']}**\n\n"
                    f"{scenario['explanation']}"
                )

            elif scenario["action"] == "일부 이익실현 검토":

                st.warning(
                    f"**{scenario['action']}**\n\n"
                    f"{scenario['explanation']}"
                )

            else:

                st.info(
                    f"**{scenario['action']}**\n\n"
                    f"{scenario['explanation']}"
                )

    else:

        st.info(
            "보유하지 않은 ETF입니다.\n\n"
            "현재 추세가 유지되고 있고 MA20 부근에서 눌림이 확인되면 "
            "매수 검토 대상으로 볼 수 있습니다. "
            "단기 급등 구간에서는 추격보다 눌림을 기다리는 방식으로 접근합니다."
        )

    # --------------------------------------------------------
    # CHART
    # --------------------------------------------------------

    st.markdown("### 차트")

    period = st.radio(
        "차트 기간",
        [
            "1M",
            "3M",
            "6M",
            "1Y",
        ],
        index=1,
        horizontal=True,
        key=f"period_{code}",
        label_visibility="collapsed",
    )

    draw_chart(
        df,
        period,
    )

    # --------------------------------------------------------
    # NEXT WATCH
    # --------------------------------------------------------

    st.markdown("### 다음에 볼 것")

    watch_items = []

    if pd.notna(latest["MA20"]):

        if price > latest["MA20"]:

            watch_items.append(
                "현재가는 MA20 위에 있습니다."
            )

        else:

            watch_items.append(
                "현재가가 MA20 아래인지 확인하세요."
            )

    if pd.notna(latest["MA60"]):

        if price > latest["MA60"]:

            watch_items.append(
                "MA60 위에서 추세가 유지되는지 확인하세요."
            )

        else:

            watch_items.append(
                "MA60 회복 여부를 확인하세요."
            )

    if pd.notna(latest["RSI14"]):

        if latest["RSI14"] >= 70:

            watch_items.append(
                "RSI가 높아 단기 추격 위험을 확인하세요."
            )

        elif latest["RSI14"] <= 40:

            watch_items.append(
                "RSI가 낮아 반등 여부를 확인하세요."
            )

        else:

            watch_items.append(
                "RSI가 극단적이지 않아 추세를 함께 확인하세요."
            )

    for item in watch_items:

        st.write(
            f"• {item}"
        )

    # --------------------------------------------------------
    # TECHNICAL DETAIL
    # --------------------------------------------------------

    with st.expander("상세 기술지표 보기"):

        t1, t2, t3 = st.columns(3)

        with t1:

            st.metric(
                "MA5",
                fmt_price(latest["MA5"]),
            )

        with t2:

            st.metric(
                "MA20",
                fmt_price(latest["MA20"]),
            )

        with t3:

            st.metric(
                "MA60",
                fmt_price(latest["MA60"]),
            )

        t4, t5, t6 = st.columns(3)

        with t4:

            st.metric(
                "MA120",
                fmt_price(latest["MA120"]),
            )

        with t5:

            st.metric(
                "BB 상단",
                fmt_price(latest["BB_UPPER"]),
            )

        with t6:

            st.metric(
                "BB 하단",
                fmt_price(latest["BB_LOWER"]),
            )

        t7, t8, t9 = st.columns(3)

        with t7:

            st.metric(
                "RSI14",
                f"{latest['RSI14']:.1f}"
                if pd.notna(latest["RSI14"])
                else "-",
            )

        with t8:

            st.metric(
                "MACD",
                f"{latest['MACD']:.2f}"
                if pd.notna(latest["MACD"])
                else "-",
            )

        with t9:

            st.metric(
                "MACD Signal",
                f"{latest['MACD_SIGNAL']:.2f}"
                if pd.notna(latest["MACD_SIGNAL"])
                else "-",
            )

        st.markdown("#### 최근 데이터")

        technical_columns = [
            "Close",
            "MA20",
            "MA60",
            "RSI14",
            "MACD",
            "VOLUME_RATIO",
            "RET5",
            "RET20",
            "RET60",
        ]

        available_columns = [
            c
            for c in technical_columns
            if c in df.columns
        ]

        recent = df[
            available_columns
        ].tail(10).copy()

        st.dataframe(
            recent,
            use_container_width=True,
        )


# ============================================================
# MY ETF TAB
# ============================================================

def render_my_etf():

    st.title("📊 ETF RADAR")

    st.caption(
        "내 ETF를 한눈에 보고, 지금은 매수·보유·눌림·관망 중 어디에 가까운지 확인합니다."
    )

    # --------------------------------------------------------
    # WATCHLIST
    # --------------------------------------------------------

    watchlist = load_watchlist()

    if "selected_code" not in st.session_state:

        if watchlist:
            st.session_state.selected_code = watchlist[0]

        else:
            st.session_state.selected_code = list(
                ETF_UNIVERSE.keys()
            )[0]

    st.markdown("### 내 ETF")

    if watchlist:

        watch_names = [
            ETF_UNIVERSE.get(
                code,
                code,
            )
            for code in watchlist
        ]

        selected_index = 0

        if st.session_state.selected_code in watchlist:

            selected_index = watchlist.index(
                st.session_state.selected_code
            )

        selected_name = st.selectbox(
            "관심 ETF",
            watch_names,
            index=selected_index,
            label_visibility="collapsed",
        )

        for code, name in ETF_UNIVERSE.items():

            if name == selected_name:

                st.session_state.selected_code = code
                break

    else:

        st.info(
            "관심 ETF가 없습니다. 아래 검색에서 ETF를 추가해주세요."
        )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    st.markdown("### ETF 찾기")

    keyword = st.text_input(
        "ETF 검색",
        placeholder="예: AI, 반도체, 나스닥, 전력",
        label_visibility="collapsed",
    )

    search_result = search_etfs(keyword)

    if search_result:

        search_names = list(
            search_result.values()
        )

        search_selected = st.selectbox(
            "검색 결과",
            search_names,
        )

        selected_search_code = next(
            (
                code
                for code, name in search_result.items()
                if name == search_selected
            ),
            None,
        )

        b1, b2 = st.columns(2)

        with b1:

            if st.button(
                "관심종목에 추가",
                use_container_width=True,
            ):

                if selected_search_code:

                    if selected_search_code not in watchlist:

                        watchlist.append(
                            selected_search_code
                        )

                        if save_watchlist(watchlist):

                            st.session_state.selected_code = (
                                selected_search_code
                            )

                            st.success(
                                f"{search_selected} 추가 완료"
                            )

                            st.rerun()

                    else:

                        st.info(
                            "이미 관심종목에 있습니다."
                        )

        with b2:

            if st.button(
                "현재 ETF 삭제",
                use_container_width=True,
            ):

                current_code = (
                    st.session_state.selected_code
                )

                if current_code in watchlist:

                    watchlist.remove(
                        current_code
                    )

                    save_watchlist(
                        watchlist
                    )

                    if watchlist:

                        st.session_state.selected_code = watchlist[0]

                    st.success(
                        "관심종목에서 삭제했습니다."
                    )

                    st.rerun()

    # --------------------------------------------------------
    # DETAIL
    # --------------------------------------------------------

    code = st.session_state.selected_code

    name = ETF_UNIVERSE.get(
        code,
        code,
    )

    st.divider()

    render_etf_detail(
        code,
        name,
    )


# ============================================================
# THEME TAB
# ============================================================

def render_theme_etf(code):

    name = ETF_UNIVERSE.get(
        code,
        code,
    )

    with st.spinner(
        f"{name} 분석 중..."
    ):

        df = load_price_data(code)

    if df.empty:
        return None

    df = calculate_indicators(df)

    latest = df.iloc[-1]

    judgment = get_judgment(df)

    return {
        "code": code,
        "name": name,
        "price": latest["Close"],
        "ret20": latest["RET20"],
        "rsi": latest["RSI14"],
        "judgment": judgment["label"],
    }


def render_future_theme():

    st.title("🚀 미래테마")

    st.caption(
        "현재 주도 → 후속 수혜 → 선행 관심 순서로 테마의 연결고리를 살펴봅니다."
    )

    st.info(
        "테마의 단계는 투자 확정 신호가 아니라 리서치용 분류입니다. "
        "ETF 가격 추세와 실제 투자 흐름을 함께 확인하세요."
    )

    # --------------------------------------------------------
    # REFRESH
    # --------------------------------------------------------

    if st.button(
        "🔄 테마 데이터 새로고침",
        use_container_width=True,
    ):

        st.cache_data.clear()

        st.rerun()

    # --------------------------------------------------------
    # THEME CHAIN
    # --------------------------------------------------------

    st.markdown("### 테마 순환 구조")

    chain_cols = st.columns(
        len(THEME_CHAIN)
    )

    for index, (
        theme_name,
        label,
    ) in enumerate(THEME_CHAIN):

        with chain_cols[index]:

            st.caption(
                label
            )

            st.markdown(
                f"**{theme_name}**"
            )

    st.divider()

    # --------------------------------------------------------
    # THEME CARDS
    # --------------------------------------------------------

    for theme_name, info in THEMES.items():

        with st.container():

            st.subheader(
                theme_name
            )

            if info["stage"] == "LEADER":

                st.success(
                    f"현재 주도 · {info['description']}"
                )

            elif info["stage"] == "FOLLOWER":

                st.info(
                    f"후속 수혜 · {info['description']}"
                )

            elif info["stage"] == "EARLY":

                st.warning(
                    f"선행 관심 · {info['description']}"
                )

            else:

                st.caption(
                    f"관찰 · {info['description']}"
                )

            codes = info["etfs"]

            if not codes:

                st.caption(
                    "현재 앱의 ETF 목록에서는 전용 ETF를 별도로 연결하지 않았습니다."
                )

                st.divider()

                continue

            results = []

            for code in codes:

                result = render_theme_etf(
                    code
                )

                if result:

                    results.append(
                        result
                    )

            if results:

                for result in results:

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.write(
                            f"**{result['name']}**"
                        )

                        st.caption(
                            result["code"]
                        )

                    with col2:

                        st.metric(
                            "20일",
                            fmt_pct(
                                result["ret20"]
                            ),
                        )

                    with col3:

                        st.metric(
                            "판단",
                            result["judgment"],
                        )

            st.divider()

    # --------------------------------------------------------
    # EARLY / GEM
    # --------------------------------------------------------

    st.markdown("### 🔎 원석 후보")

    early_themes = [
        theme
        for theme, info in THEMES.items()
        if info["stage"] == "EARLY"
    ]

    if early_themes:

        for theme in early_themes:

            info = THEMES[theme]

            st.warning(
                f"**{theme}**\n\n"
                f"{info['description']}"
            )

            if info["etfs"]:

                for code in info["etfs"]:

                    st.write(
                        f"• {ETF_UNIVERSE.get(code, code)}"
                    )

            else:

                st.caption(
                    "현재 등록된 국내 ETF 중 직접 연결할 전용 상품이 없습니다."
                )

    # --------------------------------------------------------
    # RESEARCH LOGIC
    # --------------------------------------------------------

    st.markdown("### 테마를 보는 방법")

    st.write(
        "• LEADER : 현재 시장의 관심이 집중되는 주도 영역"
    )

    st.write(
        "• FOLLOWER : 주도 영역의 투자 확대에 따라 후속 수혜를 받을 수 있는 영역"
    )

    st.write(
        "• EARLY : 아직 시장 관심이 상대적으로 낮지만 구조적인 성장 가능성을 관찰하는 영역"
    )

    st.write(
        "• WATCH : 방향성이 확인될 때까지 관찰하는 영역"
    )


# ============================================================
# MAIN
# ============================================================

tab1, tab2 = st.tabs(
    [
        "📌 내 ETF",
        "🚀 미래테마",
    ]
)


with tab1:

    render_my_etf()


with tab2:

    render_future_theme()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ETF RADAR · 시장 데이터 기반 리서치 보조 도구 · 투자 판단은 사용자가 최종 결정"
)