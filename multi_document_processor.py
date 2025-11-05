"""
Multi-Document Processor
Handles batch processing of multiple documents from directories or ZIP files.
"""

import os
import zipfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class DocumentInfo:
    """Information about a document to process."""
    file_path: str
    file_name: str
    file_size: int
    file_type: str  # pdf, txt, docx, etc.
    relative_path: str  # Path relative to input directory/zip
    content: Optional[str] = None


@dataclass
class BatchResult:
    """Result of batch document processing."""
    total_documents: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]
    aggregate_stats: Dict[str, Any]
    output_directory: str
    processing_time: float


class MultiDocumentProcessor:
    """
    Processes multiple documents from directories or ZIP files.
    
    Features:
    - Process all documents in a directory (recursive)
    - Extract and process documents from ZIP
    - Batch processing with progress tracking
    - Aggregate statistics across documents
    - Cross-document analysis
    """
    
    SUPPORTED_EXTENSIONS = {
        '.pdf': 'pdf',
        '.txt': 'text',
        '.md': 'markdown',
        '.docx': 'word',
        '.doc': 'word',
        '.json': 'json'
    }
    
    def __init__(self, output_base_dir: str = "batch_reviews"):
        self.output_base_dir = output_base_dir
        self.temp_dir = Path(output_base_dir) / "_temp"
    
    def discover_documents(self, input_path: str, 
                          recursive: bool = True) -> List[DocumentInfo]:
        """
        Discover all supported documents in path (directory or ZIP).
        
        Args:
            input_path: Path to directory or ZIP file
            recursive: If True, search subdirectories
        
        Returns:
            List of DocumentInfo objects
        """
        path = Path(input_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {input_path}")
        
        if path.is_file() and path.suffix.lower() == '.zip':
            return self._discover_from_zip(path)
        elif path.is_dir():
            return self._discover_from_directory(path, recursive)
        elif path.is_file():
            # Single file
            return [self._create_document_info(path, path.parent)]
        else:
            raise ValueError(f"Unsupported path type: {input_path}")
    
    def _discover_from_directory(self, directory: Path, 
                                 recursive: bool) -> List[DocumentInfo]:
        """Discover documents in directory."""
        documents = []
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                doc_info = self._create_document_info(file_path, directory)
                documents.append(doc_info)
        
        logger.info(f"Discovered {len(documents)} documents in {directory}")
        return documents
    
    def _discover_from_zip(self, zip_path: Path) -> List[DocumentInfo]:
        """Discover documents in ZIP file."""
        documents = []
        
        # Create temp directory for extraction
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        extract_dir = self.temp_dir / f"zip_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract all files
                zip_ref.extractall(extract_dir)
                logger.info(f"Extracted ZIP to {extract_dir}")
            
            # Discover extracted documents
            for file_path in extract_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    doc_info = self._create_document_info(file_path, extract_dir)
                    documents.append(doc_info)
            
            logger.info(f"Discovered {len(documents)} documents in ZIP: {zip_path}")
            
        except Exception as e:
            logger.error(f"Error processing ZIP file: {e}")
            raise
        
        return documents
    
    def _create_document_info(self, file_path: Path, base_path: Path) -> DocumentInfo:
        """Create DocumentInfo from file path."""
        relative_path = file_path.relative_to(base_path)
        file_type = self.SUPPORTED_EXTENSIONS.get(file_path.suffix.lower(), 'unknown')
        
        return DocumentInfo(
            file_path=str(file_path),
            file_name=file_path.name,
            file_size=file_path.stat().st_size,
            file_type=file_type,
            relative_path=str(relative_path)
        )
    
    def load_document_content(self, doc_info: DocumentInfo) -> str:
        """Load content from document."""
        try:
            if doc_info.file_type == 'pdf':
                return self._load_pdf(doc_info.file_path)
            elif doc_info.file_type in ['text', 'markdown', 'json']:
                with open(doc_info.file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif doc_info.file_type == 'word':
                return self._load_word(doc_info.file_path)
            else:
                logger.warning(f"Unsupported file type: {doc_info.file_type}")
                return ""
        except Exception as e:
            logger.error(f"Error loading {doc_info.file_path}: {e}")
            return ""
    
    def _load_pdf(self, file_path: str) -> str:
        """Load PDF content."""
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = []
                for page in reader.pages:
                    text.append(page.extract_text())
                return '\n'.join(text)
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return ""
    
    def _load_word(self, file_path: str) -> str:
        """Load Word document content."""
        try:
            import docx
            doc = docx.Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except ImportError:
            logger.warning("python-docx not installed")
            return ""
        except Exception as e:
            logger.error(f"Error reading Word document: {e}")
            return ""
    
    async def process_batch(self, documents: List[DocumentInfo],
                          review_function: callable,
                          parallel: bool = False,
                          max_concurrent: int = 3) -> BatchResult:
        """
        Process multiple documents in batch.
        
        Args:
            documents: List of documents to process
            review_function: Async function to review each document
            parallel: If True, process documents in parallel
            max_concurrent: Max concurrent processes if parallel
        
        Returns:
            BatchResult with all results and statistics
        """
        import time
        start_time = time.time()
        
        # Create batch output directory
        batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_output_dir = Path(self.output_base_dir) / f"batch_{batch_id}"
        batch_output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Starting batch processing of {len(documents)} documents")
        logger.info(f"Output directory: {batch_output_dir}")
        
        results = []
        successful = 0
        failed = 0
        
        if parallel and len(documents) > 1:
            # Parallel processing with semaphore
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_with_semaphore(doc):
                async with semaphore:
                    return await self._process_single_document(
                        doc, review_function, batch_output_dir
                    )
            
            tasks = [process_with_semaphore(doc) for doc in documents]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
        else:
            # Sequential processing
            for i, doc in enumerate(documents, 1):
                logger.info(f"Processing document {i}/{len(documents)}: {doc.file_name}")
                
                result = await self._process_single_document(
                    doc, review_function, batch_output_dir
                )
                results.append(result)
        
        # Count successes/failures
        for result in results:
            if isinstance(result, Exception):
                failed += 1
                logger.error(f"Document failed: {result}")
            elif result.get('success', False):
                successful += 1
            else:
                failed += 1
        
        # Calculate aggregate statistics
        aggregate_stats = self._calculate_aggregate_stats(results)
        
        # Save batch summary
        batch_summary = {
            'batch_id': batch_id,
            'total_documents': len(documents),
            'successful': successful,
            'failed': failed,
            'processing_time': time.time() - start_time,
            'documents': [
                {
                    'file_name': doc.file_name,
                    'file_path': doc.file_path,
                    'relative_path': doc.relative_path,
                    'file_size': doc.file_size,
                    'file_type': doc.file_type
                }
                for doc in documents
            ],
            'aggregate_stats': aggregate_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        summary_path = batch_output_dir / "batch_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(batch_summary, f, indent=2)
        
        logger.info(f"Batch processing complete: {successful}/{len(documents)} successful")
        
        return BatchResult(
            total_documents=len(documents),
            successful=successful,
            failed=failed,
            results=results,
            aggregate_stats=aggregate_stats,
            output_directory=str(batch_output_dir),
            processing_time=time.time() - start_time
        )
    
    async def _process_single_document(self, doc_info: DocumentInfo,
                                      review_function: callable,
                                      output_dir: Path) -> Dict[str, Any]:
        """Process a single document."""
        try:
            # Load content
            if not doc_info.content:
                doc_info.content = self.load_document_content(doc_info)
            
            if not doc_info.content:
                return {
                    'success': False,
                    'file_name': doc_info.file_name,
                    'error': 'Failed to load content'
                }
            
            # Create document-specific output directory
            safe_name = "".join(c for c in Path(doc_info.file_name).stem 
                               if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')[:50]
            doc_output_dir = output_dir / safe_name
            doc_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Call review function
            result = await review_function(
                document_text=doc_info.content,
                document_title=doc_info.file_name,
                output_directory=str(doc_output_dir)
            )
            
            return {
                'success': True,
                'file_name': doc_info.file_name,
                'file_path': doc_info.file_path,
                'relative_path': doc_info.relative_path,
                'output_directory': str(doc_output_dir),
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Error processing {doc_info.file_name}: {e}", exc_info=True)
            return {
                'success': False,
                'file_name': doc_info.file_name,
                'file_path': doc_info.file_path,
                'error': str(e)
            }
    
    def _calculate_aggregate_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregate statistics across all documents."""
        successful_results = [r for r in results if isinstance(r, dict) and r.get('success')]
        
        if not successful_results:
            return {}
        
        # Extract scores if available
        scores = []
        for result in successful_results:
            if 'result' in result and isinstance(result['result'], dict):
                score = result['result'].get('final_score') or result['result'].get('score')
                if score is not None:
                    scores.append(score)
        
        aggregate = {
            'total_processed': len(successful_results),
            'total_failed': len(results) - len(successful_results)
        }
        
        if scores:
            aggregate['scores'] = {
                'mean': sum(scores) / len(scores),
                'min': min(scores),
                'max': max(scores),
                'count': len(scores)
            }
        
        return aggregate
    
    def cleanup_temp(self):
        """Clean up temporary extraction directory."""
        if self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info(f"Cleaned up temp directory: {self.temp_dir}")


class CrossDocumentAnalyzer:
    """
    Performs cross-document analysis on batch results.
    """
    
    @staticmethod
    def compare_documents(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple documents and find patterns."""
        successful = [r for r in results if r.get('success')]
        
        if len(successful) < 2:
            return {"error": "Need at least 2 successful reviews for comparison"}
        
        comparison = {
            'total_documents': len(successful),
            'documents': []
        }
        
        for result in successful:
            if 'result' in result:
                doc_info = {
                    'file_name': result['file_name'],
                    'score': result['result'].get('final_score') or result['result'].get('score'),
                    'issues': result['result'].get('issues', {})
                }
                comparison['documents'].append(doc_info)
        
        # Find best and worst
        if comparison['documents']:
            scores = [d['score'] for d in comparison['documents'] if d.get('score')]
            if scores:
                comparison['best_score'] = max(scores)
                comparison['worst_score'] = min(scores)
                comparison['average_score'] = sum(scores) / len(scores)
        
        return comparison
    
    @staticmethod
    def generate_comparison_report(comparison: Dict[str, Any], 
                                  output_path: str):
        """Generate markdown comparison report."""
        report = []
        report.append("# Cross-Document Comparison Report\n")
        report.append(f"**Total Documents:** {comparison.get('total_documents', 0)}\n")
        
        if 'average_score' in comparison:
            report.append(f"**Average Score:** {comparison['average_score']:.1f}/100\n")
            report.append(f"**Best Score:** {comparison['best_score']:.1f}/100\n")
            report.append(f"**Worst Score:** {comparison['worst_score']:.1f}/100\n")
        
        report.append("\n## Document Rankings\n\n")
        
        docs = comparison.get('documents', [])
        if docs:
            # Sort by score
            sorted_docs = sorted(docs, key=lambda x: x.get('score', 0), reverse=True)
            
            report.append("| Rank | Document | Score |\n")
            report.append("|------|----------|-------|\n")
            
            for i, doc in enumerate(sorted_docs, 1):
                score = doc.get('score', 'N/A')
                score_str = f"{score:.1f}/100" if isinstance(score, (int, float)) else score
                report.append(f"| {i} | {doc['file_name']} | {score_str} |\n")
        
        report_text = ''.join(report)
        
        with open(output_path, 'w') as f:
            f.write(report_text)
        
        logger.info(f"Comparison report saved: {output_path}")
        return report_text

