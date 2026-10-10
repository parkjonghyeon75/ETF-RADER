# pages/2_KRX_ETF_검증.py
# 기존 app.py는 수정하지 않습니다.
# Streamlit Cloud에서 별도 페이지로 동작합니다.

from pathlib import Path
import re
import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="KRX ETF 분류 검증", layout="wide")
st.title("KRX ETF 분류 검증 (시험 5건)")
st.caption("기존 app.py와 분리된 검증 페이지입니다. 이 페이지는 백테스트 데이터를 수정하지 않습니다.")

API_URL = "https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd"
SAMPLE_URL = "https://data-dbg.krx.co.kr/svc/sample/apis/etp/etf_bydd_trd"
CSV_PATH = Path("KRX_DELISTED_ALL.csv")


def normalize_date(value):
    """2012/05/21, 2012-05-21, 20120521 -> YYYYMMDD."""
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) != 8:
        return None
    try:
        return pd.to_datetime(digits, format="%Y%m%d").strftime("%Y%m%d")
    except (ValueError, TypeError):
        return None


def normalize_name(value):
    return re.sub(r"[\W_]+", "", str(value or "")).upper()


def normalize_code(value):
    # ISU_CD may be a 12-character standard code (KR...); CSV may contain short code.
    digits = re.sub(r"\D", "", str(value or ""))
    return digits[-6:] if len(digits) >= 6 else digits


def get_rows(payload):
    if isinstance(payload, dict):
        rows = payload.get("OutBlock_1")
        if rows is None:
            # Some responses may wrap the output block in another object.
            for value in payload.values():
                if isinstance(value, dict) and "OutBlock_1" in value:
                    rows = value["OutBlock_1"]
                    break
    else:
        rows = None

    if isinstance(rows, dict):
        rows = [rows]
    if rows is None:
        raise ValueError(
            "응답에 OutBlock_1이 없습니다. 응답 필드: "
            + ", ".join(map(str, payload.keys())) if isinstance(payload, dict)
            else f"JSON 객체가 아닙니다: {type(payload).__name__}"
        )
    if not isinstance(rows, list):
        raise ValueError("OutBlock_1 형식이 list/dict가 아닙니다.")
    return rows


def fetch_etf_day(date_yyyymmdd, api_key, sample=False):
    base = SAMPLE_URL if sample else API_URL
    response = requests.get(
        base,
        params={"basDd": date_yyyymmdd},
        headers=({"AUTH_KEY": api_key} if api_key and not sample else {}),
        timeout=25,
    )
    response.raise_for_status()
    try:
        payload = response.json()
    except ValueError:
        raise ValueError(f"JSON이 아닌 응답입니다: {response.text[:250]}")
    rows = get_rows(payload)
    return pd.DataFrame(rows), response.status_code


def candidate_rows(df):
    # ETF가 아닐 수 있는 유형도 있으므로 후보로만 선정하며 ETF 확정 판정은 하지 않습니다.
    allowed = {"수익증권", "투자회사", "부동산투자회사", "선박투자회사"}
    sec = df["증권구분"].astype(str).str.strip()
    candidates = df[sec.isin(allowed)].copy()
    candidates["_폐지일정규화"] = candidates["폐지일"].map(normalize_date)
    candidates = candidates[candidates["_폐지일정규화"].notna()].copy()
    return candidates


st.markdown(
    """
    **검증 범위**
    - 날짜 형식: `YYYY/MM/DD`를 KRX API 형식 `YYYYMMDD`로 변환합니다.
    - API 주소: KRX ETF 일별매매정보의 공식 엔드포인트를 사용합니다.
    - 시험 대상: 원본 CSV에서 ETF일 가능성을 추가 확인할 증권구분을 가진 종목 중 최대 5건.
    - 종목명/코드 일치는 참고 신호일 뿐이며, 자동으로 ETF 확정 처리하지 않습니다.
    """
)

if not CSV_PATH.exists():
    st.error(
        f"`{CSV_PATH.name}`을 찾지 못했습니다. GitHub 저장소의 app.py와 같은 루트 폴더에 "
        "KRX_DELISTED_ALL.csv를 업로드하고 커밋했는지 확인하세요."
    )
    st.stop()

try:
    source_df = pd.read_csv(CSV_PATH, dtype=str, encoding="utf-8-sig").fillna("")
except Exception as exc:
    st.error(f"CSV 읽기 실패: {type(exc).__name__}: {exc}")
    st.stop()

required_columns = {"종목코드", "종목명", "증권구분", "폐지일"}
missing = required_columns - set(source_df.columns)
if missing:
    st.error(f"CSV 필수 컬럼이 없습니다: {', '.join(sorted(missing))}")
    st.write("현재 컬럼:", list(source_df.columns))
    st.stop()

st.success(f"CSV 읽기 성공: {len(source_df):,}행")
st.write("날짜 형식 예시:", source_df["폐지일"].head(3).tolist())
st.write("변환 결과 예시:", [normalize_date(x) for x in source_df["폐지일"].head(3)])

candidates = candidate_rows(source_df)
st.write(f"분류 검토 후보: {len(candidates):,}건 (ETF 확정 목록이 아닙니다)")

with st.expander("후보 유형 분포", expanded=False):
    st.dataframe(
        candidates["증권구분"].value_counts().rename_axis("증권구분").reset_index(name="건수"),
        use_container_width=True,
        hide_index=True,
    )

