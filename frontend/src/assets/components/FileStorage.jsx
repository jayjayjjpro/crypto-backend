import { useState, useEffect } from "react";
import { Container, Typography, Box, Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from "@mui/material";
import axios from "axios";
import FileList from "./FileList";
import UploadButton from "./UploadButton";
import DeleteDialog from "./DeleteDialog";

const API_BASE_URL = "http://localhost:8000"; // Backend URL

function FileStorage({ onLogout }) {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [openLogoutConfirm, setOpenLogoutConfirm] = useState(false);
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
        const response = await axios.post(`${API_BASE_URL}/upload/`, formData, {
            headers: { "Content-Type": "multipart/form-data" }
        });

        console.log("API Response:", response.data); 

        if (response.data.error) {
            alert(`Error: ${response.data.error}\nFile: ${response.data.filename}`);
        } else {
            alert("File uploaded successfully!");
            fetchFiles(); 
        }
    } catch (error) {
        console.error("Error uploading file:", error);
        alert("An error occurred while uploading the file.");
    }
};



  const handleDownload = async (filename) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/files/${filename}/download/`, {
        responseType: "blob", // Important!
      });

      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename); // Force filename
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Error downloading file:", error);
      alert("Failed to download file.");
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
      {/* User Info and Logout Button positioned at the top-right */}
      {user && (
        <Box sx={{ position: "absolute", top: 16, right: 16, display: "flex", alignItems: "center", gap: 2 }}>
          <Typography variant="body1">👤 {user.email}</Typography>
          <Button variant="contained" color="secondary" onClick={() => setOpenLogoutConfirm(true)}>
            Logout
          </Button>
        </Box>
      )}

      <Container maxWidth="sm">
        {/* Header */}
        <Typography variant="h4" align="center" sx={{ mb: 2 }}>📂 My File Storage</Typography>

        {/* Upload Button */}
        <UploadButton onUpload={handleFileUpload} />

        {/* File List */}
        <FileList files={files} onDownload={handleDownload} onVerify={handleVerify} onDelete={confirmDelete} />

        {/* Delete Confirmation Dialog */}
        <DeleteDialog open={openDialog} file={selectedFile} onClose={() => setOpenDialog(false)} onDelete={handleDelete} />
      </Container>

      {/* 🚀 Logout Confirmation Dialog (NEW) */}
      <Dialog open={openLogoutConfirm} onClose={() => setOpenLogoutConfirm(false)}>
        <DialogTitle>Confirm Logout</DialogTitle>
        <DialogContent>
          <DialogContentText>Are you sure you want to log out?</DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenLogoutConfirm(false)} color="primary">Cancel</Button>
          <Button onClick={onLogout} color="secondary" variant="contained">Confirm Logout</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
  
}

export default FileStorage;
