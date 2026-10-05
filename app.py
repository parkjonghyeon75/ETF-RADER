# -*- coding: utf-8 -*-
"""
ETF RADAR TRUE WALK-FORWARD BACKTEST
====================================

목적
----
기존 백테스트의 가장 큰 문제를 수정한다.

기존:
    고정 미국 ETF 테마군(BT_THEME_GROUPS) 사용

이번 버전:
    ETF RADAR 실제 THEME_LEXICON 방식 사용
    -> 국내 ETF universe
    -> 과거 날짜 기준 가격만 사용
    -> 테마점수 계산
    -> 선행 ETF 선정
    -> C / D / D+M 비교
    -> 다음 거래일 시가 진입
    -> 미래 가격은 오직 성과 계산에만 사용

중요
----
현재 ETF universe의 종목명을 과거에도 사용한다.
따라서 '생존자 편향(survivorship bias)'은 별도 주의가 필요하다.

실행:
    python ETF_RADAR_TRUE_WALK_FORWARD.py

필수:
    pip install yfinance pandas numpy requests
"""

from pathlib import Path
from datetime import datetime
import json
import html
import re
import warnings

import numpy as np
import pandas as pd
import requests
import yfinance as yf

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent

START_DATE = "2018-01-01"
END_DATE = "2026-10-01"

BENCHMARK = "069500.KS"   # KODEX 200

INITIAL_CASH = 1_000_000

HOLD_DAYS = 60

FEE_PER_SIDE = 0.0010
SLIPPAGE_PER_SIDE = 0.0005

STEP_DAYS = 5

MIN_THEME_MEMBERS = 2
MAX_THEME_MEMBERS = 8
MAX_ETFS_PER_THEME = 5

OOS_START_YEAR = 2024

THEME_LEXICON = {
    "AI 반도체": ["반도체", "AI반도체", "AI 반도체", "HBM", "메모리", "시스템반도체", "반도체장비", "반도체소부장"],
    "로봇": ["로봇", "로보틱스", "휴머노이드", "로보틱", "스마트팩토리"],
    "방산": ["방산", "방위산업", "K방산", "국방", "우주항공방산"],
    "2차전지": ["2차전지", "이차전지", "배터리", "전고체", "양극재", "음극재", "리튬", "배터리소재"],
    "전기차": ["전기차", "EV", "전기자동차", "자율주행", "모빌리티"],
    "조선": ["조선", "조선업", "선박", "LNG선", "해운", "선박기자재"],
    "원자력": ["원자력", "원전", "SMR", "소형모듈원전", "핵융합"],
    "전력 인프라": ["전력", "전력인프라", "전력설비", "전력망", "변압기", "전선", "송배전", "전기설비"],
    "데이터센터·AI 인프라": ["데이터센터", "AI인프라", "AI 인프라", "서버", "네트워크", "클라우드", "IDC"],
    "냉각·열관리": ["냉각", "열관리", "액침냉각", "수랭", "칠러", "열교환", "냉동공조"],
    "바이오": ["바이오", "헬스케어", "제약", "신약", "항암", "면역", "의료기기", "유전체"],
    "우주항공": ["우주", "우주항공", "항공우주", "위성", "발사체", "UAM"],
    "AI 소프트웨어": ["AI", "인공지능", "생성AI", "AI소프트웨어", "소프트웨어", "빅데이터"],
    "클라우드": ["클라우드", "SaaS", "데이터센터"],
    "보안": ["보안", "사이버보안", "정보보안", "보안솔루션"],
    "5G·통신": ["5G", "6G", "통신", "네트워크", "위성통신"],
    "신재생에너지": ["태양광", "태양광발전", "풍력", "신재생", "친환경에너지", "수소"],
    "수소": ["수소", "수소경제", "수소연료전지", "연료전지"],
    "친환경·탄소": ["탄소", "탄소중립", "친환경", "ESG", "폐기물", "리사이클", "재활용"],
    "금융": ["은행", "금융", "증권", "보험", "고배당", "배당"],
    "자동차": ["자동차", "자동차부품", "차량", "모빌리티"],
    "화장품·K뷰티": ["화장품", "K뷰티", "뷰티", "미용"],
    "음식료·소비": ["음식료", "식품", "소비재", "유통", "소비"],
    "건설·인프라": ["건설", "인프라", "SOC", "건설기계", "시멘트"],
    "철강·금속": ["철강", "금속", "구리", "알루미늄", "비철금속"],
    "원자재": ["원자재", "상품", "원유", "천연가스", "커머디티"],
    "금·귀금속": ["금", "골드", "귀금속", "은", "실버"],
    "중국": ["중국", "차이나", "CSI", "홍콩", "상하이"],
    "미국 기술": ["나스닥", "미국테크", "미국기술", "S&P500", "테크"],
    "반도체 장비·소부장": ["반도체장비", "반도체장비주", "소부장", "소재부품장비", "장비"],
}


