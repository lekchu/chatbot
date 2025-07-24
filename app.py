import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO
import base64
import os

# --- Load model and label encoder ---
model = joblib.load("ppd_model_pipeline.pkl")
le = joblib.load("label_encoder.pkl")

# --- Page Configuration ---
st.set_page_config(page_title="MOMLY - Postpartum Risk Predictor", page_icon="👩‍🍼", layout="wide")

# --- Light Theme Styling ---
st.markdown("""
    <style>
        body, .stApp {
            background-color: #f9f9f9;
            color: #222222;
            font-family: 'Segoe UI', sans-serif;
        }
        h1, h2, h3, h4 {
            color: #c94f7c;
        }
        .stButton > button {
            background-color: #c94f7c;
            color: white;
            border-radius: 10px;
        }
        .stTextInput, .stSelectbox, .stSlider, .stRadio > div {
            background-color: white;
            color: #222222;
            border-radius: 8px;
            padding: 5px;
        }
        .risk-tip {
            background-color: #fff0f5;
            padding: 10px;
            border-left: 6px solid #c94f7c;
            border-radius: 5px;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Navigation ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

st.session_state.page = st.sidebar.radio(
    "Navigate",
    ["Home", "Take Test", "Result Explanation", "Feedback", "Resources"],
    index=["Home", "Take Test", "Result Explanation", "Feedback", "Resources"].index(st.session_state.page),
    key="menu"
)

menu = st.session_state.page

# --- Home Page ---
if menu == "Home":
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <h1>MOMLY - Postpartum Depression Risk Predictor</h1>
        <h3>Empowering maternal health through compassion and intelligence</h3>
        <img src="https://images.unsplash.com/photo-1618374656826-e6c9daeddf3e" width="600" style="margin-top:20px; border-radius:10px;">
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start Assessment"):
        st.session_state.page = "Take Test"
        st.rerun()

# --- Take Test Page ---
elif menu == "Take Test":
    st.header("📝 Postpartum Emotional Check-In")

    for var, default in {
        'question_index': 0,
        'responses': [],
        'age': 25,
        'support': "Medium",
        'name': "",
        'place': ""
    }.items():
        if var not in st.session_state:
            st.session_state[var] = default

    idx = st.session_state.question_index

    if idx == 0:
        st.session_state.name = st.text_input("First Name", value=st.session_state.name)
        st.session_state.place = st.text_input("Your Place", value=st.session_state.place)
        st.session_state.age = st.slider("Your Age", 18, 45, value=st.session_state.age)
        st.session_state.support = st.selectbox("Level of Family Support", ["High", "Medium", "Low"],
                                                index=["High", "Medium", "Low"].index(st.session_state.support))
        if st.button("Start Questionnaire"):
            if st.session_state.name.strip() and st.session_state.place.strip():
                st.session_state.question_index += 1
                st.rerun()
            else:
                st.warning("Please enter your name and place before starting.")

    q_responses = [
        ("I have been able to laugh and see the funny side of things.",
         {"As much as I always could": 0, "Not quite so much now": 1, "Definitely not so much now": 2, "Not at all": 3}),
        ("I have looked forward with enjoyment to things",
         {"As much as I ever did": 0, "Rather less than I used to": 1, "Definitely less than I used to": 2, "Hardly at all": 3}),
        ("I have blamed myself unnecessarily when things went wrong",
         {"No, never": 0, "Not very often": 1, "Yes, some of the time": 2, "Yes, most of the time": 3}),
        ("I have been anxious or worried for no good reason",
         {"No, not at all": 0, "Hardly ever": 1, "Yes, sometimes": 2, "Yes, very often": 3}),
        ("I have felt scared or panicky for no very good reason",
         {"No, not at all": 0, "No, not much": 1, "Yes, sometimes": 2, "Yes, quite a lot": 3}),
        ("Things have been getting on top of me",
         {"No, I have been coping as well as ever": 0, "No, most of the time I have coped quite well": 1,
          "Yes, sometimes I haven't been coping as well as usual": 2, "Yes, most of the time I haven't been able to cope at all": 3}),
        ("I have been so unhappy that I have had difficulty sleeping",
         {"No, not at all": 0, "Not very often": 1, "Yes, sometimes": 2, "Yes, most of the time": 3}),
        ("I have felt sad or miserable",
         {"No, not at all": 0, "Not very often": 1, "Yes, quite often": 2, "Yes, most of the time": 3}),
        ("I have been so unhappy that I have been crying",
         {"No, never": 0, "Only occasionally": 1, "Yes, quite often": 2, "Yes, most of the time": 3}),
        ("The thought of harming myself has occurred to me",
         {"Never": 0, "Hardly ever": 1, "Sometimes": 2, "Yes, quite often": 3})
    ]

    if 1 <= idx <= 10:
        q_text, options = q_responses[idx - 1]
        choice = st.radio(f"{idx}. {q_text}", list(options.keys()), key=f"q{idx}")
        col1, col2 = st.columns(2)
        if col1.button("Back") and idx > 1:
            st.session_state.question_index -= 1
            st.session_state.responses.pop()
            st.rerun()
        if col2.button("Next"):
            st.session_state.responses.append(options[choice])
            st.session_state.question_index += 1
            st.rerun()

    elif idx == 11:
        name = st.session_state.name
        place = st.session_state.place
        age = st.session_state.age
        support = st.session_state.support
        q_values = st.session_state.responses
        score = sum(q_values)

        input_df = pd.DataFrame([{
            "Name": name,
            "Age": age,
            "FamilySupport": support,
            **{f"Q{i+1}": val for i, val in enumerate(q_values)},
            "EPDS_Score": score
        }])

        pred_encoded = model.predict(input_df.drop(columns=["Name"]))[0]
        pred_label = le.inverse_transform([pred_encoded])[0]

        st.success(f"{name}, your predicted PPD Risk is: {pred_label}")
        st.caption("Assessment is based on the validated EPDS scale.")

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pred_encoded,
            number={"suffix": " / 3"},
            gauge={
                "axis": {"range": [0, 3]},
                "bar": {"color": "deeppink"},
                "steps": [
                    {"range": [0, 1], "color": "#d0f0c0"},
                    {"range": [1, 2], "color": "#ffe699"},
                    {"range": [2, 3], "color": "#ff9999"}
                ]
            },
            title={"text": "Predicted Risk Level"}
        ))
        st.plotly_chart(fig, use_container_width=True)

        tips = {
            "Mild": "- Stay active\n- Eat well\n- Talk to someone\n- Practice self-care",
            "Moderate": "- Monitor symptoms\n- Join a group\n- Share with family\n- Avoid isolation",
            "Severe": "- Contact a therapist\n- Alert family\n- Prioritize mental health\n- Reduce stressors",
            "Profound": "- Seek urgent psychiatric help\n- Talk to someone now\n- Call helpline\n- Avoid being alone"
        }

        st.subheader("Personalized Tips")
        st.markdown(f"<div class='risk-tip'>{tips.get(pred_label, 'Please consult a professional.')}</div>", unsafe_allow_html=True)

        # PDF Download
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Postpartum Depression Risk Report", ln=True, align='C')
        for key, val in input_df.iloc[0].items():
            pdf.cell(200, 10, txt=f"{key}: {val}", ln=True)
        pdf.cell(200, 10, txt=f"Prediction: {pred_label}", ln=True)
        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        b64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        st.markdown(f'<a href="data:application/pdf;base64,{b64_pdf}" download="{name}_PPD_Report.pdf">📄 Download PDF Report</a>', unsafe_allow_html=True)

        if st.button("Start Over"):
            for key in ['question_index', 'responses', 'age', 'support', 'name', 'place']:
                st.session_state.pop(key, None)
            st.rerun()

# --- Result Explanation ---
elif menu == "Result Explanation":
    st.header("🔍 Understanding Risk Levels")
    st.markdown("""
    | Risk Level | Interpretation |
    |------------|----------------|
    | Mild       | Normal ups and downs |
    | Moderate   | Monitor and talk to someone |
    | Severe     | Likely clinical depression, seek help |
    | Profound   | Needs urgent professional support |
    """)

# --- Feedback ---
elif menu == "Feedback":
    st.header("💬 Share Feedback")
    name = st.text_input("Name (optional)")
    msg = st.text_area("How was your experience with MOMLY?")
    if st.button("Submit"):
        st.success("Thank you for your kind feedback!")

# --- Resources ---
elif menu == "Resources":
    st.header("📚 Resources and Help")
    st.markdown("""
    - [Postpartum Support International](https://www.postpartum.net)
    - [WHO Maternal Mental Health](https://www.who.int/news-room/fact-sheets/detail/mental-health-of-women-during-pregnancy-and-after-childbirth)
    - [India Mental Health Helpline: 1800-599-0019](https://telemanas.mohfw.gov.in)
    - [Talk to MOMLY](#chat-with-momly)
    """)

