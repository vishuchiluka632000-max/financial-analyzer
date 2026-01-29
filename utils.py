import base64
import streamlit as st

def set_bg(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(
                rgba(0,0,0,0.75),
                rgba(0,0,0,0.75)
            ),
            url("{image_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        div[data-testid="stMetric"],
        .stDataFrame,
        .stPlotlyChart,
        .stMarkdown,
        .stAlert {{
            background: rgba(20,20,20,0.85);
            padding: 15px;
            border-radius: 14px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
