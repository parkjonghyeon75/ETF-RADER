# -*- coding: utf-8 -*-
"""ETF RADAR delisted ETF backfill - Diagnostic & Fixed Version."""
from __future__ import annotations
import io, os, re, json, zipfile, hashlib
from datetime import date, timedelta
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ETF RADAR · 상장폐지 ETF 진단 및 수집", page_icon="📊", layout="wide")
st.title("ETF RADAR — 상장폐지 ETF 진단 및 수집 시스템")
st.warning("이 앱은 백테스트용 별도 도구입니다. 기존 운영 app.py를 수정하지 않습니다.")
st.info("주의: 현재 수집 범위는 각 상장폐지일 직전 최대 7일의 시세 확인 및 검증입니다.")

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
else:
    st.error("KRX 인증정보가 설정되지 않았습니다. Streamlit Cloud Secrets를 확인하세요.")

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
    if pd.isna(value): return ""
    value = str(value).strip().upper()
    if value.endswith(".0"): value = value[:-2]
    return re.sub(r"[^A-Z0-9]", "", value)

def date8(value: object) -> Optional[str]:
    if pd.isna(value): return None
    s = re.sub(r"\D", "", str(value))
    return s[:8] if len(s) >= 8 else None

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_krx_etf_day(api_key: str, bas_dd: str) -> pd.DataFrame:
    import requests
    url = "https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd"
    response = requests.get(url, params={"basDd": bas_dd}, headers={"AUTH_KEY": api_key}, timeout=15)
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
        if rows is None: return pd.DataFrame()
    else:
        return pd.DataFrame()
    return pd.DataFrame(rows)

def make_zip(files: dict[str, object]) -> bytes:
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, payload in files.items():
            if isinstance(payload, bytes): data = payload
            elif isinstance(payload, pd.DataFrame): data = payload.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            elif isinstance(payload, str): data = payload.encode("utf-8")
            else: data = str(payload).encode("utf-8")
            zf.writestr(name, data)
    return mem.getvalue()

with st.sidebar:
    st.subheader("수집 기간 설정")
    period_option = st.selectbox("기간 선택", ["최근 1년 (모바일 권장)", "최근 2년", "최근 3년"], index=0)
    today = date.today()
    if period_option == "최근 1년 (모바일 권장)":
        default_start = today - timedelta(days=365)
    elif period_option == "최근 2년":
        default_start = today - timedelta(days=365*2)
    else:
        default_start = today - timedelta(days=365*3)

    start_date = st.date_input("수집 시작일", value=default_start, min_value=date(2015, 1, 1), max_value=today)
    end_date = st.date_input("수집 종료일", value=today, min_value=date(2015, 1, 1), max_value=today)
    mode = st.radio("수집 범위", ["시험 수집 (ETF 5개)", "전체 ETF 가격 수집"], index=0)
    limit = 5 if mode == "시험 수집 (ETF 5개)" else 0

def get_tmp_paths(start_s: str, end_s: str, mode_name: str):
    key = hashlib.sha256(f"{start_s}:{end_s}:{mode_name}".encode("utf-8")).hexdigest()[:16]
    return (
        os.path.join("/tmp", f"etf_prices_{key}.csv"),
        os.path.join("/tmp", f"etf_state_{key}.json")
    )

start_s, end_s = start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")
prices_csv_path, state_json_path = get_tmp_paths(start_s, end_s, mode)

