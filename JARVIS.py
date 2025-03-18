
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipedia
import requests
from bs4 import BeautifulSoup
import openai
import pyautogui
import sympy
import sqlite3
import pywhatkit
import os
import subprocess
import json
import smtplib
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# OpenAI API Key (GPT-4)
openai.api_key = "your_openai_api_key"

# Text-to-Speech Engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 150)

# Speech Recognition
r = sr.Recognizer()

# Database Setup
conn = sqlite3.connect("jarvis_memory.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS user_data (question TEXT, answer TEXT)''')
conn.commit()

# Function to Speak Text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to Recognize Speech
def recognize_speech():
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio, language='en')
        print(f"You said: {query}")
        return query.lower()
    except:
        return None

# Function to Greet User
def greet():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good Morning!")
    elif hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am JARVIS. How can I assist you?")

# AI Response (GPT-4)
def generate_response_gpt4(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response['choices'][0]['message']['content']
        cursor.execute("INSERT INTO user_data (question, answer) VALUES (?, ?)", (prompt, reply))
        conn.commit()
        return reply
    except:
        return "Sorry, I couldn't process that."

# Weather Function
def get_weather():
    url = 'https://www.google.com/search?q=weather'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    weather_info = soup.find('div', class_='BNeawe').text
    speak(f"Current weather: {weather_info}")

# News Function
def get_news():
    url = 'https://www.google.com/search?q=news'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    headlines = [headline.text for headline in soup.find_all('div', class_='BNeawe')]
    speak("Here are some news headlines:")
    for headline in headlines[:5]:
        speak(headline)

# Play Music
def play_music(query):
    query = query.replace("play", "").strip()
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)

# Calculate Math Expressions
def calculate(expression):
    try:
        result = eval(expression)
        speak(f"The result is {result}")
    except:
        speak("Sorry, I couldn't calculate that.")

# Solve Equations
def solve_equation(equation):
    try:
        x = sympy.symbols('x')
        expr = sympy.sympify(equation)
        solution = sympy.solve(expr, x)
        speak(f"The solution is {solution}")
    except:
        speak("Sorry, I couldn't solve the equation.")

# Scroll Functions
def scroll_down():
    pyautogui.scroll(-100)

def scroll_up():
    pyautogui.scroll(100)

# Wikipedia Search
def search_wikipedia(query):
    try:
        results = wikipedia.summary(query, sentences=2)
        speak(f"According to Wikipedia: {results}")
    except:
        speak("Sorry, no information found.")

# Control Smart Devices (IFTTT)
def control_device(device_name, action):
    url = f"https://maker.ifttt.com/trigger/{device_name}/with/key/YOUR_IFTTT_KEY"
    payload = json.dumps({"action": action})
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        speak(f"{device_name} {action}ed successfully.")
    else:
        speak("An error occurred while controlling the device.")

# WhatsApp Message Sending
def send_whatsapp_message(contact, message):
    pywhatkit.sendwhatmsg_instantly(contact, message)
    speak("Message sent successfully.")

# Call Function (Using WhatsApp)
def make_call(contact):
    try:
        pywhatkit.sendwhatmsg_instantly(contact, "Hello! Calling you now.")
        speak(f"Calling {contact} on WhatsApp.")
    except:
        speak("Sorry, I couldn't make the call.")

# Email Sending
def send_email(to_email, subject, body):
    try:
        sender_email = "your_email@gmail.com"
        sender_password = "your_password"

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(sender_email, to_email, message)
        server.quit()

        speak("Email sent successfully.")
    except:
        speak("Sorry, I couldn't send the email.")

# Find and Launch an App
def find_and_launch_app(query):
    app_name = query.replace("open", "").strip()
    try:
        if os.name == "nt":
            subprocess.run(f"start {app_name}", shell=True)
        elif os.name == "posix":
            subprocess.run(f"open -a {app_name}", shell=True)
        speak(f"Opening {app_name}")
    except:
        speak(f"Sorry, I couldn't find {app_name}.")

# API for Flask (Android/WebView)
@app.route('/jarvis', methods=['POST'])
def jarvis_api():
    user_query = request.json.get("query")
    response = generate_response_gpt4(user_query)
    return jsonify({"response": response})

# Main Function
def main():
    greet()
    while True:
        query = recognize_speech()
        if query is None:
            continue

        if "hello" in query:
            speak("Hello! How can I assist you?")

        elif "open browser" in query:
            webbrowser.open('https://www.google.com')

        elif "search wikipedia" in query:
            speak("What do you want to search for?")
            search_query = recognize_speech()
            if search_query:
                search_wikipedia(search_query)

        elif "weather" in query:
            get_weather()

        elif "news" in query:
            get_news()

        elif "play music" in query:
            speak("Which song?")
            song_query = recognize_speech()
            if song_query:
                play_music(song_query)

        elif "calculate" in query:
            speak("Say the mathematical expression.")
            expression = recognize_speech()
            if expression:
                calculate(expression)

        elif "scroll down" in query:
            scroll_down()

        elif "scroll up" in query:
            scroll_up()

        elif "call" in query:
            speak("Who do you want to call?")
            contact = recognize_speech()
            if contact:
                make_call(contact)

        elif "email" in query:
            speak("Who do you want to send an email to?")
            recipient = recognize_speech()
            speak("What is the subject?")
            subject = recognize_speech()
            speak("What should I write in the email?")
            body = recognize_speech()
            if recipient and subject and body:
                send_email(recipient, subject, body)

        elif "exit" in query or "stop" in query:
            speak("Goodbye! Have a great day.")
            break

if __name__ == "__main__":
    main()
