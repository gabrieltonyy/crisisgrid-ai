/**
 * Media Upload Hook
 * Handles file upload with validation and preview
 */

import { useState, useCallback } from 'react';

export interface UploadedFile {
  file: File;
  preview: string;
  type: 'image' | 'video';
  size: number;
  name: string;
}

export interface UseMediaUploadOptions {
  maxFileSize?: number; // in bytes
  allowedImageTypes?: string[];
  allowedVideoTypes?: string[];
  maxImages?: number;
  maxVideos?: number;
}

export interface MediaUploadState {
  images: UploadedFile[];
  videos: UploadedFile[];
  errors: string[];
  uploading: boolean;
}

const DEFAULT_OPTIONS: Required<UseMediaUploadOptions> = {
  maxFileSize: 10 * 1024 * 1024, // 10MB
  allowedImageTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'],
  allowedVideoTypes: ['video/mp4', 'video/quicktime', 'video/x-msvideo'],
  maxImages: 5,
  maxVideos: 2,
};

export function useMediaUpload(options: UseMediaUploadOptions = {}) {
  const maxFileSize = options.maxFileSize ?? DEFAULT_OPTIONS.maxFileSize;
  const allowedImageTypes = options.allowedImageTypes ?? DEFAULT_OPTIONS.allowedImageTypes;
  const allowedVideoTypes = options.allowedVideoTypes ?? DEFAULT_OPTIONS.allowedVideoTypes;
  const maxImages = options.maxImages ?? DEFAULT_OPTIONS.maxImages;
  const maxVideos = options.maxVideos ?? DEFAULT_OPTIONS.maxVideos;

  const [state, setState] = useState<MediaUploadState>({
    images: [],
    videos: [],
    errors: [],
    uploading: false,
  });

  const validateFile = useCallback((file: File): string | null => {
    // Check file size
    if (file.size > maxFileSize) {
      return `File "${file.name}" is too large. Maximum size is ${maxFileSize / (1024 * 1024)}MB`;
    }

    // Check file type
    const isImage = allowedImageTypes.includes(file.type);
    const isVideo = allowedVideoTypes.includes(file.type);

    if (!isImage && !isVideo) {
      return `File "${file.name}" has an unsupported format. Allowed formats: ${[...allowedImageTypes, ...allowedVideoTypes].join(', ')}`;
    }

    // Check limits
    if (isImage && state.images.length >= maxImages) {
      return `Maximum ${maxImages} images allowed`;
    }

    if (isVideo && state.videos.length >= maxVideos) {
      return `Maximum ${maxVideos} videos allowed`;
    }

    return null;
  }, [allowedImageTypes, allowedVideoTypes, maxFileSize, maxImages, maxVideos, state.images.length, state.videos.length]);

  const createPreview = useCallback((file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        if (e.target?.result) {
          resolve(e.target.result as string);
        } else {
          reject(new Error('Failed to read file'));
        }
      };
      
      reader.onerror = () => {
        reject(new Error('Failed to read file'));
      };
      
      reader.readAsDataURL(file);
    });
  }, []);

  const addFiles = useCallback(async (files: FileList | File[]) => {
    setState(prev => ({ ...prev, uploading: true, errors: [] }));

    const fileArray = Array.from(files);
    const newErrors: string[] = [];
    const newImages: UploadedFile[] = [];
    const newVideos: UploadedFile[] = [];

    for (const file of fileArray) {
      const error = validateFile(file);
      
      if (error) {
        newErrors.push(error);
        continue;
      }

      try {
        const preview = await createPreview(file);
        const isImage = allowedImageTypes.includes(file.type);
        
        const uploadedFile: UploadedFile = {
          file,
          preview,
          type: isImage ? 'image' : 'video',
          size: file.size,
          name: file.name,
        };

        if (isImage) {
          newImages.push(uploadedFile);
        } else {
          newVideos.push(uploadedFile);
        }
      } catch (error) {
        newErrors.push(`Failed to process file "${file.name}"`);
      }
    }

    setState(prev => ({
      images: [...prev.images, ...newImages],
      videos: [...prev.videos, ...newVideos],
      errors: newErrors,
      uploading: false,
    }));
  }, [validateFile, createPreview, allowedImageTypes]);

  const removeImage = useCallback((index: number) => {
    setState(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index),
    }));
  }, []);

  const removeVideo = useCallback((index: number) => {
    setState(prev => ({
      ...prev,
      videos: prev.videos.filter((_, i) => i !== index),
    }));
  }, []);

  const clearAll = useCallback(() => {
    // Revoke object URLs to prevent memory leaks
    state.images.forEach(img => URL.revokeObjectURL(img.preview));
    state.videos.forEach(vid => URL.revokeObjectURL(vid.preview));

    setState({
      images: [],
      videos: [],
      errors: [],
      uploading: false,
    });
  }, [state.images, state.videos]);

  const clearErrors = useCallback(() => {
    setState(prev => ({ ...prev, errors: [] }));
  }, []);

  // Get total file size
  const getTotalSize = useCallback(() => {
    const imageSize = state.images.reduce((sum, img) => sum + img.size, 0);
    const videoSize = state.videos.reduce((sum, vid) => sum + vid.size, 0);
    return imageSize + videoSize;
  }, [state.images, state.videos]);

  // Format file size for display
  const formatFileSize = useCallback((bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }, []);

  return {
    images: state.images,
    videos: state.videos,
    errors: state.errors,
    uploading: state.uploading,
    addFiles,
    removeImage,
    removeVideo,
    clearAll,
    clearErrors,
    getTotalSize,
    formatFileSize,
    hasFiles: state.images.length > 0 || state.videos.length > 0,
    canAddImage: state.images.length < maxImages,
    canAddVideo: state.videos.length < maxVideos,
  };
}

// Made with Bob
