# Vercel Custom Domain Setup for Tourism Analytics Platform

## Overview
This configuration sets up analytics.lenilani.com to proxy to your Streamlit app at tourism-analytics-platform.streamlit.app

## IMPORTANT: Make Deployment Public

The deployment is currently behind authentication. To make it public:

### Via Vercel Dashboard (Recommended):
1. Go to: https://vercel.com/rprovines-projects/tourism-analytics-platform/settings
2. Navigate to "Deployment Protection" 
3. Change from "Only members of rprovines-projects" to "Public"
4. Save changes

### Via CLI:
```bash
vercel --prod --public
```

## Setup Instructions

### 1. Deploy to Vercel
```bash
# Install Vercel CLI if you haven't already
npm i -g vercel

# Deploy the project
vercel --prod --public
```

### 2. Configure Custom Domain
1. Go to your Vercel project settings: https://vercel.com/rprovines-projects/tourism-analytics-platform/settings/domains
2. Click "Add Domain"
3. Enter `analytics.lenilani.com`
4. Vercel will provide DNS records to add to your domain provider

### 3. DNS Configuration
Add the following records to your domain DNS (lenilani.com):

**For subdomain (recommended):**
- Type: CNAME
- Name: analytics
- Value: cname.vercel-dns.com

**OR for A record:**
- Type: A
- Name: analytics
- Value: 76.76.21.21

### 4. Verify Domain
Once DNS propagates (usually within a few minutes to 48 hours):
- Visit https://analytics.lenilani.com
- It should display your Tourism Analytics Platform

## Current Deployment
- **Vercel URL**: https://tourism-analytics-platform-rprovines-projects.vercel.app
- **Target App**: https://tourism-analytics-platform.streamlit.app
- **Status**: Requires authentication (needs to be made public)

## How It Works
- The `vercel.json` file contains rewrite rules that proxy all requests to the Streamlit app
- The `public/index.html` provides a fallback redirect page
- No server code is needed - Vercel handles the proxying automatically

## Files
- `vercel.json` - Vercel configuration with rewrite rules
- `package.json` - Project metadata for Vercel deployment
- `public/index.html` - Fallback redirect page

## Troubleshooting
- **Authentication Required**: Make sure to set deployment to "Public" in Vercel settings
- If the domain doesn't work immediately, DNS propagation can take up to 48 hours
- Check Vercel dashboard for domain verification status
- Ensure your DNS records match exactly what Vercel provides