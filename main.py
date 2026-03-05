import os
import sys
import chainlit as cl

# 路径挂载，确保能找到各模块
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "prompt_architect"))
sys.path.append(os.path.join(ROOT_DIR, "project_manager"))

from prompt_architect.brain import ArchitectBrain
from project_manager.brain import ProjectManagerBrain
from utils.vision import analyze_image
from utils.document import read_document
from utils.config_loader import config_loader

class MasterBrain:
    def __init__(self):
        self.architect = ArchitectBrain()
        self.pm = ProjectManagerBrain()
        self.prompts = config_loader.get_prompt("master")["master_agent"]

    async def process(self, input_text, image_info="", doc_info=""):
        # 1. 整合最终查询文本
        full_query = f"{input_text}\n{image_info}\n{doc_info}"

        # 2. 话题切换逻辑 (由 Architect 维护)
        if self.architect.check_task_switch(full_query):
            await cl.Message(content=self.prompts["ui_messages"]["detected_switch"]).send()

        # 3. 第一步：生成架构 Prompt
        msg = cl.Message(content=self.prompts["ui_messages"]["step1_start"])
        await msg.send()
        
        architect_prompt = self.architect.process(full_query)
        
        msg.content = f"{self.prompts['ui_messages']['step1_success_prefix']}\n\n---\n{architect_prompt}\n---"
        await msg.update()

        # 4. 第二步：自动移交给 Project Manager 生成项目
        msg_pm = cl.Message(content=self.prompts["ui_messages"]["step2_start"])
        await msg_pm.send()
        
        pm_response = self.pm.process(architect_prompt)
        
        msg_pm.content = pm_response
        await msg_pm.update()
        
        return self.prompts["ui_messages"]["process_complete"]

@cl.on_chat_start
async def start():
    brain = MasterBrain()
    cl.user_session.set("brain", brain)
    welcome_msg = config_loader.get_prompt("master", "master_agent.ui_messages.welcome")
    await cl.Message(content=welcome_msg).send()

@cl.on_message
async def main(message: cl.Message):
    brain = cl.user_session.get("brain")
    
    image_info = ""
    doc_info = ""

    # 处理上传的文件
    if message.elements:
        for file in message.elements:
            if "image" in file.mime:
                image_info += f"\n[视觉分析结果: {analyze_image(file.path)}]"
            elif any(t in file.mime for t in ["pdf", "text", "officedocument"]):
                content = read_document(file.path)
                doc_info += f"\n[参考文档内容: {content}]"

    # 执行主控逻辑
    final_status = await brain.process(message.content, image_info, doc_info)
    
    await cl.Message(content=final_status).send()
