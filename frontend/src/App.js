import React from "react";
import { Routes, Route, Link, useLocation } from "react-router-dom";
import AdminPage from "./pages/AdminPage";
import UserPage from "./pages/UserPage";
import "./App.css";

function App() {
  const location = useLocation();

  return (
    <div className="app">
      <header className="navbar">
        <h1>Knowledge Base Agent</h1>
        <nav>
          <Link
            to="/"
            className={location.pathname === "/" ? "active" : ""}
          >
            Ask
          </Link>
          <Link
            to="/admin"
            className={location.pathname === "/admin" ? "active" : ""}
          >
            Admin
          </Link>
        </nav>
      </header>
      <Routes>
        <Route path="/" element={<UserPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Routes>
    </div>
  );
}

export default App;
