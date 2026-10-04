import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date

st.set_page_config(page_title="ETF RADAR BACKTEST", page_icon="🧪", layout="wide")
POOL={"QQQ":"나스닥100","XLK":"미국기술","SMH":"반도체","SOXX":"반도체","BOTZ":"로봇AI","ARKQ":"자동화로봇","HACK":"사이버보안","ITA":"방산","PAVE":"인프라","URA":"원전우라늄","LIT":"2차전지","XBI":"바이오","INDA":"인도","EWY":"한국","EWJ":"일본","EEM":"신흥국","GLD":"금","TLT":"미국장기채","SPY":"S&P500"}
BENCH="SPY"

@st.cache_data(ttl=3600,show_spinner=False)
def getdata(tickers,start,end):
    x=yf.download(tickers,start=start,end=end,auto_adjust=True,progress=False,threads=True,group_by="ticker")
    out={}
    for t in tickers:
        try:
            d=x[t].copy() if len(tickers)>1 else x.copy()
            if not d.empty: out[t]=d
        except: pass
    return out

def ind(d):
    d=d.copy()
    d["Close"]=pd.to_numeric(d["Close"],errors="coerce")
    d["Volume"]=pd.to_numeric(d.get("Volume",np.nan),errors="coerce")
    d=d.dropna(subset=["Close"])
    d["MA20"]=d.Close.rolling(20).mean(); d["MA60"]=d.Close.rolling(60).mean()
    d["R5"]=d.Close.pct_change(5)*100; d["R20"]=d.Close.pct_change(20)*100
    d["VR"]=d.Volume/d.Volume.rolling(20).mean()
    delta=d.Close.diff(); g=delta.clip(lower=0).rolling(14).mean(); l=(-delta.clip(upper=0)).rolling(14).mean()
    d["RSI"]=100-100/(1+g/l.replace(0,np.nan))
    return d

def signal(r,br):
    c=float(r.Close); m20=float(r.MA20); m60=float(r.MA60)
    r5=float(r.R5); r20=float(r.R20); vr=float(r.VR) if pd.notna(r.VR) else 1; rsi=float(r.RSI) if pd.notna(r.RSI) else 50
    dist=(c/m20-1)*100; rel=r20-br; acc=r5-r20/4
    a=92 if -1<=dist<=3 else 82 if dist<=5 else 65 if dist<8 else 35
    b=92 if 48<=rsi<=62 else 84 if 43<=rsi<68 else 68 if rsi<72 else 35
    f=92 if 1.1<=vr<=1.7 else 82 if 1<=vr<1.1 else 76 if .9<=vr<1 else 58 if vr<2.2 else 38
    q=90 if .5<=acc<=5 else 78 if 0<=acc<.5 else 68 if acc>5 else 52
    z=88 if rel>=6 else 80 if rel>=3 else 70 if rel>=0 else 48
    s=90 if c>=m60 and m20>=m60 else 78 if c>=m60 else 55 if c>=m20 else 35
    score=round(a*.22+b*.18+f*.22+q*.16+z*.14+s*.08)
    return score, score>=72 and vr>=1.05 and rsi<70 and dist<7 and rel>=-1

def run_backtest(start,end,tickers):
    raw=getdata(tickers+[BENCH],(pd.Timestamp(start)-pd.Timedelta(days=100)).strftime("%Y-%m-%d"),(pd.Timestamp(end)+pd.Timedelta(days=2)).strftime("%Y-%m-%d"))
    p={k:ind(v) for k,v in raw.items()}
    b=p.get(BENCH,pd.DataFrame())
    rows=[]
    for t in tickers:
        if t not in p: continue
        d=p[t].join(b[["R20"]].rename(columns={"R20":"BR"}),how="inner")
        for i in range(len(d)):
            if d.index[i]<pd.Timestamp(start) or d.index[i]>pd.Timestamp(end): continue
            r=d.iloc[i]
            if any(pd.isna(r.get(k)) for k in ["MA20","MA60","R5","R20","VR","RSI"]): continue
            score,ok=signal(r,float(r.BR))
            if not ok or i+1>=len(d): continue
            fut=d.iloc[i+1:i+61]; entry=float(r.Close)
            vals={}
            for n in (5,20,60):
                vals[n]=(float(fut.iloc[n-1].Close)/entry-1)*100 if len(fut)>=n else np.nan
                vals[f"dd{n}"]=(float(fut.iloc[:n].Close.min())/entry-1)*100 if len(fut)>=1 else np.nan
            rows.append({"날짜":d.index[i].date(),"ETF":t,"테마":POOL.get(t,t),"선행점수":score,"매수가":entry,**{f"{n}일수익":vals[n] for n in (5,20,60)},**{f"{n}일최저낙폭":vals[f"dd{n}"] for n in (5,20,60)}})
    return pd.DataFrame(rows)

st.title("🧪 ETF RADAR BACKTEST")
st.caption("현재 ETF RADAR 선행신호의 실제 사후 성과를 검증하는 별도 앱")
st.subheader("① 테스트 기간")
c1, c2 = st.columns(2)
s = c1.date_input("시작일", date(2021,1,1), key="bt_start")
e = c2.date_input("종료일", date(2025,12,31), key="bt_end")

st.subheader("② 테스트 ETF")
ts = st.multiselect(
    "ETF를 선택하십시오",
    list(POOL),
    ["QQQ","XLK","SMH","BOTZ","ITA","PAVE","URA","LIT","XBI","INDA","EWY","GLD"],
    format_func=lambda x: f"{x} · {POOL[x]}",
    key="bt_tickers",
)

