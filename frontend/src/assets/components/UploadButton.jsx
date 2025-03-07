import React from "react";
import { Button, Stack } from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";

const UploadButton = ({ onUpload }) => {
  return (
    <Stack direction="row" justifyContent="center" sx={{ mb: 2 }}>
      <Button variant="contained" color="primary" startIcon={<CloudUploadIcon />} component="label">
        Upload File
        <input type="file" hidden onChange={onUpload} />
      </Button>
    </Stack>
  );
};

export default UploadButton;
