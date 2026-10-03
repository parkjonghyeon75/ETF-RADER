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

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# DARK WARM GRAPHITE THEME
# ============================================================

st.markdown(
    """
<style>
:root{
    --bg:#171817;
    --panel:#232623;
    --panel2:#2b2e2b;
    --panel3:#323632;
    --line:#424742;
    --text:#f3f0e8;
    --muted:#a4aaa2;
    --mint:#65d7b5;
    --coral:#f0786d;
    --amber:#e6bb63;
}

/* 전체 배경 */
html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main,
.block-container{
    background:var(--bg)!important;
    color:var(--text)!important;
}

[data-testid="stHeader"],
[data-testid="stDecoration"]{
    background:var(--bg)!important;
}

.block-container{
    max-width:1180px!important;
    padding:12px 12px 32px!important;
}

/* 기본 컨테이너 */
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="column"],
[data-testid="stColumn"],
.element-container{
    background:transparent!important;
    color:var(--text)!important;
}

/* 텍스트 */
h1,h2,h3,h4,h5,h6,
p,
span,
label{
    color:inherit;
}

/* 버튼 */
.stButton > button{
    background:#303430!important;
    color:#f5f1e8!important;
    border:1px solid #4b514b!important;
    border-radius:8px!important;
    font-weight:800!important;
}

.stButton > button:hover{
    background:#3a3f3a!important;
    border-color:var(--mint)!important;
    color:#ffffff!important;
}

/* 입력창 */
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
    color:#858c84!important;
    -webkit-text-fill-color:#858c84!important;
}

div[data-baseweb="select"] span{
    color:#f5f1e8!important;
}

/* 드롭다운 */
ul[role="listbox"],
div[role="listbox"],
li[role="option"]{
    background:#292c29!important;
    color:#f5f1e8!important;
}

li[role="option"]:hover{
    background:#3a3f3a!important;
}

/* 라디오 */
[data-testid="stRadio"] [role="radiogroup"]{
    background:#242724!important;
    border:1px solid var(--line)!important;
    border-radius:9px!important;
    padding:4px 8px!important;
}

/* Alert */
[data-testid="stAlert"],
[data-testid="stNotification"]{
    background:#292c29!important;
    color:#ddd9cf!important;
    border:1px solid #454b45!important;
}

/* Caption */
.stCaption,
[data-testid="stCaptionContainer"]{
    color:var(--muted)!important;
}

/* Dataframe */
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] > div{
    background:#242724!important;
    border:1px solid var(--line)!important;
}

/* Tabs */
button[data-baseweb="tab"]{
    background:transparent!important;
    color:var(--muted)!important;
}

.stTabs [data-baseweb="tab-list"]{
    background:#242724!important;
    border-bottom:1px solid var(--line)!important;
}

.stTabs [aria-selected="true"]{
    color:var(--mint)!important;
}

/* Expander */
[data-testid="stExpander"]{
    background:#242724!important;
    border:1px solid var(--line)!important;
    border-radius:9px!important;
}

[data-testid="stExpander"] summary{
    background:#242724!important;
    color:#eeeae0!important;
}

/* Plotly */
.js-plotly-plot,
.plot-container,
.svg-container{
    background:#242724!important;
    border-radius:10px!important;
    touch-action:pan-y!important;
}

hr{
    border-color:#383d38!important;
}

/* 모바일 */
@media(max-width:700px){

    .block-container{
        padding:8px 9px 24px!important;
    }

    .scenarios{
        grid-template-columns:repeat(2,1fr);
    }
}
</style>
""",
    unsafe_allow_html=True
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
# JSON
# ============================================================

def read_json(path, default):

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


def write_json(path, data):

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
# ETF UNIVERSE
# ============================================================

def load_universe():

    universe = dict(BASE_ETFS)

    cached = read_json(
        UNIVERSE_FILE,
        {},
    )

    if isinstance(cached, dict):

        for code, name in cached.items():

            if code and name:

                universe[
                    str(code).zfill(6)
                ] = str(name)

    return universe


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
        timeout=7,
    ) as response:

        raw = response.read()

    root = ET.fromstring(raw)

    result = {}

    for item in root.findall(".//item"):

        code = (
            item.attrib.get("itemcode")
            or item.attrib.get("code")
            or ""
        )

        name = (
            item.attrib.get("itemname")
            or item.attrib.get("name")
            or ""
        )

        if code and name:

            result[
                str(code).zfill(6)
            ] = name

    return result


