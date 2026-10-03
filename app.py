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
from datetime import datetime

# ============================================================
# ETF RADAR v11
# Mobile-first ETF analysis dashboard
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# FILE / CACHE
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"
ETF_CACHE_FILE = "etf_universe_cache.json"

ETF_CACHE_HOURS = 6
PRICE_CACHE_TTL = 300


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
        "keywords": [
            "AI반도체",
            "AI반도체핵심",
            "반도체",
            "필라델피아반도체",
            "AI테크"
        ],
        "seeds": [
            "395160",
            "462100",
            "486410",
            "091160",
            "091230",
            "381180"
        ],
        "reason":
            "AI 연산 수요가 늘수록 GPU·메모리·첨단공정 투자와 함께 수요가 연결되는 영역입니다."
    },

    "AI 소프트웨어·빅테크": {
        "keywords": [
            "AI테크",
            "나스닥",
            "테크TOP",
            "S&P500"
        ],
        "seeds": [
            "487240",
            "452330",
            "133690",
            "379810"
        ],
        "reason":
            "AI 서비스·클라우드·빅테크 투자 확대와 함께 실적 성장이 연결되는 영역입니다."
    },

    "데이터센터·AI 인프라": {
        "keywords": [
            "AI",
            "데이터",
            "테크",
            "반도체"
        ],
        "seeds": [
            "487240",
            "395160",
            "471990"
        ],
        "reason":
            "AI 데이터센터 증설은 반도체뿐 아니라 전력·냉각·네트워크 인프라 수요를 동반합니다."
    },

    "전력 인프라": {
        "keywords": [
            "전력",
            "전기",
            "설비"
        ],
        "seeds": [
            "471990",
            "445380"
        ],
        "reason":
            "데이터센터와 산업용 전력 수요 증가가 송배전·전력설비 투자로 이어지는 구조입니다."
    },

    "원자력": {
        "keywords": [
            "원자력",
            "원전"
        ],
        "seeds": [
            "445380",
            "465560"
        ],
        "reason":
            "대규모 전력 수요와 탄소저감 요구가 원전 신규 건설·SMR 관심으로 연결됩니다."
    },

    "냉각·열관리": {
        "keywords": [
            "AI",
            "데이터센터",
            "반도체"
        ],
        "seeds": [
            "395160",
            "471990",
            "487240"
        ],
        "reason":
            "고집적 AI 서버가 늘면서 전력 효율과 열관리 기술의 중요도가 커지고 있습니다."
    },

    "로봇·휴머노이드": {
        "keywords": [
            "로봇",
            "휴머노이드"
        ],
        "seeds": [
            "465610",
            "476250"
        ],
        "reason":
            "자동화·서비스 로봇·휴머노이드 산업의 장기 성장 기대가 연결되는 테마입니다."
    },

    "방산·항공우주": {
        "keywords": [
            "방산",
            "우주",
            "항공"
        ],
        "seeds": [
            "449450",
            "463250",
            "476250"
        ],
        "reason":
            "국방비 확대와 우주산업 투자가 국내 방산·항공우주 기업의 수요로 연결됩니다."
    },

    "조선·해운": {
        "keywords": [
            "조선",
            "해운"
        ],
        "seeds": [
            "139230"
        ],
        "reason":
            "선박 교체 수요와 고부가 선박 발주 사이클의 영향을 받는 산업군입니다."
    },

    "바이오·헬스케어": {
        "keywords": [
            "헬스케어",
            "바이오"
        ],
        "seeds": [
            "329200",
            "266420",
            "462610",
            "143860",
            "227540"
        ],
        "reason":
            "신약개발·의료서비스·바이오시밀러 등 장기 성장 기대가 반영되는 영역입니다."
    },

    "비만치료제": {
        "keywords": [
            "바이오",
            "헬스케어"
        ],
        "seeds": [
            "266420",
            "329200"
        ],
        "reason":
            "GLP-1 계열 치료제 시장 확대와 관련 기업의 연구개발 흐름을 함께 보는 테마입니다."
    },

    "2차전지·ESS": {
        "keywords": [
            "2차전지",
            "배터리",
            "ESS"
        ],
        "seeds": [
            "305540",
            "364980",
            "438320"
        ],
        "reason":
            "전기차와 전력저장장치 확대에 따라 배터리 소재·부품·장비 수요가 연결됩니다."
    },

    "자율주행·전기차": {
        "keywords": [
            "자동차",
            "2차전지",
            "전기차"
        ],
        "seeds": [
            "091180",
            "305540",
            "364980"
        ],
        "reason":
            "전동화와 자율주행 기술의 확산에 따라 자동차와 배터리 생태계가 함께 움직입니다."
    },

    "클라우드·사이버보안": {
        "keywords": [
            "클라우드",
            "AI",
            "테크"
        ],
        "seeds": [
            "487240",
            "452330",
            "133690"
        ],
        "reason":
            "기업 IT 투자와 AI 서비스 확산이 클라우드·보안 인프라 수요로 연결됩니다."
    },

    "콘텐츠·미디어": {
        "keywords": [
            "콘텐츠",
            "미디어"
        ],
        "seeds": [],
        "reason":
            "K-콘텐츠와 글로벌 스트리밍 산업 성장에 영향을 받는 소비·미디어 영역입니다."
    },

    "금융·밸류업": {
        "keywords": [
            "은행",
            "금융",
            "밸류업"
        ],
        "seeds": [
            "091170",
            "091220",
            "139270"
        ],
        "reason":
            "주주환원과 자본효율 개선 정책이 금융주 밸류에이션에 영향을 줄 수 있습니다."
    },

    "배당·인컴": {
        "keywords": [
            "배당",
            "커버드콜",
            "인컴"
        ],
        "seeds": [
            "458730",
            "476480",
            "451780",
            "211560",
            "161510"
        ],
        "reason":
            "현금흐름과 분배금을 중시하는 투자 수요가 연결되는 방어적 성격의 영역입니다."
    },

    "금·원자재": {
        "keywords": [
            "금",
            "원유",
            "원자재"
        ],
        "seeds": [
            "132030",
            "411060",
            "261220"
        ],
        "reason":
            "금리·달러·인플레이션과 글로벌 경기 변화에 따라 가격 흐름이 달라지는 자산군입니다."
    },

    "미국 기술주": {
        "keywords": [
            "미국S&P",
            "나스닥",
            "테크TOP",
            "미국반도체"
        ],
        "seeds": [
            "360750",
            "379800",
            "448290",
            "133690",
            "379810",
            "452330",
            "486410"
        ],
        "reason":
            "미국 대형 기술주와 성장주 흐름을 국내 ETF로 추적하는 대표 테마입니다."
    },
}


# ============================================================
# THEME FLOW
# ============================================================

THEME_CHAIN = [
    ("AI 반도체", "현재 주도"),
    ("데이터센터·AI 인프라", "후속 수혜"),
    ("전력 인프라", "후속 수혜"),
    ("원자력", "관심 확대"),
    ("냉각·열관리", "초기 관심"),
]


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

.block-container {
    max-width: 1180px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}

html, body, [class*="css"] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

.section-title {
    font-size: 1.02rem;
    font-weight: 800;
    margin: 1rem 0 .55rem 0;
    letter-spacing: -0.02em;
}

.small-muted {
    font-size: .76rem;
    color: #7b8494;
    line-height: 1.45;
}

.tiny {
    font-size: .70rem;
    color: #87909e;
}

