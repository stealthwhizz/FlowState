@echo off
REM FlowState S3 Deployment Script (Windows Batch)
REM Deploys to AWS S3 static website hosting in ap-south-1 (India)

set BUCKET_NAME=flowstate-stealthwhizz
set REGION=ap-south-1
set WEBSITE_URL=http://%BUCKET_NAME%.s3-website.%REGION%.amazonaws.com

echo 🚀 Starting FlowState deployment to S3...
echo Bucket: %BUCKET_NAME%
echo Region: %REGION%

REM Check if AWS CLI is available
aws --version >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS CLI is not installed. Please install it first.
    echo    https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
    pause
    exit /b 1
)

REM Check AWS configuration
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS CLI is not configured. Please run 'aws configure' first.
    pause
    exit /b 1
)

echo ✅ AWS CLI is configured

REM Build the project
echo 🔨 Building production version...
call npm run build

if not exist "dist" (
    echo ❌ Build failed - dist/ directory not found
    pause
    exit /b 1
)

echo ✅ Build completed

REM Create bucket (ignore error if exists)
echo 📦 Creating S3 bucket (if needed)...
aws s3api create-bucket --bucket %BUCKET_NAME% --region %REGION% --create-bucket-configuration LocationConstraint=%REGION% 2>nul

REM Upload files
echo 📤 Uploading files to S3...
aws s3 sync dist/ s3://%BUCKET_NAME%/ --region %REGION% --delete

REM Configure website hosting
echo 🌐 Configuring static website hosting...
aws s3 website s3://%BUCKET_NAME%/ --index-document index.html --error-document index.html --region %REGION%

REM Set public read policy
echo 🔓 Setting public read policy...
echo {"Version":"2012-10-17","Statement":[{"Sid":"PublicReadGetObject","Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::%BUCKET_NAME%/*"}]} > temp_policy.json
aws s3api put-bucket-policy --bucket %BUCKET_NAME% --policy file://temp_policy.json --region %REGION%
del temp_policy.json

REM Configure public access
echo 🔧 Configuring public access settings...
aws s3api put-public-access-block --bucket %BUCKET_NAME% --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" --region %REGION%

echo.
echo 🎉 Deployment completed successfully!
echo.
echo 📍 Your FlowState dashboard is now live at:
echo    %WEBSITE_URL%
echo.
pause