def refresh_universe():

    try:

        external = fetch_catalog()

        if external:

            universe = dict(
                st.session_state.etf_universe
            )

            universe.update(external)

            st.session_state.etf_universe = (
                universe
            )

            write_json(
                UNIVERSE_FILE,
                universe,
            )

            st.session_state.notice = (
                f"ETF 목록을 "
                f"{len(external):,}개 확인했습니다."
            )

            return

    except Exception:

        pass

    st.session_state.notice = (
        "외부 목록 연결이 지연되어 "
        "기존 ETF 목록을 사용합니다."
    )


# ============================================================
# SESSION
# ============================================================

def init_state():

    if "watchlist" not in st.session_state:

        watchlist = read_json(
            WATCHLIST_FILE,
            DEFAULT_WATCHLIST.copy(),
        )

        if isinstance(watchlist, list):

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

        st.session_state.etf_universe = (
            load_universe()
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

    if "page_request" not in st.session_state:

        st.session_state.page_request = None

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


def sf(value, default=0.0):

    try:

        return (
            default
            if pd.isna(value)
            else float(value)
        )

    except Exception:

        return default


def money(value):

    value = sf(value)

    if abs(value) >= 1000:

        return f"{value:,.0f}원"

    return f"{value:,.2f}원"


# ============================================================
# NORMALIZE
# ============================================================

def normalize(df):

    if df is None or df.empty:

        return pd.DataFrame()

    df = df.copy()

    if isinstance(
        df.columns,
        pd.MultiIndex,
    ):

        df.columns = [
            c[0]
            if isinstance(c, tuple)
            else str(c)
            for c in df.columns
        ]

    rename = {}

    for column in df.columns:

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

    df = df.rename(
        columns=rename,
    )

    required = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    if any(
        column not in df.columns
        for column in required
    ):

        return pd.DataFrame()

    for column in required:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = df.dropna(
        subset=["Close"]
    )

    try:

        if df.index.tz is not None:

            df.index = (
                df.index.tz_localize(None)
            )

    except Exception:

        pass

    return df[required]


# ============================================================
# PRICE
# ============================================================

def fetch_naver(code):

    try:

        url = (
            "https://fchart.stock.naver.com/"
            f"spevent.nhn?"
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

        root = ET.fromstring(raw)

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

        return normalize(data)

    except Exception:

        return pd.DataFrame()


def load_price(
    code,
    force=False,
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
            now - cached["time"]
        ).total_seconds() < 300
    ):

        return cached["data"]

    data = fetch_naver(code)

    if data.empty:

        data = fetch_yahoo(code)

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

    data = df.copy()

    data["MA20"] = (
        data.Close.rolling(20).mean()
    )

    data["MA60"] = (
        data.Close.rolling(60).mean()
    )

    delta = data.Close.diff()

    gain = (
        delta.where(
            delta > 0,
            0,
        ).rolling(14).mean()
    )

    loss = (
        (-delta.where(
            delta < 0,
            0,
        )).rolling(14).mean()
    )

    rs = (
        gain /
        loss.replace(
            0,
            np.nan,
        )
    )

    data["RSI14"] = (
        100 -
        (
            100 /
            (1 + rs)
        )
    )

    data["VOL20"] = (
        data.Volume.rolling(20).mean()
    )

    data["VOL_RATIO"] = (
        data.Volume /
        data.VOL20
    )

    data["RET20"] = (
        data.Close.pct_change(20)
        * 100
    )

    data["HIGH20"] = (
        data.High.rolling(20).max()
    )

    data["LOW20"] = (
        data.Low.rolling(20).min()
    )

    data["LOW60"] = (
        data.Low.rolling(60).min()
    )

    return data


# ============================================================
# JUDGMENT
# ============================================================

def judgment(data):

    row = data.iloc[-1]

    current = sf(row.Close)
    ma20 = sf(row.MA20, current)
    ma60 = sf(row.MA60, current)
    rsi = sf(row.RSI14, 50)
    volume_ratio = sf(
        row.VOL_RATIO,
        1,
    )
    return20 = sf(
        row.RET20,
        0,
    )

    above20 = current >= ma20
    above60 = current >= ma60

    ma_state = (
        "20일선 상회"
        if above20
        else "20일선 하회"
    )

    rsi_state = (
        "과열권"
        if rsi >= 70
        else
        "강세권"
        if rsi >= 60
        else
        "중립권"
        if rsi >= 45
        else
        "약세권"
        if rsi >= 30
        else
        "과매도권"
    )

    volume_state = (
        "거래량 강한 확대"
        if volume_ratio >= 1.5
        else
        "거래량 증가"
        if volume_ratio >= 1.1
        else
        "평균 수준"
        if volume_ratio >= .8
        else
        "거래량 감소"
    )

    if (
        above20
        and above60
        and rsi >= 70
    ):

        title = "상승 추세 · 추격 주의"

        action = (
            "추세는 양호하지만 RSI가 높은 구간입니다. "
            "신규 매수는 현재가 추격보다 "
            "20일선 부근 눌림 확인을 우선합니다."
        )

    elif above20 and above60:

        title = "상승 추세 유지"

        action = (
            "20일선과 60일선 위입니다. "
            "보유자는 20일선 이탈 여부를 확인하고, "
            "미보유자는 돌파 추격보다 눌림을 기다립니다."
        )

    elif above60:

        title = "단기 조정 · 중기 추세 확인"

        action = (
            "20일선 아래 조정이지만 60일선 위라면 "
            "중기 추세 훼손 여부를 추가 확인합니다."
        )

    elif rsi <= 40:

        title = "중기 약세 · 방어 우선"

        action = (
            "60일선 아래에서 RSI도 약합니다. "
            "신규 진입보다 지지 형성과 "
            "거래량 회복을 확인합니다."
        )

    else:

        title = "방향 확인 구간"

        action = (
            "추세가 명확하지 않습니다. "
            "20일선 회복 또는 최근 고점 돌파와 "
            "거래량 동반 여부를 확인합니다."
        )

    reasons = [
        (
            f"현재가 {money(current)} · "
            f"20일선 {money(ma20)} · "
            f"{ma_state}"
        ),
        (
            f"RSI14 {rsi:.1f} · "
            f"{rsi_state}"
        ),
        (
            f"거래량 {volume_ratio:.2f}배 · "
            f"{volume_state} · "
            f"20일 수익률 {return20:+.2f}%"
        ),
    ]

    return {
        "title": title,
        "action": action,
        "ma": ma_state,
        "rs": rsi_state,
        "vs": volume_state,
        "rsi": rsi,
        "vr": volume_ratio,
        "ret": return20,
        "reasons": reasons,
    }


# ============================================================
# PRICE LEVELS
# ============================================================

def levels(data):

    row = data.iloc[-1]

    current = sf(row.Close)
    ma20 = sf(row.MA20, current)
    ma60 = sf(row.MA60, current)
    high20 = sf(row.HIGH20, current)
    low20 = sf(row.LOW20, current)
    low60 = sf(row.LOW60, current)

    return [
        (
            "1차 관심가격",
            ma20,
            "20일선 눌림 확인",
        ),
        (
            "핵심 지지",
            min(ma60, low20),
            "중기 추세 확인",
        ),
        (
            "돌파 기준",
            high20,
            "최근 20일 고점",
        ),
        (
            "위험 가격",
            min(
                ma60,
                low20,
                low60,
            ),
            "이탈 시 방어 검토",
        ),
    ]


# ============================================================
# NAVIGATION
# ============================================================

def navigate(code):

    st.session_state.selected_code = (
        str(code).zfill(6)
    )

    st.session_state.page_request = (
        "📊 내 ETF"
    )

    st.rerun()


# ============================================================
# SEARCH
# ============================================================

def search(query):

    query = (
        query or ""
    ).strip().lower()

    return [
        (code, name)
        for code, name
        in st.session_state.etf_universe.items()
        if query
        and (
            query in code.lower()
            or query in name.lower()
        )
    ][:40]


# ============================================================
# ETF FINDER
# ============================================================

def render_finder():

    st.markdown("### ETF 찾기")

    left, right = st.columns(
        [5, 1]
    )

    with left:

        query = st.text_input(
            "ETF 검색",
            placeholder="ETF명 또는 종목코드",
            label_visibility="collapsed",
            key="search_q",
        )

    with right:

        if st.button(
            "목록 갱신",
            use_container_width=True,
        ):

            refresh_universe()

            st.rerun()

    if st.session_state.notice:

        st.caption(
            st.session_state.notice
        )

        st.session_state.notice = None

    results = search(query)

    if results:

        labels = [
            f"{name} · {code}"
            for code, name
            in results
        ]

        selected = st.selectbox(
            "검색 결과",
            labels,
            label_visibility="collapsed",
            key="search_select",
        )

        code, name = results[
            labels.index(selected)
        ]

        left, right = st.columns(
            [5, 1]
        )

        left.caption(
            f"선택: {name} ({code})"
        )

        with right:

            if st.button(
                (
                    "추가"
                    if code
                    not in st.session_state.watchlist
                    else "등록됨"
                ),
                disabled=(
                    code
                    in st.session_state.watchlist
                ),
                use_container_width=True,
                key=f"add_{code}",
            ):

                if (
                    code
                    not in
                    st.session_state.watchlist
                ):

                    st.session_state.watchlist.append(
                        code
                    )

                    write_json(
                        WATCHLIST_FILE,
                        st.session_state.watchlist,
                    )

                navigate(code)


# ============================================================
# WATCHLIST
# ============================================================

def render_watchlist():

    st.markdown("### 관심종목")

    watchlist = (
        st.session_state.watchlist
    )

    if not watchlist:

        st.caption(
            "관심종목이 없습니다."
        )

        return

    labels = [
        f"{name_of(code)} · {code}"
        for code in watchlist
    ]

    current = (
        st.session_state.selected_code
    )

    index = (
        watchlist.index(current)
        if current in watchlist
        else 0
    )

    selected = st.selectbox(
        "관심종목",
        labels,
        index=index,
        label_visibility="collapsed",
        key="watch_select",
    )

    code = watchlist[
        labels.index(selected)
    ]

    st.session_state.selected_code = code

    if st.button(
        "현재 ETF 관심종목에서 삭제",
        use_container_width=True,
        key="delete_watch",
    ):

        st.session_state.watchlist = [
            item
            for item in watchlist
            if item != code
        ]

        write_json(
            WATCHLIST_FILE,
            st.session_state.watchlist,
        )

        st.session_state.selected_code = (
            st.session_state.watchlist[0]
            if st.session_state.watchlist
            else list(BASE_ETFS)[0]
        )

        st.rerun()


# ============================================================
# JUDGMENT UI
# ============================================================

def render_judgment(data):

    result = judgment(data)

    st.markdown(
        "### 현재판단 · 지금대응"
    )

    a, b, c = st.columns(3)

    with a:

        st.metric(
            "20일선",
            result["ma"],
        )

    with b:

        st.metric(
            "RSI14",
            f'{result["rsi"]:.1f}',
            result["rs"],
        )

    with c:

        st.metric(
            "거래량",
            f'{result["vr"]:.2f}배',
            result["vs"],
        )

    left, right = st.columns(2)

    with left:

        st.markdown(
            "**현재 시장 판단**"
        )

        st.subheader(
            result["title"]
        )

        st.write(
            " · ".join(
                result["reasons"]
            )
        )

    with right:

        st.markdown(
            "**지금 대응**"
        )

        st.write(
            result["action"]
        )


# ============================================================
# CHART
# ============================================================

def render_chart(data):

    end_date = data.index.max()

    start_date = (
        end_date -
        pd.DateOffset(months=6)
    )

    chart_data = data[
        data.index >= start_date
    ].copy()

    figure = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=.025,
        row_heights=[
            .76,
            .24,
        ],
    )

    figure.add_trace(
        go.Candlestick(
            x=chart_data.index,
            open=chart_data.Open,
            high=chart_data.High,
            low=chart_data.Low,
            close=chart_data.Close,
            increasing_line_color="#65d7b5",
            increasing_fillcolor="#65d7b5",
            decreasing_line_color="#f0786d",
            decreasing_fillcolor="#f0786d",
            name="가격",
        ),
        row=1,
        col=1,
    )

    figure.add_trace(
        go.Scatter(
            x=chart_data.index,
            y=chart_data.MA20,
            mode="lines",
            line=dict(
                color="#79b7d9",
                width=1.5,
            ),
            name="20일선",
        ),
        row=1,
        col=1,
    )

    figure.add_trace(
        go.Scatter(
            x=chart_data.index,
            y=chart_data.MA60,
            mode="lines",
            line=dict(
                color="#e6bb63",
                width=1.4,
            ),
            name="60일선",
        ),
        row=1,
        col=1,
    )

    volume_colors = np.where(
        chart_data.Close
        >= chart_data.Open,
        "#65d7b5",
        "#f0786d",
    )

    figure.add_trace(
        go.Bar(
            x=chart_data.index,
            y=chart_data.Volume,
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
            t=18,
            b=5,
        ),
        paper_bgcolor="#242624",
        plot_bgcolor="#242624",
        font=dict(
            color="#eeeae0",
        ),
        dragmode=False,
        hovermode="x unified",
        showlegend=True,
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
        key="six_month_fixed_chart",
    )

    st.caption(
        "최근 6개월 고정 · 확대/축소/좌우이동 없음"
    )


