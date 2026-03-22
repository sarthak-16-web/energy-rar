import { useMemo, useState } from "react";
import "./index.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [message, setMessage] = useState("");
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);

  const fileName = useMemo(() => {
    return file ? file.name : "No PDF selected";
  }, [file]);

  const handleUpload = async () => {
    if (!file) {
      setMessage("Please select a PDF file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setUploading(true);
      setMessage("");
      setAnswer("");

      const res = await fetch(`${API_BASE}/upload-pdf`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      setMessage("PDF uploaded successfully. You can ask questions now.");
    } catch (error) {
      setMessage(error.message || "Something went wrong while uploading.");
    } finally {
      setUploading(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) {
      setMessage("Please enter a question.");
      return;
    }

    try {
      setAsking(true);
      setMessage("");

      const res = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Failed to get answer");
      }

      setAnswer(data.answer);
    } catch (error) {
      setMessage(error.message || "Something went wrong while getting the answer.");
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="page">
      <div className="bg-orb orb-one" />
      <div className="bg-orb orb-two" />
      <div className="grid-overlay" />

      <main className="shell">
        <section className="hero">
          <div className="hero-badge">Energy Document RAG</div>
          <h1>Chat with Energy Documents</h1>
          <p className="hero-text">
            Upload a PDF, extract its knowledge, and ask questions with a sleek
            minimal RAG experience powered by FastAPI, ChromaDB, and Groq.
          </p>

          <div className="hero-stats">
            <div className="stat-card">
              <span className="stat-label">Upload</span>
              <strong>1 PDF</strong>
            </div>
            <div className="stat-card">
              <span className="stat-label">Answers</span>
              <strong>From document only</strong>
            </div>
            <div className="stat-card">
              <span className="stat-label">Stack</span>
              <strong>React + FastAPI</strong>
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Document Workspace</p>
              <h2>Upload and Ask</h2>
            </div>
            <div className="status-pill">
              <span className="status-dot" />
              Ready
            </div>
          </div>

          <div className="panel-grid">
            <div className="glass-card">
              <div className="card-top">
                <div>
                  <p className="card-kicker">Step 1</p>
                  <h3>Upload PDF</h3>
                </div>
                <div className="icon-box">PDF</div>
              </div>

              <label className="upload-box">
                <input
                  type="file"
                  accept="application/pdf"
                  onChange={(e) => setFile(e.target.files[0])}
                />
                <div className="upload-content">
                  <div className="upload-icon">↑</div>
                  <p className="upload-title">Choose your energy document</p>
                  <p className="upload-subtitle">
                    Select one PDF to build the knowledge base
                  </p>
                  <div className="file-chip">{fileName}</div>
                </div>
              </label>

              <button
                className="primary-btn"
                onClick={handleUpload}
                disabled={uploading}
              >
                {uploading ? "Uploading PDF..." : "Upload Document"}
              </button>
            </div>

            <div className="glass-card">
              <div className="card-top">
                <div>
                  <p className="card-kicker">Step 2</p>
                  <h3>Ask Questions</h3>
                </div>
                <div className="icon-box">AI</div>
              </div>

              <textarea
                rows="7"
                placeholder="Ask anything from the uploaded PDF...
For example:
• What is the main topic of the report?
• What are the key findings?
• What energy source is discussed most?"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
              />

              <button
                className="primary-btn"
                onClick={handleAsk}
                disabled={asking}
              >
                {asking ? "Generating Answer..." : "Get Answer"}
              </button>
            </div>
          </div>

          {message && (
            <div className="info-banner">
              <span className="info-badge">Info</span>
              <p>{message}</p>
            </div>
          )}

          <div className="answer-panel">
            <div className="answer-header">
              <div>
                <p className="eyebrow">Response</p>
                <h3>Generated Answer</h3>
              </div>
            </div>

            {answer ? (
              <div className="answer-content">
                <p>{answer}</p>
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">✦</div>
                <p>Your answer will appear here after you ask a question.</p>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}