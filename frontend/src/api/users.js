import axiosInstance from "./axiosInstance";

export const getUsers = async () => {
  const response = await axiosInstance.get(`/users/`);
  return response.data;
};

export const deleteUser = async (userId) => {
  const response = await axiosInstance.delete(`/users/${userId}`);
  return response.data;
};

export const editUser = async (userId, data) => {
  const response = await axiosInstance.put(`/users/${userId}`, data);
  return response.data;
};
