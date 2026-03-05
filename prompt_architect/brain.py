import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.memory import UniversalMemory
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv

load_dotenv()

class ArchitectBrain:
    def __init__(self):
        model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:latest")
        self.llm = OllamaLLM(model=model_name)
        self.memory = UniversalMemory(namespace="prompt_architect")
        self.current_task_id = "default_task"

    def check_task_switch(self, input_text):
        """需求6：识别话题切换，返回布尔值"""
        # 利用 LLM 判定或关键词判定
        keywords = ["新任务", "另一个项目", "重新开始", "换个话题"]
        if any(k in input_text for k in keywords):
            self.current_task_id = str(uuid.uuid4())
            return True
        return False

    def process(self, input_text):
        # 1. 检索该任务下的 RAG 记忆
        docs = self.memory.search(input_text, self.current_task_id)
        context = "\n---\n".join([d.page_content for d in docs])

        # 2. 构造 Prompt 生成逻辑
        system_logic = f"""
        你是一位资深的 Prompt Engineer。
        [历史背景]: {context}
        [当前需求]: {input_text}
        
        请根据需求生成最适合的 AI Prompt（如 ChatGPT, Claude 或 Midjourney 风格），
        并给出简要的参数微调建议。
        """
        
        response = self.llm.invoke(system_logic)
        
        # 3. 异步保存记忆
        self.memory.save(self.current_task_id, input_text, response)
        return response
