/**
 * Report Map Component
 * Displays single report location on map
 */

'use client';

import { BaseMap } from './BaseMap';
import { LocationMarker } from './LocationMarker';
import type { ReportResponse } from '@/types/api';
import { getCrisisLabel } from '../ui/CrisisIcon';

interface ReportMapProps {
  report: ReportResponse;
  className?: string;
  zoom?: number;
}

export function ReportMap({ report, className, zoom = 14 }: ReportMapProps) {
  const position: [number, number] = [report.latitude, report.longitude];

  const markerTitle = getCrisisLabel(report.crisis_type);
  const markerDescription = report.location_text || `${report.latitude.toFixed(4)}, ${report.longitude.toFixed(4)}`;

  return (
    <BaseMap
      center={position}
      zoom={zoom}
      className={className || 'h-96 w-full rounded-lg'}
    >
      <LocationMarker
        position={position}
        title={markerTitle}
        description={markerDescription}
        crisisType={report.crisis_type}
      />
    </BaseMap>
  );
}

// Made with Bob