# ============================================================
# FUTURE THEME DATA
# ============================================================

def theme_rows(theme):

    cache = (
        st.session_state.theme_cache.get(
            theme
        )
    )

    now = datetime.now()

    if (
        cache
        and (
            now - cache["time"]
        ).total_seconds() < 300
    ):

        return cache["rows"]

    info = THEMES[theme]

    candidates = []
    seen = set()

    for code in info["seeds"]:

        code = str(code).zfill(6)

        if code not in seen:

            candidates.append(code)
            seen.add(code)

    for code, name in (
        st.session_state.etf_universe.items()
    ):

        if (
            code not in seen
            and any(
                keyword.lower()
                in name.lower()
                for keyword
                in info["keywords"]
            )
        ):

            candidates.append(code)
            seen.add(code)

    rows = []

    for code in candidates[:4]:

        data = indicators(
            load_price(code)
        )

        if data.empty:

            continue

        row = data.iloc[-1]

        price = sf(row.Close)

        rows.append(
            {
                "code": code,
                "name": name_of(code),
                "price": price,
                "rsi": sf(
                    row.RSI14,
                    50,
                ),
                "vr": sf(
                    row.VOL_RATIO,
                    1,
                ),
                "ret": sf(
                    row.RET20,
                    0,
                ),
                "trend":
                    (
                        "상승"
                        if price
                        >= sf(
                            row.MA20,
                            price,
                        )
                        else "조정"
                    ),
            }
        )

    st.session_state.theme_cache[
        theme
    ] = {
        "time": now,
        "rows": rows,
    }

    return rows


