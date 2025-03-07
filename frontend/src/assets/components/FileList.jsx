import React from "react";
import { List, ListItem, ListItemIcon, ListItemText, Button, Paper } from "@mui/material";
import FolderIcon from "@mui/icons-material/Folder";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";

const FileList = ({ files, onDownload, onVerify, onDelete }) => {
  return (
    <Paper elevation={3} sx={{ padding: 2 }}>
      <List>
        {files.map((file, index) => (
          <ListItem key={index}>
            <ListItemIcon>
              {file.s3_url.endsWith("/") ? <FolderIcon color="primary" /> : <InsertDriveFileIcon color="action" />}
            </ListItemIcon>
            <ListItemText primary={file.filename} />
            <Button variant="contained" size="small" onClick={() => onDownload(file.filename)}>
              Download
            </Button>
            <Button variant="outlined" size="small" onClick={() => onVerify(file.filename)}>
              Verify
            </Button>
            <Button variant="outlined" size="small" color="error" onClick={() => onDelete(file.filename)}>
              Delete
            </Button>
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default FileList;
