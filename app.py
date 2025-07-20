import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO
import base64
import os

# --- Configuration and File Loading ---
MODEL_PATH = "ppd_model_pipeline.pkl"
ENCODER_PATH = "label_encoder.pkl"
IMAGE_PATH = "maternity_care.png"

if not os.path.exists(MODEL_PATH):
    st.error(f"Error: Model file '{MODEL_PATH}' not found. Please ensure it's in the same directory.")
    st.stop()
if not os.path.exists(ENCODER_PATH):
    st.error(f"Error: Label encoder file '{ENCODER_PATH}' not found. Please ensure it's in the same directory.")
    st.stop()

try:
    model = joblib.load(MODEL_PATH)
    le = joblib.load(ENCODER_PATH)
except Exception as e:
    st.error(f"Error loading model or encoder: {e}. Please check your .pkl files.")
    st.stop()

st.set_page_config(page_title="PPD Risk Predictor", page_icon="🧠", layout="centered")

# --- Global CSS Styling and Animation ---
def add_page_styling():
    st.markdown("""
    <style>
    .stApp {
        animation: fadeBg 10s ease-in-out infinite;
        background-color: #001f3f;
        color: white;
    }
    @keyframes fadeBg {
        0% { background-color: #001f3f; }
        50% { background-color: #001f3f; }
        100% { background-color: #001f3f; }
    }
    body {
        color: white;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 1.1em;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stButton button:first-child {
        background-color: #007BFF;
    }
    .stButton button:first-child:hover {
        background-color: #0056b3;
    }
    div.stSpinner > div {
        text-align: center;
    }
    div.stAlert {
        font-size: 1.1em;
    }
    .css-h5f0l0 {
        color: white !important;
    }
    .css-1d391kg {
        background-color: #00172e;
    }
    .css-1f1j096 {
        color: white;
    }
    .css-pkz2s3 p {
        color: white;
        font-size: 1.1em;
    }
    .css-pkz2s3 button:hover {
        background-color: #002b5c;
    }
    </style>
    """, unsafe_allow_html=True)

add_page_styling()

# --- Session State Initialization ---
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

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

