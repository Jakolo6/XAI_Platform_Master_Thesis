/**
 * DASHBOARD PAGE
 * Route: /dashboard
 * 
 * Main dashboard after login - protected route
 */

import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { Database, BarChart3, Brain, ArrowRight } from 'lucide-react'

export default async function DashboardPage() {
  const supabase = await createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Welcome Section */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Welcome back!
          </h1>
          <p className="text-lg text-gray-600">
            {user.email}
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Database className="h-6 w-6 text-blue-600" />
              </div>
              <span className="text-2xl font-bold text-gray-900">3</span>
            </div>
            <h3 className="text-sm font-medium text-gray-600">Available Datasets</h3>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Brain className="h-6 w-6 text-green-600" />
              </div>
              <span className="text-2xl font-bold text-gray-900">6</span>
            </div>
            <h3 className="text-sm font-medium text-gray-600">Model Types</h3>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <BarChart3 className="h-6 w-6 text-purple-600" />
              </div>
              <span className="text-2xl font-bold text-gray-900">2</span>
            </div>
            <h3 className="text-sm font-medium text-gray-600">XAI Methods</h3>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Link
              href="/datasets"
              className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow group"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Database className="h-6 w-6 text-blue-600" />
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-blue-600 transition-colors" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Manage Datasets
              </h3>
              <p className="text-sm text-gray-600">
                View and configure available financial datasets for training
              </p>
            </Link>

            <Link
              href="/models/train"
              className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow group"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <Brain className="h-6 w-6 text-green-600" />
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-green-600 transition-colors" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Train Model
              </h3>
              <p className="text-sm text-gray-600">
                Start training a new model on your selected dataset
              </p>
            </Link>

            <Link
              href="/benchmarks"
              className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow group"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <BarChart3 className="h-6 w-6 text-purple-600" />
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-purple-600 transition-colors" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                View Benchmarks
              </h3>
              <p className="text-sm text-gray-600">
                Compare model performance across different datasets
              </p>
            </Link>

            <div className="bg-gray-50 rounded-lg border border-dashed border-gray-300 p-6 opacity-60">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                  <Brain className="h-6 w-6 text-gray-400" />
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">
                Generate Explanations
              </h3>
              <p className="text-sm text-gray-500">
                Coming soon - SHAP and LIME explanations
              </p>
            </div>
          </div>
        </div>

        {/* Getting Started Guide */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg shadow-lg p-8 text-white">
          <h2 className="text-2xl font-bold mb-4">Getting Started</h2>
          <ol className="space-y-3">
            <li className="flex items-start">
              <span className="flex-shrink-0 w-6 h-6 bg-white text-blue-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">
                1
              </span>
              <span>Browse available datasets and understand their characteristics</span>
            </li>
            <li className="flex items-start">
              <span className="flex-shrink-0 w-6 h-6 bg-white text-blue-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">
                2
              </span>
              <span>Train models using different algorithms (XGBoost, Random Forest, etc.)</span>
            </li>
            <li className="flex items-start">
              <span className="flex-shrink-0 w-6 h-6 bg-white text-blue-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">
                3
              </span>
              <span>Compare performance across datasets in the benchmarks section</span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  )
}
