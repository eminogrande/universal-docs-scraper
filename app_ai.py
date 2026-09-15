#!/usr/bin/env python3
"""
AI-Enhanced Universal Documentation Scraper Web Interface
"""

from flask import Flask, render_template, request, jsonify, send_file, session
import os
import json
import threading
from pathlib import Path
from datetime import datetime
import secrets
import tempfile
from ai_enhanced_scraper import AIEnhancedDocScraper
from urllib.parse import urlparse
from github_repo_scraper import GitHubRepoScraper

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Store scraping sessions in memory
scraping_sessions = {}

@app.route('/favicon.ico')
def favicon():
    # Silence browser favicon requests
    return ('', 204)

@app.route('/')
def index():
    # Get API key from URL parameter if provided
    api_key = request.args.get('api_key')
    if not api_key:
        # Prefill with default OpenRouter key so users see free catalog by default
        api_key = os.getenv('OPENROUTER_DEFAULT_KEY', 'REDACTED-OPENROUTER-KEY')
    # Check which template to use
    ui_style = request.args.get('ui', 'github')  # Default to GitHub style
    if ui_style == 'github':
        return render_template('github_ui.html', api_key=api_key)
    else:
        return render_template('ai_scraper.html', api_key=api_key)

@app.route('/api/models')
def get_models():
    """Get full model list from OpenRouter and choose a sensible default.

    Behavior:
    - Always return ALL OpenRouter models (free + premium), using a default key
      to access the full catalog. If user provides their own key, it is used.
    - Mark free models based on id suffix ":free" or zero pricing.
    - Default selection: latest free model by release date if available, else latest overall.
    """
    user_api_key = (request.args.get('api_key') or '').strip()
    # Default key (user provided) to broaden access; safe fallback to provided literal
    default_key = os.getenv('OPENROUTER_DEFAULT_KEY', 'REDACTED-OPENROUTER-KEY').strip()
    effective_key = user_api_key or default_key

    scraper = AIEnhancedDocScraper(api_key=effective_key)
    # Primary attempt with effective key
    models = scraper.get_available_models(api_key=effective_key) or []
    # Fallback attempt without Authorization if too few came back
    if len(models) < 10:
        try:
            fallback = scraper.get_available_models(api_key=None) or []
            # merge by id
            by_id = {m.get('id'): m for m in models if m.get('id')}
            for m in fallback:
                mid = m.get('id')
                if mid and mid not in by_id:
                    by_id[mid] = m
            models = list(by_id.values())
        except Exception:
            pass

    def is_free(m: dict) -> bool:
        mid = (m.get('id') or '').lower()
        if ':free' in mid:
            return True
        pricing = m.get('pricing') or {}
        try:
            p = pricing.get('prompt') or pricing.get('input') or 0
            c = pricing.get('completion') or pricing.get('output') or 0
            return (float(p) == 0.0) and (float(c) == 0.0)
        except Exception:
            return False

    # annotate models with free flag for UI convenience
    for m in models:
        m['is_free'] = is_free(m)

    # Try to find a working free model using a quick health check with the provided key
    # Prefer known good IDs first, then other free models by context length
    preferred_free_ids = [
        'qwen/qwen3-coder:free',
        'deepseek/deepseek-chat-v3-0324:free',
        'google/gemini-2.0-flash-exp:free',
        'deepseek/deepseek-r1:free',
    ]

    # Build candidate list: preferred first if present, then remaining free by context_length desc
    by_id = {m.get('id'): m for m in models if m.get('id')}
    free_candidates = []
    for pid in preferred_free_ids:
        if pid in by_id and by_id[pid] not in free_candidates:
            free_candidates.append(by_id[pid])
    # append other free models
    others = [m for m in models if m.get('is_free') and m not in free_candidates]
    others.sort(key=lambda m: (m.get('context_length') or 0), reverse=True)
    free_candidates.extend(others)

    def quick_test(model_id: str, key: str) -> bool:
        try:
            import requests as _rq
            url = 'https://openrouter.ai/api/v1/chat/completions'
            headers = {
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'HTTP-Referer': 'https://github.com/yourusername/docscraper',
                'X-Title': 'DocScrape Model Probe'
            }
            payload = {
                'model': model_id,
                'messages': [
                    { 'role': 'system', 'content': 'Reply with the single word: OK' },
                    { 'role': 'user', 'content': 'Health check.' }
                ],
                'temperature': 0,
                'max_tokens': 3
            }
            resp = _rq.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                return True
            return False
        except Exception:
            return False

    working_default_id = None
    # Only attempt if we have a usable key
    if effective_key:
        # Test up to first 6 free candidates to keep latency reasonable
        for cand in free_candidates[:6]:
            mid = cand.get('id')
            if not mid:
                continue
            ok = quick_test(mid, effective_key)
            cand['tested_ok'] = bool(ok)
            if ok and not working_default_id:
                working_default_id = mid
        # mark others as not tested
        for m in models:
            if m.get('is_free') and 'tested_ok' not in m:
                m['tested_ok'] = False


    # Sort by (release date desc, context length desc)
    from datetime import datetime
    def parse_dt(m: dict):
        for k in ('release_date', 'released_at', 'created', 'created_at', 'last_updated'):
            v = m.get(k)
            if not v:
                continue
            sv = str(v)
            try:
                return datetime.fromisoformat(sv.replace('Z','+00:00'))
            except Exception:
                for fmt in ('%Y-%m-%d', '%Y/%m/%d'):
                    try:
                        return datetime.strptime(sv, fmt)
                    except Exception:
                        continue
        return datetime.min

    # Sort by: free first, then tested_ok, then date/context_length
    models.sort(key=lambda m: (
        0 if m.get('is_free') else 1,
        0 if m.get('tested_ok') else 1,
        parse_dt(m),
        m.get('context_length') or 0
    ), reverse=True)

    # Choose default: pin qwen/qwen3-coder:free if available; else working free; else first free; else first overall
    qwen_id = 'qwen/qwen3-coder:free'
    ids = {m.get('id'): True for m in models}
    default_model_id = None
    if qwen_id in ids:
        default_model_id = qwen_id
    elif working_default_id:
        default_model_id = working_default_id
    else:
        # Fallback to first free model by our sort
        for m in models:
            if m.get('is_free'):
                default_model_id = m.get('id')
                break
    if not default_model_id and models:
        default_model_id = models[0].get('id')

    return jsonify({
        'default_model_id': default_model_id,
        'models': models
    })

