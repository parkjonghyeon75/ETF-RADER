# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import os
from datetime import datetime


# ============================================================
# ETF RADAR
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# 기본 ETF
#
# 한글명을 Unicode escape로 저장하여
# 소스파일 인코딩 문제를 최대한 차단
# ============================================================

BASE_ETFS = {
    "395160": "\u004b\u004f\u0044\u0045\u0058 AI\uBC18\uB3C4\uCCB4\uD575\uC2EC\uC7A5\uBE44",
    "487240": "\u004b\u004f\u0044\u0045\u0058 AI\uBC18\uB3C4\uCCB4",
    "471990": "\u004b\u004f\u0044\u0045\u0058 AI\uBC18\uB3C4\uCCB4TOP2Plus",

    "133690": "TIGER \uBBF8\uAD6D\uB098\uC2A4\uB2E4\uC2A4100",
    "360750": "TIGER \uBBF8\uAD6DS&P500",
    "458730": "TIGER \uAE00\uB85C\uBC8CAI&\uB85C\uBD07",
    "381170": "TIGER \uBBF8\uAD6D\uD14C\uD06CTOP10 INDXX",

    "396500": "TIGER \uBC18\uB3C4\uCCB4",
    "091160": "\u004b\u004f\u0044\u0045\u0058 \uBC18\uB3C4\uCCB4",
    "091180": "\u004b\u004f\u0044\u0045\u0058 \uC790\uB3D9\uCC28",
    "139260": "TIGER 200 IT",
    "305720": "\u004b\u004f\u0044\u0045\u0058 2\uCC28\uC804\uC9C0\uC0B0\uC5C5",
    "364690": "\u004b\u004f\u0044\u0045\u0058 \uD601\uC2E0\uAE30\uC220\uD14C\uB9C8\uC561\uD2F0\uBE0C",

    "117700": "\u004b\u004f\u0044\u0045\u0058 \uAC74\uC124",
    "140700": "\u004b\u004f\u0044\u0045\u0058 \uBCF4\uD5D8",
    "144600": "\u004b\u004f\u0044\u0045\u0058 \uC740\uD589",
    "102780": "\u004b\u004f\u0044\u0045\u0058 \uC0BC\uC131\uADF8\uB8F9",

    "261220": "\u004b\u004f\u0044\u0045\u0058 WTI\uC6D0\uC720\uC120\uBB3C(H)",

    "449170": "TIGER \uAE00\uB85C\uBC8CAI\uC778\uD504\uB77C\uC561\uD2F0\uBE0C",
    "434060": "TIGER \uAE00\uB85C\uBC8CAI&\uBC18\uB3C4\uCCB4\uC561\uD2F0\uBE0C",

    "464240": "\u004b\u004f\u0044\u0045\u0058 AI\uC804\uB825\uD575\uC2EC\uC124\uBE44",
    "487130": "\u004b\u004f\u0044\u0045\u0058 AI\uC804\uB825\uC778\uD504\uB77C",

    "475050": "ACE \uAE00\uB85C\uBC8C\uBC18\uB3C4\uCCB4TOP4 Plus",
    "469150": "ACE AI\uBC18\uB3C4\uCCB4\uD3EC\uCEE4\uC2A4",

    "130730": "KOSEF \uB2E8\uAE30\uC790\uAE08",
    "161510": "PLUS \uACE0\uBC30\uB2F9\uC8FC",
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
# 미래테마
# ============================================================

FUTURE_CHAIN = {
    "\uD604\uC7AC\uC8FC\uB3C4": {
        "AI\uBC18\uB3C4\uCCB4\u00B7\uD575\uC2EC\uC7A5\uBE44": [
            "395160",
            "487240",
            "471990",
            "469150",
        ],
        "\uBBF8\uAD6D \uBE45\uD14C\uD06C & \uD601\uC2E0": [
            "133690",
            "360750",
            "381170",
        ],
    },

    "\uB2E4\uC74C\uC218\uD61C": {
        "\uB370\uC774\uD130\uC13C\uD130\u00B7AI \uC778\uD504\uB77C": [
            "449170",
            "434060",
        ],
        "\uC804\uB825 \uC778\uD504\uB77C & \uC124\uBE44": [
            "464240",
            "487130",
        ],
        "\uBC14\uC774\uC624\u00B7\uD5EC\uC2A4\uCF00\uC5B4 \uD601\uC2E0": [
            "364690",
        ],
    },

    "\uCD08\uAE30\uAD00\uC2EC": {
        "\uB85C\uBCF4\uD2F1\uC2A4 & AI \uC790\uC728\uC8FC\uD589": [
            "458730",
        ],
        "\uC6B0\uC8FC\uD56D\uACF5 & \uBC29\uC0B0": [
            "364690",
        ],
        "SMR\u00B7\uC6D0\uC790\uB825 \uC5D0\uB108\uC9C0": [
            "130730",
            "161510",
        ],
    },
}


# ============================================================
# 파일
# ============================================================

WATCHLIST_FILE = "watchlist.json"
HOLDINGS_FILE = "holdings.json"
UNIVERSE_FILE = "etf_universe_cache.json"


# ============================================================
# JSON
# ============================================================

def load_json(path, default):

    try:

        if os.path.exists(path):

            with open(
                path,
                "r",
                encoding="utf-8",
            ) as f:

                return json.load(f)

    except Exception:
        pass

    return default


def save_json(path, data):

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

    except Exception:
        pass


# ============================================================
# SESSION
# ============================================================

if "watchlist" not in st.session_state:

    st.session_state.watchlist = load_json(
        WATCHLIST_FILE,
        DEFAULT_WATCHLIST.copy(),
    )

if "holdings" not in st.session_state:

    st.session_state.holdings = load_json(
        HOLDINGS_FILE,
        [],
    )

if "etf_universe" not in st.session_state:

    st.session_state.etf_universe = load_json(
        UNIVERSE_FILE,
        {},
    )

if "selected_code" not in st.session_state:

    st.session_state.selected_code = None

if "future_detail_code" not in st.session_state:

    st.session_state.future_detail_code = None

if "theme_last_update" not in st.session_state:

    st.session_state.theme_last_update = None

if "nav" not in st.session_state:

    st.session_state.nav = "\uD83D\uDCCA \uB0B4 ETF"

if "search_code" not in st.session_state:

    st.session_state.search_code = None

if "watch_code" not in st.session_state:

    st.session_state.watch_code = None


# ============================================================
# 공통
# ============================================================

def normalize_code(code):

    return str(code).strip().zfill(6)


def get_etf_name(code):

    code = normalize_code(code)

    if code in BASE_ETFS:

        return BASE_ETFS[code]

    universe = st.session_state.get(
        "etf_universe",
        {},
    )

    item = universe.get(code)

    if isinstance(item, str):

        return item

    if isinstance(item, dict):

        return (
            item.get("name")
            or item.get("ETF명")
            or item.get("etf_name")
            or code
        )

    return code


def safe_num(value):

    try:

        if pd.isna(value):

            return np.nan

        return float(value)

    except Exception:

        return np.nan


# ============================================================
# ETF 검색
# ============================================================

def search_etfs(keyword):

    keyword = str(keyword).strip().lower()

    if not keyword:

        return []

    universe = dict(BASE_ETFS)

    cached = st.session_state.get(
        "etf_universe",
        {},
    )

    if isinstance(cached, dict):

        for code, item in cached.items():

            code = normalize_code(code)

            if isinstance(item, str):

                universe[code] = item

            elif isinstance(item, dict):

                name = (
                    item.get("name")
                    or item.get("ETF명")
                    or item.get("etf_name")
                )

                if name:

                    universe[code] = name

    results = []

    for code, name in universe.items():

        code = normalize_code(code)

        if (
            keyword in code.lower()
            or keyword in str(name).lower()
        ):

            results.append(
                {
                    "code": code,
                    "name": str(name),
                }
            )

    results.sort(
        key=lambda x: (
            not x["code"].startswith(keyword),
            x["name"],
        )
    )

    return results


# ============================================================
# Yahoo
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner=False,
)
def fetch_yahoo(code):

    code = normalize_code(code)

    try:

        df = yf.download(
            f"{code}.KS",
            period="2y",
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False,
        )

        if df is None or df.empty:

            return pd.DataFrame()

        if isinstance(
            df.columns,
            pd.MultiIndex,
        ):

            df.columns = [
                c[0] if isinstance(c, tuple) else c
                for c in df.columns
            ]

        required = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]

        for col in required:

            if col not in df.columns:

                return pd.DataFrame()

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce",
            )

        df = df.dropna(
            subset=["Close"]
        )

        return df

    except Exception:

        return pd.DataFrame()


