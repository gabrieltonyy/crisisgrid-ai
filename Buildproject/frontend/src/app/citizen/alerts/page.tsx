/**
 * Nearby Alerts Page
 * Displays nearby active alerts with map and list views
 */

'use client';

import { useState, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { useQuery } from '@tanstack/react-query';
import { Button, Select, Alert as AntAlert, Segmented } from 'antd';
import { 
  ReloadOutlined, 
  EnvironmentOutlined,
  UnorderedListOutlined
} from '@ant-design/icons';
import { AlertCard } from '@/components/cards/AlertCard';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { EmptyState } from '@/components/ui/EmptyState';
import { useGeolocation } from '@/hooks/useGeolocation';
import apiClient from '@/lib/api/client';
import type { AlertResponse } from '@/types/api';
import { formatDistanceToNow } from 'date-fns';

const AlertsMap = dynamic(
  () => import('@/components/maps/AlertsMap').then((mod) => mod.AlertsMap),
  { ssr: false }
);

type ViewMode = 'map' | 'list';
type SortOption = 'distance' | 'time' | 'severity';

const CRISIS_TYPE_OPTIONS = [
  { label: 'All Types', value: 'all' },
  { label: 'Fire', value: 'FIRE' },
  { label: 'Flood', value: 'FLOOD' },
  { label: 'Wildlife', value: 'WILDLIFE' },
  { label: 'Accident', value: 'ACCIDENT' },
  { label: 'Security', value: 'SECURITY' },
  { label: 'Health', value: 'HEALTH' },
  { label: 'Landslide', value: 'LANDSLIDE' },
  { label: 'Hazardous Spill', value: 'HAZARDOUS_SPILL' },
  { label: 'Other', value: 'OTHER' },
];

const SEVERITY_OPTIONS = [
  { label: 'All Severities', value: 'all' },
  { label: 'Critical', value: 'CRITICAL' },
  { label: 'High', value: 'HIGH' },
  { label: 'Medium', value: 'MEDIUM' },
  { label: 'Low', value: 'LOW' },
];

/**
 * Calculate distance between two coordinates
 */
function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371e3;
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

export default function AlertsPage() {
  const [viewMode, setViewMode] = useState<ViewMode>('map');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [crisisTypeFilter, setCrisisTypeFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<SortOption>('distance');

  // Get user location
  const {
    latitude: userLat,
    longitude: userLon,
    error: locationError,
  } = useGeolocation({ watch: false });

  // Fetch alerts
  const {
    data: alerts = [],
    isLoading: alertsLoading,
    error: alertsError,
    refetch,
    dataUpdatedAt,
  } = useQuery<AlertResponse[]>({
    queryKey: ['alerts', 'nearby'],
    queryFn: async () => {
      const response = await apiClient.get('/alerts');
      return response.data;
    },
    refetchInterval: 30000, // Auto-refresh every 30 seconds
    staleTime: 30000,
  });

  // Filter and sort alerts
  const filteredAndSortedAlerts = useMemo(() => {
    let filtered = [...alerts];

    // Filter by severity
    if (severityFilter !== 'all') {
      filtered = filtered.filter((alert) => alert.severity === severityFilter);
    }

    // Filter by crisis type
    if (crisisTypeFilter !== 'all') {
      filtered = filtered.filter((alert) => alert.crisis_type === crisisTypeFilter);
    }

    // Filter only active alerts
    filtered = filtered.filter((alert) => alert.status === 'ACTIVE');

    // Add distance if user location available
    if (userLat !== null && userLon !== null) {
      filtered = filtered.map((alert) => ({
        ...alert,
        distance: calculateDistance(userLat, userLon, alert.latitude, alert.longitude),
      }));
    }

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === 'distance' && 'distance' in a && 'distance' in b) {
        return (a.distance as number) - (b.distance as number);
      } else if (sortBy === 'time') {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      } else if (sortBy === 'severity') {
        const severityOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
        return severityOrder[a.severity] - severityOrder[b.severity];
      }
      return 0;
    });

    return filtered;
  }, [alerts, severityFilter, crisisTypeFilter, sortBy, userLat, userLon]);

  // Get severity counts
  const severityCounts = useMemo(() => {
    return {
      CRITICAL: filteredAndSortedAlerts.filter((a) => a.severity === 'CRITICAL').length,
      HIGH: filteredAndSortedAlerts.filter((a) => a.severity === 'HIGH').length,
      MEDIUM: filteredAndSortedAlerts.filter((a) => a.severity === 'MEDIUM').length,
      LOW: filteredAndSortedAlerts.filter((a) => a.severity === 'LOW').length,
    };
  }, [filteredAndSortedAlerts]);

  const isLoading = alertsLoading;
  const hasError = alertsError;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Nearby Alerts</h1>
        <p className="text-gray-600">
          View active alerts in your area and stay informed about potential hazards
        </p>
      </div>

      {/* Location Status */}
      {locationError && (
        <AntAlert
          message="Location Access Required"
          description="Please enable location access to see nearby alerts and distances."
          type="warning"
          showIcon
          className="mb-6"
        />
      )}

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
          {/* Left side: Filters */}
          <div className="flex flex-col sm:flex-row gap-3 flex-1 w-full lg:w-auto">
            <Select
              value={severityFilter}
              onChange={setSeverityFilter}
              options={SEVERITY_OPTIONS}
              className="w-full sm:w-48"
              placeholder="Filter by severity"
            />
            <Select
              value={crisisTypeFilter}
              onChange={setCrisisTypeFilter}
              options={CRISIS_TYPE_OPTIONS}
              className="w-full sm:w-48"
              placeholder="Filter by type"
            />
            <Select
              value={sortBy}
              onChange={setSortBy}
              className="w-full sm:w-48"
              placeholder="Sort by"
              options={[
                { label: 'Distance', value: 'distance', disabled: !userLat },
                { label: 'Time', value: 'time' },
                { label: 'Severity', value: 'severity' },
              ]}
            />
          </div>

          {/* Right side: View toggle and refresh */}
          <div className="flex gap-3 items-center w-full lg:w-auto justify-between lg:justify-end">
            <Segmented
              value={viewMode}
              onChange={(value) => setViewMode(value as ViewMode)}
              options={[
                { label: 'Map', value: 'map', icon: <EnvironmentOutlined /> },
                { label: 'List', value: 'list', icon: <UnorderedListOutlined /> },
              ]}
            />
            <Button
              icon={<ReloadOutlined />}
              onClick={() => refetch()}
              loading={isLoading}
            >
              Refresh
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-sm p-4 text-center">
          <div className="text-2xl font-bold text-gray-900">{filteredAndSortedAlerts.length}</div>
          <div className="text-sm text-gray-600">Total Alerts</div>
        </div>
        <div className="bg-red-50 rounded-lg shadow-sm p-4 text-center border border-red-200">
          <div className="text-2xl font-bold text-red-600">{severityCounts.CRITICAL}</div>
          <div className="text-sm text-red-700">Critical</div>
        </div>
        <div className="bg-orange-50 rounded-lg shadow-sm p-4 text-center border border-orange-200">
          <div className="text-2xl font-bold text-orange-600">{severityCounts.HIGH}</div>
          <div className="text-sm text-orange-700">High</div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4 text-center">
          <div className="text-xs text-gray-500">Last Updated</div>
          <div className="text-sm font-medium text-gray-900">
            {dataUpdatedAt ? formatDistanceToNow(dataUpdatedAt, { addSuffix: true }) : 'Never'}
          </div>
        </div>
      </div>

      {/* Content */}
      {isLoading && (
        <div className="flex justify-center items-center py-20">
          <LoadingSpinner size="large" message="Loading nearby alerts..." />
        </div>
      )}

      {hasError && !isLoading && (
        <ErrorAlert
          title="Failed to Load Alerts"
          message="Unable to fetch nearby alerts. Please try again."
          onRetry={() => refetch()}
        />
      )}

      {!isLoading && !hasError && filteredAndSortedAlerts.length === 0 && (
        <EmptyState
          title="No Alerts Found"
          description={
            severityFilter !== 'all' || crisisTypeFilter !== 'all'
              ? 'No alerts match your current filters. Try adjusting the filters above.'
              : 'There are no active alerts in your area at this time.'
          }
          icon="✅"
        />
      )}

      {!isLoading && !hasError && filteredAndSortedAlerts.length > 0 && (
        <>
          {/* Map View */}
          {viewMode === 'map' && (
            <div className="bg-white rounded-lg shadow-md p-4">
              <AlertsMap
                alerts={filteredAndSortedAlerts}
                userLocation={
                  userLat && userLon ? { latitude: userLat, longitude: userLon } : undefined
                }
                className="h-[600px] w-full rounded-lg"
              />
            </div>
          )}

          {/* List View */}
          {viewMode === 'list' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredAndSortedAlerts.map((alert) => (
                <AlertCard
                  key={alert.id}
                  alert={alert}
                  userLocation={
                    userLat && userLon ? { latitude: userLat, longitude: userLon } : undefined
                  }
                  onViewMap={() => setViewMode('map')}
                />
              ))}
            </div>
          )}
        </>
      )}

      {/* Info Footer */}
      <div className="mt-8 rounded-lg border border-sky-200 bg-sky-50 p-4">
        <h3 className="mb-2 text-sm font-semibold text-sky-950">Operational Tips</h3>
        <ul className="list-disc space-y-1 pl-5 text-sm text-sky-900">
          <li>Alerts are automatically refreshed every 30 seconds</li>
          <li>Enable location access to see distances and sort by proximity</li>
          <li>Click on map markers to view alert details</li>
          <li>Use filters to focus on specific severity levels or crisis types</li>
          <li>Critical alerts require immediate attention</li>
        </ul>
      </div>
    </div>
  );
}

// Made with Bob
