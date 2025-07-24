
import streamlit as st
import random
from datetime import datetime

# Page setup
st.set_page_config(page_title="MOMLY - Your Gentle Friend", layout="centered")
st.markdown("""
    <style>
    .stApp {
        background-color: #f7f0f5;
    }
    .momly-bubble {
        background-color: #ffe6f0;
        padding: 12px 16px;
        border-radius: 20px;
        margin: 6px 0;
        max-width: 80%;
        display: inline-block;
    }
    .user-bubble {
        background-color: #d9fdd3;
        padding: 12px 16px;
        border-radius: 20px;
        margin: 6px 0;
        max-width: 80%;
        display: inline-block;
        align-self: flex-end;
        float: right;
    }
    </style>
""", unsafe_allow_html=True)

# Title section
st.markdown("<h2 style='text-align:center; color:#c94f7c;'>🤱 MOMLY - Your Gentle Friend</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>I'm here to support you anytime, mama 🌸</p>", unsafe_allow_html=True)

# Initialize chat history
if "momly_chat" not in st.session_state:
    st.session_state.momly_chat = []
    st.session_state.momly_chat.append(("momly", "Hi sweet mama 💖 How are you feeling today?"))

# Chatbot response logic
def get_momly_reply(user_message):
    msg = user_message.lower()
    if any(word in msg for word in ["sad", "tired", "lonely", "anxious", "depressed"]):
        return random.choice([
            "I'm sorry you're feeling this way. You're not alone — take a deep breath with me 🌷",
            "These feelings are valid, and I'm here to walk with you 💛",
            "Would you like a calming video or a small breathing exercise?"
        ])
    elif any(word in msg for word in ["happy", "better", "relaxed", "good"]):
        return random.choice([
            "That’s beautiful to hear! Keep shining ✨",
            "So glad to hear that 🌼 Would you like a gentle journal prompt to celebrate this mood?",
        ])
    elif "activity" in msg:
        return "How about a 5-min doodle or a short walk? 🌿 Or maybe journaling how you feel today?"
    elif "video" in msg:
        return "Here's a calming video I found: [Relaxing Baby Moments](https://www.youtube.com/watch?v=2OEL4P1Rz04) 🎥"
    elif "help" in msg or "emergency" in msg:
        return "If you need urgent support, please call a trusted person or a helpline ❤️ You matter."
    else:
        return random.choice([
            "I’m listening 🌷 Tell me more.",
            "Thank you for opening up. You're doing better than you think 💖",
            "Would a gentle affirmation help right now?"
        ])

# Display chat
for sender, msg in st.session_state.momly_chat:
    bubble_class = "momly-bubble" if sender == "momly" else "user-bubble"
    st.markdown(f"<div class='{bubble_class}'>{msg}</div>", unsafe_allow_html=True)

# Input box
user_input = st.text_input("You:", placeholder="Tell MOMLY how you feel...", key="user_input")

if user_input:
    st.session_state.momly_chat.append(("user", user_input))
    reply = get_momly_reply(user_input)
    st.session_state.momly_chat.append(("momly", reply))
    st.experimental_rerun()

# Reset
if st.button("🧹 Clear Conversation"):
    st.session_state.momly_chat = [("momly", "Hi again mama 🌸 How are you feeling right now?")]
    st.experimental_rerun()
