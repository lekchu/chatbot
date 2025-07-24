import random
import os
import requests
import json

# --- Configuration for LLM (Large Language Model) Integration ---
# Choose your LLM provider. Uncomment and configure the one you want to use.
# For Google Gemini API, you'll need `pip install google-generativeai`
# For OpenAI API, you'll need `pip install openai`
# For Hugging Face Inference API, you'll need `pip install requests`

# Set to True if you want to use an LLM, False to use rule-based fallback
USE_LLM = False 

# --- Google Gemini API Configuration (Example) ---
# import google.generativeai as genai
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # Store your API key securely in Streamlit secrets or environment variables
# if GOOGLE_API_KEY and USE_LLM:
#     genai.configure(api_key=GOOGLE_API_KEY)
#     GEMINI_MODEL = genai.GenerativeModel('gemini-pro')

# --- OpenAI API Configuration (Example) ---
# from openai import OpenAI
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Store your API key securely
# if OPENAI_API_KEY and USE_LLM:
#     OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)

# --- Hugging Face Inference API Configuration (Example) ---
# HF_API_TOKEN = os.getenv("HF_API_TOKEN") # Store your API token securely
# HF_MODEL_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium" # Example model
# HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}

def get_llm_response(chat_history):
    """
    Placeholder function to integrate with an external Large Language Model (LLM) API.
    
    Args:
        chat_history (list of tuples): List of (sender, message) pairs for context.
                                      Example: [("user", "Hi"), ("momly", "Hello!")]
    Returns:
        str: Response from the LLM, or None if LLM is not configured/fails.
    """
    if not USE_LLM:
        return None

    # --- Implement your chosen LLM integration here ---
    
    # Example: Google Gemini API (uncomment and configure if using)
    # if GOOGLE_API_KEY:
    #     try:
    #         # Format chat history for Gemini's multi-turn conversational model
    #         # Gemini roles are 'user' and 'model'
    #         gemini_history = []
    #         for sender, message in chat_history:
    #             if sender == "user":
    #                 gemini_history.append({"role": "user", "parts": [message]})
    #             elif sender == "momly": # MOMLY acts as the model
    #                 gemini_history.append({"role": "model", "parts": [message]})
    #         
    #         response = GEMINI_MODEL.generate_content(gemini_history)
    #         return response.text
    #     except Exception as e:
    #         print(f"Gemini API Error: {e}")
    #         return None

    # Example: OpenAI API (uncomment and configure if using)
    # if OPENAI_API_KEY:
    #     try:
    #         messages = [{"role": "system", "content": "You are MOMLY, a gentle, supportive chatbot for new mothers, focusing on well-being and postpartum mental health. Offer empathy, practical tips, and resources. Keep responses concise and caring."}]
    #         for sender, message in chat_history:
    #             if sender == "user":
    #                 messages.append({"role": "user", "content": message})
    #             elif sender == "momly":
    #                 messages.append({"role": "assistant", "content": message})
    #         
    #         chat_completion = OPENAI_CLIENT.chat.completions.create(
    #             model="gpt-3.5-turbo", # or "gpt-4" if you have access
    #             messages=messages
    #         )
    #         return chat_completion.choices[0].message.content
    #     except Exception as e:
    #         print(f"OpenAI API Error: {e}")
    #         return None

    # Example: Hugging Face Inference API (uncomment and configure if using)
    # if HF_API_TOKEN and HF_MODEL_URL:
    #     try:
    #         # For DialoGPT-medium, simply pass the last user message
    #         last_user_message = next((msg for sender, msg in reversed(chat_history) if sender == "user"), "")
    #         payload = {"inputs": last_user_message}
    #         response = requests.post(HF_MODEL_URL, headers=HEADERS, json=payload)
    #         response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
    #         result = response.json()
    #         if isinstance(result, list) and result and 'generated_text' in result[0]:
    #             return result[0]['generated_text']
    #         return None
    #     except Exception as e:
    #         print(f"Hugging Face API Error: {e}")
    #         return None

    return None # If no LLM configured or API call fails

