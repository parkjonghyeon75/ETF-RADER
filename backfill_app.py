"""ETF RADAR - 상장폐지 ETF 검증 및 백테스트 자료 점검 도구

운영 app.py와 독립된 Streamlit 앱입니다.
- 종목코드/ISIN은 문자열로 보존하고 완전 일치만 허용합니다.
- 현행 ETF 마스터만으로 과거 ETF 여부를 추정하지 않습니다.
- 일별 시세는 실제 제공된 자료만 사용하며, 미수집 가격을 만들어내지 않습니다.
- 백테스트 매매규칙이 제공되지 않은 상태에서 수익률/MDD/승률을 임의 재계산하지 않습니다.
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

APP_VERSION = "4.4.0"

st.set_page_config(page_title="ETF RADAR | 상장폐지 ETF 검증", layout="wide")
st.title("ETF RADAR — 상장폐지 ETF 검증 및 백테스트 자료 점검")
st.caption(f"별도 검증 앱 · 버전 {APP_VERSION} · 운영 app.py 수정 없음")

st.warning(
    "이 도구는 근거가 없는 종목을 ETF로 추정하지 않습니다. "
    "과거 ETF 기준정보/ETF 전용 폐지목록과 실제 과거 시세가 부족하면 결과를 '미검증'으로 분리합니다."
)

def read_csv_upload(uploaded_file) -> pd.DataFrame:
    raw = uploaded_file.getvalue()
    errors = []
    for encoding in ("utf-8-sig", "cp949", "utf-8"):
        try:
            return pd.read_csv(io.BytesIO(raw), dtype=str, encoding=encoding, keep_default_na=False)
        except Exception as exc:
            errors.append(f"{encoding}: {exc}")
    raise ValueError("CSV를 읽을 수 없습니다: " + " | ".join(errors))

def clean_text(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()

def find_col(df: Optional[pd.DataFrame], candidates: list[str]) -> Optional[str]:
    if df is None:
        return None
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    lowered = {str(c).strip().lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    return None

def normalize_code(value) -> str:
    if value is None:
        return ""
    text = str(value).strip().upper()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    if re.fullmatch(r"\d+\.0", text):
        text = text[:-2]
    return text

def normalize_isin(value) -> str:
    if value is None:
        return ""
    text = re.sub(r"\s+", "", str(value)).upper()
    return "" if text.lower() in {"nan", "none", "null"} else text

def parse_date(value) -> str:
    text = str(value or "").strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return ""
    digits = re.sub(r"[^0-9]", "", text)
    if len(digits) == 8:
        return digits
    parsed = pd.to_datetime(text, errors="coerce")
    return parsed.strftime("%Y%m%d") if pd.notna(parsed) else ""

def csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

def inventory_row(label, frame):
    return {"자료": label, "상태": "로드 완료" if frame is not None else "미제공",
            "행 수": len(frame) if frame is not None else 0,
            "컬럼 수": len(frame.columns) if frame is not None else 0}

st.subheader("1. 검증 자료")
st.markdown(
    "CSV 또는 ZIP 파일을 한 번에 하나씩 직접 업로드할 수 있습니다. "
    "직접 업로드한 자료가 저장소에서 자동 발견한 자료보다 우선합니다. "
    "ZIP은 내부 CSV 파일을 읽으며, 원본 파일을 수정하지 않습니다."
)

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEARCH_DIRS = [ROOT, ROOT / "data"]
ROLE_LABELS = {
    "delisted": "상장폐지 원본",
    "master": "ETF 기준정보",
    "historical": "과거 ETF 기준정보 / ETF 전용 폐지목록",
    "daily": "ETF 일별 시세",
    "backtest": "기존 백테스트 종목/신호",
}

def infer_role(filename: str) -> str:
    name = filename.lower()
    # Do not accidentally treat this tool's audit output as an input source.
    if "audit" in name or "diagnostic" in name or "진단" in name or "검증결과" in name:
        return ""
    if "histor" in name or "과거" in name or "history" in name:
        return "historical"
    if "delisted" in name or "상장폐지" in name or "폐지목록" in name:
        return "delisted"
    if "daily" in name or "raw" in name or "시세" in name or "trd" in name:
        return "daily"
    if "backtest" in name or "signal" in name or "신호" in name or "백테스트" in name:
        return "backtest"
    if "master" in name or "기준정보" in name or "etf_master" in name:
        return "master"
    return ""

def read_bytes_csv(raw: bytes, label: str) -> pd.DataFrame:
    errors = []
    for encoding in ("utf-8-sig", "cp949", "utf-8"):
        try:
            return pd.read_csv(io.BytesIO(raw), dtype=str, encoding=encoding, keep_default_na=False)
        except Exception as exc:
            errors.append(f"{encoding}: {exc}")
    raise ValueError(f"{label}: CSV를 읽을 수 없습니다: " + " | ".join(errors))

def read_uploaded_bundle(uploaded_file, assigned_role: str):
    """Return list of (role, source label, dataframe); ZIP members inherit the selected role."""
    raw = uploaded_file.getvalue()
    name = uploaded_file.name
    output = []
    if name.lower().endswith(".zip"):
        try:
            with zipfile.ZipFile(io.BytesIO(raw), "r") as zf:
                members = [m for m in zf.namelist()
                           if m.lower().endswith(".csv") and not m.startswith("__MACOSX/")]
                for member in members:
                    member_role = infer_role(Path(member).name) or assigned_role
                    # The category chosen by the user takes precedence for ambiguous ZIP contents.
                    if assigned_role:
                        member_role = assigned_role
                    output.append((member_role, f"{name}::{Path(member).name}",
                                   read_bytes_csv(zf.read(member), member)))
        except zipfile.BadZipFile:
            raise ValueError(f"{name}: ZIP 파일을 열 수 없습니다.")
    elif name.lower().endswith(".csv"):
        output.append((assigned_role or infer_role(name), name, read_bytes_csv(raw, name)))
    else:
        raise ValueError(f"{name}: CSV 또는 ZIP 파일만 지원합니다.")
    return output

with st.expander("자료 파일 업로드", expanded=True):
    st.caption(
        "휴대폰에서 파일명이 표시되지 않는 문제를 피하기 위해 한 번에 파일 하나씩 선택합니다. "
        "CSV/ZIP만 자료로 처리합니다. 기존 data 폴더 파일은 유지됩니다."
    )
    uploaded_file = st.file_uploader(
        "파일 선택 (CSV 또는 ZIP)",
        key="single_source_upload_v44",
        help="파일 하나를 선택한 뒤 아래에서 자료 종류를 지정하세요."
    )
    upload_slots = {}
    if uploaded_file is not None:
        st.success(f"파일 수신 확인: {uploaded_file.name} · {uploaded_file.size:,} bytes")
        suffix = Path(uploaded_file.name).suffix.lower()
        if suffix not in {".csv", ".zip"}:
            st.error(f"지원하지 않는 파일 형식: {suffix or '확장자 없음'}. CSV 또는 ZIP 파일을 선택하세요.")
        else:
            detected = infer_role(uploaded_file.name)
            role_options = list(ROLE_LABELS.keys())
            default_index = role_options.index(detected) if detected in role_options else 0
            selected_role = st.selectbox(
                "이 파일의 자료 종류",
                options=role_options,
                index=default_index,
                format_func=lambda key: ROLE_LABELS[key],
                key="role_for_single_upload_v44"
            )
            upload_slots[selected_role] = uploaded_file
    else:
        st.info("아직 파일이 앱에 전달되지 않았습니다. 파일을 선택하면 파일명과 크기가 여기에 표시됩니다.")

# Discover repository files as a fallback, but never use audit/diagnostic outputs as source data.
discovered: dict[str, tuple[str, bytes]] = {}
source_errors = []
for folder in SEARCH_DIRS:
    if not folder.exists():
        continue
    for file_path in folder.iterdir():
        if not file_path.is_file():
            continue
        try:
            if file_path.suffix.lower() == ".csv":
                role = infer_role(file_path.name)
                if role:
                    discovered[role] = (str(file_path.relative_to(ROOT)), file_path.read_bytes())
            elif file_path.suffix.lower() == ".zip":
                with zipfile.ZipFile(file_path, "r") as zf:
                    for member in zf.namelist():
                        if member.lower().endswith(".csv") and not member.startswith("__MACOSX/"):
                            role = infer_role(Path(member).name)
                            if role:
                                discovered[role] = (f"{file_path.name}::{Path(member).name}", zf.read(member))
        except Exception as exc:
            source_errors.append(f"{file_path.name}: {exc}")

# Load repository fallback first, then replace each role with direct user uploads.
frames: dict[str, Optional[pd.DataFrame]] = {k: None for k in ROLE_LABELS}
source_names: dict[str, str] = {}
for role, item in discovered.items():
    try:
        frames[role] = read_bytes_csv(item[1], item[0])
        source_names[role] = item[0]
    except Exception as exc:
        source_errors.append(str(exc))

for role, uploaded_file in upload_slots.items():
    if uploaded_file is None:
        continue
    try:
        parsed_items = read_uploaded_bundle(uploaded_file, role)
        candidates = [item for item in parsed_items if item[0] == role and item[2] is not None]
        if not candidates:
            st.warning(f"{uploaded_file.name}: {ROLE_LABELS[role]}에 사용할 CSV를 찾지 못했습니다.")
            continue
        # If ZIP contains several CSVs, combine only when their columns match exactly.
        dfs = [item[2] for item in candidates]
        if len(dfs) == 1:
            frames[role] = dfs[0]
            source_names[role] = candidates[0][1]
        else:
            common_columns = list(dfs[0].columns)
            if all(list(df.columns) == common_columns for df in dfs):
                frames[role] = pd.concat(dfs, ignore_index=True)
                source_names[role] = f"{uploaded_file.name} ({len(dfs)} CSV 결합)"
            else:
                # Prefer a clearly named matching CSV rather than silently merging incompatible schemas.
                named = [item for item in candidates if infer_role(Path(item[1].split("::")[-1]).name) == role]
                chosen = named[0] if named else candidates[0]
                frames[role] = chosen[2]
                source_names[role] = chosen[1]
                st.warning(f"{uploaded_file.name}: CSV별 컬럼 구성이 달라 '{chosen[1]}'만 사용했습니다.")
    except Exception as exc:
        st.error(str(exc))

with st.expander("자료 연결 상태", expanded=True):
    for key, label in ROLE_LABELS.items():
        frame = frames.get(key)
        source = source_names.get(key, "파일 없음")
        st.write(f"{'●' if frame is not None else '○'} **{label}** — {source} "
                 f"({len(frame):,}행" if frame is not None else f"○ **{label}** — 파일 없음")
        if frame is not None:
            st.caption(f"컬럼 {len(frame.columns)}개: " + ", ".join(map(str, frame.columns[:12])))

for err in source_errors:
    st.error(err)

st.dataframe(pd.DataFrame([
    inventory_row(ROLE_LABELS[k], frames[k]) for k in ROLE_LABELS
]), use_container_width=True, hide_index=True)

if st.button("검증 및 자료 연결 실행", type="primary", use_container_width=True):
    if frames["delisted"] is None:
        st.error("상장폐지 원본 CSV를 올려 주세요.")
        st.stop()
    if frames["master"] is None:
        st.error("ETF 기준정보 CSV를 올려 주세요.")
        st.stop()

    d0 = frames["delisted"].copy()
    m0 = frames["master"].copy()
    h0 = frames["historical"].copy() if frames["historical"] is not None else None
    daily0 = frames["daily"].copy() if frames["daily"] is not None else None
    bt0 = frames["backtest"].copy() if frames["backtest"] is not None else None

    # Column detection: only known names; never infer from arbitrary columns.
    d_code = find_col(d0, ["단축코드", "종목코드", "ISU_SRT_CD", "ISU_CD", "SRT_CD", "Code", "code"])
    d_isin = find_col(d0, ["표준코드", "ISIN", "ISU_STD_CD"])
    d_name = find_col(d0, ["종목명", "한글종목명", "한글종목약명", "ISU_NM", "Name", "name"])
    d_date = find_col(d0, ["폐지일", "상장폐지일", "DELIST_DATE", "delisting_date", "폐지일자"])
    d_type = find_col(d0, ["증권구분", "상품유형", "상품구분", "ETF여부", "종목유형", "TYPE"])

    m_code = find_col(m0, ["단축코드", "종목코드", "ISU_SRT_CD", "ISU_CD", "SRT_CD", "Code", "code"])
    m_isin = find_col(m0, ["표준코드", "ISIN", "ISU_STD_CD"])
    m_name = find_col(m0, ["한글종목명", "한글종목약명", "종목명", "ISU_NM", "Name", "name"])
    m_list_date = find_col(m0, ["상장일", "LIST_DATE", "listing_date"])

    if not (d_code or d_isin):
        st.error("상장폐지 원본에서 종목코드/ISIN 컬럼을 찾지 못했습니다.")
        st.stop()
    if not (m_code or m_isin):
        st.error("ETF 기준정보에서 종목코드/ISIN 컬럼을 찾지 못했습니다.")
        st.stop()

    d = d0.copy()
    m = m0.copy()
    d["원본CSV행번호"] = range(2, len(d) + 2)
    d["정규화_단축코드"] = d[d_code].map(normalize_code) if d_code else ""
    d["정규화_ISIN"] = d[d_isin].map(normalize_isin) if d_isin else ""
    d["정규화_종목명"] = clean_text(d[d_name]) if d_name else ""
    d["정규화_폐지일"] = d[d_date].map(parse_date) if d_date else ""
    d["원본_유형값"] = clean_text(d[d_type]) if d_type else ""

    m["정규화_단축코드"] = m[m_code].map(normalize_code) if m_code else ""
    m["정규화_ISIN"] = m[m_isin].map(normalize_isin) if m_isin else ""
    m["정규화_종목명"] = clean_text(m[m_name]) if m_name else ""
    m["정규화_상장일"] = m[m_list_date].map(parse_date) if m_list_date else ""

    m_codes = set(m.loc[m["정규화_단축코드"] != "", "정규화_단축코드"])
    m_isins = set(m.loc[m["정규화_ISIN"] != "", "정규화_ISIN"])
    code_names = (m[m["정규화_단축코드"] != ""].drop_duplicates("정규화_단축코드")
                  .set_index("정규화_단축코드")["정규화_종목명"].to_dict())
    isin_names = (m[m["정규화_ISIN"] != ""].drop_duplicates("정규화_ISIN")
                  .set_index("정규화_ISIN")["정규화_종목명"].to_dict())
    d["현행마스터_단축코드완전일치"] = d["정규화_단축코드"].ne("") & d["정규화_단축코드"].isin(m_codes)
    d["현행마스터_ISIN완전일치"] = d["정규화_ISIN"].ne("") & d["정규화_ISIN"].isin(m_isins)
    d["현행마스터_코드일치종목명"] = d["정규화_단축코드"].map(code_names).fillna("")
    d["현행마스터_ISIN일치종목명"] = d["정규화_ISIN"].map(isin_names).fillna("")

    # Match historical reference only by exact code/ISIN. It is evidence only;
    # classification requires explicit ETF type evidence or an explicitly ETF-only source.
    hist_count = 0
    hist_type_col = None
    historical_is_etf_only = False
    if h0 is not None:
        h_code = find_col(h0, ["단축코드", "종목코드", "ISU_SRT_CD", "ISU_CD", "SRT_CD", "Code", "code"])
        h_isin = find_col(h0, ["표준코드", "ISIN", "ISU_STD_CD"])
        hist_type_col = find_col(h0, ["상품유형", "상품구분", "증권구분", "ETF여부", "종목유형", "TYPE", "시장구분"])
        if h_code or h_isin:
            h = h0.copy()
            h["_code"] = h[h_code].map(normalize_code) if h_code else ""
            h["_isin"] = h[h_isin].map(normalize_isin) if h_isin else ""
            h_codes = set(h.loc[h["_code"] != "", "_code"])
            h_isins = set(h.loc[h["_isin"] != "", "_isin"])
            d["과거자료_단축코드완전일치"] = d["정규화_단축코드"].ne("") & d["정규화_단축코드"].isin(h_codes)
            d["과거자료_ISIN완전일치"] = d["정규화_ISIN"].ne("") & d["정규화_ISIN"].isin(h_isins)
            hist_count = int((d["과거자료_단축코드완전일치"] | d["과거자료_ISIN완전일치"]).sum())
            if hist_type_col:
                vals = clean_text(h[hist_type_col]).str.upper()
                historical_is_etf_only = bool(vals.isin(["ETF", "상장지수펀드", "상장지수투자신탁", "EXCHANGE TRADED FUND"]).any())
        else:
            d["과거자료_단축코드완전일치"] = False
            d["과거자료_ISIN완전일치"] = False
    else:
        d["과거자료_단축코드완전일치"] = False
        d["과거자료_ISIN완전일치"] = False

    explicit_types = {"ETF", "상장지수펀드", "상장지수투자신탁", "EXCHANGE TRADED FUND"}
    explicit_delisted_etf = bool(d["원본_유형값"].str.upper().isin(explicit_types).any())
    # Do not call matches "confirmed ETF" unless an ETF-specific reference/type is present.
    evidence_available = (h0 is not None and hist_count > 0 and (historical_is_etf_only or explicit_delisted_etf))

    st.subheader("2. 종목 식별 결과")
    a, b, c, e = st.columns(4)
    a.metric("상장폐지 원본 행", f"{len(d):,}")
    b.metric("현행 코드 일치 행", f"{int(d['현행마스터_단축코드완전일치'].sum()):,}")
    c.metric("현행 ISIN 일치 행", f"{int(d['현행마스터_ISIN완전일치'].sum()):,}")
    e.metric("과거 코드/ISIN 일치 행", f"{hist_count:,}")

    if evidence_available:
        st.success("과거 자료의 완전 일치와 ETF 유형 근거가 일부 확인됐습니다. 개별 행의 근거를 확인하세요.")
    elif h0 is None:
        st.error("ETF 상장폐지 확정 불가: 과거 ETF 기준정보/ETF 전용 폐지목록이 없습니다.")
    elif hist_count == 0:
        st.error("ETF 상장폐지 확정 불가: 과거 자료와 코드/ISIN 완전 일치가 없습니다.")
    else:
        st.warning("코드/ISIN 일치 후보는 있지만 ETF 유형을 입증하는 근거가 부족합니다. 확정 ETF로 처리하지 않았습니다.")

    # Daily prices: exact-code joins, date coverage, no fabricated prices.
    daily_summary = pd.DataFrame()
    daily_enriched = pd.DataFrame()
    if daily0 is not None:
        p_code = find_col(daily0, ["ISU_CD", "단축코드", "종목코드", "ISU_SRT_CD", "code"])
        p_date = find_col(daily0, ["BAS_DD", "기준일", "일자", "DATE", "date"])
        p_close = find_col(daily0, ["TDD_CLSPRC", "종가", "종가(원)", "close"])
        p_name = find_col(daily0, ["ISU_NM", "종목명", "한글종목명", "name"])
        if p_code:
            px = daily0.copy()
            px["정규화_단축코드"] = px[p_code].map(normalize_code)
            px["정규화_일자"] = px[p_date].map(parse_date) if p_date else ""
            close_str = clean_text(px[p_close]).str.replace(",", "", regex=False) if p_close else pd.Series([""] * len(px))
            px["종가_숫자"] = pd.to_numeric(close_str, errors="coerce")
            px["종목명_원본"] = clean_text(px[p_name]) if p_name else ""
            px["현행마스터_코드일치"] = px["정규화_단축코드"].isin(m_codes)
            px["폐지목록_코드일치"] = px["정규화_단축코드"].isin(set(d["정규화_단축코드"]))
            valid_dates = px["정규화_일자"].replace("", pd.NA).dropna()
            daily_summary = pd.DataFrame([
                {"항목": "시세 행 수", "결과": len(px)},
                {"항목": "고유 종목코드 수", "결과": px.loc[px["정규화_단축코드"] != "", "정규화_단축코드"].nunique()},
                {"항목": "중복 코드-날짜 행 수", "결과": int(px.duplicated(["정규화_단축코드", "정규화_일자"]).sum()) if p_date else "날짜 컬럼 없음"},
                {"항목": "종가 결측/비수치 행 수", "결과": int(px["종가_숫자"].isna().sum())},
                {"항목": "폐지목록 코드와 일치하는 시세 행 수", "결과": int(px["폐지목록_코드일치"].sum())},
                {"항목": "시세 날짜 범위", "결과": f"{valid_dates.min()} ~ {valid_dates.max()}" if len(valid_dates) else "날짜 없음"},
            ])
            daily_enriched = px
            st.subheader("3. 일별 시세 커버리지")
            st.dataframe(daily_summary, use_container_width=True, hide_index=True)
            matched_px = px[px["폐지목록_코드일치"]]
            if matched_px.empty:
                st.warning("제공된 시세 파일에서 상장폐지 원본과 완전 일치하는 종목코드가 없습니다. 이 파일은 최근 ETF 시세만 포함할 수 있습니다.")
            else:
                st.info(f"상장폐지 원본과 코드가 일치하는 시세 행 {len(matched_px):,}개를 찾았습니다. 이것만으로 폐지일/ETF 유형이 확정되는 것은 아닙니다.")
        else:
            st.warning("일별 시세 파일에 인식 가능한 종목코드 컬럼이 없어 시세 연결을 생략했습니다.")

    # Existing backtest universe coverage against delisted list by exact code only.
    bt_audit = pd.DataFrame()
    if bt0 is not None:
        bt_code = find_col(bt0, ["단축코드", "종목코드", "ISU_CD", "ISU_SRT_CD", "code", "ticker", "symbol"])
        bt_date = find_col(bt0, ["일자", "기준일", "DATE", "date", "BAS_DD", "signal_date"])
        if bt_code:
            bt_audit = bt0.copy()
            bt_audit["정규화_단축코드"] = bt_audit[bt_code].map(normalize_code)
            delisted_codes = set(d.loc[d["정규화_단축코드"] != "", "정규화_단축코드"])
            bt_audit["상장폐지목록_코드완전일치"] = bt_audit["정규화_단축코드"].isin(delisted_codes)
            if bt_date:
                bt_audit["정규화_일자"] = bt_audit[bt_date].map(parse_date)
            st.subheader("4. 기존 백테스트와 상장폐지 목록 대조")
            st.metric("백테스트 행 중 폐지목록 코드 일치", f"{int(bt_audit['상장폐지목록_코드완전일치'].sum()):,} / {len(bt_audit):,}")
            st.dataframe(bt_audit.head(200), use_container_width=True)
            st.warning("이 대조는 종목코드의 존재 여부만 확인합니다. 원래 매수·매도 규칙, 체결가, 수수료, 보유기간이 연결되지 않았으므로 수익률/MDD/승률은 재계산하지 않았습니다.")
        else:
            st.warning("백테스트 CSV에서 명시적인 종목코드 컬럼을 찾지 못했습니다. 임의 컬럼을 코드로 사용하지 않았습니다.")

    st.subheader("5. 대조 결과")
    show_cols = [c for c in [
        d_code, d_isin, d_name, d_date, d_type, "정규화_단축코드", "정규화_ISIN",
        "현행마스터_단축코드완전일치", "현행마스터_ISIN완전일치",
        "과거자료_단축코드완전일치", "과거자료_ISIN완전일치"
    ] if c and c in d.columns]
    st.dataframe(d[show_cols].head(500), use_container_width=True, hide_index=True)

    summary = pd.DataFrame([
        {"항목": "앱 버전", "결과": APP_VERSION},
        {"항목": "실행 일시", "결과": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        {"항목": "상장폐지 원본 행 수", "결과": len(d)},
        {"항목": "ETF 마스터 행 수", "결과": len(m)},
        {"항목": "현행 마스터 코드 완전 일치 행 수", "결과": int(d["현행마스터_단축코드완전일치"].sum())},
        {"항목": "현행 마스터 ISIN 완전 일치 행 수", "결과": int(d["현행마스터_ISIN완전일치"].sum())},
        {"항목": "과거 자료 코드/ISIN 완전 일치 행 수", "결과": hist_count},
        {"항목": "ETF 상장폐지 확정 가능", "결과": "일부 근거 확인 - 개별 행 검토 필요" if evidence_available else "아니오 - 근거 부족"},
        {"항목": "백테스트 성과 재계산", "결과": "실행하지 않음 - 매매 규칙/체결 데이터 연결 필요"},
        {"항목": "KRX API 재조회", "결과": "실행하지 않음 - 업로드 자료만 분석"},
    ])

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("SUMMARY.csv", csv_bytes(summary))
        zf.writestr("DELISTED_MATCH_AUDIT.csv", csv_bytes(d))
        if not daily_summary.empty:
            zf.writestr("DAILY_COVERAGE_SUMMARY.csv", csv_bytes(daily_summary))
        if not daily_enriched.empty:
            zf.writestr("DAILY_PRICE_AUDIT.csv", csv_bytes(daily_enriched))
        if not bt_audit.empty:
            zf.writestr("BACKTEST_UNIVERSE_AUDIT.csv", csv_bytes(bt_audit))
        manifest = {
            "app_version": APP_VERSION,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "input_rows": {k: (len(v) if v is not None else None) for k, v in frames.items()},
            "rules": {
                "exact_code_isin_matching_only": True,
                "name_based_inference": False,
                "identifier_numeric_cast": False,
                "fabricated_prices": False,
                "krx_api_called": False,
                "backtest_performance_recalculated": False
            }
        }
        zf.writestr("RUN_MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    st.download_button(
        "검증 결과 ZIP 다운로드", data=zip_buffer.getvalue(),
        file_name=f"ETF_RADAR_BACKFILL_AUDIT_{datetime.now():%Y%m%d_%H%M%S}.zip",
        mime="application/zip", use_container_width=True
    )
    st.download_button(
        "상장폐지 대조 CSV 다운로드", data=csv_bytes(d),
        file_name="DELISTED_MATCH_AUDIT.csv", mime="text/csv", use_container_width=True
    )

st.divider()
st.caption(
    "정확한 코드/ISIN 대조와 근거 자료의 존재를 구분합니다. 이 버전은 저장소에 등록된 자료를 분석하며 KRX API를 재호출하거나 "
    "백테스트 성과를 임의로 재계산하지 않습니다. 운영용 app.py에는 영향을 주지 않습니다."
)
