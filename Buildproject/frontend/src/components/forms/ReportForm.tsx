/**
 * Report Form Component
 * Complete crisis report submission form
 */

'use client';

import { useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { Form, Input, Button, Card, Result, Space, Divider } from 'antd';
import {
  CheckCircleOutlined,
  SendOutlined,
} from '@ant-design/icons';
import { useReportForm } from '@/hooks/useReportForm';
import { useCreateReport } from '@/lib/api';
import { CrisisTypeSelector } from './CrisisTypeSelector';
import { MediaUpload } from './MediaUpload';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorAlert } from '@/components/ui/ErrorAlert';
import { formatPercentScore } from '@/lib/utils';
import type { CrisisType, ReportSubmissionResponse } from '@/types/api';

const { TextArea } = Input;
const LocationPicker = dynamic(
  () => import('./LocationPicker').then((mod) => mod.LocationPicker),
  { ssr: false }
);

interface ReportFormProps {
  onSuccess?: (response: ReportSubmissionResponse) => void;
  onCancel?: () => void;
  className?: string;
}

export function ReportForm({
  onSuccess,
  onCancel,
  className = '',
}: ReportFormProps) {
  const {
    formData,
    errors,
    updateField,
    setLocation,
    markTouched,
    validateForm,
    reset,
    getCharacterCount,
    shouldShowError,
  } = useReportForm();

  const [mediaFiles, setMediaFiles] = useState<File[]>([]);
  const [submissionResponse, setSubmissionResponse] = useState<ReportSubmissionResponse | null>(null);

  const { mutate: createReport, isPending, error: apiError } = useCreateReport();

  const handleSubmit = useCallback(async () => {
    // Mark all fields as touched to show validation errors
    markTouched('crisis_type');
    markTouched('description');
    markTouched('location');

    // Validate form
    if (!validateForm()) {
      return;
    }

    // Prepare form data for submission
    const reportData = new FormData();
    reportData.append('crisis_type', formData.crisis_type as string);
    reportData.append('description', formData.description);
    reportData.append('latitude', formData.latitude!.toString());
    reportData.append('longitude', formData.longitude!.toString());
    
    if (formData.location_text) {
      reportData.append('location_text', formData.location_text);
    }

    if (formData.is_anonymous) {
      reportData.append('is_anonymous', 'true');
    }

    // Add media files
    mediaFiles.forEach((file) => {
      if (file.type.startsWith('image/')) {
        reportData.append('images', file);
      } else if (file.type.startsWith('video/')) {
        reportData.append('videos', file);
      }
    });

    // Submit report
    createReport(
      {
        crisis_type: formData.crisis_type as CrisisType,
        description: formData.description,
        latitude: formData.latitude!,
        longitude: formData.longitude!,
        location_text: formData.location_text,
        is_anonymous: formData.is_anonymous,
      },
      {
        onSuccess: (response) => {
          setSubmissionResponse(response);
          if (onSuccess) {
            onSuccess(response);
          }
        },
      }
    );
  }, [formData, mediaFiles, validateForm, markTouched, createReport, onSuccess]);

  const handleReset = useCallback(() => {
    reset();
    setMediaFiles([]);
    setSubmissionResponse(null);
  }, [reset]);

  // Show success state
  if (submissionResponse) {
    return (
      <Card className={className}>
        <Result
          status="success"
          icon={<CheckCircleOutlined className="text-green-500" />}
          title="Report Submitted Successfully!"
          subTitle={
            <div className="space-y-2">
              <p>Your crisis report has been received and is being processed.</p>
              <div className="bg-gray-50 p-4 rounded-lg text-left">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="font-semibold">Report ID:</div>
                  <div className="font-mono">{submissionResponse.report.id}</div>
                  
                  <div className="font-semibold">Status:</div>
                  <div className="capitalize">{submissionResponse.report.status.replace(/_/g, ' ')}</div>
                  
                  <div className="font-semibold">Crisis Type:</div>
                  <div className="capitalize">{submissionResponse.report.crisis_type}</div>
                  
                  <div className="font-semibold">Confidence Score:</div>
                  <div>{formatPercentScore(submissionResponse.report.confidence_score, 1)}</div>
                  
                  {submissionResponse.estimated_verification_time && (
                    <>
                      <div className="font-semibold">Est. Verification:</div>
                      <div>{submissionResponse.estimated_verification_time} seconds</div>
                    </>
                  )}
                </div>
              </div>
              <p className="text-sm text-gray-600 mt-4">
                Emergency services have been notified and will respond based on the severity assessment.
              </p>
            </div>
          }
          extra={[
            <Button type="primary" key="new" onClick={handleReset}>
              Submit Another Report
            </Button>,
            <Button key="view" onClick={() => window.location.href = `/citizen/reports/${submissionResponse.report.id}`}>
              View Report Details
            </Button>,
          ]}
        />
      </Card>
    );
  }

  return (
    <Card className={className} title="Report a Crisis">
      <Form layout="vertical" onFinish={handleSubmit}>
        {/* Crisis Type */}
        <Form.Item
          label={<span className="font-semibold">Crisis Type</span>}
          required
          validateStatus={shouldShowError('crisis_type') ? 'error' : ''}
          help={shouldShowError('crisis_type') ? errors.crisis_type : ''}
        >
          <CrisisTypeSelector
            value={formData.crisis_type}
            onChange={(value) => updateField('crisis_type', value)}
            error={shouldShowError('crisis_type') ? errors.crisis_type : undefined}
            disabled={isPending}
          />
        </Form.Item>

        {/* Description */}
        <Form.Item
          label={<span className="font-semibold">Description</span>}
          required
          validateStatus={shouldShowError('description') ? 'error' : ''}
          help={
            shouldShowError('description') 
              ? errors.description 
              : `${getCharacterCount()}/1000 characters (minimum 20)`
          }
        >
          <TextArea
            value={formData.description}
            onChange={(e) => updateField('description', e.target.value)}
            onBlur={() => markTouched('description')}
            placeholder="Describe what you're seeing. Include details like: What is happening? How severe is it? Are people in danger? Any landmarks nearby?"
            rows={6}
            maxLength={1000}
            showCount
            disabled={isPending}
            status={shouldShowError('description') ? 'error' : ''}
          />
        </Form.Item>

        {/* Location */}
        <Form.Item
          label={<span className="font-semibold">Location</span>}
          required
          validateStatus={shouldShowError('location') ? 'error' : ''}
          help={shouldShowError('location') ? errors.location : 'Click on the map or use auto-detect to set the crisis location'}
        >
          <LocationPicker
            latitude={formData.latitude}
            longitude={formData.longitude}
            onLocationChange={setLocation}
            error={shouldShowError('location') ? errors.location : undefined}
            disabled={isPending}
          />
        </Form.Item>

        <Divider />

        {/* Media Upload */}
        <Form.Item
          label={<span className="font-semibold">Photos & Videos (Optional)</span>}
          help="Adding photos or videos helps verify your report faster"
        >
          <MediaUpload
            onFilesChange={setMediaFiles}
            disabled={isPending}
          />
        </Form.Item>

        <Divider />

        {/* API Error */}
        {apiError && (
          <ErrorAlert
            message={apiError.message}
            onRetry={handleSubmit}
            className="mb-4"
          />
        )}

        {/* Submit Button */}
        <Form.Item>
          <Space className="w-full justify-end">
            {onCancel && (
              <Button onClick={onCancel} disabled={isPending}>
                Cancel
              </Button>
            )}
            <Button
              type="primary"
              htmlType="submit"
              icon={isPending ? <LoadingSpinner size="small" /> : <SendOutlined />}
              loading={isPending}
              size="large"
              disabled={isPending}
            >
              {isPending ? 'Submitting Report...' : 'Submit Report'}
            </Button>
          </Space>
        </Form.Item>

        {/* Loading overlay */}
        {isPending && (
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg">
            <LoadingSpinner 
              message="Submitting your report and notifying emergency services..." 
              size="large"
            />
          </div>
        )}
      </Form>
    </Card>
  );
}

// Made with Bob
