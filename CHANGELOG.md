# Changelog

All notable changes. Newest first. SHAs point to commits on `main`.

## 2026-10-14 — [RELEASE] v0.1.0 — hermes-agent for emino

First tagged release. Describes `main` at HEAD `2d8487a4`.

- State: Python CLI (`scraper/universal_scraper.py`), Flask web app (`frontend/app.py`) and Streamlit app (`streamlit_app.py`) that convert a docs site to Markdown files plus `COMBINED_DOCUMENTATION.md`.
- Deploy configs for Docker, Fly.io, Railway and Render. No live URL documented.
- Docs: README rewritten with status, architecture, user flow, endpoints and run commands. CHANGELOG and PROMPTLOG added (docs PR only, no code change).

## 2025-07-22

- `2d8487a4` Added a Streamlit app (`streamlit_app.py`) with a form, live progress and a zip download button.
- `44864246` Scraper now writes `COMBINED_DOCUMENTATION.md` with all pages in one file. Added Dockerfile, `fly.toml`, `railway.json`, `render.yaml`, `deployment.md`. Flask app reads `PORT` and binds `0.0.0.0` for cloud hosts. Added `frontend/test_server.py`.

## 2025-07-19

- `e7be2ce2` Initial commit: universal scraper with sitemap discovery, crawl fallback, platform content selectors, Markdown output with frontmatter, Flask web UI, Striga docs analysis.
