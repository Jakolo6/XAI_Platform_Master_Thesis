/**
 * HOME PAGE - Landing Page
 * Route: /
 * 
 * The main landing page of the XAI Platform.
 * Redirects authenticated users to dashboard.
 * Shows welcome message and login button for guests.
 */

'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { ArrowRight, BarChart3, Brain, Shield, Zap } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold">XAI Finance</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/login"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Login
              </Link>
              <Link
                href="/dashboard"
                className="bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium inline-flex items-center"
              >
                Dashboard
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Explainable AI in
            <span className="text-blue-600"> Financial Services</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            A comprehensive research platform for benchmarking explainable AI (XAI) methods
            in financial fraud detection. Compare models, generate explanations, and conduct
            human studies.
          </p>
          <div className="flex justify-center space-x-4">
            <Link
              href="/dashboard"
              className="bg-blue-600 text-white hover:bg-blue-700 px-8 py-3 rounded-lg text-lg font-medium inline-flex items-center"
            >
              View Dashboard
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
            <Link
              href="/models"
              className="bg-white text-blue-600 hover:bg-gray-50 border-2 border-blue-600 px-8 py-3 rounded-lg text-lg font-medium"
            >
              Explore Models
            </Link>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="text-3xl font-bold text-blue-600 mb-2">6</div>
            <div className="text-gray-600">ML Models Trained</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="text-3xl font-bold text-green-600 mb-2">94.3%</div>
            <div className="text-gray-600">Best AUC-ROC Score</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="text-3xl font-bold text-purple-600 mb-2">270k</div>
            <div className="text-gray-600">Training Samples</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="text-3xl font-bold text-orange-600 mb-2">452</div>
            <div className="text-gray-600">Engineered Features</div>
          </div>
        </div>

        {/* Features */}
        <div className="mt-20">
          <h2 className="text-3xl font-bold text-center mb-12">Platform Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <BarChart3 className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Model Benchmarking</h3>
              <p className="text-gray-600">
                Compare 6 different ML algorithms with comprehensive metrics and visualizations.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Brain className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">XAI Explanations</h3>
              <p className="text-gray-600">
                Generate SHAP and LIME explanations to understand model predictions.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="bg-purple-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Fraud Detection</h3>
              <p className="text-gray-600">
                Real-world IEEE-CIS dataset with 590k fraud transactions.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="bg-orange-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-orange-600" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Fast Training</h3>
              <p className="text-gray-600">
                XGBoost trains in 8 seconds with 94.1% AUC-ROC performance.
              </p>
            </div>
          </div>
        </div>

        {/* Models Overview */}
        <div className="mt-20">
          <h2 className="text-3xl font-bold text-center mb-12">Trained Models</h2>
          <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Model
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    AUC-ROC
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    F1 Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Training Time
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">🥇</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">CatBoost</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">0.943</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">0.717</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">231.8s</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">🥈</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">XGBoost</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">0.941</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">0.697</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">8.1s ⚡</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">🥉</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">Random Forest</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">0.932</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">0.659</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">32.5s</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">#4</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">LightGBM</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">0.930</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">0.643</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">47.7s</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-20 bg-blue-600 rounded-2xl p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">Ready to Explore?</h2>
          <p className="text-xl mb-8 opacity-90">
            Access the full platform to view detailed metrics, compare models, and generate explanations.
          </p>
          <Link
            href="/dashboard"
            className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3 rounded-lg text-lg font-medium inline-flex items-center"
          >
            Go to Dashboard
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center text-gray-600">
            <p className="mb-2">XAI Finance Benchmark Platform</p>
            <p className="text-sm">
              Master's Thesis - Nova School of Business and Economics
            </p>
            <p className="text-sm mt-2">
              Built with Next.js 15, TypeScript, and TailwindCSS
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
