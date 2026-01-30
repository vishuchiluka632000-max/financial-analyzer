import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time
import google.generativeai as genai

# ================= CONFIG =================

st.set_page_config("Stock Analyzer Pro Platform", layout="wide")

ALPHA_KEY = "IDN45N3R2QL85M87"        # market data
GEMINI_API_KEY = "PASTE_YOUR_GEMINI_KEY_HERE"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ================= UI STYLE =================

st.markdown("""
<style>
.card{background:#1f2933;padding:18px;border-radius:14px}
.title{font-size:38px;font-weight:700}
.sub{color:#9ca3af}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>📊 Stock Analyzer Pro</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Real-time markets • Trending movers • AI insights</div>", unsafe_allow_html=True)

# ================= SIDEBAR =================

st.sidebar.header("Market Controls")
symbol = st.sidebar.text_input("Track Stock", "AAPL")

# ================= DATA =================

@st.cache_data(ttl=180)
def fetch_stock(symbol):
    url=f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_KEY}"
    r=requests.get(url).json()
    ts=r.get("Time Series (Daily)",{})

    if not ts:
        return pd.DataFrame()

    df=pd.DataFrame(ts).T.astype(float)
    df.index=pd.to_datetime(df.index)
    df.sort_index(inplace=True)

    df.rename(columns={
        "1. open":"Open",
        "2. high":"High",
        "3. low":"Low",
        "4. close":"Close",
        "5. volume":"Volume"
    }, inplace=True)

    return df.tail(150)

@st.cache_data(ttl=300)
def market_movers():
    symbols=["AAPL","MSFT","NVDA","TSLA","AMZN"]
    rows=[]
    for s in symbols:
        df=fetch_stock(s)
        if len(df)>1:
            ch=((df["Close"].iloc[-1]/df["Close"].iloc[-2])-1)*100
            rows.append([s,round(ch,2)])
    return pd.DataFrame(rows,columns=["Stock","% Change"]).sort_values("% Change",ascending=False)

# ================= AI =================

def ai_insight(question, context):
    try:
        prompt=f"""
You are a stock market expert.

DATA:
{context}

Give clear investing insight.
"""
        r=model.generate_content(
            prompt+"\nQuestion: "+question,
            generation_config={"temperature":0.3,"max_output_tokens":400}
        )
        return r.text
    except:
        return "AI temporarily unavailable — try again shortly."

# ================= TABS =================

tab1,tab2,tab3 = st.tabs(["📈 Market Dashboard","🔥 Trending Stocks","🤖 AI Assistant"])

# ================= DASHBOARD =================

with tab1:
    df=fetch_stock(symbol)

    if df.empty:
        st.warning("Loading market data — wait 1 minute on first run.")
        st.stop()

    latest=df["Close"].iloc[-1]
    prev=df["Close"].iloc[-2]
    change=((latest/prev)-1)*100

    c1,c2,c3=st.columns(3)
    c1.metric("Price",f"{latest:.2f}")
    c2.metric("Daily Change",f"{change:.2f}%")
    c3.metric("Trend","Bullish 📈" if change>0 else "Bearish 📉")

    st.plotly_chart(
        px.line(df,x=df.index,y="Close",template="plotly_dark"),
        use_container_width=True
    )

# ================= TRENDING =================

with tab2:
    movers=market_movers()
    st.subheader("Market Movers Today")
    st.dataframe(movers,use_container_width=True)

# ================= AI =================

with tab3:
    st.subheader("Ask Stock AI")

    q=st.text_input("Ask about risk, future, trend, investment quality")

    if q:
        context=f"""
Stock: {symbol}
Price: {latest:.2f}
Change: {change:.2f}%
"""

        with st.spinner("AI analyzing market..."):
            ans=ai_insight(q,context)

        st.success(ans)

st.caption("Professional trading-style analytics platform (MVP)")
