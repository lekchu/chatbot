
import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import json

# Load ML model and label encoder
model = joblib.load("ppd_model_pipeline (1).pkl")
le = joblib.load("label_encoder (1).pkl")

# Page configuration
st.set_page_config(page_title="PPD Risk Predictor", layout="wide")

# Sidebar navigation
st.sidebar.title("🔍 Navigate")
page = st.sidebar.radio("Go to", ["🏠 Home", "🧠 Predict", "📚 About", "🌐 Resources", "📝 Feedback", "💬 Chatbot Assistant"])

# --- Home Page ---
if page == "🏠 Home":
    st.title("Postpartum Depression (PPD) Risk Predictor")
    st.markdown("""
    Welcome to the PPD Risk Predictor Web App.

    **Postpartum Depression (PPD)** affects many mothers globally. 
    This tool uses machine learning to assess the potential **risk level** of PPD 
    based on maternal, familial, and social data.
    
    > ⚠️ This tool is **not a medical diagnosis**. Always consult a healthcare provider.
    """)

# --- Prediction Page ---
elif page == "🧠 Predict":
    st.title("🧠 PPD Risk Prediction Form")

    with st.form("ppd_form"):
        st.subheader("Please fill in the following:")
        
        age = st.number_input("Mother's Age", min_value=15, max_value=50)
        employment = st.selectbox("Are you employed?", ["Yes", "No"])
        partner_support = st.slider("Partner Support Level (1-5)", 1, 5)
        number_of_children = st.number_input("Number of Children", min_value=0, max_value=10)
        education = st.selectbox("Education Level", ["None", "Primary", "Secondary", "Graduate", "Postgraduate"])
        physical_health = st.selectbox("Any physical health issues?", ["Yes", "No"])
        past_mental_issues = st.selectbox("History of mental health issues?", ["Yes", "No"])
        family_support = st.slider("Family Support Level (1-5)", 1, 5)
        sleep_hours = st.slider("Average Sleep Hours", 0, 12)
        breastfeeding = st.selectbox("Currently breastfeeding?", ["Yes", "No"])
        
        submit = st.form_submit_button("🔍 Predict")

    if submit:
        input_df = pd.DataFrame({
            "Age": [age],
            "Employment": [employment],
            "PartnerSupport": [partner_support],
            "Children": [number_of_children],
            "Education": [education],
            "PhysicalHealthIssues": [physical_health],
            "MentalHealthHistory": [past_mental_issues],
            "FamilySupport": [family_support],
            "SleepHours": [sleep_hours],
            "Breastfeeding": [breastfeeding]
        })

        prediction = model.predict(input_df)
        label = le.inverse_transform(prediction)[0]

        st.success(f"🧾 **Predicted Risk Level: {label}**")

        fig = go.Figure(data=[go.Pie(labels=["Risk Level"], values=[1], hole=.5)])
        fig.update_traces(marker=dict(colors=["#e76f51"]), textinfo='none')
        fig.update_layout(title_text=f"Risk Level: {label}")
        st.plotly_chart(fig)

# --- About Page ---
elif page == "📚 About":
    st.title("📚 About This Project")
    st.markdown("""
    This PPD Predictor is part of a research-based initiative to identify early signs of Postpartum Depression.

    - **Model Used**: Feed-Forward Artificial Neural Network (FFANN)
    - **Accuracy**: ~95% (multi-class classification)
    - **Data**: Maternal, family, and health data (based on EPDS scale)
    - **Goal**: Assist mothers and healthcare providers in early risk identification.

    Developed by **Lily**, MSc Computer Science.
    """)

# --- Resources Page ---
elif page == "🌐 Resources":
    st.title("🌐 Mental Health Resources")
    st.markdown("""
    - [Postpartum Support International](https://www.postpartum.net/)
    - [WHO Maternal Mental Health](https://www.who.int/news-room/fact-sheets/detail/mental-health-of-women-during-pregnancy-and-after-childbirth)
    - [India Mental Health Helpline](https://www.nimhans.ac.in/helpline-number/)

    Reach out. You're not alone. ❤️
    """)

# --- Feedback Page ---
elif page == "📝 Feedback":
    st.title("📝 Feedback")
    with st.form("feedback_form"):
        name = st.text_input("Your Name (optional)")
        feedback = st.text_area("Your thoughts about this app:")
        submitted = st.form_submit_button("Submit")

    if submitted:
        st.success("Thank you for your feedback!")

# --- Chatbot Page ---
elif page == "💬 Chatbot Assistant":
    st.title("💬 Chatbot Assistant")

    # Load Lottie animation
    def load_lottie(path):
        with open(path, "r") as f:
            return json.load(f)

    lottie_json = load_lottie("animation.json")
    st_lottie(lottie_json, height=200)

    st.markdown("Ask me anything about Postpartum Depression or this app!")
    user_input = st.text_input("You:", placeholder="Type your question here...")

    def get_bot_reply(user_message):
        user_message = user_message.lower()

        if "hello" in user_message or "hi" in user_message:
            return "Hello! I'm here to help you understand postpartum depression and guide you through the app."

        elif "what is ppd" in user_message or "postpartum depression" in user_message:
            return "Postpartum Depression (PPD) is a type of mood disorder associated with childbirth, affecting mental health after delivery."

        elif "predict" in user_message or "how to predict" in user_message:
            return "To predict your PPD risk, go to the '🧠 Predict' page and fill out the questionnaire."

        elif "help" in user_message:
            return "Sure! You can ask about PPD, how the app works, or find mental health support under '🌐 Resources'."

        elif "resource" in user_message or "support" in user_message:
            return "Visit the '🌐 Resources' page for mental health helplines and international support sites."

        elif "bye" in user_message:
            return "Take care! If you have any concerns, always consult a medical professional."

        elif user_message.strip() == "":
            return ""

        else:
            return "I'm still learning! Please try asking something else related to postpartum depression or the app."

    if user_input:
        st.markdown(f"**You:** {user_input}")
        response = get_bot_reply(user_input)
        st.markdown(f"**Bot:** {response}")
