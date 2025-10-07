import ast
import gzip
import hashlib
import io
import json
import textwrap
import os
import re
import shutil
import sys
import tempfile
import traceback
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen

from dotenv import load_dotenv

# ===================== Load environment variables =====================
load_dotenv()

# ===================== Paths / Config =====================
MAX_FILE_BYTES = 2 * 1024 * 1024  # 2MB per file safety limit
SKIP_DIRS = {
    ".git", "__pycache__", "venv", ".venv", "build", "dist", "node_modules",
    ".mypy_cache", ".pytest_cache", "target", "out", ".gradle", ".idea"
}

PY_EXTS   = {"py"}
JS_TS_EXTS= {"js", "jsx", "ts", "tsx", "mjs", "cjs"}
JAVA_EXTS = {"java"}
GO_EXTS   = {"go"}
C_EXTS    = {"c", "h"}
CPP_EXTS  = {"cc", "cpp", "cxx", "hpp", "hh", "hxx", "h++", "c++"}
RUST_EXTS = {"rs"}
RUBY_EXTS = {"rb"}
PHP_EXTS  = {"php"}
KT_EXTS   = {"kt", "kts"}

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sanitize_repo_name(name: str) -> str:
    return re.sub(r"[^\w\-\.]+", "-", name).strip("-")

def parse_github_url(url: str):
    url = url.strip()
    url = re.sub(r"\.git$", "", url)
    m = re.match(r"^https?://github\.com/([^/]+)/([^/]+)(?:/(tree|blob)/([^/]+)(/.*)?)?$", url)
    if not m:
        raise ValueError("Unrecognized GitHub URL. Expect https://github.com/<owner>/<repo>[...]")
    owner, repo, kind, branch, subpath = m.groups()
    repo = sanitize_repo_name(repo)
    subpath = (subpath or "").lstrip("/")
    return {"owner": owner, "repo": repo, "branch": branch, "subpath": subpath, "kind": kind or "repo"}

def http_get_json(url: str, token: Optional[str] = None):
    headers = {"User-Agent": "streamlit-kg-app"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers)
    with urlopen(req, timeout=30) as resp:
        return json.load(io.TextIOWrapper(resp, encoding="utf-8"))

def get_default_branch(owner: str, repo: str, token: Optional[str] = None) -> str:
    try:
        info = http_get_json(f"https://api.github.com/repos/{owner}/{repo}", token=token)
        if info.get("default_branch"):
            return info["default_branch"]
    except Exception:
        pass
    for candidate in ("main", "master"):
        if can_download_zip(owner, repo, candidate):
            return candidate
    return "main"

def can_download_zip(owner: str, repo: str, branch: str) -> bool:
    url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"
    try:
        req = Request(url, headers={"User-Agent": "streamlit-kg-app"})
        with urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False

def download_repo_zip(owner: str, repo: str, branch: str) -> bytes:
    url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"
    req = Request(url, headers={"User-Agent": "streamlit-kg-app"})
    with urlopen(req, timeout=60) as resp:
        return resp.read()

def unzip_to_temp(zip_bytes: bytes) -> str:
    tmpdir = tempfile.mkdtemp(prefix="ghrepo_")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        zf.extractall(tmpdir)
    entries = [os.path.join(tmpdir, d) for d in os.listdir(tmpdir)]
    dirs = [p for p in entries if os.path.isdir(p)]
    if not dirs:
        raise RuntimeError("Unexpected ZIP structure.")
    return max(dirs, key=lambda p: sum(len(files) for _, _, files in os.walk(p)))

def detect_lang_by_ext(ext: str) -> str:
    e = ext.lower().lstrip(".")
    if e in PY_EXTS: return "python"
    if e in JS_TS_EXTS: return "javascript"
    if e in JAVA_EXTS: return "java"
    if e in GO_EXTS: return "go"
    if e in CPP_EXTS or e in C_EXTS: return "cpp" if e in CPP_EXTS else "c"
    if e in RUST_EXTS: return "rust"
    if e in RUBY_EXTS: return "ruby"
    if e in PHP_EXTS: return "php"
    if e in KT_EXTS: return "kotlin"
    return "text"

def iter_repo_files(root_dir: str, subpath: Optional[str] = None, max_files: Optional[int] = None):
    base = os.path.join(root_dir, subpath) if subpath else root_dir
    count = 0
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            abs_path = os.path.join(dirpath, fn)
            rel_path = os.path.relpath(abs_path, root_dir).replace("\\", "/")
            yield abs_path, rel_path
            count += 1
            if max_files and count >= max_files:
                return

def read_text_file(path: str) -> Optional[str]:
    try:
        if os.path.getsize(path) > MAX_FILE_BYTES:
            return None
        with open(path, "rb") as f:
            data = f.read()
        if b"\x00" in data:
            return None
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("utf-8", errors="ignore")
    except Exception:
        return None

def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path

def fingerprint(owner: str, repo: str, branch: str, subpath: Optional[str], url: str) -> str:
    payload = f"{owner}/{repo}@{branch}:{subpath or ''}|{url}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]

def load_json_autoz(path: str) -> dict:
    try:
        if path.endswith(".gz"):
            with gzip.open(path, "rt", encoding="utf-8") as f:
                return json.load(f)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except UnicodeDecodeError:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
        
def save_json_gz(obj: dict, path: str):
    ensure_dir(os.path.dirname(path))
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))

# ===================== Language Parsers =====================

def parse_python_text(py_src: str):
    classes, imports, functions = [], [], []
    try:
        tree = ast.parse(py_src)
    except SyntaxError:
        return classes, imports, functions
    if hasattr(tree, "body"):
        for n in tree.body:
            if isinstance(n, ast.FunctionDef) or isinstance(n, ast.AsyncFunctionDef):
                functions.append(n.name)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({"type": "import", "module": alias.name, "names": [], "level": 0})
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            names = [alias.name for alias in node.names]
            imports.append({"type": "from", "module": mod, "names": names, "level": node.level or 0})
    return classes, imports, functions

_ident = r"[A-Za-z_][A-Za-z0-9_]*"
_js_ident = r"[A-Za-z_$][A-Za-z0-9_$]*"

def parse_js_ts_text(src: str):
    classes, imports, functions = [], [], []
    for m in re.finditer(rf"\bclass\s+({_js_ident})\b", src):
        classes.append(m.group(1))
    for m in re.finditer(r"""import\s+(?:[\s\S]*?\s+from\s+)?['"'"]""", src):
        imports.append({"type": "import", "module": m.group(1), "names": [], "level": 0})
    for m in re.finditer(r"""require\(\s*'"['"]\s*\)""", src):
        imports.append({"type": "import", "module": m.group(1), "names": [], "level": 0})
    for m in re.finditer(rf"\bfunction\s+({_js_ident})\s*\(", src):
        functions.append(m.group(1))
    for m in re.finditer(rf"\bexport\s+function\s+({_js_ident})\s*\(", src):
        functions.append(m.group(1))
    for m in re.finditer(rf"\b(?:const|let|var)\s+({_js_ident})\s*=\s*function\b", src):
        functions.append(m.group(1))
    for m in re.finditer(rf"\b(?:const|let|var)\s+({_js_ident})\s*=\s*\(", src):
        functions.append(m.group(1))
    return classes, imports, list(dict.fromkeys(functions))

