"""
Clustering service for grouping nearby crisis reports into incidents.
Implements DBSCAN-like clustering with crisis-specific radius rules.
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID
import logging

# Type checker doesn't understand SQLAlchemy's runtime behavior
# mypy: disable-error-code="assignment,arg-type,operator"

from app.models.report import Report
from app.models.incident import Incident
from app.schemas.common import CrisisType, IncidentStatus, SeverityLevel, AgentName, AgentRunStatus
from app.services.georisk_service import get_clustering_radius
from app.utils.geo import haversine_distance, calculate_centroid
from app.utils.ids import generate_incident_id, generate_agent_run_id
from app.utils.time import utc_now
from app.services.cloudant_service import cloudant_service

logger = logging.getLogger(__name__)


class ClusteringService:
    """Service for clustering crisis reports into incidents."""
    
    def __init__(self, db: Session):
        """
        Initialize clustering service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def cluster_reports(
        self,
        crisis_type: Optional[CrisisType] = None,
        time_window_hours: int = 24,
        min_reports: int = 1
    ) -> Dict[str, Any]:
        """
        Cluster unassigned reports into incidents.
        
        Args:
            crisis_type: Optional filter for specific crisis type
            time_window_hours: Time window for clustering (default 24 hours)
            min_reports: Minimum reports to form an incident (default 1)
            
        Returns:
            Dictionary with clustering results
        """
        agent_run_id = generate_agent_run_id("clustering")
        
        logger.info(
            f"Starting clustering: crisis_type={crisis_type}, "
            f"time_window={time_window_hours}h, min_reports={min_reports}"
        )
        
        # Get unassigned reports
        unassigned_reports = self._get_unassigned_reports(
            crisis_type, time_window_hours
        )
        
        if not unassigned_reports:
            logger.info("No unassigned reports to cluster")
            return {
                "agent_run_id": agent_run_id,
                "clusters_created": 0,
                "reports_clustered": 0,
                "unassigned_reports": 0
            }
        
        logger.info(f"Found {len(unassigned_reports)} unassigned reports")
        
        # Perform clustering
        clusters = self._perform_clustering(unassigned_reports, min_reports)
        
        # Create incidents from clusters
        incidents_created = []
        reports_clustered = 0
        
        for cluster in clusters:
            if len(cluster) >= min_reports:
                incident = self._create_incident_from_cluster(cluster)
                if incident:
                    incidents_created.append(incident.id)
                    reports_clustered += len(cluster)
        
        result = {
            "agent_run_id": agent_run_id,
            "clusters_created": len(incidents_created),
            "reports_clustered": reports_clustered,
            "unassigned_reports": len(unassigned_reports) - reports_clustered,
            "incident_ids": incidents_created,
            "clustered_at": utc_now().isoformat()
        }
        
        logger.info(
            f"Clustering complete: {len(incidents_created)} incidents created, "
            f"{reports_clustered} reports clustered"
        )
        
        # Log to Cloudant
        self._log_to_cloudant(agent_run_id, result)
        
        return result
    
    def find_matching_incident(
        self,
        report: Report,
        max_distance_override: Optional[float] = None
    ) -> Optional[Incident]:
        """
        Find an existing incident that matches a report.
        
        Args:
            report: Report to match
            max_distance_override: Optional override for clustering radius
            
        Returns:
            Matching incident or None
        """
        # Get clustering radius for crisis type
        max_distance = max_distance_override or get_clustering_radius(report.crisis_type)
        
        # Query recent incidents of same type
        time_threshold = utc_now() - timedelta(hours=24)
        
        incidents = self.db.query(Incident).filter(
            Incident.crisis_type == report.crisis_type,
            Incident.status.in_([
                IncidentStatus.PENDING_VERIFICATION,
                IncidentStatus.VERIFIED,
                IncidentStatus.NEEDS_CONFIRMATION,
                IncidentStatus.PROVISIONAL_CRITICAL
            ]),
            Incident.created_at >= time_threshold
        ).all()
        
        # Find closest incident within radius
        closest_incident = None
        min_distance = float('inf')
        
        for incident in incidents:
            distance = haversine_distance(
                float(report.latitude),
                float(report.longitude),
                float(incident.latitude),  # type: ignore
                float(incident.longitude)  # type: ignore
            )
            
            if distance <= max_distance and distance < min_distance:
                min_distance = distance
                closest_incident = incident
        
        if closest_incident:
            logger.info(
                f"Found matching incident {closest_incident.id} "
                f"at {min_distance:.2f}m from report {report.id}"
            )
        
        return closest_incident
    
    def add_report_to_incident(
        self,
        report: Report,
        incident: Incident
    ) -> Incident:
        """
        Add a report to an existing incident and update incident properties.
        
        Args:
            report: Report to add
            incident: Incident to update
            
        Returns:
            Updated incident
        """
        # Link report to incident
        report.incident_id = incident.id
        
        # Update incident metadata
        incident.report_count += 1
        incident.last_updated_at = utc_now()
        
        # Recalculate incident centroid if multiple reports
        if incident.report_count > 1:
            all_reports = self.db.query(Report).filter(
                Report.incident_id == incident.id
            ).all()
            
            coordinates = [
                (float(r.latitude), float(r.longitude))
                for r in all_reports
            ]
            
            centroid_lat, centroid_lon = calculate_centroid(coordinates)
            incident.latitude = centroid_lat
            incident.longitude = centroid_lon
        
        # Update confidence scores (simple average for now)
        all_reports = self.db.query(Report).filter(
            Report.incident_id == incident.id
        ).all()
        
        if all_reports:
            avg_confidence = sum(float(r.confidence_score) for r in all_reports) / len(all_reports)
            incident.cross_report_confidence = min(100, avg_confidence + (len(all_reports) * 5))
            incident.update_confidence_score()
        
        self.db.commit()
        self.db.refresh(incident)
        
        logger.info(
            f"Added report {report.id} to incident {incident.id} "
            f"(now {incident.report_count} reports)"
        )
        
        return incident
    
    def _get_unassigned_reports(
        self,
        crisis_type: Optional[CrisisType],
        time_window_hours: int
    ) -> List[Report]:
        """
        Get reports that are not assigned to any incident.
        
        Args:
            crisis_type: Optional filter for crisis type
            time_window_hours: Time window in hours
            
        Returns:
            List of unassigned reports
        """
        time_threshold = utc_now() - timedelta(hours=time_window_hours)
        
        query = self.db.query(Report).filter(
            Report.incident_id.is_(None),
            Report.created_at >= time_threshold,
            Report.status != IncidentStatus.FALSE_REPORT
        )
        
        if crisis_type:
            query = query.filter(Report.crisis_type == crisis_type)
        
        return query.all()
    
    def _perform_clustering(
        self,
        reports: List[Report],
        min_reports: int
    ) -> List[List[Report]]:
        """
        Perform DBSCAN-like clustering on reports.
        
        Args:
            reports: List of reports to cluster
            min_reports: Minimum reports per cluster
            
        Returns:
            List of clusters (each cluster is a list of reports)
        """
        # Group reports by crisis type first
        by_crisis_type: Dict[CrisisType, List[Report]] = {}
        for report in reports:
            if report.crisis_type not in by_crisis_type:
                by_crisis_type[report.crisis_type] = []
            by_crisis_type[report.crisis_type].append(report)
        
        all_clusters = []
        
        # Cluster each crisis type separately
        for crisis_type, crisis_reports in by_crisis_type.items():
            clusters = self._cluster_by_distance(
                crisis_reports,
                get_clustering_radius(crisis_type)
            )
            all_clusters.extend(clusters)
        
        return all_clusters
    
    def _cluster_by_distance(
        self,
        reports: List[Report],
        max_distance: float
    ) -> List[List[Report]]:
        """
        Cluster reports by distance using a simple greedy algorithm.
        
        Args:
            reports: List of reports to cluster
            max_distance: Maximum distance for clustering
            
        Returns:
            List of clusters
        """
        if not reports:
            return []
        
        clusters: List[List[Report]] = []
        visited: Set[UUID] = set()
        
        for report in reports:
            if report.id in visited:
                continue
            
            # Start new cluster
            cluster = [report]
            visited.add(report.id)
            
            # Find all reports within radius
            for other_report in reports:
                if other_report.id in visited:
                    continue
                
                # Check if within radius of any report in cluster
                for cluster_report in cluster:
                    distance = haversine_distance(
                        float(cluster_report.latitude),
                        float(cluster_report.longitude),
                        float(other_report.latitude),
                        float(other_report.longitude)
                    )
                    
                    if distance <= max_distance:
                        cluster.append(other_report)
                        visited.add(other_report.id)
                        break
            
            clusters.append(cluster)
        
        return clusters
    
    def _create_incident_from_cluster(
        self,
        cluster: List[Report]
    ) -> Optional[Incident]:
        """
        Create an incident from a cluster of reports.
        
        Args:
            cluster: List of reports in the cluster
            
        Returns:
            Created incident or None if failed
        """
        if not cluster:
            return None
        
        # Use first report as reference
        primary_report = cluster[0]
        
        # Calculate centroid location
        coordinates = [
            (float(r.latitude), float(r.longitude))
            for r in cluster
        ]
        centroid_lat, centroid_lon = calculate_centroid(coordinates)
        
        # Generate incident ID
        incident_id = generate_incident_id(primary_report.crisis_type.value)
        
        # Calculate initial confidence
        avg_confidence = sum(float(r.confidence_score) for r in cluster) / len(cluster)
        cross_report_confidence = min(100, avg_confidence + (len(cluster) * 5))
        
        # Create incident
        incident = Incident(
            id=incident_id,
            crisis_type=primary_report.crisis_type,
            status=IncidentStatus.PENDING_VERIFICATION,
            severity=SeverityLevel.MEDIUM,
            latitude=centroid_lat,
            longitude=centroid_lon,
            location_description=primary_report.location_text,
            confidence_score=0.0,
            cross_report_confidence=cross_report_confidence,
            report_count=len(cluster),
            first_reported_at=min(r.created_at for r in cluster),
            description=f"Clustered incident from {len(cluster)} reports"
        )
        
        # Update confidence score
        incident.update_confidence_score()
        
        # Save incident
        self.db.add(incident)
        self.db.flush()
        
        # Link all reports to incident
        for report in cluster:
            report.incident_id = incident.id
        
        self.db.commit()
        self.db.refresh(incident)
        
        logger.info(
            f"Created incident {incident.id} from {len(cluster)} reports "
            f"at ({centroid_lat:.4f}, {centroid_lon:.4f})"
        )
        
        return incident
    
    def _log_to_cloudant(self, agent_run_id: str, result: Dict[str, Any]) -> None:
        """
        Log clustering results to Cloudant.
        
        Args:
            agent_run_id: Agent run ID
            result: Clustering result
        """
        if not cloudant_service.enabled:
            return
        
        try:
            cloudant_service.store_agent_log(
                agent_run_id=agent_run_id,
                agent_type="clustering_agent",
                payload=result
            )
        except Exception as e:
            logger.error(f"Failed to log to Cloudant: {e}")


def get_clustering_service(db: Session) -> ClusteringService:
    """
    Factory function to get clustering service instance.
    
    Args:
        db: Database session
        
    Returns:
        ClusteringService instance
    """
    return ClusteringService(db)

# Made with Bob