import sys
import os
import re
from langchain_ollama import OllamaLLM
from utils.memory import UniversalMemory
from utils.config_loader import config_loader

class ProjectManagerBrain:
    def __init__(self):
        model_name = config_loader.get_setting("llm.model_name")
        self.llm = OllamaLLM(model=model_name)
        
        pm_settings = config_loader.get_setting("agents.project_manager")
        self.memory = UniversalMemory(namespace=pm_settings["namespace"])
        
        self.prompts = config_loader.get_prompt("pm", "pm_agent")
        projects_root = self.prompts["storage"]["projects_root"]
        self.base_projects_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), projects_root)
        
        if not os.path.exists(self.base_projects_dir):
            os.makedirs(self.base_projects_dir)

    def extract_project_name(self, input_text):
        """
        从输入文本中提取项目名称，如果提取不到则让 LLM 生成一个。
        """
        prompt_tmpl = self.prompts["rules"]["project_name_extraction"]["prompt"]
        prompt = prompt_tmpl.format(input_text=input_text)
        
        name = self.llm.invoke(prompt).strip()
        # 移除非法字符
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        return name if name else self.prompts["rules"]["project_name_extraction"]["default_name"]

    def generate_design_doc(self, input_text):
        """
        利用 LLM 生成详细的需求设计文档。
        """
        prompt_tmpl = self.prompts["rules"]["design_doc_generation"]["prompt"]
        prompt = prompt_tmpl.format(input_text=input_text)
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
        suffix = self.prompts["rules"]["design_doc_generation"]["file_suffix"]
        file_name = f"{project_name}{suffix}"
        file_path = os.path.join(project_path, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(design_doc_content)
            
        # 4. 保存记忆
        self.memory.save(project_name, input_text, f"Project created at {project_path}. Design doc generated.")
        
        return f"✅ 项目已创建！\n\n**项目路径**: `{project_path}`\n**设计文档**: `{file_name}`\n\n你可以去对应的文件夹下查看详细的需求设计。"
