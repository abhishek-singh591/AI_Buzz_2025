import os
import streamlit as st
import tempfile
import zipfile
import io
import re
import uuid

# Custom CSS for better scrolling and layout
st.markdown("""
<style>
/* Custom styling for better layout and scrolling */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Sidebar styling */
.sidebar .sidebar-content {
    background-color: #f8f9fa;
}

/* Column styling for better scrolling */
.stColumn > div {
    height: 80vh;
    overflow-y: auto;
    padding-right: 10px;
}

/* Custom scrollbar */
.stColumn > div::-webkit-scrollbar {
    width: 8px;
}

.stColumn > div::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

.stColumn > div::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 4px;
}

.stColumn > div::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}

/* Chat history styling */
.streamlit-expander {
    border: 1px solid #e1e5e9;
    border-radius: 8px;
    margin-bottom: 10px;
}

.streamlit-expander .streamlit-expanderHeader {
    background-color: #f8f9fa;
    border-radius: 8px 8px 0 0;
}

/* Documentation content styling */
h1, h2, h3 {
    color: #2c3e50;
}

/* Mermaid diagram container */
.mermaid {
    margin: 20px 0;
}

/* Page list styling */
.stButton > button {
    margin-bottom: 8px;
    text-align: left;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 14px;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Primary button styling for selected page */
.stButton > button[kind="primary"] {
    background-color: #ff6b6b;
    border-color: #ff6b6b;
}

/* Secondary button styling for unselected pages */
.stButton > button[kind="secondary"] {
    background-color: #f8f9fa;
    border-color: #dee2e6;
    color: #495057;
}

/* Sticky chat input styling - Enhanced for Streamlit */
.sticky-chat-container {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    width: 100% !important;
    background-color: white !important;
    border-top: 2px solid #ff6b6b !important;
    padding: 1rem !important;
    z-index: 999999 !important;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.15) !important;
    backdrop-filter: blur(10px) !important;
    background-color: rgba(255, 255, 255, 0.98) !important;
}

/* Ensure the sticky container is above everything */
.sticky-chat-container * {
    position: relative !important;
}

/* Adjust main content to account for sticky chat */
.main-content-with-sticky-chat {
    padding-bottom: 160px !important;
    margin-bottom: 20px !important;
}

/* Chat input styling */
.sticky-chat-input {
    max-width: 800px !important;
    margin: 0 auto !important;
}

/* Force Streamlit elements to respect sticky positioning */
.sticky-chat-container .stTextInput > div > div > input {
    border: 2px solid #ff6b6b !important;
    border-radius: 8px !important;
    padding: 12px !important;
    font-size: 16px !important;
}

.sticky-chat-container .stButton > button {
    background-color: #ff6b6b !important;
    border-color: #ff6b6b !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    font-weight: bold !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .sticky-chat-container {
        padding: 0.75rem !important;
    }
    .main-content-with-sticky-chat {
        padding-bottom: 140px !important;
    }
}

/* Half-and-half layout adjustments */
.stColumn .sticky-chat-container {
    position: relative;
    bottom: auto;
    left: auto;
    right: auto;
    box-shadow: none;
    border-top: none;
    padding: 0;
}
</style>
""", unsafe_allow_html=True)

from build_wiki import build_sharded_wiki_from_github, get_unique_cache_dir
from build_embeddings import build_embeddings_for_repo
from generate_wiki_pages import generate_wiki_pages
from hybrid_code_chatbot import build_hybrid_code_chatbot_graph

