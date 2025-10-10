#!/bin/bash

echo "==================================="
echo "Quick SHAP Debug"
echo "==================================="

# Login
echo -e "\n🔐 Logging in..."
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"researcher@xai.com","password":"research123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  exit 1
fi

echo "✅ Logged in"

# Get first model
echo -e "\n📊 Getting models..."
MODEL_ID=$(curl -s "http://localhost:8000/api/v1/models" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)[0]['id'])")

echo "✅ Model ID: $MODEL_ID"

# Generate SHAP
echo -e "\n🔮 Generating SHAP..."
START_TIME=$(date +%s)

RESULT=$(curl -s -X POST "http://localhost:8000/api/v1/explanations/generate?model_id=$MODEL_ID&method=shap" \
  -H "Authorization: Bearer $TOKEN")

EXPLANATION_ID=$(echo $RESULT | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")

if [ -z "$EXPLANATION_ID" ]; then
  echo "❌ Failed to start SHAP"
  echo "$RESULT"
  exit 1
fi

echo "✅ Task started: $EXPLANATION_ID"

# Poll for completion
echo -e "\n⏳ Waiting for completion..."
for i in {1..30}; do
  sleep 2
  STATUS=$(curl -s "http://localhost:8000/api/v1/explanations/$EXPLANATION_ID" \
    -H "Authorization: Bearer $TOKEN" \
    | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))")
  
  ELAPSED=$(($(date +%s) - START_TIME))
  echo "  [${ELAPSED}s] Status: $STATUS"
  
  if [ "$STATUS" = "completed" ]; then
    echo -e "\n✅ SHAP completed in ${ELAPSED}s!"
    exit 0
  elif [ "$STATUS" = "failed" ]; then
    echo -e "\n❌ SHAP failed!"
    exit 1
  fi
done

echo -e "\n⏰ Timeout after 60s"
echo -e "\n💡 Check Celery worker logs:"
echo "   docker-compose logs celery_worker --tail=100"
