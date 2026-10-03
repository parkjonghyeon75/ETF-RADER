import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


# ============================================================
# ETF RADAR
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

h1, h2, h3 {
    letter-spacing: -0.5px;
}

.small-muted {
    color: #8b95a7;
    font-size: 0.82rem;
}

.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    margin-top: 0.8rem;
    margin-bottom: 0.45rem;
}

.radar-card {
    border: 1px solid rgba(128,128,128,0.18);
    border-radius: 14px;
    padding: 14px 15px;
    margin-bottom: 10px;
    background: rgba(128,128,128,0.035);
}

.radar-card-title {
    font-size: 0.88rem;
    font-weight: 700;
    margin-bottom: 6px;
}

.radar-value {
    font-size: 1.25rem;
    font-weight: 800;
}

.radar-desc {
    font-size: 0.82rem;
    color: #8993a4;
    margin-top: 3px;
}

.buy-box {
    border-left: 4px solid #4f8cff;
    padding: 12px 14px;
    border-radius: 10px;
    background: rgba(79,140,255,0.06);
    margin-bottom: 8px;
}

.warn-box {
    border-left: 4px solid #f0a23b;
    padding: 12px 14px;
    border-radius: 10px;
    background: rgba(240,162,59,0.07);
    margin-bottom: 8px;
}

.danger-box {
    border-left: 4px solid #e55353;
    padding: 12px 14px;
    border-radius: 10px;
    background: rgba(229,83,83,0.07);
    margin-bottom: 8px;
}

.good-box {
    border-left: 4px solid #39a96b;
    padding: 12px 14px;
    border-radius: 10px;
    background: rgba(57,169,107,0.07);
    margin-bottom: 8px;
}

.info-box {
    border-left: 4px solid #8b7cff;
    padding: 12px 14px;
    border-radius: 10px;
    background: rgba(139,124,255,0.07);
    margin-bottom: 8px;
}

.stButton > button {
    min-height: 42px;
    border-radius: 10px !important;
}

