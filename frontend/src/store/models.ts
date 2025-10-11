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
      set({ selectedModel: response.data, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch model',
        isLoading: false,
      });
    }
  },

  fetchModelMetrics: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await modelsAPI.getMetrics(id);
      set({ selectedMetrics: response.data, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch metrics',
        isLoading: false,
      });
    }
  },

  fetchLeaderboard: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await modelsAPI.getLeaderboard();
      set({ leaderboard: response.data, isLoading: false });
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
