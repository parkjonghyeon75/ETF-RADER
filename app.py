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
    "091180": "KODEX 자동차",
    "139260": "TIGER 200 IT",
    "305720": "KODEX 2차전지산업",
    "364690": "KODEX 혁신기술테마액티브",
    "117700": "KODEX 건설",
    "140700": "KODEX 보험",
    "144600": "KODEX 은행",
    "102780": "KODEX 삼성그룹",
    "261220": "KODEX WTI원유선물(H)",
    "449170": "TIGER 글로벌AI인프라액티브",
    "434060": "TIGER 글로벌AI&반도체액티브",
    "464240": "KODEX AI전력핵심설비",
    "487130": "KODEX AI전력인프라",
    "475050": "ACE 글로벌반도체TOP4 Plus",
    "469150": "ACE AI반도체포커스",
    "130730": "KOSEF 단기자금",
    "161510": "PLUS 고배당주",
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
    "현재주도": {
        "AI반도체·핵심장비": [
            "395160",
            "487240",
            "471990",
            "469150",
        ],
        "미국 빅테크 & 혁신": [
            "133690",
            "360750",
            "381170",
        ],
    },

    "다음수혜": {
        "데이터센터·AI 인프라": [
            "449170",
            "434060",
        ],
        "전력 인프라 & 설비": [
            "464240",
            "487130",
        ],
        "바이오·헬스케어 혁신": [
            "364690",
        ],
    },

    "초기관심": {
        "로보틱스 & AI 자율주행": [
            "458730",
        ],
        "우주항공 & 방산": [
            "364690",
        ],
        "SMR·원자력 에너지": [
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
# 세션
# ============================================================

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

if "holdings" not in st.session_state:
    st.session_state.holdings = []

if "etf_universe" not in st.session_state:
    st.session_state.etf_universe = {}

if "selected_code" not in st.session_state:
    st.session_state.selected_code = None

if "future_detail_code" not in st.session_state:
    st.session_state.future_detail_code = None

if "theme_last_update" not in st.session_state:
    st.session_state.theme_last_update = None

if "nav" not in st.session_state:
    st.session_state.nav = "📊 내 ETF"

if "search_code" not in st.session_state:
    st.session_state.search_code = None

if "watch_code" not in st.session_state:
    st.session_state.watch_code = None


# ============================================================
# JSON
# ============================================================

def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass

    return default


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
            )
    except Exception:
        pass


if not st.session_state.watchlist:
    st.session_state.watchlist = load_json(
        WATCHLIST_FILE,
        DEFAULT_WATCHLIST.copy(),
    )

if not st.session_state.holdings:
    st.session_state.holdings = load_json(
        HOLDINGS_FILE,
        [],
    )

if not st.session_state.etf_universe:
    st.session_state.etf_universe = load_json(
        UNIVERSE_FILE,
        {},
    )


# ============================================================
# ETF 이름
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


# ============================================================
# 검색
# ============================================================

def search_etfs(keyword):

    keyword = str(keyword).strip().lower()

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

    if not keyword:
        return []

    result = []

    for code, name in universe.items():

        code = normalize_code(code)
        name = str(name)

        if (
            keyword in code.lower()
            or keyword in name.lower()
        ):
            result.append(
                {
                    "code": code,
                    "name": name,
                }
            )

    result.sort(
        key=lambda x: (
            not x["code"].startswith(keyword),
            x["name"],
        )
    )

    return result


# ============================================================
# Yahoo
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
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

        if isinstance(df.columns, pd.MultiIndex):

            df.columns = [
                col[0] if isinstance(col, tuple) else col
                for col in df.columns
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
# 지표
# ============================================================

def calculate_indicators(df):

    if df.empty:
        return df

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

    rs = avg_gain / avg_loss.replace(
        0,
        np.nan,
    )

    d["RSI14"] = 100 - (
        100 / (1 + rs)
    )

    d["VOL20"] = d["Volume"].rolling(20).mean()

    d["VOL_RATIO"] = (
        d["Volume"]
        / d["VOL20"].replace(0, np.nan)
    )

    d["RET5"] = close.pct_change(5) * 100
    d["RET20"] = close.pct_change(20) * 100

    d["HIGH20"] = d["High"].rolling(20).max()
    d["LOW20"] = d["Low"].rolling(20).min()

    d["HIGH60"] = d["High"].rolling(60).max()
    d["LOW60"] = d["Low"].rolling(60).min()

    return d


# ============================================================
# 안전 숫자
# ============================================================

def num(value):

    try:

        if pd.isna(value):
            return np.nan

        return float(value)

    except Exception:
        return np.nan


# ============================================================
# 판단
# ============================================================

def get_judgment(df):

    if df.empty:

        return (
            "데이터 부족",
            "분석 대기",
            [],
        )

    x = df.iloc[-1]

    close = num(x["Close"])
    ma20 = num(x["MA20"])
    ma60 = num(x["MA60"])
    rsi = num(x["RSI14"])
    volume_ratio = num(x["VOL_RATIO"])

    reasons = []

    if (
        not np.isnan(close)
        and not np.isnan(ma20)
        and not np.isnan(ma60)
    ):

        if close > ma20 > ma60:

            trend = "상승추세"

            reasons.append(
                "현재가가 20일선과 60일선 위에 있습니다."
            )

        elif close < ma20 < ma60:

            trend = "하락추세"

            reasons.append(
                "현재가가 20일선과 60일선 아래에 있습니다."
            )

        else:

            trend = "혼조"

            reasons.append(
                "단기와 중기 이동평균선 방향이 엇갈리고 있습니다."
            )

    else:

        trend = "데이터 부족"

    if not np.isnan(rsi):

        if rsi >= 70:

            reasons.append(
                f"RSI {rsi:.1f}로 단기 과열 여부를 확인해야 합니다."
            )

        elif rsi <= 30:

            reasons.append(
                f"RSI {rsi:.1f}로 과매도 구간입니다."
            )

        else:

            reasons.append(
                f"RSI {rsi:.1f}로 중립권입니다."
            )

    if not np.isnan(volume_ratio):

        if volume_ratio >= 1.5:

            reasons.append(
                f"거래량이 20일 평균의 약 {volume_ratio:.1f}배입니다."
            )

        elif volume_ratio < 0.7:

            reasons.append(
                "거래량이 평균보다 낮아 추격보다 확인이 필요합니다."
            )

        else:

            reasons.append(
                "거래량은 평균적인 수준입니다."
            )

    if trend == "상승추세":

        if not np.isnan(rsi) and rsi >= 70:

            title = "상승추세 · 과열주의"
            action = "보유 중심 · 추격매수 주의"

        elif not np.isnan(volume_ratio) and volume_ratio >= 1.5:

            title = "상승추세 · 수급강화"
            action = "보유 중심 · 눌림목 대응"

        else:

            title = "상승추세"
            action = "보유 중심 · 눌림목 매수 검토"

    elif trend == "하락추세":

        title = "하락추세"
        action = "신규매수 보수적 접근"

    else:

        title = "혼조구간"
        action = "방향 확인 후 대응"

    return title, action, reasons


# ============================================================
# 가격구간
# ============================================================

def get_levels(df):

    if df.empty:
        return {}

    x = df.iloc[-1]

    ma20 = num(x["MA20"])
    ma60 = num(x["MA60"])
    low20 = num(x["LOW20"])
    low60 = num(x["LOW60"])
    high20 = num(x["HIGH20"])

    support_values = [
        v for v in [ma60, low20]
        if not np.isnan(v)
    ]

    risk_values = [
        v for v in [ma60, low20, low60]
        if not np.isnan(v)
    ]

    return {
        "first": ma20,
        "support": min(support_values)
        if support_values else np.nan,
        "breakout": high20,
        "risk": min(risk_values)
        if risk_values else np.nan,
    }


# ============================================================
# 차트
# ============================================================

def render_chart(df):

    if df.empty:
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
        height=420,
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
# 분석 화면
# ============================================================

def render_analysis(code):

    code = normalize_code(code)
    name = get_etf_name(code)

    # --------------------------------------------------------
    # 한글 ETF명은 HTML을 사용하지 않음
    # --------------------------------------------------------

    st.subheader(name)
    st.caption(f"종목코드 {code}")

    df = fetch_yahoo(code)

    if df.empty:

        st.error(
            "시장 데이터를 가져오지 못했습니다."
        )

        return

    df = calculate_indicators(df)

    if df.empty:
        st.error("분석 데이터가 없습니다.")
        return

    last = df.iloc[-1]

    price = num(last["Close"])

    if len(df) >= 2:
        prev = num(df.iloc[-2]["Close"])
    else:
        prev = np.nan

    if (
        not np.isnan(price)
        and not np.isnan(prev)
        and prev != 0
    ):

        change = (
            price / prev - 1
        ) * 100

    else:

        change = np.nan

    # --------------------------------------------------------
    # 가격 카드
    # --------------------------------------------------------

    with st.container(border=True):

        st.caption("현재가")

        if np.isnan(price):

            st.metric(
                "현재가",
                "-",
            )

        else:

            delta = (
                f"{change:+.2f}%"
                if not np.isnan(change)
                else None
            )

            st.metric(
                "현재가",
                f"{price:,.0f}원",
                delta=delta,
            )

    # --------------------------------------------------------
    # 판단
    # --------------------------------------------------------

    title, action, reasons = get_judgment(df)

    st.markdown("### 📌 현재 판단")

    with st.container(border=True):

        st.markdown(
            f"#### {title}"
        )

        st.write(
            f"**대응:** {action}"
        )

        for reason in reasons:

            st.write(
                f"• {reason}"
            )

    # --------------------------------------------------------
    # 가격구간
    # --------------------------------------------------------

    levels = get_levels(df)

    st.markdown("### 🎯 핵심 가격구간")

    with st.container(border=True):

        a, b = st.columns(2)

        with a:

            first = levels.get(
                "first",
                np.nan,
            )

            support = levels.get(
                "support",
                np.nan,
            )

            st.metric(
                "1차 관심",
                (
                    f"{first:,.0f}원"
                    if not np.isnan(first)
                    else "-"
                ),
            )

            st.metric(
                "주요 지지",
                (
                    f"{support:,.0f}원"
                    if not np.isnan(support)
                    else "-"
                ),
            )

        with b:

            breakout = levels.get(
                "breakout",
                np.nan,
            )

            risk = levels.get(
                "risk",
                np.nan,
            )

            st.metric(
                "돌파 기준",
                (
                    f"{breakout:,.0f}원"
                    if not np.isnan(breakout)
                    else "-"
                ),
            )

            st.metric(
                "리스크 기준",
                (
                    f"{risk:,.0f}원"
                    if not np.isnan(risk)
                    else "-"
                ),
            )

    # --------------------------------------------------------
    # 시나리오
    # --------------------------------------------------------

    st.markdown("### 🧭 대응 시나리오")

    with st.container(border=True):

        st.markdown("**📈 상승 시나리오**")

        st.write(
            "최근 고점 돌파와 거래량 증가가 동시에 나타나는지 "
            "확인합니다. 급등 직후에는 추격보다 재눌림 여부를 "
            "확인하는 방식으로 접근합니다."
        )

        st.markdown("**↔️ 눌림목 시나리오**")

        st.write(
            "20일선 또는 주요 지지구간까지 조정될 경우 "
            "지지 여부와 거래량 감소 여부를 확인합니다."
        )

        st.markdown("**⚠️ 하락 시나리오**")

        st.write(
            "주요 지지선 이탈과 거래량 증가가 동시에 나타나면 "
            "신규매수보다 추세 회복 여부를 우선 확인합니다."
        )

    # --------------------------------------------------------
    # 차트
    # --------------------------------------------------------

    st.markdown("### 📈 차트")

    render_chart(df)


# ============================================================
# 통합 ETF 화면
# ============================================================

def render_my_etf():

    st.markdown(
        "# 📊 내 ETF"
    )

    st.caption(
        "ETF를 검색하고 관심종목에 추가한 뒤 바로 분석할 수 있습니다."
    )

    # ========================================================
    # ETF 찾기
    # ========================================================

    st.markdown("### 🔎 ETF 찾기")

    keyword = st.text_input(
        "ETF 검색",
        placeholder="ETF명 또는 종목코드 입력",
        label_visibility="collapsed",
        key="search_keyword",
    )

    results = search_etfs(keyword)

    if results:

        # ====================================================
        # 중요
        # 드롭다운에는 한글 이름을 절대 넣지 않는다.
        # ====================================================

        codes = [
            normalize_code(x["code"])
            for x in results
        ]

        selected_code = st.selectbox(
            "검색 결과",
            codes,
            key="search_code",
            label_visibility="collapsed",
        )

        selected_code = normalize_code(
            selected_code
        )

        # ----------------------------------------------------
        # 한글명은 네이티브 Streamlit
        # ----------------------------------------------------

        selected_name = get_etf_name(
            selected_code
        )

        with st.container(border=True):

            st.subheader(
                selected_name
            )

            st.caption(
                f"종목코드 {selected_code}"
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "➕ 관심 ETF 추가",
                    use_container_width=True,
                    key="add_search_etf",
                ):

                    if (
                        selected_code
                        not in st.session_state.watchlist
                    ):

                        st.session_state.watchlist.append(
                            selected_code
                        )

                        save_json(
                            WATCHLIST_FILE,
                            st.session_state.watchlist,
                        )

                        st.success(
                            "관심 ETF에 추가했습니다."
                        )

                    else:

                        st.info(
                            "이미 관심 ETF에 등록되어 있습니다."
                        )

            with c2:

                if st.button(
                    "📊 ETF 분석",
                    use_container_width=True,
                    key="analyze_search_etf",
                ):

                    st.session_state.selected_code = (
                        selected_code
                    )

                    st.rerun()

    elif keyword.strip():

        st.info(
            "검색 결과가 없습니다."
        )

    else:

        st.caption(
            "ETF명 또는 종목코드를 입력하세요."
        )

    # ========================================================
    # 내 ETF
    # ========================================================

    st.markdown("---")

    st.markdown("### ⭐ 관심 ETF")

    watchlist = [
        normalize_code(x)
        for x in st.session_state.watchlist
    ]

    watchlist = list(
        dict.fromkeys(watchlist)
    )

    if not watchlist:

        st.info(
            "등록된 관심 ETF가 없습니다."
        )

    else:

        # 역시 코드만
        selected_watch = st.selectbox(
            "관심 ETF",
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
                f"종목코드 {selected_watch}"
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "📊 선택 ETF 분석",
                    use_container_width=True,
                    key="analyze_watch_etf",
                ):

                    st.session_state.selected_code = (
                        selected_watch
                    )

                    st.rerun()

            with c2:

                if st.button(
                    "🗑 관심 ETF 삭제",
                    use_container_width=True,
                    key="delete_watch_etf",
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

                        st.rerun()

    # ========================================================
    # 선택 ETF 분석
    # ========================================================

    if st.session_state.selected_code:

        st.markdown("---")

        st.markdown("## 📊 ETF 분석")

        render_analysis(
            st.session_state.selected_code
        )


# ============================================================
# 미래테마
# ============================================================

def render_future_theme():

    st.markdown(
        "# 🔮 미래테마"
    )

    st.caption(
        "현재 주도 → 다음 수혜 → 초기 관심 순으로 확인합니다."
    )

    if st.button(
        "🔄 테마 업데이트",
        use_container_width=False,
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
            "마지막 업데이트: "
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

            columns = st.columns(
                min(3, len(codes))
            )

            for i, code in enumerate(codes):

                code = normalize_code(code)
                name = get_etf_name(code)

                with columns[i % len(columns)]:

                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            f"**{name}**"
                        )

                        st.caption(
                            code
                        )

                        raw = fetch_yahoo(code)

                        if (
                            raw is not None
                            and not raw.empty
                        ):

                            last_price = num(
                                raw.iloc[-1]["Close"]
                            )

                            if not np.isnan(last_price):

                                st.write(
                                    f"**{last_price:,.0f}원**"
                                )

                            if len(raw) >= 2:

                                previous = num(
                                    raw.iloc[-2]["Close"]
                                )

                                if (
                                    not np.isnan(last_price)
                                    and not np.isnan(previous)
                                    and previous != 0
                                ):

                                    change = (
                                        last_price /
                                        previous -
                                        1
                                    ) * 100

                                    st.caption(
                                        f"전일 대비 {change:+.2f}%"
                                    )

                        button_key = (
                            "future_analysis_"
                            + stage
                            + "_"
                            + theme
                            + "_"
                            + code
                        )

                        if st.button(
                            "ETF 분석",
                            use_container_width=True,
                            key=button_key,
                        ):

                            if (
                                st.session_state.future_detail_code
                                == code
                            ):

                                st.session_state.future_detail_code = None

                            else:

                                st.session_state.future_detail_code = code

                            st.rerun()

                        # ------------------------------------
                        # 방금 누른 버튼 바로 아래
                        # ------------------------------------

                        if (
                            st.session_state.future_detail_code
                            == code
                        ):

                            st.markdown("---")

                            render_analysis(
                                code
                            )

                            if st.button(
                                "📊 내 ETF 화면으로 이동",
                                use_container_width=True,
                                key=f"go_my_etf_{code}",
                            ):

                                st.session_state.selected_code = code
                                st.session_state.nav = "📊 내 ETF"

                                st.rerun()


# ============================================================
# 상단
# ============================================================

st.markdown(
    "# 📊 ETF RADAR"
)

st.caption(
    "국내 ETF 기술적 흐름 · 가격구간 · 대응 시나리오"
)


# ============================================================
# 메뉴
# ============================================================

nav = st.radio(
    "메뉴",
    [
        "📊 내 ETF",
        "🔮 미래테마",
    ],
    horizontal=True,
    key="nav",
    label_visibility="collapsed",
)


st.markdown("---")


# ============================================================
# 화면
# ============================================================

if nav == "📊 내 ETF":

    render_my_etf()

elif nav == "🔮 미래테마":

    render_future_theme()


# ============================================================
# 하단
# ============================================================

st.divider()

st.caption(
    "ETF RADAR · Technical Analysis Dashboard"
)