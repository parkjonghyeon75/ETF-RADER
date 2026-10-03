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
# PREMIUM WARM GRAPHITE THEME
# ============================================================
st.markdown(r'''<style>
:root{
    --bg:#171817;
    --bg2:#1d1f1d;
    --panel:#242624;
    --panel2:#2b2e2b;
    --panel3:#323532;
    --line:#414641;
    --text:#f3f0e8;
    --text2:#ddd9cf;
    --muted:#9da39b;
    --mint:#65d7b5;
    --coral:#f0786d;
    --amber:#e6bb63;
    --orange:#ee9365;
    --sky:#79b7d9;
}

/* ============================================================
   STREAMLIT 전체 기본 흰색 영역 제거
   ============================================================ */

html,
body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section.main,
.main,
.main > div,
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

[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="column"],
[data-testid="stColumn"],
.element-container,
.stMarkdown,
.stCaption{
    background:transparent!important;
    color:var(--text)!important;
}

*{
    box-sizing:border-box;
    scrollbar-color:#555b55 var(--bg);
    scrollbar-width:thin;
}

body{
    background:var(--bg)!important;
    color:var(--text)!important;
}

h1,h2,h3,h4,h5,h6,
p,span,label,div{
    color:inherit;
}

/* ============================================================
   HEADER
   ============================================================ */

.app-title{
    font-size:1.65rem;
    font-weight:900;
    letter-spacing:-.05em;
    color:#f5f1e8!important;
}

.app-sub{
    color:var(--muted)!important;
    font-size:.78rem;
    margin-top:2px;
}

.section{
    font-size:1.05rem;
    font-weight:900;
    margin:18px 0 8px;
    color:#f1eee5!important;
}

.sub{
    color:var(--muted)!important;
    font-size:.78rem;
}

/* ============================================================
   HERO / CARD
   ============================================================ */

.hero,
.panel,
.card,
.theme-card{
    background:var(--panel)!important;
    border:1px solid var(--line)!important;
    border-radius:13px!important;
    color:var(--text)!important;
    box-shadow:0 6px 22px rgba(0,0,0,.20)!important;
}

.hero{
    padding:16px;
    margin:10px 0;
}

.hero-name{
    font-size:1.3rem;
    font-weight:900;
    color:#f5f1e8!important;
}

.hero-code{
    font-size:.76rem;
    color:var(--muted)!important;
}

.quote{
    display:flex;
    align-items:baseline;
    gap:12px;
    margin-top:13px;
}

.price{
    font-size:2.1rem;
    font-weight:900;
    letter-spacing:-.05em;
    color:#fffaf0!important;
}

.chg{
    font-size:1rem;
    font-weight:800;
}

.pos{
    color:var(--mint)!important;
}

.neg{
    color:var(--coral)!important;
}

.neu{
    color:var(--text2)!important;
}

/* ============================================================
   EVIDENCE
   ============================================================ */

.panel{
    padding:13px;
    margin:8px 0;
}

.evidence{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:7px;
    margin:8px 0;
}

.e-box{
    background:var(--panel2)!important;
    border:1px solid var(--line)!important;
    border-radius:9px;
    padding:10px;
}

.e-label,
.e-sub{
    font-size:.7rem;
    color:var(--muted)!important;
}

.e-value{
    font-size:.95rem;
    font-weight:900;
    margin-top:3px;
    color:#f4f0e7!important;
}

/* ============================================================
   JUDGMENT
   ============================================================ */

.judge{
    border-left:4px solid var(--mint);
    padding:13px;
    background:var(--panel2)!important;
    border-radius:9px;
}

.judge-title{
    font-size:.73rem;
    color:var(--muted)!important;
}

.judge-main{
    font-size:1.2rem;
    font-weight:900;
    margin-top:3px;
    color:#f5f1e8!important;
}

.judge-text{
    font-size:.83rem;
    line-height:1.55;
    color:#d8d7d0!important;
    margin-top:7px;
}

.action{
    border-left:4px solid var(--amber);
    padding:13px;
    background:var(--panel2)!important;
    border-radius:9px;
}

.action-title{
    font-size:.73rem;
    color:var(--amber)!important;
    font-weight:800;
}

.action-text{
    font-size:.84rem;
    line-height:1.55;
    font-weight:700;
    margin-top:5px;
    color:#eeeae0!important;
}

/* ============================================================
   PRICE SCENARIO
   ============================================================ */

.scenarios{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:7px;
}

.scenario{
    background:var(--panel)!important;
    border:1px solid var(--line)!important;
    border-radius:9px;
    padding:10px;
}

.s-label{
    font-size:.68rem;
    color:var(--muted)!important;
}

.s-price{
    font-size:1.05rem;
    font-weight:900;
    margin-top:4px;
    color:#f5f1e8!important;
}

.s-desc{
    font-size:.7rem;
    color:#c4c7c1!important;
    line-height:1.4;
    margin-top:5px;
}

/* ============================================================
   FUTURE THEME
   ============================================================ */

.theme-card{
    padding:13px;
    margin:9px 0;
    background:linear-gradient(
        135deg,
        #252825,
        #222522
    )!important;
}

.stage{
    font-size:.72rem;
    color:var(--mint)!important;
    font-weight:900;
}

.theme-title{
    font-size:1.1rem;
    font-weight:900;
    margin-top:2px;
    color:#f4f0e7!important;
}

.theme-reason{
    font-size:.79rem;
    color:#c4c8c1!important;
    line-height:1.5;
    margin:4px 0 10px;
}

.theme-etf{
    background:var(--panel2)!important;
    border:1px solid var(--line)!important;
    border-radius:9px;
    padding:11px;
}

.theme-name{
    font-size:.95rem;
    font-weight:900;
    color:#f4f0e7!important;
}

.theme-code{
    font-size:.7rem;
    color:var(--muted)!important;
}

.theme-grid{
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:5px;
    margin-top:8px;
}

.theme-stat{
    background:#202320!important;
    border:1px solid #3b403b;
    border-radius:7px;
    padding:8px;
}

.theme-stat-label{
    font-size:.65rem;
    color:var(--muted)!important;
}

.theme-stat-value{
    font-size:.92rem;
    font-weight:900;
    margin-top:2px;
    color:#f2eee5!important;
}

/* ============================================================
   BUTTON
   ============================================================ */

.stButton > button,
button[kind="secondary"],
button[kind="primary"]{
    background:#303430!important;
    color:#f5f1e8!important;
    border:1px solid #4b514b!important;
    border-radius:8px!important;
    font-weight:800!important;
    box-shadow:none!important;
}

.stButton > button:hover{
    background:#3a3f3a!important;
    border-color:var(--mint)!important;
    color:#fff!important;
}

.stButton > button[kind="primary"]{
    background:#3a6f61!important;
    border-color:#65d7b5!important;
}

/* ============================================================
   INPUT
   ============================================================ */

div[data-baseweb="input"],
div[data-baseweb="input"] > div,
div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"],
div[data-baseweb="textarea"] > div{
    background:#292c29!important;
    color:#f5f1e8!important;
    border-color:#4a504a!important;
    box-shadow:none!important;
}

input,
textarea{
    background:#292c29!important;
    color:#f5f1e8!important;
    -webkit-text-fill-color:#f5f1e8!important;
    border-color:#4a504a!important;
}

input::placeholder,
textarea::placeholder{
    color:#858c84!important;
    -webkit-text-fill-color:#858c84!important;
}

div[data-baseweb="select"] span{
    color:#f5f1e8!important;
}

/* ============================================================
   DROPDOWN
   ============================================================ */

ul[role="listbox"],
div[role="listbox"],
[data-baseweb="popover"] > div,
li[role="option"],
div[role="option"]{
    background:#292c29!important;
    color:#f5f1e8!important;
    border-color:#4a504a!important;
}

li[role="option"]:hover,
div[role="option"]:hover{
    background:#3a3f3a!important;
}

/* ============================================================
   RADIO
   ============================================================ */

[data-testid="stRadio"]{
    background:transparent!important;
    color:#ddd9cf!important;
}

[data-testid="stRadio"] label,
[data-testid="stRadio"] label p{
    color:#ddd9cf!important;
}

[data-testid="stRadio"] [role="radiogroup"]{
    background:#242724!important;
    border:1px solid var(--line)!important;
    border-radius:9px!important;
    padding:4px 8px!important;
}

/* ============================================================
   ALERT / CAPTION
   ============================================================ */

[data-testid="stAlert"],
div[data-testid="stNotification"]{
    background:#292c29!important;
    color:#ddd9cf!important;
    border:1px solid #454b45!important;
}

.stAlert p,
.stAlert span,
.stAlert div,
[data-testid="stCaptionContainer"],
.stCaption{
    color:var(--muted)!important;
}

/* ============================================================
   DATAFRAME
   ============================================================ */

[data-testid="stDataFrame"],
div[data-testid="stDataFrame"] > div{
    background:#242724!important;
    border:1px solid var(--line)!important;
    color:#eeeae0!important;
}

[data-testid="stDataFrame"] iframe{
    background:#242724!important;
}

/* ============================================================
   TABS
   ============================================================ */

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

/* ============================================================
   EXPANDER
   ============================================================ */

[data-testid="stExpander"]{
    background:#242724!important;
    border:1px solid var(--line)!important;
    border-radius:9px!important;
}

[data-testid="stExpander"] summary{
    background:#242724!important;
    color:#eeeae0!important;
}

hr{
    border-color:#383d38!important;
}

/* ============================================================
   PLOTLY
   ============================================================ */

div[data-testid="stPlotlyChart"],
.js-plotly-plot,
.plot-container,
.svg-container{
    background:#242724!important;
    border-radius:10px!important;
}

.js-plotly-plot{
    touch-action:pan-y!important;
}

/* ============================================================
   STREAMLIT TOP STATUS
   ============================================================ */

[data-testid="stStatusWidget"]{
    display:none!important;
}

/* ============================================================
   MOBILE
   ============================================================ */

@media(max-width:700px){

    .block-container{
        padding:8px 9px 24px!important;
    }

    .price{
        font-size:1.85rem;
    }

    .scenarios{
        grid-template-columns:repeat(2,1fr);
    }

    .theme-grid{
        grid-template-columns:repeat(2,1fr);
    }

    .theme-name{
        font-size:.9rem;
    }

    .theme-stat-value{
        font-size:.86rem;
    }

    .e-value{
        font-size:.82rem;
    }
}
</style>
''', unsafe_allow_html=True)


