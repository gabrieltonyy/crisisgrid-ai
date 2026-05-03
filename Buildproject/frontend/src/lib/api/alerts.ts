/**
 * Alerts API Service
 * Handles alert generation and retrieval
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from './client';
import { handleApiError } from './utils';
import type { AlertResponse } from '@/types/api';

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Generate alert for an incident
 */
export async function generateAlert(incidentId: string): Promise<AlertResponse> {
  try {
    const response = await apiClient.post<AlertResponse>(
      `/alerts/generate/${incidentId}`
    );
    return response.data;
  } catch (error) {
    const message = handleApiError(error);
    throw new Error(message);
  }
}

/**
 * Get alerts for an incident
 */
export async function getAlerts(incidentId: string): Promise<AlertResponse[]> {
  try {
    const response = await apiClient.get<AlertResponse[]>(
      `/alerts/${incidentId}`
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
 * Hook to generate an alert for an incident
 * 
 * @example
 * const { mutate, isPending } = useGenerateAlert();
 * 
 * mutate('incident-123');
 */
export function useGenerateAlert() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: generateAlert,
    onSuccess: (data, incidentId) => {
      // Invalidate alerts list for this incident
      queryClient.invalidateQueries({ queryKey: ['alerts', incidentId] });
      
      // Invalidate incident queries
      queryClient.invalidateQueries({ queryKey: ['incident', incidentId] });
      
      // Invalidate general alerts queries
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      
      // Set the new alert in cache
      queryClient.setQueryData(['alert', data.id], data);
    },
    onError: (error) => {
      console.error('Failed to generate alert:', error);
    },
  });
}

/**
 * Hook to fetch alerts for an incident
 * 
 * @param incidentId - The incident ID
 * @param options - Query options
 * 
 * @example
 * const { data, isLoading } = useAlerts('incident-123');
 */
export function useAlerts(
  incidentId: string,
  options?: {
    enabled?: boolean;
    refetchInterval?: number;
  }
) {
  return useQuery({
    queryKey: ['alerts', incidentId],
    queryFn: () => getAlerts(incidentId),
    enabled: options?.enabled !== false && !!incidentId,
    refetchInterval: options?.refetchInterval,
    staleTime: 30000, // Consider data fresh for 30 seconds
    retry: 2,
  });
}

/**
 * Hook to fetch a single alert by ID (from cache or refetch)
 * 
 * @param alertId - The alert ID
 * @param incidentId - The incident ID (for refetching if needed)
 * 
 * @example
 * const { data, isLoading } = useAlert('alert-123', 'incident-123');
 */
export function useAlert(
  alertId: string,
  incidentId: string,
  options?: {
    enabled?: boolean;
  }
) {
  return useQuery({
    queryKey: ['alert', alertId],
    queryFn: async () => {
      // Fetch all alerts for the incident and find the specific one
      const alerts = await getAlerts(incidentId);
      const alert = alerts.find(a => a.id === alertId);
      if (!alert) {
        throw new Error(`Alert ${alertId} not found`);
      }
      return alert;
    },
    enabled: options?.enabled !== false && !!alertId && !!incidentId,
    staleTime: 30000,
    retry: 2,
  });
}

/**
 * Hook to prefetch alerts for an incident
 */
export function usePrefetchAlerts() {
  const queryClient = useQueryClient();
  
  return (incidentId: string) => {
    queryClient.prefetchQuery({
      queryKey: ['alerts', incidentId],
      queryFn: () => getAlerts(incidentId),
      staleTime: 30000,
    });
  };
}

// Made with Bob