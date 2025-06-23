# 🚀 Simple One-Click Deployment

> **DigitalOcean keeps showing 2 servers? Use Railway instead!**

## ⚡ **Option 1: Railway (Recommended - Actually Works!)**

**Why Railway**: 
- ✅ Actually detects single service correctly
- ✅ Auto-provisions databases
- ✅ Cheaper ($20-25/month total)
- ✅ Easier setup

### **Steps (5 minutes)**:

1. **Go to**: [railway.app](https://railway.app)
2. **Sign up** with GitHub
3. **Click**: "Deploy from GitHub repo"
4. **Select**: `rprovine/tourism-analytics-platform`
5. **Railway will**:
   - Auto-detect the Dockerfile
   - Deploy as single service
   - Provide PostgreSQL database
   - Provide Redis database
6. **Set Environment Variables**:
   ```
   SECRET_KEY=your-32-character-secret-key
   DEBUG=false
   PROJECT_NAME=Tourism Analytics Platform - KoinTyme
   ```
7. **Deploy!**

**Total Cost**: ~$25/month  
**Setup Time**: 5 minutes  
**Services**: 1 (finally!)

## 🔵 **Option 2: DigitalOcean (If You Must)**

**The Issue**: DigitalOcean's auto-detection is overly aggressive and sees multiple services even when there's only one Dockerfile.

**Workaround**:
1. **Create App** in DigitalOcean
2. **When it shows 2 services**: 
   - **Delete both** auto-detected services
   - **Manually add** ONE web service:
     - Name: `api`
     - Source Directory: `/`
     - Build Command: (blank)
     - Run Command: (blank)
     - Port: `8000`
3. **Add databases** separately
4. **Deploy**

## 🌐 **Option 3: Render (Backup Option)**

1. **Go to**: [render.com](https://render.com)
2. **New Web Service**
3. **Connect**: `rprovine/tourism-analytics-platform`
4. **Settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `sh -c 'alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT'`
5. **Add PostgreSQL** and **Redis** databases
6. **Deploy**

**Cost**: ~$25/month

## 🎯 **What You Get (All Options)**

After deployment, you'll have:
- ✅ **Live Tourism Analytics Platform**
- ✅ **KoinTyme branding throughout**
- ✅ **Working sentiment analysis**
- ✅ **Working demand forecasting** 
- ✅ **Real-time dashboard statistics**
- ✅ **Complete API documentation**
- ✅ **Professional production setup**

## 📞 **Recommendation**

**Use Railway** - it's the only platform that consistently detects this as a single service and deploys correctly on the first try.

DigitalOcean's auto-detection has issues with this particular setup.

---

*🚀 Engineered by KoinTyme - Get your analytics platform live in minutes!*