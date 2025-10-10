/**
 * HOME PAGE - Research-Focused Landing Page
 * Route: /
 * 
 * Enhanced homepage for Master Thesis presentation
 * Features research context, thesis information, and academic credibility
 */

'use client';

import Link from 'next/link';
import { ArrowRight, BarChart3, Brain, Database, Github, Layers, Shield, Zap, TrendingUp, Scale, FileText, Award, CheckCircle2, Target, Users, BookOpen } from 'lucide-react';
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

const scaleIn = {
  initial: { opacity: 0, scale: 0.9 },
  whileInView: { opacity: 1, scale: 1 },
  transition: { duration: 0.5 },
  viewport: { once: true }
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

      {/* What the Platform Does */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              What the Platform Does
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              A complete workflow for training models, generating explanations, and benchmarking results.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 - Train Models */}
            <motion.div 
              className="bg-gradient-to-br from-blue-50 to-white p-8 rounded-xl border border-blue-100 hover:shadow-lg transition-all"
              {...scaleIn}
            >
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Train Models
              </h3>
              <p className="text-gray-600">
                Upload or link financial datasets (e.g., IEEE-CIS Fraud, Give Me Some Credit) and train models 
                like XGBoost, Random Forest, or Neural Networks.
              </p>
            </motion.div>

            {/* Feature 2 - Generate Explanations */}
            <motion.div 
              className="bg-gradient-to-br from-orange-50 to-white p-8 rounded-xl border border-orange-100 hover:shadow-lg transition-all"
              {...scaleIn}
              transition={{ delay: 0.1 }}
            >
              <div className="w-12 h-12 bg-orange-600 rounded-lg flex items-center justify-center mb-4">
                <FileText className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Generate Explanations
              </h3>
              <p className="text-gray-600">
                Apply SHAP, LIME, or counterfactual explanations to reveal how features influence each prediction 
                and make AI decisions transparent.
              </p>
            </motion.div>

            {/* Feature 3 - Benchmark Results */}
            <motion.div 
              className="bg-gradient-to-br from-green-50 to-white p-8 rounded-xl border border-green-100 hover:shadow-lg transition-all"
              {...scaleIn}
              transition={{ delay: 0.2 }}
            >
              <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center mb-4">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Benchmark Results
              </h3>
              <p className="text-gray-600">
                Quantify and compare models across explainability metrics such as faithfulness, stability, 
                sparsity, and runtime performance.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Why It Matters - Research Focus */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              {/* Left - Text */}
              <div>
                <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
                  Why Explainability Matters
                </h2>
                <p className="text-lg text-gray-600 mb-6">
                  Explainability is essential for trust and regulatory compliance in financial AI. 
                  This platform provides a standardized way to evaluate how transparent and reliable 
                  model explanations are — aligned with EU AI Act principles on fairness, oversight, and traceability.
                </p>
                <div className="space-y-4">
                  <div className="flex items-start">
                    <CheckCircle2 className="h-6 w-6 text-green-600 mr-3 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-gray-900">Regulatory Compliance</h4>
                      <p className="text-gray-600">Meet EU AI Act requirements for transparency and accountability</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <CheckCircle2 className="h-6 w-6 text-green-600 mr-3 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-gray-900">Trust & Adoption</h4>
                      <p className="text-gray-600">Build confidence in AI decisions among stakeholders and users</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <CheckCircle2 className="h-6 w-6 text-green-600 mr-3 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-gray-900">Risk Management</h4>
                      <p className="text-gray-600">Identify and mitigate biases and errors in financial models</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right - Visual */}
              <div className="relative">
                <div className="bg-white rounded-xl shadow-lg p-8">
                  <div className="flex items-center justify-between mb-8">
                    <div className="text-center flex-1">
                      <div className="text-3xl font-bold text-blue-600 mb-2">95%</div>
                      <div className="text-sm text-gray-600">Accuracy</div>
                    </div>
                    <Scale className="h-12 w-12 text-gray-400 mx-4" />
                    <div className="text-center flex-1">
                      <div className="text-3xl font-bold text-orange-600 mb-2">89%</div>
                      <div className="text-sm text-gray-600">Explainability</div>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <span className="text-sm font-medium text-gray-700">Transparency</span>
                      <CheckCircle2 className="h-5 w-5 text-blue-600" />
                    </div>
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <span className="text-sm font-medium text-gray-700">Faithfulness</span>
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    </div>
                    <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                      <span className="text-sm font-medium text-gray-700">Human Oversight</span>
                      <CheckCircle2 className="h-5 w-5 text-purple-600" />
                    </div>
                    <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                      <span className="text-sm font-medium text-gray-700">Regulatory Ready</span>
                      <CheckCircle2 className="h-5 w-5 text-orange-600" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Architecture Section */}
      <section id="architecture" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              From Data to Decision Transparency
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Modern, scalable architecture built with industry-leading technologies.
            </p>
          </motion.div>

          <motion.div 
            className="bg-gradient-to-br from-gray-50 to-white rounded-xl shadow-lg p-8 md:p-12 border border-gray-200"
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
          >
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
              {/* Frontend */}
              <motion.div 
                className="text-center group cursor-pointer"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-blue-600 transition-colors">
                  <Zap className="h-10 w-10 text-blue-600 group-hover:text-white transition-colors" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Frontend</h3>
                <p className="text-gray-600 mb-4">Next.js + Netlify</p>
                <div className="text-sm text-gray-500 space-y-1">
                  <p>Interactive dashboard</p>
                  <p>Visual analytics</p>
                  <p>Responsive design</p>
                </div>
              </motion.div>

              {/* Arrow */}
              <div className="hidden md:flex justify-center">
                <ArrowRight className="h-8 w-8 text-gray-400" />
              </div>

              {/* Backend */}
              <motion.div 
                className="text-center group cursor-pointer"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-green-600 transition-colors">
                  <Layers className="h-10 w-10 text-green-600 group-hover:text-white transition-colors" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Backend</h3>
                <p className="text-gray-600 mb-4">FastAPI + Railway</p>
                <div className="text-sm text-gray-500 space-y-1">
                  <p>Async tasks</p>
                  <p>Model training</p>
                  <p>SHAP computation</p>
                </div>
              </motion.div>

              {/* Arrow */}
              <div className="hidden md:flex justify-center md:col-start-2">
                <ArrowRight className="h-8 w-8 text-gray-400" />
              </div>

              {/* Database */}
              <motion.div 
                className="text-center md:col-start-3 group cursor-pointer"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-purple-600 transition-colors">
                  <Database className="h-10 w-10 text-purple-600 group-hover:text-white transition-colors" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Database</h3>
                <p className="text-gray-600 mb-4">Supabase</p>
                <div className="text-sm text-gray-500 space-y-1">
                  <p>Experiment metadata</p>
                  <p>Results storage</p>
                  <p>Audit logs</p>
                </div>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Thesis Context */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            className="bg-white rounded-xl shadow-lg p-8 md:p-12 border-l-4 border-blue-600"
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
          >
            <div className="flex items-start mb-6">
              <BookOpen className="h-8 w-8 text-blue-600 mr-4 flex-shrink-0" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Academic Origin</h2>
                <p className="text-gray-600">
                  Developed as part of the Master Thesis <span className="font-semibold">"Explainable AI in Financial Services"</span> by 
                  Jakob Lindner at Nova School of Business and Economics.
                </p>
              </div>
            </div>
            <p className="text-gray-600 mb-6">
              The platform demonstrates how modern XAI techniques can make financial decision systems transparent, 
              accountable, and compliant with emerging regulations like the EU AI Act.
            </p>
            <div className="flex items-center justify-between pt-6 border-t border-gray-200">
              <div className="flex items-center space-x-6">
                <div className="text-sm">
                  <div className="font-semibold text-gray-900">Nova SBE</div>
                  <div className="text-gray-500">2025</div>
                </div>
                <div className="text-sm">
                  <div className="font-semibold text-gray-900">Open Source</div>
                  <div className="text-gray-500">MIT License</div>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <img src="/api/placeholder/80/30" alt="Nova SBE" className="h-8 opacity-60" />
                <img src="/api/placeholder/80/30" alt="Supabase" className="h-8 opacity-60" />
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-blue-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
              Ready to Explore Explainable AI?
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              Join researchers worldwide in advancing transparent and accountable AI for financial services.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/register"
                className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-gray-50 transition-colors shadow-lg"
              >
                Get Started Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link
                href="/benchmarks"
                className="inline-flex items-center justify-center px-8 py-3 border-2 border-white text-base font-medium rounded-md text-white hover:bg-blue-700 transition-colors"
              >
                View Benchmarks
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
