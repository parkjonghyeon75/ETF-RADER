# -*- coding: utf-8 -*-

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import json
import os
import html
from datetime import datetime

st.set_page_config(
    page_title="ETF RADAR",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def esc(value):
    return html.escape(str(value))

CSS = r"""
<style>
:root {
    --bg: #07111f; --bg2: #091522; --panel: #0d1928;
    --text: #e3eaf2; --blue: #62aef2; --green: #39c99a; --red: #ef6678; --yellow: #d5ae58;
}
html, body, .stApp, .stApp *, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"] {
    font-family: "Noto Sans KR", sans-serif !important;
    background: #07111f !important;
    color: #e3eaf2 !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"] { background: #07111f !important; }
[data-testid="stSidebar"] { background: #091522 !important; }
[data-testid="stSidebar"] * { color: #d7e1eb !important; }
.block-container { max-width: 1180px !important; padding: 10px 12px 32px !important; }

div[data-baseweb="input"], div[data-baseweb="input"] > div,
div[data-baseweb="select"], div[data-baseweb="select"] > div {
    background: #0c1928 !important; border-color: #294159 !important; color: #ffffff !important;
}
div[data-baseweb="input"] input { background: transparent !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
div[data-baseweb="select"] span, div[data-baseweb="select"] div { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"], li[role="option"] {
    background: #0b1725 !important; color: #ffffff !important;
}
li[role="option"] * { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
li[role="option"]:hover { background: #16283b !important; }

.stButton > button {
    background: #122236 !important; color: #dce5ee !important; border: 1px solid #29445d !important;
    border-radius: 8px !important; font-weight: 700 !important; min-height: 36px !important;
}
.stButton > button:hover { background: #18314a !important; border-color: #4a7fa8 !important; color: #ffffff !important; }

[data-testid="stAlert"] { background: #0d1928 !important; border: 1px solid #263d53 !important; color: #cbd6e1 !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: #72869b !important; }

.app-header { padding: 3px 0 10px; }
.app-title { font-size: 1.45rem; font-weight: 850; color: #e5edf5 !important; }
.app-subtitle { font-size: 0.74rem; color: #74889d !important; margin-top: 3px; }

.hero { background: #0d1928; border: 1px solid #263e54; border-radius: 12px; padding: 14px; margin-bottom: 10px; }
.hero-name { font-size: 1.16rem; font-weight: 800; color: #e0e8f0 !important; }
.hero-code { font-size: 0.70rem; color: #73879b !important; margin-top: 2px; }
.quote-row { display: flex; gap: 12px; align-items: baseline; margin-top: 9px; }
.quote-price { font-size: 1.72rem; font-weight: 850; color: #e6edf4 !important; }
.quote-change { font-size: 0.84rem; font-weight: 750; }
.hero-date { font-size: 0.68rem; color: #71859a !important; margin-top: 7px; }

.positive { color: #39c99a !important; }
.negative { color: #ef6678 !important; }
.neutral { color: #a8b7c6 !important; }

.section-title { font-size: 0.90rem; font-weight: 800; color: #cdd8e3 !important; margin: 15px 0 7px; }

.evidence-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 6px 0 9px; }
.evidence-box { background: #0b1725; border: 1px solid #20374c; border-radius: 8px; padding: 8px; }
.evidence-label { font-size: 0.64rem; color: #74879b !important; }
.evidence-value { font-size: 0.86rem; font-weight: 800; color: #cdd8e3 !important; margin-top: 2px; }
.evidence-sub { font-size: 0.62rem; color: #71859a !important; margin-top: 2px; }

.judgment-box, .action-box { background: #0d1928; border: 1px solid #22394e; border-radius: 9px; padding: 11px; min-height: 112px; }
.judgment-box { border-left: 3px solid #4b8bbd; }
.action-box { border-left: 3px solid #90763c; }
.judgment-title, .action-title { font-size: 0.66rem; color: #75899d !important; font-weight: 750; }
.action-title { color: #b59a5a !important; }
.judgment-main { font-size: 0.96rem; font-weight: 800; color: #d6e0e9 !important; margin-top: 4px; }
.judgment-reason, .action-main { font-size: 0.74rem; line-height: 1.48; color: #aab9c8 !important; margin-top: 7px; }
.reason-label, .action-reason-label { font-size: 0.64rem; font-weight: 750; margin-bottom: 3px; }
.reason-label { color: #6f8499 !important; }
.action-reason-label { color: #a48b50 !important; }

.holding-box { background: #0b1725; border: 1px solid #20374c; border-radius: 8px; padding: 9px; }
.holding-value { font-size: 0.84rem; font-weight: 800; color: #ccd7e1 !important; }
.holding-detail { font-size: 0.69rem; color: #8294a7 !important; margin-top: 3px; }

.theme-card-lead, .theme-card-next, .theme-card-early { border-radius: 10px; padding: 12px; margin-bottom: 7px; }
.theme-card-lead { background: linear-gradient(135deg, #0d2238 0%, #0d1928 100%); border: 1px solid #2a5278; border-left: 4px solid #39c99a; }
.theme-card-next { background: linear-gradient(135deg, #1f1b11 0%, #0d1928 100%); border: 1px solid #5a4b28; border-left: 4px solid #d5ae58; }
.theme-card-early { background: linear-gradient(135deg, #121c2e 0%, #0d1928 100%); border: 1px solid #2c4464; border-left: 4px solid #62aef2; }
.theme-stage { font-size: 0.65rem; font-weight: 800; }
.theme-title { font-size: 0.98rem; font-weight: 800; color: #d2dde7 !important; margin-top: 2px; }
.theme-reason { font-size: 0.71rem; color: #899bab !important; margin: 4px 0 8px; }

.theme-etf-box { background: #0b1725; border: 1px solid #1f3549; border-radius: 8px; padding: 9px; min-height: 145px; }
.theme-etf-name { font-size: 0.76rem; font-weight: 800; color: #d0dbe5 !important; }
.theme-etf-code { font-size: 0.62rem; color: #708398 !important; margin-top: 2px; }
.theme-data-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 4px; margin-top: 7px; }
.theme-data-item { background: #091522; border-radius: 5px; padding: 5px; }
.theme-data-label { font-size: 0.57rem; color: #6f8296 !important; }
.theme-data-value { font-size: 0.70rem; font-weight: 800; color: #bdcad6 !important; margin-top: 1px; }

.future-analysis-panel { background: #0a1523; border: 2px solid #2d4c6a; border-radius: 10px; padding: 14px; margin: 8px 0 16px 0; }
.future-update-box { background: #0b1725; border: 1px solid #29445d; border-radius: 9px; padding: 9px 10px; margin-bottom: 10px; }
.future-update-title { font-size: 0.72rem; font-weight: 800; color: #cbd8e3 !important; }
.future-update-time { font-size: 0.61rem; color: #71869a !important; margin-top: 2px; }
</style>
"""
st.html(CSS)

WATCHLIST_FILE, HOLDINGS_FILE, UNIVERSE_FILE = "watchlist.json", "holdings.json", "etf_universe_cache.json"

BASE_ETFS = {
    "395160": "KODEX AI반도체핵심장비", "487240": "KODEX AI반도체", "471990": "KODEX AI반도체TOP2Plus",
    "133690": "TIGER 미국나스닥100", "360750": "TIGER 미국S&P500", "458730": "TIGER 글로벌AI&로봇",
    "381170": "TIGER 미국테크TOP10 INDXX", "396500": "TIGER 반도체", "091160": "KODEX 반도체",
    "091180": "KODEX 자동차", "139260": "TIGER 200 IT", "305720": "KODEX 2차전지산업",
    "364690": "KODEX 혁신기술테마액티브", "117700": "KODEX 건설", "140700": "KODEX 보험",
    "144600": "KODEX 은행", "102780": "KODEX 삼성그룹", "261220": "KODEX WTI원유선물(H)",
    "449170": "TIGER 글로벌AI인프라액티브", "434060": "TIGER 글로벌AI&반도체액티브",
    "464240": "KODEX AI전력핵심설비", "487130": "KODEX AI전력인프라", "475050": "ACE 글로벌반도체TOP4 Plus",
    "469150": "ACE AI반도체포커스", "130730": "KOSEF 단기자금", "161510": "PLUS 고배당주",
}

DEFAULT_WATCHLIST = ["395160", "487240", "471990", "133690", "360750", "458730"]

THEMES = {
    "AI반도체·핵심장비": {"stage": "현재주도", "badge_class": "theme-card-lead", "stage_color": "#39c99a", "keywords": ["AI반도체", "반도체", "AI", "HBM", "포커스"], "seeds": ["395160", "487240", "471990", "469150"], "reason": "AI 하드웨어 연산 수요 및 HBM·장비 투자 집중 구간"},
    "미국 빅테크 & 혁신": {"stage": "현재주도", "badge_class": "theme-card-lead", "stage_color": "#39c99a", "keywords": ["나스닥", "S&P500", "테크TOP10"], "seeds": ["133690", "360750", "381170"], "reason": "글로벌 AI 빅테크 실적 성장이 이끄는 주도 영역"},
    "데이터센터·AI 인프라": {"stage": "다음수혜", "badge_class": "theme-card-next", "stage_color": "#d5ae58", "keywords": ["데이터센터", "AI인프라"], "seeds": ["449170", "434060"], "reason": "클라우드 데이터센터 및 서버 네트워크 인프라 확충 수혜"},
    "전력 인프라 & 설비": {"stage": "다음수혜", "badge_class": "theme-card-next", "stage_color": "#d5ae58", "keywords": ["전력", "전력인프라", "전력핵심설비"], "seeds": ["464240", "487130"], "reason": "데이터센터 전력 수요 급증에 따른 전력망 및 설비 투자"},
    "바이오·헬스케어 혁신": {"stage": "다음수혜", "badge_class": "theme-card-next", "stage_color": "#d5ae58", "keywords": ["바이오", "헬스케어"], "seeds": ["364690"], "reason": "고령화 및 신약 개발 모멘텀의 구조적 성장 섹터"},
    "로보틱스 & AI 자율주행": {"stage": "초기관심", "badge_class": "theme-card-early", "stage_color": "#62aef2", "keywords": ["로봇", "자율주행", "AI&로봇"], "seeds": ["458730"], "reason": "제조 및 일상 속 자동화 도입에 따른 장기 침투율 상승"},
    "우주항공 & 방산": {"stage": "초기관심", "badge_class": "theme-card-early", "stage_color": "#62aef2", "keywords": ["우주", "방산", "항공"], "seeds": ["364690"], "reason": "글로벌 안보 환경 변화 및 상업용 우주 탐사 인프라"},
    "SMR·원자력 에너지": {"stage": "초기관심", "badge_class": "theme-card-early", "stage_color": "#62aef2", "keywords": ["원자력", "원전", "SMR"], "seeds": ["130730", "161510"], "reason": "AI 데이터센터의 독립 무탄소 전력원으로 급부상 중인 섹터"}
}

FUTURE_CHAIN = [
    ("현재주도", ["AI반도체·핵심장비", "미국 빅테크 & 혁신"]),
    ("다음수혜", ["데이터센터·AI 인프라", "전력 인프라 & 설비", "바이오·헬스케어 혁신"]),
    ("초기관심", ["로보틱스 & AI 자율주행", "우주항공 & 방산", "SMR·원자력 에너지"]),
]

def clean_text(text): return str(text) if isinstance(text, str) else str(text)

def read_json(path, default):
    try:
        if not os.path.exists(path): return default
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            return data if data is not None else default
    except Exception: return default

def write_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception: return False

def load_etf_universe():
    universe = dict(BASE_ETFS)
    cached = read_json(UNIVERSE_FILE, {})
    if isinstance(cached, dict):
        for code, name in cached.items():
            code = str(code).strip().zfill(6)
            if code and name:
                universe[code] = clean_text(name.get("name", f"ETF {code}") if isinstance(name, dict) else name)
    return universe

def init_state():
    if "watchlist" not in st.session_state:
        saved = read_json(WATCHLIST_FILE, DEFAULT_WATCHLIST.copy())
        st.session_state.watchlist = [str(x).strip().zfill(6) for x in saved if x] if saved else DEFAULT_WATCHLIST.copy()
    if "holdings" not in st.session_state: st.session_state.holdings = read_json(HOLDINGS_FILE, {})
    if "etf_universe" not in st.session_state: st.session_state.etf_universe = load_etf_universe()
    if "price_cache" not in st.session_state: st.session_state.price_cache = {}
    if "theme_cache" not in st.session_state: st.session_state.theme_cache = {}
    if "selected_code" not in st.session_state: st.session_state.selected_code = st.session_state.watchlist[0] if st.session_state.watchlist else "395160"
    if "main_nav" not in st.session_state: st.session_state.main_nav = "📊 내 ETF"
    if "future_detail_code" not in st.session_state: st.session_state.future_detail_code = None
    if "theme_last_update" not in st.session_state: st.session_state.theme_last_update = None

def get_etf_name(code):
    code = str(code).strip().zfill(6)
    name = BASE_ETFS.get(code) or st.session_state.etf_universe.get(code) or f"ETF {code}"
    return clean_text(name.get("name", f"ETF {code}") if isinstance(name, dict) else name)

def normalize_df(df):
    if df is None or df.empty: return pd.DataFrame()
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [str(col[0]) for col in df.columns]
    rename_map = {}
    for col in df.columns:
        k = str(col).lower()
        if k in ["open", "high", "low", "close", "volume"]: rename_map[col] = k.capitalize()
    df = df.rename(columns=rename_map)
    req = ["Open", "High", "Low", "Close", "Volume"]
    if not all(c in df.columns for c in req): return pd.DataFrame()
    df = df[req].apply(pd.to_numeric, errors="coerce").dropna(subset=["Close"])
    if getattr(df.index, "tz", None) is not None:
        try: df.index = df.index.tz_localize(None)
        except Exception: pass
    return df

def fetch_yahoo(code):
    try:
        df = yf.download(f"{str(code).strip().zfill(6)}.KS", period="2y", interval="1d", auto_adjust=False, progress=False, threads=False)
        return normalize_df(df)
    except Exception: return pd.DataFrame()

def load_price_data(code, force=False):
    code = str(code).strip().zfill(6)
    now = datetime.now()
    cached = st.session_state.price_cache.get(code)
    if cached and not force and (now - cached["time"]).total_seconds() < 300:
        return cached["data"]
    df = fetch_yahoo(code)
    if not df.empty: st.session_state.price_cache[code] = {"time": now, "data": df}
    return df

def calculate_indicators(df):
    if df.empty: return pd.DataFrame()
    d = df.copy()
    d["MA20"], d["MA60"], d["MA120"] = d["Close"].rolling(20).mean(), d["Close"].rolling(60).mean(), d["Close"].rolling(120).mean()
    delta = d["Close"].diff()
    gain, loss = delta.clip(lower=0).rolling(14).mean(), (-delta).clip(upper=0).rolling(14).mean()
    d["RSI14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
    d["VOL20"] = d["Volume"].rolling(20).mean()
    d["VOL_RATIO"] = d["Volume"] / d["VOL20"].replace(0, np.nan)
    d["RET5"], d["RET20"] = d["Close"].pct_change(5) * 100, d["Close"].pct_change(20) * 100
    d["HIGH20"], d["LOW20"] = d["High"].rolling(20).max(), d["Low"].rolling(20).min()
    d["HIGH60"], d["LOW60"] = d["High"].rolling(60).max(), d["Low"].rolling(60).min()
    return d

def safe_float(v, default=0.0):
    try: return default if pd.isna(v) else float(v)
    except Exception: return default

def money(v):
    v = safe_float(v)
    return f"{v:,.0f}원" if abs(v) >= 1000 else f"{v:,.2f}원"

def get_judgment(d):
    if d.empty:
        return {"title": "데이터 부족", "reasons": ["데이터 없음"], "action": "확인 필요", "ma_state": "확인 불가", "rsi_state": "확인 불가", "vol_state": "확인 불가", "rsi": 0, "vol_ratio": 0, "ret20": 0}
    row = d.iloc[-1]
    cur, ma20, ma60 = safe_float(row["Close"]), safe_float(row["MA20"]), safe_float(row["MA60"])
    rsi, vr, ret20 = safe_float(row["RSI14"], 50), safe_float(row["VOL_RATIO"], 1), safe_float(row["RET20"], 0)
    
    above20, above60 = cur >= ma20, cur >= ma60
    ma_state = "20일선 상회" if above20 else "20일선 하회"
    rsi_state = "과열권" if rsi >= 70 else ("강세권" if rsi >= 60 else ("중립권" if rsi >= 45 else ("약세권" if rsi >= 30 else "과매도권")))
    vol_state = "거래량 강한 확대" if vr >= 1.5 else ("거래량 증가" if vr >= 1.1 else ("평균 수준" if vr >= 0.8 else "거래량 감소"))

    if above20 and above60 and rsi >= 70:
        title, action = "상승 추세 · 추격 주의", "신규 매수는 추격보다 눌림 확인을 우선합니다."
    elif above20 and above60:
        title, action = "상승 추세 유지", "보유자는 추세를 확인하고 신규 매수는 눌림을 우선합니다."
    elif above60 and not above20:
        title, action = "단기 조정 · 중기 추세 확인", "20일선 회복 여부를 확인합니다."
    else:
        title, action = "방향 확인 구간", "추세가 명확하지 않습니다."

    reasons = [f"현재가 {money(cur)} · 20일선 {money(ma20)}", f"60일선 {money(ma60)}", f"RSI14 {rsi:.1f} ({rsi_state})", f"거래량 {vr:.2f}배 ({vol_state})"]
    return {"title": title, "reasons": reasons, "action": action, "ma_state": ma_state, "rsi_state": rsi_state, "vol_state": vol_state, "rsi": rsi, "vol_ratio": vr, "ret20": ret20}

def calculate_levels(d):
    if d.empty: return None
    cur = safe_float(d["Close"].iloc[-1])
    return {"first": safe_float(d["MA20"].iloc[-1], cur), "support": min(safe_float(d["MA60"].iloc[-1], cur), safe_float(d["LOW20"].iloc[-1], cur)), "breakout": safe_float(d["HIGH20"].iloc[-1], cur), "risk": min(safe_float(d["MA60"].iloc[-1], cur), safe_float(d["LOW20"].iloc[-1], cur))}

def render_judgment(d):
    j = get_judgment(d)
    st.markdown('<div class="section-title">현재판단 · 지금대응</div>', unsafe_allow_html=True)
    st.html(f"""
        <div class="evidence-grid">
            <div class="evidence-box"><div class="evidence-label">20일선</div><div class="evidence-value">{esc(j["ma_state"])}</div></div>
            <div class="evidence-box"><div class="evidence-label">RSI14</div><div class="evidence-value">{j["rsi"]:.1f}</div></div>
            <div class="evidence-box"><div class="evidence-label">거래량</div><div class="evidence-value">{j["vol_ratio"]:.2f}배</div></div>
        </div>
    """)
    c1, c2 = st.columns(2)
    with c1:
        st.html(f'<div class="judgment-box"><div class="judgment-title">현재판단</div><div class="judgment-main">{esc(j["title"])}</div><div class="judgment-reason">{"<br>".join(esc(x) for x in j["reasons"])}</div></div>')
    with c2:
        st.html(f'<div class="action-box"><div class="action-title">지금대응</div><div class="action-main">{esc(j["action"])}</div></div>')

def render_scenarios(d):
    l = calculate_levels(d)
    if not l: return
    st.markdown("### 핵심가격 · 대응 시나리오")
    cards = [("① 1차 관심", l["first"], "20일선 부근 눌림"), ("② 핵심 지지", l["support"], "중기 추세 방어"), ("③ 돌파 기준", l["breakout"], "최근 20일 고점"), ("④ 위험 가격", l["risk"], "핵심 지지 이탈")]
    cols = st.columns(4)
    for col, (lbl, price, cond) in zip(cols, cards):
        with col:
            with st.container(border=True):
                st.markdown(f"**{lbl}**")
                st.markdown(f"### {money(price)}")
                st.caption(cond)

def render_chart(d):
    if d.empty: return
    df_c = d.tail(126).copy()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.025, row_heights=[0.75, 0.25])
    fig.add_trace(go.Candlestick(x=df_c.index, open=df_c["Open"], high=df_c["High"], low=df_c["Low"], close=df_c["Close"], increasing_line_color="#39c99a", decreasing_line_color="#ef6678", showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=df_c["MA20"], line=dict(color="#4f86b5", width=1.4), name="20일선"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=df_c["MA60"], line=dict(color="#a58c52", width=1.3), name="60일선"), row=1, col=1)
    fig.add_trace(go.Bar(x=df_c.index, y=df_c["Volume"], marker_color=np.where(df_c["Close"] >= df_c["Open"], "#327f69", "#9b4653"), opacity=0.5, showlegend=False), row=2, col=1)
    fig.update_xaxes(fixedrange=True, showgrid=False, rangeslider_visible=False)
    fig.update_yaxes(fixedrange=True, gridcolor="#17283a", row=1, col=1)
    fig.update_yaxes(fixedrange=True, showticklabels=False, showgrid=False, row=2, col=1)
    fig.update_layout(height=390, margin=dict(l=4, r=4, t=18, b=4), paper_bgcolor="#0d1928", plot_bgcolor="#0d1928", font=dict(color="#aab8c7"), legend=dict(orientation="h", y=1.02, x=1, xanchor="right"), dragmode=False, hovermode=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True, "staticPlot": True})

