#!/bin/bash

# BHSI Google Cloud Deployment Setup Script
# This script sets up all necessary GCP resources and GitHub secrets for deployment

set -e

echo "🚀 Setting up BHSI Google Cloud Deployment..."

# Check if required tools are installed
command -v gcloud >/dev/null 2>&1 || { echo "❌ gcloud CLI is required but not installed. Please install it first."; exit 1; }
command -v gh >/dev/null 2>&1 || { echo "❌ GitHub CLI is required but not installed. Please install it first."; exit 1; }

# Configuration variables
PROJECT_ID=""
REGION="us-central1"
SERVICE_ACCOUNT_NAME="bhsi-deployer"
REPOSITORY_NAME="bhsi"

# Get project ID
read -p "Enter your Google Cloud Project ID: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Project ID is required"
    exit 1
fi

echo "📋 Setting up project: $PROJECT_ID in region: $REGION"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable bigqueryconnection.googleapis.com

# Create Artifact Registry repository
echo "📦 Creating Artifact Registry repository..."
gcloud artifacts repositories create bhsi \
    --repository-format=docker \
    --location=$REGION \
    --description="BHSI Docker images"

# Create service account
echo "👤 Creating service account..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name="BHSI Deployment Service Account" \
    --description="Service account for BHSI deployment"

# Grant necessary permissions
echo "🔐 Granting permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Create and download service account key
echo "🔑 Creating service account key..."
gcloud iam service-accounts keys create bhsi-deployer-key.json \
    --iam-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com

# Get the service account key content
SERVICE_ACCOUNT_KEY=$(cat bhsi-deployer-key.json)

# Clean up the key file
rm bhsi-deployer-key.json

echo "🔐 Setting up GitHub secrets..."

# Set GitHub secrets
gh secret set GCP_SERVICE_ACCOUNT_KEY --body "$SERVICE_ACCOUNT_KEY"
gh secret set GCP_PROJECT_ID --body "$PROJECT_ID"
gh secret set GCP_REGION --body "$REGION"

echo "📝 Please set the following secrets manually in your GitHub repository:"
echo ""
echo "Required API Keys:"
echo "- OPENAI_API_KEY: Your OpenAI API key"
echo "- GEMINI_API_KEY: Your Google Gemini API key"
echo "- GOOGLE_API_KEY: Your Google Custom Search API key"
echo "- GOOGLE_CX: Your Google Custom Search Engine ID"
echo ""
echo "Database Configuration:"
echo "- DATABASE_URL: Your database connection string"
echo "- SECRET_KEY: A secure secret key for JWT tokens"
echo "- ALGORITHM: JWT algorithm (e.g., HS256)"
echo "- ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time"
echo ""
echo "BigQuery Configuration:"
echo "- BIGQUERY_PROJECT_ID: $PROJECT_ID"
echo "- BIGQUERY_DATASET: Your BigQuery dataset name"
echo "- BIGQUERY_LOCATION: $REGION"
echo ""
echo "Application Configuration:"
echo "- ALLOWED_DOMAINS: Comma-separated list of allowed domains"
echo "- MAX_SCRAPE_PAGES: Maximum pages to scrape (e.g., 10)"
echo "- API_KEY_HEADER: Header name for API key (e.g., X-API-Key)"
echo "- RATE_LIMIT_PER_MINUTE: Rate limit per minute (e.g., 60)"
echo "- OPENAI_MODEL: OpenAI model name (e.g., gpt-4)"
echo ""
echo "Frontend Configuration:"
echo "- VITE_API_BASE_URL: Your backend API URL"
echo ""
echo "🎉 Setup complete! You can now deploy by pushing to the backend-deploy branch."
echo ""
echo "To set secrets via command line, use:"
echo "gh secret set SECRET_NAME --body 'SECRET_VALUE'" 