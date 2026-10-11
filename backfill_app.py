"""ETF RADAR - 상장폐지 ETF 식별·가격 데이터 진단 도구

중요 원칙
- 운영용 app.py와 독립 실행되는 별도 Streamlit 앱입니다.
- 현재 ETF 마스터만으로 과거 상장폐지 ETF를 추정하지 않습니다.
- 종목코드는 문자열로 보존합니다(영문자 및 선행 0 유지).
- 종목명/증권구분만으로 ETF 여부를 확정하지 않습니다.
- 이 버전은 진단과 증거 연결만 수행하며 백테스트를 재계산하지 않습니다.
- KRX API를 호출하지 않으며 대량 재조회하지 않습니다.
"""
from __future__ import annotations

import io
import json
import re
import zipfile
from datetime import datetime
from typing import Optional

import pandas as pd
import streamlit as st

APP_VERSION = "2.0.0"

st.set_page_config(page_title="ETF RADAR | 상장폐지 ETF 검증", layout="wide")
st.title("ETF RADAR — 상장폐지 ETF 식별 및 데이터 진단")
st.caption(f"진단 전용 · 버전 {APP_VERSION} · 백테스트 재계산 및 KRX 전체 재조회 없음")
st.warning(
    "현재 ETF 마스터는 현행 ETF 목록일 수 있어 상장폐지 ETF의 존재를 증명하지 못합니다. "
    "과거 ETF 기준정보 또는 ETF 전용 상장폐지 원본이 없으면 추정 매칭하지 않고 '확인 불가'로 표시합니다."
)

# ---- File and schema helpers -------------------------------------------------
def read_csv_upload(uploaded_file) -> pd.DataFrame:
    """Read a CSV conservatively, preserving identifiers as strings."""
    raw = uploaded_file.getvalue()
    errors = []
    for encoding in ("utf-8-sig", "cp949", "utf-8"):
        try:
            return pd.read_csv(io.BytesIO(raw), dtype=str, encoding=encoding, keep_default_na=False)
        except Exception as exc:  # try next common KRX encoding
            errors.append(f"{encoding}: {exc}")
    raise ValueError("CSV를 읽을 수 없습니다. 인코딩을 확인하세요. " + " | ".join(errors))


