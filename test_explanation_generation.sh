#!/bin/bash

# Test Explanation Generation
# This script tests the SHAP/LIME explanation generation endpoint

BASE_URL="https://xaiplatformmasterthesis-production.up.railway.app/api/v1"
MODEL_ID="ieee-cis-fraud_xgboost_413d3682"

echo "🧪 Testing Explanation Generation"
echo "=================================="
echo ""

# Test 1: Generate SHAP explanation
echo "1️⃣ Generating SHAP explanation..."
SHAP_RESPONSE=$(curl -s -X POST "$BASE_URL/explanations/generate" \
  -H "Content-Type: application/json" \
  -d "{
    \"model_id\": \"$MODEL_ID\",
    \"method\": \"shap\",
    \"sample_size\": 50
  }")

echo "Response:"
echo "$SHAP_RESPONSE" | python3 -m json.tool
echo ""

# Wait a bit for processing
echo "⏳ Waiting 30 seconds for SHAP generation..."
sleep 30

# Test 2: Check explanations for model
echo ""
echo "2️⃣ Checking explanations for model..."
EXPLANATIONS=$(curl -s "$BASE_URL/explanations/model/$MODEL_ID")
echo "$EXPLANATIONS" | python3 -m json.tool
echo ""

# Test 3: Generate LIME explanation
echo "3️⃣ Generating LIME explanation..."
LIME_RESPONSE=$(curl -s -X POST "$BASE_URL/explanations/generate" \
  -H "Content-Type: application/json" \
  -d "{
    \"model_id\": \"$MODEL_ID\",
    \"method\": \"lime\",
    \"sample_size\": 50
  }")

echo "Response:"
echo "$LIME_RESPONSE" | python3 -m json.tool
echo ""

echo "✅ Test complete! Check Railway logs for detailed processing status."
echo ""
echo "To check explanations later, run:"
echo "curl $BASE_URL/explanations/model/$MODEL_ID | python3 -m json.tool"