# ============================================================
# FUTURE THEME UI
# ============================================================

def render_theme(
    theme,
    stage,
    index,
):

    info = THEMES[theme]

    st.markdown(
        f"**{stage}**"
    )

    st.markdown(
        f"### {theme}"
    )

    st.caption(
        info["reason"]
    )

    rows = theme_rows(theme)

    if not rows:

        st.caption(
            "현재 표시 가능한 ETF 데이터가 없습니다."
        )

        return

    columns = st.columns(
        len(rows)
    )

    for i, item in enumerate(rows):

        with columns[i]:

            st.markdown(
                f'**{item["name"]}**'
            )

            st.caption(
                item["code"]
            )

            st.metric(
                "현재가",
                money(item["price"]),
            )

            st.metric(
                "RSI14",
                f'{item["rsi"]:.1f}',
            )

            st.metric(
                "거래량",
                f'{item["vr"]:.2f}배',
            )

            st.metric(
                "20일",
                f'{item["ret"]:+.2f}%',
            )

            st.caption(
                f'추세: {item["trend"]}'
            )

            if st.button(
                "ETF 분석",
                use_container_width=True,
                key=(
                    f"theme_"
                    f"{index}_"
                    f"{i}_"
                    f'{item["code"]}'
                ),
            ):

                navigate(
                    item["code"]
                )


