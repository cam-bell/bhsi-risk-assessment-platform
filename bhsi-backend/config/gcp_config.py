from google.cloud import secretmanager
from google.cloud import storage
from google.cloud import aiplatform
import os

# GCP Project Configuration

PROJECT_ID = "solid-topic-443216-b2"  # Replace with your GCP project ID
REGION = "europe-west1"

# Cloud SQL Configuration
DB_INSTANCE = "bhsi-db"
DB_NAME = "bhsi_db"
DB_USER = "postgres"

# Cloud Storage Configuration
BUCKET_NAME = "bhsi-storage"

# Vertex AI Configuration
VERTEX_AI_LOCATION = "us-central1"  # Updated to match Gemini endpoint region
GEMINI_ENDPOINT_ID = "5541306607037579264"  # Your newly created endpoint ID

def get_secret(secret_id):
    """Retrieve a secret from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def init_vertex_ai():
    """Initialize Vertex AI."""
    aiplatform.init(project=PROJECT_ID, location=VERTEX_AI_LOCATION)

def get_storage_client():
    """Get Cloud Storage client."""
    return storage.Client(project=PROJECT_ID)

def get_bucket():
    """Get Cloud Storage bucket."""
    client = get_storage_client()
    return client.bucket(BUCKET_NAME) 