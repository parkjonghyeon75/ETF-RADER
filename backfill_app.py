"""ETF RADAR survivorship-bias diagnostic/backfill tool v5.5.0.

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

VERSION = "5.6.0"
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

def read_csv(raw: bytes, label="CSV") -> pd.DataFrame:
    errs=[]
    for enc in ("utf-8-sig", "cp949", "utf-8"):
        try:
            df=pd.read_csv(io.BytesIO(raw), dtype=str, keep_default_na=False, encoding=enc)
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
    # Signal exports can vary in header spelling between app versions.
    d=find_col(df,["date","날짜","일자","기준일","BAS_DD","signal_date","신호일","신호 날짜","거래일"])
    c=find_col(df,["etf","ETF코드","ETF 코드","종목코드","단축코드","ISU_CD","Code","Ticker","ticker","종목코드(단축코드)","ETF Code","ticker_code"])
    f=find_col(df,["FINAL_V2","FINAL","signal","신호","D_미래테마선행가격","최종신호","최종 신호"])
    # Fallback only when a recognizable date + code column and FINAL/SIGNAL header exist.
    if not f:
        f=next((col for col in df.columns if re.search(r"FINAL|SIGNAL|신호", str(col), re.I)), None)
    return bool(d and c and f)

def is_price_table(df):
    c=find_col(df,["ETF코드","etf","ISU_CD","단축코드","종목코드","Code","Ticker","ticker"])
    d=find_col(df,["날짜","date","Date","일자","기준일","BAS_DD","DATE"])
    close=find_col(df,["Close","close","종가","TDD_CLSPRC","CLSPRC"])
    return bool(c and d and close)

def classify_csv(name, df):
    n=Path(name).name.lower()
    # Column signatures take precedence over filenames to avoid treating a
    # price_history CSV as a signal file just because its parent is a ZIP.
    if is_signal_table(df): return "signals"
    if is_price_table(df): return "prices"
    if find_col(df,["폐지일","상장폐지일","해지일","상장폐지일자"]) and find_col(df,["단축코드","종목코드","ISU_CD","표준코드"]): return "delisted"
    if find_col(df,["표준코드","ISIN"]) and find_col(df,["단축코드"]) and find_col(df,["상장일","상장일자","LIST_DD"]): return "master"
    if "histor" in n or "과거기준" in n: return "historical"
    if "delisted" in n or "상장폐지" in n or "폐지목록" in n: return "delisted"
    if "master" in n or "기준정보" in n: return "master"
    if "daily" in n or "raw" in n or "시세" in n: return "prices"
    return ""

def parse_file(name, raw):
    out=[]
    if name.lower().endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for member in z.namelist():
                if member.startswith("__MACOSX/") or not member.lower().endswith(".csv"): continue
                try:
                    df=read_csv(z.read(member), member)
                    role=classify_csv(member,df)
                    if role: out.append((role,f"{name}::{member}",df))
                except Exception as e: out.append(("error",f"{name}::{member}",str(e)))
    elif name.lower().endswith(".csv"):
        df=read_csv(raw,name); role=classify_csv(name,df)
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
st.write("여러 CSV/ZIP을 한 번에 선택할 수 있습니다. ZIP 안에서는 파일명보다 CSV 컬럼 구조를 우선해 신호·가격 파일을 구분합니다.")
repo_items=get_repo_files()
uploads=st.file_uploader("CSV 또는 백테스트 ZIP 선택",type=["csv","zip"],accept_multiple_files=True,key="sources_v56")
items=list(repo_items); errors=[]
for f in uploads or []:
    try:
        parsed=parse_file(f.name,f.getvalue())
        items.extend(parsed)
    except Exception as e: errors.append(f"{f.name}: {e}")
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

# Early, source-only diagnostic download. This button is rendered before API,
# matching, and simulation code, so later failures cannot hide every ZIP option.
early_diag = {
    "source_status.csv": csv_bytes(pd.DataFrame(status_rows)),
}
for role_name, role_items in byrole.items():
    for idx, (source_name, source_df) in enumerate(role_items, start=1):
        safe_source = re.sub(r"[^A-Za-z0-9_.-]+", "_", Path(source_name).name)[:80] or f"source_{idx}.csv"
        early_diag[f"inputs/{role_name}_{idx}_{safe_source}.csv"] = csv_bytes(source_df)
early_buffer = io.BytesIO()
with zipfile.ZipFile(early_buffer, "w", zipfile.ZIP_DEFLATED) as early_zip:
    for member_name, member_bytes in early_diag.items():
        early_zip.writestr(member_name, member_bytes)
    early_zip.writestr("README.txt", f"ETF RADAR source diagnostic v{VERSION}\nContains parsed source tables before API collection and matching.\n")
st.download_button(
    "📦 자료 진단 ZIP 다운로드 (초기 다운로드)",
    data=early_buffer.getvalue(),
    file_name="ETF_RADAR_SOURCE_DIAGNOSTIC.zip",
    mime="application/zip",
    key="dl_zip_early_v56",
)

# ---------- KRX API, optional ----------
st.header("2. KRX 공식 일별 시세 수집(선택)")
st.caption("KRX ETF 일별매매정보는 날짜별 요청이며 응답의 ISU_CD는 종목코드입니다. 과거 상장폐지 종목이 API에서 반환된다는 보장은 없습니다. API 응답 성공과 과거 가격 커버리지는 별개입니다.")
api_key=""
try: api_key=str(st.secrets.get("KRX_OPENAPI_KEY","")).strip()
except Exception: pass
if api_key: st.success("KRX_OPENAPI_KEY 설정 확인됨(키 값 비표시)")
else: st.info("API 키가 없으면 업로드된 가격 자료만 사용합니다.")
with st.expander("API 수집 설정",expanded=False):
    api_start=st.date_input("시작일",value=date(2026,1,1),key="api_start_v55")
    api_end=st.date_input("종료일",value=date.today(),key="api_end_v55")
    max_days=st.number_input("최대 조회 거래일 수",min_value=1,max_value=2000,value=30,step=10,key="api_days_v55")
    delay=st.slider("요청 간 대기(초)",min_value=0.0,max_value=1.0,value=0.0,step=0.05,key="api_delay_v55")
    if st.button("KRX 일별 시세 수집",disabled=(not api_key or api_start>api_end),key="api_collect_v55"):
        import requests
        dates=[]; cur=api_start
        while cur<=api_end and len(dates)<int(max_days):
            if cur.weekday()<5: dates.append(cur.strftime("%Y%m%d"))
            cur+=timedelta(days=1)
        got=[]; fail=[]; bar=st.progress(0); msg=st.empty(); sess=requests.Session()
        for i,dd in enumerate(dates):
            try:
                resp=sess.get("https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd",params={"basDd":dd},headers={"AUTH_KEY":api_key},timeout=15)
                if resp.status_code==200:
                    payload=resp.json(); rows=payload.get("OutBlock_1",[]) if isinstance(payload,dict) else []
                    if rows:
                        d=pd.DataFrame(rows).astype(str); d["BAS_DD"]=d.get("BAS_DD",dd); d["_REQUEST_DATE"]=dd; got.append(d)
                else: fail.append({"날짜":dd,"HTTP":resp.status_code,"오류":resp.text[:250]})
            except Exception as e: fail.append({"날짜":dd,"HTTP":"EXCEPTION","오류":str(e)[:250]})
            bar.progress((i+1)/max(1,len(dates))); msg.write(f"{i+1}/{len(dates)}일 조회 · 수신 {sum(len(x) for x in got):,}행 · 오류 {len(fail)}")
            if delay: time.sleep(float(delay))
        new=pd.concat(got,ignore_index=True) if got else pd.DataFrame()
        st.session_state["api_daily_v55"]=new; st.session_state["api_fail_v55"]=pd.DataFrame(fail)
        st.success(f"조회 완료: 요청 {len(dates)}일, 수신 {len(new):,}행, 오류 {len(fail)}일")
api_df=st.session_state.get("api_daily_v55",pd.DataFrame())
if not api_df.empty: byrole["prices"].append(("KRX OpenAPI(이번 세션)",api_df))

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
    name_guess=find_col(delisted,["종목명","한글종목명","종목약명","ISU_NM"])
    date_opts=["(없음)"]+dc_options; name_opts=["(없음)"]+dc_options
    ddate=st.selectbox("상장폐지일 컬럼",date_opts,index=date_opts.index(date_guess) if date_guess in dc_options else 0,key="ddate_v55")
    dname=st.selectbox("종목명 컬럼(표시용만)",name_opts,index=name_opts.index(name_guess) if name_guess in dc_options else 0,key="dname_v55")
    master=master_src[1] if master_src else None
    hist=hist_src[1] if hist_src else None
    mcode=find_col(master,["단축코드","종목코드","ISU_CD"]) if master is not None else None
    misin=find_col(master,["표준코드","ISIN"]) if master is not None else None
    hcode=find_col(hist,["단축코드","종목코드","ISU_CD","ETF코드"]) if hist is not None else None
    hlist=find_col(hist,["상장일","상장일자","LIST_DD","상장일(YYYYMMDD)"]) if hist is not None else None
    master_codes=set(master[mcode].map(norm)) if master is not None and mcode else set()
    master_isins=set(master[misin].map(norm)) if master is not None and misin else set()
    # ISIN is a separate identifier; never compare a 6-digit short code to an ISIN.
    disin=find_col(delisted,["표준코드","ISIN","ISIN코드","국제증권식별번호"])
    rows=[]
    for _,r in delisted.iterrows():
        code=norm(r[dcode])
        if not code: continue
        deldate=norm_date(r[ddate]) if ddate!="(없음)" else ""
        nm=str(r[dname]) if dname!="(없음)" else ""
        isin=norm(r[disin]) if disin and disin in delisted.columns else ""
        # No partial-code/name matching. Only exact code equality is accepted.
        observed=prices[prices["_CODE"].eq(code)] if not prices.empty else pd.DataFrame()
        listdate=""
        if hist is not None and hcode and hlist:
            hs=hist[hist[hcode].map(norm).eq(code)]
            if len(hs)==1: listdate=norm_date(hs.iloc[0][hlist])
        rows.append({"상장폐지코드":code,"종목명(표시용)":nm,"폐지일":deldate,"과거기준정보_상장일":listdate,"현행마스터_단축코드정확일치":code in master_codes,"상장폐지목록_ISIN":isin,"현행마스터_ISIN정확일치":bool(isin and isin in master_isins),"관측가격행수":len(observed),"최초관측일":observed["_DATE"].min() if len(observed) else "","최종관측일":observed["_DATE"].max() if len(observed) else "","상장기간완전확인":bool(listdate and deldate and listdate<=deldate),"판정":"가격 관측됨" if len(observed) else "가격 미관측"})
    match_df=pd.DataFrame(rows).drop_duplicates("상장폐지코드") if rows else pd.DataFrame()
    for _,r in match_df.iterrows(): validity[r["상장폐지코드"]]={"상장일":r["과거기준정보_상장일"],"폐지일":r["폐지일"]}
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
    chosen=st.selectbox("신호 CSV 선택",labels,key="signal_source_v56")
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
                truth={"TRUE","1","Y","YES","T","참"}
                sig["_FLAG"]=sig[flag].map(lambda x:norm(x) in truth)
                sig=sig[sig["_FLAG"]&(sig["_DATE"]>=bt_start.strftime("%Y%m%d"))&(sig["_DATE"]<=bt_end.strftime("%Y%m%d"))].sort_values("_DATE")
                pmap={c:g.reset_index(drop=True) for c,g in prices.groupby("_CODE")}
                missing_price_codes=sorted(set(sig["_CODE"])-set(pmap))
                def sim(corrected):
                    cash=cash0; peak=cash0; mdd=0.0; next_free=""; trades=[]; equity=[]
                    for _,s in sig.iterrows():
                        code=s["_CODE"]; sd=s["_DATE"]
                        if not code: continue
                        window=validity.get(code,{}) if corrected else {}
                        ld=window.get("상장일",""); xd=window.get("폐지일","")
                        # In corrected run, require verified listing and delisting dates for
                        # delisted-list codes; otherwise do not silently treat as corrected.
                        if corrected and code in validity and (not ld or not xd): continue
                        if corrected and code in validity and (sd<ld or sd>xd): continue
                        p=pmap.get(code)
                        if p is None: continue
                        possible=p.index[p["_DATE"].gt(sd)].tolist()
                        if not possible: continue
                        j=possible[0]; ed=p.loc[j,"_DATE"]; ep=float(p.loc[j,"_OPEN"]) if pd.notna(p.loc[j,"_OPEN"]) else float("nan")
                        if not (ep>0): continue
                        if corrected and code in validity and (ed<ld or ed>xd): continue
                        if next_free and ed<=next_free: continue
                        k=min(j+hold-1,len(p)-1)
                        if corrected and code in validity and p.loc[k,"_DATE"]>xd:
                            eligible=p.index[(p["_DATE"]>=ed)&(p["_DATE"]<=xd)].tolist()
                            if not eligible: continue
                            k=eligible[-1]
                        xd_actual=p.loc[k,"_DATE"]; xp=float(p.loc[k,"_CLOSE"])
                        if not (xp>0): continue
                        net=(xp/ep)*(1-fee)*(1-slip)*(1-fee)*(1-slip)-1
                        # single-position equity path, mark-to-market relative to equity at entry
                        entry_equity=cash
                        for q in range(j,k+1):
                            close=float(p.loc[q,"_CLOSE"])
                            mark=entry_equity*(close/ep)*(1-fee)*(1-slip)
                            peak=max(peak,mark)
                            if peak>0: mdd=min(mdd,(mark/peak-1)*100)
                            equity.append({"날짜":p.loc[q,"_DATE"],"자산":mark})
                        cash=max(0.0,cash*(1+net)); next_free=xd_actual
                        trades.append({"종목코드":code,"신호일":sd,"진입일":ed,"청산일":xd_actual,"진입가":ep,"청산가":xp,"순수익률(%)":net*100,"신호컬럼":flag,"시뮬레이션":"단일 포지션·고정보유기간"})
                    td=pd.DataFrame(trades)
                    met={"거래수":len(td),"승률(%)":float((td["순수익률(%)"]>0).mean()*100) if len(td) else float("nan"),"누적수익률(%)":(cash/cash0-1)*100,"MDD(%)":mdd,"최종자산(원)":cash}
                    return td,met,pd.DataFrame(equity)
                bt,bm,be=sim(False); ct,cm,ce=sim(True)
                result=pd.DataFrame([{"구분":"보정 전(진단 시뮬레이션)",**bm},{"구분":"기간 확인된 폐지 ETF만 필터(진단 시뮬레이션)",**cm}])
                unknown=int((~match_df["상장기간완전확인"]).sum()) if not match_df.empty else 0
                checks_passed=(unknown==0 and len(missing_price_codes)==0 and not prices.empty and not match_df.empty)
                # The app cannot prove exhaustive historical price coverage or reproduce the live engine.
                # Therefore it never labels the overall survivorship correction as complete.
                complete=False
                st.subheader("진단 성과 비교"); st.dataframe(result,use_container_width=True,hide_index=True)
                if checks_passed: st.info("현재 업로드 자료의 코드 연결·상장기간 필수값 검사는 통과했습니다. 다만 전체 과거 시세 커버리지와 운영 app.py 엔진 재현은 검증할 수 없어 최종 보정 완료로 판정하지 않습니다.")
                else: st.error(f"필수 검사 미통과: 과거 상장기간 미확인 {unknown:,}개, 신호 가격 미보유 코드 {len(missing_price_codes):,}개. 이 결과를 생존편향 보정 완료 또는 운영 전략 성과로 사용하지 마세요.")
                if missing_price_codes: st.dataframe(pd.DataFrame({"가격자료 없는 신호코드":missing_price_codes}),use_container_width=True,hide_index=True)
                st.download_button("전후 비교 CSV",csv_bytes(result),"ETF_RADAR_SURVIVORSHIP_COMPARISON.csv","text/csv",key="dl_result_v55")
                st.download_button("보정 전 거래 상세 CSV",csv_bytes(bt),"ETF_RADAR_BASELINE_TRADES_DIAGNOSTIC.csv","text/csv",key="dl_base_v55")
                st.download_button("기간 필터 거래 상세 CSV",csv_bytes(ct),"ETF_RADAR_FILTERED_TRADES_DIAGNOSTIC.csv","text/csv",key="dl_corr_v55")
                audit=match_df if not match_df.empty else pd.DataFrame()
                api_fail=st.session_state.get("api_fail_v55",pd.DataFrame())
                out={"summary.csv":csv_bytes(result),"delisted_match_audit.csv":csv_bytes(audit),"source_status.csv":csv_bytes(pd.DataFrame(status_rows)),"prices_used.csv":csv_bytes(prices),"baseline_trades_diagnostic.csv":csv_bytes(bt),"filtered_trades_diagnostic.csv":csv_bytes(ct),"missing_signal_price_codes.csv":csv_bytes(pd.DataFrame({"code":missing_price_codes})),"krx_api_failures.csv":csv_bytes(api_fail)}
                zbuf=io.BytesIO()
                with zipfile.ZipFile(zbuf,"w",zipfile.ZIP_DEFLATED) as z:
                    for n,b in out.items(): z.writestr(n,b)
                    z.writestr("README.txt",f"ETF RADAR backfill diagnostic {VERSION}\nOverall correction complete: {complete}\nThis is not a rerun of the live app.py strategy engine.\nHistorical listing dates and complete delisted ETF price coverage must be verified separately.\n")
                st.download_button("전체 진단 ZIP 다운로드",zbuf.getvalue(),"ETF_RADAR_SURVIVORSHIP_DIAGNOSTIC.zip","application/zip",key="dl_zip_v55")
    else: st.error("선택한 신호 자료에서 날짜·코드·신호 플래그 컬럼을 찾지 못했습니다.")
else:
    st.warning("신호 CSV를 인식하지 못했습니다. 백테스트 ZIP에 날짜·ETF 코드·FINAL/FINAL_V2 신호 컬럼이 포함되어 있는지 확인하세요.")

st.header("5. 현재 자료 판정")
all_signal_codes=set()
for _,df in byrole["signals"]:
    c=find_col(df,["etf","ETF코드","종목코드","단축코드","ISU_CD","Code","Ticker","ticker"])
    if c: all_signal_codes.update(df[c].map(norm))
price_codes=set(prices["_CODE"]) if not prices.empty else set()
missing=sorted(x for x in all_signal_codes if x and x not in price_codes)
st.json({"버전":VERSION,"가격행수":int(len(prices)),"가격코드수":int(len(price_codes)),"인식한 신호파일수":len(signal_options) if 'signal_options' in globals() else len(byrole['signals']),"폐지목록코드수":int(len(match_df)),"폐지목록_가격관측코드수":int((match_df['관측가격행수']>0).sum()) if not match_df.empty else 0,"신호코드중_가격없는코드수":len(missing),"판정":"진단 전용 — 전체 과거 가격/상장기간 커버리지 및 운영 전략 엔진 재현은 별도 검증 필요"})
# Always-available diagnostic ZIP: independent of signal detection and simulation.
# This is the key fix for the missing download button reported by the user.
st.header("6. 진단 자료 다운로드")
st.info("아래 ZIP은 신호 파일을 찾지 못했거나 진단 계산을 실행하지 않아도 항상 생성됩니다. 현재 연결된 자료·가격·코드 매칭·API 오류를 담습니다.")
base_diag = {
    "source_status.csv": csv_bytes(pd.DataFrame(status_rows)),
    "delisted_match_audit.csv": csv_bytes(match_df if not match_df.empty else pd.DataFrame()),
    "prices_used.csv": csv_bytes(prices if not prices.empty else pd.DataFrame(columns=["_CODE", "_DATE", "_OPEN", "_CLOSE", "_SOURCE"])),
    "krx_api_daily.csv": csv_bytes(api_df if not api_df.empty else pd.DataFrame()),
    "krx_api_failures.csv": csv_bytes(st.session_state.get("api_fail_v55", pd.DataFrame())),
    "missing_signal_price_codes.csv": csv_bytes(pd.DataFrame({"code": missing})),
}
# Include the loaded input CSV tables so the ZIP remains useful when no backtest was run.
for role_name, items in byrole.items():
    for idx, (source_name, source_df) in enumerate(items, start=1):
        safe_source = re.sub(r"[^A-Za-z0-9_.-]+", "_", Path(source_name).name)[:80] or f"source_{idx}.csv"
        base_diag[f"inputs/{role_name}_{idx}_{safe_source}.csv"] = csv_bytes(source_df)
diag_buffer = io.BytesIO()
with zipfile.ZipFile(diag_buffer, "w", zipfile.ZIP_DEFLATED) as diag_zip:
    for member_name, member_bytes in base_diag.items():
        diag_zip.writestr(member_name, member_bytes)
    diag_zip.writestr(
        "README.txt",
        f"ETF RADAR diagnostic package v{VERSION}\n"
        f"Price rows: {len(prices)}\n"
        f"Price codes: {len(price_codes)}\n"
        f"Delisted codes: {len(match_df)}\n"
        f"Delisted codes with observed prices: {int((match_df['관측가격행수'] > 0).sum()) if not match_df.empty else 0}\n"
        f"Missing signal price codes: {len(missing)}\n"
        "This diagnostic package is available even when no backtest calculation has been run.\n"
        "It does not certify complete historical coverage or reproduce the live app.py strategy engine.\n"
    )
st.download_button(
    "📦 진단 ZIP 다운로드 (항상 표시)",
    data=diag_buffer.getvalue(),
    file_name="ETF_RADAR_DIAGNOSTIC_ALWAYS_AVAILABLE.zip",
    mime="application/zip",
    key="dl_zip_always_v56",
    type="primary",
)
st.caption("주의: KRX의 현재 ETF 일별매매정보만으로 과거 상장폐지 ETF의 전체 가격 이력이 확보된다고 보장할 수 없습니다. 이름 또는 부분 코드 매칭은 하지 않습니다.")
