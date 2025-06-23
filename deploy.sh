#!/bin/bash

# Tourism Analytics Platform - Quick Deploy Script
# Engineered by KoinTyme

echo "🌺 Tourism Analytics Platform - Deployment Script"
echo "🚀 Engineered by KoinTyme"
echo "=================================================="

# Check if deployment target is provided
if [ -z "$1" ]; then
    echo "Usage: ./deploy.sh [digitalocean|railway|heroku|aws]"
    echo ""
    echo "Available options:"
    echo "  digitalocean  - Deploy to DigitalOcean App Platform"
    echo "  railway       - Deploy to Railway"
    echo "  heroku        - Deploy to Heroku"
    echo "  aws           - Deploy to AWS ECS"
    exit 1
fi

DEPLOY_TARGET=$1

case $DEPLOY_TARGET in
    "digitalocean")
        echo "🔵 Deploying to DigitalOcean App Platform..."
        echo "1. Go to: https://cloud.digitalocean.com/apps"
        echo "2. Click 'Create App'"
        echo "3. Connect GitHub repo: rprovine/tourism-analytics-platform"
        echo "4. Use configuration from .do/deploy.template.yaml"
        echo "5. Add PostgreSQL and Redis databases"
        echo "6. Set environment variables"
        echo "7. Deploy!"
        echo ""
        echo "📖 Full guide: ./DEPLOYMENT.md"
        ;;
    
    "railway")
        echo "🚂 Deploying to Railway..."
        if ! command -v railway &> /dev/null; then
            echo "Installing Railway CLI..."
            npm install -g @railway/cli
        fi
        
        echo "Logging into Railway..."
        railway login
        
        echo "Initializing project..."
        railway init
        
        echo "Deploying..."
        railway up
        
        echo "Adding databases..."
        railway add postgresql
        railway add redis
        
        echo "✅ Deployment initiated! Set environment variables in Railway dashboard."
        ;;
    
    "heroku")
        echo "🟣 Deploying to Heroku..."
        if ! command -v heroku &> /dev/null; then
            echo "Please install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli"
            exit 1
        fi
        
        heroku create tourism-analytics-$(date +%s)
        heroku container:login
        heroku container:push web
        heroku container:release web
        heroku addons:create heroku-postgresql:mini
        heroku addons:create heroku-redis:mini
        
        echo "✅ Deployed to Heroku! Set environment variables with:"
        echo "heroku config:set SECRET_KEY=your-secret-key"
        ;;
    
    "aws")
        echo "🟠 AWS deployment requires manual setup."
        echo "📖 Follow the AWS guide in DEPLOYMENT.md"
        echo "Key steps:"
        echo "1. Create ECR repository"
        echo "2. Push Docker image"
        echo "3. Set up ECS cluster"
        echo "4. Configure RDS and ElastiCache"
        echo "5. Set up ALB and Route53"
        ;;
    
    *)
        echo "❌ Unknown deployment target: $DEPLOY_TARGET"
        echo "Available options: digitalocean, railway, heroku, aws"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment process started!"
echo "📞 Need help? Contact KoinTyme Support: support@kointyme.com"
echo "🌐 KoinTyme: https://kointyme.com"