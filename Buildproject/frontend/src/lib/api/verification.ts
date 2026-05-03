/**
 * Verification API Service
 * Handles report verification operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from './client';
import { handleApiError, buildQueryString } from './utils';
import type {
  VerificationResponse,
  VerificationHistoryResponse,
  PendingVerificationItem,
  PaginatedResponse,
  VerificationStats,
} from '@/types/api';

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Trigger AI verification for a report
 */
export async function verifyReport(
  reportId: string,
  forceRevalidation: boolean = false
): Promise<VerificationResponse> {
  try {
    const response = await apiClient.post<VerificationResponse>(
      `/verification/reports/${reportId}/verify`,
      { force_revalidation: forceRevalidation }
    );
    return response.data;
  } catch (error) {
    const message = handleApiError(error);
    throw new Error(message);
  }
}

/**
 * Get verification history for a report
 */
export async function getVerificationHistory(
  reportId: string
): Promise<VerificationHistoryResponse> {
  try {
    const response = await apiClient.get<VerificationHistoryResponse>(
      `/verification/reports/${reportId}`
    );
    return response.data;
  } catch (error) {
    const message = handleApiError(error);
    throw new Error(message);
  }
}

/**
 * Get list of pending verifications (paginated)
 */
export async function getPendingVerifications(
  page: number = 1,
  limit: number = 20
): Promise<PaginatedResponse<PendingVerificationItem>> {
  try {
    const queryString = buildQueryString({ page, limit });
    const response = await apiClient.get<PaginatedResponse<PendingVerificationItem>>(
      `/verification/pending${queryString}`
    );
    return response.data;
  } catch (error) {
    const message = handleApiError(error);
    throw new Error(message);
  }
}

/**
 * Get verification statistics
 */
export async function getVerificationStats(): Promise<VerificationStats> {
  try {
    const response = await apiClient.get<VerificationStats>('/verification/stats');
    return response.data;
  } catch (error) {
    const message = handleApiError(error);
    throw new Error(message);
  }
}

// ============================================================================
// REACT QUERY HOOKS
// ============================================================================

/**
 * Hook to trigger report verification
 * 
 * @example
 * const { mutate, isPending } = useVerifyReport();
 * 
 * mutate({ reportId: 'report-123', forceRevalidation: false });
 */
export function useVerifyReport() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ reportId, forceRevalidation = false }: { 
      reportId: string; 
      forceRevalidation?: boolean;
    }) => verifyReport(reportId, forceRevalidation),
    onSuccess: (data, variables) => {
      // Invalidate and refetch related queries
      queryClient.invalidateQueries({ queryKey: ['report', variables.reportId] });
      queryClient.invalidateQueries({ queryKey: ['verification', 'history', variables.reportId] });
      queryClient.invalidateQueries({ queryKey: ['verification', 'pending'] });
      queryClient.invalidateQueries({ queryKey: ['verification', 'stats'] });
      
      // If report has incident_id, invalidate incident queries
      if (data.report_id) {
        queryClient.invalidateQueries({ queryKey: ['reports'] });
      }
    },
    onError: (error) => {
      console.error('Failed to verify report:', error);
    },
  });
}

/**
 * Hook to fetch verification history for a report
 * 
 * @param reportId - The report ID
 * @param options - Query options
 * 
 * @example
 * const { data, isLoading } = useVerificationHistory('report-123');
 */
export function useVerificationHistory(
  reportId: string,
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
) {
  return useQuery({
    queryKey: ['verification', 'history', reportId],
    queryFn: () => getVerificationHistory(reportId),
    enabled: options?.enabled !== false && !!reportId,
    refetchInterval: options?.refetchInterval,
    staleTime: 60000, // Consider data fresh for 1 minute
    retry: 2,
  });
}

/**
 * Hook to fetch pending verifications with pagination
 * 
 * @param page - Page number (1-indexed)
 * @param limit - Items per page
 * @param options - Query options
 * 
 * @example
 * const { data, isLoading } = usePendingVerifications(1, 20);
 */
export function usePendingVerifications(
  page: number = 1,
  limit: number = 20,
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
) {
  return useQuery({
    queryKey: ['verification', 'pending', page, limit],
    queryFn: () => getPendingVerifications(page, limit),
    enabled: options?.enabled !== false,
    refetchInterval: options?.refetchInterval || 30000, // Auto-refetch every 30s
    staleTime: 10000, // Consider data fresh for 10 seconds
    retry: 2,
  });
}

/**
 * Hook to fetch verification statistics
 * 
 * @param options - Query options
 * 
 * @example
 * const { data, isLoading } = useVerificationStats();
 */
export function useVerificationStats(
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
) {
  return useQuery({
    queryKey: ['verification', 'stats'],
    queryFn: getVerificationStats,
    enabled: options?.enabled !== false,
    refetchInterval: options?.refetchInterval || 60000, // Auto-refetch every minute
    staleTime: 30000, // Consider data fresh for 30 seconds
    retry: 2,
  });
}

/**
 * Hook to prefetch verification history
 */
export function usePrefetchVerificationHistory() {
  const queryClient = useQueryClient();
  
  return (reportId: string) => {
    queryClient.prefetchQuery({
      queryKey: ['verification', 'history', reportId],
      queryFn: () => getVerificationHistory(reportId),
      staleTime: 60000,
    });
  };
}

// Made with Bob