import chainlit as cl
import os
import sys

# 路径挂载
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain import ProjectManagerBrain

@cl.on_chat_start
async def start():
    # 每个用户会话拥有独立的大脑实例
    brain = ProjectManagerBrain()
    cl.user_session.set("brain", brain)
    await cl.Message(content="💼 **Project Manager Agent 已上线**\n\n请将 `prompt_architect` 生成的需求 prompt 转发给我，我将为你：\n1. 在 `projects` 文件夹下创建独立的项目目录。\n2. 生成一份详尽的 `.md` 需求设计文档（包含接口定义和功能描述）。\n3. 将需求拆解到最细粒度。").send()

@cl.on_message
async def main(message: cl.Message):
    brain = cl.user_session.get("brain")
    
    # 1. 提取消息内容
    input_text = message.content

    # 2. 生成响应并流式显示
    msg = cl.Message(content="正在架构项目并生成设计文档...")
    await msg.send()
    
    # 3. 处理需求并生成项目
    response = brain.process(input_text)
    
    msg.content = response
    await msg.update()
