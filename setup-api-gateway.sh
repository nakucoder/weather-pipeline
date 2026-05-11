#!/bin/bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

API_ID="nj6nmdc5ge"
ROOT_RESOURCE_ID="7kijnnwu3k"
REGION="us-east-2"
ACCOUNT_ID="275928090561"
LAMBDA_NAME="miami-weather-lambda"
LAMBDA_ARN="arn:aws:lambda:us-east-2:275928090561:function:miami-weather-lambda"

# ── Step 1: Create /weather resource ─────────────────────────────────────────
echo "=== Step 1: Create /weather resource ==="
WEATHER_RESOURCE_ID=$(aws apigateway create-resource \
  --rest-api-id "$API_ID" \
  --parent-id "$ROOT_RESOURCE_ID" \
  --path-part weather \
  --region "$REGION" \
  --query "id" \
  --output text)
echo "Resource ID: $WEATHER_RESOURCE_ID"

# ── Step 2: Create GET method (no auth) ──────────────────────────────────────
echo ""
echo "=== Step 2: Create GET method ==="
aws apigateway put-method \
  --rest-api-id "$API_ID" \
  --resource-id "$WEATHER_RESOURCE_ID" \
  --http-method GET \
  --authorization-type NONE \
  --region "$REGION"
echo "Done."

# ── Step 3: Lambda proxy integration ─────────────────────────────────────────
echo ""
echo "=== Step 3: Set up Lambda proxy integration ==="
aws apigateway put-integration \
  --rest-api-id "$API_ID" \
  --resource-id "$WEATHER_RESOURCE_ID" \
  --http-method GET \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/${LAMBDA_ARN}/invocations" \
  --region "$REGION"
echo "Done."

# ── Step 4: Grant API Gateway permission to invoke Lambda ─────────────────────
echo ""
echo "=== Step 4: Grant invoke permission to API Gateway ==="
aws lambda add-permission \
  --function-name "$LAMBDA_NAME" \
  --statement-id "apigateway-prod-weather" \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/GET/weather" \
  --region "$REGION"
echo "Done."

# ── Step 5: Deploy to prod stage ──────────────────────────────────────────────
echo ""
echo "=== Step 5: Deploy to prod stage ==="
aws apigateway create-deployment \
  --rest-api-id "$API_ID" \
  --stage-name prod \
  --region "$REGION"
echo "Done."

# ── Final URL ─────────────────────────────────────────────────────────────────
echo ""
echo "=== Invoke URL ==="
echo "https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod/weather"
