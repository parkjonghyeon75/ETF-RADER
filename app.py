# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
# ETF 기본 목록
# 한글은 Unicode escape로 저장
# ============================================================

BASE_ETFS = {
    "395160": "KODEX AI\uBC18\uB3C4\uCCB4\uD575\uC2EC\uC7A5\uBE44",
    "487240": "KODEX AI\uBC18\uB3C4\uCCB4",
    "471990": "KODEX AI\uBC18\uB3C4\uCCB4TOP2Plus",

    "133690": "TIGER \uBBF8\uAD6D\uB098\uC2A4\uB2E4100",
    "360750": "TIGER \uBBF8\uAD6DS&P500",
    "458730": "TIGER \uAE00\uB85C\uBC8CAI&\uB85C\uBD07",
    "381170": "TIGER \uBBF8\uAD6D\uD14C\uD06CTOP10 INDXX",
    "396500": "TIGER \uBC18\uB3C4\uCCB4",

    "091160": "KODEX \uBC18\uB3C4\uCCB4",
    "091180": "KODEX \uC790\uB3D9\uCC28",
    "139260": "TIGER 200 IT",

    "305720": "KODEX 2\uCC28\uC804\uC9C0\uC0B0\uC5C5",
    "364690": "KODEX \uD601\uC2E0\uAE30\uC220\uD14C\uB9C8\uC561\uD2F0\uBE0C",

    "117700": "KODEX \uAC74\uC124",
    "140700": "KODEX \uBCF4\uD5D8",
    "144600": "KODEX \uC740\uD589",
    "102780": "KODEX \uC0BC\uC131\uADF8\uB8F9",

    "261220": "KODEX WTI\uC6D0\uC720\uC120\uBB3C(H)",

    "449170": "TIGER \uAE00\uB85C\uBC8CAI\uC778\uD504\uB77C\uC561\uD2F0\uBE0C",
    "434060": "TIGER \uAE00\uB85C\uBC8CAI&\uBC18\uB3C4\uCCB4\uC561\uD2F0\uBE0C",

    "464240": "KODEX AI\uC804\uB825\uD575\uC2EC\uC124\uBE44",
    "487130": "KODEX AI\uC804\uB825\uC778\uD504\uB77C",

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
# Session State
# ============================================================

if "watchlist" not in st.session_state:
    st.session_state.watchlist = DEFAULT_WATCHLIST.copy()

if "selected_code" not in st.session_state:
    st.session_state.selected_code = None

if "search_keyword" not in st.session_state:
    st.session_state.search_keyword = ""

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "theme_updated" not in st.session_state:
    st.session_state.theme_updated = None


# ============================================================
# 기본 함수
# ============================================================

def normalize_code(code):

    if code is None:
        return ""

    code = str(code).strip()

    if code.isdigit():
        return code.zfill(6)

    return code


# ============================================================
# 화면 표시용 ETF명
#
# ★ 중요
# 캐시의 ETF명을 사용하지 않음
# ============================================================

def get_display_name(code):

    code = normalize_code(code)

    if code in BASE_ETFS:
        return BASE_ETFS[code]

    return code


# ============================================================
# 깨진 문자열 감지
# ============================================================

def is_broken_text(text):

    if not text:
        return True

    text = str(text)

    broken_patterns = [
        "\ufffd",
        "Ã",
        "Â",
        "ì",
        "ë",
        "í",
        "î",
        "ï",
        "ð",
        "ñ",
        "ò",
        "ó",
        "ô",
        "õ",
        "ö",
        "÷",
        "ø",
        "ù",
        "ú",
        "û",
        "ü",
        "ý",
        "þ",
    ]

    return any(x in text for x in broken_patterns)


# ============================================================
# ETF 검색
#
# ★ 기존 검색이 안 되는 문제 방지
# ★ 코드 / ETF명 모두 검색
# ★ 한글명은 BASE_ETFS를 기준으로 검색
# ============================================================

def search_etfs(keyword):

    keyword = str(keyword or "").strip().lower()

    results = []

    # --------------------------------------------------------
    # 기본 ETF
    # --------------------------------------------------------

    for code, name in BASE_ETFS.items():

        code_text = str(code).lower()
        name_text = str(name).lower()

        if (
            keyword == ""
            or keyword in code_text
            or keyword in name_text
        ):

            results.append({
                "code": code,
                "name": name,
            })


    # --------------------------------------------------------
    # 캐시
    # --------------------------------------------------------

    cache_file = "etf_universe_cache.json"

    if os.path.exists(cache_file):

        try:

            with open(
                cache_file,
                "r",
                encoding="utf-8"
            ) as f:

                cache = json.load(f)

            if isinstance(cache, dict):

                for code, item in cache.items():

                    code = normalize_code(code)

                    # 기본 ETF는 이미 처리
                    if code in BASE_ETFS:
                        continue

                    if isinstance(item, dict):
                        name = item.get("name", "")
                    else:
                        name = str(item)

                    if not name:
                        continue

                    if is_broken_text(name):
                        continue

                    code_text = code.lower()
                    name_text = str(name).lower()

                    if (
                        keyword == ""
                        or keyword in code_text
                        or keyword in name_text
                    ):

                        results.append({
                            "code": code,
                            "name": str(name),
                        })

        except Exception:
            pass


    # --------------------------------------------------------
    # 중복 제거
    # --------------------------------------------------------

    unique = {}

    for item in results:

        code = normalize_code(
            item["code"]
        )

        if code not in unique:

            unique[code] = item


    return list(unique.values())


# ============================================================
# Yahoo Finance
# ============================================================

def yahoo_symbol(code):

    return f"{normalize_code(code)}.KS"


@st.cache_data(
    ttl=300,
    show_spinner=False
)
def fetch_yahoo(code, period="1y"):

    code = normalize_code(code)

    try:

        df = yf.download(
            yahoo_symbol(code),
            period=period,
            auto_adjust=False,
            progress=False,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        if isinstance(
            df.columns,
            pd.MultiIndex
        ):

            df.columns = (
                df.columns
                .get_level_values(0)
            )


        needed = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]


        for col in needed:

            if col not in df.columns:
                df[col] = np.nan


        df = df[needed].copy()

        df = df.dropna(
            subset=["Close"]
        )

        return df


    except Exception:

        return pd.DataFrame()


# ============================================================
# 보조지표
# ============================================================

def calculate_indicators(df):

    df = df.copy()

    if df.empty:
        return df


    df["MA20"] = (
        df["Close"]
        .rolling(20)
        .mean()
    )

    df["MA60"] = (
        df["Close"]
        .rolling(60)
        .mean()
    )


    delta = df["Close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)


    avg_gain = (
        gain
        .rolling(14)
        .mean()
    )

    avg_loss = (
        loss
        .rolling(14)
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


    df["RSI"] = (
        100
        -
        (
            100
            /
            (1 + rs)
        )
    )


    df["Volume20"] = (
        df["Volume"]
        .rolling(20)
        .mean()
    )


    df["VolumeRatio"] = (
        df["Volume"]
        /
        df["Volume20"]
    )


    return df


# ============================================================
# 지지 / 저항
# ============================================================

def calculate_levels(df):

    df = calculate_indicators(df)

    if df.empty:
        return {}


    close = float(
        df["Close"].iloc[-1]
    )


    ma20 = (
        float(df["MA20"].iloc[-1])
        if pd.notna(df["MA20"].iloc[-1])
        else close
    )


    ma60 = (
        float(df["MA60"].iloc[-1])
        if pd.notna(df["MA60"].iloc[-1])
        else ma20
    )


    support1 = float(
        df["Low"]
        .tail(20)
        .min()
    )


    support2 = float(
        df["Low"]
        .tail(60)
        .min()
    )


    recent20_high = float(
        df["High"]
        .tail(20)
        .max()
    )


    recent60_high = float(
        df["High"]
        .tail(60)
        .max()
    )


    breakout = max(
        recent20_high,
        recent60_high
    )


    risk = min(
        support1,
        support2
    )


    return {
        "current": close,
        "ma20": ma20,
        "ma60": ma60,
        "support1": support1,
        "support2": support2,
        "breakout": breakout,
        "risk": risk,
    }


# ============================================================
# 판단
# ============================================================

def get_judgment(df):

    df = calculate_indicators(df)

    if df.empty:

        return {
            "title": "데이터 부족",
            "action": "추가 데이터 확인",
            "reason": "차트 데이터를 충분히 확보하지 못했습니다.",
        }


    last = df.iloc[-1]


    close = float(
        last["Close"]
    )


    ma20 = (
        float(last["MA20"])
        if pd.notna(last["MA20"])
        else close
    )


    ma60 = (
        float(last["MA60"])
        if pd.notna(last["MA60"])
        else ma20
    )


    rsi = (
        float(last["RSI"])
        if pd.notna(last["RSI"])
        else 50
    )


    volume_ratio = (
        float(last["VolumeRatio"])
        if pd.notna(last["VolumeRatio"])
        else 1
    )


    if close > ma20 > ma60:

        trend = "\uC0C1\uC2B9 \uCD94\uC138"

    elif close < ma20 < ma60:

        trend = "\uD558\uB77D \uCD94\uC138"

    else:

        trend = "\uD63C\uC870 / \uBC29\uD5A5 \uD655\uC778"


    if rsi >= 70:

        rsi_state = "\uB2E8\uAE30 \uACFC\uC5F4"

    elif rsi <= 30:

        rsi_state = "\uB2E8\uAE30 \uCE68\uCCB4"

    else:

        rsi_state = "\uC911\uB9BD"


    if volume_ratio >= 1.5:

        volume_state = "\uAC70\uB798\uB7C9 \uAC15\uD568"

    elif volume_ratio <= 0.7:

        volume_state = "\uAC70\uB798\uB7C9 \uC57D\uD568"

    else:

        volume_state = "\uD3C9\uADE0 \uC218\uC900"


    if close > ma20 > ma60:

        action = (
            "\uBCF4\uC720 \uC6B0\uC120 "
            "\u00B7 \uB204\uB9BC\uBAA9 \uBD84\uD560 \uC811\uADFC"
        )

    elif close < ma20 < ma60:

        action = (
            "\uC2E0\uADDC \uCD94\uACA9\uBCF4\uB2E4 "
            "\uCD94\uC138 \uD68C\uBCF5 \uD655\uC778"
        )

    else:

        action = (
            "\uBC29\uD5A5 \uD655\uC778 \uD6C4 "
            "\uBD84\uD560 \uB300\uC751"
        )


    reason = (
        f"{trend} / {rsi_state} / {volume_state}. "
        f"\uD604\uC7AC\uAC00\uC640 20\uC77C\uC120\u00B760\uC77C\uC120 "
        f"\uAD00\uACC4\uB97C \uC6B0\uC120 \uD655\uC778\uD558\uACE0 "
        f"\uAC70\uB798\uB7C9 \uB3D9\uBC18 \uC5EC\uBD80\uB97C "
        f"\uD655\uC778\uD558\uB294 \uAD6C\uAC04\uC785\uB2C8\uB2E4."
    )


    return {
        "title": trend,
        "action": action,
        "reason": reason,
        "rsi": rsi,
        "volume_ratio": volume_ratio,
    }


# ============================================================
# 가격별 대응안
# ============================================================

def render_price_response(df):

    levels = calculate_levels(df)

    if not levels:
        return


    table = pd.DataFrame(
        [
            [
                "\uD604\uC7AC\uAC00",
                levels["current"],
                "\uCD94\uACA9\uBCF4\uB2E4 \uD604\uC7AC \uCD94\uC138\uC640 \uAC70\uB798\uB7C9 \uD655\uC778",
            ],

            [
                "1\uCC28 \uAD00\uC2EC",
                levels["ma20"],
                "20\uC77C\uC120 \uC9C0\uC9C0 \uD655\uC778 \uC2DC 1\uCC28 \uBD84\uD560",
            ],

            [
                "\uC8FC\uC694 \uC9C0\uC9C0",
                levels["support1"],
                "\uC9C0\uC9C0 \uD655\uC778 \uC2DC 2\uCC28 \uBD84\uD560 \uB300\uC751 \uAC80\uD1A0",
            ],

            [
                "2\uCC28 \uC9C0\uC9C0",
                levels["support2"],
                "\uAC15\uD55C \uC870\uC815 \uAD6C\uAC04. \uCD94\uC138 \uD6FC\uC190 \uC5EC\uBD80 \uD655\uC778",
            ],

            [
                "\uB3CC\uD30C \uAE30\uC900",
                levels["breakout"],
                "\uAC70\uB798\uB7C9 \uB3D9\uBC18 \uB3CC\uD30C \uC2DC \uC0C1\uC2B9 \uC7AC\uAC00\uC18D \uD655\uC778",
            ],

            [
                "\uC704\uD5D8 \uAE30\uC900",
                levels["risk"],
                "\uC774\uD0C8 \uC2DC \uC2E0\uADDC\uB9E4\uC218\uBCF4\uB2E4 \uCD94\uC138 \uD68C\uBCF5 \uD655\uC778",
            ],
        ],
        columns=[
            "\uAD6C\uAC04",
            "\uAC00\uACA9",
            "\uB300\uC751",
        ],
    )


    table["\uAC00\uACA9"] = table[
        "\uAC00\uACA9"
    ].map(
        lambda x: f"{x:,.0f}"
    )


    st.markdown(
        "#### \uAC00\uACA9\uBCC4 \uB300\uC751\uC548"
    )


    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# 판단근거
# ============================================================

def render_judgment(df):

    result = get_judgment(df)

    st.markdown(
        "#### \uD310\uB2E8\uADFC\uAC70"
    )

    st.info(
        f"**\uD604\uC7AC \uD310\uB2E8:** {result['action']}\n\n"
        f"{result['reason']}"
    )


# ============================================================
# 시나리오
# ============================================================

def render_scenarios(df):

    levels = calculate_levels(df)

    if not levels:
        return


    st.markdown(
        "#### \uB300\uC751 \uC2DC\uB098\uB9AC\uC624"
    )


    c1, c2, c3 = st.columns(3)


    with c1:

        st.markdown(
            "**\uC0C1\uC2B9 \uC2DC\uB098\uB9AC\uC624**"
        )

        st.write(
            f"\uB3CC\uD30C \uAE30\uC900 "
            f"{levels['breakout']:,.0f}\uC6D0 "
            "\uC0C1\uD5A5 \uB3CC\uD30C + \uAC70\uB798\uB7C9 \uC99D\uAC00 \uC2DC "
            "\uC0C1\uC2B9 \uC7AC\uAC00\uC18D \uC5EC\uBD80\uB97C \uD655\uC778\uD569\uB2C8\uB2E4."
        )


    with c2:

        st.markdown(
            "**\uB204\uB9BC \uC2DC\uB098\uB9AC\uC624**"
        )

        st.write(
            f"20\uC77C\uC120 "
            f"{levels['ma20']:,.0f}\uC6D0 "
            f"\uBC0F 1\uCC28 \uC9C0\uC9C0 "
            f"{levels['support1']:,.0f}\uC6D0 "
            "\uBD80\uADFC\uC758 \uC9C0\uC9C0 \uC5EC\uBD80\uB97C \uD655\uC778\uD569\uB2C8\uB2E4."
        )


    with c3:

        st.markdown(
            "**\uD558\uB77D \uC2DC\uB098\uB9AC\uC624**"
        )

        st.write(
            f"\uC8FC\uC694 \uC9C0\uC9C0 \uC774\uD0C8 \uC2DC "
            f"\uC2E0\uADDC\uB9E4\uC218\uBCF4\uB2E4 \uCD94\uC138 \uD68C\uBCF5\uC744 \uC6B0\uC120 \uD655\uC778\uD569\uB2C8\uB2E4. "
            f"\uC704\uD5D8 \uAE30\uC900 {levels['risk']:,.0f}\uC6D0"
        )


# ============================================================
# 차트
#
# ★ 중요
# 확대 / 이동 / 스크롤 확대를 모두 차단
# ============================================================

def render_chart(df, name):

    if df.empty:

        st.warning(
            "\uCC28\uD2B8 \uB370\uC774\uD130\uAC00 \uC5C6\uC2B5\uB2C8\uB2E4."
        )

        return


    df = calculate_indicators(df)


    fig = make_subplots(

        rows=2,
        cols=1,

        shared_xaxes=True,

        vertical_spacing=0.05,

        row_heights=[
            0.72,
            0.28,
        ],
    )


    # --------------------------------------------------------
    # 가격
    # --------------------------------------------------------

    fig.add_trace(

        go.Candlestick(

            x=df.index,

            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],

            name="\uAC00\uACA9",

        ),

        row=1,
        col=1,
    )


    # --------------------------------------------------------
    # MA20
    # --------------------------------------------------------

    fig.add_trace(

        go.Scatter(

            x=df.index,

            y=df["MA20"],

            mode="lines",

            name="MA20",

        ),

        row=1,
        col=1,
    )


    # --------------------------------------------------------
    # MA60
    # --------------------------------------------------------

    fig.add_trace(

        go.Scatter(

            x=df.index,

            y=df["MA60"],

            mode="lines",

            name="MA60",

        ),

        row=1,
        col=1,
    )


    # --------------------------------------------------------
    # 거래량
    # --------------------------------------------------------

    fig.add_trace(

        go.Bar(

            x=df.index,

            y=df["Volume"],

            name="\uAC70\uB798\uB7C9",

        ),

        row=2,
        col=1,
    )


    # --------------------------------------------------------
    # ★ 차트 고정
    # --------------------------------------------------------

    fig.update_layout(

        title=name,

        height=620,

        margin=dict(
            l=10,
            r=10,
            t=45,
            b=10,
        ),

        xaxis_rangeslider_visible=False,

        dragmode=False,

        hovermode="x unified",

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
        ),
    )


    # --------------------------------------------------------
    # ★ X축 줌 / 팬 차단
    # --------------------------------------------------------

    fig.update_xaxes(
        fixedrange=True,
        rangeslider_visible=False,
    )


    # --------------------------------------------------------
    # ★ Y축 이동 / 확대 차단
    # --------------------------------------------------------

    fig.update_yaxes(
        fixedrange=True,
    )


    st.plotly_chart(

        fig,

        use_container_width=True,

        config={
            "scrollZoom": False,
            "doubleClick": False,
            "displayModeBar": False,
            "staticPlot": False,
        },

    )


# ============================================================
# ETF 분석
# ============================================================

def render_analysis(code):

    code = normalize_code(code)

    # ★ 화면 표시명은 무조건 안전한 함수 사용
    name = get_display_name(code)


    st.divider()


    st.subheader(
        f"📊 {name}"
    )


    st.caption(
        f"\uC885\uBAA9\uCF54\uB4DC {code}"
    )


    with st.spinner(
        "\uB370\uC774\uD130\uB97C \uBD84\uC11D\uD558\uACE0 \uC788\uC2B5\uB2C8\uB2E4..."
    ):

        df = fetch_yahoo(
            code,
            "1y"
        )


    if df.empty:

        st.error(
            "\uD574\uB2F9 ETF\uC758 \uAC00\uACA9 \uB370\uC774\uD130\uB97C \uAC00\uC838\uC624\uC9C0 \uBABB\uD588\uC2B5\uB2C8\uB2E4."
        )

        return


    df = calculate_indicators(df)


    current = float(
        df["Close"].iloc[-1]
    )


    previous = (
        float(df["Close"].iloc[-2])
        if len(df) >= 2
        else current
    )


    change = current - previous


    change_pct = (
        change / previous * 100
        if previous != 0
        else 0
    )


    c1, c2, c3 = st.columns(3)


    with c1:

        st.metric(
            "\uD604\uC7AC\uAC00",
            f"{current:,.0f}\uC6D0",
            f"{change:+,.0f}\uC6D0",
        )


    with c2:

        st.metric(
            "\uB4F1\uB77D\uB960",
            f"{change_pct:+.2f}%",
        )


    with c3:

        rsi = df["RSI"].iloc[-1]

        if pd.isna(rsi):
            rsi_text = "-"
        else:
            rsi_text = f"{float(rsi):.1f}"

        st.metric(
            "RSI",
            rsi_text,
        )


    render_judgment(df)

    render_price_response(df)

    render_scenarios(df)


    st.markdown(
        "#### \uCC28\uD2B8"
    )


    render_chart(
        df,
        name,
    )


# ============================================================
# 분석 버튼
# ============================================================

def analysis_button(code, key_prefix):

    code = normalize_code(code)

    active = (
        st.session_state.selected_code
        == code
    )


    if active:

        label = (
            "🔽 ETF \uBD84\uC11D \uB2EB\uAE30"
        )

    else:

        label = (
            "📊 ETF \uBD84\uC11D"
        )


    return st.button(

        label,

        use_container_width=True,

        key=f"{key_prefix}_{code}",

    )


# ============================================================
# 내 ETF
# ============================================================

def render_my_etf():

    st.title("📊 \uB0B4 ETF")

    st.caption(
        "ETF \uCC3E\uAE30\uC640 \uAD00\uC2EC ETF\uB97C \uD55C \uD654\uBA74\uC5D0\uC11C \uAD00\uB9AC\uD569\uB2C8\uB2E4."
    )


    # ========================================================
    # ETF 찾기
    # ========================================================

    st.markdown(
        "### 🔎 ETF \uCC3E\uAE30"
    )


    search_col1, search_col2 = st.columns(
        [4, 1]
    )


    with search_col1:

        keyword = st.text_input(

            "ETF \uAC80\uC0C9",

            value=st.session_state.search_keyword,

            placeholder="\uC885\uBAA9\uCF54\uB4DC \uB610\uB294 ETF\uBA85\uC744 \uC785\uB825\uD558\uC138\uC694",

            label_visibility="collapsed",

            key="etf_search_input",

        )


    with search_col2:

        search_clicked = st.button(

            "\uAC80\uC0C9",

            use_container_width=True,

            key="etf_search_button",

        )


    # --------------------------------------------------------
    # 검색 버튼을 누른 경우
    # --------------------------------------------------------

    if search_clicked:

        st.session_state.search_keyword = (
            keyword.strip()
        )

        st.session_state.search_results = (
            search_etfs(
                st.session_state.search_keyword
            )
        )

        st.session_state.selected_code = None

        st.rerun()


    # --------------------------------------------------------
    # 최초 진입 시 전체 목록
    # --------------------------------------------------------

    if not st.session_state.search_results:

        st.session_state.search_results = (
            search_etfs("")
        )


    results = (
        st.session_state.search_results
    )


    if results:

        # ★ 드롭다운에는 코드만
        codes = [
            normalize_code(
                item["code"]
            )
            for item in results
        ]


        # 중복 제거
        codes = list(
            dict.fromkeys(codes)
        )


        selected_search = st.selectbox(

            "\uAC80\uC0C9\uACB0\uACFC",

            codes,

            key="search_code",

            format_func=lambda x: str(x),

        )


        selected_search = normalize_code(
            selected_search
        )


        # ----------------------------------------------------
        # ★ 한글 표시
        # 캐시가 아닌 BASE_ETFS에서 직접 가져옴
        # ----------------------------------------------------

        selected_name = get_display_name(
            selected_search
        )


        with st.container(
            border=True
        ):

            st.markdown(
                f"### {selected_name}"
            )

            st.caption(
                f"\uC885\uBAA9\uCF54\uB4DC {selected_search}"
            )


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


            if (
                st.session_state.selected_code
                == selected_search
            ):

                render_analysis(
                    selected_search
                )


            if (
                selected_search
                not in st.session_state.watchlist
            ):

                if st.button(

                    "⭐ \uAD00\uC2EC ETF \uCD94\uAC00",

                    use_container_width=True,

                    key=f"add_{selected_search}",

                ):

                    st.session_state.watchlist.append(
                        selected_search
                    )

                    st.rerun()

            else:

                st.caption(
                    "⭐ \uD604\uC7AC \uAD00\uC2EC ETF\uC5D0 \uB4F1\uB85D\uB418\uC5B4 \uC788\uC2B5\uB2C8\uB2E4."
                )


    else:

        st.info(
            "\uAC80\uC0C9 \uACB0\uACFC\uAC00 \uC5C6\uC2B5\uB2C8\uB2E4."
        )


    # ========================================================
    # 관심 ETF
    # ========================================================

    st.divider()


    st.markdown(
        "### ⭐ \uAD00\uC2EC ETF"
    )


    if not st.session_state.watchlist:

        st.info(
            "\uAD00\uC2EC ETF\uAC00 \uC5C6\uC2B5\uB2C8\uB2E4."
        )

        return


    watch_codes = [
        normalize_code(x)
        for x in st.session_state.watchlist
    ]


    watch_code = st.selectbox(

        "\uAD00\uC2EC ETF \uC120\uD0DD",

        watch_codes,

        key="watch_code",

        format_func=lambda x: str(x),

    )


    watch_code = normalize_code(
        watch_code
    )


    watch_name = get_display_name(
        watch_code
    )


    with st.container(
        border=True
    ):

        st.markdown(
            f"### {watch_name}"
        )

        st.caption(
            f"\uC885\uBAA9\uCF54\uB4DC {watch_code}"
        )


        c1, c2 = st.columns(2)


        with c1:

            if analysis_button(
                watch_code,
                "watch_analysis",
            ):

                if (
                    st.session_state.selected_code
                    == watch_code
                ):

                    st.session_state.selected_code = None

                else:

                    st.session_state.selected_code = (
                        watch_code
                    )

                st.rerun()


        with c2:

            if st.button(

                "🗑 \uAD00\uC2EC ETF \uC0AD\uC81C",

                use_container_width=True,

                key=f"remove_{watch_code}",

            ):

                if watch_code in (
                    st.session_state.watchlist
                ):

                    st.session_state.watchlist.remove(
                        watch_code
                    )

                st.session_state.selected_code = None

                st.rerun()


        if (
            st.session_state.selected_code
            == watch_code
        ):

            render_analysis(
                watch_code
            )


# ============================================================
# 미래테마
# ============================================================

def render_future_theme():

    st.title("🔮 \uBBF8\uB798\uD14C\uB9C8")

    st.caption(
        "\uD604\uC7AC \uC8FC\uB3C4 \uD14C\uB9C8\uC5D0\uC11C \uB2E4\uC74C \uC218\uD61C \uD14C\uB9C8\uB85C \uC774\uC5B4\uC9C0\uB294 \uD750\uB984\uC744 \uD655\uC778\uD569\uB2C8\uB2E4."
    )


    if st.button(

        "🔄 \uD14C\uB9C8 \uC5C5\uB370\uC774\uD2B8",

        use_container_width=True,

        key="theme_update_button",

    ):

        st.session_state.theme_updated = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        )

        st.rerun()


    if st.session_state.theme_updated:

        st.caption(
            f"\uB9C8\uC9C0\uB9C9 \uC5C5\uB370\uC774\uD2B8: "
            f"{st.session_state.theme_updated}"
        )


    for stage, themes in FUTURE_CHAIN.items():

        st.markdown(
            f"### {stage}"
        )


        for theme_name, codes in themes.items():

            with st.container(
                border=True
            ):

                st.markdown(
                    f"#### {theme_name}"
                )


                for code in codes:

                    code = normalize_code(
                        code
                    )

                    name = get_display_name(
                        code
                    )

                    st.write(
                        f"• {name} ({code})"
                    )


# ============================================================
# Main
# ============================================================

def main():

    st.title(
        "📊 ETF RADAR"
    )

    st.caption(
        "ETF \uCC28\uD2B8 \u00B7 \uCD94\uC138 \u00B7 \uAC70\uB798\uB7C9 \u00B7 \uC9C0\uC9C0/\uC800\uD56D \u00B7 \uB300\uC751 \uC2DC\uB098\uB9AC\uC624"
    )


    tab1, tab2 = st.tabs(
        [
            "📊 \uB0B4 ETF",
            "🔮 \uBBF8\uB798\uD14C\uB9C8",
        ]
    )


    with tab1:

        render_my_etf()


    with tab2:

        render_future_theme()


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":

    main()