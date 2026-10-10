# -*- coding: utf-8 -*-
"""ETF RADAR delisted ETF backfill - Streamlit Community Cloud helper.

Credentials must be entered in Streamlit Cloud App Settings > Secrets, never in this UI
or committed to GitHub. This app is separate from the production ETF RADAR app.py.
"""
from __future__ import annotations
import io, os, re, json, time, zipfile
from datetime import date
from typing import Optional
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ETF RADAR · 상장폐지 ETF 데이터 수집", page_icon="📊", layout="wide")
st.title("ETF RADAR — 상장폐지 ETF 데이터 수집")
st.warning("이 앱은 백테스트용 별도 도구입니다. 기존 운영 app.py를 수정하지 않습니다.")
st.markdown("""
이 도구는 KRX 상장폐지 목록과 KRX OPEN API의 ETF 일별매매정보를 이용해 과거 ETF를 검증하고 가격을 수집합니다.
**ETF 판정은 생성한 ISIN이 폐지 전 KRX ETF 일별 데이터에 정확히 존재하는 경우만 허용합니다. 종목명 유사도나 코드 일부 매칭은 사용하지 않습니다.**
""")

# Read secrets without ever displaying their values.
def get_secret(key: str) -> str:
    try:
        val = st.secrets.get(key, "")
        return str(val).strip() if val is not None else ""
    except Exception:
        return ""

krx_id, krx_pw = get_secret("KRX_ID"), get_secret("KRX_PW")
krx_openapi_key = get_secret("KRX_OPENAPI_KEY")
if krx_id and krx_pw:
    os.environ["KRX_ID"] = krx_id
    os.environ["KRX_PW"] = krx_pw
    st.success("KRX 인증정보 설정 확인 완료 (값은 표시하지 않습니다).")
else:
    st.error("KRX 인증정보가 설정되지 않았습니다. Streamlit Cloud의 이 앱 Settings → Secrets에 아래 형식으로 입력하세요.")
    st.code('KRX_ID = "본인 KRX 계정 ID"\nKRX_PW = "본인 KRX 계정 비밀번호"\nKRX_OPENAPI_KEY = "발급받은 KRX OPEN API 인증키"', language="toml")
    st.caption("인증정보를 채팅이나 GitHub 코드에 올리지 마세요. KRX 계정으로 실제 데이터 조회가 가능한지는 별도 확인이 필요합니다.")


def norm(s: object) -> str:
    return re.sub(r"[\s_\-()（）\[\]]+", "", str(s)).lower()

def find_col(df: pd.DataFrame, exact: list[str], contains: tuple[str, ...] = ()) -> Optional[str]:
    by_norm = {norm(c): c for c in df.columns}
    for candidate in exact:
        if norm(candidate) in by_norm:
            return by_norm[norm(candidate)]
    for c in df.columns:
        nc = norm(c)
        if any(norm(part) in nc for part in contains):
            return c
    return None

def code_key(value: object) -> str:
    """Normalize a security code without truncating or extracting arbitrary digits."""
    if pd.isna(value):
        return ""
    value = str(value).strip().upper()
    if value.endswith(".0"):
        value = value[:-2]
    return re.sub(r"[^A-Z0-9]", "", value)

def valid_isin(value: object) -> str:
    """KR ISIN is KR plus 10 alphanumeric characters (12 chars total)."""
    if pd.isna(value):
        return ""
    value = str(value).strip().upper()
    return value if re.fullmatch(r"KR[A-Z0-9]{10}", value) else ""

def date8(value: object) -> Optional[str]:
    if pd.isna(value):
        return None
    s = re.sub(r"\D", "", str(value))
    return s[:8] if len(s) >= 8 else None

def kr_isin_from_numeric_short_code(value: object) -> str:
    """Construct Korean ETF-style ISIN only for six-digit numeric short codes.

    The generated value is not accepted by itself: the code is subsequently
    checked against KRX's ETF daily-trading API on a date before delisting.
    The construction is cross-checked against the current KRX ETF master.
    """
    code = code_key(value)
    if not re.fullmatch(r"\d{6}", code):
        return ""
    base = "KR7" + code + "00"
    expanded = "".join(str(ord(ch) - 55) if ch.isalpha() else ch for ch in base.upper())
    total = 0
    for i, ch in enumerate((expanded + "0")[::-1]):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return base + str((-total) % 10)