# ============================================================
# 기술지표
# ============================================================

def calculate_indicators(df):

    if df is None or df.empty:

        return pd.DataFrame()

    d = df.copy()

    close = d["Close"]

    d["MA20"] = close.rolling(20).mean()
    d["MA60"] = close.rolling(60).mean()
    d["MA120"] = close.rolling(120).mean()

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = (
        avg_gain
        /
        avg_loss.replace(
            0,
            np.nan,
        )
    )

    d["RSI14"] = 100 - (
        100 / (1 + rs)
    )

    d["VOL20"] = (
        d["Volume"]
        .rolling(20)
        .mean()
    )

    d["VOL_RATIO"] = (
        d["Volume"]
        /
        d["VOL20"].replace(
            0,
            np.nan,
        )
    )

    d["RET5"] = (
        close.pct_change(5)
        * 100
    )

    d["RET20"] = (
        close.pct_change(20)
        * 100
    )

    d["HIGH20"] = (
        d["High"]
        .rolling(20)
        .max()
    )

    d["LOW20"] = (
        d["Low"]
        .rolling(20)
        .min()
    )

    d["HIGH60"] = (
        d["High"]
        .rolling(60)
        .max()
    )

    d["LOW60"] = (
        d["Low"]
        .rolling(60)
        .min()
    )

    return d


