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

@app.post("/transcribe_jumper")
async def transcribe_jumper(request: Request, file: UploadFile = File(...)):

    print("START")
    contents = await file.read()
    with open(vid_file, 'wb') as wfile:
        wfile.write(contents)
    # Insert Local Video File Path
    clip = mp.VideoFileClip(vid_file)
    # Insert Local Audio File Path
    clip.audio.write_audiofile(aud_file)

    sound = AudioSegment.from_file(aud_file, format='mp3')
    sound.export(wav_file, format="wav")
    text = get_large_audio_transcription(wav_file)

    html_content = ""

    for item in text:
        html_content += "<button onclick=\"jump({})\">".format(item[1]) + item[0] + "</button>"

    return templates.TemplateResponse("process.html", {"finished": html_content, "request": request})


@app.post("/transcribe")
async def transcribe(request: Request, file: UploadFile = File(...), email: str = Form(...),  title: str = Form(...),  sentence_num: str = Form(...)):
    print("START")
    contents = await file.read()
    with open(vid_file, 'wb') as wfile:
        wfile.write(contents)
    # Insert Local Video File Path
    clip = mp.VideoFileClip(vid_file)
    # Insert Local Audio File Path
    clip.audio.write_audiofile(aud_file)

    sound = AudioSegment.from_file(aud_file, format='mp3')
    sound.export(wav_file, format="wav")
    text = get_large_audio_transcription(wav_file)
    print("\nFull text:", text)

    # html_content = ""
    #
    # for item in text:
    #     html_content += "<button onclick=\"jump({})\">".format(item[1]) + item[0] + "</button>"

    print("the email is: ", email)
    #email_user(email, text)
    summary = getSummarization(title,text[:500],sentence_num)
    tags = getTags(text[:500])
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
    'x-rapidapi-host': aylien,
    'x-rapidapi-key': aylien_key
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    try:
        return_response = response.json()
    except:
        print(response.text)
        return_response = {"sentences": "sample text here"}
    return return_response['sentences']

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

def get_large_audio_transcription(path, chunked=False):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    # Start Stop is a list of lists containing the start and stop time for audio chunks and transcription outputs
    start_stops = []
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
    start = 0
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")

        time_elapsed = audio_chunk.duration_seconds
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
                start_stops.append(["**undiscernable**", start])
                start = start + time_elapsed
            else:
                text = f"{text.capitalize()}. "
                #print(chunk_filename, ":", text)
                print("Text\n{}\n-----".format(text))
                whole_text += text
                start_stops.append([text, start])
                start = start + time_elapsed
    # return the text for all chunks detected
    print("finished")
    if chunked:
        return start_stops
    else:
        return whole_text
