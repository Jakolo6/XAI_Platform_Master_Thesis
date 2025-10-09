'use client';

interface ConfusionMatrixChartProps {
  confusionMatrix: {
    tn: number;
    fp: number;
    fn: number;
    tp: number;
  };
}

export default function ConfusionMatrixChart({ confusionMatrix }: ConfusionMatrixChartProps) {
  const total = confusionMatrix.tn + confusionMatrix.fp + confusionMatrix.fn + confusionMatrix.tp;
  
  const data = [
    { label: 'TN', value: confusionMatrix.tn, color: 'bg-green-500', textColor: 'text-green-900', position: 'top-left' },
    { label: 'FP', value: confusionMatrix.fp, color: 'bg-red-500', textColor: 'text-red-900', position: 'top-right' },
    { label: 'FN', value: confusionMatrix.fn, color: 'bg-red-500', textColor: 'text-red-900', position: 'bottom-left' },
    { label: 'TP', value: confusionMatrix.tp, color: 'bg-green-500', textColor: 'text-green-900', position: 'bottom-right' },
  ];

  const getOpacity = (value: number) => {
    const percentage = (value / total) * 100;
    if (percentage > 80) return 'opacity-100';
    if (percentage > 50) return 'opacity-90';
    if (percentage > 20) return 'opacity-70';
    if (percentage > 5) return 'opacity-50';
    return 'opacity-30';
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Labels */}
      <div className="flex justify-center mb-4">
        <div className="text-center">
          <div className="text-sm font-semibold text-gray-700 mb-2">Predicted</div>
          <div className="flex space-x-8">
            <div className="text-sm text-gray-600">Negative</div>
            <div className="text-sm text-gray-600">Positive</div>
          </div>
        </div>
      </div>

      <div className="flex items-center">
        {/* Actual Label */}
        <div className="mr-4">
          <div className="text-sm font-semibold text-gray-700 transform -rotate-90 whitespace-nowrap">
            Actual
          </div>
        </div>

        {/* Matrix Grid */}
        <div className="flex-1">
          <div className="grid grid-cols-2 gap-4">
            {/* True Negative */}
            <div className={`${data[0].color} ${getOpacity(data[0].value)} rounded-lg p-8 text-center`}>
              <div className="text-4xl font-bold text-white mb-2">
                {data[0].value.toLocaleString()}
              </div>
              <div className="text-sm font-semibold text-white mb-1">{data[0].label}</div>
              <div className="text-xs text-white opacity-90">
                {((data[0].value / total) * 100).toFixed(1)}%
              </div>
            </div>

            {/* False Positive */}
            <div className={`${data[1].color} ${getOpacity(data[1].value)} rounded-lg p-8 text-center`}>
              <div className="text-4xl font-bold text-white mb-2">
                {data[1].value.toLocaleString()}
              </div>
              <div className="text-sm font-semibold text-white mb-1">{data[1].label}</div>
              <div className="text-xs text-white opacity-90">
                {((data[1].value / total) * 100).toFixed(1)}%
              </div>
            </div>

            {/* False Negative */}
            <div className={`${data[2].color} ${getOpacity(data[2].value)} rounded-lg p-8 text-center`}>
              <div className="text-4xl font-bold text-white mb-2">
                {data[2].value.toLocaleString()}
              </div>
              <div className="text-sm font-semibold text-white mb-1">{data[2].label}</div>
              <div className="text-xs text-white opacity-90">
                {((data[2].value / total) * 100).toFixed(1)}%
              </div>
            </div>

            {/* True Positive */}
            <div className={`${data[3].color} ${getOpacity(data[3].value)} rounded-lg p-8 text-center`}>
              <div className="text-4xl font-bold text-white mb-2">
                {data[3].value.toLocaleString()}
              </div>
              <div className="text-sm font-semibold text-white mb-1">{data[3].label}</div>
              <div className="text-xs text-white opacity-90">
                {((data[3].value / total) * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Legend */}
          <div className="mt-6 flex justify-center space-x-6 text-sm">
            <div className="flex items-center">
              <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
              <span className="text-gray-600">Correct Prediction</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-red-500 rounded mr-2"></div>
              <span className="text-gray-600">Incorrect Prediction</span>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-2 gap-4 text-center">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-2xl font-bold text-gray-900">
            {(((confusionMatrix.tn + confusionMatrix.tp) / total) * 100).toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">Overall Accuracy</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-2xl font-bold text-gray-900">
            {((confusionMatrix.fp / (confusionMatrix.fp + confusionMatrix.tn)) * 100).toFixed(2)}%
          </div>
          <div className="text-sm text-gray-600">False Positive Rate</div>
        </div>
      </div>
    </div>
  );
}
