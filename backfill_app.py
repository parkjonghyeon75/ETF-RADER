"""
ETF RADAR historical/backfill diagnostics — separate tool
IMPORTANT: Reconstructed from requirements only because the supplied ZIP lacked the original
backfill_app.py and app.py. It does not overwrite either file.
Run: streamlit run backfill_app.py
"""
from __future__ import annotations

import io
import re
import zipfile
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="ETF RADAR Backfill Diagnostics", page_icon="🧪", layout="wide")
st.title("ETF RADAR — 과거 데이터 / 상장폐지 ETF 검증")
st.warning("재구성한 별도 진단 도구입니다. 원본 app.py의 신호 스키마와 대조 검증되지 않았으며, 추정 매칭은 수행하지 않습니다.")

def col(df, candidates):
    norm = {re.sub(r"[\s_\-]", "", str(c)).lower(): c for c in df.columns}
    for c in candidates:
        k = re.sub(r"[\s_\-]", "", c).lower()
        if k in norm:
            return norm[k]
    return None

def code_str(x):
    s = str(x).strip()
    if s.endswith(".0"):
        s = s[:-2]
    # Preserve alphanumeric 6-character codes exactly; do not coerce to numeric.
    return s.upper()

def read_csv(file):
    try:
        file.seek(0)
        return pd.read_csv(file, dtype=str)
    except UnicodeDecodeError:
        file.seek(0)
        return pd.read_csv(file, dtype=str, encoding="cp949")

st.markdown("""
이 도구는 업로드된 자료끼리 **명시적 코드 완전 일치**만 확인합니다.
종목명 유사도나 코드 일부 일치로 폐지 ETF를 추정 연결하지 않습니다.
""")

with st.sidebar:
    master_file = st.file_uploader("KRX ETF 기준정보 CSV", type=["csv"], key="master")
    delisted_file = st.file_uploader("상장폐지 목록 CSV", type=["csv"], key="delisted")
    signals_file = st.file_uploader("신호 CSV (선택)", type=["csv"], key="signals")
    prices_file = st.file_uploader("가격 이력 CSV (선택)", type=["csv"], key="prices")

if not master_file or not delisted_file:
    st.info("시작하려면 KRX ETF 기준정보와 상장폐지 목록 CSV를 업로드하세요.")
    st.stop()

try:
    master = read_csv(master_file)
    delisted = read_csv(delisted_file)
except Exception as e:
    st.error(f"CSV 읽기 실패: {e}")
    st.stop()

m_code = col(master, ["ISU_CD","종목코드","단축코드","ticker","code"])
d_code = col(delisted, ["ISU_CD","종목코드","단축코드","ticker","code"])
m_name = col(master, ["ISU_NM","한글종목명","종목명","상품명","name"])
d_name = col(delisted, ["ISU_NM","한글종목명","종목명","상품명","name"])
if not m_code or not d_code:
    st.error("두 파일에서 명시적인 종목코드 열을 찾지 못했습니다. 열 이름을 확인하세요.")
    st.write({"기준정보 열":list(master.columns),"상장폐지 열":list(delisted.columns)})
    st.stop()

master = master.copy()
delisted = delisted.copy()
master["_code"] = master[m_code].map(code_str)
delisted["_code"] = delisted[d_code].map(code_str)
master["_name"] = master[m_name].fillna("").astype(str) if m_name else ""
delisted["_name"] = delisted[d_name].fillna("").astype(str) if d_name else ""

master_codes = set(master["_code"].dropna())
delisted["exact_code_match"] = delisted["_code"].isin(master_codes)
matched = delisted[delisted["exact_code_match"]].copy()
unmatched = delisted[~delisted["exact_code_match"]].copy()
st.subheader("기준정보 코드 일치 진단")
a,b,c,d = st.columns(4)
a.metric("기준정보 행 수", f"{len(master):,}")
b.metric("상장폐지 목록 행 수", f"{len(delisted):,}")
c.metric("완전 일치 코드", f"{len(matched):,}")
d.metric("일치하지 않는 코드", f"{len(unmatched):,}")
st.caption("주의: 코드가 일치해도 그 자체만으로 ETF였다고 확정하지 않습니다. 기준정보의 공식 상품 유형/식별 필드가 제공되면 별도 검토가 필요합니다.")
with st.expander("완전 일치 목록"):
    st.dataframe(matched, use_container_width=True)
