"""
Pydantic schemas for CrisisGrid AI API.
"""

from app.schemas.common import (
    CrisisType,
    IncidentStatus,
    SeverityLevel,
    UserRole,
    ConfirmationType,
    DispatchStatus,
    AlertStatus,
    AuthorityType,
    AgentName,
    AgentRunStatus,
    LocationSchema,
    APIResponse,
    APIError,
    PaginationParams,
    PaginatedResponse,
    get_authority_for_crisis,
    get_risk_radius_meters,
    get_severity_from_confidence,
)

from app.schemas.reports import (
    CrisisReportCreateRequest,
    ReportConfirmationRequest,
    ReportResponse,
    ReportDetailResponse,
    ReportSubmissionResponse,
    NearbyReportsRequest,
    ReportStatistics,
)

from app.schemas.incidents import (
    IncidentResponse,
    IncidentDetailResponse,
    IncidentWithReports,
    IncidentListResponse,
    IncidentFilterRequest,
    IncidentStatistics,
)

from app.schemas.alerts import (
    AlertResponse,
    AlertDetailResponse,
    NearbyAlertsRequest,
    AlertStatistics,
)

from app.schemas.agents import (
    AgentInput,
    AgentOutput,
    VerificationAgentOutput,
    GeoRiskAgentOutput,
    AlertAgentOutput,
    DispatchAgentOutput,
    AdvisoryAgentOutput,
    AgentRunResponse,
    AgentRunListResponse,
)

__all__ = [
    # Enums
    "CrisisType",
    "IncidentStatus",
    "SeverityLevel",
    "UserRole",
    "ConfirmationType",
    "DispatchStatus",
    "AlertStatus",
    "AuthorityType",
    "AgentName",
    "AgentRunStatus",
    # Common
    "LocationSchema",
    "APIResponse",
    "APIError",
    "PaginationParams",
    "PaginatedResponse",
    # Utility functions
    "get_authority_for_crisis",
    "get_risk_radius_meters",
    "get_severity_from_confidence",
    # Reports
    "CrisisReportCreateRequest",
    "ReportConfirmationRequest",
    "ReportResponse",
    "ReportDetailResponse",
    "ReportSubmissionResponse",
    "NearbyReportsRequest",
    "ReportStatistics",
    # Incidents
    "IncidentResponse",
    "IncidentDetailResponse",
    "IncidentWithReports",
    "IncidentListResponse",
    "IncidentFilterRequest",
    "IncidentStatistics",
    # Alerts
    "AlertResponse",
    "AlertDetailResponse",
    "NearbyAlertsRequest",
    "AlertStatistics",
    # Agents
    "AgentInput",
    "AgentOutput",
    "VerificationAgentOutput",
    "GeoRiskAgentOutput",
    "AlertAgentOutput",
    "DispatchAgentOutput",
    "AdvisoryAgentOutput",
    "AgentRunResponse",
    "AgentRunListResponse",
]

# Made with Bob
