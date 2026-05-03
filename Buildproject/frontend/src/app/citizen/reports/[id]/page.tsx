/**
 * Report Details Page
 * Displays full details of a specific report
 */

'use client';

import { useParams, useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import { Button, Card, Descriptions, Tag, Space, Typography, Divider, Image } from 'antd';
import {
  ArrowLeftOutlined,
  EnvironmentOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  FileImageOutlined,
  VideoCameraOutlined,
  AlertOutlined,
} from '@ant-design/icons';
import { format } from 'date-fns';
import { CrisisIcon, getCrisisLabel } from '@/components/ui/CrisisIcon';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { IncidentTimeline } from '@/components/cards/IncidentTimeline';
import { useReport } from '@/lib/api';

const { Title, Text, Paragraph } = Typography;
const ReportMap = dynamic(
  () => import('@/components/maps/ReportMap').then((mod) => mod.ReportMap),
  { ssr: false }
);

export default function ReportDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const reportId = params.id as string;

  // Fetch report details
  const { data: report, isLoading, error, refetch } = useReport(reportId);

  const formatTimestamp = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMMM dd, yyyy HH:mm:ss');
    } catch {
      return dateString;
    }
  };

  const handleBack = () => {
    router.push('/citizen/reports');
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <LoadingSpinner message="Loading report details..." size="large" />
      </div>
    );
  }

  // Error state
  if (error || !report) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={handleBack}
          className="mb-4"
        >
          Back to Reports
        </Button>
        <ErrorAlert
          title="Failed to load report"
          message={error?.message || 'Report not found.'}
          onRetry={refetch}
        />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={handleBack}
          className="mb-4"
        >
          Back to Reports
        </Button>
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <CrisisIcon type={report.crisis_type} style={{ fontSize: '2rem' }} />
            <div>
              <Title level={2} className="!mb-0">
                {getCrisisLabel(report.crisis_type)} Report
              </Title>
              <Text type="secondary">Report ID: {report.id}</Text>
            </div>
          </div>
          <StatusBadge status={report.status} />
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Report Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description Card */}
          <Card title="Report Description" className="shadow-sm">
            <Paragraph className="text-base whitespace-pre-wrap">
              {report.description}
            </Paragraph>
          </Card>

          {/* Details Card */}
          <Card title="Report Information" className="shadow-sm">
            <Descriptions column={1} bordered>
              <Descriptions.Item label="Crisis Type">
                <Space>
                  <CrisisIcon type={report.crisis_type} />
                  {getCrisisLabel(report.crisis_type)}
                </Space>
              </Descriptions.Item>
              
              <Descriptions.Item label="Status">
                <StatusBadge status={report.status} />
              </Descriptions.Item>

              <Descriptions.Item label="Submitted">
                <Space>
                  <ClockCircleOutlined />
                  {formatTimestamp(report.created_at)}
                </Space>
              </Descriptions.Item>

              {report.updated_at && report.updated_at !== report.created_at && (
                <Descriptions.Item label="Last Updated">
                  <Space>
                    <ClockCircleOutlined />
                    {formatTimestamp(report.updated_at)}
                  </Space>
                </Descriptions.Item>
              )}

              <Descriptions.Item label="Confidence Score">
                <Space>
                  <CheckCircleOutlined />
                  {Math.round((report.confidence_score || 0) * 100)}%
                </Space>
              </Descriptions.Item>

              <Descriptions.Item label="Severity Score">
                <Tag color={report.severity_score > 0.7 ? 'red' : report.severity_score > 0.4 ? 'orange' : 'blue'}>
                  {Math.round((report.severity_score || 0) * 100)}%
                </Tag>
              </Descriptions.Item>

              <Descriptions.Item label="Source">
                <Tag>{report.source}</Tag>
              </Descriptions.Item>

              <Descriptions.Item label="Anonymous">
                {report.is_anonymous ? 'Yes' : 'No'}
              </Descriptions.Item>

              {report.incident_id && (
                <Descriptions.Item label="Incident ID">
                  <Space>
                    <AlertOutlined />
                    {report.incident_id}
                  </Space>
                </Descriptions.Item>
              )}
            </Descriptions>
          </Card>

          {/* Media Attachments */}
          {(report.image_url || report.video_url) && (
            <Card title="Media Attachments" className="shadow-sm">
              <Space direction="vertical" size="large" className="w-full">
                {report.image_url && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <FileImageOutlined />
                      <Text strong>Image</Text>
                    </div>
                    <Image
                      src={report.image_url}
                      alt="Report image"
                      className="rounded-lg"
                      style={{ maxHeight: 400 }}
                    />
                  </div>
                )}
                
                {report.video_url && (
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <VideoCameraOutlined />
                      <Text strong>Video</Text>
                    </div>
                    <video
                      src={report.video_url}
                      controls
                      className="w-full rounded-lg"
                      style={{ maxHeight: 400 }}
                    >
                      Your browser does not support the video tag.
                    </video>
                  </div>
                )}
              </Space>
            </Card>
          )}

          {/* Timeline */}
          {report.incident_id && (
            <Card title="Incident Timeline" className="shadow-sm">
              <IncidentTimeline report={report} />
            </Card>
          )}
        </div>

        {/* Right Column - Location */}
        <div className="space-y-6">
          {/* Location Card */}
          <Card title="Location" className="shadow-sm">
            <Space direction="vertical" size="middle" className="w-full">
              <div>
                <Text type="secondary" className="block mb-1">
                  <EnvironmentOutlined /> Address
                </Text>
                <Text>
                  {report.location_text || 'No address provided'}
                </Text>
              </div>

              <div>
                <Text type="secondary" className="block mb-1">
                  Coordinates
                </Text>
                <Text copyable>
                  {report.latitude.toFixed(6)}, {report.longitude.toFixed(6)}
                </Text>
              </div>

              <Divider className="my-2" />

              {/* Map */}
              <div className="w-full">
                <ReportMap report={report} className="h-64 w-full rounded-lg" />
              </div>
            </Space>
          </Card>

          {/* Quick Actions */}
          <Card title="Quick Actions" className="shadow-sm">
            <Space direction="vertical" className="w-full">
              <Button
                type="default"
                block
                icon={<EnvironmentOutlined />}
                onClick={() => {
                  window.open(
                    `https://www.google.com/maps?q=${report.latitude},${report.longitude}`,
                    '_blank'
                  );
                }}
              >
                View in Google Maps
              </Button>
              
              {report.incident_id && (
                <Button
                  type="default"
                  block
                  icon={<AlertOutlined />}
                  onClick={() => {
                    // Navigate to incident details if available
                    router.push(`/citizen/incidents/${report.incident_id}`);
                  }}
                >
                  View Related Incident
                </Button>
              )}
            </Space>
          </Card>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
