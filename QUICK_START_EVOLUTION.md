# ⚡ QUICK START - Platform Evolution

**Goal:** Transform to multi-dataset research platform in 3 weeks

---

## 🎯 WEEK 1: SUPABASE FOUNDATION

### Monday: Setup (2 hours)
```bash
# 1. Create Supabase account
https://supabase.com → Sign up

# 2. Create project
Name: xai-research-platform
Region: [your region]
Password: [secure password]

# 3. Get credentials
Dashboard → Settings → API
Copy: URL, anon key, service key

# 4. Update .env
echo "SUPABASE_URL=https://xxx.supabase.co" >> backend/.env
echo "SUPABASE_KEY=your_anon_key" >> backend/.env
echo "SUPABASE_SERVICE_KEY=your_service_key" >> backend/.env
```

### Tuesday: Database Migration (4 hours)
```bash
# 1. Run migration in Supabase SQL Editor
# Copy from: IMPLEMENTATION_GUIDE.md → Day 2 → Migration Script

# 2. Verify tables created
# Check Supabase Dashboard → Table Editor
# Should see: datasets, models, model_metrics, explanations, experiments, benchmarks
```

### Wednesday: Install Supabase Client (3 hours)
```bash
# 1. Install dependencies
cd backend
pip install supabase-py pyyaml

# 2. Create Supabase client
# Copy from: IMPLEMENTATION_GUIDE.md → Day 3 → Supabase Client

# 3. Test connection
python -c "from app.supabase.client import get_supabase_client; client = get_supabase_client(); print('Connected!')"
```

### Thursday: Dataset Registry (4 hours)
```bash
# 1. Create config directory
mkdir -p config

# 2. Create datasets.yaml
# Copy from: IMPLEMENTATION_GUIDE.md → Day 4 → Dataset Registry Config

# 3. Create registry loader
# Copy from: IMPLEMENTATION_GUIDE.md → Day 4 → Dataset Registry Loader

# 4. Test registry
python -c "from app.datasets.registry import get_dataset_registry; reg = get_dataset_registry(); print(reg.list_datasets())"
```

### Friday: Sync Existing Data (4 hours)
```bash
# 1. Create migration script
cat > backend/scripts/migrate_to_supabase.py << 'EOF'
"""Migrate existing data to Supabase."""

import asyncio
from app.core.database import get_db
from app.supabase.client import get_supabase_client
from app.models.model import Model
from app.models.dataset import Dataset
from sqlalchemy import select

async def migrate():
    supabase = get_supabase_client()
    
    # Migrate datasets
    async for db in get_db():
        result = await db.execute(select(Dataset))
        datasets = result.scalars().all()
        
        for dataset in datasets:
            await supabase.insert_dataset({
                'id': str(dataset.id),
                'name': dataset.name,
                'description': dataset.description,
                'source': dataset.source,
                'status': dataset.status,
                'total_samples': dataset.total_rows,
                'num_features': dataset.total_columns,
            })
        
        # Migrate models
        result = await db.execute(select(Model))
        models = result.scalars().all()
        
        for model in models:
            await supabase.insert_model({
                'id': str(model.id),
                'name': model.name,
                'model_type': model.model_type,
                'dataset_id': str(model.dataset_id),
                'hyperparameters': model.hyperparameters,
                'status': model.status,
            })

if __name__ == '__main__':
    asyncio.run(migrate())
EOF

# 2. Run migration
python backend/scripts/migrate_to_supabase.py

# 3. Verify in Supabase Dashboard
```

---

## 🎯 WEEK 2: MULTI-DATASET SUPPORT

### Monday: Dataset Loaders (4 hours)
```bash
# 1. Create loader structure
mkdir -p backend/app/datasets/loaders

# 2. Create base loader
# Copy from: IMPLEMENTATION_GUIDE.md → Day 5 → Base Dataset Loader

# 3. Create IEEE-CIS loader
# Copy from: IMPLEMENTATION_GUIDE.md → Day 5 → IEEE-CIS Loader

# 4. Test loader
python -c "from app.datasets.loaders.ieee_cis import IEEECISLoader; print('Loader ready!')"
```

