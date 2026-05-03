/**
 * Advisory Map Component
 * Displays incident location with risk radius on map
 */

'use client';

import { BaseMap } from './BaseMap';
import { LocationMarker } from './LocationMarker';
import type { CrisisType, SeverityLevel } from '@/types/api';

interface AdvisoryMapProps {
  latitude: number;
  longitude: number;
  crisisType: CrisisType;
  severity: SeverityLevel;
  radiusMeters?: number;
  locationText?: string;
  className?: string;
}

export function AdvisoryMap({
  latitude,
  longitude,
  crisisType,
  severity,
  radiusMeters = 1000,
  locationText,
  className = 'h-96 w-full rounded-lg',
}: AdvisoryMapProps) {
  const center: [number, number] = [latitude, longitude];

  // Calculate appropriate zoom level based on radius
  const getZoomLevel = (radius: number): number => {
    if (radius <= 500) return 15;
    if (radius <= 1000) return 14;
    if (radius <= 2000) return 13;
    if (radius <= 5000) return 12;
    return 11;
  };

  const zoom = getZoomLevel(radiusMeters);

  return (
    <div className="relative">
      <BaseMap center={center} zoom={zoom} className={className}>
        <LocationMarker
          position={center}
          title="Incident Location"
          description={locationText || `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`}
          crisisType={crisisType}
          severity={severity}
          radius={radiusMeters}
        />
      </BaseMap>
      
      {/* Map Legend */}
      <div className="absolute bottom-4 right-4 bg-white p-3 rounded-lg shadow-md z-[1000] max-w-xs">
        <div className="text-xs space-y-1">
          <div className="font-semibold mb-2">Map Legend</div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span>Incident Location</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full border-2 border-red-500 bg-red-500 bg-opacity-10"></div>
            <span>Affected Area ({(radiusMeters / 1000).toFixed(1)}km radius)</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Made with Bob