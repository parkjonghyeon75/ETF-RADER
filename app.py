import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from urllib.request import urlopen, Request
import xml.etree.ElementTree as ET
import json
import os


# ============================================================
# ETF RADAR
# 기존 정보밀도 유지 + 가독성 개선 + 미래테마 인라인 분석
# ============================================================

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# FILES
# ============================================================

DATA_DIR = "."

WATCH_FILE = os.path.join(DATA_DIR, "watchlist.json")
HOLD_FILE = os.path.join(DATA_DIR, "holdings.json")
CACHE_FILE = os.path.join(DATA_DIR, "etf_universe_cache.json")


# ============================================================
# BASE ETF
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


DEFAULT_WATCH = [
    "395160",
    "487240",
    "471990",
    "133690",
    "360750",
    "458730",
]


# ============================================================
# FUTURE THEMES
# ============================================================

FUTURE_THEMES = [

    (
        "현재 주도",
        "AI 반도체",
        "AI 연산 수요와 HBM·첨단 패키징 투자 확대의 직접 수혜 구간",
        ["395160", "487240", "471990"]
    ),

    (
        "다음 수혜",
        "데이터센터·AI 인프라",
        "AI 데이터센터 증설에 따라 서버·인프라 투자로 수요가 확산되는 구간",
        ["449170", "434060", "381170"]
    ),

    (
        "다음 수혜",
        "전력 인프라",
        "데이터센터 전력수요 증가와 전력망 투자 확대가 연결되는 구간",
        ["464240", "487130"]
    ),

    (
        "관심 확대",
        "원자력",
        "전력수요 증가에 대응하는 안정적 전원 투자 테마",
        ["464240"]
    ),

    (
        "초기 관심",
        "냉각·열관리",
        "고집적 AI 서버의 발열 증가에 따른 냉각·열관리 수요 확대",
        ["449170"]
    ),
]


# ============================================================
# GLOBAL STYLE
# ============================================================

