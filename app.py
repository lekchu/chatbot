import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO
import base64
from datetime import datetime

# Load model and label encoder
model = joblib.load("ppd_model_pipeline.pkl")
le = joblib.load("label_encoder.pkl")

# Page configuration
st.set_page_config(page_title="Postpartum Depression Risk Predictor", page_icon="🧠", layout="wide")

# Inject custom CSS to mimic professional business site
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background: #ffffff;
        color: #333333;
    }
    .main-header {
        background: linear-gradient(to right, #007bff, #00c6ff);
        color: white;
        padding: 4rem 2rem;
        border-radius: 0.75rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        font-size: 1.25rem;
        font-weight: 400;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        margin-top: 1rem;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .section {
        padding: 2rem 1rem;
        margin: 0 auto;
        max-width: 1000px;
    }
    .card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

# Navigation
menu = st.sidebar.radio("Navigate", ["🏠 Home", "📝 Take Test", "📊 Result Explanation", "📩 Feedback", "🔗 Resources"])

if menu == "🏠 Home":
    st.markdown("""
        <div class="main-header">
            <h1>Postpartum Depression Risk Predictor</h1>
            <p>Empowering maternal mental health through intelligent assessment</p>
        </div>
    """, unsafe_allow_html=True)

    st.image("https://cdn.pixabay.com/photo/2020/03/27/13/51/mother-4972506_1280.jpg", use_column_width=True)

    st.markdown("""
    <div class="section">
        <div class="card">
            <h3>Why Use This Tool?</h3>
            <p>This AI-powered platform uses the globally validated EPDS (Edinburgh Postnatal Depression Scale) questionnaire to evaluate potential risk levels of postpartum depression. Whether you're a new mother or a healthcare provider, this tool provides immediate insights based on your responses.</p>
        </div>
        <div class="card">
            <h3>How It Works</h3>
            <ol>
                <li>Answer a 10-question assessment</li>
                <li>Get instant risk evaluation</li>
                <li>Download a report or share it with a professional</li>
            </ol>
        </div>
        <div class="card">
            <h3>Confidential & Secure</h3>
            <p>Your answers are not stored anywhere. This is a safe and private tool for awareness and screening.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🧠 Take the Assessment Now"):
        st.session_state.page = "📝 Take Test"
        st.experimental_rerun()

elif menu == "📝 Take Test":
    st.title("📝 Postpartum Depression Questionnaire")
    name = st.text_input("Full Name")
    age = st.slider("Your Age", 18, 45, 25)
    location = st.text_input("Your Location")
    support = st.selectbox("How would you describe your family support?", ["High", "Medium", "Low"])

    questions = [
        ("I have been able to laugh and see the funny side of things.", ["As much as I always could", "Not quite so much now", "Definitely not so much now", "Not at all"]),
        ("I have looked forward with enjoyment to things", ["As much as I ever did", "Rather less than I used to", "Definitely less than I used to", "Hardly at all"]),
        ("I have blamed myself unnecessarily when things went wrong", ["No, never", "Not very often", "Yes, some of the time", "Yes, most of the time"]),
        ("I have been anxious or worried for no good reason", ["No, not at all", "Hardly ever", "Yes, sometimes", "Yes, very often"]),
        ("I have felt scared or panicky for no very good reason", ["No, not at all", "No, not much", "Yes, sometimes", "Yes, quite a lot"]),
        ("Things have been getting on top of me", ["No, I have been coping as well as ever", "No, most of the time I have coped quite well", "Yes, sometimes I haven't been coping as well as usual", "Yes, most of the time I haven't been able to cope at all"]),
        ("I have been so unhappy that I have had difficulty sleeping", ["No, not at all", "Not very often", "Yes, sometimes", "Yes, most of the time"]),
        ("I have felt sad or miserable", ["No, not at all", "Not very often", "Yes, quite often", "Yes, most of the time"]),
        ("I have been so unhappy that I have been crying", ["No, never", "Only occasionally", "Yes, quite often", "Yes, most of the time"]),
        ("The thought of harming myself has occurred to me", ["Never", "Hardly ever", "Sometimes", "Yes, quite often"]),
    ]

    mappings = [3, 2, 1, 0]  # Used to reverse-score answers
    scores = []

    for i, (question, options) in enumerate(questions):
        answer = st.radio(f"Q{i+1}. {question}", options, key=f"q{i}")
        scores.append(mappings[options.index(answer)])

    if st.button("Predict Risk"):
        score_sum = sum(scores)
        data = pd.DataFrame([{  # Name removed from model input
            "Age": age,
            "FamilySupport": support,
            **{f"Q{i+1}": scores[i] for i in range(10)},
            "EPDS_Score": score_sum
        }])

        pred = model.predict(data)[0]
        label = le.inverse_transform([pred])[0]

        st.success(f"{name}, your predicted Postpartum Depression Risk is: {label}")
        st.write(f"**Total EPDS Score:** {score_sum}")

        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pred,
            number={"suffix": " / 3"},
            gauge={
                "axis": {"range": [0, 3]},
                "bar": {"color": "deeppink"},
                "steps": [
                    {"range": [0, 1], "color": "lightgreen"},
                    {"range": [1, 2], "color": "gold"},
                    {"range": [2, 3], "color": "red"}
                ]
            },
            title={"text": "Risk Level"}
        ))
        st.plotly_chart(fig, use_container_width=True)

        # PDF Report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Postpartum Depression Risk Report", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
        pdf.cell(200, 10, txt=f"Location: {location}", ln=True)
        pdf.cell(200, 10, txt=f"Age: {age}", ln=True)
        pdf.cell(200, 10, txt=f"Family Support: {support}", ln=True)
        pdf.cell(200, 10, txt=f"EPDS Score: {score_sum}", ln=True)
        pdf.cell(200, 10, txt=f"Predicted Risk Level: {label}", ln=True)
        pdf.cell(200, 10, txt=f"Generated on: {datetime.now().isoformat(timespec='seconds')}", ln=True)

        buffer = BytesIO()
        pdf.output(buffer)
        b64 = base64.b64encode(buffer.getvalue()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{name}_PPD_Report.pdf">📄 Download Your PDF Report</a>'
        st.markdown(href, unsafe_allow_html=True)

elif menu == "📊 Result Explanation":
    st.title("📊 Understanding Your Risk Score")
    st.markdown("""
    | Risk Level | Interpretation |
    |------------|----------------|
    | Mild (0)   | Normal mood variations |
    | Moderate (1) | Some depressive signs; consider monitoring |
    | Severe (2) | Significant risk; consult professional |
    | Profound (3) | Urgent help required |
    """)

elif menu == "📩 Feedback":
    st.title("📩 We Value Your Feedback")
    user = st.text_input("Your Name")
    fb = st.text_area("Share your thoughts")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")

elif menu == "🔗 Resources":
    st.title("🔗 Mental Health Resources")
    st.markdown("""
    - [National Mental Health Helpline - 1800-599-0019](https://www.mohfw.gov.in)
    - [WHO on Maternal Mental Health](https://www.who.int/news-room/fact-sheets/detail/mental-health-of-women-during-pregnancy-and-after-childbirth)
    - [Postpartum Support International](https://www.postpartum.net/)
    """)