.radar-card {
    border: 1px solid rgba(128,140,160,.20);
    border-radius: 14px;
    padding: 13px 14px;
    margin: 6px 0;
    background: rgba(255,255,255,.025);
}

.compact-stat {
    border: 1px solid rgba(128,140,160,.18);
    border-radius: 12px;
    padding: 9px 10px;
    min-height: 67px;
    background: rgba(255,255,255,.018);
}

.compact-label {
    font-size: .69rem;
    color: #818a99;
    margin-bottom: 3px;
}

.compact-value {
    font-size: .94rem;
    font-weight: 750;
    line-height: 1.15;
}

.compact-sub {
    font-size: .68rem;
    color: #8d96a5;
    margin-top: 4px;
    line-height: 1.25;
}

.judgment {
    font-size: 1.02rem;
    font-weight: 850;
    line-height: 1.2;
}

.reason {
    font-size: .79rem;
    line-height: 1.5;
    color: #a3abb8;
}

.action {
    font-size: .82rem;
    line-height: 1.45;
    font-weight: 650;
}

.price-number {
    font-size: 1.02rem;
    font-weight: 800;
}

.price-reason {
    font-size: .72rem;
    color: #8b94a3;
    line-height: 1.35;
    margin-top: 3px;
}

.badge {
    display: inline-block;
    padding: 3px 7px;
    border-radius: 999px;
    font-size: .68rem;
    font-weight: 750;
    background: rgba(120,130,150,.12);
    margin-bottom: 5px;
}

.theme-card {
    border: 1px solid rgba(128,140,160,.18);
    border-radius: 15px;
    padding: 13px 14px;
    margin: 7px 0;
}

.theme-name {
    font-size: .96rem;
    font-weight: 850;
    letter-spacing: -0.02em;
}

.theme-reason {
    font-size: .75rem;
    color: #8d96a5;
    line-height: 1.45;
    margin-top: 4px;
}

.theme-etf {
    font-size: .76rem;
    line-height: 1.5;
    margin-top: 7px;
}

.holding-box {
    border: 1px solid rgba(90,150,255,.22);
    border-radius: 14px;
    padding: 12px 13px;
    background: rgba(60,110,200,.05);
}

.good-box {
    border-left: 3px solid #3dbb7a;
    background: rgba(61,187,122,.07);
    padding: 11px 12px;
    border-radius: 9px;
}

.warn-box {
    border-left: 3px solid #e6a23c;
    background: rgba(230,162,60,.07);
    padding: 11px 12px;
    border-radius: 9px;
}

.danger-box {
    border-left: 3px solid #e35d6a;
    background: rgba(227,93,106,.07);
    padding: 11px 12px;
    border-radius: 9px;
}

.info-box {
    border-left: 3px solid #5b8def;
    background: rgba(91,141,239,.07);
    padding: 11px 12px;
    border-radius: 9px;
}

.stButton > button {
    min-height: 40px;
    border-radius: 10px;
}

div[data-testid="stMetricValue"] {
    font-size: 1rem;
}

@media (max-width: 700px) {

    .block-container {
        padding-left: .75rem;
        padding-right: .75rem;
    }

    .section-title {
        margin-top: .8rem;
    }

    .theme-card {
        padding: 11px 12px;
    }

}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# BASIC HELPERS
# ============================================================

def safe_float(value, default=np.nan):
    try:
        return float(value)
    except Exception:
        return default


def fmt_price(value):
    if value is None or pd.isna(value):
        return "-"

    value = float(value)

    if abs(value) >= 1000:
        return f"{value:,.0f}원"

    return f"{value:,.2f}"


def fmt_pct(value):
    if value is None or pd.isna(value):
        return "-"

    return f"{float(value):+.1f}%"


def fmt_volume(value):
    if value is None or pd.isna(value):
        return "-"

    v = float(value)

    if v >= 100000000:
        return f"{v / 100000000:.1f}억"

    if v >= 10000:
        return f"{v / 10000:.1f}만"

    return f"{v:,.0f}"


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ============================================================
# JSON HELPERS
# ============================================================

def safe_read_json(path, default):

    try:

        if os.path.exists(path):

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return data

    except Exception:
        pass

    return default


def safe_write_json(path, data):

    try:

        tmp = path + ".tmp"

        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

        os.replace(tmp, path)

        return True

    except Exception:
        return False


# ============================================================
# SESSION STATE
# ============================================================

def init_state():

    if "selected_code" not in st.session_state:
        st.session_state.selected_code = DEFAULT_WATCHLIST[0]

    if "search_query" not in st.session_state:
        st.session_state.search_query = ""

    if "catalog_updated_at" not in st.session_state:
        st.session_state.catalog_updated_at = ""

    if "etf_universe" not in st.session_state:
        st.session_state.etf_universe = {}

    if "watchlist" not in st.session_state:

        saved = safe_read_json(
            WATCHLIST_FILE,
            DEFAULT_WATCHLIST
        )

        if isinstance(saved, dict):
            saved = list(saved.keys())

        if not isinstance(saved, list):
            saved = DEFAULT_WATCHLIST.copy()

        st.session_state.watchlist = [
            str(x).zfill(6)
            for x in saved
        ]

    if "holdings" not in st.session_state:

        saved_holdings = safe_read_json(
            HOLDINGS_FILE,
            {}
        )

        if not isinstance(saved_holdings, dict):
            saved_holdings = {}

        st.session_state.holdings = saved_holdings

    if "price_cache" not in st.session_state:
        st.session_state.price_cache = {}


init_state()


# ============================================================
# KRX ETF CATALOG
# ============================================================

def parse_krx_payload(payload):

    result = {}

    if isinstance(payload, dict):

        candidates = (
            payload.get("data")
            or payload.get("rows")
            or payload.get("items")
            or []
        )

    elif isinstance(payload, list):

        candidates = payload

    else:

        candidates = []

    for row in candidates:

        if not isinstance(row, dict):
            continue

        code = (
            row.get("ISU_SRT_CD")
            or row.get("isu_srt_cd")
            or row.get("code")
            or row.get("ticker")
        )

        name = (
            row.get("ISU_ABBRV")
            or row.get("isu_abbrv")
            or row.get("name")
            or row.get("itemName")
        )

        if code is None or name is None:
            continue

        code = re.sub(
            r"[^0-9]",
            "",
            str(code)
        )

        if len(code) != 6:
            continue

        name = str(name).strip()

        if name:
            result[code] = name

    return result


def fetch_krx_etf_catalog():

    urls = [
        "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd",
        "https://data-dbg.krx.co.kr/comm/bldAttendant/getJsonData.cmd",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://data.krx.co.kr/",
        "Content-Type":
            "application/x-www-form-urlencoded; charset=UTF-8",
    }

    body = urllib.parse.urlencode({
        "bld":
            "dbms/MDC/STAT/standard/MDCSTAT04601",
        "locale":
            "ko_KR",
        "share":
            "1",
        "csvxls_isNo":
            "false",
    }).encode("utf-8")

    for url in urls:

        try:

            req = urllib.request.Request(
                url,
                data=body,
                headers=headers,
                method="POST"
            )

            with urllib.request.urlopen(
                req,
                timeout=8
            ) as resp:

                raw = resp.read().decode(
                    "utf-8",
                    errors="ignore"
                )

            parsed = json.loads(raw)

            result = parse_krx_payload(parsed)

            if result:
                return result

        except Exception:
            continue

    return {}


