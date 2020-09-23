# import io
# import os



# # curl -X POST -u "apikey:zFhfoOCtPEdcbv6X5vSmN8t0ozvy7qrOAkwVeYB61RON" ^
# # --header "Content-Type: audio/flac" ^
# # --data-binary @C:\Users\moyer\OneDrive\development\prytaniaaudio-file.flac ^
# # "https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/aa65b72c-fa84-4d17-95c6-800c00543716/v1/recognize"

# creds = {
#   "apikey": "zFhfoOCtPEdcbv6X5vSmN8t0ozvy7qrOAkwVeYB61RON",
#   "iam_apikey_description": "Auto-generated for key 7a826bed-868a-43a0-b309-596ef4c1f8ac",
#   "iam_apikey_name": "Auto-generated service credentials",
#   "iam_role_crn": "crn:v1:bluemix:public:iam::::serviceRole:Manager",
#   "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::a/683cc353730f438783afabc5e049572f::serviceid:ServiceId-9eba6efe-0603-4d53-900d-3fdbbf4712c8",
#   "url": "https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/aa65b72c-fa84-4d17-95c6-800c00543716"
# }

# from ibm_watson import SpeechToTextV1
# from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
# from os.path import join, dirname
# from ibm_watson.websocket import RecognizeCallback, AudioSource
# import json
# authenticator = IAMAuthenticator(creds['apikey'])
# speech_to_text = SpeechToTextV1(
#     authenticator=authenticator
# )

# speech_to_text.set_service_url(creds['url'])

# from ibm_watson import ApiException
# # try:
# #     # Invoke a Speech to Text method
# # except ApiException as ex:
# #     print "Method failed with status code " + str(ex.code) + ": " + ex.message

# class MyRecognizeCallback(RecognizeCallback):
#     def __init__(self):
#         RecognizeCallback.__init__(self)

#     def on_data(self, data):
#         print(json.dumps(data, indent=2))

#     def on_error(self, error):
#         print('Error received: {}'.format(error))

#     def on_inactivity_timeout(self, error):
#         print('Inactivity timeout: {}'.format(error))

# myRecognizeCallback = MyRecognizeCallback()

# # audio types
# # aduio/mp3
# # audio/wav

# with open(join(dirname(__file__), './.', 'short.wav'),
#               'rb') as audio_file:
#     audio_source = AudioSource(audio_file)
#     speech_to_text.recognize_using_websocket(
#         audio=audio_source,
#         content_type='audio/wav',
#         recognize_callback=myRecognizeCallback,
#         model='en-US_BroadbandModel',
#         keywords=['colorado', 'tornado', 'tornadoes'],
#         keywords_threshold=0.5,
#         max_alternatives=3,
#         speaker_labels=True,
#         inactivity_timeout=-1)


import requests
import json
def getSummarization(title, text, sentence_num):
    url = "https://aylien-text.p.rapidapi.com/summarize"
    querystring = {"title":title,"text":text,"sentences_number":sentence_num}
    headers = {
    'x-rapidapi-host': "aylien-text.p.rapidapi.com",
    'x-rapidapi-key': "B8VlALjFnYmsh2N4csJcqG44pXj9p1iP5UljsnJvpKGSaq38Dj"
    }
    response = json.loads(requests.request("GET", url, headers=headers, params=querystring).text)
    return response['sentences']

getSummarization('hello', 'hi', '2')