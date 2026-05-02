"""ID generation utilities for reports and incidents."""

import time
import uuid
from typing import Optional


def generate_report_id() -> uuid.UUID:
    """Generate a unique UUID for a report."""
    return uuid.uuid4()


def generate_incident_id(crisis_type: str, sequence: Optional[int] = None) -> str:
    """
    Generate incident ID in format: incident_{type}_{sequence}
    Example: incident_fire_001
    
    Args:
        crisis_type: Type of crisis (e.g., 'fire', 'flood')
        sequence: Optional sequence number, if None generates timestamp-based
    
    Returns:
        Formatted incident ID string
    """
    if sequence is None:
        sequence = int(time.time() * 1000) % 100000
    return f"incident_{crisis_type.lower()}_{sequence:05d}"

# Made with Bob
