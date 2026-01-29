import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config("Stock Analyzer Pro", layout="wide")

# ---------------- UI ----------------

st.markdown("""
<style>
.hero{background:linear-gradient(135deg,#141e30,#243b55);
padding:50px;border-radius:18px;color:white;text-align:center}
.box{background:#1f2933;padding:18px;border-radius:15px;margin:10px}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>📊 Stock Analyzer Pro</h1><p>Screener Excel → Smart Analysis</p></div>', unsafe_allow_html=True)

uploaded = st.file_uploader("Upload Screener Excel", type="xlsx")

# ---------------- CLEAN DATA ----------------

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

# ---------------- MAIN ----------------

if uploaded:

    st.success("Excel loaded successfully")

    df = load_clean(uploaded)

    if df is None:
        st.error("Invalid Screener file format")
        st.stop()

    years = df.columns[1:]

    revenue = fetch(df,"sales")
    profit = fetch(df,"net profit")
    equity = fetch(df,"reserves")
    debt = fetch(df,"borrowings")

    if revenue is None or profit is None:
        st.error("Essential financial rows missing in file")
        st.stop()

    equity = equity if equity is not None else revenue*0
    debt = debt if debt is not None else revenue*0

    # ---------------- RATIOS ----------------

    profit_margin = (profit.iloc[-1]/revenue.iloc[-1])*100
    roe = (profit.iloc[-1]/equity.iloc[-1])*100 if equity.iloc[-1]!=0 else 0
    debt_equity = debt.iloc[-1]/equity.iloc[-1] if equity.iloc[-1]!=0 else 0

    growth = ((revenue.iloc[-1]/revenue.iloc[0])**(1/len(revenue))-1)*100

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Profit Margin %",round(profit_margin,2))
    c2.metric("ROE %",round(roe,2))
    c3.metric("Debt/Equity",round(debt_equity,2))
    c4.metric("Revenue Growth %",round(growth,2))

    # ---------------- CHARTS ----------------

    def chart(series,title):
        fig = px.line(x=years, y=series, markers=True,
                      labels={"x":"Year","y":title},
                      template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Performance Trends")

    chart(revenue,"Revenue")
    chart(profit,"Profit")
    chart(debt,"Debt")
    chart(equity,"Equity")

    # ---------------- EDUCATION ----------------

    st.subheader("📚 Ratio Meaning (Beginner Friendly)")

    st.info(f"""
Profit Margin {round(profit_margin,2)}% → Company keeps ₹{round(profit_margin,2)} profit on every ₹100 sales

ROE {round(roe,2)}% → Shareholder money earns {round(roe,2)}% return

Debt/Equity {round(debt_equity,2)} → Debt risk level (below 0.5 is healthy)
""")

    # ---------------- HEALTH ----------------

    st.subheader("🧠 Company Strength")

    good = []
    bad = []

    if profit_margin>15: good.append("High profitability")
    else: bad.append("Low profit margin")

    if roe>20: good.append("Strong return on capital")
    else: bad.append("Weak ROE")

    if debt_equity<0.5: good.append("Low debt risk")
    else: bad.append("High debt")

    if growth>10: good.append("Growing business")
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

    if score>=75:
        st.success("Excellent Long-Term Stock")
    elif score>=50:
        st.warning("Average – Monitor Carefully")
    else:
        st.error("Financially Weak")

    with st.expander("View Clean Financial Table"):
        st.dataframe(df)

st.caption("Inspired by Screener.in | Built with Streamlit")
