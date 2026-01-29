import streamlit as st

st.title("📊 Multi-Year Financial Analyzer")

st.write("Enter last 5 years financial data (in Crores)")

revenue = [
    st.number_input("Revenue Year 1", value=356),
    st.number_input("Revenue Year 2", value=484),
    st.number_input("Revenue Year 3", value=474),
    st.number_input("Revenue Year 4", value=550),
    st.number_input("Revenue Year 5", value=657)
]

profit = [
    st.number_input("Profit Year 1", value=205),
    st.number_input("Profit Year 2", value=308),
    st.number_input("Profit Year 3", value=305),
    st.number_input("Profit Year 4", value=350),
    st.number_input("Profit Year 5", value=429)
]

cashflow = [
    st.number_input("Cashflow Year 1", value=306),
    st.number_input("Cashflow Year 2", value=762),
    st.number_input("Cashflow Year 3", value=-22),
    st.number_input("Cashflow Year 4", value=298),
    st.number_input("Cashflow Year 5", value=427)
]

current_assets = st.number_input("Current Assets (Latest)", value=1584)
current_liabilities = st.number_input("Current Liabilities (Latest)", value=1007)

liabilities = st.number_input("Total Liabilities (Latest)", value=1060)
equity = st.number_input("Equity (Latest)", value=1136)

if st.button("Analyze Company"):

    rev_growth = ((revenue[-1] - revenue[0]) / revenue[0]) * 100
    profit_growth = ((profit[-1] - profit[0]) / profit[0]) * 100

    profit_margin = profit[-1] / revenue[-1] * 100
    current_ratio = current_assets / current_liabilities
    debt_equity = liabilities / equity
    cash_quality = cashflow[-1] / profit[-1]

    growth_rate = (rev_growth + profit_growth) / 200
    intrinsic_value = cashflow[-1] * (1 + growth_rate) / 0.12

    score = 0
    if rev_growth > 20: score += 2
    if profit_growth > 20: score += 20
    if profit_margin > 15: score += 20
    if current_ratio > 1.3: score += 20
    if debt_equity < 0.5: score += 20

    st.subheader("Results")

    st.write("Revenue Growth:", round(rev_growth,2), "%")
    st.write("Profit Growth:", round(profit_growth,2), "%")
    st.write("Profit Margin:", round(profit_margin,2), "%")
    st.write("Current Ratio:", round(current_ratio,2))
    st.write("Debt/Equity:", round(debt_equity,2))
    st.write("Cash Quality:", round(cash_quality,2))
    st.write("Intrinsic Value:", round(intrinsic_value,2), "Crore")

    st.subheader(f"Score: {score}/100")
