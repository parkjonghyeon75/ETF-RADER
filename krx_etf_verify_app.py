# KRX ETF delisting verifier v4. Separate Streamlit app; does not modify app.py or source CSV.
import os, re, time
from pathlib import Path
from datetime import timedelta
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="KRX ETF 분류 검증 v5", layout="wide")
st.title("KRX ETF 분류 검증 v5")
st.caption("원본 코드·이전상장 코드·종목명·폐지사유를 함께 기록합니다. 결과는 자동 확정 판정이 아닌 공식 ETF 거래자료 대조 결과입니다.")
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

def norm_code(value):
    # Preserve letters: KRX ETF codes can be alphanumeric (e.g. 0184E0).
    s = str(value or "").strip().upper()
    if s.endswith(".0") and s[:-2].isdigit(): s = s[:-2]
    return re.sub(r"[^0-9A-Z]", "", s)

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
    return pd.DataFrame(parse_rows(payload))

if not CSV_PATH.exists():
    st.error("KRX_DELISTED_ALL.csv를 저장소 최상위에서 찾지 못했습니다."); st.stop()
try: source = pd.read_csv(CSV_PATH, dtype=str, encoding="utf-8-sig").fillna("")
except Exception as e:
    st.error(f"CSV 읽기 오류: {type(e).__name__}: {e}"); st.stop()
required = {"종목코드", "종목명", "증권구분", "폐지일", "상장일"}
if required - set(source.columns):
    st.error("필수 컬럼 누락: " + ", ".join(sorted(required-set(source.columns)))); st.stop()
source["폐지일_API형식"] = source["폐지일"].map(norm_date)
source["상장일_API형식"] = source["상장일"].map(norm_date)
allowed = {"수익증권", "투자회사", "부동산투자회사", "선박투자회사"}
candidates = source[source["증권구분"].astype(str).str.strip().isin(allowed) & source["폐지일_API형식"].notna()].copy()

st.success(f"원본 CSV 읽기 성공: {len(source):,}행")
st.write(f"검토 후보: {len(candidates):,}건")
st.warning("KRX ETF 일별매매정보는 ETF 거래목록만 제공합니다. 원본 코드가 6자리 영숫자 코드가 아니면 코드 직접 비교가 불가능할 수 있으며, 불일치만으로 비ETF 확정 판정을 내리지 않습니다.")

with st.form("verify_v5"):
    sample_mode = st.checkbox("공개 샘플 API 사용 (연결/응답형식 점검 전용)", value=False)
    key = st.text_input("KRX API 인증키", value=get_key(), type="password", help="키는 채팅이나 GitHub 코드에 올리지 마세요. Streamlit Secrets 사용을 권장합니다.")
    n = st.selectbox("검사할 후보 수", [5, 10, 20, 50], index=0)
    window = st.selectbox("폐지일 주변 검사 방식", ["폐지일 당일 + 직전 7일", "폐지일 당일 + 직전 30일", "상장일 + 폐지일 주변"], index=0)
    run = st.form_submit_button("v5 검증 실행", type="primary")

