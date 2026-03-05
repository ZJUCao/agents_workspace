import os
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma  # 更改导入路径
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

class UniversalMemory:
    def __init__(self, namespace="default"):
        model_name = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        self.embeddings = OllamaEmbeddings(model=model_name)
        # 统一存储在根目录下的 chroma_db 文件夹中
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        persist_dir_base = os.getenv("CHROMA_DB_DIR", "chroma_db")
        persist_dir = os.path.join(base_dir, persist_dir_base, namespace)
        
        self.vector_db = Chroma(
            collection_name=f"{namespace}_collection",
            embedding_function=self.embeddings,
            persist_directory=persist_dir
        )

    def save(self, task_id, user_input, agent_output):
        content = f"User: {user_input}\nAgent: {agent_output}"
        doc = Document(page_content=content, metadata={"task_id": task_id})
        self.vector_db.add_documents([doc])

    def search(self, query, task_id, k=3):
        # 这里的 filter 确保了任务间的物理隔离
        return self.vector_db.similarity_search(
            query, k=k, filter={"task_id": task_id}
        )
