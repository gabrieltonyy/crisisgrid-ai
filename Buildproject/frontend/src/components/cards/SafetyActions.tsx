/**
 * Safety Actions Component
 * Displays priority-ordered safety action checklist
 */

'use client';

import { useState } from 'react';
import { List, Checkbox, Card } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import { getCrisisColor } from '../ui/CrisisIcon';
import type { SafetyAction, CrisisType } from '@/types/api';

interface SafetyActionsProps {
  actions: SafetyAction[];
  crisisType: CrisisType;
  className?: string;
}

export function SafetyActions({ actions, crisisType, className = '' }: SafetyActionsProps) {
  const [checkedItems, setCheckedItems] = useState<Set<number>>(new Set());
  const crisisColor = getCrisisColor(crisisType);

  const handleCheck = (priority: number) => {
    setCheckedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(priority)) {
        newSet.delete(priority);
      } else {
        newSet.add(priority);
      }
      return newSet;
    });
  };

  // Sort actions by priority
  const sortedActions = [...actions].sort((a, b) => a.priority - b.priority);

  // Calculate completion percentage
  const completionPercentage = actions.length > 0 
    ? Math.round((checkedItems.size / actions.length) * 100) 
    : 0;

  return (
    <Card
      className={`shadow-md ${className}`}
      variant="borderless"
      style={{ borderTop: `4px solid ${crisisColor}` }}
    >
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold m-0 flex items-center gap-2">
            <ExclamationCircleOutlined style={{ color: crisisColor }} />
            Safety Action Checklist
          </h3>
          <span className="text-sm font-medium text-gray-600">
            {checkedItems.size} / {actions.length} completed
          </span>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <div
            className="h-full transition-all duration-300 ease-in-out"
            style={{
              width: `${completionPercentage}%`,
              backgroundColor: completionPercentage === 100 ? '#52c41a' : crisisColor,
            }}
          />
        </div>
      </div>

      {/* Actions List */}
      <List
        dataSource={sortedActions}
        renderItem={(action) => {
          const isChecked = checkedItems.has(action.priority);
          const isCritical = action.priority <= 3;

          return (
            <List.Item
              className={`
                border-l-4 pl-4 mb-3 rounded-r-lg transition-all
                ${isChecked ? 'bg-green-50 border-green-500 opacity-75' : 'bg-white border-gray-300'}
                ${isCritical && !isChecked ? 'border-red-500 bg-red-50' : ''}
                hover:shadow-sm
              `}
            >
              <div className="flex items-start gap-3 w-full">
                {/* Checkbox */}
                <Checkbox
                  checked={isChecked}
                  onChange={() => handleCheck(action.priority)}
                  className="mt-1"
                />

                {/* Priority Badge */}
                <div
                  className={`
                    flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-white
                    ${isCritical ? 'bg-red-500' : 'bg-blue-500'}
                  `}
                >
                  {action.priority}
                </div>

                {/* Action Content */}
                <div className="flex-1 min-w-0">
                  <p
                    className={`
                      font-medium mb-1
                      ${isChecked ? 'line-through text-gray-500' : 'text-gray-900'}
                    `}
                  >
                    {action.action}
                  </p>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    {action.rationale}
                  </p>
                  {isCritical && !isChecked && (
                    <div className="mt-2 text-xs font-semibold text-red-600 flex items-center gap-1">
                      <ExclamationCircleOutlined />
                      <span>CRITICAL ACTION</span>
                    </div>
                  )}
                </div>
              </div>
            </List.Item>
          );
        }}
      />

      {/* Footer Note */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 italic">
          💡 Tip: Check off actions as you complete them to track your safety progress.
          {actions.some(a => a.priority <= 3) && (
            <span className="block mt-1 text-red-600 font-medium">
              ⚠️ Complete critical actions (1-3) immediately!
            </span>
          )}
        </p>
      </div>
    </Card>
  );
}

// Made with Bob
