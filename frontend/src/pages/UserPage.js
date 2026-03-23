import React, { useState, useRef, useEffect } from "react";
import { queryKnowledgeBase } from "../api";

function UserPage() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I can answer questions based on the documents in our knowledge base. What would you like to know?",
      sources: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = await queryKnowledgeBase(question);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.data.answer,
          sources: res.data.sources || [],
        },
      ]);
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        "Something went wrong. Please try again.";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: msg, sources: [] },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <div>{msg.content}</div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources">
                  Sources:{" "}
                  {msg.sources.map((s, j) => (
                    <span key={j}>{s}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-area" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about the knowledge base..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default UserPage;
