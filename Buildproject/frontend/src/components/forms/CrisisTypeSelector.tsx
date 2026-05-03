/**
 * Crisis Type Selector Component
 * Dropdown for selecting crisis type with icons and descriptions
 */

'use client';

import { Select } from 'antd';
import { CrisisIcon, getCrisisLabel } from '@/components/ui/CrisisIcon';
import type { CrisisType } from '@/types/api';

interface CrisisTypeSelectorProps {
  value?: CrisisType | '';
  onChange: (value: CrisisType) => void;
  error?: string;
  disabled?: boolean;
  className?: string;
}

const CRISIS_DESCRIPTIONS: Record<CrisisType, string> = {
  FIRE: 'Building fire, wildfire, or smoke',
  FLOOD: 'Flooding, water damage, or heavy rain',
  WILDLIFE: 'Dangerous animal encounter or wildlife threat',
  ACCIDENT: 'Vehicle accident, collision, or crash',
  SECURITY: 'Security threat or public safety issue',
  HEALTH: 'Medical or public health emergency',
  LANDSLIDE: 'Landslide, debris flow, or slope collapse',
  HAZARDOUS_SPILL: 'Chemical, fuel, or hazardous material spill',
  OTHER: 'Other emergency situation',
};

const CRISIS_OPTIONS: CrisisType[] = [
  'FIRE',
  'FLOOD',
  'WILDLIFE',
  'ACCIDENT',
  'SECURITY',
  'HEALTH',
  'LANDSLIDE',
  'HAZARDOUS_SPILL',
  'OTHER',
];

export function CrisisTypeSelector({
  value,
  onChange,
  error,
  disabled = false,
  className = '',
}: CrisisTypeSelectorProps) {
  return (
    <div className={className}>
      <Select
        value={value || undefined}
        onChange={onChange}
        placeholder="Select crisis type"
        size="large"
        disabled={disabled}
        status={error ? 'error' : undefined}
        className="w-full"
        options={CRISIS_OPTIONS.map((type) => ({
          value: type,
          label: (
            <div className="flex items-center gap-3 py-1">
              <CrisisIcon type={type} style={{ fontSize: '1.25rem' }} />
              <div className="flex flex-col">
                <span className="font-medium">{getCrisisLabel(type)}</span>
                <span className="text-xs text-gray-500">
                  {CRISIS_DESCRIPTIONS[type]}
                </span>
              </div>
            </div>
          ),
        }))}
        optionLabelProp="label"
        showSearch
        filterOption={(input, option) => {
          const type = option?.value as CrisisType;
          const label = getCrisisLabel(type).toLowerCase();
          const description = CRISIS_DESCRIPTIONS[type].toLowerCase();
          const searchTerm = input.toLowerCase();
          return label.includes(searchTerm) || description.includes(searchTerm);
        }}
      />
      {error && (
        <div className="mt-1 text-sm text-red-500">{error}</div>
      )}
    </div>
  );
}

// Made with Bob
