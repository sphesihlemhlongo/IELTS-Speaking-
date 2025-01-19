import os
import pyaudio
import wave
import openai
import random
import vertexai

from flask import Flask
from dotenv import load_dotenv
from google.cloud import aiplatform
from google.cloud import speech
from vertexai.preview import rag

load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
openai.api_key = os.getenv("OPENAI_API_KEY")

corpus = rag.create_corpus(display_name="ielts_rag", description="from rags to riches ")
print(corpus)

# Initialize Vertex AI API once per session
PROJECT_ID = "ielts-simulation-448302"  # Replace with your GCP Project ID
LOCATION = "us-central1"  # Vertex AI location
CORPUS_NAME = f"projects/{PROJECT_ID}/locations/us-central1/ragCorpora/{4611686018427387904}"  # Replace with your RAG Corpus ID

vertexai.init(project=PROJECT_ID, location=LOCATION)

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

def get_ielts_response(user_input, section):
    """
    Generate IELTS simulation questions using Vertex AI RAG.
    """

    # Construct the input text for the RAG query
    prompt = (
        "You are an IELTS examiner conducting a speaking test.\n"
        f"Section: {section}\n"
        f"Question: {user_input}\n"
        "Provide a professional and conversational response."
    )

    # Call RAG Retrieval Query
    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
                rag_corpus=CORPUS_NAME,
            )
        ],
        text=prompt,
        similarity_top_k=10,  # Adjust number of similar documents to retrieve
        vector_distance_threshold=0.5,  # Optional threshold for vector search
    )

    # Process the response to extract the answer
    contexts = response.contexts
    if contexts:
        # Extract the most relevant context
        generated_response = contexts[0].text
    else:
        generated_response = "I'm sorry, I couldn't retrieve any relevant information."

    return generated_response


def main():
    print("Starting IELTS Speaking Test simulation...\n")
    
    # Example: Part 1 simulation
    section = "Part 1"
    for _ in range(3):  # Simulate three Part 1 questions
        print(f"IELTS Examiner ({section}):")
        question = get_ielts_response(user_input="", section=section)  # Get a question
        print(question)

        # Record user response
        input("Your response: ")  # Replace this with real-time user input handling
        print("\n")



# app = Flask(__name__)

# @app.route('/')
# def home():
#     return "Hello, IELTS Simulation!"

if __name__ == '__main__':
    # app.run(debug=True)
    main()
