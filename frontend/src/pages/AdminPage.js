import React, { useState, useEffect, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { uploadDocument, listDocuments, deleteDocument } from "../api";

function AdminPage() {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [alert, setAlert] = useState(null);

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await listDocuments();
      setDocuments(res.data);
    } catch (err) {
      setAlert({ type: "error", text: "Failed to load documents." });
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const onDrop = useCallback(
    async (acceptedFiles) => {
      if (acceptedFiles.length === 0) return;
      const file = acceptedFiles[0];
      setUploading(true);
      setProgress(0);
      setAlert(null);

      try {
        await uploadDocument(file, (e) => {
          if (e.total) setProgress(Math.round((e.loaded / e.total) * 100));
        });
        setAlert({
          type: "success",
          text: `"${file.name}" uploaded and processed successfully.`,
        });
        fetchDocuments();
      } catch (err) {
        const msg =
          err.response?.data?.detail || "Upload failed. Please try again.";
        setAlert({ type: "error", text: msg });
      } finally {
        setUploading(false);
        setProgress(0);
      }
    },
    [fetchDocuments]
  );

  const handleDelete = async (docId, name) => {
    if (!window.confirm(`Delete "${name}"? This cannot be undone.`)) return;
    try {
      await deleteDocument(docId);
      setAlert({ type: "success", text: `"${name}" deleted.` });
      fetchDocuments();
    } catch {
      setAlert({ type: "error", text: "Delete failed." });
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "text/markdown": [".md"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
    },
    multiple: false,
    disabled: uploading,
  });

  return (
    <div className="page">
      <h2 className="page-title">Admin — Document Management</h2>

      {alert && (
        <div className={`alert ${alert.type}`}>{alert.text}</div>
      )}

      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? "active" : ""}`}
      >
        <input {...getInputProps()} />
        <div className="icon">&#128196;</div>
        {uploading ? (
          <div className="upload-progress">
            <p>Uploading & processing...</p>
            <div className="progress-bar">
              <div
                className="progress-bar-fill"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        ) : isDragActive ? (
          <p>Drop the file here...</p>
        ) : (
          <p>
            Drag & drop a document here, or click to select
            <br />
            <small>Supported: PDF, TXT, MD, DOCX</small>
          </p>
        )}
      </div>

      <h3 style={{ marginBottom: "1rem", fontWeight: 600 }}>
        Uploaded Documents ({documents.length})
      </h3>

      {documents.length === 0 ? (
        <div className="empty-state">
          No documents uploaded yet. Upload your first document above.
        </div>
      ) : (
        <div className="doc-list">
          {documents.map((doc) => (
            <div key={doc.id} className="doc-card">
              <div className="doc-info">
                <h3>{doc.original_name}</h3>
                <p>
                  {doc.chunk_count} chunks &middot; Uploaded{" "}
                  {new Date(doc.upload_date).toLocaleDateString()}
                </p>
              </div>
              <div className="doc-actions">
                <span className={`status-badge ${doc.status}`}>
                  {doc.status}
                </span>
                <button
                  className="btn-delete"
                  onClick={() => handleDelete(doc.id, doc.original_name)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AdminPage;
