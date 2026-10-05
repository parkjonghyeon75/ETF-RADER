# -*- coding: utf-8 -*-
# ============================================================
# ETF RADAR - D 전략 검증 전용 LAB
# 목적:
#   1) D 전략의 2018~현재 장기 안정성 검증
#   2) 연도별 / 시장국면별 성과 확인
#   3) 승리/패배 거래의 공통점 확인
#   4) 테마점수 / 선행점수 / 과열점수 / 가격상태별 성과 확인
#   5) 검증 결과를 CSV로 저장
#
# 사용:
#   streamlit run ETF_RADAR_D_VALIDATION.py
#
# 같은 폴더에 다음 CSV가 있으면 자동 로드:
#   ETF_RADAR_BACKTEST_SIGNAL_DETAIL.csv
#   ETF_RADAR_FINAL_3_STRATEGY_TRADES.csv
#   ETF_RADAR_FINAL_3_STRATEGY_ANNUAL.csv
#   ETF_RADAR_FINAL_3_STRATEGY_COMPARISON.csv
# ============================================================

import os
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="ETF RADAR · D 전략 검증",
    page_icon="🔬",
    layout="wide",
)

# ------------------------------------------------------------
# 1. 파일 로드
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "signal": "ETF_RADAR_BACKTEST_SIGNAL_DETAIL.csv",
    "trades": "ETF_RADAR_FINAL_3_STRATEGY_TRADES.csv",
    "annual": "ETF_RADAR_FINAL_3_STRATEGY_ANNUAL.csv",
    "comparison": "ETF_RADAR_FINAL_3_STRATEGY_COMPARISON.csv",
}

def read_csv_auto(uploaded, filename):
    if uploaded is not None:
        return pd.read_csv(uploaded)

    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        return pd.read_csv(path)

    return None

signal_df = read_csv_auto(st.session_state.get("_upload_signal"), FILES["signal"])
trades_df = read_csv_auto(st.session_state.get("_upload_trades"), FILES["trades"])
annual_df = read_csv_auto(st.session_state.get("_upload_annual"), FILES["annual"])
comparison_df = read_csv_auto(st.session_state.get("_upload_comparison"), FILES["comparison"])

# ------------------------------------------------------------
# 2. 유틸
# ------------------------------------------------------------
def pct(x):
    if pd.isna(x):
        return "-"
    return f"{x:+.2f}%"

def num(x):
    if pd.isna(x):
        return "-"
    return f"{x:.2f}"

def classify_result(x):
    if pd.isna(x):
        return "미확정"
    if x >= 10:
        return "대승 (+10% 이상)"
    if x > 0:
        return "승리"
    if x <= -10:
        return "대손실 (-10% 이하)"
    return "손실"

def safe_float(s):
    return pd.to_numeric(s, errors="coerce")

# ------------------------------------------------------------
# 3. 헤더
# ------------------------------------------------------------
st.title("🔬 ETF RADAR — D 전략 검증 LAB")
st.caption(
    "D = 미래테마 + 선행 ETF + 가격구간. "
    "전략을 새로 만드는 화면이 아니라, 현재 D 가설이 실제로 견고한지 검증하는 화면입니다."
)

st.info(
    "검증 원칙: 먼저 D를 평가하고, 결과가 나쁘다고 임의의 필터를 추가하지 않습니다. "
    "손실 원인을 확인한 뒤 최소한의 가설만 만들고 다시 검증합니다."
)

# ------------------------------------------------------------
# 4. 업로드
# ------------------------------------------------------------
with st.expander("📂 CSV 파일 확인 / 교체", expanded=False):
    u1 = st.file_uploader("① 검사시점 상세 CSV", type="csv", key="up_signal")
    u2 = st.file_uploader("② 전략 거래 CSV", type="csv", key="up_trades")
    u3 = st.file_uploader("③ 연도별 성과 CSV", type="csv", key="up_annual")
    u4 = st.file_uploader("④ 전략 비교 CSV", type="csv", key="up_comparison")

    if u1 is not None:
        signal_df = pd.read_csv(u1)
    if u2 is not None:
        trades_df = pd.read_csv(u2)
    if u3 is not None:
        annual_df = pd.read_csv(u3)
    if u4 is not None:
        comparison_df = pd.read_csv(u4)

