#!/usr/bin/env python3
"""
Universal Documentation Scraper
A flexible web scraper for converting any documentation site to markdown files.
"""

import requests
from bs4 import BeautifulSoup
import markdownify
import os
import time
import re
import json
import argparse
from urllib.parse import urljoin, urlparse
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import List, Set, Dict, Optional
import logging
from datetime import datetime

class UniversalDocsScraper:
    def __init__(self, base_url: str, output_dir: str = "scraped_docs", 
                 rate_limit: float = 1.0, max_pages: int = 1000):
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.rate_limit = rate_limit
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; UniversalDocsScraper/1.0; +https://github.com/yourusername/universal-docs-scraper)'
        })
        self.visited_urls: Set[str] = set()
        self.scraped_count = 0
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Content selectors for different documentation platforms
        self.content_selectors = [
            # Readme.com
            '.readme-content', '[data-testid="readme-content"]', '.hub-content-body',
            # GitBook
            '.markdown-section', '.page-wrapper', 
            # Docusaurus
            '.markdown', 'article', '.docMainContainer',
            # MkDocs
            '.md-content', '.content',
            # Sphinx
            '.document', '.body',
            # Generic
            'main', '[role="main"]', '.main-content', '.documentation-content',
            '#content', '.content-wrapper'
        ]
        
        # Elements to remove
        self.remove_selectors = [
            'nav', 'header', 'footer', '.sidebar', '.navigation', '.toc',
            '.breadcrumbs', '.edit-page', '.feedback', '.rating',
            '[class*="sidebar"]', '[class*="navigation"]', '[class*="footer"]'
        ]
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.output_dir / 'scraper.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def get_sitemap_urls(self) -> List[str]:
        """Try to find and parse sitemap URLs"""
        sitemap_locations = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap-index.xml',
            '/sitemaps/sitemap.xml',
            '/robots.txt'  # Check robots.txt for sitemap location
        ]
        
        all_urls = set()
        
        # First check robots.txt
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                for line in response.text.splitlines():
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        urls = self.parse_sitemap(sitemap_url)
                        all_urls.update(urls)
        except Exception as e:
            self.logger.debug(f"Could not fetch robots.txt: {e}")
        
        # Try common sitemap locations
        for location in sitemap_locations:
            sitemap_url = urljoin(self.base_url, location)
            urls = self.parse_sitemap(sitemap_url)
            all_urls.update(urls)
            
        return list(all_urls)
    
    def parse_sitemap(self, sitemap_url: str) -> Set[str]:
        """Parse a sitemap and return URLs"""
        urls = set()
        try:
            response = self.session.get(sitemap_url, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                # Handle namespaces
                namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                # Check if it's a sitemap index
                sitemaps = root.findall('.//ns:sitemap', namespaces)
                if sitemaps:
                    for sitemap in sitemaps:
                        loc = sitemap.find('ns:loc', namespaces)
                        if loc is not None:
                            sub_urls = self.parse_sitemap(loc.text)
                            urls.update(sub_urls)
                else:
                    # Direct sitemap with URLs
                    for url_elem in root.findall('.//ns:url', namespaces):
                        loc = url_elem.find('ns:loc', namespaces)
                        if loc is not None:
                            urls.add(loc.text)
                            
        except Exception as e:
            self.logger.debug(f"Could not parse sitemap {sitemap_url}: {e}")
            
        return urls
    
    def discover_urls_by_crawling(self) -> List[str]:
        """Discover URLs by crawling the site"""
        self.logger.info("Starting URL discovery through crawling...")
        
        to_visit = [self.base_url]
        discovered = set()
        
        while to_visit and len(discovered) < self.max_pages:
            url = to_visit.pop(0)
            if url in discovered:
                continue
                
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    discovered.add(url)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find all internal links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(url, href)
                        
                        # Only process internal links
                        if (full_url.startswith(self.base_url) and 
                            full_url not in discovered and 
                            not any(ext in full_url for ext in ['.pdf', '.zip', '.png', '.jpg', '.gif'])):
                            to_visit.append(full_url)
                    
                    time.sleep(self.rate_limit)
                    
            except Exception as e:
                self.logger.error(f"Error crawling {url}: {e}")
                
        return list(discovered)
    
    def extract_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Extract main content from the page"""
        # First, remove unwanted elements
        for selector in self.remove_selectors:
            for elem in soup.select(selector):
                elem.decompose()
        
        # Try to find main content
        for selector in self.content_selectors:
            content = soup.select_one(selector)
            if content:
                return content
                
        # Fallback: use body
        return soup.find('body')
    
    def clean_filename(self, url: str) -> str:
        """Create a clean filename from URL"""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if not path:
            return "index.md"
            
        # Replace problematic characters
        filename = re.sub(r'[^\w\-_./]', '_', path)
        filename = filename.replace('/', '_')
        
        # Ensure .md extension
        if not filename.endswith('.md'):
            filename += '.md'
            
        return filename
    
    def scrape_page(self, url: str) -> bool:
        """Scrape a single page"""
        try:
            self.logger.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                self.logger.error(f"HTTP {response.status_code} for {url}")
                return False
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = "Untitled"
            title_elem = soup.find('title')
            if title_elem:
                title = title_elem.get_text().strip()
            
            # Extract main content
            content = self.extract_content(soup)
            if not content:
                self.logger.warning(f"No content found for {url}")
                return False
            
            # Convert to markdown
            markdown_content = markdownify.markdownify(
                str(content),
                heading_style="ATX",
                bullets="-",
                code_language="",
                strip=['img', 'script', 'style']
            )
            
            # Clean up markdown
            markdown_content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)
            markdown_content = markdown_content.strip()
            
            # Save file
            filename = self.clean_filename(url)
            filepath = self.output_dir / filename
            
            # Add metadata
            metadata = {
                'title': title,
                'source_url': url,
                'scraped_at': datetime.now().isoformat(),
                'scraper_version': '1.0.0'
            }
            
            final_content = f"""---
{json.dumps(metadata, indent=2)}
---

# {title}

{markdown_content}
"""
            
            # Ensure parent directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            self.scraped_count += 1
            self.logger.info(f"✅ Saved as {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return False
    
    def run(self, urls: Optional[List[str]] = None):
        """Run the scraper"""
        self.logger.info(f"🚀 Starting scraper for {self.base_url}")
        self.logger.info(f"📁 Output directory: {self.output_dir.absolute()}")
        
        # Get URLs to scrape
        if urls:
            urls_to_scrape = urls
        else:
            # Try sitemap first
            urls_to_scrape = self.get_sitemap_urls()
            
            if not urls_to_scrape:
                self.logger.info("No sitemap found, starting crawl discovery...")
                urls_to_scrape = self.discover_urls_by_crawling()
        
        if not urls_to_scrape:
            self.logger.error("No URLs found to scrape!")
            return
        
        self.logger.info(f"📄 Found {len(urls_to_scrape)} URLs to scrape")
        
        # Scrape pages
        success_count = 0
        for i, url in enumerate(urls_to_scrape, 1):
            if self.scraped_count >= self.max_pages:
                self.logger.warning(f"Reached maximum page limit ({self.max_pages})")
                break
                
            self.logger.info(f"\n[{i}/{len(urls_to_scrape)}]")
            
            if self.scrape_page(url):
                success_count += 1
            
            # Rate limiting
            time.sleep(self.rate_limit)
        
        self.logger.info(f"\n🎉 Scraping complete! {success_count}/{len(urls_to_scrape)} pages scraped successfully")
        self.logger.info(f"📁 Files saved to: {self.output_dir.absolute()}")
        
        # Save scraping summary
        self.save_summary(urls_to_scrape, success_count)
        
        # Create combined markdown file
        if success_count > 0:
            self.create_combined_markdown()
    
    def save_summary(self, urls: List[str], success_count: int):
        """Save a summary of the scraping session"""
        summary = {
            'base_url': self.base_url,
            'total_urls': len(urls),
            'successful_scrapes': success_count,
            'failed_scrapes': len(urls) - success_count,
            'scraped_at': datetime.now().isoformat(),
            'rate_limit': self.rate_limit,
            'max_pages': self.max_pages
        }
        
        summary_file = self.output_dir / 'scraping_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def create_combined_markdown(self):
        """Create a single markdown file with all scraped content"""
        self.logger.info("Creating combined markdown file...")
        
        combined_file = self.output_dir / 'COMBINED_DOCUMENTATION.md'
        
        with open(combined_file, 'w', encoding='utf-8') as combined:
            # Write header
            combined.write(f"""# Combined Documentation - {self.base_url}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total files: {len(list(self.output_dir.glob('*.md')))}

---

""")
            
            # Sort markdown files for consistent ordering
            md_files = sorted([f for f in self.output_dir.glob('*.md') 
                              if f.name not in ['COMBINED_DOCUMENTATION.md', 'README.md']])
            
            for i, md_file in enumerate(md_files, 1):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract title from content or use filename
                    title = md_file.stem.replace('_', ' ').title()
                    if content.startswith('---'):
                        # Try to extract title from frontmatter
                        lines = content.split('\n')
                        for line in lines[1:]:
                            if line.startswith('---'):
                                break
                            if line.startswith('title:'):
                                title = line.replace('title:', '').strip().strip('"\'')
                    
                    combined.write(f"\n\n{'='*80}\n")
                    combined.write(f"## [{i}] {title}\n")
                    combined.write(f"Source: {md_file.name}\n")
                    combined.write(f"{'='*80}\n\n")
                    combined.write(content)
                    combined.write("\n\n")
                    
                except Exception as e:
                    self.logger.error(f"Error adding {md_file} to combined file: {e}")
        
        self.logger.info(f"✅ Combined markdown saved as COMBINED_DOCUMENTATION.md")


def main():
    parser = argparse.ArgumentParser(description='Universal Documentation Scraper')
    parser.add_argument('url', help='Base URL of the documentation site to scrape')
    parser.add_argument('-o', '--output', default='scraped_docs', 
                        help='Output directory (default: scraped_docs)')
    parser.add_argument('-r', '--rate-limit', type=float, default=1.0,
                        help='Seconds between requests (default: 1.0)')
    parser.add_argument('-m', '--max-pages', type=int, default=1000,
                        help='Maximum number of pages to scrape (default: 1000)')
    parser.add_argument('--urls', nargs='+', help='Specific URLs to scrape')
    
    args = parser.parse_args()
    
    scraper = UniversalDocsScraper(
        base_url=args.url,
        output_dir=args.output,
        rate_limit=args.rate_limit,
        max_pages=args.max_pages
    )
    
    scraper.run(urls=args.urls)


if __name__ == "__main__":
    main()