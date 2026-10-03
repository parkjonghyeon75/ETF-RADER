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
# ETF RADAR v12
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


# ============================================================
# FUTURE THEME FLOW
# ============================================================

FUTURE_CHAIN = [
    ("AI 반도체", "🔥 현재 주도"),
    ("데이터센터·AI 인프라", "➡️ 다음 수혜"),
    ("전력 인프라", "➡️ 다음 수혜"),
    ("원자력", "👀 관심 확대"),
    ("냉각·열관리", "🌱 초기 관심"),
]


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

:root {
    --bg:#07101d;
    --panel:#0d1726;
    --panel2:#111e30;
    --line:#203149;
    --text:#edf3fa;
    --muted:#8fa0b5;
    --accent:#57a6ff;
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
    padding:1rem 1rem 3rem;
}

h1,h2,h3 {
    letter-spacing:-0.04em;
}

h1 {
    font-size:2rem !important;
    margin-bottom:.15rem !important;
}

h2 {
    font-size:1.35rem !important;
}

h3 {
    font-size:1.05rem !important;
}

div[data-testid="stMetric"] {
    background:var(--panel);
    border:1px solid var(--line);
    border-radius:14px;
    padding:10px 12px;
}

div[data-testid="stMetricLabel"] {
    color:var(--muted);
    font-size:.72rem;
}

div[data-testid="stMetricValue"] {
    color:var(--text);
    font-size:1.05rem;
}

.stButton > button {
    border-radius:10px;
    border:1px solid var(--line);
    background:var(--panel2);
    color:var(--text);
    min-height:38px;
}

.stButton > button:hover {
    border-color:var(--accent);
    color:white;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
textarea {
    background:var(--panel) !important;
    border-color:var(--line) !important;
}

div[data-testid="stRadio"] label {
    color:var(--text);
}

div[data-testid="stExpander"] {
    background:var(--panel);
    border:1px solid var(--line);
    border-radius:14px;
}

hr {
    border-color:var(--line);
}

.small-muted {
    color:var(--muted);
    font-size:.78rem;
}

.eyebrow {
    color:var(--accent);
    font-size:.75rem;
    font-weight:700;
    letter-spacing:.08em;
}

.hero {
    background:
        linear-gradient(
            135deg,
            #0e1c2e,
            #0b1523
        );
    border:1px solid var(--line);
    border-radius:18px;
    padding:18px;
    margin:8px 0 14px;
}

.judgment {
    background:
        linear-gradient(
            135deg,
            #101e31,
            #0c1725
        );
    border:1px solid #29425f;
    border-radius:16px;
    padding:16px;
    margin:12px 0;
}

.action-box {
    border-left:3px solid var(--accent);
    background:#0b1726;
    padding:12px 14px;
    border-radius:10px;
}

.price-card {
    background:var(--panel);
    border:1px solid var(--line);
    border-radius:13px;
    padding:12px;
    min-height:145px;
}

.price-label {
    color:var(--muted);
    font-size:.72rem;
}

.price-value {
    font-size:1.15rem;
    font-weight:750;
    margin:.15rem 0 .3rem;
}

.price-why {
    font-size:.78rem;
    line-height:1.45;
    color:#c7d3e2;
}

.price-action {
    font-size:.78rem;
    color:#8fc5ff;
    margin-top:.4rem;
}

.theme-card {
    background:var(--panel);
    border:1px solid var(--line);
    border-radius:16px;
    padding:16px;
    margin:10px 0;
}

.stage {
    font-size:.78rem;
    font-weight:800;
}

.theme-name {
    font-size:1.2rem;
    font-weight:800;
    margin:4px 0;
}

.chip {
    display:inline-block;
    background:#14263b;
    border:1px solid #263e59;
    color:#bcdcff;
    border-radius:999px;
    padding:3px 8px;
    font-size:.7rem;
    margin:2px 3px 2px 0;
}

@media (max-width:700px) {

    .block-container {
        padding:.65rem .65rem 2rem;
    }

    h1 {
        font-size:1.55rem !important;
    }

    h2 {
        font-size:1.15rem !important;
    }

    .hero {
        padding:14px;
    }

    div[data-testid="stMetricValue"] {
        font-size:.92rem;
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

        if valid_cache and isinstance(items, dict):

            combined.update(
                {
                    str(k).zfill(6): str(v)
                    for k, v in items.items()
                }
            )

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
            },
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
                .get("itemcode", "")
                .strip()
            )

            name = (
                item.attrib
                .get("itemname", "")
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
        pass

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

            st.session_state.watchlist = [
                str(x).zfill(6)
                for x in saved
            ]

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

        for item in root.findall(
            ".//item"
        ):

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
            ],
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
    days=300
):

    code = str(code).zfill(6)

    now = datetime.now().timestamp()

    cached = (
        st.session_state
        .price_cache
        .get(code)
    )

    if cached:

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
# PRICE LEVELS
# ============================================================

