# KRX ETF delisting candidate verifier v3. Separate app; never modifies app.py/source CSV.
import os, re, time
from pathlib import Path
from datetime import timedelta
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="KRX ETF 분류 검증 v3", layout="wide")
st.title("KRX ETF 분류 검증 v3")
st.caption("후보 종목코드·종목명·응답 스키마를 함께 점검합니다. 결과는 확정 판정이 아니라 검토용 증거입니다.")
CSV_PATH = Path(__file__).resolve().parent / "KRX_DELISTED_ALL.csv"
API_URL = "https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd"
SAMPLE_URL = "https://data-dbg.krx.co.kr/svc/sample/apis/etp/etf_bydd_trd"


def norm_date(value):
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) != 8: return None
    try: return pd.to_datetime(digits, format="%Y%m%d").strftime("%Y%m%d")
    except (ValueError, TypeError): return None

def norm_name(value):
    return re.sub(r"[^0-9A-Za-z가-힣]", "", str(value or "")).upper()

def name_tokens(value):
    # Secondary comparison only; do not remove meaningful class/share suffixes from exact match.
    n = norm_name(value)
    for token in ("ETF", "상장지수펀드"):
        n = n.replace(token, "")
    return n

def parse_rows(payload):
    if not isinstance(payload, dict): raise ValueError("응답이 JSON 객체가 아닙니다.")
    rows = payload.get("OutBlock_1")
    if isinstance(rows, dict): rows = [rows]
    if not isinstance(rows, list):
        raise ValueError("OutBlock_1 목록이 없습니다. 응답 키: " + ", ".join(map(str, payload.keys())))
    return rows

def get_key():
    key = os.getenv("KRX_API_KEY", "")
    try: key = key or str(st.secrets.get("KRX_API_KEY", ""))
    except Exception: pass
    return key.strip()

def call_krx(date, sample, api_key):
    url = SAMPLE_URL if sample else API_URL
    headers = {} if sample else {"AUTH_KEY": api_key}
    r = requests.get(url, params={"basDd": date}, headers=headers, timeout=25)
    if r.status_code != 200:
        detail = re.sub(r"\s+", " ", r.text[:160])
        raise RuntimeError(f"HTTP {r.status_code}: {detail}")
    try: payload = r.json()
    except ValueError: raise ValueError("JSON 응답이 아닙니다: " + r.text[:160])
    return pd.DataFrame(parse_rows(payload)), r.status_code

if not CSV_PATH.exists():
    st.error("KRX_DELISTED_ALL.csv를 저장소 최상위에서 찾지 못했습니다."); st.stop()
try: source = pd.read_csv(CSV_PATH, dtype=str, encoding="utf-8-sig").fillna("")
except Exception as e:
    st.error(f"CSV 읽기 오류: {type(e).__name__}: {e}"); st.stop()
required = {"종목코드", "종목명", "증권구분", "폐지일"}
if required - set(source.columns):
    st.error("필수 컬럼 누락: " + ", ".join(sorted(required-set(source.columns)))); st.stop()
source["폐지일_API형식"] = source["폐지일"].map(norm_date)
allowed = {"수익증권", "투자회사", "부동산투자회사", "선박투자회사"}
candidates = source[source["증권구분"].astype(str).str.strip().isin(allowed) & source["폐지일_API형식"].notna()].copy()
st.success(f"원본 CSV 읽기 성공: {len(source):,}행")
st.write(f"검토 후보: {len(candidates):,}건")
st.warning("종목코드 형식이 KRX ISU_CD와 다를 수 있고, 이름이 일치하지 않아도 ETF가 아닐 수 있습니다. 자동으로 ETF/비ETF 확정 판정을 내리지 않습니다.")

with st.form("verify_v3"):
    sample_mode = st.checkbox("공개 샘플 API 사용 (연결/응답형식 점검 전용)", value=False)
    key = st.text_input("KRX API 인증키", value=get_key(), type="password", help="키는 채팅이나 GitHub 코드에 올리지 마세요. Streamlit Secrets 사용을 권장합니다.")
    n = st.selectbox("검사할 후보 수", [5, 10, 20, 50], index=0)
    lookback = st.selectbox("폐지일 이전 조회 범위(달력일)", [14, 30, 60, 90], index=1)
    run = st.form_submit_button("v3 검증 실행", type="primary")

