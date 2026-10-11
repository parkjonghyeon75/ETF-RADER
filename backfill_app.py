"""ETF RADAR survivorship-bias backfill tool.

Separate Streamlit app. Does not modify/import the live app.py at runtime.
- Reads user-supplied KRX data and existing ETF_RADAR backtest ZIP/CSVs.
- Optionally queries the official KRX ETF daily-trading OpenAPI for historical dates.
- Matches identifiers by exact full-string code only; no name/code guessing.
- Excludes signals outside each ETF's observed listing-to-delisting window.
- Recalculates baseline vs date-filtered portfolio metrics from saved signal flags.
- Exports CSVs and a diagnostic ZIP.

Important: API availability/entitlement and historical coverage must be verified at runtime.
No result is labelled complete if price-history coverage is missing.
"""
from __future__ import annotations
import io, json, os, re, time, zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional
import pandas as pd
import streamlit as st

VERSION = "5.1.0"
APP_TITLE = "ETF RADAR — 상장폐지 ETF 시세 복원 및 생존편향 검증"
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption(f"독립 백필 도구 v{VERSION} · app.py의 신호/가격 CSV 형식 연결 · 운영 app.py는 수정하지 않습니다")
st.warning("이 앱은 공식 과거 시세를 실제로 확보한 범위만 사용합니다. 식별자/시세 누락이 있으면 완료로 표시하지 않습니다.")

ROOT = Path(__file__).resolve().parent
SEARCH_DIRS = [ROOT, ROOT / "data"]
ROLE_NAMES = {
    "delisted": "KRX 상장폐지 목록",
    "master": "KRX ETF 기준정보",
    "daily": "KRX 일별 시세",
    "backtest": "기존 ETF RADAR 백테스트 ZIP/신호·가격 CSV",
    "historical": "과거 ETF 기준정보(선택)",
}

def norm(v) -> str:
    if v is None: return ""
    s = str(v).strip().upper()
    if s.lower() in {"nan", "none", "null", "nat"}: return ""
    return s

def norm_date(v) -> str:
    s = str(v or "").strip()
    if not s: return ""
    digits = re.sub(r"\D", "", s)
    if len(digits) == 8: return digits
    d = pd.to_datetime(s, errors="coerce")
    return d.strftime("%Y%m%d") if pd.notna(d) else ""

def read_csv_bytes(raw: bytes, label="CSV") -> pd.DataFrame:
    errors=[]
    for enc in ("utf-8-sig", "cp949", "utf-8"):
        try:
            df = pd.read_csv(io.BytesIO(raw), dtype=str, keep_default_na=False, encoding=enc)
            df.columns = [str(c).strip().replace("\ufeff", "") for c in df.columns]
            for c in df.columns: df[c] = df[c].astype(str).str.strip()
            return df
        except Exception as e: errors.append(f"{enc}: {e}")
    raise ValueError(f"{label} 읽기 실패: " + " / ".join(errors))

def role_for(name: str) -> str:
    n = Path(name).name.lower()
    if "audit" in n or "diagnostic" in n or "검증결과" in n: return ""
    if "histor" in n or "과거기준" in n: return "historical"
    if "delisted" in n or "상장폐지" in n or "폐지목록" in n: return "delisted"
    if "master" in n or "기준정보" in n or "etf_master" in n: return "master"
    if "daily" in n or "raw" in n or "시세" in n or "price" in n or "ohlcv" in n or "price_history" in n: return "daily"
    if "backtest" in n or "signal" in n or "신호" in n or n.endswith(".zip"): return "backtest"
    return ""

def parse_bundle(name: str, raw: bytes):
    out=[]
    if name.lower().endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for member in z.namelist():
                if member.lower().endswith(".csv") and not member.startswith("__MACOSX/"):
                    r=role_for(member) or role_for(name)
                    if r: out.append((r, f"{name}::{member}", read_csv_bytes(z.read(member), member)))
    elif name.lower().endswith(".csv"):
        r=role_for(name)
        if r: out.append((r, name, read_csv_bytes(raw, name)))
    return out