# ============================================================
# FILES
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"
UNIVERSE_FILE = "etf_universe_cache.json"


# ============================================================
# ETF BASE DATA
# ============================================================

BASE_ETFS = {
    "395160":"KODEX AI반도체핵심장비",
    "487240":"KODEX AI반도체",
    "471990":"KODEX AI반도체TOP2Plus",
    "133690":"TIGER 미국나스닥100",
    "360750":"TIGER 미국S&P500",
    "458730":"TIGER 글로벌AI&로봇",
    "381170":"TIGER 미국테크TOP10 INDXX",
    "396500":"TIGER 반도체",
    "091160":"KODEX 반도체",
    "305720":"KODEX 2차전지산업",
    "449170":"TIGER 글로벌AI인프라액티브",
    "434060":"TIGER 글로벌AI&반도체액티브",
    "464240":"KODEX AI전력핵심설비",
    "487130":"KODEX AI전력인프라",
    "475050":"ACE 글로벌반도체TOP4 Plus",
    "469150":"ACE AI반도체포커스"
}

FALLBACK_ETFS = BASE_ETFS.copy()

DEFAULT_WATCHLIST = [
    "395160",
    "487240",
    "471990",
    "133690",
    "360750",
    "458730"
]


# ============================================================
# THEMES
# ============================================================