def search_etfs(q):
    q = (q or "").strip().lower()
    if not q: return []
    res = []
    for code, name in st.session_state.etf_universe.items():
        code, name_str = str(code).strip().zfill(6), clean_text(name)
        if q in code.lower() or q in name_str.lower(): res.append({"code": code, "name": name_str})
    return res[:30]

def etf_format_func(x):
    return f"{clean_text(x.get('name', ''))} · {str(x.get('code', '')).zfill(6)}" if isinstance(x, dict) else str(x)

def render_finder():
    st.markdown('<div class="section-title">ETF 찾기</div>', unsafe_allow_html=True)
    q = st.text_input("ETF명 또는 종목코드", placeholder="예: AI반도체 / 395160", label_visibility="collapsed", key="search_q")
    results = search_etfs(q)
    if results:
        sel = st.selectbox("검색 결과", results, format_func=etf_format_func, key="search_result_obj")
        if isinstance(sel, dict):
            code, name = str(sel["code"]).strip().zfill(6), clean_text(sel["name"])
            st.html(f'<div class="holding-box"><div class="holding-value">{esc(name)}</div><div class="holding-detail">종목코드 {esc(code)}</div></div>')
            if st.button("추가", use_container_width=True, key=f"finder_add_{code}"):
                if code not in st.session_state.watchlist:
                    st.session_state.watchlist.append(code)
                    write_json(WATCHLIST_FILE, st.session_state.watchlist)
                st.session_state.selected_code = code
                st.rerun()

