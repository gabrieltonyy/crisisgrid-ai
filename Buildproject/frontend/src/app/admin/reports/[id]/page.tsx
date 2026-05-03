/**
 * Admin Report Detail Page
 * Displays a single crisis report details for admin/authority users.
 */

'use client';

import { useParams, useRouter } from 'next/navigation';
import { Button, Card, Typography, Tag, Space } from 'antd';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { getCrisisLabel } from '@/components/ui/CrisisIcon';
import { useReport } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';

const { Title, Text } = Typography;

export default function AdminReportDetailPage() {
  const router = useRouter();
  const params = useParams();

  const reportId = Array.isArray(params?.id)
    ? params.id[0]
    : (params?.id as string);

  const {
    data: report,
    isLoading,
    error,
    refetch,
  } = useReport(reportId ?? '');

  // 🔹 Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  // 🔹 Error state
  if (error) {
    return (
      <div className="p-6">
        <ErrorAlert
          title="Failed to load report"
          message="An error occurred while fetching the report."
          onRetry={refetch}
        />
      </div>
    );
  }

  // 🔹 CRITICAL FIX: Handle undefined report
  if (!report) {
    return (
      <div className="p-6">
        <ErrorAlert
          title="Report not found"
          message="The selected report could not be loaded."
          onRetry={refetch}
        />
      </div>
    );
  }

  // 🔹 Main UI (safe now — report is guaranteed)
  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <div className="page-kicker mb-2">Report Details</div>

          <Title level={2} className="!mb-1">
            <Tag color="blue">{report.id.substring(0, 8)}</Tag>
            {getCrisisLabel(report.crisis_type)}
          </Title>

          <Space size="middle" className="text-sm">
            <StatusBadge status={report.status} />
            <span>
              {formatDistanceToNow(new Date(report.created_at), {
                addSuffix: true,
              })}
            </span>
          </Space>
        </div>

        <Button onClick={() => router.back()}>
          Back to Reports
        </Button>
      </div>

      {/* Report Details */}
      <Card>
        <Space direction="vertical" size="middle" className="w-full">
          <div>
            <Text strong>Description:</Text>
            <p className="whitespace-pre-line mt-1">
              {report.description}
            </p>
          </div>

          <div>
            <Text strong>Location:</Text>
            <p className="mt-1">
              {report.location_text ||
                `${report.latitude.toFixed(4)}, ${report.longitude.toFixed(4)}`}
            </p>
          </div>

          <div>
            <Text strong>Confidence Score:</Text>
            <p className="mt-1">
              {report.confidence_score != null
                ? `${report.confidence_score.toFixed(1)}%`
                : 'N/A'}
            </p>
          </div>

          {report.severity_score != null && (
            <div>
              <Text strong>Severity Score:</Text>
              <p className="mt-1">
                {report.severity_score.toFixed(1)}
              </p>
            </div>
          )}
        </Space>
      </Card>
    </div>
  );
}