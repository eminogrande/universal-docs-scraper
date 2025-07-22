"""
Streamlit version of Universal Docs Scraper
Deploy directly to Streamlit Cloud for free!
"""

import streamlit as st
import sys
import os
from pathlib import Path
import zipfile
import io
from datetime import datetime

# Add scraper to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scraper.universal_scraper import UniversalDocsScraper

st.set_page_config(
    page_title="Universal Docs Scraper",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Universal Documentation Scraper")
st.markdown("Convert any documentation website to clean Markdown files")

# Input form
with st.form("scraper_form"):
    url = st.text_input("Documentation URL", placeholder="https://docs.example.com")
    col1, col2 = st.columns(2)
    with col1:
        rate_limit = st.number_input("Rate Limit (seconds)", min_value=0.1, value=1.0, step=0.1)
    with col2:
        max_pages = st.number_input("Max Pages", min_value=1, value=100)
    
    submitted = st.form_submit_button("Start Scraping", type="primary")

if submitted and url:
    # Create output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    domain = url.split('/')[2].replace('www.', '')
    output_dir = f"scraped_{domain}_{timestamp}"
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    log_container = st.container()
    
    # Initialize scraper
    scraper = UniversalDocsScraper(
        base_url=url,
        output_dir=output_dir,
        rate_limit=rate_limit,
        max_pages=max_pages
    )
    
    # Run scraper
    with st.spinner("Discovering URLs..."):
        urls = scraper.get_sitemap_urls()
        if not urls:
            urls = scraper.discover_urls_by_crawling()
    
    if urls:
        st.success(f"Found {len(urls)} URLs to scrape")
        
        # Scrape pages
        for i, page_url in enumerate(urls):
            progress = (i + 1) / len(urls)
            progress_bar.progress(progress)
            status_text.text(f"Scraping {i+1}/{len(urls)}: {page_url}")
            
            with log_container:
                if scraper.scrape_page(page_url):
                    st.success(f"✅ Scraped: {page_url}")
                else:
                    st.error(f"❌ Failed: {page_url}")
            
            if scraper.scraped_count >= max_pages:
                break
        
        # Create combined markdown
        if scraper.scraped_count > 0:
            with st.spinner("Creating combined markdown..."):
                scraper.create_combined_markdown()
        
        # Create download
        with st.spinner("Creating download package..."):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, output_dir)
                        zf.write(file_path, arcname)
            
            zip_buffer.seek(0)
            
            st.download_button(
                label="📥 Download Scraped Documentation",
                data=zip_buffer,
                file_name=f"{output_dir}.zip",
                mime="application/zip"
            )
            
            st.success(f"✅ Scraping complete! {scraper.scraped_count} pages scraped.")
    else:
        st.error("No URLs found to scrape")

# Features section
with st.expander("✨ Features"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **🚀 Smart Detection**
        - Automatic content extraction
        - Removes navigation/ads
        - Preserves formatting
        """)
    with col2:
        st.markdown("""
        **📄 Clean Output**
        - Well-formatted Markdown
        - Combined single file
        - Metadata preserved
        """)
    with col3:
        st.markdown("""
        **🕷️ Intelligent**
        - Sitemap detection
        - Smart crawling
        - Rate limiting
        """)

st.markdown("---")
st.markdown("Made with ❤️ | [GitHub](https://github.com/eminogrande/universal-docs-scraper)")