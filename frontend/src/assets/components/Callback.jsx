import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const COGNITO_TOKEN_URL = import.meta.env.VITE_COGNITO_TOKEN_URL;
const CLIENT_ID = import.meta.env.VITE_CLIENT_ID;
const CLIENT_SECRET = import.meta.env.VITE_CLIENT_SECRET;
const REDIRECT_URL = import.meta.env.VITE_REDIRECT_URL;

const Callback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");

    if (code) {
      // Exchange authorization code for access token
      axios.post(
        COGNITO_TOKEN_URL,
        new URLSearchParams({
          grant_type: "authorization_code",
          client_id: CLIENT_ID,
          client_secret: CLIENT_SECRET, 
          code,
          redirect_uri: REDIRECT_URL,
        }),
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded", 
          }
        }
      )
      .then((response) => {
        sessionStorage.setItem("access_token", response.data.access_token);
        sessionStorage.setItem("id_token", response.data.id_token);
        sessionStorage.setItem("refresh_token", response.data.refresh_token);
        window.dispatchEvent(new Event("storage"));
        navigate("/dashboard");
      })
      .catch((error) => {
        console.error("Token exchange failed:", error.response?.data || error.message);
      });
      
    }
  }, []);

  return <h2>Logging in...</h2>;
};

export default Callback;
