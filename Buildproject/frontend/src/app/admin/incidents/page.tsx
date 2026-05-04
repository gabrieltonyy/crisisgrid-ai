/**
 * Admin Incidents Page
 * Manage and view incident clusters derived from reports, alerts, and dispatches.
 */

'use client';

import { useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Button, Table, Tag, Typography } from 'antd';
import { AlertOutlined, ClusterOutlined, EyeOutlined, SendOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { formatDistanceToNow } from 'date-fns';
import apiClient from '@/lib/api/client';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { SeverityBadge } from '@/components/ui/SeverityBadge';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { getCrisisLabel } from '@/components/ui/CrisisIcon';
import { formatPercentScore } from '@/lib/utils';
import type {
  AlertResponse,
  DispatchResponse,
  IncidentStatus,
  ReportResponse,
  SeverityLevel,
} from '@/types/api';

const { Title, Text } = Typography;

type IncidentRow = {
  id: string;
  crisis_type: ReportResponse['crisis_type'];
  status: IncidentStatus;
  severity: SeverityLevel;
  confidence_score: number;
  severity_score: number;
  location_text?: string;
  report_count: number;
  alert_count: number;
  dispatch_count: number;
  latest_report_id: string;
  last_updated_at: string;
};

const severityOrder: Record<SeverityLevel, number> = {
  LOW: 1,
  MEDIUM: 2,
  HIGH: 3,
  CRITICAL: 4,
};

const scoreToSeverity = (score: number): SeverityLevel => {
  if (score >= 90) return 'CRITICAL';
  if (score >= 70) return 'HIGH';
  if (score >= 40) return 'MEDIUM';
  return 'LOW';
};

const fetchReports = async (): Promise<ReportResponse[]> => {
  const response = await apiClient.get<ReportResponse[]>('/reports');
  return response.data;
};

const fetchAlerts = async (): Promise<AlertResponse[]> => {
  const response = await apiClient.get<AlertResponse[]>('/alerts');
  return response.data;
};

const fetchDispatches = async (): Promise<DispatchResponse[]> => {
  const response = await apiClient.get<DispatchResponse[]>('/dispatch/logs');
  return response.data;
};

export default function AdminIncidentsPage() {
  const router = useRouter();

  const reportsQuery = useQuery({
    queryKey: ['admin-reports'],
    queryFn: fetchReports,
    refetchInterval: 30000,
  });

  const alertsQuery = useQuery({
    queryKey: ['admin-alerts'],
    queryFn: fetchAlerts,
    refetchInterval: 30000,
  });

  const dispatchQuery = useQuery({
    queryKey: ['dispatch-logs'],
    queryFn: fetchDispatches,
    refetchInterval: 30000,
  });

  const incidents = useMemo<IncidentRow[]>(() => {
    const reports = reportsQuery.data || [];
    const alerts = alertsQuery.data || [];
    const dispatches = dispatchQuery.data || [];

    const alertsByIncident = new Map<string, AlertResponse[]>();
    alerts.forEach((alert) => {
      const list = alertsByIncident.get(alert.incident_id) || [];
      list.push(alert);
      alertsByIncident.set(alert.incident_id, list);
    });

    const dispatchesByIncident = new Map<string, DispatchResponse[]>();
    dispatches.forEach((dispatch) => {
      const list = dispatchesByIncident.get(dispatch.incident_id) || [];
      list.push(dispatch);
      dispatchesByIncident.set(dispatch.incident_id, list);
    });

    const grouped = new Map<string, ReportResponse[]>();
    reports
      .filter((report) => Boolean(report.incident_id))
      .forEach((report) => {
        const incidentId = report.incident_id as string;
        const list = grouped.get(incidentId) || [];
        list.push(report);
        grouped.set(incidentId, list);
      });

    return Array.from(grouped.entries())
      .map(([incidentId, incidentReports]) => {
        const sortedReports = [...incidentReports].sort(
          (a, b) => new Date(b.updated_at || b.created_at).getTime() - new Date(a.updated_at || a.created_at).getTime()
        );
        const latest = sortedReports[0];
        const incidentAlerts = alertsByIncident.get(incidentId) || [];
        const incidentDispatches = dispatchesByIncident.get(incidentId) || [];
        const alertSeverity = incidentAlerts
          .map((alert) => alert.severity)
          .sort((a, b) => severityOrder[b] - severityOrder[a])[0];

        return {
          id: incidentId,
          crisis_type: latest.crisis_type,
          status: latest.status,
          severity: alertSeverity || scoreToSeverity(latest.severity_score),
          confidence_score: Math.max(...incidentReports.map((report) => report.confidence_score)),
          severity_score: Math.max(...incidentReports.map((report) => report.severity_score)),
          location_text: latest.location_text,
          report_count: incidentReports.length,
          alert_count: incidentAlerts.length,
          dispatch_count: incidentDispatches.length,
          latest_report_id: latest.id,
          last_updated_at: latest.updated_at || latest.created_at,
        };
      })
      .sort((a, b) => new Date(b.last_updated_at).getTime() - new Date(a.last_updated_at).getTime());
  }, [alertsQuery.data, dispatchQuery.data, reportsQuery.data]);

  const isLoading = reportsQuery.isLoading || alertsQuery.isLoading || dispatchQuery.isLoading;
  const error = reportsQuery.error || alertsQuery.error || dispatchQuery.error;

  const columns: ColumnsType<IncidentRow> = [
    {
      title: 'Incident',
      dataIndex: 'id',
      key: 'id',
      width: 150,
      render: (id: string) => <Text code>{id}</Text>,
    },
    {
      title: 'Type',
      dataIndex: 'crisis_type',
      key: 'crisis_type',
      width: 120,
      render: (type: IncidentRow['crisis_type']) => <Tag color="blue">{getCrisisLabel(type)}</Tag>,
      sorter: (a, b) => a.crisis_type.localeCompare(b.crisis_type),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 170,
      render: (status: IncidentStatus) => <StatusBadge status={status} />,
      sorter: (a, b) => a.status.localeCompare(b.status),
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      width: 120,
      render: (severity: SeverityLevel) => <SeverityBadge severity={severity} />,
      sorter: (a, b) => severityOrder[a.severity] - severityOrder[b.severity],
      defaultSortOrder: 'descend',
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence_score',
      key: 'confidence_score',
      width: 120,
      render: (score: number) => <Text strong>{formatPercentScore(score)}</Text>,
      sorter: (a, b) => a.confidence_score - b.confidence_score,
    },
    {
      title: 'Location',
      dataIndex: 'location_text',
      key: 'location_text',
      ellipsis: true,
      render: (location: string | undefined) => location || 'Unknown location',
    },
    {
      title: 'Activity',
      key: 'activity',
      width: 190,
      render: (_, record) => (
        <div className="flex items-center gap-2 flex-wrap">
          <Tag>{record.report_count} reports</Tag>
          <Tag icon={<AlertOutlined />} color={record.alert_count ? 'orange' : 'default'}>
            {record.alert_count}
          </Tag>
          <Tag icon={<SendOutlined />} color={record.dispatch_count ? 'blue' : 'default'}>
            {record.dispatch_count}
          </Tag>
        </div>
      ),
    },
    {
      title: 'Updated',
      dataIndex: 'last_updated_at',
      key: 'last_updated_at',
      width: 150,
      render: (date: string) => (
        <Text className="text-xs text-gray-600">
          {formatDistanceToNow(new Date(date), { addSuffix: true })}
        </Text>
      ),
      sorter: (a, b) => new Date(a.last_updated_at).getTime() - new Date(b.last_updated_at).getTime(),
    },
    {
      title: 'Action',
      key: 'action',
      width: 110,
      fixed: 'right',
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => router.push(`/admin/reports/${record.latest_report_id}`)}
        >
          View
        </Button>
      ),
    },
  ];

  if (isLoading) {
    return <LoadingSpinner size="large" message="Loading incident clusters..." />;
  }

  if (error) {
    return (
      <ErrorAlert
        title="Failed to load incidents"
        message="Unable to load incident data. Please try again."
        onRetry={() => {
          reportsQuery.refetch();
          alertsQuery.refetch();
          dispatchQuery.refetch();
        }}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <div className="page-kicker mb-2">Incident clustering</div>
        <Title level={2} className="!mb-1">
          <ClusterOutlined className="mr-2" />
          Incident Management
        </Title>
        <Text type="secondary">
          Local orchestration clusters reports into incidents and links alert and dispatch activity.
        </Text>
      </div>

      <Table
        rowKey="id"
        columns={columns}
        dataSource={incidents}
        pagination={{
          pageSize: 20,
          showSizeChanger: false,
          showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} incidents`,
        }}
        scroll={{ x: 1160 }}
      />
    </div>
  );
}

// Made with Bob
