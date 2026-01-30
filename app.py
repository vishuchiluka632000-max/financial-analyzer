import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time

st.set_page_config("Stock Analyzer Pro", layout="wide")

ALPHA_KEY = "IDN45N3R2QL85M87"

st.markdown("""
<style>
.card{background:#1f2933;padding:18px;border-radius:14px}
.title{font-size:38px;font-weight:700}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>📊 Stock Analyzer Pro</div>", unsafe_allow_html=True)

# -------- AUTO REFRESH --------
if "refresh" not in st.session_state:
    st.session_state.refresh = 0

if st.button("🔄 Refresh Market"):
    st.session_state.refresh += 1

# -------- DATA --------

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
    return df.tail(120)

symbol = st.sidebar.text_input("Track Stock", "AAPL")
df = fetch_stock(symbol)

if df.empty:
    st.warning("Loading market data... wait 1 min if first time.")
    st.stop()

latest = df["4. close"].iloc[-1]
prev = df["4. close"].iloc[-2]
change = ((latest/prev)-1)*100

# -------- DASHBOARD --------

c1,c2,c3 = st.columns(3)

c1.metric("Price", f"{latest:.2f}")
c2.metric("Daily Change", f"{change:.2f}%")
c3.metric("Trend", "Up 📈" if change>0 else "Down 📉")

st.plotly_chart(
    px.line(df, x=df.index, y="4. close", template="plotly_dark"),
    use_container_width=True
)

# -------- MARKET MOVERS --------

st.subheader("🔥 Market Movers")

symbols = ["AAPL","MSFT","NVDA","TSLA"]

rows=[]
