import pyttsx3
import speech_recognition as sr
import threading
from typing import Optional, Callable
import time

class VoiceEngine:
    """Handles Text-to-Speech (TTS) and Speech-to-Text (STT) for the assessment"""
    
    def __init__(self):
        # Initialize TTS engine
        try:
            self.engine = pyttsx3.init()
            # Set properties
            self.engine.setProperty('rate', 150)    # Speed percent (can go over 100)
            self.engine.setProperty('volume', 0.9)  # Volume 0-1
            # Initializing voices
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer a female voice for empathy (if available)
                for voice in voices:
                    if "female" in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
        except Exception as e:
            print(f"Error initializing TTS engine: {e}")
            self.engine = None

        # STT Recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def speak(self, text: str, emotion: str = 'neutral'):
        """Read text aloud with empathetic prosody (simulated)"""
        if not self.engine:
            return
            
        def _speak():
            try:
                # Create a new engine instance for the thread
                local_engine = pyttsx3.init()
                
                # Adjust prosody based on emotion
                if emotion == 'supportive':
                    local_engine.setProperty('rate', 130) # Slower, calmer
                    local_engine.setProperty('volume', 0.8)
                elif emotion == 'urgent':
                    local_engine.setProperty('rate', 180) # Faster
                    local_engine.setProperty('volume', 1.0)
                
                local_engine.say(text)
                local_engine.runAndWait()
            except Exception as e:
                print(f"TTS Thread Error: {e}")

        threading.Thread(target=_speak, daemon=True).start()

    def analyze_tone(self, text: str) -> str:
        """
        Simulate emotion/tone detection from voice/text.
        Detects anxiety, confusion, or confidence.
        """
        confused_keywords = ['um', 'uh', 'dont know', 'not sure', 'wait']
        anxious_keywords = ['help', 'fast', 'hard', 'cant']
        
        text_lower = text.lower()
        if any(w in text_lower for w in confused_keywords):
            return 'confused'
        if any(w in text_lower for w in anxious_keywords):
            return 'anxious'
        return 'confident'

    def listen(self, timeout: int = 5, phrase_time_limit: int = 5) -> Optional[str]:
        """Listen for speech and return transcribed text"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return "[Unintelligible]"
        except Exception as e:
            print(f"STT Error: {e}")
            return f"[Error: {str(e)}]"

    def analyze_voice_biomarkers(self, audio_data) -> dict:
        """
        Placeholder for phonatory analysis (intonation, jitter, shimmer, pauses)
        Would use librosa in a full implementation.
        """
        return {
            'mean_pitch': 110.5,
            'jitter': 0.02,
            'shimmer': 0.05,
            'pause_frequency': 0.2, # pauses per word
            'speech_rate': 120    # words per minute
        }
