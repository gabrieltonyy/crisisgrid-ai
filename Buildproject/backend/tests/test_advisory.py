"""
Tests for advisory service and API endpoints.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.advisory_service import AdvisoryService, advisory_service
from app.schemas.common import CrisisType, SeverityLevel, IncidentStatus
from app.models.incident import Incident


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def sample_incident():
    """Create a sample incident for testing."""
    incident = Mock(spec=Incident)
    incident.id = "incident_fire_001"
    incident.crisis_type = CrisisType.FIRE
    incident.severity = SeverityLevel.HIGH
    incident.status = IncidentStatus.VERIFIED
    incident.latitude = -1.2921
    incident.longitude = 36.8219
    incident.location_description = "Nairobi CBD"
    incident.confidence_score = 85.0
    return incident


@pytest.fixture
def advisory_svc():
    """Create advisory service instance."""
    return AdvisoryService()


# ============================================================================
# PLAYBOOK TESTS
# ============================================================================

def test_get_playbook_fire(advisory_svc):
    """Test getting fire playbook."""
    playbook = advisory_svc.get_playbook(CrisisType.FIRE)
    
    assert playbook["playbook_id"] == "FIRE_STANDARD"
    assert len(playbook["immediate_actions"]) == 3
    assert playbook["immediate_actions"][0]["priority"] == 1
    assert "evacuate" in playbook["immediate_actions"][0]["action"].lower()
    assert len(playbook["what_to_do"]) > 0
    assert len(playbook["what_not_to_do"]) > 0
    assert len(playbook["emergency_contacts"]) > 0


def test_get_playbook_flood(advisory_svc):
    """Test getting flood playbook."""
    playbook = advisory_svc.get_playbook(CrisisType.FLOOD)
    
    assert playbook["playbook_id"] == "FLOOD_STANDARD"
    assert len(playbook["immediate_actions"]) == 3
    assert "higher ground" in playbook["immediate_actions"][0]["action"].lower()


def test_get_playbook_wildlife(advisory_svc):
    """Test getting wildlife playbook."""
    playbook = advisory_svc.get_playbook(CrisisType.WILDLIFE)
    
    assert playbook["playbook_id"] == "WILDLIFE_STANDARD"
    assert "distance" in playbook["immediate_actions"][0]["action"].lower()


def test_get_playbook_accident(advisory_svc):
    """Test getting accident playbook."""
    playbook = advisory_svc.get_playbook(CrisisType.ACCIDENT)
    
    assert playbook["playbook_id"] == "ACCIDENT_STANDARD"
    assert "safety" in playbook["immediate_actions"][0]["action"].lower()


def test_get_playbook_security(advisory_svc):
    """Test getting security playbook."""
    playbook = advisory_svc.get_playbook(CrisisType.SECURITY)
    
    assert playbook["playbook_id"] == "SECURITY_STANDARD"
    assert "safe location" in playbook["immediate_actions"][0]["action"].lower()


def test_get_playbook_health(advisory_svc):
    """Test getting health playbook."""
    playbook = advisory_svc.get_playbook(CrisisType.HEALTH)
    
    assert playbook["playbook_id"] == "HEALTH_STANDARD"
    assert "avoid" in playbook["immediate_actions"][0]["action"].lower()


def test_get_playbook_landslide(advisory_svc):
    """Test getting landslide playbook."""
    playbook = advisory_svc.get_playbook(CrisisType.LANDSLIDE)
    
    assert playbook["playbook_id"] == "LANDSLIDE_STANDARD"
    assert "evacuate" in playbook["immediate_actions"][0]["action"].lower()


def test_get_playbook_hazmat(advisory_svc):
    """Test getting hazmat playbook."""
    playbook = advisory_svc.get_playbook(CrisisType.HAZARDOUS_SPILL)
    
    assert playbook["playbook_id"] == "HAZMAT_STANDARD"
    assert "evacuate" in playbook["immediate_actions"][0]["action"].lower()


def test_get_playbook_other(advisory_svc):
    """Test getting general playbook."""
    playbook = advisory_svc.get_playbook(CrisisType.OTHER)
    
    assert playbook["playbook_id"] == "GENERAL_STANDARD"
    assert len(playbook["immediate_actions"]) == 3


# ============================================================================
# RISK LEVEL TESTS
# ============================================================================

def test_determine_risk_level_immediate(advisory_svc):
    """Test immediate risk level determination."""
    risk_level = advisory_svc.determine_risk_level(300, CrisisType.FIRE)
    assert risk_level == "IMMEDIATE"


def test_determine_risk_level_high(advisory_svc):
    """Test high risk level determination."""
    risk_level = advisory_svc.determine_risk_level(700, CrisisType.FIRE)
    assert risk_level == "HIGH"


def test_determine_risk_level_moderate(advisory_svc):
    """Test moderate risk level determination."""
    risk_level = advisory_svc.determine_risk_level(1500, CrisisType.FIRE)
    assert risk_level == "MODERATE"


def test_determine_risk_level_low(advisory_svc):
    """Test low risk level determination."""
    risk_level = advisory_svc.determine_risk_level(3000, CrisisType.FIRE)
    assert risk_level == "LOW"


def test_determine_risk_level_no_distance(advisory_svc):
    """Test risk level when distance is unknown."""
    risk_level = advisory_svc.determine_risk_level(None, CrisisType.FIRE)
    assert risk_level == "MODERATE"


def test_determine_risk_level_flood_multiplier(advisory_svc):
    """Test flood crisis type multiplier."""
    # Flood has 1.5x multiplier, so 750m feels like 500m
    risk_level = advisory_svc.determine_risk_level(750, CrisisType.FLOOD)
    assert risk_level == "IMMEDIATE"


def test_determine_risk_level_accident_multiplier(advisory_svc):
    """Test accident crisis type multiplier."""
    # Accident has 0.5x multiplier, so 250m feels like 500m
    risk_level = advisory_svc.determine_risk_level(250, CrisisType.ACCIDENT)
    assert risk_level == "IMMEDIATE"


# ============================================================================
# PRIMARY ADVICE TESTS
# ============================================================================

def test_generate_primary_advice_immediate(advisory_svc):
    """Test primary advice for immediate danger."""
    advice = advisory_svc.generate_primary_advice(
        CrisisType.FIRE, "IMMEDIATE", 250.0
    )
    
    assert "IMMEDIATE DANGER" in advice
    assert "250m" in advice
    assert "Evacuate immediately" in advice


def test_generate_primary_advice_high(advisory_svc):
    """Test primary advice for high risk."""
    advice = advisory_svc.generate_primary_advice(
        CrisisType.FLOOD, "HIGH", 800.0
    )
    
    assert "HIGH RISK" in advice
    assert "800m" in advice
    assert "Prepare to evacuate" in advice


def test_generate_primary_advice_moderate(advisory_svc):
    """Test primary advice for moderate risk."""
    advice = advisory_svc.generate_primary_advice(
        CrisisType.WILDLIFE, "MODERATE", None
    )
    
    assert "MODERATE RISK" in advice
    assert "Stay alert" in advice


def test_generate_primary_advice_low(advisory_svc):
    """Test primary advice for low risk."""
    advice = advisory_svc.generate_primary_advice(
        CrisisType.ACCIDENT, "LOW", None
    )
    
    assert "LOW RISK" in advice
    assert "Monitor" in advice


# ============================================================================
# ADVISORY GENERATION TESTS
# ============================================================================

@patch('app.services.advisory_service.cloudant_service')
def test_generate_advisory_success(mock_cloudant, advisory_svc, mock_db, sample_incident):
    """Test successful advisory generation."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = sample_incident
    mock_cloudant.store_agent_log.return_value = "log_id"
    
    # Execute
    advisory = advisory_svc.generate_advisory(
        db=mock_db,
        incident_id="incident_fire_001",
        user_latitude=-1.2900,
        user_longitude=36.8200
    )
    
    # Assert
    assert advisory is not None
    assert advisory.incident_id == "incident_fire_001"
    assert advisory.crisis_type == CrisisType.FIRE
    assert advisory.severity == SeverityLevel.HIGH
    assert advisory.distance_meters is not None
    assert advisory.risk_level in ["IMMEDIATE", "HIGH", "MODERATE", "LOW"]
    assert len(advisory.immediate_actions) == 3
    assert len(advisory.what_to_do) > 0
    assert len(advisory.what_not_to_do) > 0
    assert advisory.evacuation_advice is not None
    assert len(advisory.emergency_contacts) > 0
    assert advisory.playbook_used == "FIRE_STANDARD"