def render_watchlist():
    st.markdown('<div class="section-title">관심종목</div>', unsafe_allow_html=True)
    wl = st.session_state.watchlist
    if not wl: return
    items = [{"code": c, "name": get_etf_name(c)} for c in wl]
    cur = st.session_state.selected_code
    sel = st.selectbox("관심종목 선택", items, index=next((i for i, x in enumerate(items) if x["code"] == cur), 0), format_func=etf_format_func, key="watch_select_obj")
    if isinstance(sel, dict): st.session_state.selected_code = str(sel["code"]).strip().zfill(6)
    if st.button("현재 ETF 삭제", use_container_width=True, key="remove_watch"):
        if cur in wl:
            wl.remove(cur)
            write_json(WATCHLIST_FILE, wl)
            st.session_state.selected_code = wl[0] if wl else "395160"
            st.rerun()

def render_holdings(code, current):
    st.markdown('<div class="section-title">보유 상태</div>', unsafe_allow_html=True)
    old = st.session_state.holdings.get(code)
    held = st.radio("보유 여부", ["미보유", "보유중"], index=1 if old else 0, horizontal=True, key=f"held_{code}")
    if held == "보유중":
        c1, c2 = st.columns(2)
        with c1: avg = st.number_input("평균매수가", min_value=0.0, value=float(old.get("avg_price", 0) if old else 0), step=100.0, key=f"avg_{code}")
        with c2: qty = st.number_input("보유수량", min_value=0.0, value=float(old.get("quantity", 0) if old else 0), step=1.0, key=f"qty_{code}")
        if st.button("보유정보 저장", key=f"save_{code}", use_container_width=True):
            st.session_state.holdings[code] = {"avg_price": avg, "quantity": qty}
            write_json(HOLDINGS_FILE, st.session_state.holdings)
            st.rerun()
        if avg > 0:
            pnl = (current / avg - 1) * 100
            st.html(f'<div class="holding-box"><div class="holding-value">보유 {qty:,.0f}주</div><div class="holding-detail">평단가 {money(avg)} · 수익률 <span class="{"positive" if pnl >= 0 else "negative"}">{pnl:+.2f}%</span></div></div>')
    elif old and st.button("보유정보 삭제", key=f"del_{code}", use_container_width=True):
        del st.session_state.holdings[code]
        write_json(HOLDINGS_FILE, st.session_state.holdings)
        st.rerun()