@app.route('/api/test_ai', methods=['POST'])
def test_ai():
    """Minimal round-trip to verify API key + provider are working.

    Expects JSON: { api_key, model, use_openrouter }
    Returns: { ok: bool, provider: 'openrouter'|'openai', status: int, sample?: str, error?: str }
    """
    try:
        data = request.json or {}
        api_key = (data.get('api_key') or '').strip()
        model = (data.get('model') or 'gpt-4-turbo-preview').strip()
        use_openrouter = True

        if not api_key:
            # Always 200 to avoid noisy console errors; UI reads ok=false
            return jsonify({ 'ok': False, 'error': 'Missing api_key', 'status': 400 })

        url = 'https://openrouter.ai/api/v1/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        # Optional metadata headers per OpenRouter best practices
        headers['HTTP-Referer'] = 'https://github.com/yourusername/docscraper'
        headers['X-Title'] = 'DocScrape Key Test'

        payload = {
            'model': model,
            'messages': [
                { 'role': 'system', 'content': 'Reply with the single word: OK' },
                { 'role': 'user', 'content': 'Health check.' }
            ],
            'temperature': 0,
            'max_tokens': 3
        }

        import requests as _rq
        resp = _rq.post(url, headers=headers, json=payload, timeout=20)
        status = resp.status_code
        if status == 200:
            try:
                content = resp.json()['choices'][0]['message']['content'].strip()
                return jsonify({
                    'ok': True,
                    'provider': 'openrouter',
                    'status': status,
                    'sample': content
                })
            except Exception:
                return jsonify({ 'ok': True, 'provider': 'openrouter' if use_openrouter else 'openai', 'status': status })
        else:
            # Bubble up error message if present
            try:
                err = resp.json()
            except Exception:
                err = resp.text
            return jsonify({
                'ok': False,
                'provider': 'openrouter',
                'status': status,
                'error': err
            })
    except Exception as e:
        return jsonify({ 'ok': False, 'status': 500, 'error': str(e) })