def clean_text(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def find_col(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    # exact match first, then case-insensitive exact match
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    lowered = {str(c).strip().lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    return None


def normalize_short_code(value) -> str:
    """Normalize only whitespace/case. Never numeric-cast or zfill identifiers."""
    if value is None:
        return ""
    text = str(value).strip().upper()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    # CSV readers may leave spreadsheet-style trailing .0 for numeric identifiers.
    # Strip .0 only for purely numeric strings; never alter alphanumeric codes.
    if re.fullmatch(r"\d+\.0", text):
        text = text[:-2]
    return text


def normalize_isin(value) -> str:
    if value is None:
        return ""
    text = re.sub(r"\s+", "", str(value)).upper()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    return text


def parse_date(value) -> str:
    text = str(value or "").strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return ""
    digits = re.sub(r"[^0-9]", "", text)
    if len(digits) == 8:
        return digits
    try:
        parsed = pd.to_datetime(text, errors="coerce")
        if pd.notna(parsed):
            return parsed.strftime("%Y%m%d")
    except Exception:
        pass
    return ""


def summarize_df(label: str, df: Optional[pd.DataFrame]) -> dict:
    if df is None:
        return {"자료": label, "상태": "미제공", "행 수": 0, "컬럼 수": 0}
    return {"자료": label, "상태": "로드 완료", "행 수": len(df), "컬럼 수": len(df.columns)}


def make_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


st.subheader("1. 기존 자료 불러오기")
st.markdown("필요한 자료를 업로드하세요. 파일이 이미 있는 경우에도 업로드한 파일의 실제 컬럼을 기준으로 검사합니다.")
col_a, col_b = st.columns(2)
with col_a:
    delisted_upload = st.file_uploader("상장폐지 원본 CSV (예: KRX_DELISTED_ALL.csv)", type=["csv"], key="delisted")
    master_upload = st.file_uploader("ETF 기준정보 CSV (현행 또는 과거 기준정보)", type=["csv"], key="master")
with col_b:
    daily_upload = st.file_uploader("ETF 일별 시세 CSV (선택)", type=["csv"], key="daily")
    historical_master_upload = st.file_uploader(
        "과거 ETF 기준정보 / ETF 전용 상장폐지 목록 CSV (권장)",
        type=["csv"],
        key="historical_master",
        help="상장폐지 ETF를 확정하려면 이 자료가 가장 중요합니다. 단순 종목명 목록은 확정 증거로 취급하지 않습니다.",
    )

# Parse files with explicit error reporting.
frames: dict[str, Optional[pd.DataFrame]] = {"delisted": None, "master": None, "daily": None, "historical": None}
errors: list[str] = []
for key, uploaded in (("delisted", delisted_upload), ("master", master_upload), ("daily", daily_upload), ("historical", historical_master_upload)):
    if uploaded is not None:
        try:
            frames[key] = read_csv_upload(uploaded)
        except Exception as exc:
            errors.append(f"{uploaded.name}: {exc}")

if errors:
    for err in errors:
        st.error(err)

inventory = pd.DataFrame([
    summarize_df("상장폐지 원본", frames["delisted"]),
    summarize_df("ETF 기준정보", frames["master"]),
    summarize_df("일별 시세", frames["daily"]),
    summarize_df("과거 ETF 기준정보/ETF 전용 폐지목록", frames["historical"]),
])
st.dataframe(inventory, use_container_width=True, hide_index=True)

if st.button("기존 자료 진단 실행", type="primary", use_container_width=True):
    if frames["delisted"] is None:
        st.error("상장폐지 원본 CSV를 먼저 업로드하세요.")
        st.stop()
    if frames["master"] is None:
        st.error("ETF 기준정보 CSV를 먼저 업로드하세요.")
        st.stop()

    delisted = frames["delisted"].copy()
    master = frames["master"].copy()
    daily = frames["daily"].copy() if frames["daily"] is not None else None
    historical = frames["historical"].copy() if frames["historical"] is not None else None

    # Detect source columns without silently selecting arbitrary first columns.
    d_code_col = find_col(delisted, ["종목코드", "단축코드", "ISU_SRT_CD", "ISU_CD", "SRT_CD", "Code", "code"])
    d_isin_col = find_col(delisted, ["표준코드", "ISIN", "isin", "ISU_STD_CD"])
    d_name_col = find_col(delisted, ["종목명", "한글종목명", "한글종목약명", "ISU_NM", "Name", "name"])
    d_date_col = find_col(delisted, ["폐지일", "상장폐지일", "DELIST_DATE", "delisting_date", "폐지일자"])
    d_type_col = find_col(delisted, ["증권구분", "상품유형", "상품구분", "ETF여부", "종목유형", "TYPE"])

    m_code_col = find_col(master, ["단축코드", "종목코드", "ISU_SRT_CD", "ISU_CD", "SRT_CD", "Code", "code"])
    m_isin_col = find_col(master, ["표준코드", "ISIN", "isin", "ISU_STD_CD"])
    m_name_col = find_col(master, ["한글종목명", "한글종목약명", "종목명", "ISU_NM", "Name", "name"])
    m_list_date_col = find_col(master, ["상장일", "LIST_DATE", "listing_date"])

    daily_code_col = find_col(daily, ["ISU_CD", "단축코드", "종목코드", "ISU_SRT_CD", "code"]) if daily is not None else None
    daily_date_col = find_col(daily, ["BAS_DD", "기준일", "일자", "DATE", "date"]) if daily is not None else None
    daily_close_col = find_col(daily, ["TDD_CLSPRC", "종가", "종가(원)", "close"]) if daily is not None else None
    daily_name_col = find_col(daily, ["ISU_NM", "종목명", "한글종목명", "name"]) if daily is not None else None

    schema_rows = []
    for label, df, mapping in [
        ("상장폐지 원본", delisted, {"코드": d_code_col, "ISIN": d_isin_col, "종목명": d_name_col, "폐지일": d_date_col, "유형": d_type_col}),
        ("ETF 기준정보", master, {"단축코드": m_code_col, "표준코드/ISIN": m_isin_col, "종목명": m_name_col, "상장일": m_list_date_col}),
    ]:
        for field, col in mapping.items():
            schema_rows.append({"자료": label, "항목": field, "발견 컬럼": col or "없음"})
    st.subheader("2. 컬럼 구조 확인")
    st.dataframe(pd.DataFrame(schema_rows), use_container_width=True, hide_index=True)

    if not d_code_col and not d_isin_col:
        st.error("상장폐지 원본에서 명시적인 종목코드 또는 ISIN 컬럼을 찾지 못했습니다. 첫 번째 컬럼을 코드로 간주하지 않고 중단합니다.")
        st.stop()
    if not m_code_col and not m_isin_col:
        st.error("ETF 기준정보에서 명시적인 단축코드 또는 ISIN 컬럼을 찾지 못했습니다. 추정 매칭하지 않고 중단합니다.")
        st.stop()

    # Build normalized working frames; retain original columns.
    d = delisted.copy()
    m = master.copy()
    d["_source_row"] = range(2, len(d) + 2)
    m["_source_row"] = range(2, len(m) + 2)
    d["_code_norm"] = d[d_code_col].map(normalize_short_code) if d_code_col else ""
    d["_isin_norm"] = d[d_isin_col].map(normalize_isin) if d_isin_col else ""
    d["_name_norm"] = clean_text(d[d_name_col]) if d_name_col else ""
    d["_delist_date_norm"] = d[d_date_col].map(parse_date) if d_date_col else ""
    d["_type_value"] = clean_text(d[d_type_col]) if d_type_col else ""

    m["_code_norm"] = m[m_code_col].map(normalize_short_code) if m_code_col else ""
    m["_isin_norm"] = m[m_isin_col].map(normalize_isin) if m_isin_col else ""
    m["_name_norm"] = clean_text(m[m_name_col]) if m_name_col else ""

    # Current daily raw exact join against current ETF master (data-integrity check only).
    daily_summary = pd.DataFrame()
    daily_rows = pd.DataFrame()
    if daily is not None and daily_code_col:
        day = daily.copy()
        day["_code_norm"] = day[daily_code_col].map(normalize_short_code)
        if daily_date_col:
            day["_date_norm"] = day[daily_date_col].map(parse_date)
        else:
            day["_date_norm"] = ""
        if daily_close_col:
            close_text = clean_text(day[daily_close_col]).str.replace(",", "", regex=False)
            day["_close_numeric"] = pd.to_numeric(close_text, errors="coerce")
        else:
            day["_close_numeric"] = pd.NA
        master_codes = set(m.loc[m["_code_norm"] != "", "_code_norm"])
        day["현행마스터코드일치"] = day["_code_norm"].isin(master_codes)
        daily_rows = day
        daily_summary = pd.DataFrame([
            {"검사항목": "시세 행 수", "결과": len(day)},
            {"검사항목": "고유 시세 코드 수", "결과": day.loc[day["_code_norm"] != "", "_code_norm"].nunique()},
            {"검사항목": "시세 코드 중 현행 마스터와 일치하는 고유 코드 수", "결과": day.loc[day["현행마스터코드일치"], "_code_norm"].nunique()},
            {"검사항목": "종가 결측 행 수", "결과": int(day["_close_numeric"].isna().sum()) if daily_close_col else "종가 컬럼 없음"},
            {"검사항목": "날짜 범위", "결과": (f"{day['_date_norm'].replace('', pd.NA).dropna().min()} ~ {day['_date_norm'].replace('', pd.NA).dropna().max()}" if day["_date_norm"].replace('', pd.NA).notna().any() else "날짜 컬럼/값 없음")},
        ])

    # Exact code/ISIN matches to supplied master are evidence of presence in that master,
    # not evidence that the delisted record itself is an ETF. The source may be a current-only master.
    code_master = m[m["_code_norm"] != ""].drop_duplicates("_code_norm")
    isin_master = m[m["_isin_norm"] != ""].drop_duplicates("_isin_norm")
    code_map = dict(zip(code_master["_code_norm"], code_master["_name_norm"]))
    isin_map = dict(zip(isin_master["_isin_norm"], isin_master["_name_norm"]))
    d["현행마스터_단축코드일치"] = d["_code_norm"].ne("") & d["_code_norm"].isin(set(code_map))
    d["현행마스터_ISIN일치"] = d["_isin_norm"].ne("") & d["_isin_norm"].isin(set(isin_map))
    d["현행마스터_코드일치종목명"] = d["_code_norm"].map(code_map).fillna("")
    d["현행마스터_ISIN일치종목명"] = d["_isin_norm"].map(isin_map).fillna("")

    # Optional historical/ETF-only reference is the only input that can upgrade a match to
    # a candidate for confirmation; still do not infer ETF status from name alone.
    hist_code_col = find_col(historical, ["단축코드", "종목코드", "ISU_SRT_CD", "ISU_CD", "SRT_CD", "Code", "code"]) if historical is not None else None
    hist_isin_col = find_col(historical, ["표준코드", "ISIN", "isin", "ISU_STD_CD"]) if historical is not None else None
    hist_name_col = find_col(historical, ["한글종목명", "한글종목약명", "종목명", "ISU_NM", "Name", "name"]) if historical is not None else None
    hist_delist_col = find_col(historical, ["폐지일", "상장폐지일", "DELIST_DATE", "delisting_date", "폐지일자"]) if historical is not None else None
    hist_type_col = find_col(historical, ["상품유형", "상품구분", "증권구분", "ETF여부", "종목유형", "TYPE", "시장구분"]) if historical is not None else None

    if historical is not None and not (hist_code_col or hist_isin_col):
        st.warning("추가 과거 기준정보에 단축코드/ISIN 컬럼이 없어 확정 매칭에 사용할 수 없습니다.")

    confirmed_reference_match = False
    if historical is not None and (hist_code_col or hist_isin_col):
        h = historical.copy()
        h["_code_norm"] = h[hist_code_col].map(normalize_short_code) if hist_code_col else ""
        h["_isin_norm"] = h[hist_isin_col].map(normalize_isin) if hist_isin_col else ""
        h["_name_norm"] = clean_text(h[hist_name_col]) if hist_name_col else ""
        h["_delist_date_norm"] = h[hist_delist_col].map(parse_date) if hist_delist_col else ""
        h["_type_value"] = clean_text(h[hist_type_col]) if hist_type_col else ""
        h_codes = set(h.loc[h["_code_norm"] != "", "_code_norm"])
        h_isins = set(h.loc[h["_isin_norm"] != "", "_isin_norm"])
        d["과거자료_단축코드일치"] = d["_code_norm"].ne("") & d["_code_norm"].isin(h_codes)
        d["과거자료_ISIN일치"] = d["_isin_norm"].ne("") & d["_isin_norm"].isin(h_isins)
        confirmed_reference_match = bool(d["과거자료_단축코드일치"].any() or d["과거자료_ISIN일치"].any())
    else:
        d["과거자료_단축코드일치"] = False
        d["과거자료_ISIN일치"] = False

    # Record source limitations instead of making a guessed ETF classification.
    has_explicit_etf_type = False
    if d_type_col:
        type_values = set(d["_type_value"].str.strip().str.upper())
        has_explicit_etf_type = bool(type_values & {"ETF", "상장지수펀드", "상장지수투자신탁", "EXCHANGE TRADED FUND"})
    hist_has_etf_type = False
    if historical is not None and hist_type_col:
        ht = clean_text(historical[hist_type_col]).str.upper()
        hist_has_etf_type = bool(ht.isin(["ETF", "상장지수펀드", "상장지수투자신탁", "EXCHANGE TRADED FUND"]).any())

    st.subheader("3. 핵심 검증 결과")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("상장폐지 원본 행", f"{len(d):,}")
    k2.metric("현행 마스터 코드 일치", f"{int(d['현행마스터_단축코드일치'].sum()):,}")
    k3.metric("현행 마스터 ISIN 일치", f"{int(d['현행마스터_ISIN일치'].sum()):,}")
    k4.metric("과거 자료 코드/ISIN 일치", f"{int((d['과거자료_단축코드일치'] | d['과거자료_ISIN일치']).sum()):,}")

    if daily_summary.empty:
        st.info("일별 시세 파일은 제공되지 않았거나 종목코드 컬럼을 찾지 못해 시세 연결 검사는 생략했습니다.")
    else:
        st.markdown("**일별 시세 무결성 검사 (가격 재계산 아님)**")
        st.dataframe(daily_summary, use_container_width=True, hide_index=True)

    exact_count = int((d["현행마스터_단축코드일치"] | d["현행마스터_ISIN일치"]).sum())
    historical_count = int((d["과거자료_단축코드일치"] | d["과거자료_ISIN일치"]).sum())
    if historical is None:
        st.error(
            "검증 중단: 과거 ETF 기준정보 또는 ETF 전용 상장폐지 목록이 제공되지 않았습니다. "
            "현행 ETF 마스터와의 일치 여부는 과거 상장폐지 ETF를 확정할 수 없습니다. "
            "종목명/증권구분으로 추정하지 않았으며 백테스트는 재계산하지 않았습니다."
        )
    elif historical_count == 0:
        st.error(
            "검증 중단: 추가 과거 기준정보와 코드/ISIN 완전 일치가 0건입니다. "
            "코드 일부 일치나 이름 유사도로 보정하지 않았습니다. 백테스트는 재계산하지 않았습니다."
        )
    elif not hist_has_etf_type and not has_explicit_etf_type:
        st.warning(
            f"과거 자료에서 코드/ISIN 일치 {historical_count:,}건을 찾았지만 ETF 전용 자료 또는 명시적 ETF 유형이 확인되지 않았습니다. "
            "이는 종목 식별 후보이지 상장폐지 ETF 확정 결과가 아닙니다. 백테스트는 재계산하지 않았습니다."
        )
    else:
        st.warning(
            f"코드/ISIN 일치 {historical_count:,}건이 확인됐습니다. 다만 이 도구는 폐지일과 ETF 상품유형의 원본 근거를 별도로 검토해야 하므로 "
            "현재 단계에서는 확정 판정이나 백테스트 재계산을 하지 않습니다."
        )

    # Export detail and summary, with source evidence columns preserved.
    export_detail = d.copy()
    # Internal helper columns are intentionally included with clear names for auditability.
    export_detail = export_detail.rename(columns={
        "_source_row": "원본CSV행번호",
        "_code_norm": "정규화_단축코드(문자열보존)",
        "_isin_norm": "정규화_ISIN",
        "_name_norm": "정규화_종목명",
        "_delist_date_norm": "정규화_폐지일(YYYYMMDD)",
        "_type_value": "원본_유형값",
    })
    summary = pd.DataFrame([
        {"항목": "앱 버전", "결과": APP_VERSION},
        {"항목": "진단 일시", "결과": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        {"항목": "상장폐지 원본 행 수", "결과": len(d)},
        {"항목": "ETF 마스터 행 수", "결과": len(m)},
        {"항목": "현행 마스터 단축코드 일치 행 수", "결과": int(d["현행마스터_단축코드일치"].sum())},
        {"항목": "현행 마스터 ISIN 일치 행 수", "결과": int(d["현행마스터_ISIN일치"].sum())},
        {"항목": "과거 자료 코드/ISIN 일치 행 수", "결과": historical_count},
        {"항목": "ETF 상장폐지 확정", "결과": "아니오 - 본 도구는 근거 부족 시 추정하지 않음"},
        {"항목": "백테스트 재계산", "결과": "실행하지 않음"},
        {"항목": "KRX API 재조회", "결과": "실행하지 않음"},
    ])
    st.subheader("4. 대조 결과 미리보기")
    display_cols = [c for c in [d_code_col, d_isin_col, d_name_col, d_date_col, d_type_col,
                                "현행마스터_단축코드일치", "현행마스터_ISIN일치",
                                "과거자료_단축코드일치", "과거자료_ISIN일치"] if c and c in d.columns]
    display_cols = list(dict.fromkeys(display_cols))
    st.dataframe(d[display_cols].head(200) if display_cols else d.head(200), use_container_width=True)

    # ZIP contains reproducible audit artifacts only; never claims a backfill was completed.
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("DIAGNOSTIC_SUMMARY.csv", make_csv_bytes(summary))
        zf.writestr("DELISTED_MATCH_AUDIT.csv", make_csv_bytes(export_detail))
        if not daily_summary.empty:
            zf.writestr("DAILY_RAW_INTEGRITY.csv", make_csv_bytes(daily_summary))
        manifest = {
            "app_version": APP_VERSION,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "inputs": {k: (v.shape if v is not None else None) for k, v in frames.items()},
            "policy": {
                "exact_code_and_isin_matching_only": True,
                "name_based_inference_disabled": True,
                "numeric_zfill_disabled": True,
                "krx_api_called": False,
                "backtest_recalculated": False,
            },
        }
        zf.writestr("RUN_MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    zip_buffer.seek(0)
    st.download_button(
        "진단 결과 ZIP 다운로드",
        data=zip_buffer.getvalue(),
        file_name=f"ETF_RADAR_DELSTED_DIAGNOSTIC_{datetime.now():%Y%m%d_%H%M%S}.zip",
        mime="application/zip",
        use_container_width=True,
    )
    st.download_button(
        "대조 결과 CSV 다운로드",
        data=make_csv_bytes(export_detail),
        file_name="DELISTED_MATCH_AUDIT.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.divider()
st.caption(
    "이 앱은 진단 도구입니다. 코드/ISIN 완전 일치, ETF 상품유형, 상장폐지일의 원본 근거가 충분하지 않으면 확정 결과를 만들지 않습니다. "
    "어떤 경우에도 이 앱은 기존 운영 app.py를 수정하거나 백테스트를 자동 재계산하지 않습니다."
)
