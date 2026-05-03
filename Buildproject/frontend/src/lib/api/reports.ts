/**
 * Reports API Service
 * Handles crisis report submission and retrieval
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from './client';
import { handleApiError } from './utils';
import type {
  CreateReportRequest,
  ReportResponse,
  ReportSubmissionResponse,
} from '@/types/api';

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Create a new crisis report
 */
export async function createReport(
  data: CreateReportRequest
): Promise<ReportSubmissionResponse> {
  try {
    const response = await apiClient.post<ReportSubmissionResponse>(
      '/reports',
      data
    );
    return response.data;
  } catch (error) {
    const message = handleApiError(error);
    throw new Error(message);
  }
}

/**
 * Get all reports
 */
export async function getReports(): Promise<ReportResponse[]> {
  try {
    const response = await apiClient.get<ReportResponse[]>('/reports');
    return response.data;
  } catch (error) {
    const message = handleApiError(error);
    throw new Error(message);
  }
}

/**
 * Get reports submitted by the authenticated user
 */
export async function getMyReports(): Promise<ReportResponse[]> {
  try {
    const response = await apiClient.get<ReportResponse[]>('/reports/me');
    return response.data;
  } catch (error) {
    const message = handleApiError(error);
    throw new Error(message);
  }
}

/**
 * Get a report by ID
 */
export async function getReport(reportId: string): Promise<ReportResponse> {
  try {
    const response = await apiClient.get<ReportResponse>(`/reports/${reportId}`);
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
 * Hook to create a new crisis report
 * 
 * @example
 * const { mutate, isPending, error } = useCreateReport();
 * 
 * mutate({
 *   crisis_type: 'FIRE',
 *   description: 'Large fire visible',
 *   latitude: -1.2921,
 *   longitude: 36.8219,
 * });
 */
export function useCreateReport() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createReport,
    onSuccess: (data) => {
      // Invalidate reports list queries
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      
      // Set the new report in cache
      queryClient.setQueryData(['report', data.report.id], data.report);
      
      // If report has incident_id, invalidate incident queries
      if (data.report.incident_id) {
        queryClient.invalidateQueries({ 
          queryKey: ['incident', data.report.incident_id] 
        });
      }
    },
    onError: (error) => {
      console.error('Failed to create report:', error);
    },
  });
}

/**
 * Hook to fetch a report by ID
 * 
 * @param reportId - The report ID to fetch
 * @param options - Query options
 * 
 * @example
 * const { data, isLoading, error } = useReport('report-id-123');
 */
export function useReport(
  reportId: string,
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
) {
  return useQuery({
    queryKey: ['report', reportId],
    queryFn: () => getReport(reportId),
    enabled: options?.enabled !== false && !!reportId,
    refetchInterval: options?.refetchInterval,
    staleTime: 30000, // Consider data fresh for 30 seconds
    retry: 2,
  });
}

/**
 * Hook to fetch all reports
 *
 * @param options - Query options
 *
 * @example
 * const { data, isLoading, error } = useReports();
 */
export function useReports(
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
) {
  return useQuery({
    queryKey: ['reports'],
    queryFn: getReports,
    enabled: options?.enabled !== false,
    refetchInterval: options?.refetchInterval,
    staleTime: 30000, // Consider data fresh for 30 seconds
    retry: 2,
  });
}

/**
 * Hook to fetch authenticated user's reports.
 */
export function useMyReports(
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
) {
  return useQuery({
    queryKey: ['my-reports'],
    queryFn: getMyReports,
    enabled: options?.enabled !== false,
    refetchInterval: options?.refetchInterval,
    staleTime: 30000,
    retry: 2,
  });
}

/**
 * Hook to prefetch a report (useful for optimistic UI)
 */
export function usePrefetchReport() {
  const queryClient = useQueryClient();
  
  return (reportId: string) => {
    queryClient.prefetchQuery({
      queryKey: ['report', reportId],
      queryFn: () => getReport(reportId),
      staleTime: 30000,
    });
  };
}

// Made with Bob
