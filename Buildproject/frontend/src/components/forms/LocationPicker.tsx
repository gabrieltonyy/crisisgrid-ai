/**
 * Location Picker Component
 * Interactive map for selecting crisis location
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import { Button, Input, Space, Alert } from 'antd';
import { EnvironmentOutlined, AimOutlined } from '@ant-design/icons';
import { useMapEvents, Marker } from 'react-leaflet';
import L from 'leaflet';
import { BaseMap } from '@/components/maps/BaseMap';
import { useGeolocation } from '@/hooks/useGeolocation';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

interface LocationPickerProps {
  latitude: number | null;
  longitude: number | null;
  onLocationChange: (latitude: number, longitude: number, locationText?: string) => void;
  error?: string;
  disabled?: boolean;
  className?: string;
}

// Default center (Nairobi, Kenya)
const DEFAULT_CENTER: [number, number] = [-1.2921, 36.8219];

function MapClickHandler({ 
  onLocationSelect 
}: { 
  onLocationSelect: (lat: number, lng: number) => void 
}) {
  useMapEvents({
    click: (e) => {
      onLocationSelect(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export function LocationPicker({
  latitude,
  longitude,
  onLocationChange,
  error,
  disabled = false,
  className = '',
}: LocationPickerProps) {
  const [mapCenter, setMapCenter] = useState<[number, number]>(DEFAULT_CENTER);
  const [locationText, setLocationText] = useState('');
  
  const {
    latitude: geoLat,
    longitude: geoLng,
    loading: geoLoading,
    error: geoError,
    getCurrentPosition,
  } = useGeolocation({ enableHighAccuracy: true, timeout: 10000 });

  // Update map center when location is selected
  useEffect(() => {
    if (latitude !== null && longitude !== null) {
      setMapCenter([latitude, longitude]);
    }
  }, [latitude, longitude]);

  // Auto-detect location when geolocation succeeds
  useEffect(() => {
    if (geoLat !== null && geoLng !== null && latitude === null) {
      onLocationChange(geoLat, geoLng, 'Current location');
      setLocationText('Current location');
    }
  }, [geoLat, geoLng, latitude, onLocationChange]);

  const handleMapClick = useCallback((lat: number, lng: number) => {
    if (!disabled) {
      onLocationChange(lat, lng, locationText || `${lat.toFixed(6)}, ${lng.toFixed(6)}`);
    }
  }, [disabled, locationText, onLocationChange]);

  const handleAutoDetect = useCallback(() => {
    getCurrentPosition();
  }, [getCurrentPosition]);

  const handleLocationTextChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const text = e.target.value;
    setLocationText(text);
    if (latitude !== null && longitude !== null) {
      onLocationChange(latitude, longitude, text);
    }
  }, [latitude, longitude, onLocationChange]);

  // Custom marker icon for selected location
  const selectedIcon = L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        background-color: #1890ff;
        width: 30px;
        height: 30px;
        border-radius: 50% 50% 50% 0;
        transform: rotate(-45deg);
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      ">
        <div style="
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          transform: rotate(45deg);
          color: white;
          font-weight: bold;
          font-size: 16px;
        ">📍</div>
      </div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -30],
  });

  return (
    <div className={className}>
      <Space direction="vertical" size="middle" className="w-full">
        {/* Auto-detect button */}
        <Button
          type="primary"
          icon={<AimOutlined />}
          onClick={handleAutoDetect}
          loading={geoLoading}
          disabled={disabled}
          block
        >
          {geoLoading ? 'Detecting location...' : 'Use My Current Location'}
        </Button>

        {/* Geolocation error */}
        {geoError && (
          <Alert
            type="warning"
            message="Location Detection Failed"
            description={geoError}
            showIcon
            closable
          />
        )}

        {/* Location text input */}
        <Input
          prefix={<EnvironmentOutlined />}
          placeholder="Location description (optional)"
          value={locationText}
          onChange={handleLocationTextChange}
          disabled={disabled}
          size="large"
        />

        {/* Map */}
        <div className="relative">
          {geoLoading && (
            <div className="absolute inset-0 z-10 flex items-center justify-center bg-white bg-opacity-75 rounded-lg">
              <LoadingSpinner message="Detecting your location..." size="small" />
            </div>
          )}
          
          <BaseMap
            center={mapCenter}
            zoom={13}
            className="h-80 w-full rounded-lg border-2 border-gray-200"
          >
            <MapClickHandler onLocationSelect={handleMapClick} />
            {latitude !== null && longitude !== null && (
              <Marker position={[latitude, longitude]} icon={selectedIcon} />
            )}
          </BaseMap>
          
          <div className="mt-2 text-sm text-gray-500 text-center">
            Click on the map to select the crisis location
          </div>
        </div>

        {/* Selected coordinates display */}
        {latitude !== null && longitude !== null && (
          <Alert
            type="success"
            message="Location Selected"
            description={
              <div className="text-sm">
                <div>Latitude: {latitude.toFixed(6)}</div>
                <div>Longitude: {longitude.toFixed(6)}</div>
                {locationText && <div className="mt-1 font-medium">{locationText}</div>}
              </div>
            }
            showIcon
          />
        )}

        {/* Validation error */}
        {error && (
          <Alert type="error" message={error} showIcon />
        )}
      </Space>
    </div>
  );
}

// Made with Bob