THEMES = {

    "AI 반도체":{
        "keywords":[
            "AI반도체",
            "반도체",
            "AI",
            "HBM",
            "반도체장비"
        ],
        "seeds":[
            "395160",
            "487240",
            "471990",
            "396500"
        ],
        "reason":
            "AI 연산 확대와 첨단 반도체 투자 증가의 직접적인 수혜 영역입니다."
    },

    "데이터센터·AI 인프라":{
        "keywords":[
            "데이터센터",
            "AI인프라",
            "AI 인프라",
            "글로벌AI인프라"
        ],
        "seeds":[
            "449170",
            "434060",
            "381170"
        ],
        "reason":
            "AI 서비스 확산에 따라 서버·네트워크·데이터센터 투자를 추적합니다."
    },

    "전력 인프라":{
        "keywords":[
            "전력",
            "전력인프라",
            "전력핵심설비",
            "전력설비"
        ],
        "seeds":[
            "464240",
            "487130"
        ],
        "reason":
            "데이터센터와 산업용 전력수요 증가에 따른 전력망 투자를 추적합니다."
    },

    "원자력":{
        "keywords":[
            "원자력",
            "원전"
        ],
        "seeds":[],
        "reason":
            "전력수요와 에너지 믹스 변화에 따른 원전 관련 흐름을 추적합니다."
    },

    "냉각·열관리":{
        "keywords":[
            "냉각",
            "열관리",
            "액침냉각"
        ],
        "seeds":[
            "434060",
            "449170"
        ],
        "reason":
            "AI 서버 고집적화에 따른 냉각·열관리 후방 수혜를 추적합니다."
    }
}

FUTURE_CHAIN = [
    ("AI 반도체","현재 주도"),
    ("데이터센터·AI 인프라","다음 수혜"),
    ("전력 인프라","다음 수혜"),
    ("원자력","관심 확대"),
    ("냉각·열관리","초기 관심")
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
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return default


def write_json(path, data):

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
# ETF UNIVERSE
# ============================================================

def load_universe():

    u = dict(BASE_ETFS)

    cached = read_json(
        UNIVERSE_FILE,
        {}
    )

    if isinstance(cached, dict):

        for c, n in cached.items():

            if c and n:

                u[str(c).zfill(6)] = str(n)

    return u


def fetch_catalog():

    url = (
        "https://finance.naver.com/"
        "api/sise/etfItemList.nhn"
    )

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent":
            "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(
        req,
        timeout=7
    ) as r:

        raw = r.read()

    root = ET.fromstring(raw)

    out = {}

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

            out[
                str(code).zfill(6)
            ] = name

    return out


