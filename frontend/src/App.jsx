import { useState } from "react";
import axios from "axios";
import "./index.css";

const API_BASE = "http://localhost:8000";

function App() {
  const [githubUrl, setGithubUrl] = useState("");
  const [projectId, setProjectId] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [history, setHistory] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const uploadRepo = async () => {
    try {
      setLoading(true);
      const formData = new FormData();
      formData.append("github_url", githubUrl);

      const res = await axios.post(`${API_BASE}/upload/`, formData);
      setProjectId(res.data.project_id);
      alert("Upload successful!");
    } catch {
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const askQuestion = async () => {
    try {
      setLoading(true);

      const res = await axios.post(`${API_BASE}/ask/`, {
        project_id: projectId,
        question: question,
      });

      setAnswer(res.data.answer);
      setSources(res.data.sources || []);
      loadHistory();
    } catch {
      alert("Error asking question");
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    if (!projectId) return;
    const res = await axios.get(`${API_BASE}/history/${projectId}`);
    setHistory(res.data);
  };

  const loadStatus = async () => {
    const res = await axios.get(`${API_BASE}/status/`);
    setStatus(res.data);
  };

  return (
    <div className="page">
      <h1 className="header">🚀 Codebase Q&A</h1>

      <div className="layout">

        {/* LEFT SIDEBAR */}
        <div className="sidebar">

          {/* Upload */}
          <div className="card">
            <h2 className="section-title">Upload Repository</h2>

            <input
              type="text"
              placeholder="Paste GitHub repo URL"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              className="input"
            />

            <button className="primary-button" onClick={uploadRepo}>
              {loading ? "Uploading..." : "Upload"}
            </button>

            {projectId && (
              <p className="project-id">
                Project ID: {projectId}
              </p>
            )}
          </div>

          {/* Ask */}
          <div className="card">
            <h2 className="section-title">Ask Question</h2>

            <input
              type="text"
              placeholder="Ask about the code..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="input"
            />

            <button className="primary-button" onClick={askQuestion}>
              {loading ? "Thinking..." : "Ask"}
            </button>
          </div>

          {/* History */}
          <div className="card">
            <h2 className="section-title">History</h2>

            <button className="secondary-button" onClick={loadHistory}>
              Load History
            </button>

            <div style={{ marginTop: 10, maxHeight: "200px", overflowY: "auto" }}>
              {history.map((item, index) => (
                <div key={index} style={{ marginBottom: 12 }}>
                  <div style={{ fontWeight: "bold", color: "#38bdf8" }}>
                    Q: {item.question}
                  </div>
                  <div style={{ fontSize: 13, color: "#cbd5e1" }}>
                    A: {item.answer}
                  </div>
                  <hr style={{ borderColor: "#1e293b" }} />
                </div>
              ))}
            </div>
          </div>

          {/* Status */}
          <div className="card">
            <h2 className="section-title">System Status</h2>

            <button className="secondary-button" onClick={loadStatus}>
              Check Status
            </button>

            {status && (
              <pre className="pre">
                {JSON.stringify(status, null, 2)}
              </pre>
            )}
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div className="answer-panel">
          <h2 className="section-title">Answer</h2>

          {answer ? (
            <div className="answer-box">
              {answer}
            </div>
          ) : (
            <div style={{ color: "#64748b" }}>
              Your answer will appear here...
            </div>
          )}

          {sources.length > 0 && (
            <>
              <h3 style={{ marginTop: 25, color: "#facc15" }}>
                Sources
              </h3>

              {sources.map((src, index) => (
                <div key={index} className="source-card">
                  <div className="file-path">
                    {src.file_path}
                  </div>

                  <div className="snippet">
                    {src.snippet}
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
