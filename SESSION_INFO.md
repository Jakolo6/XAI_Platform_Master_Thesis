# Session Information

## User Credentials
- **Email:** researcher@xai.com
- **Password:** research123
- **User ID:** b0b71f72-90d5-47d3-b43a-5342bf7916f3

## Access Token
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiMGI3MWY3Mi05MGQ1LTQ3ZDMtYjQzYS01MzQyYmY3OTE2ZjMiLCJlbWFpbCI6InJlc2VhcmNoZXJAeGFpLmNvbSIsImV4cCI6MTc1OTkzNTMyMywidHlwZSI6ImFjY2VzcyJ9.a0vss-CR3bZhw199iRzEj87AWewxLGiH0ErPaJoxOc4
```

## Dataset Information
- **Dataset ID:** 3794c993-fac2-4063-aa61-cb882d6c0291
- **Task ID:** 58bcdcdd-96ab-4e82-876d-3bed7a4cb121
- **Status:** Downloading
- **Name:** IEEE-CIS Fraud Detection

## Quick Commands

### Check Dataset Status
```bash
curl http://localhost:8000/api/v1/datasets/3794c993-fac2-4063-aa61-cb882d6c0291 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiMGI3MWY3Mi05MGQ1LTQ3ZDMtYjQzYS01MzQyYmY3OTE2ZjMiLCJlbWFpbCI6InJlc2VhcmNoZXJAeGFpLmNvbSIsImV4cCI6MTc1OTkzNTMyMywidHlwZSI6ImFjY2VzcyJ9.a0vss-CR3bZhw199iRzEj87AWewxLGiH0ErPaJoxOc4"
```

### Preprocess Dataset (after download completes)
```bash
curl -X POST http://localhost:8000/api/v1/datasets/3794c993-fac2-4063-aa61-cb882d6c0291/preprocess \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiMGI3MWY3Mi05MGQ1LTQ3ZDMtYjQzYS01MzQyYmY3OTE2ZjMiLCJlbWFpbCI6InJlc2VhcmNoZXJAeGFpLmNvbSIsImV4cCI6MTc1OTkzNTMyMywidHlwZSI6ImFjY2VzcyJ9.a0vss-CR3bZhw199iRzEj87AWewxLGiH0ErPaJoxOc4"
```

### Train XGBoost Model (after preprocessing completes)
```bash
curl -X POST http://localhost:8000/api/v1/models/train \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiMGI3MWY3Mi05MGQ1LTQ3ZDMtYjQzYS01MzQyYmY3OTE2ZjMiLCJlbWFpbCI6InJlc2VhcmNoZXJAeGFpLmNvbSIsImV4cCI6MTc1OTkzNTMyMywidHlwZSI6ImFjY2VzcyJ9.a0vss-CR3bZhw199iRzEj87AWewxLGiH0ErPaJoxOc4" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "XGBoost Fraud Detector v1",
    "model_type": "xgboost",
    "dataset_id": "3794c993-fac2-4063-aa61-cb882d6c0291",
    "optimize": false
  }'
```

## Monitoring

- **Flower (Celery Tasks):** http://localhost:5555
- **API Docs:** http://localhost:8000/api/v1/docs
- **Logs:** `docker-compose logs -f celery_worker`