missing = []
if signal_df is None: missing.append(FILES["signal"])
if trades_df is None: missing.append(FILES["trades"])

if missing:
    st.error("필수 CSV가 없습니다: " + ", ".join(missing))
    st.stop()

# ------------------------------------------------------------
# 5. 날짜/숫자 정리
# ------------------------------------------------------------
signal_df["날짜"] = pd.to_datetime(signal_df["날짜"], errors="coerce")
trades_df["신호일"] = pd.to_datetime(trades_df["신호일"], errors="coerce")
trades_df["진입일"] = pd.to_datetime(trades_df["진입일"], errors="coerce")
trades_df["청산일"] = pd.to_datetime(trades_df["청산일"], errors="coerce")

for c in [
    "테마점수", "선행점수", "과열점수", "매수가",
    "5일수익", "5일최저낙폭",
    "20일수익", "20일최저낙폭",
    "60일수익", "60일최저낙폭",
]:
    if c in signal_df.columns:
        signal_df[c] = safe_float(signal_df[c])

trades_df["순수익률"] = safe_float(trades_df["순수익률"])

# ------------------------------------------------------------
# 6. D 거래만 추출
# ------------------------------------------------------------
d_trades = trades_df[
    trades_df["전략"].astype(str).str.startswith("D")
].copy()

if d_trades.empty:
    st.error("전략 거래 CSV에서 D 전략 거래를 찾지 못했습니다.")
    st.stop()

# 신호 상세와 D 거래를 ETF + 신호일로 연결
detail_cols = [
    "날짜", "테마", "테마점수", "테마단계", "ETF",
    "선행점수", "과열점수", "가격상태", "매수가",
    "5일수익", "5일최저낙폭",
    "20일수익", "20일최저낙폭",
    "60일수익", "60일최저낙폭",
]

detail_cols = [c for c in detail_cols if c in signal_df.columns]

d_detail = signal_df[detail_cols].copy()

merged = d_trades.merge(
    d_detail,
    left_on=["신호일", "ETF"],
    right_on=["날짜", "ETF"],
    how="left",
)

merged["보유일"] = (
    merged["청산일"] - merged["진입일"]
).dt.days

merged["결과"] = merged["순수익률"].apply(classify_result)
merged["연도"] = merged["신호일"].dt.year

# ------------------------------------------------------------
# 7. ① 현재 D의 기본 성적
# ------------------------------------------------------------
st.markdown("---")
st.header("① D 전략 현재 성적")

total_return = (np.prod(1 + merged["순수익률"].dropna() / 100) - 1) * 100
win_rate = (merged["순수익률"] > 0).mean() * 100
avg_return = merged["순수익률"].mean()
median_return = merged["순수익률"].median()

wins = merged.loc[merged["순수익률"] > 0, "순수익률"]
losses = merged.loc[merged["순수익률"] < 0, "순수익률"]

profit_factor = (
    wins.sum() / abs(losses.sum())
    if len(losses) and losses.sum() != 0
    else np.nan
)

equity = (1 + merged["순수익률"].fillna(0) / 100).cumprod()
mdd = ((equity / equity.cummax()) - 1).min() * 100

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("거래수", f"{len(merged)}")
c2.metric("누적복리", pct(total_return))
c3.metric("승률", f"{win_rate:.1f}%")
c4.metric("평균거래", pct(avg_return))
c5.metric("Profit Factor", f"{profit_factor:.2f}")
c6.metric("MDD", pct(mdd))

st.caption(
    "주의: 위 누적복리는 CSV에 기록된 D 거래 순서대로 단순 연속 재투자한 값입니다. "
    "원본 비교 CSV의 총수익률과 계산 정의가 다를 수 있으므로 두 값을 혼용하지 않습니다."
)

# ------------------------------------------------------------
# 8. ② 연도별 안정성
# ------------------------------------------------------------
st.markdown("---")
st.header("② 연도별 안정성 — 장기검증의 핵심")

annual_rows = []

for year, g in merged.groupby("연도"):
    r = g["순수익률"].dropna()

    if len(r) == 0:
        continue

    wins_y = r[r > 0]
    losses_y = r[r < 0]

    annual_rows.append({
        "연도": int(year),
        "거래수": len(r),
        "승률": (r > 0).mean() * 100,
        "평균수익": r.mean(),
        "중앙수익": r.median(),
        "최고수익": r.max(),
        "최대손실": r.min(),
        "Profit Factor": (
            wins_y.sum() / abs(losses_y.sum())
            if len(losses_y) and losses_y.sum() != 0 else np.nan
        ),
        "누적복리": ((1 + r / 100).prod() - 1) * 100,
    })

