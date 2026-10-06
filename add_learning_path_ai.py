import codecs

# 1. Update interface.py
path = 'render-backend/app/services/ai/interface.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
if "generate_learning_path" not in content:
    content = content.replace("    @abstractmethod", "    @abstractmethod\n    async def generate_learning_path(self, task_name: str, nodes: list, edges: list) -> str:\n        pass\n\n    @abstractmethod")
    with open(path, 'w', encoding='utf-8') as f: f.write(content)

# 2. Update placeholder.py
path = 'render-backend/app/services/ai/placeholder.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
if "generate_learning_path" not in content:
    content = content.replace("    async def analyze_task", "    async def generate_learning_path(self, task_name: str, nodes: list, edges: list) -> str:\n        return '# Placeholder Learning Path'\n\n    async def analyze_task")
    with open(path, 'w', encoding='utf-8') as f: f.write(content)

# 3. Update gemini_provider.py
path = 'render-backend/app/services/ai/gemini_provider.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
if "generate_learning_path" not in content:
    gemini_func = """
    async def generate_learning_path(self, task_name: str, nodes: list, edges: list) -> str:
        if not self.api_key:
            raise ValueError("Gemini API Key is not configured.")

        prompt = f\"\"\"
You are an expert technical instructor and technical writer. 
The user has been researching a topic called '{task_name}'. 
We have extracted their research into a Knowledge Graph with the following Nodes and Edges:

Nodes:
{json.dumps(nodes, indent=2)}

Edges:
{json.dumps(edges, indent=2)}

INSTRUCTIONS:
Using ONLY the provided Knowledge Graph data, generate a comprehensive, logically sequenced "Learning Path" document in Markdown format.
The document must include:
1. **Introduction**: A brief overview of what this learning path covers.
2. **Prerequisites**: Identify foundational concepts (nodes that have many outgoing edges or act as roots).
3. **The Learning Sequence**: A step-by-step, ordered path through the topics. For each step, provide a clear explanation of how it relates to the previous steps, referencing the specific URLs or resources from the nodes.
4. **Expected Outcomes**: What the user will have mastered by completing this path.

Format the output entirely in clean, readable Markdown (no json or extra markdown tags). Make it look like professional documentation.
\"\"\"
        try:
            model = genai.GenerativeModel(self.model_name)
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini Learning Path error: {e}")
            raise
"""
    content = content + gemini_func
    with open(path, 'w', encoding='utf-8') as f: f.write(content)

# 4. Update service.py
path = 'render-backend/app/services/ai/service.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
if "generate_learning_path" not in content:
    service_func = """
    async def generate_learning_path(self, task_name: str, nodes: list, edges: list) -> str:
        if not settings.AI_ENABLED:
            raise HTTPException(status_code=503, detail="AI analysis is temporarily unavailable or disabled.")
        
        provider = self.providers.get(settings.GRAPH_AI_PROVIDER, self.placeholder)
        if not provider:
             provider = self.placeholder

        try:
            return await provider.generate_learning_path(task_name, nodes, edges)
        except Exception as e:
            logger.error(f"AI learning path generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"AI learning path failed: {e}")
"""
    content = content + service_func
    with open(path, 'w', encoding='utf-8') as f: f.write(content)