def safe_float(x, default=np.nan):
    try:
        v = float(x)
        return v if np.isfinite(v) else default
    except Exception:
        return default


def normalize_code(x):
    s = str(x or "").strip().upper()
    if s.isdigit():
        return s.zfill(6)
    return s


def clean_name(x):
    s = html.unescape(str(x or "")).strip()
    if not s:
        return ""
    if any(ch in s for ch in ["Ã", "Â", "â", "�"]):
        return ""
    return s


def fetch_naver_etf_master():
    url = "https://finance.naver.com/api/sise/etfItemList.nhn"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://finance.naver.com/sise/etf.nhn",
    }

    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()

    try:
        payload = r.json()
    except Exception:
        payload = json.loads(
            r.content.decode("cp949", errors="ignore")
        )

    items = payload.get("result", {}).get("etfItemList", [])

    out = {}

    for item in items:
        code = normalize_code(item.get("itemcode"))
        name = clean_name(item.get("itemname"))

        if code and name:
            out[code] = name

    return out


def theme_hits(name, keywords):
    text = str(name).replace(" ", "").lower()

    return sum(
        1
        for k in keywords
        if str(k).replace(" ", "").lower() in text
    )


def build_theme_universe(universe):
    theme_members = {}

    for theme, keywords in THEME_LEXICON.items():

        ranked = []

        for code, name in universe.items():

            hits = theme_hits(name, keywords)

            if hits > 0:
                ranked.append(
                    (
                        hits,
                        code,
                        name
                    )
                )

        ranked.sort(
            key=lambda x: (x[0], x[2]),
            reverse=True
        )

        members = [
            x[0:3]
            for x in ranked[:MAX_THEME_MEMBERS]
        ]

        if len(members) >= MIN_THEME_MEMBERS:
            theme_members[theme] = members

    return theme_members


def download_prices(codes):
    tickers = [f"{c}.KS" for c in codes]

    # benchmark
    tickers.append(BENCHMARK)

    tickers = list(dict.fromkeys(tickers))

    print(f"가격 데이터 다운로드: {len(tickers)}개")

    raw = yf.download(
        tickers,
        start="2017-01-01",
        end=END_DATE,
        auto_adjust=True,
        progress=False,
        threads=True,
        group_by="ticker",
    )

    data = {}

    for ticker in tickers:

        try:

            if len(tickers) == 1:
                d = raw.copy()
            else:
                d = raw[ticker].copy()

            if d.empty:
                continue

            d.columns = [
                str(c)
                for c in d.columns
            ]

            d["Close"] = pd.to_numeric(
                d["Close"],
                errors="coerce"
            )

            d["Open"] = pd.to_numeric(
                d.get("Open"),
                errors="coerce"
            )

            d["Volume"] = pd.to_numeric(
                d.get("Volume"),
                errors="coerce"
            )

            d = d.dropna(
                subset=["Close"]
            )

            if len(d) >= 260:
                data[ticker] = d

        except Exception:
            continue

    return data


def add_indicators(d):
    d = d.copy()

    close = d["Close"]

    d["MA20"] = close.rolling(20).mean()
    d["MA60"] = close.rolling(60).mean()
    d["MA120"] = close.rolling(120).mean()

    d["R5"] = close.pct_change(5) * 100
    d["R20"] = close.pct_change(20) * 100
    d["R60"] = close.pct_change(60) * 100

    d["VOL20"] = d["Volume"].rolling(20).mean()
    d["VR"] = d["Volume"] / d["VOL20"]

    delta = close.diff()

    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()

    rs = gain / loss.replace(0, np.nan)

    d["RSI"] = 100 - 100 / (1 + rs)

    d["LOW20"] = close.rolling(20).min()

    return d