# ============================================================
# 종합판단
# ============================================================

def get_judgment(df):

    if df.empty:

        return {
            "title": "\uB370\uC774\uD130 \uBD80\uC871",
            "action": "\uBD84\uC11D \uB300\uAE30",
            "reasons": [],
        }

    x = df.iloc[-1]

    close = safe_num(x["Close"])
    ma20 = safe_num(x["MA20"])
    ma60 = safe_num(x["MA60"])
    rsi = safe_num(x["RSI14"])
    vol = safe_num(x["VOL_RATIO"])
    ret5 = safe_num(x["RET5"])

    reasons = []

    # --------------------------------------------------------
    # 추세
    # --------------------------------------------------------

    if (
        not np.isnan(close)
        and not np.isnan(ma20)
        and not np.isnan(ma60)
    ):

        if close > ma20 > ma60:

            trend = "\uC0C1\uC2B9\uCD94\uC138"

            reasons.append(
                f"\uD604\uC7AC\uAC00 {close:,.0f}\uC6D0\uB85C "
                f"20\uC77C\uC120 {ma20:,.0f}\uC6D0\uACFC "
                f"60\uC77C\uC120 {ma60:,.0f}\uC6D0 \uC704\uC5D0 \uC788\uC5B4 "
                "\uB2E8\uAE30\u00B7\uC911\uAE30 \uCD94\uC138\uAC00 \uC0C1\uBC29\uC785\uB2C8\uB2E4."
            )

        elif close < ma20 < ma60:

            trend = "\uD558\uB77D\uCD94\uC138"

            reasons.append(
                f"\uD604\uC7AC\uAC00 {close:,.0f}\uC6D0\uB85C "
                f"20\uC77C\uC120 {ma20:,.0f}\uC6D0\uACFC "
                f"60\uC77C\uC120 {ma60:,.0f}\uC6D0 \uC544\uB798\uC5D0 \uC788\uC5B4 "
                "\uCD94\uC138 \uD68C\uBCF5 \uD655\uC778\uC774 \uD544\uC694\uD569\uB2C8\uB2E4."
            )

        else:

            trend = "\uD63C\uC870\uAD6C\uAC04"

            reasons.append(
                "\uD604\uC7AC\uAC00\uC640 \uC774\uB3D9\uD3C9\uADE0\uC120\uC758 \uBC30\uCE58\uAC00 "
                "\uC77C\uCE58\uD558\uC9C0 \uC54A\uC544 \uBC29\uD5A5 \uD655\uC778\uC774 \uD544\uC694\uD569\uB2C8\uB2E4."
            )

    else:

        trend = "\uB370\uC774\uD130 \uBD80\uC871"

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    if not np.isnan(rsi):

        if rsi >= 70:

            reasons.append(
                f"RSI {rsi:.1f}\uB85C \uB2E8\uAE30 \uACFC\uC5F4\uAD8C\uC5D0 \uC811\uADFC\uD574 "
                "\uCD94\uACA9\uB9E4\uC218\uC5D0 \uC8FC\uC758\uAC00 \uD544\uC694\uD569\uB2C8\uB2E4."
            )

        elif rsi <= 30:

            reasons.append(
                f"RSI {rsi:.1f}\uB85C \uACFC\uB9E4\uB3C4\uAD8C\uC785\uB2C8\uB2E4."
            )

        else:

            reasons.append(
                f"RSI {rsi:.1f}\uB85C \uADF9\uB2E8\uC801\uC778 \uACFC\uC5F4\u00B7\uACFC\uB9E4\uB3C4 \uC0C1\uD0DC\uB294 \uC544\uB2D9\uB2C8\uB2E4."
            )

    # --------------------------------------------------------
    # 거래량
    # --------------------------------------------------------

    if not np.isnan(vol):

        if vol >= 1.5:

            reasons.append(
                f"\uAC70\uB798\uB7C9\uC774 20\uC77C \uD3C9\uADE0\uC758 {vol:.1f}\uBC30\uB85C "
                "\uC218\uAE09 \uAC15\uD654\uAC00 \uD655\uC778\uB429\uB2C8\uB2E4."
            )

        elif vol <= 0.7:

            reasons.append(
                f"\uAC70\uB798\uB7C9\uC774 20\uC77C \uD3C9\uADE0\uC758 {vol:.1f}\uBC30\uB85C "
                "\uC218\uAE09\uC774 \uC57D\uD574 \uC788\uC5B4 \uCD94\uACA9\uBCF4\uB2E4 \uD655\uC778\uC774 \uD544\uC694\uD569\uB2C8\uB2E4."
            )

        else:

            reasons.append(
                "\uAC70\uB798\uB7C9\uC740 \uD3C9\uADE0\uC801\uC778 \uC218\uC900\uC785\uB2C8\uB2E4."
            )

    # --------------------------------------------------------
    # 종합
    # --------------------------------------------------------

    if trend == "\uC0C1\uC2B9\uCD94\uC138":

        if not np.isnan(rsi) and rsi >= 70:

            title = "\uC0C1\uC2B9\uCD94\uC138 \u00B7 \uACFC\uC5F4\uC8FC\uC758"

            action = (
                "\uBCF4\uC720 \uC911\uC2EC \u00B7 "
                "\uCD94\uACA9\uB9E4\uC218 \uC8FC\uC758"
            )

        elif not np.isnan(vol) and vol >= 1.5:

            title = "\uC0C1\uC2B9\uCD94\uC138 \u00B7 \uC218\uAE09\uAC15\uD654"

            action = (
                "\uBCF4\uC720 \uC911\uC2EC \u00B7 "
                "\uB204\uB9BC\uBAA9 \uB300\uC751"
            )

        else:

            title = "\uC0C1\uC2B9\uCD94\uC138"

            action = (
                "\uBCF4\uC720 \uC911\uC2EC \u00B7 "
                "\uC870\uC815 \uC2DC \uBD84\uD560\uB300\uC751"
            )

    elif trend == "\uD558\uB77D\uCD94\uC138":

        title = "\uD558\uB77D\uCD94\uC138"

        action = (
            "\uC2E0\uADDC\uB9E4\uC218 \uBCF4\uC218\uC801 \uC811\uADFC"
        )

    else:

        title = "\uD63C\uC870\uAD6C\uAC04"

        action = (
            "\uBC29\uD5A5 \uD655\uC778 \uD6C4 \uB300\uC751"
        )

    return {
        "title": title,
        "action": action,
        "reasons": reasons,
    }


