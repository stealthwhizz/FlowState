#!/bin/bash

# FlowState S3 Deployment Script
# Deploys to AWS S3 static website hosting in ap-south-1 (India)

set -e  # Exit on any error

# Configuration
BUCKET_NAME="flowstate-stealthwhizz"
REGION="ap-south-1"
WEBSITE_URL="http://${BUCKET_NAME}.s3-website.${REGION}.amazonaws.com"

echo "🚀 Starting FlowState deployment to S3..."
echo "Bucket: $BUCKET_NAME"
echo "Region: $REGION"

# Check if AWS CLI is installed and configured
echo "📋 Checking AWS CLI configuration..."
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI is configured"

# Build the project
echo "🔨 Building production version..."
npm run build

if [ ! -d "dist" ]; then
    echo "❌ Build failed - dist/ directory not found"
    exit 1
fi

echo "✅ Build completed"

# Check if bucket exists, create if it doesn't
echo "🪣 Checking if S3 bucket exists..."
if aws s3api head-bucket --bucket "$BUCKET_NAME" --region "$REGION" 2>/dev/null; then
    echo "✅ Bucket $BUCKET_NAME already exists"
else
    echo "📦 Creating S3 bucket: $BUCKET_NAME"
    aws s3api create-bucket \
        --bucket "$BUCKET_NAME" \
        --region "$REGION" \
        --create-bucket-configuration LocationConstraint="$REGION"
    echo "✅ Bucket created successfully"
fi

# Upload files to S3
echo "📤 Uploading files to S3..."
aws s3 sync dist/ s3://"$BUCKET_NAME"/ \
    --region "$REGION" \
    --delete \
    --cache-control "public, max-age=31536000" \
    --exclude "*.html" \
    --exclude "*.json"

# Upload HTML and JSON files with no-cache
aws s3 sync dist/ s3://"$BUCKET_NAME"/ \
    --region "$REGION" \
    --delete \
    --cache-control "no-cache" \
    --include "*.html" \
    --include "*.json"

echo "✅ Files uploaded successfully"

# Configure static website hosting
echo "🌐 Configuring static website hosting..."
aws s3 website s3://"$BUCKET_NAME"/ \
    --index-document index.html \
    --error-document index.html \
    --region "$REGION"

echo "✅ Website hosting configured"

# Set bucket policy for public read access
echo "🔓 Setting public read policy..."
POLICY='{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::'$BUCKET_NAME'/*"
        }
    ]
}'

echo "$POLICY" | aws s3api put-bucket-policy \
    --bucket "$BUCKET_NAME" \
    --policy file:///dev/stdin \
    --region "$REGION"

echo "✅ Public read policy applied"

# Disable block public access (required for website hosting)
echo "🔧 Configuring public access settings..."
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" \
    --region "$REGION"

echo "✅ Public access configured"

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📍 Your FlowState dashboard is now live at:"
echo "   $WEBSITE_URL"
echo ""
echo "🔗 You can also access it via:"
echo "   https://$BUCKET_NAME.s3.$REGION.amazonaws.com/index.html"
echo ""