def find_col(df, choices):
    if df is None: return None
    for c in choices:
        if c in df.columns: return c
    lower={str(c).lower():c for c in df.columns}
    for c in choices:
        if c.lower() in lower: return lower[c.lower()]
    return None

def bytes_csv(df): return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

def find_repo_inputs():
    found={}
    for folder in SEARCH_DIRS:
        if not folder.is_dir(): continue
        for p in folder.iterdir():
            if p.is_file() and p.suffix.lower() in {".csv", ".zip"}:
                try:
                    for role, source, df in parse_bundle(p.name, p.read_bytes()):
                        if role and role not in found: found[role]=(source, df)
                except Exception: pass
    return found

st.info("app.py 통합 ZIP의 INDEPENDENT_SIGNALS.csv(date/etf/FINAL_V2)와 INDEPENDENT_PRICE_HISTORY.csv(ETF코드/날짜/Open/Close)를 인식합니다. 상장폐지 ETF의 과거 상장일은 별도 과거 기준정보가 없으면 확인된 것으로 간주하지 않습니다.")
st.header("1. 자료 연결")
st.write("CSV 또는 기존 백테스트 ZIP을 한 번에 여러 개 선택할 수 있습니다. 저장소의 root/data 파일은 자동으로 읽고, 업로드 자료가 같은 종류면 업로드 자료가 우선합니다.")
repo = find_repo_inputs()
up = st.file_uploader("CSV/ZIP 자료 선택", type=["csv","zip"], accept_multiple_files=True, key="all_sources_v51")
inputs={k:v for k,v in repo.items()}
upload_errors=[]
for f in (up or []):
    try:
        for role, source, df in parse_bundle(f.name, f.getvalue()):
            if role: inputs[role]=(source,df)
    except Exception as e: upload_errors.append(f"{f.name}: {e}")
for e in upload_errors: st.error(e)
status=[]
for role,label in ROLE_NAMES.items():
    item=inputs.get(role)
    status.append({"자료":label,"상태":"로드 완료" if item else "없음","출처":item[0] if item else "","행 수":len(item[1]) if item else 0,"열 수":len(item[1].columns) if item else 0})
st.dataframe(pd.DataFrame(status), use_container_width=True, hide_index=True)

# Load frames by semantic role, retaining original text identifiers.
frames={k:(v[1].copy() if k in inputs else None) for k,v in [(k,inputs.get(k)) for k in ROLE_NAMES]}
# Backtest ZIP may contain multiple CSVs with prices and signals; keep all members available for user selection.
backtest_tables=[]
for f in (up or []):
    if f.name.lower().endswith('.zip'):
        try:
            with zipfile.ZipFile(io.BytesIO(f.getvalue())) as z:
                for m in z.namelist():
                    if m.lower().endswith('.csv') and not m.startswith('__MACOSX/'):
                        backtest_tables.append((f.name+'::'+m, read_csv_bytes(z.read(m),m)))
        except Exception: pass
for p in SEARCH_DIRS:
    if p.is_dir():
        for zpath in p.glob('*.zip'):
            try:
                with zipfile.ZipFile(zpath) as z:
                    for m in z.namelist():
                        if m.lower().endswith('.csv') and not m.startswith('__MACOSX/'):
                            table=read_csv_bytes(z.read(m),m)
                            # Only keep plausible signal/price CSVs, not audit outputs.
                            if any(c in table.columns for c in ['FINAL_V2','FINAL','D_미래테마선행가격','Adj Close','TDD_CLSPRC','Close']):
                                backtest_tables.append((str(zpath.name)+'::'+m,table))
            except Exception: pass

