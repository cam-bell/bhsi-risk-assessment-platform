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
REGION="europe-west1"
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

# Set GitHub secrets (only the essential ones)
gh secret set GCP_SERVICE_ACCOUNT_KEY --body "$SERVICE_ACCOUNT_KEY"
gh secret set GCP_PROJECT_ID --body "$PROJECT_ID"
gh secret set GCP_REGION --body "$REGION"

echo "📝 Optional: Set Gemini API Key if you want to override the default:"
echo "gh secret set GEMINI_API_KEY --body 'your-gemini-api-key'"
echo ""
echo "🎉 Setup complete! The project is ready for deployment."
echo ""
echo "✅ All required configuration is already hardcoded:"
echo "- NewsAPI Key: d191eaacfc0c47118a582d23e35e9c63"
echo "- BigQuery Project: solid-topic-443216-b2"
echo "- BigQuery Dataset: risk_monitoring"
echo "- JWT Secret: your-secret-key-change-in-production"
echo "- All Cloud Service URLs"
echo ""
echo "🚀 Deploy by pushing to the backend-deploy branch:"
echo "git push origin backend-deploy" 