with st.form("krx_test_form"):
    api_key = st.text_input(
        "KRX Open API 인증키",
        type="password",
        value=st.secrets.get("KRX_API_KEY", ""),
        help="권장: Streamlit Cloud → Settings → Secrets에 KRX_API_KEY를 등록하세요. 채팅이나 코드에 키를 적지 마세요.",
    )
    use_sample = st.checkbox(
        "공개 샘플 주소만 시험 (인증키 없이 연결/응답 형식 확인)",
        value=True,
        help="샘플 응답은 실제 상장폐지 이력 검증이 아닙니다. 연결 및 응답 구조만 확인합니다.",
    )
    run_test = st.form_submit_button("5건 시험 검증 실행", type="primary")

if run_test:
    test = candidates.head(5).copy()
    if test.empty:
        st.error("시험할 후보가 없습니다.")
        st.stop()
    if not use_sample and not api_key.strip():
        st.error("실제 API 호출에는 승인된 KRX API 인증키가 필요합니다.")
        st.stop()

    results = []
    api_errors = []
    progress = st.progress(0)
    status = st.empty()

    for idx, (_, row) in enumerate(test.iterrows(), start=1):
        delist_date = row["_폐지일정규화"]
        delist_dt = pd.to_datetime(delist_date, format="%Y%m%d")
        # 폐지일 이전 1~5 calendar days, 평일만 시도. 최대 5개 API calls per target.
        attempt_dates = []
        for offset in range(1, 8):
            d = delist_dt - pd.Timedelta(days=offset)
            if d.weekday() < 5:
                attempt_dates.append(d.strftime("%Y%m%d"))
            if len(attempt_dates) >= 5:
                break

        found = False
        last_status = ""
        for query_date in attempt_dates:
            try:
                day_df, http_status = fetch_etf_day(
                    query_date, api_key.strip(), sample=use_sample
                )
                last_status = f"HTTP {http_status}; {len(day_df)} rows"
                if not day_df.empty:
                    # Keep reference data for the result audit.
                    for _, etf in day_df.iterrows():
                        code_match = (
                            normalize_code(row["종목코드"])
                            and normalize_code(row["종목코드"]) == normalize_code(etf.get("ISU_CD", ""))
                        )
                        name_match = (
                            normalize_name(row["종목명"])
                            and normalize_name(row["종목명"]) == normalize_name(etf.get("ISU_NM", ""))
                        )
                        if code_match or name_match:
                            results.append({
                                "원본종목코드": row["종목코드"],
                                "원본종목명": row["종목명"],
                                "증권구분": row["증권구분"],
                                "폐지일": row["폐지일"],
                                "조회기준일": query_date,
                                "KRX종목코드": etf.get("ISU_CD", ""),
                                "KRX종목명": etf.get("ISU_NM", ""),
                                "코드일치": bool(code_match),
                                "이름일치": bool(name_match),
                                "판정": "일치 후보 - 추가 확인 필요",
                                "API모드": "샘플" if use_sample else "실제 API",
                            })
                            found = True
                if found:
                    break
            except Exception as exc:
                api_errors.append({
                    "원본종목명": row["종목명"],
                    "폐지일": row["폐지일"],
                    "조회기준일": query_date,
                    "오류": f"{type(exc).__name__}: {exc}",
                })
                last_status = f"오류: {type(exc).__name__}: {exc}"
                break
            time.sleep(0.15)

        if not found:
            results.append({
                "원본종목코드": row["종목코드"],
                "원본종목명": row["종목명"],
                "증권구분": row["증권구분"],
                "폐지일": row["폐지일"],
                "조회기준일": ";".join(attempt_dates),
                "KRX종목코드": "",
                "KRX종목명": "",
                "코드일치": False,
                "이름일치": False,
                "판정": (
                    "샘플 응답으로는 이력 판정 불가"
                    if use_sample
                    else "일치 없음 - ETF 아님으로 단정 금지"
                ),
                "API모드": "샘플" if use_sample else "실제 API",
                "마지막상태": last_status,
            })

        progress.progress(idx / len(test))
        status.write(f"{idx}/{len(test)}건 처리")

    result_df = pd.DataFrame(results)
    st.subheader("시험 결과")
    st.dataframe(result_df, use_container_width=True, hide_index=True)

    st.download_button(
        "시험 결과 CSV 다운로드",
        data=result_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="KRX_ETF_TYPE_TEST_5.csv",
        mime="text/csv",
    )

    if api_errors:
        st.warning("일부 API 호출에서 오류가 발생했습니다. 오류 상세:")
        st.dataframe(pd.DataFrame(api_errors), use_container_width=True, hide_index=True)

    st.info(
        "이 시험은 최대 5개 원본 후보를 대상으로 한 기술 검증입니다. "
        "샘플 모드에서는 ETF 이력 일치 여부를 판정할 수 없습니다. "
        "실제 API 모드에서 일치가 없더라도 ETF가 아니라고 확정하지 마세요. "
        "아직 백테스트 데이터는 수정되지 않았습니다."
    )

with st.expander("연결 정보 / 공식 API 스펙"):
    st.code(API_URL)
    st.write("요청 파라미터: basDd=YYYYMMDD")
    st.write("인증 헤더: AUTH_KEY")
    st.write("예상 응답 블록: OutBlock_1 (필드 예: BAS_DD, ISU_CD, ISU_NM)")
    st.markdown("[KRX ETF 일별매매정보 공식 안내](https://openapi.krx.co.kr/contents/OPP/USES/service/OPPUSES003_S2.cmd?BO_ID=nrEpCLaZpoLCTzPUMxuF)")