def leading_signal(row, benchmark_ret20):
    current = safe_float(row.get("Close"))
    ma20 = safe_float(row.get("MA20"), current)
    ma60 = safe_float(row.get("MA60"), current)

    r5 = safe_float(row.get("R5"), 0)
    r20 = safe_float(row.get("R20"), 0)
    vr = safe_float(row.get("VR"), 1)
    rsi = safe_float(row.get("RSI"), 50)

    if not np.isfinite(ma20) or ma20 == 0:
        return None

    dist20 = (current / ma20 - 1) * 100
    rs20 = r20 - benchmark_ret20
    accel = r5 - r20 / 4

    early_price = (
        92 if -1 <= dist20 <= 3
        else 82 if dist20 <= 5
        else 65 if dist20 < 8
        else 35
    )

    early_rsi = (
        92 if 48 <= rsi <= 62
        else 84 if 43 <= rsi < 68
        else 68 if rsi < 72
        else 35
    )

    flow = (
        92 if 1.10 <= vr <= 1.70
        else 82 if 1.0 <= vr < 1.10
        else 76 if 0.9 <= vr < 1.0
        else 58 if vr < 2.2
        else 38
    )

    accel_score = (
        90 if 0.5 <= accel <= 5
        else 78 if 0 <= accel < 0.5
        else 68 if accel > 5
        else 52
    )

    rel = (
        88 if rs20 >= 6
        else 80 if rs20 >= 3
        else 70 if rs20 >= 0
        else 48
    )

    structure = (
        90 if current >= ma60 and ma20 >= ma60
        else 78 if current >= ma60
        else 55 if current >= ma20
        else 35
    )

    score = round(
        early_price * 0.22
        + early_rsi * 0.18
        + flow * 0.22
        + accel_score * 0.16
        + rel * 0.14
        + structure * 0.08
    )

    early_buy = (
        score >= 72
        and vr >= 1.05
        and rsi < 70
        and dist20 < 7
        and rs20 >= -1
    )

    return {
        "score": int(np.clip(score, 0, 100)),
        "early_buy": bool(early_buy),
        "rs20": rs20,
        "dist20": dist20,
        "rsi": rsi,
        "vr": vr,
        "accel": accel,
    }


def price_zone(row):
    c = safe_float(row.get("Close"))
    ma20 = safe_float(row.get("MA20"))
    ma60 = safe_float(row.get("MA60"))
    low20 = safe_float(row.get("LOW20"))

    if not all(
        np.isfinite(x)
        for x in [c, ma20, ma60, low20]
    ):
        return {"state": "무효"}

    support = max(
        low20,
        ma20 * 0.985
    )

    ideal_top = ma20 * 1.025

    invalid = min(
        ma60 * 0.97,
        support * 0.97
    )

    if (
        c <= ideal_top
        and c >= invalid
        and c >= ma60 * 0.98
    ):
        state = "매수구간"

    elif c < invalid:
        state = "무효"

    elif c > ma20 * 1.07:
        state = "추격금지"

    else:
        state = "눌림대기"

    return {
        "state": state,
        "support": support,
        "ideal_top": ideal_top,
        "invalid": invalid,
    }


