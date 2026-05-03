/**
 * Incident Timeline Component
 * Displays timeline of incident events
 */

'use client';

import { Timeline } from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  AlertOutlined,
  BellOutlined,
  CarOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { format } from 'date-fns';
import type { ReportResponse, AlertResponse, DispatchResponse } from '@/types/api';

interface IncidentTimelineProps {
  report: ReportResponse;
  alerts?: AlertResponse[];
  dispatches?: DispatchResponse[];
  className?: string;
}

interface TimelineEvent {
  timestamp: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

export function IncidentTimeline({
  report,
  alerts = [],
  dispatches = [],
  className = '',
}: IncidentTimelineProps) {
  const formatTimestamp = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy HH:mm');
    } catch {
      return dateString;
    }
  };

  // Build timeline events from report, alerts, and dispatches
  const events: TimelineEvent[] = [];

  // Report submission
  events.push({
    timestamp: report.created_at,
    title: 'Report Submitted',
    description: `Crisis report submitted: ${report.crisis_type}`,
    icon: <FileTextOutlined />,
    color: 'blue',
  });

  // Verification status changes
  if (report.status === 'VERIFIED') {
    events.push({
      timestamp: report.updated_at || report.created_at,
      title: 'Report Verified',
      description: `Confidence score: ${Math.round((report.confidence_score || 0) * 100)}%`,
      icon: <CheckCircleOutlined />,
      color: 'green',
    });
  } else if (report.status === 'PROVISIONAL_CRITICAL') {
    events.push({
      timestamp: report.updated_at || report.created_at,
      title: 'Provisional Critical Status',
      description: 'Report marked as potentially critical, pending verification',
      icon: <AlertOutlined />,
      color: 'red',
    });
  } else if (report.status === 'FALSE_REPORT') {
    events.push({
      timestamp: report.updated_at || report.created_at,
      title: 'Report Rejected',
      description: 'Report marked as false or duplicate',
      icon: <ClockCircleOutlined />,
      color: 'gray',
    });
  }

  // Incident creation (if linked)
  if (report.incident_id) {
    events.push({
      timestamp: report.updated_at || report.created_at,
      title: 'Incident Created',
      description: `Incident #${report.incident_id} created from this report`,
      icon: <AlertOutlined />,
      color: 'orange',
    });
  }

  // Alert generation
  alerts.forEach((alert) => {
    events.push({
      timestamp: alert.created_at,
      title: 'Alert Generated',
      description: `${alert.severity} alert sent to nearby citizens`,
      icon: <BellOutlined />,
      color: alert.severity === 'CRITICAL' ? 'red' : 'orange',
    });
  });

  // Dispatch events
  dispatches.forEach((dispatch) => {
    events.push({
      timestamp: dispatch.created_at,
      title: 'Emergency Dispatch',
      description: `${dispatch.authority_type.replace('_', ' ')} dispatched`,
      icon: <CarOutlined />,
      color: 'purple',
    });

    if (dispatch.acknowledged_at) {
      events.push({
        timestamp: dispatch.acknowledged_at,
        title: 'Dispatch Acknowledged',
        description: `${dispatch.authority_type.replace('_', ' ')} acknowledged`,
        icon: <CheckCircleOutlined />,
        color: 'green',
      });
    }
  });

  // Sort events by timestamp (newest first)
  events.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  // Convert to Ant Design Timeline items
  const timelineItems = events.map((event, index) => ({
    key: index,
    color: event.color,
    dot: event.icon,
    children: (
      <div className="pb-4">
        <div className="flex items-start justify-between gap-2 mb-1">
          <span className="font-semibold text-gray-900">{event.title}</span>
          <span className="text-xs text-gray-500 whitespace-nowrap">
            {formatTimestamp(event.timestamp)}
          </span>
        </div>
        <p className="text-sm text-gray-600">{event.description}</p>
      </div>
    ),
  }));

  if (timelineItems.length === 0) {
    return (
      <div className={`text-center py-8 text-gray-500 ${className}`}>
        <ClockCircleOutlined className="text-2xl mb-2" />
        <p>No timeline events available</p>
      </div>
    );
  }

  return (
    <div className={className}>
      <Timeline items={timelineItems} mode="left" />
    </div>
  );
}

// Made with Bob