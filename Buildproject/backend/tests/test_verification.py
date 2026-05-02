"""
Tests for verification functionality.
Tests watsonx.ai service, verification service, and verification endpoints.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from app.services.watsonx_service import WatsonxService
from app.services.verification_service import VerificationService
from app.repositories.verification_repository import VerificationRepository
from app.schemas.common import CrisisType, IncidentStatus, AgentName, AgentRunStatus
from app.models.report import Report
from app.models.agent_run import AgentRun


# ============================================================================
# WATSONX SERVICE TESTS
# ============================================================================

class TestWatsonxService:
    """Tests for WatsonxService."""
    
    def test_fallback_analysis_fire(self):
        """Test fallback analysis for fire report."""
        service = WatsonxService()
        service.enabled = False  # Force fallback mode
        
        report_data = {
            "crisis_type": "FIRE",
            "description": "Large fire with visible flames and heavy smoke spreading rapidly",
            "latitude": -1.2921,
            "longitude": 36.8219,
            "location_text": "Nairobi CBD",
            "image_url": "/uploads/fire.jpg",
            "video_url": None
        }
        
        result = service.analyze_report(report_data)
        
        assert result["credibility_score"] >= 50
        assert result["credibility_score"] <= 100
        assert result["crisis_category"] == "FIRE"
        assert result["severity_score"] == 75  # Fire severity
        assert result["urgency_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert "reasoning" in result
        assert "fallback" in result["reasoning"].lower()
    
    def test_fallback_analysis_with_media_boost(self):
        """Test that media presence boosts credibility."""
        service = WatsonxService()
        service.enabled = False
        
        # Report without media
        report_no_media = {
            "crisis_type": "FLOOD",
            "description": "Water rising in the street",
            "latitude": -1.2921,
            "longitude": 36.8219,
            "image_url": None,
            "video_url": None
        }
        
        # Report with media
        report_with_media = {
            "crisis_type": "FLOOD",
            "description": "Water rising in the street",
            "latitude": -1.2921,
            "longitude": 36.8219,
            "image_url": "/uploads/flood.jpg",
            "video_url": None
        }
        
        result_no_media = service.analyze_report(report_no_media)
        result_with_media = service.analyze_report(report_with_media)
        
        # Media should boost credibility
        assert result_with_media["credibility_score"] > result_no_media["credibility_score"]
    
    def test_validate_analysis(self):
        """Test analysis validation and normalization."""
        service = WatsonxService()
        
        # Test with valid analysis
        analysis = {
            "credibility_score": 78.5,
            "crisis_category": "FIRE",
            "severity_score": 82.0,
            "urgency_level": "HIGH",
            "recommended_action": "Dispatch fire service",
            "reasoning": "High severity fire"
        }
        
        report_data = {"crisis_type": "FIRE"}
        
        result = service._validate_analysis(analysis, report_data)
        
        assert result["credibility_score"] == 78.5
        assert result["crisis_category"] == "FIRE"
        assert result["severity_score"] == 82.0
        assert result["urgency_level"] == "HIGH"
    
    def test_validate_analysis_invalid_category(self):
        """Test validation with invalid crisis category."""
        service = WatsonxService()
        
        analysis = {
            "credibility_score": 70,
            "crisis_category": "INVALID_TYPE",
            "severity_score": 75,
            "urgency_level": "HIGH"
        }
        
        report_data = {"crisis_type": "FIRE"}
        
        result = service._validate_analysis(analysis, report_data)
        
        # Should fall back to report's crisis type
        assert result["crisis_category"] == "FIRE"


# ============================================================================
# VERIFICATION SERVICE TESTS
# ============================================================================

class TestVerificationService:
    """Tests for VerificationService."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock()
    
    @pytest.fixture
    def mock_report(self):
        """Create mock report."""
        report = Mock(spec=Report)
        report.id = uuid4()
        report.crisis_type = CrisisType.FIRE
        report.description = "Large fire with smoke"
        report.latitude = Decimal("-1.2921")
        report.longitude = Decimal("36.8219")
        report.location_text = "Nairobi CBD"
        report.image_url = "/uploads/fire.jpg"
        report.video_url = None
        report.is_anonymous = False
        report.source = "CITIZEN_APP"
        report.status = IncidentStatus.PENDING_VERIFICATION
        return report
    
    @patch('app.services.verification_service.watsonx_service')
    @patch('app.services.verification_service.cloudant_service')
    def test_verify_report_success(self, mock_cloudant, mock_watsonx, mock_db, mock_report):
        """Test successful report verification."""
        # Setup mocks
        mock_watsonx.analyze_report.return_value = {
            "credibility_score": 78.5,
            "crisis_category": "FIRE",
            "severity_score": 82.0,
            "urgency_level": "HIGH",
            "recommended_action": "Dispatch fire service",
            "reasoning": "High credibility fire report"
        }
        
        mock_cloudant.enabled = True
        
        # Create service with mocked repository
        service = VerificationService(mock_db)
        service.repo = Mock(spec=VerificationRepository)
        service.repo.get_report_by_id.return_value = mock_report
        
        # Mock agent run
        mock_agent_run = Mock(spec=AgentRun)
        mock_agent_run.run_id = "run_verification_123"
        service.repo.create_agent_run.return_value = mock_agent_run
        service.repo.update_report_verification.return_value = mock_report
        service.repo.update_agent_run.return_value = mock_agent_run
        
        # Verify report
        result = service.verify_report(mock_report.id)
        
        # Assertions
        assert result.report_id == mock_report.id
        assert result.verified is True  # Above threshold
        assert result.final_confidence_score >= 60.0
        assert result.status == IncidentStatus.VERIFIED
        
        # Verify repository calls
        service.repo.get_report_by_id.assert_called_once_with(mock_report.id)
        service.repo.create_agent_run.assert_called_once()
        service.repo.update_report_verification.assert_called_once()
        service.repo.update_agent_run.assert_called_once()
    
    @patch('app.services.verification_service.watsonx_service')
    def test_verify_report_low_confidence(self, mock_watsonx, mock_db, mock_report):
        """Test verification with low confidence (rejected)."""
        # Setup mocks
        mock_watsonx.analyze_report.return_value = {
            "credibility_score": 35.0,  # Below threshold
            "crisis_category": "FIRE",
            "severity_score": 40.0,
            "urgency_level": "LOW",
            "recommended_action": "Monitor situation",
            "reasoning": "Low credibility"
        }
        
        service = VerificationService(mock_db)
        service.repo = Mock(spec=VerificationRepository)
        service.repo.get_report_by_id.return_value = mock_report
        
        mock_agent_run = Mock(spec=AgentRun)
        mock_agent_run.run_id = "run_verification_123"
        service.repo.create_agent_run.return_value = mock_agent_run
        service.repo.update_report_verification.return_value = mock_report
        service.repo.update_agent_run.return_value = mock_agent_run
        
        result = service.verify_report(mock_report.id)
        
        assert result.verified is False
        assert result.status == IncidentStatus.FALSE_REPORT
        assert result.final_confidence_score < 60.0
    
    def test_verify_report_not_found(self, mock_db):
        """Test verification of non-existent report."""
        service = VerificationService(mock_db)
        service.repo = Mock(spec=VerificationRepository)
        service.repo.get_report_by_id.return_value = None
        
        with pytest.raises(ValueError, match="not found"):
            service.verify_report(uuid4())
    
    def test_verify_report_already_verified(self, mock_db, mock_report):
        """Test verification of already verified report."""
        mock_report.status = IncidentStatus.VERIFIED
        
        service = VerificationService(mock_db)
        service.repo = Mock(spec=VerificationRepository)
        service.repo.get_report_by_id.return_value = mock_report
        
        with pytest.raises(ValueError, match="already verified"):
            service.verify_report(mock_report.id, force_revalidation=False)
    
    def test_calculate_final_confidence_with_media(self, mock_db, mock_report):
        """Test confidence calculation with media boost."""
        service = VerificationService(mock_db)
        
        # With media
        mock_report.image_url = "/uploads/fire.jpg"
        confidence_with_media = service._calculate_final_confidence(70.0, mock_report)
        
        # Without media
        mock_report.image_url = None
        confidence_without_media = service._calculate_final_confidence(70.0, mock_report)
        
        assert confidence_with_media > confidence_without_media
    
    def test_calculate_final_confidence_anonymous_penalty(self, mock_db, mock_report):
        """Test confidence calculation with anonymous penalty."""
        service = VerificationService(mock_db)
        
        # Not anonymous
        mock_report.is_anonymous = False
        confidence_not_anon = service._calculate_final_confidence(70.0, mock_report)
        
        # Anonymous
        mock_report.is_anonymous = True
        confidence_anon = service._calculate_final_confidence(70.0, mock_report)
        
        assert confidence_not_anon > confidence_anon


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

