# API Documentation

**Version:** 0.1.0  
**Base URL:** `http://localhost:8000/api/v1`  
**Authentication:** JWT Bearer Token (for researchers)

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Datasets](#datasets)
3. [Models](#models)
4. [Explanations](#explanations)
5. [Human Study](#human-study)
6. [Reports](#reports)
7. [Tasks](#tasks)
8. [Health](#health)

---

## Authentication

### Register Researcher
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "researcher@example.com",
  "password": "SecurePassword123",
  "full_name": "John Doe",
  "institution": "Nova SBE"
}

Response: 200 OK
{
  "id": "uuid",
  "email": "researcher@example.com",
  "full_name": "John Doe",
  "institution": "Nova SBE",
  "role": "researcher",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-08T10:00:00Z"
}
```

### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=researcher@example.com&password=SecurePassword123

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "uuid",
    "email": "researcher@example.com",
    "full_name": "John Doe",
    "role": "researcher"
  }
}
```

### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer {token}

Response: 200 OK
{
  "id": "uuid",
  "email": "researcher@example.com",
  "full_name": "John Doe",
  "institution": "Nova SBE",
  "role": "researcher",
  "is_active": true
}
```

### Refresh Token
```http
POST /api/v1/auth/refresh
Authorization: Bearer {token}

Response: 200 OK
{
  "access_token": "new_token...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## Datasets

### List Datasets
```http
GET /api/v1/datasets?skip=0&limit=100
Authorization: Bearer {token}

Response: 200 OK
[
  {
    "id": "uuid",
    "name": "IEEE-CIS Fraud Detection",
    "description": "Kaggle fraud detection dataset",
    "source": "kaggle",
    "status": "ready",
    "total_rows": 500000,
    "total_columns": 150,
    "created_at": "2024-01-08T10:00:00Z",
    "processed_at": "2024-01-08T10:30:00Z"
  }
]
```

### Create Dataset
```http
POST /api/v1/datasets
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Custom Dataset",
  "description": "My custom fraud dataset",
  "source": "upload"
}

Response: 201 Created
{
  "id": "uuid",
  "name": "Custom Dataset",
  "status": "uploading",
  "created_at": "2024-01-08T10:00:00Z"
}
```

### Get Dataset Details
```http
GET /api/v1/datasets/{dataset_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "id": "uuid",
  "name": "IEEE-CIS Fraud Detection",
  "description": "Kaggle fraud detection dataset",
  "source": "kaggle",
  "status": "ready",
  "size_info": {
    "total_rows": 500000,
    "total_columns": 150,
    "file_size_mb": 45.2,
    "sample_size": 500000
  },
  "quality_info": {
    "missing_values_count": 1234,
    "duplicate_rows_count": 0,
    "class_distribution": {"0": 475000, "1": 25000}
  },
  "feature_columns": ["TransactionAmt", "card1", ...],
  "numerical_features": ["TransactionAmt", ...],
  "categorical_features": ["ProductCD", ...],
  "target_column": "isFraud",
  "created_at": "2024-01-08T10:00:00Z",
  "processed_at": "2024-01-08T10:30:00Z"
}
```

### Download IEEE-CIS Dataset
```http
POST /api/v1/datasets/download-ieee-cis
Authorization: Bearer {token}

Response: 202 Accepted
{
  "message": "Download started",
  "dataset_id": "uuid",
  "task_id": "task_uuid",
  "status": "downloading"
}
```

### Trigger Preprocessing
```http
POST /api/v1/datasets/{dataset_id}/preprocess?apply_sampling=true
Authorization: Bearer {token}

Response: 202 Accepted
{
  "message": "Preprocessing started",
  "dataset_id": "uuid",
  "task_id": "task_uuid",
  "status": "processing"
}
```

### Get Dataset Statistics
```http
GET /api/v1/datasets/{dataset_id}/statistics
Authorization: Bearer {token}

Response: 200 OK
{
  "dataset_id": "uuid",
  "statistics": {
    "total_rows": 500000,
    "total_columns": 150,
    "memory_usage_mb": 45.2,
    "missing_values": {...},
    "class_distribution": {"0": 475000, "1": 25000},
    "fraud_percentage": 5.0,
    "numerical_features": {...},
    "categorical_features": {...}
  },
  "size_info": {...},
  "quality_info": {...}
}
```

### Delete Dataset
```http
DELETE /api/v1/datasets/{dataset_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "message": "Dataset deleted successfully",
  "dataset_id": "uuid"
}
```

---

## Models

### Train Model
```http
POST /api/v1/models/train
Authorization: Bearer {token}
Content-Type: application/json

{
  "dataset_id": "uuid",
  "model_type": "xgboost",
  "name": "XGBoost Baseline",
  "description": "Baseline XGBoost model",
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 6,
    "learning_rate": 0.1
  },
  "optimize_hyperparameters": false
}

Response: 202 Accepted
{
  "message": "Training started",
  "model_id": "uuid",
  "task_id": "task_uuid",
  "status": "training",
  "estimated_duration": "5-10 minutes"
}
```

### List Models
```http
GET /api/v1/models?skip=0&limit=100&model_type=xgboost&status=completed
Authorization: Bearer {token}

Response: 200 OK
[
  {
    "id": "uuid",
    "name": "XGBoost Baseline",
    "model_type": "xgboost",
    "dataset_id": "uuid",
    "status": "completed",
    "version": "1.0.0",
    "model_hash": "sha256_hash",
    "training_samples": 350000,
    "validation_samples": 75000,
    "created_at": "2024-01-08T10:00:00Z",
    "training_completed_at": "2024-01-08T10:15:00Z"
  }
]
```

### Get Model Details
```http
GET /api/v1/models/{model_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "id": "uuid",
  "name": "XGBoost Baseline",
  "description": "Baseline XGBoost model",
  "model_type": "xgboost",
  "dataset_id": "uuid",
  "status": "completed",
  "hyperparameters": {...},
  "feature_columns": [...],
  "target_column": "isFraud",
  "version": "1.0.0",
  "model_hash": "sha256_hash",
  "model_size_mb": 12.5,
  "training_samples": 350000,
  "validation_samples": 75000,
  "training_time_info": {
    "duration_seconds": 450.2,
    "started_at": "2024-01-08T10:00:00Z",
    "completed_at": "2024-01-08T10:15:00Z"
  },
  "is_baseline": true,
  "created_at": "2024-01-08T10:00:00Z"
}
```

### Get Model Metrics
```http
GET /api/v1/models/{model_id}/metrics
Authorization: Bearer {token}

Response: 200 OK
{
  "model_id": "uuid",
  "metrics": [
    {
      "id": "uuid",
      "metric_type": "validation",
      "core_metrics": {
        "accuracy": 0.95,
        "precision": 0.87,
        "recall": 0.82,
        "f1_score": 0.84,
        "auc_roc": 0.93,
        "auc_pr": 0.78,
        "log_loss": 0.15,
        "brier_score": 0.08
      },
      "calibration_error": 0.05,
      "confusion_matrix": [[470000, 5000], [4500, 20500]],
      "feature_importance": {...},
      "created_at": "2024-01-08T10:15:00Z"
    }
  ]
}
```

### Get Leaderboard
```http
GET /api/v1/models/leaderboard?metric=auc_roc&limit=10
Authorization: Bearer {token}

Response: 200 OK
{
  "leaderboard": [
    {
      "rank": 1,
      "model_id": "uuid",
      "model_name": "XGBoost Optimized",
      "model_type": "xgboost",
      "auc_roc": 0.95,
      "auc_pr": 0.82,
      "f1_score": 0.86,
      "training_date": "2024-01-08T10:00:00Z"
    }
  ],
  "metric": "auc_roc",
  "total_models": 6
}
```

### Make Predictions
```http
POST /api/v1/models/{model_id}/predict
Authorization: Bearer {token}
Content-Type: application/json

{
  "instances": [
    {"TransactionAmt": 100.0, "card1": 12345, ...}
  ]
}

Response: 200 OK
{
  "predictions": [0.85],
  "predictions_binary": [1],
  "model_id": "uuid",
  "timestamp": "2024-01-08T10:00:00Z"
}
```

---

## Explanations

### Generate Explanation
```http
POST /api/v1/explanations/generate
Authorization: Bearer {token}
Content-Type: application/json

{
  "model_id": "uuid",
  "method": "shap_tree",
  "explanation_type": "global",
  "name": "SHAP Global Explanation",
  "sample_size": 10000,
  "config": {
    "check_additivity": false
  }
}

Response: 202 Accepted
{
  "message": "Explanation generation started",
  "explanation_id": "uuid",
  "task_id": "task_uuid",
  "status": "generating",
  "estimated_duration": "2-5 minutes"
}
```

### Get Explanation
```http
GET /api/v1/explanations/{explanation_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "id": "uuid",
  "name": "SHAP Global Explanation",
  "method": "shap_tree",
  "explanation_type": "global",
  "model_id": "uuid",
  "dataset_id": "uuid",
  "status": "completed",
  "sample_size": 10000,
  "explanation_hash": "sha256_hash",
  "is_cached": true,
  "cache_hit_count": 5,
  "generation_time_info": {
    "duration_seconds": 120.5,
    "started_at": "2024-01-08T10:00:00Z",
    "completed_at": "2024-01-08T10:02:00Z"
  },
  "created_at": "2024-01-08T10:00:00Z"
}
```

### Compare Explanation Methods
```http
POST /api/v1/explanations/compare
Authorization: Bearer {token}
Content-Type: application/json

{
  "model_id": "uuid",
  "methods": ["shap_tree", "lime"],
  "sample_size": 1000
}

Response: 200 OK
{
  "comparison": [
    {
      "method": "shap_tree",
      "explanation_id": "uuid",
      "metrics": {
        "faithfulness_correlation": 0.92,
        "stability": 0.88,
        "sparsity_ratio": 0.15,
        "generation_time_ms": 2500
      }
    },
    {
      "method": "lime",
      "explanation_id": "uuid",
      "metrics": {
        "faithfulness_correlation": 0.85,
        "stability": 0.75,
        "sparsity_ratio": 0.20,
        "generation_time_ms": 3200
      }
    }
  ]
}
```

### List Available Methods
```http
GET /api/v1/explanations/methods
Authorization: Bearer {token}

Response: 200 OK
{
  "methods": [
    {
      "name": "shap_tree",
      "display_name": "SHAP TreeExplainer",
      "applicable_models": ["random_forest", "xgboost", "lightgbm", "catboost"],
      "explanation_types": ["global", "local"],
      "description": "Fast SHAP for tree-based models"
    },
    {
      "name": "shap_kernel",
      "display_name": "SHAP KernelExplainer",
      "applicable_models": ["logistic_regression", "mlp"],
      "explanation_types": ["global", "local"],
      "description": "Model-agnostic SHAP using kernel method"
    },
    {
      "name": "lime",
      "display_name": "LIME",
      "applicable_models": ["all"],
      "explanation_types": ["local"],
      "description": "Local Interpretable Model-agnostic Explanations"
    }
  ]
}
```

---

## Human Study

### Create Study Session
```http
POST /api/v1/study/sessions
Content-Type: application/json

{
  "consent_given": true,
  "user_agent": "Mozilla/5.0...",
  "screen_resolution": "1920x1080"
}

Response: 201 Created
{
  "id": "uuid",
  "session_id": "session_abc123xyz",
  "condition": "shap_explanation",
  "status": "active",
  "target_interactions": 20,
  "transaction_order": [1, 5, 12, ...],
  "created_at": "2024-01-08T10:00:00Z"
}
```

### Get Study Session
```http
GET /api/v1/study/sessions/{session_id}

Response: 200 OK
{
  "id": "uuid",
  "session_id": "session_abc123xyz",
  "condition": "shap_explanation",
  "status": "active",
  "progress_info": {
    "total_interactions": 5,
    "target_interactions": 20,
    "completion_percentage": 25.0,
    "average_response_time_ms": 15000
  },
  "consent_given": true,
  "created_at": "2024-01-08T10:00:00Z"
}
```

### Log Interaction
```http
POST /api/v1/study/interactions
Content-Type: application/json

{
  "session_id": "uuid",
  "transaction_index": 1,
  "transaction_id": "trans_123",
  "participant_decision": 1,
  "confidence_rating": 6,
  "trust_rating": 5,
  "response_time_ms": 12500,
  "explanation_viewed": true,
  "explanation_view_duration_ms": 8000,
  "ui_interactions": [...]
}

Response: 201 Created
{
  "id": "uuid",
  "session_id": "uuid",
  "transaction_index": 1,
  "decision_accuracy": true,
  "created_at": "2024-01-08T10:05:00Z"
}
```

### Export Study Results
```http
GET /api/v1/study/results?format=csv
Authorization: Bearer {token}

Response: 200 OK
Content-Type: text/csv

session_id,condition,transaction_index,participant_decision,confidence_rating,trust_rating,response_time_ms,decision_accuracy
session_abc,shap_explanation,1,1,6,5,12500,true
...
```

---

## Reports

### Generate XAI Audit Report
```http
POST /api/v1/reports/generate
Authorization: Bearer {token}
Content-Type: application/json

{
  "model_id": "uuid",
  "explanation_id": "uuid",
  "include_fairness": true,
  "include_drift": true,
  "format": "pdf"
}

Response: 202 Accepted
{
  "message": "Report generation started",
  "report_id": "uuid",
  "task_id": "task_uuid",
  "status": "generating"
}
```

### Get Report
```http
GET /api/v1/reports/{report_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "id": "uuid",
  "model_id": "uuid",
  "explanation_id": "uuid",
  "format": "pdf",
  "status": "completed",
  "file_path": "reports/audit_report_uuid.pdf",
  "file_size_mb": 2.5,
  "created_at": "2024-01-08T10:00:00Z"
}
```

### Download Report
```http
GET /api/v1/reports/{report_id}/download
Authorization: Bearer {token}

Response: 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="xai_audit_report.pdf"

[Binary PDF data]
```

---

## Tasks

### Get Task Status
```http
GET /api/v1/tasks/{task_id}

Response: 200 OK
{
  "task_id": "task_uuid",
  "status": "SUCCESS",
  "ready": true,
  "successful": true,
  "result": {
    "status": "success",
    "dataset_id": "uuid",
    "train_size": 350000,
    "val_size": 75000,
    "test_size": 75000
  }
}
```

### Cancel Task
```http
POST /api/v1/tasks/{task_id}/cancel

Response: 200 OK
{
  "message": "Task cancelled successfully",
  "task_id": "task_uuid",
  "status": "cancelled"
}
```

---

## Health

### Basic Health Check
```http
GET /api/v1/health

Response: 200 OK
{
  "status": "healthy",
  "timestamp": 1704708000.0,
  "version": "0.1.0",
  "environment": "development"
}
```

### Detailed Health Check
```http
GET /api/v1/health/detailed

Response: 200 OK
{
  "status": "healthy",
  "timestamp": 1704708000.0,
  "version": "0.1.0",
  "environment": "development",
  "services": {
    "database": {
      "status": "healthy",
      "response_time_ms": null
    },
    "redis": {
      "status": "healthy",
      "response_time_ms": null
    }
  }
}
```

### Readiness Check
```http
GET /api/v1/health/readiness

Response: 200 OK
{
  "status": "ready",
  "timestamp": 1704708000.0
}
```

### Liveness Check
```http
GET /api/v1/health/liveness

Response: 200 OK
{
  "status": "alive",
  "timestamp": 1704708000.0
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data",
  "type": "validation_error",
  "timestamp": 1704708000.0
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials",
  "type": "authentication_error"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions. Researcher role required.",
  "type": "authorization_error"
}
```

### 404 Not Found
```json
{
  "detail": "Dataset not found",
  "type": "not_found_error"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "type": "internal_error",
  "timestamp": 1704708000.0
}
```

---

## Rate Limiting

- **Researchers:** 100 requests per minute
- **Study Participants:** 20 requests per minute
- **Anonymous:** 10 requests per minute

---

## Pagination

List endpoints support pagination:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 1000)

---

## Filtering & Sorting

### Models Endpoint
```http
GET /api/v1/models?model_type=xgboost&status=completed&sort_by=auc_roc&order=desc
```

### Datasets Endpoint
```http
GET /api/v1/datasets?source=kaggle&status=ready&sort_by=created_at&order=desc
```

---

## WebSocket Support (Future)

Real-time task progress updates will be available via WebSocket:
```javascript
ws://localhost:8000/ws/tasks/{task_id}
```

---

## API Versioning

Current version: `v1`  
Base path: `/api/v1`

Future versions will be available at `/api/v2`, etc.

---

**Interactive API Documentation:** http://localhost:8000/api/v1/docs  
**Alternative Documentation:** http://localhost:8000/api/v1/redoc
