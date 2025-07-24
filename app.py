import streamlit as st
from datetime import datetime
import random

# Page setup
st.set_page_config(page_title="MOMLY - Your Gentle Friend", layout="centered")
st.markdown("""
    <style>
    .stApp {
        background-color: #f7f0f5;
    }
    .momly-bubble {
        background-color: #ffe6f0;
        padding: 10px 15px;
        border-radius: 18px;
        margin: 5px 0;
        max-width: 80%;
        display: inline-block;
    }
    .user-bubble {
        background-color: #d9fdd3;
        padding: 10px 15px;
        border-radius: 18px;
        margin: 5px 0;
        max-width: 80%;
        display: inline-block;
        align-self: flex-end;
    }
    </style>
""", unsafe_allow_html=True)

# Title section
st.markdown("<h2 style='text-align:center; color:#c94f7c;'>🤱 MOMLY - Your Gentle Friend</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>I'm here to listen, support, and help you feel calm 🌸</p>", unsafe_allow_html=True)

# Chat history in session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.chat_history.append(("momly", "Hi there, mama! 💖 How are you feeling today?"))

# Keyword-response mapping (basic)
def get_momly_response(user_msg):
    user_msg = user_msg.lower()
    if any(word in user_msg for word in ["sad", "tired", "lonely", "anxious", "depressed"]):
        return random.choice([
            "I'm really sorry you're feeling this way. Want to take a few deep breaths together? 🌷",
            "You're not alone. These feelings are valid and I’m here to help you through them 💛",
            "Would you like a calming video or a small activity suggestion to feel a bit better?"
        ])
    elif any(word in user_msg for word in ["happy", "good", "better", "relaxed"]):
        return random.choice([
            "That makes me so happy to hear! Keep nurturing that peace 🌸",
            "Beautiful! Would you like to save this moment in your mood journal?",
        ])
    elif "activity" in user_msg:
        return random.choice([
            "How about listening to calming music or going for a short walk? 🌿",
            "Try journaling or doodling for 5 minutes – it can be surprisingly healing 🎨",
        ])
    elif "video" in user_msg:
        return "Here's a calming video you might like: [Gentle Relaxation Video](https://www.youtube.com/watch?v=2OEL4P1Rz04) 🎥"
    elif "help" in user_msg or "emergency" in user_msg:
        return "If you’re in crisis, please call a mental health helpline or talk to a loved one right away ❤️"
    else:
        return random.choice([
            "I'm listening 🌷 Tell me more.",
            "Thank you for sharing that. You’re doing better than you think 💖",
            "Would you like to try a quick relaxation exercise?",
        ])

# Chat display
for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"<div class='user-bubble'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='momly-bubble'>{msg}</div>", unsafe_allow_html=True)

# User input
user_input = st.text_input("You:", placeholder="Type something and press Enter...", key="chat_input")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    momly_reply = get_momly_response(user_input)
    st.session_state.chat_history.append(("momly", momly_reply))
    st.experimental_rerun()

# Reset option
if st.button("🧹 Clear Conversation"):
    st.session_state.chat_history = [("momly", "Hi again, mama! How are you feeling right now?")]
    st.experimental_rerun()
