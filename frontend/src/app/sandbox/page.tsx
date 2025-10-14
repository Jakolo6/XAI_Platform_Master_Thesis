/**
 * EXPLAINABLE AI SANDBOX - REVISED LAYOUT
 * Route: /sandbox
 * 
 * Improved UX with clear sections:
 * 1. Customer Snapshot - Human-readable context
 * 2. Feature Attribution - SHAP vs LIME side-by-side
 * 3. Comparison View - Agreement/disagreement analysis
 * 4. Human-Readable Summary - Natural language explanation
 */

'use client';

export const dynamic = 'force-dynamic';

import { useEffect, useState } from 'react';
import { 
  Brain, 
  User,
  DollarSign,
  Home,
  Briefcase,
  Baby,
  Car,
  TrendingUp, 
  TrendingDown, 
  AlertCircle,
  RefreshCw,
  CheckCircle,
  XCircle,
  Info,
  BarChart3,
  GitCompare,
  Globe,
  Target
} from 'lucide-react';
import { explanationsAPI, modelsAPI } from '@/lib/api';
import GlobalExplanationView from './global-view';

// Types
interface PredictionInstance {
  instance_id: string;
  features: Record<string, any>;
  prediction: number;
  true_label?: string;
  model_output: string;
  note?: string;
}

interface FeatureContribution {
  feature: string;
  value: any;
  contribution: number;
  importance: number;
}

interface ExplanationData {
  method: 'shap' | 'lime';
  features: FeatureContribution[];
  prediction_proba: number;
  base_value?: number;
}

interface FeatureComparison {
  feature: string;
  shapEffect: number;
  limeEffect: number;
  agreement: boolean;
}

