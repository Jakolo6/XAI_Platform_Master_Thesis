import { create } from 'zustand';
import { modelsAPI } from '@/lib/api';

interface Model {
  id: string;
  name: string;
  model_type: string;
  version: string;
  status: string;
  dataset_id?: string;
  hyperparameters?: Record<string, any>;
  training_config?: Record<string, any>;
  training_time_seconds?: number;
  model_size_mb?: number;
  feature_importance?: Record<string, number>;
  created_at: string;
  updated_at: string;
}

interface ModelMetrics {
  auc_roc: number;
  auc_pr: number;
  f1_score: number;
  precision: number;
  recall: number;
  accuracy: number;
  log_loss: number;
  brier_score: number;
  confusion_matrix: {
    tn: number;
    fp: number;
    fn: number;
    tp: number;
  };
  expected_calibration_error: number;
  maximum_calibration_error: number;
  roc_curve?: {
    fpr: number[];
    tpr: number[];
    thresholds: number[];
  };
  pr_curve?: {
    precision: number[];
    recall: number[];
    thresholds: number[];
  };
}

interface LeaderboardEntry {
  rank: number;
  model_id: string;
  model_name: string;
  model_type: string;
  auc_roc: number;
  auc_pr: number;
  f1_score: number;
  accuracy: number;
  training_time_seconds: number;
}

interface ModelsState {
  models: Model[];
  selectedModel: Model | null;
  selectedMetrics: ModelMetrics | null;
  leaderboard: LeaderboardEntry[];
  isLoading: boolean;
  error: string | null;
  
  fetchModels: () => Promise<void>;
  fetchModelById: (id: string) => Promise<void>;
  fetchModelMetrics: (id: string) => Promise<void>;
  fetchLeaderboard: () => Promise<void>;
  clearError: () => void;
}

export const useModelsStore = create<ModelsState>((set) => ({
  models: [],
  selectedModel: null,
  selectedMetrics: null,
  leaderboard: [],
  isLoading: false,
  error: null,

  fetchModels: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await modelsAPI.getAll();
      set({ models: response.data, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch models',
        isLoading: false,
      });
    }
  },

  fetchModelById: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await modelsAPI.getById(id);
      const modelData = response.data;
      
      // Debug logging
      console.log('[MODELS STORE] Fetched model data:', {
        id: modelData?.id,
        hasAucRoc: 'auc_roc' in (modelData || {}),
        auc_roc: modelData?.auc_roc,
        f1_score: modelData?.f1_score,
        accuracy: modelData?.accuracy,
        allKeys: Object.keys(modelData || {})
      });
      
      // Set both selectedModel and selectedMetrics to the same data
      // The backend returns metrics merged into the model object
      set({ 
        selectedModel: modelData,
        selectedMetrics: modelData, // Metrics are part of the model data
        isLoading: false 
      });
      
      console.log('[MODELS STORE] State updated successfully');
    } catch (error: any) {
      console.error('[MODELS STORE] Error fetching model:', error);
      set({
        error: error.response?.data?.detail || 'Failed to fetch model',
        isLoading: false,
      });
    }
  },

  fetchModelMetrics: async (id: string) => {
    // Metrics are already fetched with the model, so this is a no-op
    // Kept for backwards compatibility
    return Promise.resolve();
  },

  fetchLeaderboard: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await modelsAPI.getLeaderboard();
      const models = response.data;
      
      // Transform models into leaderboard format
      const leaderboard: LeaderboardEntry[] = models
        .filter((m: any) => m.auc_roc !== null && m.auc_roc !== undefined)
        .map((model: any, index: number) => ({
          rank: index + 1,
          model_id: model.id,
          model_name: model.name || model.id,
          model_type: model.model_type,
          auc_roc: model.auc_roc || 0,
          auc_pr: model.auc_pr || 0,
          f1_score: model.f1_score || 0,
          accuracy: model.accuracy || 0,
          training_time_seconds: model.training_time_seconds || 0,
        }))
        .sort((a: LeaderboardEntry, b: LeaderboardEntry) => (b.auc_roc || 0) - (a.auc_roc || 0)); // Sort by AUC-ROC descending
      
      console.log('[MODELS STORE] Leaderboard data:', leaderboard);
      set({ leaderboard, isLoading: false });
    } catch (error: any) {
      console.error('Failed to fetch leaderboard:', error);
      set({
        error: error.response?.data?.detail || 'Failed to fetch leaderboard',
        isLoading: false,
        leaderboard: [] // Set empty array on error
      });
    }
  },

  clearError: () => set({ error: null }),
}));
