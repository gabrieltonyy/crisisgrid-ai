/**
 * Report Card Component
 * Displays report summary in a card format
 */

'use client';

import { Card } from 'antd';
import { AlertOutlined, ClockCircleOutlined, EnvironmentOutlined, CheckCircleOutlined, PictureOutlined } from '@ant-design/icons';
import { CrisisIcon, getCrisisLabel } from '../ui/CrisisIcon';
import { StatusBadge } from '../ui/StatusBadge';
import type { ReportResponse } from '@/types/api';
import { formatPercentScore } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

interface ReportCardProps {
  report: ReportResponse;
  onClick?: () => void;
  className?: string;
}

export function ReportCard({ report, onClick, className = '' }: ReportCardProps) {
  const truncateText = (text: string, maxLength: number = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const formatTimeAgo = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return 'Recently';
    }
  };

  return (
    <Card
      hoverable
      onClick={onClick}
      className={`cursor-pointer border border-slate-200 transition-shadow hover:shadow-lg ${className}`}
      styles={{ body: { padding: '16px' } }}
    >
      <div className="space-y-3">
        {/* Header: Crisis Type and Status */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <CrisisIcon type={report.crisis_type} className="flex-shrink-0" />
            <span className="font-semibold text-base truncate">
              {getCrisisLabel(report.crisis_type)}
            </span>
          </div>
          <StatusBadge status={report.status} className="flex-shrink-0" />
        </div>

        {/* Description */}
        <p className="text-gray-700 text-sm leading-relaxed">
          {truncateText(report.description)}
        </p>

        {/* Footer: Location, Time, and Verification */}
        <div className="space-y-2 text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <EnvironmentOutlined className="flex-shrink-0" />
            <span className="truncate">
              {report.location_text || `${report.latitude.toFixed(4)}, ${report.longitude.toFixed(4)}`}
            </span>
          </div>
          
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-1">
              <ClockCircleOutlined className="flex-shrink-0" />
              <span>{formatTimeAgo(report.created_at)}</span>
            </div>
            
            {report.confidence_score !== undefined && (
              <div className="flex items-center gap-1">
                <CheckCircleOutlined className="flex-shrink-0" />
                <span>Confidence: {formatPercentScore(report.confidence_score)}</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-1">
            <AlertOutlined className="flex-shrink-0" />
            <span>Severity: {formatPercentScore(report.severity_score)}</span>
          </div>
        </div>

        {/* Media indicator */}
        {(report.image_url || report.video_url) && (
          <div className="flex items-center gap-1 text-xs font-medium text-sky-700">
            <PictureOutlined />
            <span>Media attached</span>
          </div>
        )}
      </div>
    </Card>
  );
}

// Made with Bob
