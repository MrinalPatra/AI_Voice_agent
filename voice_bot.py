import os
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai
import pygame
import tempfile
import time
import sounddevice as sd
from scipy.io.wavfile import write
import io
from pygame import mixer

# Configure Gemini API
GOOGLE_API_KEY = "your-Gemini-api-key"  # Replace with your actual API key
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.5-pro-preview-05-06')

# Role definition
ROLE = "I am an AI assistant that helps users with their questions and tasks. I am friendly, knowledgeable, and always ready to assist."

class VoiceAgent:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.fs = 16000  # Sample rate
        self.duration = 5  # seconds
        
    def speak(self, text):
        """Convert text to speech and play it"""
        try:
            # Create TTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to a bytes buffer instead of a file
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            buffer.seek(0)
            
            # Load and play directly from buffer
            pygame.mixer.music.load(buffer)
            pygame.mixer.music.play()
            
            # Wait for audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Clean up
            pygame.mixer.music.unload()
            buffer.close()
            
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
            print("Text that failed to convert:", text)
    
    def listen(self):
        """Listen to user's voice input and convert to text"""
        print(f"Please speak now (recording for {self.duration} seconds)...")
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_wav.close()
        try:
            recording = sd.rec(int(self.duration * self.fs), samplerate=self.fs, channels=1, dtype='int16')
            sd.wait()  # Wait until recording is finished
            write(temp_wav.name, self.fs, recording)
            
            # Add a small delay to ensure file is written
            time.sleep(0.1)
            
            with sr.AudioFile(temp_wav.name) as source:
                audio = self.recognizer.record(source)
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"You said: {text}")
                    return text
                except sr.UnknownValueError:
                    print("Sorry, I couldn't understand that.")
                except sr.RequestError:
                    print("Sorry, there was an error with the speech recognition service.")
        except Exception as e:
            print(f"Error recording audio: {e}")
        finally:
            # Add a small delay before deletion
            time.sleep(0.1)
            try:
                if os.path.exists(temp_wav.name):
                    os.unlink(temp_wav.name)
            except Exception as e:
                print(f"Warning: Could not delete temporary file: {e}")
        return None
    
    def get_gemini_response(self, user_input):
        """Get response from Gemini model"""
        try:
            prompt = f"{ROLE}\nUser: {user_input}\nAssistant:"
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error getting response from Gemini: {e}")
            return "I apologize, but I'm having trouble generating a response right now."
    
    def run(self):
        """Main loop for the voice agent"""
        # Initial greeting
        greeting = f"Hello! {ROLE} How can I help you today?"
        print(greeting)
        self.speak(greeting)
        
        while True:
            # Listen for user input
            user_input = self.listen()
            if user_input is None:
                continue
            
            # Get response from Gemini
            response = self.get_gemini_response(user_input)
            print(f"AI: {response}")
            
            # Speak the response
            self.speak(response)
            
            # Check if user wants to end the conversation
            if "goodbye" in user_input.lower() or "bye" in user_input.lower():
                farewell = "Goodbye! Have a great day!"
                print(farewell)
                self.speak(farewell)
                break

if __name__ == "__main__":
    agent = VoiceAgent()
    agent.run()
