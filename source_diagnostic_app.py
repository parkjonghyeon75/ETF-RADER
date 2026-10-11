import io
import zipfile
from datetime import datetime
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="ETF RADAR 기준자료 수집기", layout="wide")
st.title("ETF RADAR — KRX 기준자료 수집·진단")
st.caption("기존 운영용 app.py와 별도로 실행하는 자료 준비 도구입니다. 자동 매칭이나 백테스트 재계산은 하지 않습니다.")

st.warning(
    "이 도구는 KRX API 인증키가 필요한 API를 임의로 추측해 호출하지 않습니다. "
    "먼저 공식 KRX 화면에서 내려받은 CSV를 업로드해 구조를 검증하고, "
    "실제 API 응답을 확보한 경우에만 응답 원본을 기록합니다."
)

st.header("1. KRX에서 내려받은 파일 업로드")
st.markdown(
    "KRX 정보데이터시스템 또는 KRX ETP 상품정보 화면에서 내려받은 파일을 업로드하세요. "
    "상장폐지 전체 목록과 ETF 상품 기준정보를 각각 받을 수 있다면 모두 올려주세요."
)
uploaded = st.file_uploader(
    "CSV 파일 선택 (여러 파일 가능)",
    type=["csv", "txt", "xlsx", "xls"],
    accept_multiple_files=True
)

def read_uploaded(file):
    raw = file.getvalue()
    suffix = file.name.lower()
    if suffix.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(raw))
        encoding = "excel"
    else:
        df = None
        encoding = None
        errors = []
        for enc in ["utf-8-sig", "cp949", "euc-kr", "utf-8"]:
            try:
                df = pd.read_csv(io.BytesIO(raw), encoding=enc, dtype=str)
                encoding = enc
                break
            except Exception as e:
                errors.append(f"{enc}: {e}")
        if df is None:
            raise ValueError("CSV를 읽을 수 없습니다. " + " / ".join(errors[-2:]))
    return raw, df, encoding

def code_candidates(df):
    preferred = ["단축코드", "종목코드", "ISU_SRT_CD", "SRT_CD", "Code", "code", "ISU_CD", "표준코드", "ISIN"]
    return [c for c in preferred if c in df.columns]

def inspect_file(name, df, encoding):
    st.subheader(name)
    st.write(f"행 수: **{len(df):,}** · 열 수: **{len(df.columns):,}** · 인코딩: `{encoding}`")
    st.write("컬럼명:", list(map(str, df.columns)))
    candidates = code_candidates(df)
    if candidates:
        st.write("식별자 후보 컬럼:", candidates)
        st.dataframe(df[candidates].head(12), use_container_width=True)
    else:
        st.warning("일반적인 종목코드/ISIN 컬럼명을 찾지 못했습니다. 전체 컬럼을 확인하세요.")
    st.dataframe(df.head(8), use_container_width=True)

records = []
if uploaded:
    for f in uploaded:
        try:
            raw, df, enc = read_uploaded(f)
            inspect_file(f.name, df, enc)
            records.append((f.name, raw, df, enc))
        except Exception as e:
            st.error(f"{f.name} 읽기 실패: {e}")

st.divider()
st.header("2. KRX 원본자료 직접 수집")
st.markdown(
    "공식 KRX 다운로드 링크 또는 API 주소가 확인되어 있다면 여기서 직접 요청해 응답 원본을 저장할 수 있습니다. "
    "API 명세를 모르는 상태에서 주소나 인증키 형식을 추측하지 않습니다."
)
with st.form("fetch_form"):
    fetch_url = st.text_input("공식 KRX 다운로드/API URL", placeholder="https://...")
    method = st.selectbox("요청 방식", ["GET", "POST"])
    auth_key = st.text_input("인증키 (선택)", type="password")
    key_location = st.radio("인증키 전달 방식", ["사용 안 함", "쿼리 파라미터", "헤더"], horizontal=True)
    key_name = st.text_input("인증키 필드명", value="serviceKey")
    extra_params = st.text_area("추가 쿼리 파라미터 (한 줄에 key=value)", placeholder="예: basDd=20261011")
    extra_headers = st.text_area("추가 헤더 (한 줄에 key: value)", placeholder="예: Accept: application/json")
    submitted = st.form_submit_button("KRX 주소 요청 및 응답 확인", type="primary")

if submitted:
    if not fetch_url.strip().startswith("https://"):
        st.error("안전 확인을 위해 https:// 로 시작하는 공식 URL을 입력해 주세요.")
    else:
        try:
            params = {}
            for line in extra_params.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    params[k.strip()] = v.strip()
            headers = {}
            for line in extra_headers.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    headers[k.strip()] = v.strip()
            if auth_key and key_location == "쿼리 파라미터":
                params[key_name.strip() or "serviceKey"] = auth_key
            elif auth_key and key_location == "헤더":
                headers[key_name.strip() or "Authorization"] = auth_key
            with st.spinner("입력한 공식 주소에 요청 중..."):
                if method == "GET":
                    response = requests.get(fetch_url.strip(), params=params, headers=headers, timeout=30)
                else:
                    response = requests.post(fetch_url.strip(), params=params, headers=headers, timeout=30)
            st.session_state["fetched_response"] = {
                "url": response.url,
                "status": response.status_code,
                "content_type": response.headers.get("Content-Type", ""),
                "body": response.content,
                "text": response.text[:12000]
            }
        except Exception as e:
            st.error(f"요청 실패: {type(e).__name__}: {e}")

