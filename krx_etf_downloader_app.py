import io
import json
import time
import zipfile
from datetime import date, timedelta, datetime

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="ETF RADAR | KRX 자동 수집", layout="wide")
st.title("ETF RADAR — KRX ETF 시세 자동 수집")
st.caption("별도 진단 앱입니다. 운영 app.py를 수정하지 않으며, 백테스트를 재계산하지 않습니다.")

BASE_URL = "https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd"

def get_api_key():
    try:
        return str(st.secrets.get("KRX_OPENAPI_KEY", "")).strip()
    except Exception:
        return ""

def request_etf_day(day: date, key: str):
    ymd = day.strftime("%Y%m%d")
    r = requests.get(
        BASE_URL,
        params={"basDd": ymd},
        headers={"AUTH_KEY": key, "Accept": "application/json"},
        timeout=25,
    )
    body_text = r.text
    try:
        payload = r.json()
    except Exception:
        payload = None

    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}; 응답={body_text[:500]}")
    if not isinstance(payload, dict):
        raise RuntimeError(f"JSON 객체가 아닌 응답; 응답={body_text[:500]}")
    if "OutBlock_1" not in payload:
        # KRX error payload is kept in the diagnostic message, never treated as success.
        raise RuntimeError(f"응답에 OutBlock_1 없음; 응답={json.dumps(payload, ensure_ascii=False)[:800]}")
    rows = payload["OutBlock_1"]
    if not isinstance(rows, list):
        raise RuntimeError("OutBlock_1이 배열이 아닙니다.")
    return rows, body_text, r.status_code, r.headers.get("Content-Type", "")

def business_days(start: date, end: date):
    days = pd.date_range(start=start, end=end, freq="B")
    return [x.date() for x in days]

key = get_api_key()
if key:
    st.success("KRX_OPENAPI_KEY가 Streamlit Secrets에 설정되어 있습니다.")
else:
    st.error("KRX_OPENAPI_KEY를 찾지 못했습니다. Streamlit Cloud → 앱 → Settings → Secrets에 다음을 추가하세요.")
    st.code('KRX_OPENAPI_KEY = "발급받은_실제_KRX_인증키"')
    st.markdown("인증키를 채팅이나 코드에 붙여넣지 마세요. Secrets에만 입력하세요.")

with st.expander("API 연결 정보", expanded=False):
    st.write("공식 API 경로: `GET https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd`")
    st.write("인증: `AUTH_KEY` 요청 헤더 · 기준일: `basDd=YYYYMMDD`")
    st.write("ETF 가격 데이터의 종목코드는 `ISU_CD` 필드를 원문 그대로 보존합니다.")

st.subheader("1. 연결 시험")
test_date = st.date_input("시험 기준일", value=date(2026, 10, 8), key="test_date")
if st.button("KRX API 연결 시험", type="primary", disabled=not bool(key)):
    with st.spinner("KRX API 응답 확인 중..."):
        try:
            rows, raw, status, ctype = request_etf_day(test_date, key)
            st.session_state["krx_test_raw"] = raw
            st.session_state["krx_test_meta"] = {
                "date": test_date.isoformat(), "http_status": status,
                "content_type": ctype, "row_count": len(rows),
                "columns": list(rows[0].keys()) if rows else [],
            }
            if rows:
                st.success(f"API 응답 구조 확인: HTTP {status}, 데이터 {len(rows):,}행")
                st.write("컬럼:", list(rows[0].keys()))
                st.dataframe(pd.DataFrame(rows).head(20), use_container_width=True)
            else:
                st.warning("OutBlock_1은 존재하지만 해당 날짜 데이터가 0행입니다. 영업일인지 확인하세요.")
        except Exception as e:
            st.session_state["krx_test_error"] = str(e)
            st.error(f"연결 시험 실패: {e}")
            st.caption("이 결과는 실패로 기록되며, 데이터 수집 성공으로 처리하지 않습니다.")

st.subheader("2. 날짜 범위 ETF 시세 수집")
st.write("먼저 5영업일 이내로 시험하세요. 날짜별 실제 응답을 확인하고, 실패 날짜와 원문 오류를 함께 저장합니다.")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작일", value=date(2026, 10, 1), key="start_date")
with col2:
    end_date = st.date_input("종료일", value=date(2026, 10, 9), key="end_date")