st.header("2. KRX 공식 과거 시세 수집")
st.markdown("KRX OpenAPI 키가 Streamlit Cloud **Settings → Secrets**의 `KRX_OPENAPI_KEY`에 설정되어 있으면 공식 ETF 일별 시세 API를 호출할 수 있습니다. API 키를 화면에 직접 입력하거나 채팅에 공유하지 마세요.")
with st.expander("API 수집 설정", expanded=True):
    default_start=date.today()-timedelta(days=730)
    start_date=st.date_input("수집 시작일", value=default_start, key="api_start_v51")
    end_date=st.date_input("수집 종료일", value=date.today(), key="api_end_v51")
    max_days=st.number_input("이번 실행에서 조회할 달력 일수 상한", min_value=1, max_value=3660, value=730, step=30, help="기본값은 전체 설정 기간을 한 번에 조회합니다. KRX API의 호출 제한에 따라 실행 시간이 길거나 일부 날짜가 실패할 수 있습니다.")
    delay=st.slider("요청 간 대기(초)", min_value=0.1, max_value=2.0, value=0.15, step=0.05)
    api_key=""
    try: api_key=str(st.secrets.get("KRX_OPENAPI_KEY", "")).strip()
    except Exception: pass
    if api_key: st.success("KRX_OPENAPI_KEY 설정 확인됨 (키 값은 표시하지 않음)")
    else: st.warning("KRX_OPENAPI_KEY가 없습니다. 저장된 일별 시세와 업로드 자료만 분석할 수 있습니다.")

# API requests only happen after the explicit button is pressed.
if "krx_collected_v51" not in st.session_state: st.session_state.krx_collected_v51 = pd.DataFrame()
if st.button("KRX 공식 ETF 일별 시세 수집 시작", type="primary", disabled=not api_key or start_date>end_date, key="collect_krx_v51"):
    try:
        import requests
        endpoint="https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd"
        all_dates=[]; cur=start_date
        while cur<=end_date and len(all_dates)<int(max_days):
            if cur.weekday() < 5:
                all_dates.append(cur.strftime('%Y%m%d'))
            cur+=timedelta(days=1)
        got=[]; failures=[]; bar=st.progress(0); msg=st.empty()
        sess=requests.Session()
        for i,dd in enumerate(all_dates):
            try:
                resp=sess.get(endpoint, params={"basDd":dd}, headers={"AUTH_KEY":api_key}, timeout=25)
                if resp.status_code==200:
                    payload=resp.json()
                    rows=payload.get("OutBlock_1", []) if isinstance(payload,dict) else []
                    if rows:
                        d=pd.DataFrame(rows).astype(str)
                        d["BAS_DD"]=d.get("BAS_DD", pd.Series([dd]*len(d))).replace("",dd)
                        d["_REQUEST_DATE"]=dd
                        got.append(d)
                else: failures.append({"날짜":dd,"HTTP":resp.status_code,"오류":resp.text[:300]})
            except Exception as e: failures.append({"날짜":dd,"HTTP":"EXCEPTION","오류":str(e)[:300]})
            bar.progress((i+1)/max(1,len(all_dates))); msg.write(f"조회 {i+1}/{len(all_dates)}일 · 응답 행 {sum(len(x) for x in got):,} · 오류 {len(failures)}")
            time.sleep(float(delay))
        new=pd.concat(got,ignore_index=True) if got else pd.DataFrame()
        if not new.empty:
            prior=st.session_state.krx_collected_v51
            st.session_state.krx_collected_v51=pd.concat([prior,new],ignore_index=True).drop_duplicates(subset=[c for c in ['BAS_DD','ISU_CD'] if c in new.columns],keep='last')
        st.session_state.krx_failures_v51=pd.DataFrame(failures)
        st.success(f"API 응답 완료: {len(all_dates)}일 조회, 실제 수신 {len(new):,}행, 실패 {len(failures)}일")
        if failures: st.dataframe(pd.DataFrame(failures).head(100),use_container_width=True,hide_index=True)
    except Exception as e: st.error(f"KRX API 실행 실패: {type(e).__name__}: {e}")
