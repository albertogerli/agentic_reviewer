'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface TrendsChartProps {
  days: number;
}

interface TrendData {
  date: string;
  avg_score: number;
  count: number;
  min_score: number;
  max_score: number;
}

export function TrendsChart({ days }: TrendsChartProps) {
  const [data, setData] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrends();
  }, [days]);

  const fetchTrends = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/analytics/trends?days=${days}`);
      const result = await response.json();
      setData(result.trends || []);
    } catch (error) {
      console.error('Error fetching trends:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8 text-center">
        <p className="text-gray-500">No trend data available</p>
      </div>
    );
  }

  const maxScore = Math.max(...data.map(d => d.max_score));
  const avgOverall = Math.round(data.reduce((a, b) => a + b.avg_score, 0) / data.length);
  const totalReviews = data.reduce((a, b) => a + b.count, 0);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white rounded-xl shadow-lg p-8"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
          <span>📈</span>
          <span>Score Trends Over Time</span>
        </h2>
        <p className="text-gray-600 mt-1">
          Average document scores for the last {days} days
        </p>
      </div>

      {/* Simple Bar Chart with CSS */}
      <div className="space-y-3 mb-6">
        {data.slice(-10).map((item, idx) => (
          <motion.div
            key={item.date}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
            className="relative"
          >
            <div className="flex items-center space-x-3">
              <div className="w-24 text-xs text-gray-600 font-medium">
                {new Date(item.date).toLocaleDateString('it-IT', { month: 'short', day: 'numeric' })}
              </div>
              <div className="flex-1 relative h-12 bg-gray-100 rounded-lg overflow-hidden">
                {/* Avg Score Bar */}
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${item.avg_score}%` }}
                  transition={{ duration: 0.8, delay: idx * 0.05 }}
                  className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary-500 to-primary-600 flex items-center justify-end pr-3"
                >
                  <span className="text-white font-bold text-sm">{item.avg_score}</span>
                </motion.div>
                
                {/* Min/Max indicators */}
                <div 
                  className="absolute top-0 bottom-0 w-1 bg-red-400" 
                  style={{ left: `${item.min_score}%` }}
                  title={`Min: ${item.min_score}`}
                />
                <div 
                  className="absolute top-0 bottom-0 w-1 bg-green-400" 
                  style={{ left: `${item.max_score}%` }}
                  title={`Max: ${item.max_score}`}
                />
              </div>
              <div className="w-16 text-sm text-gray-600 text-right">
                {item.count} rev
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center space-x-6 text-sm text-gray-600 mb-6 pb-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-3 bg-gradient-to-r from-primary-500 to-primary-600 rounded"></div>
          <span>Average Score</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-red-400 rounded"></div>
          <span>Min</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-400 rounded"></div>
          <span>Max</span>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-primary-600">
            {avgOverall}
          </div>
          <div className="text-sm text-gray-600 mt-1">Overall Avg</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">
            {maxScore}
          </div>
          <div className="text-sm text-gray-600 mt-1">Best Score</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-700">
            {totalReviews}
          </div>
          <div className="text-sm text-gray-600 mt-1">Total Reviews</div>
        </div>
      </div>
    </motion.div>
  );
}
