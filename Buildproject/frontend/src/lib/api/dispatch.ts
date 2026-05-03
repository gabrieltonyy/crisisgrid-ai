/**
 * Dispatch API Service
 * Handles authority dispatch operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from './client';
import { handleApiError } from './utils';
import type { DispatchResponse } from '@/types/api';

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Dispatch authorities for an incident
 */
export async function dispatchAuthority(
  incidentId: string
): Promise<DispatchResponse[]> {
  try {
    const response = await apiClient.post<DispatchResponse[]>(
      `/dispatch/${incidentId}`
    );
    return response.data;
  } catch (error) {
    const message = handleApiError(error);
    throw new Error(message);
  }
}

/**
 * Get dispatches for an incident
 */
export async function getDispatches(
  incidentId: string
): Promise<DispatchResponse[]> {
  try {
    const response = await apiClient.get<DispatchResponse[]>(
      `/dispatch/${incidentId}`
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
 * Hook to dispatch authorities for an incident
 * 
 * @example
 * const { mutate, isPending } = useDispatchAuthority();
 * 
 * mutate('incident-123');
 */
export function useDispatchAuthority() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: dispatchAuthority,
    onSuccess: (data, incidentId) => {
      // Invalidate dispatches list for this incident
      queryClient.invalidateQueries({ queryKey: ['dispatch', incidentId] });
      
      // Invalidate incident queries
      queryClient.invalidateQueries({ queryKey: ['incident', incidentId] });
      
      // Invalidate general dispatch queries
      queryClient.invalidateQueries({ queryKey: ['dispatches'] });
      
      // Set the dispatches in cache
      queryClient.setQueryData(['dispatch', incidentId], data);
    },
    onError: (error) => {
      console.error('Failed to dispatch authorities:', error);
    },
  });
}

/**
 * Hook to fetch dispatches for an incident
 * 
 * @param incidentId - The incident ID
 * @param options - Query options
 * 
 * @example
 * const { data, isLoading } = useDispatches('incident-123');
 */
export function useDispatches(
  incidentId: string,
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
) {
  return useQuery({
    queryKey: ['dispatch', incidentId],
    queryFn: () => getDispatches(incidentId),
    enabled: options?.enabled !== false && !!incidentId,
    refetchInterval: options?.refetchInterval,
    staleTime: 30000, // Consider data fresh for 30 seconds
    retry: 2,
  });
}

/**
 * Hook to fetch a single dispatch by ID (from cache or refetch)
 * 
 * @param dispatchId - The dispatch ID
 * @param incidentId - The incident ID (for refetching if needed)
 * 
 * @example
 * const { data, isLoading } = useDispatch('dispatch-123', 'incident-123');
 */
export function useDispatch(
  dispatchId: string,
  incidentId: string,
  options?: {
    enabled?: boolean;
  }
) {
  return useQuery({
    queryKey: ['dispatch', 'single', dispatchId],
    queryFn: async () => {
      // Fetch all dispatches for the incident and find the specific one
      const dispatches = await getDispatches(incidentId);
      const dispatch = dispatches.find(d => d.id === dispatchId);
      if (!dispatch) {
        throw new Error(`Dispatch ${dispatchId} not found`);
      }
      return dispatch;
    },
    enabled: options?.enabled !== false && !!dispatchId && !!incidentId,
    staleTime: 30000,
    retry: 2,
  });
}

/**
 * Hook to prefetch dispatches for an incident
 */
export function usePrefetchDispatches() {
  const queryClient = useQueryClient();
  
  return (incidentId: string) => {
    queryClient.prefetchQuery({
      queryKey: ['dispatch', incidentId],
      queryFn: () => getDispatches(incidentId),
      staleTime: 30000,
    });
  };
}

// Made with Bob