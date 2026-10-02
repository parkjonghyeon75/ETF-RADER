
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="ETF Radar",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.block-container {max-width: 760px; padding: 1rem .8rem 5rem;}
header, footer {visibility:hidden;}
h1 {font-size:1.55rem!important; margin-bottom:.2rem!important;}
h2 {font-size:1.15rem!important;}
h3 {font-size:1rem!important;}
div[data-testid="stMetric"] {
    padding:.55rem .45rem; border:1px solid rgba(128,128,128,.22);
    border-radius:12px;
}
.stButton button {border-radius:12px; min-height:2.8rem;}
div[data-testid="stExpander"] {border-radius:14px;}
.small {font-size:.82rem; opacity:.75;}
.badge {padding:.35rem .6rem; border-radius:999px; font-weight:700;}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=900)
def load_data(symbol, period):
    import yfinance as yf
    df = yf.download(symbol, period=period, interval="1d",
                     auto_adjust=False, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).title() for c in df.columns]
    return df[["Open","High","Low","Close","Volume"]].dropna()

def indicators(df):
    x=df.copy(); c=x.Close
    for n in [20,60,120]: x[f"MA{n}"]=c.rolling(n).mean()
    d=c.diff(); g=d.clip(lower=0); l=-d.clip(upper=0)
    ag=g.ewm(alpha=1/14,adjust=False).mean()
    al=l.ewm(alpha=1/14,adjust=False).mean()
    x["RSI"]=100-(100/(1+ag/al.replace(0,np.nan)))
    e12=c.ewm(span=12,adjust=False).mean()
    e26=c.ewm(span=26,adjust=False).mean()
    x["MACD"]=e12-e26
    x["Signal"]=x.MACD.ewm(span=9,adjust=False).mean()
    mid=c.rolling(20).mean(); sd=c.rolling(20).std()
    x["BBmid"]=mid; x["BBup"]=mid+2*sd; x["BBlow"]=mid-2*sd
    tr=pd.concat([(x.High-x.Low),(x.High-c.shift()).abs(),
                  (x.Low-c.shift()).abs()],axis=1).max(axis=1)
    x["ATR"]=tr.rolling(14).mean()
    x["VMA"]=x.Volume.rolling(20).mean()
    x["VR"]=x.Volume/x.VMA
    return x

def levels(df, lookback=120, window=5, tol=1.2):
    d=df.tail(lookback); h=d.High.values; l=d.Low.values
    hi=[]; lo=[]
    for i in range(window,len(d)-window):
        if h[i]==max(h[i-window:i+window+1]): hi.append(h[i])
        if l[i]==min(l[i-window:i+window+1]): lo.append(l[i])
    def cluster(vals):
        vals=sorted(map(float,vals)); out=[]
        for v in vals:
            if not out or abs(v-np.mean(out[-1]))/np.mean(out[-1])*100>tol:
                out.append([v])
            else: out[-1].append(v)
        return [np.mean(a) for a in out]
    cur=float(d.Close.iloc[-1])
    s=sorted([v for v in cluster(lo) if v<cur],reverse=True)
    r=sorted([v for v in cluster(hi) if v>cur])
    return s[:4],r[:4]

def engine(df,support,resist):
    q=df.iloc[-1]; score=0; flags=[]
    for ok,good,bad in [
        (q.Close>q.MA20,"MA20 위","MA20 아래"),
        (q.MA20>q.MA60,"MA20>MA60","MA20<MA60"),
        (q.MA60>q.MA120,"MA60>MA120","MA60<MA120"),
        (q.MACD>q.Signal,"MACD 상승","MACD 하락")]:
        score += 1 if ok else -1; flags.append(good if ok else bad)
    if 50<=q.RSI<=70: score+=1; flags.append("RSI 정상 상승영역")
    elif q.RSI<50: score-=1; flags.append("RSI 약세")
    else: flags.append("RSI 과열")
    if q.VR>=1.3: score+=1; flags.append("거래량 증가")
    if score>=5: state="상승 강화"
    elif score>=2: state="상승 우위"
    elif score<=-3: state="하락"
    else: state="혼조"
    cur=float(q.Close)
    s1=support[0] if support else np.nan
    r1=resist[0] if resist else np.nan
    if pd.notna(s1):
        pull=f"{s1:,.0f} 부근 지지 확인"
    else: pull="단기 지지선 산출 필요"
    if pd.notna(r1):
        breakout=f"{r1:,.0f} 돌파 + 거래량 확인"
    else: breakout="단기 저항선 산출 필요"
    return score,state,flags,pull,breakout

st.title("📈 ETF Radar")
st.caption("모바일 ETF 기술적 분석 · 지지/저항 · 시나리오")