def build_etf_catalog(force=False):

    merged = {}

    merged.update(
        FALLBACK_ETF_UNIVERSE
    )

    merged.update(
        BASE_ETF_UNIVERSE
    )

    cache = safe_read_json(
        ETF_CACHE_FILE,
        {}
    )

    cached_at = safe_float(
        cache.get("timestamp")
        if isinstance(cache, dict)
        else np.nan
    )

    cached_data = (
        cache.get("data", {})
        if isinstance(cache, dict)
        else {}
    )

    fresh = (
        not pd.isna(cached_at)
        and (
            datetime.now().timestamp()
            - cached_at
            < ETF_CACHE_HOURS * 3600
        )
    )

    if (
        isinstance(cached_data, dict)
        and fresh
        and not force
    ):

        merged.update({
            str(k).zfill(6): str(v)
            for k, v in cached_data.items()
        })

    else:

        krx = fetch_krx_etf_catalog()

        if krx:

            merged.update(krx)

            safe_write_json(
                ETF_CACHE_FILE,
                {
                    "timestamp":
                        datetime.now().timestamp(),
                    "data":
                        krx,
                }
            )

            st.session_state.catalog_updated_at = now_text()

        elif isinstance(cached_data, dict):

            merged.update({
                str(k).zfill(6): str(v)
                for k, v in cached_data.items()
            })

            if not st.session_state.catalog_updated_at:
                st.session_state.catalog_updated_at = "캐시 자료 사용"

    st.session_state.etf_universe = dict(
        sorted(
            merged.items(),
            key=lambda x: x[1]
        )
    )

    return st.session_state.etf_universe


if not st.session_state.etf_universe:

    build_etf_catalog(
        force=False
    )


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


def is_held(code):

    item = st.session_state.holdings.get(
        code,
        {}
    )

    return bool(
        item.get(
            "held",
            False
        )
    )


def get_holding(code):

    item = st.session_state.holdings.get(
        code,
        {}
    )

    return {
        "held":
            bool(item.get("held", False)),

        "avg_price":
            safe_float(
                item.get("avg_price"),
                0.0
            ),

        "quantity":
            safe_float(
                item.get("quantity"),
                0.0
            ),
    }


def set_holding(
    code,
    held,
    avg_price=0.0,
    quantity=0.0
):

    st.session_state.holdings[code] = {

        "held":
            bool(held),

        "avg_price":
            float(avg_price or 0),

        "quantity":
            float(quantity or 0),
    }

    save_holdings()


def add_watchlist(code):

    code = str(code).zfill(6)

    if code not in st.session_state.watchlist:

        st.session_state.watchlist.append(
            code
        )

        save_watchlist()

    st.session_state.selected_code = code


def remove_watchlist(code):

    if code in st.session_state.watchlist:

        st.session_state.watchlist.remove(
            code
        )

        save_watchlist()

    if (
        st.session_state.selected_code
        == code
    ):

        if st.session_state.watchlist:

            st.session_state.selected_code = (
                st.session_state.watchlist[0]
            )

        else:

            st.session_state.selected_code = (
                next(
                    iter(
                        st.session_state.etf_universe
                    ),
                    "395160"
                )
            )


# ============================================================
# PRICE DATA
# ============================================================

def fetch_naver_data(
    code,
    count=260
):

    url = (
        "https://fchart.stock.naver.com/"
        f"sise.nhn?symbol={urllib.parse.quote(str(code))}"
        f"&timeframe=day"
        f"&count={int(count)}"
        f"&requestType=0"
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
        ) as resp:

            xml_data = resp.read()

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

            if len(parts) < 6:
                continue

            rows.append(
                parts[:6]
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
                "Volume"
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
            "Volume"
        ]:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

        df = (
            df.dropna(
                subset=[
                    "Date",
                    "Close"
                ]
            )
            .sort_values("Date")
            .set_index("Date")
        )

        return df

    except Exception:

        return pd.DataFrame()


def fetch_yahoo_data(
    code,
    period="1y"
):

    try:

        ticker = yf.Ticker(
            f"{code}.KS"
        )

        df = ticker.history(
            period=period,
            auto_adjust=False
        )

        if (
            df is None
            or df.empty
        ):
            return pd.DataFrame()

        return (
            df[
                [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume"
                ]
            ]
            .dropna(
                subset=["Close"]
            )
        )

    except Exception:

        return pd.DataFrame()


def load_price_data(
    code,
    force=False
):

    code = str(code).zfill(6)

    cached = st.session_state.price_cache.get(
        code
    )

    if cached and not force:

        ts, cached_df = cached

        if (
            datetime.now().timestamp()
            - ts
            < PRICE_CACHE_TTL
        ):

            return cached_df.copy()

    df = fetch_naver_data(
        code,
        260
    )

    if len(df) < 30:

        df = fetch_yahoo_data(
            code,
            "1y"
        )

    if not df.empty:

        st.session_state.price_cache[code] = (
            datetime.now().timestamp(),
            df.copy()
        )

    return df.copy()


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

def add_indicators(df):

    if df.empty:
        return df

    out = df.copy()

    close = out["Close"]

    # Moving averages
    out["MA5"] = close.rolling(5).mean()
    out["MA20"] = close.rolling(20).mean()
    out["MA60"] = close.rolling(60).mean()
    out["MA120"] = close.rolling(120).mean()

    # RSI
    delta = close.diff()

    gain = delta.clip(
        lower=0
    )

    loss = -delta.clip(
        upper=0
    )

    avg_gain = gain.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14
    ).mean()

    rs = (
        avg_gain
        /
        avg_loss.replace(
            0,
            np.nan
        )
    )

    out["RSI14"] = (
        100
        -
        (
            100
            /
            (1 + rs)
        )
    )

    out["RSI14"] = out[
        "RSI14"
    ].fillna(50)

    # MACD
    ema12 = close.ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = close.ewm(
        span=26,
        adjust=False
    ).mean()

    out["MACD"] = (
        ema12 - ema26
    )

    out["MACD_SIGNAL"] = (
        out["MACD"]
        .ewm(
            span=9,
            adjust=False
        )
        .mean()
    )

    out["MACD_HIST"] = (
        out["MACD"]
        -
        out["MACD_SIGNAL"]
    )

    # Bollinger
    out["BB_MID"] = (
        close.rolling(20).mean()
    )

    std20 = close.rolling(20).std()

    out["BB_UPPER"] = (
        out["BB_MID"]
        +
        2 * std20
    )

    out["BB_LOWER"] = (
        out["BB_MID"]
        -
        2 * std20
    )

    # Volume
    out["VOL20"] = (
        out["Volume"]
        .rolling(20)
        .mean()
    )

    out["VOL_RATIO"] = (
        out["Volume"]
        /
        out["VOL20"].replace(
            0,
            np.nan
        )
    )

    # Returns
    out["RET1"] = (
        close.pct_change(1)
        * 100
    )

    out["RET5"] = (
        close.pct_change(5)
        * 100
    )

    out["RET20"] = (
        close.pct_change(20)
        * 100
    )

    out["RET60"] = (
        close.pct_change(60)
        * 100
    )

    # High / Low
    out["HIGH20"] = (
        out["High"]
        .rolling(20)
        .max()
    )

    out["LOW20"] = (
        out["Low"]
        .rolling(20)
        .min()
    )

    out["MA20_GAP"] = (
        close
        /
        out["MA20"]
        - 1
    ) * 100

    out["MA60_GAP"] = (
        close
        /
        out["MA60"]
        - 1
    ) * 100

    return out


