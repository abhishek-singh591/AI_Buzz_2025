# generate_wiki_pages.py

import os
import re
import json
import gzip
import uuid
import zipfile
import hashlib
import traceback
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import pandas as pd
import pickle

import utils  

# ========================= XML Parsing =========================
def load_wiki_xml(path: str) -> Dict[str, Any]:
    import xml.etree.ElementTree as ET
    text = utils.read_text(path).strip()
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

# ========================= Embeddings IO =========================
def load_embeddings_bundle(emb_dir: str) -> Dict[str, Any]:
    units_path = os.path.join(emb_dir, "units.parquet")
    units_alt = os.path.join(emb_dir, "units.parquet.jsonl.gz")
    if os.path.isfile(units_path):
        df = pd.read_parquet(units_path)
    elif os.path.isfile(units_alt):
        rows = []
        with gzip.open(units_alt, "rt", encoding="utf-8") as f:
            for line in f:
                rows.append(json.loads(line))
        df = pd.DataFrame.from_records(rows)
    else:
        raise FileNotFoundError("units.parquet not found in embeddings dir")

    import faiss
    code_index = faiss.read_index(os.path.join(emb_dir, "code.index"))
    summary_index = faiss.read_index(os.path.join(emb_dir, "summary.index"))
    code_ids = json.loads(utils.read_text(os.path.join(emb_dir, "code_ids.json")))
    summary_ids = json.loads(utils.read_text(os.path.join(emb_dir, "summary_ids.json")))
    return {"df": df, "code_index": code_index, "summary_index": summary_index,
            "code_ids": code_ids, "summary_ids": summary_ids}

def embed_query(texts: List[str]) -> np.ndarray:
    from qgenie import QGenieClient
    client = QGenieClient()
    embedding_response = client.embeddings(texts)
    embeddings = [item.embedding for item in embedding_response.data]
    return np.asarray(embeddings, dtype=np.float32)

def section_normalize(title: str) -> str:
    t = (title or "").strip().lower()
    t = re.sub(r"[\s_-]+", " ", t)
    t = t.replace("&amp;", "and")
    return t


# ========================= Hybrid Query =========================
SECTION_HINTS = {
    "system architecture": ["architecture", "design", "diagram", "docs/architecture", "docs/design", ".github/workflows", "dockerfile", "docker-compose", "helm", "k8s", "terraform", "ansible"],
    "core features": ["core/", "models/", "transformers/", "qefficient/", "pipeline", "api", "feature"],
    "data management/flow": ["data/", "dataset", "db/", ".sql", "migrations", "etl", "pipeline"],
    "backend systems": ["api/", "/controllers/", "/services/", "/routes/", "server", "backend"],
    "model integration": ["modeling_", "inference", "training", "weights", "checkpoint", "load_model"],
    "deployment/infrastructure": ["dockerfile", "docker-compose", "helm", "k8s", "terraform", "ansible", ".github/workflows", "jenkinsfile", "cloudbuild"],
    "examples and notebooks": ["examples/", ".ipynb", "notebooks/"],
    "overview": ["readme", "docs/index", "docs/readme"],
    "extensibility and customization": ["plugin", "extension", "hooks", "interface", "adapter"],
}

def find_lexical_candidates(df: pd.DataFrame, keywords: List[str], max_files: int = 8, max_symbols: int = 12) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if not keywords:
        return df.head(0).copy(), df.head(0).copy()
    kw = [k.lower() for k in keywords if k]
    mask_files = (df["level"] == "file")
    mask_syms = (df["level"] == "symbol")

    def any_kw_in_path(p: str) -> bool:
        pl = (p or "").lower()
        return any(k in pl for k in kw)

    def any_kw_in_sym(r) -> bool:
        cand = [(r.get("file_path") or ""), (r.get("symbol_name") or ""), (r.get("signature") or "")]
        cand = " ".join([c.lower() for c in cand])
        return any(k in cand for k in kw)

    f_hits = df[mask_files].copy()
    f_hits = f_hits[f_hits["file_path"].apply(any_kw_in_path)]
    s_hits = df[mask_syms].copy()
    s_hits = s_hits[s_hits.apply(any_kw_in_sym, axis=1)]

    if len(f_hits):
        f_hits = f_hits.assign(_len=f_hits["file_path"].str.len(),
                               _has_sum=f_hits["summary"].fillna("").str.len() > 0)
        f_hits = f_hits.sort_values(by=["_has_sum", "_len"], ascending=[False, True]).drop(columns=["_len","_has_sum"]).head(max_files)
    if len(s_hits):
        s_hits = s_hits.assign(_has_sum=s_hits["summary"].fillna("").str.len() > 0)
        s_hits = s_hits.sort_values(by=["_has_sum"], ascending=[False]).drop(columns=["_has_sum"]).head(max_symbols)
    return f_hits, s_hits