# ============================================================
# MY ETF
# ============================================================

def my_etf():

    render_finder()

    render_watchlist()

    code = (
        st.session_state.selected_code
    )

    data = indicators(
        load_price(code)
    )

    if data.empty:

        st.error(
            "가격 데이터를 불러오지 못했습니다. "
            "잠시 후 다시 시도해 주세요."
        )

        return

    current = sf(
        data.Close.iloc[-1]
    )

    previous = sf(
        data.Close.iloc[-2],
        current,
    )

    change = (
        current - previous
    )

    change_pct = (
        change / previous * 100
        if previous
        else 0
    )

    st.markdown(
        f"## {name_of(code)}"
    )

    st.caption(
        f"{code} · 기준일 "
        f"{data.index[-1].strftime('%Y-%m-%d')}"
    )

    left, right = st.columns(
        [2, 1]
    )

    with left:

        st.markdown(
            f"# {money(current)}"
        )

    with right:

        if change > 0:

            st.success(
                f"{money(change)} "
                f"({change_pct:+.2f}%)"
            )

        elif change < 0:

            st.error(
                f"{money(change)} "
                f"({change_pct:+.2f}%)"
            )

        else:

            st.info(
                f"{money(change)} "
                f"({change_pct:+.2f}%)"
            )

    holding = (
        st.session_state.holdings.get(
            code
        )
    )

    st.markdown(
        "### 보유 상태"
    )

    holding_status = st.radio(
        "보유 여부",
        [
            "미보유",
            "보유중",
        ],
        index=(
            1
            if holding
            else 0
        ),
        horizontal=True,
        label_visibility="collapsed",
        key=f"hold_{code}",
    )

    if holding_status == "보유중":

        left, right = st.columns(2)

        with left:

            average_price = st.number_input(
                "평균매수가",
                min_value=0.0,
                value=float(
                    holding.get(
                        "avg_price",
                        0,
                    )
                    if holding
                    else 0
                ),
                step=100.0,
                key=f"avg_{code}",
            )

        with right:

            quantity = st.number_input(
                "보유수량",
                min_value=0.0,
                value=float(
                    holding.get(
                        "quantity",
                        0,
                    )
                    if holding
                    else 0
                ),
                step=1.0,
                key=f"qty_{code}",
            )

        if st.button(
            "보유정보 저장",
            use_container_width=True,
            key=f"save_{code}",
        ):

            st.session_state.holdings[
                code
            ] = {
                "avg_price":
                    average_price,
                "quantity":
                    quantity,
            }

            write_json(
                HOLDINGS_FILE,
                st.session_state.holdings,
            )

            st.rerun()

    elif code in st.session_state.holdings:

        if st.button(
            "보유정보 삭제",
            use_container_width=True,
            key=f"delhold_{code}",
        ):

            del st.session_state.holdings[
                code
            ]

            write_json(
                HOLDINGS_FILE,
                st.session_state.holdings,
            )

            st.rerun()

    render_judgment(data)

    st.markdown(
        "### 핵심가격 · 대응 시나리오"
    )

    price_levels = levels(data)

    columns = st.columns(4)

    for column, (
        label,
        price,
        description,
    ) in zip(
        columns,
        price_levels,
    ):

        with column:

            st.metric(
                label,
                money(price),
            )

            st.caption(
                description
            )

    st.markdown(
        "### 가격 흐름"
    )

    render_chart(data)


