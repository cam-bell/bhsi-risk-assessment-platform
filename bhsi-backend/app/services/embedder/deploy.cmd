@echo off
echo Building and deploying embedder service...

echo Step 1: Building Docker image...
gcloud builds submit --tag gcr.io/solid-topic-443216-b2/embedder-service .

if errorlevel 1 (
    echo Build failed!
    exit /b 1
)

echo Step 2: Deploying to Cloud Run...
gcloud run deploy embedder-service ^
    --image gcr.io/solid-topic-443216-b2/embedder-service ^
    --region europe-west1 ^
    --platform managed ^
    --allow-unauthenticated ^
    --memory 512Mi ^
    --cpu 1 ^
    --timeout 300 ^
    --max-instances 10 ^
    --update-env-vars GOOGLE_API_KEY=AIzaSyA3TisG5sHeIUpO61dygoF7r_ntWbmUdas,PROJECT_ID=solid-topic-443216-b2,LOCATION=europe-west1,ENDPOINT_ID=1947305461535473664

if errorlevel 1 (
    echo Deployment failed!
    exit /b 1
)

echo Step 3: Testing deployment...
echo Waiting 10 seconds for service to start...
timeout /t 10 /nobreak > nul

echo Testing health endpoint...
curl -f https://embedder-service-YOUR_HASH-ew.a.run.app/health

echo Deployment complete!
echo Update the URL above with your actual Cloud Run service URL 