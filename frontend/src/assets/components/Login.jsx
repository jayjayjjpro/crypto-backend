import React, { useEffect } from "react";

const COGNITO_LOGIN_URL = import.meta.env.VITE_COGNITO_LOGIN_URL

const Login = () => {
  useEffect(() => {
    const token = sessionStorage.getItem("access_token");
    if (token) {
      window.location.href = "/dashboard"; // Redirect if already logged in
    }
  }, []);

  const handleLogin = () => {
    window.location.href = COGNITO_LOGIN_URL; // Redirect to AWS Cognito Hosted UI
  };

  return (
    <div style={{ textAlign: "center", paddingTop: "100px" }}>
      <h1>Login to My File Storage</h1>
      <button onClick={handleLogin} style={{ padding: "10px 20px", fontSize: "16px" }}>
        Sign in with Cognito
      </button>
    </div>
  );
};

export default Login;