### Tuesday: Add New Datasets (6 hours)
```bash
# 1. Create GiveMeSomeCredit loader
cat > backend/app/datasets/loaders/givemesomecredit.py << 'EOF'
from .base import BaseDatasetLoader
from app.utils.kaggle_client import download_kaggle_dataset

class GiveMeSomeCreditLoader(BaseDatasetLoader):
    async def download(self):
        return await download_kaggle_dataset(
            self.config['kaggle_dataset'],
            self.data_dir
        )
    
    def preprocess(self, df):
        # Handle missing
        df = df.fillna(df.median(numeric_only=True))
        
        # Scale
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
        numerical_cols = [c for c in numerical_cols if c != self.config['target_column']]
        df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
        
        return df
EOF

# 2. Create German Credit loader
cat > backend/app/datasets/loaders/german_credit.py << 'EOF'
from .base import BaseDatasetLoader
from app.utils.kaggle_client import download_kaggle_dataset

class GermanCreditLoader(BaseDatasetLoader):
    async def download(self):
        return await download_kaggle_dataset(
            self.config['kaggle_dataset'],
            self.data_dir
        )
    
    def preprocess(self, df):
        # Encode categorical
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col != self.config['target_column']:
                df[col] = df[col].astype('category').cat.codes
        
        # Encode target
        df[self.config['target_column']] = (df[self.config['target_column']] == self.config['positive_class']).astype(int)
        
        # Scale
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
        numerical_cols = [c for c in numerical_cols if c != self.config['target_column']]
        df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
        
        return df
EOF

# 3. Test download and preprocessing
python -c "
from app.datasets.loaders.givemesomecredit import GiveMeSomeCreditLoader
from app.datasets.registry import get_dataset_registry
import asyncio

async def test():
    registry = get_dataset_registry()
    config = registry.get_dataset_config('givemesomecredit')
    loader = GiveMeSomeCreditLoader('givemesomecredit', config)
    await loader.download()
    print('Downloaded!')

asyncio.run(test())
"
```

### Wednesday: Update Backend Endpoints (4 hours)
```bash
# 1. Update training endpoint to accept dataset_id
# Edit: backend/app/api/v1/endpoints/models.py

# Add dataset_id parameter:
@router.post("/train")
async def train_model(
    dataset_id: str,  # NEW
    model_type: str,
    hyperparameters: dict = None,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_researcher)
):
    # Get dataset config
    from app.datasets.registry import get_dataset_registry
    registry = get_dataset_registry()
    dataset_config = registry.get_dataset_config(dataset_id)
    
    # Trigger training task with dataset_id
    task = train_model_task.delay(
        dataset_id=dataset_id,
        model_type=model_type,
        hyperparameters=hyperparameters
    )
    
    return {"task_id": task.id}

# 2. Update explanation endpoint
# Edit: backend/app/api/v1/endpoints/explanations.py

@router.post("/generate")
async def generate_explanation(
    model_id: str,
    dataset_id: str,  # NEW
    method: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_researcher)
):
    # Trigger explanation task
    task = generate_explanation_task.delay(
        model_id=model_id,
        dataset_id=dataset_id,
        method=method
    )
    
    return {"task_id": task.id}
```

