import yt_dlp
import sys
import whisper
import requests
import json
import pyperclip
from gtts import gTTS
import os

def clear_link(link):
    if 'list' in link:
        return link.split('&list')[0]
    return link

# translating data
address="http://localhost:11434/api/generate"
languages = {
    "de": "jobautomation/openeurollm-german:latest",
    "en": "llama3:latest",
    "pl": "jobautomation/openeurollm-polish:latest"
}

if len(sys.argv) == 3 :
    from_language = sys.argv[1]
    to_language = sys.argv[2]
else:
    print("give 2 arguments")
    sys.exit()
    
languages_keys = (sys.argv[2])

if languages_keys not in languages:
    print("Unsupported language pair.")
    sys.exit()

if languages_keys in languages:
    modelTranslate=languages[languages_keys]


# downloading mp3 from youtube

url = pyperclip.paste()
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'mp3/source.%(ext)s',
    'overwrites': True,
    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }
    ],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([clear_link(url)])

# mp3 to text
model = whisper.load_model("large")
result = model.transcribe("mp3/source.mp3", language=from_language)
# print(result["text"]) prints original text from .mp3 in terminal

text = result["text"]

# translating
playload = {
    "model":modelTranslate,
    "prompt":f''' "You are a professional translator. I will provide the text, source language, and target language. Translate accurately, preserving the meaning, style, and context of the original. Do not add explanations or comments—provide only the translated text. TEXT: '{text}', TARGET LANGUAGE: '{to_language}', SOURCE LANGUAGE: '{from_language}'" ''',
    "stream":False
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(address, data=json.dumps(playload))
try:
    data = response.json()
    response_text = data.get("response")
    print(response_text) #prints the text translated in the terminal
except json.JSONDecodeError:
    print("Bug")
    print(response.text)

# translate text to mp3
if response_text and response_text.strip():
    tts = gTTS(response_text, lang=to_language)
    tts.save("mp3/output.mp3")
    os.system("start mp3/output.mp3")
else:
    print("There is no text to read!")
