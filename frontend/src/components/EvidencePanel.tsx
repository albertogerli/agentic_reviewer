'use client';

import { motion, AnimatePresence } from 'framer-motion';
import type { Issue } from './ThreePanelLayout';

interface EvidencePanelProps {
  selectedIssue: Issue | null;
  acceptedIssues: Set<string>;
  onAcceptSuggestion: (issue: Issue) => void;
}

export function EvidencePanel({ selectedIssue, acceptedIssues, onAcceptSuggestion }: EvidencePanelProps) {
  const issueId = selectedIssue ? `${selectedIssue.agent}-${selectedIssue.title}` : '';
  const isAccepted = acceptedIssues.has(issueId);
  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="p-4 bg-primary-600 text-white">
        <h3 className="font-bold flex items-center space-x-2">
          <span>🔎</span>
          <span>Evidence</span>
        </h3>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        <AnimatePresence mode="wait">
          {selectedIssue ? (
            <motion.div
              key={selectedIssue.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              {/* Severity Badge */}
              <div className="flex items-center justify-between">
                <span className={`px-3 py-1 rounded-full text-sm font-bold ${getSeverityBadge(selectedIssue.severity)}`}>
                  {selectedIssue.severity.toUpperCase()}
                </span>
                <div className="text-right">
                  <div className="text-xs text-gray-500">Confidence</div>
                  <div className="text-lg font-bold text-gray-900">
                    {selectedIssue.confidence}%
                  </div>
                </div>
              </div>

              {/* Agent */}
              <div className="bg-white rounded-lg p-3 border border-gray-200">
                <div className="text-xs text-gray-500 mb-1">Identified by</div>
                <div className="font-semibold text-gray-900">
                  {formatAgentName(selectedIssue.agent)}
                </div>
              </div>

              {/* Location */}
              {selectedIssue.location && (
                <div className="bg-white rounded-lg p-3 border border-gray-200">
                  <div className="text-xs text-gray-500 mb-1">📍 Location</div>
                  <div className="text-sm text-gray-800">
                    {selectedIssue.location}
                  </div>
                </div>
              )}

              {/* Evidence */}
              {selectedIssue.evidence && (
                <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-200">
                  <div className="text-xs text-yellow-800 font-semibold mb-2">
                    🔍 Evidence
                  </div>
                  <div className="text-sm text-yellow-900 italic leading-relaxed">
                    "{selectedIssue.evidence}"
                  </div>
                </div>
              )}

              {/* Description */}
              <div className="bg-white rounded-lg p-3 border border-gray-200">
                <div className="text-xs text-gray-500 mb-2">Description</div>
                <div className="text-sm text-gray-800 leading-relaxed">
                  {selectedIssue.description}
                </div>
              </div>

              {/* Suggestion */}
              {selectedIssue.suggestion && (
                <div className="bg-green-50 rounded-lg p-3 border border-green-200">
                  <div className="text-xs text-green-800 font-semibold mb-2">
                    ✅ Suggested Fix
                  </div>
                  <div className="text-sm text-green-900 leading-relaxed">
                    {selectedIssue.suggestion}
                  </div>
                </div>
              )}

              {/* Action Button */}
              {selectedIssue.suggestion && (
                <motion.button
                  onClick={() => onAcceptSuggestion(selectedIssue)}
                  disabled={isAccepted}
                  whileHover={{ scale: isAccepted ? 1 : 1.02 }}
                  whileTap={{ scale: isAccepted ? 1 : 0.98 }}
                  className={`w-full font-medium py-3 px-4 rounded-lg transition-all flex items-center justify-center space-x-2 ${
                    isAccepted
                      ? 'bg-green-500 text-white cursor-not-allowed'
                      : 'bg-primary-600 hover:bg-primary-700 text-white'
                  }`}
                >
                  {isAccepted ? (
                    <>
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span>Suggestion Accepted!</span>
                    </>
                  ) : (
                    <>
                      <span>✨</span>
                      <span>Accept Suggestion</span>
                    </>
                  )}
                </motion.button>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center h-full text-center p-4"
            >
              <div className="text-6xl mb-4">📋</div>
              <h4 className="font-bold text-gray-700 mb-2">No Issue Selected</h4>
              <p className="text-sm text-gray-500 leading-relaxed">
                Click on an issue from the list to view detailed evidence and suggestions
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

function getSeverityBadge(severity: string): string {
  switch (severity) {
    case 'critical':
      return 'bg-red-600 text-white';
    case 'high':
      return 'bg-orange-500 text-white';
    case 'medium':
      return 'bg-yellow-500 text-white';
    case 'low':
      return 'bg-blue-500 text-white';
    default:
      return 'bg-gray-500 text-white';
  }
}

function formatAgentName(name: string): string {
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

