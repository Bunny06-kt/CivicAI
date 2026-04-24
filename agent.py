import json
import os
from unittest import result
from dotenv import load_dotenv

USE_AI = True

try:
    import google.generativeai as genai
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
except:
    USE_AI = False


# -----------------------------
# RULE-BASED INTENT (FAST + SAFE)
# -----------------------------
def rule_based_intent(user_input):
    text = user_input.lower()

    if "subsidy" in text or "सोलर" in text or "beku" in text:
        return "apply_scheme"

    if "track" in text or "status" in text:
        return "track_application"

    if "office" in text or "near" in text:
        return "nearest_office"

    return "general_query"


# -----------------------------
# OPTIONAL AI INTENT (MULTILINGUAL BOOST)
# -----------------------------
def ai_intent(user_input):
    if not USE_AI:
        return None

    prompt = f"""
Detect intent of user.

Return ONLY one word:
apply_scheme / track_application / nearest_office / general_query

Input: {user_input}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip().lower()
    except:
        return None


# -----------------------------
# FINAL INTENT DECISION
# -----------------------------
def get_intent(user_input):
    ai_result = ai_intent(user_input)

    if ai_result in ["apply_scheme", "track_application", "nearest_office"]:
        return ai_result

    return rule_based_intent(user_input)


# -----------------------------
# MULTILINGUAL RESPONSE (AI)
# -----------------------------
def translate_response(user_input, response_text):
    text = user_input.lower()

    # -----------------------------
    # LANGUAGE DETECTION
    # -----------------------------
    if any(char in text for char in "अआइईउऊएऐओऔ"):
        lang = "hindi"
    elif any(word in text for word in ["beku", "nanage", "illa", "ide"]):
        lang = "kannada"
    else:
        lang = "english"

    # -----------------------------
    # TRANSLATION MAP
    # -----------------------------
    translations = {
        "hindi": {
            "Your Solar Subsidy application is ready.": "आपका सोलर सब्सिडी आवेदन तैयार है।",
            "Your application is under review.": "आपका आवेदन समीक्षा में है।",
            "Nearest office is 2 km away.": "निकटतम कार्यालय 2 किमी दूर है।",
            "I can help you apply for schemes, track applications, and find nearby services.":
                "मैं योजनाओं के लिए आवेदन करने, आवेदन की स्थिति देखने और नजदीकी सेवाएं खोजने में मदद कर सकता हूँ।"
        },
        "kannada": {
            "Your Solar Subsidy application is ready.": "ನಿಮ್ಮ ಸೊಲಾರ್ ಸಬ್ಸಿಡಿ ಅರ್ಜಿ ಸಿದ್ಧವಾಗಿದೆ.",
            "Your application is under review.": "ನಿಮ್ಮ ಅರ್ಜಿ ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ.",
            "Nearest office is 2 km away.": "ಹತ್ತಿರದ ಕಚೇರಿ 2 ಕಿಮೀ ದೂರದಲ್ಲಿದೆ.",
            "I can help you apply for schemes, track applications, and find nearby services.":
                "ನಾನು ಯೋಜನೆಗಳಿಗೆ ಅರ್ಜಿ ಹಾಕಲು, ಅರ್ಜಿಯ ಸ್ಥಿತಿ ತಿಳಿಯಲು ಮತ್ತು ಹತ್ತಿರದ ಸೇವೆಗಳನ್ನು ಹುಡುಕಲು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ."
        }
    }

    # -----------------------------
    # RETURN TRANSLATED RESPONSE
    # -----------------------------
    if lang in translations and response_text in translations[lang]:
        return translations[lang][response_text]

    return response_text

# -----------------------------
# MAIN AGENT LOGIC
# -----------------------------
def agent(user_input):
    intent = get_intent(user_input)

    # APPLY SCHEME
    if intent == "apply_scheme":
        result = {
            "action": "autofill_form",
            "response": "Your Solar Subsidy application is shown.",
            "data": {
                "scheme": "Solar Subsidy",
                "documents_required": [
                    "Aadhaar Card",
                    "Electricity Bill",
                    "Bank Passbook",
                    "Income Certificate"
                ],
                "office_visits_required": "Minimum 1 visit",
                "form_fields": {
                    "name": "Demo User",
                    "income": "3 LPA",
                    "location": "Bangalore"
                }
            }
        }

    # TRACK
    elif intent == "track_application":
        result = {
            "action": "show_status",
            "response": "Your application is under review.",
            "data": {
                "status": "Under Review",
                "office_visits_required": "0–1 visits",
                "next_step": "Wait for approval"
            }
        }

    # OFFICE
    elif intent == "nearest_office":
        result = {
            "action": "provide_location",
            "response": "Nearest office is 2 km away.",
            "data": {
                "office": "Bangalore Civic Center",
                "timing": "10 AM - 5 PM",
                "office_visits_required": "1 visit"
            }
        }

    # DEFAULT
    else:
        result = {
            "action": "answer_query",
            "response": "I can help you apply for schemes, track applications, and find nearby services.",
            "data": {}
        }

    # Apply multilingual response
    result["response"] = translate_response(user_input, result)\
    
    return result
# -----------------------------
# TEST MODE
# -----------------------------
if __name__ == "__main__":
    print(" CivicAI Hybrid Agent (Multilingual + Safe)\n")

    while True:
        user_input = input("You: ") 
        if user_input.lower() in ["exit", "quit"]:
            break

        result = agent(user_input)

        print("\n Agent Output:")
        print(result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("\n" + "-" * 40)