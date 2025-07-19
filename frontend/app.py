#!/usr/bin/env python3
"""
Web interface for Universal Documentation Scraper
"""

from flask import Flask, render_template, request, jsonify, send_file, session
import sys
import os
import json
import threading
import queue
import time
from pathlib import Path
from datetime import datetime
import zipfile
import io
import secrets

# Add parent directory to path to import scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.universal_scraper import UniversalDocsScraper

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Store scraping progress
scraping_sessions = {}

class ScrapingSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.status = "initializing"
        self.progress = 0
        self.total_urls = 0
        self.scraped_urls = 0
        self.logs = []
        self.output_dir = None
        self.start_time = datetime.now()
        self.end_time = None
        self.error = None
        
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'status': self.status,
            'progress': self.progress,
            'total_urls': self.total_urls,
            'scraped_urls': self.scraped_urls,
            'logs': self.logs[-50:],  # Last 50 log entries
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'error': self.error
        }

class LogCapture:
    def __init__(self, session):
        self.session = session
        
    def write(self, message):
        if message.strip():
            self.session.logs.append({
                'time': datetime.now().isoformat(),
                'message': message.strip()
            })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def start_scraping():
    data = request.json
    url = data.get('url')
    rate_limit = float(data.get('rate_limit', 1.0))
    max_pages = int(data.get('max_pages', 100))
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Create session
    session_id = secrets.token_urlsafe(16)
    scraping_session = ScrapingSession(session_id)
    scraping_sessions[session_id] = scraping_session
    
    # Start scraping in background thread
    thread = threading.Thread(
        target=run_scraper,
        args=(scraping_session, url, rate_limit, max_pages)
    )
    thread.start()
    
    return jsonify({'session_id': session_id})

def run_scraper(session, url, rate_limit, max_pages):
    try:
        session.status = "discovering"
        
        # Create output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        domain = url.split('/')[2].replace('www.', '')
        output_dir = f"scraped_{domain}_{timestamp}"
        session.output_dir = output_dir
        
        # Initialize scraper
        scraper = UniversalDocsScraper(
            base_url=url,
            output_dir=output_dir,
            rate_limit=rate_limit,
            max_pages=max_pages
        )
        
        # Capture logs
        import logging
        log_handler = logging.StreamHandler(LogCapture(session))
        log_handler.setLevel(logging.INFO)
        scraper.logger.addHandler(log_handler)
        
        # Discover URLs
        session.logs.append({
            'time': datetime.now().isoformat(),
            'message': f'Starting URL discovery for {url}'
        })
        
        urls = scraper.get_sitemap_urls()
        if not urls:
            session.logs.append({
                'time': datetime.now().isoformat(),
                'message': 'No sitemap found, starting crawl discovery...'
            })
            urls = scraper.discover_urls_by_crawling()
        
        session.total_urls = len(urls)
        session.status = "scraping"
        
        # Scrape pages
        for i, page_url in enumerate(urls):
            if session.status == "cancelled":
                break
                
            session.scraped_urls = i
            session.progress = int((i / len(urls)) * 100)
            
            scraper.scrape_page(page_url)
            
            if scraper.scraped_count >= max_pages:
                break
        
        session.status = "completed"
        session.end_time = datetime.now()
        
        # Save summary
        scraper.save_summary(urls, scraper.scraped_count)
        
    except Exception as e:
        session.status = "error"
        session.error = str(e)
        session.end_time = datetime.now()
        import traceback
        session.logs.append({
            'time': datetime.now().isoformat(),
            'message': f'Error: {traceback.format_exc()}'
        })

@app.route('/status/<session_id>')
def get_status(session_id):
    session = scraping_sessions.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify(session.to_dict())

@app.route('/download/<session_id>')
def download_results(session_id):
    session = scraping_sessions.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    if session.status != "completed":
        return jsonify({'error': 'Scraping not completed'}), 400
    
    if not session.output_dir or not os.path.exists(session.output_dir):
        return jsonify({'error': 'Output directory not found'}), 404
    
    # Create zip file in memory
    memory_file = io.BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(session.output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, session.output_dir)
                zf.write(file_path, arcname)
    
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'{session.output_dir}.zip'
    )

@app.route('/cancel/<session_id>', methods=['POST'])
def cancel_scraping(session_id):
    session = scraping_sessions.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    session.status = "cancelled"
    return jsonify({'status': 'cancelled'})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, port=5000)