def parse_java_text(src: str):
    classes, imports, functions = [], [], []
    for m in re.finditer(rf"\b(class|interface|enum)\s+({_ident})\b", src):
        classes.append(m.group(2))
    for m in re.finditer(r"\bimport\s+([a-zA-Z0-9_\.]+)(?:\s*;\s*)", src):
        imports.append({"type": "import", "module": m.group(1), "names": [], "level": 0})
    return classes, imports, functions

def parse_go_text(src: str):
    classes, imports, functions = [], [], []
    for m in re.finditer(r'import\s+"([^"]+)"', src):
        imports.append({"type": "import", "module": m.group(1), "names": [], "level": 0})
    block = re.search(r"import\s*\((.*?)\)", src, re.S)
    if block:
        for m in re.finditer(r'"([^"]+)"', block.group(1)):
            imports.append({"type": "import", "module": m.group(1), "names": [], "level": 0})
    for m in re.finditer(rf"\btype\s+({_ident})\s+struct\b", src):
        classes.append(m.group(1))
    for m in re.finditer(rf"\bfunc\s+(?:\([^)]+\)\s*)?({_ident})\s*\(", src):
        functions.append(m.group(1))
    return classes, imports, functions

def parse_c_cpp_text(src: str):
    """
    Heuristic parsing for C/C++:
      - #include "..." and #include <...>  -> imports
      - class/struct <Name>                -> classes
      - top-level function definitions     -> functions (declarations excluded)
    """
    import re

    classes, imports, functions = [], [], []

    # Includes: #include <header> or #include "header"
    include_pattern = r'#\s*include\s*<"[>"]'
    for m in re.finditer(include_pattern, src):
        imports.append({"type": "import", "module": m.group(1), "names": [], "level": 0})

    # Identifier pattern
    _ident = r"[A-Za-z_][A-Za-z0-9_]*"

    # class/struct names
    for m in re.finditer(rf"\b(class|struct)\s+({_ident})\b", src):
        classes.append(m.group(2))

    # Heuristic top-level function definition (requires a body '{', avoids ';' declarations)
    # Examples matched:
    #   int foo(int a) { ... }
    #   static inline MyType ns::Class::method(T x) { ... }
    #   template<typename T> T bar(T x) { ... }
    func_pattern = (
        r"(?m)^[ \t]*"                 # line start
        r"[A-Za-z_][\w:\s\*\&\<\>]*\s+" # return type / qualifiers
        r"(" + _ident + r")"           # function name (capture)
        r"\s*\([^;]*\)"                # args (not containing ';')
        r"\s*\{"                       # opening brace of body
    )
    for m in re.finditer(func_pattern, src):
        functions.append(m.group(1))

    # De-dup preserve order
    functions = list(dict.fromkeys(functions))
    return classes, imports, functions



def parse_rust_text(src: str):
    classes, imports, functions = [], [], []
    for m in re.finditer(r"\buse\s+([A-Za-z0-9_:\{\}\*,\s]+);", src):
        mod = re.sub(r"\s+", " ", m.group(1)).strip()
        imports.append({"type": "import", "module": mod, "names": [], "level": 0})
    for m in re.finditer(rf"\b(struct|enum)\s+({_ident})\b", src):
        classes.append(m.group(2))
    for m in re.finditer(rf"\bfn\s+({_ident})\s*\(", src):
        functions.append(m.group(1))
    return classes, imports, functions

def parse_ruby_text(src: str):
    classes, imports, functions = [], [], []
    for m in re.finditer(rf"\bclass\s+({_ident})\b", src):
        classes.append(m.group(1))
    for m in re.finditer(r"""(?:require|require_relative)\s+'"['"]""", src):
        imports.append({"type": "import", "module": m.group(1), "names": [], "level": 0})
    for m in re.finditer(rf"(?m)^\s*def\s+({_ident})\b", src):
        functions.append(m.group(1))
    return classes, imports, functions

def parse_php_text(src: str):
    classes, imports, functions = [], [], []
    for m in re.finditer(rf"\bclass\s+({_ident})\b", src):
        classes.append(m.group(1))
    for m in re.finditer(rf"\bfunction\s+({_ident})\s*\(", src):
        functions.append(m.group(1))
    for m in re.finditer(rf"\buse\s+([A-Za-z0-9_\\]+)\s*;", src):
        imports.append({"type": "import", "module": m.group(1), "names": [], "level": 0})
    return classes, imports, functions

def parse_kotlin_text(src: str):
    classes, imports, functions = [], [], []
    for m in re.finditer(rf"\b(class|object|interface)\s+({_ident})\b", src):
        classes.append(m.group(2))
    for m in re.finditer(rf"\bimport\s+([A-Za-z0-9_\.]+)\s*", src):
        imports.append({"type": "import", "module": m.group(1), "names": [], "level": 0})
    for m in re.finditer(rf"\bfun\s+({_ident})\s*\(", src):
        functions.append(m.group(1))
    return classes, imports, functions

def parse_any_text_by_ext(ext: str, text: str):
    e = ext.lower().lstrip(".")
    if e in PY_EXTS: return parse_python_text(text)
    if e in JS_TS_EXTS: return parse_js_ts_text(text)
    if e in JAVA_EXTS: return parse_java_text(text)
    if e in GO_EXTS: return parse_go_text(text)
    if e in C_EXTS or e in CPP_EXTS: return parse_c_cpp_text(text)
    if e in RUST_EXTS: return parse_rust_text(text)
    if e in RUBY_EXTS: return parse_ruby_text(text)
    if e in PHP_EXTS: return parse_php_text(text)
    if e in KT_EXTS: return parse_kotlin_text(text)
    return [], [], []


