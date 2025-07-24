import random

# --- MOMLY Knowledge Base ---
knowledge_base = {
    "breastfeeding": [
        "It's normal to feed every 2-3 hours. Watch for rooting or sucking cues 💕",
        "Stay hydrated and try to alternate sides while nursing. You're doing amazing 💖"
    ],
    "baby sleep": [
        "Try swaddling, white noise, or gentle rocking to help baby rest 💤",
        "Newborns wake often. Even small naps can help you recharge 💜"
    ],
    "postpartum sadness": [
        "You're not alone, mama. Postpartum feelings are common and treatable 💗",
        "Let’s take a deep breath together. Would you like some calming activities? 🌿"
    ],
    "self care": [
        "Taking care of yourself is part of caring for your baby 💆‍♀️",
        "Even 10 minutes of rest or a walk can lift your mood 🌞"
    ],
    "activities": [
        "How about a short walk, journaling, or playing soft music? 🎶",
        "Try drawing, stretching, or simply closing your eyes for a moment 💫"
    ],
    "default": [
        "I'm here to listen, mama. Could you share more? 💬",
        "Let’s get through this together. Tell me how you're feeling 💖"
    ]
}

# --- Simple Keyword Intent Map ---
intent_keywords = {
    "breastfeeding": ["breastfeed", "milk", "latch", "feeding"],
    "baby sleep": ["sleep", "awake", "night", "bedtime", "nap"],
    "postpartum sadness": ["sad", "cry", "depressed", "unhappy", "blue"],
    "self care": ["tired", "burnout", "rest", "me time", "self care"],
    "activities": ["activity", "suggest", "what to do", "relax", "fun"]
}

# --- Intent Detection ---
def detect_intent(user_input):
    msg = user_input.lower()
    for intent, keywords in intent_keywords.items():
        if any(word in msg for word in keywords):
            return intent
    return "default"

# --- MOMLY Response Generator ---
def momly_response(user_input):
    intent = detect_intent(user_input)
    response_list = knowledge_base.get(intent, knowledge_base["default"])
    return random.choice(response_list)
