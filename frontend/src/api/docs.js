import axiosInstance from "./axiosInstance";

export const getEntity = async (entityId) => {
  const response = await axiosInstance.get(`/docs/entities/${entityId}`);
  return response.data;
};

export const updateEntityDocs = async (entityId, docs, visibility) => {
  const response = await axiosInstance.put(`/docs/entities/${entityId}`, {
    docs,
    visibility,
  });
  return response.data;
};

export const getProjectDocumentation = async (projectId, searchQuery) => {
  const response = await axiosInstance.get(
    `/docs/project/${projectId}/search`,
    {
      params: {
        query: searchQuery,
      },
    }
  );
  return response.data;
};
