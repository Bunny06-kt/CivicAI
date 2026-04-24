import os
import random
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# -----------------------------
# CACHE (in-memory)
# -----------------------------
CACHE = {}

# -----------------------------
# LANGUAGE DETECTION
# -----------------------------
def detect_language(text):
    if any('\u0900' <= ch <= '\u097F' for ch in text):
        return "hindi"
    if any('\u0C80' <= ch <= '\u0CFF' for ch in text):
        return "kannada"
    if any(word in text.lower() for word in ["beku", "nanage"]):
        return "kannada"
    return "english"

# -----------------------------
# UNCLEAR DETECTION
# -----------------------------
def is_unclear(text):
    if not text or len(text.split()) <= 2:
        return True
    if any(w in text.lower() for w in ["uh", "hmm", "aaa"]):
        return True
    return False

# -----------------------------
# INTENT
# -----------------------------
def get_intent(text):
    text = text.lower()

    if "सब्सिडी" in text or "beku" in text:
        return "apply_scheme"

    if "track" in text or "status" in text:
        return "track_application"

    if "office" in text or "near" in text:
        return "nearest_office"

    return "general_query"

# -----------------------------
# GEMINI CALL (OPTIMIZED)
# -----------------------------
def call_llm(user_input):
    # CACHE CHECK
    if user_input in CACHE:
        return CACHE[user_input]

    try:
        model = genai.GenerativeModel("gemini-pro")

        prompt = f"""
        Answer briefly (1-2 lines max).
        Be clear and helpful.

        User: {user_input}
        """

        response = model.generate_content(prompt)
        text = response.text.strip()

        # STORE IN CACHE
        CACHE[user_input] = text

        return text

    except Exception:
        return "Sorry, I couldn't process that right now."

# -----------------------------
# TRANSLATION
# -----------------------------
def translate(user_input, intent, default):
    lang = detect_language(user_input)

    translations = {
        "hindi": {
            "apply_scheme": "आपका आवेदन तैयार है — कार्यालय जाने की आवश्यकता नहीं।",
            "track_application": "आपका आवेदन समीक्षा में है।",
            "nearest_office": "निकटतम कार्यालय पास में है।",
            "smart_autofill": "भाषा स्पष्ट नहीं है। स्मार्ट ऑटोफिल किया जा रहा है।"
        },
        "kannada": {
            "apply_scheme": "ನಿಮ್ಮ ಅರ್ಜಿ ಸಿದ್ಧವಾಗಿದೆ — ಕಚೇರಿ ಭೇಟಿ ಅಗತ್ಯವಿಲ್ಲ.",
            "track_application": "ನಿಮ್ಮ ಅರ್ಜಿ ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ.",
            "nearest_office": "ಹತ್ತಿರದ ಕಚೇರಿ ಲಭ್ಯವಿದೆ.",
            "smart_autofill": "ಭಾಷೆ ಸ್ಪಷ್ಟವಾಗಿಲ್ಲ. ಸ್ಮಾರ್ಟ್ ಸ್ವಯಂ ಭರ್ತಿ ಮಾಡಲಾಗುತ್ತಿದೆ."
        }
    }

    return translations.get(lang, {}).get(intent, default)

# -----------------------------
# MAIN AGENT
# -----------------------------
def agent(user_input):

    # Smart fallback trigger
    if is_unclear(user_input):
        intent = "smart_autofill"
    else:
        intent = get_intent(user_input)

    # -------------------------
    if intent == "apply_scheme":
        response = "Your application is ready."
        data = {"source": "rule_based"}

    elif intent == "track_application":
        response = "Your application is under review."
        data = {"source": "rule_based"}

    elif intent == "nearest_office":
        response = "Nearest office is nearby."
        data = {"source": "rule_based"}

    elif intent == "smart_autofill":
        response = "Language unclear. Proceeding with smart autofill."
        data = {"source": "rule_based"}

    else:
        #  ONLY HERE WE CALL LLM
        response = call_llm(user_input)
        data = {"source": "gemini_llm"}

    # Translation layer
    response = translate(user_input, intent, response)

    return {
        "intent": intent,
        "response": response,
        "data": data
    }