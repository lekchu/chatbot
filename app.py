import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO
import base64
import os
import random

# Load model and encoder
model = joblib.load("ppd_model_pipeline.pkl")
le = joblib.load("label_encoder.pkl")

# Set up page
st.set_page_config(page_title="PPD Predictor & MOMLY", layout="wide")

# Load custom styles
def load_custom_style():
    with open("style/app_style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_style()

# Sidebar navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"

st.session_state.page = st.sidebar.radio(
    "Navigate",
    ["Home", "Take Test", "Result Explanation", "Chat with MOMLY", "Feedback", "Resources"],
    index=["Home", "Take Test", "Result Explanation", "Chat with MOMLY", "Feedback", "Resources"].index(st.session_state.page),
    key="menu"
)

menu = st.session_state.page

# -------- HOME --------
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

# -------- TEST --------
elif menu == "Take Test":
    st.header("Postpartum Depression Questionnaire")

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
        st.session_state.name = st.text_input("Your Name", value=st.session_state.name)
        st.session_state.place = st.text_input("Your Location", value=st.session_state.place)
        st.session_state.age = st.slider("Your Age", 18, 45, value=st.session_state.age)
        st.session_state.support = st.selectbox("Family Support Level", ["High", "Medium", "Low"],
                                                index=["High", "Medium", "Low"].index(st.session_state.support))
        if st.button("Start Questionnaire"):
            if st.session_state.name.strip() and st.session_state.place.strip():
                st.session_state.question_index += 1
                st.rerun()
            else:
                st.warning("Please enter your name and location before starting.")

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

        tips = {
            "Mild": "- Stay active\n- Eat well\n- Talk to someone\n- Practice self-care",
            "Moderate": "- Monitor symptoms\n- Join a group\n- Share with family\n- Avoid isolation",
            "Severe": "- Contact a therapist\n- Alert family\n- Prioritize mental health\n- Reduce stressors",
            "Profound": "- Seek urgent psychiatric help\n- Talk to someone now\n- Call helpline\n- Avoid being alone"
        }

        st.subheader("Personalized Tips")
        st.markdown(tips.get(pred_label, "Please consult a mental health professional immediately."))

        os.makedirs("data", exist_ok=True)
        input_df.to_csv("data/ppd_results.csv", mode='a', index=False, header=not os.path.exists("data/ppd_results.csv"))

        # PDF fix for Streamlit Cloud
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Postpartum Depression Risk Report", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
        pdf.cell(200, 10, txt=f"Place: {place}", ln=True)
        pdf.cell(200, 10, txt=f"Age: {age}", ln=True)
        pdf.cell(200, 10, txt=f"Support: {support}", ln=True)
        pdf.cell(200, 10, txt=f"Score: {score}", ln=True)
        pdf.cell(200, 10, txt=f"Predicted Risk: {pred_label}", ln=True)
        pdf.cell(200, 10, txt="Tool used: EPDS – Edinburgh Postnatal Depression Scale", ln=True)

        pdf_data = pdf.output(dest='S').encode('latin1')
        b64_pdf = base64.b64encode(pdf_data).decode('utf-8')
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{name}_PPD_Result.pdf">📄 Download PDF Report</a>'
        st.markdown(href, unsafe_allow_html=True)

        if st.button("Restart"):
            for key in ['question_index', 'responses', 'age', 'support', 'name', 'place']:
                st.session_state.pop(key, None)
            st.rerun()

# -------- MOMLY CHATBOT --------
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

# -------- RESULT INFO --------
elif menu == "Result Explanation":
    st.header("Understanding Your Risk Level")
    st.markdown("""
    | Risk Level | Meaning |
    |------------|----------------|
    | Mild       | Normal emotional ups/downs |
    | Moderate   | Monitor mood, talk to someone |
    | Severe     | May need therapy/support |
    | Profound   | Seek professional help soon |
    """)

# -------- FEEDBACK --------
elif menu == "Feedback":
    st.header("We value your feedback 💬")
    name = st.text_input("Your Name")
    message = st.text_area("Your Feedback")
    if st.button("Submit"):
        st.success("Thank you for your kind feedback!")

# -------- RESOURCES --------
elif menu == "Resources":
    st.header("Helpful Links & Support")
    st.markdown("""
    - 📞 [India Mental Health Helpline - 1800-599-0019](https://www.mohfw.gov.in)
    - 🌐 [WHO Maternal Mental Health](https://www.who.int/news-room/fact-sheets/detail/mental-health-of-women-during-pregnancy-and-after-childbirth)
    - 💞 [Postpartum Support International](https://www.postpartum.net/)
    """)
