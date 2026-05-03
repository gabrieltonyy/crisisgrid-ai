/**
 * Citizen Report Page
 * Page for citizens to submit crisis reports
 */

'use client';

import { Typography, Alert, Space } from 'antd';
import { 
  WarningOutlined, 
  SafetyOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { ReportForm } from '@/components/forms/ReportForm';
import type { ReportSubmissionResponse } from '@/types/api';

const { Title, Paragraph, Text } = Typography;

export default function ReportPage() {
  const handleSuccess = (_response: ReportSubmissionResponse) => {
    // Scroll to top to show success message
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Page Header */}
      <div className="mb-6">
        <Title level={2} className="mb-2">
          <WarningOutlined className="text-red-500 mr-2" />
          Report a Crisis
        </Title>
        <Paragraph className="text-gray-600 text-lg">
          Help us respond quickly by providing accurate information about the emergency situation.
        </Paragraph>
      </div>

      {/* Important Notice */}
      <Alert
        type="error"
        message="Life-Threatening Emergency?"
        description={
          <div>
            <Paragraph className="mb-2">
              <strong>If this is a life-threatening emergency, call 911 immediately.</strong>
            </Paragraph>
            <Paragraph className="mb-0">
              Use this form for non-life-threatening situations or to provide additional information 
              about an ongoing emergency.
            </Paragraph>
          </div>
        }
        showIcon
        icon={<WarningOutlined />}
        className="mb-6"
      />

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
        <Title level={4} className="text-blue-900 mb-3">
          <SafetyOutlined className="mr-2" />
          How to Report Effectively
        </Title>
        <Space direction="vertical" size="small" className="w-full">
          <div className="flex items-start gap-2">
            <CheckCircleOutlined className="text-green-600 mt-1" />
            <Text>
              <strong>Be Specific:</strong> Describe exactly what you see, hear, or smell
            </Text>
          </div>
          <div className="flex items-start gap-2">
            <CheckCircleOutlined className="text-green-600 mt-1" />
            <Text>
              <strong>Include Details:</strong> Mention landmarks, street names, or building numbers
            </Text>
          </div>
          <div className="flex items-start gap-2">
            <CheckCircleOutlined className="text-green-600 mt-1" />
            <Text>
              <strong>Add Media:</strong> Photos and videos help verify your report faster
            </Text>
          </div>
          <div className="flex items-start gap-2">
            <CheckCircleOutlined className="text-green-600 mt-1" />
            <Text>
              <strong>Stay Safe:</strong> Only report if it is safe to do so - your safety comes first
            </Text>
          </div>
        </Space>
      </div>

      {/* Report Form */}
      <ReportForm onSuccess={handleSuccess} />

      {/* Additional Information */}
      <div className="mt-8 p-6 bg-gray-50 rounded-lg border border-gray-200">
        <Title level={5} className="mb-3">What Happens Next?</Title>
        <Space direction="vertical" size="small" className="w-full text-gray-700">
          <div className="flex items-start gap-2">
            <span className="font-semibold text-blue-600">1.</span>
            <Text>
              Your report is immediately analyzed by our AI verification system
            </Text>
          </div>
          <div className="flex items-start gap-2">
            <span className="font-semibold text-blue-600">2.</span>
            <Text>
              Emergency services are automatically notified based on severity
            </Text>
          </div>
          <div className="flex items-start gap-2">
            <span className="font-semibold text-blue-600">3.</span>
            <Text>
              Nearby citizens receive safety alerts if the situation affects them
            </Text>
          </div>
          <div className="flex items-start gap-2">
            <span className="font-semibold text-blue-600">4.</span>
            <Text>
              You can track your report status in the &quot;My Reports&quot; section
            </Text>
          </div>
        </Space>
      </div>

      {/* Privacy Notice */}
      <Alert
        type="info"
        message="Privacy & Data Usage"
        description={
          <Text className="text-sm">
            Your report data is used solely for emergency response coordination. 
            Location data helps dispatch the nearest resources. Media files are analyzed 
            to verify the crisis and may be shared with emergency responders. 
            We protect your privacy while ensuring effective emergency response.
          </Text>
        }
        showIcon
        className="mt-6"
      />
    </div>
  );
}

// Made with Bob
