import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatMetric(value: number | undefined, decimals: number = 3): string {
  if (value === undefined || value === null) return '-';
  return value.toFixed(decimals)
}

export function formatPercentage(value: number | undefined, decimals: number = 1): string {
  if (value === undefined || value === null) return '-';
  return `${(value * 100).toFixed(decimals)}%`
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`
  }
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}m ${remainingSeconds.toFixed(0)}s`
}

export function getModelTypeColor(modelType: string): string {
  const colors: Record<string, string> = {
    xgboost: 'bg-blue-500',
    lightgbm: 'bg-green-500',
    catboost: 'bg-purple-500',
    random_forest: 'bg-orange-500',
    logistic_regression: 'bg-gray-500',
    mlp: 'bg-pink-500',
  }
  return colors[modelType] || 'bg-gray-500'
}

export function getModelTypeLabel(modelType: string): string {
  const labels: Record<string, string> = {
    xgboost: 'XGBoost',
    lightgbm: 'LightGBM',
    catboost: 'CatBoost',
    random_forest: 'Random Forest',
    logistic_regression: 'Logistic Regression',
    mlp: 'MLP',
  }
  return labels[modelType] || modelType
}

export function getRankBadge(rank: number): string {
  const badges: Record<number, string> = {
    1: '🥇',
    2: '🥈',
    3: '🥉',
  }
  return badges[rank] || `#${rank}`
}
