import sys
import io
import os
import datetime

# from moviepy.editor import *
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import speech
from google.cloud import storage

# global variable, please change them with your values
bucket_name = "bountify-test-bucket"
output_file = "output.txt"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "savvy-container.json"

# def convert_video_to_mp3(video_file_path):
audio_file = "input/input.wav"
# video = VideoFileClip(video_file_path)
# audio = video.audio
# audio.write_audiofile(audio_file_path)
# # return audio_file_path


def upload_file_to_cloud_storage(audio_file):
    bucket_url = "gs://{}/{}".format(bucket_name, audio_file)
    file_name = os.path.join(os.path.dirname(__file__), audio_file)
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(audio_file)
    print(u"{} is uploading to storage...".format(bucket_url))
    blob.upload_from_filename(file_name)
    print("File is uploaded.")
    os.remove(file_name)
    return bucket_url


def convert_speech_to_text(bucket_file_url, output_file="output.txt"):
    client = speech.SpeechClient()

    audio = {"uri": bucket_file_url}
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        enable_speaker_diarization=True,
        diarization_speaker_count=2,
        model="phone_call",
        enable_word_time_offsets=True,
        use_enhanced=True,
        language_code="en-US")

    operation = client.long_running_recognize(config, audio)

    print(u"Waiting for speech-to-text operation to complete...")
    response = operation.result()

    with open(output_file, "w") as text_file:
        for result in response.results:
            alternative = result.alternatives[0]
            current_speaker_tag = -1
            transcript = ""
            time = 0
            for word in alternative.words:
                if word.speaker_tag != current_speaker_tag:
                    if (transcript != ""):
                        print(u"Speaker {} - {} - {}".format(current_speaker_tag,
                              str(datetime.timedelta(seconds=time)), transcript), file=text_file)
                    transcript = ""
                    current_speaker_tag = word.speaker_tag
                    time = word.start_time.seconds

                transcript = transcript + " " + word.word
        if transcript != "":
            print(u"Speaker {} - {} - {}".format(current_speaker_tag,
                  str(datetime.timedelta(seconds=time)), transcript), file=text_file)
        print(u"Speech to text operation is completed, output file is created: {}".format(
            output_file))


# mainprogram starts here
# video_file_path = sys.argv[1]
# audio_file = convert_video_to_mp3(video_file_path)
audio_file_bucket_url = upload_file_to_cloud_storage(audio_file)
convert_speech_to_text(audio_file_bucket_url, output_file)
