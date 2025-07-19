# Universal Documentation Scraper 📚

A powerful and flexible web scraper designed to convert any documentation website into clean, organized Markdown files. Perfect for offline reading, archiving, or processing documentation with LLMs.

## 🌟 Features

- **Universal Compatibility**: Works with most documentation platforms (Readme.com, GitBook, Docusaurus, MkDocs, Sphinx, etc.)
- **Smart Content Extraction**: Automatically identifies and extracts main content while removing navigation, ads, and clutter
- **Sitemap Support**: Automatically discovers pages via sitemap.xml or robots.txt
- **Intelligent Crawling**: Falls back to crawling when no sitemap is available
- **Rate Limiting**: Respects server resources with configurable delays
- **Clean Markdown Output**: Converts HTML to well-formatted Markdown with proper structure
- **Metadata Preservation**: Stores source URL, title, and scraping timestamp
- **Progress Logging**: Real-time progress updates and detailed logging
- **Web Interface**: Simple web UI for easy scraping (see `frontend/` directory)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/universal-docs-scraper.git
cd universal-docs-scraper

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Scrape a documentation site
python scraper/universal_scraper.py https://docs.example.com

# Specify output directory
python scraper/universal_scraper.py https://docs.example.com -o my_docs

# Adjust rate limiting (seconds between requests)
python scraper/universal_scraper.py https://docs.example.com -r 2.0

# Limit maximum pages
python scraper/universal_scraper.py https://docs.example.com -m 100

# Scrape specific URLs only
python scraper/universal_scraper.py https://docs.example.com --urls https://docs.example.com/guide https://docs.example.com/api
```

### Web Interface

For a user-friendly experience, use the web interface:

```bash
cd frontend
python app.py
# Open http://localhost:5000 in your browser
```

## 📁 Output Structure

The scraper creates an output directory with:
- Markdown files for each scraped page
- `scraping_summary.json` with statistics
- `scraper.log` with detailed logs

Each Markdown file includes:
- YAML frontmatter with metadata
- Original page title
- Clean, formatted content

## 🏗️ Project Structure

```
universal-docs-scraper/
├── scraper/
│   └── universal_scraper.py    # Main scraper script
├── frontend/
│   ├── app.py                  # Flask web application
│   ├── templates/
│   └── static/
├── docs/
│   └── striga_docs/           # Example: Scraped Striga documentation
├── analysis/
│   └── striga_analysis.md     # Example: Analysis of Striga docs
├── requirements.txt
├── LICENSE
└── README.md
```

## 📊 Example: Striga Documentation Analysis

This repository includes a complete scrape of the Striga API documentation (as of January 2025) along with a detailed analysis of authentication requirements and user flows. See `analysis/striga_analysis.md` for insights on building frictionless Bitcoin wallets with fiat off-ramps.

### Key Findings from Striga Analysis:
- Comprehensive user story mapping with authentication requirements
- Identification of lowest-friction paths for Bitcoin → EUR → Card flows
- Complete API endpoint categorization
- KYC tier requirements and limitations

## 🛠️ How It Works

1. **URL Discovery**:
   - First attempts to find sitemap.xml via common locations and robots.txt
   - Falls back to intelligent crawling if no sitemap exists

2. **Content Extraction**:
   - Uses platform-specific selectors for major documentation systems
   - Removes navigation, sidebars, footers automatically
   - Falls back to generic content detection

3. **Markdown Conversion**:
   - Preserves formatting, code blocks, and structure
   - Cleans up excessive whitespace
   - Maintains readability

4. **Rate Limiting**:
   - Default 1-second delay between requests
   - Configurable to respect server resources

## 🔧 Configuration

### Content Selectors

The scraper uses intelligent defaults but can be customized by modifying the `content_selectors` list in `universal_scraper.py`:

```python
self.content_selectors = [
    '.your-custom-selector',
    '#specific-content-id',
    # ... add your selectors
]
```

### Remove Selectors

Customize elements to remove by modifying `remove_selectors`:

```python
self.remove_selectors = [
    '.ads',
    '.popup',
    # ... elements to remove
]
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Areas for Contribution:
- Add support for more documentation platforms
- Improve content extraction algorithms
- Add authentication support for private docs
- Enhance the web interface
- Add export formats (PDF, EPUB, etc.)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Originally created to scrape and analyze Striga API documentation
- Inspired by the need for offline documentation access
- Built with love for the developer community

## ⚠️ Disclaimer

Please respect website terms of service and robots.txt when using this scraper. This tool is intended for personal use, archiving, and research purposes. Always check the website's terms before scraping.

## 📈 Scraping Statistics

When the scraper completes, it generates a `scraping_summary.json` file with statistics:

```json
{
  "base_url": "https://docs.striga.com",
  "total_urls": 160,
  "successful_scrapes": 156,
  "failed_scrapes": 4,
  "scraped_at": "2025-01-18T10:30:00",
  "rate_limit": 1.0,
  "max_pages": 1000
}
```

## 🚦 Status

- ✅ Core scraping functionality
- ✅ Universal platform support
- ✅ Web interface
- ✅ Striga documentation example
- 🔄 Authentication support (planned)
- 🔄 PDF export (planned)

---

**Created with ❤️ by [Your Name] | Generated: January 2025**