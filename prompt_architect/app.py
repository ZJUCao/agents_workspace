import chainlit as cl
import os
import sys

# 路径挂载
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain import ArchitectBrain
from utils.vision import analyze_image
from utils.document import read_document

@cl.on_chat_start
async def start():
    # 每个用户会话拥有独立的大脑实例
    brain = ArchitectBrain()
    cl.user_session.set("brain", brain)
    await cl.Message(content="🚀 **Prompt Architect (纯净版) 已上线**\n\n你可以通过以下方式下达指令：\n1. **直接打字** 描述需求。\n2. **拖入图片** (使用 Llava 识别)。\n3. **上传文档** (支持 PDF/Word/TXT)。").send()

@cl.on_message
async def main(message: cl.Message):
    brain = cl.user_session.get("brain")
    
    image_info = ""
    doc_info = ""

    # 1. 处理上传的非语音附件
    if message.elements:
        for file in message.elements:
            # 处理图片
            if "image" in file.mime:
                image_info += f"\n[视觉分析结果: {analyze_image(file.path)}]"
            # 处理文档
            elif any(t in file.mime for t in ["pdf", "text", "officedocument"]):
                content = read_document(file.path)
                doc_info += f"\n[参考文档内容: {content}]"

    # 2. 整合最终查询文本
    full_query = f"{message.content}\n{image_info}\n{doc_info}"

    # 3. 话题切换逻辑
    if brain.check_task_switch(full_query):
        await cl.Message(content="✨ 检测到新话题，已为您建立独立的上下文空间。").send()

    # 4. 生成响应并流式显示
    msg = cl.Message(content="正在架构 Prompt...")
    await msg.send()
    
    response = brain.process(full_query)
    
    msg.content = response
    await msg.update()