def score_theme(rows, bench20, bench60):
    if len(rows) < MIN_THEME_MEMBERS:
        return None

    vals = []

    for row in rows:

        r20 = safe_float(row.get("R20"))
        r60 = safe_float(row.get("R60"))

        if not np.isfinite(r20) or not np.isfinite(r60):
            continue

        sig = leading_signal(
            row,
            bench20
        )

        if sig is None:
            continue

        vals.append({
            "r20": r20,
            "r60": r60,
            "rs20": sig["rs20"],
            "rs60": r60 - bench60,
            "vr": safe_float(row.get("VR"), 1),
            "ma60gap": (
                safe_float(row.get("Close"))
                / safe_float(row.get("MA60"))
                - 1
            ) * 100,
            "accel": sig["accel"],
            "rsi": sig["rsi"],
            "lead": sig["score"],
            "early": sig["early_buy"],
        })

    if len(vals) < MIN_THEME_MEMBERS:
        return None

    x = pd.DataFrame(vals)

    def clip_score(v, lo, hi):
        return float(
            np.clip(
                (v - lo) / (hi - lo) * 100,
                0,
                100
            )
        )

    r20 = clip_score(x["r20"].mean(), -10, 15)
    r60 = clip_score(x["r60"].mean(), -15, 30)

    rs20 = clip_score(x["rs20"].mean(), -10, 12)
    rs60 = clip_score(x["rs60"].mean(), -15, 20)

    vr = clip_score(x["vr"].mean(), 0.8, 2.0)

    breadth = (
        (x["r20"] > -2).mean()
        * 100
    )

    ma60 = clip_score(
        x["ma60gap"].mean(),
        -10,
        15
    )

    accel = clip_score(
        x["accel"].mean(),
        -5,
        6
    )

    rsi = float(
        np.clip(
            100
            - abs(
                float(x["rsi"].mean())
                - 58
            ) * 2.5,
            0,
            100
        )
    )

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

    lead_theme = (
        x["lead"].mean() * 0.55
        + breadth * 0.25
        + x["early"].mean() * 100 * 0.20
    )

    final = (
        score * 0.70
        + lead_theme * 0.30
    )

    heat = 0

    if x["rsi"].mean() >= 75:
        heat += 12

    if x["r20"].mean() >= 12:
        heat += 10

    if x["ma60gap"].mean() >= 15:
        heat += 8

    final = float(
        np.clip(
            final - heat,
            0,
            100
        )
    )

    return {
        "score": final,
        "members": len(x),
        "breadth": breadth,
        "lead_avg": float(x["lead"].mean()),
        "early_ratio": float(x["early"].mean()),
        "heat": heat,
    }


def build_snapshot(
    date,
    data,
    theme_members
):
    """
    신호일 현재까지 존재하는 데이터만 사용한다.
    미래 데이터는 절대 사용하지 않는다.
    """

    bench = data.get(BENCHMARK)

    if bench is None:
        return None

    if date not in bench.index:
        return None

    b = bench.loc[:date]

    if len(b) < 65:
        return None

    br = b.iloc[-1]

    bench20 = safe_float(
        br.get("R20")
    )

    bench60 = safe_float(
        br.get("R60")
    )

    if not np.isfinite(bench20):
        return None

    if not np.isfinite(bench60):
        return None

    theme_results = []

    for theme, members in theme_members.items():

        rows = []

        for _, code, name in members:

            ticker = f"{code}.KS"

            d = data.get(ticker)

            if d is None or d.empty:
                continue

            hist = d.loc[:date]

            if len(hist) < 65:
                continue

            row = hist.iloc[-1]

            if (
                pd.isna(row.get("MA60"))
                or pd.isna(row.get("R20"))
                or pd.isna(row.get("R60"))
            ):
                continue

            z = row.to_dict()

            z["ETF"] = ticker
            z["CODE"] = code
            z["NAME"] = name

            rows.append(z)

        if len(rows) < MIN_THEME_MEMBERS:
            continue

        ts = score_theme(
            rows,
            bench20,
            bench60
        )

        if ts is None:
            continue

        ts["theme"] = theme
        ts["rows"] = rows

        theme_results.append(ts)

    if not theme_results:
        return None

    theme_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    top = theme_results[0]

    candidates = []

    for row in top["rows"]:

        sig = leading_signal(
            row,
            bench20
        )

        if sig is None:
            continue

        zone = price_zone(row)

        # 현재 앱의 선행 ETF 선택 개념을 유지
        final_score = (
            sig["score"] * 0.65
            + top["score"] * 0.35
        )

        candidates.append({
            "ETF": row["ETF"],
            "CODE": row["CODE"],
            "NAME": row["NAME"],
            "score": final_score,
            "sig": sig,
            "zone": zone,
        })

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    winner = candidates[0]

    return {
        "theme": top["theme"],
        "theme_score": top["score"],
        "winner": winner,
        "themes": theme_results,
    }


