# BHSI Deployment Setup Guide

This guide will help you set up automated deployment for both the backend and frontend of the BHSI project to Google Cloud Run.

## Prerequisites

1. **Google Cloud CLI** installed and authenticated
2. **GitHub CLI** installed and authenticated
3. **Docker** installed locally (for testing)

## Quick Setup

### 1. Run the Setup Script

```bash
chmod +x setup-gcp-deployment.sh
./setup-gcp-deployment.sh
```

This script will:

- Enable required Google Cloud APIs
- Create Artifact Registry repository
- Create service account with necessary permissions
- Set up GitHub secrets for GCP authentication

### 2. Set Required Secrets

After running the setup script, set these secrets in your GitHub repository:

#### API Keys

```bash
gh secret set OPENAI_API_KEY --body "your-openai-api-key"
gh secret set GEMINI_API_KEY --body "your-gemini-api-key"
gh secret set GOOGLE_API_KEY --body "your-google-custom-search-api-key"
gh secret set GOOGLE_CX --body "your-google-custom-search-engine-id"
```

#### Database Configuration

```bash
gh secret set DATABASE_URL --body "your-database-connection-string"
gh secret set SECRET_KEY --body "your-secure-secret-key"
gh secret set ALGORITHM --body "HS256"
gh secret set ACCESS_TOKEN_EXPIRE_MINUTES --body "30"
```

#### BigQuery Configuration

```bash
gh secret set BIGQUERY_PROJECT_ID --body "your-project-id"
gh secret set BIGQUERY_DATASET --body "bhsi_dataset"
gh secret set BIGQUERY_LOCATION --body "us-central1"
```

#### Application Configuration

```bash
gh secret set ALLOWED_DOMAINS --body "example.com,another-domain.com"
gh secret set MAX_SCRAPE_PAGES --body "10"
gh secret set API_KEY_HEADER --body "X-API-Key"
gh secret set RATE_LIMIT_PER_MINUTE --body "60"
gh secret set OPENAI_MODEL --body "gpt-4"
```

#### Frontend Configuration

```bash
gh secret set VITE_API_BASE_URL --body "https://your-backend-url.run.app"
```

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Enable Google Cloud APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable bigqueryconnection.googleapis.com
```

### 2. Create Artifact Registry

```bash
gcloud artifacts repositories create bhsi \
    --repository-format=docker \
    --location=us-central1 \
    --description="BHSI Docker images"
```

### 3. Create Service Account

```bash
gcloud iam service-accounts create bhsi-deployer \
    --display-name="BHSI Deployment Service Account"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:bhsi-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:bhsi-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:bhsi-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.admin"
```

### 4. Create Service Account Key

```bash
gcloud iam service-accounts keys create bhsi-deployer-key.json \
    --iam-account=bhsi-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## Deployment

### Backend Deployment

The backend will be deployed when you push to the `backend-deploy` branch. The workflow will:

1. Build the Docker image from `bhsi-backend/Dockerfile`
2. Push to Google Artifact Registry
3. Deploy to Cloud Run with all environment variables

### Frontend Deployment

The frontend will be deployed when you push to the `backend-deploy` branch. The workflow will:

1. Build the React application
2. Create a Docker image with nginx
3. Push to Google Artifact Registry
4. Deploy to Cloud Run

## Testing Locally

### Backend

```bash
cd bhsi-backend
docker build -t bhsi-backend .
docker run -p 8000:8000 bhsi-backend
```

### Frontend

```bash
cd bhsi-frontend
npm install
npm run build
# Serve the dist folder with a static server
```

## Environment Variables

### Backend Environment Variables

| Variable              | Description                    | Example            |
| --------------------- | ------------------------------ | ------------------ |
| `OPENAI_API_KEY`      | OpenAI API key                 | `sk-...`           |
| `GEMINI_API_KEY`      | Google Gemini API key          | `AIza...`          |
| `GOOGLE_API_KEY`      | Google Custom Search API key   | `AIza...`          |
| `GOOGLE_CX`           | Google Custom Search Engine ID | `123456789:abcdef` |
| `DATABASE_URL`        | Database connection string     | `postgresql://...` |
| `SECRET_KEY`          | JWT secret key                 | `your-secret-key`  |
| `BIGQUERY_PROJECT_ID` | BigQuery project ID            | `your-project-id`  |
| `BIGQUERY_DATASET`    | BigQuery dataset name          | `bhsi_dataset`     |
| `BIGQUERY_LOCATION`   | BigQuery location              | `us-central1`      |

### Frontend Environment Variables

| Variable            | Description     | Example                            |
| ------------------- | --------------- | ---------------------------------- |
| `VITE_API_BASE_URL` | Backend API URL | `https://bhsi-backend-xxx.run.app` |

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure the service account has the necessary roles
2. **Image Build Fails**: Check the Dockerfile and requirements.txt
3. **Environment Variables Missing**: Verify all secrets are set in GitHub
4. **BigQuery Connection Issues**: Check BigQuery permissions and dataset existence

### Debugging

1. Check GitHub Actions logs for detailed error messages
2. Verify Google Cloud Console for service status
3. Test locally with Docker before deploying

## Security Notes

- Never commit API keys or secrets to the repository
- Use GitHub secrets for all sensitive information
- Regularly rotate service account keys
- Monitor Cloud Run logs for any security issues

## Cost Optimization

- Cloud Run scales to zero when not in use
- BigQuery charges based on data processed
- Monitor usage in Google Cloud Console
- Set up billing alerts to avoid unexpected charges