@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    """Start the scraping process"""
    data = request.json
    url = data.get('url')
    api_key = data.get('api_key')
    model = data.get('model', 'qwen/qwen-2.5-coder-32b-instruct:free')
    use_ai = data.get('use_ai', True)
    use_openrouter = True  # Always OpenRouter
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Create session ID
    session_id = secrets.token_urlsafe(16)
    
    # Create scraping session
    scraping_session = {
        'id': session_id,
        'status': 'running',
        'progress': 0,
        'url': url,
        'model': model,
        'use_ai': use_ai,
        'logs': [],
        'result': None,
        'error': None,
        'start_time': datetime.now().isoformat()
    }
    scraping_sessions[session_id] = scraping_session
    
    # Start scraping in background
    thread = threading.Thread(
        target=run_scraping,
        args=(session_id, url, api_key, model, use_ai, use_openrouter)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'session_id': session_id})

def run_scraping(session_id, url, api_key, model, use_ai, use_openrouter):
    """Run the scraping process in background"""
    session = scraping_sessions[session_id]
    
    try:
        # Update progress
        session['logs'].append(f"Starting scraping of {url}")
        session['progress'] = 10
        
        # Initialize scraper
        scraper = AIEnhancedDocScraper(
            api_key=api_key,
            model=model,
            use_openrouter=True
        )
        
        session['logs'].append(f"Detecting documentation type...")
        session['progress'] = 20
        
        # Detect documentation type
        doc_type = scraper.detect_documentation_type(url)
        session['logs'].append(f"Detected type: {doc_type}")
        session['progress'] = 30
        
        # Scrape content (docs site or GitHub repo)
        session['logs'].append("Scraping documentation...")
        if 'github.com' in url:
            try:
                session['logs'].append("Detected GitHub repository. Cloning and analyzing...")
                gh = GitHubRepoScraper(url)
                gh.clone()
                content = gh.scrape()
                session['logs'].append(f"Repo files analyzed: {content.get('repo',{}).get('files_count',0)}")
            except Exception as e:
                session['logs'].append(f"GitHub scrape failed: {e}. Falling back to generic web scrape.")
                content = scraper.scrape_generic(url)
        else:
            if doc_type == 'openapi':
                content = scraper.scrape_openapi(url)
            else:
                content = scraper.scrape_generic(url)
        
        session['logs'].append(f"Found {len(content.get('sections', {}))} sections")
        try:
            srcs = content.get('sources') or []
            session['logs'].append(f"Sources discovered: {len(srcs)}")
        except Exception:
            pass
        session['progress'] = 60
        
        # Build raw markdown (unaltered) before any AI step
        try:
            raw_doc = AIEnhancedDocScraper(api_key=None).format_as_markdown(content)
        except Exception:
            raw_doc = ''

        # Build diagrams (programmatic + optional AI from raw)
        session['logs'].append("Preparing diagrams from raw source...")
        diagrams = []
        try:
            g1 = scraper._build_openapi_tag_graph(content)
            if g1: diagrams.append(g1)
        except Exception:
            pass
        try:
            g2 = scraper._build_openapi_class_diagram(content)
            if g2: diagrams.append(g2)
        except Exception:
            pass
        try:
            g3 = scraper._build_auth_or_onboarding_sequence(content)
            if g3: diagrams.append(g3)
        except Exception:
            pass
        try:
            g4 = scraper._build_system_architecture_graph(content)
            if g4: diagrams.append(g4)
        except Exception:
            pass
        try:
            g5 = scraper._build_card_order_state_diagram(content)
            if g5: diagrams.append(g5)
        except Exception:
            pass
        try:
            g6 = scraper._build_withdrawal_sequence(content)
            if g6: diagrams.append(g6)
        except Exception:
            pass
        try:
            g7 = scraper._build_pse_secure_elements_sequence(content)
            if g7: diagrams.append(g7)
        except Exception:
            pass
        try:
            g8 = scraper._build_iban_integration_sequence(content)
            if g8: diagrams.append(g8)
        except Exception:
            pass
        if not diagrams:
            try:
                dm = scraper._build_docs_map_mermaid(content)
                if dm: diagrams.append(dm)
            except Exception:
                pass

        if use_ai and api_key:
            session['logs'].append(f"Generating diagrams with AI using {model}...")
            try:
                extra = scraper._generate_rich_mermaid_from_raw(raw_doc)
                if extra:
                    diagrams.extend([c for c in extra if c])
                    session['logs'].append(f"AI diagram generation: OK ({len(extra)} added)")
                else:
                    session['logs'].append("AI diagram generation: no output")
            except Exception as e:
                session['logs'].append(f"AI diagram generation error: {e}")

        session['progress'] = 85
        
        # Save to temp file with descriptive name
        temp_dir = Path(tempfile.gettempdir()) / 'doc_scraper'
        temp_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        parsed = urlparse(url)
        host_slug = parsed.netloc.replace('.', '_').replace(':', '_') or 'docs'
        path_part = parsed.path.strip('/').split('/')[:1]
        path_slug = (path_part[0].replace('-', '_').replace('.', '_') if path_part and path_part[0] else 'index')
        base = f"{host_slug}__{path_slug}__{timestamp}"
        # Paths
        raw_filename = f"{base}__RAW.md"
        raw_filepath = temp_dir / raw_filename
        enhanced_filename = f"{base}__AI.md"
        enhanced_filepath = temp_dir / enhanced_filename
        
        # Log basic diagram diagnostics
        try:
            session['logs'].append(f"Diagrams prepared: {len(diagrams)}")
        except Exception:
            pass

        # Save raw doc
        try:
            with open(raw_filepath, 'w', encoding='utf-8') as rf:
                rf.write(raw_doc)
            session['logs'].append(f"Raw markdown saved: {raw_filename}")
        except Exception as e:
            session['logs'].append(f"Failed to save raw markdown: {e}")

        # Create charts-only markdown
        charts_filename = f"{base}__CHARTS.md"
        charts_filepath = temp_dir / charts_filename
        try:
            charts_parts = [f"# Architecture & Flow Diagrams\n\nGenerated: {datetime.now().isoformat()}\n"]
            count = 0
            for i, m in enumerate(diagrams[:50], 1):
                if not m:
                    continue
                charts_parts.append(f"\n## Diagram {i}\n\n```mermaid\n{m.strip()}\n```\n")
                count += 1
            with open(charts_filepath, 'w', encoding='utf-8') as cf:
                cf.write('\n'.join(charts_parts))
            session['logs'].append(f"Charts markdown saved: {charts_filename} ({count} diagrams)")
        except Exception as e:
            charts_filename = None
            charts_filepath = None
            session['logs'].append(f"Charts markdown skipped: {e}")

        # Result payload (keep legacy fields for compatibility)
        session['result'] = {
            'filename': raw_filename,
            'filepath': str(raw_filepath),
            'raw_filename': raw_filename,
            'raw_filepath': str(raw_filepath),
            'enhanced_filename': None,
            'enhanced_filepath': None,
            'charts_filename': charts_filename,
            'charts_filepath': str(charts_filepath) if charts_filepath else None,
            'size': len(raw_doc),
            'sections': len(content.get('sections', {})),
            'diagrams': diagrams[:10]
        }
        session['progress'] = 100
        session['status'] = 'completed'
        session['end_time'] = datetime.now().isoformat()
        
    except Exception as e:
        session['error'] = str(e)
        session['logs'].append(f"Error: {e}")
        session['status'] = 'failed'
        session['progress'] = 100

