@echo off
echo Building and deploying Gemini LLM service...

echo Step 1: Building Docker image...
gcloud builds submit --tag gcr.io/solid-topic-443216-b2/gemini-service .

if errorlevel 1 (
    echo Build failed!
    exit /b 1
)

echo Step 2: Deploying to Cloud Run...
gcloud run deploy gemini-service ^
    --image gcr.io/solid-topic-443216-b2/gemini-service ^
    --region europe-west1 ^
    --platform managed ^
    --allow-unauthenticated ^
    --memory 1Gi ^
    --cpu 1 ^
    --timeout 300 ^
    --max-instances 10 ^
    --update-env-vars GOOGLE_API_KEY=AIzaSyA3TisG5sHeIUpO61dygoF7r_ntWbmUdas,PROJECT_ID=solid-topic-443216-b2,LOCATION=europe-west1

if errorlevel 1 (
    echo Deployment failed!
    exit /b 1
)

echo Step 3: Testing deployment...
echo Waiting 15 seconds for service to start...
timeout /t 15 /nobreak > nul

echo Testing health endpoint...
echo Note: Update URL below with your actual Cloud Run service URL
echo curl https://gemini-service-YOUR_HASH-ew.a.run.app/health

echo Deployment complete!
echo Update the URL above with your actual Cloud Run service URL 