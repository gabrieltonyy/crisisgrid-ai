/**
 * Advisory Card Component
 * Displays safety advisory information in card format
 */

'use client';

import { Card, Alert, Divider } from 'antd';
import { 
  PhoneOutlined, 
  ExclamationCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import { CrisisIcon, getCrisisLabel, getCrisisColor } from '../ui/CrisisIcon';
import { SeverityBadge } from '../ui/SeverityBadge';
import type { AdvisoryResponse } from '@/types/api';

interface AdvisoryCardProps {
  advisory: AdvisoryResponse;
  className?: string;
}

export function AdvisoryCard({ advisory, className = '' }: AdvisoryCardProps) {
  const crisisColor = getCrisisColor(advisory.crisis_type);

  return (
    <Card
      className={`shadow-md ${className}`}
      variant="borderless"
      style={{ borderTop: `4px solid ${crisisColor}` }}
    >
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <CrisisIcon type={advisory.crisis_type} style={{ fontSize: '2rem' }} />
            <div>
              <h2 className="text-xl font-bold m-0">
                {getCrisisLabel(advisory.crisis_type)} Safety Advisory
              </h2>
              <p className="text-sm text-gray-500 m-0">
                {advisory.ai_enhanced ? 'AI-Enhanced Guidance' : 'Standard Guidance'}
              </p>
            </div>
          </div>
          <SeverityBadge severity={advisory.severity} showIcon />
        </div>

        {/* Risk Level Alert */}
        <Alert
          message={`Risk Level: ${advisory.risk_level.toUpperCase()}`}
          description={advisory.primary_advice}
          type={advisory.severity === 'CRITICAL' ? 'error' : advisory.severity === 'HIGH' ? 'warning' : 'info'}
          showIcon
          icon={<ExclamationCircleOutlined />}
          className="mb-4"
        />

        {/* Distance Info */}
        {advisory.distance_meters !== undefined && (
          <div className="text-sm text-gray-600 mb-2">
            <InfoCircleOutlined className="mr-1" />
            Distance from incident: {advisory.distance_meters < 1000 
              ? `${Math.round(advisory.distance_meters)}m` 
              : `${(advisory.distance_meters / 1000).toFixed(1)}km`}
          </div>
        )}
      </div>

      <Divider className="my-4" />

      {/* Immediate Actions */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
          Immediate Actions Required
        </h3>
        <div className="space-y-3">
          {advisory.immediate_actions.map((action, index) => (
            <div 
              key={index}
              className="flex gap-3 p-3 bg-red-50 border border-red-200 rounded-lg"
            >
              <div className="flex-shrink-0 w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center font-bold">
                {action.priority}
              </div>
              <div className="flex-1">
                <p className="font-medium text-gray-900 mb-1">{action.action}</p>
                <p className="text-sm text-gray-600">{action.rationale}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <Divider className="my-4" />

      {/* What to Do */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <CheckCircleOutlined style={{ color: '#52c41a' }} />
          What to Do
        </h3>
        <ul className="space-y-2">
          {advisory.what_to_do.map((tip, index) => (
            <li key={index} className="flex items-start gap-2">
              <CheckCircleOutlined className="text-green-500 mt-1 flex-shrink-0" />
              <span className="text-gray-700">{tip}</span>
            </li>
          ))}
        </ul>
      </div>

      <Divider className="my-4" />

      {/* What NOT to Do */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
          What NOT to Do
        </h3>
        <ul className="space-y-2">
          {advisory.what_not_to_do.map((avoid, index) => (
            <li key={index} className="flex items-start gap-2">
              <CloseCircleOutlined className="text-red-500 mt-1 flex-shrink-0" />
              <span className="text-gray-700">{avoid}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Evacuation Advice */}
      {advisory.evacuation_advice && (
        <>
          <Divider className="my-4" />
          <Alert
            message="Evacuation Guidance"
            description={advisory.evacuation_advice}
            type="warning"
            showIcon
            className="mb-4"
          />
        </>
      )}

      <Divider className="my-4" />

      {/* Emergency Contacts */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <PhoneOutlined style={{ color: '#1890ff' }} />
          Emergency Contacts
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {advisory.emergency_contacts.map((contact, index) => (
            <a
              key={index}
              href={`tel:${contact.number}`}
              className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <span className="font-medium text-gray-900">{contact.service}</span>
              <span className="text-blue-600 font-semibold">{contact.number}</span>
            </a>
          ))}
        </div>
      </div>

      {/* Additional Resources */}
      {advisory.additional_resources.length > 0 && (
        <>
          <Divider className="my-4" />
          <div>
            <h3 className="text-sm font-semibold mb-2 text-gray-600">Additional Resources</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              {advisory.additional_resources.map((resource, index) => (
                <li key={index}>• {resource}</li>
              ))}
            </ul>
          </div>
        </>
      )}

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500">
        <div className="flex justify-between items-center">
          <span>Playbook: {advisory.playbook_used}</span>
          <span>Generated: {new Date(advisory.generated_at).toLocaleString()}</span>
        </div>
      </div>
    </Card>
  );
}

// Made with Bob
