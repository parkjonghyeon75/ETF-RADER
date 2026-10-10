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
이 도구는 KRX 상장폐지 종목 목록에서 ETF를 식별하고, 선택한 ETF의 과거 가격을 수집합니다.
**수집 성공 여부는 KRX 계정 권한과 응답 형식에 따라 달라질 수 있습니다.** 결과를 받기 전까지 실제 데이터가 확보된 것으로 간주하지 마세요.
""")

# Read secrets without ever displaying their values.
def get_secret(key: str) -> str:
    try:
        val = st.secrets.get(key, "")
        return str(val).strip() if val is not None else ""
    except Exception:
        return ""

krx_id, krx_pw = get_secret("KRX_ID"), get_secret("KRX_PW")
if krx_id and krx_pw:
    os.environ["KRX_ID"] = krx_id
    os.environ["KRX_PW"] = krx_pw
    st.success("KRX 인증정보 설정 확인 완료 (값은 표시하지 않습니다).")
else:
    st.error("KRX 인증정보가 설정되지 않았습니다. Streamlit Cloud의 이 앱 Settings → Secrets에 아래 형식으로 입력하세요.")
    st.code('KRX_ID = "본인 KRX 계정 ID"\nKRX_PW = "본인 KRX 계정 비밀번호"', language="toml")
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

def read_uploaded_csv(uploaded_file: object) -> pd.DataFrame:
    """Read KRX CSV exports using common Korean encodings without guessing column meaning."""
    raw = uploaded_file.getvalue()
    last_error = None
    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            return pd.read_csv(io.BytesIO(raw), dtype=str, encoding=encoding).fillna("")
        except Exception as exc:
            last_error = exc
    raise ValueError(f"CSV 인코딩을 판독할 수 없습니다: {type(last_error).__name__}: {last_error}")

with st.sidebar:
    st.header("수집 설정")
    etf_master_file = st.file_uploader(
        "ETF 기준정보 연결 (KRX_ETF_MASTER.csv)",
        type=["csv"],
        help="ZIP이 아니라 KRX_ETF_MASTER.csv 파일 자체를 선택하세요. 현재 기준정보는 과거 상장폐지 ETF를 모두 포함하지 않을 수 있습니다."
    )
    etf_delisted_file = st.file_uploader(
        "KRX ETF 상장폐지 종목검색 결과 CSV (선택)",
        type=["csv"],
        help="KRX ETF 종목검색에서 ‘상장폐지종목포함’을 선택해 내려받은 CSV입니다. 일반 상장폐지 목록과 혼용하지 않습니다."
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

        # Prefer an ETF-specific delisted list if supplied. The general delisted-stock
        # endpoint does not identify ETFs reliably in the supplied diagnostic data.
        etf_specific_delisted = None
        if etf_delisted_file is not None:
            etf_specific_delisted = read_uploaded_csv(etf_delisted_file)
            outputs["KRX_ETF_SPECIFIC_DELISTED_SOURCE.csv"] = csv_bytes(etf_specific_delisted)

        # Prefer the official ETF master. No ticker truncation and no name-based inference.
        etfs = pd.DataFrame()
        master_rows = 0
        matched_rows = 0
        if etf_master_file is not None:
            master = read_uploaded_csv(etf_master_file)
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

            if etf_specific_delisted is not None:
                specific_short_col = find_col(
                    etf_specific_delisted,
                    ["단축코드", "종목코드", "ISU_SRT_CD", "isuSrtCd"],
                    ("단축코드", "종목코드", "isusrtcd")
                )
                specific_name_col = find_col(
                    etf_specific_delisted,
                    ["종목명", "한글종목명", "ISU_ABBRV", "isuNm"],
                    ("종목명", "한글명", "issueabbrev")
                )
                specific_delist_col = find_col(
                    etf_specific_delisted,
                    ["상장폐지일", "폐지일", "LISTING_END_DD"],
                    ("상장폐지일", "폐지일", "listingend")
                )
                if not specific_short_col:
                    outputs["ETF_SPECIFIC_SOURCE_SCHEMA.csv"] = csv_bytes(etf_specific_delisted.head(100))
                    outputs["RUN_MANIFEST.json"] = json.dumps({
                        "status": "etf_specific_source_schema_review_required",
                        "columns": list(etf_specific_delisted.columns),
                        "message": "ETF 전용 상장폐지 CSV에서 종목코드 컬럼을 찾지 못했습니다."
                    }, ensure_ascii=False, indent=2).encode("utf-8")
                    status.update(label="ETF 전용 CSV 컬럼 확인 필요", state="error")
                    st.error("ETF 전용 CSV에서 종목코드 컬럼을 찾지 못했습니다. 진단 ZIP의 컬럼 샘플을 확인합니다.")
                    st.download_button("진단 ZIP 다운로드", make_zip(outputs), file_name="ETF_RADAR_ETF_DELISTED_SCHEMA_REVIEW.zip", mime="application/zip")
                    st.stop()
                delisted = etf_specific_delisted.copy()
                delisted["_exact_code_key"] = delisted[specific_short_col].map(code_key)
                name_col = specific_name_col
                short_col = specific_short_col
                delist_col = specific_delist_col
            else:
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
            etfs["collector_match_method"] = (
                "exact_full_short_code_etf_specific_delisted_source"
                if etf_specific_delisted is not None
                else "exact_full_short_code_general_delisted_source"
            )
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
                "next_step": (
                    "ETF 전용 상장폐지 목록은 확보했으나 현재 기준정보에 없는 코드의 ISIN은 확인되지 않았습니다. "
                    "KRX 과거 ETF 종목 기본정보에서 단축코드와 표준코드(ISIN)가 함께 있는 이력 자료가 필요합니다."
                    if etf_specific_delisted is not None else
                    "KRX ETF 종목검색에서 '상장폐지종목포함'을 선택해 ETF 전용 CSV를 내려받아 업로드하세요. "
                    "해당 자료에 ISIN이 없고 현행 기준정보와도 일치하지 않으면 과거 ETF 단축코드-ISIN 매핑 원본이 필요합니다."
                )
            }, ensure_ascii=False, indent=2).encode("utf-8")
            st.error("유효한 ETF ISIN 후보가 없습니다. 이름이나 코드 일부로 추정하지 않고 중단했습니다.")
            if etf_specific_delisted is None:
                st.info("일반 상장폐지 목록 대신 KRX ETF 종목검색의 ‘상장폐지종목포함’ CSV를 왼쪽 새 업로드 칸에 넣어 다시 검증하세요.")
            else:
                st.info("ETF 전용 목록은 사용했지만 과거 ISIN 연결이 확인되지 않았습니다. 이 경우 가격 수집을 시작하지 않습니다.")
            st.download_button("진단 파일 다운로드", make_zip(outputs), file_name="ETF_RADAR_KRX_DIAGNOSTICS.zip", mime="application/zip")
            st.stop()
        status.update(label=f"상장폐지 ETF {len(etfs)}개 중 {len(candidates)}개 가격 수집 시작", state="running")
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
            "price_requests":int(len(candidates)), "price_rows":int(len(prices_out)),
            "success_count":int(sum(1 for x in coverage if x.get("rows",0)>0)), "failure_count":int(len(failures)),
            "limited_run":bool(limit), "limit":int(limit),
            "notes":["ETF classification uses KRX product/security type column.", "KRX default adjusted-price endpoint is used.", "This output alone does not remove survivorship bias; integrate listing dates and historical universe before rerunning backtest."]
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
1. GitHub 저장소에서 이 파일만 `backfill_app.py`로 교체합니다. 운영용 `app.py`는 수정하지 않습니다.
2. `requirements.txt`를 확인하고 별도 Streamlit 앱으로 배포합니다.
3. 새 앱의 Settings → Secrets에 `KRX_ID`, `KRX_PW`를 설정합니다.
4. `KRX_ETF_MASTER.csv`를 업로드합니다.
5. 일반 상장폐지 목록에서 ETF 매칭이 0건이면, KRX ETF 종목검색에서 **‘상장폐지종목포함’** 을 선택해 내려받은 CSV를 새 업로드 칸에 넣습니다.
6. 실제 ISIN 후보가 확인되기 전에는 가격 수집을 시작하지 않습니다.

Streamlit Cloud는 별도 앱에서 다른 엔트리포인트 파일을 지정해 배포할 수 있으며, Secrets는 앱 설정에서 관리합니다.
""")
