import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO
import base64

# Load model and label encoder
# Ensure these files are in the same directory or provide correct paths
try:
    model = joblib.load("ppd_model_pipeline.pkl")
    le = joblib.load("label_encoder.pkl")
except FileNotFoundError:
    st.error("Model or Label Encoder files not found. Please ensure 'ppd_model_pipeline (1).pkl' and 'label_encoder (1).pkl' are in the same directory.")
    st.stop() # Stop execution if files are not found

# Page config
st.set_page_config(page_title="PPD Risk Predictor", page_icon="🧠", layout="wide")

# Blue background animation - MODIFIED FOR IMAGE BACKGROUND
def add_page_animation():
    st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1540306431945-816d2ddb6e21?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"); /* REPLACE WITH YOUR IMAGE URL */
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed; /* Keeps background fixed when scrolling */
        position: relative; /* Needed for the ::before pseudo-element */
    }
    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.4); /* Dark overlay for readability, adjust opacity as needed */
        z-index: -1; /* Puts the overlay behind the content */
    }
    /* Styles for text and elements to ensure readability on dark background */
    h1, h2, h3, h4, h5, h6, label, .stMarkdown, .stSuccess, .stInfo, .stWarning, p, .stRadio > div > label > div > p, .stSelectbox > label > div > p {
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7); /* Optional text shadow */
    }
    .stButton>button {
        background-color: #4CAF50; /* Green */
        color: white;
        padding: 10px 24px;
        border: none;
        border-radius: 8px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        -webkit-transition-duration: 0.4s; /* Safari */
        transition-duration: 0.4s;
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19);
    }
    .stButton>button:hover {
        background-color: #45a049;
        color: white;
    }
    /* Style for text inputs and text areas for better visibility */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(255, 255, 255, 0.8) !important; /* Slightly transparent white background */
        color: black !important;
        border-radius: 5px;
        padding: 8px;
    }
    /* Style for selectbox for better visibility */
    .stSelectbox>div>div {
        background-color: rgba(255, 255, 255, 0.8) !important;
        color: black !important;
        border-radius: 5px;
    }
    /* Style for radio buttons for better visibility */
    .stRadio > div > label > div > p {
        color: white !important; /* Ensure radio button text is white */
    }
    /* Adjust sidebar background color for better contrast */
    .stSidebar {
        background-color: rgba(0, 31, 63, 0.9) !important; /* Darker, slightly transparent blue */
    }
    .stSidebar .stRadio > label {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

add_page_animation()

# Sidebar navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Add "Chat with SereniMom" to the navigation
st.session_state.page = st.sidebar.radio(
    "Navigate",
    ["Home", "Take Test", "Chat with SereniMom", "Result Explanation", "Feedback", "Resources"],
    index=["Home", "Take Test", "Chat with SereniMom", "Result Explanation", "Feedback", "Resources"].index(st.session_state.page),
    key="menu"
)

menu = st.session_state.page

# HOME
if menu == "Home":
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <h1 style="font-size: 3.5em; color: white;">POSTPARTUM DEPRESSION RISK PREDICTOR</h1>
        <h3 style="font-size: 1.6em; color: white;">Empowering maternal health through smart technology</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start Test"):
        st.session_state.page = "Take Test"
        st.rerun()

# TEST PAGE
elif menu == "Take Test":
    st.header("Questionnaire")

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
        st.session_state.name = st.text_input("First Name", value=st.session_state.name)
        st.session_state.place = st.text_input("Your Place", value=st.session_state.place)
        st.session_state.age = st.slider("Your Age", 18, 45, value=st.session_state.age)
        st.session_state.support = st.selectbox("Level of Family Support", ["High", "Medium", "Low"],
                                                index=["High", "Medium", "Low"].index(st.session_state.support))
        if st.button("Start Questionnaire"):
            if st.session_state.name.strip() and st.session_state.place.strip():
                st.session_state.question_index += 1
                st.rerun()
            else:
                st.warning("Please enter your name and place before starting.")

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
         {"No, I have been coping as well as ever": 0, "No, most of the time I have coped quite well": 1,
          "Yes, sometimes I haven't been coping as well as usual": 2, "Yes, most of the time I haven't been able to cope at all": 3}),
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
        with col1:
            if st.button("Back") and idx > 1:
                st.session_state.question_index -= 1
                if st.session_state.responses: # Ensure responses list is not empty before popping
                    st.session_state.responses.pop()
                st.rerun()
        with col2:
            if st.button("Next"):
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

        # Perform prediction
        # The model expects 'FamilySupport' to be encoded, so let's ensure this is handled
        # The pipeline should handle this if it's set up correctly, but a direct check is good.
        try:
            pred_encoded = model.predict(input_df.drop(columns=["Name"]))[0]
            pred_label = le.inverse_transform([pred_encoded])[0]
        except Exception as e:
            st.error(f"Error during prediction: {e}")
            st.stop()


        st.success(f"{name}, your predicted PPD Risk is: {pred_label}")
        st.markdown("<p style='color:#ccc; font-style:italic;'>Note: This screening result is generated based on the EPDS – Edinburgh Postnatal Depression Scale, a globally validated tool for postpartum depression assessment.</p>", unsafe_allow_html=True)

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
            title={"text": "Risk Level", "font": {"color": "white"}} # Ensure title color is white
        ))
        st.plotly_chart(fig, use_container_width=True)

        tips = {
            "Mild": "- Stay active\n- Eat well\n- Talk to someone\n- Practice self-care",
            "Moderate": "- Monitor symptoms\n- Join a group\n- Share with family\n- Avoid isolation",
            "Severe": "- Contact a therapist\n- Alert family\n- Prioritize mental health\n- Reduce stressors",
            "Profound": "- Seek urgent psychiatric help\n- Talk to someone now\n- Call helpline\n- Avoid being alone"
        }

        st.subheader("Personalized Tips")
        st.markdown(tips.get(pred_label, "Consult a professional immediately."))

        # PDF Report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Postpartum Depression Risk Prediction", ln=True, align='C')
        pdf.ln(10) # Add a line break for spacing
        pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
        pdf.cell(200, 10, txt=f"Place: {place}", ln=True)
        pdf.cell(200, 10, txt=f"Age: {age}", ln=True)
        pdf.cell(200, 10, txt=f"Support Level: {support}", ln=True)
        pdf.cell(200, 10, txt=f"Total Score: {score}", ln=True)
        pdf.cell(200, 10, txt=f"Predicted Risk Level: {pred_label}", ln=True)
        pdf.ln(10) # Add a line break for spacing
        pdf.set_font("Arial", 'I', size=10) # Italic font for note
        pdf.multi_cell(0, 10, txt="(Assessment based on the EPDS - Edinburgh Postnatal Depression Scale, a globally validated tool for postpartum depression assessment.)")
        pdf.ln(5)
        pdf.set_font("Arial", size=12) # Back to normal font
        pdf.multi_cell(0, 10, txt=f"Personalized Tips:\n{tips.get(pred_label, 'Consult a professional immediately.')}")


        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        b64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{name}_PPD_Result.pdf">Download Result (PDF)</a>'
        st.markdown(href, unsafe_allow_html=True)

        if st.button("Restart"):
            for key in ['question_index', 'responses', 'age', 'support', 'name', 'place']:
                st.session_state.pop(key, None)
            st.rerun()

