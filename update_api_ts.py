import codecs

path = 'taskrebuild/extension/src/lib/api.ts'
with open(path, 'a', encoding='utf-8') as f:
    f.write("\nexport const generateLearningPath = (taskId: string) => fetchApi(`/api/tasks/${taskId}/learning-path`, { method: 'POST' });\n")
    f.write("export const getLearningPath = (taskId: string) => fetchApi(`/api/tasks/${taskId}/learning-path`);\n")
