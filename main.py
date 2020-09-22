from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import subprocess
import moviepy.editor as mp 
import speech_recognition as sr
import os
from os import path
import pydub
from pydub import AudioSegment
from pydub.silence import split_on_silence
from starlette.responses import FileResponse, RedirectResponse, Response
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import *
import requests
import json
# config.py is formatted as
# MY_ADDRESS =  "<an outlook email>"
# PASSWORD = "<outlook password>"

app = FastAPI()
app.mount(r'/static', StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="static")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

vid_file = r'./binary.mp4'
aud_file = r'./audio.mp3'
wav_file = r'./transcript.wav'
@app.post("/transcribe")
async def transcribe(request: Request, file: UploadFile = File(...), email: str = Form(...),  title: str = Form(...),  sentence_num: str = Form(...)):
    print("START")
    contents = await file.read()
    print("AFTER CONTENTS")
    with open(vid_file, 'wb') as wfile:
        wfile.write(contents)
    print("WROTE FILE")
    # Insert Local Video File Path  
    clip = mp.VideoFileClip(vid_file)
    print("CLIPPED")
    # Insert Local Audio File Path 
    clip.audio.write_audiofile(aud_file)
    print("CLIPPED AGAIN")

    sound = AudioSegment.from_file(aud_file, format='mp3')
    sound.export(wav_file, format="wav")
    print("GOT SOUND")
    text = get_large_audio_transcription(wav_file)
    print("\nFull text:", text)
    print("the email is: ", email)
    #email_user(email, text)
    summary = getSummarization(title,text,sentence_num)
    tags = getTags(text)    
    return templates.TemplateResponse('transcribe.html', context={'request':request, 'text':text, 'email':email, 'summary': summary, 'tags':tags})

@app.get("/transcribe", response_class=HTMLResponse)
async def transcribe(request: Request):
    text = 'sample text'
    email = 'sample@email.com'
    summary = 'meeting summary'
    tags = 'tags'
    return templates.TemplateResponse('transcribe.html', context={'request':request, 'text':text, 'email':email, 'summary': summary,'tags':tags})


def getSummarization(title, text, sentence_num):
    url = "https://aylien-text.p.rapidapi.com/summarize"
    querystring = {"title":title,"text":text,"sentences_number":sentence_num}
    headers = {
    'x-rapidapi-host':aylien,
    'x-rapidapi-key': aylien_key
    }
    response = json.loads(requests.request("GET", url, headers=headers, params=querystring).text)
    return response['sentences']

def getTags(text):
    url = "https://aylien-text.p.rapidapi.com/hashtags"
    querystring = {"text":text,"language":"en"}
    headers = {
    'x-rapidapi-host':aylien,
    'x-rapidapi-key': aylien_key
    }
    response = json.loads(requests.request("GET", url, headers=headers, params=querystring).text)
    return response['hashtags']

def email_user(email_address , transcript):
    email=email_address
    s = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)
    msg = MIMEMultipart()  
    msg['From']=MY_ADDRESS
    msg['To']=email
    msg['Subject']="Prtania meeting notes"

    # add in the message body
    message=transcript
    msg.attach(MIMEText(message, 'plain'))

    # send the message via the server set up earlier.
    s.send_message(msg)
    del msg

def get_large_audio_transcription(path):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    # open the audio file using pydub
    r = sr.Recognizer()
    sound = AudioSegment.from_wav(path)  
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 500,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                whole_text += text
    # return the text for all chunks detected
    return whole_text