def search_hybrid_plus(query: str, section_title: str, emb: Dict[str, Any], topk_file: int, topk_symbol: int, extra_file: int = 6, extra_symbol: int = 10) -> Tuple[pd.DataFrame, pd.DataFrame]:
    import faiss
    # Vector search (summary embeddings for semantic, code for code context)
    qvec = embed_query([query])[0].reshape(1, -1)
    Ds, Is = emb["summary_index"].search(qvec, topk_symbol)
    Df, If = emb["code_index"].search(qvec, topk_file)
    sids = [emb["summary_ids"][i] for i in Is[0]]
    fids = [emb["code_ids"][i] for i in If[0]]
    df = emb["df"].set_index("uid")
    sym_hits = df.loc[sids].reset_index().assign(score=Ds[0])
    file_hits = df.loc[fids].reset_index().assign(score=Df[0])

    # Lexical boosters by section
    hints = SECTION_HINTS.get(section_normalize(section_title), [])
    f_boost, s_boost = find_lexical_candidates(df.reset_index(), hints, max_files=extra_file, max_symbols=extra_symbol)

    def combine(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
        if len(b) == 0: return a
        both = pd.concat([a, b], ignore_index=True)
        both = both.drop_duplicates(subset=["uid"], keep="first")
        return both

    file_hits = combine(file_hits, f_boost)
    sym_hits = combine(sym_hits, s_boost)

    return file_hits, sym_hits

# ========================= Prompt Builders =========================
SECTION_TO_MERMAID = {
    "system architecture": ["flowchart", "graph TD", "graph LR"],
    "backend systems": ["sequenceDiagram", "flowchart"],
    "model integration": ["sequenceDiagram", "classDiagram"],
    "data management/flow": ["erDiagram", "flowchart"],
    "deployment/infrastructure": ["flowchart", "graph LR", "graph TD"],
    "examples and notebooks": ["flowchart"],
    "overview": ["flowchart"],
    "extensibility and customization": ["classDiagram", "flowchart"],
}

ALLOWED_SECTIONS = [
    "overview", "system architecture", "core features", "data management/flow",
    "backend systems", "model integration", "deployment/infrastructure",
    "examples and notebooks", "extensibility and customization",
]

FORBIDDEN_SECTIONS = [
    "text examples", "c++ examples", "python examples", "random scripts", "misc", "playground"
]

def build_context_pack(file_hits: pd.DataFrame, sym_hits: pd.DataFrame, max_units: int = 16, max_code_chars: int = 1200) -> str:
    rows = []
    for _, r in sym_hits.head(max_units).iterrows():
        rows.append({
            "kind": f"symbol::{r.get('symbol_type') or ''}",
            "path": r.get("file_path"),
            "name": r.get("symbol_name") or r.get("signature") or "",
            "summary": (r.get("summary") or "")[:800],
            "docstring": (r.get("docstring") or "")[:800],
            "code": (r.get("code") or "")[:max_code_chars]
        })
    remain = max(0, max_units - len(rows))
    if remain > 0:
        for _, r in file_hits.head(remain).iterrows():
            rows.append({
                "kind": "file",
                "path": r.get("file_path"),
                "name": "",
                "summary": (r.get("summary") or "")[:800],
                "docstring": "",
                "code": (r.get("code") or "")[:max_code_chars]
            })
    return json.dumps(rows, ensure_ascii=False, indent=2)

def build_page_prompt(
    repo_id: str,
    section_title: str,
    page_spec: Dict[str, Any],
    file_hits: pd.DataFrame,
    sym_hits: pd.DataFrame,
    lang_text: str,
    readme_ok: bool,
    min_files_per_page: int = 2,
    max_files_per_page: int = 5,
    max_units: int = 16,
    max_code_chars: int = 1200
) -> Tuple[str, str]:
    sec_norm = section_normalize(section_title)
    mermaid_pref = SECTION_TO_MERMAID.get(sec_norm, ["flowchart"])
    context_block = build_context_pack(file_hits, sym_hits, max_units=max_units, max_code_chars=max_code_chars)

    xml_files_hint = page_spec.get("relevant_files") or []
    xml_files_hint_text = json.dumps(xml_files_hint, ensure_ascii=False, indent=2) if xml_files_hint else "[]"

    avoid_readme = "EXCEPT in 'Overview' or 'Examples and Notebooks'." if not readme_ok else "Allowed for this page."

   
    draft = f"""You are a senior technical writer and software architect documenting the repository '{repo_id}'.

PAGE SPEC:

Section: {section_title}
Page ID: {page_spec.get('id')}
Title: {page_spec.get('title')}
Description: {page_spec.get('description')}
Importance: {page_spec.get('importance')}

ALLOWED vs FORBIDDEN SECTION TITLES (context; do not create new sections):

Allowed: {ALLOWED_SECTIONS}
Forbidden: {FORBIDDEN_SECTIONS}

FILE GROUNDEDNESS (HARD RULES):

Use ONLY file paths from the context units below; do NOT invent paths.
Include {min_files_per_page}–{max_files_per_page} exact file paths (verbatim) in a "References" section.
README-like files (README, README.md/.rst/.txt) are {avoid_readme}
Prefer code/config files that truly support the page topic.

MERMAID DIAGRAMS:

Include at least one Mermaid diagram suitable for this section.
Recommended types for '{section_title}': {mermaid_pref}
Valid: sequenceDiagram, classDiagram, stateDiagram-v2, flowchart, erDiagram, graph LR, graph TD.
Use fenced code blocks.
Add a short caption below each diagram.

## CRITICAL: Depth and Richness Requirements
- Write a comprehensive, detailed, and in-depth documentation page.
- Cover not just what the code does, but also why, how, and in what context it is used.
- Include explanations of architecture, design decisions, workflows, and interactions.
- Provide usage examples, edge cases, and best practices.
- Add diagrams, tables, and lists where helpful.
- For each referenced file or symbol, explain its role and how it fits into the bigger picture.
- Do NOT summarize briefly; aim for a thorough, multi-section document that could serve as a standalone reference for a new engineer.
- The documentation should be at least 800 words unless the topic is extremely narrow.

OUTPUT FORMAT (STRICT):

Return ONLY Markdown. No front-matter, no commentary.
Suggested headings:
# {page_spec.get('title')}
## Overview
## Key Components / Concepts
## How it Works
## Example(s)
## Diagram(s)
## References (with exact file paths)

Be thorough, detailed, and educational. Avoid generic filler. Make this page as useful as possible for onboarding and deep understanding.

CONTEXT UNITS (use these only; do not invent file paths): {context_block}

XML 'relevant_files' hints (optional): {xml_files_hint_text}
"""

    refine = f"""You are a meticulous documentation editor.
Refine the Markdown for page '{page_spec.get('title')}' under '{section_title}' for repo '{repo_id}'.

CHECKLIST (MUST):

Content is grounded in file paths from the provided context.
"References" contains {min_files_per_page}–{max_files_per_page} exact file paths used in the write-up.
Mermaid diagram(s) exist and use suitable type(s) for this section (e.g., {mermaid_pref}); fix syntax if needed.
Headings present: # Title, ## Overview, ## Key Components / Concepts, ## How it Works, ## Example(s), ## Diagram(s), ## References.
No generic filler; precise explanations aligned with the code/summaries.
Language: {lang_text}. No extra commentary.

## CRITICAL: Depth and Richness Requirements
- Ensure the documentation is comprehensive, detailed, and in-depth.
- Add further explanations, examples, and clarifications where needed.
- Expand on any brief sections.
- The documentation should be at least 800 words unless the topic is extremely narrow.

Return ONLY the final Markdown (no extra text). ORIGINAL DRAFT:
"""
    return draft, refine
# ========================= QGenie =========================
def qgenie_chat(prompt: str, system: Optional[str] = None) -> str:
    from qgenie import QGenieClient, ChatMessage
    client = QGenieClient()
    messages = []
    if system:
        messages.append(ChatMessage(role="system", content=system))
    messages.append(ChatMessage(role="user", content=prompt))
    response = client.chat(messages=messages, model="Pro")
    return (getattr(response, "first_content", None) or str(response) or "").strip()

# ========================= Post-processing Helpers =========================
def extract_mermaid_blocks(markdown_text: str) -> List[str]:
    MERMAID_BLOCK_RE = re.compile(r"mermaid\s+([\s\S]*?)", re.IGNORECASE)
    return [m.group(1).strip() for m in MERMAID_BLOCK_RE.finditer(markdown_text or "")]

def insert_mermaid_fallback(md: str, diagram_code: str) -> str:
    block = f"\nmermaid\n{diagram_code.strip()}\n\n\nDiagram: auto-generated fallback.\n"
    if "## Diagram(s)" in md:
        return md.replace("## Diagram(s)", "## Diagram(s)\n" + block, 1)
    return md + "\n\n## Diagram(s)\n" + block

def linkify_references(md: str, owner: str, repo: str, branch: str, subpath: str = "") -> str:
    if not (owner and repo and branch) or not md: return md
    base = f"https://github.com/{owner}/{repo}/blob/{branch}/"
    if subpath: sp = subpath.strip("/").rstrip("/")
    if sp: base += sp + "/"
    lines = md.splitlines()
    out = []
    in_refs = False
    for i, line in enumerate(lines):
        hdr = line.strip().lower()
        if hdr.startswith("## references"):
            in_refs = True
            out.append(line)
            continue
        if in_refs:
            if hdr.startswith("## ") and i != 0:
                in_refs = False
                out.append(line)
                continue
            replaced = line
            m_code = re.findall(r"`([^`]+)`", line)
            if m_code:
                for p in m_code:
                    p_clean = p.strip()
                    if not p_clean:
                        continue
                    url = base + p_clean.lstrip("/")
                    replaced = replaced.replace(f"`{p}`", f"[`{p}`]({url})")
                out.append(replaced)
                continue
            m = re.match(r"^\s*([-*]|\d+\.)\s+(.+)$", line)
            if m:
                p = m.group(2).strip()
                if ("/" in p) or ("." in os.path.basename(p)):
                    url = base + p.lstrip("/")
                    replaced = line.replace(p, f"[`{p}`]({url})")
            out.append(replaced)
        else:
            out.append(line)
    return "\n".join(out)

# ========================= Main Generation Function =========================
def generate_wiki_pages(
    output_root: str,
    lang_text: str = "English",
    page_ids: Optional[List[str]] = None,
    retrieval_knobs: Optional[Dict[str, Any]] = None,
    gen_knobs: Optional[Dict[str, Any]] = None,
    diagram_fallback: bool = True,
    use_cache: bool = True,
    clear_cache: bool = False
) -> Dict[str, Dict[str, Any]]:
    """
    Generates Markdown documentation pages for each wiki page using hybrid code+summary embeddings and QGenie.
    Returns: dict of page_id -> {markdown_path, markdown_content, hybrid_results}
    """
    # Load wiki XML
    wiki_xml_path = os.path.join(output_root, "wiki_xml", "wiki.xml")
    wiki = load_wiki_xml(wiki_xml_path)

    # Load embeddings
    emb_dir = os.path.join(output_root, "embeddings")
    emb = load_embeddings_bundle(emb_dir)

    # Get repo info for linkification
    owner, repo, branch, subpath = utils.parse_repo_from_wiki_path(wiki_xml_path)
    repo_title = wiki["meta"].get("title") or f"{owner}/{repo}" or "Repository"

    # Section id -> title
    sections_by_id = {s["id"]: s["title"] for s in wiki.get("sections", [])}

    # Stable page order
    pages_order = []
    seen = set()
    for s in wiki.get("sections", []):
        for pid in s.get("page_refs", []):
            if pid in wiki["pages"] and pid not in seen:
                pages_order.append(pid); seen.add(pid)
    for pid in wiki.get("pages", {}).keys():
        if pid not in seen:
            pages_order.append(pid)

    if page_ids is None:
        page_ids = pages_order

    # Default knobs
    retrieval_knobs = retrieval_knobs or {
        "topk_symbol": 12,
        "topk_file": 8,
        "max_units": 16,
        "max_code_chars": 1200,
    }
    gen_knobs = gen_knobs or {
        "min_refs": 2,
        "max_refs": 5,
        "include_overview_readme": True,
    }

    # Output directories
    pages_dir = utils.ensure_dir(os.path.join(output_root, "wiki_pages"))
    cache_dir = utils.ensure_dir(os.path.join(pages_dir, ".cache"))

    def build_cache_key(page_spec, sec_title, retrieval_knobs, gen_knobs, ctx_unit_ids, version="v2"):
        payload = {
            "v": version,
            "page": {k: page_spec.get(k) for k in ["id","title","description","importance","parent_section"]},
            "section": sec_title,
            "retrieval": retrieval_knobs,
            "generation": gen_knobs,
            "ctx_ids": ctx_unit_ids[:64],
        }
        blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha1(blob).hexdigest()[:16]

    def page_cache_paths(cache_dir, page_id, key):
        return os.path.join(cache_dir, f"{page_id}__{key}draft.md"), os.path.join(cache_dir, f"{page_id}__{key}final.md")

    def context_ids_from_hits(file_hits, sym_hits, max_units):
        ids = []
        if len(sym_hits):
            ids.extend(sym_hits["uid"].tolist()[:max_units])
        if len(file_hits):
            remain = max(0, max_units - len(ids))
            ids.extend(file_hits["uid"].tolist()[:remain])
        return ids

    results = {}

    for pid in page_ids:
        p = wiki["pages"][pid]
        sec_title = sections_by_id.get(p.get("parent_section", ""), "(Unknown Section)")
        sec_norm = section_normalize(sec_title)
        key_terms = SECTION_HINTS.get(sec_norm, [])
        query = f"{p.get('title')} — {sec_title}. {p.get('description')}. " + " ".join(key_terms[:8])

        file_hits, sym_hits = search_hybrid_plus(
            query=query,
            section_title=sec_title,
            emb=emb,
            topk_file=int(retrieval_knobs["topk_file"]),
            topk_symbol=int(retrieval_knobs["topk_symbol"]),
            extra_file=6, extra_symbol=10
        )

        readme_ok = gen_knobs["include_overview_readme"] and (sec_norm in ("overview", "examples and notebooks"))
        draft_prompt, refine_prompt = build_page_prompt(
            repo_id=repo_title,
            section_title=sec_title,
            page_spec=p,
            file_hits=file_hits,
            sym_hits=sym_hits,
            lang_text=lang_text,
            readme_ok=readme_ok,
            min_files_per_page=int(gen_knobs["min_refs"]),
            max_files_per_page=int(gen_knobs["max_refs"]),
            max_units=int(retrieval_knobs["max_units"]),
            max_code_chars=int(retrieval_knobs["max_code_chars"]),
        )

        ctx_ids = context_ids_from_hits(file_hits, sym_hits, int(retrieval_knobs["max_units"]))
        cache_key = build_cache_key(
            page_spec=p,
            sec_title=sec_title,
            retrieval_knobs=retrieval_knobs,
            gen_knobs=gen_knobs,
            ctx_unit_ids=ctx_ids,
            version="v2"
        )
        draft_cache_path, final_cache_path = page_cache_paths(cache_dir, pid, cache_key)

        final_md = None
        if use_cache and (not clear_cache) and os.path.isfile(final_cache_path):
            final_md = utils.read_text(final_cache_path)

        if final_md is None:
            system_msg = ("Follow the user's instructions EXACTLY. Output ONLY Markdown; "
                          "include required Mermaid diagrams; obey file selection constraints; "
                          "no extra commentary.")
            draft_md = qgenie_chat(draft_prompt, system=system_msg)
            utils.write_text(draft_cache_path, draft_md)

            final_md = qgenie_chat(refine_prompt + "\n\n" + draft_md, system=system_msg)
            if diagram_fallback:
                diags = extract_mermaid_blocks(final_md)
                if not diags:
                    fallback = f"""Generate only a Mermaid diagram for the page '{p.get('title')}' ({sec_title}).
Use 'sequenceDiagram' unless a class or flowchart is clearly better; return a single Mermaid fenced block and nothing else.

Context units (for accurate names & calls): {build_context_pack(file_hits, sym_hits, max_units=int(retrieval_knobs["max_units"]), max_code_chars=600)} """
                    fb_md = qgenie_chat(fallback, system="Return ONLY a mermaid fenced block.")
                    m = re.search(r"mermaid\s+([\s\S]*?)", fb_md, re.IGNORECASE)
                    code = m.group(1).strip() if m else fb_md.strip().strip("`")
                    if code:
                        final_md = insert_mermaid_fallback(final_md, code)
            final_md = linkify_references(final_md, owner, repo, branch, subpath)
            utils.write_text(final_cache_path, final_md)

        page_path = os.path.join(pages_dir, f"{pid}.md")
        utils.write_text(page_path, final_md)
        results[pid] = {
            "markdown_path": page_path,
            "markdown_content": final_md,
            "hybrid_results": {
                "file_hits": file_hits,
                "sym_hits": sym_hits,
            }
        }

    return results

# Example usage:
# results = generate_wiki_pages(output_root="/path/to/repo_cache")
# print(results.keys())