annual_check = pd.DataFrame(annual_rows).sort_values("연도")

st.dataframe(
    annual_check,
    use_container_width=True,
    hide_index=True,
    column_config={
        "승률": st.column_config.NumberColumn(format="%.1f%%"),
        "평균수익": st.column_config.NumberColumn(format="%+.2f%%"),
        "중앙수익": st.column_config.NumberColumn(format="%+.2f%%"),
        "최고수익": st.column_config.NumberColumn(format="%+.2f%%"),
        "최대손실": st.column_config.NumberColumn(format="%+.2f%%"),
        "Profit Factor": st.column_config.NumberColumn(format="%.2f"),
        "누적복리": st.column_config.NumberColumn(format="%+.2f%%"),
    },
)

# 자동 경고
bad_years = annual_check[
    (annual_check["거래수"] >= 2) &
    (annual_check["누적복리"] < 0)
]

if not bad_years.empty:
    st.warning(
        "⚠️ 손실 연도: "
        + ", ".join(str(int(x)) for x in bad_years["연도"])
        + " — 해당 연도의 거래를 별도로 분석해야 합니다."
    )

# ------------------------------------------------------------
# 9. ③ 승리 / 패배 거래 원인 분석
# ------------------------------------------------------------
st.markdown("---")
st.header("③ 승리·패배 거래의 공통점")

def group_analysis(df, col):
    if col not in df.columns:
        return pd.DataFrame()

    g = df.groupby(col, dropna=False)

    out = g["순수익률"].agg(
        거래수="count",
        평균수익="mean",
        중앙수익="median",
    ).reset_index()

    out["승률"] = g["순수익률"].apply(lambda x: (x > 0).mean() * 100).values
    out["최대손실"] = g["순수익률"].min().values
    out["최고수익"] = g["순수익률"].max().values

    return out.sort_values("평균수익", ascending=False)

for col, title in [
    ("가격상태", "가격상태별"),
    ("테마단계", "테마단계별"),
]:
    st.subheader(title)
    t = group_analysis(merged, col)
    if not t.empty:
        st.dataframe(
            t,
            use_container_width=True,
            hide_index=True,
            column_config={
                "승률": st.column_config.NumberColumn(format="%.1f%%"),
                "평균수익": st.column_config.NumberColumn(format="%+.2f%%"),
                "중앙수익": st.column_config.NumberColumn(format="%+.2f%%"),
                "최대손실": st.column_config.NumberColumn(format="%+.2f%%"),
                "최고수익": st.column_config.NumberColumn(format="%+.2f%%"),
            },
        )

# 점수 구간
st.subheader("점수 구간별")

score_specs = [
    ("테마점수", [0, 60, 65, 70, 75, 80, 1000]),
    ("선행점수", [0, 60, 70, 75, 80, 85, 1000]),
    ("과열점수", [-1, 5, 10, 20, 30, 40, 101]),
]

for col, bins in score_specs:
    if col not in merged.columns:
        continue

    tmp = merged.copy()
    labels = []
    for a, b in zip(bins[:-1], bins[1:]):
        labels.append(f"{a}~{b}" if b < 1000 else f"{a}+")
    tmp["_구간"] = pd.cut(
        tmp[col],
        bins=bins,
        labels=labels,
        include_lowest=True,
        right=False,
    )

    result = group_analysis(tmp, "_구간")

    if not result.empty:
        st.markdown(f"**{col}**")
        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True,
            column_config={
                "승률": st.column_config.NumberColumn(format="%.1f%%"),
                "평균수익": st.column_config.NumberColumn(format="%+.2f%%"),
                "중앙수익": st.column_config.NumberColumn(format="%+.2f%%"),
                "최대손실": st.column_config.NumberColumn(format="%+.2f%%"),
                "최고수익": st.column_config.NumberColumn(format="%+.2f%%"),
            },
        )

# ------------------------------------------------------------
# 10. ④ 약세 거래 집중 분석
# ------------------------------------------------------------
st.markdown("---")
st.header("④ D가 틀린 거래를 집중 분석")