st.markdown(
    """
<style>

:root {
    --bg: #171817;
    --panel: #232623;
    --panel2: #2b2e2b;
    --panel3: #323632;
    --line: #454a45;

    --text: #f3f0e8;
    --sub: #d2d6d0;
    --muted: #b9beb7;

    --mint: #65d7b5;
    --coral: #f0786d;
    --amber: #e6bb63;
}


/* ----------------------------------------------------------
   APP
---------------------------------------------------------- */

html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
    background: var(--bg) !important;
    color: var(--text) !important;
}

[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
}

.block-container {
    max-width: 1100px;
    padding: 1rem 0.85rem 3rem !important;
}

* {
    box-sizing: border-box;
}

body {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Noto Sans KR",
        sans-serif;
}


/* ----------------------------------------------------------
   TEXT
---------------------------------------------------------- */

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span {
    color: var(--text);
}

[data-testid="stCaptionContainer"] {
    color: var(--sub) !important;
    font-size: 0.84rem !important;
    line-height: 1.45 !important;
}

small,
.caption {
    color: var(--sub) !important;
}

hr {
    border-color: var(--line) !important;
    margin: 0.7rem 0 !important;
}


/* ----------------------------------------------------------
   BUTTON
---------------------------------------------------------- */

button {
    border-radius: 10px !important;
}

.stButton > button {
    background: var(--panel2) !important;
    color: var(--text) !important;
    border: 1px solid var(--line) !important;
    font-weight: 650 !important;
    min-height: 38px;
}

.stButton > button:hover {
    border-color: var(--mint) !important;
    color: var(--mint) !important;
}


/* ----------------------------------------------------------
   INPUT
---------------------------------------------------------- */

input,
textarea {
    background: var(--panel2) !important;
    color: var(--text) !important;
    border: 1px solid var(--line) !important;
}

input::placeholder {
    color: #c1c6c0 !important;
}


/* ----------------------------------------------------------
   SELECTBOX
---------------------------------------------------------- */

[data-baseweb="select"] > div {
    background: var(--panel2) !important;
    border-color: var(--line) !important;
    color: var(--text) !important;
}

[data-baseweb="select"] span,
[data-baseweb="select"] input {
    color: var(--text) !important;
}

[data-baseweb="popover"] {
    background: var(--panel2) !important;
    color: var(--text) !important;
}

[role="option"] {
    background: var(--panel2) !important;
    color: var(--text) !important;
}

[role="option"]:hover {
    background: var(--panel3) !important;
}


/* ----------------------------------------------------------
   RADIO
---------------------------------------------------------- */

[data-testid="stRadio"] label {
    color: var(--text) !important;
}

[data-testid="stRadio"] p {
    color: var(--text) !important;
}


/* ----------------------------------------------------------
   METRIC
---------------------------------------------------------- */

[data-testid="stMetric"] {
    background: var(--panel) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    padding: 0.65rem 0.75rem !important;
}

[data-testid="stMetricLabel"] {
    color: var(--sub) !important;
    font-size: 0.78rem !important;
}

[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-size: 1.25rem !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
}


/* ----------------------------------------------------------
   ALERT
---------------------------------------------------------- */

[data-testid="stAlert"] {
    color: var(--text) !important;
    background: var(--panel) !important;
    border-color: var(--line) !important;
}


/* ----------------------------------------------------------
   EXPANDER
---------------------------------------------------------- */

[data-testid="stExpander"] {
    background: var(--panel) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] summary {
    color: var(--text) !important;
}


/* ----------------------------------------------------------
   DATAFRAME
---------------------------------------------------------- */

[data-testid="stDataFrame"] {
    border: 1px solid var(--line) !important;
}


/* ----------------------------------------------------------
   TABS
---------------------------------------------------------- */

.stTabs [data-baseweb="tab"] {
    color: var(--sub) !important;
}

.stTabs [aria-selected="true"] {
    color: var(--mint) !important;
}


/* ----------------------------------------------------------
   PLOTLY
---------------------------------------------------------- */

.js-plotly-plot,
.plot-container,
.svg-container {
    touch-action: pan-y !important;
}


/* ----------------------------------------------------------
   MOBILE
---------------------------------------------------------- */

@media (max-width: 700px) {

    .block-container {
        padding: 0.65rem 0.65rem 2.5rem !important;
    }

    .stButton > button {
        min-height: 36px;
    }

    .stMarkdown h1 {
        font-size: 1.65rem;
    }

    .stMarkdown h2 {
        font-size: 1.35rem;
    }

    .stMarkdown h3 {
        font-size: 1.05rem;
    }
}

</style>
""",
    unsafe_allow_html=True
)


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
                indent=2
            )

        return True

    except Exception:
        return False


# ============================================================
# ETF CATALOG
# ============================================================

def fetch_catalog():

    url = "https://finance.naver.com/api/sise/etfItemList.nhn"

    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urlopen(req, timeout=8) as r:

        raw = r.read().decode(
            "utf-8",
            errors="ignore"
        )

    data = json.loads(raw)

    rows = data.get(
        "result",
        {}
    ).get(
        "etfItemList",
        []
    )

    out = {}

    for x in rows:

        code = str(
            x.get(
                "itemcode",
                ""
            )
        ).zfill(6)

        name = x.get(
            "itemname",
            ""
        )

        if code and name:
            out[code] = name

    return out


@st.cache_data(
    ttl=1800,
    show_spinner=False
)
def refresh_universe():

    try:

        catalog = fetch_catalog()

        if catalog:

            merged = dict(BASE_ETFS)

            merged.update(catalog)

            save_json(
                CACHE_FILE,
                merged
            )

            return merged, True

    except Exception:
        pass

    cached = load_json(
        CACHE_FILE,
        {}
    )

    merged = dict(BASE_ETFS)

    if isinstance(cached, dict):

        merged.update(
            {
                str(k).zfill(6): v
                for k, v in cached.items()
            }
        )

    return merged, False


# ============================================================
# PRICE DATA
# ============================================================

