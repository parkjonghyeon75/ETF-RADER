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
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 760px;
        padding-top: 0.8rem;
        padding-bottom: 3rem;
        padding-left: 0.9rem;
        padding-right: 0.9rem;
    }

    h1 {
        letter-spacing: -0.05em;
    }

    h2, h3 {
        letter-spacing: -0.04em;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 10px 12px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.12rem;
    }

    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    button {
        border-radius: 10px !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FILE
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
        "keywords": [
            "AI",
            "반도체",
            "반도체TOP2",
            "핵심공정",
        ],
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
        "description": "AI 서버와 데이터센터 증설에 따른 인프라 투자 확대",
        "keywords": [
            "데이터센터",
            "서버",
            "AI인프라",
        ],
        "etfs": [
            "471990",
            "487240",
            "486410",
        ],
    },

    "전력 인프라": {
        "stage": "FOLLOWER",
        "label": "후속 수혜",
        "description": "AI 데이터센터 전력 수요 증가에 따른 전력설비 투자 영역",
        "keywords": [
            "전력",
            "전력인프라",
            "원자력",
        ],
        "etfs": [
            "471990",
            "445380",
            "465560",
        ],
    },

    "냉각·열관리": {
        "stage": "EARLY",
        "label": "선행 관심",
        "description": "AI 서버 고집적화에 따른 냉각과 열관리 수요 증가 영역",
        "keywords": [
            "냉각",
            "열관리",
            "쿨링",
        ],
        "etfs": [],
    },

    "AI 의료·바이오": {
        "stage": "EARLY",
        "label": "선행 관심",
        "description": "AI 기술과 의료·바이오 산업의 결합 영역",
        "keywords": [
            "의료",
            "바이오",
            "헬스케어",
        ],
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
        "keywords": [
            "로봇",
            "자동화",
        ],
        "etfs": [
            "465610",
            "476250",
        ],
    },

    "2차전지": {
        "stage": "WATCH",
        "label": "관찰",
        "description": "전기차·ESS·배터리 소재 및 장비 관련 영역",
        "keywords": [
            "2차전지",
            "배터리",
            "소부장",
        ],
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
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "내 ETF"

if "selected_code" not in st.session_state:
    st.session_state.selected_code = DEFAULT_WATCHLIST[0]

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "search_results" not in st.session_state:
    st.session_state.search_results = {}

if "search_selected_code" not in st.session_state:
    st.session_state.search_selected_code = None


# ============================================================
# WATCHLIST
# ============================================================

def load_watchlist():

    if not os.path.exists(WATCHLIST_FILE):
        return DEFAULT_WATCHLIST.copy()

    try:

        with open(
            WATCHLIST_FILE,
            "r",
            encoding="utf-8",
        ) as f:

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

        with open(
            WATCHLIST_FILE,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                items,
                f,
                ensure_ascii=False,
                indent=2,
            )

        return True

    except Exception:

        return False


# ============================================================
# NAVER DATA
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner=False,
)
def fetch_from_naver(
    code,
    count=500,
):

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
                "User-Agent": "Mozilla/5.0",
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=10,
        ) as response:

            data = response.read()

        root = ET.fromstring(data)

        rows = []

        for item in root.findall(".//item"):

            raw = item.attrib.get(
                "data",
                "",
            )

            parts = raw.split("|")

            if len(parts) != 6:
                continue

            (
                date_value,
                open_value,
                high_value,
                low_value,
                close_value,
                volume_value,
            ) = parts

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

        df["Date"] = pd.to_datetime(
            df["Date"]
        )

        df = df.sort_values("Date")

        df = df.set_index("Date")

        return df

    except Exception:

        return pd.DataFrame()


# ============================================================
# YAHOO FALLBACK
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner=False,
)
def fetch_from_yahoo(code):

    try:

        ticker = yf.Ticker(
            f"{code}.KS"
        )

        df = ticker.history(
            period="2y",
            interval="1d",
            auto_adjust=False,
        )

        if df.empty:
            return pd.DataFrame()

        df = df.reset_index()

        if "Datetime" in df.columns:

            df = df.rename(
                columns={
                    "Datetime": "Date"
                }
            )

        df["Date"] = pd.to_datetime(
            df["Date"]
        )

        df = df.set_index("Date")

        columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]

        df = df[
            [
                c
                for c in columns
                if c in df.columns
            ]
        ]

        return df

    except Exception:

        return pd.DataFrame()


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner=False,
)
def load_price_data(code):

    df = fetch_from_naver(
        code,
        500,
    )

    if df.empty:

        df = fetch_from_yahoo(
            code
        )

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

    df = df.dropna(
        subset=["Close"]
    )

    return df


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

