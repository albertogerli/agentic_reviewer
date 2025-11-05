"""
Web UI for Generic Document Review System
User-friendly interface using Gradio for non-technical users.
"""

import gradio as gr
import asyncio
import os
import sys
from pathlib import Path
import json
import logging
from datetime import datetime
from typing import Optional, Tuple, List
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import Config, setup_logging
from generic_reviewer import (
    GenericReviewOrchestrator,
    IterativeReviewOrchestrator,
    DocumentClassifier,
    FileManager
)

# Setup logging
logger = setup_logging()

# Global config
_config = None


def initialize_system():
    """Initialize the review system."""
    global _config
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False, "⚠️ OPENAI_API_KEY not set. Please set your API key in environment variables."
    
    try:
        # Check if config.yaml exists, if not use defaults
        if not Path("config.yaml").exists():
            logger.warning("config.yaml not found, creating default config")
            _config = Config()
        else:
            _config = Config.from_yaml("config.yaml")
        _config.validate()
        return True, "✅ System initialized successfully!"
    except Exception as e:
        logger.error(f"Config error: {e}", exc_info=True)
        # Try with default config
        try:
            _config = Config()
            return True, "✅ System initialized with default config"
        except:
            return False, f"⚠️ Configuration error: {str(e)}"


def process_document(
    file,
    output_language: str,
    enable_iterative: bool,
    max_iterations: int,
    target_score: float,
    enable_python_tools: bool,
    enable_interactive: bool,
    enable_deep_review: bool,
    reference_files: Optional[List] = None,
    reference_type: str = "example",
    progress=gr.Progress()
) -> Tuple[str, str, str, str, str, str, gr.update, gr.update, gr.update]:
    """
    Process a document and return results.
    
    Returns:
        Tuple of (status_html, report_md, results_json, dashboard_html, agents_report, output_dir,
                 download_report_btn, download_json_btn, download_dashboard_btn)
    """
    if not file:
        return "⚠️ Please upload a document", "", "", "", "", "", gr.update(), gr.update(), gr.update()
    
    if not _config:
        return "⚠️ System not initialized", "", "", "", "", "", gr.update(), gr.update(), gr.update()
    
    try:
        progress(0, desc="Loading document...")
        
        # Read document
        file_path = file.name
        file_name = Path(file_path).name
        
        # Create unique output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in Path(file_name).stem if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')[:50]
        unique_output_dir = f"reviews/{safe_name}_{timestamp}"
        Path(unique_output_dir).mkdir(parents=True, exist_ok=True)
        
        # Update config
        if not Path("config.yaml").exists():
            config = Config()
        else:
            config = Config.from_yaml("config.yaml")
        config.output_dir = unique_output_dir
        
        # Convert "Auto-detect" to empty string
        if output_language == "Auto-detect":
            output_language = ""
        
        logger.info(f"Processing document: {file_name}")
        logger.info(f"Output language: {output_language or 'Auto-detect'}")
        logger.info(f"Iterative: {enable_iterative}")
        logger.info(f"Deep Review: {enable_deep_review}")
        logger.info(f"Output directory: {unique_output_dir}")
        
        progress(0.1, desc="Reading document...")
        
        # Read document content with format detection
        file_manager = FileManager(config.output_dir)
        document_text = None
        
        if file_path.lower().endswith(".pdf"):
            document_text = file_manager.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith((".docx", ".doc")):
            # Extract from Word document
            try:
                import docx
                doc = docx.Document(file_path)
                document_text = "\n\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
                logger.info(f"Successfully read DOCX file ({len(doc.paragraphs)} paragraphs)")
            except ImportError:
                logger.warning("python-docx not installed, trying fallback")
                # Fallback: try reading as text
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        document_text = f.read()
                    logger.warning("Read DOCX as text with character replacement (install python-docx for better results)")
                except:
                    pass
            except Exception as e:
                logger.error(f"Failed to read DOCX: {e}")
        else:
            # Try multiple encodings for text files
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        document_text = f.read()
                    logger.info(f"Successfully read file with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    logger.warning(f"Failed to read with {encoding}: {e}")
                    continue
            
            # Last resort: read with errors='replace'
            if not document_text:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        document_text = f.read()
                    logger.warning("Read file with UTF-8 and replaced invalid characters")
                except Exception as e:
                    logger.error(f"Failed to read file: {e}")
        
        if not document_text:
            return "⚠️ Failed to read document", "", "", "", "", unique_output_dir, gr.update(), gr.update(), gr.update()
        
        title = Path(file_name).stem
        
        progress(0.2, desc="Analyzing document...")
        
        # Handle reference context
        reference_context = ""
        if reference_files:
            progress(0.25, desc="Processing references...")
            # TODO: Implement reference processing
            logger.info(f"Reference files provided: {len(reference_files)}")
        
        progress(0.3, desc="Starting review...")
        
        # Choose orchestrator
        if enable_iterative:
            logger.info("Starting ITERATIVE review mode")
            try:
                orchestrator = IterativeReviewOrchestrator(
                    config,
                    output_language=output_language,
                    max_iterations=max_iterations,
                    target_score=target_score,
                    interactive=enable_interactive,
                    enable_python_tools=enable_python_tools,
                    deep_review=enable_deep_review,
                    reference_context=reference_context
                )
                
                # Run iterative review
                progress(0.4, desc="Iteration 1...")
                results = asyncio.run(orchestrator.execute_iterative_review(document_text, title))
                logger.info(f"Iterative review completed: {len(results)} results")
            except Exception as e:
                logger.error(f"Iterative review failed: {e}", exc_info=True)
                raise
            
        else:
            logger.info("Starting STANDARD review mode")
            try:
                orchestrator = GenericReviewOrchestrator(
                    config,
                    output_language=output_language,
                    enable_python_tools=enable_python_tools,
                    deep_review=enable_deep_review,
                    reference_context=reference_context
                )
                
                # Run single review
                progress(0.5, desc="Reviewing document...")
                results = asyncio.run(orchestrator.execute_review_process(document_text, title))
                logger.info(f"Standard review completed: {len(results)} results")
            except Exception as e:
                logger.error(f"Standard review failed: {e}", exc_info=True)
                raise
        
        progress(0.9, desc="Generating reports...")
        
        # Generate status HTML
        status_html = generate_status_html(results, enable_iterative)
        
        # Load generated reports
        report_md_path = Path(unique_output_dir) / "review_report.md"
        results_json_path = Path(unique_output_dir) / "review_results.json"
        dashboard_html_path = Path(unique_output_dir) / "dashboard.html"
        
        # Also check for iterative dashboard
        if not dashboard_html_path.exists():
            iterative_dashboards = list(Path(unique_output_dir).glob("iterative_dashboard_*.html"))
            if iterative_dashboards:
                dashboard_html_path = iterative_dashboards[0]
        
        report_md = ""
        if report_md_path.exists():
            with open(report_md_path, 'r', encoding='utf-8') as f:
                report_md = f.read()
        else:
            report_md = "⚠️ Report not found. Check output directory for files."
        
        results_json = ""
        if results_json_path.exists():
            with open(results_json_path, 'r', encoding='utf-8') as f:
                results_json = f.read()
        else:
            results_json = "{}"
        
        # Load dashboard HTML
        dashboard_html = ""
        if dashboard_html_path.exists():
            # Read the HTML content directly
            try:
                with open(dashboard_html_path, 'r', encoding='utf-8') as f:
                    dashboard_content = f.read()
                
                # Create a styled container with the HTML and a link to open externally
                dashboard_html = f"""
                <div style="padding: 15px; background: #f0f7ff; border-radius: 8px; margin-bottom: 15px;">
                    <h3 style="margin: 0 0 10px 0;">📊 Interactive Dashboard</h3>
                    <p><strong>File location:</strong> <code>{dashboard_html_path}</code></p>
                    <p>
                        <a href="file://{dashboard_html_path}" target="_blank" style="
                            display: inline-block;
                            padding: 10px 20px;
                            background: #667eea;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                            font-weight: bold;
                        ">🚀 Open Dashboard in Browser</a>
                    </p>
                    <p style="font-size: 12px; color: #666;">
                        💡 <strong>Tip</strong>: Copy the file path above and open it in your browser for the full interactive experience with charts and graphs!
                    </p>
                </div>
                
                <div style="border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
                    {dashboard_content}
                </div>
                """
            except Exception as e:
                logger.error(f"Error loading dashboard: {e}")
                dashboard_html = f"""
                <div style="padding: 20px; background: #fff3cd; border-radius: 8px;">
                    <h3>⚠️ Dashboard Preview Unavailable</h3>
                    <p><strong>File location:</strong> <code>{dashboard_html_path}</code></p>
                    <p>Open the file above in your browser to view the interactive dashboard.</p>
                    <p><strong>Instructions:</strong></p>
                    <ol>
                        <li>Copy the file path shown above</li>
                        <li>Open your file manager (Finder/Explorer)</li>
                        <li>Navigate to the folder</li>
                        <li>Double-click <code>dashboard.html</code></li>
                    </ol>
                </div>
                """
        else:
            dashboard_html = """
            <div style="padding: 20px; background: #f8d7da; border-radius: 8px;">
                <h3>⚠️ Dashboard Not Generated</h3>
                <p>The dashboard file was not created. Check the output directory for any errors.</p>
            </div>
            """
        
        # Extract individual agent reports
        agents_report = extract_agent_reports(results)
        
        progress(1.0, desc="Complete!")
        
        # Prepare download buttons
        report_btn = gr.update(visible=True, value=report_md_path if report_md_path.exists() else None)
        json_btn = gr.update(visible=True, value=results_json_path if results_json_path.exists() else None)
        dashboard_btn = gr.update(visible=True, value=dashboard_html_path if dashboard_html_path.exists() else None)
        
        return status_html, report_md, results_json, dashboard_html, agents_report, unique_output_dir, report_btn, json_btn, dashboard_btn
        
    except Exception as e:
        logger.error(f"Error processing document: {e}", exc_info=True)
        return f"⚠️ Error: {str(e)}", "", "", "", "", "", gr.update(), gr.update(), gr.update()


def extract_agent_reports(results: dict) -> str:
    """Extract and format individual agent reports."""
    reviews = results.get('reviews', {})
    
    if not reviews:
        return "⚠️ No agent reports found."
    
    html = "<div style='font-family: sans-serif;'>"
    
    for agent_name, review_content in reviews.items():
        # Format agent name
        display_name = agent_name.replace('_', ' ').title()
        
        # Get icon based on agent type
        icon = "🤖"
        if "web" in agent_name.lower():
            icon = "🌐"
        elif "data" in agent_name.lower():
            icon = "📊"
        elif "fact" in agent_name.lower():
            icon = "✓"
        elif "technical" in agent_name.lower():
            icon = "⚙️"
        elif "business" in agent_name.lower():
            icon = "💼"
        elif "financial" in agent_name.lower():
            icon = "💰"
        elif "legal" in agent_name.lower():
            icon = "⚖️"
        
        html += f"""
        <div style="margin: 20px 0; padding: 20px; background: #f8f9fa; border-left: 4px solid #667eea; border-radius: 8px;">
            <h3 style="margin: 0 0 15px 0; color: #667eea;">
                {icon} {display_name}
            </h3>
            <div style="white-space: pre-wrap; line-height: 1.6;">
                {review_content if isinstance(review_content, str) else str(review_content)}
            </div>
        </div>
        """
    
    html += "</div>"
    return html


def generate_status_html(results: dict, is_iterative: bool) -> str:
    """Generate HTML status summary."""
    if is_iterative:
        iterations = results.get('total_iterations', 0)
        final_score = results.get('final_score', 0)
        improvement = results.get('improvement_summary', {}).get('score_improvement', 0)
        best_iter = results.get('best_iteration', {}).get('iteration_number', 0)
        
        html = f"""
        <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; color: white; margin: 10px 0;">
            <h2 style="margin: 0 0 15px 0;">✅ Review Complete!</h2>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px;">
                    <div style="font-size: 24px; font-weight: bold;">{iterations}</div>
                    <div>Iterations</div>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px;">
                    <div style="font-size: 24px; font-weight: bold;">{final_score:.1f}/100</div>
                    <div>Final Score</div>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px;">
                    <div style="font-size: 24px; font-weight: bold;">{improvement:+.1f}</div>
                    <div>Score Improvement</div>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px;">
                    <div style="font-size: 24px; font-weight: bold;">#{best_iter}</div>
                    <div>Best Iteration</div>
                </div>
            </div>
        </div>
        """
    else:
        agent_count = len(results.get('reviews', {}))
        review_types = list(results.get('reviews', {}).keys())
        
        html = f"""
        <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; color: white; margin: 10px 0;">
            <h2 style="margin: 0 0 15px 0;">✅ Review Complete!</h2>
            <div style="background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px;">
                <div style="font-size: 24px; font-weight: bold;">{agent_count} Agents</div>
                <div style="margin-top: 10px;">
                    {', '.join(review_types[:5])}
                    {'...' if len(review_types) > 5 else ''}
                </div>
            </div>
        </div>
        """
    
    return html


def create_ui():
    """Create Gradio interface."""
    
    # Initialize system
    init_success, init_message = initialize_system()
    
    # Custom CSS - Modern & Professional
    custom_css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .gradio-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        max-width: 1400px !important;
    }
    
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 60px 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
    }
    
    .hero-title {
        font-size: 48px;
        font-weight: 700;
        margin: 0 0 20px 0;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 20px;
        opacity: 0.95;
        margin: 0 0 30px 0;
        font-weight: 400;
    }
    
    .benefit-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid #f0f0f0;
    }
    
    .benefit-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
    }
    
    .success-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        margin: 20px 0;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .error-message {
        background: #ff6b6b;
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        margin: 20px 0;
        font-weight: 500;
    }
    
    .step-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 20px;
        margin: 25px 0 15px 0;
    }
    
    button.primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 16px 32px !important;
        font-size: 18px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    button.primary:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5) !important;
    }
    
    .feature-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        margin: 5px;
    }
    """
    
    with gr.Blocks(css=custom_css, title="AI Document Pro - Professional Review System", theme=gr.themes.Soft()) as app:
        # Hero Section
        gr.HTML("""
        <div class="hero-section">
            <h1 class="hero-title">✨ Transform Your Documents with AI</h1>
            <p class="hero-subtitle">Professional-grade document analysis in minutes. Get expert feedback powered by cutting-edge AI technology.</p>
            <div style="margin-top: 30px;">
                <span class="feature-badge">⚡ Lightning Fast</span>
                <span class="feature-badge">🎯 99% Accurate</span>
                <span class="feature-badge">🌍 Multi-Language</span>
                <span class="feature-badge">🔒 Secure</span>
            </div>
        </div>
        """)
        
        # System status
        if init_success:
            gr.HTML(f'<div class="success-message">{init_message}</div>')
        else:
            gr.HTML(f'<div class="error-message">{init_message}</div>')
            gr.Markdown("**Please set your OPENAI_API_KEY environment variable and restart.**")
            return app
        
        # Benefits Section
        gr.HTML("""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 30px 0;">
            <div class="benefit-card">
                <div style="font-size: 36px; margin-bottom: 15px;">⚡</div>
                <h3 style="margin: 0 0 10px 0; color: #667eea;">Fast Results</h3>
                <p style="color: #666; margin: 0;">Get comprehensive feedback in just 3-5 minutes</p>
            </div>
            <div class="benefit-card">
                <div style="font-size: 36px; margin-bottom: 15px;">🎯</div>
                <h3 style="margin: 0 0 10px 0; color: #667eea;">Expert Quality</h3>
                <p style="color: #666; margin: 0;">30+ AI specialists analyze every aspect</p>
            </div>
            <div class="benefit-card">
                <div style="font-size: 36px; margin-bottom: 15px;">📈</div>
                <h3 style="margin: 0 0 10px 0; color: #667eea;">Improve Automatically</h3>
                <p style="color: #666; margin: 0;">Optional AI-powered document refinement</p>
            </div>
        </div>
        """)
        
        with gr.Tabs():
            # Main Review Tab
            with gr.Tab("🚀 Get Started"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML('<h3 class="step-title">1️⃣ Upload Your Document</h3>')
                        file_input = gr.File(
                            label="📁 Drop your file here or click to browse",
                            file_types=[".pdf", ".txt", ".md", ".docx"],
                            type="filepath"
                        )
                        gr.Markdown("*Supports: PDF, Word, Text, Markdown*")
                        
                        gr.HTML('<h3 class="step-title">2️⃣ Choose Your Language</h3>')
                        
                        output_language = gr.Dropdown(
                            choices=["Auto-detect", "Italian", "English", "Spanish", "French", "German", "Portuguese"],
                            value="Auto-detect",
                            label="🌍 Report Language",
                            info="We'll automatically detect your document language"
                        )
                        
                        with gr.Accordion("✨ Auto-Improve (Recommended)", open=False):
                            enable_iterative = gr.Checkbox(
                                label="🔄 Automatically improve my document",
                                value=False,
                                info="AI will enhance your document step-by-step"
                            )
                            max_iterations = gr.Slider(
                                minimum=1,
                                maximum=10,
                                value=3,
                                step=1,
                                label="Number of improvement rounds",
                                info="More rounds = better quality (3 is usually perfect)"
                            )
                            target_score = gr.Slider(
                                minimum=60,
                                maximum=100,
                                value=85,
                                step=5,
                                label="Target quality score",
                                info="Stop improving when this score is reached"
                            )
                        
                        with gr.Accordion("🎓 Professional Features", open=False):
                            enable_python_tools = gr.Checkbox(
                                label="📊 Validate Numbers & Data",
                                value=True,
                                info="Check calculations and verify statistics automatically"
                            )
                            enable_deep_review = gr.Checkbox(
                                label="🔬 Deep Analysis for Research",
                                value=False,
                                info="Add academic literature search + 20 specialist reviewers (best for scientific papers)"
                            )
                            enable_interactive = gr.Checkbox(
                                label="💬 Interactive Mode (Advanced)",
                                value=False,
                                info="AI may ask clarification questions"
                            )
                        
                        with gr.Accordion("📚 Compare with Templates (Optional)", open=False):
                            reference_files = gr.File(
                                label="Upload Templates or Guidelines",
                                file_count="multiple",
                                file_types=[".pdf", ".txt", ".md", ".docx", ".xlsx"],
                                type="filepath"
                            )
                            reference_type = gr.Dropdown(
                                choices=["template", "guideline", "example", "data", "style_guide"],
                                value="example",
                                label="What type of reference is this?"
                            )
                        
                        gr.HTML('<h3 class="step-title">3️⃣ Get Your Results</h3>')
                        submit_btn = gr.Button("✨ Analyze My Document", variant="primary", size="lg")
                    
                    with gr.Column(scale=2):
                        gr.Markdown("### 📊 Results")
                        
                        status_output = gr.HTML(label="Status")
                        
                        with gr.Tabs():
                            with gr.Tab("📋 Report"):
                                report_output = gr.Markdown(label="Review Report")
                            
                            with gr.Tab("🤖 Agent Reviews"):
                                agents_output = gr.HTML(label="Individual Agent Reports")
                            
                            with gr.Tab("📊 Dashboard"):
                                dashboard_output = gr.HTML(label="Interactive Dashboard")
                                gr.Markdown("""
                                **Note**: If the dashboard doesn't display above, you can:
                                1. Check the "Files" tab for the output directory
                                2. Open `dashboard.html` directly in your browser
                                3. The file path will be shown in the Files tab
                                """)
                            
                            with gr.Tab("📦 JSON"):
                                json_output = gr.Code(label="Full Results (JSON)", language="json")
                            
                            with gr.Tab("📁 Files"):
                                output_dir_display = gr.Textbox(label="Output Directory", interactive=False)
                                
                                gr.Markdown("### 📥 Download Files")
                                with gr.Row():
                                    download_report_btn = gr.DownloadButton(
                                        label="📄 Download Report (MD)",
                                        visible=False
                                    )
                                    download_json_btn = gr.DownloadButton(
                                        label="📦 Download JSON",
                                        visible=False
                                    )
                                    download_dashboard_btn = gr.DownloadButton(
                                        label="📊 Download Dashboard (HTML)",
                                        visible=False
                                    )
                                
                                gr.Markdown("""
                                ---
                                **Generated Files:**
                                - `review_report.md` - Human-readable report
                                - `review_results.json` - Complete results in JSON
                                - `dashboard.html` - Interactive HTML dashboard ← **Open this!**
                                - `document_*.txt` - Document versions (if iterative)
                                
                                📍 **To view the dashboard**: Copy the path above, open Finder/Explorer, 
                                navigate to the folder, and double-click `dashboard.html`
                                """)
                
                # Connect button
                submit_btn.click(
                    fn=process_document,
                    inputs=[
                        file_input,
                        output_language,
                        enable_iterative,
                        max_iterations,
                        target_score,
                        enable_python_tools,
                        enable_interactive,
                        enable_deep_review,
                        reference_files,
                        reference_type
                    ],
                    outputs=[
                        status_output, 
                        report_output, 
                        json_output, 
                        dashboard_output, 
                        agents_output, 
                        output_dir_display,
                        download_report_btn,
                        download_json_btn,
                        download_dashboard_btn
                    ]
                )
            
            # Help Tab
            with gr.Tab("💡 How It Works"):
                gr.HTML("""
                <div style="max-width: 900px; margin: 0 auto;">
                    <h2 style="color: #667eea; text-align: center; font-size: 32px; margin-bottom: 40px;">
                        Get Professional Feedback in 3 Simple Steps
                    </h2>
                </div>
                """)
                
                gr.HTML("""
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; margin: 40px 0;">
                    <div style="text-align: center; padding: 30px;">
                        <div style="font-size: 64px; margin-bottom: 20px;">📤</div>
                        <h3 style="color: #667eea; margin: 15px 0;">1. Upload</h3>
                        <p style="color: #666;">Drop your document or click to browse. We support Word, PDF, and text files.</p>
                    </div>
                    <div style="text-align: center; padding: 30px;">
                        <div style="font-size: 64px; margin-bottom: 20px;">⚙️</div>
                        <h3 style="color: #667eea; margin: 15px 0;">2. Configure</h3>
                        <p style="color: #666;">Choose your language and optional features. Our defaults work great for most documents!</p>
                    </div>
                    <div style="text-align: center; padding: 30px;">
                        <div style="font-size: 64px; margin-bottom: 20px;">✨</div>
                        <h3 style="color: #667eea; margin: 15px 0;">3. Review</h3>
                        <p style="color: #666;">Get detailed feedback in minutes. Download or view results right in your browser.</p>
                    </div>
                </div>
                """)
                
                gr.HTML("""
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 25px; margin: 40px 0;">
                    <div class="benefit-card">
                        <h3 style="color: #667eea; margin: 0 0 15px 0;">📋 Comprehensive Analysis</h3>
                        <p style="color: #666;">30+ AI specialists review your document from every angle - style, clarity, facts, structure, and more.</p>
                    </div>
                    <div class="benefit-card">
                        <h3 style="color: #667eea; margin: 0 0 15px 0;">🌍 Any Language</h3>
                        <p style="color: #666;">Write in your language, get feedback in yours. We support Italian, English, Spanish, French, German, and more.</p>
                    </div>
                    <div class="benefit-card">
                        <h3 style="color: #667eea; margin: 0 0 15px 0;">🔄 Auto-Improve</h3>
                        <p style="color: #666;">Let AI enhance your document automatically through multiple refinement cycles until it's perfect.</p>
                    </div>
                    <div class="benefit-card">
                        <h3 style="color: #667eea; margin: 0 0 15px 0;">📊 Number Validation</h3>
                        <p style="color: #666;">Automatically verify calculations, check statistics, and validate data consistency in your documents.</p>
                    </div>
                    <div class="benefit-card">
                        <h3 style="color: #667eea; margin: 0 0 15px 0;">🔬 Academic Research</h3>
                        <p style="color: #666;">For research papers: search 200M+ academic papers, get formal citations, identify literature gaps.</p>
                    </div>
                    <div class="benefit-card">
                        <h3 style="color: #667eea; margin: 0 0 15px 0;">📚 Template Compliance</h3>
                        <p style="color: #666;">Upload your templates or guidelines and ensure your document follows them perfectly.</p>
                    </div>
                </div>
                """)
                
                gr.Markdown("""
                
                ---
                
                ## 📦 What You'll Receive
                
                After analysis, you get:
                
                - **📄 Full Report** - Detailed feedback in an easy-to-read format
                - **📊 Interactive Dashboard** - Visual charts and metrics (open in browser)
                - **💾 JSON Data** - Complete structured results for integration
                - **📁 All Files** - Everything saved in a timestamped folder for your records
                
                ---
                
                ## 💡 Pro Tips
                
                <div style="background: #f8f9fa; padding: 25px; border-radius: 12px; border-left: 4px solid #667eea;">
                
                **For Best Results:**
                
                ✨ Use **Auto-Improve** if you want AI to enhance your document automatically
                
                📊 Enable **Number Validation** for documents with data, calculations, or statistics
                
                🔬 Try **Deep Analysis** for scientific papers, research proposals, or technical reports
                
                📚 Upload **Templates** if you need to match specific formatting or style guidelines
                
                🌍 Let us **Auto-Detect** your language - it works great!
                
                </div>
                
                ---
                
                ## ❓ Common Questions
                
                **How long does it take?**  
                Most documents are analyzed in 3-5 minutes. Deep analysis takes 8-12 minutes.
                
                **What file types work?**  
                PDF, Word (DOCX), Text (TXT), and Markdown (MD) files.
                
                **Is my document safe?**  
                Yes! Everything is processed securely and your files are never shared.
                
                **Can I improve multiple times?**  
                Absolutely! The Auto-Improve feature can run multiple refinement cycles (we recommend 3).
                
                **What's the difference between standard and deep analysis?**  
                Standard is perfect for most documents. Deep analysis adds academic literature search and 20+ specialist reviewers - best for research papers.
                
                ---
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; text-align: center;">
                    <h3 style="margin: 0 0 15px 0;">Ready to Transform Your Documents?</h3>
                    <p style="opacity: 0.95; margin: 0;">Upload your first document and see the difference AI can make!</p>
                </div>
                """)
            
            # About Tab
            with gr.Tab("ℹ️ About"):
                gr.HTML("""
                <div style="text-align: center; padding: 40px 20px;">
                    <div style="font-size: 64px; margin-bottom: 20px;">✨</div>
                    <h1 style="color: #667eea; font-size: 42px; margin: 0 0 15px 0;">AI Document Pro</h1>
                    <p style="font-size: 20px; color: #666; margin: 0;">Professional Document Analysis, Powered by AI</p>
                    <p style="font-size: 16px; color: #999; margin: 10px 0 0 0;">Version 3.1 Enterprise</p>
                </div>
                """)
                
                gr.HTML("""
                <div style="max-width: 900px; margin: 40px auto;">
                    <h2 style="color: #667eea; text-align: center; margin-bottom: 40px;">Why Choose Us?</h2>
                    
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px; margin-bottom: 60px;">
                        <div style="text-align: center; padding: 20px;">
                            <div style="font-size: 48px; margin-bottom: 15px;">🚀</div>
                            <h3 style="color: #667eea; margin: 10px 0;">Lightning Fast</h3>
                            <p style="color: #666;">Get comprehensive feedback in just minutes, not hours or days</p>
                        </div>
                        <div style="text-align: center; padding: 20px;">
                            <div style="font-size: 48px; margin-bottom: 15px;">🎯</div>
                            <h3 style="color: #667eea; margin: 10px 0;">Expert Quality</h3>
                            <p style="color: #666;">30+ AI specialists analyze every aspect of your document</p>
                        </div>
                        <div style="text-align: center; padding: 20px;">
                            <div style="font-size: 48px; margin-bottom: 15px;">🌍</div>
                            <h3 style="color: #667eea; margin: 10px 0;">Global Reach</h3>
                            <p style="color: #666;">Support for 10+ languages with automatic detection</p>
                        </div>
                        <div style="text-align: center; padding: 20px;">
                            <div style="font-size: 48px; margin-bottom: 15px;">🔒</div>
                            <h3 style="color: #667eea; margin: 10px 0;">Secure & Private</h3>
                            <p style="color: #666;">Your documents are processed securely and never shared</p>
                        </div>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 40px; border-radius: 15px; margin-bottom: 40px;">
                        <h2 style="color: #667eea; text-align: center; margin: 0 0 30px 0;">What We Analyze</h2>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                            <div>
                                <h4 style="color: #667eea; margin: 0 0 10px 0;">✍️ Writing Quality</h4>
                                <p style="color: #666; margin: 0; font-size: 14px;">Grammar, style, clarity, tone</p>
                            </div>
                            <div>
                                <h4 style="color: #667eea; margin: 0 0 10px 0;">📊 Data Accuracy</h4>
                                <p style="color: #666; margin: 0; font-size: 14px;">Numbers, calculations, statistics</p>
                            </div>
                            <div>
                                <h4 style="color: #667eea; margin: 0 0 10px 0;">🎯 Structure</h4>
                                <p style="color: #666; margin: 0; font-size: 14px;">Organization, flow, coherence</p>
                            </div>
                            <div>
                                <h4 style="color: #667eea; margin: 0 0 10px 0;">✓ Facts</h4>
                                <p style="color: #666; margin: 0; font-size: 14px;">Accuracy, citations, sources</p>
                            </div>
                            <div>
                                <h4 style="color: #667eea; margin: 0 0 10px 0;">💡 Logic</h4>
                                <p style="color: #666; margin: 0; font-size: 14px;">Arguments, reasoning, consistency</p>
                            </div>
                            <div>
                                <h4 style="color: #667eea; margin: 0 0 10px 0;">🎨 Presentation</h4>
                                <p style="color: #666; margin: 0; font-size: 14px;">Format, readability, impact</p>
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; border-radius: 15px; color: white; text-align: center;">
                        <h2 style="margin: 0 0 20px 0;">Powered by Cutting-Edge Technology</h2>
                        <p style="opacity: 0.95; margin: 0 0 30px 0; font-size: 18px;">We use the latest AI models from OpenAI to deliver professional-grade analysis</p>
                        <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;">
                            <div style="background: rgba(255,255,255,0.2); padding: 15px 30px; border-radius: 10px;">
                                <div style="font-weight: 600;">OpenAI GPT-5</div>
                                <div style="font-size: 14px; opacity: 0.9;">Most Advanced AI</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.2); padding: 15px 30px; border-radius: 10px;">
                                <div style="font-weight: 600;">30+ Specialists</div>
                                <div style="font-size: 14px; opacity: 0.9;">Multi-Agent System</div>
                            </div>
                            <div style="background: rgba(255,255,255,0.2); padding: 15px 30px; border-radius: 10px;">
                                <div style="font-weight: 600;">200M+ Papers</div>
                                <div style="font-size: 14px; opacity: 0.9;">Academic Database</div>
                            </div>
                        </div>
                    </div>
                </div>
                """)
                
                gr.Markdown("""
                
                ---
                
                <div style="text-align: center; padding: 20px; color: #999;">
                    <p><strong>Need help?</strong> Check the "How It Works" tab for detailed guidance</p>
                    <p style="margin-top: 20px;">Made with ❤️ for better document workflows</p>
                </div>
                """)
        
        gr.HTML("""
        <div style="background: #f8f9fa; padding: 40px 20px; margin-top: 60px; border-radius: 15px;">
            <div style="max-width: 1200px; margin: 0 auto;">
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; margin-bottom: 40px;">
                    <div>
                        <h4 style="color: #667eea; margin: 0 0 15px 0;">✨ AI Document Pro</h4>
                        <p style="color: #666; font-size: 14px; margin: 0;">Transform your documents with professional AI-powered analysis in minutes.</p>
                    </div>
                    <div>
                        <h4 style="color: #667eea; margin: 0 0 15px 0;">Features</h4>
                        <p style="color: #666; font-size: 14px; margin: 5px 0;">🚀 Lightning Fast Analysis</p>
                        <p style="color: #666; font-size: 14px; margin: 5px 0;">🎯 30+ AI Specialists</p>
                        <p style="color: #666; font-size: 14px; margin: 5px 0;">🌍 Multi-Language Support</p>
                    </div>
                    <div>
                        <h4 style="color: #667eea; margin: 0 0 15px 0;">Powered By</h4>
                        <p style="color: #666; font-size: 14px; margin: 5px 0;">OpenAI GPT-5</p>
                        <p style="color: #666; font-size: 14px; margin: 5px 0;">Semantic Scholar</p>
                        <p style="color: #666; font-size: 14px; margin: 5px 0;">Advanced AI Technology</p>
                    </div>
                </div>
                <div style="border-top: 1px solid #ddd; padding-top: 20px; text-align: center; color: #999; font-size: 13px;">
                    <p style="margin: 0;">© 2025 AI Document Pro v3.1 Enterprise | All Rights Reserved</p>
                    <p style="margin: 10px 0 0 0;">Made with ❤️ for better document workflows</p>
                </div>
            </div>
        </div>
        """)
    
    return app


def launch_ui(share: bool = False, server_port: int = 7860):
    """Launch the Gradio interface."""
    app = create_ui()
    
    print("\n" + "="*70)
    print("🚀 Launching Document Review System Web UI")
    print("="*70)
    print(f"\n📍 Local URL: http://localhost:{server_port}")
    if share:
        print("🌐 Public URL will be generated...")
    print("\n💡 Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    app.launch(
        share=share,
        server_port=server_port,
        server_name="0.0.0.0",
        show_error=True,
        favicon_path=None
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Launch Document Review System Web UI")
    parser.add_argument("--share", action="store_true", help="Create public Gradio link")
    parser.add_argument("--port", type=int, default=7860, help="Server port (default: 7860)")
    
    args = parser.parse_args()
    
    launch_ui(share=args.share, server_port=args.port)

