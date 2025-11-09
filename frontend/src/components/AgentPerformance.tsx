'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface AgentPerformanceProps {
  days: number;
}

interface AgentStats {
  name: string;
  total_reviews: number;
  total_issues_found: number;
  critical_issues: number;
  high_issues: number;
  avg_issues_per_review: number;
}

export function AgentPerformance({ days }: AgentPerformanceProps) {
  const [data, setData] = useState<AgentStats[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPerformance();
  }, [days]);

  const fetchPerformance = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/analytics/agents-performance?days=${days}`);
      const result = await response.json();
      setData(result.agents || []);
    } catch (error) {
      console.error('Error fetching agent performance:', error);
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
        <p className="text-gray-500">No agent performance data available</p>
      </div>
    );
  }

  // Top 10 agents
  const topAgents = data.slice(0, 10);
  const maxIssues = Math.max(...topAgents.map(a => a.total_issues_found));

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white rounded-xl shadow-lg p-8"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
          <span>🤖</span>
          <span>Agent Performance</span>
        </h2>
        <p className="text-gray-600 mt-1">
          Top performing agents by issues found
        </p>
      </div>

      {/* Horizontal Bar Chart with CSS */}
      <div className="space-y-3 mb-8">
        {topAgents.map((agent, idx) => (
          <motion.div
            key={agent.name}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
            className="relative"
          >
            <div className="flex items-center space-x-3">
              <div className="w-40 text-sm font-medium text-gray-900 truncate">
                {agent.name}
              </div>
              <div className="flex-1 relative h-10 bg-gray-100 rounded-lg overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(agent.total_issues_found / maxIssues) * 100}%` }}
                  transition={{ duration: 0.8, delay: idx * 0.05 }}
                  className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary-500 to-primary-600 flex items-center justify-end pr-3"
                >
                  <span className="text-white font-bold text-sm">{agent.total_issues_found}</span>
                </motion.div>
              </div>
              <div className="flex space-x-2">
                {agent.critical_issues > 0 && (
                  <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-bold rounded">
                    {agent.critical_issues} C
                  </span>
                )}
                {agent.high_issues > 0 && (
                  <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs font-bold rounded">
                    {agent.high_issues} H
                  </span>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Detailed Stats Table */}
      <div>
        <h3 className="text-lg font-bold text-gray-900 mb-4">Detailed Stats</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b-2 border-gray-200">
              <tr>
                <th className="px-4 py-2 text-left font-semibold text-gray-700">Agent</th>
                <th className="px-4 py-2 text-center font-semibold text-gray-700">Reviews</th>
                <th className="px-4 py-2 text-center font-semibold text-gray-700">Issues</th>
                <th className="px-4 py-2 text-center font-semibold text-gray-700">Critical</th>
                <th className="px-4 py-2 text-center font-semibold text-gray-700">High</th>
                <th className="px-4 py-2 text-center font-semibold text-gray-700">Avg/Review</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {topAgents.map((agent, idx) => (
                <motion.tr
                  key={agent.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="hover:bg-gray-50"
                >
                  <td className="px-4 py-3 font-medium text-gray-900">{agent.name}</td>
                  <td className="px-4 py-3 text-center text-gray-700">{agent.total_reviews}</td>
                  <td className="px-4 py-3 text-center">
                    <span className="px-2 py-1 bg-primary-100 text-primary-800 rounded-full font-semibold">
                      {agent.total_issues_found}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full font-semibold">
                      {agent.critical_issues}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded-full font-semibold">
                      {agent.high_issues}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center text-gray-700 font-semibold">
                    {agent.avg_issues_per_review}
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}