def calculate_levels(d):

    if d.empty:
        return {}

    close = float(
        d["Close"].iloc[-1]
    )

    ma20 = float(
        last_valid(
            d,
            "MA20",
            close
        )
    )

    ma60 = float(
        last_valid(
            d,
            "MA60",
            close
        )
    )

    low20 = float(
        d["Low"]
        .tail(20)
        .min()
    )

    high20 = float(
        d["High"]
        .tail(20)
        .max()
    )

    if np.isfinite(ma60):

        support = min(
            ma60,
            low20
        )

    else:
        support = low20

    risk = min(
        support,
        float(
            d["Low"]
            .tail(60)
            .min()
        )
    )

    return {

        "current":
            close,

        "first_interest":
            ma20,

        "support":
            support,

        "breakout":
            high20,

        "risk":
            risk,
    }


def pct(
    a,
    b
):

    if (
        b in (0, None)
        or not np.isfinite(b)
    ):
        return np.nan

    return (
        a / b - 1
    ) * 100


# ============================================================
# JUDGMENT
# ============================================================

def get_judgment(
    d,
    code
):

    if d.empty:

        return (
            "데이터 확인 필요",
            [
                "가격 데이터를 불러오지 못했습니다."
            ],
            "잠시 후 다시 조회해 주세요."
        )

    close = float(
        d["Close"].iloc[-1]
    )

    ma20 = float(
        last_valid(
            d,
            "MA20",
            close
        )
    )

    ma60 = float(
        last_valid(
            d,
            "MA60",
            close
        )
    )

    rsi = float(
        last_valid(
            d,
            "RSI",
            50
        )
    )

    vr = float(
        last_valid(
            d,
            "VOL_RATIO",
            1
        )
    )

    ret20 = float(
        last_valid(
            d,
            "RET20",
            0
        )
    )

    above20 = (
        close >= ma20
    )

    above60 = (
        close >= ma60
    )

    if (
        above20
        and above60
        and rsi >= 70
    ):

        judgment = (
            "추세 양호 · 추격 주의"
        )

        action = (
            "보유자는 추세를 따라가되 "
            "추가매수는 눌림 확인 후, "
            "미보유자는 돌파 추격보다 "
            "20일선 부근 확인을 우선합니다."
        )

    elif (
        above20
        and above60
    ):

        judgment = (
            "상승 추세 유지"
        )

        action = (
            "보유자는 추세 유지 여부를 "
            "보면서 대응하고, 미보유자는 "
            "눌림이 나올 때 20일선 지지 "
            "여부를 확인합니다."
        )

    elif (
        above60
        and not above20
    ):

        judgment = (
            "단기 조정 · 중기 추세 확인"
        )

        action = (
            "20일선 회복 전에는 공격적인 "
            "진입보다 지지 확인을 우선하고, "
            "보유자는 60일선 이탈 여부를 "
            "확인합니다."
        )

    elif (
        not above60
        and rsi <= 40
    ):

        judgment = (
            "중기 약세 · 방어 우선"
        )

        action = (
            "신규 진입은 서두르지 말고 "
            "추세 회복을 확인합니다. "
            "보유자는 핵심지지 이탈 여부를 "
            "기준으로 대응합니다."
        )

    else:

        judgment = (
            "방향 확인 구간"
        )

        action = (
            "거래량을 동반한 돌파 또는 "
            "핵심지지 반응이 확인될 때까지 "
            "분할·대기 접근을 우선합니다."
        )

    reasons = [

        (
            f"20일선 "
            f"{'위' if above20 else '아래'}: "
            f"단기 추세는 "
            f"{'유지' if above20 else '조정'} "
            f"상태입니다."
        ),

        (
            f"60일선 "
            f"{'위' if above60 else '아래'}: "
            f"중기 추세는 "
            f"{'방어' if above60 else '약화'} "
            f"상태입니다."
        ),

        (
            f"RSI {rsi:.0f} · "
            f"거래량 {vr:.1f}배 · "
            f"20일 수익률 {ret20:+.1f}%로 "
            f"현재 탄력도를 확인할 수 있습니다."
        ),
    ]

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

    close = float(
        d["Close"].iloc[-1]
    )

    distance = pct(
        close,
        price
    )

    if level_name == "1차 관심가격":

        return (

            f"현재가 대비 "
            f"{distance:+.1f}%. "
            f"20일선 부근이라 눌림이 나온다면 "
            f"단기 추세가 살아있는지 확인하는 가격입니다.",

            "접근 시 거래량 감소 후 반등하는지 확인"
        )

    if level_name == "핵심지지":

        return (

            f"현재가 대비 "
            f"{distance:+.1f}%. "
            f"60일선·최근 저점을 함께 고려한 "
            f"중기 방어선입니다.",

            "이탈 시 보수적으로 비중과 추세를 재점검"
        )

    if level_name == "돌파기준":

        return (

            f"현재가 대비 "
            f"{distance:+.1f}%. "
            f"최근 20거래일 고점 기준으로 "
            f"매물 부담을 넘어서는 가격입니다.",

            "돌파 + 거래량 증가가 함께 나오는지 확인"
        )

    return (

        f"현재가 대비 "
        f"{distance:+.1f}%. "
        f"중기 하단을 깨면 기존 상승 시나리오를 "
        f"다시 봐야 하는 가격입니다.",

        "명확한 이탈이면 추가매수보다 방어를 우선"
    )