### Thursday: Update Celery Tasks (4 hours)
```bash
# 1. Update training task
# Edit: backend/app/tasks/training_tasks.py

@celery_app.task
def train_model_task(dataset_id: str, model_type: str, hyperparameters: dict):
    # Load dataset
    from app.datasets.registry import get_dataset_registry
    from app.datasets.loaders import get_loader
    
    registry = get_dataset_registry()
    config = registry.get_dataset_config(dataset_id)
    
    loader = get_loader(dataset_id, config)
    train_df, val_df, test_df = loader.load_splits()
    
    # Get target column from config
    target_col = config['target_column']
    
    # Train model
    X_train = train_df.drop(target_col, axis=1)
    y_train = train_df[target_col]
    
    # ... rest of training logic ...
    
    # Save to Supabase
    from app.supabase.client import get_supabase_client
    supabase = get_supabase_client()
    
    await supabase.insert_model({
        'dataset_id': dataset_id,
        'model_type': model_type,
        'hyperparameters': hyperparameters,
        # ... metrics ...
    })

# 2. Update explanation task
# Edit: backend/app/tasks/explanation_tasks.py

@celery_app.task
def generate_explanation_task(model_id: str, dataset_id: str, method: str):
    # Load dataset
    from app.datasets.loaders import get_loader
    loader = get_loader(dataset_id, config)
    
    # Generate explanation
    # ...
    
    # Save to Supabase
    from app.supabase.client import get_supabase_client
    supabase = get_supabase_client()
    
    await supabase.insert_explanation({
        'model_id': model_id,
        'dataset_id': dataset_id,
        'method': method,
        'summary_json': summary,
        'top_features': top_features,
        # ... quality metrics ...
    })
```

### Friday: Testing (4 hours)
```bash
# 1. Test dataset loading
python -c "
from app.datasets.loaders import get_loader
from app.datasets.registry import get_dataset_registry

registry = get_dataset_registry()
for dataset_id in ['ieee-cis-fraud', 'givemesomecredit', 'german-credit']:
    config = registry.get_dataset_config(dataset_id)
    loader = get_loader(dataset_id, config)
    train, val, test = loader.load_splits()
    print(f'{dataset_id}: train={len(train)}, val={len(val)}, test={len(test)}')
"

# 2. Test model training
curl -X POST http://localhost:8000/api/v1/models/train \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "givemesomecredit",
    "model_type": "xgboost",
    "hyperparameters": {}
  }'

# 3. Verify in Supabase
# Check Dashboard → Table Editor → models
```

---

## 🎯 WEEK 3: FRONTEND & BENCHMARKING

### Monday: Dataset Selector Component (4 hours)
```typescript
// frontend/src/components/datasets/DatasetSelector.tsx
'use client';

import { useState, useEffect } from 'react';
import { Database, CheckCircle2 } from 'lucide-react';

interface Dataset {
  id: string;
  name: string;
  display_name: string;
  description: string;
  total_samples: number;
  num_features: number;
  tags: string[];
}

export function DatasetSelector({ onSelect, selectedId }: {
  onSelect: (id: string) => void;
  selectedId?: string;
}) {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const response = await fetch('/api/v1/datasets');
      const data = await response.json();
      setDatasets(data);
    } catch (error) {
      console.error('Failed to fetch datasets:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading datasets...</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {datasets.map(dataset => (
        <div
          key={dataset.id}
          onClick={() => onSelect(dataset.id)}
          className={`
            p-6 rounded-lg border-2 cursor-pointer transition-all
            ${selectedId === dataset.id 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-200 hover:border-blue-300'
            }
          `}
        >
          <div className="flex items-start justify-between mb-3">
            <Database className="h-8 w-8 text-blue-600" />
            {selectedId === dataset.id && (
              <CheckCircle2 className="h-6 w-6 text-blue-600" />
            )}
          </div>
          
          <h3 className="text-lg font-bold text-gray-900 mb-2">
            {dataset.display_name}
          </h3>
          
          <p className="text-sm text-gray-600 mb-4">
            {dataset.description}
          </p>
          
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>{dataset.total_samples?.toLocaleString()} samples</span>
            <span>{dataset.num_features} features</span>
          </div>
          
          {dataset.tags && (
            <div className="flex flex-wrap gap-2 mt-3">
              {dataset.tags.map(tag => (
                <span
                  key={tag}
                  className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
```

