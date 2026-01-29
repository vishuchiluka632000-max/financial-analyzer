import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Financial Analyzer Pro", layout="wide")

st.title("📊 Financial Analyzer Pro")
st.write("Upload Screener Excel financial report")

uploaded = st.file_uploader(
    "Upload Excel file from Screener.in",
    type=["xlsx"]
)

def clean_screener_excel(file):
    raw = pd.read_excel(file, header=None)

    # find first row that has year like 2019, 2020 etc
    header_row = None
    for i in range(len(raw)):
        row_text = " ".join(raw.iloc[i].astype(str))
        if "20" in row_text:
            header_row = i
            break

    if header_row is None:
        st.error("Could not detect financial table automatically.")
        return None

    df = pd.read_excel(file, header=header_row)

    # remove junk columns
    df = df.loc[:, ~df.columns.astype(str).str.contains("Unnamed")]

    # drop empty rows
    df = df.dropna(how="all")

    return df

if uploaded:
    st.success("File uploaded successfully")

    df = clean_screener_excel(uploaded)

    if df is not None:
        st.subheader("📄 Clean Financial Data")
        st.dataframe(df)

        # Try auto-plot revenue if exists
        possible_rev = [c for c in df.columns if "Sales" in str(c) or "Revenue" in str(c)]

        if possible_rev:
            rev_col = possible_rev[0]

            chart_df = df.set_index(df.columns[0])[rev_col]

            st.subheader("📈 Revenue Trend")

            fig = px.line(
                chart_df,
                x=chart_df.index,
                y=chart_df.values,
                labels={"x":"Year", "y":"Revenue"},
                markers=True
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Revenue column not detected automatically.")

st.markdown("---")
st.caption("Works with Screener.in Excel exports")
