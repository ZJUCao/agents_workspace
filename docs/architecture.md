# 系统整体架构说明

本项目是一个基于 **Chainlit** 的 AI 全栈开发主控 Agent 系统，旨在通过多 Agent 协同（Architect + Project Manager）将用户的模糊需求转化为结构化的设计方案并自动创建项目原型。

## 1. 核心模块架构

### 1.1 主控层 (Master Control)
- **文件**: [main.py](file:///home/troy/agents_workspace/main.py)
- **功能**: 
  - 作为系统的入口点，集成 Chainlit 提供 Web 交互界面。
  - 调度 `ArchitectBrain` 和 `ProjectManagerBrain`。
  - 处理多模态输入（文本、图片、文档）。

### 1.2 架构师 Agent (Prompt Architect)
- **文件**: [prompt_architect/brain.py](file:///home/troy/agents_workspace/prompt_architect/brain.py)
- **功能**: 
  - **需求解析**: 接收用户原始描述，利用 LLM 生成专业化的 AI Prompt。
  - **话题切换**: 识别用户是否开启了新任务，并自动重置上下文。

### 1.3 项目管理 Agent (Project Manager)
- **文件**: [project_manager/brain.py](file:///home/troy/agents_workspace/project_manager/brain.py)
- **功能**: 
  - **项目初始化**: 根据架构 Prompt 提取项目名称并创建本地目录。
  - **设计文档生成**: 自动生成详细的 `requirement_design.md`，涵盖功能拆解、接口定义和技术选型。

### 1.4 工具与支撑层 (Utils & Infrastructure)
- **文件**: [utils/](file:///home/troy/agents_workspace/utils/)
- **功能**: 
  - **Memory (RAG)**: 使用 ChromaDB 和 Ollama Embeddings 实现跨会话的知识记忆与检索。
  - **Vision/Document**: 提供图片分析和多格式文档（PDF, Docx）读取能力。

## 2. 数据流向

1. **用户输入** -> `main.py` (Chainlit 捕获)
2. **文本/多模态数据** -> `ArchitectBrain` (生成结构化 Prompt)
3. **结构化 Prompt** -> `ProjectManagerBrain` (创建项目目录 & 设计文档)
4. **处理结果** -> `main.py` -> **用户界面** (反馈结果)

## 3. 技术栈
- **Web 框架**: Chainlit
- **大模型框架**: LangChain / LangChain-Ollama
- **本地模型**: Ollama (Qwen2.5, Nomic-Embed-Text)
- **向量数据库**: ChromaDB
- **开发语言**: Python 3.13+
