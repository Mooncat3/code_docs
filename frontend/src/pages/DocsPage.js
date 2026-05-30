import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getProjectDocumentation } from "../api/docs";
import {
  Box,
  Container,
  CircularProgress,
  Paper,
  Typography,
  TextField,
} from "@mui/material";
import NavButton from "../components/common/NavButton";

const DocsPage = () => {
  const { projectId } = useParams();
  const [htmlContent, setHtmlContent] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDocumentation = async () => {
      try {
        const content = await getProjectDocumentation(projectId, searchQuery);
        setHtmlContent(content);
      } catch (error) {
        console.error("Error fetching documentation:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchDocumentation();
  }, [projectId, searchQuery]);

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      <Box display="flex" width={"100%"} marginBottom={3}>
        <NavButton url={`/projects/${projectId}`} />

        <TextField
          fullWidth
          variant="outlined"
          label="Поиск по названиям сущностей"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{ marginLeft: "auto", width: "50%" }}
        />
      </Box>

      <Paper elevation={3} sx={{ p: 3, mb: 3, overflow: "auto" }}>
        {htmlContent ? (
          <div
            dangerouslySetInnerHTML={{
              __html: htmlContent,
            }}
          />
        ) : (
          <Typography>
            Документации не существует, либо она недоступна.
          </Typography>
        )}
      </Paper>
    </Container>
  );
};

export default DocsPage;
