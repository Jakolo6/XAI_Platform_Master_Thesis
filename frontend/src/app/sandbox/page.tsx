/**
 * EXPLAINABLE AI
 * Route: /sandbox
 * 
 * Generate and compare SHAP and LIME explanations for trained models
 * Visualize global and local feature importance with side-by-side comparison
 * Compares SHAP vs LIME for the same prediction with human-readable insights
 */

'use client';

export const dynamic = 'force-dynamic';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Brain, 
  Lightbulb, 
  TrendingUp, 
  TrendingDown, 
  AlertCircle,
  Sliders,
  Globe,
  Target,
  ThumbsUp,
  ThumbsDown,
  Star,
  RefreshCw,
  ChevronRight,
  Info
} from 'lucide-react';
import { explanationsAPI, modelsAPI } from '@/lib/api';

type ViewMode = 'local' | 'global';
type ExplanationMethod = 'shap' | 'lime';

interface PredictionInstance {
  instance_id: string;
  features: Record<string, any>;
  prediction: number;
  true_label?: string;
  model_output: string;
}

interface FeatureContribution {
  feature: string;
  value: any;
  contribution: number;
  importance: number;
}

interface ExplanationData {
  method: ExplanationMethod;
  features: FeatureContribution[];
  prediction_proba: number;
  base_value?: number;
}

