import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO
import base64
import os # To check if files exist

# --- Configuration and File Loading ---
# Define file paths
MODEL_PATH = "ppd_model_pipeline.pkl"
ENCODER_PATH = "label_encoder.pkl"
IMAGE_PATH = "maternity_care.png"

# Check if model and encoder files exist
if not os.path.exists(MODEL_PATH):
    st.error(f"Error: Model file '{MODEL_PATH}' not found. Please ensure it's in the same directory.")
    st.stop()
if not os.path.exists(ENCODER_PATH):
    st.error(f"Error: Label encoder file '{ENCODER_PATH}' not found. Please ensure it's in the same directory.")
    st.stop()

# Load model and encoder
try:
    model = joblib.load(MODEL_PATH)
    le = joblib.load(ENCODER_PATH)
except Exception as e:
    st.error(f"Error loading model or encoder: {e}. Please check your .pkl files.")
    st.stop()

st.set_page_config(page_title="PPD Risk Predictor", page_icon="🧠", layout="centered") # Changed layout to centered for better focus

# --- Session State Initialization ---
# Initialize session state variables if they don't exist
for var, default in {
    'page': "Home",
    'question_index': 0,
    'responses': [],
    'age': 25,
    'support': "Medium",
    'name': "",
    'place': ""
}.items():
    if var not in st.session_state:
        st.session_state[var] = default

# --- Global CSS Styling ---
st.markdown("""
<style>
.stApp {
    background-color: #001f3f; /* Dark Blue */
    color: white;
}
.stButton>button {
    background-color: #4CAF50; /* Green */
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 1.1em;
    border: none;
    cursor: pointer;
    transition: background-color 0.3s ease;
}
.stButton>button:hover {
    background-color: #45a049; /* Darker Green on Hover */
}
/* Style for primary buttons (e.g., Start Test, Next, Submit) */
.stButton button:first-child {
    background-color: #007BFF; /* Primary Blue */
}
.stButton button:first-child:hover {
    background-color: #0056b3; /* Darker Primary Blue on Hover */
}
/* Center elements in the main body more effectively */
div.stSpinner > div {
    text-align: center;
}
div.stAlert { /* Streamlit Alerts (success, warning, error, info) */
    font-size: 1.1em;
}
.css-h5f0l0 { /* Specific class for radio buttons in Streamlit, targeting the label */
    color: white !important;
}
/* Sidebar styling */
.css-1d391kg { /* Target sidebar background */
    background-color: #00172e; /* Slightly darker blue for sidebar */
}
.css-1f1j096 { /* Target sidebar text */
    color: white;
}
.css-pkz2s3 p { /* Sidebar button text */
    color: white;
    font-size: 1.1em;
}
.css-pkz2s3 button:hover { /* Sidebar button hover */
    background-color: #002b5c;
}
.bottom-image {
    display: flex;
    justify-content: center;
    margin-top: 50px;
}
</style>
""", unsafe_allow_html=True)

# --- Questionnaire Data ---
# Using a list of dictionaries for more clarity
QUESTIONS = [
    {"text": "I have been able to laugh and see the funny side of things.",
     "options": {"As much as I always could": 0, "Not quite so much now": 1, "Definitely not so much now": 2, "Not at all": 3}},
    {"text": "I have looked forward with enjoyment to things",
     "options": {"As much as I ever did": 0, "Rather less than I used to": 1, "Definitely less than I used to": 2, "Hardly at all": 3}},
    {"text": "I have blamed myself unnecessarily when things went wrong",
     "options": {"No, never": 0, "Not very often": 1, "Yes, some of the time": 2, "Yes, most of the time": 3}},
    {"text": "I have been anxious or worried for no good reason",
     "options": {"No, not at all": 0, "Hardly ever": 1, "Yes, sometimes": 2, "Yes, very often": 3}},
    {"text": "I have felt scared or panicky for no very good reason",
     "options": {"No, not at all": 0, "No, not much": 1, "Yes, sometimes": 2, "Yes, quite a lot": 3}},
    {"text": "Things have been getting on top of me",
     "options": {"No, I have been coping as well as ever": 0, "No, most of the time I have coped quite well": 1,
                 "Yes, sometimes I haven't been coping as well as usual": 2, "Yes, most of the time I haven't been able to cope at all": 3}},
    {"text": "I have been so unhappy that I have had difficulty sleeping",
     "options": {"No, not at all": 0, "Not very often": 1, "Yes, sometimes": 2, "Yes, most of the time": 3}},
    {"text": "I have felt sad or miserable",
     "options": {"No, not at all": 0, "Not very often": 1, "Yes, quite often": 2, "Yes, most of the time": 3}},
    {"text": "I have been so unhappy that I have been crying",
     "options": {"No, never": 0, "Only occasionally": 1, "Yes, quite often": 2, "Yes, most of the time": 3}},
    {"text": "The thought of harming myself has occurred to me",
     "options": {"Never": 0, "Hardly ever": 1, "Sometimes": 2, "Yes, quite often": 3}}
]

