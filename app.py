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
# Korean Encoding Safe Version
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# ETF 기본 목록
#
# 중요:
# 한글명은 Unicode escape로 저장하여
# Streamlit / GitHub / Android 환경의 인코딩 문제를 방지
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

if "theme_updated" not in st.session_state:
    st.session_state.theme_updated = None

if "search_keyword" not in st.session_state:
    st.session_state.search_keyword = ""


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
# ★ 핵심
# ETF 화면 표시명은 캐시를 사용하지 않는다.
#
# 캐시에 깨진 한글이 들어 있어도
# 화면에는 절대 사용하지 않음.
# ============================================================

def get_display_name(code):

    code = normalize_code(code)

    if code in BASE_ETFS:
        return BASE_ETFS[code]

    return code


# ============================================================
# 캐시에서 깨진 한글이 들어오는 것을 방지
# ============================================================

def is_broken_text(text):

    if not text:
        return True

    text = str(text)

    broken = [
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

    return any(x in text for x in broken)


# ============================================================
# ETF 검색
# ============================================================

def search_etfs(keyword):

    keyword = str(keyword or "").strip().lower()

    rows = []

    # 기본 ETF
    for code, name in BASE_ETFS.items():

        if not keyword:
            rows.append({
                "code": code,
                "name": name,
            })

        else:

            if (
                keyword in code.lower()
                or keyword in name.lower()
            ):

                rows.append({
                    "code": code,
                    "name": name,
                })


    # 캐시
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

                    if code in BASE_ETFS:
                        continue

                    if isinstance(item, dict):
                        name = item.get("name", "")
                    else:
                        name = str(item)

                    # 깨진 캐시 이름은 제외
                    if is_broken_text(name):
                        continue

                    if not name:
                        continue

                    if (
                        not keyword
                        or keyword in code.lower()
                        or keyword in name.lower()
                    ):

                        rows.append({
                            "code": code,
                            "name": name,
                        })

        except Exception:
            pass


    # 중복 제거
    unique = {}

    for row in rows:

        code = normalize_code(row["code"])

        if code not in unique:

            unique[code] = {
                "code": code,
                "name": row["name"],
            }


    return list(unique.values())


# ============================================================
# Yahoo Finance
# ============================================================

def yahoo_symbol(code):

    return f"{normalize_code(code)}.KS"


@st.cache_data(ttl=300, show_spinner=False)
def fetch_yahoo(code, period="1y"):

    code = normalize_code(code)

    symbol = yahoo_symbol(code)

    try:

        df = yf.download(
            symbol,
            period=period,
            auto_adjust=False,
            progress=False,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.rename(
            columns={
                "Open": "Open",
                "High": "High",
                "Low": "Low",
                "Close": "Close",
                "Volume": "Volume",
            }
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

        df = df.dropna(subset=["Close"])

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

    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA60"] = df["Close"].rolling(60).mean()

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    df["RSI"] = 100 - (
        100 / (1 + rs)
    )

    df["Volume20"] = (
        df["Volume"]
        .rolling(20)
        .mean()
    )

    df["VolumeRatio"] = (
        df["Volume"]
        / df["Volume20"]
    )

    return df


# ============================================================
# 지지 / 저항
# ============================================================

def calculate_levels(df):

    df = calculate_indicators(df)

    if df.empty:
        return {}

    close = float(df["Close"].iloc[-1])

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

    recent20 = df["Low"].tail(20)

    recent60 = df["Low"].tail(60)

    support1 = float(
        recent20.min()
    )

    support2 = float(
        recent60.min()
    )

    recent20_high = float(
        df["High"].tail(20).max()
    )

    recent60_high = float(
        df["High"].tail(60).max()
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

    close = float(last["Close"])

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


    # 추세
    if close > ma20 > ma60:

        trend = "상승 추세"

    elif close < ma20 < ma60:

        trend = "하락 추세"

    else:

        trend = "혼조 / 방향 확인"


    # RSI
    if rsi >= 70:

        rsi_state = "단기 과열"

    elif rsi <= 30:

        rsi_state = "단기 침체"

    else:

        rsi_state = "중립"


    # 거래량
    if volume_ratio >= 1.5:

        volume_state = "거래량 강함"

    elif volume_ratio <= 0.7:

        volume_state = "거래량 약함"

    else:

        volume_state = "평균 수준"


    if trend == "상승 추세":

        action = "보유 우선 · 눌림목 분할 접근"

    elif trend == "하락 추세":

        action = "신규 추격보다 추세 회복 확인"

    else:

        action = "방향 확인 후 분할 대응"


    reason = (
        f"{trend} / {rsi_state} / {volume_state}. "
        f"현재가와 20일선·60일선 관계를 우선 확인하고 "
        f"거래량이 동반되는지 확인하는 구간입니다."
    )


    return {
        "title": trend,
        "action": action,
        "reason": reason,
        "rsi": rsi,
        "volume_ratio": volume_ratio,
    }


# ============================================================
# 가격별 대응
# ============================================================

def render_price_response(df):

    levels = calculate_levels(df)

    if not levels:
        st.warning("가격 데이터를 확인할 수 없습니다.")
        return

    current = levels["current"]
    ma20 = levels["ma20"]
    support1 = levels["support1"]
    support2 = levels["support2"]
    breakout = levels["breakout"]
    risk = levels["risk"]


    table = pd.DataFrame(

        [
            [
                "현재가",
                current,
                "추격매수보다 현재 추세와 거래량 확인",
            ],

            [
                "1차 관심",
                ma20,
                "20일선 지지 확인 시 1차 분할 접근",
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


    table["가격"] = table["가격"].map(
        lambda x: f"{x:,.0f}"
    )


    st.markdown("#### 가격별 대응안")

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# 판단 근거
# ============================================================

def render_judgment(df):

    result = get_judgment(df)

    st.markdown("#### 판단근거")

    st.info(
        f"**현재 판단:** {result['action']}\n\n"
        f"{result['reason']}"
    )


# ============================================================
# 시나리오
# ============================================================

def render_scenarios(df):

    levels = calculate_levels(df)

    if not levels:
        return

    st.markdown("#### 대응 시나리오")

    c1, c2, c3 = st.columns(3)


    with c1:

        st.markdown("**상승 시나리오**")

        st.write(
            f"돌파 기준 {levels['breakout']:,.0f}원 "
            "상향 돌파 + 거래량 증가 시 "
            "상승 재가속 여부를 확인합니다."
        )


    with c2:

        st.markdown("**눌림 시나리오**")

        st.write(
            f"20일선 {levels['ma20']:,.0f}원 "
            "및 1차 지지 {levels['support1']:,.0f}원 "
            "부근의 지지 여부를 확인합니다."
        )


    with c3:

        st.markdown("**하락 시나리오**")

        st.write(
            f"주요 지지 이탈 시 신규매수보다 "
            f"추세 회복을 우선 확인합니다. "
            f"위험 기준 {levels['risk']:,.0f}원"
        )


# ============================================================
# 차트
# ============================================================

def render_chart(df, name):

    if df.empty:
        st.warning("차트 데이터가 없습니다.")
        return

    df = calculate_indicators(df)

    fig = make_subplots(

        rows=2,
        cols=1,

        shared_xaxes=True,

        vertical_spacing=0.08,

        row_heights=[
            0.72,
            0.28,
        ],

    )


    # 캔들
    fig.add_trace(

        go.Candlestick(

            x=df.index,

            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],

            name="가격",

        ),

        row=1,
        col=1,
    )


    # MA20
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


    # MA60
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


    # 거래량
    fig.add_trace(

        go.Bar(

            x=df.index,

            y=df["Volume"],

            name="거래량",

        ),

        row=2,
        col=1,
    )


    fig.update_layout(

        title=name,

        height=620,

        xaxis_rangeslider_visible=False,

        margin=dict(
            l=10,
            r=10,
            t=45,
            b=10,
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
        ),
    )


    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# ETF 분석
# ============================================================

def render_analysis(code):

    code = normalize_code(code)

    # ★ 화면 표시명은 반드시 이 함수 사용
    name = get_display_name(code)

    st.markdown("---")

    st.subheader(
        f"📊 {name}"
    )

    st.caption(
        f"종목코드 {code}"
    )


    with st.spinner("ETF 데이터를 분석하고 있습니다..."):

        df = fetch_yahoo(code, "1y")


    if df.empty:

        st.error(
            "해당 ETF의 가격 데이터를 가져오지 못했습니다."
        )

        return


    df = calculate_indicators(df)


    # 현재가
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
            "현재가",
            f"{current:,.0f}원",
            f"{change:+,.0f}원",
        )


    with c2:

        st.metric(
            "등락률",
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

    st.markdown("#### 차트")

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

        label = "🔽 ETF 분석 닫기"

    else:

        label = "📊 ETF 분석"


    return st.button(
        label,
        use_container_width=True,
        key=f"{key_prefix}_{code}",
    )


# ============================================================
# 내 ETF
# ============================================================

def render_my_etf():

    st.title("📊 내 ETF")

    st.caption(
        "ETF 찾기와 관심 ETF를 한 화면에서 관리하고 바로 분석합니다."
    )


    # ========================================================
    # ETF 찾기
    # ========================================================

    st.markdown("### 🔎 ETF 찾기")


    keyword = st.text_input(
        "ETF 검색",
        value=st.session_state.search_keyword,
        placeholder="종목코드 또는 ETF명을 입력하세요",
        key="etf_search_input",
    )


    st.session_state.search_keyword = keyword


    results = search_etfs(keyword)


    if results:

        # ----------------------------------------------------
        # ★ 중요
        # 드롭다운에는 한글명을 절대로 넣지 않는다.
        # 종목코드만 표시
        # ----------------------------------------------------

        codes = [
            normalize_code(x["code"])
            for x in results
        ]


        selected_search = st.selectbox(
            "검색결과",
            codes,
            key="search_code",
        )


        selected_search = normalize_code(
            selected_search
        )


        # ----------------------------------------------------
        # ★ 핵심 수정부
        #
        # 검색 결과에서 가져온 name을 사용하지 않는다.
        # 캐시도 사용하지 않는다.
        #
        # 종목코드 → BASE_ETFS → Unicode escape 문자열
        # ----------------------------------------------------

        selected_name = get_display_name(
            selected_search
        )


        # ----------------------------------------------------
        # 별도 ETF명 표시
        # ----------------------------------------------------

        with st.container(border=True):

            st.markdown(
                f"### {selected_name}"
            )

            st.caption(
                f"종목코드 {selected_search}"
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


            # 관심 ETF 추가
            if selected_search not in st.session_state.watchlist:

                if st.button(
                    "⭐ 관심 ETF 추가",
                    use_container_width=True,
                    key=f"add_{selected_search}",
                ):

                    st.session_state.watchlist.append(
                        selected_search
                    )

                    st.rerun()

            else:

                st.caption(
                    "⭐ 현재 관심 ETF에 등록되어 있습니다."
                )


    else:

        st.info(
            "검색 결과가 없습니다."
        )


    # ========================================================
    # 관심 ETF
    # ========================================================

    st.divider()

    st.markdown("### ⭐ 관심 ETF")


    if not st.session_state.watchlist:

        st.info(
            "관심 ETF가 없습니다."
        )

        return


    watch_codes = [
        normalize_code(x)
        for x in st.session_state.watchlist
    ]


    watch_code = st.selectbox(
        "관심 ETF 선택",
        watch_codes,
        key="watch_code",
    )


    watch_code = normalize_code(
        watch_code
    )


    # ★ 역시 캐시 이름 사용하지 않음
    watch_name = get_display_name(
        watch_code
    )


    with st.container(border=True):

        st.markdown(
            f"### {watch_name}"
        )

        st.caption(
            f"종목코드 {watch_code}"
        )


        col1, col2 = st.columns(2)


        with col1:

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


        with col2:

            if st.button(
                "🗑 관심 ETF 삭제",
                use_container_width=True,
                key=f"remove_{watch_code}",
            ):

                if watch_code in st.session_state.watchlist:

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

    st.title("🔮 미래테마")

    st.caption(
        "현재 주도 테마에서 다음 수혜 테마로 이어지는 흐름을 확인합니다."
    )


    if st.button(
        "🔄 테마 업데이트",
        use_container_width=True,
    ):

        st.session_state.theme_updated = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        )

        st.rerun()


    if st.session_state.theme_updated:

        st.caption(
            f"마지막 업데이트: "
            f"{st.session_state.theme_updated}"
        )


    for stage, themes in FUTURE_CHAIN.items():

        st.markdown(
            f"### {stage}"
        )


        for theme_name, codes in themes.items():

            with st.container(border=True):

                st.markdown(
                    f"#### {theme_name}"
                )


                valid_codes = []

                for code in codes:

                    code = normalize_code(code)

                    if code in BASE_ETFS:

                        valid_codes.append(code)


                for code in valid_codes:

                    name = get_display_name(code)

                    st.write(
                        f"• {name} ({code})"
                    )


# ============================================================
# 메인
# ============================================================

def main():

    st.title("📊 ETF RADAR")

    st.caption(
        "ETF 차트 · 추세 · 거래량 · 지지/저항 · 대응 시나리오"
    )


    tab1, tab2 = st.tabs(
        [
            "📊 내 ETF",
            "🔮 미래테마",
        ]
    )


    with tab1:

        render_my_etf()


    with tab2:

        render_future_theme()


# ============================================================
# 실행
# ============================================================

if __name__ == "__main__":

    main()