export default function SandboxPage() {
  // State
  const [viewMode, setViewMode] = useState<'local' | 'global'>('local');
  const [selectedModel, setSelectedModel] = useState<any>(null);
  const [models, setModels] = useState<any[]>([]);
  const [selectedInstance, setSelectedInstance] = useState<PredictionInstance | null>(null);
  const [shapExplanation, setShapExplanation] = useState<ExplanationData | null>(null);
  const [limeExplanation, setLimeExplanation] = useState<ExplanationData | null>(null);
  const [shapGlobal, setShapGlobal] = useState<any>(null);
  const [limeGlobal, setLimeGlobal] = useState<any>(null);
  const [interpretation, setInterpretation] = useState<string>('');
  const [ruleBasedInterpretation, setRuleBasedInterpretation] = useState<any>(null);
  const [llmInterpretation, setLlmInterpretation] = useState<any>(null);
  const [interpretationMode, setInterpretationMode] = useState<'rule-based' | 'llm' | 'both'>('both');
  const [isLoadingInterpretation, setIsLoadingInterpretation] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'shap' | 'lime' | 'comparison'>('shap');
  
  // Rating state
  const [ruleBasedRating, setRuleBasedRating] = useState({ clarity: 0, trust: 0, fairness: 0 });
  const [llmRating, setLlmRating] = useState({ clarity: 0, trust: 0, fairness: 0 });

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
      setError('Failed to load models');
    }
  };

  const loadGlobalExplanations = async () => {
    if (!selectedModel) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const modelId = selectedModel.id || selectedModel.model_id;
      
      // Load global SHAP
      const shapResponse = await explanationsAPI.getGlobalExplanations(modelId);
      setShapGlobal(shapResponse.data.shap);
      
      // Load global LIME  
      setLimeGlobal(shapResponse.data.lime);
      
    } catch (error: any) {
      console.error('Failed to load global explanations:', error);
      setError(error.response?.data?.detail || 'Failed to load global explanations. Please ensure they have been generated.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadSamplePrediction = async () => {
    if (!selectedModel) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const modelId = selectedModel.id || selectedModel.model_id;
      
      // Load sample instance
      const sampleResponse = await explanationsAPI.getSampleInstance(modelId);
      setSelectedInstance(sampleResponse.data);
      
      // Load SHAP explanation
      const shapResponse = await explanationsAPI.getLocalExplanation(
        modelId,
        sampleResponse.data.instance_id,
        'shap'
      );
      setShapExplanation(shapResponse.data);
      
      // Load LIME explanation
      const limeResponse = await explanationsAPI.getLocalExplanation(
        modelId,
        sampleResponse.data.instance_id,
        'lime'
      );
      setLimeExplanation(limeResponse.data);
      
      // Generate interpretation
      generateInterpretation(shapResponse.data, limeResponse.data, sampleResponse.data);
      
    } catch (error: any) {
      console.error('Failed to load prediction:', error);
      setError(error.response?.data?.detail || 'Failed to load prediction');
    } finally {
      setIsLoading(false);
    }
  };

  const generateInterpretation = (shap: ExplanationData, lime: ExplanationData, instance: PredictionInstance) => {
    const predictionClass = instance.prediction > 0.5 ? 1 : 0;
    const confidence = predictionClass === 1 ? instance.prediction * 100 : (1 - instance.prediction) * 100;
    
    const topShapFeatures = shap.features.slice(0, 3);
    const outcome = predictionClass === 1 ? 'default on the loan' : 'repay the loan';
    
    let text = `The model predicts the customer will likely **${outcome}** with ${confidence.toFixed(1)}% confidence.\n\n`;
    text += `**Key Factors (SHAP):**\n`;
    
    topShapFeatures.forEach(f => {
      const direction = f.contribution > 0 ? 'increases' : 'decreases';
      const risk = predictionClass === 1 ? 'default risk' : 'repayment likelihood';
      text += `- **${f.feature}**: ${direction} ${risk} by ${Math.abs(f.contribution).toFixed(3)}\n`;
    });
    
    setInterpretation(text);
  };

  const loadDualInterpretations = async () => {
    if (!selectedModel || !selectedInstance || !shapExplanation) return;
    
    setIsLoadingInterpretation(true);
    
    try {
      const modelId = selectedModel.id || selectedModel.model_id;
      
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      
      const response = await fetch(`${apiBaseUrl}/interpretation/local`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model_id: modelId,
          instance_id: selectedInstance.instance_id,
          shap_data: shapExplanation,
          mode: interpretationMode
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate interpretations');
      }
      
      const data = await response.json();
      
      if (interpretationMode === 'both') {
        setRuleBasedInterpretation(data.rule_based);
        setLlmInterpretation(data.llm_based);
      } else if (interpretationMode === 'rule-based') {
        setRuleBasedInterpretation(data.rule_based);
        setLlmInterpretation(null);
      } else {
        setLlmInterpretation(data.llm_based);
        setRuleBasedInterpretation(null);
      }
      
    } catch (error: any) {
      console.error('Failed to load interpretations:', error);
      setError('Failed to generate human-readable interpretations');
    } finally {
      setIsLoadingInterpretation(false);
    }
  };

  const getFeatureComparison = (): FeatureComparison[] => {
    if (!shapExplanation || !limeExplanation) return [];
    
    const shapMap = new Map(shapExplanation.features.map(f => [f.feature, f.contribution]));
    const limeMap = new Map(limeExplanation.features.map(f => [f.feature, f.contribution]));
    
    const allFeatures = new Set([...shapMap.keys(), ...limeMap.keys()]);
    
    return Array.from(allFeatures)
      .map(feature => {
        const shapEffect = shapMap.get(feature) || 0;
        const limeEffect = limeMap.get(feature) || 0;
        const agreement = (shapEffect * limeEffect) >= 0; // Same sign
        
        return { feature, shapEffect, limeEffect, agreement };
      })
      .sort((a, b) => Math.abs(b.shapEffect) - Math.abs(a.shapEffect))
      .slice(0, 10);
  };

  const getAgreementRate = (): number => {
    const comparison = getFeatureComparison();
    if (comparison.length === 0) return 0;
    
    const agreements = comparison.filter(c => c.agreement).length;
    return (agreements / comparison.length) * 100;
  };

  // Helper function to format feature names
  const formatFeatureName = (name: string): string => {
    return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // Helper function to get icon for feature
  const getFeatureIcon = (name: string) => {
    const lowerName = name.toLowerCase();
    if (lowerName.includes('age') || lowerName.includes('birth')) return <User className="w-4 h-4" />;
    if (lowerName.includes('income') || lowerName.includes('amt')) return <DollarSign className="w-4 h-4" />;
    if (lowerName.includes('credit') || lowerName.includes('loan')) return <Home className="w-4 h-4" />;
    if (lowerName.includes('employ') || lowerName.includes('work')) return <Briefcase className="w-4 h-4" />;
    if (lowerName.includes('child')) return <Baby className="w-4 h-4" />;
    if (lowerName.includes('car')) return <Car className="w-4 h-4" />;
    return <Info className="w-4 h-4" />;
  };

  // Get top interpretable features for snapshot
  const getSnapshotFeatures = () => {
    if (!shapExplanation || !selectedInstance) return [];
    
    const topFeatures = shapExplanation.features
      .slice(0, 6)
      .map(f => ({
        name: f.feature,
        value: f.value,
        displayValue: typeof f.value === 'number' ? f.value.toFixed(2) : f.value,
        icon: getFeatureIcon(f.feature)
      }));
    
    return topFeatures;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Brain className="w-8 h-8 text-indigo-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Explainability Sandbox</h1>
                <p className="text-sm text-gray-600">
                  {viewMode === 'local' ? 'Interactive local explanation explorer' : 'Model-level feature importance'}
                </p>
              </div>
            </div>
            
            {/* View Mode Toggle */}
            <div className="flex gap-2 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('local')}
                className={`px-4 py-2 rounded-md font-medium transition-colors flex items-center gap-2 ${
                  viewMode === 'local'
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Target className="w-4 h-4" />
                Local View
              </button>
              <button
                onClick={() => setViewMode('global')}
                className={`px-4 py-2 rounded-md font-medium transition-colors flex items-center gap-2 ${
                  viewMode === 'global'
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Globe className="w-4 h-4" />
                Global View
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Model Selection */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Model</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Model</label>
              <select
                value={selectedModel?.id || selectedModel?.model_id || ''}
                onChange={(e) => {
                  const model = models.find(m => (m.id || m.model_id) === e.target.value);
                  setSelectedModel(model);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Choose a model...</option>
                {models.map((model) => (
                  <option key={model.id || model.model_id} value={model.id || model.model_id}>
                    {model.name || model.model_id} - {model.model_type}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Dataset</label>
              <input
                type="text"
                value={selectedModel?.dataset_id || 'N/A'}
                disabled
                className="w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg text-gray-600"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Model Type</label>
              <input
                type="text"
                value={selectedModel?.model_type || 'N/A'}
                disabled
                className="w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg text-gray-600"
              />
            </div>
          </div>
          
          <button
            onClick={viewMode === 'local' ? loadSamplePrediction : loadGlobalExplanations}
            disabled={!selectedModel || isLoading}
            className="mt-4 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Loading...
              </>
            ) : viewMode === 'local' ? (
              <>
                <RefreshCw className="w-5 h-5" />
                Load Sample Prediction
              </>
            ) : (
              <>
                <RefreshCw className="w-5 h-5" />
                Load Global Explanations
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* CONDITIONAL RENDERING: LOCAL vs GLOBAL VIEW */}
        {viewMode === 'global' && shapGlobal && limeGlobal ? (
          <GlobalExplanationView
            modelId={selectedModel?.id || selectedModel?.model_id}
            modelData={selectedModel}
            shapGlobal={shapGlobal}
            limeGlobal={limeGlobal}
          />
        ) : viewMode === 'local' && selectedInstance && shapExplanation ? (
          <>
            {/* 1️⃣ CUSTOMER SNAPSHOT */}
            {selectedInstance && shapExplanation && (
          <div className="bg-gradient-to-br from-white to-indigo-50 rounded-xl shadow-lg border border-indigo-200 p-8 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <User className="w-6 h-6 text-indigo-600" />
              Customer Snapshot
            </h2>
            
            {/* Feature Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
              {getSnapshotFeatures().map((feature, idx) => (
                <div key={idx} className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
                  <div className="flex items-center gap-2 mb-2 text-gray-600">
                    {feature.icon}
                    <span className="text-xs font-medium">{formatFeatureName(feature.name)}</span>
                  </div>
                  <p className="text-lg font-bold text-gray-900">{feature.displayValue}</p>
                  <p className="text-xs text-gray-500 mt-1">Normalized value</p>
                </div>
              ))}
            </div>

            {/* Prediction Outcome */}
            <div className="bg-white rounded-xl p-6 border-2 border-indigo-300">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  {selectedInstance.prediction < 0.5 ? (
                    <>
                      <CheckCircle className="w-8 h-8 text-green-600" />
                      <div>
                        <h3 className="text-xl font-bold text-green-900">Loan Approved</h3>
                        <p className="text-sm text-green-700">Customer will likely repay</p>
                      </div>
                    </>
                  ) : (
                    <>
                      <XCircle className="w-8 h-8 text-red-600" />
                      <div>
                        <h3 className="text-xl font-bold text-red-900">Loan Denied</h3>
                        <p className="text-sm text-red-700">High default risk</p>
                      </div>
                    </>
                  )}
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-gray-900">
                    {((1 - selectedInstance.prediction) * 100).toFixed(1)}%
                  </p>
                  <p className="text-sm text-gray-600">Confidence</p>
                </div>
              </div>

              {/* Probability Bar */}
              <div className="relative h-4 bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 rounded-full overflow-hidden">
                <div
                  className="absolute top-0 h-full bg-white border-2 border-gray-900"
                  style={{
                    left: `${(1 - selectedInstance.prediction) * 100}%`,
                    width: '4px',
                    transform: 'translateX(-50%)'
                  }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-600 mt-1">
                <span>0% (Will Default)</span>
                <span>100% (Will Repay)</span>
              </div>
            </div>

            {selectedInstance.note && (
              <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start gap-2">
                <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-blue-800">{selectedInstance.note}</p>
              </div>
            )}
          </div>
        )}

        {/* 2️⃣ FEATURE ATTRIBUTION PANELS */}
        {shapExplanation && limeExplanation && (
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-indigo-600" />
              Feature Attribution
            </h2>

            {/* Tabs */}
            <div className="flex gap-2 mb-6 border-b border-gray-200">
              <button
                onClick={() => setActiveTab('shap')}
                className={`px-6 py-3 font-medium transition-colors ${
                  activeTab === 'shap'
                    ? 'text-indigo-600 border-b-2 border-indigo-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                SHAP
              </button>
              <button
                onClick={() => setActiveTab('lime')}
                className={`px-6 py-3 font-medium transition-colors ${
                  activeTab === 'lime'
                    ? 'text-indigo-600 border-b-2 border-indigo-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                LIME
              </button>
              <button
                onClick={() => setActiveTab('comparison')}
                className={`px-6 py-3 font-medium transition-colors ${
                  activeTab === 'comparison'
                    ? 'text-indigo-600 border-b-2 border-indigo-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Comparison
              </button>
            </div>

            {/* SHAP Tab */}
            {activeTab === 'shap' && (
              <div>
                <div className="mb-4 flex items-center justify-between">
                  <p className="text-sm text-gray-600">
                    Prediction Probability: <span className="font-bold text-gray-900">{(shapExplanation.prediction_proba * 100).toFixed(1)}%</span>
                  </p>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 bg-red-500 rounded"></div>
                      <span>Increases risk</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 bg-blue-500 rounded"></div>
                      <span>Decreases risk</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  {shapExplanation.features.slice(0, 15).map((feature, idx) => {
                    const isPositive = feature.contribution > 0;
                    const maxContribution = Math.max(...shapExplanation.features.map(f => Math.abs(f.contribution)));
                    const width = (Math.abs(feature.contribution) / maxContribution) * 100;

                    return (
                      <div key={idx} className="group">
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span className="font-medium text-gray-700">{formatFeatureName(feature.feature)}</span>
                          <span className={`font-bold ${isPositive ? 'text-red-600' : 'text-blue-600'}`}>
                            {isPositive ? '+' : ''}{feature.contribution.toFixed(3)}
                          </span>
                        </div>
                        <div className="relative h-6 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className={`absolute top-0 h-full ${isPositive ? 'bg-red-500' : 'bg-blue-500'} transition-all duration-300 group-hover:opacity-80`}
                            style={{ width: `${width}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* LIME Tab */}
            {activeTab === 'lime' && (
              <div>
                <div className="mb-4 flex items-center justify-between">
                  <p className="text-sm text-gray-600">
                    Prediction Probability: <span className="font-bold text-gray-900">{(limeExplanation.prediction_proba * 100).toFixed(1)}%</span>
                  </p>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 bg-red-500 rounded"></div>
                      <span>Increases risk</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 bg-blue-500 rounded"></div>
                      <span>Decreases risk</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  {limeExplanation.features.slice(0, 15).map((feature, idx) => {
                    const isPositive = feature.contribution > 0;
                    const maxContribution = Math.max(...limeExplanation.features.map(f => Math.abs(f.contribution)));
                    const width = (Math.abs(feature.contribution) / maxContribution) * 100;

                    return (
                      <div key={idx} className="group">
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span className="font-medium text-gray-700">{formatFeatureName(feature.feature)}</span>
                          <span className={`font-bold ${isPositive ? 'text-red-600' : 'text-blue-600'}`}>
                            {isPositive ? '+' : ''}{feature.contribution.toFixed(3)}
                          </span>
                        </div>
                        <div className="relative h-6 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className={`absolute top-0 h-full ${isPositive ? 'bg-red-500' : 'bg-blue-500'} transition-all duration-300 group-hover:opacity-80`}
                            style={{ width: `${width}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Comparison Tab */}
            {activeTab === 'comparison' && (
              <div>
                <div className="mb-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 border border-indigo-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <GitCompare className="w-6 h-6 text-indigo-600" />
                      <div>
                        <p className="font-semibold text-gray-900">Agreement Rate</p>
                        <p className="text-sm text-gray-600">SHAP vs LIME consistency</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-3xl font-bold text-indigo-600">{getAgreementRate().toFixed(0)}%</p>
                      <p className="text-sm text-gray-600">
                        {getAgreementRate() >= 80 ? 'High consistency' : getAgreementRate() >= 60 ? 'Moderate consistency' : 'Low consistency'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-semibold text-gray-700">Feature</th>
                        <th className="text-right py-3 px-4 font-semibold text-gray-700">SHAP Effect</th>
                        <th className="text-right py-3 px-4 font-semibold text-gray-700">LIME Effect</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-700">Agreement</th>
                      </tr>
                    </thead>
                    <tbody>
                      {getFeatureComparison().map((comp, idx) => (
                        <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-3 px-4 font-medium text-gray-900">{formatFeatureName(comp.feature)}</td>
                          <td className={`py-3 px-4 text-right font-mono ${comp.shapEffect > 0 ? 'text-red-600' : 'text-blue-600'}`}>
                            {comp.shapEffect > 0 ? '+' : ''}{comp.shapEffect.toFixed(3)}
                          </td>
                          <td className={`py-3 px-4 text-right font-mono ${comp.limeEffect > 0 ? 'text-red-600' : 'text-blue-600'}`}>
                            {comp.limeEffect > 0 ? '+' : ''}{comp.limeEffect.toFixed(3)}
                          </td>
                          <td className="py-3 px-4 text-center">
                            {comp.agreement ? (
                              <CheckCircle className="w-5 h-5 text-green-600 mx-auto" />
                            ) : (
                              <XCircle className="w-5 h-5 text-red-600 mx-auto" />
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 4️⃣ DUAL INTERPRETATION - RULE-BASED vs LLM-BASED */}
        {shapExplanation && selectedInstance && (
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl shadow-lg border border-purple-200 p-8">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Brain className="w-6 h-6 text-purple-600" />
                <h2 className="text-2xl font-bold text-gray-900">Human-Readable Explanations</h2>
              </div>
              
              {/* Mode Toggle */}
              <div className="flex gap-2 bg-white rounded-lg p-1 border border-purple-200">
                <button
                  onClick={() => setInterpretationMode('rule-based')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    interpretationMode === 'rule-based'
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Rule-Based
                </button>
                <button
                  onClick={() => setInterpretationMode('llm')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    interpretationMode === 'llm'
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  LLM-Based
                </button>
                <button
                  onClick={() => setInterpretationMode('both')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    interpretationMode === 'both'
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Compare Both
                </button>
              </div>
            </div>

            <button
              onClick={loadDualInterpretations}
              disabled={isLoadingInterpretation}
              className="mb-6 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
            >
              {isLoadingInterpretation ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Brain className="w-5 h-5" />
                  Generate Explanation{interpretationMode === 'both' ? 's' : ''}
                </>
              )}
            </button>

            {/* Explanations Display */}
            {(ruleBasedInterpretation || llmInterpretation) && (
              <div className={`grid ${interpretationMode === 'both' ? 'grid-cols-1 lg:grid-cols-2' : 'grid-cols-1'} gap-6`}>
                {/* Rule-Based Explanation */}
                {ruleBasedInterpretation && (
                  <div className="bg-gray-50 rounded-xl p-6 border-2 border-gray-300">
                    <div className="flex items-center gap-2 mb-4">
                      <Target className="w-5 h-5 text-gray-700" />
                      <h3 className="text-lg font-bold text-gray-900">Rule-Based Interpretation</h3>
                    </div>
                    <p className="text-xs text-gray-600 mb-4 italic">Deterministic SHAP reasoning</p>
                    
                    <div className="prose prose-sm max-w-none text-gray-800">
                      <div dangerouslySetInnerHTML={{ 
                        __html: ruleBasedInterpretation.interpretation
                          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                          .replace(/\n/g, '<br/>') 
                      }} />
                    </div>

                    {/* Rating for Rule-Based */}
                    <div className="mt-6 pt-6 border-t border-gray-300">
                      <h4 className="text-sm font-semibold text-gray-900 mb-3">Rate this explanation</h4>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Clarity</label>
                          <div className="flex gap-1">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <button
                                key={star}
                                onClick={() => setRuleBasedRating({ ...ruleBasedRating, clarity: star })}
                                className={`text-xl transition-colors ${
                                  star <= ruleBasedRating.clarity ? 'text-yellow-400' : 'text-gray-300'
                                } hover:text-yellow-500`}
                              >
                                ★
                              </button>
                            ))}
                          </div>
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Trust</label>
                          <div className="flex gap-1">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <button
                                key={star}
                                onClick={() => setRuleBasedRating({ ...ruleBasedRating, trust: star })}
                                className={`text-xl transition-colors ${
                                  star <= ruleBasedRating.trust ? 'text-yellow-400' : 'text-gray-300'
                                } hover:text-yellow-500`}
                              >
                                ★
                              </button>
                            ))}
                          </div>
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Fairness</label>
                          <div className="flex gap-1">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <button
                                key={star}
                                onClick={() => setRuleBasedRating({ ...ruleBasedRating, fairness: star })}
                                className={`text-xl transition-colors ${
                                  star <= ruleBasedRating.fairness ? 'text-yellow-400' : 'text-gray-300'
                                } hover:text-yellow-500`}
                              >
                                ★
                              </button>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* LLM-Based Explanation */}
                {llmInterpretation && (
                  <div className="bg-white rounded-xl p-6 border-2 border-purple-300">
                    <div className="flex items-center gap-2 mb-4">
                      <Brain className="w-5 h-5 text-purple-700" />
                      <h3 className="text-lg font-bold text-gray-900">LLM-Based Interpretation</h3>
                    </div>
                    <p className="text-xs text-gray-600 mb-4 italic">Natural language via GPT-4</p>
                    
                    <div className="prose prose-sm max-w-none text-gray-800">
                      <div dangerouslySetInnerHTML={{ 
                        __html: llmInterpretation.interpretation
                          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                          .replace(/\n/g, '<br/>') 
                      }} />
                    </div>

                    {/* Rating for LLM */}
                    <div className="mt-6 pt-6 border-t border-purple-200">
                      <h4 className="text-sm font-semibold text-gray-900 mb-3">Rate this explanation</h4>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Clarity</label>
                          <div className="flex gap-1">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <button
                                key={star}
                                onClick={() => setLlmRating({ ...llmRating, clarity: star })}
                                className={`text-xl transition-colors ${
                                  star <= llmRating.clarity ? 'text-yellow-400' : 'text-gray-300'
                                } hover:text-yellow-500`}
                              >
                                ★
                              </button>
                            ))}
                          </div>
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Trust</label>
                          <div className="flex gap-1">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <button
                                key={star}
                                onClick={() => setLlmRating({ ...llmRating, trust: star })}
                                className={`text-xl transition-colors ${
                                  star <= llmRating.trust ? 'text-yellow-400' : 'text-gray-300'
                                } hover:text-yellow-500`}
                              >
                                ★
                              </button>
                            ))}
                          </div>
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Fairness</label>
                          <div className="flex gap-1">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <button
                                key={star}
                                onClick={() => setLlmRating({ ...llmRating, fairness: star })}
                                className={`text-xl transition-colors ${
                                  star <= llmRating.fairness ? 'text-yellow-400' : 'text-gray-300'
                                } hover:text-yellow-500`}
                              >
                                ★
                              </button>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
          </>
        ) : null}
      </div>
    </div>
  );
}
