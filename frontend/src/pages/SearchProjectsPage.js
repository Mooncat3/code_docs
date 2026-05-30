import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Container,
  Paper,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  Pagination,
  CircularProgress,
} from "@mui/material";
import { searchPublicProjects } from "../api/projects";
import ProjectItem from "../components/common/ProjectItem";

const SearchProjectsPage = () => {
  const [query, setQuery] = useState("");
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const limit = 20;

  const searchProjects = async () => {
    setLoading(true);
    try {
      const skip = (page - 1) * limit;
      const { projects, totalCount } = await searchPublicProjects(
        query,
        skip,
        limit
      );
      setProjects(projects);
      setTotalCount(totalCount);
    } catch (error) {
      console.error("Error searching projects:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    searchProjects();
  }, [page]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    searchProjects();
  };

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Поиск среди публичных проектов
      </Typography>

      <Paper component="form" onSubmit={handleSearch} sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: "flex", gap: 2 }}>
          <TextField
            fullWidth
            variant="outlined"
            label="Поиск проектов"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Поиск по названию или описанию..."
          />
          <Button
            type="submit"
            variant="contained"
            disabled={loading}
            sx={{ minWidth: 120 }}
          >
            Поиск
          </Button>
        </Box>
      </Paper>

      {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <Paper elevation={3}>
            <List>
              {projects.map((project) => (
                <ProjectItem
                  project={project}
                  key={project.id}
                  isSearch={true}
                />
              ))}
              {projects.length === 0 && (
                <ListItem>
                  <ListItemText primary="Проекты не найдены" />
                </ListItem>
              )}
            </List>
          </Paper>

          {projects.length > 0 && totalCount > limit && (
            <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
              <Pagination
                count={Math.ceil(totalCount / limit)}
                page={page}
                onChange={handlePageChange}
                color="primary"
              />
            </Box>
          )}
        </>
      )}
    </Container>
  );
};

export default SearchProjectsPage;
