#!/bin/bash

# Script to fix all domain HTTPS issues
# Run this on the server as root

echo "=== Fixing HTTPS for all domains ==="

# 1. Create SSL certificates
echo "Creating SSL certificates..."

# For mermaid.emino.app
if [ ! -d "/etc/letsencrypt/live/mermaid.emino.app" ]; then
    echo "Creating certificate for mermaid.emino.app..."
    certbot certonly --nginx -d mermaid.emino.app --non-interactive --agree-tos --email admin@emino.app
else
    echo "Certificate for mermaid.emino.app already exists"
fi

# For docscraper.emino.app (optional, can use docscrape cert)
if [ ! -d "/etc/letsencrypt/live/docscraper.emino.app" ]; then
    echo "Creating certificate for docscraper.emino.app..."
    certbot certonly --nginx -d docscraper.emino.app --non-interactive --agree-tos --email admin@emino.app
else
    echo "Certificate for docscraper.emino.app already exists"
fi

# 2. Create nginx configuration for docscraper.emino.app (redirect)
echo "Creating nginx config for docscraper.emino.app..."
cat > /etc/nginx/sites-available/docscraper.emino.app << 'EOF'
server {
    listen 80;
    server_name docscraper.emino.app;
    return 301 https://docscrape.emino.app$request_uri;
}

server {
    listen 443 ssl http2;
    server_name docscraper.emino.app;
    
    ssl_certificate /etc/letsencrypt/live/docscrape.emino.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docscrape.emino.app/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    return 301 https://docscrape.emino.app$request_uri;
}
EOF

# 3. Create nginx configuration for mermaid.emino.app
echo "Creating nginx config for mermaid.emino.app..."
cat > /etc/nginx/sites-available/mermaid.emino.app << 'EOF'
server {
    listen 80;
    server_name mermaid.emino.app;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mermaid.emino.app;
    
    ssl_certificate /etc/letsencrypt/live/mermaid.emino.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mermaid.emino.app/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
}
EOF

# 4. Fix docscrape.emino.app configuration
echo "Updating nginx config for docscrape.emino.app..."
cat > /etc/nginx/sites-available/docscrape.emino.app << 'EOF'
server {
    listen 80;
    server_name docscrape.emino.app;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name docscrape.emino.app;

    ssl_certificate /etc/letsencrypt/live/docscrape.emino.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/docscrape.emino.app/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
}
EOF

# 5. Enable all sites
echo "Enabling nginx sites..."
ln -sf /etc/nginx/sites-available/docscraper.emino.app /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/mermaid.emino.app /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/docscrape.emino.app /etc/nginx/sites-enabled/

# 6. Test nginx configuration
echo "Testing nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "Configuration is valid. Reloading nginx..."
    systemctl reload nginx
    echo "Nginx reloaded successfully"
else
    echo "ERROR: Nginx configuration is invalid. Please check the configs."
    exit 1
fi

# 7. Test all domains
echo ""
echo "=== Testing all domains ==="
echo "Testing docscrape.emino.app..."
curl -s -o /dev/null -w "HTTP Code: %{http_code}\n" https://docscrape.emino.app

echo "Testing docscraper.emino.app (should redirect)..."
curl -s -o /dev/null -w "HTTP Code: %{http_code} - Redirect: %{redirect_url}\n" https://docscraper.emino.app

echo "Testing mermaid.emino.app..."
curl -s -o /dev/null -w "HTTP Code: %{http_code}\n" https://mermaid.emino.app

echo ""
echo "=== All done! ==="
echo "Domains configured:"
echo "- https://docscrape.emino.app (main)"
echo "- https://docscraper.emino.app (redirects to docscrape)"
echo "- https://mermaid.emino.app (same app)"