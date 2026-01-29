import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Financial Analyzer Pro", layout="wide")

st.title("📊 Financial Analyzer Pro")

st.write("Upload Screener Excel file (financial statements)")

uploaded = st.file_uploader(
    "Upload Excel file",
    type=["xlsx"]
)

def clean_screener_excel(file):
    # Read raw without headers
    raw = pd.read_excel(file, header=None)

    # Find row where years start (contains 20xx)
    header_row = None
    for i in range(len(raw)):
        if raw.iloc[i].astype(str).str.contains("20").any():
            header_row = i
            break

    if header_row is None:
        return None

    df = pd.read_excel(file, header=header_row)

    # Remove ju
