import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO
import os
import random

# Import the chatbot functionality from momly_chatbot.py
# Make sure momly_chatbot.py exists in the same directory!
from momly_chatbot import get_momly_reply, USE_LLM 

# --- Streamlit Page Configuration ---
# THIS MUST BE THE VERY FIRST STREAMLIT COMMAND CALLED!
# Any st.write(), st.sidebar.radio(), st.button() etc. before this will cause the error.
st.set_page_config(page_title="PPD Predictor & MOMLY", layout="wide")

# --- Configuration Paths ---
MODEL_PATH = "ppd_model_pipeline.pkl"
ENCODER_PATH = "label_encoder.pkl"
STYLE_PATH = "style/app_style.css"
IMAGE_PATH = "images/maternity_care.png"
RESULTS_CSV_PATH = "data/ppd_results.csv"

# Ensure necessary directories exist *before* trying to access files in them
os.makedirs("data", exist_ok=True)
os.makedirs("style", exist_ok=True)
os.makedirs("images", exist_ok=True)

# --- Load Model and Encoder ---
@st.cache_resource
def load_model_and_encoder():
    """Loads the pre-trained model and label encoder, stopping the app if files are missing."""
    try:
        model = joblib.load(MODEL_PATH)
        le = joblib.load(ENCODER_PATH)
        return model, le
    except FileNotFoundError as e:
        st.error(f"Required file not found: {e}. Please ensure '{MODEL_PATH}' and '{ENCODER_PATH}' are in the root directory.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading model or encoder: {e}. Please check your .pkl files and their compatibility.")
        st.stop()

model, le = load_model_and_encoder()

# --- Load Custom Styles ---
def load_custom_style(filepath):
    """Loads and applies custom CSS styles from a file."""
    if os.path.exists(filepath):
        with open(filepath) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"Custom style file not found at {filepath}. Using default Streamlit styles.")

load_custom_style(STYLE_PATH)

# --- Session State Initialization ---
# Initialize session state variables if they don't exist
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "momly_chat" not in st.session_state:
    st.session_state.momly_chat = [("momly", "Hi sweet mama 💖 How are you feeling today?")]

# Sidebar navigation
st.session_state.page = st.sidebar.radio(
    "Navigate",
    ["Home", "Take Test", "Result Explanation", "Chat with MOMLY", "Feedback", "Resources"],
    index=["Home", "Take Test", "Result Explanation", "Chat with MOMLY", "Feedback", "Resources"].index(st.session_state.page),
    key="menu_radio"
)

menu = st.session_state.page

# --- Page Content Sections ---

# -------- HOME --------
if menu == "Home":
    if os.path.exists(IMAGE_PATH):
        st.image(IMAGE_PATH, width=250)
    else:
        st.warning(f"Image not found at {IMAGE_PATH}. Please ensure it exists.")
        st.empty() # Placeholder for the image to prevent layout issues

    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <h1>POSTPARTUM DEPRESSION RISK PREDICTOR</h1>
        <h3>Empowering maternal health through smart technology</h3>
        <p style="font-size:1.1em;">Take a quick screening and get personalized support. You are not alone 💖</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Placeholder for a real YouTube video ID (e.g., "dQw4w9WgXcQ")
    # This URL is just a placeholder and will not play an actual video unless replaced.
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") 

    if st.button("Start Test", key="home_start_test_button"):
        st.session_state.page = "Take Test"
        st.rerun()

