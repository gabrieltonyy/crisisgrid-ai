/**
 * Report Form Hook
 * Manages form state and validation for crisis report submission
 */

import { useState, useCallback } from 'react';
import type { CrisisType } from '@/types/api';

export interface ReportFormData {
  crisis_type: CrisisType | '';
  description: string;
  latitude: number | null;
  longitude: number | null;
  location_text: string;
  is_anonymous: boolean;
  contact_name: string;
  contact_phone: string;
  contact_email: string;
}

export interface ReportFormErrors {
  crisis_type?: string;
  description?: string;
  location?: string;
  contact_name?: string;
  contact_phone?: string;
  contact_email?: string;
}

const INITIAL_FORM_DATA: ReportFormData = {
  crisis_type: '',
  description: '',
  latitude: null,
  longitude: null,
  location_text: '',
  is_anonymous: false,
  contact_name: '',
  contact_phone: '',
  contact_email: '',
};

export function useReportForm() {
  const [formData, setFormData] = useState<ReportFormData>(INITIAL_FORM_DATA);
  const [errors, setErrors] = useState<ReportFormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const updateField = useCallback(<K extends keyof ReportFormData>(
    field: K,
    value: ReportFormData[K]
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error for this field when user starts typing
    if (errors[field as keyof ReportFormErrors]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field as keyof ReportFormErrors];
        return newErrors;
      });
    }
  }, [errors]);

  const setLocation = useCallback((latitude: number, longitude: number, locationText?: string) => {
    setFormData(prev => ({
      ...prev,
      latitude,
      longitude,
      location_text: locationText || prev.location_text,
    }));
    
    // Clear location error
    if (errors.location) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors.location;
        return newErrors;
      });
    }
  }, [errors.location]);

  const markTouched = useCallback((field: string) => {
    setTouched(prev => ({ ...prev, [field]: true }));
  }, []);

  const validateField = useCallback((field: keyof ReportFormData): string | undefined => {
    const value = formData[field];

    switch (field) {
      case 'crisis_type':
        if (!value) return 'Please select a crisis type';
        break;

      case 'description':
        if (!value || (value as string).trim().length === 0) {
          return 'Description is required';
        }
        if ((value as string).trim().length < 20) {
          return 'Description must be at least 20 characters';
        }
        if ((value as string).length > 1000) {
          return 'Description must not exceed 1000 characters';
        }
        break;

      case 'latitude':
      case 'longitude':
        if (formData.latitude === null || formData.longitude === null) {
          return 'Location is required';
        }
        break;

      case 'contact_name':
        if (!formData.is_anonymous && (!value || (value as string).trim().length === 0)) {
          return 'Name is required for non-anonymous reports';
        }
        break;

      case 'contact_phone':
        if (!formData.is_anonymous && value) {
          const phoneRegex = /^[\d\s\-\+\(\)]+$/;
          if (!(value as string).match(phoneRegex)) {
            return 'Please enter a valid phone number';
          }
        }
        break;

      case 'contact_email':
        if (!formData.is_anonymous && value) {
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!(value as string).match(emailRegex)) {
            return 'Please enter a valid email address';
          }
        }
        break;
    }

    return undefined;
  }, [formData]);

  const validateForm = useCallback((): boolean => {
    const newErrors: ReportFormErrors = {};

    // Validate crisis type
    const crisisTypeError = validateField('crisis_type');
    if (crisisTypeError) newErrors.crisis_type = crisisTypeError;

    // Validate description
    const descriptionError = validateField('description');
    if (descriptionError) newErrors.description = descriptionError;

    // Validate location
    if (formData.latitude === null || formData.longitude === null) {
      newErrors.location = 'Location is required';
    }

    // Validate contact info if not anonymous
    if (!formData.is_anonymous) {
      const nameError = validateField('contact_name');
      if (nameError) newErrors.contact_name = nameError;

      if (formData.contact_phone) {
        const phoneError = validateField('contact_phone');
        if (phoneError) newErrors.contact_phone = phoneError;
      }

      if (formData.contact_email) {
        const emailError = validateField('contact_email');
        if (emailError) newErrors.contact_email = emailError;
      }

      // At least one contact method required
      if (!formData.contact_phone && !formData.contact_email) {
        newErrors.contact_phone = 'Please provide at least one contact method';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData, validateField]);

  const reset = useCallback(() => {
    setFormData(INITIAL_FORM_DATA);
    setErrors({});
    setTouched({});
  }, []);

  const getCharacterCount = useCallback(() => {
    return formData.description.length;
  }, [formData.description]);

  const getRemainingCharacters = useCallback(() => {
    return 1000 - formData.description.length;
  }, [formData.description]);

  const isFieldValid = useCallback((field: keyof ReportFormData): boolean => {
    return !validateField(field);
  }, [validateField]);

  const shouldShowError = useCallback((field: keyof ReportFormErrors): boolean => {
    return touched[field] && !!errors[field];
  }, [touched, errors]);

  return {
    formData,
    errors,
    touched,
    updateField,
    setLocation,
    markTouched,
    validateField,
    validateForm,
    reset,
    getCharacterCount,
    getRemainingCharacters,
    isFieldValid,
    shouldShowError,
    isValid: Object.keys(errors).length === 0,
    isDirty: JSON.stringify(formData) !== JSON.stringify(INITIAL_FORM_DATA),
  };
}

// Made with Bob