if run:
    if not sample_mode and not key.strip(): st.error("실제 API 모드에는 승인된 인증키가 필요합니다."); st.stop()
    if candidates.empty: st.error("검사 후보가 없습니다."); st.stop()
    test = candidates.head(int(n)).copy()
    date_map = {}
    for _, row in test.iterrows():
        end = pd.to_datetime(row["폐지일_API형식"], format="%Y%m%d")
        dates = [(end - timedelta(days=i)).strftime("%Y%m%d") for i in range(int(lookback)+1)]
        date_map[str(row["폐지일_API형식"])] = dates
    unique_dates = sorted({d for dates in date_map.values() for d in dates}, reverse=True)
    st.info(f"{len(test)}개 후보, 중복 제거한 {len(unique_dates)}개 날짜를 조회합니다.")
    date_rows, date_errors = {}, {}
    progress = st.progress(0); status = st.empty()
    for i, date in enumerate(unique_dates):
        try:
            df, _ = call_krx(date, sample_mode, key.strip())
            if not df.empty and not {"ISU_CD", "ISU_NM"}.issubset(df.columns):
                raise ValueError("필수 필드 ISU_CD/ISU_NM 없음. 실제 필드: " + ", ".join(map(str, df.columns)))
            date_rows[date] = df
        except Exception as e: date_errors[date] = f"{type(e).__name__}: {e}"
        progress.progress((i+1)/len(unique_dates)); status.write(f"조회 중: {i+1}/{len(unique_dates)} 날짜")
        time.sleep(0.03)
    status.empty(); progress.empty()
    results=[]; sample_rows=[]; schema_rows=[]
    for _, row in test.iterrows():
        source_code = re.sub(r"\D", "", str(row["종목코드"]))
        source_name = str(row["종목명"]).strip()
        exact_name = norm_name(source_name); secondary_name = name_tokens(source_name)
        dates = date_map[str(row["폐지일_API형식"])]
        exact_hits=[]; secondary_hits=[]; code_hits=[]; success_dates=0; errors=[]; total_rows=0
        for date in dates:
            if date in date_errors: errors.append(date + " " + date_errors[date]); continue
            df = date_rows.get(date, pd.DataFrame()); success_dates += 1
            if df.empty: continue
            total_rows += len(df)
            if not schema_rows:
                schema_rows = [{"응답컬럼": str(c)} for c in df.columns]
            for _, h in df.iterrows():
                krx_code = re.sub(r"\D", "", str(h.get("ISU_CD", "")))
                krx_name = str(h.get("ISU_NM", ""))
                nn = norm_name(krx_name); nt = name_tokens(krx_name)
                item = (date, str(h.get("ISU_CD", "")), krx_name)
                if exact_name and nn == exact_name: exact_hits.append(item)
                elif secondary_name and nt == secondary_name: secondary_hits.append(item)
                # Code comparison is a lead only; source codes may be internal/legacy IDs.
                if source_code and krx_code and (source_code == krx_code or source_code.lstrip("0") == krx_code.lstrip("0")):
                    code_hits.append(item)
                if len(sample_rows) < 25:
                    sample_rows.append({"조회일":date,"KRX종목코드":str(h.get("ISU_CD","")),"KRX종목명":krx_name})
        if exact_hits:
            verdict="정확한 종목명 일치 — ETF 여부 추가 확인 필요"; hit=exact_hits[0]
        elif secondary_hits:
            verdict="보조 이름 일치 — 수동 확인 필요"; hit=secondary_hits[0]
        elif code_hits:
            verdict="코드 후보 일치 — 코드 체계 확인 필요"; hit=code_hits[0]
        elif success_dates:
            verdict="조회 성공, 코드/이름 일치 없음 — 판정 보류"; hit=("", "", "")
        else:
            verdict="조회 실패 — 판정 보류"; hit=("", "", "")
        results.append({
            "원본종목코드":str(row["종목코드"]),"원본종목명":source_name,"증권구분":str(row["증권구분"]),"폐지일":str(row["폐지일"]),
            "조회시작일":dates[-1],"조회종료일":dates[0],"정상응답일수":success_dates,"조회된거래행수":total_rows,
            "정확한이름일치수":len(exact_hits),"보조이름일치수":len(secondary_hits),"코드후보일치수":len(code_hits),
            "후보KRX기준일":hit[0],"후보KRX종목코드":hit[1],"후보KRX종목명":hit[2],"결과":verdict,
            "API모드":"공개 샘플" if sample_mode else "실제 인증 API","오류요약":" | ".join(errors[:3])})
    out=pd.DataFrame(results)
    st.subheader("후보별 결과")
    st.dataframe(out, hide_index=True, width="stretch")
    st.download_button("후보별 결과 CSV 다운로드", out.to_csv(index=False).encode("utf-8-sig"), "KRX_ETF_TYPE_TEST_V3.csv", "text/csv")
    if schema_rows:
        st.subheader("KRX 응답 필드 확인")
        st.write("아래는 응답 컬럼 목록입니다. 종목코드 형식이 원본 코드와 다른지 확인하는 데 사용합니다.")
        st.dataframe(pd.DataFrame(schema_rows), hide_index=True, width="stretch")
    if sample_rows:
        with st.expander("조회된 KRX 데이터 일부 (최대 25행)"):
            st.dataframe(pd.DataFrame(sample_rows), hide_index=True, width="stretch")
    if date_errors:
        with st.expander(f"API 오류 상세 ({len(date_errors)}개 날짜)"):
            st.dataframe(pd.DataFrame([{"기준일":d,"오류":e} for d,e in date_errors.items()]), hide_index=True, width="stretch")
    st.info("중요: 이름/코드 일치는 조사 단서일 뿐 ETF 확정 증거가 아닙니다. 조회 기간 내 불일치도 비ETF 판정 근거가 아닙니다. 최종 확정에는 공식 상장·폐지 이력 및 종목 표준코드 확인이 필요합니다.")

with st.expander("API 명세"):
    st.write("실제 API:", API_URL); st.write("샘플 API:", SAMPLE_URL)
    st.write("파라미터: basDd=YYYYMMDD / 실제 API 인증 헤더: AUTH_KEY")
    st.markdown("[KRX 공식 ETF API 안내](https://openapi.krx.co.kr/contents/OPP/USES/service/OPPUSES003_S2.cmd?BO_ID=VujebrcOsZQMybnUuwLk)")
