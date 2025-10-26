"""
Train an ethical German Credit model with fair features only.

This script:
1. Loads the German Credit dataset
2. Excludes discriminatory features (gender, nationality, marital status)
3. Trains XGBoost on ethically acceptable features only
4. Saves the model and scaler for denormalization
5. Registers the model in the database
"""

import sys
import uuid
import joblib
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, precision_score, recall_score, accuracy_score
import xgboost as xgb

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.utils.supabase_client import supabase_db
from app.utils.r2_storage import r2_storage_client
import structlog

logger = structlog.get_logger()

# ============================================================================
# ETHICAL FEATURE CONFIGURATION
# ============================================================================

# Features to EXCLUDE (discriminatory or sensitive)
EXCLUDED_FEATURES = [
    'personal_status',      # Gender-coded (e.g., "male single", "female divorced")
    'foreign_worker',       # Nationality discrimination
    'dependents',           # Family status
    # Add any other features that encode marital status, sex, nationality
]

# Features to KEEP (ethically neutral and interpretable)
ETHICAL_FEATURES = [
    'age',
    'credit_amount',
    'duration',             # Loan duration in months
    'installment_rate',     # Installment rate in percentage of disposable income
    'present_residence',    # Years at current residence
    'existing_credits',     # Number of existing credits
    'num_dependents',       # Number of people liable to provide maintenance for (if not discriminatory)
    'checking_status',      # Status of checking account
    'credit_history',       # Credit history
    'purpose',              # Purpose of credit
    'savings_status',       # Savings account/bonds
    'employment',           # Present employment since
    'property_magnitude',   # Property
    'other_payment_plans',  # Other installment plans
    'housing',              # Housing
    'job',                  # Job type
    'own_telephone',        # Telephone
]

# Feature display names for human-readable output
FEATURE_DISPLAY_NAMES = {
    'age': 'Age',
    'credit_amount': 'Credit Amount',
    'duration': 'Duration (months)',
    'installment_rate': 'Installment Rate (%)',
    'present_residence': 'Years at Residence',
    'existing_credits': 'Existing Credits',
    'checking_status': 'Checking Account',
    'credit_history': 'Credit History',
    'purpose': 'Loan Purpose',
    'savings_status': 'Savings Account',
    'employment': 'Employment Length',
    'property_magnitude': 'Property',
    'other_payment_plans': 'Other Payment Plans',
    'housing': 'Housing',
    'job': 'Job Type',
    'own_telephone': 'Has Telephone',
}

# Categorical mappings for denormalization
CATEGORICAL_MAPPINGS = {
    'checking_status': {
        0: '< 0 DM',
        1: '0 - 200 DM',
        2: '> 200 DM',
        3: 'No checking account'
    },
    'credit_history': {
        0: 'No credits / all paid',
        1: 'All paid this bank',
        2: 'Existing paid',
        3: 'Delayed payment',
        4: 'Critical account'
    },
    'purpose': {
        0: 'New car',
        1: 'Used car',
        2: 'Furniture/equipment',
        3: 'Radio/TV',
        4: 'Domestic appliances',
        5: 'Repairs',
        6: 'Education',
        7: 'Vacation',
        8: 'Retraining',
        9: 'Business',
        10: 'Other'
    },
    'savings_status': {
        0: '< 100 DM',
        1: '100 - 500 DM',
        2: '500 - 1000 DM',
        3: '> 1000 DM',
        4: 'Unknown / no savings'
    },
    'employment': {
        0: 'Unemployed',
        1: '< 1 year',
        2: '1 - 4 years',
        3: '4 - 7 years',
        4: '> 7 years'
    },
    'housing': {
        0: 'Rent',
        1: 'Own',
        2: 'For free'
    },
    'job': {
        0: 'Unemployed/unskilled',
        1: 'Unskilled resident',
        2: 'Skilled',
        3: 'Highly skilled'
    }
}


