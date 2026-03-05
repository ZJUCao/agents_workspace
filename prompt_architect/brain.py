import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.memory import UniversalMemory
from utils.config_loader import config_loader
from langchain_ollama import OllamaLLM

class ArchitectBrain:
    def __init__(self):
        model_name = config_loader.get_setting("llm.model_name")
        self.llm = OllamaLLM(model=model_name)
        
        arch_config = config_loader.get_setting("agents.architect")
        self.memory = UniversalMemory(namespace=arch_config["namespace"])
        self.current_task_id = "default_task"
        self.system_prompt_template = arch_config["system_prompt"]
        
        master_config = config_loader.get_prompt("master", "master_agent")
        self.switch_keywords = master_config["routing_rules"]["task_switch_keywords"]

    def check_task_switch(self, input_text):
        """需求6：识别话题切换，返回布尔值"""
        if any(k in input_text for k in self.switch_keywords):
            self.current_task_id = str(uuid.uuid4())
            return True
        return False

    def process(self, input_text):
        # 1. 检索该任务下的 RAG 记忆
        k = config_loader.get_setting("agents.architect.k_search", 3)
        docs = self.memory.search(input_text, self.current_task_id, k=k)
        context = "\n---\n".join([d.page_content for d in docs])

        # 2. 构造 Prompt 生成逻辑
        system_logic = self.system_prompt_template.format(
            context=context,
            input_text=input_text
        )
        
        response = self.llm.invoke(system_logic)
        
        # 3. 异步保存记忆
        self.memory.save(self.current_task_id, input_text, response)
        return response