div[data-testid="stMetric"] {
    border: 1px solid rgba(128,128,128,0.16);
    border-radius: 12px;
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# FILE / CACHE
# ============================================================

WATCHLIST_FILE = "watchlist.json"
ETF_CACHE_FILE = "etf_universe_cache.json"

ETF_CACHE_HOURS = 6


# ============================================================
# BASE ETF UNIVERSE
# ============================================================

BASE_ETF_UNIVERSE = {

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


DEFAULT_WATCHLIST = [
    "395160",
    "487240",
    "471990",
    "133690",
    "360750",
    "458730"
]


# ============================================================
# FALLBACK ETF UNIVERSE
# ============================================================

FALLBACK_ETF_UNIVERSE = {

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


# ============================================================
# THEME DEFINITIONS
# ============================================================

THEMES = {

    "AI 반도체": {
        "stage": "LEADER",
        "description": "AI 연산 수요와 반도체 고성능화에 연결되는 핵심 영역",
        "keywords": [
            "ai반도체",
            "반도체",
            "hbm",
            "메모리",
            "시스템반도체",
            "반도체장비",
            "반도체소부장",
            "semiconductor",
            "chip"
        ],
        "etfs": [
            "395160",
            "462100",
            "486410",
            "487240",
            "452330"
        ]
    },

    "AI 소프트웨어·빅테크": {
        "stage": "LEADER",
        "description": "AI 모델·클라우드·빅테크 플랫폼에 연결되는 영역",
        "keywords": [
            "ai",
            "인공지능",
            "빅테크",
            "테크",
            "소프트웨어",
            "클라우드",
            "미국테크",
            "나스닥",
            "technology",
            "software"
        ],
        "etfs": [
            "487240",
            "452330",
            "133690",
            "379810"
        ]
    },

    "데이터센터·AI 인프라": {
        "stage": "FOLLOWER",
        "description": "AI 데이터센터 확대에 필요한 서버·전력·인프라 영역",
        "keywords": [
            "데이터센터",
            "ai인프라",
            "인프라",
            "서버",
            "데이터",
            "클라우드",
            "data center",
            "ai infrastructure"
        ],
        "etfs": [
            "471990",
            "487240",
            "486410"
        ]
    },

    "전력 인프라": {
        "stage": "FOLLOWER",
        "description": "AI 데이터센터 전력수요 증가와 전력망 투자에 연결되는 영역",
        "keywords": [
            "전력",
            "전력기기",
            "전력인프라",
            "전력설비",
            "변압기",
            "배전",
            "송전",
            "electric",
            "power"
        ],
        "etfs": [
            "471990",
            "445380",
            "465560"
        ]
    },

    "원자력": {
        "stage": "FOLLOWER",
        "description": "원전·원전 기자재·글로벌 원자력 산업 관련 영역",
        "keywords": [
            "원자력",
            "원전",
            "원전산업",
            "원자로",
            "nuclear"
        ],
        "etfs": [
            "445380",
            "465560"
        ]
    },

    "냉각·열관리": {
        "stage": "EARLY",
        "description": "고집적 AI 서버의 발열 증가와 열관리 수요에 연결되는 영역",
        "keywords": [
            "냉각",
            "열관리",
            "액침냉각",
            "수랭",
            "냉각시스템",
            "thermal",
            "cooling"
        ],
        "etfs": []
    },

    "로봇·휴머노이드": {
        "stage": "FOLLOWER",
        "description": "산업 자동화와 휴머노이드 확산에 연결되는 영역",
        "keywords": [
            "로봇",
            "로보틱스",
            "휴머노이드",
            "자동화",
            "robot",
            "robotics",
            "humanoid"
        ],
        "etfs": [
            "465610",
            "476250"
        ]
    },

    "방산·항공우주": {
        "stage": "WATCH",
        "description": "방산·항공우주 산업과 관련된 영역",
        "keywords": [
            "방산",
            "방위산업",
            "항공우주",
            "우주",
            "위성",
            "defense",
            "aerospace",
            "space"
        ],
        "etfs": [
            "449450",
            "463250"
        ]
    },

    "조선·해운": {
        "stage": "WATCH",
        "description": "조선·선박·해운 산업 관련 영역",
        "keywords": [
            "조선",
            "조선업",
            "선박",
            "해운",
            "운송",
            "ship",
            "shipping"
        ],
        "etfs": [
            "139230"
        ]
    },

    "바이오·헬스케어": {
        "stage": "WATCH",
        "description": "바이오·헬스케어 전반을 추적하는 영역",
        "keywords": [
            "바이오",
            "헬스케어",
            "제약",
            "의료",
            "health",
            "healthcare",
            "bio",
            "pharma"
        ],
        "etfs": [
            "329200",
            "266420",
            "462610"
        ]
    },

    "비만치료제": {
        "stage": "EARLY",
        "description": "GLP-1 등 비만치료제 관련 산업",
        "keywords": [
            "비만",
            "비만치료",
            "glp",
            "치료제",
            "대사질환",
            "obesity"
        ],
        "etfs": []
    },

    "2차전지·ESS": {
        "stage": "WATCH",
        "description": "배터리 소재·셀·장비와 ESS 관련 영역",
        "keywords": [
            "2차전지",
            "배터리",
            "전지",
            "ess",
            "양극재",
            "음극재",
            "배터리소재",
            "battery"
        ],
        "etfs": [
            "305540",
            "364980",
            "438320"
        ]
    },

    "자율주행·전기차": {
        "stage": "WATCH",
        "description": "전기차·자율주행·자동차 기술 관련 영역",
        "keywords": [
            "자율주행",
            "전기차",
            "전기자동차",
            "자동차",
            "ev",
            "autonomous",
            "모빌리티"
        ],
        "etfs": [
            "091180"
        ]
    },

    "클라우드·사이버보안": {
        "stage": "EARLY",
        "description": "클라우드 전환과 AI 시대의 보안 인프라 관련 영역",
        "keywords": [
            "클라우드",
            "사이버보안",
            "보안",
            "정보보안",
            "cloud",
            "cyber",
            "security"
        ],
        "etfs": []
    },

    "콘텐츠·미디어": {
        "stage": "WATCH",
        "description": "미디어·콘텐츠·엔터테인먼트 관련 영역",
        "keywords": [
            "콘텐츠",
            "미디어",
            "엔터테인먼트",
            "게임",
            "웹툰",
            "k콘텐츠",
            "media",
            "content"
        ],
        "etfs": []
    },

    "금융·밸류업": {
        "stage": "WATCH",
        "description": "은행·증권·보험과 기업가치 제고 관련 영역",
        "keywords": [
            "금융",
            "은행",
            "증권",
            "보험",
            "밸류업",
            "valueup",
            "financial"
        ],
        "etfs": [
            "139270",
            "091170",
            "140700"
        ]
    },

    "배당·인컴": {
        "stage": "WATCH",
        "description": "배당 및 현금흐름 중심의 인컴형 ETF 영역",
        "keywords": [
            "배당",
            "고배당",
            "인컴",
            "커버드콜",
            "dividend",
            "income"
        ],
        "etfs": [
            "458730",
            "476480",
            "451780",
            "211560",
            "161510"
        ]
    },

    "금·원자재": {
        "stage": "WATCH",
        "description": "금·원유 등 주요 원자재 관련 영역",
        "keywords": [
            "금",
            "골드",
            "원자재",
            "원유",
            "구리",
            "gold",
            "commodity",
            "oil"
        ],
        "etfs": [
            "132030",
            "411060",
            "261220"
        ]
    },

    "미국 기술주": {
        "stage": "LEADER",
        "description": "미국 대형 기술주 및 나스닥 중심 시장",
        "keywords": [
            "미국",
            "나스닥",
            "s&p",
            "테크",
            "technology",
            "nasdaq",
            "sp500"
        ],
        "etfs": [
            "133690",
            "360750",
            "379800",
            "448290",
            "452330"
        ]
    }
}


# ============================================================
# THEME CHAIN
# ============================================================

THEME_CHAIN = [
    ("AI 반도체", "현재 핵심"),
    ("데이터센터·AI 인프라", "후속 수혜"),
    ("전력 인프라", "후속 수혜"),
    ("원자력", "후속 관심"),
    ("냉각·열관리", "선행 관심"),
]


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "📌 내 ETF"

if "selected_code" not in st.session_state:
    st.session_state.selected_code = DEFAULT_WATCHLIST[0]

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "search_selected_code" not in st.session_state:
    st.session_state.search_selected_code = DEFAULT_WATCHLIST[0]

if "catalog_updated_at" not in st.session_state:
    st.session_state.catalog_updated_at = None


# ============================================================
# TEXT NORMALIZE
# ============================================================

def normalize_text(value):

    if value is None:
        return ""

    text = str(value).lower().strip()

    return re.sub(
        r"[^0-9a-z가-힣]",
        "",
        text
    )


def clean_code(code):

    if code is None:
        return ""

    code = str(code).strip()

    match = re.search(
        r"\d{6}",
        code
    )

    if match:
        return match.group(0)

    return code


# ============================================================
# ETF CACHE
# ============================================================

def save_etf_cache(catalog):

    try:

        payload = {
            "updated_at": datetime.now().isoformat(),
            "catalog": catalog
        }

        with open(
            ETF_CACHE_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                payload,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception:
        pass


def load_etf_cache():

    if not os.path.exists(
        ETF_CACHE_FILE
    ):
        return {}, None

    try:

        with open(
            ETF_CACHE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            payload = json.load(f)

        catalog = payload.get(
            "catalog",
            {}
        )

        updated_at = payload.get(
            "updated_at"
        )

        if not isinstance(
            catalog,
            dict
        ):
            return {}, None

        return catalog, updated_at

    except Exception:

        return {}, None


def cache_is_fresh(updated_at):

    if not updated_at:
        return False

    try:

        dt = datetime.fromisoformat(
            updated_at
        )

        return (
            datetime.now() - dt
            < timedelta(
                hours=ETF_CACHE_HOURS
            )
        )

    except Exception:

        return False


# ============================================================
# KRX CATALOG
# ============================================================

def extract_krx_rows(payload):

    rows = []

    def walk(obj):

        if isinstance(obj, list):

            if (
                obj
                and all(
                    isinstance(
                        x,
                        dict
                    )
                    for x in obj
                )
            ):

                rows.extend(obj)

            for item in obj:
                walk(item)

        elif isinstance(obj, dict):

            for value in obj.values():
                walk(value)

    walk(payload)

    return rows


def parse_krx_row(row):

    code_keys = [
        "ISU_SRT_CD",
        "ISU_CD",
        "isuSrtCd",
        "isuCd",
        "isu_cd",
        "종목코드",
        "code",
        "ticker"
    ]

    name_keys = [
        "ISU_ABBRV",
        "ISU_NM",
        "isuAbbrv",
        "isuNm",
        "isu_nm",
        "종목명",
        "name",
        "tickerName"
    ]

    code = None
    name = None

    for key in code_keys:

        if key in row and row[key]:

            code = clean_code(
                row[key]
            )

            if len(code) == 6:
                break

    for key in name_keys:

        if key in row and row[key]:

            name = str(
                row[key]
            ).strip()

            if name:
                break

    if (
        code
        and len(code) == 6
        and name
    ):
        return code, name

    return None, None


@st.cache_data(
    ttl=21600,
    show_spinner=False
)
def fetch_krx_etf_catalog():

    endpoint = (
        "https://data.krx.co.kr/"
        "comm/bldAttendant/"
        "getJsonData.cmd"
    )

    today = datetime.now().strftime(
        "%Y%m%d"
    )

    payload_candidates = [

        {
            "bld":
                "dbms/MDC/STAT/standard/"
                "MDCSTAT04601",
            "locale": "ko_KR",
            "trdDd": today,
            "share": "1",
            "csvxls_isNo": "false"
        },

        {
            "bld":
                "dbms/MDC/STAT/standard/"
                "MDCSTAT04601",
            "locale": "ko_KR",
            "trdDd": today,
            "mktId": "ALL",
            "share": "1",
            "csvxls_isNo": "false"
        },

        {
            "bld":
                "dbms/MDC/STAT/standard/"
                "MDCSTAT04601",
            "locale": "ko_KR",
            "share": "1",
            "csvxls_isNo": "false"
        }
    ]

    headers = {
        "User-Agent":
            "Mozilla/5.0 "
            "(Linux; Android 10; Mobile) "
            "AppleWebKit/537.36 "
            "Chrome/120 Safari/537.36",

        "Referer":
            "https://data.krx.co.kr/",

        "Content-Type":
            "application/x-www-form-urlencoded; "
            "charset=UTF-8"
    }

    for payload in payload_candidates:

        try:

            data = urllib.parse.urlencode(
                payload
            ).encode("utf-8")

            request = urllib.request.Request(
                endpoint,
                data=data,
                headers=headers,
                method="POST"
            )

            with urllib.request.urlopen(
                request,
                timeout=15
            ) as response:

                raw = response.read().decode(
                    "utf-8",
                    errors="ignore"
                )

            if not raw.strip():
                continue

            parsed = json.loads(
                raw
            )

            rows = extract_krx_rows(
                parsed
            )

            catalog = {}

            for row in rows:

                code, name = parse_krx_row(
                    row
                )

                if code and name:

                    catalog[code] = name

            if len(catalog) >= 100:

                return catalog

        except Exception:

            continue

    return {}


# ============================================================
# BUILD ETF CATALOG
# ============================================================

def build_etf_catalog(force=False):

    cached_catalog, cached_updated_at = (
        load_etf_cache()
    )

    catalog = {}

    # fallback
    catalog.update(
        FALLBACK_ETF_UNIVERSE
    )

    # 기존 ETF
    catalog.update(
        BASE_ETF_UNIVERSE
    )

    # 저장된 캐시
    if cached_catalog:

        catalog.update(
            cached_catalog
        )

    # 캐시가 최신이면 사용
    if (
        not force
        and cache_is_fresh(
            cached_updated_at
        )
    ):

        st.session_state.catalog_updated_at = (
            cached_updated_at
        )

        return catalog

    # KRX 최신 목록
    krx_catalog = fetch_krx_etf_catalog()

    if krx_catalog:

        catalog.update(
            krx_catalog
        )

        save_etf_cache(
            catalog
        )

        st.session_state.catalog_updated_at = (
            datetime.now().isoformat()
        )

    elif cached_updated_at:

        st.session_state.catalog_updated_at = (
            cached_updated_at
        )

    return catalog


# ============================================================
# ETF CATALOG
# ============================================================

if "etf_universe" not in st.session_state:

    st.session_state.etf_universe = (
        build_etf_catalog(
            force=False
        )
    )


def get_etf_universe():

    return st.session_state.etf_universe


# ============================================================
# WATCHLIST
# ============================================================

def load_watchlist():

    if not os.path.exists(
        WATCHLIST_FILE
    ):
        return DEFAULT_WATCHLIST.copy()

    try:

        with open(
            WATCHLIST_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        if not isinstance(
            data,
            list
        ):
            return DEFAULT_WATCHLIST.copy()

        result = []

        for code in data:

            code = clean_code(
                code
            )

            if (
                len(code) == 6
                and code not in result
            ):
                result.append(code)

        if result:
            return result

    except Exception:
        pass

    return DEFAULT_WATCHLIST.copy()


def save_watchlist(
    watchlist
):

    try:

        with open(
            WATCHLIST_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                watchlist,
                f,
                ensure_ascii=False,
                indent=2
            )

    except Exception:
        pass


if "watchlist" not in st.session_state:

    st.session_state.watchlist = (
        load_watchlist()
    )


def get_watchlist():

    return st.session_state.watchlist


# ============================================================
# NAVER DATA
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner=False
)
def fetch_naver_data(
    code,
    count=250
):

    url = (
        "https://fchart.stock.naver.com/"
        f"sise.nhn?symbol={code}"
        f"&timeframe=day"
        f"&count={count}"
        f"&requestType=0"
    )

    try:

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            xml_data = response.read()

        root = ET.fromstring(
            xml_data
        )

        rows = []

        for item in root.findall(
            ".//item"
        ):

            data = item.attrib.get(
                "data",
                ""
            )

            parts = data.split("|")

            if len(parts) != 6:
                continue

            date, opn, high, low, close, volume = parts

            rows.append({
                "Date":
                    pd.to_datetime(date),
                "Open":
                    float(opn),
                "High":
                    float(high),
                "Low":
                    float(low),
                "Close":
                    float(close),
                "Volume":
                    float(volume)
            })

        if not rows:

            return pd.DataFrame()

        df = pd.DataFrame(
            rows
        )

        df = df.sort_values(
            "Date"
        )

        df = df.set_index(
            "Date"
        )

        return df

    except Exception:

        return pd.DataFrame()


# ============================================================
# YAHOO DATA
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner=False
)
def fetch_yahoo_data(
    code
):

    try:

        ticker = yf.Ticker(
            f"{code}.KS"
        )

        df = ticker.history(
            period="2y",
            interval="1d",
            auto_adjust=False
        )

        if (
            df is None
            or df.empty
        ):
            return pd.DataFrame()

        df = df.reset_index()

        if "Datetime" in df.columns:

            df = df.rename(
                columns={
                    "Datetime": "Date"
                }
            )

        if "Date" not in df.columns:

            return pd.DataFrame()

        df = df.set_index(
            "Date"
        )

        columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
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
# LOAD PRICE
# ============================================================

def load_price_data(
    code
):

    df = fetch_naver_data(
        code
    )

    if (
        not df.empty
        and len(df) >= 30
    ):

        return df

    return fetch_yahoo_data(
        code
    )


# ============================================================
# INDICATORS
# ============================================================

def calculate_indicators(
    df
):

    if (
        df is None
        or df.empty
    ):
        return pd.DataFrame()

    df = df.copy()

    close = df["Close"]

    # MA
    df["MA5"] = (
        close.rolling(5).mean()
    )

    df["MA20"] = (
        close.rolling(20).mean()
    )

    df["MA60"] = (
        close.rolling(60).mean()
    )

    df["MA120"] = (
        close.rolling(120).mean()
    )

    # RSI
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
        /
        avg_loss.replace(
            0,
            np.nan
        )
    )

    df["RSI14"] = (
        100
        -
        (
            100 /
            (1 + rs)
        )
    )

    # MACD
    ema12 = close.ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = close.ewm(
        span=26,
        adjust=False
    ).mean()

    df["MACD"] = (
        ema12 - ema26
    )

    df["MACD_SIGNAL"] = (
        df["MACD"].ewm(
            span=9,
            adjust=False
        ).mean()
    )

    df["MACD_HIST"] = (
        df["MACD"]
        -
        df["MACD_SIGNAL"]
    )

    # Bollinger
    bb_mid = close.rolling(
        20
    ).mean()

    bb_std = close.rolling(
        20
    ).std()

    df["BB_MID"] = bb_mid

    df["BB_UPPER"] = (
        bb_mid + 2 * bb_std
    )

    df["BB_LOWER"] = (
        bb_mid - 2 * bb_std
    )

    # Volume
    df["VOL20"] = (
        df["Volume"].rolling(20).mean()
    )

    df["VOL_RATIO"] = (
        df["Volume"]
        /
        df["VOL20"]
    )

    # Returns
    df["RET1"] = (
        close.pct_change(1) * 100
    )

    df["RET5"] = (
        close.pct_change(5) * 100
    )

    df["RET20"] = (
        close.pct_change(20) * 100
    )

    df["RET60"] = (
        close.pct_change(60) * 100
    )

    # High / Low
    df["HIGH20"] = (
        close.rolling(20).max()
    )

    df["LOW20"] = (
        close.rolling(20).min()
    )

    # MA gap
    df["MA20_GAP"] = (
        close / df["MA20"] - 1
    ) * 100

    df["MA60_GAP"] = (
        close / df["MA60"] - 1
    ) * 100

    return df


# ============================================================
# LEVELS
# ============================================================

def calculate_levels(
    df
):

    latest = df.iloc[-1]

    current = latest["Close"]

    levels = {

        "현재가":
            current,

        "MA20":
            latest.get(
                "MA20",
                np.nan
            ),

        "MA60":
            latest.get(
                "MA60",
                np.nan
            ),

        "20일 저점":
            latest.get(
                "LOW20",
                np.nan
            ),

        "20일 고점":
            latest.get(
                "HIGH20",
                np.nan
            )
    }

    resistance_candidates = [
        levels["20일 고점"],
        levels["MA60"],
        levels["MA20"]
    ]

    resistance_candidates = [
        x
        for x in resistance_candidates
        if pd.notna(x)
        and x > current
    ]

    if resistance_candidates:

        levels["저항"] = min(
            resistance_candidates
        )

    else:

        levels["저항"] = (
            levels["20일 고점"]
        )

    support_candidates = [
        levels["MA20"],
        levels["MA60"],
        levels["20일 저점"]
    ]

    support_candidates = [
        x
        for x in support_candidates
        if pd.notna(x)
        and x < current
    ]

    if support_candidates:

        levels["지지"] = max(
            support_candidates
        )

    else:

        levels["지지"] = (
            levels["MA20"]
        )

    return levels


# ============================================================
# JUDGMENT
# ============================================================

def get_judgment(
    df
):

    if (
        df is None
        or len(df) < 30
    ):

        return (
            "데이터 부족",
            "충분한 가격 데이터가 확보되지 않아 "
            "추세 판단을 보류합니다."
        )

    latest = df.iloc[-1]

    price = latest["Close"]
    ma20 = latest["MA20"]
    ma60 = latest["MA60"]

    rsi = latest["RSI14"]
    vol_ratio = latest["VOL_RATIO"]

    ret5 = latest["RET5"]
    ret20 = latest["RET20"]

    high20 = latest["HIGH20"]

    if (
        pd.isna(ma20)
        or pd.isna(ma60)
    ):

        return (
            "데이터 부족",
            "이동평균 계산에 필요한 데이터가 부족합니다."
        )

    # 추격 위험
    if (
        price > ma20
        and ma20 > ma60
        and ret5 >= 7
        and rsi >= 70
    ):

        return (
            "추격 위험",
            "중장기 상승 구조는 유지되지만 "
            "단기 상승폭과 RSI가 높아 신규 추격매수에는 부담이 있습니다."
        )

    # 돌파
    if (
        price >= high20 * 0.995
        and vol_ratio >= 1.3
        and rsi < 72
    ):

        return (
            "돌파 확인",
            "최근 고점 부근에서 거래량이 증가하고 있어 "
            "돌파 지속 여부를 확인할 구간입니다."
        )

    # 눌림목
    if (
        price > ma20
        and ma20 > ma60
        and -4 <= ret5 <= 2
    ):

        return (
            "눌림목 관심",
            "상승 추세는 유지되고 있으며 "
            "단기 조정이 진행 중이라 지지 확인이 중요합니다."
        )

    # 상승
    if (
        price > ma20
        and ma20 > ma60
        and ret20 > 0
    ):

        return (
            "보유 유지",
            "가격이 MA20·MA60 위에 있고 "
            "중기 추세가 유지되고 있습니다."
        )

    # MA20 아래
    if (
        price < ma20
        and price > ma60
    ):

        return (
            "관망 후 확인",
            "단기 추세가 약해졌지만 MA60은 유지되고 있습니다. "
            "MA20 회복 여부를 확인하는 것이 중요합니다."
        )

    # MA60 아래
    if price < ma60:

        return (
            "리스크 재검토",
            "중기 이동평균 아래에 있어 "
            "신규 매수보다 추세 회복 여부를 확인할 필요가 있습니다."
        )

    return (
        "관망",
        "추세 방향이 뚜렷하지 않아 추가 확인이 필요합니다."
    )


# ============================================================
# INDICATOR EXPLANATIONS
# ============================================================

def explain_rsi(
    rsi
):

    if pd.isna(rsi):

        return "RSI 데이터 없음"

    if rsi >= 70:

        return (
            "과열권. 상승추세가 강하지만 "
            "단기 추격에는 주의가 필요합니다."
        )

    if rsi >= 60:

        return (
            "강세권. 매수세가 유지되고 있는 구간입니다."
        )

    if rsi >= 50:

        return (
            "중립 이상. 상승 모멘텀 회복 여부를 확인할 구간입니다."
        )

    if rsi >= 40:

        return (
            "중립 이하. 단기 매수세가 아직 강하지 않습니다."
        )

    return (
        "약세권. 추세 회복 여부를 확인할 필요가 있습니다."
    )


def explain_volume(
    vol_ratio
):

    if pd.isna(vol_ratio):

        return "거래량 데이터 없음"

    if vol_ratio >= 2:

        return (
            "평균 대비 거래량이 2배 이상 증가했습니다."
        )

    if vol_ratio >= 1.3:

        return (
            "평균보다 거래량이 증가하고 있습니다."
        )

    if vol_ratio >= 0.8:

        return (
            "평균적인 거래량 흐름입니다."
        )

    return (
        "거래량이 평균보다 낮습니다."
    )


def explain_trend(
    latest
):

    price = latest["Close"]
    ma20 = latest["MA20"]
    ma60 = latest["MA60"]

    if (
        pd.isna(ma20)
        or pd.isna(ma60)
    ):

        return (
            "추세 계산에 필요한 데이터가 부족합니다."
        )

    if price > ma20 > ma60:

        return "단기·중기 상승 구조"

    if (
        price > ma20
        and price < ma60
    ):

        return (
            "단기 반등이나 중기 추세 확인 필요"
        )

    if (
        price < ma20
        and price > ma60
    ):

        return "단기 조정"

    if price < ma20 < ma60:

        return "중기 약세 구조"

    return "혼조"


def explain_macd(
    latest
):

    macd = latest["MACD"]
    signal = latest["MACD_SIGNAL"]
    hist = latest["MACD_HIST"]

    if (
        pd.isna(macd)
        or pd.isna(signal)
    ):

        return "MACD 데이터 없음"

    if (
        macd > signal
        and hist > 0
    ):

        return (
            "상승 모멘텀이 우세합니다."
        )

    if (
        macd < signal
        and hist < 0
    ):

        return (
            "하락 모멘텀이 우세합니다."
        )

    return (
        "모멘텀 방향 전환을 확인할 구간입니다."
    )


# ============================================================
# TRADE SCENARIO
# ============================================================

def get_trade_scenario(
    df
):

    latest = df.iloc[-1]

    price = latest["Close"]

    ma20 = latest["MA20"]
    ma60 = latest["MA60"]

    high20 = latest["HIGH20"]

    scenarios = []

    # 눌림
    if pd.notna(ma20):

        if price >= ma20:

            scenarios.append({
                "type": "buy",
                "title": "① 눌림목",
                "text": (
                    f"현재가 {price:,.0f}원 기준 "
                    f"MA20 {ma20:,.0f}원 부근까지 조정 후 "
                    "지지가 확인되면 관심을 유지할 수 있습니다."
                )
            })

        else:

            scenarios.append({
                "type": "warn",
                "title": "① MA20 회복",
                "text": (
                    f"현재가가 MA20({ma20:,.0f}원) 아래에 있어 "
                    "먼저 MA20 회복 여부를 확인합니다."
                )
            })

    # 돌파
    if pd.notna(high20):

        scenarios.append({
            "type": "good",
            "title": "② 돌파",
            "text": (
                f"20일 고점 {high20:,.0f}원 돌파와 "
                "거래량 증가가 동시에 나타나는지 확인합니다."
            )
        })

    # 이탈
    if pd.notna(ma60):

        scenarios.append({
            "type": "danger",
            "title": "③ 추세 이탈",
            "text": (
                f"MA60 {ma60:,.0f}원 이탈이 지속되면 "
                "중기 추세를 다시 확인할 필요가 있습니다."
            )
        })

    return scenarios


# ============================================================
# INTEREST CONDITIONS
# ============================================================

def get_interest_conditions(
    df
):

    latest = df.iloc[-1]

    price = latest["Close"]

    ma20 = latest["MA20"]

    rsi = latest["RSI14"]

    vol_ratio = latest["VOL_RATIO"]

    high20 = latest["HIGH20"]

    conditions = []

    if pd.notna(ma20):

        if price >= ma20:

            conditions.append(
                (
                    "✓",
                    "MA20 위 유지",
                    "추세 유지 조건"
                )
            )

        else:

            conditions.append(
                (
                    "○",
                    "MA20 회복",
                    "단기 추세 회복 확인"
                )
            )

    if pd.notna(high20):

        if price >= high20 * 0.98:

            conditions.append(
                (
                    "✓",
                    "20일 고점 접근",
                    "돌파 여부 확인"
                )
            )

        else:

            gap = (
                (high20 / price - 1)
                * 100
            )

            conditions.append(
                (
                    "○",
                    f"최근 고점까지 {gap:.1f}%",
                    "돌파 후보"
                )
            )

    if pd.notna(vol_ratio):

        if vol_ratio >= 1.3:

            conditions.append(
                (
                    "✓",
                    "거래량 증가",
                    "관심도 상승"
                )
            )

        else:

            conditions.append(
                (
                    "○",
                    "거래량 대기",
                    "평균 거래량 확인"
                )
            )

    if pd.notna(rsi):

        if 50 <= rsi <= 68:

            conditions.append(
                (
                    "✓",
                    "RSI 안정 구간",
                    "모멘텀 확인"
                )
            )

        elif rsi > 70:

            conditions.append(
                (
                    "!",
                    "RSI 과열",
                    "추격 주의"
                )
            )

        else:

            conditions.append(
                (
                    "○",
                    "RSI 회복 필요",
                    "모멘텀 확인"
                )
            )

    return conditions


# ============================================================
# THEME MATCH
# ============================================================

def get_theme_matches(
    theme_name
):

    catalog = get_etf_universe()

    info = THEMES.get(
        theme_name,
        {}
    )

    keywords = info.get(
        "keywords",
        []
    )

    seed_codes = info.get(
        "etfs",
        []
    )

    normalized_keywords = [
        normalize_text(x)
        for x in keywords
    ]

    matches = {}

    # Seed ETF
    for code in seed_codes:

        if code in catalog:

            matches[code] = {
                "code": code,
                "name": catalog[code],
                "score": 100,
                "seed": True
            }

    # 전체 ETF 자동 검색
    for code, name in catalog.items():

        normalized_name = normalize_text(
            name
        )

        score = 0

        for keyword in normalized_keywords:

            if (
                keyword
                and keyword in normalized_name
            ):

                score += 1

        if score > 0:

            if code in matches:

                matches[code]["score"] += (
                    score * 10
                )

            else:

                matches[code] = {
                    "code": code,
                    "name": name,
                    "score": score * 10,
                    "seed": False
                }

    result = list(
        matches.values()
    )

    result.sort(
        key=lambda x: (
            -x["score"],
            x["name"]
        )
    )

    return result


# ============================================================
# ETF -> THEME
# ============================================================

def get_themes_for_etf(
    code
):

    catalog = get_etf_universe()

    name = catalog.get(
        code,
        code
    )

    normalized_name = normalize_text(
        name
    )

    result = []

    for theme_name, info in THEMES.items():

        if code in info.get(
            "etfs",
            []
        ):

            result.append(
                theme_name
            )

            continue

        for keyword in info.get(
            "keywords",
            []
        ):

            if (
                normalize_text(keyword)
                in normalized_name
            ):

                result.append(
                    theme_name
                )

                break

    return result


# ============================================================
# ETF SEARCH
# ============================================================

def search_etfs(
    keyword,
    limit=50
):

    catalog = get_etf_universe()

    keyword = str(
        keyword
    ).strip()

    if not keyword:
        return []

    normalized_keyword = normalize_text(
        keyword
    )

    results = []

    # 직접 코드
    direct_code = clean_code(
        keyword
    )

    if (
        len(direct_code) == 6
        and direct_code.isdigit()
    ):

        if direct_code in catalog:

            results.append({
                "code":
                    direct_code,
                "name":
                    catalog[
                        direct_code
                    ],
                "score":
                    1000
            })

        else:

            results.append({
                "code":
                    direct_code,
                "name":
                    f"{direct_code} (직접 조회)",
                "score":
                    1000
            })

    # 이름 검색
    for code, name in catalog.items():

        normalized_name = normalize_text(
            name
        )

        score = 0

        if (
            normalized_keyword
            == normalized_name
        ):

            score += 500

        if (
            normalized_keyword
            in normalized_name
        ):

            score += 200

        if (
            normalized_keyword
            in normalize_text(code)
        ):

            score += 300

        # 테마 검색
        for theme_name, info in THEMES.items():

            theme_norm = normalize_text(
                theme_name
            )

            if (
                normalized_keyword
                in theme_norm
            ):

                if code in info.get(
                    "etfs",
                    []
                ):

                    score += 250

                for tk in info.get(
                    "keywords",
                    []
                ):

                    if (
                        normalize_text(tk)
                        in normalized_name
                    ):

                        score += 30

        if score > 0:

            results.append({
                "code":
                    code,
                "name":
                    name,
                "score":
                    score
            })

    # 중복 제거
    unique = {}

    for item in results:

        code = item["code"]

        if (
            code not in unique
            or item["score"]
            > unique[code]["score"]
        ):

            unique[code] = item

    results = list(
        unique.values()
    )

    results.sort(
        key=lambda x: (
            -x["score"],
            x["name"]
        )
    )

    return results[:limit]


# ============================================================
# RECENT MOVEMENT
# ============================================================

def render_recent_movement(
    df
):

    if len(df) < 6:
        return

    recent = df.tail(
        5
    ).copy()

    recent["등락률"] = (
        recent["Close"].pct_change()
        * 100
    )

    display = recent[
        [
            "Close",
            "등락률",
            "VOL_RATIO",
            "RSI14"
        ]
    ].copy()

    display.columns = [
        "종가",
        "일간등락",
        "거래량배수",
        "RSI"
    ]

    display.index = (
        display.index.strftime(
            "%m/%d"
        )
    )

    display["종가"] = (
        display["종가"].round(0)
    )

    display["일간등락"] = (
        display["일간등락"].round(2)
    )

    display["거래량배수"] = (
        display["거래량배수"].round(2)
    )

    display["RSI"] = (
        display["RSI"].round(1)
    )

    st.markdown(
        '<div class="section-title">'
        '📈 최근 5거래일 변화'
        '</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        display,
        use_container_width=True
    )


# ============================================================
# INTEREST RADAR
# ============================================================

def render_interest_radar(
    df
):

    latest = df.iloc[-1]

    judgment, explanation = (
        get_judgment(df)
    )

    rsi = latest["RSI14"]
    vol_ratio = latest["VOL_RATIO"]
    ret5 = latest["RET5"]
    ret20 = latest["RET20"]

    st.markdown(
        '<div class="section-title">'
        '📡 관심 레이더'
        '</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(4)

    metrics = [

        (
            "현재 판단",
            judgment,
            explanation
        ),

        (
            "5일 수익률",
            (
                f"{ret5:+.1f}%"
                if pd.notna(ret5)
                else "-"
            ),
            "단기 움직임"
        ),

        (
            "20일 수익률",
            (
                f"{ret20:+.1f}%"
                if pd.notna(ret20)
                else "-"
            ),
            "중기 움직임"
        ),

        (
            "거래량",
            (
                f"{vol_ratio:.1f}배"
                if pd.notna(vol_ratio)
                else "-"
            ),
            "20일 평균 대비"
        )
    ]

    for col, metric in zip(
        cols,
        metrics
    ):

        title, value, desc = metric

        with col:

            st.markdown(
                f"""
                <div class="radar-card">
                    <div class="radar-card-title">
                        {title}
                    </div>
                    <div class="radar-value">
                        {value}
                    </div>
                    <div class="radar-desc">
                        {desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    if judgment == "추격 위험":

        st.warning(
            "현재는 상승 추세보다 단기 과열 여부가 중요합니다. "
            "새로 진입한다면 눌림 여부를 확인하는 것이 핵심입니다."
        )

    elif judgment in [
        "눌림목 관심",
        "돌파 확인"
    ]:

        st.info(
            "현재 차트에서 관찰할 조건이 발생하고 있습니다. "
            "가격 자체보다 거래량과 지지/돌파 여부를 함께 확인하세요."
        )

    elif judgment == "리스크 재검토":

        st.warning(
            "중기 추세가 약해진 상태입니다. "
            "반등만으로 추세 전환으로 판단하지 않고 "
            "MA20/MA60 회복 여부를 확인하세요."
        )


# ============================================================
# INTEREST CONDITIONS
# ============================================================

def render_interest_conditions(
    df
):

    conditions = (
        get_interest_conditions(df)
    )

    st.markdown(
        '<div class="section-title">'
        '🔔 관심 유지 조건'
        '</div>',
        unsafe_allow_html=True
    )

    if not conditions:
        return

    cols = st.columns(
        min(
            4,
            len(conditions)
        )
    )

    for idx, item in enumerate(
        conditions
    ):

        icon, title, desc = item

        with cols[
            idx % len(cols)
        ]:

            st.markdown(
                f"""
                <div class="radar-card">
                    <div style="font-size:1.15rem;">
                        {icon}
                    </div>
                    <b>{title}</b>
                    <div class="radar-desc">
                        {desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# ETF THEME
# ============================================================

def render_etf_themes(
    code
):

    themes = get_themes_for_etf(
        code
    )

    st.markdown(
        '<div class="section-title">'
        '🔗 연결 테마'
        '</div>',
        unsafe_allow_html=True
    )

    if not themes:

        st.caption(
            "현재 ETF 이름 기준으로 자동 연결되는 테마가 없습니다."
        )

        return

    st.write(
        " · ".join(
            [
                f"**{x}**"
                for x in themes
            ]
        )
    )


# ============================================================
# PRICE SCENARIO
# ============================================================

def render_price_scenario(
    df
):

    levels = calculate_levels(
        df
    )

    st.markdown(
        '<div class="section-title">'
        '🎯 핵심 가격 구간'
        '</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(4)

    values = [

        (
            "현재가",
            levels["현재가"]
        ),

        (
            "MA20",
            levels["MA20"]
        ),

        (
            "MA60",
            levels["MA60"]
        ),

        (
            "최근 고점",
            levels["20일 고점"]
        )
    ]

    for col, (
        label,
        value
    ) in zip(
        cols,
        values
    ):

        with col:

            if pd.notna(value):

                st.metric(
                    label,
                    f"{value:,.0f}"
                )

            else:

                st.metric(
                    label,
                    "-"
                )

    st.markdown(
        '<div class="section-title">'
        '📍 가격 시나리오'
        '</div>',
        unsafe_allow_html=True
    )

    scenarios = (
        get_trade_scenario(df)
    )

    for scenario in scenarios:

        css = scenario["type"]

        if css == "buy":

            box_class = "buy-box"

        elif css == "warn":

            box_class = "warn-box"

        elif css == "danger":

            box_class = "danger-box"

        else:

            box_class = "good-box"

        st.markdown(
            f"""
            <div class="{box_class}">
                <b>{scenario["title"]}</b><br>
                {scenario["text"]}
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# CHART
# ============================================================

def render_chart(
    df,
    name
):

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[
            0.70,
            0.30
        ]
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="가격"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MA20"],
            name="MA20",
            line=dict(
                width=1.5
            )
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MA60"],
            name="MA60",
            line=dict(
                width=1.5
            )
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["BB_UPPER"],
            name="BB Upper",
            line=dict(
                width=1,
                dash="dot"
            ),
            opacity=0.6
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["BB_LOWER"],
            name="BB Lower",
            line=dict(
                width=1,
                dash="dot"
            ),
            opacity=0.6
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            name="거래량"
        ),
        row=2,
        col=1
    )

    fig.update_layout(
        height=560,
        margin=dict(
            l=10,
            r=10,
            t=35,
            b=10
        ),
        title=name,
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# ETF DETAIL
# ============================================================

def render_etf_detail(
    code
):

    code = clean_code(
        code
    )

    catalog = get_etf_universe()

    name = catalog.get(
        code,
        f"ETF {code}"
    )

    st.markdown(
        f"# {name}"
    )

    st.caption(
        f"{code} · ETF RADAR"
    )

    with st.spinner(
        "가격 데이터를 분석하고 있습니다..."
    ):

        raw_df = load_price_data(
            code
        )

    if (
        raw_df is None
        or raw_df.empty
    ):

        st.error(
            "가격 데이터를 불러오지 못했습니다. "
            "잠시 후 다시 시도하거나 ETF 코드를 확인해주세요."
        )

        return

    df = calculate_indicators(
        raw_df
    )

    if df.empty:

        st.error(
            "기술지표를 계산할 수 없습니다."
        )

        return

    latest = df.iloc[-1]

    current = latest["Close"]

    if len(df) >= 2:

        prev = df.iloc[-2]["Close"]

    else:

        prev = current

    daily_change = (
        (current / prev - 1)
        * 100
        if prev
        else 0
    )

    judgment, explanation = (
        get_judgment(df)
    )

    # ========================================================
    # TOP METRICS
    # ========================================================

    cols = st.columns(5)

    cols[0].metric(
        "현재가",
        f"{current:,.0f}",
        f"{daily_change:+.2f}%"
    )

    cols[1].metric(
        "RSI",
        (
            f"{latest['RSI14']:.1f}"
            if pd.notna(
                latest["RSI14"]
            )
            else "-"
        )
    )

    cols[2].metric(
        "20일",
        (
            f"{latest['RET20']:+.1f}%"
            if pd.notna(
                latest["RET20"]
            )
            else "-"
        )
    )

    cols[3].metric(
        "거래량",
        (
            f"{latest['VOL_RATIO']:.1f}배"
            if pd.notna(
                latest["VOL_RATIO"]
            )
            else "-"
        )
    )

    cols[4].metric(
        "판단",
        judgment
    )

    # ========================================================
    # JUDGMENT
    # ========================================================

    if judgment == "추격 위험":

        st.markdown(
            f"""
            <div class="warn-box">
                <b>⚠️ {judgment}</b><br>
                {explanation}
            </div>
            """,
            unsafe_allow_html=True
        )

    elif judgment in [
        "눌림목 관심",
        "돌파 확인",
        "보유 유지"
    ]:

        st.markdown(
            f"""
            <div class="good-box">
                <b>📌 {judgment}</b><br>
                {explanation}
            </div>
            """,
            unsafe_allow_html=True
        )

    elif judgment == "리스크 재검토":

        st.markdown(
            f"""
            <div class="danger-box">
                <b>⚠️ {judgment}</b><br>
                {explanation}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="info-box">
                <b>ℹ️ {judgment}</b><br>
                {explanation}
            </div>
            """,
            unsafe_allow_html=True
        )

    # ========================================================
    # INTEREST RADAR
    # ========================================================

    render_interest_radar(
        df
    )

    # ========================================================
    # PRICE
    # ========================================================

    render_price_scenario(
        df
    )

    # ========================================================
    # INTEREST CONDITIONS
    # ========================================================

    render_interest_conditions(
        df
    )

    # ========================================================
    # RECENT MOVEMENT
    # ========================================================

    render_recent_movement(
        df
    )

    # ========================================================
    # THEMES
    # ========================================================

    render_etf_themes(
        code
    )

    # ========================================================
    # INDICATOR EXPLANATION
    # ========================================================

    with st.expander(
        "📚 보조지표 해석"
    ):

        c1, c2 = st.columns(2)

        with c1:

            st.write(
                f"**추세:** "
                f"{explain_trend(latest)}"
            )

            st.write(
                f"**RSI:** "
                f"{explain_rsi(latest['RSI14'])}"
            )

        with c2:

            st.write(
                f"**거래량:** "
                f"{explain_volume(latest['VOL_RATIO'])}"
            )

            st.write(
                f"**MACD:** "
                f"{explain_macd(latest)}"
            )

    # ========================================================
    # CHART
    # ========================================================

    render_chart(
        df.tail(180),
        name
    )


# ============================================================
# SEARCH
# ============================================================

def render_search():

    st.markdown(
        '<div class="section-title">'
        '🔎 ETF 찾기'
        '</div>',
        unsafe_allow_html=True
    )

    catalog = get_etf_universe()

    st.caption(
        f"검색 데이터: {len(catalog):,}개 ETF · "
        "종목명 / 코드 / 테마 키워드 검색"
    )

    col1, col2 = st.columns(
        [4, 1]
    )

    with col1:

        query = st.text_input(
            "ETF 검색",
            value=st.session_state.search_query,
            placeholder=(
                "예: 반도체 / AI / 원전 / 방산 / 395160"
            ),
            label_visibility="collapsed"
        )

    with col2:

        refresh = st.button(
            "🔄 목록 업데이트",
            use_container_width=True
        )

    if refresh:

        with st.spinner(
            "KRX ETF 목록을 업데이트합니다..."
        ):

            try:
                fetch_krx_etf_catalog.clear()
            except Exception:
                pass

            new_catalog = (
                build_etf_catalog(
                    force=True
                )
            )

            st.session_state.etf_universe = (
                new_catalog
            )

        st.success(
            "ETF 목록 업데이트 완료 · "
            f"{len(new_catalog):,}개"
        )

        catalog = new_catalog

    st.session_state.search_query = (
        query
    )

    if not query:

        st.caption(
            "검색어를 입력하면 ETF가 표시됩니다."
        )

        return

    results = search_etfs(
        query,
        limit=50
    )

    if not results:

        st.warning(
            "검색 결과가 없습니다. "
            "ETF 6자리 코드를 직접 입력해도 분석할 수 있습니다."
        )

        return

    options = [
        (
            f"{item['code']} · "
            f"{item['name']}"
        )
        for item in results
    ]

    selected_index = 0

    for idx, item in enumerate(
        results
    ):

        if (
            item["code"]
            ==
            st.session_state.search_selected_code
        ):

            selected_index = idx
            break

    selected_label = st.selectbox(
        "검색 결과",
        options,
        index=selected_index
    )

    selected_code = (
        selected_label[:6]
    )

    st.session_state.search_selected_code = (
        selected_code
    )

    # 선택 즉시 분석
    st.session_state.selected_code = (
        selected_code
    )

    render_etf_detail(
        selected_code
    )


# ============================================================
# WATCHLIST
# ============================================================

def add_to_watchlist(
    code
):

    code = clean_code(
        code
    )

    if len(code) != 6:
        return False

    watchlist = get_watchlist()

    if code not in watchlist:

        watchlist.append(
            code
        )

        st.session_state.watchlist = (
            watchlist
        )

        save_watchlist(
            watchlist
        )

        return True

    return False


def render_watchlist_selector():

    watchlist = get_watchlist()

    # 중복 제거
    watchlist = list(
        dict.fromkeys(
            [
                clean_code(x)
                for x in watchlist
                if len(clean_code(x)) == 6
            ]
        )
    )

    if not watchlist:

        watchlist = (
            DEFAULT_WATCHLIST.copy()
        )

    st.session_state.watchlist = (
        watchlist
    )

    catalog = get_etf_universe()

    labels = []
    code_by_label = {}

    for code in watchlist:

        name = catalog.get(
            code,
            f"ETF {code}"
        )

        label = (
            f"{code} · {name}"
        )

        labels.append(
            label
        )

        code_by_label[label] = (
            code
        )

    current_label = None

    for label, code in code_by_label.items():

        if (
            code
            ==
            st.session_state.selected_code
        ):

            current_label = label
            break

    if current_label is None:

        current_label = labels[0]

    selected_label = st.selectbox(
        "내 ETF",
        labels,
        index=labels.index(
            current_label
        )
    )

    selected_code = (
        code_by_label[
            selected_label
        ]
    )

    st.session_state.selected_code = (
        selected_code
    )

    return selected_code


# ============================================================
# MY ETF
# ============================================================

def render_my_etf():

    st.title(
        "📌 내 ETF"
    )

    st.caption(
        "ETF를 선택하면 바로 분석합니다."
    )

    selected_code = (
        render_watchlist_selector()
    )

    st.divider()

    # 바로 분석
    render_etf_detail(
        selected_code
    )

    st.divider()

    # 검색
    render_search()

    # 추가
    with st.expander(
        "➕ 관심 ETF 추가"
    ):

        code_input = st.text_input(
            "ETF 코드",
            placeholder="예: 395160"
        )

        if st.button(
            "관심종목에 추가",
            use_container_width=True
        ):

            code = clean_code(
                code_input
            )

            if len(code) != 6:

                st.error(
                    "6자리 ETF 코드를 입력해주세요."
                )

            else:

                if add_to_watchlist(
                    code
                ):

                    catalog = (
                        get_etf_universe()
                    )

                    st.success(
                        f"{catalog.get(code, code)} "
                        "추가 완료"
                    )

                    st.rerun()

                else:

                    st.info(
                        "이미 관심종목에 있습니다."
                    )


# ============================================================
# THEME QUICK METRICS
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner=False
)
def get_theme_quick_metrics(
    theme_name
):

    matches = get_theme_matches(
        theme_name
    )

    if not matches:

        return None

    # 너무 많은 가격 호출 방지
    sample = matches[:3]

    returns = []
    rsi_values = []
    positive_count = 0

    for item in sample:

        code = item["code"]

        try:

            raw = load_price_data(
                code
            )

            if raw.empty:
                continue

            df = calculate_indicators(
                raw
            )

            if df.empty:
                continue

            latest = df.iloc[-1]

            if pd.notna(
                latest["RET20"]
            ):

                returns.append(
                    latest["RET20"]
                )

                if (
                    latest["RET20"]
                    > 0
                ):

                    positive_count += 1

            if pd.notna(
                latest["RSI14"]
            ):

                rsi_values.append(
                    latest["RSI14"]
                )

        except Exception:

            continue

    if not returns:

        return {
            "count": len(matches),
            "avg20": np.nan,
            "rsi": np.nan,
            "positive_ratio": np.nan
        }

    return {
        "count": len(matches),
        "avg20": np.mean(
            returns
        ),
        "rsi": (
            np.mean(
                rsi_values
            )
            if rsi_values
            else np.nan
        ),
        "positive_ratio": (
            positive_count
            /
            len(returns)
        )
    }


# ============================================================
# FUTURE THEME
# ============================================================

def render_future_theme():

    st.title(
        "🚀 미래테마"
    )

    st.caption(
        "ETF 전체 목록을 테마와 자동 연결하고 "
        "최근 가격 흐름을 함께 확인합니다."
    )

    # ========================================================
    # UPDATE
    # ========================================================

    top1, top2, top3 = st.columns(
        [1.25, 1.25, 2.5]
    )

    with top1:

        if st.button(
            "🔄 미래테마 업데이트",
            use_container_width=True
        ):

            with st.spinner(
                "ETF 목록과 테마 연결을 업데이트합니다..."
            ):

                try:
                    fetch_krx_etf_catalog.clear()
                except Exception:
                    pass

                new_catalog = (
                    build_etf_catalog(
                        force=True
                    )
                )

                st.session_state.etf_universe = (
                    new_catalog
                )

            get_theme_quick_metrics.clear()

            st.success(
                f"업데이트 완료 · "
                f"ETF {len(new_catalog):,}개"
            )

    with top2:

        if st.button(
            "🔄 가격 캐시 초기화",
            use_container_width=True
        ):

            try:

                fetch_naver_data.clear()
                fetch_yahoo_data.clear()
                get_theme_quick_metrics.clear()

            except Exception:
                pass

            st.success(
                "가격 데이터 캐시를 초기화했습니다."
            )

    with top3:

        updated = (
            st.session_state.catalog_updated_at
        )

        if updated:

            try:

                dt = datetime.fromisoformat(
                    updated
                )

                updated_text = (
                    dt.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                )

            except Exception:

                updated_text = str(
                    updated
                )

        else:

            updated_text = "기록 없음"

        st.info(
            f"ETF 목록 기준: {updated_text} · "
            f"자동 갱신 기준 {ETF_CACHE_HOURS}시간"
        )

    # ========================================================
    # OVERVIEW
    # ========================================================

    catalog = get_etf_universe()

    total_theme = len(
        THEMES
    )

    unique_matched = set()

    total_matches = 0

    for theme_name in THEMES:

        matches = get_theme_matches(
            theme_name
        )

        total_matches += len(
            matches
        )

        for item in matches:

            unique_matched.add(
                item["code"]
            )

    cols = st.columns(4)

    cols[0].metric(
        "등록 테마",
        f"{total_theme}개"
    )

    cols[1].metric(
        "검색 ETF",
        f"{len(catalog):,}개"
    )

    cols[2].metric(
        "테마 연결 ETF",
        f"{len(unique_matched):,}개"
    )

    cols[3].metric(
        "테마-ETF 연결",
        f"{total_matches:,}건"
    )

    # ========================================================
    # THEME FLOW
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🔗 테마 흐름'
        '</div>',
        unsafe_allow_html=True
    )

    chain_text = " → ".join(
        [
            f"**{theme}** ({stage})"
            for theme, stage
            in THEME_CHAIN
        ]
    )

    st.markdown(
        chain_text
    )

    st.caption(
        "단계는 앱의 관찰 분류이며, "
        "실제 시장 흐름은 ETF의 가격·거래량·RSI를 별도로 확인합니다."
    )

    # ========================================================
    # RADAR
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '📡 테마 레이더'
        '</div>',
        unsafe_allow_html=True
    )

    radar_rows = []

    for theme_name, info in THEMES.items():

        quick = get_theme_quick_metrics(
            theme_name
        )

        if quick is None:
            continue

        radar_rows.append({

            "테마":
                theme_name,

            "단계":
                info.get(
                    "stage",
                    ""
                ),

            "관련 ETF":
                quick["count"],

            "20일 평균":
                (
                    f"{quick['avg20']:+.1f}%"
                    if pd.notna(
                        quick["avg20"]
                    )
                    else "-"
                ),

            "평균 RSI":
                (
                    f"{quick['rsi']:.1f}"
                    if pd.notna(
                        quick["rsi"]
                    )
                    else "-"
                )
        })

    if radar_rows:

        st.dataframe(
            pd.DataFrame(
                radar_rows
            ),
            use_container_width=True,
            hide_index=True
        )

    # ========================================================
    # CORE THEMES
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '⭐ 핵심 테마'
        '</div>',
        unsafe_allow_html=True
    )

    for theme_name, stage in THEME_CHAIN:

        info = THEMES.get(
            theme_name,
            {}
        )

        matches = get_theme_matches(
            theme_name
        )

        st.markdown(
            f"### {theme_name} · {stage}"
        )

        st.caption(
            info.get(
                "description",
                ""
            )
        )

        if not matches:

            st.info(
                "현재 자동 매칭 ETF가 없습니다."
            )

            continue

        rows = []

        # 상위 6개
        for item in matches[:6]:

            code = item["code"]

            try:

                raw = load_price_data(
                    code
                )

                if raw.empty:
                    continue

                df = calculate_indicators(
                    raw
                )

                if df.empty:
                    continue

                latest = df.iloc[-1]

                judgment, _ = (
                    get_judgment(df)
                )

                rows.append({

                    "코드":
                        code,

                    "ETF":
                        item["name"],

                    "20일":
                        (
                            f"{latest['RET20']:+.1f}%"
                            if pd.notna(
                                latest["RET20"]
                            )
                            else "-"
                        ),

                    "RSI":
                        (
                            f"{latest['RSI14']:.1f}"
                            if pd.notna(
                                latest["RSI14"]
                            )
                            else "-"
                        ),

                    "거래량":
                        (
                            f"{latest['VOL_RATIO']:.1f}배"
                            if pd.notna(
                                latest["VOL_RATIO"]
                            )
                            else "-"
                        ),

                    "상태":
                        judgment
                })

            except Exception:

                continue

        if rows:

            st.dataframe(
                pd.DataFrame(
                    rows
                ),
                use_container_width=True,
                hide_index=True
            )

        if len(matches) > 6:

            with st.expander(
                f"전체 자동 매칭 ETF 보기 · "
                f"{len(matches)}개"
            ):

                all_rows = [
                    {
                        "코드":
                            item["code"],
                        "ETF":
                            item["name"]
                    }
                    for item in matches
                ]

                st.dataframe(
                    pd.DataFrame(
                        all_rows
                    ),
                    use_container_width=True,
                    hide_index=True
                )

        st.divider()

    # ========================================================
    # EXTENDED THEME
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🧭 확장 테마 탐색'
        '</div>',
        unsafe_allow_html=True
    )

    selected_theme = st.selectbox(
        "관심 테마",
        list(
            THEMES.keys()
        )
    )

    info = THEMES[
        selected_theme
    ]

    matches = get_theme_matches(
        selected_theme
    )

    st.markdown(
        f"### {selected_theme}"
    )

    st.caption(
        info.get(
            "description",
            ""
        )
    )

    st.write(
        f"자동 매칭 ETF: "
        f"**{len(matches)}개**"
    )

    if matches:

        rows = []

        for item in matches[:12]:

            code = item["code"]

            try:

                raw = load_price_data(
                    code
                )

                if raw.empty:
                    continue

                df = calculate_indicators(
                    raw
                )

                latest = df.iloc[-1]

                judgment, _ = (
                    get_judgment(df)
                )

                rows.append({

                    "코드":
                        code,

                    "ETF":
                        item["name"],

                    "20일":
                        (
                            f"{latest['RET20']:+.1f}%"
                            if pd.notna(
                                latest["RET20"]
                            )
                            else "-"
                        ),

                    "RSI":
                        (
                            f"{latest['RSI14']:.1f}"
                            if pd.notna(
                                latest["RSI14"]
                            )
                            else "-"
                        ),

                    "거래량":
                        (
                            f"{latest['VOL_RATIO']:.1f}배"
                            if pd.notna(
                                latest["VOL_RATIO"]
                            )
                            else "-"
                        ),

                    "현재상태":
                        judgment
                })

            except Exception:

                continue

        if rows:

            st.dataframe(
                pd.DataFrame(
                    rows
                ),
                use_container_width=True,
                hide_index=True
            )

    else:

        st.info(
            "현재 ETF 목록에서 자동 매칭되는 상품이 없습니다."
        )

    # ========================================================
    # GUIDE
    # ========================================================

    with st.expander(
        "💡 미래테마 레이더 사용법"
    ):

        st.markdown(
            """
**① 미래테마 업데이트**

`🔄 미래테마 업데이트`를 누르면 ETF 목록을 다시 확인합니다.

**② 자동 테마 매칭**

ETF 이름과 테마 키워드를 비교하여 관련 ETF를 자동으로 연결합니다.

**③ 가격 흐름 확인**

20일 수익률 / RSI / 거래량을 함께 확인합니다.

**④ ETF 분석**

관심 ETF를 선택하면 상세 분석 화면에서

- 현재 추세
- RSI
- MACD
- 거래량
- 지지 / 저항
- 눌림목
- 돌파
- 추격 위험
- 관심 가격
- 관심 유지 조건

을 확인할 수 있습니다.

**⑤ 자동 갱신**

ETF 목록은 6시간 캐시를 기준으로 자동 갱신됩니다.

앱이 종료되어 있는 동안 계속 백그라운드에서 실행되는 방식은 아니며,
앱을 다시 접속했을 때 갱신 조건을 확인합니다.
"""
        )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "📡 ETF RADAR"
)

page = st.sidebar.radio(
    "메뉴",
    [
        "📌 내 ETF",
        "🚀 미래테마"
    ],
    index=(
        0
        if st.session_state.page
        == "📌 내 ETF"
        else 1
    )
)

st.session_state.page = page


# ============================================================
# MAIN
# ============================================================

if page == "📌 내 ETF":

    render_my_etf()

else:

    render_future_theme()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ETF RADAR · 기술적 지표는 참고용이며 "
    "최종 투자 판단은 사용자의 판단과 책임에 따라 이루어져야 합니다."
)