@st.cache_data(
    ttl=300,
    show_spinner=False
)
def get_price_data(code):

    code = str(code).zfill(6)

    # --------------------------------------------------------
    # NAVER
    # --------------------------------------------------------

    try:

        url = (
            "https://fchart.stock.naver.com/"
            f"spevent.nhn?symbol={code}"
            "&timeframe=day&count=600&requestType=0"
        )

        req = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urlopen(req, timeout=8) as r:
            xml = r.read()

        root = ET.fromstring(xml)

        rows = []

        for item in root.findall("item"):

            raw = item.attrib.get(
                "data",
                ""
            ).split("|")

            if len(raw) >= 6:
                rows.append(raw)

        if rows:

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
                df["Date"]
            )

            for c in [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume"
            ]:

                df[c] = pd.to_numeric(
                    df[c],
                    errors="coerce"
                )

            return (
                df
                .dropna()
                .sort_values("Date")
                .reset_index(drop=True)
            )

    except Exception:
        pass


    # --------------------------------------------------------
    # YAHOO FALLBACK
    # --------------------------------------------------------

    try:

        t = yf.download(
            f"{code}.KS",
            period="2y",
            interval="1d",
            auto_adjust=False,
            progress=False
        )

        if t is not None and not t.empty:

            if isinstance(
                t.columns,
                pd.MultiIndex
            ):
                t.columns = (
                    t.columns
                    .get_level_values(0)
                )

            t = t.reset_index()

            return (
                t[
                    [
                        "Date",
                        "Open",
                        "High",
                        "Low",
                        "Close",
                        "Volume"
                    ]
                ]
                .dropna()
                .reset_index(drop=True)
            )

    except Exception:
        pass


    return pd.DataFrame()


# ============================================================
# INDICATORS
# ============================================================

def indicators(df):

    if df.empty:
        return df

    x = df.copy()

    x["MA20"] = (
        x["Close"]
        .rolling(20)
        .mean()
    )

    x["MA60"] = (
        x["Close"]
        .rolling(60)
        .mean()
    )

    delta = x["Close"].diff()

    gain = (
        delta
        .clip(lower=0)
        .rolling(14)
        .mean()
    )

    loss = (
        -delta
        .clip(upper=0)
        .rolling(14)
        .mean()
    )

    rs = (
        gain /
        loss.replace(
            0,
            np.nan
        )
    )

    x["RSI14"] = (
        100 -
        (
            100 /
            (1 + rs)
        )
    )

    x["VOL20"] = (
        x["Volume"]
        .rolling(20)
        .mean()
    )

    x["VOL_RATIO"] = (
        x["Volume"] /
        x["VOL20"].replace(
            0,
            np.nan
        )
    )

    x["RET20"] = (
        x["Close"] /
        x["Close"].shift(20) -
        1
    ) * 100

    x["HIGH20"] = (
        x["High"]
        .rolling(20)
        .max()
    )

    x["LOW20"] = (
        x["Low"]
        .rolling(20)
        .min()
    )

    x["LOW60"] = (
        x["Low"]
        .rolling(60)
        .min()
    )

    return x


# ============================================================
# ANALYSIS
# ============================================================

