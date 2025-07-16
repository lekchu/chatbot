import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO
import base64

# --- Load Model and Label Encoder ---
# Ensure these files are in the same directory as app.py
try:
    model = joblib.load("ppd_model_pipeline.pkl")
    le = joblib.load("label_encoder.pkl")
except FileNotFoundError:
    st.error("Error: Model or label encoder file not found. Please ensure 'ppd_model_pipeline.pkl' and 'label_encoder.pkl' are in the same directory as 'app.py'.")
    st.stop() # Stop the app if essential files are missing

# --- Page Configuration ---
st.set_page_config(page_title="PPD Risk Predictor", page_icon="🧠", layout="wide")

# --- Helper Function for Base64 Image Encoding ---
def get_base64_image(image_path):
    """Encodes an image to a base64 string for embedding in CSS."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except FileNotFoundError:
        # st.warning(f"Background image not found at '{image_path}'. Ensure it's in the same directory as 'app.py'.")
        return "" # Return empty string if not found, to avoid breaking CSS

# --- Dynamic CSS Generation with Background Image and Animations ---
# Get base64 string for background image (assuming 'background.png' exists)
bg_image_base64 = get_base64_image("background.png")

custom_css = f"""
<style>
/* Global App Styling - Dark Blue/Black Theme */
.stApp {{
    background-color: #0A1128; /* Deep dark blue, similar to vdigtech.com */
    color: #FAFAFA; /* Light off-white for general text */
    font-family: 'Arial', sans-serif; /* A clear, modern sans-serif font */
    animation: fadeIn 2s ease-in-out; /* Global fade-in animation for the app */
}}

/* Hide the default Streamlit header and footer */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

/* Custom Header / Top Navigation Bar */
.top-nav-container {{
    background-color: #1C2C5B; /* Darker blue for header */
    padding: 10px 20px;
    display: flex;
    justify-content: center; /* Center the navigation items */
    gap: 20px; /* Space between navigation buttons */
    border-bottom: 2px solid #E84C3D; /* Accent line at the bottom of the nav */
}}

.top-nav-button > button {{
    background-color: transparent; /* Make buttons transparent initially */
    color: white;
    border: none;
    padding: 10px 20px;
    font-size: 1.1em;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.3s ease, color 0.3s ease, transform 0.2s ease;
    border-radius: 5px;
}}

.top-nav-button > button:hover {{
    background-color: rgba(232, 76, 61, 0.2); /* Light red semi-transparent on hover */
    color: #E84C3D; /* Highlight text with accent color */
    transform: translateY(-2px); /* Subtle lift */
}}

.top-nav-button > button[aria-selected="true"] {{
    background-color: #E84C3D; /* Vibrant red for selected item */
    color: white; /* White text for selected item */
    font-weight: bold;
}}


/* Header/Title Styling */
h1, h2, h3, h4, h5, h6 {{
    color: #FAFAFA; /* Ensure all headers are light */
    text-align: center; /* Center align main headers for a grander feel */
}}

/* Specific Home Page Title */
.home-title {{
    font-size: 3.5em;
    color: #FAFAFA;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.5); /* Subtle shadow for depth */
    animation: slideInFromLeft 1s ease-out; /* Animation for home title */
}}

.home-subtitle {{
    font-size: 1.6em;
    color: #E0E0E0; /* Slightly dimmer than main text */
    margin-top: -10px; /* Pull subtitle closer to title */
    animation: slideInFromRight 1s ease-out 0.3s forwards; /* Animation for subtitle with delay */
    opacity: 0; /* Start invisible for animation */
}}

/* Sidebar Styling - Add background image - HIDING IT IF TOP NAV IS USED */
[data-testid="stSidebar"] {{
    display: none; /* Hide the entire sidebar */
}}

/* Buttons Styling - General (for buttons not in top nav) */
div.stButton > button:first-child {{
    background-color: #E84C3D; /* A vibrant red, similar to vdigtech.com's accents */
    color: white;
    border: none;
    border-radius: 8px; /* Rounded corners for modern look */
    padding: 10px 20px;
    font-size: 1.1em;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s ease;
    margin: 10px 5px; /* Add some margin around buttons */
}}

div.stButton > button:first-child:hover {{
    background-color: #C23A2C; /* Darker red on hover */
    transform: translateY(-2px); /* Slight lift on hover */
}}