def calculate_indicators(df):

    df = df.copy()

    if df.empty:
        return df

    close = df["Close"]

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

    rs = avg_gain / avg_loss.replace(
        0,
        np.nan,
    )

    df["RSI14"] = (
        100 -
        (
            100 /
            (1 + rs)
        )
    )

    # MACD
    ema12 = close.ewm(
        span=12,
        adjust=False,
    ).mean()

    ema26 = close.ewm(
        span=26,
        adjust=False,
    ).mean()

    df["MACD"] = (
        ema12 -
        ema26
    )

    df["MACD_SIGNAL"] = (
        df["MACD"]
        .ewm(
            span=9,
            adjust=False,
        )
        .mean()
    )

    df["MACD_HIST"] = (
        df["MACD"] -
        df["MACD_SIGNAL"]
    )

    # Bollinger
    middle = close.rolling(20).mean()
    std = close.rolling(20).std()

    df["BB_MID"] = middle
    df["BB_UPPER"] = (
        middle +
        std * 2
    )

    df["BB_LOWER"] = (
        middle -
        std * 2
    )

    # Volume
    df["VOL20"] = (
        df["Volume"]
        .rolling(20)
        .mean()
    )

    df["VOLUME_RATIO"] = (
        df["Volume"] /
        df["VOL20"]
    )

    # Returns
    df["RET5"] = (
        close.pct_change(5) *
        100
    )

    df["RET20"] = (
        close.pct_change(20) *
        100
    )

    df["RET60"] = (
        close.pct_change(60) *
        100
    )

    # High / Low
    df["HIGH20"] = (
        close.rolling(20).max()
    )

    df["LOW20"] = (
        close.rolling(20).min()
    )

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

            support_candidates.append(
                float(value)
            )

    if support_candidates:

        support = max(
            support_candidates
        )

    else:

        support = np.nan

    resistance = latest.get(
        "HIGH20"
    )

    if pd.notna(resistance):

        resistance = float(
            resistance
        )

    else:

        resistance = np.nan

    return support, resistance


# ============================================================
# PRICE ZONES
# ============================================================

def calculate_price_zones(df):

    if df.empty:
        return {}

    latest = df.iloc[-1]

    ma20 = latest["MA20"]
    ma60 = latest["MA60"]

    support, resistance = (
        calculate_support_resistance(df)
    )

    zones = {}

    # 1차 접근
    if pd.notna(ma20):

        zones["primary_low"] = (
            ma20 * 0.97
        )

        zones["primary_high"] = (
            ma20 * 1.02
        )

    # 2차 접근
    if pd.notna(ma60):

        zones["secondary_low"] = (
            ma60 * 0.97
        )

        zones["secondary_high"] = (
            ma60 * 1.02
        )

    # 저항
    if pd.notna(resistance):

        zones["resistance_low"] = (
            resistance * 0.97
        )

        zones["resistance_high"] = (
            resistance * 1.02
        )

    zones["support"] = support

    zones["resistance"] = resistance

    return zones


# ============================================================
# JUDGMENT
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

    close = latest["Close"]
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
        abs(close - ma20)
        / ma20
        <= 0.035
    )

    momentum_positive = (
        macd > signal
    )

    if weak_trend:

        return {
            "label": "리스크 재검토",
            "type": "error",
            "reason": "현재가가 MA20 아래이고 MA20도 MA60보다 낮아 중기 추세가 약해진 상태입니다.",
            "trend": "약세",
        }

    if positive_trend and extended:

        return {
            "label": "눌림목 대기",
            "type": "warning",
            "reason": "중기 추세는 살아 있지만 단기 상승폭이 커졌습니다. 지금 추격하기보다 MA20 부근 조정 여부를 확인하는 편이 좋습니다.",
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
            "reason": "중기 상승 추세 안에서 MA20 부근까지 눌림이 나타났고 RSI도 과열권이 아닙니다.",
            "trend": "상승 추세",
        }

    if positive_trend:

        return {
            "label": "보유 유지",
            "type": "success",
            "reason": "현재가가 MA20과 MA60 위에 있어 중기 상승 구조가 유지되고 있습니다. 급등 여부만 확인하면 됩니다.",
            "trend": "상승 추세",
        }

    if (
        momentum_positive
        and rsi >= 45
    ):

        return {
            "label": "관망 후 확인",
            "type": "warning",
            "reason": "MACD 모멘텀은 개선되고 있지만 아직 중기 추세 전환이 완전히 확인되지 않았습니다.",
            "trend": "전환 확인",
        }

    return {
        "label": "관망",
        "type": "info",
        "reason": "현재 추세 방향이 뚜렷하지 않습니다. MA20과 MA60 방향을 확인한 뒤 접근하는 구간입니다.",
        "trend": "중립",
    }


