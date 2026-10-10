# -*- coding: utf-8 -*-
"""ETF RADAR delisted ETF backfill - verified classification mode.
Keeps production app.py untouched. ETF status is confirmed only by exact
identifier matches to the official KRX ETF master; names/security labels are
never used to infer ETF status.
"""
from __future__ import annotations
import io, os, re, json, time, zipfile
from datetime import date
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ETF RADAR · 상장폐지 ETF 검증", page_icon="📊", layout="wide")
st.title("ETF RADAR — 상장폐지 ETF 검증 / 백필")
st.warning("운영 app.py와 분리된 검증 도구입니다. 운영 파일은 수정하지 않습니다.")
st.markdown(
    "상장폐지 목록의 `증권구분`은 ETF 전용 분류가 아닙니다. "
    "종목명이나 `수익증권` 같은 포괄 분류값으로 ETF를 추정하지 않고, "
    "KRX ETF 전종목 기본정보와 **종목코드의 정확한 일치**로만 확인합니다."
)

def secret(key: str) -> str:
    try:
        v = st.secrets.get(key, "")
        return str(v).strip() if v is not None else ""
    except Exception:
        return ""

krx_id, krx_pw = secret("KRX_ID"), secret("KRX_PW")
if krx_id and krx_pw:
    os.environ["KRX_ID"], os.environ["KRX_PW"] = krx_id, krx_pw
    st.success("KRX 인증정보 설정 확인 완료 (값은 표시하지 않습니다).")
else:
    st.error("Streamlit Cloud → App Settings → Secrets에 KRX_ID와 KRX_PW를 설정하세요.")
    st.code('KRX_ID = "본인 KRX 계정 ID"\nKRX_PW = "본인 KRX 계정 비밀번호"', language="toml")

def norm_col(x):
    return re.sub(r"[\s_\-()（）\[\]]+", "", str(x)).lower()

def find_col(df, exact=(), contains=()):
    by_norm = {norm_col(c): c for c in df.columns}
    for x in exact:
        if norm_col(x) in by_norm:
            return by_norm[norm_col(x)]
    for c in df.columns:
        if any(norm_col(x) in norm_col(c) for x in contains):
            return c
    return None

def code6(v):
    s = re.sub(r"\D", "", str(v))
    return s[-6:].zfill(6) if s else ""

def csv_bytes(df):
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

def make_zip(files):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        for n, payload in files.items():
            z.writestr(n, payload)
    return b.getvalue()

with st.sidebar:
    st.header("수집 설정")
    start_date = st.date_input("수집 시작일", value=date(2010, 1, 1), min_value=date(1990, 1, 1), max_value=date.today())
    end_date = st.date_input("수집 종료일", value=min(date(2026, 10, 8), date.today()), min_value=date(1990, 1, 1), max_value=date.today())
    mode = st.radio("수집 범위", ["시험 수집 (ETF 5개)", "일부 수집", "전체 확인 ETF 수집"], index=0)
    limit = 5 if mode == "시험 수집 (ETF 5개)" else (int(st.number_input("수집 ETF 개수", 1, 100, 20, 5)) if mode == "일부 수집" else 0)
    pause = st.slider("종목 간 대기 시간(초)", 0.1, 1.0, 0.3, 0.1)