### Tuesday: Dataset Management Page (4 hours)
```typescript
// frontend/src/app/datasets/page.tsx
/**
 * DATASETS PAGE
 * Route: /datasets
 * 
 * Manage and view all datasets.
 * Add new datasets, view statistics, download data.
 */

'use client';

import { useState, useEffect } from 'react';
import { DatasetSelector } from '@/components/datasets/DatasetSelector';
import { Database, Plus, Download } from 'lucide-react';
import Link from 'next/link';

export default function DatasetsPage() {
  const [selectedDataset, setSelectedDataset] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Datasets</h1>
            <p className="text-gray-600 mt-2">
              Manage datasets for model training and evaluation
            </p>
          </div>
          
          <Link
            href="/datasets/add"
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="h-5 w-5 mr-2" />
            Add Dataset
          </Link>
        </div>

        {/* Dataset Selector */}
        <DatasetSelector
          onSelect={setSelectedDataset}
          selectedId={selectedDataset}
        />

        {/* Selected Dataset Details */}
        {selectedDataset && (
          <div className="mt-8 bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Dataset Details</h2>
            {/* Add dataset statistics, preview, etc. */}
          </div>
        )}
      </div>
    </div>
  );
}
```

### Wednesday: Update Model Training UI (4 hours)
```typescript
// frontend/src/app/models/train/page.tsx
'use client';

import { useState } from 'react';
import { DatasetSelector } from '@/components/datasets/DatasetSelector';
import { modelsAPI } from '@/lib/api';

export default function TrainModelPage() {
  const [selectedDataset, setSelectedDataset] = useState<string>('');
  const [modelType, setModelType] = useState<string>('xgboost');
  const [training, setTraining] = useState(false);

  const handleTrain = async () => {
    if (!selectedDataset) {
      alert('Please select a dataset');
      return;
    }

    setTraining(true);
    try {
      const response = await modelsAPI.train({
        dataset_id: selectedDataset,
        model_type: modelType,
        hyperparameters: {}
      });
      
      alert('Training started! Task ID: ' + response.data.task_id);
    } catch (error) {
      console.error('Training failed:', error);
      alert('Training failed');
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Train New Model</h1>

      {/* Step 1: Select Dataset */}
      <div className="mb-8">
        <h2 className="text-xl font-bold mb-4">1. Select Dataset</h2>
        <DatasetSelector
          onSelect={setSelectedDataset}
          selectedId={selectedDataset}
        />
      </div>

      {/* Step 2: Select Model Type */}
      {selectedDataset && (
        <div className="mb-8">
          <h2 className="text-xl font-bold mb-4">2. Select Model Type</h2>
          <div className="grid grid-cols-3 gap-4">
            {['xgboost', 'lightgbm', 'catboost', 'random_forest'].map(type => (
              <button
                key={type}
                onClick={() => setModelType(type)}
                className={`
                  p-4 rounded-lg border-2 transition-all
                  ${modelType === type 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-blue-300'
                  }
                `}
              >
                {type.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step 3: Train */}
      {selectedDataset && modelType && (
        <div>
          <button
            onClick={handleTrain}
            disabled={training}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {training ? 'Training...' : 'Start Training'}
          </button>
        </div>
      )}
    </div>
  );
}
```

