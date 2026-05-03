/**
 * Media Upload Component
 * Drag-and-drop file upload with preview and validation
 */

'use client';

import { Upload, Button, Image, Alert, Progress } from 'antd';
import { 
  InboxOutlined, 
  DeleteOutlined, 
  FileImageOutlined,
  VideoCameraOutlined,
} from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';
import { useMediaUpload } from '@/hooks/useMediaUpload';
import { useCallback, useEffect } from 'react';

const { Dragger } = Upload;

interface MediaUploadProps {
  onFilesChange: (files: File[]) => void;
  error?: string;
  disabled?: boolean;
  className?: string;
}

export function MediaUpload({
  onFilesChange,
  error,
  disabled = false,
  className = '',
}: MediaUploadProps) {
  const {
    images,
    videos,
    errors: uploadErrors,
    uploading,
    addFiles,
    removeImage,
    removeVideo,
    clearErrors,
    formatFileSize,
    canAddImage,
    canAddVideo,
  } = useMediaUpload({
    maxFileSize: 10 * 1024 * 1024, // 10MB
    maxImages: 5,
    maxVideos: 2,
  });

  // Update parent component when files change
  useEffect(() => {
    const allFiles = [
      ...images.map(img => img.file),
      ...videos.map(vid => vid.file),
    ];
    onFilesChange(allFiles);
  }, [images, videos, onFilesChange]);

  const handleBeforeUpload = useCallback((file: File) => {
    // Don't actually upload, just add to state
    addFiles([file]);
    return false; // Prevent auto upload
  }, [addFiles]);

  const handleRemove = useCallback((file: UploadFile) => {
    const imageIndex = images.findIndex(img => img.file.name === file.name);
    if (imageIndex !== -1) {
      removeImage(imageIndex);
      return;
    }
    
    const videoIndex = videos.findIndex(vid => vid.file.name === file.name);
    if (videoIndex !== -1) {
      removeVideo(videoIndex);
    }
  }, [images, videos, removeImage, removeVideo]);

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: true,
    accept: 'image/*,video/*',
    beforeUpload: handleBeforeUpload,
    onRemove: handleRemove,
    disabled: disabled || (!canAddImage && !canAddVideo),
    showUploadList: false,
  };

  return (
    <div className={className}>
      <div className="space-y-4">
        {/* Upload area */}
        <Dragger {...uploadProps}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">
            Click or drag files to upload
          </p>
          <p className="ant-upload-hint">
            Support for images and videos. Max 10MB per file.
            <br />
            Up to 5 images and 2 videos allowed.
          </p>
        </Dragger>

        {/* Upload errors */}
        {uploadErrors.length > 0 && (
          <Alert
            type="error"
            message="Upload Errors"
            description={
              <ul className="list-disc list-inside">
                {uploadErrors.map((err, idx) => (
                  <li key={idx} className="text-sm">{err}</li>
                ))}
              </ul>
            }
            closable
            onClose={clearErrors}
            showIcon
          />
        )}

        {/* Validation error */}
        {error && (
          <Alert type="error" message={error} showIcon />
        )}

        {/* Image previews */}
        {images.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <FileImageOutlined className="text-blue-500" />
              <span className="font-medium">Images ({images.length}/5)</span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
              {images.map((img, index) => (
                <div key={index} className="relative group">
                  <Image
                    src={img.preview}
                    alt={img.name}
                    className="rounded-lg object-cover w-full h-32"
                    preview={{
                      mask: <div className="text-xs">Preview</div>,
                    }}
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all rounded-lg flex items-center justify-center">
                    <Button
                      type="primary"
                      danger
                      shape="circle"
                      icon={<DeleteOutlined />}
                      onClick={() => removeImage(index)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
                      disabled={disabled}
                    />
                  </div>
                  <div className="mt-1 text-xs text-gray-500 truncate">
                    {img.name}
                  </div>
                  <div className="text-xs text-gray-400">
                    {formatFileSize(img.size)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Video previews */}
        {videos.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <VideoCameraOutlined className="text-purple-500" />
              <span className="font-medium">Videos ({videos.length}/2)</span>
            </div>
            <div className="space-y-3">
              {videos.map((vid, index) => (
                <div key={index} className="border rounded-lg p-3 flex items-center gap-3">
                  <video
                    src={vid.preview}
                    className="w-32 h-20 rounded object-cover"
                    controls
                  />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">{vid.name}</div>
                    <div className="text-sm text-gray-500">
                      {formatFileSize(vid.size)}
                    </div>
                  </div>
                  <Button
                    type="primary"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => removeVideo(index)}
                    disabled={disabled}
                  >
                    Remove
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Upload status */}
        {uploading && (
          <div className="flex items-center gap-3">
            <Progress percent={100} status="active" showInfo={false} />
            <span className="text-sm text-gray-600">Processing files...</span>
          </div>
        )}

        {/* File count info */}
        {(images.length > 0 || videos.length > 0) && (
          <Alert
            type="info"
            message={
              <div className="text-sm">
                <div>Total files: {images.length + videos.length}</div>
                {!canAddImage && <div className="text-orange-600">Maximum images reached (5)</div>}
                {!canAddVideo && <div className="text-orange-600">Maximum videos reached (2)</div>}
              </div>
            }
            showIcon
          />
        )}
      </div>
    </div>
  );
}

// Made with Bob
