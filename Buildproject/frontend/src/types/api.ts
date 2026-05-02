// Common types
export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface Location extends Coordinates {
  address?: string;
  city?: string;
  region?: string;
  country?: string;
}

// Alert types
export type AlertSeverity = 'critical' | 'high' | 'medium' | 'low';
export type AlertStatus = 'pending' | 'verified' | 'dispatched' | 'resolved' | 'false_alarm';
export type AlertType = 'fire' | 'flood' | 'earthquake' | 'medical' | 'accident' | 'crime' | 'other';

export interface Alert {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  status: AlertStatus;
  location: Location;
  description: string;
  timestamp: string;
  verified: boolean;
  trust_score?: number;
  cluster_id?: string;
  media_urls?: string[];
}

// Report types
export type ReportStatus = 'pending' | 'verified' | 'rejected' | 'duplicate';

export interface Report {
  id: string;
  citizen_id?: string;
  type: AlertType;
  description: string;
  location: Location;
  media_urls?: string[];
  timestamp: string;
  status: ReportStatus;
  verification_notes?: string;
  trust_score?: number;
}

// Dispatch types
export type DispatchStatus = 'pending' | 'assigned' | 'en_route' | 'on_scene' | 'completed' | 'cancelled';
export type ResourceType = 'fire_truck' | 'ambulance' | 'police' | 'rescue' | 'utility';

export interface DispatchLog {
  id: string;
  alert_id: string;
  resource_type: ResourceType;
  resource_id: string;
  status: DispatchStatus;
  assigned_at: string;
  eta?: number;
  route?: Coordinates[];
  notes?: string;
}

// Advisory types
export type AdvisoryLevel = 'info' | 'warning' | 'alert' | 'emergency';

export interface Advisory {
  id: string;
  title: string;
  message: string;
  level: AdvisoryLevel;
  affected_areas: string[];
  valid_from: string;
  valid_until: string;
  created_at: string;
  active: boolean;
}

// Incident types
export interface Incident {
  id: string;
  alert_ids: string[];
  type: AlertType;
  severity: AlertSeverity;
  location: Location;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  affected_radius?: number;
}

// Verification types
export interface VerificationResult {
  report_id: string;
  verified: boolean;
  trust_score: number;
  confidence: number;
  reasoning: string;
  cross_references: string[];
  timestamp: string;
}

// Analytics types
export interface AlertStatistics {
  total_alerts: number;
  by_severity: Record<AlertSeverity, number>;
  by_type: Record<AlertType, number>;
  by_status: Record<AlertStatus, number>;
  average_response_time: number;
  verification_rate: number;
}

export interface DashboardMetrics {
  active_alerts: number;
  pending_verifications: number;
  dispatched_resources: number;
  resolved_today: number;
  average_trust_score: number;
  response_time_avg: number;
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// API Request types
export interface CreateReportRequest {
  type: AlertType;
  description: string;
  location: Location;
  media_files?: File[];
  citizen_id?: string;
}

export interface VerifyReportRequest {
  report_id: string;
  verified: boolean;
  notes?: string;
}

export interface CreateDispatchRequest {
  alert_id: string;
  resource_type: ResourceType;
  resource_id: string;
  notes?: string;
}

export interface CreateAdvisoryRequest {
  title: string;
  message: string;
  level: AdvisoryLevel;
  affected_areas: string[];
  valid_until: string;
}

// Filter types
export interface AlertFilters {
  severity?: AlertSeverity[];
  status?: AlertStatus[];
  type?: AlertType[];
  start_date?: string;
  end_date?: string;
  location?: Coordinates;
  radius?: number;
}

// Made with Bob
