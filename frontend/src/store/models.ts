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
      // Backend returns model with metrics merged in
      const modelData = response.data;
      
      console.log('Full response object:', response);
      console.log('response.data:', modelData);
      console.log('Keys in modelData:', Object.keys(modelData || {}));
      console.log('auc_roc from response:', modelData?.auc_roc);
      console.log('Type of modelData:', typeof modelData);
      
      // Extract metrics from the model data
      const metrics: any = {
        auc_roc: modelData?.auc_roc,
        auc_pr: modelData?.auc_pr,
        f1_score: modelData?.f1_score,
        precision: modelData?.precision,
        recall: modelData?.recall,
        accuracy: modelData?.accuracy,
        log_loss: modelData?.log_loss,
        brier_score: modelData?.brier_score,
        confusion_matrix: modelData?.confusion_matrix,
        expected_calibration_error: modelData?.expected_calibration_error,
        maximum_calibration_error: modelData?.maximum_calibration_error,
        roc_curve: modelData?.roc_curve,
        pr_curve: modelData?.pr_curve,
      };
      
      console.log('Extracted metrics:', metrics);
      
      set({ 
        selectedModel: modelData,
        selectedMetrics: metrics,
        isLoading: false 
      });
    } catch (error: any) {
      console.error('Error fetching model:', error);
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
