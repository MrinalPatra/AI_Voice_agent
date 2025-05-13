import os
import speech_recognition as sr
from gtts import gTTS
import openai
import pygame
import tempfile
import time
import sounddevice as sd
from scipy.io.wavfile import write
import io
from pygame import mixer

# Configure OpenAI API
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"  # Replace with your actual OpenAI API key
openai.api_key = OPENAI_API_KEY

# Role definition
ROLE = "I am an AI Financial Advisor that helps users with their financial questions and tasks."

class VoiceAgent:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.fs = 16000  # Sample rate
        self.duration = 10  # seconds
        
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
    
    def get_openai_response(self, user_input):
        """Get response from OpenAI model"""
        try:
            messages = [
                {"role": "system", "content": ROLE},
                {"role": "user", "content": user_input}
            ]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting response from OpenAI: {e}")
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
            
            # Get response from OpenAI
            response = self.get_openai_response(user_input)
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
