'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { DocumentTextIcon, CloudArrowUpIcon, FolderIcon } from '@heroicons/react/24/outline';
import { useReviewStore } from '../store/reviewStore';

export function FileUpload() {
  const { file, setFile, setReferenceFiles: setStoreReferenceFiles, error } = useReviewStore();
  const [referenceFiles, setReferenceFiles] = useState<File[]>([]);
  
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, [setFile]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    maxFiles: 1,
  });
  
  const handleReferenceFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setReferenceFiles(files);
    setStoreReferenceFiles(files);
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
          
          {file ? (
            <div className="space-y-2">
              <div className="flex items-center justify-center space-x-2">
                <DocumentTextIcon className="w-6 h-6 text-primary-600" />
                <p className="text-lg font-semibold text-gray-900">
                  {file.name}
                </p>
              </div>
              <p className="text-sm text-gray-500">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
              <p className="text-sm text-primary-600">
                Click or drag to replace
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-xl font-semibold text-gray-700">
                {isDragActive
                  ? 'Drop your document here'
                  : 'Drag & drop your document'}
              </p>
              <p className="text-sm text-gray-500">
                or click to browse
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
      {file && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-6 p-6 bg-gray-50 rounded-xl border border-gray-200"
        >
          <div className="flex items-center gap-2 mb-3">
            <FolderIcon className="w-5 h-5 text-gray-600" />
            <h4 className="font-semibold text-gray-800">Reference Documents (Optional)</h4>
          </div>
          <p className="text-sm text-gray-600 mb-3">
            Upload templates, guidelines, or examples for the AI to reference
          </p>
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.doc,.txt,.md,.xlsx,.xls"
            onChange={handleReferenceFilesChange}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-primary-50 file:text-primary-700
              hover:file:bg-primary-100
              cursor-pointer"
          />
          {referenceFiles.length > 0 && (
            <motion.ul
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-3 space-y-2"
            >
              {referenceFiles.map((f, i) => (
                <li
                  key={i}
                  className="text-sm text-gray-700 flex items-center gap-2 bg-white px-3 py-2 rounded-lg"
                >
                  <DocumentTextIcon className="w-4 h-4 text-primary-600" />
                  <span>{f.name}</span>
                  <span className="text-gray-400 ml-auto">
                    ({(f.size / 1024).toFixed(1)} KB)
                  </span>
                </li>
              ))}
            </motion.ul>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}

