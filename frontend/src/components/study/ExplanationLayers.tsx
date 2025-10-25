/**
 * EXPLANATION LAYER COMPONENTS - UCI German Credit Study
 * 
 * 4 distinct explanation styles for loan approval decisions:
 * - Layer 1: Analytical/Raw SHAP (baseline machine logic)
 * - Layer 2: Plain Text Summary (human-friendly, vague)
 * - Layer 3: Causal Narrative with Counterfactual (cause + what to change)
 * - Layer 4: Hybrid Structured Dashboard (professional, mixed numbers + language)
 */

import React from 'react';
import { TrendingUp, TrendingDown, AlertCircle, Info, CheckCircle, XCircle, Lightbulb } from 'lucide-react';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface ExplanationLayerProps {
  data: {
    layer_id: string;
    decision: {
      label: string;
      score: number;
      risk_level?: string;
    };
    content: any;
    top_features?: any[];
  };
}

// ============================================================================
// LAYER 1: Analytical / Raw SHAP
// ============================================================================
// Baseline machine logic view - just the numbers
// Top 5 features with direction and numeric contribution
// No storytelling, no what-if

export const Layer1Explanation: React.FC<ExplanationLayerProps> = ({ data }) => {
  const { content } = data;
  const drivers = content.drivers || [];

  return (
    <div className="space-y-4">
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
        <h4 className="font-bold text-slate-900 text-lg mb-1">{content.title}</h4>
        <p className="text-sm text-slate-600">
          Analytical view showing feature contributions to the decision.
        </p>
      </div>
      
      <div className="space-y-2">
        {drivers.map((driver: any, idx: number) => (
          <div key={idx} className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-lg">
            {driver.direction === 'increases' ? (
              <TrendingUp className="w-6 h-6 text-red-500 flex-shrink-0" />
            ) : (
              <TrendingDown className="w-6 h-6 text-green-500 flex-shrink-0" />
            )}
            <div className="flex-1">
              <div className="font-semibold text-gray-900">{driver.feature_name}</div>
              <div className="text-sm text-gray-600">
                {driver.direction === 'increases' ? 'Increases' : 'Decreases'} risk
              </div>
            </div>
            <div className="text-right">
              <div className="font-mono font-bold text-gray-900">
                {driver.contribution > 0 ? '+' : ''}{driver.contribution.toFixed(4)}
              </div>
              <div className="text-xs text-gray-500">SHAP value</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// LAYER 2: Conversational Summary (LLM-Generated)
// ============================================================================
// OpenAI GPT-4 generated friendly explanation
// Conversational tone, no jargon, no numbers

export const Layer2Explanation: React.FC<ExplanationLayerProps> = ({ data }) => {
  const { content } = data;

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-bold text-blue-900 text-lg mb-1">{content.title}</h4>
        <p className="text-sm text-blue-700">
          {content.subtitle}
        </p>
      </div>
      
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <p className="text-gray-800 text-lg leading-relaxed">
          {content.text}
        </p>
      </div>
    </div>
  );
};

// ============================================================================
// LAYER 3: Story-Driven Causality (Narrative + Counterfactual)
// ============================================================================
// Causal explanation with actual values + counterfactual "what-if"
// Emulates mental simulation for learning and fairness

export const Layer3Explanation: React.FC<ExplanationLayerProps> = ({ data }) => {
  const { content } = data;

  return (
    <div className="space-y-4">
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <h4 className="font-bold text-purple-900 text-lg mb-1">{content.title}</h4>
        <p className="text-sm text-purple-700">
          {content.subtitle}
        </p>
      </div>
      
      {/* Causal Explanation */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-start gap-3 mb-4">
          <Info className="w-6 h-6 text-purple-600 flex-shrink-0 mt-1" />
          <div>
            <h5 className="font-semibold text-gray-900 mb-2">Why This Decision?</h5>
            <p className="text-gray-800 leading-relaxed">
              {content.causal_explanation}
            </p>
          </div>
        </div>
      </div>

      {/* Counterfactual */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <Lightbulb className="w-6 h-6 text-amber-600 flex-shrink-0 mt-1" />
          <div>
            <h5 className="font-semibold text-gray-900 mb-2">What Could Change This?</h5>
            <p className="text-gray-800 leading-relaxed">
              {content.counterfactual}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// LAYER 4: Visual Dashboard + Metaphor (Cognitive Fusion)
// ============================================================================
// Combines numeric + linguistic + visual + metaphorical cues
// Emoji-enhanced drivers + risk meter + LLM-generated metaphor

export const Layer4Explanation: React.FC<ExplanationLayerProps> = ({ data }) => {
  const { content } = data;
  const { decision_header, top_drivers, metaphor, guidance } = content;

  // Determine colors based on decision
  const isApproved = decision_header.label === 'APPROVED';
  const headerColor = isApproved ? 'bg-green-50 border-green-300' : 'bg-red-50 border-red-300';
  const iconColor = isApproved ? 'text-green-600' : 'text-red-600';
  const Icon = isApproved ? CheckCircle : XCircle;

  return (
    <div className="space-y-4">
      {/* Title */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-4">
        <h4 className="font-bold text-indigo-900 text-lg mb-1">{content.title}</h4>
        <p className="text-sm text-indigo-700">{content.subtitle}</p>
      </div>

      {/* Decision Header with Risk Meter */}
      <div className={`${headerColor} border-2 rounded-lg p-6`}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <Icon className={`w-10 h-10 ${iconColor}`} />
            <div>
              <h4 className="text-2xl font-bold text-gray-900">{decision_header.label}</h4>
              <p className="text-sm text-gray-700">{decision_header.risk_level}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-gray-900">
              {(decision_header.score * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-gray-600">Risk Score</div>
          </div>
        </div>
        {/* Risk Meter */}
        <div className="mt-3 pt-3 border-t border-gray-300">
          <p className="text-base font-semibold text-gray-800">{decision_header.risk_meter}</p>
        </div>
      </div>

      {/* Metaphor Box */}
      {metaphor && (
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-300 rounded-lg p-5">
          <div className="flex items-center gap-3">
            <span className="text-3xl">💭</span>
            <p className="text-gray-800 text-base italic font-medium leading-relaxed">
              "{metaphor}"
            </p>
          </div>
        </div>
      )}

      {/* Top Drivers with Emojis */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h5 className="font-bold text-gray-900 text-lg mb-4">Key Factors</h5>
        <div className="space-y-3">
          {top_drivers.map((driver: any, idx: number) => (
            <div key={idx} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
              <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                <span className="text-sm font-bold text-indigo-600">{idx + 1}</span>
              </div>
              <div className="flex-1">
                <p className="text-gray-800 text-base leading-relaxed">{driver.reason}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Actionable Guidance */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <Lightbulb className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
          <div>
            <h5 className="font-semibold text-gray-900 mb-2">Guidance</h5>
            <p className="text-gray-800 leading-relaxed">{guidance}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// MAIN ROUTER COMPONENT
// ============================================================================
// Routes to the correct layer component based on layer_id

export const ExplanationRouter: React.FC<ExplanationLayerProps> = ({ data }) => {
  const { layer_id } = data;
  
  switch (layer_id) {
    case 'layer_1':
      return <Layer1Explanation data={data} />;
    case 'layer_2':
      return <Layer2Explanation data={data} />;
    case 'layer_3':
      return <Layer3Explanation data={data} />;
    case 'layer_4':
      return <Layer4Explanation data={data} />;
    default:
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-red-800 font-semibold">Unknown layer type: {layer_id}</p>
          </div>
        </div>
      );
  }
};
