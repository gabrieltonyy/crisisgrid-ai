"""
Comprehensive test suite for Phase 6: Alert and Dispatch Simulation.
Tests alert generation, dispatch logic, and API endpoints.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.alert_service import alert_service
from app.services.dispatch_service import dispatch_service
from app.models.incident import Incident
from app.models.alert import Alert
from app.models.dispatch_log import DispatchLog
from app.schemas.common import (
    CrisisType,
    IncidentStatus,
    SeverityLevel,
    AlertStatus,
    DispatchStatus,
    AuthorityType
)
from app.utils.ids import generate_alert_id, generate_dispatch_id


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def verified_fire_incident():
    """Create a verified fire incident with high confidence."""
    incident = Mock(spec=Incident)
    incident.id = "incident_fire_001"
    incident.crisis_type = CrisisType.FIRE
    incident.status = IncidentStatus.VERIFIED
    incident.confidence_score = 85.0
    incident.latitude = -1.2921
    incident.longitude = 36.8219
    incident.location_description = "Nairobi CBD"
    incident.severity = SeverityLevel.HIGH
    return incident


@pytest.fixture
def unverified_incident():
    """Create an unverified incident."""
    incident = Mock(spec=Incident)
    incident.id = "incident_fire_002"
    incident.crisis_type = CrisisType.FIRE
    incident.status = IncidentStatus.PENDING_VERIFICATION
    incident.confidence_score = 50.0
    incident.latitude = -1.2921
    incident.longitude = 36.8219
    return incident


@pytest.fixture
def low_confidence_incident():
    """Create a verified incident with low confidence."""
    incident = Mock(spec=Incident)
    incident.id = "incident_fire_003"
    incident.crisis_type = CrisisType.FIRE
    incident.status = IncidentStatus.VERIFIED
    incident.confidence_score = 65.0  # Below 70% threshold
    incident.latitude = -1.2921
    incident.longitude = 36.8219
    return incident


# ============================================================================
# ALERT SERVICE TESTS
# ============================================================================

class TestAlertService:
    """Test alert service functionality."""
    
    def test_determine_alert_level_critical(self):
        """Test alert level determination for CRITICAL (90+)."""
        level = alert_service.determine_alert_level(95.0)
        assert level == "CRITICAL"
    
    def test_determine_alert_level_high(self):
        """Test alert level determination for HIGH (80-89)."""
        level = alert_service.determine_alert_level(85.0)
        assert level == "HIGH"
    
    def test_determine_alert_level_medium(self):
        """Test alert level determination for MEDIUM (70-79)."""
        level = alert_service.determine_alert_level(75.0)
        assert level == "MEDIUM"
    
    def test_determine_alert_level_low(self):
        """Test alert level determination for LOW (<70)."""
        level = alert_service.determine_alert_level(65.0)
        assert level == "LOW"
    
    def test_generate_alert_message_fire_critical(self):
        """Test alert message generation for critical fire."""
        message = alert_service.generate_alert_message(CrisisType.FIRE, "CRITICAL")
        assert "CRITICAL FIRE ALERT" in message
        assert "Evacuate immediately" in message
    
    def test_generate_alert_message_flood_high(self):
        """Test alert message generation for high flood."""
        message = alert_service.generate_alert_message(CrisisType.FLOOD, "HIGH")
        assert "HIGH FLOOD ALERT" in message
        assert "higher ground" in message
    
    @patch('app.services.alert_service.alert_repository')
    @patch('app.services.alert_service.get_alert_radius')
    def test_generate_alert_success(
        self, 
        mock_get_radius, 
        mock_repo,
        mock_db, 
        verified_fire_incident
    ):
        """Test successful alert generation for verified incident."""
        # Setup mocks
        mock_db.query.return_value.filter.return_value.first.return_value = verified_fire_incident
        mock_repo.check_duplicate_alert.return_value = False
        mock_get_radius.return_value = 1000
        
        mock_alert = Mock(spec=Alert)
        mock_alert.alert_id = "alert_fire_001"
        mock_repo.create_alert.return_value = mock_alert
        
        # Generate alert
        alert = alert_service.generate_alert(mock_db, "incident_fire_001")
        
        # Verify
        assert alert is not None
        assert mock_repo.create_alert.called
    
    def test_generate_alert_unverified_incident(self, mock_db, unverified_incident):
        """Test alert generation fails for unverified incident."""
        mock_db.query.return_value.filter.return_value.first.return_value = unverified_incident
        
        alert = alert_service.generate_alert(mock_db, "incident_fire_002")
        
        assert alert is None
    
    def test_generate_alert_low_confidence(self, mock_db, low_confidence_incident):
        """Test alert generation fails for low confidence incident."""
        mock_db.query.return_value.filter.return_value.first.return_value = low_confidence_incident
        
        alert = alert_service.generate_alert(mock_db, "incident_fire_003")
        
        assert alert is None
    
    @patch('app.services.alert_service.alert_repository')
    def test_generate_alert_duplicate_prevention(
        self, 
        mock_repo,
        mock_db, 
        verified_fire_incident
    ):
        """Test duplicate alert prevention (idempotency)."""
        mock_db.query.return_value.filter.return_value.first.return_value = verified_fire_incident
        mock_repo.check_duplicate_alert.return_value = True
        
        existing_alert = Mock(spec=Alert)
        existing_alert.alert_id = "alert_fire_001"
        mock_repo.get_active_alerts_by_incident.return_value = [existing_alert]
        
        alert = alert_service.generate_alert(mock_db, "incident_fire_001")
        
        # Should return existing alert, not create new one
        assert alert == existing_alert
        assert not mock_repo.create_alert.called
    
    def test_generate_alert_incident_not_found(self, mock_db):
        """Test alert generation when incident doesn't exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        alert = alert_service.generate_alert(mock_db, "nonexistent_incident")
        
        assert alert is None