def simulate_strategy(
    signals,
    data,
    flag,
    initial_cash=INITIAL_CASH,
    hold_days=HOLD_DAYS
):
    """
    동일 체결엔진:
    - 신호일 종가까지 정보 사용
    - 다음 거래일 시가 진입
    - 고정 보유기간
    - 수수료/슬리피지
    - 보유 중 새 신호 무시
    """

    if signals.empty:
        return pd.DataFrame(), {}

    x = signals[
        signals[flag].fillna(False)
    ].sort_values("날짜")

    cash = float(initial_cash)

    next_available = pd.Timestamp.min

    trades = []

    for _, sig in x.iterrows():

        signal_date = pd.Timestamp(
            sig["날짜"]
        )

        if signal_date < next_available:
            continue

        ticker = sig["ETF"]

        d = data.get(ticker)

        if d is None or d.empty:
            continue

        if signal_date not in d.index:
            continue

        pos = d.index.get_loc(
            signal_date
        )

        entry_i = pos + 1
        exit_i = (
            entry_i
            + hold_days
            - 1
        )

        if exit_i >= len(d):
            continue

        entry = safe_float(
            d.iloc[entry_i].get("Open")
        )

        exit_price = safe_float(
            d.iloc[exit_i].get("Close")
        )

        if (
            not np.isfinite(entry)
            or not np.isfinite(exit_price)
            or entry <= 0
        ):
            continue

        buy = (
            entry
            * (1 + SLIPPAGE_PER_SIDE)
        )

        sell = (
            exit_price
            * (1 - SLIPPAGE_PER_SIDE)
        )

        net = (
            sell / buy
            - 1
            - FEE_PER_SIDE * 2
        )

        before = cash

        cash *= 1 + net

        future_window = d.iloc[
            entry_i:exit_i + 1
        ]

        mfe = (
            future_window["High"].max()
            / entry
            - 1
        ) * 100

        mae = (
            future_window["Low"].min()
            / entry
            - 1
        ) * 100

        trades.append({
            "신호일": signal_date.date(),
            "진입일": d.index[entry_i].date(),
            "청산일": d.index[exit_i].date(),
            "테마": sig["테마"],
            "ETF": ticker,
            "ETF명": sig["ETF명"],
            "테마점수": sig["테마점수"],
            "선행점수": sig["선행점수"],
            "가격상태": sig["가격상태"],
            "진입가": entry,
            "청산가": exit_price,
            "MFE": mfe,
            "MAE": mae,
            "순수익률": net * 100,
            "거래후자산": cash,
        })

        next_available = (
            d.index[exit_i]
            + pd.Timedelta(days=1)
        )

    td = pd.DataFrame(trades)

    if td.empty:
        return td, {
            "거래수": 0,
            "총수익률": 0,
            "CAGR": np.nan,
            "MDD": 0,
            "승률": np.nan,
            "Profit Factor": np.nan,
        }

    equity = td["거래후자산"]

    peak = equity.cummax()

    dd = (
        equity / peak
        - 1
    ) * 100

    total = (
        cash / initial_cash
        - 1
    ) * 100

    start = pd.Timestamp(
        td["청산일"].iloc[0]
    )

    end = pd.Timestamp(
        td["청산일"].iloc[-1]
    )

    years = max(
        1 / 365.25,
        (end - start).days
        / 365.25
    )

    cagr_value = (
        (cash / initial_cash)
        ** (1 / years)
        - 1
    ) * 100

    r = td["순수익률"]

    wins = r[r > 0]
    losses = r[r < 0]

    gain = wins.sum()
    loss = abs(losses.sum())

    pf = (
        gain / loss
        if loss > 0
        else np.inf
        if gain > 0
        else np.nan
    )

    return td, {
        "거래수": len(td),
        "총수익률": total,
        "CAGR": cagr_value,
        "MDD": dd.min(),
        "승률": (
            (r > 0).mean()
            * 100
        ),
        "Profit Factor": pf,
        "평균거래수익": r.mean(),
        "평균MFE": td["MFE"].mean(),
        "평균MAE": td["MAE"].mean(),
    }


