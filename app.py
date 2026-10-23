"""
ETF RADAR — reconstructed standalone app (safe draft)
IMPORTANT: This is a new reconstruction because the supplied repository ZIP contained
only requirements.txt. It is NOT a replacement verified against the original app.py.
Run with: streamlit run app.py
"""
from __future__ import annotations

import io
import re
from datetime import date, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

try:
    import yfinance as yf
except Exception:
    yf = None

st.set_page_config(page_title="ETF RADAR", page_icon="📡", layout="wide")
st.title("ETF RADAR")
st.caption("데이터 기반 ETF 탐색 · 재구성 초안 — 원본 운영 앱과 대조 검증 전에는 운영본을 덮어쓰지 마세요.")

st.warning(
    "이 앱은 제공된 ZIP에 원본 app.py가 없어 별도로 재구성한 초안입니다. "
    "기존 화면·기능과 동등하다고 검증된 버전이 아닙니다."
)

def find_col(df: pd.DataFrame, names: list[str]) -> Optional[str]:
    normalized = {re.sub(r"[\s_\-]", "", str(c)).lower(): c for c in df.columns}
    for name in names:
        key = re.sub(r"[\s_\-]", "", name).lower()
        if key in normalized:
            return normalized[key]
    return None

def normalize_code(value) -> str:
    s = str(value).strip()
    if s.endswith(".0"):
        s = s[:-2]
    digits = re.sub(r"\D", "", s)
    return digits.zfill(6) if digits and len(digits) <= 6 else s

def classify_group(name: str, code: str = "", theme: str = "") -> str:
    text = f"{name} {theme}".lower()
    # Keep broad overseas benchmark funds separate from domestic industry themes.
    if any(k in text for k in ["나스닥100", "nasdaq 100", "nasdaq100", "s&p500", "s&p 500", "sp500", "미국s&p", "미국 나스닥"]):
        return "해외 대표 지수"
    # Exclusions are applied only to the upside-target recommendation universe.
    if any(k in text for k in ["인버스", "곱버스", "숏", "베어", "inverse", "bear", "short"]):
        return "상승목표 제외"
    if any(k in text for k in ["원유", "금선물", "은선물", "구리", "천연가스", "원자재", "gold", "crude oil", "commodity"]):
        return "상승목표 제외"
    return "국내 산업·테마"

def load_price_upload(upload) -> pd.DataFrame:
    raw = pd.read_csv(upload)
    date_col = find_col(raw, ["date", "날짜", "기준일", "trading_date"])
    code_col = find_col(raw, ["code", "ticker", "종목코드", "단축코드", "isu_cd"])
    close_col = find_col(raw, ["close", "종가", "adj close", "adj_close", "수정종가"])
    if not date_col or not code_col or not close_col:
        raise ValueError("가격 CSV에 날짜/종목코드/종가 열이 필요합니다.")
    raw = raw.rename(columns={date_col:"date", code_col:"code", close_col:"close"})
    raw["date"] = pd.to_datetime(raw["date"], errors="coerce")
    raw["code"] = raw["code"].map(normalize_code)
    raw["close"] = pd.to_numeric(raw["close"], errors="coerce")
    raw = raw.dropna(subset=["date","code","close"])
    raw = raw[raw["close"] > 0].sort_values(["code","date"])
    return raw[["date","code","close"]]

def fetch_yahoo(code: str, period: str) -> pd.DataFrame:
    if yf is None:
        return pd.DataFrame()
    ticker = f"{code}.KS"
    try:
        data = yf.download(ticker, period=period, auto_adjust=True, progress=False, threads=False)
        if data is None or data.empty:
            return pd.DataFrame()
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        close_col = "Close" if "Close" in data.columns else None
        if close_col is None:
            return pd.DataFrame()
        result = data[[close_col]].reset_index()
        result.columns = ["date", "close"]
        result["code"] = code
        result["date"] = pd.to_datetime(result["date"], errors="coerce")
        result["close"] = pd.to_numeric(result["close"], errors="coerce")
        return result.dropna(subset=["date","close"])
    except Exception:
        return pd.DataFrame()

