# -*- coding: utf-8 -*-

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
from datetime import datetime


# ============================================================
# ETF RADAR
# 최종 통합 버전
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# FILES
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"
UNIVERSE_FILE = "etf_universe_cache.json"


# ============================================================
# ETF DATA
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
    "305720": "KODEX 2차전지산업",

    "449170": "TIGER 글로벌AI인프라액티브",
    "434060": "TIGER 글로벌AI&반도체액티브",

    "464240": "KODEX AI전력핵심설비",
    "487130": "KODEX AI전력인프라",

    "475050": "ACE 글로벌반도체TOP4 Plus",
    "469150": "ACE AI반도체포커스",
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
# THEMES
# ============================================================

THEMES = {

    "AI 반도체": {
        "keywords": [
            "AI반도체",
            "반도체",
            "AI",
            "HBM",
            "반도체장비",
        ],
        "seeds": [
            "395160",
            "487240",
            "471990",
            "396500",
        ],
        "reason":
            "AI 연산 확대와 첨단 반도체 투자 증가의 직접적인 수혜 영역입니다.",
    },

    "데이터센터·AI 인프라": {
        "keywords": [
            "데이터센터",
            "AI인프라",
            "AI 인프라",
            "글로벌AI인프라",
        ],
        "seeds": [
            "449170",
            "434060",
            "381170",
        ],
        "reason":
            "AI 서비스 확산에 따라 서버·네트워크·데이터센터 투자를 추적합니다.",
    },

    "전력 인프라": {
        "keywords": [
            "전력",
            "전력인프라",
            "전력핵심설비",
            "전력설비",
        ],
        "seeds": [
            "464240",
            "487130",
        ],
        "reason":
            "데이터센터와 산업용 전력수요 증가에 따른 전력망 투자를 추적합니다.",
    },

    "원자력": {
        "keywords": [
            "원자력",
            "원전",
        ],
        "seeds": [],
        "reason":
            "전력수요와 에너지 믹스 변화에 따른 원전 관련 흐름을 추적합니다.",
    },

    "냉각·열관리": {
        "keywords": [
            "냉각",
            "열관리",
            "액침냉각",
        ],
        "seeds": [
            "434060",
            "449170",
        ],
        "reason":
            "AI 서버 고집적화에 따른 냉각·열관리 후방 수혜를 추적합니다.",
    },
}


FUTURE_CHAIN = [
    ("AI 반도체", "현재 주도"),
    ("데이터센터·AI 인프라", "다음 수혜"),
    ("전력 인프라", "다음 수혜"),
    ("원자력", "관심 확대"),
    ("냉각·열관리", "초기 관심"),
]


# ============================================================
# GLOBAL STYLE
# ============================================================

