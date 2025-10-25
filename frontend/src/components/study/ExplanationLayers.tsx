/**
 * EXPLANATION LAYER COMPONENTS
 * 
 * Reusable components for rendering the 4 different explanation styles.
 * Import these into the study session page and use based on layer_type.
 * 
 * TODO: Implement each layer according to your research design
 */

import React from 'react';
import { TrendingUp, TrendingDown, AlertCircle, Info } from 'lucide-react';

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface FeatureContribution {
  feature: string;
  value: any;
  contribution: number;
  importance: number;
}

interface ExplanationLayerProps {
  features: FeatureContribution[];
  prediction_proba: number;
  base_value: number;
  rendered_content: any;
}

// ============================================================================
// LAYER 1: [DEFINE YOUR FIRST INTERPRETATION STYLE]
// ============================================================================
// Example: Simple feature list with directional indicators
// Format: "Feature X increases/decreases risk by Y"
// ============================================================================

export const Layer1Explanation: React.FC<ExplanationLayerProps> = ({
  features,
  prediction_proba,
  rendered_content
}) => {
  return (
    <div className="space-y-4">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
          <Info className="w-5 h-5" />
          Layer 1: Simple Feature List (Placeholder)
        </h4>
        <p className="text-sm text-blue-800">
          This layer shows a straightforward list of features and their impact.
        </p>
      </div>
      
      {/* TODO: Implement your Layer 1 visualization */}
      <div className="space-y-2">
        {features.map((feature, idx) => (
          <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            {feature.contribution > 0 ? (
              <TrendingUp className="w-5 h-5 text-red-500 flex-shrink-0" />
            ) : (
              <TrendingDown className="w-5 h-5 text-green-500 flex-shrink-0" />
            )}
            <div className="flex-1">
              <div className="font-medium text-gray-900">{feature.feature}</div>
              <div className="text-sm text-gray-600">
                {feature.contribution > 0 ? 'Increases' : 'Decreases'} risk by{' '}
                {Math.abs(feature.contribution).toFixed(3)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// LAYER 2: [DEFINE YOUR SECOND INTERPRETATION STYLE]
// ============================================================================
// Example: Natural language narrative
// Format: Paragraph explaining the decision in plain English
// ============================================================================

export const Layer2Explanation: React.FC<ExplanationLayerProps> = ({
  features,
  prediction_proba,
  rendered_content
}) => {
  return (
    <div className="space-y-4">
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <h4 className="font-semibold text-purple-900 mb-2 flex items-center gap-2">
          <Info className="w-5 h-5" />
          Layer 2: Natural Language Narrative (Placeholder)
        </h4>
        <p className="text-sm text-purple-800">
          This layer provides a human-readable explanation in narrative form.
        </p>
      </div>
      
      {/* TODO: Implement your Layer 2 visualization */}
      <div className="prose prose-sm max-w-none">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <p className="text-gray-800 leading-relaxed">
            The model predicts a risk score of <strong>{(prediction_proba * 100).toFixed(1)}%</strong>.
            This decision is primarily influenced by the following factors:
          </p>
          <ul className="mt-4 space-y-2">
            {features.slice(0, 3).map((feature, idx) => (
              <li key={idx} className="text-gray-700">
                <strong>{feature.feature}</strong>: This factor{' '}
                {feature.contribution > 0 ? 'increases' : 'decreases'} the risk
                significantly.
              </li>
            ))}
          </ul>
          <p className="mt-4 text-gray-600 text-sm italic">
            [TODO: Replace with actual natural language generation or LLM-based explanation]
          </p>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// LAYER 3: [DEFINE YOUR THIRD INTERPRETATION STYLE]
// ============================================================================
// Example: Visual bar chart with color coding
// Format: Horizontal bars showing positive/negative contributions
// ============================================================================

export const Layer3Explanation: React.FC<ExplanationLayerProps> = ({
  features,
  prediction_proba,
  rendered_content
}) => {
  const maxContribution = Math.max(...features.map(f => Math.abs(f.contribution)));
  
  return (
    <div className="space-y-4">
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <h4 className="font-semibold text-green-900 mb-2 flex items-center gap-2">
          <Info className="w-5 h-5" />
          Layer 3: Visual Bar Chart (Placeholder)
        </h4>
        <p className="text-sm text-green-800">
          This layer uses visual bars to show feature contributions.
        </p>
      </div>
      
      {/* TODO: Implement your Layer 3 visualization */}
      <div className="space-y-3">
        {features.map((feature, idx) => {
          const percentage = (Math.abs(feature.contribution) / maxContribution) * 100;
          const isPositive = feature.contribution > 0;
          
          return (
            <div key={idx} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-gray-900">{feature.feature}</span>
                <span className={`font-mono ${isPositive ? 'text-red-600' : 'text-green-600'}`}>
                  {isPositive ? '+' : ''}{feature.contribution.toFixed(3)}
                </span>
              </div>
              <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden">
                <div
                  className={`h-full ${isPositive ? 'bg-red-500' : 'bg-green-500'} transition-all duration-500`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ============================================================================
// LAYER 4: [DEFINE YOUR FOURTH INTERPRETATION STYLE]
// ============================================================================
// Example: Counterfactual "what-if" scenarios
// Format: "If feature X was Y, the decision would change to Z"
// ============================================================================

export const Layer4Explanation: React.FC<ExplanationLayerProps> = ({
  features,
  prediction_proba,
  rendered_content
}) => {
  return (
    <div className="space-y-4">
      <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
        <h4 className="font-semibold text-orange-900 mb-2 flex items-center gap-2">
          <Info className="w-5 h-5" />
          Layer 4: Counterfactual Scenarios (Placeholder)
        </h4>
        <p className="text-sm text-orange-800">
          This layer shows "what-if" scenarios to explain the decision.
        </p>
      </div>
      
      {/* TODO: Implement your Layer 4 visualization */}
      <div className="space-y-3">
        {features.slice(0, 3).map((feature, idx) => (
          <div key={idx} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-sm font-bold text-blue-600">{idx + 1}</span>
              </div>
              <div className="flex-1">
                <div className="font-medium text-gray-900 mb-1">
                  What if {feature.feature} was different?
                </div>
                <div className="text-sm text-gray-600">
                  Current value: <strong>{feature.value}</strong>
                </div>
                <div className="text-sm text-gray-600 mt-2">
                  <em>[TODO: Generate counterfactual scenario - e.g., "If this was X, the decision would likely change to Y"]</em>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// MAIN ROUTER COMPONENT
// ============================================================================
// Use this in your study session page to render the correct layer

interface ExplanationRouterProps {
  layer_type: string;
  features: FeatureContribution[];
  prediction_proba: number;
  base_value: number;
  rendered_content: any;
}

export const ExplanationRouter: React.FC<ExplanationRouterProps> = ({
  layer_type,
  features,
  prediction_proba,
  base_value,
  rendered_content
}) => {
  const props = { features, prediction_proba, base_value, rendered_content };
  
  switch (layer_type) {
    case 'layer_1':
      return <Layer1Explanation {...props} />;
    case 'layer_2':
      return <Layer2Explanation {...props} />;
    case 'layer_3':
      return <Layer3Explanation {...props} />;
    case 'layer_4':
      return <Layer4Explanation {...props} />;
    default:
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <AlertCircle className="w-5 h-5 text-red-600 mb-2" />
          <p className="text-red-800">Unknown layer type: {layer_type}</p>
        </div>
      );
  }
};
