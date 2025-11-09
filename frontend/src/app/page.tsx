'use client';

import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileUpload } from '../components/FileUpload';
import { LiveProgress } from '../components/LiveProgress';
import { ReviewResults } from '../components/ReviewResults';
import { useReviewStore } from '../store/reviewStore';
import { SparklesIcon, CpuChipIcon, GlobeAltIcon } from '@heroicons/react/24/outline';

export default function Home() {
  const { file, config, setConfig, startReview, isProcessing, progress, reset } = useReviewStore();
  
  // Reset state ONLY on first mount, not on every render
  useEffect(() => {
    // Only reset if there's stale data (completed review)
    if (progress.progress === 100 && !isProcessing) {
      console.log('🔄 Resetting stale review data');
      reset();
    }
  }, []); // Empty deps = only on mount
  
  const handleStartReview = () => {
    if (file) {
      startReview();
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-primary rounded-xl flex items-center justify-center shadow-lg">
                <SparklesIcon className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                  Agentic Reviewer
                </h1>
                <p className="text-sm text-gray-600">AI-Powered Document Analysis</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <a
                href="/history"
                className="px-4 py-2 text-sm font-semibold text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors flex items-center space-x-2"
              >
                <span>📊</span>
                <span>Analytics</span>
              </a>
              <span className="px-3 py-1 text-xs font-semibold text-green-700 bg-green-100 rounded-full">
                ● Online
              </span>
              <span className="px-3 py-1 text-xs font-medium text-gray-600 bg-gray-100 rounded-full">
                v2.0.0
              </span>
            </div>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h2 className="text-5xl font-extrabold text-gray-900 mb-4">
            Professional Document
            <span className="bg-gradient-primary bg-clip-text text-transparent"> Review System</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Upload your document and let our AI agents provide comprehensive analysis,
            fact-checking, and actionable recommendations.
          </p>
        </motion.div>
        
        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12"
        >
          <FeatureCard
            icon={<CpuChipIcon className="w-8 h-8" />}
            title="Multi-Agent AI"
            description="Specialized AI agents analyze different aspects of your document"
          />
          <FeatureCard
            icon={<GlobeAltIcon className="w-8 h-8" />}
            title="Web Research"
            description="Real-time fact-checking with internet sources and citations"
          />
          <FeatureCard
            icon={<SparklesIcon className="w-8 h-8" />}
            title="Iterative Improvement"
            description="Optional iterative mode to refine your document automatically"
          />
        </motion.div>
        
        {/* Main Content */}
        <div className="space-y-8">
          {/* Upload Section */}
          {!isProcessing && progress.progress === 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-2xl shadow-2xl p-8"
            >
              <FileUpload />
              
              {/* Configuration Options */}
              {file && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-8 pt-8 border-t border-gray-200"
                >
                  <h3 className="text-lg font-bold text-gray-900 mb-6">Review Options</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Language Select */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Output Language
                      </label>
                      <select
                        value={config.output_language}
                        onChange={(e) => setConfig({ output_language: e.target.value })}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      >
                        <option value="">Auto-detect</option>
                        <option value="English">English</option>
                        <option value="Italian">Italiano</option>
                        <option value="Spanish">Español</option>
                        <option value="French">Français</option>
                        <option value="German">Deutsch</option>
                      </select>
                    </div>
                    
                    {/* Checkboxes */}
                    <div className="space-y-3">
                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={config.enable_deep_review}
                          onChange={(e) => setConfig({ enable_deep_review: e.target.checked })}
                          className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                        />
                        <span className="text-sm font-medium text-gray-700">
                          Deep Review (Tier 3 Specialists)
                        </span>
                      </label>
                      
                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={config.enable_python_tools}
                          onChange={(e) => setConfig({ enable_python_tools: e.target.checked })}
                          className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                        />
                        <span className="text-sm font-medium text-gray-700">
                          Python Data Validation
                        </span>
                      </label>
                      
                      {/* Iterative Improvement con opzioni dettagliate */}
                      <div className="space-y-3">
                        <label className="flex items-center space-x-3 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={config.enable_iterative}
                            onChange={(e) => setConfig({ enable_iterative: e.target.checked })}
                            className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                          />
                          <span className="text-sm font-medium text-gray-700">
                            Iterative Improvement
                          </span>
                        </label>
                        
                        {/* Opzioni iterative dettagliate */}
                        {config.enable_iterative && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            className="ml-8 pl-4 border-l-2 border-primary-200 space-y-3 bg-primary-50/30 p-3 rounded-r-lg"
                          >
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Max Iterations
                              </label>
                              <input
                                type="number"
                                min="1"
                                max="10"
                                value={config.max_iterations}
                                onChange={(e) => setConfig({
                                  max_iterations: parseInt(e.target.value) || 3
                                })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                              />
                              <p className="text-xs text-gray-500 mt-1">
                                🔄 How many refinement cycles (1-10)
                              </p>
                            </div>
                            
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                Target Score
                              </label>
                              <input
                                type="number"
                                min="0"
                                max="100"
                                step="5"
                                value={config.target_score}
                                onChange={(e) => setConfig({
                                  target_score: parseFloat(e.target.value) || 85
                                })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                              />
                              <p className="text-xs text-gray-500 mt-1">
                                🎯 Stop when document reaches this quality score (0-100)
                              </p>
                            </div>
                            
                            <label className="flex items-center space-x-2 cursor-pointer">
                              <input
                                type="checkbox"
                                checked={config.enable_interactive}
                                onChange={(e) => setConfig({ enable_interactive: e.target.checked })}
                                className="w-4 h-4 text-primary-600 rounded"
                              />
                              <span className="text-sm text-gray-700">
                                💬 Interactive Mode (AI can ask questions)
                              </span>
                            </label>
                          </motion.div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Start Button */}
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={handleStartReview}
                    disabled={!file}
                    className={`
                      mt-8 w-full py-4 rounded-xl font-bold text-lg
                      bg-gradient-primary text-white
                      shadow-lg hover:shadow-xl
                      transition-all duration-300
                      disabled:opacity-50 disabled:cursor-not-allowed
                    `}
                  >
                    <span className="flex items-center justify-center space-x-2">
                      <SparklesIcon className="w-6 h-6" />
                      <span>Start AI Review</span>
                    </span>
                  </motion.button>
                </motion.div>
              )}
            </motion.div>
          )}
          
          {/* Progress Section */}
          <LiveProgress />
          
          {/* Results Section */}
          <ReviewResults />
        </div>
      </main>
      
      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-600">
            Powered by GPT-5 • OpenAI Responses API • Multi-Agent Architecture
          </p>
        </div>
      </footer>
    </div>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      className="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-shadow duration-300"
    >
      <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center text-primary-600 mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-bold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </motion.div>
  );
}