api_daily=st.session_state.krx_collected_v51
if not api_daily.empty:
    st.info(f"이번 세션에 수집된 KRX 시세: {len(api_daily):,}행 / {api_daily['BAS_DD'].nunique() if 'BAS_DD' in api_daily else 0:,}일")

# Normalize all price sources into one schema. This explicitly supports app.py's
# INDEPENDENT_PRICE_HISTORY.csv (ETF코드, 날짜, Open/Close) export as well as KRX API rows.
price_parts=[]
def add_price_source(df, source_label):
    if df is None or df.empty: return
    code_col=find_col(df,['ETF코드','etf','ISU_CD','단축코드','종목코드','Code','Ticker','ticker'])
    date_col=find_col(df,['날짜','date','Date','일자','기준일','BAS_DD','DATE'])
    open_col=find_col(df,['Open','open','시가','TDD_OPNPRC','OPNPRC'])
    close_col=find_col(df,['Close','close','종가','TDD_CLSPRC','CLSPRC'])
    if not code_col or not date_col: return
    tmp=pd.DataFrame()
    tmp['_CODE']=df[code_col].map(norm)
    tmp['_DATE']=df[date_col].map(norm_date)
    tmp['_OPEN']=pd.to_numeric(df[open_col].astype(str).str.replace(',','',regex=False),errors='coerce') if open_col else float('nan')
    tmp['_CLOSE']=pd.to_numeric(df[close_col].astype(str).str.replace(',','',regex=False),errors='coerce') if close_col else float('nan')
    tmp['_SOURCE']=source_label
    tmp=tmp[(tmp['_CODE']!='')&(tmp['_DATE']!='')&(tmp['_OPEN'].gt(0)|tmp['_CLOSE'].gt(0))]
    if not tmp.empty: price_parts.append(tmp)

# Prefer the historical price history exported by the user's own app.py.
for name, table in backtest_tables:
    if find_col(table,['ETF코드','etf','Code','Ticker','ISU_CD','단축코드','종목코드']) and find_col(table,['날짜','date','Date','BAS_DD']) and find_col(table,['Close','close','종가','TDD_CLSPRC']):
        add_price_source(table, name)
if frames.get('daily') is not None: add_price_source(frames['daily'], inputs.get('daily',('KRX daily',None))[0])
if not api_daily.empty: add_price_source(api_daily, 'KRX OpenAPI')
daily=pd.concat(price_parts,ignore_index=True,sort=False) if price_parts else pd.DataFrame()
if not daily.empty:
    # For duplicate code/date rows keep the first source (backtest history first, API fills gaps).
    daily=daily.drop_duplicates(['_CODE','_DATE'],keep='first').sort_values(['_CODE','_DATE']).reset_index(drop=True)

