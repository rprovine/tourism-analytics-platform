# 🚀 DigitalOcean Single-Server Deployment

> **Fix for "Two Servers" Issue - Deploy as Single Service**

## ✅ **Step-by-Step Single Service Deployment**

### 1. **Create DigitalOcean App**
- Go to: [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
- Click: **"Create App"**
- Choose: **"GitHub"**

### 2. **Connect Repository**
- Repository: `rprovine/tourism-analytics-platform`
- Branch: `main`
- Source Directory: `/` (root)
- Autodeploy: ✅ **Enable**

### 3. **Configure Single Service**
**IMPORTANT**: DigitalOcean might detect multiple services. Here's how to fix:

**Service Configuration:**
- **Service Name**: `tourism-analytics`
- **Service Type**: `Web Service`
- **Source Directory**: `/`
- **Dockerfile Path**: `Dockerfile` (use the main one, NOT Dockerfile.simple)
- **Build Command**: (leave blank - auto-detected)
- **Run Command**: (leave blank - auto-detected)

### 4. **Set Port and Resources**
- **HTTP Port**: `8000`
- **Instance Count**: `1`
- **Instance Size**: `Basic ($12/month)`

### 5. **Add Databases**
Click **"Add Database"** twice:

**PostgreSQL Database:**
- **Name**: `tourism-db`
- **Engine**: `PostgreSQL 15`
- **Size**: `Basic ($15/month)`

**Redis Database:**
- **Name**: `tourism-redis` 
- **Engine**: `Redis 7`
- **Size**: `Basic ($15/month)`

### 6. **Environment Variables**
Add these in the **Environment** section:

```
SECRET_KEY = [Generate 32-character key - see below]
DEBUG = false
PROJECT_NAME = Tourism Analytics Platform - KoinTyme
API_V1_STR = /api/v1
HOST = 0.0.0.0
PORT = 8000
```

**Generate SECRET_KEY:**
```python
import secrets
print(secrets.token_urlsafe(32))
# Copy the output to SECRET_KEY
```

### 7. **Review Configuration**
**Double-check you have:**
- ✅ **1 Web Service** (not 2!)
- ✅ **1 PostgreSQL Database**
- ✅ **1 Redis Database**  
- ✅ **Environment variables set**

### 8. **Deploy**
- Click **"Create Resources"**
- Wait 5-10 minutes for deployment
- You'll get a URL like: `https://tourism-analytics-abc123.ondigitalocean.app`

## 🔧 **If DigitalOcean Still Shows Two Services**

**Problem**: DigitalOcean detects docker-compose files and thinks you want multiple services.

**Solution**: 
1. **Delete the detected services**
2. **Manually add one service** with these settings:
   - Service Type: **Web Service**
   - Name: `api`
   - Source Directory: `/`
   - Dockerfile: `Dockerfile`
   - Port: `8000`

## 🎯 **Expected Final Setup**

**Services: 1**
- `api` (Web Service) - $12/month

**Databases: 2**  
- `tourism-db` (PostgreSQL) - $15/month
- `tourism-redis` (Redis) - $15/month

**Total: ~$42/month**

## ✅ **Test Your Deployment**

Once live, test these URLs:
```
https://your-app.ondigitalocean.app/api/v1/           # Main platform
https://your-app.ondigitalocean.app/api/v1/health/    # Health check
https://your-app.ondigitalocean.app/docs              # API docs
```

## 🚨 **Troubleshooting**

**If you still see two services:**
1. **Start over** with App Platform
2. **Choose "Docker" instead of "Source Code"**
3. **Upload just the Dockerfile** (not the whole repo)
4. **Manually configure** the GitHub connection

**If deployment fails:**
1. Check the **build logs** in DigitalOcean dashboard
2. Verify **environment variables** are set
3. Ensure **database connections** are working

## 📞 **Need Help?**

- **DigitalOcean Support**: [Support Center](https://cloud.digitalocean.com/support)
- **KoinTyme Support**: support@kointyme.com

---

*🚀 This should deploy as a single service with all KoinTyme analytics integrated!*