#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, List, Tuple


class GitHubRepoScraper:
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.clone_dir = None
        self.work_dir = None  # optional subpath inside repo when URL points to tree/blob

    def clone(self) -> str:
        tmpdir = tempfile.mkdtemp(prefix="repo_")
        clone_url, branch, subpath = self._normalize_github_url(self.repo_url)
        cmd = ["git", "clone", "--depth=1"]
        if branch:
            cmd += ["--branch", branch]
        cmd += [clone_url, tmpdir]
        try:
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            shutil.rmtree(tmpdir, ignore_errors=True)
            raise
        self.clone_dir = tmpdir
        # Set working directory if a subpath was specified in the URL
        if subpath:
            wd = Path(tmpdir) / subpath
            if wd.exists() and wd.is_dir():
                self.work_dir = str(wd)
            else:
                self.work_dir = str(Path(tmpdir))
        else:
            self.work_dir = str(Path(tmpdir))
        return tmpdir

    def scrape(self, max_files: int = 1000) -> Dict:
        if not self.clone_dir:
            self.clone()
        base = Path(self.work_dir or self.clone_dir)
        files = self._list_files(base, max_files)
        readmes = [p for p in files if p.name.lower().startswith("readme")]
        docs_dirs = [p for p in base.glob("**/") if p.name.lower() in ("docs", "documentation", "doc", "wiki")]
        # Collect docs text
        sections: Dict[str, str] = {}
        for r in readmes[:5]:
            sections[str(r.relative_to(base))] = self._read_text(r)
        for d in docs_dirs[:3]:
            for md in d.glob("**/*.md"):
                if len(sections) >= 60:
                    break
                sections[str(md.relative_to(base))] = self._read_text(md)
        # Code analysis
        endpoints, endpoint_graph = self._find_endpoints(files, base)
        classes = self._find_classes(files, base)
        imports_graph = self._build_import_graph(files, base)
        tree_graph = self._build_tree_graph(files, base)

        repo_name = self._repo_name_from_url(self.repo_url)
        content: Dict = {
            'title': f"Repository: {repo_name}",
            'description': f'Scraped from {self.repo_url}',
            'doc_type': 'github_repo',
            'sections': sections,
            'repo': {
                'files_count': len(files),
                'readmes': [str(r.relative_to(base)) for r in readmes[:5]],
                'docs_dirs': [str(d.relative_to(base)) for d in docs_dirs[:3]],
                'endpoints': endpoints,
                'classes': classes,
            },
            # programmatic graphs for enhancer to append
            'repo_tree_graph': tree_graph,
            'repo_dep_graph': imports_graph,
            'repo_endpoint_graph': endpoint_graph,
        }
        return content

    def _normalize_github_url(self, url: str) -> Tuple[str, str, str]:
        """Return (clone_url, branch, subpath) for a GitHub URL.

        Supports URLs like:
        - https://github.com/owner/repo
        - https://github.com/owner/repo/
        - https://github.com/owner/repo/tree/branch
        - https://github.com/owner/repo/tree/branch/path/to/dir
        - https://github.com/owner/repo/blob/branch/path/to/file
        """
        try:
            parsed = urlparse(url)
            parts = [p for p in parsed.path.split('/') if p]
            # Expect parts[0]=owner, parts[1]=repo
            if len(parts) < 2:
                return url, '', ''
            owner, repo = parts[0], parts[1]
            # strip .git from repo if present in path
            repo = repo[:-4] if repo.endswith('.git') else repo
            clone_url = f"https://github.com/{owner}/{repo}.git"
            branch = ''
            subpath = ''
            if len(parts) >= 4 and parts[2] in ('tree', 'blob'):
                branch = parts[3]
                if len(parts) > 4:
                    subpath = '/'.join(parts[4:])
                    # for blob, drop filename to nearest directory root
                    if parts[2] == 'blob' and '/' in subpath:
                        subpath = '/'.join(subpath.split('/')[:-1])
            return clone_url, branch, subpath
        except Exception:
            return url, '', ''

    def _repo_name_from_url(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            parts = [p for p in parsed.path.split('/') if p]
            if len(parts) >= 2:
                return parts[1]
            return url.rstrip('/').split('/')[-1]
        except Exception:
            return url.rstrip('/').split('/')[-1]

    def _list_files(self, base: Path, max_files: int) -> List[Path]:
        exts = {'.py', '.ts', '.tsx', '.js', '.jsx', '.go', '.rb', '.java', '.kt', '.rs', '.md', '.yaml', '.yml'}
        files: List[Path] = []
        for p in base.rglob('*'):
            if p.is_file() and p.suffix.lower() in exts and '.git' not in p.parts:
                files.append(p)
                if len(files) >= max_files:
                    break
        return files

    def _read_text(self, path: Path, limit: int = 200000) -> str:
        try:
            txt = path.read_text(encoding='utf-8', errors='ignore')
            if len(txt) > limit:
                return txt[:limit] + "\n... (truncated)"
            return txt
        except Exception:
            return ''

    def _find_endpoints(self, files: List[Path], base: Path) -> Tuple[List[Dict], str]:
        endpoints = []
        edges = []
        route_patterns = [
            ('.py', re.compile(r"@app\.route\(['\"]([^'\"]+)")),
            ('.py', re.compile(r"app\.(get|post|put|delete)\(['\"]([^'\"]+)")),
            ('.py', re.compile(r"FastAPI\(|APIRouter\(|app\.(get|post|put|delete)\(")),
            ('.js', re.compile(r"\b(app|router)\.(get|post|put|delete)\(['\"]([^'\"]+)")),
            ('.ts', re.compile(r"\b(app|router)\.(get|post|put|delete)\(['\"]([^'\"]+)")),
        ]
        for f in files:
            rel = str(f.relative_to(base))
            try:
                for i, line in enumerate(f.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
                    for ext, pat in route_patterns:
                        if f.suffix.lower() == ext or (ext == '.py' and f.suffix.lower() == '.py'):
                            m = pat.search(line)
                            if m:
                                path = m.group(1) if m.lastindex and len(m.groups()) >= 1 else None
                                if path and isinstance(path, str):
                                    endpoints.append({'file': rel, 'line': i, 'path': path})
                                    edges.append((self._safe_id(rel), self._safe_id(path)))
            except Exception:
                continue
        # build endpoint graph
        g = ["graph TB", "Code[(Codebase)]"]
        seen = set()
        for fnode, ep in edges[:200]:
            if fnode not in seen:
                g.append(f"Code --> {fnode}")
                seen.add(fnode)
            g.append(f"{fnode} --> {ep}")
        return endpoints, "\n".join(g)

    def _find_classes(self, files: List[Path], base: Path) -> List[Dict]:
        classes = []
        class_pat = re.compile(r"^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\s*[:(]", re.M)
        for f in files:
            if f.suffix.lower() != '.py':
                continue
            try:
                text = f.read_text(encoding='utf-8', errors='ignore')
                for m in class_pat.finditer(text):
                    name = m.group(1)
                    line = text[:m.start()].count('\n') + 1
                    classes.append({'file': str(f.relative_to(base)), 'line': line, 'class': name})
            except Exception:
                continue
        return classes[:300]

    def _build_import_graph(self, files: List[Path], base: Path) -> str:
        edges = []
        py_imp = re.compile(r"^\s*(from\s+([\w\.]+)\s+import|import\s+([\w\.]+))")
        js_imp = re.compile(r"^\s*import\s+.*?from\s+['\"]([^'\"]+)['\"]|^\s*require\(['\"]([^'\"]+)['\"]\)")
        for f in files:
            rel = str(f.relative_to(base))
            try:
                text = f.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            if f.suffix.lower() == '.py':
                for line in text.splitlines():
                    m = py_imp.match(line)
                    if m:
                        mod = (m.group(2) or m.group(3) or '').split('.')[0]
                        if mod:
                            edges.append((self._safe_id(rel), self._safe_id(mod)))
            elif f.suffix.lower() in ('.js', '.jsx', '.ts', '.tsx'):
                for line in text.splitlines():
                    m = js_imp.match(line)
                    if m:
                        mod = m.group(1) or m.group(2)
                        if mod and not mod.startswith('.'):
                            edges.append((self._safe_id(rel), self._safe_id(mod)))
        g = ["graph LR", "Code[(Codebase)]"]
        seen = set()
        for a, b in edges[:400]:
            if a not in seen:
                g.append(f"Code --> {a}")
                seen.add(a)
            g.append(f"{a} --> {b}")
        return "\n".join(g)

    def _build_tree_graph(self, files: List[Path], base: Path) -> str:
        g = ["graph TB", "ROOT[Repo]"]
        added = set()
        for f in files[:400]:
            parts = f.relative_to(base).parts
            parent = 'ROOT'
            path_acc = ''
            for part in parts:
                path_acc = f"{path_acc}/{part}" if path_acc else part
                node = self._safe_id(path_acc)
                label = part
                if node not in added:
                    g.append(f"{parent} --> {node}[\"{label}\"]")
                    added.add(node)
                parent = node
        return "\n".join(g)

    def _safe_id(self, name: str) -> str:
        return re.sub(r'[^a-zA-Z0-9_]', '_', name) or 'N'
