# chatbot_app.py

import os
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

class State(dict):
    pass
# LangGraph state definition
def retrieve(query_func):
    def retrieve_node(state):
        if state is None:
            state={}
        question=state.get("question","")
        if not question:
            return {"context":""}
        doc=query_func(question)
        if not doc:
            return {"context":""}
        if hasattr(doc[0],'page_content'):
            texts=[d.page_content for d in doc]
        else:
            texts=[str(d) for d in doc]
        ctx="\n\n---\n\n".join(texts)
        return {"context": ctx}
    return retrieve_node    

def build_graph(query_func):
    graph = StateGraph(dict)
    graph.add_node("retrieve", retrieve(query_func))
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", END)
    app=graph.compile()
    return app

