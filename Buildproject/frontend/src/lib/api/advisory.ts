/**
 * Advisory API Service
 * Handles safety advisory operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from './client';
import { handleApiError, buildQueryString } from './utils';
import type {
  AdvisoryResponse,
  AdvisoryRequest,
  AdvisoryQueryParams,
} from '@/types/api';

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Get safety advisory for an incident (using query parameters)
 */
export async function getAdvisory(
  incidentId: string,
  params?: AdvisoryQueryParams
): Promise<AdvisoryResponse> {
  try {
    const queryString = params ? buildQueryString(params) : '';
    const response = await apiClient.get<AdvisoryResponse>(
      `/advisory/${incidentId}${queryString}`
    );
    return response.data;
  } catch (error) {
    const message = handleApiError(error);
    throw new Error(message);
  }
}

/**
 * Get safety advisory for an incident (using request body)
 */
export async function getAdvisoryWithBody(
  request: AdvisoryRequest
): Promise<AdvisoryResponse> {
  try {
    const response = await apiClient.post<AdvisoryResponse>(
      '/advisory',
      request
    );
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
 * Hook to fetch safety advisory for an incident (GET with query params)
 * 
 * @param incidentId - The incident ID
 * @param params - Optional query parameters (user location, context)
 * @param options - Query options
 * 
 * @example
 * const { data, isLoading } = useAdvisory('incident-123', {
 *   user_latitude: -1.2921,
 *   user_longitude: 36.8219,
 *   user_context: 'at home'
 * });
 */
export function useAdvisory(
  incidentId: string,
  params?: AdvisoryQueryParams,
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
) {
  // Create a stable query key that includes params
  const queryKey = ['advisory', incidentId, params];
  
  return useQuery({
    queryKey,
    queryFn: () => getAdvisory(incidentId, params),
    enabled: options?.enabled !== false && !!incidentId,
    refetchInterval: options?.refetchInterval,
    staleTime: 60000, // Consider data fresh for 1 minute
    retry: 2,
  });
}

/**
 * Hook to get safety advisory using POST request with body
 * Useful when you need to send more complex data or prefer POST over GET
 * 
 * @example
 * const { mutate, isPending, data } = useAdvisoryWithBody();
 * 
 * mutate({
 *   incident_id: 'incident-123',
 *   user_latitude: -1.2921,
 *   user_longitude: 36.8219,
 *   user_context: 'at home with family'
 * });
 */
export function useAdvisoryWithBody() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: getAdvisoryWithBody,
    onSuccess: (data, variables) => {
      // Cache the advisory result
      queryClient.setQueryData(
        ['advisory', variables.incident_id, {
          user_latitude: variables.user_latitude,
          user_longitude: variables.user_longitude,
          user_context: variables.user_context,
        }],
        data
      );
      
      // Also cache without params for general access
      queryClient.setQueryData(
        ['advisory', variables.incident_id],
        data
      );
    },
    onError: (error) => {
      console.error('Failed to get advisory:', error);
    },
  });
}

/**
 * Hook to prefetch advisory for an incident
 */
export function usePrefetchAdvisory() {
  const queryClient = useQueryClient();
  
  return (incidentId: string, params?: AdvisoryQueryParams) => {
    queryClient.prefetchQuery({
      queryKey: ['advisory', incidentId, params],
      queryFn: () => getAdvisory(incidentId, params),
      staleTime: 60000,
    });
  };
}

/**
 * Hook to invalidate advisory cache for an incident
 * Useful when incident data changes and advisory needs to be refreshed
 */
export function useInvalidateAdvisory() {
  const queryClient = useQueryClient();
  
  return (incidentId: string) => {
    queryClient.invalidateQueries({ 
      queryKey: ['advisory', incidentId] 
    });
  };
}

// Made with Bob