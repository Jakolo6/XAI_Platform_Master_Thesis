'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { DatasetSelector } from '@/components/datasets/DatasetSelector';
import { Play, ArrowLeft, ArrowRight, CheckCircle2 } from 'lucide-react';
import { modelsAPI } from '@/lib/api';

export const dynamic = 'force-dynamic';

export default function TrainModelPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [selectedDataset, setSelectedDataset] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [hyperparameters, setHyperparameters] = useState<Record<string, any>>({});
  const [training, setTraining] = useState(false);
  const [trainingResult, setTrainingResult] = useState<any>(null);

  // Pre-select dataset from URL parameter
  useEffect(() => {
    const datasetParam = searchParams.get('dataset');
    if (datasetParam) {
      setSelectedDataset(datasetParam);
      setStep(2); // Auto-advance to model selection
    }
  }, [searchParams]);

  const modelTypes = [
    { 
      id: 'xgboost', 
      name: 'XGBoost', 
      description: 'Fast gradient boosting',
      recommended: true,
      speed: 'Fast',
      accuracy: 'High'
    },
    { 
      id: 'lightgbm', 
      name: 'LightGBM', 
      description: 'Light gradient boosting',
      recommended: true,
      speed: 'Very Fast',
      accuracy: 'High'
    },
    { 
      id: 'catboost', 
      name: 'CatBoost', 
      description: 'Categorical boosting',
      recommended: false,
      speed: 'Medium',
      accuracy: 'High'
    },
    { 
      id: 'random_forest', 
      name: 'Random Forest', 
      description: 'Ensemble of trees',
      recommended: false,
      speed: 'Medium',
      accuracy: 'Medium'
    },
    { 
      id: 'logistic_regression', 
      name: 'Logistic Regression', 
      description: 'Linear model',
      recommended: false,
      speed: 'Very Fast',
      accuracy: 'Low'
    },
    { 
      id: 'mlp', 
      name: 'Neural Network', 
      description: 'Multi-layer perceptron',
      recommended: false,
      speed: 'Slow',
      accuracy: 'Medium'
    },
  ];

  const handleTrain = async () => {
    setTraining(true);
    try {
      // Real API call to backend
      const response = await modelsAPI.train({
        name: `${selectedModel}_${selectedDataset}`,
        dataset_id: selectedDataset,
        model_type: selectedModel,
        hyperparameters: hyperparameters
      });

      const result = response.data;
      console.log('Training result:', result); // Debug log
      setTrainingResult(result);
      
      // Show success message and navigate to model detail
      setStep(5); // Move to success step
    } catch (error: any) {
      console.error('Training failed:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      
      let errorMsg = 'Failed to start training.';
      
      if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMsg = error.response.data.message;
      } else if (error.message) {
        errorMsg = error.message;
      }
      
      // Add helpful context
      if (error.response?.status === 400) {
        errorMsg += '\n\nPossible issues:\n- Dataset not processed yet\n- Invalid model type\n- Backend not running';
      }
      
      alert(errorMsg);
    } finally {
      setTraining(false);
    }
  };

  const canProceed = (currentStep: number) => {
    if (currentStep === 1) return selectedDataset !== '';
    if (currentStep === 2) return selectedModel !== '';
    return true;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Train New Model</h1>
          <p className="text-gray-600 mt-2">
            Follow the steps to train a model on your selected dataset
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-12">
          {[1, 2, 3, 4].map((s, idx) => (
            <div key={s} className="flex items-center">
              <div className={`
                flex items-center justify-center w-12 h-12 rounded-full font-bold text-lg
                transition-all duration-300
                ${step >= s 
                  ? 'bg-blue-600 text-white shadow-lg' 
                  : 'bg-gray-200 text-gray-600'
                }
              `}>
                {step > s ? <CheckCircle2 className="h-6 w-6" /> : s}
              </div>
              
              {idx < 3 && (
                <div className={`
                  w-24 h-1 mx-2 transition-all duration-300
                  ${step > s ? 'bg-blue-600' : 'bg-gray-200'}
                `} />
              )}
            </div>
          ))}
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          {/* Step 1: Select Dataset */}
          {step === 1 && (
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Step 1: Select Dataset
                </h2>
                <p className="text-gray-600">
                  Choose a dataset to train your model on
                </p>
              </div>

              <DatasetSelector
                onSelect={setSelectedDataset}
                selectedId={selectedDataset}
              />

              {selectedDataset && (
                <div className="mt-8 flex justify-end">
                  <button
                    onClick={() => setStep(2)}
                    className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Continue
                    <ArrowRight className="h-5 w-5 ml-2" />
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Step 2: Select Model */}
          {step === 2 && (
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Step 2: Select Model Type
                </h2>
                <p className="text-gray-600">
                  Choose the algorithm to train
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {modelTypes.map(model => (
                  <div
                    key={model.id}
                    onClick={() => setSelectedModel(model.id)}
                    className={`
                      relative p-6 rounded-lg border-2 cursor-pointer transition-all
                      hover:shadow-lg hover:scale-[1.02]
                      ${selectedModel === model.id 
                        ? 'border-blue-500 bg-blue-50 shadow-md' 
                        : 'border-gray-200 hover:border-blue-300'
                      }
                    `}
                  >
                    {model.recommended && (
                      <div className="absolute top-2 right-2">
                        <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded">
                          Recommended
                        </span>
                      </div>
                    )}

                    <h3 className="font-bold text-lg text-gray-900 mb-2">
                      {model.name}
                    </h3>
                    <p className="text-sm text-gray-600 mb-4">
                      {model.description}
                    </p>

                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Speed:</span>
                        <span className="font-medium">{model.speed}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Accuracy:</span>
                        <span className="font-medium">{model.accuracy}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 flex justify-between">
                <button
                  onClick={() => setStep(1)}
                  className="flex items-center px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <ArrowLeft className="h-5 w-5 mr-2" />
                  Back
                </button>
                {selectedModel && (
                  <button
                    onClick={() => setStep(3)}
                    className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Continue
                    <ArrowRight className="h-5 w-5 ml-2" />
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Step 3: Configure Hyperparameters */}
          {step === 3 && (
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Step 3: Configure Hyperparameters
                </h2>
                <p className="text-gray-600">
                  Adjust model parameters or use defaults
                </p>
              </div>

              {/* Hyperparameter Configuration */}
              <div className="space-y-6">
                {selectedModel === 'xgboost' && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Learning Rate
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={hyperparameters.learning_rate || 0.1}
                        onChange={(e) => setHyperparameters({...hyperparameters, learning_rate: parseFloat(e.target.value)})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <p className="text-sm text-gray-500 mt-1">Default: 0.1</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Max Depth
                      </label>
                      <input
                        type="number"
                        value={hyperparameters.max_depth || 6}
                        onChange={(e) => setHyperparameters({...hyperparameters, max_depth: parseInt(e.target.value)})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <p className="text-sm text-gray-500 mt-1">Default: 6</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Number of Estimators
                      </label>
                      <input
                        type="number"
                        value={hyperparameters.n_estimators || 100}
                        onChange={(e) => setHyperparameters({...hyperparameters, n_estimators: parseInt(e.target.value)})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <p className="text-sm text-gray-500 mt-1">Default: 100</p>
                    </div>
                  </>
                )}

                {selectedModel === 'lightgbm' && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Learning Rate
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={hyperparameters.learning_rate || 0.1}
                        onChange={(e) => setHyperparameters({...hyperparameters, learning_rate: parseFloat(e.target.value)})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <p className="text-sm text-gray-500 mt-1">Default: 0.1</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Number of Leaves
                      </label>
                      <input
                        type="number"
                        value={hyperparameters.num_leaves || 31}
                        onChange={(e) => setHyperparameters({...hyperparameters, num_leaves: parseInt(e.target.value)})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <p className="text-sm text-gray-500 mt-1">Default: 31</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Number of Estimators
                      </label>
                      <input
                        type="number"
                        value={hyperparameters.n_estimators || 100}
                        onChange={(e) => setHyperparameters({...hyperparameters, n_estimators: parseInt(e.target.value)})}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <p className="text-sm text-gray-500 mt-1">Default: 100</p>
                    </div>
                  </>
                )}

                {(selectedModel === 'random_forest' || selectedModel === 'catboost' || selectedModel === 'logistic_regression' || selectedModel === 'mlp') && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-blue-800">
                      Using default hyperparameters for {modelTypes.find(m => m.id === selectedModel)?.name}.
                      Advanced configuration coming soon!
                    </p>
                  </div>
                )}

                {/* Reset to Defaults Button */}
                <div className="pt-4">
                  <button
                    onClick={() => setHyperparameters({})}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Reset to Defaults
                  </button>
                </div>
              </div>

              <div className="mt-8 flex justify-between">
                <button
                  onClick={() => setStep(2)}
                  className="flex items-center px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <ArrowLeft className="h-5 w-5 mr-2" />
                  Back
                </button>
                <button
                  onClick={() => setStep(4)}
                  className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Continue
                  <ArrowRight className="h-5 w-5 ml-2" />
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Confirm & Train */}
          {step === 4 && (
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Step 4: Confirm & Train
                </h2>
                <p className="text-gray-600">
                  Review your selections and start training
                </p>
              </div>

              {/* Summary */}
              <div className="bg-gray-50 rounded-lg p-6 mb-6">
                <h3 className="font-semibold text-gray-900 mb-4">Training Configuration</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Dataset:</span>
                    <span className="font-medium text-gray-900">{selectedDataset}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Model Type:</span>
                    <span className="font-medium text-gray-900">
                      {modelTypes.find(m => m.id === selectedModel)?.name}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Hyperparameters:</span>
                    <span className="font-medium text-gray-900">
                      {Object.keys(hyperparameters).length > 0 ? 'Custom' : 'Default'}
                    </span>
                  </div>
                  {Object.keys(hyperparameters).length > 0 && (
                    <div className="pl-4 pt-2 space-y-1">
                      {Object.entries(hyperparameters).map(([key, value]) => (
                        <div key={key} className="flex justify-between text-sm">
                          <span className="text-gray-500">{key}:</span>
                          <span className="text-gray-700">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Command Preview */}
              <div className="bg-gray-900 rounded-lg p-4 mb-6">
                <div className="text-gray-400 text-sm mb-2">Command to run:</div>
                <div className="text-green-400 font-mono text-sm">
                  python scripts/train_model_simple.py {selectedDataset} {selectedModel}
                </div>
              </div>

              {/* Training Result */}
              {trainingResult && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                  <div className="flex items-start">
                    <CheckCircle2 className="h-5 w-5 text-green-600 mr-3 mt-0.5" />
                    <div>
                      <p className="font-medium text-green-900 mb-1">Training Started!</p>
                      <p className="text-sm text-green-700">
                        Model ID: <code className="bg-green-100 px-1 rounded">{trainingResult.model_id}</code>
                      </p>
                      <p className="text-sm text-green-700 mt-1">
                        Check the models page to monitor progress.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-between">
                <button
                  onClick={() => setStep(3)}
                  disabled={training}
                  className="flex items-center px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  <ArrowLeft className="h-5 w-5 mr-2" />
                  Back
                </button>
                <button
                  onClick={handleTrain}
                  disabled={training}
                  className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  <Play className="h-5 w-5 mr-2" />
                  {training ? 'Starting Training...' : 'Start Training'}
                </button>
              </div>
            </div>
          )}

          {/* Step 5: Success */}
          {step === 5 && trainingResult && (
            <div>
              <div className="text-center py-12">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-6">
                  <CheckCircle2 className="h-10 w-10 text-green-600" />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  Training Started Successfully!
                </h2>
                <p className="text-gray-600 mb-8 max-w-md mx-auto">
                  Your model is now training. SHAP explanations will be automatically generated when training completes.
                </p>

                <div className="bg-gray-50 rounded-lg p-6 mb-8 max-w-md mx-auto">
                  <div className="space-y-3 text-left">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Model ID:</span>
                      <code className="font-mono text-sm bg-white px-2 py-1 rounded">
                        {trainingResult.model_id || trainingResult.id || 'Processing...'}
                      </code>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Dataset:</span>
                      <span className="font-medium text-gray-900">{selectedDataset}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Model Type:</span>
                      <span className="font-medium text-gray-900">
                        {modelTypes.find(m => m.id === selectedModel)?.name}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex gap-4 justify-center">
                  <button
                    onClick={() => {
                      const modelId = trainingResult.model_id || trainingResult.id;
                      if (modelId) {
                        router.push(`/models/${modelId}`);
                      } else {
                        alert('Model ID not found. Please check the models page.');
                        router.push('/models');
                      }
                    }}
                    className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    View Model Details
                    <ArrowRight className="h-5 w-5 ml-2" />
                  </button>
                  <button
                    onClick={() => {
                      setStep(1);
                      setSelectedDataset('');
                      setSelectedModel('');
                      setTrainingResult(null);
                    }}
                    className="flex items-center px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Train Another Model
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Help Text */}
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>
            Training will run in the background. You can monitor progress in the Models page.
          </p>
        </div>
      </div>
    </div>
  );
}
