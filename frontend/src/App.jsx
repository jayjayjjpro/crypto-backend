import { useState } from "react";
import { Container, Typography, Button, Grid, Paper, List, ListItem, ListItemIcon, ListItemText } from "@mui/material";
import { CloudUpload, Folder, InsertDriveFile } from "@mui/icons-material";

function App() {
  const [files, setFiles] = useState([
    { name: "Document.pdf", type: "file" },
    { name: "Project Folder", type: "folder" },
  ]);

  return (
    <Container maxWidth="md">
      <Typography variant="h4" align="center" gutterBottom>
        📂 My File Storage
      </Typography>
      
      {/* Upload Button */}
      <Button variant="contained" color="primary" startIcon={<CloudUpload />} sx={{ mb: 2 }}>
        Upload File
      </Button>

      {/* File List */}
      <Paper elevation={3} sx={{ padding: 2 }}>
        <List>
          {files.map((file, index) => (
            <ListItem key={index}>
              <ListItemIcon>
                {file.type === "folder" ? <Folder color="primary" /> : <InsertDriveFile color="action" />}
              </ListItemIcon>
              <ListItemText primary={file.name} />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Container>
  );
}

export default App;