def render_my_etf():
    render_finder()
    render_watchlist()
    code, name = st.session_state.selected_code, get_etf_name(st.session_state.selected_code)
    df = load_price_data(code)
    if df.empty:
        st.error("가격 데이터를 불러오지 못했습니다.")
        return
    d = calculate_indicators(df)
    if d.empty: return
    cur, prev = safe_float(d["Close"].iloc[-1]), safe_float(d["Close"].iloc[-2]) if len(d) >= 2 else safe_float(d["Close"].iloc[-1])
    chg, chg_pct = cur - prev, ((cur - prev) / prev * 100) if prev != 0 else 0
    st.html(f'<div class="hero"><div class="hero-name">{esc(name)}</div><div class="hero-code">{esc(code)}</div><div class="quote-row"><div class="quote-price">{money(cur)}</div><div class="quote-change {"positive" if chg > 0 else "negative"}">{money(chg)} ({chg_pct:+.2f}%)</div></div><div class="hero-date">기준일 {esc(d.index[-1].strftime("%Y-%m-%d"))}</div></div>')
    render_holdings(code, cur)
    render_judgment(d)
    render_scenarios(d)
    st.markdown('<div class="section-title">가격 흐름 · 최근 6개월</div>', unsafe_allow_html=True)
    render_chart(d)

