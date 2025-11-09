'use client';

import { motion } from 'framer-motion';
import { useMemo } from 'react';
import type { Issue } from './ThreePanelLayout';

interface DocumentViewerProps {
  documentText: string;
  documentTitle: string;
  selectedIssue: Issue | null;
  hoveredIssue: Issue | null;
}

export function DocumentViewer({ documentText, documentTitle, selectedIssue, hoveredIssue }: DocumentViewerProps) {
  // Highlight locations mentioned in issues
  const highlightedText = useMemo(() => {
    if (!selectedIssue && !hoveredIssue) {
      return documentText;
    }

    const activeIssue = selectedIssue || hoveredIssue;
    if (!activeIssue || !activeIssue.evidence) {
      return documentText;
    }

    // Simple highlighting: wrap evidence text in span
    const evidence = activeIssue.evidence;
    if (documentText.includes(evidence)) {
      return documentText.replace(
        evidence,
        `<mark class="bg-yellow-200 px-1 rounded">${evidence}</mark>`
      );
    }

    return documentText;
  }, [documentText, selectedIssue, hoveredIssue]);

  return (
    <div className="h-full flex flex-col">
      {/* Document Header */}
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <h3 className="font-bold text-gray-900 truncate">{documentTitle}</h3>
        <p className="text-xs text-gray-600 mt-1">
          {documentText.length.toLocaleString()} characters
        </p>
      </div>

      {/* Document Content */}
      <div className="flex-1 overflow-y-auto p-6 bg-white">
        {selectedIssue || hoveredIssue ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: highlightedText }}
          />
        ) : (
          <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
            {documentText.substring(0, 5000)}
            {documentText.length > 5000 && (
              <p className="text-gray-500 italic mt-4">
                ... (showing first 5000 characters, select an issue to see highlights)
              </p>
            )}
          </div>
        )}
      </div>

      {/* Hint */}
      {!selectedIssue && !hoveredIssue && (
        <div className="p-4 bg-blue-50 border-t border-blue-200 text-center">
          <p className="text-sm text-blue-800">
            💡 <strong>Tip:</strong> Click or hover over an issue to highlight it in the document
          </p>
        </div>
      )}
    </div>
  );
}

