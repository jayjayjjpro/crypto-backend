import { useState, useEffect } from "react";
import { Container, Typography, Button, Paper, List, ListItem, ListItemIcon, ListItemText, Box, Stack, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import FolderIcon from "@mui/icons-material/Folder";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";
import axios from "axios";

const API_BASE_URL = "http://localhost:8000";  // Change this to match your backend URL

function App() {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);

  // Fetch the list of uploaded files
  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/files/`);
      setFiles(response.data);
    } catch (error) {
      console.error("Error fetching files:", error);
    }
  };

  // Handle File Upload
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      console.log("Upload success:", response.data);
      fetchFiles(); // Refresh file list after upload
    } catch (error) {
      console.error("Error uploading file:", error);
    }
  };

  // Handle File Download
  const handleDownload = async (filename) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/files/${filename}/download/`);
      window.open(response.data.presigned_url, "_blank");
    } catch (error) {
      console.error("Error generating download link:", error);
    }
  };

  // Handle File Integrity Verification
  const handleVerify = async (filename) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/files/${filename}/verify/`);
      alert(response.data.is_valid ? "File is valid!" : "File integrity check failed!");
    } catch (error) {
      console.error("Error verifying file:", error);
    }
  };

  // Open Confirmation Dialog
  const confirmDelete = (filename) => {
    setSelectedFile(filename);
    setOpenDialog(true);
  };

  // Handle Delete File
  const handleDelete = async () => {
    if (!selectedFile) return;

    try {
      await axios.delete(`${API_BASE_URL}/files/${selectedFile}/delete/`);
      fetchFiles(); // Refresh file list after deletion
    } catch (error) {
      console.error("Error deleting file:", error);
    }
    
    // Close Dialog
    setOpenDialog(false);
    setSelectedFile(null);
  };

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        flexDirection: "column",
      }}
    >
      <Container maxWidth="sm">
        <Typography variant="h4" align="center" gutterBottom>
          📂 My File Storage
        </Typography>

        {/* Upload Button */}
        <Stack direction="row" justifyContent="center" sx={{ mb: 2 }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<CloudUploadIcon />}
            component="label"
          >
            Upload File
            <input type="file" hidden onChange={handleFileUpload} />
          </Button>
        </Stack>

        {/* File List */}
        <Paper elevation={3} sx={{ padding: 2 }}>
          <List>
            {files.map((file, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {file.s3_url.endsWith("/") ? <FolderIcon color="primary" /> : <InsertDriveFileIcon color="action" />}
                </ListItemIcon>
                <ListItemText primary={file.filename} />
                <Button variant="contained" size="small" onClick={() => handleDownload(file.filename)}>
                  Download
                </Button>
                <Button variant="outlined" size="small" onClick={() => handleVerify(file.filename)}>
                  Verify
                </Button>
                <Button variant="outlined" size="small" color="error" onClick={() => confirmDelete(file.filename)}>
                  Delete
                </Button>
              </ListItem>
            ))}
          </List>
        </Paper>
      </Container>

      {/* Delete Confirmation Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete <strong>{selectedFile}</strong>? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDelete} color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default App;