bad = merged[merged["순수익률"] <= 0].copy()
bad = bad.sort_values("순수익률")

st.subheader(f"전체 손실 거래 {len(bad)}건")

show_bad_cols = [
    "연도", "신호일", "진입일", "청산일", "ETF",
    "테마", "테마점수", "선행점수", "과열점수",
    "테마단계", "가격상태", "순수익률", "보유일",
    "20일수익", "60일수익",
]
show_bad_cols = [c for c in show_bad_cols if c in bad.columns]

st.dataframe(
    bad[show_bad_cols],
    use_container_width=True,
    hide_index=True,
    height=520,
    column_config={
        "순수익률": st.column_config.NumberColumn(format="%+.2f%%"),
        "20일수익": st.column_config.NumberColumn(format="%+.2f%%"),
        "60일수익": st.column_config.NumberColumn(format="%+.2f%%"),
        "테마점수": st.column_config.NumberColumn(format="%.1f"),
        "선행점수": st.column_config.NumberColumn(format="%.1f"),
        "과열점수": st.column_config.NumberColumn(format="%.1f"),
    },
)

st.subheader("손실 유형")

if not bad.empty:
    loss_type = pd.DataFrame({
        "손실구분": [
            "경미한 손실 (-0~-5%)",
            "중간 손실 (-5~-10%)",
            "대손실 (-10% 이하)",
        ],
        "건수": [
            ((bad["순수익률"] < 0) & (bad["순수익률"] > -5)).sum(),
            ((bad["순수익률"] <= -5) & (bad["순수익률"] > -10)).sum(),
            (bad["순수익률"] <= -10).sum(),
        ],
    })
    loss_type["비율"] = loss_type["건수"] / len(bad) * 100
    st.dataframe(
        loss_type,
        use_container_width=True,
        hide_index=True,
        column_config={
            "비율": st.column_config.NumberColumn(format="%.1f%%")
        },
    )

# ------------------------------------------------------------
# 11. ⑤ 보유기간 분석
# ------------------------------------------------------------
st.markdown("---")
st.header("⑤ 보유기간과 결과의 관계")

hold_bins = [-1, 20, 60, 120, 250, 10_000]
hold_labels = [
    "20일 이하",
    "21~60일",
    "61~120일",
    "121~250일",
    "251일 이상",
]

tmp = merged.copy()
tmp["_보유구간"] = pd.cut(
    tmp["보유일"],
    bins=hold_bins,
    labels=hold_labels,
    right=True,
)

hold_result = group_analysis(tmp, "_보유구간")

st.dataframe(
    hold_result,
    use_container_width=True,
    hide_index=True,
    column_config={
        "승률": st.column_config.NumberColumn(format="%.1f%%"),
        "평균수익": st.column_config.NumberColumn(format="%+.2f%%"),
        "중앙수익": st.column_config.NumberColumn(format="%+.2f%%"),
        "최대손실": st.column_config.NumberColumn(format="%+.2f%%"),
        "최고수익": st.column_config.NumberColumn(format="%+.2f%%"),
    },
)

# ------------------------------------------------------------
# 12. ⑥ 시장환경 검증 — SPY
# ------------------------------------------------------------
st.markdown("---")
st.header("⑥ 시장환경별 D 성과")
st.caption(
    "여기서는 시장필터를 전략에 추가하지 않습니다. "
    "단지 D가 어떤 시장에서 강하고 약한지 사후적으로 관찰합니다."
)

@st.cache_data(ttl=86400, show_spinner=False)
def get_spy_regime(start_date, end_date):
    start = pd.Timestamp(start_date) - pd.Timedelta(days=180)
    end = pd.Timestamp(end_date) + pd.Timedelta(days=5)

    x = yf.download(
        "SPY",
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        auto_adjust=True,
        progress=False,
    )

    if x is None or x.empty:
        return pd.DataFrame()

    if isinstance(x.columns, pd.MultiIndex):
        x.columns = x.columns.get_level_values(0)

    x = x.rename(columns=str.title)
    close = x["Close"].astype(float)

    out = pd.DataFrame(index=close.index)
    out["Close"] = close
    out["MA20"] = close.rolling(20).mean()
    out["MA60"] = close.rolling(60).mean()
    out["R20"] = close.pct_change(20) * 100

    out["시장국면"] = np.select(
        [
            (out["Close"] > out["MA60"]) & (out["MA20"] > out["MA60"]) & (out["R20"] > 5),
            (out["Close"] > out["MA60"]) & (out["MA20"] > out["MA60"]),
            (out["Close"] < out["MA60"]) & (out["MA20"] < out["MA60"]),
        ],
        [
            "강한 상승",
            "상승/중립",
            "하락",
        ],
        default="전환/혼조",
    )

    out.index = pd.to_datetime(out.index).tz_localize(None)
    return out

