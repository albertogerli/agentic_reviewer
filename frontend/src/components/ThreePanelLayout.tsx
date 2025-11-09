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

  const handleIssueClick = (issue: Issue) => {
    setSelectedIssue(issue);
  };

  const handleIssueHover = (issue: Issue | null) => {
    setHoveredIssue(issue);
  };

  return (
    <div className="w-full h-[800px] bg-white rounded-2xl shadow-2xl overflow-hidden border border-gray-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-6">
        <h2 className="text-2xl font-bold flex items-center space-x-3">
          <span className="text-3xl">🔍</span>
          <span>Evidence-First Analysis</span>
        </h2>
        <p className="text-primary-100 mt-2">
          Interactive issue explorer with real-time document highlighting
        </p>
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
          <EvidencePanel selectedIssue={selectedIssue} />
        </div>
      </div>
    </div>
  );
}

