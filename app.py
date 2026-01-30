import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import google.generativeai as genai

# ---------------- CONFIG ----------------

st.set_page_config("Stock Analyzer Pro AI", layout="wide")

ALPHA_KEY = "IDN45N3R2QL85M87"   # stock price API
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

# ---------------- STOCK PRICE ----------------

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

# ---------------- TRENDING ----------------

def trending_stocks():
    symbols = ["AAPL","MSFT","NVDA","TSLA","AMZN","META","GOOGL","NFLX"]
    moves = []

    for s in symbols:
        df = g
