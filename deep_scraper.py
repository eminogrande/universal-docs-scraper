#!/usr/bin/env python3
"""
Deep Documentation Scraper with Advanced Link Following
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import hashlib
import time
import re
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path
import json

class DeepDocumentationScraper:
    def __init__(self, max_depth: int = 3, max_pages: int = 100, follow_external: bool = False):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.follow_external = follow_external
        self.visited_urls: Set[str] = set()
        self.content_hashes: Set[str] = set()
        self.scraped_content: List[Dict] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; DocScraper/1.0; +https://github.com/docscraper)'
        })
        
    def should_follow_link(self, url: str, base_domain: str) -> bool:
        """Determine if a link should be followed based on patterns and domain."""
        parsed = urlparse(url)
        
        # Skip non-HTTP protocols
        if parsed.scheme and parsed.scheme not in ['http', 'https']:
            return False
            
        # Skip common non-documentation patterns
        skip_patterns = [
            r'/signin', r'/login', r'/logout', r'/register',
            r'\.(jpg|jpeg|png|gif|svg|ico|pdf|zip|tar|gz)$',
            r'/download/', r'/cdn-cgi/', r'/wp-admin/',
            r'#$', r'javascript:', r'mailto:', r'tel:'
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, url.lower()):
                return False
        
        # Prioritize documentation patterns
        doc_patterns = [
            r'/docs/', r'/documentation/', r'/api/', r'/guide/',
            r'/tutorial/', r'/reference/', r'/manual/', r'/wiki/',
            r'/help/', r'/faq/', r'/getting-started/', r'/quickstart/',
            r'/examples/', r'/concepts/', r'/architecture/', r'/spec/'
        ]
        
        for pattern in doc_patterns:
            if re.search(pattern, url.lower()):
                return True
        
        # Check domain restrictions
        if not self.follow_external:
            url_domain = parsed.netloc or base_domain
            if url_domain != base_domain:
                return False
        
        return True
    
    def extract_structured_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract structured content from a page."""
        content = {
            'url': url,
            'title': '',
            'headings': [],
            'code_blocks': [],
            'api_endpoints': [],
            'paragraphs': [],
            'links': [],
            'tables': [],
            'lists': []
        }
        
        # Extract title
        title = soup.find('title')
        if title:
            content['title'] = title.get_text().strip()
        
        # Extract headings with hierarchy
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                content['headings'].append({
                    'level': i,
                    'text': heading.get_text().strip(),
                    'id': heading.get('id', '')
                })
        
        # Extract code blocks
        for code in soup.find_all(['code', 'pre']):
            code_text = code.get_text().strip()
            if len(code_text) > 10:  # Skip tiny snippets
                lang = code.get('class', [''])[0] if code.get('class') else ''
                if 'language-' in lang:
                    lang = lang.replace('language-', '')
                content['code_blocks'].append({
                    'language': lang,
                    'code': code_text
                })
        
        # Extract API endpoints from code and text
        api_pattern = r'(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+([/\w\-\{\}\.]+)'
        for match in re.finditer(api_pattern, soup.get_text()):
            content['api_endpoints'].append({
                'method': match.group(1),
                'path': match.group(2)
            })
        
        # Extract paragraphs (limit to meaningful ones)
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 50:  # Skip short paragraphs
                content['paragraphs'].append(text[:1000])  # Limit length
        
        # Extract tables
        for table in soup.find_all('table'):
            headers = [th.get_text().strip() for th in table.find_all('th')]
            rows = []
            for tr in table.find_all('tr'):
                cells = [td.get_text().strip() for td in tr.find_all('td')]
                if cells:
                    rows.append(cells)
            if headers or rows:
                content['tables'].append({
                    'headers': headers,
                    'rows': rows[:20]  # Limit rows
                })
        
        # Extract lists (ul/ol)
        for lst in soup.find_all(['ul', 'ol']):
            items = [li.get_text().strip() for li in lst.find_all('li', recursive=False)]
            if items:
                content['lists'].append(items[:20])  # Limit items
        
        # Extract links for further crawling
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text().strip()
            content['links'].append({
                'href': href,
                'text': text
            })
        
        return content
    
    def scrape_url(self, url: str, depth: int = 0) -> Optional[Dict]:
        """Scrape a single URL and extract content."""
        if url in self.visited_urls or depth > self.max_depth:
            return None
        
        if len(self.visited_urls) >= self.max_pages:
            return None
        
        self.visited_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'html' not in content_type:
                return None
            
            # Check for duplicate content
            content_hash = hashlib.md5(response.content).hexdigest()
            if content_hash in self.content_hashes:
                return None
            self.content_hashes.add(content_hash)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            content = self.extract_structured_content(soup, url)
            content['depth'] = depth
            
            return content
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def scrape_documentation(self, start_url: str, progress_callback=None) -> Dict:
        """Main method to scrape documentation starting from a URL."""
        parsed_start = urlparse(start_url)
        base_domain = parsed_start.netloc
        
        # Queue of URLs to visit with their depth
        queue = [(start_url, 0)]
        results = {
            'base_url': start_url,
            'domain': base_domain,
            'pages': [],
            'api_summary': {},
            'structure': {},
            'total_pages': 0
        }
        
        while queue and len(self.visited_urls) < self.max_pages:
            current_url, depth = queue.pop(0)
            
            if current_url in self.visited_urls:
                continue
            
            if progress_callback:
                progress = min(95, int((len(self.visited_urls) / self.max_pages) * 100))
                progress_callback(progress, f"Scraping: {current_url[:80]}...")
            
            content = self.scrape_url(current_url, depth)
            
            if content:
                results['pages'].append(content)
                
                # Add discovered links to queue
                if depth < self.max_depth:
                    for link_info in content.get('links', []):
                        href = link_info['href']
                        absolute_url = urljoin(current_url, href)
                        
                        if self.should_follow_link(absolute_url, base_domain):
                            if absolute_url not in self.visited_urls:
                                queue.append((absolute_url, depth + 1))
                
                # Aggregate API endpoints
                for endpoint in content.get('api_endpoints', []):
                    key = f"{endpoint['method']} {endpoint['path']}"
                    results['api_summary'][key] = results['api_summary'].get(key, 0) + 1
            
            # Rate limiting
            time.sleep(0.5)
        
        results['total_pages'] = len(results['pages'])
        
        # Build document structure from headings
        results['structure'] = self.build_document_structure(results['pages'])
        
        return results
    
    def build_document_structure(self, pages: List[Dict]) -> Dict:
        """Build a hierarchical structure from all pages."""
        structure = {
            'sections': {},
            'api_groups': {},
            'code_languages': set()
        }
        
        for page in pages:
            # Group by top-level headings
            current_section = page['title']
            for heading in page.get('headings', []):
                if heading['level'] == 1:
                    current_section = heading['text']
                if current_section not in structure['sections']:
                    structure['sections'][current_section] = []
                structure['sections'][current_section].append({
                    'level': heading['level'],
                    'text': heading['text'],
                    'url': page['url']
                })
            
            # Group APIs by path prefix
            for endpoint in page.get('api_endpoints', []):
                path_parts = endpoint['path'].split('/')
                if len(path_parts) > 1:
                    group = path_parts[1] if path_parts[1] else 'root'
                    if group not in structure['api_groups']:
                        structure['api_groups'][group] = []
                    structure['api_groups'][group].append(endpoint)
            
            # Collect code languages
            for code_block in page.get('code_blocks', []):
                if code_block.get('language'):
                    structure['code_languages'].add(code_block['language'])
        
        # Convert set to list for JSON serialization
        structure['code_languages'] = list(structure['code_languages'])
        
        return structure
    
    def format_for_llm(self, results: Dict) -> str:
        """Format scraped content for LLM consumption."""
        output = []
        
        # Header
        output.append(f"# Documentation for {results['domain']}")
        output.append(f"Base URL: {results['base_url']}")
        output.append(f"Total pages scraped: {results['total_pages']}")
        output.append("")
        
        # Table of Contents from structure
        if results['structure']['sections']:
            output.append("## Table of Contents")
            for section, headings in results['structure']['sections'].items():
                output.append(f"\n### {section}")
                for h in headings[:10]:  # Limit items
                    indent = "  " * (h['level'] - 1)
                    output.append(f"{indent}- {h['text']}")
        
        # API Summary
        if results['api_summary']:
            output.append("\n## API Endpoints")
            for endpoint, count in sorted(results['api_summary'].items())[:50]:
                output.append(f"- {endpoint}")
        
        # Detailed content from each page
        output.append("\n## Detailed Documentation")
        
        for page in results['pages'][:50]:  # Limit pages in output
            output.append(f"\n### {page['title']}")
            output.append(f"URL: {page['url']}")
            
            # Add headings
            for heading in page['headings'][:10]:
                output.append(f"{'#' * heading['level']} {heading['text']}")
            
            # Add key paragraphs
            for para in page['paragraphs'][:3]:
                output.append(f"\n{para}\n")
            
            # Add code examples
            for code in page['code_blocks'][:3]:
                lang = code.get('language', '')
                output.append(f"\n```{lang}")
                output.append(code['code'][:500])  # Limit code length
                output.append("```\n")
        
        return "\n".join(output)