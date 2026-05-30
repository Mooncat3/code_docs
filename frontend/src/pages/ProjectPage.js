import React, { useState, useEffect, useContext } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { AuthContext } from "../contexts/AuthContext";
import { getProject, updateProject, deleteProject } from "../api/projects";
import { getProjectFiles, deleteFile } from "../api/files";
import {
  Box,
  Button,
  Typography,
  Container,
  Paper,
  IconButton,
  TextField,
  Switch,
  FormControlLabel,
  CircularProgress,
  Divider,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import FileUploader from "../components/projects/FileUploader";
import FileTree from "../components/projects/FileTree";
import ConfirmDialog from "../components/common/ConfirmDialog";

const ProjectPage = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [editedProject, setEditedProject] = useState({});
  const [openDeleteProject, setOpenDeleteProject] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [projectData, filesData] = await Promise.all([
          getProject(projectId),
          getProjectFiles(projectId),
        ]);
        setProject(projectData);
        setEditedProject({
          title: projectData.title,
          description: projectData.description,
          is_public: projectData.is_public,
        });
        setFiles(filesData);
      } catch (error) {
        console.error("Error fetching project:", error);
        //navigate("/projects");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [projectId, navigate]);

  const handleUpdateProject = async () => {
    try {
      const updatedProject = await updateProject(projectId, editedProject);
      setProject(updatedProject);
      setEditMode(false);
    } catch (error) {
      console.error("Error updating project:", error);
    }
  };

  const handleDeleteProject = async () => {
    try {
      await deleteProject(projectId);
      navigate("/projects");
    } catch (error) {
      console.error("Error deleting project:", error);
    }
  };

  const handleUploadSuccess = async () => {
    try {
      const filesData = await getProjectFiles(projectId);
      setFiles(filesData);
    } catch (error) {
      console.error("Error fetching files:", error);
    }
  };

  const handleFileClick = (file) => {
    navigate(`/projects/${projectId}/files/${file.id}`);
  };

  const handleFileDelete = async (fileId) => {
    try {
      await deleteFile(fileId);
      const updatedFiles = files.filter((file) => file.id !== fileId);
      setFiles(updatedFiles);
    } catch (error) {
      console.error("Error deleting file:", error);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!project) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
        <Typography>Проект не найден</Typography>
      </Box>
    );
  }

  return (
    <>
      <ConfirmDialog
        open={openDeleteProject}
        onConfirm={handleDeleteProject}
        onClose={() => setOpenDeleteProject(false)}
        title="Удалить проект"
        message="Вы уверены, что хотите удалить проект?"
      />

      <Container maxWidth="lg">
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Typography variant="h6" sx={{ marginRight: 4 }}>
            Файлы
          </Typography>

          <TextField
            fullWidth
            variant="outlined"
            label="Поиск по файлам"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            sx={{ marginLeft: "auto", width: "50%" }}
          />

          {user && user.id === project.owner.id && (
            <FileUploader
              projectId={projectId}
              onUploadSuccess={handleUploadSuccess}
            />
          )}
        </Box>

        <Paper elevation={3} sx={{ maxHeight: "500px", overflow: "auto" }}>
          {files.length > 0 ? (
            <FileTree
              files={files}
              user={user}
              onFileClick={handleFileClick}
              onFileDelete={handleFileDelete}
              searchQuery={searchQuery}
            />
          ) : (
            <Typography sx={{ p: 2 }}>
              Файлы не найдены. Загрузите первые файлы для проекта!
            </Typography>
          )}
        </Paper>

        <Divider sx={{ my: 4 }} />

        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 3,
          }}
        >
          {editMode ? (
            <TextField
              label="Название"
              value={editedProject.title}
              onChange={(e) =>
                setEditedProject({ ...editedProject, title: e.target.value })
              }
              fullWidth
            />
          ) : (
            <Typography
              variant="h4"
              sx={{ overflowWrap: "anywhere", fontWeight: "bold" }}
            >
              {project.title}
            </Typography>
          )}
          {user && user.id === project.owner.id && (
            <Box display="flex">
              <IconButton onClick={() => setEditMode(!editMode)}>
                <EditIcon />
              </IconButton>
              <IconButton onClick={() => setOpenDeleteProject(true)}>
                <DeleteIcon />
              </IconButton>
            </Box>
          )}
        </Box>

        {editMode ? (
          <Box sx={{ mb: 3 }}>
            <TextField
              label="Описание"
              multiline
              rows={6}
              fullWidth
              value={editedProject.description || ""}
              onChange={(e) =>
                setEditedProject({
                  ...editedProject,
                  description: e.target.value,
                })
              }
            />
            <FormControlLabel
              control={
                <Switch
                  checked={editedProject.is_public}
                  onChange={(e) =>
                    setEditedProject({
                      ...editedProject,
                      is_public: e.target.checked,
                    })
                  }
                />
              }
              label="Публичность"
              sx={{ mt: 1 }}
            />
            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                onClick={handleUpdateProject}
                sx={{ mr: 2 }}
              >
                Сохранить
              </Button>
              <Button variant="outlined" onClick={() => setEditMode(false)}>
                Отменить
              </Button>
            </Box>
          </Box>
        ) : (
          <Typography
            variant="body1"
            sx={{ mb: 3, overflowWrap: "break-word" }}
          >
            {project.description || "Нет описания"}
          </Typography>
        )}

        <Divider sx={{ my: 4 }} />

        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Typography variant="h6">Документация</Typography>
          <Button
            variant="contained"
            onClick={() => navigate(`/projects/${projectId}/docs`)}
          >
            Открыть документацию
          </Button>
        </Box>
      </Container>
    </>
  );
};

export default ProjectPage;