def load_and_prepare_data(data_path: str):
    """Load German Credit data and prepare ethical features."""
    print("\n" + "=" * 80)
    print("STEP 1: LOADING AND PREPARING DATA")
    print("=" * 80)
    
    # Load data
    df = pd.read_csv(data_path)
    print(f"✅ Loaded {len(df)} samples with {len(df.columns)} columns")
    print(f"   Columns: {list(df.columns)}")
    
    # Identify target column
    target_col = 'Risk' if 'Risk' in df.columns else 'class'
    if target_col not in df.columns:
        raise ValueError(f"Target column not found. Available: {list(df.columns)}")
    
    print(f"✅ Target column: {target_col}")
    
    # Map column names to standardized names (handle different dataset versions)
    column_mapping = {
        'Age': 'age',
        'Credit amount': 'credit_amount',
        'Duration': 'duration',
        'Installment rate in percentage of disposable income': 'installment_rate',
        'Present residence since': 'present_residence',
        'Number of existing credits at this bank': 'existing_credits',
        'Status of existing checking account': 'checking_status',
        'Credit history': 'credit_history',
        'Purpose': 'purpose',
        'Saving accounts/bonds': 'savings_status',
        'Present employment since': 'employment',
        'Property': 'property_magnitude',
        'Other installment plans': 'other_payment_plans',
        'Housing': 'housing',
        'Job': 'job',
        'Telephone': 'own_telephone',
    }
    
    df = df.rename(columns=column_mapping)
    
    # Filter to ethical features only
    available_features = [f for f in ETHICAL_FEATURES if f in df.columns]
    excluded_found = [f for f in EXCLUDED_FEATURES if f in df.columns]
    
    print(f"\n📋 Feature Selection:")
    print(f"   ✅ Keeping {len(available_features)} ethical features")
    print(f"   ❌ Excluding {len(excluded_found)} discriminatory features: {excluded_found}")
    
    # Select features and target
    X = df[available_features].copy()
    y = df[target_col].copy()
    
    # Encode target (1 = bad credit risk, 0 = good)
    if y.dtype == 'object':
        y = (y == 'bad').astype(int)
    
    print(f"\n✅ Final dataset: {len(X)} samples, {len(X.columns)} features")
    print(f"   Target distribution: {y.value_counts().to_dict()}")
    
    return X, y, available_features


def preprocess_features(X_train, X_val, X_test):
    """Preprocess features with normalization."""
    print("\n" + "=" * 80)
    print("STEP 2: PREPROCESSING FEATURES")
    print("=" * 80)
    
    # Encode categorical variables
    categorical_cols = X_train.select_dtypes(include=['object', 'category']).columns.tolist()
    numerical_cols = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    print(f"📊 Feature types:")
    print(f"   Categorical: {len(categorical_cols)} - {categorical_cols}")
    print(f"   Numerical: {len(numerical_cols)} - {numerical_cols}")
    
    # Encode categorical features
    for col in categorical_cols:
        X_train[col] = X_train[col].astype('category').cat.codes
        X_val[col] = X_val[col].astype('category').cat.codes
        X_test[col] = X_test[col].astype('category').cat.codes
    
    # Normalize numerical features
    scaler = StandardScaler()
    X_train[numerical_cols] = scaler.fit_transform(X_train[numerical_cols])
    X_val[numerical_cols] = scaler.transform(X_val[numerical_cols])
    X_test[numerical_cols] = scaler.transform(X_test[numerical_cols])
    
    print(f"✅ Categorical features encoded")
    print(f"✅ Numerical features normalized (StandardScaler)")
    
    return X_train, X_val, X_test, scaler, categorical_cols, numerical_cols


def train_xgboost_model(X_train, y_train, X_val, y_val):
    """Train XGBoost model."""
    print("\n" + "=" * 80)
    print("STEP 3: TRAINING XGBOOST MODEL")
    print("=" * 80)
    
    # XGBoost parameters (optimized for credit risk)
    params = {
        'objective': 'binary:logistic',
        'eval_metric': 'auc',
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 200,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42,
        'n_jobs': -1
    }
    
    print(f"📋 Model parameters: {params}")
    
    # Train model
    model = xgb.XGBClassifier(**params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    
    print(f"✅ Model trained successfully")
    
    return model


def evaluate_model(model, X_test, y_test):
    """Evaluate model performance."""
    print("\n" + "=" * 80)
    print("STEP 4: EVALUATING MODEL")
    print("=" * 80)
    
    # Predictions
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    # Metrics
    metrics = {
        'auc_roc': float(roc_auc_score(y_test, y_pred_proba)),
        'auc_pr': float(average_precision_score(y_test, y_pred_proba)),
        'f1_score': float(f1_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred)),
        'recall': float(recall_score(y_test, y_pred)),
        'accuracy': float(accuracy_score(y_test, y_pred))
    }
    
    print(f"📊 Model Performance:")
    print(f"   AUC-ROC:   {metrics['auc_roc']:.4f}")
    print(f"   AUC-PR:    {metrics['auc_pr']:.4f}")
    print(f"   F1 Score:  {metrics['f1_score']:.4f}")
    print(f"   Precision: {metrics['precision']:.4f}")
    print(f"   Recall:    {metrics['recall']:.4f}")
    print(f"   Accuracy:  {metrics['accuracy']:.4f}")
    
    return metrics


