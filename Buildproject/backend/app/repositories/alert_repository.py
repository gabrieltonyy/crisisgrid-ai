"""
Alert repository for database operations.
Handles CRUD operations for alerts.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

from app.models.alert import Alert
from app.schemas.common import AlertStatus

logger = logging.getLogger(__name__)


class AlertRepository:
    """Repository for alert database operations."""
    
    @staticmethod
    def create_alert(db: Session, alert_data: dict) -> Alert:
        """
        Create a new alert in the database.
        
        Args:
            db: Database session
            alert_data: Dictionary containing alert data
            
        Returns:
            Created Alert object
        """
        alert = Alert(**alert_data)
        db.add(alert)
        db.commit()
        db.refresh(alert)
        logger.info(f"Created alert {alert.alert_id} for incident {alert.incident_id}")
        return alert
    
    @staticmethod
    def get_alert_by_id(db: Session, alert_id: str) -> Optional[Alert]:
        """
        Get alert by ID.
        
        Args:
            db: Database session
            alert_id: Alert ID
            
        Returns:
            Alert object or None if not found
        """
        return db.query(Alert).filter(Alert.alert_id == alert_id).first()
    
    @staticmethod
    def get_alerts_by_incident(db: Session, incident_id: str) -> List[Alert]:
        """
        Get all alerts for an incident.
        
        Args:
            db: Database session
            incident_id: Incident ID
            
        Returns:
            List of Alert objects
        """
        return db.query(Alert).filter(Alert.incident_id == incident_id).order_by(Alert.issued_at.desc()).all()
    
    @staticmethod
    def get_active_alerts_by_incident(db: Session, incident_id: str) -> List[Alert]:
        """
        Get active alerts for an incident.
        
        Args:
            db: Database session
            incident_id: Incident ID
            
        Returns:
            List of active Alert objects
        """
        return db.query(Alert).filter(
            and_(
                Alert.incident_id == incident_id,
                Alert.status == AlertStatus.ACTIVE
            )
        ).order_by(Alert.issued_at.desc()).all()
    
    @staticmethod
    def update_alert_status(db: Session, alert_id: str, status: AlertStatus) -> Optional[Alert]:
        """
        Update alert status.
        
        Args:
            db: Database session
            alert_id: Alert ID
            status: New status
            
        Returns:
            Updated Alert object or None if not found
        """
        alert = AlertRepository.get_alert_by_id(db, alert_id)
        if alert:
            alert.status = status
            db.commit()
            db.refresh(alert)
            logger.info(f"Updated alert {alert_id} status to {status.value}")
        return alert
    
    @staticmethod
    def check_duplicate_alert(db: Session, incident_id: str) -> bool:
        """
        Check if an active alert already exists for an incident.
        
        Args:
            db: Database session
            incident_id: Incident ID
            
        Returns:
            True if duplicate exists, False otherwise
        """
        existing = db.query(Alert).filter(
            and_(
                Alert.incident_id == incident_id,
                Alert.status == AlertStatus.ACTIVE
            )
        ).first()
        return existing is not None
    
    @staticmethod
    def get_all_active_alerts(db: Session, limit: int = 100) -> List[Alert]:
        """
        Get all active alerts.
        
        Args:
            db: Database session
            limit: Maximum number of alerts to return
            
        Returns:
            List of active Alert objects
        """
        return db.query(Alert).filter(
            Alert.status == AlertStatus.ACTIVE
        ).order_by(Alert.issued_at.desc()).limit(limit).all()


# Singleton instance
alert_repository = AlertRepository()

# Made with Bob