with st.expander("일치하지 않는 목록 — 추정 매칭 금지"):
    st.dataframe(unmatched, use_container_width=True)

diagnostics = []
if signals_file:
    try:
        signals = read_csv(signals_file)
        s_code = col(signals, ["ISU_CD","종목코드","단축코드","ticker","code"])
        s_date = col(signals, ["date","날짜","신호일","signal_date","기준일"])
        if not s_code:
            diagnostics.append(("signals", "코드 열 없음", len(signals)))
        else:
            signals["_code"] = signals[s_code].map(code_str)
            diagnostics.append(("signals", "전체 행", len(signals)))
            diagnostics.append(("signals", "기준정보 코드와 완전 일치", int(signals["_code"].isin(master_codes).sum())))
            if s_date:
                signals["_date"] = pd.to_datetime(signals[s_date], errors="coerce")
                diagnostics.append(("signals", "날짜 파싱 실패", int(signals["_date"].isna().sum())))
        st.subheader("신호 파일 진단")
        st.dataframe(signals.head(500), use_container_width=True)
    except Exception as e:
        st.error(f"신호 CSV 읽기 실패: {e}")

if prices_file:
    try:
        prices = read_csv(prices_file)
        p_code = col(prices, ["ISU_CD","종목코드","단축코드","ticker","code"])
        p_date = col(prices, ["date","날짜","기준일","trading_date"])
        p_close = col(prices, ["close","종가","수정종가","adj_close","adj close"])
        st.subheader("가격 이력 진단")
        if not all([p_code,p_date,p_close]):
            st.error("가격 이력에서 코드/날짜/종가 열을 모두 찾지 못했습니다.")
            st.write(list(prices.columns))
        else:
            prices["_code"] = prices[p_code].map(code_str)
            prices["_date"] = pd.to_datetime(prices[p_date], errors="coerce")
            prices["_close"] = pd.to_numeric(prices[p_close], errors="coerce")
            bad_date = int(prices["_date"].isna().sum())
            bad_close = int(prices["_close"].isna().sum() + (prices["_close"] <= 0).sum())
            st.write({
                "행 수":len(prices),
                "고유 코드 수":int(prices["_code"].nunique()),
                "날짜 파싱 실패":bad_date,
                "종가 누락/비수치/0 이하":bad_close,
                "중복 코드-날짜":int(prices.duplicated(["_code","_date"]).sum()),
                "기준정보와 코드 완전 일치 행":int(prices["_code"].isin(master_codes).sum())
            })
            st.dataframe(prices.head(500), use_container_width=True)
    except Exception as e:
        st.error(f"가격 CSV 읽기 실패: {e}")

if diagnostics:
    st.subheader("진단 요약")
    st.dataframe(pd.DataFrame(diagnostics, columns=["파일","검사","결과"]), use_container_width=True)

# Export evidence: raw inputs and normalized exact-code matching, without claiming validation success.
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("delisted_exact_code_matches.csv", matched.drop(columns=[], errors="ignore").to_csv(index=False))
    z.writestr("delisted_unmatched_no_guessing.csv", unmatched.to_csv(index=False))
    z.writestr("diagnostic_summary.txt",
               f"Generated UTC: {datetime.utcnow().isoformat()}Z\n"
               f"Master rows: {len(master)}\nDelisted rows: {len(delisted)}\n"
               f"Exact-code matches: {len(matched)}\nUnmatched: {len(unmatched)}\n"
               "No fuzzy/name/partial-code matching performed.\n"
               "This report does not certify delisted ETF identity or historical price coverage.\n")
st.download_button("진단 ZIP 다운로드", buf.getvalue(), file_name="ETF_RADAR_BACKFILL_DIAGNOSTICS.zip",
                   mime="application/zip")