if run:
    if not sample_mode and not key.strip(): st.error("실제 API 모드에는 승인된 인증키가 필요합니다."); st.stop()
    test = candidates.head(int(n)).copy()
    if test.empty: st.error("검사 후보가 없습니다."); st.stop()
    date_map = {}
    for idx, row in test.iterrows():
        end = pd.to_datetime(row["폐지일_API형식"], format="%Y%m%d")
        if window == "폐지일 당일 + 직전 7일": offsets = range(0, 8)
        else: offsets = range(0, 31)
        dates = {(end - timedelta(days=i)).strftime("%Y%m%d") for i in offsets}
        if window == "상장일 + 폐지일 주변" and row["상장일_API형식"]:
            dates.add(row["상장일_API형식"])
        date_map[str(idx)] = sorted(dates, reverse=True)
    unique_dates = sorted({d for ds in date_map.values() for d in ds}, reverse=True)
    st.info(f"{len(test)}개 후보를 대상으로 중복 제거한 {len(unique_dates)}개 기준일을 조회합니다.")
    date_rows, date_errors = {}, {}
    progress = st.progress(0); status = st.empty()
    for i, date in enumerate(unique_dates):
        try:
            df = call_krx(date, sample_mode, key.strip())
            if not df.empty and not {"ISU_CD", "ISU_NM"}.issubset(df.columns):
                raise ValueError("필수 필드 ISU_CD/ISU_NM 없음. 실제 필드: " + ", ".join(map(str, df.columns)))
            date_rows[date] = df
        except Exception as e: date_errors[date] = f"{type(e).__name__}: {e}"
        progress.progress((i+1)/len(unique_dates)); status.write(f"조회 중: {i+1}/{len(unique_dates)} 기준일")
        time.sleep(0.03)
    status.empty(); progress.empty()
    results=[]; sample_rows=[]; schema_cols=[]
    for idx, row in test.iterrows():
        src_code = norm_code(row["종목코드"])
        # KRX delisted-listing code can differ from the current trading code.
        code_comparable = bool(re.fullmatch(r"[0-9A-Z]{6}", src_code))
        src_name = str(row["종목명"]).strip(); src_name_norm = norm_name(src_name)
        prior_code = norm_code(row.get("이전상장후_종목코드", ""))
        prior_name = str(row.get("이전상장후_종목명", "")).strip()
        prior_name_norm = norm_name(prior_name)
        prior_code_comparable = bool(re.fullmatch(r"[0-9A-Z]{6}", prior_code))
        exact_hits=[]; prior_name_hits=[]; code_hits=[]; prior_code_hits=[]; rows_count=0; ok_dates=0; errs=[]
        dates = date_map[str(idx)]
        for date in dates:
            if date in date_errors:
                errs.append(date + " " + date_errors[date]); continue
            ok_dates += 1; df = date_rows.get(date, pd.DataFrame())
            if df.empty: continue
            rows_count += len(df)
            if not schema_cols: schema_cols = list(df.columns)
            for _, h in df.iterrows():
                krx_code = norm_code(h.get("ISU_CD", "")); krx_name = str(h.get("ISU_NM", ""))
                item = (date, str(h.get("ISU_CD", "")), krx_name)
                krx_name_norm = norm_name(krx_name)
                if src_name_norm and krx_name_norm == src_name_norm: exact_hits.append(item)
                if prior_name_norm and krx_name_norm == prior_name_norm: prior_name_hits.append(item)
                if code_comparable and src_code == krx_code: code_hits.append(item)
                if prior_code_comparable and prior_code == krx_code: prior_code_hits.append(item)
                if len(sample_rows) < 25: sample_rows.append({"조회일":date,"KRX종목코드":str(h.get("ISU_CD", "")),"KRX종목명":krx_name})
        if exact_hits: verdict="원본 종목명 일치 — 공식 폐지이력 추가 확인 필요"; hit=exact_hits[0]
        elif prior_name_hits: verdict="이전상장후 종목명 일치 — 관계 확인 필요"; hit=prior_name_hits[0]
        elif code_hits: verdict="원본 6자리 코드 일치 — 공식 이력 확인 필요"; hit=code_hits[0]
        elif prior_code_hits: verdict="이전상장후 6자리 코드 일치 — 관계 확인 필요"; hit=prior_code_hits[0]
        elif not code_comparable and not prior_code_comparable: verdict="원본/이전상장 코드 모두 직접 비교 불가 — 판정 보류"; hit=("","","")
        elif ok_dates: verdict="조회 성공, 일치 없음 — 비ETF 확정 금지"; hit=("","","")
        else: verdict="API 조회 실패 — 판정 보류"; hit=("","","")
        results.append({
            "원본종목코드":str(row["종목코드"]),"원본종목명":src_name,"증권구분":str(row["증권구분"]),"상장일":str(row["상장일"]),"폐지일":str(row["폐지일"]),
            "폐지사유":str(row.get("폐지사유", "")),"이전상장후_종목코드":str(row.get("이전상장후_종목코드", "")),"이전상장후_종목명":prior_name,
            "원본코드_직접비교가능": "예" if code_comparable else "아니오", "이전상장코드_직접비교가능":"예" if prior_code_comparable else "아니오", "검사기준일수":len(dates),"정상응답일수":ok_dates,"조회된거래행수":rows_count,
            "정확한이름일치수":len(exact_hits),"이전상장후_이름일치수":len(prior_name_hits),"원본코드일치수":len(code_hits),"이전상장후_코드일치수":len(prior_code_hits),"후보KRX기준일":hit[0],"후보KRX종목코드":hit[1],"후보KRX종목명":hit[2],"결과":verdict,
            "API모드":"공개 샘플" if sample_mode else "실제 인증 API","오류요약":" | ".join(errs[:3])})
    out=pd.DataFrame(results)
    st.subheader("후보별 결과")
    st.dataframe(out, hide_index=True, width="stretch")
    st.download_button("후보별 결과 CSV 다운로드", out.to_csv(index=False).encode("utf-8-sig"), "KRX_ETF_TYPE_TEST_V5.csv", "text/csv")
    if schema_cols:
        st.subheader("KRX 응답 컬럼")
        st.code(", ".join(map(str, schema_cols)))
    if sample_rows:
        with st.expander("조회된 KRX 데이터 일부 (최대 25행)"):
            st.dataframe(pd.DataFrame(sample_rows), hide_index=True, width="stretch")
    if date_errors:
        with st.expander(f"API 오류 상세 ({len(date_errors)}개 날짜)"):
            st.dataframe(pd.DataFrame([{"기준일":d,"오류":e} for d,e in date_errors.items()]), hide_index=True, width="stretch")
    st.info("이 도구는 KRX ETF 일별 거래자료와 대조합니다. 거래목록 불일치만으로 비ETF라고 확정하지 않습니다. 최종 확정에는 공식 종목 기본정보 및 상장·폐지 이력 확인이 필요합니다.")

with st.expander("API 명세"):
    st.write("실제 API:", API_URL); st.write("샘플 API:", SAMPLE_URL)
    st.write("파라미터: basDd=YYYYMMDD / 실제 API 인증 헤더: AUTH_KEY")
    st.markdown("[KRX 공식 서비스 목록](https://openapi.krx.co.kr/contents/OPP/INFO/service/OPPINFO004.cmd)")