@app.route('/api/status/<session_id>')
def get_status(session_id):
    """Get the status of a scraping session"""
    if session_id not in scraping_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = scraping_sessions[session_id]
    return jsonify({
        'status': session['status'],
        'progress': session['progress'],
        'logs': session['logs'],
        'result': session['result'],
        'error': session['error']
    })

@app.route('/api/download/<session_id>')
def download_result(session_id):
    """Download the scraped documentation"""
    if session_id not in scraping_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = scraping_sessions[session_id]
    if session['status'] != 'completed' or not session['result']:
        return jsonify({'error': 'No result available'}), 400
    
    res = session['result']
    filepath = res.get('enhanced_filepath') or res.get('filepath')
    filename = res.get('enhanced_filename') or res.get('filename')
    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype='text/markdown'
    )

@app.route('/api/download_raw/<session_id>')
def download_raw(session_id):
    if session_id not in scraping_sessions:
        return jsonify({'error': 'Session not found'}), 404
    res = scraping_sessions[session_id].get('result') or {}
    fp = res.get('raw_filepath')
    fn = res.get('raw_filename')
    if not fp or not os.path.exists(fp):
        return jsonify({'error': 'Raw file not found'}), 404
    return send_file(fp, as_attachment=True, download_name=fn, mimetype='text/markdown')

