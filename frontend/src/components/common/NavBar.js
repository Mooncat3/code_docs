import React, { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../../contexts/AuthContext";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
} from "@mui/material";
import CodeIcon from "@mui/icons-material/Code";

const NavBar = () => {
  const { user, signOut } = useContext(AuthContext);
  const [anchorEl, setAnchorEl] = React.useState(null);
  const navigate = useNavigate();

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    signOut();
    navigate("/login");
    handleMenuClose();
  };

  return (
    <AppBar position="static" sx={{ marginBottom: 4 }}>
      <Toolbar>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            mr: 2,
            textDecoration: "none",
            color: "inherit",
          }}
          component={Link}
          to="/"
        >
          <CodeIcon sx={{ mr: 1 }} />
          <Typography variant="h6">CodeDocs</Typography>
        </Box>

        <Box sx={{ flexGrow: 1 }} />

        <Button color="inherit" component={Link} to="/search">
          Поиск проектов
        </Button>

        {user ? (
          <>
            {user.role === "admin" && (
              <Button color="inherit" component={Link} to="/admin">
                Админ-панель
              </Button>
            )}
            <IconButton onClick={handleMenuOpen} sx={{ ml: 2 }}>
              <Avatar sx={{ width: 32, height: 32 }}>
                {user.username.charAt(0).toUpperCase()}
              </Avatar>
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
            >
              <MenuItem
                onClick={() => {
                  navigate("/projects");
                  handleMenuClose();
                }}
              >
                Мои проекты
              </MenuItem>
              <MenuItem onClick={handleLogout}>Выйти</MenuItem>
            </Menu>
          </>
        ) : (
          <>
            <Button color="inherit" component={Link} to="/login">
              Вход
            </Button>
            <Button color="inherit" component={Link} to="/register">
              Регистрация
            </Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default NavBar;