def analyze(df):

    if df.empty:
        return None

    x = indicators(df)

    r = x.iloc[-1]

    close = float(r["Close"])

    ma20 = (
        float(r["MA20"])
        if pd.notna(r["MA20"])
        else close
    )

    ma60 = (
        float(r["MA60"])
        if pd.notna(r["MA60"])
        else ma20
    )

    rsi = (
        float(r["RSI14"])
        if pd.notna(r["RSI14"])
        else 50.0
    )

    vr = (
        float(r["VOL_RATIO"])
        if pd.notna(r["VOL_RATIO"])
        else 1.0
    )

    ret20 = (
        float(r["RET20"])
        if pd.notna(r["RET20"])
        else 0.0
    )

    high20 = (
        float(r["HIGH20"])
        if pd.notna(r["HIGH20"])
        else close
    )

    low20 = (
        float(r["LOW20"])
        if pd.notna(r["LOW20"])
        else close
    )

    low60 = (
        float(r["LOW60"])
        if pd.notna(r["LOW60"])
        else low20
    )


    # --------------------------------------------------------
    # JUDGMENT
    # --------------------------------------------------------

    if (
        close > ma20
        and close > ma60
        and rsi >= 70
    ):

        judgment = "상승 추세 · 추격 주의"

        action = "추격보다 눌림 확인"

        reason = (
            f"주가가 MA20·MA60 위에 있어 "
            f"추세는 유지되지만 RSI {rsi:.1f}으로 "
            f"단기 과열 여부를 확인해야 합니다."
        )

        action_reason = (
            "급등 구간에서는 추가 매수보다 "
            "MA20 부근 지지 확인 후 대응하는 편이 "
            "가격 리스크를 줄일 수 있습니다."
        )


    elif (
        close > ma20
        and close > ma60
    ):

        judgment = "상승 추세 유지"

        action = "보유·눌림 접근"

        reason = (
            f"현재가가 MA20·MA60 위에 있고 "
            f"20일 수익률이 {ret20:+.1f}%로 "
            f"중기 추세가 유지되고 있습니다."
        )

        action_reason = (
            f"거래량이 평균의 {vr:.2f}배인 만큼 "
            "추세 지속 여부를 확인하면서 "
            "급등 추격보다 MA20 지지 여부를 "
            "우선 확인합니다."
        )


    elif (
        close < ma20
        and close > ma60
    ):

        judgment = "단기 조정 · 중기 추세 확인"

        action = "MA60 지지 확인"

        reason = (
            "현재가가 MA20 아래로 내려왔지만 "
            "MA60 위에 있어 단기 조정과 "
            "중기 추세가 충돌하는 구간입니다."
        )

        action_reason = (
            "MA60을 지키면서 거래량이 안정되면 "
            "재상승 가능성을 확인하고, "
            "이탈 시 대응 강도를 낮춥니다."
        )


    elif (
        close < ma60
        and rsi < 45
    ):

        judgment = "중기 약세 · 방어 우선"

        action = "신규매수 보류"

        reason = (
            f"현재가가 MA60 아래이고 "
            f"RSI {rsi:.1f}으로 모멘텀이 약해 "
            "중기 추세 회복 확인이 필요합니다."
        )

        action_reason = (
            "MA60 회복과 거래량 개선이 확인되기 전에는 "
            "신규 진입보다 추세 회복 여부를 확인합니다."
        )


    else:

        judgment = "방향 확인 구간"

        action = "돌파·지지 확인"

        reason = (
            f"현재가는 {close:,.0f}원이며 "
            "MA20/MA60과의 방향성이 뚜렷하지 않아 "
            "확인 구간입니다."
        )

        action_reason = (
            "최근 고점 돌파 또는 MA20·MA60 지지 중 "
            "어느 쪽이 확인되는지 보고 "
            "다음 대응을 결정합니다."
        )


    # --------------------------------------------------------
    # PRICE LEVELS
    # --------------------------------------------------------

    first = ma20

    support = min(
        ma60,
        low20
    )

    breakout = high20

    danger = min(
        ma60,
        low20,
        low60
    )


    return {
        "df": x,
        "close": close,
        "ma20": ma20,
        "ma60": ma60,
        "rsi": rsi,
        "vr": vr,
        "ret20": ret20,
        "high20": high20,
        "low20": low20,
        "low60": low60,

        "judgment": judgment,
        "action": action,

        "reason": reason,
        "action_reason": action_reason,

        "first": first,
        "support": support,
        "breakout": breakout,
        "danger": danger,
    }


# ============================================================
# FORMAT
# ============================================================

def fmt_money(v):
    return f"{v:,.0f}원"


def fmt_pct(v):
    return f"{v:+.2f}%"


# ============================================================
# COMPACT INDICATORS
# ============================================================

