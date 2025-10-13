/**
 * INTERPRETATION LAYER PAGE
 * Route: /interpretation
 * 
 * Compares LLM-driven vs Rule-based interpretation of SHAP values
 * for Home Credit Default Risk predictions
 */

'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import { 
  Brain, 
  MessageSquare, 
  AlertCircle, 
  Info, 
  Sparkles,
  Download,
  RefreshCw,
  Star,
  CheckCircle2,
  Zap,
  FileText
} from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://xaiplatformmasterthesis-production.up.railway.app/api/v1';

interface Model {
  id: string;
  name: string;
  model_type: string;
  dataset_id: string;
}

interface ShapData {
  features: Array<{
    feature: string;
    contribution: number;
    value: any;
  }>;
  prediction: string;
  prediction_proba: number;
}

interface Interpretation {
  mode: string;
  interpretation: string;
  top_features: string[];
  confidence: number;
  prediction: string;
  method: string;
  tokens_used?: number;
}

export default function InterpretationLayerPage() {
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [shapData, setShapData] = useState<ShapData | null>(null);
  const [mode, setMode] = useState<'llm' | 'rule-based' | 'compare'>('compare');
  const [llmInterpretation, setLlmInterpretation] = useState<Interpretation | null>(null);
  const [ruleInterpretation, setRuleInterpretation] = useState<Interpretation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Rating state
  const [clarity, setClarity] = useState(0);
  const [trustworthiness, setTrustworthiness] = useState(0);
  const [fairness, setFairness] = useState(0);

  // Load models on mount
  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/models/`);
      setModels(response.data);
    } catch (err) {
      console.error('Failed to load models:', err);
      setError('Failed to load models');
    }
  };

  const loadShapData = async () => {
    if (!selectedModel) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(
        `${API_BASE_URL}/interpretation/model/${selectedModel.id}/shap`
      );
      
      // Transform SHAP explanation to expected format
      const shapExplanation = response.data;
      const transformedData: ShapData = {
        features: Object.entries(shapExplanation.feature_importance || {}).map(([name, value]) => ({
          feature: name,
          contribution: value as number,
          value: value
        })).slice(0, 10), // Top 10 features
        prediction: shapExplanation.prediction || 'Unknown',
        prediction_proba: 0.5 // Default, can be enhanced
      };
      
      setShapData(transformedData);
    } catch (err: any) {
      console.error('Failed to load SHAP data:', err);
      
      // Handle detailed error response
      const errorDetail = err.response?.data?.detail;
      if (typeof errorDetail === 'object' && errorDetail.help) {
        setError(errorDetail.help);
      } else if (typeof errorDetail === 'string') {
        setError(errorDetail);
      } else {
        setError('Failed to load SHAP data. This model may not have SHAP explanations generated yet. Please train a new model or select a different one.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const generateInterpretation = async () => {
    if (!selectedModel || !shapData) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      if (mode === 'compare') {
        // Generate both
        const response = await axios.post(
          `${API_BASE_URL}/interpretation/compare`,
          {
            model_id: selectedModel.id,
            shap_data: shapData
          },
          {
            params: { model_id: selectedModel.id }
          }
        );
        
        setLlmInterpretation(response.data.llm);
        setRuleInterpretation(response.data.rule_based);
      } else {
        // Generate single
        const response = await axios.post(
          `${API_BASE_URL}/interpretation/generate`,
          {
            model_id: selectedModel.id,
            shap_data: shapData,
            mode: mode
          }
        );
        
        if (mode === 'llm') {
          setLlmInterpretation(response.data);
        } else {
          setRuleInterpretation(response.data);
        }
      }
    } catch (err: any) {
      console.error('Failed to generate interpretation:', err);
      setError(err.response?.data?.detail || 'Failed to generate interpretation');
    } finally {
      setIsLoading(false);
    }
  };

  const submitFeedback = async (interpretationMode: string) => {
    if (!clarity || !trustworthiness || !fairness) {
      alert('Please rate all dimensions');
      return;
    }
    
    try {
      await axios.post(`${API_BASE_URL}/interpretation/feedback`, {
        interpretation_id: `${selectedModel?.id}_${interpretationMode}_${Date.now()}`,
        model_id: selectedModel?.id,
        mode: interpretationMode,
        clarity,
        trustworthiness,
        fairness
      });
      
      alert('Thank you for your feedback!');
      setClarity(0);
      setTrustworthiness(0);
      setFairness(0);
    } catch (err) {
      console.error('Failed to submit feedback:', err);
      alert('Failed to submit feedback');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-4 mb-4">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl">
              <MessageSquare className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900">Interpretation Layer</h1>
              <p className="text-lg text-gray-600 mt-2">
                Translating AI into Human Reasoning
              </p>
            </div>
          </div>
        </div>

        {/* Info Banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <div className="flex items-start space-x-3">
            <Info className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-900 mb-2">Master's Thesis Research</h3>
              <p className="text-blue-800 text-sm">
                This page compares two paradigms of interpretability translation for financial AI:
                <strong> (1) LLM-driven</strong> natural language generation using GPT-4, and
                <strong> (2) Rule-based</strong> deterministic SHAP reasoning.
                Your ratings help evaluate which approach provides better explanations.
              </p>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Section 1: Model Selection */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <Brain className="h-5 w-5 text-indigo-600" />
            <span>1. Select Model</span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Trained Model
              </label>
              <select
                value={selectedModel?.id || ''}
                onChange={(e) => {
                  const model = models.find(m => m.id === e.target.value);
                  setSelectedModel(model || null);
                  setShapData(null);
                  setLlmInterpretation(null);
                  setRuleInterpretation(null);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Choose a model...</option>
                {models.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name} ({model.model_type})
                  </option>
                ))}
              </select>
            </div>
            
            {selectedModel && (
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Dataset</p>
                <p className="text-lg font-semibold text-gray-900">{selectedModel.dataset_id}</p>
              </div>
            )}
          </div>
          
          {selectedModel && !shapData && (
            <button
              onClick={loadShapData}
              disabled={isLoading}
              className="mt-4 flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              <span>{isLoading ? 'Loading...' : 'Load SHAP Data'}</span>
            </button>
          )}
        </div>

        {/* Section 2: SHAP Data Preview */}
        {shapData && (
          <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
              <FileText className="h-5 w-5 text-indigo-600" />
              <span>2. SHAP Output (Top Features)</span>
            </h2>
            
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <p className="text-sm font-semibold text-gray-700 mb-2">
                Prediction: <span className="text-indigo-600">{shapData.prediction}</span>
              </p>
              <div className="space-y-2">
                {shapData.features.slice(0, 5).map((feature, idx) => (
                  <div key={idx} className="flex justify-between items-center text-sm">
                    <span className="text-gray-700">{feature.feature}</span>
                    <span className={`font-mono ${feature.contribution > 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {feature.contribution > 0 ? '+' : ''}{feature.contribution.toFixed(3)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Section 3: Mode Selection */}
        {shapData && (
          <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">3. Select Interpretation Mode</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <button
                onClick={() => setMode('llm')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  mode === 'llm' 
                    ? 'border-purple-500 bg-purple-50' 
                    : 'border-gray-200 hover:border-purple-300'
                }`}
              >
                <Sparkles className="h-6 w-6 text-purple-600 mb-2" />
                <h3 className="font-semibold text-gray-900">LLM Mode</h3>
                <p className="text-sm text-gray-600">GPT-4 Turbo</p>
              </button>
              
              <button
                onClick={() => setMode('rule-based')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  mode === 'rule-based' 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <Zap className="h-6 w-6 text-blue-600 mb-2" />
                <h3 className="font-semibold text-gray-900">Rule-Based</h3>
                <p className="text-sm text-gray-600">Deterministic</p>
              </button>
              
              <button
                onClick={() => setMode('compare')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  mode === 'compare' 
                    ? 'border-green-500 bg-green-50' 
                    : 'border-gray-200 hover:border-green-300'
                }`}
              >
                <CheckCircle2 className="h-6 w-6 text-green-600 mb-2" />
                <h3 className="font-semibold text-gray-900">Compare Both</h3>
                <p className="text-sm text-gray-600">Side-by-side</p>
              </button>
            </div>
            
            <button
              onClick={generateInterpretation}
              disabled={isLoading}
              className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 font-semibold"
            >
              <Sparkles className={`h-5 w-5 ${isLoading ? 'animate-spin' : ''}`} />
              <span>{isLoading ? 'Generating...' : 'Generate Interpretation'}</span>
            </button>
          </div>
        )}

        {/* Section 4: Comparison Panel */}
        {(llmInterpretation || ruleInterpretation) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* LLM Interpretation */}
            {llmInterpretation && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
                    <Sparkles className="h-5 w-5 text-purple-600" />
                    <span>LLM Interpretation</span>
                  </h3>
                  <span className="text-xs text-gray-500">{llmInterpretation.method}</span>
                </div>
                
                <div className="prose prose-sm max-w-none">
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 whitespace-pre-wrap">
                    {llmInterpretation.interpretation}
                  </div>
                </div>
                
                {llmInterpretation.tokens_used && (
                  <p className="text-xs text-gray-500 mt-2">
                    Tokens used: {llmInterpretation.tokens_used}
                  </p>
                )}
              </div>
            )}
            
            {/* Rule-Based Interpretation */}
            {ruleInterpretation && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
                    <Zap className="h-5 w-5 text-blue-600" />
                    <span>Rule-Based Interpretation</span>
                  </h3>
                  <span className="text-xs text-gray-500">{ruleInterpretation.method}</span>
                </div>
                
                <div className="prose prose-sm max-w-none">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 whitespace-pre-wrap">
                    {ruleInterpretation.interpretation}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Section 5: Rating */}
        {(llmInterpretation || ruleInterpretation) && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
              <Star className="h-5 w-5 text-yellow-500" />
              <span>4. Rate the Explanation Quality</span>
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Clarity (1-5)
                </label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={clarity || ''}
                  onChange={(e) => setClarity(parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Trustworthiness (1-5)
                </label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={trustworthiness || ''}
                  onChange={(e) => setTrustworthiness(parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fairness (1-5)
                </label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={fairness || ''}
                  onChange={(e) => setFairness(parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
            
            <div className="flex gap-4">
              {llmInterpretation && (
                <button
                  onClick={() => submitFeedback('llm')}
                  className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  Submit LLM Rating
                </button>
              )}
              
              {ruleInterpretation && (
                <button
                  onClick={() => submitFeedback('rule-based')}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Submit Rule-Based Rating
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
