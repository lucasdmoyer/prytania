# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
# account_sid = 'AC99c11c35fb5623c437c7d549f684069e'
# auth_token = '0055486e42edab20044c2f8906180f3d'
# client = Client(account_sid, auth_token)

# call = client.calls.create(
#                         url='http://demo.twilio.com/docs/voice.xml',
#                         to='+14252832729',
#                         from_='+12078257668'
#                     )

# print(call.sid)


import moviepy.editor as mp 
import speech_recognition as sr
import os
from os import path
import pydub
from pydub import AudioSegment
from pydub.silence import split_on_silence
# Insert Local Video File Path  
# clip = mp.VideoFileClip(r"./kawhi.mp4") 
  
# # Insert Local Audio File Path 
# clip.audio.write_audiofile(r"./audio.mp3") 

# convert mp3 file to wav         

sound = AudioSegment.from_file(r"C:\Users\moyer\OneDrive\development\prytania\test.mp3", format='mp3')
AUDIO_FILE = "./transcript.wav"
sound.export(AUDIO_FILE, format="wav")
# use the audio file as the audio source                                        
r = sr.Recognizer()
with sr.AudioFile(AUDIO_FILE) as source:
    audio = r.record(source)  # read the entire audio file                  
    # print("Transcription: " + r.recognize_google(audio))
    # set up the response object
    # response = {
    #     "success": True,
    #     "error": None,
    #     "transcription": None
    # }
    # # try recognizing the speech in the recording
    # # if a RequestError or UnknownValueError exception is caught,
    # #     update the response object accordingly
    # try:
    #     response["transcription"] = r.recognize_google(audio)
    # except sr.RequestError:
    #     # API was unreachable or unresponsive
    #     response["success"] = False
    #     response["error"] = "API unavailable"
    # except sr.UnknownValueError:
    #     # speech was unintelligible
    #     response["error"] = "Unable to recognize speech"
    # print(response)

def get_large_audio_transcription(path):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    # open the audio file using pydub
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

path = "transcript.wav"
print("\nFull text:", get_large_audio_transcription(path))