# --- PDF Generation Function ---
def create_pdf_report(name, place, age, support, q_values, score, pred_label, tips_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(0, 15, txt="Postpartum Depression Risk Prediction Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(0, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(0, 10, txt=f"Place: {place}", ln=True)
    pdf.cell(0, 10, txt=f"Age: {age}", ln=True)
    pdf.cell(0, 10, txt=f"Family Support Level: {support}", ln=True)
    pdf.cell(0, 10, txt=f"Total EPDS Score: {score}/30", ln=True) # Max score is 3*10 = 30
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt="Predicted Risk Level:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=pred_label, ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt="Personalized Tips:", ln=True)
    pdf.set_font("Arial", size=12)
    # Add tips line by line
    for line in tips_text.split('\n'):
        if line.strip(): # Avoid empty lines
            pdf.multi_cell(0, 7, txt=line.strip())
    pdf.ln(5)

    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 7, txt="Note: This screening result is based on the EPDS – Edinburgh Postnatal Depression Scale. It is for informational purposes only and does not constitute medical advice. Please consult with a healthcare professional for diagnosis and treatment.")

    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    return pdf_buffer.getvalue()

# --- Page Functions ---

def home_page():
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <h1 style="font-size: 3.5em; color: white;">POSTPARTUM DEPRESSION RISK PREDICTOR</h1>
        <h3 style="font-size: 1.6em; color: white;">Empowering maternal health through smart technology</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("Start Test", key="home_start_test"):
        st.session_state.page = "Take Test"
        st.session_state.question_index = 0 # Reset questionnaire for a new test
        st.session_state.responses = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def take_test_page():
    st.header("PPD Risk Assessment Questionnaire")
    st.info("Please answer the following questions to assess your PPD risk based on the Edinburgh Postnatal Depression Scale (EPDS).")

    idx = st.session_state.question_index

    if idx == 0:
        st.subheader("Personal Information")
        name = st.text_input("First Name", value=st.session_state.name, help="Your first name for the report.")
        place = st.text_input("Your Place", value=st.session_state.place, help="Your city or region.")
        age = st.slider("Your Age", 18, 45, value=st.session_state.age, help="Your age in years.")
        support = st.selectbox("Level of Family Support", ["High", "Medium", "Low"],
                               index=["High", "Medium", "Low"].index(st.session_state.support),
                               help="How much support do you feel you receive from your family?")

        # Update session state with collected info
        st.session_state.name = name
        st.session_state.place = place
        st.session_state.age = age
        st.session_state.support = support

        st.markdown("---") # Separator
        if st.button("Start Questionnaire", key="start_questionnaire_btn"):
            if st.session_state.name.strip() and st.session_state.place.strip():
                st.session_state.question_index += 1
                st.rerun()
            else:
                st.warning("Please enter your name and place before starting the questionnaire.")

    elif 1 <= idx <= len(QUESTIONS):
        current_q_data = QUESTIONS[idx - 1]
        q_text = current_q_data["text"]
        options = current_q_data["options"]

        st.subheader(f"Question {idx} of {len(QUESTIONS)}")
        st.write(q_text)

        # Determine the default index for the radio button
        # If a response for this question already exists, use its index
        default_index = 0
        if len(st.session_state.responses) >= idx:
            # Find the key (text option) corresponding to the stored value
            stored_value = st.session_state.responses[idx-1]
            for i, (text, val) in enumerate(options.items()):
                if val == stored_value:
                    default_index = i
                    break

        choice = st.radio("Select your answer:", list(options.keys()), key=f"q{idx}", index=default_index)

        st.markdown("---")
        col1, col2 = st.columns([1, 1]) # Adjust column width for buttons

        with col1:
            if st.button("Previous", key=f"back_q{idx}", disabled=(idx == 1)): # Disable 'Previous' on first question
                st.session_state.question_index -= 1
                # Remove the response for the question we're going back from, if it exists
                if len(st.session_state.responses) >= idx:
                    st.session_state.responses.pop()
                st.rerun()
        with col2:
            if st.button("Next", key=f"next_q{idx}"):
                # Update response for the current question
                if len(st.session_state.responses) < idx: # Append if new
                    st.session_state.responses.append(options[choice])
                else: # Overwrite if existing (e.g., after going back and changing an answer)
                    st.session_state.responses[idx-1] = options[choice]

                st.session_state.question_index += 1
                st.rerun()

    elif idx == len(QUESTIONS) + 1: # After all questions are answered
        st.subheader("Your PPD Risk Prediction Result")

        name = st.session_state.name
        place = st.session_state.place
        age = st.session_state.age
        support = st.session_state.support
        q_values = st.session_state.responses
        score = sum(q_values)

        if len(q_values) != len(QUESTIONS):
            st.error("It seems some questions were skipped. Please go back and complete all questions.")
            if st.button("Go back to questions"):
                st.session_state.question_index = 1 # Go back to the first question
                st.rerun()
            return

        input_df = pd.DataFrame([{
            "Age": age,
            "FamilySupport": support,
            **{f"Q{i+1}": val for i, val in enumerate(q_values)},
            "EPDS_Score": score
        }])

        # Encode FamilySupport before prediction
        input_df['FamilySupport'] = input_df['FamilySupport'].map({"High": 0, "Medium": 1, "Low": 2})

        try:
            pred_encoded = model.predict(input_df)[0]
            pred_label = le.inverse_transform([pred_encoded])[0]
        except Exception as e:
            st.error(f"Error during prediction: {e}. Please ensure the model pipeline and data types are correct.")
            pred_label = "Error" # Fallback
            pred_encoded = 0 # Fallback for gauge

        st.success(f"Hello {name}, your predicted PPD Risk Level is: **{pred_label}**")
        st.markdown("<p style='color:#ccc; font-style:italic;'>Note: This screening result is based on the EPDS – Edinburgh Postnatal Depression Scale. It is for informational purposes only.</p>", unsafe_allow_html=True)

        # Define colors for the gauge based on risk level
        gauge_colors = {
            "Mild": "lightgreen",
            "Moderate": "gold",
            "Severe": "orange",
            "Profound": "red",
            "Error": "gray"
        }
        gauge_bar_color = gauge_colors.get(pred_label, "purple") # Default if label not found

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pred_encoded,
            number={"suffix": " / 3", "font": {"color": "white"}}, # Max encoded value is 3 (for Profound)
            gauge={
                "axis": {"range": [0, 3], "tickvals": [0, 1, 2, 3], "ticktext": ["Mild", "Moderate", "Severe", "Profound"], "tickfont": {"color": "white"}},
                "bar": {"color": gauge_bar_color},
                "steps": [
                    {"range": [0, 0.9], "color": "rgba(144, 238, 144, 0.2)"}, # Mild
                    {"range": [0.9, 1.9], "color": "rgba(255, 215, 0, 0.2)"}, # Moderate
                    {"range": [1.9, 2.9], "color": "rgba(255, 165, 0, 0.2)"}, # Severe
                    {"range": [2.9, 3.1], "color": "rgba(255, 0, 0, 0.2)"}  # Profound (slightly extended to ensure 3 fits)
                ],
                "threshold": {
                    "line": {"color": "darkblue", "width": 4},
                    "thickness": 0.75,
                    "value": pred_encoded
                }
            },
            title={"text": "PPD Risk Level", "font": {"size": 24, "color": "white"}}
        ))
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10), paper_bgcolor="#001f3f", font={"color": "white"}) # Match app background
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
        pred_tips = tips.get(pred_label, "Consult a professional immediately.") # Default to professional help for any undefined label

        st.subheader("Personalized Tips & Recommendations")
        st.markdown(pred_tips)

        st.markdown("---")
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            pdf_bytes = create_pdf_report(name, place, age, support, q_values, score, pred_label, pred_tips)
            b64_pdf = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{name}_PPD_Risk_Report.pdf" style="background-color: #007BFF; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; display: inline-block;">Download Result (PDF)</a>'
            st.markdown(href, unsafe_allow_html=True)
        with col_res2:
            if st.button("Take Another Test", key="restart_test"):
                # Reset all relevant session state variables
                st.session_state.question_index = 0
                st.session_state.responses = []
                st.session_state.age = 25 # Reset to default
                st.session_state.support = "Medium" # Reset to default
                st.session_state.name = "" # Clear name
                st.session_state.place = "" # Clear place
                st.session_state.page = "Take Test" # Stay on test page or go to Home
                st.rerun()