# ========== XML Parsing Helper ==========
def load_wiki_xml(path: str) -> dict:
    import xml.etree.ElementTree as ET
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    start = text.find("<wiki_structure")
    end = text.rfind("</wiki_structure>")
    if start != -1 and end != -1:
        text = text[start:end + len("</wiki_structure>")]
    root = ET.fromstring(text)
    if root.tag != "wiki_structure":
        raise ValueError("Root is not <wiki_structure>")
    sections_el = root.find("sections")
    pages_el = root.find("pages")
    sections = []
    pages_map = {}
    if sections_el is not None:
        for s in sections_el.findall("section"):
            sid = s.get("id") or ""
            title = (s.findtext("title") or "").strip()
            refs = []
            pages_container = s.find("pages")
            if pages_container is not None:
                for pr in pages_container.findall("page_ref"):
                    tid = (pr.text or "").strip()
                    if tid:
                        refs.append(tid)
            subs = []
            subs_el = s.find("subsections")
            if subs_el is not None:
                for sr in subs_el.findall("section_ref"):
                    t = (sr.text or "").strip()
                    if t:
                        subs.append(t)
            sections.append({"id": sid, "title": title, "page_refs": refs, "subsections": subs})
    if pages_el is not None:
        for p in pages_el.findall("page"):
            pid = p.get("id") or ""
            title = (p.findtext("title") or "").strip()
            desc = (p.findtext("description") or "").strip()
            imp = (p.findtext("importance") or "medium").strip().lower()
            rf = []
            rf_el = p.find("relevant_files")
            if rf_el is not None:
                for fp in rf_el.findall("file_path"):
                    t = (fp.text or "").strip()
                    if t:
                        rf.append(t)
            rel = []
            rel_el = p.find("related_pages")
            if rel_el is not None:
                for rp in rel_el.findall("related"):
                    t = (rp.text or "").strip()
                    if t:
                        rel.append(t)
            parent = (p.findtext("parent_section") or "").strip()
            pages_map[pid] = {
                "id": pid, "title": title, "description": desc, "importance": imp,
                "relevant_files": rf, "related_pages": rel, "parent_section": parent
            }
    meta = {
        "title": (root.findtext("title") or "").strip(),
        "description": (root.findtext("description") or "").strip(),
    }
    return {"meta": meta, "sections": sections, "pages": pages_map}

# ========== UI: Sidebar Inputs ==========
st.set_page_config(page_title="Codebase Wiki & Chatbot", layout="wide")
st.title("DocuGenie: Codebase Documentation & Q&A Chatbot")

