/**
 * Error Fallback Component
 * Reusable error display component for specific sections
 */

'use client';

import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorFallbackProps {
  error?: Error | string;
  onRetry?: () => void;
  title?: string;
  message?: string;
  showDetails?: boolean;
}

export default function ErrorFallback({
  error,
  onRetry,
  title = 'Something went wrong',
  message = 'An error occurred while loading this content.',
  showDetails = false,
}: ErrorFallbackProps) {
  const errorMessage = error instanceof Error ? error.message : error;

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6">
      {/* Icon and Title */}
      <div className="flex items-start gap-3 mb-4">
        <div className="flex-shrink-0">
          <AlertCircle className="h-6 w-6 text-red-600" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-red-900">{title}</h3>
          <p className="text-sm text-red-700 mt-1">{message}</p>
        </div>
      </div>

      {/* Error Details */}
      {showDetails && errorMessage && (
        <div className="mb-4 p-3 bg-red-100 rounded border border-red-300">
          <p className="text-sm text-red-800 font-mono">{errorMessage}</p>
        </div>
      )}

      {/* Retry Button */}
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Try Again
        </button>
      )}
    </div>
  );
}

/**
 * Loading Error Component
 * For data loading failures
 */
export function LoadingError({
  onRetry,
  resource = 'data',
}: {
  onRetry?: () => void;
  resource?: string;
}) {
  return (
    <ErrorFallback
      title="Failed to load"
      message={`We couldn't load the ${resource}. Please try again.`}
      onRetry={onRetry}
    />
  );
}

/**
 * Network Error Component
 * For network/API failures
 */
export function NetworkError({ onRetry }: { onRetry?: () => void }) {
  return (
    <ErrorFallback
      title="Network Error"
      message="Unable to connect to the server. Please check your connection and try again."
      onRetry={onRetry}
    />
  );
}

/**
 * Not Found Error Component
 * For 404 errors
 */
export function NotFoundError({
  resource = 'resource',
}: {
  resource?: string;
}) {
  return (
    <ErrorFallback
      title="Not Found"
      message={`The ${resource} you're looking for doesn't exist or has been removed.`}
    />
  );
}

/**
 * Permission Error Component
 * For 403 errors
 */
export function PermissionError() {
  return (
    <ErrorFallback
      title="Access Denied"
      message="You don't have permission to access this resource."
    />
  );
}