def price_cards(d):

    levels = calculate_levels(d)

    if not levels:
        return []

    return [

        (
            "1차 관심가격",
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


def theme_snapshot(theme):

    info = THEMES.get(
        theme,
        {}
    )

    rows = []

    for code in info.get(
        "seeds",
        []
    )[:5]:

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

        close = float(
            d["Close"].iloc[-1]
        )

        rsi = last_valid(
            d,
            "RSI",
            np.nan
        )

        ret20 = last_valid(
            d,
            "RET20",
            np.nan
        )

        vr = last_valid(
            d,
            "VOL_RATIO",
            np.nan
        )

        ma20 = last_valid(
            d,
            "MA20",
            close
        )

        trend = (
            "상승"
            if close >= ma20
            else
            "조정"
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

    return rows


def theme_stage(theme):

    for t, stage in FUTURE_CHAIN:

        if t == theme:
            return stage

    return "관심 테마"


# ============================================================
# UI HELPERS
# ============================================================

def money(v):

    if (
        v is None
        or not np.isfinite(v)
    ):
        return "-"

    return f"{v:,.0f}원"


def pct_text(v):

    if (
        v is None
        or not np.isfinite(v)
    ):
        return "-"

    return f"{v:+.1f}%"


def render_theme_chips(
    code,
    name
):

    themes = match_themes(
        code,
        name
    )

    if themes:

        html = " ".join(
            f'<span class="chip">{t}</span>'
            for t in themes
        )

        st.markdown(
            html,
            unsafe_allow_html=True
        )


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

    st.session_state.selected_code = code
    st.session_state.main_page = "📊 내 ETF"


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="eyebrow">'
    'PREMIUM ETF ANALYSIS'
    '</div>',
    unsafe_allow_html=True
)

st.title("📡 ETF RADAR")

st.caption(
    "가격·추세·거래량을 한 화면에서 보고, "
    "지금의 대응까지 바로 연결합니다."
)


# ============================================================
# MAIN NAVIGATION
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
# ETF SEARCH
# ============================================================

def render_search_and_watchlist():

    st.markdown(
        "### 🔎 ETF 찾기 · 관심종목 추가"
    )

    c1, c2 = st.columns(
        [3, 1]
    )

    with c1:

        query = st.text_input(
            "ETF명 또는 6자리 종목코드",
            placeholder=(
                "예: AI반도체 / 395160 / 전력"
            ),
            key="etf_search_input",
            label_visibility="collapsed",
        )

    with c2:

        refresh = st.button(
            "🔄 ETF 목록 갱신",
            use_container_width=True
        )

    if refresh:

        with st.spinner(
            "ETF 목록을 다시 탐색하고 있습니다..."
        ):

            n = fetch_krx_etf_catalog()

        if n:

            st.success(
                f"ETF 목록 {n:,}개를 확인했습니다."
            )

        else:

            st.info(
                "외부 ETF 목록을 가져오지 못해 "
                "기본 목록으로 계속 검색합니다."
            )

    universe = (
        st.session_state
        .etf_universe
    )

    q = (
        query
        or ""
    ).strip().lower()

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

    selected_search_code = None

    if results:

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

        selected_search_code = (
            selected_label
            .split(
                " · ",
                1
            )[0]
        )

        c1, c2 = st.columns(
            [3, 1]
        )

        with c1:

            st.caption(
                "선택: "
                f"{selected_search_code} · "
                f"{universe[selected_search_code]}"
            )

        with c2:

            exists = (
                selected_search_code
                in st.session_state.watchlist
            )

            if st.button(
                (
                    "✓ 관심종목 등록됨"
                    if exists
                    else
                    "＋ 관심종목 추가"
                ),
                key=f"add_{selected_search_code}",
                use_container_width=True,
                disabled=exists,
            ):

                if (
                    selected_search_code
                    not in st.session_state.watchlist
                ):

                    st.session_state.watchlist.append(
                        selected_search_code
                    )

                    save_watchlist()

                set_selected(
                    selected_search_code
                )

                st.rerun()

    elif q:

        st.info(
            "검색 결과가 없습니다. "
            "ETF명 일부 또는 6자리 종목코드를 입력해 보세요."
        )

    # ========================================================
    # WATCHLIST
    # ========================================================

    if st.session_state.watchlist:

        st.markdown(
            "### ⭐ 내 관심 ETF"
        )

        watch_options = []

        for code in (
            st.session_state.watchlist
        ):

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
                f"{code} · {name}"
            )

        current = (
            st.session_state
            .selected_code
        )

        current_label = next(
            (
                x
                for x in watch_options
                if x.startswith(
                    current + " · "
                )
            ),
            watch_options[0]
        )

        picked = st.selectbox(
            "관심 ETF 선택",
            watch_options,
            index=watch_options.index(
                current_label
            ),
            key="watchlist_select",
            label_visibility="collapsed",
        )

        picked_code = (
            picked
            .split(
                " · ",
                1
            )[0]
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

        rc1, rc2 = st.columns(
            [4, 1]
        )

        with rc2:

            if st.button(
                "삭제",
                key=(
                    "remove_"
                    + st.session_state.selected_code
                ),
                use_container_width=True
            ):

                code = (
                    st.session_state
                    .selected_code
                )

                st.session_state.watchlist = [
                    x
                    for x
                    in st.session_state.watchlist
                    if x != code
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

    avg = float(
        data.get(
            "avg_price",
            0
        )
        or 0
    )

    qty = float(
        data.get(
            "quantity",
            0
        )
        or 0
    )

    st.markdown(
        "### 💼 보유 상태"
    )

    col1, col2 = st.columns(
        [1.1, 2.9]
    )

    with col1:

        status = st.radio(
            "보유 여부",
            [
                "미보유",
                "보유중"
            ],
            index=(
                1
                if held
                else 0
            ),
            horizontal=True,
            key=f"holding_status_{code}",
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

        with col2:

            st.markdown(
                '<div class="small-muted">'
                '미보유 · 신규 진입 기준으로 판단합니다.'
                '</div>',
                unsafe_allow_html=True
            )

        return False, 0, 0

    with col2:

        h1, h2, h3 = st.columns(3)

        with h1:

            avg_new = st.number_input(
                "평균매수가",
                min_value=0.0,
                value=avg,
                step=100.0,
                key=f"avg_{code}"
            )

        with h2:

            qty_new = st.number_input(
                "수량",
                min_value=0.0,
                value=qty,
                step=1.0,
                key=f"qty_{code}"
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
# CURRENT JUDGMENT
# ============================================================

def render_judgment(
    d,
    code,
    held
):

    name = (
        st.session_state
        .etf_universe
        .get(
            code,
            "ETF"
        )
    )

    judgment, reasons, action = (
        get_judgment(
            d,
            code
        )
    )

    st.markdown(
        "### 🎯 현재 판단 · 지금 대응"
    )

    st.markdown(
        '<div class="judgment">',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(
        [1.05, 1.95]
    )

    with c1:

        st.markdown(
            '<div class="small-muted">'
            '현재 판단'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"### {judgment}"
        )

        st.markdown(
            f'<div class="small-muted">'
            f'{name} · {code}'
            f'</div>',
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            "**판단 근거**"
        )

        for reason in reasons:

            st.markdown(
                f"- {reason}"
            )

    st.markdown(
        '<div class="action-box">',
        unsafe_allow_html=True
    )

    st.markdown(
        "**지금 대응**"
    )

    st.markdown(
        action
    )

    st.markdown(
        "</div></div>",
        unsafe_allow_html=True
    )


# ============================================================
# CORE PRICE + SCENARIO
# ============================================================

def render_price_scenarios(d):

    st.markdown(
        "### 💰 핵심가격 · 대응 시나리오"
    )

    cards = price_cards(d)

    cols = st.columns(4)

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
        "### 📈 가격 차트"
    )

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=d.index,
            open=d["Open"],
            high=d["High"],
            low=d["Low"],
            close=d["Close"],
            name="가격",
        )
    )

    for col, label in [
        ("MA20", "20일선"),
        ("MA60", "60일선"),
        ("BB_UPPER", "BB 상단"),
        ("BB_LOWER", "BB 하단"),
    ]:

        if col in d.columns:

            fig.add_trace(
                go.Scatter(
                    x=d.index,
                    y=d[col],
                    mode="lines",
                    name=label,
                    line=dict(
                        width=1.2
                    ),
                )
            )

    fig.update_layout(

        height=480,

        margin=dict(
            l=10,
            r=10,
            t=30,
            b=10,
        ),

        template="plotly_dark",

        paper_bgcolor="#07101d",
        plot_bgcolor="#07101d",

        xaxis_rangeslider_visible=False,

        dragmode="pan",

        hovermode="x unified",

        legend=dict(
            orientation="h",
            y=1.02,
            x=0,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": False,
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "lasso2d",
                "select2d",
            ],
        },
    )

    vol = go.Figure()

    vol.add_trace(
        go.Bar(
            x=d.index,
            y=d["Volume"],
            name="거래량",
        )
    )

    if "VOL20" in d.columns:

        vol.add_trace(
            go.Scatter(
                x=d.index,
                y=d["VOL20"],
                mode="lines",
                name="20일 평균",
            )
        )

    vol.update_layout(

        height=180,

        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10,
        ),

        template="plotly_dark",

        paper_bgcolor="#07101d",
        plot_bgcolor="#07101d",

        xaxis_rangeslider_visible=False,

        showlegend=False,
    )

    st.plotly_chart(
        vol,
        use_container_width=True,
        config={
            "scrollZoom": False,
            "displaylogo": False,
        },
    )


# ============================================================
# MY ETF PAGE
# ============================================================

def render_my_etf():

    render_search_and_watchlist()

    code = (
        st.session_state
        .selected_code
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

        st.warning(
            f"{name} ({code})의 가격 데이터를 "
            "가져오지 못했습니다."
        )

        st.info(
            "네트워크 또는 외부 금융 데이터 "
            "제공처 상태를 확인한 뒤 다시 조회해 주세요."
        )

        return

    current = float(
        d["Close"].iloc[-1]
    )

    ret20 = last_valid(
        d,
        "RET20",
        np.nan
    )

    rsi = last_valid(
        d,
        "RSI",
        np.nan
    )

    vr = last_valid(
        d,
        "VOL_RATIO",
        np.nan
    )

    ma20 = last_valid(
        d,
        "MA20",
        current
    )

    st.markdown(
        '<div class="hero">',
        unsafe_allow_html=True
    )

    st.markdown(
        f"## {name}"
    )

    st.markdown(
        f'<div class="small-muted">'
        f'{code} · 기준일 '
        f'{d.index[-1].strftime("%Y-%m-%d")}'
        f'</div>',
        unsafe_allow_html=True
    )

    render_theme_chips(
        code,
        name
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    # ========================================================
    # QUICK METRICS
    # ========================================================

    m1, m2, m3, m4, m5 = st.columns(5)

    m1.metric(
        "현재가",
        money(current)
    )

    m2.metric(
        "20일",
        pct_text(ret20)
    )

    m3.metric(
        "RSI",
        (
            f"{rsi:.0f}"
            if np.isfinite(rsi)
            else "-"
        )
    )

    m4.metric(
        "거래량",
        (
            f"{vr:.1f}배"
            if np.isfinite(vr)
            else "-"
        )
    )

    m5.metric(
        "20일선",
        (
            "상회"
            if current >= ma20
            else "하회"
        )
    )

    # ========================================================
    # HOLDING
    # ========================================================

    held, avg, qty = render_holding(
        code,
        current
    )

    # ========================================================
    # MOST IMPORTANT:
    # CURRENT JUDGMENT -> ACTION
    # ========================================================

    render_judgment(
        d,
        code,
        held
    )

    # ========================================================
    # CORE PRICE + SCENARIO
    # ========================================================

    render_price_scenarios(
        d
    )

    # ========================================================
    # CHART
    # ========================================================

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

    info = THEMES[
        theme
    ]

    rows = theme_snapshot(
        theme
    )

    st.markdown(
        '<div class="theme-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="stage">'
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
        f'<div class="small-muted">'
        f'<b>왜 중요한가</b> · '
        f'{info["reason"]}'
        f'</div>',
        unsafe_allow_html=True
    )

    if rows:

        cols = st.columns(
            min(
                4,
                len(rows)
            )
        )

        for i, item in enumerate(
            rows[:4]
        ):

            with cols[i]:

                st.markdown(
                    f"**{item['name']}**"
                )

                st.caption(
                    f"{money(item['price'])} · "
                    f"20일 {pct_text(item['ret20'])} · "
                    f"RSI {item['rsi']:.0f} · "
                    f"{item['trend']}"
                )

                if st.button(
                    "ETF 분석",
                    key=(
                        f"theme_go_"
                        f"{theme}_"
                        f"{item['code']}"
                    ),
                    use_container_width=True
                ):

                    set_selected(
                        item["code"]
                    )

                    st.rerun()

    else:

        st.caption(
            "대표 ETF 가격 데이터를 "
            "불러오지 못했습니다."
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
        "현재 주도 → 다음 수혜 → 관심 확대 흐름을 "
        "한눈에 보고, 대표 ETF까지 바로 연결합니다."
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(
        [1, 4]
    )

    with c1:

        if st.button(
            "🔄 시장 다시 탐색",
            use_container_width=True
        ):

            st.session_state.price_cache = {}

            with st.spinner(
                "ETF 목록과 테마 데이터를 다시 탐색합니다..."
            ):

                fetch_krx_etf_catalog()

            st.rerun()

    with c2:

        st.caption(
            "테마 단계는 투자 권유가 아니라 "
            "현재 가격·추세·거래량 흐름을 보기 위한 "
            "탐색용 분류입니다."
        )

    # ========================================================
    # FUTURE FLOW
    # ========================================================

    st.markdown(
        "### 현재 → 다음 수혜 흐름"
    )

    for theme, stage in FUTURE_CHAIN:

        render_theme_card(
            theme,
            stage
        )

    # ========================================================
    # SUMMARY TABLE
    # ========================================================

    st.markdown(
        "### 📋 미래테마 한눈에 보기"
    )

    table_rows = []

    for theme, stage in FUTURE_CHAIN:

        rows = theme_snapshot(
            theme
        )

        if rows:

            top = rows[0]

            table_rows.append(
                {
                    "상태":
                        stage,

                    "테마":
                        theme,

                    "대표 ETF":
                        top["name"],

                    "현재가":
                        money(
                            top["price"]
                        ),

                    "20일":
                        pct_text(
                            top["ret20"]
                        ),

                    "RSI":
                        (
                            f"{top['rsi']:.0f}"
                            if np.isfinite(
                                top["rsi"]
                            )
                            else "-"
                        ),

                    "거래량":
                        (
                            f"{top['vr']:.1f}배"
                            if np.isfinite(
                                top["vr"]
                            )
                            else "-"
                        ),
                }
            )

        else:

            table_rows.append(
                {
                    "상태":
                        stage,

                    "테마":
                        theme,

                    "대표 ETF":
                        "-",

                    "현재가":
                        "-",

                    "20일":
                        "-",

                    "RSI":
                        "-",

                    "거래량":
                        "-",
                }
            )

    st.dataframe(
        pd.DataFrame(
            table_rows
        ),
        use_container_width=True,
        hide_index=True,
    )

    # ========================================================
    # ALL THEMES
    # ========================================================

    st.markdown(
        "### 전체 테마 탐색"
    )

    theme = st.selectbox(
        "테마 선택",
        list(THEMES.keys()),
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
# MAIN RENDER
# ============================================================

if nav == "📊 내 ETF":

    render_my_etf()

else:

    render_future_themes()