max_days = st.number_input("최대 요청 영업일 수 (첫 시험은 5 권장)", min_value=1, max_value=250, value=5, step=1)
delay = st.slider("요청 간 대기 시간(초)", min_value=0.0, max_value=2.0, value=0.2, step=0.1)
if st.button("선택 기간 ETF 시세 수집", disabled=not bool(key)):
    if end_date < start_date:
        st.error("종료일은 시작일보다 빠를 수 없습니다.")
    else:
        dates = business_days(start_date, end_date)
        if len(dates) > int(max_days):
            st.error(f"선택 기간은 {len(dates)}영업일입니다. 현재 최대 요청은 {int(max_days)}일입니다. 기간을 줄이거나 최대 요청일 수를 조정하세요.")
        else:
            rows_all, logs, raw_files = [], [], {}
            progress = st.progress(0)
            status_box = st.empty()
            for i, d in enumerate(dates):
                status_box.write(f"조회 중: {d.isoformat()} ({i+1}/{len(dates)})")
                try:
                    rows, raw, status, ctype = request_etf_day(d, key)
                    raw_files[f"raw_api/{d.strftime('%Y%m%d')}.json"] = raw.encode("utf-8")
                    for row in rows:
                        row = dict(row)
                        row["_REQUEST_DATE"] = d.strftime("%Y%m%d")
                        rows_all.append(row)
                    logs.append({
                        "요청일": d.strftime("%Y%m%d"), "HTTP상태": status,
                        "조회상태": "응답구조확인",
                        "응답행수": len(rows), "컬럼": "|".join(list(rows[0].keys())) if rows else "",
                        "오류": "" if rows else "OutBlock_1 0행 (휴장일/데이터 여부 확인 필요)",
                        "Content-Type": ctype,
                    })
                except Exception as e:
                    logs.append({
                        "요청일": d.strftime("%Y%m%d"), "HTTP상태": "",
                        "조회상태": "실패", "응답행수": 0, "컬럼": "",
                        "오류": str(e), "Content-Type": "",
                    })
                progress.progress((i + 1) / len(dates))
                if delay:
                    time.sleep(delay)
            data_df = pd.DataFrame(rows_all)
            log_df = pd.DataFrame(logs)
            st.session_state["collected_data"] = data_df
            st.session_state["collected_logs"] = log_df
            st.session_state["collected_raw"] = raw_files
            st.session_state["collection_period"] = (start_date.isoformat(), end_date.isoformat())
            good = int((log_df["조회상태"] == "응답구조확인").sum()) if not log_df.empty else 0
            failed = int((log_df["조회상태"] == "실패").sum()) if not log_df.empty else 0
            st.write(f"조회 시도 {len(dates)}일 · 응답구조 확인 {good}일 · 실패 {failed}일 · 수집 가격행 {len(data_df):,}건")
            st.dataframe(log_df, use_container_width=True)
            if not data_df.empty:
                st.dataframe(data_df.head(30), use_container_width=True)
            if failed:
                st.warning("실패 날짜가 있습니다. 실패가 남아 있으면 전체 수집 성공으로 간주하지 마세요.")
            elif data_df.empty:
                st.warning("오류는 없지만 가격 행이 0건입니다. 응답 원문을 확인해야 합니다.")
            else:
                st.info("수집 결과를 저장할 수 있습니다. 이것은 API 응답 수집 결과이며, 상장폐지 ETF 매칭이나 백테스트 검증 성공을 뜻하지 않습니다.")

if "collected_logs" in st.session_state:
    st.subheader("3. 다운로드")
    data_df = st.session_state["collected_data"]
    log_df = st.session_state["collected_logs"]
    raw_files = st.session_state["collected_raw"]
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("KRX_ETF_DAILY_RAW.csv", data_df.to_csv(index=False).encode("utf-8-sig"))
        z.writestr("KRX_API_DIAGNOSTIC_LOG.csv", log_df.to_csv(index=False).encode("utf-8-sig"))
        for name, content in raw_files.items():
            z.writestr(name, content)
        z.writestr("README.txt",
            "KRX ETF API 수집 결과\n"
            "KRX_ETF_DAILY_RAW.csv: 날짜별 ETF 일별매매정보 응답 행\n"
            "KRX_API_DIAGNOSTIC_LOG.csv: 날짜별 요청 결과와 오류\n"
            "raw_api/: 날짜별 원본 JSON 응답\n"
            "이 ZIP은 상장폐지 ETF 식별/매칭 성공 또는 백테스트 검증 성공을 의미하지 않습니다.\n"
        )
    st.download_button(
        "📦 KRX_ETF_API_DIAGNOSTIC.zip 다운로드",
        data=zip_buf.getvalue(),
        file_name="KRX_ETF_API_DIAGNOSTIC.zip",
        mime="application/zip",
        use_container_width=True,
    )
    st.download_button(
        "시세 CSV 다운로드",
        data=data_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="KRX_ETF_DAILY_RAW.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.download_button(
        "진단 로그 CSV 다운로드",
        data=log_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="KRX_API_DIAGNOSTIC_LOG.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.divider()
st.caption("안전 규칙: 코드/이름 추정으로 ETF를 분류하지 않음 · 원본 API 응답 보존 · 실패를 성공으로 표시하지 않음 · 운영 app.py 및 백테스트 데이터 미수정")
