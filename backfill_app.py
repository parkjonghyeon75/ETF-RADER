"""ETF RADAR survivorship-bias diagnostic/backfill tool v5.20.0.

Independent Streamlit app. Never imports or edits the live app.py.
Uses exact identifiers only; never guesses codes from names or partial strings.
A simplified one-position fixed-holding-period simulation is diagnostic only and
is never represented as a rerun of the live ETF RADAR engine.
"""
from __future__ import annotations
import io, re, time, zipfile
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import streamlit as st

VERSION = "5.22.0"
TITLE = "ETF RADAR — 상장폐지 ETF 시세 복원 및 생존편향 검증"
ROOT = Path(__file__).resolve().parent
SEARCH_DIRS = [ROOT, ROOT / "data"]

st.set_page_config(page_title=TITLE, layout="wide")
st.title(TITLE)
st.caption(f"독립 진단 도구 v{VERSION} · 운영 app.py를 수정하거나 import하지 않습니다")
st.warning("이 도구의 단순 시뮬레이션은 운영 app.py의 실제 매매 엔진 재현이 아닙니다. 식별자·가격·상장일 자료가 불완전하면 결과를 최종 검증으로 표시하지 않습니다.")

# ---------- parsing and normalization ----------
def norm(v) -> str:
    if v is None: return ""
    s = str(v).strip().upper()
    if s in {"", "NAN", "NONE", "NULL", "NAT"}: return ""
    # CSVs sometimes render numeric short codes as 123456.0; remove only this
    # representation artifact. Preserve leading zeros and all letters.
    if re.fullmatch(r"\d+\.0+", s): s = s.split(".", 1)[0]
    return s

def norm_date(v) -> str:
    if v is None: return ""
    s = str(v).strip()
    if not s or s.upper() in {"NAN", "NONE", "NULL", "NAT"}: return ""
    digits = re.sub(r"\D", "", s)
    if len(digits) == 8 and digits[:4].isdigit():
        try: return pd.to_datetime(digits, format="%Y%m%d", errors="raise").strftime("%Y%m%d")
        except Exception: pass
    d = pd.to_datetime(s, errors="coerce")
    return d.strftime("%Y%m%d") if pd.notna(d) else ""

def read_csv(raw: bytes, label="CSV", *, nrows=None, usecols=None) -> pd.DataFrame:
    errs=[]
    for enc in ("utf-8-sig", "cp949", "utf-8"):
        try:
            df=pd.read_csv(io.BytesIO(raw), dtype=str, keep_default_na=False, encoding=enc, nrows=nrows, usecols=usecols)
            df.columns=[str(c).strip().replace("\ufeff", "") for c in df.columns]
            for c in df.columns: df[c]=df[c].astype(str).str.strip()
            return df
        except Exception as e: errs.append(f"{enc}: {e}")
    raise ValueError(f"{label} 읽기 실패: {' / '.join(errs)}")

def _colkey(value):
    # Match headers despite BOM, spaces, underscores, hyphens, or case differences.
    return re.sub(r"[^0-9A-Z가-힣]", "", str(value).replace("\ufeff", "").strip().upper())

def find_col(df, names):
    if df is None: return None
    exact={str(c).strip().replace("\ufeff", ""):c for c in df.columns}
    lower={str(c).strip().replace("\ufeff", "").lower():c for c in df.columns}
    normalized={_colkey(c):c for c in df.columns}
    for n in names:
        if n in exact: return exact[n]
    for n in names:
        if n.lower() in lower: return lower[n.lower()]
    for n in names:
        if _colkey(n) in normalized: return normalized[_colkey(n)]
    return None

def is_signal_table(df):
    """Recognize the real ETF RADAR signal export by schema, not sample rows.

    INDEPENDENT_SIGNALS.csv uses date + etf + FINAL/FINAL_V2. Header-only
    probing (nrows=0) is intentional, so empty probe frames must still classify.
    """
    d=find_col(df,["date","날짜","일자","기준일","BAS_DD","signal_date","신호일","신호 날짜","거래일"])
    c=find_col(df,["etf","ETF코드","ETF 코드","종목코드","단축코드","ISU_CD","Code","Ticker","ticker","종목코드(단축코드)","ETF Code","ticker_code"])
    f=find_col(df,["FINAL_V2","FINAL","signal","신호","D_미래테마선행가격","최종신호","최종 신호"])
    if not f:
        f=next((col for col in df.columns if re.search(r"FINAL(?:_V2)?|SIGNAL|신호", str(col), re.I)), None)
    return bool(d and c and f)

def is_price_table(df):
    c=find_col(df,["ETF코드","etf","ISU_CD","단축코드","종목코드","Code","Ticker","ticker"])
    d=find_col(df,["날짜","date","Date","일자","기준일","BAS_DD","DATE"])
    close=find_col(df,["Close","close","종가","TDD_CLSPRC","CLSPRC"])
    return bool(c and d and close)

def classify_csv(name, df):
    n=Path(name).name.lower()
    # Official ETF RADAR backtest export. Its actual schema is date + etf +
    # FINAL/FINAL_V2. The filename is a strong hint, but schema validation remains
    # mandatory so unrelated files are never misclassified.
    if n == "independent_signals.csv":
        if is_signal_table(df): return "signals"
        # Keep a specific, visible classification error rather than silently
        # making the signal-file count appear to be zero.
        raise ValueError(
            f"{name}: 공식 신호 파일명은 확인했지만 필수 열(date, etf, FINAL/FINAL_V2)을 찾지 못했습니다. "
            f"실제 컬럼={list(df.columns)}"
        )
    if "independent_price_history" in n and is_price_table(df): return "prices"
    # Fallback for other export versions: classify by actual column signature.
    if is_signal_table(df): return "signals"
    if is_price_table(df): return "prices"
    if find_col(df,["폐지일","상장폐지일","해지일","상장폐지일자"]) and find_col(df,["단축코드","종목코드","ISU_CD","표준코드"]): return "delisted"
    if find_col(df,["표준코드","ISIN"]) and find_col(df,["단축코드"]) and find_col(df,["상장일","상장일자","LIST_DD"]): return "master"
    if "histor" in n or "과거기준" in n or "crosswalk" in n or "코드연결" in n or "식별자연결" in n: return "historical"
    if "delisted" in n or "상장폐지" in n or "폐지목록" in n: return "delisted"
    if "master" in n or "기준정보" in n: return "master"
    if "daily" in n or "raw" in n or "시세" in n: return "prices"
    return ""

def _read_classified_csv(member_name, raw):
    # Probe only the header before deciding which CSVs deserve a full read.
    # This is essential because INDEPENDENT_PRICE_HISTORY.csv expands to 170 MB+
    # in the newer ZIP and includes many columns unused by this diagnostic.
    header=read_csv(raw, member_name, nrows=0)
    role=classify_csv(member_name, header)
    if not role:
        return None, None
    if role == "prices":
        wanted=[]
        for candidates in (["ETF코드","etf","ISU_CD","단축코드","종목코드","Code","Ticker","ticker"],
                           ["날짜","date","Date","일자","기준일","BAS_DD","DATE"],
                           ["Open","open","시가","TDD_OPNPRC","OPNPRC"],
                           ["Close","close","종가","TDD_CLSPRC","CLSPRC"]):
            col=find_col(header,candidates)
            if col and col not in wanted: wanted.append(col)
        if len(wanted) < 3:
            raise ValueError(f"{member_name}: 가격 자료 필수 열 부족. 감지된 열={wanted}")
        df=read_csv(raw, member_name, usecols=wanted)
    else:
        df=read_csv(raw, member_name)
    if role == "signals":
        # Guard against a schema-only false positive: keep the actual table only
        # if date/code/signal columns still exist after the full read.
        if not is_signal_table(df):
            raise ValueError(f"{member_name}: 신호 헤더는 감지했지만 전체 CSV 컬럼 재검증 실패")
    return role, df

def parse_file(name, raw):
    out=[]
    if name.lower().endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for member in z.namelist():
                if member.startswith("__MACOSX/") or not member.lower().endswith(".csv"): continue
                try:
                    member_raw=z.read(member)
                    role,df=_read_classified_csv(member,member_raw)
                    if role: out.append((role,f"{name}::{member}",df))
                except Exception as e: out.append(("error",f"{name}::{member}",str(e)))
    elif name.lower().endswith(".csv"):
        role,df=_read_classified_csv(name,raw)
        if role: out.append((role,name,df))
    return out