fetched = st.session_state.get("fetched_response")
if fetched:
    st.write(f"HTTP 상태: **{fetched['status']}** · Content-Type: `{fetched['content_type']}` · 응답 크기: **{len(fetched['body']):,} bytes**")
    st.write("요청 URL (인증키가 포함될 수 있으므로 공유 전 확인하세요):")
    st.code(fetched["url"])
    st.subheader("응답 본문 미리보기")
    st.code(fetched["text"], language="json" if "json" in fetched["content_type"].lower() else "text")
    st.download_button(
        "원본 API 응답 다운로드",
        data=fetched["body"],
        file_name="krx_api_response.bin",
        mime="application/octet-stream",
        use_container_width=True
    )

st.divider()
st.header("3. 공식 KRX API 응답 진단")
st.markdown(
    "실제 API 응답 본문(JSON/CSV/XML)을 파일로 저장했다면 업로드하세요. "
    "이 앱은 응답의 키/컬럼/샘플을 보여주며, 종목코드나 ISIN을 임의 추정하지 않습니다."
)
api_files = st.file_uploader(
    "API 응답 원본 파일 업로드",
    type=["json", "csv", "txt", "xml"],
    accept_multiple_files=True,
    key="api_files"
)
api_summary = []
for f in api_files or []:
    raw = f.getvalue()
    item = {"파일명": f.name, "바이트": len(raw), "앞부분": raw[:1500].decode("utf-8", errors="replace")}
    api_summary.append(item)
    st.subheader(f.name)
    st.code(item["앞부분"], language="json" if f.name.lower().endswith(".json") else "text")
    if f.name.lower().endswith(".csv"):
        try:
            df = pd.read_csv(io.BytesIO(raw), dtype=str, encoding="utf-8-sig")
            st.write("컬럼명:", list(df.columns))
            st.dataframe(df.head(10), use_container_width=True)
        except Exception as e:
            st.error(f"CSV 파싱 실패: {e}")

st.divider()
st.header("4. 진단 패키지 다운로드")
st.write("업로드한 파일의 원본, 컬럼/행 수 진단표, API 응답 미리보기 정보를 ZIP으로 묶습니다.")
if st.button("진단 ZIP 만들기", type="primary", use_container_width=True):
    buffer = io.BytesIO()
    manifest = {
        "생성시각": datetime.now().isoformat(timespec="seconds"),
        "안내": "이 패키지는 자료 구조 진단용이며 매칭 성공이나 백테스트 검증을 의미하지 않습니다."
    }
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("README.txt",
                   "ETF RADAR 기준자료 진단 패키지\n"
                   "원본 파일은 업로드한 그대로 포함됩니다.\n"
                   "이 ZIP은 KRX 데이터의 정확성이나 매칭 성공을 보증하지 않습니다.\n")
        for name, raw, df, enc in records:
            safe = name.replace("/", "_").replace("\\", "_")
            z.writestr(f"uploaded_sources/{safe}", raw)
        for f in api_files or []:
            safe = f.name.replace("/", "_").replace("\\", "_")
            z.writestr(f"api_responses/{safe}", f.getvalue())
        if fetched:
            z.writestr("api_responses/krx_api_response.bin", fetched["body"])
            z.writestr("api_responses/response_metadata.txt",
                       f"HTTP status: {fetched['status']}\nContent-Type: {fetched['content_type']}\nURL: {fetched['url']}\n")
        for name, raw, df, enc in records:
            report = pd.DataFrame([{
                "파일명": name, "행수": len(df), "열수": len(df.columns),
                "인코딩": enc, "컬럼명": " | ".join(map(str, df.columns)),
                "식별자후보": " | ".join(code_candidates(df))
            }])
            z.writestr(f"reports/{name}_structure.csv", report.to_csv(index=False).encode("utf-8-sig"))
        z.writestr("manifest.txt", "\n".join(f"{k}: {v}" for k, v in manifest.items()))
    st.download_button(
        "📦 ETF_RADAR_SOURCE_DIAGNOSTIC.zip 다운로드",
        data=buffer.getvalue(),
        file_name="ETF_RADAR_SOURCE_DIAGNOSTIC.zip",
        mime="application/zip",
        use_container_width=True
    )

st.info(
    "중요: 이 버전은 자료를 업로드·검사·패키징하는 진단 도구입니다. "
    "직접 수집은 사용자가 제공한 공식 HTTPS 주소와 API 명세에 따라 동작합니다. "
    "KRX URL/파라미터/인증 방식이 확인되지 않은 상태에서는 올바른 자료를 자동으로 찾았다고 간주하지 마세요."
)
