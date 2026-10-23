# -*- coding: utf-8 -*-
"""
ETF RADAR — self-contained candidate app
- No app_modules.py dependency.
- US ETF leading signals + Korean ETF theme matching + separate entry-timing assessment.
- Missing data is shown as unavailable; no fabricated default scores.
Run: streamlit run app.py
"""
from __future__ import annotations

import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

try:
    import yfinance as yf
except Exception:
    yf = None

try:
    import requests
except Exception:
    requests = None

try:
    import plotly.express as px
except Exception:
    px = None

APP_TITLE = "ETF RADAR"
MASTER_CSV = "KRX_ETF_MASTER.csv"
CACHE_SECONDS = 900
HISTORY_PERIOD = "1y"

# Explicitly mapped US-listed ETF proxies. Multiple proxies are averaged only when data exists.
THEMES: Dict[str, Dict[str, object]] = {
    "반도체": {"us": ["SMH", "SOXX"], "keywords": ["반도체", "semiconductor", "반도체소부장"]},
    "AI·로봇": {"us": ["BOTZ", "AIQ", "QQQ"], "keywords": ["로봇", "인공지능", "AI", "자율주행", "자동화", "로보틱스"]},
    "전력·원전": {"us": ["GRID", "URA"], "keywords": ["전력", "원자력", "원전", "전력설비", "전력기기", "우라늄"]},
    "신재생에너지": {"us": ["ICLN", "TAN"], "keywords": ["신재생", "태양광", "풍력", "클린에너지", "친환경에너지"]},
    "바이오·헬스케어": {"us": ["IBB", "XBI", "XLV"], "keywords": ["바이오", "헬스케어", "제약", "의료기기", "헬스"]},
    "방산·우주": {"us": ["ITA", "ARKX"], "keywords": ["방산", "우주항공", "항공우주", "국방"]},
    "조선·운송": {"us": ["BOAT", "IYT"], "keywords": ["조선", "해운", "운송", "선박"]},
    "2차전지": {"us": ["LIT", "BATT"], "keywords": ["2차전지", "배터리", "리튬", "양극재", "음극재", "전기차배터리"]},
    "에너지": {"us": ["XLE", "OIH"], "keywords": ["에너지", "원유", "석유", "가스", "정유"]},
    "미국 대형주": {"us": ["SPY", "QQQ"], "keywords": ["S&P500", "나스닥100", "미국대표", "미국S&P", "미국나스닥"]},
}
US_BENCHMARK = "SPY"
ETF_MASTER_COLUMNS = ["code", "name", "theme"]


def norm_code(value) -> str:
    s = re.sub(r"\D", "", str(value or ""))
    return s[-6:].zfill(6) if s else ""


def safe_float(value) -> Optional[float]:
    try:
        x = float(value)
        return x if np.isfinite(x) else None
    except Exception:
        return None


def get_close_frame(ticker: str, period: str = HISTORY_PERIOD) -> pd.DataFrame:
    """Fetch daily close prices. Empty frame means unavailable, never a synthetic series."""
    if yf is None:
        return pd.DataFrame()
    try:
        raw = yf.download(ticker, period=period, interval="1d", auto_adjust=True,
                          progress=False, threads=False, timeout=15)
        if raw is None or raw.empty:
            return pd.DataFrame()
        if isinstance(raw.columns, pd.MultiIndex):
            if ("Close", ticker) in raw.columns:
                close = raw[("Close", ticker)]
            elif "Close" in raw.columns.get_level_values(0):
                close = raw.xs("Close", axis=1, level=0).iloc[:, 0]
            else:
                return pd.DataFrame()
        elif "Close" in raw.columns:
            close = raw["Close"]
        else:
            return pd.DataFrame()
        out = pd.DataFrame({"Close": pd.to_numeric(close, errors="coerce")}).dropna()
        out = out[out["Close"] > 0]
        out.index = pd.to_datetime(out.index)
        return out[~out.index.duplicated(keep="last")].sort_index()
    except Exception:
        return pd.DataFrame()