# ===================== Compact v2 (per-file) + Sharding =====================
def build_repo_compact_v2(root_dir: str, subpath: Optional[str] = None, progress=None, max_files: Optional[int] = None):
    """
    Compact v2:
      - dicts.imports (deduped module/header names)
      - files: [{path, lang, classes[], functions[], imports[idx]}]
    """
    files = []
    import_to_idx = {}
    imports_list = []

    def get_import_index(name: str) -> int:
        if name not in import_to_idx:
            import_to_idx[name] = len(imports_list)
            imports_list.append(name)
        return import_to_idx[name]

    file_list = list(iter_repo_files(root_dir, subpath, max_files=max_files))
    n = len(file_list)
    totals = {"files": 0, "classes": 0, "functions": 0, "imports": 0}

    for i, (abs_path, rel_path) in enumerate(file_list, start=1):
        if progress:
            progress.progress(min(i / max(n, 1), 1.0), text=f"Scanning {rel_path} ({i}/{n})")

        ext = os.path.splitext(rel_path)[1]
        lang = detect_lang_by_ext(ext)
        text = read_text_file(abs_path)

        rec = {"path": rel_path, "lang": lang, "classes": [], "functions": [], "imports": []}
        totals["files"] += 1

        if not text:
            files.append(rec)
            continue

        classes, imports, functions = parse_any_text_by_ext(ext, text)

        if classes:
            rec["classes"] = sorted(set(classes))
            totals["classes"] += len(rec["classes"])

        if functions:
            rec["functions"] = sorted(set(functions))
            totals["functions"] += len(rec["functions"])

        if imports:
            mods = []
            for imp in imports:
                module = (imp.get("module") or "").strip()
                if module:
                    mods.append(module)
            if mods:
                mods = sorted(set(mods))
                rec["imports"] = [get_import_index(m) for m in mods]
                totals["imports"] += len(mods)

        files.append(rec)

    compact = {"meta": {}, "dicts": {"imports": imports_list}, "files": files}
    return compact, totals

def save_compact_graph_v2(cache_dir: str, meta: dict, compact: dict, gzip_out: bool = True) -> str:
    compact["meta"] = meta | {"schema": "v2-compact"}
    base_name = f"{meta['owner']}__{meta['repo']}__{meta['branch']}__{meta['graph_id']}__v2.json"
    base_name = base_name.replace("/", "_")
    out_path = os.path.join(cache_dir, base_name + (".gz" if gzip_out else ""))
    if gzip_out:
        save_json_gz(compact, out_path)
    else:
        ensure_dir(os.path.dirname(out_path))
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(compact, f, ensure_ascii=False, separators=(",", ":"))
    return out_path

def shard_compact_by_top_dir(compact: dict, out_dir: str, gzip_out: bool = True) -> dict:
    """
    Writes:
      - out_dir/manifest.json[.gz]
      - out_dir/shards/shard__<topdir>.json[.gz]
    """
    imports = compact.get("dicts", {}).get("imports", [])
    files = compact.get("files", [])
    groups = defaultdict(list)
    for f in files:
        top = (f["path"].split("/", 1)[0]) if "/" in f["path"] else ""
        groups[top].append(f)

    ensure_dir(out_dir)
    shards_dir = os.path.join(out_dir, "shards")
    ensure_dir(shards_dir)

    meta = compact.get("meta", {})
    shard_records = []
    for top, flist in groups.items():
        shard = {"meta": meta | {"shard": top}, "dicts": {"imports": imports}, "files": flist}
        name = f"shard__{top or '_root'}.json" + (".gz" if gzip_out else "")
        path = os.path.join(shards_dir, name)
        if gzip_out:
            save_json_gz(shard, path)
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(shard, f, ensure_ascii=False, separators=(",", ":"))
        shard_records.append({"topdir": top, "path": os.path.relpath(path, out_dir)})

    manifest = {"meta": meta, "shards": shard_records, "imports_count": len(imports), "files_total": len(files)}
    man_path = os.path.join(out_dir, "manifest.json" + (".gz" if gzip_out else ""))
    if gzip_out:
        save_json_gz(manifest, man_path)
    else:
        with open(man_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, separators=(",", ":"))
    return manifest