# ============================================================
# EXPLANATION HELPERS
# ============================================================

def rsi_comment(rsi):

    if pd.isna(rsi):
        return "RSI 데이터를 확인할 수 없습니다."

    if rsi >= 70:
        return "단기 과열권입니다. 추격 매수는 주의가 필요합니다."

    if rsi >= 60:
        return "상승 모멘텀이 강한 편이지만 단기 추격은 가격 위치를 함께 봐야 합니다."

    if rsi >= 45:
        return "중립~양호한 구간입니다. 추세와 함께 보면 됩니다."

    if rsi >= 30:
        return "상대적으로 약한 구간입니다. 반등 여부를 확인할 필요가 있습니다."

    return "과매도권에 가까워 기술적 반등 가능성을 함께 살펴볼 구간입니다."


def volume_comment(ratio):

    if pd.isna(ratio):
        return "거래량 데이터를 확인할 수 없습니다."

    if ratio >= 2:
        return "평균보다 거래가 크게 증가해 현재 움직임에 시장 참여가 강하게 붙고 있습니다."

    if ratio >= 1.2:
        return "평균보다 거래량이 증가해 현재 방향의 신뢰도를 살펴볼 수 있습니다."

    if ratio >= 0.8:
        return "평균 수준의 거래량입니다. 방향성이 강하게 확인된 상태는 아닙니다."

    return "거래량이 평균보다 적어 강한 추세 확인에는 시간이 필요합니다."


def trend_comment(
    price,
    ma20,
    ma60,
):

    if pd.isna(ma20) or pd.isna(ma60):

        return "이동평균 데이터가 부족합니다."

    if price > ma20 > ma60:

        return "현재가가 MA20과 MA60 위에 있고 단기 평균도 중기 평균보다 높아 상승 구조가 유지되고 있습니다."

    if price > ma60 and price < ma20:

        return "중기 추세는 아직 유지되지만 단기적으로 MA20 아래에 있어 눌림 구간인지 확인이 필요합니다."

    if price < ma20 < ma60:

        return "현재가와 이동평균 구조가 모두 약해져 추세 회복 여부를 먼저 확인하는 구간입니다."

    return "이동평균 구조가 혼재되어 방향성을 추가 확인할 필요가 있습니다."


def macd_comment(
    macd,
    signal,
):

    if pd.isna(macd) or pd.isna(signal):

        return "MACD 데이터를 확인할 수 없습니다."

    if macd > signal:

        return "MACD가 Signal 위에 있어 단기 모멘텀은 긍정적입니다."

    return "MACD가 Signal 아래에 있어 단기 모멘텀이 약해지고 있습니다."


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

    price = float(
        latest["Close"]
    )

    support, resistance = (
        calculate_support_resistance(df)
    )

    zones = calculate_price_zones(
        df
    )

    profit = (
        price -
        average_price
    ) * shares

    profit_pct = (
        (
            price /
            average_price
        ) - 1
    ) * 100

    ma20 = latest["MA20"]
    ma60 = latest["MA60"]
    rsi = latest["RSI14"]
    macd = latest["MACD"]
    signal = latest["MACD_SIGNAL"]

    if (
        price < ma20
        and ma20 < ma60
    ):

        action = "리스크 재검토"

        explanation = (
            "현재가가 MA20 아래로 내려가고 중기 이동평균도 약해지고 있습니다. "
            "추가매수보다 추세 회복 여부를 먼저 확인하는 시나리오입니다."
        )

    elif (
        pd.notna(resistance)
        and price >= resistance * 0.97
        and pd.notna(rsi)
        and rsi >= 68
    ):

        action = "일부 이익실현 검토"

        explanation = (
            "최근 저항권에 접근했고 RSI도 높은 수준입니다. "
            "추가 상승 가능성을 열어두되 일부 이익실현을 검토할 수 있는 가격대입니다."
        )

    elif (
        pd.notna(ma20)
        and abs(price - ma20)
        / ma20
        <= 0.035
        and pd.notna(rsi)
        and 42 <= rsi <= 67
        and price > ma60
    ):

        action = "추가매수 검토"

        explanation = (
            "중기 추세가 유지되는 가운데 MA20 부근까지 조정된 상태입니다. "
            "1차 가격대에서 일부 접근하고 MA60 부근을 2차 확인 구간으로 볼 수 있습니다."
        )

    else:

        action = "보유 유지 검토"

        explanation = (
            "현재 추세가 크게 훼손되지 않았습니다. "
            "MA20 위에서 움직이는 동안 보유를 유지하고, "
            "MA20 이탈 후 MA60까지 약해지는지를 확인하는 시나리오입니다."
        )

    return {
        "price": price,
        "profit": profit,
        "profit_pct": profit_pct,
        "action": action,
        "explanation": explanation,
        "support": support,
        "resistance": resistance,
        "zones": zones,
    }