# --- Questionnaire Data ---
QUESTIONS = [
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

# --- PDF Generation Function (with sanitization for FPDF and BytesIO for in-memory) ---
def create_pdf_report(name, place, age, support, q_values, score, pred_label, tips_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(0, 15, txt="Postpartum Depression Risk Prediction Report", ln=True, align='C')
    pdf.ln(10)

    def sanitize_text_for_pdf(text):
        if isinstance(text, (int, float)):
            text = str(text)
        return text.encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Date: {sanitize_text_for_pdf(pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'))}", ln=True)
    pdf.cell(0, 10, txt=f"Name: {sanitize_text_for_pdf(name)}", ln=True)
    pdf.cell(0, 10, txt=f"Place: {sanitize_text_for_pdf(place)}", ln=True)
    pdf.cell(0, 10, txt=f"Age: {sanitize_text_for_pdf(age)}", ln=True)
    pdf.cell(0, 10, txt=f"Family Support Level: {sanitize_text_for_pdf(support)}", ln=True)
    pdf.cell(0, 10, txt=f"Total EPDS Score: {sanitize_text_for_pdf(score)}/30", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt="Predicted Risk Level:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=sanitize_text_for_pdf(pred_label), ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt="Personalized Tips:", ln=True)
    pdf.set_font("Arial", size=12)
    for line in tips_text.split('\n'):
        if line.strip():
            pdf.multi_cell(0, 7, txt=sanitize_text_for_pdf(line.strip()))
    pdf.ln(5)

    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 7, txt="Note: This screening result is based on the EPDS – Edinburgh Postnatal Depression Scale. It is for informational purposes only and does not constitute medical advice. Please consult with a healthcare professional for diagnosis and treatment.")

    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    return pdf_buffer.getvalue()

# --- Sidebar navigation ---
with st.sidebar:
    if os.path.exists(IMAGE_PATH):
        st.image(IMAGE_PATH, width=150)
    else:
        st.warning(f"Warning: Image file '{IMAGE_PATH}' not found. Please place it in the same directory.")

    st.markdown("## Navigation")
    st.session_state.page = st.radio(
        "Navigate",
        ["🏠 Home", "📝 Take Test", "📊 Result Explanation", "📬 Feedback", "🧰 Resources"],
        index=["🏠 Home", "📝 Take Test", "📊 Result Explanation", "📬 Feedback", "🧰 Resources"].index(st.session_state.page),
        key="menu_radio"
    )

menu = st.session_state.page

# --- Page Content based on Navigation ---

# HOME Page
if menu == "🏠 Home":
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <h1 style="font-size: 3.5em; color: white;">POSTPARTUM DEPRESSION RISK PREDICTOR</h1>
        <h3 style="font-size: 1.6em; color: white;">Empowering maternal health through smart technology</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📝 Start Test"):
        st.session_state.page = "📝 Take Test"
        st.session_state.question_index = 0
        st.session_state.responses = []
        st.session_state.age = 25
        st.session_state.support = "Medium"
        st.session_state.name = ""
        st.session_state.place = ""
        st.rerun()

# TEST PAGE
elif menu == "📝 Take Test":
    st.header("📝 Questionnaire")
    st.info("Please answer the following questions to assess your PPD risk based on the Edinburgh Postnatal Depression Scale (EPDS).")

    idx = st.session_state.question_index

    if idx == 0:
        st.subheader("Personal Information")
        st.session_state.name = st.text_input("First Name", value=st.session_state.name, help="Your first name for the report.")
        st.session_state.place = st.text_input("Your Place", value=st.session_state.place, help="Your city or region.")
        st.session_state.age = st.slider("Your Age", 18, 45, value=st.session_state.age, help="Your age in years.")
        st.session_state.support = st.selectbox("Level of Family Support", ["High", "Medium", "Low"],
                                               index=["High", "Medium", "Low"].index(st.session_state.support),
                                               help="How much support do you feel you receive from your family?")

        st.markdown("---")
        if st.button("Start Questionnaire", key="start_questionnaire_btn"):
            if st.session_state.name.strip() and st.session_state.place.strip():
                st.session_state.question_index += 1
                st.rerun()
            else:
                st.warning("Please enter your name and place before starting the questionnaire.")

    elif 1 <= idx <= len(QUESTIONS):
        q_text, options = QUESTIONS[idx - 1]

        st.subheader(f"Question {idx} of {len(QUESTIONS)}")
        st.write(q_text)

        default_index = 0
        if len(st.session_state.responses) >= idx:
            stored_value = st.session_state.responses[idx-1]
            for i, (text, val) in enumerate(options.items()):
                if val == stored_value:
                    default_index = i
                    break

        choice = st.radio("Select your answer:", list(options.keys()), key=f"q{idx}", index=default_index)

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back", key=f"back_q{idx}", disabled=(idx == 1)):
                st.session_state.question_index -= 1
                if len(st.session_state.responses) >= idx:
                    st.session_state.responses.pop()
                st.rerun()
        with col2:
            if st.button("Next ➡️", key=f"next_q{idx}"):
                if len(st.session_state.responses) < idx:
                    st.session_state.responses.append(options[choice])
                else:
                    st.session_state.responses[idx-1] = options[choice]
                st.session_state.question_index += 1
                st.rerun()

    elif idx == len(QUESTIONS) + 1:
        st.subheader("Your PPD Risk Prediction Result")

        name = st.session_state.name
        place = st.session_state.place
        age = st.session_state.age
        support = st.session_state.support
        q_values = st.session_state.responses
        score = sum(q_values)

        if len(q_values) != len(QUESTIONS):
            st.error("It seems some questions were skipped or not fully answered. Please go back and complete all questions.")
            if st.button("Go back to questions"):
                st.session_state.question_index = 1
                st.rerun()
            return # <--- This is where the SyntaxError would occur in the context of the main script body.

        input_data = {
            "Age": [age],
            "FamilySupport": [support],
            "EPDS_Score": [score]
        }
        for i, val in enumerate(q_values):
            input_data[f"Q{i+1}"] = [val]

        input_df = pd.DataFrame(input_data)

        family_support_mapping = {"High": 0, "Medium": 1, "Low": 2}
        input_df['FamilySupport'] = input_df['FamilySupport'].map(family_support_mapping)

        numeric_cols = [f"Q{i+1}" for i in range(len(QUESTIONS))] + ["Age", "EPDS_Score", "FamilySupport"]
        for col in numeric_cols:
            if col in input_df.columns:
                input_df[col] = pd.to_numeric(input_df[col], errors='coerce').fillna(0).astype(int)

        # --- IMPORTANT DEBUGGING STEPS ---
        st.subheader("--- Debugging Info (for developer) ---")
        st.write("DataFrame before prediction:")
        st.dataframe(input_df)
        st.write("DataFrame dtypes:")
        st.write(input_df.dtypes)
        st.write("DataFrame info:")
        buffer = BytesIO()
        input_df.info(buf=buffer)
        st.text(buffer.getvalue().decode('utf-8'))
        st.write("Any NaN values in DataFrame?")
        st.write(input_df.isnull().sum())
        st.subheader("--- End Debugging Info ---")
        # --- END IMPORTANT DEBUGGING STEPS ---

        pred_label = "Error"
        pred_encoded = 0

        try:
            pred_encoded = model.predict(input_df)[0]
            pred_label = le.inverse_transform([pred_encoded])[0]
        except Exception as e:
            st.error(f"Error during prediction: {e}. This likely means the input data types or columns are not what the model expects.")
            st.warning("Please check the 'Debugging Info' above and compare it to how your model was trained.")

        st.success(f"Hello {name}, your predicted PPD Risk Level is: **{pred_label}**")
        st.markdown("<p style='color:#ccc; font-style:italic;'>Note: This screening result is based on the EPDS – Edinburgh Postnatal Depression Scale. It is for informational purposes only.</p>", unsafe_allow_html=True)

        gauge_colors = {
            "Mild": "lightgreen",
            "Moderate": "gold",
            "Severe": "orange",
            "Profound": "red",
            "Error": "gray"
        }
        gauge_bar_color = gauge_colors.get(pred_label, "purple")

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pred_encoded,
            number={"suffix": " / 3", "font": {"color": "white"}},
            gauge={
                "axis": {"range": [0, 3], "tickvals": [0, 1, 2, 3], "ticktext": ["Mild", "Moderate", "Severe", "Profound"], "tickfont": {"color": "white"}},
                "bar": {"color": gauge_bar_color},
                "steps": [
                    {"range": [0, 0.9], "color": "rgba(144, 238, 144, 0.2)"},
                    {"range": [0.9, 1.9], "color": "rgba(255, 215, 0, 0.2)"},
                    {"range": [1.9, 2.9], "color": "rgba(255, 165, 0, 0.2)"},
                    {"range": [2.9, 3.1], "color": "rgba(255, 0, 0, 0.2)"}
                ],
                "threshold": {
                    "line": {"color": "darkblue", "width": 4},
                    "thickness": 0.75,
                    "value": pred_encoded
                }
            },
            title={"text": "PPD Risk Level", "font": {"size": 24, "color": "white"}}
        ))
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10), paper_bgcolor="#001f3f", font={"color": "white"})
        st.plotly_chart(fig, use_container_width=True)

        tips = {
            "Mild": """
- **Stay Active**: Gentle exercise like walking can boost mood.
- **Eat Well**: Maintain a balanced diet for energy and well-being.
- **Talk to Someone**: Share your feelings with a trusted friend, partner, or family member.
- **Practice Self-Care**: Take time for yourself, even if it's just a few minutes of quiet.
- **Rest**: Prioritize sleep whenever possible.
""",
            "Moderate": """
- **Monitor Symptoms**: Keep a journal of your feelings to track changes.
- **Join a Support Group**: Connecting with other new mothers can be incredibly helpful.
- **Share with Family/Partner**: Ensure your support system understands what you're going through.
- **Avoid Isolation**: Make an effort to connect with others, even if you don't feel like it.
- **Consider Professional Check-in**: A brief chat with a doctor or counselor can provide reassurance and early guidance.
""",
            "Severe": """
- **Contact a Therapist/Doctor**: It's crucial to seek professional help for diagnosis and treatment options.
- **Alert Family/Partner**: Let your closest ones know you need significant support.
- **Prioritize Mental Health**: Make your well-being the top priority, even over some daily tasks.
- **Reduce Stressors**: Delegate tasks and reduce commitments where possible.
- **Don't Struggle Alone**: Reach out to helplines or emergency services if you feel overwhelmed.
""",
            "Profound": """
- **Seek Urgent Psychiatric Help**: Contact your doctor, an emergency room, or a mental health crisis line immediately.
- **Talk to Someone Now**: Do not be alone. Reach out to a trusted person, family member, or a crisis hotline.
- **Call Helpline/Emergency Services**: If you feel unsafe or have thoughts of harming yourself or your baby, get immediate professional help.
- **Avoid Being Alone**: Ensure you are in a safe environment with supportive individuals.
- **Remember You're Not Alone**: PPD is treatable, and help is available.
"""
        }
        pred_tips = tips.get(pred_label, "Consult a professional immediately.")

        st.subheader("💡 Personalized Tips")
        st.markdown(pred_tips)

        st.markdown("---")
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            pdf_bytes = create_pdf_report(name, place, age, support, q_values, score, pred_label, pred_tips)
            b64_pdf = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{name}_PPD_Risk_Report.pdf" style="background-color: #007BFF; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; display: inline-block;">📥 Download Result (PDF)</a>'
            st.markdown(href, unsafe_allow_html=True)
        with col_res2:
            if st.button("🔄 Restart", key="restart_test"):
                st.session_state.question_index = 0
                st.session_state.responses = []
                st.session_state.age = 25
                st.session_state.support = "Medium"
                st.session_state.name = ""
                st.session_state.place = ""
                st.session_state.page = "📝 Take Test"
                st.rerun()

