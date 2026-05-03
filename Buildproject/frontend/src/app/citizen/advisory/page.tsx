/**
 * Safety Advisory Page
 * Displays crisis-specific safety guidance and recommendations
 */

'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import { useQuery } from '@tanstack/react-query';
import { Button, Space, Alert } from 'antd';
import { PhoneOutlined, ReloadOutlined } from '@ant-design/icons';
import { CrisisTypeSelector } from '@/components/forms/CrisisTypeSelector';
import { AdvisoryCard } from '@/components/cards/AdvisoryCard';
import { SafetyActions } from '@/components/cards/SafetyActions';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { EmptyState } from '@/components/ui/EmptyState';
import apiClient from '@/lib/api/client';
import type { CrisisType, AdvisoryResponse } from '@/types/api';

const AdvisoryMap = dynamic(
  () => import('@/components/maps/AdvisoryMap').then((mod) => mod.AdvisoryMap),
  { ssr: false }
);

export default function AdvisoryPage() {
  const [selectedCrisisType, setSelectedCrisisType] = useState<CrisisType | ''>('');

  // Fetch advisory data
  const {
    data: advisory,
    isLoading,
    error,
    refetch,
  } = useQuery<AdvisoryResponse>({
    queryKey: ['advisory', selectedCrisisType],
    queryFn: async () => {
      const response = await apiClient.get(`/advisory/${selectedCrisisType}`);
      return response.data;
    },
    enabled: selectedCrisisType !== '',
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const handleEmergencyCall = (number: string) => {
    window.location.href = `tel:${number}`;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Safety Advisory</h1>
        <p className="text-gray-600">
          Get crisis-specific safety guidance and recommended actions
        </p>
      </div>

      {/* Crisis Type Selector */}
      <div className="mb-8 max-w-2xl">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Crisis Type
        </label>
        <CrisisTypeSelector
          value={selectedCrisisType}
          onChange={(value) => setSelectedCrisisType(value)}
        />
      </div>

      {/* Emergency Contacts Quick Access */}
      <div className="mb-8">
        <Alert
          message="Emergency Contacts"
          description={
            <div className="mt-2">
              <Space wrap>
                <Button
                  type="primary"
                  danger
                  icon={<PhoneOutlined />}
                  onClick={() => handleEmergencyCall('911')}
                  size="large"
                >
                  Call 911
                </Button>
                <Button
                  type="default"
                  icon={<PhoneOutlined />}
                  onClick={() => handleEmergencyCall('311')}
                  size="large"
                >
                  Non-Emergency (311)
                </Button>
              </Space>
            </div>
          }
          type="info"
          showIcon
        />
      </div>

      {/* Content Area */}
      {!selectedCrisisType && (
        <EmptyState
          title="Select a Crisis Type"
          description="Choose a crisis type above to view safety advisory and recommended actions"
        />
      )}

      {selectedCrisisType && isLoading && (
        <div className="flex justify-center items-center py-20">
          <LoadingSpinner size="large" message="Loading safety advisory..." />
        </div>
      )}

      {selectedCrisisType && error && (
        <ErrorAlert
          title="Failed to Load Advisory"
          message="Unable to fetch safety advisory. Please try again."
          onRetry={() => refetch()}
        />
      )}

      {selectedCrisisType && advisory && (
        <div className="space-y-8">
          {/* Refresh Button */}
          <div className="flex justify-end">
            <Button
              icon={<ReloadOutlined />}
              onClick={() => refetch()}
              loading={isLoading}
            >
              Refresh Advisory
            </Button>
          </div>

          {/* Advisory Card */}
          <AdvisoryCard advisory={advisory} />

          {/* Safety Actions Checklist */}
          {advisory.immediate_actions.length > 0 && (
            <SafetyActions
              actions={advisory.immediate_actions}
              crisisType={advisory.crisis_type}
            />
          )}

          {/* Advisory Map */}
          {advisory.incident_id && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4">Incident Location</h2>
              <p className="text-gray-600 mb-4">
                The map below shows the incident location and affected area. Stay informed about the risk radius.
              </p>
              <AdvisoryMap
                latitude={37.7749} // Default coordinates - in real app, fetch from incident
                longitude={-122.4194}
                crisisType={advisory.crisis_type}
                severity={advisory.severity}
                radiusMeters={advisory.distance_meters || 1000}
                locationText="Incident Location"
                className="h-[500px] w-full rounded-lg"
              />
            </div>
          )}

          {/* Additional Information */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">
              Important Information
            </h3>
            <ul className="list-disc space-y-2 pl-5 text-blue-800">
              <li>Follow all instructions from local authorities</li>
              <li>Keep emergency contacts readily available</li>
              <li>Stay informed through official channels</li>
              <li>Prepare an emergency kit if you have not already</li>
              <li>Share this information with family and neighbors</li>
            </ul>
          </div>

          {/* Disclaimer */}
          <div className="text-sm text-gray-500 text-center border-t pt-4">
            <p>
              This advisory is generated based on the crisis type and current conditions.
              Always follow instructions from local emergency services and authorities.
            </p>
            {advisory.ai_enhanced && (
              <p className="mt-2">
                This advisory has been enhanced with AI-powered recommendations
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Made with Bob