def refresh_universe():

    try:

        ext = fetch_catalog()

        if ext:

            u = dict(
                st.session_state.etf_universe
            )

            u.update(ext)

            st.session_state.etf_universe = u

            write_json(
                UNIVERSE_FILE,
                u
            )

            st.session_state.notice = (
                f"ETF 목록을 {len(ext):,}개 확인했습니다."
            )

            return

    except Exception:

        pass

    st.session_state.notice = (
        "외부 목록 연결이 지연되어 기존 ETF 목록을 사용합니다."
    )


# ============================================================
# SESSION STATE
# ============================================================

def init_state():

    if "watchlist" not in st.session_state:

        w = read_json(
            WATCHLIST_FILE,
            DEFAULT_WATCHLIST.copy()
        )

        if isinstance(w, list):

            st.session_state.watchlist = [
                str(x).zfill(6)
                for x in w
            ]

        else:

            st.session_state.watchlist = (
                DEFAULT_WATCHLIST.copy()
            )

    if "holdings" not in st.session_state:

        st.session_state.holdings = read_json(
            HOLDINGS_FILE,
            {}
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

        st.session_state.main_page = "📊 내 ETF"

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
            f"ETF {code}"
        )
    )


def sf(v, d=0.0):

    try:

        return d if pd.isna(v) else float(v)

    except Exception:

        return d


def money(v):

    v = sf(v)

    if abs(v) >= 1000:

        return f"{v:,.0f}원"

    return f"{v:,.2f}원"


# ============================================================
# DATA NORMALIZE
# ============================================================

def normalize(df):

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    if isinstance(
        df.columns,
        pd.MultiIndex
    ):

        df.columns = [
            c[0]
            if isinstance(c, tuple)
            else str(c)
            for c in df.columns
        ]

    ren = {}

    for c in df.columns:

        k = str(c).lower()

        ren[c] = {
            "open":"Open",
            "high":"High",
            "low":"Low",
            "close":"Close",
            "volume":"Volume"
        }.get(k, c)

    df = df.rename(columns=ren)

    req = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    if any(
        c not in df.columns
        for c in req
    ):

        return pd.DataFrame()

    for c in req:

        df[c] = pd.to_numeric(
            df[c],
            errors="coerce"
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

    return df[req]


# ============================================================
# PRICE DATA
# ============================================================

def fetch_naver(code):

    try:

        url = (
            "https://fchart.stock.naver.com/"
            f"spevent.nhn?symbol={str(code).zfill(6)}"
            "&timeframe=day"
            "&count=600"
            "&requestType=0"
        )

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            req,
            timeout=7
        ) as r:

            raw = r.read()

        root = ET.fromstring(raw)

        rows = []

        for item in root.findall(".//item"):

            p = item.attrib.get(
                "data",
                ""
            ).split("|")

            if len(p) >= 6:

                rows.append([
                    p[0],
                    float(p[1]),
                    float(p[2]),
                    float(p[3]),
                    float(p[4]),
                    float(p[5])
                ])

        if not rows:

            return pd.DataFrame()

        d = pd.DataFrame(
            rows,
            columns=[
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume"
            ]
        )

        d["Date"] = pd.to_datetime(
            d["Date"]
        )

        return normalize(
            d.set_index("Date")
        )

    except Exception:

        return pd.DataFrame()


def fetch_yahoo(code):

    try:

        return normalize(
            yf.download(
                f"{str(code).zfill(6)}.KS",
                period="2y",
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=False
            )
        )

    except Exception:

        return pd.DataFrame()


def load_price(code, force=False):

    code = str(code).zfill(6)

    now = datetime.now()

    cached = (
        st.session_state.price_cache
        .get(code)
    )

    if (
        cached
        and not force
        and (
            now - cached["time"]
        ).total_seconds() < 300
    ):

        return cached["data"]

    d = fetch_naver(code)

    if d.empty:

        d = fetch_yahoo(code)

    if not d.empty:

        st.session_state.price_cache[
            code
        ] = {
            "time":now,
            "data":d
        }

    return d


# ============================================================
# INDICATORS
# ============================================================

