import wave
import pyaudio
import speech_recognition as sr


# Setup channel info
FORMAT = pyaudio.paInt16  # data type formate
CHANNELS = 2  # Adjust to your number of channels
RATE = 44100  # Sample Rate
CHUNK = 1024  # Block Size
RECORD_SECONDS = 50  # Record time
WAVE_OUTPUT_FILENAME = "input/input.wav"

# Startup pyaudio instance
audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
print("recording for 30 secs...")
frames = []

# Record for RECORD_SECONDS
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
print("Finished recording. Check audio file saved under 'input' folder.")


# Stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

# Write your new .wav file with built in Python 3 Wave module
waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()


# BETS ADDED: Now lets convert the audio saved to text for further analysis.


print("Now lets convert the audio to text and display it...")

filename = 'input/input.wav'

# initialize the recognizer
r = sr.Recognizer()

with sr.AudioFile(filename) as source:
    # try listen for the data (load audio to memory)
    try:
        audio_data = r.record(source)
        # recognize (convert from speech to audio)
        # BETS NOTE google API used here u have option to choose other speech_recognition APIS also
        text = r.recognize_google(audio_data)

        print(text)
    except:
        print("Sorry... something went wrong reading the audio file.")


# BETS ADDED: Now lets write the audio text to a text file. No module is required for this.

# Open funciton to open the file in write mode ('w+')
# Write Only (‘w’) : Open the file for writing. For existing file, the data is truncated and over-written. The handle is positioned at the beginning of the file. Creates the file if the file does not exists.
# Write and Read (‘w+’) : Open the file for reading and writing. For existing file, data is truncated and over-written. The handle is positioned at the beginning of the file.

print("Write text to a file. Check folder Output/TextOutput.txt")

outputfile = open("output/TextOutput.txt", "w")

outputfile.write(text)

outputfile.close()
