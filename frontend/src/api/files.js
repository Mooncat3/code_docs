import axiosInstance from "./axiosInstance";

export const getFile = async (fileId) => {
  const response = await axiosInstance.get(`/files/${fileId}`);
  return response.data;
};

export const getProjectFiles = async (projectId) => {
  const response = await axiosInstance.get(`/files/project/${projectId}`);
  return response.data;
};

export const getFileEntities = async (fileId) => {
  const response = await axiosInstance.get(`/files/entities/${fileId}`);
  return response.data;
};

export const deleteFile = async (fileId) => {
  const response = await axiosInstance.delete(`/files/${fileId}`);
  return response.data;
};