/* Input Fields and Selectboxes */
.stTextInput > div > div > input,
.stSelectbox > div > div > div > div,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {{
    background-color: #2D416B; /* Darker input fields */
    color: #FAFAFA;
    border: 1px solid #4A6B9C; /* Subtle border */
    border-radius: 5px;
    padding: 10px;
    width: 100%; /* Ensure inputs take full width of their container */
}}
.stTextInput > label, .stSelectbox > label, .stSlider > label, .stTextArea > label {{
    color: #FAFAFA; /* Ensure labels are light */
}}

/* Specific styling for the selectbox dropdown to ensure text visibility */
.stSelectbox div[data-baseweb="select"] > div {{
    width: 100%; /* Ensure the select box itself takes full width */
}}
.stSelectbox div[data-baseweb="select"] > div > div[role="button"] {{
    width: 100%; /* Ensure the displayed button within selectbox takes full width */
    padding-right: 25px; /* Add padding to prevent text from going under arrow */
}}


/* Radio buttons (main content) */
.stRadio > label {{
    color: #FAFAFA; /* Ensure radio labels are light */
}}

/* Success, Info, Warning messages */
div[data-testid="stAlert"] {{
    border-radius: 8px;
    padding: 15px;
}}
div[data-testid="stAlert"].success {{
    background-color: #28a74520; /* Light green transparent background */
    color: #28a745; /* Green text */
    border-left: 5px solid #28a745;
}}
div[data-testid="stAlert"].info {{
    background-color: #17a2b820; /* Light blue transparent background */
    color: #17a2b8; /* Blue text */
    border-left: 5px solid #17a2b8;
}}
div[data-testid="stAlert"].warning {{
    background-color: #ffc10720; /* Light yellow transparent background */
    color: #ffc107; /* Yellow text */
    border-left: 5px solid #ffc107;
}}

/* Table styling in Result Explanation */
.stMarkdown table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
    background-color: #1C2C5B; /* Table background matching sidebar */
    color: #FAFAFA;
}}
.stMarkdown th, .stMarkdown td {{
    border: 1px solid #4A6B9C; /* Table cell borders */
    padding: 10px;
    text-align: left;
}}
.stMarkdown th {{
    background-color: #2D416B; /* Table header background */
    font-weight: bold;
}}

/* PDF Download Link Styling */
a[download] {{
    display: inline-block;
    background-color: #17A2B8; /* A nice blue for download link */
    color: white;
    padding: 10px 20px;
    border-radius: 8px;
    text-decoration: none;
    margin-top: 20px;
    transition: background-color 0.3s ease;
}}
a[download]:hover {{
    background-color: #138496; /* Darker blue on hover */
}}

/* Custom note styling */
.custom-note {{
    color: #ccc;
    font-style: italic;
    text-align: center;
    margin-top: 20px;
}}

/* Keyframe Animations for Home Page */
@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to {{ opacity: 1; }}
}}

@keyframes slideInFromLeft {{
    from {{ transform: translateX(-100%); opacity: 0; }}
    to {{ transform: translateX(0); opacity: 1; }}
}}

@keyframes slideInFromRight {{
    from {{ transform: translateX(100%); opacity: 0; }}
    to {{ transform: translateX(0); opacity: 1; }}
}}

