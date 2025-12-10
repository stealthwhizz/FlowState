# FlowState S3 Deployment Script (PowerShell)
# Deploys to AWS S3 static website hosting in ap-south-1 (India)

param(
    [string]$BucketName = "flowstate-stealthwhizz",
    [string]$Region = "ap-south-1"
)

$ErrorActionPreference = "Stop"

# Configuration
$WebsiteUrl = "http://$BucketName.s3-website.$Region.amazonaws.com"

Write-Host "🚀 Starting FlowState deployment to S3..." -ForegroundColor Green
Write-Host "Bucket: $BucketName" -ForegroundColor Cyan
Write-Host "Region: $Region" -ForegroundColor Cyan

# Check if AWS CLI is installed and configured
Write-Host "📋 Checking AWS CLI configuration..." -ForegroundColor Yellow

try {
    $null = Get-Command aws -ErrorAction Stop
    Write-Host "✅ AWS CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html" -ForegroundColor Yellow
    exit 1
}

try {
    aws sts get-caller-identity --output json | Out-Null
    Write-Host "✅ AWS CLI is configured" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI is not configured. Please run 'aws configure' first." -ForegroundColor Red
    exit 1
}

# Build the project
Write-Host "🔨 Building production version..." -ForegroundColor Yellow
npm run build

if (-not (Test-Path "dist")) {
    Write-Host "❌ Build failed - dist/ directory not found" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build completed" -ForegroundColor Green

# Check if bucket exists, create if it doesn't
Write-Host "🪣 Checking if S3 bucket exists..." -ForegroundColor Yellow

try {
    aws s3api head-bucket --bucket $BucketName --region $Region 2>$null
    Write-Host "✅ Bucket $BucketName already exists" -ForegroundColor Green
} catch {
    Write-Host "📦 Creating S3 bucket: $BucketName" -ForegroundColor Yellow
    aws s3api create-bucket --bucket $BucketName --region $Region --create-bucket-configuration LocationConstraint=$Region
    Write-Host "✅ Bucket created successfully" -ForegroundColor Green
}

# Upload files to S3
Write-Host "📤 Uploading files to S3..." -ForegroundColor Yellow

# Upload static assets with long cache
aws s3 sync dist/ s3://$BucketName/ --region $Region --delete --cache-control "public, max-age=31536000" --exclude "*.html" --exclude "*.json"

# Upload HTML and JSON files with no-cache
aws s3 sync dist/ s3://$BucketName/ --region $Region --delete --cache-control "no-cache" --include "*.html" --include "*.json"

Write-Host "✅ Files uploaded successfully" -ForegroundColor Green

# Configure static website hosting
Write-Host "🌐 Configuring static website hosting..." -ForegroundColor Yellow
aws s3 website s3://$BucketName/ --index-document index.html --error-document index.html --region $Region
Write-Host "✅ Website hosting configured" -ForegroundColor Green

# Set bucket policy for public read access
Write-Host "🔓 Setting public read policy..." -ForegroundColor Yellow

$Policy = @"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BucketName/*"
        }
    ]
}
"@

$Policy | aws s3api put-bucket-policy --bucket $BucketName --policy file:///dev/stdin --region $Region
Write-Host "✅ Public read policy applied" -ForegroundColor Green

# Disable block public access (required for website hosting)
Write-Host "🔧 Configuring public access settings..." -ForegroundColor Yellow
aws s3api put-public-access-block --bucket $BucketName --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" --region $Region
Write-Host "✅ Public access configured" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Your FlowState dashboard is now live at:" -ForegroundColor Cyan
Write-Host "   $WebsiteUrl" -ForegroundColor White
Write-Host ""
Write-Host "🔗 You can also access it via:" -ForegroundColor Cyan
Write-Host "   https://$BucketName.s3.$Region.amazonaws.com/index.html" -ForegroundColor White
Write-Host ""