def metric_row(a):

    cols = st.columns(4)

    values = [

        (
            "RSI14",
            f"{a['rsi']:.1f}"
        ),

        (
            "거래량",
            f"{a['vr']:.2f}배"
        ),

        (
            "20일 수익률",
            fmt_pct(a["ret20"])
        ),

        (
            "MA20 / MA60",
            f"{a['ma20']:,.0f} / "
            f"{a['ma60']:,.0f}"
        ),
    ]


    for c, (label, value) in zip(
        cols,
        values
    ):

        with c:

            st.markdown(
                f"""
                <div style="
                    color:#d2d6d0;
                    font-size:.72rem;
                    font-weight:650;
                    margin-bottom:2px;
                ">
                    {label}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div style="
                    color:#f3f0e8;
                    font-size:.98rem;
                    font-weight:750;
                    line-height:1.35;
                ">
                    {value}
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# CURRENT JUDGMENT
# ============================================================

def render_judgment(a):

    st.markdown(
        "### 현재판단 · 지금대응"
    )

    c1, c2 = st.columns(2)


    with c1:

        st.markdown(
            "**현재판단**"
        )

        st.markdown(
            f"### {a['judgment']}"
        )

        st.markdown(
            "**판단근거**"
        )

        st.write(
            a["reason"]
        )


    with c2:

        st.markdown(
            "**지금대응**"
        )

        st.markdown(
            f"### {a['action']}"
        )

        st.markdown(
            "**대응근거**"
        )

        st.write(
            a["action_reason"]
        )


# ============================================================
# PRICE SCENARIOS
# ============================================================

def price_scenarios(a):

    st.markdown(
        "### 핵심가격 · 대응 시나리오"
    )


    rows = [

        (
            "1차 관심가격",
            a["first"],
            "MA20 부근",
            "눌림 시 지지 여부 확인"
        ),

        (
            "핵심 지지",
            a["support"],
            "MA60·최근 저점",
            "이탈 여부로 중기 추세 확인"
        ),

        (
            "돌파 기준",
            a["breakout"],
            "최근 20일 고점",
            "거래량 동반 돌파 여부 확인"
        ),

        (
            "위험 가격",
            a["danger"],
            "중기 방어선",
            "이탈 시 신규매수보다 방어 우선"
        ),
    ]


    cols = st.columns(4)


    for c, (
        title,
        price,
        basis,
        action
    ) in zip(cols, rows):

        with c:

            st.markdown(
                f"**{title}**"
            )

            st.markdown(
                f"### {fmt_money(price)}"
            )

            st.caption(
                basis
            )

            st.write(
                action
            )


# ============================================================
# CHART
# ============================================================

def render_chart(a):

    x = (
        a["df"]
        .tail(130)
        .copy()
    )


    fig = go.Figure()


    fig.add_trace(
        go.Candlestick(
            x=x["Date"],
            open=x["Open"],
            high=x["High"],
            low=x["Low"],
            close=x["Close"],
            name="가격"
        )
    )


    fig.add_trace(
        go.Scatter(
            x=x["Date"],
            y=x["MA20"],
            name="MA20",
            mode="lines",
            line=dict(
                width=1.5
            )
        )
    )


    fig.add_trace(
        go.Scatter(
            x=x["Date"],
            y=x["MA60"],
            name="MA60",
            mode="lines",
            line=dict(
                width=1.5
            )
        )
    )


    fig.update_layout(

        height=410,

        margin=dict(
            l=5,
            r=5,
            t=10,
            b=5
        ),

        paper_bgcolor="#232623",

        plot_bgcolor="#232623",

        font=dict(
            color="#d2d6d0"
        ),

        xaxis_rangeslider_visible=False,

        dragmode=False,

        hovermode="x unified",

        legend=dict(
            orientation="h",
            y=1.02,
            x=0
        )
    )


    fig.update_xaxes(
        fixedrange=True,
        showgrid=False
    )

    fig.update_yaxes(
        fixedrange=True,
        gridcolor="#3a3e3a"
    )


    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "scrollZoom": False,
            "doubleClick": False,
            "responsive": True
        }
    )


    st.caption(
        "최근 6개월 기준 · 확대/축소/좌우이동 없음"
    )


# ============================================================
# INLINE ETF ANALYSIS
# ============================================================

def render_inline_etf(
    code,
    universe,
    title="ETF 상세 분석"
):

    code = str(code).zfill(6)

    name = universe.get(
        code,
        BASE_ETFS.get(
            code,
            code
        )
    )


    a = get_analysis(code)


    if a is None:

        st.error(
            "가격 데이터를 가져오지 못했습니다."
        )

        return


    st.markdown(
        f"## {title}"
    )

    st.markdown(
        f"### {name}"
    )

    st.caption(
        f"{code} · 기준일 "
        f"{a['df'].iloc[-1]['Date'].strftime('%Y-%m-%d')}"
    )


    pcol, dcol = st.columns(
        [1.2, 1]
    )


    with pcol:

        st.markdown(
            f"# {fmt_money(a['close'])}"
        )


    with dcol:

        prev = (
            float(
                a["df"]
                .iloc[-2]["Close"]
            )
            if len(a["df"]) > 1
            else a["close"]
        )

        chg = (
            a["close"] -
            prev
        )

        pct = (
            chg /
            prev *
            100
            if prev
            else 0
        )


        if chg > 0:

            st.success(
                f"{chg:+,.0f}원 "
                f"({pct:+.2f}%)"
            )

        elif chg < 0:

            st.error(
                f"{chg:+,.0f}원 "
                f"({pct:+.2f}%)"
            )

        else:

            st.info(
                "0원 (0.00%)"
            )


    metric_row(a)

    render_judgment(a)

    price_scenarios(a)


    with st.expander(
        "세부 지표",
        expanded=False
    ):

        st.write(
            f"현재가: {fmt_money(a['close'])} "
            f"· MA20: {fmt_money(a['ma20'])} "
            f"· MA60: {fmt_money(a['ma60'])}"
        )

        st.write(
            f"RSI14: {a['rsi']:.1f} "
            f"· 거래량/20일평균: {a['vr']:.2f}배 "
            f"· 20일 수익률: {a['ret20']:+.2f}%"
        )


    render_chart(a)


# ============================================================
# ETF FINDER
# ============================================================

def render_finder(universe):

    st.markdown(
        "### ETF 찾기"
    )


    query = st.text_input(
        "테마명 또는 ETF명",
        placeholder="예: 반도체 / AI / 전력 / KODEX"
    )


    c1, c2 = st.columns(
        [1, 1]
    )


    with c1:

        apply = st.button(
            "APPLY",
            use_container_width=True,
            key="finder_apply"
        )


    with c2:

        refresh = st.button(
            "시장 새로고침",
            use_container_width=True,
            key="market_refresh"
        )


    if refresh:

        refresh_universe.clear()

        universe2, ok = (
            refresh_universe()
        )

        st.session_state.universe = (
            universe2
        )

        st.session_state.catalog_status = (
            ok
        )

        st.rerun()


    if apply or query:

        q = query.strip().lower()


        if q:

            result = {
                k: v
                for k, v in universe.items()
                if (
                    q in str(k).lower()
                    or
                    q in str(v).lower()
                )
            }

        else:

            result = universe


        if not result:

            st.info(
                "검색 결과가 없습니다."
            )

        else:

            opts = list(
                result.keys()
            )[:250]


            selected = st.selectbox(

                "검색 결과",

                opts,

                format_func=lambda x:
                    f"{result[x]} · {x}",

                key="finder_select"
            )


            if st.button(
                "선택 ETF 분석",
                key="finder_go",
                use_container_width=True
            ):

                st.session_state.selected_code = (
                    selected
                )

                st.rerun()


# ============================================================
# MY ETF
# ============================================================

def render_my_etf(universe):

    st.markdown(
        "# 📊 내 ETF"
    )


    render_finder(
        universe
    )


    st.divider()


    watch = load_json(
        WATCH_FILE,
        DEFAULT_WATCH
    )


    watch = [
        str(x).zfill(6)
        for x in watch
        if str(x).zfill(6)
        in universe
    ]


    if not watch:
        watch = DEFAULT_WATCH


    selected_default = (
        st.session_state.get(
            "selected_code",
            watch[0]
        )
    )


    if selected_default not in universe:
        selected_default = watch[0]


    selected = st.selectbox(

        "분석 ETF",

        watch,

        index=(
            watch.index(
                selected_default
            )
            if selected_default in watch
            else 0
        ),

        format_func=lambda x:
            f"{universe.get(x, x)} · {x}",

        key="my_etf_select"
    )


    st.session_state.selected_code = (
        selected
    )


    code = selected

    name = universe.get(
        code,
        code
    )


    a = get_analysis(
        code
    )


    if a is None:

        st.error(
            "가격 데이터를 가져오지 못했습니다."
        )

        return


    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        f"## {name}"
    )

    st.caption(
        f"{code} · 기준일 "
        f"{a['df'].iloc[-1]['Date'].strftime('%Y-%m-%d')}"
    )


    pcol, dcol = st.columns(
        [1.2, 1]
    )


    with pcol:

        st.markdown(
            f"# {fmt_money(a['close'])}"
        )


    with dcol:

        prev = (
            float(
                a["df"]
                .iloc[-2]["Close"]
            )
            if len(a["df"]) > 1
            else a["close"]
        )

        chg = (
            a["close"] -
            prev
        )

        pct = (
            chg /
            prev *
            100
            if prev
            else 0
        )


        if chg > 0:

            st.success(
                f"{chg:+,.0f}원 "
                f"({pct:+.2f}%)"
            )

        elif chg < 0:

            st.error(
                f"{chg:+,.0f}원 "
                f"({pct:+.2f}%)"
            )

        else:

            st.info(
                "0원 (0.00%)"
            )


    # --------------------------------------------------------
    # COMPACT INDICATORS
    # --------------------------------------------------------

    metric_row(a)


    # --------------------------------------------------------
    # HOLDINGS
    # --------------------------------------------------------

    holdings = load_json(
        HOLD_FILE,
        {}
    )


    h = (
        holdings.get(
            code,
            {}
        )
        if isinstance(
            holdings,
            dict
        )
        else {}
    )


    st.markdown(
        "### 보유상태"
    )


    status = st.radio(

        "보유 여부",

        [
            "미보유",
            "보유중"
        ],

        index=(
            1 if h else 0
        ),

        horizontal=True,

        key=f"hold_status_{code}"
    )


    if status == "보유중":

        c1, c2, c3 = st.columns(3)


        with c1:

            avg = st.number_input(

                "평균단가",

                min_value=0.0,

                value=float(
                    h.get(
                        "avg",
                        0
                    )
                ),

                step=100.0,

                key=f"avg_{code}"
            )


        with c2:

            qty = st.number_input(

                "수량",

                min_value=0.0,

                value=float(
                    h.get(
                        "qty",
                        0
                    )
                ),

                step=1.0,

                key=f"qty_{code}"
            )


        with c3:

            st.write("")
            st.write("")

            if st.button(
                "보유정보 저장",
                key=f"save_{code}",
                use_container_width=True
            ):

                holdings[code] = {
                    "avg": avg,
                    "qty": qty
                }

                save_json(
                    HOLD_FILE,
                    holdings
                )

                st.success(
                    "저장했습니다."
                )


    else:

        if st.button(
            "보유정보 삭제",
            key=f"del_{code}"
        ):

            if code in holdings:
                del holdings[code]

            save_json(
                HOLD_FILE,
                holdings
            )

            st.success(
                "삭제했습니다."
            )


    # --------------------------------------------------------
    # CORE ANALYSIS
    # --------------------------------------------------------

    render_judgment(a)

    price_scenarios(a)

    render_chart(a)


# ============================================================
# FUTURE THEME ETF CARD
# ============================================================

def render_theme_card(
    theme,
    stage,
    reason,
    codes,
    universe
):

    st.markdown(
        f"**{stage}**"
    )

    st.markdown(
        f"### {theme}"
    )

    st.caption(
        reason
    )


    for code in codes:

        code = str(code).zfill(6)

        name = universe.get(
            code,
            BASE_ETFS.get(
                code,
                code
            )
        )


        a = get_analysis(
            code
        )


        if a is None:
            continue


        with st.container(
            border=True
        ):

            c1, c2, c3, c4 = st.columns(
                [1.7, 1, 1, 1]
            )


            with c1:

                st.markdown(
                    f"**{name}**"
                )

                st.caption(
                    code
                )

                st.markdown(
                    f"**{fmt_money(a['close'])}**"
                )


            with c2:

                st.caption(
                    "RSI14"
                )

                st.write(
                    f"{a['rsi']:.1f}"
                )


            with c3:

                st.caption(
                    "거래량"
                )

                st.write(
                    f"{a['vr']:.2f}배"
                )


            with c4:

                st.caption(
                    "20일"
                )

                st.write(
                    fmt_pct(
                        a["ret20"]
                    )
                )


            st.caption(
                f"판단: {a['judgment']} "
                f"· 대응: {a['action']}"
            )


            if st.button(
                "ETF 분석",
                key=f"theme_detail_{code}",
                use_container_width=True
            ):

                st.session_state.theme_detail_code = (
                    code
                )

                st.rerun()


# ============================================================
# FUTURE THEMES
# ============================================================

def render_future_themes(
    universe
):

    st.markdown(
        "# 🚀 미래테마"
    )

    st.caption(
        "현재 주도 → 다음 수혜 → 초기 관심 순으로 "
        "ETF와 기술지표를 함께 확인합니다."
    )


    if not st.session_state.get(
        "catalog_status",
        True
    ):

        st.caption(
            "외부 ETF 목록 연결이 지연되어 "
            "기본/저장 목록을 함께 사용합니다."
        )


    for (
        stage,
        theme,
        reason,
        codes
    ) in FUTURE_THEMES:

        render_theme_card(
            theme,
            stage,
            reason,
            codes,
            universe
        )

        st.divider()


    # ========================================================
    # INLINE DETAIL
    # ========================================================

    detail = st.session_state.get(
        "theme_detail_code"
    )


    if detail:

        st.markdown("---")


        render_inline_etf(
            detail,
            universe,
            "미래테마 · ETF 분석"
        )


        if st.button(
            "분석 닫기",
            key="close_theme_detail"
        ):

            st.session_state.theme_detail_code = None

            st.rerun()


# ============================================================
# SESSION STATE
# ============================================================

if "main_page" not in st.session_state:

    st.session_state.main_page = (
        "📊 내 ETF"
    )


if "page_request" not in st.session_state:

    st.session_state.page_request = None


if "selected_code" not in st.session_state:

    st.session_state.selected_code = (
        DEFAULT_WATCH[0]
    )


if "theme_detail_code" not in st.session_state:

    st.session_state.theme_detail_code = None


if "catalog_status" not in st.session_state:

    st.session_state.catalog_status = True


# ============================================================
# NAVIGATION REQUEST
# ============================================================

if st.session_state.page_request:

    requested_page = (
        st.session_state.page_request
    )

    st.session_state.page_request = None

    if requested_page in [
        "📊 내 ETF",
        "🚀 미래테마"
    ]:

        st.session_state.main_page = (
            requested_page
        )


# ============================================================
# ETF UNIVERSE
# ============================================================

universe = st.session_state.get(
    "universe"
)


if not universe:

    universe, ok = (
        refresh_universe()
    )

    st.session_state.universe = (
        universe
    )

    st.session_state.catalog_status = (
        ok
    )


# ============================================================
# MAIN NAVIGATION
# ============================================================

page = st.radio(

    "페이지",

    [
        "📊 내 ETF",
        "🚀 미래테마"
    ],

    index=(
        0
        if st.session_state.main_page
        == "📊 내 ETF"
        else 1
    ),

    horizontal=True,

    key="main_page_radio",

    label_visibility="collapsed"
)


st.session_state.main_page = page


# ============================================================
# PAGE
# ============================================================

if page == "📊 내 ETF":

    render_my_etf(
        universe
    )

else:

    render_future_themes(
        universe
    )