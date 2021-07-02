from google.cloud import speech
import os
import io

# SET ENVIRONMENTAL VARIALBE
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "savvy-container.json"

# Creates google client
client = speech.SpeechClient()

# Full path of the audio file, Replace with your file name
file_name = os.path.join(os.path.dirname(__file__), "input/input.wav")

# Loads the audio file into memory
with io.open(file_name, "rb") as audio_file:
    content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)

config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,

    audio_channel_count=2,
    language_code="en-za",
)

# Sends the request to google to transcribe the audio
response = client.recognize(request={"config": config, "audio": audio})

# Reads the response
for result in response.results:
    print("Transcript: {}".format(result.alternatives[0].transcript))
