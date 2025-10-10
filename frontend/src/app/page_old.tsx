/**
 * HOME PAGE - Research-Focused Landing Page
 * Route: /
 * 
 * Enhanced homepage for Master Thesis presentation
 * Features research context, thesis information, and academic credibility
 */

'use client';

import Link from 'next/link';
import { ArrowRight, BarChart3, Brain, Database, Github, Layers, Shield, Zap, TrendingUp, Scale, FileText, Award, CheckCircle2 } from 'lucide-react';
import { motion } from 'framer-motion';

// Animation variants
const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5 }
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};

export default function Home() {
  return (
    <div className="bg-gradient-to-b from-blue-50 via-white to-gray-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
          <motion.div 
            className="text-center"
            initial="initial"
            animate="animate"
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp} className="mb-4">
              <span className="inline-flex items-center px-4 py-1.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                <Award className="w-4 h-4 mr-2" />
                Master Thesis 2025 · Nova School of Business and Economics
              </span>
            </motion.div>
            
            <motion.h1 
              variants={fadeInUp}
              className="text-4xl sm:text-6xl font-bold text-gray-900 mb-6"
            >
              Explainable AI Benchmark Platform
              <br />
              <span className="bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                for Financial Services
              </span>
            </motion.h1>
            
            <motion.p 
              variants={fadeInUp}
              className="text-xl text-gray-600 mb-4 max-w-3xl mx-auto"
            >
              An open-source research platform to quantify how well financial AI models balance 
              predictive performance and interpretability — with SHAP, LIME, and counterfactual explanations.
            </motion.p>
            
            <motion.p 
              variants={fadeInUp}
              className="text-sm text-gray-500 mb-8"
            >
              Created by Jakob Lindner · Nova SBE
            </motion.p>
            
            <motion.div 
              variants={fadeInUp}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Link
                href="/register"
                className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl"
              >
                Try the Platform
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <a
                href="https://github.com/Jakolo6/XAI_Platform_Master_Thesis"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center px-8 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
              >
                <Github className="mr-2 h-5 w-5" />
                View on GitHub
              </a>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Platform Features
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Everything you need to benchmark and evaluate explainability algorithms 
              on real-world financial datasets.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-gradient-to-br from-blue-50 to-white p-8 rounded-xl border border-blue-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Benchmark XAI Algorithms
              </h3>
              <p className="text-gray-600">
                Compare SHAP, LIME, and other state-of-the-art explainability methods 
                across multiple datasets and metrics.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-gradient-to-br from-green-50 to-white p-8 rounded-xl border border-green-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center mb-4">
                <Database className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Dataset Flexibility
              </h3>
              <p className="text-gray-600">
                Plug in IEEE-CIS Fraud Detection, German Credit, Give Me Some Credit, 
                and more financial datasets with ease.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-gradient-to-br from-purple-50 to-white p-8 rounded-xl border border-purple-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center mb-4">
                <Layers className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Supabase Integration
              </h3>
              <p className="text-gray-600">
                Persistent research results and experiment tracking powered by 
                Supabase for reliable cloud storage.
              </p>
            </div>
          </div>

          {/* Additional Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
            {/* Feature 4 */}
            <div className="bg-gradient-to-br from-orange-50 to-white p-8 rounded-xl border border-orange-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-orange-600 rounded-lg flex items-center justify-center mb-4">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Multiple ML Models
              </h3>
              <p className="text-gray-600">
                Train and compare XGBoost, Random Forest, Neural Networks, and more 
                on your datasets.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="bg-gradient-to-br from-red-50 to-white p-8 rounded-xl border border-red-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-red-600 rounded-lg flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Reproducible Research
              </h3>
              <p className="text-gray-600">
                All experiments are tracked and versioned, ensuring reproducibility 
                for academic research.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="bg-gradient-to-br from-indigo-50 to-white p-8 rounded-xl border border-indigo-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-indigo-600 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Performance Metrics
              </h3>
              <p className="text-gray-600">
                Comprehensive evaluation with AUC-ROC, precision, recall, and 
                explainability-specific metrics.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section id="architecture" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Platform Architecture
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Modern, scalable architecture built with industry-leading technologies.
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8 md:p-12">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
              {/* Frontend */}
              <div className="text-center">
                <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Zap className="h-10 w-10 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Frontend</h3>
                <p className="text-gray-600 mb-4">Next.js 15 + React</p>
                <ul className="text-sm text-gray-500 space-y-1">
                  <li>• TypeScript</li>
                  <li>• TailwindCSS</li>
                  <li>• shadcn/ui</li>
                </ul>
              </div>

              {/* Arrow */}
              <div className="hidden md:flex justify-center">
                <ArrowRight className="h-8 w-8 text-gray-400" />
              </div>

              {/* Backend */}
              <div className="text-center">
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Layers className="h-10 w-10 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Backend</h3>
                <p className="text-gray-600 mb-4">FastAPI + Python</p>
                <ul className="text-sm text-gray-500 space-y-1">
                  <li>• Async/Await</li>
                  <li>• ML Pipeline</li>
                  <li>• XAI Methods</li>
                </ul>
              </div>

              {/* Arrow */}
              <div className="hidden md:flex justify-center md:col-start-2">
                <ArrowRight className="h-8 w-8 text-gray-400" />
              </div>

              {/* Database */}
              <div className="text-center md:col-start-3">
                <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Database className="h-10 w-10 text-purple-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Database</h3>
                <p className="text-gray-600 mb-4">Supabase</p>
                <ul className="text-sm text-gray-500 space-y-1">
                  <li>• PostgreSQL</li>
                  <li>• Auth</li>
                  <li>• Storage</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-blue-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to Start Benchmarking?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join researchers worldwide in advancing explainable AI for financial services.
          </p>
          <Link
            href="/register"
            className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-gray-50 transition-colors"
          >
            Get Started Free
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </section>
    </div>
  );
}
