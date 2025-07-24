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
                "I'm sorry you're feeling this way. You're not alone — take a deep breath with me 🌷",
                "These feelings are valid, and I'm here to walk with you 💛",
                "Would you like a calming video or a small breathing exercise?"
            ])
        elif any(word in msg for word in ["happy", "better", "relaxed", "good"]):
            return random.choice([
                "That’s beautiful to hear! Keep shining ✨",
                "So glad to hear that 🌼 Want a gentle journal prompt to reflect?",
            ])
        elif "activity" in msg:
            return "How about a 5-min doodle or a short walk? 🌿 Or maybe journaling how you feel today?"
        elif "video" in msg:
            return "Here's a calming video: [Relax Video](https://www.youtube.com/watch?v=2OEL4P1Rz04) 🎥"
        elif "help" in msg or "emergency" in msg:
            return "If you need urgent support, call a trusted person or mental health helpline ❤️"
        else:
            return random.choice([
                "I’m listening 🌷 Tell me more.",
                "You're doing better than you think 💖",
                "Would you like a soothing affirmation?"
            ])

    # Display messages
    for sender, msg in st.session_state.momly_chat:
        bubble_color = "#ffe6f0" if sender == "momly" else "#d9fdd3"
        text_color = "#000"
        align = "left" if sender == "momly" else "right"
        st.markdown(f"""
        <div style='background-color:{bubble_color}; padding:10px 15px; border-radius:20px; margin:6px 0; max-width:75%; float:{align}; clear:both; color:{text_color};'>
            {msg}
        </div>""", unsafe_allow_html=True)

    user_input = st.text_input("You:", placeholder="How are you feeling today?", key="chat_input")

    if user_input:
        st.session_state.momly_chat.append(("user", user_input))
        reply = get_momly_reply(user_input)
        st.session_state.momly_chat.append(("momly", reply))
        st.experimental_rerun()

    if st.button("🧹 Clear Chat"):
        st.session_state.momly_chat = [("momly", "Hi again 🌸 How are you feeling right now?")]
        st.experimental_rerun()
