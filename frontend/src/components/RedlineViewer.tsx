'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { useReviewStore } from '../store/reviewStore';

export interface ProposedChange {
  id: string;
  agent: string;
  issue_title: string;
  type: 'delete' | 'insert' | 'replace';
  location: string;
  old_text: string;
  new_text: string;
  reason: string;
  status: 'pending' | 'accepted' | 'rejected';
}

interface RedlineViewerProps {
  changes: ProposedChange[];
  onAccept: (changeId: string) => void;
  onReject: (changeId: string) => void;
  onAcceptAll: () => void;
  onRejectAll: () => void;
  onApplyChanges?: () => void;
}

export function RedlineViewer({ changes, onAccept, onReject, onAcceptAll, onRejectAll, onApplyChanges }: RedlineViewerProps) {
  const [filter, setFilter] = useState<'all' | 'pending' | 'accepted' | 'rejected'>('all');
  const [selectedChange, setSelectedChange] = useState<ProposedChange | null>(null);
  const [isApplying, setIsApplying] = useState(false);

  const filteredChanges = changes.filter(c => {
    if (filter === 'all') return true;
    return c.status === filter;
  });

  const statusCounts = {
    pending: changes.filter(c => c.status === 'pending').length,
    accepted: changes.filter(c => c.status === 'accepted').length,
    rejected: changes.filter(c => c.status === 'rejected').length,
  };

  if (changes.length === 0) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-8 text-center">
        <div className="text-6xl mb-4">📝</div>
        <h3 className="text-xl font-bold text-blue-900 mb-2">
          No Specific Text Changes Proposed
        </h3>
        <p className="text-blue-700">
          The agents provided suggestions in the issues list, but did not propose specific text replacements.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Controls */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center space-x-3">
              <span className="text-3xl">✏️</span>
              <span>Proposed Text Changes</span>
            </h2>
            <p className="text-gray-600 mt-1">
              Review and accept/reject changes suggested by AI agents
            </p>
          </div>
          
          <div className="flex space-x-2">
            {statusCounts.pending > 0 && (
              <>
                <button
                  onClick={onAcceptAll}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors flex items-center space-x-2"
                >
                  <span>✓</span>
                  <span>Accept All ({statusCounts.pending})</span>
                </button>
                <button
                  onClick={onRejectAll}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors flex items-center space-x-2"
                >
                  <span>✗</span>
                  <span>Reject All</span>
                </button>
              </>
            )}
            
            {statusCounts.accepted > 0 && onApplyChanges && (
              <button
                onClick={async () => {
                  setIsApplying(true);
                  try {
                    await onApplyChanges();
                  } finally {
                    setIsApplying(false);
                  }
                }}
                disabled={isApplying}
                className="px-6 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white font-bold rounded-lg transition-colors flex items-center space-x-2 shadow-lg"
              >
                <span>📝</span>
                <span>{isApplying ? 'Generating...' : `Generate Revised Document (${statusCounts.accepted} changes)`}</span>
              </button>
            )}
          </div>
        </div>

        {/* Status Pills */}
        <div className="flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              filter === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            All ({changes.length})
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              filter === 'pending'
                ? 'bg-yellow-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Pending ({statusCounts.pending})
          </button>
          <button
            onClick={() => setFilter('accepted')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              filter === 'accepted'
                ? 'bg-green-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Accepted ({statusCounts.accepted})
          </button>
          <button
            onClick={() => setFilter('rejected')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              filter === 'rejected'
                ? 'bg-red-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Rejected ({statusCounts.rejected})
          </button>
        </div>
      </div>

      {/* Changes List */}
      <div className="space-y-4">
        <AnimatePresence>
          {filteredChanges.map((change, idx) => (
            <ChangeCard
              key={change.id}
              change={change}
              index={idx}
              isSelected={selectedChange?.id === change.id}
              onSelect={() => setSelectedChange(change)}
              onAccept={() => onAccept(change.id)}
              onReject={() => onReject(change.id)}
            />
          ))}
        </AnimatePresence>
      </div>

      {filteredChanges.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">No changes in this category</p>
        </div>
      )}
    </div>
  );
}