</style>
"""

st.markdown(custom_css, unsafe_allow_html=True) # Apply the custom CSS

# --- Session State Initialization ---
# Initialize session state variables once at the beginning of the script
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "responses" not in st.session_state:
    st.session_state.responses = []
if "age" not in st.session_state:
    st.session_state.age = 25
if "support" not in st.session_state:
    st.session_state.support = "Medium"
if "name" not in st.session_state:
    st.session_state.name = ""
if "place" not in st.session_state:
    st.session_state.place = ""
# Flag for feedback submission to prevent re-displaying success message on rerun
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False


# --- TOP Navigation Bar ---
nav_items = ["Home", "Take Test", "Result Explanation", "Feedback", "Resources"]
cols = st.columns(len(nav_items)) # Create a column for each navigation item

st.markdown("<div class='top-nav-container'>", unsafe_allow_html=True) # Start nav container
for i, item in enumerate(nav_items):
    # Use st.markdown to create a custom button-like element with class 'top-nav-button'
    # and a data attribute to indicate if it's the current page
    is_selected = "true" if st.session_state.page == item else "false"
    if st.button(item, key=f"top_nav_{item}", type="secondary"):
        st.session_state.page = item
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True) # End nav container


menu = st.session_state.page # Get the current page from session state

# --- Main Content Rendering ---

# HOME
if menu == "Home":
    # Apply specific classes for animation
    st.markdown(f"""
    <div style="text-align: center; padding: 60px 20px;">
        <h1 class="home-title">POSTPARTUM DEPRESSION RISK PREDICTOR</h1>
        <h3 class="home-subtitle">Empowering maternal health through smart technology</h3>
    </div>
    """, unsafe_allow_html=True)

    # Place the button below the markdown text, centered
    st.markdown("<div style='text-align: center; margin-top: 40px;'>", unsafe_allow_html=True)
    if st.button("Start Test", key="home_start_button"): # Added key to prevent warning if multiple buttons have same label
        st.session_state.page = "Take Test"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# TEST PAGE
elif menu == "Take Test":
    st.header("Questionnaire")

    idx = st.session_state.question_index

    if idx == 0:
        st.session_state.name = st.text_input("First Name", value=st.session_state.name, key="first_name_input")
        st.session_state.place = st.text_input("Your Place", value=st.session_state.place, key="place_input")
        st.session_state.age = st.slider("Your Age", 18, 45, value=st.session_state.age, key="age_slider")
        # Ensure selectbox uses the correct current value from session_state
        support_options = ["High", "Medium", "Low"]
        st.session_state.support = st.selectbox("Level of Family Support", support_options,
                                                index=support_options.index(st.session_state.support),
                                                key="support_selectbox")

        st.markdown("<br>", unsafe_allow_html=True) # Add some space

        if st.button("Start Questionnaire", key="start_questionnaire_button"):
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
        st.markdown(f"**Question {idx} of 10**")
        q_text, options = q_responses[idx - 1]
        
        # Determine current selection for radio button if navigating back
        current_response_value = None
        if len(st.session_state.responses) >= idx:
            current_response_value = st.session_state.responses[idx-1]
        
        default_index = 0
        if current_response_value is not None:
            # Find the index of the previously selected value
            for i, (key, val) in enumerate(options.items()):
                if val == current_response_value:
                    default_index = i
                    break

        choice = st.radio(f"{q_text}", list(options.keys()), key=f"q_radio_{idx}", index=default_index)

        st.markdown("<br>", unsafe_allow_html=True) # Add some space

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back", key=f"back_button_{idx}"):
                if idx > 1:
                    st.session_state.question_index -= 1
                    # No need to pop here, as the response will be overwritten by next button click
                    # if the user changes their answer on a previous question.
                    # Or, if simply going back, the state is preserved until they move forward again.
                    st.rerun()
                else: # If on first question (idx == 1), go back to info input (idx == 0)
                    st.session_state.question_index = 0
                    st.rerun()
        with col2:
            if st.button("Next", key=f"next_button_{idx}"):
                # Store or update the response for the current question
                if len(st.session_state.responses) < idx: # If it's a new question
                    st.session_state.responses.append(options[choice])
                else: # If navigating back and then forward (updating existing response)
                    st.session_state.responses[idx-1] = options[choice]

                st.session_state.question_index += 1
                st.rerun()

    elif idx == 11: # End of questionnaire, display results
        name = st.session_state.name
        place = st.session_state.place
        age = st.session_state.age
        support = st.session_state.support
        q_values = st.session_state.responses

        if len(q_values) != 10: # Basic check if all 10 questions have responses
            st.error("It seems some questions were skipped or not completed. Please go back and complete the questionnaire.")
            if st.button("Go Back to Questions", key="go_back_questions"):
                st.session_state.question_index = 1 # Reset to the first question
                # Do NOT clear responses here if the user just needs to complete skipped questions
                st.rerun()
            st.stop() # Stop further execution until user goes back

        score = sum(q_values)

        input_df = pd.DataFrame([{
            "Name": name, # Included for context, but dropped before model prediction
            "Age": age,
            "FamilySupport": support,
            **{f"Q{i+1}": val for i, val in enumerate(q_values)},
            "EPDS_Score": score
        }])

        pred_encoded = model.predict(input_df.drop(columns=["Name"]))[0]
        pred_label = le.inverse_transform([pred_encoded])[0]

        st.markdown(f"<h2 style='text-align: center; color: #E84C3D;'>{name}, Your PPD Risk Prediction:</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #FAFAFA;'>{pred_label}</h3>", unsafe_allow_html=True)
        st.markdown("<p class='custom-note'>Note: This screening result is generated based on the EPDS – Edinburgh Postnatal Depression Scale, a globally validated tool for postpartum depression assessment.</p>", unsafe_allow_html=True)

        # Gauge chart with improved colors and a more central look
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pred_encoded,
            number={"suffix": " / 3", "font_color": "#FAFAFA"}, # White number
            gauge={
                "axis": {"range": [0, 3], "tickwidth": 1, "tickcolor": "#FAFAFA"},
                "bar": {"color": "#E84C3D"}, # Red/pink bar
                "steps": [
                    {"range": [0, 1], "color": "#28a745"}, # Green for Mild
                    {"range": [1, 2], "color": "#ffc107"}, # Yellow for Moderate
                    {"range": [2, 3], "color": "#dc3545"}  # Red for Severe/Profound
                ],
                "threshold": {
                    "line": {"color": "white", "width": 4},
                    "thickness": 0.75,
                    "value": pred_encoded # Show current value on threshold
                }
            },
            title={"text": "<span style='color:#FAFAFA;'>Risk Level</span>"} # White title
        ))
        fig.update_layout(
            paper_bgcolor="#0A1128", # Background of the chart area
            font_color="#FAFAFA" # Default font color for the chart
        )
        st.plotly_chart(fig, use_container_width=True)

        tips = {
            "Mild": "- Stay active\n- Eat well\n- Talk to someone\n- Practice self-care",
            "Moderate": "- Monitor symptoms\n- Join a group\n- Share with family\n- Avoid isolation",
            "Severe": "- Contact a therapist\n- Alert family\n- Prioritize mental health\n- Reduce stressors",
            "Profound": "- Seek urgent psychiatric help\n- Talk to someone now\n- Call helpline\n- Avoid being alone"
        }

        st.subheader("Personalized Tips")
        st.markdown(tips.get(pred_label, "Consult a professional immediately."))

        # PDF Report Generation
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        pdf.cell(200, 10, txt="Postpartum Depression Risk Prediction Report", ln=True, align='C')
        pdf.ln(10) # Add a line break for spacing

        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
        pdf.cell(200, 10, txt=f"Place: {place}", ln=True)
        pdf.cell(200, 10, txt=f"Age: {age}", ln=True)
        pdf.cell(200, 10, txt=f"Support Level: {support}", ln=True)
        pdf.ln(5) # Small line break
        pdf.cell(200, 10, txt=f"Total EPDS Score: {score}", ln=True)
        
        # Determine color for predicted risk level in PDF
        risk_color = (40, 167, 69) # Green for Mild
        if pred_label == "Moderate":
            risk_color = (255, 193, 7) # Yellow for Moderate
        elif pred_label == "Severe":
            risk_color = (220, 53, 69) # Red for Severe
        elif pred_label == "Profound":
            risk_color = (139, 0, 0) # Dark Red for Profound

        pdf.set_text_color(*risk_color) # Set text color
        pdf.cell(200, 10, txt=f"Predicted Risk Level: {pred_label}", ln=True)
        pdf.set_text_color(0, 0, 0) # Reset text color to black (default)

        pdf.ln(10) # Line break before note
        pdf.set_font("Arial", 'I', size=10) # Italic for the note
        pdf.multi_cell(0, 5, txt="(Assessment based on the EPDS - Edinburgh Postnatal Depression Scale, a globally validated tool)")
        
        # Add Personalized Tips to PDF
        pdf.ln(10)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(200, 10, txt="Personalized Tips:", ln=True)
        pdf.set_font("Arial", size=10)
        # Split tips by newline and add each as a new cell
        for tip_line in tips.get(pred_label, "Consult a professional immediately.").split('\n'):
            pdf.multi_cell(0, 5, txt=tip_line)
        pdf.ln(5)

        # Add questions and answers to PDF
        pdf.ln(10)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(200, 10, txt="Your Responses:", ln=True)
        pdf.set_font("Arial", size=10)
        for i, (q_text, options) in enumerate(q_responses):
            if i < len(q_values): # Ensure we don't go out of bounds for q_values
                selected_option_value = q_values[i]
                # Find the text of the selected option
                selected_option_text = next((k for k, v in options.items() if v == selected_option_value), "N/A")
                pdf.multi_cell(0, 5, txt=f"Q{i+1}: {q_text}\n   Your Answer: {selected_option_text} (Score: {selected_option_value})")
                pdf.ln(2) # Small space between questions
            else:
                # Fallback for missing answers (shouldn't happen with the `if len(q_values) != 10` check)
                pdf.multi_cell(0, 5, txt=f"Q{i+1}: {q_text}\n   Answer: Not provided")
                pdf.ln(2)

        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer, dest='S') # FIX: dest='S' to output to BytesIO object
        b64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{name}_PPD_Result.pdf">Download Result (PDF)</a>'
        st.markdown(href, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True) # Add some space
        if st.button("Restart Test", key="restart_test_button"):
            # Reset all relevant session state variables
            st.session_state.question_index = 0
            st.session_state.responses = []
            st.session_state.age = 25
            st.session_state.support = "Medium"
            st.session_state.name = ""
            st.session_state.place = ""
            st.session_state.feedback_submitted = False # Reset feedback flag
            st.session_state.page = "Home" # Redirect to home on restart
            st.rerun()

# RESULT EXPLANATION
elif menu == "Result Explanation":
    st.header("Understanding Risk Levels")
    st.info("All assessments in this app are based on the EPDS (Edinburgh Postnatal Depression Scale), a trusted and validated 10-question tool used worldwide to screen for postpartum depression.")
    st.markdown("""
    | Risk Level | Meaning |
    |------------|---------|
    | Mild       | Normal ups and downs, low risk of PPD. |
    | Moderate   | Requires monitoring; symptoms are noticeable but not severe. |
    | Severe     | Suggests possible clinical depression; professional assessment recommended. |
    | Profound   | Needs professional help urgently; symptoms are significant and impacting daily life. |
    """)
    st.markdown("<p class='custom-note'>The numerical values (0, 1, 2, 3) correspond to the categories 'Mild', 'Moderate', 'Severe', and 'Profound' respectively, as mapped by the model's output.</p>", unsafe_allow_html=True)


# FEEDBACK
elif menu == "Feedback":
    st.header("Share Your Feedback")
    # Only show the form if feedback hasn't just been submitted in this rerun
    if not st.session_state.feedback_submitted:
        feedback_name = st.text_input("Your Name (Optional)", key="feedback_name_input")
        feedback_message = st.text_area("Your Feedback", height=150, key="feedback_message_input")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Submit Feedback", key="submit_feedback_button"):
            if feedback_message.strip():
                st.success("Thank you for your valuable feedback! We appreciate your input.")
                st.session_state.feedback_submitted = True # Set flag after successful submission
                st.rerun() # Rerun to clear form and display success message
            else:
                st.warning("Please enter some feedback before submitting.")
    else:
        st.success("Your feedback has been submitted. Thank you!")
        # Offer a way to submit more feedback without navigating away
        if st.button("Submit More Feedback", key="submit_more_feedback"):
            st.session_state.feedback_submitted = False
            st.rerun()

# RESOURCES
elif menu == "Resources":
    st.header("Helpful Links and Support")
    st.markdown("""
    <div style="background-color: #1C2C5B; padding: 20px; border-radius: 10px; margin-bottom: 15px;">
        <h3>📞 National Mental Health Helpline (India)</h3>
        <p>For immediate support and counseling:</p>
        <p style="font-size: 1.2em; font-weight: bold; color: #E84C3D;">1800-599-0019</p>
        <a href="https://www.mohfw.gov.in" target="_blank" style="color: #17A2B8; text-decoration: none;">Visit MoHFW Website</a>
    </div>

    <div style="background-color: #1C2C5B; padding: 20px; border-radius: 10px; margin-bottom: 15px;">
        <h3>🌍 WHO Maternal Mental Health</h3>
        <p>Information and resources from the World Health Organization:</p>
        <a href="https://www.who.int/news-room/fact-sheets/detail/mental-health-of-women-during-pregnancy-and-after-childbirth" target="_blank" style="color: #17A2B8; text-decoration: none;">Learn more on WHO Website</a>
    </div>

    <div style="background-color: #1C2C5B; padding: 20px; border-radius: 10px; margin-bottom: 15px;">
        <h3>🤝 Postpartum Support International (PSI)</h3>
        <p>Dedicated to helping families worldwide recover from perinatal mood and anxiety disorders:</p>
        <a href="https://www.postpartum.net/" target="_blank" style="color: #17A2B8; text-decoration: none;">Visit Postpartum Support International</a>
    </div>
    """, unsafe_allow_html=True)
