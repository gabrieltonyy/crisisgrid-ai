"""IBM Cloudant NoSQL database service for storing raw payloads and audit logs."""

from typing import Optional, Dict, Any
import logging
from datetime import datetime
from ibmcloudant.cloudant_v1 import CloudantV1, Document
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException

from app.core.config import settings
from app.utils.time import utc_now, format_iso8601

logger = logging.getLogger(__name__)


class CloudantService:
    """Service for IBM Cloudant NoSQL database operations."""
    
    def __init__(self):
        """Initialize Cloudant client if enabled."""
        self.enabled = settings.CLOUDANT_ENABLED
        self.client: Optional[CloudantV1] = None
        
        if self.enabled:
            try:
                # Create authenticator
                authenticator = IAMAuthenticator(settings.CLOUDANT_API_KEY)
                
                # Create Cloudant client
                self.client = CloudantV1(authenticator=authenticator)
                self.client.set_service_url(settings.CLOUDANT_URL)
                
                # Database names
                self.db_reports = settings.CLOUDANT_DB_REPORTS
                self.db_agent_logs = settings.CLOUDANT_DB_AGENT_LOGS
                self.db_audit_events = settings.CLOUDANT_DB_AUDIT_EVENTS
                
                logger.info("Cloudant service initialized successfully")
                
                # Ensure databases exist
                self._ensure_databases()
                
            except Exception as e:
                logger.error(f"Failed to initialize Cloudant service: {e}")
                self.enabled = False
                self.client = None
    
    def _ensure_databases(self) -> None:
        """Ensure required databases exist, create if they don't."""
        if not self.client:
            return
        
        databases = [
            self.db_reports,
            self.db_agent_logs,
            self.db_audit_events
        ]
        
        for db_name in databases:
            try:
                # Try to get database info
                self.client.get_database_information(db=db_name)
                logger.info(f"Database '{db_name}' exists")
            except ApiException as e:
                if e.code == 404:
                    # Database doesn't exist, create it
                    try:
                        self.client.put_database(db=db_name)
                        logger.info(f"Created database '{db_name}'")
                    except Exception as create_error:
                        logger.error(f"Failed to create database '{db_name}': {create_error}")
                else:
                    logger.error(f"Error checking database '{db_name}': {e}")
    
    def store_raw_report(
        self,
        report_id: str,
        report_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Store raw report payload in Cloudant.
        
        Args:
            report_id: UUID of the report
            report_data: Raw report data dictionary
            metadata: Optional metadata (user_agent, ip_address, etc.)
            
        Returns:
            Document ID if successful, None otherwise
        """
        if not self.enabled or not self.client:
            logger.warning("Cloudant not enabled, skipping raw report storage")
            return None
        
        try:
            # Prepare document
            doc = {
                "_id": f"report_{report_id}",
                "type": "crisis_report",
                "report_id": report_id,
                "data": report_data,
                "metadata": metadata or {},
                "stored_at": format_iso8601(utc_now())
            }
            
            # Store document
            response = self.client.post_document(
                db=self.db_reports,
                document=Document(**doc)
            ).get_result()
            
            logger.info(f"Stored raw report in Cloudant: {response.get('id')}")
            return response.get("id")
            
        except Exception as e:
            logger.error(f"Failed to store raw report in Cloudant: {e}")
            return None
    
    def store_agent_log(
        self,
        agent_run_id: str,
        agent_type: str,
        payload: Dict[str, Any]
    ) -> Optional[str]:
        """
        Store agent execution log in Cloudant.
        
        Args:
            agent_run_id: ID of the agent run
            agent_type: Type of agent (verification, dispatch, etc.)
            payload: Agent execution payload
            
        Returns:
            Document ID if successful, None otherwise
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            doc = {
                "_id": f"agent_{agent_run_id}",
                "type": "agent_log",
                "agent_run_id": agent_run_id,
                "agent_type": agent_type,
                "payload": payload,
                "logged_at": format_iso8601(utc_now())
            }
            
            response = self.client.post_document(
                db=self.db_agent_logs,
                document=Document(**doc)
            ).get_result()
            
            logger.info(f"Stored agent log in Cloudant: {response.get('id')}")
            return response.get("id")
            
        except Exception as e:
            logger.error(f"Failed to store agent log in Cloudant: {e}")
            return None
    
    def store_audit_event(
        self,
        event_type: str,
        entity_id: str,
        entity_type: str,
        action: str,
        details: Dict[str, Any]
    ) -> Optional[str]:
        """
        Store audit event in Cloudant.
        
        Args:
            event_type: Type of event (report_created, status_changed, etc.)
            entity_id: ID of the entity
            entity_type: Type of entity (report, incident, etc.)
            action: Action performed
            details: Event details
            
        Returns:
            Document ID if successful, None otherwise
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            timestamp = utc_now()
            doc = {
                "_id": f"audit_{entity_type}_{entity_id}_{int(timestamp.timestamp() * 1000)}",
                "type": "audit_event",
                "event_type": event_type,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "action": action,
                "details": details,
                "timestamp": format_iso8601(timestamp)
            }
            
            response = self.client.post_document(
                db=self.db_audit_events,
                document=Document(**doc)
            ).get_result()
            
            logger.info(f"Stored audit event in Cloudant: {response.get('id')}")
            return response.get("id")
            
        except Exception as e:
            logger.error(f"Failed to store audit event in Cloudant: {e}")
            return None
    
    def get_document(self, db_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document from Cloudant.
        
        Args:
            db_name: Database name
            doc_id: Document ID
            
        Returns:
            Document data if found, None otherwise
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            response = self.client.get_document(
                db=db_name,
                doc_id=doc_id
            ).get_result()
            
            return response
            
        except ApiException as e:
            if e.code == 404:
                logger.warning(f"Document not found: {doc_id}")
            else:
                logger.error(f"Failed to retrieve document: {e}")
            return None


# Global instance
cloudant_service = CloudantService()

# Made with Bob
