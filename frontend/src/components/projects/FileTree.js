import React from "react";
import {
  List,
  ListItem,
  ListItemText,
  Collapse,
  IconButton,
  Typography,
  Box,
  Chip,
} from "@mui/material";
import {
  Folder,
  FolderOpen,
  InsertDriveFile,
  Delete as DeleteIcon,
} from "@mui/icons-material";
import { ExpandMore, ChevronRight } from "@mui/icons-material";
import ConfirmDialog from "../common/ConfirmDialog";

const FileTree = ({ files, user, onFileClick, onFileDelete, searchQuery }) => {
  const [expandedFolders, setExpandedFolders] = React.useState({});
  const [deleteDialog, setDeleteDialog] = React.useState({
    open: false,
    fileId: null,
    fileName: "",
  });

  const handleDeleteClick = (fileId, fileName, e) => {
    e.stopPropagation();
    setDeleteDialog({
      open: true,
      fileId,
      fileName,
    });
  };

  const handleDeleteConfirm = async () => {
    if (deleteDialog.fileId) {
      await onFileDelete(deleteDialog.fileId);
    }
    setDeleteDialog((prev) => {
      return { ...prev, open: false, fileId: null };
    });
  };

  const handleDeleteCancel = () => {
    setDeleteDialog((prev) => {
      return { ...prev, open: false, fileId: null };
    });
  };

  const toggleFolder = (path) => {
    setExpandedFolders((prev) => ({
      ...prev,
      [path]: !prev[path],
    }));
  };

  const buildTree = (files) => {
    const tree = {};

    files.forEach((file) => {
      if (
        searchQuery &&
        !file.filename
          .toLowerCase()
          .trim()
          .includes(searchQuery.toLowerCase().trim())
      )
        return;

      const pathParts = file.filename.split("/");
      let currentLevel = tree;

      pathParts.forEach((part, index) => {
        if (!currentLevel[part]) {
          currentLevel[part] = {};
        }

        if (index === pathParts.length - 1) {
          if (!currentLevel[part].files) {
            currentLevel[part].files = [];
          }
          currentLevel[part].files.push(file);
        } else {
          currentLevel = currentLevel[part];
        }
      });
    });

    return tree;
  };

  const getDepth = (path) => {
    return path.split("/").length - 1;
  };

  const renderTree = (nodes, path = "") => {
    if (!Object.keys(nodes).length)
      return <Typography sx={{ p: 2 }}>Файлы не найдены</Typography>;

    return Object.keys(nodes).map((key) => {
      const node = nodes[key];
      const currentPath = path ? `${path}/${key}` : key;
      const isFolder = !node.files;
      const depth = getDepth(currentPath);

      if (isFolder) {
        return (
          <div key={currentPath}>
            <ListItem
              button="true"
              onClick={() => toggleFolder(currentPath)}
              sx={{
                pl: depth * 2 + 2,
                cursor: "pointer",
              }}
            >
              <IconButton size="small">
                {expandedFolders[currentPath] ? <FolderOpen /> : <Folder />}
              </IconButton>
              <ListItemText primary={key} />
              {expandedFolders[currentPath] ? <ExpandMore /> : <ChevronRight />}
            </ListItem>
            <Collapse
              in={expandedFolders[currentPath]}
              timeout="auto"
              unmountOnExit
            >
              <List component="div" disablePadding>
                {renderTree(node, currentPath)}
              </List>
            </Collapse>
          </div>
        );
      }

      return node.files.map((file, index) => (
        <ListItem
          key={`${file.id}-${index}`}
          button="true"
          onClick={() => onFileClick(file)}
          sx={{
            pl: depth * 2 + 2,
            cursor: "pointer",
          }}
          secondaryAction={
            <Box flexDirection="row" display="flex" alignItems="center">
              <Chip label={`v${index + 1}`} size="small" sx={{ mr: 1 }} />
              <Typography variant="body2" color="text.secondary">
                {file.language || "Unknown"}
              </Typography>
              {user && user.id === file.project.owner.id && (
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={(e) => handleDeleteClick(file.id, key, e)}
                >
                  <DeleteIcon />
                </IconButton>
              )}
            </Box>
          }
        >
          <IconButton size="small">
            <InsertDriveFile />
          </IconButton>
          <ListItemText
            primary={index === 0 ? key : `${key} (v${index + 1})`}
            secondary={new Date(file.modified_timestamp * 1000).toLocaleString(
              "ru-RU"
            )}
          />
        </ListItem>
      ));
    });
  };

  const tree = buildTree(files);

  return (
    <>
      <List>{renderTree(tree)}</List>

      <ConfirmDialog
        open={deleteDialog.open}
        onClose={handleDeleteCancel}
        onConfirm={handleDeleteConfirm}
        title="Удалить файл"
        message={`Вы уверены, что хотите удалить "${deleteDialog.fileName}"?`}
      />
    </>
  );
};

export default FileTree;