def latest(df):

    return df.iloc[-1]


# ============================================================
# TREND / EXPLANATION
# ============================================================

def trend_state(r):

    c = safe_float(
        r.get("Close")
    )

    ma20 = safe_float(
        r.get("MA20")
    )

    ma60 = safe_float(
        r.get("MA60")
    )

    if (
        np.isnan(c)
        or np.isnan(ma20)
    ):
        return "데이터 부족"

    if (
        not np.isnan(ma60)
        and c > ma20 > ma60
    ):
        return "상승 추세"

    if (
        not np.isnan(ma60)
        and c < ma20 < ma60
    ):
        return "하락 추세"

    if c > ma20:
        return "단기 상승"

    return "조정 / 횡보"


def explain_rsi(rsi):

    if pd.isna(rsi):
        return "RSI 데이터가 부족합니다."

    if rsi >= 70:
        return (
            f"RSI {rsi:.0f}으로 과열권입니다. "
            "상승 추세여도 단기 추격은 신중하게 봅니다."
        )

    if rsi >= 55:
        return (
            f"RSI {rsi:.0f}으로 "
            "매수 우위가 유지되는 구간입니다."
        )

    if rsi >= 45:
        return (
            f"RSI {rsi:.0f}으로 "
            "방향성이 강하지 않은 중립 구간입니다."
        )

    if rsi >= 30:
        return (
            f"RSI {rsi:.0f}으로 "
            "조정 압력이 있지만 과매도는 아닙니다."
        )

    return (
        f"RSI {rsi:.0f}으로 과매도권입니다. "
        "반등 신호 확인이 필요합니다."
    )


def explain_volume(ratio):

    if pd.isna(ratio):
        return "거래량 데이터가 부족합니다."

    if ratio >= 1.5:
        return (
            f"20일 평균 대비 거래량 {ratio:.1f}배로 "
            "수급이 크게 유입된 상태입니다."
        )

    if ratio >= 1.1:
        return (
            f"20일 평균 대비 거래량 {ratio:.1f}배로 "
            "평소보다 활발합니다."
        )

    if ratio <= 0.7:
        return (
            f"20일 평균 대비 거래량 {ratio:.1f}배로 "
            "거래가 위축되어 있습니다."
        )

    return (
        f"20일 평균 대비 거래량 {ratio:.1f}배로 "
        "평범한 수준입니다."
    )


def explain_trend(r):

    state = trend_state(r)

    if state == "상승 추세":

        return (
            "현재가가 20일선과 60일선 위에 있어 "
            "단기·중기 추세가 같은 방향입니다."
        )

    if state == "하락 추세":

        return (
            "현재가가 20일선과 60일선 아래에 있어 "
            "추세 회복 전까지 보수적으로 봅니다."
        )

    if state == "단기 상승":

        return (
            "20일선 위이지만 "
            "중기선과의 관계가 완전히 정렬되지는 않았습니다."
        )

    return (
        "단기 추세가 약해 "
        "20일선 회복 여부를 확인할 필요가 있습니다."
    )


def explain_macd(r):

    macd = safe_float(
        r.get("MACD")
    )

    signal = safe_float(
        r.get("MACD_SIGNAL")
    )

    hist = safe_float(
        r.get("MACD_HIST")
    )

    if (
        np.isnan(macd)
        or np.isnan(signal)
    ):
        return "MACD 데이터가 부족합니다."

    if (
        macd > signal
        and hist >= 0
    ):

        return (
            "MACD가 시그널 위에 있어 "
            "단기 모멘텀이 우호적입니다."
        )

    if (
        macd < signal
        and hist < 0
    ):

        return (
            "MACD가 시그널 아래에 있어 "
            "단기 모멘텀이 약합니다."
        )

    return (
        "MACD 방향이 혼조여서 "
        "가격과 거래량 확인이 필요합니다."
    )


# ============================================================
# JUDGEMENT
# ============================================================

def get_judgment(
    df,
    code=None
):

    if (
        df.empty
        or len(df) < 30
    ):

        return (
            "데이터 부족",
            "최근 가격 데이터가 충분하지 않습니다.",
            "추가 데이터가 쌓인 뒤 판단합니다."
        )

    r = latest(df)

    c = safe_float(
        r["Close"]
    )

    ma20 = safe_float(
        r["MA20"]
    )

    ma60 = safe_float(
        r["MA60"]
    )

    rsi = safe_float(
        r["RSI14"]
    )

    vr = safe_float(
        r["VOL_RATIO"]
    )

    held = (
        is_held(code)
        if code
        else False
    )

    # 중기 추세 이탈
    if (
        not np.isnan(ma60)
        and c < ma60
    ):

        if held:

            return (
                "리스크 재검토",

                "현재가가 60일선 아래이고 "
                "중기 추세가 약합니다.",

                "보유 중이라면 추가매수보다 "
                "60일선 회복 여부를 먼저 확인합니다."
            )

        return (
            "관망 후 확인",

            "현재가가 60일선 아래라 "
            "중기 추세가 아직 약합니다.",

            "미보유라면 60일선 회복과 "
            "거래량 증가를 확인한 뒤 접근합니다."
        )

    # 과열
    if (
        rsi >= 72
        or (
            not np.isnan(ma20)
            and c > ma20 * 1.08
        )
    ):

        if held:

            return (
                "보유 유지 · 추격 자제",

                "추세는 유지되지만 RSI 또는 "
                "20일선 이격이 커 단기 과열 신호가 있습니다.",

                "보유 중이면 추격매수보다 "
                "눌림 확인을 우선합니다."
            )

        return (
            "추격 주의",

            "추세는 좋지만 RSI 또는 "
            "20일선 이격이 커 단기 과열 신호가 있습니다.",

            "미보유라면 현재가 추격보다 "
            "20일선 부근 눌림을 기다립니다."
        )

    # 거래량을 동반한 상승
    if (
        not np.isnan(ma20)
        and c > ma20
        and vr >= 1.15
    ):

        if held:

            return (
                "보유 유지",

                "20일선 위에서 거래량이 평균보다 늘며 "
                "추세가 유지되고 있습니다.",

                "보유 중이면 추세 유지 여부를 보면서 "
                "추가매수는 지지 확인 시만 검토합니다."
            )

        return (
            "돌파 확인",

            "20일선 위에서 거래량이 늘어 "
            "단기 수급이 개선되고 있습니다.",

            "미보유라면 고점 추격보다 "
            "돌파 안착 또는 눌림을 확인합니다."
        )

    # 20일선 부근
    if (
        not np.isnan(ma20)
        and c >= ma20 * 0.97
        and c <= ma20 * 1.03
    ):

        if held:

            return (
                "보유 유지 · 눌림 확인",

                "현재가가 20일선 부근으로 조정받아 "
                "추세 확인 구간입니다.",

                "20일선 지지 여부를 보고 "
                "추가매수 여부를 판단합니다."
            )

        return (
            "눌림목 관심",

            "현재가가 20일선 부근이라 "
            "추세가 유지된다면 진입 후보 구간입니다.",

            "20일선 지지와 거래량 회복을 확인합니다."
        )

    # 기본
    if held:

        return (
            "보유 유지",

            "중기 추세가 크게 훼손되지 않았지만 "
            "강한 수급 신호도 제한적입니다.",

            "추세선을 유지하는지 확인하면서 대응합니다."
        )

    return (
        "관망",

        "현재 위치에서 뚜렷한 "
        "돌파·눌림 신호가 강하지 않습니다.",

        "20일선 방향과 거래량 변화를 기다립니다."
    )