# CHAT WITH SERENIMOM (PLACEHOLDER FOR CHATBOT)
elif menu == "Chat with SereniMom":
    st.header("Chat with SereniMom")
    st.write("Hello! I'm SereniMom, your friendly companion. I'm here to listen, offer support, and answer your questions about motherhood and well-being. How can I help you today?")

    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat messages
    for message in st.session_state.chat_history:
        st.markdown(message) # Use markdown to allow for bolding or other formatting

    # User input
    user_input = st.text_input("Type your message here...", key="chat_input")
    if st.button("Send Message"):
        if user_input:
            # Append user message to history
            st.session_state.chat_history.append(f"**You:** {user_input}")

            # --- This is where you would call your actual chatbot backend ---
            # For now, it's a placeholder response
            chatbot_response = "Thank you for sharing. I'm still learning, but I'm here for you. Please remember to reach out to a professional if you need immediate support."
            # In a real application, you'd send `user_input` to your Flask/FastAPI backend
            # and get a meaningful response back.
            # Example:
            # import requests
            # try:
            #    response_api = requests.post("YOUR_CHATBOT_BACKEND_URL/chat", json={"message": user_input})
            #    chatbot_response = response_api.json().get("reply", "Sorry, I couldn't understand that.")
            # except requests.exceptions.RequestException:
            #    chatbot_response = "I'm having trouble connecting right now. Please try again later."
            # --- End of chatbot backend call placeholder ---

            # Append chatbot response to history
            st.session_state.chat_history.append(f"**SereniMom:** {chatbot_response}")

            # Rerun to update the chat history display
            st.rerun()