# -------- TEST --------
elif menu == "Take Test":
    st.header("Postpartum Depression Questionnaire")

    # Initialize test-specific session state variables
    for var, default in {
        'question_index': 0,
        'responses': [], # Stores scores (0-3) for each question
        'age': 25,
        'support': "Medium",
        'name': "",
        'place': ""
    }.items():
        if var not in st.session_state:
            st.session_state[var] = default

    idx = st.session_state.question_index

    # Initial information input page
    if idx == 0:
        st.session_state.name = st.text_input("Your Name", value=st.session_state.name, key="name_input")
        st.session_state.place = st.text_input("Your Location", value=st.session_state.place, key="place_input")
        st.session_state.age = st.slider("Your Age", 18, 45, value=st.session_state.age, key="age_slider")
        st.session_state.support = st.selectbox("Family Support Level", ["High", "Medium", "Low"],
                                                 index=["High", "Medium", "Low"].index(st.session_state.support), key="support_select")
        if st.button("Start Questionnaire", key="start_quiz_button"):
            if st.session_state.name.strip() and st.session_state.place.strip():
                st.session_state.question_index += 1
                st.rerun()
            else:
                st.warning("Please enter your name and location before starting.")

    # EPDS Questionnaire Questions and Options
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
         {"No, I have been coping well": 0, "Most of the time I coped": 1,
          "Sometimes I didn’t cope well": 2, "Most of the time I couldn’t cope": 3}),
        ("I have been so unhappy that I have had difficulty sleeping",
         {"No, not at all": 0, "Not very often": 1, "Yes, sometimes": 2, "Yes, most of the time": 3}),
        ("I have felt sad or miserable",
         {"No, not at all": 0, "Not very often": 1, "Yes, quite often": 2, "Yes, most of the time": 3}),
        ("I have been so unhappy that I have been crying",
         {"No, never": 0, "Only occasionally": 1, "Yes, quite often": 2, "Yes, most of the time": 3}),
        ("The thought of harming myself has occurred to me",
         {"Never": 0, "Hardly ever": 1, "Sometimes": 2, "Yes, quite often": 3})
    ]

    # Display questionnaire pages
    if 1 <= idx <= 10:
        q_text, options = q_responses[idx - 1]
        
        # Determine the currently selected value for the radio button if already answered
        current_response_score = st.session_state.responses[idx-1] if idx-1 < len(st.session_state.responses) else None
        current_response_key = None
        if current_response_score is not None:
            for k, v in options.items():
                if v == current_response_score:
                    current_response_key = k
                    break
        
        # Default to the first option if no prior response or current_response_key not found
        default_index = list(options.keys()).index(current_response_key) if current_response_key else 0
        
        choice = st.radio(f"{idx}. {q_text}", list(options.keys()), index=default_index, key=f"q_radio_{idx}")
        
        col1, col2 = st.columns(2)
        if col1.button("Back", key=f"back_button_{idx}"):
            if idx > 1:
                st.session_state.question_index -= 1
                # Remove the last response if going back, ensuring no IndexError
                if st.session_state.responses and len(st.session_state.responses) >= idx:
                    st.session_state.responses.pop() 
                st.rerun()
            else: # If on the first question, go back to info page
                st.session_state.question_index = 0
                st.session_state.responses = []
                st.rerun()

        if col2.button("Next", key=f"next_button_{idx}"):
            # Update response for current question before moving to next
            if idx-1 < len(st.session_state.responses):
                st.session_state.responses[idx-1] = options[choice]
            else:
                st.session_state.responses.append(options[choice])
            
            st.session_state.question_index += 1
            st.rerun()

    # Display results page
    elif idx == 11:
        # Before processing, ensure all 10 responses are correctly captured.
        if len(st.session_state.responses) != 10:
            st.warning("It seems some questions were skipped or not recorded. Please go back to ensure all 10 questions are answered.")
            if st.button("Return to Questions", key="return_to_questions"):
                st.session_state.question_index = 1 # Send them back to the first question or the last unanswered
                st.rerun()
            st.stop() # Stop execution until the user returns to questions

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

        try:
            pred_encoded = model.predict(input_df.drop(columns=["Name"]))[0]
            pred_label = le.inverse_transform([pred_encoded])[0]
        except Exception as e:
            st.error(f"Error during prediction. Please ensure your model is correctly loaded and data is in the right format: {e}")
            pred_label = "Unknown" # Fallback
            pred_encoded = 0 # Fallback for gauge

        st.success(f"{name}, your predicted PPD Risk is: {pred_label}")

        # Display risk level using Plotly Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pred_encoded,
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

        # Personalized tips based on predicted risk
        tips = {
            "Mild": "- Stay active\n- Eat well\n- Talk to someone\n- Practice self-care",
            "Moderate": "- Monitor symptoms\n- Join a group\n- Share with family\n- Avoid isolation",
            "Severe": "- Contact a therapist\n- Alert family\n- Prioritize mental health\n- Reduce stressors",
            "Profound": "- Seek urgent psychiatric help\n- Talk to someone now\n- Call helpline\n- Avoid being alone"
        }

        st.subheader("Personalized Tips")
        st.markdown(tips.get(pred_label, "Please consult a mental health professional immediately."))

        # Save results to CSV
        try:
            # Check if file exists to decide on header.
            if not os.path.exists(os.path.dirname(RESULTS_CSV_PATH)):
                os.makedirs(os.path.dirname(RESULTS_CSV_PATH))
            input_df.to_csv(RESULTS_CSV_PATH, mode='a', index=False, header=not os.path.exists(RESULTS_CSV_PATH))
        except Exception as e:
            st.warning(f"Could not save results to CSV: {e}")

        # PDF generation using BytesIO for st.download_button
        def create_pdf_report(name, place, age, support, score, pred_label, q_responses_values):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, txt="Postpartum Depression Risk Report", ln=True, align='C')
            pdf.ln(10) # Add some space

            # Personal Info
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, txt="Personal Information:", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, txt=f"Name: {name}", ln=True)
            pdf.cell(0, 10, txt=f"Location: {place}", ln=True)
            pdf.cell(0, 10, txt=f"Age: {age}", ln=True)
            pdf.cell(0, 10, txt=f"Family Support: {support}", ln=True)
            pdf.ln(5)

            # EPDS Score and Risk
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, txt="Assessment Results:", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, txt=f"EPDS Score: {score}", ln=True)
            pdf.cell(0, 10, txt=f"Predicted Risk Level: {pred_label}", ln=True)
            pdf.ln(5)

            # Question Details (Optional, can be added if desired)
            if q_responses_values:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, txt="Questionnaire Responses (Scores):", ln=True)
                pdf.set_font("Arial", size=10)
                for i, q_score in enumerate(q_responses_values):
                    pdf.cell(0, 7, txt=f"Q{i+1}: {q_score}", ln=True)
                pdf.ln(5)

            # Disclaimer
            pdf.set_font("Arial", 'I', 10)
            pdf.multi_cell(0, 5, txt="Disclaimer: This tool uses the EPDS (Edinburgh Postnatal Depression Scale) for screening purposes and provides a predicted risk level based on your responses. It is NOT a diagnostic instrument. For a definitive diagnosis and personalized treatment plan, please consult a qualified healthcare professional or mental health expert. Your well-being is paramount.", align='L')

            pdf_output = BytesIO()
            pdf.output(pdf_output, dest='S')
            return pdf_output.getvalue()

        pdf_bytes = create_pdf_report(name, place, age, support, score, pred_label, q_values)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name=f"{name}_PPD_Result.pdf",
            mime="application/pdf",
            key="download_pdf_button"
         )
        # Use st.download_button for a more reliable download experience
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name=f"{name}_PPD_Result.pdf",
            mime="application/pdf",
            key="download_pdf_button"
        )

        if st.button("Restart Test", key="restart_test_button"):
            # Clear all relevant session state variables
            for key in ['question_index', 'responses', 'age', 'support', 'name', 'place']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# -------- CHAT WITH MOMLY --------