# ============================================================
# 가격구간
# ============================================================

def calculate_levels(df):

    if df.empty:

        return {
            "ma20": np.nan,
            "support1": np.nan,
            "support2": np.nan,
            "breakout": np.nan,
            "risk": np.nan,
            "high20": np.nan,
            "low20": np.nan,
            "low60": np.nan,
        }

    x = df.iloc[-1]

    ma20 = safe_num(x["MA20"])
    ma60 = safe_num(x["MA60"])
    low20 = safe_num(x["LOW20"])
    low60 = safe_num(x["LOW60"])
    high20 = safe_num(x["HIGH20"])

    support_candidates = [
        v
        for v in [
            ma20,
            ma60,
            low20,
        ]
        if not np.isnan(v)
    ]

    if support_candidates:

        support1 = max(
            support_candidates
        )

        support2 = min(
            support_candidates
        )

    else:

        support1 = np.nan
        support2 = np.nan

    risk_candidates = [
        v
        for v in [
            ma60,
            low20,
            low60,
        ]
        if not np.isnan(v)
    ]

    risk = (
        min(risk_candidates)
        if risk_candidates
        else np.nan
    )

    return {
        "ma20": ma20,
        "support1": support1,
        "support2": support2,
        "breakout": high20,
        "risk": risk,
        "high20": high20,
        "low20": low20,
        "low60": low60,
    }


