# krx_etf_verify_app.py
# Standalone Streamlit app for a 5-row KRX ETF API smoke test.
# Does not modify app.py or any backtest data.

import os
import re
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="KRX ETF 분류 검증", layout="wide")
st.title("KRX ETF 분류 검증")
st.caption("기존 ETF_RADAR 앱과 분리된 시험 앱입니다. 최대 5개 후보만 검사하며 백테스트 데이터는 수정하지 않습니다.")

CSV_PATH = Path(__file__).resolve().parent / "KRX_DELISTED_ALL.csv"
SAMPLE_URL = "https://data-dbg.krx.co.kr/svc/sample/apis/etp/etf_bydd_trd"
API_URL = "https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd"


def norm_date(value):
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) != 8:
        return None
    try:
        return pd.to_datetime(digits, format="%Y%m%d").strftime("%Y%m%d")
    except (ValueError, TypeError):
        return None


def norm_code(value):
    digits = re.sub(r"\D", "", str(value or ""))
    return digits[-6:] if len(digits) >= 6 else digits


def norm_name(value):
    return re.sub(r"[\W_]+", "", str(value or "")).upper()


def parse_rows(payload):
    if not isinstance(payload, dict):
        raise ValueError(f"응답이 JSON 객체가 아닙니다: {type(payload).__name__}")
    rows = payload.get("OutBlock_1")
    if isinstance(rows, dict):
        rows = [rows]
    if not isinstance(rows, list):
        raise ValueError(
            "응답에 OutBlock_1 목록이 없습니다. 응답 키: "
            + ", ".join(map(str, payload.keys()))
        )
    return rows


def call_krx(date, sample, api_key):
    url = SAMPLE_URL if sample else API_URL
    headers = {} if sample else {"AUTH_KEY": api_key}
    response = requests.get(url, params={"basDd": date}, headers=headers, timeout=25)
    response.raise_for_status()
    try:
        payload = response.json()
    except ValueError:
        raise ValueError(f"JSON 응답이 아닙니다: {response.text[:200]}")
    return pd.DataFrame(parse_rows(payload)), response.status_code


if not CSV_PATH.exists():
    st.error("KRX_DELISTED_ALL.csv를 찾지 못했습니다. 새 Streamlit 앱도 기존 GitHub 저장소를 사용하고, Main file path를 krx_etf_verify_app.py로 지정해야 합니다.")
    st.stop()

try:
    source = pd.read_csv(CSV_PATH, dtype=str, encoding="utf-8-sig").fillna("")
except Exception as exc:
    st.error(f"CSV 읽기 오류: {type(exc).__name__}: {exc}")
    st.stop()

required = {"종목코드", "종목명", "증권구분", "폐지일"}
missing = required - set(source.columns)
if missing:
    st.error(f"CSV 필수 컬럼 누락: {', '.join(sorted(missing))}")
    st.write("실제 컬럼:", list(source.columns))
    st.stop()

source["폐지일_API형식"] = source["폐지일"].map(norm_date)
st.success(f"CSV 읽기 성공: {len(source):,}행")
st.write("날짜 변환 예시")
st.dataframe(
    pd.DataFrame({
        "원본 폐지일": source["폐지일"].head(5),
        "API용 YYYYMMDD": source["폐지일_API형식"].head(5),
    }),
    hide_index=True,
    width="stretch",
)

# These are candidate security categories only, NOT an ETF classification.
allowed = {"수익증권", "투자회사", "부동산투자회사", "선박투자회사"}
candidates = source[
    source["증권구분"].astype(str).str.strip().isin(allowed)
    & source["폐지일_API형식"].notna()
].copy()

st.warning("증권구분은 후보 선별에만 사용합니다. 이 값만으로 ETF라고 확정하지 않습니다.")
st.write(f"검토 후보: {len(candidates):,}건 / 시험 실행은 최대 5건")

with st.expander("후보 증권구분 분포"):
    st.dataframe(
        candidates["증권구분"].value_counts().rename_axis("증권구분").reset_index(name="건수"),
        hide_index=True,
        width="stretch",
    )

with st.form("test"):
    sample_mode = st.checkbox("공개 샘플 API만 시험 (인증키 없이 연결/응답 형식 확인)", value=True)
    secret_key = st.text_input(
        "KRX API 인증키 (실제 API 모드에서만 필요)",
        value=st.secrets.get("KRX_API_KEY", os.getenv("KRX_API_KEY", "")),
        type="password",
        help="실제 API는 KRX에서 발급 및 승인된 키가 필요합니다. 키를 코드나 채팅에 올리지 마세요.",
    )
    submitted = st.form_submit_button("최대 5건 시험 실행", type="primary")

