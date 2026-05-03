/**
 * Error Alert Component
 * Displays error messages with retry option
 */

import { Alert, Button } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';

interface ErrorAlertProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  showRetry?: boolean;
  type?: 'error' | 'warning';
  className?: string;
}

export function ErrorAlert({
  title = 'Error',
  message,
  onRetry,
  showRetry = true,
  type = 'error',
  className = '',
}: ErrorAlertProps) {
  return (
    <Alert
      type={type}
      message={title}
      description={
        <div className="flex flex-col gap-3">
          <p>{message}</p>
          {showRetry && onRetry && (
            <Button
              type="primary"
              danger={type === 'error'}
              icon={<ReloadOutlined />}
              onClick={onRetry}
              size="small"
            >
              Try Again
            </Button>
          )}
        </div>
      }
      showIcon
      className={className}
    />
  );
}

// Made with Bob