@patch('app.services.advisory_service.cloudant_service')
def test_generate_advisory_no_location(mock_cloudant, advisory_svc, mock_db, sample_incident):
    """Test advisory generation without user location."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = sample_incident
    mock_cloudant.store_agent_log.return_value = "log_id"
    
    # Execute
    advisory = advisory_svc.generate_advisory(
        db=mock_db,
        incident_id="incident_fire_001"
    )
    
    # Assert
    assert advisory is not None
    assert advisory.distance_meters is None
    assert advisory.risk_level == "MODERATE"  # Default when no location


@patch('app.services.advisory_service.cloudant_service')
def test_generate_advisory_with_context(mock_cloudant, advisory_svc, mock_db, sample_incident):
    """Test advisory generation with user context."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = sample_incident
    mock_cloudant.store_agent_log.return_value = "log_id"
    
    # Execute
    advisory = advisory_svc.generate_advisory(
        db=mock_db,
        incident_id="incident_fire_001",
        user_latitude=-1.2900,
        user_longitude=36.8200,
        user_context="at home with family"
    )
    
    # Assert
    assert advisory is not None
    assert advisory.incident_id == "incident_fire_001"


def test_generate_advisory_incident_not_found(advisory_svc, mock_db):
    """Test advisory generation when incident not found."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Execute
    advisory = advisory_svc.generate_advisory(
        db=mock_db,
        incident_id="nonexistent"
    )
    
    # Assert
    assert advisory is None


@patch('app.services.advisory_service.cloudant_service')
def test_generate_advisory_different_crisis_types(mock_cloudant, advisory_svc, mock_db):
    """Test advisory generation for different crisis types."""
    mock_cloudant.store_agent_log.return_value = "log_id"
    
    crisis_types = [
        CrisisType.FIRE,
        CrisisType.FLOOD,
        CrisisType.WILDLIFE,
        CrisisType.ACCIDENT,
        CrisisType.SECURITY,
        CrisisType.HEALTH,
        CrisisType.LANDSLIDE,
        CrisisType.HAZARDOUS_SPILL
    ]
    
    for crisis_type in crisis_types:
        # Setup incident
        incident = Mock(spec=Incident)
        incident.id = f"incident_{crisis_type.value}_001"
        incident.crisis_type = crisis_type
        incident.severity = SeverityLevel.HIGH
        incident.latitude = -1.2921
        incident.longitude = 36.8219
        incident.location_description = "Test Location"
        incident.confidence_score = 80.0
        
        mock_db.query.return_value.filter.return_value.first.return_value = incident
        
        # Execute
        advisory = advisory_svc.generate_advisory(
            db=mock_db,
            incident_id=incident.id,
            user_latitude=-1.2900,
            user_longitude=36.8200
        )
        
        # Assert
        assert advisory is not None
        assert advisory.crisis_type == crisis_type
        assert len(advisory.immediate_actions) > 0


# ============================================================================
# AI ENHANCEMENT TESTS
# ============================================================================

def test_enhance_with_ai_success(advisory_svc, sample_incident):
    """Test AI enhancement when watsonx is available."""
    # Setup - patch the watsonx service on the advisory_svc instance
    with patch.object(advisory_svc, 'watsonx') as mock_watsonx:
        mock_watsonx.enabled = True
        mock_watsonx.model = Mock()
        mock_watsonx.model.generate_text.return_value = "Additional AI-generated safety advice for your specific situation."
        
        playbook = advisory_svc.get_playbook(CrisisType.FIRE)
        
        # Execute
        enhanced_advice = advisory_svc.enhance_with_ai(
            incident=sample_incident,
            playbook=playbook,
            user_context="at home",
            distance_meters=500.0
        )
        
        # Assert
        assert enhanced_advice is not None
        assert len(enhanced_advice) > 20
        assert "Additional AI-generated" in enhanced_advice


@patch('app.services.advisory_service.watsonx_service')
def test_enhance_with_ai_disabled(mock_watsonx, advisory_svc, sample_incident):
    """Test AI enhancement when watsonx is disabled."""
    # Setup
    mock_watsonx.enabled = False
    
    playbook = advisory_svc.get_playbook(CrisisType.FIRE)
    
    # Execute
    enhanced_advice = advisory_svc.enhance_with_ai(
        incident=sample_incident,
        playbook=playbook,
        user_context="at home",
        distance_meters=500.0
    )
    
    # Assert
    assert enhanced_advice is None


@patch('app.services.advisory_service.watsonx_service')
def test_enhance_with_ai_error(mock_watsonx, advisory_svc, sample_incident):
    """Test AI enhancement when error occurs."""
    # Setup
    mock_watsonx.enabled = True
    mock_watsonx.model = Mock()
    mock_watsonx.model.generate_text.side_effect = Exception("AI error")
    
    playbook = advisory_svc.get_playbook(CrisisType.FIRE)
    
    # Execute
    enhanced_advice = advisory_svc.enhance_with_ai(
        incident=sample_incident,
        playbook=playbook,
        user_context="at home",
        distance_meters=500.0
    )
    
    # Assert
    assert enhanced_advice is None


# ============================================================================
# EDGE CASES
# ============================================================================

@patch('app.services.advisory_service.cloudant_service')
def test_generate_advisory_zero_distance(mock_cloudant, advisory_svc, mock_db, sample_incident):
    """Test advisory when user is at incident location."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = sample_incident
    mock_cloudant.store_agent_log.return_value = "log_id"
    
    # Execute - same coordinates as incident
    advisory = advisory_svc.generate_advisory(
        db=mock_db,
        incident_id="incident_fire_001",
        user_latitude=-1.2921,
        user_longitude=36.8219
    )
    
    # Assert
    assert advisory is not None
    assert advisory.distance_meters == 0.0
    assert advisory.risk_level == "IMMEDIATE"


@patch('app.services.advisory_service.cloudant_service')
def test_generate_advisory_very_far(mock_cloudant, advisory_svc, mock_db, sample_incident):
    """Test advisory when user is very far from incident."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = sample_incident
    mock_cloudant.store_agent_log.return_value = "log_id"
    
    # Execute - coordinates far away
    advisory = advisory_svc.generate_advisory(
        db=mock_db,
        incident_id="incident_fire_001",
        user_latitude=-1.5000,
        user_longitude=37.0000
    )
    
    # Assert
    assert advisory is not None
    assert advisory.distance_meters > 10000  # More than 10km
    assert advisory.risk_level == "LOW"


@patch('app.services.advisory_service.cloudant_service')
def test_cloudant_logging_failure(mock_cloudant, advisory_svc, mock_db, sample_incident):
    """Test that advisory generation continues even if Cloudant logging fails."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = sample_incident
    mock_cloudant.store_agent_log.side_effect = Exception("Cloudant error")
    
    # Execute - should not raise exception
    advisory = advisory_svc.generate_advisory(
        db=mock_db,
        incident_id="incident_fire_001",
        user_latitude=-1.2900,
        user_longitude=36.8200
    )
    
    # Assert - advisory still generated
    assert advisory is not None


# Made with Bob