### Thursday: Cross-Dataset Comparison (4 hours)
```typescript
// frontend/src/app/benchmarks/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function BenchmarksPage() {
  const [benchmarkData, setBenchmarkData] = useState([]);

  useEffect(() => {
    fetchBenchmarks();
  }, []);

  const fetchBenchmarks = async () => {
    const response = await fetch('/api/v1/benchmarks');
    const data = await response.json();
    
    // Transform for chart
    const chartData = data.map(item => ({
      dataset: item.dataset_name,
      xgboost_auc: item.models.xgboost?.auc_roc,
      lightgbm_auc: item.models.lightgbm?.auc_roc,
      catboost_auc: item.models.catboost?.auc_roc,
    }));
    
    setBenchmarkData(chartData);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Cross-Dataset Benchmarks</h1>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Model Performance Across Datasets</h2>
        
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={benchmarkData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="dataset" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="xgboost_auc" fill="#3B82F6" name="XGBoost" />
            <Bar dataKey="lightgbm_auc" fill="#10B981" name="LightGBM" />
            <Bar dataKey="catboost_auc" fill="#F59E0B" name="CatBoost" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
```

### Friday: Documentation & Testing (4 hours)
```bash
# 1. Update README
cat >> README.md << 'EOF'

## 🗂️ Multi-Dataset Support

### Adding a New Dataset

1. Add to `config/datasets.yaml`:
```yaml
- id: my-dataset
  name: my-dataset
  display_name: "My Dataset"
  source: kaggle
  kaggle_dataset: username/dataset-name
  target_column: target
  positive_class: 1
```

2. Create loader in `backend/app/datasets/loaders/my_dataset.py`

3. Register in Supabase via API or dashboard

4. Download and preprocess:
```bash
python scripts/download_dataset.py my-dataset
```

### Supported Datasets

- **IEEE-CIS Fraud Detection** - 590K transactions, fraud detection
- **Give Me Some Credit** - 150K records, credit default prediction
- **German Credit Risk** - 1K records, credit risk classification

EOF

# 2. Create dataset download script
cat > backend/scripts/download_dataset.py << 'EOF'
import sys
import asyncio
from app.datasets.registry import get_dataset_registry
from app.datasets.loaders import get_loader

async def download(dataset_id: str):
    registry = get_dataset_registry()
    config = registry.get_dataset_config(dataset_id)
    
    loader = get_loader(dataset_id, config)
    await loader.download()
    
    print(f"✅ Downloaded {dataset_id}")

if __name__ == '__main__':
    dataset_id = sys.argv[1] if len(sys.argv) > 1 else 'ieee-cis-fraud'
    asyncio.run(download(dataset_id))
EOF

# 3. Test everything
python backend/scripts/download_dataset.py givemesomecredit
python backend/scripts/download_dataset.py german-credit

# 4. Train models on all datasets
for dataset in ieee-cis-fraud givemesomecredit german-credit; do
  curl -X POST http://localhost:8000/api/v1/models/train \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"dataset_id\": \"$dataset\", \"model_type\": \"xgboost\"}"
done
```

---

## ✅ COMPLETION CHECKLIST

### Week 1: Supabase Foundation
- [ ] Supabase project created
- [ ] Database schema migrated
- [ ] Supabase client implemented
- [ ] Dataset registry created
- [ ] Existing data migrated

### Week 2: Multi-Dataset Support
- [ ] Base dataset loader created
- [ ] 3 dataset loaders implemented
- [ ] Backend endpoints updated
- [ ] Celery tasks updated
- [ ] Multi-dataset training tested

### Week 3: Frontend & Benchmarking
- [ ] Dataset selector component
- [ ] Dataset management page
- [ ] Model training UI updated
- [ ] Cross-dataset comparison
- [ ] Documentation complete

---

## 🎯 SUCCESS CRITERIA

✅ Can train models on 3+ datasets
✅ All metadata stored in Supabase
✅ Raw data stays local
✅ Cross-dataset benchmarking works
✅ Frontend shows dataset selector
✅ Documentation complete

---

## 🚀 LAUNCH

After 3 weeks:
1. ✅ Commit all changes
2. ✅ Push to GitHub
3. ✅ Make repository public
4. ✅ Add comprehensive README
5. ✅ Create release v2.0.0
6. ✅ Share on research communities
7. ✅ Submit paper

**You'll have a publication-worthy research platform!** 🎓✨
