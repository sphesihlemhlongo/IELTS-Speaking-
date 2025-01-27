import os
import time
import uuid
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from google.cloud import speech
import google.generativeai as genai
from threading import Thread
import datetime
from flask import Flask, send_from_directory

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
genai.configure(api_key=os.getenv("Gemini_API_Key"))

# print(sd.query_devices())
# sd.default.device
print(sd.default.device)
print("You are screwed")
app = Flask(__name__, static_folder="build")
CORS(app) 

@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

# Global variables
def create_session_file(user_id, session_type):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{session_type}_{timestamp}.txt"
    return os.path.join("sessions", filename)

is_recording = False
prompts = {
    "part_1": [
        "Can you tell me about yourself?",
        "What do you do? Do you work or study?",
        "What are your hobbies?",
        "Do you like traveling? Why or why not?"
    ],
    "part_2": [
        "Describe a memorable trip you took. You should say:\n- Where you went\n- Who you went with\n- What you did\nAnd explain why it was memorable.",
        "Describe a favorite book you’ve read. You should say:\n- What it is\n- Who wrote it\n- What it is about\nAnd explain why you enjoyed it."
    ],
    "part_3": [
        "Why do you think people enjoy traveling to new places?",
        "How does reading books contribute to personal growth?",
        "What is the importance of leisure activities in a busy lifestyle?"
    ]
}
frames = []
samplerate = 16000
test_progress = {}
sessions = {}
selected_device =sd.default.device

@app.route('/start_test', methods=['POST'])
def start_test():
    data = request.json
    user_id = data.get('user_id', 'default_user')
    session_type = data.get('session_type', 'practice')  # 'practice' or 'test'
    filename = create_session_file(user_id, session_type)

    sessions[user_id] = {
        "session_type": session_type,
        "current_section": "part_1",
        "question_index": 0,
        "filename": filename
    }

    os.makedirs("sessions", exist_ok=True)
    with open(filename, "w") as f:
        f.write(f"Session Type: {session_type}\n\n")

    question = prompts["part_1"][0]
    return jsonify({"section": "part_1", "question": question})

@app.route('/next_question', methods=['POST'])
def next_question():
    data = request.json
    user_id = data.get('user_id', 'default_user')
    response = data.get('response', '')

    session = sessions.get(user_id, {})
    section = session.get("current_section", "part_1")
    question_index = session.get("question_index", 0)
    filename = session.get("filename")

    if not filename:
        return jsonify({"error": "Session not started."}), 400

    with open(filename, "a") as f:
        f.write(f"Q: {prompts[section][question_index]}\nA: {response}\n\n")

    if section == "part_1":
        if question_index < len(prompts["part_1"]) - 1:
            session["question_index"] += 1
        else:
            session["current_section"] = "part_2"
            session["question_index"] = 0

    elif section == "part_2":
        if question_index < len(prompts["part_2"]) - 1:
            session["question_index"] += 1
        else:
            session["current_section"] = "part_3"
            session["question_index"] = 0

    elif section == "part_3":
        if question_index < len(prompts["part_3"]) - 1:
            session["question_index"] += 1
        else:
            return jsonify({"message": "Test completed!", "filename": filename})

    section = session["current_section"]
    question_index = session["question_index"]
    next_question = prompts[section][question_index]

    return jsonify({"section": section, "question": next_question})

def generate_unique_filename(base_name="file", extension="txt", directory="."):
    """
    Generate a unique filename by appending a timestamp and a UUID to the base name.

    Parameters:
        base_name (str): The base name for the file (default is "file").
        extension (str): The file extension (default is "txt").
        directory (str): The directory to check for existing filenames (default is the current directory).

    Returns:
        str: A unique filename.
    """
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    while True:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]  # Use the first 8 characters of a UUID
        filename = f"{base_name}_{timestamp}_{unique_id}.{extension}"
        full_path = os.path.join(directory, filename)

        if not os.path.exists(full_path):
            return filename

