import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import openai

# ---------------- CONFIG ----------------

st.set_page_config("Stock Analyzer Pro AI", layout="wide")

NEWS_API_KEY = "YOUR_NEWSAPI_KEY"   # https://newsapi.org
OPENAI_KEY = "YOUR_OPENAI_KEY"     # https://platform.openai.com

openai.api_key = OPENAI_KEY

# ---------------- UI STYLE ----------------

st.markdown("""
<style>
.hero{
background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);
padding:40px;border-radius:18px;color:white;text-align:center}
.card{background:#1f2933;padding:20px;border-radius:15px;margin:10px}
.small{color:#9ca3af}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>📊 Stock Analyzer Pro AI</h1>
<p>Financial Analysis + News + AI Assistant</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------

st.sidebar.title("⚙ Controls")
uploaded = st.sidebar.file_uploader("Upload Screener Excel", type="xlsx")

show_news = st.sidebar.checkbox("Show Latest News", True)
show_ai = st.sidebar.checkbox("Enable AI Assistant", True)

# ---------------- FUNCTIONS ----------------

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

def fetch(df, keyword):
    for i in range(len(df)):
        if keyword.lower() in str(df.iloc[i,0]).lower():
            return pd.to_numeric(df.iloc[i,1:], errors="coerce")
    return None

def chart(series, years, title):
    fig = px.line(x=years, y=series, markers=True,
                  labels={"x":"Year","y":title},
                  template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- NEWS ----------------

def get_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    r = requests.get(url).json()
    return r.get("articles",[])[:5]

# ---------------- AI BOT ----------------

def ask_ai(question, context):
    prompt = f"""
You are a stock analysis assistant.
Financial data:
{context}

User question: {question}
Give simple beginner friendly answer.
"""

    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content

# ---------------- MAIN APP ----------------

if uploaded:

    df = load_clean(uploaded)

    if df is None:
        st.error("Invalid Screener file format")
        st.stop()

    years = df.columns[1:]

    revenue = fetch(df,"sales")
    profit = fetch(df,"net profit")
    equity = fetch(df,"reserves") or revenue*0
    debt = fetch(df,"borrowings") or revenue*0

    if revenue is None or profit is None:
        st.error("Missing Sales or Profit row")
        st.stop()

    # -------- RATIOS --------

    profit_margin = profit.iloc[-1]/revenue.iloc[-1]*100
    roe = profit.iloc[-1]/equity.iloc[-1]*100 if equity.iloc[-1]!=0 else 0
    debt_equity = debt.iloc[-1]/equity.iloc[-1] if equity.iloc[-1]!=0 else 0
    growth = ((revenue.iloc[-1]/revenue.iloc[0])**(1/len(revenue))-1)*100

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Profit Margin %",round(profit_margin,2))
    c2.metric("ROE %",round(roe,2))
    c3.metric("Debt/Equity",round(debt_equity,2))
    c4.metric("Revenue Growth %",round(growth,2))

    # -------- TABS --------

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Financials","🧠 Stock Health","📰 News","🤖 AI Assistant"]
    )

    # ================= TAB 1 =================

    with tab1:
        chart(revenue, years, "Revenue")
        chart(profit, years, "Profit")
        chart(debt, years, "Debt")
        chart(equity, years, "Equity")

        with st.expander("View Clean Financial Table"):
            st.dataframe(df)

    # ================= TAB 2 =================

    with tab2:
        good,bad=[],[]

        if profit_margin>15: good.append("High profitability")
        else: bad.append("Low margins")

        if roe>20: good.append("Strong ROE")
        else: bad.append("Weak ROE")

        if debt_equity<0.5: good.append("Low debt")
        else: bad.append("High debt")

        if growth>10: good.append("Strong growth")
        else: bad.append("Slow growth")

        for g in good: st.success("✅ "+g)
        for b in bad: st.error("⚠ "+b)

        score = sum([
            profit_margin>15,
            roe>20,
            debt_equity<0.5,
            growth>10
        ])*25

        st.progress(score/100)
        st.metric("Stock Score",f"{score}/100")

    # ================= TAB 3 =================

    with tab3:
        if show_news:
            st.subheader("🌍 Latest Global + Indian Market News")

            news = get_news("stock market india global economy")

            for n in news:
                st.markdown(f"### {n['title']}")
                st.write(n['description'])
                st.caption(n['source']['name'])
                st.divider()

    # ================= TAB 4 =================

    with tab4:
        if show_ai:
            st.subheader("🤖 Ask AI About This Stock")

            question = st.text_input("Ask anything (risk, future, health etc)")

            if question:
                context = f"""
Revenue latest: {revenue.iloc[-1]}
Profit latest: {profit.iloc[-1]}
ROE: {roe:.2f}%
Debt Equity: {debt_equity:.2f}
Growth: {growth:.2f}%
"""
                with st.spinner("AI thinking..."):
                    answer = ask_ai(question, context)

                st.success(answer)

st.caption("📌 AI Powered Financial Analysis Dashboard")