# ============================================================
# FORMAT
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


def fmt_range(
    low,
    high,
):

    if pd.isna(low) or pd.isna(high):
        return "-"

    return (
        f"{low:,.0f} ~ "
        f"{high:,.0f}원"
    )


# ============================================================
# SEARCH
# ============================================================

def search_etfs(
    keyword,
):

    keyword = (
        keyword
        .strip()
        .lower()
    )

    if not keyword:

        return {}

    results = {}

    # ETF 검색
    for code, name in ETF_UNIVERSE.items():

        if (
            keyword in code.lower()
            or keyword in name.lower()
        ):

            results[code] = name

    # 테마 검색
    for theme_name, info in THEMES.items():

        theme_words = [
            theme_name
        ] + info.get(
            "keywords",
            [],
        )

        theme_match = any(
            keyword in word.lower()
            or word.lower() in keyword
            for word in theme_words
        )

        if theme_match:

            for code in info["etfs"]:

                if code in ETF_UNIVERSE:

                    results[code] = (
                        ETF_UNIVERSE[code]
                    )

    return results


# ============================================================
# CHART
# ============================================================

def draw_chart(
    df,
    period,
):

    if df.empty:

        st.warning(
            "차트 데이터가 없습니다."
        )

        return

    period_days = {
        "1M": 22,
        "3M": 66,
        "6M": 132,
        "1Y": 252,
    }

    days = period_days.get(
        period,
        66,
    )

    chart_df = (
        df.tail(days)
        .copy()
    )

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[
            0.78,
            0.22,
        ],
        vertical_spacing=0.04,
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["Close"],
            name="가격",
            mode="lines",
            line=dict(
                width=2
            ),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA20"],
            name="MA20",
            mode="lines",
            line=dict(
                width=1.5
            ),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA60"],
            name="MA60",
            mode="lines",
            line=dict(
                width=1.5
            ),
        ),
        row=1,
        col=1,
    )

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
# PRICE SCENARIO
# ============================================================

def render_price_scenario(
    df,
    judgment,
):

    latest = df.iloc[-1]

    price = latest["Close"]

    zones = calculate_price_zones(
        df
    )

    st.markdown(
        "### 가격 대응 구간"
    )

    st.caption(
        "이 가격대는 MA20·MA60·최근 고점/저점을 이용한 기술적 참고 구간입니다."
    )

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "현재가",
            fmt_price(price),
        )

    with c2:

        st.metric(
            "최근 저항",
            fmt_price(
                zones.get(
                    "resistance"
                )
            ),
        )

    c3, c4 = st.columns(2)

    with c3:

        st.metric(
            "1차 접근",
            fmt_range(
                zones.get(
                    "primary_low",
                    np.nan,
                ),
                zones.get(
                    "primary_high",
                    np.nan,
                ),
            ),
        )

    with c4:

        st.metric(
            "2차 접근",
            fmt_range(
                zones.get(
                    "secondary_low",
                    np.nan,
                ),
                zones.get(
                    "secondary_high",
                    np.nan,
                ),
            ),
        )

    if judgment["label"] == "매수 검토":

        st.success(
            "현재는 1차 접근 가격대가 핵심입니다. "
            "1차 구간에서 한 번에 접근하기보다 분할 접근하고, "
            "MA20이 유지되는지를 확인하는 시나리오입니다."
        )

    elif judgment["label"] == "눌림목 대기":

        st.warning(
            "현재가는 단기적으로 올라온 상태입니다. "
            "지금 추격하기보다 1차 접근 구간까지 내려오는지 확인하고, "
            "추가 조정 시 2차 접근 구간을 확인하는 방식입니다."
        )

    elif judgment["label"] == "보유 유지":

        st.info(
            "현재 추세가 유지되는 동안에는 보유를 유지하는 시나리오입니다. "
            "MA20 부근 조정 시 1차 대응, MA60 부근까지 내려오면 "
            "중기 추세 훼손 여부를 다시 확인합니다."
        )

    elif judgment["label"] == "리스크 재검토":

        st.error(
            "현재는 가격을 낮춰 매수하기보다 추세 회복 여부를 먼저 확인하는 구간입니다. "
            "MA20 회복 → MA60 회복 순서가 중요합니다."
        )

    else:

        st.info(
            "현재는 방향성이 명확하지 않습니다. "
            "1차 접근 가격대에서 지지가 확인되거나 "
            "저항을 돌파한 뒤 안착하는지를 확인하는 시나리오입니다."
        )