def result_explanation_page():
    st.header("Understanding Your PPD Risk Level")
    st.info("The assessment in this app is based on the **Edinburgh Postnatal Depression Scale (EPDS)**, a widely used screening tool. Your total score from the 10 questions determines your risk category.")

    st.subheader("EPDS Score Interpretation")
    st.markdown("""
    The EPDS is scored from 0 to 30. A higher score indicates more symptoms of depression.

    * **0-9**: Typically indicates a low probability of PPD.
    * **10-12**: Suggests a moderate probability of PPD. It's advisable to monitor symptoms and consider discussing with a healthcare professional.
    * **13 or higher**: Strongly suggests the presence of PPD and indicates a need for professional evaluation.
    """)

    st.subheader("Risk Level Breakdown (as used in this predictor)")
    st.markdown("""
    | Risk Level | Encoded Value | EPDS Score Range (Approx.) | Meaning & Recommendation |
    | :--------- | :------------ | :------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
    | **Mild** | 0             | 0 - 9                      | Normal emotional fluctuations after childbirth. Continue with self-care and maintain social connections.                                         |
    | **Moderate** | 1             | 10 - 14                    | Symptoms are noticeable and warrant attention. Consider talking to a trusted person, joining a support group, or consulting a healthcare provider for monitoring. |
    | **Severe** | 2             | 15 - 19                    | Significant symptoms of depression. It is highly recommended to seek professional medical advice and support from a doctor or therapist.         |
    | **Profound** | 3             | 20 - 30                    | Severe symptoms of depression, requiring immediate professional intervention. Please seek urgent help from a healthcare provider or crisis service. |
    """)
    st.markdown("<p style='font-style:italic; color:#aaa;'>Disclaimer: These ranges are approximate and the model's classification may vary slightly based on other input factors like age and family support. Always consult a healthcare professional for diagnosis and treatment.</p>", unsafe_allow_html=True)