# ============================================================
# 금액별 대응
# ============================================================

def render_price_response(df):

    if df.empty:

        return

    last = df.iloc[-1]

    current = safe_num(last["Close"])

    levels = calculate_levels(df)

    ma20 = levels["ma20"]
    support1 = levels["support1"]
    support2 = levels["support2"]
    breakout = levels["breakout"]
    risk = levels["risk"]

    st.markdown(
        "### 💰 가격별 대응안"
    )

    table = pd.DataFrame(
        [
            [
                "현재가",
                current,
                "추격보다 현재 추세와 거래량 확인",
            ],
            [
                "1차 관심",
                ma20,
                "20일선 부근 지지 확인 후 1차 분할",
            ],
            [
                "주요 지지",
                support1,
                "지지 확인 시 2차 분할 대응 검토",
            ],
            [
                "2차 지지",
                support2,
                "강한 조정 구간. 추세 훼손 여부 확인",
            ],
            [
                "돌파 기준",
                breakout,
                "거래량 동반 돌파 시 상승 재가속 확인",
            ],
            [
                "위험 기준",
                risk,
                "이탈 시 신규매수보다 추세 회복 확인",
            ],
        ],
        columns=[
            "구간",
            "가격",
            "대응",
        ],
    )

    table["가격"] = table["가격"].apply(
        lambda x:
        f"{x:,.0f}원"
        if not pd.isna(x)
        else "-"
    )

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "※ 가격구간은 이동평균선과 최근 고저점을 이용한 기술적 참고구간입니다."
    )


# ============================================================
# 판단근거
# ============================================================

def render_judgment(df):

    result = get_judgment(df)

    with st.container(border=True):

        st.markdown(
            f"#### {result['title']}"
        )

        st.write(
            f"**현재 대응:** {result['action']}"
        )

        st.markdown(
            "**판단근거**"
        )

        for reason in result["reasons"]:

            st.write(
                f"• {reason}"
            )


# ============================================================
# 시나리오
# ============================================================

def render_scenarios(df):

    levels = calculate_levels(df)

    support1 = levels["support1"]
    support2 = levels["support2"]
    breakout = levels["breakout"]
    risk = levels["risk"]

    def fmt(x):

        if np.isnan(x):
            return "-"

        return f"{x:,.0f}원"

    st.markdown(
        "### 🧭 대응 시나리오"
    )

    with st.container(border=True):

        st.markdown(
            "#### 📈 상승 시나리오"
        )

        st.write(
            f"{fmt(breakout)} 부근의 최근 고점을 거래량과 함께 "
            "돌파하면 상승 재가속 여부를 확인합니다. "
            "돌파 직후 급등한다면 추격보다는 재눌림을 기다리는 "
            "대응이 가능합니다."
        )

        st.markdown(
            "#### ↔️ 눌림목 시나리오"
        )

        st.write(
            f"{fmt(support1)} → {fmt(support2)} 구간으로 "
            "조정될 경우 이동평균선 지지 여부와 거래량 감소를 "
            "확인합니다. 지지 확인 시 분할 접근을 검토합니다."
        )

        st.markdown(
            "#### ⚠️ 하락 시나리오"
        )

        st.write(
            f"{fmt(risk)} 아래로 이탈하고 거래량까지 증가하면 "
            "기존 상승 시나리오가 약화될 수 있습니다. "
            "이 경우 신규매수보다 추세 회복 여부를 우선 확인합니다."
        )


# ============================================================
# 차트
# ============================================================

def render_chart(df):

    if df.empty:

        st.info(
            "차트 데이터가 없습니다."
        )

        return

    d = df.tail(180)

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

    fig.add_trace(
        go.Scatter(
            x=d.index,
            y=d["MA20"],
            name="MA20",
            mode="lines",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=d.index,
            y=d["MA60"],
            name="MA60",
            mode="lines",
        )
    )

    fig.update_layout(
        height=430,
        margin=dict(
            l=5,
            r=5,
            t=20,
            b=5,
        ),
        xaxis_rangeslider_visible=False,
        template="plotly_white",
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
            "displayModeBar": False,
        },
    )


