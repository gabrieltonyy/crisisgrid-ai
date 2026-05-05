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

// Crisis and Status types (matching backend)
export type CrisisType = 'FIRE' | 'FLOOD' | 'WILDLIFE' | 'ACCIDENT' | 'SECURITY' | 'HEALTH' | 'LANDSLIDE' | 'HAZARDOUS_SPILL' | 'OTHER';
export type IncidentStatus = 'PENDING_VERIFICATION' | 'NEEDS_CONFIRMATION' | 'PROVISIONAL_CRITICAL' | 'VERIFIED' | 'DISPATCHED' | 'RESOLVED' | 'FALSE_REPORT';
export type SeverityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type AlertStatus = 'ACTIVE' | 'EXPIRED' | 'CANCELLED';
export type DispatchStatus = 'PENDING' | 'SIMULATED_SENT' | 'SENT' | 'ACKNOWLEDGED' | 'ARRIVED' | 'COMPLETED' | 'CANCELLED' | 'FAILED';
export type AuthorityType = 'FIRE_SERVICE' | 'FIRE_DEPARTMENT' | 'DISASTER_MANAGEMENT' | 'WILDLIFE_AUTHORITY' | 'POLICE' | 'AMBULANCE' | 'PUBLIC_HEALTH';
export type AgentName = 'verification_agent' | 'clustering_agent' | 'alert_agent' | 'dispatch_agent' | 'advisory_agent';
export type AgentRunStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';

// Alert types (legacy - keeping for compatibility)
export type AlertSeverity = 'critical' | 'high' | 'medium' | 'low';
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
  credibility_score: number;
  crisis_category: CrisisType;
  severity_score: number;
  urgency_level: string;
  recommended_action: string;
  reasoning: string;
}

export interface AgentRunSummary {
  run_id: string;
  agent_name: AgentName;
  status: AgentRunStatus;
  confidence_score?: number;
  decision?: string;
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  error_message?: string;
}

export interface VerificationHistoryItem {
  agent_run: AgentRunSummary;
  verification_result?: VerificationResult;
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
  total_pages?: number;
}

// ============================================================================
// API REQUEST TYPES
// ============================================================================

export interface CreateReportRequest {
  crisis_type: CrisisType;
  description: string;
  latitude: number;
  longitude: number;
  location_text?: string;
  image_url?: string;
  video_url?: string;
  is_anonymous?: boolean;
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

export interface AdvisoryQueryParams {
  user_latitude?: number;
  user_longitude?: number;
  user_context?: string;
}

export interface AdvisoryRequest {
  incident_id: string;
  user_latitude?: number;
  user_longitude?: number;
  user_context?: string;
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface ReportResponse {
  id: string;
  incident_id?: string;
  user_id?: string;
  crisis_type: CrisisType;
  description: string;
  image_url?: string;
  video_url?: string;
  latitude: number;
  longitude: number;
  location_text?: string;
  status: IncidentStatus;
  confidence_score: number;
  severity_score: number;
  source: string;
  is_anonymous: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ReportSubmissionResponse {
  report: ReportResponse;
  processing_status: string;
  estimated_verification_time: number;
}

export interface VerificationResponse {
  report_id: string;
  status: IncidentStatus;
  verification_result: VerificationResult;
  final_confidence_score: number;
  final_severity_score: number;
  verified: boolean;
  agent_run_id: string;
  verified_at: string;
}

export interface VerificationHistoryResponse {
  report_id: string;
  current_status: IncidentStatus;
  verification_count: number;
  history: VerificationHistoryItem[];
}

export interface PendingVerificationItem {
  id: string;
  crisis_type: CrisisType;
  description: string;
  latitude: number;
  longitude: number;
  location_text?: string;
  status: IncidentStatus;
  created_at: string;
  has_media: boolean;
}

export interface VerificationStats {
  total_verified: number;
  total_rejected: number;
  total_pending: number;
  average_confidence: number;
  average_verification_time: number;
  verification_rate: number;
}

export interface AlertResponse {
  id: string;
  incident_id: string;
  crisis_type: CrisisType;
  alert_title: string;
  alert_message: string;
  severity: SeverityLevel;
  target_radius_meters: number;
  latitude: number;
  longitude: number;
  location_text?: string;
  status: AlertStatus;
  created_at: string;
  expires_at?: string;
}

export interface DispatchResponse {
  id: string;
  incident_id: string;
  authority_type: AuthorityType;
  crisis_type: CrisisType;
  message?: string;
  priority: string;
  status: DispatchStatus;
  latitude: number;
  longitude: number;
  location_text?: string;
  contact_method: string;
  response_time_seconds?: number;
  created_at: string;
  acknowledged_at?: string;
}

export interface SafetyAction {
  priority: number;
  action: string;
  rationale: string;
}

export interface AdvisoryResponse {
  incident_id: string;
  crisis_type: CrisisType;
  severity: SeverityLevel;
  distance_meters?: number;
  risk_level: string;
  primary_advice: string;
  immediate_actions: SafetyAction[];
  what_to_do: string[];
  what_not_to_do: string[];
  evacuation_advice?: string;
  emergency_contacts: Array<{ service: string; number: string }>;
  additional_resources: string[];
  generated_at: string;
  playbook_used: string;
  ai_enhanced: boolean;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version?: string;
  services?: Record<string, string>;
  orchestrate?: {
    enabled: boolean;
    mode: string;
    status: string;
    pipeline_id?: string;
    pipeline_valid?: boolean;
    registered_agent_count?: number;
    remote_configured?: boolean;
    remote_reachable?: boolean | null;
    last_probe_status?: string;
    current_execution_mode?: string;
    fallback_to_local?: boolean;
  };
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