st.markdown(
    """
<style>

:root{
    --bg:#171817;
    --panel:#232623;
    --panel2:#2b2e2b;
    --panel3:#323632;
    --line:#4b514b;

    --text:#f5f3ed;
    --sub:#d9ddd7;
    --muted:#c8cdc6;

    --mint:#65d7b5;
    --coral:#f0786d;
    --amber:#e6bb63;
}


/* ============================================================
   APP
============================================================ */

html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stHeader"],
[data-testid="stDecoration"]{

    background:var(--bg)!important;
    color:var(--text)!important;
}


.block-container{

    max-width:1180px!important;

    padding:
        12px
        12px
        32px!important;
}


[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="column"],
[data-testid="stColumn"],
.element-container{

    background:transparent!important;
    color:var(--text)!important;
}


body{

    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Noto Sans KR",
        sans-serif;
}


/* ============================================================
   TEXT
============================================================ */

h1,
h2,
h3,
h4,
h5,
h6,
p,
span,
label,
div{

    color:inherit;
}


[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] *{

    color:var(--sub)!important;

    font-size:.88rem!important;

    line-height:1.45!important;
}


/* ============================================================
   BUTTON
============================================================ */

.stButton > button{

    background:#303430!important;

    color:#f5f1e8!important;

    border:
        1px solid
        #4b514b!important;

    border-radius:8px!important;

    font-weight:800!important;

    min-height:38px;
}


.stButton > button:hover{

    background:#3a3f3a!important;

    border-color:
        var(--mint)!important;

    color:#ffffff!important;
}


/* ============================================================
   INPUT
============================================================ */

div[data-baseweb="input"],
div[data-baseweb="input"] > div,
div[data-baseweb="select"],
div[data-baseweb="select"] > div{

    background:#292c29!important;

    color:#f5f1e8!important;

    border-color:#4a504a!important;
}


input{

    background:#292c29!important;

    color:#f5f1e8!important;

    -webkit-text-fill-color:#f5f1e8!important;
}


input::placeholder{

    color:#b8beb7!important;

    -webkit-text-fill-color:#b8beb7!important;
}


div[data-baseweb="select"] span{

    color:#f5f1e8!important;
}


/* ============================================================
   DROPDOWN
============================================================ */

ul[role="listbox"],
div[role="listbox"],
li[role="option"]{

    background:#292c29!important;

    color:#f5f1e8!important;
}


li[role="option"]:hover{

    background:#3a3f3a!important;
}


/* ============================================================
   RADIO
============================================================ */

[data-testid="stRadio"]
[role="radiogroup"]{

    background:#242724!important;

    border:
        1px solid
        var(--line)!important;

    border-radius:9px!important;

    padding:
        4px
        8px!important;
}


/* ============================================================
   ALERT
============================================================ */

[data-testid="stAlert"],
[data-testid="stNotification"]{

    background:#292c29!important;

    color:#eeeae0!important;

    border:
        1px solid
        #454b45!important;
}


/* ============================================================
   METRIC
============================================================ */

[data-testid="stMetric"]{

    background:#242724!important;

    border:
        1px solid
        var(--line)!important;

    border-radius:10px!important;

    padding:
        .55rem
        .65rem!important;
}


[data-testid="stMetricLabel"]{

    color:var(--sub)!important;

    font-size:.76rem!important;
}


[data-testid="stMetricValue"]{

    color:var(--text)!important;

    font-size:1.08rem!important;
}


[data-testid="stMetricDelta"]{

    font-size:.72rem!important;
}


/* ============================================================
   EXPANDER
============================================================ */

[data-testid="stExpander"]{

    background:#242724!important;

    border:
        1px solid
        var(--line)!important;

    border-radius:9px!important;
}


[data-testid="stExpander"] summary{

    background:#242724!important;

    color:#eeeae0!important;
}


/* ============================================================
   TABS
============================================================ */

button[data-baseweb="tab"]{

    background:transparent!important;

    color:var(--sub)!important;
}


.stTabs [aria-selected="true"]{

    color:var(--mint)!important;
}


/* ============================================================
   PLOTLY
============================================================ */

.js-plotly-plot,
.plot-container,
.svg-container{

    background:#242724!important;

    border-radius:10px!important;

    touch-action:pan-y!important;
}


/* ============================================================
   DIVIDER
============================================================ */

hr{

    border-color:#383d38!important;
}


/* ============================================================
   MOBILE
============================================================ */

@media(max-width:700px){

    .block-container{

        padding:
            8px
            9px
            24px!important;
    }

    .stButton > button{

        min-height:36px;
    }

    .stMarkdown h1{

        font-size:1.55rem;
    }

    .stMarkdown h2{

        font-size:1.28rem;
    }

    .stMarkdown h3{

        font-size:1.02rem;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# JSON
# ============================================================

def read_json(
    path,
    default
):

    try:

        if not os.path.exists(path):

            return default

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)

    except Exception:

        return default


def write_json(
    path,
    data
):

    try:

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
            )

        return True

    except Exception:

        return False


# ============================================================
# SESSION STATE
# ============================================================

def init_state():

    if "watchlist" not in st.session_state:

        watchlist = read_json(
            WATCHLIST_FILE,
            DEFAULT_WATCHLIST.copy(),
        )

        if isinstance(
            watchlist,
            list,
        ):

            st.session_state.watchlist = [
                str(x).zfill(6)
                for x in watchlist
            ]

        else:

            st.session_state.watchlist = (
                DEFAULT_WATCHLIST.copy()
            )


    if "holdings" not in st.session_state:

        st.session_state.holdings = read_json(
            HOLDINGS_FILE,
            {},
        )


    if "etf_universe" not in st.session_state:

        universe = dict(BASE_ETFS)

        cached = read_json(
            UNIVERSE_FILE,
            {},
        )

        if isinstance(
            cached,
            dict,
        ):

            universe.update(
                {
                    str(k).zfill(6): str(v)
                    for k, v
                    in cached.items()
                    if v
                }
            )

        st.session_state.etf_universe = (
            universe
        )


    if "price_cache" not in st.session_state:

        st.session_state.price_cache = {}


    if "theme_cache" not in st.session_state:

        st.session_state.theme_cache = {}


    if "selected_code" not in st.session_state:

        st.session_state.selected_code = (
            st.session_state.watchlist[0]
            if st.session_state.watchlist
            else list(BASE_ETFS)[0]
        )


    if "main_page" not in st.session_state:

        st.session_state.main_page = (
            "📊 내 ETF"
        )


    if "theme_detail_code" not in st.session_state:

        st.session_state.theme_detail_code = None


    if "finder_query" not in st.session_state:

        st.session_state.finder_query = ""


    if "notice" not in st.session_state:

        st.session_state.notice = None


# ============================================================
# UTILITIES
# ============================================================

def name_of(code):

    code = str(code).zfill(6)

    return st.session_state.etf_universe.get(
        code,
        BASE_ETFS.get(
            code,
            f"ETF {code}",
        ),
    )


def sf(
    value,
    default=0.0
):

    try:

        return (
            default
            if pd.isna(value)
            else float(value)
        )

    except Exception:

        return default


def money(value):

    return f"{sf(value):,.0f}원"


# ============================================================
# PRICE NORMALIZATION
# ============================================================

def normalize(df):

    if df is None or df.empty:

        return pd.DataFrame()


    x = df.copy()


    if isinstance(
        x.columns,
        pd.MultiIndex,
    ):

        x.columns = [
            c[0]
            if isinstance(c, tuple)
            else str(c)
            for c in x.columns
        ]


    rename = {}

    for column in x.columns:

        key = str(column).lower()

        rename[column] = {

            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",

        }.get(
            key,
            column,
        )


    x = x.rename(
        columns=rename
    )


    required = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]


    if any(
        c not in x.columns
        for c in required
    ):

        return pd.DataFrame()


    for column in required:

        x[column] = pd.to_numeric(
            x[column],
            errors="coerce",
        )


    x = x.dropna(
        subset=["Close"]
    )


    return x[required]


# ============================================================
# NAVER PRICE
# ============================================================

def fetch_naver(code):

    try:

        url = (
            "https://fchart.stock.naver.com/"
            "spevent.nhn?"
            f"symbol={str(code).zfill(6)}"
            "&timeframe=day"
            "&count=600"
            "&requestType=0"
        )


        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "Mozilla/5.0",
            },
        )


        with urllib.request.urlopen(
            request,
            timeout=7,
        ) as response:

            raw = response.read()


        root = ET.fromstring(
            raw
        )


        rows = []


        for item in root.findall(
            ".//item"
        ):

            values = item.attrib.get(
                "data",
                "",
            ).split("|")


            if len(values) >= 6:

                rows.append(
                    [
                        values[0],
                        float(values[1]),
                        float(values[2]),
                        float(values[3]),
                        float(values[4]),
                        float(values[5]),
                    ]
                )


        if not rows:

            return pd.DataFrame()


        data = pd.DataFrame(
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


        data["Date"] = pd.to_datetime(
            data["Date"]
        )


        return normalize(
            data.set_index("Date")
        )


    except Exception:

        return pd.DataFrame()


# ============================================================
# YAHOO FALLBACK
# ============================================================

def fetch_yahoo(code):

    try:

        data = yf.download(
            f"{str(code).zfill(6)}.KS",
            period="2y",
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False,
        )


        return normalize(
            data
        )


    except Exception:

        return pd.DataFrame()


# ============================================================
# PRICE LOADER
# ============================================================

def load_price(
    code,
    force=False
):

    code = str(code).zfill(6)

    now = datetime.now()

    cached = (
        st.session_state.price_cache.get(
            code
        )
    )


    if (
        cached
        and not force
        and (
            now -
            cached["time"]
        ).total_seconds() < 300
    ):

        return cached["data"]


    data = fetch_naver(
        code
    )


    if data.empty:

        data = fetch_yahoo(
            code
        )


    if not data.empty:

        st.session_state.price_cache[
            code
        ] = {
            "time": now,
            "data": data,
        }


    return data


# ============================================================
# INDICATORS
# ============================================================

def indicators(df):

    if df.empty:

        return pd.DataFrame()


    x = df.copy()


    x["MA20"] = (
        x["Close"]
        .rolling(20)
        .mean()
    )


    x["MA60"] = (
        x["Close"]
        .rolling(60)
        .mean()
    )


    delta = x["Close"].diff()


    gain = (
        delta
        .clip(lower=0)
        .rolling(14)
        .mean()
    )


    loss = (
        -delta
        .clip(upper=0)
        .rolling(14)
        .mean()
    )


    rs = (
        gain /
        loss.replace(
            0,
            np.nan,
        )
    )


    x["RSI14"] = (
        100 -
        (
            100 /
            (1 + rs)
        )
    )


    x["VOL20"] = (
        x["Volume"]
        .rolling(20)
        .mean()
    )


    x["VOL_RATIO"] = (
        x["Volume"] /
        x["VOL20"].replace(
            0,
            np.nan,
        )
    )


    x["RET20"] = (
        x["Close"]
        .pct_change(20)
        * 100
    )


    x["HIGH20"] = (
        x["High"]
        .rolling(20)
        .max()
    )


    x["LOW20"] = (
        x["Low"]
        .rolling(20)
        .min()
    )


    x["LOW60"] = (
        x["Low"]
        .rolling(60)
        .min()
    )


    return x


# ============================================================
# ANALYSIS
# ============================================================

def analyze(code):

    raw = load_price(
        code
    )


    if raw.empty:

        return None


    x = indicators(
        raw
    )


    if x.empty:

        return None


    row = x.iloc[-1]


    close = sf(
        row["Close"]
    )


    ma20 = sf(
        row["MA20"],
        close,
    )


    ma60 = sf(
        row["MA60"],
        ma20,
    )


    rsi = sf(
        row["RSI14"],
        50,
    )


    vr = sf(
        row["VOL_RATIO"],
        1,
    )


    ret20 = sf(
        row["RET20"],
        0,
    )


    high20 = sf(
        row["HIGH20"],
        close,
    )


    low20 = sf(
        row["LOW20"],
        close,
    )


    low60 = sf(
        row["LOW60"],
        low20,
    )


    # --------------------------------------------------------
    # JUDGMENT
    # --------------------------------------------------------

    if (
        close > ma20
        and close > ma60
        and rsi >= 70
    ):

        judgment = (
            "상승 추세 · 추격 주의"
        )

        action = (
            "추격보다 눌림 확인"
        )

        reason = (
            f"현재가가 MA20·MA60 위에 있어 "
            f"추세는 유지되지만 RSI {rsi:.1f}으로 "
            "단기 과열 여부를 확인해야 합니다."
        )

        action_reason = (
            "급등 구간에서는 추가 매수보다 "
            "MA20 부근 지지 확인 후 대응하는 편이 "
            "가격 리스크를 줄일 수 있습니다."
        )


    elif (
        close > ma20
        and close > ma60
    ):

        judgment = (
            "상승 추세 유지"
        )

        action = (
            "보유·눌림 접근"
        )

        reason = (
            f"현재가가 MA20·MA60 위에 있고 "
            f"20일 수익률이 {ret20:+.1f}%로 "
            "중기 추세가 유지되고 있습니다."
        )

        action_reason = (
            f"거래량이 평균의 {vr:.2f}배인 만큼 "
            "추세 지속 여부를 확인하면서 "
            "급등 추격보다 MA20 지지 여부를 "
            "우선 확인합니다."
        )


    elif (
        close < ma20
        and close > ma60
    ):

        judgment = (
            "단기 조정 · 중기 추세 확인"
        )

        action = (
            "MA60 지지 확인"
        )

        reason = (
            "현재가가 MA20 아래지만 MA60 위에 있어 "
            "단기 조정과 중기 추세가 충돌하는 구간입니다."
        )

        action_reason = (
            "MA60을 지키면서 거래량이 안정되면 "
            "재상승 가능성을 확인하고, "
            "이탈 시 대응 강도를 낮춥니다."
        )


    elif (
        close < ma60
        and rsi < 45
    ):

        judgment = (
            "중기 약세 · 방어 우선"
        )

        action = (
            "신규매수 보류"
        )

        reason = (
            f"현재가가 MA60 아래이고 "
            f"RSI {rsi:.1f}으로 모멘텀이 약해 "
            "중기 추세 회복 확인이 필요합니다."
        )

        action_reason = (
            "MA60 회복과 거래량 개선이 확인되기 전에는 "
            "신규 진입보다 추세 회복 여부를 확인합니다."
        )


    else:

        judgment = (
            "방향 확인 구간"
        )

        action = (
            "돌파·지지 확인"
        )

        reason = (
            f"현재가는 {close:,.0f}원이며 "
            "MA20/MA60과의 방향성이 뚜렷하지 않아 "
            "확인 구간입니다."
        )

        action_reason = (
            "최근 고점 돌파 또는 MA20·MA60 지지 중 "
            "어느 쪽이 확인되는지 보고 "
            "다음 대응을 결정합니다."
        )


    return {

        "df": x,

        "close": close,

        "ma20": ma20,

        "ma60": ma60,

        "rsi": rsi,

        "vr": vr,

        "ret20": ret20,

        "high20": high20,

        "low20": low20,

        "low60": low60,

        "judgment": judgment,

        "action": action,

        "reason": reason,

        "action_reason": action_reason,

        "first": ma20,

        "support": min(
            ma60,
            low20,
        ),

        "breakout": high20,

        "danger": min(
            ma60,
            low20,
            low60,
        ),
    }


# ============================================================
# IMPORTANT:
# 이전 NameError의 직접 원인이었던 함수
# ============================================================

def get_analysis(code):

    return analyze(
        code
    )


# ============================================================
# ETF CATALOG
# ============================================================

def fetch_catalog():

    url = (
        "https://finance.naver.com/"
        "api/sise/etfItemList.nhn"
    )


    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                "Mozilla/5.0",
        },
    )


    with urllib.request.urlopen(
        request,
        timeout=8,
    ) as response:

        raw = response.read().decode(
            "utf-8",
            errors="ignore",
        )


    data = json.loads(
        raw
    )


    rows = data.get(
        "result",
        {},
    ).get(
        "etfItemList",
        [],
    )


    result = {}


    for item in rows:

        code = str(
            item.get(
                "itemcode",
                "",
            )
        ).zfill(6)


        name = item.get(
            "itemname",
            "",
        )


        if code and name:

            result[code] = name


    return result


def refresh_universe():

    try:

        catalog = fetch_catalog()


        if catalog:

            universe = dict(
                st.session_state.etf_universe
            )


            universe.update(
                catalog
            )


            st.session_state.etf_universe = (
                universe
            )


            write_json(
                UNIVERSE_FILE,
                universe,
            )


            st.session_state.notice = (
                f"ETF 시장 목록 "
                f"{len(catalog):,}개를 "
                "새로 확인했습니다."
            )


            return True


    except Exception:

        pass


    st.session_state.notice = (
        "시장 목록 연결이 지연되어 "
        "기존 ETF 목록을 유지합니다."
    )


    return False


# ============================================================
# METRICS
# ============================================================

def render_metrics(a):

    cols = st.columns(
        4
    )


    values = [

        (
            "RSI14",
            f"{a['rsi']:.1f}",
        ),

        (
            "거래량",
            f"{a['vr']:.2f}배",
        ),

        (
            "20일 수익률",
            f"{a['ret20']:+.2f}%",
        ),

        (
            "MA20 / MA60",
            f"{a['ma20']:,.0f} / "
            f"{a['ma60']:,.0f}",
        ),
    ]


    for column, (
        label,
        value,
    ) in zip(
        cols,
        values,
    ):

        with column:

            st.metric(
                label,
                value,
            )


# ============================================================
# JUDGMENT
# ============================================================

def render_judgment(a):

    st.markdown(
        "### 현재판단 · 지금대응"
    )


    left, right = st.columns(
        2
    )


    with left:

        st.markdown(
            "**현재판단**"
        )

        st.subheader(
            a["judgment"]
        )

        st.markdown(
            "**판단근거**"
        )

        st.write(
            a["reason"]
        )


    with right:

        st.markdown(
            "**지금대응**"
        )

        st.subheader(
            a["action"]
        )

        st.markdown(
            "**대응근거**"
        )

        st.write(
            a["action_reason"]
        )


# ============================================================
# PRICE SCENARIOS
# ============================================================

def price_scenarios(a):

    st.markdown(
        "### 핵심가격 · 대응 시나리오"
    )


    rows = [

        (
            "1차 관심가격",
            a["first"],
            "MA20 부근",
            "눌림 시 지지 여부 확인",
        ),

        (
            "핵심 지지",
            a["support"],
            "MA60·최근 저점",
            "이탈 여부로 중기 추세 확인",
        ),

        (
            "돌파 기준",
            a["breakout"],
            "최근 20일 고점",
            "거래량 동반 돌파 여부 확인",
        ),

        (
            "위험 가격",
            a["danger"],
            "중기 방어선",
            "이탈 시 신규매수보다 방어 우선",
        ),
    ]


    cols = st.columns(
        4
    )


    for column, (
        title,
        price,
        basis,
        action,
    ) in zip(
        cols,
        rows,
    ):

        with column:

            st.metric(
                title,
                money(price),
            )

            st.caption(
                basis
            )

            st.write(
                action
            )


# ============================================================
# CHART
# ============================================================

def render_chart(a):

    data = (
        a["df"]
        .tail(130)
        .copy()
    )


    figure = make_subplots(

        rows=2,

        cols=1,

        shared_xaxes=True,

        vertical_spacing=.025,

        row_heights=[
            .78,
            .22,
        ],
    )


    figure.add_trace(

        go.Candlestick(

            x=data.index,

            open=data["Open"],

            high=data["High"],

            low=data["Low"],

            close=data["Close"],

            name="가격",

            increasing_line_color="#65d7b5",

            increasing_fillcolor="#65d7b5",

            decreasing_line_color="#f0786d",

            decreasing_fillcolor="#f0786d",
        ),

        row=1,

        col=1,
    )


    figure.add_trace(

        go.Scatter(

            x=data.index,

            y=data["MA20"],

            name="MA20",

            line=dict(

                color="#79b7d9",

                width=1.5,
            ),
        ),

        row=1,

        col=1,
    )


    figure.add_trace(

        go.Scatter(

            x=data.index,

            y=data["MA60"],

            name="MA60",

            line=dict(

                color="#e6bb63",

                width=1.4,
            ),
        ),

        row=1,

        col=1,
    )


    volume_colors = np.where(

        data["Close"]
        >= data["Open"],

        "#65d7b5",

        "#f0786d",
    )


    figure.add_trace(

        go.Bar(

            x=data.index,

            y=data["Volume"],

            marker_color=volume_colors,

            opacity=.45,

            name="거래량",

            showlegend=False,
        ),

        row=2,

        col=1,
    )


    figure.update_xaxes(

        fixedrange=True,

        showgrid=False,

        rangeslider_visible=False,
    )


    figure.update_yaxes(

        fixedrange=True,

        showgrid=True,

        gridcolor="#303530",

        zeroline=False,
    )


    figure.update_yaxes(

        fixedrange=True,

        showgrid=False,

        showticklabels=False,

        row=2,

        col=1,
    )


    figure.update_layout(

        height=410,

        margin=dict(
            l=5,
            r=5,
            t=10,
            b=5,
        ),

        paper_bgcolor="#242624",

        plot_bgcolor="#242624",

        font=dict(
            color="#eeeae0",
        ),

        dragmode=False,

        hovermode="x unified",

        legend=dict(

            orientation="h",

            y=1.02,

            x=1,

            xanchor="right",

            font=dict(
                size=10,
            ),
        ),
    )


    st.plotly_chart(

        figure,

        use_container_width=True,

        config={

            "displayModeBar": False,

            "scrollZoom": False,

            "doubleClick": False,

            "responsive": True,
        },

        key=(
            f"chart_"
            f"{a['df'].index[-1]}"
        ),
    )


    st.caption(
        "최근 6개월 기준 · "
        "확대/축소/좌우이동 없음"
    )


# ============================================================
# ETF FINDER
# ============================================================

def render_finder(
    universe
):

    st.markdown(
        "### ETF 찾기"
    )


    left, right = st.columns(
        [5, 1]
    )


    with left:

        query = st.text_input(

            "테마명 또는 ETF명",

            value=st.session_state.finder_query,

            placeholder=(
                "예: 반도체 / AI / 전력 / KODEX"
            ),

            label_visibility="collapsed",

            key="finder_input",
        )


    with right:

        if st.button(

            "시장 새로고침",

            use_container_width=True,

            key="market_refresh",
        ):

            refresh_universe()

            st.rerun()


    st.session_state.finder_query = (
        query
    )


    if st.session_state.notice:

        st.info(
            st.session_state.notice
        )

        st.session_state.notice = None


    if not query.strip():

        st.caption(
            "ETF명 또는 종목코드를 입력하면 "
            "검색 결과가 표시됩니다."
        )

        return


    q = query.strip().lower()


    result = {

        code: name

        for code, name

        in universe.items()

        if (
            q in code.lower()
            or
            q in name.lower()
        )
    }


    if not result:

        st.warning(
            "검색 결과가 없습니다."
        )

        return


    options = list(
        result.keys()
    )[:100]


    selected = st.selectbox(

        "검색 결과",

        options,

        format_func=lambda x:
            f"{result[x]} · {x}",

        key="finder_select",
    )


    if st.button(

        "선택 ETF 분석",

        use_container_width=True,

        key="finder_go",
    ):

        st.session_state.selected_code = (
            selected
        )

        st.session_state.main_page = (
            "📊 내 ETF"
        )

        st.rerun()


# ============================================================
# MY ETF
# ============================================================

def render_my_etf(
    universe
):

    st.markdown(
        "# 📊 내 ETF"
    )


    render_finder(
        universe
    )


    st.divider()


    watch = [

        str(x).zfill(6)

        for x

        in st.session_state.watchlist

        if str(x).zfill(6)
        in universe
    ]


    if not watch:

        watch = (
            DEFAULT_WATCHLIST.copy()
        )


    selected_default = (
        st.session_state.get(
            "selected_code",
            watch[0],
        )
    )


    if selected_default not in watch:

        selected_default = watch[0]


    selected = st.selectbox(

        "분석 ETF",

        watch,

        index=watch.index(
            selected_default
        ),

        format_func=lambda x:
            f"{universe.get(x,x)} · {x}",

        key="my_etf_select",
    )


    st.session_state.selected_code = (
        selected
    )


    a = get_analysis(
        selected
    )


    if a is None:

        st.error(
            "가격 데이터를 가져오지 못했습니다."
        )

        return


    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        f"## {name_of(selected)}"
    )


    st.caption(

        f"{selected} · 기준일 "

        f"{a['df'].index[-1].strftime('%Y-%m-%d')}"
    )


    pcol, dcol = st.columns(
        [1.2, 1]
    )


    prev = sf(
        a["df"].iloc[-2]["Close"],
        a["close"],
    )


    change = (
        a["close"] -
        prev
    )


    pct = (
        change /
        prev *
        100
        if prev
        else 0
    )


    with pcol:

        st.markdown(
            f"# {money(a['close'])}"
        )


    with dcol:

        if change > 0:

            st.success(
                f"{change:+,.0f}원 "
                f"({pct:+.2f}%)"
            )

        elif change < 0:

            st.error(
                f"{change:+,.0f}원 "
                f"({pct:+.2f}%)"
            )

        else:

            st.info(
                "0원 (0.00%)"
            )


    render_metrics(
        a
    )


    # --------------------------------------------------------
    # HOLDINGS
    # --------------------------------------------------------

    holdings = (
        st.session_state.holdings
    )


    h = (

        holdings.get(
            selected,
            {},
        )

        if isinstance(
            holdings,
            dict,
        )

        else {}
    )


    st.markdown(
        "### 보유상태"
    )


    status = st.radio(

        "보유 여부",

        [
            "미보유",
            "보유중",
        ],

        index=(
            1
            if h
            else 0
        ),

        horizontal=True,

        key=f"hold_status_{selected}",
    )


    if status == "보유중":

        c1, c2, c3 = st.columns(
            3
        )


        with c1:

            avg = st.number_input(

                "평균단가",

                min_value=0.0,

                value=float(
                    h.get(
                        "avg",
                        h.get(
                            "avg_price",
                            0,
                        ),
                    )
                ),

                step=100.0,

                key=f"avg_{selected}",
            )


        with c2:

            qty = st.number_input(

                "수량",

                min_value=0.0,

                value=float(
                    h.get(
                        "qty",
                        h.get(
                            "quantity",
                            0,
                        ),
                    )
                ),

                step=1.0,

                key=f"qty_{selected}",
            )


        with c3:

            st.write("")
            st.write("")


            if st.button(

                "보유정보 저장",

                use_container_width=True,

                key=f"save_{selected}",
            ):

                holdings[selected] = {

                    "avg": avg,

                    "qty": qty,
                }


                st.session_state.holdings = (
                    holdings
                )


                write_json(

                    HOLDINGS_FILE,

                    holdings,
                )


                st.success(
                    "저장했습니다."
                )


    elif selected in holdings:

        if st.button(

            "보유정보 삭제",

            key=f"del_{selected}",
        ):

            del holdings[
                selected
            ]


            write_json(
                HOLDINGS_FILE,
                holdings,
            )


            st.rerun()


    # --------------------------------------------------------
    # CORE ANALYSIS
    # --------------------------------------------------------

    render_judgment(
        a
    )


    price_scenarios(
        a
    )


    st.markdown(
        "### 가격 흐름"
    )


    render_chart(
        a
    )


# ============================================================
# FUTURE THEME CARD
# ============================================================

def render_theme_card(

    theme,

    stage,

    reason,

    codes,

    universe,

    index,
):

    st.markdown(
        f"**{stage} · {theme}**"
    )


    st.caption(
        reason
    )


    for j, code in enumerate(
        codes
    ):

        code = str(code).zfill(6)


        a = get_analysis(
            code
        )


        if a is None:

            continue


        with st.container(
            border=True
        ):

            c1, c2, c3, c4, c5 = (
                st.columns(
                    [
                        2.2,
                        1,
                        1,
                        1,
                        1.7,
                    ]
                )
            )


            with c1:

                st.markdown(
                    f"**{name_of(code)}**"
                )

                st.caption(
                    code
                )

                st.write(
                    money(
                        a["close"]
                    )
                )


            with c2:

                st.caption(
                    "RSI14"
                )

                st.write(
                    f"{a['rsi']:.1f}"
                )


            with c3:

                st.caption(
                    "거래량"
                )

                st.write(
                    f"{a['vr']:.2f}배"
                )


            with c4:

                st.caption(
                    "20일"
                )

                st.write(
                    f"{a['ret20']:+.2f}%"
                )


            with c5:

                st.caption(
                    "현재판단"
                )

                st.write(
                    a["judgment"]
                )


                if st.button(

                    "ETF 분석",

                    use_container_width=True,

                    key=(
                        f"theme_detail_"
                        f"{index}_"
                        f"{j}_"
                        f"{code}"
                    ),
                ):

                    # 중요:
                    # 미래테마 화면을 유지한다.
                    # 내 ETF로 이동시키지 않는다.

                    st.session_state.theme_detail_code = (
                        code
                    )

                    st.session_state.main_page = (
                        "🚀 미래테마"
                    )

                    st.rerun()


# ============================================================
# INLINE ETF DETAIL
# ============================================================

def render_inline_etf(

    code,

    universe,

    title="ETF 상세 분석",
):

    a = get_analysis(
        code
    )


    if a is None:

        st.error(
            "가격 데이터를 가져오지 못했습니다."
        )

        return


    st.markdown(
        "---"
    )


    st.markdown(
        f"## {title}"
    )


    st.markdown(
        f"### {name_of(code)}"
    )


    st.caption(

        f"{code} · 기준일 "

        f"{a['df'].index[-1].strftime('%Y-%m-%d')}"
    )


    pcol, dcol = st.columns(
        [1.2, 1]
    )


    prev = sf(
        a["df"].iloc[-2]["Close"],
        a["close"],
    )


    change = (
        a["close"] -
        prev
    )


    pct = (
        change /
        prev *
        100
        if prev
        else 0
    )


    with pcol:

        st.markdown(
            f"# {money(a['close'])}"
        )


    with dcol:

        if change > 0:

            st.success(
                f"{change:+,.0f}원 "
                f"({pct:+.2f}%)"
            )

        elif change < 0:

            st.error(
                f"{change:+,.0f}원 "
                f"({pct:+.2f}%)"
            )

        else:

            st.info(
                "0원 (0.00%)"
            )


    render_metrics(
        a
    )


    render_judgment(
        a
    )


    price_scenarios(
        a
    )


    with st.expander(
        "세부 지표",
        expanded=False,
    ):

        st.write(

            f"현재가 {money(a['close'])} · "

            f"MA20 {money(a['ma20'])} · "

            f"MA60 {money(a['ma60'])} · "

            f"RSI14 {a['rsi']:.1f} · "

            f"거래량/20일평균 "
            f"{a['vr']:.2f}배 · "

            f"20일 수익률 "
            f"{a['ret20']:+.2f}%"
        )


    render_chart(
        a
    )


    if st.button(

        "분석 닫기",

        use_container_width=True,

        key="close_theme_detail",
    ):

        st.session_state.theme_detail_code = (
            None
        )

        st.rerun()


# ============================================================
# FUTURE THEMES
# ============================================================

def render_future_themes(
    universe
):

    st.markdown(
        "# 🚀 미래테마"
    )


    st.caption(

        "현재 주도 → 다음 수혜 → "
        "초기 관심 순으로 ETF와 "
        "기술지표를 함께 확인합니다."
    )


    if st.button(

        "시장 데이터 다시 불러오기",

        use_container_width=True,

        key="future_refresh",
    ):

        st.session_state.price_cache = {}

        st.session_state.theme_detail_code = (
            None
        )

        refresh_universe()

        st.rerun()


    for index, (
        theme,
        stage,
    ) in enumerate(
        FUTURE_CHAIN
    ):

        info = THEMES[
            theme
        ]


        render_theme_card(

            theme,

            stage,

            info["reason"],

            info["seeds"],

            universe,

            index,
        )


        st.divider()


    # --------------------------------------------------------
    # INLINE DETAIL
    # --------------------------------------------------------

    detail = (
        st.session_state.get(
            "theme_detail_code"
        )
    )


    if detail:

        render_inline_etf(

            detail,

            universe,

            "미래테마 · ETF 분석",
        )


# ============================================================
# INIT
# ============================================================

init_state()


# ============================================================
# NAVIGATION
# 중요:
# radio widget key와 main_page를 분리한다.
# ============================================================

page = st.radio(

    "페이지",

    [
        "📊 내 ETF",
        "🚀 미래테마",
    ],

    index=(

        0
        if st.session_state.main_page
        == "📊 내 ETF"

        else 1
    ),

    horizontal=True,

    key="main_page_radio",

    label_visibility="collapsed",
)


if page != st.session_state.main_page:

    st.session_state.main_page = (
        page
    )


    if page == "📊 내 ETF":

        st.session_state.theme_detail_code = (
            None
        )


# ============================================================
# UNIVERSE
# ============================================================

universe = (
    st.session_state.etf_universe
)


# ============================================================
# PAGE
# ============================================================

if page == "📊 내 ETF":

    render_my_etf(
        universe
    )

else:

    render_future_themes(
        universe
    )