def get_momly_reply(user_message, chat_history):
    """
    Generates a response from MOMLY.
    Prioritizes LLM response if USE_LLM is True and LLM integration is successful.
    Falls back to a more intelligent rule-based system otherwise.
    
    Args:
        user_message (str): The user's input message.
        chat_history (list): The full conversation history for context.
    Returns:
        str: MOMLY's response.
    """
    # 1. Try to get a response from the LLM if enabled
    if USE_LLM:
        llm_response = get_llm_response(chat_history)
        if llm_response:
            return llm_response

    # 2. Fallback to enhanced rule-based system if LLM is not used or fails
    msg = user_message.lower()

    # Keywords for urgent help (always prioritize these)
    if any(word in msg for word in ["help", "emergency", "crisis", "harm", "suicide", "end my life"]):
        return "If you are in immediate danger or need urgent support, please contact a trusted person, a mental health helpline, or emergency services immediately. You are loved and help is available. ❤️ **National Helpline (India): 1800-599-0019**"

    # Keywords for sad/negative emotions
    if any(word in msg for word in ["sad", "tired", "lonely", "anxious", "depressed", "down", "overwhelmed", "struggling", "bad", "stressed"]):
        return random.choice([
            "I hear you, mama. It sounds like you're carrying a lot right now. You're not alone — take a deep breath with me 🌷",
            "These feelings are valid, and I'm here to listen without judgment 💛. Remember, it's okay not to be okay.",
            "Would you like to try a calming breathing exercise together, or perhaps a soothing sound/video?",
            "It's okay to feel this way. Remember to be kind to yourself. What's one small thing you could do for yourself right now?",
            "Sending you a warm hug. Sometimes just acknowledging these feelings can be a step forward. How long have you been feeling this way?",
            "It sounds challenging. Is there anything specific on your mind that's contributing to this feeling?"
        ])
    # Keywords for positive emotions
    elif any(word in msg for word in ["happy", "better", "relaxed", "good", "great", "well", "positive", "fine", "okay"]):
        return random.choice([
            "That’s beautiful to hear! Your strength shines through ✨. What made you feel good today?",
            "So glad to hear that 🌼! Want a gentle journal prompt to reflect on this positive feeling?",
            "It warms my heart to know you're feeling positive! Keep that energy going. You deserve all the good things.",
            "Wonderful! Every little bit of joy matters. Is there anything you'd like to celebrate, no matter how small?"
        ])
    # Keywords for activity suggestions
    elif any(word in msg for word in ["activity", "do", "distract", "idea", "suggestions", "what should i do"]):
        return random.choice([
            "How about a 5-minute mindfulness exercise, a quick doodle, or a gentle stretch? 🌿",
            "You could try listening to some calming music, or perhaps writing down 3 things you're grateful for.",
            "Maybe a short walk outside to get some fresh air, or engaging in a simple hobby you enjoy?"
        ])
    # Keywords for video
    elif any(word in msg for word in ["video", "watch", "show me a video", "calming video"]):
        # Replace with a real calming video link if you have one
        return "Here's a calming video for you, mama: [Relax Video](https://www.youtube.com/watch?v=1FwX1V5tqQY) 🎥"
    # Keywords for sleep
    elif any(word in msg for word in ["sleep", "tired", "insomnia", "rest"]):
        return random.choice([
            "Sleep can be so challenging with a new baby. Have you tried a warm bath before bed, or a quiet meditation?",
            "It's hard when sleep eludes you. Even short rests can help. Remember, you're doing amazing.",
            "Perhaps a cup of chamomile tea or some gentle stretching could help you wind down before trying to sleep."
        ])
    # Keywords for baby care/challenges
    elif any(word in msg for word in ["baby", "feeding", "crying", "newborn", "motherhood", "mom"]):
        return random.choice([
            "Motherhood is a journey with its ups and downs. Remember to be patient and kind to yourself.",
            "It's completely normal to feel overwhelmed with a new baby. You're doing a great job.",
            "Remember, a fed baby is best. Don't stress too much about the 'how'. You've got this!",
            "Crying is tough. It's okay to put your baby down safely for a few minutes and take a breather if you need to."
        ])
    # Keywords for affirmations/encouragement
    elif any(word in msg for word in ["affirmation", "encourage", "inspire", "positive words"]):
        return random.choice([
            "You are doing enough. You are a good mother. You are loved. 💖",
            "This season of life is temporary, and you are strong enough to navigate it. ✨",
            "Be gentle with yourself. You are learning and growing every single day."
        ])
    # General responses (catch-all)
    else:
        return random.choice([
            "I'm here to listen, mama 🌷. Tell me more about what's on your mind.",
            "You're doing great, remember that 💖. What else would you like to talk about?",
            "How can I support you right now?",
            "Sometimes just sharing helps. What's one thing you're thinking about?",
            "I'm here for you, no matter what you want to talk about."
        ])
