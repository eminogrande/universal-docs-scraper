#!/usr/bin/env python3
"""
AI-Enhanced Universal Documentation Scraper
Scrapes any documentation and uses AI to optimize it for LLM agents
"""

import json
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
import hashlib
from typing import List, Dict, Optional, Tuple, Any
import os

class AIEnhancedDocScraper:
    def __init__(self, api_key: Optional[str] = None, model: str = "qwen/qwen-2.5-coder-32b-instruct:free", use_openrouter: bool = True):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        # Always use OpenRouter
        self.use_openrouter = True
        self.scraped_content = {}
        self.visited_urls = set()
        self.base_url = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; DocScraper/1.0; +https://github.com/yourusername/docscraper)'
        })
        # Track sitemap metadata (url -> lastmod)
        self.sitemap_meta: Dict[str, str] = {}
        
    def get_available_models(self, api_key: Optional[str] = None) -> List[Dict]:
        """Fetch available models from OpenRouter.

        Optionally include an API key to access full catalog; endpoint is
        generally public but headers are harmless and sometimes helpful.
        """
        try:
            headers = {
                # OpenRouter prefers a referer/title header
                "HTTP-Referer": "https://docscrape.emino.app",
                "X-Title": "DocScrape Model Fetch",
            }
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            response = requests.get('https://openrouter.ai/api/v1/models', headers=headers, timeout=20)
            if response.status_code == 200:
                models = response.json().get('data', [])
                # Sort by context length and capabilities
                return sorted(models, key=lambda x: x.get('context_length', 0) or 0, reverse=True)
            return []
        except Exception as e:
            print(f"Error fetching OpenRouter models: {e}")
            return []
    
    def detect_documentation_type(self, url: str) -> str:
        """Detect the type of documentation (OpenAPI, GitBook, Docusaurus, Mintlify, etc.)"""
        response = self.session.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for OpenAPI/Swagger
        if '/swagger' in url or '/openapi' in url or '/docs/swagger.json' in response.text:
            return 'openapi'
        
        # Check for GitBook
        if soup.find('meta', {'name': 'generator', 'content': lambda x: x and 'gitbook' in x.lower()}):
            return 'gitbook'
        
        # Check for Docusaurus
        if soup.find('meta', {'name': 'generator', 'content': lambda x: x and 'docusaurus' in x.lower()}):
            return 'docusaurus'
        
        # Check for ReadMe
        if 'readme.io' in url or soup.find('div', class_='readme'):
            return 'readme'

        # Check for Mintlify
        gen = soup.find('meta', {'name': 'generator'})
        if gen and (gen.get('content') or '').strip().lower() == 'mintlify':
            return 'mintlify'

        # Check for MkDocs
        if soup.find('meta', {'name': 'generator', 'content': lambda x: x and 'mkdocs' in x.lower()}):
            return 'mkdocs'
        
        # Check for Sphinx
        if soup.find('div', class_='sphinxsidebar'):
            return 'sphinx'
        
        return 'generic'
    
    def scrape_openapi(self, base_url: str) -> Dict:
        """Scrape OpenAPI/Swagger documentation"""
        # Try common swagger.json locations
        swagger_urls = [
            urljoin(base_url, '/swagger.json'),
            urljoin(base_url, '/docs/swagger.json'),
            urljoin(base_url, '/api/swagger.json'),
            urljoin(base_url, '/v1/swagger.json'),
            urljoin(base_url, '/openapi.json'),
            urljoin(base_url, '/api-docs'),
        ]
        
        for swagger_url in swagger_urls:
            try:
                response = self.session.get(swagger_url)
                if response.status_code == 200:
                    try:
                        spec = response.json()
                        return self.parse_openapi_spec(spec)
                    except json.JSONDecodeError:
                        continue
            except:
                continue
        
        # If no swagger.json found, scrape the HTML
        return self.scrape_generic(base_url)
    
    def parse_openapi_spec(self, spec: Dict) -> Dict:
        """Parse OpenAPI specification into structured content"""
        content = {
            'title': spec.get('info', {}).get('title', 'API Documentation'),
            'version': spec.get('info', {}).get('version', ''),
            'description': spec.get('info', {}).get('description', ''),
            'base_url': spec.get('servers', [{}])[0].get('url', '') if spec.get('servers') else '',
            'sections': {},
            'doc_type': 'openapi'
        }
        # Include schemas for diagram generation
        content['schemas'] = spec.get('components', {}).get('schemas', {}) if spec.get('components') else {}
        
        # Group endpoints by tags
        paths = spec.get('paths', {})
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    tags = operation.get('tags', ['General'])
                    for tag in tags:
                        if tag not in content['sections']:
                            content['sections'][tag] = []
                        
                        endpoint_data = {
                            'path': path,
                            'method': method.upper(),
                            'summary': operation.get('summary', ''),
                            'description': operation.get('description', ''),
                            'parameters': operation.get('parameters', []),
                            'requestBody': operation.get('requestBody', {}),
                            'responses': operation.get('responses', {})
                        }
                        content['sections'][tag].append(endpoint_data)
        
        return content
    
    def scrape_generic(self, start_url: str) -> Dict:
        """Generic scraper for any documentation site"""
        self.base_url = start_url
        self.visited_urls = set()
        content = {
            'title': 'Documentation',
            'sections': {},
            'sources': []
        }
        
        # Start crawling from the base URL
        self._crawl_page(start_url, content)

        # If crawl yields too little, try sitemap-driven aggregation using a readability proxy fallback
        total_chars = sum(len(v or '') for v in content['sections'].values())
        if len(content['sections']) < 5 or total_chars < 2000:
            print("Low content discovered via crawl; attempting sitemap-based aggregation...")
            try:
                urls = self.get_sitemap_urls(start_url)
                print(f"Sitemap URLs discovered: {len(urls)}")
                for u in urls[:100]:  # cap to keep things responsive
                    if u in self.visited_urls:
                        continue
                    text = self._fetch_readable_text(u)
                    if text and len(text.strip()) > 50:
                        section_name = urlparse(u).path.strip('/') or 'index'
                        content['sections'][section_name] = text
                        content['sources'].append({
                            'url': u,
                            'lastmod': self.sitemap_meta.get(u)
                        })
                        self.visited_urls.add(u)
                        time.sleep(0.2)
            except Exception as e:
                print(f"Sitemap aggregation failed: {e}")

        return content
    
    def _crawl_page(self, url: str, content: Dict, max_depth: int = 3, current_depth: int = 0):
        """Recursively crawl documentation pages"""
        if current_depth >= max_depth or url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract main content
            main_content = self._extract_main_content(soup)
            if main_content:
                # Generate section name from URL or title
                title = soup.find('h1')
                section_name = title.text.strip() if title else urlparse(url).path.strip('/')
                content['sections'][section_name] = main_content
                # Track source without lastmod
                if not any(s.get('url') == url for s in content.get('sources', [])):
                    content.setdefault('sources', []).append({'url': url, 'lastmod': None})
            
            # Find and crawl linked documentation pages
            if current_depth < max_depth - 1:
                links = self._find_documentation_links(soup, url)
                for link in links[:20]:  # Limit to prevent infinite crawling
                    time.sleep(0.5)  # Rate limiting
                    self._crawl_page(link, content, max_depth, current_depth + 1)
                    
        except Exception as e:
            print(f"Error crawling {url}: {e}")
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract the main content from a page"""
        # Common content containers
        content_selectors = [
            'main', 'article', '.content', '#content', '.documentation',
            '.markdown-body', '.doc-content', '.page-content', '[role="main"]'
        ]
        # Additional selectors for modern doc generators (e.g., Mintlify)
        content_selectors.extend([
            '[data-page-mode]',
            'div[class*="prose"]',
            'article[class*="prose"]',
            'section[class*="content"]',
            'div[id*="content"]',
        ])
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                # Remove navigation, ads, etc.
                for element in content.select('nav, aside, .sidebar, .ads, script, style'):
                    element.decompose()
                text = content.get_text(separator='\n', strip=True)
                return self._clean_text(text)
        
        # Fallback to body content
        body = soup.find('body')
        if body:
            for element in body.select('nav, aside, header, footer, script, style'):
                element.decompose()
            text = body.get_text(separator='\n', strip=True)
            return self._clean_text(text)

        return ""

    def _clean_text(self, text: str) -> str:
        """Remove common UI noise and compress whitespace."""
        try:
            lines = []
            noisy = (
                'Copy page', 'Ask AI', 'Powered by Mintlify',
                'Search...', '⌘', 'On this page', 'home page', 'Navigation',
                'Responses are generated using AI and may contain mistakes.',
                'Assistant', 'website', 'github'
            )
            for line in text.splitlines():
                s = line.strip()
                if not s:
                    lines.append('')
                    continue
                if any(token in s for token in noisy):
                    continue
                if s.lower() in ('copy', 'k'):
                    continue
                if s.startswith('Copy'):
                    continue
                lines.append(s)
            # collapse multiple blanks
            out = []
            blank = False
            for s in lines:
                if s == '':
                    if not blank:
                        out.append(s)
                    blank = True
                else:
                    out.append(s)
                    blank = False
            return '\n'.join(out).strip()
        except Exception:
            return text

    def _fetch_readable_text(self, url: str) -> str:
        """Fetch readable text for JS-heavy sites.

        Attempts a readability proxy (r.jina.ai) first, then falls back to
        basic extraction if needed.
        """
        try:
            parsed = urlparse(url)
            proxy_url = f"https://r.jina.ai/http://{parsed.netloc}{parsed.path}"
            r = self.session.get(proxy_url, timeout=20)
            if r.status_code == 200 and len(r.text.strip()) > 100:
                return self._clean_text(r.text)
        except Exception as e:
            print(f"Readability proxy failed for {url}: {e}")
        # Fallback basic fetch
        try:
            resp = self.session.get(url, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            text = self._extract_main_content(soup)
            if text:
                return self._clean_text(text)
        except Exception as e:
            print(f"Basic fetch failed for {url}: {e}")
        return ""

    def parse_sitemap(self, sitemap_url: str) -> List[str]:
        urls: List[str] = []
        try:
            r = self.session.get(sitemap_url, timeout=10)
            if r.status_code != 200:
                return urls
            import xml.etree.ElementTree as ET
            root = ET.fromstring(r.content)
            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            # If it's a sitemap index
            sitemaps = root.findall('.//ns:sitemap', ns)
            if sitemaps:
                for sm in sitemaps:
                    loc = sm.find('ns:loc', ns)
                    if loc is not None and loc.text:
                        urls.extend(self.parse_sitemap(loc.text.strip()))
            else:
                for url_elem in root.findall('.//ns:url', ns):
                    loc = url_elem.find('ns:loc', ns)
                    if loc is not None and loc.text:
                        u = loc.text.strip()
                        urls.append(u)
                        lastmod = url_elem.find('ns:lastmod', ns)
                        if lastmod is not None and lastmod.text:
                            self.sitemap_meta[u] = lastmod.text.strip()
        except Exception as e:
            print(f"Failed to parse sitemap {sitemap_url}: {e}")
        return urls

    def get_sitemap_urls(self, base: str) -> List[str]:
        base = base.rstrip('/')
        urls: List[str] = []
        # From robots.txt
        try:
            robots = urljoin(base, '/robots.txt')
            rr = self.session.get(robots, timeout=10)
            if rr.status_code == 200:
                for line in rr.text.splitlines():
                    if line.lower().startswith('sitemap:'):
                        sm = line.split(':', 1)[1].strip()
                        urls.extend(self.parse_sitemap(sm))
        except Exception as e:
            print(f"robots.txt fetch failed: {e}")
        # Common sitemap locations
        for loc in ['/sitemap.xml', '/sitemap_index.xml', '/sitemap-index.xml']:
            urls.extend(self.parse_sitemap(urljoin(base, loc)))
        # Filter same domain and dedupe
        dom = urlparse(base).netloc
        urls = [u for u in urls if urlparse(u).netloc == dom]
        seen = set()
        uniq = []
        for u in urls:
            if u not in seen:
                uniq.append(u)
                seen.add(u)
        return uniq
    
    def _find_documentation_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Find links to other documentation pages"""
        links = []
        base_domain = urlparse(current_url).netloc
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(current_url, href)
            
            # Only follow links on the same domain
            if urlparse(full_url).netloc == base_domain:
                # Filter for likely documentation links
                if any(keyword in full_url.lower() for keyword in ['docs', 'api', 'guide', 'reference', 'tutorial']):
                    if full_url not in self.visited_urls:
                        links.append(full_url)
        
        return list(set(links))
    
    def enhance_with_ai(self, content: Dict, progress_cb=None, max_chunks: int = 6, max_seconds: int = 240) -> str:
        """Use AI to enhance and optimize documentation for AI agents.

        Fallback behavior: If the AI requests fail or return no content, return
        the standard formatted markdown so users still get a usable document.
        """
        if not self.api_key:
            print("No API key provided, skipping AI enhancement")
            return self.format_as_markdown(content)
        
        # Prepare the content for AI processing
        raw_text = self.format_as_markdown(content)
        
        # Split into chunks if too large
        chunks = self._split_into_chunks(raw_text, 10000)
        total_chunks = len(chunks)
        if total_chunks > max_chunks:
            chunks = chunks[:max_chunks]
        enhanced_sections = []
        start_time = time.time()
        
        for i, chunk in enumerate(chunks):
            if time.time() - start_time > max_seconds:
                if progress_cb:
                    progress_cb({'event': 'ai_timeout', 'processed': i, 'total': total_chunks})
                break
            try:
                if progress_cb:
                    progress_cb({'event': 'ai_chunk_start', 'index': i+1, 'total': len(chunks)})
                print(f"Processing chunk {i+1}/{len(chunks)} with AI...")
                enhanced = self._process_with_ai(chunk)
                if enhanced:
                    enhanced_sections.append(enhanced)
                    if progress_cb:
                        progress_cb({'event': 'ai_chunk_done', 'index': i+1, 'total': len(chunks), 'ok': True})
                else:
                    if progress_cb:
                        progress_cb({'event': 'ai_chunk_done', 'index': i+1, 'total': len(chunks), 'ok': False})
            except Exception as e:
                if progress_cb:
                    progress_cb({'event': 'ai_chunk_error', 'index': i+1, 'total': len(chunks), 'error': str(e)})
            time.sleep(0.5)  # gentle rate limiting

        # If nothing came back from AI, fall back to standard markdown
        if not enhanced_sections:
            print("AI enhancement returned no content; falling back to standard markdown.")
            return self.format_as_markdown(content)

        # Combine all enhanced sections
        final_doc = self._combine_enhanced_sections(enhanced_sections, content.get('title', 'Documentation'))

        # If the AI wrapped the output in a markdown code block, strip it
        def _strip_fence(txt: str) -> str:
            t = txt.strip()
            if t.startswith('```') and t.endswith('```'):
                # remove first and last fenced lines
                lines = t.splitlines()
                # drop first and last
                if len(lines) >= 2:
                    return '\n'.join(lines[1:-1]).strip()
            return txt

        final_doc = _strip_fence(final_doc)

        # Pass 1: attempt to auto-fix mermaid fences with AI until they validate (best-effort)
        try:
            final_doc = self._autofix_mermaid_blocks(final_doc)
        except Exception as e:
            print(f"Mermaid autofix failed: {e}")

        # Unfence ```markdown blocks but keep others (e.g., mermaid)
        try:
            import re
            def _unfence_markdown(m):
                return m.group(1)
            final_doc = re.sub(r"```markdown\s*([\s\S]*?)```", _unfence_markdown, final_doc, flags=re.MULTILINE)
        except Exception:
            pass

        # Programmatic, doc-specific diagrams
        try:
            openapi_graph = self._build_openapi_tag_graph(content)
            if openapi_graph:
                final_doc += "\n\n---\n\n## API Overview (Tags & Endpoints)\n\n" + "```mermaid\n" + openapi_graph + "\n```"
        except Exception as e:
            print(f"OpenAPI tag graph failed: {e}")
        try:
            openapi_classes = self._build_openapi_class_diagram(content)
            if openapi_classes:
                final_doc += "\n\n---\n\n## API Data Model (Schemas)\n\n" + "```mermaid\n" + openapi_classes + "\n```"
        except Exception as e:
            print(f"OpenAPI class diagram failed: {e}")
        try:
            auth_seq = self._build_auth_or_onboarding_sequence(content)
            if auth_seq:
                final_doc += "\n\n---\n\n## Authentication / Onboarding Flow\n\n" + "```mermaid\n" + auth_seq + "\n```"
        except Exception as e:
            print(f"Auth/onboarding sequence failed: {e}")

        # Additional, domain-specific diagrams
        try:
            arch = self._build_system_architecture_graph(content)
            if arch:
                final_doc += "\n\n---\n\n## System Architecture\n\n" + "```mermaid\n" + arch + "\n```"
        except Exception as e:
            print(f"Architecture graph failed: {e}")
        try:
            states = self._build_card_order_state_diagram(content)
            if states:
                final_doc += "\n\n---\n\n## Card Order State Machine\n\n" + "```mermaid\n" + states + "\n```"
        except Exception as e:
            print(f"Card order state diagram failed: {e}")
        try:
            wd = self._build_withdrawal_sequence(content)
            if wd:
                final_doc += "\n\n---\n\n## Withdrawal Flow\n\n" + "```mermaid\n" + wd + "\n```"
        except Exception as e:
            print(f"Withdrawal sequence failed: {e}")
        try:
            pse = self._build_pse_secure_elements_sequence(content)
            if pse:
                final_doc += "\n\n---\n\n## PSE Secure Elements Flow (mTLS + Ephemeral Token)\n\n" + "```mermaid\n" + pse + "\n```"
        except Exception as e:
            print(f"PSE sequence failed: {e}")
        try:
            iban = self._build_iban_integration_sequence(content)
            if iban:
                final_doc += "\n\n---\n\n## IBAN Integration Flow\n\n" + "```mermaid\n" + iban + "\n```"
        except Exception as e:
            print(f"IBAN sequence failed: {e}")
        try:
            wh = self._build_webhook_sequence(content)
            if wh:
                final_doc += "\n\n---\n\n## Webhook Delivery Flow\n\n" + "```mermaid\n" + wh + "\n```"
        except Exception as e:
            print(f"Webhook sequence failed: {e}")

        # Ensure at least some Mermaid content exists; append docs-map fallback if missing
        try:
            import re
            mermaid_blocks = re.findall(r"```mermaid[\s\S]*?```", final_doc)
            if len(mermaid_blocks) < 1:
                print("Mermaid diagrams missing; appending docs map fallback.")
                dm = self._build_docs_map_mermaid(content)
                if dm:
                    final_doc += ("\n\n---\n\n## Documentation Map (Auto-Added)\n\n"
                                  "```mermaid\n" + dm + "\n```")
            # If diagrams look sparse, ask AI to synthesize richer diagrams from RAW docs
            mermaid_blocks = re.findall(r"```mermaid\s*([\s\S]*?)```", final_doc)
            if len(mermaid_blocks) < 3:
                print("Generating additional diagrams from raw source...")
                extra = self._generate_rich_mermaid_from_raw(raw_text)
                if extra:
                    for code in extra[:3 - len(mermaid_blocks)]:
                        final_doc += "\n\n---\n\n## Additional Diagram (AI from Raw)\n\n```mermaid\n" + code.strip() + "\n```"
        except Exception:
            pass

        # Append Sources & Freshness if available
        sources = content.get('sources') or []
        if sources:
            final_doc += "\n\n---\n\n## Sources & Freshness\n\n"
            for s in sources[:200]:
                lm = s.get('lastmod') or 'unknown'
                final_doc += f"- [{s.get('url')}]({s.get('url')}) • lastmod: {lm}\n"
            if len(sources) > 200:
                final_doc += f"\n...and {len(sources)-200} more sources.\n"
            final_doc += "\n"

        # Append raw extracted content for completeness (collapsed)
        final_doc += ("\n\n---\n\n"
                      "<details>\n<summary><strong>Raw Extracted Content</strong> (expand)</summary>\n\n\n")
        final_doc += raw_text
        final_doc += "\n\n</details>\n"
        return final_doc

    def extract_documentation_structure(self, raw_text: str, model: str = None) -> Dict[str, Any]:
        """Extract structured information from raw documentation for better diagram generation."""
        try:
            use_model = model or self.model
            sys = (
                "You are a documentation analyzer. Extract structured information from documentation. "
                "Return JSON with the following structure:\n"
                "{\n"
                "  \"title\": \"Main title/product name\",\n"
                "  \"components\": [\"list of main system components\"],\n"
                "  \"apis\": [{\"method\": \"GET\", \"path\": \"/path\", \"purpose\": \"description\"}],\n"
                "  \"flows\": [{\"name\": \"flow name\", \"steps\": [\"step1\", \"step2\"]}],\n"
                "  \"integrations\": [\"external systems\"],\n"
                "  \"data_models\": [{\"name\": \"model\", \"fields\": [\"field1\", \"field2\"]}]\n"
                "}"
            )
            prompt = (
                "Extract the key architectural components and flows from this documentation:\n\n"
                + raw_text[:15000]
            )
            
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/yourusername/docscraper",
                "X-Title": "Structure Extraction",
                "Content-Type": "application/json"
            }
            data = {
                "model": use_model,
                "messages": [
                    {"role": "system", "content": sys},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            resp = requests.post(url, headers=headers, json=data, timeout=60)
            if resp.status_code != 200:
                return {}
            
            content = resp.json()["choices"][0]["message"]["content"].strip()
            # Try to parse JSON from response
            import json
            import re
            # Extract JSON if wrapped in markdown
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
            if json_match:
                content = json_match.group(1)
            return json.loads(content)
        except Exception as e:
            print(f"Structure extraction error: {e}")
            return {}

    def generate_smart_diagrams(self, structure: Dict[str, Any], model: str = None) -> List[str]:
        """Generate focused diagrams from extracted structure."""
        try:
            use_model = model or self.model
            diagrams = []
            
            # Architecture diagram
            if structure.get('components'):
                arch_prompt = (
                    "Create a Mermaid graph TD showing the architecture with these components:\n"
                    f"Components: {', '.join(structure['components'][:20])}\n"
                    f"Integrations: {', '.join(structure.get('integrations', [])[:10])}\n"
                    "Show how they connect. Use clean labels and --> arrows."
                )
                arch_diagram = self._generate_single_diagram(arch_prompt, use_model)
                if arch_diagram:
                    diagrams.append(arch_diagram)
            
            # Flow diagram
            if structure.get('flows'):
                flow = structure['flows'][0] if structure['flows'] else {}
                if flow.get('steps'):
                    flow_prompt = (
                        f"Create a Mermaid sequenceDiagram for '{flow.get('name', 'Main Flow')}':\n"
                        f"Steps: {' -> '.join(flow['steps'][:15])}\n"
                        "Include participants and interactions."
                    )
                    flow_diagram = self._generate_single_diagram(flow_prompt, use_model)
                    if flow_diagram:
                        diagrams.append(flow_diagram)
            
            # API diagram
            if structure.get('apis'):
                api_groups = {}
                for api in structure['apis'][:30]:
                    path_parts = api.get('path', '/').split('/')
                    group = path_parts[1] if len(path_parts) > 1 else 'root'
                    if group not in api_groups:
                        api_groups[group] = []
                    api_groups[group].append(f"{api.get('method', 'GET')} {api.get('path', '/')}")
                
                api_prompt = (
                    "Create a Mermaid graph showing API endpoints grouped by resource:\n"
                    + "\n".join([f"{k}: {', '.join(v[:5])}" for k, v in list(api_groups.items())[:10]])
                    + "\nUse a clean hierarchical structure."
                )
                api_diagram = self._generate_single_diagram(api_prompt, use_model)
                if api_diagram:
                    diagrams.append(api_diagram)
            
            return diagrams[:3]
        except Exception as e:
            print(f"Smart diagram generation error: {e}")
            return []
    
    def _generate_single_diagram(self, prompt: str, model: str) -> str:
        """Generate a single Mermaid diagram from a focused prompt."""
        try:
            sys = "Generate only valid Mermaid v11 code. No explanations, just the diagram code."
            
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/yourusername/docscraper",
                "X-Title": "Diagram Generation",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": sys},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 1000
            }
            
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            if resp.status_code != 200:
                return ""
            
            content = resp.json()["choices"][0]["message"]["content"].strip()
            # Clean up the response
            import re
            # Remove markdown fences if present
            content = re.sub(r'```(?:mermaid)?\s*([\s\S]*?)```', r'\1', content)
            return content.strip()
        except Exception as e:
            print(f"Single diagram generation error: {e}")
            return ""

    def _generate_rich_mermaid_from_raw(self, raw_text: str) -> List[str]:
        """Ask the model to produce rich, valid Mermaid diagrams directly from raw docs.

        Returns unfenced Mermaid code blocks (strings). Universal and brand-neutral.
        """
        try:
            sys = (
                "You generate only Mermaid code for diagrams. Return only code fences if present,"
                " but prefer returning just Mermaid code without fences. Use Mermaid v11 syntax."
            )
            prompt = (
                "You are a diagram generator. Based ONLY on the raw documentation below, produce up to three clear Mermaid diagrams that reflect the system accurately.\n"
                "Follow these rules:\n"
                "- Use generic labels unless the source explicitly names services (e.g., use 'API Server' not a brand).\n"
                "- Prefer: (1) Architecture graph TD, (2) One or two sequenceDiagram flows for core operations (auth, webhooks, CRUD, provisioning).\n"
                "- Diagrams must be valid in Mermaid v11.10.1. Use plain --> arrows.\n"
                "- Do NOT add prose. Return only Mermaid code for each diagram, separated by a blank line.\n\n"
                "RAW DOCUMENTATION START\n---\n" + raw_text[:20000] + "\n---\nRAW DOCUMENTATION END\n"
            )
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/yourusername/docscraper",
                "X-Title": "Mermaid From Raw",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": sys},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 2000
            }
            resp = requests.post(url, headers=headers, json=data, timeout=60)
            if resp.status_code != 200:
                try:
                    print(f"diagram gen error: {resp.status_code} - {resp.text}")
                except Exception:
                    pass
                return []
            out = resp.json()["choices"][0]["message"]["content"].strip()
            import re
            codes = []
            # Extract fenced mermaid first
            for m in re.findall(r"```mermaid\s*([\s\S]*?)```", out, re.MULTILINE):
                codes.append(m.strip())
            if not codes:
                # Split by two or more newlines to try to capture multiple diagrams
                chunks = re.split(r"\n\s*\n", out)
                # Filter chunks that look like valid mermaid directives
                directives = ("graph ", "flowchart", "sequenceDiagram", "classDiagram", "stateDiagram", "stateDiagram-v2", "erDiagram", "gantt", "pie")
                for c in chunks:
                    cs = c.strip()
                    if any(cs.startswith(d) for d in directives):
                        codes.append(cs)
            return codes[:3]
        except Exception as e:
            print(f"diagram gen exception: {e}")
            return []

    def _build_openapi_tag_graph(self, content: Dict) -> str:
        """Build a Mermaid graph of OpenAPI tags and their endpoints."""
        if content.get('doc_type') != 'openapi':
            return ""
        sections = content.get('sections') or {}
        if not sections:
            return ""
        lines = ["graph TB", "API[(API)]"]
        count = 0
        for tag, endpoints in sections.items():
            tid = self._safe_id(f"tag_{tag}")
            lines.append(f"API --> {tid}[\"{tag}\"]")
            for ep in endpoints[:20]:  # cap per tag
                eid = self._safe_id(f"{ep.get('method','GET')}_{ep.get('path','/')}".replace('/', '_'))
                label = f"{ep.get('method','GET')} {ep.get('path','/')}"
                if len(label) > 50:
                    label = label[:47] + '…'
                lines.append(f"{tid} --> {eid}[\"{label}\"]")
                count += 1
                if count >= 200:
                    break
            if count >= 200:
                break
        return "\n".join(lines)

    def _build_openapi_class_diagram(self, content: Dict) -> str:
        """Build a Mermaid classDiagram from OpenAPI component schemas (simplified)."""
        if content.get('doc_type') != 'openapi':
            return ""
        schemas = content.get('schemas') or {}
        if not schemas:
            return ""
        lines = ["classDiagram"]
        added = 0
        for name, schema in list(schemas.items())[:40]:
            cname = self._safe_id(name)
            lines.append(f"class {cname}")
            props = (schema or {}).get('properties') or {}
            for prop, meta in list(props.items())[:12]:
                ptype = meta.get('type') or meta.get('$ref', '').split('/')[-1] or 'any'
                lines.append(f"{cname} : {prop} {ptype}")
            added += 1
        return "\n".join(lines) if added else ""

    def _build_auth_or_onboarding_sequence(self, content: Dict) -> str:
        """Build a Mermaid sequenceDiagram for auth or onboarding based on detected endpoints in text."""
        # Gather potential endpoints from openapi sections
        endpoints = []
        if content.get('doc_type') == 'openapi':
            for tag_eps in (content.get('sections') or {}).values():
                for ep in tag_eps:
                    endpoints.append(f"{ep.get('method','GET')} {ep.get('path','/')}")
        else:
            # Regex scan of generic text
            import re
            text = self._gather_all_text(content)
            for m in re.finditer(r"\b(GET|POST|PUT|PATCH|DELETE)\s+(/[-a-zA-Z0-9_./{}:]+)", text):
                endpoints.append(f"{m.group(1)} {m.group(2)}")

        eps = set(endpoints)
        lines = ["sequenceDiagram", "autonumber", "participant C as Client", "participant API as API"]
        built = False
        # Authentication flow if common endpoints present
        if any('/auth/nonce' in e for e in eps) or any('nonce' in e and '/auth' in e for e in eps):
            lines += ["C->>API: GET /auth/nonce", "API-->>C: nonce"]
            built = True
        if any('/auth/challenge' in e for e in eps) or any('challenge' in e and '/auth' in e for e in eps):
            lines += ["C->>API: POST /auth/challenge (message, signature)", "API-->>C: JWT token"]
            built = True
        # Onboarding hints
        if any('/auth/signup' in e for e in eps) or any('/user/terms' in e for e in eps) or any('/kyc' in e for e in eps):
            lines += [
                "C->>API: POST /auth/signup (email, otp)",
                "API-->>C: user registered",
                "C->>API: GET /user/terms",
                "C->>API: POST /user/terms",
                "C->>API: GET /kyc/integration",
                "API-->>C: KYC URL/Token",
            ]
            built = True
        return "\n".join(lines) if built else ""

    def _gather_all_text(self, content: Dict) -> str:
        parts = []
        for k, v in (content.get('sections') or {}).items():
            if isinstance(v, list):
                for item in v:
                    # include summaries and descriptions if present
                    if isinstance(item, dict):
                        parts.append(item.get('summary', '') or '')
                        parts.append(item.get('description', '') or '')
            else:
                parts.append(str(v))
        return "\n".join(parts)

    def _build_system_architecture_graph(self, content: Dict) -> str:
        """Build a generic system architecture graph based on detected keywords (universal)."""
        text = self._gather_all_text(content).lower()
        if not text or len(text) < 200:
            return ""
        # Detect common components
        has_sdk = any(k in text for k in ('sdk', 'client library'))
        has_cli = 'cli' in text
        has_auth = any(k in text for k in ('oauth', 'jwt', 'siwe', 'api key', 'auth'))
        has_db = any(k in text for k in ('database', 'postgres', 'mysql', 'sqlite', 'mongodb', 'dynamodb'))
        has_queue = any(k in text for k in ('queue', 'kafka', 'rabbitmq', 'pub/sub', 'sns', 'sqs'))
        has_webhook = 'webhook' in text
        has_storage = any(k in text for k in ('s3', 'blob storage', 'object storage', 'gcs', 'minio'))
        has_blockchain = any(k in text for k in ('blockchain', 'smart contract', 'contract', 'on-chain', 'onchain'))
        has_third_party = any(k in text for k in ('monerium', 'sumsub', 'stripe', 'paypal', 'twilio', 'github', 'slack'))

        lines = ['graph TB']
        # Clients
        lines.append('U[User] --> APP[Application]')
        if has_sdk:
            lines.append('APP --> SDK[SDK / Client Library]')
            lines.append('SDK --> API{HTTP API}')
        elif has_cli:
            lines.append('APP --> CLI[CLI]')
            lines.append('CLI --> API{HTTP API}')
        else:
            lines.append('APP --> API{HTTP API}')
        # Core services
        if has_auth:
            lines.append('API --> AUTH[Auth Service]')
        if has_db:
            lines.append('API --> DB[(Database)]')
        if has_queue:
            lines.append('API --> Q[Queue/Broker]')
        if has_storage:
            lines.append('API --> ST[Object Storage]')
        if has_webhook:
            lines.append('API --> WH[Webhook Dispatcher]')
        if has_blockchain:
            lines.append('API --> CHAIN[(Blockchain)]')
        if has_third_party:
            lines.append('API --> EXT[Third-Party Services]')
            lines.append('classDef ext fill:#f8f9ff,stroke:#8aa,stroke-width:1px')
            lines.append('class EXT ext')
        return "\n".join(lines)

    def _build_card_order_state_diagram(self, content: Dict) -> str:
        """Build stateDiagram-v2 for Card Order State Transitions when hints are found."""
        text = self._gather_all_text(content)
        if 'card order state' not in text.lower():
            tokens = ('PENDINGTRANSACTION', 'TRANSACTIONCOMPLETE', 'CONFIRMATIONREQUIRED', 'READY', 'CARDCREATED')
            if not any(t in text for t in tokens):
                return ""
        lines = [
            'stateDiagram-v2',
            '[*] --> PENDINGTRANSACTION',
            'PENDINGTRANSACTION --> READY: Confirm payment / Free order',
            'PENDINGTRANSACTION --> TRANSACTIONCOMPLETE: Payment processed',
            'PENDINGTRANSACTION --> CANCELLED: Cancel order',
            'PENDINGTRANSACTION --> FAILEDTRANSACTION: Payment failed',
            'TRANSACTIONCOMPLETE --> CONFIRMATIONREQUIRED: Additional checks',
            'CONFIRMATIONREQUIRED --> READY: Verified (phone/SOF/address)',
            'READY --> CARDCREATED: Create card',
            'CARDCREATED --> [*]'
        ]
        return "\n".join(lines)

    def _build_withdrawal_sequence(self, content: Dict) -> str:
        text = self._gather_all_text(content).lower()
        if 'withdraw' not in text:
            return ""
        lines = [
            'sequenceDiagram',
            'participant C as Client',
            'participant API as API Server',
            'participant D as Delay Relay',
            'participant S as Safe Contracts',
            'participant G as Blockchain Network',
            'C->>API: GET /accounts/withdraw/transaction-data',
            'API-->>C: EIP-712 typed data',
            'C->>C: Sign typed data (EOA signer)',
            'C->>API: POST /accounts/withdraw {payload, signature}',
            'API->>D: Enqueue execution',
            'D-->>S: Execute after 3 min',
            'S-->>G: On-chain transfer',
            'API-->>C: Withdrawal submitted (id, status)'
        ]
        return "\n".join(lines)

    def _build_pse_secure_elements_sequence(self, content: Dict) -> str:
        text = self._gather_all_text(content).lower()
        if 'pse' not in text and 'secure elements' not in text:
            return ""
        lines = [
            'sequenceDiagram',
            'participant FE as Frontend',
            'participant BE as Backend',
            'participant PSE as Secure Elements API (mTLS)',
            'participant SDK as Secure Elements SDK (iframe)',
            'FE->>BE: Request ephemeral-token',
            'BE->>PSE: POST /ephemeral-token (mTLS)',
            'PSE-->>BE: { token, expiresAt }',
            'BE-->>FE: token',
            'FE->>SDK: init(token)',
            'SDK-->>FE: Secure card elements rendered'
        ]
        return "\n".join(lines)

    def _build_iban_integration_sequence(self, content: Dict) -> str:
        text = self._gather_all_text(content).lower()
        if 'iban' not in text:
            return ""
        lines = [
            'sequenceDiagram',
            'participant C as Client',
            'participant API as API Server',
            'participant MON as IBAN Provider',
            'C->>API: GET /ibans/available',
            'API-->>C: { available }',
            'C->>API: GET /ibans/signing-message',
            'API-->>C: message to sign',
            'C->>API: POST /ibans/monerium-profile { signature, callbackUrl }',
            'API->>MON: Create/Link profile',
            'alt Existing profile',
            '    API-->>C: 422 with redirectUrl',
            '    C->>MON: OAuth consent',
            'else New profile',
            '    MON-->>API: Provisioning',
            'end',
            'C->>API: GET /ibans/details (poll)',
            'API-->>C: { status: ASSIGNED, iban, bic }'
        ]
        return "\n".join(lines)

    def _build_webhook_sequence(self, content: Dict) -> str:
        text = self._gather_all_text(content).lower()
        if 'webhook' not in text:
            return ""
        lines = [
            'sequenceDiagram',
            'participant EVT as Event Source',
            'participant API as API',
            'participant WH as Webhook Dispatcher',
            'participant SUB as Subscriber Endpoint',
            'EVT-->>API: Business Event (create/update)',
            'API-->>WH: Enqueue delivery',
            'loop Retries with backoff'
            '    WH->>SUB: POST /webhook (HMAC-SHA256 signed)',
            '    alt 2xx'
            '        WH-->>API: Delivered'
            '    else non-2xx'
            '        WH-->>WH: Schedule retry'
            '    end',
            'end'
        ]
        return "\n".join(lines)

    def _build_docs_map_mermaid(self, content: Dict) -> str:
        """Generic docs map: derive a site map from sources or sections."""
        sources = content.get('sources') or []
        if not sources and not content.get('sections'):
            return ''
        lines = ['graph LR']
        try:
            if sources:
                from urllib.parse import urlparse
                root = None
                buckets = {}
                for s in sources[:200]:
                    u = s.get('url') or ''
                    if not u:
                        continue
                    p = urlparse(u)
                    host = p.netloc.replace('.', '_')
                    root = root or host
                    segs = [seg for seg in p.path.split('/') if seg]
                    if not segs:
                        label = 'index'
                    else:
                        label = segs[0]
                    buckets.setdefault(label, 0)
                    buckets[label] += 1
                lines.append(f'{root}["{root}"]')
                for k, cnt in list(buckets.items())[:40]:
                    nid = self._safe_id(k)
                    lines.append(f'{root} --> {nid}["{k} ({cnt})"]')
            else:
                # fallback to sections
                root = self._safe_id(content.get('title') or 'Docs')
                lines.append(f'{root}["{content.get("title","Docs")}"]')
                for name in list((content.get('sections') or {}).keys())[:50]:
                    nid = self._safe_id(name)
                    lines.append(f'{root} --> {nid}["{name}"]')
        except Exception:
            return ''
        return "\n".join(lines)

    def _safe_id(self, name: str) -> str:
        import re
        sid = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        if not sid:
            sid = 'N'
        return sid

    def _autofix_mermaid_blocks(self, doc: str) -> str:
        """Scan markdown for mermaid fenced blocks and use AI to fix syntax until sane.

        This does not execute mermaid; it enforces simple rules and asks the model
        to return corrected, v11-compatible code without fences. We run up to 2 passes per block.
        """
        import re
        pattern = re.compile(r"```mermaid\s*([\s\S]*?)```", re.MULTILINE)
        blocks = list(pattern.finditer(doc))
        if not blocks:
            return doc

        def sanitize(code: str) -> str:
            c = (code or '').strip().replace('\r', '')
            # normalize arrows and stray tokens
            c = re.sub(r"\s-\>\s", " --> ", c)
            # If directive missing, wrap as graph TD and comment original
            directives = ("graph ", "flowchart", "sequenceDiagram", "classDiagram", "stateDiagram", "stateDiagram-v2", "erDiagram", "gantt", "pie")
            if not any(c.startswith(d) for d in directives):
                commented = '\n'.join(["%% " + line for line in c.splitlines()])
                c = "graph TD\nA[Diagram]\n%% auto-sanitized\n" + commented
            return c

        def ai_fix(code: str) -> str:
            prompt = (
                "You are a Mermaid v11.10.1 syntax fixer.\n"
                "Given a Mermaid diagram, return ONLY corrected Mermaid code (no fences, no prose).\n"
                "Preserve intent and structure. Prefer graph TD / sequenceDiagram / classDiagram.\n"
                "Ensure it parses in Mermaid v11.10.1.\n\n"
                "Diagram to fix:\n---\n" + code + "\n---\n"
            )
            try:
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                headers["HTTP-Referer"] = "https://github.com/yourusername/docscraper"
                headers["X-Title"] = "Mermaid Fixer"
                data = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You return only valid Mermaid code."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.0,
                    "max_tokens": 1200
                }
                resp = requests.post(url, headers=headers, json=data, timeout=45)
                if resp.status_code == 200:
                    out = resp.json()["choices"][0]["message"]["content"].strip()
                    # strip fences if returned
                    if out.startswith("```"):
                        out = re.sub(r"^```\w*\s*", "", out).rstrip("`").strip()
                    return out
                else:
                    print(f"AI mermaid fix error: {resp.status_code} - {resp.text}")
            except Exception as e:
                print(f"AI mermaid fix exception: {e}")
            return code

        new_doc = doc
        offset = 0
        for m in blocks:
            raw = m.group(1)
            fixed = sanitize(raw)
            # up to 2 AI passes
            for _ in range(2):
                candidate = ai_fix(fixed)
                candidate = sanitize(candidate)
                fixed = candidate
            # replace in doc
            start, end = m.span(1)
            start += offset
            end += offset
            new_block = f"```mermaid\n{fixed}\n```"
            new_doc = new_doc[:m.start() + offset] + new_block + new_doc[m.end() + offset:]
            offset += len(new_block) - (m.end() - m.start())
        print("Mermaid blocks auto-fixed: ", len(blocks))
        return new_doc
    
    def _split_into_chunks(self, text: str, max_size: int = 10000) -> List[str]:
        """Split text into chunks for AI processing"""
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line)
            if current_size + line_size > max_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def _process_with_ai(self, text: str) -> Optional[str]:
        """Process documentation chunk with AI"""
        prompt = """You are an expert at optimizing API documentation for AI agents and LLMs. 

Transform the following documentation into a perfectly structured format that is optimal for AI agents to understand and use. 

Requirements:
1. Add clear section headers and organization
2. Include explicit examples for every endpoint/function
3. Add type hints and parameter descriptions
4. Include error handling information
5. Add context about relationships between different parts
6. Format code examples in multiple languages when relevant
7. Include authentication flow details
8. Add rate limiting and best practices
9. Make implicit information explicit
10. Add a quick reference section
11. Do NOT invent or hallucinate endpoints, parameters, or data. Only transform content present in the source. If information is missing, do not add generic TODOs; instead, omit or note "insufficient detail in source" in one line.
12. Include an "Architecture & Flows" section with rich Mermaid code blocks (```mermaid fences) suitable for Mermaid v11.10.1:
   - Architecture Overview: graph TD. Use only generic labels unless the source explicitly names services. Prefer neutral terms like "Application", "API Server", "Auth Service", "Database", "Queue/Broker", "Object Storage", "Webhook Dispatcher", "External Provider", "Blockchain".
   - Detailed API Sequences: sequenceDiagram(s) that mirror real flows detected in the source (e.g., authentication, webhooks, background jobs, CRUD flows). Only include brand/provider names if they appear in the source; otherwise use generic labels.
   - If entities are clear, add a classDiagram for core data structures.
15. IMPORTANT: Mermaid must be valid for Mermaid v11.10.1. Use plain --> arrows (no HTML entities). Do not wrap Mermaid in additional fences.
13. Use only information present in the source. Never introduce product/brand names (e.g., vendor names) that are not in the source. Prefer neutral labels when in doubt.
14. Keep the output compact and de-duplicated. Remove UI boilerplate like "Copy page", navigation, or site chrome.
15. Add a "Sources & Freshness" section linking to original pages.

Documentation to optimize:
---
{text}
---

Output the enhanced documentation in clean Markdown format optimized for AI agent consumption:"""

        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/yourusername/docscraper",
                "X-Title": "Documentation Scraper",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert at creating documentation for AI agents."},
                    {"role": "user", "content": prompt.format(text=text)}
                ],
                "temperature": 0.3,
                "max_tokens": 4000
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                try:
                    err = response.json()
                except Exception:
                    err = response.text
                print(f"AI API error: {response.status_code} - {err}")
                return None
                
        except Exception as e:
            print(f"Error processing with AI: {e}")
            return None
    
    def _combine_enhanced_sections(self, sections: List[str], title: str) -> str:
        """Combine AI-enhanced sections into final documentation"""
        doc = [f"# {title} - AI-Optimized Documentation for LLM Agents\n"]
        doc.append(f"Generated: {datetime.now().isoformat()}\n")
        doc.append("---\n\n")
        doc.append("## 🤖 AI Agent Quick Reference\n\n")
        doc.append("This documentation has been optimized for AI agents and LLMs with:\n")
        doc.append("- Clear structure and navigation\n")
        doc.append("- Explicit examples for every endpoint\n")
        doc.append("- Complete type information\n")
        doc.append("- Error handling patterns\n")
        doc.append("- Best practices and guidelines\n\n")
        doc.append("---\n\n")
        
        for section in sections:
            doc.append(section)
            doc.append("\n\n---\n\n")
        
        return '\n'.join(doc)
    
    def format_as_markdown(self, content: Dict) -> str:
        """Format scraped content as markdown without AI enhancement"""
        doc = []
        doc.append(f"# {content.get('title', 'Documentation')}\n")
        
        if content.get('version'):
            doc.append(f"**Version:** {content['version']}\n")
        
        if content.get('base_url'):
            doc.append(f"**Base URL:** {content['base_url']}\n")
        
        if content.get('description'):
            doc.append(f"\n{content['description']}\n")
        
        doc.append("\n## Table of Contents\n\n")
        for section in content.get('sections', {}).keys():
            doc.append(f"- [{section}](#{section.lower().replace(' ', '-')})\n")
        
        doc.append("\n---\n\n")
        
        for section_name, section_content in content.get('sections', {}).items():
            doc.append(f"## {section_name}\n\n")
            
            if isinstance(section_content, list):
                # API endpoints
                for endpoint in section_content:
                    doc.append(f"### {endpoint['method']} {endpoint['path']}\n\n")
                    if endpoint.get('summary'):
                        doc.append(f"**{endpoint['summary']}**\n\n")
                    if endpoint.get('description'):
                        doc.append(f"{endpoint['description']}\n\n")
                    
                    # Parameters
                    if endpoint.get('parameters'):
                        doc.append("**Parameters:**\n\n")
                        doc.append("| Name | Type | Required | Description |\n")
                        doc.append("|------|------|----------|-------------|\n")
                        for param in endpoint['parameters']:
                            name = param.get('name', '')
                            param_type = param.get('schema', {}).get('type', 'string')
                            required = '✓' if param.get('required', False) else ''
                            description = param.get('description', '')
                            doc.append(f"| {name} | {param_type} | {required} | {description} |\n")
                        doc.append("\n")
                    
                    doc.append("---\n\n")
            else:
                # Generic content
                doc.append(f"{section_content}\n\n")
        
        return '\n'.join(doc)
    
    def scrape_and_save(self, url: str, output_file: str = None, use_ai: bool = True) -> str:
        """Main method to scrape documentation and save to file"""
        print(f"🔍 Detecting documentation type for: {url}")
        doc_type = self.detect_documentation_type(url)
        print(f"📚 Detected type: {doc_type}")
        
        print(f"🕷️ Scraping documentation...")
        if doc_type == 'openapi':
            content = self.scrape_openapi(url)
        else:
            content = self.scrape_generic(url)
        
        print(f"📝 Found {len(content.get('sections', {}))} sections")
        
        if use_ai and self.api_key:
            print(f"🤖 Enhancing with AI using model: {self.model}")
            final_doc = self.enhance_with_ai(content)
        else:
            print(f"📄 Formatting as standard markdown")
            final_doc = self.format_as_markdown(content)
        
        # Save to file
        if not output_file:
            domain = urlparse(url).netloc.replace('.', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"{domain}_AI_ENHANCED_{timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_doc)
        
        print(f"✅ Documentation saved to: {output_file}")
        return output_file


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-Enhanced Documentation Scraper')
    parser.add_argument('url', help='Documentation URL to scrape')
    parser.add_argument('--api-key', help='OpenAI or OpenRouter API key')
    parser.add_argument('--model', default='qwen/qwen3-coder:free', help='AI model to use (OpenRouter id)')
    parser.add_argument('--output', help='Output file name')
    parser.add_argument('--no-ai', action='store_true', help='Skip AI enhancement')
    
    args = parser.parse_args()
    
    scraper = AIEnhancedDocScraper(
        api_key=args.api_key,
        model=args.model,
        use_openrouter=args.use_openrouter
    )
    
    scraper.scrape_and_save(
        url=args.url,
        output_file=args.output,
        use_ai=not args.no_ai
    )


if __name__ == "__main__":
    main()