if st.button("데이터 진단 및 수집 시작", type="primary", disabled=not (krx_id and krx_pw), use_container_width=True):
    try:
        from krx_data_api import fetch
    except Exception as e:
        st.error(f"KRX API 라이브러리를 불러오지 못했습니다: {e}")
        st.stop()

    status = st.status("KRX 상장폐지 종목 목록 조회 및 컬럼 분석 중…", expanded=True)
    outputs: dict[str, bytes] = {}
    
    try:
        all_delisted = fetch("delisted", strtDd=start_s, endDd=end_s)
        if all_delisted is None or all_delisted.empty:
            st.error("KRX에서 상장폐지 목록을 받지 못했습니다.")
            st.stop()
        outputs["KRX_DELISTED_ALL.csv"] = all_delisted

        if krx_openapi_key:
            short_col_direct = find_col(all_delisted, ["종목코드", "단축코드", "ISU_SRT_CD"], ("단축코드", "종목코드"))
            delist_col_direct = find_col(all_delisted, ["상장폐지일", "폐지일", "LISTING_END_DD"], ("상장폐지일", "폐지일"))
            
            if not short_col_direct or not delist_col_direct:
                st.error("상장폐지 목록에서 단축코드 또는 상장폐지일 컬럼을 찾지 못했습니다.")
                st.stop()

            delisted_direct = all_delisted.copy()
            delisted_direct["collector_ticker"] = delisted_direct[short_col_direct].map(code_key)
            delisted_direct["collector_delisting_date"] = delisted_direct[delist_col_direct].map(date8)
            delisted_direct = delisted_direct[
                delisted_direct["collector_ticker"].str.fullmatch(r"\d{6}", na=False)
                & delisted_direct["collector_delisting_date"].notna()
            ].copy()
            
            code_delist_dates = {}
            for rec in delisted_direct[["collector_ticker", "collector_delisting_date"]].to_dict("records"):
                code_delist_dates.setdefault(rec["collector_ticker"], set()).add(rec["collector_delisting_date"])
            wanted_codes = set(code_delist_dates)
            
            if code_limit := (int(limit) if int(limit) > 0 else 0):
                wanted_codes = set(sorted(wanted_codes)[:code_limit])
                code_delist_dates = {c: code_delist_dates[c] for c in wanted_codes}

            candidate_query_dates = set()
            selected_delist_dates = sorted({d for dates in code_delist_dates.values() for d in dates})
            for delist_text in selected_delist_dates:
                delist_dt = pd.to_datetime(delist_text, format="%Y%m%d", errors="coerce")
                if pd.isna(delist_dt): continue
                for offset in range(1, 8):
                    query_dt = delist_dt - pd.Timedelta(days=offset)
                    if query_dt.weekday() >= 5: continue
                    if start_date <= query_dt.date() <= end_date:
                        candidate_query_dates.add(query_dt.normalize())
            
            scan_dates = pd.DatetimeIndex(sorted(candidate_query_dates))
            
            completed_scan_dates = set()
            matched_codes = set()
            failed_dates = {}
            api_diagnostics = []
            
            if os.path.exists(state_json_path):
                try:
                    with open(state_json_path, "r", encoding="utf-8") as f:
                        st_data = json.load(f)
                        completed_scan_dates = set(st_data.get("completed_scan_dates", []))
                        matched_codes = set(st_data.get("matched_codes", []))
                        failed_dates = dict(st_data.get("failed_dates", {}))
                except Exception:
                    pass

            status.update(label=f"총 {len(scan_dates):,}개 영업일 API 응답 및 컬럼 진단 중", state="running")
            direct_progress = st.progress(len(completed_scan_dates) / max(len(scan_dates), 1))
            direct_log = st.empty()

            # [수정 완료] 괄호 짝 오류 수정됨
            pending_dates = [d.strftime("%Y%m%d") for d in scan_dates if d.strftime("%Y%m%d") not in completed_scan_dates]

            def fetch_single_date(qd):
                try:
                    df = fetch_krx_etf_day(krx_openapi_key, qd)
                    return qd, df, None
                except Exception as ex:
                    return qd, pd.DataFrame(), str(ex)

            batch_size = 4
            for i in range(0, len(pending_dates), batch_size):
                chunk = pending_dates[i:i + batch_size]
                chunk_prices = []
                
                with ThreadPoolExecutor(max_workers=batch_size) as executor:
                    futures = {executor.submit(fetch_single_date, qd): qd for qd in chunk}
                    for future in as_completed(futures):
                        query_date, day_df, err = future.result()
                        if err:
                            failed_dates[query_date] = err
                            continue

                        failed_dates.pop(query_date, None)
                        code_field = find_col(day_df, ["ISU_CD", "ISU_SRT_CD", "단축코드", "종목코드"], ("isusrtcd", "단축코드", "종목코드"))
                        
                        api_codes = pd.Series(dtype=str)
                        six_codes = set()
                        overlap = set()
                        if not day_df.empty and code_field:
                            api_codes = day_df[code_field].map(code_key)
                            six_codes = set(api_codes[api_codes.str.fullmatch(r"\d{6}", na=False)])
                            overlap = wanted_codes & six_codes
                            if overlap:
                                matched_codes.update(overlap)
                                col_map = {
                                    "Open": find_col(day_df, ["TDD_OPNPRC", "시가"], ("tddopnprc",)),
                                    "High": find_col(day_df, ["TDD_HGPRC", "고가"], ("tddhgprc",)),
                                    "Low": find_col(day_df, ["TDD_LWPRC", "저가"], ("tddlwprc",)),
                                    "Close": find_col(day_df, ["TDD_CLSPRC", "종가"], ("tddclsprc",)),
                                    "Volume": find_col(day_df, ["ACC_TRDVOL", "거래량"], ("acctrdvol",)),
                                    "Name": find_col(day_df, ["ISU_NM", "종목명"], ("isunm",)),
                                }
                                for _, api_row in day_df.iterrows():
                                    ticker = code_key(api_row.get(code_field, ""))
                                    if ticker not in overlap: continue
                                    close_val = pd.to_numeric(str(api_row.get(col_map["Close"], "")).replace(",", ""), errors="coerce")
                                    chunk_prices.append({
                                        "date": query_date,
                                        "ticker": ticker,
                                        "name": str(api_row.get(col_map["Name"], "")) if col_map["Name"] else "",
                                        "Open": pd.to_numeric(str(api_row.get(col_map["Open"], "")).replace(",", ""), errors="coerce"),
                                        "High": pd.to_numeric(str(api_row.get(col_map["High"], "")).replace(",", ""), errors="coerce"),
                                        "Low": pd.to_numeric(str(api_row.get(col_map["Low"], "")).replace(",", ""), errors="coerce"),
                                        "Close": close_val,
                                        "Volume": pd.to_numeric(str(api_row.get(col_map["Volume"], "")).replace(",", ""), errors="coerce"),
                                        "Adj Close": close_val,
                                        "source": "KRX etf_bydd_trd",
                                    })

                        api_diagnostics.append({
                            "query_date": query_date,
                            "response_rows": len(day_df),
                            "api_columns": "|".join(map(str, day_df.columns)),
                            "code_field_detected": str(code_field or ""),
                            "six_digit_codes_count": len(six_codes),
                            "exact_overlap_count": len(overlap),
                            "sample_api_codes": "|".join(sorted(six_codes)[:5]),
                            "sample_overlap": "|".join(sorted(overlap)[:5])
                        })

                        completed_scan_dates.add(query_date)

                if chunk_prices:
                    df_chunk = pd.DataFrame(chunk_prices)
                    header = not os.path.exists(prices_csv_path)
                    df_chunk.to_csv(prices_csv_path, mode="a", index=False, header=header, encoding="utf-8-sig")

                with open(state_json_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "matched_codes": sorted(matched_codes),
                        "completed_scan_dates": sorted(completed_scan_dates),
                        "failed_dates": failed_dates,
                        "api_diagnostics": api_diagnostics
                    }, f, ensure_ascii=False, indent=2)
                
                progress_val = len(completed_scan_dates) / max(len(scan_dates), 1)
                direct_progress.progress(progress_val)
                direct_log.code(f"진행 중: {len(completed_scan_dates)}/{len(scan_dates)}일 완료 · 매칭 종목: {len(matched_codes)}개")

            price_df = pd.read_csv(prices_csv_path) if os.path.exists(prices_csv_path) else pd.DataFrame()
            if not price_df.empty:
                price_df = price_df.drop_duplicates(["ticker", "date"], keep="last").sort_values(["ticker", "date"])
            
            matched_meta = delisted_direct[delisted_direct["collector_ticker"].isin(matched_codes)].copy()
            outputs["KRX_DELISTED_ETF_METADATA.csv"] = matched_meta
            outputs["KRX_DELISTED_ETF_PRICES.csv"] = price_df
            outputs["KRX_API_DIAGNOSTIC_LOG.csv"] = pd.DataFrame(api_diagnostics)
            outputs["RUN_MANIFEST.json"] = json.dumps({
                "status": "completed_zero_matches" if len(matched_codes) == 0 else "completed_with_matches",
                "matched_codes_count": len(matched_codes),
                "price_rows": len(price_df),
                "completed_scan_dates": len(completed_scan_dates),
                "failed_scan_dates": failed_dates,
                "delisted_source_column": short_col_direct,
                "delisted_total_rows": len(delisted_direct),
                "unique_wanted_codes": len(wanted_codes),
                "note": "If matched_codes_count is 0, exact short code match failed against etf_bydd_trd endpoint for the selected period."
            }, ensure_ascii=False, indent=2)
            
            if len(matched_codes) == 0:
                status.update(label="진단 완료: 일치하는 ETF 코드를 찾지 못했습니다 (매칭 0건)", state="error")
                st.error(f"조회 완료({len(completed_scan_dates)}일)되었으나, 상장폐지 목록 코드와 KRX API 종목코드 간에 일치하는 항목이 **0건**입니다.")
                st.info("아래 다운로드 버튼을 통해 **KRX_API_DIAGNOSTIC_LOG.csv**를 확인하여 API 응답 컬럼과 코드 형식을 진단해 주세요.")
            else:
                status.update(label="데이터 수집 및 검증 완료", state="complete")
                st.success(f"수집 성공: 매칭 종목 {len(matched_codes):,}개 · 가격 행 {len(price_df):,}건")

            st.download_button("진단 및 수집 결과 ZIP 다운로드", make_zip(outputs), file_name=f"ETF_RADAR_DIAGNOSTIC_{start_s}_{end_s}.zip", mime="application/zip", type="primary", use_container_width=True)
            st.stop()

    except Exception as e:
        status.update(label="오류 발생", state="error")
        st.exception(e)