def csv_bytes(df): return df.to_csv(index=False).encode("utf-8-sig")

def get_repo_files():
    result=[]
    for folder in SEARCH_DIRS:
        if folder.is_dir():
            for p in folder.iterdir():
                if p.is_file() and p.suffix.lower() in {".csv",".zip"}:
                    try: result.extend(parse_file(p.name,p.read_bytes()))
                    except Exception: pass
    return result

# ---------- source loading ----------
st.header("1. 자료 연결")
st.write("여러 CSV/ZIP을 한 번에 선택할 수 있습니다. ZIP 안에서는 파일명보다 CSV 컬럼 구조를 우선해 신호·가격 파일을 구분합니다. 과거 코드 연결은 공식 코드 연결표가 제공된 경우에만 사용합니다.")
repo_items=get_repo_files()
# Mobile browsers can fail silently with Streamlit multi-file selection.
# Use a single-file picker here and make the receipt state explicit.
upload=st.file_uploader("CSV 또는 ZIP 파일 하나 선택",type=["csv","zip"],accept_multiple_files=False,key="sources_single_v59")
items=list(repo_items); errors=[]; upload_audit=[]
if upload is not None:
    try:
        raw_upload=upload.getvalue()
        parsed=parse_file(upload.name,raw_upload)
        items.extend(parsed)
        parsed_roles=sorted({role for role, _, _ in parsed if role != "error"})
        inner_errors=[f"{src}: {df}" for role, src, df in parsed if role == "error"]
        errors.extend(inner_errors)
        upload_audit.append({
            "파일명": upload.name,
            "업로드 수신": "성공",
            "파일 크기(bytes)": len(raw_upload),
            "내부 CSV/자료 수": sum(1 for role, _, _ in parsed if role != "error"),
            "인식된 자료 유형": ", ".join(parsed_roles) if parsed_roles else "없음",
            "상태": "분석 가능" if parsed_roles else ("읽기 오류" if inner_errors else "파일은 수신했으나 자료 유형 미인식"),
            "세부 오류": " | ".join(inner_errors),
        })
    except Exception as e:
        msg=f"{upload.name}: {type(e).__name__}: {e}"
        errors.append(msg)
        upload_audit.append({"파일명":upload.name,"업로드 수신":"파일 선택됨","파일 크기(bytes)":getattr(upload,"size",0),"내부 CSV/자료 수":0,"인식된 자료 유형":"없음","상태":"파싱 실패","세부 오류":msg})
if upload is not None:
    st.subheader("업로드 수신 결과 — 파일별 확인")
    st.dataframe(pd.DataFrame(upload_audit),use_container_width=True,hide_index=True)
    if upload_audit and all(row.get("상태") == "분석 가능" for row in upload_audit):
        st.success(f"업로드 확인: {upload.name} ({len(upload.getvalue()):,} bytes) 수신 및 자료 분석 완료")
    else:
        st.warning("파일은 선택되어 수신됐지만 자료 분류에 실패했습니다. 위 표의 세부 오류를 확인하세요.")
else:
    st.info("아직 앱에 전달된 파일이 없습니다. Upload를 누르고 파일을 하나 선택하세요. 파일명이 표시되지 않으면 앱이 파일을 수신하지 못한 상태입니다.")
for e in errors: st.error(e)
roles={"delisted":"KRX 상장폐지 목록","master":"현행 KRX ETF 기준정보","historical":"과거 기준정보(선택)","prices":"일별 가격 이력","signals":"백테스트 신호"}
selected={}
# Prefer uploaded source over repository source; if duplicates, keep every signal/price table below.
for role,_,_ in items:
    if role in roles: selected[role]=selected.get(role,0)+1
status_rows=[]
for role,label in roles.items():
    matches=[(src,df) for r,src,df in items if r==role and isinstance(df,pd.DataFrame)]
    status_rows.append({"자료":label,"인식 파일 수":len(matches),"출처 예시":"; ".join(x[0] for x in matches[:3])})
st.dataframe(pd.DataFrame(status_rows),use_container_width=True,hide_index=True)
# Explicitly expose signal schema/row/flag counts per uploaded source. This prevents
# a recognized signal file from being confused with a nonzero TRUE-signal count.
signal_source_audit=[]
for src_sig, df_sig in [(src, df) for role,src,df in items if role=="signals" and isinstance(df,pd.DataFrame)]:
    d_sig=find_col(df_sig,["date","날짜","일자","기준일","BAS_DD","signal_date","신호일","신호 날짜","거래일"])
    c_sig=find_col(df_sig,["etf","ETF코드","ETF 코드","종목코드","단축코드","ISU_CD","Code","Ticker","ticker","종목코드(단축코드)","ETF Code","ticker_code"])
    flags=[c for c in df_sig.columns if re.search(r"FINAL(?:_V2)?|SIGNAL|신호",str(c),re.I)]
    rec={"출처":src_sig,"행수":len(df_sig),"날짜컬럼":d_sig or "","코드컬럼":c_sig or "","신호컬럼":"; ".join(flags),"고유코드수":int(df_sig[c_sig].map(norm).replace("",pd.NA).nunique()) if c_sig else 0}
    for flag_col in flags:
        vals=df_sig[flag_col].map(lambda v:norm(v) in {"TRUE","1","Y","YES","T","참"})
        rec[f"{flag_col}_TRUE건수"]=int(vals.sum())
    signal_source_audit.append(rec)
if signal_source_audit:
    st.subheader("신호 파일 실제 인식 진단")
    st.dataframe(pd.DataFrame(signal_source_audit),use_container_width=True,hide_index=True)
# Show why candidate CSVs were not assigned to the signal role instead of silently dropping them.
unknown_candidates=[]
for role0, src0, df0 in items:
    if isinstance(df0, pd.DataFrame) and role0 not in roles and role0 != "error":
        unknown_candidates.append({"출처":src0,"행수":len(df0),"컬럼":", ".join(map(str,df0.columns[:30]))})
if unknown_candidates:
    with st.expander("분류되지 않은 CSV 확인", expanded=False):
        st.dataframe(pd.DataFrame(unknown_candidates),use_container_width=True,hide_index=True)

# collect all dataframes by role; use uploaded inputs first by reverse order
byrole={r:[] for r in roles}
for r,src,df in items:
    if r in byrole and isinstance(df,pd.DataFrame): byrole[r].append((src,df))

# Early source-only diagnostic ZIP; available before API collection or simulation.
early_diag = {"source_status.csv": csv_bytes(pd.DataFrame(status_rows))}
for role_name, role_items in byrole.items():
    for idx, (source_name, source_df) in enumerate(role_items, start=1):
        safe_source = re.sub(r"[^A-Za-z0-9_.-]+", "_", Path(source_name).name)[:80] or f"source_{idx}.csv"
        early_diag[f"inputs/{role_name}_{idx}_{safe_source}.csv"] = csv_bytes(source_df)
early_buffer = io.BytesIO()
with zipfile.ZipFile(early_buffer, "w", zipfile.ZIP_DEFLATED) as early_zip:
    for member_name, member_bytes in early_diag.items():
        early_zip.writestr(member_name, member_bytes)
    early_zip.writestr("README.txt", f"ETF RADAR source diagnostic v{VERSION}\nParsed source tables before API collection and matching.\n")
st.download_button("📦 초기 자료 진단 ZIP 다운로드", data=early_buffer.getvalue(), file_name="ETF_RADAR_SOURCE_DIAGNOSTIC.zip", mime="application/zip", key="dl_zip_early_v510")

# ---------- KRX API, optional ----------
st.header("2. KRX 공식 일별 시세 수집(선택)")
st.caption("KRX ETF 일별매매정보는 날짜별 요청이며 응답의 ISU_CD는 종목코드입니다. 현재 API의 6자리 코드와 상장폐지 목록의 8자리 코드가 다르면 자동으로 자르거나 이름으로 연결하지 않습니다. 과거 공식 코드 연결표가 있어야 정확히 연결할 수 있습니다.")
api_key=""
try: api_key=str(st.secrets.get("KRX_OPENAPI_KEY","")).strip()
except Exception: pass
if api_key: st.success("KRX_OPENAPI_KEY 설정 확인됨(키 값 비표시)")
else: st.info("API 키가 없으면 업로드된 가격 자료만 사용합니다.")

