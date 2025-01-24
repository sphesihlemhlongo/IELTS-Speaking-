import './App.css';
import React, { useState } from "react";
import axios from "axios";

function App() {
  const [transcription, setTranscription] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [section, setSection] = useState("");
  const [question, setQuestion] = useState("");
  const [responseFeedback, setResponseFeedback] = useState("");
  const [mode, setMode] = useState(""); // Track whether it's "practice" or "test"
  const [testCompleted, setTestCompleted] = useState(false);

  const startSession = (selectedMode) => {
    setMode(selectedMode);
    axios
      .post(`http://127.0.0.1:5000/start_${selectedMode}`, { user_id: "test_user" })
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
          setTranscription("");
          setAiResponse("");
          setResponseFeedback("");
        }
      })
      .catch((err) => console.error(err));
  };

  const startRecording = async () => {
    try {
      setIsRecording(true);
      await axios.post("http://127.0.0.1:5000/api/start-record");
    } catch (error) {
      console.error("Error starting recording:", error);
    }
  };

  const stopRecording = async () => {
    try {
      const result = await axios.post("http://127.0.0.1:5000/api/stop-record");
      setIsRecording(false);

      const transcriptionResult = await axios.post("http://127.0.0.1:5000/api/transcribe", {
        filename: result.data.filename,
      });
      setTranscription(transcriptionResult.data.transcription);
    } catch (error) {
      console.error("Error stopping recording:", error);
    }
  };

  const handleGenerateResponse = () => {
    axios
      .post("http://127.0.0.1:5000/generate_response", {
        user_id: "test_user",
        transcription: transcription,
      })
      .then((response) => {
        setAiResponse(response.data.ai_response);
        setResponseFeedback(response.data.feedback || ""); // Set feedback if provided
      })
      .catch((error) => {
        console.error("Error generating response:", error);
      });
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col justify-between">
      <header className="bg-blue-200 py-4 shadow-md">
        <h1 className="text-center text-3xl font-bold text-gray-800">
          IELTS Speaking Practice Tool
        </h1>
      </header>

      <main className="flex-grow flex flex-col items-center py-8 px-4">
        {testCompleted ? (
          <div className="bg-green-100 border border-green-400 text-green-700 p-4 rounded mb-6">
            <h2 className="text-xl font-semibold">
              Congratulations! You’ve completed the {mode === "practice" ? "practice session" : "test"}.
            </h2>
          </div>
        ) : (
          <div className="bg-white shadow-md rounded-lg p-6 w-full max-w-3xl">
            {!section ? (
              <div className="flex space-x-4">
                <button
                  className="flex-1 bg-green-300 text-gray-800 py-2 px-4 rounded hover:bg-gray-600 hover:text-white"
                  onClick={() => startSession("test")}
                >
                  Start Test
                </button>
                <button
                  className="flex-1 bg-blue-300 text-gray-800 py-2 px-4 rounded hover:bg-gray-600 hover:text-white"
                  onClick={() => startSession("practice")}
                >
                  Practice
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="bg-blue-100 text-blue-800 p-4 rounded shadow-sm">
                  <h2 className="text-lg font-semibold mb-2">Section: {section}</h2>
                  <p>{question}</p>
                </div>

                <div className="text-center">
                  {!isRecording ? (
                    <button
                      className="bg-green-300 text-gray-800 py-2 px-4 rounded hover:bg-gray-600 hover:text-white"
                      onClick={startRecording}
                    >
                      Start Recording
                    </button>
                  ) : (
                    <button
                      className="bg-red-300 text-gray-800 py-2 px-4 rounded hover:bg-gray-600 hover:text-white"
                      onClick={stopRecording}
                    >
                      Stop Recording
                    </button>
                  )}
                </div>

                <textarea
                  className="w-full border border-gray-300 p-2 rounded mt-4 resize-none"
                  placeholder="User's transcribed answer will appear here..."
                  value={transcription}
                  onChange={(e) => setTranscription(e.target.value)}
                  rows="4"
                />

                <div className="text-center">
                  <button
                    className="bg-green-300 text-gray-800 py-2 px-4 rounded mt-4 hover:bg-gray-600 hover:text-white"
                    onClick={handleGenerateResponse}
                  >
                    Get Examiner's Response
                  </button>
                </div>

                <div className="bg-gray-50 border border-gray-200 p-4 rounded">
                  <h2 className="text-lg font-semibold">Examiner's Response:</h2>
                  <p>{aiResponse}</p>
                  {responseFeedback && (
                    <div className="mt-4 bg-yellow-100 border border-yellow-300 text-yellow-800 p-2 rounded">
                      <h3 className="font-semibold">Feedback:</h3>
                      <p>{responseFeedback}</p>
                    </div>
                  )}
                </div>

                <button
                  className="w-full bg-green-300 text-gray-800 py-2 px-4 rounded hover:bg-gray-600 hover:text-white"
                  onClick={nextQuestion}
                >
                  Next Question
                </button>
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="bg-blue-200 py-4 shadow-md">
        <p className="text-center text-gray-800 text-sm">
          &copy; 2025 IELTS Speaking Practice Tool.
        </p>
      </footer>
    </div>
  );
}

export default App;
