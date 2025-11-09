'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { TrendsChart } from '../../components/TrendsChart';
import { AgentPerformance } from '../../components/AgentPerformance';

interface Review {
  id: string;
  title: string;
  type: string;
  category: string;
  date: string;
  score: number;
  total_issues: number;
  total_changes: number;
  total_agents: number;
}

export default function HistoryPage() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  useEffect(() => {
    fetchHistory();
  }, [days]);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/analytics/history?days=${days}&limit=100`);
      const data = await response.json();
      setReviews(data.reviews || []);
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredReviews = reviews.filter(review => {
    const matchesSearch = review.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         review.type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || review.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = ['all', ...Array.from(new Set(reviews.map(r => r.category)))];

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <Link href="/" className="text-primary-600 hover:text-primary-700 text-sm mb-2 inline-block">
              ← Back to Review
            </Link>
            <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              📊 Analytics Dashboard
            </h1>
            <p className="text-gray-600 mt-2">
              Review history, trends, and performance insights
            </p>
          </div>
        </motion.div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-primary-500"
          >
            <div className="text-3xl mb-2">📄</div>
            <div className="text-3xl font-bold text-gray-900">{reviews.length}</div>
            <div className="text-sm text-gray-600 mt-1">Total Reviews</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500"
          >
            <div className="text-3xl mb-2">⭐</div>
            <div className="text-3xl font-bold text-gray-900">
              {reviews.length > 0 ? Math.round(reviews.reduce((a, b) => a + b.score, 0) / reviews.length) : 0}
            </div>
            <div className="text-sm text-gray-600 mt-1">Avg Score</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-yellow-500"
          >
            <div className="text-3xl mb-2">🔍</div>
            <div className="text-3xl font-bold text-gray-900">
              {reviews.reduce((a, b) => a + b.total_issues, 0)}
            </div>
            <div className="text-sm text-gray-600 mt-1">Total Issues Found</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500"
          >
            <div className="text-3xl mb-2">✏️</div>
            <div className="text-3xl font-bold text-gray-900">
              {reviews.reduce((a, b) => a + b.total_changes, 0)}
            </div>
            <div className="text-sm text-gray-600 mt-1">Total Changes Proposed</div>
          </motion.div>
        </div>

        {/* Trends Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <TrendsChart days={days} />
        </motion.div>

        {/* Agent Performance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <AgentPerformance days={days} />
        </motion.div>

        {/* History Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          {/* Controls */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Review History</h2>
            <div className="flex space-x-4">
              <select
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
              </select>
            </div>
          </div>

          {/* Search & Filter */}
          <div className="flex space-x-4 mb-6">
            <input
              type="text"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>
                  {cat === 'all' ? 'All Categories' : cat.charAt(0).toUpperCase() + cat.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Table */}
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p className="text-gray-600 mt-4">Loading history...</p>
            </div>
          ) : filteredReviews.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg">No reviews found</p>
              <p className="text-sm mt-2">Try adjusting your filters or create a new review</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b-2 border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Document</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Category</th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase">Score</th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase">Issues</th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase">Changes</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Date</th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-700 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredReviews.map((review, idx) => (
                    <motion.tr
                      key={review.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-4 py-4">
                        <div className="font-medium text-gray-900">{review.title}</div>
                        <div className="text-sm text-gray-500">{review.type}</div>
                      </td>
                      <td className="px-4 py-4">
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                          {review.category}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-center">
                        <span className={`px-3 py-1 rounded-full text-sm font-bold ${getScoreColor(review.score)}`}>
                          {review.score}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-center font-semibold text-gray-700">
                        {review.total_issues}
                      </td>
                      <td className="px-4 py-4 text-center font-semibold text-gray-700">
                        {review.total_changes}
                      </td>
                      <td className="px-4 py-4 text-sm text-gray-600">
                        {new Date(review.date).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-4 text-center">
                        <button
                          onClick={() => window.location.href = `/?review=${review.id}`}
                          className="px-3 py-1 bg-primary-600 hover:bg-primary-700 text-white text-sm rounded-lg transition-colors"
                        >
                          View
                        </button>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}