spy = get_spy_regime(
    merged["신호일"].min(),
    merged["신호일"].max(),
)

if spy.empty:
    st.warning("SPY 데이터를 가져오지 못했습니다. CSV 기반 분석은 계속 가능합니다.")
else:
    regime = []
    for _, r in merged.iterrows():
        d = r["신호일"]
        if pd.isna(d):
            continue

        idx = spy.index[spy.index <= d]
        if len(idx) == 0:
            continue

        sr = spy.loc[idx[-1]]

        regime.append({
            "신호일": d,
            "ETF": r["ETF"],
            "순수익률": r["순수익률"],
            "시장국면": sr["시장국면"],
            "SPY": sr["Close"],
            "SPY_MA20": sr["MA20"],
            "SPY_MA60": sr["MA60"],
            "SPY_R20": sr["R20"],
        })

    regime_df = pd.DataFrame(regime)

    if not regime_df.empty:
        regime_result = group_analysis(regime_df, "시장국면")

        st.dataframe(
            regime_result,
            use_container_width=True,
            hide_index=True,
            column_config={
                "승률": st.column_config.NumberColumn(format="%.1f%%"),
                "평균수익": st.column_config.NumberColumn(format="%+.2f%%"),
                "중앙수익": st.column_config.NumberColumn(format="%+.2f%%"),
                "최대손실": st.column_config.NumberColumn(format="%+.2f%%"),
                "최고수익": st.column_config.NumberColumn(format="%+.2f%%"),
            },
        )

# ------------------------------------------------------------
# 13. ⑦ 검증 판정
# ------------------------------------------------------------
st.markdown("---")
st.header("⑦ 검증 판정")

positive_years = int((annual_check["누적복리"] > 0).sum())
negative_years = int((annual_check["누적복리"] < 0).sum())

if profit_factor > 1.2 and win_rate >= 50 and mdd > -35:
    st.success(
        "현재 데이터 기준 D는 '폐기'가 아니라 '추가 검증할 가치가 있는 전략'입니다."
    )
elif profit_factor > 1.0:
    st.warning(
        "D는 약한 우위가 있으나 아직 견고하다고 단정하기 어렵습니다."
    )
else:
    st.error(
        "현재 D는 우위가 확인되지 않습니다. 추가 필터보다 가설 자체를 재검토해야 합니다."
    )

st.markdown(
    f"""
**현재 자동 판정 요약**

- 거래수: **{len(merged)}**
- 승률: **{win_rate:.1f}%**
- Profit Factor: **{profit_factor:.2f}**
- MDD: **{mdd:.2f}%**
- 양(+)의 연도: **{positive_years}**
- 음(-)의 연도: **{negative_years}**

> 이 화면은 새로운 매매조건을 자동으로 만들어내지 않습니다.
> 손실 원인을 확인한 뒤 사람이 가설을 세우고, 그 가설을 별도 백테스트로 검증하는 것을 원칙으로 합니다.
"""
)

# ------------------------------------------------------------
# 14. CSV 다운로드
# ------------------------------------------------------------
st.markdown("---")
st.header("⑧ 검증 결과 CSV")

downloads = {
    "D_전체거래_검증": merged,
    "D_연도별_검증": annual_check,
    "D_손실거래_검증": bad,
}

for name, df in downloads.items():
    st.download_button(
        f"📥 {name} CSV",
        data=df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
        file_name=f"ETF_RADAR_{name}.csv",
        mime="text/csv",
        use_container_width=True,
        key=f"download_{name}",
    )

# ------------------------------------------------------------
# 15. 원본 비교 CSV도 표시
# ------------------------------------------------------------
if comparison_df is not None:
    st.markdown("---")
    st.header("⑨ 기존 C / D / D+M 비교 원본")
    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True,
    )
