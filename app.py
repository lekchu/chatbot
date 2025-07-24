import streamlit as st
import pandas as pd
import joblib
import os
import base64
import momly_chatbot

# --- Configuration ---
MODEL_PATH = "ppd_model_pipeline.pkl"
ENCODER_PATH = "label_encoder.pkl"
STYLE_PATH = "style/app_style.css"
LOGO_PATH = "images/momly_character.gif"
SIDEBAR_BG = "images/background.png"

# Create necessary folders
os.makedirs("data", exist_ok=True)
os.makedirs("style", exist_ok=True)
os.makedirs("images", exist_ok=True)

# --- Page Config ---
st.set_page_config(page_title="MOMLY - Postpartum Support", layout="wide")

# --- Load Model & Encoder ---
@st.cache_resource
def load_model_and_encoder():
    try:
        model = joblib.load(MODEL_PATH)
        encoder = joblib.load(ENCODER_PATH)
        return model, encoder
    except Exception as e:
        st.error(f"Error loading model or encoder: {e}")
        st.stop()

model, encoder = load_model_and_encoder()

# --- Load Styles ---
def load_custom_style(path):
    if os.path.exists(path):
        with open(path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Inject sidebar background
    if os.path.exists(SIDEBAR_BG):
        sidebar_bg_encoded = base64.b64encode(open(SIDEBAR_BG, "rb").read()).decode()
        st.markdown(f"""
            <style>
                section[data-testid="stSidebar"] {{
                    background-image: url("data:image/png;base64,{sidebar_bg_encoded}");
                    background-size: cover;
                    background-position: center;
                }}
            </style>
        """, unsafe_allow_html=True)

load_custom_style(STYLE_PATH)

# --- MOMLY Floating Character ---
if os.path.exists(LOGO_PATH):
    st.markdown(f"""
        <img src="data:image/gif;base64,{base64.b64encode(open(LOGO_PATH, 'rb').read()).decode()}"
        class="momly-character-floating">
    """, unsafe_allow_html=True)

# --- Session Initialization ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "momly_chat" not in st.session_state:
    st.session_state.momly_chat = [("momly", "Hi sweet mama 💖 How are you feeling today?")]

# --- Navigation ---
st.session_state.page = st.sidebar.radio(
    "Navigate",
    ["Home", "Take Test", "Result Explanation", "Chat with MOMLY", "Feedback", "Resources"],
    index=["Home", "Take Test", "Result Explanation", "Chat with MOMLY", "Feedback", "Resources"].index(st.session_state.page),
    key="menu_radio"
)

menu = st.session_state.page

# --- Page Logic ---

# --- Home Page ---
if menu == "Home":
    st.title("👩‍🍼 Welcome to MOMLY")
    st.markdown("""
        **MOMLY** is your gentle companion during postpartum recovery.
        From emotional check-ins to baby tips — we’re here for you 💗
    """)

# --- Take Test Page ---
elif menu == "Take Test":
    st.header("🧠 Postpartum Depression Self-Assessment")
    st.info("This test is not a diagnosis. It’s a helpful screening tool 💬")

    # Replace with your actual input questions
    st.write("Questionnaire coming soon...")

# --- Results Explanation ---
elif menu == "Result Explanation":
    st.header("📊 Understanding Your Results")
    st.write("""
    Your score helps identify if you're at risk for postpartum depression (PPD).
    We use a clinically validated model for guidance, not for diagnosis.
    """)

# --- Chatbot Page ---
elif menu == "Chat with MOMLY":
    st.markdown('<div id="momly-chat-container">', unsafe_allow_html=True)
    st.markdown("<h4>💬 Talk to MOMLY</h4>", unsafe_allow_html=True)

    for sender, msg in st.session_state.momly_chat:
        bubble_class = "user-bubble" if sender == "user" else "momly-bubble"
        st.markdown(f'<div class="{bubble_class}">{msg}</div>', unsafe_allow_html=True)

    user_input = st.text_input("Type your message:", key="chat_input")
    if user_input:
        st.session_state.momly_chat.append(("user", user_input))
        reply = momly_chatbot.momly_response(user_input)
        st.session_state.momly_chat.append(("momly", reply))
        st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# --- Feedback Page ---
elif menu == "Feedback":
    st.header("💬 We'd love your feedback!")
    st.markdown("Please help us improve MOMLY for future mothers 💝")

    with st.form("feedback_form"):
        name = st.text_input("Name (optional)")
        experience = st.radio("How was your experience?", ["Excellent", "Good", "Okay", "Needs Improvement"])
        comment = st.text_area("Additional comments or suggestions")
        submitted = st.form_submit_button("Submit")

        if submitted:
            st.success("Thanks for your feedback, mama 💌")

# --- Resources Page ---
elif menu == "Resources":
    st.header("📚 Trusted Resources for Mothers")

    st.markdown("""
    - [📖 Postpartum Support International](https://www.postpartum.net)
    - [🍼 WHO Postnatal Care Guidelines](https://www.who.int)
    - [💡 CDC: Mental Health for Moms](https://www.cdc.gov/reproductivehealth)
    - [📞 National Helpline (India): 1800-599-0019](https://telemanas.mohfw.gov.in/)
    - [🌐 Find local counselors & support groups](https://therapyroute.com)

    > MOMLY is here with love — but professional help is always encouraged when needed 💗
    """)

    st.info("Feel free to explore, read, or ask MOMLY directly!")