# RESULT EXPLANATION
elif menu == "Result Explanation":
    st.header("Understanding Risk Levels")
    st.info("All assessments in this app are based on the EPDS (Edinburgh Postnatal Depression Scale), a trusted and validated 10-question tool used worldwide to screen for postpartum depression.")
    st.markdown("""
    <style>
        .dataframe {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            color: white; /* Text color for the table */
        }
        .dataframe th, .dataframe td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .dataframe th {
            background-color: #003366; /* Darker blue for header */
            color: white;
        }
        .dataframe tr:nth-child(even) {
            background-color: rgba(255, 255, 255, 0.1); /* Slightly transparent white for even rows */
        }
        .dataframe tr:nth-child(odd) {
            background-color: rgba(255, 255, 255, 0.05); /* Even more transparent for odd rows */
        }
    </style>
    <table class="dataframe">
        <thead>
            <tr>
                <th>Risk Level</th>
                <th>Meaning</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Mild (0)</td>
                <td>Normal ups and downs</td>
            </tr>
            <tr>
                <td>Moderate (1)</td>
                <td>Requires monitoring</td>
            </tr>
            <tr>
                <td>Severe (2)</td>
                <td>Suggests possible clinical depression</td>
            </tr>
            <tr>
                <td>Profound (3)</td>
                <td>Needs professional help urgently</td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)


# FEEDBACK
elif menu == "Feedback":
    st.header("Share Feedback")
    st.write("We value your input! Please share your thoughts on how we can improve.")
    name = st.text_input("Your Name")
    message = st.text_area("Your Feedback")
    if st.button("Submit Feedback"):
        if name.strip() and message.strip():
            # In a real application, you would save this feedback to a database
            st.success("Thank you for your valuable feedback!")
            st.session_state.feedback_name = "" # Clear after submission
            st.session_state.feedback_message = "" # Clear after submission
            # Note: Directly clearing text_input and text_area values like this
            # is tricky with Streamlit's reruns. For production, consider using
            # a different state management or a form submission pattern.
        else:
            st.warning("Please fill in both your name and feedback message.")

# RESOURCES
elif menu == "Resources":
    st.header("Helpful Links and Support")
    st.markdown("""
    Here are some resources that can provide further assistance and information:

    - **National Mental Health Helpline (India):** [1800-599-0019](tel:18005990019) (Ministry of Health and Family Welfare, India)
    - **WHO Maternal Mental Health:** [Learn more about global initiatives and guidelines](https://www.who.int/news-room/fact-sheets/detail/mental-health-of-women-during-pregnancy-and-after-childbirth)
    - **Postpartum Support International (PSI):** [Global support for maternal mental health](https://www.postpartum.net/)
    - **Aasra (India-based suicide prevention & mental health helpline):** [aasra.info](http://www.aasra.info/)
    - **Online Therapy Platforms:** Consider exploring platforms like BetterHelp or Talkspace for online therapy options (check availability in your region).
    """)
    st.subheader("Remember:")
    st.info("Seeking help is a sign of strength. You are not alone.")
