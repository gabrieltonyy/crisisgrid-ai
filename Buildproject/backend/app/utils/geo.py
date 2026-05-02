"""
Geographic utility functions for CrisisGrid AI.
Includes distance calculations and geographic clustering utilities.
"""

import math
from typing import Tuple, List, Dict, Any


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    Uses the Haversine formula.
    
    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees
        
    Returns:
        Distance in meters
        
    Example:
        >>> haversine_distance(-1.2921, 36.8219, -1.2864, 36.8172)
        652.89  # approximately 653 meters
    """
    # Earth's radius in meters
    EARTH_RADIUS_METERS = 6371000
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    
    # Distance in meters
    distance = EARTH_RADIUS_METERS * c
    
    return distance


def is_within_radius(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    radius_meters: float
) -> bool:
    """
    Check if two points are within a specified radius.
    
    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees
        radius_meters: Radius threshold in meters
        
    Returns:
        True if points are within radius, False otherwise
    """
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    return distance <= radius_meters


def calculate_centroid(coordinates: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Calculate the geographic centroid (center point) of multiple coordinates.
    
    Args:
        coordinates: List of (latitude, longitude) tuples
        
    Returns:
        Tuple of (centroid_latitude, centroid_longitude)
        
    Raises:
        ValueError: If coordinates list is empty
    """
    if not coordinates:
        raise ValueError("Cannot calculate centroid of empty coordinates list")
    
    # Convert to radians and calculate Cartesian coordinates
    x = 0.0
    y = 0.0
    z = 0.0
    
    for lat, lon in coordinates:
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        
        x += math.cos(lat_rad) * math.cos(lon_rad)
        y += math.cos(lat_rad) * math.sin(lon_rad)
        z += math.sin(lat_rad)
    
    # Average
    total = len(coordinates)
    x /= total
    y /= total
    z /= total
    
    # Convert back to latitude/longitude
    lon_centroid = math.atan2(y, x)
    hyp = math.sqrt(x * x + y * y)
    lat_centroid = math.atan2(z, hyp)
    
    return (math.degrees(lat_centroid), math.degrees(lon_centroid))


def get_bounding_box(
    lat: float,
    lon: float,
    radius_meters: float
) -> Dict[str, float]:
    """
    Calculate a bounding box around a point for efficient spatial queries.
    
    Args:
        lat: Center latitude in degrees
        lon: Center longitude in degrees
        radius_meters: Radius in meters
        
    Returns:
        Dictionary with min_lat, max_lat, min_lon, max_lon
    """
    # Earth's radius in meters
    EARTH_RADIUS_METERS = 6371000
    
    # Angular distance in radians
    angular_distance = radius_meters / EARTH_RADIUS_METERS
    
    # Convert to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    
    # Calculate bounds
    min_lat = lat_rad - angular_distance
    max_lat = lat_rad + angular_distance
    
    # Handle longitude wrapping
    if abs(lat_rad) + angular_distance < math.pi / 2:
        # Not near poles
        delta_lon = math.asin(math.sin(angular_distance) / math.cos(lat_rad))
        min_lon = lon_rad - delta_lon
        max_lon = lon_rad + delta_lon
    else:
        # Near poles - use full longitude range
        min_lon = -math.pi
        max_lon = math.pi
    
    return {
        "min_lat": math.degrees(min_lat),
        "max_lat": math.degrees(max_lat),
        "min_lon": math.degrees(min_lon),
        "max_lon": math.degrees(max_lon)
    }


def format_distance(distance_meters: float) -> str:
    """
    Format distance in human-readable format.
    
    Args:
        distance_meters: Distance in meters
        
    Returns:
        Formatted string (e.g., "1.5 km" or "250 m")
    """
    if distance_meters >= 1000:
        return f"{distance_meters / 1000:.1f} km"
    else:
        return f"{int(distance_meters)} m"

# Made with Bob