def write_text_to_file(text, filename, directory="./text_files"):
    """
    Write the given text to a specified file in the given directory.

    Parameters:
        text (str): The text content to write to the file.
        filename (str): The name of the file.
        directory (str): The directory to save the file.

    Returns:
        str: Full path to the written text file.
    """
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    full_path = os.path.join(directory, filename)
    with open(full_path, 'w', encoding='utf-8') as file:
        file.write(text)

    return full_path

def save_to_folder(folder_name, file_path):
    """
    Save an existing file to the specified folder.

    Parameters:
        folder_name (str): The name of the folder where the file should be saved.
        file_path (str): The path to the existing file.

    Returns:
        str: Full path to the saved file in the new folder.
    """
    # Ensure the folder exists
    os.makedirs(folder_name, exist_ok=True)

    # Get the filename from the provided file path
    filename = os.path.basename(file_path)
    full_path = os.path.join(folder_name, filename)

    # Copy the file to the new folder
    # with open(file_path, 'rb') as src_file:
    #     content = src_file.read()

    # with open(full_path, 'wb') as dest_file:
    #     dest_file.write(content)

    os.rename(file_path, full_path)

    return full_path


@app.route('/api/start-record', methods=['POST'])
def start_record():
    global is_recording, frames
    is_recording = True

    # Start recording in a separate thread
    def record():
        global is_recording, frames
        samplerate = 16000  # Sample rate
        
        # frames = []
        def callback(indata, frames_count, time, status):
            if is_recording:
                frames.append(indata.copy())

        # Open the input stream using sounddevice
        with sd.InputStream(
            samplerate=samplerate,
            channels=1,
            dtype='int16',
            callback=callback,
            blocksize=1024,
            device=selected_device
        ):
            while is_recording:
                sd.sleep(100)  # Keep the thread alive while recording


    thread = Thread(target=record)
    thread.start()

    return jsonify({"message": "Recording started"})

@app.route('/api/stop-record', methods=['POST'])
def stop_record():
    global is_recording, frames
    is_recording = False

    # Save audio to a .wav file
    filename = generate_unique_filename("audio","wav", directory=".")
    frames_array = np.concatenate(frames, axis=0)  # Convert list of numpy arrays to bytes

    write(filename, samplerate, frames_array.astype(np.int16))

    return jsonify({"message": "Recording stopped", "filename": filename})


def transcribe_audio(audio_recording):
    client = speech.SpeechClient()
    
    with open(audio_recording, 'rb') as audio_file:
        content = audio_file.read()

    # The name of the audio file to transcribe
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    
    save_to_folder("./audio_recordings", audio_recording)
    
    # Print the transcription result
    for result in response.results:
        transcript = "Transcript: {}".format(result.alternatives[0].transcript)
        # print("Transcript: {}".format(result.alternatives[0].transcript))
        
        return result.alternatives[0].transcript
    return ""

def get_response(user_input):
    text_filename = generate_unique_filename("transcription-generatedResponse","txt", directory=".")
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"You are an IELTS examiner. Respond to the following candidate answer: '{user_input}'"
        )
        write_text_to_file(user_input, text_filename, "./transcipts")
        write_text_to_file(response.text, text_filename, "./generated_response")
        # print(f"User Input: {user_input}")  # Log user input
        # print(f"AI Response: {response.text}")  # Log AI response
        return response.text
    except Exception as e:
        return str(e)
    
@app.route('/generate_response', methods=['POST'])
def generate_response():
    data = request.get_json()
    user_transcription = data.get('transcription', '')

    if not user_transcription:
        return jsonify({"error": "No transcription provided"}), 400

    try:
        # Generate response using Gemini
        ai_response = get_response(user_transcription)
        return jsonify({"ai_response": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500    
 

# Flask route to handle transcription
@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json()
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "Filename is required"}), 400

    transcription = transcribe_audio(filename)
    print(f"Transcription: {transcription}")  # Log transcription
    return jsonify({"transcription": transcription})

# Flask route to generate response
@app.route("/api/respond", methods=["POST"])
def respond():
    data = request.get_json()
    user_input = data.get("user_input")
    if not user_input:
        return jsonify({"error": "User input is required"}), 400

    response = get_response(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    port = os.environ.get("PORT", 5000)  # Default to 5000 if not set
    app.run(debug=True, host="0.0.0.0", port=port)