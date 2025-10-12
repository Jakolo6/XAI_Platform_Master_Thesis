/**
 * DASHBOARD PAGE
 * Route: /dashboard
 * 
 * Main dashboard after login - protected route
 */

'use client';

import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Database, BarChart3, Brain, ArrowRight, Sparkles, FileText, Users, Download, Loader2 } from 'lucide-react'
import { modelsAPI } from '@/lib/api'

export const dynamic = 'force-dynamic';

export default function DashboardPage() {
  const router = useRouter()
  const supabase = createClient()
  const [user, setUser] = useState<any>(null)
  const [stats, setStats] = useState({
    totalModels: 0,
    completedModels: 0,
    trainingModels: 0
  })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    checkAuth()
    fetchStats()
  }, [])

  const checkAuth = async () => {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      router.push('/login')
    } else {
      setUser(user)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await modelsAPI.getAll()
      const models = response.data || []
      setStats({
        totalModels: models.length,
        completedModels: models.filter((m: any) => m.status === 'completed').length,
        trainingModels: models.filter((m: any) => m.status === 'training').length
      })
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
      </div>
    )
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
                <Brain className="h-6 w-6 text-blue-600" />
              </div>
              {isLoading ? (
                <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
              ) : (
                <span className="text-2xl font-bold text-gray-900">{stats.totalModels}</span>
              )}
            </div>
            <h3 className="text-sm font-medium text-gray-600">Your Trained Models</h3>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <BarChart3 className="h-6 w-6 text-green-600" />
              </div>
              {isLoading ? (
                <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
              ) : (
                <span className="text-2xl font-bold text-gray-900">{stats.completedModels}</span>
              )}
            </div>
            <h3 className="text-sm font-medium text-gray-600">Completed Models</h3>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Database className="h-6 w-6 text-orange-600" />
              </div>
              <span className="text-2xl font-bold text-gray-900">3</span>
            </div>
            <h3 className="text-sm font-medium text-gray-600">Available Datasets</h3>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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

            <Link
              href="/research"
              className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow group relative overflow-hidden"
            >
              <div className="absolute top-2 right-2">
                <span className="bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                  NEW
                </span>
              </div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-pink-100 rounded-lg flex items-center justify-center">
                  <Sparkles className="h-6 w-6 text-purple-600" />
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-purple-600 transition-colors" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                XAI Research Lab
              </h3>
              <p className="text-sm text-gray-600">
                Compare explanation quality, view leaderboards, and export results
              </p>
            </Link>

            <Link
              href="/study"
              className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow group"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                  <Users className="h-6 w-6 text-orange-600" />
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-orange-600 transition-colors" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Human Study
              </h3>
              <p className="text-sm text-gray-600">
                Evaluate trust and understanding of AI explanations
              </p>
            </Link>

            <Link
              href="/reports"
              className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow group"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center">
                  <Download className="h-6 w-6 text-teal-600" />
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-teal-600 transition-colors" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Export Reports
              </h3>
              <p className="text-sm text-gray-600">
                Download CSV/JSON data for thesis documentation
              </p>
            </Link>
          </div>
        </div>

        {/* Getting Started Guide */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg shadow-lg p-8 text-white">
          <h2 className="text-2xl font-bold mb-4">Complete XAI Workflow</h2>
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
              <span>Train models - SHAP explanations are auto-generated!</span>
            </li>
            <li className="flex items-start">
              <span className="flex-shrink-0 w-6 h-6 bg-white text-blue-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">
                3
              </span>
              <span>View model details with Global & Local SHAP explanations</span>
            </li>
            <li className="flex items-start">
              <span className="flex-shrink-0 w-6 h-6 bg-white text-blue-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">
                4
              </span>
              <span>Evaluate explanation quality and compare SHAP vs LIME</span>
            </li>
            <li className="flex items-start">
              <span className="flex-shrink-0 w-6 h-6 bg-white text-blue-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">
                5
              </span>
              <span>Export results as CSV/JSON for your thesis research</span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  )
}