def score_one(g: pd.DataFrame) -> dict:
    g = g.sort_values("date").dropna(subset=["close"])
    close = g["close"].astype(float)
    result = {"observations": int(len(g)), "last_date": g["date"].max() if len(g) else pd.NaT,
              "last_close": float(close.iloc[-1]) if len(g) else np.nan,
              "return_20d": np.nan, "return_60d": np.nan, "momentum_score": np.nan}
    # Require sufficient history rather than filling candidates artificially.
    if len(close) < 61:
        result["status"] = "가격 이력 부족(최소 61개 관측치 필요)"
        return result
    r20 = close.iloc[-1] / close.iloc[-21] - 1
    r60 = close.iloc[-1] / close.iloc[-61] - 1
    result.update(return_20d=float(r20), return_60d=float(r60),
                  momentum_score=float(0.4*r20 + 0.6*r60), status="평가 가능")
    return result

with st.sidebar:
    st.header("입력 데이터")
    master_file = st.file_uploader("ETF 기준목록 CSV", type=["csv"])
    prices_file = st.file_uploader("가격 이력 CSV (선택)", type=["csv"])
    period = st.selectbox("Yahoo Finance 조회 기간", ["6mo", "1y", "2y", "5y"], index=1)
    min_obs = st.number_input("최소 가격 관측치", min_value=20, max_value=500, value=61, step=1)
    refresh = st.button("가격 조회 및 추천 계산", type="primary")

if master_file is None:
    st.info("먼저 ETF 기준목록 CSV를 업로드하세요. 종목코드와 종목명 열이 필요합니다. 데이터가 없으면 임의의 ETF 목록을 만들지 않습니다.")
    st.stop()

try:
    master = pd.read_csv(master_file, dtype=str)
except Exception as exc:
    st.error(f"기준목록 CSV 읽기 실패: {exc}")
    st.stop()

code_col = find_col(master, ["code", "ticker", "종목코드", "단축코드", "isu_cd", "isu cd"])
name_col = find_col(master, ["name", "종목명", "한글종목명", "etf명", "상품명"])
theme_col = find_col(master, ["theme", "테마", "업종", "분류", "기초지수명"])
if not code_col or not name_col:
    st.error("기준목록에서 종목코드 및 종목명 열을 찾지 못했습니다. 원본 열 이름을 확인하세요.")
    st.write("발견한 열:", list(master.columns))
    st.stop()

universe = master.copy()
universe["code"] = universe[code_col].map(normalize_code)
universe["name"] = universe[name_col].fillna("").astype(str).str.strip()
universe["theme"] = universe[theme_col].fillna("").astype(str) if theme_col else ""
universe = universe[(universe["code"] != "") & (universe["name"] != "")]
universe = universe.drop_duplicates("code", keep="first")
universe["group"] = [classify_group(n,c,t) for n,c,t in zip(universe["name"], universe["code"], universe["theme"])]

st.subheader("유니버스 현황")
c1,c2,c3 = st.columns(3)
c1.metric("기준목록 ETF/상품 수", f"{len(universe):,}")
c2.metric("국내 산업·테마", f"{(universe['group']=='국내 산업·테마').sum():,}")
c3.metric("해외 대표 지수", f"{(universe['group']=='해외 대표 지수').sum():,}")

if prices_file is not None:
    try:
        prices = load_price_upload(prices_file)
        price_source = "업로드한 가격 CSV"
    except Exception as exc:
        st.error(f"가격 CSV 오류: {exc}")
        st.stop()
else:
    prices = pd.DataFrame(columns=["date","code","close"])
    price_source = "가격 데이터 미수집"

