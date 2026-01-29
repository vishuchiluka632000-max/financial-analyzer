import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Stock Analyzer Pro", layout="wide")

# ---------- UI STYLE ----------

st.markdown("""
<style>
.hero{
background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);
padding:50px;border-radius:18px;color:white;text-align:center;margin-bottom:40px;
}
.card{background:#1e1e1e;padding:22px;border-radius:16px;margin-bottom:15px}
.metric{font-size:22px;font-weight:bold}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>📊 Stock Financial Analyzer Pro</h1>
<p>Upload Screener Excel → Analyze like a Pro Investor</p>
</div>
""", unsafe_allow_html=True)

# ---------- UPLOAD ----------

uploaded = st.file_uploader("📤 Upload Screener Excel file", type=["xlsx"])

# ---------- CLEAN SCREENER DATA ----------

def clean_excel(file):
    raw = pd.read_excel(file, header=None)

    header_row = None
    for i in range(len(raw)):
        row = raw.iloc[i].dropna().astype(str)
        text = " ".join(row.values)
        if any(y in text for y in ["2019","2020","2021","2022","2023","2024"]):
            header_row = i
            break

    if header_row is None:
        return None

    df = pd.read_excel(file, header=header_row)
    df = df.loc[:, ~df.columns.astype(str).str.contains("Unnamed")]
    df = df.dropna(how="all")
    return df

# ---------- RATIO ENGINE ----------

def find_row(df, keyword):
    for i in range(len(df)):
        if keyword.lower() in str(df.iloc[i,0]).lower():
            return df.iloc[i,1:]
    return None

def safe(v):
    return v.astype(float)

# ---------- MAIN ----------

if uploaded:
    st.success("File uploaded successfully")

    df = clean_excel(uploaded)

    if df is None:
        st.error("Could not read this Screener file format.")
        st.stop()

    years = df.columns[1:]

    revenue = safe(find_row(df,"sales") or find_row(df,"revenue"))
    profit = safe(find_row(df,"net profit"))
    equity = safe(find_row(df,"reserves") or find_row(df,"equity"))
    debt = safe(find_row(df,"borrowings"))
    assets = safe(find_row(df,"total assets"))

    # ---------- RATIOS ----------

    profit_margin = (profit / revenue * 100).iloc[-1]
    roe = (profit / equity * 100).iloc[-1]
    debt_equity = (debt / equity).iloc[-1]
    growth = ((revenue.iloc[-1] / revenue.iloc[0]) ** (1/len(revenue)) - 1) * 100

    # ---------- DASHBOARD ----------

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Profit Margin %", round(profit_margin,2))
    c2.metric("ROE %", round(roe,2))
    c3.metric("Debt/Equity", round(debt_equity,2))
    c4.metric("Revenue CAGR %", round(growth,2))

    # ---------- CHARTS ----------

    st.subheader("📈 Financial Trends")

    def plot(series, name):
        fig = px.line(x=years, y=series.values, labels={"x":"Year","y":name},
                      template="plotly_dark", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    plot(revenue,"Revenue")
    plot(profit,"Profit")
    plot(debt,"Debt")
    plot(equity,"Equity")

    # ---------- BEGINNER EXPLANATIONS ----------

    st.subheader("📚 Ratio Explanation")

    st.info(f"""
Profit Margin {round(profit_margin,2)}% → Out of ₹100 sales, company keeps ₹{round(profit_margin,2)} as profit.

ROE {round(roe,2)}% → Every ₹100 shareholder money generates ₹{round(roe,2)} profit.

Debt/Equity {round(debt_equity,2)} → Company uses ₹{round(debt_equity,2)} debt per ₹1 own capital.
""")

    # ---------- AUTO SUMMARY ----------

    st.subheader("🧠 Business Health Summary")

    positives = []
    risks = []

    if profit_margin > 15:
        positives.append("Strong profit margins")
    else:
        risks.append("Low margins")

    if roe > 20:
        positives.append("Excellent ROE (efficient business)")
    else:
        risks.append("Weak ROE")

    if debt_equity < 0.5:
        positives.append("Low debt risk")
    else:
        risks.append("High debt burden")

    if growth > 10:
        positives.append("Good revenue growth")
    else:
        risks.append("Slow growth")

    for p in positives:
        st.success("✅ " + p)

    for r in risks:
        st.error("⚠ " + r)

    # ---------- VERDICT ----------

    score = 0
    if profit_margin>15: score+=25
    if roe>20: score+=25
    if debt_equity<0.5: score+=25
    if growth>10: score+=25

    st.subheader("📊 Stock Health Score")

    st.progress(score/100)
    st.metric("Score", f"{score}/100")

    if score>=75:
        st.success("STRONG COMPANY – Long term potential")
    elif score>=50:
        st.warning("AVERAGE – Needs monitoring")
    else:
        st.error("RISKY – Financial weakness")

    # ---------- RAW DATA ----------

    with st.expander("📄 View Clean Financial Table"):
        st.dataframe(df)

# ---------- FOOTER ----------

st.markdown("---")
st.caption("Inspired by Screener • Built with Streamlit")