@app.route('/api/download_enhanced/<session_id>')
def download_enhanced(session_id):
    if session_id not in scraping_sessions:
        return jsonify({'error': 'Session not found'}), 404
    res = scraping_sessions[session_id].get('result') or {}
    fp = res.get('enhanced_filepath')
    fn = res.get('enhanced_filename')
    if not fp or not os.path.exists(fp):
        return jsonify({'error': 'Enhanced file not found'}), 404
    return send_file(fp, as_attachment=True, download_name=fn, mimetype='text/markdown')

@app.route('/api/download_charts/<session_id>')
def download_charts(session_id):
    if session_id not in scraping_sessions:
        return jsonify({'error': 'Session not found'}), 404
    res = scraping_sessions[session_id].get('result') or {}
    fp = res.get('charts_filepath')
    fn = res.get('charts_filename')
    if not fp or not os.path.exists(fp):
        return jsonify({'error': 'Charts file not found'}), 404
    return send_file(fp, as_attachment=True, download_name=fn, mimetype='text/markdown')

@app.route('/api/diagrams/<session_id>')
def get_diagrams(session_id):
    if session_id not in scraping_sessions:
        return jsonify({'error': 'Session not found'}), 404
    session = scraping_sessions[session_id]
    res = session.get('result') or {}
    return jsonify({'diagrams': res.get('diagrams', [])})

@app.route('/api/regenerate-diagrams/<session_id>', methods=['POST'])
def regenerate_diagrams(session_id):
    """Regenerate diagrams using structured extraction approach."""
    if session_id not in scraping_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = scraping_sessions[session_id]
    res = session.get('result') or {}
    raw_content = res.get('raw_content', '')
    
    if not raw_content:
        return jsonify({'error': 'No content available for diagram generation'}), 400
    
    data = request.get_json() or {}
    api_key = data.get('api_key', '')
    model = data.get('model', 'openai/gpt-4o-mini')
    
    if not api_key:
        return jsonify({'error': 'API key required'}), 400
    
    try:
        scraper = AIEnhancedDocScraper(api_key=api_key, model=model)
        
        # First extract structure
        structure = scraper.extract_documentation_structure(raw_content, model)
        
        if not structure:
            # Fallback to raw generation
            diagrams = scraper._generate_rich_mermaid_from_raw(raw_content)
        else:
            # Generate smart diagrams from structure
            diagrams = scraper.generate_smart_diagrams(structure, model)
        
        # Store the new diagrams
        res['diagrams'] = diagrams
        session['result'] = res
        
        return jsonify({
            'success': True,
            'diagrams': diagrams,
            'structure': structure
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host='0.0.0.0', port=port, debug=debug_mode, threaded=True)
