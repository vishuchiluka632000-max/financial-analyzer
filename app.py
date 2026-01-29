import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Financial Analyzer Pro", layout="wide")

st.image(
    "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c",
    use_column_width=True
)

st.title("📊 Financial Analyzer Pro")

left, right = st.columns(2)

with left:
    st.subheader("Upload Financial Data")
    uploaded = st.file_uploader(
        "Upload Excel, CSV, PDF or Screenshot",
        type=["xlsx", "csv", "pdf", "png", "jpg"]
    )

with right:
    st.subheader("Manual Input (optional)")
    revenue = st.number_input("Latest Revenue", 0.0)
    profit = st.number_input("Latest Profit", 0.0)
    cashflow = st.number_input("Latest Cashflow", 0.0)

if uploaded:
    st.success("File uploaded successfully!")

    if uploaded.name.endswith(("xlsx","csv")):
        df = pd.read_excel(uploaded) if uploaded.name.endswith("xlsx") else pd.read_csv(uploaded)
        st.dataframe(df)

    if uploaded.name.endswith(("png","jpg")):
        img = Image.open(uploaded)
        st.image(img, caption="Uploaded Screenshot")

st.button("Analyze Company")