# Focused proof test for a confirmed delisted ETF. This deliberately tests one
# exact code/date and reports the raw API response; it does not infer a match.
st.subheader("우선 검증: 상장폐지 ETF 과거 시세 1건 확인")
st.write("KRX 공시로 확인된 **KODEX 25-11 회사채(A+이상)액티브 (467940)** 를 대상으로 2024-10-10의 공식 ETF 일별매매정보 응답에 종목코드가 실제 포함되는지 확인합니다.")
st.caption("종목코드 467940 · 조회일 20241010 · 이름 추정/부분 코드 매칭 없음")
if st.button("467940 과거 시세 검증 실행", disabled=not bool(api_key), key="targeted_467940_test_v580"):
    import requests
    test_rows=[]
    test_meta=[]
    try:
        test_resp=requests.get(
            "https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd",
            params={"basDd":"20241010"},
            headers={"AUTH_KEY":api_key}, timeout=20,
        )
        test_meta.append({"조회일":"20241010","HTTP 상태":test_resp.status_code,"응답 바이트":len(test_resp.content)})
        if test_resp.status_code == 200:
            try:
                test_payload=test_resp.json()
                test_data=test_payload.get("OutBlock_1",[]) if isinstance(test_payload,dict) else []
                if isinstance(test_data,list):
                    for rec in test_data:
                        if isinstance(rec,dict) and norm(rec.get("ISU_CD")) == "467940":
                            test_rows.append(rec)
                    st.session_state["targeted_467940_raw_v580"] = pd.DataFrame(test_data).astype(str)
                    st.session_state["targeted_467940_meta_v580"] = pd.DataFrame(test_meta)
                    st.session_state["targeted_467940_match_v580"] = pd.DataFrame(test_rows)
                    if test_rows:
                        st.success("확인 성공: KRX 응답에서 ISU_CD=467940 정확 일치 행을 찾았습니다.")
                        st.dataframe(pd.DataFrame(test_rows), use_container_width=True, hide_index=True)
                    else:
                        st.warning(f"HTTP 200이지만 해당 날짜 응답 {len(test_data):,}행에서 ISU_CD=467940을 찾지 못했습니다. 이는 '과거 데이터 미제공'을 단정하지 않고, 해당 날짜 응답에 없다는 뜻입니다.")
                        st.write("응답 컬럼:", ", ".join(map(str, pd.DataFrame(test_data).columns)) if test_data else "OutBlock_1이 비어 있음")
                else:
                    st.error("HTTP 200 응답이지만 OutBlock_1이 목록 형식이 아닙니다.")
                    st.code(test_resp.text[:3000])
            except Exception as e:
                st.error(f"JSON 해석 실패: {e}")
                st.code(test_resp.text[:3000])
        else:
            st.error(f"KRX API 오류: HTTP {test_resp.status_code}")
            st.code(test_resp.text[:3000])
        st.session_state["targeted_467940_meta_v580"] = pd.DataFrame(test_meta)
    except Exception as e:
        st.error(f"요청 실패: {e}")
        st.session_state["targeted_467940_meta_v580"] = pd.DataFrame([{"조회일":"20241010","HTTP 상태":"EXCEPTION","오류":str(e)}])

