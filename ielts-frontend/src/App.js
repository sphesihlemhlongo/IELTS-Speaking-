import './App.css';
import React, { useState } from "react";
import axios from "axios";
// import './tailwind.css';


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
    <div className="min-h-screen bg-gray-100 flex flex-col justify-between">
      {/* Header/Nav Bar */}
      <header className="bg-blue-200 py-4 shadow-md">
        <h1 className="text-center text-3xl font-bold text-gray-800">
          IELTS Speaking Test
        </h1>
      </header>

      <main className="flex-grow flex flex-col items-center py-8 px-4">
        {testCompleted ? (
          <div className="bg-green-100 border border-green-400 text-green-700 p-4 rounded mb-6">
            <h2 className="text-xl font-semibold">
              Congratulations! You’ve completed the test.
            </h2>
          </div>
        ) : (
          <div className="bg-white shadow-md rounded-lg p-6 w-full max-w-3xl">
            {!section ? (
              <button
                className="w-full bg-green-300 text-gray-800 py-2 px-4 rounded hover:bg-gray-600 hover:text-white"
                onClick={startTest}
              >
                Start Test
              </button>
            ) : (
              <div className="space-y-6">
                <div
                  className="bg-blue-100 text-blue-800 p-4 rounded shadow-sm"
                >
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

      {/* Footer */}
      <footer className="bg-blue-200 py-4 shadow-md">
        <p className="text-center text-gray-800 text-sm">
          &copy; 2025 IELTS Speaking Practice Tool.
        </p>
      </footer>
    </div>
  );
}


export default App;