# ============================================================
# ETF DETAIL
# ============================================================

def render_etf_detail(
    code,
    name,
):

    with st.spinner(
        "ETF 데이터를 불러오는 중입니다..."
    ):

        df = load_price_data(
            code
        )

    if df.empty:

        st.error(
            "가격 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해주세요."
        )

        return

    df = calculate_indicators(
        df
    )

    latest = df.iloc[-1]

    price = float(
        latest["Close"]
    )

    previous = (
        df["Close"].iloc[-2]
        if len(df) >= 2
        else np.nan
    )

    if (
        pd.notna(previous)
        and previous != 0
    ):

        daily_change = (
            price / previous - 1
        ) * 100

    else:

        daily_change = np.nan

    judgment = get_judgment(
        df
    )

    st.subheader(
        name
    )

    st.caption(
        f"{code} · 최근 데이터 {df.index[-1].strftime('%Y-%m-%d')}"
    )

    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    p1, p2 = st.columns(2)

    with p1:

        st.metric(
            "현재가",
            fmt_price(price),
            fmt_pct(daily_change),
        )

    with p2:

        st.metric(
            "20일 수익률",
            fmt_pct(
                latest["RET20"]
            ),
            f"60일 {fmt_pct(latest['RET60'])}",
        )

    # --------------------------------------------------------
    # JUDGMENT
    # --------------------------------------------------------

    st.markdown(
        "### 🎯 지금의 판단"
    )

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

    st.markdown(
        "### 🔍 왜 이렇게 판단했나?"
    )

    trend_text = trend_comment(
        price,
        latest["MA20"],
        latest["MA60"],
    )

    rsi_text = rsi_comment(
        latest["RSI14"]
    )

    volume_text = volume_comment(
        latest["VOLUME_RATIO"]
    )

    macd_text = macd_comment(
        latest["MACD"],
        latest["MACD_SIGNAL"],
    )

    e1, e2 = st.columns(2)

    with e1:

        st.metric(
            "추세",
            judgment["trend"],
        )

        st.caption(
            trend_text
        )

    with e2:

        st.metric(
            "RSI",
            (
                f"{latest['RSI14']:.1f}"
                if pd.notna(
                    latest["RSI14"]
                )
                else "-"
            ),
        )

        st.caption(
            rsi_text
        )

    e3, e4 = st.columns(2)

    with e3:

        st.metric(
            "거래량",
            fmt_ratio(
                latest["VOLUME_RATIO"]
            ),
        )

        st.caption(
            volume_text
        )

    with e4:

        st.metric(
            "MACD",
            (
                "긍정"
                if latest["MACD"]
                > latest["MACD_SIGNAL"]
                else "약화"
            ),
        )

        st.caption(
            macd_text
        )

    # --------------------------------------------------------
    # MA
    # --------------------------------------------------------

    ma1, ma2 = st.columns(2)

    with ma1:

        st.metric(
            "MA20",
            fmt_price(
                latest["MA20"]
            ),
        )

    with ma2:

        st.metric(
            "MA60",
            fmt_price(
                latest["MA60"]
            ),
        )

    # --------------------------------------------------------
    # PRICE SCENARIO
    # --------------------------------------------------------

    render_price_scenario(
        df,
        judgment,
    )

    # --------------------------------------------------------
    # HOLDING
    # --------------------------------------------------------

    st.markdown(
        "### 💼 보유 중이라면"
    )

    holding = st.radio(
        "현재 보유 여부",
        [
            "보유하지 않음",
            "보유 중",
        ],
        horizontal=True,
        key=f"holding_{code}",
    )

    if holding == "보유 중":

        h1, h2 = st.columns(2)

        with h1:

            average_price = st.number_input(
                "평균 매수가",
                min_value=0.0,
                value=float(price),
                step=100.0,
                key=f"avg_{code}",
            )

        with h2:

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

            st.markdown(
                "#### 현재 포지션"
            )

            h3, h4, h5 = st.columns(3)

            with h3:

                st.metric(
                    "평가손익",
                    f"{scenario['profit']:+,.0f}원",
                )

            with h4:

                st.metric(
                    "수익률",
                    f"{scenario['profit_pct']:+.2f}%",
                )

            with h5:

                st.metric(
                    "현재가",
                    fmt_price(
                        scenario["price"]
                    ),
                )

            st.markdown(
                "#### 대응 시나리오"
            )

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

            zones = scenario["zones"]

            z1, z2, z3 = st.columns(3)

            with z1:

                st.metric(
                    "1차 가격대",
                    fmt_range(
                        zones.get(
                            "primary_low",
                            np.nan,
                        ),
                        zones.get(
                            "primary_high",
                            np.nan,
                        ),
                    ),
                )

            with z2:

                st.metric(
                    "2차 가격대",
                    fmt_range(
                        zones.get(
                            "secondary_low",
                            np.nan,
                        ),
                        zones.get(
                            "secondary_high",
                            np.nan,
                        ),
                    ),
                )

            with z3:

                st.metric(
                    "저항 가격대",
                    fmt_range(
                        zones.get(
                            "resistance_low",
                            np.nan,
                        ),
                        zones.get(
                            "resistance_high",
                            np.nan,
                        ),
                    ),
                )

    else:

        st.info(
            "보유하지 않은 경우에는 현재가를 추격하기보다 "
            "1차 접근 가격대에서 지지가 확인되는지 보고, "
            "더 깊은 조정이 발생하면 2차 가격대를 확인하는 방식으로 접근할 수 있습니다."
        )

    # --------------------------------------------------------
    # CHART
    # --------------------------------------------------------

    st.markdown(
        "### 📈 가격 흐름"
    )

    period = st.radio(
        "기간",
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
    # FINAL SUMMARY
    # --------------------------------------------------------

    st.markdown(
        "### 한 줄 정리"
    )

    if judgment["label"] == "매수 검토":

        st.success(
            "상승 추세 안에서 눌림이 확인되는지가 핵심입니다. "
            "현재가 추격보다 1차 가격대의 반응을 확인하세요."
        )

    elif judgment["label"] == "눌림목 대기":

        st.warning(
            "방향은 좋지만 가격이 앞서 있습니다. "
            "MA20 부근 조정을 기다리는 쪽이 핵심입니다."
        )

    elif judgment["label"] == "보유 유지":

        st.success(
            "추세는 유지되고 있습니다. "
            "MA20 이탈 후 MA60까지 약해지는지만 집중해서 보시면 됩니다."
        )

    elif judgment["label"] == "리스크 재검토":

        st.error(
            "지금은 가격보다 추세 회복 여부가 중요합니다. "
            "MA20 → MA60 회복 순서를 확인하세요."
        )

    else:

        st.info(
            "현재 방향성이 명확하지 않습니다. "
            "가격대와 이동평균 방향을 함께 확인하세요."
        )


# ============================================================
# SEARCH UI
# ============================================================

def render_search():

    st.markdown(
        "### 🔎 ETF 찾기"
    )

    st.caption(
        "ETF 이름·종목코드뿐 아니라 AI·전력·반도체·로봇·2차전지 같은 테마명도 검색할 수 있습니다."
    )

    with st.form(
        "etf_search_form",
        clear_on_submit=False,
    ):

        query = st.text_input(
            "검색어",
            value=st.session_state.search_query,
            placeholder="예: AI 반도체 / 전력 / 나스닥 / 395160",
        )

        submitted = st.form_submit_button(
            "🔎 검색",
            type="primary",
            use_container_width=True,
        )

    if submitted:

        st.session_state.search_query = (
            query.strip()
        )

        st.session_state.search_results = (
            search_etfs(
                query
            )
        )

        st.session_state.search_selected_code = None

    results = (
        st.session_state.search_results
    )

    if not results:

        if st.session_state.search_query:

            st.warning(
                f"'{st.session_state.search_query}'에 해당하는 ETF를 찾지 못했습니다."
            )

        return

    st.markdown(
        f"**검색 결과 {len(results)}개**"
    )

    result_codes = list(
        results.keys()
    )

    result_labels = [
        f"{code} · {results[code]}"
        for code in result_codes
    ]

    selected_label = st.selectbox(
        "분석할 ETF",
        result_labels,
        key="search_result_select",
    )

    selected_code = result_codes[
        result_labels.index(
            selected_label
        )
    ]

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "📊 이 ETF 분석하기",
            type="primary",
            use_container_width=True,
        ):

            st.session_state.selected_code = (
                selected_code
            )

            st.success(
                f"{ETF_UNIVERSE[selected_code]}를 분석합니다."
            )

            st.rerun()

    with c2:

        if st.button(
            "⭐ 관심 ETF 추가",
            use_container_width=True,
        ):

            watchlist = load_watchlist()

            if selected_code not in watchlist:

                watchlist.append(
                    selected_code
                )

                save_watchlist(
                    watchlist
                )

                st.success(
                    "관심 ETF에 추가했습니다."
                )

            else:

                st.info(
                    "이미 관심 ETF에 있습니다."
                )


