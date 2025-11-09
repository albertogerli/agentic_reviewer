'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useReviewStore } from '../store/reviewStore';

export function LiveProgress() {
  const { progress, agents, isProcessing } = useReviewStore();
  
  if (!isProcessing && progress.progress === 0) {
    return null;
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-4xl mx-auto mt-8"
    >
      {/* Progress Bar */}
      <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
              <div className="absolute inset-0 w-3 h-3 bg-red-500 rounded-full animate-ping" />
            </div>
            <h3 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              LIVE ANALYSIS
            </h3>
          </div>
          <div className="text-3xl font-bold text-primary-600">
            {Math.round(progress.progress)}%
          </div>
        </div>
        
        {/* Status Message with Icon */}
        <div className="bg-primary-50 border border-primary-200 rounded-xl p-4">
          <p className="text-lg text-gray-800 font-medium">
            {progress.status}
          </p>
          {progress.totalAgents > 0 && (
            <p className="text-sm text-gray-600 mt-2">
              🤖 {progress.totalAgents} AI agents deployed • {progress.completedAgents} completed
            </p>
          )}
        </div>
        
        {/* Progress Bar */}
        <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden">
          <motion.div
            className="absolute inset-y-0 left-0 bg-gradient-primary rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress.progress}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-shimmer" />
        </div>
        
        {/* Agent Counter */}
        {progress.totalAgents > 0 && (
          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {progress.completedAgents}
              </div>
              <div className="text-sm text-gray-600 mt-1">Completed</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-600">
                {progress.totalAgents}
              </div>
              <div className="text-sm text-gray-600 mt-1">Total Agents</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-400">
                {progress.totalAgents - progress.completedAgents}
              </div>
              <div className="text-sm text-gray-600 mt-1">Remaining</div>
            </div>
          </div>
        )}
      </div>
      
      {/* Agent Activity Feed */}
      {agents.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl shadow-xl p-8 mt-6"
        >
          <h4 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-3" />
            Agent Activity
          </h4>
          
          <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
            <AnimatePresence>
              {agents.map((agent, index) => (
                <motion.div
                  key={agent.key}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`
                    flex items-center justify-between p-4 rounded-xl
                    transition-all duration-300
                    ${agent.status === 'completed' ? 'bg-green-50 border-2 border-green-200' :
                      agent.status === 'analyzing' ? 'bg-yellow-50 border-2 border-yellow-300 shadow-lg scale-105' :
                      'bg-gray-50 border-2 border-gray-200'}
                  `}
                >
                  <div className="flex items-center space-x-4">
                    <span className="text-3xl">{agent.icon}</span>
                    <div>
                      <p className="font-semibold text-gray-900">{agent.name}</p>
                      <p className="text-sm text-gray-600">
                        {agent.status === 'completed' ? 'Analysis complete' :
                         agent.status === 'analyzing' ? 'Analyzing document...' :
                         'Queued'}
                      </p>
                    </div>
                  </div>
                  
                  <div className={`
                    px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wider
                    ${agent.status === 'completed' ? 'bg-green-500 text-white' :
                      agent.status === 'analyzing' ? 'bg-yellow-500 text-white animate-pulse' :
                      'bg-gray-300 text-gray-600'}
                  `}>
                    {agent.status === 'completed' ? '✓ Done' :
                     agent.status === 'analyzing' ? '⚡ Running' :
                     '⏳ Pending'}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