elif menu == "Chat with MOMLY":
    st.markdown("<h2 style='text-align:center; color:#fdd;'>🤱 MOMLY - Your Gentle Friend</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#ccc;'>I'm here to support you anytime, mama 🌸</p>", unsafe_allow_html=True)

    if USE_LLM:
        st.info("MOMLY is currently powered by an intelligent model. Responses may vary.")
    else:
        st.info("MOMLY is using a rule-based system. For a more intelligent experience, configure an LLM API in `momly_chatbot.py`.")

    # Display chat messages
    for sender, msg in st.session_state.momly_chat:
        bubble_color = "#ffe6f0" if sender == "momly" else "#d9fdd3"
        align = "left" if sender == "momly" else "right"
        st.markdown(f"""
        <div style='background-color:{bubble_color}; padding:10px 15px; border-radius:20px; margin:6px 0; max-width:75%; float:{align}; clear:both; color:black;'>
            {msg}
        </div>""", unsafe_allow_html=True)

    # Input for user
    user_input = st.text_input("You:", placeholder="How are you feeling today?", key="chat_input")
    if user_input:
        st.session_state.momly_chat.append(("user", user_input))
        
        # Pass the full chat history to the reply function for context
        reply = get_momly_reply(user_input, st.session_state.momly_chat) 
        st.session_state.momly_chat.append(("momly", reply))
        st.rerun()

    if st.button("🧹 Clear Chat", key="clear_chat_button"):
        st.session_state.momly_chat = [("momly", "Hi again 🌸 How are you feeling today?")]
        st.rerun()

# -------- RESULT EXPLANATION --------
elif menu == "Result Explanation":
    st.header("Understanding Your Risk Level")
    st.markdown("""
    | Risk Level | Meaning                                                     |
    |------------|-------------------------------------------------------------|
    | Mild       | Normal emotional ups and downs. Keep practicing self-care.  |
    | Moderate   | Monitor your mood, consider talking to a trusted person or a professional. |
    | Severe     | It is recommended to seek therapy or professional support.  |
    | Profound   | Please seek urgent professional mental health help immediately. |
    """)

# -------- FEEDBACK --------
elif menu == "Feedback":
    st.header("We value your feedback 💬")
    st.markdown("Your input helps us improve! Please share your thoughts below.")
    with st.form("feedback_form", clear_on_submit=True): # Added clear_on_submit for convenience
        name = st.text_input("Your Name", key="feedback_name")
        email = st.text_input("Your Email (Optional)", key="feedback_email")
        message = st.text_area("Your Feedback", key="feedback_message")
        submitted = st.form_submit_button("Submit Feedback")
        if submitted:
            if not name.strip() or not message.strip():
                st.error("Please provide your name and feedback message.")
            else:
                # In a real application, you would send this to a database/email
                st.success(f"Thank you, {name}, for your feedback! We appreciate it.")
                # Form will clear automatically due to clear_on_submit=True

# -------- RESOURCES --------
elif menu == "Resources":
    st.header("Helpful Links & Support")
    st.markdown("""
    Find valuable resources and support networks here:
    
    * **📞 India Mental Health Helpline:** [1800-599-0019](tel:+9118005990019) (Ministry of Health & Family Welfare, India)
    * **🌐 WHO Maternal Mental Health:** [Understanding Maternal Mental Health](https://www.who.int/news-room/fact-sheets/detail/mental-health-of-women-during-pregnancy-and-after-childbirth) - Information from the World Health Organization.
    * **💞 Postpartum Support International (PSI):** [Global Support Network](https://www.postpartum.net/) - Offers resources, helplines, and support for parents.
    * **📚 National Institute of Mental Health (NIMH) - PPD:** [Information on Postpartum Depression](https://www.nimh.nih.gov/health/topics/depression/postpartum-depression) - Comprehensive guide.
    * **💡 Local Support Groups:** Search for local postpartum support groups in your area. Many hospitals and community centers offer them.
    """)
