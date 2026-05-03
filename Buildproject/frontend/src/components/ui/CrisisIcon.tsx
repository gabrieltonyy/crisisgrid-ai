/**
 * Crisis Icon Component
 * Displays appropriate icon for each crisis type
 */

import {
  FireOutlined,
  ThunderboltOutlined,
  AlertOutlined,
  MedicineBoxOutlined,
  CarOutlined,
  WarningOutlined,
  SafetyOutlined,
  ExperimentOutlined,
} from '@ant-design/icons';
import type { CrisisType } from '@/types/api';

interface CrisisIconProps {
  type: CrisisType;
  className?: string;
  style?: React.CSSProperties;
}

const CRISIS_ICONS: Record<CrisisType, { icon: React.ComponentType<any>; color: string }> = {
  FIRE: {
    icon: FireOutlined,
    color: '#ff4d4f',
  },
  FLOOD: {
    icon: ThunderboltOutlined,
    color: '#1890ff',
  },
  WILDLIFE: {
    icon: WarningOutlined,
    color: '#fa8c16',
  },
  ACCIDENT: {
    icon: CarOutlined,
    color: '#faad14',
  },
  SECURITY: {
    icon: SafetyOutlined,
    color: '#722ed1',
  },
  HEALTH: {
    icon: MedicineBoxOutlined,
    color: '#eb2f96',
  },
  LANDSLIDE: {
    icon: WarningOutlined,
    color: '#a16207',
  },
  HAZARDOUS_SPILL: {
    icon: ExperimentOutlined,
    color: '#13c2c2',
  },
  OTHER: {
    icon: AlertOutlined,
    color: '#8c8c8c',
  },
};

export function CrisisIcon({ type, className, style }: CrisisIconProps) {
  const config = CRISIS_ICONS[type];
  const Icon = config.icon;

  return (
    <Icon
      className={className}
      style={{
        color: config.color,
        fontSize: '1.5rem',
        ...style,
      }}
    />
  );
}

export function getCrisisColor(type: CrisisType): string {
  return CRISIS_ICONS[type].color;
}

export function getCrisisLabel(type: CrisisType): string {
  const labels: Record<CrisisType, string> = {
    FIRE: 'Fire',
    FLOOD: 'Flood',
    WILDLIFE: 'Wildlife',
    ACCIDENT: 'Accident',
    SECURITY: 'Security',
    HEALTH: 'Health Emergency',
    LANDSLIDE: 'Landslide',
    HAZARDOUS_SPILL: 'Hazardous Spill',
    OTHER: 'Other',
  };
  return labels[type];
}

// Made with Bob
