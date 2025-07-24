import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO
import os
import random
import base64 # <-- Make sure to add this import!

# Import the chatbot functionality from momly_chatbot.py
# Make sure momly_chatbot.py exists in the same directory!


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
MOMLY_CHARACTER_GIF_PATH = "images/momly_character.gif" 

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

load_custom_style(STYLE_PATH) # This loads your app_style (1).css

# --- MOMLY Animated Character (Global Logo Placement) ---
# Moved here to appear as a fixed logo on all pages
if os.path.exists(MOMLY_CHARACTER_GIF_PATH):
    st.markdown(f"""
    <img src="data:image/gif;base64,{base64.b64encode(open(MOMLY_CHARACTER_GIF_PATH, 'rb').read()).decode()}" class="momly-character">
    """, unsafe_allow_html=True)
else:
    st.warning(f"MOMLY character GIF not found at {MOMLY_CHARACTER_GIF_PATH}.")
# --- End of MOMLY Animated Character Addition ---

# --- Session State Initialization ---
# Initialize session state variables if they don't exist
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "momly_chat" not in st.session_state:
    st.session_state.momly_chat = [("momly", "Hi sweet mama 💖 How are you feeling today?")]

# Sidebar navigation - This will now appear on the right due to CSS
st.session_state.page = st.sidebar.radio(
    "Navigate",
    ["Home", "Take Test", "Result Explanation", "Chat with MOMLY", "Feedback", "Resources"],
    index=["Home", "Take Test", "Result Explanation", "Chat with MOMLY", "Feedback", "Resources"].index(st.session_state.page),
    key="menu_radio"
)

menu = st.session_state.page

# ... (rest of your app (8).py content remains the same) ...