# ============================================================================
# DISPATCH SERVICE TESTS
# ============================================================================

class TestDispatchService:
    """Test dispatch service functionality."""
    
    def test_get_authorities_for_fire(self):
        """Test authority mapping for fire incidents."""
        authorities = dispatch_service.get_authorities_for_crisis(CrisisType.FIRE)
        assert AuthorityType.FIRE_SERVICE in authorities
    
    def test_get_authorities_for_flood(self):
        """Test authority mapping for flood incidents."""
        authorities = dispatch_service.get_authorities_for_crisis(CrisisType.FLOOD)
        assert AuthorityType.DISASTER_MANAGEMENT in authorities
    
    def test_get_authorities_for_accident(self):
        """Test authority mapping for accident incidents (multiple authorities)."""
        authorities = dispatch_service.get_authorities_for_crisis(CrisisType.ACCIDENT)
        assert AuthorityType.AMBULANCE in authorities
        assert AuthorityType.POLICE in authorities
    
    def test_get_authorities_for_wildlife(self):
        """Test authority mapping for wildlife incidents."""
        authorities = dispatch_service.get_authorities_for_crisis(CrisisType.WILDLIFE)
        assert AuthorityType.WILDLIFE_AUTHORITY in authorities
    
    def test_determine_priority_critical(self):
        """Test priority determination for CRITICAL (90+)."""
        priority = dispatch_service.determine_priority(95.0)
        assert priority == "CRITICAL"
    
    def test_determine_priority_high(self):
        """Test priority determination for HIGH (80-89)."""
        priority = dispatch_service.determine_priority(85.0)
        assert priority == "HIGH"
    
    def test_determine_priority_medium(self):
        """Test priority determination for MEDIUM (70-79)."""
        priority = dispatch_service.determine_priority(75.0)
        assert priority == "MEDIUM"
    
    def test_simulate_eta_critical(self):
        """Test ETA simulation for critical priority."""
        eta = dispatch_service.simulate_eta("CRITICAL")
        assert 3 <= eta <= 7
    
    def test_simulate_eta_high(self):
        """Test ETA simulation for high priority."""
        eta = dispatch_service.simulate_eta("HIGH")
        assert 5 <= eta <= 10
    
    def test_generate_dispatch_message(self):
        """Test dispatch message generation."""
        message = dispatch_service.generate_dispatch_message(
            CrisisType.FIRE,
            "HIGH",
            "Nairobi CBD",
            85.0
        )
        assert "HIGH priority" in message
        assert "FIRE" in message
        assert "Nairobi CBD" in message
        assert "85.0%" in message
    
    @patch('app.services.dispatch_service.dispatch_repository')
    def test_dispatch_authority_success(
        self, 
        mock_repo,
        mock_db, 
        verified_fire_incident
    ):
        """Test successful authority dispatch for high priority incident."""
        mock_db.query.return_value.filter.return_value.first.return_value = verified_fire_incident
        mock_repo.check_duplicate_dispatch.return_value = False
        
        mock_dispatch = Mock(spec=DispatchLog)
        mock_dispatch.dispatch_id = "dispatch_fire_001"
        mock_repo.create_dispatch.return_value = mock_dispatch
        
        dispatches = dispatch_service.dispatch_authority(mock_db, "incident_fire_001")
        
        assert len(dispatches) > 0
        assert mock_repo.create_dispatch.called
    
    def test_dispatch_authority_low_priority(self, mock_db, low_confidence_incident):
        """Test dispatch fails for low priority incident."""
        mock_db.query.return_value.filter.return_value.first.return_value = low_confidence_incident
        
        dispatches = dispatch_service.dispatch_authority(mock_db, "incident_fire_003")
        
        assert len(dispatches) == 0
    
    @patch('app.services.dispatch_service.dispatch_repository')
    def test_dispatch_authority_duplicate_prevention(
        self, 
        mock_repo,
        mock_db, 
        verified_fire_incident
    ):
        """Test duplicate dispatch prevention (idempotency)."""
        mock_db.query.return_value.filter.return_value.first.return_value = verified_fire_incident
        mock_repo.check_duplicate_dispatch.return_value = True
        
        dispatches = dispatch_service.dispatch_authority(mock_db, "incident_fire_001")
        
        # Should not create dispatch if duplicate exists
        assert len(dispatches) == 0
        assert not mock_repo.create_dispatch.called
    
    def test_dispatch_authority_incident_not_found(self, mock_db):
        """Test dispatch when incident doesn't exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        dispatches = dispatch_service.dispatch_authority(mock_db, "nonexistent_incident")
        
        assert len(dispatches) == 0


# ============================================================================
# ID GENERATION TESTS
# ============================================================================

class TestIDGeneration:
    """Test ID generation utilities."""
    
    def test_generate_alert_id_format(self):
        """Test alert ID format."""
        alert_id = generate_alert_id("fire")
        assert alert_id.startswith("alert_fire_")
        assert len(alert_id.split("_")) == 3
    
    def test_generate_dispatch_id_format(self):
        """Test dispatch ID format."""
        dispatch_id = generate_dispatch_id("flood")
        assert dispatch_id.startswith("dispatch_flood_")
        assert len(dispatch_id.split("_")) == 3
    
    def test_generate_alert_id_with_sequence(self):
        """Test alert ID with custom sequence."""
        alert_id = generate_alert_id("fire", 123)
        assert alert_id == "alert_fire_00123"
    
    def test_generate_dispatch_id_with_sequence(self):
        """Test dispatch ID with custom sequence."""
        dispatch_id = generate_dispatch_id("flood", 456)
        assert dispatch_id == "dispatch_flood_00456"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestAlertDispatchIntegration:
    """Test integration between alert and dispatch services."""
    
    @patch('app.services.alert_service.alert_repository')
    @patch('app.services.dispatch_service.dispatch_repository')
    @patch('app.services.alert_service.get_alert_radius')
    def test_full_alert_dispatch_flow(
        self,
        mock_get_radius,
        mock_dispatch_repo,
        mock_alert_repo,
        mock_db,
        verified_fire_incident
    ):
        """Test complete flow: incident -> alert -> dispatch."""
        # Setup mocks
        mock_db.query.return_value.filter.return_value.first.return_value = verified_fire_incident
        mock_alert_repo.check_duplicate_alert.return_value = False
        mock_dispatch_repo.check_duplicate_dispatch.return_value = False
        mock_get_radius.return_value = 1000
        
        mock_alert = Mock(spec=Alert)
        mock_alert.alert_id = "alert_fire_001"
        mock_alert_repo.create_alert.return_value = mock_alert
        
        mock_dispatch = Mock(spec=DispatchLog)
        mock_dispatch.dispatch_id = "dispatch_fire_001"
        mock_dispatch_repo.create_dispatch.return_value = mock_dispatch
        
        # Generate alert
        alert = alert_service.generate_alert(mock_db, "incident_fire_001")
        assert alert is not None
        
        # Dispatch authorities
        dispatches = dispatch_service.dispatch_authority(mock_db, "incident_fire_001")
        assert len(dispatches) > 0


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_alert_level_boundary_90(self):
        """Test alert level at 90% boundary (CRITICAL threshold)."""
        assert alert_service.determine_alert_level(90.0) == "CRITICAL"
        assert alert_service.determine_alert_level(89.9) == "HIGH"
    
    def test_alert_level_boundary_80(self):
        """Test alert level at 80% boundary (HIGH threshold)."""
        assert alert_service.determine_alert_level(80.0) == "HIGH"
        assert alert_service.determine_alert_level(79.9) == "MEDIUM"
    
    def test_alert_level_boundary_70(self):
        """Test alert level at 70% boundary (MEDIUM threshold)."""
        assert alert_service.determine_alert_level(70.0) == "MEDIUM"
        assert alert_service.determine_alert_level(69.9) == "LOW"
    
    def test_priority_boundary_90(self):
        """Test priority at 90% boundary (CRITICAL threshold)."""
        assert dispatch_service.determine_priority(90.0) == "CRITICAL"
        assert dispatch_service.determine_priority(89.9) == "HIGH"
    
    def test_priority_boundary_80(self):
        """Test priority at 80% boundary (HIGH threshold)."""
        assert dispatch_service.determine_priority(80.0) == "HIGH"
        assert dispatch_service.determine_priority(79.9) == "MEDIUM"
    
    def test_dispatch_only_high_critical(self):
        """Test that only HIGH and CRITICAL incidents trigger dispatch."""
        # MEDIUM priority (75%) should not dispatch
        incident = Mock(spec=Incident)
        incident.id = "incident_fire_004"
        incident.crisis_type = CrisisType.FIRE
        incident.confidence_score = 75.0
        
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = incident
        
        dispatches = dispatch_service.dispatch_authority(mock_db, "incident_fire_004")
        assert len(dispatches) == 0


# Made with Bob