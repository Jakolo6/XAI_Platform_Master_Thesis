# XAI Platform - ML Specialist Documentation

## 📋 Overview

This document provides comprehensive technical details about the machine learning models, evaluation metrics, and explainability methods used in the XAI Platform for fraud detection.

---

## 🤖 Supported ML Algorithms

### 1. **XGBoost (Extreme Gradient Boosting)**
- **Type:** Gradient Boosting Decision Trees
- **Implementation:** `xgboost.XGBClassifier`
- **Best For:** High performance on tabular data, handles missing values
- **Key Hyperparameters:**
  - `n_estimators`: Number of boosting rounds (default: 100)
  - `max_depth`: Maximum tree depth (default: 6)
  - `learning_rate`: Step size shrinkage (default: 0.1)
  - `subsample`: Fraction of samples for training (default: 0.8)
  - `colsample_bytree`: Fraction of features per tree (default: 0.8)

### 2. **Random Forest**
- **Type:** Ensemble of Decision Trees
- **Implementation:** `sklearn.ensemble.RandomForestClassifier`
- **Best For:** Robust predictions, feature importance
- **Key Hyperparameters:**
  - `n_estimators`: Number of trees (default: 100)
  - `max_depth`: Maximum tree depth (default: None)
  - `min_samples_split`: Minimum samples to split (default: 2)
  - `min_samples_leaf`: Minimum samples per leaf (default: 1)

### 3. **LightGBM**
- **Type:** Gradient Boosting with leaf-wise growth
- **Implementation:** `lightgbm.LGBMClassifier`
- **Best For:** Fast training, memory efficient
- **Key Hyperparameters:**
  - `n_estimators`: Number of boosting rounds (default: 100)
  - `num_leaves`: Maximum tree leaves (default: 31)
  - `learning_rate`: Step size (default: 0.1)

### 4. **CatBoost**
- **Type:** Gradient Boosting with categorical feature support
- **Implementation:** `catboost.CatBoostClassifier`
- **Best For:** Categorical features, robust to overfitting
- **Key Hyperparameters:**
  - `iterations`: Number of boosting rounds (default: 100)
  - `depth`: Tree depth (default: 6)
  - `learning_rate`: Step size (default: 0.1)

### 5. **Logistic Regression**
- **Type:** Linear Classification Model
- **Implementation:** `sklearn.linear_model.LogisticRegression`
- **Best For:** Baseline, interpretability
- **Key Hyperparameters:**
  - `C`: Inverse regularization strength (default: 1.0)
  - `penalty`: Regularization type (default: 'l2')
  - `solver`: Optimization algorithm (default: 'lbfgs')

---

## 📊 Evaluation Metrics

### Classification Metrics

#### **1. AUC-ROC (Area Under ROC Curve)**
- **Range:** 0.0 to 1.0 (higher is better)
- **Interpretation:**
  - 1.0 = Perfect classifier
  - 0.9-1.0 = Excellent
  - 0.8-0.9 = Good
  - 0.7-0.8 = Fair
  - 0.5 = Random classifier
- **Use Case:** Overall discrimination ability across all thresholds
- **Formula:** Area under the curve of TPR vs FPR

#### **2. AUC-PR (Area Under Precision-Recall Curve)**
- **Range:** 0.0 to 1.0 (higher is better)
- **Interpretation:** Better for imbalanced datasets than AUC-ROC
- **Baseline:** Proportion of positive class (e.g., 3.5% for IEEE-CIS dataset)
- **Use Case:** Performance on minority class (fraud cases)

#### **3. F1 Score**
- **Range:** 0.0 to 1.0 (higher is better)
- **Formula:** `2 × (Precision × Recall) / (Precision + Recall)`
- **Interpretation:** Harmonic mean of precision and recall
- **Use Case:** Balance between precision and recall

#### **4. Precision**
- **Range:** 0.0 to 1.0 (higher is better)
- **Formula:** `TP / (TP + FP)`
- **Interpretation:** Of all predicted frauds, how many are actual frauds?
- **Use Case:** Minimize false alarms

#### **5. Recall (Sensitivity, TPR)**
- **Range:** 0.0 to 1.0 (higher is better)
- **Formula:** `TP / (TP + FN)`
- **Interpretation:** Of all actual frauds, how many did we catch?
- **Use Case:** Minimize missed fraud cases

