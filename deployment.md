# Deployment Guide

## Quick Deploy Options

### 1. Railway (Recommended - Easiest)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy from the repository
railway up
```
Or use the web interface:
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repo
3. Railway will auto-detect the Dockerfile and deploy

### 2. Render
1. Go to [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Render will use the `render.yaml` file automatically

### 3. Fly.io
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
fly launch
fly deploy
```

### 4. Google Cloud Run
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/universal-docs-scraper

# Deploy to Cloud Run
gcloud run deploy --image gcr.io/PROJECT-ID/universal-docs-scraper --platform managed
```

### 5. Heroku (Requires credit card)
```bash
# Create Procfile
echo "web: cd frontend && python app.py" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

## Important Notes

1. **Environment Variables**: Set `PORT` if your platform requires a specific port
2. **Memory**: The scraper may need 512MB+ RAM for large documentation sites
3. **Timeouts**: Some platforms have 30-second timeouts - consider this for large scraping jobs
4. **Storage**: Scraped files are temporary - consider adding cloud storage for persistence

## Streamlit Cloud (NEW - Easiest for Python!)

**Perfect for Python apps with UI:**

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Select `streamlit_app.py` as the main file
5. Deploy!

Run locally with:
```bash
streamlit run streamlit_app.py
```

## Cost Comparison

| Platform | Free Tier | Paid Starting Price | Best For |
|----------|-----------|-------------------|----------|
| Streamlit Cloud | Unlimited public apps | $0 | Python apps with UI |
| Railway | $5 credit/month | $5/month | Full-stack apps |
| Render | 750 hours/month | $7/month | Web services |
| Fly.io | 3 shared VMs | $1.94/month | Global apps |
| Google Cloud Run | 2M requests/month | Pay per use | Scalable APIs |
| PythonAnywhere | 1 web app | $5/month | Python only |
| Vercel | Unlimited | $20/month | Next.js/React |

## Security Considerations

1. Add rate limiting to prevent abuse
2. Consider adding authentication for production use
3. Set up CORS properly if exposing API
4. Use environment variables for sensitive data