# ============================================================
# TRADE SCENARIO
# ============================================================

def get_trade_scenario(
    df,
    code
):

    if df.empty:
        return []

    r = latest(df)

    ma20 = safe_float(
        r["MA20"]
    )

    ma60 = safe_float(
        r["MA60"]
    )

    high20 = safe_float(
        r["HIGH20"]
    )

    held = is_held(code)

    scenarios = []

    if not np.isnan(ma20):

        if held:

            scenarios.append(
                (
                    "① 지지 확인",
                    fmt_price(ma20),
                    "20일선 지지 + 거래량 회복이면 "
                    "보유 추세가 유지되는지 확인합니다."
                )
            )

        else:

            scenarios.append(
                (
                    "① 눌림 접근",
                    fmt_price(ma20),
                    "20일선 부근에서 하락이 멈추고 "
                    "거래량이 안정되면 관심 구간으로 봅니다."
                )
            )

    if not np.isnan(high20):

        scenarios.append(
            (
                "② 돌파 확인",
                fmt_price(high20),
                "최근 20일 고점 돌파와 거래량 증가가 "
                "함께 나오는지 확인합니다."
            )
        )

    if not np.isnan(ma60):

        if held:

            scenarios.append(
                (
                    "③ 중기 추세 방어",
                    fmt_price(ma60),
                    "60일선 이탈은 중기 추세가 약해졌다는 신호로 "
                    "대응 강도를 재검토합니다."
                )
            )

        else:

            scenarios.append(
                (
                    "③ 위험 기준",
                    fmt_price(ma60),
                    "60일선 아래에서는 신규 진입보다 "
                    "추세 회복 확인을 우선합니다."
                )
            )

    return scenarios


# ============================================================
# PRICE LEVELS
# ============================================================

def calculate_levels(df):

    if df.empty:
        return {}

    r = latest(df)

    c = safe_float(
        r["Close"]
    )

    ma20 = safe_float(
        r["MA20"]
    )

    ma60 = safe_float(
        r["MA60"]
    )

    low20 = safe_float(
        r["LOW20"]
    )

    high20 = safe_float(
        r["HIGH20"]
    )

    first_interest = (
        ma20
        if not np.isnan(ma20)
        else c
    )

    core_support = (
        ma60
        if not np.isnan(ma60)
        else low20
    )

    breakout = high20

    candidates = [
        ma60,
        low20
    ]

    valid_candidates = [
        x for x in candidates
        if not np.isnan(x)
    ]

    risk = (
        min(valid_candidates)
        if valid_candidates
        else np.nan
    )

    return {

        "current":
            c,

        "first_interest":
            first_interest,

        "core_support":
            core_support,

        "breakout":
            breakout,

        "risk":
            risk,

        "ma20":
            ma20,

        "ma60":
            ma60,

        "low20":
            low20,

        "high20":
            high20,
    }


def level_reason(
    key,
    levels
):

    if key == "first_interest":

        return (
            "최근 20일 단기 추세선. "
            "상승 추세에서 눌림이 멈추는지 확인하는 1차 기준입니다."
        )

    if key == "core_support":

        if not pd.isna(
            levels.get("ma60")
        ):

            return (
                "60일 중기 추세선. "
                "이 선의 지지 여부가 중기 추세 유지에 중요합니다."
            )

        return (
            "최근 20일 저점. "
            "단기 매물대가 확인되는 가격대입니다."
        )

    if key == "breakout":

        return (
            "최근 20일 최고가. "
            "돌파와 거래량 증가가 함께 나타나는지 확인하는 기준입니다."
        )

    if key == "risk":

        return (
            "중기 추세가 약해지는 하단 기준. "
            "이탈 시 기존 시나리오를 다시 점검합니다."
        )

    return "현재 시장가격입니다."


# ============================================================
# THEME MATCHING
# ============================================================

def get_theme_matches(
    theme_name,
    limit=5
):

    theme = THEMES.get(
        theme_name,
        {}
    )

    seeds = theme.get(
        "seeds",
        []
    )

    keywords = theme.get(
        "keywords",
        []
    )

    universe = (
        st.session_state.etf_universe
    )

    ranked = []

    for code, name in universe.items():

        score = 0

        if code in seeds:
            score += 100

        for kw in keywords:

            if kw in name:
                score += 20

        if score > 0:

            ranked.append(
                (
                    score,
                    code,
                    name
                )
            )

    ranked.sort(
        key=lambda x: (
            -x[0],
            x[2]
        )
    )

    return [
        (code, name)
        for _, code, name
        in ranked[:limit]
    ]


def get_themes_for_etf(code):

    name = st.session_state.etf_universe.get(
        code,
        ""
    )

    result = []

    for theme_name, info in THEMES.items():

        if (
            code in info.get("seeds", [])
            or any(
                k in name
                for k in info.get(
                    "keywords",
                    []
                )
            )
        ):

            result.append(
                theme_name
            )

    return result


def theme_stage(theme_name):

    for name, stage in THEME_CHAIN:

        if name == theme_name:
            return stage

    return "관심 테마"


def theme_stage_badge(stage):

    return {

        "현재 주도":
            "🔥 현재 주도",

        "후속 수혜":
            "➡️ 후속 수혜",

        "관심 확대":
            "👀 관심 확대",

        "초기 관심":
            "🌱 초기 관심",

        "관심 테마":
            "👀 관심 테마",

        "관찰 필요":
            "⚠️ 관찰 필요",

    }.get(
        stage,
        stage
    )


def theme_snapshot(
    theme_name,
    limit=3
):

    matches = get_theme_matches(
        theme_name,
        limit=limit
    )

    rows = []

    for code, name in matches:

        df = add_indicators(
            load_price_data(code)
        )

        if df.empty:
            continue

        r = latest(df)

        rows.append({

            "code":
                code,

            "name":
                name,

            "price":
                safe_float(
                    r.get("Close")
                ),

            "ret20":
                safe_float(
                    r.get("RET20")
                ),

            "rsi":
                safe_float(
                    r.get("RSI14")
                ),

            "vol":
                safe_float(
                    r.get("VOL_RATIO")
                ),

            "trend":
                trend_state(r),
        })

    return rows


# ============================================================
# TOP UI
# ============================================================