# RESULT EXPLANATION
elif menu == "📊 Result Explanation":
    st.header("📊 Understanding Risk Levels")
    st.info("All assessments in this app are based on the EPDS (Edinburgh Postnatal Depression Scale), a trusted and validated 10-question tool used worldwide to screen for postpartum depression.")
    st.markdown("""
    | Risk Level | Encoded Value | EPDS Score Range (Approx.) | Meaning & Recommendation |
    | :--------- | :------------ | :------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
    | **Mild** | 0             | 0 - 9                      | Normal emotional fluctuations after childbirth. Continue with self-care and maintain social connections.                                         |
    | **Moderate** | 1             | 10 - 14                    | Symptoms are noticeable and warrant attention. Consider talking to a trusted person, joining a support group, or consulting a healthcare provider for monitoring. |
    | **Severe** | 2             | 15 - 19                    | Significant symptoms of depression. It is highly recommended to seek professional medical advice and support from a doctor or therapist.         |
    | **Profound** | 3             | 20 - 30                    | Severe symptoms of depression, requiring immediate professional intervention. Please seek urgent help from a healthcare provider or crisis service. |
    """)
    st.markdown("<p style='font-style:italic; color:#aaa;'>Disclaimer: These ranges are approximate and the model's classification may vary slightly based on other input factors like age and family support. Always consult a healthcare professional for diagnosis and treatment.</p>", unsafe_allow_html=True)


