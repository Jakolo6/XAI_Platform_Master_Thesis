#!/bin/bash

echo "🔍 XAI Platform Quick Health Check"
echo "===================================="
echo ""

# 1. Backend Health
echo "1️⃣ Backend Health Check:"
curl -s https://xaiplatformmasterthesis-production.up.railway.app/health
echo ""
echo ""

# 2. Datasets Endpoint
echo "2️⃣ Datasets Endpoint:"
curl -s https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/ | head -c 200
echo "..."
echo ""
echo ""

# 3. CORS Check
echo "3️⃣ CORS Headers Check:"
curl -s -X OPTIONS \
  -H "Origin: https://xai-working-project.netlify.app" \
  -H "Access-Control-Request-Method: POST" \
  -I https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/ 2>&1 \
  | grep -i "access-control"
echo ""

echo "===================================="
echo "✅ Health Check Complete!"
echo ""
echo "Next steps:"
echo "1. Check Railway logs for any errors"
echo "2. Test frontend at: https://xai-working-project.netlify.app"
echo "3. See SYSTEM_HEALTH_CHECK.md for detailed tests"