#### **6. Accuracy**
- **Range:** 0.0 to 1.0 (higher is better)
- **Formula:** `(TP + TN) / (TP + TN + FP + FN)`
- **Interpretation:** Overall correctness
- **Note:** Can be misleading for imbalanced datasets

### Calibration Metrics

#### **7. Log Loss (Cross-Entropy Loss)**
- **Range:** 0.0 to ∞ (lower is better)
- **Formula:** `-1/N × Σ(y × log(p) + (1-y) × log(1-p))`
- **Interpretation:** Measures probability calibration
- **Use Case:** Evaluate confidence of predictions

#### **8. Brier Score**
- **Range:** 0.0 to 1.0 (lower is better)
- **Formula:** `1/N × Σ(p - y)²`
- **Interpretation:** Mean squared error of probability predictions
- **Use Case:** Probability accuracy

#### **9. Expected Calibration Error (ECE)**
- **Range:** 0.0 to 1.0 (lower is better)
- **Interpretation:** Average difference between predicted probabilities and actual outcomes
- **Use Case:** Assess probability calibration across bins

#### **10. Maximum Calibration Error (MCE)**
- **Range:** 0.0 to 1.0 (lower is better)
- **Interpretation:** Worst-case calibration error
- **Use Case:** Identify problematic probability ranges

---

## 📈 Performance Curves

### ROC Curve (Receiver Operating Characteristic)
- **X-axis:** False Positive Rate (FPR) = FP / (FP + TN)
- **Y-axis:** True Positive Rate (TPR) = TP / (TP + FN)
- **Interpretation:**
  - Curve closer to top-left corner = better performance
  - Diagonal line = random classifier
  - Area under curve = AUC-ROC score
- **Data Points:** 100 sampled points from all thresholds
- **Use Case:** Visualize trade-off between TPR and FPR

### Precision-Recall Curve
- **X-axis:** Recall = TP / (TP + FN)
- **Y-axis:** Precision = TP / (TP + FP)
- **Interpretation:**
  - Curve closer to top-right corner = better performance
  - Baseline = proportion of positive class
  - Area under curve = AUC-PR score
- **Data Points:** 100 sampled points from all thresholds
- **Use Case:** Better for imbalanced datasets (fraud detection)

---

## 🔍 Feature Importance

### Calculation Methods

#### **Tree-Based Models (XGBoost, Random Forest, LightGBM, CatBoost)**
- **Method:** Gain-based importance
- **Formula:** Sum of information gain from all splits using the feature
- **Normalization:** Scores sum to 1.0
- **Interpretation:** Higher score = more important for predictions

#### **Linear Models (Logistic Regression)**
- **Method:** Absolute coefficient values
- **Formula:** `|coefficient|`
- **Normalization:** Scores sum to 1.0
- **Interpretation:** Higher score = stronger linear relationship

### Display
- **Top N Features:** 20 features stored, 15 displayed
- **Format:** Dictionary mapping feature names to importance scores
- **Visualization:** Horizontal bar chart with percentages

---

## 🎯 Model Training Configuration

### Data Splitting
```python
train_size = 0.70  # 70% for training
val_size = 0.15    # 15% for validation
test_size = 0.15   # 15% for testing
```

### Hyperparameter Optimization (Optional)
- **Framework:** Optuna
- **Method:** Tree-structured Parzen Estimator (TPE)
- **Objective:** Maximize AUC-ROC on validation set
- **Trials:** Configurable (default: 50)
- **Timeout:** Configurable (default: 300 seconds)

### Early Stopping (Gradient Boosting Models)
- **Enabled:** Yes for XGBoost, LightGBM, CatBoost
- **Patience:** 10 rounds without improvement
- **Metric:** Validation loss

---

## 🧠 Explainability Methods

### 1. SHAP (SHapley Additive exPlanations)
- **Type:** Game-theoretic approach
- **Method:** TreeExplainer for tree-based models
- **Output:** Feature attribution values
- **Interpretation:** How much each feature contributes to prediction
- **Advantages:**
  - Theoretically sound (Shapley values)
  - Consistent and locally accurate
  - Works well with tree-based models
- **Generation Time:** ~30-60 seconds

### 2. LIME (Local Interpretable Model-agnostic Explanations)
- **Type:** Local surrogate model
- **Method:** Perturb input and fit linear model
- **Samples:** 200 perturbations (optimized)
- **Output:** Feature weights for local region
- **Interpretation:** Linear approximation of model behavior
- **Advantages:**
  - Model-agnostic
  - Intuitive linear explanations
  - Good for local understanding