# ============================================================
# 전체 ETF 분석
# ============================================================

def render_analysis(code):

    code = normalize_code(code)

    name = get_etf_name(code)

    st.subheader(name)

    st.caption(
        f"\uC885\uBAA9\uCF54\uB4DC {code}"
    )

    df = fetch_yahoo(code)

    if df.empty:

        st.error(
            "\uC2DC\uC7A5 \uB370\uC774\uD130\uB97C \uAC00\uC838\uC624\uC9C0 \uBABB\uD588\uC2B5\uB2C8\uB2E4."
        )

        return

    df = calculate_indicators(df)

    if df.empty:

        st.error(
            "\uBD84\uC11D \uAC00\uB2A5\uD55C \uB370\uC774\uD130\uAC00 \uC5C6\uC2B5\uB2C8\uB2E4."
        )

        return

    last = df.iloc[-1]

    price = safe_num(
        last["Close"]
    )

    if len(df) >= 2:

        previous = safe_num(
            df.iloc[-2]["Close"]
        )

    else:

        previous = np.nan

    if (
        not np.isnan(price)
        and not np.isnan(previous)
        and previous != 0
    ):

        change = (
            price / previous - 1
        ) * 100

    else:

        change = np.nan

    # ========================================================
    # 현재가
    # ========================================================

    with st.container(border=True):

        if np.isnan(change):

            st.metric(
                "\uD604\uC7AC\uAC00",
                f"{price:,.0f}\uC6D0",
            )

        else:

            st.metric(
                "\uD604\uC7AC\uAC00",
                f"{price:,.0f}\uC6D0",
                f"{change:+.2f}%",
            )

    # ========================================================
    # 판단근거
    # ========================================================

    st.markdown(
        "### 📌 현재 판단"
    )

    render_judgment(df)

    # ========================================================
    # 가격별 대응
    # ========================================================

    render_price_response(df)

    # ========================================================
    # 시나리오
    # ========================================================

    render_scenarios(df)

    # ========================================================
    # 보조지표 요약
    # ========================================================

    st.markdown(
        "### 📊 보조지표"
    )

    rsi = safe_num(
        last["RSI14"]
    )

    volume_ratio = safe_num(
        last["VOL_RATIO"]
    )

    ret5 = safe_num(
        last["RET5"]
    )

    ret20 = safe_num(
        last["RET20"]
    )

    a, b, c, d = st.columns(4)

    with a:

        st.metric(
            "RSI",
            (
                f"{rsi:.1f}"
                if not np.isnan(rsi)
                else "-"
            ),
        )

    with b:

        st.metric(
            "거래량",
            (
                f"{volume_ratio:.1f}배"
                if not np.isnan(volume_ratio)
                else "-"
            ),
        )

    with c:

        st.metric(
            "5일 수익률",
            (
                f"{ret5:+.1f}%"
                if not np.isnan(ret5)
                else "-"
            ),
        )

    with d:

        st.metric(
            "20일 수익률",
            (
                f"{ret20:+.1f}%"
                if not np.isnan(ret20)
                else "-"
            ),
        )

    # ========================================================
    # 차트
    # ========================================================

    st.markdown(
        "### 📈 차트"
    )

    render_chart(df)


# ============================================================
# 분석 토글 버튼
# ============================================================

def analysis_button(
    code,
    key_prefix,
):

    code = normalize_code(code)

    active = (
        st.session_state.selected_code
        == code
    )

    if active:

        label = (
            "🔽 ETF 분석 닫기"
        )

    else:

        label = (
            "📊 ETF 분석"
        )

    return st.button(
        label,
        use_container_width=True,
        key=f"{key_prefix}_{code}",
    )


# ============================================================
# 내 ETF + ETF 찾기
# ============================================================