def render_top_selector():

    st.markdown(
        "## 📡 ETF RADAR"
    )

    st.caption(
        "ETF 찾기 → 관심종목 → 보유여부 → "
        "기술적 판단 → 대응 가격 순서로 한 화면에서 확인합니다."
    )

    # --------------------------------------------------------
    # ETF SEARCH
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">① ETF 찾기</div>',
        unsafe_allow_html=True
    )

    q_col, refresh_col = st.columns(
        [5, 1]
    )

    with q_col:

        query = st.text_input(
            "ETF 검색",

            value=
                st.session_state.search_query,

            placeholder=
                "ETF명 또는 6자리 종목코드 입력",

            label_visibility=
                "collapsed",

            key=
                "top_search_box",
        )

        st.session_state.search_query = query

    with refresh_col:

        if st.button(
            "시장 새로고침",
            use_container_width=True,
            key="catalog_refresh"
        ):

            build_etf_catalog(
                force=True
            )

            st.rerun()

    q = (
        st.session_state.search_query
        .strip()
        .lower()
    )

    universe = (
        st.session_state.etf_universe
    )

    if q:

        matches = [
            (c, n)
            for c, n in universe.items()
            if (
                q in c.lower()
                or q in n.lower()
            )
        ]

    else:

        matches = [
            (c, universe[c])
            for c in st.session_state.watchlist
            if c in universe
        ]

        if not matches:

            matches = list(
                universe.items()
            )[:20]

    if matches:

        labels = [
            f"{name}  ·  {code}"
            for code, name
            in matches[:80]
        ]

        current_code = (
            st.session_state.selected_code
        )

        default_idx = 0

        for i, (code, _) in enumerate(
            matches[:80]
        ):

            if code == current_code:

                default_idx = i

                break

        chosen_label = st.selectbox(
            "검색 결과",
            labels,
            index=default_idx,
            key="top_search_result",
            label_visibility="collapsed",
        )

        chosen_index = labels.index(
            chosen_label
        )

        chosen_code = matches[
            chosen_index
        ][0]

        if (
            chosen_code
            != st.session_state.selected_code
        ):

            st.session_state.selected_code = (
                chosen_code
            )

    elif q:

        st.warning(
            "검색 결과가 없습니다. "
            "ETF명 일부 또는 정확한 6자리 종목코드를 입력해 보세요."
        )

    # --------------------------------------------------------
    # WATCHLIST
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">② 관심종목</div>',
        unsafe_allow_html=True
    )

    if st.session_state.watchlist:

        watch_options = []

        for code in (
            st.session_state.watchlist
        ):

            name = universe.get(
                code,
                f"ETF {code}"
            )

            watch_options.append(
                f"{name}  ·  {code}"
            )

        current_watch_label = (
            f"{universe.get(
                st.session_state.selected_code,
                st.session_state.selected_code
            )}  ·  {st.session_state.selected_code}"
        )

        if current_watch_label in watch_options:

            idx = watch_options.index(
                current_watch_label
            )

        else:

            idx = 0

        wc1, wc2 = st.columns(
            [5, 1]
        )

        with wc1:

            selected_watch = st.selectbox(
                "관심 ETF",
                watch_options,
                index=idx,
                key="watch_select",
                label_visibility="collapsed"
            )

            selected_index = (
                watch_options.index(
                    selected_watch
                )
            )

            selected_code = (
                st.session_state.watchlist[
                    selected_index
                ]
            )

            st.session_state.selected_code = (
                selected_code
            )

        with wc2:

            if st.button(
                "삭제",
                key="watch_remove",
                use_container_width=True
            ):

                remove_watchlist(
                    selected_code
                )

                st.rerun()

    else:

        st.info(
            "관심종목이 없습니다. "
            "위에서 ETF를 검색한 후 추가해 주세요."
        )

    selected_code = (
        st.session_state.selected_code
    )

    name = universe.get(
        selected_code,
        selected_code
    )

    if selected_code not in (
        st.session_state.watchlist
    ):

        if st.button(
            f"＋ {name} 관심종목에 추가",
            use_container_width=True,
            key="add_current_watch"
        ):

            add_watchlist(
                selected_code
            )

            st.rerun()

    # --------------------------------------------------------
    # HOLDING STATUS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">③ 보유 여부</div>',
        unsafe_allow_html=True
    )

    holding = get_holding(
        selected_code
    )

    held_value = st.radio(
        "보유 여부",
        ["미보유", "보유"],
        index=
            1
            if holding["held"]
            else 0,
        horizontal=True,
        key=
            f"held_radio_{selected_code}",
        label_visibility="collapsed"
    )

    held = (
        held_value == "보유"
    )

    if held:

        h1, h2, h3 = st.columns(
            3
        )

        with h1:

            avg = st.number_input(
                "평균매수가",

                min_value=0.0,

                value=float(
                    holding["avg_price"]
                ),

                step=100.0,

                format="%.0f",

                key=
                    f"avg_price_{selected_code}"
            )

        with h2:

            qty = st.number_input(
                "보유수량",

                min_value=0.0,

                value=float(
                    holding["quantity"]
                ),

                step=1.0,

                format="%.0f",

                key=
                    f"quantity_{selected_code}"
            )

        with h3:

            st.markdown(
                """
<div class="compact-stat">
<div class="compact-label">상태</div>
<div class="compact-value">보유 중</div>
<div class="compact-sub">
보유 기준으로 대응 시나리오를 표시합니다.
</div>
</div>
""",
                unsafe_allow_html=True
            )

        set_holding(
            selected_code,
            True,
            avg,
            qty
        )

    else:

        if holding["held"]:

            set_holding(
                selected_code,
                False,
                0,
                0
            )

        st.markdown(
            """
<div class="small-muted">
미보유 상태에서는 신규 진입 기준으로
눌림목·돌파·위험가격을 안내합니다.
</div>
""",
            unsafe_allow_html=True
        )

    return selected_code


# ============================================================
# CURRENT SNAPSHOT
# ============================================================

