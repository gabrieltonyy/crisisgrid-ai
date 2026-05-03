/**
 * Citizen Reports List Page
 * Displays all reports submitted by the citizen
 */

'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { Button, Select, Row, Col, Space, Typography } from 'antd';
import { PlusOutlined, FilterOutlined } from '@ant-design/icons';
import { ReportCard } from '@/components/cards/ReportCard';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { EmptyState } from '@/components/ui/EmptyState';
import { useMyReports } from '@/lib/api';
import type { IncidentStatus } from '@/types/api';

const { Title } = Typography;

type FilterStatus = 'all' | IncidentStatus;
type SortOption = 'newest' | 'oldest';

export default function ReportsPage() {
  const router = useRouter();
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [sortBy, setSortBy] = useState<SortOption>('newest');

  // Fetch user's reports using /reports/me endpoint
  const { data: reports, isLoading, error, refetch } = useMyReports();

  // Filter and sort reports
  const filteredAndSortedReports = useMemo(() => {
    if (!reports) return [];

    let filtered = reports;

    // Apply status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter((report) => report.status === filterStatus);
    }

    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      const dateA = new Date(a.created_at).getTime();
      const dateB = new Date(b.created_at).getTime();
      return sortBy === 'newest' ? dateB - dateA : dateA - dateB;
    });

    return sorted;
  }, [reports, filterStatus, sortBy]);

  // Handle report card click
  const handleReportClick = (reportId: string) => {
    router.push(`/citizen/reports/${reportId}`);
  };

  // Handle new report button
  const handleNewReport = () => {
    router.push('/citizen/report');
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <LoadingSpinner message="Loading your reports..." size="large" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <ErrorAlert
          title="Failed to load reports"
          message={error.message || 'An error occurred while fetching your reports.'}
          onRetry={refetch}
        />
      </div>
    );
  }

  // Empty state
  if (!reports || reports.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <Title level={2} className="!mb-0">My Reports</Title>
        </div>
        <EmptyState
          title="No reports yet"
          description="You haven't submitted any crisis reports. Submit your first report to help your community stay safe."
          action={{
            label: 'Submit First Report',
            onClick: handleNewReport,
          }}
        />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <Title level={2} className="!mb-0">My Reports</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleNewReport}
          size="large"
        >
          New Report
        </Button>
      </div>

      {/* Filters and Sort */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <Space wrap size="middle" className="w-full">
          <div className="flex items-center gap-2">
            <FilterOutlined />
            <span className="font-medium">Filter:</span>
            <Select
              value={filterStatus}
              onChange={setFilterStatus}
              style={{ width: 200 }}
              options={[
                { label: 'All Reports', value: 'all' },
                { label: 'Pending Verification', value: 'PENDING_VERIFICATION' },
                { label: 'Needs Confirmation', value: 'NEEDS_CONFIRMATION' },
                { label: 'Verified', value: 'VERIFIED' },
                { label: 'Provisional Critical', value: 'PROVISIONAL_CRITICAL' },
                { label: 'Dispatched', value: 'DISPATCHED' },
                { label: 'False Report', value: 'FALSE_REPORT' },
                { label: 'Resolved', value: 'RESOLVED' },
              ]}
            />
          </div>

          <div className="flex items-center gap-2">
            <span className="font-medium">Sort:</span>
            <Select
              value={sortBy}
              onChange={setSortBy}
              style={{ width: 150 }}
              options={[
                { label: 'Newest First', value: 'newest' },
                { label: 'Oldest First', value: 'oldest' },
              ]}
            />
          </div>

          <div className="text-sm text-gray-500">
            Showing {filteredAndSortedReports.length} of {reports.length} reports
          </div>
        </Space>
      </div>

      {/* Reports Grid */}
      {filteredAndSortedReports.length === 0 ? (
        <EmptyState
          title="No reports match your filters"
          description="Try adjusting your filters to see more reports."
        />
      ) : (
        <Row gutter={[16, 16]}>
          {filteredAndSortedReports.map((report) => (
            <Col
              key={report.id}
              xs={24}
              sm={24}
              md={12}
              lg={8}
              xl={6}
            >
              <ReportCard
                report={report}
                onClick={() => handleReportClick(report.id)}
              />
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
}

// Made with Bob
