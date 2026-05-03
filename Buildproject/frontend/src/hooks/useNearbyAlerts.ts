/**
 * Nearby Alerts Hook
 * Fetches and filters alerts based on user location
 */

import { useQuery } from '@tanstack/react-query';
import { useGeolocation } from './useGeolocation';
import type { AlertResponse } from '@/types/api';

export interface NearbyAlert extends AlertResponse {
  distance?: number; // Distance in meters
}

export interface UseNearbyAlertsOptions {
  maxDistance?: number; // Maximum distance in meters
  autoRefetch?: boolean;
  refetchInterval?: number;
  enabled?: boolean;
}

/**
 * Calculate distance between two coordinates using Haversine formula
 * Returns distance in meters
 */
function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371e3; // Earth's radius in meters
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;
}

/**
 * Format distance for display
 */
export function formatDistance(meters: number): string {
  if (meters < 1000) {
    return `${Math.round(meters)}m`;
  }
  return `${(meters / 1000).toFixed(1)}km`;
}

/**
 * Hook to fetch alerts near user's location
 */
export function useNearbyAlerts(options: UseNearbyAlertsOptions = {}) {
  const {
    maxDistance = 50000, // 50km default
    autoRefetch = true,
    refetchInterval = 30000, // 30 seconds
    enabled = true,
  } = options;

  // Get user's location
  const {
    latitude: userLat,
    longitude: userLon,
    loading: locationLoading,
    error: locationError,
  } = useGeolocation({ watch: false });

  // Fetch all active alerts
  // Note: In a real implementation, this would be an API endpoint that accepts location params
  const {
    data: allAlerts,
    isLoading: alertsLoading,
    error: alertsError,
    refetch,
  } = useQuery<AlertResponse[]>({
    queryKey: ['alerts', 'active'],
    queryFn: async () => {
      // This is a placeholder - in reality, you'd call your API
      // For now, return empty array since we don't have a global alerts endpoint
      return [];
    },
    enabled: enabled && userLat !== null && userLon !== null,
    refetchInterval: autoRefetch ? refetchInterval : false,
    staleTime: 30000,
  });

  // Filter and sort alerts by distance
  const nearbyAlerts: NearbyAlert[] = React.useMemo(() => {
    if (!allAlerts || userLat === null || userLon === null) {
      return [];
    }

    return allAlerts
      .map((alert) => {
        const distance = calculateDistance(
          userLat,
          userLon,
          alert.latitude,
          alert.longitude
        );

        return {
          ...alert,
          distance,
        };
      })
      .filter((alert) => alert.distance! <= maxDistance)
      .sort((a, b) => a.distance! - b.distance!);
  }, [allAlerts, userLat, userLon, maxDistance]);

  // Get alerts by severity
  const alertsBySeverity = React.useMemo(() => {
    return {
      CRITICAL: nearbyAlerts.filter((a) => a.severity === 'CRITICAL'),
      HIGH: nearbyAlerts.filter((a) => a.severity === 'HIGH'),
      MEDIUM: nearbyAlerts.filter((a) => a.severity === 'MEDIUM'),
      LOW: nearbyAlerts.filter((a) => a.severity === 'LOW'),
    };
  }, [nearbyAlerts]);

  // Get closest alert
  const closestAlert = nearbyAlerts.length > 0 ? nearbyAlerts[0] : null;

  // Get critical alerts count
  const criticalCount = alertsBySeverity.CRITICAL.length;

  return {
    alerts: nearbyAlerts,
    alertsBySeverity,
    closestAlert,
    criticalCount,
    totalCount: nearbyAlerts.length,
    isLoading: locationLoading || alertsLoading,
    error: locationError || (alertsError as Error | null),
    userLocation: userLat && userLon ? { latitude: userLat, longitude: userLon } : null,
    refetch,
    formatDistance,
  };
}

// Re-export React for the useMemo hook
import React from 'react';

// Made with Bob