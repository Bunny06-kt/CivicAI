import speech_recognition as sr
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import win32com.client
from agent import agent

# -----------------------------
# TTS (VOICE OUTPUT)
# -----------------------------
speaker = win32com.client.Dispatch("SAPI.SpVoice")

def speak(text):
    print("🔊 Bot:", text)
    speaker.Speak(text)


# -----------------------------
# VOICE INPUT (SIMPLE)
# -----------------------------
def voice_input():
    fs = 16000
    duration = 3

    print("\n🎤 Speak now (or wait for fallback)...")

    try:
        recording = sd.rec(int(duration * fs),
                           samplerate=fs,
                           channels=1,
                           dtype='float32')

        sd.wait()

        recording = np.int16(recording * 32767)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        write(temp_file.name, fs, recording)

        recognizer = sr.Recognizer()

        with sr.AudioFile(temp_file.name) as source:
            audio = recognizer.record(source)

        try:
            try:
                text = recognizer.recognize_google(audio, language="kn-IN")
            except:
                try:
                    text = recognizer.recognize_google(audio, language="hi-IN")
                except:
                    text = recognizer.recognize_google(audio, language="en-IN")

            print("🗣 Voice Input:", text)
            return text

        except:
            print("⚠️ Voice not clear")
            return None

    except:
        print("⚠️ Microphone error")
        return None


# -----------------------------
# SAFE INPUT (VOICE + TEXT FALLBACK)
# -----------------------------
def get_input():
    text = voice_input()

    if text:
        return text

    # 🔥 FALLBACK MODE
    print("⌨️ Switching to text input...")
    return input("Type your query: ")


# -----------------------------
# MAIN DEMO LOOP
# -----------------------------
if __name__ == "__main__":
    print("🚀 CivicAI Hackathon Demo (Hybrid Safe Mode)\n")

    while True:
        user_input = get_input()

        if user_input.lower() in ["exit", "quit"]:
            speak("Goodbye")
            break

        result = agent(user_input)

        print("\n🤖 OUTPUT:")
        print(result)

        reply = result.get("message") or result.get("response") or "OK"

        speak(reply)

        print("-" * 40)