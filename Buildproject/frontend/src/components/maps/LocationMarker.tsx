/**
 * Location Marker Component
 * Custom marker for map locations
 */

'use client';

import { Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import type { CrisisType, SeverityLevel } from '@/types/api';
import { getCrisisColor } from '../ui/CrisisIcon';

interface LocationMarkerProps {
  position: [number, number];
  title?: string;
  description?: string;
  crisisType?: CrisisType;
  severity?: SeverityLevel;
  radius?: number; // in meters
  onClick?: () => void;
}

const SEVERITY_COLORS: Record<SeverityLevel, string> = {
  CRITICAL: '#ff4d4f',
  HIGH: '#fa8c16',
  MEDIUM: '#faad14',
  LOW: '#52c41a',
};

export function LocationMarker({
  position,
  title,
  description,
  crisisType,
  severity,
  radius,
  onClick,
}: LocationMarkerProps) {
  // Create custom icon based on crisis type and severity
  const iconColor = crisisType ? getCrisisColor(crisisType) : (severity ? SEVERITY_COLORS[severity] : '#1890ff');
  
  const customIcon = L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        background-color: ${iconColor};
        width: 30px;
        height: 30px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      ">
        <div style="
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          transform: rotate(45deg);
          color: white;
          font-weight: bold;
          font-size: 16px;
        ">!</div>
      </div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -30],
  });

  return (
    <>
      <Marker
        position={position}
        icon={customIcon}
        eventHandlers={{
          click: onClick,
        }}
      >
        {(title || description) && (
          <Popup>
            {title && <div className="font-semibold mb-1">{title}</div>}
            {description && <div className="text-sm text-gray-600">{description}</div>}
          </Popup>
        )}
      </Marker>
      
      {radius && (
        <Circle
          center={position}
          radius={radius}
          pathOptions={{
            color: iconColor,
            fillColor: iconColor,
            fillOpacity: 0.1,
            weight: 2,
          }}
        />
      )}
    </>
  );
}

// Made with Bob