interface ChangeCardProps {
  change: ProposedChange;
  index: number;
  isSelected: boolean;
  onSelect: () => void;
  onAccept: () => void;
  onReject: () => void;
}

function ChangeCard({ change, index, isSelected, onSelect, onAccept, onReject }: ChangeCardProps) {
  const typeColors = {
    delete: 'bg-red-100 text-red-800',
    insert: 'bg-green-100 text-green-800',
    replace: 'bg-blue-100 text-blue-800',
  };

  const statusColors = {
    pending: 'border-yellow-300 bg-yellow-50',
    accepted: 'border-green-300 bg-green-50',
    rejected: 'border-red-300 bg-red-50',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ delay: index * 0.05 }}
      className={`bg-white rounded-xl shadow-lg border-2 p-6 transition-all hover:shadow-xl ${statusColors[change.status]} ${
        isSelected ? 'ring-4 ring-primary-300' : ''
      }`}
      onClick={onSelect}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${typeColors[change.type]}`}>
              {change.type.toUpperCase()}
            </span>
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${
              change.status === 'pending' ? 'bg-yellow-500 text-white' :
              change.status === 'accepted' ? 'bg-green-500 text-white' :
              'bg-red-500 text-white'
            }`}>
              {change.status.toUpperCase()}
            </span>
          </div>
          <h3 className="text-lg font-bold text-gray-900">{change.issue_title}</h3>
          <p className="text-sm text-gray-600 mt-1">
            📍 {change.location} • by {formatAgentName(change.agent)}
          </p>
        </div>
      </div>

      {/* Redline Display */}
      <div className="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-200">
        {change.type === 'delete' && (
          <div className="space-y-2">
            <div className="text-xs text-gray-500 font-semibold">DELETE:</div>
            <div className="text-red-600 line-through bg-red-50 p-2 rounded">
              {change.old_text}
            </div>
          </div>
        )}

        {change.type === 'insert' && (
          <div className="space-y-2">
            <div className="text-xs text-gray-500 font-semibold">INSERT:</div>
            <div className="text-green-600 bg-green-50 p-2 rounded border-l-4 border-green-500">
              {change.new_text}
            </div>
          </div>
        )}

        {change.type === 'replace' && (
          <div className="space-y-3">
            <div>
              <div className="text-xs text-gray-500 font-semibold mb-1">REMOVE:</div>
              <div className="text-red-600 line-through bg-red-50 p-2 rounded">
                {change.old_text}
              </div>
            </div>
            <div className="flex items-center justify-center">
              <span className="text-2xl">⬇️</span>
            </div>
            <div>
              <div className="text-xs text-gray-500 font-semibold mb-1">REPLACE WITH:</div>
              <div className="text-green-600 bg-green-50 p-2 rounded border-l-4 border-green-500">
                {change.new_text}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Reason */}
      <div className="bg-blue-50 rounded-lg p-3 mb-4 border border-blue-200">
        <div className="text-xs text-blue-800 font-semibold mb-1">REASON:</div>
        <p className="text-sm text-blue-900">{change.reason}</p>
      </div>

      {/* Action Buttons */}
      {change.status === 'pending' && (
        <div className="flex space-x-2">
          <button
            onClick={(e) => { e.stopPropagation(); onAccept(); }}
            className="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            <span>✓</span>
            <span>Accept</span>
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); onReject(); }}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
          >
            <span>✗</span>
            <span>Reject</span>
          </button>
        </div>
      )}

      {change.status !== 'pending' && (
        <div className={`text-center py-2 rounded-lg font-semibold ${
          change.status === 'accepted' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {change.status === 'accepted' ? '✓ Accepted' : '✗ Rejected'}
        </div>
      )}
    </motion.div>
  );
}

function formatAgentName(name: string): string {
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