def indicators(prices: pd.DataFrame) -> dict:
    if prices is None or prices.empty or "Close" not in prices:
        return {"available": False}
    c = pd.to_numeric(prices["Close"], errors="coerce").dropna()
    if len(c) < 25:
        return {"available": False, "reason": "유효한 일별 가격이 25개 미만입니다."}
    last = float(c.iloc[-1])
    ma20 = float(c.rolling(20).mean().iloc[-1])
    ma60 = float(c.rolling(60).mean().iloc[-1]) if len(c) >= 60 else np.nan
    ret5 = (last / float(c.iloc[-6]) - 1) * 100 if len(c) >= 6 else np.nan
    ret20 = (last / float(c.iloc[-21]) - 1) * 100 if len(c) >= 21 else np.nan
    ret60 = (last / float(c.iloc[-61]) - 1) * 100 if len(c) >= 61 else np.nan
    high20 = float(c.iloc[-21:].max())
    low20 = float(c.iloc[-21:].min())
    delta = c.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = float((100 - (100 / (1 + rs))).iloc[-1]) if pd.notna((100 - (100 / (1 + rs))).iloc[-1]) else np.nan
    volume_ratio = np.nan
    # yfinance price fetch is intentionally Close-only; volume confirmation is not fabricated.
    return {
        "available": True, "price": last, "date": c.index[-1].strftime("%Y-%m-%d"),
        "ma20": ma20, "ma60": ma60, "ret5": ret5, "ret20": ret20, "ret60": ret60,
        "high20": high20, "low20": low20, "rsi": rsi, "volume_ratio": volume_ratio,
        "dist20": (last / ma20 - 1) * 100 if ma20 else np.nan,
        "above_ma20": bool(last >= ma20) if np.isfinite(ma20) else False,
        "above_ma60": bool(last >= ma60) if np.isfinite(ma60) else False,
    }


def fetch_us_snapshot() -> Tuple[pd.DataFrame, dict]:
    tickers = sorted({t for info in THEMES.values() for t in info["us"]} | {US_BENCHMARK})
    rows, data = [], {}
    for ticker in tickers:
        frame = get_close_frame(ticker)
        m = indicators(frame)
        data[ticker] = frame
        if m.get("available"):
            rows.append({"ticker": ticker, **m})
    snap = pd.DataFrame(rows)
    bench = next((r for r in rows if r["ticker"] == US_BENCHMARK), None)
    if bench:
        for row in rows:
            row["rs20_vs_spy"] = row.get("ret20", np.nan) - bench.get("ret20", np.nan)
            r60 = row.get("ret60", np.nan)
            b60 = bench.get("ret60", np.nan)
            row["rs60_vs_spy"] = r60 - b60 if pd.notna(r60) and pd.notna(b60) else np.nan
            row["acceleration"] = row.get("ret20", np.nan) - (r60 / 3 if pd.notna(r60) else np.nan)
    snap = pd.DataFrame(rows)
    return snap, data


def infer_theme(name: str) -> Optional[str]:
    text = str(name).lower().replace(" ", "")
    # More specific themes first to reduce broad-word collisions.
    priority = ["반도체", "2차전지", "전력·원전", "방산·우주", "바이오·헬스케어",
                "신재생에너지", "조선·운송", "에너지", "AI·로봇", "미국 대형주"]
    for theme in priority:
        for kw in THEMES[theme]["keywords"]:
            k = str(kw).lower().replace(" ", "")
            if k and k in text:
                return theme
    return None


