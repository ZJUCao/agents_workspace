# Python 开发环境配置文档

本指南旨在帮助开发者快速搭建并运行 AI 全栈开发主控 Agent 项目。

## 1. 基础环境要求

- **操作系统**: Linux / macOS / Windows (WSL2)
- **Python**: 3.13 或更高版本
- **大模型支持**: Ollama (本地部署)

## 2. 部署步骤

### 2.1 克隆并进入项目目录
```bash
git clone <repository_url>
cd agents_workspace
```

### 2.2 创建并激活虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# Windows 使用: venv\Scripts\activate
```

### 2.3 安装依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4 配置本地模型 (Ollama)
本项目默认使用以下模型：
- **文本模型**: `qwen2.5:latest`
- **向量嵌入模型**: `nomic-embed-text:latest`
- **视觉模型 (可选)**: `llava:latest`

在终端运行以下命令下载模型：
```bash
ollama pull qwen2.5
ollama pull nomic-embed-text
ollama pull llava
```

### 2.5 环境变量配置
创建 `.env` 文件并配置以下参数：
```env
OLLAMA_MODEL=qwen2.5:latest
OLLAMA_EMBED_MODEL=nomic-embed-text
CHROMA_DB_DIR=chroma_db
PROJECTS_ROOT=projects
```

## 3. 运行项目

使用 Chainlit 启动 Web 应用：
```bash
chainlit run main.py --port 8000
```
访问 `http://localhost:8000` 即可开始交互。

## 4. 常见问题 (FAQ)

- **Ollama 连接失败**: 请确保 Ollama 服务已启动 (在后台运行或执行 `ollama serve`)。
- **ChromaDB 报错**: 如果数据库文件损坏，可以尝试删除 `chroma_db/` 文件夹并重新运行。
- **依赖冲突**: 建议在全新的 `venv` 虚拟环境中安装依赖。
