"""
Dispatch repository for database operations.
Handles CRUD operations for dispatch logs.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

from app.models.dispatch_log import DispatchLog
from app.schemas.common import DispatchStatus

logger = logging.getLogger(__name__)


class DispatchRepository:
    """Repository for dispatch log database operations."""
    
    @staticmethod
    def create_dispatch(db: Session, dispatch_data: dict) -> DispatchLog:
        """
        Create a new dispatch log in the database.
        
        Args:
            db: Database session
            dispatch_data: Dictionary containing dispatch data
            
        Returns:
            Created DispatchLog object
        """
        dispatch = DispatchLog(**dispatch_data)
        db.add(dispatch)
        db.commit()
        db.refresh(dispatch)
        logger.info(f"Created dispatch {dispatch.dispatch_id} for incident {dispatch.incident_id}")
        return dispatch
    
    @staticmethod
    def get_dispatch_by_id(db: Session, dispatch_id: str) -> Optional[DispatchLog]:
        """
        Get dispatch log by ID.
        
        Args:
            db: Database session
            dispatch_id: Dispatch ID
            
        Returns:
            DispatchLog object or None if not found
        """
        return db.query(DispatchLog).filter(DispatchLog.dispatch_id == dispatch_id).first()
    
    @staticmethod
    def get_dispatches_by_incident(db: Session, incident_id: str) -> List[DispatchLog]:
        """
        Get all dispatch logs for an incident.
        
        Args:
            db: Database session
            incident_id: Incident ID
            
        Returns:
            List of DispatchLog objects
        """
        return db.query(DispatchLog).filter(
            DispatchLog.incident_id == incident_id
        ).order_by(DispatchLog.dispatched_at.desc()).all()
    
    @staticmethod
    def get_pending_dispatches(db: Session, limit: int = 100) -> List[DispatchLog]:
        """
        Get pending dispatch logs.
        
        Args:
            db: Database session
            limit: Maximum number of dispatches to return
            
        Returns:
            List of pending DispatchLog objects
        """
        return db.query(DispatchLog).filter(
            DispatchLog.status == DispatchStatus.PENDING
        ).order_by(DispatchLog.dispatched_at.desc()).limit(limit).all()
    
    @staticmethod
    def update_dispatch_status(
        db: Session, 
        dispatch_id: str, 
        status: DispatchStatus,
        notes: Optional[str] = None
    ) -> Optional[DispatchLog]:
        """
        Update dispatch status.
        
        Args:
            db: Database session
            dispatch_id: Dispatch ID
            status: New status
            notes: Optional notes to add
            
        Returns:
            Updated DispatchLog object or None if not found
        """
        dispatch = DispatchRepository.get_dispatch_by_id(db, dispatch_id)
        if dispatch:
            dispatch.status = status
            if notes:
                dispatch.response_notes = notes
            db.commit()
            db.refresh(dispatch)
            logger.info(f"Updated dispatch {dispatch_id} status to {status.value}")
        return dispatch
    
    @staticmethod
    def check_duplicate_dispatch(
        db: Session, 
        incident_id: str, 
        authority_type: str
    ) -> bool:
        """
        Check if a dispatch already exists for an incident and authority type.
        
        Args:
            db: Database session
            incident_id: Incident ID
            authority_type: Authority type
            
        Returns:
            True if duplicate exists, False otherwise
        """
        existing = db.query(DispatchLog).filter(
            and_(
                DispatchLog.incident_id == incident_id,
                DispatchLog.authority_type == authority_type,
                DispatchLog.status.in_([
                    DispatchStatus.PENDING,
                    DispatchStatus.SIMULATED_SENT,
                    DispatchStatus.SENT,
                    DispatchStatus.ACKNOWLEDGED,
                    DispatchStatus.ARRIVED
                ])
            )
        ).first()
        return existing is not None
    
    @staticmethod
    def get_all_dispatches(db: Session, limit: int = 100) -> List[DispatchLog]:
        """
        Get all dispatch logs.
        
        Args:
            db: Database session
            limit: Maximum number of dispatches to return
            
        Returns:
            List of DispatchLog objects
        """
        return db.query(DispatchLog).order_by(
            DispatchLog.dispatched_at.desc()
        ).limit(limit).all()


# Singleton instance
dispatch_repository = DispatchRepository()

# Made with Bob