# ============================================================
# FUTURE
# ============================================================

def future():

    st.markdown(
        "## 미래테마"
    )

    st.caption(
        "현재 주도 → 다음 수혜 → 초기 관심"
    )

    if st.button(
        "시장 데이터 다시 탐색",
        use_container_width=True,
        key="theme_refresh",
    ):

        st.session_state.price_cache = {}
        st.session_state.theme_cache = {}

        refresh_universe()

        st.rerun()

    for index, (
        theme,
        stage,
    ) in enumerate(
        FUTURE_CHAIN
    ):

        render_theme(
            theme,
            stage,
            index,
        )

    summary = []

    for theme, stage in FUTURE_CHAIN:

        rows = theme_rows(theme)

        if rows:

            summary.append(
                {
                    "테마": theme,
                    "단계": stage,
                    "평균 20일수익률":
                        f"{np.mean([x['ret'] for x in rows]):+.2f}%",
                    "평균 RSI":
                        f"{np.mean([x['rsi'] for x in rows]):.1f}",
                    "평균 거래량":
                        f"{np.mean([x['vr'] for x in rows]):.2f}배",
                }
            )

    if summary:

        st.markdown(
            "### 테마 요약"
        )

        st.dataframe(
            pd.DataFrame(summary),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# APP START
# ============================================================

init_state()


# 중요:
# widget이 만들어진 뒤 main_page를 직접 변경하지 않고
# rerun 시작 시점에 page_request를 반영한다.

if st.session_state.page_request:

    requested_page = (
        st.session_state.page_request
    )

    st.session_state.page_request = None

    if requested_page in [
        "📊 내 ETF",
        "🚀 미래테마",
    ]:

        st.session_state.main_page = (
            requested_page
        )


st.markdown(
    "# ETF RADAR"
)

st.caption(
    "ETF 추세 · 모멘텀 · 거래량 · "
    "핵심가격 · 대응 시나리오"
)


page = st.radio(
    "메뉴",
    [
        "📊 내 ETF",
        "🚀 미래테마",
    ],
    horizontal=True,
    key="main_page",
)


if page == "📊 내 ETF":

    my_etf()

else:

    future()