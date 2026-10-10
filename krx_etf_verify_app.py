# Standalone KRX ETF delisting verification app. Does not modify app.py or source CSV.
import os, re, time
from pathlib import Path
from datetime import timedelta
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="KRX ETF 분류 검증 v2", layout="wide")
st.title("KRX ETF 분류 검증")
st.caption("폐지일 기준으로 KRX ETF 일별매매정보를 조회합니다. 기존 app.py와 원본 CSV는 수정하지 않습니다.")
CSV_PATH = Path(__file__).resolve().parent / "KRX_DELISTED_ALL.csv"
SAMPLE_URL = "https://data-dbg.krx.co.kr/svc/sample/apis/etp/etf_bydd_trd"
API_URL = "https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd"


def norm_date(value):
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) != 8: return None
    try: return pd.to_datetime(digits, format="%Y%m%d").strftime("%Y%m%d")
    except (ValueError, TypeError): return None

def norm_name(value):
    # Conservative normalization: remove whitespace and punctuation, preserve Korean/Latin/digits.
    return re.sub(r"[^0-9A-Za-z가-힣]", "", str(value or "")).upper()

def parse_rows(payload):
    if not isinstance(payload, dict): raise ValueError("응답이 JSON 객체가 아닙니다.")
    rows = payload.get("OutBlock_1")
    if isinstance(rows, dict): rows = [rows]
    if rows is None and any(k in payload for k in ("result", "msg", "message", "error")):
        raise ValueError("KRX 응답에 OutBlock_1이 없습니다: " + str(payload)[:250])
    if not isinstance(rows, list): raise ValueError("OutBlock_1 목록이 없습니다. 응답 키: " + ", ".join(map(str,payload.keys())))
    return rows

def get_key():
    key = os.getenv("KRX_API_KEY", "")
    try:
        key = key or str(st.secrets.get("KRX_API_KEY", ""))
    except Exception:
        pass
    return key.strip()

def call_krx(date, sample, api_key):
    url = SAMPLE_URL if sample else API_URL
    headers = {} if sample else {"AUTH_KEY": api_key}
    r = requests.get(url, params={"basDd": date}, headers=headers, timeout=25)
    if r.status_code != 200:
        detail = re.sub(r"\s+", " ", r.text[:180])
        raise RuntimeError(f"HTTP {r.status_code}: {detail}")
    try: payload = r.json()
    except ValueError: raise ValueError("JSON 응답이 아닙니다: " + r.text[:180])
    return pd.DataFrame(parse_rows(payload)), r.status_code

if not CSV_PATH.exists():
    st.error("KRX_DELISTED_ALL.csv를 저장소 최상위에서 찾지 못했습니다.")
    st.stop()
try: source = pd.read_csv(CSV_PATH, dtype=str, encoding="utf-8-sig").fillna("")
except Exception as e:
    st.error(f"CSV 읽기 오류: {type(e).__name__}: {e}"); st.stop()
required = {"종목코드", "종목명", "증권구분", "폐지일"}
if required - set(source.columns):
    st.error("필수 컬럼 누락: " + ", ".join(sorted(required-set(source.columns))))
    st.stop()
source["폐지일_API형식"] = source["폐지일"].map(norm_date)
allowed = {"수익증권", "투자회사", "부동산투자회사", "선박투자회사"}
candidates = source[source["증권구분"].astype(str).str.strip().isin(allowed) & source["폐지일_API형식"].notna()].copy()
st.success(f"원본 CSV 읽기 성공: {len(source):,}행")
st.warning("증권구분은 후보 선별용일 뿐 ETF 확정 근거가 아닙니다. API에 일치 항목이 없어도 ETF가 아니라고 단정하지 않습니다.")
st.write(f"검토 후보: {len(candidates):,}건")

with st.form("test_v2"):
    sample_mode = st.checkbox("공개 샘플 API 사용 (연결 확인용이며 실제 폐지일 검증에는 부적합)", value=False)
    key = st.text_input("KRX API 인증키", value=get_key(), type="password", help="키를 GitHub 코드나 채팅에 올리지 마세요. Secrets에 저장하는 방식을 권장합니다.")
    n = st.selectbox("검사할 후보 수", [5, 10, 20], index=0)
    lookback = st.selectbox("폐지일 이전 조회 범위(달력일)", [7, 14, 21], index=1)
    run = st.form_submit_button("폐지일 기준 검증 실행", type="primary")