if st.button("데이터 수집 시작", type="primary", disabled=not (krx_id and krx_pw) or start_date > end_date, use_container_width=True):
    from krx_data_api import fetch
    start_s, end_s = start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")
    status = st.status("KRX 상장폐지 목록 및 ETF 기준정보 조회 중…", expanded=True)
    outputs = {}
    try:
        delisted = fetch("delisted", strtDd=start_s, endDd=end_s)
        if delisted is None or delisted.empty:
            st.error("KRX 상장폐지 목록이 비어 있습니다. 인증, 조회 기간, KRX 계정 권한을 확인하세요.")
            st.stop()
        etf_master = fetch("etf_all_info")
        if etf_master is None or etf_master.empty:
            outputs["KRX_DELISTED_ALL.csv"] = csv_bytes(delisted)
            outputs["RUN_MANIFEST.json"] = json.dumps({
                "status":"etf_master_unavailable", "start":start_s, "end":end_s,
                "delisted_rows":len(delisted), "delisted_columns":list(delisted.columns)
            }, ensure_ascii=False, indent=2).encode("utf-8")
            status.update(label="KRX ETF 기준정보를 받지 못함", state="error")
            st.error("ETF 여부를 확인할 공식 ETF 기준정보를 받지 못했습니다. 이름/분류값으로 대체하지 않고 중단했습니다.")
            st.download_button("진단 ZIP 다운로드", make_zip(outputs), "ETF_RADAR_KRX_MASTER_REVIEW.zip", "application/zip")
            st.stop()

        d_code = find_col(delisted, ["종목코드","단축코드","ISU_SRT_CD"], ("종목코드","단축코드","isusrtcd"))
        e_code = find_col(etf_master, ["종목코드","단축코드","ISU_SRT_CD","종목코드(단축코드)"], ("종목코드","단축코드","isusrtcd"))
        e_isin = find_col(etf_master, ["표준코드","ISU_CD","ISIN"], ("표준코드","isucd","isin"))
        e_name = find_col(etf_master, ["종목명","한글종목명","ISU_ABBRV"], ("종목명","한글명","issueabbrev"))
        d_name = find_col(delisted, ["종목명","한글종목명","ISU_ABBRV"], ("종목명","한글명","issueabbrev"))
        if not d_code or not e_code:
            outputs["KRX_DELISTED_ALL.csv"] = csv_bytes(delisted)
            outputs["KRX_ETF_MASTER.csv"] = csv_bytes(etf_master)
            outputs["RUN_MANIFEST.json"] = json.dumps({
                "status":"identifier_columns_missing", "delisted_columns":list(delisted.columns),
                "etf_master_columns":list(etf_master.columns)
            }, ensure_ascii=False, indent=2).encode("utf-8")
            status.update(label="식별자 컬럼 확인 필요", state="error")
            st.error("두 자료의 종목코드 컬럼을 확인하지 못했습니다. 원본 컬럼을 담아 진단 ZIP을 제공합니다.")
            st.download_button("진단 ZIP 다운로드", make_zip(outputs), "ETF_RADAR_KRX_MASTER_REVIEW.zip", "application/zip")
            st.stop()

        d = delisted.copy()
        e = etf_master.copy()
        d["_code_key"] = d[d_code].map(code6)
        e["_code_key"] = e[e_code].map(code6)
        # Exact KRX short-code match only. Do not classify by product type or name.
        valid_master = e[e["_code_key"].ne("")].drop_duplicates("_code_key")
        confirmed = d[d["_code_key"].isin(set(valid_master["_code_key"]))].copy()
        master_keep = ["_code_key", e_code] + ([e_isin] if e_isin else []) + ([e_name] if e_name else [])
        master_small = valid_master[master_keep].copy()
        rename = {e_code:"krx_etf_master_code"}
        if e_isin: rename[e_isin] = "krx_etf_master_isin"
        if e_name: rename[e_name] = "krx_etf_master_name"
        master_small = master_small.rename(columns=rename)
        confirmed = confirmed.merge(master_small, on="_code_key", how="inner")
        outputs["KRX_DELISTED_ALL.csv"] = csv_bytes(delisted)
        outputs["KRX_ETF_MASTER.csv"] = csv_bytes(etf_master)
        outputs["KRX_DELISTED_ETF_CONFIRMED_BY_CODE.csv"] = csv_bytes(confirmed)
        type_col = find_col(delisted, ["증권구분","상품구분","증권종류","상품종류"], ("증권구분","상품구분","증권종류","상품종류"))
        if type_col:
            outputs["KRX_DELISTED_PRODUCT_TYPE_VALUES.csv"] = csv_bytes(
                delisted[type_col].astype(str).value_counts(dropna=False).rename_axis("value").reset_index(name="count")
            )

        if confirmed.empty:
            manifest = {
                "status":"no_exact_match_to_current_etf_master",
                "start":start_s, "end":end_s, "delisted_rows":int(len(delisted)),
                "current_etf_master_rows":int(len(etf_master)), "confirmed_delisted_etfs":0,
                "classification_column":type_col,
                "classification_values":sorted(delisted[type_col].astype(str).unique().tolist()) if type_col else [],
                "note":"The delisted endpoint's security-type field is not an ETF-specific classification. Current ETF master exact-code matching did not verify any delisted ETFs. Historical ETF master data is required; names and broad security types were not used to guess."
            }
            outputs["RUN_MANIFEST.json"] = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
            status.update(label="과거 ETF 기준정보 필요", state="error")
            st.error("상장폐지 목록의 `증권구분`은 ETF 전용 분류가 아니며, 현재 ETF 기준정보와 일치하는 상장폐지 종목도 없습니다. 상장폐지 당시의 공식 ETF 종목 마스터가 있어야 안전하게 검증할 수 있습니다. 이름으로 추정하지 않고 중단했습니다.")
            st.dataframe(pd.DataFrame([
                {"항목":"상장폐지 목록 행","값":len(delisted)},
                {"항목":"현재 KRX ETF 기준정보 행","값":len(etf_master)},
                {"항목":"정확한 코드 일치 상장폐지 ETF","값":0},
                {"항목":"판별 컬럼","값":type_col or "없음"}
            ]), hide_index=True, use_container_width=True)
            st.download_button("검증 결과 ZIP 다운로드", make_zip(outputs), "ETF_RADAR_KRX_HISTORICAL_MASTER_REQUIRED.zip", "application/zip", type="primary")
            st.stop()

        # A current ETF master match proves ETF identity only for matched identifiers.
        # A historical listing is only collected if KRX master supplies a usable ISIN.
        if not e_isin or "krx_etf_master_isin" not in confirmed.columns:
            status.update(label="ISIN 컬럼 확인 필요", state="error")
            st.error("ETF 코드는 확인됐지만 ETF 기준정보에 ISIN 컬럼이 없어 가격 조회를 안전하게 진행할 수 없습니다.")
            outputs["RUN_MANIFEST.json"] = json.dumps({"status":"isin_column_missing","confirmed_rows":len(confirmed),"etf_master_columns":list(etf_master.columns)}, ensure_ascii=False, indent=2).encode("utf-8")
            st.download_button("진단 ZIP 다운로드", make_zip(outputs), "ETF_RADAR_KRX_ISIN_REVIEW.zip", "application/zip")
            st.stop()

        # Diagnose ISIN failures instead of stopping without a downloadable report.
        isin_raw = confirmed["krx_etf_master_isin"].astype(str).str.strip()
        isin_valid_mask = isin_raw.str.fullmatch(r"KR[0-9]{10}", na=False)
        if not isin_valid_mask.any():
            outputs["KRX_DELISTED_ETF_CODE_MATCHES_NO_ISIN.csv"] = csv_bytes(confirmed)
            outputs["KRX_ETF_MASTER.csv"] = csv_bytes(etf_master)
            outputs["RUN_MANIFEST.json"] = json.dumps({
                "status": "code_match_but_no_valid_isin",
                "start": start_s, "end": end_s,
                "delisted_rows": int(len(delisted)),
                "etf_master_rows": int(len(etf_master)),
                "code_matched_rows": int(len(confirmed)),
                "etf_master_code_column": str(e_code),
                "etf_master_isin_column": str(e_isin),
                "isin_sample_values": isin_raw.head(30).tolist(),
                "isin_valid_pattern": "KR followed by exactly 10 digits",
                "note": "Exact short-code matches were found, but ISIN values did not match the expected format. Inspect source columns and values; no ETF identity was inferred from names or broad type labels."
            }, ensure_ascii=False, indent=2).encode("utf-8")
            status.update(label="종목코드 일치 / ISIN 형식 확인 필요", state="error")
            st.error("종목코드는 일치했지만 ISIN 값이 KR + 숫자 10자리 형식과 일치하지 않습니다. 진단 ZIP에 실제 ISIN 예시와 원본 ETF 기준정보를 담았습니다.")
            st.download_button("ISIN 진단 ZIP 다운로드", make_zip(outputs), "ETF_RADAR_KRX_ISIN_DIAGNOSTIC.zip", "application/zip", type="primary")
            st.stop()

        confirmed = confirmed.loc[isin_valid_mask].copy()
        if limit:
            confirmed = confirmed.head(limit)
        if confirmed.empty:
            st.error("유효한 ISIN이 없어 가격 수집을 진행하지 않았습니다.")
            st.stop()

        price_parts, failures, coverage = [], [], []
        for i, row in enumerate(confirmed.to_dict("records"), 1):
            ticker = code6(row.get("_code_key",""))
            name = str(row.get(d_name,"")) if d_name else str(row.get("krx_etf_master_name",""))
            isin = str(row["krx_etf_master_isin"])
            try:
                prices = fetch("individual_price_trend", isuCd=isin, strtDd=start_s, endDd=end_s, adjBasDd=end_s)
                if prices is None or prices.empty:
                    failures.append({"ticker":ticker,"name":name,"isin":isin,"reason":"empty price result"})
                    continue
                p = prices.copy()
                date_col = find_col(p, ["일자","날짜","거래일","TRD_DD","date"], ("일자","날짜","거래일","trddd","date"))
                close_col = find_col(p, ["종가","TDD_CLSPRC","Close"], ("종가","tddclsprc","close"))
                if not date_col or not close_col:
                    failures.append({"ticker":ticker,"name":name,"isin":isin,"reason":f"price schema unrecognized: {list(p.columns)}"})
                    continue
                out = pd.DataFrame({"date":pd.to_datetime(p[date_col], errors="coerce"),"ticker":ticker,"name":name})
                for target, aliases in {"Open":["시가","TDD_OPNPRC","Open"],"High":["고가","TDD_HGPRC","High"],"Low":["저가","TDD_LWPRC","Low"],"Close":["종가","TDD_CLSPRC","Close"],"Volume":["거래량","ACC_TRDVOL","Volume"],"Adj Close":["수정종가","수정주가","Adj Close"]}.items():
                    c = find_col(p, aliases, tuple(aliases))
                    out[target] = pd.to_numeric(p[c].astype(str).str.replace(",","",regex=False).str.replace("+","",regex=False), errors="coerce") if c else (out["Close"] if target=="Adj Close" else float("nan"))
                out["isin"] = isin
                out = out.dropna(subset=["date"]).sort_values("date")
                price_parts.append(out)
                coverage.append({"ticker":ticker,"name":name,"isin":isin,"rows":len(out),"first_date":str(out.date.min().date()) if len(out) else None,"last_date":str(out.date.max().date()) if len(out) else None})
            except Exception as ex:
                failures.append({"ticker":ticker,"name":name,"isin":isin,"reason":f"{type(ex).__name__}: {ex}"})
            st.progress(i / len(confirmed), text=f"{i}/{len(confirmed)} · {ticker} {name}")
            if i < len(confirmed): time.sleep(float(pause))
        prices_out = pd.concat(price_parts, ignore_index=True) if price_parts else pd.DataFrame()
        outputs["KRX_DELISTED_ETF_PRICES.csv"] = csv_bytes(prices_out)
        outputs["KRX_DELISTED_ETF_FETCH_FAILURES.csv"] = csv_bytes(pd.DataFrame(failures))
        outputs["KRX_DELISTED_ETF_PRICE_COVERAGE.csv"] = csv_bytes(pd.DataFrame(coverage))
        outputs["RUN_MANIFEST.json"] = json.dumps({
            "status":"completed_with_or_without_failures","start":start_s,"end":end_s,
            "delisted_rows":len(delisted),"current_etf_master_rows":len(etf_master),
            "confirmed_by_exact_code":len(confirmed),"price_rows":len(prices_out),
            "success_count":sum(1 for x in coverage if x.get("rows",0)>0),"failure_count":len(failures),
            "classification_method":"exact short-code match to KRX ETF master; no name/type inference",
            "warning":"A current ETF master may not contain ETFs that were already delisted. This run cannot establish a complete historical ETF universe."
        }, ensure_ascii=False, indent=2).encode("utf-8")
        status.update(label="수집 완료", state="complete")
        st.success(f"완료: 가격 {len(prices_out):,}행 · 성공 {len(coverage)}개 · 실패 {len(failures)}개")
        st.download_button("수집 결과 ZIP 다운로드", make_zip(outputs), f"ETF_RADAR_DELISTED_BACKFILL_{start_s}_{end_s}.zip", "application/zip", type="primary", use_container_width=True)
    except Exception as ex:
        status.update(label="수집 중 오류 발생", state="error")
        st.exception(ex)
        st.info("오류 화면이나 Cloud logs를 보내 주세요. 인증정보는 보내지 마세요.")

st.divider()
st.subheader("휴대폰에서 다음 실행")
st.markdown("""
1. GitHub 저장소에서 `backfill_app.py`만 이 수정본으로 교체합니다.
2. **`app.py`는 수정하거나 덮어쓰지 마세요.**
3. Streamlit Cloud의 별도 백필 앱에서 Main file path가 `backfill_app.py`인지 확인하고 재배포합니다.
4. 시험 수집(ETF 5개)을 선택하고 **데이터 수집 시작**을 누릅니다.
5. 결과 ZIP을 내려받아 이 채팅에 첨부합니다.

주의: 이 수정본은 상장폐지 목록의 `증권구분`을 ETF로 오인하지 않도록 고쳤습니다. 현재 ETF 마스터에 없는 과거 상장폐지 ETF는 과거 ETF 기준정보가 별도로 확보되기 전까지 자동 확정하지 않습니다.
""")