def load_master() -> Tuple[pd.DataFrame, str]:
    """Prefer the user's KRX master CSV; otherwise try Naver's ETF list endpoint."""
    candidates = []
    try:
        local = pd.read_csv(MASTER_CSV, dtype=str, encoding="utf-8-sig")
        candidates.append(("local", local))
    except Exception:
        try:
            local = pd.read_csv(MASTER_CSV, dtype=str, encoding="cp949")
            candidates.append(("local", local))
        except Exception:
            pass
    if candidates:
        source, raw = candidates[0]
        colmap = {str(c).strip().lower(): c for c in raw.columns}
        code_col = next((colmap[k] for k in ["code", "단축코드", "종목코드", "ticker"] if k in colmap), None)
        name_col = next((colmap[k] for k in ["name", "한글종목명", "종목명", "etf명"] if k in colmap), None)
        if code_col and name_col:
            df = pd.DataFrame({"code": raw[code_col].map(norm_code), "name": raw[name_col].astype(str)})
            df = df[(df["code"].str.len() == 6) & (df["name"].str.len() > 1)]
            df = df.drop_duplicates("code")
            df["theme"] = df["name"].map(infer_theme)
            return df.reset_index(drop=True), "KRX_ETF_MASTER.csv"
    if requests is not None:
        urls = [
            "https://finance.naver.com/api/sise/etfItemList.nhn",
            "https://finance.naver.com/api/sise/etfItemList.nhn?targetColumn=market_sum"
        ]
        for url in urls:
            try:
                r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
                payload = r.json()
                items = payload.get("result", {}).get("etfItemList", [])
                if items:
                    df = pd.DataFrame([{
                        "code": norm_code(x.get("itemcode", "")),
                        "name": str(x.get("itemname", "")).strip()
                    } for x in items])
                    df = df[(df["code"].str.len() == 6) & (df["name"].str.len() > 1)].drop_duplicates("code")
                    df["theme"] = df["name"].map(infer_theme)
                    return df.reset_index(drop=True), "Naver ETF list"
            except Exception:
                continue
    return pd.DataFrame(columns=ETF_MASTER_COLUMNS), "자료 없음"


def theme_signal(theme: str, snap: pd.DataFrame) -> dict:
    proxies = THEMES[theme]["us"]
    if snap.empty:
        return {"available": False, "theme": theme, "reason": "미국 ETF 가격 데이터를 가져오지 못했습니다."}
    sub = snap[snap["ticker"].isin(proxies)]
    if sub.empty:
        return {"available": False, "theme": theme, "reason": "해당 테마의 미국 ETF 데이터가 없습니다."}
    # Each proxy contributes only if the relevant measure is present.
    r20 = pd.to_numeric(sub["ret20"], errors="coerce").dropna()
    rs20 = pd.to_numeric(sub.get("rs20_vs_spy", pd.Series(dtype=float)), errors="coerce").dropna()
    r60 = pd.to_numeric(sub["ret60"], errors="coerce").dropna()
    accel = pd.to_numeric(sub.get("acceleration", pd.Series(dtype=float)), errors="coerce").dropna()
    if r20.empty:
        return {"available": False, "theme": theme, "reason": "20거래일 수익률이 없어 신호를 계산할 수 없습니다."}
    avg20 = float(r20.mean())
    avg_rs20 = float(rs20.mean()) if not rs20.empty else np.nan
    avg60 = float(r60.mean()) if not r60.empty else np.nan
    avg_accel = float(accel.mean()) if not accel.empty else np.nan
    # Bounded, transparent components; no neutral score when data is absent.
    score = 50 + np.clip(avg20 * 1.2, -20, 20)
    if np.isfinite(avg_rs20):
        score += np.clip(avg_rs20 * 0.8, -15, 15)
    if np.isfinite(avg_accel):
        score += np.clip(avg_accel * 0.5, -10, 10)
    score = float(np.clip(score, 0, 100))
    if avg20 > 2 and (not np.isfinite(avg_rs20) or avg_rs20 > 0):
        state = "선행 강세"
    elif avg20 < -2 and (not np.isfinite(avg_rs20) or avg_rs20 < 0):
        state = "선행 약세"
    else:
        state = "방향 탐색"
    return {
        "available": True, "theme": theme, "score": score, "state": state,
        "proxy": ", ".join(sub["ticker"].tolist()), "ret20": avg20, "ret60": avg60,
        "rs20": avg_rs20, "acceleration": avg_accel,
        "latest": str(sub["date"].max())
    }


