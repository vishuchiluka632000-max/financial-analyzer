import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Financial Analyzer Pro",
    layout="wide"
)

# ---------- HERO SECTION ----------

st.markdown("""
<style>
.hero {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    padding:60px;
    border-radius:20px;
    color:white;
    text-align:center;
    margin-bottom:40px;
}
.card {
    background:#1e1e1e;
    padding:25px;
    border-radius:16px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>📈 Financial Analyzer Pro</h1>
<p>Upload Screener Excel • Get insights • Track growth • Predict future</p>
</div>
""", unsafe_allow_html=True)

# ---------- FILE UPLOAD ----------

st.subheader("📤 Upload Screener Financial Excel")

uploaded = st.file_uploader(
    "Drop Excel file here",
    type=["xlsx"]
)

def clean_screener_excel(file):
    raw = pd.read_excel(file, header=None)

    header_row = None

    for i in range(len(raw)):
        row = raw.iloc[i].dropna().astype(str)
        text = " ".join(row.values)

        if any(year in text for year in ["2019", "2020", "2021", "2022", "2023", "2024"]):
            header_row = i
            break

    if header_row is None:
        return None

    df = pd.read_excel(file, header=header_row)

    df = df.loc[:, ~df.columns.astype(str).str.contains("Unnamed")]
    df = df.dropna(how="all")

    return df

if uploaded:
    st.success("File uploaded successfully")

    df = clean_screener_excel(uploaded)

    if df is None:
        st.error("Could not auto-detect financial table. Try another Screener file.")
    else:
        col1, col2 = st.columns([1.2, 1])

        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("📄 Clean Financial Data")
            st.dataframe(df, height=400)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("📊 Growth Charts")

            metric_col = df.columns[0]
            numeric_cols = df.columns[1:]

            selected = st.selectbox("Select Metric", numeric_cols)

            chart_data = df[[metric_col, selected]].dropna()
            chart_data.columns = ["Year", "Value"]

            fig = px.line(
                chart_data,
                x="Year",
                y="Value",
                markers=True,
                template="plotly_dark"
            )

            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ---------- FOOTER ----------

st.markdown("---")
st.caption("Built with Streamlit • Financial analytics simplified")
