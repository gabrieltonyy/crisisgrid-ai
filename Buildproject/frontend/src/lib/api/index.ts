/**
 * API Services Index
 * Central export point for all API services and hooks
 */

// Export API client and utilities
export { default } from './client';
export { default as apiClient } from './client';
export { apiCall, handleApiError as handleClientApiError } from './client';
export type { ApiResponse } from './client';
export * from './utils';

// Export Reports API
export * from './reports';

// Export Verification API
export * from './verification';

// Export Alerts API
export * from './alerts';

// Export Dispatch API
export * from './dispatch';

// Export Advisory API
export * from './advisory';

// Export Health API
export * from './health';

// Export Auth API
export * from './auth';

// Re-export commonly used types for convenience
export type {
  CreateReportRequest,
  ReportResponse,
  ReportSubmissionResponse,
  VerificationResponse,
  VerificationHistoryResponse,
  PendingVerificationItem,
  VerificationStats,
  AlertResponse,
  DispatchResponse,
  AdvisoryResponse,
  AdvisoryRequest,
  AdvisoryQueryParams,
  HealthResponse,
  PaginatedResponse,
} from '@/types/api';

// Made with Bob