@pytest.fixture
def client():
    """Create test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


def test_health_endpoint(client):
    """Test that health endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200


def test_verify_report_endpoint_not_found(client):
    """Test verify endpoint with non-existent report."""
    fake_id = str(uuid4())
    response = client.post(f"/api/v1/verification/reports/{fake_id}/verify")
    assert response.status_code == 404


def test_get_pending_verifications_endpoint(client):
    """Test get pending verifications endpoint."""
    response = client.get("/api/v1/verification/pending")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert "page" in data
    assert "page_size" in data


def test_get_verification_stats_endpoint(client):
    """Test get verification stats endpoint."""
    response = client.get("/api/v1/verification/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_verified" in data
    assert "total_rejected" in data
    assert "total_pending" in data
    assert "average_confidence" in data
    assert "verification_rate" in data


def test_get_verification_history_not_found(client):
    """Test verification history for non-existent report."""
    fake_id = str(uuid4())
    response = client.get(f"/api/v1/verification/reports/{fake_id}")
    assert response.status_code == 404


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_openapi_schema(client):
    """Test that OpenAPI schema includes verification endpoints."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    
    # Check verification endpoints are in schema
    paths = schema.get("paths", {})
    assert "/api/v1/verification/reports/{report_id}/verify" in paths
    assert "/api/v1/verification/reports/{report_id}" in paths
    assert "/api/v1/verification/pending" in paths
    assert "/api/v1/verification/stats" in paths


def test_docs_endpoint(client):
    """Test that API docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


# Made with Bob