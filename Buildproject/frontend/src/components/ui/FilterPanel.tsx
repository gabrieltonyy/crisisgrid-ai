/**
 * Filter Panel Component
 * Reusable filter panel for lists with multiple filter types
 */

'use client';

import { useState } from 'react';
import { Form, Select, DatePicker, Input, Button, Collapse } from 'antd';
import { FilterOutlined, ClearOutlined } from '@ant-design/icons';

const { RangePicker } = DatePicker;

export type FilterType = 'select' | 'multiselect' | 'daterange' | 'search';

export interface FilterConfig {
  name: string;
  label: string;
  type: FilterType;
  options?: Array<{ label: string; value: string | number }>;
  placeholder?: string;
  allowClear?: boolean;
}

interface FilterPanelProps {
  filters: FilterConfig[];
  onApply: (values: Record<string, any>) => void;
  onReset?: () => void;
  defaultCollapsed?: boolean;
  className?: string;
}

export function FilterPanel({
  filters,
  onApply,
  onReset,
  defaultCollapsed = false,
  className = '',
}: FilterPanelProps) {
  const [form] = Form.useForm();
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);

  const handleApply = () => {
    const values = form.getFieldsValue();
    // Filter out empty values
    const filteredValues = Object.entries(values).reduce((acc, [key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        acc[key] = value;
      }
      return acc;
    }, {} as Record<string, any>);
    
    onApply(filteredValues);
  };

  const handleReset = () => {
    form.resetFields();
    if (onReset) {
      onReset();
    } else {
      onApply({});
    }
  };

  const renderFilter = (filter: FilterConfig) => {
    switch (filter.type) {
      case 'select':
        return (
          <Select
            placeholder={filter.placeholder || `Select ${filter.label}`}
            allowClear={filter.allowClear !== false}
            options={filter.options}
            className="w-full"
          />
        );

      case 'multiselect':
        return (
          <Select
            mode="multiple"
            placeholder={filter.placeholder || `Select ${filter.label}`}
            allowClear={filter.allowClear !== false}
            options={filter.options}
            className="w-full"
            maxTagCount="responsive"
          />
        );

      case 'daterange':
        return (
          <RangePicker
            className="w-full"
            format="YYYY-MM-DD"
          />
        );

      case 'search':
        return (
          <Input.Search
            placeholder={filter.placeholder || `Search ${filter.label}`}
            allowClear={filter.allowClear !== false}
            onSearch={handleApply}
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className={`ops-panel rounded-lg ${className}`}>
      <Collapse
        activeKey={isCollapsed ? [] : ['filters']}
        onChange={(keys) => setIsCollapsed(keys.length === 0)}
        ghost
        expandIconPosition="end"
        items={[
          {
            key: 'filters',
            label: (
            <div className="flex items-center gap-2 font-medium">
              <FilterOutlined />
              <span>Filters</span>
            </div>
            ),
            children: (
              <Form
                form={form}
                layout="vertical"
                onFinish={handleApply}
                className="pt-2"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {filters.map((filter) => (
                    <Form.Item
                      key={filter.name}
                      name={filter.name}
                      label={filter.label}
                      className="mb-0"
                    >
                      {renderFilter(filter)}
                    </Form.Item>
                  ))}
                </div>

                <div className="flex flex-wrap items-center gap-2 mt-4 pt-4 border-t border-gray-200">
                  <Button
                    type="primary"
                    icon={<FilterOutlined />}
                    onClick={handleApply}
                  >
                    Apply Filters
                  </Button>
                  <Button
                    icon={<ClearOutlined />}
                    onClick={handleReset}
                  >
                    Reset
                  </Button>
                </div>
              </Form>
            ),
          },
        ]}
      />
    </div>
  );
}

// Made with Bob
