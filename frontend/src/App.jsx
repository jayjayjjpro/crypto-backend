import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./assets/components/Login";
import Callback from "./assets/components/Callback";
import FileStorage from "./assets/components/FileStorage";

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check authentication status on mount
    const checkAuth = () => {
      setIsAuthenticated(!!sessionStorage.getItem("access_token"));
    };

    checkAuth(); // Ensure it runs on page load

    // Listen for storage changes (if another tab logs out)
    window.addEventListener("storage", checkAuth);

    return () => window.removeEventListener("storage", checkAuth);
  }, []);

  const handleLogout = () => {
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("id_token");
    sessionStorage.removeItem("refresh_token");
    setIsAuthenticated(false);
    window.location.href = "/"; // Redirect to login page
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/callback" element={<Callback />} />
        <Route 
          path="/dashboard" 
          element={isAuthenticated ? <FileStorage onLogout={handleLogout} /> : <Navigate to="/" />} 
        />
      </Routes>
    </Router>
  );
};

export default App;
