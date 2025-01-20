import './App.css';
import React, { useState } from "react";
import axios from "axios";

function App() {
  const [transcription, setTranscription] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [isRecording, setIsRecording] = useState(false);

  // Start recording function
  const startRecording = async () => {
    try {
      setIsRecording(true);
      await axios.post("http://127.0.0.1:5000/api/start-record");
    } catch (error) {
      console.error("Error starting recording:", error);
    }
  };

  // Stop recording function
  const stopRecording = async () => {
    try {
      const result = await axios.post("http://127.0.0.1:5000/api/stop-record");
      setIsRecording(false);

      // Fetch transcription after stopping the recording
      const transcriptionResult = await axios.post("http://127.0.0.1:5000/api/transcribe", {
        filename: result.data.filename,
      });
      setTranscription(transcriptionResult.data.transcription);
    } catch (error) {
      console.error("Error stopping recording:", error);
    }
  };

  // Function to fetch AI response
  const handleGenerateResponse = () => {
    axios
        .post("http://127.0.0.1:5000/generate_response", {
            transcription: transcription,
        })
        .then((response) => {
            setAiResponse(response.data.ai_response);
        })
        .catch((error) => {
            console.error("Error generating response:", error);
        });
};

  return (
    <div className="App">
      <h1>IELTS Speaking Practice</h1>
      {!isRecording ? (
        <button onClick={startRecording}>Start Recording</button>
      ) : (
        <button onClick={stopRecording}>Stop Recording</button>
      )}
      <div>
                <textarea
                    placeholder="User's transcribed answer will appear here..."
                    value={transcription}
                    onChange={(e) => setTranscription(e.target.value)}
                    rows="4"
                    cols="50"
                />
                <button onClick={handleGenerateResponse}>
                    Get Examiner's Response
                </button>
            </div>
            <div>
                <h2>Examiner's Response:</h2>
                <p>{aiResponse}</p>
            </div>
        </div>
    );
};

export default App;