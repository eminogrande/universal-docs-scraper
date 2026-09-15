#!/usr/bin/env python3
"""
Run multiple scraping strategies and summarize outputs for comparison.

Strategies
- AIEnhancedDocScraper (no AI): faithful, text-first markdown.
- AIEnhancedDocScraper (with AI): if API key present.
- DeepDocumentationScraper: structured crawl rendered to LLM-friendly markdown.
- LLMExporter: HTML→Markdown preservation with absolute links/images in one llm.txt.

Outputs
- Creates a timestamped directory and writes artifacts plus summary.json.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import sys
from pathlib import Path as _Path
_here = _Path(__file__).resolve().parent.parent
if str(_here) not in sys.path:
    sys.path.insert(0, str(_here))

from ai_enhanced_scraper import AIEnhancedDocScraper
from deep_scraper import DeepDocumentationScraper
from llm_export import LLMExporter


def safe_filename(url: str) -> str:
    p = urlparse(url)
    host = p.netloc.replace('.', '_').replace(':', '_') or 'docs'
    seg = (p.path.strip('/') or 'index').split('/')[0].replace('-', '_')
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{host}__{seg}__{ts}"


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description='Compare scraping strategies')
    ap.add_argument('--url', required=True)
    ap.add_argument('--outdir', default=None)
    ap.add_argument('--max-pages', type=int, default=300)
    ap.add_argument('--depth', type=int, default=5)
    ap.add_argument('--api-key', default=os.getenv('OPENROUTER_DEFAULT_KEY') or os.getenv('OPENAI_API_KEY'))
    ap.add_argument('--model', default='qwen/qwen3-coder:free')
    args = ap.parse_args()

    base = args.outdir or (Path.cwd() / 'experiments_out' / safe_filename(args.url))
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)

    summary = {
        'url': args.url,
        'outdir': str(base),
        'artifacts': {},
    }

    # 1) LLMExporter (single llm.txt + links)
    try:
        exp = LLMExporter(max_pages=args.max_pages, max_depth=args.depth, site_wide=True, en_only=True)
        llm_path = base / 'llm.txt'
        links_path = base / 'links.txt'
        out_path, links = exp.export(args.url, str(llm_path), max_pages=args.max_pages, llms_out=str(base / 'llms.txt'))
        write_text(links_path, '\n'.join(links) + '\n')
        summary['artifacts']['llm_export'] = {
            'file': str(llm_path),
            'llms_txt': str(base / 'llms.txt'),
            'links': str(links_path),
            'link_count': len(links),
            'size_bytes': llm_path.stat().st_size if llm_path.exists() else 0,
        }
    except Exception as e:
        summary['artifacts']['llm_export'] = {'error': str(e)}

    # 2) AIEnhancedDocScraper (no AI)
    try:
        aie = AIEnhancedDocScraper(api_key=None, model=args.model)
        out_md = base / 'standard_markdown.md'
        content = aie.scrape_generic(args.url)
        write_text(out_md, aie.format_as_markdown(content))
        summary['artifacts']['ai_enhanced_no_ai'] = {
            'file': str(out_md),
            'sections': len(content.get('sections', {})),
            'size_bytes': out_md.stat().st_size if out_md.exists() else 0,
        }
    except Exception as e:
        summary['artifacts']['ai_enhanced_no_ai'] = {'error': str(e)}

    # 3) AIEnhancedDocScraper (with AI) if key present
    if args.api_key:
        try:
            aie_ai = AIEnhancedDocScraper(api_key=args.api_key, model=args.model)
            out_ai = base / 'ai_enhanced.md'
            content_ai = aie_ai.scrape_generic(args.url)
            enhanced = aie_ai.enhance_with_ai(content_ai)
            write_text(out_ai, enhanced)
            summary['artifacts']['ai_enhanced_ai'] = {
                'file': str(out_ai),
                'sections': len(content_ai.get('sections', {})),
                'size_bytes': out_ai.stat().st_size if out_ai.exists() else 0,
            }
        except Exception as e:
            summary['artifacts']['ai_enhanced_ai'] = {'error': str(e)}
    else:
        summary['artifacts']['ai_enhanced_ai'] = {'skipped': 'no API key'}

    # 4) DeepDocumentationScraper
    try:
        deep = DeepDocumentationScraper(max_depth=args.depth, max_pages=args.max_pages)
        results = deep.scrape_documentation(args.url)
        out_deep = base / 'deep_scrape.md'
        write_text(out_deep, deep.format_for_llm(results))
        summary['artifacts']['deep_scraper'] = {
            'file': str(out_deep),
            'pages': results.get('total_pages', 0),
            'endpoints_found': len(results.get('api_summary', {})),
            'size_bytes': out_deep.stat().st_size if out_deep.exists() else 0,
        }
    except Exception as e:
        summary['artifacts']['deep_scraper'] = {'error': str(e)}

    # Save summary
    (base / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
