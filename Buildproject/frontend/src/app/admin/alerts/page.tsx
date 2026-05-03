/**
 * Admin Alerts Page
 * Monitor and manage all crisis alerts
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Table, Typography, Button, Tag } from 'antd';
import { AlertOutlined, EyeOutlined } from '@ant-design/icons';
import { FilterPanel, type FilterConfig } from '@/components/ui/FilterPanel';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { SeverityBadge } from '@/components/ui/SeverityBadge';
import { getCrisisLabel } from '@/components/ui/CrisisIcon';
import type { AlertResponse, CrisisType, SeverityLevel, AlertStatus } from '@/types/api';
import { formatDistanceToNow } from 'date-fns';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '/api/v1';

// Fetch alerts
const fetchAlerts = async (): Promise<AlertResponse[]> => {
  const response = await fetch(`${API_BASE_URL}/alerts`);
  if (!response.ok) throw new Error('Failed to fetch alerts');
  return response.json();
};

// Status badge component
const AlertStatusBadge = ({ status }: { status: AlertStatus }) => {
  const config = {
    ACTIVE: { color: 'green', label: 'Active' },
    EXPIRED: { color: 'default', label: 'Expired' },
    CANCELLED: { color: 'red', label: 'Cancelled' },
  };

  const { color, label } = config[status] || { color: 'default', label: status };

    return <Tag color={color} className="font-medium">{label}</Tag>;
};

// Filter configurations
const filterConfigs: FilterConfig[] = [
  {
    name: 'severity',
    label: 'Severity',
    type: 'multiselect',
    options: [
      { label: 'Critical', value: 'CRITICAL' },
      { label: 'High', value: 'HIGH' },
      { label: 'Medium', value: 'MEDIUM' },
      { label: 'Low', value: 'LOW' },
    ],
  },
  {
    name: 'crisis_type',
    label: 'Crisis Type',
    type: 'multiselect',
    options: [
      { label: 'Fire', value: 'FIRE' },
      { label: 'Flood', value: 'FLOOD' },
      { label: 'Wildlife', value: 'WILDLIFE' },
      { label: 'Accident', value: 'ACCIDENT' },
      { label: 'Security', value: 'SECURITY' },
      { label: 'Health', value: 'HEALTH' },
      { label: 'Landslide', value: 'LANDSLIDE' },
      { label: 'Hazardous Spill', value: 'HAZARDOUS_SPILL' },
      { label: 'Other', value: 'OTHER' },
    ],
  },
  {
    name: 'status',
    label: 'Status',
    type: 'select',
    options: [
      { label: 'Active', value: 'ACTIVE' },
      { label: 'Expired', value: 'EXPIRED' },
      { label: 'Cancelled', value: 'CANCELLED' },
    ],
  },
  {
    name: 'search',
    label: 'Search',
    type: 'search',
    placeholder: 'Search by message or location...',
  },
];

export default function AdminAlertsPage() {
  const router = useRouter();
  const [filters, setFilters] = useState<Record<string, any>>({});
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  // Fetch alerts with auto-refresh
  const { data: alerts, isLoading, error, refetch } = useQuery({
    queryKey: ['admin-alerts'],
    queryFn: fetchAlerts,
    refetchInterval: 30000, // 30 seconds
  });

  // Apply filters
  const filteredAlerts = alerts?.filter((alert) => {
    // Severity filter
    if (filters.severity?.length > 0 && !filters.severity.includes(alert.severity)) {
      return false;
    }

    // Crisis type filter
    if (filters.crisis_type?.length > 0 && !filters.crisis_type.includes(alert.crisis_type)) {
      return false;
    }

    // Status filter
    if (filters.status && alert.status !== filters.status) {
      return false;
    }

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      const matchesMessage = alert.alert_message.toLowerCase().includes(searchLower);
      const matchesLocation = alert.location_text?.toLowerCase().includes(searchLower);
      if (!matchesMessage && !matchesLocation) {
        return false;
      }
    }

    return true;
  }) || [];

  // Table columns
  const columns: ColumnsType<AlertResponse> = [
    {
      title: 'Reference',
      dataIndex: 'id',
      key: 'id',
      width: 120,
      render: (id: string) => (
        <Text code className="text-xs">
          {id.substring(0, 8)}
        </Text>
      ),
    },
    {
      title: 'Crisis Type',
      dataIndex: 'crisis_type',
      key: 'crisis_type',
      width: 130,
      render: (type: CrisisType) => (
        <Tag color="blue">{getCrisisLabel(type)}</Tag>
      ),
      sorter: (a, b) => a.crisis_type.localeCompare(b.crisis_type),
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      width: 110,
      render: (severity: SeverityLevel) => <SeverityBadge severity={severity} />,
      sorter: (a, b) => {
        const order = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
        return order[a.severity] - order[b.severity];
      },
      defaultSortOrder: 'descend',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: AlertStatus) => <AlertStatusBadge status={status} />,
      sorter: (a, b) => a.status.localeCompare(b.status),
    },
    {
      title: 'Message',
      dataIndex: 'alert_message',
      key: 'alert_message',
      ellipsis: true,
      render: (text: string) => (
        <Text ellipsis className="text-sm">
          {text}
        </Text>
      ),
    },
    {
      title: 'Area',
      dataIndex: 'location_text',
      key: 'location',
      width: 150,
      ellipsis: true,
      render: (text: string | undefined, record: AlertResponse) => (
        <Text ellipsis className="text-sm">
          {text || `${record.latitude.toFixed(4)}, ${record.longitude.toFixed(4)}`}
        </Text>
      ),
    },
    {
      title: 'Radius',
      dataIndex: 'target_radius_meters',
      key: 'radius',
      width: 100,
      render: (radius: number) => (
        <Text className="text-xs text-gray-600">
          {radius >= 1000 ? `${(radius / 1000).toFixed(1)}km` : `${radius}m`}
        </Text>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date: string) => (
        <Text className="text-xs text-gray-600">
          {formatDistanceToNow(new Date(date), { addSuffix: true })}
        </Text>
      ),
      sorter: (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      fixed: 'right',
      render: () => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => router.push(`/citizen/alerts`)}
        >
          View
        </Button>
      ),
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <ErrorAlert
          title="Failed to load alerts"
          message="Please check your connection and try again."
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  return (
      <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <div className="page-kicker mb-2">Public warning feed</div>
          <Title level={2} className="!mb-1">
            <AlertOutlined className="mr-2" />
            Alert Monitoring
          </Title>
          <Text type="secondary">
            {filteredAlerts.length} of {alerts?.length || 0} alerts
            {' • '}
            <span className="text-green-600 font-medium">
              Auto-refreshing every 30s
            </span>
          </Text>
        </div>
      </div>

      {/* Filters */}
      <FilterPanel
        filters={filterConfigs}
        onApply={setFilters}
        onReset={() => setFilters({})}
        defaultCollapsed={false}
      />

      {/* Alerts Table */}
      <div className="ops-panel overflow-hidden rounded-lg">
        <Table
          columns={columns}
          dataSource={filteredAlerts}
          rowKey="id"
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: filteredAlerts.length,
            showSizeChanger: false,
            showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} alerts`,
            onChange: (page) => setCurrentPage(page),
          }}
          scroll={{ x: 1300 }}
          rowClassName={(record) => 
            record.severity === 'CRITICAL' && record.status === 'ACTIVE' 
              ? 'bg-red-50' 
              : ''
          }
        />
      </div>
    </div>
  );
}

// Made with Bob
