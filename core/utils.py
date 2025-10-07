
"""
Common utility functions shared across the AI_BUZZ codebase.
 
This module contains frequently used utility functions for:
- File system operations
- GitHub repository operations  
- Text processing
- JSON/compression handling
- Language detection
- Date/time utilities
"""
 
import os
import re
import json
import gzip
import hashlib
import tempfile
import zipfile
import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
 
# ===================== Constants =====================
 
SKIP_DIRS = {
    ".git", "__pycache__", "venv", ".venv", "build", "dist", "node_modules",
    ".mypy_cache", ".pytest_cache", "target", "out", ".gradle", ".idea"
}
 
MAX_FILE_BYTES = 2 * 1024 * 1024  # 2MB per file safety limit
 
# Language extension mappings
PY_EXTS   = {".py"}
JS_TS_EXTS= {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
JAVA_EXTS = {".java"}
GO_EXTS   = {".go"}
C_EXTS    = {".c", ".h"}
CPP_EXTS  = {".cc", ".cpp", ".cxx", ".hpp", ".hh", ".hxx", ".c++", ".h++"}
RUST_EXTS = {".rs"}
RUBY_EXTS = {".rb"}
PHP_EXTS  = {".php"}
KT_EXTS   = {".kt", ".kts"}
 
# ===================== File System Utilities =====================
 
def ensure_dir(path: str) -> str:
    """Ensure directory exists, create if it doesn't."""
    os.makedirs(path, exist_ok=True)
    return path
 
def read_text(path: str) -> str:
    """Read text file with UTF-8 encoding."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
 
def write_text(path: str, text: str):
    """Write text to file, creating directory if needed."""
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
 
def read_text_file(path: str) -> Optional[str]:
    """Read text file with safety checks (size, binary content)."""
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
 
# ===================== Date/Time Utilities =====================
 
def now_iso() -> str:
    """Get current UTC time in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
 
# ===================== GitHub Repository Utilities =====================
 
def sanitize_repo_name(name: str) -> str:
    """Sanitize repository name for safe usage."""
    return re.sub(r"[^\w\-\.]+", "-", name).strip("-")
 
def parse_github_url(url: str) -> Dict[str, str]:
    """
    Parse GitHub URL into components.
    
    Supports:
    - https://github.com/<owner>/<repo>
    - https://github.com/<owner>/<repo>.git
    - https://github.com/<owner>/<repo>/tree/<branch>/<optional subpath>
    - https://github.com/<owner>/<repo>/blob/<branch>/<file>
    
    Returns: dict(owner, repo, branch, subpath, kind)
    """
    url = url.strip()
    url = re.sub(r"\.git$", "", url)
    m = re.match(r"^https?://github\.com/([^/]+)/([^/]+)(?:/(tree|blob)/([^/]+)(/.*)?)?$", url)
    if not m:
        raise ValueError("Unrecognized GitHub URL. Expect https://github.com/<owner>/<repo>[...]")
    owner, repo, kind, branch, subpath = m.groups()
    repo = sanitize_repo_name(repo)
    subpath = (subpath or "").lstrip("/")
    return {"owner": owner, "repo": repo, "branch": branch, "subpath": subpath, "kind": kind or "repo"}
 
def http_get_json(url: str, token: Optional[str] = None) -> Dict[str, Any]:
    """Make HTTP GET request and return JSON response."""
    headers = {"User-Agent": "ai-buzz-app"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers)
    with urlopen(req, timeout=30) as resp:
        return json.load(io.TextIOWrapper(resp, encoding="utf-8"))
 
def get_default_branch(owner: str, repo: str, token: Optional[str] = None) -> str:
    """Get default branch for a GitHub repository."""
    try:
        info = http_get_json(f"https://api.github.com/repos/{owner}/{repo}", token=token)
        if info.get("default_branch"):
            return info["default_branch"]
    except Exception:
        pass
    # Fallback to common branch names
    for candidate in ("main", "master"):
        if can_download_zip(owner, repo, candidate):
            return candidate
    return "main"
 
def can_download_zip(owner: str, repo: str, branch: str) -> bool:
    """Check if repository ZIP can be downloaded."""
    url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"
    try:
        req = Request(url, headers={"User-Agent": "ai-buzz-app"})
        with urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False
 
def download_repo_zip(owner: str, repo: str, branch: str) -> bytes:
    """Download repository as ZIP bytes."""
    url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"
    req = Request(url, headers={"User-Agent": "ai-buzz-app"})
    with urlopen(req, timeout=60) as resp:
        return resp.read()
 
def unzip_to_temp(zip_bytes: bytes) -> str:
    """Extract ZIP bytes to temporary directory and return root path."""
    tmpdir = tempfile.mkdtemp(prefix="ghrepo_")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        zf.extractall(tmpdir)
    # Pick largest directory by file count
    entries = [os.path.join(tmpdir, d) for d in os.listdir(tmpdir)]
    dirs = [p for p in entries if os.path.isdir(p)]
    if not dirs:
        raise RuntimeError("Unexpected ZIP structure.")
    return max(dirs, key=lambda p: sum(len(files) for _, _, files in os.walk(p)))
 
def fingerprint(owner: str, repo: str, branch: str, subpath: Optional[str], url: str) -> str:
    """Generate unique fingerprint for repository configuration."""
    payload = f"{owner}/{repo}@{branch}:{subpath or ''}|{url}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]
 
# ===================== Language Detection =====================
 
def detect_lang(path: str) -> str:
    """Detect programming language from file extension."""
    ext = os.path.splitext(path)[1].lower()
    if ext in PY_EXTS: return "python"
    if ext in JS_TS_EXTS: return "javascript"
    if ext in JAVA_EXTS: return "java"
    if ext in GO_EXTS: return "go"
    if ext in C_EXTS or ext in CPP_EXTS: return "cpp" if ext in CPP_EXTS else "c"
    if ext in RUST_EXTS: return "rust"
    if ext in RUBY_EXTS: return "ruby"
    if ext in PHP_EXTS: return "php"
    if ext in KT_EXTS: return "kotlin"
    return "text"
 
def detect_lang_by_ext(ext: str) -> str:
    """Detect programming language from extension string."""
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
 
# ===================== JSON/Compression Utilities =====================
 
def load_json_autoz(path: str) -> Dict[str, Any]:
    """Load JSON file, automatically handling gzip compression."""
    if path.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
 
def save_json_gz(obj: dict, path: str):
    """Save object as gzipped JSON file."""
    ensure_dir(os.path.dirname(path))
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
 
# ===================== File Iteration Utilities =====================
 
def iter_repo_files(root_dir: str, subpath: Optional[str] = None, max_files: Optional[int] = None):
    """Iterate over repository files, skipping common ignore directories."""
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
 
# ===================== Path Utilities =====================
 
def infer_graph_id_from_wiki_path(wiki_path: str) -> str:
    """Infer graph ID from wiki XML file path."""
    # Expect: <owner>__<repo>__<branch>__<graphid>__wiki.xml
    base = os.path.basename(wiki_path or "")
    if base.endswith("__wiki.xml"):
        core = base[:-len("__wiki.xml")]
        parts = core.split("__")
        if len(parts) >= 4:
            return parts[-1]
    parent = os.path.basename(os.path.dirname(wiki_path or ""))
    return parent or "graph"
 
def parse_repo_from_wiki_path(wiki_path: str) -> tuple[str, str, str, str]:
    """Parse repository info from wiki XML file path."""
    base = os.path.basename(wiki_path or "")
    owner = repo = branch = ""
    graph_id = infer_graph_id_from_wiki_path(wiki_path)
    if base.endswith("__wiki.xml"):
        core = base[:-len("__wiki.xml")]
        parts = core.split("__")
        if len(parts) >= 4:
            owner, repo, branch = parts[0], parts[1], parts[2]
    return owner, repo, branch, graph_id
 
 