if refresh and prices_file is None:
    if yf is None:
        st.error("yfinance를 사용할 수 없습니다. requirements.txt 설치 상태를 확인하세요.")
    else:
        bar = st.progress(0.0, text="가격 데이터 수집 중")
        chunks = []
        codes = universe["code"].tolist()
        for i, code in enumerate(codes):
            got = fetch_yahoo(code, period)
            if not got.empty:
                chunks.append(got)
            bar.progress((i+1)/max(len(codes),1), text=f"가격 데이터 조회 {i+1}/{len(codes)}")
        prices = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame(columns=["date","code","close"])
        price_source = "Yahoo Finance 조회"
        st.session_state["radar_prices"] = prices
        st.session_state["radar_price_source"] = price_source

if "radar_prices" in st.session_state and prices_file is None:
    prices = st.session_state["radar_prices"]
    price_source = st.session_state.get("radar_price_source", price_source)

if prices.empty:
    st.warning("가격 데이터가 없습니다. 가격 CSV를 업로드하거나 '가격 조회 및 추천 계산'을 누르세요.")
    st.stop()

prices["code"] = prices["code"].map(normalize_code)
prices = prices[prices["code"].isin(set(universe["code"]))]
counts = prices.groupby("code")["close"].count()
score_rows = []
for code, grp in prices.groupby("code"):
    score_rows.append({"code":code, **score_one(grp)})
scores = pd.DataFrame(score_rows)
result = universe.merge(scores, on="code", how="left")
result["observations"] = result["observations"].fillna(0).astype(int)
result["status"] = result["status"].fillna("가격 데이터 없음")
result.loc[result["observations"] < int(min_obs), "status"] = "가격 이력 부족"
result["eligible"] = result["group"].ne("상승목표 제외") & result["momentum_score"].notna() & result["observations"].ge(int(min_obs))
result["score_pct"] = result["momentum_score"] * 100

st.subheader("데이터 품질 진단")
d1,d2,d3,d4 = st.columns(4)
d1.metric("가격 데이터 종목 수", f"{prices['code'].nunique():,}")
d2.metric("가격 행 수", f"{len(prices):,}")
d3.metric("평가 가능 종목", f"{result['momentum_score'].notna().sum():,}")
d4.metric("추천 가능 후보", f"{result['eligible'].sum():,}")
st.caption(f"가격 출처: {price_source}. 20일·60일 수익률은 수정종가 기반이며, 61개 관측치 미만은 점수 계산에서 제외합니다.")

if result["eligible"].sum() == 0:
    st.error("최종 후보 0개: 임의로 종목을 채우지 않습니다. 아래 상태별 집계로 탈락 원인을 확인하세요.")
    st.dataframe(result["status"].value_counts().rename_axis("상태").reset_index(name="종목 수"), use_container_width=True)

tab1,tab2,tab3 = st.tabs(["최종 후보","해외 대표 지수","전체 진단"])
with tab1:
    rec = result[result["eligible"] & result["group"].eq("국내 산업·테마")].sort_values("momentum_score", ascending=False)
    st.dataframe(rec[["code","name","theme","last_date","last_close","return_20d","return_60d","score_pct","observations","status"]].head(100), use_container_width=True)
    if rec.empty:
        st.info("국내 산업·테마 후보가 없습니다. 가격 이력 부족과 상태별 탈락 사유를 확인하세요.")
with tab2:
    idx = result[result["group"].eq("해외 대표 지수")].sort_values("momentum_score", ascending=False)
    st.dataframe(idx[["code","name","last_date","last_close","return_20d","return_60d","score_pct","observations","status"]], use_container_width=True)
    st.caption("해외 대표 지수는 국내 산업·테마와 별도 그룹으로 표시하며, 상승목표 제외 그룹과 혼동하지 않습니다.")
with tab3:
    st.dataframe(result.sort_values(["group","momentum_score"], ascending=[True,False]), use_container_width=True)
    st.download_button("진단 결과 CSV 다운로드", result.to_csv(index=False).encode("utf-8-sig"),
                       file_name="ETF_RADAR_DIAGNOSTICS.csv", mime="text/csv")
    st.download_button("사용한 가격 데이터 CSV 다운로드", prices.to_csv(index=False).encode("utf-8-sig"),
                       file_name="ETF_RADAR_PRICE_HISTORY.csv", mime="text/csv")
