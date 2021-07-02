from google.cloud.speech_v1.types.cloud_speech import SpeakerDiarizationConfig
from pydub import AudioSegment
import io
import os
from google.cloud import speech
# from google.cloud.speech_v1p1beta1.gapic import enums  ##this is old google speech v2 do not take
# from google.cloud.speech_v1p1beta1 import types

import pyaudio
import datetime

import wave
from google.cloud import storage

# # BETS ADDED: If in case the file format does not allow to be read (with error like wav.Error: file does not start with RIFF id)
# # use the below code to convert the file to normal WAV format

# import soundfile
# import wave

# file_path = './input/20210620_144839.wav'

# # read and rewrite the file with soudfile
# data, samplerate = soundfile.read(file_path)
# soundfile.write(file_path, data, samplerate)

# # now try to open the file with wave
# with wave.open(file_path) as file:
#     print('wav file converted and opened!')


# encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16

filepath = "input/"
# using same google bucket to avoid creating another one
output_filepath = "audio_wav_input"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "savvy-container.json"


def mp3_to_wav(audio_file_name):
    if audio_file_name.split('.')[1] == 'mp3':
        sound = AudioSegment.from_mp3(audio_file_name)
        audio_file_name = audio_file_name.split('.')[0] + '.wav'
        sound.export(audio_file_name, format="wav")
        print('done conveting')


def frame_rate_channel(audio_file_name):
    with wave.open(audio_file_name, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        print('converted frame rate channel')
        return frame_rate, channels


def stereo_to_mono(audio_file_name):
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format="wav")


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    try:
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "savvy-container.json"
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)
        print('file uploaded')
    except Exception as e:
        print(e)
        return False


def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()


def google_transcribe(audio_file_name):

    file_name = filepath + audio_file_name
    mp3_to_wav(file_name)

    # The name of the audio file to transcribe

    frame_rate, channels = frame_rate_channel(file_name)

    if channels > 1:
        stereo_to_mono(file_name)

    bucket_name = 'audio_wav_input'
    source_file_name = filepath + audio_file_name
    destination_blob_name = audio_file_name

    upload_blob(bucket_name, source_file_name, destination_blob_name)

    gcs_uri = 'gs://audio_wav_input/' + audio_file_name
    transcript = ''

    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=frame_rate,
        language_code='en-US')

    # Detects speech in the audio file
    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=100000)

    result = response.results[-1]
    words_info = result.alternatives

    tag = 1
    speaker = ""
    time = 0
    transcript = []
    transcript = response.results
    all_transcript_text = []
    for result in response.results:

        alternative = result.alternatives[0]
        if response.results.index(result) == 0:
            first_speaker = 'SPEAKER 1: ' + str(alternative)
            all_transcript_text.append(first_speaker)
            # transcript = f"SPEAKER 1: {alternative}"
            print(
                f'SPEAKER 1: {alternative}')
        elif response.results.index(result) % 2 != 0:
            speaker2 = 'SPEAKER 2: ' + str(alternative)
            all_transcript_text.append(speaker2)
            # transcript = f"SPEAKER 2: {alternative}"
            print(f'SPEAKER 2: {alternative}')
        else:
            alt_speaker = 'SPEAKER 1: ' + str(alternative)
            all_transcript_text.append(alt_speaker)
            # transcript = f"SPEAKER 1: {alternative}"
            print(f'SPEAKER 1: {alternative}')

    print(u"Speech to text operation is completed, output file is created: {}".format(
        output_filepath))
    print('BETS TESTING FINAL TRANSCRIPT VALUE... ', all_transcript_text)
    return transcript

    # result = response.results[-1]
    # words_info = result.alternatives[0].words

    # tag = 1
    # speaker = ""
    # for word_info in words_info:
    # if word_info.speaker_tag == tag:
    #     speaker = speaker+" "+word_info.word
    # else:
    #     transcript += "speaker {}: {}".format(tag, speaker) + '\n'
    #     tag = word_info.speaker_tag
    #     speaker = ""+word_info.word

    # for result in response.results:
    # if result.speaker_tag == tag:
    #     speaker = speaker+" "+result.word
    # else:
    #     transcript += "speaker {}: {}".format(tag, speaker) + '\n'
    #     tag = result.speaker_tag
    #     speaker = ""+result.word

    transcript += "speaker {}: {}".format(tag, speaker)

    delete_blob(bucket_name, destination_blob_name)
    print('Blob Deleted')
    return transcript

    # # client = speech.SpeechClient()
    # # audio = types.RecognitionAudio(uri=gcs_uri)
    # from google.cloud import speech
    # client = speech.SpeechClient()

    # audio = speech.RecognitionAudio(uri=gcs_uri)
    # config = speech.RecognitionConfig(
    #     encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    #     # sample_rate_hertz=8000,
    #     sample_rate_hertz=frame_rate,
    #     language_code="en-IN",
    # )

    # operation = client.long_running_recognize(config=config, audio=audio)
    # response = operation.result(timeout=100000)

    # result = response.results[-1]
    # words_info = result.alternatives[0].words

    # tag = 1
    # speaker = ""

    # for word_info in words_info:
    #     if word_info.speaker_tag == tag:
    #         speaker = speaker+" "+word_info.word
    #     else:
    #         transcript += "speaker {}: {}".format(tag, speaker) + '\n'
    #         tag = word_info.speaker_tag
    #         speaker = ""+word_info.word

    # transcript += "speaker {}: {}".format(tag, speaker)

    # delete_blob(bucket_name, destination_blob_name)
    # print('Blob Deleted')
    # return transcript


def write_transcripts(transcript_filename, transcript):
    f = open(output_filepath + '_' + transcript_filename, "w+")
    f.write(str(transcript))
    f.close()
    print('File transcribing done.')


if __name__ == "__main__":
    for audio_file_name in os.listdir(filepath):
        exists = os.path.isfile(
            output_filepath + audio_file_name.split('.')[0] + '.txt')
        if exists:
            pass
        else:
            transcript = google_transcribe(audio_file_name)
            transcript_filename = audio_file_name.split('.')[0] + '.txt'
            write_transcripts(transcript_filename, transcript)
