# 🎯 Deploy to Render.com (Recommended)

> **Railway having issues? Render.com is more reliable for FastAPI apps!**

## 🚀 **Step-by-Step Render Deployment**

### **Step 1: Sign Up & Connect GitHub**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repositories

### **Step 2: Create Web Service**
1. **Click "New +"** → **Web Service**
2. **Connect Repository**: `rprovine/tourism-analytics-platform`
3. **Fill in details**:
   - **Name**: `tourism-analytics-platform`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: `Python 3`

### **Step 3: Configure Build & Deploy**
```
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### **Step 4: Environment Variables**
Add these in Render dashboard:
```
SECRET_KEY = your-32-character-secret-key
DEBUG = false
PROJECT_NAME = Tourism Analytics Platform - KoinTyme
```

**Generate SECRET_KEY:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### **Step 5: Deploy**
1. **Click "Create Web Service"**
2. **Wait for deployment** (2-3 minutes)
3. **Your app will be live** at: `https://your-app.onrender.com`

## 🗄️ **Add Databases (After App Works)**

### **PostgreSQL Database**
1. **New +** → **PostgreSQL**
2. **Name**: `tourism-analytics-db`
3. **Plan**: Free tier is fine for demo
4. **Create Database**
5. **Copy connection URL**
6. **Add to Web Service** environment variables:
   ```
   DATABASE_URL = [paste the connection URL]
   ```

### **Redis Database**
1. **New +** → **Redis**
2. **Name**: `tourism-analytics-redis`
3. **Plan**: Free tier
4. **Create**
5. **Copy connection URL**
6. **Add to Web Service**:
   ```
   REDIS_URL = [paste the connection URL]
   ```

### **Redeploy with Databases**
1. Go to your **Web Service**
2. **Manual Deploy** → **Deploy latest commit**
3. **Wait for deployment**

## ✅ **Expected Results**

After deployment, visit:
- **Landing Page**: `https://your-app.onrender.com`
- **Health Check**: `https://your-app.onrender.com/health`
- **API Docs**: `https://your-app.onrender.com/docs`

## 🎯 **Why Render > Railway**

✅ **Better FastAPI support**  
✅ **More reliable database connections**  
✅ **Clearer deployment logs**  
✅ **Free tier includes databases**  
✅ **Easier environment variable management**

## 🔧 **Troubleshooting**

### **If deployment fails:**
1. **Check build logs** in Render dashboard
2. **Verify requirements.txt** is in root directory
3. **Check environment variables** are set correctly

### **If app starts but shows errors:**
1. **Add databases** (PostgreSQL + Redis)
2. **Redeploy** after adding databases
3. **Check application logs** for specific errors

---

**🚀 Render.com should deploy your Tourism Analytics Platform successfully!**

*KoinTyme platforms work best on reliable infrastructure.*