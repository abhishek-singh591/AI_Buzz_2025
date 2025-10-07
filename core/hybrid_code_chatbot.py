import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List
 
from langgraph.graph import StateGraph, END
 
# --- Retriever Node ---
class HybridRetriever:
    def __init__(self, embeddings_dir: str):
        import faiss
        units_path = os.path.join(embeddings_dir, "units.parquet")
        if not os.path.isfile(units_path):
            raise FileNotFoundError(f"units.parquet not found in {embeddings_dir}")
        self.df = pd.read_parquet(units_path).set_index("uid")
        
        # Load file index and IDs
        file_index_path = os.path.join(embeddings_dir, "file_summary.index")
        file_ids_path = os.path.join(embeddings_dir, "file_summary_ids.json")
        self.file_index = faiss.read_index(file_index_path)
        with open(file_ids_path, "r", encoding="utf-8") as f:
            self.file_ids = json.load(f)
        
        # Load symbol index and IDs
        symbol_index_path = os.path.join(embeddings_dir, "symbol_summary.index")
        symbol_ids_path = os.path.join(embeddings_dir, "symbol_summary_ids.json")
        self.symbol_index = faiss.read_index(symbol_index_path)
        with open(symbol_ids_path, "r", encoding="utf-8") as f:
            self.symbol_ids = json.load(f)
        
        # Validate index and ID list sizes match
        file_index_size = self.file_index.ntotal
        symbol_index_size = self.symbol_index.ntotal
        
        if file_index_size != len(self.file_ids):
            print(f"WARNING: File index size ({file_index_size}) != file_ids length ({len(self.file_ids)})")
        
        if symbol_index_size != len(self.symbol_ids):
            print(f"WARNING: Symbol index size ({symbol_index_size}) != symbol_ids length ({len(self.symbol_ids)})")
 
    def embed_query(self, query: str, history: List[Dict[str, str]]) -> np.ndarray:
        # Concatenate history for richer embedding
        history_text = ""
        if history:
            history_text = "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history])
        full_query = f"{history_text}\nCurrent question: {query}" if history_text else query
        from qgenie import QGenieClient
        client = QGenieClient()
        embedding_response = client.embeddings([full_query])
        embedding = embedding_response.data[0].embedding
        return np.asarray(embedding, dtype=np.float32).reshape(1, -1)
 
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state["question"]
        history = state.get("history", [])
        topk_file = state.get("topk_file", 5)
        topk_symbol = state.get("topk_symbol", 5)
        qvec = self.embed_query(query, history)
        Df, If = self.file_index.search(qvec, topk_file)
        Ds, Is = self.symbol_index.search(qvec, topk_symbol)
 
        file_hits = []
        # Only process file results if we have files
        if len(self.file_ids) > 0:
            for score, idx in zip(Df[0].tolist(), If[0].tolist()):
                # Bounds checking to prevent IndexError and skip invalid indices
                if idx >= 0 and idx < len(self.file_ids):
                    uid = self.file_ids[idx]
                    row = self.df.loc[uid]
                    file_hits.append({
                        "uid": uid,
                        "file_path": row["file_path"],
                        "summary": row.get("summary", ""),
                        "code": row.get("code", ""),
                        "score": float(score),
                    })
 
        symbol_hits = []
        # Only process symbol results if we have symbols
        if len(self.symbol_ids) > 0:
            for score, idx in zip(Ds[0].tolist(), Is[0].tolist()):
                # Bounds checking to prevent IndexError and skip invalid indices
                if idx >= 0 and idx < len(self.symbol_ids):
                    uid = self.symbol_ids[idx]
                    row = self.df.loc[uid]
                    symbol_hits.append({
                        "uid": uid,
                        "file_path": row["file_path"],
                        "symbol_type": row.get("symbol_type", ""),
                        "symbol_name": row.get("symbol_name", ""),
                        "signature": row.get("signature", ""),
                        "summary": row.get("summary", ""),
                        "code": row.get("code", ""),
                        "score": float(score),
                    })
 
        # Compose context markdown
        context_md = []
        context_md.append("## Top Files\n")
        for hit in file_hits:
            context_md.append(f"**{hit['file_path']}**\n")
            if hit["summary"]:
                context_md.append(f"- Summary: {hit['summary']}\n")
            context_md.append(f"```python\n{hit['code'][:800]}\n```\n")
        context_md.append("\n## Top Symbols\n")
        for hit in symbol_hits:
            context_md.append(f"**{hit['symbol_type']} {hit['symbol_name']} ({hit['file_path']})**\n")
            if hit["summary"]:
                context_md.append(f"- Summary: {hit['summary']}\n")
            context_md.append(f"```python\n{hit['code'][:800]}\n```\n")
 
        state["retrieved_files"] = file_hits
        state["retrieved_symbols"] = symbol_hits
        state["context"] = "\n".join(context_md)
        return state
 

# --- LLM Node ---
class LLMAnswerer:
    def __init__(self, model_name="Pro"):
        self.model_name = model_name
 
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        from qgenie import QGenieClient, ChatMessage
        client = QGenieClient()
        question = state["question"]
        context = state["context"]
        history = state.get("history", [])
        history_text = ""
        if history:
            history_text = "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history])
        prompt = f"""You are a codebase assistant. Use the following context and chat history to answer the user's question.
 
Chat history:
{history_text}
 
Context:
{context}
 
Current question:
{question}
 
Return a concise, factual answer. If relevant, cite file paths or symbol names from the context."""
        response = client.chat(messages=[ChatMessage(role="user", content=prompt)], model=self.model_name)
        answer = getattr(response, "first_content", None) or str(response)
        state["answer"] = answer
        return state
 
# --- LangGraph Construction ---
def build_hybrid_code_chatbot_graph(embeddings_dir: str, model_name="Pro"):
    graph = StateGraph(dict)
    retriever = HybridRetriever(embeddings_dir)
    llm = LLMAnswerer(model_name)
    graph.add_node("retrieve", retriever)
    graph.add_node("llm", llm)
    graph.add_edge("retrieve", "llm")
    graph.add_edge("llm", END)
    graph.set_entry_point("retrieve")
    return graph.compile()
 
# # --- Multi-turn Example Usage ---
# if __name__ == "__main__":
#     embeddings_dir = ".cache/embeddings/<graph_id>"
#     chatbot_graph = build_hybrid_code_chatbot_graph(embeddings_dir, model_name="Pro")
#     history = []
#     print("Hybrid Code Chatbot (multi-turn). Type your question, or just press Enter to exit.")
#     while True:
#         question = input("User: ").strip()
#         if not question:
#             print("Exiting chat.")
#             break
#         state = {
#             "question": question,
#             "history": history,
#             "topk_file": 5,
#             "topk_symbol": 5,
#         }
#         result = chatbot_graph.invoke(state)
#         answer = result["answer"]
#         print("Bot:", answer)
#         print("\nReferences (files):", [f["file_path"] for f in result["retrieved_files"]])
#         print("References (symbols):", [s["symbol_name"] for s in result["retrieved_symbols"]])
#         # Update history for context retention
#         history.append({"question": question, "answer": answer})
 
