# 🚀 Tourism Analytics Platform - Deployment Guide

> **Engineered by KoinTyme** - Enterprise deployment options for production hosting

## 🎯 **Single-Server Deployment (Recommended)**

The platform can run as a **single FastAPI service** with all analytics integrated. The Streamlit dashboard is optional for enterprise users.

**What you get with single-server deployment:**
- ✅ Complete FastAPI backend with all APIs
- ✅ Landing page with integrated analytics
- ✅ Sentiment analysis, forecasting, chat features
- ✅ Real-time statistics dashboard
- ✅ API documentation interface
- ✅ Cost-effective single container deployment

## Quick Deploy Options

### 🔥 Option 1: DigitalOcean App Platform (Recommended)

**Why Choose This**: Easiest setup, managed services, auto-scaling

1. **Create DigitalOcean Account**: [Sign up here](https://cloud.digitalocean.com)

2. **Deploy via App Platform**:
   - Go to "Apps" → "Create App"
   - Choose "GitHub" and connect your repository
   - Select: `rprovine/tourism-analytics-platform`
   - Branch: `main`
   - Auto-deploy: Enable

3. **Configure Services**:
   ```
   Web Service:
   - Name: tourism-analytics
   - Source: /
   - Build Command: (auto-detected)
   - Run Command: (auto-detected)
   - HTTP Port: 8000
   - Instance Size: Basic ($12/month)
   ```

4. **Add Databases** (via App Platform):
   - PostgreSQL: Basic ($15/month)
   - Redis: Basic ($15/month)

5. **Environment Variables**:
   ```
   DATABASE_URL=<auto-provided-by-DO>
   REDIS_URL=<auto-provided-by-DO>
   SECRET_KEY=<generate-secure-key>
   DEBUG=false
   PROJECT_NAME=Tourism Analytics Platform - KoinTyme
   ```

6. **Custom Domain** (Optional):
   - Add your domain in App Platform settings
   - Update DNS records as instructed
   - SSL automatically provided

**Total Cost**: ~$42/month
**Setup Time**: 15 minutes
**Live URL**: `https://your-app-name.ondigitalocean.app`

---

### ⚡ Option 2: Railway (Developer-Friendly)

**Why Choose This**: Fastest deployment, great developer experience

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy**:
   ```bash
   cd tourism-analytics-platform
   railway login
   railway init
   railway up
   ```

3. **Add Services**:
   ```bash
   railway add postgresql
   railway add redis
   ```

4. **Set Environment Variables** (in Railway dashboard):
   ```
   SECRET_KEY=your-production-secret
   DEBUG=false
   PROJECT_NAME=Tourism Analytics Platform - KoinTyme
   ```

**Total Cost**: ~$25/month
**Setup Time**: 10 minutes

---

### 🌐 Option 3: Vercel + PlanetScale + Upstash

**Why Choose This**: Serverless, global edge deployment

1. **Deploy to Vercel**:
   ```bash
   npm i -g vercel
   vercel --docker
   ```

2. **Database**: [PlanetScale](https://planetscale.com) (MySQL compatible)
3. **Redis**: [Upstash](https://upstash.com) (serverless Redis)

**Total Cost**: ~$20/month
**Setup Time**: 20 minutes

---

### 🏢 Option 4: AWS (Enterprise)

**Why Choose This**: Maximum scalability, enterprise features

1. **Push to ECR**:
   ```bash
   aws ecr create-repository --repository-name tourism-analytics
   docker build -t tourism-analytics .
   docker tag tourism-analytics:latest <account>.dkr.ecr.region.amazonaws.com/tourism-analytics:latest
   docker push <account>.dkr.ecr.region.amazonaws.com/tourism-analytics:latest
   ```

2. **Create ECS Service**:
   - Use Fargate for serverless containers
   - Configure ALB for load balancing
   - Set up RDS PostgreSQL
   - Set up ElastiCache Redis

3. **Domain & SSL**:
   - Route53 for DNS
   - Certificate Manager for SSL

**Total Cost**: $50-150/month
**Setup Time**: 1-2 hours

---

## 🔧 Production Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname
REDIS_URL=redis://host:port/0

# Security
SECRET_KEY=your-super-secure-secret-key-minimum-32-characters
DEBUG=false

# Application
PROJECT_NAME=Tourism Analytics Platform - KoinTyme
API_V1_STR=/api/v1
HOST=0.0.0.0
PORT=8000

# Storage
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# Model Paths
SENTIMENT_MODEL_PATH=models/sentiment
FORECASTING_MODEL_PATH=models/forecasting

# Optional API Keys
OPENAI_API_KEY=your-openai-key
HUBSPOT_API_KEY=your-hubspot-key
GOOGLE_TRANSLATE_API_KEY=your-google-translate-key
```

### Generate Secure Secret Key

```python
import secrets
print(secrets.token_urlsafe(32))
```

## 🎯 Post-Deployment Setup

1. **Run Migrations**:
   ```bash
   # Via platform console or API
   curl -X POST https://your-domain.com/api/v1/admin/migrate
   ```

2. **Seed Demo Data**:
   ```bash
   # Via API or admin panel
   curl -X POST https://your-domain.com/api/v1/admin/seed-demo-data
   ```

3. **Train Models**:
   ```bash
   curl -X POST https://your-domain.com/api/v1/forecasting/train
   ```

## 🔍 Health Monitoring

- **Health Check**: `https://your-domain.com/api/v1/health/`
- **Detailed Health**: `https://your-domain.com/api/v1/health/detailed`
- **Metrics**: Built-in Prometheus metrics at `/metrics`

## 🛡️ Security Checklist

- ✅ Use strong SECRET_KEY (32+ characters)
- ✅ Set DEBUG=false in production
- ✅ Use managed databases with backups
- ✅ Enable SSL/HTTPS
- ✅ Configure CORS properly
- ✅ Set up monitoring and alerts
- ✅ Regular security updates

## 📞 Support

**KoinTyme Production Support**
- 📧 Email: support@kointyme.com
- 🌐 Website: [kointyme.com](https://kointyme.com)
- 📱 24/7 Enterprise Support Available

---

*🚀 Engineered by KoinTyme - Pioneering AI Solutions for Tourism Industry*