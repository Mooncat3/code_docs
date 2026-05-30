import React, { useState } from "react";
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
} from "@mui/material";
import UploadIcon from "@mui/icons-material/Upload";
import { uploadFiles } from "../../api/projects";

const FileUploader = ({ projectId, onUploadSuccess }) => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState([]);

  const handleFileChange = (e) => {
    const fileList = Array.from(e.target.files);
    setFiles(fileList);
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    setLoading(true);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file, file.webkitRelativePath || file.name);
    });

    try {
      await uploadFiles(projectId, formData);
      onUploadSuccess();
      setOpen(false);
      setFiles([]);
    } catch (error) {
      console.error("Error uploading files:", error);
    }
    setLoading(false);
  };

  return (
    <>
      <Button
        variant="contained"
        startIcon={<UploadIcon />}
        onClick={() => setOpen(true)}
        sx={{ marginLeft: 4 }}
      >
        Загрузить файлы
      </Button>

      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Загрузить файлы</DialogTitle>
        <DialogContent>
          <input
            type="file"
            webkitdirectory=""
            directory=""
            multiple
            onChange={handleFileChange}
            style={{ display: "none" }}
            id="file-upload-input"
          />
          <label htmlFor="file-upload-input">
            <Button variant="contained" component="span" fullWidth>
              Выбрать папку
            </Button>
          </label>

          {files.length > 0 && (
            <div style={{ marginTop: "16px" }}>
              <h4>Выбранные файлы:</h4>
              <ul style={{ maxHeight: "200px", overflow: "auto" }}>
                {files.map((file, index) => (
                  <li key={index}>{file.webkitRelativePath || file.name}</li>
                ))}
              </ul>
            </div>
          )}
        </DialogContent>
        <DialogActions>
          {loading && <CircularProgress />}

          <Button onClick={() => setOpen(false)}>Отменить</Button>
          <Button
            onClick={handleUpload}
            disabled={files.length === 0}
            variant="contained"
            color="primary"
          >
            Загрузить
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default FileUploader;
