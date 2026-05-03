/**
 * TrendIndicator Component
 * Displays trend direction with arrow and percentage
 */

import React from 'react';
import { ArrowUpOutlined, ArrowDownOutlined, MinusOutlined } from '@ant-design/icons';

interface TrendIndicatorProps {
  value: number;
  suffix?: string;
  showZero?: boolean;
  className?: string;
}

export default function TrendIndicator({ 
  value, 
  suffix = '%',
  showZero = false,
  className = '' 
}: TrendIndicatorProps) {
  const isPositive = value > 0;
  const isNegative = value < 0;
  const isNeutral = value === 0;

  if (isNeutral && !showZero) {
    return null;
  }

  const colorClass = isPositive 
    ? 'text-green-600' 
    : isNegative 
    ? 'text-red-600' 
    : 'text-gray-500';

  const Icon = isPositive 
    ? ArrowUpOutlined 
    : isNegative 
    ? ArrowDownOutlined 
    : MinusOutlined;

  return (
    <span className={`inline-flex items-center gap-1 text-sm font-medium ${colorClass} ${className}`}>
      <Icon className="text-xs" />
      <span>{Math.abs(value)}{suffix}</span>
    </span>
  );
}

// Made with Bob