def make_signal_rows(
    dates,
    data,
    theme_members
):
    rows = []

    for i, date in enumerate(dates):

        if i % 50 == 0:
            print(
                f"검사 {i + 1:,}/{len(dates):,}"
            )

        snap = build_snapshot(
            date,
            data,
            theme_members
        )

        if snap is None:
            continue

        winner = snap["winner"]

        ticker = winner["ETF"]

        d = data.get(ticker)

        if d is None or d.empty:
            continue

        if date not in d.index:
            continue

        pos = d.index.get_loc(date)

        if pos + HOLD_DAYS >= len(d):
            continue

        sig = winner["sig"]

        zone = winner["zone"]

        c_ok = (
            snap["theme_score"] >= 60
            and sig["score"] >= 72
            and sig["early_buy"]
        )

        d_ok = (
            c_ok
            and zone["state"]
            == "매수구간"
        )

        # 시장환경:
        # 신호일 현재 KODEX200이 MA60/MA120 위이고
        # 20일 수익률 >= 0
        bench = data[BENCHMARK]
        bp = bench.loc[:date]

        market_ok = False

        if len(bp) >= 120:

            br = bp.iloc[-1]

            market_ok = bool(
                safe_float(
                    br.get("Close")
                )
                >= safe_float(
                    br.get("MA60")
                )
                and safe_float(
                    br.get("Close")
                )
                >= safe_float(
                    br.get("MA120")
                )
                and safe_float(
                    br.get("R20")
                ) >= 0
            )

        dm_ok = (
            d_ok
            and market_ok
        )

        rows.append({
            "날짜": date.date(),
            "테마": snap["theme"],
            "테마점수": snap["theme_score"],
            "ETF": ticker,
            "ETF명": winner["NAME"],
            "선행점수": sig["score"],
            "과열방지": sig["early_buy"],
            "가격상태": zone["state"],
            "A_테마선정": True,
            "C_미래테마선행": c_ok,
            "D_미래테마선행가격": d_ok,
            "D+M_시장환경": dm_ok,
        })

    return pd.DataFrame(rows)


def annual_report(trades, strategy):
    if trades.empty:
        return pd.DataFrame()

    x = trades.copy()

    x["청산일"] = pd.to_datetime(
        x["청산일"]
    )

    x["연도"] = x["청산일"].dt.year

    rows = []

    for year, g in x.groupby("연도"):

        r = g["순수익률"]

        wins = r[r > 0]
        losses = r[r < 0]

        rows.append({
            "전략": strategy,
            "연도": year,
            "거래수": len(g),
            "승률": (
                (r > 0).mean()
                * 100
            ),
            "평균수익": r.mean(),
            "누적복리수익": (
                (1 + r / 100).prod()
                - 1
            ) * 100,
            "Profit Factor": (
                wins.sum()
                / abs(losses.sum())
                if len(losses)
                else np.inf
            ),
        })

    return pd.DataFrame(rows)


