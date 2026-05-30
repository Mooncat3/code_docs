import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getProjects, createProject } from "../api/projects";
import {
  Box,
  Button,
  Typography,
  Container,
  Paper,
  List,
  ListItem,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Switch,
  FormControlLabel,
  CircularProgress,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import ProjectItem from "../components/common/ProjectItem";

const ProjectsPage = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [newProject, setNewProject] = useState({
    title: "",
    description: "",
    is_public: false,
  });
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await getProjects();
        setProjects(data);
      } catch (error) {
        console.error("Error fetching projects:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchProjects();
  }, []);

  const handleCreateProject = async () => {
    try {
      const createdProject = await createProject(newProject);
      setProjects([...projects, createdProject]);
      setOpenDialog(false);
      setNewProject({ title: "", description: "", is_public: false });
      navigate(`/projects/${createdProject.id}`);
    } catch (error) {
      console.error("Error creating project:", error);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }
  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h4">Мои проекты</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Новый проект
        </Button>
      </Box>

      <Paper elevation={3}>
        <List>
          {projects.map((project) => (
            <ProjectItem project={project} key={project.id} />
          ))}
          {projects.length === 0 && (
            <ListItem>
              <ListItemText primary="Проекты не найдены. Создайте свой первый проект!" />
            </ListItem>
          )}
        </List>
      </Paper>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Создать проект</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Название"
            fullWidth
            value={newProject.title}
            onChange={(e) =>
              setNewProject({ ...newProject, title: e.target.value })
            }
          />
          <TextField
            margin="dense"
            label="Описание"
            fullWidth
            multiline
            rows={3}
            value={newProject.description}
            onChange={(e) =>
              setNewProject({ ...newProject, description: e.target.value })
            }
          />
          <FormControlLabel
            control={
              <Switch
                checked={newProject.is_public}
                onChange={(e) =>
                  setNewProject({ ...newProject, is_public: e.target.checked })
                }
              />
            }
            label="Публичность"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Отменить</Button>
          <Button
            onClick={handleCreateProject}
            variant="contained"
            color="primary"
          >
            Создать
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ProjectsPage;