def entry_assessment(m: dict) -> dict:
    if not m.get("available"):
        return {"state": "판단 불가", "score": np.nan, "reason": m.get("reason", "가격 데이터 부족")}
    p, ma20, ma60, dist, rsi = m["price"], m["ma20"], m["ma60"], m["dist20"], m["rsi"]
    if not np.isfinite(dist):
        return {"state": "판단 불가", "score": np.nan, "reason": "이동평균 데이터 부족"}
    if dist > 8 or (np.isfinite(rsi) and rsi >= 78):
        return {"state": "추격 금지", "score": 20, "reason": "단기 이격 또는 RSI 과열"}
    if p < ma20:
        return {"state": "눌림목 대기", "score": 35, "reason": "현재가가 20일 이동평균 아래"}
    if np.isfinite(ma60) and p < ma60:
        return {"state": "관찰", "score": 45, "reason": "60일 추세가 아직 약함"}
    if dist >= 3.5:
        return {"state": "눌림목 대기", "score": 55, "reason": "20일선과 이격이 커져 조정 확인 필요"}
    if np.isfinite(rsi) and rsi < 40:
        return {"state": "관찰", "score": 45, "reason": "RSI 약세"}
    return {"state": "매수 고려", "score": 75, "reason": "20일선 부근이며 단기 과열 신호가 제한적"}