if "targeted_467940_meta_v580" in st.session_state:
    test_meta_df=st.session_state["targeted_467940_meta_v580"]
    st.dataframe(test_meta_df, use_container_width=True, hide_index=True)
    test_csvs={"request_status.csv":csv_bytes(test_meta_df)}
    if "targeted_467940_match_v580" in st.session_state:
        test_csvs["exact_match_467940.csv"]=csv_bytes(st.session_state["targeted_467940_match_v580"])
    if "targeted_467940_raw_v580" in st.session_state:
        test_csvs["full_krx_response_20241010.csv"]=csv_bytes(st.session_state["targeted_467940_raw_v580"])
    test_zip=io.BytesIO()
    with zipfile.ZipFile(test_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, payload in test_csvs.items():
            zf.writestr(filename, payload)
        zf.writestr("README.txt", "Exact-code KRX API test for 467940 on 2024-10-10. No name or partial-code matching was used.\n")
    st.download_button("📦 467940 단건 검증 결과 ZIP", data=test_zip.getvalue(), file_name="KRX_467940_20241010_TEST.zip", mime="application/zip", key="dl_467940_test_v510")
with st.expander("API 수집 설정",expanded=False):
    api_start=st.date_input("시작일",value=date(2020,1,2),key="api_start_v56")
    api_end=st.date_input("종료일",value=date(2026,10,8),key="api_end_v56")
    max_days=st.number_input("최대 조회 거래일 수",min_value=1,max_value=2000,value=2000,step=50,key="api_days_v56")
    delay=st.slider("요청 간 대기(초)",min_value=0.0,max_value=1.0,value=0.1,step=0.05,key="api_delay_v56")
    if st.button("KRX 일별 시세 수집",disabled=(not api_key or api_start>api_end),key="api_collect_v55"):
        import requests
        dates=[]; cur=api_start
        while cur<=api_end and len(dates)<int(max_days):
            if cur.weekday()<5: dates.append(cur.strftime("%Y%m%d"))
            cur+=timedelta(days=1)
        # Resume-safe historical collection: preserve prior successful rows and checkpoint
        # every 10 requests so a later request failure does not erase earlier data.
        got=[]; fail=[]; bar=st.progress(0); msg=st.empty(); sess=requests.Session()
        prior=st.session_state.get("api_daily_v56",pd.DataFrame())
        if isinstance(prior,pd.DataFrame) and not prior.empty: got.append(prior.copy())
        prior_fail=st.session_state.get("api_fail_v56",pd.DataFrame())
        if isinstance(prior_fail,pd.DataFrame) and not prior_fail.empty: fail.extend(prior_fail.to_dict("records"))
        for i,dd in enumerate(dates):
            try:
                resp=None
                for attempt in range(3):
                    try:
                        resp=sess.get("https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd",params={"basDd":dd},headers={"AUTH_KEY":api_key},timeout=20)
                        if resp.status_code >= 500 and attempt < 2:
                            time.sleep(1.0*(attempt+1)); continue
                        break
                    except Exception:
                        if attempt >= 2: raise
                        time.sleep(1.0*(attempt+1))
                if resp is not None and resp.status_code==200:
                    payload=resp.json(); rows=payload.get("OutBlock_1",[]) if isinstance(payload,dict) else []
                    if rows:
                        d=pd.DataFrame(rows).astype(str); d["BAS_DD"]=d.get("BAS_DD",dd); d["_REQUEST_DATE"]=dd; got.append(d)
                elif resp is not None:
                    fail.append({"날짜":dd,"HTTP":resp.status_code,"오류":resp.text[:250]})
            except Exception as e: fail.append({"날짜":dd,"HTTP":"EXCEPTION","오류":str(e)[:250]})
            if (i+1)%10==0 or i+1==len(dates):
                checkpoint=pd.concat(got,ignore_index=True) if got else pd.DataFrame()
                if not checkpoint.empty and "BAS_DD" in checkpoint.columns and "ISU_CD" in checkpoint.columns:
                    checkpoint=checkpoint.drop_duplicates(["BAS_DD","ISU_CD"],keep="last")
                st.session_state["api_daily_v56"]=checkpoint
                st.session_state["api_fail_v56"]=pd.DataFrame(fail)
            bar.progress((i+1)/max(1,len(dates))); msg.write(f"{i+1}/{len(dates)}일 조회 · 누적 수신 {sum(len(x) for x in got):,}행 · 오류 {len(fail)}")
            if delay: time.sleep(float(delay))
        new=pd.concat(got,ignore_index=True) if got else pd.DataFrame()
        if not new.empty and "BAS_DD" in new.columns and "ISU_CD" in new.columns:
            new=new.drop_duplicates(["BAS_DD","ISU_CD"],keep="last")
        st.session_state["api_daily_v56"]=new; st.session_state["api_fail_v56"]=pd.DataFrame(fail)
        st.success(f"조회 완료: 이번 실행 요청 {len(dates):,}일, 누적 수신 {len(new):,}행, 누적 오류 {len(fail):,}일. 오류가 있으면 실패 CSV를 확인하세요.")
api_df=st.session_state.get("api_daily_v56",pd.DataFrame())
if not api_df.empty:
    byrole["prices"].append(("KRX OpenAPI(이번 세션)",api_df))

# The targeted proof test's raw response contains the entire ETF market for that
# date (hundreds of rows), not just the target ETF. Only inject the exact-code row
# into the price pipeline; keep the full raw response in the diagnostic ZIP only.
targeted_raw = st.session_state.get("targeted_467940_raw_v580", pd.DataFrame())
targeted_match_for_prices = st.session_state.get("targeted_467940_match_v580", pd.DataFrame())
if isinstance(targeted_match_for_prices, pd.DataFrame) and not targeted_match_for_prices.empty:
    byrole["prices"].append(("KRX OpenAPI(467940 단건검증·정확일치)", targeted_match_for_prices))

# ---------- prepare price tables and signals ----------
def canonical_prices(df, source):
    cc=find_col(df,["ETF코드","etf","ISU_CD","단축코드","종목코드","Code","Ticker","ticker"])
    dc=find_col(df,["날짜","date","Date","일자","기준일","BAS_DD","DATE"])
    oc=find_col(df,["Open","open","시가","TDD_OPNPRC","OPNPRC"])
    xc=find_col(df,["Close","close","종가","TDD_CLSPRC","CLSPRC"])
    if not cc or not dc or not xc: return pd.DataFrame()
    x=pd.DataFrame({"_CODE":df[cc].map(norm),"_DATE":df[dc].map(norm_date),"_OPEN":pd.to_numeric(df[oc].astype(str).str.replace(",","",regex=False),errors="coerce") if oc else float("nan"),"_CLOSE":pd.to_numeric(df[xc].astype(str).str.replace(",","",regex=False),errors="coerce"),"_SOURCE":source})
    return x[(x._CODE!="")&(x._DATE!="")&(x._CLOSE>0)].copy()
price_tables=[]
for src,df in byrole["prices"]:
    x=canonical_prices(df,src)
    if not x.empty: price_tables.append(x)
prices=pd.concat(price_tables,ignore_index=True) if price_tables else pd.DataFrame(columns=["_CODE","_DATE","_OPEN","_CLOSE","_SOURCE"])
if not prices.empty:
    # Preserve first-priority source (repo first, then uploaded/API); duplicate keys are explicit.
    prices=prices.drop_duplicates(["_CODE","_DATE"],keep="last").sort_values(["_CODE","_DATE"]).reset_index(drop=True)

st.header("3. 상장폐지 종목·상장기간 검증")
st.warning("주의: ETF라고 명시된 증권구분 값이 없는 일반 상장폐지 목록은 ETF 상장폐지 근거로 사용하지 않습니다. 이 자료의 상장일/폐지일 및 6자리 코드만으로 ETF 생존편향 보정을 수행하지 않습니다.")
delisted_src=byrole["delisted"][-1] if byrole["delisted"] else None
master_src=byrole["master"][-1] if byrole["master"] else None
hist_src=byrole["historical"][-1] if byrole["historical"] else None
match_df=pd.DataFrame(); validity={}
if delisted_src:
    delisted=delisted_src[1]
    code_guess=find_col(delisted,["단축코드","종목코드","ISU_CD","표준코드","종목코드(단축코드)"])
    dc_options=list(delisted.columns)
    dcode=st.selectbox("상장폐지 목록의 코드 컬럼",dc_options,index=dc_options.index(code_guess) if code_guess in dc_options else 0,key="dcode_v55")
    date_guess=find_col(delisted,["폐지일","상장폐지일","해지일","상장폐지일자"])
    # Use listing date already present in the official delisted source when available.
    # A separate historical crosswalk is not required merely to read this date.
    delisted_listdate_col=find_col(delisted,["상장일","상장일자","LIST_DD","상장일(YYYYMMDD)"])
    name_guess=find_col(delisted,["종목명","한글종목명","종목약명","ISU_NM"])
    date_opts=["(없음)"]+dc_options; name_opts=["(없음)"]+dc_options
    ddate=st.selectbox("상장폐지일 컬럼",date_opts,index=date_opts.index(date_guess) if date_guess in dc_options else 0,key="ddate_v55")
    dname=st.selectbox("종목명 컬럼(표시용만)",name_opts,index=name_opts.index(name_guess) if name_guess in dc_options else 0,key="dname_v55")
    master=master_src[1] if master_src else None
    hist=hist_src[1] if hist_src else None
    mcode=find_col(master,["단축코드","종목코드","ISU_CD"]) if master is not None else None
    misin=find_col(master,["표준코드","ISIN"]) if master is not None else None
    # Historical crosswalk is accepted only when it explicitly contains both the delisted
    # identifier and the corresponding 6-digit ETF short code. No truncation/name matching.
    hsrc=find_col(hist,["상장폐지코드","원본종목코드","폐지종목코드","종목코드(8자리)"]) if hist is not None else None
    hcode=find_col(hist,["과거단축코드","단축코드","ETF코드","ISU_CD","종목코드"]) if hist is not None else None
    hlist=find_col(hist,["상장일","상장일자","LIST_DD","상장일(YYYYMMDD)"]) if hist is not None else None
    crosswalk={}
    crosswalk_rejections=[]
    if hist is not None and hsrc and hcode and hsrc != hcode:
        _hm=hist[[hsrc,hcode]].copy()
        _hm["_SRC"]=_hm[hsrc].map(norm); _hm["_DST"]=_hm[hcode].map(norm)
        _hm=_hm[(_hm["_SRC"]!="")&(_hm["_DST"]!="")].drop_duplicates()
        for _key,_grp in _hm.groupby("_SRC"):
            _targets=sorted(set(_grp["_DST"]))
            # An official crosswalk must explicitly map the exact source identifier
            # to one unambiguous six-digit ETF short code. Never truncate or guess.
            if len(_targets) != 1:
                crosswalk_rejections.append({"원본코드":_key,"대상코드": "|".join(_targets),"사유":"대상 코드가 복수"})
            elif not re.fullmatch(r"\d{6}", _targets[0]):
                crosswalk_rejections.append({"원본코드":_key,"대상코드":_targets[0],"사유":"대상 코드가 6자리 숫자 단축코드가 아님"})
            else:
                crosswalk[_key]=_targets[0]
    master_codes=set(master[mcode].map(norm)) if master is not None and mcode else set()
    master_isins=set(master[misin].map(norm)) if master is not None and misin else set()
    # ISIN is a separate identifier; never compare a 6-digit short code to an ISIN.
    disin=find_col(delisted,["표준코드","ISIN","ISIN코드","국제증권식별번호"])
    # A generic KRX delisted-securities list is NOT evidence that each row was an ETF.
    # Only explicitly identified ETF rows may constrain ETF signals.
    delisted_security_type_col = find_col(delisted, ["증권구분", "증권 종류", "증권종류", "상품구분"])
    _etf_type_values = {"ETF", "상장지수펀드", "상장지수집합투자기구"}
    def _row_is_explicit_etf(row):
        if not delisted_security_type_col:
            return False
        return norm(row.get(delisted_security_type_col, "")) in _etf_type_values

    rows=[]
    for _,r in delisted.iterrows():
        code=norm(r[dcode])
        if not code: continue
        deldate=norm_date(r[ddate]) if ddate!="(없음)" else ""
        nm=str(r[dname]) if dname!="(없음)" else ""
        isin=norm(r[disin]) if disin and disin in delisted.columns else ""
        # No partial-code/name matching and no automatic 8-digit -> 6-digit conversion.
        # Direct equality is valid only for an already-six-digit numeric short code;
        # other identifiers need an explicit, unambiguous official crosswalk.
        if code in crosswalk:
            price_code=crosswalk[code]
            code_evidence="공식 연결표 완전일치"
        elif re.fullmatch(r"\d{6}", code):
            price_code=code
            code_evidence="동일 6자리 코드 완전일치"
        else:
            price_code=""
            code_evidence="공식 연결표 없음 — 가격코드 미확정"
        observed=prices[prices["_CODE"].eq(price_code)] if price_code and not prices.empty else pd.DataFrame()
        listdate=""
        listdate_source=""
        # Prefer the official delisted file's own listing date; fall back to an
        # unambiguous historical reference row if the source does not contain it.
        if delisted_listdate_col:
            listdate=norm_date(r[delisted_listdate_col])
            if listdate: listdate_source="상장폐지 목록의 상장일"
        if not listdate and hist is not None and hlist:
            if hsrc and hcode and code in crosswalk:
                hs=hist[hist[hsrc].map(norm).eq(code) & hist[hcode].map(norm).eq(price_code)]
            elif hcode and not hsrc:
                # Listing date alone is not a code crosswalk; accept only an exact code match.
                hs=hist[hist[hcode].map(norm).eq(code)]
            else:
                hs=pd.DataFrame()
            if len(hs)==1:
                listdate=norm_date(hs.iloc[0][hlist])
                if listdate: listdate_source="과거 기준정보"
        explicit_etf = _row_is_explicit_etf(r)
        rows.append({"상장폐지코드":code,"가격조회코드(정확연결)":price_code,"코드연결근거":code_evidence,"종목명(표시용)":nm,"증권구분_원본값":str(r.get(delisted_security_type_col, "")) if delisted_security_type_col else "컬럼 없음","ETF_명시확인":explicit_etf,"폐지일":deldate,"상장일_확인값":listdate,"상장일_근거":listdate_source,"현행마스터_단축코드정확일치":code in master_codes,"상장폐지목록_ISIN":isin,"현행마스터_ISIN정확일치":bool(isin and isin in master_isins),"관측가격행수":len(observed),"최초관측일":observed["_DATE"].min() if len(observed) else "","최종관측일":observed["_DATE"].max() if len(observed) else "","상장기간완전확인":bool(explicit_etf and listdate and deldate and listdate<=deldate),"판정":("ETF 명시 확인 · 가격 관측됨" if explicit_etf and len(observed) else "ETF 명시 확인 · 가격 미관측" if explicit_etf else "ETF 여부 미확인 — 보정 근거로 사용 불가")})
    match_df=pd.DataFrame(rows).drop_duplicates("상장폐지코드") if rows else pd.DataFrame()
    for _,r in match_df.iterrows():
        _window={"상장일":r["상장일_확인값"],"폐지일":r["폐지일"]}
        _source_code=norm(r.get("상장폐지코드", ""))
        _pc=norm(r.get("가격조회코드(정확연결)", ""))
        _evidence=str(r.get("코드연결근거", ""))
        _etf_verified=bool(r.get("ETF_명시확인", False))
        # Never apply generic-security delisting dates to ETF signals.
        if _etf_verified and _source_code and _evidence in {"공식 연결표 완전일치", "동일 6자리 코드 완전일치"}:
            validity[_source_code]=_window
        if _etf_verified and _pc and _evidence in {"공식 연결표 완전일치", "동일 6자리 코드 완전일치"}:
            validity[_pc]=_window
    if not match_df.empty:
        st.metric("폐지목록 고유 코드",f"{len(match_df):,}")
        st.metric("폐지목록 코드 중 가격 관측",f"{int((match_df['관측가격행수']>0).sum()):,}")
        st.dataframe(match_df.head(500),use_container_width=True,hide_index=True)
else:
    st.error("상장폐지 목록을 인식하지 못했습니다. KRX_DELISTED_ALL.csv 또는 해당 자료가 포함된 ZIP을 연결하세요.")

# ---------- signal selection and explicitly diagnostic simulation ----------
st.header("4. 신호 데이터와 보정 전후 진단 계산")
signal_options=[]
for src,df in byrole["signals"]:
    if is_signal_table(df): signal_options.append((src,df))
if signal_options:
    labels=[x[0] for x in signal_options]
    chosen=st.selectbox("신호 CSV 선택",labels,key="signal_source_v57")
    sdf=next(df for src,df in signal_options if src==chosen)
    sig_date=find_col(sdf,["date","날짜","일자","기준일","BAS_DD","signal_date","신호일"])
    sig_code=find_col(sdf,["etf","ETF코드","종목코드","단축코드","ISU_CD","Code","Ticker","ticker"])
    flag_cols=[c for c in ["FINAL_V2","FINAL","signal","신호","D_미래테마선행가격"] if c in sdf.columns]
    if not flag_cols: flag_cols=[c for c in sdf.columns if re.search(r"FINAL|SIGNAL|신호",c,re.I)]
    if sig_date and sig_code and flag_cols:
        flag=st.selectbox("신호 플래그 컬럼",flag_cols,index=0,key="flag_v56")
        c1,c2=st.columns(2)
        with c1: bt_start=st.date_input("백테스트 시작일",value=date(2020,1,1),key="bt_start_v55")
        with c2: bt_end=st.date_input("백테스트 종료일",value=date.today(),key="bt_end_v55")
        hold=int(st.number_input("최대 보유 거래일",min_value=1,max_value=250,value=20,key="hold_v55"))
        fee=float(st.number_input("편도 수수료(%)",min_value=0.0,max_value=2.0,value=0.10,step=0.05,key="fee_v55"))/100
        slip=float(st.number_input("편도 슬리피지(%)",min_value=0.0,max_value=2.0,value=0.05,step=0.05,key="slip_v55"))/100
        cash0=float(st.number_input("초기자산(원)",min_value=100000,value=10000000,step=1000000,key="cash0_v55"))
        if st.button("진단 계산 실행",type="primary",key="run_v55"):
            if prices.empty: st.error("유효한 가격 자료가 없습니다. 가격 CSV/ZIP 또는 KRX 시세를 먼저 연결하세요.")
            elif bt_start>bt_end: st.error("백테스트 시작일이 종료일보다 늦습니다.")
            else:
                sig=sdf.copy(); sig["_CODE"]=sig[sig_code].map(norm); sig["_DATE"]=sig[sig_date].map(norm_date)
                valid_signal_date_rows=int((sig["_DATE"]!="").sum())
                truth={"TRUE","1","Y","YES","T","참"}
                sig["_FLAG"]=sig[flag].map(lambda x:norm(x) in truth)
                sig=sig[sig["_FLAG"]&(sig["_DATE"]>=bt_start.strftime("%Y%m%d"))&(sig["_DATE"]<=bt_end.strftime("%Y%m%d"))].sort_values("_DATE")
                pmap={c:g.reset_index(drop=True) for c,g in prices.groupby("_CODE")}
                # Map a signal identifier to a price identifier only when the audit
                # table established an exact identifier or an unambiguous official
                # crosswalk. Never infer from names, suffixes, or partial codes.
                signal_to_price_code={}
                if not match_df.empty:
                    for _, mr in match_df.iterrows():
                        source_code=norm(mr.get("상장폐지코드", ""))
                        target_code=norm(mr.get("가격조회코드(정확연결)", ""))
                        evidence=str(mr.get("코드연결근거", ""))
                        if source_code and target_code and evidence in {"공식 연결표 완전일치", "동일 6자리 코드 완전일치"}:
                            signal_to_price_code[source_code]=target_code
                sig["_PRICE_CODE"]=sig["_CODE"].map(lambda c: signal_to_price_code.get(c,c))
                missing_price_codes=sorted({code for code, price_code in zip(sig["_CODE"],sig["_PRICE_CODE"]) if code and price_code not in pmap})
                # Record whether the selected signal file actually contains usable signals.
                signal_diagnostics = {
                    "선택 신호파일": chosen,
                    "신호 원본 행수": int(len(sdf)),
                    "신호 원본 중 날짜 유효 행수": valid_signal_date_rows,
                    "선택 기간 내 TRUE 신호 행수": int(len(sig)),
                    "선택 기간 내 신호 코드 수": int(sig["_CODE"].replace("", pd.NA).nunique()),
                    "가격자료 코드 수": int(len(pmap)),
                    "가격자료 없는 신호 코드 수": int(len(missing_price_codes)),
                }
                def sim(corrected, allow_overlap=False):
                    cash=cash0; peak=cash0; mdd=0.0; next_free=""; trades=[]; equity=[]
                    rejected={}
                    def reject(reason): rejected[reason]=rejected.get(reason,0)+1
                    for _,s in sig.iterrows():
                        code=s["_CODE"]; sd=s["_DATE"]
                        if not code: reject("종목코드 비어 있음"); continue
                        window=validity.get(code,{}) if corrected else {}
                        ld=window.get("상장일",""); xd=window.get("폐지일","")
                        # In corrected run, require verified listing and delisting dates for
                        # delisted-list codes; otherwise do not silently treat as corrected.
                        if corrected and code in validity and (not ld or not xd): reject("상장일/폐지일 미확인"); continue
                        if corrected and code in validity and (sd<ld or sd>xd): reject("신호일이 상장기간 밖"); continue
                        price_code=signal_to_price_code.get(code, code)
                        p=pmap.get(price_code)
                        if p is None: reject("해당 종목 가격표 없음(정확 코드/공식 연결 없음)"); continue
                        possible=p.index[p["_DATE"].gt(sd)].tolist()
                        if not possible: reject("신호일 이후 가격 없음"); continue
                        j=possible[0]; ed=p.loc[j,"_DATE"]
                        # CRITICAL: never carry an old signal forward to the first price
                        # months/years later. Entry must be the next available trading
                        # session, within 7 calendar days of the signal date.
                        try:
                            signal_day=pd.to_datetime(sd, format="%Y%m%d", errors="raise")
                            entry_day=pd.to_datetime(ed, format="%Y%m%d", errors="raise")
                            entry_gap_days=(entry_day-signal_day).days
                        except Exception:
                            reject("신호일/진입일 날짜 해석 실패"); continue
                        if entry_gap_days < 1 or entry_gap_days > 7:
                            reject("신호일 직후 가격 없음(다음 거래일まで7일 초과)"); continue
                        ep=float(p.loc[j,"_OPEN"]) if pd.notna(p.loc[j,"_OPEN"]) else float("nan")
                        if not (ep>0): reject("진입일 시가 결측/0 이하"); continue
                        if corrected and code in validity and (ed<ld or ed>xd): reject("진입일이 상장기간 밖"); continue
                        if (not allow_overlap) and next_free and ed<=next_free: reject("단일 포지션 중복으로 제외"); continue
                        k=min(j+hold-1,len(p)-1)
                        if corrected and code in validity and p.loc[k,"_DATE"]>xd:
                            eligible=p.index[(p["_DATE"]>=ed)&(p["_DATE"]<=xd)].tolist()
                            if not eligible: reject("폐지일 전 청산 가능 가격 없음"); continue
                            k=eligible[-1]
                        xd_actual=p.loc[k,"_DATE"]; xp=float(p.loc[k,"_CLOSE"])
                        if not (xp>0): reject("청산일 종가 결측/0 이하"); continue
                        net=(xp/ep)*(1-fee)*(1-slip)*(1-fee)*(1-slip)-1
                        # single-position equity path, mark-to-market relative to equity at entry
                        entry_equity=cash
                        for q in range(j,k+1):
                            close=float(p.loc[q,"_CLOSE"])
                            mark=entry_equity*(close/ep)*(1-fee)*(1-slip)
                            peak=max(peak,mark)
                            if peak>0: mdd=min(mdd,(mark/peak-1)*100)
                            equity.append({"날짜":p.loc[q,"_DATE"],"자산":mark})
                        if not allow_overlap: cash=max(0.0,cash*(1+net)); next_free=xd_actual
                        trades.append({"신호종목코드":code,"가격조회코드(정확연결)":price_code,"신호일":sd,"진입일":ed,"청산일":xd_actual,"진입가":ep,"청산가":xp,"순수익률(%)":net*100,"신호컬럼":flag,"시뮬레이션":"신호별 독립 가상거래(중복 허용)" if allow_overlap else "단일 포지션·고정보유기간"})
                    td=pd.DataFrame(trades)
                    if allow_overlap:
                        met={"거래수":len(td),"승률(%)":float((td["순수익률(%)"]>0).mean()*100) if len(td) else float("nan"),"평균 거래수익률(%)":float(td["순수익률(%)"].mean()) if len(td) else float("nan"),"중앙값 거래수익률(%)":float(td["순수익률(%)"].median()) if len(td) else float("nan"),"누적수익률(%)":float("nan"),"MDD(%)":float("nan"),"최종자산(원)":float("nan")}
                    else:
                        met={"거래수":len(td),"승률(%)":float((td["순수익률(%)"]>0).mean()*100) if len(td) else float("nan"),"누적수익률(%)":(cash/cash0-1)*100,"MDD(%)":mdd,"최종자산(원)":cash}
                    audit=pd.DataFrame([{"구분":"보정 후" if corrected else "보정 전", "제외 사유":k, "건수":v} for k,v in sorted(rejected.items())])
                    audit=pd.concat([audit,pd.DataFrame([{"구분":"보정 후" if corrected else "보정 전", "제외 사유":"실제 거래 생성", "건수":len(td)}])],ignore_index=True)
                    return td,met,pd.DataFrame(equity),audit
                bt,bm,be,ba=sim(False); ct,cm,ce,ca=sim(True)
                # Independent per-signal analysis: overlap is allowed only for signal-level diagnostics,
                # not as a portfolio/backtest return. Portfolio metrics are deliberately NaN.
                it,im,ie,ia=sim(False, allow_overlap=True); ict,icm,ice,ica=sim(True, allow_overlap=True)
                reason_audit=pd.concat([ba,ca],ignore_index=True)
                independent_reason_audit=pd.concat([ia,ica],ignore_index=True)
                result=pd.DataFrame([{"구분":"보정 전(단일 포지션 진단)",**bm},{"구분":"기간 확인된 폐지 ETF만 필터(단일 포지션 진단)",**cm},
                                     {"구분":"보정 전(신호별 독립 분석·중복 허용)",**im},{"구분":"기간 확인된 폐지 ETF만 필터(신호별 독립 분석·중복 허용)",**icm}])
                unknown=int((~match_df["상장기간완전확인"]).sum()) if not match_df.empty else 0
                has_signal_rows = len(sig) > 0
                # A code appearing somewhere in a price file is NOT proof that its
                # price exists near the historical signal date. Require meaningful
                # date coverage and at least one observed delisted-list code before
                # even passing this tool's preliminary checks. This is still not a
                # certification that the delisted list contains ETFs only.
                _valid_price_dates = prices["_DATE"].replace("", pd.NA).dropna() if not prices.empty else pd.Series(dtype=str)
                _price_day_count = int(_valid_price_dates.nunique())
                _price_first_date = str(_valid_price_dates.min()) if len(_valid_price_dates) else ""
                _price_last_date = str(_valid_price_dates.max()) if len(_valid_price_dates) else ""
                _delisted_observed_count = int((match_df["관측가격행수"] > 0).sum()) if not match_df.empty else 0
                _requested_start = bt_start.strftime("%Y%m%d")
                _requested_end = bt_end.strftime("%Y%m%d")
                _price_range_covers_request = bool(_price_first_date and _price_last_date and _price_first_date <= _requested_start and _price_last_date >= _requested_end)
                checks_passed=(has_signal_rows and unknown==0 and len(missing_price_codes)==0 and not prices.empty and not match_df.empty and _price_day_count >= 100 and _price_range_covers_request and _delisted_observed_count > 0)
                # This diagnostic never certifies full survivorship correction or
                # reproduces the live app.py strategy engine.
                complete=False
                st.subheader("선택 신호자료 진단")
                st.dataframe(pd.DataFrame([signal_diagnostics]),use_container_width=True,hide_index=True)
                st.subheader("진단 성과 비교"); st.dataframe(result,use_container_width=True,hide_index=True)
                st.subheader("신호별 독립 가상거래 분석")
                st.caption("각 TRUE 신호를 다른 신호와 겹쳐도 독립적으로 평가합니다. 이 표는 신호 품질 진단용이며, 중복 포지션을 허용하므로 포트폴리오 누적수익률·MDD로 해석하지 않습니다.")
                independent_summary=pd.DataFrame([{"구분":"보정 전·신호별 독립 분석",**im},{"구분":"기간 확인된 폐지 ETF만 필터·신호별 독립 분석",**icm}])
                st.dataframe(independent_summary,use_container_width=True,hide_index=True)
                st.download_button("신호별 독립 가상거래 상세 CSV",csv_bytes(it.assign(구분="보정 전" ).pipe(lambda x: pd.concat([x, ict.assign(구분="보정 후")],ignore_index=True,sort=False))),"ETF_RADAR_INDEPENDENT_SIGNAL_TRADES.csv","text/csv",key="dl_independent_trades_v516")
                st.subheader("신호별 제외 사유 진단")
                st.caption("선택 기간의 TRUE 신호를 시뮬레이터가 처음 탈락시킨 사유별 집계입니다. 이는 운영 app.py의 매매엔진 결과가 아니라 이 진단 시뮬레이션의 분기별 집계입니다.")
                st.dataframe(reason_audit,use_container_width=True,hide_index=True)
                st.download_button("신호 제외 사유 CSV",csv_bytes(reason_audit),"ETF_RADAR_SIGNAL_REJECTION_REASONS.csv","text/csv",key="dl_reason_audit_v515")
                if not has_signal_rows:
                    st.error("선택 기간에 TRUE 신호가 0건입니다. 이 상태의 거래수 0·가격 누락 0은 검증 성공이 아닙니다. 신호 플래그 값/컬럼과 기간을 확인하세요.")
                elif checks_passed:
                    st.info("예비 검사 통과: 요청 기간의 가격 날짜 범위와 최소 날짜 수, 신호 코드 가격 보유, 일부 상장폐지 목록 코드 가격 관측 조건을 충족했습니다. 단, 상장폐지 목록이 ETF 전용임을 입증하거나 운영 app.py 엔진을 재현한 것은 아니므로 최종 생존편향 보정 완료로 판정하지 않습니다.")
                else:
                    st.error(f"필수 검사 미통과: 가격 날짜 {_price_day_count:,}일({_price_first_date or '없음'}~{_price_last_date or '없음'}), 요청 기간 전체 포함={_price_range_covers_request}, 상장기간 미확인 {unknown:,}개, 신호 가격 미보유 코드 {len(missing_price_codes):,}개, 상장폐지 목록 중 가격 관측 코드 {_delisted_observed_count:,}개. 코드가 가격 파일에 한 번이라도 있다는 사실만으로 신호일 당시 가격이 존재하는 것은 아닙니다. 이 결과를 생존편향 보정 완료 또는 운영 전략 성과로 사용하지 마세요.")
                if missing_price_codes: st.dataframe(pd.DataFrame({"가격자료 없는 신호코드":missing_price_codes}),use_container_width=True,hide_index=True)
                st.download_button("전후 비교 CSV",csv_bytes(result),"ETF_RADAR_SURVIVORSHIP_COMPARISON.csv","text/csv",key="dl_result_v55")
                st.download_button("보정 전 거래 상세 CSV",csv_bytes(bt),"ETF_RADAR_BASELINE_TRADES_DIAGNOSTIC.csv","text/csv",key="dl_base_v55")
                st.download_button("기간 필터 거래 상세 CSV",csv_bytes(ct),"ETF_RADAR_FILTERED_TRADES_DIAGNOSTIC.csv","text/csv",key="dl_corr_v55")
                audit=match_df if not match_df.empty else pd.DataFrame()
                api_fail=st.session_state.get("api_fail_v56",pd.DataFrame())
                out={"summary.csv":csv_bytes(result),"delisted_match_audit.csv":csv_bytes(audit),"source_status.csv":csv_bytes(pd.DataFrame(status_rows)),"prices_used.csv":csv_bytes(prices),"baseline_trades_diagnostic.csv":csv_bytes(bt),"filtered_trades_diagnostic.csv":csv_bytes(ct),"signal_rejection_reasons.csv":csv_bytes(reason_audit),"independent_signal_trades.csv":csv_bytes(pd.concat([it.assign(구분="보정 전"),ict.assign(구분="보정 후")],ignore_index=True,sort=False)),"independent_signal_summary.csv":csv_bytes(independent_summary),"independent_signal_rejection_reasons.csv":csv_bytes(independent_reason_audit),"missing_signal_price_codes.csv":csv_bytes(pd.DataFrame({"code":missing_price_codes})),"krx_api_failures.csv":csv_bytes(api_fail)}
                result_zip=io.BytesIO()
                with zipfile.ZipFile(result_zip, "w", zipfile.ZIP_DEFLATED) as z:
                    for filename, payload in out.items():
                        z.writestr(filename, payload)
                    z.writestr("README.txt", f"ETF RADAR backfill diagnostic {VERSION}\nThis is a diagnostic simulation, not a rerun of live app.py.\nIndependent signal analysis allows overlapping hypothetical trades; its returns are not portfolio returns.\nEntry price must be within 7 calendar days after the signal date; stale signals are rejected.\n")
                st.download_button("📦 전체 진단 ZIP 다운로드", data=result_zip.getvalue(), file_name="ETF_RADAR_SURVIVORSHIP_DIAGNOSTIC.zip", mime="application/zip", key="dl_zip_v510")
    else: st.error("선택한 신호 자료에서 날짜·코드·신호 플래그 컬럼을 찾지 못했습니다.")
else:
    st.warning("신호 CSV를 인식하지 못했습니다. 이전 진단 ZIP에는 INDEPENDENT_SIGNALS.csv가 없었습니다. 원본 ETF_RADAR_BACKTEST_*.zip을 업로드하면 내부 INDEPENDENT_SIGNALS.csv를 직접 검사합니다.")
    st.caption("공식 신호 파일을 찾았지만 필수 컬럼이 다르면 오류 목록에 파일명과 실제 컬럼이 표시됩니다. 파일명만으로 신호 데이터를 임의 판정하지 않습니다.")

st.header("5. 현재 자료 판정")
all_signal_codes=set()
for _,df in byrole["signals"]:
    c=find_col(df,["etf","ETF코드","종목코드","단축코드","ISU_CD","Code","Ticker","ticker"])
    if c: all_signal_codes.update(df[c].map(norm))
price_codes=set(prices["_CODE"]) if not prices.empty else set()
missing=sorted(x for x in all_signal_codes if x and x not in price_codes)
_summary_valid_dates = prices["_DATE"].replace("", pd.NA).dropna() if not prices.empty else pd.Series(dtype=str)
_summary_price_days = int(_summary_valid_dates.nunique())
_summary_price_first = str(_summary_valid_dates.min()) if len(_summary_valid_dates) else ""
_summary_price_last = str(_summary_valid_dates.max()) if len(_summary_valid_dates) else ""
st.json({"버전":VERSION,"가격행수":int(len(prices)),"가격코드수":int(len(price_codes)),"가격날짜수":_summary_price_days,"가격자료_최초일":_summary_price_first,"가격자료_최종일":_summary_price_last,"인식한 신호파일수":len(signal_options) if 'signal_options' in globals() else len(byrole['signals']),"폐지목록코드수":int(len(match_df)),"폐지목록_가격관측코드수":int((match_df['관측가격행수']>0).sum()) if not match_df.empty else 0,"신호코드중_가격없는코드수":len(missing),"중요한 시간정합성 검사":"진입 가격은 신호일 이후 7일 이내에 존재해야 하며, 수개월/수년 뒤 가격으로 과거 신호를 실행하지 않음","주의":"코드가 가격자료에 한 번이라도 존재한다는 사실만으로 신호일 당시 가격 커버리지가 확인된 것은 아님","판정":"진단 전용 — 전체 과거 가격/상장기간 커버리지 및 운영 전략 엔진 재현은 별도 검증 필요"})
# Hard gate: recognized signals are not enough if historical prices cover only a few days.
# The uploaded diagnostic ZIP contains signal history from 2020-01-02 to 2026-10-08,
# while the supplied daily-price CSV covers only 6 dates in 2026-10-01..2026-10-08.
if not prices.empty:
    _price_days = int(prices["_DATE"].replace("", pd.NA).dropna().nunique())
    _price_first = str(prices["_DATE"].replace("", pd.NA).dropna().min())
    _price_last = str(prices["_DATE"].replace("", pd.NA).dropna().max())
    if _price_days < 100:
        st.error(
            f"과거 가격 커버리지 부족: 가격 날짜 {_price_days}일({_price_first}~{_price_last})만 있습니다. "
            "신호 파일 인식은 성공했지만, 이 가격자료로는 2020년 이후 백테스트나 상장폐지 ETF의 생존편향 보정을 검증할 수 없습니다. "
            "과거 일별 가격 CSV를 추가한 뒤 다시 실행하세요."
        )
    else:
        st.info(f"가격 날짜 커버리지: {_price_days}일({_price_first}~{_price_last}). 전체 신호 기간을 포함하는지는 별도 확인해야 합니다.")

# Always-available diagnostic ZIP: independent of signal detection and simulation.
# This is the key fix for the missing download button reported by the user.
st.header("6. 진단 자료 다운로드")
st.info("아래 ZIP은 신호 파일을 찾지 못했거나 진단 계산을 실행하지 않아도 항상 생성됩니다. 현재 연결된 자료·가격·코드 매칭·API 오류를 담습니다. 6자리/8자리 코드는 공식 연결표가 있을 때만 연결합니다.")
# Build an explicit audit for the known one-day proof case. Keep it separate from
# the delisted-list audit: absence from that input list is not a price-query failure.
targeted_raw = st.session_state.get("targeted_467940_raw_v580", pd.DataFrame())
targeted_meta = st.session_state.get("targeted_467940_meta_v580", pd.DataFrame())
targeted_match = st.session_state.get("targeted_467940_match_v580", pd.DataFrame())
targeted_canonical = canonical_prices(targeted_match, "KRX OpenAPI(467940 단건검증·정확일치)") if isinstance(targeted_match, pd.DataFrame) and not targeted_match.empty else pd.DataFrame()
targeted_price = prices[(prices["_CODE"].eq("467940")) & (prices["_DATE"].eq("20241010"))].copy() if not prices.empty else pd.DataFrame()
delisted_code_col = find_col(delisted_src[1], ["단축코드", "종목코드", "ISU_CD", "표준코드", "종목코드(단축코드)"]) if delisted_src else None
delisted_exact_467940 = bool(delisted_src and delisted_code_col and delisted_src[1][delisted_code_col].map(norm).eq("467940").any())
targeted_audit = pd.DataFrame([{
    "검증코드": "467940",
    "검증일": "20241010",
    "단건_API_응답행수": int(len(targeted_raw)) if isinstance(targeted_raw, pd.DataFrame) else 0,
    "단건_API_정확코드행수": int(len(targeted_match)) if isinstance(targeted_match, pd.DataFrame) else 0,
    "가격파이프라인_정확코드날짜행수": int(len(targeted_price)),
    "상장폐지목록_동일코드존재": delisted_exact_467940,
    "판정": "단건 가격 통합 확인" if len(targeted_price) else ("API 응답은 있으나 정확코드 가격 통합 미확인" if len(targeted_raw) else "단건 API 검증자료 없음"),
    "주의": "상장폐지 목록에 코드가 없다는 사실은 시세 조회 실패를 뜻하지 않음; 과거 코드 연결은 공식 연결표로 별도 검증 필요"
}])

# Recompute source counts at ZIP-generation time so session API/test tables are included.
current_status_rows = []
for role, label in roles.items():
    matches = [(src, df) for r, src, df in items if r == role and isinstance(df, pd.DataFrame)]
    if role == "prices":
        known_sources = {src for src, _df in matches}
        matches += [(src, df) for src, df in byrole["prices"] if src.startswith("KRX OpenAPI(") and src not in known_sources]
    current_status_rows.append({"자료": label, "인식 파일 수": len(matches), "출처 예시": "; ".join(x[0] for x in matches[:5])})

base_diag = {
    "source_status.csv": csv_bytes(pd.DataFrame(current_status_rows)),
    "delisted_match_audit.csv": csv_bytes(match_df if not match_df.empty else pd.DataFrame()),
    "targeted_467940_audit.csv": csv_bytes(targeted_audit),
    "targeted_467940_request_status.csv": csv_bytes(targeted_meta if isinstance(targeted_meta, pd.DataFrame) else pd.DataFrame()),
    "targeted_467940_exact_api_rows.csv": csv_bytes(targeted_match if isinstance(targeted_match, pd.DataFrame) else pd.DataFrame()),
    "targeted_467940_raw_response.csv": csv_bytes(targeted_raw if isinstance(targeted_raw, pd.DataFrame) else pd.DataFrame()),
    "targeted_467940_canonical_rows.csv": csv_bytes(targeted_canonical),
    "targeted_467940_price_integration_rows.csv": csv_bytes(targeted_price),
    "prices_used.csv": csv_bytes(prices if not prices.empty else pd.DataFrame(columns=["_CODE", "_DATE", "_OPEN", "_CLOSE", "_SOURCE"])),
    "krx_api_daily.csv": csv_bytes(api_df if not api_df.empty else pd.DataFrame()),
    "krx_api_failures.csv": csv_bytes(st.session_state.get("api_fail_v55", pd.DataFrame())),
    "missing_signal_price_codes.csv": csv_bytes(pd.DataFrame({"code": missing})),
    "signal_source_diagnostic.csv": csv_bytes(pd.DataFrame([{
        "signal_files_recognized": len(byrole["signals"]),
        "price_files_recognized": len(byrole["prices"]),
        "signals_selected_for_run": int(len(signal_options)) if "signal_options" in globals() else 0,
        "price_rows": int(len(prices)),
        "price_codes": int(len(price_codes)),
        "delisted_codes": int(len(match_df)),
        "delisted_codes_with_prices": int((match_df["관측가격행수"] > 0).sum()) if not match_df.empty else 0,
        "missing_signal_price_codes": int(len(missing)),
        "warning": "An empty missing-code list is not proof of validation if no signal data was recognized or selected."
    }]) ),
}
# Include the loaded input CSV tables so the ZIP remains useful when no backtest was run.
for role_name, items in byrole.items():
    for idx, (source_name, source_df) in enumerate(items, start=1):
        safe_source = re.sub(r"[^A-Za-z0-9_.-]+", "_", Path(source_name).name)[:80] or f"source_{idx}.csv"
        base_diag[f"inputs/{role_name}_{idx}_{safe_source}.csv"] = csv_bytes(source_df)
# Always-available diagnostic ZIP, independent of signal detection and simulation.
st.header("6. 진단 자료 다운로드")
st.info("아래 ZIP은 신호 파일을 찾지 못했거나 진단 계산을 실행하지 않아도 생성됩니다. 현재 연결된 자료·가격·코드 매칭·API 오류를 담습니다.")
diag_buffer = io.BytesIO()
with zipfile.ZipFile(diag_buffer, "w", zipfile.ZIP_DEFLATED) as diag_zip:
    for member_name, member_bytes in base_diag.items():
        diag_zip.writestr(member_name, member_bytes)
    diag_zip.writestr("README.txt", f"ETF RADAR diagnostic package v{VERSION}\n467940 20241010 integrated price rows: {len(targeted_price)}\n467940 present in delisted-list exact-code column: {delisted_exact_467940}\nPrice rows: {len(prices)}\nPrice codes: {len(price_codes)}\nDelisted codes: {len(match_df)}\nDelisted codes with observed prices: {int((match_df['관측가격행수'] > 0).sum()) if not match_df.empty else 0}\nMissing signal price codes: {len(missing)}\nThis diagnostic does not certify complete historical coverage or reproduce the live app.py strategy engine.\n")
st.download_button("📦 진단 ZIP 다운로드 (항상 표시)", data=diag_buffer.getvalue(), file_name="ETF_RADAR_DIAGNOSTIC_ALWAYS_AVAILABLE.zip", mime="application/zip", key="dl_zip_always_v510", type="primary")
st.caption("주의: KRX의 현재 ETF 일별매매정보만으로 과거 상장폐지 ETF의 전체 가격 이력이 확보된다고 보장할 수 없습니다. 이름 또는 부분 코드 매칭은 하지 않습니다.")
