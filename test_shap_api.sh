#!/bin/bash

echo "🧪 Testing SHAP API Endpoint"
echo "=============================="
echo ""

# Get auth token
echo "1. Getting authentication token..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"researcher@xai.com","password":"research123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get token. Is the backend running?"
  exit 1
fi

echo "✅ Token obtained"
echo ""

# Get XGBoost model ID
echo "2. Getting XGBoost model ID..."
MODEL_ID=$(curl -s http://localhost:8000/api/v1/models/leaderboard/performance \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "import sys, json; models = json.load(sys.stdin); xgb = [m for m in models if m['model_type'] == 'xgboost']; print(xgb[0]['model_id'] if xgb else '')" 2>/dev/null)

if [ -z "$MODEL_ID" ]; then
  echo "❌ Failed to get XGBoost model ID"
  exit 1
fi

echo "✅ Model ID: $MODEL_ID"
echo ""

# Generate explanation
echo "3. Generating SHAP explanation..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/explanations/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"model_id\": \"$MODEL_ID\",
    \"method\": \"shap\",
    \"config\": {}
  }")

EXPLANATION_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ -z "$EXPLANATION_ID" ]; then
  echo "❌ Failed to generate explanation"
  echo "Response: $RESPONSE"
  exit 1
fi

echo "✅ Explanation ID: $EXPLANATION_ID"
echo ""

# Poll for completion
echo "4. Waiting for explanation to complete..."
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
  sleep 2
  ATTEMPT=$((ATTEMPT + 1))
  
  STATUS=$(curl -s http://localhost:8000/api/v1/explanations/$EXPLANATION_ID \
    -H "Authorization: Bearer $TOKEN" | \
    python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null)
  
  echo "   Attempt $ATTEMPT/$MAX_ATTEMPTS - Status: $STATUS"
  
  if [ "$STATUS" = "completed" ]; then
    echo ""
    echo "✅ Explanation completed successfully!"
    echo ""
    
    # Get top features
    echo "5. Top 5 Features:"
    curl -s http://localhost:8000/api/v1/explanations/$EXPLANATION_ID \
      -H "Authorization: Bearer $TOKEN" | \
      python3 -c "
import sys, json
data = json.load(sys.stdin)
result = json.loads(data.get('result', '{}'))
features = result.get('feature_importance', [])[:5]
for i, f in enumerate(features, 1):
    print(f\"   {i}. {f['feature']}: {f['importance']:.4f}\")
" 2>/dev/null
    
    echo ""
    echo "🎉 SHAP API is working perfectly!"
    echo ""
    echo "Now go to: http://localhost:3000"
    echo "1. Login (researcher@xai.com / research123)"
    echo "2. Click XGBoost model"
    echo "3. Click 'Generate SHAP Explanation'"
    echo "4. View the beautiful charts!"
    exit 0
  fi
  
  if [ "$STATUS" = "failed" ]; then
    echo ""
    echo "❌ Explanation failed"
    exit 1
  fi
done

echo ""
echo "⏱️  Timeout waiting for explanation"
echo "Check Flower dashboard: http://localhost:5555"
