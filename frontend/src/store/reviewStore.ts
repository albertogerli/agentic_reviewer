import { create } from 'zustand';

export interface Agent {
  key: string;
  name: string;
  icon: string;
  status: 'pending' | 'analyzing' | 'completed';
}

export interface ReviewProgress {
  progress: number;
  status: string;
  currentAgent: string | null;
  completedAgents: number;
  totalAgents: number;
}

export interface ReviewConfig {
  output_language: string;
  enable_iterative: boolean;
  max_iterations: number;
  target_score: number;
  enable_python_tools: boolean;
  enable_interactive: boolean;
  enable_deep_review: boolean;
}

export interface ReviewResults {
  report_md: string;
  results_json: any;
  dashboard_html: string;
}

interface ReviewState {
  // Current review
  reviewId: string | null;
  file: File | null; // Main file for backward compatibility
  inputFiles: File[]; // Multiple input files
  referenceFiles: File[];
  config: ReviewConfig;
  
  // Progress
  progress: ReviewProgress;
  agents: Agent[];
  
  // Results
  results: ReviewResults | null;
  outputDir: string | null;
  
  // UI State
  isProcessing: boolean;
  error: string | null;
  
  // WebSocket
  ws: WebSocket | null;
  
  // Actions
  setFile: (file: File | null) => void;
  setInputFiles: (files: File[]) => void;
  setReferenceFiles: (files: File[]) => void;
  setConfig: (config: Partial<ReviewConfig>) => void;
  startReview: () => Promise<void>;
  updateProgress: (progress: Partial<ReviewProgress>) => void;
  updateAgent: (agentKey: string, status: Agent['status']) => void;
  setResults: (results: ReviewResults, outputDir: string) => void;
  setError: (error: string | null) => void;
  reset: () => void;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

const DEFAULT_CONFIG: ReviewConfig = {
  output_language: '',
  enable_iterative: false,
  max_iterations: 3,
  target_score: 85.0,
  enable_python_tools: false,
  enable_interactive: false,
  enable_deep_review: false,
};

const DEFAULT_PROGRESS: ReviewProgress = {
  progress: 0,
  status: 'Ready',
  currentAgent: null,
  completedAgents: 0,
  totalAgents: 0,
};

export const useReviewStore = create<ReviewState>((set, get) => ({
  // Initial state
  reviewId: null,
  file: null,
  inputFiles: [],
  referenceFiles: [],
  config: DEFAULT_CONFIG,
  progress: DEFAULT_PROGRESS,
  agents: [],
  results: null,
  outputDir: null,
  isProcessing: false,
  error: null,
  ws: null,
  
  // Actions
  setFile: (file) => set({ file, error: null }),
  
  setInputFiles: (files) => set({ inputFiles: files, file: files[0] || null, error: null }),
  
  setReferenceFiles: (files) => set({ referenceFiles: files }),
  
  setConfig: (config) => set((state) => ({
    config: { ...state.config, ...config }
  })),
  
  startReview: async () => {
    const { file, inputFiles, referenceFiles, config, connectWebSocket } = get();
    
    // Use inputFiles if available, otherwise fall back to single file
    const filesToProcess = inputFiles.length > 0 ? inputFiles : (file ? [file] : []);
    
    if (filesToProcess.length === 0) {
      set({ error: 'No files selected' });
      return;
    }
    
    try {
      set({ isProcessing: true, error: null, progress: DEFAULT_PROGRESS });
      
      // Connect WebSocket for real-time updates
      connectWebSocket();
      
      // Upload files and start review
      const formData = new FormData();
      
      // Add all input files
      filesToProcess.forEach((f) => {
        formData.append('files', f);
      });
      
      formData.append('config', JSON.stringify(config));
      
      // Add reference files if any
      referenceFiles.forEach((refFile) => {
        formData.append('reference_files', refFile);
      });
      
      const response = await fetch('http://localhost:8000/api/review/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Failed to start review');
      }
      
      const data = await response.json();
      
      // CRITICAL: Set reviewId and clear old data
      console.log('✅ Upload success! New review_id:', data.review_id);
      set({ 
        reviewId: data.review_id,
        results: null,  // Clear old results
        error: null
      });
      
    } catch (error: any) {
      set({ 
        error: error.message || 'Failed to start review',
        isProcessing: false 
      });
    }
  },
  
  updateProgress: (progress) => set((state) => ({
    progress: { ...state.progress, ...progress }
  })),
  
  updateAgent: (agentKey, status) => set((state) => ({
    agents: state.agents.map(agent =>
      agent.key === agentKey ? { ...agent, status } : agent
    )
  })),
  
  setResults: (results, outputDir) => set({
    results,
    outputDir,
    isProcessing: false,
    progress: { ...DEFAULT_PROGRESS, progress: 100, status: 'Complete!' }
  }),
  
  setError: (error) => set({ error, isProcessing: false }),
  
  reset: () => {
    // Disconnect WebSocket before reset
    const { disconnectWebSocket } = get();
    disconnectWebSocket();
    
    set({
      reviewId: null,
      file: null,
      referenceFiles: [],
      config: DEFAULT_CONFIG,
      progress: DEFAULT_PROGRESS,
      agents: [],
      results: null,
      outputDir: null,
      isProcessing: false,
      error: null,
    });
  },
  
  connectWebSocket: () => {
    const { ws, disconnectWebSocket } = get();
    
    // Close existing connection
    if (ws) {
      disconnectWebSocket();
    }
    
    const newWs = new WebSocket('ws://localhost:8000/ws');
    
    newWs.onopen = () => {
      console.log('WebSocket connected');
    };
    
    newWs.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'progress':
          // Extract agent counts from status message
          const completedMatch = data.status.match(/\((\d+)\/(\d+)\)/);
          let completedAgents = get().progress.completedAgents;
          let totalAgents = get().progress.totalAgents;
          
          if (completedMatch) {
            completedAgents = parseInt(completedMatch[1]);
            totalAgents = parseInt(completedMatch[2]);
          }
          
          set((state) => ({
            progress: {
              progress: data.progress,
              status: data.status,
              currentAgent: data.agent?.name || state.progress.currentAgent,
              completedAgents,
              totalAgents,
            }
          }));
          
          // Update agent status if agent info is present
          if (data.agent) {
            const agents = get().agents;
            const agentKey = data.agent.name.toLowerCase().replace(/\s+/g, '_');
            
            // Check if agent exists in list
            const existingAgent = agents.find(a => a.key === agentKey);
            
            if (existingAgent) {
              // Update existing agent
              get().updateAgent(agentKey, data.agent.status);
            } else {
              // Add new agent to list (in case it wasn't in initial list)
              const newAgent = {
                key: agentKey,
                name: data.agent.name,
                icon: data.agent.icon,
                status: data.agent.status as 'pending' | 'analyzing' | 'completed',
              };
              set((state) => ({
                agents: [...state.agents, newAgent]
              }));
            }
          }
          break;
          
        case 'agents_selected':
          const agents = data.agents.map((key: string) => ({
            key,
            name: key.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
            icon: getAgentIcon(key),
            status: 'pending' as const,
          }));
          
          // Update with document type info if available
          const progressUpdate: any = { totalAgents: agents.length };
          if (data.document_type) {
            console.log(`📄 Document type: ${data.document_type}`);
          }
          
          set({ agents, progress: { ...get().progress, ...progressUpdate } });
          break;
          
        case 'complete':
          console.log('🎉 Review complete! Fetching results for:', data.review_id);
          
          // Wait a moment for backend to finish writing files
          setTimeout(() => {
            fetch(`http://localhost:8000/api/review/${data.review_id}/results`)
              .then(res => {
                if (!res.ok) {
                  throw new Error(`HTTP ${res.status}: ${res.statusText}`);
                }
                return res.json();
              })
              .then(results => {
                console.log('✅ Results loaded:', results);
                get().setResults(results, data.output_dir);
              })
              .catch(error => {
                console.error('❌ Failed to load results:', error);
                get().setError(`Failed to load results: ${error.message}`);
              });
          }, 1000);
          break;
          
        case 'error':
          set({ error: data.error, isProcessing: false });
          break;
      }
    };
    
    newWs.onerror = (error) => {
      console.error('WebSocket error:', error);
      set({ error: 'Connection error' });
    };
    
    newWs.onclose = () => {
      console.log('WebSocket disconnected');
    };
    
    set({ ws: newWs });
  },
  
  disconnectWebSocket: () => {
    const { ws } = get();
    if (ws) {
      ws.close();
      set({ ws: null });
    }
  },
}));

// Helper function
function getAgentIcon(key: string): string {
  const icons: Record<string, string> = {
    style_editor: '🎨',
    consistency_checker: '🔍',
    fact_checker: '✓',
    logic_checker: '🧠',
    technical_expert: '⚙️',
    subject_matter_expert: '🎓',
    business_analyst: '💼',
    financial_analyst: '💰',
    legal_expert: '⚖️',
    data_validator: '📊',
    web_researcher: '🌐',
    academic_researcher: '📚',
  };
  return icons[key] || '🤖';
}

