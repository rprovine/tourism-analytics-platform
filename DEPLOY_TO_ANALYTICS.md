# Deploy Tourism BI Platform to analytics.lenilani.com

## Option 1: Deploy with Railway (Recommended)

Railway provides the easiest deployment for Streamlit apps with custom domains.

### Steps:

1. **Login to Railway**
```bash
railway login
```

2. **Initialize project**
```bash
cd /Users/renoprovine/Development/tourism-analytics-platform
railway init
```

3. **Deploy the app**
```bash
railway up
```

4. **Add custom domain**
- Go to Railway dashboard
- Select your project
- Go to Settings → Domains
- Add custom domain: analytics.lenilani.com
- Update DNS records:
  - Type: CNAME
  - Name: analytics
  - Value: [your-app].up.railway.app

## Option 2: Deploy with Render

### Steps:

1. **Push to GitHub**
```bash
git add .
git commit -m "Deploy Tourism BI Platform"
git push origin main
```

2. **Connect to Render**
- Go to https://render.com
- Create new Web Service
- Connect GitHub repository
- Select branch: main
- Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`

3. **Add custom domain**
- Go to Settings → Custom Domains
- Add: analytics.lenilani.com
- Update DNS with provided CNAME

## Option 3: Deploy with Streamlit Cloud (Free)

### Steps:

1. **Push to GitHub**
```bash
git add .
git commit -m "Deploy Tourism BI Platform"
git push origin main
```

2. **Deploy on Streamlit Cloud**
- Go to https://share.streamlit.io
- Click "New app"
- Select repository
- Main file path: streamlit_app.py
- Click Deploy

3. **Custom domain setup**
- Contact Streamlit support for custom domain
- Or use subdomain: yourapp.streamlit.app
- Set up redirect from analytics.lenilani.com

## Option 4: Deploy with Google Cloud Run

### Steps:

1. **Create Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD streamlit run streamlit_app.py --server.port 8080 --server.address 0.0.0.0
```

2. **Build and push**
```bash
gcloud builds submit --tag gcr.io/[PROJECT-ID]/tourism-bi
gcloud run deploy --image gcr.io/[PROJECT-ID]/tourism-bi --platform managed
```

3. **Map custom domain**
```bash
gcloud run domain-mappings create --service tourism-bi --domain analytics.lenilani.com
```

## DNS Configuration

For analytics.lenilani.com, add one of these DNS records:

### For Railway/Render:
- Type: CNAME
- Name: analytics
- Value: [provided-by-platform].railway.app or .onrender.com

### For Google Cloud Run:
- Type: A
- Name: analytics
- Value: [IP provided by Google]

## Environment Variables

Create `.env` file:
```env
APP_NAME=Tourism Business Intelligence Platform
ENVIRONMENT=production
```

## Post-Deployment

1. Test the site: https://analytics.lenilani.com
2. Set up monitoring
3. Configure SSL certificate (usually automatic)
4. Set up GitHub Actions for CI/CD

## Quick Deploy Script

```bash
#!/bin/bash
# deploy.sh
echo "Deploying Tourism BI Platform..."
git add .
git commit -m "Update Tourism BI Platform"
git push origin main
railway up
echo "Deployment complete!"
```

## Support

For issues, check:
- Application logs in deployment platform
- Streamlit error messages
- DNS propagation status