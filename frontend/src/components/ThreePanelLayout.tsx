'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { IssuesList } from './IssuesList';
import { DocumentViewer } from './DocumentViewer';
import { EvidencePanel } from './EvidencePanel';

export interface Issue {
  agent: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  confidence: number;
  title: string;
  category: string;
  description: string;
  location: string;
  evidence: string;
  suggestion: string;
}

interface ThreePanelLayoutProps {
  issues: Issue[];
  documentText: string;
  documentTitle: string;
}

export function ThreePanelLayout({ issues, documentText, documentTitle }: ThreePanelLayoutProps) {
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);
  const [hoveredIssue, setHoveredIssue] = useState<Issue | null>(null);
  const [acceptedIssues, setAcceptedIssues] = useState<Set<string>>(new Set());
  const [isAcceptingAll, setIsAcceptingAll] = useState(false);

  const handleIssueClick = (issue: Issue) => {
    setSelectedIssue(issue);
  };

  const handleIssueHover = (issue: Issue | null) => {
    setHoveredIssue(issue);
  };

  const handleAcceptSuggestion = (issue: Issue) => {
    const issueId = `${issue.agent}-${issue.title}`;
    setAcceptedIssues(prev => new Set([...prev, issueId]));
  };

  const handleAcceptAll = () => {
    setIsAcceptingAll(true);
    
    // Simulate accepting all issues with animation
    const issuesWithSuggestions = issues.filter(issue => issue.suggestion);
    let delay = 0;
    
    issuesWithSuggestions.forEach((issue, index) => {
      setTimeout(() => {
        const issueId = `${issue.agent}-${issue.title}`;
        setAcceptedIssues(prev => new Set([...prev, issueId]));
        
        // Complete animation after last issue
        if (index === issuesWithSuggestions.length - 1) {
          setTimeout(() => setIsAcceptingAll(false), 300);
        }
      }, delay);
      delay += 50; // 50ms between each acceptance
    });
  };

  const issuesWithSuggestions = issues.filter(issue => issue.suggestion);
  const acceptedCount = acceptedIssues.size;
  const totalCount = issuesWithSuggestions.length;

  return (
    <div className="w-full h-[800px] bg-white rounded-2xl shadow-2xl overflow-hidden border border-gray-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold flex items-center space-x-3">
              <span className="text-3xl">🔍</span>
              <span>Evidence-First Analysis</span>
            </h2>
            <p className="text-primary-100 mt-2">
              Interactive issue explorer with real-time document highlighting
            </p>
          </div>
          
          {/* Accept All Button */}
          {totalCount > 0 && (
            <motion.button
              onClick={handleAcceptAll}
              disabled={isAcceptingAll || acceptedCount === totalCount}
              whileHover={{ scale: isAcceptingAll || acceptedCount === totalCount ? 1 : 1.05 }}
              whileTap={{ scale: isAcceptingAll || acceptedCount === totalCount ? 1 : 0.95 }}
              className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center space-x-2 shadow-lg ${
                acceptedCount === totalCount
                  ? 'bg-green-500 text-white cursor-not-allowed'
                  : isAcceptingAll
                  ? 'bg-white/20 text-white cursor-wait'
                  : 'bg-white text-primary-600 hover:bg-primary-50'
              }`}
            >
              {acceptedCount === totalCount ? (
                <>
                  <span>✅</span>
                  <span>All Accepted!</span>
                </>
              ) : isAcceptingAll ? (
                <>
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Accepting...</span>
                </>
              ) : (
                <>
                  <span>✨</span>
                  <span>Accept All ({acceptedCount}/{totalCount})</span>
                </>
              )}
            </motion.button>
          )}
        </div>
      </div>

      {/* 3-Panel Layout */}
      <div className="flex h-[calc(100%-88px)]">
        {/* Panel A: Issues List (Left - 30%) */}
        <div className="w-[30%] border-r border-gray-200 overflow-y-auto">
          <IssuesList
            issues={issues}
            selectedIssue={selectedIssue}
            onIssueClick={handleIssueClick}
            onIssueHover={handleIssueHover}
            acceptedIssues={acceptedIssues}
          />
        </div>

        {/* Panel B: Document with Highlights (Center - 45%) */}
        <div className="w-[45%] border-r border-gray-200">
          <DocumentViewer
            documentText={documentText}
            documentTitle={documentTitle}
            selectedIssue={selectedIssue}
            hoveredIssue={hoveredIssue}
          />
        </div>

        {/* Panel C: Evidence Details (Right - 25%) */}
        <div className="w-[25%]">
          <EvidencePanel 
            selectedIssue={selectedIssue}
            acceptedIssues={acceptedIssues}
            onAcceptSuggestion={handleAcceptSuggestion}
          />
        </div>
      </div>
    </div>
  );
}

