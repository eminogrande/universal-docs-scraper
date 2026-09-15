#!/usr/bin/env python3
"""
LLM Exporter: Crawl a documentation site and emit a single `llm.txt` file.

Pipeline
- Discover links (nav + internal anchors + sitemap) restricted to the same host
  and, by default, the path prefix of the start URL.
- Extract main content from each page and convert to clean Markdown using
  markdownify (preserve headings, lists, code blocks, tables, links, images).
- Rewrite relative URLs (href/src) to absolute. Optionally download images.
- Concatenate all pages into one file with a ToC and source URLs.

Usage
  python universal-docs-scraper/llm_export.py \
    --url https://docs.example.com/intro \
    --out llm.txt --max-pages 500 --depth 5

Notes
- This script avoids AI enhancement; its goal is faithful capture for LLMs.
- Requires: requests, beautifulsoup4, markdownify, lxml.
"""

from __future__ import annotations

import argparse
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin, urlparse


CONTENT_SELECTORS = [
    'main', 'article', '.content', '#content', '.documentation',
    '.markdown-body', '.doc-content', '.page-content', '[role="main"]',
    '[data-page-mode]', 'div[class*="prose"]', 'article[class*="prose"]',
    'section[class*="content"]', 'div[id*="content"]'
]

NAV_SELECTORS = [
    'nav', 'aside', '.sidebar', '[aria-label="Sidebar"]',
    'header', 'footer', '.toc', '[data-toc]'
]

SKIP_LINK_PATTERNS = [
    r'\.pdf$', r'\.zip$', r'\.gz$', r'\.tar$', r'\.dmg$', r'\.exe$',
    r'\.svg$', r'\.png$', r'\.jpg$', r'\.jpeg$', r'\.gif$', r'\.ico$',
    r'mailto:', r'javascript:', r'tel:', r'#', r'\?download='
]

DOC_LINK_HINTS = [
    '/docs', '/doc', '/api', '/guide', '/reference', '/manual', '/wiki',
    '/help', '/faq', '/getting-started', '/quickstart', '/examples',
    '/concepts', '/architecture', '/spec', '/sdk', '/developer'
]


@dataclass
class Page:
    url: str
    title: str
    markdown: str