st.header("3. 상장폐지 ETF 식별 및 가격 이력 확인")
delisted=frames.get('delisted'); master=frames.get('master')
match_rows=[]; delisted_code_col=None; delisted_date_col=None; delisted_name_col=None
if delisted is not None and not delisted.empty:
    st.caption("상장폐지 목록의 코드·이름·폐지일 컬럼을 지정합니다. 종목명 추정 매칭은 하지 않습니다.")
    delisted_code_col=st.selectbox("상장폐지 목록 코드 컬럼", options=list(delisted.columns), index=(list(delisted.columns).index(find_col(delisted,['단축코드','종목코드','ISU_CD','표준코드','종목코드(단축코드)'])) if find_col(delisted,['단축코드','종목코드','ISU_CD','표준코드','종목코드(단축코드)']) in delisted.columns else 0), key='delisted_code_col_v51')
    delisted_name_col=st.selectbox("상장폐지 목록 이름 컬럼", options=['(선택 안 함)']+list(delisted.columns), index=(list(delisted.columns).index(find_col(delisted,['종목명','한글종목명','종목약명','ISU_NM']))+1 if find_col(delisted,['종목명','한글종목명','종목약명','ISU_NM']) in delisted.columns else 0), key='delisted_name_col_v51')
    delisted_date_col=st.selectbox("상장폐지일 컬럼", options=['(선택 안 함)']+list(delisted.columns), index=(list(delisted.columns).index(find_col(delisted,['폐지일','상장폐지일','해지일','상장폐지일자']))+1 if find_col(delisted,['폐지일','상장폐지일','해지일','상장폐지일자']) in delisted.columns else 0), key='delisted_date_col_v51')
    master_code=find_col(master,['단축코드','종목코드','ISU_CD']) if master is not None else None
    master_name=find_col(master,['한글종목명','종목명','종목약명']) if master is not None else None
    master_isin=find_col(master,['표준코드','ISIN']) if master is not None else None
    d_codes=delisted[delisted_code_col].map(norm)
    for i,code in enumerate(d_codes):
        if not code: continue
        rawrow=delisted.iloc[i]
        is_short=bool(master is not None and master_code and code in set(master[master_code].map(norm)))
        is_isin=bool(master is not None and master_isin and code in set(master[master_isin].map(norm)))
        price_rows=daily[daily['_CODE'].eq(code)] if not daily.empty and '_CODE' in daily else pd.DataFrame()
        name=rawrow[delisted_name_col] if delisted_name_col!='(선택 안 함)' else ''
        dateval=norm_date(rawrow[delisted_date_col]) if delisted_date_col!='(선택 안 함)' else ''
        match_rows.append({'상장폐지코드':code,'목록종목명':name,'폐지일':dateval,'현행마스터_단축코드정확일치':is_short,'현행마스터_ISIN정확일치':is_isin,'현행마스터일치_주의':'현행 마스터 일치는 과거 ETF 여부를 증명하지 않음' if (is_short or is_isin) else '','관측시세행수':len(price_rows),'최초관측일':price_rows['_DATE'].min() if len(price_rows) else '', '최종관측일':price_rows['_DATE'].max() if len(price_rows) else '', '판정':'가격 관측됨' if len(price_rows) else ('기준정보 코드 일치·시세 없음' if is_short or is_isin else '식별자/시세 미확인')})
    match_df=pd.DataFrame(match_rows).drop_duplicates('상장폐지코드') if match_rows else pd.DataFrame()
    if not match_df.empty:
        st.dataframe(match_df.head(500),use_container_width=True,hide_index=True)
        st.metric('폐지목록 고유 코드',f'{len(match_df):,}')
        st.metric('폐지목록 코드 중 실제 시세 관측',f'{(match_df["관측시세행수"]>0).sum():,}')
else:
    match_df=pd.DataFrame()
    st.error("상장폐지 목록이 없습니다. 업로드하거나 저장소 root/data에 KRX_DELISTED_ALL.csv를 두어야 합니다.")

# Determine date windows only from explicit delisting date; listing date from master if exact code match.
validity={}
if not match_df.empty:
    for _,r in match_df.iterrows():
        code=norm(r['상장폐지코드']); deldate=norm_date(r['폐지일'])
        listdate=''
        # Only a separately supplied historical master may establish a past listing date.
        # The current master is not evidence that a delisted ETF existed in earlier years.
        historical=frames.get('historical')
        if historical is not None:
            mc=find_col(historical,['단축코드','종목코드','ISU_CD','ETF코드'])
            lc=find_col(historical,['상장일','상장일자','LIST_DD','상장일(YYYYMMDD)'])
            if mc and lc:
                mrows=historical[historical[mc].map(norm).eq(code)]
                if len(mrows)==1: listdate=norm_date(mrows.iloc[0][lc])
        validity[code]={'상장일':listdate,'폐지일':deldate}

