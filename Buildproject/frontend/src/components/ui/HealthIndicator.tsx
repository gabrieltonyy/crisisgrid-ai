/**
 * HealthIndicator Component
 * Displays system health status with color-coded indicator
 */

import React from 'react';
import { CheckCircleOutlined, WarningOutlined, CloseCircleOutlined } from '@ant-design/icons';

export type HealthStatus = 'healthy' | 'degraded' | 'down';

interface HealthIndicatorProps {
  status: HealthStatus;
  showLabel?: boolean;
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

export default function HealthIndicator({ 
  status, 
  showLabel = true,
  size = 'medium',
  className = '' 
}: HealthIndicatorProps) {
  const config = {
    healthy: {
      icon: CheckCircleOutlined,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      label: 'All Systems Operational',
    },
    degraded: {
      icon: WarningOutlined,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
      label: 'Degraded Performance',
    },
    down: {
      icon: CloseCircleOutlined,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      label: 'System Issues',
    },
  };

  const sizeClasses = {
    small: 'text-xs',
    medium: 'text-sm',
    large: 'text-base',
  };

  const { icon: Icon, color, bgColor, label } = config[status];

  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      <span className={`flex items-center justify-center w-6 h-6 rounded-full ${bgColor}`}>
        <Icon className={`${color} ${sizeClasses[size]}`} />
      </span>
      {showLabel && (
        <span className={`font-medium ${color} ${sizeClasses[size]}`}>
          {label}
        </span>
      )}
    </div>
  );
}

// Made with Bob