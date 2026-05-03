/**
 * Admin Dashboard Page - Command Center
 * Main admin dashboard for monitoring and managing the crisis response system
 */

'use client';

import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Row, Col, Button, Card, List, Typography, Space, Progress, Tag } from 'antd';
import {
  FileTextOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  DashboardOutlined,
  SendOutlined,
  WarningOutlined,
  ClusterOutlined,
  RadarChartOutlined,
  SafetyOutlined,
} from '@ant-design/icons';
import { StatisticsCard } from '@/components/cards/StatisticsCard';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { SeverityBadge } from '@/components/ui/SeverityBadge';
import apiClient from '@/lib/api/client';
import type {
  ReportResponse,
  AlertResponse,
  VerificationStats,
  HealthResponse,
  DispatchResponse,
} from '@/types/api';
import { formatPercentScore, normalizePercentScore } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

const { Title, Text } = Typography;

const fetchReports = async (): Promise<ReportResponse[]> => {
  const response = await apiClient.get<ReportResponse[]>('/reports');
  return response.data;
};

const fetchAlerts = async (): Promise<AlertResponse[]> => {
  const response = await apiClient.get<AlertResponse[]>('/alerts');
  return response.data;
};

const fetchVerificationStats = async (): Promise<VerificationStats> => {
  const response = await apiClient.get<VerificationStats>('/verification/stats');
  return response.data;
};

const fetchHealth = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
};

const fetchDispatchLogs = async (): Promise<DispatchResponse[]> => {
  const response = await apiClient.get<DispatchResponse[]>('/dispatch/logs');
  return response.data;
};

