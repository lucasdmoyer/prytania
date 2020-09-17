from fastapi import FastAPI, File, UploadFile
import subprocess
import moviepy.editor as mp 
import speech_recognition as sr
import os
from os import path
import pydub
from pydub import AudioSegment
from pydub.silence import split_on_silence
from starlette.responses import FileResponse
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

vid_file = r'./binary.mp4'
aud_file = r'./audio.mp3'
wav_file = r'./transcript.wav'
@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
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
    return {"text": text}


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