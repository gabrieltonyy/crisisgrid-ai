/**
 * Statistics Card Component
 * Displays key metrics in card format with trend indicators
 */

'use client';

import { Card, Statistic } from 'antd';
import TrendIndicator from '../ui/TrendIndicator';
import type { ReactNode } from 'react';

export type StatisticType = 'success' | 'warning' | 'danger' | 'info';

interface StatisticsCardProps {
  title: string;
  value: number | string;
  trend?: number;
  change?: string;
  icon?: ReactNode;
  type?: StatisticType;
  suffix?: string;
  prefix?: string;
  loading?: boolean;
  className?: string;
}

const TYPE_COLORS: Record<StatisticType, { bg: string; border: string; text: string; hex: string; ring: string }> = {
  success: {
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    text: 'text-green-600',
    hex: '#16a34a',
    ring: 'bg-emerald-100',
  },
  warning: {
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    text: 'text-amber-600',
    hex: '#d97706',
    ring: 'bg-amber-100',
  },
  danger: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    text: 'text-red-600',
    hex: '#dc2626',
    ring: 'bg-red-100',
  },
  info: {
    bg: 'bg-sky-50',
    border: 'border-sky-200',
    text: 'text-sky-600',
    hex: '#0284c7',
    ring: 'bg-sky-100',
  },
};

export function StatisticsCard({
  title,
  value,
  trend,
  change,
  icon,
  type = 'info',
  suffix,
  prefix,
  loading = false,
  className = '',
}: StatisticsCardProps) {
  const colors = TYPE_COLORS[type];

  return (
    <Card
      loading={loading}
      className={`${colors.bg} border ${colors.border} overflow-hidden ${className}`}
      styles={{ body: { padding: '20px' } }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <Statistic
            title={
              <span className="text-gray-600 text-sm font-medium">{title}</span>
            }
            value={value}
            suffix={suffix}
            prefix={prefix}
            valueStyle={{ 
              color: colors.hex,
              fontSize: '28px',
              fontWeight: 800,
              letterSpacing: 0,
            }}
          />
          
          {/* Trend and Change */}
          <div className="mt-2 flex items-center gap-2">
            {trend !== undefined && (
              <TrendIndicator value={trend} />
            )}
            {change && (
              <span className="text-xs text-gray-500">{change}</span>
            )}
          </div>
        </div>

        {/* Icon */}
        {icon && (
          <div className={`h-12 w-12 rounded-lg ${colors.ring} ${colors.text} flex items-center justify-center text-2xl`}>
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}

// Made with Bob