def main():

    print("=" * 72)
    print("ETF RADAR TRUE WALK-FORWARD BACKTEST")
    print("=" * 72)

    # -------------------------------------------------------
    # 1. 실제 ETF master
    # -------------------------------------------------------

    print("\n[1] KRX/Naver ETF universe")

    universe = fetch_naver_etf_master()

    print(
        f"ETF universe: {len(universe):,}"
    )

    if len(universe) < 10:
        raise RuntimeError(
            "ETF universe를 가져오지 못했습니다."
        )

    theme_members = build_theme_universe(
        universe
    )

    print(
        f"자동 테마 수: {len(theme_members)}"
    )

    # -------------------------------------------------------
    # 2. 가격 데이터
    # -------------------------------------------------------

    codes = set()

    for members in theme_members.values():

        for _, code, _ in members:
            codes.add(code)

    print(
        f"백테스트 ETF 수: {len(codes):,}"
    )

    data = download_prices(
        sorted(codes)
    )

    data = {
        k: add_indicators(v)
        for k, v in data.items()
    }

    data = {
        k: v
        for k, v in data.items()
        if not v.empty
    }

    if BENCHMARK not in data:
        raise RuntimeError(
            "KODEX200 benchmark 데이터가 없습니다."
        )

    # -------------------------------------------------------
    # 3. 공통 날짜
    # -------------------------------------------------------

    common = data[BENCHMARK].index

    for members in theme_members.values():

        for _, code, _ in members:

            ticker = f"{code}.KS"

            if ticker in data:
                common = common.intersection(
                    data[ticker].index
                )

    common = common.sort_values()

    common = common[
        (common >= pd.Timestamp(START_DATE))
        & (common <= pd.Timestamp(END_DATE))
    ]

    # step
    dates = list(
        common[::STEP_DAYS]
    )

    print(
        f"검사 날짜: {len(dates):,}"
    )

    # -------------------------------------------------------
    # 4. 실제 앱 로직으로 신호 생성
    # -------------------------------------------------------

    print(
        "\n[2] 실제 미래테마 엔진 재생"
    )

    signals = make_signal_rows(
        dates,
        data,
        theme_members
    )

    if signals.empty:
        raise RuntimeError(
            "신호가 생성되지 않았습니다."
        )

    signals.to_csv(
        BASE_DIR
        / "ETF_RADAR_TRUE_WALK_FORWARD_SIGNALS.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"생성 신호: {len(signals):,}"
    )

    # -------------------------------------------------------
    # 5. 전략별 실제 거래
    # -------------------------------------------------------

    strategies = [
        (
            "C_미래테마선행",
            "C_미래테마선행"
        ),
        (
            "D_미래테마선행가격",
            "D_미래테마선행가격"
        ),
        (
            "D+M_시장환경",
            "D+M_시장환경"
        ),
    ]

    summary = []
    annual = []
    all_trades = []

    for strategy_name, flag in strategies:

        print(
            f"\n[3] {strategy_name}"
        )

        trades, metrics = simulate_strategy(
            signals,
            data,
            flag
        )

        if not trades.empty:

            trades.insert(
                0,
                "전략",
                strategy_name
            )

            all_trades.append(
                trades
            )

            a = annual_report(
                trades,
                strategy_name
            )

            annual.append(a)

        summary.append({
            "전략": strategy_name,
            "신호수": int(
                signals[flag].sum()
            ),
            **metrics
        })

        print(
            pd.Series(
                summary[-1]
            ).to_string()
        )

    summary_df = pd.DataFrame(
        summary
    )

    trades_df = (
        pd.concat(
            all_trades,
            ignore_index=True
        )
        if all_trades
        else pd.DataFrame()
    )

    annual_df = (
        pd.concat(
            annual,
            ignore_index=True
        )
        if annual
        else pd.DataFrame()
    )

    # -------------------------------------------------------
    # 6. OOS
    # -------------------------------------------------------

    oos_rows = []

    signals["연도"] = pd.to_datetime(
        signals["날짜"]
    ).dt.year

    for strategy_name, flag in strategies:

        oos_signals = signals[
            signals["연도"]
            >= OOS_START_YEAR
        ].copy()

        trades, metrics = simulate_strategy(
            oos_signals,
            data,
            flag
        )

        oos_rows.append({
            "전략": strategy_name,
            "OOS시작": OOS_START_YEAR,
            "신호수": int(
                oos_signals[flag].sum()
            ),
            **metrics
        })

    oos_df = pd.DataFrame(
        oos_rows
    )

    # -------------------------------------------------------
    # 7. 전략 독립성
    # -------------------------------------------------------

    overlap_rows = []

    for i in range(len(strategies)):

        for j in range(i + 1, len(strategies)):

            a = signals.loc[
                signals[strategies[i][1]],
                ["날짜", "ETF"]
            ]

            b = signals.loc[
                signals[strategies[j][1]],
                ["날짜", "ETF"]
            ]

            sa = set(
                map(
                    tuple,
                    a.values.tolist()
                )
            )

            sb = set(
                map(
                    tuple,
                    b.values.tolist()
                )
            )

            union = sa | sb

            inter = sa & sb

            overlap_rows.append({
                "전략A": strategies[i][0],
                "전략B": strategies[j][0],
                "신호A": len(sa),
                "신호B": len(sb),
                "공통신호": len(inter),
                "Jaccard": (
                    len(inter) / len(union)
                    if union
                    else np.nan
                )
            })

    overlap_df = pd.DataFrame(
        overlap_rows
    )

    # -------------------------------------------------------
    # 8. 비용 민감도
    # -------------------------------------------------------

    cost_rows = []

    global original_fee
    original_fee = FEE_PER_SIDE

    for cost in [
        0.0000,
        0.0005,
        0.0010,
        0.0020,
        0.0030,
    ]:

        # simulate 함수의 전역 비용을 임시 변경
        globals()["FEE_PER_SIDE"] = cost

        for strategy_name, flag in strategies:

            trades, metrics = simulate_strategy(
                signals,
                data,
                flag
            )

            cost_rows.append({
                "전략": strategy_name,
                "왕복비용": cost * 2 * 100,
                "거래수": metrics.get(
                    "거래수",
                    0
                ),
                "총수익률": metrics.get(
                    "총수익률",
                    np.nan
                ),
                "CAGR": metrics.get(
                    "CAGR",
                    np.nan
                ),
                "MDD": metrics.get(
                    "MDD",
                    np.nan
                ),
                "PF": metrics.get(
                    "Profit Factor",
                    np.nan
                ),
            })

    globals()["FEE_PER_SIDE"] = original_fee

    cost_df = pd.DataFrame(
        cost_rows
    )

    # -------------------------------------------------------
    # 9. 저장
    # -------------------------------------------------------

    summary_df.to_csv(
        BASE_DIR
        / "ETF_RADAR_TRUE_WALK_FORWARD_SUMMARY.csv",
        index=False,
        encoding="utf-8-sig"
    )

    annual_df.to_csv(
        BASE_DIR
        / "ETF_RADAR_TRUE_WALK_FORWARD_ANNUAL.csv",
        index=False,
        encoding="utf-8-sig"
    )

    trades_df.to_csv(
        BASE_DIR
        / "ETF_RADAR_TRUE_WALK_FORWARD_TRADES.csv",
        index=False,
        encoding="utf-8-sig"
    )

    oos_df.to_csv(
        BASE_DIR
        / "ETF_RADAR_TRUE_WALK_FORWARD_OOS.csv",
        index=False,
        encoding="utf-8-sig"
    )

    overlap_df.to_csv(
        BASE_DIR
        / "ETF_RADAR_TRUE_WALK_FORWARD_OVERLAP.csv",
        index=False,
        encoding="utf-8-sig"
    )

    cost_df.to_csv(
        BASE_DIR
        / "ETF_RADAR_TRUE_WALK_FORWARD_COST.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # -------------------------------------------------------
    # 10. 최종 판정
    # -------------------------------------------------------

    report = []

    report.append(
        "ETF RADAR TRUE WALK-FORWARD REPORT"
    )
    report.append("=" * 60)
    report.append(
        f"기간: {START_DATE} ~ {END_DATE}"
    )
    report.append(
        f"OOS: {OOS_START_YEAR}+"
    )
    report.append(
        f"보유기간: {HOLD_DAYS} 거래일"
    )
    report.append("")

    for _, row in summary_df.iterrows():

        report.append(
            f"{row['전략']} | "
            f"신호 {row['신호수']} | "
            f"거래 {row['거래수']} | "
            f"CAGR {row['CAGR']:.2f}% | "
            f"MDD {row['MDD']:.2f}% | "
            f"승률 {row['승률']:.2f}% | "
            f"PF {row['Profit Factor']:.2f}"
        )

    report.append("")
    report.append("OOS")
    report.append("-" * 60)

    for _, row in oos_df.iterrows():

        report.append(
            f"{row['전략']} | "
            f"거래 {row['거래수']} | "
            f"CAGR {row['CAGR']:.2f}% | "
            f"MDD {row['MDD']:.2f}% | "
            f"PF {row['Profit Factor']:.2f}"
        )

    report.append("")
    report.append(
        "주의: 현재 ETF master를 과거에도 적용하므로 "
        "생존자 편향 가능성이 있습니다."
    )

    report.append(
        "주의: 실제 앱의 현재 테마 자동발굴 방식과 동일한 "
        "THEME_LEXICON/가격지표 계산을 사용합니다."
    )

    with open(
        BASE_DIR
        / "ETF_RADAR_TRUE_WALK_FORWARD_REPORT.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(
            "\n".join(report)
        )

    print("\n")
    print("=" * 72)
    print("최종 결과")
    print("=" * 72)
    print(
        summary_df.to_string(
            index=False
        )
    )

    print("\nOOS")
    print(
        oos_df.to_string(
            index=False
        )
    )

    print("\n완료.")
    print(
        "ETF_RADAR_TRUE_WALK_FORWARD_SUMMARY.csv"
    )


if __name__ == "__main__":
    main()