def theme_candidates(theme):
    info, res, used = THEMES[theme], [], set()
    for code in info["seeds"]:
        code = str(code).strip().zfill(6)
        if code not in used: res.append({"code": code, "name": get_etf_name(code)}); used.add(code)
    for code, name in st.session_state.etf_universe.items():
        code, name_str = str(code).strip().zfill(6), clean_text(name)
        if any(k.lower() in f"{code} {name_str}".lower() for k in info["keywords"]) and code not in used:
            res.append({"code": code, "name": name_str}); used.add(code)
    return res[:3]

def theme_snapshot(theme):
    cached = st.session_state.theme_cache.get(theme)
    if cached and (datetime.now() - cached["time"]).total_seconds() < 300: return cached["rows"]
    rows = []
    for item in theme_candidates(theme):
        df = load_price_data(item["code"])
        if df.empty: continue
        d = calculate_indicators(df)
        if d.empty: continue
        row = d.iloc[-1]
        cur = safe_float(row["Close"])
        rows.append({"code": item["code"], "name": item["name"], "price": cur, "rsi": safe_float(row["RSI14"], 50), "vr": safe_float(row["VOL_RATIO"], 1), "ret": safe_float(row["RET20"], 0), "trend": "상승" if cur >= safe_float(row["MA20"], cur) else "조정"})
    st.session_state.theme_cache[theme] = {"time": datetime.now(), "rows": rows}
    return rows

