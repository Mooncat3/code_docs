import axiosInstance from "./axiosInstance";

export const getProjects = async () => {
  const response = await axiosInstance.get("/projects/my/");
  return response.data;
};

export const getProject = async (projectId) => {
  const response = await axiosInstance.get(`/projects/${projectId}`);
  return response.data;
};

export const createProject = async (projectData) => {
  const response = await axiosInstance.post("/projects/", projectData);
  return response.data;
};

export const updateProject = async (projectId, projectData) => {
  const response = await axiosInstance.put(
    `/projects/${projectId}`,
    projectData
  );
  return response.data;
};

export const deleteProject = async (projectId) => {
  const response = await axiosInstance.delete(`/projects/${projectId}`);
  return response.data;
};

export const uploadFiles = async (projectId, formData) => {
  const response = await axiosInstance.post(
    `/projects/${projectId}/files`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );
  return response.data;
};

export const searchPublicProjects = async (
  query = "",
  skip = 0,
  limit = 10
) => {
  const response = await axiosInstance.get("/projects/", {
    params: {
      query,
      skip,
      limit,
    },
  });
  return {
    projects: response.data.projects,
    totalCount: response.data.total_count,
  };
};