st.header("4. 기존 백테스트 신호를 이용한 보정 전후 재계산")
# Select signals/price tables from parsed backtest archive or role inputs.
signal_candidates=[]; price_candidates=[]
if frames.get('backtest') is not None: signal_candidates.append((inputs.get('backtest',('업로드 백테스트',None))[0],frames['backtest']))
for name,df in backtest_tables:
    if any(c in df.columns for c in ['FINAL_V2','FINAL','D_미래테마선행가격','signal_date','신호일','date','etf']) and any(c in df.columns for c in ['날짜','date','일자','BAS_DD','signal_date']): signal_candidates.append((name,df))
    if (find_col(df,['Close','종가','TDD_CLSPRC']) and find_col(df,['ETF코드','etf','Code','Ticker','ISU_CD','단축코드','종목코드']) and find_col(df,['date','Date','날짜','일자','BAS_DD'])): price_candidates.append((name,df))
# Deduplicate by source name.
signal_candidates=list({n:(n,d) for n,d in signal_candidates}.values()); price_candidates=list({n:(n,d) for n,d in price_candidates}.values())
if signal_candidates:
    signal_names=[item[0] for item in signal_candidates]
    sig_name=st.selectbox('신호 데이터 선택',signal_names,index=0,key='sig_choice_v51')
    sig_df=next(df for name,df in signal_candidates if name==sig_name)
    sdate=find_col(sig_df,['date','날짜','일자','기준일','BAS_DD','signal_date','신호일'])
    scode=find_col(sig_df,['etf','ETF코드','종목코드','단축코드','ISU_CD','Code','Ticker','ticker'])
    flag_candidates=[c for c in ['FINAL_V2','FINAL','D_미래테마선행가격','D','신호','signal'] if c in sig_df.columns]
    if not flag_candidates: flag_candidates=[c for c in sig_df.columns if re.search(r'FINAL|신호|SIGNAL',c,re.I)]
    if sdate and scode and flag_candidates:
        signal_flag=st.selectbox('사용할 신호 컬럼',flag_candidates,index=0,key='signal_flag_v51')
        start_bt,end_bt=st.columns(2)
        with start_bt: bt_start=st.date_input('백테스트 시작일',value=date(2020,1,1),key='bt_start_v51')
        with end_bt: bt_end=st.date_input('백테스트 종료일',value=date.today(),key='bt_end_v51')
        hold_days=st.number_input('최대 보유 거래일',min_value=1,max_value=250,value=20,key='hold_days_v51')
        fee=st.number_input('편도 수수료(%)',min_value=0.0,max_value=2.0,value=0.10,step=0.05,key='fee_v51')/100
        slip=st.number_input('편도 슬리피지(%)',min_value=0.0,max_value=2.0,value=0.05,step=0.05,key='slip_v51')/100
        cash0=st.number_input('초기자산(원)',min_value=100000,value=10000000,step=1000000,key='cash_v51')
        if st.button('상장기간 필터 적용 및 전후 백테스트 계산',type='primary',key='run_bt_v51'):
            if daily.empty or not {'_CODE','_DATE'}.issubset(daily.columns): st.error('가격 자료에 코드·거래일 컬럼이 없습니다.')
            else:
                prices=daily.copy()
                prices['_OPEN']=pd.to_numeric(prices['_OPEN'],errors='coerce')
                prices['_CLOSE']=pd.to_numeric(prices['_CLOSE'],errors='coerce')
                prices=prices.dropna(subset=['_OPEN','_CLOSE'])
                prices=prices[(prices['_OPEN']>0)&(prices['_CLOSE']>0)].sort_values(['_CODE','_DATE'])
                if prices.empty:
                    st.error('유효한 시가/종가 가격행이 없습니다. 가격 CSV의 Open/Close 또는 KRX 시가/종가 컬럼을 확인하세요.')
                else:
                    sig=sig_df.copy(); sig['_CODE']=sig[scode].map(norm); sig['_DATE']=sig[sdate].map(norm_date); sig['_FLAG']=sig[signal_flag].map(lambda x: norm(x) in {'TRUE','1','Y','YES','T'} or str(x).strip()=='참')
                    sig=sig[(sig['_FLAG'])&(sig['_DATE']>=bt_start.strftime('%Y%m%d'))&(sig['_DATE']<=bt_end.strftime('%Y%m%d'))].copy()
                    # Restrict to code/date pairs with actual price history and apply exact point-in-time validity windows.
                    prices_by={c:g.reset_index(drop=True) for c,g in prices.groupby('_CODE')}
                    def simulate(signal_frame, corrected):
                        rows=[]; cash=float(cash0); next_date=''; equity_points=[]; peak=float(cash0); mdd=0.0
                        for _,sr in signal_frame.sort_values('_DATE').iterrows():
                            code=sr['_CODE']; sd=sr['_DATE']; p=prices_by.get(code)
                            if p is None: continue
                            window=validity.get(code,{}) if corrected else {}
                            ld=window.get('상장일',''); xd=window.get('폐지일','')
                            if corrected and ((ld and sd<ld) or (xd and sd>xd)): continue
                            # Signal is known at close; enter at next available trading day open.
                            ix=p.index[p['_DATE'].gt(sd)].tolist()
                            if not ix: continue
                            j=ix[0]; entry_date=p.loc[j,'_DATE']; entry=float(p.loc[j,'_OPEN'])
                            if entry<=0: continue
                            if corrected and ((ld and entry_date<ld) or (xd and entry_date>xd)): continue
                            if next_date and entry_date<=next_date: continue
                            k=min(j+int(hold_days)-1,len(p)-1); exit_date=p.loc[k,'_DATE']; exitp=float(p.loc[k,'_CLOSE'])
                            if corrected and xd and exit_date>xd:
                                eligible=p[(p['_DATE']>=entry_date)&(p['_DATE']<=xd)]
                                if eligible.empty: continue
                                k=eligible.index[-1]; exit_date=p.loc[k,'_DATE']; exitp=float(p.loc[k,'_CLOSE'])
                            if exitp<=0: continue
                            net=(exitp/entry)*(1-fee-slip)**2-1
                            # Single-position portfolio; mark equity to market at every observed close while a trade is open.
                            path=p.loc[j:k, ['_DATE','_CLOSE']]
                            for _,pr in path.iterrows():
                                mark=cash * max(0.0, (float(pr['_CLOSE'])/entry) * (1-fee-slip)**2)
                                equity_points.append({'날짜':pr['_DATE'],'자산':mark})
                                peak=max(peak,mark)
                                mdd=min(mdd,(mark/peak-1)*100 if peak else 0.0)
                            cash*=max(0.0,1+net); next_date=exit_date
                            rows.append({'종목코드':code,'신호일':sd,'진입일':entry_date,'청산일':exit_date,'진입가':entry,'청산가':exitp,'순수익률(%)':net*100,'청산사유':'상장폐지일/보유기간 종료','전략컬럼':signal_flag})
                        td=pd.DataFrame(rows)
                        if td.empty: return td, {'거래수':0,'승률(%)':float('nan'),'누적수익률(%)':0.0,'MDD(%)':0.0,'최종자산':float(cash0)}
                        return td,{'거래수':len(td),'승률(%)':float((td['순수익률(%)']>0).mean()*100),'누적수익률(%)':(cash/float(cash0)-1)*100,'MDD(%)':float(mdd),'최종자산':float(cash)}
                    base_trades,base_m=simulate(sig,False); corr_trades,corr_m=simulate(sig,True)
                    summary=pd.DataFrame([{'구분':'보정 전',**base_m},{'구분':'상장기간 보정 후',**corr_m}])
                    st.subheader('전후 성과 비교'); st.dataframe(summary,use_container_width=True,hide_index=True)
                    excluded_codes=set(match_df.loc[~match_df['폐지일'].astype(str).eq(''),'상장폐지코드'].map(norm)) if not match_df.empty else set()
                    st.caption(f"주의: 이 계산은 업로드된 신호 플래그와 가격을 사용한 독립 1포지션/고정보유기간 비교입니다. app.py의 전체 신호생성·C/D 체결 엔진을 재실행한 결과는 아닙니다. 상장일/폐지일이 확인되지 않은 코드는 보정할 수 없습니다. 검증된 공식 시세가 충분한 경우에만 생존편향 보정 결과로 해석하세요.")
                    st.download_button('전후 성과 비교 CSV',bytes_csv(summary),'ETF_RADAR_SURVIVORSHIP_COMPARISON.csv','text/csv',key='dl_summary_v51')
                    st.download_button('보정 후 거래상세 CSV',bytes_csv(corr_trades),'ETF_RADAR_CORRECTED_TRADES.csv','text/csv',key='dl_trades_v51')
                    # diagnostic bundle includes match audit, metrics, raw API history and failures
                    files_out={'summary.csv':bytes_csv(summary),'baseline_trades.csv':bytes_csv(base_trades),'corrected_trades.csv':bytes_csv(corr_trades),'delisted_match_audit.csv':bytes_csv(match_df) if not match_df.empty else b'', 'krx_api_daily.csv':bytes_csv(api_daily) if not api_daily.empty else b'', 'source_status.csv':bytes_csv(pd.DataFrame(status))}
                    try: files_out['krx_api_failures.csv']=bytes_csv(st.session_state.get('krx_failures_v51',pd.DataFrame()))
                    except Exception: pass
                    zbuf=io.BytesIO()
                    with zipfile.ZipFile(zbuf,'w',zipfile.ZIP_DEFLATED) as z:
                        for n,b in files_out.items(): z.writestr(n,b)
                        z.writestr('README.txt',f'ETF RADAR backfill v{VERSION}\nKRX API collected rows: {len(api_daily)}\nHistorical prices must be complete before treating survivorship correction as final.\nThis independent fixed-hold simulation uses uploaded signal flags; it is not the full app.py C/D execution engine.\n')
                    st.download_button('전체 진단 ZIP 다운로드',zbuf.getvalue(),'ETF_RADAR_SURVIVORSHIP_BACKFILL.zip','application/zip',key='dl_zip_v51')
    else: st.info('신호 날짜·코드·신호 플래그가 있는 기존 백테스트 CSV/ZIP을 연결하면 전후 재계산이 활성화됩니다.')
else:
    st.warning('기존 백테스트 신호 파일을 찾지 못했습니다. 기존 ETF_RADAR 백테스트 ZIP 또는 신호 CSV를 자료 연결에 추가하세요.')

st.header('5. 현재 자료 기준 판정')
summary_status={
 '버전':VERSION,
 'KRX API 수집 행':int(len(api_daily)),
 '가격 데이터 행':int(len(daily)) if not daily.empty else 0,
 '상장폐지 코드 진단 수':int(len(match_df)) if not match_df.empty else 0,
 '상장폐지 코드 중 시세 관측 수':int((match_df['관측시세행수']>0).sum()) if not match_df.empty else 0,
 '완전 검증 여부':'미검증 — 실제 과거 가격 범위 및 상장/폐지일 완전성 확인 필요'
}
st.json(summary_status)
st.caption('기존 app.py는 import하거나 수정하지 않습니다. app.py가 내보낸 저장 신호·가격과 KRX 자료를 연결하되, 저장 신호를 재생성하는 것은 아닙니다. KRX API 응답, 과거 상장정보, 저장된 신호 데이터가 확보된 범위에 한해서만 계산됩니다.')
