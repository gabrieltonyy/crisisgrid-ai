/**
 * Health API Service
 * Handles health check operations
 */

import { useQuery } from '@tanstack/react-query';
import apiClient from './client';
import { handleApiError } from './utils';
import type { HealthResponse } from '@/types/api';

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Check API health status
 */
export async function checkHealth(): Promise<HealthResponse> {
  try {
    const response = await apiClient.get<HealthResponse>('/health');
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
 * Hook to check API health status
 * 
 * @param options - Query options
 * 
 * @example
 * const { data, isLoading, error } = useHealth({
 *   refetchInterval: 30000 // Check every 30 seconds
 * });
 */
export function useHealth(
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
    retry?: boolean | number;
  }
) {
  return useQuery({
    queryKey: ['health'],
    queryFn: checkHealth,
    enabled: options?.enabled !== false,
    refetchInterval: options?.refetchInterval || 60000, // Default: check every minute
    staleTime: 30000, // Consider data fresh for 30 seconds
    retry: options?.retry !== undefined ? options.retry : 1, // Only retry once for health checks
    refetchOnWindowFocus: true, // Recheck when user returns to tab
    refetchOnReconnect: true, // Recheck when network reconnects
  });
}

/**
 * Hook to check if API is healthy (returns boolean)
 * 
 * @example
 * const isHealthy = useIsHealthy();
 */
export function useIsHealthy(): boolean {
  const { data, isError } = useHealth({
    refetchInterval: 60000,
    retry: 1,
  });
  
  if (isError) return false;
  if (!data) return true; // Assume healthy if not yet loaded
  
  return data.status === 'healthy' || data.status === 'ok';
}

// Made with Bob