/**
 * Admin Dispatch Page
 * Monitor and coordinate emergency response dispatches
 */

'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Table, Typography, Tag, Timeline } from 'antd';
import { SendOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { FilterPanel, type FilterConfig } from '@/components/ui/FilterPanel';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import type { DispatchResponse, AuthorityType, DispatchStatus } from '@/types/api';
import { formatDistanceToNow } from 'date-fns';
import type { ColumnsType } from 'antd/es/table';
import apiClient from '@/lib/api/client';

const { Title, Text } = Typography;

// Fetch dispatch logs
const fetchDispatchLogs = async (): Promise<DispatchResponse[]> => {
  const response = await apiClient.get<DispatchResponse[]>('/dispatch/logs');
  return response.data;
};

// Status badge component
const DispatchStatusBadge = ({ status }: { status: DispatchStatus }) => {
  const config = {
    PENDING: { color: 'default', label: 'Pending' },
    SIMULATED_SENT: { color: 'blue', label: 'Simulated Sent' },
    SENT: { color: 'processing', label: 'Sent' },
    ACKNOWLEDGED: { color: 'warning', label: 'Acknowledged' },
    ARRIVED: { color: 'purple', label: 'Arrived' },
    COMPLETED: { color: 'success', label: 'Completed' },
    CANCELLED: { color: 'default', label: 'Cancelled' },
    FAILED: { color: 'error', label: 'Failed' },
  };

  const { color, label } = config[status] || { color: 'default', label: status };

  return <Tag color={color}>{label}</Tag>;
};

// Authority type badge
const AuthorityBadge = ({ type }: { type: AuthorityType }) => {
  const config = {
    FIRE_SERVICE: { color: 'red', label: 'Fire Service' },
    DISASTER_MANAGEMENT: { color: 'orange', label: 'Disaster Mgmt' },
    WILDLIFE_AUTHORITY: { color: 'green', label: 'Wildlife' },
    POLICE: { color: 'blue', label: 'Police' },
    AMBULANCE: { color: 'purple', label: 'Ambulance' },
    PUBLIC_HEALTH: { color: 'magenta', label: 'Public Health' },
    FIRE_DEPARTMENT: { color: 'red', label: 'Fire Department' },
  };

  const { color, label } = config[type] || { color: 'default', label: type };

  return (
    <Tag color={color} className="font-medium">
      {label}
    </Tag>
  );
};

// Filter configurations
const filterConfigs: FilterConfig[] = [
  {
    name: 'authority_type',
    label: 'Authority Type',
    type: 'multiselect',
    options: [
      { label: 'Fire Service', value: 'FIRE_SERVICE' },
      { label: 'Disaster Management', value: 'DISASTER_MANAGEMENT' },
      { label: 'Wildlife Authority', value: 'WILDLIFE_AUTHORITY' },
      { label: 'Police', value: 'POLICE' },
      { label: 'Ambulance', value: 'AMBULANCE' },
      { label: 'Public Health', value: 'PUBLIC_HEALTH' },
    ],
  },
  {
    name: 'status',
    label: 'Status',
    type: 'multiselect',
    options: [
      { label: 'Simulated Sent', value: 'SIMULATED_SENT' },
      { label: 'Sent', value: 'SENT' },
      { label: 'Acknowledged', value: 'ACKNOWLEDGED' },
      { label: 'Arrived', value: 'ARRIVED' },
      { label: 'Completed', value: 'COMPLETED' },
      { label: 'Cancelled', value: 'CANCELLED' },
      { label: 'Failed', value: 'FAILED' },
    ],
  },
];

export default function AdminDispatchPage() {
  const [filters, setFilters] = useState<Record<string, any>>({});
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  // Fetch dispatch logs
  const { data: dispatches, isLoading, error, refetch } = useQuery({
    queryKey: ['dispatch-logs'],
    queryFn: fetchDispatchLogs,
  });

  // Apply filters
  const filteredDispatches = dispatches?.filter((dispatch) => {
    // Authority type filter
    if (filters.authority_type?.length > 0 && !filters.authority_type.includes(dispatch.authority_type)) {
      return false;
    }

    // Status filter
    if (filters.status?.length > 0 && !filters.status.includes(dispatch.status)) {
      return false;
    }

    return true;
  }) || [];

  // Group dispatches by incident for timeline view
  const dispatchTimeline = filteredDispatches.slice(0, 10).map((dispatch) => ({
    color: dispatch.status === 'COMPLETED' ? 'green' : dispatch.status === 'FAILED' ? 'red' : 'blue',
    children: (
      <div className="space-y-2">
        <div className="flex items-center gap-2 flex-wrap">
          <AuthorityBadge type={dispatch.authority_type} />
          <DispatchStatusBadge status={dispatch.status} />
          <Text code className="text-xs">{dispatch.id.substring(0, 8)}</Text>
        </div>
        <Text className="text-sm text-gray-600">
          {dispatch.message || `Dispatched to ${dispatch.authority_type}`}
        </Text>
        <Text className="text-xs text-gray-400">
          {formatDistanceToNow(new Date(dispatch.created_at), { addSuffix: true })}
        </Text>
      </div>
    ),
  }));

  // Table columns
  const columns: ColumnsType<DispatchResponse> = [
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
      title: 'Authority Type',
      dataIndex: 'authority_type',
      key: 'authority_type',
      width: 180,
      render: (type: AuthorityType) => <AuthorityBadge type={type} />,
      sorter: (a, b) => a.authority_type.localeCompare(b.authority_type),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 150,
      render: (status: DispatchStatus) => <DispatchStatusBadge status={status} />,
      sorter: (a, b) => a.status.localeCompare(b.status),
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority: string) => (
        <Tag color={priority === 'HIGH' ? 'red' : priority === 'MEDIUM' ? 'orange' : 'default'}>
          {priority}
        </Tag>
      ),
    },
    {
      title: 'Message',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
      render: (text: string | undefined) => (
        <Text ellipsis className="text-sm">
          {text || 'No message'}
        </Text>
      ),
    },
    {
      title: 'Location',
      dataIndex: 'location_text',
      key: 'location',
      width: 150,
      ellipsis: true,
      render: (text: string | undefined, record: DispatchResponse) => (
        <Text ellipsis className="text-sm">
          {text || `${record.latitude.toFixed(4)}, ${record.longitude.toFixed(4)}`}
        </Text>
      ),
    },
    {
      title: 'Response Time',
      dataIndex: 'response_time_seconds',
      key: 'response_time',
      width: 130,
      render: (seconds: number | undefined) => (
        <Text className="text-xs text-gray-600">
          {seconds ? `${Math.round(seconds / 60)}m` : 'N/A'}
        </Text>
      ),
    },
    {
      title: 'Dispatched',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date: string) => (
        <Text className="text-xs text-gray-600">
          {formatDistanceToNow(new Date(date), { addSuffix: true })}
        </Text>
      ),
      sorter: (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
      defaultSortOrder: 'descend',
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
          title="Failed to load dispatch logs"
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
          <div className="page-kicker mb-2">Response coordination</div>
          <Title level={2} className="!mb-1">
            <SendOutlined className="mr-2" />
            Dispatch Coordination
          </Title>
          <Text type="secondary">
            {filteredDispatches.length} of {dispatches?.length || 0} dispatch logs
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

      {/* Recent Dispatch Timeline */}
      {dispatchTimeline.length > 0 && (
        <div className="ops-panel rounded-lg p-6">
          <Title level={4} className="!mb-4">
            <ClockCircleOutlined className="mr-2" />
            Recent Dispatch Activity
          </Title>
          <Timeline items={dispatchTimeline} />
        </div>
      )}

      {/* Dispatch Logs Table */}
      <div className="ops-panel overflow-hidden rounded-lg">
        <Table
          columns={columns}
          dataSource={filteredDispatches}
          rowKey="id"
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: filteredDispatches.length,
            showSizeChanger: false,
            showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} dispatches`,
            onChange: (page) => setCurrentPage(page),
          }}
          scroll={{ x: 1300 }}
        />
      </div>
    </div>
  );
}

// Made with Bob