# ===================== README collection & integration =====================
READ_ME_REGEX = re.compile(r"(?i)^readme(\.(md|rst|txt))?$")
def collect_readmes_text(root_dir: str, subpath: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Scan repo for README-like files and return list of {path, size, content}.
    """
    base = os.path.join(root_dir, subpath) if subpath else root_dir
    readmes = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if READ_ME_REGEX.match(fn):
                abs_path = os.path.join(dirpath, fn)
                rel_path = os.path.relpath(abs_path, root_dir).replace("\\", "/")
                txt = read_text_file(abs_path) or ""
                if txt.strip():
                    readmes.append({"path": rel_path, "size": len(txt), "content": txt})
    return readmes

def save_doc_hints(graph_meta: Dict[str, Any], v2_dir: str, readmes: List[Dict[str, Any]]) -> str:
    """
    Save README doc hints under: <v2_dir>/<graph_id>/doc_hints.json.gz
    """
    out_dir = ensure_dir(os.path.join(v2_dir, graph_meta["graph_id"]))
    out_path = os.path.join(out_dir, "doc_hints.json.gz")
    save_json_gz({"meta": graph_meta, "readmes": readmes}, out_path)
    return out_path

def load_doc_hints(graph_id: str, v2_dir: str) -> Optional[Dict[str, Any]]:
    p1 = os.path.join(v2_dir, graph_id, "doc_hints.json.gz")
    p2 = os.path.join(v2_dir, graph_id, "doc_hints.json")
    if os.path.isfile(p1):
        return load_json_autoz(p1)
    if os.path.isfile(p2):
        return load_json_autoz(p2)
    return None

def make_readme_excerpt(doc_hints: Dict[str, Any], max_chars: int = 4000) -> str:
    """
    Select and concatenate README content (prioritizing root README, then docs/, then others) up to max_chars.
    """
    readmes = doc_hints.get("readmes", [])
    if not readmes:
        return ""
    def score(r: Dict[str, Any]) -> float:
        p = r["path"].lower()
        s = 0.0
        if "/" not in p: s += 100.0                # root readme
        if p.startswith("readme"): s += 50.0
        if p.startswith("docs/") or "/docs/" in p: s += 40.0
        if p.startswith("examples/") or "/examples/" in p: s += 30.0
        return s - 0.001 * len(p)
    reads = sorted(readmes, key=score, reverse=True)

    chunks = []
    total = 0
    for r in reads:
        header = f"\n### {r['path']}\n"
        piece = header + (r.get("content") or "")
        take = piece
        if total + len(piece) > max_chars:
            take = piece[: max(0, max_chars - total)]
        if take:
            chunks.append(take)
            total += len(take)
        if total >= max_chars:
            break
    return "\n".join(chunks).strip()


# ===================== Relevance Guard (signals + pruning) =====================

def _norm_title(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[\s\-_]+", " ", s)
    s = s.replace("&", "and")
    return s

def _derive_repo_signals_from_paths(file_paths: List[str]) -> dict:
    has_py = any(p.endswith(".py") for p in file_paths)
    has_js_ts = any(p.endswith((".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")) for p in file_paths)
    has_java = any(p.endswith(".java") for p in file_paths)
    has_cpp = any(p.endswith((".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh", ".hxx")) for p in file_paths)
    has_go = any(p.endswith(".go") for p in file_paths)
    has_rust = any(p.endswith(".rs") for p in file_paths)
    has_kotlin = any(p.endswith((".kt", ".kts")) for p in file_paths)
    has_php = any(p.endswith(".php") for p in file_paths)
    has_ruby = any(p.endswith(".rb") for p in file_paths)

    lower_paths = [p.lower() for p in file_paths]
    has_examples_dir = any("/examples/" in p or p.startswith("examples/") for p in lower_paths)
    has_notebooks = any(p.endswith(".ipynb") for p in lower_paths) or any("/notebook" in p or "/notebooks" in p for p in lower_paths)
    has_docs = any(p in ("readme", "readme.md") or p.startswith("docs/") or "/docs/" in p or p.endswith(("mkdocs.yml", "mkdocs.yaml")) for p in lower_paths)
    has_scripts = any("/scripts/" in p or p.startswith("scripts/") for p in lower_paths)
    has_bench = any("bench" in p or "perf" in p for p in lower_paths)
    has_infra = any(any(tok in p for tok in ["dockerfile", "docker-compose", "helm", "k8s", "terraform", "ansible", ".github/workflows", "cloudbuild", "jenkinsfile"]) for p in lower_paths)
    has_frontend = any(any(tok in p for tok in ["package.json", "vite.config", "webpack.config", "src/components", "src/app", "next.config"]) for p in lower_paths)
    has_backend = any(any(tok in p for tok in ["api/", "/controllers/", "/services/", "/routes/"]) for p in lower_paths)
    has_data = any(any(tok in p for tok in ["data/", "/dataset", "/etl", "/pipeline", "/db/", ".sql", "migrations/"]) for p in lower_paths)
    has_models = any(any(tok in p for tok in ["model", "ml", "nn", "inference", "training", "weights"]) for p in lower_paths)

    return {
        "has_py": has_py, "has_js_ts": has_js_ts, "has_java": has_java, "has_cpp": has_cpp,
        "has_go": has_go, "has_rust": has_rust, "has_kotlin": has_kotlin, "has_php": has_php, "has_ruby": has_ruby,
        "has_examples_dir": has_examples_dir, "has_notebooks": has_notebooks, "has_docs": has_docs,
        "has_scripts": has_scripts, "has_bench": has_bench, "has_infra": has_infra,
        "has_frontend": has_frontend, "has_backend": has_backend, "has_data": has_data, "has_models": has_models,
    }

def _allowed_forbidden_sections(signals: dict) -> tuple[list, list]:
    base_allowed = [
        "overview",
        "system architecture",
        "core features",
        "data management/flow",
        "deployment/infrastructure",
        "extensibility and customization",
    ]
    if signals["has_frontend"]:
        base_allowed.append("frontend components")
    if signals["has_backend"] or any(signals[k] for k in ("has_py","has_java","has_go","has_rust","has_php","has_kotlin")):
        base_allowed.append("backend systems")
    if signals["has_models"]:
        base_allowed.append("model integration")
    if signals["has_examples_dir"] or signals["has_notebooks"]:
        base_allowed.append("examples and notebooks")

    forbidden = []
    if not (signals["has_examples_dir"] or signals["has_notebooks"]):
        forbidden.extend(["examples", "notebooks", "examples and notebooks"])
    if not signals["has_frontend"]:
        forbidden.append("frontend components")
    if not (signals["has_backend"] or any(signals[k] for k in ("has_py","has_java","has_go","has_rust","has_php","has_kotlin"))):
        forbidden.append("backend systems")
    if not signals["has_models"]:
        forbidden.append("model integration")
    forbidden.extend(["text examples", "c++ examples", "python examples", "random scripts", "playground", "misc"])

    allowed_norm = sorted(set(_norm_title(x) for x in base_allowed))
    forbidden_norm = sorted(set(_norm_title(x) for x in forbidden))
    return allowed_norm, forbidden_norm

def _collect_all_paths_from_compact(compact: dict) -> List[str]:
    return [f.get("path", "") for f in compact.get("files", [])]

def _prune_and_renumber_wiki(xml_text: str,
                             allowed_sections_norm: list[str],
                             file_paths_set: set[str]) -> str:
    import xml.etree.ElementTree as ET
    def _exists_file(fp: str) -> bool:
        return fp in file_paths_set
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return xml_text
    if root.tag != "wiki_structure":
        return xml_text

    sections_el = root.find("sections")
    pages_el = root.find("pages")
    if sections_el is None or pages_el is None:
        return xml_text

    # Filter sections by allowed titles
    kept_sections = []
    for s in list(sections_el.findall("section")):
        title = (s.findtext("title") or "").strip()
        if title and _norm_title(title) in allowed_sections_norm:
            kept_sections.append(s)
    for s in list(sections_el):
        sections_el.remove(s)
    for s in kept_sections:
        sections_el.append(s)

    # Keep only pages with at least one valid file
    page_elems = list(pages_el.findall("page"))
    kept_pages = []
    for p in page_elems:
        rf = p.find("relevant_files")
        valid_files = []
        if rf is not None:
            for fp in rf.findall("file_path"):
                t = (fp.text or "").strip()
                if t and _exists_file(t):
                    valid_files.append(t)
        if valid_files:
            for child in list(rf):
                rf.remove(child)
            for v in sorted(set(valid_files)):
                ET.SubElement(rf, "file_path").text = v
            kept_pages.append(p)
    for p in page_elems:
        pages_el.remove(p)
    for p in kept_pages:
        pages_el.append(p)

    # Remove invalid page_refs and drop empty sections
    valid_page_ids = set(p.get("id") for p in pages_el.findall("page"))
    final_sections = []
    for s in list(sections_el.findall("section")):
        pages_container = s.find("pages")
        kept_refs = []
        if pages_container is not None:
            for r in list(pages_container.findall("page_ref")):
                tid = (r.text or "").strip()
                if tid in valid_page_ids:
                    kept_refs.append(tid)
        if pages_container is None:
            pages_container = ET.SubElement(s, "pages")
        for r in list(pages_container):
            pages_container.remove(r)
        for tid in kept_refs:
            ET.SubElement(pages_container, "page_ref").text = tid
        if kept_refs:
            final_sections.append(s)
    for s in list(sections_el):
        sections_el.remove(s)
    for s in final_sections:
        sections_el.append(s)

    # Renumber IDs sequentially
    new_sec_ids = {}
    for i, s in enumerate(list(sections_el.findall("section")), start=1):
        old = s.get("id")
        new = f"section-{i}"
        new_sec_ids[old] = new
        s.set("id", new)
    old_to_new_page = {}
    for i, p in enumerate(list(pages_el.findall("page")), start=1):
        old = p.get("id")
        new = f"page-{i}"
        old_to_new_page[old] = new
        p.set("id", new)
        ps = p.find("parent_section")
        if ps is not None:
            o = (ps.text or "").strip()
            if o in new_sec_ids:
                ps.text = new_sec_ids[o]
            if not ps.text:
                ps.text = "section-1"
    for s in list(sections_el.findall("section")):
        pages_container = s.find("pages") or s
        for r in list(pages_container.findall("page_ref")):
            tid = (r.text or "").strip()
            if tid in old_to_new_page:
                r.text = old_to_new_page[tid]
    return ET.tostring(root, encoding="unicode")


# ===================== Prompt Builders (QGenie) =====================
XML_SPEC = """Return your analysis in the following XML format:

<wiki_structure>
  <title>[Overall title for the wiki]</title>
  <description>[Brief description of the repository]</description>
  <sections>
    <section id="section-1">
      <title>[Section title]</title>
      <pages>
        <page_ref>page-1</page_ref>
      </pages>
      <subsections>
        <section_ref>section-2</section_ref>
      </subsections>
    </section>
  </sections>
  <pages>
    <page id="page-1">
      <title>[Page title]</title>
      <description>[Brief description]</description>
      <importance>high|medium|low</importance>
      <relevant_files>
        <file_path>[Path to a relevant file]</file_path>
      </relevant_files>
      <related_pages>
        <related>page-2</related>
      </related_pages>
      <parent_section>section-1</parent_section>
    </page>
  </pages>
</wiki_structure>
"""

PARTIAL_XML_SPEC = """Return ONLY this exact structure for this shard:

<partial_wiki>
  <sections>
    <section id="sec-SHARD-1">
      <title>[Section title]</title>
      <pages>
        <page id="page-SHARD-1">
          <title>[Page title]</title>
          <description>[Brief description]</description>
          <importance>high|medium|low</importance>
          <relevant_files>
            <file_path>[path/to/file]</file_path>
          </relevant_files>
          <related_pages>
            <related>page-SHARD-2</related>
          </related_pages>
        </page>
      </pages>
      <subsections>
        <section_ref>sec-SHARD-2</section_ref>
      </subsections>
    </section>
  </sections>
</partial_wiki>
"""


def build_prompt_shard_guarded(
    owner_repo: str,
    source_url: str,
    lang_text: str,
    shard_name: str,
    shard_summary: dict,
    allowed_sections_norm: list[str],
    forbidden_sections_norm: list[str],
    readme_excerpt: str = ""
) -> str:
    """
    Builds a strict shard prompt for documentation generation.
    """
    import textwrap

    files = shard_summary["files"]
    file_paths = [f["path"] for f in files]

    context_files = []
    for f in files:
        context_files.append({
            "path": f["path"],
            "lang": f["lang"],
            "classes": f["classes"][:8],
            "functions": f["functions"][:8],
            "imports": f["imports"][:8],
        })

    readme_block = ""
    if readme_excerpt:
        readme_block = textwrap.dedent(f"""
            ## README excerpt (context; do NOT quote directly; use for guidance only)
            <readme>
            {readme_excerpt}
            </readme>
        """).strip()

    file_paths_json = json.dumps(file_paths, ensure_ascii=False, indent=2)
    context_files_json = json.dumps(context_files[:80], ensure_ascii=False, indent=2)

    prompt = textwrap.dedent(f"""
        You are a senior documentation architect.

        Repository: {owner_repo or '(unknown)'}
        Source: {source_url or '(unknown)'}
        This prompt is for shard: {shard_name}
        IMPORTANT: The wiki content MUST be generated in {lang_text}.

        {readme_block}

        ## What you are building (THIS SHARD ONLY)
        Return a coherent <partial_wiki> for this shard. Do NOT describe other shards or the whole repo.

        ## REQUIRED SECTIONS (must always be present, in this order)
        1. **Overview**: Summarize what the repository does, its main purpose, and high-level functionality.
        2. **Installation and Setup**: Provide instructions and context for installing, configuring, and running the repository.
        3. **Core Architecture**: Describe the main architectural components, design patterns, and how the system is organized.

        ## DYNAMIC SECTION GENERATION
        - After the required sections, analyze the repository files, context, and knowledge graph.
        - Propose additional sections and pages that are most relevant for this repository.
        - The section titles and pages should reflect the actual content and structure of the repo.
        - Example: For a machine learning repo (e.g., Transformers), you might include sections/pages like "Modeling Classes", "Export & Inference", "Fine-Tuning", "Testing".
        - Example: For a deployment/web repo, you might include "Frontend Implementation", "Backend Implementation", "Deployment", "CI/CD Pipeline", etc.
        - Use your judgment to surface the most important and useful topics for users of this repo.

        ## ALLOWED vs FORBIDDEN section titles
        - Allowed (use ONLY these; case-insensitive match): {allowed_sections_norm}
        - Forbidden (must NOT appear): {forbidden_sections_norm}

        ## File selection rules (EXTREMELY IMPORTANT)
        - You are given a list of files from this shard (see below). **You may ONLY reference file paths from that list.**
        - For EACH page you propose:
          - Include **2–5** <file_path> entries under <relevant_files>.
          - **Prefer code or config files** that directly support the page topic.
          - **Avoid README-like files** (`README`, `README.md`, `README.rst`, `README.txt`) **EXCEPT** for pages under **"Overview"** or **"Installation and Setup"**.
          - If you cannot find suitable files for a page, **do NOT create that page**.
        - NEVER invent file names or directories. Use exact, case-correct paths from the list.

        ## Page quality bar
        - Write concise, specific titles and descriptions.
        - Avoid generic statements; anchor content to the chosen relevant files.
        - Keep 6–14 pages total across all sections in this shard. No filler.

        ## Files from this shard (you MUST choose file_path ONLY from this list)
        [file_paths]
        {file_paths_json}
        [/file_paths]

        ## Context details for some files (use as hints; do NOT copy)
        {context_files_json}

        ## REQUIRED OUTPUT FORMAT (STRICT):
        <partial_wiki>
          <sections>
            <section id="sec-{shard_name}-1">
              <title>[Section title from allowed list]</title>
              <pages>
                <page id="page-{shard_name}-1">
                  <title>[Page title]</title>
                  <description>[Brief description in {lang_text}]</description>
                  <importance>high|medium|low</importance>
                  <relevant_files>
                    <file_path>[One file path from the list above]</file_path>
                    <file_path>[Another]</file_path>
                  </relevant_files>
                  <related_pages>
                    <related>page-{shard_name}-2</related>
                  </related_pages>
                </page>
              </pages>
              <subsections>
                <section_ref>sec-{shard_name}-2</section_ref>
              </subsections>
            </section>
          </sections>
        </partial_wiki>

        ## HARD CONSTRAINTS
        - Output ONLY <partial_wiki>. No extra text, no markdown, no commentary.
        - Use IDs starting with: sec-{shard_name}-N, page-{shard_name}-N (N = 1..).
        - Use section titles ONLY from the allowed list, never from the forbidden list.
        - For non-"Overview"/"Installation and Setup" pages, DO NOT include README-like files in <relevant_files>.
        - Do NOT create a page if you cannot pick 2–5 valid file paths for it from the list.

        ## DEDUPLICATION POLICY (CRITICAL)
        - Each section title MUST appear only once in this shard.
        - Each page title MUST be unique within this shard (case-insensitive).
        - If multiple pages or sections have the same or similar title, merge their content or keep only the most relevant one.
        - Remove any duplicate or redundant sections or pages.
        - Only use canonical allowed section titles. Do NOT create variations (e.g., 'Overview' and 'Project Overview').
        - If two sections/pages cover similar content, merge them into one and remove the duplicate.
    """).strip()

    return prompt

def build_final_refine_prompt(
    owner_repo: str,
    source_url: str,
    lang_text: str,
    merged_xml: str,
    readme_excerpt: str = ""
) -> str:
    """
    Final single-shot refine:
      - normalize and validate,
      - enforce section title policy,
      - enforce file selection policy,
      - produce ONLY <wiki_structure>.
    """
    import textwrap

    readme_block = ""
    if readme_excerpt:
        readme_block = textwrap.dedent(f"""
            ## README excerpt (context; do NOT quote directly; use for guidance only)
            <readme>
            {readme_excerpt}
            </readme>
        """).strip()

    required_output_format = textwrap.dedent(f"""
        <wiki_structure>
          <title>[Overall wiki title]</title>
          <description>[Short description in {lang_text}]</description>
          <sections>
            <section id="section-1">
              <title>[Section title]</title>
              <pages>
                <page_ref>page-1</page_ref>
              </pages>
              <subsections>
                <section_ref>section-2</section_ref>
              </subsections>
            </section>
          </sections>
          <pages>
            <page id="page-1">
              <title>[Page title]</title>
              <description>[Brief description in {lang_text}]</description>
              <importance>high|medium|low</importance>
              <relevant_files>
                <file_path>[Exact repo path]</file_path>
              </relevant_files>
              <related_pages>
                <related>page-2</related>
              </related_pages>
              <parent_section>section-1</parent_section>
            </page>
          </pages>
        </wiki_structure>
    """).strip()

    prompt = textwrap.dedent(f"""
        You are a meticulous documentation architect.

        We combined shard-level partial wikis into a single merged XML for repository: {owner_repo or '(unknown)'}
        Source: {source_url or '(unknown)'}
        IMPORTANT: The wiki content MUST be generated in {lang_text}.

        {readme_block}

        ## REQUIRED SECTIONS (must always be present, in this order)
        1. **Overview**: Summarize what the repository does, its main purpose, and high-level functionality.
        2. **Installation and Setup**: Provide instructions and context for installing, configuring, and running the repository.
        3. **Core Architecture**: Describe the main architectural components, design patterns, and how the system is organized.

        ## DYNAMIC SECTION GENERATION
        - After the required sections, analyze the repository files, context, and knowledge graph.
        - Propose additional sections and pages that are most relevant for this repository.
        - The section titles and pages should reflect the actual content and structure of the repo.
        - Example: For a machine learning repo (e.g., Transformers), you might include sections/pages like "Modeling Classes", "Export & Inference", "Fine-Tuning", "Testing".
        - Example: For a deployment/web repo, you might include "Frontend Implementation", "Backend Implementation", "Deployment", "CI/CD Pipeline", etc.
        - Use your judgment to surface the most important and useful topics for users of this repo.

        ## Policies to enforce
        1) **IDs and references**
           - Sections: id = section-1..N; Pages: id = page-1..M (sequential, no gaps).
           - Each <page> MUST have exactly one <parent_section> that exists.
           - All <section_ref> and <page_ref> MUST reference existing IDs.

        2) **Section and Page Titles (DEDUPLICATION POLICY)**
           - Each section title MUST appear only once in the final wiki (case-insensitive).
           - Each page title MUST be unique within the final wiki (case-insensitive).
           - If multiple sections or pages have the same or similar title, merge their content or keep only the most relevant one.
           - Remove any duplicate or redundant sections or pages.
           - Only use canonical allowed section titles. Do NOT create variations (e.g., 'Overview' and 'Project Overview').
           - If two sections/pages cover similar content, merge them into one and remove the duplicate.

        3) **File selection**
           - Each page MUST include **2–5** <file_path> entries in <relevant_files>.
           - Prefer code or config files relevant to the page topic.
           - **Avoid README-like files** (README, README.md/.rst/.txt) **EXCEPT** for pages under "Overview" or "Installation and Setup".
           - Remove any page that cannot justify at least 1 non-README file (unless under "Overview" or "Installation and Setup").

        4) **Language**
           - All human-readable fields (title, description) must be in {lang_text}.

        ## Merge input (clean and normalize it)
        {merged_xml}

        ## REQUIRED OUTPUT FORMAT (STRICT)
        Return ONLY a single valid <wiki_structure> as defined here (no commentary):
        {required_output_format}
    """).strip()

    return prompt


# ===================== QGenie Inference =====================
def qgenie_generate(prompt: str, model: str = None) -> str:
    try:
        from qgenie import ChatMessage, QGenieClient
    except ImportError:
        raise RuntimeError("qgenie is not installed. Run: pip install qgenie")
    client = QGenieClient(timeout=100)
    chat_response = client.chat(
        messages=[ChatMessage(role="user", content=prompt)], model=model, 
    )
    result = getattr(chat_response, "first_content", None)
    if not result:
        result = str(chat_response)
    return (result or "").strip()

def validate_or_wrap_xml(text: str, root_tag: str) -> str:
    t = text.strip()
    start = t.find(f"<{root_tag}")
    end = t.rfind(f"</{root_tag}>")
    if start != -1 and end != -1:
        return t[start:end + len(f"</{root_tag}>")].strip()
    return f"<{root_tag}>\n{text}\n</{root_tag}>"

def extract_partial(xml_text: str) -> Any:
    import xml.etree.ElementTree as ET
    s = xml_text.strip()
    start = s.find("<partial_wiki")
    end = s.rfind("</partial_wiki>")
    if start == -1 or end == -1:
        s = f"<partial_wiki>{s}</partial_wiki>"
    try:
        return ET.fromstring(s)
    except Exception:
        return ET.fromstring("<partial_wiki><sections/></partial_wiki>")

def merge_partials(partials: List[Any]) -> Any:
    import xml.etree.ElementTree as ET
    section_by_key = {}
    page_pool = []

    def norm_title(s: str) -> str:
        return _norm_title(s)

    for frag in partials:
        sects = frag.find("sections")
        if sects is None: continue
        for s in list(sects.findall("section")):
            title = (s.findtext("title") or "").strip()
            if not title: continue
            key = norm_title(title)
            entry = section_by_key.setdefault(key, {"title": title, "pages": []})
            pages = s.find("pages")
            if pages is not None:
                for p in list(pages.findall("page")):
                    page = {
                        "id": p.get("id") or "",
                        "title": (p.findtext("title") or "").strip(),
                        "description": (p.findtext("description") or "").strip(),
                        "importance": (p.findtext("importance") or "medium").strip(),
                        "relevant_files": [fp.text.strip() for fp in p.findall("./relevant_files/file_path") if (fp.text or "").strip()],
                        "related_pages": [rp.text.strip() for rp in p.findall("./related_pages/related") if (rp.text or "").strip()],
                        "parent_key": key
                    }
                    if page["title"]:
                        entry["pages"].append(page)
                        page_pool.append(page)

    root = ET.Element("root")
    sections_el = ET.SubElement(root, "sections")
    pages_el = ET.SubElement(root, "pages")

    sec_id_map = {}
    for i, (key, entry) in enumerate(section_by_key.items(), start=1):
        sid = f"section-{i}"
        sec_id_map[key] = sid
        s = ET.SubElement(sections_el, "section", {"id": sid})
        ET.SubElement(s, "title").text = entry["title"]

    page_id_map = {}
    for i, page in enumerate(page_pool, start=1):
        pid = f"page-{i}"
        page_id_map[page["id"]] = pid
        p = ET.SubElement(pages_el, "page", {"id": pid})
        ET.SubElement(p, "title").text = page["title"]
        ET.SubElement(p, "description").text = page["description"]
        ET.SubElement(p, "importance").text = page["importance"] or "medium"
        rf = ET.SubElement(p, "relevant_files")
        for fp in sorted(set(page["relevant_files"])):
            ET.SubElement(rf, "file_path").text = fp
        rp = ET.SubElement(p, "related_pages")
        for r in page.get("related_pages", []):
            if r in page_id_map:
                ET.SubElement(rp, "related").text = page_id_map[r]
            else:
                ET.SubElement(rp, "related").text = r
        ET.SubElement(p, "parent_section").text = sec_id_map.get(page.get("parent_key", ""), "section-1")

    for s in list(sections_el.findall("section")):
        title = s.findtext("title") or ""
        key = _norm_title(title)
        entry = section_by_key.get(key, {})
        pages = entry.get("pages", [])
        pages_container = ET.SubElement(s, "pages")
        for page in pages:
            old_id = page.get("id", "")
            final_id = page_id_map.get(old_id)
            if final_id:
                ET.SubElement(pages_container, "page_ref").text = final_id

    return root

def compose_final_wiki(owner_repo: str, description: str, merged_root: Any) -> str:
    import xml.etree.ElementTree as ET
    ws = ET.Element("wiki_structure")
    ET.SubElement(ws, "title").text = f"Wiki – {owner_repo}" if owner_repo else "Wiki"
    ET.SubElement(ws, "description").text = description or "Auto-generated wiki structure."
    src_sections = merged_root.find("sections")
    dst_sections = ET.SubElement(ws, "sections")
    if src_sections is not None:
        for s in list(src_sections.findall("section")):
            dst_sections.append(s)
    src_pages = merged_root.find("pages")
    dst_pages = ET.SubElement(ws, "pages")
    if src_pages is not None:
        for p in list(src_pages.findall("page")):
            dst_pages.append(p)
    return ET.tostring(ws, encoding="unicode")

def clean_final_wiki_duplicates(xml_text: str) -> str:
    """
    Removes duplicate pages (by title, case-insensitive) and merges their relevant_files.
    Also ensures each section title is unique.
    """
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return xml_text

    # Deduplicate sections by title
    sections_el = root.find("sections")
    seen_section_titles = set()
    kept_sections = []
    for s in list(sections_el.findall("section")):
        title = (s.findtext("title") or "").strip().lower()
        if title not in seen_section_titles:
            seen_section_titles.add(title)
            kept_sections.append(s)
    for s in list(sections_el):
        sections_el.remove(s)
    for s in kept_sections:
        sections_el.append(s)

    # Deduplicate pages by title
    pages_el = root.find("pages")
    seen_page_titles = {}
    kept_pages = []
    for p in list(pages_el.findall("page")):
        title = (p.findtext("title") or "").strip().lower()
        if title in seen_page_titles:
            # Merge relevant_files
            prev_p = seen_page_titles[title]
            rf_prev = prev_p.find("relevant_files")
            rf_curr = p.find("relevant_files")
            files_prev = set(fp.text for fp in rf_prev.findall("file_path") if fp.text)
            files_curr = set(fp.text for fp in rf_curr.findall("file_path") if fp.text)
            all_files = files_prev | files_curr
            # Clear and re-add
            for fp in list(rf_prev):
                rf_prev.remove(fp)
            for fp in sorted(all_files):
                ET.SubElement(rf_prev, "file_path").text = fp
            # Optionally: merge descriptions, importance, etc.
        else:
            seen_page_titles[title] = p
            kept_pages.append(p)
    for p in list(pages_el):
        pages_el.remove(p)
    for p in kept_pages:
        pages_el.append(p)

    return ET.tostring(root, encoding="unicode")

# ===================== Output Path Functions =====================
def get_unique_cache_dir(gh_url: str) -> str:
    # Unique name based on sanitized URL and hash
    safe_url = re.sub(r"[^\w\-\.]+", "-", gh_url.strip()).strip("-")
    url_hash = hashlib.sha1(gh_url.encode("utf-8")).hexdigest()[:12]
    return os.path.join(".cache", f"{safe_url}-{url_hash}")

def knowledge_graph_dir(cache_dir: str) -> str:
    return os.path.join(cache_dir, "knowledge_graph")

def wiki_xml_dir(cache_dir: str) -> str:
    return os.path.join(cache_dir, "wiki_xml")

def wiki_default_output_path(cache_dir: str) -> str:
    return os.path.join(wiki_xml_dir(cache_dir), "wiki.xml")

def wiki_partial_output_path(cache_dir: str, shard_name: str) -> str:
    return os.path.join(wiki_xml_dir(cache_dir), f"partial__{shard_name}.xml")

def knowledge_graph_manifest_path(cache_dir: str) -> str:
    return os.path.join(knowledge_graph_dir(cache_dir), "manifest.json.gz")

# ===================== Main Pipeline Function =====================
def build_sharded_wiki_from_github(
    gh_url: str,
    token: Optional[str] = None,
    max_files: int = 0,
    lang_text: str = "English",
    qgenie_model: str = "Pro",
    max_files_per_shard: int = 300,
    readme_max_chars: int = 8000,
    output_root: Optional[str] = None,
) -> Dict[str, Any]:
    """
    End-to-end pipeline: downloads GitHub repo, builds compact graph, shards, generates wiki XML via QGenie.
    Output is always saved under .cache/github-url-unique-name/knowledge_graph and .cache/github-url-unique-name/wiki_xml.
    Returns: dict with paths and final XML content.
    """
    # Output directories
    if output_root is None:
        cache_dir = get_unique_cache_dir(gh_url)
    else:
        cache_dir = output_root
    
    kg_dir = knowledge_graph_dir(cache_dir)
    wiki_dir = wiki_xml_dir(cache_dir)
    os.makedirs(kg_dir, exist_ok=True)
    os.makedirs(wiki_dir, exist_ok=True)

    # Parse GitHub URL
    parts = parse_github_url(gh_url)
    owner = parts["owner"]
    repo = parts["repo"]
    branch = parts["branch"] or get_default_branch(owner, repo, token=token)
    subpath = parts["subpath"] or None

    g_id = fingerprint(owner, repo, branch, subpath, gh_url)
    meta_common = {
        "source_url": gh_url,
        "owner": owner,
        "repo": repo,
        "branch": branch,
        "subpath": subpath or "",
        "created_at": now_iso(),
        "graph_id": g_id,
    }

    # Download and unzip repo
    zip_bytes = download_repo_zip(owner, repo, branch)
    repo_root = unzip_to_temp(zip_bytes)

    # Build compact graph
    limit = max_files if max_files and max_files > 0 else None
    compact, totals = build_repo_compact_v2(repo_root, subpath=subpath, progress=None, max_files=limit)
    meta = meta_common | {"totals": totals}
    single_path = os.path.join(kg_dir, "compact_graph.json.gz")
    save_json_gz(compact, single_path)

    # Collect README files and save doc hints
    readmes = collect_readmes_text(repo_root, subpath=subpath)
    hints_path = None
    if readmes:
        hints_path = os.path.join(kg_dir, "doc_hints.json.gz")
        save_json_gz({"meta": meta, "readmes": readmes}, hints_path)

    # Create shards
    manifest = shard_compact_by_top_dir(compact | {"meta": meta}, out_dir=kg_dir, gzip_out=True)
    man_path = knowledge_graph_manifest_path(cache_dir)

    # Cleanup temp
    try:
        shutil.rmtree(os.path.dirname(repo_root))
    except Exception:
        pass

    # Wiki generation
    manifest_path = man_path
    graph_meta = manifest.get("meta", {})
    owner_repo = f"{graph_meta.get('owner','')}/{graph_meta.get('repo','')}".strip("/")
    source_url = graph_meta.get("source_url", "")

    # Load README doc hints (if available) and prepare excerpt
    readme_hints = None
    if hints_path and os.path.isfile(hints_path):
        readme_hints = load_json_autoz(hints_path)
    readme_excerpt = ""
    if readme_hints:
        readme_excerpt = make_readme_excerpt(readme_hints, max_chars=int(readme_max_chars))

    # Build global path list (for allowed/forbidden + pruning)
    all_paths = []
    for s in manifest.get("shards", []):
        spath = s.get("path")
        if spath and not os.path.isabs(spath):
            spath = os.path.join(kg_dir, spath)
        shard = load_json_autoz(spath)
        all_paths.extend(_collect_all_paths_from_compact(shard))
    signals = _derive_repo_signals_from_paths(all_paths)
    allowed_norm, forbidden_norm = _allowed_forbidden_sections(signals)

    # MAP: per shard
    partial_xmls = []
    saved_partial_paths = []
    for idx, s in enumerate(manifest.get("shards", []), start=1):
        spath = s.get("path")
        if spath and not os.path.isabs(spath):
            spath = os.path.join(kg_dir, spath)
        shard = load_json_autoz(spath)

        shard_name = shard.get("meta", {}).get("shard") or f"shard{idx}"
        safe_shard_name = shard_name.replace("/", "_")
        dict_imports = shard.get("dicts", {}).get("imports", [])
        files = shard.get("files", [])
        # build shard summary
        recs = []
        for f in files:
            imps = [dict_imports[i] for i in f.get("imports", []) if 0 <= i < len(dict_imports)]
            sym = len(f.get("classes", [])) + len(f.get("functions", [])) + len(imps)
            recs.append({"path": f["path"], "lang": f.get("lang") or "unknown",
                         "classes": f.get("classes", []), "functions": f.get("functions", []),
                         "imports": imps, "symbol_count": sym})
        recs.sort(key=lambda r: (r["symbol_count"], r["path"].lower()), reverse=True)
        shard_summary = {"files": recs[:int(max_files_per_shard)],
                         "files_total": len(files),
                         "langs": Counter([r["lang"] for r in recs]).most_common()}

        prompt = build_prompt_shard_guarded(
            owner_repo, source_url, lang_text, safe_shard_name,
            shard_summary, allowed_norm, forbidden_norm,
            readme_excerpt=readme_excerpt
        )

        xml = qgenie_generate(prompt)
        # Save partial for reuse
        partial_path = wiki_partial_output_path(cache_dir, safe_shard_name)
        ensure_dir(os.path.dirname(partial_path))
        with open(partial_path, "w", encoding="utf-8") as f:
            f.write(xml)
        saved_partial_paths.append(partial_path)
        partial_xmls.append(xml)

    # REDUCE
    partial_trees = [extract_partial(x) for x in partial_xmls]
    merged_root = merge_partials(partial_trees)
    final_xml = compose_final_wiki(owner_repo=owner_repo, description="Auto-generated wiki structure.", merged_root=merged_root)

    # PRUNE (strict)
    final_xml = _prune_and_renumber_wiki(final_xml, allowed_norm, set(all_paths))

    # REFINE with QGenie + README
    refine_prompt = build_final_refine_prompt(owner_repo, source_url, lang_text, final_xml, readme_excerpt=readme_excerpt)
    final_xml = qgenie_generate(refine_prompt)
    final_xml = validate_or_wrap_xml(final_xml, "wiki_structure")

    # === DEDUPLICATE PAGES AND SECTIONS ===
    final_xml = clean_final_wiki_duplicates(final_xml)

    # Save final wiki XML
    final_path = wiki_default_output_path(cache_dir)
    ensure_dir(os.path.dirname(final_path))
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(final_xml)

    return {
        "compact_graph_path": single_path,
        "readme_hints_path": hints_path,
        "shard_manifest_path": man_path,
        "saved_partial_paths": saved_partial_paths,
        "final_wiki_path": final_path,
        "final_wiki_xml": final_xml,
        "totals": totals,
        "cache_dir": cache_dir,
        "knowledge_graph_dir": kg_dir,
        "wiki_xml_dir": wiki_dir,
    }
# ===================== Example Usage =====================
# if __name__ == "__main__":
#     import argparse
#     parser = argparse.ArgumentParser(description="Build sharded wiki from GitHub repo")
#     parser.add_argument("--gh_url", help="GitHub repo URL")
#     parser.add_argument("--token", help="GitHub token", default=None)
#     parser.add_argument("--max_files", type=int, default=0)
#     parser.add_argument("--lang", default="English")
#     parser.add_argument("--model", default="Pro")
#     parser.add_argument("--max_files_per_shard", type=int, default=200)
#     parser.add_argument("--readme_max_chars", type=int, default=4000)
#     args = parser.parse_args()

#     result = build_sharded_wiki_from_github(
#         gh_url=args.gh_url,
#         token=args.token,
#         max_files=args.max_files,
#         lang_text=args.lang,
#         qgenie_model=args.model,
#         max_files_per_shard=args.max_files_per_shard,
#         readme_max_chars=args.readme_max_chars,
#     )
#     print("Final wiki XML saved at:", result["final_wiki_path"])
#     print(result["final_wiki_xml"])