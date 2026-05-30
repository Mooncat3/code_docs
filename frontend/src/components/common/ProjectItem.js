import React from "react";
import { useNavigate } from "react-router-dom";
import { ListItem, ListItemText, Chip, Divider } from "@mui/material";

const ProjectItem = ({ project, isSearch = false }) => {
  const navigate = useNavigate();

  return (
    <React.Fragment key={project.id}>
      <ListItem
        button="true"
        onClick={() => navigate(`/projects/${project.id}`)}
        secondaryAction={
          !isSearch ? (
            <Chip
              label={project.is_public ? "Публичный" : "Приватный"}
              color={project.is_public ? "success" : "default"}
              size="small"
            />
          ) : (
            <></>
          )
        }
        sx={{ cursor: "pointer" }}
      >
        <ListItemText
          primary={project.title}
          secondary={project.description || "Нет описания"}
          slotProps={{
            secondary: { noWrap: true },
            primary: { fontSize: 24, fontWeight: "bold" },
          }}
          sx={{ maxWidth: "90%" }}
        />
      </ListItem>
      <Divider />
    </React.Fragment>
  );
};

export default ProjectItem;
