'use client';

export const dynamic = 'force-dynamic';

import { useState } from 'react';
import { FileText, Brain, MessageSquare, AlertCircle, CheckCircle2, Info, Sparkles } from 'lucide-react';

export default function InterpretationLayerPage() {
  const [selectedExample, setSelectedExample] = useState<'shap' | 'lime' | null>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center space-x-4 mb-4">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl">
              <MessageSquare className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900">Interpretation Layer</h1>
              <p className="text-lg text-gray-600 mt-2">
                Converting complex AI explanations into human-understandable insights
              </p>
            </div>
          </div>
        </div>

        {/* Info Banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <div className="flex items-start space-x-3">
            <Info className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-900 mb-2">Purpose</h3>
              <p className="text-blue-800 text-sm">
                This layer bridges the gap between technical model explanations (SHAP/LIME) and 
                regulatory interpretation. It translates complex feature importance scores and 
                contribution values into natural language that stakeholders can understand and 
                use for compliance, auditing, and decision-making.
              </p>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* SHAP Interpretation Example */}
          <div 
            className={`bg-white rounded-lg shadow-sm border-2 p-6 cursor-pointer transition-all ${
              selectedExample === 'shap' ? 'border-blue-500 shadow-lg' : 'border-gray-200 hover:border-blue-300'
            }`}
            onClick={() => setSelectedExample('shap')}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Brain className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900">SHAP Translation</h3>
              </div>
              {selectedExample === 'shap' && (
                <CheckCircle2 className="h-6 w-6 text-blue-600" />
              )}
            </div>

            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Technical Output</p>
                <code className="text-sm text-gray-700 block">
                  Feature: "credit_history_length"<br />
                  SHAP Value: -0.23<br />
                  Base Value: 0.15
                </code>
              </div>

              <div className="flex items-center justify-center">
                <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
                <p className="text-xs font-semibold text-blue-700 uppercase mb-2">Human Interpretation</p>
                <p className="text-sm text-gray-800">
                  "The applicant's <strong>short credit history</strong> significantly <strong>decreases</strong> their 
                  likelihood of loan approval by 23 percentage points. This is a <strong>major risk factor</strong> 
                  that requires additional verification or collateral."
                </p>
              </div>
            </div>
          </div>

          {/* LIME Interpretation Example */}
          <div 
            className={`bg-white rounded-lg shadow-sm border-2 p-6 cursor-pointer transition-all ${
              selectedExample === 'lime' ? 'border-orange-500 shadow-lg' : 'border-gray-200 hover:border-orange-300'
            }`}
            onClick={() => setSelectedExample('lime')}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <FileText className="h-6 w-6 text-orange-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900">LIME Translation</h3>
              </div>
              {selectedExample === 'lime' && (
                <CheckCircle2 className="h-6 w-6 text-orange-600" />
              )}
            </div>

            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Technical Output</p>
                <code className="text-sm text-gray-700 block">
                  Feature: "debt_to_income_ratio"<br />
                  Weight: 0.45<br />
                  Value: 0.62 (High)
                </code>
              </div>

              <div className="flex items-center justify-center">
                <div className="p-2 bg-gradient-to-r from-orange-500 to-red-600 rounded-full">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
              </div>

              <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-lg p-4 border border-orange-200">
                <p className="text-xs font-semibold text-orange-700 uppercase mb-2">Human Interpretation</p>
                <p className="text-sm text-gray-800">
                  "The applicant's <strong>high debt-to-income ratio (62%)</strong> is the <strong>strongest indicator</strong> 
                  of potential default risk. This exceeds the recommended threshold of 40% and suggests the applicant 
                  may struggle with additional debt obligations."
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Key Features */}
        <div className="bg-white rounded-lg shadow-sm border p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Interpretation Layer Capabilities</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-start space-x-3">
              <div className="p-2 bg-green-100 rounded-lg flex-shrink-0">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Natural Language Generation</h3>
                <p className="text-sm text-gray-600">
                  Converts numerical feature contributions into clear, contextual explanations
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="p-2 bg-green-100 rounded-lg flex-shrink-0">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Regulatory Compliance</h3>
                <p className="text-sm text-gray-600">
                  Formats explanations to meet GDPR, FCRA, and other regulatory requirements
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="p-2 bg-green-100 rounded-lg flex-shrink-0">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Risk Assessment</h3>
                <p className="text-sm text-gray-600">
                  Categorizes factors as major, moderate, or minor risk indicators
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="p-2 bg-green-100 rounded-lg flex-shrink-0">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Actionable Insights</h3>
                <p className="text-sm text-gray-600">
                  Provides recommendations for risk mitigation or approval conditions
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Use Cases */}
        <div className="bg-white rounded-lg shadow-sm border p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Regulatory Use Cases</h2>
          
          <div className="space-y-4">
            <div className="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg">
              <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-900 mb-1">Adverse Action Notices (FCRA)</h3>
                <p className="text-sm text-blue-800">
                  Automatically generate legally compliant explanations for loan denials or unfavorable terms
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3 p-4 bg-purple-50 rounded-lg">
              <AlertCircle className="h-5 w-5 text-purple-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-purple-900 mb-1">Right to Explanation (GDPR)</h3>
                <p className="text-sm text-purple-800">
                  Provide data subjects with meaningful information about automated decision-making
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3 p-4 bg-green-50 rounded-lg">
              <AlertCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-green-900 mb-1">Model Auditing & Documentation</h3>
                <p className="text-sm text-green-800">
                  Create audit trails with human-readable explanations for regulatory review
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3 p-4 bg-orange-50 rounded-lg">
              <AlertCircle className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-orange-900 mb-1">Stakeholder Communication</h3>
                <p className="text-sm text-orange-800">
                  Enable non-technical stakeholders to understand and trust AI-driven decisions
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Coming Soon Badge */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-3 rounded-full">
            <Sparkles className="h-5 w-5" />
            <span className="font-semibold">Full Implementation Coming Soon</span>
          </div>
          <p className="text-gray-600 mt-4 text-sm">
            This page demonstrates the concept. Integration with live SHAP/LIME outputs is under development.
          </p>
        </div>
      </div>
    </div>
  );
}
