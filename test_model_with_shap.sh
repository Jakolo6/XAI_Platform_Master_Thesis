#!/bin/bash

echo "🚀 Testing Model Training with Auto-SHAP Generation"
echo "===================================================="
echo ""

# Wait for Railway deployment
echo "⏳ Waiting 60 seconds for Railway to deploy..."
sleep 60

BASE_URL="https://xaiplatformmasterthesis-production.up.railway.app/api/v1"

# Train a new model
echo "1️⃣ Training new model on german-credit dataset..."
TRAIN_RESPONSE=$(curl -s -X POST "$BASE_URL/models/train" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "german-credit",
    "model_type": "xgboost"
  }')

echo "$TRAIN_RESPONSE" | python3 -m json.tool
echo ""

# Wait for training
echo "⏳ Waiting 90 seconds for training and SHAP generation..."
sleep 90

# Check for new models
echo ""
echo "2️⃣ Checking models for german-credit..."
MODELS=$(curl -s "$BASE_URL/models/dataset/german-credit")
echo "$MODELS" | python3 -m json.tool | head -50
echo ""

# Extract model ID
MODEL_ID=$(echo "$MODELS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['id'] if data else '')" 2>/dev/null)

if [ -n "$MODEL_ID" ]; then
    echo "3️⃣ Checking explanations for model: $MODEL_ID"
    EXPLANATIONS=$(curl -s "$BASE_URL/explanations/model/$MODEL_ID")
    echo "$EXPLANATIONS" | python3 -m json.tool
    echo ""
    
    if [ "$(echo "$EXPLANATIONS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")" -gt 0 ]; then
        echo "✅ SUCCESS! SHAP explanation was auto-generated!"
    else
        echo "⚠️  No explanations found yet. Check Railway logs."
    fi
else
    echo "⚠️  No models found. Training may still be in progress."
fi

echo ""
echo "To manually check explanations later:"
echo "curl $BASE_URL/explanations/model/\$MODEL_ID | python3 -m json.tool"
