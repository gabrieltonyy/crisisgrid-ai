/**
 * Risk Level Badge Component
 * Displays risk level with color-coded styling
 */

import { Tag } from 'antd';
import { WarningOutlined, ExclamationCircleOutlined, InfoCircleOutlined } from '@ant-design/icons';

type RiskLevel = 'IMMEDIATE' | 'HIGH' | 'MODERATE' | 'LOW';

interface RiskLevelBadgeProps {
  level: RiskLevel;
  className?: string;
  showIcon?: boolean;
}

const RISK_CONFIG: Record<RiskLevel, { color: string; label: string; icon: React.ComponentType<any> }> = {
  IMMEDIATE: {
    color: 'red',
    label: 'Immediate Risk',
    icon: WarningOutlined,
  },
  HIGH: {
    color: 'orange',
    label: 'High Risk',
    icon: ExclamationCircleOutlined,
  },
  MODERATE: {
    color: 'gold',
    label: 'Moderate Risk',
    icon: ExclamationCircleOutlined,
  },
  LOW: {
    color: 'green',
    label: 'Low Risk',
    icon: InfoCircleOutlined,
  },
};

export function RiskLevelBadge({ level, className, showIcon = true }: RiskLevelBadgeProps) {
  const config = RISK_CONFIG[level];
  const Icon = config.icon;

  return (
    <Tag color={config.color} className={className} icon={showIcon ? <Icon /> : undefined}>
      {config.label}
    </Tag>
  );
}

// Made with Bob