def save_model_and_scaler(model, scaler, feature_names, categorical_cols, numerical_cols, output_dir):
    """Save model, scaler, and metadata."""
    print("\n" + "=" * 80)
    print("STEP 5: SAVING MODEL AND SCALER")
    print("=" * 80)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_path = output_dir / 'german_credit_fair_xgb.pkl'
    joblib.dump(model, model_path)
    model_size_mb = model_path.stat().st_size / (1024 * 1024)
    print(f"✅ Model saved: {model_path} ({model_size_mb:.2f} MB)")
    
    # Save scaler
    scaler_path = output_dir / 'german_credit_scaler.pkl'
    joblib.dump(scaler, scaler_path)
    print(f"✅ Scaler saved: {scaler_path}")
    
    # Save metadata
    metadata = {
        'model_id': 'german_credit_fair_xgb',
        'feature_names': feature_names,
        'categorical_cols': categorical_cols,
        'numerical_cols': numerical_cols,
        'excluded_features': EXCLUDED_FEATURES,
        'feature_display_names': FEATURE_DISPLAY_NAMES,
        'categorical_mappings': CATEGORICAL_MAPPINGS
    }
    
    metadata_path = output_dir / 'model_metadata.pkl'
    joblib.dump(metadata, metadata_path)
    print(f"✅ Metadata saved: {metadata_path}")
    
    return model_path, scaler_path, metadata_path, model_size_mb


def main():
    """Main training pipeline."""
    print("=" * 80)
    print("ETHICAL GERMAN CREDIT MODEL TRAINING")
    print("=" * 80)
    
    # Configuration
    data_path = 'data/datasets/german-credit/raw/german_credit_data.csv'
    output_dir = 'data/models/german_credit_fair'
    
    try:
        # Step 1: Load data
        X, y, feature_names = load_and_prepare_data(data_path)
        
        # Split data
        X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
        X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)
        
        print(f"\n📊 Data splits:")
        print(f"   Train: {len(X_train)} samples")
        print(f"   Val:   {len(X_val)} samples")
        print(f"   Test:  {len(X_test)} samples")
        
        # Step 2: Preprocess
        X_train, X_val, X_test, scaler, categorical_cols, numerical_cols = preprocess_features(
            X_train.copy(), X_val.copy(), X_test.copy()
        )
        
        # Step 3: Train
        model = train_xgboost_model(X_train, y_train, X_val, y_val)
        
        # Step 4: Evaluate
        metrics = evaluate_model(model, X_test, y_test)
        
        # Step 5: Save
        model_path, scaler_path, metadata_path, model_size_mb = save_model_and_scaler(
            model, scaler, feature_names, categorical_cols, numerical_cols, output_dir
        )
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS: ETHICAL MODEL TRAINING COMPLETE")
        print("=" * 80)
        print(f"\n📁 Output files:")
        print(f"   Model:    {model_path}")
        print(f"   Scaler:   {scaler_path}")
        print(f"   Metadata: {metadata_path}")
        print(f"\n📊 Model Performance:")
        print(f"   AUC-ROC: {metrics['auc_roc']:.4f}")
        print(f"   F1:      {metrics['f1_score']:.4f}")
        print(f"\n🎯 Next steps:")
        print(f"   1. Upload model to R2: models/german-credit/german_credit_fair_xgb.pkl")
        print(f"   2. Upload scaler to R2: models/german-credit/german_credit_scaler.pkl")
        print(f"   3. Register model in database with model_id='german_credit_fair_xgb'")
        print(f"   4. Update study_service.py to use denormalization")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
