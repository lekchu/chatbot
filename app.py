import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from fpdf import FPDF
import base64
from datetime import datetime

# Load model and label encoder
model = joblib.load("ppd_model_pipeline.pkl")
le = joblib.load("label_encoder.pkl")

# Page config
st.set_page_config(page_title="PPD Risk Predictor", page_icon="🧠", layout="wide")

# Style
st.markdown(
    """
    <style>
        .main {
            background-color: #f0f8ff;
        }
        h1 {
            color: #003366;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧠 Postpartum Depression (PPD) Risk Predictor")

# Questions
QUESTIONS = [
    "I have been able to laugh and see the funny side of things.",
    "I have looked forward with enjoyment to things.",
    "I have blamed myself unnecessarily when things went wrong.",
    "I have been anxious or worried for no good reason.",
    "I have felt scared or panicky for no very good reason.",
    "Things have been getting on top of me.",
    "I have been so unhappy that I have had difficulty sleeping.",
    "I have felt sad or miserable.",
    "I have been so unhappy that I have been crying.",
    "The thought of harming myself has occurred to me.",
]

OPTIONS = [
    "As much as I always could",
    "Not quite so much now",
    "Definitely not so much now",
    "Not at all",
]

EPDS_SCORES = {
    "As much as I always could": 0,
    "Not quite so much now": 1,
    "Definitely not so much now": 2,
    "Not at all": 3,
}

# App logic
if "responses" not in st.session_state:
    st.session_state.responses = []
if "name" not in st.session_state:
    st.session_state.name = ""
if "age" not in st.session_state:
    st.session_state.age = 25
if "support" not in st.session_state:
    st.session_state.support = "High"

idx = len(st.session_state.responses)

if idx == 0:
    st.subheader("👤 Enter Your Information")
    st.session_state.name = st.text_input("Your Name")
    st.session_state.age = st.slider("Age", 18, 45, 25)
    st.session_state.support = st.selectbox("Family Support Level", ["High", "Medium", "Low"])

if 0 <= idx < len(QUESTIONS):
    st.subheader(f"📝 Question {idx + 1}")
    st.write(QUESTIONS[idx])
    choice = st.radio("Select your response:", OPTIONS, key=f"q{idx}")
    if st.button("Next"):
        st.session_state.responses.append(EPDS_SCORES[choice])
        st.experimental_rerun()
elif idx == len(QUESTIONS):
    st.subheader("✅ Submit Your Responses")
    if st.button("Submit"):
        input_data = {
            "Age": [st.session_state.age],
            "EPDS_Score": [sum(st.session_state.responses)],
            "FamilySupport": [st.session_state.support],
        }
        for i, val in enumerate(st.session_state.responses):
            input_data[f"Q{i+1}"] = [val]

        input_df = pd.DataFrame(input_data)

        # ✅ Manual encoding for 'FamilySupport'
        support_mapping = {"High": 2, "Medium": 1, "Low": 0}
        input_df["FamilySupport"] = input_df["FamilySupport"].map(support_mapping)

        if input_df["FamilySupport"].isnull().any():
            st.error("❌ Error: Could not encode 'FamilySupport'.")
            st.stop()

        # Prediction
        try:
            pred_encoded = model.predict(input_df)[0]
            pred_label = le.inverse_transform([pred_encoded])[0]

            # Show result
            st.success(f"🧾 Hello {st.session_state.name}, your predicted PPD Risk Level is: **{pred_label}**")

            # Graph
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=sum(st.session_state.responses),
                title={'text': "EPDS Score"},
                gauge={'axis': {'range': [0, 30]}}
            ))
            st.plotly_chart(fig)

            # PDF Report
            class PDF(FPDF):
                def header(self):
                    self.set_font("Arial", "B", 14)
                    self.cell(200, 10, "Postpartum Depression Risk Report", ln=True, align="C")

                def footer(self):
                    self.set_y(-15)
                    self.set_font("Arial", "I", 8)
                    self.cell(0, 10, f"Page {self.page_no()}", align="C")

            pdf = PDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, f"Name: {st.session_state.name}", ln=True)
            pdf.cell(200, 10, f"Age: {st.session_state.age}", ln=True)
            pdf.cell(200, 10, f"Family Support: {st.session_state.support}", ln=True)
            pdf.cell(200, 10, f"EPDS Score: {sum(st.session_state.responses)}", ln=True)
            pdf.cell(200, 10, f"Risk Level: {pred_label}", ln=True)
            pdf.cell(200, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

            pdf_output = f"/tmp/{st.session_state.name}_PPD_Report.pdf"
            pdf.output(pdf_output)

            with open(pdf_output, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="{st.session_state.name}_PPD_Report.pdf">📄 Download Report PDF</a>'
                st.markdown(href, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error during prediction: {e}")

elif idx > len(QUESTIONS):
    st.info("✅ Test complete. You may restart or download your report.")
