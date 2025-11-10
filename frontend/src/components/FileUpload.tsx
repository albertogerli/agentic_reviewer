'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { DocumentTextIcon, CloudArrowUpIcon, FolderIcon } from '@heroicons/react/24/outline';
import { useReviewStore } from '../store/reviewStore';

export function FileUpload() {
  const { file, setFile, setInputFiles: setStoreInputFiles, setReferenceFiles: setStoreReferenceFiles, error } = useReviewStore();
  const [inputFiles, setInputFiles] = useState<File[]>([]);
  const [referenceFiles, setReferenceFiles] = useState<File[]>([]);
  
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      // Support multiple input files
      const updatedFiles = [...inputFiles, ...acceptedFiles];
      setInputFiles(updatedFiles);
      setStoreInputFiles(updatedFiles);
    }
  }, [inputFiles, setStoreInputFiles]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    maxFiles: 10, // Allow up to 10 documents
    multiple: true,
  });
  
  const handleReferenceFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setReferenceFiles(prev => [...prev, ...files]);
    setStoreReferenceFiles([...referenceFiles, ...files]);
  };
  
  const removeInputFile = (index: number) => {
    const updated = inputFiles.filter((_, i) => i !== index);
    setInputFiles(updated);
    setStoreInputFiles(updated);
  };
  
  const removeReferenceFile = (index: number) => {
    const updated = referenceFiles.filter((_, i) => i !== index);
    setReferenceFiles(updated);
    setStoreReferenceFiles(updated);
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full"
    >
      <div
        {...getRootProps()}
        className={`
          relative overflow-hidden
          border-2 border-dashed rounded-2xl
          p-12 text-center cursor-pointer
          transition-all duration-300 ease-in-out
          ${isDragActive
            ? 'border-primary-500 bg-primary-50 scale-105'
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          }
          ${error ? 'border-red-400 bg-red-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <motion.div
          animate={{
            y: isDragActive ? -5 : 0,
          }}
          transition={{ duration: 0.2 }}
          className="flex flex-col items-center space-y-4"
        >
          {isDragActive ? (
            <CloudArrowUpIcon className="w-20 h-20 text-primary-500 animate-bounce-slow" />
          ) : (
            <DocumentTextIcon className="w-20 h-20 text-gray-400" />
          )}
          
          {inputFiles.length > 0 ? (
            <div className="space-y-3 w-full">
              <div className="flex items-center justify-between">
                <p className="text-lg font-semibold text-gray-900">
                  📄 {inputFiles.length} document{inputFiles.length > 1 ? 's' : ''} to analyze
                </p>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setInputFiles([]);
                    setStoreInputFiles([]);
                  }}
                  className="text-xs text-red-600 hover:text-red-700 font-medium px-3 py-1 rounded-lg hover:bg-red-50 transition-colors"
                >
                  Clear All
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-40 overflow-y-auto">
                {inputFiles.map((f, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg border border-gray-200 group hover:border-primary-300 transition-all"
                  >
                    <DocumentTextIcon className="w-4 h-4 text-primary-600 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-700 truncate">{f.name}</p>
                      <p className="text-xs text-gray-400">{(f.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        removeInputFile(i);
                      }}
                      className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 transition-opacity"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
              
              <p className="text-sm text-primary-600 flex items-center justify-center gap-2">
                <CloudArrowUpIcon className="w-4 h-4" />
                Click or drag to add more documents (max 10)
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-xl font-semibold text-gray-700">
                {isDragActive
                  ? 'Drop your documents here'
                  : 'Drag & drop your documents'}
              </p>
              <p className="text-sm text-gray-500">
                or click to browse • Upload multiple files
              </p>
              <div className="flex items-center justify-center space-x-2 mt-4">
                <span className="px-3 py-1 text-xs font-medium text-primary-700 bg-primary-100 rounded-full">
                  PDF
                </span>
                <span className="px-3 py-1 text-xs font-medium text-primary-700 bg-primary-100 rounded-full">
                  DOCX
                </span>
                <span className="px-3 py-1 text-xs font-medium text-primary-700 bg-primary-100 rounded-full">
                  TXT
                </span>
                <span className="px-3 py-1 text-xs font-medium text-primary-700 bg-primary-100 rounded-full">
                  MD
                </span>
              </div>
            </div>
          )}
        </motion.div>
        
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 text-red-600 text-sm font-medium"
          >
            {error}
          </motion.div>
        )}
      </div>
      
      {/* Reference Files Section */}
      {inputFiles.length > 0 && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-6 p-6 bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl border-2 border-dashed border-purple-200"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <FolderIcon className="w-5 h-5 text-purple-600" />
              <h4 className="font-semibold text-gray-800">
                📚 Reference Documents (Optional)
              </h4>
              {referenceFiles.length > 0 && (
                <span className="px-2 py-0.5 text-xs font-bold text-purple-700 bg-purple-200 rounded-full">
                  {referenceFiles.length}
                </span>
              )}
            </div>
            {referenceFiles.length > 0 && (
              <button
                onClick={() => {
                  setReferenceFiles([]);
                  setStoreReferenceFiles([]);
                }}
                className="text-xs text-red-600 hover:text-red-700 font-medium px-3 py-1 rounded-lg hover:bg-red-50 transition-colors"
              >
                Clear All
              </button>
            )}
          </div>
          
          <p className="text-sm text-gray-600 mb-3">
            Upload templates, guidelines, examples, or data files for AI reference
          </p>
          
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.doc,.txt,.md,.xlsx,.xls"
            onChange={handleReferenceFilesChange}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-lg file:border-0
              file:text-sm file:font-semibold
              file:bg-purple-100 file:text-purple-700
              hover:file:bg-purple-200
              cursor-pointer border border-purple-200 rounded-lg bg-white"
          />
          
          {referenceFiles.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-40 overflow-y-auto">
                {referenceFiles.map((f, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg border border-purple-200 group hover:border-purple-400 transition-all"
                  >
                    <DocumentTextIcon className="w-4 h-4 text-purple-600 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-700 truncate">{f.name}</p>
                      <p className="text-xs text-gray-400">
                        {(f.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <button
                      onClick={() => removeReferenceFile(i)}
                      className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 transition-opacity"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}

