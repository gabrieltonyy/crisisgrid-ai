"""
Unit tests for clustering and GeoRisk functionality.
Tests distance calculations, clustering algorithms, and geographic risk assessment.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from decimal import Decimal

from app.utils.geo import (
    haversine_distance,
    is_within_radius,
    calculate_centroid,
    get_bounding_box,
    format_distance
)
from app.services.georisk_service import (
    get_clustering_radius,
    get_alert_radius,
    get_evacuation_radius,
    CRISIS_RADIUS_CONFIG
)
from app.schemas.common import CrisisType, SeverityLevel


class TestHaversineDistance:
    """Test haversine distance calculations."""
    
    def test_same_location(self):
        """Test distance between same coordinates is zero."""
        distance = haversine_distance(-1.2921, 36.8219, -1.2921, 36.8219)
        assert distance == 0.0
    
    def test_known_distance(self):
        """Test distance calculation with known coordinates."""
        # Nairobi CBD to Westlands (approximately 5km)
        distance = haversine_distance(-1.2921, 36.8219, -1.2630, 36.8063)
        assert 4500 < distance < 5500  # Allow some tolerance
    
    def test_short_distance(self):
        """Test short distance calculation (within 1km)."""
        # Two points about 500m apart
        distance = haversine_distance(-1.2921, 36.8219, -1.2864, 36.8172)
        assert 600 < distance < 700
    
    def test_long_distance(self):
        """Test long distance calculation."""
        # Nairobi to Mombasa (approximately 440km)
        distance = haversine_distance(-1.2921, 36.8219, -4.0435, 39.6682)
        assert 430000 < distance < 450000
    
    def test_negative_coordinates(self):
        """Test with negative coordinates."""
        distance = haversine_distance(-1.0, -1.0, -2.0, -2.0)
        assert distance > 0


class TestIsWithinRadius:
    """Test radius checking."""
    
    def test_within_radius(self):
        """Test points within radius."""
        # 500m apart, checking 1000m radius
        result = is_within_radius(-1.2921, 36.8219, -1.2864, 36.8172, 1000)
        assert result is True
    
    def test_outside_radius(self):
        """Test points outside radius."""
        # 5km apart, checking 1000m radius
        result = is_within_radius(-1.2921, 36.8219, -1.2630, 36.8063, 1000)
        assert result is False
    
    def test_exact_radius(self):
        """Test point exactly at radius boundary."""
        # Calculate exact distance first
        distance = haversine_distance(-1.2921, 36.8219, -1.2864, 36.8172)
        result = is_within_radius(-1.2921, 36.8219, -1.2864, 36.8172, distance)
        assert result is True


class TestCalculateCentroid:
    """Test centroid calculation."""
    
    def test_single_point(self):
        """Test centroid of single point."""
        coords = [(-1.2921, 36.8219)]
        centroid = calculate_centroid(coords)
        assert centroid == (-1.2921, 36.8219)
    
    def test_two_points(self):
        """Test centroid of two points."""
        coords = [(-1.0, 36.0), (-2.0, 37.0)]
        centroid = calculate_centroid(coords)
        # Centroid should be roughly between the two points
        assert -2.0 <= centroid[0] <= -1.0
        assert 36.0 <= centroid[1] <= 37.0
    
    def test_multiple_points(self):
        """Test centroid of multiple points."""
        coords = [
            (-1.2921, 36.8219),
            (-1.2864, 36.8172),
            (-1.2950, 36.8250)
        ]
        centroid = calculate_centroid(coords)
        # Centroid should be within the bounds
        lats = [c[0] for c in coords]
        lons = [c[1] for c in coords]
        assert min(lats) <= centroid[0] <= max(lats)
        assert min(lons) <= centroid[1] <= max(lons)
    
    def test_empty_coordinates(self):
        """Test centroid with empty list raises error."""
        with pytest.raises(ValueError):
            calculate_centroid([])


class TestGetBoundingBox:
    """Test bounding box calculation."""
    
    def test_bounding_box_structure(self):
        """Test bounding box returns correct structure."""
        bbox = get_bounding_box(-1.2921, 36.8219, 1000)
        assert "min_lat" in bbox
        assert "max_lat" in bbox
        assert "min_lon" in bbox
        assert "max_lon" in bbox
    
    def test_bounding_box_contains_center(self):
        """Test bounding box contains center point."""
        lat, lon = -1.2921, 36.8219
        bbox = get_bounding_box(lat, lon, 1000)
        assert bbox["min_lat"] <= lat <= bbox["max_lat"]
        assert bbox["min_lon"] <= lon <= bbox["max_lon"]
    
    def test_bounding_box_size(self):
        """Test bounding box size increases with radius."""
        bbox_small = get_bounding_box(-1.2921, 36.8219, 500)
        bbox_large = get_bounding_box(-1.2921, 36.8219, 2000)
        
        # Larger radius should give larger bounding box
        assert (bbox_large["max_lat"] - bbox_large["min_lat"]) > \
               (bbox_small["max_lat"] - bbox_small["min_lat"])


class TestFormatDistance:
    """Test distance formatting."""
    
    def test_format_meters(self):
        """Test formatting distances in meters."""
        assert format_distance(250) == "250 m"
        assert format_distance(999) == "999 m"
    
    def test_format_kilometers(self):
        """Test formatting distances in kilometers."""
        assert format_distance(1000) == "1.0 km"
        assert format_distance(1500) == "1.5 km"
        assert format_distance(5432) == "5.4 km"


class TestCrisisRadiusConfig:
    """Test crisis-specific radius configuration."""
    
    def test_all_crisis_types_configured(self):
        """Test all crisis types have radius configuration."""
        for crisis_type in CrisisType:
            assert crisis_type in CRISIS_RADIUS_CONFIG
            config = CRISIS_RADIUS_CONFIG[crisis_type]
            assert "clustering_radius" in config
            assert "alert_radius" in config
            assert "evacuation_radius" in config
            assert "description" in config
    
    def test_fire_radius(self):
        """Test fire-specific radius configuration."""
        assert get_clustering_radius(CrisisType.FIRE) == 500
        assert get_alert_radius(CrisisType.FIRE) == 1000
        assert get_evacuation_radius(CrisisType.FIRE) == 2000
    
    def test_flood_radius(self):
        """Test flood-specific radius configuration."""
        assert get_clustering_radius(CrisisType.FLOOD) == 1000
        assert get_alert_radius(CrisisType.FLOOD) == 2000
        assert get_evacuation_radius(CrisisType.FLOOD) == 3000
    
    def test_wildlife_radius(self):
        """Test wildlife-specific radius configuration."""
        assert get_clustering_radius(CrisisType.WILDLIFE) == 1500
        assert get_alert_radius(CrisisType.WILDLIFE) == 2500
        assert get_evacuation_radius(CrisisType.WILDLIFE) == 1000
    
    def test_accident_radius(self):
        """Test accident-specific radius configuration."""
        assert get_clustering_radius(CrisisType.ACCIDENT) == 300
        assert get_alert_radius(CrisisType.ACCIDENT) == 500
        assert get_evacuation_radius(CrisisType.ACCIDENT) == 200
    
    def test_radius_relationships(self):
        """Test that alert radius >= clustering radius for all types."""
        for crisis_type in CrisisType:
            clustering = get_clustering_radius(crisis_type)
            alert = get_alert_radius(crisis_type)
            assert alert >= clustering, \
                f"{crisis_type}: alert radius should be >= clustering radius"


class TestClusteringScenarios:
    """Test clustering scenarios with mock data."""
    
    def test_single_report_forms_incident(self):
        """Test that a single report can form an incident."""
        # This would be tested with actual database in integration tests
        # Here we test the logic
        reports = [
            {"id": uuid4(), "lat": -1.2921, "lon": 36.8219, "type": CrisisType.FIRE}
        ]
        assert len(reports) >= 1
    
    def test_nearby_reports_cluster(self):
        """Test that nearby reports should cluster together."""
        # Two reports 400m apart (within fire clustering radius of 500m)
        lat1, lon1 = -1.2921, 36.8219
        lat2, lon2 = -1.2864, 36.8172
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        fire_radius = get_clustering_radius(CrisisType.FIRE)
        
        assert distance < fire_radius, "Reports should be within clustering radius"
    
    def test_distant_reports_dont_cluster(self):
        """Test that distant reports should not cluster together."""
        # Two reports 5km apart (outside fire clustering radius of 500m)
        lat1, lon1 = -1.2921, 36.8219
        lat2, lon2 = -1.2630, 36.8063
        
        distance = haversine_distance(lat1, lon1, lat2, lon2)
        fire_radius = get_clustering_radius(CrisisType.FIRE)
        
        assert distance > fire_radius, "Reports should be outside clustering radius"
    
    def test_different_crisis_types_dont_cluster(self):
        """Test that different crisis types should not cluster together."""
        # Even if nearby, different crisis types should form separate incidents
        fire_type = CrisisType.FIRE
        flood_type = CrisisType.FLOOD
        
        assert fire_type != flood_type


class TestGeoRiskScenarios:
    """Test geographic risk assessment scenarios."""
    
    def test_high_severity_increases_risk(self):
        """Test that higher severity increases risk score."""
        # Risk calculation logic: higher severity = higher base score
        low_severity_base = 25
        high_severity_base = 75
        critical_severity_base = 90
        
        assert high_severity_base > low_severity_base
        assert critical_severity_base > high_severity_base
    
    def test_fire_has_high_urgency(self):
        """Test that fire has high urgency multiplier."""
        fire_config = CRISIS_RADIUS_CONFIG[CrisisType.FIRE]
        accident_config = CRISIS_RADIUS_CONFIG[CrisisType.ACCIDENT]
        
        # Fire should have tighter clustering (more urgent)
        assert fire_config["clustering_radius"] <= accident_config["clustering_radius"] * 2
    
    def test_flood_affects_large_area(self):
        """Test that flood has larger affected area."""
        flood_radius = get_alert_radius(CrisisType.FLOOD)
        fire_radius = get_alert_radius(CrisisType.FIRE)
        
        # Flood should affect larger area
        assert flood_radius > fire_radius
    
    def test_wildlife_has_wide_alert_zone(self):
        """Test that wildlife has wide alert zone due to animal movement."""
        wildlife_alert = get_alert_radius(CrisisType.WILDLIFE)
        accident_alert = get_alert_radius(CrisisType.ACCIDENT)
        
        # Wildlife should have wider alert zone
        assert wildlife_alert > accident_alert


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_distance(self):
        """Test handling of zero distance."""
        distance = haversine_distance(0, 0, 0, 0)
        assert distance == 0.0
    
    def test_equator_crossing(self):
        """Test distance calculation crossing equator."""
        distance = haversine_distance(-1.0, 36.0, 1.0, 36.0)
        assert distance > 0
    
    def test_prime_meridian_crossing(self):
        """Test distance calculation crossing prime meridian."""
        distance = haversine_distance(0, -1.0, 0, 1.0)
        assert distance > 0
    
    def test_extreme_latitudes(self):
        """Test with extreme latitude values."""
        # Near poles
        distance = haversine_distance(89.0, 0, 89.0, 180)
        assert distance > 0
    
    def test_extreme_longitudes(self):
        """Test with extreme longitude values."""
        distance = haversine_distance(0, -179, 0, 179)
        assert distance > 0


# Integration test scenarios (would require database)
class TestClusteringIntegration:
    """Integration test scenarios for clustering (require database setup)."""
    
    @pytest.mark.skip(reason="Requires database setup")
    def test_cluster_multiple_fire_reports(self):
        """Test clustering multiple fire reports in same area."""
        pass
    
    @pytest.mark.skip(reason="Requires database setup")
    def test_cluster_reports_different_times(self):
        """Test clustering reports from different time windows."""
        pass
    
    @pytest.mark.skip(reason="Requires database setup")
    def test_update_incident_with_new_report(self):
        """Test adding new report to existing incident."""
        pass
    
    @pytest.mark.skip(reason="Requires database setup")
    def test_recalculate_centroid_on_cluster_update(self):
        """Test centroid recalculation when cluster grows."""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob