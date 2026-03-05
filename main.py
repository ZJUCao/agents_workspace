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

class MasterBrain:
    def __init__(self):
        self.architect = ArchitectBrain()
        self.pm = ProjectManagerBrain()

    async def process(self, input_text, image_info="", doc_info=""):
        # 1. 整合最终查询文本
        full_query = f"{input_text}\n{image_info}\n{doc_info}"

        # 2. 话题切换逻辑 (由 Architect 维护)
        if self.architect.check_task_switch(full_query):
            await cl.Message(content="✨ 检测到新话题，已为您建立独立的上下文空间。").send()

        # 3. 第一步：生成架构 Prompt
        msg = cl.Message(content="🎨 **Step 1: 正在为您构建需求架构 Prompt...**")
        await msg.send()
        
        architect_prompt = self.architect.process(full_query)
        
        msg.content = f"✅ **架构 Prompt 已生成**\n\n---\n{architect_prompt}\n---"
        await msg.update()

        # 4. 第二步：自动移交给 Project Manager 生成项目
        msg_pm = cl.Message(content="💼 **Step 2: 正在根据架构 Prompt 生成项目与设计文档...**")
        await msg_pm.send()
        
        pm_response = self.pm.process(architect_prompt)
        
        msg_pm.content = pm_response
        await msg_pm.update()
        
        return "🎉 **全流程处理完成！**"

@cl.on_chat_start
async def start():
    brain = MasterBrain()
    cl.user_session.set("brain", brain)
    await cl.Message(content="🤖 **AI 全栈开发主控 Agent 已上线**\n\n我是你的主控大脑，将协同 `Prompt Architect` 和 `Project Manager` 为你服务：\n\n1. **需求架构**：我会先将你的模糊需求转化为结构化的 Prompt。\n2. **项目生成**：接着我会自动为你创建项目目录并生成详细的设计文档。\n\n请直接告诉我你的项目想法，或者上传图片/文档。").send()

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