# ============================================================
# WATCHLIST UI
# ============================================================

def render_watchlist_selector():

    watchlist = load_watchlist()

    st.markdown(
        "### ⭐ 내 ETF"
    )

    if not watchlist:

        st.info(
            "관심 ETF가 없습니다."
        )

        return

    labels = [
        f"{code} · {ETF_UNIVERSE.get(code, code)}"
        for code in watchlist
    ]

    current_code = (
        st.session_state.selected_code
    )

    if current_code in watchlist:

        current_index = (
            watchlist.index(
                current_code
            )
        )

    else:

        current_index = 0

        st.session_state.selected_code = (
            watchlist[0]
        )

    selected_label = st.selectbox(
        "내 ETF 선택",
        labels,
        index=current_index,
        key="watchlist_select",
    )

    selected_code = watchlist[
        labels.index(
            selected_label
        )
    ]

    st.session_state.selected_code = (
        selected_code
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "📊 분석",
            use_container_width=True,
        ):

            st.session_state.selected_code = (
                selected_code
            )

            st.rerun()

    with c2:

        if st.button(
            "🗑 관심종목 삭제",
            use_container_width=True,
        ):

            watchlist.remove(
                selected_code
            )

            save_watchlist(
                watchlist
            )

            if watchlist:

                st.session_state.selected_code = (
                    watchlist[0]
                )

            st.rerun()