export default function ExplainableAI() {
  const router = useRouter();
  
  // State
  const [viewMode, setViewMode] = useState<ViewMode>('local');
  const [selectedModel, setSelectedModel] = useState<any>(null);
  const [models, setModels] = useState<any[]>([]);
  const [selectedInstance, setSelectedInstance] = useState<PredictionInstance | null>(null);
  const [shapExplanation, setShapExplanation] = useState<ExplanationData | null>(null);
  const [limeExplanation, setLimeExplanation] = useState<ExplanationData | null>(null);
  const [interpretation, setInterpretation] = useState<string>('');
  const [showDisagreement, setShowDisagreement] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // What-if analysis
  const [whatIfFeature, setWhatIfFeature] = useState<string | null>(null);
  const [whatIfValue, setWhatIfValue] = useState<number>(0);
  
  // Human rating
  const [clarity, setClarity] = useState(0);
  const [trustworthiness, setTrustworthiness] = useState(0);
  const [actionability, setActionability] = useState(0);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const response = await modelsAPI.getAll();
      const completedModels = response.data.filter((m: any) => m.status === 'completed');
      setModels(completedModels);
      if (completedModels.length > 0) {
        setSelectedModel(completedModels[0]);
      }
    } catch (error) {
      console.error('Failed to load models:', error);
      setError('Failed to load models. Please ensure backend is running.');
    }
  };

  const loadSampleInstance = async () => {
    if (!selectedModel) return;
    
    setIsLoading(true);
    setError(null);
    try {
      if (viewMode === 'local') {
        // Load a sample prediction instance for local view
        const response = await explanationsAPI.getSampleInstance(selectedModel.model_id);
        setSelectedInstance(response.data);
        
        // Load local explanations for this instance
        await loadExplanations(response.data.instance_id);
      } else {
        // Load global explanations for the model
        await loadGlobalExplanations();
      }
    } catch (error: any) {
      console.error('Failed to load sample:', error);
      setError('Failed to load sample instance. Please try another model.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadExplanations = async (instanceId: string) => {
    if (!selectedModel) return;
    
    try {
      // Load both SHAP and LIME local explanations
      const [shapResponse, limeResponse] = await Promise.all([
        explanationsAPI.getLocalExplanation(selectedModel.model_id, instanceId, 'shap'),
        explanationsAPI.getLocalExplanation(selectedModel.model_id, instanceId, 'lime')
      ]);
      
      setShapExplanation(shapResponse.data);
      setLimeExplanation(limeResponse.data);
      
      // Generate interpretation
      generateInterpretation(shapResponse.data, limeResponse.data);
    } catch (error) {
      console.error('Failed to load explanations:', error);
      setError('Failed to load explanations for this instance.');
    }
  };

  const loadGlobalExplanations = async () => {
    if (!selectedModel) return;
    
    try {
      // Load global explanations using the new endpoint
      const response = await explanationsAPI.getGlobalExplanations(selectedModel.model_id);
      const { shap, lime, has_shap, has_lime } = response.data;
      
      if (!has_shap && !has_lime) {
        setError('Global explanations not found. Please generate explanations for this model first.');
        return;
      }
      
      // Load SHAP if available
      if (has_shap && shap) {
        const shapData = {
          method: 'shap' as const,
          features: Object.entries(shap.feature_importance || {}).map(([name, value]) => ({
            feature: name,
            contribution: value as number,
            value: value as number,
            importance: Math.abs(value as number)
          })),
          prediction_proba: 0,
          base_value: 0
        };
        setShapExplanation(shapData);
      }
      
      // Load LIME if available
      if (has_lime && lime) {
        const limeData = {
          method: 'lime' as const,
          features: Object.entries(lime.feature_importance || {}).map(([name, value]) => ({
            feature: name,
            contribution: value as number,
            value: value as number,
            importance: Math.abs(value as number)
          })),
          prediction_proba: 0
        };
        setLimeExplanation(limeData);
      }
      
      // Show info if only one method is available
      if (has_shap && !has_lime) {
        setError('Only SHAP explanation available. Generate LIME to compare both methods.');
      } else if (has_lime && !has_shap) {
        setError('Only LIME explanation available. Generate SHAP to compare both methods.');
      }
    } catch (error) {
      console.error('Failed to load global explanations:', error);
      setError('Failed to load global explanations. Please generate them first from the model detail page.');
    }
  };

  const generateInterpretation = (shap: ExplanationData, lime: ExplanationData) => {
    // Generate human-readable interpretation for local view
    const topShapFeatures = shap.features.slice(0, 3);
    const topLimeFeatures = lime.features.slice(0, 3);
    
    const prediction = shap.prediction_proba > 0.5 ? 'fraud' : 'legitimate';
    const confidence = (shap.prediction_proba * 100).toFixed(1);
    
    let text = `The model predicts this transaction as **${prediction}** with ${confidence}% confidence.\n\n`;
    
    text += `**Key Drivers (SHAP):**\n`;
    topShapFeatures.forEach(f => {
      const direction = f.contribution > 0 ? 'increased' : 'decreased';
      text += `- ${f.feature} (${f.value}): ${direction} ${prediction} probability by ${Math.abs(f.contribution).toFixed(3)}\n`;
    });
    
    text += `\n**Key Drivers (LIME):**\n`;
    topLimeFeatures.forEach(f => {
      const direction = f.contribution > 0 ? 'increased' : 'decreased';
      text += `- ${f.feature} (${f.value}): ${direction} ${prediction} probability by ${Math.abs(f.contribution).toFixed(3)}\n`;
    });
    
    // Check for disagreements
    const disagreements = findDisagreements(shap.features, lime.features);
    if (disagreements.length > 0) {
      text += `\n**⚠️ Method Disagreements:**\n`;
      disagreements.forEach(d => {
        text += `- ${d.feature}: SHAP emphasizes ${d.shap > 0 ? 'positive' : 'negative'} impact, LIME shows ${d.lime > 0 ? 'positive' : 'negative'} impact\n`;
      });
    }
    
    setInterpretation(text);
  };

  const generateGlobalInterpretation = (shapExp: any, limeExp: any) => {
    // Generate human-readable interpretation for global view
    const shapFeatures = shapExp.explanation_data?.features || [];
    const limeFeatures = limeExp.explanation_data?.features || [];
    
    const topShapFeatures = shapFeatures.slice(0, 5);
    const topLimeFeatures = limeFeatures.slice(0, 5);
    
    let text = `**Global Feature Importance Analysis**\n\n`;
    text += `This shows which features are most important for the model's predictions across the entire dataset.\n\n`;
    
    text += `**Most Important Features (SHAP):**\n`;
    topShapFeatures.forEach((f: any, idx: number) => {
      text += `${idx + 1}. **${f.feature}**: Average importance of ${Math.abs(f.importance || f.contribution).toFixed(3)}\n`;
    });
    
    text += `\n**Most Important Features (LIME):**\n`;
    topLimeFeatures.forEach((f: any, idx: number) => {
      text += `${idx + 1}. **${f.feature}**: Average importance of ${Math.abs(f.importance || f.contribution).toFixed(3)}\n`;
    });
    
    // Check for disagreements in feature ranking
    const topShapNames = topShapFeatures.map((f: any) => f.feature);
    const topLimeNames = topLimeFeatures.map((f: any) => f.feature);
    const commonFeatures = topShapNames.filter((name: string) => topLimeNames.includes(name));
    
    text += `\n**Method Agreement:**\n`;
    text += `Both methods agree on ${commonFeatures.length} out of top 5 features: ${commonFeatures.join(', ') || 'None'}\n`;
    
    setInterpretation(text);
  };

  const findDisagreements = (shapFeatures: FeatureContribution[], limeFeatures: FeatureContribution[]) => {
    const disagreements: any[] = [];
    
    shapFeatures.forEach(sf => {
      const lf = limeFeatures.find(l => l.feature === sf.feature);
      if (lf && Math.sign(sf.contribution) !== Math.sign(lf.contribution)) {
        disagreements.push({
          feature: sf.feature,
          shap: sf.contribution,
          lime: lf.contribution
        });
      }
    });
    
    return disagreements;
  };

  const handleWhatIf = async (feature: string, newValue: number) => {
    if (!selectedModel || !selectedInstance) return;
    
    try {
      // Call what-if analysis endpoint
      const response = await explanationsAPI.whatIfAnalysis(
        selectedModel.model_id,
        selectedInstance.instance_id,
        feature,
        newValue
      );
      
      // Update explanations with new values
      setShapExplanation(response.data.shap);
      setLimeExplanation(response.data.lime);
      generateInterpretation(response.data.shap, response.data.lime);
    } catch (error) {
      console.error('What-if analysis failed:', error);
    }
  };

  const submitRating = async () => {
    if (!selectedModel || !selectedInstance) return;
    
    try {
      await explanationsAPI.submitInterpretabilityRating({
        model_id: selectedModel.model_id,
        instance_id: selectedInstance.instance_id,
        clarity,
        trustworthiness,
        actionability,
        shap_method: 'shap',
        lime_method: 'lime'
      });
      
      alert('Thank you for your feedback!');
      // Reset ratings
      setClarity(0);
      setTrustworthiness(0);
      setActionability(0);
    } catch (error) {
      console.error('Failed to submit rating:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl">
                <Lightbulb className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Explainable AI</h1>
                <p className="text-gray-600 mt-1">
                  Generate and compare SHAP and LIME explanations for your trained models
                </p>
              </div>
            </div>
            
            {/* Global vs Local Toggle */}
            <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => {
                  setViewMode('local');
                  setSelectedInstance(null);
                  setShapExplanation(null);
                  setLimeExplanation(null);
                  setInterpretation('');
                }}
                className={`px-4 py-2 rounded-md flex items-center space-x-2 transition-colors ${
                  viewMode === 'local'
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Target className="h-4 w-4" />
                <span>Local View</span>
              </button>
              <button
                onClick={() => {
                  setViewMode('global');
                  setSelectedInstance(null);
                  setShapExplanation(null);
                  setLimeExplanation(null);
                  setInterpretation('');
                }}
                className={`px-4 py-2 rounded-md flex items-center space-x-2 transition-colors ${
                  viewMode === 'global'
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Globe className="h-4 w-4" />
                <span>Global View</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Model Context Panel */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <Brain className="h-5 w-5 text-indigo-600" />
            <span>1. Model Context</span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Model
              </label>
              <select
                value={selectedModel?.model_id || ''}
                onChange={(e) => {
                  const model = models.find(m => m.model_id === e.target.value);
                  setSelectedModel(model);
                  setSelectedInstance(null);
                  setShapExplanation(null);
                  setLimeExplanation(null);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Choose a model...</option>
                {models.map(model => (
                  <option key={model.model_id} value={model.model_id}>
                    {model.name} - {model.model_type}
                  </option>
                ))}
              </select>
            </div>
            
            {selectedModel && (
              <>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Dataset</p>
                  <p className="text-lg font-semibold text-gray-900">{selectedModel.dataset_id}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Model Type</p>
                  <p className="text-lg font-semibold text-gray-900">{selectedModel.model_type}</p>
                </div>
              </>
            )}
          </div>
          
          {selectedModel && (
            <button
              onClick={loadSampleInstance}
              disabled={isLoading}
              className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              <span>
                {isLoading 
                  ? 'Loading...' 
                  : viewMode === 'local' 
                    ? 'Load Sample Prediction' 
                    : 'Load Global Explanations'}
              </span>
            </button>
          )}
          
          {viewMode === 'local' && selectedInstance && (
            <div className="mt-4 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
              <p className="text-sm font-medium text-indigo-900 mb-2">
                Target Prediction: <span className="font-bold">{selectedInstance.model_output}</span>
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                {Object.entries(selectedInstance.features).slice(0, 8).map(([key, value]) => (
                  <div key={key} className="bg-white rounded px-2 py-1">
                    <span className="text-gray-600">{key}:</span>
                    <span className="ml-1 font-medium text-gray-900">{String(value)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {viewMode === 'global' && shapExplanation && (
            <div className="mt-4 p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <p className="text-sm font-medium text-purple-900">
                Showing global feature importance across the entire dataset
              </p>
            </div>
          )}
        </div>

        {/* Explanation Comparison Panel */}
        {shapExplanation && limeExplanation && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* SHAP Explanation */}
              <ExplanationCard
                title="SHAP Explanation"
                method="shap"
                explanation={shapExplanation}
                color="blue"
              />
              
              {/* LIME Explanation */}
              <ExplanationCard
                title="LIME Explanation"
                method="lime"
                explanation={limeExplanation}
                color="orange"
              />
            </div>

            {/* Interpretation Layer */}
            <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
                  <Info className="h-5 w-5 text-purple-600" />
                  <span>3. Human-Readable Interpretation</span>
                </h2>
                <button
                  onClick={() => setShowDisagreement(!showDisagreement)}
                  className="text-sm text-purple-600 hover:text-purple-700 flex items-center space-x-1"
                >
                  <AlertCircle className="h-4 w-4" />
                  <span>{showDisagreement ? 'Hide' : 'Show'} Disagreements</span>
                </button>
              </div>
              
              <div className="prose max-w-none">
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 whitespace-pre-line">
                  {interpretation}
                </div>
              </div>
            </div>

            {/* Human Interpretability Rating */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
                <Star className="h-5 w-5 text-yellow-500" />
                <span>4. Rate This Explanation</span>
              </h2>
              
              <p className="text-gray-600 mb-6">
                Help improve XAI by rating how well these explanations helped you understand the prediction.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <RatingInput
                  label="Clarity"
                  description="How clear and understandable was the explanation?"
                  value={clarity}
                  onChange={setClarity}
                />
                <RatingInput
                  label="Trustworthiness"
                  description="How much do you trust this explanation?"
                  value={trustworthiness}
                  onChange={setTrustworthiness}
                />
                <RatingInput
                  label="Actionability"
                  description="Can you take action based on this explanation?"
                  value={actionability}
                  onChange={setActionability}
                />
              </div>
              
              <button
                onClick={submitRating}
                disabled={clarity === 0 || trustworthiness === 0 || actionability === 0}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Submit Rating
              </button>
            </div>
          </>
        )}

        {/* Empty State */}
        {!selectedInstance && !isLoading && (
          <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
            <Lightbulb className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Start Exploring Explanations
            </h3>
            <p className="text-gray-600 mb-6">
              Select a model and load a sample prediction to begin interpreting AI decisions.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

// Helper Components

interface ExplanationCardProps {
  title: string;
  method: ExplanationMethod;
  explanation: ExplanationData;
  color: 'blue' | 'orange';
}

function ExplanationCard({ title, method, explanation, color }: ExplanationCardProps) {
  const colorClasses = {
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-900',
      bar: 'bg-blue-500',
      negBar: 'bg-red-500'
    },
    orange: {
      bg: 'bg-orange-50',
      border: 'border-orange-200',
      text: 'text-orange-900',
      bar: 'bg-orange-500',
      negBar: 'bg-red-500'
    }
  };
  
  const colors = colorClasses[color];
  const topFeatures = explanation.features.slice(0, 10);
  const maxContribution = Math.max(...topFeatures.map(f => Math.abs(f.contribution)));
  
  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">{title}</h3>
      
      <div className={`${colors.bg} ${colors.border} border rounded-lg p-4 mb-4`}>
        <p className="text-sm font-medium ${colors.text}">
          Prediction Probability: <span className="text-2xl font-bold">{(explanation.prediction_proba * 100).toFixed(1)}%</span>
        </p>
      </div>
      
      <div className="space-y-3">
        {topFeatures.map((feature, idx) => {
          const width = (Math.abs(feature.contribution) / maxContribution) * 100;
          const isPositive = feature.contribution > 0;
          
          return (
            <div key={idx} className="group">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">{feature.feature}</span>
                <span className="text-xs text-gray-500">{String(feature.value)}</span>
              </div>
              
              <div className="relative h-6 bg-gray-100 rounded overflow-hidden">
                <div
                  className={`absolute h-full ${isPositive ? colors.bar : colors.negBar} transition-all`}
                  style={{ width: `${width}%` }}
                />
                <div className="absolute inset-0 flex items-center px-2">
                  <span className="text-xs font-medium text-white">
                    {isPositive ? '+' : ''}{feature.contribution.toFixed(3)}
                  </span>
                </div>
              </div>
              
              {/* Tooltip on hover */}
              <div className="hidden group-hover:block mt-1 text-xs text-gray-600 bg-gray-50 rounded p-2">
                {isPositive ? <TrendingUp className="h-3 w-3 inline mr-1" /> : <TrendingDown className="h-3 w-3 inline mr-1" />}
                {feature.feature} = {String(feature.value)} {isPositive ? 'increased' : 'decreased'} prediction by {Math.abs(feature.contribution).toFixed(3)}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

interface RatingInputProps {
  label: string;
  description: string;
  value: number;
  onChange: (value: number) => void;
}

function RatingInput({ label, description, value, onChange }: RatingInputProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-900 mb-1">{label}</label>
      <p className="text-xs text-gray-600 mb-3">{description}</p>
      <div className="flex space-x-2">
        {[1, 2, 3, 4, 5].map(rating => (
          <button
            key={rating}
            onClick={() => onChange(rating)}
            className={`w-10 h-10 rounded-lg border-2 transition-all ${
              value >= rating
                ? 'bg-yellow-400 border-yellow-500 text-white'
                : 'bg-white border-gray-300 text-gray-400 hover:border-yellow-400'
            }`}
          >
            {rating}
          </button>
        ))}
      </div>
    </div>
  );
}