use_cache = True
with st.sidebar:
    # Only show setup form if no documentation is loaded
    if not st.session_state.get('page_files'):
        st.header("Repository & Generation Settings")
        if st.session_state.get('manual_reset', False):
            st.success("Ready for new documentation setup")
        github_url = st.text_input("GitHub URL", value="https://github.com/pallets/flask")
        github_token = st.text_input("GitHub Token (optional)", type="password")
        language = st.selectbox("Documentation Language", ["English", "Chinese", "Spanish", "French"], index=0)
        model_name = st.selectbox("QGenie Model", ["Pro", "Turbo", ], index=0)
        st.subheader("Performance Options")
        max_files = st.slider("Max Files to Process", min_value=10, max_value=300, value=50, 
                             help="Fewer files = faster processing. More files = more comprehensive docs.")
        regenerate = st.checkbox("Regenerate Documentation (ignore cache)", value=False)
        generate_btn = st.button("Generate Documentation", type="primary", use_container_width=True)
    else:
        generate_btn = False
        github_url = st.session_state.get('github_url', '')
        github_token = ''
        language = 'English'
        model_name = 'Pro'
        max_files = 300
        use_cache = True
        regenerate = False

        # --- Chatbot Button (only if not in chat view) ---
        if not st.session_state.get('show_half_and_half', False):
            if st.button("💬 Open Chatbot", key="open_chatbot_btn", use_container_width=True, type="primary"):
                st.session_state.show_half_and_half = True
                st.rerun()

        if st.button("Generate New Documentation", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.manual_reset = True
            st.rerun()

# ========== Helper Functions ==========

def create_github_url(github_url, file_path, line_number=None):
    if not github_url or not github_url.startswith('https://github.com/'):
        return file_path
    repo_part = github_url.replace('https://github.com/', '').rstrip('/')
    if line_number:
        return f"https://github.com/{repo_part}/blob/HEAD/{file_path}#L{line_number}"
    else:
        return f"https://github.com/{repo_part}/blob/HEAD/{file_path}"

def display_references_with_links(retrieved_files, retrieved_symbols, github_url):
    """
    Display references as clickable GitHub links using actual retrieval results.
    """
    if retrieved_files or retrieved_symbols:
        st.markdown("**📚 References:**")
        # File references
        for file_data in retrieved_files:
            file_path = file_data.get("file_path")
            github_link = create_github_url(github_url, file_path)
            st.markdown(f"- File: [{file_path}]({github_link})")
        # Symbol references
        for symbol_data in retrieved_symbols:
            symbol_name = symbol_data.get("symbol_name", "")
            file_path = symbol_data.get("file_path", "")
            github_link = create_github_url(github_url, file_path)
            st.markdown(f"- Symbol: `{symbol_name}` in [{file_path}]({github_link})")

# ========== Mermaid Diagram Functions ==========
MERMAID_BLOCK_RE = re.compile(r"```mermaid\s+([\s\S]*?)```", re.IGNORECASE)

def extract_mermaid_blocks(markdown_text: str) -> list:
    return [m.group(1).strip() for m in MERMAID_BLOCK_RE.finditer(markdown_text or "")]

def render_mermaid(mermaid_code: str, height: int = 500):
    try:
        import streamlit_mermaid as stmd
        safe = (mermaid_code or "").replace("\\", "\\\\").replace("`", "\\`")
        cid = f"mermaid-{uuid.uuid4().hex}"
        stmd.st_mermaid(safe, key=cid)
    except ImportError:
        st.code(mermaid_code, language="mermaid")
        st.info(" Install `streamlit-mermaid` to render diagrams interactively: `pip install streamlit-mermaid`")
    except Exception as e:
        st.code(mermaid_code, language="mermaid")
        st.warning(f" Could not render Mermaid diagram: {e}")

def render_markdown_with_mermaid(markdown_content: str):
    if not markdown_content:
        return
    # Split content by Mermaid blocks
    parts = MERMAID_BLOCK_RE.split(markdown_content)
    for i, part in enumerate(parts):
        if i % 2 == 0:
            if part.strip():
                st.markdown(part, unsafe_allow_html=True)
        else:
            if part.strip():
                render_mermaid(part.strip())

# ========== Pipeline Execution ==========
def run_pipeline(github_url, github_token, language, model_name, regenerate, max_files=max_files, use_cache=True):
    root_cache_dir = os.path.join("..", ".cache")
    repo_name = get_unique_cache_dir(github_url).split(os.sep)[-1]
    repo_dir = os.path.join(root_cache_dir, repo_name)
    repo_dir = os.path.abspath(repo_dir)
    os.makedirs(repo_dir, exist_ok=True)
    cache_exists = os.path.exists(os.path.join(repo_dir, "wiki_pages"))

    if cache_exists and not regenerate:
        st.success(" Loaded documentation from cache.")
    else:
        if regenerate:
            st.info(" Regenerating documentation (ignoring cache)...")
        else:
            st.info(" Building documentation from scratch...")
        with st.spinner("Building sharded wiki..."):
            build_sharded_wiki_from_github(
                gh_url=github_url,
                token=github_token,
                output_root=repo_dir,
                lang_text=language,
                qgenie_model=model_name,
                max_files=max_files,
            )
        with st.spinner("Building code embeddings..."):
            embeddings_dir = build_embeddings_for_repo(
                github_url=github_url,
                token=github_token,
                output_root=repo_dir,
                MAX_FILES=max_files,
                force_summarize=regenerate,
                model_name=model_name,
            )
        with st.spinner("Generating documentation pages..."):
            generate_wiki_pages(
                output_root=repo_dir,
                lang_text=language,
            )
        st.success(" Documentation generated and cached.")

    wiki_pages_dir = os.path.join(repo_dir, "wiki_pages")
    if os.path.exists(wiki_pages_dir):
        page_files = sorted([f for f in os.listdir(wiki_pages_dir) if f.endswith(".md")])
        page_contents = {}
        for f in page_files:
            with open(os.path.join(wiki_pages_dir, f), "r", encoding="utf-8") as fp:
                page_contents[f] = fp.read()
    else:
        page_files = []
        page_contents = {}

    chatbot_graph = build_hybrid_code_chatbot_graph(os.path.join(repo_dir, "embeddings"), model_name=model_name)
    return page_files, page_contents, chatbot_graph, repo_dir

# ========== Session State ==========
if "page_files" not in st.session_state:
    st.session_state.page_files = []
if "page_contents" not in st.session_state:
    st.session_state.page_contents = {}
if "chatbot_graph" not in st.session_state:
    st.session_state.chatbot_graph = None
if "repo_dir" not in st.session_state:
    st.session_state.repo_dir = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "github_url" not in st.session_state:
    st.session_state.github_url = None
if "show_half_and_half" not in st.session_state:
    st.session_state.show_half_and_half = False

# ========== Run Pipeline ==========
if 'generate_btn' in locals() and generate_btn:
    st.session_state.page_files, st.session_state.page_contents, st.session_state.chatbot_graph, st.session_state.repo_dir = run_pipeline(
        github_url, github_token, language, model_name, regenerate, max_files, use_cache
    )
    st.session_state.github_url = github_url
    st.session_state.chat_history = []
    st.session_state.show_half_and_half = False
    st.session_state.manual_reset = False

# ========== Sidebar Navigation (ORDERED) ==========
def extract_page_title(markdown_content: str, filename: str) -> str:
    if not markdown_content:
        return filename.replace('.md', '').replace('_', ' ').title()
    h1_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()
    h2_match = re.search(r'^##\s+(.+)$', markdown_content, re.MULTILINE)
    if h2_match:
        return h2_match.group(1).strip()
    return filename.replace('.md', '').replace('_', ' ').title()

def get_page_titles(page_files: list, page_contents: dict) -> dict:
    titles = {}
    for filename in page_files:
        content = page_contents.get(filename, '')
        titles[filename] = extract_page_title(content, filename)
    return titles

page_titles = {}

if st.session_state.get('page_files'):
    page_titles = get_page_titles(st.session_state.page_files, st.session_state.page_contents)
    with st.sidebar:
        st.header("Documentation Pages")
        if "selected_page" not in st.session_state:
            st.session_state.selected_page = st.session_state.get('page_files', [None])[0]
        st.markdown("**Select a page:**")
        page_list_container = st.container()
        with page_list_container:
            # --- BEGIN ORDERED PAGE LIST ---
            wiki_xml_path = os.path.join(st.session_state.repo_dir, "wiki_xml", "wiki.xml")
            wiki = load_wiki_xml(wiki_xml_path)

            # Get ordered page IDs from wiki structure
            ordered_page_ids = []
            seen = set()
            for s in wiki.get("sections", []):
                for pid in s.get("page_refs", []):
                    if pid in wiki["pages"] and pid not in seen:
                        ordered_page_ids.append(pid)
                        seen.add(pid)
            for pid in wiki.get("pages", {}).keys():
                if pid not in seen:
                    ordered_page_ids.append(pid)

            # Map page IDs to filenames
            page_id_to_filename = {}
            for fname in st.session_state.page_files:
                match = re.match(r"(page-\d+)\.md", fname)
                if match:
                    page_id_to_filename[match.group(1)] = fname

            # List pages in sidebar in the correct order
            for i, pid in enumerate(ordered_page_ids):
                fname = page_id_to_filename.get(pid)
                if not fname:
                    continue
                title = page_titles[fname]
                if st.button(
                    title, 
                    key=f"page_btn_{i}",
                    use_container_width=True,
                    type="primary" if fname == st.session_state.selected_page else "secondary"
                ):
                    st.session_state.selected_page = fname
                    st.rerun()
            # --- END ORDERED PAGE LIST ---

        selected_page = st.session_state.get('selected_page')
        if st.button(" Download All Documentation", use_container_width=True):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                page_contents = st.session_state.get('page_contents', {})
                for fname, content in page_contents.items():
                    zf.writestr(fname, content)
            st.download_button(
                label="Download ZIP",
                data=buf.getvalue(),
                file_name="documentation.zip",
                mime="application/zip",
                use_container_width=True,
            )

# ========== Main Content Area ==========
if st.session_state.get('page_files'):
    selected_page = st.session_state.get('selected_page')
    page_title = page_titles.get(selected_page, selected_page) if selected_page else "Documentation"

    # HALF-AND-HALF VIEW
    if st.session_state.get('show_half_and_half', False):
        col1, col2 = st.columns([1, 1], gap="large")
        with col1:
            st.header(f" {page_title}")
            doc_container = st.container()
            with doc_container:
                if selected_page and st.session_state.page_contents:
                    render_markdown_with_mermaid(st.session_state.page_contents[selected_page])
                else:
                    st.info("No documentation content available.")

        with col2:
            st.header("Q&A Chatbot")
            chat_input_container = st.container()
            with chat_input_container:
                user_question = st.text_input("Ask your question here:", key="chat_input")
                ask_clicked = st.button("Ask", use_container_width=True)
                if ask_clicked:
                    if user_question.strip():
                        state = {
                            "question": user_question,
                            "history": st.session_state.get('chat_history', []),
                            "topk_file": 5,
                            "topk_symbol": 5,
                        }
                        result = st.session_state.chatbot_graph.invoke(state)
                        answer = result["answer"]
                        # Use actual retrieval results for references
                        retrieved_files = result.get("retrieved_files", [])
                        retrieved_symbols = result.get("retrieved_symbols", [])
                        st.session_state.chat_history.append({
                            "question": user_question,
                            "answer": answer,
                            "retrieved_files": retrieved_files,
                            "retrieved_symbols": retrieved_symbols,
                        })
                        st.rerun()

                # Show the latest answer immediately after Ask button
                if st.session_state.get('chat_history'):
                    latest_entry = st.session_state.chat_history[-1]
                    st.markdown(f"**Question:** {latest_entry['question']}")
                    st.markdown(f"**Answer:** {latest_entry['answer']}")
                    current_github_url = st.session_state.github_url or github_url
                    display_references_with_links(
                        latest_entry["retrieved_files"], 
                        latest_entry["retrieved_symbols"], 
                        current_github_url
                    )
            # --- Close Chat Button ---
            if st.button("❌ Close Chat", key="close_chat_btn", type="secondary"):
                st.session_state.show_half_and_half = False
                st.rerun()
            # Chat history section (optional, below everything)
            if st.session_state.get('chat_history'):
                st.markdown("---")
                st.subheader(" Chat History")
                chat_container = st.container()
                with chat_container:
                    chat_history = st.session_state.get('chat_history', [])
                    for idx, entry in enumerate(chat_history):
                        with st.expander(f"Q{idx+1}: {entry['question'][:50]}..." if len(entry['question']) > 50 else f"Q{idx+1}: {entry['question']}", expanded=False):
                            st.markdown(f"**Question:** {entry['question']}")
                            st.markdown(f"**Answer:** {entry['answer']}")
                            current_github_url = st.session_state.github_url or github_url
                            display_references_with_links(
                                entry["retrieved_files"], 
                                entry["retrieved_symbols"], 
                                current_github_url
                            )

    # FULL-WIDTH DOCUMENTATION VIEW
    else:
        st.markdown("---")
        if selected_page and st.session_state.page_contents:
            render_markdown_with_mermaid(st.session_state.page_contents[selected_page])
        else:
            st.info("No documentation content available.")

else:
    # Show different messages based on whether cache exists
    if 'github_url' in locals() and github_url and github_url.strip():
        root_cache_dir = os.path.join("..", ".cache")
        repo_name = get_unique_cache_dir(github_url).split(os.sep)[-1]
        repo_dir = os.path.join(root_cache_dir, repo_name)
        repo_dir = os.path.abspath(repo_dir)
        wiki_pages_dir = os.path.join(repo_dir, "wiki_pages")
        if os.path.exists(wiki_pages_dir):
            st.info(" Documentation exists in cache. Click **Generate Documentation** to load it, or check the **Regenerate Documentation** box to create fresh documentation.")
        else:
            st.info(" Enter a GitHub URL and click **Generate Documentation** to begin.")
    else:
        st.info(" Enter a GitHub URL and click **Generate Documentation** to begin.")