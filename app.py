import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import google.generativeai as genai

# ---------------- CONFIG ----------------

st.set_page_config("Stock Analyzer Pro AI", layout="wide")

ALPHA_KEY = "IDN45N3R2QL85M87"
GEMINI_API_KEY = "PASTE_YOUR_GEMINI_KEY_HERE"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------- UI ----------------

st.markdown("""
<style>
.hero{
background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);
padding:40px;border-radius:18px;color:white;text-align:center}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>📊 Stock Analyzer Pro AI</h1>
<p>Live Markets • Trending Stocks • Smart AI Insights</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------

st.sidebar.title("Controls")
uploaded = st.sidebar.file_uploader("Upload Screener Excel", type="xlsx")
symbol = st.sidebar.text_input("Track Stock Symbol", "AAPL")

# ---------------- SCREENER CLEAN ----------------

def load_clean(file):
    raw = pd.read_excel(file, header=None)
    header = None
    for i in range(len(raw)):
        if raw.iloc[i].astype(str).str.contains("202").any():
            header = i
            break
    if header is None:
        return None

    df = pd.read_excel(file, header=header)
    df = df.loc[:, ~df.columns.astype(str).str.contains("Unnamed")]
    df.dropna(how="all", inplace=True)
    return df

def fetch(df, key):
    for i in range(len(df)):
        if key.lower() in str(df.iloc[i,0]).lower():
            return pd.to_numeric(df.iloc[i,1:], errors="coerce")
    return None

# ---------------- STOCK DATA (CACHED) ----------------

@st.cache_data(ttl=120)
def get_price(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_KEY}"
    data = requests.get(url).json()

    ts = data.get("Time Series (Daily)", {})
    if not ts:
        return pd.DataFrame()

    df = pd.DataFrame(ts).T.astype(float)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)

    df.rename(columns={
        "1. open":"Open",
        "2. high":"High",
        "3. low":"Low",
        "4. close":"Close",
        "5. volume":"Volume"
    }, inplace=True)

    return df.tail(200)

# ---------------- TRENDING (LIMITED + CACHED) ----------------

@st.cache_data(ttl=300)
def trending_stocks():
    symbols = ["AAPL","MSFT","NVDA","TSLA"]
    moves = []

    for s in symbols:
        df = get_price(s)
        if len(df) > 1:
            ch = ((df["Close"].iloc[-1] / df["Close"].iloc[-2]) - 1) * 100
            moves.append((s, round(ch,2)))

    gainers = sorted(moves, key=lambda x: x[1], reverse=True)
    losers = sorted(moves, key=lambda x: x[1])

    return gainers, losers

# ---------------- AI ----------------

def ai_answer(question, context):
    try:
        prompt = f"""
You are a professional stock analyst.

DATA:
{context}

Explain clearly for investors.
"""
        response = model.generate_content(
            prompt + "\nQuestion: " + question,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 500
            }
        )
        return response.text
    except:
        return "AI is busy right now. Try again in a moment."

# ---------------- TABS ----------------

tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Live Market", "🔥 Trending", "📊 Screener Analysis", "🤖 AI Assistant"]
)

# ================= LIVE MARKET =================

with tab1:
    price_df = get_price(symbol)

    if price_df.empty:
        st.warning("Waiting for market data — refresh after 1 minute.")
    else:
        fig = px.line(price_df, x=price_df.index, y="Close", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        latest = price_df["Close"].iloc[-1]
        change = ((price_df["Close"].iloc[-1] / price_df["Close"].iloc[-2]) - 1) * 100

        c1, c2 = st.columns(2)
        c1.metric("Current Price", f"{latest:.2f}")
        c2.metric("Daily Change %", f"{change:.2f}")

# ================= TRENDING =================

with tab2:
    gainers, losers = trending_stocks()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Gainers")
        for s in gainers:
            st.success(f"{s[0]}  +{s[1]}%")

    with col2:
        st.subheader("Top Losers")
        for s in losers:
            st.error(f"{s[0]}  {s[1]}%")

# ================= SCREENER =================

with tab3:
    if uploaded:
        df = load_clean(uploaded)

        if df is None:
            st.error("Invalid Screener file")
        else:
            years = df.columns[1:]

            revenue = fetch(df,"sales")
            profit = fetch(df,"net profit")
            equity = fetch(df,"reserves") or revenue*0
            debt = fetch(df,"borrowings") or revenue*0

            pm = profit.iloc[-1]/revenue.iloc[-1]*100
            roe = profit.iloc[-1]/equity.iloc[-1]*100 if equity.iloc[-1]!=0 else 0
            de = debt.iloc[-1]/equity.iloc[-1] if equity.iloc[-1]!=0 else 0
            growth = ((revenue.iloc[-1]/revenue.iloc[0])**(1/len(revenue))-1)*100

            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Profit Margin %",round(pm,2))
            c2.metric("ROE %",round(roe,2))
            c3.metric("Debt/Equity",round(de,2))
            c4.metric("Growth %",round(growth,2))

            st.plotly_chart(px.line(x=years,y=revenue,markers=True,template="plotly_dark",
                                    labels={"x":"Year","y":"Revenue"}),use_container_width=True)

            st.plotly_chart(px.line(x=years,y=profit,markers=True,template="plotly_dark",
                                    labels={"x":"Year","y":"Profit"}),use_container_width=True)

            st.dataframe(df)
    else:
        st.info("Upload Screener Excel to analyze")

# ================= AI =================

with tab4:
    q = st.text_input("Ask AI about stock health, trend, risk or future")

    if q:
        context = f"Symbol: {symbol}\n"

        if not price_df.empty:
            context += f"Price: {latest:.2f}, Change: {change:.2f}%\n"

        if uploaded:
            context += f"Profit Margin: {pm:.2f}% | ROE: {roe:.2f}% | Debt Equity: {de:.2f} | Growth: {growth:.2f}%"

        with st.spinner("AI analyzing..."):
            answer = ai_answer(q, context)

        st.success(answer)

st.caption("🚀 Professional AI Stock Analytics Platform")
