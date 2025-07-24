# app.py
import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO
import base64
import os
import random

# Load model and encoder
model = joblib.load("ppd_model_pipeline.pkl")
le = joblib.load("label_encoder.pkl")

st.set_page_config(page_title="PPD Predictor & MOMLY", layout="wide")

def load_custom_style():
    with open("style/app_style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_style()

# Sidebar navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"

st.session_state.page = st.sidebar.radio(
    "Navigate",
    ["Home", "Take Test", "Result Explanation", "Chat with MOMLY", "Feedback", "Resources"],
    index=["Home", "Take Test", "Result Explanation", "Chat with MOMLY", "Feedback", "Resources"].index(st.session_state.page),
    key="menu"
)

menu = st.session_state.page

# PDF generation helper
def generate_pdf_report(name, place, age, support, score, pred_label):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Postpartum Depression Risk Report", ln=True, align='C')
    pdf.ln(5)

    lines = [
        f"Name: {name}",
        f"Location: {place}",
        f"Age: {age}",
        f"Family Support: {support}",
        f"EPDS Score: {score}",
        f"Predicted Risk Level: {pred_label}",
        "Based on EPDS – Edinburgh Postnatal Depression Scale.",
        "This tool does not replace clinical diagnosis."
    ]

    for line in lines:
        safe_line = line.encode('latin-1', 'ignore').decode('latin-1')
        pdf.cell(200, 10, txt=safe_line, ln=True)

    pdf_bytes = pdf.output(dest='S').encode('latin-1', 'ignore')
    b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    download_link = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{name}_PPD_Report.pdf">\ud83d\udcc4 Download Your PDF Report</a>'
    return download_link

# Add all other pages like Home, Take Test, Result Explanation, Chat with MOMLY, Feedback, Resources
# Use previous code structure you already had for each page section, and replace the PDF section
# inside "Take Test" -> Result display -> with:

# download_link = generate_pdf_report(name, place, age, support, score, pred_label)
# st.markdown(download_link, unsafe_allow_html=True)

# (For brevity, the other logic is unchanged from the previous working version you had — only PDF part updated.)
