import React, { useState, useEffect, useContext } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getFile, getFileEntities } from "../api/files";
import { AuthContext } from "../contexts/AuthContext";
import { updateEntityDocs } from "../api/docs";
import {
  Box,
  Typography,
  Container,
  Paper,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  TextField,
  Button,
  CircularProgress,
  Divider,
  FormControlLabel,
  Switch,
  IconButton,
} from "@mui/material";
import Editor from "@monaco-editor/react";
import CodeIcon from "@mui/icons-material/Code";
import DescriptionIcon from "@mui/icons-material/Description";
import NavButton from "../components/common/NavButton";
import CheckIcon from "@mui/icons-material/Check";
import DownloadIcon from "@mui/icons-material/Download";

const DownloadButton = ({ text, filename }) => {
  const download = (text, filename) => {
    const file = new File([text], filename, {
      type: "text/plain",
    });
    const link = document.createElement("a");
    const url = URL.createObjectURL(file);
    link.href = url;
    link.download = file.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  return (
    <IconButton
      sx={{ position: "absolute", bottom: 12, right: 20 }}
      size="large"
      onClick={() => download(text, filename)}
    >
      <DownloadIcon fontSize="large" color="primary" />
    </IconButton>
  );
};

const CustomEditor = ({ file, isModified = false }) => {
  const getLanguage = (language) => {
    if (!language) return "plaintext";
    const lang = language.toLowerCase().trim();
    if (lang === "c++") return "cpp";
    else if (lang === "c#") return "csharp";
    else if (lang === "tsx") return "typescript";
    else if (lang === "jsx") return "javascript";
    else if (lang === "transact-sql") return "sql";
    return lang;
  };

  return (
    <Box position="relative" sx={{ flex: 1, p: 1 }}>
      <Paper elevation={3} sx={{ height: "100%" }}>
        <Editor
          height="100%"
          language={getLanguage(file?.language)}
          value={isModified ? file.modified_content : file.original_content}
          options={{
            readOnly: true,
            minimap: { enabled: false },
          }}
        />
      </Paper>
      <DownloadButton
        text={isModified ? file.modified_content : file.original_content}
        filename={file.filename.split("/").pop()}
      />
    </Box>
  );
};

const EditorPage = () => {
  const { projectId, fileId } = useParams();
  const [file, setFile] = useState(null);
  const [entities, setEntities] = useState([]);

  const [selectedEntity, setSelectedEntity] = useState(null);
  const [showCheck, setShowCheck] = useState(false);
  const [docsValue, setDocsValue] = useState("");

  const [tabValue, setTabValue] = useState("original");
  const [loading, setLoading] = useState(true);
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  const fetchData = async () => {
    try {
      const [fileData, entitiesData] = await Promise.all([
        getFile(fileId),
        getFileEntities(fileId),
      ]);
      setFile(fileData);
      setEntities(entitiesData);
    } catch (error) {
      console.error("Error fetching file:", error);
      //navigate(`/projects/${projectId}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [fileId, projectId, navigate]);

  const handleEntitySelect = (entity) => {
    if (!user || user.id !== file.project.owner.id) return;
    setTabValue("documentation");
    setSelectedEntity(entity);
  };

  useEffect(() => {
    if (!showCheck) return;
    const timeout = setTimeout(() => setShowCheck(false), 1500);
    return () => clearTimeout(timeout);
  }, [showCheck]);

  useEffect(() => {
    if (!selectedEntity) return;
    setDocsValue(
      selectedEntity.modified_docs || selectedEntity.original_docs || ""
    );
  }, [selectedEntity]);

  const handleDocsUpdate = async () => {
    try {
      const updatedEntity = await updateEntityDocs(
        selectedEntity.id,
        docsValue,
        selectedEntity.visibility
      );
      setEntities(
        entities.map((e) => (e.id === updatedEntity.id ? updatedEntity : e))
      );
      setSelectedEntity(updatedEntity);
      setShowCheck(true);
      await fetchData();
    } catch (error) {
      console.error("Error updating documentation:", error);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!file) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
        <Typography>Файл не найден</Typography>
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      <NavButton url={`/projects/${projectId}`} />

      <Typography variant="h4" sx={{ mb: 1 }}>
        {file.filename}
      </Typography>

      <Paper
        elevation={3}
        sx={{
          display: "flex",
          height: "75vh",
          p: 2,
          borderRadius: 3,
        }}
      >
        <Box sx={{ width: "30%", mr: 2, overflow: "auto" }}>
          <Typography variant="h6">
            {entities.length
              ? "Сущности в коде"
              : "В коде не найдено сущностей"}
          </Typography>

          <List>
            {entities.map((entity) => (
              <ListItem
                key={entity.id}
                button="true"
                selected={selectedEntity?.id === entity.id}
                onClick={() => handleEntitySelect(entity)}
                sx={{ cursor: "pointer" }}
              >
                <ListItemText
                  primary={entity.name}
                  secondary={`${entity.type} (lines ${entity.line_start}-${entity.line_end})`}
                />
              </ListItem>
            ))}
          </List>
        </Box>

        <Box
          sx={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
          }}
        >
          <Tabs
            value={tabValue}
            onChange={(e, newValue) => setTabValue(newValue)}
            sx={{ minHeight: 70, maxHeight: 70 }}
          >
            <Tab icon={<CodeIcon />} label="Исходный" value="original" />
            {file.modified_content !== null && (
              <Tab icon={<CodeIcon />} label="Измененный" value="modified" />
            )}
            {selectedEntity && (
              <Tab
                icon={<DescriptionIcon />}
                label="Документация"
                value="documentation"
              />
            )}
          </Tabs>

          {tabValue === "original" && <CustomEditor file={file} />}

          {tabValue === "modified" && (
            <CustomEditor file={file} isModified={true} />
          )}

          {tabValue === "documentation" && selectedEntity && (
            <Paper elevation={3} sx={{ p: 2, overflow: "auto" }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                {selectedEntity.name} ({selectedEntity.type})
              </Typography>
              <TextField
                label="Описание"
                multiline
                fullWidth
                rows={10}
                value={docsValue}
                onChange={(e) => setDocsValue(e.target.value)}
              />
              <Typography color="textSecondary" sx={{ mb: 2 }} fontSize={12}>
                Поддержка HTML и MarkdownV2
              </Typography>

              <FormControlLabel
                control={
                  <Switch
                    checked={selectedEntity.visibility}
                    onChange={(e) =>
                      setSelectedEntity({
                        ...selectedEntity,
                        visibility: e.target.checked,
                      })
                    }
                  />
                }
                label="Видимость в документации"
                sx={{ mb: 1 }}
              />

              <Box display={"flex"}>
                <Button variant="contained" onClick={handleDocsUpdate}>
                  Сохранить
                </Button>

                {showCheck && (
                  <CheckIcon
                    color="success"
                    sx={{ marginLeft: 3 }}
                    fontSize={"large"}
                  />
                )}
              </Box>

              <Divider sx={{ my: 3 }} />
              <Typography variant="subtitle1">
                Исходная документация:
              </Typography>
              <Paper
                elevation={0}
                sx={{ p: 2, backgroundColor: "grey.100", mt: 1 }}
              >
                <Typography variant="body2" whiteSpace="pre-wrap">
                  {selectedEntity.original_docs ||
                    "Исходная документация не найдена"}
                </Typography>
              </Paper>
            </Paper>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default EditorPage;
