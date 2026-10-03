import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import os
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


# ============================================================
# ETF RADAR v13
# Premium Mobile ETF Analysis Dashboard
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# FILES / CACHE
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"
ETF_CACHE_FILE = "etf_universe_cache.json"

ETF_CACHE_HOURS = 12
PRICE_CACHE_TTL = 300


# ============================================================
# ETF UNIVERSE
# ============================================================

BASE_ETFS = {
    "360750": "TIGER 미국S&P500",
    "379800": "KODEX 미국S&P500TR",
    "448290": "SOL 미국S&P500",
    "133690": "TIGER 미국나스닥100",
    "379810": "KODEX 미국나스닥100TR",

    "487240": "KODEX AI테크TOP10",
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


FALLBACK_ETFS = {
    "091160": "KODEX 반도체",
    "091230": "TIGER 반도체",
    "381180": "TIGER 미국필라델피아반도체나스닥",
    "139260": "TIGER IT",

    "091180": "KODEX 자동차",

    "091170": "KODEX 은행",
    "091220": "TIGER 은행",
    "139270": "TIGER 금융",

    "139230": "TIGER 조선운송",

    "143860": "TIGER 헬스케어",
    "227540": "TIGER 200 헬스케어",

    "211560": "TIGER 배당성장",
    "161510": "PLUS 고배당주",

    "132030": "KODEX 골드선물(H)",
    "411060": "ACE KRX금현물",
    "261220": "KODEX WTI원유선물(H)",

    "114260": "KODEX 국고채3년",
    "148070": "KOSEF 국고채10년",

    "449450": "ARIRANG K방산Fn",
    "463250": "TIGER K방산&우주",
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
            "반도체",
            "ai반도체",
            "반도체핵심",
            "미국반도체",
            "semiconductor",
        ],
        "seeds": [
            "395160",
            "462100",
            "486410",
            "091160",
            "091230",
            "381180",
        ],
        "reason":
            "AI 데이터센터 확대와 함께 HBM·첨단 패키징·고성능 반도체 수요가 이어지는 핵심 공급망입니다.",
    },

    "AI 소프트웨어·빅테크": {
        "keywords": [
            "ai테크",
            "나스닥",
            "테크",
            "s&p500",
            "빅테크",
            "소프트웨어",
        ],
        "seeds": [
            "487240",
            "452330",
            "133690",
            "379810",
            "360750",
        ],
        "reason":
            "AI 모델과 클라우드 투자가 확대되면서 플랫폼·소프트웨어·빅테크 전반으로 수혜 범위가 넓어질 수 있습니다.",
    },

    "데이터센터·AI 인프라": {
        "keywords": [
            "ai",
            "반도체",
            "전력",
            "테크",
        ],
        "seeds": [
            "471990",
            "395160",
            "487240",
            "462100",
        ],
        "reason":
            "AI 서버와 데이터센터 증설은 반도체뿐 아니라 전력·네트워크·냉각 등 주변 인프라 투자를 동반합니다.",
    },

    "전력 인프라": {
        "keywords": [
            "전력",
            "전기",
            "설비",
            "전력핵심",
        ],
        "seeds": [
            "471990",
        ],
        "reason":
            "데이터센터 전력수요와 전력망 투자 확대가 이어질 경우 전력기기·송배전 설비 수요가 연결됩니다.",
    },

    "원자력": {
        "keywords": [
            "원자력",
            "원전",
        ],
        "seeds": [
            "445380",
            "465560",
        ],
        "reason":
            "전력수요 증가와 안정적인 기저전원 확보 논의가 원전 및 관련 공급망 관심으로 이어지고 있습니다.",
    },

    "냉각·열관리": {
        "keywords": [
            "냉각",
            "열관리",
            "데이터센터",
        ],
        "seeds": [
            "471990",
            "395160",
        ],
        "reason":
            "고집적 AI 서버의 발열 증가로 데이터센터 냉각과 열관리의 중요도가 높아지는 구조적 테마입니다.",
    },

    "로봇·휴머노이드": {
        "keywords": [
            "로봇",
            "휴머노이드",
        ],
        "seeds": [
            "465610",
            "476250",
        ],
        "reason":
            "AI와 제조 자동화가 결합되면서 산업용·서비스·휴머노이드 로봇으로 관심 범위가 확대되고 있습니다.",
    },

    "방산·항공우주": {
        "keywords": [
            "방산",
            "우주",
            "항공",
        ],
        "seeds": [
            "449450",
            "463250",
        ],
        "reason":
            "국방비 확대와 항공우주 산업의 수주 및 공급망 투자 흐름이 관련 기업과 ETF에 연결됩니다.",
    },

    "조선·해운": {
        "keywords": [
            "조선",
            "해운",
            "운송",
        ],
        "seeds": [
            "139230",
        ],
        "reason":
            "선박 교체 수요와 고부가 선박 중심의 수주 흐름이 국내 조선 공급망에 연결될 수 있습니다.",
    },

    "바이오·헬스케어": {
        "keywords": [
            "바이오",
            "헬스케어",
        ],
        "seeds": [
            "329200",
            "266420",
            "462610",
        ],
        "reason":
            "신약개발과 헬스케어 산업의 기술 진전 및 글로벌 자금 유입 여부를 함께 볼 필요가 있는 테마입니다.",
    },

    "2차전지·ESS": {
        "keywords": [
            "2차전지",
            "배터리",
            "ess",
            "전지",
        ],
        "seeds": [
            "305540",
            "364980",
            "438320",
        ],
        "reason":
            "전기차뿐 아니라 ESS와 전력망 안정화 수요가 배터리 산업의 새로운 수요처로 연결될 수 있습니다.",
    },

    "금·원자재": {
        "keywords": [
            "금",
            "원유",
            "원자재",
        ],
        "seeds": [
            "132030",
            "411060",
            "261220",
        ],
        "reason":
            "금리·달러·지정학적 위험 등 거시 변수에 따라 포트폴리오 방어 및 원자재 노출 수단으로 활용됩니다.",
    },

    "배당·인컴": {
        "keywords": [
            "배당",
            "커버드콜",
            "인컴",
            "고배당",
        ],
        "seeds": [
            "458730",
            "476480",
            "451780",
            "211560",
            "161510",
        ],
        "reason":
            "현금흐름과 변동성 관리가 중요한 구간에서 배당·인컴형 전략의 역할을 점검할 수 있습니다.",
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
# CSS
# ============================================================

st.markdown(
    """
<style>

:root {
    --bg:#070d16;
    --panel:#0d1622;
    --panel2:#111d2b;
    --line:#26374d;
    --text:#f2f6fb;
    --muted:#9aaabd;
    --accent:#5da9ff;
    --red:#ff6575;
    --blue:#65aaff;
    --green:#54d39a;
    --yellow:#f0c86a;
}

html, body, [class*="css"] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

.stApp {
    background:var(--bg);
    color:var(--text);
}

.block-container {
    max-width:1180px;
    padding:0.85rem 1rem 3rem;
}

h1,h2,h3 {
    color:var(--text) !important;
    letter-spacing:-0.04em;
}

h1 {
    font-size:2rem !important;
    margin-bottom:.1rem !important;
}

h2 {
    font-size:1.35rem !important;
}

h3 {
    font-size:1.05rem !important;
}

p {
    color:#d5deea;
}

.stCaption,
[data-testid="stCaptionContainer"] {
    color:var(--muted) !important;
}

.small-muted {
    color:var(--muted);
    font-size:.78rem;
}

.eyebrow {
    color:#75b8ff;
    font-size:.72rem;
    font-weight:800;
    letter-spacing:.12em;
    margin-bottom:2px;
}

/* -----------------------------------------
   buttons
----------------------------------------- */

.stButton > button {
    border-radius:9px;
    border:1px solid #30435b;
    background:#111d2b;
    color:#edf4fb;
    min-height:38px;
    font-weight:650;
}

.stButton > button:hover {
    border-color:#65adff;
    color:#ffffff;
    background:#16263a;
}

/* -----------------------------------------
   input
----------------------------------------- */

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
textarea {
    background:#0d1622 !important;
    border-color:#30435b !important;
    color:#f3f7fb !important;
}

/* -----------------------------------------
   hero
----------------------------------------- */

.hero {
    background:
        linear-gradient(
            135deg,
            #101d2c 0%,
            #0b1420 100%
        );
    border:1px solid #2a3d54;
    border-radius:16px;
    padding:17px 18px;
    margin:8px 0 12px;
}

.hero-name {
    font-size:1.35rem;
    font-weight:800;
    color:#ffffff;
}

.hero-code {
    color:#91a4ba;
    font-size:.76rem;
    margin-top:2px;
}

/* -----------------------------------------
   current price
----------------------------------------- */

.price-hero {
    background:#0c1520;
    border:1px solid #26384d;
    border-radius:15px;
    padding:15px 17px;
    margin:10px 0 12px;
}

.current-label {
    color:#9bacc0;
    font-size:.75rem;
    margin-bottom:2px;
}

.current-price {
    color:#ffffff;
    font-size:2rem;
    font-weight:850;
    letter-spacing:-.05em;
    line-height:1.05;
}

.day-change {
    font-size:1rem;
    font-weight:750;
    margin-top:5px;
}

.change-up {
    color:#ff6878;
}

.change-down {
    color:#68aaff;
}

.change-flat {
    color:#b6c1ce;
}

.indicator-line {
    color:#aebccc;
    font-size:.76rem;
    margin-top:10px;
    line-height:1.6;
}

.indicator-strong {
    color:#e8eef6;
    font-weight:700;
}

/* -----------------------------------------
   judgment
----------------------------------------- */

.judgment {
    background:
        linear-gradient(
            135deg,
            #101c2b,
            #0c1520
        );
    border:1px solid #2a4058;
    border-radius:15px;
    padding:16px;
    margin:10px 0 14px;
}

.judgment-title {
    color:#8fbfff;
    font-size:.72rem;
    font-weight:800;
    letter-spacing:.05em;
}

.judgment-main {
    color:#ffffff;
    font-size:1.22rem;
    font-weight:850;
    margin:3px 0 8px;
}

.reason-row {
    color:#c9d4e1;
    font-size:.79rem;
    line-height:1.5;
    padding:2px 0;
}

.action-box {
    margin-top:13px;
    padding:12px 14px;
    border-left:3px solid #61aaff;
    background:#0a1420;
    border-radius:8px;
}

.action-title {
    color:#75b8ff;
    font-weight:800;
    font-size:.78rem;
    margin-bottom:4px;
}

.action-text {
    color:#eef4fa;
    font-size:.84rem;
    line-height:1.55;
}

/* -----------------------------------------
   price scenarios
----------------------------------------- */

.section-title {
    margin-top:20px;
    margin-bottom:8px;
}

.price-card {
    background:#0d1622;
    border:1px solid #26384d;
    border-radius:12px;
    padding:11px 12px;
    min-height:118px;
}

.price-label {
    color:#93a5b9;
    font-size:.70rem;
    font-weight:700;
}

.price-value {
    color:#ffffff;
    font-size:1.12rem;
    font-weight:850;
    margin:3px 0 4px;
}

.price-why {
    color:#c2cedb;
    font-size:.73rem;
    line-height:1.42;
}

.price-action {
    color:#83bfff;
    font-size:.72rem;
    line-height:1.4;
    margin-top:6px;
}

/* -----------------------------------------
   holding
----------------------------------------- */

.holding-panel {
    background:#0b141f;
    border:1px solid #24364a;
    border-radius:13px;
    padding:12px;
    margin:10px 0;
}

/* -----------------------------------------
   search result
----------------------------------------- */

.search-result {
    background:#0d1723;
    border:1px solid #2a3c51;
    border-radius:11px;
    padding:10px 12px;
    margin:6px 0 8px;
}

.search-name {
    color:#f5f8fc;
    font-weight:750;
    font-size:.91rem;
}

.search-code {
    color:#8fa1b5;
    font-size:.72rem;
    margin-top:2px;
}

/* -----------------------------------------
   watchlist
----------------------------------------- */

.watchlist-panel {
    background:#0b141f;
    border:1px solid #25384d;
    border-radius:13px;
    padding:11px 12px;
    margin:8px 0 12px;
}

/* -----------------------------------------
   theme cards
----------------------------------------- */

.theme-card {
    background:#0c1520;
    border:1px solid #25384b;
    border-radius:13px;
    padding:13px 14px;
    margin:7px 0;
}

.theme-stage {
    color:#78b8ff;
    font-size:.69rem;
    font-weight:800;
    letter-spacing:.04em;
}

.theme-name {
    color:#ffffff;
    font-size:1.04rem;
    font-weight:800;
    margin:2px 0 4px;
}

.theme-reason {
    color:#aebdcd;
    font-size:.76rem;
    line-height:1.5;
    margin-bottom:9px;
}

.etf-mini {
    background:#101b28;
    border:1px solid #26394e;
    border-radius:10px;
    padding:9px;
    min-height:90px;
}

.etf-mini-name {
    color:#eef4fa;
    font-size:.76rem;
    font-weight:700;
    line-height:1.35;
}

.etf-mini-data {
    color:#aebccc;
    font-size:.68rem;
    margin-top:4px;
    line-height:1.45;
}

/* -----------------------------------------
   remove ugly separators / chips
----------------------------------------- */

hr {
    border-color:#1d2b3d;
}

/* -----------------------------------------
   dataframe
----------------------------------------- */

div[data-testid="stDataFrame"] {
    border:1px solid #26384c;
    border-radius:10px;
    overflow:hidden;
}

/* -----------------------------------------
   mobile
----------------------------------------- */

@media (max-width:700px) {

    .block-container {
        padding:.55rem .55rem 2rem;
    }

    h1 {
        font-size:1.55rem !important;
    }

    h2 {
        font-size:1.16rem !important;
    }

    .hero {
        padding:13px;
    }

    .current-price {
        font-size:1.72rem;
    }

    .judgment {
        padding:13px;
    }

    .price-card {
        min-height:105px;
        padding:9px;
    }

    .theme-card {
        padding:11px;
    }

}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# JSON HELPERS
# ============================================================

def safe_read_json(path, default):

    try:
        if not os.path.exists(path):
            return default

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    except Exception:
        return default


def safe_write_json(path, data):

    try:

        with open(path, "w", encoding="utf-8") as f:

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
# ETF CATALOG
# ============================================================

def load_etf_universe():

    combined = {}

    combined.update(BASE_ETFS)
    combined.update(FALLBACK_ETFS)

    cached = safe_read_json(
        ETF_CACHE_FILE,
        {}
    )

    if isinstance(cached, dict):

        timestamp = cached.get(
            "_timestamp",
            0
        )

        items = cached.get(
            "items",
            {}
        )

        try:

            valid_cache = (
                datetime.now().timestamp()
                - float(timestamp)
                <
                ETF_CACHE_HOURS * 3600
            )

        except Exception:

            valid_cache = False

        if (
            valid_cache
            and isinstance(items, dict)
        ):

            for k, v in items.items():

                combined[
                    str(k).zfill(6)
                ] = str(v)

    return combined


def fetch_krx_etf_catalog():

    url = (
        "https://finance.naver.com/api/"
        "sise/etfItemList.nhn"
    )

    try:

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            req,
            timeout=8
        ) as response:

            raw = response.read()

        root = ET.fromstring(raw)

        result = {}

        for item in root.findall(".//item"):

            code = (
                item.attrib
                .get(
                    "itemcode",
                    ""
                )
                .strip()
            )

            name = (
                item.attrib
                .get(
                    "itemname",
                    ""
                )
                .strip()
            )

            if (
                re.fullmatch(
                    r"\d{6}",
                    code
                )
                and name
            ):

                result[code] = name

        if result:

            safe_write_json(
                ETF_CACHE_FILE,
                {
                    "_timestamp":
                        datetime.now().timestamp(),
                    "items":
                        result,
                }
            )

            st.session_state.etf_universe.update(
                result
            )

            return len(result)

    except Exception:
        return 0

    return 0


# ============================================================
# SESSION STATE
# ============================================================

def init_state():

    if "watchlist" not in st.session_state:

        saved = safe_read_json(
            WATCHLIST_FILE,
            DEFAULT_WATCHLIST
        )

        if isinstance(saved, list):

            st.session_state.watchlist = list(
                dict.fromkeys(
                    str(x).zfill(6)
                    for x in saved
                )
            )

        else:

            st.session_state.watchlist = (
                DEFAULT_WATCHLIST.copy()
            )

    if "holdings" not in st.session_state:

        saved = safe_read_json(
            HOLDINGS_FILE,
            {}
        )

        st.session_state.holdings = (
            saved
            if isinstance(saved, dict)
            else {}
        )

    if "etf_universe" not in st.session_state:

        st.session_state.etf_universe = (
            load_etf_universe()
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


init_state()


# ============================================================
# PRICE DATA
# ============================================================

def normalize_df(df):

    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()

    if isinstance(
        out.columns,
        pd.MultiIndex
    ):

        out.columns = [
            c[0]
            if isinstance(c, tuple)
            else c
            for c in out.columns
        ]

    rename = {}

    for c in out.columns:

        lc = str(c).lower()

        if lc == "open":
            rename[c] = "Open"

        elif lc == "high":
            rename[c] = "High"

        elif lc == "low":
            rename[c] = "Low"

        elif lc == "close":
            rename[c] = "Close"

        elif lc == "adj close":
            rename[c] = "Adj Close"

        elif lc == "volume":
            rename[c] = "Volume"

    out = out.rename(
        columns=rename
    )

    needed = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    if not all(
        c in out.columns
        for c in needed
    ):
        return pd.DataFrame()

    out = out[
        needed
    ].dropna(
        subset=["Close"]
    )

    return out


def fetch_naver(code, days=300):

    end = datetime.now()

    start = (
        end
        - timedelta(
            days=max(days * 2, 500)
        )
    )

    url = (
        "https://fchart.stock.naver.com/"
        "sise.nhn?"
        +
        urllib.parse.urlencode(
            {
                "symbol": code,
                "timeframe": "day",
                "startTime":
                    start.strftime("%Y%m%d"),
                "endTime":
                    end.strftime("%Y%m%d"),
                "count": days,
            }
        )
    )

    try:

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            req,
            timeout=8
        ) as response:

            raw = response.read()

        root = ET.fromstring(raw)

        rows = []

        for item in root.findall(".//item"):

            data = item.attrib.get(
                "data",
                ""
            )

            parts = data.split("|")

            if len(parts) >= 6:
                rows.append(parts)

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
            ]
        )

        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )

        for col in [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        df = (
            df
            .dropna()
            .set_index("Date")
            .sort_index()
        )

        return normalize_df(df)

    except Exception:
        return pd.DataFrame()


def fetch_yahoo(code, days=300):

    try:

        ticker = yf.Ticker(
            f"{code}.KS"
        )

        df = ticker.history(
            period="2y",
            auto_adjust=False,
            actions=False
        )

        return normalize_df(
            df.tail(days)
        )

    except Exception:
        return pd.DataFrame()


def load_price_data(
    code,
    days=300,
    force=False
):

    code = str(code).zfill(6)

    now = datetime.now().timestamp()

    cached = (
        st.session_state
        .price_cache
        .get(code)
    )

    if (
        not force
        and cached
    ):

        timestamp, df = cached

        if (
            now - timestamp
            < PRICE_CACHE_TTL
            and isinstance(
                df,
                pd.DataFrame
            )
            and not df.empty
        ):

            return df.copy()

    df = fetch_naver(
        code,
        days
    )

    if df.empty:

        df = fetch_yahoo(
            code,
            days
        )

    if not df.empty:

        st.session_state.price_cache[
            code
        ] = (
            now,
            df.copy()
        )

    return df


# ============================================================
# INDICATORS
# ============================================================

def add_indicators(df):

    if df.empty:
        return df

    d = df.copy()

    close = d["Close"]

    d["MA20"] = (
        close
        .rolling(20)
        .mean()
    )

    d["MA60"] = (
        close
        .rolling(60)
        .mean()
    )

    d["MA120"] = (
        close
        .rolling(120)
        .mean()
    )

    d["STD20"] = (
        close
        .rolling(20)
        .std()
    )

    d["BB_UPPER"] = (
        d["MA20"]
        + 2 * d["STD20"]
    )

    d["BB_LOWER"] = (
        d["MA20"]
        - 2 * d["STD20"]
    )

    delta = close.diff()

    gain = delta.clip(
        lower=0
    )

    loss = -delta.clip(
        upper=0
    )

    avg_gain = (
        gain
        .ewm(
            alpha=1 / 14,
            adjust=False,
            min_periods=14
        )
        .mean()
    )

    avg_loss = (
        loss
        .ewm(
            alpha=1 / 14,
            adjust=False,
            min_periods=14
        )
        .mean()
    )

    rs = (
        avg_gain
        /
        avg_loss.replace(
            0,
            np.nan
        )
    )

    d["RSI"] = (
        100
        -
        (
            100
            /
            (1 + rs)
        )
    )

    d["VOL20"] = (
        d["Volume"]
        .rolling(20)
        .mean()
    )

    d["VOL_RATIO"] = (
        d["Volume"]
        /
        d["VOL20"]
    )

    d["RET1"] = (
        close
        .pct_change(1)
        * 100
    )

    d["RET5"] = (
        close
        .pct_change(5)
        * 100
    )

    d["RET20"] = (
        close
        .pct_change(20)
        * 100
    )

    return d


def last_valid(
    d,
    col,
    default=np.nan
):

    if col not in d.columns:
        return default

    s = d[col].dropna()

    if len(s):
        return s.iloc[-1]

    return default


# ============================================================
# FORMATTERS
# ============================================================

def money(v):

    try:

        if (
            v is None
            or not np.isfinite(v)
        ):
            return "-"

        return f"{v:,.0f}원"

    except Exception:

        return "-"


def pct_text(v):

    try:

        if (
            v is None
            or not np.isfinite(v)
        ):
            return "-"

        return f"{v:+.1f}%"

    except Exception:

        return "-"


def signed_money(v):

    try:

        if (
            v is None
            or not np.isfinite(v)
        ):
            return "-"

        return f"{v:+,.0f}원"

    except Exception:

        return "-"


def safe_float(v, default=np.nan):

    try:

        value = float(v)

        if np.isfinite(value):
            return value

        return default

    except Exception:

        return default


# ============================================================
# PRICE LEVELS
# ============================================================

def calculate_levels(d):

    if d.empty:
        return {}

    close = safe_float(
        d["Close"].iloc[-1]
    )

    ma20 = safe_float(
        last_valid(
            d,
            "MA20",
            close
        ),
        close
    )

    ma60 = safe_float(
        last_valid(
            d,
            "MA60",
            close
        ),
        close
    )

    low20 = safe_float(
        d["Low"]
        .tail(20)
        .min(),
        close
    )

    high20 = safe_float(
        d["High"]
        .tail(20)
        .max(),
        close
    )

    support = min(
        ma60,
        low20
    )

    risk = min(
        support,
        safe_float(
            d["Low"]
            .tail(60)
            .min(),
            support
        )
    )

    return {
        "current": close,
        "first_interest": ma20,
        "support": support,
        "breakout": high20,
        "risk": risk,
    }


def pct(
    a,
    b
):

    try:

        if (
            b in (0, None)
            or not np.isfinite(b)
        ):
            return np.nan

        return (
            a / b - 1
        ) * 100

    except Exception:

        return np.nan


# ============================================================
# JUDGMENT
# ============================================================

def get_judgment(
    d,
    code,
    held=False
):

    if d.empty:

        return (
            "데이터 확인 필요",
            [
                "가격 데이터를 불러오지 못했습니다."
            ],
            "가격 데이터가 확인된 후 다시 판단합니다."
        )

    close = safe_float(
        d["Close"].iloc[-1]
    )

    ma20 = safe_float(
        last_valid(
            d,
            "MA20",
            close
        ),
        close
    )

    ma60 = safe_float(
        last_valid(
            d,
            "MA60",
            close
        ),
        close
    )

    rsi = safe_float(
        last_valid(
            d,
            "RSI",
            50
        ),
        50
    )

    vr = safe_float(
        last_valid(
            d,
            "VOL_RATIO",
            1
        ),
        1
    )

    ret1 = safe_float(
        last_valid(
            d,
            "RET1",
            0
        ),
        0
    )

    ret20 = safe_float(
        last_valid(
            d,
            "RET20",
            0
        ),
        0
    )

    above20 = close >= ma20
    above60 = close >= ma60

    if above20 and above60 and rsi >= 70:

        judgment = "상승 추세 유지 · 과열 여부 확인"

        action = (
            "보유자는 추세 유지 여부를 확인하면서 대응합니다. "
            "신규 접근은 현재가 추격보다 20일선 또는 "
            "1차 지지 가격에서 거래량이 안정되는지 확인하는 "
            "눌림 접근이 우선입니다."
        )

    elif above20 and above60:

        judgment = "상승 추세 유지"

        action = (
            "보유자는 추세가 유지되는 동안 대응하고, "
            "미보유자는 현재가 추격보다 20일선 부근 "
            "눌림과 반등 여부를 확인하는 접근이 적합합니다."
        )

    elif above60 and not above20:

        judgment = "단기 조정 · 중기 추세 확인"

        action = (
            "20일선 회복 전에는 공격적인 신규 진입보다 "
            "지지 확인을 우선합니다. 보유자는 60일선이 "
            "유지되는지를 핵심 기준으로 봅니다."
        )

    elif not above60 and rsi <= 40:

        judgment = "중기 약세 · 방어 우선"

        action = (
            "신규 진입은 서두르기보다 추세 회복을 확인합니다. "
            "보유자는 핵심지지 이탈 여부를 기준으로 "
            "비중과 대응을 재점검합니다."
        )

    else:

        judgment = "방향 확인 구간"

        action = (
            "20일선·60일선의 방향이 명확해질 때까지 "
            "분할 또는 대기 접근을 우선합니다. "
            "거래량을 동반한 돌파 여부가 다음 판단의 핵심입니다."
        )

    trend20 = "상회" if above20 else "하회"
    trend60 = "상회" if above60 else "하회"

    reasons = [
        f"20일선 {trend20} · 60일선 {trend60} → 단기·중기 추세 위치",
        f"RSI {rsi:.0f} → {'과열권 접근' if rsi >= 65 else '중립권' if rsi >= 45 else '약세권'}",
        f"거래량 20일 평균 대비 {vr:.1f}배 → {'거래 증가' if vr >= 1.2 else '평균 수준' if vr >= 0.8 else '거래 감소'}",
        f"당일 {ret1:+.1f}% · 20일 {ret20:+.1f}% → 최근 가격 탄력 확인",
    ]

    if held:

        action = (
            "보유중입니다. "
            + action
        )

    else:

        action = (
            "현재 미보유입니다. "
            + action
        )

    return (
        judgment,
        reasons,
        action
    )


# ============================================================
# SCENARIOS
# ============================================================

def scenario_for(
    level_name,
    price,
    d
):

    close = safe_float(
        d["Close"].iloc[-1]
    )

    distance = pct(
        price,
        close
    )

    if level_name == "1차 눌림":

        return (
            f"현재가 대비 {distance:+.1f}%. "
            "20일선 기준의 단기 추세 확인 가격입니다.",
            "거래량이 안정된 뒤 반등하는지 확인"
        )

    if level_name == "핵심지지":

        return (
            f"현재가 대비 {distance:+.1f}%. "
            "60일선과 최근 저점을 함께 고려한 중기 방어 가격입니다.",
            "지지 반응 확인 후 대응 · 명확한 이탈은 방어 우선"
        )

    if level_name == "돌파기준":

        return (
            f"현재가 대비 {distance:+.1f}%. "
            "최근 20거래일 고점 기준의 돌파 확인 가격입니다.",
            "가격 돌파와 거래량 증가가 함께 나오는지 확인"
        )

    return (
        f"현재가 대비 {distance:+.1f}%. "
        "중기 하단을 깨는 경우 기존 상승 시나리오를 다시 점검합니다.",
        "명확한 이탈 시 추가매수보다 방어를 우선"
    )


def price_cards(d):

    levels = calculate_levels(d)

    if not levels:
        return []

    return [
        (
            "1차 눌림",
            levels["first_interest"],
            "20일선"
        ),
        (
            "핵심지지",
            levels["support"],
            "60일선·최근저점"
        ),
        (
            "돌파기준",
            levels["breakout"],
            "20일 고점"
        ),
        (
            "위험가격",
            levels["risk"],
            "중기 하단"
        ),
    ]


# ============================================================
# THEME MATCHING
# ============================================================

def match_themes(
    code,
    name
):

    text = (
        f"{code} {name}"
        .lower()
    )

    found = []

    for theme, info in THEMES.items():

        if (
            code in info["seeds"]
            or
            any(
                k.lower() in text
                for k in info["keywords"]
            )
        ):

            found.append(theme)

    return found


def theme_snapshot(
    theme,
    limit=4
):

    info = THEMES.get(
        theme,
        {}
    )

    rows = []

    for code in info.get(
        "seeds",
        []
    )[:limit]:

        try:

            name = (
                st.session_state
                .etf_universe
                .get(
                    code,
                    BASE_ETFS.get(
                        code,
                        FALLBACK_ETFS.get(
                            code,
                            code
                        )
                    )
                )
            )

            d = add_indicators(
                load_price_data(
                    code,
                    180
                )
            )

            if d.empty:
                continue

            close = safe_float(
                d["Close"].iloc[-1]
            )

            rsi = safe_float(
                last_valid(
                    d,
                    "RSI",
                    np.nan
                )
            )

            ret20 = safe_float(
                last_valid(
                    d,
                    "RET20",
                    np.nan
                )
            )

            vr = safe_float(
                last_valid(
                    d,
                    "VOL_RATIO",
                    np.nan
                )
            )

            ma20 = safe_float(
                last_valid(
                    d,
                    "MA20",
                    close
                ),
                close
            )

            trend = (
                "상승"
                if close >= ma20
                else "조정"
            )

            rows.append(
                {
                    "code": code,
                    "name": name,
                    "price": close,
                    "ret20": ret20,
                    "rsi": rsi,
                    "vr": vr,
                    "trend": trend,
                }
            )

        except Exception:
            continue

    return rows


def theme_stage(theme):

    for t, stage in FUTURE_CHAIN:

        if t == theme:
            return stage

    return "관심 테마"


# ============================================================
# WATCHLIST
# ============================================================

def save_watchlist():

    safe_write_json(
        WATCHLIST_FILE,
        st.session_state.watchlist
    )


def save_holdings():

    safe_write_json(
        HOLDINGS_FILE,
        st.session_state.holdings
    )


def set_selected(code):

    code = str(code).zfill(6)

    st.session_state.selected_code = code
    st.session_state.main_page = "📊 내 ETF"


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="eyebrow">PREMIUM ETF ANALYSIS</div>',
    unsafe_allow_html=True
)

st.title("📡 ETF RADAR")

st.caption(
    "가격 · 추세 · 거래량을 보고 현재 판단과 대응 가격까지 연결합니다."
)


# ============================================================
# NAVIGATION
# ============================================================

nav = st.radio(
    "메뉴",
    [
        "📊 내 ETF",
        "🔭 미래테마"
    ],
    horizontal=True,
    key="main_page",
    label_visibility="collapsed",
)


# ============================================================
# SEARCH / WATCHLIST
# ============================================================

def render_search_and_watchlist():

    st.markdown(
        "### 🔎 ETF 찾기"
    )

    c1, c2 = st.columns(
        [3.5, 1]
    )

    with c1:

        query = st.text_input(
            "ETF명 또는 종목코드",
            placeholder="AI반도체 / 전력 / 395160",
            key="etf_search_input",
            label_visibility="collapsed",
        )

    with c2:

        refresh = st.button(
            "ETF 목록 갱신",
            key="refresh_etf_catalog",
            use_container_width=True
        )

    if refresh:

        with st.spinner(
            "ETF 목록을 갱신하는 중..."
        ):

            n = fetch_krx_etf_catalog()

        if n > 0:

            st.success(
                f"ETF {n:,}개 목록을 확인했습니다."
            )

        else:

            st.info(
                "외부 목록을 가져오지 못했습니다. "
                "현재 저장된 ETF 목록으로 검색합니다."
            )

    universe = st.session_state.etf_universe

    q = (
        query.strip().lower()
        if query
        else ""
    )

    results = []

    if q:

        for code, name in universe.items():

            if (
                q in code.lower()
                or
                q in name.lower()
            ):

                results.append(
                    (
                        code,
                        name
                    )
                )

        results = results[:30]

    if results:

        st.markdown(
            '<div class="search-result">',
            unsafe_allow_html=True
        )

        options = [
            f"{code} · {name}"
            for code, name in results
        ]

        selected_label = st.selectbox(
            "검색 결과",
            options,
            key="search_result_select",
            label_visibility="collapsed",
        )

        selected_code = (
            selected_label
            .split(
                " · ",
                1
            )[0]
        )

        selected_name = universe.get(
            selected_code,
            "ETF"
        )

        st.markdown(
            f'<div class="search-name">'
            f'{selected_name}'
            f'</div>'
            f'<div class="search-code">'
            f'{selected_code}'
            f'</div>',
            unsafe_allow_html=True
        )

        exists = (
            selected_code
            in st.session_state.watchlist
        )

        if exists:

            st.button(
                "✓ 관심종목에 등록되어 있습니다",
                key=f"already_added_{selected_code}",
                use_container_width=True,
                disabled=True,
            )

        else:

            if st.button(
                "＋ 관심종목에 추가",
                key=f"add_watch_{selected_code}",
                use_container_width=True
            ):

                st.session_state.watchlist.append(
                    selected_code
                )

                st.session_state.watchlist = list(
                    dict.fromkeys(
                        st.session_state.watchlist
                    )
                )

                save_watchlist()

                st.session_state.selected_code = (
                    selected_code
                )

                st.session_state.main_page = (
                    "📊 내 ETF"
                )

                st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    elif q:

        st.info(
            "검색 결과가 없습니다. "
            "ETF명 일부 또는 6자리 종목코드를 입력해 주세요."
        )

    # --------------------------------------------------------
    # WATCHLIST
    # --------------------------------------------------------

    st.markdown(
        "### ⭐ 관심종목"
    )

    if not st.session_state.watchlist:

        st.info(
            "검색에서 ETF를 추가하면 여기에 표시됩니다."
        )

        return

    watch_options = []

    for code in st.session_state.watchlist:

        name = universe.get(
            code,
            BASE_ETFS.get(
                code,
                FALLBACK_ETFS.get(
                    code,
                    "ETF"
                )
            )
        )

        watch_options.append(
            f"{name} · {code}"
        )

    selected_code = st.session_state.selected_code

    current_index = 0

    for i, option in enumerate(
        watch_options
    ):

        if option.endswith(
            f"· {selected_code}"
        ):

            current_index = i
            break

    picked = st.selectbox(
        "관심종목 선택",
        watch_options,
        index=current_index,
        key="watchlist_select_v13",
        label_visibility="collapsed",
    )

    picked_code = (
        picked
        .split(
            " · ",
            1
        )[-1]
        .strip()
    )

    if (
        picked_code
        !=
        st.session_state.selected_code
    ):

        st.session_state.selected_code = (
            picked_code
        )

        st.rerun()

    c1, c2 = st.columns(
        [4, 1]
    )

    with c2:

        if st.button(
            "삭제",
            key=f"remove_watch_{selected_code}",
            use_container_width=True
        ):

            st.session_state.watchlist = [
                x
                for x in st.session_state.watchlist
                if x != selected_code
            ]

            save_watchlist()

            if st.session_state.watchlist:

                st.session_state.selected_code = (
                    st.session_state.watchlist[0]
                )

            else:

                st.session_state.selected_code = (
                    list(BASE_ETFS)[0]
                )

            st.rerun()


# ============================================================
# HOLDING
# ============================================================

def render_holding(
    code,
    current_price
):

    data = (
        st.session_state
        .holdings
        .get(
            code,
            {}
        )
    )

    held = bool(
        data.get(
            "held",
            False
        )
    )

    avg = safe_float(
        data.get(
            "avg_price",
            0
        ),
        0
    )

    qty = safe_float(
        data.get(
            "quantity",
            0
        ),
        0
    )

    st.markdown(
        "### 💼 보유 상태"
    )

    c1, c2 = st.columns(
        [1.2, 3.8]
    )

    with c1:

        status = st.radio(
            "보유 여부",
            [
                "미보유",
                "보유중"
            ],
            index=(
                1 if held else 0
            ),
            horizontal=True,
            key=f"holding_status_v13_{code}",
            label_visibility="collapsed",
        )

    new_held = (
        status == "보유중"
    )

    if not new_held:

        if held:

            st.session_state.holdings[
                code
            ] = {
                "held": False,
                "avg_price": 0,
                "quantity": 0,
            }

            save_holdings()

        with c2:

            st.markdown(
                '<div class="small-muted">'
                '현재 미보유 · 신규 진입 관점으로 판단합니다.'
                '</div>',
                unsafe_allow_html=True
            )

        return False, 0, 0

    with c2:

        h1, h2, h3 = st.columns(3)

        with h1:

            avg_new = st.number_input(
                "평균매수가",
                min_value=0.0,
                value=avg,
                step=100.0,
                key=f"avg_price_v13_{code}"
            )

        with h2:

            qty_new = st.number_input(
                "수량",
                min_value=0.0,
                value=qty,
                step=1.0,
                key=f"quantity_v13_{code}"
            )

        with h3:

            pnl = (
                (
                    current_price
                    - avg_new
                )
                * qty_new
                if avg_new > 0
                else 0
            )

            ret = (
                pct(
                    current_price,
                    avg_new
                )
                if avg_new > 0
                else np.nan
            )

            st.metric(
                "평가손익",
                (
                    f"{pnl:+,.0f}원"
                    if avg_new > 0
                    else "-"
                ),
                (
                    f"{ret:+.1f}%"
                    if np.isfinite(ret)
                    else None
                )
            )

    new_data = {
        "held": True,
        "avg_price": avg_new,
        "quantity": qty_new,
    }

    if new_data != data:

        st.session_state.holdings[
            code
        ] = new_data

        save_holdings()

    return (
        True,
        avg_new,
        qty_new
    )


# ============================================================
# CURRENT PRICE
# ============================================================

def render_current_price(
    d,
    code,
    name
):

    current = safe_float(
        d["Close"].iloc[-1]
    )

    previous = (
        safe_float(
            d["Close"].iloc[-2]
        )
        if len(d) >= 2
        else current
    )

    change = (
        current - previous
    )

    change_pct = pct(
        current,
        previous
    )

    rsi = safe_float(
        last_valid(
            d,
            "RSI",
            np.nan
        )
    )

    vr = safe_float(
        last_valid(
            d,
            "VOL_RATIO",
            np.nan
        )
    )

    ma20 = safe_float(
        last_valid(
            d,
            "MA20",
            current
        ),
        current
    )

    ma60 = safe_float(
        last_valid(
            d,
            "MA60",
            current
        ),
        current
    )

    if change > 0:

        change_class = "change-up"
        arrow = "▲"

    elif change < 0:

        change_class = "change-down"
        arrow = "▼"

    else:

        change_class = "change-flat"
        arrow = "—"

    st.markdown(
        '<div class="price-hero">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="current-label">'
        '현재가'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="current-price">'
        f'{money(current)}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="day-change {change_class}">'
        f'{arrow} {signed_money(change)} '
        f'({pct_text(change_pct)})'
        f'</div>',
        unsafe_allow_html=True
    )

    ma20_text = (
        "20일선 위"
        if current >= ma20
        else "20일선 아래"
    )

    ma60_text = (
        "60일선 위"
        if current >= ma60
        else "60일선 아래"
    )

    rsi_text = (
        f"RSI {rsi:.0f}"
        if np.isfinite(rsi)
        else "RSI -"
    )

    vol_text = (
        f"거래량 20일 평균 대비 {vr:.1f}배"
        if np.isfinite(vr)
        else "거래량 -"
    )

    st.markdown(
        f'<div class="indicator-line">'
        f'<span class="indicator-strong">'
        f'{rsi_text}'
        f'</span>'
        f' · '
        f'<span class="indicator-strong">'
        f'{vol_text}'
        f'</span>'
        f' · '
        f'<span class="indicator-strong">'
        f'{ma20_text}'
        f'</span>'
        f' · '
        f'<span class="indicator-strong">'
        f'{ma60_text}'
        f'</span>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    return current


# ============================================================
# CURRENT JUDGMENT
# ============================================================

def render_judgment(
    d,
    code,
    held
):

    judgment, reasons, action = (
        get_judgment(
            d,
            code,
            held
        )
    )

    st.markdown(
        '<div class="section-title">'
        '### 🎯 현재 판단 · 지금 대응'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="judgment">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="judgment-title">'
        'CURRENT JUDGMENT'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="judgment-main">'
        f'{judgment}'
        f'</div>',
        unsafe_allow_html=True
    )

    for reason in reasons:

        st.markdown(
            f'<div class="reason-row">'
            f'• {reason}'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="action-box">'
        '<div class="action-title">'
        '지금 대응'
        '</div>'
        '<div class="action-text">',
        unsafe_allow_html=True
    )

    st.markdown(
        action
    )

    st.markdown(
        '</div></div></div>',
        unsafe_allow_html=True
    )


# ============================================================
# PRICE SCENARIOS
# ============================================================

def render_price_scenarios(d):

    st.markdown(
        '<div class="section-title">'
        '### 💰 핵심가격 · 대응 시나리오'
        '</div>',
        unsafe_allow_html=True
    )

    cards = price_cards(d)

    if not cards:
        return

    cols = st.columns(
        len(cards)
    )

    for col, item in zip(
        cols,
        cards
    ):

        label, price, why_short = item

        with col:

            why, action = scenario_for(
                label,
                price,
                d
            )

            st.markdown(
                '<div class="price-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="price-label">'
                f'{label} · {why_short}'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="price-value">'
                f'{money(price)}'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="price-why">'
                f'{why}'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="price-action">'
                f'→ {action}'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )


# ============================================================
# CHART
# ============================================================

def render_chart(
    d,
    code,
    name
):

    st.markdown(
        '<div class="section-title">'
        '### 📈 가격 차트'
        '</div>',
        unsafe_allow_html=True
    )

    # 최근 180일을 표시하여 모바일에서 가격 움직임이
    # 너무 압축되지 않도록 함
    chart_df = d.tail(180).copy()

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=chart_df.index,
            open=chart_df["Open"],
            high=chart_df["High"],
            low=chart_df["Low"],
            close=chart_df["Close"],
            name="가격",
            increasing_line_color="#ff6575",
            decreasing_line_color="#65aaff",
            increasing_fillcolor="#ff6575",
            decreasing_fillcolor="#65aaff",
        )
    )

    # 20일선
    if "MA20" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["MA20"],
                mode="lines",
                name="20일선",
                line=dict(
                    width=1.6,
                    color="#f0c86a"
                )
            )
        )

    # 60일선
    if "MA60" in chart_df.columns:

        fig.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["MA60"],
                mode="lines",
                name="60일선",
                line=dict(
                    width=1.4,
                    color="#72b7ff"
                )
            )
        )

    fig.update_layout(

        height=560,

        margin=dict(
            l=5,
            r=5,
            t=25,
            b=5
        ),

        template="plotly_dark",

        paper_bgcolor="#070d16",
        plot_bgcolor="#070d16",

        xaxis_rangeslider_visible=False,

        dragmode="pan",

        hovermode="x unified",

        showlegend=True,

        legend=dict(
            orientation="h",
            y=1.02,
            x=0,
            font=dict(
                size=10
            )
        ),

        xaxis=dict(
            showgrid=True,
            gridcolor="#172638",
            rangeslider=dict(
                visible=False
            )
        ),

        yaxis=dict(
            showgrid=True,
            gridcolor="#172638",
            fixedrange=False
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": True,
            "displaylogo": False,
            "responsive": True,
            "modeBarButtonsToRemove": [
                "lasso2d",
                "select2d",
            ],
        },
        key=f"price_chart_{code}"
    )

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    vol = go.Figure()

    volume_colors = np.where(
        chart_df["Close"] >= chart_df["Open"],
        "#ff6575",
        "#65aaff"
    )

    vol.add_trace(
        go.Bar(
            x=chart_df.index,
            y=chart_df["Volume"],
            name="거래량",
            marker_color=volume_colors,
        )
    )

    if "VOL20" in chart_df.columns:

        vol.add_trace(
            go.Scatter(
                x=chart_df.index,
                y=chart_df["VOL20"],
                mode="lines",
                name="20일 평균",
                line=dict(
                    width=1.3,
                    color="#f0c86a"
                )
            )
        )

    vol.update_layout(

        height=145,

        margin=dict(
            l=5,
            r=5,
            t=8,
            b=5
        ),

        template="plotly_dark",

        paper_bgcolor="#070d16",
        plot_bgcolor="#070d16",

        xaxis_rangeslider_visible=False,

        showlegend=False,

        xaxis=dict(
            showgrid=False
        ),

        yaxis=dict(
            showgrid=True,
            gridcolor="#172638"
        )
    )

    st.plotly_chart(
        vol,
        use_container_width=True,
        config={
            "scrollZoom": False,
            "displaylogo": False,
            "responsive": True,
        },
        key=f"volume_chart_{code}"
    )


# ============================================================
# MY ETF
# ============================================================

def render_my_etf():

    render_search_and_watchlist()

    code = (
        st.session_state.selected_code
    )

    name = (
        st.session_state
        .etf_universe
        .get(
            code,
            BASE_ETFS.get(
                code,
                FALLBACK_ETFS.get(
                    code,
                    "ETF"
                )
            )
        )
    )

    d = add_indicators(
        load_price_data(
            code,
            300
        )
    )

    if d.empty:

        st.error(
            f"{name} ({code}) 가격 데이터를 불러오지 못했습니다."
        )

        st.info(
            "네트워크 또는 외부 금융 데이터 제공처 문제일 수 있습니다. "
            "잠시 후 다시 조회해 주세요."
        )

        return

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.markdown(
        '<div class="hero">',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="hero-name">'
        f'{name}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="hero-code">'
        f'{code} · 기준일 '
        f'{d.index[-1].strftime("%Y-%m-%d")}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # CURRENT PRICE + INDICATORS
    # --------------------------------------------------------

    current = render_current_price(
        d,
        code,
        name
    )

    # --------------------------------------------------------
    # HOLDING
    # --------------------------------------------------------

    held, avg, qty = render_holding(
        code,
        current
    )

    # --------------------------------------------------------
    # JUDGMENT
    # --------------------------------------------------------

    render_judgment(
        d,
        code,
        held
    )

    # --------------------------------------------------------
    # CORE PRICE
    # --------------------------------------------------------

    render_price_scenarios(
        d
    )

    # --------------------------------------------------------
    # CHART
    # --------------------------------------------------------

    render_chart(
        d,
        code,
        name
    )


# ============================================================
# FUTURE THEME CARD
# ============================================================

def render_theme_card(
    theme,
    stage
):

    info = THEMES.get(
        theme,
        {}
    )

    if not info:
        return

    # 안전한 예외 처리
    try:

        rows = theme_snapshot(
            theme,
            limit=4
        )

    except Exception:

        rows = []

    st.markdown(
        '<div class="theme-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="theme-stage">'
        f'{stage}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="theme-name">'
        f'{theme}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="theme-reason">'
        f'{info.get("reason", "")}'
        f'</div>',
        unsafe_allow_html=True
    )

    if rows:

        cols = st.columns(
            len(rows)
        )

        for i, item in enumerate(rows):

            with cols[i]:

                st.markdown(
                    '<div class="etf-mini">',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div class="etf-mini-name">'
                    f'{item["name"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                rsi = item["rsi"]

                rsi_text = (
                    f"{rsi:.0f}"
                    if np.isfinite(rsi)
                    else "-"
                )

                vr = item["vr"]

                vr_text = (
                    f"{vr:.1f}배"
                    if np.isfinite(vr)
                    else "-"
                )

                st.markdown(
                    f'<div class="etf-mini-data">'
                    f'{money(item["price"])}'
                    f' · 20일 {pct_text(item["ret20"])}'
                    f'<br>'
                    f'RSI {rsi_text}'
                    f' · 거래량 {vr_text}'
                    f' · {item["trend"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )

                if st.button(
                    "ETF 분석",
                    key=(
                        "theme_analysis_v13_"
                        + re.sub(
                            r"[^0-9A-Za-z가-힣]+",
                            "_",
                            theme
                        )
                        + "_"
                        + item["code"]
                    ),
                    use_container_width=True
                ):

                    # ------------------------------------------------
                    # 중요:
                    # 미래테마에서 분석을 누르면
                    # 선택 ETF만 저장하고 바로 내 ETF로 이동
                    # ------------------------------------------------

                    st.session_state.selected_code = (
                        item["code"]
                    )

                    st.session_state.main_page = (
                        "📊 내 ETF"
                    )

                    st.rerun()

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )

    else:

        st.caption(
            "대표 ETF 가격 데이터를 불러오지 못했습니다."
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# FUTURE THEME PAGE
# ============================================================

def render_future_themes():

    st.markdown(
        '<div class="hero">',
        unsafe_allow_html=True
    )

    st.markdown(
        "## 🔭 미래테마 레이더"
    )

    st.markdown(
        "현재 주도 → 다음 수혜 → 관심 확대 흐름을 보고 "
        "대표 ETF 분석으로 바로 이동합니다."
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(
        [1.2, 4]
    )

    with c1:

        if st.button(
            "시장 데이터 새로고침",
            key="theme_refresh_v13",
            use_container_width=True
        ):

            st.session_state.price_cache = {}
            st.session_state.theme_cache = {}

            with st.spinner(
                "시장 데이터를 다시 확인하는 중..."
            ):

                fetch_krx_etf_catalog()

            st.rerun()

    with c2:

        st.caption(
            "테마 단계는 투자 권유가 아니라 가격·추세·거래량을 "
            "기준으로 현재 흐름을 탐색하기 위한 분류입니다."
        )

    # --------------------------------------------------------
    # FLOW
    # --------------------------------------------------------

    st.markdown(
        "### 현재 → 다음 흐름"
    )

    for theme, stage in FUTURE_CHAIN:

        render_theme_card(
            theme,
            stage
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    st.markdown(
        "### 📋 미래테마 한눈에 보기"
    )

    table_rows = []

    for theme, stage in FUTURE_CHAIN:

        try:

            rows = theme_snapshot(
                theme,
                limit=1
            )

        except Exception:

            rows = []

        if rows:

            top = rows[0]

            rsi = top["rsi"]

            vr = top["vr"]

            table_rows.append(
                {
                    "상태": stage,
                    "테마": theme,
                    "대표 ETF": top["name"],
                    "현재가": money(
                        top["price"]
                    ),
                    "20일": pct_text(
                        top["ret20"]
                    ),
                    "RSI": (
                        f"{rsi:.0f}"
                        if np.isfinite(rsi)
                        else "-"
                    ),
                    "거래량": (
                        f"{vr:.1f}배"
                        if np.isfinite(vr)
                        else "-"
                    ),
                }
            )

        else:

            table_rows.append(
                {
                    "상태": stage,
                    "테마": theme,
                    "대표 ETF": "-",
                    "현재가": "-",
                    "20일": "-",
                    "RSI": "-",
                    "거래량": "-",
                }
            )

    if table_rows:

        st.dataframe(
            pd.DataFrame(
                table_rows
            ),
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # ALL THEMES
    # --------------------------------------------------------

    st.markdown(
        "### 전체 테마 탐색"
    )

    theme = st.selectbox(
        "테마 선택",
        list(THEMES.keys()),
        key="all_theme_selector_v13",
        label_visibility="collapsed"
    )

    if theme not in [
        x[0]
        for x in FUTURE_CHAIN
    ]:

        render_theme_card(
            theme,
            theme_stage(theme)
        )


# ============================================================
# MAIN
# ============================================================

try:

    if nav == "📊 내 ETF":

        render_my_etf()

    else:

        render_future_themes()

except Exception:

    # 사용자에게 Python traceback을 노출하지 않음
    st.error(
        "화면을 구성하는 과정에서 문제가 발생했습니다."
    )

    st.info(
        "페이지를 새로고침하거나 잠시 후 다시 시도해 주세요."
    )