if run:
    if not sample_mode and not key.strip():
        st.error("실제 API 모드에는 승인된 인증키가 필요합니다."); st.stop()
    if candidates.empty:
        st.error("검사 후보가 없습니다."); st.stop()
    test = candidates.head(int(n)).copy()
    # Create dates from the recorded delisting date backwards, deduplicated; non-trading dates may return empty/error.
    date_map = {}
    for _, row in test.iterrows():
        end = pd.to_datetime(row["폐지일_API형식"], format="%Y%m%d")
        dates = [(end - timedelta(days=i)).strftime("%Y%m%d") for i in range(int(lookback)+1)]
        date_map[str(row["폐지일_API형식"])] = dates
    unique_dates = sorted({d for dates in date_map.values() for d in dates}, reverse=True)
    st.info(f"후보 {len(test)}건, 중복 제거한 날짜 {len(unique_dates)}개를 조회합니다. 요청 수에 따라 시간이 걸릴 수 있습니다.")
    date_rows, date_errors = {}, {}
    progress = st.progress(0)
    status = st.empty()
    for i, date in enumerate(unique_dates):
        try:
            df, code = call_krx(date, sample_mode, key.strip())
            # Verify expected schema even if the list is empty.
            if not df.empty and not {"ISU_CD", "ISU_NM"}.issubset(df.columns):
                raise ValueError("필수 필드 ISU_CD/ISU_NM이 없습니다: " + ", ".join(df.columns))
            date_rows[date] = df
        except Exception as e:
            date_errors[date] = f"{type(e).__name__}: {e}"
        progress.progress((i+1)/len(unique_dates))
        status.write(f"조회 중: {i+1}/{len(unique_dates)} 날짜")
    status.empty(); progress.empty()
    results=[]
    for _, row in test.iterrows():
        code0 = str(row["종목코드"]).strip()
        name0 = str(row["종목명"]).strip()
        target = norm_name(name0)
        dates = date_map[str(row["폐지일_API형식"])]
        matches=[]; successful_dates=0; errors=[]
        for date in dates:
            if date in date_errors:
                errors.append(date + " " + date_errors[date]); continue
            df = date_rows.get(date, pd.DataFrame())
            successful_dates += 1
            if df.empty or not {"ISU_CD","ISU_NM"}.issubset(df.columns): continue
            tmp=df.copy(); tmp["_norm_name"] = tmp["ISU_NM"].map(norm_name)
            # Exact normalized name only. Source ID is not assumed to be KRX short code.
            hit=tmp[tmp["_norm_name"].eq(target)] if target else tmp.iloc[0:0]
            for _, h in hit.iterrows():
                matches.append((date, str(h.get("ISU_CD","")), str(h.get("ISU_NM",""))))
        if matches:
            first=matches[0]
            verdict="이름 일치 발견 - ETF 후보, 코드/ISIN 추가 검증 필요"
            matched_date, krx_code, krx_name=first
        elif successful_dates:
            verdict="조회 완료, 이름 일치 없음 - ETF 아님으로 단정 금지"
            matched_date=krx_code=krx_name=""
        else:
            verdict="조회 실패 - 결과 판정 보류"
            matched_date=krx_code=krx_name=""
        results.append({
            "원본종목코드":code0,"원본종목명":name0,"증권구분":row["증권구분"],"폐지일":row["폐지일"],
            "조회시작일":dates[-1],"조회종료일":dates[0],"정상응답일수":successful_dates,
            "이름일치발견":bool(matches),"일치기준일":matched_date,"KRX종목코드":krx_code,"KRX종목명":krx_name,
            "결과":verdict,"API모드":"공개 샘플" if sample_mode else "실제 인증 API","오류요약":" | ".join(errors[:3])
        })
    out=pd.DataFrame(results)
    st.subheader("검증 결과")
    st.dataframe(out, hide_index=True, width="stretch")
    st.download_button("검증 결과 CSV 다운로드", out.to_csv(index=False).encode("utf-8-sig"), "KRX_ETF_TYPE_TEST_V2.csv", "text/csv")
    if date_errors:
        with st.expander(f"조회 오류 상세 ({len(date_errors)}개 날짜)"):
            st.dataframe(pd.DataFrame([{"기준일":d,"오류":e} for d,e in date_errors.items()]), hide_index=True, width="stretch")
    st.info("이 버전은 폐지일 전후 날짜를 조회하고 종목명 완전 일치만 기록합니다. 이름 일치는 ETF 확정이 아니며, 이름 불일치도 ETF가 아니라는 증거가 아닙니다. 확정에는 종목코드/표준코드(ISIN 포함) 및 별도 상장·폐지 이력 확인이 필요합니다. 원본 CSV와 app.py는 변경하지 않습니다.")

with st.expander("API 명세"):
    st.write("실제 API:", API_URL)
    st.write("샘플 API:", SAMPLE_URL)
    st.write("파라미터: basDd=YYYYMMDD / 실제 API 인증 헤더: AUTH_KEY")
    st.markdown("[KRX 공식 ETF API 안내](https://openapi.krx.co.kr/contents/OPP/USES/service/OPPUSES003_S2.cmd?BO_ID=VujebrcOsZQMybnUuwLk)")
