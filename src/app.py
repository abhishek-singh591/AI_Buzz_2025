# app.py
import streamlit as st
import streamlit.components.v1 as components
import streamlit_mermaid as stmd
import sys
import argparse
import re
from functools import partial
from imagine.langchain import ImagineChat
from langchain_core.messages import HumanMessage, AIMessage

from utils import split_markdown_into_segments, fix_escaped_html_tags
from wiki_generator import generate_wiki_from_repo
from chat_bot import build_graph
from rag_utils import query_vector_store

# Streamlit config
st.set_page_config(page_title="Repo → AI Wiki (RAG)", layout="wide")
st.title("📘 GitHub Repo → AI Wiki (RAG-grounded)")

# Parse CLI arguments from run.sh
parser = argparse.ArgumentParser()
parser.add_argument("--repo_url", type=str, default="https://github.com/pallets/flask")
parser.add_argument("--model_name", type=str, default="default-model")
args, _ = parser.parse_known_args()

# Session state initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "wiki_generated" not in st.session_state:
    st.session_state.wiki_generated = False

chat_model = ImagineChat()

def render_tree_diagram(tree_text: str):
    """Render ASCII-like tree as nested <ul> HTML with white text."""
    lines = tree_text.splitlines()
    html = "<ul style='font-family:monospace; color:white;'>"
    prev_indent = 0
    for line in lines:
        stripped = line.strip()
        indent = (len(line) - len(stripped)) // 2
        html += "<ul>" * max(indent - prev_indent, 0)
        html += "</ul>" * max(prev_indent - indent, 0)
        html += f"<li>{stripped}</li>"
        prev_indent = indent
    html += "</ul>" * (prev_indent + 1)
    components.html(f"<div style='white-space:pre;'>{html}</div>", height=600, scrolling=True)

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    repo_url = st.text_input("GitHub Repository URL", value=args.repo_url)
    language = st.selectbox("Wiki language", ["en", "ja", "zh", "zh-tw", "es", "kr", "vi", "pt-br", "fr", "ru"], index=0)
    comprehensive = st.checkbox("Comprehensive structure", value=True)
    run_btn = st.button("Generate Wiki")

# Wiki generation
if run_btn:
    with st.spinner("Cloning, indexing, generating wiki..."):
        result, db = generate_wiki_from_repo(repo_url, language=language, comprehensive=comprehensive, model_name=args.model_name)
    retrieve_func = partial(query_vector_store, db)
    app = build_graph(retrieve_func)
    st.session_state.result = result
    st.session_state.app = app
    st.session_state.wiki_generated = True

    st.subheader("📂 Repository File Tree")
    render_tree_diagram(result["file_tree"])

    st.subheader("📄 README Preview")
    st.code(result["readme"][:4000] + ("\n…" if len(result["readme"]) > 4000 else ""), language="markdown")

    st.subheader("📑 Generated Wiki Pages (Markdown)")
    for title, md in result["pages"].items():
        with st.expander(title, expanded=False):
            for block in split_markdown_into_segments(md):
                content = block.get("content", "")
                if block.get("type") == "text":
                    st.markdown(content)
                elif block.get("type") == "mermaid":
                    components.html(f'''
                        <html>
                        <head>
                            <script type="module">
                                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                                mermaid.initialize({{ startOnLoad: true }});
                            </script>
                        </head>
                        <body>
                            <div class="mermaid">{fix_escaped_html_tags(content)}</div>
                        </body>
                        </html>
                    ''', height=500)
                else:
                    st.error(f"Unknown block type: {block.get('type')}")
            st.download_button(
                label="⬇️ Download Markdown",
                data=md.encode("utf-8"),
                file_name=f"{title.lower().replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True,
            )

# Chat interface
if st.session_state.wiki_generated:
    user_input = st.chat_input("Ask a question about your codebase...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        state = st.session_state.app.invoke({"question": user_input})
        context = state.get("context", "")
        message_history = [
            HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"])
            for msg in st.session_state.chat_history
        ]
        message_history.append(AIMessage(content=context))
        reply_text = chat_model.generate([message_history]).generations[0][0].text
        st.session_state.chat_history.append({"role": "assistant", "content": reply_text})

        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("🤖 Chatbot")
            for msg in st.session_state.chat_history:
                st.chat_message(msg["role"]).write(msg["content"])
        with col2:
            st.subheader("📂 Repository File Tree")
            render_tree_diagram(st.session_state.result["file_tree"])
            st.subheader("📄 README Preview")
            st.code(st.session_state.result["readme"][:4000] + ("\n…" if len(st.session_state.result["readme"]) > 4000 else ""), language="markdown")
            st.subheader("📑 Generated Wiki Pages (Markdown)")
            for title, md in st.session_state.result["pages"].items():
                with st.expander(title, expanded=False):
                    st.markdown(md)
                    st.download_button(
                        label="⬇️ Download Markdown",
                        data=md.encode("utf-8"),
                        file_name=f"{title.lower().replace(' ', '_')}.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )

if not st.session_state.wiki_generated:
    st.info("Enter a repo URL and click **Generate Wiki** to begin.")

# Utility to clean LLM output
def clean_llm_output(text: str) -> str:
    text = re.sub(r"^```.*?```$", "", text, flags=re.DOTALL | re.MULTILINE).strip()
    for end in [
        "let me know if you need more help",
        "please let me know if you need any further assistance",
        "i hope this helps",
        "feel free to ask",
    ]:
        text = re.sub(end + ".*", "", text, flags=re.IGNORECASE | re.DOTALL).strip()
    return text