def indicators(df):

    if df.empty:

        return pd.DataFrame()

    d = df.copy()

    d["MA20"] = (
        d.Close.rolling(20).mean()
    )

    d["MA60"] = (
        d.Close.rolling(60).mean()
    )

    delta = d.Close.diff()

    gain = (
        delta.where(
            delta > 0,
            0
        ).rolling(14).mean()
    )

    loss = (
        (-delta.where(
            delta < 0,
            0
        )).rolling(14).mean()
    )

    rs = (
        gain /
        loss.replace(
            0,
            np.nan
        )
    )

    d["RSI14"] = (
        100 -
        (
            100 /
            (1 + rs)
        )
    )

    d["VOL20"] = (
        d.Volume.rolling(20).mean()
    )

    d["VOL_RATIO"] = (
        d.Volume /
        d.VOL20
    )

    d["RET20"] = (
        d.Close.pct_change(20) * 100
    )

    d["HIGH20"] = (
        d.High.rolling(20).max()
    )

    d["LOW20"] = (
        d.Low.rolling(20).min()
    )

    d["LOW60"] = (
        d.Low.rolling(60).min()
    )

    return d


# ============================================================
# JUDGMENT
# ============================================================

def judgment(d):

    r = d.iloc[-1]

    cur = sf(r.Close)

    ma20 = sf(
        r.MA20,
        cur
    )

    ma60 = sf(
        r.MA60,
        cur
    )

    rsi = sf(
        r.RSI14,
        50
    )

    vr = sf(
        r.VOL_RATIO,
        1
    )

    ret = sf(
        r.RET20,
        0
    )

    above20 = cur >= ma20
    above60 = cur >= ma60

    ma = (
        "20일선 상회"
        if above20
        else
        "20일선 하회"
    )

    rs = (
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

    vs = (
        "거래량 강한 확대"
        if vr >= 1.5
        else
        "거래량 증가"
        if vr >= 1.1
        else
        "평균 수준"
        if vr >= .8
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
            "신규 진입보다 지지 형성과 거래량 회복을 확인합니다."
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
            f"현재가 {money(cur)} · "
            f"20일선 {money(ma20)} · {ma}"
        ),
        (
            f"RSI14 {rsi:.1f} · {rs}"
        ),
        (
            f"거래량 {vr:.2f}배 · {vs} · "
            f"20일 수익률 {ret:+.2f}%"
        )
    ]

    return {
        "title":title,
        "action":action,
        "ma":ma,
        "rs":rs,
        "vs":vs,
        "rsi":rsi,
        "vr":vr,
        "ret":ret,
        "reasons":reasons
    }


# ============================================================
# PRICE LEVELS
# ============================================================