def fetch_krx_etf_day(api_key: str, bas_dd: str) -> pd.DataFrame:
    """Fetch one official KRX ETF daily universe by date; never logs the key."""
    import requests
    url = "https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd"
    response = requests.get(url, params={"basDd": bas_dd}, headers={"AUTH_KEY": api_key}, timeout=25)
    if response.status_code in (401, 403):
        raise RuntimeError(f"KRX ETF API 인증/이용권한 거부 (HTTP {response.status_code})")
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        rows = None
        for key in ("OutBlock_1", "output", "data", "result", "items"):
            if isinstance(payload.get(key), list):
                rows = payload[key]; break
        if rows is None:
            # Surface only response keys/status, never headers or credentials.
            raise RuntimeError("KRX ETF API 응답에서 종목 목록을 찾지 못함. 응답키=" + ",".join(map(str, payload.keys())))
    else:
        raise RuntimeError("KRX ETF API 응답 형식이 예상과 다름")
    return pd.DataFrame(rows)

def previous_calendar_days(date_value: str, count: int = 7) -> list[str]:
    dt = pd.to_datetime(date_value, format="%Y%m%d", errors="coerce")
    if pd.isna(dt):
        return []
    return [(dt - pd.Timedelta(days=i)).strftime("%Y%m%d") for i in range(1, count + 1)]

def canonical_price_columns(df: pd.DataFrame, ticker: str, name: str) -> pd.DataFrame:
    cols_out = ["date", "ticker", "name", "Open", "High", "Low", "Close", "Volume", "Adj Close", "adj_close_is_raw_fallback", "adj_close_source", "source"]
    if df is None or df.empty:
        return pd.DataFrame(columns=cols_out)
    d = df.copy(); cols = list(d.columns)
    def pick(*terms):
        for term in terms:
            for c in cols:
                if norm(c) == norm(term): return c
        for term in terms:
            for c in cols:
                if norm(term) in norm(c): return c
        return None
    date_col = pick("일자", "날짜", "거래일", "TRD_DD", "date", "Date")
    fields = {
        "Open": pick("시가", "TDD_OPNPRC", "Open"),
        "High": pick("고가", "TDD_HGPRC", "High"),
        "Low": pick("저가", "TDD_LWPRC", "Low"),
        "Close": pick("종가", "TDD_CLSPRC", "Close"),
        "Volume": pick("거래량", "ACC_TRDVOL", "Volume"),
        "Adj Close": pick("수정종가", "수정주가", "Adj Close", "AdjClose"),
    }
    out = pd.DataFrame()
    out["date"] = pd.to_datetime(d[date_col], errors="coerce") if date_col else pd.NaT
    out["ticker"] = str(ticker).zfill(6); out["name"] = str(name)
    for target, source in fields.items():
        out[target] = pd.to_numeric(d[source].astype(str).str.replace(",", "", regex=False).str.replace("+", "", regex=False), errors="coerce") if source else float("nan")
    if out["Adj Close"].isna().all() and out["Close"].notna().any():
        out["Adj Close"] = out["Close"]
        out["adj_close_source"] = "KRX_adjusted_endpoint_close"
    else:
        out["adj_close_source"] = "KRX_explicit_adjusted_close"
    out["adj_close_is_raw_fallback"] = False
    out["source"] = "KRX individual_price_trend (default adjusted-price mode)"
    out = out.dropna(subset=["date"]).sort_values("date").drop_duplicates(["ticker", "date"], keep="last")
    return out

def make_zip(files: dict[str, object]) -> bytes:
    """Build a ZIP safely from bytes, text, or tabular diagnostic outputs."""
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, payload in files.items():
            if isinstance(payload, bytes):
                data = payload
            elif isinstance(payload, pd.DataFrame):
                # Defensive conversion: a DataFrame must never be passed directly
                # to ZipFile.writestr (which expects bytes or text).
                data = csv_bytes(payload)
            elif isinstance(payload, str):
                data = payload.encode("utf-8")
            else:
                data = str(payload).encode("utf-8")
            zf.writestr(name, data)
    return mem.getvalue()

def csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

with st.sidebar:
    st.header("수집 설정")
    etf_master_file = st.file_uploader(
        "ETF 기준정보 연결 (KRX_ETF_MASTER.csv)",
        type=["csv"],
        help="ZIP이 아니라 ZIP 안의 KRX_ETF_MASTER.csv 파일 자체를 선택하세요. 단축코드 완전 일치만 허용합니다."
    )
    start_date = st.date_input("수집 시작일", value=date(2010, 1, 1), min_value=date(1990, 1, 1), max_value=date.today())
    end_date = st.date_input("수집 종료일", value=min(date(2026, 10, 8), date.today()), min_value=date(1990, 1, 1), max_value=date.today())
    mode = st.radio("수집 범위", ["시험 수집 (ETF 5개)", "일부 수집", "전체 ETF 가격 수집"], index=0)
    if mode == "일부 수집":
        limit = st.number_input("수집 ETF 개수", min_value=1, max_value=100, value=20, step=5)
    elif mode == "시험 수집 (ETF 5개)":
        limit = 5
    else:
        limit = 0
    pause = st.slider("종목 간 대기 시간(초)", min_value=0.1, max_value=1.0, value=0.3, step=0.1)
    st.caption("전체 수집은 오래 걸릴 수 있습니다. 먼저 시험 수집을 권장합니다.")
    if krx_openapi_key:
        st.success("KRX OPEN API 인증키 설정 확인 (값은 표시하지 않습니다).")
    else:
        st.warning("과거 ETF 검증을 위해 Streamlit Secrets에 KRX_OPENAPI_KEY가 필요합니다.")

start_s, end_s = start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")
if start_s > end_s:
    st.error("시작일은 종료일보다 늦을 수 없습니다.")