# ============================================================
# MY ETF
# ============================================================

def render_my_etf():

    st.title(
        "📊 ETF RADAR"
    )

    st.caption(
        "내 ETF의 현재 위치와 대응 가격대를 한눈에 확인합니다."
    )

    render_search()

    st.divider()

    render_watchlist_selector()

    st.divider()

    code = (
        st.session_state.selected_code
    )

    name = ETF_UNIVERSE.get(
        code,
        code,
    )

    render_etf_detail(
        code,
        name,
    )


# ============================================================
# THEME ETF ANALYSIS
# ============================================================

def theme_etf_summary(
    code,
):

    df = load_price_data(
        code
    )

    if df.empty:
        return None

    df = calculate_indicators(
        df
    )

    latest = df.iloc[-1]

    judgment = get_judgment(
        df
    )

    return {
        "code": code,
        "name": ETF_UNIVERSE.get(
            code,
            code,
        ),
        "price": latest["Close"],
        "ret20": latest["RET20"],
        "rsi": latest["RSI14"],
        "judgment": judgment["label"],
        "trend": judgment["trend"],
    }


# ============================================================
# FUTURE THEME
# ============================================================

def render_future_theme():

    st.title(
        "🚀 미래테마"
    )

    st.caption(
        "현재 주도 → 후속 수혜 → 선행 관심 순서로 다음 투자 후보군을 살펴봅니다."
    )

    st.info(
        "테마 단계는 미래를 확정적으로 예측하는 신호가 아니라 "
        "ETF를 조사하기 위한 연구용 분류입니다."
    )

    # --------------------------------------------------------
    # THEME FLOW
    # --------------------------------------------------------

    st.markdown(
        "### 🔄 테마 흐름"
    )

    flow_cols = st.columns(
        len(THEME_CHAIN)
    )

    for i, (
        theme,
        label,
    ) in enumerate(
        THEME_CHAIN
    ):

        with flow_cols[i]:

            st.caption(
                label
            )

            st.write(
                f"**{theme}**"
            )

    st.divider()

    # --------------------------------------------------------
    # CURRENT LEADER
    # --------------------------------------------------------

    st.markdown(
        "### 🔥 현재 주도"
    )

    leader_themes = [
        (
            name,
            info,
        )
        for name, info in THEMES.items()
        if info["stage"] == "LEADER"
    ]

    for theme_name, info in leader_themes:

        st.success(
            f"**{theme_name}**\n\n"
            f"{info['description']}"
        )

        for code in info["etfs"]:

            result = theme_etf_summary(
                code
            )

            if result:

                c1, c2, c3 = st.columns(3)

                with c1:

                    st.write(
                        f"**{result['name']}**"
                    )

                    st.caption(
                        result["code"]
                    )

                with c2:

                    st.metric(
                        "20일",
                        fmt_pct(
                            result["ret20"]
                        ),
                    )

                with c3:

                    st.metric(
                        "판단",
                        result["judgment"],
                    )

    # --------------------------------------------------------
    # FOLLOWERS
    # --------------------------------------------------------

    st.markdown(
        "### ➡️ 후속 수혜"
    )

    follower_themes = [
        (
            name,
            info,
        )
        for name, info in THEMES.items()
        if info["stage"] == "FOLLOWER"
    ]

    for theme_name, info in follower_themes:

        with st.container():

            st.subheader(
                theme_name
            )

            st.info(
                info["description"]
            )

            for code in info["etfs"]:

                result = theme_etf_summary(
                    code
                )

                if result:

                    c1, c2, c3 = st.columns(3)

                    with c1:

                        st.write(
                            f"**{result['name']}**"
                        )

                    with c2:

                        st.metric(
                            "20일",
                            fmt_pct(
                                result["ret20"]
                            ),
                        )

                    with c3:

                        st.metric(
                            "상태",
                            result["judgment"],
                        )

    # --------------------------------------------------------
    # EARLY
    # --------------------------------------------------------

    st.markdown(
        "### 💎 선행 관심 / 원석"
    )

    early_themes = [
        (
            name,
            info,
        )
        for name, info in THEMES.items()
        if info["stage"] == "EARLY"
    ]

    for theme_name, info in early_themes:

        st.warning(
            f"**{theme_name}**\n\n"
            f"{info['description']}"
        )

        if info["etfs"]:

            for code in info["etfs"]:

                result = theme_etf_summary(
                    code
                )

                if result:

                    c1, c2, c3 = st.columns(3)

                    with c1:

                        st.write(
                            f"**{result['name']}**"
                        )

                    with c2:

                        st.metric(
                            "20일",
                            fmt_pct(
                                result["ret20"]
                            ),
                        )

                    with c3:

                        st.metric(
                            "판단",
                            result["judgment"],
                        )

        else:

            st.caption(
                "현재 등록된 국내 ETF 중 이 테마를 직접 추종하는 전용 ETF가 없습니다."
            )

    # --------------------------------------------------------
    # WATCH
    # --------------------------------------------------------

    st.markdown(
        "### 👀 관찰 테마"
    )

    watch_themes = [
        (
            name,
            info,
        )
        for name, info in THEMES.items()
        if info["stage"] == "WATCH"
    ]

    for theme_name, info in watch_themes:

        st.info(
            f"**{theme_name}** · {info['description']}"
        )

        names = [
            ETF_UNIVERSE.get(
                code,
                code,
            )
            for code in info["etfs"]
        ]

        if names:

            st.write(
                " · ".join(names)
            )

    # --------------------------------------------------------
    # HOW TO USE
    # --------------------------------------------------------

    st.markdown(
        "### 📌 미래테마 활용법"
    )

    st.write(
        "① 현재 주도 테마의 추세가 유지되는지 확인"
    )

    st.write(
        "② 그 다음 단계의 후속 수혜 테마를 미리 관찰"
    )

    st.write(
        "③ 선행 관심 테마는 가격보다 거래량과 추세 전환을 먼저 확인"
    )

    st.write(
        "④ 실제 매수는 미래테마 판단보다 개별 ETF의 가격 구간과 추세를 함께 확인"
    )


# ============================================================
# MAIN NAVIGATION
# ============================================================

st.divider()

nav = st.radio(
    "메인 메뉴",
    [
        "📌 내 ETF",
        "🚀 미래테마",
    ],
    index=(
        0
        if st.session_state.page == "내 ETF"
        else 1
    ),
    horizontal=True,
    label_visibility="collapsed",
)

if nav == "📌 내 ETF":

    st.session_state.page = "내 ETF"

    render_my_etf()

else:

    st.session_state.page = "미래테마"

    render_future_theme()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ETF RADAR · 시장 데이터 기반 리서치 보조 도구 · 최종 투자 판단은 사용자가 결정"
)