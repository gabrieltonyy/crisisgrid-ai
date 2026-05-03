/**
 * Alerts Map Component
 * Displays multiple alerts on map with markers and clustering
 */

'use client';

import { Fragment, useMemo } from 'react';
import { Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import { BaseMap } from './BaseMap';
import { getCrisisColor, getCrisisLabel } from '../ui/CrisisIcon';
import type { AlertResponse } from '@/types/api';

interface AlertsMapProps {
  alerts: AlertResponse[];
  userLocation?: { latitude: number; longitude: number };
  onAlertClick?: (alert: AlertResponse) => void;
  className?: string;
}

const SEVERITY_COLORS = {
  CRITICAL: '#ff4d4f',
  HIGH: '#fa8c16',
  MEDIUM: '#faad14',
  LOW: '#52c41a',
};

/**
 * Create custom marker icon based on severity
 */
function createAlertIcon(severity: string): L.DivIcon {
  const color = SEVERITY_COLORS[severity as keyof typeof SEVERITY_COLORS] || '#1890ff';
  
  return L.divIcon({
    className: 'custom-alert-marker',
    html: `
      <div style="
        background-color: ${color};
        width: 32px;
        height: 32px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        border: 3px solid white;
        box-shadow: 0 3px 10px rgba(0,0,0,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
      ">
        <div style="
          transform: rotate(45deg);
          color: white;
          font-weight: bold;
          font-size: 18px;
        ">!</div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  });
}

/**
 * Create user location marker icon
 */
function createUserIcon(): L.DivIcon {
  return L.divIcon({
    className: 'custom-user-marker',
    html: `
      <div style="
        background-color: #1890ff;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      "></div>
    `,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
}

export function AlertsMap({
  alerts,
  userLocation,
  onAlertClick,
  className = 'h-[600px] w-full rounded-lg',
}: AlertsMapProps) {
  // Calculate map center based on alerts or user location
  const center: [number, number] = useMemo(() => {
    if (userLocation) {
      return [userLocation.latitude, userLocation.longitude];
    }
    if (alerts.length > 0) {
      const avgLat = alerts.reduce((sum, a) => sum + a.latitude, 0) / alerts.length;
      const avgLng = alerts.reduce((sum, a) => sum + a.longitude, 0) / alerts.length;
      return [avgLat, avgLng];
    }
    return [37.7749, -122.4194]; // Default to San Francisco
  }, [alerts, userLocation]);

  // Calculate appropriate zoom level
  const zoom = useMemo(() => {
    if (alerts.length === 0) return 12;
    if (alerts.length === 1) return 14;
    
    // Calculate bounds to fit all alerts
    const lats = alerts.map(a => a.latitude);
    const lngs = alerts.map(a => a.longitude);
    const latRange = Math.max(...lats) - Math.min(...lats);
    const lngRange = Math.max(...lngs) - Math.min(...lngs);
    const maxRange = Math.max(latRange, lngRange);
    
    if (maxRange < 0.01) return 14;
    if (maxRange < 0.05) return 12;
    if (maxRange < 0.1) return 11;
    if (maxRange < 0.5) return 10;
    return 9;
  }, [alerts]);

  return (
    <div className="relative">
      <BaseMap center={center} zoom={zoom} className={className}>
        {/* User Location Marker */}
        {userLocation && (
          <>
            <Marker
              position={[userLocation.latitude, userLocation.longitude]}
              icon={createUserIcon()}
            >
              <Popup>
                <div className="text-center">
                  <div className="font-semibold">Your Location</div>
                </div>
              </Popup>
            </Marker>
            <Circle
              center={[userLocation.latitude, userLocation.longitude]}
              radius={100}
              pathOptions={{
                color: '#1890ff',
                fillColor: '#1890ff',
                fillOpacity: 0.1,
                weight: 2,
              }}
            />
          </>
        )}

        {/* Alert Markers */}
        {alerts.map((alert) => (
          <Fragment key={alert.id}>
            <Marker
              position={[alert.latitude, alert.longitude]}
              icon={createAlertIcon(alert.severity)}
              eventHandlers={{
                click: () => onAlertClick?.(alert),
              }}
              // @ts-ignore - custom property for clustering
              severity={alert.severity}
            >
              <Popup>
                <div className="min-w-[200px]">
                  <div className="font-semibold text-base mb-1">
                    {getCrisisLabel(alert.crisis_type)}
                  </div>
                  <div className="text-sm text-gray-600 mb-2">
                    {alert.alert_title}
                  </div>
                  <div className="text-xs text-gray-500 mb-2">
                    {alert.location_text || `${alert.latitude.toFixed(4)}, ${alert.longitude.toFixed(4)}`}
                  </div>
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className="px-2 py-1 rounded text-xs font-medium text-white"
                      style={{ backgroundColor: SEVERITY_COLORS[alert.severity] }}
                    >
                      {alert.severity}
                    </span>
                    <span className="text-xs text-gray-500">
                      {alert.status}
                    </span>
                  </div>
                  {alert.target_radius_meters && (
                    <div className="text-xs text-gray-500">
                      Radius: {(alert.target_radius_meters / 1000).toFixed(1)}km
                    </div>
                  )}
                </div>
              </Popup>
              
              {/* Alert Radius Circle */}
              {alert.target_radius_meters && (
                <Circle
                  center={[alert.latitude, alert.longitude]}
                  radius={alert.target_radius_meters}
                  pathOptions={{
                    color: getCrisisColor(alert.crisis_type),
                    fillColor: getCrisisColor(alert.crisis_type),
                    fillOpacity: 0.1,
                    weight: 2,
                  }}
                />
              )}
            </Marker>
          </Fragment>
        ))}
      </BaseMap>

      {/* Map Legend */}
      <div className="absolute bottom-4 right-4 bg-white p-3 rounded-lg shadow-md z-[1000] max-w-xs">
        <div className="text-xs space-y-2">
          <div className="font-semibold mb-2">Severity Levels</div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: SEVERITY_COLORS.CRITICAL }}></div>
            <span>Critical</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: SEVERITY_COLORS.HIGH }}></div>
            <span>High</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: SEVERITY_COLORS.MEDIUM }}></div>
            <span>Medium</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: SEVERITY_COLORS.LOW }}></div>
            <span>Low</span>
          </div>
          {userLocation && (
            <>
              <div className="border-t pt-2 mt-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                  <span>Your Location</span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Alert Count Badge */}
      <div className="absolute top-4 left-4 bg-white px-3 py-2 rounded-lg shadow-md z-[1000]">
        <div className="text-sm font-semibold">
          {alerts.length} {alerts.length === 1 ? 'Alert' : 'Alerts'}
        </div>
      </div>
    </div>
  );
}

// Made with Bob