def levels(d):

    r = d.iloc[-1]

    cur = sf(
        r.Close
    )

    ma20 = sf(
        r.MA20,
        cur
    )

    ma60 = sf(
        r.MA60,
        cur
    )

    high = sf(
        r.HIGH20,
        cur
    )

    low = sf(
        r.LOW20,
        cur
    )

    low60 = sf(
        r.LOW60,
        cur
    )

    return [
        (
            "1차 관심가격",
            ma20,
            "20일선 눌림 확인"
        ),
        (
            "핵심 지지",
            min(ma60, low),
            "중기 추세 확인"
        ),
        (
            "돌파 기준",
            high,
            "최근 20일 고점"
        ),
        (
            "위험 가격",
            min(
                ma60,
                low,
                low60
            ),
            "이탈 시 방어 검토"
        )
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

def search(q):

    q = (
        q or ""
    ).strip().lower()

    return [
        (c,n)
        for c,n
        in st.session_state.etf_universe.items()
        if q
        and (
            q in c.lower()
            or q in n.lower()
        )
    ][:40]


# ============================================================
# ETF FINDER
# ============================================================

def render_finder():

    st.markdown(
        '<div class="section">ETF 찾기</div>',
        unsafe_allow_html=True
    )

    a,b = st.columns([5,1])

    with a:

        q = st.text_input(
            "ETF 검색",
            placeholder="ETF명 또는 종목코드",
            label_visibility="collapsed",
            key="search_q"
        )

    with b:

        if st.button(
            "목록 갱신",
            use_container_width=True
        ):

            refresh_universe()
            st.rerun()

    if st.session_state.notice:

        st.caption(
            st.session_state.notice
        )

        st.session_state.notice = None

    res = search(q)

    if res:

        labels = [
            f"{n} · {c}"
            for c,n in res
        ]

        label = st.selectbox(
            "검색 결과",
            labels,
            label_visibility="collapsed",
            key="search_select"
        )

        c,n = res[
            labels.index(label)
        ]

        x,y = st.columns([5,1])

        x.caption(
            f"선택: {n} ({c})"
        )

        with y:

            if st.button(
                "추가"
                if c not in st.session_state.watchlist
                else "등록됨",
                disabled=(
                    c in st.session_state.watchlist
                ),
                use_container_width=True,
                key=f"add_{c}"
            ):

                if (
                    c
                    not in
                    st.session_state.watchlist
                ):

                    st.session_state.watchlist.append(
                        c
                    )

                    write_json(
                        WATCHLIST_FILE,
                        st.session_state.watchlist
                    )

                navigate(c)


# ============================================================
# WATCHLIST
# ============================================================

def render_watchlist():

    st.markdown(
        '<div class="section">관심종목</div>',
        unsafe_allow_html=True
    )

    w = st.session_state.watchlist

    if not w:

        st.caption(
            "관심종목이 없습니다."
        )

        return

    labels = [
        f"{name_of(c)} · {c}"
        for c in w
    ]

    cur = (
        st.session_state.selected_code
    )

    idx = (
        w.index(cur)
        if cur in w
        else 0
    )

    label = st.selectbox(
        "관심종목",
        labels,
        index=idx,
        label_visibility="collapsed",
        key="watch_select"
    )

    code = w[
        labels.index(label)
    ]

    st.session_state.selected_code = code

    if st.button(
        "현재 ETF 관심종목에서 삭제",
        use_container_width=True,
        key="delete_watch"
    ):

        st.session_state.watchlist = [
            x for x in w
            if x != code
        ]

        write_json(
            WATCHLIST_FILE,
            st.session_state.watchlist
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

def render_judgment(d):

    j = judgment(d)

    st.markdown(
        '<div class="section">현재판단 · 지금대응</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'''
        <div class="evidence">

            <div class="e-box">
                <div class="e-label">20일선</div>
                <div class="e-value {'pos' if '상회' in j['ma'] else 'neg'}">
                    {j['ma']}
                </div>
                <div class="e-sub">
                    단기 추세
                </div>
            </div>

            <div class="e-box">
                <div class="e-label">RSI14</div>
                <div class="e-value {
                    'pos'
                    if j['rsi'] >= 60
                    else
                    'neg'
                    if j['rsi'] < 40
                    else
                    'neu'
                }">
                    {j['rsi']:.1f}
                </div>
                <div class="e-sub">
                    {j['rs']}
                </div>
            </div>

            <div class="e-box">
                <div class="e-label">거래량</div>
                <div class="e-value {
                    'pos'
                    if j['vr'] >= 1.1
                    else
                    'neg'
                    if j['vr'] < .8
                    else
                    'neu'
                }">
                    {j['vr']:.2f}배
                </div>
                <div class="e-sub">
                    {j['vs']}
                </div>
            </div>

        </div>
        ''',
        unsafe_allow_html=True
    )

    a,b = st.columns(2)

    with a:

        st.markdown(
            f'''
            <div class="judge">
                <div class="judge-title">
                    현재 시장 판단
                </div>

                <div class="judge-main">
                    {j["title"]}
                </div>

                <div class="judge-text">
                    {"<br>".join(j["reasons"])}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

    with b:

        st.markdown(
            f'''
            <div class="action">
                <div class="action-title">
                    지금 대응
                </div>

                <div class="action-text">
                    {j["action"]}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )


# ============================================================
# CHART
# ============================================================

def render_chart(d):

    end = d.index.max()

    start = (
        end -
        pd.DateOffset(months=6)
    )

    x = d[
        d.index >= start
    ].copy()

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=.025,
        row_heights=[.76,.24]
    )

    fig.add_trace(
        go.Candlestick(
            x=x.index,
            open=x.Open,
            high=x.High,
            low=x.Low,
            close=x.Close,
            increasing_line_color="#65d7b5",
            increasing_fillcolor="#65d7b5",
            decreasing_line_color="#f0786d",
            decreasing_fillcolor="#f0786d",
            name="가격"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=x.index,
            y=x.MA20,
            mode="lines",
            line=dict(
                color="#79b7d9",
                width=1.5
            ),
            name="20일선"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=x.index,
            y=x.MA60,
            mode="lines",
            line=dict(
                color="#e6bb63",
                width=1.4
            ),
            name="60일선"
        ),
        row=1,
        col=1
    )

    vc = np.where(
        x.Close >= x.Open,
        "#65d7b5",
        "#f0786d"
    )

    fig.add_trace(
        go.Bar(
            x=x.index,
            y=x.Volume,
            marker_color=vc,
            opacity=.45,
            name="거래량",
            showlegend=False
        ),
        row=2,
        col=1
    )

    fig.update_xaxes(
        fixedrange=True,
        showgrid=False,
        rangeslider_visible=False
    )

    fig.update_yaxes(
        fixedrange=True,
        showgrid=True,
        gridcolor="#303530",
        zeroline=False
    )

    fig.update_yaxes(
        fixedrange=True,
        showgrid=False,
        showticklabels=False,
        row=2,
        col=1
    )

    fig.update_layout(
        height=410,
        margin=dict(
            l=5,
            r=5,
            t=18,
            b=5
        ),
        paper_bgcolor="#242624",
        plot_bgcolor="#242624",
        font=dict(
            color="#eeeae0"
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
                size=10
            )
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar":False,
            "scrollZoom":False,
            "doubleClick":False,
            "responsive":True
        },
        key="six_month_fixed_chart"
    )

    st.caption(
        "최근 6개월 고정 · 확대/축소/좌우이동 없음"
    )


# ============================================================
# FUTURE THEME DATA
# ============================================================

def theme_rows(theme):

    cache = (
        st.session_state.theme_cache
        .get(theme)
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

    for c in info["seeds"]:

        c = str(c).zfill(6)

        if c not in seen:

            candidates.append(c)
            seen.add(c)

    for c,n in (
        st.session_state.etf_universe.items()
    ):

        if (
            c not in seen
            and any(
                k.lower() in n.lower()
                for k in info["keywords"]
            )
        ):

            candidates.append(c)
            seen.add(c)

    rows = []

    for c in candidates[:4]:

        try:

            d = indicators(
                load_price(c)
            )

            if d.empty:
                continue

            r = d.iloc[-1]

            price = sf(
                r.Close
            )

            rows.append({
                "code":c,
                "name":name_of(c),
                "price":price,
                "rsi":sf(
                    r.RSI14,
                    50
                ),
                "vr":sf(
                    r.VOL_RATIO,
                    1
                ),
                "ret":sf(
                    r.RET20,
                    0
                ),
                "trend":
                    "상승"
                    if price >= sf(
                        r.MA20,
                        price
                    )
                    else
                    "조정"
            })

        except Exception:

            continue

    st.session_state.theme_cache[
        theme
    ] = {
        "time":now,
        "rows":rows
    }

    return rows


# ============================================================
# FUTURE THEME UI
# ============================================================

def render_theme(
    theme,
    stage,
    index
):

    info = THEMES[theme]

    st.markdown(
        f'''
        <div class="theme-card">

            <div class="stage">
                {stage}
            </div>

            <div class="theme-title">
                {theme}
            </div>

            <div class="theme-reason">
                {info["reason"]}
            </div>

        </div>
        ''',
        unsafe_allow_html=True
    )

    rows = theme_rows(theme)

    if not rows:

        st.caption(
            "현재 표시 가능한 ETF 데이터가 없습니다."
        )

        return

    cols = st.columns(
        len(rows)
    )

    for i,item in enumerate(rows):

        with cols[i]:

            cls = (
                "pos"
                if item["ret"] >= 0
                else
                "neg"
            )

            trend_cls = (
                "pos"
                if item["trend"] == "상승"
                else
                "neg"
            )

            st.markdown(
                f'''
                <div class="theme-etf">

                    <div class="theme-name">
                        {item["name"]}
                    </div>

                    <div class="theme-code">
                        {item["code"]}
                    </div>

                    <div class="theme-grid">

                        <div class="theme-stat">
                            <div class="theme-stat-label">
                                현재가
                            </div>
                            <div class="theme-stat-value">
                                {money(item["price"])}
                            </div>
                        </div>

                        <div class="theme-stat">
                            <div class="theme-stat-label">
                                RSI14
                            </div>
                            <div class="theme-stat-value">
                                {item["rsi"]:.1f}
                            </div>
                        </div>

                        <div class="theme-stat">
                            <div class="theme-stat-label">
                                거래량
                            </div>
                            <div class="theme-stat-value">
                                {item["vr"]:.2f}배
                            </div>
                        </div>

                        <div class="theme-stat">
                            <div class="theme-stat-label">
                                20일
                            </div>
                            <div class="theme-stat-value {cls}">
                                {item["ret"]:+.2f}%
                            </div>
                        </div>

                    </div>

                    <div style="
                        font-size:.74rem;
                        color:#b8bec2;
                        margin-top:7px
                    ">
                        추세:
                        <span class="{trend_cls}">
                            {item["trend"]}
                        </span>
                    </div>

                </div>
                ''',
                unsafe_allow_html=True
            )

            if st.button(
                "ETF 분석",
                use_container_width=True,
                key=(
                    f"theme_"
                    f"{index}_"
                    f"{i}_"
                    f"{item['code']}"
                )
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

    d = indicators(
        load_price(code)
    )

    if d.empty:

        st.warning(
            "가격 데이터를 불러오지 못했습니다. "
            "잠시 후 다시 시도해 주세요."
        )

        return

    cur = sf(
        d.Close.iloc[-1]
    )

    prev = sf(
        d.Close.iloc[-2],
        cur
    )

    ch = cur - prev

    pct = (
        ch / prev * 100
        if prev
        else 0
    )

    cls = (
        "pos"
        if ch > 0
        else
        "neg"
        if ch < 0
        else
        "neu"
    )

    st.markdown(
        f'''
        <div class="hero">

            <div class="hero-name">
                {name_of(code)}
            </div>

            <div class="hero-code">
                {code}
                · 기준일
                {d.index[-1].strftime("%Y-%m-%d")}
            </div>

            <div class="quote">

                <div class="price">
                    {money(cur)}
                </div>

                <div class="chg {cls}">
                    {money(ch)}
                    ({pct:+.2f}%)
                </div>

            </div>

        </div>
        ''',
        unsafe_allow_html=True
    )

    h = (
        st.session_state.holdings
        .get(code)
    )

    st.markdown(
        '<div class="section">보유 상태</div>',
        unsafe_allow_html=True
    )

    held = st.radio(
        "보유 여부",
        [
            "미보유",
            "보유중"
        ],
        index=(
            1
            if h
            else
            0
        ),
        horizontal=True,
        label_visibility="collapsed",
        key=f"hold_{code}"
    )

    if held == "보유중":

        a,b = st.columns(2)

        avg = a.number_input(
            "평균매수가",
            min_value=0.0,
            value=float(
                h.get(
                    "avg_price",
                    0
                )
                if h
                else
                0
            ),
            step=100.0,
            key=f"avg_{code}"
        )

        qty = b.number_input(
            "보유수량",
            min_value=0.0,
            value=float(
                h.get(
                    "quantity",
                    0
                )
                if h
                else
                0
            ),
            step=1.0,
            key=f"qty_{code}"
        )

        if st.button(
            "보유정보 저장",
            use_container_width=True,
            key=f"save_{code}"
        ):

            st.session_state.holdings[
                code
            ] = {
                "avg_price":avg,
                "quantity":qty
            }

            write_json(
                HOLDINGS_FILE,
                st.session_state.holdings
            )

            st.rerun()

    elif code in st.session_state.holdings:

        if st.button(
            "보유정보 삭제",
            use_container_width=True,
            key=f"delhold_{code}"
        ):

            del st.session_state.holdings[
                code
            ]

            write_json(
                HOLDINGS_FILE,
                st.session_state.holdings
            )

            st.rerun()

    render_judgment(d)

    st.markdown(
        '<div class="section">'
        '핵심가격 · 대응 시나리오'
        '</div>',
        unsafe_allow_html=True
    )

    cards = levels(d)

    cards_html = "".join(
        f'''
        <div class="scenario">

            <div class="s-label">
                {label}
            </div>

            <div class="s-price">
                {money(price)}
            </div>

            <div class="s-desc">
                {desc}
            </div>

        </div>
        '''
        for label,price,desc
        in cards
    )

    st.markdown(
        f'''
        <div class="scenarios">
            {cards_html}
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section">가격 흐름</div>',
        unsafe_allow_html=True
    )

    render_chart(d)


# ============================================================
# FUTURE
# ============================================================

def future():

    st.markdown(
        '''
        <div class="hero">

            <div class="hero-name">
                미래테마
            </div>

            <div class="hero-code">
                현재 주도 → 다음 수혜 → 초기 관심
            </div>

        </div>
        ''',
        unsafe_allow_html=True
    )

    if st.button(
        "시장 데이터 다시 탐색",
        use_container_width=True,
        key="theme_refresh"
    ):

        st.session_state.price_cache = {}
        st.session_state.theme_cache = {}

        refresh_universe()

        st.rerun()

    for i,(theme,stage) in enumerate(
        FUTURE_CHAIN
    ):

        render_theme(
            theme,
            stage,
            i
        )

    rows = []

    for theme,stage in FUTURE_CHAIN:

        r = theme_rows(theme)

        if r:

            rows.append({
                "테마":theme,
                "단계":stage,
                "평균 20일수익률":
                    f"{np.mean([x['ret'] for x in r]):+.2f}%",
                "평균 RSI":
                    f"{np.mean([x['rsi'] for x in r]):.1f}",
                "평균 거래량":
                    f"{np.mean([x['vr'] for x in r]):.2f}배"
            })

    if rows:

        st.markdown(
            '<div class="section">테마 요약</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# APP START
# ============================================================

init_state()


# 중요:
# 위젯이 만들어진 이후 main_page를 직접 변경하지 않고
# 다음 rerun 시작 시점에서만 변경한다.
if st.session_state.page_request:

    req = (
        st.session_state.page_request
    )

    st.session_state.page_request = None

    if req in [
        "📊 내 ETF",
        "🚀 미래테마"
    ]:

        st.session_state.main_page = req


st.markdown(
    '''
    <div class="app-title">
        ETF RADAR
    </div>

    <div class="app-sub">
        ETF 추세 · 모멘텀 · 거래량 ·
        핵심가격 · 대응 시나리오
    </div>
    ''',
    unsafe_allow_html=True
)


page = st.radio(
    "메뉴",
    [
        "📊 내 ETF",
        "🚀 미래테마"
    ],
    horizontal=True,
    key="main_page"
)


if page == "📊 내 ETF":

    my_etf()

else:

    future()