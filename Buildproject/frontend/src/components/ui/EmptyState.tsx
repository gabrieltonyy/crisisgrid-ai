/**
 * Empty State Component
 * Displays when no data is available
 */

import { Empty, Button } from 'antd';
import { InboxOutlined } from '@ant-design/icons';

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export function EmptyState({
  title = 'No data available',
  description,
  icon,
  action,
  className = '',
}: EmptyStateProps) {
  const image =
    typeof icon === 'string' ? (
      <span className="text-6xl leading-none" aria-hidden="true">
        {icon}
      </span>
    ) : (
      icon || <InboxOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />
    );

  return (
    <div className={`flex items-center justify-center py-12 ${className}`}>
      <Empty
        image={image}
        styles={{ image: { height: 80 } }}
        description={
          <div className="text-center">
            <p className="text-lg font-medium text-gray-900 mb-2">{title}</p>
            {description && (
              <p className="text-sm text-gray-500">{description}</p>
            )}
          </div>
        }
      >
        {action && (
          <Button type="primary" onClick={action.onClick}>
            {action.label}
          </Button>
        )}
      </Empty>
    </div>
  );
}

// Made with Bob
