import json
from typing import List
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rag_utils import create_vector_store,query_vector_store



def create_documents_from_json(data: json) -> List[Document]:
    """Load JSON file and split into chunks suited for RAG (512/50)."""
    docs: List[Document] = []

    # with open(json_path, "r", encoding="utf-8") as f:
    #     data = json.load(f)
    for key in ["file_tree", "xml", "readme"]:
        if key in data and isinstance(data[key], str):
            docs.append(Document(page_content=data[key], metadata={"source": key}))

    # Flatten nested 'pages' dictionary
    if "pages" in data and isinstance(data["pages"], dict):
        for page_key, page_text in data["pages"].items():
            if isinstance(page_text, str):
                docs.append(Document(page_content=page_text, metadata={"source": f"pages/{page_key}"}))

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(docs)

