'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import React from 'react';
import { useReviewStore } from '../store/reviewStore';
import { DocumentArrowDownIcon, ChartBarIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { ThreePanelLayout } from './ThreePanelLayout';
import { RiskHeatmap } from './RiskHeatmap';
import { RedlineViewer, type ProposedChange } from './RedlineViewer';

export function ReviewResults() {
  const { results, reviewId, isProcessing } = useReviewStore();
  const [activeTab, setActiveTab] = useState<'summary' | 'agents' | 'evidence' | 'redline' | 'raw'>('summary');
  const [changes, setChanges] = useState<ProposedChange[]>([]);
  
  // Initialize changes from results
  React.useEffect(() => {
    if (results && results.proposed_changes) {
      setChanges(results.proposed_changes);
    }
  }, [results]);

  // Handle accept/reject changes
  const handleAcceptChange = (changeId: string) => {
    setChanges(changes.map(c => 
      c.id === changeId ? { ...c, status: 'accepted' as const } : c
    ));
  };

  const handleRejectChange = (changeId: string) => {
    setChanges(changes.map(c => 
      c.id === changeId ? { ...c, status: 'rejected' as const } : c
    ));
  };

  const handleAcceptAll = () => {
    setChanges(changes.map(c => 
      c.status === 'pending' ? { ...c, status: 'accepted' as const } : c
    ));
  };

  const handleRejectAll = () => {
    setChanges(changes.map(c => 
      c.status === 'pending' ? { ...c, status: 'rejected' as const } : c
    ));
  };

  const handleApplyChanges = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/review/${reviewId}/apply-changes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(changes),
      });

      if (!response.ok) {
        throw new Error('Failed to apply changes');
      }

      const result = await response.json();
      console.log('✅ Changes applied:', result);
      
      // Show success message
      alert(`✅ Revised document generated successfully!\n\n${result.summary.accepted} changes applied.\n\nYou can download it from the files section.`);
    } catch (error) {
      console.error('Error applying changes:', error);
      alert('❌ Error applying changes. Please try again.');
    }
  };
  
  if (!results || isProcessing) {
    return null;
  }
  
  console.log('📊 Results:', results); // Debug
  
  const handleDownload = (fileType: string) => {
    window.open(`http://localhost:8000/api/review/${reviewId}/download/${fileType}`, '_blank');
  };
  
  // Extract data from generic_reviewer format
  const agentReviews = results.agent_reviews || {};
  const agentCount = Object.keys(agentReviews).length;
  const docType = results.document_info?.type || results.document_type || {};
  const docTitle = results.document_info?.title || results.document_title || 'Document';
  
  // Count issues and suggestions
  let issuesCount = 0;
  let suggestionsCount = 0;
  Object.values(agentReviews).forEach((review: any) => {
    const text = typeof review === 'string' ? review : (review.review || '');
    issuesCount += (text.match(/❌|issue|problem|error|concern/gi) || []).length;
    suggestionsCount += (text.match(/✅|suggest|recommend|improve|should/gi) || []).length;
  });
  
  // Calculate smart score if not provided
  let overallScore: string | number = results.overall_score || results.score || 'N/A';
  if (overallScore === 'N/A' && agentCount > 0) {
    // Simple heuristic: more suggestions than issues = better score
    const ratio = suggestionsCount / Math.max(issuesCount, 1);
    if (ratio > 2) overallScore = 85;
    else if (ratio > 1) overallScore = 75;
    else if (ratio > 0.5) overallScore = 65;
    else overallScore = 55;
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-6xl mx-auto mt-8 space-y-6"
    >
      {/* Success Banner */}
      <motion.div
        initial={{ scale: 0.9 }}
        animate={{ scale: 1 }}
        className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl shadow-2xl p-8 text-white"
      >
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
            <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div>
            <h2 className="text-3xl font-bold">Review Complete!</h2>
            <p className="text-white/90 mt-1">
              Your document has been analyzed by {agentCount} AI agents
            </p>
          </div>
        </div>
      </motion.div>
      
      {/* Download Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <DownloadCard
          title="Markdown Report"
          description="Detailed review in markdown format"
          icon={<DocumentTextIcon className="w-8 h-8" />}
          color="blue"
          onClick={() => handleDownload('md')}
        />
        <DownloadCard
          title="JSON Results"
          description="Structured data for further processing"
          icon={<DocumentArrowDownIcon className="w-8 h-8" />}
          color="purple"
          onClick={() => handleDownload('json')}
        />
        <DownloadCard
          title="Interactive Dashboard"
          description="Visual analytics and charts"
          icon={<ChartBarIcon className="w-8 h-8" />}
          color="green"
          onClick={() => handleDownload('html')}
        />
      </div>
      
      {/* Results Tabs */}
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-8" aria-label="Tabs">
            <button 
              onClick={() => setActiveTab('summary')}
              className={`border-b-2 py-4 px-1 text-sm font-medium transition-colors ${
                activeTab === 'summary' 
                  ? 'border-primary-500 text-primary-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Summary
            </button>
            <button 
              onClick={() => setActiveTab('agents')}
              className={`border-b-2 py-4 px-1 text-sm font-medium transition-colors ${
                activeTab === 'agents' 
                  ? 'border-primary-500 text-primary-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Agent Reports
            </button>
            <button 
              onClick={() => setActiveTab('evidence')}
              className={`border-b-2 py-4 px-1 text-sm font-medium transition-colors ${
                activeTab === 'evidence' 
                  ? 'border-primary-500 text-primary-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              🔍 Evidence Explorer
            </button>
            <button 
              onClick={() => setActiveTab('redline')}
              className={`border-b-2 py-4 px-1 text-sm font-medium transition-colors ${
                activeTab === 'redline' 
                  ? 'border-primary-500 text-primary-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              ✏️ Redline Editor
            </button>
            <button 
              onClick={() => setActiveTab('raw')}
              className={`border-b-2 py-4 px-1 text-sm font-medium transition-colors ${
                activeTab === 'raw' 
                  ? 'border-primary-500 text-primary-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Raw Data
            </button>
          </nav>
        </div>
        
        <div className="p-8">
          {/* Summary Tab */}
          {activeTab === 'summary' && (
          <div className="space-y-6">
            {/* Document Info */}
            <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
              <h4 className="font-bold text-primary-900 text-lg">{docTitle}</h4>
              {docType.type && (
                <p className="text-sm text-primary-700 mt-1">
                  Type: {docType.type}
                  {docType.category && ` · Category: ${docType.category}`}
                </p>
              )}
              {docType.detected_language && (
                <p className="text-sm text-primary-600 mt-1">
                  Language: {docType.detected_language}
                </p>
              )}
            </div>
            
            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6 border-t border-gray-200">
              <StatCard label="Agents Used" value={agentCount} color="blue" />
              <StatCard label="Issues Found" value={issuesCount} color="red" />
              <StatCard label="Suggestions" value={suggestionsCount} color="green" />
              <StatCard label="Overall Score" value={overallScore} color="purple" />
            </div>
            
            {/* Agent Reviews Preview */}
            {agentCount > 0 && (
              <div className="mt-8">
                <h4 className="font-bold text-gray-900 text-lg mb-4">Agent Insights (Top 5)</h4>
                <div className="space-y-3">
                  {Object.entries(agentReviews).slice(0, 5).map(([name, review]: [string, any]) => {
                    const reviewText = typeof review === 'string' ? review : (review.review || review.content || 'Review completed');
                    const icon = getAgentIcon(name);
                    return (
                      <div key={name} className="p-4 bg-gray-50 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                        <div className="flex items-center space-x-3 mb-2">
                          <span className="text-2xl">{icon}</span>
                          <span className="font-semibold text-gray-900">
                            {formatAgentName(name)}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 leading-relaxed">
                          {reviewText.length > 300 ? reviewText.substring(0, 300) + '...' : reviewText}
                        </p>
                      </div>
                    );
                  })}
                </div>
                {agentCount > 5 && (
                  <p className="text-center text-sm text-gray-500 mt-4">
                    + {agentCount - 5} more agents... Download full report for details
                  </p>
                )}
              </div>
            )}
            
            {/* Summary Text */}
            {results.summary && (
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h5 className="font-semibold text-blue-900 mb-2">Executive Summary</h5>
                <p className="text-blue-800 leading-relaxed">{results.summary}</p>
              </div>
            )}
          </div>
          )}
          
          {/* Agent Reports Tab */}
          {activeTab === 'agents' && (
            <div className="space-y-4">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Detailed Agent Reports</h3>
              {Object.entries(agentReviews).map(([name, review]: [string, any]) => {
                const reviewText = typeof review === 'string' ? review : (review.review || review.content || 'Review completed');
                const icon = getAgentIcon(name);
                return (
                  <motion.div
                    key={name}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-6 bg-gradient-to-r from-gray-50 to-white border-l-4 border-primary-500 rounded-lg shadow-sm hover:shadow-md transition-all"
                  >
                    <div className="flex items-center space-x-3 mb-4">
                      <span className="text-3xl">{icon}</span>
                      <h4 className="text-xl font-bold text-gray-900">
                        {formatAgentName(name)}
                      </h4>
                    </div>
                    <div className="prose prose-sm max-w-none text-gray-700">
                      <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed bg-white p-4 rounded border border-gray-200">
                        {reviewText}
                      </pre>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
          
          {/* Evidence Explorer Tab */}
          {activeTab === 'evidence' && (
            <div className="space-y-6">
              {/* Risk Heatmap */}
              {results.risk_heatmap && Object.keys(results.risk_heatmap).length > 0 && (
                <RiskHeatmap riskData={results.risk_heatmap} />
              )}
              
              {/* 3-Panel Layout */}
              {results.structured_issues && results.structured_issues.length > 0 ? (
                <ThreePanelLayout
                  issues={results.structured_issues}
                  documentText={results.document_text || "Document text not available"}
                  documentTitle={docTitle}
                />
              ) : (
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-8 text-center">
                  <div className="text-6xl mb-4">🎉</div>
                  <h3 className="text-xl font-bold text-blue-900 mb-2">
                    No Structured Issues Found
                  </h3>
                  <p className="text-blue-700">
                    The agents did not identify any issues using the structured format. 
                    Check the "Agent Reports" tab for detailed feedback.
                  </p>
                </div>
              )}
            </div>
          )}
          
          {/* Redline Editor Tab */}
          {activeTab === 'redline' && (
            <RedlineViewer
              changes={changes}
              onAccept={handleAcceptChange}
              onReject={handleRejectChange}
              onAcceptAll={handleAcceptAll}
              onRejectAll={handleRejectAll}
              onApplyChanges={handleApplyChanges}
            />
          )}
          
          {/* Raw Data Tab */}
          {activeTab === 'raw' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-bold text-gray-900">Raw JSON Data</h3>
                <button
                  onClick={() => navigator.clipboard.writeText(JSON.stringify(results, null, 2))}
                  className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm font-medium"
                >
                  📋 Copy to Clipboard
                </button>
              </div>
              <div className="bg-gray-900 rounded-lg p-6 overflow-auto max-h-[600px]">
                <pre className="text-green-400 text-sm font-mono">
                  {JSON.stringify(results, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// Helper functions
function getAgentIcon(agentName: string): string {
  const iconMap: Record<string, string> = {
    'style_editor': '✍️',
    'fact_checker': '🔍',
    'logic_checker': '🧠',
    'technical_expert': '⚙️',
    'consistency_checker': '📊',
    'subject_matter_expert': '🎓',
    'web_researcher': '🌐',
    'data_validator': '📈',
    'grammar_expert': '📝',
    'clarity_expert': '💡',
    'legal_expert': '⚖️',
    'ethical_reviewer': '🤝',
    'coordinator': '👑',
    'final_evaluator': '⭐',
  };
  
  const normalized = agentName.toLowerCase().replace(/[^a-z_]/g, '_');
  return iconMap[normalized] || '🤖';
}

function formatAgentName(name: string): string {
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

interface DownloadCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  color: 'blue' | 'purple' | 'green';
  onClick: () => void;
}

function DownloadCard({ title, description, icon, color, onClick }: DownloadCardProps) {
  const colorClasses = {
    blue: 'from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700',
    purple: 'from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700',
    green: 'from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700',
  };
  
  return (
    <motion.button
      whileHover={{ scale: 1.05, y: -5 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`
        bg-gradient-to-br ${colorClasses[color]}
        text-white rounded-xl p-6 shadow-lg
        transition-all duration-300
        flex flex-col items-start space-y-3
      `}
    >
      <div className="p-3 bg-white/20 rounded-lg">
        {icon}
      </div>
      <div className="text-left">
        <h4 className="text-lg font-bold">{title}</h4>
        <p className="text-sm text-white/80 mt-1">{description}</p>
      </div>
      <div className="flex items-center text-sm font-medium mt-2">
        <span>Download</span>
        <DocumentArrowDownIcon className="w-4 h-4 ml-2" />
      </div>
    </motion.button>
  );
}

interface StatCardProps {
  label: string;
  value: string | number;
  color?: 'blue' | 'red' | 'green' | 'purple';
}

function StatCard({ label, value, color = 'blue' }: StatCardProps) {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-50',
    red: 'text-red-600 bg-red-50',
    green: 'text-green-600 bg-green-50',
    purple: 'text-purple-600 bg-purple-50',
  };
  
  return (
    <div className={`${colorClasses[color]} rounded-lg p-4 text-center border border-${color}-200`}>
      <div className={`text-3xl font-bold ${colorClasses[color].split(' ')[0]}`}>
        {value}
      </div>
      <div className="text-sm text-gray-600 mt-1 font-medium">{label}</div>
    </div>
  );
}
