/**
 * Export utilities for downloading data in various formats
 */

/**
 * Convert array of objects to CSV format
 */
export const convertToCSV = (data: any[]): string => {
  if (!data || data.length === 0) {
    return '';
  }

  // Get headers from first object
  const headers = Object.keys(data[0]);
  
  // Create CSV header row
  const headerRow = headers.join(',');
  
  // Create data rows
  const dataRows = data.map(item => {
    return headers.map(header => {
      const value = item[header];
      
      // Handle different data types
      if (value === null || value === undefined) {
        return '';
      }
      
      // Escape quotes and wrap in quotes if contains comma
      const stringValue = String(value);
      if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
        return `"${stringValue.replace(/"/g, '""')}"`;
      }
      
      return stringValue;
    }).join(',');
  });
  
  // Combine header and data
  return [headerRow, ...dataRows].join('\n');
};

/**
 * Download a file with given content
 */
export const downloadFile = (content: string, filename: string, mimeType: string = 'text/plain') => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Export SHAP explanation to CSV
 */
export const exportSHAPToCSV = (explanation: any, modelName: string = 'model') => {
  if (!explanation || !explanation.feature_importance) {
    throw new Error('Invalid SHAP explanation data');
  }

  const data = explanation.feature_importance.map((item: any, index: number) => ({
    rank: index + 1,
    feature: item.feature,
    importance: item.importance,
    mean_shap_value: item.mean_shap_value || item.importance,
  }));

  const csv = convertToCSV(data);
  const filename = `shap_${modelName}_${new Date().toISOString().split('T')[0]}.csv`;
  downloadFile(csv, filename, 'text/csv');
};

/**
 * Export LIME explanation to CSV
 */
export const exportLIMEToCSV = (explanation: any, modelName: string = 'model') => {
  if (!explanation || !explanation.feature_importance) {
    throw new Error('Invalid LIME explanation data');
  }

  const data = explanation.feature_importance.map((item: any, index: number) => ({
    rank: index + 1,
    feature: item.feature,
    weight: item.weight || item.importance,
    importance: item.importance || item.weight,
  }));

  const csv = convertToCSV(data);
  const filename = `lime_${modelName}_${new Date().toISOString().split('T')[0]}.csv`;
  downloadFile(csv, filename, 'text/csv');
};

/**
 * Export comparison data to CSV
 */
export const exportComparisonToCSV = (comparison: any, modelName: string = 'model') => {
  if (!comparison || !comparison.shap || !comparison.lime) {
    throw new Error('Invalid comparison data');
  }

  // Combine SHAP and LIME data
  const shapFeatures = new Map(
    comparison.shap.feature_importance.map((f: any) => [f.feature, f.importance])
  );
  const limeFeatures = new Map(
    comparison.lime.feature_importance.map((f: any) => [f.feature, f.weight || f.importance])
  );

  // Get all unique features
  const allFeatures = new Set([
    ...shapFeatures.keys(),
    ...limeFeatures.keys(),
  ]);

  const data = Array.from(allFeatures).map(feature => ({
    feature,
    shap_importance: shapFeatures.get(feature) || 0,
    lime_weight: limeFeatures.get(feature) || 0,
    in_both: shapFeatures.has(feature) && limeFeatures.has(feature) ? 'Yes' : 'No',
  }));

  // Sort by SHAP importance
  data.sort((a, b) => Number(b.shap_importance) - Number(a.shap_importance));

  const csv = convertToCSV(data);
  const filename = `comparison_${modelName}_${new Date().toISOString().split('T')[0]}.csv`;
  downloadFile(csv, filename, 'text/csv');
};

/**
 * Export quality metrics to CSV
 */
export const exportQualityMetricsToCSV = (metrics: any, modelName: string = 'model') => {
  if (!metrics || !metrics.quality_metrics) {
    throw new Error('Invalid quality metrics data');
  }

  const data = [
    {
      metric: 'Faithfulness',
      value: metrics.quality_metrics.faithfulness,
      description: 'How accurate the explanation is',
    },
    {
      metric: 'Robustness',
      value: metrics.quality_metrics.robustness,
      description: 'How stable across perturbations',
    },
    {
      metric: 'Complexity',
      value: metrics.quality_metrics.complexity,
      description: 'How simple the explanation is',
    },
  ];

  const csv = convertToCSV(data);
  const filename = `quality_metrics_${modelName}_${new Date().toISOString().split('T')[0]}.csv`;
  downloadFile(csv, filename, 'text/csv');
};

/**
 * Export all data as JSON
 */
export const exportAsJSON = (data: any, filename: string) => {
  const json = JSON.stringify(data, null, 2);
  downloadFile(json, filename, 'application/json');
};

/**
 * Export chart as image (requires canvas)
 */
export const exportChartAsImage = async (chartElement: HTMLElement, filename: string) => {
  try {
    // This would require html2canvas library
    // For now, just throw an error with instructions
    throw new Error('Chart export requires html2canvas library. Install with: npm install html2canvas');
  } catch (error) {
    console.error('Failed to export chart:', error);
    throw error;
  }
};
