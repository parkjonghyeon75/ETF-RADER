# -*- coding: utf-8 -*-
"""
ETF RADAR STRATEGY BACKTEST

목적
- 현재 ETF RADAR의 핵심 아이디어를 과거 시점으로 되돌려 검증한다.
- A: 단순 보유
- B: 선행점수
- C: 미래테마 + 선행 ETF
- D: 미래테마 + 선행 ETF + 가격구간

주의
- 이 앱은 연구용 백테스트입니다.
- 실제 주문 체결, 세금, 배당, 환전비용 등은 완전히 반영하지 않습니다.
- 신호일 종가가 아니라 다음 거래일 종가 진입으로 계산하여 look-ahead를 줄입니다.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date

st.set_page_config(page_title="ETF RADAR STRATEGY TEST", page_icon="🧪", layout="wide")

# ============================================================
# 1. 테스트 유니버스
# ============================================================
POOL = {
    "QQQ": "나스닥100",
    "XLK": "미국기술",
    "SMH": "반도체",
    "SOXX": "반도체",
    "BOTZ": "로봇AI",
    "ARKQ": "자동화로봇",
    "HACK": "사이버보안",
    "ITA": "방산",
    "PAVE": "인프라",
    "URA": "원전우라늄",
    "LIT": "2차전지",
    "XBI": "바이오",
    "INDA": "인도",
    "EWY": "한국",
    "EWJ": "일본",
    "EEM": "신흥국",
    "GLD": "금",
    "TLT": "미국장기채",
}
BENCH = "SPY"

# 실제 테마 계산을 위해 2개 이상 ETF가 있는 테마를 중심으로 사용
THEME_GROUPS = {
    "미국기술": ["QQQ", "XLK"],
    "반도체": ["SMH", "SOXX"],
    "로봇AI": ["BOTZ", "ARKQ"],
    "위험선호": ["QQQ", "XLK", "SMH", "SOXX", "BOTZ", "ARKQ"],
    "방어자산": ["GLD", "TLT"],
    "글로벌": ["INDA", "EWY", "EWJ", "EEM"],
}

# ============================================================
# 2. 데이터
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def download_prices(tickers, start, end):
    symbols = list(dict.fromkeys(list(tickers) + [BENCH]))
    x = yf.download(
        symbols,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        threads=True,
        group_by="ticker",
    )
    out = {}
    for t in symbols:
        try:
            if len(symbols) == 1:
                d = x.copy()
            else:
                d = x[t].copy()
            if not d.empty:
                d.columns = [str(c) for c in d.columns]
                out[t] = d
        except Exception:
            continue
    return out


def indicators(d):
    d = d.copy()
    if "Close" not in d.columns:
        return pd.DataFrame()
    d["Close"] = pd.to_numeric(d["Close"], errors="coerce")
    d["Volume"] = pd.to_numeric(d.get("Volume", np.nan), errors="coerce")
    d = d.dropna(subset=["Close"])

    d["MA20"] = d["Close"].rolling(20).mean()
    d["MA60"] = d["Close"].rolling(60).mean()
    d["MA120"] = d["Close"].rolling(120).mean()
    d["MA200"] = d["Close"].rolling(200).mean()
    d["R5"] = d["Close"].pct_change(5) * 100
    d["R20"] = d["Close"].pct_change(20) * 100
    d["R60"] = d["Close"].pct_change(60) * 100
    d["R120"] = d["Close"].pct_change(120) * 100
    d["R252"] = d["Close"].pct_change(252) * 100
    d["HIGH252"] = d["Close"].rolling(252).max()
    d["VR"] = d["Volume"] / d["Volume"].rolling(20).mean()

    delta = d["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    d["RSI"] = 100 - 100 / (1 + rs)

    d["VOL20"] = d["Volume"].rolling(20).mean()
    d["LOW20"] = d["Close"].rolling(20).min()
    d["HIGH20"] = d["Close"].rolling(20).max()
    return d


# ============================================================
# 3. 기존 ETF RADAR 선행신호와 동일한 핵심 구조
# ============================================================
def leading_signal(row, benchmark_ret20=0):
    current = float(row.get("Close", 0) or 0)
    ma20 = float(row.get("MA20", current) or current)
    ma60 = float(row.get("MA60", current) or current)
    ret5 = float(row.get("R5", 0) or 0)
    ret20 = float(row.get("R20", 0) or 0)
    vr = float(row.get("VR", 1) or 1)
    rsi = float(row.get("RSI", 50) or 50)

    dist20 = (current / ma20 - 1) * 100 if ma20 else 0
    rs20 = ret20 - benchmark_ret20
    accel = ret5 - ret20 / 4

    early_price = 92 if -1 <= dist20 <= 3 else 82 if dist20 <= 5 else 65 if dist20 < 8 else 35
    early_rsi = 92 if 48 <= rsi <= 62 else 84 if 43 <= rsi < 68 else 68 if rsi < 72 else 35
    flow = 92 if 1.10 <= vr <= 1.70 else 82 if 1.0 <= vr < 1.10 else 76 if 0.9 <= vr < 1.0 else 58 if vr < 2.2 else 38
    accel_score = 90 if 0.5 <= accel <= 5 else 78 if 0 <= accel < 0.5 else 68 if accel > 5 else 52
    rel = 88 if rs20 >= 6 else 80 if rs20 >= 3 else 70 if rs20 >= 0 else 48
    structure = 90 if current >= ma60 and ma20 >= ma60 else 78 if current >= ma60 else 55 if current >= ma20 else 35

    score = round(
        early_price * 0.22
        + early_rsi * 0.18
        + flow * 0.22
        + accel_score * 0.16
        + rel * 0.14
        + structure * 0.08
    )

    early_buy = score >= 72 and vr >= 1.05 and rsi < 70 and dist20 < 7 and rs20 >= -1

    return {
        "score": int(max(0, min(100, score))),
        "early_buy": bool(early_buy),
        "rs20": rs20,
        "dist20": dist20,
        "rsi": rsi,
        "vr": vr,
        "accel": accel,
    }


# ============================================================
# 4. 테마 점수
# ============================================================
def theme_score(theme_rows, bench_ret20=0, bench_ret60=0):
    if len(theme_rows) < 2:
        return None

    vals = []
    for r in theme_rows:
        if pd.isna(r.get("R20")) or pd.isna(r.get("R60")):
            continue
        sig = leading_signal(r, bench_ret20)
        vals.append({
            "r20": float(r["R20"]),
            "r60": float(r["R60"]),
            "rs20": sig["rs20"],
            "rs60": float(r["R60"]) - bench_ret60,
            "vr": float(r.get("VR", 1) if pd.notna(r.get("VR", 1)) else 1),
            "ma60gap": ((float(r["Close"]) / float(r["MA60"]) - 1) * 100) if pd.notna(r.get("MA60")) and r["MA60"] else 0,
            "accel": sig["accel"],
            "rsi": sig["rsi"],
            "lead": sig["score"],
            "early": sig["early_buy"],
        })

    if len(vals) < 2:
        return None

    x = pd.DataFrame(vals)

    def clip_score(v, lo, hi):
        return float(np.clip((v - lo) / (hi - lo) * 100, 0, 100))

    r20 = clip_score(x["r20"].mean(), -10, 15)
    r60 = clip_score(x["r60"].mean(), -15, 30)
    rs20 = clip_score(x["rs20"].mean(), -10, 12)
    rs60 = clip_score(x["rs60"].mean(), -15, 20)
    vr = clip_score(x["vr"].mean(), 0.8, 2.0)
    breadth = float((x["r20"] > -2).mean() * 100)
    ma60 = clip_score(x["ma60gap"].mean(), -10, 15)
    accel = clip_score(x["accel"].mean(), -5, 6)
    rsi = 100 - abs(float(x["rsi"].mean()) - 58) * 2.5
    rsi = float(np.clip(rsi, 0, 100))

    score = (
        r20 * 0.15
        + r60 * 0.15
        + rs20 * 0.15
        + rs60 * 0.10
        + vr * 0.15
        + breadth * 0.15
        + ma60 * 0.05
        + accel * 0.05
        + rsi * 0.05
    )

    early_count = int(x["early"].sum())
    early_ratio = early_count / len(x)
    lead_avg = float(x["lead"].mean())

    # 기존 앱의 선행 테마 개념을 반영
    lead_theme = lead_avg * 0.55 + breadth * 0.25 + early_ratio * 100 * 0.20
    final = score * 0.70 + lead_theme * 0.30

    # 과열 패널티: 너무 많이 오른 테마는 미래테마 후보에서 감점
    heat = 0
    if float(x["rsi"].mean()) >= 75:
        heat += 12
    if float(x["r20"].mean()) >= 12:
        heat += 10
    if float(x["ma60gap"].mean()) >= 15:
        heat += 8

    final = float(np.clip(final - heat, 0, 100))

    if final >= 78:
        stage = "현재 주도"
    elif final >= 64:
        stage = "다음 수혜"
    elif final >= 50:
        stage = "관심 확대"
    else:
        stage = "초기 관심"

    return {
        "score": final,
        "stage": stage,
        "breadth": breadth,
        "lead_avg": lead_avg,
        "early_count": early_count,
        "members": len(x),
        "heat": heat,
    }


# ============================================================
# 5. 날짜별 테마 선정
# ============================================================
def build_snapshot(all_data, date_i):
    bench = all_data.get(BENCH)
    if bench is None or bench.empty:
        return None

    b = bench.iloc[: date_i + 1]
    if len(b) < 65:
        return None
    br = b.iloc[-1]
    bench_ret20 = float(br.get("R20", np.nan))
    bench_ret60 = float(br.get("R60", np.nan))
    if not np.isfinite(bench_ret20) or not np.isfinite(bench_ret60):
        return None

    theme_results = []
    for theme, members in THEME_GROUPS.items():
        rows = []
        for t in members:
            d = all_data.get(t)
            if d is None or d.empty or len(d) <= date_i:
                continue
            r = d.iloc[date_i]
            if pd.isna(r.get("MA60")) or pd.isna(r.get("R20")) or pd.isna(r.get("R60")):
                continue
            rr = r.to_dict()
            rr["ETF"] = t
            rows.append(rr)
        ts = theme_score(rows, bench_ret20, bench_ret60)
        if ts:
            ts["theme"] = theme
            ts["rows"] = rows
            theme_results.append(ts)

    if not theme_results:
        return None

    theme_results.sort(key=lambda z: z["score"], reverse=True)
    top = theme_results[0]
    candidates = []
    for r in top["rows"]:
        sig = leading_signal(r, bench_ret20)
        heat = 0
        c = float(r["Close"])
        ma20 = float(r["MA20"])
        rsi = sig["rsi"]
        dist20 = sig["dist20"]
        if rsi >= 78:
            heat += 32
        elif rsi >= 72:
            heat += 24
        elif rsi >= 68:
            heat += 12
        if float(r["R5"]) >= 10:
            heat += 25
        elif float(r["R5"]) >= 7:
            heat += 18
        elif float(r["R5"]) >= 5:
            heat += 10
        if dist20 >= 12:
            heat += 23
        elif dist20 >= 8:
            heat += 16
        elif dist20 >= 5:
            heat += 8
        if sig["vr"] >= 2:
            heat += 15
        elif sig["vr"] >= 1.5:
            heat += 10
        elif sig["vr"] >= 1.2:
            heat += 5
        candidates.append({"ETF": r["ETF"], "sig": sig, "heat": min(100, heat), "close": c, "ma20": ma20})

    if not candidates:
        return None

    # 선행점수 - 과열패널티를 적용해 테마 대표 ETF를 선정
    candidates.sort(key=lambda z: z["sig"]["score"] - z["heat"] * 0.35, reverse=True)
    winner = candidates[0]

    return {
        "theme": top["theme"],
        "theme_score": top["score"],
        "theme_stage": top["stage"],
        "winner": winner,
        "themes": theme_results,
    }


# ============================================================
# 6. 가격구간
# ============================================================
def price_zone(r):
    c = float(r["Close"])
    ma20 = float(r["MA20"])
    ma60 = float(r["MA60"])
    low20 = float(r["LOW20"])

    # 매수 가능: MA20 부근/최근 저점 부근 + 추세 훼손 전
    support = max(low20, ma20 * 0.985)
    ideal_top = ma20 * 1.025
    invalid = min(ma60 * 0.97, support * 0.97)

    if c <= ideal_top and c >= invalid and c >= ma60 * 0.98:
        state = "매수구간"
    elif c < invalid:
        state = "무효"
    elif c > ma20 * 1.07:
        state = "추격금지"
    else:
        state = "눌림대기"

    return {"state": state, "support": support, "ideal_top": ideal_top, "invalid": invalid}


# ============================================================
# 7. 전체 전략 백테스트
# ============================================================
def run_strategy_backtest(start, end, tickers, step_days=5):
    download_start = (pd.Timestamp(start) - pd.Timedelta(days=140)).strftime("%Y-%m-%d")
    download_end = (pd.Timestamp(end) + pd.Timedelta(days=80)).strftime("%Y-%m-%d")

    raw = download_prices(tickers, download_start, download_end)
    data = {k: indicators(v) for k, v in raw.items()}
    data = {k: v for k, v in data.items() if not v.empty}

    if BENCH not in data:
        raise RuntimeError("SPY 벤치마크 데이터를 가져오지 못했습니다.")

    common = data[BENCH].index
    for t in tickers:
        if t in data:
            common = common.intersection(data[t].index)
    common = common.sort_values()
    common = common[(common >= pd.Timestamp(start)) & (common <= pd.Timestamp(end))]

    rows = []
    dates_used = []

    # 5거래일 간격으로 검사하여 실행시간을 줄이고 과도한 중복신호를 완화
    for pos in range(0, len(common) - 61, max(1, step_days)):
        dt = common[pos]
        hist_pos = data[BENCH].index.get_loc(dt)
        snap = build_snapshot(data, hist_pos)
        if snap is None:
            continue

        winner = snap["winner"]
        t = winner["ETF"]
        d = data[t]
        if hist_pos + 60 >= len(d):
            continue

        # 신호 당일 종가가 아닌 다음 거래일 종가 진입
        entry_i = hist_pos + 1
        entry = d.iloc[entry_i]
        entry_price = float(entry["Close"])
        if not np.isfinite(entry_price) or entry_price <= 0:
            continue

        # 전략 A: 선택된 테마의 대표 ETF를 무조건 보유
        # 전략 B: 선행점수 >=72
        # 전략 C: 미래테마 + 선행 ETF
        # 전략 D: 미래테마 + 선행 ETF + 가격구간
        sig = winner["sig"]
        zone = price_zone(d.iloc[hist_pos])

        # A: 단순 테마 대표 ETF
        a_ok = True
        # B: 개별 선행점수만 통과
        b_ok = sig["score"] >= 72 and sig["early_buy"]
        # C: 미래테마 + 선행 ETF
        c_ok = snap["theme_score"] >= 60 and b_ok
        # D: C + 가격구간
        d_ok = c_ok and zone["state"] == "매수구간"

        future = d.iloc[entry_i + 0 : entry_i + 60]
        if len(future) < 60:
            continue

        rec = {
            "날짜": dt.date(),
            "테마": snap["theme"],
            "테마점수": round(snap["theme_score"], 1),
            "테마단계": snap["theme_stage"],
            "ETF": t,
            "선행점수": sig["score"],
            "과열점수": winner["heat"],
            "가격상태": zone["state"],
            "매수가": entry_price,
            "A_단순테마": a_ok,
            "B_선행점수": b_ok,
            "C_미래테마선행": c_ok,
            "D_미래테마선행가격": d_ok,
        }

        for n in [5, 20, 60]:
            ret = (float(future.iloc[n - 1]["Close"]) / entry_price - 1) * 100
            dd = (float(future.iloc[:n]["Close"].min()) / entry_price - 1) * 100
            rec[f"{n}일수익"] = ret
            rec[f"{n}일최저낙폭"] = dd

        # 전략별 활성 여부에 따른 결과도 별도 저장
        rows.append(rec)
        dates_used.append(dt)

    return pd.DataFrame(rows), data


# ============================================================
# 8. 성과 계산
# ============================================================
def strategy_summary(r, flag, horizon):
    x = r.loc[r[flag], f"{horizon}일수익"].dropna()
    dd = r.loc[r[flag], f"{horizon}일최저낙폭"].dropna()
    if x.empty:
        return {
            "신호수": 0,
            "승률": np.nan,
            "평균수익": np.nan,
            "중앙값": np.nan,
            "평균낙폭": np.nan,
            "최고": np.nan,
            "최대손실": np.nan,
        }
    return {
        "신호수": len(x),
        "승률": (x > 0).mean() * 100,
        "평균수익": x.mean(),
        "중앙값": x.median(),
        "평균낙폭": dd.mean() if not dd.empty else np.nan,
        "최고": x.max(),
        "최대손실": x.min(),
    }


# ============================================================
# 9. D 전략 자산곡선 시뮬레이션
# ============================================================
def simulate_equity_curve(r, data, initial_cash=1_000_000, hold_days=20,
                          fee_per_side=0.0010, slippage_per_side=0.0005):
    """D 전략을 실제 포트폴리오처럼 1회 1포지션으로 순차 시뮬레이션.
    - 신호일 이후 다음 거래일 종가 진입
    - D 조건만 사용
    - 보유 중 새 신호는 무시
    - 기본은 hold_days 후 청산
    - 수수료+슬리피지를 매수/매도 각각 반영
    """
    if r is None or r.empty:
        return pd.DataFrame(), {}
    rr = r.loc[r["D_미래테마선행가격"] == True].copy()
    rr["날짜"] = pd.to_datetime(rr["날짜"])
    rr = rr.sort_values("날짜").reset_index(drop=True)

    cash = float(initial_cash)
    equity_rows = []
    trades = []
    next_available = pd.Timestamp.min
    n_days = 0
    wins = 0

    for _, sig in rr.iterrows():
        signal_date = pd.Timestamp(sig["날짜"])
        if signal_date < next_available:
            continue
        ticker = sig["ETF"]
        d = data.get(ticker)
        if d is None or d.empty:
            continue
        idx = d.index.searchsorted(signal_date)
        entry_i = idx + 1
        exit_i = entry_i + int(hold_days) - 1
        if entry_i >= len(d) or exit_i >= len(d):
            continue
        entry_date = d.index[entry_i]
        exit_date = d.index[exit_i]
        entry_raw = float(d.iloc[entry_i]["Close"])
        exit_raw = float(d.iloc[exit_i]["Close"])
        if not np.isfinite(entry_raw) or not np.isfinite(exit_raw) or entry_raw <= 0:
            continue

        # 매수/매도 슬리피지를 불리하게 적용
        buy_price = entry_raw * (1 + slippage_per_side)
        sell_price = exit_raw * (1 - slippage_per_side)
        gross_ret = sell_price / buy_price - 1
        net_ret = gross_ret - fee_per_side * 2
        start_cash = cash
        cash = cash * (1 + net_ret)
        wins += int(net_ret > 0)
        n_days += max(1, (exit_date - entry_date).days)
        next_available = exit_date + pd.Timedelta(days=1)

        trades.append({
            "신호일": signal_date.date(), "진입일": entry_date.date(), "청산일": exit_date.date(),
            "테마": sig["테마"], "ETF": ticker, "테마점수": sig["테마점수"],
            "선행점수": sig["선행점수"], "가격상태": sig["가격상태"],
            "진입가격": entry_raw, "청산가격": exit_raw,
            "순수익률": net_ret * 100, "거래후자산": cash,
        })
        equity_rows.append({"날짜": exit_date, "자산": cash})

    trades_df = pd.DataFrame(trades)
    curve = pd.DataFrame(equity_rows)
    if curve.empty:
        return curve, {"초기자산": initial_cash, "최종자산": initial_cash, "총수익률": 0.0,
                       "승률": np.nan, "거래수": 0, "최대낙폭": 0.0, "연환산": np.nan}
    curve = curve.sort_values("날짜").drop_duplicates("날짜", keep="last")
    curve["고점"] = curve["자산"].cummax()
    curve["낙폭"] = (curve["자산"] / curve["고점"] - 1) * 100
    final_cash = float(curve.iloc[-1]["자산"])
    total_ret = (final_cash / initial_cash - 1) * 100
    days = max(1, (pd.Timestamp(curve.iloc[-1]["날짜"]) - pd.Timestamp(curve.iloc[0]["날짜"])).days)
    annualized = ((final_cash / initial_cash) ** (365.25 / days) - 1) * 100 if final_cash > 0 else -100
    metrics = {
        "초기자산": initial_cash, "최종자산": final_cash, "총수익률": total_ret,
        "승률": (wins / len(trades_df) * 100) if len(trades_df) else np.nan,
        "거래수": len(trades_df), "최대낙폭": float(curve["낙폭"].min()), "연환산": annualized,
        "평균거래수익": float(trades_df["순수익률"].mean()) if not trades_df.empty else np.nan,
    }
    return curve, {**metrics, "trades": trades_df}


def simulate_buy_hold(ticker, data, initial_cash=1_000_000):
    d = data.get(ticker)
    if d is None or d.empty:
        return pd.DataFrame(), {}
    x = d.dropna(subset=["Close"]).copy()
    if len(x) < 2:
        return pd.DataFrame(), {}
    p0 = float(x.iloc[0]["Close"])
    curve = pd.DataFrame({"날짜": x.index, "자산": initial_cash * x["Close"] / p0})
    curve["고점"] = curve["자산"].cummax()
    curve["낙폭"] = (curve["자산"] / curve["고점"] - 1) * 100
    final_cash = float(curve.iloc[-1]["자산"])
    days = max(1, (x.index[-1] - x.index[0]).days)
    annualized = ((final_cash / initial_cash) ** (365.25 / days) - 1) * 100
    return curve, {"초기자산": initial_cash, "최종자산": final_cash,
                   "총수익률": (final_cash / initial_cash - 1) * 100,
                   "최대낙폭": float(curve["낙폭"].min()), "연환산": annualized}

# ============================================================
# 10. 장기·단기 자동판정 백테스트
# ============================================================
def horizon_judgment_backtest_row(d, i):
    """시점 i까지의 정보만 사용해 장기/단기 판정을 만들고
    이후 20/60/120/250 거래일 성과를 별도로 기록한다.
    미래 데이터는 판정 계산에 사용하지 않는다.
    """
    if i < 200 or i + 250 >= len(d):
        return None

    r = d.iloc[i]
    close = float(r["Close"])
    ma60 = float(r["MA60"])
    ma120 = float(r["MA120"])
    ma200 = float(r["MA200"])
    r60 = float(r["R60"])
    r20 = float(r["R20"])
    r5 = float(r["R5"])
    rsi = float(r["RSI"])
    vr = float(r["VR"]) if np.isfinite(r["VR"]) else 1.0

    # 장기 보유 판단: 장기 추세 + 장기 모멘텀 + 장기 추세 훼손 여부
    long_score = 0
    long_score += 25 if close > ma200 else 0
    long_score += 20 if ma120 > ma200 else 0
    long_score += 15 if ma60 > ma120 else 0
    long_score += 15 if r60 > 10 else 8 if r60 > 0 else 0
    long_score += 15 if ma200 >= float(d.iloc[i-21]["MA200"]) else 0
    long_score += 10 if ma120 >= float(d.iloc[i-21]["MA120"]) else 0

    if long_score >= 80:
        long_state = "🟢 장기 핵심보유"
    elif long_score >= 65:
        long_state = "🟢 장기 보유"
    elif long_score >= 50:
        long_state = "🟡 추세 확인"
    else:
        long_state = "🔴 장기 재검토"

    # 단기 운용 판단: 최근 모멘텀 + MA20/60 + RSI + 거래량
    short_score = 0
    short_score += 25 if r5 > 0 else 0
    short_score += 20 if r20 > 2 else 10 if r20 > 0 else 0
    short_score += 20 if close > float(r["MA20"]) else 0
    short_score += 15 if float(r["MA20"]) > ma60 else 0
    short_score += 10 if 50 <= rsi <= 68 else 5 if 45 <= rsi <= 72 else 0
    short_score += 10 if vr >= 1.05 else 5 if vr >= 0.9 else 0

    if short_score >= 75:
        short_state = "🔥 단기 강세"
    elif short_score >= 60:
        short_state = "🟢 보유/운용"
    elif short_score >= 45:
        short_state = "🟡 매수 대기"
    else:
        short_state = "⚪ 단기 관찰"

    if long_score >= 80 and short_score >= 75:
        final_state = "🟢 장기 핵심보유 + 적극 운용"
    elif long_score >= 65 and short_score >= 60:
        final_state = "🟢 장기 보유 + 운용"
    elif long_score >= 65:
        final_state = "🟢 장기 보유 + 신규매수 대기"
    elif long_score < 50 and short_score < 50:
        final_state = "🔴 장기 재검토 + 단기 관찰"
    else:
        final_state = "🟡 혼합/추세 확인"

    entry_i = i + 1
    entry_price = float(d.iloc[entry_i]["Close"])
    out = {
        "신호일": d.index[i].date(),
        "진입일": d.index[entry_i].date(),
        "장기점수": long_score,
        "장기판정": long_state,
        "단기점수": short_score,
        "단기판정": short_state,
        "최종판정": final_state,
        "진입가": entry_price,
    }
    for h in [20, 60, 120, 250]:
        exit_price = float(d.iloc[entry_i + h - 1]["Close"])
        out[f"{h}일후수익률"] = (exit_price / entry_price - 1) * 100
    return out


def run_horizon_backtest(start, end, tickers, step_days=5):
    download_start = (pd.Timestamp(start) - pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    download_end = (pd.Timestamp(end) + pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    raw = download_prices(tickers, download_start, download_end)
    data = {k: indicators(v) for k, v in raw.items()}
    rows = []
    for ticker in tickers:
        d = data.get(ticker)
        if d is None or len(d) < 451:
            continue
        dates = d.index[(d.index >= pd.Timestamp(start)) & (d.index <= pd.Timestamp(end))]
        for dt in dates[::max(1, int(step_days))]:
            i = d.index.get_loc(dt)
            rec = horizon_judgment_backtest_row(d, i)
            if rec is not None:
                rec["ETF"] = ticker
                rec["종목명"] = POOL.get(ticker, ticker)
                rows.append(rec)
    return pd.DataFrame(rows), data


def summarize_horizon_backtest(df):
    if df is None or df.empty:
        return pd.DataFrame()
    rows = []
    for state_col in ["장기판정", "단기판정", "최종판정"]:
        for state, g in df.groupby(state_col):
            rows.append({
                "구분": state_col,
                "판정": state,
                "건수": len(g),
                "20일 평균": g["20일후수익률"].mean(),
                "60일 평균": g["60일후수익률"].mean(),
                "120일 평균": g["120일후수익률"].mean(),
                "250일 평균": g["250일후수익률"].mean(),
                "20일 승률": (g["20일후수익률"] > 0).mean() * 100,
                "120일 승률": (g["120일후수익률"] > 0).mean() * 100,
                "250일 승률": (g["250일후수익률"] > 0).mean() * 100,
            })
    return pd.DataFrame(rows)



# ============================================================
# 10-B. 장기판정 V2 — 장기보유와 추세훼손을 분리
# ============================================================
def horizon_judgment_v2(d, i):
    """시점 i 이전 데이터만 사용.
    V1의 문제였던 '일시적 조정 = 장기 재검토'를 줄이고,
    장기 재검토는 구조적 추세 훼손이 확인될 때만 발생하도록 설계한다.
    """
    if i < 252 or i + 250 >= len(d):
        return None
    r=d.iloc[i]
    close=float(r["Close"]); ma60=float(r["MA60"]); ma120=float(r["MA120"]); ma200=float(r["MA200"])
    ma200_60=float(d.iloc[i-60]["MA200"]); ma120_20=float(d.iloc[i-20]["MA120"])
    r60=float(r["R60"]); r120=float(r["R120"])
    high252=float(r["HIGH252"]) if np.isfinite(r["HIGH252"]) else close
    dd252=(close/high252-1)*100 if high252>0 else 0

    # 장기 적합도: 한 번의 조정으로 급락하지 않도록 '구조'에 더 높은 가중치
    score=0
    score += 30 if close > ma200 else 0
    score += 20 if ma120 > ma200 else 0
    score += 15 if ma60 > ma120 else 0
    score += 15 if ma200 > ma200_60 else 0
    score += 10 if ma120 > ma120_20 else 0
    score += 5 if r120 > 0 else 0
    score += 5 if dd252 > -20 else 0

    # 구조적 훼손: 단순 조정이 아니라 여러 조건이 동시에 무너진 경우만 재검토
    structural_break = (
        close < ma200 and
        ma120 < ma200 and
        ma200 <= ma200_60 and
        r120 < 0
    )

    # 20거래일 이상 MA200 아래에 있었는지도 확인
    below20 = int((d["Close"].iloc[i-19:i+1] < d["MA200"].iloc[i-19:i+1]).sum()) >= 15
    structural_break = structural_break and below20

    if structural_break:
        long_state="🔴 장기 재검토"
    elif score >= 80:
        long_state="🟢 장기 핵심보유"
    elif score >= 65:
        long_state="🟢 장기 보유"
    else:
        long_state="🟡 추세 확인"

    # 단기 운용은 기존 V1과 동일한 구조를 유지
    r20=float(r["R20"]); r5=float(r["R5"]); rsi=float(r["RSI"])
    vr=float(r["VR"]) if np.isfinite(r["VR"]) else 1.0
    short_score=0
    short_score += 25 if r5 > 0 else 0
    short_score += 20 if r20 > 2 else 10 if r20 > 0 else 0
    short_score += 20 if close > float(r["MA20"]) else 0
    short_score += 15 if float(r["MA20"]) > ma60 else 0
    short_score += 10 if 50 <= rsi <= 68 else 5 if 45 <= rsi <= 72 else 0
    short_score += 10 if vr >= 1.05 else 5 if vr >= 0.9 else 0
    if short_score >= 75: short_state="🔥 단기 강세"
    elif short_score >= 60: short_state="🟢 보유/운용"
    elif short_score >= 45: short_state="🟡 매수 대기"
    else: short_state="⚪ 단기 관찰"

    if long_state == "🔴 장기 재검토":
        final_state="🔴 장기 재검토"
    elif long_state == "🟢 장기 핵심보유" and short_state == "🔥 단기 강세":
        final_state="🟢 장기 핵심보유 + 적극 운용"
    elif long_state in ("🟢 장기 핵심보유","🟢 장기 보유"):
        final_state="🟢 장기 보유 + 현재 추세 확인"
    else:
        final_state="🟡 장기 보유 가능 + 추세 확인"

    entry_i=i+1; entry_price=float(d.iloc[entry_i]["Close"])
    out={"신호일":d.index[i].date(),"진입일":d.index[entry_i].date(),
         "장기점수V2":score,"장기판정V2":long_state,"단기점수":short_score,
         "단기판정":short_state,"최종판정V2":final_state,"진입가":entry_price,
         "구조적훼손":structural_break,"252일고점대비":dd252}
    for h in [20,60,120,250]:
        ep=float(d.iloc[entry_i+h-1]["Close"])
        out[f"{h}일후수익률"]=(ep/entry_price-1)*100
    return out


def run_horizon_backtest_v2(start,end,tickers,step_days=5):
    download_start=(pd.Timestamp(start)-pd.Timedelta(days=520)).strftime("%Y-%m-%d")
    download_end=(pd.Timestamp(end)+pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    raw=download_prices(tickers,download_start,download_end)
    data={k:indicators(v) for k,v in raw.items()}
    rows=[]
    for ticker in tickers:
        d=data.get(ticker)
        if d is None or len(d)<520: continue
        dates=d.index[(d.index>=pd.Timestamp(start))&(d.index<=pd.Timestamp(end))]
        for dt in dates[::max(1,int(step_days))]:
            i=d.index.get_loc(dt); rec=horizon_judgment_v2(d,i)
            if rec is not None:
                rec["ETF"]=ticker; rec["종목명"]=POOL.get(ticker,ticker); rows.append(rec)
    return pd.DataFrame(rows),data


def summarize_horizon_v2(df):
    if df is None or df.empty: return pd.DataFrame()
    rows=[]
    for col in ["장기판정V2","단기판정","최종판정V2"]:
        for state,g in df.groupby(col):
            rows.append({"구분":col,"판정":state,"건수":len(g),
                "20일 평균":g["20일후수익률"].mean(),"60일 평균":g["60일후수익률"].mean(),
                "120일 평균":g["120일후수익률"].mean(),"250일 평균":g["250일후수익률"].mean(),
                "20일 승률":(g["20일후수익률"]>0).mean()*100,
                "120일 승률":(g["120일후수익률"]>0).mean()*100,
                "250일 승률":(g["250일후수익률"]>0).mean()*100})
    return pd.DataFrame(rows)

# ============================================================
# 10-C. 장기판정 V3 — 장기적합성 / 장기추세 / 현재운용 분리
# ============================================================
def horizon_judgment_v3(d, i):
    """시점 i 이전 데이터만 사용.

    V3 원칙
    1) 장기적합성: 일시적 조정 때문에 장기보유 ETF를 탈락시키지 않는다.
    2) 장기추세: 현재 가격이 MA200 아래인지보다 장기 추세의 방향을 우선한다.
    3) 구조적훼손: 장기수익률/MA200/MA120이 동시에 약해질 때만 경고한다.
    4) 현재운용: 단기 점수는 장기적합성과 별도로 판단한다.
    """
    if i < 252 or i + 250 >= len(d):
        return None
    r=d.iloc[i]
    close=float(r["Close"])
    ma20=float(r["MA20"]); ma60=float(r["MA60"])
    ma120=float(r["MA120"]); ma200=float(r["MA200"])
    ma200_60=float(d.iloc[i-60]["MA200"])
    ma120_60=float(d.iloc[i-60]["MA120"])
    r60=float(r["R60"]); r120=float(r["R120"]); r252=float(r["R252"])
    high252=float(r["HIGH252"]) if np.isfinite(r["HIGH252"]) else close
    dd252=(close/high252-1)*100 if high252>0 else 0

    # --------------------------------------------------------
    # A. 장기적합성
    # 핵심은 '현재 가격 위치'보다 장기 추세의 지속성.
    # --------------------------------------------------------
    suitability=0
    suitability += 25 if r252 > 15 else 18 if r252 > 0 else 8 if r252 > -15 else 0
    suitability += 20 if ma200 > ma200_60 else 0
    suitability += 15 if ma120 > ma120_60 else 0
    suitability += 15 if r120 > 10 else 10 if r120 > 0 else 4 if r120 > -10 else 0
    suitability += 15 if ma120 > ma200 else 7 if ma120 >= ma200*0.98 else 0
    suitability += 10 if r60 > 0 else 4 if r60 > -8 else 0

    # 장기적합성은 일시적 가격조정만으로 핵심보유를 박탈하지 않음.
    if suitability >= 75:
        fit_state="🟢 장기 핵심보유"
    elif suitability >= 55:
        fit_state="🟢 장기 보유"
    elif suitability >= 40:
        fit_state="🟡 장기 보유 + 추세 확인"
    else:
        fit_state="🔴 장기 적합성 재검토"

    # --------------------------------------------------------
    # B. 장기추세 상태
    # --------------------------------------------------------
    trend_score=0
    trend_score += 30 if ma200 > ma200_60 else 0
    trend_score += 25 if ma120 > ma120_60 else 0
    trend_score += 20 if ma120 > ma200 else 0
    trend_score += 15 if r120 > 0 else 0
    trend_score += 10 if close > ma200 else 0
    if trend_score >= 75:
        trend_state="🟢 장기 상승추세"
    elif trend_score >= 50:
        trend_state="🟡 장기 추세 확인"
    else:
        trend_state="🔴 장기 하락추세"

    # --------------------------------------------------------
    # C. 구조적 훼손
    # 단순 MA200 하회는 훼손으로 보지 않는다.
    # 장기수익률 음수 + MA200 하락 + MA120 하락 + MA120<MA200
    # 네 조건이 동시에 확인될 때만 장기 경고.
    # --------------------------------------------------------
    below20=int((d["Close"].iloc[i-19:i+1] < d["MA200"].iloc[i-19:i+1]).sum()) >= 15
    structural_break=(
        r252 < 0 and r120 < 0 and
        ma200 <= ma200_60 and ma120 <= ma120_60 and
        ma120 < ma200 and close < ma200 and below20
    )

    # --------------------------------------------------------
    # D. 현재 운용 — V2의 단기 구조 유지
    # --------------------------------------------------------
    r20=float(r["R20"]); r5=float(r["R5"]); rsi=float(r["RSI"])
    vr=float(r["VR"]) if np.isfinite(r["VR"]) else 1.0
    short_score=0
    short_score += 25 if r5 > 0 else 0
    short_score += 20 if r20 > 2 else 10 if r20 > 0 else 0
    short_score += 20 if close > ma20 else 0
    short_score += 15 if ma20 > ma60 else 0
    short_score += 10 if 50 <= rsi <= 68 else 5 if 45 <= rsi <= 72 else 0
    short_score += 10 if vr >= 1.05 else 5 if vr >= 0.9 else 0
    if short_score >= 75: short_state="🔥 단기 강세"
    elif short_score >= 60: short_state="🟢 보유/운용"
    elif short_score >= 45: short_state="🟡 매수 대기"
    else: short_state="⚪ 단기 관찰"

    # --------------------------------------------------------
    # E. 최종 행동
    # 장기적합성/장기추세/현재운용을 섞지 않고 순서대로 표시.
    # --------------------------------------------------------
    if structural_break:
        action="🔴 장기 추세 훼손 · 신규매수 중단"
    elif fit_state == "🟢 장기 핵심보유" and short_state == "🔥 단기 강세":
        action="🟢 핵심보유 + 적극 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유") and short_state in ("🟢 보유/운용","🔥 단기 강세"):
        action="🟢 장기보유 + 현재 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유"):
        action="🟡 장기보유 유지 + 신규매수 대기"
    else:
        action="🟡 추세 확인 후 운용"

    entry_i=i+1
    entry_price=float(d.iloc[entry_i]["Close"])
    out={
        "신호일":d.index[i].date(),"진입일":d.index[entry_i].date(),
        "장기적합성점수V3":suitability,"장기적합성V3":fit_state,
        "장기추세점수V3":trend_score,"장기추세V3":trend_state,
        "단기점수V3":short_score,"단기운용V3":short_state,
        "최종행동V3":action,"진입가":entry_price,
        "구조적훼손V3":structural_break,"252일고점대비":dd252,
    }
    for h in [20,60,120,250]:
        ep=float(d.iloc[entry_i+h-1]["Close"])
        out[f"{h}일후수익률"]=(ep/entry_price-1)*100
    return out


def run_horizon_backtest_v3(start,end,tickers,step_days=5):
    download_start=(pd.Timestamp(start)-pd.Timedelta(days=520)).strftime("%Y-%m-%d")
    download_end=(pd.Timestamp(end)+pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    raw=download_prices(tickers,download_start,download_end)
    data={k:indicators(v) for k,v in raw.items()}
    rows=[]
    for ticker in tickers:
        d=data.get(ticker)
        if d is None or len(d)<520: continue
        dates=d.index[(d.index>=pd.Timestamp(start))&(d.index<=pd.Timestamp(end))]
        for dt in dates[::max(1,int(step_days))]:
            i=d.index.get_loc(dt)
            rec=horizon_judgment_v3(d,i)
            if rec is not None:
                rec["ETF"]=ticker; rec["종목명"]=POOL.get(ticker,ticker); rows.append(rec)
    return pd.DataFrame(rows),data


def summarize_horizon_v3(df):
    if df is None or df.empty: return pd.DataFrame()
    rows=[]
    for col in ["장기적합성V3","장기추세V3","단기운용V3","최종행동V3"]:
        for state,g in df.groupby(col):
            rows.append({"구분":col,"판정":state,"건수":len(g),
                "20일 평균":g["20일후수익률"].mean(),"60일 평균":g["60일후수익률"].mean(),
                "120일 평균":g["120일후수익률"].mean(),"250일 평균":g["250일후수익률"].mean(),
                "20일 승률":(g["20일후수익률"]>0).mean()*100,
                "120일 승률":(g["120일후수익률"]>0).mean()*100,
                "250일 승률":(g["250일후수익률"]>0).mean()*100})
    return pd.DataFrame(rows)




# ============================================================
# 10-D. 장기판정 V4 — 보유 적합성과 현재 추세를 완전히 분리
# ============================================================
def horizon_judgment_v4(d, i):
    """시점 i 이전 데이터만 사용.

    V4 원칙
    - 장기적합성은 미래수익률을 예측하는 점수가 아니라 '계속 보유할 만한 구조인가'를 판단.
    - 단기 조정/고점 대비 하락만으로 장기 핵심보유를 박탈하지 않음.
    - 장기적합성에는 최근 1년 동안 장기추세가 유지된 '지속성'을 가장 크게 반영.
    - 현재 추세와 단기운용은 별도 축으로 판단.
    - 구조적 훼손만 실제 신규매수 중단 사유로 사용.
    """
    if i < 300 or i + 250 >= len(d): return None
    r=d.iloc[i]
    close=float(r["Close"]); ma20=float(r["MA20"]); ma60=float(r["MA60"])
    ma120=float(r["MA120"]); ma200=float(r["MA200"])
    ma200_60=float(d.iloc[i-60]["MA200"]); ma120_60=float(d.iloc[i-60]["MA120"])
    r20=float(r["R20"]); r60=float(r["R60"]); r120=float(r["R120"]); r252=float(r["R252"])
    high252=float(r["HIGH252"]) if np.isfinite(r["HIGH252"]) else close
    dd252=(close/high252-1)*100 if high252>0 else 0

    # ① 장기 지속성: 최근 252일 중 장기추세 위에서 머문 비율
    w=d.iloc[i-251:i+1]
    above200=float((w["Close"] >= w["MA200"]).mean())*100
    above120=float((w["Close"] >= w["MA120"]).mean())*100
    ma200_up=ma200 > ma200_60
    ma120_up=ma120 > ma120_60

    # ② 장기적합성: 현재 가격의 단기 위치보다 추세 지속성을 우선
    suitability=(
        above200*0.40
        + above120*0.20
        + (25 if ma200_up else 0)
        + (15 if r252>0 else 7 if r252>-15 else 0)
    )
    suitability=float(np.clip(suitability,0,100))

    if suitability >= 78:
        fit_state="🟢 장기 핵심보유"
    elif suitability >= 62:
        fit_state="🟢 장기 보유"
    elif suitability >= 48:
        fit_state="🟡 장기 보유 + 추세 확인"
    else:
        fit_state="🔴 장기 적합성 재검토"

    # ③ 장기추세: 현재 위치를 포함해 '지금의 추세'를 별도 판단
    trend_score=0
    trend_score += 30 if ma200_up else 0
    trend_score += 25 if ma120_up else 0
    trend_score += 20 if ma120 > ma200 else 0
    trend_score += 15 if r120 > 0 else 0
    trend_score += 10 if close > ma200 else 0
    if trend_score >= 75: trend_state="🟢 장기 상승추세"
    elif trend_score >= 50: trend_state="🟡 장기 조정/추세 확인"
    else: trend_state="🔴 장기 하락추세"

    # ④ 구조적 훼손: 지속성 자체가 무너졌을 때만
    structural_break=(
        above200 < 45 and above120 < 50 and
        r252 < 0 and r120 < 0 and
        not ma200_up and not ma120_up and
        ma120 < ma200 and close < ma200
    )

    # ⑤ 현재 운용 — 기존 단기 구조 유지
    rsi=float(r["RSI"]); vr=float(r["VR"]) if np.isfinite(r["VR"]) else 1.0
    short_score=0
    short_score += 25 if float(r["R5"]) > 0 else 0
    short_score += 20 if r20 > 2 else 10 if r20 > 0 else 0
    short_score += 20 if close > ma20 else 0
    short_score += 15 if ma20 > ma60 else 0
    short_score += 10 if 50 <= rsi <= 68 else 5 if 45 <= rsi <= 72 else 0
    short_score += 10 if vr >= 1.05 else 5 if vr >= 0.9 else 0
    if short_score >= 75: short_state="🔥 단기 강세"
    elif short_score >= 60: short_state="🟢 보유/운용"
    elif short_score >= 45: short_state="🟡 매수 대기"
    else: short_state="⚪ 단기 관찰"

    # ⑥ 최종 행동: 장기 보유 판단과 매매 타이밍을 분리
    if structural_break:
        action="🔴 구조적 추세 훼손 · 신규매수 중단"
    elif fit_state == "🟢 장기 핵심보유" and short_state == "🔥 단기 강세":
        action="🟢 핵심보유 + 적극 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유") and short_state in ("🟢 보유/운용","🔥 단기 강세"):
        action="🟢 장기보유 + 현재 운용"
    elif fit_state in ("🟢 장기 핵심보유","🟢 장기 보유"):
        action="🟡 장기보유 유지 + 신규매수 대기"
    elif trend_state == "🟡 장기 조정/추세 확인":
        action="🟡 장기 추세 확인 후 운용"
    else:
        action="⚪ 관찰"

    entry_i=i+1; entry_price=float(d.iloc[entry_i]["Close"])
    out={
        "신호일":d.index[i].date(),"진입일":d.index[entry_i].date(),
        "장기적합성점수V4":round(suitability,1),"장기적합성V4":fit_state,
        "장기추세점수V4":trend_score,"장기추세V4":trend_state,
        "단기점수V4":short_score,"단기운용V4":short_state,
        "장기추세지속성V4":round(above200,1),"구조적훼손V4":structural_break,
        "최종행동V4":action,"진입가":entry_price,"252일고점대비":dd252,
    }
    for h in [20,60,120,250]:
        ep=float(d.iloc[entry_i+h-1]["Close"]); out[f"{h}일후수익률"]=(ep/entry_price-1)*100
    return out

def run_horizon_backtest_v4(start,end,tickers,step_days=5):
    download_start=(pd.Timestamp(start)-pd.Timedelta(days=560)).strftime("%Y-%m-%d")
    download_end=(pd.Timestamp(end)+pd.Timedelta(days=420)).strftime("%Y-%m-%d")
    raw=download_prices(tickers,download_start,download_end)
    data={k:indicators(v) for k,v in raw.items()}
    rows=[]
    for ticker in tickers:
        d=data.get(ticker)
        if d is None or len(d)<560: continue
        dates=d.index[(d.index>=pd.Timestamp(start))&(d.index<=pd.Timestamp(end))]
        for dt in dates[::max(1,int(step_days))]:
            i=d.index.get_loc(dt); rec=horizon_judgment_v4(d,i)
            if rec is not None:
                rec["ETF"]=ticker; rec["종목명"]=POOL.get(ticker,ticker); rows.append(rec)
    return pd.DataFrame(rows),data

def summarize_horizon_v4(df):
    if df is None or df.empty: return pd.DataFrame()
    rows=[]
    for col in ["장기적합성V4","장기추세V4","단기운용V4","최종행동V4"]:
        for state,g in df.groupby(col):
            rows.append({"구분":col,"판정":state,"건수":len(g),
                "20일 평균":g["20일후수익률"].mean(),"60일 평균":g["60일후수익률"].mean(),
                "120일 평균":g["120일후수익률"].mean(),"250일 평균":g["250일후수익률"].mean(),
                "20일 승률":(g["20일후수익률"]>0).mean()*100,
                "120일 승률":(g["120일후수익률"]>0).mean()*100,
                "250일 승률":(g["250일후수익률"]>0).mean()*100})
    return pd.DataFrame(rows)

# ============================================================
# 10. UI
# ============================================================
st.title("🧪 ETF RADAR STRATEGY TEST")
st.caption("미래테마 → 선행 ETF → 과열 필터 → 가격구간까지 실제 투자 흐름을 과거 데이터로 검증합니다.")

st.info(
    "이번 테스트의 목적은 기능을 더 만드는 것이 아니라, "
    "현재 ETF RADAR의 핵심 로직에 실제 투자 우위가 있는지 확인하는 것입니다. "
    "데이터 다운로드와 계산은 Streamlit 캐시를 사용해 반복 실행을 줄입니다."
)

c1, c2 = st.columns(2)
start = c1.date_input("시작일", date(2021, 1, 1), key="st_start")
end = c2.date_input("종료일", date(2025, 12, 31), key="st_end")

selected = st.multiselect(
    "테스트 ETF",
    list(POOL.keys()),
    ["QQQ", "XLK", "SMH", "SOXX", "BOTZ", "ARKQ", "GLD", "TLT", "INDA", "EWY", "EWJ", "EEM"],
    format_func=lambda x: f"{x} · {POOL[x]}",
)

step = st.select_slider(
    "검사 간격",
    options=[1, 3, 5, 10],
    value=5,
    format_func=lambda x: "매일" if x == 1 else f"{x}거래일마다",
)

st.markdown("---")
run_clicked = st.button("🧪 전체 투자로직 백테스트 실행", type="primary", use_container_width=True)

if run_clicked:
    if start >= end:
        st.error("시작일은 종료일보다 빨라야 합니다.")
        st.stop()
    if len(selected) < 4:
        st.error("테마 비교를 위해 ETF를 4개 이상 선택하십시오.")
        st.stop()

    with st.status("전체 투자로직을 과거 날짜별로 검증하는 중...", expanded=True) as status:
        st.write("① 과거 가격 데이터 다운로드")
        st.write("② ETF별 기술지표 계산")
        st.write("③ 날짜별 미래테마 계산")
        st.write("④ 테마 대표 ETF + 선행신호 + 가격구간 판정")
        st.write("⑤ 다음 거래일 진입 후 5·20·60일 성과 계산")
        try:
            result, data = run_strategy_backtest(start, end, selected, step)
            st.session_state["strategy_result"] = result
            st.session_state["strategy_data"] = data
            status.update(label="백테스트 완료", state="complete", expanded=False)
        except Exception as ex:
            status.update(label="백테스트 실패", state="error", expanded=True)
            st.exception(ex)
            st.stop()

r = st.session_state.get("strategy_result")

if r is None:
    st.markdown("### 테스트 방법")
    st.markdown(
        """
        **A. 단순 테마** → 테마 대표 ETF를 선택

        **B. 선행점수** → 선행점수 조건을 추가

        **C. 미래테마 + 선행** → 미래테마가 강한 구간에서만 선행 ETF 선택

        **D. 미래테마 + 선행 + 가격** → C에 현재 가격구간까지 추가

        최종적으로 **D가 A/B/C보다 지속적으로 우수한지** 확인합니다.
        """
    )
else:
    if r.empty:
        st.error("조건을 만족하는 테스트 결과가 없습니다.")
        st.stop()

    st.success(f"검증 완료 · {len(r):,}개 검사 시점")

    flags = {
        "A 단순테마": "A_단순테마",
        "B 선행점수": "B_선행점수",
        "C 미래테마+선행": "C_미래테마선행",
        "D 미래테마+선행+가격": "D_미래테마선행가격",
    }

    st.subheader("① 한눈에 보는 핵심 결과")
    for horizon in [20, 60]:
        st.markdown(f"#### {horizon}일 성과")
        cols = st.columns(4)
        for col, (name, flag) in zip(cols, flags.items()):
            q = strategy_summary(r, flag, horizon)
            if q["신호수"] == 0:
                col.metric(name, "신호 없음")
            else:
                col.metric(name, f"{q['평균수익']:+.2f}%", f"승률 {q['승률']:.1f}%")

    st.subheader("② 전략 비교표")
    rows = []
    for name, flag in flags.items():
        for h in [5, 20, 60]:
            q = strategy_summary(r, flag, h)
            rows.append({
                "전략": name,
                "기간": f"{h}일",
                "신호수": q["신호수"],
                "승률": q["승률"],
                "평균수익": q["평균수익"],
                "중앙값": q["중앙값"],
                "평균최저낙폭": q["평균낙폭"],
                "최고수익": q["최고"],
                "최대손실": q["최대손실"],
            })
    summary = pd.DataFrame(rows)
    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "승률": st.column_config.NumberColumn(format="%.1f%%"),
            "평균수익": st.column_config.NumberColumn(format="%+.2f%%"),
            "중앙값": st.column_config.NumberColumn(format="%+.2f%%"),
            "평균최저낙폭": st.column_config.NumberColumn(format="%.2f%%"),
            "최고수익": st.column_config.NumberColumn(format="%+.2f%%"),
            "최대손실": st.column_config.NumberColumn(format="%+.2f%%"),
        },
    )

    st.subheader("③ 연도별 검증")
    r2 = r.copy()
    r2["연도"] = pd.to_datetime(r2["날짜"]).dt.year
    year_rows = []
    for year, g in r2.groupby("연도"):
        for name, flag in flags.items():
            q = strategy_summary(g, flag, 20)
            year_rows.append({
                "연도": int(year),
                "전략": name,
                "신호수": q["신호수"],
                "20일 승률": q["승률"],
                "20일 평균": q["평균수익"],
                "20일 평균낙폭": q["평균낙폭"],
            })
    st.dataframe(
        pd.DataFrame(year_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "20일 승률": st.column_config.NumberColumn(format="%.1f%%"),
            "20일 평균": st.column_config.NumberColumn(format="%+.2f%%"),
            "20일 평균낙폭": st.column_config.NumberColumn(format="%.2f%%"),
        },
    )

    st.subheader("④ 어떤 테마가 실제로 잘 작동했는가")
    theme_rows = []
    for theme, g in r.groupby("테마"):
        q = strategy_summary(g, "C_미래테마선행", 20)
        if q["신호수"]:
            theme_rows.append({
                "테마": theme,
                "신호수": q["신호수"],
                "20일 승률": q["승률"],
                "20일 평균": q["평균수익"],
                "60일 평균": strategy_summary(g, "C_미래테마선행", 60)["평균수익"],
                "60일 평균낙폭": strategy_summary(g, "C_미래테마선행", 60)["평균낙폭"],
            })
    if theme_rows:
        st.dataframe(
            pd.DataFrame(theme_rows).sort_values("20일 평균", ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={
                "20일 승률": st.column_config.NumberColumn(format="%.1f%%"),
                "20일 평균": st.column_config.NumberColumn(format="%+.2f%%"),
                "60일 평균": st.column_config.NumberColumn(format="%+.2f%%"),
                "60일 평균낙폭": st.column_config.NumberColumn(format="%.2f%%"),
            },
        )

    st.subheader("⑤ 최종 판단")
    c20 = strategy_summary(r, "C_미래테마선행", 20)
    d20 = strategy_summary(r, "D_미래테마선행가격", 20)
    c60 = strategy_summary(r, "C_미래테마선행", 60)
    d60 = strategy_summary(r, "D_미래테마선행가격", 60)

    if d20["신호수"] and c20["신호수"]:
        delta20 = d20["평균수익"] - c20["평균수익"]
        delta60 = d60["평균수익"] - c60["평균수익"] if d60["신호수"] else np.nan
        if delta20 > 0 and (np.isnan(delta60) or delta60 > 0):
            st.success(
                f"가격구간을 추가했을 때 평균수익이 개선되었습니다. "
                f"20일 {delta20:+.2f}%p / 60일 {delta60:+.2f}%p"
            )
        else:
            st.warning(
                f"가격구간 추가 효과가 뚜렷하지 않습니다. "
                f"20일 {delta20:+.2f}%p / 60일 {delta60:+.2f}%p"
            )

    with st.expander("⑥ 전체 검사 원본 데이터"):
        st.dataframe(r, use_container_width=True, hide_index=True, height=520)


    st.markdown("---")
    st.subheader("⑦ 💰 100만원 실제 운용 시뮬레이션")
    st.caption("D 전략 신호가 발생했을 때 1회 1포지션으로 순차 진입합니다. 보유 중 새 신호는 건너뛰며, 수수료와 슬리피지를 포함합니다.")
    sc1, sc2, sc3, sc4 = st.columns(4)
    initial_cash = sc1.number_input("초기자금", min_value=100000, value=1000000, step=100000, key="sim_cash")
    hold_days = sc2.selectbox("보유기간", [5, 20, 60], index=1, key="sim_hold")
    fee = sc3.number_input("편도 비용", min_value=0.0, max_value=1.0, value=0.10, step=0.01, key="sim_fee", help="수수료·세금 등을 단순화한 가정(%)")
    slip = sc4.number_input("편도 슬리피지", min_value=0.0, max_value=1.0, value=0.05, step=0.01, key="sim_slip", help="신호와 실제 체결가격 차이 가정(%)")
    if st.button("💰 100만원 운용 결과 계산", type="primary", use_container_width=True):
        curve, m = simulate_equity_curve(
            r, data, initial_cash=float(initial_cash), hold_days=int(hold_days),
            fee_per_side=float(fee)/100, slippage_per_side=float(slip)/100
        )
        st.session_state["sim_curve"] = curve
        st.session_state["sim_metrics"] = m
        st.session_state["sim_hold"] = hold_days

    m = st.session_state.get("sim_metrics")
    curve = st.session_state.get("sim_curve")
    if m is not None:
        mc = st.columns(5)
        mc[0].metric("최종자산", f"₩{m['최종자산']:,.0f}")
        mc[1].metric("총수익률", f"{m['총수익률']:+.1f}%")
        mc[2].metric("연환산", f"{m['연환산']:+.1f}%")
        mc[3].metric("승률", f"{m['승률']:.1f}%" if np.isfinite(m['승률']) else "-")
        mc[4].metric("최대낙폭", f"{m['최대낙폭']:.1f}%")
        if curve is not None and not curve.empty:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=curve["날짜"], y=curve["자산"], mode="lines", name="D 전략 자산"))
            fig.update_layout(height=380, margin=dict(l=10,r=10,t=30,b=10), yaxis_title="자산(원)", xaxis_title="날짜")
            st.plotly_chart(fig, use_container_width=True)
        trades = m.get("trades") if isinstance(m, dict) else None
        if trades is not None and not trades.empty:
            st.markdown(f"**거래 {len(trades)}회 · 평균 거래수익 {trades['순수익률'].mean():+.2f}%**")
            st.dataframe(trades, use_container_width=True, hide_index=True)
            st.download_button("📥 100만원 거래내역 CSV", trades.to_csv(index=False).encode("utf-8-sig"), "ETF_RADAR_100만원_거래내역.csv", "text/csv", use_container_width=True)

    st.download_button(
        "📥 전략 백테스트 CSV 저장",
        r.to_csv(index=False).encode("utf-8-sig"),
        "ETF_RADAR_STRATEGY_BACKTEST.csv",
        "text/csv",
        use_container_width=True,
    )


# ============================================================
# 11. 장기·단기 자동판정 백테스트 UI
# ============================================================
st.markdown("---")
st.header("🧪 내 ETF 장기·단기 자동판정 백테스트")
st.caption("장기 보유 가치와 현재 단기 운용 타이밍을 분리해서 검증합니다. 판정 시점 이후 20·60·120·250거래일 수익률을 비교합니다.")

hc1, hc2 = st.columns(2)
h_start = hc1.date_input("자동판정 시작일", date(2018, 1, 1), key="h_start")
h_end = hc2.date_input("자동판정 종료일", date.today(), key="h_end")
h_selected = st.multiselect(
    "자동판정 테스트 ETF",
    list(POOL.keys()),
    ["QQQ", "XLK", "SMH", "SOXX", "BOTZ", "GLD", "TLT"],
    format_func=lambda x: f"{x} · {POOL[x]}",
    key="h_selected",
)
h_step = st.select_slider(
    "자동판정 검사 간격",
    options=[1, 3, 5, 10],
    value=5,
    format_func=lambda x: "매일" if x == 1 else f"{x}거래일마다",
    key="h_step",
)

if st.button("🧪 장기·단기 자동판정 테스트 실행", type="primary", use_container_width=True):
    if h_start >= h_end:
        st.error("시작일은 종료일보다 빨라야 합니다.")
        st.stop()
    if not h_selected:
        st.error("테스트 ETF를 1개 이상 선택하십시오.")
        st.stop()
    with st.spinner("장기·단기 판정과 이후 수익률을 계산하는 중..."):
        try:
            h_result, h_data = run_horizon_backtest(h_start, h_end, h_selected, h_step)
            st.session_state["horizon_result"] = h_result
        except Exception as ex:
            st.exception(ex)
            st.stop()

hr = st.session_state.get("horizon_result")
if hr is not None:
    if hr.empty:
        st.warning("조건을 만족하는 백테스트 결과가 없습니다.")
    else:
        st.success(f"자동판정 검증 완료 · {len(hr):,}개 검사 시점")
        hs = summarize_horizon_backtest(hr)
        st.subheader("① 판정별 성과")
        st.dataframe(
            hs,
            use_container_width=True,
            hide_index=True,
            column_config={
                "20일 평균": st.column_config.NumberColumn(format="%+.2f%%"),
                "60일 평균": st.column_config.NumberColumn(format="%+.2f%%"),
                "120일 평균": st.column_config.NumberColumn(format="%+.2f%%"),
                "250일 평균": st.column_config.NumberColumn(format="%+.2f%%"),
                "20일 승률": st.column_config.NumberColumn(format="%.1f%%"),
                "120일 승률": st.column_config.NumberColumn(format="%.1f%%"),
                "250일 승률": st.column_config.NumberColumn(format="%.1f%%"),
            },
        )

        st.subheader("② ETF별 장기판정 검증")
        etf_rows = []
        for ticker, g in hr.groupby("ETF"):
            for state, sg in g.groupby("장기판정"):
                etf_rows.append({
                    "ETF": ticker,
                    "장기판정": state,
                    "건수": len(sg),
                    "120일 평균": sg["120일후수익률"].mean(),
                    "250일 평균": sg["250일후수익률"].mean(),
                    "120일 승률": (sg["120일후수익률"] > 0).mean() * 100,
                    "250일 승률": (sg["250일후수익률"] > 0).mean() * 100,
                })
        st.dataframe(pd.DataFrame(etf_rows), use_container_width=True, hide_index=True,
                     column_config={
                         "120일 평균": st.column_config.NumberColumn(format="%+.2f%%"),
                         "250일 평균": st.column_config.NumberColumn(format="%+.2f%%"),
                         "120일 승률": st.column_config.NumberColumn(format="%.1f%%"),
                         "250일 승률": st.column_config.NumberColumn(format="%.1f%%"),
                     })

        st.subheader("③ 원본 결과")
        with st.expander("전체 검사 데이터"):
            st.dataframe(hr, use_container_width=True, hide_index=True, height=520)

        st.download_button(
            "📥 장기·단기 자동판정 결과 CSV 저장",
            hr.to_csv(index=False).encode("utf-8-sig"),
            "ETF_RADAR_HORIZON_BACKTEST.csv",
            "text/csv",
            use_container_width=True,
        )


# ============================================================
# 12. 장기판정 V2 검증 UI
# ============================================================
st.markdown("---")
st.header("🧪 장기보유 자동판정 V2 검증")
st.caption("V1의 단순 점수판정을 개선해, 일시적 조정과 구조적 추세 훼손을 구분합니다.")

v2c1,v2c2=st.columns(2)
v2_start=v2c1.date_input("V2 시작일",date(2018,1,1),key="v2_start")
v2_end=v2c2.date_input("V2 종료일",date(2025,12,31),key="v2_end")
v2_selected=st.multiselect("V2 테스트 ETF",list(POOL.keys()),
    ["QQQ","XLK","SMH","SOXX","BOTZ","ARKQ","GLD","TLT"],
    format_func=lambda x:f"{x} · {POOL[x]}",key="v2_selected")
v2_step=st.select_slider("V2 검사 간격",options=[1,3,5,10],value=5,
    format_func=lambda x:"매일" if x==1 else f"{x}거래일마다",key="v2_step")

if st.button("🧪 장기보유 V2 백테스트 실행",type="primary",use_container_width=True):
    if v2_start>=v2_end: st.error("시작일은 종료일보다 빨라야 합니다."); st.stop()
    if not v2_selected: st.error("ETF를 1개 이상 선택하십시오."); st.stop()
    with st.spinner("V2 장기판정과 미래수익률을 검증하는 중..."):
        try:
            v2_result,v2_data=run_horizon_backtest_v2(v2_start,v2_end,v2_selected,v2_step)
            st.session_state["horizon_v2_result"]=v2_result
        except Exception as ex:
            st.exception(ex); st.stop()

v2r=st.session_state.get("horizon_v2_result")
if v2r is not None:
    if v2r.empty:
        st.warning("V2 결과가 없습니다.")
    else:
        st.success(f"V2 검증 완료 · {len(v2r):,}개 검사 시점")
        v2s=summarize_horizon_v2(v2r)
        st.subheader("① V2 판정별 성과")
        st.dataframe(v2s,use_container_width=True,hide_index=True,
            column_config={"20일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "60일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "120일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "250일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "20일 승률":st.column_config.NumberColumn(format="%.1f%%"),
                           "120일 승률":st.column_config.NumberColumn(format="%.1f%%"),
                           "250일 승률":st.column_config.NumberColumn(format="%.1f%%")})

        st.subheader("② V2 핵심 검증 — 장기판정이 순서대로 좋아지는가")
        longv=v2r.groupby("장기판정V2").agg(
            건수=("ETF","size"),
            평균120일=("120일후수익률","mean"),
            평균250일=("250일후수익률","mean"),
            승률120일=("120일후수익률",lambda x:(x>0).mean()*100),
            승률250일=("250일후수익률",lambda x:(x>0).mean()*100),
        ).reset_index()
        st.dataframe(longv,use_container_width=True,hide_index=True,
            column_config={"평균120일":st.column_config.NumberColumn(format="%+.2f%%"),
                           "평균250일":st.column_config.NumberColumn(format="%+.2f%%"),
                           "승률120일":st.column_config.NumberColumn(format="%.1f%%"),
                           "승률250일":st.column_config.NumberColumn(format="%.1f%%")})

        st.subheader("③ ETF별 V2 장기판정")
        ev=[]
        for ticker,g in v2r.groupby("ETF"):
            for state,sg in g.groupby("장기판정V2"):
                ev.append({"ETF":ticker,"장기판정V2":state,"건수":len(sg),
                           "120일 평균":sg["120일후수익률"].mean(),"250일 평균":sg["250일후수익률"].mean(),
                           "250일 승률":(sg["250일후수익률"]>0).mean()*100})
        st.dataframe(pd.DataFrame(ev),use_container_width=True,hide_index=True,
            column_config={"120일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "250일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "250일 승률":st.column_config.NumberColumn(format="%.1f%%")})

        st.download_button("📥 장기보유 V2 결과 CSV 저장",v2r.to_csv(index=False).encode("utf-8-sig"),
            "ETF_RADAR_HORIZON_BACKTEST_V2.csv","text/csv",use_container_width=True)


# ============================================================
# 13. 장기판정 V3 검증 UI
# ============================================================
st.markdown("---")
st.header("🧪 장기보유 자동판정 V3 검증")
st.caption("장기적합성 · 장기추세 · 현재운용을 분리해 판단합니다. 일시적 조정은 장기보유 탈락으로 처리하지 않습니다.")

v3c1,v3c2=st.columns(2)
v3_start=v3c1.date_input("V3 시작일",date(2018,1,1),key="v3_start")
v3_end=v3c2.date_input("V3 종료일",date(2025,12,31),key="v3_end")
v3_selected=st.multiselect("V3 테스트 ETF",list(POOL.keys()),
    ["QQQ","XLK","SMH","SOXX","BOTZ","ARKQ","GLD","TLT"],
    format_func=lambda x:f"{x} · {POOL[x]}",key="v3_selected")
v3_step=st.select_slider("V3 검사 간격",options=[1,3,5,10],value=5,
    format_func=lambda x:"매일" if x==1 else f"{x}거래일마다",key="v3_step")

if st.button("🧪 장기보유 V3 백테스트 실행",type="primary",use_container_width=True):
    if v3_start>=v3_end: st.error("시작일은 종료일보다 빨라야 합니다."); st.stop()
    if not v3_selected: st.error("ETF를 1개 이상 선택하십시오."); st.stop()
    with st.spinner("V3 장기적합성·추세·운용을 검증하는 중..."):
        try:
            v3_result,v3_data=run_horizon_backtest_v3(v3_start,v3_end,v3_selected,v3_step)
            st.session_state["horizon_v3_result"]=v3_result
        except Exception as ex:
            st.exception(ex); st.stop()

v3r=st.session_state.get("horizon_v3_result")
if v3r is not None:
    if v3r.empty:
        st.warning("V3 결과가 없습니다.")
    else:
        st.success(f"V3 검증 완료 · {len(v3r):,}개 검사 시점")
        v3s=summarize_horizon_v3(v3r)
        st.subheader("① V3 판정별 성과")
        st.dataframe(v3s,use_container_width=True,hide_index=True,
            column_config={"20일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "60일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "120일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "250일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "20일 승률":st.column_config.NumberColumn(format="%.1f%%"),
                           "120일 승률":st.column_config.NumberColumn(format="%.1f%%"),
                           "250일 승률":st.column_config.NumberColumn(format="%.1f%%")})

        st.subheader("② V3 핵심 검증 — 장기적합성이 실제 미래성과를 구분하는가")
        lv=v3r.groupby("장기적합성V3").agg(
            건수=("ETF","size"), 평균120일=("120일후수익률","mean"), 평균250일=("250일후수익률","mean"),
            승률120일=("120일후수익률",lambda x:(x>0).mean()*100), 승률250일=("250일후수익률",lambda x:(x>0).mean()*100)
        ).reset_index()
        st.dataframe(lv,use_container_width=True,hide_index=True,
            column_config={"평균120일":st.column_config.NumberColumn(format="%+.2f%%"),
                           "평균250일":st.column_config.NumberColumn(format="%+.2f%%"),
                           "승률120일":st.column_config.NumberColumn(format="%.1f%%"),
                           "승률250일":st.column_config.NumberColumn(format="%.1f%%")})

        st.subheader("③ ETF별 V3 장기적합성")
        ev=[]
        for ticker,g in v3r.groupby("ETF"):
            for state,sg in g.groupby("장기적합성V3"):
                ev.append({"ETF":ticker,"장기적합성V3":state,"건수":len(sg),
                           "120일 평균":sg["120일후수익률"].mean(),"250일 평균":sg["250일후수익률"].mean(),
                           "250일 승률":(sg["250일후수익률"]>0).mean()*100})
        st.dataframe(pd.DataFrame(ev),use_container_width=True,hide_index=True,
            column_config={"120일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "250일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "250일 승률":st.column_config.NumberColumn(format="%.1f%%")})

        st.subheader("④ QQQ · SMH · SOXX 집중검증")
        focus=v3r[v3r["ETF"].isin(["QQQ","SMH","SOXX"])]
        if not focus.empty:
            fv=focus.groupby(["ETF","장기적합성V3"]).agg(
                건수=("ETF","size"), 평균120일=("120일후수익률","mean"), 평균250일=("250일후수익률","mean"),
                승률250일=("250일후수익률",lambda x:(x>0).mean()*100)
            ).reset_index()
            st.dataframe(fv,use_container_width=True,hide_index=True,
                column_config={"평균120일":st.column_config.NumberColumn(format="%+.2f%%"),
                               "평균250일":st.column_config.NumberColumn(format="%+.2f%%"),
                               "승률250일":st.column_config.NumberColumn(format="%.1f%%")})

        st.download_button("📥 장기보유 V3 결과 CSV 저장",v3r.to_csv(index=False).encode("utf-8-sig"),
            "ETF_RADAR_HORIZON_BACKTEST_V3.csv","text/csv",use_container_width=True)


# ============================================================
# 14. 장기판정 V4 검증 UI
# ============================================================
st.markdown("---")
st.header("🧪 장기보유 자동판정 V4 검증")
st.caption("장기적합성은 '미래수익률 예측'이 아니라 장기추세 지속성을 기준으로 판단하고, 현재 운용은 별도로 봅니다.")

v4c1,v4c2=st.columns(2)
v4_start=v4c1.date_input("V4 시작일",date(2018,1,1),key="v4_start")
v4_end=v4c2.date_input("V4 종료일",date(2025,12,31),key="v4_end")
v4_selected=st.multiselect("V4 테스트 ETF",list(POOL.keys()),
    ["QQQ","XLK","SMH","SOXX","BOTZ","ARKQ","GLD","TLT"],
    format_func=lambda x:f"{x} · {POOL[x]}",key="v4_selected")
v4_step=st.select_slider("V4 검사 간격",options=[1,3,5,10],value=5,
    format_func=lambda x:"매일" if x==1 else f"{x}거래일마다",key="v4_step")

if st.button("🧪 장기보유 V4 백테스트 실행",type="primary",use_container_width=True):
    if v4_start>=v4_end: st.error("시작일은 종료일보다 빨라야 합니다."); st.stop()
    if not v4_selected: st.error("테스트 ETF를 1개 이상 선택하십시오."); st.stop()
    with st.spinner("V4 장기적합성·추세·운용을 검증하는 중..."):
        try:
            v4_result,v4_data=run_horizon_backtest_v4(v4_start,v4_end,v4_selected,v4_step)
            st.session_state["horizon_v4_result"]=v4_result
        except Exception as ex:
            st.exception(ex); st.stop()

v4r=st.session_state.get("horizon_v4_result")
if v4r is not None:
    if v4r.empty:
        st.warning("V4 결과가 없습니다.")
    else:
        st.success(f"V4 검증 완료 · {len(v4r):,}개 검사 시점")
        v4s=summarize_horizon_v4(v4r)
        st.subheader("① V4 판정별 성과")
        st.dataframe(v4s,use_container_width=True,hide_index=True,
            column_config={"20일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "60일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "120일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "250일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "20일 승률":st.column_config.NumberColumn(format="%.1f%%"),
                           "120일 승률":st.column_config.NumberColumn(format="%.1f%%"),
                           "250일 승률":st.column_config.NumberColumn(format="%.1f%%")})

        st.subheader("② 핵심 ETF 검증 — QQQ / SMH / SOXX")
        focus=v4r[v4r["ETF"].isin(["QQQ","SMH","SOXX"])].copy()
        if not focus.empty:
            fv=focus.groupby(["ETF","장기적합성V4"]).agg(건수=("ETF","size"),
                평균120=("120일후수익률","mean"),평균250=("250일후수익률","mean"),
                승률120=("120일후수익률",lambda x:(x>0).mean()*100),
                승률250=("250일후수익률",lambda x:(x>0).mean()*100)).reset_index().rename(columns={"평균120":"120일 평균","평균250":"250일 평균","승률120":"120일 승률","승률250":"250일 승률"})
            st.dataframe(fv,use_container_width=True,hide_index=True,
                column_config={"120일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                               "250일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                               "120일 승률":st.column_config.NumberColumn(format="%.1f%%"),
                               "250일 승률":st.column_config.NumberColumn(format="%.1f%%")})

        st.subheader("③ V4 장기추세 지속성 검증")
        pv=v4r.groupby("장기추세V4").agg(건수=("ETF","size"),
            평균120=("120일후수익률","mean"),평균250=("250일후수익률","mean"),
            승률120=("120일후수익률",lambda x:(x>0).mean()*100),
            승률250=("250일후수익률",lambda x:(x>0).mean()*100)).reset_index().rename(columns={"평균120":"120일 평균","평균250":"250일 평균","승률120":"120일 승률","승률250":"250일 승률"})
        st.dataframe(pv,use_container_width=True,hide_index=True,
            column_config={"120일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "250일 평균":st.column_config.NumberColumn(format="%+.2f%%"),
                           "120일 승률":st.column_config.NumberColumn(format="%.1f%%"),
                           "250일 승률":st.column_config.NumberColumn(format="%.1f%%")})

        st.subheader("④ V4 구조적 훼손 비율")
        br=v4r.groupby("ETF")["구조적훼손V4"].mean().mul(100).reset_index(name="구조적훼손 비율")
        st.dataframe(br,use_container_width=True,hide_index=True,
            column_config={"구조적훼손 비율":st.column_config.NumberColumn(format="%.1f%%")})

        st.download_button("📥 장기보유 V4 결과 CSV 저장",v4r.to_csv(index=False).encode("utf-8-sig"),
            "ETF_RADAR_HORIZON_BACKTEST_V4.csv","text/csv",use_container_width=True)

# ============================================================
# 15. 실전형 C/D 체결 백테스트 V6
# ============================================================
def _trade_levels_v6(d, signal_i, entry_price):
    """신호일의 정보만 사용해 다음 거래일 진입 기준을 계산한다."""
    r = d.iloc[signal_i]
    c = float(r["Close"])
    ma20 = float(r["MA20"])
    ma60 = float(r["MA60"])
    low20 = float(r["LOW20"])
    support = max(low20, ma20 * 0.985)
    stop1 = min(ma60 * 0.97, support * 0.97)
    stop2 = min(stop1, low20 * 0.98)
    if not np.isfinite(stop1) or stop1 <= 0:
        stop1 = entry_price * 0.95
    if not np.isfinite(stop2) or stop2 <= 0:
        stop2 = stop1
    risk = max(entry_price - stop1, entry_price * 0.02)
    tp1 = entry_price + risk
    tp2 = entry_price + risk * 2.0
    return {"entry": entry_price, "support": support, "stop1": stop1,
            "stop2": stop2, "risk": risk, "tp1": tp1, "tp2": tp2,
            "signal_close": c}


def simulate_cd_trade_v7(r, data, initial_cash=1_000_000,
                         fee_per_side=0.0010, slippage_per_side=0.0005,
                         max_hold_days=250):
    """V7 실전형 C/D 체결 시뮬레이션.

    C/D 선정 로직은 변경하지 않고 청산 구조만 개선한다.
    1) D 신호 다음 거래일 시가 진입.
    2) 1R에서 50% 익절.
    3) 2R에서 남은 물량의 50%(전체의 25%) 익절.
    4) 2R 도달 이후 남은 25%는 20일선 추적손절.
    5) 1차 손절은 보유물량의 50%, 2차 손절은 잔여물량 전량.
    6) 같은 봉에서 손절과 익절이 충돌하면 보수적으로 손절 우선.
    7) 최대 보유기간 종료 시 잔여물량 종가 청산.
    8) 보유 중 새 D 신호는 무시.
    """
    if r is None or r.empty:
        return pd.DataFrame(), {"거래수": 0}

    signals = r.loc[r["D_미래테마선행가격"] == True].copy()
    if signals.empty:
        return pd.DataFrame(), {"거래수": 0}
    signals["날짜"] = pd.to_datetime(signals["날짜"])
    signals = signals.sort_values("날짜").reset_index(drop=True)

    cash = float(initial_cash)
    trades = []
    next_available = pd.Timestamp.min

    def px(v, fallback):
        try:
            v = float(v)
            return v if np.isfinite(v) and v > 0 else fallback
        except Exception:
            return fallback

    for _, sig in signals.iterrows():
        signal_date = pd.Timestamp(sig["날짜"])
        if signal_date < next_available:
            continue

        ticker = sig["ETF"]
        d = data.get(ticker)
        if d is None or d.empty:
            continue

        idx = d.index.searchsorted(signal_date)
        if idx >= len(d) or d.index[idx] != signal_date:
            continue
        entry_i = idx + 1
        if entry_i >= len(d):
            continue

        entry_row = d.iloc[entry_i]
        raw_entry = px(entry_row.get("Open", np.nan),
                       px(entry_row.get("Close", np.nan), np.nan))
        if not np.isfinite(raw_entry) or raw_entry <= 0:
            continue

        entry_fill = raw_entry * (1 + slippage_per_side)
        lv = _trade_levels_v6(d, idx, entry_fill)
        stop1 = float(lv["stop1"])
        stop2 = float(lv["stop2"])
        tp1 = float(lv["tp1"])
        tp2 = float(lv["tp2"])

        # 전체 포지션을 1.0으로 두고 부분청산한다.
        remaining = 1.0
        realized = 0.0
        tp1_hit = False
        tp2_hit = False
        stop1_hit = False
        stop2_hit = False
        trail_hit = False
        trail_active = False
        exit_reason = ""

        last_i = min(len(d) - 1, entry_i + int(max_hold_days) - 1)
        exit_i = last_i

        def net_return(fill, weight):
            # entry_fill은 진입 슬리피지를 이미 반영.
            # 각 부분청산에는 청산 슬리피지와 양쪽 비용을 보수적으로 반영.
            return weight * ((fill / entry_fill - 1) - fee_per_side * 2)

        for j in range(entry_i, last_i + 1):
            bar = d.iloc[j]
            close_j = px(bar.get("Close", np.nan), np.nan)
            high_j = px(bar.get("High", np.nan), close_j)
            low_j = px(bar.get("Low", np.nan), close_j)
            ma20_j = px(bar.get("MA20", np.nan), np.nan)
            if not np.isfinite(close_j):
                continue

            # ① 구조적 손절. 가장 보수적으로 2차 손절을 먼저 검사.
            if remaining > 0 and low_j <= stop2:
                fill = stop2 * (1 - slippage_per_side)
                realized += net_return(fill, remaining)
                stop2_hit = True
                exit_reason = "2차 손절"
                remaining = 0.0
                exit_i = j
                break

            if remaining > 0 and (not stop1_hit) and low_j <= stop1:
                fill = stop1 * (1 - slippage_per_side)
                cut = min(0.5, remaining)
                realized += net_return(fill, cut)
                remaining -= cut
                stop1_hit = True
                # 같은 봉의 TP는 인정하지 않는다.
                if j == last_i and remaining > 0:
                    fill = close_j * (1 - slippage_per_side)
                    realized += net_return(fill, remaining)
                    remaining = 0.0
                    exit_reason = "1차 손절·기간만료"
                    exit_i = j
                    break
                continue

            # ② 2R 도달 이후에는 다음 봉부터 20일선 추적손절을 활성화.
            if trail_active and remaining > 0 and np.isfinite(ma20_j) and ma20_j > 0:
                trail_stop = ma20_j * 0.99
                if low_j <= trail_stop:
                    fill = trail_stop * (1 - slippage_per_side)
                    realized += net_return(fill, remaining)
                    trail_hit = True
                    exit_reason = "20일선 추적손절"
                    remaining = 0.0
                    exit_i = j
                    break

            # ③ 2R: 남은 물량의 절반(초기 포지션 기준 25%)만 익절.
            if remaining > 0 and (not tp2_hit) and high_j >= tp2:
                fill = tp2 * (1 - slippage_per_side)
                cut = min(0.5, remaining)
                realized += net_return(fill, cut)
                remaining -= cut
                tp2_hit = True
                trail_active = remaining > 0
                # 같은 봉의 추적손절은 장중 순서를 알 수 없으므로 다음 봉부터 적용.
                continue

            # ④ 1R: 최초 물량의 절반 익절.
            if remaining > 0 and (not tp1_hit) and high_j >= tp1:
                fill = tp1 * (1 - slippage_per_side)
                cut = min(0.5, remaining)
                realized += net_return(fill, cut)
                remaining -= cut
                tp1_hit = True
                if remaining <= 0:
                    exit_reason = "1R 익절"
                    exit_i = j
                    break

            # ⑤ 최대 보유기간 종료.
            if j == last_i and remaining > 0:
                fill = close_j * (1 - slippage_per_side)
                realized += net_return(fill, remaining)
                remaining = 0.0
                if trail_active:
                    exit_reason = "추적손절·기간만료"
                elif tp2_hit:
                    exit_reason = "2R 후 기간만료"
                elif tp1_hit:
                    exit_reason = "1R 후 기간만료"
                else:
                    exit_reason = "기간만료"
                exit_i = j
                break

        cash *= (1 + realized)
        exit_date = d.index[exit_i]
        next_available = exit_date + pd.Timedelta(days=1)

        trades.append({
            "신호일": signal_date.date(),
            "진입일": d.index[entry_i].date(),
            "청산일": exit_date.date(),
            "ETF": ticker,
            "테마": sig["테마"],
            "테마점수": float(sig["테마점수"]),
            "선행점수": int(sig["선행점수"]),
            "진입가": entry_fill,
            "1차익절": tp1,
            "2차익절": tp2,
            "1차손절": stop1,
            "2차손절": stop2,
            "R": lv["risk"],
            "1R도달": tp1_hit,
            "2R도달": tp2_hit,
            "1차손절도달": stop1_hit,
            "2차손절도달": stop2_hit,
            "20일선추적손절": trail_hit,
            "청산사유": exit_reason,
            "보유거래일": int(exit_i - entry_i + 1),
            "순수익률": realized * 100,
            "거래후자산": cash,
        })

    td = pd.DataFrame(trades)
    if td.empty:
        return td, {
            "초기자산": initial_cash, "최종자산": initial_cash,
            "총수익률": 0.0, "거래수": 0, "승률": np.nan,
            "최대낙폭": 0.0, "연환산": np.nan,
        }

    curve = td[["청산일", "거래후자산"]].copy()
    curve["청산일"] = pd.to_datetime(curve["청산일"])
    curve["고점"] = curve["거래후자산"].cummax()
    curve["낙폭"] = (curve["거래후자산"] / curve["고점"] - 1) * 100

    final_cash = float(td.iloc[-1]["거래후자산"])
    total_ret = (final_cash / initial_cash - 1) * 100
    days = max(1, (curve["청산일"].iloc[-1] - curve["청산일"].iloc[0]).days)
    annualized = ((final_cash / initial_cash) ** (365.25 / days) - 1) * 100 if final_cash > 0 else -100

    wins = int((td["순수익률"] > 0).sum())
    avg_win = td.loc[td["순수익률"] > 0, "순수익률"].mean()
    avg_loss = td.loc[td["순수익률"] <= 0, "순수익률"].mean()
    gross_profit = td.loc[td["순수익률"] > 0, "순수익률"].sum()
    gross_loss = -td.loc[td["순수익률"] < 0, "순수익률"].sum()

    metrics = {
        "초기자산": initial_cash,
        "최종자산": final_cash,
        "총수익률": total_ret,
        "연환산": annualized,
        "거래수": len(td),
        "승률": wins / len(td) * 100,
        "평균승리": avg_win,
        "평균손실": avg_loss,
        "손익비": (abs(avg_win / avg_loss) if pd.notna(avg_win) and pd.notna(avg_loss) and avg_loss != 0 else np.nan),
        "ProfitFactor": (gross_profit / gross_loss if gross_loss > 0 else np.inf),
        "기대값": td["순수익률"].mean(),
        "최대낙폭": float(curve["낙폭"].min()),
        "1R도달률": td["1R도달"].mean() * 100,
        "2R도달률": td["2R도달"].mean() * 100,
        "1차손절률": td["1차손절도달"].mean() * 100,
        "2차손절률": td["2차손절도달"].mean() * 100,
        "추적손절률": td["20일선추적손절"].mean() * 100,
        "평균보유일": td["보유거래일"].mean(),
    }
    return td, metrics


# ============================================================
# 16. 실전 체결형 C/D 검증 UI V6
# ============================================================
st.markdown("---")
st.header("🧪 실전 체결형 C/D 백테스트 V7")
st.caption("C/D 신호 → 다음 거래일 시가 진입 → 1R 50% · 2R 추가 25% · 20일선 추적손절 → 1/2차 손절 → 비용·슬리피지 → 최대 250거래일을 실제 체결에 가깝게 재현합니다.")

v6c1,v6c2,v6c3,v6c4 = st.columns(4)
v7_cash = v6c1.number_input("V7 초기자금", min_value=100000, value=1000000, step=100000, key="v7_cash")
v7_fee = v6c2.number_input("편도 비용(%)", min_value=0.0, max_value=1.0, value=0.10, step=0.01, key="v7_fee")
v7_slip = v6c3.number_input("편도 슬리피지(%)", min_value=0.0, max_value=1.0, value=0.05, step=0.01, key="v7_slip")
v7_hold = v6c4.number_input("최대 보유일", min_value=20, max_value=250, value=250, step=10, key="v7_hold")

if st.button("🚀 실전형 C/D 검증 실행 V7", type="primary", use_container_width=True):
    # 이 버튼 하나만 눌러도 선행 C/D 백테스트를 자동 계산한다.
    v7r = st.session_state.get("strategy_result")
    v7data = st.session_state.get("strategy_data")
    try:
        if v7r is None or v7data is None:
            with st.spinner("① C/D 신호를 먼저 계산하는 중..."):
                result, data = run_strategy_backtest(
                    date(2021, 1, 1), date(2025, 12, 31),
                    ["QQQ", "XLK", "SMH", "SOXX", "BOTZ", "ARKQ", "GLD", "TLT", "INDA", "EWY", "EWJ", "EEM"],
                    5
                )
                st.session_state["strategy_result"] = result
                st.session_state["strategy_data"] = data
                v7r, v7data = result, data

        with st.spinner("② V7 청산 규칙을 실제 체결 순서로 재생하는 중..."):
            v7trades, v7m = simulate_cd_trade_v7(
                v7r, v7data,
                initial_cash=float(v7_cash),
                fee_per_side=float(v7_fee) / 100,
                slippage_per_side=float(v7_slip) / 100,
                max_hold_days=int(v7_hold),
            )
            st.session_state["v7_trades"] = v7trades
            st.session_state["v7_metrics"] = v7m
            st.success(f"V7 실전형 검증 완료 · {v7m.get('거래수', 0)}건")
    except Exception as ex:
        st.error("V7 실전형 C/D 검증 중 오류가 발생했습니다.")
        st.exception(ex)

v7m = st.session_state.get("v7_metrics")
v7trades = st.session_state.get("v7_trades")
if v7m is not None:
    if v7m.get("거래수", 0) == 0:
        st.warning("실전형 조건을 만족하는 D 거래가 없습니다.")
    else:
        mc = st.columns(6)
        mc[0].metric("거래수", f"{v7m['거래수']}")
        mc[1].metric("최종자산", f"₩{v7m['최종자산']:,.0f}")
        mc[2].metric("총수익률", f"{v7m['총수익률']:+.1f}%")
        mc[3].metric("연환산", f"{v7m['연환산']:+.1f}%")
        mc[4].metric("승률", f"{v7m['승률']:.1f}%")
        mc[5].metric("MDD", f"{v7m['최대낙폭']:.1f}%")

        st.subheader("① 손익 구조")
        k1,k2,k3,k4,k5 = st.columns(5)
        k1.metric("평균 승리", f"{v7m['평균승리']:+.2f}%" if pd.notna(v7m['평균승리']) else "-")
        k2.metric("평균 손실", f"{v7m['평균손실']:+.2f}%" if pd.notna(v7m['평균손실']) else "-")
        k3.metric("손익비", f"{v7m['손익비']:.2f}" if pd.notna(v7m['손익비']) else "-")
        k4.metric("Profit Factor", f"{v7m['ProfitFactor']:.2f}" if np.isfinite(v7m['ProfitFactor']) else "∞")
        k5.metric("기대값/거래", f"{v7m['기대값']:+.2f}%")

        st.subheader("② 실제 청산 원인")
        reason = v7trades["청산사유"].value_counts().rename_axis("청산사유").reset_index(name="건수")
        reason["비율"] = reason["건수"] / len(v7trades) * 100
        st.dataframe(reason, use_container_width=True, hide_index=True,
                     column_config={"비율": st.column_config.NumberColumn(format="%.1f%%")})

        st.subheader("③ 1R / 2R / 손절 도달률")
        rr = pd.DataFrame([{
            "1R 도달": v7m["1R도달률"], "2R 도달": v7m["2R도달률"],
            "1차 손절": v7m["1차손절률"], "2차 손절": v7m["2차손절률"],
            "20일선 추적손절": v7m["추적손절률"],
            "평균 보유일": v7m["평균보유일"],
        }])
        st.dataframe(rr, use_container_width=True, hide_index=True,
                     column_config={
                         "1R 도달": st.column_config.NumberColumn(format="%.1f%%"),
                         "2R 도달": st.column_config.NumberColumn(format="%.1f%%"),
                         "1차 손절": st.column_config.NumberColumn(format="%.1f%%"),
                         "2차 손절": st.column_config.NumberColumn(format="%.1f%%"),
                         "평균 보유일": st.column_config.NumberColumn(format="%.1f"),
                     })

        st.subheader("④ 연도별 실전 성과")
        yr = v7trades.copy()
        yr["연도"] = pd.to_datetime(yr["청산일"]).dt.year
        yrows=[]
        for y,g in yr.groupby("연도"):
            vals=g["순수익률"]
            yrows.append({"연도":int(y),"거래수":len(g),"승률":(vals>0).mean()*100,
                          "평균수익":vals.mean(),"누적단순수익":vals.sum(),"평균보유일":g["보유거래일"].mean()})
        st.dataframe(pd.DataFrame(yrows),use_container_width=True,hide_index=True,
                     column_config={"승률":st.column_config.NumberColumn(format="%.1f%%"),
                                    "평균수익":st.column_config.NumberColumn(format="%+.2f%%"),
                                    "누적단순수익":st.column_config.NumberColumn(format="%+.2f%%"),
                                    "평균보유일":st.column_config.NumberColumn(format="%.1f")})

        st.subheader("⑤ 전체 거래내역")
        st.dataframe(v7trades, use_container_width=True, hide_index=True, height=520)

        # V7 결과를 CSV로 바로 다운로드할 수 있도록 제공
        csv_bytes = v7trades.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            "📥 V7 실전형 C/D 거래내역 CSV 다운로드",
            data=csv_bytes,
            file_name="ETF_RADAR_CD_LIVE_BACKTEST_V7.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_v7_trade_csv",
        )
        st.download_button("📥 실전형 C/D 거래내역 CSV", v7trades.to_csv(index=False).encode("utf-8-sig"),
                           "ETF_RADAR_CD_LIVE_BACKTEST_V7.csv", "text/csv", use_container_width=True)