class LLMExporter:
    def __init__(self, max_pages: int = 500, max_depth: int = 5, rate_limit: float = 0.3, site_wide: bool = False, en_only: bool = False):
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.rate_limit = rate_limit
        self.site_wide = site_wide
        self.en_only = en_only
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; LLMExporter/1.0)'
        })
        self.visited: Set[str] = set()

    def same_origin(self, a: str, b: str) -> bool:
        pa, pb = urlparse(a), urlparse(b)
        return (pa.scheme, pa.netloc) == (pb.scheme, pb.netloc)

    def base_prefix(self, url: str) -> str:
        p = urlparse(url)
        # Use first path segment as a guard (e.g., /wallet from /wallet/introduction)
        seg = (p.path.strip('/') + '/').split('/', 1)[0]
        return '/' + seg if seg else '/'

    def should_follow(self, href: str, start_url: str, path_prefix_only: bool = True) -> bool:
        if not href:
            return False
        full = urljoin(start_url, href)
        if not self.same_origin(full, start_url):
            return False
        # Language filter: exclude common non-English locale segments
        if self.en_only:
            p = urlparse(full).path.lower()
            non_en = (
                '/cn/', '/zh/', '/zh-cn/', '/zh-hans/', '/zh-hant/', '/de/', '/fr/', '/es/', '/pt/', '/ja/', '/ko/', '/ru/', '/it/', '/tr/', '/ar/', '/hi/', '/id/'
            )
            if any(seg in p for seg in non_en):
                return False
        for pat in SKIP_LINK_PATTERNS:
            if re.search(pat, full, flags=re.IGNORECASE):
                return False
        if not path_prefix_only or self.site_wide:
            return True
        # Constrain to base path prefix to avoid whole-site crawl
        pref = self.base_prefix(start_url)
        return urlparse(full).path.startswith(pref)

    def discover_links(self, start_url: str) -> List[str]:
        # BFS across internal links; seed with sitemap and start page
        seen: Set[str] = set()
        queue: List[Tuple[str, int]] = [(start_url, 0)]
        results: List[str] = []

        # Add sitemap URLs when available
        try:
            robots = urljoin(start_url, '/robots.txt')
            rr = self.session.get(robots, timeout=10)
            if rr.status_code == 200:
                for line in rr.text.splitlines():
                    if line.lower().startswith('sitemap:'):
                        sm = line.split(':', 1)[1].strip()
                        results.extend(self._parse_sitemap(sm, start_url))
        except Exception:
            pass

        while queue and len(results) < self.max_pages:
            url, depth = queue.pop(0)
            if url in seen or depth > self.max_depth:
                continue
            seen.add(url)
            try:
                r = self.session.get(url, timeout=15)
                if 'html' not in r.headers.get('content-type', '').lower():
                    continue
                soup = BeautifulSoup(r.text, 'html.parser')

                # Prefer navigation containers to harvest the site’s doc tree
                candidates = []
                for sel in NAV_SELECTORS:
                    candidates.extend(soup.select(sel))
                if not candidates:
                    candidates = [soup]

                for node in candidates:
                    for a in node.find_all('a', href=True):
                        href = a['href']
                        full = urljoin(url, href)
                        if self.should_follow(full, start_url):
                            if full not in results:
                                results.append(full)
                                if depth < self.max_depth:
                                    queue.append((full, depth + 1))
                time.sleep(self.rate_limit)
            except Exception:
                continue

        # Soft-rank: keep unique, prefer doc-like paths first
        uniq: List[str] = []
        seen = set()
        def score(u: str) -> Tuple[int, int]:
            p = urlparse(u).path.lower()
            hit = any(h in p for h in DOC_LINK_HINTS)
            return (0 if hit else 1, len(p))
        for u in sorted(set(results), key=score):
            if u not in seen:
                uniq.append(u)
                seen.add(u)
        return uniq[: self.max_pages]

    def _parse_sitemap(self, sitemap_url: str, start_url: str) -> List[str]:
        out: List[str] = []
        try:
            r = self.session.get(sitemap_url, timeout=10)
            if r.status_code != 200:
                return out
            import xml.etree.ElementTree as ET
            root = ET.fromstring(r.content)
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = root.findall('.//ns:url', ns)
            if not urls:
                # sitemap index
                for sm in root.findall('.//ns:sitemap', ns):
                    loc = sm.find('ns:loc', ns)
                    if loc is not None and loc.text:
                        out.extend(self._parse_sitemap(loc.text.strip(), start_url))
            else:
                for u in urls:
                    loc = u.find('ns:loc', ns)
                    if loc is not None and loc.text:
                        full = loc.text.strip()
                        if self.same_origin(full, start_url) and self.should_follow(full, start_url):
                            out.append(full)
        except Exception:
            pass
        return out

    def extract_markdown(self, url: str) -> Page:
        r = self.session.get(url, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        # Title
        title = (soup.find('h1') or soup.find('title'))
        page_title = title.get_text(strip=True) if title else urlparse(url).path.strip('/') or 'index'

        # Find main content
        root = None
        for sel in CONTENT_SELECTORS:
            root = soup.select_one(sel)
            if root:
                break
        if root is None:
            root = soup.find('body') or soup

        # Remove navigation + scripts/styles
        for sel in NAV_SELECTORS + ['script', 'style']:
            for el in root.select(sel):
                el.decompose()

        # Rewrite links and images to absolute
        for a in root.find_all('a', href=True):
            a['href'] = urljoin(url, a['href'])
        for img in root.find_all('img', src=True):
            img['src'] = urljoin(url, img['src'])

        html = str(root)
        # Convert to Markdown with careful options
        markdown = md(
            html,
            heading_style='ATX',
            bullets='-',
            code_language=False,
            strip=['video', 'audio']
        )

        # Normalize whitespace; collapse boilerplate
        markdown = self._clean_markdown(markdown)
        return Page(url=url, title=page_title, markdown=markdown)

    def _clean_markdown(self, s: str) -> str:
        lines = []
        noisy = (
            'Ask AI', 'On this page', 'Powered by', 'Copy', 'Share', 'Edit this page'
        )
        for line in s.splitlines():
            t = line.rstrip()
            if any(tok in t for tok in noisy):
                continue
            lines.append(t)
        # Collapse triple blank lines
        out: List[str] = []
        blanks = 0
        for t in lines:
            if t.strip() == '':
                blanks += 1
                if blanks <= 2:
                    out.append('')
            else:
                blanks = 0
                out.append(t)
        return '\n'.join(out).strip() + '\n'

    def export(self, start_url: str, out_path: str, max_pages: Optional[int] = None, llms_out: Optional[str] = None) -> Tuple[str, List[str]]:
        max_pages = max_pages or self.max_pages
        links = self.discover_links(start_url)
        links = [u for u in links if self.should_follow(u, start_url)]
        links = [start_url] + [u for u in links if u != start_url]
        links = links[:max_pages]

        pages: List[Page] = []
        for i, u in enumerate(links, 1):
            try:
                pages.append(self.extract_markdown(u))
            except Exception as e:
                pages.append(Page(url=u, title=urlparse(u).path.strip('/') or 'index', markdown=f"_Failed to fetch: {e}_\n"))
            time.sleep(self.rate_limit)

        # Assemble llm.txt
        out = []
        host = urlparse(start_url).netloc
        out.append(f"# LLM Knowledge Pack for {host}\n")
        out.append(f"Start URL: {start_url}\n")
        out.append(f"Total pages: {len(pages)}\n")
        out.append("\n## Links\n")
        for u in links:
            out.append(f"- {u}")
        out.append("\n---\n\n## Pages\n")
        for p in pages:
            anchor = p.title.lower().replace(' ', '-').replace('/', '-')
            out.append(f"\n### {p.title}\n")
            out.append(f"Source: {p.url}\n\n")
            out.append(p.markdown)
        text = '\n'.join(out).rstrip() + '\n'

        Path(out_path).write_text(text, encoding='utf-8')

        # Optionally emit llms.txt manifest
        if llms_out:
            self._emit_llms_txt(llms_out, start_url, pages)

        return out_path, links

    def _emit_llms_txt(self, path: str, start_url: str, pages: List[Page]) -> None:
        host = urlparse(start_url).netloc
        title = pages[0].title if pages else host
        # Naive summary: first non-empty paragraph from first page
        summary = ''
        if pages:
            for line in pages[0].markdown.splitlines():
                t = line.strip()
                if t and not t.startswith('#') and not t.startswith('!['):
                    summary = t
                    break
        if not summary:
            summary = f"Auto-generated manifest of documentation links for {host}."

        # Group pages: API/Reference vs other docs
        docs: List[Tuple[str,str]] = []
        api: List[Tuple[str,str]] = []
        for p in pages:
            url = p.url
            title_line = p.title or url
            low = url.lower()
            if any(k in low for k in ('/api', '/reference', '/swagger', '/openapi')):
                api.append((title_line, url))
            else:
                docs.append((title_line, url))

        def fmt_section(name: str, items: List[Tuple[str,str]]) -> List[str]:
            out = []
            if items:
                out.append(f"\n## {name}\n")
                for t,u in items[:200]:
                    out.append(f"- [{t}]({u}): {host} {t}")
            return out

        lines: List[str] = []
        lines.append(f"# {title}\n")
        lines.append(f"> {summary}\n")
        lines.extend(fmt_section('Docs', docs))
        lines.extend(fmt_section('API Reference', api))
        Path(path).write_text('\n'.join(lines).strip() + '\n', encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description='Export docs into a single llm.txt file')
    ap.add_argument('--url', required=True, help='Starting documentation URL (e.g., a top-level page)')
    ap.add_argument('--out', default='llm.txt', help='Output file path')
    ap.add_argument('--links-out', default=None, help='Optional path to also write the discovered links list')
    ap.add_argument('--llms-out', default=None, help='Also emit an llms.txt formatted manifest to this path')
    ap.add_argument('--max-pages', type=int, default=500)
    ap.add_argument('--depth', type=int, default=5)
    ap.add_argument('--site-wide', action='store_true', help='Follow all same-origin links, not just the start path prefix')
    ap.add_argument('--en-only', action='store_true', help='Exclude common non-English language paths (e.g., /cn/, /zh/, /de/)')
    args = ap.parse_args()

    exp = LLMExporter(max_pages=args.max_pages, max_depth=args.depth, site_wide=args.site_wide, en_only=args.en_only)
    path, links = exp.export(args.url, args.out, max_pages=args.max_pages, llms_out=args.llms_out)
    print(f"Wrote {path} with {len(links)} links.")
    if args.links_out:
        Path(args.links_out).write_text("\n".join(links) + "\n", encoding='utf-8')
        print(f"Also wrote links to {args.links_out}")


if __name__ == '__main__':
    main()
