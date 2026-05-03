/**
 * Admin Incidents Page
 * Manage and view incident clusters
 */

'use client';

import { useRouter } from 'next/navigation';
import { Card, Typography, Button, Result } from 'antd';
import { ClusterOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

export default function AdminIncidentsPage() {
  const router = useRouter();

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <div className="page-kicker mb-2">Incident clustering</div>
        <Title level={2} className="!mb-1">
          <ClusterOutlined className="mr-2" />
          Incident Management
        </Title>
      </div>

      <Card className="ops-panel">
        <Result
          icon={<ClusterOutlined className="text-blue-500" />}
          title="Incident Management Coming Soon"
          subTitle="This feature will allow you to view and manage incident clusters created from multiple related reports."
          extra={[
            <Button
              key="dashboard"
              type="primary"
              onClick={() => router.push('/admin/dashboard')}
            >
              Back to Dashboard
            </Button>,
            <Button
              key="reports"
              onClick={() => router.push('/admin/reports')}
            >
              View Reports
            </Button>,
          ]}
        >
          <div className="text-left max-w-2xl mx-auto space-y-4">
            <Paragraph>
              <strong>What are Incidents?</strong>
            </Paragraph>
            <Paragraph>
              Incidents are clusters of related reports that have been grouped together by our AI clustering system.
              This helps identify larger crisis events that span multiple reports from different sources.
            </Paragraph>
            <Paragraph>
              <strong>Planned Features:</strong>
            </Paragraph>
            <ul className="list-disc list-inside space-y-2 text-gray-600">
              <li>View all incident clusters with their related reports</li>
              <li>Track incident severity and status over time</li>
              <li>See geographic distribution of incidents</li>
              <li>Manage incident lifecycle (active, monitoring, resolved)</li>
              <li>View alerts and dispatches associated with each incident</li>
            </ul>
          </div>
        </Result>
      </Card>
    </div>
  );
}

// Made with Bob