def render_snapshot(
    df,
    code
):

    r = latest(df)

    price = safe_float(
        r["Close"]
    )

    rsi = safe_float(
        r["RSI14"]
    )

    ret20 = safe_float(
        r["RET20"]
    )

    vol = safe_float(
        r["VOL_RATIO"]
    )

    ret5 = safe_float(
        r["RET5"]
    )

    st.markdown(
        '<div class="section-title">④ 현재 상태</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(
        5
    )

    items = [

        (
            "현재가",
            fmt_price(price),
            f"1일 {fmt_pct(safe_float(r['RET1']))}"
        ),

        (
            "RSI(14)",
            f"{rsi:.0f}"
            if not pd.isna(rsi)
            else "-",
            "과열 70 · 과매도 30"
        ),

        (
            "20일선",
            fmt_price(
                safe_float(
                    r["MA20"]
                )
            ),
            f"현재 대비 {fmt_pct(
                safe_float(
                    r['MA20_GAP']
                )
            )}"
        ),

        (
            "거래량",
            f"{vol:.1f}배"
            if not pd.isna(vol)
            else "-",
            "20일 평균 대비"
        ),

        (
            "20일 수익",
            fmt_pct(ret20),
            f"5일 {fmt_pct(ret5)}"
        ),
    ]

    for col, (
        label,
        value,
        sub
    ) in zip(
        cols,
        items
    ):

        with col:

            st.markdown(
                f"""
<div class="compact-stat">
<div class="compact-label">{label}</div>
<div class="compact-value">{value}</div>
<div class="compact-sub">{sub}</div>
</div>
""",
                unsafe_allow_html=True
            )

    # --------------------------------------------------------
    # JUDGEMENT
    # --------------------------------------------------------

    (
        judgment,
        reason,
        action
    ) = get_judgment(
        df,
        code
    )

    st.markdown(
        '<div class="section-title">⑤ 판단 · 근거 · 대응</div>',
        unsafe_allow_html=True
    )

    a, b, c = st.columns(
        [1.05, 2.1, 2.1]
    )

    with a:

        st.markdown(
            f"""
<div class="radar-card">
<div class="compact-label">현재 판단</div>
<div class="judgment">{judgment}</div>
</div>
""",
            unsafe_allow_html=True
        )

    with b:

        st.markdown(
            f"""
<div class="radar-card">
<div class="compact-label">판단 근거</div>
<div class="reason">
{reason}
</div>

<div class="reason" style="margin-top:5px">
{explain_trend(r)}
<br>
{explain_rsi(rsi)}
</div>
</div>
""",
            unsafe_allow_html=True
        )

    with c:

        st.markdown(
            f"""
<div class="radar-card">
<div class="compact-label">대응</div>
<div class="action">
{action}
</div>

<div class="reason" style="margin-top:5px">
{explain_volume(vol)}
<br>
{explain_macd(r)}
</div>
</div>
""",
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # HOLDING RESULT
    # --------------------------------------------------------

    holding = get_holding(
        code
    )

    if (
        holding["held"]
        and holding["avg_price"] > 0
    ):

        pnl_pct = (
            price
            /
            holding["avg_price"]
            - 1
        ) * 100

        pnl_amt = (
            price
            -
            holding["avg_price"]
        ) * holding["quantity"]

        box_cls = (
            "good-box"
            if pnl_pct >= 0
            else "danger-box"
        )

        st.markdown(
            f"""
<div class="{box_cls}">
<b>보유 기준</b>
· 평균매수가 {fmt_price(holding["avg_price"])}
· 현재 평가수익률 <b>{fmt_pct(pnl_pct)}</b>
· 평가손익 {pnl_amt:,.0f}원

<br>

<span class="small-muted">
보유 중에는 신규매수 신호와 별도로
평균매수가·중기 추세를 함께 고려합니다.
</span>

</div>
""",
            unsafe_allow_html=True
        )


# ============================================================
# CORE PRICE LEVEL
# ============================================================

def render_price_levels(
    df,
    code
):

    levels = calculate_levels(
        df
    )

    st.markdown(
        '<div class="section-title">⑥ 핵심 가격 · 왜 이 가격인가?</div>',
        unsafe_allow_html=True
    )

    level_items = [

        (
            "1차 관심가격",
            "first_interest"
        ),

        (
            "핵심지지",
            "core_support"
        ),

        (
            "돌파기준",
            "breakout"
        ),

        (
            "위험가격",
            "risk"
        ),
    ]

    cols = st.columns(
        4
    )

    for col, (
        label,
        key
    ) in zip(
        cols,
        level_items
    ):

        value = levels.get(
            key,
            np.nan
        )

        reason = level_reason(
            key,
            levels
        )

        with col:

            st.markdown(
                f"""
<div class="radar-card">
<div class="compact-label">{label}</div>
<div class="price-number">
{fmt_price(value)}
</div>

<div class="price-reason">
{reason}
</div>
</div>
""",
                unsafe_allow_html=True
            )

    st.markdown(
        """
<div class="small-muted">
가격은 자동 계산된 기술적 기준입니다.
실제 매매에서는 장중 변동·수급·시장환경을 함께 확인하세요.
</div>
""",
        unsafe_allow_html=True
    )

    scenarios = get_trade_scenario(
        df,
        code
    )

    if scenarios:

        st.markdown(
            '<div class="section-title">대응 시나리오</div>',
            unsafe_allow_html=True
        )

        for (
            title,
            price,
            desc
        ) in scenarios:

            st.markdown(
                f"""
<div class="radar-card">
<b>{title}</b>
&nbsp;&nbsp;
<span class="price-number">
{price}
</span>
<br>

<span class="reason">
{desc}
</span>

</div>
""",
                unsafe_allow_html=True
            )


# ============================================================
# RECENT MOVEMENT
# ============================================================

def render_recent_movement(
    df
):

    r = latest(df)

    st.markdown(
        '<div class="section-title">⑦ 최근 흐름</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(
        4
    )

    data = [

        (
            "1일",
            safe_float(
                r.get("RET1")
            )
        ),

        (
            "5일",
            safe_float(
                r.get("RET5")
            )
        ),

        (
            "20일",
            safe_float(
                r.get("RET20")
            )
        ),

        (
            "60일",
            safe_float(
                r.get("RET60")
            )
        ),
    ]

    for col, (
        label,
        val
    ) in zip(
        cols,
        data
    ):

        with col:

            st.markdown(
                f"""
<div class="compact-stat">
<div class="compact-label">{label} 변화</div>
<div class="compact-value">
{fmt_pct(val)}
</div>
</div>
""",
                unsafe_allow_html=True
            )


# ============================================================
# INTEREST CONDITIONS
# ============================================================

def render_interest_conditions(
    df,
    code
):

    r = latest(df)

    price = safe_float(
        r["Close"]
    )

    ma20 = safe_float(
        r["MA20"]
    )

    high20 = safe_float(
        r["HIGH20"]
    )

    vol = safe_float(
        r["VOL_RATIO"]
    )

    rsi = safe_float(
        r["RSI14"]
    )

    held = is_held(
        code
    )

    conditions = []

    if not np.isnan(ma20):

        conditions.append(
            (
                "20일선",
                price >= ma20 * .985,
                f"현재가 {fmt_price(price)} / "
                f"20일선 {fmt_price(ma20)}"
            )
        )

    if not np.isnan(high20):

        conditions.append(
            (
                "20일 고점",
                price >= high20 * .99,
                f"고점 {fmt_price(high20)} 부근"
            )
        )

    conditions.append(
        (
            "거래량",
            vol >= 1.1
            if not np.isnan(vol)
            else False,

            f"평균 대비 {vol:.1f}배"
            if not np.isnan(vol)
            else "데이터 부족"
        )
    )

    conditions.append(
        (
            "RSI",
            45 <= rsi <= 68
            if not np.isnan(rsi)
            else False,

            f"RSI {rsi:.0f}"
            if not np.isnan(rsi)
            else "데이터 부족"
        )
    )

    st.markdown(
        '<div class="section-title">⑧ 관심 조건</div>',
        unsafe_allow_html=True
    )

    for (
        name,
        ok,
        detail
    ) in conditions:

        icon = (
            "✓"
            if ok
            else "·"
        )

        st.markdown(
            f"""
<div class="radar-card">
<b>{icon} {name}</b>
&nbsp;&nbsp;
<span class="reason">
{detail}
</span>
</div>
""",
            unsafe_allow_html=True
        )

    if held:

        st.markdown(
            """
<div class="small-muted">
보유 중이면 위 조건을 “신규 진입”보다
“추세 유지/추가매수 여부” 판단에 활용합니다.
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
        '<div class="section-title">⑨ 연결 테마</div>',
        unsafe_allow_html=True
    )

    if themes:

        st.write(
            " · ".join(
                themes[:6]
            )
        )

    else:

        st.caption(
            "현재 자동 키워드 기준으로 "
            "연결된 대표 테마가 없습니다."
        )


# ============================================================
# CHART
# ============================================================

def render_chart(
    df,
    code
):

    st.markdown(
        '<div class="section-title">⑩ 가격 차트</div>',
        unsafe_allow_html=True
    )

    chart_df = (
        df.tail(180)
        .copy()
    )

    if chart_df.empty:

        st.info(
            "차트 데이터가 없습니다."
        )

        return

    fig = make_subplots(

        rows=2,

        cols=1,

        shared_xaxes=True,

        vertical_spacing=0.05,

        row_heights=[
            0.72,
            0.28
        ],
    )

    fig.add_trace(

        go.Candlestick(

            x=chart_df.index,

            open=chart_df["Open"],

            high=chart_df["High"],

            low=chart_df["Low"],

            close=chart_df["Close"],

            name="가격",
        ),

        row=1,
        col=1
    )

    fig.add_trace(

        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA20"],
            name="20일선",
            mode="lines"
        ),

        row=1,
        col=1
    )

    fig.add_trace(

        go.Scatter(
            x=chart_df.index,
            y=chart_df["MA60"],
            name="60일선",
            mode="lines"
        ),

        row=1,
        col=1
    )

    fig.add_trace(

        go.Scatter(
            x=chart_df.index,
            y=chart_df["BB_UPPER"],
            name="볼린저 상단",
            mode="lines",
            line=dict(
                dash="dot"
            )
        ),

        row=1,
        col=1
    )

    fig.add_trace(

        go.Scatter(
            x=chart_df.index,
            y=chart_df["BB_LOWER"],
            name="볼린저 하단",
            mode="lines",
            line=dict(
                dash="dot"
            )
        ),

        row=1,
        col=1
    )

    fig.add_trace(

        go.Bar(
            x=chart_df.index,
            y=chart_df["Volume"],
            name="거래량"
        ),

        row=2,
        col=1
    )

    fig.update_layout(

        height=520,

        margin=dict(
            l=8,
            r=8,
            t=10,
            b=10
        ),

        xaxis_rangeslider_visible=False,

        hovermode="x unified",

        dragmode="pan",

        legend=dict(
            orientation="h",
            y=1.02,
            x=0
        ),

        font=dict(
            size=10
        ),
    )

    fig.update_xaxes(
        showgrid=False
    )

    fig.update_yaxes(
        showgrid=True,
        row=1,
        col=1
    )

    fig.update_yaxes(
        showgrid=False,
        row=2,
        col=1
    )

    # --------------------------------------------------------
    # MOBILE CHART CONFIG
    # --------------------------------------------------------

    config = {

        "scrollZoom":
            False,

        "displaylogo":
            False,

        "displayModeBar":
            True,

        "modeBarButtonsToRemove":
            [
                "lasso2d",
                "select2d"
            ],

        "doubleClick":
            "reset",
    }

    st.plotly_chart(

        fig,

        use_container_width=True,

        config=config,

        key=
            f"chart_{code}"
    )

    st.caption(
        "차트 안에서 휠 확대는 꺼두었습니다. "
        "모바일 페이지 스크롤을 우선하고, "
        "확대/축소는 차트의 버튼을 사용하세요."
    )


# ============================================================
# ETF DETAIL
# ============================================================

def render_etf_detail(
    code
):

    name = st.session_state.etf_universe.get(
        code,
        f"ETF {code}"
    )

    st.markdown(
        f"## {name}"
    )

    st.caption(
        f"종목코드 {code} · 데이터 조회 {now_text()}"
    )

    df = load_price_data(
        code
    )

    df = add_indicators(
        df
    )

    if (
        df.empty
        or len(df) < 30
    ):

        st.error(
            "가격 데이터를 불러오지 못했습니다. "
            "잠시 후 다시 시도하거나 다른 ETF를 선택해 주세요."
        )

        return

    render_snapshot(
        df,
        code
    )

    render_price_levels(
        df,
        code
    )

    render_recent_movement(
        df
    )

    render_interest_conditions(
        df,
        code
    )

    render_etf_themes(
        code
    )

    render_chart(
        df,
        code
    )


# ============================================================
# FUTURE THEME CARD
# ============================================================

def render_theme_card(
    theme_name
):

    stage = theme_stage(
        theme_name
    )

    info = THEMES[
        theme_name
    ]

    rows = theme_snapshot(
        theme_name,
        3
    )

    badge = theme_stage_badge(
        stage
    )

    st.markdown(
        f"""
<div class="theme-card">

<div class="badge">
{badge}
</div>

<div class="theme-name">
{theme_name}
</div>

<div class="theme-reason">
{info["reason"]}
</div>
""",
        unsafe_allow_html=True
    )

    if rows:

        for row in rows:

            st.markdown(
                f"""
<div class="theme-etf">

<b>{row["name"]}</b>

· {fmt_price(row["price"])}

· 20일 {fmt_pct(row["ret20"])}

· RSI {row["rsi"]:.0f}

· 거래량 {row["vol"]:.1f}배

· <b>{row["trend"]}</b>

</div>
""",
                unsafe_allow_html=True
            )

    else:

        st.markdown(
            """
<div class="theme-etf">
연결 ETF의 가격 데이터를 확인하지 못했습니다.
</div>
""",
            unsafe_allow_html=True
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# FUTURE THEME PAGE
# ============================================================

def render_future_theme():

    st.markdown(
        "## 🔭 미래테마 레이더"
    )

    st.caption(
        "현재 시장의 흐름에서 "
        "후속 수혜·관심 확대 가능성을 빠르게 확인하는 화면입니다."
    )

    top_col, date_col = st.columns(
        [1, 3]
    )

    with top_col:

        if st.button(
            "🔄 시장 다시 탐색",
            use_container_width=True,
            key="theme_refresh"
        ):

            build_etf_catalog(
                force=True
            )

            # 사용자가 누른 '시장 다시 탐색'에 한해
            # 가격 데이터도 새로 읽습니다.
            st.session_state.price_cache = {}

            st.rerun()

    with date_col:

        updated = (
            st.session_state.catalog_updated_at
            or "자동 캐시 기준"
        )

        st.markdown(
            f"""
<div class="small-muted"
style="padding-top:10px">

마지막 시장 탐색:
{updated}

<br>

테마 가격 캐시는 내부적으로만 사용하며
사용자 화면에는 개발자용 초기화 버튼을 노출하지 않습니다.

</div>
""",
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # NOW
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">지금 볼 테마</div>',
        unsafe_allow_html=True
    )

    for (
        theme_name,
        _stage
    ) in THEME_CHAIN:

        render_theme_card(
            theme_name
        )

    # --------------------------------------------------------
    # CORE THEME TABLE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">핵심 테마</div>',
        unsafe_allow_html=True
    )

    rows = []

    for (
        theme_name,
        stage
    ) in THEME_CHAIN:

        matches = theme_snapshot(
            theme_name,
            1
        )

        if not matches:
            continue

        x = matches[0]

        rows.append({

            "상태":
                theme_stage_badge(stage),

            "테마":
                theme_name,

            "대표 ETF":
                x["name"],

            "현재가":
                fmt_price(
                    x["price"]
                ),

            "20일":
                fmt_pct(
                    x["ret20"]
                ),

            "RSI":
                f"{x['rsi']:.0f}",

            "거래량":
                f"{x['vol']:.1f}배",
        })

    if rows:

        table = pd.DataFrame(
            rows,
            columns=[
                "상태",
                "테마",
                "대표 ETF",
                "현재가",
                "20일",
                "RSI",
                "거래량"
            ]
        )

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "현재 테마 데이터를 불러오지 못했습니다."
        )

    # --------------------------------------------------------
    # ALL THEMES
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">전체 테마 탐색</div>',
        unsafe_allow_html=True
    )

    selected_theme = st.selectbox(
        "테마 선택",
        list(THEMES.keys()),
        key="future_theme_select"
    )

    if selected_theme:

        render_theme_card(
            selected_theme
        )


# ============================================================
# MAIN
# ============================================================

page = st.radio(
    "메뉴",
    [
        "내 ETF",
        "미래테마"
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="main_page"
)


if page == "내 ETF":

    selected = render_top_selector()

    st.divider()

    render_etf_detail(
        selected
    )

else:

    render_future_theme()