def build_recommendations(master: pd.DataFrame, snap: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    signals = []
    for theme in THEMES:
        s = theme_signal(theme, snap)
        signals.append(s)
    sig_df = pd.DataFrame(signals)
    recs = []
    if master.empty:
        return sig_df, pd.DataFrame()
    matched = master[master["theme"].notna()].copy()
    # Limit per-theme price requests by liquidity/order in the source master; do not claim ranking is by liquidity.
    for _, row in matched.iterrows():
        code, name, theme = row["code"], row["name"], row["theme"]
        # Yahoo Finance Korean ETF suffix is commonly .KS; try .KQ only if .KS fails.
        frame = get_close_frame(f"{code}.KS")
        if frame.empty:
            frame = get_close_frame(f"{code}.KQ")
        m = indicators(frame)
        ts = next((x for x in signals if x.get("theme") == theme), {})
        ent = entry_assessment(m)
        if not ts.get("available"):
            overall = np.nan
            recommendation = "신호 데이터 부족"
        elif not m.get("available"):
            overall = np.nan
            recommendation = "국내 가격 데이터 부족"
        else:
            overall = 0.65 * ts["score"] + 0.35 * ent["score"]
            if ts["score"] < 40:
                recommendation = "테마 약세 — 관망"
            elif ent["state"] == "매수 고려" and ts["score"] >= 55:
                recommendation = "매수 고려"
            elif ent["state"] == "추격 금지":
                recommendation = "추격 금지"
            elif ent["state"] == "눌림목 대기":
                recommendation = "눌림목 대기"
            else:
                recommendation = "관찰"
        recs.append({
            "종목코드": code, "국내 ETF": name, "테마": theme,
            "테마점수": round(ts["score"], 1) if ts.get("available") else np.nan,
            "미국20일(%)": round(ts["ret20"], 2) if ts.get("available") else np.nan,
            "미국60일(%)": round(ts["ret60"], 2) if ts.get("available") and np.isfinite(ts.get("ret60", np.nan)) else np.nan,
            "미국 SPY대비(%)": round(ts["rs20"], 2) if ts.get("available") and np.isfinite(ts.get("rs20", np.nan)) else np.nan,
            "현재가": round(m["price"], 2) if m.get("available") else np.nan,
            "20일선 이격(%)": round(m["dist20"], 2) if m.get("available") else np.nan,
            "RSI14": round(m["rsi"], 1) if m.get("available") and np.isfinite(m.get("rsi", np.nan)) else np.nan,
            "진입상태": ent["state"], "종합점수": round(overall, 1) if np.isfinite(overall) else np.nan,
            "추천판정": recommendation, "판정근거": ent.get("reason", ""),
            "가격기준일": m.get("date", "")
        })
    df = pd.DataFrame(recs)
    if not df.empty:
        df = df.sort_values(["종합점수", "테마점수"], ascending=False, na_position="last")
    return sig_df, df


def render():
    st.set_page_config(page_title=APP_TITLE, page_icon="📡", layout="wide")
    st.title("📡 ETF RADAR")
    st.caption("미국장 선행 신호 → 국내 ETF 연결 → 진입 시점 판단 | 데이터가 없으면 점수를 만들지 않습니다.")

    with st.sidebar:
        st.subheader("데이터 설정")
        st.write("가격 데이터: Yahoo Finance")
        st.write(f"갱신 주기: {CACHE_SECONDS // 60}분 권장")
        force_refresh = st.button("데이터 새로고침")
        st.markdown("---")
        st.write("국내 ETF 마스터")
        st.write(f"`{MASTER_CSV}` 파일이 있으면 우선 사용합니다.")

    if force_refresh:
        st.cache_data.clear()

    @st.cache_data(ttl=CACHE_SECONDS, show_spinner=False)
    def cached_master():
        return load_master()

    @st.cache_data(ttl=CACHE_SECONDS, show_spinner=False)
    def cached_us():
        return fetch_us_snapshot()

    with st.spinner("국내 ETF 목록과 미국 선행 신호를 불러오는 중입니다..."):
        master, master_source = cached_master()
        snap, _ = cached_us()

    if yf is None:
        st.error("yfinance 패키지가 설치되지 않았습니다. `pip install yfinance` 후 다시 실행하세요.")
        st.stop()

    tabs = st.tabs(["🎯 추천 ETF", "🌎 미국 선행 신호", "🧭 테마 레이더", "ℹ️ 데이터·판정 기준"])
    with tabs[0]:
        st.subheader("국내 ETF 추천 후보")
        st.caption(f"국내 ETF 목록 출처: {master_source} · 미국 데이터 기준일은 테마별로 다를 수 있습니다.")
        if master.empty:
            st.warning("국내 ETF 마스터를 불러오지 못했습니다. `KRX_ETF_MASTER.csv`를 app.py와 같은 폴더에 넣어 주세요. 데이터가 없어서 국내 ETF 추천을 만들지 않았습니다.")
        else:
            st.write(f"전체 ETF {len(master):,}개 · 테마 연결 후보 {int(master['theme'].notna().sum()):,}개")
            if st.button("추천 후보 계산", type="primary"):
                st.session_state["etf_radar_recs"] = None
                st.cache_data.clear()
            if "etf_radar_recs" not in st.session_state or st.session_state["etf_radar_recs"] is None:
                with st.spinner("테마 신호와 국내 ETF 가격을 계산합니다. ETF 수에 따라 시간이 걸릴 수 있습니다..."):
                    sig_df, rec_df = build_recommendations(master, snap)
                st.session_state["etf_radar_recs"] = (sig_df, rec_df)
            sig_df, rec_df = st.session_state["etf_radar_recs"]
            if rec_df.empty:
                st.info("테마 키워드에 연결된 ETF가 없습니다. 마스터 파일의 종목명 형식을 확인하세요.")
            else:
                state_filter = st.multiselect("판정 필터", sorted(rec_df["추천판정"].dropna().unique()), default=[])
                view = rec_df[rec_df["추천판정"].isin(state_filter)] if state_filter else rec_df
                st.dataframe(view, use_container_width=True, hide_index=True)
                csv = view.to_csv(index=False).encode("utf-8-sig")
                st.download_button("추천 결과 CSV 다운로드", csv, "ETF_RADAR_RECOMMENDATIONS.csv", "text/csv")
    with tabs[1]:
        st.subheader("미국 ETF 선행 신호")
        if snap.empty:
            st.warning("미국 ETF 가격 데이터를 가져오지 못했습니다. 네트워크 또는 Yahoo Finance 응답을 확인하세요.")
        else:
            cols = ["ticker", "price", "ret5", "ret20", "ret60", "rs20_vs_spy", "rs60_vs_spy", "acceleration", "date"]
            cols = [c for c in cols if c in snap.columns]
            display = snap[cols].copy()
            display = display.rename(columns={
                "ticker": "미국 ETF", "price": "현재가", "ret5": "5일(%)", "ret20": "20일(%)",
                "ret60": "60일(%)", "rs20_vs_spy": "SPY 대비 20일(%)", "rs60_vs_spy": "SPY 대비 60일(%)",
                "acceleration": "모멘텀 가속(%)", "date": "기준일"
            })
            st.dataframe(display.sort_values("SPY 대비 20일(%)", ascending=False, na_position="last"), use_container_width=True, hide_index=True)
    with tabs[2]:
        st.subheader("테마별 미국 선행 신호")
        sig_df = pd.DataFrame([theme_signal(t, snap) for t in THEMES])
        if sig_df.empty:
            st.warning("테마 신호를 계산할 수 없습니다.")
        else:
            for _, row in sig_df.iterrows():
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
                    c1.markdown(f"**{row['theme']}**")
                    if row.get("available"):
                        c2.metric("테마점수", f"{row['score']:.1f}")
                        c3.metric("20일 수익률", f"{row['ret20']:.2f}%")
                        c4.write(f"상태: **{row['state']}** · 미국 프록시: {row['proxy']}")
                    else:
                        c2.write("점수 없음")
                        c3.write("데이터 없음")
                        c4.write(row.get("reason", "계산 불가"))
    with tabs[3]:
        st.subheader("데이터와 판정 기준")
        st.markdown("""
**중요한 한계와 원칙**
- 미국 ETF 가격은 Yahoo Finance에서 조회합니다. 데이터 제공 여부와 지연은 외부 서비스에 달려 있습니다.
- 국내 ETF 마스터는 `KRX_ETF_MASTER.csv`를 우선 사용하고, 파일이 없으면 Naver ETF 목록 API를 시도합니다.
- 테마 연결은 ETF 종목명 키워드 기반의 1차 분류입니다. 복수 테마·합성·환헤지·레버리지/인버스 상품은 별도 검토가 필요합니다.
- 테마 매력도와 진입 타이밍은 별도 계산합니다. 테마가 강해도 국내 ETF의 진입 상태가 나쁘면 매수 추천으로 표시하지 않습니다.
- 가격 데이터가 부족하면 점수를 만들지 않고 `데이터 부족`으로 표시합니다.
- 이 도구는 투자 참고용이며 수익을 보장하지 않습니다.
""")
        st.markdown("**진입 판정 규칙**")
        st.write("추격 금지: 20일선 대비 +8% 초과 이격 또는 RSI14 ≥ 78")
        st.write("눌림목 대기: 20일선 아래 또는 20일선 대비 +3.5% 이상 이격")
        st.write("매수 고려: 20일선 부근, 추세 조건과 과열 조건을 통과")
        st.write("관찰: 추세/모멘텀이 불충분하거나 추가 확인이 필요")

    st.caption(f"마지막 화면 갱신: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · 앱 후보 버전 — 실제 시세 연결은 실행 환경에서 확인 필요")


if __name__ == "__main__":
    render()
