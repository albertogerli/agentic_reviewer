'use client';

import { motion } from 'framer-motion';
import { useMemo } from 'react';

interface RiskHeatmapProps {
  riskData: {
    [category: string]: {
      count: number;
      score: number;
    };
  };
}

export function RiskHeatmap({ riskData }: RiskHeatmapProps) {
  // Prepare data for visualization
  const categories = useMemo(() => {
    return Object.entries(riskData)
      .map(([name, data]) => ({
        name,
        count: data.count,
        score: data.score,
        riskLevel: getRiskLevel(data.score, data.count)
      }))
      .sort((a, b) => b.score - a.score);
  }, [riskData]);

  const maxScore = useMemo(() => {
    return Math.max(...categories.map(c => c.score), 1);
  }, [categories]);

  if (categories.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8 text-center">
        <div className="text-6xl mb-4">🎉</div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">No Risks Detected!</h3>
        <p className="text-gray-600">Your document appears to be in excellent shape.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-red-500 to-orange-500 text-white p-6">
        <h3 className="text-2xl font-bold flex items-center space-x-3">
          <span className="text-3xl">🔥</span>
          <span>Risk Heatmap by Category</span>
        </h3>
        <p className="text-white/90 mt-2">
          Visual breakdown of document risks across categories
        </p>
      </div>

      {/* Heatmap Grid */}
      <div className="p-6 space-y-3">
        {categories.map((category, idx) => (
          <motion.div
            key={category.name}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
            className="group"
          >
            {/* Category Header */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{getCategoryIcon(category.name)}</span>
                <span className="font-semibold text-gray-900 capitalize">
                  {category.name}
                </span>
                <span className="text-sm text-gray-500">
                  ({category.count} {category.count === 1 ? 'issue' : 'issues'})
                </span>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${getRiskLevelColors(category.riskLevel)}`}>
                {category.riskLevel.toUpperCase()}
              </span>
            </div>

            {/* Risk Bar */}
            <div className="relative h-10 bg-gray-100 rounded-lg overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(category.score / maxScore) * 100}%` }}
                transition={{ duration: 0.6, delay: idx * 0.05 }}
                className={`h-full flex items-center justify-end pr-3 ${getRiskBarColor(category.score / maxScore)}`}
              >
                <span className="text-sm font-bold text-white">
                  Risk: {category.score.toFixed(1)}
                </span>
              </motion.div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Legend */}
      <div className="px-6 pb-6">
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h4 className="text-xs font-semibold text-gray-700 mb-3">RISK LEVELS</h4>
          <div className="grid grid-cols-4 gap-2">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-600 rounded"></div>
              <span className="text-xs text-gray-700">Critical</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-orange-500 rounded"></div>
              <span className="text-xs text-gray-700">High</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-yellow-500 rounded"></div>
              <span className="text-xs text-gray-700">Medium</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded"></div>
              <span className="text-xs text-gray-700">Low</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function getRiskLevel(score: number, count: number): 'critical' | 'high' | 'medium' | 'low' {
  // Higher score or more issues = higher risk
  if (score >= 10 || count >= 10) return 'critical';
  if (score >= 5 || count >= 5) return 'high';
  if (score >= 2 || count >= 2) return 'medium';
  return 'low';
}

function getRiskLevelColors(level: string): string {
  switch (level) {
    case 'critical':
      return 'bg-red-600 text-white';
    case 'high':
      return 'bg-orange-500 text-white';
    case 'medium':
      return 'bg-yellow-500 text-white';
    case 'low':
      return 'bg-green-500 text-white';
    default:
      return 'bg-gray-500 text-white';
  }
}

function getRiskBarColor(ratio: number): string {
  if (ratio >= 0.75) return 'bg-gradient-to-r from-red-600 to-red-500';
  if (ratio >= 0.5) return 'bg-gradient-to-r from-orange-600 to-orange-500';
  if (ratio >= 0.25) return 'bg-gradient-to-r from-yellow-600 to-yellow-500';
  return 'bg-gradient-to-r from-green-600 to-green-500';
}

function getCategoryIcon(category: string): string {
  const icons: Record<string, string> = {
    compliance: '⚖️',
    legal: '📜',
    technical: '⚙️',
    content: '📝',
    style: '✍️',
    security: '🔒',
    financial: '💰',
    quality: '⭐',
    accessibility: '♿',
    performance: '⚡',
  };
  return icons[category.toLowerCase()] || '📋';
}