def render_my_etf():

    st.title(
        "📊 내 ETF"
    )

    st.caption(
        "ETF 찾기와 관심 ETF를 한 화면에서 관리하고 바로 분석합니다."
    )

    # ========================================================
    # ETF 찾기
    # ========================================================

    st.markdown(
        "### 🔎 ETF 찾기"
    )

    keyword = st.text_input(
        "ETF 검색",
        placeholder="\uC885\uBAA9\uBA85 \uB610\uB294 \uC885\uBAA9\uCF54\uB4DC \uC785\uB825",
        label_visibility="collapsed",
        key="search_keyword",
    )

    results = search_etfs(
        keyword
    )

    if results:

        # ====================================================
        # 드롭다운에는 숫자만
        # ====================================================

        codes = [
            normalize_code(
                item["code"]
            )
            for item in results
        ]

        selected_search = st.selectbox(
            "검색결과",
            codes,
            key="search_code",
            label_visibility="collapsed",
        )

        selected_search = normalize_code(
            selected_search
        )

        selected_name = get_etf_name(
            selected_search
        )

        # ====================================================
        # 선택된 ETF
        # ====================================================

        with st.container(border=True):

            st.subheader(
                selected_name
            )

            st.caption(
                f"\uC885\uBAA9\uCF54\uB4DC {selected_search}"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "➕ 관심 ETF 추가",
                    use_container_width=True,
                    key="add_search_etf",
                ):

                    if (
                        selected_search
                        not in st.session_state.watchlist
                    ):

                        st.session_state.watchlist.append(
                            selected_search
                        )

                        save_json(
                            WATCHLIST_FILE,
                            st.session_state.watchlist,
                        )

                        st.success(
                            "\uAD00\uC2EC ETF\uC5D0 \uCD94\uAC00\uD588\uC2B5\uB2C8\uB2E4."
                        )

                    else:

                        st.info(
                            "\uC774\uBBF8 \uAD00\uC2EC ETF\uC5D0 \uB4F1\uB85D\uB418\uC5B4 \uC788\uC2B5\uB2C8\uB2E4."
                        )

            with col2:

                if analysis_button(
                    selected_search,
                    "search_analysis",
                ):

                    if (
                        st.session_state.selected_code
                        == selected_search
                    ):

                        st.session_state.selected_code = None

                    else:

                        st.session_state.selected_code = (
                            selected_search
                        )

                    st.rerun()

            # -----------------------------------------------
            # 검색한 ETF 분석
            # -----------------------------------------------

            if (
                st.session_state.selected_code
                == selected_search
            ):

                st.divider()

                render_analysis(
                    selected_search
                )

    elif keyword.strip():

        st.info(
            "\uAC80\uC0C9 \uACB0\uACFC\uAC00 \uC5C6\uC2B5\uB2C8\uB2E4."
        )

    else:

        st.caption(
            "\uC885\uBAA9\uBA85 \uB610\uB294 \uC885\uBAA9\uCF54\uB4DC\uB97C \uC785\uB825\uD574 \uC8FC\uC138\uC694."
        )

    # ========================================================
    # 관심 ETF
    # ========================================================

    st.divider()

    st.markdown(
        "### ⭐ 관심 ETF"
    )

    watchlist = [
        normalize_code(
            code
        )
        for code in st.session_state.watchlist
    ]

    watchlist = list(
        dict.fromkeys(
            watchlist
        )
    )

    if not watchlist:

        st.info(
            "\uC544\uC9C1 \uAD00\uC2EC ETF\uAC00 \uC5C6\uC2B5\uB2C8\uB2E4."
        )

    else:

        selected_watch = st.selectbox(
            "\uAD00\uC2EC ETF \uC120\uD0DD",
            watchlist,
            key="watch_code",
            label_visibility="collapsed",
        )

        selected_watch = normalize_code(
            selected_watch
        )

        watch_name = get_etf_name(
            selected_watch
        )

        with st.container(border=True):

            st.subheader(
                watch_name
            )

            st.caption(
                f"\uC885\uBAA9\uCF54\uB4DC {selected_watch}"
            )

            col1, col2 = st.columns(2)

            with col1:

                if analysis_button(
                    selected_watch,
                    "watch_analysis",
                ):

                    if (
                        st.session_state.selected_code
                        == selected_watch
                    ):

                        st.session_state.selected_code = None

                    else:

                        st.session_state.selected_code = (
                            selected_watch
                        )

                    st.rerun()

            with col2:

                if st.button(
                    "🗑 관심 ETF 삭제",
                    use_container_width=True,
                    key="delete_watch",
                ):

                    if (
                        selected_watch
                        in st.session_state.watchlist
                    ):

                        st.session_state.watchlist.remove(
                            selected_watch
                        )

                        save_json(
                            WATCHLIST_FILE,
                            st.session_state.watchlist,
                        )

                        if (
                            st.session_state.selected_code
                            == selected_watch
                        ):

                            st.session_state.selected_code = None

                        st.rerun()


        # ====================================================
        # 관심 ETF 분석
        # ====================================================

        if (
            st.session_state.selected_code
            == selected_watch
        ):

            st.divider()

            render_analysis(
                selected_watch
            )