def feedback_page():
    st.header("Share Your Valuable Feedback")
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
                # In a real application, you would send this data to a backend (e.g., database, email service)
                # For this demo, we'll just show a success message.
                st.success("Thank you for your valuable feedback! We appreciate you taking the time.")
                # Clear form fields after submission (requires re-running the script, or setting form values directly if possible in Streamlit)
                # This often involves resetting session state variables or using a key trick for text_input
                # For simplicity here, we just show success.

def resources_page():
    st.header("Helpful Resources & Support")
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
    * **National Alliance on Mental Illness (NAMI):** [Provides advocacy, education, support, and public awareness for people affected by mental illness.](https://www.nami.org/Home)
    """)
    st.markdown("<p style='font-style:italic; color:#aaa;'>Note: Please verify the contact details and website links as they may change over time.</p>", unsafe_allow_html=True)

# --- Main App Logic ---

# Sidebar Navigation
with st.sidebar:
    st.image(IMAGE_PATH, width=150)
    st.markdown("## Navigation")
    pages = ["Home", "Take Test", "Result Explanation", "Feedback", "Resources"]
    for p in pages:
        if st.button(p, key=f"sidebar_{p}"):
            st.session_state.page = p
            st.rerun()

# Page Router
menu = st.session_state.page

if menu == "Home":
    home_page()
elif menu == "Take Test":
    take_test_page()
elif menu == "Result Explanation":
    result_explanation_page()
elif menu == "Feedback":
    feedback_page()
elif menu == "Resources":
    resources_page()

# 👶 Add bottom-centered image (Moved to sidebar for better aesthetic, or can keep here if preferred in main area)
# If you want it *below* the main content area always, keep this block:
# with open(IMAGE_PATH, "rb") as f:
#     image_data = f.read()
# b64_image = base64.b64encode(image_data).decode()
# st.markdown(f"""
# <div class="bottom-image">
#     <img src="data:image/png;base64,{b64_image}" width="250"/>
# </div>
# """, unsafe_allow_html=True)

# Add a subtle footer
st.markdown("<hr style='border:1px solid #002b5c;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777;'>PPD Risk Predictor © 2025. Empowering Maternal Health.</p>", unsafe_allow_html=True)