if submitted:
    if candidates.empty:
        st.error("검토 후보가 없습니다.")
        st.stop()
    if not sample_mode and not secret_key.strip():
        st.error("실제 API 모드에는 승인된 KRX API 인증키가 필요합니다.")
        st.stop()

    test = candidates.head(5)
    results = []
    api_error = None

    # First verify the endpoint/response schema on one known reference date.
    st.subheader("1) API 주소 및 응답 형식 확인")
    try:
        test_date = "20200414"
        ref_df, status_code = call_krx(test_date, sample_mode, secret_key.strip())
        expected = {"ISU_CD", "ISU_NM"}
        has_fields = expected.issubset(set(ref_df.columns))
        st.write(f"주소: `{SAMPLE_URL if sample_mode else API_URL}`")
        st.write(f"HTTP 상태: {status_code}")
        st.write(f"기준일: {test_date}")
        st.write(f"응답 행 수: {len(ref_df)}")
        st.write(f"종목코드/종목명 필드 확인: {'통과' if has_fields else '실패'}")
        if not has_fields:
            st.write("실제 응답 필드:", list(ref_df.columns))
            st.error("응답 구조가 예상과 다릅니다. 여기서 중단합니다.")
            st.stop()
    except Exception as exc:
        st.error(f"API 주소 또는 응답 형식 확인 실패: {type(exc).__name__}: {exc}")
        st.info("샘플 API 연결 실패는 상장폐지 ETF 여부를 의미하지 않습니다. 결과를 확정하지 않았습니다.")
        st.stop()

    st.subheader("2) 후보 5건과 기준일 ETF 목록 대조")
    ref_df = ref_df.copy()
    ref_df["_code"] = ref_df["ISU_CD"].map(norm_code)
    ref_df["_name"] = ref_df["ISU_NM"].map(norm_name)

    for _, row in test.iterrows():
        code = norm_code(row["종목코드"])
        name = norm_name(row["종목명"])
        code_matches = ref_df[ref_df["_code"].eq(code)] if code else ref_df.iloc[0:0]
        name_matches = ref_df[ref_df["_name"].eq(name)] if name else ref_df.iloc[0:0]
        matched = not code_matches.empty or not name_matches.empty
        match = code_matches.iloc[0] if not code_matches.empty else (
            name_matches.iloc[0] if not name_matches.empty else None
        )
        results.append({
            "원본종목코드": row["종목코드"],
            "원본종목명": row["종목명"],
            "증권구분": row["증권구분"],
            "폐지일": row["폐지일"],
            "비교기준일": test_date,
            "KRX종목코드": match["ISU_CD"] if match is not None else "",
            "KRX종목명": match["ISU_NM"] if match is not None else "",
            "코드일치": not code_matches.empty,
            "이름일치": not name_matches.empty,
            "결과": (
                "기준일 목록과 일치 - 후보일 뿐, ETF 확정 아님"
                if matched
                else "기준일 목록과 불일치 - ETF 아님으로 단정 금지"
            ),
            "API모드": "공개 샘플" if sample_mode else "실제 인증 API",
        })

    result_df = pd.DataFrame(results)
    st.dataframe(result_df, hide_index=True, width="stretch")
    st.download_button(
        "시험 결과 CSV 다운로드",
        result_df.to_csv(index=False).encode("utf-8-sig"),
        "KRX_ETF_TYPE_TEST_5.csv",
        "text/csv",
    )
    st.info(
        "공개 샘플은 2020-04-14 기준의 API 연결/스키마 시험입니다. "
        "샘플 데이터와 일치하지 않는다고 해서 해당 종목이 ETF가 아니라고 결론 내릴 수 없습니다. "
        "상장폐지일 직전 실제 거래일을 각각 조회하고 종목코드/ISIN을 대조해야 합니다. "
        "이 앱은 원본 CSV나 백테스트 데이터를 변경하지 않습니다."
    )

with st.expander("API 명세"):
    st.write("샘플 주소:", SAMPLE_URL)
    st.write("실제 주소:", API_URL)
    st.write("요청 파라미터: `basDd=YYYYMMDD`")
    st.write("인증 헤더: `AUTH_KEY` (실제 API만)")
    st.markdown("[KRX 공식 ETF 일별매매정보 안내](https://openapi.krx.co.kr/contents/OPP/USES/service/OPPUSES003_S2.cmd?BO_ID=nrEpCLaZpoLCTzPUMxuF)")