# ============================================================
# 미래테마
# ============================================================

def render_future_theme():

    st.title(
        "🔮 미래테마"
    )

    st.caption(
        "\uD604\uC7AC \uC8FC\uB3C4 \u2192 \uB2E4\uC74C \uC218\uD61C \u2192 \uCD08\uAE30 \uAD00\uC2EC"
    )

    if st.button(
        "🔄 테마 업데이트",
        key="theme_update",
    ):

        st.session_state.theme_last_update = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        )

        st.rerun()

    if st.session_state.theme_last_update:

        st.caption(
            "\uB9C8\uC9C0\uB9C9 \uC5C5\uB370\uC774\uD2B8: "
            + st.session_state.theme_last_update
        )

    # ========================================================
    # 단계
    # ========================================================

    for stage, themes in FUTURE_CHAIN.items():

        st.markdown(
            f"## {stage}"
        )

        for theme, codes in themes.items():

            st.markdown(
                f"### {theme}"
            )

            cols = st.columns(
                min(
                    3,
                    len(codes),
                )
            )

            for idx, code in enumerate(codes):

                code = normalize_code(
                    code
                )

                name = get_etf_name(
                    code
                )

                with cols[
                    idx % len(cols)
                ]:

                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            f"**{name}**"
                        )

                        st.caption(
                            code
                        )

                        raw = fetch_yahoo(
                            code
                        )

                        if (
                            raw is not None
                            and not raw.empty
                        ):

                            price = safe_num(
                                raw.iloc[-1]["Close"]
                            )

                            if not np.isnan(price):

                                st.metric(
                                    "\uD604\uC7AC\uAC00",
                                    f"{price:,.0f}\uC6D0",
                                )

                            if len(raw) >= 2:

                                previous = safe_num(
                                    raw.iloc[-2]["Close"]
                                )

                                if (
                                    not np.isnan(price)
                                    and not np.isnan(previous)
                                    and previous != 0
                                ):

                                    change = (
                                        price
                                        /
                                        previous
                                        - 1
                                    ) * 100

                                    st.caption(
                                        f"\uC804\uC77C \uB300\uBE44 {change:+.2f}%"
                                    )

                        # ------------------------------------
                        # 토글
                        # ------------------------------------

                        active = (
                            st.session_state.future_detail_code
                            == code
                        )

                        if active:

                            button_label = (
                                "🔽 ETF 분석 닫기"
                            )

                        else:

                            button_label = (
                                "📊 ETF 분석"
                            )

                        if st.button(
                            button_label,
                            use_container_width=True,
                            key=(
                                "future_analysis_"
                                + stage
                                + "_"
                                + theme
                                + "_"
                                + code
                            ),
                        ):

                            if active:

                                st.session_state.future_detail_code = None

                            else:

                                st.session_state.future_detail_code = code

                            st.rerun()

                        # ------------------------------------
                        # 바로 아래 분석
                        # ------------------------------------

                        if (
                            st.session_state.future_detail_code
                            == code
                        ):

                            st.divider()

                            render_analysis(
                                code
                            )

                            if st.button(
                                "📊 내 ETF 화면에서 보기",
                                use_container_width=True,
                                key=(
                                    "future_go_my_"
                                    + code
                                ),
                            ):

                                st.session_state.selected_code = code
                                st.session_state.nav = (
                                    "📊 내 ETF"
                                )
                                st.session_state.future_detail_code = None

                                st.rerun()


# ============================================================
# HEADER
# ============================================================

st.title(
    "📊 ETF RADAR"
)

st.caption(
    "\uAD6D\uB0B4 ETF \uAE30\uC220\uC801 \uD750\uB984 \u00B7 \uAC00\uACA9\uAD6C\uAC04 \u00B7 \uB300\uC751 \uC2DC\uB098\uB9AC\uC624"
)


# ============================================================
# MENU
# ============================================================

nav = st.radio(
    "\uBA54\uB274",
    [
        "📊 내 ETF",
        "🔮 미래테마",
    ],
    horizontal=True,
    key="nav",
    label_visibility="collapsed",
)


st.divider()


# ============================================================
# 화면
# ============================================================

if nav == "📊 내 ETF":

    render_my_etf()

else:

    render_future_theme()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ETF RADAR · Technical Analysis Dashboard"
)