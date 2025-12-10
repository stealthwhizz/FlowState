# FlowState S3 Deployment Script (Simple PowerShell)
# Deploys to AWS S3 static website hosting in ap-south-1 (India)

$BucketName = "flowstate-stealthwhizz"
$Region = "ap-south-1"
$WebsiteUrl = "http://$BucketName.s3-website.$Region.amazonaws.com"

Write-Host "Starting FlowState deployment to S3..." -ForegroundColor Green
Write-Host "Bucket: $BucketName" -ForegroundColor Cyan
Write-Host "Region: $Region" -ForegroundColor Cyan

# Check AWS CLI
Write-Host "Checking AWS CLI..." -ForegroundColor Yellow
try {
    aws sts get-caller-identity | Out-Null
    Write-Host "AWS CLI is configured" -ForegroundColor Green
} catch {
    Write-Host "AWS CLI is not configured. Please run 'aws configure' first." -ForegroundColor Red
    exit 1
}

# Build completed (already done by npm script)
Write-Host "Build completed" -ForegroundColor Green

# Create bucket (ignore error if exists)
Write-Host "Creating S3 bucket..." -ForegroundColor Yellow
aws s3api create-bucket --bucket $BucketName --region $Region --create-bucket-configuration LocationConstraint=$Region 2>$null

# Upload files
Write-Host "Uploading files to S3..." -ForegroundColor Yellow
aws s3 sync dist/ s3://$BucketName/ --region $Region --delete

# Configure website hosting
Write-Host "Configuring static website hosting..." -ForegroundColor Yellow
aws s3 website s3://$BucketName/ --index-document index.html --error-document index.html --region $Region

# Set public read policy
Write-Host "Setting public read policy..." -ForegroundColor Yellow
$PolicyJson = @"
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

$PolicyJson | aws s3api put-bucket-policy --bucket $BucketName --policy file:///dev/stdin --region $Region

# Configure public access
Write-Host "Configuring public access settings..." -ForegroundColor Yellow
aws s3api put-public-access-block --bucket $BucketName --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" --region $Region

Write-Host ""
Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Your FlowState dashboard is now live at:" -ForegroundColor Cyan
Write-Host $WebsiteUrl -ForegroundColor White
Write-Host ""