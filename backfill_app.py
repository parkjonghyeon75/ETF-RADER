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

def make_zip(files: dict[str, bytes]) -> bytes:
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, payload in files.items(): zf.writestr(name, payload)
    return mem.getvalue()

def csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

with st.sidebar:
    st.header("수집 설정")
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
        if type_col is None:
            outputs["KRX_DELISTED_SCHEMA_SAMPLE.csv"] = csv_bytes(all_delisted.head(100))
            status.update(label="종목 분류 컬럼 확인 필요", state="error")
            st.error("KRX 응답에서 ETF 분류 컬럼을 찾지 못했습니다. 원본 목록을 다운로드할 수 있게 제공했습니다.")
            outputs["RUN_MANIFEST.json"] = json.dumps({"status":"schema_review_required", "start":start_s, "end":end_s, "columns":list(all_delisted.columns)}, ensure_ascii=False, indent=2).encode("utf-8")
            st.download_button("원본 목록 ZIP 다운로드", make_zip(outputs), file_name="ETF_RADAR_KRX_SCHEMA_REVIEW.zip", mime="application/zip")
            st.stop()
        type_values = all_delisted[type_col].astype(str).str.upper()
        is_etf = type_values.str.contains(r"\bETF\b|상장지수|상장지수펀드", regex=True, na=False)
        if not is_etf.any():
            outputs["KRX_DELISTED_PRODUCT_TYPE_VALUES.csv"] = csv_bytes(all_delisted[type_col].astype(str).value_counts(dropna=False).rename_axis("value").reset_index(name="count"))
            status.update(label="ETF 분류값 확인 필요", state="error")
            st.error("KRX 분류 컬럼은 찾았지만 ETF 값이 확인되지 않았습니다. 이름만으로 추정하지 않고 중단했습니다.")
            outputs["RUN_MANIFEST.json"] = json.dumps({"status":"product_type_review_required", "start":start_s, "end":end_s, "type_column":type_col}, ensure_ascii=False, indent=2).encode("utf-8")
            st.download_button("분류 확인 ZIP 다운로드", make_zip(outputs), file_name="ETF_RADAR_KRX_TYPE_REVIEW.zip", mime="application/zip")
            st.stop()
        etfs = all_delisted.loc[is_etf].copy()
        etfs["collector_name"] = etfs[name_col].astype(str) if name_col else ""
        etfs["collector_ticker"] = etfs[short_col].astype(str).str.extract(r"(\d{6})", expand=False).fillna("") if short_col else ""
        etfs["collector_isin"] = etfs[isin_col].astype(str).str.extract(r"(KR\d{10})", expand=False).fillna("") if isin_col else ""
        etfs["collector_delisting_date"] = etfs[delist_col].map(date8) if delist_col else None
        outputs["KRX_DELISTED_ETF_METADATA.csv"] = csv_bytes(etfs)
        candidates = etfs[etfs["collector_ticker"].ne("") & etfs["collector_isin"].ne("")].copy()
        if limit:
            candidates = candidates.head(int(limit))
        if candidates.empty:
            outputs["RUN_MANIFEST.json"] = json.dumps({"status":"no_valid_etf_identifiers", "start":start_s, "end":end_s, "etf_candidates":len(etfs)}, ensure_ascii=False, indent=2).encode("utf-8")
            st.error("ETF 항목은 찾았지만 가격 조회에 필요한 종목코드와 ISIN을 함께 식별할 수 없습니다.")
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
1. GitHub 저장소에 이 파일을 `backfill_app.py` 이름으로 추가합니다.
2. 저장소 루트의 `requirements.txt`에 필요한 패키지가 들어 있는지 확인합니다.
3. Streamlit Community Cloud에서 **Create app → 기존 저장소 선택 → Main file path를 `backfill_app.py`** 로 지정해 별도 앱으로 배포합니다.
4. 새 앱의 Settings → Secrets에 `KRX_ID`, `KRX_PW`를 설정합니다.
5. 먼저 **시험 수집 (ETF 5개)** 을 실행하고 ZIP을 다운로드합니다.

Streamlit Cloud는 별도 앱에서 다른 엔트리포인트 파일을 지정해 배포할 수 있으며, Secrets는 앱 설정에서 관리합니다.
""")
