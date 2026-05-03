/**
 * Admin Reports Page
 * Manage and view all crisis reports
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Table, Typography, Button, Tag } from 'antd';
import { FileTextOutlined, EyeOutlined, DownloadOutlined } from '@ant-design/icons';
import { FilterPanel, type FilterConfig } from '@/components/ui/FilterPanel';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { getCrisisLabel } from '@/components/ui/CrisisIcon';
import type { ReportResponse, CrisisType, IncidentStatus } from '@/types/api';
import { formatPercentScore, normalizePercentScore } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';
import type { ColumnsType } from 'antd/es/table';
import apiClient from '@/lib/api/client';

const { Title, Text } = Typography;

// Fetch reports using apiClient (attaches Authorization header)
const fetchReports = async (): Promise<ReportResponse[]> => {
  const response = await apiClient.get<ReportResponse[]>('/reports');
  return response.data;
};

// Filter configurations for report table
const filterConfigs: FilterConfig[] = [
  {
    name: 'status',
    label: 'Status',
    type: 'multiselect',
    options: [
      { label: 'Pending Verification', value: 'PENDING_VERIFICATION' },
      { label: 'Needs Confirmation', value: 'NEEDS_CONFIRMATION' },
      { label: 'Verified', value: 'VERIFIED' },
      { label: 'Provisional Critical', value: 'PROVISIONAL_CRITICAL' },
      { label: 'Dispatched', value: 'DISPATCHED' },
      { label: 'False Report', value: 'FALSE_REPORT' },
      { label: 'Resolved', value: 'RESOLVED' },
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
    name: 'search',
    label: 'Search',
    type: 'search',
    placeholder: 'Search by description or location...',
  },
];

export default function AdminReportsPage() {
  const router = useRouter();
  const [filters, setFilters] = useState<Record<string, any>>({});
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  // Fetch reports using React Query
  const { data: reports, isLoading, error, refetch } = useQuery({
    queryKey: ['admin-reports'],
    queryFn: fetchReports,
  });

  // Apply filters to reports
  const filteredReports = reports?.filter((report) => {
    // Status filter
    if (filters.status?.length > 0 && !filters.status.includes(report.status)) {
      return false;
    }

    // Crisis type filter
    if (filters.crisis_type?.length > 0 && !filters.crisis_type.includes(report.crisis_type)) {
      return false;
    }

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      const matchesDescription = report.description.toLowerCase().includes(searchLower);
      const matchesLocation = report.location_text?.toLowerCase().includes(searchLower);
      if (!matchesDescription && !matchesLocation) {
        return false;
      }
    }

    return true;
  }) || [];

  // Define table columns
  const columns: ColumnsType<ReportResponse> = [
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
      render: (type: CrisisType) => <Tag color="blue">{getCrisisLabel(type)}</Tag>,
      sorter: (a, b) => a.crisis_type.localeCompare(b.crisis_type),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 180,
      render: (status: IncidentStatus) => <StatusBadge status={status} />,
      sorter: (a, b) => a.status.localeCompare(b.status),
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence_score',
      key: 'confidence_score',
      width: 130,
      render: (score: number) => (
        <span
          className={
            normalizePercentScore(score) > 80
              ? 'text-green-600 font-medium'
              : normalizePercentScore(score) > 50
              ? 'text-yellow-600'
              : 'text-red-600'
          }
        >
          {formatPercentScore(score)}
        </span>
      ),
      sorter: (a, b) => normalizePercentScore(a.confidence_score) - normalizePercentScore(b.confidence_score),
    },
    {
      title: 'Location',
      dataIndex: 'location_text',
      key: 'location',
      ellipsis: true,
      render: (text: string | undefined, record: ReportResponse) => (
        <Text ellipsis className="text-sm">
          {text || `${record.latitude.toFixed(4)}, ${record.longitude.toFixed(4)}`}
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
      defaultSortOrder: 'descend',
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      fixed: 'right',
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => router.push(`/admin/reports/${record.id}`)}
        >
          View
        </Button>
      ),
    },
  ];

  // Export to CSV handler (unchanged)
  const handleExport = () => {
    if (!filteredReports.length) return;

    const headers = ['ID', 'Crisis Type', 'Status', 'Confidence', 'Description', 'Location', 'Created At'];
    const rows = filteredReports.map((r) => [
      r.id,
      r.crisis_type,
      r.status,
      formatPercentScore(r.confidence_score),
      r.description.replace(/,/g, ';'),
      r.location_text || `${r.latitude},${r.longitude}`,
      r.created_at,
    ]);

    const csv = [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reports-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

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
          title="Failed to load reports"
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
          <div className="page-kicker mb-2">Community intake</div>
          <Title level={2} className="!mb-1">
            <FileTextOutlined className="mr-2" />
            Report Management
          </Title>
          <Text type="secondary">
            {filteredReports.length} of {reports?.length || 0} reports
          </Text>
        </div>
        <Button
          icon={<DownloadOutlined />}
          onClick={handleExport}
          disabled={filteredReports.length === 0}
        >
          Export CSV
        </Button>
      </div>

      {/* Filters */}
      <FilterPanel
        filters={filterConfigs}
        onApply={setFilters}
        onReset={() => setFilters({})}
        defaultCollapsed={false}
      />

      {/* Reports Table */}
      <div className="ops-panel overflow-hidden rounded-lg">
        <Table
          columns={columns}
          dataSource={filteredReports}
          rowKey="id"
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: filteredReports.length,
            showSizeChanger: false,
            showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} reports`,
            onChange: (page) => setCurrentPage(page),
          }}
          scroll={{ x: 1200 }}
          onRow={(record) => ({
            onClick: () => router.push(`/admin/reports/${record.id}`),
            className: 'cursor-pointer hover:bg-gray-50',
          })}
        />
      </div>
    </div>
  );
}

// Made with Bob
