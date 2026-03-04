import sys
import os
import re
from langchain_ollama import OllamaLLM
from utils.memory import UniversalMemory

class ProjectManagerBrain:
    def __init__(self):
        self.llm = OllamaLLM(model="qwen2.5:latest")
        self.memory = UniversalMemory(namespace="project_manager")
        self.base_projects_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "projects")
        
        if not os.path.exists(self.base_projects_dir):
            os.makedirs(self.base_projects_dir)

    def extract_project_name(self, input_text):
        """
        从输入文本中提取项目名称，如果提取不到则让 LLM 生成一个。
        """
        prompt = f"""
        请从以下需求描述中提取一个简洁的项目英文名称（作为文件夹名，只能包含字母、数字和下划线）：
        ---
        {input_text}
        ---
        如果描述中没有明确名称，请根据内容生成一个合适的英文名称。
        只输出名称，不要有任何其他文字。
        """
        name = self.llm.invoke(prompt).strip()
        # 移除非法字符
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        return name if name else "unnamed_project"

    def generate_design_doc(self, input_text):
        """
        利用 LLM 生成详细的需求设计文档。
        """
        prompt = f"""
        你是一位资深的系统架构师和产品经理。
        请根据以下原始需求，生成一份极其详尽的项目需求设计文档（Markdown 格式）。
        要求：
        1. **需求拆解**：将需求拆解到最细粒度（功能点级别）。
        2. **接口定义**：定义核心模块的接口（函数名、参数、返回值、功能描述）。
        3. **功能描述**：详细描述每个核心功能模块的逻辑和预期行为。
        4. **技术选型建议**：给出适合该项目的技术栈建议。
        
        原始需求：
        ---
        {input_text}
        ---
        请用中文输出，保持专业、严谨且易于开发人员阅读。
        """
        return self.llm.invoke(prompt)

    def process(self, input_text):
        # 1. 确定项目名称并创建目录
        project_name = self.extract_project_name(input_text)
        project_path = os.path.join(self.base_projects_dir, project_name)
        
        if not os.path.exists(project_path):
            os.makedirs(project_path)
            
        # 2. 生成设计文档
        design_doc_content = self.generate_design_doc(input_text)
        
        # 3. 写入 .md 文件
        file_name = f"{project_name}_requirement_design.md"
        file_path = os.path.join(project_path, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(design_doc_content)
            
        # 4. 保存记忆
        self.memory.save(project_name, input_text, f"Project created at {project_path}. Design doc generated.")
        
        return f"✅ 项目已创建！\n\n**项目路径**: `{project_path}`\n**设计文档**: `{file_name}`\n\n你可以去对应的文件夹下查看详细的需求设计。"
