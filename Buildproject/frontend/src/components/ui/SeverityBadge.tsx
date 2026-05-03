/**
 * Severity Badge Component
 * Displays severity level with color-coded styling
 */

import type { SeverityLevel } from '@/types/api';

interface SeverityBadgeProps {
  severity: SeverityLevel;
  className?: string;
  showIcon?: boolean;
}

const SEVERITY_CONFIG: Record<SeverityLevel, { className: string; dot: string; label: string }> = {
  CRITICAL: {
    className: 'border-red-200 bg-red-50 text-red-700',
    dot: 'bg-red-500',
    label: 'Critical',
  },
  HIGH: {
    className: 'border-orange-200 bg-orange-50 text-orange-700',
    dot: 'bg-orange-500',
    label: 'High',
  },
  MEDIUM: {
    className: 'border-amber-200 bg-amber-50 text-amber-700',
    dot: 'bg-amber-500',
    label: 'Medium',
  },
  LOW: {
    className: 'border-emerald-200 bg-emerald-50 text-emerald-700',
    dot: 'bg-emerald-500',
    label: 'Low',
  },
};

export function SeverityBadge({ severity, className, showIcon = false }: SeverityBadgeProps) {
  const config = SEVERITY_CONFIG[severity];

  return (
    <span className={`inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-xs font-semibold ${config.className} ${className || ''}`}>
      {showIcon && <span className={`h-2 w-2 rounded-full ${config.dot}`} />}
      {config.label}
    </span>
  );
}

// Made with Bob
