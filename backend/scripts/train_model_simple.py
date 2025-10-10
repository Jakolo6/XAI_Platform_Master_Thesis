"""Simple model training script (without Celery)."""

import sys
import uuid
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.datasets.registry import get_dataset_registry
from app.datasets.loaders import get_loader
from app.utils.training import ModelTrainer
from app.supabase.client import get_supabase_client
import structlog

logger = structlog.get_logger()


def train_model_simple(dataset_id: str, model_type: str):
    """Train a model on a dataset (simplified, no Celery).
    
    Args:
        dataset_id: Dataset identifier
        model_type: Model type (xgboost, lightgbm, etc.)
    """
    print("=" * 60)
    print(f"TRAINING MODEL: {model_type} on {dataset_id}")
    print("=" * 60)
    
    try:
        # Get dataset configuration
        print("\n1. Loading dataset...")
        registry = get_dataset_registry()
        dataset_config = registry.get_dataset_config(dataset_id)
        
        if not dataset_config:
            print(f"   ❌ Dataset not found: {dataset_id}")
            return False
        
        print(f"   ✅ Dataset: {dataset_config['display_name']}")
        
        # Load dataset
        loader = get_loader(dataset_id, dataset_config)
        
        if not loader.splits_exist():
            print(f"   ❌ Dataset not processed. Run: python scripts/process_dataset.py {dataset_id}")
            return False
        
        train_df, val_df, test_df = loader.load_splits()
        print(f"   ✅ Loaded: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")
        
        # Prepare data
        print("\n2. Preparing data...")
        target_col = loader.get_target_column()
        
        X_train = train_df.drop(columns=[target_col])
        y_train = train_df[target_col]
        X_val = val_df.drop(columns=[target_col])
        y_val = val_df[target_col]
        X_test = test_df.drop(columns=[target_col])
        y_test = test_df[target_col]
        
        print(f"   ✅ Features: {len(X_train.columns)}")
        print(f"   ✅ Target: {target_col}")
        
        # Train model
        print(f"\n3. Training {model_type}...")
        trainer = ModelTrainer(model_type, hyperparameters=None)
        
        training_results = trainer.train(X_train, y_train, X_val, y_val)
        print(f"   ✅ Training complete in {training_results['training_time_seconds']:.2f}s")
        
        # Evaluate
        print("\n4. Evaluating model...")
        metrics = trainer.evaluate(X_test, y_test)
        
        print(f"   ✅ Metrics:")
        print(f"      AUC-ROC: {metrics['auc_roc']:.4f}")
        print(f"      AUC-PR:  {metrics['auc_pr']:.4f}")
        print(f"      F1:      {metrics['f1_score']:.4f}")
        print(f"      Precision: {metrics['precision']:.4f}")
        print(f"      Recall:  {metrics['recall']:.4f}")
        
        # Save model
        print("\n5. Saving model...")
        model_id = str(uuid.uuid4())
        model_dir = Path(f"data/models/{model_id}")
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = str(model_dir / "model.pkl")
        model_hash = trainer.save_model(model_path)
        model_size_mb = Path(model_path).stat().st_size / (1024 * 1024)
        
        print(f"   ✅ Saved to {model_path}")
        print(f"   ✅ Size: {model_size_mb:.2f} MB")
        
        # Save to Supabase
        print("\n6. Saving to Supabase...")
        supabase = get_supabase_client()
        
        # Get dataset UUID from Supabase
        datasets = supabase.get_datasets(is_active=False)
        supabase_dataset = next((d for d in datasets if d['name'] == dataset_id), None)
        
        if not supabase_dataset:
            print(f"   ⚠️  Dataset not found in Supabase")
            dataset_uuid = None
        else:
            dataset_uuid = supabase_dataset['id']
        
        # Insert model
        supabase.insert_model({
            'id': model_id,
            'name': f"{model_type}_{dataset_id}",
            'model_type': model_type,
            'version': '1.0.0',
            'dataset_id': dataset_uuid,
            'hyperparameters': trainer.hyperparameters,
            'model_path': f"models/{model_id}/model.pkl",
            'model_hash': model_hash,
            'model_size_mb': model_size_mb,
            'training_time_seconds': training_results["training_time_seconds"],
            'status': 'completed',
        })
        
        # Insert metrics
        supabase.insert_model_metrics({
            'model_id': model_id,
            **metrics
        })
        
        print(f"   ✅ Saved to Supabase")
        print(f"   ✅ Model ID: {model_id}")
        
        print("\n" + "=" * 60)
        print("SUCCESS: Model trained and saved!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train a model')
    parser.add_argument('dataset_id', help='Dataset ID')
    parser.add_argument('model_type', help='Model type (xgboost, lightgbm, catboost, random_forest, logistic_regression, mlp)')
    
    args = parser.parse_args()
    
    success = train_model_simple(args.dataset_id, args.model_type)
    sys.exit(0 if success else 1)
