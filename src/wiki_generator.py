import os
import re
import subprocess
import tempfile
import json
from typing import Dict, Any
from rag_chatbot import create_documents_from_json
import xml.etree.ElementTree as ET
from prompts import build_structure_prompt, build_page_content_prompt
from transformers import pipeline
from lxml import etree
from langchain_chroma import Chroma
from rag_utils import create_documents, create_vector_store, query_vector_store

# ------------------------------
# Git helpers
# ------------------------------
def clone_repo(repo_url: str, dest: str):
    subprocess.run(["git", "clone", "--depth=1", repo_url, dest], check=True)

def get_file_tree(path: str) -> str:
    lines = []
    for root, _, files in os.walk(path):
        if ".git" in root:
            continue
        level = root.replace(path, "").count(os.sep)
        indent = "  " * level
        lines.append(f"{indent}{os.path.basename(root)}/")
        sub = "  " * (level + 1)
        for f in files:
            lines.append(f"{sub}{f}")
    return "\n".join(lines)

def read_readme(path: str) -> str:
    p = os.path.join(path, "README.md")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    return "No README.md found."

# ------------------------------
# LLM helpers (GPT-OSS-20B)
# ------------------------------
model_id = "Qwen/Qwen3-14B"
safe_model = model_id.replace("/", "_")

_llm = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype="auto",
    device_map="cuda:1",
)

def call_llm_structure(prompt: str, chunk_size: int = 4096, max_chunks: int = 5) -> str:
    """
    Generate text in chunks until </wiki_structure> is found or max_chunks is reached.
    """
    full_output = ""
    remaining_prompt = prompt
    chunk_count = 0

    while chunk_count < max_chunks:
        out = _llm(
            remaining_prompt,
            max_new_tokens=chunk_size,
            do_sample=False,
            return_full_text=False,
        )
        chunk = out[0]["generated_text"]
        full_output += chunk
        chunk_count += 1

        if "</wiki_structure>" in full_output:
            break

        # Prepare continuation prompt with context
        continuation_context = full_output[-500:].replace("\n", " ")
        remaining_prompt = f"Continue writing the wiki structure XML based on the previous content:\n{continuation_context}"

    return full_output.strip()

def call_llm(prompt: str) -> str:
    out = _llm(
        prompt,
        max_new_tokens=4096,
        do_sample=True,
        return_full_text=False,
    )
    return out[0]["generated_text"]

# ------------------------------
# XML extraction / parsing
# ------------------------------
_XML_BLOCK = re.compile(
    r"(?:```xml\s*)?<wiki_structure>.*?</wiki_structure>(?:\s*```)?",
    re.DOTALL | re.IGNORECASE,
)

def extract_xml(text: str) -> str:
    if not text:
        raise ValueError("Empty model response.")
    m = _XML_BLOCK.search(text)
    if not m:
        m2 = re.search(r"<wiki_structure>.*?</wiki_structure>", text, re.DOTALL | re.IGNORECASE)
        if not m2:
            raise ValueError(f"No <wiki_structure> block found. Snippet:\n{text[:600]}")
        return m2.group(0).strip()
    return m.group(0).strip()

def clean_malformed_xml(xml_text: str) -> str:
    tag_corrections = {
        "page-ref": "page_ref",
        "file-path": "file_path",
        "related-page": "related",
        "section-ref": "section_ref",
        "data-models": "data_models",
        "javascript-integration": "javascript_integration",
        "session-management": "session_management",
        "customizing-flask": "customizing_flask",
    }
    for wrong_tag, correct_tag in tag_corrections.items():
        xml_text = re.sub(f"<{wrong_tag}>", f"<{correct_tag}>", xml_text)
        xml_text = re.sub(f"</{wrong_tag}>", f"</{correct_tag}>", xml_text)
    return xml_text.replace("&amp;amp;lt;", "<").replace("&amp;amp;gt;", ">")

def safe_parse_xml(xml_text: str):
    parser = etree.XMLParser(recover=True)
    return etree.fromstring(xml_text.encode("utf-8"), parser=parser)

# ------------------------------
# Caching helpers
# ------------------------------
def get_cache_path(repo: str, model_id: str) -> str:
    os.makedirs(".wiki_cache", exist_ok=True)
    safe_model = model_id.replace("/", "_")
    return os.path.join(".wiki_cache", f"{repo}__{safe_model}.json")

def load_from_cache(repo: str, model_id: str) -> Dict[str, Any]:
    path = get_cache_path(repo, model_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_to_cache(repo: str, model_id: str, data: Dict[str, Any]):
    path = get_cache_path(repo, model_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ------------------------------
# Main pipeline
# ------------------------------
def generate_wiki_from_repo(
    repo_url: str,
    language: str = "en",
    model_name: str = "Qwen/Qwen-14B",
    comprehensive: bool = True,
) -> Dict[str, Any]:
    owner, repo = repo_url.rstrip("/").split("/")[-2:]
    cached = load_from_cache(repo, model_id)
    if cached:
        index_dir = os.path.abspath(f"./repo_index_{repo}__{safe_model}_chatbot")
        # if os.listdir(index_dir):
        #     return cached,db
        doc=create_documents_from_json(cached)
        db = create_vector_store(doc, store_path=index_dir)
        return cached,db

    with tempfile.TemporaryDirectory() as temp_dir:
        clone_repo(repo_url, temp_dir)
        file_tree = get_file_tree(temp_dir)
        readme = read_readme(temp_dir)

        structure_prompt = build_structure_prompt(file_tree, readme, owner, repo, language, comprehensive)
        raw = call_llm_structure(structure_prompt)
        print("XML Structure Genretared")
        xml_text = extract_xml(raw)
        xml_text = clean_malformed_xml(xml_text)

        try:
            root_et = ET.fromstring(xml_text)
        except Exception:
            root_lxml = safe_parse_xml(xml_text)
            xml_text = etree.tostring(root_lxml, encoding="unicode")
            root_et = ET.fromstring(xml_text)

        docs = create_documents(temp_dir)
        index_dir = os.path.abspath(f"./repo_index_{repo}__{safe_model}")
        db = create_vector_store(docs, store_path=index_dir)
        pages_md: Dict[str, str] = {}
        count = 0
        for page in root_et.findall(".//page"):
            title = (page.findtext("title") or "").strip() or "Untitled"
            file_paths = [fp.text for fp in page.findall("./relevant_files/file_path")]
            q = f"Wiki Page: {title}. Relevant files: {', '.join(file_paths)}"
            chunks = query_vector_store(db, q, k=5)
            context = "\n\n".join(d.page_content for d in chunks)
            count = count + 1
            content_prompt = build_page_content_prompt(title, file_paths, language, context)
            md = call_llm(content_prompt)
            print(f"Page {count} Content Genretared")
            pages_md[title] = md

        result = {
            "file_tree": file_tree,
            "readme": readme,
            "xml": xml_text,
            "pages": pages_md,
        }
        doc=create_documents_from_json(result)
        index_dir = os.path.abspath(f"./repo_index_{repo}__{safe_model}_chatbot")
        db = create_vector_store(doc, store_path=index_dir)

        save_to_cache(repo, model_id, result)
        return result,db

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo_url", type=str, required=True)
    parser.add_argument("--language", type=str, default="en")
    parser.add_argument("--comprehensive", action="store_true")
    parser.add_argument("--model_name", type=str, default="meta-llama/Llama-3.1-8B-Instruct")
    args = parser.parse_args()

    generate_wiki_from_repo(
        repo_url=args.repo_url,
        language=args.language,
        comprehensive=args.comprehensive,
        model_name=args.model_name
    )