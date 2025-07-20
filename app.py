import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO
import base64

# Load model and encoder
model = joblib.load("ppd_model_pipeline.pkl")
le = joblib.load("label_encoder.pkl")

st.set_page_config(page_title="PPD Risk Predictor", page_icon="🧠", layout="wide")

# Session state init
if "page" not in st.session_state:
    st.session_state.page = "Home"

# CSS Styling
st.markdown("""
<style>
.stApp {
    background-color: #001f3f;
    color: white;
}
.topnav {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin: 20px 0 40px 0;
}
.topnav button {
    background-color: white;
    color: #001f3f;
    border: none;
    padding: 10px 18px;
    font-size: 16px;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
}
.topnav button.active {
    background-color: deeppink;
    color: white;
}
.topnav button:hover {
    background-color: #ccc;
}
.bottom-image {
    display: flex;
    justify-content: center;
    margin-top: 60px;
}
</style>
""", unsafe_allow_html=True)

# Navigation bar
nav_labels = ["Home", "Take Test", "Result Explanation", "Feedback", "Resources"]
nav_html = "<div class='topnav'>"
for label in nav_labels:
    active_class = "active" if st.session_state.page == label else ""
    nav_html += f"""
        <form action="" method="post">
            <button class="{active_class}" name="nav" type="submit" value="{label}">{label}</button>
        </form>
    """
nav_html += "</div>"
st.markdown(nav_html, unsafe_allow_html=True)

# Set page if button clicked
if "nav" in st.session_state:
    st.session_state.page = st.session_state.nav

# OR (fix for rerun preserving selection)
nav = st.experimental_get_query_params().get("nav")
if nav and nav[0] in nav_labels:
    st.session_state.page = nav[0]

