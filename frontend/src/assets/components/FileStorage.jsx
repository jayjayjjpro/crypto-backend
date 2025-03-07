import { useState, useEffect } from "react";
import { Container, Typography, Box, Button } from "@mui/material";
import axios from "axios";
import FileList from "./FileList";
import UploadButton from "./UploadButton";
import DeleteDialog from "./DeleteDialog";

const API_BASE_URL = "http://localhost:8000"; // Backend URL

function FileStorage({ onLogout }) {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchFiles();
    fetchUserInfo();
  }, []);

  const fetchFiles = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/files/`);
      setFiles(response.data);
    } catch (error) {
      console.error("Error fetching files:", error);
    }
  };

  const fetchUserInfo = async () => {
    const idToken = localStorage.getItem("id_token");
    if (idToken) {
      try {
        const decodedToken = JSON.parse(atob(idToken.split(".")[1])); // Decode JWT payload
        setUser(decodedToken);
      } catch (error) {
        console.error("Error decoding token:", error);
      }
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post(`${API_BASE_URL}/upload/`, formData, { headers: { "Content-Type": "multipart/form-data" } });
      fetchFiles();
    } catch (error) {
      console.error("Error uploading file:", error);
    }
  };

  const handleDownload = async (filename) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/files/${filename}/download/`);
      window.open(response.data.presigned_url, "_blank");
    } catch (error) {
      console.error("Error generating download link:", error);
    }
  };

  const handleVerify = async (filename) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/files/${filename}/verify/`);
      alert(response.data.is_valid ? "File is valid!" : "File integrity check failed!");
    } catch (error) {
      console.error("Error verifying file:", error);
    }
  };

  const confirmDelete = (filename) => {
    setSelectedFile(filename);
    setOpenDialog(true);
  };

  const handleDelete = async () => {
    try {
      await axios.delete(`${API_BASE_URL}/files/${selectedFile}/delete/`);
      fetchFiles();
    } catch (error) {
      console.error("Error deleting file:", error);
    }

    setOpenDialog(false);
    setSelectedFile(null);
  };

  return (
    <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", flexDirection: "column" }}>
      <Container maxWidth="sm">
        {/* Header with User Info and Logout Button */}
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
          <Typography variant="h4" align="center">📂 My File Storage</Typography>
          {user && <Typography variant="body1">👤 {user.email}</Typography>}
          <Button variant="contained" color="secondary" onClick={onLogout}>
            Logout
          </Button>
        </Box>

        <UploadButton onUpload={handleFileUpload} />
        <FileList files={files} onDownload={handleDownload} onVerify={handleVerify} onDelete={confirmDelete} />

        <DeleteDialog open={openDialog} file={selectedFile} onClose={() => setOpenDialog(false)} onDelete={handleDelete} />
      </Container>
    </Box>
  );
}

export default FileStorage;