def render_future_theme():
    st.html('<div class="hero"><div class="hero-name">미래테마 대시보드</div><div class="hero-code">현재 주도 섹터부터 다음 수혜 및 초기 관심 기술 분석</div></div>')
    update_time = st.session_state.theme_last_update
    c1, c2 = st.columns([3, 1])
    with c1:
        st.html(f'<div class="future-update-box"><div class="future-update-title">테마 데이터 기준 시각</div><div class="future-update-time">마지막 업데이트 · {esc(update_time.strftime("%Y-%m-%d %H:%M:%S") if update_time else "업데이트 전")}</div></div>')
    with c2:
        if st.button("🔄 전체 갱신", use_container_width=True, key="refresh_future_theme"):
            st.session_state.theme_cache = {}
            st.session_state.theme_last_update = datetime.now()
            st.rerun()

    cur_detail = st.session_state.get("future_detail_code")
    for stage_name, theme_names in FUTURE_CHAIN:
        st.markdown(f"### 📍 [{stage_name}] 핵심 테마군")
        for theme in theme_names:
            info = THEMES[theme]
            st.html(f'<div class="{info["badge_class"]}"><div class="theme-stage" style="color: {info["stage_color"]};">STAGE: {esc(stage_name)}</div><div class="theme-title">{esc(theme)}</div><div class="theme-reason">{esc(info["reason"])}</div></div>')
            rows = theme_snapshot(theme)
            if not rows: continue
            cols = st.columns(len(rows))
            for i, item in enumerate(rows):
                with cols[i]:
                    st.html(f'<div class="theme-etf-box"><div class="theme-etf-name">{esc(item["name"])}</div><div class="theme-etf-code">{esc(item["code"])}</div><div class="theme-data-grid"><div class="theme-data-item"><div class="theme-data-label">현재가</div><div class="theme-data-value">{money(item["price"])}</div></div><div class="theme-data-item"><div class="theme-data-label">RSI</div><div class="theme-data-value">{item["rsi"]:.1f}</div></div><div class="theme-data-item"><div class="theme-data-label">거래량</div><div class="theme-data-value">{item["vr"]:.2f}배</div></div><div class="theme-data-item"><div class="theme-data-label">20일</div><div class="theme-data-value {"positive" if item["ret"] >= 0 else "negative"}">{item["ret"]:+.2f}%</div></div></div></div>')
                    is_active = (cur_detail == item["code"])
                    if st.button("분석 닫기" if is_active else "ETF 분석", key=f"btn_{theme}_{item['code']}", use_container_width=True):
                        st.session_state.future_detail_code = None if is_active else item["code"]
                        st.rerun()
            if cur_detail and any(r["code"] == cur_detail for r in rows):
                matched = next((r for r in rows if r["code"] == cur_detail), None)
                if matched:
                    st.html('<div class="future-analysis-panel">')
                    st.markdown(f"#### 🔍 [{matched['name']} ({matched['code']})] 정밀 분석 패널")
                    if st.button("내 ETF 화면으로 이동", key=f"move_my_{matched['code']}"):
                        st.session_state.selected_code, st.session_state.main_nav, st.session_state.future_detail_code = matched['code'], "📊 내 ETF", None
                        st.rerun()
                    df_d = load_price_data(matched['code'])
                    if not df_d.empty:
                        d_d = calculate_indicators(df_d)
                        if not d_d.empty:
                            render_judgment(d_d)
                            render_scenarios(d_d)
                            st.markdown('<div class="section-title">가격 흐름 · 최근 6개월</div>', unsafe_allow_html=True)
                            render_chart(d_d)
                    st.html('</div>')
        st.write("")

init_state()
st.html('<div class="app-header"><div class="app-title">ETF RADAR</div><div class="app-subtitle">ETF 추세 · 모멘텀 · 거래량 · 핵심가격 · 대응 시나리오</div></div>')

nav = st.radio("메뉴", ["📊 내 ETF", "🚀 미래테마"], horizontal=True, key="main_nav", label_visibility="collapsed")
render_my_etf() if nav == "📊 내 ETF" else render_future_theme()
