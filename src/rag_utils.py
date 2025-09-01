import os
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage
from imagine.langchain import ImagineChat, ImagineEmbeddings
from typing import List
from dotenv import load_dotenv
import os
from langchain.schema import Document

load_dotenv()  # This loads variables from .env into environment

api_key = os.getenv("IMAGINE_API_KEY")
endpoint = os.getenv("IMAGINE_API_ENDPOINT")
 
SUPPORTED_EXTS = (".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rb", ".php", ".md", ".json", ".yaml", ".yml")


def create_documents(repo_dir: str) -> List[Document]:
    """Load repository files and split into chunks suited for code (512/50)."""
    docs: List[Document] = []
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.lower().endswith(SUPPORTED_EXTS):
                fpath = os.path.join(root, file)
                try:
                    loader = TextLoader(fpath, encoding="utf-8")
                    file_docs = loader.load()
                    for d in file_docs:
                        # keep relative source for citations
                        d.metadata = {"source": os.path.relpath(fpath, repo_dir)}
                        docs.append(d)
                except Exception:
                    # skip unreadable files
                    continue

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(docs)


def create_vector_store(docs: List[Document], store_path: str) -> Chroma:
    """Create or load a persistent Chroma database with ImagineEmbeddings."""
    embeddings = ImagineEmbeddings()
    os.makedirs(store_path, exist_ok=True)
    # If no index exists yet, create from documents; otherwise load.
    if not any(os.scandir(store_path)):
        Chroma.from_documents(docs, embeddings, persist_directory=store_path)
    return Chroma(persist_directory=store_path, embedding_function=embeddings)


def query_vector_store(db: Chroma, query: str, k: int = 5):
    """Retrieve k relevant chunks for a query."""
    retriever = db.as_retriever(search_kwargs={"k": k})
    return retriever.invoke(query)