# FEEDBACK
elif menu == "📬 Feedback":
    st.header("📬 Share Feedback")
    st.write("Your input helps us improve this tool and support more mothers.")

    with st.form("feedback_form"):
        name = st.text_input("Your Name (Optional)")
        email = st.text_input("Your Email (Optional)", help="We won't share your email.")
        message = st.text_area("Your Feedback / Suggestions", height=150, help="What do you like? What can be improved?")
        submitted = st.form_submit_button("Submit Feedback")

        if submitted:
            if message.strip() == "":
                st.warning("Please enter your feedback before submitting.")
            else:
                st.success("Thank you for your valuable feedback! 💌 We appreciate you taking the time.")

# RESOURCES
elif menu == "🧰 Resources":
    st.header("Helpful Links and Support")
    st.write("If you are struggling or need support, please know that you are not alone and help is available.")

    st.subheader("Emergency & Crisis Support")
    st.markdown("""
    * **National Mental Health Helpline (India):** **1800-599-0019** (Toll-Free)
    * **AASRA (Crisis Intervention, Mumbai, India):** **+91 98204 66726** (24/7)
    * **Vandrevala Foundation (Mental Health Helpline, India):** **1860-2662-345** or **1800-2333-330**
    * **Immediate Medical Emergency:** Dial your local emergency number (e.g., 112 in India)
    """)

    st.subheader("Online Resources & Organizations")
    st.markdown("""
    * **World Health Organization (WHO) - Maternal Mental Health:** [Learn about global initiatives and information on maternal mental health.](https://www.who.int/news-room/fact-sheets/detail/mental-health-of-women-during-pregnancy-and-after-childbirth)
    * **Postpartum Support International (PSI):** [A leading organization dedicated to helping women and families worldwide affected by perinatal mood and anxiety disorders.](https://www.postpartum.net/) (Offers helpline, support groups, and resources)
    * **PPD Moms (Online Support Community):** [An online community for mothers experiencing PPD.](https://www.ppdmoms.com/) (Check for updated links or similar communities)
    * **National Alliance on Mental Illness (NAMI): [Provides advocacy, education, support, and public awareness for people affected by mental illness.](https://www.nami.org/Home)
    """)
    st.markdown("<p style='font-style:italic; color:#aaa;'>Note: Please verify the contact details and website links as they may change over time.</p>", unsafe_allow_html=True)

# Add a subtle footer
st.markdown("<hr style='border:1px solid #002b5c;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777;'>PPD Risk Predictor © 2025. Empowering Maternal Health.</p>", unsafe_allow_html=True)
