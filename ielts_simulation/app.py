import os
from google.cloud import speech
import pyaudio
import wave

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def record_audio():
    # Set up PyAudio to capture audio from the microphone
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    frames = []
    print("Recording...")

    # Record for 5 seconds (can adjust for longer speech duration)
    for i in range(0, int(16000 / 1024 * 5)):
        data = stream.read(1024)
        frames.append(data)

    print("Recording finished.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save audio to a .wav file
    filename = "audio.wav"
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))

    return filename

def transcribe_audio(filename):
    client = speech.SpeechClient()

    with open(filename, 'rb') as audio_file:
        content = audio_file.read()

     # The name of the audio file to transcribe
    gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"

    # audio = speech.RecognitionAudio(uri=gcs_uri)
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    # Print the transcription result
    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))
        return result.alternatives[0].transcript

def main():
    audio_file = record_audio()  # Record the audio
    transcript = transcribe_audio(audio_file)  # Transcribe the audio
    print("User said:", transcript)


# app = Flask(__name__)

# @app.route('/')
# def home():
#     return "Hello, IELTS Simulation!"

if __name__ == '__main__':
    # app.run(debug=True)
    main()
