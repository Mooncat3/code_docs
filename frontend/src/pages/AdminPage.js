import React, { useState, useEffect, useContext } from "react";
import { AuthContext } from "../contexts/AuthContext";
import { getUsers, deleteUser, editUser } from "../api/users";
import {
  Box,
  Typography,
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Button,
  Switch,
  FormControlLabel,
} from "@mui/material";
import ConfirmDialog from "../components/common/ConfirmDialog";

const AdminPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState(null);
  const { user } = useContext(AuthContext);

  const fetchUsers = async () => {
    try {
      const usersData = await getUsers();
      setUsers(usersData);
    } catch (error) {
      console.error("Error fetching users:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleDeleteUser = async () => {
    if (!selectedUser || selectedUser.id === user.id) return;
    try {
      await deleteUser(selectedUser.id);
      setUsers((prev) => prev.filter((e) => e.id !== selectedUser.id));
      setSelectedUser(null);
    } catch (error) {
      console.error("Error delete user:", error);
    } finally {
      setSelectedUser(null);
    }
  };

  const handleEditUser = async (currentUser, data) => {
    if (!currentUser || currentUser.id === user.id) return;
    try {
      await editUser(currentUser.id, data);
      fetchUsers();
    } catch (error) {
      console.error("Error edit user:", error);
    }
  };

  if (!user || user.role !== "admin") {
    return (
      <Container>
        <Typography variant="h4" color="error">
          Доступ запрещен
        </Typography>
        <Typography>У вас нет разрешения на доступ к этой странице.</Typography>
      </Container>
    );
  }

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <>
      <ConfirmDialog
        open={!!selectedUser}
        onClose={() => setSelectedUser(null)}
        onConfirm={handleDeleteUser}
        title="Удалить пользователя"
        message="Вы действительно хотите удалить пользователя?"
      ></ConfirmDialog>

      <Container maxWidth="lg">
        <Typography variant="h4" sx={{ mb: 3 }}>
          Панель администратора
        </Typography>

        <Typography variant="h5" sx={{ mb: 2 }}>
          Управление пользователями
        </Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Имя пользователя</TableCell>
                <TableCell>Почта</TableCell>
                <TableCell>Роль</TableCell>
                <TableCell>Дата регистрации</TableCell>
                <TableCell>Активен</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.username}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{user.role}</TableCell>
                  <TableCell>
                    {new Date(
                      user.register_timestamp * 1000
                    ).toLocaleDateString("ru-RU")}
                  </TableCell>
                  <TableCell>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={user.is_active}
                          onChange={async (e) => {
                            await handleEditUser(user, {
                              is_active: e.target.checked,
                            });
                          }}
                        />
                      }
                    />
                  </TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      color="error"
                      onClick={() => {
                        setSelectedUser(user);
                      }}
                    >
                      Удалить
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Container>
    </>
  );
};

export default AdminPage;
