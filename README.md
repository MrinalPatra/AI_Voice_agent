# AI Voice Agent

This is an AI-based voice agent that uses Google's Speech-to-Text, Text-to-Speech, and Gemini API to create an interactive voice assistant.

## Features

- Voice input using Google Speech-to-Text
- Voice output using Google Text-to-Speech
- AI responses using Google's Gemini API
- Role-based conversation
- Interactive voice interface

## Prerequisites

- Python 3.7 or higher
- Google API key for Gemini
- Microphone for voice input
- Speakers for voice output

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and add your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

1. Run the voice agent:
   ```bash
   python voice_bot.py
   ```
2. The agent will greet you and start listening for your voice input
3. Speak your query or command
4. The agent will process your input and respond through voice
5. To exit, say "quit", "exit", "bye", or "goodbye"

## Note

Make sure you have a working microphone and speakers connected to your system. The agent requires an internet connection to use Google's services. 