with st.expander("⚙️ 종목 / 기간 설정", expanded=True):
    symbol=st.text_input("Yahoo Finance 종목코드","069500.KS")
    period=st.selectbox("조회기간",["6mo","1y","2y","5y"],index=1)
    if st.button("🔄 분석 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

try:
    df=indicators(load_data(symbol,period))
    support,resist=levels(df)
    score,state,flags,pull,breakout=engine(df,support,resist)
    q=df.iloc[-1]; cur=float(q.Close)
    prev=float(df.Close.iloc[-2]); change=(cur/prev-1)*100

    st.subheader(symbol)
    m1,m2,m3=st.columns(3)
    m1.metric("현재가",f"{cur:,.0f}",f"{change:+.2f}%")
    m2.metric("RSI",f"{q.RSI:.1f}")
    m3.metric("점수",f"{score:+d}")

    st.markdown(f"### 🟢 현재 상태: **{state}**")
    st.write(" · ".join(flags))

    # Main chart
    with st.expander("📊 가격 / 이동평균 / 지지저항",expanded=True):
        view=df.tail(160)
        fig=go.Figure()
        fig.add_trace(go.Candlestick(x=view.index,open=view.Open,high=view.High,
                                     low=view.Low,close=view.Close,name="가격"))
        for n in [20,60,120]:
            fig.add_trace(go.Scatter(x=view.index,y=view[f"MA{n}"],
                                     mode="lines",name=f"MA{n}"))
        for i,v in enumerate(support[:3],1):
            fig.add_hline(y=v,line_dash="dot",annotation_text=f"S{i} {v:,.0f}")
        for i,v in enumerate(resist[:3],1):
            fig.add_hline(y=v,line_dash="dot",annotation_text=f"R{i} {v:,.0f}")
        fig.update_layout(height=430,margin=dict(l=5,r=5,t=10,b=5),
                          xaxis_rangeslider_visible=False,showlegend=True)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    st.subheader("🎯 자동 시나리오")
    st.info(f"**① 눌림:** {pull}")
    st.info(f"**② 돌파:** {breakout}")
    if support:
        st.warning(f"**③ 지지 이탈:** {support[0]:,.0f} 종가 이탈 여부 확인")

    c1,c2=st.columns(2)
    with c1:
        st.metric("1차 지지",f"{support[0]:,.0f}" if support else "-")
        st.metric("2차 지지",f"{support[1]:,.0f}" if len(support)>1 else "-")
    with c2:
        st.metric("1차 저항",f"{resist[0]:,.0f}" if resist else "-")
        st.metric("2차 저항",f"{resist[1]:,.0f}" if len(resist)>1 else "-")

    with st.expander("📐 RSI / MACD / 볼린저",expanded=False):
        tab1,tab2,tab3=st.tabs(["RSI","MACD","볼린저"])
        with tab1:
            f=go.Figure(go.Scatter(x=df.index,y=df.RSI,mode="lines",name="RSI"))
            f.add_hline(y=70,line_dash="dot"); f.add_hline(y=30,line_dash="dot")
            f.update_layout(height=280,margin=dict(l=5,r=5,t=10,b=5),yaxis_range=[0,100])
            st.plotly_chart(f,use_container_width=True,config={"displayModeBar":False})
        with tab2:
            f=go.Figure()
            f.add_trace(go.Scatter(x=df.index,y=df.MACD,name="MACD"))
            f.add_trace(go.Scatter(x=df.index,y=df.Signal,name="Signal"))
            f.update_layout(height=280,margin=dict(l=5,r=5,t=10,b=5))
            st.plotly_chart(f,use_container_width=True,config={"displayModeBar":False})
        with tab3:
            f=go.Figure()
            for col in ["BBup","BBmid","BBlow","Close"]:
                f.add_trace(go.Scatter(x=df.index,y=df[col],mode="lines",name=col))
            f.update_layout(height=280,margin=dict(l=5,r=5,t=10,b=5))
            st.plotly_chart(f,use_container_width=True,config={"displayModeBar":False})

    with st.expander("📦 거래량",expanded=False):
        f=go.Figure()
        f.add_trace(go.Bar(x=df.index,y=df.Volume,name="Volume"))
        f.add_trace(go.Scatter(x=df.index,y=df.VMA,name="20일 평균"))
        f.update_layout(height=260,margin=dict(l=5,r=5,t=10,b=5))
        st.plotly_chart(f,use_container_width=True,config={"displayModeBar":False})

    st.caption("본 도구는 기술적 지표를 계산해 시나리오를 제시하며 투자 결과를 보장하지 않습니다.")

except Exception as e:
    st.error("데이터를 불러오지 못했습니다.")
    st.code(str(e))
