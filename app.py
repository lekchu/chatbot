# FINAL APP.PY with login, style, chatbot, PDF fix
import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO
import base64
import os
import random
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# --- AUTH SETUP ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'], config['cookie']['name'],
    config['cookie']['key'], config['cookie']['expiry_days']
)

name, auth_status, username = authenticator.login("Login", location="main")

if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome {name} 👋")

    # Load model and encoder
    model = joblib.load("ppd_model_pipeline.pkl")
    le = joblib.load("label_encoder.pkl")

    # Set up page
    st.set_page_config(page_title="PPD Predictor & MOMLY", layout="wide")

    # Load CSS
    def load_custom_style():
        with open("style/app_style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    load_custom_style()

    if "page" not in st.session_state:
        st.session_state.page = "Home"

    st.session_state.page = st.sidebar.radio(
        "Navigate",
        ["Home", "Take Test", "Result Explanation", "Chat with MOMLY", "Feedback", "Resources"],
        index=["Home", "Take Test", "Result Explanation", "Chat with MOMLY", "Feedback", "Resources"].index(st.session_state.page),
        key="menu"
    )

    menu = st.session_state.page

    # --- HOME ---
    if menu == "Home":
        st.image("images/maternity_care.png", width=250)
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px;">
            <h1>POSTPARTUM DEPRESSION RISK PREDICTOR</h1>
            <h3>Empowering maternal health through smart technology</h3>
            <p style="font-size:1.1em;">Take a quick screening and get personalized support. You are not alone 💖</p>
        </div>
        """, unsafe_allow_html=True)
        st.video("https://www.youtube.com/watch?v=2OEL4P1Rz04")
        if st.button("Start Test"):
            st.session_state.page = "Take Test"
            st.rerun()

    # --- CHAT WITH MOMLY ---
    elif menu == "Chat with MOMLY":
        st.markdown("<h2 style='text-align:center; color:#fdd;'>🤱 MOMLY - Your Gentle Friend</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#ccc;'>I'm here to support you anytime, mama 🌸</p>", unsafe_allow_html=True)

        if "momly_chat" not in st.session_state:
            st.session_state.momly_chat = []
            st.session_state.momly_chat.append(("momly", "Hi sweet mama 💖 How are you feeling today?"))

        def get_momly_reply(user_message):
            msg = user_message.lower()
            if any(word in msg for word in ["sad", "tired", "lonely", "anxious", "depressed"]):
                return random.choice([
                    "You're not alone — take a deep breath with me 🌷",
                    "These feelings are valid, and I’m here with you 💛",
                    "Would you like a calming video or breathing exercise?"
                ])
            elif any(word in msg for word in ["happy", "better", "relaxed", "good"]):
                return random.choice([
                    "That’s beautiful to hear! Keep shining ✨",
                    "So glad to hear that 🌼 Want a journal prompt?"
                ])
            elif "activity" in msg:
                return "Try a short walk, a drawing, or a gratitude list 💚"
            elif "video" in msg:
                return "Here’s something soothing: [Relaxing Video](https://www.youtube.com/watch?v=2OEL4P1Rz04)"
            elif "help" in msg or "emergency" in msg:
                return "Please contact a mental health line or a loved one immediately. You are loved ❤️"
            else:
                return random.choice([
                    "I'm here to listen 🌷",
                    "Tell me more. You're doing great 💖",
                    "Would an affirmation help right now?"
                ])

        for sender, msg in st.session_state.momly_chat:
            bubble_color = "#ffe6f0" if sender == "momly" else "#d9fdd3"
            align = "left" if sender == "momly" else "right"
            st.markdown(f"""
            <div style='background-color:{bubble_color}; padding:10px 15px; border-radius:20px; margin:6px 0; max-width:75%; float:{align}; clear:both; color:black;'>
                {msg}
            </div>""", unsafe_allow_html=True)

        user_input = st.text_input("You:", placeholder="How are you feeling today?", key="chat_input")
        if user_input:
            st.session_state.momly_chat.append(("user", user_input))
            st.session_state.momly_chat.append(("momly", get_momly_reply(user_input)))
            st.experimental_rerun()

        if st.button("🧹 Clear Chat"):
            st.session_state.momly_chat = [("momly", "Hi again 🌸 How are you feeling today?")]
            st.experimental_rerun()

# --- HANDLE LOGIN ERRORS ---
elif auth_status == False:
    st.error("Username or password is incorrect")
    st.stop()
elif auth_status == None:
    st.warning("Please log in to use the app")
    st.stop()



        
