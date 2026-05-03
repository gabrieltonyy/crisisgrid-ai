/**
 * Alert Card Component
 * Displays alert summary in card format
 */

'use client';

import { Card, Button, Space, Tag } from 'antd';
import {
  EnvironmentOutlined,
  ClockCircleOutlined,
  ArrowRightOutlined,
  CompassOutlined
} from '@ant-design/icons';
import { CrisisIcon, getCrisisLabel, getCrisisColor } from '../ui/CrisisIcon';
import { SeverityBadge } from '../ui/SeverityBadge';
import type { AlertResponse, AlertStatus } from '@/types/api';
import { formatDistanceToNow } from 'date-fns';

interface AlertCardProps {
  alert: AlertResponse;
  userLocation?: { latitude: number; longitude: number };
  onViewMap?: () => void;
  onGetDirections?: () => void;
  className?: string;
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
function formatDistance(meters: number): string {
  if (meters < 1000) {
    return `${Math.round(meters)}m away`;
  }
  return `${(meters / 1000).toFixed(1)}km away`;
}

/**
 * Format time ago
 */
function formatTimeAgo(dateString: string): string {
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true });
  } catch {
    return 'Recently';
  }
}

/**
 * Get alert status badge config
 */
function getAlertStatusConfig(status: AlertStatus): { color: string; label: string } {
  const configs = {
    ACTIVE: { color: 'green', label: 'Active' },
    EXPIRED: { color: 'default', label: 'Expired' },
    CANCELLED: { color: 'red', label: 'Cancelled' },
  };
  return configs[status];
}

export function AlertCard({
  alert,
  userLocation,
  onViewMap,
  onGetDirections,
  className = '',
}: AlertCardProps) {
  const crisisColor = getCrisisColor(alert.crisis_type);

  // Calculate distance if user location is available
  const distance = userLocation
    ? calculateDistance(
        userLocation.latitude,
        userLocation.longitude,
        alert.latitude,
        alert.longitude
      )
    : null;

  // Get severity color for border
  const severityColors = {
    CRITICAL: '#ff4d4f',
    HIGH: '#fa8c16',
    MEDIUM: '#faad14',
    LOW: '#52c41a',
  };
  const borderColor = severityColors[alert.severity];

  const handleGetDirections = () => {
    if (onGetDirections) {
      onGetDirections();
    } else {
      // Open Google Maps with directions
      const url = `https://www.google.com/maps/dir/?api=1&destination=${alert.latitude},${alert.longitude}`;
      window.open(url, '_blank');
    }
  };

  return (
    <Card
      hoverable
      className={`transition-shadow hover:shadow-lg ${className}`}
      variant="borderless"
      style={{ borderLeft: `4px solid ${borderColor}` }}
      styles={{ body: { padding: '16px' } }}
    >
      <div className="space-y-3">
        {/* Header: Crisis Type, Severity, and Status */}
        <div className="flex items-start justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <CrisisIcon type={alert.crisis_type} className="flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-base truncate m-0">
                {getCrisisLabel(alert.crisis_type)}
              </h3>
              <p className="text-xs text-gray-500 truncate m-0">
                {alert.alert_title}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <SeverityBadge severity={alert.severity} showIcon />
            <Tag color={getAlertStatusConfig(alert.status).color}>
              {getAlertStatusConfig(alert.status).label}
            </Tag>
          </div>
        </div>

        {/* Alert Message */}
        <p className="text-gray-700 text-sm leading-relaxed">
          {alert.alert_message}
        </p>

        {/* Location and Distance */}
        <div className="space-y-2 text-xs text-gray-600">
          <div className="flex items-center gap-1">
            <EnvironmentOutlined className="flex-shrink-0" />
            <span className="truncate">
              {alert.location_text || `${alert.latitude.toFixed(4)}, ${alert.longitude.toFixed(4)}`}
            </span>
          </div>

          <div className="flex items-center justify-between gap-2 flex-wrap">
            <div className="flex items-center gap-1">
              <ClockCircleOutlined className="flex-shrink-0" />
              <span>{formatTimeAgo(alert.created_at)}</span>
            </div>

            {distance !== null && (
              <div className="flex items-center gap-1 font-medium" style={{ color: crisisColor }}>
                <CompassOutlined className="flex-shrink-0" />
                <span>{formatDistance(distance)}</span>
              </div>
            )}
          </div>
        </div>

        {/* Target Radius Info */}
        {alert.target_radius_meters && (
          <div className="text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded">
            Affected radius: {(alert.target_radius_meters / 1000).toFixed(1)}km
          </div>
        )}

        {/* Action Buttons */}
        <div className="pt-2 border-t border-gray-200">
          <Space wrap>
            {onViewMap && (
              <Button
                type="primary"
                size="small"
                icon={<EnvironmentOutlined />}
                onClick={onViewMap}
              >
                View on Map
              </Button>
            )}
            <Button
              type="default"
              size="small"
              icon={<ArrowRightOutlined />}
              onClick={handleGetDirections}
            >
              Get Directions
            </Button>
          </Space>
        </div>

        {/* Expiry Warning */}
        {alert.expires_at && (
          <div className="text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded">
            Expires: {new Date(alert.expires_at).toLocaleString()}
          </div>
        )}
      </div>
    </Card>
  );
}

// Made with Bob
