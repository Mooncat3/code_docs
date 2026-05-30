import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@mui/material";
import ArrowBackIosIcon from "@mui/icons-material/ArrowBackIos";

const NavButton = ({ label = "Назад", url }) => {
  const navigate = useNavigate();

  return (
    <Button
      color="primary"
      startIcon={<ArrowBackIosIcon />}
      onClick={() => navigate(url)}
      sx={{ marginBottom: 1 }}
    >
      {label}
    </Button>
  );
};

export default NavButton;