st.markdown("---")
run_clicked = st.button(
    "🧪  백테스트 실행",
    type="primary",
    use_container_width=True,
    key="run_backtest",
)

if run_clicked:
    if s >= e:
        st.error("시작일은 종료일보다 빨라야 합니다.")
        st.stop()
    if not ts:
        st.error("테스트할 ETF를 하나 이상 선택하십시오.")
        st.stop()

    with st.status("백테스트 진행 중...", expanded=True) as status:
        st.write("① 과거 가격 데이터를 다운로드하고 있습니다.")
        st.write("② ETF별 선행신호를 계산하고 있습니다.")
        st.write("③ 신호 이후 5·20·60일 성과를 계산하고 있습니다.")
        result = run_backtest(s, e, ts)
        st.session_state["bt_result"] = result
        st.session_state["bt_period"] = f"{s} ~ {e}"
        status.update(label="백테스트 완료", state="complete", expanded=False)

r = st.session_state.get("bt_result")

if r is not None:
    if r.empty:
        st.error("조건을 만족한 선행신호가 없습니다.")
        st.stop()

    st.success(
        f"백테스트 완료 · {st.session_state.get('bt_period','')} · "
        f"선행신호 {len(r):,}회"
    )

    st.subheader("③ 핵심 결과")
    cols = st.columns(3)
    for c, n in zip(cols, [5,20,60]):
        x = r[f"{n}일수익"].dropna()
        c.metric(f"{n}일 승률", f"{(x>0).mean()*100:.1f}%")

    st.subheader("④ 핵심 성과")
    out=[]
    for n in [5,20,60]:
        x=r[f"{n}일수익"].dropna()
        dd=r[f"{n}일최저낙폭"].dropna()
        out.append({
            "기간":f"{n}일","신호수":len(x),
            "승률":(x>0).mean()*100,
            "평균수익률":x.mean(),
            "중앙수익률":x.median(),
            "평균최저낙폭":dd.mean(),
            "최고수익":x.max(),
            "최대손실":x.min()
        })

    # 모바일에서는 넓은 표 대신 기간별 핵심 수치를 카드로 표시
    for q in out:
        a,b,c,d = st.columns(4)
        a.metric(f"{q['기간']} 신호", f"{q['신호수']:,}회")
        b.metric("승률", f"{q['승률']:.1f}%")
        c.metric("평균수익", f"{q['평균수익률']:+.2f}%")
        d.metric("평균최저낙폭", f"{q['평균최저낙폭']:.2f}%")
        st.caption(
            f"중앙 {q['중앙수익률']:+.2f}%  ·  "
            f"최고 {q['최고수익']:+.2f}%  ·  "
            f"최대손실 {q['최대손실']:+.2f}%"
        )

    st.subheader("⑤ ETF별 핵심 결과")
    g=r.groupby(["ETF","테마"]).agg(
        신호수=("ETF","size"),
        승률20=("20일수익",lambda x:(x.dropna()>0).mean()*100),
        평균20=("20일수익","mean"),
        평균60=("60일수익","mean"),
        평균최저낙폭60=("60일최저낙폭","mean")
    ).reset_index().sort_values(["평균20","승률20"],ascending=False)

    # ETF별로 한 장씩 보여줘 모바일에서 가로 스크롤이 필요 없게 함
    for _, q in g.iterrows():
        with st.container(border=True):
            st.markdown(f"**{q['ETF']} · {q['테마']}**")
            a,b,c,d = st.columns(4)
            a.metric("신호", f"{int(q['신호수'])}회")
            b.metric("20일 승률", f"{q['승률20']:.1f}%")
            c.metric("20일 평균", f"{q['평균20']:+.2f}%")
            d.metric("60일 평균", f"{q['평균60']:+.2f}%")
            st.caption(f"60일 평균최저낙폭 {q['평균최저낙폭60']:.2f}%")

    with st.expander("⑥ 전체 신호 원본 데이터 보기"):
        st.caption("원본 데이터는 열이 많기 때문에 모바일에서는 가로 스크롤이 발생할 수 있습니다. 핵심 결과는 위 카드에 모두 표시됩니다.")
        mobile_cols=["날짜","ETF","테마","선행점수","매수가","5일수익","20일수익","60일수익"]
        st.dataframe(
            r[mobile_cols],
            use_container_width=True,
            hide_index=True,
            height=420,
            column_config={
                "날짜": st.column_config.TextColumn("날짜", width="small"),
                "ETF": st.column_config.TextColumn("ETF", width="small"),
                "테마": st.column_config.TextColumn("테마", width="medium"),
                "선행점수": st.column_config.NumberColumn("선행점수", width="small", format="%d"),
                "매수가": st.column_config.NumberColumn("매수가", width="small", format="%.2f"),
                "5일수익": st.column_config.NumberColumn("5일", width="small", format="%.2f%%"),
                "20일수익": st.column_config.NumberColumn("20일", width="small", format="%.2f%%"),
                "60일수익": st.column_config.NumberColumn("60일", width="small", format="%.2f%%"),
            },
        )

    st.download_button(
        "📥 전체 신호 결과 CSV 저장",
        r.to_csv(index=False).encode("utf-8-sig"),
        "etf_radar_backtest.csv",
        "text/csv",
        key="download_bt"
    )
else:
    st.info(
        "위에서 기간과 ETF를 선택한 뒤 **🧪 백테스트 실행**을 누르십시오. "
        "실행 후 결과는 화면에 계속 남습니다."
    )
