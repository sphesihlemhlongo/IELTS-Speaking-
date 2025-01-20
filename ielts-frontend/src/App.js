import './App.css';
import React, { useState } from "react";
import axios from "axios";

function App() {
  const [transcription, setTranscription] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [section, setSection] = useState("");
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [testCompleted, setTestCompleted] = useState(false);

  const startTest = () => {
    axios
        .post("http://127.0.0.1:5000/start_test", { user_id: "test_user" })
        .then((res) => {
            setSection(res.data.section);
            setQuestion(res.data.question);
        })
        .catch((err) => console.error(err));
};

  const nextQuestion = () => {
    axios
        .post("http://127.0.0.1:5000/next_question", { user_id: "test_user" })
        .then((res) => {
            if (res.data.message === "Test completed!") {
                setTestCompleted(true);
            } else {
                setSection(res.data.section);
                setQuestion(res.data.question);
            }
        })
        .catch((err) => console.error(err));
  };

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
            user_id: "test_user",
            transcription,
        })
        .then((res) => {
            setAiResponse(res.data.response);
        })
        .catch((err) => console.error(err));
};

return (
  <div className="App">
      <h1>IELTS Speaking Test</h1>
      {testCompleted ? (
          <h2>Congratulations! You’ve completed the test.</h2>
      ) : (
          <>
              {!section && (
                  <button onClick={startTest}>Start Test</button>
              )}
              {section && (
                  <div>
                      <h2>Section: {section}</h2>
                      <p>{question}</p>

                      {/* Recording controls */}
                      {!isRecording ? (
                          <button onClick={startRecording}>
                              Start Recording
                          </button>
                      ) : (
                          <button onClick={stopRecording}>
                              Stop Recording
                          </button>
                      )}

                      {/* Transcription display */}
                      <div>
                          <textarea
                              placeholder="User's transcribed answer will appear here..."
                              value={transcription}
                              onChange={(e) =>
                                  setTranscription(e.target.value)
                              }
                              rows="4"
                              cols="50"
                          />
                          <button onClick={handleGenerateResponse}>
                              Get Examiner's Response
                          </button>
                      </div>

                      {/* AI Examiner's Response */}
                      <div>
                          <h2>Examiner's Response:</h2>
                          <p>{aiResponse}</p>
                      </div>

                      {/* Next question button */}
                      <button onClick={nextQuestion}>
                          Next Question
                      </button>
                  </div>
              )}
          </>
      )}
  </div>
);
};

export default App;