- **Generation Time:** ~3-5 minutes

---

## 📁 Data Storage

### PostgreSQL Database
- **Models Table:** Stores model metadata, hyperparameters, feature importance
- **Model Metrics Table:** Stores evaluation metrics, ROC/PR curves
- **Explanations Table:** Stores SHAP/LIME results

### Supabase (Cloud Storage)
- **Models Bucket:** Stores serialized model files (.pkl)
- **Datasets Bucket:** Stores processed datasets
- **Path Format:** `{model_id}/model.pkl`

### Model File Format
- **Format:** Pickle (.pkl)
- **Contents:** Trained scikit-learn/XGBoost/etc. model object
- **Compression:** None (for compatibility)
- **Hash:** SHA-256 for version control

---

## 🔬 Datasets

### IEEE-CIS Fraud Detection
- **Source:** Kaggle Competition
- **Samples:** 590,540 transactions
- **Features:** 50 (selected from 400+)
- **Class Balance:** 96.5% legitimate, 3.5% fraud
- **Split:** 70% train, 15% validation, 15% test
- **Feature Types:**
  - Transaction features (V1-V339)
  - Card features (C1-C14)
  - Address features (addr1, addr2)
  - Distance features (D1-D15)

### Give Me Some Credit
- **Source:** Kaggle Competition
- **Samples:** 150,000 borrowers
- **Features:** 10 financial indicators
- **Class Balance:** ~93% good, ~7% default
- **Task:** Predict probability of default

### German Credit Risk
- **Source:** UCI ML Repository
- **Samples:** 1,000 loan applications
- **Features:** 20 attributes
- **Class Balance:** 70% good credit, 30% bad credit
- **Task:** Credit risk assessment

---

## 🚀 API Endpoints

### Model Training
```
POST /api/v1/models/train
Body: {
  "dataset_id": "ieee-cis-fraud",
  "model_type": "xgboost",
  "hyperparameters": {...},
  "optimize": false
}
```

### Get Model Details
```
GET /api/v1/models/{model_id}
Response: {
  "id": "...",
  "model_type": "xgboost",
  "hyperparameters": {...},
  "feature_importance": {...},
  "training_time_seconds": 4.79,
  ...
}
```

### Get Model Metrics
```
GET /api/v1/models/{model_id}/metrics
Response: {
  "auc_roc": 0.9024,
  "auc_pr": 0.8123,
  "f1_score": 0.4987,
  "roc_curve": {
    "fpr": [...],
    "tpr": [...],
    "thresholds": [...]
  },
  "pr_curve": {...},
  ...
}
```

---

## 📊 Benchmarking

### Comparison Metrics
- **Primary:** AUC-ROC (overall discrimination)
- **Secondary:** AUC-PR (imbalanced data performance)
- **Tertiary:** F1 Score (precision-recall balance)
- **Efficiency:** Training time, model size

### Leaderboard
- **Ranking:** By AUC-ROC score
- **Filters:** Dataset, model type
- **Display:** Top 10 models

---

## 🔐 Best Practices

### For ML Specialists

1. **Model Selection:**
   - Start with XGBoost for best performance
   - Use Random Forest for interpretability
   - Try LightGBM for large datasets

2. **Hyperparameter Tuning:**
   - Enable optimization for production models
   - Use validation set for early stopping
   - Monitor overfitting (train vs validation metrics)

3. **Evaluation:**
   - Focus on AUC-PR for imbalanced data
   - Check calibration metrics (ECE, MCE)
   - Analyze confusion matrix for business impact

4. **Explainability:**
   - Use SHAP for global feature importance
   - Use LIME for individual prediction explanations
   - Validate explanations with domain knowledge

5. **Deployment:**
   - Monitor model performance over time
   - Retrain periodically with new data
   - Version control with model hashing

---

## 📞 Technical Support

For questions about model implementation, evaluation metrics, or explainability methods, refer to:
- **Code:** `/backend/app/utils/training.py`
- **API:** `/backend/app/api/v1/endpoints/models.py`
- **Frontend:** `/frontend/src/app/models/[id]/page.tsx`

---

**Last Updated:** January 11, 2025  
**Version:** 1.0.0  
**Platform:** XAI Finance - Explainable AI for Fraud Detection