export default function AdminDashboardPage() {
  const router = useRouter();

  const { data: reports, isLoading: reportsLoading, error: reportsError } = useQuery({
    queryKey: ['admin-reports'],
    queryFn: fetchReports,
    refetchInterval: 30000,
  });

  const { data: alerts, isLoading: alertsLoading, error: alertsError } = useQuery({
    queryKey: ['admin-alerts'],
    queryFn: fetchAlerts,
    refetchInterval: 30000,
  });

  const { data: verificationStats, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ['verification-stats'],
    queryFn: fetchVerificationStats,
    refetchInterval: 30000,
  });

  const { data: health, isLoading: healthLoading, error: healthError } = useQuery({
    queryKey: ['system-health'],
    queryFn: fetchHealth,
    refetchInterval: 30000,
  });

  const { data: dispatches, isLoading: dispatchLoading, error: dispatchError } = useQuery({
    queryKey: ['dispatch-logs'],
    queryFn: fetchDispatchLogs,
    refetchInterval: 30000,
  });

  const totalReports = reports?.length || 0;
  const reportsLast24h = reports?.filter((report) => {
    const createdAt = new Date(report.created_at);
    const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000);
    return createdAt > yesterday;
  }).length || 0;

  const verifiedReports = reports?.filter((report) => report.status === 'VERIFIED').length || 0;
  const activeAlerts = alerts?.filter((alert) => alert.status === 'ACTIVE').length || 0;
  const criticalAlerts = alerts?.filter((alert) => alert.severity === 'CRITICAL' && alert.status === 'ACTIVE').length || 0;
  const highSeverityAlerts = alerts?.filter((alert) => alert.status === 'ACTIVE' && ['CRITICAL', 'HIGH'].includes(alert.severity)) || [];
  const generatedAlerts = alerts?.length || 0;
  const dispatchActivity = dispatches?.length || 0;
  const activeIncidentIds = new Set([
    ...(alerts?.filter((alert) => alert.status === 'ACTIVE').map((alert) => alert.incident_id).filter(Boolean) || []),
    ...(reports?.filter((report) => report.status !== 'RESOLVED' && report.incident_id).map((report) => report.incident_id as string) || []),
  ]);

  const verificationRate = normalizePercentScore(verificationStats?.verification_rate);
  const averageConfidence = normalizePercentScore(verificationStats?.average_confidence);
  const pendingVerifications = verificationStats?.total_pending || 0;
  const serviceEntries = Object.entries(health?.services || {});
  const systemHealthy = ['healthy', 'ok'].includes((health?.status || '').toLowerCase())
    && serviceEntries.every(([, status]) => !['down', 'failed', 'error', 'disconnected'].includes(status.toLowerCase()));

  const recentActivity = [
    ...(reports?.slice(0, 5).map((report) => ({
      type: 'report' as const,
      id: report.id,
      title: `${report.crisis_type} report received`,
      description: report.description.length > 72 ? `${report.description.substring(0, 72)}...` : report.description,
      timestamp: report.created_at,
      status: report.status,
    })) || []),
    ...(alerts?.slice(0, 5).map((alert) => ({
      type: 'alert' as const,
      id: alert.id,
      title: `${alert.severity} alert issued`,
      description: alert.alert_message.length > 72 ? `${alert.alert_message.substring(0, 72)}...` : alert.alert_message,
      timestamp: alert.created_at,
      severity: alert.severity,
    })) || []),
  ]
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 8);

  const isLoading = reportsLoading || alertsLoading || statsLoading || healthLoading || dispatchLoading;
  const hasError = reportsError || alertsError || statsError || healthError || dispatchError;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (hasError) {
    return (
      <ErrorAlert
        title="Failed to load dashboard data"
        message="Please check your connection and try again."
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="page-kicker mb-2">Operations overview</div>
          <Title level={2} className="!mb-1">
            <DashboardOutlined className="mr-2" />
            Command Center
          </Title>
          <Text type="secondary">Real-time crisis intelligence, verification, alerting, and dispatch coordination.</Text>
        </div>
        <Space wrap>
          <Tag color={systemHealthy ? 'success' : 'error'} className="px-3 py-1 font-semibold">
            {systemHealthy ? 'System Stable' : 'System Attention Required'}
          </Tag>
          <Tag color="processing" className="px-3 py-1 font-semibold">Auto-refresh 30s</Tag>
        </Space>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} xl={8} xxl={4}>
          <StatisticsCard
            title="Total Reports"
            value={totalReports}
            trend={reportsLast24h > 0 ? 15 : 0}
            change={`${reportsLast24h} in last 24h`}
            icon={<FileTextOutlined />}
            type="info"
          />
        </Col>
        <Col xs={24} sm={12} xl={8} xxl={4}>
          <StatisticsCard
            title="Verified Reports"
            value={verifiedReports}
            change={`${formatPercentScore(totalReports ? (verifiedReports / totalReports) : 0)} verified`}
            icon={<CheckCircleOutlined />}
            type="success"
          />
        </Col>
        <Col xs={24} sm={12} xl={8} xxl={4}>
          <StatisticsCard
            title="Active Incidents"
            value={activeIncidentIds.size}
            change={`${criticalAlerts} critical alerts`}
            icon={<ClusterOutlined />}
            type={criticalAlerts > 0 ? 'danger' : 'warning'}
          />
        </Col>
        <Col xs={24} sm={12} xl={8} xxl={4}>
          <StatisticsCard
            title="Generated Alerts"
            value={generatedAlerts}
            change={`${activeAlerts} active`}
            icon={<AlertOutlined />}
            type={activeAlerts > 0 ? 'warning' : 'info'}
          />
        </Col>
        <Col xs={24} sm={12} xl={8} xxl={4}>
          <StatisticsCard
            title="Dispatch Activity"
            value={dispatchActivity}
            change={`${dispatches?.filter((dispatch) => ['ARRIVED', 'COMPLETED'].includes(dispatch.status)).length || 0} on scene/done`}
            icon={<SendOutlined />}
            type="info"
          />
        </Col>
        <Col xs={24} sm={12} xl={8} xxl={4}>
          <StatisticsCard
            title="System Health"
            value={systemHealthy ? 'Stable' : 'Issues'}
            icon={systemHealthy ? <CheckCircleOutlined /> : <WarningOutlined />}
            type={systemHealthy ? 'success' : 'danger'}
            change={`${serviceEntries.length || 0} services`}
          />
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} xl={8}>
          <Card
            title={
              <span className="font-semibold">
                <RadarChartOutlined className="mr-2" />
                Agent Verification
              </span>
            }
            className="h-full"
          >
            <div className="space-y-5">
              <Progress
                type="dashboard"
                percent={Math.round(verificationRate)}
                strokeColor={verificationRate >= 80 ? '#16a34a' : '#f59e0b'}
                trailColor="#e2e8f0"
              />
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="rounded-lg bg-slate-50 p-3">
                  <div className="text-lg font-bold text-slate-900">{verificationStats?.total_verified || 0}</div>
                  <div className="text-xs text-slate-500">Verified</div>
                </div>
                <div className="rounded-lg bg-slate-50 p-3">
                  <div className="text-lg font-bold text-slate-900">{pendingVerifications}</div>
                  <div className="text-xs text-slate-500">Pending</div>
                </div>
                <div className="rounded-lg bg-slate-50 p-3">
                  <div className="text-lg font-bold text-slate-900">{formatPercentScore(averageConfidence)}</div>
                  <div className="text-xs text-slate-500">Avg. confidence</div>
                </div>
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={24} xl={8}>
          <Card
            title={
              <span className="font-semibold">
                <SafetyOutlined className="mr-2" />
                High-Severity Incidents
              </span>
            }
            className="h-full"
          >
            <List
              dataSource={highSeverityAlerts.slice(0, 5)}
              locale={{ emptyText: 'No high-severity active alerts' }}
              renderItem={(alert) => (
                <List.Item className="px-0">
                  <List.Item.Meta
                    title={
                      <div className="flex items-center justify-between gap-3">
                        <span className="font-medium">{alert.alert_title}</span>
                        <SeverityBadge severity={alert.severity} />
                      </div>
                    }
                    description={
                      <div className="text-sm text-slate-500">
                        {alert.location_text || `${alert.latitude.toFixed(4)}, ${alert.longitude.toFixed(4)}`}
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        <Col xs={24} xl={8}>
          <Card
            title={
              <span className="font-semibold">
                <CheckCircleOutlined className="mr-2" />
                System Health
              </span>
            }
            className="h-full"
          >
            <div className="space-y-3">
              {serviceEntries.length === 0 ? (
                <Text type="secondary">No service details returned by the health endpoint.</Text>
              ) : (
                serviceEntries.map(([service, status]) => (
                  <div key={service} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
                    <span className="font-medium capitalize text-slate-700">{service.replace(/_/g, ' ')}</span>
                    <Tag color={['connected', 'configured', 'ok', 'healthy'].includes(status.toLowerCase()) ? 'success' : 'warning'}>
                      {status}
                    </Tag>
                  </div>
                ))
              )}
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={7}>
          <Card
            title={
              <span className="font-semibold">
                <SendOutlined className="mr-2" />
                Quick Actions
              </span>
            }
            className="h-full"
          >
            <Space direction="vertical" className="w-full" size="middle">
              <Button type="primary" block icon={<FileTextOutlined />} onClick={() => router.push('/admin/reports')}>
                Review Reports
              </Button>
              <Button block icon={<AlertOutlined />} onClick={() => router.push('/admin/alerts')}>
                Monitor Alerts
              </Button>
              <Button block icon={<SendOutlined />} onClick={() => router.push('/admin/dispatch')}>
                Dispatch Logs
              </Button>
              <Button block type="dashed" onClick={() => router.push('/admin/incidents')}>
                Incident Clusters
              </Button>
            </Space>
          </Card>
        </Col>

        <Col xs={24} lg={17}>
          <Card
            title={
              <span className="font-semibold">
                <DashboardOutlined className="mr-2" />
                Recent Activity
              </span>
            }
            className="h-full"
          >
            <List
              dataSource={recentActivity}
              locale={{ emptyText: 'No recent activity' }}
              renderItem={(item) => (
                <List.Item
                  className="cursor-pointer px-2 transition-colors hover:bg-sky-50"
                  onClick={() => {
                    if (item.type === 'report') {
                      router.push(`/citizen/reports/${item.id}`);
                    }
                  }}
                >
                  <List.Item.Meta
                    avatar={
                      item.type === 'report' ? (
                        <FileTextOutlined className="text-xl text-sky-600" />
                      ) : (
                        <AlertOutlined className="text-xl text-orange-500" />
                      )
                    }
                    title={
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-medium">{item.title}</span>
                        {item.type === 'report' && 'status' in item && (
                          <StatusBadge status={item.status} />
                        )}
                        {item.type === 'alert' && 'severity' in item && (
                          <SeverityBadge severity={item.severity} />
                        )}
                      </div>
                    }
                    description={
                      <div className="space-y-1">
                        <div className="text-sm text-slate-600">{item.description}</div>
                        <div className="text-xs text-slate-400">
                          {formatDistanceToNow(new Date(item.timestamp), { addSuffix: true })}
                        </div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}

// Made with Bob
