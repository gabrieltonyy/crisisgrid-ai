/**
 * Loading Spinner Component
 * Displays loading state with optional message
 */

import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'small' | 'default' | 'large';
  fullScreen?: boolean;
  className?: string;
}

export function LoadingSpinner({
  message = 'Loading...',
  size = 'default',
  fullScreen = false,
  className = '',
}: LoadingSpinnerProps) {
  const spinner = (
    <div className={`flex flex-col items-center justify-center gap-4 ${className}`}>
      <Spin
        indicator={<LoadingOutlined style={{ fontSize: size === 'large' ? 48 : size === 'small' ? 24 : 36 }} spin />}
        size={size}
      />
      {message && (
        <p className="text-gray-600 text-center">{message}</p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-white bg-opacity-90 z-50">
        {spinner}
      </div>
    );
  }

  return spinner;
}

// Made with Bob