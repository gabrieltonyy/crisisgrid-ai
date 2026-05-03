/**
 * Status Badge Component
 * Displays report/incident status with appropriate styling
 */

import type { IncidentStatus } from '@/types/api';

interface StatusBadgeProps {
  status: IncidentStatus;
  className?: string;
}

const STATUS_CONFIG: Record<IncidentStatus, { className: string; label: string }> = {
  PENDING_VERIFICATION: {
    className: 'border-amber-200 bg-amber-50 text-amber-700',
    label: 'Pending Verification',
  },
  NEEDS_CONFIRMATION: {
    className: 'border-orange-200 bg-orange-50 text-orange-700',
    label: 'Needs Confirmation',
  },
  VERIFIED: {
    className: 'border-emerald-200 bg-emerald-50 text-emerald-700',
    label: 'Verified',
  },
  DISPATCHED: {
    className: 'border-blue-200 bg-blue-50 text-blue-700',
    label: 'Dispatched',
  },
  PROVISIONAL_CRITICAL: {
    className: 'border-red-200 bg-red-50 text-red-700',
    label: 'Provisional Critical',
  },
  FALSE_REPORT: {
    className: 'border-slate-200 bg-slate-50 text-slate-700',
    label: 'False Report',
  },
  RESOLVED: {
    className: 'border-sky-200 bg-sky-50 text-sky-700',
    label: 'Resolved',
  },
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status];

  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold ${config.className} ${className || ''}`}>
      {config.label}
    </span>
  );
}

// Made with Bob
