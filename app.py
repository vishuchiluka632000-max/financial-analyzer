GEMINI_API_KEY = "YOUR_KEY"
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import yfinance as yf
import requests
import google.generativeai as genai

# ---------------- CONFIG ----------------

st.set_page_config("Stock Analyzer Pro AI", layout="wide")

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-pro")

# ---------------- UI STYLE ----------------

st.markdown("""
<style>
.hero{background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);
padding:40px;border-radius:20px;color:white;text-align:center}
.card{background:#1f2933;padding:20px;border-radius:15px;margin:8px}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>📊 Stock Analyzer Pro AI</h1>
<p>Live Markets • AI Insights • Pro Financial Dashboard</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------

st.sidebar.title("⚙ Controls")
uploaded = st.sidebar.file_uploader("Upload Screener Excel", type="xlsx")

symbol = st.sidebar.text_input("Track Stock (NSE/BSE/US)", "AAPL")

# ---------------- DATA CLEAN ----------------

def load_clean(file):
    raw = pd.read_excel(file, header=None)
    header=None
    for i in range(len(raw)):
        if raw.iloc[i].astype(str).str.contains("202").any():
            header=i
            break
    if header is None:
        return None

    df=pd.read_excel(file,header=header)
    df=df.loc[:,~df.columns.astype(str).str.contains("Unnamed")]
    df.dropna(how="all",inplace=True)
    return df

def fetch(df,key):
    for i in range(len(df)):
        if key.lower() in str(df.iloc[i,0]).lower():
            return pd.to_numeric(df.iloc[i,1:],errors="coerce")
    return None

# ---------------- STOCK PRICE ----------------

def get_price(symbol):
    data=yf.Ticker(symbol)
    hist=data.history(period="1y")
    return hist

# ---------------- TRENDING ----------------

def trending_stocks():
    tickers=["AAPL","MSFT","GOOGL","AMZN","TSLA","META","NVDA","NFLX","INTC","AMD"]
    movers=[]

    for t in tickers:
        d=yf.Ticker(t).history(period="5d")
        if len(d)>1:
            change=((d["Close"][-1]/d["Close"][0])-1)*100
            movers.append((t,round(change,2)))

    gainers=sorted(movers,key=lambda x:x[1],reverse=True)[:5]
    losers=sorted(movers,key=lambda x:x[1])[:5]

    return gainers,losers

# ---------------- AI ----------------

def ai_answer(question,context):
    prompt=f"""
You are a professional stock market analyst.

DATA:
{context}

Answer clearly, simply, with investment insight.
"""
    r=model.generate_content(prompt+"\nUser: "+question)
    return r.text

# ---------------- MAIN ----------------

tabs = st.tabs(["📈 Dashboard","🔥 Trending","📊 Screener Analysis","🤖 AI Assistant"])

# ================= DASHBOARD =================

with tabs[0]:
    st.subheader("Live Stock Price")

    price=get_price(symbol)

    fig=px.line(price,x=price.index,y="Close",template="plotly_dark")
    st.plotly_chart(fig,use_container_width=True)

    latest=price["Close"][-1]
    change=((price["Close"][-1]/price["Close"][-2])-1)*100

    c1,c2=st.columns(2)
    c1.metric("Current Price",f"{latest:.2f}")
    c2.metric("Daily Change",f"{change:.2f}%")

# ================= TRENDING =================

with tabs[1]:
    gainers,losers=trending_stocks()

    col1,col2=st.columns(2)

    with col1:
        st.subheader("📈 Top Gainers")
        for g in gainers:
            st.success(f"{g[0]}  +{g[1]}%")

    with col2:
        st.subheader("📉 Top Losers")
        for l in losers:
            st.error(f"{l[0]}  {l[1]}%")

# ================= SCREENER =================

with tabs[2]:
    if uploaded:
        df=load_clean(uploaded)

        if df is None:
            st.error("Invalid Screener file")
        else:
            years=df.columns[1:]

            revenue=fetch(df,"sales")
            profit=fetch(df,"net profit")
            equity=fetch(df,"reserves") or revenue*0
            debt=fetch(df,"borrowings") or revenue*0

            pm=profit.iloc[-1]/revenue.iloc[-1]*100
            roe=profit.iloc[-1]/equity.iloc[-1]*100 if equity.iloc[-1]!=0 else 0
            de=debt.iloc[-1]/equity.iloc[-1] if equity.iloc[-1]!=0 else 0
            growth=((revenue.iloc[-1]/revenue.iloc[0])**(1/len(revenue))-1)*100

            c1,c2,c3,c4=st.columns(4)
            c1.metric("Profit Margin %",round(pm,2))
            c2.metric("ROE %",round(roe,2))
            c3.metric("Debt/Equity",round(de,2))
            c4.metric("Revenue Growth %",round(growth,2))

            st.plotly_chart(px.line(x=years,y=revenue,markers=True,template="plotly_dark",
                                    labels={"x":"Year","y":"Revenue"}),use_container_width=True)

            st.plotly_chart(px.line(x=years,y=profit,markers=True,template="plotly_dark",
                                    labels={"x":"Year","y":"Profit"}),use_container_width=True)

            st.dataframe(df)

    else:
        st.info("Upload Screener Excel to analyze")

# ================= AI =================

with tabs[3]:
    st.subheader("🤖 StockGPT – Your AI Market Assistant")

    q=st.text_input("Ask about stock, trend, risk, valuation, future")

    if q:
        context=f"""
Symbol: {symbol}
Latest price: {latest:.2f}
Daily change: {change:.2f}%
"""

        if uploaded:
            context+=f"""
Profit margin: {pm:.2f}%
ROE: {roe:.2f}%
Debt Equity: {de:.2f}
Growth: {growth:.2f}%
"""

        with st.spinner("AI analyzing..."):
            ans=ai_answer(q,context)

        st.success(ans)

st.caption("🚀 Professional Stock Analysis Platform with AI")
