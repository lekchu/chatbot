import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
from fpdf import FPDF
import os
import random

# ========== CONFIGURATION ==========
st.set_page_config(page_title="MOMLY - Postpartum Risk Predictor", layout="centered")
st.markdown("<style>body { background-color: #FAF8F6; color: #222831; font-family: 'Quicksand', sans-serif; }</style>", unsafe_allow_html=True)

# ========== STYLE & DIRECTORIES ==========
STYLE_PATH = "style/app_style.css"
os.makedirs("style", exist_ok=True)
os.makedirs("pdfs", exist_ok=True)

# ========== SAMPLE QUESTIONS ==========
questions = [
    "1. I have been able to laugh and see the funny side of things.",
    "2. I have looked forward with enjoyment to things.",
    "3. I have blamed myself unnecessarily when things went wrong.",
    "4. I have felt anxious or worried for no good reason.",
    "5. I have felt scared or panicky for no very good reason.",
    "6. Things have been getting on top of me.",
    "7. I have been so unhappy that I have had difficulty sleeping.",
    "8. I have felt sad or miserable.",
    "9. I have been so unhappy that I have been crying.",
    "10. The thought of harming myself has occurred to me."
]

options = ["Not at all", "Rarely", "Sometimes", "Often"]
option_scores = {"Not at all": 0, "Rarely": 1, "Sometimes": 2, "Often": 3}

# ========== MODEL SIMULATOR ==========
def fake_model_predict(score):
    if score <= 7:
        return "Low", "#57D183", "You're doing well emotionally, but stay mindful 🌱"
    elif score <= 13:
        return "Moderate", "#FFC75F", "Mild signs of stress. Try relaxing activities 💆‍♀️"
    else:
        return "High", "#FF6B6B", "You may be at risk. Please talk to someone you trust 💗"

# ========== PDF GENERATOR ==========
def generate_pdf(score, level, tip):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="MOMLY - Emotional Risk Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Total Score: {score}\nRisk Level: {level}\n\nTips:\n{tip}")
    
    filename = f"pdfs/momly_report_{random.randint(1000,9999)}.pdf"
    pdf.output(filename)
    return filename

def get_pdf_download_link(filepath):
    with open(filepath, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode()
        return f'<a href="data:application/pdf;base64,{base64_pdf}" download="MOMLY_Risk_Report.pdf">📥 Download Your Report (PDF)</a>'

# ========== MAIN UI ==========
st.title("🤱 MOMLY - Postpartum Risk Prediction")
st.write("Answer the following questions honestly. We'll assess your emotional state and give personalized tips to help you.")

# --- Form Start ---
with st.form("ppd_form"):
    responses = []
    for q in questions:
        choice = st.radio(q, options, key=q)
        responses.append(option_scores[choice])
    submitted = st.form_submit_button("Check My Emotional Risk 💖")

# ========== PREDICTION ==========
if submitted:
    total_score = sum(responses)
    risk_level, color, tip = fake_model_predict(total_score)

    # --- Gauge Chart ---
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=total_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Your Risk Level: {risk_level}", 'font': {'size': 20}},
        gauge={
            'axis': {'range': [0, 30]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 7], 'color': "#D3F6DB"},
                {'range': [8, 13], 'color': "#FFF4CC"},
                {'range': [14, 30], 'color': "#FFD6D6"}
            ],
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

    # --- Tips ---
    st.subheader("💡 Personalized Suggestions")
    st.info(tip)

    # --- PDF Download ---
    report_path = generate_pdf(total_score, risk_level, tip)
    st.markdown(get_pdf_download_link(report_path), unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("---")
st.markdown(
    "<center><sub>Built with love by MOMLY 💗 — Your mental health companion</sub></center>",
    unsafe_allow_html=True
)