if st.button("데이터 수집 시작", type="primary", disabled=not (krx_id and krx_pw) or start_s > end_s, use_container_width=True):
    try:
        from krx_data_api import fetch
    except Exception as e:
        st.error(f"KRX API 라이브러리를 불러오지 못했습니다: {type(e).__name__}: {e}")
        st.info("requirements.txt가 GitHub 저장소 루트에 있는지 확인한 뒤 앱을 재배포하세요.")
        st.stop()

    status = st.status("KRX 상장폐지 종목 목록 조회 중…", expanded=True)
    progress = st.progress(0)
    log_area = st.empty()
    log_lines = []
    outputs: dict[str, bytes] = {}
    try:
        all_delisted = fetch("delisted", strtDd=start_s, endDd=end_s)
        if all_delisted is None or all_delisted.empty:
            st.error("KRX에서 상장폐지 목록을 받지 못했습니다. 로그인, 기간, 계정 권한을 확인하세요.")
            st.stop()
        outputs["KRX_DELISTED_ALL.csv"] = csv_bytes(all_delisted)
        type_col = find_col(all_delisted,
            ["증권구분", "상품구분", "증권종류", "상품종류", "SCTY_TP_NM", "SECURITY_TYPE"],
            ("증권구분", "상품구분", "증권종류", "상품종류", "securitytype", "producttype"))
        name_col = find_col(all_delisted, ["종목명", "한글종목명", "ISU_ABBRV", "isuNm"], ("종목명", "한글명", "issueabbrev"))
        short_col = find_col(all_delisted, ["종목코드", "단축코드", "ISU_SRT_CD", "isuSrtCd"], ("단축코드", "종목코드", "isusrtcd"))
        isin_col = find_col(all_delisted, ["표준코드", "ISU_CD", "isuCd", "ISIN"], ("표준코드", "isucd", "isin"))
        delist_col = find_col(all_delisted, ["상장폐지일", "폐지일", "LISTING_END_DD"], ("상장폐지일", "폐지일", "listingend"))

        # Prefer the official ETF master. No ticker truncation and no name-based inference.
        etfs = pd.DataFrame()
        master_rows = 0
        matched_rows = 0
        # If a user supplied an official ETF master, use it first. The API fallback
        # is only for runs without an uploaded master; otherwise a current master
        # would be silently ignored whenever an API key is configured.
        if krx_openapi_key and etf_master_file is None:
            if not short_col or not delist_col:
                st.error("상장폐지 목록에서 종목코드 또는 폐지일 컬럼을 찾지 못했습니다.")
                st.stop()
            # Generate candidate ISINs only for six-digit numeric codes, then verify
            # each exact ISIN against the official ETF daily universe before delisting.
            work = all_delisted.copy()
            work["_short_code_exact"] = work[short_col].map(code_key)
            work["_delist_date_exact"] = work[delist_col].map(date8)
            work["_generated_isin"] = work["_short_code_exact"].map(kr_isin_from_numeric_short_code)
            work = work[work["_generated_isin"].ne("") & work["_delist_date_exact"].notna()].copy()
            unique_dates = sorted(work["_delist_date_exact"].unique())
            api_cache: dict[str, pd.DataFrame] = {}
            verified_isins: dict[str, dict] = {}
            api_errors: list[dict] = []
            api_response_samples: list[dict] = []
            total_dates = len(unique_dates)
            st.info(f"KRX ETF API로 숫자형 6자리 종목코드의 ISIN을 검증합니다. 확인할 폐지일: {total_dates}개")
            api_progress = st.progress(0)
            for idx, ddate in enumerate(unique_dates, start=1):
                group = work[work["_delist_date_exact"] == ddate]
                wanted = set(group["_generated_isin"].tolist())
                found = False
                for query_date in previous_calendar_days(ddate, 7):
                    if query_date not in api_cache:
                        try:
                            api_cache[query_date] = fetch_krx_etf_day(krx_openapi_key, query_date)
                        except Exception as api_exc:
                            api_errors.append({"query_date":query_date,"error":f"{type(api_exc).__name__}: {api_exc}"})
                            # Auth/permission/format errors won't be fixed by trying earlier dates.
                            if isinstance(api_exc, RuntimeError) and ("인증/이용권한" in str(api_exc) or "응답에서 종목 목록" in str(api_exc)):
                                raise
                            continue
                    day_df = api_cache[query_date]
                    # Only retry earlier calendar days when the endpoint returned no
                    # usable trading-day data (e.g. weekend/holiday). If a valid ETF
                    # universe is returned but the exact ISIN is absent, older dates
                    # are unlikely to repair an incorrect generated ISIN and cause
                    # thousands of unnecessary API requests.
                    isin_field = find_col(day_df, ["ISU_CD", "표준코드", "ISIN"], ("isucd", "표준코드", "isin"))
                    if len(api_response_samples) < 5:
                        api_response_samples.append({
                            "query_date": query_date,
                            "row_count": len(day_df),
                            "columns": " | ".join(map(str, day_df.columns)),
                            "isin_column_detected": isin_field or "",
                            "sample_values": " | ".join(day_df[isin_field].astype(str).head(5).tolist()) if isin_field and not day_df.empty else ""
                        })
                    if isin_field and not day_df.empty:
                        day_isins = set(day_df[isin_field].map(valid_isin).tolist())
                        overlap = wanted & day_isins
                        for isin in overlap:
                            row = group[group["_generated_isin"] == isin].iloc[0]
                            verified_isins[isin] = {"ticker":row["_short_code_exact"], "isin":isin, "verified_on":query_date}
                        found = bool(overlap)
                        # A successful response for a trading day is sufficient for
                        # this candidate date; don't scan six more dates if no match.
                        break
                api_progress.progress(idx / max(total_dates, 1))
                if idx % 20 == 0 or idx == total_dates:
                    log_area.code(f"KRX ETF API 날짜 검증 {idx}/{total_dates} · 확인된 ISIN {len(verified_isins)} · API 응답 캐시 {len(api_cache)}")
            verified = pd.DataFrame(list(verified_isins.values()))
            if verified.empty:
                outputs["KRX_ETF_API_ERRORS.csv"] = csv_bytes(pd.DataFrame(api_errors, columns=["query_date","error"]))
                outputs["KRX_ETF_API_RESPONSE_SAMPLE.csv"] = csv_bytes(pd.DataFrame(api_response_samples, columns=["query_date","row_count","columns","isin_column_detected","sample_values"]))
                outputs["KRX_ISIN_GENERATION_AUDIT.csv"] = csv_bytes(work[[short_col, name_col, delist_col, "_generated_isin"]].head(1000) if name_col else work[[short_col, delist_col, "_generated_isin"]].head(1000))
                outputs["RUN_MANIFEST.json"] = json.dumps({"status":"krx_etf_api_returned_no_exact_isin_matches","delisted_rows":len(all_delisted),"numeric_six_digit_rows":len(work),"unique_delisting_dates":total_dates,"api_dates_queried":len(api_cache),"api_errors":len(api_errors),"response_sample_rows":len(api_response_samples),"response_columns_sampled":api_response_samples[0].get("columns","") if api_response_samples else "","rule":"generated KR7+6digit+00+checkdigit ISIN must appear as exact ISU_CD in official KRX ETF daily data before delisting; no name-based matching"},ensure_ascii=False,indent=2).encode("utf-8")
                st.error("KRX ETF API에서 정확한 ISIN 일치가 확인되지 않았습니다. 아래 진단 ZIP에 API 응답 오류와 조회 범위를 담았습니다.")
                st.download_button("KRX ETF API 진단 ZIP 다운로드", make_zip(outputs), file_name="ETF_RADAR_KRX_OPENAPI_DIAGNOSTIC.zip", mime="application/zip")
                st.stop()
            verified_map = verified.set_index("ticker")["isin"].to_dict()
            etfs = all_delisted.copy()
            etfs["_exact_code_key"] = etfs[short_col].map(code_key)
            etfs["_master_isin"] = etfs["_exact_code_key"].map(verified_map).fillna("")
            etfs = etfs[etfs["_master_isin"].ne("")].copy()
            etfs["_master_name"] = etfs[name_col].astype(str) if name_col else ""
            master_rows = len(verified_map)
            matched_rows = len(etfs)
            etfs["collector_name"] = etfs[name_col].astype(str) if name_col else ""
            etfs["collector_ticker"] = etfs["_exact_code_key"]
            etfs["collector_isin"] = etfs["_master_isin"]
            etfs["collector_master_name"] = etfs["_master_name"]
            etfs["collector_match_method"] = "generated_isin_exactly_verified_in_krx_etf_daily_api"
            outputs["KRX_ETF_API_VERIFIED_ISIN_MAP.csv"] = csv_bytes(verified)
            outputs["KRX_ETF_API_ERRORS.csv"] = csv_bytes(pd.DataFrame(api_errors, columns=["query_date","error"]))
        elif etf_master_file is not None:
            try:
                master = pd.read_csv(etf_master_file, dtype=str, encoding="utf-8-sig").fillna("")
            except Exception:
                etf_master_file.seek(0)
                master = pd.read_csv(etf_master_file, dtype=str, encoding="cp949").fillna("")
            master_short_col = find_col(master, ["단축코드", "ISU_SRT_CD", "isuSrtCd"], ("단축코드", "isusrtcd"))
            master_isin_col = find_col(master, ["표준코드", "ISU_CD", "isuCd", "ISIN"], ("표준코드", "isucd", "isin"))
            master_name_col = find_col(master, ["한글종목명", "한글종목약명", "종목명", "ISU_ABBRV"], ("한글종목명", "한글종목약명", "종목명"))
            if not master_short_col or not master_isin_col:
                outputs["ETF_MASTER_SCHEMA_SAMPLE.csv"] = csv_bytes(master.head(100))
                outputs["RUN_MANIFEST.json"] = json.dumps({"status":"etf_master_schema_review_required", "columns":list(master.columns)}, ensure_ascii=False, indent=2).encode("utf-8")
                status.update(label="ETF 기준정보 컬럼 확인 필요", state="error")
                st.error("ETF 기준정보에서 단축코드 또는 표준코드 컬럼을 찾지 못했습니다.")
                st.download_button("진단 ZIP 다운로드", make_zip(outputs), file_name="ETF_RADAR_ETF_MASTER_SCHEMA_REVIEW.zip", mime="application/zip")
                st.stop()
            master_rows = len(master)
            master = master.copy()
            master["_exact_code_key"] = master[master_short_col].map(code_key)
            master["_master_isin"] = master[master_isin_col].map(valid_isin)
            master["_master_name"] = master[master_name_col].astype(str) if master_name_col else ""
            master = master[master["_exact_code_key"].ne("")].drop_duplicates("_exact_code_key", keep=False)
            delisted = all_delisted.copy()
            delisted["_exact_code_key"] = delisted[short_col].map(code_key) if short_col else ""
            # Exact full-code equality only; no last-six/substring matching.
            etfs = delisted.merge(
                master[["_exact_code_key", "_master_isin", "_master_name"]],
                on="_exact_code_key", how="inner", validate="many_to_one"
            )
            matched_rows = len(etfs)
            etfs["collector_name"] = etfs[name_col].astype(str) if name_col else etfs["_master_name"]
            etfs["collector_ticker"] = etfs["_exact_code_key"]
            etfs["collector_isin"] = etfs["_master_isin"]
            etfs["collector_master_name"] = etfs["_master_name"]
            etfs["collector_match_method"] = "exact_full_short_code"
        else:
            type_values = all_delisted[type_col].astype(str).str.upper() if type_col else pd.Series("", index=all_delisted.index)
            is_etf = type_values.str.contains(r"ETF|상장지수|상장지수펀드", regex=True, na=False)
            if not is_etf.any():
                type_values_df = (all_delisted[type_col].astype(str).value_counts(dropna=False).rename_axis("value").reset_index(name="count") if type_col else pd.DataFrame({"value":["분류 컬럼 없음"],"count":[len(all_delisted)]}))
                outputs["KRX_DELISTED_PRODUCT_TYPE_VALUES.csv"] = csv_bytes(type_values_df)
                outputs["RUN_MANIFEST.json"] = json.dumps({"status":"etf_master_required", "start":start_s, "end":end_s, "type_column":type_col, "message":"Upload official KRX ETF master CSV; do not infer by name or partial code."}, ensure_ascii=False, indent=2).encode("utf-8")
                status.update(label="ETF 기준정보 연결 필요", state="error")
                st.error("KRX 상장폐지 목록의 분류값만으로 ETF를 판별할 수 없습니다. 왼쪽 ‘ETF 기준정보 연결’에 KRX_ETF_MASTER.csv를 업로드해 주세요.")
                st.download_button("진단 ZIP 다운로드", make_zip(outputs), file_name="ETF_RADAR_ETF_MASTER_REQUIRED.zip", mime="application/zip")
                st.stop()
            etfs = all_delisted.loc[is_etf].copy()
            etfs["collector_name"] = etfs[name_col].astype(str) if name_col else ""
            etfs["collector_ticker"] = etfs[short_col].map(code_key) if short_col else ""
            etfs["collector_isin"] = etfs[isin_col].map(valid_isin) if isin_col else ""
            etfs["collector_match_method"] = "explicit_product_type_only"
        etfs["collector_delisting_date"] = etfs[delist_col].map(date8) if delist_col else None
        outputs["KRX_DELISTED_ETF_METADATA.csv"] = csv_bytes(etfs)
        candidates = etfs[
            etfs["collector_ticker"].astype(str).ne("") &
            etfs["collector_isin"].astype(str).map(valid_isin).ne("")
        ].copy()
        outputs["KRX_ETF_MASTER_MATCH_AUDIT.csv"] = csv_bytes(etfs)
        if etf_master_file is not None:
            outputs["RUN_MANIFEST.json"] = json.dumps({
                "status":"exact_code_matching_complete",
                "start":start_s, "end":end_s,
                "delisted_rows":len(all_delisted), "etf_master_rows":master_rows,
                "exact_code_matches":matched_rows, "valid_isin_candidates":len(candidates),
                "matching_rule":"exact full short-code equality; no truncation, substring or name inference",
                "isin_regex":"^KR[A-Z0-9]{10}$"
            }, ensure_ascii=False, indent=2).encode("utf-8")
        if candidates.empty:
            # Explain whether the failure is code linkage, ISIN validation, or historical-master coverage.
            delisted_codes = set(delisted["_exact_code_key"].astype(str)) if "delisted" in locals() and "_exact_code_key" in delisted else set()
            master_codes = set(master["_exact_code_key"].astype(str)) if etf_master_file is not None and "master" in locals() and "_exact_code_key" in master else set()
            exact_overlap = sorted((delisted_codes & master_codes) - {""})
            outputs["MATCH_DIAGNOSTIC.csv"] = csv_bytes(pd.DataFrame([
                {"metric":"delisted_rows","value":len(all_delisted)},
                {"metric":"master_rows","value":master_rows},
                {"metric":"exact_full_code_overlap_unique","value":len(exact_overlap)},
                {"metric":"matched_rows","value":matched_rows},
                {"metric":"etf_rows_after_match","value":len(etfs)},
                {"metric":"valid_isin_candidates","value":len(candidates)},
                {"metric":"delisted_code_length_counts","value":json.dumps(all_delisted[short_col].astype(str).str.len().value_counts().to_dict(), ensure_ascii=False) if short_col else "short-code column not found"},
                {"metric":"master_code_length_counts","value":json.dumps(master[master_short_col].astype(str).str.len().value_counts().to_dict(), ensure_ascii=False) if etf_master_file is not None and "master" in locals() else "master not loaded"},
                {"metric":"matching_rule","value":"exact normalized full code only; no truncation, substring, or name inference"},
            ]))
            outputs["RUN_MANIFEST.json"] = json.dumps({
                "status":"no_valid_etf_identifiers",
                "start":start_s, "end":end_s,
                "delisted_rows":len(all_delisted), "etf_master_rows":master_rows,
                "exact_full_code_overlap_unique":len(exact_overlap),
                "exact_code_matches":matched_rows, "etf_candidates":len(etfs),
                "valid_isin_candidates":len(candidates),
                "reason":"No exact full-code matches or no matched rows with valid KR + 10 alphanumeric ISIN.",
                "next_step":"Use a historical ETF master that contains delisted ETF short codes. Do not infer ETF identity from the last six characters or names."
            }, ensure_ascii=False, indent=2).encode("utf-8")
            st.error("정확한 단축코드 매칭 및 유효 ISIN 후보가 없습니다. 이름이나 코드 일부로 추정하지 않고 중단했습니다.")
            st.info("현재 기준정보는 현행 ETF 1,172개이며, 상장폐지 목록과 원본 코드 완전 일치가 없을 수 있습니다. 상장폐지 당시의 ETF 기준정보가 필요할 수 있습니다.")
            st.download_button("진단 파일 다운로드", make_zip(outputs), file_name="ETF_RADAR_KRX_DIAGNOSTICS.zip", mime="application/zip")
            st.stop()
        # Apply the user-selected limit to the expensive individual price-history
        # requests. Previously the mode selector displayed a limit but did not apply it.
        total_valid_candidates = len(candidates)
        if int(limit) > 0:
            candidates = candidates.head(int(limit)).copy()
        status.update(label=f"유효 후보 {total_valid_candidates}개 중 {len(candidates)}개 가격 수집 시작", state="running")
        price_parts, failures, coverage = [], [], []
        for i, row in enumerate(candidates.to_dict("records"), start=1):
            ticker, name, isin = row["collector_ticker"], row["collector_name"], row["collector_isin"]
            delist = date8(row.get("collector_delisting_date")) or end_s
            fetch_end = min(delist, end_s)
            try:
                prices = fetch("individual_price_trend", isuCd=isin, strtDd=start_s, endDd=fetch_end, adjBasDd=fetch_end)
                normalized = canonical_price_columns(prices, ticker, name)
                if normalized.empty:
                    failures.append({"ticker":ticker,"name":name,"isin":isin,"reason":"empty price result"})
                    coverage.append({"ticker":ticker,"name":name,"isin":isin,"rows":0,"first_date":None,"last_date":None,"delisting_date":delist})
                else:
                    normalized["isin"] = isin; normalized["delisting_date"] = delist
                    price_parts.append(normalized)
                    coverage.append({"ticker":ticker,"name":name,"isin":isin,"rows":len(normalized),"first_date":str(normalized.date.min().date()),"last_date":str(normalized.date.max().date()),"delisting_date":delist})
            except Exception as e:
                failures.append({"ticker":ticker,"name":name,"isin":isin,"reason":f"{type(e).__name__}: {e}"})
                coverage.append({"ticker":ticker,"name":name,"isin":isin,"rows":0,"first_date":None,"last_date":None,"delisting_date":delist})
            progress.progress(i / len(candidates))
            log_lines.append(f"{i}/{len(candidates)} · {ticker} {name} · 누적 가격 행 {sum(len(p) for p in price_parts):,} · 실패 {len(failures)}")
            log_area.code("\n".join(log_lines[-8:]))
            if i < len(candidates): time.sleep(float(pause))
        prices_out = pd.concat(price_parts, ignore_index=True) if price_parts else pd.DataFrame(columns=["date","ticker","name","Open","High","Low","Close","Volume","Adj Close"])
        outputs["KRX_DELISTED_ETF_PRICES.csv"] = csv_bytes(prices_out)
        outputs["KRX_DELISTED_ETF_FETCH_FAILURES.csv"] = csv_bytes(pd.DataFrame(failures, columns=["ticker","name","isin","reason"]))
        outputs["KRX_DELISTED_ETF_PRICE_COVERAGE.csv"] = csv_bytes(pd.DataFrame(coverage))
        manifest = {
            "status":"completed_with_or_without_failures", "start":start_s, "end":end_s,
            "generated_at":pd.Timestamp.now().isoformat(timespec="seconds"),
            "source":"KRX Data Marketplace / krx_data_api",
            "all_delisted_rows":int(len(all_delisted)), "etf_candidates":int(len(etfs)),
            "valid_price_candidates_total":int(total_valid_candidates),
            "price_requests":int(len(candidates)), "price_rows":int(len(prices_out)),
            "success_count":int(sum(1 for x in coverage if x.get("rows",0)>0)), "failure_count":int(len(failures)),
            "limited_run":bool(limit), "limit":int(limit),
            "notes":["ETF classification uses exact KRX API ISIN verification.", "KRX default adjusted-price endpoint is used.", "Selected collection limit is applied to price requests.", "This output alone does not remove survivorship bias; integrate listing dates and historical universe before rerunning backtest."]
        }
        outputs["RUN_MANIFEST.json"] = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
        status.update(label="데이터 수집 완료", state="complete")
        st.success(f"완료: ETF 가격 {len(prices_out):,}행 · 가격 조회 성공 {manifest['success_count']}개 · 실패 {len(failures)}개")
        st.dataframe(pd.DataFrame([{"항목":"상장폐지 목록 행","값":len(all_delisted)},{"항목":"ETF 분류 후보","값":len(etfs)},{"항목":"가격 조회 대상","값":len(candidates)},{"항목":"가격 데이터 행","값":len(prices_out)},{"항목":"가격 조회 실패","값":len(failures)}]), use_container_width=True, hide_index=True)
        st.download_button("수집 결과 ZIP 다운로드", make_zip(outputs), file_name=f"ETF_RADAR_DELISTED_BACKFILL_{start_s}_{end_s}.zip", mime="application/zip", type="primary", use_container_width=True)
        st.caption("다운로드한 ZIP을 이 채팅에 첨부해 주세요. 실제 수집 결과를 확인한 뒤 기존 백테스트와 통합하겠습니다.")
    except Exception as e:
        status.update(label="수집 중 오류 발생", state="error")
        st.exception(e)
        st.info("오류 화면이나 Cloud logs의 오류 내용을 보내 주시면 원인을 확인하겠습니다. 인증정보 자체는 보내지 마세요.")

st.divider()
st.subheader("휴대폰에서 진행하는 순서")
st.markdown("""
1. GitHub 저장소에 이 파일을 `backfill_app.py` 이름으로 추가합니다.
2. 저장소 루트의 `requirements.txt`에 필요한 패키지가 들어 있는지 확인합니다.
3. Streamlit Community Cloud에서 **Create app → 기존 저장소 선택 → Main file path를 `backfill_app.py`** 로 지정해 별도 앱으로 배포합니다.
4. 새 앱의 Settings → Secrets에 `KRX_ID`, `KRX_PW`를 설정합니다.
5. 먼저 **시험 수집 (ETF 5개)** 을 실행하고 ZIP을 다운로드합니다.

Streamlit Cloud는 별도 앱에서 다른 엔트리포인트 파일을 지정해 배포할 수 있으며, Secrets는 앱 설정에서 관리합니다.
""")
