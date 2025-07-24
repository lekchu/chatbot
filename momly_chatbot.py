import random

# Knowledge base grouped by maternal topics
knowledge_base = {
    "breastfeeding": [
        "Newborns often feed every 2–3 hours. Look for cues like rooting or sucking 💕",
        "Try to alternate sides and stay hydrated, mama! You're doing amazing 💖"
    ],
    "postpartum depression": [
        "It's okay to feel overwhelmed. You're not alone 💗 Let’s talk through it.",
        "If the sadness lasts beyond 2 weeks, consider talking to a professional. I’m here too 🌷"
    ],
    "baby sleep": [
        "Try swaddling, white noise, and keeping a consistent bedtime routine 💤",
        "It's normal for newborns to wake often. Rest when you can, mama 💜"
    ],
    "self care": [
        "You deserve time to breathe. Even 5 quiet minutes can help 🌿",
        "Ask for help when needed — it’s a sign of strength, not weakness 💪"
    ],
    "crying baby": [
        "Babies cry for many reasons: hunger, gas, tiredness, or just needing a cuddle 🤱",
        "Try skin-to-skin contact or gentle rocking. You're doing beautifully 💞"
    ],
    "default": [
        "I'm still learning, mama 🌈 Could you tell me more?",
        "Hmm, can you say that a bit differently? I’m here for you 💗"
    ]
}

# Keyword-based intent detection
intent_keywords = {
    "breastfeeding": ["breastfeed", "latch", "milk", "nursing", "feed"],
    "postpartum depression": ["sad", "depressed", "low", "crying", "blue", "mood"],
    "baby sleep": ["sleep", "nap", "night", "awake", "bedtime"],
    "self care": ["self", "tired", "me time", "burnout", "stress"],
    "crying baby": ["cry", "fussy", "colic", "scream", "irritated"],
}

def get_intent(message):
    msg = message.lower()
    for intent, keywords in intent_keywords.items():
        if any(word in msg for word in keywords):
            return intent
    return "default"

def momly_response(message):
    intent = get_intent(message)
    responses = knowledge_base.get(intent, knowledge_base["default"])
    return random.choice(responses)
