'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useMemo } from 'react';
import type { Issue } from './ThreePanelLayout';

interface IssuesListProps {
  issues: Issue[];
  selectedIssue: Issue | null;
  onIssueClick: (issue: Issue) => void;
  onIssueHover: (issue: Issue | null) => void;
  acceptedIssues: Set<string>;
}

export function IssuesList({ issues, selectedIssue, onIssueClick, onIssueHover, acceptedIssues }: IssuesListProps) {
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'severity' | 'confidence'>('severity');

  // Extract unique categories
  const categories = useMemo(() => {
    return ['all', ...Array.from(new Set(issues.map(i => i.category)))];
  }, [issues]);

  // Filter and sort issues
  const filteredIssues = useMemo(() => {
    let filtered = issues;

    if (severityFilter !== 'all') {
      filtered = filtered.filter(i => i.severity === severityFilter);
    }

    if (categoryFilter !== 'all') {
      filtered = filtered.filter(i => i.category === categoryFilter);
    }

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === 'severity') {
        const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
        return severityOrder[b.severity] - severityOrder[a.severity];
      } else {
        return b.confidence - a.confidence;
      }
    });

    return filtered;
  }, [issues, severityFilter, categoryFilter, sortBy]);

  return (
    <div className="h-full flex flex-col">
      {/* Filters Header */}
      <div className="p-4 bg-gray-50 border-b border-gray-200 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-gray-900">
            Issues ({filteredIssues.length})
          </h3>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'severity' | 'confidence')}
            className="text-xs border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="severity">By Severity</option>
            <option value="confidence">By Confidence</option>
          </select>
        </div>

        {/* Severity Filter */}
        <div className="flex gap-2 flex-wrap">
          {['all', 'critical', 'high', 'medium', 'low'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                severityFilter === sev
                  ? getSeverityColors(sev).bg + ' ' + getSeverityColors(sev).text
                  : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
              }`}
            >
              {sev.charAt(0).toUpperCase() + sev.slice(1)}
            </button>
          ))}
        </div>

        {/* Category Filter */}
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat === 'all' ? 'All Categories' : cat.charAt(0).toUpperCase() + cat.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Issues List */}
      <div className="flex-1 overflow-y-auto">
        <AnimatePresence>
          {filteredIssues.map((issue, idx) => {
            const issueId = `${issue.agent}-${issue.title}`;
            const isAccepted = acceptedIssues.has(issueId);
            return (
              <IssueCard
                key={idx}
                issue={issue}
                isSelected={selectedIssue === issue}
                isAccepted={isAccepted}
                onClick={() => onIssueClick(issue)}
                onMouseEnter={() => onIssueHover(issue)}
                onMouseLeave={() => onIssueHover(null)}
              />
            );
          })}
        </AnimatePresence>

        {filteredIssues.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            <p className="text-lg">🎉 No issues found!</p>
            <p className="text-sm mt-2">Try adjusting your filters</p>
          </div>
        )}
      </div>
    </div>
  );
}

interface IssueCardProps {
  issue: Issue;
  isSelected: boolean;
  isAccepted: boolean;
  onClick: () => void;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
}

function IssueCard({ issue, isSelected, isAccepted, onClick, onMouseEnter, onMouseLeave }: IssueCardProps) {
  const colors = getSeverityColors(issue.severity);

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className={`p-4 border-b border-gray-200 cursor-pointer transition-all relative ${
        isAccepted
          ? 'bg-green-50 border-l-4 border-l-green-500 opacity-75'
          : isSelected 
          ? 'bg-primary-50 border-l-4 border-l-primary-500' 
          : 'hover:bg-gray-50 border-l-4 border-l-transparent'
      }`}
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {/* Accepted Badge */}
      {isAccepted && (
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          className="absolute top-2 right-2 bg-green-500 text-white rounded-full p-1"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        </motion.div>
      )}
      
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className={`px-2 py-0.5 rounded text-xs font-bold ${colors.bg} ${colors.text}`}>
              {issue.severity.toUpperCase()}
            </span>
            <span className="text-xs text-gray-500">
              {issue.confidence}% confidence
            </span>
            {isAccepted && (
              <span className="text-xs text-green-700 font-semibold">
                ✓ Accepted
              </span>
            )}
          </div>
          <h4 className="font-semibold text-gray-900 text-sm leading-tight">
            {issue.title}
          </h4>
        </div>
      </div>

      {/* Category & Agent */}
      <div className="flex items-center gap-2 text-xs text-gray-600 mb-2">
        <span className="px-2 py-0.5 bg-gray-100 rounded">
          {issue.category}
        </span>
        <span>•</span>
        <span className="italic">{formatAgentName(issue.agent)}</span>
      </div>

      {/* Description Preview */}
      <p className="text-sm text-gray-700 line-clamp-2">
        {issue.description}
      </p>

      {/* Confidence Bar */}
      <div className="mt-2 h-1 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${colors.bg}`}
          style={{ width: `${issue.confidence}%` }}
        />
      </div>
    </motion.div>
  );
}

function getSeverityColors(severity: string) {
  switch (severity) {
    case 'critical':
      return { bg: 'bg-red-600', text: 'text-white' };
    case 'high':
      return { bg: 'bg-orange-500', text: 'text-white' };
    case 'medium':
      return { bg: 'bg-yellow-500', text: 'text-white' };
    case 'low':
      return { bg: 'bg-blue-500', text: 'text-white' };
    default:
      return { bg: 'bg-gray-500', text: 'text-white' };
  }
}

function formatAgentName(name: string): string {
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

